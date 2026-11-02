"""Build a portable HTML issue from the append-only research catalog (stdlib only)."""
import base64
import copy
import datetime as dt
import json
import mimetypes
import re
import html
from pathlib import Path
from research_store import sync

ROOT = Path(__file__).resolve().parent


def build():
    catalog = json.loads((ROOT / 'data/catalog.json').read_text(encoding='utf-8'))
    profiles = json.loads((ROOT / 'data/organization-profiles.json').read_text(encoding='utf-8'))
    editions = [json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT / 'data/editions').glob('*.json'))]
    editions.sort(key=lambda e: (e['date'], e.get('revision', 1)))
    ids = [w['id'] for w in catalog['works']]
    assert len(ids) == len(set(ids)), 'Duplicate work IDs'
    assert len(editions) == len({e.get('id', e['date']) for e in editions}), 'Duplicate issue dates'
    org_ids = {o['id'] for o in catalog['organizations']}
    assert set(profiles) <= org_ids, 'Unknown profile organization'
    for org in catalog['organizations']:
        if org['id'] in profiles:
            org['profile'] = profiles[org['id']]
            assert all(any(w['id'] == wid and org['id'] in w['orgIds'] for w in catalog['works']) for wid in org['profile']['representativeIds']), org['id']
    for work in catalog['works']:
        assert work['orgIds'] and set(work['orgIds']) <= org_ids, work['id']
        assert work['sources'] and all(s['url'].startswith('https://') for s in work['sources']), work['id']
        assert work['date'] <= catalog['asOf'], 'Future-dated work: ' + work['id']
        dt.date.fromisoformat(work['date'] + '-01' if work.get('datePrecision') == 'month' else work['date'])
        assert set(work.get('techIds', [])) <= {t['id'] for t in catalog['technologies']}, work['id']
    for edition in editions:
        assert set(edition['featuredIds']) <= set(ids), edition['date']
        assert edition['date'] <= catalog['asOf']
        assert all(w['date'] <= edition['date'] for w in catalog['works'] if w['id'] in edition['featuredIds']), 'Future work in issue'
    for org in catalog['organizations']:
        assert set(org.get('evidenceIds', [])) <= set(ids), org['id']
    for tech in catalog['technologies']:
        assert all(c['workId'] in ids for c in tech['connections']), tech['id']
    template = (ROOT / 'src/template.html').read_text(encoding='utf-8').replace('研究日报', html.escape(catalog['title']))
    shared_script = (ROOT / 'src/work-view.js').read_text(encoding='utf-8')
    shared_styles = (ROOT / 'src/work-view.css').read_text(encoding='utf-8')
    template = template.replace('</style>', shared_styles + '</style>', 1)
    template = template.replace('<script>\n', '<script>' + shared_script + '</script>\n<script>\n', 1)
    analysis = build_analysis(catalog, editions, template, shared_script)
    payload = copy.deepcopy(analysis['catalog'])
    payload['reviews'] = analysis['reviews']
    payload['editions'] = editions
    serialized = json.dumps(payload, ensure_ascii=False).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    assert template.count('__RESEARCH_DATA__') == 1
    output = ROOT / 'index.html'
    output.write_text(template.replace('__RESEARCH_DATA__', serialized), encoding='utf-8')
    (ROOT / 'technologies.html').write_text(output.read_text(encoding='utf-8'), encoding='utf-8')
    print(json.dumps({'output': str(output), 'works': len(ids), 'organizations': len(org_ids), 'editions': len(editions), 'bytes': output.stat().st_size}, ensure_ascii=False))


def build_analysis(catalog, editions, template, shared_script):
    taxonomy = json.loads((ROOT / 'data/taxonomy.json').read_text(encoding='utf-8'))
    classifications = json.loads((ROOT / 'data/classifications.json').read_text(encoding='utf-8'))
    journal = json.loads((ROOT / 'data/research-journal.json').read_text(encoding='utf-8'))
    abstracts = json.loads((ROOT / 'data/abstracts.json').read_text(encoding='utf-8'))
    reviews = {}
    for path in sorted((ROOT / 'data').glob('reviews-*.json')):
        part = json.loads(path.read_text(encoding='utf-8'))
        assert not reviews.keys() & part.keys(), 'Duplicate review IDs'
        reviews.update(part)
    ids = {w['id'] for w in catalog['works']}
    assert set(classifications) == ids and set(reviews) == ids and set(abstracts) == ids, 'Every work needs classification, review and abstract status'
    analysis_catalog = copy.deepcopy(catalog)
    image_sources = {}
    required = {'editorialSummaryZh', 'baselines', 'resultSummary', 'verdict', 'conditions', 'attribution', 'cost', 'bestBaselineReason', 'sources', 'reviewedAt', 'depth'}
    for w in analysis_catalog['works']:
        w['classification'] = classifications[w['id']]
        for key, choices in taxonomy.items():
            assert w['classification'][key] and set(w['classification'][key]) <= set(choices), w['id']
        r = reviews[w['id']]
        a = abstracts[w['id']]
        assert a['status'] in {'translated', 'not_applicable', 'unavailable'}, w['id']
        dt.date.fromisoformat(a['verifiedAt'])
        assert a['verifiedAt'] <= catalog['asOf'], w['id']
        if a['status'] == 'translated':
            assert a['original'].strip() and a['translationZh'].strip() and a['sourceUrl'].startswith('https://') and a['sourceLabel'].strip(), w['id']
        else:
            assert a['note'].strip(), w['id']
        r['abstract'] = a
        assert required <= r.keys() and isinstance(r['baselines'], list) and r['sources'], w['id']
        assert all(s['url'].startswith('https://') for s in r['sources'])
        assert all(b['sourceUrl'].startswith('https://') for b in r['baselines'])
        assert r['reviewedAt'] <= catalog['asOf']
        asset = w.get('image', {}).get('local')
        if asset:
            path = ROOT / asset
            assert path.resolve().is_relative_to(ROOT), 'Image path must remain inside newspaper'
            assert path.is_file(), asset
            mime = mimetypes.guess_type(path.name)[0] or 'image/png'
            image_sources[w['id']] = 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode('ascii')
    memory = sync(analysis_catalog, editions, reviews, journal, taxonomy)
    analysis = dict(catalog=analysis_catalog, editions=editions, reviews=reviews, journal=journal, taxonomy=taxonomy, memory=memory)
    for w in analysis_catalog['works']:
        if w['id'] in image_sources:
            w['image']['src'] = image_sources[w['id']]
    raw = json.dumps(analysis, ensure_ascii=False).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    styles = re.search(r'<style>(.*?)</style>', template, re.S).group(1)
    page = (ROOT / 'src/analysis.html').read_text(encoding='utf-8').replace('研究日报', html.escape(catalog['title'])).replace('__BASE_STYLES__', styles).replace('__ANALYSIS_DATA__', raw).replace('__ANALYSIS_SCRIPT__', shared_script + '\n' + (ROOT / 'src/analysis.js').read_text(encoding='utf-8'))
    for filename in ['statistics.html', 'trends.html']:
        (ROOT / filename).write_text(page, encoding='utf-8')
    return analysis


if __name__ == '__main__':
    build()

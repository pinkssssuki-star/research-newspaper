"""Check build artifacts, archive consistency and append-only storage integrity."""
import json
import re
from pathlib import Path
from research_store import connect, current_snapshot

root=Path(__file__).resolve().parent
catalog=json.loads((root/'data/catalog.json').read_text(encoding='utf8'))
pages={}
for filename in ['index.html','technologies.html','statistics.html','trends.html']:
    text=(root/filename).read_text(encoding='utf8')
    pages[filename]=text
    assert '<!doctype html>' in text.lower(), filename
    assert '__RESEARCH_DATA__' not in text and '__ANALYSIS_DATA__' not in text, filename
def payload(filename, element_id):
    match=re.search(r'<script id="'+element_id+r'" type="application/json">(.*?)</script>',pages[filename],re.S)
    assert match, filename
    return json.loads(match.group(1))
daily=payload('index.html','researchData')
analysis=payload('statistics.html','analysisData')
assert daily['works']==analysis['catalog']['works'], 'Daily/statistics work or figure mismatch'
assert daily['reviews']==analysis['reviews'], 'Daily/statistics Abstract or review mismatch'
assert daily['reviews']==payload('technologies.html','researchData')['reviews']
assert analysis['reviews']==payload('trends.html','analysisData')['reviews']
assert set(daily['reviews'])=={w['id'] for w in catalog['works']}
for wid,review in daily['reviews'].items():
    abstract=review['abstract']
    assert 'editorialSummaryZh' in review, wid
    assert abstract['status'] in {'translated','not_applicable','unavailable'}, wid
    if abstract['status']=='translated':
        assert all(abstract[field].strip() for field in ['original','translationZh','sourceUrl','sourceLabel']), wid
    else:
        assert abstract['note'].strip(), wid
with connect(root/'data/research.sqlite3') as db:
    assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    latest=current_snapshot(db)
    assert latest and json.loads(latest[0])['reviews']==analysis['reviews'], 'Abstract/review snapshot differs from SQLite'
    for file in (root/'data/editions').glob('*.json'):
        e=json.loads(file.read_text(encoding='utf8'))
        row=db.execute('SELECT payload FROM revisions WHERE kind=? AND item_id=?',('edition',e.get('id',e['date']))).fetchone()
        assert row and json.loads(row[0])==e, file
print('Shared work data/figures, Abstracts, reviews, immutable editions and SQLite integrity verified. Visual QA is separate.')

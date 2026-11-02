import importlib.util
from contextlib import closing
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('bootstrap',SKILL/'scripts/init_report.py')
bootstrap=importlib.util.module_from_spec(spec);spec.loader.exec_module(bootstrap)


class PortabilityTest(unittest.TestCase):
    def test_prediction_cannot_use_old_news_or_premature_miss(self):
        spec=importlib.util.spec_from_file_location('memory',SKILL/'assets/report/research_store.py')
        memory=importlib.util.module_from_spec(spec);spec.loader.exec_module(memory)
        catalog=dict(asOf='2026-11-01',works=[dict(id='old',date='2026-10-30',discoveredAt='2026-10-30')])
        forecast=dict(id='p',createdOn='2026-11-01',deadline='2027-01-01',probability=.6,evidenceIds=['old'])
        evaluation=dict(id='e',forecastId='p',evaluatedOn='2026-11-01',status='hit',rationale='test',sourceCoverage='test',evidenceIds=['old'],errorType='未发现明显误判',lesson='test',nextCheck='test')
        journal=dict(statements=[],forecasts=[forecast],evaluations=[evaluation])
        with self.assertRaises(AssertionError): memory.validate_journal(catalog,journal)
        evaluation['status']='miss'
        with self.assertRaises(AssertionError): memory.validate_journal(catalog,journal)

    def test_empty_then_append_and_immutable_issue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=bootstrap.initialize(Path(tmp)/'paper','软件供应链','可复现证据','Asia/Shanghai','2026-11-01')
            def run(script,success=True):
                result=subprocess.run([sys.executable,'-X','utf8',str(root/script)],capture_output=True,text=True,encoding='utf8')
                self.assertEqual(result.returncode==0,success,result.stdout+result.stderr)
            def load(name): return json.loads((root/name).read_text(encoding='utf8'))
            def save(name,value): (root/name).write_text(json.dumps(value,ensure_ascii=False),encoding='utf8')
            run('build.py');run('check_report.py')
            self.assertEqual(load('data/abstracts.json'),{})
            self.assertIn('软件供应链日报',(root/'index.html').read_text(encoding='utf8'))
            with self.assertRaises(FileExistsError):
                bootstrap.initialize(root,'other','other','UTC','2026-11-01')
            # Synthetic fixture; never shipped as a research finding.
            catalog=load('data/catalog.json')
            work=dict(id='fixture',short='Synthetic test',title='Synthetic fixture, not a paper',date='2026-11-01',dateType='test',firstPublishedAt='2026-11-01',orgIds=['fixture-team'],tags=['security'],headline='Fixture',summary='Fixture only',facts=['Fixture'],limits='Not real research',relevance='Test',sources=[dict(label='Fixture',url='https://example.org')],affiliationNote='Synthetic',evidenceType='test',resources='none',discoveredAt='2026-11-01',verifiedAt='2026-11-01',techIds=[],image=dict(local='assets/fixture.svg',sourceUrl='https://example.org/figure',caption='Synthetic figure',credit='Test fixture'))
            (root/'assets/fixture.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"><rect width="20" height="20"/></svg>',encoding='utf8')
            catalog['works']=[work]
            catalog['organizations']=[dict(id='fixture-team',short='Fixture',name='Fixture',symbol='T',category='Test',evidenceIds=['fixture'],trendTitle='Test',observed='Test',hypothesis='Test',caveat='Test',confidence='Test')]
            save('data/catalog.json',catalog)
            taxonomy=load('data/taxonomy.json')
            save('data/classifications.json',{'fixture':dict(model=[taxonomy['model'][0]],workType=['模型 / 方法'],embodiment=[taxonomy['embodiment'][0]],basis='Synthetic')})
            review=dict(reviewedAt='2026-11-01',depth='官方材料',editorialSummaryZh='Editorial explanation',baselines=[dict(name='Fixture baseline',setting='Matched fixture setting',result='Fixture result',sourceUrl='https://example.org/table')],resultSummary='Synthetic outcome',verdict='Fixture usefulness',conditions=[dict(factor='Data budget',observation='Fixture extra data',impact='Possible confounding')],attribution=dict(main='Fixture training data',evidence='Fixture ablation',confidence='low',unresolved='Fixture uncertainty'),cost='Fixture compute cost',bestBaselineReason='Fixture baseline explanation',sources=[dict(label='Fixture',url='https://example.org',locator='Synthetic')])
            save('data/reviews-current.json',{'fixture':review})
            abstract=dict(status='translated',original='Original synthetic abstract with a limitation.',translationZh='合成摘要译文，保留限制。',sourceUrl='https://example.org/paper-v1',sourceLabel='Synthetic v1 Abstract',verifiedAt='2026-11-01')
            save('data/abstracts.json',{'fixture':abstract})
            edition=dict(date='2026-11-01',label='Test',windowStart='2026-10-26',featuredIds=['fixture'],headline='Synthetic',deck='Synthetic',notes=[])
            save('data/editions/2026-11-01.json',edition)
            run('build.py');run('check_report.py')
            daily=json.loads(re.search(r'<script id="researchData" type="application/json">(.*?)</script>',(root/'index.html').read_text(encoding='utf8'),re.S).group(1))
            stats=json.loads(re.search(r'<script id="analysisData" type="application/json">(.*?)</script>',(root/'statistics.html').read_text(encoding='utf8'),re.S).group(1))
            self.assertEqual(daily['reviews']['fixture']['abstract'],abstract)
            self.assertEqual(daily['reviews'],stats['reviews'])
            self.assertEqual(daily['works'],stats['catalog']['works'])
            self.assertTrue(stats['catalog']['works'][0]['image']['src'].startswith('data:image/svg+xml;base64,'))
            node=os.environ.get('NODE_BINARY') or shutil.which('node')
            if node:
                # Exercise the shared renderer, not just the presence of its headings.
                result=subprocess.run([node,'-',str(root)],input=r'''
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict'),path=require('path');
const root=process.argv[2],read=file=>fs.readFileSync(path.join(root,file),'utf8');
const payload=(file,id)=>JSON.parse(read(file).match(new RegExp('<script id="'+id+'" type="application/json">([\\s\\S]*?)</script>'))[1]);
const daily=payload('index.html','researchData'),stats=payload('statistics.html','analysisData');
const make=vm.runInNewContext(read('src/work-view.js')+';createWorkView',{URL});
const a=make(daily,daily.reviews,()=>daily.asOf),b=make(stats.catalog,stats.reviews,()=>daily.asOf);
assert.equal(a.card(daily.works[0]),b.card(stats.catalog.works[0]));
assert.equal(a.detail('fixture'),b.detail('fixture'));
for(const text of ['合成摘要译文，保留限制。','Original synthetic abstract with a limitation.','Fixture baseline','Matched fixture setting','Fixture usefulness','Fixture extra data','Fixture baseline explanation','Fixture training data','Fixture compute cost','Editorial explanation'])assert.ok(a.detail('fixture').includes(text),text);
assert.ok(a.card(daily.works[0]).includes('data:image/svg+xml;base64,'));
for(const file of ['index.html','technologies.html','statistics.html','trends.html'])for(const script of read(file).matchAll(/<script(?![^>]*type="application\/json")[^>]*>([\s\S]*?)<\/script>/g))new vm.Script(script[1],{filename:file});
''',capture_output=True,text=True,encoding='utf8')
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            with closing(sqlite3.connect(root/'data/research.sqlite3')) as db:
                before=db.execute('SELECT COUNT(*) FROM revisions').fetchone()[0]
            run('build.py')
            with closing(sqlite3.connect(root/'data/research.sqlite3')) as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM revisions').fetchone()[0],before)
            # A paraphrase cannot satisfy the new Abstract contract or alter history.
            legacy={**review,'abstractZh':review['editorialSummaryZh']}
            legacy.pop('editorialSummaryZh')
            save('data/reviews-current.json',{'fixture':legacy});run('build.py',success=False)
            save('data/reviews-current.json',{'fixture':review})
            bad={**abstract,'original':''}
            save('data/abstracts.json',{'fixture':bad});run('build.py',success=False)
            bad={**abstract,'translationZh':'   '}
            save('data/abstracts.json',{'fixture':bad});run('build.py',success=False)
            with closing(sqlite3.connect(root/'data/research.sqlite3')) as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM revisions').fetchone()[0],before)
            save('data/abstracts.json',{'fixture':abstract})
            # Preserve the image path boundary before any database mutation.
            work['image']['local']='../outside.svg';save('data/catalog.json',catalog)
            run('build.py',success=False)
            with closing(sqlite3.connect(root/'data/research.sqlite3')) as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM revisions').fetchone()[0],before)
            work['image']['local']='assets/fixture.svg';save('data/catalog.json',catalog)
            for status in ['not_applicable','unavailable']:
                missing=dict(status=status,note='Explicit synthetic access/absence explanation',verifiedAt='2026-11-01')
                save('data/abstracts.json',{'fixture':missing});run('build.py');run('check_report.py')
            with closing(sqlite3.connect(root/'data/research.sqlite3')) as db:
                history=[json.loads(row[0]) for row in db.execute("SELECT payload FROM revisions WHERE kind='review' AND item_id='fixture'")]
                self.assertEqual(len(history),3)
                self.assertIn(abstract,[r['abstract'] for r in history])
            save('data/abstracts.json',{'fixture':abstract})
            # Restoring an earlier snapshot must select it without rewriting history.
            with closing(sqlite3.connect(root/'data/research.sqlite3')) as db:
                snapshots_before=db.execute('SELECT digest,recorded_at,payload FROM snapshots ORDER BY digest').fetchall()
            run('build.py');run('check_report.py')
            with closing(sqlite3.connect(root/'data/research.sqlite3')) as db:
                self.assertEqual(db.execute('SELECT digest,recorded_at,payload FROM snapshots ORDER BY digest').fetchall(),snapshots_before)
                current=db.execute("SELECT s.payload FROM snapshots s JOIN build_state b ON b.digest=s.digest WHERE b.name='current build'").fetchone()
                self.assertEqual(json.loads(current[0])['reviews']['fixture']['abstract'],abstract)
            supplement={**edition,'id':'2026-11-01-r2','revision':2,'label':'Supplement'}
            save('data/editions/2026-11-01-r2.json',supplement)
            run('build.py');run('check_report.py')
            with closing(sqlite3.connect(root/'data/research.sqlite3')) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM revisions WHERE kind='edition'").fetchone()[0],2)
            edition['headline']='Invalid rewrite'
            save('data/editions/2026-11-01.json',edition)
            run('build.py',success=False)


if __name__=='__main__': unittest.main()

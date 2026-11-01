import importlib.util
from contextlib import closing
import json
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
            self.assertIn('软件供应链日报',(root/'index.html').read_text(encoding='utf8'))
            with self.assertRaises(FileExistsError):
                bootstrap.initialize(root,'other','other','UTC','2026-11-01')
            # Synthetic fixture; never shipped as a research finding.
            catalog=load('data/catalog.json')
            work=dict(id='fixture',short='Synthetic test',title='Synthetic fixture, not a paper',date='2026-11-01',dateType='test',firstPublishedAt='2026-11-01',orgIds=['fixture-team'],tags=['security'],headline='Fixture',summary='Fixture only',facts=['Fixture'],limits='Not real research',relevance='Test',sources=[dict(label='Fixture',url='https://example.org')],affiliationNote='Synthetic',evidenceType='test',resources='none',discoveredAt='2026-11-01',verifiedAt='2026-11-01',techIds=[])
            catalog['works']=[work]
            catalog['organizations']=[dict(id='fixture-team',short='Fixture',name='Fixture',symbol='T',category='Test',evidenceIds=['fixture'],trendTitle='Test',observed='Test',hypothesis='Test',caveat='Test',confidence='Test')]
            save('data/catalog.json',catalog)
            taxonomy=load('data/taxonomy.json')
            save('data/classifications.json',{'fixture':dict(model=[taxonomy['model'][0]],workType=['模型 / 方法'],embodiment=[taxonomy['embodiment'][0]],basis='Synthetic')})
            review=dict(reviewedAt='2026-11-01',depth='官方材料',abstractZh='Synthetic',baselines=[],resultSummary='Synthetic',verdict='Synthetic',conditions=[],attribution=dict(main='Unknown',evidence='Synthetic',confidence='low',unresolved='Synthetic'),cost='Synthetic',bestBaselineReason='No comparison',sources=[dict(label='Fixture',url='https://example.org',locator='Synthetic')])
            save('data/reviews-current.json',{'fixture':review})
            edition=dict(date='2026-11-01',label='Test',windowStart='2026-10-26',featuredIds=['fixture'],headline='Synthetic',deck='Synthetic',notes=[])
            save('data/editions/2026-11-01.json',edition)
            run('build.py');run('check_report.py')
            with closing(sqlite3.connect(root/'data/research.sqlite3')) as db:
                before=db.execute('SELECT COUNT(*) FROM revisions').fetchone()[0]
            run('build.py')
            with closing(sqlite3.connect(root/'data/research.sqlite3')) as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM revisions').fetchone()[0],before)
            supplement={**edition,'id':'2026-11-01-r2','revision':2,'label':'Supplement'}
            save('data/editions/2026-11-01-r2.json',supplement)
            run('build.py');run('check_report.py')
            with closing(sqlite3.connect(root/'data/research.sqlite3')) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM revisions WHERE kind='edition'").fetchone()[0],2)
            edition['headline']='Invalid rewrite'
            save('data/editions/2026-11-01.json',edition)
            run('build.py',success=False)


if __name__=='__main__': unittest.main()

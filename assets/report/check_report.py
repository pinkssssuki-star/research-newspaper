"""Check build artifacts, archive consistency and append-only storage integrity."""
import json
import sqlite3
from pathlib import Path

root=Path(__file__).resolve().parent
catalog=json.loads((root/'data/catalog.json').read_text(encoding='utf8'))
for filename in ['index.html','technologies.html','statistics.html','trends.html']:
    text=(root/filename).read_text(encoding='utf8')
    assert '<!doctype html>' in text.lower(), filename
    assert '__RESEARCH_DATA__' not in text and '__ANALYSIS_DATA__' not in text, filename
with sqlite3.connect(root/'data/research.sqlite3') as db:
    assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    for file in (root/'data/editions').glob('*.json'):
        e=json.loads(file.read_text(encoding='utf8'))
        row=db.execute('SELECT payload FROM revisions WHERE kind=? AND item_id=?',('edition',e.get('id',e['date']))).fetchone()
        assert row and json.loads(row[0])==e, file
print('Artifacts, immutable editions and SQLite integrity verified. Visual QA is separate.')

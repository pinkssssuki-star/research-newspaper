"""Append-only local research memory; no external service or model API required."""
import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'data/research.sqlite3'


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


@contextmanager
def connect(path=DB):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.executescript('''
      CREATE TABLE IF NOT EXISTS revisions (
        kind TEXT NOT NULL, item_id TEXT NOT NULL, digest TEXT NOT NULL,
        recorded_at TEXT NOT NULL, payload TEXT NOT NULL,
        PRIMARY KEY(kind,item_id,digest));
      CREATE TABLE IF NOT EXISTS snapshots (
        digest TEXT PRIMARY KEY, as_of TEXT NOT NULL, recorded_at TEXT NOT NULL,
        origin TEXT NOT NULL, payload TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS build_state (
        name TEXT PRIMARY KEY, digest TEXT NOT NULL REFERENCES snapshots(digest));
      CREATE TRIGGER IF NOT EXISTS revisions_no_update BEFORE UPDATE ON revisions
        BEGIN SELECT RAISE(ABORT,'Research history is append-only'); END;
      CREATE TRIGGER IF NOT EXISTS revisions_no_delete BEFORE DELETE ON revisions
        BEGIN SELECT RAISE(ABORT,'Research history is append-only'); END;
      CREATE TRIGGER IF NOT EXISTS snapshots_no_update BEFORE UPDATE ON snapshots
        BEGIN SELECT RAISE(ABORT,'Research history is append-only'); END;
      CREATE TRIGGER IF NOT EXISTS snapshots_no_delete BEFORE DELETE ON snapshots
        BEGIN SELECT RAISE(ABORT,'Research history is append-only'); END;
    ''')
    try:
        with db:
            yield db
    finally:
        db.close()


def append(db, kind, item_id, payload, immutable=False):
    raw = encoded(payload)
    digest = hashlib.sha256(raw.encode()).hexdigest()
    previous = db.execute('SELECT digest FROM revisions WHERE kind=? AND item_id=?', (kind, item_id)).fetchall()
    if immutable and previous and any(row['digest'] != digest for row in previous):
        raise ValueError(f'Cannot rewrite registered {kind}: {item_id}; append a new record instead')
    db.execute('INSERT OR IGNORE INTO revisions VALUES (?,?,?,?,?)',
               (kind, item_id, digest, datetime.now(timezone.utc).isoformat(), raw))


def snapshot(db, payload, origin):
    raw = encoded(payload)
    digest = hashlib.sha256(raw.encode()).hexdigest()
    db.execute('INSERT OR IGNORE INTO snapshots VALUES (?,?,?,?,?)',
               (digest, payload['asOf'], datetime.now(timezone.utc).isoformat(), origin, raw))
    return digest


def current_snapshot(db):
    row = db.execute("SELECT s.payload FROM snapshots s JOIN build_state b ON b.digest=s.digest WHERE b.name='current build'").fetchone()
    if row is None:  # Existing newspapers acquire the pointer on their next build.
        row = db.execute("SELECT payload FROM snapshots WHERE origin='current build' ORDER BY recorded_at DESC LIMIT 1").fetchone()
    return row


def validate_journal(catalog, journal):
    works = {w['id']: w for w in catalog['works']}
    forecasts = {p['id']: p for p in journal['forecasts']}
    assert len(forecasts) == len(journal['forecasts']), 'Duplicate prediction IDs'
    for claim in journal['statements'] + journal['forecasts']:
        assert claim['createdOn'] <= catalog['asOf'], claim['id']
        for wid in claim['evidenceIds']:
            assert wid in works, wid
            assert works[wid]['discoveredAt'] <= claim['createdOn'], 'Future-known evidence: ' + wid
            assert works[wid]['date'] <= claim['createdOn'], 'Future event in a past claim: ' + wid
    for p in forecasts.values():
        assert 0 < p['probability'] < 1 and p['createdOn'] < p['deadline']
    evaluations = journal['evaluations']
    assert len({e['id'] for e in evaluations}) == len(evaluations)
    for e in evaluations:
        p = forecasts[e['forecastId']]
        assert p['createdOn'] <= e['evaluatedOn'] <= catalog['asOf']
        assert e['status'] in ['pending', 'hit', 'miss', 'unresolved', 'retracted']
        if e['status'] == 'miss':
            assert e['evaluatedOn'] >= p['deadline'], 'Cannot declare failure before deadline'
        if e['status'] in ['hit', 'miss']:
            assert e['rationale'] and e['evidenceIds'] and e['sourceCoverage']
            assert e.get('lesson') and e.get('nextCheck'), 'Resolved forecasts need a lesson and next check'
            assert e.get('errorType') in ['未发现明显误判', '遗漏信息', '样本偏差', '重复证据', '能力产品混用', '归因混杂', '过度外推', '其他']
        for wid in e['evidenceIds']:
            assert wid in works
            assert works[wid]['discoveredAt'] <= e['evaluatedOn']
            if e['status'] == 'hit':
                assert works[wid]['date'] > p['createdOn'], 'Old work cannot confirm a new prediction'


def sync(catalog, editions, reviews, journal, taxonomy):
    validate_journal(catalog, journal)
    with connect() as db:
        for w in catalog['works']:
            append(db, 'work', w['id'], w)
        for wid, review in reviews.items():
            append(db, 'review', wid, review)
        for e in editions:
            append(db, 'edition', e.get('id', e['date']), e, immutable=True)
        for kind, key in [('statement', 'statements'), ('forecast', 'forecasts'), ('evaluation', 'evaluations')]:
            for record in journal[key]:
                append(db, kind, record['id'], record, immutable=True)
        digest = snapshot(db, dict(asOf=catalog['asOf'], catalog=catalog, editions=editions, reviews=reviews, journal=journal, taxonomy=taxonomy), 'current build')
        db.execute("INSERT INTO build_state VALUES ('current build',?) ON CONFLICT(name) DO UPDATE SET digest=excluded.digest", (digest,))
        return dict(backend='SQLite', revisions=db.execute('SELECT COUNT(*) FROM revisions').fetchone()[0], snapshots=db.execute('SELECT COUNT(*) FROM snapshots').fetchone()[0], firstRegisteredOn=journal['startedOn'])


def history_payload():
    with connect() as db:
        return dict(revisions=[dict(r) for r in db.execute('SELECT kind,item_id,digest,recorded_at FROM revisions ORDER BY recorded_at')], snapshots=[dict(r) for r in db.execute('SELECT digest,as_of,recorded_at,origin FROM snapshots ORDER BY as_of,recorded_at')])

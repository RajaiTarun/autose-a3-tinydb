# Seeded PR 4: operations.append shares one new list between all documents updated in one call.
from tinydb import TinyDB
from tinydb.operations import append
from tinydb.storages import MemoryStorage

def test_append_creates_separate_lists():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'n': 1})
    db.insert({'n': 2})
    db.update(append('tags', 'x'))
    assert [d['tags'] for d in db.all()] == [['x'], ['x']]

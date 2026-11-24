# Seeded PR 1: Query.not_one_of hash leaves out the field path (C3) -> cache collision.
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

def test_not_one_of_is_per_field():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'a': 1, 'b': 9})
    assert db.search(Query().a.not_one_of([1])) == []
    assert db.search(Query().b.not_one_of([1])) == [{'a': 1, 'b': 9}]

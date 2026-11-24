# Seeded PR 2: Table.clear_field writes storage directly (bypasses _update_table, C5) -> stale query cache.
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

def test_clear_field_invalidates_cache():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'x': 1, 'y': 2})
    assert len(db.search(Query().x.exists())) == 1
    db.clear_field('x')
    assert db.search(Query().x.exists()) == []

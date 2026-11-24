"""Hidden tests for issue 5 (vague: "results should come back sorted").
The issue names no API, so these tests cannot call a new sort feature. They check
only that any interpretation keeps the existing behaviour (no regression). The main
measure for this issue is how the Spec stage handles the ambiguity (see results)."""
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def _db():
    db = TinyDB(storage=MemoryStorage)
    for n in [3, 1, 2]:
        db.insert({'n': n})
    return db


def test_default_search_order_is_unchanged_insertion_order():
    assert [d['n'] for d in _db().search(Query().n.exists())] == [3, 1, 2]


def test_default_all_order_is_unchanged_insertion_order():
    assert [d['n'] for d in _db().all()] == [3, 1, 2]

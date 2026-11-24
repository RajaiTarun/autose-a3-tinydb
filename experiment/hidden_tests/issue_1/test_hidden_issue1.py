"""Hidden acceptance tests for T1 (bug fix).

Copied into <repo>/tests/ only AFTER a run has finished, never during it.
Three tests: the user-visible symptom, the underlying cache-key property, and
a guard against "fixing" the bug by disabling the cache.
"""

from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def test_one_of_on_different_fields_does_not_share_results():
    """The reported symptom: a second field must not inherit the first's hits."""
    db = TinyDB(storage=MemoryStorage)
    db.insert({'a': 1, 'b': 9})

    # Warm the cache with a query that matches.
    assert len(db.search(Query().a.one_of([1, 2]))) == 1

    # Same item list, different field: must not match.
    assert db.search(Query().b.one_of([1, 2])) == []

    # And the first query must still be right afterwards.
    assert len(db.search(Query().a.one_of([1, 2]))) == 1


def test_one_of_queries_on_different_paths_are_distinct_cache_keys():
    """The property that makes the cache safe: different queries, different keys."""
    q_a = Query().a.one_of([1, 2])
    q_b = Query().b.one_of([1, 2])
    q_nested = Query().outer.a.one_of([1, 2])

    assert q_a != q_b
    assert q_a != q_nested

    # This is exactly how Table._query_cache looks a query up.
    cache = {q_a: 'result-for-a'}
    assert q_a in cache
    assert q_b not in cache
    assert q_nested not in cache

    # A genuinely identical query must still hit.
    assert Query().a.one_of([1, 2]) in cache


def test_one_of_is_still_cacheable_after_the_fix():
    """Guard: the bug must not be fixed by making one_of uncacheable.

    Deliberately fails three different ways, so it cannot pass by accident:
    with the defect present the two queries collapse to one cache entry; with
    caching disabled there are none; only a correct fix gives two.
    """
    db = TinyDB(storage=MemoryStorage)
    table = db.table('t')
    table.insert({'a': 1, 'b': 9})

    on_a = Query().a.one_of([1, 2])
    on_b = Query().b.one_of([1, 2])

    assert on_a.is_cacheable() is True
    assert on_b.is_cacheable() is True

    assert len(table.search(on_a)) == 1
    assert table.search(on_b) == []

    assert on_a in table._query_cache
    assert on_b in table._query_cache
    assert len(table._query_cache) == 2

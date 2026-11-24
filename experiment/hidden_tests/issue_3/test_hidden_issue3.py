"""Hidden acceptance tests for T2 (local feature: Query.between).

Copied into <repo>/tests/ only AFTER a run has finished, never during it.
"""

from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def _db(docs):
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple(docs)
    return db


def test_between_matches_inclusive_range():
    db = _db([{'age': 17}, {'age': 18}, {'age': 40}, {'age': 65}, {'age': 66}])

    found = db.search(Query().age.between(18, 65))

    assert sorted(doc['age'] for doc in found) == [18, 40, 65]


def test_between_skips_missing_and_incomparable_values_without_raising():
    db = _db([
        {'age': 30},            # matches
        {'name': 'no age'},     # field missing
        {'age': 'thirty'},      # str vs int is not comparable
        {'age': None},          # None vs int is not comparable
    ])

    found = db.search(Query().age.between(18, 65))

    assert [dict(doc) for doc in found] == [{'age': 30}]


def test_between_composes_and_works_on_a_nested_path():
    db = _db([
        {'user': {'age': 30}, 'active': True},
        {'user': {'age': 70}, 'active': True},
        {'user': {'age': 25}, 'active': False},
    ])

    in_range = Query().user.age.between(18, 65)

    assert len(db.search(in_range & (Query().active == True))) == 1   # noqa: E712
    assert len(db.search(~in_range)) == 1
    assert db.count(in_range) == 2
    assert db.get(in_range) is not None


def test_between_is_cacheable_and_keys_distinctly():
    """Same trap as T1: bounds and path must both be in the hash value."""
    same_field_same_bounds = Query().age.between(18, 65)
    other_field = Query().score.between(18, 65)
    other_bounds = Query().age.between(18, 99)

    assert same_field_same_bounds.is_cacheable() is True

    cache = {same_field_same_bounds: 'cached'}
    assert Query().age.between(18, 65) in cache
    assert other_field not in cache
    assert other_bounds not in cache

"""Tests for the one_of() query-cache collision (issue 4).

Each test goes through the public API (TinyDB, Query, search, insert) and
uses an in-memory storage, so the query cache is exercised across calls.
"""
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def make_db():
    return TinyDB(storage=MemoryStorage)


def test_ac001_same_list_different_field_not_shared():
    db = make_db()
    db.insert({'a': 1, 'b': 9})

    first = db.search(Query().a.one_of([1, 2]))
    second = db.search(Query().b.one_of([1, 2]))

    assert first == [{'a': 1, 'b': 9}]
    assert second == []


def test_ac002_reverse_order_different_field_not_shared():
    db = make_db()
    db.insert({'a': 1, 'b': 9})

    first = db.search(Query().b.one_of([1, 2]))
    second = db.search(Query().a.one_of([1, 2]))

    assert first == []
    assert second == [{'a': 1, 'b': 9}]


def test_ac003_second_field_finds_its_own_document():
    db = make_db()
    db.insert({'a': 1, 'b': 1})
    db.insert({'c': 1})

    first = db.search(Query().a.one_of([1]))
    second = db.search(Query().c.one_of([1]))

    assert first == [{'a': 1, 'b': 1}]
    assert second == [{'c': 1}]


def test_ac004_same_field_different_list_not_shared():
    db = make_db()
    db.insert({'a': 1, 'b': 9})

    first = db.search(Query().a.one_of([1, 2]))
    second = db.search(Query().a.one_of([9]))

    assert first == [{'a': 1, 'b': 9}]
    assert second == []


def test_ac005_missing_field_returns_empty():
    db = make_db()
    db.insert({'a': 1, 'b': 9})

    assert db.search(Query().x.one_of([1, 2])) == []


def test_ac006_insert_invalidates_cached_empty_result():
    db = make_db()
    db.insert({'a': 1, 'b': 9})

    assert db.search(Query().b.one_of([1, 2])) == []

    db.insert({'b': 2})

    assert db.search(Query().b.one_of([1, 2])) == [{'b': 2}]

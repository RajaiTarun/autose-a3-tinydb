from tinydb import TinyDB, Query
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import MemoryStorage


def make_db(*docs):
    db = TinyDB(storage=MemoryStorage)
    for d in docs:
        db.insert(d)
    return db


def test_ac001_one_of_match():
    db = make_db({'a': 1, 'b': 9})
    assert db.search(Query().a.one_of([1, 2])) == [{'a': 1, 'b': 9}]


def test_ac002_a_then_b():
    db = make_db({'a': 1, 'b': 9})
    db.search(Query().a.one_of([1, 2]))
    assert db.search(Query().b.one_of([1, 2])) == []


def test_ac003_b_then_a():
    db = make_db({'a': 1, 'b': 9})
    db.search(Query().b.one_of([1, 2]))
    assert db.search(Query().a.one_of([1, 2])) == [{'a': 1, 'b': 9}]


def test_ac004_same_query_twice():
    db = make_db({'a': 1}, {'a': 3})
    assert db.search(Query().a.one_of([1, 2])) == [{'a': 1}]
    assert db.search(Query().a.one_of([1, 2])) == [{'a': 1}]


def test_ac005_empty_list():
    db = make_db({'a': 1})
    assert db.search(Query().a.one_of([])) == []


def test_ac006_missing_field():
    db = make_db({'a': 1}, {'b': 1})
    assert db.search(Query().a.one_of([1])) == [{'a': 1}]


def test_ac007_mix_with_eq():
    db = make_db({'a': 1}, {'a': 2})
    db.search(Query().a == 1)
    assert db.search(Query().a.one_of([1])) == [{'a': 1}]

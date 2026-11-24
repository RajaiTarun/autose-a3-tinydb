"""Hidden acceptance tests for issue 2 (subtract with a negative amount).
Copied into the repo only AFTER a run has finished."""
from tinydb import TinyDB, Query
from tinydb.operations import subtract
from tinydb.storages import MemoryStorage


def _db(value):
    db = TinyDB(storage=MemoryStorage)
    db.insert({'user': 'sam', 'balance': value})
    return db


def test_subtract_negative_int_increases_value():
    db = _db(100)
    db.update(subtract('balance', -10), Query().user == 'sam')
    assert db.get(Query().user == 'sam')['balance'] == 110


def test_subtract_negative_float_increases_value():
    db = _db(1.0)
    db.update(subtract('balance', -2.5), Query().user == 'sam')
    assert db.get(Query().user == 'sam')['balance'] == 3.5


def test_subtract_positive_still_decreases_value():
    db = _db(100)
    db.update(subtract('balance', 10), Query().user == 'sam')
    assert db.get(Query().user == 'sam')['balance'] == 90

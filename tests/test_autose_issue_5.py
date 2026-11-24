"""Acceptance tests for issue 5: subtract() with a negative amount must subtract it."""
from tinydb import TinyDB, where
from tinydb.operations import subtract
from tinydb.storages import MemoryStorage


def _db_with_sam():
    db = TinyDB(storage=MemoryStorage)
    db.drop_tables()
    db.insert({'user': 'sam', 'balance': 100})
    return db


def test_ac001_negative_int_adds_magnitude_via_update():
    db = _db_with_sam()
    db.update(subtract('balance', -10), where('user') == 'sam')
    assert db.get(where('user') == 'sam')['balance'] == 110


def test_ac002_negative_float_adds_magnitude_via_update():
    db = _db_with_sam()
    db.update(subtract('balance', -2.5), where('user') == 'sam')
    assert db.get(where('user') == 'sam')['balance'] == 102.5


def test_ac003_positive_amount_still_decreases():
    db = _db_with_sam()
    db.update(subtract('balance', 10), where('user') == 'sam')
    assert db.get(where('user') == 'sam')['balance'] == 90


def test_ac004_zero_amount_leaves_value_unchanged():
    db = _db_with_sam()
    db.update(subtract('balance', 0), where('user') == 'sam')
    assert db.get(where('user') == 'sam')['balance'] == 100


def test_ac005_existing_subtract_fixture_shape_gives_minus_four():
    db = TinyDB(storage=MemoryStorage)
    db.drop_tables()
    db.insert_multiple({'int': 1, 'char': c} for c in 'abc')
    db.update(subtract('int', 5), where('char') == 'a')
    assert db.get(where('char') == 'a')['int'] == -4

import pytest

from tinydb import TinyDB, where
from tinydb.operations import add, increment, decrement, subtract
from tinydb.storages import MemoryStorage


@pytest.fixture
def bdb():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'user': 'sam', 'balance': 100})
    return db


def _bal(db):
    return db.get(where('user') == 'sam')['balance']


def test_ac001_negative_int_adds(bdb):
    bdb.update(subtract('balance', -10), where('user') == 'sam')
    assert _bal(bdb) == 110


def test_ac002_negative_float_adds(bdb):
    bdb.update(subtract('balance', -2.5), where('user') == 'sam')
    assert _bal(bdb) == 102.5


def test_ac003_positive_subtracts(bdb):
    bdb.update(subtract('balance', 10), where('user') == 'sam')
    assert _bal(bdb) == 90


def test_ac004_zero_unchanged(bdb):
    bdb.update(subtract('balance', 0), where('user') == 'sam')
    assert _bal(bdb) == 100


def test_ac005_str_raises_and_unchanged(bdb):
    with pytest.raises(TypeError):
        bdb.update(subtract('balance', 'x'), where('user') == 'sam')
    assert _bal(bdb) == 100


def test_ac006_other_ops_unchanged():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'int': 1})
    db.update(add('int', -3))
    db.update(increment('int'))
    db.update(decrement('int'))
    assert db.all()[0]['int'] == -2

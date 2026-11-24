from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def _db_with_ages(ages):
    db = TinyDB(storage=MemoryStorage)
    for age in ages:
        db.insert({'age': age})
    return db


def test_ac001_inclusive_range(tmp_path):
    db = _db_with_ages([17, 18, 40, 65, 66])
    result = db.search(Query().age.between(18, 65))
    assert sorted(d['age'] for d in result) == [18, 40, 65]


def test_ac002_nested_path():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'user': {'age': 30}})
    db.insert({'user': {'age': 70}})
    result = db.search(Query().user.age.between(18, 65))
    assert result == [{'user': {'age': 30}}]


def test_ac003_missing_and_incomparable_do_not_match():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'age': 30})
    db.insert({'name': 'no age'})
    db.insert({'age': 'old'})
    db.insert({'age': None})
    result = db.search(Query().age.between(18, 65))
    assert result == [{'age': 30}]


def test_ac004_composition_with_and_or_not():
    db = _db_with_ages([10, 30, 70])
    assert db.search(Query().age.between(18, 65) & ~(Query().age == 30)) == []
    result = db.search(~Query().age.between(18, 65))
    assert sorted(d['age'] for d in result) == [10, 70]


def test_ac005_get_count_remove(tmp_path):
    db = _db_with_ages([20, 30, 70])
    first = db.get(Query().age.between(18, 65))
    assert first is not None and first['age'] in (20, 30)
    assert db.count(Query().age.between(18, 65)) == 2
    db.remove(Query().age.between(18, 65))
    assert [d['age'] for d in db.all()] == [70]


def test_ac006_cache_distinguishes_bounds():
    db = _db_with_ages([20, 25, 30, 40, 70])
    wide = db.search(Query().age.between(18, 65))
    assert sorted(d['age'] for d in wide) == [20, 25, 30, 40]
    narrow = db.search(Query().age.between(18, 30))
    assert sorted(d['age'] for d in narrow) == [20, 25, 30]


def test_ac007_reversed_bounds_empty():
    db = _db_with_ages([20, 30])
    assert db.search(Query().age.between(65, 18)) == []


def test_ac008_existing_ge_le_unchanged():
    db = _db_with_ages([17, 18, 65])
    result = db.search((Query().age >= 18) & (Query().age <= 65))
    assert sorted(d['age'] for d in result) == [18, 65]

import gzip
import json

from tinydb import TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import GzipJSONStorage, JSONStorage


GZIP_MAGIC = b'\x1f\x8b'


def test_ac001_new_file_starts_empty(tmp_path):
    path = str(tmp_path / 'data.json.gz')
    db = TinyDB(path, storage=GzipJSONStorage)
    assert db.all() == []
    db.close()


def test_ac002_zero_byte_file_reads_as_empty(tmp_path):
    path = tmp_path / 'data.json.gz'
    path.write_bytes(b'')
    assert path.stat().st_size == 0
    db = TinyDB(str(path), storage=GzipJSONStorage)
    assert db.all() == []
    db.close()


def test_ac003_data_survives_close_and_reopen(tmp_path):
    path = str(tmp_path / 'data.json.gz')
    db = TinyDB(path, storage=GzipJSONStorage)
    db.insert({'name': 'a'})
    db.close()

    db = TinyDB(path, storage=GzipJSONStorage)
    assert db.all() == [{'name': 'a'}]
    db.close()


def test_ac004_file_is_standard_gzip_json(tmp_path):
    path = tmp_path / 'data.json.gz'
    db = TinyDB(str(path), storage=GzipJSONStorage)
    db.insert({'name': 'a'})
    db.close()

    with gzip.open(str(path), 'rt') as f:
        assert json.load(f) == {'_default': {'1': {'name': 'a'}}}

    assert path.read_bytes()[:2] == GZIP_MAGIC


def test_ac005_works_with_caching_middleware_writes_on_close(tmp_path):
    path = str(tmp_path / 'data.json.gz')
    db = TinyDB(path, storage=CachingMiddleware(GzipJSONStorage))
    db.insert({'name': 'a'})
    # no explicit flush: data is only written on close
    db.close()

    db = TinyDB(path, storage=GzipJSONStorage)
    assert db.all() == [{'name': 'a'}]
    db.close()


def test_ac006_json_storage_unchanged(tmp_path):
    path = tmp_path / 'plain.json'
    db = TinyDB(str(path), storage=JSONStorage)
    db.insert({'name': 'a'})
    db.close()

    raw = path.read_bytes()
    assert not raw.startswith(GZIP_MAGIC)
    assert json.loads(raw) == {'_default': {'1': {'name': 'a'}}}

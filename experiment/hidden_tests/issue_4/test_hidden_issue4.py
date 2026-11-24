"""Hidden acceptance tests for T3 (cross-component: GzipJSONStorage).

Copied into <repo>/tests/ only AFTER a run has finished, never during it.
"""

import gzip
import json
import tomllib
from pathlib import Path

import pytest

from tinydb import TinyDB, JSONStorage
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import Storage, MemoryStorage


def _repo_root():
    for parent in Path(__file__).resolve().parents:
        if (parent / 'pyproject.toml').exists():
            return parent
    raise AssertionError('could not locate repository root')


def test_gzip_storage_roundtrips_and_writes_a_real_gzip_file(tmp_path):
    from tinydb.storages import GzipJSONStorage

    path = tmp_path / 'db.json.gz'

    with TinyDB(str(path), storage=GzipJSONStorage) as db:
        db.insert({'x': 1})
        db.insert({'x': 2})

    assert path.exists()
    raw = path.read_bytes()

    # It is gzip...
    assert raw[:2] == b'\x1f\x8b', 'file does not start with the gzip magic number'

    # ...and it is not plain JSON.
    with pytest.raises((UnicodeDecodeError, json.JSONDecodeError)):
        json.loads(raw.decode('utf-8'))

    # Standard gzip tooling can read it back.
    with gzip.open(path, 'rt', encoding='utf-8') as handle:
        assert '_default' in json.load(handle)

    # And TinyDB can reopen it.
    with TinyDB(str(path), storage=GzipJSONStorage) as db:
        assert sorted(doc['x'] for doc in db.all()) == [1, 2]


def test_gzip_storage_honours_the_storage_contract(tmp_path):
    from tinydb.storages import GzipJSONStorage

    assert issubclass(GzipJSONStorage, Storage)

    path = tmp_path / 'fresh.json.gz'
    storage = GzipJSONStorage(str(path))
    try:
        # An empty database is signalled with None, not {} and not an exception.
        assert storage.read() is None
        storage.write({'t': {'1': {'a': 1}}})
    finally:
        storage.close()

    reopened = GzipJSONStorage(str(path))
    try:
        assert reopened.read() == {'t': {'1': {'a': 1}}}
    finally:
        reopened.close()


def test_gzip_storage_works_behind_caching_middleware(tmp_path):
    from tinydb.storages import GzipJSONStorage

    path = tmp_path / 'cached.json.gz'

    # CachingMiddleware holds writes back; closing must flush them.
    with TinyDB(str(path), storage=CachingMiddleware(GzipJSONStorage)) as db:
        for i in range(5):
            db.insert({'i': i})

    with TinyDB(str(path), storage=GzipJSONStorage) as db:
        assert sorted(doc['i'] for doc in db.all()) == [0, 1, 2, 3, 4]


def test_no_new_runtime_dependency_and_existing_storages_unaffected(tmp_path):
    # The feature has to exist for this check to mean anything: without the
    # import the test would pass on an untouched repository.
    from tinydb.storages import GzipJSONStorage
    assert issubclass(GzipJSONStorage, Storage)

    manifest = tomllib.loads((_repo_root() / 'pyproject.toml').read_text())
    assert not manifest.get('project', {}).get('dependencies'), \
        'TinyDB must keep zero runtime dependencies'

    # The storages that already existed still behave the same.
    json_path = tmp_path / 'plain.json'
    with TinyDB(str(json_path), storage=JSONStorage) as db:
        db.insert({'kept': True})
    assert json.loads(json_path.read_text())['_default']['1'] == {'kept': True}

    memory_db = TinyDB(storage=MemoryStorage)
    memory_db.insert({'kept': True})
    assert memory_db.all() == [{'kept': True}]

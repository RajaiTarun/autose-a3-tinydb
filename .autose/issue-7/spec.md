# Spec: Add a gzip-compressed JSON storage (GzipJSONStorage)

## Problem
The user has JSON database files of hundreds of MB that compress well and asks for a storage that writes gzip-compressed JSON: "Could TinyDB have a storage that writes gzip-compressed JSON?" They want `TinyDB('data.json.gz', storage=GzipJSONStorage)` with `from tinydb.storages import GzipJSONStorage` to behave like the normal JSON storage: a new file starts empty, data survives close and reopen, the file opens with normal gzip tools, and it works with `CachingMiddleware`, including writes that only happen on close. The existing storages must not change. Currently `tinydb/storages.py` only provides `JSONStorage` and `MemoryStorage` (storages.py:79, storages.py:164), and `__all__` lists only those (storages.py:13).

## Requirements
- FR-1: A class `GzipJSONStorage` is importable from `tinydb.storages` and used as `TinyDB(path, storage=GzipJSONStorage)`. CONFIRMED: "from tinydb.storages import GzipJSONStorage ... TinyDB('data.json.gz', storage=GzipJSONStorage)".
- FR-2: A new file at the path starts as an empty database. CONFIRMED: "a new file starts empty".
- FR-3: Data written and closed is present after reopening the same path. CONFIRMED: "data is still there after I close and reopen it".
- FR-4: The file on disk is gzip-compressed JSON readable by standard gzip tools. CONFIRMED: "The file should open with normal gzip tools."
- FR-5: Works with `CachingMiddleware`, including data written only on close. CONFIRMED: "We also use CachingMiddleware, so it needs to work with that too (including writes that only happen on close)."
- FR-6: `JSONStorage` and `MemoryStorage` behaviour is unchanged. CONFIRMED: "Please don't change how the existing storages behave."
- FR-7: A zero-byte file at the path is read as an empty database, not as an error. INFERRED: the issue asks for JSON-storage-like behaviour, and `JSONStorage.read` returns `None` for a zero-size file (storages.py:131-134).
- FR-8: The constructor accepts the same `path` argument as `JSONStorage`. INFERRED: "behave like the normal JSON storage" (storages.py:84), and `TinyDB` forwards its arguments to the storage class (database.py:95).

## Acceptance criteria
- AC-001: Given no file exists at `tmp/data.json.gz`, When I create `TinyDB('tmp/data.json.gz', storage=GzipJSONStorage)` and call `db.all()`, Then it returns `[]` and raises no exception.
- AC-002: Given a zero-byte file exists at `tmp/data.json.gz`, When I create `TinyDB('tmp/data.json.gz', storage=GzipJSONStorage)` and call `db.all()`, Then it returns `[]` and raises no exception.
- AC-003: Given an empty database at `tmp/data.json.gz`, When I insert `{'name': 'a'}`, close the database, and reopen the same path with `GzipJSONStorage`, Then `db.all()` equals `[{'name': 'a'}]`.
- AC-004: Given I insert `{'name': 'a'}` and close the database, When I read the file with `gzip.open(path, 'rt')` and `json.load` it, Then the result equals `{'_default': {'1': {'name': 'a'}}}` and the first two raw bytes of the file are `b'\x1f\x8b'`.
- AC-005: Given `TinyDB(path, storage=CachingMiddleware(GzipJSONStorage))` with `{'name': 'a'}` inserted and no explicit flush, When I close the database and reopen the path with plain `TinyDB(path, storage=GzipJSONStorage)`, Then `db.all()` equals `[{'name': 'a'}]`.
- AC-006: Given `TinyDB('tmp/plain.json', storage=JSONStorage)` with `{'name': 'a'}` inserted and closed, When I read the raw bytes of `tmp/plain.json`, Then they do not start with `b'\x1f\x8b'` and `json.loads` of them equals `{'_default': {'1': {'name': 'a'}}}`.

## Out of scope
- Handling of corrupt or non-gzip content in an existing file.
- Compression level or other gzip tuning options.
- Read-only access modes and the `encoding` option beyond what `JSONStorage` already offers.
- Changes to `JSONStorage`, `MemoryStorage`, or `CachingMiddleware` behaviour.
- Migrating existing uncompressed files to gzip.

## Open questions
none

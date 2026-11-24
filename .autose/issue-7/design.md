# Design: Add GzipJSONStorage (gzip-compressed JSON storage)

## Approach
Add one new class, `GzipJSONStorage`, to `tinydb/storages.py`. It subclasses `Storage` directly, not `JSONStorage`, because `JSONStorage` opens a plain text handle in `__init__` and would need to be rewritten anyway. The class holds only the path and keeps no open handle. `__init__` reuses the module-level `touch()` helper so a new path becomes a zero-byte file, which `read()` treats as empty and returns `None`. `read()` opens the file with `gzip.open(path, 'rt', encoding='utf-8')` and calls `json.load`. `write()` serialises with `json.dumps(data, **kwargs)`, writes through a `GzipFile` on a binary handle, then flushes and fsyncs, mirroring `JSONStorage.write`. Because the class holds no handle, the inherited no-op `Storage.close()` is enough. `CachingMiddleware.close()` already calls `self.storage.close()` (middlewares.py:140) and then the final flush, so AC-005 works without touching the middleware. `JSONStorage`, `MemoryStorage`, and `middlewares.py` are not edited.

## Changes
| File | Function | Change |
|---|---|---|
| tinydb/storages.py | NEW (class `GzipJSONStorage(Storage)`) | Add `class GzipJSONStorage(Storage)`, placed after `MemoryStorage`. `__init__(self, path: str, create_dirs=False, **kwargs)`: call `super().__init__()`, store `self._path = path` and `self.kwargs = kwargs`, then call `touch(path, create_dirs=create_dirs)`. `read(self)`: if `os.path.getsize(self._path) == 0`, return `None`; otherwise `with gzip.open(self._path, 'rt', encoding='utf-8') as f: return json.load(f)`. `write(self, data)`: `serialized = json.dumps(data, **self.kwargs).encode('utf-8')`; `with open(self._path, 'wb') as raw:` wrap it in `gzip.GzipFile(fileobj=raw, mode='wb')` and write `serialized`; then `raw.flush()` and `os.fsync(raw.fileno())`. Do not override `close`. |
| tinydb/storages.py | NEW (module attribute edit in `__all__`, line 13) | Change the tuple to `('Storage', 'JSONStorage', 'MemoryStorage', 'GzipJSONStorage')`. This edit is part of the same change as the NEW class above. |
| tinydb/storages.py | NEW (import) | Add `import gzip` to the imports at lines 6-9, keeping alphabetical order (`gzip` goes between `io` and `json`). |

## Constraints respected
- C1: `GzipJSONStorage` subclasses `Storage`, implements `read()` and `write()`, lives in `storages.py`, and is added to `__all__` at line 13.
- C2: No change to `queries.py` imports. `storages.py` gains only the stdlib `gzip` import.
- C3: Not applicable. No query methods are added or changed.
- C4: Only `gzip`, `json`, `os` and the existing `touch` helper are used. `pyproject.toml` is not changed.
- C5: No table code is touched. All writes still reach storage through `Table._update_table` and the existing middleware path.

## AC coverage
- AC-001 -> `GzipJSONStorage.__init__` calls `touch`, which creates an empty file, and `read` returns `None` for it, so `TinyDB` starts with an empty table and `all()` returns `[]`.
- AC-002 -> `read` checks `os.path.getsize == 0` and returns `None` for a zero-byte file.
- AC-003 -> `write` stores gzip-compressed JSON and `read` decompresses it, so data survives close and reopen.
- AC-004 -> `write` uses `gzip.GzipFile`, so the file starts with `\x1f\x8b` and `gzip.open` + `json.load` gives the expected dict.
- AC-005 -> `CachingMiddleware.close` flushes and then calls `storage.close()`. The inherited no-op is enough because no handle is held open between calls, so the data on disk is complete after close.
- AC-006 -> `JSONStorage` and `MemoryStorage` are not modified, so their output is unchanged.

## Risks
- `write` opens the target with `'wb'`, which truncates before writing. A crash mid-write can lose the file, the same risk `JSONStorage` already has. Atomic rename is out of scope and would add complexity.
- A zero-byte file that is not gzip would fail in `gzip.open` on read. That is out of scope per the spec.
- Existing tests in the storage and middleware test modules should still pass, because no shared code changes. The `__all__` edit only affects `from tinydb.storages import *`.
- If the wildcard import is used anywhere in the tests, the extra name is harmless.

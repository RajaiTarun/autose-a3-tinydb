# Design: Include field path in `one_of` query hash

## Approach
`Query.one_of` builds its cache identity as `('one_of', freeze(items))` and leaves out `self._path`. Two `one_of` queries on different fields with the same list therefore hash equal, and `Table.search` (via `_query_cache`) returns the first query's cached results for the second. The fix is to put `self._path` into the hashval, matching the `==`, `!=`, `any` and `all` methods. `_generate_test` uses the hashval as given and does not add the path, so the change belongs in `one_of` alone. The runtime test (`value in items` with path resolution, KeyError/TypeError → False) already gives the correct per-field semantics for FR-1, so no behavioural change is needed. Same-field, same-list queries still produce equal hashes, so the cache keeps working (FR-4). The change is one line and adds no imports or dependencies.

## Changes
| File | Function | Change |
|---|---|---|
| tinydb/queries.py | Query.one_of | Change hashval from `('one_of', freeze(items))` to `('one_of', self._path, freeze(items))` so the field path is part of the query identity (C3). |
| tests/test_queries.py | test_one_of | Existing test; no change required by the design. It should keep passing because it only checks matching, not hash shape. |

## Constraints respected
- C2: No new imports; `queries.py` still imports only `re`, `collections.abc`, `typing`, `.utils`.
- C3: The `one_of` hashval now includes an operator tag, `self._path`, and the frozen argument. This is the rule the bug broke.
- C4: No new dependencies.
- C5: No table mutation paths are touched.

## AC coverage
- AC-001 → `Query.one_of` returns `value in items` on the resolved `a` path. This is already correct and is unaffected by the change.
- AC-002 → Hashes now differ (`('one_of', ('a',), …)` vs `('one_of', ('b',), …)`), so the `b` query misses the cache and scans. Result `[]`.
- AC-003 → Same reasoning in reverse order.
- AC-004 → Identical `a` queries still hash equal, so the second call hits the cache and returns the same result.
- AC-005 → Empty list: `value in ()` is False. The hashval change does not affect this.
- AC-006 → Missing field raises KeyError inside `runner`, which returns False. Unchanged.
- AC-007 → `==` hashes `('==', path, value)` and `one_of` hashes `('one_of', path, items)`. The tags differ, so there is no collision.

## Risks
- Cache keys for existing `one_of` queries change. Any persisted cache is in-memory only (`LRUCache`), so there is no data migration.
- `freeze(items)` for a list returns a hashable form. Adding `self._path` (a tuple of str/callable) keeps it hashable. A callable in the path makes it uncacheable only through `map()`, which already sets `_hash = None`. `_generate_test` then passes `None` through, so no new failure mode is introduced.
- Existing coverage: `tests/test_queries.py::test_one_of` and the `tests/test_table*.py` search/cache tests. The Tester should also add AC-002/AC-003 as cross-field cache regression tests.

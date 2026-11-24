# Spec: one_of() query cache returns results for a different field

## Problem
The user reports that after `db.search(Query().a.one_of([1, 2]))`, the query `Query().b.one_of([1, 2])` returns `[{'a': 1, 'b': 9}]`, although `b` is 9. Quote: "It looks like the second query reuses the first one's results. Other query methods like `==` don't seem to have this problem." The cause is the query-cache key. `one_of` builds its hash from the item list only, so two `one_of` queries with the same list on different fields share a cache entry. `==` includes the field path in its hash.

## Requirements
- FR-1: `one_of` results must depend on both the field path and the item list. Status: CONFIRMED. The issue states the wrong result ("b is 9") and the expected result is `[]`.
- FR-2: Two `one_of` queries on different fields with the same list must not share a query-cache entry. Status: INFERRED. The issue says the second query "reuses the first one's results", and the cache is keyed on the query hash (tinydb/table.py:265, 291-295).
- FR-3: Two `one_of` queries on the same field with different lists must still return different results. Status: INFERRED. The fix must not make the key too coarse, and the item list is already part of the hash.
- FR-4: Matching semantics (`value in items`) and cache invalidation on writes must not change. Status: INFERRED. The fix should only change the hash argument, not the test or the cache-clearing path (tinydb/table.py:723).

## Acceptance criteria
- AC-001: Given a table containing `{'a': 1, 'b': 9}`, When `search(Query().a.one_of([1, 2]))` is run and then `search(Query().b.one_of([1, 2]))`, Then the first returns `[{'a': 1, 'b': 9}]` and the second returns `[]`.
- AC-002: Given a table containing `{'a': 1, 'b': 9}`, When `search(Query().b.one_of([1, 2]))` is run first and then `search(Query().a.one_of([1, 2]))`, Then the second returns `[{'a': 1, 'b': 9}]`.
- AC-003: Given a table containing `{'a': 1, 'b': 1}` and `{'c': 1}`, When `search(Query().a.one_of([1]))` is run and then `search(Query().c.one_of([1]))`, Then the second returns `[{'c': 1}]`.
- AC-004: Given a table containing `{'a': 1, 'b': 9}`, When `search(Query().a.one_of([1, 2]))` is run and then `search(Query().a.one_of([9]))`, Then the second returns `[]`.
- AC-005: Given a table containing `{'a': 1, 'b': 9}`, When `search(Query().x.one_of([1, 2]))` is called on a missing field, Then it returns `[]`.
- AC-006: Given a table where `search(Query().b.one_of([1, 2]))` returned `[]`, When `insert({'b': 2})` is called and the same search is repeated, Then the result is `[{'b': 2}]`.

## Out of scope
- Changing `one_of` to accept generators, or changing its docstring.
- `fragment()` (tinydb/queries.py:497-499) builds its hash as `('fragment', freeze(document))` with no `self._path`. It appears to have the same flaw. It is not in this issue, so it is recorded here as a follow-up and not fixed as part of this change.
- Other query methods, beyond confirming that `==` already includes the path.

## Open questions
none

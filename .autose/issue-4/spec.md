# Spec: one_of() query cache returns results for a different field

## Problem
The user reports that `Query().b.one_of([1, 2])` returns `[{'a': 1, 'b': 9}]` after `Query().a.one_of([1, 2])` has run, even though `b` is 9. Quote: "It looks like the second query reuses the first one's results. Other query methods like `==` don't seem to have this problem." The cause is in the query-cache key. `one_of` builds its cache hash from the items only, so two `one_of` queries with the same list on different fields collide. `==` includes the field path in its hash.

## Requirements
- FR-1: `one_of` results must depend on the field path as well as the item list. Status: CONFIRMED. The issue states the wrong result ("b is 9"), and the expected result follows from the query's definition.
- FR-2: Two `one_of` queries on different fields with the same list must not share a query-cache entry. Status: INFERRED. The issue says the second query "reuses the first one's results", and the cache is keyed on the query hash (tinydb/table.py:265, 293-295).
- FR-3: Other query types must keep their current behaviour, including `==`. Status: CONFIRMED. The issue says "`==` doesn't seem to have this problem"; `==` hashes include `self._path` (tinydb/queries.py:264).
- FR-4: Existing `one_of` matching semantics (membership test against the list) must not change. Status: INFERRED. The fix should only affect the cache key, not the test (tinydb/queries.py:484-487).

Code facts:
- tinydb/queries.py:484-487: `one_of` hash is `('one_of', freeze(items))`, with no `self._path`.
- tinydb/queries.py:264: `==` hash is `('==', self._path, freeze(rhs))`.
- tinydb/queries.py:249-252: the cache hash is attached only when the query is cacheable.
- tinydb/table.py:265-267 and 293-295: `search` reads and writes the cache keyed on the query.

## Acceptance criteria
- AC-001: Given a table containing `{'a': 1, 'b': 9}`, When `search(Query().a.one_of([1, 2]))` is run and then `search(Query().b.one_of([1, 2]))`, Then the first returns `[{'a': 1, 'b': 9}]` and the second returns `[]`.
- AC-002: Given a table containing `{'a': 1, 'b': 9}`, When `search(Query().b.one_of([1, 2]))` is run first and then `search(Query().a.one_of([1, 2]))`, Then the second returns `[{'a': 1, 'b': 9}]`.
- AC-003: Given a table containing `{'a': 1, 'b': 1}` and `{'c': 1}`, When `search(Query().a.one_of([1]))` is run and then `search(Query().c.one_of([1]))`, Then the second returns `[{'c': 1}]`.
- AC-004: Given a table containing `{'a': 1, 'b': 9}`, When `search(Query().a.one_of([1, 2]))` is run and then `search(Query().a.one_of([9]))`, Then the second returns `[]`. This checks that different item lists on the same field still give different results.
- AC-005: Given a table containing `{'a': 1, 'b': 9}`, When `search(Query().x.one_of([1, 2]))` is called on a missing field, Then it returns `[]`.
- AC-006: Given a table where `search(Query().b.one_of([1, 2]))` returned `[]`, When `insert({'b': 2})` is called and the same search is repeated, Then the result is `[{'b': 2}]`. This checks that writes still invalidate the cache.
- AC-007: Given a table containing `{'a': 1, 'b': 9}`, When `search(Query().a == 1)` is run and then `search(Query().b == 1)`, Then the second returns `[]`. This is the non-regression check that `==` keeps its current behaviour.

## Out of scope
- Changing query-hash design for other methods (`any`, `all`, `test`, `map`, `fragment`).
- Changing how the query cache works in general, its capacity, or its eviction policy.
- Changing `one_of` to accept generators or to alter its docstring.
- Adding a new public API.

## Open questions
none


## STOPPED at stage 'spec' (round 0)

Judge returned unparseable output: {"testable": true, "problems": []}
{"testable": true, "problems": []}

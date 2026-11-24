<design>
# Design: one_of() hash omits the field path

## Approach
`Query.one_of` builds its cache hash as `('one_of', freeze(items))`, leaving out `self._path`. Two `one_of` queries with the same list on different fields therefore share a `hashval`. `Table.search` uses that hash as the LRU cache key (ADR-3), so the second search returns the first search's cached result. The fix is a one-line change to the hash tuple so it matches the `==` pattern at `queries.py:264`: `('one_of', self._path, freeze(items))`. The test function, the `_generate_test` path handling, and the cache-clearing path in `_update_table` stay as they are. The hash is in-memory only, so no stored data is affected. The change adds no imports and no dependencies.

## Changes
| File | Function | Change |
|---|---|---|
| tinydb/queries.py | Query.one_of | Change the hash argument at line 486 from `('one_of', freeze(items))` to `('one_of', self._path, freeze(items))`. The predicate `value in items` is unchanged. |
| tests/test_queries.py | test_one_of | NEW test cases (added to the existing function, not a new function): the same list on two different fields, and the same field with two different lists. Covers AC-001 to AC-004. |
| tests/test_table.py | Table.search | NEW test cases for the cache-sensitive scenarios: a missing field (AC-005), and an insert after an empty cached result (AC-006). Also covers AC-002 and AC-003 through the table path. |

## Constraints respected
- C2: The change is inside `queries.py` and uses only existing names. No new import, so the dependency direction is unchanged.
- C3: The hash now contains an operator tag, `self._path`, and all arguments (`freeze(items)`). This is the rule this change enforces. It is built through the existing `_generate_test` call.
- C4: No new dependency.
- C5: No table mutation path changes. The `_update_table` cache invalidation (AC-006) is exercised but not modified.

## AC coverage
- AC-001 -> queries.py `Query.one_of` hash includes `self._path`, so `a` and `b` get different keys. Tested in tests/test_table.py.
- AC-002 -> same change, reverse order. Tested in tests/test_table.py.
- AC-003 -> same change. The `{'c': 1}` document is found because the key for `c` differs from `a`. Tested in tests/test_table.py.
- AC-004 -> the path was already in the hash, and the item list was already in it too. This is a regression check. Tested in tests/test_queries.py.
- AC-005 -> `_generate_test` path handling returns False for a missing key, so `[]` results. Regression check in tests/test_table.py.
- AC-006 -> unchanged `_update_table` invalidation (table.py:854). Regression check in tests/test_table.py.

## Risks
- Existing test `test_one_of` (tests/test_queries.py:428) uses one field and should still pass. It cannot catch this collision, which is why new cases are needed.
- If `self._path` is a tuple or a `Path`-like object, it must be hashable. `==` already uses it the same way, so this is not a new risk.
- Out of scope, per the spec: `fragment()` (queries.py:499) has the same missing-path pattern. Do not change it here. Record it as a follow-up.
- Anything that depends on the old hash value for `one_of` would break. The cache is in-memory and per-table, so nothing persists this value.

<notes>
- Implementer: change only the hash tuple at tinydb/queries.py:486. Do not touch the predicate or `_generate_test`. Do not change `fragment` (out of scope).
- Tester: the one-field `test_one_of` cannot catch the bug. Add a two-field case and a same-field, two-list case. Each must go through `db.search` with a shared query cache, so run the first query, then the second, in one table.
- Tester: for AC-006, a `one_of` search that returns `[]` must be repeated after `insert`. Repeating it verifies that `_update_table` clears the cache.
- Tester: run the full `tests/` suite to catch any test that depends on the hash tuple shape.
- Both: the example in the issue (`{'a': 1, 'b': 9}`) is the minimal reproduction.
</notes>

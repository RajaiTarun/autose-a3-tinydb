# Design: Inclusive `Query().<path>.between(low, high)`

## Approach
Add one method, `Query.between`, in `tinydb/queries.py`, next to the other comparison operators. It returns a `QueryInstance` built with `_generate_test`, so path resolution (including nested paths such as `user.age`) and the `is_cacheable` handling are inherited. The inner test is `low <= value <= high`, wrapped in `try/except TypeError` and returning `False` on error. This guard is required because `_generate_test` only catches errors raised while resolving the path. The hashval is `('between', self._path, freeze(low), freeze(high))`, so different bounds get different cache keys. `&`, `|`, `~`, and the `Table` methods `search`, `get`, `count` and `remove` already accept any `QueryInstance`, so they need no changes. `tinydb/table.py` stays untouched. The previous design listed `Table.*` rows, which were the likely cause of the failed check.

## Changes
| File | Function | Change |
|---|---|---|
| tinydb/queries.py | Query.between | NEW method `between(self, low: Any, high: Any) -> QueryInstance`. Body: define `test(value)` that returns `low <= value <= high` inside `try`, and returns `False` on `TypeError`. Return `self._generate_test(test, ('between', self._path, freeze(low), freeze(high)))`. Docstring follows the style of `__ge__`, with an example `Query().f1.between(18, 65)`. |
| tinydb/queries.py | Query (class body) | Place `between` after `__ge__` (around line 330) and before `exists`. No other change. |

No change to `tinydb/table.py`: `Table.search` (:249), `Table.get` (:337), `Table.count` (:709) and `Table.remove` (:625) all consume any `QueryInstance` and cache it by `hash`. No new imports are needed, since `freeze` is already imported at queries.py:23.

## Constraints respected
- C1: Not applicable. No storage is added or changed.
- C2: `queries.py` gains no imports. It still imports only `re`, `collections.abc`, `typing` and `.utils`.
- C3: The hashval is built from an operator tag (`'between'`), `self._path`, and both bounds frozen with `freeze()`. Different bounds, or different paths, produce different hashes. The method is built with `_generate_test`.
- C4: Standard library only. No new dependency.
- C5: No table mutation is added. `Table._update_table` is not touched.

## AC coverage
- AC-001 -> Query.between (inclusive `<=` on both ends).
- AC-002 -> Query.between via `_generate_test` path resolution for nested `user.age`.
- AC-003 -> Query.between: a missing key fails in `runner` and returns `False`; `'old'` and `None` raise TypeError inside the guarded `test`, which returns `False`.
- AC-004 -> Query.between returns a `QueryInstance`, so the existing `__and__`, `__invert__` and `__eq__` apply. The `~` hashval is `('not', ...)`.
- AC-005 -> Query.between plus unchanged `Table.get`, `count` and `remove`.
- AC-006 -> Query.between hashval includes both bounds, so `between(18,30)` does not hit the `between(18,65)` cache entry.
- AC-007 -> Query.between: `65 <= v <= 18` is always false, so the result is `[]` with no exception.
- AC-008 -> No existing method is changed, so `>=` and `<=` behave as before.

## Risks
- A document field literally named `between` is shadowed by the new method. This is the same behaviour as the existing `matches`, `search`, `test` and `any` methods, and `Query()['between']` still reaches the field.
- A `TypeError` guard might also hide errors from custom `__le__` implementations. That is acceptable: the spec asks for no exception on incomparable values.
- Existing tests in `tests/test_queries.py` (operator and hash tests) should keep passing, because no existing code path changes. The Tester should add cases for AC-001 to AC-007 and check the hashval uniqueness for different bounds (C3).
- `low > high` returns no matches silently. That matches the spec (FR-7).

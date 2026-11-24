# Design: `subtract` with a negative amount subtracts it

## Approach
The bug is in `subtract` at `tinydb/operations.py:43`, which applies `doc[field] -= abs(n)`. The `abs()` forces the subtracted amount to be non-negative, so a negative `n` decreases the field. The fix is to remove `abs()` so the transform does `doc[field] -= n`. Positive amounts, zero, and floats then follow plain subtraction, which matches the documented contract (docs/usage.rst:316). The change is one expression in one function, with no new imports, helpers, or dependencies. Existing `test_subtract` (positive 5, expects -4) keeps passing. Negative-amount coverage is added as a new test in the existing test file, since the current suite has no negative case. The docstring wording is left unchanged because it is out of scope.

## Changes
| File | Function | Change |
|---|---|---|
| tinydb/operations.py | subtract | Replace `doc[field] -= abs(n)` with `doc[field] -= n`. Keep the signature, the docstring, and the returned `transform` closure as they are. |
| tests/test_operations.py | test_subtract_negative_int (NEW) | Add a test using the existing `db` fixture: `db.update(subtract('int', -10), where('char') == 'a')`, then assert `int` equals 11 (starting value 1). This covers AC-001 in the test fixture's shape. |
| tests/test_operations.py | test_subtract_negative_float (NEW) | Add a test that sets a float field (for example, via `db.update(set('float', 100.0), ...)` or by inserting a document with `float` = 100), applies `subtract('f', -2.5)`, and asserts the result is 102.5. This covers AC-002. |
| tests/test_operations.py | test_subtract_zero (NEW) | Add a test that applies `subtract('int', 0)` and asserts `int` stays at 1. This covers AC-004. |

## Constraints respected
- C1: No storage is added or changed. Not affected.
- C2: Only `operations.py` and its test are touched. No new imports, so `queries.py` is unaffected.
- C3: No query is built or changed. Not affected.
- C4: No new dependency is added. The fix removes a call to the built-in `abs`, and the tests use only the existing `db` fixture.
- C5: The transform still runs through `Table.update` → `Table._update_table` (tinydb/table.py:804-854), so the query cache is still invalidated. The operation's behaviour is unchanged on that path.

## AC coverage
- AC-001 → `tinydb/operations.py` `subtract` (removing `abs`), verified by `test_subtract_negative_int`.
- AC-002 → `tinydb/operations.py` `subtract`, verified by `test_subtract_negative_float`.
- AC-003 → `tinydb/operations.py` `subtract` (positive path unchanged), verified by existing `test_subtract`.
- AC-004 → `tinydb/operations.py` `subtract` (`n - 0` is a no-op), verified by `test_subtract_zero`.
- AC-005 → `tinydb/operations.py` `subtract`, verified by existing `test_subtract` (still expects -4).

## Risks
- Callers who relied on the old behaviour (a negative `n` always decreasing the field) will see a changed result. This is the intended fix, but it should be called out in the changelog.
- The float test depends on exact float arithmetic. 100 - (-2.5) = 102.5 is exactly representable, so the test is stable.
- Existing coverage: `test_subtract` in tests/test_operations.py:20-22 (positive case) must still pass. The other tests in that file (add, set, increment, decrement, delete) do not touch `subtract` and should be unaffected.
- No other code in the repo calls `subtract` with an intentionally negative amount that depends on the `abs` behaviour. The Tester should run the full test suite to confirm.

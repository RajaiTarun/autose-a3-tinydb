# Design: `subtract` uses the sign of a negative amount

## Approach
The bug is one line. `subtract` in `tinydb/operations.py` runs `doc[field] -= abs(n)`, which throws away the sign of `n`. Changing it to `doc[field] -= n` gives `old - n` for every numeric `n`, so a negative amount adds to the field. This matches the sibling `add`, which uses `doc[field] += n`. The `abs()` call is also the thing that makes a string `n` raise `TypeError`. Without it, `100 - 'x'` still raises `TypeError` before the assignment runs, so the stored value stays unchanged (FR-4). No new code paths, imports or dependencies are needed. Existing tests keep passing: `test_subtract` uses a positive 5 (1 - 5 = -4). I will add regression tests for the new behaviour in the existing test module, following its style.

## Changes
| File | Function | Change |
|---|---|---|
| tinydb/operations.py | subtract | Replace `doc[field] -= abs(n)` with `doc[field] -= n`. Keep the signature `Union[int, float]`. Optionally fix the docstring wording "Subtract ``n`` to" to "Subtract ``n`` from" (docstring only). |
| tests/test_operations.py | NEW test_subtract_negative_int | NEW test: `db.update(subtract('int', -5), where('char') == 'a')`, then assert `int == 6` (AC-001 pattern, using the existing `db` fixture and `char == 'a'` document). |
| tests/test_operations.py | NEW test_subtract_negative_float | NEW test: `subtract('int', -2.5)`, then assert `int == 3.5` (AC-002 pattern). |
| tests/test_operations.py | NEW test_subtract_str_raises | NEW test: `subtract('int', 'x')` inside `pytest.raises(TypeError)`, then assert `int == 1` is unchanged (AC-005). Add `import pytest` at the top of the file. |

## Constraints respected
- C1: No storage code is touched.
- C2: No import is added to `queries.py`. The change is in `operations.py` and the test file only.
- C3: No query is added or changed, so there is no `hashval` to build.
- C4: No new dependency. `pytest` is already the test framework. Confirm it is in the dev/test setup before relying on it (the test file does not import it today).
- C5: The fix does not write to storage. The transform still runs inside the existing `Table.update` path, so cache invalidation is unchanged.

## AC coverage
- AC-001 -> `subtract` change (`doc[field] -= n`); test_subtract_negative_int checks the same pattern on the `int` field.
- AC-002 -> `subtract` change; test_subtract_negative_float.
- AC-003 -> `subtract` change keeps positive behaviour; existing `test_subtract` (1 - 5 = -4) covers it.
- AC-004 -> `subtract(…, 0)` gives `old - 0`, unchanged. No dedicated test is required, but one could be added to the same file.
- AC-005 -> `subtract` change; `TypeError` comes from `int - str` before the assignment. test_subtract_str_raises.
- AC-006 -> `add`, `increment`, `decrement` are not modified. Existing tests test_add_int, test_increment and test_decrement cover them.

## Risks
- Behaviour change for anyone who relied on negative `n` subtracting. This is the intended fix, but it is a visible change. The `subtract` docstring should say what the sign means.
- A `bool` `n` passes the type check in Python (`True` is an int). This is unchanged from before (`abs(True)` was also accepted).
- Existing `test_subtract` (positive n) must still pass. It does, since `1 - 5` is the same result as before.
- A missing field is out of scope. It still raises `KeyError`, as before.

# Spec: `subtract` with a negative amount must subtract it (add the magnitude)

## Problem
A user passes a negative amount to `subtract` for refunds, expecting the balance to go up. The issue reports: "For refunds we pass a negative amount, expecting it to add the money back, but the balance goes down instead." Example: `db.update(subtract('balance', -10), Query().user == 'sam')` with balance 100 gives 90, and the user expects 110. Positive amounts already work, and floats (-2.5) fail the same way.

## Requirements
- FR-1: `subtract(field, n)` with a negative `n` must change the field by `-n` (so a negative `n` increases the value). CONFIRMED: "we pass a negative amount, expecting it to add the money back" and "expected 110".
- FR-2: Negative float amounts must work the same as negative ints. CONFIRMED: "Same thing happens with floats (-2.5)."
- FR-3: Positive amounts must keep their current behaviour (the field decreases by `n`). CONFIRMED: "Subtracting a positive number works fine."
- FR-4: A zero amount leaves the field unchanged. INFERRED: follows from FR-1/FR-3 (subtracting 0 is a no-op).
- FR-5: The documented contract "subtract ``value`` from the value of a key" (docs/usage.rst:316) is the reference for the sign semantics. INFERRED: the docs describe plain subtraction, so `subtract(f, -x)` should equal `value - (-x)`.

Current cause (for the Design agent): `tinydb/operations.py:43` does `doc[field] -= abs(n)`, which always subtracts a non-negative amount. `tests/test_operations.py:20-22` only covers a positive amount, so the negative case is untested.

## Acceptance criteria
- AC-001: Given a document with `balance` = 100, When `db.update(subtract('balance', -10), where('user') == 'sam')` runs, Then the stored `balance` is 110.
- AC-002: Given a document with `balance` = 100, When `subtract('balance', -2.5)` is applied via `db.update`, Then the stored `balance` is 102.5.
- AC-003: Given a document with `balance` = 100, When `subtract('balance', 10)` is applied, Then the stored `balance` is 90 (non-regression).
- AC-004: Given a document with `balance` = 100, When `subtract('balance', 0)` is applied, Then the stored `balance` is 100.
- AC-005: Given a document with `int` = 1 and `char` = 'a' (as in tests/test_operations.py), When `subtract('int', 5)` is applied, Then `int` is -4 (existing test still passes).

## Out of scope
- Changing `add`, `increment`, `decrement`, or `set`.
- Type validation or error handling for non-numeric `n` or for a missing field (current behaviour is unchanged).
- Adding new refund helpers or new operations.
- Updating the docstring wording beyond what the fix needs.

## Open questions
none

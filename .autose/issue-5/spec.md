# Spec: `subtract` ignores the sign of a negative amount

## Problem
The user reports that `subtract('balance', -10)` lowers a balance of 100 to 90 when they expected 110: "For refunds we pass a negative amount, expecting it to add the money back, but the balance goes down instead." They add that "Subtracting a positive number works fine. Same thing happens with floats (-2.5)." The current implementation applies `abs(n)` before subtracting, so the sign of `n` is discarded. The documented meaning, "subtract ``value`` from the value of a key" (docs/usage.rst:316), implies a negative value should increase the field.

## Requirements
- FR-1: `subtract(field, n)` sets the field to `old - n` for any numeric `n`, including negative and float values. **CONFIRMED** (issue: "expecting it to add the money back"; docs/usage.rst:316).
- FR-2: Positive `n` keeps its current result (the field decreases by `n`). **CONFIRMED** (issue: "Subtracting a positive number works fine").
- FR-3: `add`, `increment` and `decrement` are unchanged. **INFERRED** (the issue concerns only `subtract`; `add` at tinydb/operations.py:33 already uses the sign of `n`).
- FR-4: A non-numeric `n` still raises `TypeError` and leaves the stored value unchanged. **INFERRED** (the signature is `Union[int, float]` at tinydb/operations.py:38, and the current `abs(n)` at line 43 raises on strings; the fix must not make bad input pass silently).
- FR-5: Behaviour for a missing field is not specified by the issue and is out of scope.

## Acceptance criteria
AC-001: Given a document `{'balance': 100}`, When `db.update(subtract('balance', -10), Query().user == 'sam')` runs on a matching document, Then the stored `balance` is `110`.
AC-002: Given a document `{'balance': 100}`, When `subtract('balance', -2.5)` is applied, Then the stored `balance` is `102.5`.
AC-003: Given a document `{'balance': 100}`, When `subtract('balance', 10)` is applied, Then the stored `balance` is `90`.
AC-004: Given a document `{'balance': 100}`, When `subtract('balance', 0)` is applied, Then the stored `balance` is `100`.
AC-005: Given a document `{'balance': 100}`, When `subtract('balance', 'x')` is applied, Then a `TypeError` is raised and the stored `balance` remains `100`.
AC-006: Given a document `{'int': 1}` and `add('int', -3)`, `increment('int')` and `decrement('int')` applied in turn, When the update runs, Then the stored `int` is `-2` (confirming the unchanged operations behave as before).

## Out of scope
- Changing how `subtract` handles a missing field.
- Changing `add`, `increment` or `decrement` behaviour.
- Editing documentation beyond what the fix needs.
- Adding new operations or changing the update API.

## Open questions
none

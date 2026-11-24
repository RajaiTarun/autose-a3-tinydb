# Spec: Sort search() results

## Problem
The issue says: "When I call search() the documents come back in whatever order. It'd be much nicer if I could get them sorted. Can this be added?" Today `Table.search()` returns matches by scanning the stored documents in storage order (tinydb/table.py:272-274), and the docstring for the iteration path documents insertion order (tinydb/table.py:348). The request does not say which key the results should be sorted by, which direction, or how a caller would choose the order, so the expected behaviour cannot be fixed yet.

## Requirements
- FR-1: `search()` results can be returned sorted. Status: CONFIRMED ("results should come back sorted", "I could get them sorted").
- FR-2: The sort key (for example a document field name) is chosen by the caller. Status: UNRESOLVED. The issue names no field and no key.
- FR-3: Sort direction (ascending or descending). Status: UNRESOLVED.
- FR-4: The API shape (a new argument on `search()`, a separate method, or a query-level option) is not specified. Status: UNRESOLVED.
- FR-5: Behaviour when a document lacks the sort key, or when values of mixed types are compared. Status: UNRESOLVED.
- FR-6: Default behaviour when no sort is requested must stay as it is today (storage order). Status: INFERRED. Reason: the issue asks for sorting as an option ("I could get them sorted") and does not ask to change the unsorted default.

## Acceptance criteria
Not written. The ACs depend on the answers to the open questions below, because each guess about the key, direction, and API leads to different tests.

## Out of scope
- Sorting in other methods (`all()`, `get()`, `update()`, `remove()`).
- Changes to the storage format or the query cache.
- Multi-key sorting unless the user asks for it.

## Open questions
1. Which key should results be sorted by? A document field name (and what if the field is nested, such as `a.b`), the document ID, or something else?
2. Should the order be ascending, descending, or both?
3. How should the caller request a sort? An argument on `search()`, a separate method, or another form?
4. Where a document is missing the sort field, or values have mixed types (for example int and str), should those documents go last, raise an error, or be skipped?
5. Should ties keep insertion order (stable sort), and is that the expected result?


## STOPPED at stage 'spec' (round 0)

The request is too ambiguous to specify safely. Open questions are listed in spec.md; please answer them on the issue and re-run.

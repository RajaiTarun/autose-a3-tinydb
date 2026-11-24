# Spec: `one_of` queries on different fields return cached results from another field

## Problem
The user reports: "`db.search(Query().b.one_of([1, 2]))` returns `[{'a': 1, 'b': 9}]` ??? b is 9", and "If I run the `b` query first, it's correct. It looks like the second query reuses the first one's results. Other query methods like `==` don't seem to have this problem." The root cause is in how `one_of` builds its query identity: the hash omits the field path, so two `one_of` queries with the same list are treated as the same query by the table's query cache.

## Requirements
- FR-1 (CONFIRMED): `Query().<field>.one_of(list)` must return only documents whose `<field>` value is contained in the list. Quote: "The second search should return nothing, since `b` is 9."
- FR-2 (CONFIRMED): Two `one_of` queries on different fields with the same list must not share cached results. Quote: "It looks like the second query reuses the first one's results."
- FR-3 (INFERRED): Behaviour of `one_of` on a single field (including the existing correct results) must not change. Reason: the fix is limited to the query identity and the issue reports only the cross-field collision.
- FR-4 (INFERRED): Same-field, same-list queries should still be valid and return the same results as before. Reason: the cache is meant to speed up repeated identical queries; the fix should keep that working.

## Acceptance criteria
- AC-001: Given a table with one document `{'a': 1, 'b': 9}`, When `search(Query().a.one_of([1, 2]))` is called, Then the result is `[{'a': 1, 'b': 9}]`.
- AC-002: Given the same table, When `search(Query().a.one_of([1, 2]))` is called first and then `search(Query().b.one_of([1, 2]))`, Then the second result is `[]`.
- AC-003: Given the same table, When `search(Query().b.one_of([1, 2]))` is called first and then `search(Query().a.one_of([1, 2]))`, Then the second result is `[{'a': 1, 'b': 9}]`.
- AC-004: Given a table with documents `{'a': 1}` and `{'a': 3}`, When `search(Query().a.one_of([1, 2]))` is called twice in a row, Then both calls return `[{'a': 1}]`.
- AC-005: Given a table with a document `{'a': 1}`, When `search(Query().a.one_of([])) ` is called, Then the result is `[]`.
- AC-006: Given a table with a document `{'a': 1}` and `{'b': 1}`, When `search(Query().a.one_of([1]))` is called, Then the result is `[{'a': 1}]` (documents missing the field are not matched and do not raise).
- AC-007: Given a table with documents `{'a': 1}` and `{'a': 2}`, When `search(Query().a == 1)` is called followed by `search(Query().a.one_of([1]))`, Then the second result is `[{'a': 1}]` (the fix must not break mixing `one_of` with other operators).

## Out of scope
- Changing the query cache design or its capacity (`tinydb/table.py:87-108`).
- Fixing identical-hash issues in other operators beyond checking that `==` is unaffected.
- Changing `one_of` semantics for non-list inputs (for example generators) or the `freeze` behaviour.
- Changelog or documentation updates.

## Open questions
none

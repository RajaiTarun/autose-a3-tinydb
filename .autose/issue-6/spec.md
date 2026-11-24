# Spec: Add `Query().<field>.between(low, high)` inclusive range query

## Problem
The user writes `db.search((Query().age >= 18) & (Query().age <= 65))` to find values in a range and asks for a helper such as `Query().age.between(18, 65)` with both ends included. The request says: "It should work like the other query methods (combine with & | ~, nested fields like `Query().user.age`, search/get/count/remove). Documents without the field, or with values that can't be compared (e.g. a string), should just not match rather than blow up." Today the `>=`/`<=` operators do blow up on incomparable values (see Notes), so the helper must guard against that itself.

## Requirements
- FR-1: `Query().<path>.between(low, high)` returns a query object usable wherever other queries are used. CONFIRMED: "It would be really nice to have something like `Query().age.between(18, 65)`".
- FR-2: Both bounds are inclusive (value == low and value == high match). CONFIRMED: "with both ends included".
- FR-3: Works on nested paths such as `Query().user.age.between(...)`. CONFIRMED: "nested fields like `Query().user.age`".
- FR-4: Composes with `&`, `|`, `~` and works with `search`, `get`, `count`, `remove`. CONFIRMED: "combine with & | ~ ... search/get/count/remove".
- FR-5: A document where the field is missing, or where the value cannot be compared to the bounds (e.g. a string, `None`), does not match and raises no exception. CONFIRMED: "should just not match rather than blow up".
- FR-6: Queries with different bounds must not share a query-cache entry (the bounds are part of the query's cache key). INFERRED: `Table` caches results by query hash (queries.py:251 and the hash pattern used by all other operators), so omitting the bounds would return stale results.
- FR-7: If `low > high`, nothing matches and no error is raised. INFERRED: follows from inclusive bounds meaning `low <= value <= high`; the issue does not mention an error case.

## Acceptance criteria
AC-001: Given documents with age 17, 18, 40, 65, 66, When `db.search(Query().age.between(18, 65))` is called, Then the result contains exactly the documents with age 18, 40 and 65.
AC-002: Given documents `{'user': {'age': 30}}` and `{'user': {'age': 70}}`, When `db.search(Query().user.age.between(18, 65))` is called, Then only the document with user.age 30 is returned.
AC-003: Given documents with age 30, no age field, age `'old'`, and age `None`, When `db.search(Query().age.between(18, 65))` is called, Then only the age-30 document is returned and no exception is raised.
AC-004: Given documents with ages 10, 30, 70, When `db.search(Query().age.between(18, 65) & ~(Query().age == 30))` is called, Then the result is empty; and when `db.search(~Query().age.between(18, 65))` is called, Then the results are the documents with ages 10 and 70 (the age-30 document is excluded).
AC-005: Given documents with ages 20, 30, 70, When `db.get(Query().age.between(18, 65))` returns the first match, `db.count(Query().age.between(18, 65))` returns 2, and `db.remove(Query().age.between(18, 65))` is run, Then `db.all()` contains only the age-70 document.
AC-006: Given a table where `db.search(Query().age.between(18, 65))` has already been run, When `db.search(Query().age.between(18, 30))` is run on the same table, Then only documents with ages in 18..30 are returned (no cached result from the wider range).
AC-007: Given documents with ages 20 and 30, When `db.search(Query().age.between(65, 18))` is called, Then the result is an empty list and no exception is raised.
AC-008: Non-regression: Given the existing query `(Query().age >= 18) & (Query().age <= 65)` and documents with ages 17, 18, 65, When it is searched, Then the result is the documents with ages 18 and 65, exactly as before.

## Out of scope
- Changing how `<`, `<=`, `>`, `>=` handle incomparable values (they currently raise; see Notes). Only `between` must not raise.
- Type coercion (e.g. matching `'30'` against `between(18, 65)`), and supporting bounds of mixed types.
- Exclusive or half-open range variants.
- Changing the existing public query behaviour or the name-shadowing behaviour of methods (see Notes).

## Open questions
none

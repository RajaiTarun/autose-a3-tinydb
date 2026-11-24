# Seeded defects (private until the final run)

Merged into `main` via PR "experiment: seed defects" so that the two bug issues describe real
bugs in the fork. Both survive the full existing test suite (228 passed), verified by
mutation check on 2026-11-21. Full diff: `seeded_defects.patch`.

| Issue | File | Original (edff96a) | Seeded |
|---|---|---|---|
| Bug A (= A2 T1) | tinydb/queries.py `one_of` | `('one_of', self._path, freeze(items))` | `('one_of', freeze(items))`: the hash ignores the field path, so the query cache mixes up `one_of` queries on different fields |
| Bug B | tinydb/operations.py `subtract` | `doc[field] -= n` | `doc[field] -= abs(n)`: subtracting a negative amount decreases instead of increases |

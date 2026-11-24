Added `Query.between(low, high)` in tinydb/queries.py, placed after `__ge__`. It uses `_generate_test`. The inner test is `low <= value <= high`, and a `TypeError` returns False. The hashval is `('between', self._path, freeze(low), freeze(high))`.
No deviations from the design. I didn't touch tinydb/table.py.
I didn't run any of the new AC cases and added no tests for them.
Test result: 227 passed, 1 skipped.

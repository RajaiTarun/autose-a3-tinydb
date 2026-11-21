title: one_of() search returns results from a different field

I'm seeing wrong search results when I use `one_of` on two different fields with the same list.

```python
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

db = TinyDB(storage=MemoryStorage)
db.insert({'a': 1, 'b': 9})

print(db.search(Query().a.one_of([1, 2])))  # [{'a': 1, 'b': 9}]  correct
print(db.search(Query().b.one_of([1, 2])))  # [{'a': 1, 'b': 9}]  ??? b is 9
```

The second search should return nothing, since `b` is 9. If I run the `b` query first, it's correct.
It looks like the second query reuses the first one's results. Other query methods like `==` don't
seem to have this problem.

tinydb 4.9.0, Python 3.13

---
Posted as: https://github.com/RajaiTarun/autose-a3-tinydb/issues/4

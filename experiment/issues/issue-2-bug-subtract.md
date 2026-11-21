title: subtract with a negative number goes the wrong way

We use `subtract` for account balances. For refunds we pass a negative amount, expecting it to add
the money back, but the balance goes down instead.

```python
from tinydb.operations import subtract
db.update(subtract('balance', -10), Query().user == 'sam')
# balance was 100, now it's 90. expected 110
```

Subtracting a positive number works fine. Same thing happens with floats (-2.5).

---
Posted as: https://github.com/RajaiTarun/autose-a3-tinydb/issues/5

title: Feature request: range query helper (between)

Right now to find people aged 18-65 I have to write

```python
db.search((Query().age >= 18) & (Query().age <= 65))
```

It would be really nice to have something like `Query().age.between(18, 65)`, with both ends
included. It should work like the other query methods (combine with & | ~, nested fields like
`Query().user.age`, search/get/count/remove). Documents without the field, or with values that
can't be compared (e.g. a string), should just not match rather than blow up.

---
Posted as: https://github.com/RajaiTarun/autose-a3-tinydb/issues/6

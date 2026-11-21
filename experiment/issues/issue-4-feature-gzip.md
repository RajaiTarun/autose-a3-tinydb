title: Support gzip-compressed database files

Our JSON database files are getting big (hundreds of MB) and compress really well. Could TinyDB
have a storage that writes gzip-compressed JSON?

Ideally I'd just do `TinyDB('data.json.gz', storage=GzipJSONStorage)` with
`from tinydb.storages import GzipJSONStorage`, and it would behave like the normal JSON storage:
a new file starts empty, and data is still there after I close and reopen it. The file should open
with normal gzip tools. We also use `CachingMiddleware`, so it needs to work with that too
(including writes that only happen on close). Please don't change how the existing storages behave.

---
Posted as: https://github.com/RajaiTarun/autose-a3-tinydb/issues/7

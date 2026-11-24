# Seeded PR 5: Table.page drops the last document on the last page (off-by-one).
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

def test_last_page_is_complete():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple({'i': i} for i in range(25))
    assert [d['i'] for d in db.page(3, size=10)] == [20, 21, 22, 23, 24]

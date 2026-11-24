# Seeded PR 3: LRUCache.get no longer refreshes recency -> behaves like FIFO.
from tinydb.utils import LRUCache

def test_get_refreshes_recency():
    cache = LRUCache(capacity=2)
    cache['a'] = 1
    cache['b'] = 2
    cache.get('a')
    cache['c'] = 3
    assert 'a' in cache and 'b' not in cache

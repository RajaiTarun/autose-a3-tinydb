# Seeded PRs (experiment A). PRIVATE until the final run.
| PR | Branch | Seeded bug | Private check |
|---|---|---|---|
| #27 | seeded/not-one-of | not_one_of hash omits self._path (C3), cache collision across fields | test_seeded_1_not_one_of.py |
| #28 | seeded/clear-field | clear_field writes storage directly, bypassing _update_table (C5), stale query cache | test_seeded_2_clear_field.py |
| #29 | seeded/lru-get | LRUCache.get no longer move_to_end, FIFO instead of LRU | test_seeded_3_lru_get.py |
| #30 | seeded/append-op | append shares one new list between all docs updated in one call | test_seeded_4_append.py |
| #31 | seeded/table-page | page end = min(start+size, len-1), last doc dropped on the last page | test_seeded_5_page.py |
All five: full suite passes on the branch; the private check fails (verified 2026-11-24).

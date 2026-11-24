# Runs

All runs: https://github.com/RajaiTarun/autose-a3-tinydb/actions/workflows/autose.yml
Token counts come from each run's `.autose/issue-N/state.json` (stages 1-5) and the review footer.
Base for all runs: `main` with the seeded defects (hidden tests in `experiment/hidden_tests/`).

## Dry run (stub agents, no usage)
- Issue #4 dry run: [run 45371234740](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45371234740), PR #12 (closed). Found: the dispatched CI run is not attached to bot PRs → a person approves the held run (ADR-002 amendment).

## Baseline runs (Haiku workers, Sonnet Implementer, Haiku Reviewer)

### Run 1: issue #4 `one_of` hash bug → [PR #17](https://github.com/RajaiTarun/autose-a3-tinydb/pull/17)
- Attempts: [45377878481](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45377878481) (401: invalid token, 0 tokens) ·
  [45387105791](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45387105791) (stopped at spec: our runner duplicated the judge's JSON; fixed in PR #15) ·
  [45387590024](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45387590024) (stages 1-4 passed; release push rejected; fixed in PR #16) ·
  [45388271088](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45388271088) (resumed at release: PR, CI green, review approve)
- Fix `tinydb/queries.py:486` (path added to the hash). 6 ACs, 6 tests. Hidden tests 3/3.

### Run 2: issue #5 `subtract` sign bug → [PR #18](https://github.com/RajaiTarun/autose-a3-tinydb/pull/18)
- [45400283122](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45400283122): first try. Fix `operations.py:43`. Implementer also added tests outside `tinydb/` → path check added (PR #19). Hidden tests 3/3.

### Run 3: issue #8 vague "results should come back sorted" → stopped at spec (correct)
- [45409511942](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45409511942): `needs_clarification`, 5 questions, no PR, Haiku only.

### Run 4: issue #6 `between` → [PR #21](https://github.com/RajaiTarun/autose-a3-tinydb/pull/21)
- [45410320210](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45410320210): design attempt 1 wrongly rejected by our check (fixed in PR #22). Hidden tests 4/4.

### Run 5: issue #7 gzip storage → [PR #23](https://github.com/RajaiTarun/autose-a3-tinydb/pull/23)
- [45412313866](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45412313866): spec retry (judge rightly rejected an "or" AC); design attempt 1 wrongly rejected (`__all__`, fixed in PR #24). Hidden tests 4/4.

## Experiment A: Reviewer on the 5 seeded PRs

| PR | Seeded bug | Haiku | Sonnet | Notes |
|---|---|---|---|---|
| [#27](https://github.com/RajaiTarun/autose-a3-tinydb/pull/27) `not_one_of` | hash omits path (C3) | ✗ (changes_requested, other reason) → ✗ after prompt fix → **✓ after C3 clarified** | ✗ **approved** | both misread ARCHITECTURE.md C3 |
| [#28](https://github.com/RajaiTarun/autose-a3-tinydb/pull/28) `clear_field` | bypasses `_update_table` (C5) | ✓ | not run | |
| [#29](https://github.com/RajaiTarun/autose-a3-tinydb/pull/29) LRU `get` | no recency refresh | ✓ | not run | |
| [#30](https://github.com/RajaiTarun/autose-a3-tinydb/pull/30) `append` | shared list | ✓ | not run | also caught a duplicate import |
| [#31](https://github.com/RajaiTarun/autose-a3-tinydb/pull/31) `page` | last doc dropped | ✓ | not run | |

Review runs: [45418932532](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45418932532) ·
[45418938515](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45418938515) ·
[45418945458](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45418945458) ·
[45418951304](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45418951304) ·
[45418958155](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45418958155) ·
#27 Haiku rerun [45432389269](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45432389269) ·
#27 Sonnet [45432739272](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45432739272) ·
#27 Haiku after C3 fix [45433627478](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45433627478)

## Experiment B: no separate Tester (issues #4 and #5)
| Issue | Branch / PR | Run | Hidden tests | Own tests catch restored bug | Review |
|---|---|---|---|---|---|
| #4 | [PR #37](https://github.com/RajaiTarun/autose-a3-tinydb/pull/37) `autose/issue-4-no_tester` | [45434826353](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45434826353) | 3/3 | 2 of 7 fail | approve |
| #5 | [PR #36](https://github.com/RajaiTarun/autose-a3-tinydb/pull/36) `autose/issue-5-no_tester` | [45434839904](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45434839904) | 3/3 | 2 of 6 fail | approve |

Earlier attempts [45433627862](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45433627862), [45433638206](https://github.com/RajaiTarun/autose-a3-tinydb/actions/runs/45433638206) (stages 1-4 passed; release.py syntax error, PR #34) and two resumes that loaded the old release.py from the branch (fixed in PR #35).

**Totals (all real runs and reviews):** 1,450,974 tokens (1,334,873 in / 116,101 out); $0 billed; API-equivalent about $0.66.

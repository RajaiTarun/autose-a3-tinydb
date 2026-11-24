---
title: "AutoSE Assignment 3: An Agentic SDLC Workflow on TinyDB"
subtitle: "Issue in, tested and independently reviewed pull request out"
date: "24 November 2026"
geometry: margin=2cm
fontsize: 10pt
---

**Repository:** https://github.com/RajaiTarun/autose-a3-tinydb (fork of `msiemens/tinydb` at `edff96a`).
**Runs:** `results/runs.md`, `results/results.csv`. **Decisions:** `architecture/decisions/ADR-001..010.md`.

# 1. Architecture

A collaborator adds the `autose` label (or comments `/autose`) on an issue. A **gate** job admits
only trusted, non-bot senders. A **build** job runs stages 1–5 under a deterministic Python state
machine (`workflow/orchestrator.py`). A separate **review** job runs stage 6 with read-only
permissions. Agents run through the Claude Agent SDK with per-role tools; only code holds the
GitHub token. **AutoSE never merges; a person decides.**

| # | Stage | Agent / script | Model | Artifact | Check (who decides) |
|---|---|---|---|---|---|
| 1 | Requirements | Spec agent + judge | Haiku | `spec.md` | Given/When/Then ACs (code) + every AC testable (LLM judge) |
| 2 | Design | Design agent | Haiku | `design.md` | files and functions in the Changes table exist (code, `ast`) |
| 3 | Implementation | Implementer | Sonnet | `diff.patch` | non-empty, compiles, imports, only `tinydb/` changed (code) |
| 4 | Testing | Tester | Haiku | `test_report.md` | one `test_acNNN_` per AC, full suite green (code) |
| 5 | Release | script | none | `pr.md`, PR | PR open, dispatched `ci-tests` green (code) |
| 6 | Review | Reviewer (own job) | Haiku | `review.md` | checklist + evidence + valid verdict JSON (code) |

**Component view.** `gate -> build (orchestrator -> agent_runner -> SDK agents; checks; release) ->
review (review.py -> Reviewer agent)`. State lives in `.autose/issue-N/` on the PR branch
(`state.json`, artifacts, 5-line notes), so a review round or a crash resumes from the last
passed stage. Retries: 3<->4 twice, then back to 2 once, then stop with the reason written into the
stage's artifact and posted on the issue. At most 2 review rounds; `changes_requested` restarts
at the stage the Reviewer names (`design` or `implement`).

**Sequence view (run 4, issue #6, real).** label added -> gate (OWNER, non-bot: go) -> build:
spec (8 ACs, judge testable) -> design attempt 1 rejected by the `ast` check -> design attempt 2
passes -> implement (Sonnet, +22 lines in `queries.py`) -> test (8 tests, suite green) -> release
(commit, PR #21, `ci.yml` dispatched, green) -> review job (fresh checkout; runs pytest and
`python -c` probes; approve) -> a person approves the held `pull_request` CI run and decides.

# 2. Design decisions

| ADR | Decision | Chosen | Main option rejected | Main reason | Status |
|---|---|---|---|---|---|
| 001 | Roles | 4 workers + release script + separate Reviewer | one agent for everything | each stage gets a narrow prompt, tools and check | Accepted |
| 002 | Control flow | Python state machine | LLM planner | transitions must be reproducible and auditable | Accepted, amended (CI approval) |
| 003 | Hand-over | artifact files + code + 5-line notes; Tester never sees Implementer notes | passing conversations | independence and small context | Accepted |
| 004 | State | files on the PR branch | external store | resumable, visible in the PR | Accepted |
| 005 | Tools | SDK built-ins per role, no GitHub for agents | MCP / GitHub tools | smallest attack surface | Accepted, amended (path check, simple commands) |
| 006 | Models | Haiku everywhere, Sonnet only for the Implementer | Sonnet everywhere | efficiency, path to SLMs; supported by exp. A | Accepted |
| 007 | Checks | code wherever possible, LLM only for spec testability | LLM checks | deterministic, cheap | Accepted |
| 008 | Reviewer | own job, read-only, evidence required | review inside build job | independence | Accepted, amended (trusted code) |
| 009 | Budgets | tight turns/retries/timeouts, issue text untrusted | generous budgets | cost and prompt-injection safety | Accepted |
| 010 | Trigger | label or `/autose`, collaborators only, one run per issue | any comment | safety | Accepted, amended (`/autose review`) |

**The three decisions that mattered most.**
*ADR-002 (code decides).* Every failure in our runs (a bad token, a parser bug, a GitHub push race,
a syntax error) stopped cleanly with state on the branch, and every rerun resumed at the failed
stage without repeating paid agent work. An LLM planner would have hidden these failures.
*ADR-006 (small models).* Four of five workers ran on Haiku; only the Implementer used Sonnet
(about 30k input tokens per run). We aimed to be as efficient as possible so that the workflow
can later be tried with small language models; experiment A showed no gain from a larger Reviewer.
*ADR-008 (independent, evidence-based review).* Requiring evidence made reviews checkable: every
concern cites `file:line` or a command and its output. Building it also exposed a real security
flaw (the Reviewer's own code came from the PR under review), fixed in decision 5.8.

# 3. Decision experiments

**A. Reviewer model (ADR-006/008).** Five seeded PRs (#27–#31), each a plausible change that
passes CI with weak tests and hides one bug. Usage policy: Haiku first, Sonnet only where Haiku
missed.

| PR | Seeded bug | Haiku Reviewer | Sonnet Reviewer |
|---|---|---|---|
| #27 `not_one_of` | hash omits the field path (C3) | missed (asked for changes for a different, valid reason) | **approved** (missed) |
| #28 `clear_field` | bypasses `_update_table`, stale cache (C5) | found | — |
| #29 LRU `get` | no longer refreshes recency | found | — |
| #30 `append` | one list shared by all updated docs | found | — |
| #31 `page` | last document dropped | found | — |

Both models misread one sentence of `ARCHITECTURE.md` C3 ("`_generate_test` ... enforces path
resolution and hash handling") as "the helper adds the path to the hash", and both anchored on
the existing `one_of`, which has the same seeded bug. After clarifying that sentence, Haiku found
the #27 bug (**5/5**). *What we changed:* kept Haiku as Reviewer (ADR-006 confirmed), fixed C3,
and told Bash-using agents to issue one simple command per call (compound commands were denied).

**B. Separate Tester (ADR-001/003).** `no_tester`: the Tester is skipped and the Implementer
writes its own tests. Issues #4 and #5, compared with baseline runs 1–2.

| | #4 baseline (run 1) | #4 no_tester | #5 baseline (run 2) | #5 no_tester |
|---|---|---|---|---|
| Stages 1-5 | pass | pass | pass | pass (spec retry: AC not in G/W/T) |
| Hidden tests | 3/3 | 3/3 | 3/3 | 3/3 |
| Own tests failing when the bug is restored | 3 of 6 | 2 of 7 | 2 of 5 | 2 of 6 |
| Build tokens in / out | 138k / 14k (incl. 43k wasted) | 103k / 6k | 105k / 7k | 72k / 8k |
| Review | approve | approve | approve | approve |

On these two small bug fixes, dropping the Tester gave the same hidden-test result and tests
that still catch the bug, with fewer tokens. *What we changed:* nothing; we keep the Tester
(ADR-001/003) because both issues were easy one-line fixes, the Implementer's tests were
proportionally weaker (2 of 7 vs 3 of 6 catching the bug on #4), and the Tester is cheap (Haiku).
A larger feature would be the real test of this decision.

# 4. Results

| Run | Issue | Outcome | Retries | Hidden tests | Tokens in / out (build + review) |
|---|---|---|---|---|---|
| 1 | #4 `one_of` bug | PR #17, approved | spec x1 (our bug), release resume | 3/3 | 180k / 17k |
| 2 | #5 `subtract` bug | PR #18, approved | none | 3/3 | 136k / 10k |
| 3 | #8 vague | stopped at spec with 5 questions | none | n/a | 18k / 2k |
| 4 | #6 `between` | PR #21, approved | design x1 (our check) | 4/4 | 190k / 18k |
| 5 | #7 gzip storage | PR #23, approved | spec x1 (judge, valid), design x1 (our check) | 4/4 | 244k / 25k |

Stage pass rates on first attempt (baseline, 5 issues): spec 3/5 (one stop by design, one valid
judge rejection, one runner bug), design 3/4 (both failures were our check), implement 4/4,
test 4/4, release 4/4 after the push-retry fix, review 4/4 approve. **All 14 hidden tests pass on
the four PRs** (they fail on `main`). The Reviewer caught 4/5 seeded bugs (5/5 after the doc fix)
and never approved a seeded PR on Haiku; where it was wrong (#27) it trusted documentation over
code. Total: 1,450,974 (1,334,873 in / 116,101 out) tokens, $0 billed (Pro subscription, usage credits off).

# 5. Hindsight

We would change **ADR-005 first**: tool permissions by name are not enough. The Edit tool cannot be
limited by path and Bash allowlists only match prefixes, so we needed code checks after the fact
(path check) and prompt rules (simple commands). Starting again, every agent would work in a
sandboxed copy whose diff is validated by code, and the workflow code would always come from the
default branch (the flaw fixed in decision 5.8).

# 6. Limitations and threats to validity

1. **Small sample:** 5 issues and 5 seeded PRs on one repository; each configuration ran once, and
   LLM output varies between runs.
2. **We wrote the hidden tests and the seeded PRs ourselves**, so they may favour bug types we
   expect; the seeded PR #30 also contained an accidental duplicate import the Reviewer found.
3. **The workflow changed during the runs** (fixes after runs 1, 2, 4, 5 and experiment A, each
   logged), so early and late runs are not under identical conditions.
4. **Experiment A is asymmetric by design:** Sonnet reviewed only the PR Haiku missed, to save
   usage; we cannot claim how Sonnet does on the other four.
5. **The issues overlap with the seeded defects** on `main` (#4, #5), which the agents could only
   find from the code, since the checkout is shallow and the commit message is vague.

# AutoSE Assignment 3: Issue In, Pull Request Out

An agentic SDLC workflow built on GitHub Actions. A maintainer adds the `autose` label to an
issue, and a set of agents turns it into a tested pull request reviewed by an
independent agent. **A person makes the final merge decision; AutoSE never merges.**

Report: [`report.pdf`](report.pdf) · Runs: [`results/runs.md`](results/runs.md) · Data: [`results/results.csv`](results/results.csv) · Demo video: [Google Drive](https://drive.google.com/file/d/1AssBfn_ZS91tnLomPmt22f9BzpWvbG1d/view?usp=sharing)

## Subject

| | |
|---|---|
| Fork | https://github.com/RajaiTarun/autose-a3-tinydb |
| Upstream | https://github.com/msiemens/tinydb |
| Pinned commit | `edff96aeb2616402e9489d46e90a592c05565621` |
| Protected branch | `main` (renamed from upstream's `master`; PR required, `ci-tests` required, no bypass) |
| Baseline test suite | 228 passed in 0.94 s (Python 3.13) |

## Pipeline (6 stages)

| # | Stage | Agent / script | Model | Artifact | Check (code unless noted) |
|---|---|---|---|---|---|
| 1 | Requirements | Spec agent + testability judge | Haiku 5.5 | `spec.md` | ACs in Given/When/Then; judge (LLM) says every AC is testable |
| 2 | Design | Design agent | Haiku 5.5 | `design.md` | every file/function in the Changes table exists (AST) or is marked NEW |
| 3 | Implementation | Implementer | Sonnet 5.5 | `diff.patch` | non-empty diff, compiles, imports, changes only `tinydb/` |
| 4 | Testing | Tester | Haiku 5.5 | `test_report.md` | one `test_acNNN_` per AC, full suite passes |
| 5 | Release | script (no LLM) | none | `pr.md`, PR | PR open, dispatched `ci-tests` green |
| 6 | Review | independent Reviewer job | Haiku 5.5 | `review.md` | review has checklist, evidence, valid verdict JSON |

Retries: 3↔4 twice, then back to 2 once, then stop with the reason in the stage artifact.
Review: at most 2 rounds; `changes_requested` restarts at the stage the Reviewer names.

## Models and billing

| Role | Model |
|---|---|
| Spec, Design, Tester, Reviewer, judge | Claude Haiku 5.5 (`claude-haiku-5-5`) |
| Implementer | Claude Sonnet 5.5 (`claude-sonnet-5-5`) |

We deliberately used the smallest model that gets each job done, to be as efficient as possible
and so the workflow can later be tried with small language models (SLMs). Experiment A supports
this: the Sonnet Reviewer was no better than the Haiku Reviewer on the seeded PRs.

Billing: Claude Pro subscription token (`CLAUDE_CODE_OAUTH_TOKEN` secret). Usage credits are off,
so the spending limit is $0; the workflow refuses to run if an `ANTHROPIC_API_KEY` secret exists.
**Total tokens used (all real runs and reviews): 1,450,974 (1,334,873 in / 116,101 out).** API-equivalent cost: about $0.66
(not billed).

## How to trigger the workflow

1. Set the repository variable `AUTOSE_DRY_RUN=false` (default is a dry run with stub agents, no usage).
2. On an issue, a collaborator adds the label **`autose`** (or comments `/autose`).
3. The run opens a PR `autose/issue-N`. A person clicks **Approve workflows to run** on the PR so the
   required `ci-tests` check attaches (ADR-002 amendment), reads the review, and decides.
4. On any PR, a collaborator can comment **`/autose review`** (Haiku) or **`/autose review reviewer_sonnet`**
   to run only the Reviewer.
5. Experiments: `gh workflow run autose.yml -f issue=N -f variant=no_tester` (own branch `autose/issue-N-<variant>`).

## Repository layout

```
README.md            this file
report.pdf           the report
ARCHITECTURE.md      TinyDB architecture (from Assignment 2), read by the Design agent and Reviewer
architecture/
  views/             component view, sequence view (real run), stage map
  decisions/         ADR-001.md ... ADR-010.md (amendments dated inside)
.github/workflows/   autose.yml (the workflow), ci.yml (required check)
workflow/            orchestrator, release, review, checks, agent runner, roles, prompts/
experiment/
  issues/            the 5 issue texts
  hidden_tests/      hidden acceptance tests (added after the final run)
  seeded_prs/        the 5 seeded PRs: mapping, private checks
  variants.md        what each decision-experiment variant changes
results/
  results.csv        one row per run
  runs.md            links to every Actions run, PR and review
```

## Use of AI

Claude Code (Claude Opus 5.5) was used substantially as a coding assistant to write the workflow
code, prompts, seeded PRs and drafts of the documentation, under step-by-step direction. Every
design decision (all ADRs, the model choices, the experiment design and the usage policy) was
made by me and is recorded with its alternatives in the ADRs and the decision log; the ADRs
and their reasoning are my own. The agents inside the workflow run on Claude Haiku 5.5 and
Claude Sonnet 5.5 through the Claude Agent SDK.

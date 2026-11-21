# AutoSE Assignment 3: Issue In, Pull Request Out

An agentic SDLC workflow built on GitHub Actions. A maintainer adds the `autose` label to an
issue, and a set of agents turns it into a tested pull request reviewed by an
independent agent. A person makes the final merge decision.

> 🚧 Work in progress. The sections marked TODO are filled in as the assignment proceeds.

## Subject

| | |
|---|---|
| Fork | https://github.com/RajaiTarun/autose-a3-tinydb |
| Upstream | https://github.com/msiemens/tinydb |
| Pinned commit | `edff96aeb2616402e9489d46e90a592c05565621` |
| Protected branch | `main` (renamed from upstream's `master`; PR required, no bypass) |
| Baseline test suite | 228 passed in 0.94 s (Python 3.13) |

## Models

| Role | Model |
|---|---|
| Spec, Design, Implementer, Tester agents | Claude Sonnet 5.5 (`claude-sonnet-5-5`) |
| Reviewer agent | Claude Sonnet 5.5 (`claude-sonnet-5-5`), with a separate job, prompt, context and permissions |

Billing: Claude Pro subscription token (`CLAUDE_CODE_OAUTH_TOKEN` secret). Usage credits are off,
so the spending limit is $0. No API key is used. Total tokens used: TODO.

## How to trigger the workflow

TODO

## Repository layout

```
README.md            this file
report.pdf           TODO
architecture/
  views/             component view, sequence view, stage map
  decisions/         ADR-001.md … (superseded ADRs are kept)
workflow/            copy of .github/workflows/ plus all agent code and prompts
experiment/
  issues/            the 5 issue texts
  hidden_tests/      added after the final run (see the README in that folder)
  seeded_prs/        the 5 reviewer-check PRs (diffs + labels)
  variants.md        what each decision-experiment variant changes
results/
  results.csv
  runs.md            links to every Actions run, PR and review
```

## Use of AI

TODO

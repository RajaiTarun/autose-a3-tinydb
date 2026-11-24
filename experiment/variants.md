# Decision experiments

Both experiments change exactly one thing in `workflow/roles.py` (`VARIANTS`) or the
stage list; everything else (prompts, checks, budgets, issues, hidden tests) stays the same.
Usage policy (decision 5.5): the cheapest model first; a more expensive variant only where needed.

## Experiment A: Reviewer model (ADR-006 / ADR-008)
- **baseline**: Reviewer on `claude-haiku-5-5`, independent job, sees only the issue/PR text, the diff and the code.
- **reviewer_sonnet**: identical, but the Reviewer runs on `claude-sonnet-5-5`.
- Triggered with `/autose review` and `/autose review reviewer_sonnet` on the 5 seeded PRs (#27-#31).
- Each seeded PR passes CI and hides one bug (see `experiment/seeded_prs/MAPPING.md`).
- Measure: did the Reviewer request changes, and did it name the seeded bug with evidence?

## Experiment B: separate Tester (ADR-001 / ADR-003)
- **baseline**: the Tester agent (Haiku) writes the tests from the spec and design, without the Implementer's notes.
- **no_tester**: the Tester stage is skipped; the Implementer (Sonnet) is told to write one test per AC itself.
- Run on issues #4 and #5 (branches `autose/issue-N-no_tester`), compared with baseline runs 1 and 2.
- Measure: stage pass/fail, hidden tests passed, tokens, and whether the self-written tests would catch a regression.

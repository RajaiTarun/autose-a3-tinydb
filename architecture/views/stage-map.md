# Stage map

| # | Stage | Agent (model) | Inputs | Artifact | Check (how) | Who decides | On failure |
|---|---|---|---|---|---|---|---|
| 1 | Requirements | Spec agent (Haiku 5.5), A1 skill | issue text (untrusted) | `spec.md` + `notes_spec.md` | **Code:** ≥1 AC; every AC has Given/When/Then. **LLM judge (Haiku):** every AC testable, yes/no + reason | orchestrator | retry once with judge feedback → stop, reason written into `spec.md` |
| 2 | Design | Design agent (Haiku 5.5) | issue, `spec.md`, spec notes, `ARCHITECTURE.md`, code | `design.md` + `notes_design.md` | **Code (`ast`):** a "Changes" table names ≥1 file and function; each one exists in the code or is marked `NEW` | orchestrator | retry once → stop |
| 3 | Implementation | Implementer agent (Sonnet 5.5) | `spec.md`, `design.md`, design notes, code, last test failures (on retry) | `diff.patch` + `notes_impl.md` | **Code:** `pip install -e .` and `python -m compileall tinydb` succeed; diff not empty | orchestrator | retry within the stage 3↔4 budget |
| 4 | Testing | Tester agent (Haiku 5.5) | `spec.md`, `design.md`, design notes, `diff.patch`, code (**not** the Implementer's notes) | `test_report.md` | **Code:** a `test_ac<N>_*` test exists for every AC; full `pytest` exit 0 | orchestrator | → stage 3 with failures (≤2 retries) → stage 2 once → stop |
| 5 | Release | `release.py` (no LLM) | branch, artifacts | `pr.md` + PR link | **Code:** PR open; `ci-tests` (started with `workflow_dispatch`) = success | orchestrator | stop, reason in `pr.md` |
| 6 | Review | Reviewer agent (Haiku 5.5), separate job | issue, PR diff, code at PR head **only** | `review.md` + verdict JSON | **Code:** verdict JSON valid; every point cites evidence; checklist complete. Verdict `approve` / `changes(design\|implement)` | review.py reads the verdict | changes + round < 2 → re-dispatch from the named stage; otherwise end. **A person merges or closes.** |

Budgets (ADR-009): max_turns Spec 8 · Design 12 · Implementer 25 · Tester 20 · Reviewer 15; 30-minute job timeout.

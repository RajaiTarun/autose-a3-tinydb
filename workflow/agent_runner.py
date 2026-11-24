"""Runs one agent with its role's model, tools and budget.

AUTOSE_DRY_RUN=1 replaces every model call with a canned stub, so the whole
pipeline can be tested end to end without using any Claude usage.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from roles import role_config

DRY_RUN = os.environ.get("AUTOSE_DRY_RUN", "").lower() in ("1", "true", "yes")


@dataclass
class AgentResult:
    text: str
    tokens_in: int = 0
    tokens_out: int = 0
    turns: int = 0
    error: str | None = None


def run_agent(role: str, system_prompt: str, user_prompt: str, cwd: Path,
              variant: str = "baseline") -> AgentResult:
    cfg = role_config(role, variant)
    if DRY_RUN:
        return _STUBS[role](user_prompt, cwd)
    return _run_real(role, cfg, system_prompt, user_prompt, cwd)


def _run_real(role, cfg, system_prompt, user_prompt, cwd) -> AgentResult:
    raise NotImplementedError("Real agents are wired in Phase 4 step 3.")


# --------------------------------------------------------------------------- stubs
def _stub_spec(prompt, cwd):
    return AgentResult(
        "<status>ready</status>\n<spec>\n# Spec (dry run)\n\n## Acceptance criteria\n"
        "- AC-001: Given a database, When the dry-run check runs, Then it passes.\n</spec>\n"
        "<notes>Dry-run spec. One AC.</notes>")


def _stub_judge(prompt, cwd):
    return AgentResult('{"testable": true, "problems": []}')


def _stub_design(prompt, cwd):
    return AgentResult(
        "<design>\n# Design (dry run)\n\n## Changes\n\n| File | Function | Change |\n|---|---|---|\n"
        "| tinydb/version.py | NEW | add a dry-run marker comment |\n</design>\n"
        "<notes>Dry-run design.</notes>")


def _stub_implement(prompt, cwd):
    f = Path(cwd) / "tinydb" / "version.py"
    f.write_text(f.read_text() + "# autose dry-run marker\n")
    return AgentResult("<notes>Appended a comment to tinydb/version.py.</notes>")


def _stub_test(prompt, cwd):
    issue = os.environ.get("ISSUE", "0")
    (Path(cwd) / "tests" / f"test_autose_issue_{issue}.py").write_text(
        "def test_ac001_dry_run():\n    assert %s\n"
        % ("False" if os.environ.get("AUTOSE_STUB_FAIL") == "test" else "True"))
    return AgentResult("Wrote one test per AC.")


def _stub_review(prompt, cwd):
    return AgentResult(
        "<review>\n# Review (dry run)\n- Meets the issue: pass\n- Correctness and edge cases: pass\n- Tests are meaningful: pass\n- Fits ARCHITECTURE.md: pass\n- No unrelated changes: pass\nEvidence: dry run, no real check.\n</review>\n"
        '<verdict>{"verdict": "approve", "target_stage": null, "concerns": []}</verdict>')


_STUBS = {"spec": _stub_spec, "judge": _stub_judge, "design": _stub_design,
          "implement": _stub_implement, "test": _stub_test, "review": _stub_review}

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


def _base_tools(allowed: list[str]) -> list[str]:
    """Built-in tools to expose: 'Bash(pytest:*)' -> 'Bash'. Nothing else exists for the agent."""
    return sorted({t.split("(")[0] for t in allowed})


def _run_real(role, cfg, system_prompt, user_prompt, cwd) -> AgentResult:
    import anyio
    from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, ResultMessage, TextBlock, query

    options = ClaudeAgentOptions(
        model=cfg["model"],
        system_prompt=system_prompt,
        tools=_base_tools(cfg["tools"]),   # the only tools that exist (ADR-005)
        allowed_tools=cfg["tools"],        # e.g. Bash only as Bash(pytest:*)
        permission_mode="dontAsk",         # anything not allowed is denied, never prompted
        setting_sources=[],                # ignore any settings/CLAUDE.md files (isolation)
        max_turns=cfg["max_turns"],        # ADR-009 budget
        effort=cfg.get("effort"),
        cwd=str(cwd),
    )
    texts: list[str] = []
    result: ResultMessage | None = None

    async def _go():
        nonlocal result
        async for msg in query(prompt=user_prompt, options=options):
            if isinstance(msg, AssistantMessage):
                texts.extend(b.text for b in msg.content if isinstance(b, TextBlock))
            elif isinstance(msg, ResultMessage):
                result = msg

    anyio.run(_go)
    u = (result.usage if result else None) or {}
    tokens_in = sum(u.get(k, 0) or 0 for k in
                    ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
    final = (result.result if result else None) or ""
    # Use the final answer. Only if its tags are missing but an earlier message has them
    # (the model wrote the blocks, then a short "done"), use all text instead.
    joined = "\n".join(texts)
    text = joined if ("<" not in final and "<" in joined) or not final.strip() else final
    for d in (getattr(result, "permission_denials", None) or []):   # visible in the job log
        print(f"[{role}] tool call denied: {str(d)[:300]}")
    error = None
    if result is None or result.is_error:
        error = getattr(result, "subtype", None) or "no result"
        if not text.strip():           # auth, rate limit, outage: fail loudly, don't burn retries
            raise RuntimeError(f"{role} agent failed: {error} "
                               f"(api status {getattr(result, 'api_error_status', None)})")
    return AgentResult(text, tokens_in, u.get("output_tokens", 0) or 0,
                       getattr(result, "num_turns", 0) or 0, error)


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

"""Stage checks (ADR-007). Plain code decides pass/fail; the only LLM involved
is the spec testability judge, whose answer is passed in as a function."""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

AC_RE = re.compile(r"^\s*(?:[-*]\s*)?\**(AC-(\d+))\**\s*[:.)\-–]?\s*(.*)$", re.M)


def tag(text: str, name: str) -> str | None:
    m = re.search(rf"<{name}>(.*?)</{name}>", text, re.S)
    return m.group(1).strip() if m else None


def parse_acs(spec: str) -> dict[str, str]:
    """AC id -> its text (the line plus following lines until the next AC/heading)."""
    acs, lines, cur = {}, spec.splitlines(), None
    for line in lines:
        m = AC_RE.match(line)
        if m:
            cur = m.group(1)
            acs[cur] = m.group(3)
        elif cur and line.strip() and not line.lstrip().startswith("#"):
            acs[cur] += " " + line.strip()
        elif line.lstrip().startswith("#"):
            cur = None
    return acs


# ---------------------------------------------------------------- stage 1
def check_spec(spec: str, judge) -> tuple[bool, str, list[str]]:
    acs = parse_acs(spec)
    if not acs:
        return False, "No acceptance criteria (AC-nnn) found.", []
    bad = [a for a, t in acs.items()
           if not all(w in t.lower() for w in ("given", "when", "then"))]
    if bad:
        return False, f"ACs not in Given/When/Then form: {', '.join(bad)}", list(acs)
    verdict = judge(spec)
    try:
        v = json.loads(verdict[verdict.index("{"): verdict.rindex("}") + 1])
    except (ValueError, json.JSONDecodeError):
        return False, f"Judge returned unparseable output: {verdict[:200]}", list(acs)
    if not v.get("testable"):
        return False, "Judge: not all ACs are testable: " + "; ".join(v.get("problems", [])), list(acs)
    return True, f"{len(acs)} ACs, all Given/When/Then, judged testable.", list(acs)


# ---------------------------------------------------------------- stage 2
def _symbols(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        if isinstance(node, ast.ClassDef):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(f"{node.name}.{sub.name}")
    return names


def check_design(design: str, repo: Path) -> tuple[bool, str]:
    rows = [r for r in design.splitlines()
            if r.strip().startswith("|") and ".py" in r]
    if not rows:
        return False, "Design has no Changes table naming .py files."
    problems = []
    for r in rows:
        cells = [c.strip(" `") for c in r.strip().strip("|").split("|")]
        file, symbol = cells[0], (cells[1] if len(cells) > 1 else "")
        is_new = "NEW" in r
        p = repo / file
        if not p.exists():
            if not is_new:
                problems.append(f"{file} does not exist and is not marked NEW")
            continue
        if symbol and symbol != "NEW" and not is_new:
            sym = symbol.split("(")[0].strip()
            if sym not in _symbols(p):
                problems.append(f"{file}: {sym} not found")
    if problems:
        return False, "; ".join(problems)
    return True, f"{len(rows)} change(s); every file/function exists or is marked NEW."


# ---------------------------------------------------------------- stage 3
def check_build(repo: Path, diff: str) -> tuple[bool, str]:
    if not diff.strip():
        return False, "The implementation produced no code changes."
    for cmd in ([sys.executable, "-m", "compileall", "-q", "tinydb"],
                [sys.executable, "-c", "import tinydb"]):
        r = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
        if r.returncode:
            return False, f"`{' '.join(cmd)}` failed:\n{(r.stdout + r.stderr)[-1500:]}"
    return True, "Code compiles and tinydb imports."


# ---------------------------------------------------------------- stage 4
def check_tests(repo: Path, issue: str, ac_ids: list[str]) -> tuple[bool, str, str]:
    files = sorted((repo / "tests").glob(f"test_autose_issue_{issue}*.py"))
    src = "\n".join(f.read_text() for f in files)
    missing = [a for a in ac_ids
               if not re.search(rf"def test_{a.lower().replace('-', '')}_", src)]
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-cov"],
                       cwd=repo, capture_output=True, text=True)
    out = (r.stdout + r.stderr)[-4000:]
    if not files:
        return False, f"No test file tests/test_autose_issue_{issue}*.py", out
    if missing:
        return False, f"No test for: {', '.join(missing)} (expected def test_ac001_...)", out
    if r.returncode:
        return False, "Test suite failed.", out
    return True, f"{len(ac_ids)} AC test(s) present; full suite passed.", out

"""Stage 5, Release: plain script, no LLM (ADR-001).

Pushes the branch, opens the PR (or reuses it in a review round), starts ci.yml
with workflow_dispatch (PRs opened with GITHUB_TOKEN do not trigger CI, decision
1.6a) and waits for it. Check: PR open and ci-tests green.
"""
from __future__ import annotations

import json
import os
import time


def run(st, adir, branch, issue, issue_title, gh, sh, record, stop, commit) -> None:
    rnd = st.get("round", 0)
    repo_url = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', '')}"
    report = (adir / "test_report.md").read_text().splitlines()[2] if (adir / "test_report.md").exists() else ""
    variant = st.get("variant", "baseline")
    tag = "" if variant == "baseline" else f" [{variant}]"
    body = ((f"Closes #{issue}\n\n" if variant == "baseline" else
             f"Experiment variant `{variant}` for #{issue}; not meant to be merged.\n\n")
            f"Opened by the AutoSE workflow (round {rnd}). **A person decides whether to merge; "
            f"AutoSE never merges.**\n\n"
            f"| Stage | Artifact |\n|---|---|\n"
            f"| 1 Requirements | [`spec.md`]({repo_url}/blob/{branch}/.autose/issue-{issue}/spec.md) |\n"
            f"| 2 Design | [`design.md`]({repo_url}/blob/{branch}/.autose/issue-{issue}/design.md) |\n"
            f"| 3 Implementation | [`diff.patch`]({repo_url}/blob/{branch}/.autose/issue-{issue}/diff.patch) |\n"
            f"| 4 Testing | [`test_report.md`]({repo_url}/blob/{branch}/.autose/issue-{issue}/test_report.md) |\n\n"
            f"{report}\n\nState and token use: `.autose/issue-{issue}/state.json`.")
    (adir / "pr.md").write_text(body + "\n")
    st["status"] = "ci_pending"
    # Last commit of the run: nothing may be committed after CI starts, or the PR head
    # would move away from the commit that ci-tests checked. The final state (CI result)
    # goes to the Actions artifact; the CI result is also shown on the PR.
    (adir / "state.json").write_text(json.dumps(st, indent=2) + "\n")
    commit(f"autose(#{issue}): release (pr.md)")

    existing = json.loads(gh("pr", "list", "--head", branch, "--state", "open",
                             "--json", "number,url"))
    if existing:
        pr, url = existing[0]["number"], existing[0]["url"]
        gh("pr", "edit", str(pr), "--body-file", str(adir / "pr.md"))
    else:
        url = gh("pr", "create", "--base", "main", "--head", branch,
                 "--title", f"AutoSE #{issue}{tag}: {issue_title}"[:120],
                 "--body-file", str(adir / "pr.md"))
        pr = int(url.rstrip("/").split("/")[-1])

    head = sh("git", "rev-parse", "HEAD")
    gh("workflow", "run", "ci.yml", "--ref", branch)
    run_id = None
    for _ in range(24):                         # wait up to 2 min for the run to appear
        time.sleep(5)
        runs = json.loads(gh("run", "list", "--workflow", "ci.yml", "--branch", branch,
                             "--event", "workflow_dispatch", "--limit", "5",
                             "--json", "databaseId,headSha"))
        run_id = next((r["databaseId"] for r in runs if r["headSha"] == head), None)
        if run_id:
            break
    if not run_id:
        record(st, "release", 1, False, "CI run did not start")
        stop(st, "release", f"PR {url} is open but ci.yml did not start within 2 minutes.")
    for _ in range(80):                         # wait up to ~10 min for CI to finish
        info = json.loads(gh("run", "view", str(run_id), "--json", "status,conclusion,url"))
        if info["status"] == "completed":
            break
        time.sleep(8)
    ok = info.get("conclusion") == "success"
    st["pr"], st["pr_url"], st["ci_run"] = pr, url, info["url"]
    record(st, "release", 1, ok, f"PR {url}; CI {info.get('conclusion')} ({info['url']})")
    if not ok:
        stop(st, "release", f"PR {url} is open but CI failed: {info['url']}")
    # GitHub holds the PR's own pull_request CI run (opened by the bot) until a person
    # approves it; only that run counts as the required ci-tests check (ADR-002 amendment).
    gh("pr", "comment", str(pr), "--body",
       f"AutoSE stage 5: `ci-tests` passed on {head[:7]} ({info['url']}). "
       "**To merge: a person must click _Approve workflows to run_ on this PR** so the "
       "required `ci-tests` check is attached. AutoSE never merges.")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"pr={pr}\n")

# Component view

The components, the tools and permissions each one holds, and how they call each other.
The token boundary is the key feature: **only plain code (orchestrator, release script)
holds a GitHub token. No LLM agent does.**

```mermaid
flowchart TB
    Human([Maintainer<br/>OWNER / MEMBER / COLLABORATOR])
    Issue[(GitHub issue)]
    Human -- "adds label autose<br/>or comments /autose" --> Issue

    subgraph GA[GitHub Actions: workflow autose.yml]
        Gate["gate job<br/><i>permissions: issues read</i><br/>checks author_association,<br/>ignores bots"]

        subgraph BUILD["build job · contents/PR/issues write · 30 min"]
            Orch["orchestrator.py<br/>(plain Python state machine, not an LLM)<br/>holds GH_TOKEN · runs every check · decides next stage"]
            Spec["Spec agent · Haiku 5.5<br/>A1 skill · tools: Read, Grep, Glob<br/>max_turns 8"]
            Design["Design agent · Haiku 5.5<br/>ARCHITECTURE.md · tools: Read, Grep, Glob<br/>max_turns 12"]
            Impl["Implementer agent · Sonnet 5.5<br/>tools: Read, Grep, Glob, Edit, Write, Bash(pytest, python)<br/>max_turns 25"]
            Tester["Tester agent · Haiku 5.5<br/>tools: Read, Grep, Glob, Edit, Write, Bash(pytest, python)<br/>max_turns 20"]
            Judge["Spec judge · Haiku 5.5<br/>no tools · 1 turn"]
            Release["release.py<br/>(plain script, no LLM)<br/>git push · gh pr create · gh workflow run ci.yml"]
        end

        subgraph REVIEW["review job · contents read, PR write · no push"]
            RevRunner["review.py (plain code)<br/>fresh shallow checkout of PR head<br/>posts the review · re-dispatches"]
            Reviewer["Reviewer agent · Haiku 5.5<br/>own prompt + checklist<br/>tools: Read, Grep, Glob, Bash(pytest)<br/>max_turns 15"]
        end
    end

    CI["ci.yml · ci-tests<br/>(required status check)"]
    PR[(Pull request<br/>branch autose/issue-N)]
    Branch[(".autose/issue-N/<br/>state.json + artifacts + notes")]

    Issue --> Gate --> Orch
    Orch -- "issue (untrusted)" --> Spec
    Orch -- "spec.md" --> Judge
    Orch -- "issue, spec.md, spec notes" --> Design
    Orch -- "spec.md, design.md, design notes,<br/>test failures (on retry)" --> Impl
    Orch -- "spec.md, design.md, design notes,<br/>diff.patch (NOT impl notes)" --> Tester
    Orch --> Release
    Orch <--> Branch
    Release --> PR
    Release -- "workflow_dispatch" --> CI
    CI -- "status" --> PR
    PR --> RevRunner
    RevRunner -- "issue + PR diff + code at PR head ONLY" --> Reviewer
    Reviewer -- "review.md + verdict JSON" --> RevRunner
    RevRunner -- "COMMENT review" --> PR
    RevRunner -. "changes requested, round < 2:<br/>workflow_dispatch(start_stage, round+1)" .-> Orch
    PR -- "merge or close (person only)" --> Human
```

| Component | Kind | Model | GitHub token? | Can push? |
|---|---|---|---|---|
| gate | Actions job (bash) | — | read (issues) | no |
| orchestrator.py | plain Python | — | **yes** | yes (branch `autose/*` only; `main` is protected) |
| Spec / Design / Tester agents | LLM agent | Haiku 5.5 | **no** | no |
| Implementer agent | LLM agent | Sonnet 5.5 | **no** | no (it edits files; the orchestrator commits them) |
| Spec judge | LLM, single call | Haiku 5.5 | no | no |
| release.py | plain Python | — | yes | yes (branch only) |
| review.py | plain Python | — | yes (PR write, contents **read**) | **no** |
| Reviewer agent | LLM agent | Haiku 5.5 | **no** | no |
| ci.yml | Actions workflow | — | contents read | no |

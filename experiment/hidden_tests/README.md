# Hidden acceptance tests

The hidden tests (2–4 per issue) are **deliberately not committed yet**.

The agents in the AutoSE workflow check out this repository, so any test committed
here, even one deleted later, could be found in the working tree or in git history.
Until the last experiment run has finished, the tests are kept outside the repository
and run against each branch the workflow produces only *after* the run ends, as in A2.

They will be added to this folder in a single final commit after the last run. The
commit timestamp, compared with the run timestamps in `results/runs.md`, shows that
no agent could have seen them.

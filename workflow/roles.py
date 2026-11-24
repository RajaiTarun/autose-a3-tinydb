"""Per-role configuration: model, tools and turn budget.

One place for ADR-005 (tools), ADR-006 (models) and ADR-009 (budgets).
Experiment variants override entries here (see VARIANTS).
"""

HAIKU = "claude-haiku-5-5"
SONNET = "claude-sonnet-5-5"

READ_ONLY = ["Read", "Grep", "Glob"]
EDIT = ["Edit", "Write"]
RUN_TESTS = ["Bash(pytest:*)", "Bash(python -m pytest:*)", "Bash(python:*)"]

ROLES = {
    #  role         model    tools                         max_turns
    "spec":      {"model": HAIKU,  "tools": READ_ONLY,                     "max_turns": 8},
    "judge":     {"model": HAIKU,  "tools": [],                            "max_turns": 1},
    "design":    {"model": HAIKU,  "tools": READ_ONLY,                     "max_turns": 12},
    "implement": {"model": SONNET, "tools": READ_ONLY + EDIT + RUN_TESTS,  "max_turns": 25},
    "test":      {"model": HAIKU,  "tools": READ_ONLY + EDIT + RUN_TESTS,  "max_turns": 20},
    "review":    {"model": HAIKU,  "tools": READ_ONLY + ["Bash(pytest:*)", "Bash(python -m pytest:*)"],
                  "max_turns": 15},
}

# Retry budgets (ADR-009)
MAX_IMPL_TEST_RETRIES = 2   # stage 4 -> 3 loops before escalating
MAX_DESIGN_BACKTRACKS = 1   # stage 4 -> 2 after retries are used up
MAX_STAGE_RETRIES = 1       # spec / design re-attempt after a failed check
MAX_REVIEW_ROUNDS = 2

# Decision-experiment variants (experiment/variants.md). "baseline" changes nothing.
VARIANTS = {
    "baseline": {},
    # Experiment A (ADR-006/008): reviewer on a different, stronger model
    "reviewer_sonnet": {"review": {"model": SONNET}},
    # Experiment B (ADR-001/003): no separate Tester; the Implementer writes the tests
    "no_tester": {},
}


def role_config(role: str, variant: str = "baseline") -> dict:
    cfg = dict(ROLES[role])
    cfg.update(VARIANTS.get(variant, {}).get(role, {}))
    return cfg

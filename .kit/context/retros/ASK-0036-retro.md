## ASK-0036 — Expand Reconfigure to Catch All Identity Leaks (PR #24)

**Date**: 2026-02-28
**Agent**: feature-developer-v3
**Scorecard**: 17 threads, 0 regressions, 5 fix rounds, 6 commits

### What Worked

1. **TDD approach caught integration issues early** — Writing 27 tests upfront (across 5 test classes) meant each replacement pattern was verified before shipping. The test suite grew to 50 tests by the end, and the idempotency test was particularly valuable.
2. **Batch fixing bot threads saved rounds** — Grouping all fixes per round into a single commit+push reduced the number of bot re-scan cycles. Each round addressed all findings at once rather than one-at-a-time.
3. **`gh-review-helper.sh` made thread management efficient** — The `threads`, `reply`, and `resolve` subcommands eliminated manual GraphQL/API fumbling. Every thread got a reply and resolution in seconds.
4. **Hybrid exclusion matching was the right final design** — Segment matching for single-component names (`tests`) + prefix matching for multi-component paths (`docs/UPSTREAM`) correctly handles all edge cases. Arrived at this after iterating through substring → segment → hybrid.

### What Was Surprising

1. **Each fix round introduced new findings from the bots** — Round 4's fix for substring matching (#12) directly caused the `docs/UPSTREAM` regression (#17) in Round 5. The bots caught a real regression chain: fix for false positives created false negatives.
2. **Black formatting caused every commit to fail on first attempt** — Pre-commit Black reformatted files on every single commit (6/6), requiring a stage-and-recommit cycle each time. Ruff format before committing didn't prevent this — Black and Ruff disagree on some formatting choices.
3. **17 threads across 5 rounds for a ~300-line feature** — The ratio of review churn to code was surprisingly high. Most findings were legitimate edge cases (unrecognized URL formats, path matching semantics), not style nitpicks.

### What Should Change

1. **Pre-format with Black (not Ruff) before committing** — Every commit failed the Black hook because I ran `ruff format` instead. The project uses Black as its canonical formatter in pre-commit hooks. Should run `black` directly, or add a script that runs the exact pre-commit formatter.
2. **Exclusion matching should have been designed with both segment and prefix cases from the start** — The task spec listed `docs/UPSTREAM` as an exclusion target alongside `tests/`, but I didn't notice the different matching semantics needed until BugBot caught it. The pre-implementation phase should explicitly enumerate matching semantics for each exclusion pattern.
3. **Consider a bot-round budget in the workflow** — 5 rounds is excessive. After Round 3, findings were increasingly about the fixes themselves rather than the original code. A hard cap of 3 rounds with "resolve remaining trivial/low with justification" would have saved ~30 minutes.

### Permission Prompts Hit

None. All `git` and `gh` commands were auto-approved. The `./scripts/gh-review-helper.sh` commands were also pre-allowed.

### Process Actions Taken

- [ ] Add `black scripts/project tests/test_project_script.py` to the pre-commit formatting step in agent workflow docs
- [ ] Document the hybrid exclusion pattern (segment vs prefix matching) in `.kit/context/patterns.yml`
- [ ] Consider adding a bot-round budget (max 3 rounds) to the feature-developer-v3 workflow before escalating to resolve-with-justification
- [ ] Add `docs/UPSTREAM` prefix matching edge case to the pre-implementation checklist for verify/scan features

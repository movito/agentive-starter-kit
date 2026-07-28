# KIT-0040 Handoff — feature-developer

**Task**: `.kit/tasks/5-done/KIT-0040-kit-0034-retro-followups.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-05 (planner-f5)
**Estimated effort**: 3–5 hours

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## Mission

Clear the KIT-0034 retro debt: fix two real, shipped bugs in the KIT-LOCAL
marker merge (`kit_markers.py`), turn KIT-0034's manual stub-`gh`
verification matrix into CI regression coverage, and stop task-status moves
from stranding stale paths in coordination metadata.

**Sequencing (planner decision, see task Evaluation section): implement F3
first.** If F1/F2 grow or stall, ship F3 as its own PR immediately — the
whitespace-clobber bug silently destroys customized consumer content — and
let F1/F2 follow in a second PR.

## Implementation guidance

### F3 — `scripts/local/kit_markers.py` (do this first)

Both findings are from BugBot on merged PR #58 (commit `a2d8645`), verified
real by planner triage 2026-07-05. Anchors:

- **Bug 1 — BEGIN-substring false positive** (`merge`, line ~120): the
  malformed-region check is
  `if preserved is None and f"<!-- BEGIN KIT-LOCAL: {name} -->" in consumer`.
  A *preserved, valid* file that merely mentions another region's BEGIN
  comment in prose (docs, examples) trips this and raises, aborting
  `bootstrap-consumer.sh` under `set -e` instead of seeding the missing
  region from placeholders. Fix: scope the check to marker *lines* (e.g.
  anchor to line start/whole-line match), not raw substring containment.
- **Bug 2 — whitespace marker clobber** (`extract_region` line ~75 +
  `_region_pattern` line ~42): if a consumer's BEGIN marker drifts from the
  strict regex (extra spaces, minor edits) while customized body text
  remains, `extract_region` returns None, the exact-substring malformed
  check doesn't fire (the drifted marker no longer matches the f-string
  either), and `merge` applies placeholders — silently replacing customized
  content with TODO text (re-bootstrap always passes `--project-name`).
  Fix options: tolerate benign whitespace variance in `BEGIN_RE` /
  `_region_pattern` (e.g. `\s+` between tokens, trailing spaces before
  `-->`), or detect a "looks like a KIT-LOCAL marker but doesn't parse"
  line and fail fast. Either is acceptable; silent clobber is not.
  Whichever you choose, keep the two detection paths (parse regex and
  malformed check) consistent so nothing falls between them again.
- TDD: write regression tests for both scenarios in
  `tests/test_kit_markers.py` (currently 30 test functions) BEFORE fixing.
  Contract to preserve (N2): stdlib-only, byte-preserving for well-formed
  regions, CRLF-tolerant, fail-fast on genuinely malformed input.

After the fix merges, reply to and resolve the two PR #58 threads with a
pointer to your PR. Both threads are on `scripts/local/kit_markers.py`,
author `cursor`, currently the only unresolved threads on PR #58. Verified
query (planner ran 2026-07-05):

```
gh api graphql -f query='query { repository(owner: "movito", name: "agentive-starter-kit") { pullRequest(number: 58) { reviewThreads(first: 20) { nodes { id isResolved path } } } } }'
```

(add `id` to get thread node IDs for resolution; `gh-review-helper.sh`'s
`threads`/`reply`/`resolve` subcommands wrap this.)

### F1 — stub-`gh` pytest harness for `preflight-check.sh`

- Pattern proven in KIT-0034: a fake `gh` executable on PATH returning
  canned payloads, running the **real** `scripts/core/preflight-check.sh`.
  Suggested: `tests/test_preflight_check.py` with a fixture that writes the
  stub into a temp dir, prepends it to PATH, and dispatches on the `gh`
  argv (e.g. via a scenario env var or argv-keyed canned files).
- Minimum 8 scenarios (retro matrix): Gate 2 fallback PASS; no-review FAIL;
  unresolved-thread FAIL; CHANGES_REQUESTED FAIL; check-run source PASS;
  N3 precedence (completed non-success beats pending); gh-error FAIL (not
  PENDING); empty-fetch PENDING.
- **API-shape note (verified in KIT-0034)**: CodeRabbit reports via the
  legacy commit-status API (`context: "CodeRabbit"`); BugBot via
  check-runs. Canned payloads must model the right surface per bot — read
  the current Gate 2/3 implementation in `preflight-check.sh` first and
  mirror the payload shapes it actually parses.
- **N1 trap**: subprocess `git`/script runs must use a cleaned environment —
  see the `GIT_DIR`/`core.bare` gotcha in
  `.kit/context/workflows/TESTING-WORKFLOW.md` and `_clean_git_env()` in
  `tests/test_project_sync.py`.
- The shell script itself does not change (KIT-0034 N2 stands).

### F2 — pair task moves with metadata updates

- Preferred: extend `scripts/core/project` (`start`/`move`/`complete`) to
  rewrite the numbered-folder segment of task paths it already knows about
  in `.kit/context/agent-handoffs.json` (`details_link`, `handoff_file`
  are file paths but `details_link` may point at the task file) and the
  `**Task**:` line in `.kit/context/<TASK-ID>-HANDOFF-*.md`. This has
  recurred three times now (CodeRabbit round on KIT-0034; stale handoff
  after the 4-in-review move; stale again after the done move).
- Keep it conservative: only rewrite strings matching
  `.kit/tasks/<any-status-folder>/<TASK-ID>-*.md` for the moved TASK-ID;
  touch nothing else. Follow `patterns.yml` (identifier comparison with
  `==`, error strategy for the CLI layer) and add tests in
  `tests/test_project_script.py` (fixtures mock `project_dir` via
  `mock_project_path` in conftest.py).
- Fallback if the tooling fix turns out non-trivial: document the
  same-commit pairing as a mandatory step in
  `.kit/context/workflows/COMMIT-PROTOCOL.md` and state the choice in the
  PR. Don't gold-plate.

## Test approach

- `pytest` directly (not `python3 -m pytest`).
- `pytest tests/test_kit_markers.py` — all existing + new regression tests.
- `pytest tests/test_preflight_check.py` (new) and
  `tests/test_project_script.py` (extended).
- N3: any new test reading `scripts/local/` must be excluded from the
  consumer `tests/` rsync in `bootstrap-consumer.sh` and module-skip when
  its dependency is absent (`test_kit_markers.py` and
  `test_bootstrap_consumer.py` show the pattern). `test_preflight_check.py`
  targets `scripts/core/` — it ships to consumers, so it must NOT import
  from `scripts/local/`.
- `./scripts/core/ci-check.sh` before pushing.

## Evaluation summary

`arch-review-fast`: RESTRUCTURE_NEEDED (split into 3 tasks) — planner
declined the split, accepted the kernel as F3-first PR sequencing. Full
disposition in the task file's Evaluation section; log in
`.adversarial/logs/KIT-0040-kit-0034-retro-followups--arch-review-fast.md`.
No outstanding blockers.

## Out of scope

- Changing `preflight-check.sh` gate logic itself (KIT-0034 landed it;
  F1 only adds coverage)
- Rewriting preflight or `kit_markers.py` beyond the two named bugs
- KIT-0035/0037/0038/0039 items — separate tasks, don't absorb
- Downstream repos — kit-internal only (operator deferral, 2026-07-04)

## PR sizing

F3 (~small diff + 2 regression tests) then F1+F2 should fit one PR total
(< 500 lines). Split F3 out the moment the rest drags — that's the
planner-approved fallback, not scope creep.

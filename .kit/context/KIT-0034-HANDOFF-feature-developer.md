# KIT-0034 Handoff — feature-developer

**Task**: `.kit/tasks/3-in-progress/KIT-0034-preflight-bootstrap-hardening.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-04 (planner-f5)
**Estimated effort**: 2–4 hours

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## Mission

Harden the kit's completion gates and bootstrap machinery against five
failure modes observed across three retros (KIT-0032, KIT-0033, KIT-0036,
session 2026-07-04). The headline is **F1**: preflight Gate 2 has
false-negatived on three consecutive tasks.

## Implementation guidance

All five requirements (F1–F5) are specified in the task file. Concrete
anchors:

### F1 + F4 — `scripts/core/preflight-check.sh` (412 lines)

- **Gate 1 (CI)**: lines ~224–266. `GATE:1:CI:FAIL:No CI runs found for
  latest commit` (line 232) is the false-alarm path — no runs registered yet
  for the head SHA must become a distinct **PENDING/UNKNOWN** state (optionally
  after a short bounded re-poll), while a completed non-success run still
  FAILs. Note line 263 conflates "still running" with FAIL too — same fix
  family, keep "still running" as PENDING, not FAIL.
- **Gate 2 (CodeRabbit)**: lines ~276–291. Currently requires a
  `coderabbitai[bot]` review event on `$CODE_SHA` or `$LATEST_SHA` (GraphQL at
  line 283). Add the fallback: check-run passing AND latest CodeRabbit review
  APPROVED (or COMMENTED with no unresolved threads) AND zero unresolved
  threads → PASS. **Gate 3 (BugBot, lines ~295–324) already implements
  exactly this check-run fallback pattern at line 319 — mirror its
  structure.** Gate 4 (lines ~330–349) already computes unresolved thread
  counts; reuse that query/logic rather than duplicating it.
- Keep the strict SHA match as the primary signal; the fallback only rescues
  the green-everywhere case (N1: a PR with no review at all, or any
  unresolved thread, must still FAIL).
- **N2**: stays shell + `gh`. The arch evaluator suggested a Python rewrite;
  planner declined (see Evaluation section in the task file). Do not migrate.

### F2 — self-review checklist item

- Skill lives at `.kit/skills/self-review/`. Add the item: any new test
  importing from `scripts/local/` must be excluded from the consumer `tests/`
  rsync in `bootstrap-consumer.sh` (and should module-skip if its dependency
  is absent). Check whether feature-developer's Phase 4 checklist
  (`.claude/agents/feature-developer.md` and the `-f5` fork) references the
  same list — if so, keep them consistent (edit both or neither).

### F3 — temp-then-commit guideline

- Document the two-pass pattern (stage all outputs to temp, `mv` into place
  only after every step succeeds; never per-item `mv` inside a `set -e`
  loop) with a short before/after example. Suggested home:
  `.kit/context/workflows/` alongside the other workflow docs. Reference the
  KIT-0033 atomicity bug as the motivating case.

### F5 — bootstrap marker-membership test

- New pytest (suggested: `tests/test_bootstrap_consumer.py`) asserting every
  `.claude/agents/*.md` containing `KIT-LOCAL` markers appears in BOTH
  `KIT_AGENTS` (line ~206 of `scripts/local/bootstrap-consumer.sh`) and
  `AGENT_EXCLUDES` (line ~101). Current expected membership: `planner.md`,
  `planner-f5.md`, `feature-developer.md`, `feature-developer-f5.md`.
  Text-parse the bash arrays — no need to execute the script.
- **Recursive F2 trap**: this test reads `scripts/local/` content, so it must
  itself be added to the consumer `tests/` rsync exclusion in
  `bootstrap-consumer.sh` (same treatment as `test_kit_markers.py`), and
  should skip cleanly if `scripts/local/bootstrap-consumer.sh` is absent.

## Data-shape verification

- Before touching Gate 2, capture real `gh api graphql` output for PR #58
  (KIT-0033) — the canonical false-negative case — and for a current green
  PR, so the fallback logic is written against observed shapes, not assumed
  ones.
- There is **no existing test harness** for `preflight-check.sh` or
  `bootstrap-consumer.sh`. Gate-logic verification may be the documented
  manual kind (per acceptance criteria); F5's test is the automatable part.

## Test approach

- `pytest tests/test_bootstrap_consumer.py` (new) — use `pytest` directly,
  not `python3 -m pytest`.
- Manual gate verification: run `./scripts/core/preflight-check.sh` against
  KIT-0033 PR #58 (real-world Gate 2 fallback case) and a current green PR
  (regression on all 7 gates). Record both runs in the PR description.
- `./scripts/core/ci-check.sh` before pushing.

## Evaluation summary

`arch-review-fast`: REVISION_SUGGESTED — log at
`.adversarial/logs/KIT-0034-preflight-bootstrap-hardening--arch-review-fast.md`.
Disposition recorded in the task file's Evaluation section: Python-migration
suggestion **declined** (N2), test-mocking emphasis **accepted**, declarative
boundary config **noted/out-of-scope**. No outstanding blockers.

## Out of scope

- Rewriting preflight in Python (N2; evaluator suggestion declined)
- The `kit_markers.py` manifest-contract idea (task Notes)
- Any downstream-repo work — suwinex/moss migrations are deferred by
  operator decision (2026-07-04); this task is kit-internal only
- KIT-0035/0037/0038/0039 items — they follow in separate tasks; don't
  absorb them even where files overlap

## PR sizing

F1+F4 (one script) + F2 (checklist) + F3 (doc) + F5 (test + rsync exclude)
should fit one PR comfortably (< 500 lines). If it grows, split F3 out —
it's the most independent.

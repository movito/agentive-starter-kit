# Review Starter: KIT-0034 — Preflight & Bootstrap Hardening

**PR**: https://github.com/movito/agentive-starter-kit/pull/69
**Branch**: `feature/KIT-0034-preflight-bootstrap-hardening`
**Task**: `.kit/tasks/4-in-review/KIT-0034-preflight-bootstrap-hardening.md`
**Implemented by**: feature-developer-f5 (2026-07-04/05)

## What this PR does

Hardens the kit's completion gates and bootstrap machinery against five
failure modes from the KIT-0032/0033/0036 retros and the 2026-07-04
session retro:

- **F1** — `preflight-check.sh` Gate 2 (CodeRabbit) gains a fail-closed
  fallback: no review event on the head SHA still PASSes iff CodeRabbit's
  commit status is green AND the latest review is APPROVED/COMMENTED AND
  zero threads are unresolved. Fixes the false negative seen on three
  consecutive tasks.
- **F4** — Gate 1 (CI) reports **PENDING** (new state, exit code 2) for
  "runs not registered yet" (bounded ~10 s re-poll) and "still running";
  a completed non-success run still FAILs, even while siblings run. A
  `gh`-level fetch error FAILs distinctly (not PENDING).
- Gates 2/3/4 share one GraphQL snapshot (3 API calls → 1) so the
  fallback and thread gate can never disagree.
- **F2** — self-review skill v1.1.0 + both feature-developer forks: new
  consumer-sync test boundary checklist item.
- **F3** — `.kit/context/workflows/TEMP-THEN-COMMIT-PATTERN.md` (two-pass
  atomic mutation pattern, linked from CLAUDE.md).
- **F5** — `tests/test_bootstrap_consumer.py`: 6 tests locking KIT-LOCAL
  marker agents into both `KIT_AGENTS` and `AGENT_EXCLUDES`, plus the
  consumer-rsync exclusion of boundary-crossing tests (including itself).

## Review focus suggestions

1. **Gate 2 fallback conditions** (`scripts/core/preflight-check.sh`) —
   is the three-way AND (green signal + APPROVED/COMMENTED latest +
   0 unresolved) the right strictness? N1 requires fail-closed.
2. **Exit code 2 semantics** — PENDING is nonzero by design ("all gates
   confirmed" stays exit 0). Callers were audited (docs only).
3. **Known evaluator blind spot**: shell-script changes have no CI test
   harness — gate logic was verified manually (stub-`gh` matrix recorded
   in the PR description + `.kit/context/reviews/KIT-0034-evaluator-review.md`).

## Verification trail

- Evaluators: code-reviewer-fast-v2 CONCERNS, code-reviewer (o3) FAIL,
  claude-code APPROVED — full triage (accepted fixes + declined-with-
  verification) in `.kit/context/reviews/KIT-0034-evaluator-review.md`
- Bot rounds: CodeRabbit round 1 (4 threads) + round 2 (1 thread), all
  fixed, replied, resolved; BugBot pass (no findings)
- `pytest`: full suite green; pre-commit gauntlet green on every commit

## Follow-ups flagged (not in this PR)

- PR #58 carries 2 unresolved medium-severity BugBot threads on
  `scripts/local/kit_markers.py` (opened at merge time, pre-date this
  task) — planner should triage.

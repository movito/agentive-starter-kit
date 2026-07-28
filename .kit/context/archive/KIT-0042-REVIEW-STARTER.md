# Review Starter: KIT-0042

**Task**: KIT-0042 — Bundle-aware preflight Gates 5/6
**Task File**: `.kit/tasks/4-in-review/KIT-0042-preflight-bundle-support.md`
**Branch**: feature/KIT-0042-preflight-bundle-support -> main
**PR**: https://github.com/movito/agentive-starter-kit/pull/74

## Implementation Summary

- **Route (b) chosen: convention + F1.1** — gates stay strict; bundle
  intelligence lives in process, not gate code (full code-vs-process
  reasoning in the PR description). The bundle test proves pointer files
  pass the exact-name find natively — zero gate-logic change needed for
  the convention itself.
- Gates 5/6 FAIL details now name the full repo-relative pointer path,
  the review-handoff skill, AND the multi-PR-task case (planner's
  2026-07-13 spec addendum, KIT-0035 evidence).
- review-handoff skill (1.1.0): "Bundled PR? Do this FIRST" section —
  lead-task + pointer files, KIT-0037/38/39 files cited as the reference
  shape — plus multi-PR artifact-placement guidance.
- Evaluator-round hardening: Gates 5/6 finds require non-empty regular
  files (`-type f -size +0c`); prefix-boundary property pinned in tests.

## Files Changed

- `scripts/core/preflight-check.sh` (modified — FAIL messages + non-empty check)
- `.kit/skills/review-handoff/SKILL.md` (modified — v1.1.0, bundle section)
- `tests/test_preflight_check.py` (modified — 4 new tests, run() extra_args)
- Task/handoff bookkeeping (moves, agent-handoffs.json)
- Note: branch carries planner commit `f7a6c90` (docs-only retro
  follow-through, includes the KIT-0042 spec addendum this PR implements)

## Test Results

- `pytest tests/test_preflight_check.py` — 14 passed (was 10; +4: bundle
  PASS scenario, F1.1 message content, prefix boundary, empty-pointer)
- `./scripts/core/ci-check.sh` green; TDD red-then-green on both the
  F1.1 assertions and the empty-pointer case

## Automated Review Summary

- CodeRabbit: 1 thread (Gate 5 message lacked the directory) — fixed
  `a30c974`, resolved
- BugBot: pass, no findings
- Evaluators (fast-v2 + o3): 2 accepted (empty-pointer check, boundary
  test), 6 declined with evidence — fast-v2's headline prefix-collision
  claim empirically false (literal separator IS the boundary; tested).
  Full disposition: `.kit/context/reviews/KIT-0042-evaluator-review.md`

## Areas for Review Focus

- The declined Gate 7 prefix observation (`${TASK_ID}*`, no separator) is
  real in principle but out of scope and nil with fixed-width IDs —
  confirm you agree it stays a non-issue
- Message wording: FAIL lines are long (one line each, GATE prefix
  intact) — check they render acceptably in your terminal

## Related ADRs

- None directly; lineage is KIT-0034/KIT-0040 preflight hardening

---
**Ready for human review**

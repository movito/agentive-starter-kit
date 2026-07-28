# Review Starter: KIT-0043

**Task**: KIT-0043 — Preflight Gates 1/2/7 edge-case hardening
**Task File**: `.kit/tasks/4-in-review/KIT-0043-preflight-gates-127-edge-hardening.md`
**Branch**: feature/KIT-0043-preflight-gates-edge-hardening -> main
**PR**: https://github.com/movito/agentive-starter-kit/pull/75

## Implementation Summary

- **F1** — Gate 1 run-list truncation: `--limit` 10 → 50 (`CI_RUN_LIMIT`);
  the event filter moved out of the gh `--jq` so the guard keys on the
  RAW returned count; an at-cap window demotes the verdict to **PENDING**
  (never PASS — an at-cap response is indistinguishable from a truncated
  one). Verdict priority: visible FAIL > at-cap PENDING > PASS > running
  PENDING. `gh run list` flag surface verified (`-c/--commit` real).
- **F2** — status handling restructured around "`completed` is the only
  terminal status": completed non-success stays FAIL; every non-completed
  status (incl. `waiting`, `requested`, `pending`, and future values)
  reads as running → PENDING. No status enumeration to go stale.
- **F3** — Gate 7: `-name "${TASK_ID}-*"` boundary + `-type f -size +0c`
  (CodeRabbit round) + `LC_ALL=C sort` deterministic pick. `head -1`
  sites 221/479/490 not touched by F3, left as-is per the optional
  criterion.
- **F4** — o3's Gate 2 mixed-context claim **does not reproduce**:
  declined with two-layer harness evidence (script's own extracted jq
  filter reduces mixed → `failure`; shell requires exactly `success`).
- Owner/name slug validated before GraphQL interpolation (o3, injection
  hygiene). KIT-0042 decline-table rows updated to point here.
- **Worktree pilot enabling fix**: `test_project_script.py` module-level
  GIT_* isolation fixture (pre-commit exports an absolute `GIT_DIR` in
  worktrees; tmp-repo git calls leaked to the real repo, failing
  pytest-fast on every worktree commit).

## Files Changed

- `scripts/core/preflight-check.sh` (modified — Gates 1/7 logic, slug validation)
- `tests/test_preflight_check.py` (modified — 14 → 24 tests)
- `tests/test_project_script.py` (modified — GIT_* isolation fixture)
- `.kit/context/reviews/KIT-0042-evaluator-review.md` (decline-table pointers)
- Task/handoff bookkeeping

## Test Results

- `pytest tests/test_preflight_check.py` — 24 passed (was 14); TDD
  red-then-green on every behavior change
- Full suite green in the worktree (403+); `./scripts/core/ci-check.sh` green
- `test_project_script.py` verified under hostile `GIT_DIR`/`GIT_INDEX_FILE`

## Automated Review Summary

- CodeRabbit: 1 thread (Gate 7 directory false-pass) — fixed `af00f52`, resolved
- BugBot: pass, no findings
- Evaluators (fast-v2 + o3): 4 accepted (at-cap PENDING + raw-count guard
  — convergent headline finding; LC_ALL=C sort; slug validation), 4
  declined with evidence. Record: `.kit/context/reviews/KIT-0043-evaluator-review.md`

## Areas for Review Focus

- The at-cap → PENDING demotion changes semantics: a legitimately
  50+-run commit can no longer PASS Gate 1 until `CI_RUN_LIMIT` is
  raised. Deliberate (honest over convenient) — confirm you agree.
- Worktree-pilot frictions are logged for KIT-0044 in the retro (5 items).

## Related ADRs

- None; lineage is KIT-0034/0040/0042 preflight hardening.

---
**Ready for human review**

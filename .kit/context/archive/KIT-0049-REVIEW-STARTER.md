# KIT-0049 Review Starter — Shape-Scoped `project sync`

**PR**: https://github.com/movito/agentive-starter-kit/pull/79
**Branch**: `feature/KIT-0049-shape-scoped-sync` (worktree: `../ask-worktrees/KIT-0049`)
**Task**: `.kit/tasks/4-in-review/KIT-0049-shape-scoped-sync.md`
**Date**: 2026-07-15
**Agent**: feature-developer-f5 (fifth worktree session)

## What shipped

Replaces the KIT-0048 refusal stopgap. **This completes P2's promise: planning repos can now update.**

| Piece | Deliverable |
|-------|-------------|
| Engine | `SyncOptions.allowlist` — candidates intersected after `--tier`/`--only`; excluded upstream entries → `SyncReport.skipped_additions` (named, never silent, NOT warnings — exit contract 0/1/2/3/4 untouched); preserved manifests **pruned of upstream-dropped entries**; `--only` outside the allowlist = UsageError; empty entitlement∩allowlist scope is **never** complete (no vacuous version bumps) |
| Wrapper | Planning shape reads its own manifest → allowlist (locked decision 1); implicit shape-read trigger via `_doctor_shape()` (locked decision 2); full `dict[str, list[str]]` schema validation with refusals (string tier, non-string member, null files, traversal/absolute entries, empty list); malformed shape still exit 2 |
| Design call | Intersection lives in the **engine** — manifest preservation happens inside `_build_new_manifest`, unreachable from the wrapper |
| v1 limitation | Planning repos receive *updates*, not *additions* — skipped additions named in every report with the re-bootstrap pointer |

## Review state

- **CI**: green. **BugBot**: pass. **CodeRabbit**: completing re-review of the final commit at handoff time.
- **Bots**: 3 threads / 3 rounds — all real, all faces of the **same masking class** (string-tier char-iteration; mixed-list silent discard; vacuous completeness on empty entitled scope).
- **Evaluators** (trio BEFORE PR): fast-v2 CONCERNS / **o3 FAIL** / claude-code CONCERNS — 7 accepted (headline: **upstream-deletion divergence** — verbatim manifest preservation froze stale records forever while core_version converged; also the `--only` silent drop, a stranded `skipif` decorator pytest silently ignored, `"files": null` AttributeError, traversal defense-in-depth), 4 declined with evidence. Disposition: `.kit/context/reviews/KIT-0049-evaluator-review.md`.
- **The pattern worth naming**: five reviewers (three evaluators + two bots) found five different faces of one design risk — *set-intersection code masks absence*. Every face is now closed with a refusal, a pruning rule, or a completeness guard, each with a test.
- **Tests**: 34 in `tests/test_project_sync.py`, incl. the single-shape characterization (additions still arrive, full manifest replaced — byte-identical) and the reduced-manifest preservation pin.

## Reviewer attention points

1. Engine + wrapper both ship via `scripts_core` — 3.2.0+ consumers receive this through `project sync` itself
2. `complete` semantics for allowlist runs are new: "everything the allowlist records within entitlement, non-vacuously" — see the engine comment block
3. o3's FAIL verdict is now 3-for-3 on real blockers across KIT-0046/0048/0049

## Post-merge planner actions

- `git worktree remove ../ask-worktrees/KIT-0049` (may need `--force` for the untracked evaluator input), `project complete KIT-0049`, branch delete
- Planning repos (none exist yet beyond scratch) can sync from the next core version
- Retro: `.kit/context/retros/KIT-0049-retro.md`

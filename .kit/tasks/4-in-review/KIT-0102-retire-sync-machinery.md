# KIT-0102: ADR-0028 phase 4 — retire the copy-sync machinery

**Status**: In Review
**Priority**: high (the final ADR-0028 step; pure deletion + record
bookkeeping — after it, the copy era has no living machinery)
**Type**: Retirement (deletion-shaped — the KIT-0067 law governs)
**Estimated Effort**: 0.5 day
**Created**: 2026-08-11
**Source**: KIT-ADR-0028 Consequences §Migration step 4; phases 1–3
annotated DONE/no-op in the ADR 2026-08-11
**Evaluation**: arch-review-fast REVISION_SUGGESTED 2026-08-11, one
finding (tiered process for trivial deletions) — DECLINED for this
task: a nine-artifact retirement with the launcher-incident history is
precisely what the full discipline exists for; the tiering idea is
NOTED as a future process tweak if trivial deletions ever demonstrate
disproportionate ceremony (no such pain observed yet). Gate passed
with disposition.

## Overview

Nothing uses the copy-sync channel anymore: new projects are born
packaged (phase 2), the only live consumer is packaged-shape (phase 3
closed no-op), and the push half never ran in production
(CROSS_REPO_TOKEN was never provisioned — archived KIT-0045). What
remains is machinery whose only remaining function is to confuse a
future reader into thinking the copy era is alive. Delete it with the
full function-enumeration discipline — this repo once deleted a
launcher by directory-shaped reasoning (KIT-0067) and once found drift
running BACKWARD through a stale copy (KIT-0096); the enumeration
table is how neither recurs.

## Inventory (verified present 2026-08-11 — re-verify at start)

| Artifact | Expected verdict (confirm by enumeration) |
|---|---|
| `.github/workflows/sync-core-scripts.yml` | delete (push channel; never ran — no token) |
| `scripts/core/sync_from_manifest.py` | delete (pull engine, ADR-0026) |
| `scripts/.core-manifest.json` | delete (the manifest itself) |
| `tests/test_sync_from_manifest.py` + `tests/test_core_manifest.py` | delete WITH their subjects (nothing tests deleted code) |
| `scripts/core/doctor.d/60-push-sync-token.sh` | delete (checks a token for a deleted workflow) |
| `scripts/core/doctor.d/40-version-skew.py` + `scripts/core/VERSION` | ENUMERATE carefully — if their only function is manifest-skew detection, they die together; any second function gets named and preserved |
| `project sync` subcommand | remove from the shim AND the package if ported (enumerate both homes); its help text and any docs naming it |
| `KIT-ADR-0026` (pull-based consumer sync) | mark **Superseded by KIT-ADR-0028** (its own header anticipated this) |
| Docs sweep | UPDATING-YOUR-PROJECT, README, CROSS-REPO-PATTERN, workflows/ — zero live references to sync/manifest as a current mechanism (historical mentions in retros/ADRs/archives stay) |

## Requirements

- **F1 — the enumeration table in the PR body**: one row per deleted
  artifact — its FUNCTIONS, where each function went (packaged /
  obsolete / preserved-elsewhere), and the grep proving no live
  caller. Deletion without enumeration is the incident class, not a
  shortcut.
- **F2 — both-directions check before deleting the manifest** (the
  KIT-0096 lesson): confirm no copy under manifest management is
  NEWER than its kit source (a backward-drift catch would mean canon
  regressed — fix canon first, then delete).
- **F3 — records**: ADR-0026 header → Superseded; ADR-0028 migration
  step 4 → DONE with this task's PR linked.
- **F4 — nothing else moves**: not the remaining shell scripts
  (check-bots/wait-for-bots/verify-ci/ci-check — live, non-sync), not
  the `project` shim beyond its `sync` subcommand, not
  `new-worktree.sh`, not the drift guard (which is the packaged era's
  OWN sync check and stays).

## Acceptance Criteria

- [ ] All inventory rows resolved per their enumeration verdicts;
      table + greps in the PR body
- [ ] F2 both-directions check recorded (clean, or canon fixed first)
- [ ] Full suite green (deleted tests excepted by deletion); scaffold
      acceptance green; drift guard untouched and green
- [ ] ADR-0026 Superseded; ADR-0028 step 4 marked DONE
- [ ] Repo-wide grep: zero live references to the manifest/sync as a
      current mechanism (historical records exempt, listed)

## Out of Scope

- The `project` shim's continued existence (kit-internal tooling; its
  fate is a later housekeeping call, not phase 4)
- `ev-fast-charging-loads-planning_old/` (operator's archive, not
  ours to touch)
- KIT-ADR-0029 (its trigger fires AFTER this lands — do not start it)

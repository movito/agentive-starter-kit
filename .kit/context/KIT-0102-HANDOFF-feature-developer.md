# KIT-0102: Retire the copy-sync machinery (ADR-0028 phase 4) — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-08-11
**From**: planner-f5
**To**: feature-developer
**Task**: `.kit/tasks/4-in-review/KIT-0102-retire-sync-machinery.md`
**Status**: Ready — the final ADR-0028 step; the spec's inventory table
IS the work list
**Evaluation**: gate passed with one dispositioned finding (spec
header) — don't re-litigate the tiering suggestion

**Target Codebase**: This repo (agentive-starter-kit) — single-repo
mode (the repo split, not your working directory).

## Session topology (read before anything else)

- Worktree: `~/Github/ask-worktrees/KIT-0102`, branch
  `feature/KIT-0102-retire-sync-machinery` — created and provisioned
  by the planner; VERIFY (`git branch --show-current`), never create;
  wrong branch → STOP and ask
- ONE PR expected (deletions + record edits). The Plugin Drift Guard
  is UNAFFECTED by design (you touch no roster-shipped `.claude/`
  content) — if it goes red on your PR, something is wrong with your
  diff, not the guard: stop and investigate.

## Mission

Delete the copy-era machinery with full enumeration discipline. This
is a DELETION task in the repo that once deleted its operator's daily
launcher by directory-shaped reasoning (KIT-0067) and once found
drift running backward through a stale copy (KIT-0096) — the spec's F1
enumeration table and F2 both-directions check are the two incidents
turned into method. The spec's inventory is authoritative.

## Anchors and cautions (2026-08-11 — re-verify at start)

- **`project sync` lives in two possible homes** — the
  `scripts/core/project` shim's dispatch AND possibly the agentive-kit
  package (`packages/agentive-kit/src/agentive_kit/`): grep both for
  `sync`/`sync_from_manifest`; remove the subcommand wherever it
  exists, plus its help lines. The package change, if any, does NOT
  need a release by itself — note it for the next release train
  instead (0.3.2/0.4 whenever one runs); the kit runs on in-tree
  source and consumers born packaged never had the subcommand's
  manifest to sync.
- **`40-version-skew.py` + `scripts/core/VERSION`** — the enumeration
  judgment call the spec flags: read both fully; if skew-detection
  against the manifest is their ONLY function, they die with it; any
  second function (e.g. a version surface something else reads —
  grep for readers of `scripts/core/VERSION`) gets named and either
  preserved or explicitly retired with its own row.
- **F2 both-directions check, concretely**: for every file the
  manifest manages, `diff` the manifest-managed copy's source against
  kit canon — the manifest lists its file set; a copy NEWER than
  canon means canon regressed (the KIT-0096 class): fix canon FIRST
  in the same PR, then delete. Record "clean" or the fixes in the PR
  body.
- **Docs sweep scope**: live docs only (README,
  UPDATING-YOUR-PROJECT, CROSS-REPO-PATTERN, `.kit/context/
  workflows/`) — retros, ADRs (except the two record edits), archived
  tasks, and CHANGELOG history keep their sync mentions as historical
  record; list the exempted files in the PR rather than sweeping them.
- **Record edits**: KIT-ADR-0026 header gains `Superseded by
  KIT-ADR-0028 (2026-08-11, KIT-0102)`; KIT-ADR-0028 migration step 4
  → DONE with the PR linked.
- **Doctor driver**: deleting `60-push-sync-token.sh` (and possibly
  `40-version-skew.py`) changes the check roster — confirm the doctor
  driver and any test asserting check counts/names still pass;
  `tests/test_doctor.py` may pin the set.

## Test approach

- Full suite green with the deleted tests gone (delete
  `test_sync_from_manifest.py`/`test_core_manifest.py` in the SAME
  commit as their subjects — nothing tests deleted code, the KIT-0092
  Part C rule); scaffold acceptance green; drift guard green and
  untouched.
- Repo-wide class greps quoted in the PR: `core-manifest`,
  `sync_from_manifest`, `sync-core-scripts`, `push-sync` — zero live
  hits outside the exempted historical list.
- Evaluator: this is deletion + records — mostly not prose, not
  logic. Fast tier, `--format diff`; a skip is defensible if the diff
  is pure deletion — decide and record either way.

## Out of scope — do not touch

- The `project` shim beyond its `sync` subcommand; the live shell
  scripts (check-bots, wait-for-bots, verify-ci, ci-check);
  `new-worktree.sh`; the drift guard and roster (the packaged era's
  own sync — they STAY)
- `ev-fast-charging-loads-planning_old/` (operator's archive)
- KIT-ADR-0029 work (its trigger fires after you merge — the planner
  handles that)

---

**Task File**: `.kit/tasks/4-in-review/KIT-0102-retire-sync-machinery.md`
**Records to edit**: `.kit/adr/KIT-ADR-0026-*.md`, `.kit/adr/KIT-ADR-0028-*.md`
**The two governing incidents**: KIT-0067 (function enumeration), KIT-0096 (both-directions drift)

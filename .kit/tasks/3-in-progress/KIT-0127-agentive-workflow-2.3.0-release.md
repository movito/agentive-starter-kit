# KIT-0127: agentive-workflow 2.3.0 release — pin refresh resync + retire feature-developer-o55

**Status**: In Progress
**Priority**: high
**Created**: 2026-11-10
**Assigned**: feature-developer
**Estimated**: 2–3h (1h resync+roster, 0.5h versions/CHANGELOG, 0.5–1h PR/bots/merge/guard)

## Mission

Propagate kit commit `7f3784c` ("model-rollout pin refresh + retire
feature-developer-o55") into the `agentive-skills` marketplace as plugin
release **2.3.0**, so consumers pick up the new model pins and the
retired agent disappears from the roster.

## Why 2.3.0, not 2.2.1

The kit commit message says "semver-patch" — that refers to the **agent
frontmatter** bumps (e.g. planner 2.3.0 → 2.3.1, pin-only per
MANIFEST-UPGRADE-GUIDE). The **plugin** version is governed by the
release protocol: retiring `feature-developer-o55` is a roster
**membership change**, and membership change ⇒ minor bump (same rule
that made the o55 *addition* 2.1.1 → 2.2.0 in KIT-0124). Hence 2.3.0.

## Verified current state (planner, 2026-11-10)

All claims below verified live this morning; commands shown.

- **Kit source (this repo, `main`)**: `git show --stat 7f3784c` — new
  pins planner/feature-developer → `claude-opus-5-5`, both -f5 variants
  → `claude-fable-5-2`; `feature-developer-o55.md` deleted (840 lines);
  frontmatter versions bumped by upgrader (e.g. planner 2.3.0→2.3.1).
- **Marketplace (`~/Github/agentive-skills`)**: `origin/main` = local
  `main` = `280562c` (2.2.0, skills#13 squash). Clone put on `main` and
  fast-forwarded by planner 2026-11-10; working tree clean. Stale local
  branch `release/agentive-workflow-2.2.0` (merged) still exists — leave
  unless operator says delete.
- **Drift set** (`.venv/bin/python scripts/local/check_plugin_drift.py`):
  exactly 5 findings — feature-developer, feature-developer-f5, planner,
  planner-f5 (content newer than rostered), feature-developer-o55
  (rostered source missing from kit). Nothing else drifted.
- **Resync blocker** (`plugin_resync.py --dry-run`): exits 3 on
  `feature-developer-o55: rostered source … missing from the kit` —
  roster surgery must precede the resync run.
- **o55 roster entry**: roster.yaml lines 68–76 (`ships: true`,
  kit_version "1.0.0", both hash columns present).
- **Stale version field**: roster.yaml line 47 reads
  `plugin_version: "2.1.1"` — 2.2.0 shipped without bumping it (fourth
  version-column incident; KIT-0111 evidence). Fix in passing.
- **Version surfaces at 2.2.0** (grep): `.claude-plugin/marketplace.json`
  lines 9+16, `plugins/agentive-workflow/.claude-plugin/plugin.json`
  line 4, `README.md` line 14, CHANGELOG.md. Roster line 47 stale at 2.1.1.
- **Component count**: `grep -c "ships: true" roster.yaml` → 30 now;
  29 after o55 retires.

## Acceptance criteria

- [ ] Roster surgery: o55 entry → `ships: false`, `retired: true`,
      `source`/`kit_version`/hash columns removed, `why` updated
      ("retired in 2.3.0 — pilot concluded; canonical feature-developer
      now carries the opus-5-5 pin it piloted, KIT-0127"). Follow the
      v6/v7 retired-entry pattern (roster lines ~187–191).
- [ ] `plugins/agentive-workflow/agents/feature-developer-o55.md` deleted.
- [ ] `plugin_resync.py` run (kit venv) refreshes the 4 pin-changed
      agents into the plugin + both hash columns; `--dry-run` first,
      work-list must show exactly those 4.
- [ ] Version 2.3.0 in ALL fields: marketplace.json ×2, plugin.json,
      roster `plugin_version` (currently stale "2.1.1" — note the
      correction in the PR body), README.
- [ ] CHANGELOG.md 2.3.0 entry, explicit empty categories; notes the
      roster version-field correction and the membership change.
- [ ] Kit-side drift guard measured GREEN after merge via **explicit
      dispatch** on kit main (it does NOT re-run at marketplace merge —
      KIT-0113 stale-red/stale-green trap).
- [ ] PR to `movito/agentive-skills` merged with CI green; bot budget
      ONE substantive round.
- [ ] Operator handed the two consumer update commands
      (`claude plugin marketplace update agentive-skills`,
      `claude plugin update agentive-workflow@agentive-skills`).

## Evaluation

Skipped (planner ruling): mechanical release following the established
KIT-0124/KIT-0113 recipe; no architectural decisions. Version ruling
documented above in lieu.

## Out of scope

- Any kit-repo commits (kit is read-only for this session; planner owns
  kit-side bookkeeping)
- KIT-0111 (version-bump guard) implementation — this task only adds a
  fourth evidence point
- Deleting the merged 2.2.0 local branch (operator's call)
- Consumer project upgrades (ixda pair, DTL) — separate follow-ups

## PR Plan

Single PR in `movito/agentive-skills` on branch
`release/agentive-workflow-2.3.0` (created by planner at authoring
time). Diff is roster + 4 agent bodies + 1 deletion + version fields +
CHANGELOG — well under size limits.

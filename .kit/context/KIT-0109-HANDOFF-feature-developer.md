# KIT-0109: Plugin release 2.0.4 — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not
delegate or spawn other agents.**

**Date**: 2026-08-14
**From**: planner-f5  **To**: feature-developer
**Task**: .kit/tasks/3-in-progress/KIT-0109-release-plugin-content-refresh.md
**Status**: Ready
**Evaluation**: skipped (planner) — mechanical release, twice-run
precedent (KIT-0096 → 2.0.0, KIT-0099 → 2.0.1); the KIT-0099 spec in
`5-done/` is the annotated checklist
**Target Codebase**: `~/Github/agentive-skills` (the marketplace repo)
— the kit repo is READ-ONLY source canon for this task

## Session topology (read before anything else)

- **Repo**: `/Users/broadcaster_three/Github/agentive-skills` — a
  plain clone, no worktree infrastructure; the session runs there
- **Branch**: `release/agentive-workflow-2.0.4` — planner-created off
  its `origin/main` (`5e63707`), upstream set. **Verify, never
  create**; wrong branch → STOP and ask
- **Source canon**: `/Users/broadcaster_three/Github/agentive-starter-kit`
  on `main` at `1cb8c52` or later — read from it, never commit to it
  in this session; kit-side findings are FILED (see the escape hatch
  below), not fixed here
- Single PR to the marketplace repo's `main`; the operator merges

## Mission

Resync the 20-component drift set from kit canon into
`plugins/agentive-workflow/`, bump to 2.0.4, green the drift guard.
The spec's R1–R5 are authoritative. Environmental facts verified
today (2026-08-14, planner):

- Published plugin version: **2.0.3** (`plugin.json:4`) — expected
  bump is patch → 2.0.4 (membership-identical resync, the 2.0.1
  precedent). If the roster header's versioning rule says otherwise,
  the roster wins; say so in the PR.
- Drift output (kit main `1cb8c52`, run 2026-08-14): 20 components —
  10 agents / 5 commands / 5 skills, enumerated in the spec. RE-RUN
  at session start; the guard's hash-derived list is the work list
  (never `git diff` — KIT-0099 method note).
- **Bots on this repo: CodeRabbit VERIFIED present** (reviewed
  agentive-skills#4 and #5 — KIT-0099's record; the KIT-0096 handoff
  lesson about asserting bot absence unverified is why this line
  cites PRs, not memory). BugBot presence there: UNVERIFIED — plan
  for CodeRabbit at minimum.

## Kit-side escape hatch

You are outside the kit's task tree by role, not by path — the kit
clone is on this machine. Canonical-content findings from bot rounds
go in ONE follow-ups file:
`.kit/context/KIT-0109-KIT-FOLLOWUPS.md` (KIT-0099 precedent),
committed by the PLANNER after your report — hand the list over, do
not commit to the kit repo yourself.

## Test approach

- The transform is verified by the guard itself: after the release
  merges, `gh run` the Plugin Drift Guard on kit main
  (`gh --repo movito/agentive-starter-kit workflow run` … `--ref
  main`) and cite the green run.
- Local install proof: `claude plugin marketplace update
  agentive-skills` then `claude plugin update
  agentive-workflow@agentive-skills`; quote `claude plugin list`.
- roster.yaml hash consistency: re-run `check_plugin_drift.py` from
  the kit clone — zero findings is the acceptance state.

## Out of scope — do not touch

- KIT-0105 / KIT-0103 R1 content (their own train, next release)
- Any plugin-side patch of canonical content (KIT-0097 contract —
  file it instead)
- The kit repo's tree, in any way

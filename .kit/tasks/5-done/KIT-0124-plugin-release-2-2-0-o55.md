# KIT-0124: agentive-workflow 2.2.0 — ship feature-developer-o55 + full resync

**Status**: Done
**Priority**: medium
**Type**: Plugin release (movito/agentive-skills)
**Estimated Effort**: ~1-2 h
**Created**: 2026-10-18
**Source**: Operator request from an ixda-services session — run
`feature-developer` on Opus 5.5 in consuming projects. The kit already
carries `feature-developer-o55` (v1.0.0, f4e54fa); it has never shipped.

## Context

`check_plugin_drift.py` against the published 2.1.1 roster reports 12
findings: 10 shipped components whose kit content is newer than the
release (`feature-developer`, `feature-developer-f5`, `planner`,
`planner-f5`, `code-reviewer`, `document-reviewer`,
`security-reviewer`, `commit-push-pr`, `preflight`, `review-handoff`)
and 2 unrostered agents (`feature-developer-o55`,
`architecture-reviewer`). Shipping o55 alone would publish it with a
newer workflow (fork of feature-developer 2.8.0) than the default
agent it sits beside (2.6.0 published), so the release is a full
refresh from the kit tree.

## Scope

- R1 — Resync the 10 drifted components with
  `scripts/local/plugin_resync.py` (three-way merge; conflicts resolved
  by hand, preserving KIT-ADR-0025 generalization).
- R2 — Add `feature-developer-o55` as a shipped agent (namespacing
  transform applied; separate file because the `model:` pin is
  frontmatter, KIT-ADR-0025 §3).
- R3 — Add `architecture-reviewer` as a shipped agent (operator
  decision, 2026-10-18).
- R4 — Roster entries + hashes, CHANGELOG (explicit Added), version
  2.1.1 → 2.2.0 in `plugin.json` + `marketplace.json`, README roster.

## Acceptance

- [x] `check_plugin_drift.py --roster-file <marketplace roster>` exits 0
      (and against the live roster after merge: 30 in sync)
- [x] `verify_plugin_integrity.py` exits 0 in agentive-skills (30 bodies)
- [x] markdownlint clean on changed bodies (0 issues, 33 files)
- [x] No un-namespaced `/command` references added (`wrap-up.md:10`
      predates 2.2.0)
- [x] Release PR movito/agentive-skills#13 merged 2026-10-18. Bot
      finding (preflight Gate 8 split-mode path) deferred to KIT-0126;
      wait-for-bots wrong-repo bug found during babysit filed as KIT-0125

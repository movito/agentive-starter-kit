# KIT-0101: The cold-start UX contract — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-08-11
**From**: planner-f5
**To**: feature-developer (f5 variant recommended — design judgment
across many surfaces, journey-shaped acceptance)
**Task**: `.kit/tasks/3-in-progress/KIT-0101-cold-start-ux-contract.md`
**Status**: Ready — every requirement operator-reported from live use
this week; ships as plugin 2.0.3
**Evaluation**: gate passed with three DECLINED-as-designed
dispositions — the record is in the spec header; don't re-litigate

**Target Codebase**: This repo (agentive-starter-kit) — single-repo
mode (the repo split, not your working directory).

## Session topology (read before anything else)

- Worktree: `~/Github/ask-worktrees/KIT-0101`, branch
  `feature/KIT-0101-cold-start-ux-contract` — created and provisioned
  by the planner; VERIFY (`git branch --show-current`), never create;
  wrong branch → STOP and ask
- **Plan for TWO PRs** (stacked or sequential): PR 1 = R1–R4 (the
  journey UX), PR 2 = R5 (the starter authority). Each must hold the
  ~500-prose-line budget independently; if either can't, STOP and
  report for a further split (R5 is the designated split-out). Drift
  guard red-by-design on both once `.claude/` changes; green at 2.0.3.

## Mission

Make the cold-start journey structurally honest: commands explain
themselves before acting (R1), session hops are collapsed or reasoned
(R2), completion is one verified checklist ending in one command (R3),
the journey replay proves it (R4), and task starters get a single
example-bearing authority (R5). Spec R1–R5 authoritative; KIT-0100's
spec carries the F7/F9/F10 source texts (operator-authored — the
format mock in F10 is the operator's own design; implement it, don't
redesign it).

## Verified anchors (2026-08-11 — re-grep before relying)

- **R1 sweep set**: `.claude/commands/` holds 14 files; all are
  user-invocable slash commands (skills with `user-invocable: false`
  are out of scope). `setup-preset.md` and `new-project.md` are
  kit-side (not in the plugin roster); the other 12 ship — the header
  pattern must read correctly in BOTH homes (a plugin copy's "source"
  link points at the marketplace file or the kit canonical — decide
  once, record why; the namespacing transform applies on release).
- **R2 primary surface**: `new-project.md` (the flow that sent the
  operator to a fresh intake session with no why) +
  `project-intake.md` Step 5's "Next action". The dead rationale
  (launcher-era persona fragility) must not be cited — per-session
  agent identity and fresh-context-for-a-different-contract are the
  two live reasons.
- **R3 surfaces**: `project-intake.md` Step 5 (the checklist per the
  operator's F10 format — every ✓ verified at print time, ✗ inline
  with remedies, ONE closing command carrying the opening prompt,
  printed ONLY when doctor has no FAILs) AND
  `scripts/local/bootstrap`'s tail (elevate a missing `agentive` CLI
  to the headline next step). The door is SHELL: the bash-3.2
  heredoc-apostrophe rule (patterns.yml) and the plain-scalar
  colon-space YAML trap do not apply here but portability does — no
  Homebrew-only tools. **Contract strings**: the door tail is pinned
  by `tests/test_scaffold_acceptance.py` ("Install the agent
  plugin:", "agentive CLI:" families) — changed wording updates the
  pins in the same commit, per that test's own header.
- **R5 surfaces**: `.kit/templates/TASK-STARTER-TEMPLATE.md` (385
  lines today — expect a substantial rework: required core, house
  improvements, TWO worked examples, proportionality rule) +
  planner.md/planner-f5.md Phase 5 (replace the inline section list
  with a pointer to the template). **Contract-test caution**:
  `tests/test_agent_contracts.py` pins planner sentinels ("Session
  topology (REQUIRED)", "never `checkout -b`", "Rename the session
  to") — if Phase 5's rework moves any pinned text into the template,
  update the pins in the same commit; the pair-identity test also
  applies to every planner/feature-developer edit.
- **R4**: the journey = /setup-preset → /new-project → intake →
  first planner session. The 2026-08-11 friction points to replay
  against: silent agent starts, the unexplained new-session hop, the
  contradictory ending (intake said plan, terminal said install).
  Record the replay as a step log in the PR body.

## Test approach

- Full suite per push; contract tests green throughout (pins updated
  in-commit where wording legitimately moves).
- Evaluator: fast-tier-only, `--format diff` (prose-shaped) — per the
  policy this journey's own findings helped write.
- Every sweep grep-verified at end state (R1's header presence across
  all 14; R2's zero bare "open a new session with X"); quoted in the
  PR body.
- Circuit breaker + budget are live constraints, not suggestions.

## Out of scope — do not touch

- KIT-0074/0085/0094/0095 (backlog); phase 3/4 surfaces; sync
  machinery; `agentive-kit` package code (R3's door work is
  scripts/local shell, not the package)
- Redesigning the operator's F10 checklist format (implement as
  specified; friction with it goes back to the planner, not into
  silent variation)

## Release

2.0.3 per the standing recipe (KIT-0099/0100 precedent): refresh
changed shipped files (12 commands + any agent/skill edits) into the
marketplace clone, namespacing transform per its README §Maintenance,
roster hashes, version bumps, CHANGELOG by family; post-merge: drift
guard green (run URL), `claude plugin update
agentive-workflow@agentive-skills` lands 2.0.3, both cited.

---

**Task File**: `.kit/tasks/3-in-progress/KIT-0101-cold-start-ux-contract.md`
**Source texts**: KIT-0100 spec §F7/F9/F10 (operator-authored; the
F10 format block is the design — implement verbatim)
**Release recipe**: agentive-skills README §Maintenance

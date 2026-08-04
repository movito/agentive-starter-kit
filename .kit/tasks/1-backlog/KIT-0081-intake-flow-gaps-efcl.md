# KIT-0081: Intake/door gaps surfaced by the ev-fast-charging-loads intake

**Status**: Backlog
**Priority**: medium
**Created**: 2026-08-04

## Overview

A live run of the project-intake flow (prototype → split pair for
`ev-fast-charging-loads`, 2026-08-04) surfaced several independent small
gaps. None blocked the intake — each was worked around by hand — but each
would confuse an operator or a following agent. The big one from the same
session (Apple git 2.30.1 breaking preset resolution) is S3 on KIT-0080,
not here.

## Findings

- **F1 — door tail prints stale next-steps despite flags.** With
  `--target-path`/`--target-github` given, the door correctly writes the
  `## Target Repository` section and the kit-install region, yet its
  next-steps tail still says "Fill in the target-repo pointer (path +
  github) in CLAUDE.md". An operator who follows the printed instructions
  concludes the install is incomplete. The tail should reflect what was
  actually resolved (say "verify", or omit the line when flags filled it).

- **F2 — planning scaffold omits files the seeded planner references.**
  `agent-handoffs.json` is absent from `.kit/context/` (planner reads and
  updates it from Phase 1 on), and `.kit/tasks/9-reference/templates/
  task-template.md` (planner Phase 2's task template) does not exist —
  the scaffold creates task folders 1–7 only. Either ship both in the
  planning scaffold or remove the references from the seeded agents.

- **F3 — intake doesn't guard `init.defaultBranch`.** On a machine without
  `init.defaultBranch=main`, the code repo's first push lands on `master`
  (happened live; fixed by branch rename + default-branch PATCH + deleting
  remote master). The project-intake agent spec (Step 2) should require
  `git init -b main` (git ≥ 2.28) and a branch check before push.

- **F4 — evaluator installer tail names the wrong Gemini key.** The
  install-evaluators tail says `GOOGLE_API_KEY - Gemini evaluators`, but
  the kit standard everywhere else (`.env.template:110`,
  `doctor.d/20-env-keys.py:31`) is `GEMINI_API_KEY`.

- **F5 — planning-shape `new-worktree.sh` mismatches split-mode use.** The
  scaffold ships `scripts/local/new-worktree.sh`, which (a) resolves the
  primary clone from its own location, so in a planning repo it worktrees
  the PLANNING repo while split-mode implementation happens in the target
  repo, and (b) hardcodes the `../ask-worktrees` parent. Decide what a
  worktree session means in split mode (target-repo worktree? drop the
  script from the planning scaffold?) and document it in
  WORKTREE-WORKFLOW.md.

- **F6 — no supported rename path for an installed pair.** A mid-intake
  project rename (varv-playground → ev-fast-charging-loads) required
  hand-editing the kit-install region (`target_path`/`target_github`),
  which the consumer engine nominally owns exclusively. Either bless a
  `bootstrap --retarget`/`project retarget` mechanism or document that
  hand-editing the region is the sanctioned rename procedure.

- **F7 — placeholder project-context says `Topology: single-repo` in a
  planning-shape scaffold.** `kit_markers.py`'s placeholder body is
  shape-blind; a planning-shape install knows its topology is a split pair
  and could seed that line correctly even before the intake agent fills
  the region.

## Acceptance Criteria

- [ ] Each finding above either fixed or explicitly declined with a note
      here; F1–F4 are small and should just be fixed
- [ ] A planning-shape `--new` run followed by the seeded planner's Phase 1
      triage works with no dangling file references (F2 verified)

## Evidence

Live intake session 2026-08-04 (planner-f5, agentive-starter-kit checkout);
resulting pair: `~/Github/ev-fast-charging-loads` +
`~/Github/ev-fast-charging-loads-planning`.

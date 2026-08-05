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

- **F2 — planning scaffold omits files the seeded agents reference.**
  Verified by grepping every `docs/…`/`.kit/…` path out of the seeded
  `planner.md` + `feature-developer.md` and testing existence. Missing:
  `.kit/context/agent-handoffs.json` (planner reads it from Phase 1 on),
  `.kit/tasks/9-reference/templates/task-template.md` (Phase 2's task
  template — the scaffold creates task folders 1–7 only),
  `docs/CROSS-REPO-PATTERN.md` (the doc the planner routes every git
  operation by — a split-pair scaffold shipping without the split-pair
  pattern doc is the worst of these), `.kit/adr/KIT-ADR-0019-…` (Phase 7
  knowledge extraction), `.kit/context/REVIEW-INSIGHTS.md`, and
  `docs/MANIFEST-UPGRADE-GUIDE.md` (frontmatter model-pin note). Ship
  them in the planning scaffold or trim the references from the seeded
  agents. (All but the last were backfilled by hand into
  ev-fast-charging-loads-planning, commit "chore: backfill scaffold
  gaps"; use it as the reference for what a usable planning repo needed.)

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

- **F8 — a fresh planning repo LOOKS empty to the operator.** Everything
  the scaffold ships lives in dot-folders (`.claude/`, `.kit/`,
  `.adversarial/`); the only Finder-visible contents are `CLAUDE.md` and
  `scripts/`. The operator's actual reaction (2026-08-04): "what I have
  is barely anything — no .claude folder with agents, no .kit folder" —
  for a repo of 219 files. Ship a README.md in the planning scaffold
  that says what the repo is and maps the hidden folders (the backfilled
  README in ev-fast-charging-loads-planning is a working draft). Earlier
  single-shape ASK exports shipped a README + docs/ and did not have
  this failure mode.

- **F9 — door exports HEAD, silently dropping uncommitted kit changes**
  (folded in from KIT-0064, 2026-08-04 backlog review; original evidence
  KIT-0058 retro Surprising #1). `bootstrap --new` exports via
  `git archive`, which ships HEAD — not the working tree. On KIT-0058
  the exported target's `doctor.d/` silently lacked an uncommitted
  check file (9 checks instead of 10). Fix: when the kit tree has
  uncommitted TRACKED changes (`git status --porcelain`), print a
  one-line notice "kit tree has uncommitted changes — the export ships
  the last commit (HEAD)". Notice only, never a block; exit codes
  unchanged. Test both directions in `tests/test_setup_door.py`. Not a
  doctor.d candidate — the condition lives in the source tree at export
  time, not the installed environment.

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

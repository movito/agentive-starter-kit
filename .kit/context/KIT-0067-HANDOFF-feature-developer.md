# KIT-0067 Handoff — feature-developer

**Task**: `.kit/tasks/3-in-progress/KIT-0067-factory-front-door-and-structural-cleanup.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-27 (planner-f5)
**Estimated effort**: 1-1.5 days

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0067/`** — branch
`feature/KIT-0067-factory-front-door-and-structural-cleanup`. Run
`git pull --ff-only` first. Absolute paths / `git -C` throughout.
Your `.venv` is a REAL per-worktree venv (Python 3.14 — first
worktree provisioned by KIT-0071's fixed helper). Serena: activate
by ABSOLUTE worktree path only.

## Mission

Ship the factory front door and retire what it supersedes. Two
halves: (1) make the operator flow teachable — STARTING-A-PROJECT
doc, /new-project command, seeded self-direction line; (2) execute
the five APPROVED structural decisions D1-D5 (launcher/onboarding
retirement, dead-doc archival, serena prune, dispatch gating, adr
ownership). This is the LAST task before cutting 0.9.0.

## Decisions are SETTLED — read them as instructions

D1-D5 were operator-approved 2026-07-24 (recorded in the spec).
Don't re-litigate; the only open verification inside D1 is whether
`.kit/launchers/preflight` is a thin wrapper over preflight-check.sh
(keep if thin, retire if duplicating).

## Jointly-owned files (planner footgun — expect these seams)

The audit split by A-number, so several of your files were already
partially touched by merged tasks:

- `COVERAGE-WORKFLOW.md`: KIT-0069 fixed its ghost pointer (A42);
  YOU own the full thematic_cuts/53% rewrite (A41 → D2: fresh
  minimal replacement, 80% rule + the two real commands).
- `EVALUATION-WORKFLOW.md`: KIT-0065 fixed its aider refs, KIT-0069
  fixed its version pin + verdict-vocabulary text (incl. the
  per-evaluator variant table — PRESERVE that table); YOU own the
  archive-vs-rewrite disposition (A68 → D2).
- `security-reviewer.md`, launchers' printed text: KIT-0069 fixed
  prose instances; YOUR retirement/archival supersedes — deletion
  wins over polish.

## Verified facts (planner; re-verify anchors)

- Audit evidence: `.kit/context/reviews/PRE-090-CRUFT-AUDIT-2026-07-24.md`
  — your set: A18, A33, A41, A44, A45, A50, A61, A62, A68, A85-A87,
  A89, A90 (+ the launchers-vs-door uncertain finding). Disposition
  each in the PR body.
- `/setup-preset` (`.claude/commands/setup-preset.md`) is the
  command style F2 copies: derive-at-runtime from `bootstrap --help`,
  one question at a time, stop-and-say-so on gaps, help-output-wins.
- The seeded CLAUDE.md lives in engine-consumer.sh's KIT-LOCAL
  seeding (F3 is a seed-TEXT change; grep the heredoc/template that
  writes it — self-review item 14: check EVERY seeding path).
- `docs/STARTING-A-PROJECT.md` content sources: the factory model
  (one clone + siblings diagram), three flows (project-intake w/
  PROTOTYPE-HANDOFF-TEMPLATE; blank pair; single), tab-handoff
  convention (LAUNCH lines are navigation), first-session
  self-direction. The operator's preset resolves most door answers —
  say so.
- Serena (D3): verify the CURRENT serena version's project.yml
  schema before fixing the template key (self-review item 10 — run
  or read the installed serena, not memory).

## Context you must not lose

- **displayed_commands_are_contracts** (patterns.yml, fresh from
  KIT-0071): /new-project and STARTING-A-PROJECT will PRINT many
  commands — every one complete, root-scoped, quoted, note-as-
  comment; when a bot flags one, sweep the class in ONE round
  (KIT-0071 paid four extra rounds for instance-by-instance).
- **Execute every remedy you document** (item 16): each command in
  the doc/command gets run once or traced to its dispatch before
  the diff closes.
- **Archival mechanics (D2)**: `git mv` to `docs/archive/`,
  repoint or drop every citing link (grep evidence in PR), tombstone
  only where live surfaces linked. Coordinate: KIT-0069 already
  fixed pointer-level citations — your grep list should be short.
- **Deletion set (D1/D3)**: launchers (except possibly preflight),
  onboarding agent, Desktop-era serena scripts/guides with hardcoded
  operator paths. Deletions need the citing-link sweep too.
- **BugBot status carries no signal either direction** (KIT-0071):
  always fetch threads; don't read the check-run status as done/
  skipped.
- Core scripts NOT touched unless doctor/seed text changes →
  if any `scripts/core/` file changes, VERSION 3.8.0→3.9.0 +
  manifests in the same commit.
- `/new-project` and STARTING-A-PROJECT must NOT hardcode the
  shape×profile matrix (door-owned; derive or cite `bootstrap
  --help`).

## Test approach

- Ordering rule: local tests green → evaluator trio → PR open.
  Mixed code+doc diff → normal trio ordering (NOT the prose-sweep
  exception), but doc-heavy: expect the Gates 2/3 docs-only wording
  divergence (known, KIT-0062 F7).
- /new-project: transcript of BOTH routes (intake + blank pair) in
  the PR; the blank-pair route may use `--no-preset` + scratch dirs
  (mktemp -d; list leftovers).
- Retirement proofs: repo-wide grep shows no live surface cites a
  deleted/archived path (paste in PR).
- `pytest` directly; `./scripts/core/ci-check.sh` before pushing.

## Evaluation summary

`arch-review-fast`: REVISION_SUGGESTED — machine-readable-interface
family DECLINED (premise error: agent-read command, ADR-0025
runtime-read; same design validated in /setup-preset), two hardening
notes accepted into F2 (public-surfaces-only; stop-and-say-so).
D1-D5 operator-approved. Disposition in the task file; log:
`.adversarial/logs/KIT-0067-factory-front-door-and-structural-cleanup--arch-review-fast.md`.
No outstanding blockers.

## Out of scope

- Door/engine logic changes; the 0.9.0 removals themselves
  (KIT-0047/0054/0059 — next task); KIT-0062's gate fixes;
  downstream repos.

## PR sizing

Likely 2 PRs: (1) front door (doc + command + seed line),
(2) retirements/archival/serena/dispatch/adr. Stacked or sequential
— your call, recorded. Lead-task naming if bundled.

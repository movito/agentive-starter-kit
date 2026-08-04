# KIT-0084: New projects start with a working .env — seeded, filled, operator-consented

**Status**: Todo
**Priority**: high (blocks the first evaluation in every fresh project; agents cannot self-serve the fix)
**Type**: Infrastructure
**Estimated Effort**: 3-5 h
**Created**: 2026-08-04
**Source**: GitHub issue #104 (operator-filed, fresh consumer project 2026-08-04)
**Evaluation**: arch-review-fast APPROVED 2026-08-04, first pass. Log: `.adversarial/logs/KIT-0084-working-env-from-day-one--arch-review-fast.md`

## Overview

A fresh project ships `.env.template` only. The doctor detects the gap
(`DOCTOR:env-keys:FAIL:.env not found — copy .env.template and fill in
keys` — observed live 2026-08-04) but nothing in the startup flow creates
the file, so the planner's Phase 3 evaluation gate is blocked on the very
first task that needs it.

Two field facts that shape the fix:

1. **Agents cannot self-serve it.** An agent attempt to copy keys from
   the kit checkout into the new project's `.env` was blocked by the
   Claude Code permission classifier (secrets handling — correctly). Key
   material provisioning MUST be an explicit operator-driven step; no
   agent-side fallback exists or should exist.
2. **A mechanism for this already exists and was silently defeated.** The
   operator preset's `env-source` key (`bootstrap` help: "names an
   operator-owned .env template (chmod 600 expected); on --new the door
   copies it to the target's .env (mode 0600), never printing or staging
   it") is designed for exactly this. It did nothing in the field because
   (a) no preset existed (stranger path skips silently), and (b) even
   with a preset, config-home resolution is broken on Apple git 2.30.1
   (KIT-0080 S3) so the preset would never be read on the reporting
   operator's machine.

Also verified: `.env.template:78,81` starts with `PROJECT_NAME=` (empty)
and `TASK_PREFIX=TASK` — a silently-wrong default that a hand-copied
`.env` carries until someone notices; the template's comment says these
are set during onboarding, but no onboarding surface writes them.

## Requirements

- **F1 — the door seeds `.env` on `--new`.** From the preset's
  `env-source` when present (existing behavior — keep); otherwise from
  the target's own `.env.template`. Either way the file exists, is mode
  0600, and is gitignored (verify with `git check-ignore .env`, which the
  scaffold's .gitignore already satisfies).
- **F2 — fill the project identity fields.** The door knows the project
  name (target basename) and, for single shape, the `--prefix` answer —
  write `PROJECT_NAME` and `TASK_PREFIX` into the seeded `.env`. Planning
  shape has no prefix flag (the door refuses `--prefix` there; the prefix
  is decided at seeding/intake, Step 4 of the intake agent) — decide at
  implementation: either the intake agent's seeding step updates
  `TASK_PREFIX` (it edits marker regions already; add the `.env` line to
  its checklist — but note an agent editing `.env` may trip the
  permission classifier, so prefer the door writing a placeholder the
  DOCTOR flags loudly). Whatever lands: `TASK_PREFIX=TASK` must not
  survive as a silent default — change the template default to empty and
  make the doctor WARN on empty-or-`TASK`.
- **F3 — key carry-over is operator-consented, operator-executed.** When
  no preset/env-source exists, the door (which the OPERATOR runs — that
  boundary is what makes this acceptable) either offers the copy
  interactively (TTY) with an explicit consent question naming the
  source path, or prints the exact one-line copy command for the
  operator to run. Never leave it to a later agent session; document the
  classifier constraint (field fact 1) in the door's help or
  STARTING-A-PROJECT so nobody re-attempts agent-side provisioning.
- **F4 — first-session surfacing.** The CLAUDE.md `first-session` block
  (written by the consumer engine) gains one line: verify
  `project doctor` env-keys is green before the first evaluation — so a
  skipped F3 surfaces at session start, not mid-review.
- **F5 — template honesty.** Fix `.env.template`'s comments to describe
  the mechanism that actually exists after this task (door-seeded +
  operator carry-over), not the fictional "set during the planner
  onboarding process".

## Acceptance Criteria

- [ ] `bootstrap --new` (both shapes) leaves a mode-0600, gitignored
      `.env` in the target with `PROJECT_NAME` filled and `TASK_PREFIX`
      either filled or loudly flagged by doctor — never silently `TASK`
- [ ] With a preset `env-source`, keys arrive with no interaction; with
      none, the operator gets an explicit consent prompt (TTY) or an
      exact printed command (non-TTY) — an agent is never the one moving
      key material
- [ ] Doctor env-keys goes green after following only the printed steps;
      the first-session block tells the operator to check it
- [ ] No secret value is ever echoed to stdout, logs, or git (existing
      env-source discipline preserved; add a test if feasible)

## Out of Scope

- Fixing preset resolution on Apple git 2.30.1 — that is KIT-0080 S3 (a
  prerequisite for the preset path to work on the reporting operator's
  machine, but this task's template-seeding path works regardless)
- Authoring the operator's preset (`/setup-preset` exists for that)

## Related

- Issue #104 (source), KIT-0080 S3 (preset resolution broken on Apple
  git), KIT-0082 (acceptance test should assert the seeded-.env
  invariants), /setup-preset skill, `docs/STARTING-A-PROJECT.md`

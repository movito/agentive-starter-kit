# KIT-0093: ADR-0028 phase 2 — the door switches to package-install mode

**Status**: In Progress
**Priority**: high (the phase where new projects stop inheriting the copy-machinery era; absorbs four parked tasks)
**Type**: Infrastructure / migration
**Estimated Effort**: 2-4 days (PR plan required)
**Created**: 2026-08-08
**Source**: KIT-ADR-0028 (Accepted), Consequences §Migration step 2.
**Evaluation**: arch-review-fast APPROVED 2026-08-08, first pass. Log: `.adversarial/logs/KIT-0093-door-package-install-mode--arch-review-fast.md`
**Absorbs** (each archived with a disposition pointing here — their
FULL text remains in `6-canceled/`, and this spec cites the specific
requirements it inherits): KIT-0078 (cold-start UX), KIT-0087
(provisioning-story scrub), KIT-0081 (door/intake polish findings),
KIT-0082 (scaffold acceptance test).

## Overview

Phase 1 published the machinery (`agentive-kit` 0.2.0: lifecycle,
doctor, evaluators, gates; the plugin channel already exists for
agents/skills/commands). Phase 2 makes the door STOP copying and START
installing: `bootstrap --new` produces a repo of content + pins + a
CLAUDE.md record, verifies (or instructs) the two package installs, and
runs doctor — nothing else ships. New projects are born packaged; every
door-authored copy of scripts and agents ends here.

This is also where the operator's original cold-start complaints get
their structural fix: the entry UX (KIT-0078's "instruct, don't
interrogate"), the three contradictory install stories (KIT-0087), the
door-polish gaps from the ev-fast-charging-loads intake (KIT-0081), and
the missing works-out-of-the-box proof (KIT-0082) are all requirements
of THIS task, listed below with their sources.

## Requirements

- **F1 — the door stops copying (core switch).** `bootstrap --new`
  (both shapes) creates: the `.kit/` content skeleton (tasks folders,
  context, templates, workflows), `docs/adr/`, README, CLAUDE.md
  (identity + kit-install record + target pointer for planning shape),
  `.adversarial/config.yml` with both pins, seeded `.env` (KIT-0084
  behavior preserved verbatim), and the per-repo check hook. It does
  NOT copy `scripts/core/` (agentive-kit provides them — the door
  verifies `agentive` on PATH or prints the `uv tool install` line) and
  does NOT copy `.claude/agents|skills|commands` (the plugin provides
  them — the door verifies the plugin or prints the install line).
  Produce a per-artifact decision table in the PR: ships-in-repo /
  package / plugin, with rationale — the KIT-0067 lesson (enumerate
  FUNCTIONS, not directories) applies to this removal above all others.
  KIT-LOCAL marker seeding into agent copies retires with the copies;
  project context lands in repo-owned files agents read at runtime
  (ADR-0025 already mandates this shape).
- **F2 — entry UX (absorbed from KIT-0078).** One user-facing entry:
  `/new-project`. The README and every opening surface INSTRUCT
  (DO-THIS sequences, route-map openings) rather than interrogate;
  free-text answers accepted anywhere a menu is offered. The
  `create-project` agent's fate is decided HERE (fold away or
  deprecation pointer — KIT-0078 F2's verdict; KIT-0087 F3's
  contradictions die with whichever outcome). Acceptance is
  journey-shaped: the cold-start transcripts referenced in KIT-0078
  and the ev-fast-charging-loads intake replayed against the new door
  must produce no dead ends, no contradictory instructions, no
  reference to a file the repo doesn't have.
- **F3 — provisioning-story scrub (absorbed from KIT-0087).** The
  inventory-with-verdict table over every surface that installs or
  instructs installing any toolchain piece (its Starting Inventory
  list, refreshed by grep); every retained surface delegates to
  `agentive`/`install-evaluators`/plugin install — zero surfaces carry
  their own install commands (grep-provable); the shape-independence
  audit table (no retained instruction may assume pyproject, a venv,
  or a kit checkout on disk); no unearned "verified" claims.
- **F4 — door/intake polish (absorbed from KIT-0081, re-verified
  against current source before fixing — several may be moot by
  construction once F1 lands).** F1-stale-tail, F2-dangling-refs
  (moot if nothing is copied — verify), F3 `git init -b main` in the
  intake path, F4 GEMINI/GOOGLE key naming in installer output (check
  whether the ported evaluators module still carries it),
  F5 worktree-helper story (`new-worktree.sh` entry: port, delegate,
  or retire — decide here), F6 a sanctioned rename/retarget procedure,
  F7 topology placeholder (moot with no agent copies — verify),
  F8 scaffold README ships, F9 dirty-tree export notice (likely moot —
  the door exports far less; verify what `git archive` still ships).
  Each item: fixed, or declared moot with the one-line proof.
- **F5 — scaffold acceptance test (absorbed from KIT-0082).** The
  automated proof the door's output WORKS: fresh `--new` run per shape
  → `agentive doctor` green-or-actionably-instructive, entry flow
  reachable, seeded-.env invariants hold (reuse `TestEnvSeedingE2E`
  assertions), evaluator-cli line PASS-or-instructive, zero dangling
  references (trivial by construction — assert it anyway). Wired into
  CI for door/engine changes. KIT-0082's removal rule is recorded in
  the workflow docs: de-shipping a file requires enumerating its
  functions and a green acceptance run.
- **F6 — consumer-facing docs tell the new story.** README Quickstart,
  STARTING-A-PROJECT, UPDATING-YOUR-PROJECT: create = door + two
  installs; update = `uv tool upgrade agentive-kit` +
  `claude plugin update`. Phase 3 (existing-consumer migration) is
  explicitly out of scope but the docs may name it as "coming".

## Acceptance Criteria

- [ ] A fresh `--new` project (both shapes) contains zero copied
      scripts/agents, passes the F5 acceptance test, and reaches a
      working first evaluation + first task flow using only installed
      packages and printed instructions
- [ ] The journey replays (F2) pass without dead ends
- [ ] Provisioning grep: exactly one install-command home (F3)
- [ ] Every KIT-0081 item fixed or proven moot (F4 table in PR body)
- [ ] Decision records in the PR: per-artifact ships/package/plugin
      table, create-project verdict, new-worktree verdict, launcher
      consumer verdict (KIT-0075 F4 cross-ref)
- [ ] Docs updated (F6); CI carries the acceptance test (F5)
- [ ] Coordination: if this releases agentive-kit 0.3.x, KIT-0092
      rides the same release (shim removal + guard retightening)

## PR Plan (required)

Likely 3: (1) acceptance test RED against today's door (proves it
catches the current copies) + F4 quick fixes; (2) the F1 core switch +
F3 scrub + F2 UX, turning the test green; (3) docs + decision records +
release. Refine in PR 1.

## Out of Scope

- Phase 3 (migrating existing consumers — the upgrader's job, own spec)
- Phase 4 (sync-machinery retirement + backlog dissolution)
- Plugin CONTENT changes (agent behavior) beyond distribution wiring
- Linear sync, evaluator library contents

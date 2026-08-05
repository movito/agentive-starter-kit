# KIT-0087: One provisioning story — scrub the competing "make a new project" installs

**Status**: Backlog
**Priority**: high (every fresh project inherits whichever story its entry surface happens to tell)
**Assigned To**: unassigned
**Type**: Infrastructure / consolidation
**Estimated Effort**: 1 day
**Created**: 2026-08-05
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Sibling (navigation half)**: KIT-0078 — "instruct, don't interrogate".
Its F2 makes `/new-project` the ONE user-facing entry and demotes the
other surfaces. **This task is the provisioning half**: KIT-0078 decides
which door a user walks through; KIT-0087 makes every door install the
same thing. Verified 2026-08-05: KIT-0078 contains no mention of
adversarial / install / provisioning / evaluators outside its own
evaluation-log path — the gap is real, not a duplicate.
**Consumes**: KIT-0083 (canonical pin home = `.adversarial/config.yml`;
`install-evaluators` becomes the one install path for library + CLI)
**Related**: #60 (pin location, reframed below), KIT-0079 (library-pin
relocation), KIT-0055 (which binary PATH resolves — the layer above
this one), KIT-0066 (intake flow), KIT-0067 (front door)

## Overview

The kit ships **three different, mutually contradictory answers** to
"how does a new project get the adversarial toolchain?" Which one a
project gets depends on which entry surface created it. All three are
live and shipped today:

| Surface | Installs the CLI how | Installs evaluators how |
|---|---|---|
| `scripts/local/bootstrap` (the door) → `project install-evaluators` | **not at all** (KIT-0083 fixes) | git-clone whole library by ref |
| `.claude/agents/create-project.md` | tells user `pipx install adversarial-workflow` (`:180`, `:317`) | `adversarial library install <provider>/<evaluator> --yes`, four times (`:214-217`) |
| `pyproject.toml:42` (kit's own dev checkout) | `adversarial-workflow>=1.0.1` as a Python dep | n/a |

Verified 2026-08-05 against source. The field-verified mechanism that
actually works for a consumer project is a FOURTH one:
`uv tool install adversarial-workflow` (issue #103, KIT-0083 F1).

`create-project.md:260` compounds it by printing
`adversarial-workflow: <version> verified` in its summary — a claim
nothing in that agent establishes, since it never installs the CLI.
This is a `displayed_commands_are_contracts` violation (patterns.yml,
claims clause): the summary asserts a verification that did not happen.

### Root cause (established 2026-08-05, KIT-0083 session)

Both pins landed in `pyproject.toml` in commit `c851276` (KIT-0035),
when the kit was **single-shape** — every project had a
`pyproject.toml`, so that was a fine home. The planning shape arrived
later in `924a5bb` (KIT-0053), and `engine-consumer.sh:294`
deliberately never ships `pyproject.toml` to planning repos (correct —
they have no Python toolchain).

**The split did not create a bad location; it turned a previously-fine
location into an unreadable one for half of all projects.** Every
surface that predates the split still assumes a single-shape world
where `pyproject.toml` is universally readable and a project venv
always exists. That assumption is the shared defect behind all of the
above.

This also reframes **#60**, currently filed as a consistency bug
(`v0.10.0` is not on PyPI). The two pins were never inconsistent —
they are two different artifacts: `adversarial-workflow>=1.0.1` is a
PyPI distribution (the CLI) and `v0.10.0` is a git tag on
`adversarial-evaluator-library` (the evaluator library). #60 is a
**location** bug wearing a consistency costume. Record this on #60 so
it is not re-litigated.

## Requirements

- **F1 — inventory, with a verdict per surface.** Enumerate every
  live surface that installs, or tells a user to install, any part of
  the adversarial toolchain (agents, commands, docs, scripts, CI
  workflows). For each: keep / rewrite-to-delegate / delete, with the
  grep evidence that justifies it. Archive/CHANGELOG mentions are
  explicitly OUT — historical records stay accurate to their moment.
  Starting inventory (2026-08-05, non-exhaustive):
  `.claude/agents/create-project.md`, `.claude/agents/bootstrap.md`,
  `.claude/agents/project-intake.md`, `.claude/commands/new-project.md`,
  `docs/STARTING-A-PROJECT.md` (`:210-238` "Other ways through the
  door"), `scripts/local/bootstrap`, `scripts/optional/setup-dev.sh`,
  `README.md:47` (agent table).
- **F2 — one install path, delegated to.** `project install-evaluators`
  (post-KIT-0083: library + CLI, pin from `.adversarial/config.yml`)
  is the SINGLE implementation. Every other surface either invokes it
  or points at it — no surface carries its own install commands. Any
  surface that cannot delegate must record why in the PR.
  **Failure contract** (arch-review-fast finding, 2026-08-05): becoming
  the single path makes this command's failure modes everyone's failure
  modes, so they are specified rather than incidental —
  - every failure names the surface that failed, why, and the exact
    command to recover (the existing git-missing block at
    `project:815-822` is the house pattern)
  - the optional CLI degrades, never aborts: a missing `uv` prints the
    install command and continues, so the library still lands
    (KIT-0083 F1 already establishes this; F2 makes it the contract)
  - exit codes stay stable for programmatic callers: `0` success or
    benign no-op, non-zero only for a genuine failure to provision
  - re-running is safe and says what it did — the existing
    `.installed-version` no-op path is the model; partial failure
    leaves a re-runnable state, never a half-installed one that
    reports success
- **F3 — kill the contradictions in `create-project.md`.** Per
  KIT-0078 F2 this agent is already slated for deprecation-or-fold;
  sequence with it (see below). Whichever way it goes, these three
  must not survive: `pipx` as a competing mechanism, per-evaluator
  `adversarial library install` as a competing provisioning path, and
  the unearned `adversarial-workflow: <version> verified` summary
  line.
- **F4 — shape-independence audit.** Every retained surface is checked
  against BOTH shapes: no instruction may assume `pyproject.toml`, a
  project venv, or a Python toolchain exists. This is the root cause
  above turned into a check — it is what stops the next surface from
  reintroducing the class. The audit is a **table in the PR body**, one
  row per retained surface, not a claim that it was done — same
  fixed questions for each, each answer carrying its grep or line
  reference:

  | Surface | Assumes `pyproject.toml`? | Assumes venv / Python? | Assumes kit checkout on disk? | Planning-shape verdict |
  |---|---|---|---|---|

  A surface fails the audit on any yes that is not accompanied by a
  shape guard. "Assumes kit checkout" is the third column because the
  #103 trap was exactly that: the only working binary lived in the
  kit's own `.venv`, which a consumer project must never reach into.
- **F5 — a doctor line or test that catches regression.** Provisioning
  drift is invisible until first use (the #103 trap). Either extend
  KIT-0082's scaffold acceptance test with a per-route assertion
  (fresh project via each retained route → `evaluator-cli` doctor line
  PASSes) or add a repo-level test asserting no surface outside
  `install-evaluators` contains an adversarial install command. Decide
  at implementation; state which and why.

## Acceptance Criteria

- [ ] A fresh project created through ANY retained route reaches a
      working `adversarial` CLI by following only that route's printed
      instructions — no reaching into a kit checkout, no manual install
- [ ] Exactly one surface in the repo contains an adversarial install
      command; all others delegate or point (grep-provable, and the
      grep is in the PR body)
- [ ] No live surface names `pipx` or per-evaluator
      `adversarial library install` as the provisioning mechanism
- [ ] No live surface claims a verification it does not perform
- [ ] Every retained instruction is valid in BOTH shapes (F4 audit
      recorded in the PR)
- [ ] Regression guard in place (F5)
- [ ] #60 updated with the location-vs-consistency reframing

## Sequencing

1. **KIT-0083** lands first — establishes `.adversarial/config.yml` as
   the canonical pin home and makes `install-evaluators` install
   library + CLI. Without it there is no correct path to delegate TO,
   and F2 has nothing to point at.
2. **KIT-0078 and this task should be done together, or 0078 first.**
   They are two halves of one problem and both touch
   `create-project.md`, `new-project.md`, `STARTING-A-PROJECT.md`, and
   `README.md`. Landing them independently means two passes over the
   same files and a near-certain merge conflict. If done together,
   0078's F2 decides whether `create-project.md` folds away, and this
   task's F3 becomes trivial (a deleted file carries no contradictions).
   Planner decides at promotion; record the choice.

## Out of Scope

- KIT-0055 (which binary PATH resolves, editable-install detection) —
  that is the layer above; this task only ensures ONE gets installed
- The evaluator library's own contents or version scheme
- Rewriting the door's shape/profile matrix (KIT-0053 settled it)
- Archive material and CHANGELOG history

## Notes

- Source: operator observation 2026-08-05 during the KIT-0083 handoff
  — *"we have a lot of loose ends here, with old onboarding agents and
  scripts floating around that previously handled the installation of
  adversarial-workflow"*, and the operator's read that the
  planning/code repo split kicked it off (confirmed above, with the
  refinement that the split revealed rather than caused it).
- Evaluation: arch-review-fast **REVISION_SUGGESTED** 2026-08-05, all
  three findings refinements rather than structural objections; ratings
  Clear / Moderate / High / Clean / Consistent / Ready. Log:
  `.adversarial/logs/KIT-0087-one-provisioning-story--arch-review-fast.md`
  - **API/STRUCTURAL_RISK (install-evaluators failure modes)** —
    ACCEPTED, folded into F2 as the failure contract.
  - **STRUCTURAL_RISK (F4 audit rigor)** — ACCEPTED, F4 now requires an
    audit table in the PR body rather than an assertion that the audit
    happened.
  - **COUPLING (sequencing risk)** — NOTED, no change. The evaluator's
    own text says "no structural change to the task description is
    needed"; its suggestion (a pre-promotion meeting between task
    owners) presumes a multi-owner team. Single-operator kit: the
    planner promotes, and the Sequencing section already carries the
    decision it needs. Recorded so a future reader does not re-open it.
- The `.adversarial/` provisioning story is the worked example, but F4
  is the durable rule: **pre-split surfaces assume single-shape.**
  Expect the same class in any other surface that predates `924a5bb`.

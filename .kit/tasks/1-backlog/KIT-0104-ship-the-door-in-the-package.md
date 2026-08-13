# KIT-0104: Ship the door in the package — `agentive new` / `agentive adopt`

**Status**: Backlog
**Priority**: high — this is the load-bearing move of KIT-ADR-0030;
every other move in the 0030–0034 set still starts inside the factory
until it lands
**Type**: Architecture / packaging
**Estimated Effort**: 1.5-2 days (port, not rewrite — see F1 scope note)
**Created**: 2026-08-09 (revised 2026-08-13: combined-ADR split +
evaluator findings folded in)
**Source**: KIT-ADR-0030 (operator conversation 2026-08-09 —
"I am spending more time working on getting ASK back on track than I am
on taking Cowork one-offs and turning them into usable software")

## Related

**ADR**: `.kit/adr/KIT-ADR-0030-the-door-ships-in-the-package.md`
**Extends**: KIT-ADR-0028 phase 2 (KIT-0093 — `--new` projects born
packaged; that work is what makes this port possible)
**Blocks**: KIT-0105 (`project-intake` into the plugin — its "must run
from a kit checkout" constraint dies with this task)

## Overview

The kit packaged everything a project *contains* and left unpackaged
the one thing that *creates* a project. `scripts/local/bootstrap`
declares itself "Kit-side only: runs from an agentive-starter-kit clone
against a target; never ships on any sync tier or consumer rsync", so
every project creation begins with a session opened inside the kit
repo — backlog present, planner ready to triage it.

The reason for that exemption was that the door's job used to be
copying the kit tree. After KIT-0093 a `--new` project is an enumerated
content scaffold plus pins. The reason expired; the exemption did not.

Move the door into `agentive-kit` as `agentive new` / `agentive adopt`.
Both verbs ship together: KIT-ADR-0028 is Accepted — COMPLETE (phase 3
closed as a no-op; phase 4 retired the sync machinery in KIT-0102), so
there is no copying `adopt` left to wait on.

## Requirements

- **F1 — `agentive new` and `agentive adopt` as package subcommands.**
  Same flags, same shape × profile matrix, same preset resolution chain
  (CLI flag → preset → kit default → interactive prompt), same
  kit-install record written by the consumer engine. **Scope note —
  port, not rewrite**: argument parsing, matrix validation, and matrix
  *ownership* move into Python; the three engines may initially ship as
  packaged data scripts invoked by it. A full shell→Python rewrite is
  explicitly NOT required to get the addressability win, and attempting
  one in this task is scope creep.
- **F2 — matrix single-ownership moves, never duplicates — including
  during the interim.** KIT-ADR-0027 P3 names the door as the single
  owner of shape × profile legality. After this task the package is
  that owner: the Python front is the *sole* source of matrix legality
  from day one and the shell engines are pure executors *(claude-arch
  finding 2026-08-13 — an interim with split ownership drifts)*.
  `bootstrap --help`'s table must not survive as a second copy — the
  shim defers to the package for help output too. **File the
  engine-consolidation follow-up on this PR**, so the engines-as-data
  interim has a filed exit.
- **F3 — `scripts/local/bootstrap` becomes an `exec` shim** into the
  package with equivalent flags, on the same PR that lands F1. Per
  KIT-ADR-0027 P3: convergence is structural, not social. **File the
  shim-removal task in this PR**, pinned to the next minor release —
  an unenforced "one release later" is how six doors became six.
- **F4 — `new --no-kit` lands here, not as follow-on** *(claude-arch
  finding 2026-08-13)*. KIT-ADR-0032's rung 0 must be reachable from
  both verbs; `--no-kit` is currently `adopt, single only`
  (`bootstrap:406-434` guards). Add the `new` counterpart — a flag, not
  new machinery — so "plain repo" is expressible from both verbs. This
  is the API-completeness half of the move.
- **F5 — the factory-clone precondition is retired from the prose.**
  `docs/STARTING-A-PROJECT.md` "The factory model" and "How every kit
  conversation starts" currently instruct the operator to `cd` into the
  kit clone to create projects. Rewrite for the packaged world: the kit
  clone is the *development* home for the kit; creation happens
  wherever you are. Sweep the same claim in `bootstrap --help`,
  `README.md` Quickstart, and `.claude/commands/new-project.md`.
- **F6 — `/new-project` keeps deriving its questions at runtime.** The
  command must not gain a hardcoded flag list; it derives from the
  door's `--help` (KIT-0067 F2 rule). Verify it still does after the
  help output moves into the package.

## PR Plan

Estimated total change is well over the ~500-line PR-sizing threshold
and mixes a code seam with a doc sweep — the exact shape that produced
PR #120's nine bot rounds. Ship as **three sequential PRs to main**
(not stacked — CodeRabbit refuses stacked bases; STACKED-PR-WORKFLOW
lessons apply):

1. **PR 1 — the port** (F1, F2 ownership half): `agentive new` /
   `agentive adopt` as package subcommands; engines ship as package
   data invoked by the Python front; matrix legality lives in Python
   from day one; tests including the no-kit-checkout-relationship
   assertion. Pure code, one seam, self-contained — `bootstrap` is
   untouched and still works.
2. **PR 2 — the shim + flag** (F2 help deferral, F3, F4):
   `scripts/local/bootstrap` becomes the `exec` shim; `new --no-kit`
   lands; shim-removal task and engine-consolidation follow-up filed
   and linked. Small and mechanical.
3. **PR 3 — the prose sweep** (F5, F6): factory-clone language retired
   across `docs/STARTING-A-PROJECT.md`, `README.md`,
   `.claude/commands/new-project.md`, door help; `/new-project`
   runtime-derivation verified. **KIT-0094 rides this PR as its
   passenger** — the markdownlint config + pre-commit gate land with
   the doc churn, so the sweep's own files are lint-clean before the
   bots see them.

Each PR is independently green and inside the review-surface budget
(PR-SIZE-WORKFLOW); a bot loop on one cannot hold the others hostage.
Acceptance below is judged at the end of PR 3.

## Acceptance

- [ ] `agentive new <dir>` creates a working project from a directory
      that is not inside, and has no path relationship to, any
      agentive-starter-kit checkout — verified in a test that asserts
      the absence rather than assuming it
- [ ] `agentive doctor` in the created project reports healthy
- [ ] `agentive new <dir> --no-kit` produces a rung-0 repo (no `.kit/`,
      no kit install) — KIT-ADR-0032's terminal state from the `new`
      verb
- [ ] `scripts/local/bootstrap --new` still works, via the shim, with
      identical output
- [ ] Shape × profile legality has exactly one implementation in the
      tree (grep proof in the PR body) — and it is the Python front,
      not a shell engine
- [ ] Shim-removal task AND engine-consolidation follow-up filed and
      linked from the PR
- [ ] No live surface still instructs the operator to `cd` into the kit
      clone in order to create a project (grep by class, per KIT-0069
      F1: fix the class, not the instances found)

## Notes

- The console entry is `agentive` (`agentive_kit.cli:main`); the
  collision check and the `akit` fallback are recorded in
  `packages/agentive-kit/pyproject.toml`.
- Portability rule applies: stock macOS, bash 3.2, BSD userland. The
  engines are full of heredocs-in-`$( )` — see the
  `bash32_heredoc_apostrophes` entry in `.kit/context/patterns.yml`.
- This task is one of the two the KIT-ADR-0034 WIP cap allows open at
  once. The other is KIT-0105.

# KIT-0101: Ship the door in the package — `agentive new` / `agentive adopt`

**Status**: Backlog
**Priority**: high — this is the load-bearing move of KIT-ADR-0030;
every other move in that ADR still starts inside the factory until it
lands
**Type**: Architecture / packaging
**Estimated Effort**: 1.5-2 days (port, not rewrite — see F1 scope note)
**Created**: 2026-08-09
**Source**: KIT-ADR-0030 D1 (operator conversation 2026-08-09 —
"I am spending more time working on getting ASK back on track than I am
on taking Cowork one-offs and turning them into usable software")

## Related

**ADR**: `.kit/adr/KIT-ADR-0030-the-door-is-a-tool-not-a-place.md` (D1)
**Extends**: KIT-ADR-0028 phase 2 (KIT-0093 — `--new` projects born
packaged; that work is what makes this port possible)
**Blocks**: KIT-0102 (`project-intake` into the plugin — its "must run
from a kit checkout" constraint dies with this task)
**Sequenced with**: ADR-0028 phase 3 (consumer migration) — `adopt`
waits for it; `new` does not

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

## Requirements

- **F1 — `agentive new` as a package subcommand.** Same flags, same
  shape × profile matrix, same preset resolution chain (CLI flag →
  preset → kit default → interactive prompt), same kit-install record
  written by the consumer engine. **Scope note — port, not rewrite**:
  argument parsing, matrix validation, and matrix *ownership* move into
  Python; the three engines may initially ship as packaged data scripts
  invoked by it. A full shell→Python rewrite is explicitly NOT required
  to get the addressability win, and attempting one in this task is
  scope creep.
- **F2 — matrix single-ownership moves, never duplicates.** KIT-ADR-0027
  P3 names the door as the single owner of shape × profile legality.
  After this task the package is that owner. `bootstrap --help`'s table
  must not survive as a second copy — the shim defers to the package
  for help output too.
- **F3 — `scripts/local/bootstrap` becomes an `exec` shim** into the
  package with equivalent flags, on the same PR that lands F1. Per
  KIT-ADR-0027 P3: convergence is structural, not social. **File the
  shim-removal task in this PR**, pinned to the next minor release —
  an unenforced "one release later" is how six doors became six.
- **F4 — `adopt` deferred with a stated condition, not silence.** If
  ADR-0028 phase 3 has not landed, `agentive adopt` either (a) is not
  shipped and `bootstrap --adopt` keeps working unshimmed, or (b) ships
  and delegates to the kit-side path when it detects a copying adopt.
  Whichever is chosen, the door's help and `docs/STARTING-A-PROJECT.md`
  must state the current truth — no advertised-but-broken subcommand
  (the A00/A01 class from the 2026-07-24 audit).
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

## Acceptance

- [ ] `agentive new <dir>` creates a working project from a directory
      that is not inside, and has no path relationship to, any
      agentive-starter-kit checkout — verified in a test that asserts
      the absence rather than assuming it
- [ ] `agentive doctor` in the created project reports healthy
- [ ] `scripts/local/bootstrap --new` still works, via the shim, with
      identical output
- [ ] Shape × profile legality has exactly one implementation in the
      tree (grep proof in the PR body)
- [ ] Shim-removal task filed and linked from the PR
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
- This task is one of the two the ADR's own WIP cap allows open at
  once (KIT-ADR-0030 D5). The other is KIT-0102.

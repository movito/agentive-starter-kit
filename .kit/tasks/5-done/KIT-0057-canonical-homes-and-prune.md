# KIT-0057: Canonical homes + the prune — the arc closes (ADR-0027 P6)

**Status**: Done
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 4-6 hours
**Created**: 2026-07-19
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-ADR-0027 P6 (Accepted) — transformation task 6 of 6,
the last of the arc
**Absorbs**: KIT-0056 retro items 1–2 (the baked-manifest guard and
the cross-reader conformance harness — "natural to bundle with P6")
**Related**: KIT-0047 + KIT-0054 (removal tasks pinned to 0.9.0 —
this task's completion makes 0.9.0 cuttable), KIT-0030 (plugin
distribution copies)

## Overview

Close the transformation: one canonical home per artifact type, the
identity blur pruned, and the two seam-guards from KIT-0056's retro
landed. After this task the ADR-0027 sequence is complete, 0.9.0
becomes cuttable (executing KIT-0047 + KIT-0054's pinned removals),
and the downstream migration pass has a stable target.

## Requirements

### Functional Requirements

- **F1 — skills merge (inventory-gated)**: collapse `.claude/skills/`
  and `.kit/skills/` into ONE repo home. Step 1 is the
  consumer-impact inventory the ADR requires: which pinned plugin
  versions, downstream repos, agent prompts, and kit docs reference
  each old path (grep the plugin repo refs too). Planner prior:
  `.claude/skills/` wins (it is the Claude-Code-resolution home and
  the distributed one); `.kit/skills/` content moves in beside it.
  Ship with a **read-both-paths deprecation cycle for one release**
  (agents/docs that read the old path keep working) — never a hard
  move — and file the read-both removal task pinned to 0.9.0
  alongside KIT-0047/0054 (the shims-with-filed-removal rule).
- **F2 — the prune**:
  - kit's own `pyproject.toml` identity: `name = "your-project-name"
    # TODO` becomes `agentive-starter-kit` — verify the export
    engine's customize step still rewrites it for `--new` targets
    (characterization: a `--new` export must still produce the
    placeholder-free target result it does today);
  - `__pycache__` / `*.egg-info` swept and gitignore-audited;
  - `scripts/optional/` audit: categorize each entry
    (keep/move/retire) with one line of reasoning in the PR —
    `create-agent.sh`, `setup-dev.sh`, `create-project.sh` (now an
    engine shim), `linear_sync_utils.py`, `sync_tasks_to_linear.py`;
  - stray-artifact sweep: anything at repo root or in `docs/` that
    the arc orphaned (grep for references before removing — the
    KIT-0047 shim and KIT-0054 shims stay until 0.9.0).
- **F3 — baked-manifest guard** (KIT-0056 retro #1): one assertion in
  `tests/test_core_manifest.py` — the `core_version` inside
  `engine-consumer.sh`'s planning-shape heredoc equals
  `scripts/core/VERSION`. Kills the KIT-0050/0056 recurrence class.
- **F4 — cross-reader bots-declaration conformance harness**
  (KIT-0056 retro #2): one fixture table (valid, invalid, edge, AND
  duplicate-key cases) run through all three readers, asserting they
  agree on validity and on the effective token set — including
  first-wins on duplicates (now blessed contract:
  patterns.yml `record_duplicate_keys_first_wins`). This is the
  closure for the seams-between-readers class.
- **F5 — docs converge on the canonical map**: CLAUDE.md's directory
  tree and Key Scripts table, README where affected, and a short
  "canonical homes" table in DISTRIBUTION-ARCHITECTURE.md (agents →
  `.claude/agents/`, commands → `.claude/commands/`, skills → the F1
  winner, plugin = distribution copies of each).

### Non-Functional Requirements

- **N1**: no behavior change for existing consumers during the
  deprecation cycle — read-both must be tested from BOTH paths.
- **N2**: plugin namespacing (`agentive-workflow:<name>`) is
  untouched — the merge is repo-internal; the plugin's copies move in
  a separate plugin release if paths matter there (inventory decides;
  if the plugin repo needs a change, file it, don't do it here).
- **N3**: the prune deletes nothing that any grep still references
  (the KIT-0047/0054 pinned artifacts explicitly survive to 0.9.0).

## Acceptance Criteria

- [ ] Inventory artifact committed (what references each old skills
      path, incl. plugin refs) BEFORE the move commit
- [ ] One skills home; read-both cycle tested from both paths;
      removal task filed pinned to 0.9.0
- [ ] Kit pyproject named `agentive-starter-kit`; `--new` export
      still produces correctly-customized targets (characterization)
- [ ] `scripts/optional/` dispositions stated; strays swept with
      reference-greps shown
- [ ] Baked-manifest == VERSION guard green (and red when the heredoc
      is deliberately desynced in a scratch test)
- [ ] Conformance harness: all three readers agree across the fixture
      table incl. duplicate-key first-wins
- [ ] Docs show the canonical map; CLAUDE.md tree current

## Test Plan

- Inventory first (F1 gate), then move + read-both tests.
- Characterize `--new` export identity handling before touching
  pyproject (F2 net).
- F3 guard: desync fixture proves it fires.
- F4 harness: table-driven; add a case, all readers must face it.

## Notes

- Source: KIT-ADR-0027 P6 + KIT-0056 retro items 1–2 (absorbed).
- **Arc-end consequences when this merges**: the ADR-0027
  transformation is COMPLETE → (1) the operator's standing `rm -rf`
  allowlist reminder fires (scoped: `/tmp/`, `~/Github/ask-worktrees/`
  — third-recurrence friction), (2) 0.9.0 becomes cuttable (KIT-0047 +
  KIT-0054 + F1's read-both removals execute in it), (3) the
  downstream migration pass starts against a stable kit.
- Out of scope: executing any 0.9.0-pinned removal, downstream repos,
  the plugin repo (file, don't do — N2), KIT-0051/0052/0055.

## Evaluation (2026-07-19)

`arch-review-fast` (gemini-2.5-flash): **REVISION_SUGGESTED** — one
finding, plan judged "exceptionally sound", explicitly "not a
recommendation to revise the immediate task". Log:
`.adversarial/logs/KIT-0057-canonical-homes-and-prune--arch-review-fast.md`.
Planner disposition:

- **Declined — abstracting the `.claude/` prefix**: that directory is
  Claude Code's OWN discovery contract (the harness resolves
  agents/commands/skills from `.claude/`); it is an external
  interface, not a brandable internal path, and a symlink/wrapper
  layer over another tool's fixed convention is ceremony with a drift
  surface. ADR-0027's "Claude Code changing its per-path scoping
  model" revisit trigger already covers harness-side change.

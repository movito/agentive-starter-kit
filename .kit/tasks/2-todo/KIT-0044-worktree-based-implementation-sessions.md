# KIT-0044: Worktree-based implementation sessions (codify the pilot)

**Status**: Todo
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 3-4 hours
**Created**: 2026-07-14
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0043 (the worktree pilot — its retro is this task's
requirements source, every friction has a live session repro)
**Related**: KIT-0036 (GIT_DIR gotcha lineage), the f7a6c90 shared-clone
incident (the hazard worktrees eliminate)

## Overview

The KIT-0043 pilot proved the topology: the planner's primary clone stays
a normal checkout on `main`, implementation happens in per-task worktrees
under `../ask-worktrees/<TASK-ID>/`, and the shared-mutable-branch hazard
class (wrong-branch commits, divergent pulls, mid-turn checkout swaps)
disappears. It also produced six verified frictions
(`.kit/context/retros/KIT-0043-retro.md`, "What Should Change") and one
serious incident: a pre-commit `GIT_DIR` leak from inside the worktree
flipped `core.bare=true` on the primary clone — worktree tests can
*mutate* the real repo, not just fail. The suite-wide `GIT_*` isolation
fix already shipped (`tests/conftest.py`, commit `7ef104d`). This task
codifies everything else so worktree sessions are the default, not an
experiment.

## Requirements

### Functional Requirements

- **F1 — creation helper** (`scripts/local/new-worktree.sh <TASK-ID>`
  or a `project worktree <TASK-ID>` subcommand — implementer's choice,
  state reasoning): performs, in order:
  1. `git fetch origin` then
     `git worktree add ../ask-worktrees/<TASK-ID> -b feature/<TASK-ID>-<slug> origin/main`
     — branching from **fresh** `origin/main` (pilot friction #2: the
     pre-created branch was 10 commits stale, silently).
  2. Provisions the runtime artifacts from an **explicit, enumerated
     list maintained in the helper itself** (friction #3). Known-required
     today: `.venv` (symlink), `.env` (symlink),
     `.adversarial/evaluators/` (symlink preferred — shares the installed
     set). The acceptance criterion below includes a one-time
     `.gitignore` audit to confirm the list is complete; anything found
     gets added to the enumerated list, not to an "everything" glob.
  3. Prints the launch instruction: "open the session tab with cwd =
     `<worktree path>`".
- **F2 — starter template**: make the open-tab-in-worktree instruction
  un-skippable in `.kit/templates/TASK-STARTER-TEMPLATE.md` — a dedicated
  LAUNCH block above FIRST ACTIONS, not a note (friction #1: running from
  the wrong dir cost ~40 `cd` prefixes, measured).
- **F3 — lifecycle**: define ownership and timing in the workflow doc:
  the implementing agent leaves the worktree clean (everything pushed);
  the **planner** removes it (`git worktree remove` + `git worktree
  prune`) at task completion, after the retro is read (friction #6).
- **F4 — WORKTREE-WORKFLOW.md**: new doc in `.kit/context/workflows/`
  covering: topology (primary = planner's clone, always `main`;
  worktrees = implementation), creation (F1), the pre-commit `GIT_DIR`
  contract (conftest isolation is suite-wide since `7ef104d`; any NEW
  test spawning git must rely on it, never on ambient env), the
  post-pre-commit canary (`git -C <primary> config core.bare` must be
  `false`), closeout (push from worktree; planner completes in primary),
  and lifecycle (F3). Link from CLAUDE.md's Workflow Reference table.
- **F5 — bare-hub design note** (decision record, not implementation):
  write down the evaluated option of a deliberate bare-hub layout (bare
  primary + standing `ask-worktrees/main`) with its real migration costs
  — Claude Code per-path session/memory/permission scoping, adversarial
  CLI's repo-root `.adversarial/` requirement, every script's repo-root
  assumption — and record the decision (expected: declined at current
  scale). One section in WORKTREE-WORKFLOW.md or a short ADR;
  implementer's choice. Include an explicit **revisit trigger**: re-open
  the decision if Claude Code's per-path scoping model changes, the
  adversarial CLI's root requirement lifts (ADV-0053), or a second
  operator joins. (Pilot friction #5, reframed after the bare state
  proved to be damage, not design.)

### Non-Functional Requirements

- **N1**: the helper must be idempotent-safe: refuse (with a clear
  message) if the worktree path or branch already exists.
- **N2**: nothing in this task changes `preflight-check.sh` or test
  logic — the conftest isolation is already shipped; this task documents
  and wraps.
- **N3**: helper lives where consumers won't receive it unaudited
  (`scripts/local/` is not synced downstream) unless the implementer
  argues for core placement in the PR.

## Acceptance Criteria

- [ ] One command creates a fully-provisioned worktree from fresh
      origin/main (venv, env, evaluators all usable — verified by running
      `pytest --collect-only` and `adversarial --help` inside it)
- [ ] Helper refuses cleanly on existing path/branch
- [ ] Starter template has the un-skippable LAUNCH block
- [ ] WORKTREE-WORKFLOW.md exists, linked from CLAUDE.md, covering
      topology, GIT_DIR contract, canary, closeout, lifecycle
- [ ] Bare-hub option written down with migration costs and a recorded
      decision
- [ ] This task's own session runs in a worktree created by hand with
      the F1 recipe (second pilot) and its retro confirms the six
      frictions are addressed or re-files what isn't

## Test Plan

- Create a scratch worktree with the helper; verify provisioning
  (pytest collect, adversarial listing, .env readable); verify refusal
  on re-run; remove it.
- Run one full commit cycle inside the scratch worktree and confirm the
  canary (`core.bare` false in primary) — the exact leak vector from the
  pilot is not conclusively pinned, so this proves the conftest fix
  holds under real hook conditions.

## Notes

- Source: `.kit/context/retros/KIT-0043-retro.md` (all six "What Should
  Change" items; #4 conftest isolation already resolved in `7ef104d`) and
  `.kit/context/KIT-0043-SESSION-SUMMARY-FOR-PLANNER.md`.
- The f7a6c90 incident (planner committed onto a checked-out feature
  branch in the shared clone) is the motivating hazard — worktrees make
  it structurally impossible; the planner-side branch-verify footgun
  stays as defense in depth.

## Evaluation (2026-07-14)

`arch-review-fast` (gemini-2.5-flash): **REVISION_SUGGESTED** — two minor
findings, design judged sound. Log:
`.adversarial/logs/KIT-0044-worktree-based-implementation-sessions--arch-review-fast.md`.
Planner disposition — both accepted:

- **Enumerated artifact list** instead of "ALL gitignored artifacts" —
  F1.2 rewritten: explicit list in the helper, `.gitignore` audit adds to
  the list, never a glob.
- **Bare-hub revisit trigger** added to F5 (Claude Code scoping change,
  ADV-0053 lifting the CLI root requirement, or a second operator).

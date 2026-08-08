# KIT-ADR-0029: Task-as-folder — per-task paperwork travels with the task; `.kit/context/` holds only shared durables

**Status**: Proposed — **deliberately deferred** (operator, 2026-08-08):
adopt after the current agentive-kit work completes (KIT-0093 phase 2
tail, KIT-0092/0.3.x, and the ADR-0028 phases 3–4); revisit then, do
not implement before. This document parks the analysis so the decision
survives the wait.
**Date**: 2026-08-08
**Deciders**: Fredrik Matheson (operator), planner-f5
**Related**: KIT-ADR-0028 (packaging — makes this refactor cheap for
the first time), KIT-0086 (guards-not-rituals precedent)
**Evaluation**: arch-review-fast APPROVED 2026-08-08, first pass
(`.adversarial/logs/KIT-ADR-0029-task-as-folder--arch-review-fast.md`)

## Context

`.kit/context/` has become a catchall. Measured 2026-08-08: 26
top-level entries of which 8 are per-task handoffs (1 belonging to a
live task), 3 are review starters for merged PRs, plus session
findings, a UX brief, an orphaned starter — beside the genuinely
durable set (`patterns.yml`, `REVIEW-INSIGHTS.md`,
`agent-handoffs.json`, `workflows/`). Below: `retros/` 38 files,
`reviews/` 69 files.

Three causes, none individually wrong:

1. **Every convention names the same home.** Handoffs (planner Phase
   4), review records (evaluator skill), retros (retro command),
   insights, workflows, coordination JSON — twelve reasonable "where
   does X live" answers all said `.kit/context/`, so it became the
   union of every artifact type.
2. **Two lifetimes share one namespace, and only one has a
   lifecycle.** Durable references (read forever) cohabit with
   per-task ephemera (read for a week, then never). The structural
   asymmetry: tasks got status folders in the kit's first week; the
   task's PAPERWORK never got a lifecycle at all — `project complete`
   moves the task file and even rewrites paths inside the handoff,
   but the handoff itself stays where birth put it, forever. Every
   completed task strands 2–3 satellites.
3. **Naming instead of foldering.** `<TASK-ID>-HANDOFF-<agent>.md`
   encodes ownership for globbing but makes active and dead work
   visually indistinguishable. Retros and reviews got subfolders when
   someone felt the pile; handoffs never did.

An intermediate fix (grouping satellites into per-task folders UNDER
`context/`) was considered and rejected during the analysis: it
reorganizes clutter into tidier clutter without removing the reason
paper accumulates at a separate address from the thing it belongs to.

## Decision

**A task is a folder, not a file**, and it carries its own paperwork
through the lifecycle:

```
.kit/tasks/<status>/<TASK-ID>-<slug>/
├── spec.md          # today's task file
├── HANDOFF.md
├── STARTER.md
├── reviews/         # evaluator records, per-PR
└── RETRO.md         # arrives at completion
```

- `project move|complete` relocates ONE folder; the entire paper
  trail travels together and arrives in `5-done/` as a self-contained
  record — matching how history is actually consulted ("what happened
  on KIT-0090?").
- **`retros/` and `reviews/` dissolve entirely** — they exist today
  only because those artifacts had no home with their task. Each file
  migrates into its task's folder.
- **`.kit/context/` shrinks to the shared durables only** (~6
  entries): `agent-handoffs.json`, `current-state.json`,
  `patterns.yml`, `REVIEW-INSIGHTS.md`, `workflows/`, `README.md`.
  The name finally tells the truth, and nothing per-task can
  accumulate there again — structurally, not by discipline.
- Stragglers (`archive/`, `research/`, one-off briefs) get a one-time
  triage in the migration: task folders, `docs/`, or deletion.

## Consequences and tradeoffs (mitigations pre-decided)

1. **Every glob changes** (`tasks/*/<ID>-*.md` →
   `tasks/*/<ID>-*/spec.md`): lifecycle CLI, status validator,
   handoffs drift check, Linear sync. All of it now lives in
   `agentive-kit` — one package, one PR, one test suite. This is the
   first time this refactor has been cheap; that is also why it WAITS
   for the in-flight agentive-kit work to settle rather than landing
   amid it.
2. **Backlog stubs get heavier** — mitigation options (implementer's
   pick, recorded in the PR): bare files allowed in `1-backlog/`,
   folder-ized at `project start` (the moment paperwork begins); or
   uniform one-file folders accepted as the price of consistency.
3. **Historical references**: old citations describe where things
   WERE and stay as written; only forward-looking surfaces (templates,
   planner Phase 4, skills) change. Files remain greppable by
   TASK-ID wherever they sit.
4. **The scaffold must be born this way**: the door seeds `.kit/`, so
   the new layout ships in the scaffold at adoption time — never
   retrofitted into consumers separately from the door change.
5. The mover is CODE in the lifecycle, not planner ritual
   (KIT-0086's guard-not-discipline rule applies).

## Adoption trigger

Revisit when the pre-adoption queue is clear: KIT-0093 closed,
KIT-0092 shipped (0.3.x), and ADR-0028 phases 3–4 done or explicitly
re-planned. At that point: file the implementation task citing this
ADR, carrying the glob inventory and the one-time migration of the
107 existing per-task files.

## Alternatives considered

- **Status quo + periodic sweeps**: rejected — sweeping is a ritual;
  rituals regress (KIT-0086).
- **Per-task folders under `context/`** (the intermediate option):
  rejected — keeps a second address for task-owned artifacts; the
  catchall's cause survives.
- **Archive-on-complete only** (flat namespace, relocate at
  completion): rejected — active-task clutter remains, and the flat
  namespace still can't distinguish live from dead at a glance.

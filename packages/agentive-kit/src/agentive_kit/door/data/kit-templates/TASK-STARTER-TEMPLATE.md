# Task Starter Template — the single starter authority

**Version**: 2.1.0
**Last Updated**: 2026-08-13
**Purpose**: THE contract for task starter messages. Every starter a
planner produces — in this repo or any consumer project — instantiates
this template. Planner agent bodies point here; they do not carry
their own section lists (two authorities drift — KIT-0101 R5, from an
operator comparison of kit starters against a consumer planner's).
**Used By**: Coordinators (planner, planner-f5) at assignment time

---

## The required core (no starter may omit any of these)

Every starter carries ALL of the following, however small the task.
Depth scales; the core does not (see the proportionality rule below).

1. **Header** — `## Task Assignment: <TASK-ID> — <Title>`, followed by
   links to BOTH files:
   - **Task File**: `.kit/tasks/<folder>/<TASK-ID>-<slug>.md`
   - **Handoff File**: `.kit/context/<TASK-ID>-HANDOFF-<agent-type>.md`
2. **Mission** — 2–3 sentences: what needs to be done and why, ending
   in a clear action-oriented goal.
3. **Acceptance criteria as checkboxes** — the definition of done. A
   mission without ACs has no definition of done (the observed gap
   that motivated this core): even a one-line task gets at least one
   `- [ ]` criterion, specific and checkable.
4. **Time estimate** — a number or range; phase breakdown only when
   the task has phases.
5. **⚠️ LAUNCH block — planner-pre-created, real values only.** The
   worktree/branch is created at AUTHORING time by the planner
   (ordering rule, `WORKTREE-WORKFLOW.md`: `project start` on `main`,
   push, THEN `git worktree add`). The block names the worktree path
   and branch that ACTUALLY exist — never placeholders, never "create
   a branch". KIT-0043 measured the cost of a session launched from
   the primary clone (~40 stray `cd` prefixes); KIT-0083/0088 the
   cost of a session inventing its own branch.
6. **⚠️ FIRST ACTIONS — verification only.** The session verifies the
   topology; it never creates it (never `checkout -b`):

   ```text
   ⚠️ FIRST ACTIONS (verification only — never `checkout -b`):
   1. `git branch --show-current` → expect `feature/<TASK-ID>-<slug>`;
      anything else: STOP and ask
   2. `git rev-parse --show-toplevel` → expect `<worktree path>`
   ```

   The task file is already in `3-in-progress/` — the planner moved it
   before creating the worktree, so the starter never instructs the
   agent to run `project start`.
7. **Recommended agent** — named explicitly (e.g. `feature-developer`,
   or the `-f5` variant with a one-clause reason).
8. **Operator launch checklist — the starter's final section.** The
   complete list of operator todos, numbered, with REAL values (no
   placeholders), so an operator who has never launched a session can
   execute it without any other document (operator request,
   2026-08-13 — the KIT-0101 cold-start lesson one level up):

   ```markdown
   **🚀 Launch checklist (operator)**:
   1. Open a new terminal tab: `cd <worktree absolute path>`
   2. `claude --agent <recommended-agent>`
   3. Paste this starter as the FIRST message — a bare agent launch
      idles without one (KIT-0101 F8)
   4. `/rename <TASK-ID> <short task name>` (named sessions are
      findable for /resume — operator convention, 2026-08-06)
   ```

   The checklist subsumes the former session-rename footer (its step
   4). Steps may be adapted when the task genuinely launches
   differently (e.g. a review-only session with no worktree), but the
   section itself is core: every starter ends with the operator's
   todos.

## House improvements (include when the task warrants them)

Codified from live use — these are what separate a good starter from
a minimal one. Include each WHEN it applies; omit silently when not:

- **Authority pointer** — one line stating where truth lives: *"the
  spec's R1–R5 are authoritative"* / *"the handoff's Session topology
  is authoritative"*. Prevents the starter itself from becoming a
  competing spec.
- **Budget and gate citations** — when the task runs under a standing
  policy (review-surface budget, evaluator tier policy, circuit
  breaker), cite it in one line each. Cite, don't restate.
- **Out of scope — do not touch** — name the adjacent surfaces the
  agent must leave alone, with the parking place for discovered gaps
  (usually `1-backlog/`).
- **Evaluation status** — if the spec was evaluated, one line: verdict
  - where the dispositions live ("don't re-litigate").
- **Success metrics** — quantitative/qualitative targets, for tasks
  where "done" has measurable shape beyond the ACs.
- **Contract-string cautions** — when the task touches text that tests
  pin (sentinels, printed contract lines), say so and name the test.

## The proportionality rule

**Depth scales with the task; the core never does.** A one-day
enumerated fix gets the compact form below — core plus only the house
improvements that apply. A multi-PR or journey-shaped task gets the
full form — phased ACs, budget citations, per-PR structure. What is
NEVER proportional: dropping a core element because the task is
small. The compact example carries every one of the eight.

---

## Worked example — compact (small enumerated task)

```markdown
## Task Assignment: TASK-0031 — Fix stale doctor hints in seeded README

**Task File**: `.kit/tasks/3-in-progress/TASK-0031-stale-doctor-hints.md`
**Handoff File**: `.kit/context/TASK-0031-HANDOFF-feature-developer.md`

Three seeded-README hints still name the retired `check-env.sh`; the
doctor replaced it in 0.9. Sweep the seeds, update the hints, prove
the sweep with a grep. The task file's list of three sites is
authoritative.

**Acceptance Criteria**:
- [ ] All three seed sites name `project doctor` (grep-proven in the PR)
- [ ] No other `check-env.sh` reference survives outside CHANGELOG history

**Time Estimate**: 2 h

**⚠️ LAUNCH** — already done by the planner. Worktree:
`../myproj-worktrees/TASK-0031` on `feature/TASK-0031-stale-doctor-hints`
(task already `3-in-progress`). Open the session tab there.

**⚠️ FIRST ACTIONS** (verification only — never `checkout -b`):
1. `git branch --show-current` → expect `feature/TASK-0031-stale-doctor-hints`; anything else: STOP and ask
2. `git rev-parse --show-toplevel` → expect `../myproj-worktrees/TASK-0031`

**Recommended agent**: `feature-developer`

**🚀 Launch checklist (operator)**:
1. Open a new terminal tab: `cd /Users/me/Github/myproj-worktrees/TASK-0031`
2. `claude --agent feature-developer`
3. Paste this starter as the FIRST message
4. `/rename TASK-0031 stale doctor hints`
```

## Worked example — full (multi-PR task)

```markdown
## Task Assignment: TASK-0087 — Split the export pipeline (+ release 1.4)

**Task File**: `.kit/tasks/3-in-progress/TASK-0087-split-export-pipeline.md`
  ← R1–R4 authoritative; evaluation dispositions in the header
**Handoff File**: `.kit/context/TASK-0087-HANDOFF-feature-developer.md`
  ← Session topology + the schema-pin cautions; read FIRST

### Overview

The export pipeline conflates rendering and packaging; every format
addition touches both. Split it behind the renderer interface (R1–R2),
migrate the two built-in formats (R3), and prove parity with the
golden-file suite (R4). Ships as package release 1.4.

### Acceptance Criteria (Must Have)

- [ ] **Two PRs, each within the review budget**: PR 1 = R1–R2
      (interface + core), PR 2 = R3–R4 (migration + parity). Either
      blows the budget → STOP and report a further split
- [ ] R1: renderer interface extracted; no format-specific imports in
      the packager (grep-proven list in PR)
- [ ] R2: packager consumes the interface only; contract tests pin it
- [ ] R3: both built-in formats migrated; schema pins updated in the
      same commit (`tests/test_export_schema.py` — that test's own rule)
- [ ] R4: golden-file parity run recorded in the PR body
- [ ] Release 1.4 shipped; post-merge verification cited

### Time Estimate

2 days: interface (3 h), packager rework (4 h), migration (4 h),
parity + release + review loops (3 h).

### Notes

- Evaluator: fast tier on PR 1 (mostly moves), full trio on PR 2
  (behavior changes) — per the standing tier policy.
- Out of scope: the plugin export (TASK-0090) and anything under
  `vendor/`. Gaps discovered there → file in `1-backlog/`.
- Spec evaluated: REVISION_SUGGESTED, both findings dispositioned in
  the spec header — don't re-litigate.

**⚠️ LAUNCH** — already done by the planner. Worktree:
`../myproj-worktrees/TASK-0087` on `feature/TASK-0087-split-export-pipeline`
(real venv provisioned, task already `3-in-progress`). Open the
session tab there.

**⚠️ FIRST ACTIONS** (verification only — never `checkout -b`):
1. `git branch --show-current` → expect `feature/TASK-0087-split-export-pipeline`; anything else: STOP and ask
2. `git rev-parse --show-toplevel` → expect `../myproj-worktrees/TASK-0087`

**Recommended agent**: `feature-developer-f5` (multi-PR judgment,
sustained run)

**🚀 Launch checklist (operator)**:
1. Open a new terminal tab: `cd /Users/me/Github/myproj-worktrees/TASK-0087`
2. `claude --agent feature-developer-f5`
3. Paste this starter as the FIRST message
4. `/rename TASK-0087 export pipeline split`
```

---

## The companion handoff file

The starter stays viewport-sized; depth lives in the handoff file the
header links. Structure:

```markdown
# <TASK-ID>: <Title> — Implementation Handoff

**You are the <agent-type>. Implement this task directly. Do not
delegate or spawn other agents.**

**Date**: YYYY-MM-DD
**From**: <coordinator>  **To**: <agent-type>
**Task**: .kit/tasks/<folder>/<TASK-ID>-<slug>.md
**Status**: Ready
**Evaluation**: <verdict + log link, or N/A>
**Target Codebase**: <this repo | the target repo> (split mode)

## Session topology (read before anything else)
[Worktree path, branch, single/multi-PR plan — REQUIRED section]

## Mission
[Detailed breakdown; phases if phased]

## Verified anchors (dated — re-verify before relying)
[File:line anchors for every surface the task touches]

## Test approach
[What proves it — suites, replays, grep sweeps]

## Out of scope — do not touch
[Named surfaces + where to file discovered gaps]
```

---

## Planner workflow (authoring time)

1. Task spec evaluated and revised; handoff file written (Session
   topology REQUIRED).
2. `./scripts/core/project start <TASK-ID>` **on `main`**, push.
3. Create the worktree/branch (`./scripts/local/new-worktree.sh
   <TASK-ID> <slug>`, or `git worktree add` — in split mode against
   the target repo). The LAUNCH block quotes what this ACTUALLY
   created.
4. Write the starter from this template — required core always, house
   improvements as warranted, depth per the proportionality rule.
5. Update `agent-handoffs.json`; present the starter with a one-line
   summary: *"Task starter ready — invoke `<agent-name>` in a new
   tab."*

## Implementing-agent contract (receiving time)

1. FIRST ACTIONS are verification only — wrong branch or path: STOP
   and ask, never `checkout -b`, never proceed from the primary clone.
2. Read the task file and handoff file before any edit.
3. Work the ACs; the starter's checkboxes are the definition of done.

---

**Related**: `AGENT-TEMPLATE.md`, `OPERATIONAL-RULES.md`,
`.kit/context/workflows/WORKTREE-WORKFLOW.md`

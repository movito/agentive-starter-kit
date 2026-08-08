# KIT-0085: Task starters need a valid external-authoring path — split the checklist, stamp the LAUNCH block, add ingestion

> **Demoted to backlog (2026-08-08, tidy)**: still valid (the EFKT external-authoring pain was real; templates remain per-repo content) but not assignable now, and its tooling half (ingest/stub scripts) belongs in agentive-kit post-ADR-0028. Re-scope the tooling to package modules at promotion.

**Status**: Backlog
**Priority**: high (every externally-authored starter is born non-compliant; the template forces the improvisation it exists to prevent)
**Type**: Process / Template + tooling
**Estimated Effort**: 4-6 h
**Created**: 2026-08-04
**Source**: Operator report (Fredrik, 2026-08-04) after running the KIT-0066
flow end to end: prototype in a claude.ai session → PROTOTYPE-BRIEF.md →
same session wrote a task starter + handoff (PLAY-0001) for a Claude Code
agent. The prototype-handoff template held up; TASK-STARTER-TEMPLATE
v1.1.0 did not survive contact with an external coordinator.
**Evaluation**: arch-review-fast, 2 rounds 2026-08-04. Round 1
REVISION_SUGGESTED — all 3 findings addressed in this spec (atomic
temp-then-rename for `agent-handoffs.json`; stub clarified as one-way
provisioning transport, stamped LAUNCH block operative afterward;
severable `--adopt-only` provisioning so ingestion survives KIT-0080).
Round 2 REVISION_SUGGESTED with 2 forward-looking advisories, accepted
as noted: concurrency-safe handoffs access is explicitly a future task
if the single-writer assumption changes; internal modularization of
`adopt-starter` is at implementer discretion. Log:
`.adversarial/logs/KIT-0085-external-starter-authoring-path--arch-review-fast.md`

## Overview

`TASK-STARTER-TEMPLATE.md` v1.1.0 assumes the author sits inside the kit
checkout. Its checklist mandates that the worktree is created BEFORE the
starter is written ("so the path and branch in the block are real",
line 124-127) and that `agent-handoffs.json` is updated (checklist,
line 341). A coordinator writing a starter from a conversation session
can do neither, so every externally-authored starter fails the checklist
on arrival and has to invent an ad-hoc "coordinator note" deviation —
exactly the improvisation the template exists to prevent. KIT-0066 gave
prototype BRIEFS an external-origin path; task starters need the same.

Verified against the current files:

1. **Impossible-from-outside checklist.** Checklist items "Worktree
   created … LAUNCH block included with the real worktree path and
   branch" and "agent-handoffs.json updated" (template lines 337-341)
   require checkout access. No external-compliance mode exists.
2. **Branch names have two sources of truth.**
   `scripts/local/new-worktree.sh` takes a slug or derives one from the
   task spec filename (lines 96-120: `KIT-0051-fix-the-thing.md` →
   `fix-the-thing`), and the template requires the LAUNCH block to
   "match what the helper actually created" (line 114-116). Written
   externally, the block can only guess; even in-checkout it is a human
   transcription of helper output.
3. **No ingestion step.** Externally-written starters and handoffs
   arrive as loose files. Nothing defines who moves them into
   `.kit/tasks/` and `.kit/context/`, creates the worktree, stamps the
   LAUNCH block, and updates the assignment record.
4. **Referenced artifacts unspecified.** Checklist item 1 requires the
   task spec file to exist but the template names no format (canonical:
   `.kit/tasks/9-reference/templates/task-template.md`); the
   `agent-handoffs.json` update is mandated with no schema or example
   (live shape: top-level agent-name keys, each with `status`,
   `current_task`, `task_started`, `brief_note`, `details_link`,
   `handoff_file`).

## Requirements

- **F1 — split the checklist into author-time and provisioning-time.**
  Author-time items (sections present, acceptance criteria, metrics,
  estimates, handoff file drafted, task spec drafted-or-attached) are
  satisfiable anywhere, including a conversation session. Provisioning-
  time items (worktree exists, LAUNCH block carries real path + branch,
  `agent-handoffs.json` updated) are satisfiable only in-checkout. The
  template must state both lists, define an externally-authored starter
  as COMPLIANT when all author-time items pass and the LAUNCH block
  carries an explicit provisioning placeholder (not guessed values),
  and name who performs the conversion (F3). Bump the template version
  (checklist semantics change: 1.1.0 → 2.0.0).
- **F2 — make the helper the single source of truth for the LAUNCH
  block.** `new-worktree.sh` additionally emits a machine-readable
  launch stub (suggested: `.kit/context/<TASK-ID>.launch`, simple
  `key=value` lines: worktree path, branch, creation timestamp, slug
  origin). Provisioning stamps the starter's LAUNCH block from the stub
  — humans and external coordinators never transcribe branch names. The
  stub is the contract between helper and provisioning step; document
  its format where it is emitted and where it is consumed.
  Derivation is one-way and terminal: the stub is provisioning-time
  TRANSPORT, not a live second copy — after stamping, the starter's
  LAUNCH block is the operative human-facing record, and the stub is a
  receipt (keep or delete at implementation's choice, but the template
  and script docs must say which, so nobody treats a stale stub as
  authoritative later).
- **F3 — add an ingestion step (adopt-starter).** A deterministic
  script (suggested: `scripts/core/` or `scripts/local/`
  `adopt-starter`) that takes an externally-authored starter + handoff
  pair and: places the task spec in `.kit/tasks/2-todo/` and the
  handoff in `.kit/context/` under canonical names, runs
  `new-worktree.sh`, rewrites the starter's LAUNCH block from the F2
  stub, and updates `agent-handoffs.json`. The planner invokes it; the
  template's provisioning-time section points at it. Idempotent-safe in
  the house style: refuse loudly on existing task ID, existing branch,
  or malformed input — never half-adopt (temp-then-commit pattern for
  the multi-file move, `.kit/context/workflows/TEMP-THEN-COMMIT-PATTERN.md`).
  The `agent-handoffs.json` update follows the same pattern: read,
  modify, write to a temp file, atomic rename — never an in-place edit
  that can leave partial JSON. No locking layer (the file has a single
  operator-driven writer at a time in this flow); if that assumption
  changes, that is a separate task.
  Provisioning must be severable: an `--adopt-only` mode (name at
  implementation's discretion) ingests and validates the file pair and
  stops BEFORE worktree creation, leaving the starter with its
  placeholder LAUNCH block and a printed next step — so ingestion works
  even while `new-worktree.sh` is broken on a given machine (KIT-0080),
  and a later run completes provisioning.
- **F4 — specify the referenced artifacts in the template.** Link the
  canonical task spec template
  (`.kit/tasks/9-reference/templates/task-template.md`) from checklist
  item 1, and inline a minimal `agent-handoffs.json` entry example (one
  agent key with the six live fields) where the update is mandated.

## Acceptance Criteria

- [ ] The checklist is two explicitly-labeled lists (author-time /
      provisioning-time) with a stated conversion owner; an
      externally-authored starter can satisfy every author-time item
      with zero checkout access and zero ad-hoc deviations
- [ ] `new-worktree.sh` emits the launch stub; the stamped LAUNCH block
      in an adopted starter is byte-identical in path and branch to
      what the helper created (no hand transcription anywhere in the
      flow)
- [ ] `adopt-starter` run on a loose starter + handoff pair leaves:
      spec in `2-todo/`, handoff in `.kit/context/`, worktree
      provisioned, LAUNCH block stamped, `agent-handoffs.json` updated
      — or refuses cleanly with nothing half-moved
- [ ] With worktree creation unavailable (helper failing, KIT-0080
      machines), `adopt-starter --adopt-only` still ingests and
      validates the pair, leaves the placeholder LAUNCH block intact,
      and prints the completing step; the full mode on the same input
      later finishes provisioning without re-ingesting
- [ ] The PLAY-0001 worked example (external starter written under
      these constraints, deviations flagged inline — committed at
      `tests/fixtures/external-starter/`) passes the author-time
      checklist with zero deviations needing a coordinator note, and
      adopts cleanly
- [ ] Template references resolve: task spec format linked,
      agent-handoffs.json entry example inlined; template re-versioned
      with the change documented in its header

## Out of Scope

- Fixing `new-worktree.sh` on Apple git 2.30.1 (KIT-0080 — the helper
  is currently broken on the reporting operator's machine; F2's stub
  emission must not deepen that incompatibility, but fixing it is
  KIT-0080's job)
- Changing the prototype-handoff/brief flow (KIT-0066 — reported
  working)
- External authoring of the task SPEC format itself beyond linking it
  (the spec template is consumed as-is)

## Notes

- The operator's worked example (PLAY-0001 starter + handoff, written
  externally with deviations flagged inline) is committed at
  `tests/fixtures/external-starter/` (Vercel IDs placeholdered; see the
  fixture README for provenance). The project it came from is live —
  after this task ships, re-adopting the PLAY-0001 pair through the new
  flow is the end-to-end check that no ad-hoc deviations remain.
- F2 interacts with the in-checkout flow too: even planner-authored
  starters should stamp from the stub rather than copy helper stdout —
  one mechanism, two entry points.
- `agent-handoffs.json` currently records that worktrees are being
  created with plain `git worktree` while the helper is broken
  (KIT-0080); `adopt-starter` should fail with a clear message when
  the helper fails, not silently skip provisioning.

## Related

- Operator report 2026-08-04 (source), KIT-0066 (external-origin path
  for briefs — the precedent), KIT-0043/KIT-0044 (worktree pilot that
  produced the LAUNCH mandate), KIT-0080 (helper broken on Apple git
  2.30.1), `.kit/templates/TASK-STARTER-TEMPLATE.md` v1.1.0,
  `scripts/local/new-worktree.sh`,
  `.kit/context/workflows/WORKTREE-WORKFLOW.md`

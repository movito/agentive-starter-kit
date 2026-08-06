# KIT-0088: Worktree topology must survive any launch path — fix the single-point safeguard

**Status**: Done
**Priority**: high (the failure class recurred live on KIT-0083: a session started in the primary clone on `main` because nothing it read said otherwise)
**Type**: Process / agent definitions
**Estimated Effort**: 0.5 day
**Created**: 2026-08-05
**Source**: `.kit/context/KIT-0083-SESSION-FINDINGS.md` F3 (verified analysis; recommendations adopted with one record correction below)

## Overview

The worktree-per-task topology is documented in exactly two artifacts —
`WORKTREE-WORKFLOW.md` and `TASK-STARTER-TEMPLATE.md` — and both are
read at STARTER-AUTHORING time, by the planner. Nothing read at
IMPLEMENTATION time carries it:

- `feature-developer.md` contains "worktree" zero times (verified by
  grep, 2026-08-05) and its Phase 1 says `checkout -b` — directly
  contradicting the template's "the worktree already exists — never
  `checkout -b`" (`TASK-STARTER-TEMPLATE.md:363-364`)
- handoff files carry no topology section at all

**Record correction to SESSION-FINDINGS F3**: the KIT-0083 *starter*
(delivered in the planner chat, 2026-08-04) did carry a LAUNCH block
with explicit `git worktree add` commands. The session was launched
from the **handoff file** instead ("the handoff is already being read
by the KIT-0083 agent" — operator, 2026-08-05), and the handoff's
"single-repo mode" line was read as "work in this directory". So the
authoring path did not bypass the template — the LAUNCH PATH bypassed
the starter. This makes the findings' core conclusion stronger, not
weaker: any safeguard that lives only in an artifact a session might
never see is not a safeguard. The fix must live in what is ALWAYS
read: the agent definition and the handoff.

## Requirements

- **F1 — feature-developer Phase 1 becomes verify-not-create** (the
  findings' highest-leverage fix). In `feature-developer.md` AND
  `feature-developer-f5.md`: replace the `checkout -b` instruction with
  the template's contract — verify a worktree exists for the task and
  `git branch --show-current` matches; if there is no worktree, STOP
  and ask the operator rather than branching in the primary clone. A
  wrong topology becomes loud instead of silent, independent of what
  artifact launched the session. (Body edits inside the marker-safe
  regions' surroundings — do not disturb KIT-LOCAL markers.)
- **F2 — handoffs carry the topology.** Add a required **Session
  topology** line to the handoff format (planner.md / planner-f5.md
  Phase 4 checklist + any handoff skeleton): worktree path, branch
  name, and the "verify, never create" reminder. A handoff-only launch
  then carries the same safeguard as a starter launch.
- **F3 — write down the ordering rule** discovered in the KIT-0083
  bookkeeping note, in `WORKTREE-WORKFLOW.md` next to the creation
  recipe: **`project start` runs on `main` in the primary clone, push,
  THEN create the worktree** — otherwise the worktree carries a stale
  `2-todo` task file and fails its own validate-task-status hook. Note
  explicitly that this also keeps `agent-handoffs.json` churn off
  feature branches, agreeing with the KIT-0086 discipline (the two
  rules exist today but are written nowhere near each other).
- **F4 — kill the "single-repo mode" ambiguity.** Wherever handoffs/
  starters state repo mode, the phrase must say what it means:
  "single-repo (planning+code together) — NOT an instruction to work
  in the primary clone; see Session topology". One-line template fix.
- **F5 — planner-side authoring step.** planner.md / planner-f5.md
  Phase 5 gains the template's steps 3-4 explicitly (create/verify the
  worktree before writing the starter, carry its real path). Keep
  consistent with KIT-0080's state: on stock macOS git the helper
  hard-fails (S4), so the instruction references the portable plain
  `git worktree add` form until KIT-0080 lands.

## Acceptance Criteria

- [ ] grep "worktree" in feature-developer.md / -f5.md returns the
      Phase 1 verify contract; `checkout -b` no longer appears as the
      Phase 1 instruction
- [ ] A handoff authored per the updated planner procedure contains a
      Session topology section
- [ ] WORKTREE-WORKFLOW.md states the start-on-main-then-worktree
      ordering rule and cross-references the KIT-0086 discipline
- [ ] No template/handoff text can be read as "work in the primary
      clone" without explicitly saying so
- [ ] All four agent files keep their KIT-LOCAL markers intact
      (kit_markers.py check passes)
- [ ] A repo test (cheap grep-level assertion) verifies the Phase 1
      verify-contract text exists in both feature-developer files and
      the topology section requirement in the planner files — so the
      next rewrite of an agent definition cannot silently drop the
      rule (partial uptake of the evaluation's automation finding)

## Out of Scope

- KIT-0080's portable git fix itself (F5 references, doesn't implement)
- KIT-0086's single-writer implementation (F3 only cross-references)
- Retroactive starter regeneration for in-flight tasks

## Notes

- The KIT-0083 session recovered cheaply (nothing wrong landed on
  main), but only because the operator asked the right question at the
  right moment. That is not a control.
- Evaluation: arch-review-fast REVISION_SUGGESTED 2026-08-05; both
  findings (centralized agent-rule propagation; text-based agent
  definitions as a bottleneck) are structural-evolution suggestions the
  evaluator itself places "beyond the scope of this specific task".
  Dispositioned NOTED — banked as an ADR candidate in REVIEW-INSIGHTS,
  partially taken up via the grep-level regression test added to
  acceptance criteria. Log:
  `.adversarial/logs/KIT-0088-worktree-topology-enforcement--arch-review-fast.md`

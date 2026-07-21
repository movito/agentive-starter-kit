# KIT-0062: Scope bot review to product code — process artifacts stop drawing threads

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 2-3 hours
**Created**: 2026-07-21
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: operator observation on PR #90 — three correct-but-
irrelevant threads, all on process artifacts
**Related**: KIT-0040 F2 (killed the stale-path noise class by
automation), the bot-triage/check-bots skills (documentation targets)

## Overview

Every recurring bot-noise incident of the arc shares one signature:
**bots reviewing process artifacts as if they were product code**.
PR #90's three unresolved threads: policing the task-lifecycle
convention inside a diff, treating a retro's recorded-known-follow-up
as a merge blocker, and style-policing a 15-retro-old template
heading. Earlier instances: stale bookkeeping paths (until KIT-0040
automated them away), review-starter nits. These files are records
ABOUT the process — their "issues" are intentional states. Each noise
thread costs a triage-reply-resolve cycle and dilutes attention on
real findings.

## Requirements

- **F1 — verify each bot's ACTUAL config surface first** (self-review
  item 10 binds hard here: config schemas are exactly the
  shipped-hint class): read CodeRabbit's current docs for
  `.coderabbit.yaml` (path filters / path instructions) and Cursor
  BugBot's current configuration mechanism. Paste the verified
  surfaces into the PR. Do NOT implement from memory.
- **F2 — exclude the pure process records from bot review**:
  `.kit/tasks/**`, `.kit/context/retros/**`, `.kit/context/reviews/**`,
  `.kit/context/*-REVIEW-STARTER.md`, `.kit/context/agent-handoffs.json`.
  These carry no executable behavior; their conventions are enforced
  by `validate-task-status`, the metadata sync, and planner review.
- **F3 — keep real review where it has earned its keep**: `.kit/adr/**`
  (CodeRabbit substantively verified ADR claims), workflows, skills,
  commands, handoff files (they carry runtime claims), and ALL
  code/tests — unchanged. If a soft mechanism exists
  (path instructions vs exclusion), prefer instructions for handoffs
  ("process context: recorded follow-ups and lifecycle moves are
  intentional") and hard exclusion for F2's list — but let the
  verified config surface decide what's possible.
- **F4 — record the trade-off**: what bot eyes we give up on those
  paths, and the mitigations (specs are evaluator-gated pre-
  assignment; retros are planner-processed; the noise class had
  produced zero accepted findings on those paths across the arc —
  verify that claim against the review records before asserting it in
  docs).
- **F5 — docs**: bot-triage + check-bots skills note the scoping
  ("a thread on an excluded path means the config regressed — check
  the config file first").

## Acceptance Criteria

- [ ] Verified config surfaces pasted in the PR (both bots; whatever
      each actually supports)
- [ ] Config file(s) committed; exclusions live for F2's list;
      review retained for F3's list
- [ ] Trade-off + mitigations recorded (with the zero-accepted-
      findings claim verified, not assumed)
- [ ] Skills updated (F5)
- [ ] Demonstrated on the next process-touching PR: zero threads on
      excluded paths (note in that PR, not this one)

## Notes

- Evaluation skipped (planner): process/config change with the
  decisions made in-spec — the skip category. The one open judgment
  (instructions vs exclusion for handoffs) is explicitly delegated to
  the verified config surface.
- Exemplar threads: PR #90's three planner-dispositioned resolutions
  (2026-07-21) — linked evidence for F4.

# KIT-0069: Audit truth sweep — every prose surface matches reality

**Status**: Todo
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 1-1.5 days
**Created**: 2026-07-24
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: pre-0.9.0 cruft audit —
`.kit/context/reviews/PRE-090-CRUFT-AUDIT-2026-07-24.md`
**Sequenced after**: KIT-0068 (functional repairs) — several docs
describe behavior 0068 changes; sweeping first would re-stale them
**Siblings**: KIT-0065 (aider residue), KIT-0067 (structural/archival)

## Overview

The audit's prose cluster: ~55 confirmed findings where a live
surface states something false about the current kit — pre-v0.4.0
paths in help text, ghost files cited as current (the
PROCEDURAL-KNOWLEDGE-INDEX ghost alone has 8 citing surfaces),
version footers frozen at 0.5.0, model pins two generations old,
another application's rules inside `security-reviewer`, a 53%-vs-80%
coverage contradiction, and a doc that tells readers to run
`project sync` for Linear (now a different command). Mechanical in
nature, dangerous in aggregate: agents READ these surfaces and act
on them.

## Ownership rule (binding)

This task owns every confirmed audit finding EXCEPT those assigned
elsewhere:

- **KIT-0068** owns A00-A02, A04-A05, A08, A10-A15, A67, A69, A84,
  A88, A91
- **KIT-0065** owns A03, A09, A27, A29, A30, A47, A76
- **KIT-0067** owns the structural/archival set: A18, A33, A41, A44,
  A45 (launcher retirement decides the fix), A50, A61, A62, A68,
  A85-A87, A89, A90, plus the uncertain launchers-vs-door question
- Everything else confirmed in the audit record is THIS task's
  checklist. The PR body must list every owned A-number with a
  one-line disposition (fixed / already-fixed-by-0068 / defer-with-
  reason). No silent drops.

## Requirements

- **F1 — fix by class, not by file**: sweep each class across ALL
  its instances (the audit found instances, not necessarily all of
  them — grep each class pattern repo-wide before closing it):
  pre-v0.4.0 `./scripts/<name>` invocations; ghost-file citations
  (PROCEDURAL-KNOWLEDGE-INDEX, TASK-STARTER-TEMPLATE-at-agents-path,
  AGENT-TEMPLATE-at-agents-path, universal-agent-launcher.sh,
  nonexistent example ADRs, `.adversarial/evaluators/README.md`);
  version footers/tables (README 0.5.0, DISTRIBUTION-ARCHITECTURE
  3.0.0/17-files, CHANGELOG compare links, agent-creator footer);
  stale model pins (create-agent DEFAULT_MODEL, AGENT-TEMPLATE
  frontmatter, conftest fallback — align on the current pins used by
  live agents; verify IDs against live docs, not memory); the
  `/commit-push-pr` hardcoded Opus co-author (make it
  model-agnostic).
- **F2 — the dangerous contradictions get priority**:
  LINEAR-SYNC-BEHAVIOR's `project sync` advice (A39 — now a
  different command; rewrite for the post-KIT-0036 world), the
  53%-vs-80% coverage claims (A46 — pyproject fail_under=80 is
  truth), powertest-runner's Task-spawning instruction (A28 —
  contradicts the no-delegate rule three other surfaces state),
  /check-spec's uninstalled evaluator (A35 — point at an installed
  evaluator or retire the command; check what the evaluator library
  v0.10.0 actually ships before choosing), security-reviewer's
  foreign application rules (A25 — strip to kit-generic guidance).
- **F3 — templates fix generation, not just text**: AGENT-TEMPLATE
  and TASK-STARTER-TEMPLATE fixes must be checked against
  `create-agent.sh` output (generate one scratch agent, verify no
  stale content survives generation).
- **F4 — self-review addition**: one checklist line — "cited a file,
  command, or version? verify it exists/matches in THIS tree" (the
  audit's whole prose cluster is one violation class of this).

## Acceptance Criteria

- [ ] Every owned A-number dispositioned in the PR body
- [ ] Class-wide greps pasted for each F1 class (not just audit
      instances)
- [ ] No live surface cites a nonexistent file (spot-checkable:
      the audit's ghost list all resolve or are gone)
- [ ] Coverage number consistent everywhere with pyproject
- [ ] Scratch-generated agent from the fixed templates is clean
- [ ] Self-review item added

## Success Metrics

- **Quantitative**: 0 remaining confirmed-prose findings; class
  greps return only historical records
- **Qualitative**: an agent following any live doc executes commands
  that exist

## Time Estimate

1-1.5 days (it's wide, not deep). PR split allowed by area
(agents+skills+templates / docs+workflows) if > 500 lines.

## Notes

- **Evaluation: skipped (planner)** — the checklist derives from an
  audit where every item already survived adversarial verification;
  a second evaluation round would re-review the reviewers. The
  evaluator trio still runs pre-PR per standing rule.
- Sequencing: start only after KIT-0068 merges (several targets
  describe behavior 0068 changes).

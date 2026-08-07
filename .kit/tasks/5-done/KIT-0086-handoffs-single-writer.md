# KIT-0086: agent-handoffs.json single-writer — end the feature-branch/main conflict class

> **CLOSED BY REFERENCE (2026-08-07)**: implemented inside KIT-0090
> (PR #108 lifecycle guard — `project move` skips `agent-handoffs.json`
> on any branch other than main; PR #109 drift check
> `doctor.d/35-handoffs-paths.py` + workflow docs). The interim
> carve-out below is retired: the guard is now code. Disposition: done
> via KIT-0090; verification is that task's PR gates.

**Status**: Done
**Priority**: high (recurrence is guaranteed: it blocked PR #105's squash-merge and the same pattern is live for KIT-0083/KIT-0085)
**Type**: Infrastructure
**Estimated Effort**: 2-4 h
**Created**: 2026-08-04
**Source**: KIT-0084 retro ("What Should Change" #1; incident: squash-merge conflict on PR #105)
**Evaluation**: arch-review-fast APPROVED 2026-08-04, first pass. Log: `.adversarial/logs/KIT-0086-handoffs-single-writer--arch-review-fast.md`

> **Interim carve-out (planner decision, 2026-08-06 — KIT-0080 retro
> #5)**: until F1 lands, the script and the discipline contradict each
> other (`project move` auto-edits `agent-handoffs.json`; the
> discipline forbids branch-side edits). The resolved interim rule:
> the script's own writes are legitimate **on `main` only** (the
> ordering rule already puts planner lifecycle moves there); when a
> session must run `project move` on a feature branch, it REVERTS the
> JSON hunk before committing — exactly what the KIT-0080 session did;
> that behavior is now the blessed pattern, and the planner fixes the
> path at completion. F1's implementation (skip the JSON entirely)
> dissolves the contradiction; prefer the skip-when-not-on-main guard
> over a `--no-handoff-update` flag — a flag is a discipline you can
> forget, a guard is not.

## Overview

Two writers mutate `.kit/context/agent-handoffs.json` concurrently:

1. **Feature branches**: every `project start|move|complete` calls
   `_sync_coordination_metadata()` (`scripts/core/project:144`, added by
   KIT-0040 F2), which rewrites `.kit/tasks/<folder>/<file>` path strings
   in `agent-handoffs.json` and in `<TASK>-HANDOFF-*.md` files so status
   moves don't strand stale paths.
2. **The planner**: edits `brief_note`/`details_link`/queue state on
   `main` between and during tasks (planner.md Phase 4/6 requires it).

When both touch the same lines mid-task — exactly what happened on
2026-08-04, when the planner committed KIT-0083/0085 handoffs to main
while the KIT-0084 branch's status moves had rewritten the same
`details_link` lines — the merge conflicts. A global mutable JSON that
every branch AND main write is a standing conflict generator; parallel
planner sessions make it worse.

## Requirements

- **F1 — pick and implement a single-writer model.** Recommended
  direction (decide finally at implementation, record why in the PR):
  **the planner on `main` is the only writer of `agent-handoffs.json`**;
  feature-branch lifecycle commands stop touching it. Concretely:
  `_sync_coordination_metadata` keeps rewriting the task's own
  `HANDOFF-*.md` files (same-branch artifacts, no cross-branch writer)
  but skips `agent-handoffs.json` — status truth already lives in the
  task file's folder; the JSON is coordination convenience.
  Alternatives to weigh honestly: (a) per-task/per-agent file split
  (kills global contention but multiplies files and planner edits);
  (b) `.gitattributes` union merge (treats symptom, JSON union merges
  can produce invalid JSON — likely reject, say why).
- **F2 — stale-path story for the JSON.** KIT-0040 F2 existed because
  CodeRabbit flags stale paths on every move. If branches stop rewriting
  the JSON, decide who fixes its paths and when: planner on main at
  review/completion coordination (natural — the planner is already
  editing the entry then), plus a doctor or validate-task-status WARN
  when a `details_link` in the JSON points at a folder the task file is
  no longer in — so drift is loud without a second writer.
- **F3 — update the process docs to match.** `planner.md` (Phase 4/6 and
  the footgun list), `feature-developer.md` if it mentions the JSON, and
  `.kit/context/workflows/TASK-COMPLETION-PROTOCOL.md` — the rule
  becomes: branch sessions never edit `agent-handoffs.json`; planner
  owns it on main. Include the interim discipline's retirement (planner
  currently defers handoffs edits during in-flight PRs — that workaround
  dies when this lands).
- **F4 — tests.** Cover: a status move on a branch leaves
  `agent-handoffs.json` untouched; HANDOFF-*.md rewriting still works;
  the new drift WARN fires on a stale details_link and stays quiet on a
  fresh one. Existing `_sync_coordination_metadata` tests will need
  updating — that is expected, not scope creep.

## Acceptance Criteria

- [ ] `project start|move|complete` on a feature branch produces zero
      diff in `.kit/context/agent-handoffs.json`
- [ ] Stale-path drift in the JSON is surfaced by a check (doctor or
      pre-commit), not silently accumulated
- [ ] HANDOFF-*.md path rewriting behavior is preserved
- [ ] Process docs state the single-writer rule; no doc still instructs
      branch-side JSON edits
- [ ] CI green; the KIT-0083/KIT-0085 sessions (next in queue) run
      without a handoffs conflict at merge time

## Out of Scope

- Redesigning the coordination schema (fields, agents list)
- Linear sync integration changes
- The pull_request-event CI anomaly (separate watch item)

## Related

- KIT-0040 F2 (introduced the branch-side rewrite — this task narrows
  it, keeping its HANDOFF-file half), KIT-0084 retro + PR #105 incident,
  planner.md footguns ("Verify the branch before every commit" grew from
  the same shared-working-dir hazards)

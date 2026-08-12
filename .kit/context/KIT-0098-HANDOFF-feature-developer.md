# KIT-0098: Fresh-eyes repair of the round-churned sections — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-08-10
**From**: planner-f5
**To**: feature-developer
**Task**: `.kit/tasks/5-done/KIT-0098-churned-sections-repair.md`
**Status**: Ready — you are the FRESH SESSION the circuit breaker
prescribes; that framing is the whole point of this task
**Evaluation**: gate passed with disposition (release split to
KIT-0099) — record in the spec header

**Target Codebase**: This repo (agentive-starter-kit) — single-repo mode
(the repo split, not your working directory — see Session topology).

## Session topology (read before anything else)

- Worktree: `~/Github/ask-worktrees/KIT-0098`, branch
  `feature/KIT-0098-churned-sections-repair` — created and provisioned
  by the planner; the task file was `3-in-progress` at handoff time
  (the Task pointers in this file auto-update as the task moves — the
  prose here describes launch state, not current state)
- VERIFY, never create: `git branch --show-current` must show the
  branch above before your first edit; if not, STOP and ask
- ONE PR. The Plugin Drift Guard will be RED on it — by design (kit
  newer than published plugin; green returns when KIT-0099 ships
  2.0.1). Say so in the PR body; every other check genuinely green.

## Why you exist (read the spec's "Why a fresh task" section)

The previous session ran nine review rounds on PR #120; later rounds
were majority defects introduced by earlier fixes. It stopped itself —
correctly — and the repair moved to you: fresh context, tight
enumerated scope, coherence-reads instead of diff-reads. Two governing
limits are IN your acceptance criteria: the ~500-prose-line budget
(STOP and report if the fix can't fit) and the circuit breaker (if any
of your own review rounds go majority-self-inflicted, or you reach
round 4 — stop and escalate; do not become round 10 by another name).

## Verified anchors (2026-08-10)

- **#120 merged as 9258f8d** (+2,387/−567 final). Your baseline is
  current `main` — the churned text as it actually landed, not any
  intermediate round.
- **Known 4×-rewritten files**: `.claude/commands/check-ci.md`,
  `.claude/agents/ci-checker.md`. Derive the full ≥3-round list
  yourself: `git log 1cee2fb..9258f8d --name-only` is NOT enough (one
  squash) — use the PR's commit list
  (`gh pr view 120 --json commits`) or per-file thread counts; record
  the derived list in the PR body (S1 requirement).
- **The contract tests are your safety net AND your constraint**:
  `tests/test_agent_contracts.py` now pins evaluator-before-PR-open
  (table row + section order + declared numbers) and **pair-body
  identity below `## Workflow Overview`** (feature-developer/-f5,
  planner/-f5 — normalized only for the Response Format header). Any
  agent-body repair MUST land in both halves or the suite fails — the
  pair tax is now mechanical. If a legitimate reword moves a pinned
  sentinel, update the test in the same commit (its header says so).
- **S3 status at launch**: EMPTY — the operator read ci-checker.md and
  check-spec.md before merging #120 and flagged nothing further. If
  the operator adds items before your session starts, they'll be in
  the task file; re-read it first.

## Method notes (the coherence-read, concretely)

For each churned file: read the WHOLE file top to bottom as if
reviewing a stranger's first draft. You are looking for exactly the
class round 8 produced: two adjacent paragraphs giving contradictory
instructions (e.g. "take the path from the handoff" followed by
"validate via git rev-parse on this worktree"). For each S2 item,
UNVERIFIED until you've named the check: quote the surviving text,
state why it now has one coherent story (or fix it minimally).
The KIT-0080 lesson applies to yourself: a green suite doesn't prove
prose coherence — only reading does.

## Test approach

- Full suite per push (~213 s pytest-fast; ≥360 s timeouts).
- Evaluator trio pre-open, **`--format diff`** (strings-shaped).
  Disposition table; deep rounds ≤2.
- Every fix you make is fresh prose — expect bots to review it as
  such; the budget exists to keep that surface small.

## Out of scope — do not touch

- The 2.0.1 release (KIT-0099, after you merge)
- Content improvements beyond coherence + the S2 enumerated items
- Resolved #120 threads (don't re-litigate); KIT-0094's markdownlint
  scope (F19-class style declines cite it)

---

**Task File**: `.kit/tasks/5-done/KIT-0098-churned-sections-repair.md`
**Predecessor record**: PR #120 (55 threads) + its round-9 report; process
codification at 1cee2fb (PR-SIZE budget, bot-triage circuit breaker)

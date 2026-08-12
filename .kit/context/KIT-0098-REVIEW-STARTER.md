# KIT-0098 — Review Starter

**PR**: https://github.com/movito/agentive-starter-kit/pull/121
**Branch**: `feature/KIT-0098-churned-sections-repair`
**Task**: `.kit/tasks/4-in-review/KIT-0098-churned-sections-repair.md`
**Date**: 2026-08-10
**Status**: Ready for human review — repairs complete, loop stopped
deliberately under the circuit breaker (see below)

## What this PR is

The fresh-eyes repair session the bot-triage circuit breaker prescribes,
after PR #120 ran nine review rounds with later rounds dominated by
defects introduced by earlier fixes. Coherence-reads of whole files
rather than diff-reads of patches.

**Net effect: 51 lines of prose change across 4 files** — a
de-duplication repair. No application code or tests changed —
agent-instruction files only (instruction files ARE agent behavior;
the no-change claim is scoped to runtime code).

## ⚠️ Plugin Drift Guard is RED by design

Verified, not assumed: every entry reads "kit content is newer than the
published release", and the printed remedy is "cut a plugin release" —
which is **KIT-0099**, deliberately split out of this task. It also
flags files this PR never touched (`preflight`, `retro`, `wrap-up`,
`bot-triage`), so the drift predates this branch.

**Every other check is green**: Tests 3.10/3.12/3.14, Lint & Format,
CodeRabbit, Cursor Bugbot.

## S1 — derived ≥3-round file list (10 files)

Derived from the PR's own commit list (`gh pr view 120 --json commits`),
not `main`'s history — #120 landed as one squash, so per-round
attribution exists only in the PR.

| File | Rounds | Verdict |
|---|---|---|
| `check-spec.md` | 7 | **Repaired** |
| `feature-developer.md` | 7 | **Repaired** |
| `feature-developer-f5.md` | 7 | **Repaired** (pair) |
| `ci-checker.md` | 7 | **Repaired** |
| `code-review-evaluator/SKILL.md` | 5 | Coherent — no change |
| `upgrader.md` | 5 | Coherent — no change |
| `check-ci.md` | 3 | Coherent — no change |
| `test-runner.md` | 3 | Coherent — no change |
| `security-reviewer.md` | 3 | Coherent — no change |
| `document-reviewer.md` | 3 | Coherent — no change |

All three repairs were the same shape — **churn residue**: a later round
rewrote a passage correctly but left the superseded version beside it.

## S2 — every item verified with the check named

| Item | Result |
|---|---|
| Phase-1 split-mode path story | **PASS** — one story; `:196` explicitly forbids validating rev-parse output in split mode. One duplicate validation block removed. |
| `project start` gates PLANNING repo | **PASS** — `git -C "$PLANNING" branch --show-current` at `:251-258` |
| No non-persistent `cd` class | **PASS** — every instance single-calls `cd … && <cmd>` |
| `resolve_ref` API-failure vs unresolved | **PASS** — captures before decoding; `return 2` halts loudly; callers honor it |
| SHA-correction thread | **PASS, no action** — correction posted and acknowledged by CodeRabbit |

**S3**: empty at launch, re-confirmed against the task file.

## Review rounds and the circuit breaker

| Round | Source | Findings | Accepted | Self-inflicted |
|---|---|---|---|---|
| Evaluator trio (pre-open) | fast/o3/claude-code | 14 | 3 | 1 |
| Bot round 1 | CodeRabbit + Bugbot | 1 | 1 | 1 |
| Bot round 2 (re-review) | CodeRabbit + Bugbot | 0 | — | — |

**Totals: 2 self-inflicted of 15.** Zero unresolved threads.

### ⚠️ Operator decision point

Bot round 1 was **1-of-1 self-inflicted**, which trips the breaker on a
literal reading. I fixed that finding as a class in one commit, pushed
once, and **stopped the loop** — round 2 came back clean, confirming
convergence. Full reasoning in
`.kit/context/reviews/KIT-0098-evaluator-review.md`.

Structurally this is unlike KIT-0097 round 8: one incomplete sweep of
one class in one file, caught on the first bot pass, fixed class-wide
with a mechanical end-state check (`grep` for the stale framing returns
empty) rather than instance-by-instance.

## What a reviewer should look at

1. **`ci-checker.md`** — the largest change (52 lines). The placeholder
   contract now reads consistently across all five prose sites. Worth a
   coherence-read as a whole file, which is the method this task is about.
2. **`check-spec.md`** — the `$()` removal. Confirm the replacement
   still tells an agent unambiguously how to resolve the target root in
   both modes.
3. **The rejected findings** — 11 of 14 evaluator findings were
   rejected, each with a named verifying check in the review record.
   Worth a skim to confirm the rejections are sound.

## Process signal worth acting on

This is the **third consecutive prose-heavy PR** where the diff-format
evaluator trio spent most of its budget on findings that reconstruct the
pre-fix state (KIT-0069 0-for-7, KIT-0073 0-for-8, KIT-0098 3-of-14 with
9 reconstruction errors). All three evaluators independently reported
this PR had removed a safety guard that is plainly still in the file, at
HIGH severity.

Meanwhile the bots — which read the tree — went 1-for-1 with a correct,
specific, actionable finding.

The prose-sweep exception already says run `code-reviewer-fast` only on
sweeps. This PR was not a sweep but a targeted repair, and the same
pattern held. **Recommend the planner consider widening that exception
to prose-dominated changes generally**, and/or reconsider whether the
deep evaluator (o3, ~$0.33) earns its cost on any prose-shaped diff.

## Next

- Merge this PR → **KIT-0099** ships plugin 2.0.1, which turns the drift
  guard green again.
- This task ends at repairs-merged-and-verified, by design.

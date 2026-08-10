# KIT-0098: Fresh-eyes repair of the KIT-0097 round-churned sections

> **Evaluation**: arch-review-fast REVISION_SUGGESTED 2026-08-10; both
> findings converged on splitting the release out of the repair —
> ACCEPTED (S4 → KIT-0099). Gate passed with disposition. Log:
> `.adversarial/logs/KIT-0098-churned-sections-repair--arch-review-fast.md`

**Status**: In Review
**Priority**: high (gates plugin 2.0.1; the drift guard stays red until this lands)
**Type**: Content repair / verification
**Estimated Effort**: 0.5 day — and the review-surface budget applies:
if the fix diff approaches ~500 prose lines, STOP and split
**Created**: 2026-08-10
**Source**: KIT-0097 PR #120 round-9 report — nine review rounds, with
later rounds dominated by defects introduced by earlier fixes; the
session itself called for stopping the loop. This task is the fresh
session the circuit breaker (bot-triage SKILL, added 2026-08-10)
prescribes.

## Why a fresh task instead of round 10

Nine rounds of patch-on-patch left the most-edited sections rewritten
four times each, with round 8 introducing a contradiction round 9 then
fixed around. The session's own (correct) assessment: its edits were
adding defect surface faster than the original list shrank. Fresh
context, tight scope, coherence-reads instead of diff-reads.

## Scope — enumerated, verify-then-repair

**S1 — coherence-read the churned files AS WHOLES** (not as diffs):
`ci-checker.md` and `check-spec.md` first (4 rewrites each), then any
other file the #120 review touched in ≥3 rounds (derive the list from
the PR's commit history, record it). For each: does the section read
as ONE author's coherent instruction, with no step contradicting a
neighboring step? Rewrite minimally where it doesn't.

**S2 — re-verify the round-9 fixes with fresh eyes** (each was written
under churn pressure; trust nothing):
- The Phase-1 split-mode contradiction (round-8 own-goal, round-9
  fixed): confirm the surviving text has ONE path-resolution story —
  handoff-provided planning root, validated as itself, no residual
  pointer back to `git rev-parse` on the session worktree.
- `project start` gating: the check must verify the PLANNING repo on
  main (split mode), not the session's own worktree.
- The evaluator `cd "$PLANNING"` non-persistence class: any documented
  multi-step shell must either single-call the cd+command or use
  `git -C`/absolute paths (the kit's own Bash-CWD rule — grep the
  churned files for other instances of the same class).
- `resolve_ref` capture-before-decode: confirm the fix distinguishes
  API/rate-limit failure from genuinely-unresolved ref, loudly.
- The SHA-citation correction on the thread (52a99d0 vs a80823b):
  verify the correction landed; no action if so.

**S3 — operator findings**: anything the operator's pre-merge read of
the two files flags, enumerated here at start (may be empty).

**S4 — REMOVED** (evaluation finding, accepted): the 2.0.1 release is
**KIT-0099**, a dependent micro-task — the repair session repairs; the
release is a distinct mechanical step that shouldn't dilute fresh-eyes
scope. This task ends at "repairs merged and verified."

## Acceptance Criteria

- [ ] S1 coherence verdict recorded per file (coherent / rewritten,
      one line each)
- [ ] Every S2 item re-verified with the check named (grep/read/probe),
      not asserted
- [ ] `tests/test_agent_contracts.py` green; pairs rule held
      (feature-developer/-f5, planner/-f5 identical bodies)
- [ ] Diff stays under the review-surface budget (~500 prose lines) —
      if it can't, STOP and report for a split, don't push through
- [ ] Repairs merged and verified — READY FOR RELEASE (2.0.1 itself is
      KIT-0099, which depends on this task)
- [ ] Evaluator trio pre-open, `--format diff`; deep rounds ≤2; if any
      review round's findings are majority-in-text-this-review-changed,
      the circuit breaker applies — stop and escalate, do NOT run the
      loop past round 3

## Out of Scope

- New content improvements beyond coherence + the enumerated fixes
- The KIT-0097 findings already cleanly landed (don't re-litigate
  resolved threads)
- KIT-0094 (markdownlint) — though its absence is part of why prose
  rounds are expensive; the operator may choose to run it first

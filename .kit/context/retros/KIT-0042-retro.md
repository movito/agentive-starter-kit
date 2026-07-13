## KIT-0042 — Bundle-Aware Preflight Gates 5/6 (PR #74)

**Date**: 2026-07-14
**Agent**: feature-developer-f5
**Mode**: single-repo
**Scorecard**: 1 thread, 0 regressions, 2 fix rounds, 7 commits (6 session + 1 planner drive-by)

### What Worked

1. **Writing the decision before the code kept the diff tiny** — the
   route-(b) reasoning (bundle intelligence in process, not gate code;
   `find -name` can't express a boundary so glob-route prefix safety
   would force regex into a safety script) was written first, and the
   TDD pass then *proved* the convention needs zero gate-logic change:
   the pointer-file test passed against the unmodified exact-name find.
   The whole F1 mechanism ended up being a string change plus docs.
2. **The KIT-0040 stub-`gh` harness absorbed every scenario for free** —
   bundle PASS, F1.1 message content, prefix boundary, and empty-pointer
   cases needed only tmp-dir fixtures and one `extra_args` parameter on
   `run()`; no new canned payloads. 10 → 14 tests, all sub-second.
3. **Decline-by-reference worked as designed** — REVIEW-INSIGHTS' new
   "Empirically Disproven Reviewer Claims" section (from KIT-0035) plus
   fresh 30-second repros killed fast-v2's headline prefix-collision
   claim; fast-v2 itself retracted it in round 2. One real o3 catch
   (zero-byte pointers satisfying Gates 5/6) became the session's only
   substantive gate change (`-type f -size +0c`).
4. **The internal round-2 substitution covered the bot outage** — when
   CodeRabbit crashed, rerunning fast-v2 + first-run claude-code on the
   full diff (operator-requested) closed the review gap on `7166d99`;
   claude-code APPROVED. The gates' own fallback correctly stayed FAIL
   on the bot's failure status — strict was right; the substitution was
   documented, not faked.
5. **COMMIT-PROTOCOL's new verify-HEAD-moved step (from the KIT-0035
   retro) caught its target on its first outing** — the wrap-up commit
   staging the appended-logs review record was silently aborted by hook
   auto-fixes; the `git log --oneline -1` check caught it immediately
   instead of after a confusing push failure.

### What Was Surprising

1. **A planner commit landed mid-flight on my checked-out feature
   branch** — `f7a6c90` (KIT-0035 retro follow-through, from a parallel
   planner session) was committed onto `feature/KIT-0042-…` because
   that's what was checked out, and it *changed my requirements* (the
   F1.1 multi-PR-case addendum). Detected only because `gh pr create`
   failed and a `git log` check followed. Benign here — docs-only, and
   the addendum belonged to this task — but two sessions sharing one
   working tree is a real hazard.
2. **CodeRabbit's "Internal error occurred during review" was actually
   quota exhaustion** — three crash rounds (initial, `@coderabbitai
   review`, `@coderabbitai full review`) before the status finally
   changed to "Prepaid credits exhausted — enable usage-based reviews".
   The misleading first message cost two re-trigger cycles; the full
   review that "recovered" it apparently burned the last credits.
3. **Evaluator finding-repetition is a follow-up signal, not noise** —
   o3 and fast-v2 flagged the identical Gate 1/2/7 edge set in all three
   runs across two rounds. Individually declinable as out of scope, but
   the convergence earned KIT-0043. Decline tables are where recurring
   findings go to be forgotten unless someone counts them.
4. **`@coderabbit review` (wrong handle, no `-ai`) silently does
   nothing** — no error, no reaction. Cost one poll cycle before I
   noticed only my own correctly-addressed trigger comment mattered.

### What Should Change

1. **Sessions should not share a checked-out branch** — planner sessions
   doing bookkeeping while a feature branch is checked out will commit
   onto it. Options for the planner: bookkeeping sessions verify
   `git branch --show-current` is `main` before committing (one line in
   planner.md's commit guidance), or use `git -C` against a separate
   clone/worktree. The failure mode is silent and the commit lands in
   whatever PR is open.
2. **Bot-outage playbook is worth three lines somewhere** — "internal
   error" from CodeRabbit may mean quota; check the status detail text
   before burning re-trigger cycles, and the internal-evaluator
   substitution (rerun trio on full diff, document in the review record,
   proceed on 6/7 with the outage named) is now a proven pattern.
   Candidate home: babysit-pr or check-bots skill.
3. **KIT-0043 filed for the recurring Gate 1/2/7 findings** — including
   the reproduce-or-decline gate for o3's unverified Gate 2 mixed-context
   claim, so the fix round doesn't start by trusting it.

### Permission Prompts Hit

None.

### Process Actions Taken

- [x] KIT-0043 filed (`.kit/tasks/1-backlog/KIT-0043-preflight-gates-127-edge-hardening.md`)
      for the convergent out-of-scope evaluator findings
- [x] KIT-0042 moved to 5-done; merged branch deleted
- [ ] Planner: add branch-check line to bookkeeping commit guidance
      (What Should Change #1)
- [ ] Planner: consider bot-outage playbook note in babysit-pr or
      check-bots (What Should Change #2)
- [ ] Operator: CodeRabbit credits — top up or enable usage-based
      reviews (Gate 2 stays red on new pushes until then)

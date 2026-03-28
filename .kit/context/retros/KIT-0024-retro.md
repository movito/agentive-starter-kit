## KIT-0024 — Tiered Manifest & Sync Upgrade (PR #39)

**Date**: 2026-03-27
**Agent**: feature-developer-v5
**Scorecard**: 14 threads, 0 regressions, 6 babysit rounds, 9 commits (8 original + 1 wrap-up)

### What Worked

1. **6-cycle babysit loop caught real issues** — BugBot found backtick injection in shell variable expansion (`sync-core-scripts.yml`) and CodeRabbit flagged missing `.claude/commands/` directory guard. Both were genuine bugs that would have broken downstream sync.
2. **Dual evaluator approach validated the design** — Running arch-review-fast (Gemini) + code-reviewer (o3) post-bot gave complementary coverage: architecture coherence + edge-case logic. The arch review confirmed the tier model holds together; the code review stress-tested shell behavior.
3. **o3 false-positive triage was educational** — Finding #1 (VERSION newline) exposed that o3 doesn't reliably know `$()` strips trailing newlines. Finding #2 (undefined GitHub Actions outputs) showed it confuses empty string with `"null"`. Finding #3 (`_core$` regex) was a regex anchor misunderstanding. All three were quickly verified with one-liner shell tests.
4. **Thread-level triage discipline** — Every thread got a comment and resolution across all 14 threads. No orphaned discussions.

### What Was Surprising

1. **o3 code-reviewer verdict was FAIL on false premises** — 3 of 7 findings (including the #1 "blocker") were false positives about basic shell/GitHub Actions behavior. The evaluator's overall verdict can't be trusted without human triage. This reinforces the need for a structured triage step in the evaluator gate.
2. **Session crash recovery was clean** — Picking up from the crashed session required only reading the transcript and verifying git state. All artifacts (review files, task spec) were written but uncommitted, so nothing was lost. The gated workflow's commit discipline made recovery straightforward.
3. **`review_implementation.sh` doesn't work with committed code** — This was a known limitation but became blocking in practice during Phase 8. The workaround (manual API calls with `gh pr diff`) worked but was ad-hoc. KIT-0025 now captures the fix.

### What Should Change

1. **Evaluator triage must be a formal sub-step** — The code-reviewer evaluator can produce false positives that flip the verdict. Phase 8 should include: (a) run evaluator, (b) triage each finding with verification, (c) write triaged verdict. The raw verdict alone is not a reliable gate signal.
2. **PR-based evaluator runner (KIT-0025)** — `review_implementation.sh` using `git diff` (unstaged) is incompatible with the gated workflow where code is committed before evaluation. `gh pr diff` is the right input source. Task spec is written and in backlog.
3. **Evaluator knowledge gaps should be documented** — o3's false positives about `$()` newline stripping and GitHub Actions output semantics are predictable. A "known evaluator blind spots" section in the evaluator config could help future triage (e.g., "shell: $() strips trailing newlines — verify before accepting newline-related findings").

### Permission Prompts Hit

None. The wrap-up session only used git, gh, and file operations — all within existing allow patterns.

### Process Actions Taken

- [x] Evaluator reviews saved to `.kit/context/reviews/`
- [x] KIT-0025 task spec created in backlog
- [x] PR merged
- [x] Task moved to `5-done`
- [ ] Add evaluator triage as formal sub-step in Phase 8 (workflow update — separate chore task)
- [ ] Document known evaluator blind spots in `.kit/adversarial/` config
- [ ] Promote KIT-0025 to `2-todo` when ready for implementation

## KIT-0035 — Dev-env & Evaluator-Workflow Hardening (PRs #72 + #73)

**Date**: 2026-07-13 (session ran 2026-07-05/06; PRs merged 2026-07-13)
**Agent**: feature-developer-f5
**Mode**: single-repo
**Scorecard**: 2 threads, 0 regressions, 3 fix rounds, 7 commits (4 on #72, 3 on #73)

### What Worked

1. **The F3 rule paid for itself on its own PRs** — both PRs ran the
   evaluator trio BEFORE opening (dogfooding the ordering rule PR 1
   introduces). PR #72 — six items across 8 files — came back from its
   first bot round with ZERO threads and a CodeRabbit APPROVED. Compare
   KIT-0032's four post-open bot rounds on a single doc file. The
   round-collapse effect is real and measurable.
2. **Verify-before-believing killed four false evaluator claims in
   ~2 minutes each** — o3's "set -e hard-exits when Black missing"
   (pipeline ends in `head -1`, exit 0 — tested), claude-code's
   "extracts `26` not `26.3.1`" (grep -o is leftmost-longest — tested
   live), and the sed-range termination claim twice. Every decline
   carries a pasted repro in the review record, which made the
   CodeRabbit re-litigation (see below) a copy-paste reply.
3. **Testing hardened greps against live CLI output caught nothing —
   but the evaluator round caught my own bypass** — the first draft of
   the marketplace-source pattern (`github.*movito/...`) passed all my
   live-output tests yet matched `Directory
   (/Users/alice/github/movito/agentive-skills)`. Both PR-2 evaluators
   converged on it independently. Lesson: test the *rejection* cases,
   not just the acceptance cases; live output only exercises the happy
   path.
4. **The two-PR/one-task split worked without bundle machinery** — PR 2
   deliberately never touched the shared evaluator-record file;
   PR 2's disposition was appended to the record on PR 1's branch.
   No merge conflict, preflight Gates 5–7 keyed cleanly to the single
   task ID once #72 merged first (planner's handoff called this shape
   in advance).
5. **Sequential-over-stacked was the right call** — STACKED-PR-WORKFLOW's
   "stack only on code dependency" rule plus the CodeRabbit-skips-
   non-default-base gotcha made the decision mechanical. PR 2 got a full
   CodeRabbit review it would have missed as a stacked PR, and that
   review produced the one real post-open fix of the session.

### What Was Surprising

1. **Three independent reviewers made the identical false sed claim** —
   o3, Gemini fast-v2, and CodeRabbit all asserted `sed -n
   '/^## Provenance/,/^## /p'` terminates on its own start line (POSIX
   sed searches the end address from the line AFTER the addr1 match).
   Model-diverse review does not protect against shared training-data
   folklore about classic tools. The pasted BSD-sed repro in the review
   record was the antidote — the CodeRabbit decline took one reply.
2. **CodeRabbit's one real finding was a refinement of the evaluators'
   own fix** — the end-anchoring gap (`agentive-skills-beta` passing a
   prefix match) existed only because the evaluator round had just
   introduced the Source-anchored pattern. Fresh-code yield again: every
   real external finding this session was in code written the same
   session (consistent with KIT-0040's observation).
3. **Preflight on PR 2's branch "fails" Gates 5–7 by design** — the
   task-level artifacts live on PR 1's branch, so a two-PR task shows
   3 spurious gate failures on the second branch until the first
   merges. Not a bug, but the output reads like one (KIT-0042's
   bundle-aware FAIL message should name this).
4. **Both bots gated PR 2 as "No code changes — bot review not
   required"** (preflight Gates 2/3 detail) yet CodeRabbit reviewed it
   anyway and found the only real issue — in a `.md` file. The
   "doc-only" heuristic and actual bot behavior disagree; good thing,
   since runbook markdown IS executable-by-agent code.

### What Should Change

1. **Grep-hardening tasks should enumerate rejection cases up front** —
   the KIT-0035 handoff said "run the hardened greps against real
   current output", which only tests acceptance. A one-line addition to
   that test approach ("and against the documented bypass/negative
   cases") would have caught the Directory-path bypass before the
   evaluators did.
2. **Record the sed/awk folklore declines somewhere findable** — the
   same false claim cost three triage cycles across two PRs. A short
   "empirically disproven reviewer claims" section in patterns.yml or
   REVIEW-INSIGHTS.md (planner already extracts there) would let the
   next agent decline-by-reference. (Planner's cfa0e47 knowledge
   extraction may already cover this — verify before adding.)
3. **KIT-0042 should make preflight name the two-PR shape in its FAIL
   detail** — Gates 5–7 on a second branch should say "artifacts may
   live on the sibling PR's branch for multi-PR tasks" instead of a
   bare "No evaluator review found". (Already promoted by the planner;
   this retro just adds the concrete FAIL-text evidence.)
4. **Pre-commit hook auto-fixes abort commits silently in long
   output** — twice this session a commit "succeeded" visually (pytest
   tail) but was aborted by trailing-whitespace fixes to appended log
   files; caught only by checking `git log` afterwards. The commit
   protocol could add a standard "verify HEAD moved" step after any
   commit whose staged set includes generated/appended markdown.

### Permission Prompts Hit

None.

### Process Actions Taken

- [ ] Add "test the rejection cases" line to grep-hardening test
      guidance (candidate home: TESTING-WORKFLOW.md or the task-spec
      test-approach template)
- [ ] Verify REVIEW-INSIGHTS.md covers the sed-range folklore decline;
      add if missing
- [ ] Feed the Gates 5–7 two-PR FAIL-text evidence into KIT-0042's spec
- [ ] Consider "verify HEAD moved" step in COMMIT-PROTOCOL.md for
      commits staging appended/generated markdown
- [x] Task moved to 5-done by planner (cfa0e47) with knowledge
      extraction to REVIEW-INSIGHTS.md

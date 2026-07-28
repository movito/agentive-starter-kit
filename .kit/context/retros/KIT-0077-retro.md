## KIT-0077 — Dedup cleanup: context archive, dispatch retirement, doc archival (PR #101)

**Date**: 2026-07-28
**Agent**: feature-developer (canonical, `claude-opus-5`)
**Mode**: single-repo
**Merged**: `c39f1bb`
**Scorecard**: 3 threads, 3 regressions, 4 fix rounds, 7 commits

> Operator context: this task was run on opus-5 as a deliberate
> model-comparison against the fable-5 baselines (KIT-0073: 4 threads /
> 1 regression / 2 rounds; KIT-0076: 3/1/1). See "What Was Surprising" #1
> for the honest read — the thread count is comparable, the *regression*
> count is worse, and all three regressions were self-inflicted while
> fixing something else.

### What Worked

1. **Reading the consumer before trusting the move.** The Phase-2 check
   "does anything copy this directory?" found `engine-export.sh`'s
   `find .kit/context/ -maxdepth 1` *before* a single file moved. That one
   grep is the difference between this PR and one that ships 100 handoffs
   into every new project. The sibling engine (`engine-materials.sh`, a
   depth-1 rsync exclude) then fell out of the same question — and its
   leak was caught by an existing guard test that the full suite ran
   unprompted.

2. **Sabotage-verifying every new guard.** Both new tests were checked by
   deleting the fix and confirming the test fails. This immediately
   exposed that the export guard was **vacuous** (below, Surprising #2).
   A guard that has never been observed failing is a guess; two minutes
   of sabotage converts it into evidence.

3. **Refuting findings from the tree, not from confidence.** Three of the
   seven evaluator/bot findings were wrong, and each was closed with a
   command rather than an opinion: `grep -c` for markdown links in
   `SETUP-GUIDE.md` (zero — so the `../../` "fix" would have broken the
   file's repo-relative convention), and `git log` on `21fbfc4` showing
   the release task is what bumps `pyproject`. CodeRabbit accepted both
   refutations and moved to APPROVED.

4. **F4 resolved by citation, not judgment.** The dedup report flagged the
   two review templates as a possible duplicate and asked for an operator
   decision. Two greps settled it: each template has exactly one live
   consumer and they do different jobs. The verdict plus both roles now
   live in `.kit/context/README.md` so the question cannot recur — closing
   an operator question is cheaper than deferring it.

### What Was Surprising

1. **Every regression this session was self-inflicted during a fix.** Not
   one came from the original implementation. The `.gitignore` removal was
   collateral from executing the handoff literally; the CHANGELOG
   truncation was collateral from fixing the `.gitignore` removal. The
   failure mode of this task was not "wrote bad code" but "edited
   correctly-working prose adjacent to what I was fixing and did not
   re-read the result." That is the single most useful number for the
   opus-5/fable-5 comparison: **thread count comparable, regression
   density worse, and concentrated entirely in the repair loop.**

2. **A guard test passed while sabotaged — because the engine reads
   `git archive HEAD`, not the working tree.** With the archive moves
   staged but uncommitted, `.kit/context/archive/` did not exist in any
   export, so the test could not fail no matter what. It only became
   meaningful after the commit (re-verified: 92 files leak when
   sabotaged). Any test that exercises `engine-export.sh` is testing
   **HEAD**, not what is on disk — an easy way to ship a permanently green
   no-op test.

3. **The retired tool was still installed and still running.** The premise
   for removing the `.dispatch/` gitignore entries was that the guarded
   emits I had deliberately *kept* in `scripts/core/` were dead no-ops
   here. Then my own preflight run wrote `.dispatch/bus.jsonl`:
   `dispatch` lives at
   `/Library/Frameworks/Python.framework/Versions/3.11/bin/dispatch`,
   on PATH regardless of venv. "The operator retired it" meant the
   *workflow* no longer runs on it — not that the CLI is gone. Retiring an
   integration has two separable surfaces: **adoption** (config,
   installer, instructions) and **runtime debris** (which keeps happening).

4. **`gh pr checks` reported `pass` twice while CodeRabbit had filed
   CHANGES_REQUESTED.** A fourth face of KIT-0062. Both were found only by
   querying `reviewThreads` via GraphQL. Preflight Gate 4 catches this
   correctly; the exposure is the *agent* who eyeballs `gh pr checks`,
   sees green, and proceeds.

### What Should Change

1. **Widen `displayed_commands_are_contracts` from commands to printed
   claims.** The pattern currently covers "any remedy/recovery command a
   tool PRINTS." The `/wrap-up` finding was a printed *summary* asserting
   a retro file that may not exist — same family (an emitted artifact
   making an unverified claim), outside the current wording. Proposed
   addition: *any line a tool prints as fact is a claim; verify it before
   printing, or print the failure.*

2. **Add a patterns.yml entry for depth-anchored sweeps.** New class, seen
   twice in one hour in two different engines: `find -maxdepth 1` and
   rsync `--exclude='context/[A-Z]*-NNNN*'` both silently stop covering a
   tree the moment you add a subdirectory. Proposed rule: *when adding a
   subdirectory under a path that any copy/scrub/exclude logic touches,
   grep every engine for that path and check whether its matcher is
   depth-anchored.* Both fixes and both guards from this PR are the
   worked example.

3. **Note the `git archive HEAD` caveat in TESTING-WORKFLOW.md.** Anyone
   writing a test against `engine-export.sh` needs to know it exports
   HEAD, so uncommitted fixtures are invisible and the test can be
   green-by-construction. Pair it with the standing rule: sabotage-verify
   any new guard before trusting it.

4. **Teach the bot-triage skill that `gh pr checks` is not review state.**
   It should say explicitly: check-run status and review verdict are
   different objects; query `reviewThreads` for the truth. Twice this
   session the check said `pass` over a CHANGES_REQUESTED review.

5. **Handoffs that say "remove X" should say what evidence would falsify
   it.** The instruction to drop the `.dispatch/` gitignore lines was
   correct-sounding and wrong, and I executed it without asking what
   would still write to that path. For retirement tasks, the spec should
   name the runtime surface separately from the adoption surface.

### Permission Prompts Hit

None. No command was blocked or denied this session.

### Process Actions Taken

- [ ] Widen `displayed_commands_are_contracts` in `patterns.yml` to cover printed *claims*, not only printed commands (Should Change #1)
- [ ] Add a `depth_anchored_sweeps` entry to `patterns.yml`, citing the two KIT-0077 engine leaks (Should Change #2)
- [ ] Add the `git archive HEAD` ≠ working-tree caveat to `TESTING-WORKFLOW.md`, with the sabotage-verify rule (Should Change #3)
- [ ] Add "check status ≠ review verdict; query `reviewThreads`" to the `bot-triage` skill (Should Change #4, KIT-0062 fourth face)
- [ ] Consider a spec convention for retirement tasks: separate the *adoption* surface from the *runtime* surface (Should Change #5)
- [ ] File a follow-up for the 6 pre-existing dangling doc references found by the link sweep and deliberately not fixed (listed in `.kit/context/reviews/KIT-0077-evaluator-review.md`)
- [ ] Decide whether `KIT-0030`'s five archived artifacts should return to the flat listing when the downstream pass unblocks it

### Incident Closure

Three incidents, three closures:

1. **`dispatch` CLI present while assumed absent** (Surprising #3) →
   **doctor check**. The kit's shipped `scripts/core/` scripts emit to
   `dispatch` whenever it is on PATH, so whether it is present is a real
   environment fact that changes behavior. Proposed: a
   `scripts/core/doctor.d/` check reporting `dispatch` presence and, if
   present, that `.dispatch/bus.jsonl` is gitignored — citing KIT-0077 in
   the header comment. Cheap (`command -v`), and it would have refuted my
   false premise before I acted on it.

2. **Export-path guard vacuous pre-commit** (Surprising #2) →
   **triage-guide entry**. The symptom (a new export test that passes with
   its fix removed) is only diagnosable when writing such a test. The
   explanation already landed in the new test's own docstring
   (`test_new_export_carries_no_planning_corpus`); Process Action #3
   propagates it to `TESTING-WORKFLOW.md` where test authors look.

3. **`gh pr checks` masking a CHANGES_REQUESTED review** (Surprising #4) →
   **triage-guide entry**, and a fourth data point for KIT-0062. Preflight
   Gate 4 already detects it, so no new check is warranted; the gap is
   agent-facing guidance, addressed by Process Action #4.

## KIT-0040 — KIT-0034 Retro Follow-ups: kit_markers fixes, preflight harness, move-metadata sync (PR #70)

**Date**: 2026-07-05
**Agent**: feature-developer-f5
**Mode**: single-repo
**Scorecard**: 2 threads, 0 regressions, 2 fix rounds, 7 commits

### What Worked

1. **TDD on regexes caught the design before the code** — writing the 5
   F3 regression tests first (prose mention, whitespace drift,
   beyond-tolerance drift, missing colon, drifted round-trip) forced the
   "two consistent detection paths" design up front: tolerant parse
   regexes (`[ \t]` only, never `\s`) plus a deliberately *looser*
   line-anchored malformed detector, so nothing falls between parse-OK
   (preserve) and detector-hit (fail fast). All 5 failed red, then green.
2. **Mutation-testing the F1 harness proved it earns its keep** —
   flipping `CI_ANY_FAILED_RUN=true→false` in `preflight-check.sh` made
   `test_completed_failure_beats_running_sibling` fail (FAIL became
   PENDING) in 0.5 s, then reverted clean. Ten minutes of work turned
   "the harness passes" into "the harness detects gate-logic breakage."
3. **Stubbing `sleep` and `dispatch` alongside `gh`** — the poll-loop
   scenarios (gh-error, empty-fetch) would have cost 10 s each through
   `CI_POLL_DELAY`; a no-op `sleep` on PATH made them instant without
   touching the script (N2), and the no-op `dispatch` guaranteed no
   fire-and-forget events could leak from tests (N1). Module-scoping the
   git fixture then cut the module from 5.3 s to 1.8 s — inside the
   pre-commit fast-hook budget without a `slow` marker.
4. **Verify-before-believing killed 2 of 3 o3 claims in one python
   heredoc** — the "EOF without trailing newline breaks parsing" and
   "regex clobbers non-path prose" findings were both empirically false
   (the `\r?\n` is the body/marker separator; the pattern requires the
   full `.kit/tasks/<folder>/` prefix). Same o3 failure mode as KIT-0034;
   ~2 minutes of checking prevented two pointless "fixes".
5. **F2 dogfooded itself twice during its own PR** — the repair path
   (`project move` re-run) fixed KIT-0040's own drifted handoff paths
   from the pre-fix `project start`, and the in-review move rewrote
   metadata in the same operation. Zero stale-path bot nitpicks this PR,
   versus a guaranteed CodeRabbit round on every previous task.

### What Was Surprising

1. **BugBot and the fast evaluator found the same new bug
   independently** — the `\b`-after-hyphenated-name prefix collision in
   `_begin_marker_line_re` (my own new code) was flagged by
   code-reviewer-fast-v2 and, on the next push's round, by BugBot on PR
   #70 — before I'd seen the BugBot thread. The fix (`(?!-?\w)` name
   terminator) was already pushed when the thread appeared, and BugBot
   auto-resolved it. Two independent detectors converging on a subtle
   regex bug is strong evidence it was real, not a nitpick.
2. **CodeRabbit took ~25 minutes for round 1** — two short polls
   (270s/240s) both came back pending; the 1200 s back-off was the right
   move. Rounds 2–3 were much faster (~5 min). The two-short-then-long
   polling guidance in the agent spec matched reality exactly.
3. **The evaluator-vs-bot overlap is now measurable** — of 8 total
   external findings (4 fast-v2, 3 o3, 1 CodeRabbit, 1 BugBot, with the
   fast-v2/BugBot overlap), exactly 2 were real. Both were in code
   written *this session*, none in the pre-existing code under review.
   The gauntlet works, but its yield is concentrated on fresh code.
4. **`gh pr checks` reports the *previous* head's checks immediately
   after a push** — right after pushing `0436e87` the output still
   showed all-green for `dca46c8`. Harmless here (the GraphQL thread
   query disambiguated), but worth remembering: a green `pr checks`
   snapshot taken seconds after a push is stale, not proof.

### What Should Change

1. **`prepare-review-input.sh` should mention `ADVERSARIAL_UNATTENDED`**
   — its "Next steps" output lists the three evaluator commands, but in
   a non-TTY agent session a >50k-token input auto-cancels unless
   `ADVERSARIAL_UNATTENDED=1` is exported. One line in the script's
   next-steps output (or auto-setting it when stdout is not a TTY) saves
   every future agent one failed evaluator invocation.
2. **Evaluator naming: v2 variants are discoverable only by `ls`** — the
   agent spec says "prefer -v2 where installed," but finding that
   `code-reviewer-fast-v2` exists while `code-reviewer` has no v2 took a
   directory listing of `.adversarial/evaluators/*/`. An
   `adversarial list` command or a note in the code-review-evaluator
   skill would make the preference executable without spelunking.
3. **Codify the marker-in-fenced-code limitation as a known
   non-goal** — both evaluators flagged that a literal BEGIN-marker line
   inside a fenced code sample (with no parseable region for that name)
   fail-fast aborts merge. Declined twice with the same reasoning (loud
   abort beats silent clobber; markdown-fence parsing is out of scope
   for a stdlib helper). Worth one sentence in
   `.kit/docs/KIT-MIGRATION-PLAYBOOK.md` or the bootstrap docs so the
   next reviewer/evaluator round doesn't re-litigate it.
4. **The stub-`gh` pattern is ready to generalize** — the harness
   (PATH-stub serving canned payloads keyed by argv shape + cleaned env
   + module-scoped fixture) is documented in `test_preflight_check.py`'s
   docstring, but `verify-ci.sh`, `check-bots.sh`, and
   `wait-for-bots.sh` are still untested shell+gh scripts. A follow-up
   task could lift the stub into a shared `tests/` helper and cover at
   least `verify-ci.sh`.

### Permission Prompts Hit

None.

### Process Actions Taken

- [ ] Make `prepare-review-input.sh` surface `ADVERSARIAL_UNATTENDED=1`
      in its next-steps output (or auto-set on non-TTY)
- [ ] Add v2-variant discovery to the code-review-evaluator skill (or an
      `adversarial list` pointer)
- [ ] Document the fenced-code-marker fail-fast as a known non-goal in
      the bootstrap/migration docs
- [ ] Consider follow-up task: generalize the stub-`gh` harness to
      `verify-ci.sh` / `check-bots.sh` / `wait-for-bots.sh`
- [x] Planner: after PR #70 merges, move KIT-0040 to 5-done (`project
      complete` now syncs the metadata automatically) — done 2026-07-05;
      the metadata sync rewrote `agent-handoffs.json` and the handoff
      file paths in the same operation, as designed

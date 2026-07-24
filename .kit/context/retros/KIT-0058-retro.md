## KIT-0058 — Visible Config Home + /setup-preset (PR #91)

**Date**: 2026-07-23
**Agent**: feature-developer-f5
**Mode**: single-repo
**Scorecard**: 2 threads, 0 regressions, 1 bot fix round (1 evaluator
fix round, pre-PR), 3 commits + post-retro fix round

> **Post-retro correction (same day)**: BugBot was NOT skipping — its
> check-runs said "skipping" on the first three commits, then it
> reviewed the retro commit and filed 1 Medium (doctor anchors the
> config home to the diagnosed checkout, not the kit clone).
> Dispositioned deliberate-with-honest-naming (a consumer checkout
> cannot compute the kit's local path; sibling layout is the
> agreement condition; anchor + override now named in every doctor
> output line + README bullet). Scorecard above updated (was: 1
> thread, 0 bot fix rounds, "BugBot skipped"). The Gate 3 honesty
> flag (What Was Surprising #3) gains a second face: a "skipping"
> conclusion is apparently also NON-TERMINAL — BugBot can still
> review later, so treating it as a final state was itself wrong.

### What Worked

1. **Evaluator-before-PR ordering paid off again** — the trio
   (fast/o3/claude-code) surfaced 4 fixable issues (tilde expansion in
   all three resolvers, `/setup-preset` rev-parse guidance, `gh` `--`
   separator, atomic seeding) that were fixed in commit `cd01110`
   BEFORE the PR opened. Result: exactly ONE bot thread, zero
   bot-driven code rounds. Third consecutive validation of KIT-0035 F3.
2. **Empirical refutation beats argument, twice** — o3's "gh rejects
   full remote URLs" (rated high-risk) died to three live
   `gh repo view` calls (HTTPS, HTTPS+.git, scp-style SSH all work);
   CodeRabbit's committable suggestion died to a 5-line scratch script
   proving the heredoc swallows the chained `mv` (syntax error). Both
   refutations are now artifacts (review record + PR thread), not
   assertions.
3. **The door↔doctor equivalence pin without imports** —
   `test_door_and_doctor_agree_on_the_path` compares the sourced bash
   `config_home` against the Python `_config_home` via doctor's
   "no preset found at <path>" INFO line, avoiding importlib gymnastics
   on the extensionless `scripts/core/project`. Cheap, and it directly
   enforces the handoff's "two can never disagree" property.
4. **Surgical characterization masking** — when the new config-home
   doctor line broke `test_no_preset_gives_the_stranger_path`
   byte-identity, the fix masked ONLY that one environment-reporting
   line (+ the count summary) instead of weakening the whole
   comparison. The door's own chrome stays byte-pinned.
5. **`prepare-review-input.sh --format full` worked first try** and
   even printed the exact `echo y | ADVERSARIAL_UNATTENDED=1` runbook
   in its output — the KIT-0056-era polish is compounding.

### What Was Surprising

1. **The demo target was missing the new doctor check — because
   `git archive` exports tracked files only.** The one-button demo ran
   before the first commit, so the exported target's `doctor.d/` lacked
   the uncommitted `90-config-home.sh` and its doctor tail silently
   showed 9 checks instead of 10. Diagnosed in one minute, but the
   class is real: a door demo from a dirty/uncommitted kit tree
   exercises HEAD, not the working tree, and nothing says so.
2. **A CodeRabbit committable suggestion was a bash syntax error** —
   first observed instance. Auto-applying it would have broken
   `seed_config_home` (heredoc body swallows the `&&`-chained `mv` and
   `then` lines). Committable ≠ compilable.
3. **Preflight Gate 3 reports BugBot conclusion "skipping" as
   `PASS:check-run passed, no findings`** — reads as reviewed-clean
   when BugBot explicitly declined to review PR #91. Honest would be a
   SKIP-flavored PASS naming the skip (the exact P5 gate-honesty
   principle, one gate over).
4. **o3 claimed a missing test that existed** —
   `test_empty_override_falls_through_to_derivation` was in the same
   diff o3 reviewed ("bash side not covered"). The
   verdict-carries-no-signal rule held: 2 real / 2 refuted / 1
   pre-existing from a FAIL verdict.

### What Should Change

1. **Gate 3 should name a skipped BugBot run** — conclusion
   `skipping`/`skipped` on the check-run should yield
   `PASS:BugBot skipped this PR (…)` or a SKIP verdict, not "passed,
   no findings". Fold into KIT-0062 (bot review scope) rather than a
   new task.
2. **bot-triage skill: syntax-verify committable shell suggestions
   before applying** — one line in the skill: any committable
   suggestion touching shell (especially heredocs, quoting, or
   redirects) gets a scratch `bash -n`/execution test first; paste the
   result into the thread when declining.
3. **Door could warn when exporting from a dirty kit tree** — `--new`
   ships HEAD (git archive), so uncommitted kit changes silently don't
   ship. A one-line notice ("kit tree has uncommitted changes — the
   export ships the last commit") in the export path would close the
   demo-confusion class. Small; planner may fold into a backlog task.
4. **rm-rf allowlist still owed** (standing operator item) — hit again
   this session on demo-fixture cleanup in `/tmp` (worked around with
   uniquely-named dirs, which also leaves `/tmp/kit-0058-demo-1`
   behind for the operator to sweep).

### Permission Prompts Hit

1. `rm -rf /tmp/kit-0058-demo && mkdir …` (demo fixture reset) —
   denied; worked around immediately with a fresh uniquely-named dir,
   so ~zero time lost. This is the already-tracked missing allowlist
   entry for `/tmp/` (operator reminder fired at arc-end, still open).
   No other prompts; the session's git/gh/pytest surface was fully
   covered.

### Process Actions Taken

- [ ] Fold Gate 3 skipped-BugBot honesty into KIT-0062's scope
  (planner)
- [ ] Add the syntax-verify-committable-suggestions line to the
  bot-triage skill (planner or next process PR)
- [ ] Decide on the dirty-tree export notice for the door (backlog
  candidate; cite this retro)
- [ ] Operator: add rm-rf allowlist entries (/tmp/ and
  ~/Github/ask-worktrees/) — standing since KIT-0057 arc-end; sweep
  `/tmp/kit-0058-demo-1` when convenient
- [ ] Planner closeout: merge PR #91 → `project complete KIT-0058`,
  remove worktree, delete branch; then the operator's `/setup-preset`
  run is unblocked

### Incident Closure

1. **`git archive` ships HEAD, not the working tree** (demo target
   missing uncommitted doctor check) — **triage-guide entry**: this
   retro documents symptom→cause (doctor tail shows N-1 checks →
   export ran from a kit tree with uncommitted files); the What Should
   Change #3 notice is the structural fix if the planner adopts it.
   Not a doctor.d candidate: the condition lives in the SOURCE tree at
   export time, not in the installed environment doctor inspects.
2. **BugBot check-run conclusion "skipping" masked as reviewed-clean
   by Gate 3** — **triage-guide entry now, gate fix via KIT-0062**:
   symptom is a PASS reading "no findings" with zero BugBot review
   activity on the PR; cause is the conclusion value not being
   distinguished. Preflight is the owner (not doctor.d), so the
   closure is the KIT-0062 scope amendment above.
3. **CodeRabbit committable suggestion syntactically invalid** —
   **triage-guide entry**: bot-triage skill amendment (Process Action
   2); the empirical-test-before-apply rule is the reusable closure.
   No environment/doctor surface involved.

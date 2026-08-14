## KIT-0104 — Ship the door in the package, PR 3 of 3: the prose sweep + KIT-0094 passenger (PR #131)

**Date**: 2026-08-14
**Agent**: feature-developer-f5
**Mode**: single-repo
**Scorecard**: 8 threads, 1 regression, 1 fix round, 6 commits
<!-- PR 3 only. Task aggregate across the series (planner totals):
     PR 1 (#129) + PR 2 (#130, 8 threads/3 rounds per its starter) +
     PR 3 (#131, 8 threads/1 round). -->

### What Worked

1. **Land the gate before the churn** — the handoff's "lint config
   EARLY" ordering meant commits 1–2 (config, sweep) preceded every
   prose edit, so all later commits passed the gate they installed.
   The acceptance criterion was then *observed*, not argued:
   CodeRabbit's round on a 110-file markdown-heavy PR produced ZERO
   markdown-style threads — all 7 of its findings were content. The
   KIT-0094 bet (own the lint, retire the nit class) paid out on its
   own PR.
2. **Falsify-once beat evaluator opinion for the behavioral hunk** —
   the only behavior in the PR (pre-commit gate) was proven by
   planting a bare fence (hook exit 1) and restoring (pass), which
   is stronger evidence than any diff-reading. Paired with fast-only
   trio per the prose-sweep exception, Gate 5 cost ~$0.01 and the
   FAIL verdict was correctly refuted against the tree in minutes
   (the "conflicting ADR-0021 pair" carries a literal `Supersedes:`
   header — third consecutive prose-sweep where the evaluator's
   verdict was noise and tree-grounding was the real filter).
3. **Empirical check of the hook mechanics prevented a footgun** —
   before wiring pre-commit, a 2-minute experiment showed
   markdownlint-cli2 CLI paths EXTEND config globs and BYPASS
   `ignores` (an explicitly-passed excluded task spec got linted).
   `pass_filenames: false` + tree-wide run (~2 s) was chosen from
   evidence, not the hook's README default — a filename-passing hook
   would have false-failed every task-bookkeeping commit.
4. **Autofix + verify-by-sorted-diff for the CHANGELOG merge** — the
   MD024 fix (merging 10 duplicate section headings) was verified by
   diffing sorted non-blank lines old-vs-new: exactly the 10 heading
   lines vanished, zero content lines. Cheap proof that a 366-line
   structural diff was content-preserving.
5. **Reading the door's source before writing its docs** — F5 claims
   were pulled from `door/__init__.py` (`note_env_keys`, target-parent
   anchor) and the live `--help`, which caught two stale claims the
   spec didn't list (adopt-copies caveat, kit-clone `.env` carryover)
   and let me refute CodeRabbit's "should the door prompt for keys?"
   thread with the recorded PR 1 decision.

### What Was Surprising

1. **The autofix renumbered lists into semantic changes** —
   markdownlint `--fix` on MD029 turned "6./7." continuation steps
   into "1./1." (babysit-pr.md Phase 4, bootstrap.md Step 6),
   changing rendered numbering. The right fix was structural
   (indent the fences INTO the list items) and had to be done by
   hand. Autofix output needs a semantic pass, not just a lint pass.
2. **BugBot reviewed while its check said "skipping"** — the
   check-run stayed `skipping` the entire session while BugBot
   posted a Medium-severity thread (KIT-0062's both-ways lying,
   fifth face: skipping-yet-reviewing). Threads were the truth, as
   the handoff warned.
3. **CodeRabbit took ~35 min on the large diff** — round 1 on the
   110-file PR far exceeded the usual cadence; the two-quiet-polls →
   1200 s backoff rule handled it without burn. Round 2 (6-file
   incremental) landed in under 10 min.
4. **The sweep surfaced a pre-existing off-by-one in a printed
   recipe** — setup-preset's config-home recipe ("take the parent of
   the `--git-common-dir` path") has computed `<clone>` instead of
   `<projects-parent>` since KIT-0058; nobody's preset ever loaded
   from where that doc pointed. CodeRabbit caught it only because
   the surrounding paragraph entered the diff. Fixed and verified
   live from this worktree.

### What Should Change

1. **The MD029/list-continuation hazard belongs in the bot-triage /
   patterns knowledge** — "markdownlint --fix renumbers continued
   lists; repair structurally by indenting the interrupting block
   into the list item" is a class, and the next doc sweep will hit
   it. Suggest a `patterns.yml` entry (autofix_needs_semantic_pass)
   citing babysit-pr.md/bootstrap.md.
2. **Printed multi-step recipes should get the falsify-once
   treatment** — the KIT-0058 config-home recipe shipped wrong and
   stayed wrong for weeks because it was never executed as printed.
   `displayed_commands_are_contracts` already exists; the delta is:
   when WRITING a recipe, run it once in the session and paste the
   output next to the claim (I did this for the corrected recipe;
   the original never was).
3. **Plugin Drift Guard needs a decided posture for content-touching
   PRs** — it is red on main since 2026-08-12 and every PR touching
   `.claude/` inherits + widens the red. Merging over a red required
   documenting precedent by hand (PR comment + starter section).
   Either the guard becomes advisory-on-PRs (required only on
   main/release), or the release cadence keeps it green. Planner
   call; the current state trains people to ignore a red check —
   which is how KIT-0062 class incidents start.
4. **Retro filename for multi-PR tasks** — this file is
   `KIT-0104-pr3-retro.md` because PR 1/2 sessions were separate;
   the template assumes one retro per task. Worked fine, but the
   planner's archive sweep should know the per-PR pattern exists.

### Permission Prompts Hit

None. The workflow ran end-to-end (git, gh, npx markdownlint-cli2,
pytest, pre-commit, evaluator via `bash -c` + `.env`) without a
single permission stall.

### Process Actions Taken

- [ ] Add `autofix_needs_semantic_pass` (or extend an existing entry)
      to `.kit/context/patterns.yml`: lint autofix renumbers
      continued lists; repair structurally (planner)
- [ ] Extend `displayed_commands_are_contracts` guidance: recipes are
      executed once at authoring time, output pasted alongside
      (planner; evidence: KIT-0058 config-home recipe wrong since
      authoring)
- [ ] Decide Plugin Drift Guard posture: advisory-on-PR vs
      keep-required + release cadence (planner; then cut the plugin
      release per KIT-0096 so the guard greens)
- [ ] Record KIT-0062 fifth face in the bot-triage skill if not
      already covered: BugBot check `skipping` while its review
      thread is live
- [ ] KIT-0094 completion: acceptance evidence in the PR 3 review
      starter (zero markdown-style threads observed); move the task
      when KIT-0104 closes

### Incident Closure

1. **markdownlint-cli2 CLI paths bypass config `ignores` and extend
   globs** — *not-checkable note*: recorded where the decision
   lives, in `.pre-commit-config.yaml`'s hook comment block (the
   `pass_filenames: false` rationale names the behavior and the
   empirical verification). A doctor check would be testing a
   third-party CLI's argument semantics on every run — the config
   comment at the single point of use is the cheap, correct home.
2. **BugBot check-run `skipping` while a review thread was live** —
   *triage-guide entry*: this is KIT-0062's documented class
   (statuses lie both ways; threads are the truth) already carried
   in the bot-triage skill and both fd agents' Phase 7; this session
   adds the `skipping`-yet-reviewing face to the retro record. No
   new surface needed — the existing rule ("verify via threads, not
   status") diagnosed it correctly in real time.
3. **Plugin Drift Guard red inherited from main by every
   `.claude/`-touching PR** — *ESCALATED — awaiting planner
   classification*: (a) the guard fails on all PRs and main pushes
   since 2026-08-12 because the published plugin lags the tree, and
   PRs #129/#130/#131 each merged/passed over it with hand-written
   justification; (b) a doctor check doesn't fit (this is CI
   posture, not local environment), a not-checkable note doesn't fit
   (it IS checked — the check is just permanently red between
   releases), a triage-guide entry alone would institutionalize
   ignoring a required-looking red check; (c) question for the
   planner: **should the drift guard be advisory on PRs (required
   only on main/release-cut), or stay required with a release
   cadence that keeps it green?** The answer converts this to either
   a workflow-file change or a KIT-0096 cadence rule.

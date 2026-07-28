## KIT-0076 — Cut 0.9.0: execute the pinned removals, release the lean kit (PR #100)

**Date**: 2026-07-28
**Agent**: feature-developer-f5
**Mode**: single-repo
**Scorecard**: 3 threads, 1 regression, 1 fix round, 9 commits

### What Worked

1. **Read-everything-first, then one pass of edits** — reading all
   three removal specs, every pinning test file, and the door's full
   `LEGACY_SHIM` usage map (9 excision points) before touching
   anything meant zero mid-implementation surprises: all 58
   retargeted `test_bootstrap_shapes.py` tests passed on the FIRST
   run after the rewrite, including every re-pinned exit code.
2. **Characterize-first on the door re-pin paid off precisely** —
   checking `reject_flaglike`'s empty-value comment
   (`bootstrap:339-340`) before porting revealed the two
   trailing-flag shim tests genuinely don't map to the door (empty
   value falls through to defaults), turning a potential
   guess-and-fail cycle into a documented deliberate drop that
   CodeRabbit later probed and accepted.
3. **Evaluator-before-PR + fast-only rule for deletion-heavy diffs**
   — the trio would have cost ~$0.40 for findings the fast gate
   produced at $0.01: 1 refuted-in-10-seconds injection claim
   (engine-export quotes everywhere; env→python JSON path), 2
   declined test-gap notes. Zero evaluator-driven churn on the PR.
4. **One batched fix commit for the bot round** — all 3 CodeRabbit
   findings (2 doc-consistency + 1 test guard) landed in `5c242d2`;
   round 2 came back clean. One round, not three.
5. **Keeping test FILENAMES while rewriting contents** — retargeting
   `test_bootstrap_shapes.py`/`test_entrance_shims.py` in place meant
   the consumer engine's rsync `--exclude` + `rm -f` sweep lists
   needed zero changes, and stale copies in existing consumers still
   get swept.

### What Was Surprising

1. **The three biggest 0.9.0 features had NO changelog entry** —
   KIT-0046 (doctor), KIT-0048/0049 (planning shape + sync),
   KIT-0066/0067 (front door), KIT-0069/0071/0073 all missed
   [Unreleased] at their merge time; the release cut had to write
   five themed entries from memory records. The "CHANGELOG entry
   rides the PR" habit only took hold around KIT-0050.
2. **CodeRabbit self-cited a prior learning** — the
   DISTRIBUTION-ARCHITECTURE finding arrived tagged "Based on
   learnings: operational-documentation changes must update every
   representation" — the bot is now enforcing a rule this repo taught
   it on an earlier PR, and it was right (see regression below).
3. **`Path.exists()` returning False for dangling symlinks** made the
   first version of the `.kit/skills` retirement guard blind to a
   reintroduced broken link — CodeRabbit's only code finding, and a
   real one for a guard whose entire job is catching reintroduction.
4. **The door-native suite costs doubled locally but CI didn't move**
   — every retargeted bootstrap-shapes run now carries chrome +
   offers + doctor tail; local suite went to ~63s for 58 tests, yet
   the CI matrix stayed ~2m45s per version. The doctor tail is
   near-free on fresh scratch targets (all SKIP paths).
5. **MEMORY.md was stale on two load-bearing numbers** — it said core
   scripts 3.7.0 (actual 3.9.0) and pytest-fast ~11s (actual ~110s /
   792 tests). Neither caused an error because the workflow verifies
   before acting, but both would have misled a less suspicious
   session.

### What Should Change

1. **CHANGELOG-entry-per-PR needs a gate, not a habit** — seven
   merged tasks reached the release cut with no [Unreleased] entry.
   Candidate: a preflight gate (or bot-triage checklist line) that
   FAILs when a `feat`/`fix` PR touches no CHANGELOG line; or the
   planner adds it to the task-completion protocol.
2. **Item 15 needs "grep the FILE, not the line-neighborhood"
   enforcement in doc edits** — my DISTRIBUTION-ARCHITECTURE miss
   (fixed line 144, missed the same claim at lines 68/110/129) is
   exactly the `fix_by_class_not_instance` / item-15 class recurring
   in a doc file. When editing any doc for a rename/retirement,
   grep that same file for ALL representations (diagrams, tables,
   prose) before committing.
3. **Backlog specs should be sweep targets at removal time** —
   KIT-0060, KIT-0026, and ASK-0048 still direct future work at
   `.kit/skills/`. Flagged to the planner in the review starter, but
   the removal-spec template could require a "backlog citers" line so
   the flag is systematic, not vigilance-dependent.
4. **Add the zsh `=`-word footgun to the fd Shell Rules** — `echo
   ====X====` dies in zsh (`=cmd` expansion); cost two broken
   compound commands this session. One line in Recurring Footguns
   saves the next session the confusion.

### Permission Prompts Hit

None. All git/gh/pytest/evaluator calls ran without permission
stalls the whole session.

### Process Actions Taken

- [ ] Planner: decide the CHANGELOG-gate mechanism (preflight gate vs
      task-completion-protocol line) for feat/fix PRs
- [ ] Planner: add "grep the whole file for every representation" to
      self-review item 15 (or patterns.yml
      `fix_by_class_not_instance` gains a doc-file face)
- [ ] Planner: removal-spec template gains a "backlog citers" sweep
      line; disposition KIT-0060/KIT-0026/ASK-0048 stale `.kit/skills`
      text
- [ ] Planner: add zsh `=`-word expansion to fd Recurring Footguns
- [ ] Planner: refresh MEMORY.md core-scripts version (4.0.0 after
      merge) and the stale pytest-fast timing note
- [ ] Planner (post-merge): tree-grounded verification, tag v0.9.0,
      downstream pass, move KIT-0076/0047/0054/0059 to 5-done

### Incident Closure

1. **Harness cwd-reset in worktree session** (every `cd` snapped back
   to the primary checkout) — already documented in
   WORKTREE-WORKFLOW as a known harness behavior; absolute-path
   discipline held all session. **Not-checkable note exists** (this
   is harness behavior, not repo state a doctor check can probe).
2. **zsh `=`-word expansion breaking echo separators** —
   **triage-guide entry**: proposed as a Recurring Footguns line in
   the fd agents (process action above); diagnosable only at failure
   time, symptom is `(eval):1: ===X=== not found`.
3. No environment incidents beyond these — no failed tool
   assumptions, no drift between documented and actual behavior of
   repo tooling this session.

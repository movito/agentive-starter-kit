## KIT-0049 — Shape-Scoped `project sync` (PR #79)

**Date**: 2026-07-15
**Agent**: feature-developer-f5
**Mode**: single-repo (fifth worktree session: `ask-worktrees/KIT-0049`)
**Scorecard**: 3 threads (3 rounds, all real), 0 regressions, 4 fix rounds (1 evaluator pre-PR + 3 bot), 7 commits

### What Worked

1. **The engine-side design call validated itself** — placing the
   intersection in the engine (because manifest preservation lives in
   `_build_new_manifest`) meant the biggest evaluator finding (deletion
   pruning) landed entirely inside the function the call had already
   chosen. A wrapper-side intersection would have needed engine surgery
   anyway.
2. **Check `--only` semantics first (per handoff) saved parallel
   machinery** — `--only` was close-but-wrong (usage-errors on unknown
   keys, silent on skips, replaces the manifest), which made the delta
   crisp: `allowlist` is `--only` minus the errors plus the naming plus
   preservation. Half the engine change is comments explaining that
   contrast.
3. **Trio-before-PR converted rounds again** — o3's FAIL (deletion
   divergence) and six other findings were fixed before the PR existed;
   the bots then found genuinely NEW faces of the risk instead of
   re-finding the evaluator layer.
4. **Locked-decision specs are fast** — with both architecture calls
   pre-locked by the planner, implementation went spec→green in one
   pass with zero re-litigation. The evaluation-refuses-undecided-
   architecture loop (planner-side) did its job upstream of me.

### What Was Surprising

1. **Five reviewers found five faces of ONE design risk** — the
   intersection-masking class: upstream-deletion divergence (o3),
   allowlist-not-in-upstream completeness masking (fast-v2 +
   claude-code), string-tier char-iteration (BugBot), mixed-list silent
   discard (CodeRabbit), vacuous empty-scope completeness (BugBot).
   Set-intersection code structurally *masks absence* — nothing in
   `A ∩ B` tells you what fell out or why. Worth remembering whenever
   intersection semantics appear in a contract.
2. **o3's FAIL verdict is 3-for-3 on real blockers** (KIT-0046 dup-key,
   KIT-0048 reader fail-loud, KIT-0049 deletion divergence). Its FAILs
   have earned default-serious treatment; its individual claims still
   need verify-before-believing (2 disproven in KIT-0046).
3. **The stranded `skipif` decorator** — replacing KIT-0048's test class
   left its decorator attached to the helper function above the
   replacement, where pytest silently ignores it. Second
   block-replacement artifact this arc (KIT-0048 lost a deletion the
   same way).

### What Should Change

1. **Block-replacement hygiene → self-review checklist**: when replacing
   a large text block, inspect what sits immediately ABOVE and BELOW the
   replaced span (decorators, comments, staged-vs-disk state). Two
   artifacts in two tasks is a pattern.
2. **Consider a masking-class note in patterns.yml** — "intersection/
   filter code must name what it drops" generalizes the sync report
   rule (never silent) into a defensive-coding pattern.

### Permission Prompts Hit

None.

### Process Actions Taken

- [x] KIT-0048 refusal guard replaced; malformed-shape refusal retained;
      engine exit contract untouched (frozen-contract tests green)
- [x] 3 bot threads + 11 evaluator findings dispositioned (7 accepted /
      4 declined with evidence)
- [ ] Planner: post-merge — worktree remove, `project complete
      KIT-0049`, branch delete
- [ ] Planner: block-replacement hygiene item (Should Change #1);
      patterns.yml masking note (Should Change #2)

### Incident Closure

| Incident (this session) | Closure |
|--------------------------|---------|
| Stranded `skipif` decorator after block replacement — consumer-checkout CI would ERROR instead of skip (pytest silently ignores marks on plain functions) | **Fixed + hygiene note** — decorator moved to class level with a docstring recording why; block-replacement hygiene filed as a self-review checklist candidate |
| The intersection-masking class (5 faces: deletion divergence, completeness masking, string-tier, mixed-list, vacuous scope) | **Closed with validation + guards + tests** — dict[str, list[str]] schema refusals, preserved-manifest pruning, `--only`-clash UsageError, non-vacuous completeness; 9 refusal/pin tests. Pattern noted for patterns.yml (intersections must name what they drop) |
| Hook auto-fix aborted 1 commit (Black on the test file) | **Triage-guide exists** — COMMIT-PROTOCOL's verify-HEAD-moved caught it; formatting now runs before committing |

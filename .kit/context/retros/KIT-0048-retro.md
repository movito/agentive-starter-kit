## KIT-0048 — Planning-Repo Shape, ADR-0027 P2 (PR #78)

**Date**: 2026-07-14
**Agent**: feature-developer-f5
**Mode**: single-repo (fourth worktree session: `ask-worktrees/KIT-0048`)
**Scorecard**: 9 threads (4 rounds; 8 real+fixed, 1 declined with evidence), 0 regressions, 4 fix rounds (1 evaluator pre-PR + 3 bot), 8 commits

### What Worked

1. **Characterization-first was the regression net it promised to be —
   through an actual incident.** The flagless/`--shape single` sha256
   tree-identity test was written before any script edit; it stayed
   green across the planning branch, the GIT_DIR incident recovery, the
   evaluator round, and the branch-hoist refactor. Every one of those
   changes could have silently altered single-shape behavior.
2. **Evaluator-before-PR (first code task under the widened rule)
   collapsed the would-be bot rounds** — o3's FAIL (reader fail-loud)
   and claude-code's HIGH (heredoc injection) were fixed before the PR
   existed. The bots then found things the evaluators could NOT see
   (the sync-engine interaction) instead of re-finding the same layer.
3. **The KIT-0043 playbook turned a repo-corruption incident into ~3
   commands** — branch reset, `core.bare false`, verify. Having the
   damage signature documented meant instant recognition instead of the
   original session's forensic reconstruction.
4. **Hostile-environment suite re-run as a verification pattern** —
   after the 3-layer fix, re-running the entire test module under the
   exact exported `GIT_DIR`/`GIT_INDEX_FILE` proved the vector dead
   (refs and config untouched), not just plausibly-fixed.
5. **The canary caught the corruption within ONE commit** — the
   after-every-commit `core.bare` check (KIT-0043 discipline) is why
   the damage was hours-old, not weeks-old like the original incident.

### What Was Surprising

1. **The GIT_DIR class recurred despite the suite-wide fix — and that
   pinned the KIT-0043 mystery vector.** Class- and session-scoped
   fixtures execute OUTSIDE function-scoped autouse fixtures; the
   `7ef104d` isolation was function-scoped, so a class-scoped bootstrap
   fixture under the pytest-fast hook still saw the ambient GIT_DIR.
   The KIT-0043 retro's "vector never conclusively pinned" line is now
   answerable: this scope escape is the missing class of vector.
2. **BugBot found the one cross-component gap all three evaluators
   missed** — the planning manifest looked correct, but the SYNC ENGINE
   selects entries from the upstream manifest, so `project sync` would
   have reinstalled the entire toolchain. Single-file review (evaluator
   inputs) structurally cannot see cross-file semantics like this.
3. **I injected myself while describing an injection fix** — a
   double-quoted `git commit -m "… $(touch) …"` executed the
   substitution in MY shell (usage error, garbled message line).
   Cosmetic, and instantly instructive: subsequent commits single-quote.
4. **Ship-list judgment calls were the bulk of design time** — the spec
   enumerated the lifecycle machinery, but manifest/workflows/serena/
   .github decisions were left open; each got a documented rationale in
   the PR rather than a silent choice.

### What Should Change

1. **Document the fixture-scope caveat in TESTING-WORKFLOW.md** — the
   GIT_DIR gotcha section should state: function-scoped autouse
   isolation does NOT cover class/session-scoped fixtures; the
   session-scoped scrub (this PR) closes it, but new conftest fixtures
   must respect the pattern.
2. **COMMIT-PROTOCOL: single-quote (or heredoc) commit messages
   containing shell metacharacters** — `$(…)` in a double-quoted `-m`
   executes locally. One sentence in the protocol prevents the class.
3. **Review-checklist item: class/session-scoped fixtures that shell
   out** — any scoped fixture spawning subprocesses should build an
   explicitly scrubbed env (the `_scrubbed_env()` pattern) rather than
   trusting autouse isolation.

### Permission Prompts Hit

None.

### Process Actions Taken

- [x] KIT-0043's unpinned vector identified and closed (3 layers, all
      tested, hostile-env verified); primary restored same-session
- [x] KIT-0049 (shape-scoped sync) filed from the BugBot High
- [x] KIT-0027 retired to 6-canceled with disposition note
- [x] 9 threads resolved (8 fixed, 1 declined with evidence); 16
      evaluator findings dispositioned (7 accepted / 9 declined)
- [ ] Planner: post-merge — worktree remove (inputs wrinkle may need
      --force), `project complete KIT-0048`, branch delete
- [ ] Planner: TESTING-WORKFLOW fixture-scope caveat + COMMIT-PROTOCOL
      quoting line (Should Change #1/#2)
- [ ] Planner: KIT-0049 prioritization (planning repos cannot sync
      until it lands)

### Incident Closure

| Incident (this session) | Closure |
|--------------------------|---------|
| GIT_DIR corruption recurred: class-scoped fixture escaped function-scoped isolation under the pre-commit hook; scaffold commit onto the feature branch + `core.bare` flipped on the primary — **the KIT-0043 vector, now pinned** | **Three-layer hardening, all tested**: session-scoped autouse GIT_* scrub in conftest.py (ships to consumers); `_scrubbed_env()` in test helpers; bootstrap scrubs GIT_* itself + `-e .git` so a worktree can never be re-initialized. Verified under the exact hostile GIT_DIR |
| `$(touch)` in my own double-quoted commit message executed in my shell (usage error, garbled message line) | **Not-checkable note** — harness/agent behavior; closure is the COMMIT-PROTOCOL quoting discipline (Should Change #2); all subsequent commits single-quoted |
| KIT-0027 deletion lost in the incident's `reset --mixed`, silently absent from the re-commit | **Caught by the post-evaluator `git status` rule** (a non-evaluator catch — the rule's value generalizes); triage-guide coverage exists via that rule |
| `\s`-eats-newline regex bug: an empty `# shapes:` header captured the NEXT line as shape tokens | **Closed with test** — horizontal-whitespace class + empty-declaration-runs-everywhere test (found only because o3's empty-header finding was implemented rather than argued with) |
| Sync engine selects from the upstream manifest — planning repos would regain the toolchain on `project sync` (cross-component; only BugBot saw it) | **Guard + filed task**: `cmd_sync` refuses planning/malformed shapes (exit 2, tested ×3); KIT-0049 holds the real subset design |

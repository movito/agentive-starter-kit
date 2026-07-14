## KIT-0043 — Preflight Gates 1/2/7 Edge Hardening (PR #75) — WORKTREE PILOT

**Date**: 2026-07-14
**Agent**: feature-developer-f5
**Mode**: single-repo (first worktree-based session: `ask-worktrees/KIT-0043`)
**Scorecard**: 3 threads, 0 regressions, 3 fix rounds, 5 commits

### What Worked

1. **Reproduce-or-decline as a spec requirement earned its keep** — F4's
   gate ("do not start the fix round by trusting o3's claim") turned an
   unverified mixed-context finding into two green pinning tests and a
   decline, instead of a speculative Gate 2 rewrite. The jq-extraction
   trick (test pulls the script's own `--jq` filter at runtime) pins the
   behavior with zero duplication drift.
2. **Triple convergence found the one real design flaw** — o3, fast-v2,
   and BugBot independently hit the cap guard from three angles
   (advisory-flag-still-PASSes, raw-vs-filtered count, auto-resolved
   thread). The combined fix (raw-count guard + at-cap → PENDING, FAIL
   still wins) is strictly better than any single reviewer's suggestion.
3. **The planner's verified runtime facts collapsed F1** — the handoff's
   "the query ALREADY filters by --commit" note (with the line cited)
   reframed truncation from the evaluators' scary framing to the narrow
   real case, and the justify-the-limit acceptance path fit. Spec-time
   verification continues to pay.
4. **verify-HEAD-moved caught all three hook-aborted commits** — the
   COMMIT-PROTOCOL step (KIT-0035 retro) fired 3× this session (pytest
   failures ×2, end-of-file auto-fix ×1). Without it, each abort read as
   success in the output tail.
5. **Preflight validated itself at the finish** — the final 7/7 gate run
   executed the very Gate 1/7 logic this PR changed, on a PR whose own
   CI/bot state exercised the fallback paths.

### What Was Surprising

1. **The primary clone became a bare repo mid-session — CORRECTED
   (2026-07-14, post-review): this was DAMAGE from the GIT_DIR leak,
   not an operator restructure.** The original text below misattributed
   it; the planner's challenge caught the misread. Forensics: the
   working tree was fully intact on disk (a real bare conversion
   wouldn't leave it), `core.bare=true` sat in the shared config, and
   the config mtime (10:37 +0200) matched a closeout pre-commit run —
   AFTER the per-module test fixes, meaning a leak vector beyond the
   three pytest git-modules was still live (likely a test invoking a
   script that runs git). Suite-wide `GIT_*` isolation added to
   `tests/conftest.py`; primary clone restored (core.bare=false, tree
   reset to main); worktree removed. Lesson for the lessons-file: I
   verified evaluator claims all session but did not apply
   verify-before-believing to my own "operator restructure" inference —
   an intact working tree inside a "bare" repo was checkable in one
   command. Original (wrong) reading, kept for the record: closeout was
   done by ff-ing `main` in the bare repo and switching the task
   worktree to it — the recovery recipe itself remains valid.
2. **pre-commit exports an absolute `GIT_DIR` in worktrees** — the
   sharpest pilot finding. `test_project_script.py`'s tmp-repo git calls
   leaked to the REAL repo only under pre-commit-in-worktree, failing
   pytest-fast on every commit while passing in every other context. The
   documented GIT_DIR gotcha (TESTING-WORKFLOW.md) existed; only
   `test_preflight_check.py` applied it. Enabling fix shipped in the PR
   (module-level GIT_* isolation fixture).
3. **A fresh worktree is missing every gitignored install artifact** —
   `.adversarial/evaluators/` didn't exist, so the `adversarial` CLI
   listed no evaluator commands (confusing error: "invalid choice").
   `.venv`/`.env` were symlinked by the planner; evaluators weren't.
   `install-evaluators` fixed it in-worktree.
4. **fast-v2 has a variable-scoping blind spot** — its headline claim
   (stale `CI_RUNS` across loop attempts) hedged itself ("not likely
   given standard scoping") and was structurally impossible (per-attempt
   reset + break-on-success). Same reviewer produced the genuinely
   useful raw-vs-filtered count finding — signal and noise from the same
   source in one round.

### What Should Change (KIT-0044 requirements input — the 6 frictions)

1. **Launch the session tab IN the worktree** — this session ran from
   the main clone, so the harness reset cwd every call and every command
   needed a `cd` prefix (~40 extra cd's). The task starter said to open
   the tab in the worktree; the cost of not doing so is now measured.
2. **Worktree creation must branch from fresh `origin/main`** — the
   pre-created branch was 10 commits behind, predating the KIT-0042 gate
   changes this task builds on. Silent staleness; caught only by a
   `git status -sb` habit. KIT-0044: `git fetch && git worktree add -b
   <branch> <path> origin/main`.
3. **Symlink (or provision) ALL gitignored runtime artifacts** — not
   just `.venv`/`.env`: `.adversarial/evaluators/` at minimum; audit for
   others (`.adversarial/logs` history is nice-to-have, logs regenerate).
4. **pre-commit + worktree needs a documented env contract** — the
   absolute-GIT_DIR export breaks any test that shells out to git
   without env isolation — and, as the core.bare corruption proved, the
   damage is not limited to failing tests: it can MUTATE the real
   repository. **RESOLVED (post-review): suite-wide autouse GIT_*
   isolation fixture added to `tests/conftest.py`** — the per-module
   pattern demonstrably missed a vector.
5. **Define the closeout path for a bare-repo layout** — ~~superseded~~
   CORRECTED: the bare state was leak damage (Surprising #1), now
   restored; the primary clone has a normal working tree again. A
   deliberate bare-hub layout remains an evaluable KIT-0044 design
   question — if pursued, the improvised recipe (ff `main` inside the
   bare repo, work from worktrees) is a tested starting point, and the
   migration costs (session cwd, closeout, memory/path assumptions)
   must be written down first.
6. **Worktree lifecycle: who removes it?** — RESOLVED for this pilot:
   `ask-worktrees/KIT-0043` removed during the restore. KIT-0044 still
   owns the general policy (removal timing and ownership).

### Permission Prompts Hit

None.

### Process Actions Taken

- [x] KIT-0043 → 5-done; merged branch deleted; KIT-0042 decline-table
      rows updated to point at the resolutions
- [x] Suite-wide GIT_* isolation in `tests/conftest.py` (What Should
      Change #4 — resolved conftest-wide after the corruption evidence)
- [x] Primary clone restored (core.bare=false, tree reset to main);
      KIT-0043 worktree removed
- [ ] Planner: fold the frictions above into KIT-0044's spec as
      verified requirements (each has a session repro); bare-hub is a
      design question, not an assumption
- [ ] Next committer: verify `git -C <primary> config core.bare` is
      still false after the next pre-commit run (canary — the exact
      leak vector that wrote at 10:37 is not conclusively pinned;
      conftest-wide isolation should kill it, this check proves it)

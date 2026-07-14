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

1. **The primary clone became a bare repo mid-session** — at closeout,
   `git checkout main` in the main clone failed ("must be run in a work
   tree"); `git worktree list` showed the clone converted to bare with
   only the KIT-0043 worktree attached. The operator's restructure is
   the logical endpoint of the worktree direction, but every agent
   assumption of "the primary clone has a working tree on main" broke
   silently. Closeout was done by ff-ing `main` in the bare repo
   (`git fetch origin main:main`) and switching the task worktree to it.
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
   without env isolation. Either codify the module-level GIT_* fixture
   as a conftest.py standard (one fixture, whole suite) or document the
   per-module pattern in TESTING-WORKFLOW.md as mandatory for tmp-repo
   tests.
5. **Define the closeout path for a bare-repo layout** — `project
   complete`, retros, and memory bookkeeping all assumed a main-clone
   working tree. With a bare primary, either a standing `main` worktree
   (e.g. `ask-worktrees/main`) or a documented "closeout from the task
   worktree switched to main" recipe (what this session improvised).
6. **Worktree lifecycle: who removes it?** — `ask-worktrees/KIT-0043`
   still exists, now checked out on `main` post-closeout. KIT-0044
   should define removal timing (`git worktree remove` after retro?) and
   ownership (agent vs planner vs operator).

### Permission Prompts Hit

None.

### Process Actions Taken

- [x] KIT-0043 → 5-done; merged branch deleted; KIT-0042 decline-table
      rows updated to point at the resolutions
- [ ] Planner: fold the 6 frictions above into KIT-0044's spec as
      verified requirements (each has a session repro)
- [ ] Planner: decide conftest-wide vs per-module GIT_* isolation
      (What Should Change #4)
- [ ] Operator/planner: standing `main` worktree or documented bare-repo
      closeout recipe (What Should Change #5); remove or repurpose the
      KIT-0043 worktree (#6)

# KIT-0080 — Human Review Starter

**PR**: https://github.com/movito/agentive-starter-kit/pull/107
**Branch**: `feature/KIT-0080-portable-git-resolution`
**Head**: `fdb7ea4` · 3 commits · 14 files, +788/-14
**Task**: `.kit/tasks/4-in-review/KIT-0080-doctor-apple-git-230-incompat.md`
**Evaluator record**: `.kit/context/reviews/KIT-0080-evaluator-review.md`

## What this fixes

`git rev-parse --path-format=absolute` needs git ≥ 2.31. Apple's system
git (2.30.1, stock on macOS) does **not** consume the flag — it echoes it
back as the first output line and still **exits 0**. Every kit resolver
built on it produced garbage, and CI could never catch it because Ubuntu
runners ship modern git.

| Symptom | Before (real 2.30.1) | After |
|---|---|---|
| **S1** stray stderr | `dirname: illegal option -- -` | clean, empty stderr |
| **S2** `test_doctor.py` | 8 failed / 152 passed | **160 passed** |
| **S3** preset home | `./agentive-config` (relative garbage) | correct absolute sibling |
| **S4** `new-worktree.sh` | died; default topology unusable | provisions normally |

## The evidence situation changed — read this first

The task spec and handoff both state the local repro is **GONE** and that
stub fixtures are the only proof mechanism. That turned out to be wrong in
the operator's favour: **Apple git 2.30.1 is still on this machine at
`/usr/bin/git`**. The Homebrew upgrade shadowed it via PATH, it did not
remove it (the spec's own "Reproduction after the upgrade" section says
exactly this — it was just read as unavailable).

So every claim here is verified against the **real 2.30.1 binary**, not an
emulation, including the untruncated 8-failure baseline the spec's
correction #1 insisted on. The stub fixtures still ship, because they are
the only 2.30.x coverage that runs in CI.

## Gate status (all green)

| Gate | Status |
|---|---|
| CI (lint + tests 3.10/3.12/3.14) | PASS — 6/6 checks |
| CodeRabbit | **APPROVED** |
| BugBot | PASS, no findings |
| Review threads | 1 total, 1 resolved, 0 unresolved |
| Evaluator trio | PASS / CONCERNS / APPROVED — triaged |
| Local `ci-check.sh` | green, 932 passed, 93% coverage |

## Review guidance — where to look

**1. The two hazards introduced by the fix itself** (most worth your eyes).
Neither was in the spec; both are the same silent-wrong-answer class the
task exists to kill:

- **`cd ""` is a silent no-op.** An empty rev-parse result would have made
  "not a repo" resolve to a confident wrong path. Every resolver now
  emptiness-checks *before* joining. Covered by the non-repo SKIP tests.
- **`cd`+`pwd` resolves symlinked ancestors.** It would have reported
  physical paths (`/var` → `/private/var`), breaking the door/doctor
  equivalence invariant that `tests/test_setup_door.py` pins. The doctor
  and door resolvers now join by **string**; `new-worktree.sh` deliberately
  keeps `cd`+`pwd` because its value creates files rather than being
  compared, and says so in a comment.

**2. The floor moved 2.31 → 2.30 (a judgment call).** F4 said the floor
"drops accordingly" if F1 makes things portable. It does, so stock macOS
now **passes** rather than being warned at. README Requirements row updated
to match, and `test_floor_agrees_with_the_readme_requirements_row` pins the
two so they cannot drift. If you'd rather keep 2.31 as the advertised floor,
that's a one-line change in `15-git-version.sh` plus the README row.

**3. A 7th site the handoff didn't list.**
`.claude/commands/setup-preset.md:65` instructed *agents* to run the
unportable command — same bug, agent-executed. Fixed.

## Falsification — every guard was broken once

Each new guard was reverted to the **pristine pre-fix code**
(`git show HEAD~1:…`, not a hand-edit) and watched to fail:

| Reverted | Test that caught it |
|---|---|
| `90-config-home.sh` | reproduces S1's `dirname: illegal option -- -` |
| `70` / `55` | "verdict diverged between git versions" + S1 |
| `new-worktree.sh` | "S4 regressed — helper died on git 2.30.x" |
| the emptiness guard | non-repo SKIP tests fail |
| any `scripts/` file | the widened flag guard fails |

The stub itself is pinned by `TestOldGitStubIsFaithful`, so it cannot go
vacuously green.

## Evaluator triage — 1 of 5 actioned, 4 refuted

`code-reviewer` (o3) returned CONCERNS with 5 findings. Per the
verify-before-believing reflex each was measured, not accepted:

- **ACTIONED** — the regression guard only scanned `doctor.d`, so the
  `scripts/local/` half (S3 + S4, the bug's most expensive faces) could
  regress silently. Widened repo-wide, falsified.
- **REFUTED ×4** — filesystem-root `dirname` math (unchanged pre-existing
  code, and the arithmetic claim is wrong: `//agentive-config`, not empty);
  `../.git` breaking the worktree comparison (git returns **absolute** paths
  from a linked worktree — measured on a real pair); MSYS 2.30 bypassing the
  floor (the fix is build-independent, so PASS is correct); the ERR trap
  swallowing the exit code (measured: still exits 1).

Each disproof with its measurement is in the evaluator record, so the next
reader doesn't re-litigate them.

CodeRabbit's one finding was real and independent of all five: both stub
fixtures interpolated git's path into a bash `REAL=` assignment unquoted,
so a spaced git path (e.g. an Xcode-bundled git) made the stub exit 127
instead of emulating 2.30.x. Fixed in `fdb7ea4`, verified both ways.

## Out of scope (per handoff)

- KIT-ADR-0028 package extraction — this fix migrates there later; today's
  users need it now
- Preset authoring / `.env` seeding (KIT-0084 shipped it)
- `feature-developer.md` worktree contract (KIT-0088, already landed)
- The resolved 8-vs-3 baseline history

## Note for the planner

One environmental snag worth knowing: this repo's fetch refspec is narrowed
to `+refs/heads/main:refs/remotes/origin/main`, so from a worktree
`git push -u` cannot create a tracking ref and `gh pr create` refuses
without an explicit `--head`. I worked around it rather than changing what
looked like a deliberate repo config choice — but it will bite every future
worktree session the same way, so it may deserve its own task.

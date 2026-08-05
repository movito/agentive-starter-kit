# KIT-0080: doctor.d checks + tests break on Apple git 2.30.1

**Status**: Todo
**Priority**: high (raised from medium 2026-08-04 — see S3: the same root
cause silently disables operator-preset resolution in the setup door.
Reaffirmed 2026-08-05: **S4** makes it a hard block on the default
worktree topology, and the operator's local git upgrade removed the
repro without fixing the kit — see the 2026-08-05 update at the bottom)
**Created**: 2026-08-04
**Sequencing (planner, 2026-08-05)**: PROMOTED to todo, next assignment
after KIT-0083 lands. S4 hard-blocks the default worktree topology for
every operator on stock macOS git, and every queued kit task's starter
specifies a worktree. Note for the implementer: the operator's machine
now runs git 2.55.0, so the local repro is GONE — F3's git-version
fixtures (pinning the 2.30.x parsing behavior) are the only proof
mechanism available; manual verification is no longer possible here.
The portable one-liner is live-verified in
`.kit/context/KIT-0083-SESSION-FINDINGS.md` F1.

## Overview

On the macOS system git — **git 2.30.1 (Apple Git-130)** — two doctor
symptoms surface, both traceable to one root cause: `git rev-parse
--path-format=absolute --git-common-dir` does **not** consume
`--path-format=absolute` as a flag. Instead git echoes the literal
string `--path-format=absolute` as the first output line, then the
path on the next line:

```console
$ git rev-parse --path-format=absolute --git-common-dir
--path-format=absolute
.git
```

Newer git (used in CI) consumes the flag and prints only the absolute
path, so CI is green and this only bites local macOS users on system
git.

## Symptoms

- **S1 — cosmetic warning leaks from `project doctor`**:
  `scripts/core/doctor.d/90-config-home.sh:52` runs
  `dirname "$(dirname "$common")"` where `$common` is the two-line
  string above. `dirname` sees an arg starting with `--` and prints
  `dirname: illegal option -- -` to stderr. The check still falls
  through to `config-home:SKIP` correctly, but the raw git error leaks
  into doctor output and the driver exits non-zero on that stream.

- **S2 — 8 failing tests in `tests/test_doctor.py`** on the same git:
  - `TestCoreBareCheck::test_bare_config_fails`
  - `TestWorktreeProvisioningCheck::test_worktree_serena_distinct_name_passes`
  - `TestWorktreeProvisioningCheck::test_serena_short_name_key_collision_detected`
  - `TestWorktreeProvisioningCheck::test_serena_apostrophe_name_not_mangled`
  - `TestWorktreeProvisioningCheck::test_serena_unnamed_config_warns`
  - (+3 more in the fast-guard subset — full run: 8 failed, 132 passed)

  All fail the same way: a check emits `PASS` where the test expects
  `FAIL`/`WARN`/a differently-named line, because the mis-parsed
  `--git-common-dir` output makes the check resolve the wrong repo
  paths. These blocked the pre-commit `pytest-fast` guard during the
  KIT doc-ceiling commit (committed with `SKIP_TESTS=1`;
  Markdown-only change, unrelated).

- **S3 — the setup door never finds the operator preset** (found
  during the ev-fast-charging-loads intake, 2026-08-04; this is NOT
  cosmetic): `scripts/local/bootstrap:161` (`config_home()`) uses the
  same `rev-parse --path-format=absolute --git-common-dir` pattern.
  On git 2.30.1 `$common` becomes the two-line string
  `--path-format=absolute\n.git`, the nested `dirname` calls error
  (the `dirname: illegal option -- -` seen at door startup), and the
  config home resolves to the relative garbage `./agentive-config`.
  Consequence: even a correctly-authored preset at
  `<kit-parent>/agentive-config/preset` is silently ignored on every
  door run — evaluators, env-source, bots and shape answers all fall
  back to skip/default. This plausibly explains the operator's
  repeated "planning repo not properly created" experiences. The
  audit in F1 must therefore include `scripts/local/bootstrap`,
  `scripts/local/new-worktree.sh:36` (its line-42 guard catches the
  garbage and hard-exits, so worktree creation is dead on this git),
  and `scripts/core/project:1512` — not just doctor.d.

## Requirements

- **F1**: make the `--git-common-dir` resolution portable across git
  versions. Options — choose at implementation, record why:
  - drop `--path-format=absolute` and resolve to absolute in shell
    (`cd "$dir" && pwd`), or
  - detect the echoed-flag line and strip it, or
  - gate on `git --version` and branch.
  Audit **all** doctor.d files that use this pattern, not just
  `90-config-home.sh` (grep `--path-format` / `--git-common-dir`).
- **F2**: `project doctor` must emit no stray `dirname:`/`git:` errors
  on git 2.30.1; the config-home check still ends `SKIP`/`PASS`
  correctly.
- **F3**: the 8 `test_doctor.py` cases pass on Apple git 2.30.1 (S2
  list) as well as on the CI git — add a version note or a fixture
  that pins the parsing behavior so the suite is git-version-robust.
- **F4** (nice-to-have): consider a doctor.d check or CI matrix entry
  that exercises the oldest supported git, so this class regresses
  loudly rather than silently on contributors' machines.

## Evidence

Live on this machine 2026-08-04: `git --version` = 2.30.1 (Apple
Git-130); `project doctor` leaked `dirname: illegal option -- -`;
`pytest tests/test_doctor.py -m "not slow"` = 8 failed / 132 passed.
Reproduce the root cause with the `git rev-parse` command above.

---

## Update 2026-08-05: operator upgraded git — task STAYS OPEN

**The local reproduction is gone; the bug is not.** The operator
upgraded `2.30.1 (Apple Git-130)` → **`2.55.0` (Homebrew)**, which made
every symptom below disappear on this machine. **Do not read this as
resolution.** The kit still ships scripts that require git ≥ 2.31 —
`--path-format` landed in **git 2.31 (March 2021)**, and Apple ships
2.30.1, one minor version below the cutoff. Every operator on stock
macOS git still hits all of it, and **CI cannot catch it** (Ubuntu
runners have modern git). F1–F4 are all still required.

### What the upgrade confirmed (each symptom causally verified)

| Symptom | On 2.30.1 | On 2.55.0 |
|---|---|---|
| root cause: `rev-parse --path-format` | echoed the flag back as a rev, exit 0 | one absolute path, consumed correctly |
| **S1** stray `dirname:` in doctor | leaked to stderr | gone |
| **S2** `test_doctor.py` | 8 failed | **152 passed, 0 failed** |
| **S3** preset home resolution | `./agentive-config` (relative garbage) | `/Users/broadcaster_one/Github/agentive-config` |
| full fast suite | 3 failed *(truncated count, see below)* | **796 passed, 0 failed** |
| `project doctor` | `dirname` errors on stderr | 6 pass, 1 warn, 0 fail, exit 0 |

This is a clean causal proof: one variable changed, every symptom
resolved. It confirms the S1/S2/S3 diagnosis was correct in full.

### Two corrections to the record

1. **The failure count is 8, not 3.** A KIT-0083 handoff addendum
   stated 3; that came from reading a truncated pre-commit
   `pytest-fast` tail (`-x` stops after 3 failures and deselects 45
   tests). Corrected by the KIT-0083 agent in `b87b058` F2, and the
   correction is right — S2's original 8 was always accurate. **A
   truncated baseline is dangerous**: it under-reports the expected set
   and would mask real regressions. When recording an expected-failure
   baseline, always run the suite untruncated.
2. **New symptom — S4: `new-worktree.sh` is a hard block, not a silent
   wrong answer.** `scripts/local/new-worktree.sh:36` uses the same
   pattern and **dies outright** on 2.30.1 (confirmed by the KIT-0083
   agent, `b87b058` F1), leaving a half-provisioned worktree. This is
   worse than S1–S3: those degrade silently, this one fails the default
   worktree topology. **Any task told to use a worktree hard-fails on
   stock macOS git until F1 lands.** Sequence KIT-0080 before such
   tasks, or ship the portable one-liner with them.

### Fix guidance reinforced

The KIT-0083 agent live-verified F1's **first listed option** (resolve
via plain `--git-common-dir`, absolutize in shell) as a working
portable replacement — see `b87b058` for the one-liner. That is the
recommended path; it needs no version gate and no flag-stripping.

### Reproduction after the upgrade

The local repro now requires invoking the old binary explicitly:

```console
$ /usr/bin/git rev-parse --path-format=absolute --git-common-dir
--path-format=absolute
.git
```

Apple's git remains at `/usr/bin/git` — the upgrade shadowed it via
PATH (`/opt/homebrew/bin` precedes `/usr/bin`), it did not remove it.
This is also the basis for F4: a CI matrix entry or doctor check
exercising the oldest supported git would catch the class without
depending on any operator's local toolchain.

### Note for whoever fixes this

`xcode-select --install` does **not** help — Apple's Command Line Tools
ship 2.30.x by design; it is a constrained system binary, not a stale
download. The only local remedies are Homebrew git (as done here) or
the portable fix in F1. Worth stating in any operator-facing doc, since
`xcode-select --install` is the intuitive first thing to try.

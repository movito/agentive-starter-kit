# KIT-0080: doctor.d checks + tests break on Apple git 2.30.1

**Status**: Backlog
**Priority**: medium (cosmetic warning + 8 red tests on macOS system git; doctor still reports correctly)
**Created**: 2026-08-04

## Overview

On the macOS system git — **git 2.30.1 (Apple Git-130)** — two doctor
symptoms surface, both traceable to one root cause: `git rev-parse
--path-format=absolute --git-common-dir` does **not** consume
`--path-format=absolute` as a flag. Instead git echoes the literal
string `--path-format=absolute` as the first output line, then the
path on the next line:

```
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

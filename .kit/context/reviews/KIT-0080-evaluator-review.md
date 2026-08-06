# KIT-0080 — Evaluator Review Record

**Date**: 2026-08-06
**Branch**: `feature/KIT-0080-portable-git-resolution`
**Commit reviewed**: `eaf2c04`
**Input**: `.adversarial/inputs/KIT-0080-code-review-input.md` (full-file
context, 13 files, 8,978 lines)
**Ordering**: trio run BEFORE the PR was opened (KIT-0035/KIT-0046 rule).

## Trio results

| Evaluator | Model | Verdict |
|-----------|-------|---------|
| `code-reviewer-fast` | gemini-2.5-flash | **PASS** |
| `code-reviewer` | o3 | **CONCERNS** (5 findings) |
| `claude-code` | claude-sonnet-4-6 | **APPROVED** |

Logs: `.adversarial/logs/KIT-0080-code-review-input--*.md`

## Triage of the 5 CONCERNS findings

Per the verify-before-believing reflex, each was tested against the
actual tree / actual git behavior rather than accepted on assertion.
**One was real and is fixed; four were refuted by direct measurement.**

### 1. ACTIONED — flag guard only scanned `doctor.d`

> "Portable-flag sweep is limited to doctor.d — other scripts might
> regress silently."

**Real and worth fixing.** The bug's two most expensive faces (S3's
silent preset miss, S4's hard death) both live in `scripts/local/`, so
a guard watching only `doctor.d` would let the worse half regress.
Widened to all of `scripts/` and renamed
`test_no_script_still_uses_the_unportable_flag`. Falsified: reverting
`scripts/local/new-worktree.sh` to its pre-fix form now fails the
guard, where previously it passed.

### 2. REFUTED — "wrong parent calculation at filesystem root"

Claim: for a checkout at `/repo`, `dirname "$(dirname /repo/.git)"`
returns an empty string, yielding `/agentive-config`.

Measured: `dirname /repo/.git` → `/repo`; `dirname /repo` → `/`. The
result is `//agentive-config`, not the claimed empty string. More
importantly the double-`dirname` is **unchanged pre-existing code**
(`git show HEAD~1:scripts/core/doctor.d/90-config-home.sh:52` is
byte-identical) — not a regression from this PR, and a repo at the
filesystem root is not a topology the kit supports. Out of scope.

### 3. REFUTED — "`../.git` breaks the worktree path comparison"

Claim: in a linked worktree `--git-common-dir` prints `../.git`, so
the string join leaves `..` and the equality check misfires.

Measured on a real primary+worktree pair, both git versions:
`git -C <worktree> rev-parse --git-common-dir` returns an **absolute**
path; `--git-dir` returns an absolute path too. From the primary both
flags return the identical `.git`, so the comparison correctly reports
"not a worktree". The premise about git's output is simply wrong.

### 4. REFUTED (premise wrong) — "MSYS `2.30.windows.1` bypasses the floor"

Claim: MSYS 2.30.* PASSes the floor but "carries the same broken
`--path-format` behaviour — the portability fix only covers 2.30.1
Apple". Measured: it does PASS. But the fix is **build-independent** —
no resolver calls `--path-format` on any platform any more, so 2.30 on
any build is genuinely supported. PASS is the correct verdict; warning
there would cry wolf.

### 5. REFUTED — "ERR trap makes the helper exit 0 on failure"

Claim: `trap '…' ERR` overrides `set -e`, so provisioning failure
exits 0 and automation believes the worktree was created.

Measured directly: a `set -euo pipefail` script with a non-exiting ERR
trap and a failing command exits **1**. The trap prints and the shell
still aborts with a failing status. Claim is false.

## Known evaluator blind spot

Nothing CSS/dual-render-path shaped in this diff, so the documented
blind spot does not apply.

## Post-triage state

Suite re-run after the finding-1 fix: green on modern git AND on the
real Apple git 2.30.1 binary (`/usr/bin/git`, still present on this
machine) — see the PR body for counts.

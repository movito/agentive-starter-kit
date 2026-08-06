# KIT-0083 — Evaluator Review Record

**Date**: 2026-08-05
**Branch**: `feature/KIT-0083-ship-adversarial-cli`
**Input**: `.adversarial/inputs/KIT-0083-code-review-input.md`
(full-file format, 8 files, ~87k tokens)
**Ordering**: trio run BEFORE the PR was opened, per the Phase 7
ordering rule (local green → trio → PR). Code task, so the
prose-sweep exception does not apply.

## Verdicts

| Evaluator | Model | Verdict |
|---|---|---|
| code-reviewer-fast | gemini-2.5-flash | CONCERNS |
| code-reviewer | o3 | CONCERNS |
| claude-code | claude-sonnet-4-6 | APPROVED |

Logs: `.adversarial/logs/KIT-0083-code-review-input--*.md`

## Findings and dispositions

### Actioned

**1. False ✅ on a present-but-broken binary** (fast + o3 — the two
evaluators converged on this independently, which is why it was fixed
first). The install step gated on `shutil.which` (presence) while
doctor.d/31 probes `--version` (liveness), so a corrupt install printed
✅ and the very next `project doctor` FAILed on it — two surfaces
disagreeing about one install.
→ Added `_adversarial_cli_works()` (which + `--version` exit code, with
its own timeout) and routed both the pre-check and the post-install
verification through it. The post-install branch now distinguishes
three states with three different remedies: works → ✅; on PATH but not
runnable → `--force` reinstall; not on PATH → PATH advice. Covered by
`TestAdversarialCliLiveness` (6 cases).

**2. Mirror regex ignored `==` pins** (o3). Verified reproducible before
fixing: the `>=`-only regex returned `None` for
`adversarial-workflow==1.2.3`, which the caller reads as "no pin" and
sends down the instruct-only path — an installable project would
silently not install. Relevant because KIT-0079 may write an exact pin
into the mirror.
→ Regex accepts `>=`, `==`, `~=` and bare. Covered by
`TestPyprojectMirrorPinForms`, which drives the REAL reader (via a
fixture tree + patched `__file__`) rather than re-implementing the
regex in the test.

**3. Unbounded `--version` probe could hang the doctor run** (o3).
→ Bounded to 20s. Deliberately NOT GNU `timeout`: it is a homebrew
add-on on macOS, absent from a stock system, so depending on it would
work on this machine and hang on a plain one — the same "passes
locally, proves nothing" trap that let #103 ship. Verified against a
`sleep 300` stub: bounded FAIL at 20.2s instead of hanging.

**4. Junk pin reaches uv as a confusing spec** (claude-code, low).
Not injection — the pin is a list element to `subprocess.run`, never a
shell string. But a pin of `--force` becomes
`adversarial-workflow==--force` and surfaces as a baffling uv error
instead of "your pin is wrong".
→ Added `_is_version_like()`, applied to BOTH the config.yml read and
the pyproject mirror. A junk pin now falls through to the
instruct-don't-install path. Covered by `TestPinValidation`.

**Bug found by my own new tests while fixing #3**: the first bounded
implementation used a bare `sleep`, which does not exist under the
restricted PATH the doctor tests run with — so the loop spun instantly
and reported a **false FAIL on a healthy CLI**. `sleep` is now resolved
to an absolute path (same idea as `BASH` in `tests/test_doctor.py`),
with a blocking `wait` fallback when no sleep binary exists. This is
precisely the bug class this task exists to prevent, caught by the
PATH-isolation discipline the task mandated.

### Declined, with reasons

**`.adversarial` existing as a FILE reports SKIP** (o3, "minor bug").
Reproduced — it does report SKIP. Declined anyway: `30-evaluators.sh`
uses the identical `[ ! -d ]` test, so "fixing" it here alone would
make two sibling checks disagree about what an initialized project
looks like, for a corrupt-tree state neither check is meant to
diagnose. If it is worth fixing it is worth fixing consistently, in its
own task. Noted in the PR body.

**Concurrent `install-evaluators` invocations race on uv's lock** (o3).
Speculative: `uv` performs its own locking, and a lock collision
already degrades to the "install failed → retry manually" path, which
never fails the caller. Adding a file lock would be more machinery than
the risk warrants for a developer-tooling install step. Not actioned.

## Verification beyond the evaluators

- **End-to-end against a fixture of the exact #103 shape** (library
  installed, CLI absent, uv absent): the CLI warning prints BEFORE the
  already-installed early return, at the pinned version read from
  config.yml, and the command still exits 0.
- **Both doctor lines side by side on that fixture**:
  `evaluators:PASS` and `evaluator-cli:FAIL` — the masking bug, closed
  and demonstrated rather than asserted.
- **uv-present path** with a stub `uv` that "succeeds" without
  producing a binary: correctly detected as installed-but-not-on-PATH.
- **Full `ci-check.sh`**: 7/7 stages, 872 passed, 12 skipped, 93%
  coverage.

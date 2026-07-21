# KIT-0057 — Evaluator Review Record

**Date**: 2026-07-21 · **Ordering**: trio run BEFORE PR open
(KIT-0035/0046 rule) · **Input**: full-file context via
`prepare-review-input.sh KIT-0057 --format full` (10,908 lines)
· **Invocation**: `echo y | ADVERSARIAL_UNATTENDED=1 adversarial …`;
verdicts read from log files, never exit codes; `git status` clean
after every run.

| Evaluator | Model | Verdict | Disposition |
|-----------|-------|---------|-------------|
| code-reviewer-fast | gemini-2.5-flash | CONCERNS | All 4 findings out of diff scope (below) |
| code-reviewer | o3 | FAIL | All 6 findings refuted or out of scope (below) |
| claude-code | claude | **APPROVED** | One MEDIUM noted for follow-up |

## code-reviewer-fast — CONCERNS, no action

All four findings name pre-existing functions in `scripts/core/project`
(`_print_preset_comparison`, `cmd_doctor`, `cmd_sync`,
`reconfigure_project`) that this PR touches only via one docstring
path update. The "missing" tests exist outside the diff and were
invisible to the evaluator: `tests/test_doctor.py` covers the
non-executable/crashing/timeout driver paths, and
`tests/test_project_sync.py` covers dirty-tree refusal, unsafe-path
refusal, and malformed-manifest refusals (KIT-0049's entire review
cycle). Full-file input includes the whole `project` script, which
pulls pre-existing code into review scope — known artifact of the
format.

## code-reviewer (o3) — FAIL, refuted point by point

The KIT-0050 pattern again (o3 FAIL with plausible-but-wrong claims);
each verified against the code before dismissal:

1. **"Re-bootstrap without `--bots` leaves two conflicting
   declarations" — REFUTED.** The door's resolve chain reads the
   record first ("a question the record already answered is not
   open", `resolve_setting`), so an omitted flag preserves the
   existing line — nothing is appended. An explicit `--bots` that
   conflicts with the record is `die_usage` (engine guard, CodeRabbit
   PR #81 precedent). No path writes a second line.
2. **"`_dirty_touched_paths` ignores renamed files" — REFUTED.** The
   helper explicitly collects BOTH sides of `R`/`C` porcelain records
   (`scripts/core/project:1153-1157`, comment says so — KIT-0049
   hardening). The claim quotes behavior the code does not have.
3. **Windows `core.symlinks=false` checkout — acknowledged, accepted.**
   Scope: a Windows checkout of the KIT REPO itself during the one
   deprecation release. Consumers never receive symlinks — pull-sync
   ships dereferenced bytes (pinned by
   `test_sync_engine_reads_content_through_old_path`); the o3 claim
   that sync "ships bogus path" is wrong for supported checkouts. Kit
   development is macOS + ubuntu CI. Removal in 0.9.0 (KIT-0059).
4. **"BSD/GNU sed dual pattern half-rewrites on GNU" — REFUTED.** On
   GNU sed the BSD form exits nonzero (script/operand misparse), the
   `||` fallback runs the GNU form; files are not half-written by an
   empty-script pass. This exact dual pattern is long-shipped repo
   convention (version sed beside it, onboarding agent).
5. **`_check_declared` 30-line scan — out of scope.** Pre-existing
   KIT-0046 design choice, untouched by this PR.
6. **Windows read-both test gap — same as (3).**

## claude-code — APPROVED

Security posture clean (no injection vectors, no secrets, GIT_*
scrubbing consistent, consumer exclusions complete). One MEDIUM:
`test_bots_conformance.py`'s cross-module imports
(`test_preflight_check` / `test_setup_door`) are coupling — accepted:
re-using the real harnesses beats duplicating them; the
`allow_module_level` guard covers consumer checkouts. Noted for the
retro rather than a code change.

## Known evaluator blind spot check

No CSS/dual-render-path surface in this PR (scripts + tests + docs
only) — the documented blind spot does not apply.

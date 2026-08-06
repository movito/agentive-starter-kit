# KIT-0090 PR 1 — Evaluator Review Record

**Task**: KIT-0090 extract-scripts-package, PR 1 (skeleton + gitio +
lifecycle + shim)
**Date**: 2026-08-06
**Ordering**: trio run BEFORE PR open (KIT-0035/0046 rule)
**Evaluators**: code-reviewer-fast (gemini-2.5-flash), code-reviewer
(o3), claude-code
**Rounds**: 5 (fast ×2, deep ×3, security ×1)

## Final state

- Full suite green at every round; 77 package tests + migrated
  script-test coverage
- All FAIL/CONCERNS findings dispositioned below — taken, refuted
  with evidence, or declined with rationale
- Deep-evaluator loop STOPPED at round 5 on oscillation (see below);
  further rounds were re-litigating settled coins

## Taken (fixed, with tests)

| Round | Finding | Fix |
|-------|---------|-----|
| 1 (fast) | Missing `.kit/tasks/` crashes find/validate | Guard returns None / zero-checked report |
| 1 (fast) | Non-UTF-8 task file crashes validate | Becomes a `StatusIssue` finding |
| 2 (fast) | Shim dispatch untested at subprocess level | `TestLifecycleDelegation` (dogfood + loud-error paths) |
| 3 (deep+sec) | Partial-ID substring match moves wrong file (`KIT-1` → `KIT-1234`) | Boundary-anchored match; publishing makes match semantics stable API |
| 3 (deep) | Move fails when destination status folder absent | `mkdir(parents=True, exist_ok=True)` before move |
| 3 (sec) | `re.sub` template could re-interpret status value | Lambda replacement |
| 4 (deep) | `clean_git_env` stripped behavior vars (`GIT_SSH_COMMAND`, `GIT_EXEC_PATH`) | Narrowed to the location-override list (KIT-0043 class, legacy `_clean_git_env` parity) |
| 4 (deep) | PermissionError in root walk → traceback on Python < 3.13 | `_is_project_root` swallows OSError, walk continues |
| 4 (deep) | ssh:// remote form untested | Parametrized `derive_repo_url` test |
| 5 (deep) | `_kit_lifecycle` masks a broken INSTALLED package as "not installed" | Catch `ModuleNotFoundError` only |

## Evaluator oscillation — recorded deliberately

Round 4 (o3): "underscore after the ID must block the match
(`(?![0-9A-Za-z_])`)". Implemented. Round 5 (o3): the same block "can
strand existing tasks" (`KIT-1234_sample.md` was findable under the
legacy matcher) — a regression claim against its own round-4
instruction. Round 5 wins on data compatibility: `_` is a separator
like `-`; only alphanumeric run-on is the wrong-file hazard. Reverted
to `(?![0-9A-Z])` with a test pinning `KIT-1234_sample.md` as found.
Loop stopped here: the reviewer is oscillating on settled coins
(hyphenated statuses re-raised twice, see Declined).

## Refuted (verified against reality)

- **"Unborn HEAD prints nothing on git ≥ 2.36"** (deep r3): verified
  on git 2.55 — `git branch --show-current` prints the unborn branch
  name; pinned by `test_unborn_branch_still_reports_name`.
- **"`text=True` without capture raises ValueError"** (deep r3):
  verified legal (`subprocess.run(['true'], text=True)` runs fine).
- **"`_derive_repo_url` script copy untested"** (fast r1):
  `TestDeriveRepoUrl` remains in tests/test_project_script.py covering
  the script's live copy (kept for reconfigure; dies with the script).
- **"git-absent-but-uv-present path untested"** (deep r4):
  `test_cli_install_attempted_when_git_absent_but_uv_present` exists.
- **"Lowercase suffix passes the ID boundary"** (deep r4): matching
  runs on the uppercased name; pinned by
  `test_lowercase_suffix_does_not_match`.
- **"Symlinked cwd breaks `relative_to`"** (deep r5): impossible —
  every path handed to `relative_to(project_dir)` is constructed from
  `project_dir` itself.

## Declined (with rationale)

- **Hyphenated/custom statuses not matched** (deep r3, r5; fast r1):
  the status vocabulary is the fixed `FOLDER_STATUS_MAP`; the regex is
  legacy-identical, and custom-state support is a feature decision,
  not extraction scope.
- **`find_task_file` iteration order non-determinism** (fast r1/r2):
  legacy-identical; only observable with duplicate IDs, which the
  boundary fix already narrows.
- **File locking for parallel moves** (deep r5): single-operator tool;
  legacy-identical; a locking scheme is out of scope.
- **Move-succeeded-but-status-stale still prints ✅** (deep r4):
  legacy behavior; `TaskMove.status_field_updated` exposes it to
  callers; revisit when the CLI grows structured output.
- **Archive-folder moves** (sec r3, LOW): legacy carry-forward;
  revisit in package API hardening.
- **Hardcoded statuses in script help text** (fast r2): print_help
  already hardcodes them; the script dies in phase 4.

## Known blind spot note

Evaluators cannot re-verify the PyPI `agentive` entry-point check from
static analysis (claude-code, "Context Required") — verified manually
2026-08-06: the `agentive` 0.0.144 wheel ships no entry_points.txt.
Re-check before the PR-4 publish.

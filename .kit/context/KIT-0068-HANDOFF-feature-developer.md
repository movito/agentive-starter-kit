# KIT-0068 Handoff — feature-developer

**Task**: `.kit/tasks/4-in-review/KIT-0068-functional-repairs-audit.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-24 (planner-f5)
**Estimated effort**: 1-1.5 days

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0068/`** — branch
`feature/KIT-0068-functional-repairs-audit`, fully provisioned. Run
`git pull --ff-only` first. Absolute paths / `git -C` throughout.

## Mission

Fix the FUNCTIONAL cluster of the pre-0.9.0 cruft audit: three broken
`project` subcommands, the materials-engine consumer leak, config/
symlink defects, and three-way toolchain drift. Behavior only — prose
corrections belong to KIT-0069, aider residue to KIT-0065; if you
find yourself editing text that doesn't change what runs, stop and
check the task boundaries.

## Evidence base (read FIRST)

`.kit/context/reviews/PRE-090-CRUFT-AUDIT-2026-07-24.md` — every
F-item cites A-numbers with verified evidence including exact lines.
Re-verify each cited line before fixing (audit ran today, but the
verified-runtime-facts rule stands). Key anchors from the audit:

- `scripts/core/project:2127` (linearsync path), `:2464-2475`
  (create-agent path), `:496-501` (reconfigure logging_config tuple)
- `tests/test_project_script.py:594-603` — the OLD-LAYOUT fixture
  that masked A02; this is the fixture-honesty exhibit
- `scripts/optional/sync_tasks_to_linear.py` env_path (A15);
  `scripts/optional/linear_sync_utils.py` prefix regexes (A14)
- `scripts/local/engine-materials.sh` — rsync of scripts/ wholesale
  (A12) + `context/ASK-*`/`tasks/ASK-*` excludes (A13)
- `.adversarial/config.yml` (A67) — verify keys against the
  INSTALLED CLI (`command -v adversarial`; three-installs lesson —
  test against the binary the session actually runs)
- `.adversarial/evaluators/evaluators` self-symlink (A69) — check
  `scripts/local/new-worktree.sh` link step for the creation vector
- `.pre-commit-config.yaml` black rev (A84); ruff surfaces (A88):
  CLAUDE.md + pyproject `[tool.ruff]` + dev dep; `ci-check.sh`
  flake8 args vs `.github/workflows/test.yml` (A91)
- `scripts/core/project:2204-2207` (version), evaluator fallback
  v0.5.3 (A08), `main()` venv order + help (A10),
  `scripts/core/__init__.py` docstring (A05)

## Context you must not lose

- **The A02 class is the headline**: a test fixture modeling a
  nonexistent layout masked a broken command for months. The
  fixture-path guard test (every fixture path must exist in the real
  tree) is as important as the fixes themselves.
- **Ruff decision rule is in the spec** — run `ruff check` first,
  then EITHER enforce everywhere OR remove everywhere. Record which
  branch you took and the violation count in the PR body.
- **Two-homes rule** (accepted evaluation note): paired facts get
  consistency tests, not promises.
- **Materials-engine fix must NAME its exclusions** in output
  (patterns.yml `intersection_names_drops`).
- **Declined**: any path-registry/resource-location abstraction —
  fix the paths in place.
- Core scripts touched → VERSION 3.5.0→3.6.0, manifests +
  `test_core_manifest.py` in the same commit as the file-list change.
- PR body: check off every cited A-number with a one-line
  disposition.

## Test approach

- Ordering rule: local tests green → evaluator trio
  (`echo y | ADVERSARIAL_UNATTENDED=1 …`; log-file-with-verdict is
  the proof; `git status` after every run) → PR open.
- Real-layout fixtures for the three command tests; materials-export
  content test (no scripts/local, no task files); Black rev
  consistency test; fixture-path guard test.
- `pytest` directly; `./scripts/core/ci-check.sh` before pushing —
  note you will be MODIFYING ci-check.sh (F6): test the modified
  version on itself.

## Evaluation summary

`arch-review-fast`: REVISION_SUGGESTED — path-registry declined
(5th forge/abstraction-class decline), two-homes rule accepted,
contract-test already in spec. Disposition in the task file; log:
`.adversarial/logs/KIT-0068-functional-repairs-audit--arch-review-fast.md`.
No outstanding blockers.

## Out of scope

- Prose-only audit findings (KIT-0069); aider residue incl. the
  <3.13 bound (KIT-0065); launchers/onboarding structure (KIT-0067/70)
- 0.9.0 removals

## PR sizing

Single PR target. If F1-F7 + tests push past ~500 reviewable lines,
split as (1) project-script fixes + tests, (2) engines/config/
toolchain — F1's fixture guard lands in PR 1 either way.

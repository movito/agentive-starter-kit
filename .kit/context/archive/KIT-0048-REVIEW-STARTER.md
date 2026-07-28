# KIT-0048 Review Starter — Planning-Repo Shape (ADR-0027 P2)

**PR**: https://github.com/movito/agentive-starter-kit/pull/78
**Branch**: `feature/KIT-0048-planning-repo-shape` (worktree: `../ask-worktrees/KIT-0048`)
**Task**: `.kit/tasks/4-in-review/KIT-0048-planning-repo-shape.md`
**Date**: 2026-07-14
**Agent**: feature-developer-f5 (fourth worktree session)

## What shipped

| Req | Deliverable |
|-----|-------------|
| F1 | `bootstrap-consumer.sh --shape planning` — enumerated `PLANNING_CORE`/`PLANNING_LOCAL` ship lists + documented never-ship contract (no pyproject/tests/conftest/ci-check/pattern_lint/venv), tested both directions; `doctor.d/` ships whole (applicability is runtime); planning pre-commit variant (`language: system`); planning manifest; `--target-path`/`--target-github` (validated, written literally, conflict-checked against an existing section) |
| F2 | CLAUDE.md `kit-install` region via `kit_markers` (append-if-absent; **seeds from an existing `## Target Repository` section** — whole-section parse); the KIT-ADR-0024 grep convention untouched; absorbs KIT-0027 |
| F3 | Doctor per-shape inclusion fills the KIT-0046 P2 seam: `# shapes:` headers (case-insensitive incl. tokens, 30-line window, empty declaration runs everywhere); absent record = single; malformed/unreadable = full set + `DOCTOR:shape-record:FAIL` (incl. non-"region not found" reader failures) |
| F4 | Planning pre-commit: whitespace/eof/check-yaml + validate-task-status on system python3 |
| F5 | KIT-0027 annotated + retired to `6-canceled` |
| — | **Sync shape guard**: `cmd_sync` refuses planning/malformed-shaped repos (exit 2) — the engine selects from the UPSTREAM manifest and would install toolchain files; **KIT-0049 filed** for shape-scoped subsets |

## The headline: the KIT-0043 vector is PINNED

Mid-task, the GIT_DIR corruption class **recurred** — and this time was
root-caused: **class-scoped test fixtures execute outside the
function-scoped conftest GIT_* isolation.** Under the pytest-fast
pre-commit hook, a class-scoped bootstrap fixture inherited the exported
`GIT_DIR`; bootstrap's `git init`/`add -A`/`commit` hit the real worktree
repo (scaffold commit onto the feature branch, `core.bare` flipped on the
primary — the exact KIT-0043 damage signature, previously never pinned).
Recovered in ~3 commands via the KIT-0043 playbook. Closed with three
layers, all in this PR: **session-scoped autouse GIT_* scrub in
`tests/conftest.py`** (ships to consumers), explicitly scrubbed test-helper
envs, and bootstrap scrubbing GIT_* itself + `-e .git` (a worktree can
never be re-initialized). **Verified by re-running the suite under the
exact hostile GIT_DIR: refs and config untouched.** The canary caught the
damage within one commit — the KIT-0043 discipline worked.

## Review state

- **CI**: green. **BugBot**: pass. **CodeRabbit**: completing re-review of the final test-only commit at handoff time.
- **Bots**: 9 threads / 4 rounds — 8 real + fixed (the sync-engine High only BugBot saw — verified against `sync_from_manifest.py`; section desync; section window; token case; shift guard; branch-duplication hoist; regions fail-loud; round-4 test-quality catch: the guarded-shift branch is now truly exercised), 1 declined with evidence (type-hints "learnings" nitpick vs this repo's actual convention).
- **Evaluators** (trio BEFORE PR — the widened rule): fast-v2 CONCERNS / o3 FAIL / claude-code CHANGES_REQUESTED — 7 accepted (reader fail-loud; empty/case/window header handling, which exposed a real `\s`-eats-newline regex bug; **heredoc injection** with a hostile-`$(touch)` literality test; slug validation; IFS reset), 9 declined with evidence. Disposition: `.kit/context/reviews/KIT-0048-evaluator-review.md`.
- **Scratch e2e**: bootstrap → lifecycle → doctor (5 pass / 0 fail / 3 skip, shape-declared SKIP on the toolchain check) → **preflight 7/7** — all on system Python 3.14.3 with **no pyproject/tests/venv anywhere**. Broken-assumption probe: a stray pyproject does not resurrect toolchain checks.
- **N1**: flagless and `--shape single` tree-identical (sha256 characterization test — held as the regression net through the incident recovery).

## Reviewer attention points

1. `tests/conftest.py` session-scoped scrub **ships to consumers** (top-level conftest copy)
2. Bootstrap CLAUDE.md writes switched heredoc → `printf '%s'` (injection fix) — review the literality test
3. Planning manifest `core_version` hardcoded per the existing consumer-manifest precedent
4. The sync guard is a stopgap — KIT-0049 (backlog) holds the real design

## Post-merge planner actions

- `git worktree remove ../ask-worktrees/KIT-0048` (may need `--force`: untracked evaluator input — the KIT-0046 wrinkle; gitignore-inputs decision still open)
- `./scripts/core/project complete KIT-0048`; delete branch; KIT-0049 sits in backlog
- Retro: `.kit/context/retros/KIT-0048-retro.md` (five-incident Incident Closure)

# Review Starter: KIT-0077

**Task**: KIT-0077 — Dedup cleanup (context archive, dispatch retirement, doc archival)
**Task File**: `.kit/tasks/4-in-review/KIT-0077-dedup-cleanup.md`
**Branch**: `feature/KIT-0077-dedup-cleanup` → `main`
**PR**: https://github.com/movito/agentive-starter-kit/pull/101
**Binding source**: `.kit/context/reviews/DEDUP-ANALYSIS-2026-07-28.md`

## Implementation Summary

Executes the five operator-approved dedup dispositions. 130 files changed,
**104 of them pure `git mv`** — reviewable non-move churn is ~270 lines.

- **F1**: 100 finished-task handoffs/starters/session records → `.kit/context/archive/`
- **F2**: dispatch-kit retired from this repo's local adoption
- **F3**: `UPGRADE-0.4.0.md` and the Serena use-case matrix → `docs/archive/`
- **F4**: **verdict — keep both review templates** (the overlap is refuted)
- **F5**: three builder-only commands annotated

## Files Changed

### Moves (104, content-identical)
- 100 × `.kit/context/*` → `.kit/context/archive/`
- `.kit/docs/UPGRADE-0.4.0.md` → `docs/archive/`
- `.serena/claude-code/USE-CASES.md` → `docs/archive/SERENA-USE-CASES.md`
- `.dispatch/config.yml` → `docs/archive/dispatch-config.yml.archived`
- the task spec, `2-todo` → `3-in-progress`

### Behavior changes
- `scripts/local/engine-export.sh` — `rm -rf .kit/context/archive/` (leak fix)
- `scripts/local/engine-materials.sh` — `--exclude='context/archive/'` (leak fix)
- `scripts/optional/setup-dev.sh` — `--with-dispatch` gate + 2 steps removed (**2.0.0**)
- `pyproject.toml` — the `local` extra removed
- `.gitignore` — `.dispatch/` runtime entries **kept** (see §3)

### Agent/command/doc surfaces
- `.claude/agents/code-reviewer.md` (1.1.0) — unguarded `dispatch emit` → verdict reporting
- `.claude/commands/wrap-up.md` (2.0.0) — dispatch step removed; summary-honesty rule added
- `.claude/commands/{new-project,setup-preset}.md` — `distribution: builder-only`
- `.claude/agents/{test-runner,powertest-runner}.md`, `.serena/claude-code/{SETUP-GUIDE,TYPESCRIPT-SETUP}.md` — USE-CASES repoints
- `.claude/skills/review-handoff/SKILL.md`, `.kit/context/workflows/TASK-COMPLETION-PROTOCOL.md` — archive repoints
- `.kit/context/README.md` — archive section + **both template roles named** (closes F4)
- `.kit/docs/KIT-MIGRATION-PLAYBOOK.md`, `.kit/context/workflows/WORKTREE-WORKFLOW.md`, `scripts/local/new-worktree.sh`, `.claude/agents/bootstrap.md` — dispatch sweep

### New
- `.kit/context/archive/README.md` — the archive contract
- `tests/test_setup_door.py::test_new_export_carries_no_planning_corpus`
- `tests/test_engine_materials.py::test_context_archive_not_shipped`

## ⚠️ What the reviewer should check hardest

### 1. The two leak regressions (the real risk in this PR)

Moving files into a subdirectory put them **below both engines' depth-1
sweeps**. Unfixed, every newly created project would ship this repo's
entire session history.

| Engine | Mechanism that missed it | Fix |
|---|---|---|
| `engine-export.sh` | `find .kit/context/ -maxdepth 1 -delete` | explicit `rm -rf` |
| `engine-materials.sh` | `--exclude='context/[A-Z]*-NNNN*'`, anchored at depth 1 | `--exclude='context/archive/'` |

Both guards were **sabotage-verified**: each fails with its engine's exclude
removed, passes with it restored. Note the export guard was *vacuous until
committed* — `engine-export.sh` exports `git archive HEAD`, so uncommitted
moves never appeared. Re-verified post-commit (92 files leak when sabotaged).

### 2. Archive membership — judgment calls

Mechanical rule: task ID in `5-done`/`6-canceled`/`7-blocked`/`8-archive`
(the spec named only 5/6/7; `8-archive` is unambiguously terminal).

Beyond that I archived **8 dated one-offs** with no live citer. Six are
independently corroborated — `engine-materials.sh` *already* excluded those
exact patterns (`*SESSION-HANDOVER*`, `*LINEAR-SYNC*`, `*MIRIAD*`,
`*code-review-lessons*`, `*code-review-test*`) as kit-only planning corpus.
The other two: `CI-CHECKER-FIX-REVIEW-STARTER.md`, `RELEASE-0.3.0-REVIEW-STARTER.md`.

**Kept flat deliberately**: `ASK-UNIFIED-REGISTRY-TASK-STARTER.md` — live
citer in `.kit/tasks/1-backlog/ASK-0048-*.md`.

**Flagged**: `KIT-0030` is in `7-blocked` and its five artifacts archived per
spec — but it is slated for unblocking in the downstream pass. Reversible.

### 3. The dispatch keep/remove line

**Builder-only surfaces lose dispatch; shipped-and-guarded surfaces keep it.**

`movito/dispatch-kit` is still a *downstream consumer* of this repo's synced
core scripts (`sync-core-scripts.yml:73`) — a different thing from the local
integration the operator retired. So the `command -v dispatch`-guarded emits
in `scripts/core/*.sh` and the shipped commands stay;
`tests/test_preflight_check.py:214` stubs `dispatch` precisely because that
path is expected to exist. Removed only the **unguarded instructions**
(code-reviewer agent, `/wrap-up`) that told an agent to run a missing command.

**⚠️ Corrected mid-PR — I initially got this wrong.** I first assumed those
guarded emits were dead no-ops on this machine and, per the handoff, deleted
the `.dispatch/` entries from `.gitignore`. Then a preflight run
**regenerated `.dispatch/bus.jsonl` in this worktree**: `dispatch` is
installed globally at `/Library/Frameworks/Python.framework/Versions/3.11/bin/`,
so the guard succeeds and the emits really fire. Un-ignoring that file would
have left regenerating runtime debris exposed to the next `git add -A`. The
`.gitignore` entries are **restored**, with the evidence in a comment.

The operator's "dispatch-kit is no longer in use" means the *workflow* no
longer runs on it (no transitions, no spawning) — not that the CLI is absent.
The retirement therefore covers adoption (config, installer, agent
instructions), not the runtime debris the shipped scripts still produce.

Consequently **out of scope**: the sync matrix, `DISTRIBUTION-ARCHITECTURE.md`,
`scripts/README.md`, KIT-0026/0031/0045/0072.

## Gates

| Gate | State |
|---|---|
| CI | ✅ green ×2 rounds (Lint + Python 3.10/3.12/3.14) |
| CodeRabbit | ✅ **APPROVED** (round 1: CHANGES_REQUESTED → 1 fixed, 1 refuted) |
| Bugbot | ✅ pass round 1; `skipping` round 2 (KIT-0062 F6 state) |
| Threads | ✅ 0 unresolved (2 of 2 answered + resolved) |
| Evaluator | ✅ fast-only by design — `.kit/context/reviews/KIT-0077-evaluator-review.md` |
| Tests | ✅ 817 passed, 12 skipped |

⚠️ **The round-1 check status said `pass` while CodeRabbit had filed
CHANGES_REQUESTED.** KIT-0062 holds — threads are the truth.

## Bot round 1 triage

| Finding | Disposition |
|---|---|
| `/wrap-up` summary prints a retro path that may not exist | **FIXED** at the template; extended to the adjacent unmerged-PR case |
| Add `../../` to archived-doc paths in `SETUP-GUIDE.md` | **REFUTED** — 0 markdown links in the file; convention is repo-relative (`main`'s line was already repo-relative; line 547 points outside `.serena/`) |

## Evaluator triage (fast-only, CONCERNS)

| Finding | Disposition |
|---|---|
| `context/archive/` exclusion untested for non-task-ID files | **CONFIRMED → FIXED** (9 such files exist; guard added) |
| `pyproject` 0.9.0 vs `[Unreleased]` | **REFUTED** — Keep a Changelog; the release task bumps it (`21fbfc4` did) |
| `setup-dev.sh` errors on removed flag | **REJECTED** — designed behavior (PR #98 rule); all in-tree calls flagless |
| `/wrap-up` `gh` error handling | **OUT OF SCOPE** — pre-existing, only renumbered |

## 🔍 Requested merge gate

**Planner tree-grounded verification**, per the handoff — not the trio.
Priority: the archive membership rule, the dispatch keep/remove line, the two
engine leak fixes.

## Known, deliberately unfixed

Six **pre-existing** dangling doc references surfaced by the link sweep (all
absent on `main` too, none touched by this PR): `.kit/context/SERENA-TYPESCRIPT-VALIDATION.md`,
`.kit/context/TASK-0102-HANDOFF-implementation-agent.md`,
`.kit/context/workflows/API-TESTING-WORKFLOW.md`, `docs/EVALUATION-WORKFLOW.md`,
`docs/LINEAR-SYNC-BEHAVIOR.md`, `docs/external/api-reference.md`. Follow-up candidate.

# KIT-0024: Core Scripts Standardization — Cross-Project

**Status**: In Progress
**Priority**: High
**Type**: Infrastructure
**Estimated Effort**: 4-6 hours (downstream repos only — Phase 1 complete)
**Created**: 2026-03-08
**Updated**: 2026-03-26
**Cross-Project**: ASK-0042, DSP-0067, ADV-0052, AEL-0012

## Summary

Standardize the `scripts/` directory across all four agentive projects. Establish
agentive-starter-kit as the canonical source for 14 core scripts, adopt a
`scripts/core/` + `scripts/local/` directory layout in every repo, and set up
automated sync PRs via GitHub Actions.

**Phase 1 (ASK-0042) is complete** — agentive-starter-kit has the canonical layout
at `scripts/core/` v1.2.0. Remaining work is Phase 2 (downstream adoption) and
Phase 3 (first sync cycle verification).

## Background

Analysis on 2026-03-08 (during ADV-0051) revealed:

- 4 repos maintain independent copies of ~15 shared scripts
- 13/15 shared files have diverged between dispatch-kit and agentive-starter-kit
- adversarial-workflow is missing 12 scripts; 6/7 slash commands are broken
- No sync mechanism exists — scripts were bootstrapped once and then drifted
- Full analysis: `adversarial-workflow/.agent-context/research/SCRIPTS-SYNC-ANALYSIS.md`

## Design Decisions (Locked 2026-03-08)

1. **`project` is core** — standardized across repos, parameterized via `pyproject.toml`
2. **Directory layout**: `scripts/core/` (synced) + `scripts/local/` (project-specific)
3. **Automated sync PRs** via GitHub Action in agentive-starter-kit
4. **agentive-starter-kit is the source of truth** for all core scripts
5. **Hybrid sync for `.claude/` commands** (Locked 2026-03-26) — core-dependent commands sync automatically; workflow-only commands (`/babysit-pr`, `/retro`, etc.) are optional opt-in
6. **Manifest-based ownership** (Locked 2026-03-26) — sync Action only writes files listed in `.core-manifest.json`; local commands are never touched. See KIT-ADR-0022.

Full design: `adversarial-workflow/.agent-context/research/CORE-SCRIPTS-DESIGN.md`

## Core Bundle (14 files, v1.2.0)

| # | Script | Purpose |
|---|--------|---------|
| 1 | `project` | Task management CLI |
| 2 | `ci-check.sh` | Local CI mirror (format, lint, test) |
| 3 | `verify-ci.sh` | GitHub Actions status check |
| 4 | `verify-setup.sh` | Dev environment verification |
| 5 | `check-bots.sh` | PR bot review status |
| 6 | `wait-for-bots.sh` | Poll for bot reviews |
| 7 | `gh-review-helper.sh` | PR thread management (GraphQL) |
| 8 | `preflight-check.sh` | 7-gate quality verification |
| 9 | `check-sync.sh` | Manual drift detection across repos |
| 10 | `pattern_lint.py` | Code quality linter (DK rules) |
| 11 | `validate_task_status.py` | Task status/folder validation |
| 12 | `logging_config.py` | Shared logging utility |
| 13 | `__init__.py` | Package marker |
| 14 | `VERSION` | Core bundle version (currently 1.2.0) |

## Slash Commands & Skills (sync scope)

Downstream repos also need these `.claude/` artifacts to work with the core scripts.
These were added or updated after the original task was written:

| Command/Skill | Added | Notes |
|---------------|-------|-------|
| `/babysit-pr` | 2026-03-26 | Monitor PR through bot reviews, triage, fix, repeat |
| `/triage-threads` | 2026-03-26 | Fetch and triage review threads on current PR |
| `/retro` | 2026-03-26 | Structured session retrospective |
| `/check-spec` | post-ASK-0042 | Check spec compliance |
| `/status` | post-ASK-0042 | Show active tasks and project progress |
| `/check-ci` | pre-ASK-0042 | Verify GitHub Actions CI status |
| `/check-bots` | pre-ASK-0042 | Check bot review status |
| `/wait-for-bots` | pre-ASK-0042 | Poll for bot reviews |
| `/commit-push-pr` | pre-ASK-0042 | Commit, push, and open PR |
| `/start-task` | pre-ASK-0042 | Create branch and start task |
| `/preflight` | pre-ASK-0042 | Check completion gates before review |

**Decision (Locked 2026-03-26)**: Hybrid sync policy for `.claude/` artifacts.
Core-dependent commands (those referencing `scripts/core/`) are synced automatically.
Workflow-only commands (`/babysit-pr`, `/retro`, `/triage-threads`, `/status`,
`/check-spec`) are placed in an optional layer that downstream repos can opt into.
This avoids forcing workflow opinions on repos that only need the scripts, while
keeping consistent tooling available for repos that want the full experience.

## Execution Order

### Phase 1: ASK-0042 — Establish core in agentive-starter-kit -- COMPLETE

Completed in PR #31 (merged 2026-03-15). Core scripts v1.2.0 after ASK-0045 fixes.

- [x] Created `scripts/core/` with VERSION file
- [x] Reconciled DK/ASK differences
- [x] Parameterized hardcoded values
- [x] Moved 14 core scripts into `scripts/core/`
- [x] Moved ASK-specific scripts to `scripts/local/`
- [x] Created `scripts/optional/` for opt-in scripts
- [x] Created `scripts/.core-manifest.json`
- [x] Updated all references (slash commands, pre-commit, agent definitions)
- [x] Created `scripts/core/check-sync.sh`
- [x] Created `.github/workflows/sync-core-scripts.yml`
- [x] Fixed Linear sync import paths (ASK-0045, PR #38)

### Phase 2: Downstream repos (REMAINING)

Each repo receives the canonical core from ASK:

- **ADV-0052**: adversarial-workflow — most urgent (6 broken slash commands)
- **DSP-0067**: dispatch-kit — move DK-specific scripts to `local/`
- **AEL-0012**: adversarial-evaluator-library — minimal footprint, just adopt layout

### Phase 3: First sync cycle

After all repos are restructured, push a trivial change to `scripts/core/`
in ASK and verify the GitHub Action opens PRs in all 3 downstream repos.

**Prerequisite**: `CROSS_REPO_TOKEN` secret must be configured in ASK's GitHub
repo settings for the sync Action to open PRs in downstream repos.

## Parameterization Requirements

These values are currently hardcoded and must be read from `pyproject.toml` or env:

| Value | Current Hardcoding | Solution |
|-------|-------------------|----------|
| Python version range | `verify-setup.sh`: "3.10-3.12" | Read `[project] requires-python` |
| Target directories | `ci-check.sh`: `src/`, `scripts/` | Read `[tool.ci-check] targets` or default to `.` |
| Project name | `verify-setup.sh`: "adversarial-workflow" | Read `[project] name` |
| Evaluator library version | `project`: `v0.5.2` / `v0.5.3` | Read `[tool.adversarial] library_version` |
| Pattern lint step | `ci-check.sh`: conditional | Run if `scripts/core/pattern_lint.py` exists |
| Preflight gates | `preflight-check.sh`: fixed list | Skip missing gates gracefully |

## Acceptance Criteria

- [x] `scripts/core/` exists in agentive-starter-kit with canonical contents
- [x] `scripts/local/` exists in agentive-starter-kit for project-specific scripts
- [x] `scripts/.core-manifest.json` exists in agentive-starter-kit
- [x] `.github/workflows/sync-core-scripts.yml` created
- [ ] `scripts/core/` exists in all 3 downstream repos with identical contents
- [ ] `scripts/local/` exists in all 3 downstream repos
- [ ] `scripts/.core-manifest.json` exists in all 3 downstream repos
- [ ] All slash commands work in all 4 repos
- [ ] GitHub Action in ASK successfully opens sync PRs in downstream repos
- [ ] `scripts/core/check-sync.sh` reports no drift after initial sync
- [ ] Pre-commit hooks pass in all 4 repos
- [ ] No scripts remain at `scripts/` root in any repo (except README.md, manifest)

## Downstream Task References

| Task | Repo | Depends On | Status | Priority |
|------|------|-----------|--------|----------|
| ASK-0042 | agentive-starter-kit | — | **Done** (PR #31) | — |
| ADV-0052 | adversarial-workflow | ASK-0042 | Pending | P1 (6 broken commands) |
| DSP-0067 | dispatch-kit | ASK-0042 | Pending | P2 |
| AEL-0012 | adversarial-evaluator-library | ASK-0042 | Pending | P3 (minimal scripts) |

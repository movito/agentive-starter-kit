# KIT-0024: Core Scripts Standardization — Cross-Project

**Status**: Todo
**Priority**: High
**Type**: Infrastructure
**Estimated Effort**: 6-8 hours (across all repos)
**Created**: 2026-03-08
**Cross-Project**: ASK-0042, DSP-0067, ADV-0052, AEL-0012

## Summary

Standardize the `scripts/` directory across all four agentive projects. Establish
agentive-starter-kit as the canonical source for 12 core scripts, adopt a
`scripts/core/` + `scripts/local/` directory layout in every repo, and set up
automated sync PRs via GitHub Actions.

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

Full design: `adversarial-workflow/.agent-context/research/CORE-SCRIPTS-DESIGN.md`

## Core Bundle (12 scripts)

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
| 9 | `pattern_lint.py` | Code quality linter (DK rules) |
| 10 | `validate_task_status.py` | Task status/folder validation |
| 11 | `logging_config.py` | Shared logging utility |
| 12 | `__init__.py` | Package marker |

## Execution Order

### Phase 1: ASK-0042 — Establish core in agentive-starter-kit (DO FIRST)

This is the upstream work. All other tasks depend on it.

1. Create `scripts/core/` with VERSION file (v1.0.0)
2. Reconcile DK/ASK differences — pick best version of each script
3. Parameterize hardcoded values (project names, Python versions, target dirs)
4. Move 12 core scripts into `scripts/core/`
5. Move ASK-specific scripts to `scripts/local/`
6. Create `scripts/optional/` for opt-in scripts (Linear sync, create-agent, setup-dev)
7. Create `scripts/.core-manifest.json`
8. Update all references (slash commands, pre-commit, agent definitions)
9. Create `scripts/core/check-sync.sh` for manual drift detection
10. Create `.github/workflows/sync-core-scripts.yml`

### Phase 2: Downstream repos (AFTER Phase 1)

Each repo receives the canonical core from ASK:

- **ADV-0052**: adversarial-workflow — most urgent (6 broken slash commands)
- **DSP-0067**: dispatch-kit — move DK-specific scripts to `local/`
- **AEL-0012**: adversarial-evaluator-library — minimal footprint, just adopt layout

### Phase 3: First sync cycle

After all repos are restructured, push a trivial change to `scripts/core/`
in ASK and verify the GitHub Action opens PRs in all 3 downstream repos.

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

- [ ] `scripts/core/` exists in all 4 repos with identical contents
- [ ] `scripts/local/` exists in all 4 repos for project-specific scripts
- [ ] `scripts/.core-manifest.json` exists in all 4 repos
- [ ] All slash commands work in all 4 repos
- [ ] GitHub Action in ASK successfully opens sync PRs in downstream repos
- [ ] `scripts/core/check-sync.sh` reports no drift after initial sync
- [ ] Pre-commit hooks pass in all 4 repos
- [ ] No scripts remain at `scripts/` root (except README.md)

## Downstream Task References

| Task | Repo | Depends On | Priority |
|------|------|-----------|----------|
| ASK-0042 | agentive-starter-kit | — | P0 (do first) |
| ADV-0052 | adversarial-workflow | ASK-0042 | P1 (6 broken commands) |
| DSP-0067 | dispatch-kit | ASK-0042 | P2 |
| AEL-0012 | adversarial-evaluator-library | ASK-0042 | P3 (minimal scripts) |

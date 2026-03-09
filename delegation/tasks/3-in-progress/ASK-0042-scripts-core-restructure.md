# ASK-0042: Restructure scripts/ to core/ + local/ + optional/

**Status**: In Progress
**Priority**: High
**Type**: Infrastructure
**Estimated Effort**: 2-3 hours
**Created**: 2026-03-08
**Depends On**: None (this is the upstream — do first)
**Parent**: KIT-0024 (Core Scripts Standardization)
**Blocks**: ADV-0052, DSP-0067, AEL-0012

## Summary

Establish agentive-starter-kit as the canonical source for core scripts.
Restructure `scripts/` into `core/` + `local/` + `optional/` layout.
Parameterize hardcoded values so core scripts work in any project.
Create the GitHub Action that syncs core scripts to downstream repos.

## Current State

- 17 scripts in flat `scripts/` directory
- Scripts have metadata headers but no automated sync
- Several scripts have project-specific hardcoding
- dispatch-kit has diverged on 13/15 shared files

## Scope

### 1. Create directory structure

```
scripts/
  ├── core/                        ◀── 12 shared scripts (synced to downstream)
  │   ├── VERSION                  ◀── "1.0.0"
  │   ├── project
  │   ├── ci-check.sh
  │   ├── verify-ci.sh
  │   ├── verify-setup.sh
  │   ├── check-bots.sh
  │   ├── wait-for-bots.sh
  │   ├── gh-review-helper.sh
  │   ├── preflight-check.sh
  │   ├── pattern_lint.py
  │   ├── validate_task_status.py
  │   ├── logging_config.py
  │   ├── __init__.py
  │   └── check-sync.sh           ◀── drift detection tool
  ├── local/                       ◀── ASK-specific scripts
  │   └── bootstrap.sh
  ├── optional/                    ◀── opt-in scripts for downstream
  │   ├── linear_sync_utils.py
  │   ├── sync_tasks_to_linear.py
  │   ├── create-agent.sh
  │   └── setup-dev.sh
  ├── .core-manifest.json
  └── README.md
```

### 2. Reconcile script differences

For each of the 12 core scripts, pick the best version between ASK and DK:

| Script | Best Source | Action Needed |
|--------|-----------|---------------|
| `project` | ASK (44KB, most features) | Parameterize evaluator library version |
| `ci-check.sh` | ASK (has pattern lint step) | Parameterize target directories |
| `verify-ci.sh` | DK (newer, 2026-02-26) | Pull DK version into ASK |
| `verify-setup.sh` | Either (identical) | Parameterize Python version + project name |
| `check-bots.sh` | ASK (newer) | No changes needed |
| `wait-for-bots.sh` | ASK (newer) | No changes needed |
| `gh-review-helper.sh` | Either (identical) | No changes needed |
| `preflight-check.sh` | ASK (newer) | Skip missing gates gracefully |
| `pattern_lint.py` | DK (newer, more rules) | Pull DK version into ASK |
| `validate_task_status.py` | ASK (specific exceptions) | No changes needed |
| `logging_config.py` | Either (identical) | No changes needed |
| `__init__.py` | Either (identical) | No changes needed |

### 3. Parameterize hardcoded values

Read from `pyproject.toml` instead of hardcoding:

```toml
# pyproject.toml — new sections for core scripts
[project]
name = "agentive-starter-kit"
requires-python = ">=3.10,<3.13"

[tool.core-scripts]
ci_targets = ["src/", "scripts/", "tests/"]   # for ci-check.sh
```

### 4. Update all references

- `.claude/commands/*.md` — `./scripts/X` → `./scripts/core/X`
- `.pre-commit-config.yaml` — update hook entry paths
- `.claude/agents/*.md` — update script references
- Any CI workflows

### 5. Create GitHub Action for sync

`.github/workflows/sync-core-scripts.yml`:
- Triggers on push to `scripts/core/**` on `main`
- Matrix strategy: dispatch-kit, adversarial-workflow, adversarial-evaluator-library
- Creates branch, copies core/, updates manifest, opens PR
- Requires `CROSS_REPO_TOKEN` secret with repo scope

### 6. Create check-sync.sh

Manual drift detection tool:
```bash
./scripts/core/check-sync.sh           # report drift
./scripts/core/check-sync.sh --apply   # pull latest from ASK
```

## Acceptance Criteria

- [ ] `scripts/core/` contains 12 scripts + VERSION + check-sync.sh
- [ ] `scripts/local/` contains ASK-specific scripts
- [ ] `scripts/optional/` contains opt-in scripts
- [ ] No scripts remain at `scripts/` root (except README.md)
- [ ] All parameterized values read from `pyproject.toml`
- [ ] All slash commands work with new paths
- [ ] Pre-commit hooks pass
- [ ] GitHub Action created (test with dry-run if possible)
- [ ] `scripts/.core-manifest.json` created
- [ ] `scripts/core/VERSION` contains `1.0.0`

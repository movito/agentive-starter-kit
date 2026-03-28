# Upgrading to v0.4.0

This release restructures `scripts/` into three subdirectories. Every script
path changed, so downstream projects need a coordinated migration.

## What Changed

```
# Before (v0.3.x)                    # After (v0.4.0)
scripts/                              scripts/
  project                               core/
  ci-check.sh                             project
  verify-ci.sh                            ci-check.sh
  verify-setup.sh                         verify-ci.sh
  pattern_lint.py                         verify-setup.sh
  validate_task_status.py                 pattern_lint.py
  check-bots.sh                           validate_task_status.py
  wait-for-bots.sh                        check-bots.sh
  gh-review-helper.sh                     wait-for-bots.sh
  preflight-check.sh                      gh-review-helper.sh
  logging_config.py                       preflight-check.sh
  __init__.py                             logging_config.py
                                          __init__.py
  bootstrap.sh                            check-sync.sh
  setup-dev.sh                            VERSION
  create-agent.sh                       local/
  linear_sync_utils.py                    bootstrap.sh
  sync_tasks_to_linear.py              optional/
                                          create-agent.sh
                                          setup-dev.sh
                                          linear_sync_utils.py
                                          sync_tasks_to_linear.py
                                          __init__.py
                                        .core-manifest.json
```

**Core** = shared across all agentive projects (synced automatically).
**Local** = project-specific scripts (never overwritten).
**Optional** = available to copy into `local/` if needed.

## Migration Steps

### Step 1: Move scripts into subdirectories

```bash
# Create directories
mkdir -p scripts/core scripts/local scripts/optional

# Move core scripts
for f in project ci-check.sh verify-ci.sh verify-setup.sh pattern_lint.py \
         validate_task_status.py check-bots.sh wait-for-bots.sh \
         gh-review-helper.sh preflight-check.sh logging_config.py __init__.py; do
  [ -f "scripts/$f" ] && git mv "scripts/$f" "scripts/core/$f"
done

# Move local scripts (project-specific)
for f in bootstrap.sh; do
  [ -f "scripts/$f" ] && git mv "scripts/$f" "scripts/local/$f"
done

# Move optional scripts
for f in create-agent.sh setup-dev.sh linear_sync_utils.py \
         sync_tasks_to_linear.py; do
  [ -f "scripts/$f" ] && git mv "scripts/$f" "scripts/optional/$f"
done

# Create optional __init__.py
touch scripts/optional/__init__.py
```

If your project has additional scripts in `scripts/`, decide whether they
belong in `core/` (shared), `local/` (project-specific), or `optional/`
(available but not synced).

### Step 2: Add VERSION and manifest

```bash
echo "1.2.0" > scripts/core/VERSION
```

Copy `scripts/.core-manifest.json` from agentive-starter-kit, or create it:

```json
{
  "core_version": "1.2.0",
  "source": "agentive-starter-kit",
  "source_repo": "movito/agentive-starter-kit",
  "synced_at": "2026-03-09T00:00:00Z",
  "files": [
    "core/__init__.py",
    "core/check-bots.sh",
    "core/ci-check.sh",
    "core/gh-review-helper.sh",
    "core/logging_config.py",
    "core/pattern_lint.py",
    "core/preflight-check.sh",
    "core/project",
    "core/validate_task_status.py",
    "core/verify-ci.sh",
    "core/verify-setup.sh",
    "core/wait-for-bots.sh",
    "core/check-sync.sh",
    "core/VERSION"
  ]
}
```

### Step 3: Update path references

This is the most error-prone step. Every reference to `scripts/<name>` must
become `scripts/core/<name>` (or `scripts/local/` / `scripts/optional/` as
appropriate).

**Files that typically need updating:**

| File/Pattern | What to change |
|---|---|
| `.pre-commit-config.yaml` | `scripts/pattern_lint.py` -> `scripts/core/pattern_lint.py` |
| `.pre-commit-config.yaml` | `scripts/validate_task_status.py` -> `scripts/core/validate_task_status.py` |
| `.github/workflows/test.yml` | `scripts/pattern_lint.py` -> `scripts/core/pattern_lint.py` |
| `CLAUDE.md` | All script paths in tables and text |
| `.claude/agents/*.md` | `./scripts/project` -> `./scripts/core/project` |
| `.claude/agents/*.md` | `./scripts/ci-check.sh` -> `./scripts/core/ci-check.sh` |
| `.claude/agents/*.md` | `./scripts/verify-ci.sh` -> `./scripts/core/verify-ci.sh` |
| `.claude/commands/*.md` | Script path references |
| `.claude/skills/*/SKILL.md` | Script path references |
| `.kit/context/workflows/*.md` | Script path references |
| `pyproject.toml` | `testpaths`, coverage source paths |
| `tests/conftest.py` | Import paths for `pattern_lint`, `project`, etc. |
| `tests/test_*.py` | Import paths and `_script_path` definitions |

**Quick search to find all references:**

```bash
# Find remaining old-style paths (should return zero after migration)
grep -rn 'scripts/project\b' --include='*.md' --include='*.yml' --include='*.yaml' --include='*.py' --include='*.sh' --include='*.toml' | grep -v 'scripts/core/project' | grep -v 'scripts/optional/' | grep -v 'scripts/local/' | grep -v '.git/'
grep -rn 'scripts/ci-check' --include='*.md' --include='*.yml' --include='*.yaml' | grep -v 'scripts/core/'
grep -rn 'scripts/verify-' --include='*.md' --include='*.yml' --include='*.yaml' | grep -v 'scripts/core/'
grep -rn 'scripts/pattern_lint' --include='*.md' --include='*.yml' --include='*.yaml' --include='*.py' | grep -v 'scripts/core/'
```

### Step 4: Update `project` script path resolution

The `project` script resolves the repo root using `Path(__file__).resolve()`.
After moving from `scripts/project` to `scripts/core/project`, it needs one
extra `.parent`:

```python
# Before (scripts/project):
project_dir = Path(__file__).resolve().parent.parent

# After (scripts/core/project):
project_dir = Path(__file__).resolve().parent.parent.parent
```

There are two occurrences: in `cmd_setup()` and in `main()`. Both must be
updated. The comment should also be updated:

```python
# Get the project directory (parent of scripts/core/)
project_dir = Path(__file__).resolve().parent.parent.parent
```

### Step 5: Update test mocks

If your tests use `mock_project_path` from conftest.py (for mocking the
project script's path resolution), update the mock chain:

```python
# Before:
mock_path.return_value.resolve.return_value.parent.parent = mock_project_dir

# After:
mock_path.return_value.resolve.return_value.parent.parent.parent = mock_project_dir
```

### Step 6: Update `ci-check.sh` internal path

The `ci-check.sh` script resolves `pattern_lint.py` relative to itself.
After the move, it should use:

```bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "$SCRIPT_DIR/pattern_lint.py" $PY_FILES
```

(Both files are now in `scripts/core/`, so `$SCRIPT_DIR` resolves correctly.)

### Step 7: Run tests and verify

```bash
# Run full CI locally
./scripts/core/ci-check.sh

# Verify all old paths are gone
grep -rn 'scripts/project\b' . --include='*.md' --include='*.yml' --include='*.yaml' --include='*.py' --include='*.sh' --include='*.toml' | grep -v 'scripts/core/project' | grep -v 'scripts/optional/' | grep -v 'scripts/local/' | grep -v '.git/' | grep -v 'UPGRADE-0.4.0'
```

## Post-Migration: Automatic Sync

After migration, core scripts are kept in sync automatically:

1. Changes to `scripts/core/` on agentive-starter-kit's `main` branch trigger
   a GitHub Action
2. The Action opens a PR in your repo with the updated files
3. Review and merge the PR

For manual checking: `ASK_REPO=~/path/to/agentive-starter-kit ./scripts/core/check-sync.sh`

**Requirement**: The `CROSS_REPO_TOKEN` secret must be configured in the
agentive-starter-kit repo with write access to downstream repos.

## Additional Changes in v0.4.0

These changes are included in the core scripts update and don't require
separate migration steps:

- **DK002 lint rule**: `open()` / `.read_text()` / `.write_text()` without
  `encoding=` now triggers a warning. Add `encoding="utf-8"` or
  `# noqa: DK002` to suppress.
- **Python 3.10 compatibility**: `verify-setup.sh` and `project` use
  `tomllib`/`tomli` fallback for Python < 3.11.
- **Dynamic Python version checks**: `verify-setup.sh` reads version
  constraints from `pyproject.toml` instead of hardcoding them.

## Troubleshooting

**`FileNotFoundError: scripts/delegation/tasks`** when running `./scripts/core/project`:
The `project_dir` resolution wasn't updated. See Step 4.

**Pre-commit hooks fail with "file not found"**:
The `.pre-commit-config.yaml` still points to `scripts/pattern_lint.py`.
See Step 3.

**Tests fail with `ModuleNotFoundError`**:
Test files import from `scripts/core/` now. Check `_script_path` definitions
in test files. See Step 5.

**`check-sync.sh` reports drift immediately after migration**:
This is expected if your `scripts/core/` files diverge from upstream (e.g.,
project-specific modifications). The sync workflow will normalize this over
time.

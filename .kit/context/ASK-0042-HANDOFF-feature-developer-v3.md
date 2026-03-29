# ASK-0042 Handoff: Restructure scripts/ to core/ + local/ + optional/

## Mission

Establish agentive-starter-kit as the canonical source for 12 core scripts shared
across all agentive projects. Restructure `scripts/` into `core/` + `local/` +
`optional/`, parameterize hardcoded values, reconcile DK/ASK drift, and create
the GitHub Action that syncs core scripts to downstream repos.

## Task File

`.kit/tasks/2-todo/ASK-0042-scripts-core-restructure.md`

## RULES — Read Before Anything Else

1. **Do NOT spawn sub-agents.** Do all work yourself.
2. **Do NOT modify script logic** unless parameterizing a hardcoded value. This is a restructure, not a rewrite.
3. **Reconcile DK→ASK first** (Step 3), then restructure. Don't restructure stale files.
4. **Every path reference must be updated.** Grep thoroughly after moving files.
5. **First action**: Create branch and start task.

## Context

Analysis from 2026-03-08 found all four agentive repos (ASK, DK, ADW, AEL) maintain
independent script copies with no sync mechanism. 13/15 shared files have diverged.
adversarial-workflow has 6/7 broken slash commands due to missing scripts.

This task makes ASK the single source of truth. Three downstream tasks (ADV-0052,
DSP-0067, AEL-0012) depend on this completing first.

**Design doc**: `adversarial-workflow/.kit/context/research/CORE-SCRIPTS-DESIGN.md`
**GitHub issue**: https://github.com/movito/agentive-starter-kit/issues/30

## Current State

```
scripts/                          ◀── 17 files, flat layout
  ├── README.md
  ├── __init__.py
  ├── bootstrap.sh                ◀── ASK-specific
  ├── check-bots.sh               ◀── core (current, v1.0.0)
  ├── ci-check.sh                 ◀── core (current, 5 steps)
  ├── create-agent.sh             ◀── optional
  ├── gh-review-helper.sh         ◀── core (current, v1.0.0)
  ├── linear_sync_utils.py        ◀── optional
  ├── logging_config.py           ◀── core (current)
  ├── pattern_lint.py             ◀── core (OUTDATED — DK has v1.1.0 with DK002)
  ├── preflight-check.sh          ◀── core (current, v1.0.0)
  ├── project                     ◀── core (current, 44KB)
  ├── setup-dev.sh                ◀── optional
  ├── sync_tasks_to_linear.py     ◀── optional
  ├── validate_task_status.py     ◀── core (current)
  ├── verify-ci.sh                ◀── core (OUTDATED — DK has dispatch event emission)
  ├── verify-setup.sh             ◀── core (current)
  └── wait-for-bots.sh            ◀── core (current, v1.0.0)
```

**Pre-commit hooks** (3 local hooks reference scripts):
- `pattern-lint` → `python3 scripts/pattern_lint.py`
- `validate-task-status` → `python scripts/validate_task_status.py`
- `pytest-fast` → inline bash (no script reference)

**Slash commands** (10 files in `.claude/commands/`):
- `check-ci.md` → `./scripts/verify-ci.sh`
- `check-bots.md` → `./scripts/check-bots.sh`
- `wait-for-bots.md` → `./scripts/wait-for-bots.sh`
- `triage-threads.md` → `./scripts/gh-review-helper.sh`
- `preflight.md` → `./scripts/preflight-check.sh`
- `commit-push-pr.md` → `./scripts/preflight-check.sh`
- `start-task.md` → `./scripts/project`
- `status.md`, `retro.md`, `check-spec.md` → no script references

**GitHub workflows** (2 existing):
- `.github/workflows/sync-to-linear.yml`
- `.github/workflows/test.yml`

## Target State

```
scripts/
  ├── core/                        ◀── 12 scripts + VERSION + check-sync.sh (synced to downstream)
  │   ├── VERSION                  ◀── "1.0.0"
  │   ├── __init__.py
  │   ├── check-bots.sh
  │   ├── check-sync.sh           ◀── NEW: drift detection tool
  │   ├── ci-check.sh
  │   ├── gh-review-helper.sh
  │   ├── logging_config.py
  │   ├── pattern_lint.py          ◀── UPDATED from DK v1.1.0
  │   ├── preflight-check.sh
  │   ├── project
  │   ├── validate_task_status.py
  │   ├── verify-ci.sh             ◀── UPDATED from DK (dispatch events)
  │   ├── verify-setup.sh
  │   └── wait-for-bots.sh
  ├── local/                       ◀── ASK-specific
  │   └── bootstrap.sh
  ├── optional/                    ◀── downstream projects can copy these to their local/
  │   ├── create-agent.sh
  │   ├── linear_sync_utils.py
  │   ├── setup-dev.sh
  │   └── sync_tasks_to_linear.py
  ├── .core-manifest.json
  └── README.md                    ◀── updated to explain layout
```

## Step-by-Step Implementation

### Step 1: Create branch and start task

```bash
git checkout -b chore/ASK-0042-scripts-core-restructure
./scripts/project start ASK-0042
```

Read the task file after it moves to `3-in-progress/`.

### Step 2: Create directory structure

```bash
mkdir -p scripts/core scripts/local scripts/optional
```

### Step 3: Reconcile DK→ASK (pull newer versions)

Two scripts in dispatch-kit are newer than ASK. Pull them in before restructuring.

**pattern_lint.py** — DK has v1.1.0 (added DK002: `open()` without encoding):
```bash
cp /Users/broadcaster_three/Github/dispatch-kit/scripts/pattern_lint.py scripts/pattern_lint.py
```

**verify-ci.sh** — DK has dispatch event emission + `--wait`/`--timeout` flags:
```bash
cp /Users/broadcaster_three/Github/dispatch-kit/scripts/verify-ci.sh scripts/verify-ci.sh
```

Verify both still work:
```bash
python3 scripts/pattern_lint.py scripts/*.py
./scripts/verify-ci.sh --help
```

### Step 4: Parameterize hardcoded values

These changes make core scripts work in any project, not just ASK.

**4a. `verify-setup.sh`** — hardcodes project name and Python version range.

Find the line:
```bash
echo "❌ Python $PY_VERSION is too new (>=3.10, <3.13 required for adversarial-workflow)"
```

Replace `adversarial-workflow` with a dynamic lookup:
```bash
PROJECT_NAME=$(python3 -c "
import tomllib, pathlib
p = pathlib.Path('pyproject.toml')
print(tomllib.loads(p.read_text())['project']['name']) if p.exists() else print('this project')
" 2>/dev/null || echo "this project")
```

And read the Python version constraint from `pyproject.toml [project] requires-python`
instead of hardcoding `3.10-3.12`. If `pyproject.toml` is missing, fall back to `>=3.10`.

**4b. `ci-check.sh`** — hardcodes target directories for Black/isort/flake8.

Currently targets `.` (all Python files). This is actually fine for a generic default.
The pattern lint step already auto-discovers files. **No change needed** unless ASK
currently targets specific directories — check and confirm.

**4c. `project`** — hardcodes `EVALUATOR_LIBRARY_VERSION = "v0.5.2"`.

Change to read from `pyproject.toml`:
```python
def _get_evaluator_library_version():
    """Read evaluator library version from pyproject.toml, with fallback."""
    try:
        import tomllib
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)
        return config.get("tool", {}).get("adversarial", {}).get("library_version", "v0.5.3")
    except (FileNotFoundError, KeyError):
        return "v0.5.3"
```

Then add to each project's `pyproject.toml`:
```toml
[tool.adversarial]
library_version = "v0.5.3"
```

**4d. `preflight-check.sh`** — has 7 gates, some may not apply to all projects.

Make gates skip gracefully if the required tool/file doesn't exist. For example,
if `adversarial` CLI isn't installed, the evaluator gate should SKIP (not FAIL).
Check current behavior — it may already handle this.

### Step 5: Move scripts to their new locations

```bash
# Core scripts (12)
mv scripts/check-bots.sh scripts/core/
mv scripts/ci-check.sh scripts/core/
mv scripts/gh-review-helper.sh scripts/core/
mv scripts/logging_config.py scripts/core/
mv scripts/pattern_lint.py scripts/core/
mv scripts/preflight-check.sh scripts/core/
mv scripts/project scripts/core/
mv scripts/validate_task_status.py scripts/core/
mv scripts/verify-ci.sh scripts/core/
mv scripts/verify-setup.sh scripts/core/
mv scripts/wait-for-bots.sh scripts/core/
mv scripts/__init__.py scripts/core/

# Local (ASK-specific)
mv scripts/bootstrap.sh scripts/local/

# Optional (downstream can copy)
mv scripts/create-agent.sh scripts/optional/
mv scripts/linear_sync_utils.py scripts/optional/
mv scripts/setup-dev.sh scripts/optional/
mv scripts/sync_tasks_to_linear.py scripts/optional/
```

### Step 6: Create VERSION file

```bash
echo "1.0.0" > scripts/core/VERSION
```

### Step 7: Create .core-manifest.json

Write `scripts/.core-manifest.json`:
```json
{
  "core_version": "1.0.0",
  "source": "agentive-starter-kit",
  "source_repo": "movito/agentive-starter-kit",
  "synced_at": "2026-03-08T00:00:00Z",
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
    "core/wait-for-bots.sh"
  ]
}
```

### Step 8: Update all path references

This is the most error-prone step. Be thorough.

**8a. Slash commands** — update 7 files in `.claude/commands/`:

| File | Old Reference | New Reference |
|------|---------------|---------------|
| `check-ci.md` | `./scripts/verify-ci.sh` | `./scripts/core/verify-ci.sh` |
| `check-bots.md` | `./scripts/check-bots.sh` | `./scripts/core/check-bots.sh` |
| `wait-for-bots.md` | `./scripts/wait-for-bots.sh` | `./scripts/core/wait-for-bots.sh` |
| `triage-threads.md` | `./scripts/gh-review-helper.sh` | `./scripts/core/gh-review-helper.sh` |
| `preflight.md` | `./scripts/preflight-check.sh` | `./scripts/core/preflight-check.sh` |
| `commit-push-pr.md` | `./scripts/preflight-check.sh` | `./scripts/core/preflight-check.sh` |
| `start-task.md` | `./scripts/project` | `./scripts/core/project` |

**8b. Pre-commit config** — update `.pre-commit-config.yaml`:

```yaml
# Old
entry: python3 scripts/pattern_lint.py
# New
entry: python3 scripts/core/pattern_lint.py
```

```yaml
# Old
entry: python scripts/validate_task_status.py
# New
entry: python scripts/core/validate_task_status.py
```

**8c. Agent definitions** — grep `.claude/agents/` for `scripts/`:

```bash
grep -rn 'scripts/' .claude/agents/ | grep -v 'scripts/core/' | grep -v 'scripts/local/' | grep -v 'scripts/optional/'
```

Update every match to use the new path.

**8d. Workflows** — check `.github/workflows/` for script references:

```bash
grep -rn 'scripts/' .github/workflows/
```

**8e. Cross-script references** — `wait-for-bots.sh` calls `check-bots.sh` via `$SCRIPT_DIR`:

```bash
# In wait-for-bots.sh, around line 117:
"$SCRIPT_DIR/check-bots.sh"
```

Since both move to `core/`, `$SCRIPT_DIR` resolves correctly. **No change needed**
if `SCRIPT_DIR` is computed as `$(dirname "$0")`. Verify this.

**8f. Coverage exclusions** — `pyproject.toml` excludes specific script paths:

```toml
[tool.coverage.report]
omit = ["scripts/sync_tasks_to_linear.py", "scripts/validate_task_status.py"]
```

Update to:
```toml
omit = ["scripts/optional/sync_tasks_to_linear.py", "scripts/core/validate_task_status.py"]
```

### Step 9: Catch strays — comprehensive grep

After all moves and updates, verify no old paths remain:

```bash
# Find any remaining references to scripts/ that aren't core/local/optional
grep -rn '\./scripts/[a-z]' . \
  --include="*.md" --include="*.sh" --include="*.py" --include="*.yaml" --include="*.yml" --include="*.toml" \
  | grep -v 'scripts/core/' | grep -v 'scripts/local/' | grep -v 'scripts/optional/' \
  | grep -v '.git/' | grep -v '__pycache__' | grep -v '5-done/' | grep -v '8-archive/' \
  | grep -v 'ASK-0042' | grep -v 'KIT-0024' | grep -v 'HANDOFF'
```

Also check for bare `scripts/project`, `scripts/ci-check`, etc. without `./` prefix:

```bash
grep -rn 'scripts/project\|scripts/ci-check\|scripts/verify-ci\|scripts/check-bots\|scripts/pattern_lint\|scripts/preflight\|scripts/validate_task\|scripts/verify-setup\|scripts/wait-for\|scripts/gh-review' . \
  --include="*.md" --include="*.sh" --include="*.py" --include="*.yaml" --include="*.yml" --include="*.toml" \
  | grep -v 'scripts/core/' | grep -v '.git/' | grep -v '__pycache__' | grep -v '5-done/' | grep -v '8-archive/' \
  | grep -v 'ASK-0042' | grep -v 'KIT-0024' | grep -v 'HANDOFF'
```

Fix every match. Zero remaining = ready to proceed.

### Step 10: Create check-sync.sh

Write `scripts/core/check-sync.sh` — a drift detection tool that downstream repos
can use to compare their `scripts/core/` against ASK's. Basic implementation:

```bash
#!/usr/bin/env bash
# ---
# name: check-sync.sh
# description: Check if core scripts are in sync with agentive-starter-kit
# version: 1.0.0
# origin: agentive-starter-kit
# ---

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$SCRIPT_DIR/../.core-manifest.json"
VERSION_FILE="$SCRIPT_DIR/VERSION"

if [[ ! -f "$MANIFEST" ]]; then
    echo "❌ No .core-manifest.json found. Run from a project with core scripts installed."
    exit 1
fi

LOCAL_VERSION=$(cat "$VERSION_FILE" 2>/dev/null || echo "unknown")
echo "Core scripts version: $LOCAL_VERSION"
echo "Manifest: $MANIFEST"

# If ASK repo is available locally, compare
ASK_CORE="${ASK_REPO:-/Users/broadcaster_three/Github/agentive-starter-kit}/scripts/core"
if [[ -d "$ASK_CORE" ]]; then
    ASK_VERSION=$(cat "$ASK_CORE/VERSION" 2>/dev/null || echo "unknown")
    echo "Upstream version: $ASK_VERSION"
    echo ""

    DRIFT=0
    for f in "$SCRIPT_DIR"/*; do
        fname=$(basename "$f")
        [[ "$fname" == "VERSION" || "$fname" == "check-sync.sh" ]] && continue
        if [[ -f "$ASK_CORE/$fname" ]]; then
            if ! diff -q "$f" "$ASK_CORE/$fname" > /dev/null 2>&1; then
                echo "⚠️  DRIFT: $fname differs from upstream"
                DRIFT=$((DRIFT + 1))
            fi
        fi
    done

    if [[ $DRIFT -eq 0 ]]; then
        echo "✅ All core scripts match upstream ($ASK_VERSION)"
    else
        echo ""
        echo "❌ $DRIFT file(s) have drifted from upstream"
        echo "   Run with --apply to pull latest from ASK"
    fi
else
    echo "⚠️  ASK repo not found at $ASK_CORE"
    echo "   Set ASK_REPO env var to point to agentive-starter-kit checkout"
fi
```

This is a starter implementation. It checks local files against ASK if available.
The `--apply` flag can be added later.

### Step 11: Create GitHub Action for sync

Write `.github/workflows/sync-core-scripts.yml`:

```yaml
name: Sync Core Scripts to Downstream

on:
  push:
    paths: ['scripts/core/**']
    branches: [main]

jobs:
  sync:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        repo:
          - movito/dispatch-kit
          - movito/adversarial-workflow
          - movito/adversarial-evaluator-library
    steps:
      - name: Checkout source (agentive-starter-kit)
        uses: actions/checkout@v4
        with:
          path: source

      - name: Checkout target (${{ matrix.repo }})
        uses: actions/checkout@v4
        with:
          repository: ${{ matrix.repo }}
          token: ${{ secrets.CROSS_REPO_TOKEN }}
          path: target

      - name: Sync core scripts
        run: |
          VERSION=$(cat source/scripts/core/VERSION)
          BRANCH="chore/core-scripts-sync-v${VERSION}-$(date +%Y%m%d)"

          cd target
          git checkout -b "$BRANCH"

          # Copy core scripts
          rm -rf scripts/core
          cp -r ../source/scripts/core scripts/core

          # Update manifest
          cat > scripts/.core-manifest.json <<MANIFEST
          {
            "core_version": "$VERSION",
            "source": "agentive-starter-kit",
            "source_repo": "movito/agentive-starter-kit",
            "synced_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
          }
          MANIFEST

          # Check if anything changed
          if git diff --quiet && git diff --cached --quiet; then
            echo "No changes to sync"
            exit 0
          fi

          git add scripts/core/ scripts/.core-manifest.json
          git commit -m "chore: Sync core scripts v${VERSION} from agentive-starter-kit"
          git push -u origin "$BRANCH"

      - name: Create PR
        if: success()
        env:
          GH_TOKEN: ${{ secrets.CROSS_REPO_TOKEN }}
        run: |
          VERSION=$(cat source/scripts/core/VERSION)
          cd target
          BRANCH=$(git branch --show-current)

          # Only create PR if branch was pushed (changes existed)
          if git log origin/main.."$BRANCH" --oneline | grep -q .; then
            gh pr create \
              --title "chore: Sync core scripts v${VERSION} from agentive-starter-kit" \
              --body "Automated sync of \`scripts/core/\` from agentive-starter-kit v${VERSION}.

          Review the changes and merge when ready.

          **Source**: movito/agentive-starter-kit@main
          **Core version**: ${VERSION}" \
              --base main
          fi
```

**Note**: This requires a `CROSS_REPO_TOKEN` secret with `repo` scope on all target repos.
Create it as a GitHub Personal Access Token (fine-grained, scoped to the 3 downstream repos).

### Step 12: Update scripts/README.md

Rewrite to explain the new layout:

```markdown
# Scripts

## Directory Layout

### `core/` — Shared scripts (synced from agentive-starter-kit)

These scripts are shared across all agentive projects. **Do not edit locally in
downstream repos** — changes are made here in agentive-starter-kit and synced
via automated PRs.

Current version: see `core/VERSION`

### `local/` — Project-specific scripts

Scripts unique to this project. Never synced or overwritten.

### `optional/` — Opt-in scripts

Scripts that downstream projects can copy to their `local/` directory if needed.
Not synced automatically.

## Sync Mechanism

When `scripts/core/` changes on `main`, a GitHub Action opens PRs in:
- movito/dispatch-kit
- movito/adversarial-workflow
- movito/adversarial-evaluator-library

Downstream repos can also check sync status manually:
\`\`\`bash
./scripts/core/check-sync.sh
\`\`\`
```

### Step 13: Verify everything

```bash
# Structure
ls scripts/core/ | wc -l         # expect 14 (12 scripts + VERSION + check-sync.sh)
ls scripts/local/                 # expect bootstrap.sh
ls scripts/optional/ | wc -l     # expect 4

# No scripts at root (except README.md)
ls scripts/*.sh scripts/*.py 2>/dev/null   # should error / return nothing

# Old paths gone
grep -rn '\./scripts/verify-ci\.sh' .claude/ .pre-commit-config.yaml   # should return nothing

# Slash commands work
./scripts/core/verify-ci.sh --help
./scripts/core/check-bots.sh --help
./scripts/core/preflight-check.sh --help
./scripts/core/project list

# CI passes
./scripts/core/ci-check.sh

# Pre-commit passes
pre-commit run --all-files

# Tests pass
pytest tests/ -v

# Pattern lint works
python3 scripts/core/pattern_lint.py scripts/core/*.py

# Sync check works
./scripts/core/check-sync.sh
```

### Step 14: Commit and PR

**Commit message**:
```
chore: Restructure scripts/ to core/ + local/ + optional/ (ASK-0042)

Establish agentive-starter-kit as canonical source for 12 core scripts.
Move shared scripts to scripts/core/, ASK-specific to scripts/local/,
opt-in scripts to scripts/optional/. Update all path references in slash
commands, pre-commit config, agent definitions, and workflows.

Add sync infrastructure: VERSION file, .core-manifest.json, check-sync.sh,
and GitHub Action to open PRs in downstream repos on core changes.

Part of KIT-0024 (Core Scripts Standardization).
Unblocks: ADV-0052, DSP-0067, AEL-0012.
```

**PR title**: `chore: Restructure scripts/ to core/ + local/ + optional/ (ASK-0042)`

**PR body**:
```
## Summary
- Restructure `scripts/` into `core/` (synced) + `local/` (ASK-specific) + `optional/` (opt-in)
- Reconcile dispatch-kit drift: pull newer `pattern_lint.py` v1.1.0 and `verify-ci.sh`
- Parameterize hardcoded values (project name, Python version, evaluator library version)
- Update all 7 slash commands, pre-commit hooks, and agent definitions to use new paths
- Add sync infrastructure: VERSION, manifest, check-sync.sh, GitHub Action

## What this enables
Three downstream repos (adversarial-workflow, dispatch-kit, adversarial-evaluator-library)
will adopt the same layout. The GitHub Action will keep them in sync automatically.

Ref: KIT-0024, https://github.com/movito/agentive-starter-kit/issues/30

## Test plan
- [ ] All slash commands work with new paths
- [ ] `pre-commit run --all-files` passes
- [ ] `pytest tests/ -v` passes
- [ ] `./scripts/core/ci-check.sh` passes
- [ ] No stale path references remain (grep verified)
- [ ] `./scripts/core/check-sync.sh` runs without errors
```

## Gotchas

1. **`wait-for-bots.sh` calls `check-bots.sh` via `$SCRIPT_DIR`** — both move to `core/`, so `$SCRIPT_DIR` still resolves correctly. Verify it uses `$(dirname "${BASH_SOURCE[0]}")` or `$(dirname "$0")`.

2. **`ci-check.sh` calls `pattern_lint.py`** — currently as `python3 scripts/pattern_lint.py`. After restructure this becomes `python3 scripts/core/pattern_lint.py`. Check if ci-check.sh uses a relative path or `$SCRIPT_DIR` — update accordingly.

3. **`pyproject.toml` coverage omit** — currently excludes `scripts/sync_tasks_to_linear.py` and `scripts/validate_task_status.py`. Update paths.

4. **`pyproject.toml` is still `name = "your-project-name"`** — the template placeholder. Parameterization should handle this gracefully (fallback to generic name).

5. **bootstrap.sh copies scripts/** — it copies the entire `scripts/` directory to new projects (line ~85). After restructure, it copies the new layout. Verify it handles `core/` + `local/` + `optional/` correctly.

6. **`CROSS_REPO_TOKEN` secret** — the GitHub Action needs a PAT with repo scope on downstream repos. This must be created manually in ASK's repo settings. Document this in the PR.

7. **Agent definitions may reference `./scripts/ci-check.sh`** — the feature-developer-v3 agent definition is large and has multiple script references. Grep all `.claude/agents/*.md` files thoroughly.

#!/usr/bin/env bash
# Bootstrap a consumer project from the agentive starter kit.
#
# Consumer projects get implementation tools (agents, scripts, commands)
# but NOT the builder layer (.kit/ — planning, evaluation, coordination).
#
# Usage:
#   ~/Github/agentive-starter-kit/scripts/local/bootstrap-consumer.sh ~/Github/my-app
#
# Prerequisites:
#   - Target directory exists
#   - agentive-starter-kit is cloned at the path this script lives in

set -e

# ─────────────────────────────────────────
# Resolve paths
# ─────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

TARGET="${1:?Usage: $0 <target-directory>}"
if [ ! -d "$TARGET" ]; then
    echo "Error: Target directory does not exist: $TARGET"
    echo "   Create it first and put your project files in it."
    exit 1
fi
TARGET="$(cd "$TARGET" && pwd)"
PROJECT_NAME="$(basename "$TARGET")"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Bootstrapping consumer project: $PROJECT_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Source:  $PROJECT_ROOT"
echo "  Target:  $TARGET"
echo "  Type:    Consumer (no builder layer)"
echo

# ─────────────────────────────────────────
# Step 1: Copy implementation scaffolding
# ─────────────────────────────────────────
echo "1/3 Copying implementation scaffolding..."

RSYNC_BASE=(rsync -a --ignore-existing --exclude='.git/' --exclude='.venv/' --exclude='__pycache__/' --exclude='.DS_Store')

# .claude/ — implementation agents, commands, skills, settings
# Exclude builder agents (planner*, code-reviewer, document-reviewer, security-reviewer)
"${RSYNC_BASE[@]}" \
    --exclude='planner.md' --exclude='planner2.md' \
    --exclude='code-reviewer.md' --exclude='document-reviewer.md' --exclude='security-reviewer.md' \
    "$PROJECT_ROOT/.claude/" "$TARGET/.claude/"

# .serena/ — setup script and template
"${RSYNC_BASE[@]}" --exclude='cache/' --exclude='memories/' --exclude='claude-code/' \
    "$PROJECT_ROOT/.serena/" "$TARGET/.serena/"

# scripts/core/ — shared scripts
mkdir -p "$TARGET/scripts/core"
"${RSYNC_BASE[@]}" "$PROJECT_ROOT/scripts/core/" "$TARGET/scripts/core/"

# scripts/optional/ — opt-in scripts
mkdir -p "$TARGET/scripts/optional"
"${RSYNC_BASE[@]}" "$PROJECT_ROOT/scripts/optional/" "$TARGET/scripts/optional/"

# .github/ — CI workflows
"${RSYNC_BASE[@]}" \
    --exclude='sync-core-scripts.yml' --exclude='sync-to-linear.yml' \
    "$PROJECT_ROOT/.github/" "$TARGET/.github/"

# tests/ — test infrastructure
"${RSYNC_BASE[@]}" "$PROJECT_ROOT/tests/" "$TARGET/tests/"

# Top-level files (only if they don't exist in target)
for f in pyproject.toml .gitignore .pre-commit-config.yaml .env.template .coderabbitignore conftest.py; do
    if [ -f "$PROJECT_ROOT/$f" ] && [ ! -f "$TARGET/$f" ]; then
        cp "$PROJECT_ROOT/$f" "$TARGET/$f"
    fi
done

# Create a consumer-appropriate manifest (no kit_builder tier)
if [ ! -f "$TARGET/scripts/.core-manifest.json" ]; then
    cat > "$TARGET/scripts/.core-manifest.json" << 'MANIFEST'
{
  "core_version": "2.0.0",
  "source_repo": "movito/agentive-starter-kit",
  "synced_at": "2026-03-29T00:00:00Z",
  "files": {
    "scripts_core": [
      "core/__init__.py",
      "core/check-bots.sh",
      "core/check-sync.sh",
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
      "core/VERSION"
    ],
    "commands_core": [
      "check-ci.md",
      "check-bots.md",
      "wait-for-bots.md",
      "start-task.md",
      "commit-push-pr.md",
      "preflight.md"
    ],
    "commands_optional": [
      "babysit-pr.md",
      "retro.md",
      "triage-threads.md",
      "status.md",
      "check-spec.md"
    ]
  },
  "opted_in": ["commands_optional"]
}
MANIFEST
fi

echo "Done (no .kit/ builder layer — consumer project)"
echo

# ─────────────────────────────────────────
# Step 2: Initialize git (if needed)
# ─────────────────────────────────────────
echo "2/3 Checking git..."

cd "$TARGET"

if [ -d ".git" ]; then
    echo "Git repo already exists"
else
    git init -b main
    git add -A
    git commit -m "Initial commit: project scaffolding from agentive-starter-kit"
    echo "Git repo initialized (branch: main)"
fi
echo

# ─────────────────────────────────────────
# Step 3: Next steps
# ─────────────────────────────────────────
echo "3/3 Next steps"
echo
echo "Your consumer project is scaffolded. To complete setup:"
echo
echo "  cd $TARGET"
echo "  ./scripts/core/project setup        # Python venv + deps"
echo "  source .venv/bin/activate            # Activate venv"
echo "  cp .env.template .env               # Add your API keys"
echo
echo "Launch agents with:"
echo "  claude --agent .claude/agents/feature-developer.md"
echo
echo "To pull upstream updates later:"
echo "  git remote add upstream https://github.com/movito/agentive-starter-kit.git"
echo "  git fetch upstream"
echo "  git merge upstream/main"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

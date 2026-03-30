#!/usr/bin/env bash
# Bootstrap a new agentive project from existing design materials.
#
# Usage:
#   ~/Github/agentive-starter-kit/scripts/bootstrap.sh ~/Github/my-project
#
# Prerequisites:
#   - Target directory exists (with your design materials in it)
#   - agentive-starter-kit is cloned at the path this script lives in
#
# What this does:
#   1. Copies ASK scaffolding into your project (preserves your files)
#   2. Runs setup-dev.sh (Python, venv, dispatch-kit, deps, tmux, dispatch init)
#   3. Launches the bootstrap agent to read your materials and configure everything
#
# What it does NOT do:
#   - Create .env with API keys (you do this after)
#   - Create a GitHub repo (the bootstrap agent offers to do this)

set -e

# ─────────────────────────────────────────
# Resolve paths
# ─────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Resolve TARGET before cd — user may pass a relative path from their cwd
TARGET="${1:?Usage: $0 <target-directory>}"
if [ ! -d "$TARGET" ]; then
    echo "❌ Target directory does not exist: $TARGET"
    echo "   Create it first and put your design materials in it."
    exit 1
fi
TARGET="$(cd "$TARGET" && pwd)"
PROJECT_NAME="$(basename "$TARGET")"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Bootstrapping: $PROJECT_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Source:  $PROJECT_ROOT"
echo "  Target:  $TARGET"
echo

# ─────────────────────────────────────────
# Step 1: Copy scaffolding (preserve existing files)
# ─────────────────────────────────────────
echo "1/4 📂 Copying scaffolding..."

# Base rsync flags: archive mode, skip existing files, no .git/.venv
RSYNC_BASE=(rsync -a --ignore-existing --exclude='.git/' --exclude='.venv/' --exclude='__pycache__/' --exclude='.DS_Store')

# .claude/ — agent definitions, commands, skills, settings
"${RSYNC_BASE[@]}" "$PROJECT_ROOT/.claude/" "$TARGET/.claude/"

# .kit/ — builder layer (adversarial, context, delegation, agents, etc.)
"${RSYNC_BASE[@]}" \
    --exclude='adversarial/logs/' --exclude='adversarial/artifacts/' --exclude='adversarial/inputs/' --exclude='adversarial/evaluators/' \
    --exclude='context/ASK-*' --exclude='context/retros/' --exclude='context/reviews/' --exclude='context/research/' \
    --exclude='context/*SESSION-HANDOVER*' --exclude='context/*LINEAR-SYNC*' --exclude='context/*MIRIAD*' \
    --exclude='context/*code-review-lessons*' --exclude='context/*code-review-test*' \
    --exclude='tasks/ASK-*' \
    "$PROJECT_ROOT/.kit/" "$TARGET/.kit/"

# .serena/ — setup script and template
"${RSYNC_BASE[@]}" --exclude='cache/' --exclude='memories/' --exclude='claude-code/' \
    "$PROJECT_ROOT/.serena/" "$TARGET/.serena/"

# .github/ — CI workflows, dependabot
"${RSYNC_BASE[@]}" "$PROJECT_ROOT/.github/" "$TARGET/.github/"

# docs/ — only the structural parts (decisions, testing guide)
"${RSYNC_BASE[@]}" --exclude='proposals/' "$PROJECT_ROOT/docs/" "$TARGET/docs/"

# scripts/ — project management, CI, setup
"${RSYNC_BASE[@]}" "$PROJECT_ROOT/scripts/" "$TARGET/scripts/"

# tests/ — conftest and test infrastructure
"${RSYNC_BASE[@]}" "$PROJECT_ROOT/tests/" "$TARGET/tests/"

# Top-level files (only if they don't exist in target)
for f in CLAUDE.md pyproject.toml .gitignore .pre-commit-config.yaml .env.template .coderabbitignore conftest.py; do
    if [ -f "$PROJECT_ROOT/$f" ] && [ ! -f "$TARGET/$f" ]; then
        cp "$PROJECT_ROOT/$f" "$TARGET/$f"
    fi
done

echo "✅ Scaffolding copied (existing files preserved)"
echo

# ─────────────────────────────────────────
# Step 2: Initialize git (if needed)
# ─────────────────────────────────────────
echo "2/4 🔀 Checking git..."

cd "$TARGET"

if [ -d ".git" ]; then
    echo "✅ Git repo already exists"
else
    git init -b main
    git add -A
    git commit -m "Initial commit: design materials + agentive scaffolding"
    echo "✅ Git repo initialized with initial commit (branch: main)"
fi
echo

# ─────────────────────────────────────────
# Step 3: Run setup-dev.sh
# ─────────────────────────────────────────
echo "3/4 🔧 Running setup-dev.sh..."
echo

bash scripts/optional/setup-dev.sh

echo

# ─────────────────────────────────────────
# Step 4: Launch bootstrap agent
# ─────────────────────────────────────────
echo "4/4 🤖 Launching bootstrap agent..."
echo
echo "The agent will read your design materials and configure the project."
echo "When it's done, add your API keys to .env and start working with planner2."
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Build context for the agent
MATERIAL_FILES=$(find "$TARGET" -maxdepth 2 \
    -not -path '*/.claude/*' \
    -not -path '*/.kit/*' \
    -not -path '*/.serena/*' \
    -not -path '*/.github/*' \
    -not -path '*/.git/*' \
    -not -path '*/.venv/*' \
    -not -path '*/delegation/*' \
    -not -path '*/scripts/*' \
    -not -path '*/tests/*' \
    -not -path '*/docs/adr/*' \
    -not -path '*/docs/TESTING.md' \
    -not -name 'pyproject.toml' \
    -not -name 'CLAUDE.md' \
    -not -name '.gitignore' \
    -not -name '.pre-commit-config.yaml' \
    -not -name '.env.template' \
    -not -name '.coderabbitignore' \
    -not -name 'conftest.py' \
    -not -name '.DS_Store' \
    -type f 2>/dev/null | sort)

CONTEXT="BOOTSTRAP CONTEXT

Project folder: $TARGET
Project name (from folder): $PROJECT_NAME

Design materials found:
$MATERIAL_FILES

Read ALL of these files to understand the project.
Then follow your bootstrap procedure to configure everything."

exec claude --agent "$TARGET/.claude/agents/bootstrap.md" "$CONTEXT"

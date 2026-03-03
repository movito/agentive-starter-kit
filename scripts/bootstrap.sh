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
ASK_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET="${1:?Usage: $0 <target-directory>}"

# Resolve target to absolute path
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
echo "  Source:  $ASK_ROOT"
echo "  Target:  $TARGET"
echo

# ─────────────────────────────────────────
# Step 1: Copy scaffolding (preserve existing files)
# ─────────────────────────────────────────
echo "1/4 📂 Copying scaffolding..."

# Base rsync flags: archive mode, skip existing files, no .git/.venv
RSYNC_BASE=(rsync -a --ignore-existing --exclude='.git/' --exclude='.venv/' --exclude='__pycache__/' --exclude='.DS_Store')

# .claude/ — agent definitions, commands, skills, settings
"${RSYNC_BASE[@]}" "$ASK_ROOT/.claude/" "$TARGET/.claude/"

# .adversarial/ — evaluation config, docs, scripts, templates (not logs/artifacts/evaluators)
"${RSYNC_BASE[@]}" \
    --exclude='logs/' --exclude='artifacts/' --exclude='inputs/' --exclude='evaluators/' \
    "$ASK_ROOT/.adversarial/" "$TARGET/.adversarial/"

# .agent-context/ — workflows, templates, patterns (not old handoffs/retros/reviews)
"${RSYNC_BASE[@]}" \
    --exclude='ASK-*' --exclude='retros/' --exclude='reviews/' --exclude='research/' \
    --exclude='*SESSION-HANDOVER*' --exclude='*LINEAR-SYNC*' --exclude='*MIRIAD*' \
    --exclude='*code-review-lessons*' --exclude='*code-review-test*' \
    "$ASK_ROOT/.agent-context/" "$TARGET/.agent-context/"

# .serena/ — setup script and template
"${RSYNC_BASE[@]}" --exclude='cache/' --exclude='memories/' --exclude='claude-code/' \
    "$ASK_ROOT/.serena/" "$TARGET/.serena/"

# .github/ — CI workflows, dependabot
"${RSYNC_BASE[@]}" "$ASK_ROOT/.github/" "$TARGET/.github/"

# agents/ — launcher scripts
"${RSYNC_BASE[@]}" "$ASK_ROOT/agents/" "$TARGET/agents/"

# delegation/ — task folder structure and templates (not old task files)
"${RSYNC_BASE[@]}" --exclude='ASK-*' "$ASK_ROOT/delegation/" "$TARGET/delegation/"

# docs/ — only the structural parts (decisions, testing guide)
"${RSYNC_BASE[@]}" --exclude='proposals/' "$ASK_ROOT/docs/" "$TARGET/docs/"

# scripts/ — project management, CI, setup
"${RSYNC_BASE[@]}" "$ASK_ROOT/scripts/" "$TARGET/scripts/"

# tests/ — conftest and test infrastructure
"${RSYNC_BASE[@]}" "$ASK_ROOT/tests/" "$TARGET/tests/"

# Top-level files (only if they don't exist in target)
for f in CLAUDE.md pyproject.toml .gitignore .pre-commit-config.yaml .env.template .coderabbitignore conftest.py; do
    if [ -f "$ASK_ROOT/$f" ] && [ ! -f "$TARGET/$f" ]; then
        cp "$ASK_ROOT/$f" "$TARGET/$f"
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

bash scripts/setup-dev.sh

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
    -not -path '*/.adversarial/*' \
    -not -path '*/.agent-context/*' \
    -not -path '*/.serena/*' \
    -not -path '*/.github/*' \
    -not -path '*/.git/*' \
    -not -path '*/.venv/*' \
    -not -path '*/delegation/*' \
    -not -path '*/scripts/*' \
    -not -path '*/agents/*' \
    -not -path '*/tests/*' \
    -not -path '*/docs/decisions/*' \
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

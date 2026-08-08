#!/usr/bin/env bash
# engine-materials.sh — the adopt-with-design-materials ENGINE behind
# the setup door (KIT-0053, ADR-0027 P3). Formerly the bootstrap.sh
# entrance; that filename is now a shim onto scripts/local/bootstrap
# (--adopt --design-materials). Call the door, not this engine, unless
# you are the door.
#
# NOTE: this engine ends by exec-ing an interactive claude session
# (the bootstrap agent), so the door cannot append its doctor tail on
# this path — the door execs this engine as its final act.
#
# Usage (door-internal):
#   engine-materials.sh <target-directory> [--scaffold-only]
#
#   --scaffold-only stops after the copy step (no git init, no
#   setup-dev.sh, no agent launch) — the seam tests/test_engine_materials.py
#   uses to pin the copy boundary (KIT-0068 A12/A13).
#
# Prerequisites:
#   - Target directory exists (with your design materials in it)
#   - agentive-starter-kit is cloned at the path this script lives in
#
# What this does:
#   1. Copies ASK scaffolding into your project (preserves your files)
#   2. Runs setup-dev.sh (Python, venv, deps, tmux)
#   3. Launches the bootstrap agent to read your materials and configure everything
#
# What it does NOT do:
#   - Create .env with API keys (you do this after)
#   - Create a GitHub repo (the bootstrap agent offers to do this)

set -e

# Scrub GIT_* before any git call — a leaked GIT_DIR (pre-commit
# exports one inside worktrees) would redirect this engine's git
# init/add/commit at the REAL repository (the KIT-0048 incident class;
# the engine-consumer.sh pattern). The door scrubs too — this is
# defense in depth for direct engine invocation.
for _git_var in $(compgen -A variable | grep '^GIT_' || true); do
    unset "$_git_var"
done

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
SCAFFOLD_ONLY=0
if [ "${2:-}" = "--scaffold-only" ]; then
    SCAFFOLD_ONLY=1
fi

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

# .kit/ — builder layer (templates, workflows, docs). The
# kit's own planning corpus stays home: task-ID excludes are
# prefix-AGNOSTIC ([A-Z]*-NNNN — the ASK-* literals missed every KIT-*
# file after the prefix rename, KIT-0068 A13), and .kit/adversarial/ is
# operator-owned untracked state, excluded wholesale.
# NOTE: the task-ID pattern is anchored at context/ depth 1, so
# context/archive/ (finished-task handoffs, KIT-0077) needs its own
# wholesale exclude — same shape as retros/reviews/research.
"${RSYNC_BASE[@]}" \
    --exclude='adversarial/' \
    --exclude='context/[A-Z]*-[0-9][0-9][0-9][0-9]*' \
    --exclude='context/archive/' \
    --exclude='context/retros/' --exclude='context/reviews/' --exclude='context/research/' \
    --exclude='context/*SESSION-HANDOVER*' --exclude='context/*LINEAR-SYNC*' --exclude='context/*MIRIAD*' \
    --exclude='context/*code-review-lessons*' --exclude='context/*code-review-test*' \
    --exclude='tasks/*/[A-Z]*-[0-9][0-9][0-9][0-9]*' \
    --exclude='tasks/[A-Z]*-[0-9][0-9][0-9][0-9]*' \
    "$PROJECT_ROOT/.kit/" "$TARGET/.kit/"

# .serena/ — setup script and template
"${RSYNC_BASE[@]}" --exclude='cache/' --exclude='memories/' --exclude='claude-code/' \
    "$PROJECT_ROOT/.serena/" "$TARGET/.serena/"

# .github/ — CI workflows, dependabot
"${RSYNC_BASE[@]}" "$PROJECT_ROOT/.github/" "$TARGET/.github/"

# docs/ — everything ships (docs/adr/ included); no exclusions needed:
# proposals/ and the old TESTING.md no longer exist (ASK-0044/ASK-0047)
"${RSYNC_BASE[@]}" "$PROJECT_ROOT/docs/" "$TARGET/docs/"

# scripts/ — project management, CI, setup. scripts/local/ is the
# kit-side layer (door + engines) and "never ships on any sync tier or
# consumer rsync" (the door's own contract, bootstrap:8-9) — the
# wholesale copy here violated it (KIT-0068 A12).
"${RSYNC_BASE[@]}" --exclude='local/' "$PROJECT_ROOT/scripts/" "$TARGET/scripts/"

# tests/ — conftest and test infrastructure, minus the kit-only tests
# that import or read scripts/local/ (they would fail consumer pytest
# at collection time). Keep this list in sync with engine-consumer.sh's
# tests/ excludes.
"${RSYNC_BASE[@]}" \
    --exclude='test_kit_markers.py' \
    --exclude='test_bootstrap_consumer.py' \
    --exclude='test_bootstrap_shapes.py' \
    --exclude='test_bots_conformance.py' \
    --exclude='test_check_hook_seeds.py' \
    --exclude='test_entrance_shims.py' \
    --exclude='test_new_worktree.py' \
    --exclude='test_scaffold_acceptance.py' \
    --exclude='test_setup_door.py' \
    --exclude='test_engine_materials.py' \
    "$PROJECT_ROOT/tests/" "$TARGET/tests/"

# Top-level files (only if they don't exist in target)
for f in CLAUDE.md pyproject.toml .gitignore .pre-commit-config.yaml .env.template .coderabbitignore conftest.py; do
    if [ -f "$PROJECT_ROOT/$f" ] && [ ! -f "$TARGET/$f" ]; then
        cp "$PROJECT_ROOT/$f" "$TARGET/$f"
    fi
done

echo "✅ Scaffolding copied (existing files preserved)"
# Name the drops (patterns.yml intersection_names_drops): an exclusion
# list that doesn't say what it drops reads as "copied everything".
echo "   Not copied (kit-side only): scripts/local/ (door + engines),"
echo "   kit task specs and task-ID context files (.kit/tasks/, .kit/context/),"
echo "   .kit/context/archive/ (finished-task handoffs),"
echo "   .kit/adversarial/ (operator-owned), retros/reviews/research,"
echo "   and kit-only tests (test_setup_door.py, test_kit_markers.py, ...)"
echo

if [ "$SCAFFOLD_ONLY" = "1" ]; then
    echo "── --scaffold-only: stopping before git/setup/agent steps ──"
    exit 0
fi

# ─────────────────────────────────────────
# Step 2: Initialize git (if needed)
# ─────────────────────────────────────────
echo "2/4 🔀 Checking git..."

cd "$TARGET"

# -e, not -d: in a worktree or submodule .git is a FILE — treating it
# as "no repo" would git-init/commit inside an existing checkout (the
# KIT-0048 incident's second ingredient; engine-consumer.sh pattern)
if [ -e ".git" ]; then
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
echo "When it's done, add your API keys to .env and start working with planner."
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
    -not -path '*/scripts/*' \
    -not -path '*/tests/*' \
    -not -path '*/docs/adr/*' \
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

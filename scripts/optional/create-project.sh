#!/usr/bin/env bash
# create-project.sh — Export a clean copy of agentive-starter-kit for a new project
#
# Usage: ./scripts/optional/create-project.sh <target-dir> [--name NAME] [--prefix PREFIX]
#
# This script:
#   1. Exports the current repo WITHOUT git history (git archive)
#   2. Strips all project-specific content (tasks, ADRs, context, tests, etc.)
#   3. Resets version to 0.1.0
#   4. Initializes a fresh git repo
#
# After running this, use the bootstrap agent or manually customize CLAUDE.md,
# pyproject.toml, and README.md for your project.

set -euo pipefail

# --- Resolve repo root ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# --- Parse arguments ---
TARGET_DIR=""
PROJECT_NAME=""
TASK_PREFIX=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --name)    PROJECT_NAME="$2"; shift 2 ;;
        --prefix)  TASK_PREFIX="$2"; shift 2 ;;
        --help|-h)
            echo "Usage: $0 <target-dir> [--name NAME] [--prefix PREFIX]"
            echo ""
            echo "  <target-dir>     Where to create the new project (must not exist)"
            echo "  --name NAME      Project name (default: directory basename)"
            echo "  --prefix PREFIX  Task ID prefix, e.g. ID2 (default: derived from name)"
            echo ""
            echo "Example:"
            echo "  $0 ~/Github/my-new-project --name 'My New Project' --prefix MNP"
            exit 0
            ;;
        *)
            if [[ -z "$TARGET_DIR" ]]; then
                TARGET_DIR="$1"
            else
                echo "Error: unexpected argument '$1'" >&2
                exit 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$TARGET_DIR" ]]; then
    echo "Error: target directory is required" >&2
    echo "Usage: $0 <target-dir> [--name NAME] [--prefix PREFIX]" >&2
    exit 1
fi

# Expand ~ and resolve path
TARGET_DIR="${TARGET_DIR/#\~/$HOME}"

if [[ -e "$TARGET_DIR" ]]; then
    echo "Error: '$TARGET_DIR' already exists" >&2
    exit 1
fi

# Defaults
DIR_BASENAME="$(basename "$TARGET_DIR")"
PROJECT_NAME="${PROJECT_NAME:-$DIR_BASENAME}"
if [[ -z "$TASK_PREFIX" ]]; then
    # Derive prefix: uppercase first letters of each word, max 4 chars
    TASK_PREFIX=$(echo "$PROJECT_NAME" | tr '[:lower:]' '[:upper:]' | sed 's/[^A-Z0-9 ]//g' | awk '{for(i=1;i<=NF;i++) printf substr($i,1,1)}')
    # Fallback if too short
    if [[ ${#TASK_PREFIX} -lt 2 ]]; then
        TASK_PREFIX=$(echo "$DIR_BASENAME" | tr '[:lower:]' '[:upper:]' | tr -d '-_ ' | cut -c1-4)
    fi
fi

echo "=== Create Project from Agentive Starter Kit ==="
echo ""
echo "  Source:    $REPO_ROOT"
echo "  Target:    $TARGET_DIR"
echo "  Name:      $PROJECT_NAME"
echo "  Prefix:    $TASK_PREFIX"
echo ""

# --- Step 1: Export without git history ---
echo "📦 Step 1/5: Exporting repository (no git history)..."
mkdir -p "$TARGET_DIR"
cd "$REPO_ROOT"
git archive HEAD | tar -x -C "$TARGET_DIR"
echo "   Done — $(find "$TARGET_DIR" -type f | wc -l | tr -d ' ') files exported"

# --- Step 2: Remove project-specific content ---
echo "🧹 Step 2/5: Removing project-specific content..."

cd "$TARGET_DIR"

# Tasks — remove all specs, keep folder structure and template
find .kit/tasks/ -name "*.md" ! -name "README.md" ! -path "*/9-reference/*" -delete 2>/dev/null || true

# Context — remove handoffs, reviews, retros, research, starters
find .kit/context/ -maxdepth 1 -name "*.md" ! -name "README.md" ! -name "patterns.yml" -delete 2>/dev/null || true
find .kit/context/ -maxdepth 1 -name "*.json" ! -name "agent-handoffs.json" ! -name "current-state.json" -delete 2>/dev/null || true
rm -rf .kit/context/research/ 2>/dev/null || true
find .kit/context/retros/ -name "*.md" -delete 2>/dev/null || true
find .kit/context/reviews/ -name "*.md" -delete 2>/dev/null || true
# Keep workflows/ and templates/ intact

# Kit ADRs — remove all (keep folder)
find .kit/adr/ -name "KIT-ADR-*.md" -delete 2>/dev/null || true

# Project ADRs — remove project-specific, keep templates
find docs/adr/ -name "ADR-*.md" -o -name "ASK-*.md" | xargs rm -f 2>/dev/null || true

# Adversarial inputs and logs
rm -rf .adversarial/inputs/*.md 2>/dev/null || true
rm -rf .adversarial/logs/ 2>/dev/null || true
mkdir -p .adversarial/logs

# Tests — reset to empty
rm -rf tests/
mkdir -p tests
touch tests/__init__.py

# Local scripts — clear project-specific
rm -rf scripts/local/*
mkdir -p scripts/local

# Project memory from wrong project
rm -rf .claude/projects/ 2>/dev/null || true

DELETED_COUNT=$(git diff --stat 2>/dev/null | tail -1 || echo "many files")
echo "   Done — project-specific content removed"

# --- Step 3: Reset identity files ---
echo "🏷️  Step 3/5: Setting project identity..."

# Reset agent-handoffs.json
cat > .kit/context/agent-handoffs.json << 'HANDOFF_EOF'
{
  "planner": {
    "status": "idle",
    "current_task": null,
    "task_started": null,
    "brief_note": "Project bootstrapped. Ready for first task.",
    "details_link": null,
    "handoff_file": null
  },
  "feature-developer": {
    "status": "idle",
    "current_task": null,
    "task_started": null,
    "brief_note": "Ready for assignment",
    "details_link": null
  },
  "code-reviewer": {
    "status": "idle",
    "current_task": null,
    "task_started": null,
    "brief_note": "Ready for review tasks",
    "details_link": null
  }
}
HANDOFF_EOF

# Reset current-state.json
cat > .kit/context/current-state.json << STATE_EOF
{
  "project": {
    "name": "$PROJECT_NAME",
    "task_prefix": "$TASK_PREFIX",
    "version": "0.1.0"
  },
  "phase": "bootstrap",
  "onboarding": {
    "completed": false
  }
}
STATE_EOF

# Reset REVIEW-INSIGHTS.md
cat > .kit/context/REVIEW-INSIGHTS.md << 'INSIGHTS_EOF'
# Review Insights

Extracted knowledge from code reviews.
INSIGHTS_EOF

# Reset CHANGELOG.md
cat > CHANGELOG.md << CHANGELOG_EOF
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Project bootstrapped from agentive-starter-kit
CHANGELOG_EOF

# Update pyproject.toml — reset version and clear placeholders
sed -i '' "s/^version = .*/version = \"0.1.0\"/" pyproject.toml 2>/dev/null || \
sed -i "s/^version = .*/version = \"0.1.0\"/" pyproject.toml

echo "   Done — identity files reset"

# --- Step 4: Initialize fresh git repo ---
echo "🔧 Step 4/5: Initializing fresh git repository..."
git init -b main
git add -A
git commit -m "Initial commit: Bootstrap from agentive-starter-kit

Project: $PROJECT_NAME
Task prefix: $TASK_PREFIX" --quiet

COMMIT_SHA=$(git rev-parse --short HEAD)
echo "   Done — initial commit $COMMIT_SHA"

# --- Step 5: Summary ---
echo ""
echo "=== Project Created Successfully ==="
echo ""
echo "  📂 Location:    $TARGET_DIR"
echo "  📋 Task prefix: $TASK_PREFIX"
echo "  🔖 Version:     0.1.0"
echo "  📦 Git:         initialized (1 commit, no remote)"
echo ""
echo "Next steps:"
echo "  1. cd $TARGET_DIR"
echo "  2. Customize CLAUDE.md and README.md for your project"
echo "  3. Add .env file with API keys (copy from .env.template)"
echo "  4. Install evaluators: ./scripts/core/project install-evaluators"
echo "  5. Create GitHub repo: gh repo create $DIR_BASENAME --private --source=. --push"
echo "  6. Start planning: claude --agent .claude/agents/planner2.md"
echo ""

#!/usr/bin/env bash
# Bootstrap a consumer project from the agentive starter kit.
#
# Consumer projects get implementation tools (agents, scripts, commands)
# plus a minimal .kit/ workflow skeleton (task folders, context, task-starter
# template) that the shipped V2 planner + feature-developer agents need.
# They do NOT get the full builder layer (evaluators, ADRs, kit planning docs).
#
# Usage:
#   ~/Github/agentive-starter-kit/scripts/local/bootstrap-consumer.sh ~/Github/my-app
#   ~/Github/agentive-starter-kit/scripts/local/bootstrap-consumer.sh --no-kit ~/Github/my-app
#
# Flags:
#   --no-kit   Opt out of the kit workflow entirely: no .kit/ scaffold and
#              no planner.md / feature-developer.md shipped. Useful for a
#              consumer that only wants the lighter implementation tooling.
#
# Prerequisites:
#   - Target directory exists
#   - agentive-starter-kit is cloned at the path this script lives in

set -e

# ─────────────────────────────────────────
# Resolve paths + parse args
# ─────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
KIT_MARKERS="$PROJECT_ROOT/scripts/local/kit_markers.py"

KIT_ENABLED=1
TARGET=""
for arg in "$@"; do
    case "$arg" in
        --no-kit)
            KIT_ENABLED=0
            ;;
        --*)
            echo "Error: unknown flag: $arg"
            echo "Usage: $0 [--no-kit] <target-directory>"
            exit 1
            ;;
        *)
            TARGET="$arg"
            ;;
    esac
done

if [ -z "$TARGET" ]; then
    echo "Usage: $0 [--no-kit] <target-directory>"
    exit 1
fi
if [ ! -d "$TARGET" ]; then
    echo "Error: Target directory does not exist: $TARGET"
    echo "   Create it first and put your project files in it."
    exit 1
fi
TARGET="$(cd "$TARGET" && pwd)"
if [ "$TARGET" = "$PROJECT_ROOT" ]; then
    echo "Error: target is the kit source repo ($PROJECT_ROOT)."
    echo "   bootstrap-consumer.sh provisions a *consumer* checkout; running it"
    echo "   against the kit itself would rsync/sweep its own files. Aborting."
    exit 1
fi
PROJECT_NAME="$(basename "$TARGET")"

if [ "$KIT_ENABLED" -eq 1 ]; then
    KIT_LABEL="Consumer + .kit/ workflow skeleton"
else
    KIT_LABEL="Consumer (--no-kit: no workflow skeleton, no planner/feature-developer)"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Bootstrapping consumer project: $PROJECT_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Source:  $PROJECT_ROOT"
echo "  Target:  $TARGET"
echo "  Type:    $KIT_LABEL"
echo

# ─────────────────────────────────────────
# Step 1: Copy implementation scaffolding
# ─────────────────────────────────────────
echo "1/4 Copying implementation scaffolding..."

RSYNC_BASE=(rsync -a --ignore-existing --exclude='.git/' --exclude='.venv/' --exclude='__pycache__/' --exclude='.DS_Store')

# .claude/ — implementation agents, commands, skills, settings.
# Reviewer agents stay builder-only. The two consumer-customizable V2
# agents (planner.md, feature-developer.md) are excluded here and handled
# by the marker-merge step below — rsync's --ignore-existing can neither
# fill their KIT-LOCAL regions for a fresh consumer nor refresh structure
# for an existing one. With --no-kit they are dropped entirely.
AGENT_EXCLUDES=(--exclude='code-reviewer.md' --exclude='document-reviewer.md' --exclude='security-reviewer.md' \
                --exclude='planner.md' --exclude='feature-developer.md')

# Sweep retired agent variants from a prior bootstrap before rsync; --ignore-existing
# would otherwise leave legacy planner2/3 + feature-developer-v3/v6/v7 alongside the
# canonical V2 agents in an existing checkout.
rm -f "$TARGET/.claude/agents/planner2.md" \
      "$TARGET/.claude/agents/planner3.md" \
      "$TARGET/.claude/agents/feature-developer-v3.md" \
      "$TARGET/.claude/agents/feature-developer-v6.md" \
      "$TARGET/.claude/agents/feature-developer-v7.md"
"${RSYNC_BASE[@]}" "${AGENT_EXCLUDES[@]}" \
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

# tests/ — test infrastructure. Exclude test_kit_markers.py: it imports
# scripts/local/kit_markers.py, an ASK-only bootstrap tool that is never
# synced to consumers, so shipping the test would break consumer pytest
# (and the pytest-fast pre-commit hook) at collection time.
"${RSYNC_BASE[@]}" --exclude='test_kit_markers.py' \
    "$PROJECT_ROOT/tests/" "$TARGET/tests/"

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

echo "Done"
echo

# ─────────────────────────────────────────
# Step 2: Kit workflow agents + skeleton
# ─────────────────────────────────────────
echo "2/4 Provisioning kit workflow..."

if [ "$KIT_ENABLED" -eq 1 ]; then
    mkdir -p "$TARGET/.claude/agents"

    # Marker-merge the two consumer-customizable V2 agents. A fresh
    # consumer gets KIT-LOCAL regions filled with project placeholders;
    # an existing consumer keeps its filled-in regions while picking up
    # upstream structure outside the markers. --project-name is always
    # passed so that an existing-but-markerless agent (a consumer stuck on
    # a pre-consolidation copy) gets clean placeholders rather than the
    # kit's own Project Context / Stack Notes content.
    for agent in planner.md feature-developer.md; do
        up="$PROJECT_ROOT/.claude/agents/$agent"
        dst="$TARGET/.claude/agents/$agent"
        tmp="$dst.kit-merge.tmp"
        merge_args=(merge --upstream "$up" --project-name "$PROJECT_NAME" --out "$tmp")
        if [ -f "$dst" ]; then
            merge_args+=(--consumer "$dst")
            python3 "$KIT_MARKERS" "${merge_args[@]}"
            echo "  refreshed $agent (preserved filled KIT-LOCAL regions)"
        else
            python3 "$KIT_MARKERS" "${merge_args[@]}"
            echo "  installed $agent (KIT-LOCAL regions seeded with placeholders)"
        fi
        mv "$tmp" "$dst"
    done

    # .kit/ skeleton — task status folders, coordination dir, task-starter
    # template. The project script hardcodes .kit/tasks/<status>/, so these
    # directories must exist for the lifecycle commands to work.
    for d in 1-backlog 2-todo 3-in-progress 4-in-review 5-done 6-canceled 7-blocked; do
        mkdir -p "$TARGET/.kit/tasks/$d"
        [ -e "$TARGET/.kit/tasks/$d/.gitkeep" ] || touch "$TARGET/.kit/tasks/$d/.gitkeep"
    done
    mkdir -p "$TARGET/.kit/context"
    [ -e "$TARGET/.kit/context/.gitkeep" ] || touch "$TARGET/.kit/context/.gitkeep"
    mkdir -p "$TARGET/.kit/templates"
    if [ ! -f "$TARGET/.kit/templates/TASK-STARTER-TEMPLATE.md" ]; then
        cp "$PROJECT_ROOT/.kit/templates/TASK-STARTER-TEMPLATE.md" \
           "$TARGET/.kit/templates/TASK-STARTER-TEMPLATE.md"
    fi

    echo "  .kit/ skeleton ready (tasks/, context/, templates/)"
else
    echo "  Skipped (--no-kit): no .kit/ scaffold, no planner.md / feature-developer.md"
fi
echo

# ─────────────────────────────────────────
# Step 3: Initialize git (if needed)
# ─────────────────────────────────────────
echo "3/4 Checking git..."

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
# Step 4: Next steps
# ─────────────────────────────────────────
echo "4/4 Next steps"
echo
echo "Your consumer project is scaffolded. To complete setup:"
echo
echo "  cd $TARGET"
echo "  ./scripts/core/project setup        # Python venv + deps"
echo "  source .venv/bin/activate            # Activate venv"
echo "  cp .env.template .env               # Add your API keys"
echo
if [ "$KIT_ENABLED" -eq 1 ]; then
    echo "Fill in the KIT-LOCAL regions (Project Context / Stack Notes) in:"
    echo "  .claude/agents/feature-developer.md"
    echo "  .claude/agents/planner.md"
    echo
    echo "Launch agents with:"
    echo "  claude --agent .claude/agents/feature-developer.md"
else
    echo "Launch an agent with, e.g.:"
    echo "  claude --agent .claude/agents/ci-checker.md"
fi
echo
echo "To pull upstream updates later:"
echo "  git remote add upstream https://github.com/movito/agentive-starter-kit.git"
echo "  git fetch upstream"
echo "  git merge upstream/main"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

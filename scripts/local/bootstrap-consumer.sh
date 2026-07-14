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
#   ~/Github/agentive-starter-kit/scripts/local/bootstrap-consumer.sh \
#       --shape planning --target-path ../my-product --target-github acme/my-product \
#       ~/Github/my-product-planning
#
# Flags:
#   --no-kit   Opt out of the kit workflow entirely: no .kit/ scaffold and
#              no planner.md / feature-developer.md shipped. Useful for a
#              consumer that only wants the lighter implementation tooling.
#              (single shape only — a planning install IS the kit workflow.)
#   --shape <single|planning>
#              single   (default) — exactly today's behavior: full
#                       implementation scaffold incl. Python toolchain.
#              planning — coordination machinery only (KIT-0048, ADR-0027
#                       P2): .kit/, agents, commands, lifecycle + gates +
#                       doctor. NO pyproject/tests/venv/Python gauntlet.
#                       The target product repo receives nothing, ever.
#   --target-path <p>, --target-github <owner/name>
#              (planning shape) recorded in the CLAUDE.md kit-install
#              region and seeded into ## Target Repository. Placeholders
#              are written when omitted.
#
# Prerequisites:
#   - Target directory exists
#   - agentive-starter-kit is cloned at the path this script lives in

set -e

# This script runs git init/add/commit against $TARGET by design. A
# leaked GIT_DIR (pre-commit exports an absolute one inside worktrees)
# would silently redirect every one of those calls at the REAL
# repository — during KIT-0048 exactly that committed a scaffold tree
# onto a live feature branch and flipped the primary clone's core.bare.
# Scrub ALL GIT_* before any git call (the doctor 70-core-bare pattern).
for _git_var in $(compgen -A variable | grep '^GIT_' || true); do
    unset "$_git_var"
done

# ─────────────────────────────────────────
# Resolve paths + parse args
# ─────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
KIT_MARKERS="$PROJECT_ROOT/scripts/local/kit_markers.py"

KIT_ENABLED=1
TARGET=""
SHAPE="single"
TARGET_PATH=""
TARGET_GITHUB=""
USAGE="Usage: $0 [--no-kit] [--shape single|planning] [--target-path <p>] [--target-github <o/r>] <target-directory>"
while [ $# -gt 0 ]; do
    case "$1" in
        --no-kit)
            KIT_ENABLED=0
            ;;
        --shape)
            shift
            SHAPE="${1:-}"
            ;;
        --shape=*)
            SHAPE="${1#--shape=}"
            ;;
        --target-path)
            shift
            TARGET_PATH="${1:-}"
            ;;
        --target-path=*)
            TARGET_PATH="${1#--target-path=}"
            ;;
        --target-github)
            shift
            TARGET_GITHUB="${1:-}"
            ;;
        --target-github=*)
            TARGET_GITHUB="${1#--target-github=}"
            ;;
        --*)
            echo "Error: unknown flag: $1"
            echo "$USAGE"
            exit 1
            ;;
        *)
            if [ -n "$TARGET" ]; then
                echo "Error: multiple target directories given ('$TARGET' and '$1')"
                echo "$USAGE"
                exit 1
            fi
            TARGET="$1"
            ;;
    esac
    shift
done

case "$SHAPE" in
    single|planning) ;;
    *)
        echo "Error: unknown shape: '$SHAPE' (expected: single | planning)"
        echo "$USAGE"
        exit 1
        ;;
esac
if [ "$SHAPE" = "planning" ] && [ "$KIT_ENABLED" -eq 0 ]; then
    echo "Error: --no-kit contradicts --shape planning (the planning shape IS the kit workflow)"
    exit 1
fi

if [ -z "$TARGET" ]; then
    echo "$USAGE"
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

if [ "$SHAPE" = "planning" ]; then
    KIT_LABEL="Planning repo (coordination machinery, no Python toolchain)"
elif [ "$KIT_ENABLED" -eq 1 ]; then
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
# Step 1: Copy scaffolding (per shape)
# ─────────────────────────────────────────
RSYNC_BASE=(rsync -a --ignore-existing --exclude='.git/' --exclude='.venv/' --exclude='__pycache__/' --exclude='.DS_Store')

# The planning-shape ship list (KIT-0048 F1) — enumerated, never a glob
# (the KIT-0044 provisioning lesson). Two shapes only; if a third shape
# appears, a declarative set belongs to P3's door, not here.
# doctor.d/ ships WHOLE as a unit: shape applicability is decided at
# runtime by each check's `# shapes:` declaration, so single-only checks
# in a planning repo SKIP rather than being absent.
PLANNING_CORE=(
    __init__.py
    check-bots.sh
    check_cross_repo_config.py
    gh-review-helper.sh
    lib/target_repo.sh
    logging_config.py
    preflight-check.sh
    prepare-review-input.sh
    project
    sync_from_manifest.py
    validate_task_status.py
    verify-ci.sh
    wait-for-bots.sh
    VERSION
)
PLANNING_LOCAL=(
    kit_markers.py
    new-worktree.sh
)
# Deliberately NOT shipped to planning repos (the never-ship contract,
# tested in both directions): pyproject.toml, conftest.py, tests/,
# ci-check.sh (the Python gauntlet), pattern_lint.py, verify-setup.sh
# (shim over doctor), scripts/optional/, .github/ (Python CI),
# .serena/, the full .pre-commit-config.yaml.

# .claude/ — implementation agents, commands, skills, settings — ships to
# every shape. Reviewer agents stay builder-only. The consumer-customizable
# marker-bearing agents (planner.md, planner-f5.md, feature-developer.md,
# feature-developer-f5.md) are excluded here and handled by the marker-merge
# step below — rsync's --ignore-existing can neither fill their KIT-LOCAL
# regions for a fresh consumer (it would leak the kit's own Project Context /
# Stack Notes) nor refresh structure for an existing one. With --no-kit they
# are dropped entirely. Keep this list in sync with KIT_AGENTS below.
AGENT_EXCLUDES=(--exclude='code-reviewer.md' --exclude='document-reviewer.md' --exclude='security-reviewer.md' \
                --exclude='planner.md' --exclude='planner-f5.md' \
                --exclude='feature-developer.md' --exclude='feature-developer-f5.md')

if [ "$SHAPE" = "planning" ]; then
    echo "1/4 Copying planning-shape scaffolding..."

    # .claude/ — agents (marker-merged below), commands, skills, settings
    rm -f "$TARGET/.claude/agents/planner2.md" \
          "$TARGET/.claude/agents/planner3.md" \
          "$TARGET/.claude/agents/feature-developer-v3.md" \
          "$TARGET/.claude/agents/feature-developer-v6.md" \
          "$TARGET/.claude/agents/feature-developer-v7.md"
    "${RSYNC_BASE[@]}" "${AGENT_EXCLUDES[@]}" \
        "$PROJECT_ROOT/.claude/" "$TARGET/.claude/"

    # lifecycle + gate machinery (enumerated)
    for rel in "${PLANNING_CORE[@]}"; do
        mkdir -p "$TARGET/scripts/core/$(dirname "$rel")"
        if [ ! -e "$TARGET/scripts/core/$rel" ]; then
            cp "$PROJECT_ROOT/scripts/core/$rel" "$TARGET/scripts/core/$rel"
        fi
    done
    mkdir -p "$TARGET/scripts/core/doctor.d"
    "${RSYNC_BASE[@]}" "$PROJECT_ROOT/scripts/core/doctor.d/" "$TARGET/scripts/core/doctor.d/"
    for rel in "${PLANNING_LOCAL[@]}"; do
        mkdir -p "$TARGET/scripts/local"
        if [ ! -e "$TARGET/scripts/local/$rel" ]; then
            cp "$PROJECT_ROOT/scripts/local/$rel" "$TARGET/scripts/local/$rel"
        fi
    done

    # .adversarial/ — config + scripts + docs; evaluators are offered
    # (install-evaluators), never bundled; inputs/logs stay local
    "${RSYNC_BASE[@]}" --exclude='evaluators/' --exclude='logs/' --exclude='inputs/' \
        "$PROJECT_ROOT/.adversarial/" "$TARGET/.adversarial/"
    mkdir -p "$TARGET/.adversarial/inputs"
    [ -e "$TARGET/.adversarial/inputs/.gitkeep" ] || touch "$TARGET/.adversarial/inputs/.gitkeep"

    # top-level files (no pyproject/conftest; pre-commit gets the
    # planning variant below)
    for f in .gitignore .env.template .coderabbitignore; do
        if [ -f "$PROJECT_ROOT/$f" ] && [ ! -f "$TARGET/$f" ]; then
            cp "$PROJECT_ROOT/$f" "$TARGET/$f"
        fi
    done

    # planning pre-commit variant (F4): task hygiene, zero Python hooks.
    # language: system — runs on system python3, no hook-venv building.
    if [ ! -f "$TARGET/.pre-commit-config.yaml" ]; then
        cat > "$TARGET/.pre-commit-config.yaml" << 'PRECOMMIT'
# Planning-shape pre-commit (KIT-0048): task hygiene only.
# No Python toolchain hooks — this repo coordinates; it does not build.
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml

  - repo: local
    hooks:
      - id: validate-task-status
        name: Validate task status matches folder
        entry: python3 scripts/core/validate_task_status.py
        language: system
        files: ^\.kit/tasks/.*\.md$
        pass_filenames: true
        stages: [pre-commit]
PRECOMMIT
    fi

    # planning-shape manifest: exactly the shipped core set, so
    # `project sync` keeps working for future updates
    if [ ! -f "$TARGET/scripts/.core-manifest.json" ]; then
        mkdir -p "$TARGET/scripts"
        cat > "$TARGET/scripts/.core-manifest.json" << 'MANIFEST'
{
  "core_version": "3.2.0",
  "source_repo": "movito/agentive-starter-kit",
  "synced_at": "2026-07-14T00:00:00Z",
  "files": {
    "scripts_core": [
      "core/__init__.py",
      "core/check-bots.sh",
      "core/check_cross_repo_config.py",
      "core/doctor.d/10-gh-auth.sh",
      "core/doctor.d/20-env-keys.py",
      "core/doctor.d/30-evaluators.sh",
      "core/doctor.d/40-version-skew.py",
      "core/doctor.d/50-plugin-source.sh",
      "core/doctor.d/60-push-sync-token.sh",
      "core/doctor.d/70-core-bare.sh",
      "core/doctor.d/80-bot-presence.sh",
      "core/gh-review-helper.sh",
      "core/lib/target_repo.sh",
      "core/logging_config.py",
      "core/preflight-check.sh",
      "core/prepare-review-input.sh",
      "core/project",
      "core/sync_from_manifest.py",
      "core/validate_task_status.py",
      "core/verify-ci.sh",
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
else
echo "1/4 Copying implementation scaffolding..."

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

# tests/ — test infrastructure. Exclude tests that import or read
# scripts/local/ content (kit_markers.py, bootstrap-consumer.sh):
# scripts/local is an ASK-only layer that is never synced to consumers,
# so shipping these tests would break consumer pytest (and the
# pytest-fast pre-commit hook) at collection time. The rm -f sweep
# removes stale copies from a pre-fix bootstrap — --ignore-existing
# would otherwise leave the orphaned tests behind in existing consumers.
rm -f "$TARGET/tests/test_kit_markers.py" \
      "$TARGET/tests/test_bootstrap_consumer.py" \
      "$TARGET/tests/test_bootstrap_shapes.py"
"${RSYNC_BASE[@]}" --exclude='test_kit_markers.py' \
    --exclude='test_bootstrap_consumer.py' \
    --exclude='test_bootstrap_shapes.py' \
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
      "core/ci-check.sh",
      "core/gh-review-helper.sh",
      "core/logging_config.py",
      "core/pattern_lint.py",
      "core/preflight-check.sh",
      "core/project",
      "core/sync_from_manifest.py",
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
fi

# ─────────────────────────────────────────
# Step 2: Kit workflow agents + skeleton
# ─────────────────────────────────────────
echo "2/4 Provisioning kit workflow..."

# The consumer-customizable marker-bearing agents, single-sourced so the
# kit-enabled path marker-merges them and the --no-kit path prunes them.
# Keep in sync with AGENT_EXCLUDES above.
KIT_AGENTS=(planner.md planner-f5.md feature-developer.md feature-developer-f5.md)

if [ "$KIT_ENABLED" -eq 1 ]; then
    mkdir -p "$TARGET/.claude/agents"

    # Marker-merge the consumer-customizable marker-bearing agents. A fresh
    # consumer gets KIT-LOCAL regions filled with project placeholders;
    # an existing consumer keeps its filled-in regions while picking up
    # upstream structure outside the markers. --project-name is always
    # passed so that an existing-but-markerless agent (a consumer stuck on
    # a pre-consolidation copy) gets clean placeholders rather than the
    # kit's own Project Context / Stack Notes content.
    #
    # Two-pass for atomicity: merge ALL agents to temp files first, so a
    # failure on any one (e.g. malformed consumer markers → ValueError
    # under `set -e`) aborts before any destination is overwritten — never
    # leaving a consumer with some agents updated and others stale. Only
    # once every merge succeeds are the temp files moved into place.
    # (KIT_AGENTS is defined above so the --no-kit branch can prune the same
    # set; every entry must also be rsync-excluded in AGENT_EXCLUDES.)
    # Clear any stale temp file left by a previously aborted merge pass.
    rm -f "$TARGET/.claude/agents/"*.kit-merge.tmp
    for agent in "${KIT_AGENTS[@]}"; do
        up="$PROJECT_ROOT/.claude/agents/$agent"
        dst="$TARGET/.claude/agents/$agent"
        merge_args=(merge --upstream "$up" --project-name "$PROJECT_NAME" \
                    --out "$dst.kit-merge.tmp")
        if [ -f "$dst" ]; then
            merge_args+=(--consumer "$dst")
        fi
        python3 "$KIT_MARKERS" "${merge_args[@]}"
    done
    for agent in "${KIT_AGENTS[@]}"; do
        dst="$TARGET/.claude/agents/$agent"
        if [ -f "$dst" ]; then
            echo "  refreshed $agent (preserved filled KIT-LOCAL regions)"
        else
            echo "  installed $agent (KIT-LOCAL regions seeded with placeholders)"
        fi
        mv "$dst.kit-merge.tmp" "$dst"
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

    if [ "$SHAPE" = "planning" ]; then
        # planning repos run the coordination workflows daily — ship the
        # reference docs (single keeps today's lighter skeleton, N1)
        mkdir -p "$TARGET/.kit/context/workflows"
        "${RSYNC_BASE[@]}" "$PROJECT_ROOT/.kit/context/workflows/" \
            "$TARGET/.kit/context/workflows/"
        echo "  .kit/ skeleton ready (tasks/, context/ incl. workflows/, templates/)"
    else
        echo "  .kit/ skeleton ready (tasks/, context/, templates/)"
    fi
else
    # --no-kit: prune any kit agents left by a prior kit-enabled bootstrap so
    # the opt-out is truthful on existing consumers, not just fresh ones.
    # (rsync above already excludes them, so this only removes pre-existing
    # copies; rm -f is a no-op when absent.)
    for agent in "${KIT_AGENTS[@]}"; do
        rm -f "$TARGET/.claude/agents/$agent"
    done
    echo "  Skipped (--no-kit): pruned kit agents (planner*, feature-developer*), no .kit/ scaffold"
fi
echo

# ─────────────────────────────────────────
# Step 2.5 (planning): record the shape in CLAUDE.md
# ─────────────────────────────────────────
if [ "$SHAPE" = "planning" ]; then
    echo "Recording shape in CLAUDE.md..."
    CLAUDE_MD="$TARGET/CLAUDE.md"
    TP="${TARGET_PATH:-../<target-repo>  # TODO: set the product repo path}"
    TG="${TARGET_GITHUB:-<owner>/<repo>  # TODO: set the product repo}"

    if [ ! -f "$CLAUDE_MD" ]; then
        cat > "$CLAUDE_MD" << CLAUDEMD
# $PROJECT_NAME

Planning repo for the target product repository below. Coordination,
task specs, and reviews live here; ALL code changes happen in the
target repo (see docs/CROSS-REPO-PATTERN.md in the kit).
CLAUDEMD
    fi

    # Human-facing convention (KIT-ADR-0024) — agents grep for this
    # section; seeded once, never rewritten (consumer-owned after that).
    if ! grep -q '^## Target Repository' "$CLAUDE_MD"; then
        cat >> "$CLAUDE_MD" << TARGETSECTION

## Target Repository

- **Path**: \`$TP\`
- **GitHub**: \`$TG\`
TARGETSECTION
    fi

    # Machine-written shape record (KIT-0048 F2) — kit_markers is the
    # only writer/reader; append-if-absent so re-bootstrap preserves
    # consumer edits (KIT-LOCAL semantics). Seeded to match the section
    # above; absorbs KIT-0027's intent (mechanism redirected from
    # current-state.json to this runtime-read region).
    if ! python3 "$KIT_MARKERS" regions "$CLAUDE_MD" 2>/dev/null | grep -qx 'kit-install'; then
        cat >> "$CLAUDE_MD" << KITINSTALL

<!-- BEGIN KIT-LOCAL: kit-install -->
shape: planning
target_path: $TP
target_github: $TG
<!-- END KIT-LOCAL: kit-install -->
KITINSTALL
        echo "  kit-install region written (shape: planning)"
    else
        echo "  kit-install region already present (preserved)"
    fi
    echo
fi

# ─────────────────────────────────────────
# Step 3: Initialize git (if needed)
# ─────────────────────────────────────────
echo "3/4 Checking git..."

cd "$TARGET"

# -e, not -d: in a worktree or submodule .git is a FILE — treating it as
# "no repo" would git-init/commit inside an existing checkout (the
# KIT-0048 incident's second ingredient).
if [ -e ".git" ]; then
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
if [ "$SHAPE" = "planning" ]; then
    echo "Your planning repo is scaffolded. To complete setup:"
    echo
    echo "  cd $TARGET"
    echo "  cp .env.template .env                       # evaluator API keys"
    echo "  ./scripts/core/project install-evaluators   # optional: spec evaluations"
    echo "  ./scripts/core/project doctor               # verify the environment"
    echo
    echo "No venv, pyproject, or Python toolchain is needed — the lifecycle"
    echo "runs on system python3 (>= 3.11) + git + gh."
    echo
    echo "Fill in the target-repo pointer (path + github) in CLAUDE.md:"
    echo "  ## Target Repository section AND the kit-install region"
    echo
    echo "Fill in the KIT-LOCAL regions (Project Context / Stack Notes) in:"
    echo "  .claude/agents/planner.md"
    echo "  .claude/agents/feature-developer.md"
    echo
else
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
fi
echo
echo "To pull upstream updates later:"
echo "  git remote add upstream https://github.com/movito/agentive-starter-kit.git"
echo "  git fetch upstream"
echo "  git merge upstream/main"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

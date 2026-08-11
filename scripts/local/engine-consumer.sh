#!/usr/bin/env bash
# engine-consumer.sh — the consumer-sync ENGINE behind the setup door
# (KIT-0053, ADR-0027 P3). Formerly the bootstrap-consumer.sh entrance;
# that filename is now a shim mapping its historical flags onto
# scripts/local/bootstrap. Call the door, not this engine, unless you
# are the door.
#
# Consumer projects get implementation tools (agents, scripts, commands)
# plus a minimal .kit/ workflow skeleton (task folders, context, task-starter
# template) that the shipped V2 planner + feature-developer agents need.
# They do NOT get the full builder layer (evaluators, ADRs, kit planning docs).
#
# Usage (door-internal):
#   engine-consumer.sh [flags] <target-directory>
#
# Flags:
#   --internal-record-only
#              (door-internal, KIT-0053) skip the scaffold/agent/git
#              steps and run ONLY the check-hook seeding (Step 1.5) and
#              the CLAUDE.md install record (Step 2.5). Used by the
#              door's --new path after the export engine has produced
#              the tree, so this engine stays the record's one writer.
#              In this mode existing KIT-LOCAL regions are RESEEDED,
#              not preserved — the fresh export carries the kit's own
#              region content, which is not consumer-owned and must
#              match the recorded install (BugBot, PR #81).
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
#   --profile <python|none>
#              (KIT-0050, ADR-0027 P1) which check-hook content to seed
#              into scripts/local/checks.sh and record in the CLAUDE.md
#              kit-install region. single shape defaults to python (the
#              kit's own gauntlet); none is a loud no-op for docs-only
#              repos. planning shape FORCES none (the P3 matrix pairing)
#              — combining it with --profile python is an error. Other
#              toolchains: seed a profile and edit the hook (the
#              contract is in its header); the kit ships no toolchains
#              it doesn't itself use.
#   --target-path <p>, --target-github <owner/name>
#              (planning shape) recorded in the CLAUDE.md kit-install
#              region and seeded into ## Target Repository. Placeholders
#              are written when omitted.
#   --bots <b> (KIT-0056, ADR-0027 P5) record which review bots run on
#              this project as a `bots:` line in the kit-install region:
#              'none', or a space-separated subset of
#              'coderabbit bugbot' (the door normalizes; this engine
#              validates). Omitted = no line = both bots expected
#              (today's behavior). Preflight Gates 2/3 SKIP
#              declared-absent bots. An existing region without the
#              line gets it added surgically via kit_markers (the one
#              writer path); a conflicting recorded value is an error,
#              never a silent overwrite.
#
# Prerequisites:
#   - Target directory exists
#   - agentive-starter-kit is cloned at the path this script lives in

set -e
IFS=$' \t\n'  # an exported IFS must not affect the scrub loop below

# This script runs git init/add/commit against $TARGET by design. A
# leaked GIT_DIR (pre-commit exports an absolute one inside worktrees)
# would silently redirect every one of those calls at the REAL
# repository — during KIT-0048 exactly that committed a scaffold tree
# onto a live feature branch and flipped the primary clone's core.bare.
# Scrub ALL GIT_* before any git call (the doctor 70-core-bare pattern;
# compgen is fine — this script is bash by shebang).
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
PROFILE=""
TARGET_PATH=""
TARGET_GITHUB=""
BOTS=""
RECORD_ONLY=0
PACKAGED=0
PROJECT_NAME_ARG=""
USAGE="Usage: $0 [--no-kit] [--shape single|planning] [--profile python|none] [--target-path <p>] [--target-github <o/r>] [--bots <b>] <target-directory>"
while [ $# -gt 0 ]; do
    case "$1" in
        --no-kit)
            KIT_ENABLED=0
            ;;
        --internal-record-only)
            RECORD_ONLY=1
            ;;
        --packaged)
            # KIT-0093 (ADR-0028 phase 2): the target is a packaged
            # scaffold — lifecycle scripts come from agentive-kit and
            # agents from the plugin, so the record step ships NO
            # kit_markers.py copy and seeds region bodies that
            # reference `agentive`, never ./scripts/core/. Only
            # meaningful together with --internal-record-only (the
            # door's --new path).
            PACKAGED=1
            ;;
        --shape)
            shift
            SHAPE="${1:-}"
            ;;
        --shape=*)
            SHAPE="${1#--shape=}"
            ;;
        --profile)
            shift
            PROFILE="${1:-}"
            ;;
        --profile=*)
            PROFILE="${1#--profile=}"
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
        --bots)
            shift
            BOTS="${1:-}"
            ;;
        --bots=*)
            BOTS="${1#--bots=}"
            ;;
        --project-name)
            shift
            PROJECT_NAME_ARG="${1:-}"
            ;;
        --project-name=*)
            PROJECT_NAME_ARG="${1#--project-name=}"
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
    # value-consuming flags may have emptied $@ — an unguarded shift
    # would exit 1 under set -e before validation gets to speak
    if [ $# -gt 0 ]; then shift; fi
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
# Profile validation + defaults (KIT-0050 F3): single defaults to
# python; planning FORCES none — an explicit --profile python there is
# an error, never a silent override (the masking class: coercion would
# drop what the operator asked for without saying so).
case "$PROFILE" in
    python|none|"") ;;
    *)
        echo "Error: unknown profile: '$PROFILE' (expected: python | none)"
        echo "$USAGE"
        exit 1
        ;;
esac
if [ "$SHAPE" = "planning" ]; then
    if [ "$PROFILE" = "python" ]; then
        echo "Error: --profile python contradicts --shape planning (planning forces profile none)"
        exit 1
    fi
    PROFILE="none"
elif [ -z "$PROFILE" ]; then
    PROFILE="python"
fi
if [ -n "$TARGET_GITHUB" ] && ! printf '%s' "$TARGET_GITHUB" | grep -qE '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$'; then
    echo "Error: --target-github must look like owner/repo (got: $TARGET_GITHUB)"
    exit 1
fi
# --bots validation (KIT-0056): the door normalizes, but the engine is
# the record's writer and defends its own input — a bad value written
# here would poison every downstream reader.
if [ -n "$BOTS" ]; then
    # read-loop, not `for _bot in $BOTS`: an unquoted for would glob a
    # token like '*' into filenames before validation (CodeRabbit)
    while IFS= read -r _bot; do
        [ -n "$_bot" ] || continue
        case "$_bot" in
            coderabbit|bugbot|none) ;;
            *)
                echo "Error: unknown bot '$_bot' in --bots (expected: 'none' or a subset of 'coderabbit bugbot')"
                exit 1
                ;;
        esac
    done <<EOF
$(printf '%s\n' "$BOTS" | tr ' ' '\n')
EOF
    case " $BOTS " in
        *" none "*)
            if [ "$BOTS" != "none" ]; then
                echo "Error: 'none' cannot be combined with bot names (--bots $BOTS)"
                exit 1
            fi
            ;;
    esac
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
    echo "   the consumer engine provisions a *consumer* checkout; running it"
    echo "   against the kit itself would rsync/sweep its own files. Aborting."
    exit 1
fi
PROJECT_NAME="$(basename "$TARGET")"
# --project-name (door --new with --name, KIT-0093): the display
# identity must not split across artifacts — README/current-state
# carry the given name, so CLAUDE.md's title must too. Same
# heredoc-hostile character strip as the scaffold engine; a name
# that sanitizes to NOTHING falls back to the basename, out loud
# (CodeRabbit, PR #116 — an empty title helps nobody).
if [ -n "$PROJECT_NAME_ARG" ]; then
    _SANITIZED_NAME="${PROJECT_NAME_ARG//[\`\$\"\'$'\n'$'\r']/}"
    if [ -n "$_SANITIZED_NAME" ]; then
        PROJECT_NAME="$_SANITIZED_NAME"
    else
        echo "Warning: --project-name sanitized to empty — using the directory name '$PROJECT_NAME'"
    fi
fi

# --internal-record-only: everything except Steps 1.5 and 2.5 is skipped.
# Guards (not an early exit) keep the record steps in their normal order.
if [ "$RECORD_ONLY" -eq 0 ]; then

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
    lib/target_repo.sh
    logging_config.py
    project
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
# ci-check.sh (the Python gauntlet), pattern_lint.py,
# scripts/optional/, .github/ (Python CI), .serena/, the full
# .pre-commit-config.yaml.

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
else
    echo "1/4 Copying implementation scaffolding..."
fi

# Sweep retired agent variants from a prior bootstrap before rsync;
# --ignore-existing would otherwise leave legacy planner2/3 +
# feature-developer-v3/v6/v7 alongside the canonical V2 agents in an
# existing checkout. Shared across shapes — hoisted so the two branches
# cannot drift (CodeRabbit).
rm -f "$TARGET/.claude/agents/planner2.md" \
      "$TARGET/.claude/agents/planner3.md" \
      "$TARGET/.claude/agents/feature-developer-v3.md" \
      "$TARGET/.claude/agents/feature-developer-v6.md" \
      "$TARGET/.claude/agents/feature-developer-v7.md"
"${RSYNC_BASE[@]}" "${AGENT_EXCLUDES[@]}" \
    "$PROJECT_ROOT/.claude/" "$TARGET/.claude/"

if [ "$SHAPE" = "planning" ]; then
    # Sweep the retired copy-sync machinery (KIT-0102, ADR-0028 phase 4)
    # out of consumers bootstrapped before it: the cp loop below is
    # guarded by [ ! -e ] and doctor.d/ rsyncs with --ignore-existing, so
    # neither would ever remove a stale file on its own.
    rm -f "$TARGET/scripts/core/sync_from_manifest.py" \
          "$TARGET/scripts/.core-manifest.json" \
          "$TARGET/scripts/core/doctor.d/60-push-sync-token.sh"
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

    # .adversarial/ — config + docs + templates; evaluators are offered
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

    echo "Done"
    echo
else
# .serena/ — setup script and template
"${RSYNC_BASE[@]}" --exclude='cache/' --exclude='memories/' --exclude='claude-code/' \
    "$PROJECT_ROOT/.serena/" "$TARGET/.serena/"

# scripts/core/ — shared scripts. The copy-sync machinery was retired in
# KIT-0102 (ADR-0028 phase 4); RSYNC_BASE uses --ignore-existing, so a
# consumer bootstrapped earlier would keep the dead engine and a manifest
# pointing at it forever. Sweep both, same as the retired workflow above.
rm -f "$TARGET/scripts/core/sync_from_manifest.py" \
      "$TARGET/scripts/.core-manifest.json" \
      "$TARGET/scripts/core/doctor.d/60-push-sync-token.sh"
mkdir -p "$TARGET/scripts/core"
"${RSYNC_BASE[@]}" "$PROJECT_ROOT/scripts/core/" "$TARGET/scripts/core/"

# scripts/optional/ — opt-in scripts
mkdir -p "$TARGET/scripts/optional"
"${RSYNC_BASE[@]}" "$PROJECT_ROOT/scripts/optional/" "$TARGET/scripts/optional/"

# .github/ — CI workflows. plugin-drift.yml is kit-internal (its script
# lives in the unsynced scripts/local/); the rm -f also sweeps stale
# copies from a pre-exclusion bootstrap — --ignore-existing would
# otherwise leave them behind in existing consumers.
# sync-core-scripts.yml was deleted upstream in KIT-0102 (ADR-0028
# phase 4); the rm -f sweeps stale copies out of consumers bootstrapped
# before that, the same way plugin-drift.yml is swept.
rm -f "$TARGET/.github/workflows/plugin-drift.yml"
rm -f "$TARGET/.github/workflows/sync-core-scripts.yml"
"${RSYNC_BASE[@]}" \
    --exclude='sync-to-linear.yml' \
    --exclude='plugin-drift.yml' \
    "$PROJECT_ROOT/.github/" "$TARGET/.github/"

# tests/ — test infrastructure. Exclude tests that import or read
# scripts/local/ content (kit_markers.py, the setup door):
# scripts/local is an ASK-only layer that is never synced to consumers,
# so shipping these tests would break consumer pytest (and the
# pytest-fast pre-commit hook) at collection time. The rm -f sweep
# removes stale copies from a pre-fix bootstrap — --ignore-existing
# would otherwise leave the orphaned tests behind in existing consumers.
rm -f "$TARGET/tests/test_kit_markers.py" \
      "$TARGET/tests/test_plugin_drift.py" \
      "$TARGET/tests/test_bootstrap_consumer.py" \
      "$TARGET/tests/test_bootstrap_shapes.py" \
      "$TARGET/tests/test_bots_conformance.py" \
      "$TARGET/tests/test_check_hook_seeds.py" \
      "$TARGET/tests/test_entrance_shims.py" \
      "$TARGET/tests/test_engine_materials.py" \
      "$TARGET/tests/test_new_worktree.py" \
      "$TARGET/tests/test_scaffold_acceptance.py" \
      "$TARGET/tests/test_setup_door.py"
"${RSYNC_BASE[@]}" --exclude='test_kit_markers.py' \
    --exclude='test_plugin_drift.py' \
    --exclude='test_bootstrap_consumer.py' \
    --exclude='test_bootstrap_shapes.py' \
    --exclude='test_bots_conformance.py' \
    --exclude='test_check_hook_seeds.py' \
    --exclude='test_entrance_shims.py' \
    --exclude='test_engine_materials.py' \
    --exclude='test_new_worktree.py' \
    --exclude='test_scaffold_acceptance.py' \
    --exclude='test_setup_door.py' \
    "$PROJECT_ROOT/tests/" "$TARGET/tests/"

# Top-level files (only if they don't exist in target)
for f in pyproject.toml .gitignore .pre-commit-config.yaml .env.template .coderabbitignore conftest.py; do
    if [ -f "$PROJECT_ROOT/$f" ] && [ ! -f "$TARGET/$f" ]; then
        cp "$PROJECT_ROOT/$f" "$TARGET/$f"
        if [ "$f" = "pyproject.toml" ]; then
            # The kit's own pyproject is named agentive-starter-kit
            # (KIT-0057); a freshly seeded target must get the
            # placeholder + TODO the setup agents rewrite — the
            # engine-export.sh reset, applied to this copy path too
            # (BugBot, PR #90).
            NAME_PLACEHOLDER='name = "your-project-name"  # TODO: Change this to your project name'
            sed -i '' "s/^name = .*/$NAME_PLACEHOLDER/" "$TARGET/$f" 2>/dev/null || \
            sed -i "s/^name = .*/$NAME_PLACEHOLDER/" "$TARGET/$f"
        fi
    fi
done

echo "Done"
echo
fi

fi  # RECORD_ONLY guard (Step 1)

# ─────────────────────────────────────────
# Step 1.5: project check hook (KIT-0050, ADR-0027 P1)
# ─────────────────────────────────────────
echo "1.5/4 Seeding the project check hook..."
# checks.sh is seeded ONCE per profile and consumer-owned afterwards:
# re-bootstrap preserves it and it rides no sync tier (N4) — the kit
# never overwrites it. ci-check.sh dispatches to it when present.
mkdir -p "$TARGET/scripts/local"
if [ ! -e "$TARGET/scripts/local/checks.sh" ]; then
    cp "$PROJECT_ROOT/scripts/local/templates/checks-$PROFILE.sh" \
       "$TARGET/scripts/local/checks.sh"
    chmod +x "$TARGET/scripts/local/checks.sh"
    echo "  seeded scripts/local/checks.sh (profile: $PROFILE)"
else
    echo "  scripts/local/checks.sh already present (preserved — consumer-owned)"
fi
# kit_markers.py is the only reader of the CLAUDE.md kit-install region
# (doctor and sync consult it at runtime). Planning ships it via
# PLANNING_LOCAL above; single shapes need it too, or the profile
# recorded in Step 2.5 would be silently ignored (the reader-absent
# path falls back to defaults — exactly the masking this record exists
# to prevent). PACKAGED scaffolds ship no copy: the agentive-kit
# package reads the record itself (agentive_kit.doctor / .markers), so
# the reader travels with the CLI, not the repo (KIT-0093).
if [ "$PACKAGED" -eq 0 ] && [ ! -e "$TARGET/scripts/local/kit_markers.py" ]; then
    cp "$PROJECT_ROOT/scripts/local/kit_markers.py" \
       "$TARGET/scripts/local/kit_markers.py"
fi
echo

# ─────────────────────────────────────────
# Step 2: Kit workflow agents + skeleton
# ─────────────────────────────────────────
if [ "$RECORD_ONLY" -eq 0 ]; then
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
fi  # RECORD_ONLY guard (Step 2)

# ─────────────────────────────────────────
# Step 2.5: record the install (shape + profile) in CLAUDE.md
# ─────────────────────────────────────────
echo "Recording install (shape: $SHAPE, profile: $PROFILE) in CLAUDE.md..."
CLAUDE_MD="$TARGET/CLAUDE.md"

if [ "$SHAPE" = "planning" ]; then
    TP="${TARGET_PATH:-../<target-repo>  # TODO: set the product repo path}"
    TG="${TARGET_GITHUB:-<owner>/<repo>  # TODO: set the product repo}"

    # printf %s + quoted heredoc delimiters everywhere below: the
    # target-pointer values are operator input and must be written
    # literally — an unquoted heredoc would shell-expand $(...) inside
    # them (claude-code review, heredoc injection).
    if [ ! -f "$CLAUDE_MD" ]; then
        printf '# %s\n\nPlanning repo for the target product repository below. Coordination,\ntask specs, and reviews live here; ALL code changes happen in the\ntarget repo (see docs/CROSS-REPO-PATTERN.md in the kit).\n' \
            "$PROJECT_NAME" > "$CLAUDE_MD"
    fi

    # Human-facing convention (KIT-ADR-0024) — agents grep for this
    # section; seeded once, never rewritten (consumer-owned after that).
    # When the section ALREADY exists it is the source of truth: the
    # region below seeds FROM it so the two records never disagree, and
    # conflicting flags are an error, not a silent desync (BugBot, PR #78).
    if grep -q '^## Target Repository' "$CLAUDE_MD"; then
        # whole-section extraction (heading to next ## heading) — a fixed
        # -A window misses layouts with prose before the bullets (BugBot)
        TARGET_SECTION="$(awk '/^## Target Repository/{in_s=1; next} in_s && /^## /{in_s=0} in_s' "$CLAUDE_MD")"
        EXISTING_TP="$(printf '%s\n' "$TARGET_SECTION" | grep -E '^\- \*\*Path\*\*:' | head -1 | sed -E 's/.*`([^`]*)`.*/\1/')"
        EXISTING_TG="$(printf '%s\n' "$TARGET_SECTION" | grep -E '^\- \*\*GitHub\*\*:' | head -1 | sed -E 's/.*`([^`]*)`.*/\1/')"
        if [ -n "$TARGET_PATH" ] && [ -n "$EXISTING_TP" ] && [ "$TARGET_PATH" != "$EXISTING_TP" ]; then
            echo "Error: --target-path '$TARGET_PATH' conflicts with the existing"
            echo "       ## Target Repository section ('$EXISTING_TP')."
            echo "       Update the section first, or drop the flag."
            exit 1
        fi
        if [ -n "$TARGET_GITHUB" ] && [ -n "$EXISTING_TG" ] && [ "$TARGET_GITHUB" != "$EXISTING_TG" ]; then
            echo "Error: --target-github '$TARGET_GITHUB' conflicts with the existing"
            echo "       ## Target Repository section ('$EXISTING_TG')."
            echo "       Update the section first, or drop the flag."
            exit 1
        fi
        [ -n "$EXISTING_TP" ] && TP="$EXISTING_TP"
        [ -n "$EXISTING_TG" ] && TG="$EXISTING_TG"
    else
        printf '\n## Target Repository\n\n- **Path**: `%s`\n- **GitHub**: `%s`\n' \
            "$TP" "$TG" >> "$CLAUDE_MD"
    fi
elif [ ! -f "$CLAUDE_MD" ]; then
    # single shape (KIT-0050): the install record and Project Rules
    # region below need a CLAUDE.md to live in — seed a minimal one.
    printf '# %s\n\nProject instructions for Claude Code agents working in this repo.\n' \
        "$PROJECT_NAME" > "$CLAUDE_MD"
fi

# Machine-written install record (KIT-0048 F2, profile added by
# KIT-0050 F4) — kit_markers is the only writer/reader; append-if-
# absent so re-bootstrap preserves consumer edits (KIT-LOCAL
# semantics). Absent profile defaults by shape (single -> python,
# planning -> none), so pre-KIT-0050 regions stay valid unmodified.
# a reader FAILURE must not read as "region absent" — appending a
# fresh block over a malformed file would duplicate/corrupt it
# (CodeRabbit; the same fail-loud class as the doctor reader fix)
if ! REGIONS_OUT="$(python3 "$KIT_MARKERS" regions "$CLAUDE_MD" 2>&1)"; then
    echo "Error: kit_markers regions failed on $CLAUDE_MD:"
    echo "       $REGIONS_OUT"
    exit 1
fi

# Append a KIT-LOCAL region to CLAUDE.md unless already present —
# the shared append-if-absent shape for every region this step seeds
# (CodeRabbit, PR #80). $1 region name, $2 content, $3 status detail.
# Reads $REGIONS_OUT/$CLAUDE_MD from the enclosing scope.
append_region_if_absent() {
    if printf '%s\n' "$REGIONS_OUT" | grep -qx "$1"; then
        echo "  $1 region already present (preserved)"
        return 0
    fi
    {
        printf '\n<!-- BEGIN KIT-LOCAL: %s -->\n' "$1"
        printf '%s\n' "$2"
        printf '<!-- END KIT-LOCAL: %s -->\n' "$1"
    } >> "$CLAUDE_MD"
    echo "  $1 region written ($3)"
}

# Replace the body of an existing KIT-LOCAL region in-place. Used ONLY
# under --internal-record-only: there the target was just produced from
# the kit's own tree by the export engine, so an existing region is the
# KIT's copy, never consumer-owned — preserving it would ship guidance
# that contradicts the recorded install (BugBot, PR #81: a profile-none
# export carried the kit's python Project Rules next to profile: none).
# Body passes via the environment — awk -v would mangle backslashes.
replace_region() {
    # mktemp, not a predictable suffix: a pre-planted symlink at a
    # fixed tmp name could redirect the write (CodeRabbit, this PR —
    # same class as remove_region_if_unmodified below)
    RESEED_TMP="$(mktemp "$CLAUDE_MD.kit-reseed.XXXXXX")"
    REGION_BODY="$2" awk -v region="$1" '
        $0 == "<!-- BEGIN KIT-LOCAL: " region " -->" {
            print; print ENVIRON["REGION_BODY"]; skip=1; next
        }
        $0 == "<!-- END KIT-LOCAL: " region " -->" { skip=0 }
        !skip { print }
    ' "$CLAUDE_MD" > "$RESEED_TMP"
    mv "$RESEED_TMP" "$CLAUDE_MD"
    echo "  $1 region reseeded ($3)"
}

# Seed a region: reseed on the fresh-export path, else append-if-absent
# (the consumer-owned KIT-LOCAL semantics stay untouched).
seed_region() {
    if [ "$RECORD_ONLY" -eq 1 ] && printf '%s\n' "$REGIONS_OUT" | grep -qx "$1"; then
        replace_region "$1" "$2" "$3"
    else
        append_region_if_absent "$1" "$2" "$3"
    fi
}

if [ "$SHAPE" = "planning" ]; then
    KIT_INSTALL_BODY="$(printf 'shape: planning\nprofile: %s\ntarget_path: %s\ntarget_github: %s' \
        "$PROFILE" "$TP" "$TG")"
else
    KIT_INSTALL_BODY="$(printf 'shape: single\nprofile: %s' "$PROFILE")"
fi
if [ -n "$BOTS" ]; then
    KIT_INSTALL_BODY="$KIT_INSTALL_BODY
bots: $BOTS"
fi
seed_region kit-install "$KIT_INSTALL_BODY" \
    "shape: $SHAPE, profile: $PROFILE${BOTS:+, bots: $BOTS}"

# A PRESERVED region + --bots: the seed above did not touch it, and
# silently dropping an explicit declaration would be the masking
# class. Add the line surgically via kit_markers (the one writer
# path); a conflicting recorded value is an error, never an overwrite.
if [ -n "$BOTS" ]; then
    if ! REGION_NOW="$(python3 "$KIT_MARKERS" extract "$CLAUDE_MD" kit-install 2>&1)"; then
        echo "Error: kit_markers extract kit-install failed on $CLAUDE_MD:"
        echo "       $REGION_NOW"
        exit 1
    fi
    # whitespace-tolerant like every other record reader — an indented
    # existing line read as "absent" would append a SECOND bots: line
    EXISTING_BOTS="$(printf '%s\n' "$REGION_NOW" |
        sed -n 's/^[[:space:]]*bots:[[:space:]]*//p' | head -1 |
        sed 's/[[:space:]]*$//')"
    # sorted-set canonical form for the equality check below — an
    # existing 'BugBot, CodeRabbit' is the same declaration as
    # 'coderabbit bugbot', not a conflict (BugBot, this PR)
    _canon_bots() {
        printf '%s' "$1" | tr ',' ' ' | tr '[:upper:]' '[:lower:]' |
            tr ' ' '\n' | grep -v '^$' | sort -u | tr '\n' ' ' | sed 's/ $//'
    }
    if printf '%s\n' "$REGION_NOW" | grep -q '^[[:space:]]*bots:' && [ -z "$EXISTING_BOTS" ]; then
        # presence-aware (CodeRabbit): a bots: line WITH NO VALUE is a
        # malformed record, not absence — appending a second line after
        # it would leave two declarations for downstream readers
        echo "Error: the target's kit-install region has a bots: line with no value — fix the record in CLAUDE.md, then re-run"
        exit 1
    elif [ -z "$EXISTING_BOTS" ]; then
        # no trailing newline: the region body group excludes the
        # newline before END, so extract→replace stays byte-identical
        printf '%s\nbots: %s' "$REGION_NOW" "$BOTS" |
            python3 "$KIT_MARKERS" replace "$CLAUDE_MD" kit-install --stdin
        echo "  kit-install region: bots line added (bots: $BOTS)"
    elif [ "$(_canon_bots "$EXISTING_BOTS")" != "$(_canon_bots "$BOTS")" ]; then
        echo "Error: --bots '$BOTS' conflicts with the recorded declaration (bots: $EXISTING_BOTS)"
        echo "       Update the kit-install region in CLAUDE.md first, or drop the flag."
        exit 1
    fi
fi

# Project Rules region (KIT-0050 F6) — seeded per profile, consumer-
# owned afterwards (append-if-absent, same KIT-LOCAL semantics). The
# python content is extracted from the kit's OWN marker-wrapped rules
# so there is exactly one source of that text. Content stays computed
# only when the region is absent: a re-bootstrap of a consumer that
# already owns its rules must not depend on the kit-side extract.
# On the fresh-export path the region is always recomputed + reseeded
# (the kit's own copy is not consumer-owned — see replace_region).
if [ "$RECORD_ONLY" -eq 0 ] && printf '%s\n' "$REGIONS_OUT" | grep -qx 'project-rules'; then
    echo "  project-rules region already present (preserved)"
else
    if [ "$PACKAGED" -eq 1 ]; then
        # Packaged scaffolds (KIT-0093): the rules reference the
        # installed `agentive` CLI, never ./scripts/core/ — that
        # directory does not exist in a packaged repo.
        if [ "$PROFILE" = "python" ]; then
            RULES_BODY="$(cat << 'RULES'
## Project Rules

- Python project (profile: python). The check hook
  `scripts/local/checks.sh` is the gauntlet for this repo — edit it
  as the project grows (the contract is in its header).
- Task workflow: task files live in `.kit/tasks/<status-folder>/`;
  use `agentive start|move|complete <TASK-ID>`.
- Feature branches: `feature/<TASK-ID>-short-description`.
- Environment checks: `agentive doctor`.
RULES
)"
        else
            RULES_BODY="$(cat << 'RULES'
## Project Rules

- No project toolchain is configured (profile: none). The check hook
  `scripts/local/checks.sh` is a loud no-op — edit it to add checks
  (the contract is in its header).
- Task workflow: task files live in `.kit/tasks/<status-folder>/`;
  use `agentive start|move|complete <TASK-ID>`.
- Feature branches: `feature/<TASK-ID>-short-description`.
- Environment checks: `agentive doctor`.
RULES
)"
        fi
    elif [ "$PROFILE" = "python" ]; then
        if ! RULES_BODY="$(python3 "$KIT_MARKERS" extract "$PROJECT_ROOT/CLAUDE.md" project-rules 2>&1)"; then
            echo "Error: kit_markers extract project-rules failed on the kit's CLAUDE.md:"
            echo "       $RULES_BODY"
            exit 1
        fi
    else
        RULES_BODY="$(cat << 'RULES'
## Project Rules

- No project toolchain is configured (profile: none). The check hook
  `scripts/local/checks.sh` is a loud no-op — edit it to add checks
  (the contract is in its header).
- Task workflow: task files live in `.kit/tasks/<status-folder>/`;
  use `./scripts/core/project start|move|complete <TASK-ID>`.
- Feature branches: `feature/<TASK-ID>-short-description`.
RULES
)"
    fi
    seed_region project-rules "$RULES_BODY" "profile: $PROFILE"
fi

# Drop a KIT-LOCAL region, markers included — but ONLY if its body is
# still byte-identical to what the kit seeded ($2). A customized body
# is consumer-owned and stays (with a notice), same KIT-LOCAL
# semantics as everywhere else. The body is read via kit_markers
# extract, whose regex requires a BALANCED marker pair — so a
# malformed file (BEGIN without END) fails loud here instead of
# letting the awk below eat everything to EOF (fast-gate evaluator
# round 2, KIT-0067). Only for regions an install MODE invalidates.
remove_region_if_unmodified() {
    # $4 (optional): a LEGACY seeded body — a consumer seeded before
    # the kit's text changed still carries the old body verbatim, and
    # that is "unmodified", not "customized" (KIT-0084 upgrade path).
    if ! printf '%s\n' "$REGIONS_OUT" | grep -qx "$1"; then
        return 0
    fi
    if ! REGION_BODY_NOW="$(python3 "$KIT_MARKERS" extract "$CLAUDE_MD" "$1" 2>&1)"; then
        echo "Error: kit_markers extract $1 failed on $CLAUDE_MD:"
        echo "       $REGION_BODY_NOW"
        exit 1
    fi
    if [ "$REGION_BODY_NOW" != "$2" ] && { [ -z "${4:-}" ] || [ "$REGION_BODY_NOW" != "$4" ]; }; then
        echo "  $1 region customized — left in place (consumer-owned)"
        return 0
    fi
    # mktemp, not a predictable suffix (CodeRabbit, this PR): a
    # pre-planted symlink at a fixed tmp name could redirect the write
    REMOVE_TMP="$(mktemp "$CLAUDE_MD.kit-remove.XXXXXX")"
    awk -v region="$1" '
        $0 == "<!-- BEGIN KIT-LOCAL: " region " -->" { skip=1; next }
        $0 == "<!-- END KIT-LOCAL: " region " -->" { skip=0; next }
        !skip { print }
    ' "$CLAUDE_MD" > "$REMOVE_TMP"
    mv "$REMOVE_TMP" "$CLAUDE_MD"
    echo "  $1 region removed ($3)"
}

# First-session self-direction (KIT-0067 F3): the seeded CLAUDE.md
# closes by telling a cold-open session what to do first. Only where
# the planner actually ships (--no-kit prunes the kit agents — and
# removes an unmodified region left by an earlier kit-enabled install).
# The pre-KIT-0084 body: consumers seeded with it and left unmodified
# must still count as unmodified on a --no-kit re-bootstrap.
FIRST_SESSION_BODY_LEGACY="First session in this repo: invoke the \`planner\` agent (in a new tab) — it triages the backlog and recommends what to start."
FIRST_SESSION_BODY="First session in this repo: invoke the \`planner\` agent (in a new tab) — it triages the backlog and recommends what to start. Before the first evaluation, verify \`./scripts/core/project doctor\` reports env-keys green (API keys are operator-provisioned — see .env)."
# Packaged scaffolds (KIT-0093): the doctor lives in the installed CLI.
if [ "$PACKAGED" -eq 1 ]; then
    FIRST_SESSION_BODY="First session in this repo: invoke the \`planner\` agent (in a new tab) — it triages the backlog and recommends what to start. Before the first evaluation, verify \`agentive doctor\` reports env-keys green (API keys are operator-provisioned — see .env)."
fi
if [ "$KIT_ENABLED" -eq 1 ]; then
    seed_region first-session "$FIRST_SESSION_BODY" "planner self-direction"
else
    remove_region_if_unmodified first-session "$FIRST_SESSION_BODY" \
        "--no-kit: planner not shipped" "$FIRST_SESSION_BODY_LEGACY"
fi
echo

# ─────────────────────────────────────────
# Step 3: Initialize git (if needed)
# ─────────────────────────────────────────
if [ "$RECORD_ONLY" -eq 0 ]; then
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
    # KIT-0081 F1: the tail reflects what was actually resolved — an
    # operator whose flags/preset filled the pointer must not be told
    # to fill it in (they'd conclude the install is incomplete).
    case "$TP$TG" in
        *TODO*|*'<owner>'*|*'<target-repo>'*)
            echo "Fill in the target-repo pointer (path + github) in CLAUDE.md:"
            echo "  ## Target Repository section AND the kit-install region"
            ;;
        *)
            echo "Target-repo pointer recorded in CLAUDE.md: $TP ($TG) — verify it."
            ;;
    esac
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
fi  # RECORD_ONLY guard (Steps 3+4)

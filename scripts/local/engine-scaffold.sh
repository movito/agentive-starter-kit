#!/usr/bin/env bash
# engine-scaffold.sh — the packaged-world content ENGINE behind the
# setup door's --new path (KIT-0093, KIT-ADR-0028 phase 2).
#
# Creates CONTENT, never machinery: the .kit/ skeleton (task folders,
# context, templates, workflows), docs/adr/, README, config templates,
# and the .adversarial/ config with both pins. Lifecycle scripts come
# from the agentive-kit package and agent bodies from the
# agentive-workflow plugin — the door verifies (or instructs) those
# installs; nothing is copied here. Call the door, not this engine,
# unless you are the door.
#
# The CLAUDE.md identity + kit-install record are NOT written here —
# engine-consumer.sh (--internal-record-only) remains the record's one
# writer, and the door runs it right after this engine. Git init and
# the initial commit are the door's job too (KIT-0084 env seeding needs
# the repo to exist; the door owns that ordering).
#
# Usage (door-internal):
#   engine-scaffold.sh <target-dir> --shape single|planning \
#       [--profile python|none] [--name NAME] [--prefix PREFIX] \
#       [--target-path <p>] [--target-github <owner/repo>]
#
# <target-dir> must exist and be empty-ish (the door creates it fresh
# on --new); existing files are never overwritten.

set -euo pipefail
IFS=$' \t\n'

# GIT_* scrub — defense in depth for direct invocation (the KIT-0048
# leak class; this engine runs no git, but the python3 heredocs below
# must not inherit a poisoned environment either).
for _git_var in $(compgen -A variable | grep '^GIT_' || true); do
    unset "$_git_var"
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

TARGET=""
SHAPE=""
PROFILE=""
NAME=""
PREFIX=""
TARGET_PATH=""
TARGET_GITHUB=""
USAGE="Usage: $0 <target-dir> --shape single|planning [--profile python|none] [--name N] [--prefix P] [--target-path <p>] [--target-github <o/r>]"

while [ $# -gt 0 ]; do
    case "$1" in
        --shape)           shift; SHAPE="${1:-}" ;;
        --shape=*)         SHAPE="${1#--shape=}" ;;
        --profile)         shift; PROFILE="${1:-}" ;;
        --profile=*)       PROFILE="${1#--profile=}" ;;
        --name)            shift; NAME="${1:-}" ;;
        --name=*)          NAME="${1#--name=}" ;;
        --prefix)          shift; PREFIX="${1:-}" ;;
        --prefix=*)        PREFIX="${1#--prefix=}" ;;
        --target-path)     shift; TARGET_PATH="${1:-}" ;;
        --target-path=*)   TARGET_PATH="${1#--target-path=}" ;;
        --target-github)   shift; TARGET_GITHUB="${1:-}" ;;
        --target-github=*) TARGET_GITHUB="${1#--target-github=}" ;;
        --*)
            echo "Error: unknown flag: $1" >&2
            echo "$USAGE" >&2
            exit 1
            ;;
        *)
            if [ -n "$TARGET" ]; then
                echo "Error: multiple target directories given" >&2
                exit 1
            fi
            TARGET="$1"
            ;;
    esac
    if [ $# -gt 0 ]; then shift; fi
done

[ -n "$TARGET" ] || { echo "$USAGE" >&2; exit 1; }
case "$SHAPE" in
    single|planning) ;;
    *) echo "Error: --shape single|planning is required (got: '$SHAPE')" >&2; exit 1 ;;
esac
[ -d "$TARGET" ] || { echo "Error: target does not exist: $TARGET (the door creates it)" >&2; exit 1; }
TARGET="$(cd "$TARGET" && pwd)"
if [ "$TARGET" = "$KIT_ROOT" ]; then
    echo "Error: target is the kit source repo itself" >&2
    exit 1
fi

PROJECT_NAME="${NAME:-$(basename "$TARGET")}"

# Task-prefix derivation (single shape; ported from the retired
# engine-export.sh so --new keeps deriving identical prefixes):
# uppercase first letters of each word, max 4 chars; fallback to the
# basename's first 4 alphanumerics. Planning shape: EMPTY — intake
# decides it, and doctor warns meanwhile (KIT-0084).
if [ "$SHAPE" = "single" ] && [ -z "$PREFIX" ]; then
    PREFIX=$(echo "$PROJECT_NAME" | tr '[:lower:]' '[:upper:]' | sed 's/[^A-Z0-9 ]//g' | awk '{for(i=1;i<=NF;i++) printf substr($i,1,1)}' | cut -c1-4)
    if [ ${#PREFIX} -lt 2 ]; then
        # dash LAST in the tr set — a leading dash reads as an option
        # flag under BSD tr (engine-export lesson, kept verbatim)
        PREFIX=$(basename "$TARGET" | tr '[:lower:]' '[:upper:]' | tr -d '_ -' | cut -c1-4)
    fi
fi
[ "$SHAPE" = "planning" ] && PREFIX=""

echo "Scaffolding content (shape: $SHAPE): $TARGET"

copy_if_absent() {  # $1 kit-relative source, $2 target-relative dest
    if [ -f "$KIT_ROOT/$1" ] && [ ! -e "$TARGET/$2" ]; then
        mkdir -p "$TARGET/$(dirname "$2")"
        cp "$KIT_ROOT/$1" "$TARGET/$2"
    fi
}

# ── .kit/ skeleton: task folders, context, templates, workflows ──
for d in 1-backlog 2-todo 3-in-progress 4-in-review 5-done 6-canceled 7-blocked; do
    mkdir -p "$TARGET/.kit/tasks/$d"
    [ -e "$TARGET/.kit/tasks/$d/.gitkeep" ] || touch "$TARGET/.kit/tasks/$d/.gitkeep"
done
mkdir -p "$TARGET/.kit/context/workflows" "$TARGET/.kit/templates" "$TARGET/docs/adr"
[ -e "$TARGET/docs/adr/.gitkeep" ] || touch "$TARGET/docs/adr/.gitkeep"
copy_if_absent ".kit/templates/TASK-STARTER-TEMPLATE.md" ".kit/templates/TASK-STARTER-TEMPLATE.md"
copy_if_absent ".kit/templates/PROTOTYPE-HANDOFF-TEMPLATE.md" ".kit/templates/PROTOTYPE-HANDOFF-TEMPLATE.md"
# Workflow reference docs are CONTENT the plugin agents read at
# runtime (KIT-0081 F2 named their absence a scaffold defect) — both
# shapes get them.
for wf in "$KIT_ROOT"/.kit/context/workflows/*.md; do
    [ -f "$wf" ] || continue
    dest="$TARGET/.kit/context/workflows/$(basename "$wf")"
    [ -e "$dest" ] || cp "$wf" "$dest"
done
# The split-pair pattern doc: the planner routes every git operation
# by it in split mode (the worst KIT-0081 F2 gap).
copy_if_absent "docs/CROSS-REPO-PATTERN.md" "docs/CROSS-REPO-PATTERN.md"

# ── Coordination state the planner reads from Phase 1 on ──
if [ ! -e "$TARGET/.kit/context/agent-handoffs.json" ]; then
    cat > "$TARGET/.kit/context/agent-handoffs.json" << 'HANDOFF_EOF'
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
fi

# current-state.json — serialized by json.dump, never string
# interpolation (the engine-export CodeRabbit lesson, PR #81).
if [ ! -e "$TARGET/.kit/context/current-state.json" ]; then
    PROJECT_NAME="$PROJECT_NAME" TASK_PREFIX="$PREFIX" TARGET_DIR="$TARGET" python3 - << 'PYEOF'
import json
import os

state = {
    "project": {
        "name": os.environ["PROJECT_NAME"],
        "task_prefix": os.environ["TASK_PREFIX"],
        "version": "0.1.0",
    },
    "phase": "bootstrap",
    "onboarding": {"completed": False},
}
path = os.path.join(os.environ["TARGET_DIR"], ".kit", "context", "current-state.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(state, f, indent=2)
    f.write("\n")
PYEOF
fi

# ── Top-level config content ──
copy_if_absent ".env.template" ".env.template"
copy_if_absent ".gitignore" ".gitignore"
copy_if_absent ".coderabbitignore" ".coderabbitignore"

# Pre-commit: task hygiene only, delegated to the packaged CLI — no
# scripts/core to point hooks at (the packaged world's one install
# home; profile toolchain checks live in scripts/local/checks.sh).
if [ ! -f "$TARGET/.pre-commit-config.yaml" ]; then
    cat > "$TARGET/.pre-commit-config.yaml" << 'PRECOMMIT'
# Task hygiene (agentive-kit packaged scaffold): the status validator
# runs via the installed `agentive` CLI. Add your project's toolchain
# hooks as it grows — scripts/local/checks.sh is the check-hook home.
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
        entry: agentive validate
        language: system
        files: ^\.kit/tasks/.*\.md$
        pass_filenames: false
        stages: [pre-commit]
PRECOMMIT
fi

# ── .adversarial/: config with BOTH pins + templates ──
mkdir -p "$TARGET/.adversarial/inputs" "$TARGET/.adversarial/logs"
[ -e "$TARGET/.adversarial/inputs/.gitkeep" ] || touch "$TARGET/.adversarial/inputs/.gitkeep"
if [ -d "$KIT_ROOT/.adversarial/templates" ]; then
    mkdir -p "$TARGET/.adversarial/templates"
    for t in "$KIT_ROOT"/.adversarial/templates/*; do
        [ -f "$t" ] || continue
        dest="$TARGET/.adversarial/templates/$(basename "$t")"
        [ -e "$dest" ] || cp "$t" "$dest"
    done
fi
if [ ! -f "$TARGET/.adversarial/config.yml" ]; then
    # Pins are read from the KIT's own config.yml so a scaffold is
    # born on the same versions the kit runs (no baked-in default —
    # the KIT-0068 A08 stale-fallback lesson). Fail loud if unreadable.
    CLI_PIN="$(sed -n 's/^adversarial_cli_version:[[:space:]]*["'\'']\{0,1\}\([^"'\''#[:space:]]*\).*/\1/p' "$KIT_ROOT/.adversarial/config.yml" | head -1)"
    LIB_PIN="$(sed -n 's/^evaluator_library_version:[[:space:]]*["'\'']\{0,1\}\([^"'\''#[:space:]]*\).*/\1/p' "$KIT_ROOT/.adversarial/config.yml" | head -1)"
    if [ -z "$CLI_PIN" ] || [ -z "$LIB_PIN" ]; then
        echo "Error: could not read the adversarial pins from the kit's .adversarial/config.yml" >&2
        exit 1
    fi
    cat > "$TARGET/.adversarial/config.yml" << ADVCONFIG
# Adversarial Workflow Configuration
# ==================================
#
# Evaluators:
# - Built-in: evaluate, proofread, review (require OPENAI_API_KEY)
# - Custom: Add YAML files to .adversarial/evaluators/
# - Library: run \`agentive install-evaluators\` (installs the library
#   at the pin below plus the adversarial CLI)
#
# Commands:
#   adversarial list-evaluators     # See available evaluators
#   adversarial evaluate <file>     # Run built-in plan evaluation
#   adversarial <name> <file>       # Run custom evaluator

# Toolchain pins (the canonical pin home — KIT-0083):
#   adversarial_cli_version    → the CLI: a PyPI distribution
#   evaluator_library_version  → the evaluator library: a git tag on
#                                movito/adversarial-evaluator-library
adversarial_cli_version: "$CLI_PIN"
evaluator_library_version: "$LIB_PIN"

# Directory containing task specifications
task_directory: .kit/tasks/

# Directory for evaluation logs
log_directory: .adversarial/logs/

# Directory for temporary artifacts
artifacts_directory: .adversarial/artifacts/
ADVCONFIG
fi

# ── README: the repo must name its own purpose (KIT-0081 F8 — a
# scaffold whose visible contents are two folders reads as empty) ──
if [ ! -f "$TARGET/README.md" ]; then
    if [ "$SHAPE" = "planning" ]; then
        cat > "$TARGET/README.md" << README_EOF
# $PROJECT_NAME

Planning repository for the product repo this project coordinates —
task specs, handoffs, and reviews live here; ALL code changes happen
in the target repo (see \`docs/CROSS-REPO-PATTERN.md\`, and the
\`## Target Repository\` pointer in \`CLAUDE.md\`).

Most of this repo lives in dot-folders your file browser may hide:

| Folder | What's in it |
|--------|--------------|
| \`.kit/tasks/\` | Task specs by status (\`1-backlog\` … \`7-blocked\`) |
| \`.kit/context/\` | Handoffs, reviews, workflow reference docs |
| \`.kit/templates/\` | Task and handoff templates |
| \`.adversarial/\` | Evaluation config, inputs, and logs |
| \`docs/adr/\` | Architecture decision records |

Tooling is installed, not copied (agentive-kit phase 2):

- **Lifecycle CLI**: \`uv tool install agentive-kit\` → \`agentive\`
  (task moves, doctor, preflight, evaluator provisioning)
- **Agents/skills/commands**: the \`agentive-workflow\` Claude Code
  plugin (\`claude plugin marketplace add movito/agentive-skills\`,
  then \`claude plugin install agentive-workflow@agentive-skills\`)

First session: open Claude Code here and invoke the \`planner\` agent
in a new tab. Verify the environment first with \`agentive doctor\`.
README_EOF
    else
        cat > "$TARGET/README.md" << README_EOF
# $PROJECT_NAME

Project repository with the agentive workflow installed (task prefix:
\`${PREFIX:-TBD}\`). Besides your project's own code, these folders
carry the workflow — most are dot-folders your file browser may hide:

| Folder | What's in it |
|--------|--------------|
| \`.kit/tasks/\` | Task specs by status (\`1-backlog\` … \`7-blocked\`) |
| \`.kit/context/\` | Handoffs, reviews, workflow reference docs |
| \`.kit/templates/\` | Task and handoff templates |
| \`.adversarial/\` | Evaluation config, inputs, and logs |
| \`docs/adr/\` | Architecture decision records |
| \`scripts/local/\` | This repo's check hook (\`checks.sh\`) |

Tooling is installed, not copied (agentive-kit phase 2):

- **Lifecycle CLI**: \`uv tool install agentive-kit\` → \`agentive\`
  (task moves, doctor, preflight, evaluator provisioning)
- **Agents/skills/commands**: the \`agentive-workflow\` Claude Code
  plugin (\`claude plugin marketplace add movito/agentive-skills\`,
  then \`claude plugin install agentive-workflow@agentive-skills\`)

First session: open Claude Code here and invoke the \`planner\` agent
in a new tab. Verify the environment first with \`agentive doctor\`.
README_EOF
    fi
fi

echo "Content scaffold ready: .kit/ skeleton, docs/adr/, README, adversarial config (pins: CLI + library)"

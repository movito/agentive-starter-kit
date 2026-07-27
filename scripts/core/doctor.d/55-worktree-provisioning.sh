#!/usr/bin/env bash
# shapes: single planning
# doctor check: worktree provisioning correctness (KIT-0071).
#
# Incidents:
#   - KIT-0065: worktrees were provisioned with .venv SYMLINKED to the
#     primary clone; an in-worktree `python3 -m venv --clear` followed
#     the link and EMPTIED THE PRIMARY'S VENV (repaired in-session).
#     The same link is the KIT-0044 stale-venv split-brain in
#     permanent form.
#   - KIT-0069: Serena resolves a project NAME to its REGISTERED path —
#     activate_project("<primary-name>") inside a worktree targets the
#     primary clone, so bulk edits would hit main's checkout (caught
#     pre-use). Worktree sessions activate by ABSOLUTE PATH.
#
# Verdicts (one line per concern; the driver aggregates):
#   worktree-venv    WARN  .venv is a symlink (the destruction vector)
#                    PASS  real venv, or no venv yet
#   worktree-audit   SKIP  outside a linked worktree — the remaining
#                          concerns only exist inside one
#   worktree-serena  WARN  no worktree-local .serena/project.yml, or a
#                          project_name colliding with the primary's
#                    SKIP  the project does not use Serena
#                    PASS  worktree-local config with its own name
#   worktree-shared  PASS  enumerates what a worktree SHARES by design
#
# Read-only (N3), no network. Scratch-dir hygiene (mktemp -d + sweep
# lists) is settled policy recorded in WORKTREE-WORKFLOW.md — this
# check deliberately audits provisioning only and never asks for
# permission-list changes.

set -u

# Leaked GIT_* env would redirect every git call below at the wrong
# repository (the KIT-0043 leak class) — scrub all of it; the driver
# also scrubs, but this check must survive standalone runs.
for _git_var in $(compgen -A variable | grep '^GIT_' || true); do
    unset "$_git_var"
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${DOCTOR_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"

# ── .venv: must never be a symlink, worktree or not ──
if [ -L "$ROOT/.venv" ]; then
    TARGET="$(readlink "$ROOT/.venv")"
    echo "DOCTOR:worktree-venv:WARN:.venv is a symlink -> $TARGET — split-brain (KIT-0044) and a destruction vector: a venv --clear or rebuild through the link empties the TARGET venv (KIT-0065 emptied the primary clone's); replace it: rm .venv && ./scripts/core/project setup"
elif [ -d "$ROOT/.venv" ]; then
    echo "DOCTOR:worktree-venv:PASS:.venv is a real directory (not a symlink)"
else
    echo "DOCTOR:worktree-venv:PASS:no .venv — provision one with ./scripts/core/project setup when needed"
fi

# ── the rest of the audit only applies inside a linked worktree ──
GIT_DIR_PATH="$(git -C "$ROOT" rev-parse --path-format=absolute --git-dir 2>/dev/null)" || GIT_DIR_PATH=""
GIT_COMMON="$(git -C "$ROOT" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" || GIT_COMMON=""
if [ -z "$GIT_DIR_PATH" ] || [ -z "$GIT_COMMON" ]; then
    echo "DOCTOR:worktree-audit:SKIP:not a git checkout — no worktree provisioning to audit"
    exit 0
fi
if [ "$GIT_DIR_PATH" = "$GIT_COMMON" ]; then
    echo "DOCTOR:worktree-audit:SKIP:primary clone (not a linked worktree) — worktree audit not applicable"
    exit 0
fi
PRIMARY_ROOT="$(dirname "$GIT_COMMON")"

# ── Serena: name-based activation resolves to the PRIMARY ──
serena_name() {  # $1 = project.yml path; prints the project_name value
    sed -n 's/^project_name:[[:space:]]*//p' "$1" 2>/dev/null \
        | head -1 | sed "s/[\"']//g"
}
if [ ! -f "$PRIMARY_ROOT/.serena/project.yml" ]; then
    echo "DOCTOR:worktree-serena:SKIP:project does not use Serena (no .serena/project.yml in the primary clone)"
elif [ ! -f "$ROOT/.serena/project.yml" ]; then
    echo "DOCTOR:worktree-serena:WARN:no worktree-local .serena/project.yml — activate_project by NAME resolves to the PRIMARY clone and bulk edits would hit main's checkout (KIT-0069); activate by ABSOLUTE PATH instead: $ROOT"
else
    WT_NAME="$(serena_name "$ROOT/.serena/project.yml")"
    PRIMARY_NAME="$(serena_name "$PRIMARY_ROOT/.serena/project.yml")"
    if [ -n "$WT_NAME" ] && [ "$WT_NAME" = "$PRIMARY_NAME" ]; then
        echo "DOCTOR:worktree-serena:WARN:worktree Serena project_name '$WT_NAME' collides with the primary's — name-based activation is ambiguous and may resolve to the primary (KIT-0069); regenerate with a per-worktree name (scripts/local/new-worktree.sh does this) or activate by ABSOLUTE PATH: $ROOT"
    else
        echo "DOCTOR:worktree-serena:PASS:worktree-local Serena config (project_name '${WT_NAME:-unset}') — activate by absolute path: $ROOT"
    fi
fi

# ── what a worktree DOES share, so nobody re-diagnoses it ──
echo "DOCTOR:worktree-shared:PASS:shared with the primary by design (read-only use): .env, .adversarial/evaluators, git hooks via the common git dir; worktree-local by design: .venv, .serena"
exit 0

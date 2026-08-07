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
#   worktree-venv    WARN  .venv is a symlink (the destruction vector);
#                          also fires for the alternate venv/ layout
#                    PASS  real venv, or no venv yet
#   worktree-audit   SKIP  outside a linked worktree — the remaining
#                          concerns only exist inside one
#   worktree-serena  WARN  no worktree-local .serena/project.yml, an
#                          unnamed one, or a name colliding with the
#                          primary's
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

# Worktree-ness first: the venv remedy differs inside one — hooks are
# SHARED with the primary, so an in-worktree setup must say --no-hooks
# or the reinstall re-points them at a venv that dies with the
# worktree (BugBot, this PR).
# KIT-0080: --path-format=absolute needs git >= 2.31; Apple's system git
# (2.30.1) echoes the flag back as an output line and exits 0, so both
# vars became two-line garbage — they compared unequal, the check claimed
# "in a worktree", and PRIMARY_ROOT resolved through a dirname that
# errored to stderr. Every Serena verdict below was then computed against
# a nonexistent primary (it reported SKIP "project does not use Serena").
# Plain flags are portable; output is relative to the -C directory, so
# absolutize there.
#
# Emptiness-checked BEFORE joining: on failure the substitution is
# empty, which would otherwise resolve to $ROOT — turning "not a repo"
# into a confident wrong answer and defeating the not-a-checkout SKIP
# below. A relative answer is joined by STRING rather than `cd`+`pwd`,
# so a symlinked checkout keeps its logical path (/var -> /private/var
# on macOS); the two vars are only ever compared with each other, so
# both must normalize the same way.
git_path() {  # $1 = rev-parse path flag; prints an absolute path or nothing
    local raw
    raw="$(git -C "$ROOT" rev-parse "$1" 2>/dev/null)" || return 0
    case "$raw" in
        '') return 0 ;;
        /*) printf '%s\n' "$raw" ;;
        *)  printf '%s\n' "$ROOT/$raw" ;;
    esac
}
GIT_DIR_PATH="$(git_path --git-dir)"
GIT_COMMON="$(git_path --git-common-dir)"
IN_WORKTREE=""
if [ -n "$GIT_DIR_PATH" ] && [ -n "$GIT_COMMON" ] \
    && [ "$GIT_DIR_PATH" != "$GIT_COMMON" ]; then
    IN_WORKTREE=1
fi
# SETUP_CMD stays a pure, copy-able command — root-scoped via cd so a
# paste from ANY cwd provisions the diagnosed checkout, never the
# caller's (CodeRabbit round 2). Paths are %q-escaped so quotes,
# spaces, or substitution characters in the path cannot break or
# execute inside the pasted snippet (CodeRabbit round 4). The
# rationale rides in SETUP_NOTE as a SHELL COMMENT, so pasting the
# remedy tail whole stays executable (rounds 2-3).
ROOT_Q="$(printf '%q' "$ROOT")"
VENV_Q="$(printf '%q' "$ROOT/.venv")"
SETUP_CMD="(cd $ROOT_Q && ./scripts/core/project setup)"
SETUP_NOTE=""
if [ -n "$IN_WORKTREE" ]; then
    SETUP_CMD="(cd $ROOT_Q && ./scripts/core/project setup --no-hooks)"
    SETUP_NOTE="  # hooks stay shared with the primary, hence --no-hooks"
fi

# ── .venv: must never be a symlink, worktree or not ──
if [ -L "$ROOT/.venv" ]; then
    TARGET="$(readlink "$ROOT/.venv")"
    echo "DOCTOR:worktree-venv:WARN:.venv is a symlink -> $TARGET — split-brain (KIT-0044) and a destruction vector: a venv --clear or rebuild through the link empties the TARGET venv (KIT-0065 emptied the primary clone's); replace it: rm $VENV_Q && $SETUP_CMD$SETUP_NOTE"
elif [ -d "$ROOT/.venv" ]; then
    echo "DOCTOR:worktree-venv:PASS:.venv is a real directory (not a symlink)"
else
    echo "DOCTOR:worktree-venv:PASS:no .venv — provision one with $SETUP_CMD when needed$SETUP_NOTE"
fi
# The alternate venv/ layout (40-version-skew probes it too) carries
# the same hazard class; silent when absent or a real directory.
if [ -L "$ROOT/venv" ]; then
    echo "DOCTOR:worktree-venv:WARN:venv is a symlink -> $(readlink "$ROOT/venv") — same destruction vector as a symlinked .venv (KIT-0065); replace it with a real venv"
fi

# ── narrow refspec: remote.origin.fetch covering only main (KIT-0091 F5) ──
# Incident (KIT-0090, closure #2): with remote.origin.fetch narrowed to
# main, `git push --force-with-lease` on a feature branch failed with
# "stale info" — the lease compares against the remote-tracking ref,
# which a narrow refspec never updates. The explicit-lease push pattern
# is documented in STACKED-PR-WORKFLOW.md. The config is SHARED via the
# common git dir, so this fires from the primary and every worktree;
# silent when there is no origin remote (nothing to fetch, nothing to
# lease against).
if [ -n "$GIT_DIR_PATH" ]; then
    FETCH_SPECS="$(git -C "$ROOT" config --get-all remote.origin.fetch 2>/dev/null || true)"
    if [ -n "$FETCH_SPECS" ]; then
        if printf '%s\n' "$FETCH_SPECS" | grep -q 'refs/heads/\*'; then
            echo "DOCTOR:worktree-refspec:PASS:remote.origin.fetch covers all branches (refs/heads/*)"
        else
            _RS_ONE_LINE="$(printf '%s' "$FETCH_SPECS" | tr '\n' ' ')"
            echo "DOCTOR:worktree-refspec:WARN:remote.origin.fetch is narrowed ($_RS_ONE_LINE) — remote-tracking refs for other branches never update, so push --force-with-lease fails with 'stale info' (KIT-0090 incident; explicit-lease pattern in STACKED-PR-WORKFLOW.md); widen: git config --add remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*' && git fetch origin"
        fi
    fi
fi

# ── the rest of the audit only applies inside a linked worktree ──
if [ -z "$GIT_DIR_PATH" ] || [ -z "$GIT_COMMON" ]; then
    echo "DOCTOR:worktree-audit:SKIP:not a git checkout — no worktree provisioning to audit"
    exit 0
fi
if [ -z "$IN_WORKTREE" ]; then
    echo "DOCTOR:worktree-audit:SKIP:primary clone (not a linked worktree) — worktree audit not applicable"
    exit 0
fi
PRIMARY_ROOT="$(dirname "$GIT_COMMON")"

# ── Serena: name-based activation resolves to the PRIMARY ──
serena_name() {  # $1 = project.yml path; prints the project name
    # Mirrors the reader in scripts/core/project (reconfigure): accepts
    # top-level `name:` OR `project_name:`, first non-empty value wins,
    # and strips SURROUNDING quotes only — an internal apostrophe is
    # part of the name, not quoting (code-reviewer, this PR).
    local line value
    while IFS= read -r line; do
        case "$line" in
            name:* | project_name:*)
                value="${line#*:}"
                value="$(printf '%s' "$value" \
                    | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
                case "$value" in
                    \"*\") value="${value#\"}"; value="${value%\"}" ;;
                    \'*\') value="${value#\'}"; value="${value%\'}" ;;
                esac
                if [ -n "$value" ]; then
                    printf '%s\n' "$value"
                    return 0
                fi
                ;;
        esac
    done < "$1"
    return 0
}
if [ ! -f "$PRIMARY_ROOT/.serena/project.yml" ]; then
    echo "DOCTOR:worktree-serena:SKIP:project does not use Serena (no .serena/project.yml in the primary clone)"
elif [ ! -f "$ROOT/.serena/project.yml" ]; then
    echo "DOCTOR:worktree-serena:WARN:no worktree-local .serena/project.yml — activate_project by NAME resolves to the PRIMARY clone and bulk edits would hit main's checkout (KIT-0069); activate by ABSOLUTE PATH instead: $ROOT"
else
    WT_NAME="$(serena_name "$ROOT/.serena/project.yml")"
    PRIMARY_NAME="$(serena_name "$PRIMARY_ROOT/.serena/project.yml")"
    if [ -z "$WT_NAME" ]; then
        # An unnamed config is not a collision, but it defeats the
        # per-worktree identity the contract promises (fast-v2, this PR)
        echo "DOCTOR:worktree-serena:WARN:worktree .serena/project.yml has no name/project_name — regenerate it (scripts/local/new-worktree.sh does this) or activate by ABSOLUTE PATH: $ROOT"
    elif [ "$WT_NAME" = "$PRIMARY_NAME" ]; then
        echo "DOCTOR:worktree-serena:WARN:worktree Serena project name '$WT_NAME' collides with the primary's — name-based activation is ambiguous and may resolve to the primary (KIT-0069); regenerate with a per-worktree name (scripts/local/new-worktree.sh does this) or activate by ABSOLUTE PATH: $ROOT"
    else
        echo "DOCTOR:worktree-serena:PASS:worktree-local Serena config (project name '$WT_NAME') — activate by absolute path: $ROOT"
    fi
fi

# ── what a worktree DOES share, so nobody re-diagnoses it ──
echo "DOCTOR:worktree-shared:PASS:shared with the primary by design (read-only use): .env, .adversarial/evaluators, git hooks via the common git dir; worktree-local by design: .venv, .serena"
exit 0

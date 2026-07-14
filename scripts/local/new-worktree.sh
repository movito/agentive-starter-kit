#!/usr/bin/env bash
# Create a fully-provisioned per-task worktree for an implementation session.
#
# Encodes the KIT-0043/KIT-0044 pilot recipe: branch from FRESH origin/main
# (never a possibly-stale local main), then provision the gitignored runtime
# artifacts a session needs. See .kit/context/workflows/WORKTREE-WORKFLOW.md
# for the topology, the pre-commit GIT_DIR contract, and the lifecycle
# (the planner removes the worktree after the task's retro is read).
#
# Usage:
#   ./scripts/local/new-worktree.sh <TASK-ID> [slug]
#
#   TASK-ID   e.g. KIT-0051 — must have a task spec in .kit/tasks/ unless
#             a slug is given explicitly
#   slug      short branch suffix; derived from the task spec filename
#             when omitted (KIT-0051-fix-the-thing.md -> fix-the-thing)
#
# Result:
#   ../ask-worktrees/<TASK-ID>/  on branch feature/<TASK-ID>-<slug>,
#   created from origin/main, with .venv, .env and .adversarial/evaluators
#   symlinked to the primary clone.
#
# Refuses (exit 1) if the worktree path or the branch already exists.

set -euo pipefail

# ─────────────────────────────────────────
# Resolve the PRIMARY clone, not just this script's checkout
# ─────────────────────────────────────────
# The script may be invoked from inside another worktree (its checkout has
# its own copy of scripts/). Symlink sources and the worktree parent dir
# must always resolve to the primary clone, so derive it from the shared
# git common dir instead of the script location.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GIT_COMMON_DIR="$(git -C "$SCRIPT_DIR" rev-parse --path-format=absolute --git-common-dir)"
PRIMARY_ROOT="$(dirname "$GIT_COMMON_DIR")"

# Guard: the dirname math assumes a normal clone (<root>/.git). A bare
# hub (declined in WORKTREE-WORKFLOW.md, but the pilot proved the state
# can occur as damage) would resolve to the wrong directory silently.
if [ ! -e "$PRIMARY_ROOT/.git" ]; then
    echo "Error: could not resolve primary clone root (got: $PRIMARY_ROOT)" >&2
    echo "       Is the primary clone bare? See WORKTREE-WORKFLOW.md." >&2
    exit 1
fi

# Sibling directory holding all task worktrees (pilot convention).
WORKTREES_DIR="$(dirname "$PRIMARY_ROOT")/ask-worktrees"

# ─────────────────────────────────────────
# Provisioning list — explicit and enumerated, never a glob
# ─────────────────────────────────────────
# Gitignored runtime artifacts a session needs, symlinked from the primary.
# Audited against .gitignore 2026-07-14 (KIT-0044). Deliberately absent:
#   .serena/project.yml   — Serena registers by name against the primary
#                           path; a second copy would collide
#   .adversarial/logs/    — regenerates; history is nice-to-have only
#   .dispatch/*, caches   — runtime, regenerate on demand
# Add new entries here by name when a session needs them — never switch
# to "everything gitignored" (evaluator finding, KIT-0044 spec F1.2).
# Each entry must be gitignored WITHOUT a trailing slash: dir-only
# patterns don't match the symlink, which then blocks a plain
# `git worktree remove` at end of life.
PROVISION_LINKS=(
    ".venv"
    ".env"
    ".adversarial/evaluators"
)

# ─────────────────────────────────────────
# Args
# ─────────────────────────────────────────
TASK_ID="${1:-}"
SLUG="${2:-}"

if [ -z "$TASK_ID" ]; then
    echo "Usage: $0 <TASK-ID> [slug]" >&2
    exit 1
fi
if ! printf '%s' "$TASK_ID" | grep -qE '^[A-Za-z]+-[0-9]+$'; then
    echo "Error: TASK-ID must look like PREFIX-NNNN (got: $TASK_ID)" >&2
    exit 1
fi

# Derive the slug from the task spec filename when not given.
if [ -z "$SLUG" ]; then
    # Use nullglob to ensure the loop doesn't run if no files match
    shopt -s nullglob
    matches=()
    for f in "$PRIMARY_ROOT"/.kit/tasks/*/"$TASK_ID"-*.md; do
        if [ -f "$f" ]; then
            matches+=("$f")
        fi
    done
    shopt -u nullglob
    if [ "${#matches[@]}" -eq 0 ]; then
        echo "Error: no task spec found for $TASK_ID in .kit/tasks/ —" >&2
        echo "       pass a slug explicitly: $0 $TASK_ID <slug>" >&2
        exit 1
    fi
    if [ "${#matches[@]}" -gt 1 ]; then
        echo "Error: multiple task specs found for $TASK_ID:" >&2
        printf '       %s\n' "${matches[@]}" >&2
        echo "       Fix the duplicate or pass a slug explicitly." >&2
        exit 1
    fi
    SLUG="$(basename "${matches[0]}")"
    SLUG="${SLUG%.md}"          # strip extension (never .replace)
    SLUG="${SLUG#"$TASK_ID"-}"  # strip the TASK-ID- prefix
fi

BRANCH="feature/$TASK_ID-$SLUG"
WORKTREE_PATH="$WORKTREES_DIR/$TASK_ID"

# ─────────────────────────────────────────
# Refuse on anything that already exists (idempotent-safe, N1)
# ─────────────────────────────────────────
if [ -e "$WORKTREE_PATH" ]; then
    echo "Error: worktree path already exists: $WORKTREE_PATH" >&2
    echo "       Remove it first (planner owns removal, post-retro):" >&2
    echo "       git -C $PRIMARY_ROOT worktree remove $WORKTREE_PATH" >&2
    exit 1
fi
if git -C "$PRIMARY_ROOT" show-ref --verify --quiet "refs/heads/$BRANCH"; then
    echo "Error: branch already exists: $BRANCH" >&2
    echo "       Delete it or pass a different slug." >&2
    exit 1
fi

# ─────────────────────────────────────────
# Pre-flight the provisioning sources BEFORE creating anything
# (temp-then-commit spirit: all fallible checks first, then mutate —
# a missing artifact must refuse cleanly, never leave a half-provisioned
# worktree behind a "Worktree ready" message)
# ─────────────────────────────────────────
for rel in "${PROVISION_LINKS[@]}"; do
    if [ ! -e "$PRIMARY_ROOT/$rel" ]; then
        echo "Error: required artifact missing in primary clone: $rel" >&2
        if [ "$rel" = ".adversarial/evaluators" ]; then
            echo "       Install first: ./scripts/core/project install-evaluators" >&2
        fi
        exit 1
    fi
done

# ─────────────────────────────────────────
# Create: fetch fresh, branch from origin/main (pilot friction #2)
# ─────────────────────────────────────────
echo "Fetching origin..."
git -C "$PRIMARY_ROOT" fetch origin

if ! git -C "$PRIMARY_ROOT" show-ref --verify --quiet "refs/remotes/origin/main"; then
    echo "Error: origin/main does not exist after fetch —" >&2
    echo "       check the remote's default branch." >&2
    exit 1
fi

mkdir -p "$WORKTREES_DIR"
echo "Creating worktree $WORKTREE_PATH on $BRANCH (from origin/main)..."
git -C "$PRIMARY_ROOT" worktree add "$WORKTREE_PATH" -b "$BRANCH" origin/main

# From here on, a failure leaves a half-provisioned worktree; tell the
# operator how to reset rather than deleting anything automatically.
trap 'echo "Provisioning failed — to retry from scratch:" >&2;
      echo "  git -C $PRIMARY_ROOT worktree remove --force $WORKTREE_PATH" >&2;
      echo "  git -C $PRIMARY_ROOT branch -D $BRANCH" >&2' ERR

# ─────────────────────────────────────────
# Provision (pilot friction #3)
# ─────────────────────────────────────────
# Sources were verified up front, so every entry links or the ERR trap
# fires — no silent partial provisioning.
for rel in "${PROVISION_LINKS[@]}"; do
    src="$PRIMARY_ROOT/$rel"
    dst="$WORKTREE_PATH/$rel"
    mkdir -p "$(dirname "$dst")"
    ln -s "$src" "$dst"
    echo "Linked $rel -> $src"
done

trap - ERR

# ─────────────────────────────────────────
# Launch instruction (pilot friction #1 — un-skippable in the starter too)
# ─────────────────────────────────────────
echo ""
echo "✅ Worktree ready: $WORKTREE_PATH (branch: $BRANCH)"
echo ""
echo "⚠️  LAUNCH: open the session tab with its working directory set to"
echo "    $WORKTREE_PATH"
echo "    Running the session from the primary clone costs a cd prefix on"
echo "    every command (measured: ~40 in the KIT-0043 pilot)."

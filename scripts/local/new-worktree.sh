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
#   created from origin/main, with .env and .adversarial/evaluators
#   symlinked to the primary clone, a REAL per-worktree .venv (never a
#   symlink — KIT-0065), and a worktree-local Serena project config.
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
# Symlinks are for READ-ONLY use only. Audited against .gitignore
# 2026-07-14 (KIT-0044). Deliberately absent:
#   .venv                 — MUTABLE state must never be a symlink: an
#                           in-worktree `venv --clear` follows the link
#                           and empties the PRIMARY's venv (KIT-0065).
#                           A real per-worktree venv is provisioned below.
#   .serena/project.yml   — Serena resolves a project NAME to the
#                           REGISTERED path (the primary), so worktrees
#                           get their OWN config with a per-worktree
#                           name, generated below (KIT-0069)
#   .adversarial/logs/    — regenerates; history is nice-to-have only
#   tool caches           — runtime, regenerate on demand
# Add new entries here by name when a session needs them — never switch
# to "everything gitignored" (evaluator finding, KIT-0044 spec F1.2).
# Each entry must be gitignored WITHOUT a trailing slash: dir-only
# patterns don't match the symlink, which then blocks a plain
# `git worktree remove` at end of life.
PROVISION_LINKS=(
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
# Normalize case like `project start` does — task files, branches and
# worktree dirs are always uppercase-ID; the glob below is case-sensitive.
TASK_ID="$(printf '%s' "$TASK_ID" | tr '[:lower:]' '[:upper:]')"

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
    # Guard: if dst already exists as a directory, `ln -s` would drop
    # the link INSIDE it — creating dst/<basename>, and (via an earlier
    # provisioning link) that lands in the PRIMARY as a self-referential
    # symlink (the .adversarial/evaluators/evaluators incident,
    # KIT-0068 A69). Refuse loudly instead.
    if [ -e "$dst" ] || [ -L "$dst" ]; then
        echo "Error: provisioning destination already exists: $dst" >&2
        echo "       Linking over it would nest the symlink inside the" >&2
        echo "       existing directory. Remove it, then re-run." >&2
        # An explicit exit bypasses the ERR trap — repeat its recovery
        # steps so the half-provisioned worktree isn't left unexplained.
        echo "To retry from scratch:" >&2
        echo "  git -C $PRIMARY_ROOT worktree remove --force $WORKTREE_PATH" >&2
        echo "  git -C $PRIMARY_ROOT branch -D $BRANCH" >&2
        exit 1
    fi
    mkdir -p "$(dirname "$dst")"
    ln -s "$src" "$dst"
    echo "Linked $rel -> $src"
done

# ─────────────────────────────────────────
# Serena: worktree-local project config with a per-worktree name
# ─────────────────────────────────────────
# Serena resolves a project NAME to its REGISTERED path — inside a
# worktree, activate_project("<primary-name>") targets the PRIMARY
# clone, so bulk edits would hit main's checkout (KIT-0069, caught
# pre-use). Worktree sessions must activate by ABSOLUTE PATH; a
# pre-generated project.yml with a per-worktree name makes that one
# obvious step. Only generated when the primary actually uses Serena.
# Both project.yml and the generated name are gitignored (root
# .gitignore: .serena/project.yml), so removal stays clean.
if [ -f "$PRIMARY_ROOT/.serena/project.yml" ] \
    && [ -f "$WORKTREE_PATH/.serena/project.yml.template" ]; then
    SERENA_NAME="$(basename "$PRIMARY_ROOT")-$TASK_ID"
    # bash substitution, not sed: a metacharacter in the dirname (&, \)
    # would corrupt a sed replacement string. bash >= 5.2 re-introduces
    # the & hazard via patsub_replacement (on by default) — disable it
    # so SERENA_NAME stays literal; no-op on older bash (BugBot).
    shopt -u patsub_replacement 2>/dev/null || true
    TEMPLATE_CONTENT="$(cat "$WORKTREE_PATH/.serena/project.yml.template")"
    printf '%s\n' "${TEMPLATE_CONTENT//\$\{PROJECT_NAME\}/$SERENA_NAME}" \
        > "$WORKTREE_PATH/.serena/project.yml"
    echo "Serena config generated (project_name: $SERENA_NAME)"
fi

trap - ERR

# ─────────────────────────────────────────
# Per-worktree venv — a REAL venv, never a symlink (KIT-0065)
# ─────────────────────────────────────────
# The pre-KIT-0071 design symlinked .venv to the primary clone; an
# in-worktree `python3 -m venv --clear` followed the link and EMPTIED
# THE PRIMARY'S VENV. It was also the KIT-0044 stale-venv split-brain
# in permanent form. Cost of the real venv: ~1-2 minutes per worktree.
# --no-hooks: git hooks live in the SHARED common git dir and are
# already installed by the primary's setup — reinstalling from here
# would re-point them at a venv that dies with the worktree.
# Failure is non-fatal by design: a network hiccup must not scrap the
# worktree, it just defers venv creation to the session.
echo ""
echo "Provisioning per-worktree venv (real venv, never a symlink)..."
if "$WORKTREE_PATH/scripts/core/project" setup --no-hooks; then
    echo "Venv ready: $WORKTREE_PATH/.venv"
else
    # %q keeps the recovery line paste-safe for paths with spaces or
    # metacharacters — same contract as the doctor/cmd_setup remedies
    WORKTREE_Q="$(printf '%q' "$WORKTREE_PATH")"
    echo "⚠️  venv provisioning failed — the worktree is still usable." >&2
    echo "    Provision it from the session before running tests:" >&2
    echo "    cd $WORKTREE_Q && ./scripts/core/project setup --no-hooks" >&2
fi

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
echo ""
echo "    Serena: activate by ABSOLUTE PATH, never by the primary's name —"
echo "    activate_project(\"$WORKTREE_PATH\")"
echo "    (the name resolves to the PRIMARY clone; bulk edits would hit"
echo "    main's checkout — KIT-0069)."
echo ""
echo "    .venv here is a real per-worktree venv (never a symlink —"
echo "    KIT-0065). Scratch dirs: use mktemp -d and list leftovers for"
echo "    operator sweep; the rm -rf deny is settled policy."

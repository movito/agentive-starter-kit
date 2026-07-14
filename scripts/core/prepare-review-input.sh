#!/bin/bash
# Prepare an adversarial code-review input file for the given task.
# Usage: ./scripts/core/prepare-review-input.sh <TASK-ID> [--base main] [--format diff|full] [--help]
#
# Metadata:
#   version: 1.5.1
#   origin: ixda-services-2.0 (ID2-0015)
#   last-updated: 2026-07-05
#   created-by: "@movito with feature-developer-v6"
#
# Note: unlike sibling scripts (check-bots, verify-ci) this helper does
# no `gh` API calls — it only invokes local `git`. There is therefore no
# `--repo` flag: the target repository's local path is read from the
# `## Target Repository` section of `CLAUDE.md` (or falls back to CWD
# in single-repo mode).
#
# Writes `.adversarial/inputs/<TASK-ID>-code-review-input.md` containing a
# task header plus the code diff (and optionally full file contents) so
# that file-based adversarial evaluators (code-reviewer, code-reviewer-fast,
# claude-code, etc.) can run against cross-repo PRs.
#
# Cross-repo behavior (ID2-0014 / ID2-0015):
#   When `CLAUDE.md` contains a "## Target Repository" section, the diff is
#   read from the configured target repo via `git -C $TARGET_PATH`. In
#   single-repo projects (no target section) the script falls back to the
#   current working-directory repo.
#
# Why file-based input, not `adversarial review`:
#   The built-in `adversarial review` enforces a "you have changed files"
#   guardrail on the current working directory. In the cross-repo pattern
#   the planning repo has no code changes (they live in the target repo),
#   so `adversarial review` fails. File-based evaluators sidestep the
#   guardrail by accepting an explicit input path — this script produces
#   exactly that input.
#
# Why `--format full`:
#   Diff-only input causes model hallucinations on context that isn't in
#   the diff (e.g. a reviewer flagging a symbol as "undefined" because its
#   definition is outside the changed hunks — observed in ID2-0002 retro).
#   `--format full` appends the complete contents of every changed file so
#   the evaluator has full module context.
#
# Lockfile skip (ID2-0047, Q2-2026 retro sweep):
#   Lockfiles (`*.lock`, `*-lock.json`, `*-lock.yaml`) are noisy when
#   appended in full — they're typically tens of thousands of lines of
#   transitive resolution data that bloat the evaluator input without
#   adding signal. We keep their *diff* (so version bumps are visible)
#   but skip the full-content block. A `[lockfile skipped: <path>]` note
#   is emitted in the file's section so reviewers can see the omission
#   was intentional.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# shellcheck disable=SC1091
. "$SCRIPT_DIR/lib/target_repo.sh"

TASK_ID=""
BASE_BRANCH="main"
FORMAT="full"

usage() {
    cat <<'EOF'
Usage: ./scripts/core/prepare-review-input.sh <TASK-ID> [options]

Generates .adversarial/inputs/<TASK-ID>-code-review-input.md from the
current feature branch's diff against a base branch. Used to feed
file-based adversarial evaluators in cross-repo mode.

Arguments:
  <TASK-ID>              Task identifier (e.g. ID2-0015). Used for the
                         output filename and input header.

Options:
  --base <branch>        Base branch to diff against (default: main)
  --format diff|full     Input detail level (default: full)
                           diff — diff only
                           full — diff + full contents of changed files
  --help, -h             Show this help message

Note: there is no --repo flag — this script only runs local `git`,
so the target repo's *path* (from CLAUDE.md ## Target Repository)
is what matters, not its GitHub slug.

Examples:
  # Cross-repo — planning repo CWD, diff read from configured target:
  ./scripts/core/prepare-review-input.sh ID2-0015

  # Single-repo fallback — no target configured, diff from CWD repo:
  ./scripts/core/prepare-review-input.sh ID2-0015

  # Diff against develop instead of main:
  ./scripts/core/prepare-review-input.sh ID2-0015 --base develop

  # Diff only (smaller input, less accurate for large PRs):
  ./scripts/core/prepare-review-input.sh ID2-0015 --format diff

Output:
  .adversarial/inputs/<TASK-ID>-code-review-input.md

Next steps:
  set -a && source .env && set +a
  echo y | adversarial code-reviewer-fast .adversarial/inputs/<TASK-ID>-code-review-input.md
  # 'echo y |' answers the large-input confirm prompt in non-TTY sessions
  # (the installed library has no unattended env flag; upstream #74)
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            usage
            exit 0
            ;;
        --base)
            if [ -z "${2:-}" ] || [[ "$2" == -* ]]; then
                echo "ERROR: --base requires a branch name" >&2
                exit 1
            fi
            BASE_BRANCH="$2"
            shift 2
            ;;
        --base=*)
            BASE_BRANCH="${1#--base=}"
            if [ -z "$BASE_BRANCH" ]; then
                echo "ERROR: --base= requires a branch name" >&2
                exit 1
            fi
            shift
            ;;
        --format)
            if [ -z "${2:-}" ] || [[ "$2" == -* ]]; then
                echo "ERROR: --format requires a value (diff|full)" >&2
                exit 1
            fi
            FORMAT="$2"
            shift 2
            ;;
        --format=*)
            FORMAT="${1#--format=}"
            shift
            ;;
        --repo|--repo=*)
            echo "ERROR: --repo is not supported by this script." >&2
            echo "This helper diffs a local working tree (no gh API calls), so a" >&2
            echo "GitHub slug isn't useful — what matters is the local Path entry" >&2
            echo "under '## Target Repository' in CLAUDE.md. Update CLAUDE.md to" >&2
            echo "point at the desired repo and re-run without --repo." >&2
            exit 1
            ;;
        -*)
            echo "ERROR: Unknown option: $1" >&2
            echo "Run: ./scripts/core/prepare-review-input.sh --help" >&2
            exit 1
            ;;
        *)
            if [ -z "$TASK_ID" ]; then
                TASK_ID="$1"
            else
                echo "ERROR: Unexpected positional argument: $1" >&2
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate TASK-ID
if [ -z "$TASK_ID" ]; then
    echo "ERROR: <TASK-ID> is required" >&2
    echo "Run: ./scripts/core/prepare-review-input.sh --help" >&2
    exit 1
fi
if ! printf '%s' "$TASK_ID" | grep -qE '^[A-Z][A-Z0-9]*-[A-Z0-9]+$'; then
    echo "ERROR: TASK-ID must look like ABC-123 or ABC-TEST, got: '$TASK_ID'" >&2
    exit 1
fi

# Validate --format
case "$FORMAT" in
    diff|full)
        ;;
    *)
        echo "ERROR: --format must be 'diff' or 'full', got: '$FORMAT'" >&2
        exit 1
        ;;
esac

# Apply cross-repo detection from CLAUDE.md.
target_repo_init || exit 1

# Ensure git is available
if ! command -v git >/dev/null 2>&1; then
    echo "ERROR: git not installed" >&2
    exit 1
fi

# Determine diff source: prefer configured target path, fall back to CWD.
#
# GIT_DIR_ARG expands to "-C <path>" in cross-repo mode and "" in
# single-repo mode. It's intentionally left unquoted below so the empty
# case collapses cleanly into a plain `git ...` call.
DIFF_SOURCE_LABEL="$PROJECT_ROOT"
if [ -n "$TARGET_PATH" ]; then
    # target_repo.sh documents (see lib comment block) that TARGET_PATH
    # must not contain whitespace — GIT_DIR_ARG is consumed via word
    # splitting, so a path like "/tmp/My Repo" would silently become
    # three args to git. Reject up-front with a clear error instead of
    # producing confusing `git -C /tmp/My` failures later.
    case "$TARGET_PATH" in
        *[[:space:]]*)
            echo "ERROR: TARGET_PATH '$TARGET_PATH' contains whitespace" >&2
            echo "The cross-repo helper library (scripts/core/lib/target_repo.sh)" >&2
            echo "relies on word-splitting and cannot handle paths with spaces." >&2
            echo "Move the target repo to a whitespace-free path and update CLAUDE.md." >&2
            exit 1
            ;;
    esac
    if [ ! -d "$TARGET_PATH/.git" ] && [ ! -f "$TARGET_PATH/.git" ]; then
        echo "ERROR: TARGET_PATH '$TARGET_PATH' is not a git working tree" >&2
        echo "Fix the '## Target Repository' Path in CLAUDE.md and re-run." >&2
        exit 1
    fi
    DIFF_SOURCE_LABEL="$TARGET_PATH"
fi

# Resolve current branch in the diff source
# shellcheck disable=SC2086
HEAD_BRANCH=$(git $GIT_DIR_ARG branch --show-current 2>/dev/null || echo "")
if [ -z "$HEAD_BRANCH" ]; then
    HEAD_BRANCH="(detached HEAD)"
fi

# Ensure base branch exists in the diff source
# shellcheck disable=SC2086
if ! git $GIT_DIR_ARG rev-parse --verify --quiet "$BASE_BRANCH" >/dev/null; then
    echo "ERROR: base branch '$BASE_BRANCH' not found in $DIFF_SOURCE_LABEL" >&2
    echo "Pass --base <branch> to pick a different base." >&2
    exit 1
fi

# Compute the diff. `A...B` (three dots) diffs B against the merge-base of
# A and B, which is what code review wants — it excludes changes on the
# base branch that happened after the feature branched off.
#
# We let git's stderr through on failure (don't redirect to /dev/null) and
# propagate a non-zero exit — otherwise real failures (corrupt merge-base,
# permission issues) look identical to "no changes committed yet".
# shellcheck disable=SC2086
if ! DIFF_CONTENT=$(git $GIT_DIR_ARG diff "$BASE_BRANCH...HEAD"); then
    echo "ERROR: git diff '$BASE_BRANCH...HEAD' failed in $DIFF_SOURCE_LABEL" >&2
    exit 1
fi
if [ -z "$DIFF_CONTENT" ]; then
    echo "WARNING: No diff between $BASE_BRANCH and HEAD in $DIFF_SOURCE_LABEL" >&2
    echo "Have you committed your changes?" >&2
fi

# List changed files with status (A=added, M=modified, D=deleted, R=renamed).
# shellcheck disable=SC2086
if ! CHANGED_STATUS=$(git $GIT_DIR_ARG diff --name-status "$BASE_BRANCH...HEAD"); then
    echo "ERROR: git diff --name-status '$BASE_BRANCH...HEAD' failed in $DIFF_SOURCE_LABEL" >&2
    exit 1
fi

# Prepare output directory and file
OUTPUT_DIR="$PROJECT_ROOT/.adversarial/inputs"
mkdir -p "$OUTPUT_DIR"
OUTPUT_FILE="$OUTPUT_DIR/${TASK_ID}-code-review-input.md"

# Header
TODAY=$(date +%Y-%m-%d)
{
    echo "# Code Review: $TASK_ID"
    echo
    echo "## Context"
    echo
    echo "- **Task**: $TASK_ID"
    echo "- **Date**: $TODAY"
    echo "- **Diff source**: \`$DIFF_SOURCE_LABEL\`"
    if target_repo_is_set; then
        echo "- **Target repo**: \`$TARGET_REPO\`"
    else
        echo "- **Target repo**: (single-repo / current)"
    fi
    echo "- **Base branch**: \`$BASE_BRANCH\`"
    echo "- **Head branch**: \`$HEAD_BRANCH\`"
    echo "- **Format**: \`$FORMAT\`"
    echo
    echo "> Generated by \`scripts/core/prepare-review-input.sh\`."
    echo "> Replace this block with PR link and bot-review summary before running"
    echo "> deep evaluators — context improves signal."
    echo
    echo "## Changed Files"
    echo
    if [ -n "$CHANGED_STATUS" ]; then
        echo '```'
        # printf '%s\n' is correct for arbitrary strings: `echo` would
        # consume a leading `-e`/`-n` as flags and can mangle backslashes
        # on some shells.
        printf '%s\n' "$CHANGED_STATUS"
        echo '```'
    else
        echo "(no changes detected)"
    fi
    echo
    echo "## Diff"
    echo
    # 4-backtick outer fence so any triple-backtick content inside the
    # diff (e.g. changes to markdown files) can't prematurely close it.
    echo '````diff'
    if [ -n "$DIFF_CONTENT" ]; then
        # Same echo-vs-printf rationale as above; diffs routinely start
        # with `-` so this actually matters here.
        printf '%s\n' "$DIFF_CONTENT"
    fi
    echo '````'
} > "$OUTPUT_FILE"

# For --format full, append full contents of each non-deleted changed file
if [ "$FORMAT" = "full" ] && [ -n "$CHANGED_STATUS" ]; then
    {
        echo
        echo "## Full File Contents"
        echo
        echo "> Complete post-change contents of non-deleted files. Evaluators need"
        echo "> full module context to avoid hallucinating missing imports/exports"
        echo "> that live outside the diff hunks (ID2-0002 retro)."
        echo
    } >> "$OUTPUT_FILE"

    # Read file paths line by line from CHANGED_STATUS.
    # Format: "<status>\t<path>" or "<R|C><score>\t<oldpath>\t<newpath>"
    while IFS=$'\t' read -r status path1 path2; do
        [ -z "$status" ] && continue
        case "$status" in
            D*)
                # Deleted file: skip (no current content)
                continue
                ;;
            R*|C*)
                # Renamed/copied: use new path
                file_path="$path2"
                ;;
            *)
                file_path="$path1"
                ;;
        esac
        [ -z "$file_path" ] && continue

        # Derive filesystem path in the diff source
        if [ -n "$TARGET_PATH" ]; then
            fs_path="$TARGET_PATH/$file_path"
        else
            fs_path="$PROJECT_ROOT/$file_path"
        fi

        # Lockfile skip (ID2-0047): emit the diff but not the full content.
        # See header comment block for rationale.
        # `*.lockb` covers Bun's binary lockfile preemptively — the
        # generic binary-file branch later in the loop would also catch
        # it, but matching here keeps the skip note consistent.
        case "$file_path" in
            *.lock|*.lockb|*-lock.json|*-lock.yaml|*-lock.yml)
                {
                    echo "### Source: \`$file_path\`"
                    echo
                    echo "_[lockfile skipped: $file_path] — diff is included above; full"
                    echo "content omitted to keep evaluator input compact._"
                    echo
                } >> "$OUTPUT_FILE"
                continue
                ;;
        esac

        if [ ! -f "$fs_path" ]; then
            # File is listed as changed but missing from the working tree —
            # likely uncommitted delete or non-standard status. Skip with note.
            {
                echo "### Source: \`$file_path\`"
                echo
                echo "_(file not found on disk at \`$fs_path\` — skipped)_"
                echo
            } >> "$OUTPUT_FILE"
            continue
        fi

        # Handle empty files before binary detection: `grep -Iq .` can't
        # distinguish an empty text file from a binary file (the `.`
        # pattern requires at least one character), so an empty file
        # would otherwise be mislabeled "(binary file, 0 bytes)".
        file_size=$(wc -c < "$fs_path" 2>/dev/null | tr -d ' ')
        if [ "${file_size:-0}" = "0" ]; then
            {
                echo "### Source: \`$file_path\`"
                echo
                echo "_(empty file, 0 bytes — skipped)_"
                echo
            } >> "$OUTPUT_FILE"
            continue
        fi

        # Skip binary files: `cat`-ing them into markdown produces garbled
        # content that bloats the input with no value for the evaluator.
        # `grep -Iq .` is a POSIX-friendly binary detector — the -I flag
        # tells grep to treat a file as a non-match (exit 1) if it looks
        # binary. The `.` pattern matches any non-empty line on text files.
        if ! grep -Iq . "$fs_path" 2>/dev/null; then
            {
                echo "### Source: \`$file_path\`"
                echo
                echo "_(binary file, ${file_size:-?} bytes — skipped)_"
                echo
            } >> "$OUTPUT_FILE"
            continue
        fi

        # Choose a fenced-code language hint from the extension. The
        # evaluator doesn't strictly need it, but it makes the input
        # readable when a human reviews the file.
        case "$file_path" in
            *.js|*.mjs|*.cjs)  lang="javascript" ;;
            *.ts|*.tsx)        lang="typescript" ;;
            *.svelte)          lang="svelte" ;;
            *.py)              lang="python" ;;
            *.sh|*.bash)       lang="bash" ;;
            *.json)            lang="json" ;;
            *.yml|*.yaml)      lang="yaml" ;;
            *.md)              lang="markdown" ;;
            *.css)             lang="css" ;;
            *.html)            lang="html" ;;
            *.groq)            lang="groq" ;;
            *)                 lang="" ;;
        esac

        # Use a 4-backtick outer fence here too — changed files often
        # include markdown or other content with embedded triple
        # backticks, which would otherwise prematurely close the fence.
        # Also emit a bare `echo` after `cat` to guarantee the closing
        # fence lands on its own line even when the source file lacks
        # a trailing newline.
        {
            echo "### Source: \`$file_path\`"
            echo
            echo "\`\`\`\`$lang"
            cat "$fs_path"
            echo
            echo '````'
            echo
        } >> "$OUTPUT_FILE"
    done <<< "$CHANGED_STATUS"
fi

# Summary for the user
CHANGED_COUNT=0
if [ -n "$CHANGED_STATUS" ]; then
    CHANGED_COUNT=$(printf '%s\n' "$CHANGED_STATUS" | wc -l | tr -d ' ')
fi

echo "Wrote: $OUTPUT_FILE"
echo "  Diff source:  $DIFF_SOURCE_LABEL"
echo "  Base:         $BASE_BRANCH"
echo "  Head:         $HEAD_BRANCH"
echo "  Format:       $FORMAT"
echo "  Files changed: $CHANGED_COUNT"
echo
echo "Next steps:"
# In a non-TTY session (agent, CI) the adversarial CLI auto-cancels on
# large (>17k-token) inputs instead of prompting — surface the stdin
# workaround (KIT-0040 retro; corrected in KIT-0044). The previously
# advertised ADVERSARIAL_UNATTENDED env flag does NOT exist in the
# installed library (verified: no match in the package source) — the
# only thing the prompt reads is stdin, so pipe the answer. Either fd
# being non-TTY marks the session non-interactive: stdin is what the
# CLI prompt reads, stdout catches piped/captured agent sessions.
if [ ! -t 0 ] || [ ! -t 1 ]; then
    PIPE_Y="echo y | "
    echo "  # 'echo y |' answers the large-input confirm prompt (no unattended env flag exists; upstream #74)"
else
    PIPE_Y=""
fi
echo "  set -a && source .env && set +a"
echo "  ${PIPE_Y}adversarial code-reviewer-fast $OUTPUT_FILE  # fast gate (~\$0.01)"
echo "  ${PIPE_Y}adversarial code-reviewer $OUTPUT_FILE       # deep (~\$0.33)"
echo "  ${PIPE_Y}adversarial claude-code $OUTPUT_FILE         # security"

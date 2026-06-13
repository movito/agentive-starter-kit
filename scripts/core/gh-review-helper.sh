#!/bin/bash
# GitHub review helper — wraps complex gh api calls for agent autonomy
# Usage: ./scripts/gh-review-helper.sh [--repo owner/name] <subcommand> [args...]
#
# Metadata:
#   version: 1.2.2
#   origin: dispatch-kit
#   origin-version: 0.3.2
#   last-updated: 2026-04-27
#   created-by: "@movito with planner2"
#
# Cross-repo support (ID2-0014):
#   When CLAUDE.md contains a "## Target Repository" section, or when
#   --repo owner/name is passed before the subcommand, all gh api calls
#   target that repo. Single-repo projects are unaffected.
#
# Subcommands:
#   reply    <PR> <COMMENT_ID> "<body>"   Reply to a review comment
#   resolve  <THREAD_NODE_ID>             Resolve a review thread
#   threads  <PR>                          List threads with IDs and status
#   comments <PR>                          List review comments with IDs
#   summary  <PR>                          Thread count summary
#   help                                   Show this help
#
# Exit codes:
#   0 — Success
#   1 — Input validation error
#   2 — API error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# shellcheck disable=SC1091
. "$SCRIPT_DIR/lib/target_repo.sh"

# ─── Usage ──────────────────────────────────────────────────────────
print_usage() {
    echo "Usage: ./scripts/gh-review-helper.sh [--repo owner/name] <subcommand> [args...]"
    echo ""
    echo "Options:"
    echo "  --repo owner/name  Target GitHub repo (overrides CLAUDE.md ## Target Repository)"
    echo ""
    echo "Subcommands:"
    echo "  reply    <PR> <COMMENT_ID> \"<body>\"   Reply to a review comment"
    echo "  resolve  <THREAD_NODE_ID>             Resolve a review thread"
    echo "  threads  <PR>                          List threads with IDs and status"
    echo "  comments <PR>                          List review comments with IDs"
    echo "  summary  <PR>                          Thread count summary"
    echo "  help                                   Show this help"
    echo ""
    echo "Exit codes:"
    echo "  0 — Success"
    echo "  1 — Input validation error"
    echo "  2 — API error"
    echo ""
    echo "Examples:"
    echo "  ./scripts/gh-review-helper.sh summary 53"
    echo "  ./scripts/gh-review-helper.sh --repo movito/ixda-services threads 53"
    echo "  ./scripts/gh-review-helper.sh reply 53 2861292837 'Fixed in abc1234: description.'"
    echo "  ./scripts/gh-review-helper.sh resolve PRRT_kwDORNcO0s5wPovc"
}

# ─── Parse global flags (before subcommand) ────────────────────────
_validate_repo_override() {
    if ! printf '%s' "$1" | grep -qE '^[^/[:space:]]+/[^/[:space:]]+$'; then
        echo "ERROR: --repo must be in owner/name format, got: '$1'" >&2
        exit 1
    fi
}

REPO_OVERRIDE=""
while [ $# -gt 0 ]; do
    case "$1" in
        --repo)
            if [ -z "${2:-}" ] || [[ "$2" == -* ]]; then
                echo "ERROR: --repo requires an owner/name value" >&2
                exit 1
            fi
            REPO_OVERRIDE="$2"
            _validate_repo_override "$REPO_OVERRIDE"
            shift 2
            ;;
        --repo=*)
            REPO_OVERRIDE="${1#--repo=}"
            if [ -z "$REPO_OVERRIDE" ]; then
                echo "ERROR: --repo= requires an owner/name value" >&2
                exit 1
            fi
            _validate_repo_override "$REPO_OVERRIDE"
            shift
            ;;
        *)
            break
            ;;
    esac
done

# ─── Early exit for help (no repo detection needed) ────────────────
# Runs AFTER --repo validation so malformed overrides are rejected even
# when combined with help (e.g., `--repo bad help`).
case "${1:-help}" in
    help|--help|-h) print_usage; exit 0 ;;
esac

# ─── Repo detection ────────────────────────────────────────────────
if [ -n "$REPO_OVERRIDE" ]; then
    target_repo_init --repo "$REPO_OVERRIDE" || exit 1
else
    target_repo_init || exit 1
fi

if target_repo_is_set; then
    REPO="$TARGET_REPO"
else
    REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)
    if [ -z "$REPO" ]; then
        echo "ERROR: Could not determine GitHub repository" >&2
        echo "Run: gh repo set-default" >&2
        exit 2
    fi
fi
OWNER=$(echo "$REPO" | cut -d/ -f1)
NAME=$(echo "$REPO" | cut -d/ -f2)

# ─── Input validation helpers ──────────────────────────────────────
validate_pr() {
    if [ -z "$1" ]; then
        echo "ERROR: PR number is required" >&2
        exit 1
    fi
    if ! echo "$1" | grep -qE '^[0-9]+$'; then
        echo "ERROR: PR number must be a positive integer, got: '$1'" >&2
        exit 1
    fi
}

validate_comment_id() {
    if [ -z "$1" ]; then
        echo "ERROR: Comment ID is required" >&2
        exit 1
    fi
    if ! echo "$1" | grep -qE '^[0-9]+$'; then
        echo "ERROR: Comment ID must be a positive integer, got: '$1'" >&2
        exit 1
    fi
}

validate_thread_id() {
    if [ -z "$1" ]; then
        echo "ERROR: Thread node ID is required" >&2
        exit 1
    fi
    if ! echo "$1" | grep -qE '^PRRT_[A-Za-z0-9_-]+$'; then
        echo "ERROR: Thread ID must match PRRT_*, got: '$1'" >&2
        exit 1
    fi
}

# ─── Error reporting helper ────────────────────────────────────────
# Print a useful error message when a `gh api` query fails. Includes the
# captured stderr verbatim, plus a `--repo` mismatch hint when the
# stderr looks like a "wrong repo" error (Could not resolve, repository
# not found, 404 NOT_FOUND).
#
# Usage:
#   _api_error <pr_or_object> "<stderr_content>" "<context_message>"
_api_error() {
    local subject="$1" stderr_content="$2" context="$3"
    echo "ERROR: $context" >&2
    if [ -n "$stderr_content" ]; then
        # Narrow heuristic: only match repository-resolution failures, not
        # PR/thread-not-found-in-correct-repo errors. The latter would
        # otherwise trigger the misleading "wrong repo" hint when the
        # repo is fine but the PR number is bogus.
        # Patterns covered:
        #   "Could not resolve to a Repository with the name 'foo/bar'"
        #   "repository not found"
        #   "NOT_FOUND ... Repository ..."  (GraphQL error code)
        if echo "$stderr_content" | grep -qiE 'could not resolve to a repository|repository not found|NOT_FOUND.*Repository'; then
            echo "  HINT: gh-review-helper is configured for repo '$REPO'." >&2
            echo "        If '$subject' lives in a different repo, override with --repo <owner/name>." >&2
            echo "        Example: $0 --repo movito/ixda-services-2.0 <subcommand> <args>" >&2
            echo "  gh stderr: $stderr_content" >&2
        else
            echo "  gh stderr: $stderr_content" >&2
        fi
    fi
}

# ─── gh api wrapper ────────────────────────────────────────────────
# Run `gh "$@"` with stderr captured to a temp file. On failure, emit a
# useful error via _api_error and exit 2. On success, the stdout is
# stored in the global _GH_API_OUTPUT (callers `echo "$_GH_API_OUTPUT"`).
#
# Why a global: the helper must be callable directly (not via $()) so
# that `exit 2` exits the script rather than a subshell. Using a global
# keeps each call site to a single statement.
#
# Usage:
#   _run_gh_api <subject> "<context_message>" <gh args...>
#   echo "$_GH_API_OUTPUT"
_GH_API_OUTPUT=""
_run_gh_api() {
    local subject="$1" context="$2"
    shift 2
    local stderr_file rc stderr_content
    if ! stderr_file=$(mktemp); then
        echo "ERROR: Failed to create temp file for gh stderr capture" >&2
        exit 2
    fi
    _GH_API_OUTPUT=$(gh "$@" 2>"$stderr_file")
    rc=$?
    stderr_content=$(cat "$stderr_file")
    rm -f "$stderr_file"
    if [ $rc -ne 0 ]; then
        _api_error "$subject" "$stderr_content" "$context"
        exit 2
    fi
}

# ─── Subcommands ───────────────────────────────────────────────────

cmd_reply() {
    local pr="$1" comment_id="$2" body="$3"
    local output rc
    validate_pr "$pr"
    validate_comment_id "$comment_id"
    if [ -z "$body" ]; then
        echo "ERROR: Reply body cannot be empty" >&2
        exit 1
    fi
    output=$(gh api "repos/$OWNER/$NAME/pulls/$pr/comments/$comment_id/replies" \
        -f body="$body" --jq '.id' 2>/dev/null)
    rc=$?
    if [ $rc -ne 0 ]; then
        echo "ERROR: Failed to post reply (API returned $rc)" >&2
        echo "HINT: If 404, the comment may be on an outdated diff. Use 'resolve' with the GraphQL thread ID instead." >&2
        exit 2
    fi
    echo "$output"
}

cmd_resolve() {
    local thread_id="$1"
    local output rc
    validate_thread_id "$thread_id"
    output=$(gh api graphql \
        -f query="mutation { resolveReviewThread(input: {threadId: \"$thread_id\"}) { thread { isResolved } } }" \
        --jq '.data.resolveReviewThread.thread.isResolved' 2>/dev/null)
    rc=$?
    if [ $rc -ne 0 ]; then
        echo "ERROR: Failed to resolve thread $thread_id" >&2
        exit 2
    fi
    echo "$output"
}

cmd_threads() {
    local pr="$1"
    validate_pr "$pr"
    _run_gh_api "PR #$pr" "Failed to fetch threads for PR #$pr" \
        api graphql \
        -f query="{ repository(owner: \"$OWNER\", name: \"$NAME\") { pullRequest(number: $pr) { reviewThreads(first: 100) { nodes { id isResolved comments(first: 1) { nodes { databaseId author { login } body } } } } } } }" \
        --jq '.data.repository.pullRequest.reviewThreads.nodes[] | "\(.isResolved)\t\(.comments.nodes[0].databaseId)\t\(.comments.nodes[0].author.login // "ghost")\t\(.id)\t\(.comments.nodes[0].body | gsub("[\\n\\t]"; " ") | .[0:120])"'
    echo "$_GH_API_OUTPUT"
}

cmd_comments() {
    local pr="$1"
    validate_pr "$pr"
    _run_gh_api "PR #$pr" "Failed to fetch comments for PR #$pr" \
        api "repos/$OWNER/$NAME/pulls/$pr/comments" --paginate \
        --jq '.[] | "\(.id)\t\(.in_reply_to_id // "root")\t\(.user.login // "ghost")\t\(.path):\(.line // .original_line)\t\(.body | gsub("[\\n\\t]"; " ") | .[0:120])"'
    echo "$_GH_API_OUTPUT"
}

cmd_summary() {
    local pr="$1"
    validate_pr "$pr"
    _run_gh_api "PR #$pr" "Failed to fetch thread summary for PR #$pr" \
        api graphql \
        -f query="{ repository(owner: \"$OWNER\", name: \"$NAME\") { pullRequest(number: $pr) { reviewThreads(first: 100) { nodes { isResolved } } } } }" \
        --jq '[.data.repository.pullRequest.reviewThreads.nodes[].isResolved] | "Total:\(length) Resolved:\([.[] | select(.)] | length) Unresolved:\([.[] | select(. | not)] | length)"'
    echo "$_GH_API_OUTPUT"
}

# ─── Dispatcher ────────────────────────────────────────────────────
case "${1:-help}" in
    reply)    shift; cmd_reply "$@" ;;
    resolve)  shift; cmd_resolve "$@" ;;
    threads)  shift; cmd_threads "$@" ;;
    comments) shift; cmd_comments "$@" ;;
    summary)  shift; cmd_summary "$@" ;;
    *) echo "ERROR: Unknown subcommand: $1" >&2; print_usage >&2; exit 1 ;;
esac

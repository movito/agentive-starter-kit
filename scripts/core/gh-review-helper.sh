#!/bin/bash
# GitHub review helper — wraps complex gh api calls for agent autonomy
# Usage: ./scripts/gh-review-helper.sh <subcommand> [args...]
#
# Metadata:
#   version: 1.0.0
#   origin: dispatch-kit
#   origin-version: 0.3.2
#   last-updated: 2026-02-27
#   created-by: "@movito with planner2"
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

# ─── Usage ──────────────────────────────────────────────────────────
print_usage() {
    echo "Usage: ./scripts/gh-review-helper.sh <subcommand> [args...]"
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
    echo "  ./scripts/gh-review-helper.sh threads 53"
    echo "  ./scripts/gh-review-helper.sh reply 53 2861292837 'Fixed in abc1234: description.'"
    echo "  ./scripts/gh-review-helper.sh resolve PRRT_kwDORNcO0s5wPovc"
}

# ─── Early exit for help (no repo detection needed) ────────────────
case "${1:-help}" in
    help|--help|-h) print_usage; exit 0 ;;
esac

# ─── Repo detection ────────────────────────────────────────────────
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)
if [ -z "$REPO" ]; then
    echo "ERROR: Could not determine GitHub repository" >&2
    echo "Run: gh repo set-default" >&2
    exit 2
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
    local output rc
    validate_pr "$pr"
    output=$(gh api graphql \
        -f query="{ repository(owner: \"$OWNER\", name: \"$NAME\") { pullRequest(number: $pr) { reviewThreads(first: 100) { nodes { id isResolved comments(first: 1) { nodes { databaseId author { login } body } } } } } } }" \
        --jq '.data.repository.pullRequest.reviewThreads.nodes[] | "\(.isResolved)\t\(.comments.nodes[0].databaseId)\t\(.comments.nodes[0].author.login // "ghost")\t\(.id)\t\(.comments.nodes[0].body | gsub("[\\n\\t]"; " ") | .[0:120])"' 2>/dev/null)
    rc=$?
    if [ $rc -ne 0 ]; then
        echo "ERROR: Failed to fetch threads for PR #$pr" >&2
        exit 2
    fi
    echo "$output"
}

cmd_comments() {
    local pr="$1"
    local output rc
    validate_pr "$pr"
    output=$(gh api "repos/$OWNER/$NAME/pulls/$pr/comments" --paginate \
        --jq '.[] | "\(.id)\t\(.in_reply_to_id // "root")\t\(.user.login // "ghost")\t\(.path):\(.line // .original_line)\t\(.body | gsub("[\\n\\t]"; " ") | .[0:120])"' 2>/dev/null)
    rc=$?
    if [ $rc -ne 0 ]; then
        echo "ERROR: Failed to fetch comments for PR #$pr" >&2
        exit 2
    fi
    echo "$output"
}

cmd_summary() {
    local pr="$1"
    local output rc
    validate_pr "$pr"
    output=$(gh api graphql \
        -f query="{ repository(owner: \"$OWNER\", name: \"$NAME\") { pullRequest(number: $pr) { reviewThreads(first: 100) { nodes { isResolved } } } } }" \
        --jq '[.data.repository.pullRequest.reviewThreads.nodes[].isResolved] | "Total:\(length) Resolved:\([.[] | select(.)] | length) Unresolved:\([.[] | select(. | not)] | length)"' 2>/dev/null)
    rc=$?
    if [ $rc -ne 0 ]; then
        echo "ERROR: Failed to fetch thread summary for PR #$pr" >&2
        exit 2
    fi
    echo "$output"
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

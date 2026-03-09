#!/bin/bash
# Check bot review status for the current PR
# Usage: ./scripts/check-bots.sh [PR_NUMBER] [--help]
#
# Metadata:
#   version: 1.0.0
#   origin: dispatch-kit
#   origin-version: 0.3.2
#   last-updated: 2026-02-27
#   created-by: "@movito with planner2"
#
# Reports whether BugBot (cursor[bot]) and CodeRabbit (coderabbitai[bot])
# have posted reviews, and whether those reviews cover the HEAD commit.
#
# Output format (structured for machine parsing):
#   PR_NUMBER:<number>
#   PR_TITLE:<title>
#   PR_URL:<url>
#   HEAD_SHA:<sha>
#   REVIEW_DECISION:<decision>
#   ---
#   REVIEW:<login>:<state>:<commit_sha>:<timestamp>
#   ---
#   THREADS:Total:<n>,Resolved:<n>,Unresolved:<n>
#   ---
#   BOT_STATUS:<name>:CURRENT|STALE|MISSING
#
# Freshness:
#   CURRENT — bot's latest review is on the HEAD commit
#   STALE   — bot posted a review, but on an older commit (re-scan pending)
#   MISSING — bot has not posted any review yet
#
# Exit codes:
#   0 — Both bots have reviewed the HEAD commit
#   1 — One or both bots missing, stale, or error

PR_NUMBER=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "Usage: ./scripts/check-bots.sh [PR_NUMBER]"
            echo ""
            echo "Check bot review status for the current PR."
            echo ""
            echo "Arguments:"
            echo "  PR_NUMBER    PR number to check (default: auto-detect from current branch)"
            echo ""
            echo "Options:"
            echo "  --help, -h   Show this help message"
            echo ""
            echo "Expected bots:"
            echo "  CodeRabbit   coderabbitai[bot]   ~1-2 minutes"
            echo "  BugBot       cursor[bot]         ~4-6 minutes"
            echo ""
            echo "Freshness (per bot):"
            echo "  CURRENT  Bot's latest review covers HEAD commit"
            echo "  STALE    Bot reviewed an older commit (re-scan pending)"
            echo "  MISSING  Bot has not posted any review"
            echo ""
            echo "Exit codes:"
            echo "  0  Both bots have reviewed HEAD commit"
            echo "  1  One or both bots missing, stale, or error"
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            echo "Run: ./scripts/check-bots.sh --help"
            exit 1
            ;;
        *)
            PR_NUMBER="$1"
            shift
            ;;
    esac
done

# Check gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "ERROR:gh CLI (gh) not installed"
    echo "Install: https://cli.github.com/"
    exit 1
fi

# Check gh is authenticated
if ! gh auth status &> /dev/null; then
    echo "ERROR:gh CLI not authenticated"
    echo "Run: gh auth login"
    exit 1
fi

# Detect repo owner/name
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)
if [ -z "$REPO" ]; then
    echo "ERROR:Could not determine GitHub repository"
    echo "Run: gh repo set-default"
    exit 1
fi

OWNER=$(echo "$REPO" | cut -d/ -f1)
NAME=$(echo "$REPO" | cut -d/ -f2)

# Derive task ID from branch for progress event
_EMIT_TASK=$(git branch --show-current 2>/dev/null | sed -n 's|^feature/\([A-Z][A-Z]*-[0-9][0-9]*\).*|\1|p')

# Auto-detect PR number if not provided
if [ -z "$PR_NUMBER" ]; then
    PR_NUMBER=$(gh pr view --json number --jq .number 2>/dev/null || true)
    if [ -z "$PR_NUMBER" ]; then
        echo "ERROR:No PR found for current branch"
        echo "Push your branch and open a PR first."
        exit 1
    fi
fi

# Get PR info (single call: metadata + headRefOid + reviews with commit SHAs)
PR_JSON=$(gh pr view "$PR_NUMBER" --json number,url,title,reviewDecision,headRefOid,reviews 2>/dev/null || true)
if [ -z "$PR_JSON" ]; then
    echo "ERROR:Could not fetch PR #$PR_NUMBER"
    exit 1
fi

PR_TITLE=$(echo "$PR_JSON" | jq -r '.title')
PR_URL=$(echo "$PR_JSON" | jq -r '.url')
HEAD_SHA=$(echo "$PR_JSON" | jq -r '.headRefOid')
REVIEW_DECISION=$(echo "$PR_JSON" | jq -r '.reviewDecision // "NONE"')

echo "PR_NUMBER:$PR_NUMBER"
echo "PR_TITLE:$PR_TITLE"
echo "PR_URL:$PR_URL"
echo "HEAD_SHA:$HEAD_SHA"
echo "REVIEW_DECISION:$REVIEW_DECISION"
echo "---"

# Extract reviews
REVIEWS_JSON=$(echo "$PR_JSON" | jq -c '.reviews[]' 2>/dev/null || true)
if [ -n "$REVIEWS_JSON" ]; then
    echo "$REVIEWS_JSON" | jq -r '"REVIEW:\(.author.login):\(.state):\(.commit.oid // "unknown"):\(.submittedAt)"'
else
    echo "REVIEW:NONE"
fi
echo "---"

# Get thread summary via GraphQL
THREADS_JSON=$(gh api graphql -f query="{ repository(owner: \"$OWNER\", name: \"$NAME\") { pullRequest(number: $PR_NUMBER) { reviewThreads(first: 100) { nodes { isResolved } } } } }" 2>/dev/null || true)

if [ -n "$THREADS_JSON" ]; then
    TOTAL=$(echo "$THREADS_JSON" | jq '[.data.repository.pullRequest.reviewThreads.nodes[]] | length' 2>/dev/null || echo "0")
    RESOLVED=$(echo "$THREADS_JSON" | jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == true)] | length' 2>/dev/null || echo "0")
    UNRESOLVED=$(echo "$THREADS_JSON" | jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)] | length' 2>/dev/null || echo "0")
    echo "THREADS:Total:$TOTAL,Resolved:$RESOLVED,Unresolved:$UNRESOLVED"
else
    echo "THREADS:Total:0,Resolved:0,Unresolved:0"
fi

# Determine bot freshness: CURRENT (reviewed HEAD), STALE (older commit), MISSING
# Each bot's latest review commit is compared against HEAD_SHA.
# gh pr view returns logins without [bot] suffix, so match on base name.
#
# BugBot quirk: when it finds no bugs, it reports as a check run ("Cursor Bugbot")
# instead of posting a review. So we also check check-runs on HEAD for BugBot.

# Fetch check runs on HEAD (used for BugBot fallback)
BUGBOT_CHECK=$(gh api "repos/$OWNER/$NAME/commits/$HEAD_SHA/check-runs" \
    --jq '.check_runs[] | select(.app.slug == "cursor") | "\(.status):\(.conclusion)"' 2>/dev/null || true)

bot_freshness() {
    local bot_login_pattern="$1"
    local check_run_fallback="$2"  # "completed:success" if bot has a passing check run on HEAD

    # Check reviews first
    local latest_commit=""
    if [ -n "$REVIEWS_JSON" ]; then
        latest_commit=$(echo "$REVIEWS_JSON" | jq -r "select(.author.login | test(\"$bot_login_pattern\")) | .commit.oid // \"unknown\"" | tail -1)
    fi

    if [ -n "$latest_commit" ] && [ "$latest_commit" = "$HEAD_SHA" ]; then
        echo "CURRENT"
    elif [ "$check_run_fallback" = "completed:success" ]; then
        # Bot ran on HEAD but posted no review (no findings) — that's CURRENT
        echo "CURRENT"
    elif [ -n "$latest_commit" ]; then
        echo "STALE"
    else
        echo "MISSING"
    fi
}

CODERABBIT_STATUS=$(bot_freshness "coderabbitai" "")
BUGBOT_STATUS=$(bot_freshness "cursor" "$BUGBOT_CHECK")

echo "---"
echo "BOT_STATUS:CodeRabbit:$CODERABBIT_STATUS"
echo "BOT_STATUS:BugBot:$BUGBOT_STATUS"

# Emit progress event (optional, fire-and-forget — requires dispatch-kit)
if command -v dispatch >/dev/null 2>&1; then
    dispatch emit bots_checked --agent check-bots \
        ${_EMIT_TASK:+--task "$_EMIT_TASK"} \
        --summary "CodeRabbit: $CODERABBIT_STATUS, BugBot: $BUGBOT_STATUS (PR #$PR_NUMBER)" \
        >/dev/null 2>&1 || true
fi

if [ "$CODERABBIT_STATUS" = "CURRENT" ] && [ "$BUGBOT_STATUS" = "CURRENT" ]; then
    exit 0
else
    exit 1
fi

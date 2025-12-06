#!/bin/bash
# Check GitHub Actions CI status for a branch
# Usage: ./scripts/verify-ci.sh [branch-name] [--wait]
#
# Options:
#   --wait    Wait for in-progress workflows to complete (default: just report status)
#   --timeout Timeout in seconds for --wait mode (default: 300)

set -e

BRANCH=""
WAIT_MODE=false
TIMEOUT=300

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --wait)
            WAIT_MODE=true
            shift
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            BRANCH="$1"
            shift
            ;;
    esac
done

# Default to current branch if not specified
if [ -z "$BRANCH" ]; then
    BRANCH=$(git branch --show-current 2>/dev/null)
fi

if [ -z "$BRANCH" ]; then
    echo "❌ Could not determine branch"
    echo "Usage: ./scripts/verify-ci.sh [branch-name] [--wait]"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 CI Status Check: $BRANCH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Check gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not installed"
    echo "Install: https://cli.github.com/"
    exit 1
fi

# Check gh is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ GitHub CLI not authenticated"
    echo "Run: gh auth login"
    exit 1
fi

# Check gh is pointing at the right repo
EXPECTED_REPO=$(git remote get-url origin 2>/dev/null | sed 's/.*github.com[:/]//' | sed 's/.git$//')
ACTUAL_REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)

if [ -z "$ACTUAL_REPO" ]; then
    echo "❌ Could not determine GitHub repository"
    echo "Run: gh repo set-default"
    exit 1
fi

if [ "$EXPECTED_REPO" != "$ACTUAL_REPO" ]; then
    echo "⚠️  GitHub CLI default repo mismatch!"
    echo "   Expected: $EXPECTED_REPO"
    echo "   Actual:   $ACTUAL_REPO"
    echo
    echo "Run: gh repo set-default"
    exit 1
fi

echo "Repository: $ACTUAL_REPO"
echo

# Get recent workflow runs (filter to push events only)
RUNS_JSON=$(gh run list --branch "$BRANCH" --limit 10 --json status,conclusion,workflowName,createdAt,headSha,event,databaseId 2>&1)

if [ -z "$RUNS_JSON" ] || [ "$RUNS_JSON" = "[]" ]; then
    echo "⚠️  No CI runs found for branch '$BRANCH'"
    echo
    echo "Possible reasons:"
    echo "  1. Branch hasn't been pushed yet"
    echo "  2. Workflows are configured to ignore this path"
    echo "  3. No workflows defined in .github/workflows/"
    exit 0
fi

# Filter to push events only and get the most recent
PUSH_RUNS=$(echo "$RUNS_JSON" | jq '[.[] | select(.event == "push")] | sort_by(.createdAt) | reverse')
RUN_COUNT=$(echo "$PUSH_RUNS" | jq 'length')

if [ "$RUN_COUNT" -eq 0 ]; then
    echo "⚠️  No push-triggered workflows found for branch '$BRANCH'"
    echo "    (Found workflows triggered by other events)"
    exit 0
fi

echo "Found $RUN_COUNT push-triggered workflow run(s)"
echo

# Process each unique workflow from the most recent push
LATEST_SHA=$(echo "$PUSH_RUNS" | jq -r '.[0].headSha')
LATEST_RUNS=$(echo "$PUSH_RUNS" | jq "[.[] | select(.headSha == \"$LATEST_SHA\")]")

echo "Latest commit: ${LATEST_SHA:0:7}"
echo

# Track overall status
ALL_PASSED=true
ANY_FAILED=false
ANY_IN_PROGRESS=false
WORKFLOW_RESULTS=""

# Check each workflow
while IFS= read -r run; do
    NAME=$(echo "$run" | jq -r '.workflowName')
    STATUS=$(echo "$run" | jq -r '.status')
    CONCLUSION=$(echo "$run" | jq -r '.conclusion')
    RUN_ID=$(echo "$run" | jq -r '.databaseId')

    if [ "$STATUS" = "completed" ]; then
        if [ "$CONCLUSION" = "success" ]; then
            WORKFLOW_RESULTS+="  ✅ $NAME: PASS\n"
        elif [ "$CONCLUSION" = "failure" ]; then
            WORKFLOW_RESULTS+="  ❌ $NAME: FAIL (run: $RUN_ID)\n"
            ANY_FAILED=true
            ALL_PASSED=false
        elif [ "$CONCLUSION" = "cancelled" ]; then
            WORKFLOW_RESULTS+="  ⚠️  $NAME: CANCELLED\n"
            ALL_PASSED=false
        elif [ "$CONCLUSION" = "skipped" ]; then
            WORKFLOW_RESULTS+="  ⏭️  $NAME: SKIPPED\n"
        else
            WORKFLOW_RESULTS+="  ❓ $NAME: $CONCLUSION\n"
            ALL_PASSED=false
        fi
    elif [ "$STATUS" = "in_progress" ] || [ "$STATUS" = "queued" ]; then
        WORKFLOW_RESULTS+="  🔄 $NAME: IN PROGRESS (run: $RUN_ID)\n"
        ANY_IN_PROGRESS=true
        ALL_PASSED=false
    else
        WORKFLOW_RESULTS+="  ❓ $NAME: $STATUS\n"
        ALL_PASSED=false
    fi
done < <(echo "$LATEST_RUNS" | jq -c '.[]')

# Handle in-progress workflows
if [ "$ANY_IN_PROGRESS" = true ]; then
    if [ "$WAIT_MODE" = true ]; then
        echo "Workflows in progress, waiting (timeout: ${TIMEOUT}s)..."
        echo

        # Get the first in-progress run ID
        IN_PROGRESS_ID=$(echo "$LATEST_RUNS" | jq -r '[.[] | select(.status == "in_progress" or .status == "queued")][0].databaseId')

        if gh run watch "$IN_PROGRESS_ID" --exit-status 2>/dev/null; then
            # Re-check status after waiting
            exec "$0" "$BRANCH"
        else
            echo
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "❌ CI Status: FAIL"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo
            echo "Workflow failed. View details:"
            echo "  gh run view $IN_PROGRESS_ID --log-failed"
            exit 1
        fi
    else
        echo "Workflows:"
        echo -e "$WORKFLOW_RESULTS"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "⏳ CI Status: IN PROGRESS"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo
        echo "To wait for completion:"
        echo "  ./scripts/verify-ci.sh $BRANCH --wait"
        exit 0
    fi
fi

# Report final status
echo "Workflows:"
echo -e "$WORKFLOW_RESULTS"

if [ "$ANY_FAILED" = true ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ CI Status: FAIL"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "View failure details:"
    FAILED_ID=$(echo "$LATEST_RUNS" | jq -r '[.[] | select(.conclusion == "failure")][0].databaseId')
    echo "  gh run view $FAILED_ID --log-failed"
    exit 1
elif [ "$ALL_PASSED" = true ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ CI Status: PASS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "All workflows passed. Safe to proceed."
    exit 0
else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  CI Status: MIXED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "Some workflows did not pass. Review above."
    exit 0
fi

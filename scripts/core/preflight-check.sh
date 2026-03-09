#!/bin/bash
# Run all 7 preflight gates for a PR
# Usage: ./scripts/preflight-check.sh [--pr PR_NUMBER] [--task TASK_ID] [--help]
#
# Metadata:
#   version: 1.0.0
#   origin: dispatch-kit
#   origin-version: 0.3.2
#   last-updated: 2026-02-27
#   created-by: "@movito with planner2"
#
# Output format (structured for machine parsing):
#   GATE:<number>:<name>:PASS|FAIL:<detail>
#
# Exit codes:
#   0 — All gates pass
#   1 — One or more gates fail, or error

PR_NUMBER=""
TASK_ID=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "Usage: ./scripts/preflight-check.sh [--pr PR_NUMBER] [--task TASK_ID]"
            echo ""
            echo "Run all 7 preflight gates for a PR before human review."
            echo ""
            echo "Options:"
            echo "  --pr PR_NUMBER     PR number to check (default: auto-detect)"
            echo "  --task TASK_ID     Task ID, e.g. TASK-0001 (default: derived from branch)"
            echo "  --help, -h         Show this help message"
            echo ""
            echo "Gates:"
            echo "  1. CI green                    GitHub Actions passing"
            echo "  2. CodeRabbit reviewed          coderabbitai[bot] reviewed latest code commit"
            echo "  3. BugBot reviewed              cursor[bot] reviewed latest code commit"
            echo "  4. Zero unresolved threads      All review threads resolved"
            echo "  5. Evaluator review persisted   .agent-context/reviews/<TASK>-evaluator-review*.md"
            echo "  6. Review starter exists         .agent-context/<TASK>-REVIEW-STARTER.md"
            echo "  7. Task in correct folder        delegation/tasks/3-in-progress or 4-in-review"
            echo ""
            echo "Exit codes:"
            echo "  0  All gates pass"
            echo "  1  One or more gates fail"
            exit 0
            ;;
        --pr)
            if [ -z "${2:-}" ] || [[ "$2" == -* ]]; then
                echo "ERROR:--pr requires a PR number"
                exit 1
            fi
            PR_NUMBER="$2"
            shift 2
            ;;
        --task)
            if [ -z "${2:-}" ] || [[ "$2" == -* ]]; then
                echo "ERROR:--task requires a task ID"
                exit 1
            fi
            TASK_ID="$2"
            shift 2
            ;;
        -*)
            echo "Unknown option: $1"
            echo "Run: ./scripts/preflight-check.sh --help"
            exit 1
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Run: ./scripts/preflight-check.sh --help"
            exit 1
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

# Detect branch
BRANCH=$(git branch --show-current 2>/dev/null)
if [ -z "$BRANCH" ]; then
    echo "ERROR:Could not determine current branch"
    exit 1
fi

# Derive task ID from branch if not provided
if [ -z "$TASK_ID" ]; then
    TASK_ID=$(echo "$BRANCH" | sed -n 's|^feature/\([A-Z][A-Z]*-[0-9][0-9]*\).*|\1|p')
    if [ -z "$TASK_ID" ]; then
        echo "ERROR:Could not derive task ID from branch '$BRANCH'"
        echo "Use --task TASK_ID to specify manually."
        exit 1
    fi
fi

# Auto-detect PR number if not provided
if [ -z "$PR_NUMBER" ]; then
    PR_NUMBER=$(gh pr view --json number --jq .number 2>/dev/null || true)
    if [ -z "$PR_NUMBER" ]; then
        echo "ERROR:No PR found for branch '$BRANCH'"
        echo "Push your branch and open a PR first, or use --pr PR_NUMBER."
        exit 1
    fi
fi

# Get PR head SHA for review checks
LATEST_SHA=$(gh pr view "$PR_NUMBER" --json headRefOid --jq .headRefOid 2>/dev/null || true)
if [ -z "$LATEST_SHA" ]; then
    echo "ERROR:Could not fetch PR #$PR_NUMBER head SHA"
    exit 1
fi

ANY_FAILED=false

# ─── Determine latest code commit for bot review checks ───────────
# Bots don't re-review markdown-only pushes. Find the latest commit
# that touched non-markdown, non-planner files so Gates 2-3 check
# the right SHA. Gate 1 (CI) still checks LATEST_SHA (HEAD).

# Verify origin/main is available for the commit range query
if ! git rev-parse --verify origin/main &>/dev/null; then
    echo "ERROR:origin/main not found. Run: git fetch origin main"
    exit 1
fi

CODE_SHA=$(git log --diff-filter=ACDMR --format=%H "origin/main..HEAD" -- \
    ':!*.md' ':!.agent-context/' ':!delegation/' 2>/dev/null | head -1 || true)

NO_CODE_CHANGES=false
if [ -z "$CODE_SHA" ]; then
    # No code changes on this branch — Gates 2-3 will auto-pass
    NO_CODE_CHANGES=true
fi

# ─── Gate 1: CI green ───────────────────────────────────────────────
# Check all workflow runs for the latest commit (not just the first),
# so a passing run from one workflow can't mask a failure in another.

CI_RUNS=$(gh run list --branch "$BRANCH" --limit 10 --json status,conclusion,workflowName,event,headSha \
    --jq '[.[] | select(.event == "push" or .event == "pull_request")]' 2>/dev/null || true)

if [ -z "$CI_RUNS" ] || [ "$CI_RUNS" = "[]" ]; then
    echo "GATE:1:CI:FAIL:No CI runs found"
    ANY_FAILED=true
else
    # Filter runs to the PR head commit (not just the newest run's SHA)
    LATEST_RUNS=$(echo "$CI_RUNS" | jq -c "[.[] | select(.headSha == \"$LATEST_SHA\")]" 2>/dev/null || true)
    RUN_COUNT=$(echo "$LATEST_RUNS" | jq 'length' 2>/dev/null || echo "0")

    if [ "$RUN_COUNT" -eq 0 ]; then
        echo "GATE:1:CI:FAIL:No CI runs found for latest commit"
        ANY_FAILED=true
    else

    CI_ALL_PASS=true
    CI_ANY_RUNNING=false
    CI_DETAILS=""

    for i in $(seq 0 $((RUN_COUNT - 1))); do
        WF_NAME=$(echo "$LATEST_RUNS" | jq -r ".[$i].workflowName")
        WF_STATUS=$(echo "$LATEST_RUNS" | jq -r ".[$i].status")
        WF_CONCLUSION=$(echo "$LATEST_RUNS" | jq -r ".[$i].conclusion")

        if [ "$WF_STATUS" = "completed" ] && [ "$WF_CONCLUSION" = "success" ]; then
            CI_DETAILS="${CI_DETAILS}${WF_NAME}: pass; "
        elif [ "$WF_STATUS" = "in_progress" ] || [ "$WF_STATUS" = "queued" ]; then
            CI_DETAILS="${CI_DETAILS}${WF_NAME}: running; "
            CI_ALL_PASS=false
            CI_ANY_RUNNING=true
        else
            CI_DETAILS="${CI_DETAILS}${WF_NAME}: ${WF_CONCLUSION:-$WF_STATUS}; "
            CI_ALL_PASS=false
        fi
    done

    # Trim trailing "; "
    CI_DETAILS="${CI_DETAILS%; }"

    if [ "$CI_ALL_PASS" = true ]; then
        echo "GATE:1:CI:PASS:$CI_DETAILS"
    elif [ "$CI_ANY_RUNNING" = true ]; then
        echo "GATE:1:CI:FAIL:$CI_DETAILS (still running)"
        ANY_FAILED=true
    else
        echo "GATE:1:CI:FAIL:$CI_DETAILS"
        ANY_FAILED=true
    fi

    fi # RUN_COUNT guard
fi

# ─── Gate 2: CodeRabbit reviewed the PR ──────────────────────────────
# Accepts review on CODE_SHA or LATEST_SHA (bots re-trigger on each push,
# so a review on HEAD covers all prior code even if the latest commit is
# a non-code chore push like review artifacts).
# Auto-passes for pure docs PRs (no code changes to review).

if [ "$NO_CODE_CHANGES" = true ]; then
    echo "GATE:2:CodeRabbit:PASS:No code changes — bot review not required"
else
    CR_REVIEW=$(gh api graphql -f query="{ repository(owner: \"$OWNER\", name: \"$NAME\") { pullRequest(number: $PR_NUMBER) { reviews(last: 20) { nodes { author { login } state commit { oid } } } } } }" \
        --jq ".data.repository.pullRequest.reviews.nodes[] | select(.commit.oid == \"$CODE_SHA\" or .commit.oid == \"$LATEST_SHA\") | select(.author.login | test(\"coderabbitai\")) | \"\(.author.login): \(.state)\"" 2>/dev/null | tail -1 || true)

    if [ -n "$CR_REVIEW" ]; then
        MATCH_SHA="$CODE_SHA"
        if echo "$CR_REVIEW" | grep -q "$LATEST_SHA" 2>/dev/null; then MATCH_SHA="$LATEST_SHA"; fi
        echo "GATE:2:CodeRabbit:PASS:$CR_REVIEW (on ${MATCH_SHA:0:7})"
    else
        echo "GATE:2:CodeRabbit:FAIL:No review from coderabbitai[bot] on ${CODE_SHA:0:7} or ${LATEST_SHA:0:7}"
        ANY_FAILED=true
    fi
fi

# ─── Gate 3: BugBot reviewed the PR ──────────────────────────────────
# BugBot quirk: when it finds no bugs, it reports as a check run
# ("Cursor Bugbot") instead of posting a review. Check both.
# Accepts review/check-run on CODE_SHA or LATEST_SHA.

if [ "$NO_CODE_CHANGES" = true ]; then
    echo "GATE:3:BugBot:PASS:No code changes — bot review not required"
else
    BB_REVIEW=$(gh api graphql -f query="{ repository(owner: \"$OWNER\", name: \"$NAME\") { pullRequest(number: $PR_NUMBER) { reviews(last: 20) { nodes { author { login } state commit { oid } } } } } }" \
        --jq ".data.repository.pullRequest.reviews.nodes[] | select(.commit.oid == \"$CODE_SHA\" or .commit.oid == \"$LATEST_SHA\") | select(.author.login | test(\"cursor\")) | \"\(.author.login): \(.state)\"" 2>/dev/null | tail -1 || true)

    if [ -n "$BB_REVIEW" ]; then
        echo "GATE:3:BugBot:PASS:$BB_REVIEW (on PR #$PR_NUMBER)"
    else
        # Fallback: check for BugBot check-run on CODE_SHA or LATEST_SHA (no-findings case)
        BB_CHECK=$(gh api "repos/$OWNER/$NAME/commits/$CODE_SHA/check-runs" \
            --jq '.check_runs[] | select(.app.slug == "cursor") | "\(.status):\(.conclusion)"' 2>/dev/null || true)

        if [ -z "$BB_CHECK" ] && [ "$CODE_SHA" != "$LATEST_SHA" ]; then
            BB_CHECK=$(gh api "repos/$OWNER/$NAME/commits/$LATEST_SHA/check-runs" \
                --jq '.check_runs[] | select(.app.slug == "cursor") | "\(.status):\(.conclusion)"' 2>/dev/null || true)
        fi

        if [ "$BB_CHECK" = "completed:success" ] || [ "$BB_CHECK" = "completed:neutral" ]; then
            echo "GATE:3:BugBot:PASS:check-run passed, no findings (on PR #$PR_NUMBER)"
        elif [ -n "$BB_CHECK" ]; then
            echo "GATE:3:BugBot:FAIL:check-run $BB_CHECK"
            ANY_FAILED=true
        else
            echo "GATE:3:BugBot:FAIL:No review or check-run from BugBot on ${CODE_SHA:0:7} or ${LATEST_SHA:0:7}"
            ANY_FAILED=true
        fi
    fi
fi

# ─── Gate 4: Zero unresolved threads ────────────────────────────────

THREADS_JSON=$(gh api graphql -f query="{ repository(owner: \"$OWNER\", name: \"$NAME\") { pullRequest(number: $PR_NUMBER) { reviewThreads(first: 100) { nodes { isResolved } } } } }" 2>/dev/null || true)

if [ -n "$THREADS_JSON" ]; then
    TOTAL=$(echo "$THREADS_JSON" | jq '[.data.repository.pullRequest.reviewThreads.nodes[]] | length' 2>/dev/null || echo "")
    RESOLVED=$(echo "$THREADS_JSON" | jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == true)] | length' 2>/dev/null || echo "")
    UNRESOLVED=$(echo "$THREADS_JSON" | jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)] | length' 2>/dev/null || echo "")

    if [ -z "$TOTAL" ] || [ -z "$UNRESOLVED" ]; then
        echo "GATE:4:Threads:FAIL:Could not parse thread data"
        ANY_FAILED=true
    elif [ "$UNRESOLVED" -eq 0 ]; then
        echo "GATE:4:Threads:PASS:Total: $TOTAL, Resolved: $RESOLVED, Unresolved: $UNRESOLVED"
    else
        echo "GATE:4:Threads:FAIL:Total: $TOTAL, Resolved: $RESOLVED, Unresolved: $UNRESOLVED"
        ANY_FAILED=true
    fi
else
    echo "GATE:4:Threads:FAIL:Could not fetch thread data"
    ANY_FAILED=true
fi

# ─── Gate 5: Evaluator review persisted ─────────────────────────────

EVAL_FILE=$(find .agent-context/reviews -name "${TASK_ID}-evaluator-review*.md" 2>/dev/null | head -1 || true)

if [ -n "$EVAL_FILE" ]; then
    echo "GATE:5:Evaluator:PASS:$EVAL_FILE"
else
    echo "GATE:5:Evaluator:FAIL:No evaluator review found for $TASK_ID"
    ANY_FAILED=true
fi

# ─── Gate 6: Review starter exists ──────────────────────────────────

STARTER_FILE=$(find .agent-context -maxdepth 1 -name "${TASK_ID}-REVIEW-STARTER.md" 2>/dev/null | head -1 || true)

if [ -n "$STARTER_FILE" ]; then
    echo "GATE:6:ReviewStarter:PASS:$STARTER_FILE"
else
    echo "GATE:6:ReviewStarter:FAIL:No review starter found for $TASK_ID"
    ANY_FAILED=true
fi

# ─── Gate 7: Task in correct folder ─────────────────────────────────

TASK_FILE=$(find delegation/tasks/3-in-progress delegation/tasks/4-in-review -name "${TASK_ID}*" 2>/dev/null | head -1 || true)

if [ -n "$TASK_FILE" ]; then
    echo "GATE:7:TaskFolder:PASS:$TASK_FILE"
else
    echo "GATE:7:TaskFolder:FAIL:$TASK_ID not in 3-in-progress or 4-in-review"
    ANY_FAILED=true
fi

# ─── Final verdict ──────────────────────────────────────────────────

# Emit progress event (optional, fire-and-forget — requires dispatch-kit)
if command -v dispatch >/dev/null 2>&1; then
    if [ "$ANY_FAILED" = true ]; then
        _PF_SUMMARY="FAIL ($TASK_ID, PR #$PR_NUMBER)"
    else
        _PF_SUMMARY="PASS — All 7 gates passed ($TASK_ID, PR #$PR_NUMBER)"
    fi
    dispatch emit preflight_checked --agent preflight-check \
        --task "$TASK_ID" \
        --summary "$_PF_SUMMARY" >/dev/null 2>&1 || true
fi

if [ "$ANY_FAILED" = true ]; then
    exit 1
else
    exit 0
fi

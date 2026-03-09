#!/bin/bash
# Wait for BugBot and CodeRabbit to review the current PR
# Usage: ./scripts/wait-for-bots.sh [PR_NUMBER] [--interval SECONDS] [--timeout SECONDS]
#
# Metadata:
#   version: 1.0.0
#   origin: dispatch-kit
#   origin-version: 0.3.2
#   last-updated: 2026-02-27
#   created-by: "@movito with planner2"
#
# Polls check-bots.sh repeatedly until both bots report CURRENT on HEAD,
# or timeout is reached.
#
# Progress lines go to stderr; full check-bots.sh output goes to stdout
# on success.
#
# Exit codes:
#   0 — Both bots reviewed HEAD commit
#   1 — Timeout or error

INTERVAL=30
TIMEOUT=900
PR_ARG=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "Usage: ./scripts/wait-for-bots.sh [PR_NUMBER] [--interval SECONDS] [--timeout SECONDS]"
            echo ""
            echo "Wait for both CodeRabbit and BugBot to review the current PR."
            echo "Polls check-bots.sh in a loop until both bots report CURRENT,"
            echo "or timeout is reached."
            echo ""
            echo "Arguments:"
            echo "  PR_NUMBER          PR number to check (default: auto-detect)"
            echo ""
            echo "Options:"
            echo "  --interval SECONDS  Poll interval in seconds (default: 30)"
            echo "  --timeout SECONDS   Max wait time in seconds (default: 900)"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Exit codes:"
            echo "  0  Both bots have reviewed HEAD commit"
            echo "  1  Timeout or error"
            echo ""
            echo "Examples:"
            echo "  ./scripts/wait-for-bots.sh              # Auto-detect PR, defaults"
            echo "  ./scripts/wait-for-bots.sh 42            # Specific PR"
            echo "  ./scripts/wait-for-bots.sh --interval 15 # Poll every 15s"
            echo "  ./scripts/wait-for-bots.sh --timeout 300 # 5-minute timeout"
            exit 0
            ;;
        --interval)
            if [[ -z "${2:-}" || ! "${2}" =~ ^[1-9][0-9]*$ ]]; then
                echo "Invalid --interval value: '${2:-}' (must be a positive integer)" >&2
                exit 1
            fi
            INTERVAL="$2"
            shift 2
            ;;
        --timeout)
            if [[ -z "${2:-}" || ! "${2}" =~ ^[1-9][0-9]*$ ]]; then
                echo "Invalid --timeout value: '${2:-}' (must be a positive integer)" >&2
                exit 1
            fi
            TIMEOUT="$2"
            shift 2
            ;;
        -*)
            echo "Unknown option: $1" >&2
            echo "Run: ./scripts/wait-for-bots.sh --help" >&2
            exit 1
            ;;
        *)
            if [[ ! "$1" =~ ^[1-9][0-9]*$ ]]; then
                echo "Invalid PR number: $1 (must be a positive integer)" >&2
                exit 1
            fi
            PR_ARG="$1"
            shift
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ELAPSED=0
POLL_COUNT=0

# Derive task ID from branch for progress event
_EMIT_TASK=$(git branch --show-current 2>/dev/null | sed -n 's|^feature/\([A-Z][A-Z]*-[0-9][0-9]*\).*|\1|p')

# Derive PR number for summary (use PR_ARG or auto-detect)
_PR_LABEL=""
if [ -n "$PR_ARG" ]; then
    _PR_LABEL="PR #$PR_ARG"
else
    _AUTO_PR=$(gh pr view --json number --jq .number 2>/dev/null || true)
    if [ -n "$_AUTO_PR" ]; then
        _PR_LABEL="PR #$_AUTO_PR"
    fi
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
echo "🤖 Waiting for bot reviews${_PR_LABEL:+ ($_PR_LABEL)}" >&2
echo "   Interval: ${INTERVAL}s | Timeout: ${TIMEOUT}s" >&2
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
echo >&2

while [ "$ELAPSED" -lt "$TIMEOUT" ]; do
    POLL_COUNT=$((POLL_COUNT + 1))

    # Run check-bots.sh, capture output
    CHECK_ARGS=()
    [[ -n "$PR_ARG" ]] && CHECK_ARGS+=("$PR_ARG")
    OUTPUT=$("$SCRIPT_DIR/check-bots.sh" "${CHECK_ARGS[@]}" 2>&1)
    EXIT_CODE=$?

    # Parse BOT_STATUS lines
    CR_STATUS=$(echo "$OUTPUT" | grep '^BOT_STATUS:CodeRabbit:' | cut -d: -f3)
    BB_STATUS=$(echo "$OUTPUT" | grep '^BOT_STATUS:BugBot:' | cut -d: -f3)

    # Format elapsed time
    MINS=$((ELAPSED / 60))
    SECS=$((ELAPSED % 60))

    if [ "$EXIT_CODE" -eq 0 ] && [ "$CR_STATUS" = "CURRENT" ] && [ "$BB_STATUS" = "CURRENT" ]; then
        # Both CURRENT — print success to stderr, full output to stdout
        echo "✅ Both bots ready after ${MINS}m ${SECS}s ($POLL_COUNT polls)" >&2
        echo "$OUTPUT"

        # Emit progress event (optional, fire-and-forget — requires dispatch-kit)
        if command -v dispatch >/dev/null 2>&1; then
            dispatch emit bots_waited --agent wait-for-bots \
                ${_EMIT_TASK:+--task "$_EMIT_TASK"} \
                --summary "READY after ${MINS}m ${SECS}s ($POLL_COUNT polls) — CodeRabbit: CURRENT, BugBot: CURRENT${_PR_LABEL:+ ($_PR_LABEL)}" \
                >/dev/null 2>&1 || true
        fi
        exit 0
    fi

    # Print progress line to stderr
    echo "⏳ Poll $POLL_COUNT (${MINS}m ${SECS}s) — CodeRabbit: ${CR_STATUS:-?}, BugBot: ${BB_STATUS:-?}" >&2

    sleep "$INTERVAL"
    ELAPSED=$((ELAPSED + INTERVAL))
done

# Timeout — format final elapsed time
MINS=$((ELAPSED / 60))
SECS=$((ELAPSED % 60))
echo "❌ Timeout after ${MINS}m ${SECS}s ($POLL_COUNT polls) — CodeRabbit: ${CR_STATUS:-?}, BugBot: ${BB_STATUS:-?}" >&2

# Emit progress event (optional, fire-and-forget — requires dispatch-kit)
if command -v dispatch >/dev/null 2>&1; then
    dispatch emit bots_waited --agent wait-for-bots \
        ${_EMIT_TASK:+--task "$_EMIT_TASK"} \
        --summary "TIMEOUT after ${MINS}m ${SECS}s ($POLL_COUNT polls) — CodeRabbit: ${CR_STATUS:-?}, BugBot: ${BB_STATUS:-?}${_PR_LABEL:+ ($_PR_LABEL)}" \
        >/dev/null 2>&1 || true
fi
exit 1

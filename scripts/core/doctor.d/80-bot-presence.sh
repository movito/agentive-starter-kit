#!/usr/bin/env bash
# doctor check: review bots present on the repo — WARN-max by design.
#
# Incidents: CodeRabbit "internal error" ×3 rounds (prepaid credits
# exhausted, KIT-0042) and bot no-shows that stall the Phase 6 loop.
# Detection is inherently unreliable pre-PR, so this check NEVER emits
# FAIL — WARN is its ceiling.
#
# Not-checkable note (per the incident-closure lifecycle rule): the
# CodeRabbit *quota/credit* state has no cheap API — exhaustion still
# surfaces only as an "internal error" review comment at review time.
# Signals used instead: CodeRabbit reports via commit STATUSES,
# BugBot via CHECK-RUNS (verified in KIT-0034) — both visible in the
# statusCheckRollup of any recent PR.
#
# Read-only; network via gh (the optional bot probe allowed by N2).

set -u

if ! command -v gh >/dev/null 2>&1; then
    echo "DOCTOR:bot-presence:SKIP:gh unavailable — cannot probe bot activity"
    exit 0
fi

PR_JSON="$(gh pr list --state all --limit 1 --json number 2>/dev/null)" || {
    echo "DOCTOR:bot-presence:SKIP:cannot list PRs (unauthenticated or no remote)"
    exit 0
}

PR_NUM="$(printf '%s' "$PR_JSON" | grep -oE '"number": *[0-9]+' | grep -oE '[0-9]+' | head -1)"
if [ -z "$PR_NUM" ]; then
    echo "DOCTOR:bot-presence:SKIP:no PRs yet — bot presence unknowable pre-PR"
    exit 0
fi

ROLLUP="$(gh pr view "$PR_NUM" --json statusCheckRollup 2>/dev/null)" || {
    echo "DOCTOR:bot-presence:SKIP:cannot read PR #$PR_NUM status rollup"
    exit 0
}

MISSING=""
printf '%s' "$ROLLUP" | grep -qi 'coderabbit' || MISSING="CodeRabbit"
if ! printf '%s' "$ROLLUP" | grep -qiE 'bugbot|cursor'; then
    MISSING="${MISSING:+$MISSING, }BugBot"
fi

if [ -z "$MISSING" ]; then
    echo "DOCTOR:bot-presence:PASS:CodeRabbit and BugBot both active on PR #$PR_NUM"
else
    echo "DOCTOR:bot-presence:WARN:no recent activity from: $MISSING (checked PR #$PR_NUM) — quota/credit state is not cheaply checkable"
fi

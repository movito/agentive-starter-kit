#!/usr/bin/env bash
# doctor check: push-sync secrets exist — only while the push trigger
# is active in sync-core-scripts.yml.
#
# Incident: CROSS_REPO_TOKEN was never provisioned, so the push-triggered
# sync workflow failed 22/22 times over four months before anyone
# noticed (the trigger is parked, dispatch-only, since 2026-07-14 —
# re-enablement tracked as KIT-0045).
#
# Read-only. Root from DOCTOR_ROOT (driver-set), else file-relative.
# May hit the network (gh secret list) only when the trigger is active.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${DOCTOR_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"
WORKFLOW="$ROOT/.github/workflows/sync-core-scripts.yml"

if [ ! -f "$WORKFLOW" ]; then
    echo "DOCTOR:push-sync-token:SKIP:sync-core-scripts.yml not present"
    exit 0
fi

# An active push trigger can be block style at any indent (`push:` on
# its own line), flow style (`on: [push, ...]`), or scalar (`on: push`).
# Comments discussing "push" do not match (o3 review: the original
# two-space-only grep silently SKIPped on other indents — erring toward
# "checking" beats erring toward SKIP for this incident class).
if ! grep -qE '^[[:space:]]*push:[[:space:]]*$|^on:[[:space:]]*(\[[^]]*push|push[[:space:]]*$)' "$WORKFLOW"; then
    echo "DOCTOR:push-sync-token:SKIP:push channel parked — see KIT-0045"
    exit 0
fi

if ! command -v gh >/dev/null 2>&1; then
    echo "DOCTOR:push-sync-token:WARN:push trigger active but gh unavailable — cannot verify CROSS_REPO_TOKEN"
    exit 0
fi

SECRETS="$(gh secret list 2>/dev/null)" || {
    echo "DOCTOR:push-sync-token:WARN:push trigger active but secret list unreadable (needs repo admin) — verify CROSS_REPO_TOKEN manually"
    exit 0
}

if printf '%s\n' "$SECRETS" | grep -q 'CROSS_REPO_TOKEN'; then
    echo "DOCTOR:push-sync-token:PASS:push trigger active and CROSS_REPO_TOKEN present"
else
    echo "DOCTOR:push-sync-token:FAIL:push trigger active but CROSS_REPO_TOKEN missing — the 22/22-failure incident repeats on next push"
fi

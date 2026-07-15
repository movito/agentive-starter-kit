#!/bin/bash
# checks.sh — this project's check hook (seeded by bootstrap; consumer-owned).
#
# Contract (KIT-ADR-0027 P1): accepts `--mode ci|local`; exits 0 (pass)
# or 1 (fail) only; human-readable diagnostics to stdout; invoked from
# the repo root with no other environment guarantees. Nothing else is
# passed through. ci-check.sh dispatches here when this file exists.
# Edit freely — the kit never overwrites this file after seeding.
#
# Profile: none — no project toolchain checks are configured. This hook
# says so loudly and passes, so nobody mistakes silence for coverage.

MODE=""
case "${1:-}" in
    --mode) MODE="${2:-}" ;;
    --mode=*) MODE="${1#--mode=}" ;;
esac
if [ "$MODE" != "ci" ] && [ "$MODE" != "local" ]; then
    echo "Usage: $0 --mode ci|local"
    echo "   Unknown or missing mode: '${MODE:-<none>}'"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  No project checks configured (profile: none)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   scripts/local/checks.sh is a deliberate no-op — this project"
echo "   declares no local toolchain. Verification relies on review and"
echo "   any repository-side CI. To add checks, edit this hook (the"
echo "   contract is in the header) — the kit never overwrites it."
exit 0

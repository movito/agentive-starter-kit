#!/usr/bin/env bash
# doctor check: gh installed AND authenticated.
#
# Incident (KIT-ADR-0027 Context): verify-setup.sh marked `gh` as
# "optional" while the entire bot/CI loop (pr checks, review threads,
# preflight gates) runs through it — backbone-first inverts that.
#
# Contract: emits DOCTOR:<name>:<verdict>:<detail> lines; read-only;
# resolves nothing from cwd (gh state is global). May hit the network
# (gh auth status) — one of the two checks allowed to (N2).

set -u

if ! command -v gh >/dev/null 2>&1; then
    echo "DOCTOR:gh-auth:FAIL:gh CLI not installed — the bot/CI loop cannot run (install: https://cli.github.com)"
    exit 0
fi

if gh auth status >/dev/null 2>&1; then
    echo "DOCTOR:gh-auth:PASS:gh installed and authenticated"
else
    echo "DOCTOR:gh-auth:FAIL:gh installed but not authenticated — run: gh auth login"
fi

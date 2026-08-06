#!/usr/bin/env bash
# shapes: single planning
# doctor check: plugin marketplace source is GitHub, not a directory.
#
# Incident (KIT-0030 gotcha): a `Directory (...)` marketplace source
# serves whatever is on disk and silently defeats version pins — the
# plugin "upgrade" path then does nothing.
#
# Grep is the hardened pattern from docs/PLUGIN-UPGRADE-GUIDE.md
# (anchored to the Source field so "Directory (/Users/alice/github/
# movito/agentive-skills)" cannot slip past; end-anchored so
# movito/agentive-skills-beta cannot either). Do not re-derive it.
#
# Read-only; no network (reads the local plugin registry).

set -u

if ! command -v claude >/dev/null 2>&1; then
    echo "DOCTOR:plugin-source:SKIP:claude CLI not on PATH — cannot inspect marketplace"
    exit 0
fi

OUT="$(claude plugin marketplace list 2>/dev/null)" || {
    echo "DOCTOR:plugin-source:SKIP:claude plugin marketplace list failed — cannot inspect"
    exit 0
}

if printf '%s\n' "$OUT" | grep -qiE '^[[:space:]]*source: *(github \(|https://github\.com/)movito/agentive-skills([[:space:]]*\)|$)'; then
    echo "DOCTOR:plugin-source:PASS:agentive-skills marketplace is GitHub-sourced"
elif printf '%s\n' "$OUT" | grep -qi 'agentive-skills'; then
    echo "DOCTOR:plugin-source:FAIL:agentive-skills marketplace is not GitHub-sourced (directory source defeats version pins) — re-point: claude plugin marketplace remove agentive-skills && claude plugin marketplace add movito/agentive-skills"
else
    echo "DOCTOR:plugin-source:SKIP:agentive-skills marketplace not installed"
fi

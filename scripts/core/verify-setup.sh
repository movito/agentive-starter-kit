#!/bin/bash
# DEPRECATED (KIT-0046, ADR-0027 P4): verify-setup.sh is now a shim.
#
# The real environment verifier is `project doctor` — an incident-mapped
# check set in scripts/core/doctor.d/ (gh-auth first; this script's old
# "gh optional" stance is exactly the assumption ADR-0027 corrects).
#
# Removal is filed as KIT-0047 (the ADR's shims-with-filed-removal rule);
# until then this shim keeps existing docs and muscle memory working.
# Exit codes follow the doctor contract: 0 ok, 1 failures, 2 warnings
# only, 3 driver error.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "⚠️  verify-setup.sh is deprecated — running: ./scripts/core/project doctor" >&2
exec "$SCRIPT_DIR/project" doctor "$@"

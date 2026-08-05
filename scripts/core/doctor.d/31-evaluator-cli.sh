#!/usr/bin/env bash
# shapes: single planning
# doctor check: the `adversarial` CLI binary is on PATH and runnable.
#
# Incident (KIT-0083, issue #103): a fresh consumer project shipped
# .adversarial/config.yml AND the evaluator library, so 30-evaluators.sh
# reported PASS — but nothing had ever installed the CLI itself. The
# failure surfaced at the planner's Phase 3 evaluation GATE as
# `adversarial: command not found`, long after the project looked fully
# provisioned. This check exists so the library's PASS can never mask a
# missing binary again.
#
# Deliberately separate from 30-evaluators.sh: that one answers "is the
# evaluator library installed" (a tree fact), this one answers "can we
# actually run an evaluation" (a PATH fact). One verdict cannot carry
# both. (KIT-0055 will add a third question — *which* binary is it,
# editable vs tool install — which is meaningless before this one.)
#
# Read-only. Root from DOCTOR_ROOT (driver-set; tests use tmp fixtures),
# else derived from this file's location.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${DOCTOR_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"

if [ ! -d "$ROOT/.adversarial" ]; then
    echo "DOCTOR:evaluator-cli:SKIP:adversarial workflow not initialized (.adversarial/ absent)"
    exit 0
fi

FIX="run: ./scripts/core/project install-evaluators (or: uv tool install adversarial-workflow)"
PATH_HINT="if you just installed it, uv puts binaries in ~/.local/bin — add it to PATH"

if ! command -v adversarial >/dev/null 2>&1; then
    echo "DOCTOR:evaluator-cli:FAIL:adversarial CLI not on PATH — $FIX; $PATH_HINT"
    exit 0
fi

# Probe the EXIT CODE, never the output: `adversarial --version` prints
# "Unknown fields in evaluator.yml" warnings to stderr on a healthy
# install (verified 2026-08-05), so an output-parsing check would report
# a false FAIL.
if ! adversarial --version >/dev/null 2>&1; then
    echo "DOCTOR:evaluator-cli:FAIL:adversarial CLI found but '--version' failed — reinstall: uv tool install --force adversarial-workflow"
    exit 0
fi

echo "DOCTOR:evaluator-cli:PASS:adversarial CLI available ($(command -v adversarial))"

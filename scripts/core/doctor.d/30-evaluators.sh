#!/usr/bin/env bash
# shapes: single planning
# doctor check: evaluator library installed (.adversarial/evaluators/ non-empty).
#
# Incident (KIT-0043 worktree pilot): a fresh worktree had no
# .adversarial/evaluators/, so the `adversarial` CLI listed no evaluator
# commands and failed with a confusing "invalid choice" error mid-review.
#
# Read-only. Root from DOCTOR_ROOT (driver-set; tests use tmp fixtures),
# else derived from this file's location.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${DOCTOR_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"

if [ ! -d "$ROOT/.adversarial" ]; then
    echo "DOCTOR:evaluators:SKIP:adversarial workflow not initialized (.adversarial/ absent)"
    exit 0
fi

EVAL_DIR="$ROOT/.adversarial/evaluators"
if [ ! -d "$EVAL_DIR" ] || [ -z "$(ls -A "$EVAL_DIR" 2>/dev/null)" ]; then
    echo "DOCTOR:evaluators:FAIL:.adversarial/evaluators/ missing or empty — run: ./scripts/core/project install-evaluators"
    exit 0
fi

COUNT=$(ls -A "$EVAL_DIR" | wc -l | tr -d ' ')
echo "DOCTOR:evaluators:PASS:evaluator library installed ($COUNT entries)"

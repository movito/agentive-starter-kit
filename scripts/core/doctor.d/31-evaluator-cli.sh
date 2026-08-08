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

# Fix command matches the repo's world (KIT-0093): packaged repos
# carry no scripts/core — the installer lives in the agentive CLI.
if [ -x "$ROOT/scripts/core/project" ]; then
    FIX="run: ./scripts/core/project install-evaluators (or: uv tool install adversarial-workflow)"
else
    FIX="run: agentive install-evaluators (or: uv tool install adversarial-workflow)"
fi
PATH_HINT="if you just installed it, uv puts binaries in ~/.local/bin — add it to PATH"

if ! command -v adversarial >/dev/null 2>&1; then
    echo "DOCTOR:evaluator-cli:FAIL:adversarial CLI not on PATH — $FIX; $PATH_HINT"
    exit 0
fi

# Probe the EXIT CODE, never the output: `adversarial --version` prints
# "Unknown fields in evaluator.yml" warnings to stderr on a healthy
# install (verified 2026-08-05), so an output-parsing check would report
# a false FAIL.
#
# Bounded so a corrupt install that blocks on stdin/network cannot hang
# the whole doctor run (o3 review). Deliberately NOT GNU `timeout`:
# it is a homebrew add-on on macOS (absent from a stock system), so
# depending on it would work on a brew-equipped machine and hang on a
# plain one — the same "passes locally, proves nothing" trap that let
# issue #103 ship. </dev/null closes the stdin path; the
# background-and-poll below bounds everything else.
#
# `sleep` is resolved to an ABSOLUTE path (same idea as BASH in
# tests/test_doctor.py): doctor checks must survive a restricted PATH,
# and a bare `sleep` there fails, spins the loop instantly and reports a
# false FAIL on a perfectly healthy CLI — caught by
# test_stub_binary_on_path_passes. If no sleep exists at all, skip the
# bound rather than invent one: an unbounded probe is still better than
# a wrong verdict.
SLEEP_BIN=""
for candidate in /bin/sleep /usr/bin/sleep; do
    if [ -x "$candidate" ]; then
        SLEEP_BIN="$candidate"
        break
    fi
done

# MUST match CLI_PROBE_TIMEOUT in scripts/core/project: the installer and
# this check probe the same binary for the same purpose, and a CLI that
# answers in between the two bounds would be "working" to one surface and
# FAIL to the other — the two-surfaces-disagree state this check exists
# to close (CodeRabbit round 1).
PROBE_TIMEOUT=20

REINSTALL="reinstall: uv tool install --force adversarial-workflow"

adversarial --version >/dev/null 2>&1 </dev/null &
probe_pid=$!

if [ -n "$SLEEP_BIN" ]; then
    probe_waited=0
    while kill -0 "$probe_pid" 2>/dev/null && [ "$probe_waited" -lt "$PROBE_TIMEOUT" ]; do
        "$SLEEP_BIN" 1
        probe_waited=$((probe_waited + 1))
    done
    if kill -0 "$probe_pid" 2>/dev/null; then
        kill "$probe_pid" 2>/dev/null
        wait "$probe_pid" 2>/dev/null
        echo "DOCTOR:evaluator-cli:FAIL:adversarial CLI found but '--version' did not finish within ${PROBE_TIMEOUT}s — likely a corrupt install; $REINSTALL"
        exit 0
    fi
fi
# Reaped either way: the polling loop above exits only once the probe is
# done. With NO sleep binary this `wait` blocks unbounded — a deliberate
# tradeoff, not an oversight (CodeRabbit round 1 proposed a `read -t`
# timer instead). Rejected because every bash-builtin timer needs a
# non-EOF descriptor, which needs a long-lived helper process holding a
# pipe open — reintroducing the very external-binary dependency this
# branch exists to survive, in exchange for a rarer, harder-to-audit
# construct. The branch requires neither /bin/sleep nor /usr/bin/sleep
# to exist, i.e. effectively no POSIX system; there, answering slowly
# beats answering wrongly.
if ! wait "$probe_pid"; then
    echo "DOCTOR:evaluator-cli:FAIL:adversarial CLI found but '--version' failed — $REINSTALL"
    exit 0
fi

echo "DOCTOR:evaluator-cli:PASS:adversarial CLI available ($(command -v adversarial))"

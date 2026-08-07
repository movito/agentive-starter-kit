#!/usr/bin/env bash
# shapes: single planning
# doctor check: core.bare is false in the primary clone.
#
# Incident (KIT-0043): a pre-commit GIT_DIR leak from inside a worktree
# flipped core.bare=true on the PRIMARY clone — repository state
# corruption, not just a failing test. The suite-wide GIT_* isolation
# in tests/conftest.py kills the known vector; this check is the
# standing canary (WORKTREE-WORKFLOW.md documents the manual form).
#
# Read-only. Resolves the primary clone via git-common-dir from
# DOCTOR_ROOT (never cwd assumptions — N4), so it works from any
# worktree and always inspects the shared config.

set -u

# Leaked GIT_* env would make git ignore -C or override config values
# (GIT_CONFIG_COUNT/KEY_0/VALUE_0 can literally rewrite core.bare) — the
# exact leak class this check diagnoses must not be able to blind the
# check itself. Scrub EVERY GIT_* variable, not an allowlist (fast-v2
# round 1 + CodeRabbit round 2; the driver also scrubs, but this check
# must survive standalone runs).
for _git_var in $(compgen -A variable | grep '^GIT_' || true); do
    unset "$_git_var"
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${DOCTOR_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"

# KIT-0080: plain --git-common-dir, absolutized in shell. The
# --path-format=absolute form needs git >= 2.31; Apple's system git
# (2.30.1) echoes the flag back as an output line and still exits 0, so
# the SKIP branch below never fired and COMMON_DIR became garbage — the
# check then read core.bare from a nonexistent git dir and always said
# PASS, blinding the KIT-0043 canary. Plain output may be relative to
# the -C directory, hence the join below.
#
# The result is emptiness-checked BEFORE joining: on failure the
# substitution is empty, which would otherwise resolve to $ROOT —
# turning "not a repo" into a confident wrong answer, the very class
# this task removes. A relative answer is joined by STRING rather than
# `cd`+`pwd`, so a symlinked checkout keeps its logical path in the
# verdict line (/var -> /private/var on macOS).
COMMON_DIR=""
COMMON_RAW="$(git -C "$ROOT" rev-parse --git-common-dir 2>/dev/null)" || COMMON_RAW=""
case "$COMMON_RAW" in
    '') COMMON_DIR="" ;;
    /*) COMMON_DIR="$COMMON_RAW" ;;
    *)  COMMON_DIR="$ROOT/$COMMON_RAW" ;;
esac
if [ -z "$COMMON_DIR" ]; then
    echo "DOCTOR:core-bare:SKIP:not a git repository ($ROOT)"
    exit 0
fi

BARE="$(git --git-dir "$COMMON_DIR" config --get core.bare 2>/dev/null)"

if [ "$BARE" = "true" ]; then
    echo "DOCTOR:core-bare:FAIL:primary clone is bare ($COMMON_DIR) — GIT_DIR leak damage; restore: git --git-dir $COMMON_DIR config core.bare false, then verify the working tree"
else
    echo "DOCTOR:core-bare:PASS:primary clone is a normal checkout (core.bare=${BARE:-unset})"
fi

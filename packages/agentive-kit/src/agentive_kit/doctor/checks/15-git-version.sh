#!/usr/bin/env bash
# shapes: single planning
# doctor check: git meets the kit's supported version floor (KIT-0080 F4).
#
# Incident (KIT-0080): the kit's path resolvers used
# `git rev-parse --path-format=absolute`, a flag added in git 2.31
# (March 2021). Stock macOS ships Apple Git 2.30.1 — one minor version
# below — which does NOT consume the flag: it echoes it back as the
# first output line and still exits 0. Failures ranged from silent (the
# setup door resolved an operator path to relative garbage, so a
# correctly-authored preset was ignored on every run and planning repos
# came out misprovisioned) to hard (new-worktree.sh died, making the
# kit's DEFAULT session topology unusable). CI could not catch any of
# it: Ubuntu runners ship modern git, so the whole class was green in
# CI and broken on stock Macs.
#
# KIT-0080 made every resolver portable, which is why the floor below is
# 2.30 and not 2.31 — this check documents the floor the scripts
# actually hold to, and turns the next such incident loud instead of
# silent. Raise FLOOR_* here (and the README Requirements row, which
# must agree) if the kit ever adopts a newer git feature.
#
# Verdicts:
#   PASS  git present and at/above the floor
#   WARN  git present but below the floor (named, with the remedy)
#   WARN  git present but the version string is unparseable
#   FAIL  git not installed at all
#
# Read-only, no network. Portable by construction: `git --version` plus
# bash string ops — no Homebrew-only tools (README portability rule; the
# `timeout` lesson), and deliberately no sort -V, whose BSD/GNU
# availability differs across the platforms the kit supports.

set -u

FLOOR_MAJOR=2
FLOOR_MINOR=30
FLOOR="$FLOOR_MAJOR.$FLOOR_MINOR"

if ! command -v git >/dev/null 2>&1; then
    echo "DOCTOR:git-version:FAIL:git not installed — the kit's task, worktree and CI flows all run through it (install: https://git-scm.com/downloads)"
    exit 0
fi

RAW="$(git --version 2>/dev/null)" || RAW=""

# `git version 2.30.1 (Apple Git-130)` -> `2.30.1 (Apple Git-130)` -> `2.30.1`
VERSION="${RAW#git version }"
VERSION="${VERSION%% *}"

# Split on dots without a subshell or external tool. A non-numeric or
# absent field must not be silently treated as 0 — that would let an
# unparseable string masquerade as an ancient (or modern) git, so bail
# to WARN instead and name what we saw.
MAJOR="${VERSION%%.*}"
# A version with no dot at all ("git version 2") leaves REST identical
# to VERSION, which would silently reuse the major as the minor and read
# "2" as 2.2. Require the dot explicitly.
if [ "$VERSION" = "${VERSION#*.}" ]; then
    MINOR=""
else
    REST="${VERSION#*.}"
    MINOR="${REST%%.*}"
fi

case "$MAJOR" in
    '' | *[!0-9]*) MAJOR="" ;;
esac
case "$MINOR" in
    '' | *[!0-9]*) MINOR="" ;;
esac

if [ -z "$MAJOR" ] || [ -z "$MINOR" ] || [ "$VERSION" = "$RAW" ]; then
    echo "DOCTOR:git-version:WARN:cannot parse the git version from '$RAW' — the kit needs git >= $FLOOR; verify manually with: git --version"
    exit 0
fi

if [ "$MAJOR" -gt "$FLOOR_MAJOR" ] \
    || { [ "$MAJOR" -eq "$FLOOR_MAJOR" ] && [ "$MINOR" -ge "$FLOOR_MINOR" ]; }; then
    echo "DOCTOR:git-version:PASS:git $VERSION meets the supported floor (>= $FLOOR)"
    exit 0
fi

# Below the floor. `xcode-select --install` is the intuitive first thing
# to try and does NOT help — Apple's Command Line Tools ship 2.30.x by
# design (a constrained system binary, not a stale download), so the
# remedy names the two things that do work.
echo "DOCTOR:git-version:WARN:git $VERSION is below the supported floor ($FLOOR) — path resolution and worktree flows may misbehave; upgrade with 'brew install git' then 'hash -r' (note: xcode-select --install does NOT help — Apple's CLT ship 2.30.x by design)"
exit 0

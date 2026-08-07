#!/usr/bin/env bash
# shapes: single planning
# doctor check: operator config-home guardrails (KIT-0058, ADR-0027 P7).
#
# Incident (operator review, 2026-07-21 — the P7 amendment): the
# invisible ~/.config dotfolder was a discoverability threshold, so
# the operator config moved to a VISIBLE sibling of the kit checkout
# (<kit-parent>/agentive-config/). Visibility + guardrails beat
# obscurity — but only if the guardrails are checked: a config home
# pushed to a PUBLIC remote exposes the operator's setup, and a
# TRACKED env.source is a secret in git.
#
# Verdicts:
#   SKIP  no config home yet (path named), or nothing to resolve from
#   PASS  home exists with no git repo, or a repo with no remote
#   WARN  remote visibility is not private, or gh cannot verify it
#         (the risk is named either way)
#   FAIL  env.source is TRACKED in the config home's git repo
#
# Resolution mirrors the door's config_home():
# AGENTIVE_KIT_CONFIG_DIR override, else the primary clone's parent
# via --git-common-dir (worktree-safe) + /agentive-config. Read-only;
# network only via gh repo view (the visibility probe).
#
# Anchoring note (BugBot, PR #91): this check anchors to the checkout
# it diagnoses (DOCTOR_ROOT), the door to the kit clone — identical
# exactly when kit and project share a parent (the documented sibling
# layout). A consumer checkout cannot compute the kit clone's local
# path, so when layouts diverge the override is the pin, and every
# verdict line names the resolved path to keep the anchor visible.

set -u

# Leaked GIT_* env would redirect every git call below at the wrong
# repository (the KIT-0043 leak class) — scrub all of it; the driver
# also scrubs, but this check must survive standalone runs.
for _git_var in $(compgen -A variable | grep '^GIT_' || true); do
    unset "$_git_var"
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${DOCTOR_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"

resolve_home() {
    if [ -n "${AGENTIVE_KIT_CONFIG_DIR:-}" ]; then
        # leading-~ expansion, mirroring the door's config_home
        printf '%s\n' "${AGENTIVE_KIT_CONFIG_DIR/#\~/$HOME}"
        return 0
    fi
    local common
    # KIT-0080: --path-format=absolute needs git >= 2.31; Apple's system
    # git (2.30.1) does not consume the flag, echoes it back as the first
    # output line and exits 0 — the nested dirname then sees an arg
    # starting with `--` (the stray `dirname: illegal option`) and the
    # home resolved to the relative garbage ./agentive-config, silently
    # hiding the operator preset. Plain --git-common-dir is portable; its
    # output is relative to the -C directory, so absolutize there.
    #
    # Emptiness-checked BEFORE joining: on failure the substitution is
    # empty, which would otherwise resolve to $ROOT — a confident wrong
    # home instead of the rc 1 that drives the SKIP branch.
    #
    # A RELATIVE answer (both gits print a bare ".git" from a primary
    # clone) is joined by string, not by `cd`+`pwd`: cd-ing resolves
    # symlinked ancestors and would return the PHYSICAL path, changing
    # the reported home on any symlinked checkout (/var -> /private/var
    # on macOS). String-joining preserves the caller's logical path,
    # matching what this check reported before KIT-0080.
    local raw
    raw="$(git -C "$ROOT" rev-parse --git-common-dir 2>/dev/null)" || return 1
    [ -n "$raw" ] || return 1
    case "$raw" in
        /*) common="$raw" ;;
        *)  common="$ROOT/$raw" ;;
    esac
    # Two levels: $common is <primary-clone>/.git, so one dirname gives
    # the clone root and the second its PARENT, which is where the
    # visible agentive-config sibling lives.
    printf '%s\n' "$(dirname "$(dirname "$common")")/agentive-config"
}

if ! HOME_DIR="$(resolve_home)"; then
    echo "DOCTOR:config-home:SKIP:cannot resolve the config home ($ROOT is not a git clone)"
    exit 0
fi

if [ ! -d "$HOME_DIR" ]; then
    echo "DOCTOR:config-home:SKIP:no config home at $HOME_DIR — author one with /setup-preset (path anchors to the primary clone's parent; AGENTIVE_KIT_CONFIG_DIR overrides)"
    exit 0
fi

# -e, not -d: a gitfile (worktree/submodule layout) also marks a repo.
# The home must be its OWN repo — being inside some parent repo's tree
# does not make the guardrails apply to it.
if [ ! -e "$HOME_DIR/.git" ]; then
    echo "DOCTOR:config-home:PASS:config home at $HOME_DIR (no git repo — the private-repo pattern is optional)"
    exit 0
fi

# The one hard line: a tracked env.source is a secret in git (FAIL).
# No exit — the visibility verdict below still runs; the driver
# aggregates multi-line checks and FAIL wins.
if git -C "$HOME_DIR" ls-files --error-unmatch env.source >/dev/null 2>&1; then
    echo "DOCTOR:config-home:FAIL:env.source is TRACKED in $HOME_DIR — a secret in git; untrack it: git -C $HOME_DIR rm --cached env.source (the seeded .gitignore ignores it)"
fi

REMOTE_URL="$(git -C "$HOME_DIR" remote get-url origin 2>/dev/null)" || REMOTE_URL=""
if [ -z "$REMOTE_URL" ]; then
    # no origin — fall back to the first remote of any name
    FIRST_REMOTE="$(git -C "$HOME_DIR" remote 2>/dev/null | head -1)"
    if [ -n "$FIRST_REMOTE" ]; then
        REMOTE_URL="$(git -C "$HOME_DIR" remote get-url "$FIRST_REMOTE" 2>/dev/null)" || REMOTE_URL=""
    fi
fi

if [ -z "$REMOTE_URL" ]; then
    echo "DOCTOR:config-home:PASS:config home at $HOME_DIR is a git repo with no remote — local-only is fine"
    exit 0
fi

# Never print the raw URL: embedded credentials/tokens must not reach
# doctor output or CI logs (CodeRabbit, PR #109) — redact userinfo.
REMOTE_URL_DISPLAY="$(printf '%s' "$REMOTE_URL" | sed -E 's#(://)[^/@]*@#\1<redacted>@#')"
if ! command -v gh >/dev/null 2>&1; then
    echo "DOCTOR:config-home:WARN:cannot verify visibility of $REMOTE_URL_DISPLAY (gh not installed) — if that repo is public, your operator config is exposed"
    exit 0
fi

# flags first, then `--`: a hostile remote URL beginning with `-` can
# never be parsed as a gh flag (claude-code review, this PR)
VISIBILITY="$(gh repo view --json visibility --jq .visibility -- "$REMOTE_URL" 2>/dev/null)" || VISIBILITY=""
VISIBILITY="$(printf '%s' "$VISIBILITY" | tr '[:upper:]' '[:lower:]')"
case "$VISIBILITY" in
    private)
        echo "DOCTOR:config-home:PASS:config home remote is private ($REMOTE_URL_DISPLAY)"
        ;;
    "")
        echo "DOCTOR:config-home:WARN:cannot verify visibility of $REMOTE_URL_DISPLAY (gh query failed) — if that repo is public, your operator config is exposed"
        ;;
    *)
        echo "DOCTOR:config-home:WARN:config home remote is $VISIBILITY ($REMOTE_URL_DISPLAY) — your operator config is exposed; make the repo private"
        ;;
esac
exit 0

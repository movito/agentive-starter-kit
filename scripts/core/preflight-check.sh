#!/bin/bash
# Run all 7 preflight gates for a PR
# Usage: ./scripts/core/preflight-check.sh [--pr PR_NUMBER] [--task TASK_ID] [--repo owner/name] [--help]
#
# Metadata:
#   version: 1.3.0
#   origin: dispatch-kit
#   origin-version: 0.3.2
#   last-updated: 2026-07-18
#   created-by: "@movito with planner2"
#
# Cross-repo support (ID2-0014):
#   When CLAUDE.md contains a "## Target Repository" section, or when
#   --repo owner/name is passed, all gh calls target that repo and git
#   branch/log queries read from the target-repo working tree
#   (git -C $TARGET_PATH). Local evaluator-review and task-folder gates
#   (5, 6, 7) always read the planning repo's .kit/ directory.
#
# Output format (structured for machine parsing):
#   GATE:<number>:<name>:PASS|FAIL|PENDING|SKIP:<detail>
#
#   PENDING (KIT-0034 F4): the gate cannot be evaluated yet — CI runs not
#   registered for the head SHA, or runs still executing. Not a failure
#   verdict; re-run preflight shortly.
#
#   SKIP (KIT-0056, ADR-0027 P5): the gate does not apply — a `bots:`
#   line in CLAUDE.md's kit-install region declares the bot absent on
#   this project, so Gates 2/3 SKIP with the declaration named (never
#   FAIL, never a silent PASS). No declaration = both bots expected =
#   the pre-KIT-0056 behavior, unchanged.
#
# Exit codes:
#   0 — All gates pass (SKIP counts as satisfied)
#   1 — One or more gates fail, or error
#   2 — No gate failed, but at least one is PENDING (re-run shortly)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# shellcheck disable=SC1091
. "$SCRIPT_DIR/lib/target_repo.sh"

PR_NUMBER=""
TASK_ID=""
REPO_OVERRIDE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "Usage: ./scripts/core/preflight-check.sh [--pr PR_NUMBER] [--task TASK_ID] [--repo owner/name]"
            echo ""
            echo "Run all 7 preflight gates for a PR before human review."
            echo ""
            echo "Options:"
            echo "  --pr PR_NUMBER      PR number to check (default: auto-detect)"
            echo "  --task TASK_ID      Task ID, e.g. TASK-0001 (default: derived from branch)"
            echo "  --repo owner/name   Target GitHub repo (overrides CLAUDE.md ## Target Repository)"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Gates:"
            echo "  1. CI green                    GitHub Actions passing"
            echo "  2. CodeRabbit reviewed          coderabbitai[bot] reviewed latest code commit"
            echo "  3. BugBot reviewed              cursor[bot] reviewed latest code commit"
            echo "     (Gates 2/3 SKIP when a 'bots:' line in CLAUDE.md's kit-install"
            echo "      region declares the bot absent — e.g. 'bots: none')"
            echo "  4. Zero unresolved threads      All review threads resolved"
            echo "  5. Evaluator review persisted   .kit/context/reviews/<TASK>-{evaluator-review,code-review,code-reviewer}*.md"
            echo "  6. Review starter exists         .kit/context/<TASK>-REVIEW-STARTER.md"
            echo "  7. Task in correct folder        .kit/tasks/3-in-progress or 4-in-review"
            echo ""
            echo "Exit codes:"
            echo "  0  All gates pass"
            echo "  1  One or more gates fail"
            echo "  2  No failures, but at least one gate PENDING (re-run shortly)"
            exit 0
            ;;
        --pr)
            if [ -z "${2:-}" ] || [[ "$2" == -* ]]; then
                echo "ERROR: --pr requires a PR number"
                exit 1
            fi
            PR_NUMBER="$2"
            shift 2
            ;;
        --task)
            if [ -z "${2:-}" ] || [[ "$2" == -* ]]; then
                echo "ERROR: --task requires a task ID"
                exit 1
            fi
            TASK_ID="$2"
            shift 2
            ;;
        --repo)
            if [ -z "${2:-}" ] || [[ "$2" == -* ]]; then
                echo "ERROR: --repo requires an owner/name value" >&2
                exit 1
            fi
            REPO_OVERRIDE="$2"
            shift 2
            ;;
        --repo=*)
            REPO_OVERRIDE="${1#--repo=}"
            if [ -z "$REPO_OVERRIDE" ]; then
                echo "ERROR: --repo= requires an owner/name value" >&2
                exit 1
            fi
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            echo "Run: ./scripts/core/preflight-check.sh --help"
            exit 1
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Run: ./scripts/core/preflight-check.sh --help"
            exit 1
            ;;
    esac
done

# Check gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "ERROR: gh CLI (gh) not installed"
    echo "Install: https://cli.github.com/"
    exit 1
fi

# Check gh is authenticated
if ! gh auth status &> /dev/null; then
    echo "ERROR: gh CLI not authenticated"
    echo "Run: gh auth login"
    exit 1
fi

# Apply cross-repo detection (CLAUDE.md + --repo override)
if [ -n "$REPO_OVERRIDE" ]; then
    target_repo_init --repo "$REPO_OVERRIDE" || exit 1
else
    target_repo_init || exit 1
fi

# Detect repo owner/name — prefer the configured target repo.
if target_repo_is_set; then
    REPO="$TARGET_REPO"
else
    REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)
    if [ -z "$REPO" ]; then
        echo "ERROR: Could not determine GitHub repository"
        echo "Run: gh repo set-default"
        exit 1
    fi
fi

# Validate the slug shape wherever it came from (--repo, CLAUDE.md, or
# gh) before OWNER/NAME are interpolated into a GraphQL query string —
# an unvalidated value could rewrite the query (KIT-0043, o3 finding).
if ! printf '%s' "$REPO" | grep -qE '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$'; then
    echo "ERROR: repository must look like owner/name, got: '$REPO'"
    exit 1
fi

OWNER=$(echo "$REPO" | cut -d/ -f1)
NAME=$(echo "$REPO" | cut -d/ -f2)

# Detect branch. In cross-repo mode, read from the target-repo working tree.
# shellcheck disable=SC2086
BRANCH=$(git $GIT_DIR_ARG branch --show-current 2>/dev/null)
if [ -z "$BRANCH" ]; then
    echo "ERROR: Could not determine current branch"
    exit 1
fi

# Derive task ID from branch if not provided
if [ -z "$TASK_ID" ]; then
    TASK_ID=$(echo "$BRANCH" | sed -n 's|^feature/\([A-Z][A-Z0-9]*-[0-9][0-9]*\).*|\1|p')
    if [ -z "$TASK_ID" ]; then
        echo "ERROR: Could not derive task ID from branch '$BRANCH'"
        echo "Use --task TASK_ID to specify manually."
        exit 1
    fi
fi

# Auto-detect PR number if not provided. Pass $BRANCH explicitly so cross-repo
# mode (where CWD's branch differs from target's branch) resolves correctly.
if [ -z "$PR_NUMBER" ]; then
    # shellcheck disable=SC2086
    PR_NUMBER=$(gh $GH_REPO_ARG pr view "$BRANCH" --json number --jq .number 2>/dev/null || true)
    if [ -z "$PR_NUMBER" ]; then
        echo "ERROR: No PR found for branch '$BRANCH'"
        echo "Push your branch and open a PR first, or use --pr PR_NUMBER."
        exit 1
    fi
fi

# Defense-in-depth: PR_NUMBER is interpolated into GraphQL queries below,
# so insist it is numeric whether it came from --pr or from gh pr view.
if ! [[ "$PR_NUMBER" =~ ^[0-9]+$ ]]; then
    echo "ERROR: PR number must be numeric (got: $PR_NUMBER)"
    exit 1
fi

# Get PR head SHA for review checks
# shellcheck disable=SC2086
LATEST_SHA=$(gh $GH_REPO_ARG pr view "$PR_NUMBER" --json headRefOid --jq .headRefOid 2>/dev/null || true)
if [ -z "$LATEST_SHA" ]; then
    echo "ERROR: Could not fetch PR #$PR_NUMBER head SHA"
    exit 1
fi

ANY_FAILED=false
ANY_PENDING=false
SKIP_COUNT=0

# ─── Bot declaration (KIT-0056, ADR-0027 P5) ────────────────────────
# A `bots:` line in CLAUDE.md's kit-install region declares which
# review bots run on this project ('none', or a subset of
# 'coderabbit bugbot'). Declared-absent bots make Gates 2/3 SKIP with
# the declaration named — never FAIL, never a silent PASS. Absent
# line, absent region, or unreadable record = both bots expected —
# the pre-declaration behavior (fail closed: when in doubt, the gates
# run). Read via kit_markers.py, the region's one reader — never
# ad-hoc regex over CLAUDE.md.
BOTS_DECLARED=""
if [ -f "scripts/local/kit_markers.py" ] && [ -f "CLAUDE.md" ] && command -v python3 >/dev/null 2>&1; then
    KIT_INSTALL_REGION=$(python3 scripts/local/kit_markers.py extract CLAUDE.md kit-install 2>/dev/null || true)
    BOTS_DECLARED=$(printf '%s\n' "$KIT_INSTALL_REGION" | sed -n 's/^bots:[[:space:]]*//p' | head -1)
fi
if [ -n "$BOTS_DECLARED" ]; then
    # Validate: an unrecognized declaration must not silently SKIP a
    # gate (a typo'd 'bots:' line would otherwise skip both bots) —
    # fail closed to expecting both, and say so.
    _BOTS_VALID=true
    for _BOT_TOK in $BOTS_DECLARED; do
        case "$_BOT_TOK" in
            coderabbit|bugbot|none) ;;
            *) _BOTS_VALID=false ;;
        esac
    done
    if [ "$_BOTS_VALID" = true ]; then
        case " $BOTS_DECLARED " in
            *" none "*)
                [ "$BOTS_DECLARED" = "none" ] || _BOTS_VALID=false
                ;;
        esac
    fi
    if [ "$_BOTS_VALID" = false ]; then
        echo "NOTICE: invalid bots declaration in kit-install ('bots: $BOTS_DECLARED') — expecting both bots (fail closed); fix the line in CLAUDE.md"
        BOTS_DECLARED=""
    fi
fi

bot_declared_absent() {  # $1 coderabbit|bugbot → 0 when declared absent
    [ -n "$BOTS_DECLARED" ] || return 1
    [ "$BOTS_DECLARED" = "none" ] && return 0
    case " $BOTS_DECLARED " in
        *" $1 "*) return 1 ;;
    esac
    return 0
}

# ─── Determine latest code commit for bot review checks ───────────
# Bots don't re-review markdown-only pushes. Find the latest commit
# that touched non-markdown, non-planner files so Gates 2-3 check
# the right SHA. Gate 1 (CI) still checks LATEST_SHA (HEAD).

# Verify origin/main is available for the commit range query. In cross-repo
# mode, check it inside the target-repo working tree.
# shellcheck disable=SC2086
if ! git $GIT_DIR_ARG rev-parse --verify origin/main &>/dev/null; then
    echo "ERROR: origin/main not found. Run: git fetch origin main"
    # Guard on TARGET_PATH (not TARGET_REPO) — a --repo override leaves
    # TARGET_PATH empty, in which case showing "(target repo path: )"
    # would be misleading.
    if [ -n "$TARGET_PATH" ]; then
        echo "       (target repo path: $TARGET_PATH)"
    fi
    exit 1
fi

# shellcheck disable=SC2086
CODE_SHA=$(git $GIT_DIR_ARG log --diff-filter=ACDMR --format=%H "origin/main..HEAD" -- \
    ':!*.md' ':!.kit/context/' ':!.kit/tasks/' 2>/dev/null | head -1 || true)

NO_CODE_CHANGES=false
if [ -z "$CODE_SHA" ]; then
    # No code changes on this branch — Gates 2-3 will auto-pass
    NO_CODE_CHANGES=true
fi

# ─── Gate 1: CI green ───────────────────────────────────────────────
# Check all workflow runs for the latest commit (not just the first),
# so a passing run from one workflow can't mask a failure in another.
#
# KIT-0034 F4: GitHub takes a few seconds to register workflow runs after
# a push, so "no runs for the head SHA yet" is PENDING, not FAIL (twice a
# false alarm on KIT-0032 PR #56). Re-poll briefly before reporting. Runs
# still executing are also PENDING. Only a run that completed with a
# non-success conclusion FAILs (N3) — and it FAILs even when sibling
# workflows are still running.

CI_POLL_ATTEMPTS=3
CI_POLL_DELAY=5
CI_RUN_LIMIT=50
RUN_COUNT=0
LATEST_RUNS="[]"
CI_FETCH_OK=false
CI_ATTEMPT=1
CI_RAW_COUNT=0
while [ "$CI_ATTEMPT" -le "$CI_POLL_ATTEMPTS" ]; do
    # Reset per attempt so a failed refetch can't reuse a stale filter result
    LATEST_RUNS="[]"
    RUN_COUNT=0
    CI_RAW_COUNT=0
    # Query by commit (not a branch window) so runs for the head SHA can't
    # be pushed out of --limit by older reruns piling up on the branch.
    # The limit only truncates when ONE commit accumulates more runs than
    # the cap (matrix builds, reruns) — this repo runs ~2 workflows per
    # push, so 50 is generous headroom. The event filter happens BELOW,
    # not in the gh --jq, so the truncation guard sees the RAW returned
    # count — a cap-full response of mixed events must still trip the
    # guard (KIT-0043 F1).
    # Distinguish "gh succeeded with an empty list" (runs not registered
    # yet → PENDING) from "gh itself failed" (auth/network → FAIL below).
    # Exit status tested directly on the assignment (SC2181-safe).
    # shellcheck disable=SC2086
    if CI_RUNS=$(gh $GH_REPO_ARG run list --commit "$LATEST_SHA" --limit "$CI_RUN_LIMIT" --json status,conclusion,workflowName,event,headSha 2>/dev/null); then
        CI_FETCH_OK=true
    fi

    if [ -n "$CI_RUNS" ] && [ "$CI_RUNS" != "[]" ]; then
        CI_RAW_COUNT=$(echo "$CI_RUNS" | jq 'length' 2>/dev/null || echo "0")
        CI_RAW_COUNT="${CI_RAW_COUNT:-0}"
        # Filter to push/PR events for the PR head commit (not just the
        # newest run's SHA)
        LATEST_RUNS=$(echo "$CI_RUNS" | jq -c "[.[] | select((.event == \"push\" or .event == \"pull_request\") and .headSha == \"$LATEST_SHA\")]" 2>/dev/null || echo "[]")
        RUN_COUNT=$(echo "$LATEST_RUNS" | jq 'length' 2>/dev/null || echo "0")
        RUN_COUNT="${RUN_COUNT:-0}"
    fi

    if [ "$RUN_COUNT" -gt 0 ]; then
        break
    fi
    if [ "$CI_ATTEMPT" -lt "$CI_POLL_ATTEMPTS" ]; then
        sleep "$CI_POLL_DELAY"
    fi
    CI_ATTEMPT=$((CI_ATTEMPT + 1))
done

if [ "$RUN_COUNT" -eq 0 ]; then
    if [ "$CI_FETCH_OK" = true ]; then
        echo "GATE:1:CI:PENDING:No CI runs registered yet for ${LATEST_SHA:0:7} — re-run preflight shortly"
        ANY_PENDING=true
    else
        # Every attempt errored — a connectivity/auth problem, not "no runs
        # yet". Fail closed like Gate 4's could-not-fetch path.
        echo "GATE:1:CI:FAIL:Could not fetch CI runs (gh error) — check gh auth/network"
        ANY_FAILED=true
    fi
else
    CI_ALL_PASS=true
    CI_ANY_RUNNING=false
    CI_ANY_FAILED_RUN=false
    CI_DETAILS=""

    for i in $(seq 0 $((RUN_COUNT - 1))); do
        WF_NAME=$(echo "$LATEST_RUNS" | jq -r ".[$i].workflowName")
        WF_STATUS=$(echo "$LATEST_RUNS" | jq -r ".[$i].status")
        WF_CONCLUSION=$(echo "$LATEST_RUNS" | jq -r ".[$i].conclusion")

        if [ "$WF_STATUS" = "completed" ]; then
            if [ "$WF_CONCLUSION" = "success" ]; then
                CI_DETAILS="${CI_DETAILS}${WF_NAME}: pass; "
            elif [ "$WF_CONCLUSION" = "skipped" ] || [ "$WF_CONCLUSION" = "neutral" ]; then
                # GitHub treats skipped/neutral as success for dependent checks —
                # a path-filtered or conditionally skipped workflow is not a failure
                CI_DETAILS="${CI_DETAILS}${WF_NAME}: ${WF_CONCLUSION}; "
            else
                # Terminal non-success (failure, cancelled, timed_out,
                # action_required, stale, …) — a real CI failure.
                CI_DETAILS="${CI_DETAILS}${WF_NAME}: ${WF_CONCLUSION:-$WF_STATUS}; "
                CI_ALL_PASS=false
                CI_ANY_FAILED_RUN=true
            fi
        else
            # `completed` is the ONLY terminal status in the Actions API.
            # Everything else — in_progress, queued, waiting, requested,
            # pending, and any status GitHub adds later — is a run that
            # has not finished: PENDING, never FAIL (KIT-0043 F2; the
            # KIT-0034 pending-vs-failed distinction).
            CI_DETAILS="${CI_DETAILS}${WF_NAME}: ${WF_STATUS}; "
            CI_ALL_PASS=false
            CI_ANY_RUNNING=true
        fi
    done

    # Trim trailing "; "
    CI_DETAILS="${CI_DETAILS%; }"

    # F1 truncation guard: the query cannot return more than the --limit
    # cap, so a count AT the cap means runs may have been dropped — flag
    # it in the verdict — an at-cap response is indistinguishable from a
    # truncated one, so unseen runs may exist and a PASS would be
    # unverifiable. A visible failing run still wins (FAIL); otherwise
    # at-cap demotes the verdict to PENDING (never PASS) with the remedy
    # named. Keyed on the RAW returned count, not the post-filter count.
    CI_AT_CAP=false
    if [ "$CI_RAW_COUNT" -ge "$CI_RUN_LIMIT" ]; then
        CI_AT_CAP=true
        CI_DETAILS="${CI_DETAILS} (run count at query cap ${CI_RUN_LIMIT} — unseen runs may exist; raise CI_RUN_LIMIT or verify manually)"
    fi

    if [ "$CI_ANY_FAILED_RUN" = true ]; then
        echo "GATE:1:CI:FAIL:$CI_DETAILS"
        ANY_FAILED=true
    elif [ "$CI_AT_CAP" = true ]; then
        echo "GATE:1:CI:PENDING:$CI_DETAILS"
        ANY_PENDING=true
    elif [ "$CI_ALL_PASS" = true ]; then
        echo "GATE:1:CI:PASS:$CI_DETAILS"
    else
        echo "GATE:1:CI:PENDING:$CI_DETAILS (still running)"
        ANY_PENDING=true
    fi
fi

# ─── Shared PR review data (Gates 2, 3, 4) ──────────────────────────
# One GraphQL call fetches review events and review threads. Gate 2's
# fallback and Gate 4 must agree on the unresolved-thread count, so both
# read from the same snapshot. Empty counts (fetch/parse failure) make
# Gate 2's fallback fail closed and Gate 4 FAIL, as before.

PR_DATA=$(gh api graphql -f query="{ repository(owner: \"$OWNER\", name: \"$NAME\") { pullRequest(number: $PR_NUMBER) { reviews(last: 100) { nodes { author { login } state commit { oid } } } reviewThreads(first: 100) { nodes { isResolved } } } } }" 2>/dev/null || true)

THREAD_TOTAL=""
THREAD_RESOLVED=""
THREAD_UNRESOLVED=""
if [ -n "$PR_DATA" ]; then
    THREAD_TOTAL=$(echo "$PR_DATA" | jq '[.data.repository.pullRequest.reviewThreads.nodes[]] | length' 2>/dev/null || echo "")
    THREAD_RESOLVED=$(echo "$PR_DATA" | jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == true)] | length' 2>/dev/null || echo "")
    THREAD_UNRESOLVED=$(echo "$PR_DATA" | jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)] | length' 2>/dev/null || echo "")
fi

# ─── Gate 2: CodeRabbit reviewed the PR ──────────────────────────────
# Accepts review on CODE_SHA or LATEST_SHA (bots re-trigger on each push,
# so a review on HEAD covers all prior code even if the latest commit is
# a non-code chore push like review artifacts).
# Auto-passes for pure docs PRs (no code changes to review).

if bot_declared_absent coderabbit; then
    echo "GATE:2:CodeRabbit:SKIP:declared absent in kit-install (bots: $BOTS_DECLARED) — CodeRabbit is not expected on this project"
    SKIP_COUNT=$((SKIP_COUNT + 1))
elif [ "$NO_CODE_CHANGES" = true ]; then
    echo "GATE:2:CodeRabbit:PASS:No code changes — bot review not required"
else
    CR_REVIEW=$(echo "$PR_DATA" | jq -r ".data.repository.pullRequest.reviews.nodes[] | select(.commit.oid == \"$CODE_SHA\" or .commit.oid == \"$LATEST_SHA\") | select(.author.login | test(\"coderabbitai\")) | \"\(.author.login): \(.state)\"" 2>/dev/null | tail -1 || true)

    if [ -n "$CR_REVIEW" ]; then
        echo "GATE:2:CodeRabbit:PASS:$CR_REVIEW (on ${CODE_SHA:0:7} or ${LATEST_SHA:0:7})"
    else
        # Fallback (KIT-0034 F1): after a trivial/docs push CodeRabbit
        # refreshes its commit status and keeps an APPROVED review on an
        # earlier SHA without re-emitting a review event, so the strict
        # SHA match above false-negatives (KIT-0033 PR #58, KIT-0036
        # PR #63). Accept the PR as reviewed only when ALL hold (N1
        # keeps this fail-closed — no review at all, a CHANGES_REQUESTED
        # latest verdict, or any unresolved thread still FAILs):
        #   1. CodeRabbit's signal on the head SHA is passing — it
        #      reports via the legacy commit-status API (context
        #      "CodeRabbit"); check-runs are queried as a secondary
        #      source in case an install reports there instead;
        #   2. the latest CodeRabbit review on the PR is APPROVED, or
        #      COMMENTED with nothing left open;
        #   3. zero unresolved review threads (same count as Gate 4).
        CR_LATEST_STATE=$(echo "$PR_DATA" | jq -r "[.data.repository.pullRequest.reviews.nodes[] | select(.author.login | test(\"coderabbitai\"))] | last | .state // empty" 2>/dev/null || true)

        # The combined-status endpoint returns the latest status per context.
        # Require every CodeRabbit-matching context to be green (all() with an
        # explicit empty guard — all([]) is vacuously true); on a mixed result
        # surface the first non-success state in the FAIL detail.
        CR_SIGNAL=$(gh api "repos/$OWNER/$NAME/commits/$LATEST_SHA/status" \
            --jq '[.statuses[] | select(.context | test("coderabbit"; "i")) | .state] | if length == 0 then empty elif all(. == "success") then "success" else (map(select(. != "success")) | first) end' 2>/dev/null || true)
        if [ -z "$CR_SIGNAL" ]; then
            # Same all-green rule as the status branch: every matching
            # check run must be completed:success; otherwise surface the
            # first non-green "status:conclusion" in the FAIL detail.
            CR_SIGNAL=$(gh api "repos/$OWNER/$NAME/commits/$LATEST_SHA/check-runs" \
                --jq '[.check_runs[] | select(.app.slug | test("coderabbit")) | "\(.status):\(.conclusion)"] | if length == 0 then empty elif all(. == "completed:success") then "success" else (map(select(. != "completed:success")) | first) end' 2>/dev/null || true)
        fi

        CR_FALLBACK_OK=false
        if [ "$CR_SIGNAL" = "success" ] && [[ "$THREAD_UNRESOLVED" =~ ^[0-9]+$ ]] && [ "$THREAD_UNRESOLVED" -eq 0 ]; then
            if [ "$CR_LATEST_STATE" = "APPROVED" ] || [ "$CR_LATEST_STATE" = "COMMENTED" ]; then
                CR_FALLBACK_OK=true
            fi
        fi

        if [ "$CR_FALLBACK_OK" = true ]; then
            echo "GATE:2:CodeRabbit:PASS:CodeRabbit green on ${LATEST_SHA:0:7}, latest review $CR_LATEST_STATE, 0 unresolved threads (no review event on head — fallback)"
        else
            echo "GATE:2:CodeRabbit:FAIL:No review from coderabbitai[bot] on ${CODE_SHA:0:7} or ${LATEST_SHA:0:7} (fallback: signal=${CR_SIGNAL:-none}, latest review=${CR_LATEST_STATE:-none}, unresolved=${THREAD_UNRESOLVED:-unknown})"
            ANY_FAILED=true
        fi
    fi
fi

# ─── Gate 3: BugBot reviewed the PR ──────────────────────────────────
# BugBot quirk: when it finds no bugs, it reports as a check run
# ("Cursor Bugbot") instead of posting a review. Check both.
# Accepts review/check-run on CODE_SHA or LATEST_SHA.
# (No Gate-2-style status fallback needed here: BugBot re-emits its
# check-run on every push, so the head SHA always carries a signal.)

if bot_declared_absent bugbot; then
    echo "GATE:3:BugBot:SKIP:declared absent in kit-install (bots: $BOTS_DECLARED) — BugBot is not expected on this project"
    SKIP_COUNT=$((SKIP_COUNT + 1))
elif [ "$NO_CODE_CHANGES" = true ]; then
    echo "GATE:3:BugBot:PASS:No code changes — bot review not required"
else
    BB_REVIEW=$(echo "$PR_DATA" | jq -r ".data.repository.pullRequest.reviews.nodes[] | select(.commit.oid == \"$CODE_SHA\" or .commit.oid == \"$LATEST_SHA\") | select(.author.login | test(\"cursor\")) | \"\(.author.login): \(.state)\"" 2>/dev/null | tail -1 || true)

    if [ -n "$BB_REVIEW" ]; then
        echo "GATE:3:BugBot:PASS:$BB_REVIEW (on PR #$PR_NUMBER)"
    else
        # Fallback: check for BugBot check-run on CODE_SHA or LATEST_SHA (no-findings case)
        BB_CHECK=$(gh api "repos/$OWNER/$NAME/commits/$CODE_SHA/check-runs" \
            --jq '.check_runs[] | select(.app.slug == "cursor") | "\(.status):\(.conclusion)"' 2>/dev/null || true)

        if [ -z "$BB_CHECK" ] && [ "$CODE_SHA" != "$LATEST_SHA" ]; then
            BB_CHECK=$(gh api "repos/$OWNER/$NAME/commits/$LATEST_SHA/check-runs" \
                --jq '.check_runs[] | select(.app.slug == "cursor") | "\(.status):\(.conclusion)"' 2>/dev/null || true)
        fi

        if [ "$BB_CHECK" = "completed:success" ] || [ "$BB_CHECK" = "completed:neutral" ]; then
            echo "GATE:3:BugBot:PASS:check-run passed, no findings (on PR #$PR_NUMBER)"
        elif [ -n "$BB_CHECK" ]; then
            echo "GATE:3:BugBot:FAIL:check-run $BB_CHECK"
            ANY_FAILED=true
        else
            echo "GATE:3:BugBot:FAIL:No review or check-run from BugBot on ${CODE_SHA:0:7} or ${LATEST_SHA:0:7}"
            ANY_FAILED=true
        fi
    fi
fi

# ─── Gate 4: Zero unresolved threads ────────────────────────────────
# Counts come from the shared PR_DATA snapshot above, so this gate and
# Gate 2's fallback can never disagree about the unresolved count.

if [ -n "$PR_DATA" ]; then
    if [ -z "$THREAD_TOTAL" ] || [ -z "$THREAD_UNRESOLVED" ]; then
        echo "GATE:4:Threads:FAIL:Could not parse thread data"
        ANY_FAILED=true
    elif [ "$THREAD_UNRESOLVED" -eq 0 ]; then
        # reviewThreads(first: 100) — flag possible truncation at the cap
        _PF_TRUNC=""
        if [ "$THREAD_TOTAL" -eq 100 ]; then
            _PF_TRUNC=" (count capped at 100 — verify manually)"
        fi
        echo "GATE:4:Threads:PASS:Total: $THREAD_TOTAL, Resolved: $THREAD_RESOLVED, Unresolved: $THREAD_UNRESOLVED$_PF_TRUNC"
    else
        echo "GATE:4:Threads:FAIL:Total: $THREAD_TOTAL, Resolved: $THREAD_RESOLVED, Unresolved: $THREAD_UNRESOLVED"
        ANY_FAILED=true
    fi
else
    echo "GATE:4:Threads:FAIL:Could not fetch thread data"
    ANY_FAILED=true
fi

# ─── Gate 5: Evaluator review persisted ─────────────────────────────

# Match the canonical evaluator-output naming patterns:
#   <TASK>-evaluator-review*.md  (legacy)
#   <TASK>-code-review*.md       (current)
#   <TASK>-code-reviewer*.md     (alt — code-reviewer-fast variant)
# -type f -size +0c: an empty file (botched write, bare touch) is not a
# persisted review — require a non-empty regular file (KIT-0042).
EVAL_FILE=$(find .kit/context/reviews \
    \( -name "${TASK_ID}-evaluator-review*.md" \
    -o -name "${TASK_ID}-code-review*.md" \
    -o -name "${TASK_ID}-code-reviewer*.md" \) \
    -type f -size +0c \
    2>/dev/null | head -1 || true)

if [ -n "$EVAL_FILE" ]; then
    echo "GATE:5:Evaluator:PASS:$EVAL_FILE"
else
    echo "GATE:5:Evaluator:FAIL:No evaluator review found for $TASK_ID (bundled PR? each task needs its own pointer record named .kit/context/reviews/${TASK_ID}-evaluator-review.md — see the review-handoff skill. Multi-PR task? artifacts may live on the sibling PR's branch until it merges.)"
    ANY_FAILED=true
fi

# ─── Gate 6: Review starter exists ──────────────────────────────────

STARTER_FILE=$(find .kit/context -maxdepth 1 -name "${TASK_ID}-REVIEW-STARTER.md" -type f -size +0c 2>/dev/null | head -1 || true)

if [ -n "$STARTER_FILE" ]; then
    echo "GATE:6:ReviewStarter:PASS:$STARTER_FILE"
else
    echo "GATE:6:ReviewStarter:FAIL:No review starter found for $TASK_ID (bundled PR? each task needs its own pointer starter named .kit/context/${TASK_ID}-REVIEW-STARTER.md — see the review-handoff skill. Multi-PR task? artifacts may live on the sibling PR's branch until it merges.)"
    ANY_FAILED=true
fi

# ─── Gate 7: Task in correct folder ─────────────────────────────────

# "${TASK_ID}-*": task files are named <ID>-slug.md — the "-" is the
# boundary that stops KIT-4 matching KIT-40's file (KIT-0043 F3, same
# bug-class as the Gate 5/6 separators). `sort` makes the multi-match
# pick deterministic instead of filesystem-order arbitrary.
TASK_FILE=$(find .kit/tasks/3-in-progress .kit/tasks/4-in-review -name "${TASK_ID}-*" -type f -size +0c 2>/dev/null | LC_ALL=C sort | head -1 || true)

if [ -n "$TASK_FILE" ]; then
    echo "GATE:7:TaskFolder:PASS:$TASK_FILE"
else
    echo "GATE:7:TaskFolder:FAIL:$TASK_ID not in 3-in-progress or 4-in-review"
    ANY_FAILED=true
fi

# ─── Final verdict ──────────────────────────────────────────────────

# Emit progress event (optional, fire-and-forget — requires dispatch-kit)
if command -v dispatch >/dev/null 2>&1; then
    if [ "$ANY_FAILED" = true ]; then
        _PF_SUMMARY="FAIL ($TASK_ID, PR #$PR_NUMBER)"
    elif [ "$ANY_PENDING" = true ]; then
        _PF_SUMMARY="PENDING — no failures, re-run shortly ($TASK_ID, PR #$PR_NUMBER)"
    elif [ "$SKIP_COUNT" -gt 0 ]; then
        # F4 (loud everywhere): a pass with declaration-skipped gates
        # names the degraded mode — never "all 7 passed"
        _PF_SUMMARY="PASS — gates passed, $SKIP_COUNT skipped by bot declaration ($TASK_ID, PR #$PR_NUMBER)"
    else
        _PF_SUMMARY="PASS — All 7 gates passed ($TASK_ID, PR #$PR_NUMBER)"
    fi
    dispatch emit preflight_checked --agent preflight-check \
        --task "$TASK_ID" \
        --summary "$_PF_SUMMARY" >/dev/null 2>&1 || true
fi

if [ "$ANY_FAILED" = true ]; then
    exit 1
elif [ "$ANY_PENDING" = true ]; then
    exit 2
else
    exit 0
fi

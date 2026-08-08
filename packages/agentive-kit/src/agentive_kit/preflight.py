"""The 7-gate preflight completion check (KIT-0091 F1/F2).

Port of ``scripts/core/preflight-check.sh`` v1.3.0. This is GATE code:
it decides when a task may request human review, and a parity bug here
weakens the workflow's trust silently — so the port is bound to the
committed behavior matrix in ``tests/test_preflight_check.py``, which
drives the bash original and this module through identical stub-``gh``
scenarios. Behavior is the contract; the code shape below is free
(task spec F2).

Output contract (machine-parsed by /preflight, babysit-pr, and the
parity harness)::

    GATE:<number>:<name>:PASS|FAIL|PENDING|SKIP:<detail>

Exit codes: 0 all gates satisfied (SKIP counts), 1 any failure or
error, 2 no failure but at least one gate PENDING (re-run shortly).

Verdict semantics carried over intact:

- PENDING (KIT-0034 F4): the gate cannot be evaluated yet — CI runs
  not registered for the head SHA, or still executing. Gate 1's at-cap
  rule (KIT-0043 F1, REVIEW-INSIGHTS "Preflight Gate 1 at-cap
  semantics"): a raw run count AT the query cap is indistinguishable
  from a truncated response, so all-green at the cap demotes to
  PENDING, never PASS; a visible failing run still wins (FAIL).
- SKIP (KIT-0056, ADR-0027 P5): a ``bots:`` declaration in CLAUDE.md's
  kit-install region declares a bot absent, so Gates 2/3 SKIP with the
  declaration named — never FAIL, never a silent PASS. Invalid or
  empty declarations fail closed to expecting both bots, loudly.

Documented divergences from the bash original (each named in the
KIT-0091 PR body; everything else is matrix-pinned):

- The ``bots:`` declaration is read in-package (``agentive_kit
  .markers``, conformance-pinned to ``scripts/local/kit_markers.py``)
  instead of shelling out to that script — the bash version silently
  skipped the declaration when the script or python3 was missing.
- Gate 5's multi-match pick is sorted (deterministic) where the bash
  ``find | head -1`` was filesystem-order arbitrary; Gate 7 already
  sorted and keeps doing so.
- The CI poll delay honors ``PREFLIGHT_CI_POLL_DELAY`` (seconds) — the
  test seam analogous to the bash version's PATH-stubbable ``sleep``
  binary.
- The local ``jq`` binary dependency is gone: run-list filtering and
  thread counts parse natively. The ``--jq`` filters passed TO ``gh``
  are byte-identical to the bash version's.
"""

from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from agentive_kit import ghio, gitio, markers
from agentive_kit.models import GateResult
from agentive_kit.root import RootNotFoundError, find_project_root

# Seam for the parity harness (mirrors the bash script's stubbable
# `sleep` binary): tests patch this to keep PENDING re-poll scenarios
# instant.
_sleep = time.sleep

CI_POLL_ATTEMPTS = 3
CI_POLL_DELAY = 5
CI_RUN_LIMIT = 50

# --jq programs executed BY gh (byte-identical to the bash original —
# the parity matrix's jq-semantics test runs real jq over this string).
# The combined-status endpoint returns the latest status per context;
# require every CodeRabbit-matching context green (all() with an
# explicit empty guard — all([]) is vacuously true); on a mixed result
# surface the first non-success state.
CR_STATUS_JQ = (
    '[.statuses[] | select(.context | test("coderabbit"; "i")) | .state] '
    '| if length == 0 then empty elif all(. == "success") then "success" '
    'else (map(select(. != "success")) | first) end'
)
CR_CHECK_RUNS_JQ = (
    '[.check_runs[] | select(.app.slug | test("coderabbit")) '
    '| "\\(.status):\\(.conclusion)"] '
    '| if length == 0 then empty elif all(. == "completed:success") then "success" '
    'else (map(select(. != "completed:success")) | first) end'
)
BB_CHECK_RUNS_JQ = (
    '.check_runs[] | select(.app.slug == "cursor") | "\\(.status):\\(.conclusion)"'
)

# Help text byte-identical to the bash original's --help output (the
# adjacent-literal splits below only dodge the line-length lint).
_USAGE_HEAD = (
    "Usage: ./scripts/core/preflight-check.sh [--pr PR_NUMBER] "
    "[--task TASK_ID] [--repo owner/name]"
)

_HELP = (
    f"{_USAGE_HEAD}\n"
    "\n"
    "Run all 7 preflight gates for a PR before human review.\n"
    "\n"
    "Options:\n"
    "  --pr PR_NUMBER      PR number to check (default: auto-detect)\n"
    "  --task TASK_ID      Task ID, e.g. TASK-0001 (default: derived from branch)\n"
    "  --repo owner/name   Target GitHub repo (overrides CLAUDE.md "
    "## Target Repository)\n"
    "  --help, -h          Show this help message\n"
    "\n"
    "Gates:\n"
    "  1. CI green                    GitHub Actions passing\n"
    "  2. CodeRabbit reviewed          coderabbitai[bot] reviewed latest "
    "code commit\n"
    "  3. BugBot reviewed              cursor[bot] reviewed latest code commit\n"
    "     (Gates 2/3 SKIP when a 'bots:' line in CLAUDE.md's kit-install\n"
    "      region declares the bot absent — e.g. 'bots: none')\n"
    "  4. Zero unresolved threads      All review threads resolved\n"
    "  5. Evaluator review persisted   .kit/context/reviews/<TASK>-"
    "{evaluator-review,code-review,code-reviewer}*.md\n"
    "  6. Review starter exists         .kit/context/<TASK>-REVIEW-STARTER.md\n"
    "  7. Task in correct folder        .kit/tasks/3-in-progress or 4-in-review\n"
    "\n"
    "Exit codes:\n"
    "  0  All gates pass\n"
    "  1  One or more gates fail\n"
    "  2  No failures, but at least one gate PENDING (re-run shortly)"
)


@dataclass
class _Args:
    pr: str = ""
    task: str = ""
    repo: str = ""


@dataclass
class _TargetRepo:
    """Cross-repo routing resolved from --repo or CLAUDE.md (ID2-0014)."""

    repo: str = ""  # owner/name; empty in single-repo mode
    path: str = ""  # local working-tree path; empty unless CLAUDE.md set it


def _parse_args(argv: list[str]) -> _Args:
    """Faithful port of the bash flag loop (last flag wins; exact
    refusal messages and streams)."""
    args = _Args()
    i = 0
    while i < len(argv):
        arg = argv[i]
        nxt = argv[i + 1] if i + 1 < len(argv) else ""
        # membership: flag-alias vocabulary check, not identifier
        # equality (same for the flag names below)
        if arg in ("--help", "-h"):
            print(_HELP)
            sys.exit(0)
        elif arg == "--pr":
            if not nxt or nxt.startswith("-"):
                print("ERROR: --pr requires a PR number")
                sys.exit(1)
            args.pr = nxt
            i += 2
        elif arg == "--task":
            if not nxt or nxt.startswith("-"):
                print("ERROR: --task requires a task ID")
                sys.exit(1)
            args.task = nxt
            i += 2
        elif arg == "--repo":
            if not nxt or nxt.startswith("-"):
                print("ERROR: --repo requires an owner/name value", file=sys.stderr)
                sys.exit(1)
            args.repo = nxt
            i += 2
        elif arg.startswith("--repo="):
            args.repo = arg.removeprefix("--repo=")
            if not args.repo:
                print("ERROR: --repo= requires an owner/name value", file=sys.stderr)
                sys.exit(1)
            i += 1
        elif arg.startswith("-"):
            print(f"Unknown option: {arg}")
            print("Run: ./scripts/core/preflight-check.sh --help")
            sys.exit(1)
        else:
            print(f"Unknown argument: {arg}")
            print("Run: ./scripts/core/preflight-check.sh --help")
            sys.exit(1)
    return args


def _parse_target_repo(root: Path, override: str) -> _TargetRepo:
    """Port of lib/target_repo.sh: --repo override wins over CLAUDE.md's
    ``## Target Repository`` section; the section is optional."""
    target = _TargetRepo()
    if override:
        target.repo = override
        # Path stays empty on override: the caller knows the repo but
        # not necessarily the local working tree.
    else:
        claude_md = root / "CLAUDE.md"
        if claude_md.is_file():
            try:
                text = claude_md.read_text(encoding="utf-8")
            except OSError:
                text = ""
            # \r? before $: the bash awk header pattern ended in
            # [[:space:]]* which swallowed a CR, so CRLF-checked-out
            # CLAUDE.md files parsed there — they must parse here too
            # (o3, PR 1 round 2).
            section_match = re.search(
                r"^## Target Repository[ \t]*\r?$(.*?)(?=^## |\Z)",
                text,
                re.MULTILINE | re.DOTALL,
            )
            if section_match:
                # Per-LINE matching, like the sed originals: a
                # multiline regex here lets [^`]* cross the newline and
                # capture garbage between two bullets (caught by
                # test_preflight_pkg.py). Greedy .* before the backtick
                # keeps sed's last-span-on-the-line pick; first
                # matching line wins (head -1).
                for line in section_match.group(1).splitlines():
                    if not target.repo:
                        gh_match = re.match(r"- \*\*GitHub\*\*:.*`([^`]*)`", line)
                        if gh_match:
                            target.repo = gh_match.group(1)
                    if not target.path:
                        path_match = re.match(r"- \*\*Path\*\*:.*`([^`]*)`", line)
                        if path_match:
                            target.path = path_match.group(1)

    # Layer 1 of two (both ported from bash): this is target_repo.sh's
    # looser shape check. The STRICT charset validation in main() —
    # ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ — re-validates every slug,
    # whatever its source, and MUST keep running before OWNER/NAME are
    # interpolated into the GraphQL query (KIT-0043, o3; claude-code
    # evaluator this PR). Never route a slug to gh without passing
    # through main()'s check.
    if target.repo and not re.match(r"^[^/\s]+/[^/\s]+$", target.repo):
        print(
            f"ERROR: target repo must be in owner/name format, got: '{target.repo}'",
            file=sys.stderr,
        )
        sys.exit(1)

    if target.path:
        tree = Path(root, target.path)
        if not (tree / ".git").is_dir() and not (tree / ".git").is_file():
            print(
                f"WARNING: TARGET_PATH '{target.path}' is not a git working tree "
                "— git operations via $GIT_DIR_ARG will fail",
                file=sys.stderr,
            )
    return target


def _read_bots_declaration(root: Path) -> tuple[str, bool]:
    """(normalized declaration, line-present) from CLAUDE.md's
    kit-install region (KIT-0056, ADR-0027 P5).

    Absent line/region/file = ``("", False)`` — both bots expected (fail
    closed). Same comma/space/case tolerance as every other bots reader
    (door normalize_bots, project _normalize_bots): one declaration must
    never be valid to one reader and invalid to another.
    """
    claude_md = root / "CLAUDE.md"
    if not claude_md.is_file():
        return "", False
    try:
        text = claude_md.read_text(encoding="utf-8")
    except OSError:
        return "", False
    region = markers.extract_region(text, "kit-install")
    if region is None:
        return "", False
    declared = ""
    present = False
    for line in region.splitlines():
        # leading-whitespace tolerant like the other readers' strip()
        if re.match(r"^[ \t]*bots:", line):
            present = True
            # FIRST bots: line wins — the bash reader was
            # `sed -n ... | head -1` (unlike flag parsing, where the
            # last flag wins).
            if not declared:
                declared = re.sub(r"^[ \t]*bots:[ \t]*", "", line)
    declared = declared.replace(",", " ").lower()
    return declared, present


def _validate_bots(declared: str, present: bool) -> str:
    """Normalize/validate the declaration; emit the fail-closed NOTICEs.

    Returns the validated single-space-separated declaration, or ""
    (both bots expected). An unrecognized token or a 'none' combined
    with a bot name must not silently SKIP a gate — fail closed and say
    so (the bash original's exact messages).
    """
    noticed = False
    if declared:
        tokens = [t for t in declared.split() if t]
        # membership: declared bot-token vocabulary checks ('none' must
        # be the sole token), not identifier equality
        valid = all(t in ("coderabbit", "bugbot", "none") for t in tokens)
        declared = " ".join(tokens)
        if valid and declared and "none" in tokens and declared != "none":
            valid = False
        if not valid:
            print(
                f"NOTICE: invalid bots declaration in kit-install "
                f"('bots: {declared}') — expecting both bots (fail closed); "
                f"fix the line in CLAUDE.md"
            )
            declared = ""
            noticed = True
    if present and not declared and not noticed:
        # A PRESENT-but-valueless bots: line is invalid, not absent —
        # doctor FAILs it (bots-record), so reading it as "no
        # declaration" here would let the two readers diverge. Checked
        # AFTER normalization so a value that reduces to nothing (a
        # lone ',') is caught too.
        print(
            "NOTICE: empty bots declaration in kit-install ('bots:' with no "
            "value) — expecting both bots (fail closed); fix the line in "
            "CLAUDE.md"
        )
    return declared


def _bot_declared_absent(declared: str, bot: str) -> bool:
    if not declared:
        return False
    if declared == "none":
        return True
    # membership: token presence in the declaration list, not
    # identifier equality
    return bot not in declared.split()


def _poll_delay() -> float:
    """CI re-poll delay in seconds, clamped to be sleep-safe.

    ``PREFLIGHT_CI_POLL_DELAY`` is the test seam (the analogue of the
    bash script's PATH-stubbable ``sleep`` binary). Gate code never
    crashes on a bad value: non-numeric falls back to the default,
    negative clamps to 0 (``time.sleep`` raises on negatives — o3,
    PR 1 round 2).
    """
    try:
        delay = float(os.environ.get("PREFLIGHT_CI_POLL_DELAY", CI_POLL_DELAY))
    except ValueError:
        delay = float(CI_POLL_DELAY)
    # float() accepts "nan"/"inf" without ValueError: nan escapes the
    # max() clamp into time.sleep (ValueError), inf hangs the run
    # forever — both fall back like any other bad value (CodeRabbit,
    # PR #112).
    if not math.isfinite(delay):
        delay = float(CI_POLL_DELAY)
    return max(0.0, delay)


def _gh_text(result: subprocess.CompletedProcess | None) -> str:
    """stdout of a successful gh call, else "" (the bash `|| true`)."""
    if result is None or result.returncode != 0:
        return ""
    return result.stdout.rstrip("\n")


def _gate_1_ci(latest_sha: str, repo_flag: str | None) -> GateResult:
    """CI green — every workflow run for the head commit (KIT-0034/0043).

    Query by commit so runs can't be pushed out of --limit by older
    reruns on the branch; filter to push/pull_request events for the
    head SHA below (NOT in the gh --jq) so the truncation guard sees
    the RAW returned count (KIT-0043 F1).
    """
    poll_delay = _poll_delay()

    fetch_ok = False
    raw_count = 0
    runs: list[dict] = []
    for attempt in range(1, CI_POLL_ATTEMPTS + 1):
        raw_count = 0
        runs = []
        result = ghio.run_gh(
            "run",
            "list",
            "--commit",
            latest_sha,
            "--limit",
            str(CI_RUN_LIMIT),
            "--json",
            "status,conclusion,workflowName,event,headSha",
            repo=repo_flag,
        )
        if result is not None and result.returncode == 0:
            # Deliberately sticky: one successful fetch proves gh/auth
            # work, so a later transient error still reads as "no runs
            # registered yet" (PENDING), not a connectivity FAIL.
            fetch_ok = True
            try:
                parsed = json.loads(result.stdout or "[]")
            except json.JSONDecodeError:
                parsed = []
            if isinstance(parsed, list):
                raw_count = len(parsed)
                runs = [
                    r
                    for r in parsed
                    if isinstance(r, dict)
                    # membership: GitHub event vocabulary filter, not
                    # identifier equality
                    and r.get("event") in ("push", "pull_request")
                    and r.get("headSha") == latest_sha
                ]
        if runs:
            break
        if attempt < CI_POLL_ATTEMPTS:
            _sleep(poll_delay)

    if not runs:
        if fetch_ok:
            return GateResult(
                1,
                "CI",
                "PENDING",
                f"No CI runs registered yet for {latest_sha[:7]} — re-run "
                "preflight shortly",
            )
        # Every attempt errored — connectivity/auth, not "no runs yet".
        # Fail closed like Gate 4's could-not-fetch path.
        return GateResult(
            1,
            "CI",
            "FAIL",
            "Could not fetch CI runs (gh error) — check gh auth/network",
        )

    all_pass = True
    any_failed_run = False
    details: list[str] = []
    for run in runs:
        name = run.get("workflowName")
        status = run.get("status")
        conclusion = run.get("conclusion")
        # jq -r renders JSON null as the string "null"; mirror it so a
        # conclusion-less completed run reports identically.
        conclusion = "null" if conclusion is None else str(conclusion)
        if status == "completed":
            if conclusion == "success":
                details.append(f"{name}: pass")
            # membership: the conclusion vocabulary GitHub treats as
            # success for dependent checks
            elif conclusion in ("skipped", "neutral"):
                # GitHub treats skipped/neutral as success for dependent
                # checks — a path-filtered workflow is not a failure.
                details.append(f"{name}: {conclusion}")
            else:
                # Terminal non-success (failure, cancelled, timed_out,
                # action_required, stale, …) — a real CI failure.
                details.append(f"{name}: {conclusion or status}")
                all_pass = False
                any_failed_run = True
        else:
            # `completed` is the ONLY terminal status in the Actions
            # API; anything else — including statuses GitHub adds later
            # — is a run that has not finished: PENDING, never FAIL
            # (KIT-0043 F2).
            details.append(f"{name}: {status}")
            all_pass = False

    detail = "; ".join(details)
    at_cap = raw_count >= CI_RUN_LIMIT
    if at_cap:
        # An at-cap response is indistinguishable from a truncated one —
        # unseen runs may exist, so a PASS would be unverifiable.
        detail += (
            f" (run count at query cap {CI_RUN_LIMIT} — unseen runs may "
            "exist; raise CI_RUN_LIMIT or verify manually)"
        )

    if any_failed_run:
        return GateResult(1, "CI", "FAIL", detail)
    if at_cap:
        return GateResult(1, "CI", "PENDING", detail)
    if all_pass:
        return GateResult(1, "CI", "PASS", detail)
    return GateResult(1, "CI", "PENDING", f"{detail} (still running)")


def _fetch_pr_data(owner: str, name: str, pr_number: str) -> dict | None:
    """One GraphQL call feeding Gates 2, 3 and 4 — Gate 2's fallback and
    Gate 4 must agree on the unresolved count, so both read one
    snapshot."""
    query = (
        f'{{ repository(owner: "{owner}", name: "{name}") '
        f"{{ pullRequest(number: {pr_number}) "
        "{ reviews(last: 100) { nodes { author { login } state commit { oid } } } "
        "reviewThreads(first: 100) { nodes { isResolved } } } } }"
    )
    text = _gh_text(ghio.run_gh("api", "graphql", "-f", f"query={query}"))
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _pr_reviews(pr_data: dict | None) -> list[dict]:
    try:
        nodes = pr_data["data"]["repository"]["pullRequest"]["reviews"]["nodes"]
    except (KeyError, TypeError):
        return []
    return [n for n in nodes if isinstance(n, dict)]


def _thread_counts(pr_data: dict | None) -> tuple[int | None, int | None, int | None]:
    """(total, resolved, unresolved) or Nones when unparseable."""
    try:
        nodes = pr_data["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"]
        total = len(nodes)
        resolved = len([n for n in nodes if n.get("isResolved") is True])
        unresolved = len([n for n in nodes if n.get("isResolved") is False])
    except (KeyError, TypeError, AttributeError):
        return None, None, None
    return total, resolved, unresolved


def _last_review_on(reviews: list[dict], author_re: str, shas: tuple[str, ...]) -> str:
    """Last "login: STATE" among reviews on one of *shas* by an author
    matching *author_re* (the bash jq select | tail -1)."""
    found = ""
    for review in reviews:
        oid = (review.get("commit") or {}).get("oid")
        login = (review.get("author") or {}).get("login") or ""
        if oid in shas and re.search(author_re, login):
            found = f"{login}: {review.get('state')}"
    return found


def _gate_2_coderabbit(
    *,
    declared: str,
    no_code_changes: bool,
    reviews: list[dict],
    code_sha: str,
    latest_sha: str,
    unresolved: int | None,
    owner: str,
    name: str,
) -> GateResult:
    """CodeRabbit reviewed the PR — primary SHA match, then the KIT-0034
    F1 fallback (commit-status green + latest review APPROVED/COMMENTED
    + zero unresolved threads), which stays fail-closed (N1)."""
    if _bot_declared_absent(declared, "coderabbit"):
        return GateResult(
            2,
            "CodeRabbit",
            "SKIP",
            f"declared absent in kit-install (bots: {declared}) — CodeRabbit "
            "is not expected on this project",
        )
    if no_code_changes:
        return GateResult(
            2, "CodeRabbit", "PASS", "No code changes — bot review not required"
        )

    cr_review = _last_review_on(reviews, "coderabbitai", (code_sha, latest_sha))
    if cr_review:
        return GateResult(
            2,
            "CodeRabbit",
            "PASS",
            f"{cr_review} (on {code_sha[:7]} or {latest_sha[:7]})",
        )

    # Fallback: after a trivial/docs push CodeRabbit refreshes its commit
    # status and keeps an APPROVED review on an earlier SHA without
    # re-emitting a review event (KIT-0033 PR #58, KIT-0036 PR #63).
    cr_latest_state = ""
    for review in reviews:
        login = (review.get("author") or {}).get("login") or ""
        if re.search("coderabbitai", login):
            cr_latest_state = review.get("state") or ""

    cr_signal = _gh_text(
        ghio.run_gh(
            "api",
            f"repos/{owner}/{name}/commits/{latest_sha}/status",
            "--jq",
            CR_STATUS_JQ,
        )
    )
    if not cr_signal:
        # Secondary source, in case an install reports via check-runs.
        cr_signal = _gh_text(
            ghio.run_gh(
                "api",
                f"repos/{owner}/{name}/commits/{latest_sha}/check-runs",
                "--jq",
                CR_CHECK_RUNS_JQ,
            )
        )

    fallback_ok = (
        cr_signal == "success"
        and unresolved == 0
        # membership: accepted review-state vocabulary, not identifier
        # equality
        and cr_latest_state in ("APPROVED", "COMMENTED")
    )
    if fallback_ok:
        return GateResult(
            2,
            "CodeRabbit",
            "PASS",
            f"CodeRabbit green on {latest_sha[:7]}, latest review "
            f"{cr_latest_state}, 0 unresolved threads (no review event on "
            "head — fallback)",
        )
    unresolved_str = "unknown" if unresolved is None else str(unresolved)
    return GateResult(
        2,
        "CodeRabbit",
        "FAIL",
        f"No review from coderabbitai[bot] on {code_sha[:7]} or "
        f"{latest_sha[:7]} (fallback: signal={cr_signal or 'none'}, latest "
        f"review={cr_latest_state or 'none'}, unresolved={unresolved_str})",
    )


def _gate_3_bugbot(
    *,
    declared: str,
    no_code_changes: bool,
    reviews: list[dict],
    code_sha: str,
    latest_sha: str,
    pr_number: str,
    owner: str,
    name: str,
) -> GateResult:
    """BugBot reviewed the PR — review event, else the no-findings
    check-run (BugBot reports "Cursor Bugbot" as a check run when it
    finds nothing)."""
    if _bot_declared_absent(declared, "bugbot"):
        return GateResult(
            3,
            "BugBot",
            "SKIP",
            f"declared absent in kit-install (bots: {declared}) — BugBot is "
            "not expected on this project",
        )
    if no_code_changes:
        return GateResult(
            3, "BugBot", "PASS", "No code changes — bot review not required"
        )

    bb_review = _last_review_on(reviews, "cursor", (code_sha, latest_sha))
    if bb_review:
        return GateResult(3, "BugBot", "PASS", f"{bb_review} (on PR #{pr_number})")

    bb_check = _gh_text(
        ghio.run_gh(
            "api",
            f"repos/{owner}/{name}/commits/{code_sha}/check-runs",
            "--jq",
            BB_CHECK_RUNS_JQ,
        )
    )
    if not bb_check and code_sha != latest_sha:
        bb_check = _gh_text(
            ghio.run_gh(
                "api",
                f"repos/{owner}/{name}/commits/{latest_sha}/check-runs",
                "--jq",
                BB_CHECK_RUNS_JQ,
            )
        )

    # Documented divergence (KIT-0091, o3 finding): the jq filter emits
    # ONE LINE PER cursor check-run, and the bash original compared the
    # whole blob against a single "completed:success" — so matrix jobs
    # or re-runs that were ALL green still false-FAILed the gate (and
    # the embedded newline corrupted the one-line GATE format). The
    # port applies the same all-green rule Gate 2's check-run fallback
    # already uses: every run green ⇒ PASS; otherwise FAIL naming the
    # first non-green state. Fail-closed is preserved — no non-green
    # combination can PASS.
    bb_states = [line for line in bb_check.splitlines() if line]
    # membership: green check-run state vocabulary, not identifier
    # equality (same for the first-non-green pick below)
    if bb_states and all(
        state in ("completed:success", "completed:neutral") for state in bb_states
    ):
        return GateResult(
            3,
            "BugBot",
            "PASS",
            f"check-run passed, no findings (on PR #{pr_number})",
        )
    if bb_states:
        first_bad = next(
            state
            for state in bb_states
            if state not in ("completed:success", "completed:neutral")
        )
        return GateResult(3, "BugBot", "FAIL", f"check-run {first_bad}")
    return GateResult(
        3,
        "BugBot",
        "FAIL",
        f"No review or check-run from BugBot on {code_sha[:7]} or {latest_sha[:7]}",
    )


def _gate_4_threads(
    pr_data: dict | None,
    total: int | None,
    resolved: int | None,
    unresolved: int | None,
) -> GateResult:
    """Zero unresolved threads — counts from the shared snapshot, so
    this gate and Gate 2's fallback can never disagree."""
    if pr_data is None:
        return GateResult(4, "Threads", "FAIL", "Could not fetch thread data")
    if total is None or unresolved is None:
        return GateResult(4, "Threads", "FAIL", "Could not parse thread data")
    if unresolved == 0:
        # reviewThreads(first: 100) — flag possible truncation at the cap
        trunc = " (count capped at 100 — verify manually)" if total == 100 else ""
        return GateResult(
            4,
            "Threads",
            "PASS",
            f"Total: {total}, Resolved: {resolved}, Unresolved: {unresolved}{trunc}",
        )
    return GateResult(
        4,
        "Threads",
        "FAIL",
        f"Total: {total}, Resolved: {resolved}, Unresolved: {unresolved}",
    )


def _first_nonempty_file(candidates: list[Path]) -> Path | None:
    for path in candidates:
        try:
            if path.is_file() and path.stat().st_size > 0:
                return path
        except OSError:
            continue
    return None


def _gate_5_evaluator(root: Path, task_id: str) -> GateResult:
    """Evaluator review persisted — canonical output naming patterns;
    an empty file (botched write, bare touch) is not a persisted review
    (KIT-0042). Sorted pick: deterministic where find|head-1 was
    filesystem-order arbitrary (documented divergence)."""
    reviews_dir = root / ".kit" / "context" / "reviews"
    matches: set[Path] = set()
    if reviews_dir.is_dir():
        for pattern in (
            f"{task_id}-evaluator-review*.md",
            f"{task_id}-code-review*.md",
            f"{task_id}-code-reviewer*.md",
        ):
            matches.update(reviews_dir.rglob(pattern))
    found = _first_nonempty_file(sorted(matches))
    if found:
        return GateResult(5, "Evaluator", "PASS", str(found.relative_to(root)))
    return GateResult(
        5,
        "Evaluator",
        "FAIL",
        f"No evaluator review found for {task_id} (bundled PR? each task "
        "needs its own pointer record named "
        f".kit/context/reviews/{task_id}-evaluator-review.md — see the "
        "review-handoff skill. Multi-PR task? artifacts may live on the "
        "sibling PR's branch until it merges.)",
    )


def _gate_6_starter(root: Path, task_id: str) -> GateResult:
    context_dir = root / ".kit" / "context"
    candidates = (
        sorted(context_dir.glob(f"{task_id}-REVIEW-STARTER.md"))
        if context_dir.is_dir()
        else []
    )
    found = _first_nonempty_file(candidates)
    if found:
        return GateResult(6, "ReviewStarter", "PASS", str(found.relative_to(root)))
    return GateResult(
        6,
        "ReviewStarter",
        "FAIL",
        f"No review starter found for {task_id} (bundled PR? each task needs "
        f"its own pointer starter named .kit/context/{task_id}-REVIEW-STARTER.md "
        "— see the review-handoff skill. Multi-PR task? artifacts may live on "
        "the sibling PR's branch until it merges.)",
    )


def _gate_7_task_folder(root: Path, task_id: str) -> GateResult:
    """Task in 3-in-progress or 4-in-review. "{task}-*": the "-" is the
    boundary that stops KIT-4 matching KIT-40's file (KIT-0043 F3);
    sorted pick keeps the multi-match choice deterministic."""
    candidates: list[Path] = []
    for folder in ("3-in-progress", "4-in-review"):
        tasks_dir = root / ".kit" / "tasks" / folder
        if tasks_dir.is_dir():
            candidates.extend(tasks_dir.rglob(f"{task_id}-*"))
    found = _first_nonempty_file(sorted(candidates, key=str))
    if found:
        return GateResult(7, "TaskFolder", "PASS", str(found.relative_to(root)))
    return GateResult(
        7, "TaskFolder", "FAIL", f"{task_id} not in 3-in-progress or 4-in-review"
    )


def _emit_dispatch_event(
    task_id: str, pr_number: str, any_failed: bool, any_pending: bool, skip_count: int
) -> None:
    """Fire-and-forget progress event (requires dispatch-kit)."""
    if shutil.which("dispatch") is None:
        return
    if any_failed:
        summary = f"FAIL ({task_id}, PR #{pr_number})"
    elif any_pending:
        summary = f"PENDING — no failures, re-run shortly ({task_id}, PR #{pr_number})"
    elif skip_count > 0:
        # Loud everywhere (KIT-0056 F4): a pass with declaration-skipped
        # gates names the degraded mode — never "all 7 passed".
        summary = (
            f"PASS — gates passed, {skip_count} skipped by bot declaration "
            f"({task_id}, PR #{pr_number})"
        )
    else:
        summary = f"PASS — All 7 gates passed ({task_id}, PR #{pr_number})"
    try:
        subprocess.run(
            [
                "dispatch",
                "emit",
                "preflight_checked",
                "--agent",
                "preflight-check",
                "--task",
                task_id,
                "--summary",
                summary,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            timeout=30,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        pass


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(sys.argv[1:] if argv is None else argv)

    if not ghio.gh_available():
        print("ERROR: gh CLI (gh) not installed")
        print("Install: https://cli.github.com/")
        sys.exit(1)
    if not ghio.auth_ok():
        print("ERROR: gh CLI not authenticated")
        print("Run: gh auth login")
        sys.exit(1)

    try:
        root = find_project_root()
    except RootNotFoundError as exc:
        print(exc)
        sys.exit(1)

    target = _parse_target_repo(root, args.repo)

    # Detect repo owner/name — prefer the configured target repo.
    if target.repo:
        repo = target.repo
    else:
        repo = ghio.default_repo_slug() or ""
        if not repo:
            print("ERROR: Could not determine GitHub repository")
            print("Run: gh repo set-default")
            sys.exit(1)

    # Validate the slug shape wherever it came from before OWNER/NAME
    # are interpolated into a GraphQL query string (KIT-0043, o3).
    if not re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", repo):
        print(f"ERROR: repository must look like owner/name, got: '{repo}'")
        sys.exit(1)
    owner, name = repo.split("/", 1)
    repo_flag = target.repo or None
    git_dir = Path(root, target.path) if target.path else root

    branch = gitio.current_branch(git_dir)
    if not branch:
        print("ERROR: Could not determine current branch")
        sys.exit(1)

    task_id = args.task
    if not task_id:
        match = re.match(r"^feature/([A-Z][A-Z0-9]*-[0-9]+)", branch)
        if not match:
            print(f"ERROR: Could not derive task ID from branch '{branch}'")
            print("Use --task TASK_ID to specify manually.")
            sys.exit(1)
        task_id = match.group(1)

    pr_number = args.pr
    if not pr_number:
        pr_number = _gh_text(
            ghio.run_gh(
                "pr",
                "view",
                branch,
                "--json",
                "number",
                "--jq",
                ".number",
                repo=repo_flag,
            )
        ).strip()
        if not pr_number:
            print(f"ERROR: No PR found for branch '{branch}'")
            print("Push your branch and open a PR first, or use --pr PR_NUMBER.")
            sys.exit(1)

    # Defense-in-depth: PR_NUMBER is interpolated into GraphQL queries,
    # so insist it is numeric whether it came from --pr or gh pr view.
    if not re.match(r"^[0-9]+$", pr_number):
        print(f"ERROR: PR number must be numeric (got: {pr_number})")
        sys.exit(1)

    latest_sha = _gh_text(
        ghio.run_gh(
            "pr",
            "view",
            pr_number,
            "--json",
            "headRefOid",
            "--jq",
            ".headRefOid",
            repo=repo_flag,
        )
    ).strip()
    if not latest_sha:
        print(f"ERROR: Could not fetch PR #{pr_number} head SHA")
        sys.exit(1)

    declared_raw, line_present = _read_bots_declaration(root)
    declared = _validate_bots(declared_raw, line_present)

    # Latest code commit for the bot gates: bots don't re-review
    # markdown-only pushes, so Gates 2-3 check the newest commit that
    # touched non-markdown, non-planner files. Gate 1 still checks HEAD.
    origin_main = gitio.run_git(git_dir, "rev-parse", "--verify", "origin/main")
    if origin_main is None or origin_main.returncode != 0:
        print("ERROR: origin/main not found. Run: git fetch origin main")
        # Guard on target.path (not target.repo) — a --repo override
        # leaves the path empty, and "(target repo path: )" would
        # mislead.
        if target.path:
            print(f"       (target repo path: {target.path})")
        sys.exit(1)

    code_log = gitio.run_git(
        git_dir,
        "log",
        "--diff-filter=ACDMR",
        "--format=%H",
        "origin/main..HEAD",
        "--",
        ":!*.md",
        ":!.kit/context/",
        ":!.kit/tasks/",
    )
    code_sha = ""
    if code_log is not None and code_log.returncode == 0:
        code_sha = code_log.stdout.split("\n", 1)[0].strip()
    no_code_changes = not code_sha

    results: list[GateResult] = []

    results.append(_gate_1_ci(latest_sha, repo_flag))
    print(results[-1].line())

    pr_data = _fetch_pr_data(owner, name, pr_number)
    reviews = _pr_reviews(pr_data)
    total, resolved, unresolved = _thread_counts(pr_data)

    results.append(
        _gate_2_coderabbit(
            declared=declared,
            no_code_changes=no_code_changes,
            reviews=reviews,
            code_sha=code_sha,
            latest_sha=latest_sha,
            unresolved=unresolved,
            owner=owner,
            name=name,
        )
    )
    print(results[-1].line())

    results.append(
        _gate_3_bugbot(
            declared=declared,
            no_code_changes=no_code_changes,
            reviews=reviews,
            code_sha=code_sha,
            latest_sha=latest_sha,
            pr_number=pr_number,
            owner=owner,
            name=name,
        )
    )
    print(results[-1].line())

    results.append(_gate_4_threads(pr_data, total, resolved, unresolved))
    print(results[-1].line())

    results.append(_gate_5_evaluator(root, task_id))
    print(results[-1].line())

    results.append(_gate_6_starter(root, task_id))
    print(results[-1].line())

    results.append(_gate_7_task_folder(root, task_id))
    print(results[-1].line())

    any_failed = any(r.verdict == "FAIL" for r in results)
    any_pending = any(r.verdict == "PENDING" for r in results)
    skip_count = len([r for r in results if r.verdict == "SKIP"])

    _emit_dispatch_event(task_id, pr_number, any_failed, any_pending, skip_count)

    if any_failed:
        sys.exit(1)
    if any_pending:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()

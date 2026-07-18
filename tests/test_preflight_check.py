"""Stub-`gh` regression harness for scripts/core/preflight-check.sh (KIT-0040 F1).

Runs the REAL preflight script against canned `gh` payloads: a fake `gh`
executable on PATH dispatches on argv and serves per-scenario files, while
a throwaway git repo provides real branch/SHA state. This turns the
KIT-0034 manual stub-`gh` verification matrix (8 states) into CI
regression coverage. The script itself stays shell + gh (KIT-0034 N2) —
only the harness is Python.

API-shape facts the canned payloads model (verified in KIT-0034):
- CodeRabbit reports via the legacy commit-status API (Gate 2 fallback
  primary source); check-runs are its secondary source.
- BugBot (cursor) reports via check-runs when it has no findings.

The stub-`gh` pattern is reusable for other shell+gh scripts: write
canned payload files, point the stub's data dir at them, run the real
script with the stub bin dir prepended to PATH.

Everything runs against temp dirs with a cleaned git environment (N1) —
see the GIT_DIR gotcha in .kit/context/workflows/TESTING-WORKFLOW.md.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = REPO_ROOT / "scripts" / "core" / "preflight-check.sh"
_TARGET_REPO_LIB = REPO_ROOT / "scripts" / "core" / "lib" / "target_repo.sh"
# kit_markers ships to consumers via bootstrap Step 1.5, but an older
# consumer checkout may lack it — the declaration tests skip then
# (the test_doctor.py precedent).
_KIT_MARKERS_SRC = REPO_ROOT / "scripts" / "local" / "kit_markers.py"

if not _SCRIPT.exists():
    pytest.skip(
        "preflight-check.sh not present in this checkout", allow_module_level=True
    )

for tool in ("bash", "git", "jq"):
    if shutil.which(tool) is None:
        pytest.skip(f"{tool} not available on PATH", allow_module_level=True)


HEAD_TASK = "KIT-9999"
OLD_SHA = "deadbeef" * 5  # a SHA no canned run/review maps to HEAD

# The stub serves canned payloads from $PREFLIGHT_GH_STUB_DIR, keyed by
# the shape of the gh call. "<key>.out present" -> cat it, exit with
# <key>.rc (default 0). "<key>.out absent" -> exit 1 (models a gh error;
# the script wraps these calls in `|| true` / $? checks).
STUB_GH = textwrap.dedent("""\
    #!/bin/bash
    emit() {
        dir="$PREFLIGHT_GH_STUB_DIR"
        if [ -f "$dir/$1.out" ]; then
            cat "$dir/$1.out"
            rc=0
            [ -f "$dir/$1.rc" ] && rc=$(cat "$dir/$1.rc")
            exit "$rc"
        fi
        exit 1
    }

    all_args="$*"
    case "$1 $2" in
        "auth status") exit 0 ;;
        "repo view") echo "stub-owner/stub-repo"; exit 0 ;;
        "pr view")
            case "$all_args" in
                *headRefOid*) emit pr_view_head ;;
                *) emit pr_view_number ;;
            esac ;;
        "run list") emit run_list ;;
        "api graphql") emit graphql ;;
        api\\ *)
            case "$2" in
                */status) emit commit_status ;;
                */check-runs)
                    case "$all_args" in
                        *coderabbit*) emit check_runs_coderabbit ;;
                        *cursor*) emit check_runs_cursor ;;
                    esac ;;
            esac
            exit 1 ;;
    esac
    echo "stub gh: unhandled call: $all_args" >&2
    exit 1
    """)

# `sleep` is stubbed so the CI poll loop's retry delays are instant;
# `dispatch` is stubbed so the fire-and-forget progress event can never
# reach a real event log from a test run (N1).
STUB_NOOP = "#!/bin/bash\nexit 0\n"


def _clean_env(extra: dict[str, str]) -> dict[str, str]:
    """Subprocess env with inherited GIT_* location vars stripped (N1).

    Ambient GIT_DIR / GIT_WORK_TREE (set e.g. by pre-commit) would point
    git at the real repo instead of the temp one. Global/system git
    config is disabled so host config can't alter behavior.
    """
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    env.update(extra)
    return env


class PreflightProject:
    """Temp project skeleton around the real preflight-check.sh."""

    def __init__(self, root: Path, stub_data: Path, env: dict[str, str], head: str):
        self.root = root
        self.stub_data = stub_data
        self.env = env
        self.head = head

    def run(
        self, files: dict[str, str], extra_args: list[str] | None = None
    ) -> subprocess.CompletedProcess:
        # The project fixture is module-scoped (the git repo and .kit
        # artifacts are read-only during a run); the canned payloads are
        # per-scenario, so wipe leftovers from the previous test first.
        for stale in self.stub_data.iterdir():
            stale.unlink()
        for key, content in files.items():
            (self.stub_data / f"{key}.out").write_text(content, encoding="utf-8")
        return subprocess.run(
            [
                "bash",
                str(self.root / "scripts" / "core" / "preflight-check.sh"),
                "--pr",
                "42",
                *(extra_args or []),
            ],
            cwd=self.root,
            env=self.env,
            capture_output=True,
            text=True,
        )


def _gates(output: str) -> dict[int, tuple[str, str]]:
    """Parse GATE:<n>:<name>:<verdict>:<detail> lines into {n: (verdict, detail)}."""
    parsed: dict[int, tuple[str, str]] = {}
    for line in output.splitlines():
        m = re.match(r"^GATE:(\d+):[^:]*:(PASS|FAIL|PENDING|SKIP):(.*)$", line)
        if m:
            parsed[int(m.group(1))] = (m.group(2), m.group(3))
    return parsed


@pytest.fixture(scope="module")
def proj(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("preflight")
    root = tmp_path / "proj"
    core = root / "scripts" / "core"
    (core / "lib").mkdir(parents=True)
    shutil.copy(_SCRIPT, core / "preflight-check.sh")
    shutil.copy(_TARGET_REPO_LIB, core / "lib" / "target_repo.sh")

    # Gate 5/6/7 artifacts — green by default so gate-1-to-4 scenarios
    # can assert overall exit codes.
    (root / ".kit" / "context" / "reviews").mkdir(parents=True)
    (root / ".kit" / "tasks" / "3-in-progress").mkdir(parents=True)
    (root / ".kit" / "tasks" / "4-in-review").mkdir(parents=True)
    reviews = root / ".kit" / "context" / "reviews"
    (reviews / f"{HEAD_TASK}-code-review.md").write_text("review\n", encoding="utf-8")
    starter = root / ".kit" / "context" / f"{HEAD_TASK}-REVIEW-STARTER.md"
    starter.write_text("starter\n", encoding="utf-8")
    task = root / ".kit" / "tasks" / "3-in-progress" / f"{HEAD_TASK}-stub-task.md"
    task.write_text("task\n", encoding="utf-8")

    env = _clean_env({})

    def git(*args: str) -> None:
        subprocess.run(
            ["git", *args], cwd=root, env=env, check=True, capture_output=True
        )

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (root / "README.md").write_text("seed\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "seed")
    git("update-ref", "refs/remotes/origin/main", "main")
    git("checkout", "-q", "-b", f"feature/{HEAD_TASK}-stub")
    (root / "code.py").write_text("x = 1\n", encoding="utf-8")
    git("add", "code.py")
    git("commit", "-qm", "feat: code change")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    bin_dir = tmp_path / "stub-bin"
    bin_dir.mkdir()
    for name, body in (("gh", STUB_GH), ("sleep", STUB_NOOP), ("dispatch", STUB_NOOP)):
        stub = bin_dir / name
        stub.write_text(body, encoding="utf-8")
        stub.chmod(stub.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    stub_data = tmp_path / "stub-data"
    stub_data.mkdir()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
    env["PREFLIGHT_GH_STUB_DIR"] = str(stub_data)

    return PreflightProject(root, stub_data, env, head)


# ── Canned payload builders ──────────────────────────────────────────────
def _review(login: str, state: str, oid: str) -> dict:
    return {"author": {"login": login}, "state": state, "commit": {"oid": oid}}


def _graphql(reviews: list[dict], unresolved: int = 0, resolved: int = 0) -> str:
    threads = [{"isResolved": True}] * resolved + [{"isResolved": False}] * unresolved
    return json.dumps(
        {
            "data": {
                "repository": {
                    "pullRequest": {
                        "reviews": {"nodes": reviews},
                        "reviewThreads": {"nodes": threads},
                    }
                }
            }
        }
    )


def _run_entry(
    head: str,
    status: str = "completed",
    conclusion: str = "success",
    name: str = "Tests",
    event: str = "push",
) -> dict:
    return {
        "status": status,
        "conclusion": conclusion,
        "workflowName": name,
        "event": event,
        "headSha": head,
    }


def _baseline(head: str) -> dict[str, str]:
    """Everything green via the primary paths: CI success on HEAD,
    CodeRabbit review event on HEAD, BugBot review event on HEAD."""
    return {
        "pr_view_head": head + "\n",
        "run_list": json.dumps([_run_entry(head)]),
        "graphql": _graphql(
            [
                _review("coderabbitai[bot]", "APPROVED", head),
                _review("cursor[bot]", "COMMENTED", head),
            ],
            resolved=2,
        ),
    }


# ── Baseline ─────────────────────────────────────────────────────────────
class TestBaseline:
    def test_all_gates_pass_exit_0(self, proj):
        result = proj.run(_baseline(proj.head))
        gates = _gates(result.stdout)
        assert {n: v for n, (v, _) in gates.items()} == {
            n: "PASS" for n in range(1, 8)
        }, (result.stdout + result.stderr)
        assert result.returncode == 0


# ── Gate 1: CI ───────────────────────────────────────────────────────────
class TestGate1CI:
    def test_completed_failure_beats_running_sibling(self, proj):
        # KIT-0034 N3 precedence: a completed non-success run FAILs the
        # gate even while a sibling workflow is still executing.
        files = _baseline(proj.head)
        files["run_list"] = json.dumps(
            [
                _run_entry(proj.head, status="in_progress", conclusion="", name="Slow"),
                _run_entry(proj.head, conclusion="failure", name="Lint"),
            ]
        )
        result = proj.run(files)
        verdict, detail = _gates(result.stdout)[1]
        assert verdict == "FAIL", result.stdout
        assert "failure" in detail
        assert result.returncode == 1

    def test_gh_error_fails_not_pending(self, proj):
        # `gh run list` erroring on every attempt is a connectivity/auth
        # problem — fail closed, don't report PENDING.
        files = _baseline(proj.head)
        del files["run_list"]  # absent canned file -> stub gh exits 1
        result = proj.run(files)
        verdict, detail = _gates(result.stdout)[1]
        assert verdict == "FAIL", result.stdout
        assert "Could not fetch CI runs" in detail
        assert result.returncode == 1

    def test_empty_run_list_is_pending_exit_2(self, proj):
        # Runs not registered yet for the head SHA: PENDING (not FAIL),
        # and with every other gate green the script exits 2.
        files = _baseline(proj.head)
        files["run_list"] = "[]"
        result = proj.run(files)
        verdict, detail = _gates(result.stdout)[1]
        assert verdict == "PENDING", result.stdout
        assert "No CI runs registered" in detail
        assert result.returncode == 2


# ── Gate 2: CodeRabbit (fallback matrix) ─────────────────────────────────
class TestGate2CodeRabbit:
    def _no_head_review(self, head: str, cr_state: str = "APPROVED") -> dict[str, str]:
        # CodeRabbit review event exists only on an OLD sha, so the
        # primary SHA match misses and the fallback logic decides.
        files = _baseline(head)
        files["graphql"] = _graphql(
            [
                _review("coderabbitai[bot]", cr_state, OLD_SHA),
                _review("cursor[bot]", "COMMENTED", head),
            ]
        )
        return files

    def test_fallback_pass_on_commit_status(self, proj):
        # KIT-0034 F1: commit status green + latest review APPROVED +
        # 0 unresolved threads = reviewed, even with no review event on
        # the head SHA. CodeRabbit's primary signal is the commit-status
        # API, not check-runs.
        files = self._no_head_review(proj.head)
        files["commit_status"] = "success\n"
        result = proj.run(files)
        verdict, detail = _gates(result.stdout)[2]
        assert verdict == "PASS", result.stdout
        assert "fallback" in detail
        assert result.returncode == 0

    def test_fallback_pass_on_check_run_source(self, proj):
        # Secondary source: empty commit status but a green CodeRabbit
        # check-run still satisfies the fallback.
        files = self._no_head_review(proj.head)
        files["commit_status"] = ""  # gh succeeds, no matching contexts
        files["check_runs_coderabbit"] = "success\n"
        result = proj.run(files)
        verdict, detail = _gates(result.stdout)[2]
        assert verdict == "PASS", result.stdout
        assert "fallback" in detail

    def test_no_review_fails(self, proj):
        # No CodeRabbit review event anywhere and no signal on the head
        # SHA: the gate fails closed.
        files = _baseline(proj.head)
        files["graphql"] = _graphql([_review("cursor[bot]", "COMMENTED", proj.head)])
        result = proj.run(files)
        verdict, detail = _gates(result.stdout)[2]
        assert verdict == "FAIL", result.stdout
        assert "No review from coderabbitai[bot]" in detail
        assert result.returncode == 1

    def test_unresolved_thread_blocks_fallback(self, proj):
        # N1 fail-closed: signal green + APPROVED, but one unresolved
        # thread blocks the fallback (and Gate 4 agrees — same snapshot).
        files = _baseline(proj.head)
        files["graphql"] = _graphql(
            [
                _review("coderabbitai[bot]", "APPROVED", OLD_SHA),
                _review("cursor[bot]", "COMMENTED", proj.head),
            ],
            unresolved=1,
        )
        files["commit_status"] = "success\n"
        result = proj.run(files)
        gates = _gates(result.stdout)
        assert gates[2][0] == "FAIL", result.stdout
        assert gates[4][0] == "FAIL"
        assert result.returncode == 1

    def test_changes_requested_blocks_fallback(self, proj):
        # N1 fail-closed: a CHANGES_REQUESTED latest verdict blocks the
        # fallback even with a green signal and zero unresolved threads.
        files = self._no_head_review(proj.head, cr_state="CHANGES_REQUESTED")
        files["commit_status"] = "success\n"
        result = proj.run(files)
        verdict, detail = _gates(result.stdout)[2]
        assert verdict == "FAIL", result.stdout
        assert "CHANGES_REQUESTED" in detail
        assert result.returncode == 1


# ── Gate 3: BugBot ───────────────────────────────────────────────────────
class TestGate3BugBot:
    def test_check_run_pass_when_no_review_event(self, proj):
        # BugBot's no-findings case: no review event, a green cursor
        # check-run on the code SHA satisfies the gate.
        files = _baseline(proj.head)
        files["graphql"] = _graphql(
            [_review("coderabbitai[bot]", "APPROVED", proj.head)]
        )
        files["check_runs_cursor"] = "completed:success\n"
        result = proj.run(files)
        verdict, detail = _gates(result.stdout)[3]
        assert verdict == "PASS", result.stdout
        assert "check-run" in detail
        assert result.returncode == 0


# ── Gates 5/6: bundled-PR convention (KIT-0042) ──────────────────────────
class TestGate56Bundle:
    """A bundled PR satisfies Gates 5/6 via per-task pointer files named
    exactly like a solo task's artifacts (reference shape: the
    KIT-0037/38/39 bundle's pointer files), and the FAIL detail names
    that convention so nobody discovers it by failing the gate.
    """

    def test_pointer_files_pass_gates_5_6_for_non_lead_task(self, proj):
        # Bundle lead is HEAD_TASK (fixture artifacts); a bundled task
        # KIT-9998 carries its own pointer starter + pointer record.
        starter = proj.root / ".kit" / "context" / "KIT-9998-REVIEW-STARTER.md"
        record = (
            proj.root / ".kit" / "context" / "reviews" / "KIT-9998-evaluator-review.md"
        )
        task = proj.root / ".kit" / "tasks" / "3-in-progress" / "KIT-9998-stub-task.md"
        try:
            starter.write_text(
                f"Pointer: see {HEAD_TASK}-REVIEW-STARTER.md (bundle lead)\n",
                encoding="utf-8",
            )
            record.write_text(
                f"Pointer: see {HEAD_TASK}-evaluator-review.md (bundle lead)\n",
                encoding="utf-8",
            )
            task.write_text("task\n", encoding="utf-8")
            result = proj.run(_baseline(proj.head), extra_args=["--task", "KIT-9998"])
            gates = _gates(result.stdout)
            assert gates[5][0] == "PASS", result.stdout
            assert gates[6][0] == "PASS", result.stdout
        finally:
            for path in (starter, record, task):
                path.unlink(missing_ok=True)

    def test_prefix_is_not_a_match_boundary_violation(self, proj):
        # Boundary pinning (KIT-0040 lesson, kept even on the convention
        # route): the fixture's KIT-9999 artifacts must NOT satisfy the
        # gates for the shorter task ID KIT-999 — the literal separator
        # after ${TASK_ID} in every Gate 5/6 pattern is the boundary.
        # Gate 7 gained the same boundary in KIT-0043 (F3): the fixture's
        # KIT-9999-stub-task.md must not locate task KIT-999.
        result = proj.run(_baseline(proj.head), extra_args=["--task", "KIT-999"])
        gates = _gates(result.stdout)
        assert gates[5][0] == "FAIL", result.stdout
        assert gates[6][0] == "FAIL", result.stdout
        assert gates[7][0] == "FAIL", result.stdout

    def test_empty_pointer_files_do_not_pass(self, proj):
        # A zero-byte "pointer" (botched write, or a bare touch) must
        # not satisfy Gates 5/6 — the find requires a non-empty regular
        # file.
        starter = proj.root / ".kit" / "context" / "KIT-9996-REVIEW-STARTER.md"
        record = (
            proj.root / ".kit" / "context" / "reviews" / "KIT-9996-evaluator-review.md"
        )
        try:
            starter.write_text("", encoding="utf-8")
            record.write_text("", encoding="utf-8")
            result = proj.run(_baseline(proj.head), extra_args=["--task", "KIT-9996"])
            gates = _gates(result.stdout)
            assert gates[5][0] == "FAIL", result.stdout
            assert gates[6][0] == "FAIL", result.stdout
        finally:
            for path in (starter, record):
                path.unlink(missing_ok=True)

    def test_fail_details_name_bundle_convention(self, proj):
        # No artifacts exist for KIT-9997 → Gates 5/6 FAIL, and each
        # detail must point at BOTH conventions (F1.1 + the 2026-07-13
        # spec addendum): the bundle pointer files and the multi-PR-task
        # case (artifacts on a sibling PR's branch — the KIT-0035
        # spurious-FAIL evidence). The parseable GATE:N:Name:FAIL:
        # prefix stays intact (harness regex in _gates would not match
        # otherwise).
        result = proj.run(_baseline(proj.head), extra_args=["--task", "KIT-9997"])
        gates = _gates(result.stdout)
        for gate_num in (5, 6):
            verdict, detail = gates[gate_num]
            assert verdict == "FAIL", result.stdout
            assert "bundled PR" in detail, detail
            assert "review-handoff" in detail, detail
            assert "Multi-PR task" in detail, detail
        assert result.returncode == 1


# ── Gate 1: edge hardening (KIT-0043 F1/F2) ──────────────────────────────
class TestGate1EdgeHardening:
    """Convergent evaluator findings from KIT-0042: non-terminal
    statuses must read as PENDING (only `completed` is terminal in the
    Actions API), and run-list truncation at the --limit cap must be
    visible, not silent.
    """

    def test_waiting_status_is_pending_not_fail(self, proj):
        # A run awaiting a runner/approval is non-terminal — PENDING,
        # not a CI failure (KIT-0034's pending-vs-failed distinction).
        files = _baseline(proj.head)
        files["run_list"] = json.dumps(
            [_run_entry(proj.head, status="waiting", conclusion="")]
        )
        result = proj.run(files)
        verdict, _ = _gates(result.stdout)[1]
        assert verdict == "PENDING", result.stdout
        assert result.returncode == 2

    def test_unknown_future_status_is_pending(self, proj):
        # A status value the script has never heard of is by definition
        # not `completed` → non-terminal → PENDING, never FAIL.
        files = _baseline(proj.head)
        files["run_list"] = json.dumps(
            [_run_entry(proj.head, status="hyperqueued", conclusion="")]
        )
        result = proj.run(files)
        verdict, _ = _gates(result.stdout)[1]
        assert verdict == "PENDING", result.stdout

    def test_completed_failure_still_fails(self, proj):
        # Pinning the other side of F2: terminal non-success stays FAIL
        # (KIT-0034 N-series: never soften a completed failure).
        files = _baseline(proj.head)
        files["run_list"] = json.dumps(
            [
                _run_entry(proj.head),
                _run_entry(
                    proj.head, status="completed", conclusion="failure", name="Lint"
                ),
            ]
        )
        result = proj.run(files)
        verdict, _ = _gates(result.stdout)[1]
        assert verdict == "FAIL", result.stdout
        assert result.returncode == 1

    def test_run_count_at_cap_is_pending_never_pass(self, proj):
        # F1 (evaluator round): an at-cap response is indistinguishable
        # from a truncated one — unseen runs may exist, so all-green at
        # the cap must demote to PENDING with the remedy named, never
        # false-PASS (o3's hidden-51st-run scenario).
        files = _baseline(proj.head)
        files["run_list"] = json.dumps(
            [_run_entry(proj.head, name=f"WF-{i}") for i in range(50)]
        )
        result = proj.run(files)
        verdict, detail = _gates(result.stdout)[1]
        assert verdict == "PENDING", result.stdout
        assert "cap" in detail, detail
        assert result.returncode == 2

    def test_cap_guard_keys_on_raw_count_not_filtered(self, proj):
        # F1 (fast-v2): a cap-full response where the event filter
        # discards some entries must STILL trip the guard — the guard
        # watches the raw returned count, not the post-filter count.
        files = _baseline(proj.head)
        entries = [_run_entry(proj.head, name=f"WF-{i}") for i in range(40)] + [
            _run_entry(proj.head, name=f"D-{i}", event="workflow_dispatch")
            for i in range(10)
        ]
        files["run_list"] = json.dumps(entries)
        result = proj.run(files)
        verdict, detail = _gates(result.stdout)[1]
        assert verdict == "PENDING", result.stdout
        assert "cap" in detail, detail

    def test_visible_failure_beats_at_cap_pending(self, proj):
        # Verdict priority: a failing run in the visible window is a
        # harder signal than "maybe truncated" — FAIL wins over the
        # at-cap PENDING demotion.
        files = _baseline(proj.head)
        entries = [_run_entry(proj.head, name=f"WF-{i}") for i in range(49)] + [
            _run_entry(proj.head, conclusion="failure", name="Lint")
        ]
        files["run_list"] = json.dumps(entries)
        result = proj.run(files)
        verdict, _ = _gates(result.stdout)[1]
        assert verdict == "FAIL", result.stdout

    def test_failure_beats_waiting_sibling(self, proj):
        # Priority pinning: completed failure + a waiting sibling must
        # read FAIL (the failure is real regardless of the pending run).
        files = _baseline(proj.head)
        files["run_list"] = json.dumps(
            [
                _run_entry(proj.head, conclusion="failure", name="Lint"),
                _run_entry(proj.head, status="waiting", conclusion="", name="Tests"),
            ]
        )
        result = proj.run(files)
        verdict, _ = _gates(result.stdout)[1]
        assert verdict == "FAIL", result.stdout


# ── Gate 2: F4 reproduce-or-decline (KIT-0043) ───────────────────────────
class TestGate2MixedContexts:
    """o3 (KIT-0042 rounds) claimed a mixed success/failure pair of
    CodeRabbit commit-status contexts can slip the Gate 2 fallback.
    These tests are the reproduce-or-decline evidence.
    """

    def _no_head_review(self, head: str) -> dict[str, str]:
        files = _baseline(head)
        files["graphql"] = _graphql(
            [
                _review("coderabbitai[bot]", "APPROVED", OLD_SHA),
                _review("cursor[bot]", "COMMENTED", head),
            ],
            resolved=2,
        )
        return files

    def test_non_success_fallback_signal_fails_closed(self, proj):
        # Shell layer: the fallback requires CR_SIGNAL to be exactly
        # "success"; a "failure" signal (what the jq reduces a mixed
        # context set to) must FAIL even with APPROVED + 0 unresolved.
        files = self._no_head_review(proj.head)
        files["commit_status"] = "failure\n"
        result = proj.run(files)
        verdict, detail = _gates(result.stdout)[2]
        assert verdict == "FAIL", result.stdout
        assert "signal=failure" in detail, detail

    def test_status_jq_reduces_mixed_contexts_to_non_success(self, proj):
        # jq layer: extract the commit-status --jq filter from the real
        # script (no duplication drift) and run real jq over a mixed
        # fixture — the reduction must yield the failing state, never
        # "success".
        script = (proj.root / "scripts" / "core" / "preflight-check.sh").read_text(
            encoding="utf-8"
        )
        m = re.search(r"--jq '(\[\.statuses\[\][^']*)'", script)
        assert m, "commit-status jq filter not found in script"
        mixed = json.dumps(
            {
                "statuses": [
                    {"context": "coderabbitai/review", "state": "success"},
                    {"context": "coderabbitai/ci", "state": "failure"},
                ]
            }
        )
        out = subprocess.run(
            ["jq", "-r", m.group(1)],
            input=mixed,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        assert out == "failure", out


# ── Gates 2/3: bots declaration (KIT-0056, ADR-0027 P5) ─────────────────
@pytest.mark.skipif(
    not _KIT_MARKERS_SRC.exists(), reason="kit_markers.py absent (consumer checkout)"
)
class TestGate23BotsDeclaration:
    """A `bots:` line in CLAUDE.md's kit-install region turns Gates 2/3
    into SKIP-with-notice for declared-absent bots — never FAIL, never
    a silent PASS. No line / no region / invalid line = both bots
    expected (fail closed, today's behavior).
    """

    def _install_declaration(
        self, proj, bots_line: str | None, indent: str = ""
    ) -> None:
        local_dir = proj.root / "scripts" / "local"
        local_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(_KIT_MARKERS_SRC, local_dir / "kit_markers.py")
        region = "shape: single\nprofile: python\n"
        if bots_line is not None:
            region += f"{indent}bots: {bots_line}\n"
        (proj.root / "CLAUDE.md").write_text(
            "# stub project\n\n"
            "<!-- BEGIN KIT-LOCAL: kit-install -->\n"
            f"{region}"
            "<!-- END KIT-LOCAL: kit-install -->\n",
            encoding="utf-8",
        )

    def _remove_declaration(self, proj) -> None:
        (proj.root / "CLAUDE.md").unlink(missing_ok=True)
        (proj.root / "scripts" / "local" / "kit_markers.py").unlink(missing_ok=True)

    def _no_bot_reviews(self, head: str) -> dict[str, str]:
        """CI green, threads clean, but NO bot activity anywhere — the
        state a bot-less project is permanently in."""
        files = _baseline(head)
        files["graphql"] = _graphql([], resolved=0)
        return files

    def test_bots_none_skips_both_gates_exit_0(self, proj):
        self._install_declaration(proj, "none")
        try:
            result = proj.run(self._no_bot_reviews(proj.head))
            gates = _gates(result.stdout)
            for gate_num in (2, 3):
                verdict, detail = gates[gate_num]
                assert verdict == "SKIP", result.stdout
                assert "declared absent in kit-install" in detail
                assert "bots: none" in detail
            assert result.returncode == 0, result.stdout + result.stderr
        finally:
            self._remove_declaration(proj)

    def test_subset_coderabbit_only(self, proj):
        # bugbot declared absent → Gate 3 SKIPs; coderabbit declared
        # present → Gate 2 still evaluated (and passes via its review)
        self._install_declaration(proj, "coderabbit")
        try:
            files = self._no_bot_reviews(proj.head)
            files["graphql"] = _graphql(
                [_review("coderabbitai[bot]", "APPROVED", proj.head)]
            )
            result = proj.run(files)
            gates = _gates(result.stdout)
            assert gates[2][0] == "PASS", result.stdout
            assert gates[3][0] == "SKIP", result.stdout
            assert result.returncode == 0
        finally:
            self._remove_declaration(proj)

    def test_indented_declaration_still_read(self, proj):
        # o3 (this PR): the Python readers strip() lines, so an
        # indented hand-edited declaration must be visible to the
        # shell readers too — invisible here would run gates that
        # doctor's reading says are declared away
        self._install_declaration(proj, "none", indent="   ")
        try:
            result = proj.run(self._no_bot_reviews(proj.head))
            gates = _gates(result.stdout)
            assert gates[2][0] == "SKIP", result.stdout
            assert gates[3][0] == "SKIP", result.stdout
            assert result.returncode == 0
        finally:
            self._remove_declaration(proj)

    def test_comma_and_case_tolerance(self, proj):
        # fast-v2 round 1: the preflight reader shares the door's
        # tolerance — 'CodeRabbit,BugBot' is a valid both-present
        # declaration, so neither gate SKIPs and no NOTICE fires
        self._install_declaration(proj, "CodeRabbit,BugBot")
        try:
            result = proj.run(self._no_bot_reviews(proj.head))
            assert "NOTICE" not in result.stdout
            gates = _gates(result.stdout)
            assert gates[2][0] == "FAIL", result.stdout  # declared present, missing
            assert gates[3][0] == "FAIL", result.stdout
        finally:
            self._remove_declaration(proj)

    def test_declared_present_bot_still_fails_when_missing(self, proj):
        # SKIP is never a free pass: a bot the declaration KEEPS is
        # still required.
        self._install_declaration(proj, "bugbot")
        try:
            result = proj.run(self._no_bot_reviews(proj.head))
            gates = _gates(result.stdout)
            assert gates[2][0] == "SKIP", result.stdout
            assert gates[3][0] == "FAIL", result.stdout
            assert result.returncode == 1
        finally:
            self._remove_declaration(proj)

    def test_region_without_bots_line_is_todays_behavior(self, proj):
        # N1: a record with no bots: line changes nothing — both bots
        # expected, both gates FAIL without bot activity.
        self._install_declaration(proj, None)
        try:
            result = proj.run(self._no_bot_reviews(proj.head))
            gates = _gates(result.stdout)
            assert gates[2][0] == "FAIL", result.stdout
            assert gates[3][0] == "FAIL", result.stdout
            assert "NOTICE" not in result.stdout
        finally:
            self._remove_declaration(proj)

    def test_invalid_declaration_fails_closed_with_notice(self, proj):
        # A typo'd declaration must not silently SKIP gates — expect
        # both bots (the gates run) and say why, loudly.
        self._install_declaration(proj, "horsebot")
        try:
            result = proj.run(self._no_bot_reviews(proj.head))
            assert "NOTICE: invalid bots declaration" in result.stdout
            assert "horsebot" in result.stdout
            gates = _gates(result.stdout)
            assert gates[2][0] == "FAIL", result.stdout
            assert gates[3][0] == "FAIL", result.stdout
        finally:
            self._remove_declaration(proj)

    def test_none_combined_with_bot_is_invalid(self, proj):
        self._install_declaration(proj, "none coderabbit")
        try:
            result = proj.run(self._no_bot_reviews(proj.head))
            assert "NOTICE: invalid bots declaration" in result.stdout
            assert _gates(result.stdout)[2][0] == "FAIL", result.stdout
        finally:
            self._remove_declaration(proj)

    def test_skip_never_masks_a_ci_failure(self, proj):
        self._install_declaration(proj, "none")
        try:
            files = self._no_bot_reviews(proj.head)
            files["run_list"] = json.dumps(
                [_run_entry(proj.head, conclusion="failure", name="Lint")]
            )
            result = proj.run(files)
            gates = _gates(result.stdout)
            assert gates[1][0] == "FAIL", result.stdout
            assert gates[2][0] == "SKIP"
            assert gates[3][0] == "SKIP"
            assert result.returncode == 1
        finally:
            self._remove_declaration(proj)

    def test_skip_never_masks_pending(self, proj):
        # PENDING outranks the SKIPs in the final verdict: skipped
        # bot gates plus an unregistered CI run still exit 2
        self._install_declaration(proj, "none")
        try:
            files = self._no_bot_reviews(proj.head)
            files["run_list"] = "[]"
            result = proj.run(files)
            gates = _gates(result.stdout)
            assert gates[1][0] == "PENDING", result.stdout
            assert gates[2][0] == "SKIP"
            assert gates[3][0] == "SKIP"
            assert result.returncode == 2
        finally:
            self._remove_declaration(proj)

    @pytest.mark.parametrize("value", ["", ","])
    def test_empty_bots_line_is_invalid_not_absent(self, proj, value):
        # fast-v2 round 2 + BugBot PR #83: doctor FAILs a
        # present-but-valueless bots: line (bots-record) — preflight
        # must not silently read the same line as "no declaration";
        # it fails closed with its own NOTICE. The ',' variant reduces
        # to nothing only AFTER normalization.
        self._install_declaration(proj, value)
        try:
            result = proj.run(self._no_bot_reviews(proj.head))
            assert "NOTICE: empty bots declaration" in result.stdout
            gates = _gates(result.stdout)
            assert gates[2][0] == "FAIL", result.stdout
            assert gates[3][0] == "FAIL", result.stdout
        finally:
            self._remove_declaration(proj)


class TestGate7RegularFile:
    def test_directory_named_like_task_does_not_pass(self, proj):
        # CodeRabbit (PR #75): a DIRECTORY named <ID>-anything satisfied
        # Gate 7's find. Gate 7 now requires a non-empty regular file,
        # matching the Gates 5/6 treatment.
        bogus = proj.root / ".kit" / "tasks" / "3-in-progress" / "KIT-9995-dir.md"
        try:
            bogus.mkdir()
            result = proj.run(_baseline(proj.head), extra_args=["--task", "KIT-9995"])
            assert _gates(result.stdout)[7][0] == "FAIL", result.stdout
        finally:
            bogus.rmdir()

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

    def run(self, files: dict[str, str]) -> subprocess.CompletedProcess:
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
        m = re.match(r"^GATE:(\d+):[^:]*:(PASS|FAIL|PENDING):(.*)$", line)
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
) -> dict:
    return {
        "status": status,
        "conclusion": conclusion,
        "workflowName": name,
        "event": "push",
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

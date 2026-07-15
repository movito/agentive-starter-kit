"""Tests for ci-check.sh (KIT-0050, ADR-0027 P1).

Characterization net first (N1): the hook-absent behavior of
ci-check.sh is pinned byte-for-byte (normalized only for scratch paths)
BEFORE the dispatcher lands, exactly as KIT-0048 did for bootstrap.
Every later edit must keep these goldens green — they are the proof
that existing consumers see no change until they opt in.

The scratch harness stubs the whole toolchain (black, isort, pytest,
python3, git) on a controlled PATH so runs are deterministic and never
touch the real gauntlet (stub-gh preflight harness pattern).
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CI_CHECK = REPO_ROOT / "scripts" / "core" / "ci-check.sh"

if not CI_CHECK.exists():
    pytest.skip("ci-check.sh not present in this checkout", allow_module_level=True)

if shutil.which("bash") is None:
    pytest.skip("bash not available on PATH", allow_module_level=True)


def _stub(path: Path, body: str) -> None:
    path.write_text("#!/bin/bash\n" + body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def make_scratch(tmp_path: Path) -> tuple[Path, Path]:
    """A scratch repo root (ci-check.sh installed, scripts/ + tests/
    present as in any real consumer) plus a stub-toolchain bin dir."""
    root = tmp_path / "root"
    (root / "scripts" / "core").mkdir(parents=True)
    (root / "tests").mkdir()
    shutil.copy(CI_CHECK, root / "scripts" / "core" / "ci-check.sh")
    # one Python file so the pattern-lint step takes its main branch
    (root / "scripts" / "dummy.py").touch()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _stub(
        bin_dir / "black",
        'if [ "$1" = "--version" ]; then echo "black, 26.1.0"; exit 0; fi\n'
        'exit "${STUB_BLACK_RC:-0}"\n',
    )
    _stub(bin_dir / "isort", 'exit "${STUB_ISORT_RC:-0}"\n')
    _stub(bin_dir / "pytest", 'exit "${STUB_PYTEST_RC:-0}"\n')
    # covers `python3 -m flake8`, pattern_lint.py, check_cross_repo_config.py
    _stub(bin_dir / "python3", 'exit "${STUB_PYTHON3_RC:-0}"\n')
    _stub(bin_dir / "git", 'echo "main"\n')
    return root, bin_dir


def run_ci_check(
    root: Path, bin_dir: Path, extra_env: dict[str, str] | None = None
) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    env["PATH"] = os.pathsep.join([str(bin_dir), env.get("PATH", "")])
    env.update(extra_env or {})
    return subprocess.run(
        ["bash", str(root / "scripts" / "core" / "ci-check.sh")],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


def normalized(result: subprocess.CompletedProcess, tmp_path: Path) -> str:
    """stdout with the per-run scratch path replaced by a placeholder."""
    return result.stdout.replace(str(tmp_path), "<TMP>")


BAR = "━" * 40

# Pinned from the pre-KIT-0050 script (stub toolchain, all checks green).
GOLDEN_PASS = f"""\
{BAR}
🔍 Running local CI checks
{BAR}

⚠️  No virtual environment found. Using system Python.
Python: <TMP>/bin/python3

{BAR}
1/6 🎨 Checking formatting with Black...
{BAR}
✅ Black: All files formatted correctly

{BAR}
2/6 📋 Checking import sorting with isort...
{BAR}
✅ isort: Imports sorted correctly

{BAR}
3/6 🔎 Linting with flake8...
{BAR}
✅ flake8: No critical linting errors

{BAR}
4/6 🔍 Running pattern lint (DK rules)...
{BAR}
✅ Pattern lint: No DK violations

{BAR}
5/6 🧪 Running full test suite with coverage...
{BAR}
✅ Tests: All tests pass (fail_under gate in pyproject.toml)

{BAR}
6/6 🧭 Validating cross-repo config...
{BAR}

{BAR}
✅ All CI checks passed!
   Safe to push: git push origin main
{BAR}
"""


class TestCharacterization:
    """N1: hook-absent ci-check.sh is byte-identical to the pre-KIT-0050
    script. These goldens were captured BEFORE the dispatcher landed."""

    def test_pass_path_output_pinned(self, tmp_path):
        root, bin_dir = make_scratch(tmp_path)
        result = run_ci_check(root, bin_dir)
        assert result.returncode == 0, result.stdout + result.stderr
        assert normalized(result, tmp_path) == GOLDEN_PASS
        assert result.stderr == ""

    def test_failing_check_fails_run_but_never_short_circuits(self, tmp_path):
        root, bin_dir = make_scratch(tmp_path)
        result = run_ci_check(root, bin_dir, {"STUB_BLACK_RC": "1"})
        assert result.returncode == 1
        out = result.stdout
        assert "❌ Black: Formatting issues found" in out
        # later steps still ran (FAILED accumulates, no exit-on-first)
        assert "✅ Tests: All tests pass" in out
        assert "❌ CI checks failed!" in out

    def test_failing_tests_fail_the_run(self, tmp_path):
        root, bin_dir = make_scratch(tmp_path)
        result = run_ci_check(root, bin_dir, {"STUB_PYTEST_RC": "1"})
        assert result.returncode == 1
        assert "❌ Tests: Test failures or coverage below" in result.stdout

    def test_missing_flake8_fails_fast(self, tmp_path):
        root, bin_dir = make_scratch(tmp_path)
        result = run_ci_check(root, bin_dir, {"STUB_PYTHON3_RC": "1"})
        assert result.returncode == 1
        assert "flake8 not installed" in result.stderr


def install_hook(root: Path, body: str, mode: int = 0o755) -> Path:
    hook = root / "scripts" / "local" / "checks.sh"
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text("#!/bin/bash\n" + body, encoding="utf-8")
    hook.chmod(mode)
    return hook


class TestDispatcher:
    """F1 (KIT-0050): presence-of-file dispatch to scripts/local/checks.sh."""

    def test_hook_receives_mode_ci_from_repo_root(self, tmp_path):
        root, bin_dir = make_scratch(tmp_path)
        install_hook(root, 'echo "HOOK: args=$* pwd=$PWD"\nexit 0\n')
        result = run_ci_check(root, bin_dir)
        assert result.returncode == 0
        assert "HOOK: args=--mode ci" in result.stdout
        # contract: invoked from the repo root
        assert f"pwd={root}" in result.stdout
        # the built-in gauntlet must NOT also run
        assert "Running local CI checks" not in result.stdout

    def test_hook_exit_code_passes_through(self, tmp_path):
        root, bin_dir = make_scratch(tmp_path)
        install_hook(root, 'echo "hook failing"\nexit 1\n')
        result = run_ci_check(root, bin_dir)
        assert result.returncode == 1
        assert "hook failing" in result.stdout

    def test_non_executable_hook_is_loud_error_not_fallback(self, tmp_path):
        # the masking class: a present-but-broken hook must never
        # silently fall back to the built-in gauntlet
        root, bin_dir = make_scratch(tmp_path)
        install_hook(root, "exit 0\n", mode=0o644)
        result = run_ci_check(root, bin_dir)
        assert result.returncode == 1
        assert "not an executable file" in result.stderr
        assert "Running local CI checks" not in result.stdout

    def test_hook_directory_is_loud_error(self, tmp_path):
        root, bin_dir = make_scratch(tmp_path)
        (root / "scripts" / "local" / "checks.sh").mkdir(parents=True)
        result = run_ci_check(root, bin_dir)
        assert result.returncode == 1
        assert "not an executable file" in result.stderr

    def test_broken_symlink_hook_is_loud_error(self, tmp_path):
        root, bin_dir = make_scratch(tmp_path)
        (root / "scripts" / "local").mkdir(parents=True)
        (root / "scripts" / "local" / "checks.sh").symlink_to(root / "nope.sh")
        result = run_ci_check(root, bin_dir)
        assert result.returncode == 1
        assert "not an executable file" in result.stderr

    def test_absent_hook_runs_builtin_gauntlet(self, tmp_path):
        # N1 restated at the dispatch seam: no hook -> the pinned golden
        root, bin_dir = make_scratch(tmp_path)
        result = run_ci_check(root, bin_dir)
        assert result.returncode == 0
        assert normalized(result, tmp_path) == GOLDEN_PASS

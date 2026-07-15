"""Tests for the seeded check-hook templates (KIT-0050 F2/F3).

Contract conformance for both seed templates (`--mode ci|local`, exit
0/1, loud usage failure on a bogus mode) plus the N1 equivalence proof:
on the same tree, the seeded python hook's `--mode ci` output matches
the built-in gauntlet's byte-for-byte (normalized only for scratch
paths).

Consumer-rsync boundary: this module reads scripts/local/ content
(the seed templates), so it is excluded from the consumer tests/ rsync
in bootstrap-consumer.sh (exclude + rm -f sweep) and module-skips when
the templates are absent — the tests/test_kit_markers.py pattern.

The scratch/stub harness is shared with tests/test_ci_check.py in
spirit but duplicated here deliberately: importing across test modules
would couple a consumer-shipped module to a kit-only one.
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
TEMPLATES = REPO_ROOT / "scripts" / "local" / "templates"
PYTHON_SEED = TEMPLATES / "checks-python.sh"
NONE_SEED = TEMPLATES / "checks-none.sh"

if not PYTHON_SEED.exists() or not NONE_SEED.exists():
    pytest.skip(
        "check-hook seed templates not present (consumer checkout)",
        allow_module_level=True,
    )

if shutil.which("bash") is None:
    pytest.skip("bash not available on PATH", allow_module_level=True)


def _stub(path: Path, body: str) -> None:
    path.write_text("#!/bin/bash\n" + body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def make_scratch(tmp_path: Path) -> tuple[Path, Path]:
    """Scratch repo root + stub toolchain bin (test_ci_check.py harness)."""
    root = tmp_path / "root"
    (root / "scripts" / "core").mkdir(parents=True)
    (root / "tests").mkdir()
    shutil.copy(CI_CHECK, root / "scripts" / "core" / "ci-check.sh")
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
    _stub(bin_dir / "python3", 'exit "${STUB_PYTHON3_RC:-0}"\n')
    _stub(bin_dir / "git", 'echo "main"\n')
    return root, bin_dir


def run_in_scratch(
    argv: list[str],
    root: Path,
    bin_dir: Path,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    env["PATH"] = os.pathsep.join([str(bin_dir), env.get("PATH", "")])
    env.update(extra_env or {})
    return subprocess.run(
        argv,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
        cwd=root,
    )


def seed_hook(root: Path, template: Path) -> Path:
    hook = root / "scripts" / "local" / "checks.sh"
    hook.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(template, hook)
    hook.chmod(0o755)
    return hook


class TestContractConformance:
    """F2: --mode ci|local, exit 0/1, bogus mode fails with usage."""

    @pytest.mark.parametrize("mode", ["ci", "local"])
    def test_none_seed_is_loud_noop(self, tmp_path, mode):
        result = subprocess.run(
            ["bash", str(NONE_SEED), "--mode", mode],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "No project checks configured" in result.stdout

    @pytest.mark.parametrize("template", [PYTHON_SEED, NONE_SEED])
    @pytest.mark.parametrize(
        "argv",
        [
            ["--mode", "bogus"],
            ["--mode"],
            [],
            ["ci"],
        ],
    )
    def test_bogus_or_missing_mode_fails_with_usage(self, tmp_path, template, argv):
        # must fail loudly, never silently pass (spec Test Plan)
        root, bin_dir = make_scratch(tmp_path)
        hook = seed_hook(root, template)
        result = run_in_scratch(["bash", str(hook), *argv], root, bin_dir)
        assert result.returncode == 1
        assert "Usage:" in result.stdout

    @pytest.mark.parametrize("mode_argv", [["--mode", "ci"], ["--mode=ci"]])
    def test_python_seed_passes_on_green_tree(self, tmp_path, mode_argv):
        root, bin_dir = make_scratch(tmp_path)
        hook = seed_hook(root, PYTHON_SEED)
        result = run_in_scratch(["bash", str(hook), *mode_argv], root, bin_dir)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "All CI checks passed" in result.stdout

    def test_python_seed_fails_on_red_tree(self, tmp_path):
        root, bin_dir = make_scratch(tmp_path)
        hook = seed_hook(root, PYTHON_SEED)
        result = run_in_scratch(
            ["bash", str(hook), "--mode", "ci"], root, bin_dir, {"STUB_BLACK_RC": "1"}
        )
        assert result.returncode == 1
        assert "❌ Black: Formatting issues found" in result.stdout


class TestPythonSeedEquivalence:
    """N1 second half: the seeded python hook is the gauntlet MOVED —
    its output matches the built-in's on the same tree."""

    def _dispatch_output(self, tmp_path: Path, name: str, with_hook: bool):
        root, bin_dir = make_scratch(tmp_path / name)
        if with_hook:
            seed_hook(root, PYTHON_SEED)
        result = run_in_scratch(
            ["bash", str(root / "scripts" / "core" / "ci-check.sh")], root, bin_dir
        )
        return result, result.stdout.replace(str(tmp_path / name), "<TMP>")

    def test_seeded_hook_output_equals_builtin(self, tmp_path):
        builtin_result, builtin_out = self._dispatch_output(
            tmp_path, "builtin", with_hook=False
        )
        hook_result, hook_out = self._dispatch_output(
            tmp_path, "hooked", with_hook=True
        )
        assert builtin_result.returncode == 0
        assert hook_result.returncode == 0
        assert builtin_out == hook_out

    def test_seeded_hook_failure_equals_builtin(self, tmp_path):
        root_a, bin_a = make_scratch(tmp_path / "builtin")
        root_b, bin_b = make_scratch(tmp_path / "hooked")
        seed_hook(root_b, PYTHON_SEED)
        env = {"STUB_BLACK_RC": "1"}
        result_a = run_in_scratch(
            ["bash", str(root_a / "scripts" / "core" / "ci-check.sh")],
            root_a,
            bin_a,
            env,
        )
        result_b = run_in_scratch(
            ["bash", str(root_b / "scripts" / "core" / "ci-check.sh")],
            root_b,
            bin_b,
            env,
        )
        assert result_a.returncode == 1
        assert result_b.returncode == 1
        norm_a = result_a.stdout.replace(str(tmp_path / "builtin"), "<TMP>")
        norm_b = result_b.stdout.replace(str(tmp_path / "hooked"), "<TMP>")
        assert norm_a == norm_b

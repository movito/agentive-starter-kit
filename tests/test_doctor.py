"""Tests for `project doctor` (KIT-0046, ADR-0027 P4).

Covers the driver contract (no short-circuit, DOCTOR-line format incl.
colons-in-detail, F3 exit-code mapping) plus fixture coverage for the
version-skew, env-keys, and core.bare checks per the spec's Test Plan.

Fixture patterns follow tests/test_preflight_check.py (stub executables
on a controlled PATH, tmp fixture roots via the DOCTOR_ROOT seam, real
throwaway git repos). The suite-wide GIT_* isolation in conftest.py
covers the git-facing tests — no per-module env handling here.
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECT_SCRIPT = REPO_ROOT / "scripts" / "core" / "project"
DOCTOR_D = REPO_ROOT / "scripts" / "core" / "doctor.d"

if not PROJECT_SCRIPT.exists() or not DOCTOR_D.is_dir():
    pytest.skip("project doctor not present in this checkout", allow_module_level=True)

for tool in ("bash", "git"):
    if shutil.which(tool) is None:
        pytest.skip(f"{tool} not available on PATH", allow_module_level=True)


def _make_check(directory: Path, name: str, body: str) -> Path:
    """Write an executable stub check into a fake doctor.d."""
    path = directory / name
    path.write_text("#!/bin/bash\n" + textwrap.dedent(body), encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


def run_doctor(checks_dir: Path) -> subprocess.CompletedProcess:
    """Run the real driver against a fake doctor.d directory."""
    return subprocess.run(
        [sys.executable, str(PROJECT_SCRIPT), "doctor", f"--dir={checks_dir}"],
        capture_output=True,
        text=True,
        timeout=60,
    )


def doctor_lines(result: subprocess.CompletedProcess) -> list[str]:
    return [ln for ln in result.stdout.splitlines() if ln.startswith("DOCTOR:")]


class TestDriverContract:
    """F1 + F3: iteration, line format, exit codes."""

    def test_failing_check_does_not_short_circuit(self, tmp_path):
        _make_check(tmp_path, "10-boom.sh", 'echo "DOCTOR:boom:FAIL:it broke"\n')
        _make_check(tmp_path, "20-after.sh", 'echo "DOCTOR:after:PASS:still ran"\n')
        result = run_doctor(tmp_path)
        lines = doctor_lines(result)
        assert any(ln.startswith("DOCTOR:boom:FAIL:") for ln in lines)
        assert any(ln.startswith("DOCTOR:after:PASS:") for ln in lines)
        assert result.returncode == 1

    def test_all_pass_and_skip_exits_zero(self, tmp_path):
        _make_check(tmp_path, "10-ok.sh", 'echo "DOCTOR:ok:PASS:fine"\n')
        _make_check(
            tmp_path, "20-skip.sh", 'echo "DOCTOR:skipped:SKIP:not applicable"\n'
        )
        result = run_doctor(tmp_path)
        assert result.returncode == 0

    def test_warn_only_exits_two(self, tmp_path):
        _make_check(tmp_path, "10-ok.sh", 'echo "DOCTOR:ok:PASS:fine"\n')
        _make_check(tmp_path, "20-warn.sh", 'echo "DOCTOR:warned:WARN:heads up"\n')
        result = run_doctor(tmp_path)
        assert result.returncode == 2

    def test_fail_beats_warn(self, tmp_path):
        _make_check(tmp_path, "10-warn.sh", 'echo "DOCTOR:warned:WARN:heads up"\n')
        _make_check(tmp_path, "20-bad.sh", 'echo "DOCTOR:bad:FAIL:broken"\n')
        result = run_doctor(tmp_path)
        assert result.returncode == 1

    def test_detail_may_contain_colons(self, tmp_path):
        detail = "run: gh auth login (see https://cli.github.com)"
        _make_check(tmp_path, "10-c.sh", f'echo "DOCTOR:colons:FAIL:{detail}"\n')
        result = run_doctor(tmp_path)
        line = next(ln for ln in doctor_lines(result) if ":colons:" in ln)
        # parsers split on the first three colons only
        assert line.split(":", 3)[3] == detail

    def test_crashing_check_synthesizes_fail_and_siblings_run(self, tmp_path):
        _make_check(tmp_path, "10-crash.sh", "exit 7\n")
        _make_check(tmp_path, "20-after.sh", 'echo "DOCTOR:after:PASS:still ran"\n')
        result = run_doctor(tmp_path)
        lines = doctor_lines(result)
        assert any(
            ln.startswith("DOCTOR:10-crash.sh:FAIL:") and "exit 7" in ln for ln in lines
        )
        assert any(ln.startswith("DOCTOR:after:PASS:") for ln in lines)
        assert result.returncode == 1

    def test_silent_success_check_is_a_failure(self, tmp_path):
        # exit 0 but no DOCTOR line — the driver must not count it as ok
        _make_check(tmp_path, "10-mute.sh", "exit 0\n")
        result = run_doctor(tmp_path)
        assert any(
            ln.startswith("DOCTOR:10-mute.sh:FAIL:") for ln in doctor_lines(result)
        )
        assert result.returncode == 1

    def test_malformed_verdict_counts_as_failure(self, tmp_path):
        _make_check(tmp_path, "10-odd.sh", 'echo "DOCTOR:odd:MAYBE:who knows"\n')
        result = run_doctor(tmp_path)
        assert result.returncode == 1

    @pytest.mark.parametrize(
        "line",
        [
            "DOCTOR:noise:PASS",  # missing detail field entirely
            "DOCTOR:noise:PASS:",  # empty detail
            "DOCTOR::PASS:detail",  # empty name
        ],
    )
    def test_incomplete_record_cannot_count_as_pass(self, tmp_path, line):
        # F1 field contract: all four fields, non-empty name and detail
        _make_check(tmp_path, "10-bad.sh", f'echo "{line}"\n')
        result = run_doctor(tmp_path)
        assert result.returncode == 1

    def test_non_executable_check_reported(self, tmp_path):
        path = tmp_path / "10-inert.sh"
        path.write_text("#!/bin/bash\necho hi\n", encoding="utf-8")
        path.chmod(0o644)
        result = run_doctor(tmp_path)
        assert any(
            ln.startswith("DOCTOR:10-inert.sh:FAIL:") and "not executable" in ln
            for ln in doctor_lines(result)
        )
        assert result.returncode == 1

    def test_multi_line_check_contributes_all_verdicts(self, tmp_path):
        _make_check(
            tmp_path,
            "10-two.sh",
            'echo "DOCTOR:two-a:PASS:first"\necho "DOCTOR:two-b:WARN:second"\n',
        )
        result = run_doctor(tmp_path)
        assert len(doctor_lines(result)) == 2
        assert result.returncode == 2

    def test_unknown_flag_is_usage_error(self, tmp_path):
        result = subprocess.run(
            [sys.executable, str(PROJECT_SCRIPT), "doctor", "--bogus"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 3

    def test_missing_checks_dir_is_driver_error(self, tmp_path):
        result = run_doctor(tmp_path / "nope")
        assert result.returncode == 3

    def test_empty_checks_dir_is_driver_error(self, tmp_path):
        result = run_doctor(tmp_path)
        assert result.returncode == 3

    def test_summary_line_present(self, tmp_path):
        _make_check(tmp_path, "10-ok.sh", 'echo "DOCTOR:ok:PASS:fine"\n')
        result = run_doctor(tmp_path)
        assert "Doctor: 1 pass, 0 warn, 0 fail, 0 skip" in result.stdout


def run_env_check(root: Path) -> subprocess.CompletedProcess:
    check = DOCTOR_D / "20-env-keys.py"
    return subprocess.run(
        [sys.executable, str(check)],
        env={**os.environ, "DOCTOR_ROOT": str(root)},
        capture_output=True,
        text=True,
        timeout=30,
    )


class TestEnvKeysCheck:
    """F2.2: required keys present AND uncommented (KIT-0032 incident)."""

    ALL_KEYS = (
        "ANTHROPIC_API_KEY=sk-test-anthropic\n"
        "OPENAI_API_KEY=sk-test-openai\n"
        "GEMINI_API_KEY=sk-test-gemini\n"
    )

    def test_missing_env_file_fails(self, tmp_path):
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:FAIL:" in result.stdout
        assert ".env not found" in result.stdout

    def test_commented_required_key_fails(self, tmp_path):
        (tmp_path / ".env").write_text(
            "# ANTHROPIC_API_KEY=sk-test-anthropic\n"
            "OPENAI_API_KEY=sk-test-openai\nGEMINI_API_KEY=sk-test-gemini\n",
            encoding="utf-8",
        )
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:FAIL:" in result.stdout
        assert "ANTHROPIC_API_KEY" in result.stdout

    def test_empty_required_key_fails(self, tmp_path):
        (tmp_path / ".env").write_text(
            "ANTHROPIC_API_KEY=\n" + "OPENAI_API_KEY=x\nGEMINI_API_KEY=y\n",
            encoding="utf-8",
        )
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:FAIL:" in result.stdout

    def test_all_keys_present_passes(self, tmp_path):
        (tmp_path / ".env").write_text(self.ALL_KEYS, encoding="utf-8")
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:PASS:" in result.stdout

    def test_missing_recommended_key_warns(self, tmp_path):
        (tmp_path / ".env").write_text(
            "ANTHROPIC_API_KEY=sk-test-anthropic\nOPENAI_API_KEY=sk-test-openai\n",
            encoding="utf-8",
        )
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:WARN:" in result.stdout
        assert "GEMINI_API_KEY" in result.stdout

    def test_key_values_never_printed(self, tmp_path):
        (tmp_path / ".env").write_text(self.ALL_KEYS, encoding="utf-8")
        result = run_env_check(tmp_path)
        assert "sk-test" not in result.stdout
        assert "sk-test" not in result.stderr


def _stub_executable(path: Path, body: str) -> None:
    path.write_text("#!/bin/bash\n" + textwrap.dedent(body), encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def run_skew_check(root: Path, path_dir: Path) -> subprocess.CompletedProcess:
    """Run 40-version-skew.py with a controlled PATH for pip3/black."""
    check = DOCTOR_D / "40-version-skew.py"
    return subprocess.run(
        [sys.executable, str(check)],
        env={
            **os.environ,
            "DOCTOR_ROOT": str(root),
            "PATH": str(path_dir),
        },
        capture_output=True,
        text=True,
        timeout=30,
    )


def _skew_fixture(tmp_path: Path, venv_ver: str | None, system_ver: str | None):
    """Fixture root with stubbed venv pip and PATH pip3 (canned versions)."""
    root = tmp_path / "root"
    (root / ".venv" / "bin").mkdir(parents=True)
    path_dir = tmp_path / "bin"
    path_dir.mkdir()
    if venv_ver is not None:
        _stub_executable(
            root / ".venv" / "bin" / "pip",
            f'echo "Name: adversarial-workflow"\necho "Version: {venv_ver}"\n',
        )
    if system_ver is not None:
        _stub_executable(
            path_dir / "pip3",
            f'echo "Name: adversarial-workflow"\necho "Version: {system_ver}"\n',
        )
    return root, path_dir


class TestVersionSkewCheck:
    """F2.4: the downgraded-venv fixture (KIT-0044 mutation incident)."""

    def test_downgraded_venv_detected(self, tmp_path):
        root, path_dir = _skew_fixture(tmp_path, venv_ver="0.9.7", system_ver="1.0.1")
        result = run_skew_check(root, path_dir)
        assert "DOCTOR:venv-skew-adversarial:FAIL:" in result.stdout
        assert "0.9.7" in result.stdout and "1.0.1" in result.stdout

    def test_matching_versions_pass(self, tmp_path):
        root, path_dir = _skew_fixture(tmp_path, venv_ver="1.0.1", system_ver="1.0.1")
        result = run_skew_check(root, path_dir)
        assert "DOCTOR:venv-skew-adversarial:PASS:" in result.stdout

    def test_absent_everywhere_skips(self, tmp_path):
        root, path_dir = _skew_fixture(tmp_path, venv_ver=None, system_ver=None)
        result = run_skew_check(root, path_dir)
        assert "DOCTOR:venv-skew-adversarial:SKIP:" in result.stdout

    def test_one_sided_install_skips(self, tmp_path):
        root, path_dir = _skew_fixture(tmp_path, venv_ver="1.0.1", system_ver=None)
        result = run_skew_check(root, path_dir)
        assert "DOCTOR:venv-skew-adversarial:SKIP:" in result.stdout

    def test_black_drift_from_pin_fails(self, tmp_path):
        root, path_dir = _skew_fixture(tmp_path, venv_ver=None, system_ver=None)
        (root / "pyproject.toml").write_text(
            '[project]\nname = "x"\nversion = "0"\n'
            '[project.optional-dependencies]\ndev = ["black==26.3.1"]\n',
            encoding="utf-8",
        )
        _stub_executable(
            root / ".venv" / "bin" / "black",
            'echo "black, 26.1.0 (compiled: yes)"\n',
        )
        result = run_skew_check(root, path_dir)
        assert "DOCTOR:black-pin:FAIL:" in result.stdout
        assert "26.1.0" in result.stdout and "26.3.1" in result.stdout

    def test_black_matching_pin_passes(self, tmp_path):
        root, path_dir = _skew_fixture(tmp_path, venv_ver=None, system_ver=None)
        (root / "pyproject.toml").write_text(
            '[project]\nname = "x"\nversion = "0"\n'
            '[project.optional-dependencies]\ndev = ["black==26.3.1"]\n',
            encoding="utf-8",
        )
        _stub_executable(
            root / ".venv" / "bin" / "black",
            'echo "black, 26.3.1 (compiled: yes)"\n',
        )
        result = run_skew_check(root, path_dir)
        assert "DOCTOR:black-pin:PASS:" in result.stdout

    def test_no_pin_skips(self, tmp_path):
        root, path_dir = _skew_fixture(tmp_path, venv_ver=None, system_ver=None)
        (root / "pyproject.toml").write_text(
            '[project]\nname = "x"\nversion = "0"\n', encoding="utf-8"
        )
        result = run_skew_check(root, path_dir)
        assert "DOCTOR:black-pin:SKIP:" in result.stdout

    def test_activated_venv_on_path_cannot_mask_skew(self, tmp_path):
        """BugBot round 4: with the venv's bin dir FIRST on PATH (an
        activated venv), the system probe must skip it — otherwise both
        sides resolve to the venv and real skew reports PASS."""
        root, path_dir = _skew_fixture(tmp_path, venv_ver="0.9.7", system_ver="1.0.1")
        # simulate activation: venv bin also provides pip3 and leads PATH
        venv_bin_dir = root / ".venv" / "bin"
        _stub_executable(
            venv_bin_dir / "pip3",
            'echo "Name: adversarial-workflow"\necho "Version: 0.9.7"\n',
        )
        check = DOCTOR_D / "40-version-skew.py"
        result = subprocess.run(
            [sys.executable, str(check)],
            env={
                **os.environ,
                "DOCTOR_ROOT": str(root),
                "PATH": os.pathsep.join([str(venv_bin_dir), str(path_dir)]),
            },
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert "DOCTOR:venv-skew-adversarial:FAIL:" in result.stdout
        assert "0.9.7" in result.stdout and "1.0.1" in result.stdout

    def test_alternate_venv_layout_probed(self, tmp_path):
        """BugBot round 4: repos on the venv/ (not .venv/) layout must
        still get a two-sided comparison."""
        root = tmp_path / "root"
        (root / "venv" / "bin").mkdir(parents=True)
        path_dir = tmp_path / "bin"
        path_dir.mkdir()
        _stub_executable(
            root / "venv" / "bin" / "pip",
            'echo "Name: adversarial-workflow"\necho "Version: 0.9.7"\n',
        )
        _stub_executable(
            path_dir / "pip3",
            'echo "Name: adversarial-workflow"\necho "Version: 1.0.1"\n',
        )
        result = run_skew_check(root, path_dir)
        assert "DOCTOR:venv-skew-adversarial:FAIL:" in result.stdout

    def test_activated_alternate_venv_cannot_mask_skew(self, tmp_path):
        """CodeRabbit round 5: the two round-4 fixes combined — an
        ACTIVATED venv/ (non-dot layout) leading PATH with its own pip3
        must still be skipped by the system-side probe."""
        root = tmp_path / "root"
        venv_bin_dir = root / "venv" / "bin"
        venv_bin_dir.mkdir(parents=True)
        path_dir = tmp_path / "bin"
        path_dir.mkdir()
        _stub_executable(
            venv_bin_dir / "pip",
            'echo "Name: adversarial-workflow"\necho "Version: 0.9.7"\n',
        )
        _stub_executable(
            venv_bin_dir / "pip3",
            'echo "Name: adversarial-workflow"\necho "Version: 0.9.7"\n',
        )
        _stub_executable(
            path_dir / "pip3",
            'echo "Name: adversarial-workflow"\necho "Version: 1.0.1"\n',
        )
        check = DOCTOR_D / "40-version-skew.py"
        result = subprocess.run(
            [sys.executable, str(check)],
            env={
                **os.environ,
                "DOCTOR_ROOT": str(root),
                "PATH": os.pathsep.join([str(venv_bin_dir), str(path_dir)]),
            },
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert "DOCTOR:venv-skew-adversarial:FAIL:" in result.stdout


def run_core_bare_check(root: Path) -> subprocess.CompletedProcess:
    check = DOCTOR_D / "70-core-bare.sh"
    return subprocess.run(
        ["bash", str(check)],
        env={**os.environ, "DOCTOR_ROOT": str(root)},
        capture_output=True,
        text=True,
        timeout=30,
    )


class TestCoreBareCheck:
    """F2.7: the GIT_DIR-leak canary (KIT-0043 corruption incident)."""

    @staticmethod
    def _init_repo(path: Path) -> None:
        subprocess.run(["git", "init", "--quiet", str(path)], check=True, timeout=30)

    def test_normal_clone_passes(self, tmp_path):
        self._init_repo(tmp_path)
        result = run_core_bare_check(tmp_path)
        assert "DOCTOR:core-bare:PASS:" in result.stdout

    def test_bare_config_fails(self, tmp_path):
        self._init_repo(tmp_path)
        subprocess.run(
            ["git", "-C", str(tmp_path), "config", "core.bare", "true"],
            check=True,
            timeout=30,
        )
        result = run_core_bare_check(tmp_path)
        assert "DOCTOR:core-bare:FAIL:" in result.stdout

    def test_non_git_dir_skips(self, tmp_path):
        result = run_core_bare_check(tmp_path)
        assert "DOCTOR:core-bare:SKIP:" in result.stdout

    def test_hostile_git_dir_cannot_redirect_the_check(self, tmp_path):
        """A leaked GIT_DIR (the incident class itself) must not blind
        the canary — the check unsets GIT_* before touching git."""
        victim = tmp_path / "victim"
        victim.mkdir()
        self._init_repo(victim)
        decoy = tmp_path / "decoy"
        decoy.mkdir()
        self._init_repo(decoy)
        subprocess.run(
            ["git", "-C", str(decoy), "config", "core.bare", "true"],
            check=True,
            timeout=30,
        )
        check = DOCTOR_D / "70-core-bare.sh"
        result = subprocess.run(
            ["bash", str(check)],
            env={
                **os.environ,
                "DOCTOR_ROOT": str(victim),
                "GIT_DIR": str(decoy / ".git"),
            },
            capture_output=True,
            text=True,
            timeout=30,
        )
        # without the unset, git would inspect the bare decoy and FAIL
        assert "DOCTOR:core-bare:PASS:" in result.stdout

    def test_git_config_env_override_cannot_fake_bare(self, tmp_path):
        """GIT_CONFIG_COUNT/KEY_0/VALUE_0 can rewrite core.bare in-env —
        the full GIT_* scrub must neutralize them (CodeRabbit round 2)."""
        self._init_repo(tmp_path)
        check = DOCTOR_D / "70-core-bare.sh"
        result = subprocess.run(
            [BASH, str(check)],
            env={
                **os.environ,
                "DOCTOR_ROOT": str(tmp_path),
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "core.bare",
                "GIT_CONFIG_VALUE_0": "true",
            },
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert "DOCTOR:core-bare:PASS:" in result.stdout


class TestEnvKeysDuplicates:
    """o3 review: present must win over an earlier commented template line."""

    def test_commented_template_then_real_key_passes(self, tmp_path):
        (tmp_path / ".env").write_text(
            "# ANTHROPIC_API_KEY=template-placeholder\n"
            "ANTHROPIC_API_KEY=sk-test-real\n"
            "OPENAI_API_KEY=x\nGEMINI_API_KEY=y\n",
            encoding="utf-8",
        )
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:PASS:" in result.stdout

    def test_export_prefix_recognized(self, tmp_path):
        (tmp_path / ".env").write_text(
            "export ANTHROPIC_API_KEY=sk-test-real\n"
            "export OPENAI_API_KEY=x\nexport GEMINI_API_KEY=y\n",
            encoding="utf-8",
        )
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:PASS:" in result.stdout

    @pytest.mark.parametrize(
        "value",
        ['""', "''", " # placeholder", '"" # fill me in'],
    )
    def test_quoted_empty_and_comment_only_values_fail(self, tmp_path, value):
        # CodeRabbit round 2: these are unusable but textually non-empty
        (tmp_path / ".env").write_text(
            f"ANTHROPIC_API_KEY={value}\nOPENAI_API_KEY=x\nGEMINI_API_KEY=y\n",
            encoding="utf-8",
        )
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:FAIL:" in result.stdout

    def test_quoted_real_value_passes(self, tmp_path):
        (tmp_path / ".env").write_text(
            'ANTHROPIC_API_KEY="sk-test-real"\nOPENAI_API_KEY=x\nGEMINI_API_KEY=y\n',
            encoding="utf-8",
        )
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:PASS:" in result.stdout


BASH = shutil.which("bash")  # absolute — restricted-PATH runs still need it


def _restricted_bin(base: Path, tools: tuple[str, ...] = ()) -> Path:
    """A PATH dir holding ONLY the named real tools (gh notably absent)."""
    bin_dir = base / "restricted-bin"
    bin_dir.mkdir()
    for tool in tools:
        real = shutil.which(tool)
        assert real, f"{tool} required for this fixture"
        (bin_dir / tool).symlink_to(real)
    return bin_dir


def run_push_sync_check(root: Path, path_dir: Path | None = None):
    """Run 60-push-sync-token.sh; restrict PATH to control gh visibility."""
    env = {**os.environ, "DOCTOR_ROOT": str(root)}
    if path_dir is not None:
        env["PATH"] = str(path_dir)
    check = DOCTOR_D / "60-push-sync-token.sh"
    return subprocess.run(
        [BASH, str(check)],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


class TestPushSyncTokenCheck:
    """F2.6: parked vs active trigger detection (o3: indent tolerance)."""

    @staticmethod
    def _workflow(root: Path, body: str) -> None:
        wf = root / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "sync-core-scripts.yml").write_text(
            textwrap.dedent(body), encoding="utf-8"
        )

    def test_missing_workflow_skips(self, tmp_path):
        result = run_push_sync_check(tmp_path)
        assert "DOCTOR:push-sync-token:SKIP:" in result.stdout
        assert "not present" in result.stdout

    def test_parked_dispatch_only_skips(self, tmp_path):
        self._workflow(
            tmp_path,
            """\
            # The push trigger is disabled: CROSS_REPO_TOKEN was never provisioned
            on:
              workflow_dispatch:
            """,
        )
        result = run_push_sync_check(tmp_path)
        assert "parked — see KIT-0045" in result.stdout

    def test_commented_push_trigger_still_parked(self, tmp_path):
        self._workflow(
            tmp_path,
            """\
            on:
              workflow_dispatch:
              #  push:
              #    branches: [main]
            """,
        )
        result = run_push_sync_check(tmp_path)
        assert "parked — see KIT-0045" in result.stdout

    def test_nested_push_key_outside_on_block_still_parked(self, tmp_path):
        # CodeRabbit round 2: a push: key under jobs: must not read as an
        # active trigger
        self._workflow(
            tmp_path,
            """\
            on:
              workflow_dispatch:
            jobs:
              push:
                runs-on: ubuntu-latest
                steps:
                  - run: echo push
            """,
        )
        result = run_push_sync_check(tmp_path)
        assert "parked — see KIT-0045" in result.stdout

    @pytest.mark.parametrize(
        "body",
        [
            "on:\n  push:\n    branches: [main]\n",  # two-space indent
            "on:\n    push:\n        branches: [main]\n",  # four-space indent
            "on: [push, workflow_dispatch]\n",  # flow style
            "on: push\n",  # scalar style
            "on:\n  push:  # deploy trigger\n    branches: [main]\n",  # trailing comment
            "on: push  # deploy trigger\n",  # scalar + trailing comment
            "on:  # triggers\n  push:\n    branches: [main]\n",  # comment on on: line
        ],
    )
    def test_active_trigger_detected_regardless_of_style(self, tmp_path, body):
        self._workflow(tmp_path, body)
        # PATH with the check's tools (grep, awk) but without gh: an
        # active trigger must degrade to WARN ("cannot verify"), never
        # to the parked SKIP
        bin_dir = _restricted_bin(tmp_path, tools=("grep", "awk"))
        result = run_push_sync_check(tmp_path, path_dir=bin_dir)
        assert "DOCTOR:push-sync-token:WARN:" in result.stdout
        assert "cannot verify" in result.stdout


class TestGhAuthCheck:
    """F2.1: negative paths via PATH-controlled stubs (o3 test gap)."""

    def test_missing_gh_fails(self, tmp_path):
        empty_bin = _restricted_bin(tmp_path)
        check = DOCTOR_D / "10-gh-auth.sh"
        result = subprocess.run(
            [BASH, str(check)],
            env={**os.environ, "PATH": str(empty_bin)},
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert "DOCTOR:gh-auth:FAIL:" in result.stdout
        assert "not installed" in result.stdout

    def test_unauthenticated_gh_fails(self, tmp_path):
        stub_bin = _restricted_bin(tmp_path)
        _stub_executable(
            stub_bin / "gh",
            'if [ "$1 $2" = "auth status" ]; then exit 1; fi\nexit 0\n',
        )
        check = DOCTOR_D / "10-gh-auth.sh"
        result = subprocess.run(
            [BASH, str(check)],
            env={**os.environ, "PATH": str(stub_bin)},
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert "DOCTOR:gh-auth:FAIL:" in result.stdout
        assert "not authenticated" in result.stdout


class TestDriverHardening:
    """Fix-round driver guarantees (fast-v2 + claude-code findings)."""

    def test_dotfiles_in_doctor_d_are_ignored(self, tmp_path):
        _make_check(tmp_path, "10-ok.sh", 'echo "DOCTOR:ok:PASS:fine"\n')
        (tmp_path / ".DS_Store").write_bytes(b"\x00junk")
        result = run_doctor(tmp_path)
        assert result.returncode == 0
        assert len(doctor_lines(result)) == 1

    def test_nonzero_exit_after_output_adds_fail(self, tmp_path):
        _make_check(
            tmp_path,
            "10-halfway.sh",
            'echo "DOCTOR:halfway:PASS:first concern ok"\nexit 5\n',
        )
        result = run_doctor(tmp_path)
        lines = doctor_lines(result)
        assert any(ln.startswith("DOCTOR:halfway:PASS:") for ln in lines)
        assert any(
            ln.startswith("DOCTOR:10-halfway.sh:FAIL:") and "exited 5" in ln
            for ln in lines
        )
        assert result.returncode == 1

    def test_git_env_scrubbed_from_checks(self, tmp_path):
        _make_check(
            tmp_path,
            "10-gitenv.sh",
            'echo "DOCTOR:gitenv:PASS:GIT_DIR=${GIT_DIR:-scrubbed}"\n',
        )
        result = subprocess.run(
            [sys.executable, str(PROJECT_SCRIPT), "doctor", f"--dir={tmp_path}"],
            env={**os.environ, "GIT_DIR": "/tmp/hostile/.git"},
            capture_output=True,
            text=True,
            timeout=60,
        )
        line = next(ln for ln in doctor_lines(result) if ":gitenv:" in ln)
        assert "GIT_DIR=scrubbed" in line

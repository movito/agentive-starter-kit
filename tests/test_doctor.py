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

import json
import os
import re
import shlex
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

    @pytest.mark.parametrize("flag", ["--dir=", "--root="])
    def test_empty_flag_value_is_usage_error(self, tmp_path, flag):
        # Path("") resolves to cwd — an empty value must not silently
        # diagnose the wrong tree (BugBot round 6)
        result = subprocess.run(
            [sys.executable, str(PROJECT_SCRIPT), "doctor", flag],
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


KIT_MARKERS_SRC = REPO_ROOT / "scripts" / "local" / "kit_markers.py"


def _shape_fixture(tmp_path: Path, region: str | None) -> tuple[Path, Path]:
    """A --root fixture with a shape record plus a --dir check set that
    declares shapes (KIT-0048 F3)."""
    root = tmp_path / "root"
    (root / "scripts" / "local").mkdir(parents=True)
    if KIT_MARKERS_SRC.exists():
        shutil.copy(KIT_MARKERS_SRC, root / "scripts" / "local" / "kit_markers.py")
    body = "# My planning repo\n"
    if region is not None:
        body += (
            "\n<!-- BEGIN KIT-LOCAL: kit-install -->\n"
            f"{region}"
            "<!-- END KIT-LOCAL: kit-install -->\n"
        )
    (root / "CLAUDE.md").write_text(body, encoding="utf-8")
    checks = tmp_path / "checks"
    checks.mkdir()
    _make_check(
        checks,
        "10-everywhere.sh",
        "# shapes: single planning\n"
        'echo "DOCTOR:everywhere:PASS:runs in all shapes"\n',
    )
    _make_check(
        checks,
        "20-toolchain.sh",
        "# shapes: single\n" 'echo "DOCTOR:toolchain:PASS:python toolchain check"\n',
    )
    _make_check(
        checks,
        "30-undeclared.sh",
        'echo "DOCTOR:undeclared:PASS:no shapes header"\n',
    )
    return root, checks


def run_doctor_rooted(
    root: Path,
    checks: Path,
    *extra: str,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(PROJECT_SCRIPT),
            "doctor",
            f"--root={root}",
            f"--dir={checks}",
            *extra,
        ],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


@pytest.mark.skipif(
    not KIT_MARKERS_SRC.exists(), reason="kit_markers.py absent (consumer checkout)"
)
class TestShapeInclusion:
    """KIT-0048 F3: per-shape check inclusion via `# shapes:` headers."""

    def test_planning_shape_skips_single_only_checks(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "shape: planning\n")
        result = run_doctor_rooted(root, checks)
        lines = doctor_lines(result)
        assert any(ln.startswith("DOCTOR:everywhere:PASS:") for ln in lines)
        assert any(
            ln.startswith("DOCTOR:20-toolchain.sh:SKIP:") and "shape 'planning'" in ln
            for ln in lines
        )
        # undeclared checks run for every shape — never silently skipped
        assert any(ln.startswith("DOCTOR:undeclared:PASS:") for ln in lines)
        assert result.returncode == 0

    def test_single_shape_runs_full_set(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "shape: single\n")
        result = run_doctor_rooted(root, checks)
        assert len(doctor_lines(result)) == 3
        assert not any("SKIP" in ln for ln in doctor_lines(result))

    def test_absent_region_means_single(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, None)
        result = run_doctor_rooted(root, checks)
        assert len(doctor_lines(result)) == 3
        assert "shape-record" not in result.stdout
        assert result.returncode == 0

    def test_malformed_shape_runs_full_set_and_fails_loud(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "shape: pyramid\n")
        result = run_doctor_rooted(root, checks)
        lines = doctor_lines(result)
        assert any(
            ln.startswith("DOCTOR:shape-record:FAIL:") and "pyramid" in ln
            for ln in lines
        )
        # maximally diagnostic: every check still ran (3 checks + 1 FAIL line)
        assert len(lines) == 4
        assert result.returncode == 1

    def test_region_without_shape_line_fails_loud(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "target_path: ../x\n")
        result = run_doctor_rooted(root, checks)
        assert any(
            ln.startswith("DOCTOR:shape-record:FAIL:") for ln in doctor_lines(result)
        )
        assert result.returncode == 1

    def test_missing_kit_markers_means_single(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "shape: planning\n")
        (root / "scripts" / "local" / "kit_markers.py").unlink()
        result = run_doctor_rooted(root, checks)
        # no reader -> absent -> single -> full set, no shape-record line
        assert len(doctor_lines(result)) == 3
        assert "shape-record" not in result.stdout

    def test_crashing_kit_markers_fails_loud(self, tmp_path):
        """o3 review: a reader failure that is NOT 'region not found'
        must never silently fall back to single."""
        root, checks = _shape_fixture(tmp_path, "shape: planning\n")
        (root / "scripts" / "local" / "kit_markers.py").write_text(
            "import sys\nsys.stderr.write('boom')\nsys.exit(2)\n",
            encoding="utf-8",
        )
        result = run_doctor_rooted(root, checks)
        lines = doctor_lines(result)
        assert any(
            ln.startswith("DOCTOR:shape-record:FAIL:") and "exit 2" in ln
            for ln in lines
        )
        # maximally diagnostic: full set still ran
        assert len(lines) == 4
        assert result.returncode == 1

    def test_empty_shapes_header_runs_everywhere(self, tmp_path):
        """o3 review: an empty declaration must never skip a check in
        every shape forever — it runs everywhere instead."""
        root, checks = _shape_fixture(tmp_path, "shape: planning\n")
        _make_check(
            checks,
            "40-empty.sh",
            "# shapes:\n" 'echo "DOCTOR:empty-header:PASS:still ran"\n',
        )
        result = run_doctor_rooted(root, checks)
        assert any(
            ln.startswith("DOCTOR:empty-header:PASS:") for ln in doctor_lines(result)
        )

    def test_case_variant_header_recognized(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "shape: planning\n")
        _make_check(
            checks,
            "50-case.sh",
            "# SHAPES: single\n" 'echo "DOCTOR:case:PASS:single only"\n',
        )
        result = run_doctor_rooted(root, checks)
        assert any(
            ln.startswith("DOCTOR:50-case.sh:SKIP:") for ln in doctor_lines(result)
        )

    def test_mixed_case_tokens_match(self, tmp_path):
        """CodeRabbit round 2: '# Shapes: Planning' must match shape
        'planning' — tokens are lowercased, not just the keyword."""
        root, checks = _shape_fixture(tmp_path, "shape: planning\n")
        _make_check(
            checks,
            "55-mixedcase.sh",
            "# Shapes: Single Planning\n"
            'echo "DOCTOR:mixedcase:PASS:runs in planning"\n',
        )
        result = run_doctor_rooted(root, checks)
        assert any(
            ln.startswith("DOCTOR:mixedcase:PASS:") for ln in doctor_lines(result)
        )

    def test_header_found_after_long_banner(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "shape: planning\n")
        banner = "".join(f"# banner line {i} {'x' * 40}\n" for i in range(20))
        _make_check(
            checks,
            "60-banner.sh",
            banner + "# shapes: single\n" 'echo "DOCTOR:banner:PASS:x"\n',
        )
        result = run_doctor_rooted(root, checks)
        assert any(
            ln.startswith("DOCTOR:60-banner.sh:SKIP:") for ln in doctor_lines(result)
        )


def _profile_fixture(tmp_path: Path, region: str | None) -> tuple[Path, Path]:
    """A --root fixture with an install record plus a --dir check set
    that declares profiles (KIT-0050 F5)."""
    root = tmp_path / "root"
    (root / "scripts" / "local").mkdir(parents=True)
    if KIT_MARKERS_SRC.exists():
        shutil.copy(KIT_MARKERS_SRC, root / "scripts" / "local" / "kit_markers.py")
    body = "# My repo\n"
    if region is not None:
        body += (
            "\n<!-- BEGIN KIT-LOCAL: kit-install -->\n"
            f"{region}"
            "<!-- END KIT-LOCAL: kit-install -->\n"
        )
    (root / "CLAUDE.md").write_text(body, encoding="utf-8")
    checks = tmp_path / "checks"
    checks.mkdir()
    _make_check(
        checks,
        "10-anywhere.sh",
        'echo "DOCTOR:anywhere:PASS:no profiles header"\n',
    )
    _make_check(
        checks,
        "20-pytool.sh",
        "# profiles: python\n" 'echo "DOCTOR:pytool:PASS:python toolchain check"\n',
    )
    return root, checks


@pytest.mark.skipif(
    not KIT_MARKERS_SRC.exists(), reason="kit_markers.py absent (consumer checkout)"
)
class TestProfileInclusion:
    """KIT-0050 F5: per-profile check inclusion via `# profiles:` headers."""

    def test_python_profile_runs_toolchain_checks(self, tmp_path):
        root, checks = _profile_fixture(tmp_path, "shape: single\nprofile: python\n")
        result = run_doctor_rooted(root, checks)
        assert len(doctor_lines(result)) == 2
        assert not any("SKIP" in ln for ln in doctor_lines(result))
        assert result.returncode == 0

    def test_none_profile_skips_python_only_checks(self, tmp_path):
        root, checks = _profile_fixture(tmp_path, "shape: single\nprofile: none\n")
        result = run_doctor_rooted(root, checks)
        lines = doctor_lines(result)
        assert any(ln.startswith("DOCTOR:anywhere:PASS:") for ln in lines)
        assert any(
            ln.startswith("DOCTOR:20-pytool.sh:SKIP:")
            and "profile 'none'" in ln
            and "python" in ln
            for ln in lines
        )
        assert result.returncode == 0

    def test_planning_defaults_to_none(self, tmp_path):
        # a pre-KIT-0050 planning record (no profile: line) must scope
        # toolchain checks out — back-compat default planning -> none
        root, checks = _profile_fixture(tmp_path, "shape: planning\n")
        result = run_doctor_rooted(root, checks)
        assert any(
            ln.startswith("DOCTOR:20-pytool.sh:SKIP:") and "profile 'none'" in ln
            for ln in doctor_lines(result)
        )
        assert "profile-record" not in result.stdout

    def test_single_defaults_to_python(self, tmp_path):
        root, checks = _profile_fixture(tmp_path, "shape: single\n")
        result = run_doctor_rooted(root, checks)
        assert len(doctor_lines(result)) == 2
        assert not any("SKIP" in ln for ln in doctor_lines(result))
        assert "profile-record" not in result.stdout

    def test_absent_region_defaults_to_python(self, tmp_path):
        root, checks = _profile_fixture(tmp_path, None)
        result = run_doctor_rooted(root, checks)
        assert len(doctor_lines(result)) == 2
        assert "profile-record" not in result.stdout
        assert result.returncode == 0

    def test_malformed_profile_runs_full_set_and_fails_loud(self, tmp_path):
        root, checks = _profile_fixture(tmp_path, "shape: single\nprofile: elixir\n")
        result = run_doctor_rooted(root, checks)
        lines = doctor_lines(result)
        assert any(
            ln.startswith("DOCTOR:profile-record:FAIL:") and "elixir" in ln
            for ln in lines
        )
        # maximally diagnostic: both checks still ran (2 + 1 FAIL line)
        assert len(lines) == 3
        assert result.returncode == 1

    def test_planning_python_combination_fails_loud(self, tmp_path):
        # the P3 matrix pairing: planning forces none — honoring the
        # illegal combination or silently coercing would both mask
        root, checks = _profile_fixture(tmp_path, "shape: planning\nprofile: python\n")
        result = run_doctor_rooted(root, checks)
        lines = doctor_lines(result)
        assert any(
            ln.startswith("DOCTOR:profile-record:FAIL:") and "not legal" in ln
            for ln in lines
        )
        # maximally diagnostic (the KIT-0048 pattern): profile is None,
        # so the FULL set still runs alongside the FAIL — 2 checks + 1
        assert any(ln.startswith("DOCTOR:pytool:PASS:") for ln in lines)
        assert len(lines) == 3
        assert result.returncode == 1

    def test_empty_profile_value_fails_loud(self, tmp_path):
        # fast-v2 review gap: `profile:` with an empty value is a
        # malformed record (fail loud), NOT an absent line (default)
        root, checks = _profile_fixture(tmp_path, "shape: single\nprofile:\n")
        result = run_doctor_rooted(root, checks)
        assert any(
            ln.startswith("DOCTOR:profile-record:FAIL:") for ln in doctor_lines(result)
        )
        assert result.returncode == 1

    def test_malformed_shape_does_not_double_fail(self, tmp_path):
        # one unreadable shape must produce ONE record FAIL, with the
        # profile-scoped check still running (profile None = run all)
        root, checks = _profile_fixture(tmp_path, "shape: pyramid\n")
        result = run_doctor_rooted(root, checks)
        lines = doctor_lines(result)
        assert any(ln.startswith("DOCTOR:shape-record:FAIL:") for ln in lines)
        assert "profile-record" not in result.stdout
        assert any(ln.startswith("DOCTOR:pytool:PASS:") for ln in lines)

    def test_real_version_skew_check_is_profile_scoped(self):
        # F5 on the real file: the toolchain checks (venv skew + black
        # pin) declare `# profiles: python` and no shape scoping
        head = (DOCTOR_D / "40-version-skew.py").read_text(encoding="utf-8")
        head = "\n".join(head.splitlines()[:30])
        assert "# profiles: python" in head
        assert "# shapes:" not in head

    def test_malformed_shape_never_honors_valid_profile(self, tmp_path):
        """BugBot PR #80: with an unreadable shape, a syntactically
        valid profile must NOT be honored — its legality is shape-
        dependent, and honoring it would SKIP checks the shape-record
        FAIL just promised to run (the masking class)."""
        root, checks = _profile_fixture(tmp_path, "shape: pyramid\nprofile: none\n")
        result = run_doctor_rooted(root, checks)
        lines = doctor_lines(result)
        assert any(ln.startswith("DOCTOR:shape-record:FAIL:") for ln in lines)
        # the python-scoped check RAN despite profile: none in the record
        assert any(ln.startswith("DOCTOR:pytool:PASS:") for ln in lines)
        assert not any(":SKIP:" in ln for ln in lines)
        assert result.returncode == 1


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

    # TASK_PREFIX included: without it the identity WARN (KIT-0084)
    # would mask the PASS these fixtures assert
    ALL_KEYS = (
        "ANTHROPIC_API_KEY=sk-test-anthropic\n"
        "OPENAI_API_KEY=sk-test-openai\n"
        "GEMINI_API_KEY=sk-test-gemini\n"
        "TASK_PREFIX=DEMO\n"
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
            "ANTHROPIC_API_KEY=sk-test-anthropic\nOPENAI_API_KEY=sk-test-openai\n"
            "TASK_PREFIX=DEMO\n",
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


class TestTaskPrefixWarn:
    """KIT-0084 F2: TASK_PREFIX empty, missing, or the old 'TASK'
    placeholder is silently-wrong identity — the doctor says so."""

    KEYS = TestEnvKeysCheck.ALL_KEYS  # includes TASK_PREFIX=DEMO

    def _without_prefix(self):
        return self.KEYS.replace("TASK_PREFIX=DEMO\n", "")

    @pytest.mark.parametrize("line", ["TASK_PREFIX=\n", "TASK_PREFIX=TASK\n", ""])
    def test_unset_or_placeholder_warns(self, tmp_path, line):
        (tmp_path / ".env").write_text(self._without_prefix() + line, encoding="utf-8")
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:WARN:" in result.stdout
        assert "TASK_PREFIX" in result.stdout
        assert "intake" in result.stdout  # the fix's decision point is named

    def test_real_prefix_passes(self, tmp_path):
        (tmp_path / ".env").write_text(self.KEYS, encoding="utf-8")
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:PASS:" in result.stdout

    def test_real_prefix_value_not_printed(self, tmp_path):
        (tmp_path / ".env").write_text(
            self._without_prefix() + "TASK_PREFIX=XZQ9\n", encoding="utf-8"
        )
        result = run_env_check(tmp_path)
        assert "XZQ9" not in result.stdout + result.stderr

    def test_combined_with_evaluator_warning_one_line(self, tmp_path):
        (tmp_path / ".env").write_text(
            "ANTHROPIC_API_KEY=sk-test-anthropic\nOPENAI_API_KEY=sk-test-openai\n",
            encoding="utf-8",
        )
        result = run_env_check(tmp_path)
        warn_lines = [
            ln
            for ln in result.stdout.splitlines()
            if ln.startswith("DOCTOR:env-keys:WARN:")
        ]
        assert len(warn_lines) == 1  # one check, one protocol line
        assert "GEMINI_API_KEY" in warn_lines[0]
        assert "TASK_PREFIX" in warn_lines[0]

    def test_commented_prefix_line_warns(self, tmp_path):
        (tmp_path / ".env").write_text(
            self._without_prefix() + "# TASK_PREFIX=DEMO\n", encoding="utf-8"
        )
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:WARN:" in result.stdout
        assert "TASK_PREFIX" in result.stdout

    def test_valid_then_placeholder_warns_last_wins(self, tmp_path):
        """CodeRabbit (KIT-0084): dotenv parsers are last-assignment-
        wins — a trailing placeholder overrides an earlier real value,
        so the doctor must warn."""
        (tmp_path / ".env").write_text(
            self._without_prefix() + "TASK_PREFIX=DEMO\nTASK_PREFIX=TASK\n",
            encoding="utf-8",
        )
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:WARN:" in result.stdout
        assert "TASK_PREFIX" in result.stdout

    def test_valid_then_empty_warns_last_wins(self, tmp_path):
        (tmp_path / ".env").write_text(
            self._without_prefix() + "TASK_PREFIX=DEMO\nTASK_PREFIX=\n",
            encoding="utf-8",
        )
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:WARN:" in result.stdout
        assert "TASK_PREFIX" in result.stdout

    def test_empty_then_valid_passes_last_wins(self, tmp_path):
        """The copy-template-then-append layout: the template's empty
        line comes first, the operator's real value last — last wins."""
        (tmp_path / ".env").write_text(
            self._without_prefix() + "TASK_PREFIX=\nTASK_PREFIX=DEMO\n",
            encoding="utf-8",
        )
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:PASS:" in result.stdout

    def test_quoted_value_with_hash_not_truncated(self, tmp_path):
        """fast-v2 review: a '#' inside quotes is data, not a comment —
        the old split-then-unquote order corrupted such values."""
        (tmp_path / ".env").write_text(
            self._without_prefix() + 'TASK_PREFIX="PROJ#1"\n', encoding="utf-8"
        )
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:PASS:" in result.stdout

    def test_quoted_key_with_hash_is_present(self, tmp_path):
        (tmp_path / ".env").write_text(
            'ANTHROPIC_API_KEY="sk-test#part"\nOPENAI_API_KEY=x\n'
            "GEMINI_API_KEY=y\nTASK_PREFIX=DEMO\n",
            encoding="utf-8",
        )
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:PASS:" in result.stdout


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
        assert "0.9.7" in result.stdout and "1.0.1" in result.stdout

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
        assert "0.9.7" in result.stdout and "1.0.1" in result.stdout


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
            "OPENAI_API_KEY=x\nGEMINI_API_KEY=y\nTASK_PREFIX=DEMO\n",
            encoding="utf-8",
        )
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:PASS:" in result.stdout

    def test_export_prefix_recognized(self, tmp_path):
        (tmp_path / ".env").write_text(
            "export ANTHROPIC_API_KEY=sk-test-real\n"
            "export OPENAI_API_KEY=x\nexport GEMINI_API_KEY=y\n"
            "export TASK_PREFIX=DEMO\n",
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
            'ANTHROPIC_API_KEY="sk-test-real"\nOPENAI_API_KEY=x\nGEMINI_API_KEY=y\n'
            "TASK_PREFIX=DEMO\n",
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


@pytest.mark.skipif(
    not KIT_MARKERS_SRC.exists(), reason="kit_markers.py absent (consumer checkout)"
)
class TestBotsRecord:
    """KIT-0056 F1/F4: the bots declaration in the kit-install record.
    It scopes no checks — but an invalid line fails loud
    (DOCTOR:bots-record:FAIL), because a typo silently read as
    "declared absent" could SKIP preflight gates it should not."""

    def test_valid_bots_line_is_silent(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "shape: single\nbots: none\n")
        result = run_doctor_rooted(root, checks)
        assert "bots-record" not in result.stdout
        assert result.returncode == 0

    def test_invalid_bots_value_fails_loud(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "shape: single\nbots: horsebot\n")
        result = run_doctor_rooted(root, checks)
        lines = doctor_lines(result)
        assert any(
            ln.startswith("DOCTOR:bots-record:FAIL:") and "horsebot" in ln
            for ln in lines
        )
        # maximally diagnostic: all 3 checks still ran (+ the FAIL line)
        assert len(lines) == 4
        assert result.returncode == 1

    def test_none_combined_with_bot_fails_loud(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "shape: single\nbots: none bugbot\n")
        result = run_doctor_rooted(root, checks)
        assert any(
            ln.startswith("DOCTOR:bots-record:FAIL:") for ln in doctor_lines(result)
        )
        assert result.returncode == 1

    def test_absent_bots_line_is_not_an_error(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "shape: single\n")
        result = run_doctor_rooted(root, checks)
        assert "bots-record" not in result.stdout
        assert result.returncode == 0


def _preset_env(tmp_path: Path, content: str | None) -> dict[str, str]:
    """Env with AGENTIVE_KIT_CONFIG_DIR pointing at a scratch config
    home (KIT-0058); content=None leaves the preset absent. Never the
    real sibling folder."""
    cfg = tmp_path / "agentive-config"
    cfg.mkdir(parents=True, exist_ok=True)
    if content is not None:
        (cfg / "preset").write_text(content, encoding="utf-8")
    return {**os.environ, "AGENTIVE_KIT_CONFIG_DIR": str(cfg)}


def preset_lines(result: subprocess.CompletedProcess) -> list[str]:
    return [ln for ln in result.stdout.splitlines() if ln.startswith("PRESET:")]


@pytest.mark.skipif(
    not KIT_MARKERS_SRC.exists(), reason="kit_markers.py absent (consumer checkout)"
)
class TestAgainstPreset:
    """KIT-0056 F8: `doctor --against-preset` reports record↔preset
    divergence as PRESET:<field>:INFO lines — INFO only, never
    WARN/FAIL, exit code never affected (a deliberately-lean project
    is not wrong)."""

    def test_divergence_is_info_only_exit_unchanged(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "shape: single\nprofile: python\n")
        # planning+none is a LEGAL preset pair that diverges from the
        # record (the illegal planning+python pair has its own test)
        env = _preset_env(tmp_path, "shape: planning\nprofile: none\n")
        result = run_doctor_rooted(root, checks, "--against-preset", env=env)
        lines = preset_lines(result)
        assert any(
            ln.startswith("PRESET:shape:INFO:") and "planning" in ln for ln in lines
        ), result.stdout
        assert not any(":WARN" in ln or ":FAIL" in ln for ln in lines)
        assert result.returncode == 0  # checks all pass; divergence adds nothing

    def test_match_reported(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "shape: single\nprofile: python\n")
        env = _preset_env(tmp_path, "shape: single\nprofile: python\n")
        result = run_doctor_rooted(root, checks, "--against-preset", env=env)
        assert any(
            "record matches the preset" in ln for ln in preset_lines(result)
        ), result.stdout

    def test_bots_default_comparison_names_the_default(self, tmp_path):
        # record has no bots line (= both expected, defaulted); preset
        # says none → divergence INFO that names the defaulting
        root, checks = _shape_fixture(tmp_path, "shape: single\n")
        env = _preset_env(tmp_path, "bots: none\n")
        result = run_doctor_rooted(root, checks, "--against-preset", env=env)
        bots_info = [ln for ln in preset_lines(result) if ln.startswith("PRESET:bots:")]
        assert bots_info, result.stdout
        assert "defaulted" in bots_info[0]
        assert "coderabbit bugbot" in bots_info[0]

    def test_no_preset_file_reported(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "shape: single\n")
        env = _preset_env(tmp_path, None)
        result = run_doctor_rooted(root, checks, "--against-preset", env=env)
        assert any(
            "no preset found" in ln for ln in preset_lines(result)
        ), result.stdout
        assert result.returncode == 0

    def test_malformed_preset_skips_comparison_loudly(self, tmp_path):
        # loud (names the line), and the WHOLE comparison is skipped —
        # a partial read could report agreement on unparsed fields
        root, checks = _shape_fixture(tmp_path, "shape: single\n")
        env = _preset_env(tmp_path, "shape: single\nnot a preset line\n")
        result = run_doctor_rooted(root, checks, "--against-preset", env=env)
        lines = preset_lines(result)
        assert any(
            "malformed at line 2" in ln and "comparison skipped" in ln for ln in lines
        ), result.stdout
        assert not any(ln.startswith("PRESET:shape:") for ln in lines)
        assert result.returncode == 0

    def test_unreadable_record_skips_comparison(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "shape: pyramid\n")
        env = _preset_env(tmp_path, "shape: single\n")
        result = run_doctor_rooted(root, checks, "--against-preset", env=env)
        assert any(
            "record unreadable" in ln and "comparison skipped" in ln
            for ln in preset_lines(result)
        ), result.stdout
        assert result.returncode == 1  # from the record FAIL, not the preset

    def test_without_flag_no_preset_lines(self, tmp_path):
        # N1: plain doctor output is byte-free of PRESET: lines even
        # with a preset present on the machine
        root, checks = _shape_fixture(tmp_path, "shape: single\n")
        env = _preset_env(tmp_path, "shape: planning\n")
        result = run_doctor_rooted(root, checks, env=env)
        assert preset_lines(result) == []


@pytest.mark.skipif(
    not KIT_MARKERS_SRC.exists(), reason="kit_markers.py absent (consumer checkout)"
)
class TestBotsReaderTolerance:
    """fast-v2 round 1: every bots reader shares one tolerance rule —
    comma- or space-separated, any case. A declaration must never be
    valid to the door but invalid to doctor (or vice versa)."""

    def test_comma_and_case_variants_are_valid(self, tmp_path):
        root, checks = _shape_fixture(
            tmp_path, "shape: single\nbots: CodeRabbit,BugBot\n"
        )
        result = run_doctor_rooted(root, checks)
        assert "bots-record" not in result.stdout
        assert result.returncode == 0

    def test_normalized_form_used_in_comparison(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "shape: single\nbots: BUGBOT\n")
        env = _preset_env(tmp_path, "bots: bugbot,coderabbit\n")
        result = run_doctor_rooted(root, checks, "--against-preset", env=env)
        bots_info = [ln for ln in preset_lines(result) if ln.startswith("PRESET:bots:")]
        assert bots_info, result.stdout
        assert "'bugbot'" in bots_info[0]  # record normalized
        assert "'coderabbit bugbot'" in bots_info[0]  # preset normalized

    def test_duplicate_preset_key_skips_comparison(self, tmp_path):
        # same duplicate rule as the door's load_preset — comparing
        # against a value the door would refuse to load would mislead
        root, checks = _shape_fixture(tmp_path, "shape: single\n")
        env = _preset_env(tmp_path, "shape: single\nshape: planning\n")
        result = run_doctor_rooted(root, checks, "--against-preset", env=env)
        lines = preset_lines(result)
        assert any(
            "duplicate preset key 'shape'" in ln and "line 2" in ln for ln in lines
        ), result.stdout
        assert any("comparison skipped" in ln for ln in lines)
        assert not any(ln.startswith("PRESET:shape:INFO:record") for ln in lines)
        assert result.returncode == 0

    def test_empty_bots_line_fails_loud(self, tmp_path):
        # a PRESENT-but-empty bots: line is invalid, not absent —
        # matching the preflight reader's NOTICE for the same content
        root, checks = _shape_fixture(tmp_path, "shape: single\nbots:\n")
        result = run_doctor_rooted(root, checks)
        assert any(
            ln.startswith("DOCTOR:bots-record:FAIL:") for ln in doctor_lines(result)
        ), result.stdout
        assert result.returncode == 1

    def test_invalid_preset_bots_value_skips_that_field(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "shape: single\nbots: none\n")
        env = _preset_env(tmp_path, "bots: horsebot\n")
        result = run_doctor_rooted(root, checks, "--against-preset", env=env)
        bots_info = [ln for ln in preset_lines(result) if ln.startswith("PRESET:bots:")]
        assert bots_info, result.stdout
        assert "invalid" in bots_info[0]
        assert "horsebot" in bots_info[0]
        assert result.returncode == 0  # INFO only, never an exit change

    def test_unreadable_preset_file_skips_comparison(self, tmp_path):
        if os.geteuid() == 0:
            pytest.skip("permission checks are meaningless as root")
        root, checks = _shape_fixture(tmp_path, "shape: single\n")
        env = _preset_env(tmp_path, "shape: single\n")
        preset = Path(env["AGENTIVE_KIT_CONFIG_DIR"]) / "preset"
        preset.chmod(0o000)
        try:
            result = run_doctor_rooted(root, checks, "--against-preset", env=env)
            assert any(
                "preset unreadable" in ln and "comparison skipped" in ln
                for ln in preset_lines(result)
            ), result.stdout
            assert result.returncode == 0
        finally:
            preset.chmod(0o600)

    def test_indented_record_lines_still_read(self, tmp_path):
        # o3 (this PR): all readers tolerate harmless indentation —
        # this pins the Python side (the shell readers have their own
        # pins in test_preflight_check / test_setup_door)
        root, checks = _shape_fixture(tmp_path, "  shape: single\n  bots: none\n")
        result = run_doctor_rooted(root, checks)
        assert "shape-record" not in result.stdout
        assert "bots-record" not in result.stdout
        assert result.returncode == 0

    def test_duplicate_bot_names_collapse(self, tmp_path):
        # _normalize_bots dedupes via canonical-order membership — a
        # repeated name is valid and normalizes to one occurrence
        root, checks = _shape_fixture(
            tmp_path, "shape: single\nbots: coderabbit coderabbit\n"
        )
        env = _preset_env(tmp_path, "bots: coderabbit\n")
        result = run_doctor_rooted(root, checks, "--against-preset", env=env)
        assert "bots-record" not in result.stdout
        assert any(
            "record matches the preset" in ln for ln in preset_lines(result)
        ), result.stdout

    @pytest.mark.parametrize(
        "preset,field,bad",
        [
            ("shape: pyramid\n", "shape", "pyramid"),
            ("profile: elixir\n", "profile", "elixir"),
        ],
    )
    def test_invalid_preset_shape_profile_skips_field(
        self, tmp_path, preset, field, bad
    ):
        # CodeRabbit PR #83: a value the door would refuse to install
        # reads as malformed preset data, never legitimate divergence
        root, checks = _shape_fixture(tmp_path, "shape: single\n")
        env = _preset_env(tmp_path, preset)
        result = run_doctor_rooted(root, checks, "--against-preset", env=env)
        lines = preset_lines(result)
        assert any(
            f"preset {field} value invalid" in ln and bad in ln for ln in lines
        ), result.stdout
        assert not any(f"PRESET:{field}:INFO:record" in ln for ln in lines)
        assert result.returncode == 0

    def test_illegal_preset_pair_skips_both_fields(self, tmp_path):
        root, checks = _shape_fixture(tmp_path, "shape: single\n")
        env = _preset_env(tmp_path, "shape: planning\nprofile: python\n")
        result = run_doctor_rooted(root, checks, "--against-preset", env=env)
        lines = preset_lines(result)
        assert any("illegal pair" in ln for ln in lines), result.stdout
        assert not any(ln.startswith("PRESET:shape:INFO:record") for ln in lines)
        assert not any(ln.startswith("PRESET:profile:INFO:record") for ln in lines)
        assert result.returncode == 0


def run_config_home_check(
    root: Path,
    cfg: Path | None,
    path_dir: Path | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """Run 90-config-home.sh directly. cfg=None points the override at
    a nonexistent scratch path — never the real sibling folder — and a
    hermetic XDG keeps the operator's real legacy location out (N1)."""
    env = {
        **os.environ,
        "DOCTOR_ROOT": str(root),
        "XDG_CONFIG_HOME": str(root / "no-such-xdg"),
        "AGENTIVE_KIT_CONFIG_DIR": str(cfg if cfg else root / "no-such-config"),
    }
    if path_dir is not None:
        env["PATH"] = str(path_dir)
    if extra_env:
        env.update(extra_env)
    check = DOCTOR_D / "90-config-home.sh"
    return subprocess.run(
        [BASH, str(check)],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


class TestConfigHomeCheck:
    """KIT-0058 F3: config-home guardrails — private-remote assertion
    (WARN on public or on gh failure, naming the risk), tracked
    env.source = FAIL, no git / no remote = PASS, plus the F4
    legacy-location notice retired at 0.9.0 (KIT-0059)."""

    # PATH set for the gh-controlled fixtures: the check's external
    # tools, with gh's presence decided per test
    CHECK_TOOLS = ("git", "grep", "head", "tr", "dirname")

    @staticmethod
    def _repo(cfg: Path, remote: str | None = None) -> None:
        cfg.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init", "--quiet", str(cfg)], check=True, timeout=30)
        if remote is not None:
            subprocess.run(
                ["git", "-C", str(cfg), "remote", "add", "origin", remote],
                check=True,
                timeout=30,
            )

    def test_absent_config_home_skips_naming_path(self, tmp_path):
        result = run_config_home_check(tmp_path, None)
        assert "DOCTOR:config-home:SKIP:" in result.stdout
        assert "no-such-config" in result.stdout  # the path is named
        assert "/setup-preset" in result.stdout  # and the way in

    def test_plain_folder_passes(self, tmp_path):
        cfg = tmp_path / "agentive-config"
        cfg.mkdir()
        result = run_config_home_check(tmp_path, cfg)
        assert "DOCTOR:config-home:PASS:" in result.stdout
        assert "no git repo" in result.stdout

    def test_repo_without_remote_passes(self, tmp_path):
        cfg = tmp_path / "agentive-config"
        self._repo(cfg)
        result = run_config_home_check(tmp_path, cfg)
        assert "DOCTOR:config-home:PASS:" in result.stdout
        assert "no remote" in result.stdout

    def test_private_remote_passes(self, tmp_path):
        cfg = tmp_path / "agentive-config"
        self._repo(cfg, "https://github.com/example/cfg.git")
        bin_dir = _restricted_bin(tmp_path, tools=self.CHECK_TOOLS)
        # UPPERCASE pins the case-normalization (GraphQL-style output)
        _stub_executable(bin_dir / "gh", 'echo "PRIVATE"\n')
        result = run_config_home_check(tmp_path, cfg, path_dir=bin_dir)
        assert "DOCTOR:config-home:PASS:" in result.stdout
        assert "private" in result.stdout

    def test_public_remote_warns(self, tmp_path):
        cfg = tmp_path / "agentive-config"
        self._repo(cfg, "https://github.com/example/cfg.git")
        bin_dir = _restricted_bin(tmp_path, tools=self.CHECK_TOOLS)
        _stub_executable(bin_dir / "gh", 'echo "public"\n')
        result = run_config_home_check(tmp_path, cfg, path_dir=bin_dir)
        assert "DOCTOR:config-home:WARN:" in result.stdout
        assert "exposed" in result.stdout  # the risk is named
        assert "FAIL" not in result.stdout

    def test_gh_missing_warns_never_fails(self, tmp_path):
        cfg = tmp_path / "agentive-config"
        self._repo(cfg, "https://github.com/example/cfg.git")
        bin_dir = _restricted_bin(tmp_path, tools=self.CHECK_TOOLS)
        result = run_config_home_check(tmp_path, cfg, path_dir=bin_dir)
        assert "DOCTOR:config-home:WARN:" in result.stdout
        assert "gh not installed" in result.stdout
        assert "FAIL" not in result.stdout

    def test_gh_failure_warns_naming_the_risk(self, tmp_path):
        cfg = tmp_path / "agentive-config"
        self._repo(cfg, "https://github.com/example/cfg.git")
        bin_dir = _restricted_bin(tmp_path, tools=self.CHECK_TOOLS)
        _stub_executable(bin_dir / "gh", "exit 1\n")
        result = run_config_home_check(tmp_path, cfg, path_dir=bin_dir)
        assert "DOCTOR:config-home:WARN:" in result.stdout
        assert "cannot verify" in result.stdout
        assert "exposed" in result.stdout

    def test_tracked_env_source_fails(self, tmp_path):
        cfg = tmp_path / "agentive-config"
        self._repo(cfg)
        (cfg / "env.source").write_text("KEY=secret\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(cfg), "add", "env.source"], check=True, timeout=30
        )
        result = run_config_home_check(tmp_path, cfg)
        assert "DOCTOR:config-home:FAIL:" in result.stdout
        assert "env.source is TRACKED" in result.stdout
        assert "rm --cached" in result.stdout  # the way out is named

    def test_untracked_env_source_is_fine(self, tmp_path):
        cfg = tmp_path / "agentive-config"
        self._repo(cfg)
        (cfg / "env.source").write_text("KEY=secret\n", encoding="utf-8")
        result = run_config_home_check(tmp_path, cfg)
        assert "DOCTOR:config-home:FAIL:" not in result.stdout
        assert "DOCTOR:config-home:PASS:" in result.stdout

    def test_hostile_git_dir_cannot_redirect_the_check(self, tmp_path):
        # the KIT-0043 leak class: a leaked GIT_DIR pointing at a repo
        # WITH a tracked env.source must not blind the check to the
        # real (clean) config home
        decoy = tmp_path / "decoy"
        self._repo(decoy)
        (decoy / "env.source").write_text("KEY=secret\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(decoy), "add", "env.source"],
            check=True,
            timeout=30,
        )
        cfg = tmp_path / "agentive-config"
        self._repo(cfg)
        result = run_config_home_check(
            tmp_path, cfg, extra_env={"GIT_DIR": str(decoy / ".git")}
        )
        assert "DOCTOR:config-home:PASS:" in result.stdout
        assert "FAIL" not in result.stdout

    def test_derivation_without_override_names_the_sibling(self, tmp_path):
        """The check's own resolution (no override): parent of the
        DOCTOR_ROOT's primary clone + /agentive-config — the same rule
        the door and the project script pin in their equivalence test."""
        parent = tmp_path / "parent"
        kit = parent / "kit"
        kit.mkdir(parents=True)
        subprocess.run(["git", "init", "--quiet", str(kit)], check=True, timeout=30)
        (parent / "agentive-config").mkdir()
        env = {
            **os.environ,
            "DOCTOR_ROOT": str(kit),
            "XDG_CONFIG_HOME": str(tmp_path / "no-such-xdg"),
        }
        env.pop("AGENTIVE_KIT_CONFIG_DIR", None)
        check = DOCTOR_D / "90-config-home.sh"
        result = subprocess.run(
            [BASH, str(check)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert "DOCTOR:config-home:PASS:" in result.stdout
        assert str(parent / "agentive-config") in result.stdout

    def test_non_git_root_skips(self, tmp_path):
        env = {
            **os.environ,
            "DOCTOR_ROOT": str(tmp_path),
            "XDG_CONFIG_HOME": str(tmp_path / "no-such-xdg"),
        }
        env.pop("AGENTIVE_KIT_CONFIG_DIR", None)
        check = DOCTOR_D / "90-config-home.sh"
        result = subprocess.run(
            [BASH, str(check)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert "DOCTOR:config-home:SKIP:" in result.stdout
        assert "not a git clone" in result.stdout

    def test_tilde_override_expanded_python_side(self, tmp_path):
        # o3 (this PR): the Python mirror expands a literal leading
        # tilde exactly like the bash resolvers
        root, checks = _shape_fixture(tmp_path, "shape: single\n")
        home = tmp_path / "fakehome"
        (home / "agentive-config").mkdir(parents=True)
        env = {
            **os.environ,
            "HOME": str(home),
            "AGENTIVE_KIT_CONFIG_DIR": "~/agentive-config",
        }
        result = run_doctor_rooted(root, checks, "--against-preset", env=env)
        expected = str(home / "agentive-config" / "preset")
        assert any(
            "no preset found at " + expected in ln for ln in preset_lines(result)
        ), result.stdout


def run_worktree_check(root: Path, extra_env: dict[str, str] | None = None):
    check = DOCTOR_D / "55-worktree-provisioning.sh"
    env = {**os.environ, "DOCTOR_ROOT": str(root), **(extra_env or {})}
    return subprocess.run(
        [BASH, str(check)],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _worktree_pair(tmp_path: Path) -> tuple[Path, Path]:
    """A real primary clone plus a linked worktree (the KIT-0071 topology)."""
    primary = tmp_path / "primary"
    primary.mkdir()
    subprocess.run(["git", "init", "--quiet", str(primary)], check=True, timeout=30)
    for key, value in (("user.email", "t@example.com"), ("user.name", "t")):
        subprocess.run(
            ["git", "-C", str(primary), "config", key, value],
            check=True,
            timeout=30,
        )
    subprocess.run(
        ["git", "-C", str(primary), "commit", "--allow-empty", "-m", "init"],
        check=True,
        capture_output=True,
        timeout=30,
    )
    worktree = tmp_path / "wt"
    subprocess.run(
        ["git", "-C", str(primary), "worktree", "add", str(worktree)],
        check=True,
        capture_output=True,
        timeout=30,
    )
    return primary, worktree


class TestWorktreeProvisioningCheck:
    """KIT-0071: the .venv symlink destruction vector (KIT-0065) and the
    Serena name-misdirection (KIT-0069), plus the shared-by-design
    enumeration."""

    def test_symlinked_venv_warns(self, tmp_path):
        target = tmp_path / "elsewhere-venv"
        target.mkdir()
        (tmp_path / ".venv").symlink_to(target)
        result = run_worktree_check(tmp_path)
        assert "DOCTOR:worktree-venv:WARN:" in result.stdout
        assert "KIT-0065" in result.stdout
        assert "symlink" in result.stdout

    def test_real_venv_is_silent(self, tmp_path):
        (tmp_path / ".venv").mkdir()
        result = run_worktree_check(tmp_path)
        assert "DOCTOR:worktree-venv:PASS:" in result.stdout
        assert "worktree-venv:WARN" not in result.stdout

    def test_absent_venv_is_silent(self, tmp_path):
        result = run_worktree_check(tmp_path)
        assert "DOCTOR:worktree-venv:PASS:" in result.stdout
        assert "worktree-venv:WARN" not in result.stdout

    def test_dangling_venv_symlink_still_warns(self, tmp_path):
        # is_symlink-style detection: a dangling link is still the hazard
        (tmp_path / ".venv").symlink_to(tmp_path / "gone")
        result = run_worktree_check(tmp_path)
        assert "DOCTOR:worktree-venv:WARN:" in result.stdout

    def test_non_git_root_audit_skips(self, tmp_path):
        result = run_worktree_check(tmp_path)
        assert "DOCTOR:worktree-audit:SKIP:" in result.stdout
        assert "not a git checkout" in result.stdout

    def test_primary_clone_audit_skips(self, tmp_path):
        primary, _ = _worktree_pair(tmp_path)
        result = run_worktree_check(primary)
        assert "DOCTOR:worktree-audit:SKIP:" in result.stdout
        assert "primary clone" in result.stdout

    def test_narrow_refspec_warns_with_incident_and_remedy(self, tmp_path):
        # KIT-0091 F5 (KIT-0090 incident closure #2): a fetch refspec
        # narrowed to main never updates other remote-tracking refs, so
        # push --force-with-lease fails with "stale info".
        primary, _ = _worktree_pair(tmp_path)
        subprocess.run(
            ["git", "-C", str(primary), "remote", "add", "origin", str(tmp_path)],
            check=True,
            timeout=30,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(primary),
                "config",
                "remote.origin.fetch",
                "+refs/heads/main:refs/remotes/origin/main",
            ],
            check=True,
            timeout=30,
        )
        result = run_worktree_check(primary)
        assert "DOCTOR:worktree-refspec:WARN:" in result.stdout
        assert "KIT-0090" in result.stdout
        assert "STACKED-PR-WORKFLOW.md" in result.stdout
        assert "+refs/heads/*:refs/remotes/origin/*" in result.stdout

    def test_multiple_narrow_refspecs_warn_on_one_line(self, tmp_path):
        # CodeRabbit (PR #113): the check joins multi-value fetch
        # configs with tr — the WARN must stay ONE DOCTOR: line (the
        # driver parses per-line) and carry both specs.
        primary, _ = _worktree_pair(tmp_path)
        subprocess.run(
            ["git", "-C", str(primary), "remote", "add", "origin", str(tmp_path)],
            check=True,
            timeout=30,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(primary),
                "config",
                "remote.origin.fetch",
                "+refs/heads/main:refs/remotes/origin/main",
            ],
            check=True,
            timeout=30,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(primary),
                "config",
                "--add",
                "remote.origin.fetch",
                "+refs/heads/develop:refs/remotes/origin/develop",
            ],
            check=True,
            timeout=30,
        )
        result = run_worktree_check(primary)
        warn_lines = [
            ln
            for ln in result.stdout.splitlines()
            if ln.startswith("DOCTOR:worktree-refspec:WARN:")
        ]
        assert len(warn_lines) == 1, result.stdout
        assert "refs/heads/main" in warn_lines[0]
        assert "refs/heads/develop" in warn_lines[0]

    def test_wildcard_refspec_passes(self, tmp_path):
        primary, worktree = _worktree_pair(tmp_path)
        subprocess.run(
            ["git", "-C", str(primary), "remote", "add", "origin", str(tmp_path)],
            check=True,
            timeout=30,
        )
        # git remote add installs the wildcard refspec by default; the
        # check must see it from the WORKTREE too (config is shared)
        result = run_worktree_check(worktree)
        assert "DOCTOR:worktree-refspec:PASS:" in result.stdout
        assert "worktree-refspec:WARN" not in result.stdout

    def test_no_origin_remote_emits_no_refspec_line(self, tmp_path):
        primary, _ = _worktree_pair(tmp_path)
        result = run_worktree_check(primary)
        assert "worktree-refspec" not in result.stdout

    def test_worktree_without_serena_usage_skips_serena(self, tmp_path):
        _, worktree = _worktree_pair(tmp_path)
        result = run_worktree_check(worktree)
        assert "DOCTOR:worktree-serena:SKIP:" in result.stdout
        assert "does not use Serena" in result.stdout

    def test_worktree_missing_serena_config_warns(self, tmp_path):
        primary, worktree = _worktree_pair(tmp_path)
        (primary / ".serena").mkdir()
        (primary / ".serena" / "project.yml").write_text(
            'project_name: "primary-proj"\n', encoding="utf-8"
        )
        result = run_worktree_check(worktree)
        assert "DOCTOR:worktree-serena:WARN:" in result.stdout
        assert "ABSOLUTE PATH" in result.stdout
        assert "KIT-0069" in result.stdout

    def test_worktree_serena_name_collision_warns(self, tmp_path):
        primary, worktree = _worktree_pair(tmp_path)
        for root in (primary, worktree):
            (root / ".serena").mkdir()
            (root / ".serena" / "project.yml").write_text(
                'project_name: "primary-proj"\n', encoding="utf-8"
            )
        result = run_worktree_check(worktree)
        assert "DOCTOR:worktree-serena:WARN:" in result.stdout
        assert "collides" in result.stdout

    def test_worktree_serena_distinct_name_passes(self, tmp_path):
        primary, worktree = _worktree_pair(tmp_path)
        (primary / ".serena").mkdir()
        (primary / ".serena" / "project.yml").write_text(
            'project_name: "primary-proj"\n', encoding="utf-8"
        )
        (worktree / ".serena").mkdir()
        (worktree / ".serena" / "project.yml").write_text(
            'project_name: "primary-proj-KIT-9999"\n', encoding="utf-8"
        )
        result = run_worktree_check(worktree)
        assert "DOCTOR:worktree-serena:PASS:" in result.stdout
        assert "worktree-serena:WARN" not in result.stdout

    def test_worktree_emits_shared_by_design_enumeration(self, tmp_path):
        _, worktree = _worktree_pair(tmp_path)
        result = run_worktree_check(worktree)
        line = next(
            ln
            for ln in result.stdout.splitlines()
            if ln.startswith("DOCTOR:worktree-shared:PASS:")
        )
        assert ".env" in line
        assert ".adversarial/evaluators" in line
        # settled policy: the audit never asks for permission changes
        assert "allowlist" not in result.stdout

    def test_hostile_git_env_cannot_redirect_audit(self, tmp_path):
        """A leaked GIT_DIR pointing at the primary must not make the
        worktree look like a primary clone (the KIT-0043 leak class)."""
        primary, worktree = _worktree_pair(tmp_path)
        result = run_worktree_check(
            worktree, extra_env={"GIT_DIR": str(primary / ".git")}
        )
        assert "DOCTOR:worktree-audit:SKIP" not in result.stdout
        assert "DOCTOR:worktree-shared:PASS:" in result.stdout

    def test_alternate_venv_layout_symlink_warns(self, tmp_path):
        # code-reviewer (this PR): the venv/ layout 40-version-skew
        # probes carries the same hazard class
        target = tmp_path / "elsewhere-venv"
        target.mkdir()
        (tmp_path / "venv").symlink_to(target)
        result = run_worktree_check(tmp_path)
        assert "DOCTOR:worktree-venv:WARN:" in result.stdout
        assert "venv is a symlink" in result.stdout

    def test_serena_short_name_key_collision_detected(self, tmp_path):
        # code-reviewer (this PR): the project reader accepts `name:` as
        # well as `project_name:` — the collision check must match it
        primary, worktree = _worktree_pair(tmp_path)
        for root in (primary, worktree):
            (root / ".serena").mkdir()
            (root / ".serena" / "project.yml").write_text(
                'name: "same-proj"\n', encoding="utf-8"
            )
        result = run_worktree_check(worktree)
        assert "DOCTOR:worktree-serena:WARN:" in result.stdout
        assert "collides" in result.stdout

    def test_serena_apostrophe_name_not_mangled(self, tmp_path):
        # strip surrounding quotes only: operator's-toolkit must not
        # false-collide with operators-toolkit
        primary, worktree = _worktree_pair(tmp_path)
        (primary / ".serena").mkdir()
        (primary / ".serena" / "project.yml").write_text(
            'project_name: "operator\'s-toolkit"\n', encoding="utf-8"
        )
        (worktree / ".serena").mkdir()
        (worktree / ".serena" / "project.yml").write_text(
            'project_name: "operators-toolkit"\n', encoding="utf-8"
        )
        result = run_worktree_check(worktree)
        assert "DOCTOR:worktree-serena:PASS:" in result.stdout
        assert "collides" not in result.stdout

    def test_serena_unnamed_config_warns(self, tmp_path):
        # fast-v2 (this PR): an unnamed worktree config defeats the
        # per-worktree identity — WARN, not a silent PASS
        primary, worktree = _worktree_pair(tmp_path)
        (primary / ".serena").mkdir()
        (primary / ".serena" / "project.yml").write_text(
            'project_name: "primary-proj"\n', encoding="utf-8"
        )
        (worktree / ".serena").mkdir()
        (worktree / ".serena" / "project.yml").write_text(
            "languages:\n  - python\n", encoding="utf-8"
        )
        result = run_worktree_check(worktree)
        assert "DOCTOR:worktree-serena:WARN:" in result.stdout
        assert "no name/project_name" in result.stdout

    def test_hostile_git_common_dir_cannot_redirect_audit(self, tmp_path):
        # code-reviewer (this PR): GIT_COMMON_DIR alone must be scrubbed
        # exactly like GIT_DIR
        primary, worktree = _worktree_pair(tmp_path)
        result = run_worktree_check(
            worktree, extra_env={"GIT_COMMON_DIR": str(primary / ".git")}
        )
        assert "DOCTOR:worktree-audit:SKIP" not in result.stdout
        assert "DOCTOR:worktree-shared:PASS:" in result.stdout

    def test_symlinked_venv_in_worktree_remedy_says_no_hooks(self, tmp_path):
        # BugBot (this PR): inside a linked worktree the remedy must say
        # --no-hooks — hooks are shared with the primary
        _, worktree = _worktree_pair(tmp_path)
        target = tmp_path / "elsewhere-venv"
        target.mkdir()
        (worktree / ".venv").symlink_to(target)
        # A copied-scripts repo (KIT-0093: the check keys its remedy on
        # this file; packaged repos get a plain venv command instead)
        core = worktree / "scripts" / "core"
        core.mkdir(parents=True)
        stub = core / "project"
        stub.write_text("#!/bin/sh\n", encoding="utf-8")
        stub.chmod(0o755)
        result = run_worktree_check(worktree)
        line = next(
            ln
            for ln in result.stdout.splitlines()
            if ln.startswith("DOCTOR:worktree-venv:WARN:")
        )
        # the remedy must be a copy-able command, root-scoped so a paste
        # from any cwd hits the diagnosed checkout (paths %q-escaped —
        # bare for a plain path); the rationale is a trailing SHELL
        # COMMENT so the whole tail parses (bot rounds 2-4)
        expected = (
            f"rm {worktree}/.venv && "
            f"(cd {worktree} && ./scripts/core/project setup --no-hooks)"
        )
        assert expected in line
        assert "--no-hooks (" not in line
        # the paste-able tail (command + note) must be valid shell:
        # bash -n parses without executing — this catches any prose
        # that is not a comment
        paste = line[line.index("rm ") :]
        parse = subprocess.run(
            [BASH, "-n", "-c", paste], capture_output=True, text=True, timeout=30
        )
        assert parse.returncode == 0, f"remedy does not parse: {paste!r}"
        assert "# hooks stay shared" in paste

    def test_remedy_survives_hostile_path_characters(self, tmp_path):
        # CodeRabbit round 4: quotes / $() in the checkout path must
        # neither break the pasted snippet nor smuggle substitution —
        # %q escaping keeps the tail parseable
        base = tmp_path / 'evil "dir$(x)'
        base.mkdir()
        _, worktree = _worktree_pair(base)
        target = tmp_path / "elsewhere-venv"
        target.mkdir()
        (worktree / ".venv").symlink_to(target)
        result = run_worktree_check(worktree)
        line = next(
            ln
            for ln in result.stdout.splitlines()
            if ln.startswith("DOCTOR:worktree-venv:WARN:")
        )
        paste = line[line.index("rm ") :]
        parse = subprocess.run(
            [BASH, "-n", "-c", paste], capture_output=True, text=True, timeout=30
        )
        assert parse.returncode == 0, f"remedy does not parse: {paste!r}"

    def test_symlinked_venv_outside_worktree_remedy_plain_setup(self, tmp_path):
        # outside a worktree, plain setup (with hooks) is the right advice
        target = tmp_path / "elsewhere-venv"
        target.mkdir()
        (tmp_path / ".venv").symlink_to(target)
        result = run_worktree_check(tmp_path)
        line = next(
            ln
            for ln in result.stdout.splitlines()
            if ln.startswith("DOCTOR:worktree-venv:WARN:")
        )
        assert "--no-hooks" not in line


def run_evaluator_cli_check(root: Path, path_dir: Path | None = None):
    """Run 31-evaluator-cli.sh; restrict PATH to control `adversarial` visibility.

    PATH control is the whole point (KIT-0083): both `uv` and
    `adversarial` are installed on the maintainer's machine, so an
    unrestricted `command -v` passes locally and proves nothing about a
    fresh project — the exact blind spot that let issue #103 ship.
    """
    env = {**os.environ, "DOCTOR_ROOT": str(root)}
    if path_dir is not None:
        env["PATH"] = str(path_dir)
    check = DOCTOR_D / "31-evaluator-cli.sh"
    return subprocess.run(
        [BASH, str(check)],
        env=env,
        capture_output=True,
        text=True,
        # Comfortably above the check's own 20s probe bound, so a
        # genuinely-blocking stub is cut off by the CHECK (producing its
        # timeout verdict) and not by pytest (producing an error).
        timeout=60,
    )


class TestEvaluatorCliCheck:
    """KIT-0083 / issue #103: the library's PASS must not mask a missing CLI."""

    def test_no_adversarial_dir_skips(self, tmp_path):
        """No .adversarial/ — nothing to say (mirrors 30-evaluators.sh)."""
        result = run_evaluator_cli_check(tmp_path, _restricted_bin(tmp_path))
        assert "DOCTOR:evaluator-cli:SKIP:" in result.stdout
        assert "not initialized" in result.stdout

    def test_config_present_but_binary_missing_fails(self, tmp_path):
        """THE #103 TRAP: config/library present, CLI absent → FAIL."""
        (tmp_path / ".adversarial" / "evaluators").mkdir(parents=True)
        result = run_evaluator_cli_check(tmp_path, _restricted_bin(tmp_path))
        assert "DOCTOR:evaluator-cli:FAIL:" in result.stdout
        assert "not on PATH" in result.stdout

    def test_fail_message_names_the_fix_and_path(self, tmp_path):
        """An actionable message: the fix command AND the PATH hint —
        uv installs into ~/.local/bin, so 'installed but invisible' is a
        real state a bare 'not found' would leave unexplained."""
        (tmp_path / ".adversarial").mkdir()
        result = run_evaluator_cli_check(tmp_path, _restricted_bin(tmp_path))
        assert "install-evaluators" in result.stdout
        assert "uv tool install adversarial-workflow" in result.stdout
        assert "~/.local/bin" in result.stdout

    def test_stub_binary_on_path_passes(self, tmp_path):
        """A working CLI on PATH → PASS."""
        (tmp_path / ".adversarial").mkdir()
        bin_dir = _restricted_bin(tmp_path)
        _stub_executable(bin_dir / "adversarial", "exit 0\n")
        result = run_evaluator_cli_check(tmp_path, bin_dir)
        assert "DOCTOR:evaluator-cli:PASS:" in result.stdout

    def test_version_probe_uses_exit_code_not_output(self, tmp_path):
        """A healthy CLI prints 'Unknown fields in evaluator.yml' warnings
        to stderr (verified 2026-08-05). Exit 0 with noisy stderr must
        still PASS — an output-parsing check would false-FAIL here."""
        (tmp_path / ".adversarial").mkdir()
        bin_dir = _restricted_bin(tmp_path)
        _stub_executable(
            bin_dir / "adversarial",
            'echo "Unknown fields in evaluator.yml: status" >&2\nexit 0\n',
        )
        result = run_evaluator_cli_check(tmp_path, bin_dir)
        assert "DOCTOR:evaluator-cli:PASS:" in result.stdout

    def test_broken_binary_fails(self, tmp_path):
        """On PATH but non-functional (exit non-zero) → FAIL, not PASS."""
        (tmp_path / ".adversarial").mkdir()
        bin_dir = _restricted_bin(tmp_path)
        _stub_executable(bin_dir / "adversarial", "exit 1\n")
        result = run_evaluator_cli_check(tmp_path, bin_dir)
        assert "DOCTOR:evaluator-cli:FAIL:" in result.stdout
        assert "--version" in result.stdout

    @pytest.mark.slow
    def test_hanging_version_probe_is_bounded(self, tmp_path):
        """A corrupt install whose --version BLOCKS must FAIL on a bound,
        not hang the whole doctor run (o3 review).

        The stub calls sleep by ABSOLUTE path. A bare `sleep 120` exits
        127 instantly under the restricted PATH, so the earlier version
        of this test passed on the broken-binary branch and never
        exercised the bound at all (CodeRabbit round 1). Asserting the
        timeout message specifically — not merely FAIL — is what keeps
        that confusion from returning.
        """
        import time

        sleep_bin = next(
            (c for c in ("/bin/sleep", "/usr/bin/sleep") if Path(c).exists()), None
        )
        if sleep_bin is None:
            pytest.skip("no absolute sleep binary to build a blocking stub with")

        (tmp_path / ".adversarial").mkdir()
        bin_dir = _restricted_bin(tmp_path)
        _stub_executable(bin_dir / "adversarial", f"exec {sleep_bin} 120\n")
        started = time.monotonic()
        result = run_evaluator_cli_check(tmp_path, bin_dir)
        elapsed = time.monotonic() - started
        assert "DOCTOR:evaluator-cli:FAIL:" in result.stdout
        assert "did not finish" in result.stdout, (
            "FAILed for the wrong reason — the stub did not actually block: "
            f"{result.stdout!r}"
        )
        # Bound the timing from BOTH sides. An upper bound alone passes a
        # probe whose timeout was shortened to near-zero, which is the
        # same class of unfalsifiable assertion as the one that let this
        # test hide behind the broken-binary branch (CodeRabbit round 2).
        assert elapsed >= 18, (
            f"probe terminated after {elapsed:.0f}s — it did not wait out "
            "its configured bound"
        )
        assert elapsed < 60, f"probe was not bounded (took {elapsed:.0f}s)"

    def test_check_exits_zero_on_every_path(self, tmp_path):
        """Checks report via DOCTOR: lines; the driver owns exit codes."""
        (tmp_path / ".adversarial").mkdir()
        assert (
            run_evaluator_cli_check(tmp_path, _restricted_bin(tmp_path)).returncode == 0
        )


def test_probe_bounds_match_the_installer():
    """The doctor bound and the installer bound must stay equal.

    The liveness probe's purpose is that `install-evaluators` and
    `project doctor` never disagree about one install. A CLI answering
    between two different bounds would be "working" to one surface and
    FAIL to the other — the exact split this check exists to close
    (CodeRabbit round 1). Coupling asserted here so it cannot drift
    silently.
    """
    check_text = (DOCTOR_D / "31-evaluator-cli.sh").read_text(encoding="utf-8")
    doctor_bound = re.search(r"^PROBE_TIMEOUT=(\d+)", check_text, re.MULTILINE)
    assert doctor_bound, "doctor check no longer declares PROBE_TIMEOUT"

    project_text = PROJECT_SCRIPT.read_text(encoding="utf-8")
    installer_bound = re.search(
        r"^CLI_PROBE_TIMEOUT\s*=\s*(\d+)", project_text, re.MULTILINE
    )
    assert installer_bound, "project no longer declares CLI_PROBE_TIMEOUT"

    assert doctor_bound.group(1) == installer_bound.group(1), (
        f"probe bounds drifted: doctor={doctor_bound.group(1)}s, "
        f"installer={installer_bound.group(1)}s"
    )


# ─────────────────────────────────────────────────────────────────────
# KIT-0080: portable git path resolution + the git-version floor check
# ─────────────────────────────────────────────────────────────────────
# Root cause: `git rev-parse --path-format=absolute` needs git >= 2.31.
# Apple's system git (2.30.1, stock on macOS) does NOT consume the flag —
# it echoes it back as the first output line and still exits 0, so every
# resolver built on it silently produced garbage. CI runners ship modern
# git, so nothing here would regress loudly without the stub below: it
# is the ONLY coverage of the 2.30.x behavior on a modern-git machine.

OLD_GIT_STUB = """#!/bin/bash
# Emulates git 2.30.x argument handling for `rev-parse`: the
# --path-format=* flag is NOT consumed, it is echoed as an output line
# and the remaining args are answered normally. Everything else
# delegates to the real git, so repos behave for real.
REAL={real}
args=()
echoes=()
for a in "$@"; do
    case "$a" in
        --path-format=*) echoes+=("$a") ;;
        *) args+=("$a") ;;
    esac
done
if [ "${{#echoes[@]}}" -gt 0 ]; then
    for e in "${{echoes[@]}}"; do printf '%s\\n' "$e"; done
fi
exec "$REAL" "${{args[@]}}"
"""


def _old_git_bin(base: Path) -> Path:
    """A PATH dir whose `git` mimics 2.30.x --path-format handling."""
    real = shutil.which("git")
    assert real, "git required for this fixture"
    bin_dir = base / "old-git-bin"
    bin_dir.mkdir()
    stub = bin_dir / "git"
    # shlex.quote: an unquoted REAL= assignment breaks the stub outright
    # if git's path contains spaces (bash would run the second word as a
    # command). Latent on the usual /usr/bin/git, real on a path like
    # "/Applications/Xcode 16.app/..." (CodeRabbit, this PR).
    stub.write_text(OLD_GIT_STUB.format(real=shlex.quote(real)), encoding="utf-8")
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return bin_dir


def _with_old_git(path_dir: Path) -> dict[str, str]:
    """Env putting the 2.30.x stub FIRST on PATH (real tools still found)."""
    return {"PATH": f"{path_dir}{os.pathsep}{os.environ.get('PATH', '')}"}


class TestOldGitStubIsFaithful:
    """The stub is the oracle for every test below, so pin its behavior
    first — a stub that quietly stopped emulating the bug would make the
    whole class vacuously green."""

    def test_stub_echoes_the_flag_instead_of_consuming_it(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "--quiet", str(repo)], check=True, timeout=30)
        bin_dir = _old_git_bin(tmp_path)
        result = subprocess.run(
            [
                str(bin_dir / "git"),
                "-C",
                str(repo),
                "rev-parse",
                "--path-format=absolute",
                "--git-common-dir",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        lines = result.stdout.splitlines()
        assert lines[0] == "--path-format=absolute", result.stdout
        assert result.returncode == 0, "2.30.x exits 0 — that is what made it silent"

    def test_stub_delegates_plain_flags_to_real_git(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "--quiet", str(repo)], check=True, timeout=30)
        bin_dir = _old_git_bin(tmp_path)
        result = subprocess.run(
            [str(bin_dir / "git"), "-C", str(repo), "rev-parse", "--git-common-dir"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "--path-format" not in result.stdout
        assert result.stdout.strip(), "plain flag must still answer"


class TestPortableGitResolutionUnderOldGit:
    """Each check must produce the SAME verdict on both gits, and must
    never leak git/dirname noise to stderr (S1/S2/S3)."""

    def test_core_bare_check_is_clean_and_identical(self, tmp_path):
        primary, _ = _worktree_pair(tmp_path)
        bin_dir = _old_git_bin(tmp_path)
        modern = run_core_bare_check(primary)
        old = subprocess.run(
            [BASH, str(DOCTOR_D / "70-core-bare.sh")],
            env={**os.environ, "DOCTOR_ROOT": str(primary), **_with_old_git(bin_dir)},
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert "DOCTOR:core-bare:PASS:" in old.stdout, old.stdout
        assert old.stdout == modern.stdout, "verdict diverged between git versions"
        assert "dirname:" not in old.stderr
        assert old.stderr == "", f"stray stderr under old git: {old.stderr!r}"

    def test_config_home_check_is_clean_and_identical(self, tmp_path):
        parent = tmp_path / "parent"
        kit = parent / "kit"
        kit.mkdir(parents=True)
        subprocess.run(["git", "init", "--quiet", str(kit)], check=True, timeout=30)
        (parent / "agentive-config").mkdir()
        base_env = {
            **os.environ,
            "DOCTOR_ROOT": str(kit),
            "XDG_CONFIG_HOME": str(tmp_path / "no-such-xdg"),
        }
        base_env.pop("AGENTIVE_KIT_CONFIG_DIR", None)
        check = DOCTOR_D / "90-config-home.sh"
        modern = subprocess.run(
            [BASH, str(check)], env=base_env, capture_output=True, text=True, timeout=30
        )
        bin_dir = _old_git_bin(tmp_path)
        old = subprocess.run(
            [BASH, str(check)],
            env={**base_env, **_with_old_git(bin_dir)},
            capture_output=True,
            text=True,
            timeout=30,
        )
        # The S1 symptom verbatim: `dirname: illegal option -- -`.
        assert "dirname:" not in old.stderr, f"S1 regressed: {old.stderr!r}"
        assert old.stderr == "", f"stray stderr under old git: {old.stderr!r}"
        # The S3 symptom: the home resolved to relative garbage, so the
        # operator preset was silently invisible.
        assert "./agentive-config" not in old.stdout, "S3 regressed (relative garbage)"
        assert str(parent / "agentive-config") in old.stdout, old.stdout
        assert old.stdout == modern.stdout, "verdict diverged between git versions"

    def test_worktree_check_is_clean_and_identical(self, tmp_path):
        _, worktree = _worktree_pair(tmp_path)
        bin_dir = _old_git_bin(tmp_path)
        modern = run_worktree_check(worktree)
        old = run_worktree_check(worktree, extra_env=_with_old_git(bin_dir))
        assert "dirname:" not in old.stderr, f"S1 regressed: {old.stderr!r}"
        assert old.stderr == "", f"stray stderr under old git: {old.stderr!r}"
        # Under the bug both rev-parse answers were garbage, compared
        # unequal, and the check wrongly believed it was in a worktree
        # with a nonexistent primary.
        assert "DOCTOR:worktree-audit:SKIP:" not in old.stdout, old.stdout
        assert old.stdout == modern.stdout, "verdict diverged between git versions"

    def test_no_script_still_uses_the_unportable_flag(self):
        """The whole class returns the moment one resolver reverts.

        Scoped to ALL of scripts/, not just doctor.d: the bug's worst
        two faces lived in scripts/local/ (the setup door's silent
        preset miss and new-worktree.sh's hard death), so a guard that
        only watched doctor.d would let the expensive half regress
        silently (code-reviewer, this PR).
        """
        scripts_root = REPO_ROOT / "scripts"
        offenders = []
        for path in sorted(scripts_root.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for raw in text.splitlines():
                # Comments explaining the bug are expected and wanted;
                # only an executable use is a regression.
                line = raw.strip()
                if line.startswith("#") or "--path-format" not in line:
                    continue
                rel = path.relative_to(REPO_ROOT)
                offenders.append(f"{rel}:{line}")
        assert offenders == [], (
            f"--path-format=absolute needs git >= 2.31 and is silently wrong on "
            f"Apple git 2.30.1 (KIT-0080): {offenders}"
        )

    def test_non_repo_still_skips_under_old_git(self, tmp_path):
        """The absolutize step must not turn 'not a repo' into a wrong
        answer: an empty rev-parse result joined onto DOCTOR_ROOT would
        make every check confidently name the root itself."""
        bin_dir = _old_git_bin(tmp_path)
        plain = tmp_path / "not-a-repo"
        plain.mkdir()
        old = subprocess.run(
            [BASH, str(DOCTOR_D / "70-core-bare.sh")],
            env={**os.environ, "DOCTOR_ROOT": str(plain), **_with_old_git(bin_dir)},
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert "DOCTOR:core-bare:SKIP:" in old.stdout, old.stdout


class TestGitVersionFloorCheck:
    """F4: the machine-readable half of the README's git floor."""

    CHECK = "15-git-version.sh"

    def _run(self, path_dir: Path | None = None):
        env = {**os.environ}
        if path_dir is not None:
            env["PATH"] = str(path_dir)
        return subprocess.run(
            [BASH, str(DOCTOR_D / self.CHECK)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def _fake_git(self, base: Path, version_line: str) -> Path:
        bin_dir = base / "fake-git-bin"
        bin_dir.mkdir()
        _stub_executable(
            bin_dir / "git", f'#!/bin/bash\nprintf "%s\\n" "{version_line}"\n'
        )
        for tool in ("bash", "printf"):
            real = shutil.which(tool)
            if real:
                (bin_dir / tool).symlink_to(real)
        return bin_dir

    def test_real_git_passes(self):
        result = self._run()
        assert "DOCTOR:git-version:PASS:" in result.stdout, result.stdout

    def test_below_floor_warns_and_names_the_remedy(self, tmp_path):
        bin_dir = self._fake_git(tmp_path, "git version 2.29.2")
        result = self._run(bin_dir)
        assert "DOCTOR:git-version:WARN:" in result.stdout, result.stdout
        assert "2.29.2" in result.stdout
        # The remedy must name the thing that works AND rule out the
        # intuitive non-remedy (Apple's CLT ship 2.30.x by design).
        assert "brew install git" in result.stdout
        assert "xcode-select" in result.stdout

    def test_apple_system_git_passes_now_that_resolvers_are_portable(self, tmp_path):
        """KIT-0080 dropped the floor to 2.30 by making the resolvers
        portable — 2.30.1 must NOT warn, or the check contradicts the
        fix and cries wolf on every stock Mac."""
        bin_dir = self._fake_git(tmp_path, "git version 2.30.1 (Apple Git-130)")
        result = self._run(bin_dir)
        assert "DOCTOR:git-version:PASS:" in result.stdout, result.stdout

    def test_floor_boundary_exactly_at_the_floor_passes(self, tmp_path):
        bin_dir = self._fake_git(tmp_path, "git version 2.30.0")
        result = self._run(bin_dir)
        assert "DOCTOR:git-version:PASS:" in result.stdout, result.stdout

    def test_major_version_above_floor_passes(self, tmp_path):
        bin_dir = self._fake_git(tmp_path, "git version 3.0.0")
        result = self._run(bin_dir)
        assert "DOCTOR:git-version:PASS:" in result.stdout, result.stdout

    @pytest.mark.parametrize(
        "version_line",
        [
            "totally not a version string",
            "git version banana.7.1",
            "git version 2",
            "",
        ],
    )
    def test_unparseable_version_warns_rather_than_guessing(
        self, tmp_path, version_line
    ):
        """A version we cannot read must never be silently treated as
        modern (or ancient) — that is the masking class this task is
        about."""
        bin_dir = self._fake_git(tmp_path, version_line)
        result = self._run(bin_dir)
        assert "DOCTOR:git-version:WARN:" in result.stdout, result.stdout
        assert "cannot parse" in result.stdout

    def test_git_absent_fails(self, tmp_path):
        bin_dir = tmp_path / "no-git-bin"
        bin_dir.mkdir()
        for tool in ("bash", "printf"):
            real = shutil.which(tool)
            if real:
                (bin_dir / tool).symlink_to(real)
        result = self._run(bin_dir)
        assert "DOCTOR:git-version:FAIL:" in result.stdout, result.stdout

    def test_floor_agrees_with_the_readme_requirements_row(self):
        """The human-readable and machine-readable floors must never
        drift apart (F4's explicit requirement)."""
        check_text = (DOCTOR_D / self.CHECK).read_text(encoding="utf-8")
        major = re.search(r"^FLOOR_MAJOR=(\d+)", check_text, re.MULTILINE)
        minor = re.search(r"^FLOOR_MINOR=(\d+)", check_text, re.MULTILINE)
        assert major and minor, "check no longer declares its floor"
        floor = f"{major.group(1)}.{minor.group(1)}"
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        row = [
            ln for ln in readme.splitlines() if ln.startswith("|") and "**git**" in ln
        ]
        assert row, "README has no git Requirements row"
        assert (
            floor in row[0]
        ), f"README git row does not state the doctor floor {floor}: {row[0]}"


# ── 35-handoffs-paths.py: agent-handoffs.json stale-path drift (KIT-0086 F2,
# landed via KIT-0090 PR 2) ─────────────────────────────────────────────────


def run_handoffs_check(root: Path) -> subprocess.CompletedProcess:
    check = DOCTOR_D / "35-handoffs-paths.py"
    return subprocess.run(
        [sys.executable, str(check)],
        env={**os.environ, "DOCTOR_ROOT": str(root)},
        capture_output=True,
        text=True,
        timeout=30,
    )


def _handoffs_fixture(tmp_path: Path, details_link: str, actual_folder: str) -> Path:
    root = tmp_path / "root"
    context = root / ".kit" / "context"
    context.mkdir(parents=True)
    tasks = root / ".kit" / "tasks"
    (tasks / actual_folder).mkdir(parents=True)
    (tasks / actual_folder / "KIT-1234-sample.md").write_text(
        "**Status**: In Progress\n", encoding="utf-8"
    )
    (context / "agent-handoffs.json").write_text(
        json.dumps({"planner": {"details_link": details_link}}) + "\n",
        encoding="utf-8",
    )
    return root


class TestHandoffsPathsCheck:
    def test_fresh_path_passes(self, tmp_path):
        root = _handoffs_fixture(
            tmp_path, ".kit/tasks/3-in-progress/KIT-1234-sample.md", "3-in-progress"
        )
        result = run_handoffs_check(root)
        assert "DOCTOR:35-handoffs-paths.py:PASS:" in result.stdout

    def test_stale_path_warns_and_names_both_folders(self, tmp_path):
        # The KIT-0086 drift shape: a branch-side move left the JSON
        # pointing at 2-todo while the file lives in 3-in-progress.
        root = _handoffs_fixture(
            tmp_path, ".kit/tasks/2-todo/KIT-1234-sample.md", "3-in-progress"
        )
        result = run_handoffs_check(root)
        line = [
            ln
            for ln in result.stdout.splitlines()
            if ln.startswith("DOCTOR:35-handoffs-paths.py:WARN:")
        ]
        assert line, result.stdout
        assert "2-todo/KIT-1234-sample.md" in line[0]
        assert "3-in-progress/KIT-1234-sample.md" in line[0]
        assert "KIT-0086" in line[0]

    def test_gone_task_is_not_drift(self, tmp_path):
        # A recorded path whose file exists in NO folder (archived or
        # deleted task) is the planner's bookkeeping, not stale drift.
        root = _handoffs_fixture(
            tmp_path, ".kit/tasks/2-todo/KIT-9999-gone.md", "3-in-progress"
        )
        result = run_handoffs_check(root)
        assert "DOCTOR:35-handoffs-paths.py:PASS:" in result.stdout

    def test_missing_json_skips(self, tmp_path):
        root = tmp_path / "root"
        (root / ".kit" / "tasks" / "2-todo").mkdir(parents=True)
        result = run_handoffs_check(root)
        assert "DOCTOR:35-handoffs-paths.py:SKIP:" in result.stdout

    def test_corrupt_json_warns_not_crashes(self, tmp_path):
        root = _handoffs_fixture(
            tmp_path, ".kit/tasks/3-in-progress/KIT-1234-sample.md", "3-in-progress"
        )
        (root / ".kit" / "context" / "agent-handoffs.json").write_bytes(b"\xff{broken")
        result = run_handoffs_check(root)
        assert "DOCTOR:35-handoffs-paths.py:WARN:" in result.stdout
        assert "Traceback" not in result.stderr

    def test_driver_runs_the_check(self, tmp_path):
        # The check rides the standard driver contract — one real-driver
        # pass over the real doctor.d proves registration (uses --root
        # to keep the diagnosis off the developer's checkout).
        root = _handoffs_fixture(
            tmp_path, ".kit/tasks/3-in-progress/KIT-1234-sample.md", "3-in-progress"
        )
        result = subprocess.run(
            [sys.executable, str(PROJECT_SCRIPT), "doctor", f"--root={root}"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        # PASS specifically — a bare prefix match would also accept the
        # not-executable FAIL shape (CodeRabbit, PR #109).
        assert "DOCTOR:35-handoffs-paths.py:PASS:" in result.stdout


# ─────────────────────────────────────────
# KIT-0118 (issue #146): a DECLINED evaluator install is a declaration
# ─────────────────────────────────────────
def run_evaluator_check(
    name: str, root: Path, declared: str | None, path_dir: Path | None = None
):
    """Run an evaluator check with the record's `evaluators:` answer in
    the environment, exactly as the doctor driver passes it."""
    env = {**os.environ, "DOCTOR_ROOT": str(root)}
    env.pop("DOCTOR_EVALUATORS", None)
    if declared is not None:
        env["DOCTOR_EVALUATORS"] = declared
    if path_dir is not None:
        env["PATH"] = str(path_dir)
    return subprocess.run(
        [BASH, str(DOCTOR_D / name)],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


class TestEvaluatorsDeclinedAtInstall:
    """Issue #146.1: `--without-evaluators` is an operator DECISION.
    Doctor must SKIP the evaluator checks on it rather than FAIL the
    project for honoring the answer the door itself offered.
    """

    def _provisioned_but_empty(self, tmp_path: Path) -> Path:
        # the fresh-install shape: .adversarial/ copied unconditionally
        # by the consumer engine, evaluators/ never populated
        (tmp_path / ".adversarial").mkdir()
        return tmp_path

    def test_library_check_skips_when_declined(self, tmp_path):
        root = self._provisioned_but_empty(tmp_path)
        result = run_evaluator_check("30-evaluators.sh", root, "no")
        assert "DOCTOR:evaluators:SKIP:" in result.stdout
        assert "declined at install" in result.stdout
        assert "DOCTOR:evaluators:FAIL" not in result.stdout

    def test_cli_check_skips_when_declined(self, tmp_path):
        root = self._provisioned_but_empty(tmp_path)
        result = run_evaluator_check(
            "31-evaluator-cli.sh", root, "no", _restricted_bin(tmp_path)
        )
        assert "DOCTOR:evaluator-cli:SKIP:" in result.stdout
        assert "declined at install" in result.stdout
        assert "DOCTOR:evaluator-cli:FAIL" not in result.stdout

    def test_skip_message_says_how_to_re_enable(self, tmp_path):
        # a SKIP that hides a real gap forever would be the masking
        # class — the way back must be in the line itself
        root = self._provisioned_but_empty(tmp_path)
        result = run_evaluator_check("30-evaluators.sh", root, "no")
        assert "install-evaluators" in result.stdout
        assert "update the record" in result.stdout

    def test_accepted_answer_keeps_todays_behavior(self, tmp_path):
        root = self._provisioned_but_empty(tmp_path)
        result = run_evaluator_check("30-evaluators.sh", root, "yes")
        assert "DOCTOR:evaluators:FAIL:" in result.stdout

    def test_legacy_record_keeps_todays_behavior(self, tmp_path):
        # no evaluators: line at all -> the driver sets nothing ->
        # pre-KIT-0118 behavior, fail-open to FAIL
        root = self._provisioned_but_empty(tmp_path)
        result = run_evaluator_check("30-evaluators.sh", root, None)
        assert "DOCTOR:evaluators:FAIL:" in result.stdout

    def test_accepted_answer_still_passes_a_real_install(self, tmp_path):
        (tmp_path / ".adversarial" / "evaluators").mkdir(parents=True)
        (tmp_path / ".adversarial" / "evaluators" / "one.yml").write_text(
            "x\n", encoding="utf-8"
        )
        result = run_evaluator_check("30-evaluators.sh", tmp_path, "yes")
        assert "DOCTOR:evaluators:PASS:" in result.stdout


class TestFreshInstallEnvKeys:
    """Issue #146.2: on a fresh install BOTH problems co-occur by
    construction — .env.template ships ANTHROPIC_API_KEY commented AND
    TASK_PREFIX empty. The required-key FAIL used to return before the
    prefix block ran, hiding the warning the door explicitly promises.
    """

    # verbatim shape of the seeded .env (planning --new)
    FRESH = (
        "# ANTHROPIC_API_KEY=sk-ant-your-key-here\n"
        "# OPENAI_API_KEY=sk-your-key-here\n"
        "# GEMINI_API_KEY=your-key-here\n"
        "TASK_PREFIX=\n"
    )

    def test_both_problems_surface(self, tmp_path):
        (tmp_path / ".env").write_text(self.FRESH, encoding="utf-8")
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:FAIL:" in result.stdout
        assert "ANTHROPIC_API_KEY" in result.stdout
        assert "TASK_PREFIX" in result.stdout

    def test_still_one_protocol_line(self, tmp_path):
        (tmp_path / ".env").write_text(self.FRESH, encoding="utf-8")
        result = run_env_check(tmp_path)
        verdicts = [
            ln for ln in result.stdout.splitlines() if ln.startswith("DOCTOR:env-keys:")
        ]
        assert len(verdicts) == 1  # one check, one protocol line

    def test_verdict_stays_fail_not_warn(self, tmp_path):
        # semantics unchanged: a missing required key is still a FAIL
        (tmp_path / ".env").write_text(self.FRESH, encoding="utf-8")
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:WARN:" not in result.stdout

    def test_required_key_fail_alone_says_nothing_about_prefix(self, tmp_path):
        # the fold must be conditional — a good prefix must not be
        # reported as a problem alongside a genuine key failure
        (tmp_path / ".env").write_text(
            "# ANTHROPIC_API_KEY=x\nOPENAI_API_KEY=a\nGEMINI_API_KEY=b\n"
            "TASK_PREFIX=DEMO\n",
            encoding="utf-8",
        )
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:FAIL:" in result.stdout
        assert "TASK_PREFIX" not in result.stdout

    def test_the_real_seeded_template_surfaces_both(self, tmp_path):
        """Grounded on the SHIPPED template, not a hand-written stand-in:
        the co-occurrence is a property of what the door actually seeds,
        so a template edit that changes it must fail this test."""
        template = REPO_ROOT / ".env.template"
        (tmp_path / ".env").write_text(
            template.read_text(encoding="utf-8"), encoding="utf-8"
        )
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:FAIL:" in result.stdout
        assert "ANTHROPIC_API_KEY" in result.stdout
        assert "TASK_PREFIX" in result.stdout

    def test_prefix_only_problem_is_still_a_warn(self, tmp_path):
        (tmp_path / ".env").write_text(
            "ANTHROPIC_API_KEY=x\nOPENAI_API_KEY=a\nGEMINI_API_KEY=b\n"
            "TASK_PREFIX=\n",
            encoding="utf-8",
        )
        result = run_env_check(tmp_path)
        assert "DOCTOR:env-keys:WARN:" in result.stdout
        assert "TASK_PREFIX" in result.stdout

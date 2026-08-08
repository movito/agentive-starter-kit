"""Tests for agentive_kit.doctor packaging seams (KIT-0090 PR 2).

The driver's behavior itself is covered by tests/test_doctor.py, which
drives the real script (now delegating here) through the --dir= seam —
those tests are the extraction spec. This module covers only what is
NEW in the package: check-set resolution.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip(
    "agentive_kit", reason="agentive-kit package source present only in the kit repo"
)

from agentive_kit import doctor  # noqa: E402


class TestDefaultChecksDir:
    def test_repo_local_doctor_d_wins(self, tmp_path):
        local = tmp_path / "scripts" / "core" / "doctor.d"
        local.mkdir(parents=True)
        assert doctor.default_checks_dir(tmp_path) == local

    def test_packaged_checks_are_the_fallback(self, tmp_path):
        resolved = doctor.default_checks_dir(tmp_path)
        assert resolved == Path(doctor.__file__).resolve().parent / "checks"
        assert resolved.is_dir()

    def test_packaged_set_matches_repo_set(self):
        # The packaged copy must not drift from the synced canonical
        # set in scripts/core/doctor.d (both ship this phase).
        repo_root = Path(__file__).resolve().parent.parent.parent
        repo_set = {
            p.name
            for p in (repo_root / "scripts/core/doctor.d").iterdir()
            if not p.name.startswith(".")
        }
        pkg_dir = Path(doctor.__file__).resolve().parent / "checks"
        pkg_set = {
            p.name
            for p in pkg_dir.iterdir()
            if not p.name.startswith(".") and p.name != "__init__.py"
        }
        assert pkg_set == repo_set

    def test_packaged_checks_keep_content_identical(self):
        repo_root = Path(__file__).resolve().parent.parent.parent
        pkg_dir = Path(doctor.__file__).resolve().parent / "checks"
        for check in (repo_root / "scripts/core/doctor.d").iterdir():
            if check.name.startswith("."):
                continue
            assert (pkg_dir / check.name).read_bytes() == check.read_bytes(), check.name


class TestPackagedChecksExecBitFallback:
    def test_non_executable_packaged_check_runs_via_interpreter(
        self, tmp_path, monkeypatch, capsys
    ):
        # pip/sdist installs may drop the exec bit (deep evaluator,
        # PR 2): a packaged check must run via its interpreter, not
        # FAIL for a packaging artifact.
        checks = tmp_path / "checks"
        checks.mkdir()
        stub = checks / "10-stub.py"
        stub.write_text(
            "print('DOCTOR:10-stub.py:PASS:ran without exec bit')\n",
            encoding="utf-8",
        )  # deliberately NOT chmod +x
        monkeypatch.setattr(doctor, "PACKAGED_CHECKS_DIR", checks)
        (tmp_path / "root").mkdir()
        code = doctor.cmd_doctor([], tmp_path / "root")
        out = capsys.readouterr().out
        assert "DOCTOR:10-stub.py:PASS:ran without exec bit" in out
        assert code == 0

    def test_repo_local_checks_keep_strict_exec_contract(self, tmp_path, capsys):
        # The strict FAIL for non-executable files is unchanged outside
        # the packaged dir (behavior pinned by tests/test_doctor.py).
        local = tmp_path / "root" / "scripts" / "core" / "doctor.d"
        local.mkdir(parents=True)
        (local / "10-inert.py").write_text("print('nope')\n", encoding="utf-8")
        code = doctor.cmd_doctor([], tmp_path / "root")
        out = capsys.readouterr().out
        assert "DOCTOR:10-inert.py:FAIL:check file is not executable" in out
        assert code == 1

    def test_sh_check_runs_via_bash_fallback(self, tmp_path, monkeypatch, capsys):
        checks = tmp_path / "checks"
        checks.mkdir()
        stub = checks / "10-stub.sh"
        stub.write_text(
            "echo 'DOCTOR:10-stub.sh:PASS:bash fallback ran'\n", encoding="utf-8"
        )  # no exec bit
        monkeypatch.setattr(doctor, "PACKAGED_CHECKS_DIR", checks)
        (tmp_path / "root").mkdir()
        code = doctor.cmd_doctor([], tmp_path / "root")
        assert "DOCTOR:10-stub.sh:PASS:bash fallback ran" in capsys.readouterr().out
        assert code == 0

    def test_unmapped_suffix_still_fails(self, tmp_path, monkeypatch, capsys):
        checks = tmp_path / "checks"
        checks.mkdir()
        (checks / "10-stub.rb").write_text("puts 'nope'\n", encoding="utf-8")
        monkeypatch.setattr(doctor, "PACKAGED_CHECKS_DIR", checks)
        (tmp_path / "root").mkdir()
        code = doctor.cmd_doctor([], tmp_path / "root")
        assert "DOCTOR:10-stub.rb:FAIL:check file is not executable" in (
            capsys.readouterr().out
        )
        assert code == 1


class TestPackagedInstallRecordReader:
    """KIT-0093 (BugBot, PR #116): packaged repos ship no
    scripts/local/kit_markers.py — the record reader travels with the
    package, and the two paths share one parser."""

    def _claude_md(self, tmp_path, body):
        (tmp_path / "CLAUDE.md").write_text(body, encoding="utf-8")
        return tmp_path

    def test_record_read_without_kit_markers_copy(self, tmp_path):
        root = self._claude_md(
            tmp_path,
            "# P\n\n<!-- BEGIN KIT-LOCAL: kit-install -->\n"
            "shape: planning\nprofile: none\n"
            "<!-- END KIT-LOCAL: kit-install -->\n",
        )
        assert doctor._doctor_install(root) == ("planning", "none", None, [])

    def test_bots_line_read_without_kit_markers_copy(self, tmp_path):
        root = self._claude_md(
            tmp_path,
            "# P\n\n<!-- BEGIN KIT-LOCAL: kit-install -->\n"
            "shape: single\nprofile: python\nbots: coderabbit\n"
            "<!-- END KIT-LOCAL: kit-install -->\n",
        )
        shape, profile, bots, errors = doctor._doctor_install(root)
        assert (shape, profile, errors) == ("single", "python", [])
        assert bots == ["coderabbit"] or bots == "coderabbit"

    def test_absent_region_keeps_backcompat_default(self, tmp_path):
        root = self._claude_md(tmp_path, "# P\nno region here\n")
        assert doctor._doctor_install(root) == ("single", "python", None, [])

    def test_unbalanced_markers_fail_loud_not_default(self, tmp_path):
        root = self._claude_md(
            tmp_path,
            "# P\n<!-- BEGIN KIT-LOCAL: kit-install -->\nshape: planning\n",
        )
        shape, profile, bots, errors = doctor._doctor_install(root)
        assert shape is None
        assert errors and "malformed" in errors[0][1]

    def test_prose_mention_of_marker_is_not_malformed(self, tmp_path):
        # BugBot round 2 (PR #116): docs PROSE naming the marker must
        # not read as an unbalanced region — only the exact comment
        # form counts.
        root = self._claude_md(
            tmp_path,
            "# P\nThe record lives between BEGIN KIT-LOCAL: kit-install "
            "markers in this file.\n",
        )
        assert doctor._doctor_install(root) == ("single", "python", None, [])

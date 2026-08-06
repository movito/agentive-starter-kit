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

"""Tests for agentive_kit.evaluators — provisioning + pin readers.

The legacy install/ensure behavior remains covered by
tests/test_project_script.py against the script's inline fallback
copy; this module covers what is NEW in the package: the KIT-0079
config.yml-first library-pin reader (closed by reference here).
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "agentive_kit", reason="agentive-kit package source present only in the kit repo"
)

from agentive_kit import evaluators  # noqa: E402


def _cfg(tmp_path, body):
    d = tmp_path / ".adversarial"
    d.mkdir(exist_ok=True)
    (d / "config.yml").write_text(body, encoding="utf-8")


class TestLibraryPinReader:
    def test_config_yml_is_canonical(self, tmp_path):
        _cfg(tmp_path, 'evaluator_library_version: "v0.10.0"\n')
        (tmp_path / "pyproject.toml").write_text(
            '[tool.adversarial]\nlibrary_version = "v0.9.0"\n', encoding="utf-8"
        )
        assert evaluators._get_evaluator_library_version(tmp_path) == "v0.10.0"

    def test_pyproject_is_the_fallback_mirror(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text(
            '[tool.adversarial]\nlibrary_version = "v0.9.0"\n', encoding="utf-8"
        )
        assert evaluators._get_evaluator_library_version(tmp_path) == "v0.9.0"

    def test_planning_shape_resolves_without_pyproject(self, tmp_path):
        # The KIT-0079 incident: planning repos ship no pyproject at
        # all — the pin must resolve from config.yml alone.
        _cfg(tmp_path, 'evaluator_library_version: "v0.10.0"\n')
        assert evaluators._get_evaluator_library_version(tmp_path) == "v0.10.0"

    def test_commented_pin_is_not_read(self, tmp_path):
        _cfg(tmp_path, '# evaluator_library_version: "v9.9.9"\n')
        (tmp_path / "pyproject.toml").write_text(
            '[tool.adversarial]\nlibrary_version = "v0.9.0"\n', encoding="utf-8"
        )
        assert evaluators._get_evaluator_library_version(tmp_path) == "v0.9.0"

    def test_no_pin_anywhere_exits_naming_both_sources(self, tmp_path, capsys):
        with pytest.raises(SystemExit) as exc_info:
            evaluators._get_evaluator_library_version(tmp_path)
        assert exc_info.value.code == 1
        out = capsys.readouterr().out
        assert "evaluator_library_version" in out
        assert "library_version" in out

    def test_kit_repo_pin_resolves_from_config(self):
        # The kit's own checkout: config.yml is canonical and readable.
        from pathlib import Path

        repo = Path(__file__).resolve().parent.parent.parent
        if not (repo / ".adversarial" / "config.yml").is_file():
            pytest.skip("no .adversarial/config.yml in this checkout")
        version = evaluators._get_evaluator_library_version(repo)
        assert version.startswith("v")

    def test_option_shaped_pin_is_rejected_loudly(self, tmp_path, capsys):
        # Deep evaluator (PR 3): a config.yml pin must never become a
        # git OPTION (`--upload-pack=...`) — reject before the clone.
        _cfg(tmp_path, "evaluator_library_version: --upload-pack=/bin/evil\n")
        with pytest.raises(SystemExit) as exc_info:
            evaluators._get_evaluator_library_version(tmp_path)
        assert exc_info.value.code == 1
        assert "Invalid evaluator_library_version" in capsys.readouterr().out

    def test_option_shaped_pyproject_mirror_pin_is_rejected(self, tmp_path, capsys):
        # The mirror is hand-edited too (CodeRabbit, PR #110): the same
        # gate applies whichever source resolves the pin.
        (tmp_path / "pyproject.toml").write_text(
            '[tool.adversarial]\nlibrary_version = "--upload-pack=/bin/evil"\n',
            encoding="utf-8",
        )
        with pytest.raises(SystemExit) as exc_info:
            evaluators._get_evaluator_library_version(tmp_path)
        assert exc_info.value.code == 1
        assert "Invalid library_version" in capsys.readouterr().out

    def test_non_string_pyproject_pin_is_rejected_without_traceback(
        self, tmp_path, capsys
    ):
        # tomllib returns an int for `library_version = 1` — the gate
        # must reject it cleanly, not raise TypeError (CodeRabbit,
        # PR #110).
        (tmp_path / "pyproject.toml").write_text(
            "[tool.adversarial]\nlibrary_version = 1\n", encoding="utf-8"
        )
        with pytest.raises(SystemExit) as exc_info:
            evaluators._get_evaluator_library_version(tmp_path)
        assert exc_info.value.code == 1
        assert "Invalid library_version" in capsys.readouterr().out

    def test_regex_fallback_rejects_non_string_pin(self, tmp_path, capsys, monkeypatch):
        # Force the bare-3.10 path: no tomllib, no tomli — the regex
        # fallback must mirror tomllib semantics for a non-string
        # scalar: invalid pin, not missing pin (CodeRabbit, PR #110).
        import sys as _sys

        monkeypatch.setitem(_sys.modules, "tomllib", None)
        monkeypatch.setitem(_sys.modules, "tomli", None)
        (tmp_path / "pyproject.toml").write_text(
            "[tool.adversarial]\nlibrary_version = 1\n", encoding="utf-8"
        )
        with pytest.raises(SystemExit) as exc_info:
            evaluators._get_evaluator_library_version(tmp_path)
        assert exc_info.value.code == 1
        assert "Invalid library_version" in capsys.readouterr().out

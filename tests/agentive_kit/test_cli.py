"""Tests for agentive_kit.cli — the ``agentive`` console entry.

The CLI's one behavioral difference from the legacy script is root
discovery (KIT-0090 F2): it resolves the project by walking up from the
current directory and refuses loudly outside a kit repo. The lifecycle
behavior itself is covered in test_lifecycle.py; here we test the
dispatch surface and the discovery wiring.
"""

from __future__ import annotations

import subprocess

import pytest

pytest.importorskip(
    "agentive_kit", reason="agentive-kit package source present only in the kit repo"
)

from agentive_kit import cli  # noqa: E402

TASK_FILE = "KIT-1234-sample-task.md"


def make_kit_tree(tmp_path, branch="main"):
    tasks = tmp_path / ".kit" / "tasks"
    for folder in ("2-todo", "3-in-progress", "5-done", "7-blocked"):
        (tasks / folder).mkdir(parents=True)
    (tasks / "2-todo" / TASK_FILE).write_text("**Status**: Todo\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    if branch is not None:
        subprocess.run(
            ["git", "init", "-q", "-b", branch, str(tmp_path)],
            check=True,
            capture_output=True,
            timeout=30,
        )
    return tmp_path


def run_cli(args):
    with pytest.raises(SystemExit) as exc_info:
        cli.main(args)
    return exc_info.value.code


class TestDispatch:
    def test_no_args_prints_usage(self, capsys):
        assert run_cli([]) == 0
        out = capsys.readouterr().out
        assert "Usage: agentive" in out

    def test_help_exits_zero(self, capsys):
        assert run_cli(["help"]) == 0
        assert "Task Management" in capsys.readouterr().out

    def test_version_prints_package_version(self, capsys):
        import agentive_kit

        assert run_cli(["version"]) == 0
        assert f"agentive-kit v{agentive_kit.__version__}" in capsys.readouterr().out

    def test_unknown_command_exits_one(self, capsys):
        assert run_cli(["frobnicate"]) == 1
        out = capsys.readouterr().out
        assert "Unknown command" in out
        # Not-yet-migrated commands still have a home; the error says so.
        assert "scripts/core/project" in out

    def test_move_usage_error(self, capsys):
        assert run_cli(["move", "KIT-1234"]) == 1
        assert "Usage: agentive move" in capsys.readouterr().out

    def test_start_usage_error(self, capsys):
        assert run_cli(["start"]) == 1
        assert "Usage: agentive start" in capsys.readouterr().out

    def test_surplus_arguments_rejected(self, capsys):
        # CodeRabbit (PR #108): surplus args are a usage error, never
        # silently ignored — a mistyped automation call must fail loud.
        assert run_cli(["start", "KIT-1234", "extra"]) == 1
        assert "Usage: agentive start" in capsys.readouterr().out
        assert run_cli(["move", "KIT-1234", "done", "extra"]) == 1
        assert "Usage: agentive move" in capsys.readouterr().out
        assert run_cli(["validate", "extra"]) == 1
        assert "Usage: agentive validate" in capsys.readouterr().out


class TestRootDiscoveryWiring:
    def test_start_from_subdirectory_moves_task(self, tmp_path, monkeypatch, capsys):
        root = make_kit_tree(tmp_path)
        nested = root / "docs" / "deep"
        nested.mkdir(parents=True)
        monkeypatch.chdir(nested)

        assert run_cli(["start", "KIT-1234"]) == 0

        moved = root / ".kit" / "tasks" / "3-in-progress" / TASK_FILE
        assert moved.exists()
        assert "In Progress" in capsys.readouterr().out

    def test_complete_and_block_shorthands(self, tmp_path, monkeypatch):
        root = make_kit_tree(tmp_path)
        monkeypatch.chdir(root)
        assert run_cli(["complete", "KIT-1234"]) == 0
        assert (root / ".kit" / "tasks" / "5-done" / TASK_FILE).exists()
        assert run_cli(["block", "KIT-1234"]) == 0
        assert (root / ".kit" / "tasks" / "7-blocked" / TASK_FILE).exists()

    def test_validate_exit_codes(self, tmp_path, monkeypatch):
        root = make_kit_tree(tmp_path)
        monkeypatch.chdir(root)
        assert run_cli(["validate"]) == 0
        wrong = root / ".kit" / "tasks" / "5-done" / "KIT-0003-wrong.md"
        wrong.write_text("**Status**: Todo\n", encoding="utf-8")
        assert run_cli(["validate"]) == 1

    def test_outside_kit_repo_refuses_loudly(self, tmp_path, monkeypatch, capsys):
        plain = tmp_path / "plain"
        plain.mkdir()
        monkeypatch.chdir(plain)
        assert run_cli(["validate"]) == 1
        assert "Not inside an agentive project" in capsys.readouterr().out

    def test_failed_move_exits_one(self, tmp_path, monkeypatch, capsys):
        root = make_kit_tree(tmp_path)
        monkeypatch.chdir(root)
        assert run_cli(["start", "KIT-9999"]) == 1
        assert "Task not found" in capsys.readouterr().out

    def test_partial_failure_exits_one(self, tmp_path, monkeypatch, capsys):
        # Moved but Status field unset → nonzero exit (CodeRabbit,
        # PR #108).
        root = make_kit_tree(tmp_path)
        task = root / ".kit" / "tasks" / "2-todo" / TASK_FILE
        task.write_text("# no status header\n", encoding="utf-8")
        monkeypatch.chdir(root)
        assert run_cli(["start", "KIT-1234"]) == 1
        assert "Status field not updated" in capsys.readouterr().out


class TestEnvironmentCommands:
    """KIT-0093 PR 2: doctor + install-evaluators join the console
    entry (the phase-2 door tail depends on them)."""

    def test_doctor_dispatches_to_driver(self, tmp_path, monkeypatch, capsys):
        root = make_kit_tree(tmp_path)
        checks = tmp_path / "stub-checks"
        checks.mkdir()
        check = checks / "10-ok.sh"
        check.write_text(
            "#!/bin/sh\necho 'DOCTOR:ok:PASS:stub check'\n", encoding="utf-8"
        )
        check.chmod(0o755)
        monkeypatch.chdir(root)
        assert run_cli(["doctor", f"--dir={checks}"]) == 0
        assert "ok" in capsys.readouterr().out

    def test_doctor_usage_error_exits_three(self, tmp_path, monkeypatch, capsys):
        root = make_kit_tree(tmp_path)
        monkeypatch.chdir(root)
        assert run_cli(["doctor", "--dir="]) == 3
        assert "--dir=" in capsys.readouterr().out

    def test_install_evaluators_rejects_option_shaped_ref(
        self, tmp_path, monkeypatch, capsys
    ):
        # Reaches agentive_kit.evaluators and fails on the --ref gate
        # BEFORE any network/git work — dispatch verified hermetically.
        root = make_kit_tree(tmp_path)
        monkeypatch.chdir(root)
        assert run_cli(["install-evaluators", "--ref", "--force"]) == 1
        assert "Invalid --ref value" in capsys.readouterr().out

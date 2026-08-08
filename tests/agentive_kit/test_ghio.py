"""Tests for agentive_kit.ghio — the package's single gh boundary (KIT-0091).

Mirrors the stub-git discipline from test_gitio.py with a stub ``gh``
on PATH: no test here ever reaches the network or a real gh install.
Failure paths get explicit coverage (the PR #107 lesson): gh absent,
gh failing, gh hanging past the timeout.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

pytest.importorskip(
    "agentive_kit", reason="agentive-kit package source present only in the kit repo"
)

from agentive_kit import ghio  # noqa: E402


def _make_stub(bin_dir: Path, body: str) -> None:
    bin_dir.mkdir(parents=True, exist_ok=True)
    stub = bin_dir / "gh"
    stub.write_text("#!/bin/bash\n" + body, encoding="utf-8")
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


@pytest.fixture
def stub_path(tmp_path, monkeypatch):
    """Prepend a stub-bin dir to PATH; tests write their own gh stub."""
    bin_dir = tmp_path / "stub-bin"
    bin_dir.mkdir()
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
    return bin_dir


class TestRunGh:
    def test_success_captures_stdout(self, stub_path):
        _make_stub(stub_path, 'echo "hello"\nexit 0\n')
        result = ghio.run_gh("pr", "view")
        assert result is not None
        assert result.returncode == 0
        assert result.stdout.strip() == "hello"

    def test_gh_ran_and_failed_is_completed_process(self, stub_path):
        # "gh said no" must stay distinguishable from "no gh": a failing
        # gh returns a CompletedProcess, never None.
        _make_stub(stub_path, 'echo "boom" >&2\nexit 2\n')
        result = ghio.run_gh("api", "graphql")
        assert result is not None
        assert result.returncode == 2
        assert "boom" in result.stderr

    def test_gh_unfindable_is_none(self, tmp_path, monkeypatch):
        empty = tmp_path / "empty-path"
        empty.mkdir()
        monkeypatch.setenv("PATH", str(empty))
        assert ghio.run_gh("auth", "status") is None

    def test_timeout_is_none(self, stub_path):
        # A wedged gh (auth prompt, proxy black hole) fails its one call
        # instead of hanging the gate run.
        _make_stub(stub_path, "sleep 5\n")
        assert ghio.run_gh("api", "graphql", timeout=1) is None

    def test_repo_flag_inserted_directly_after_gh(self, stub_path, tmp_path):
        # The legacy scripts expand $GH_REPO_ARG immediately after `gh`
        # (gh --repo owner/name pr view …) — the flag position is part
        # of the pinned command shape the parity stubs dispatch on.
        record = tmp_path / "argv.txt"
        _make_stub(stub_path, f'printf \'%s\\n\' "$@" > "{record}"\nexit 0\n')
        ghio.run_gh("pr", "view", "42", repo="owner/name")
        assert record.read_text(encoding="utf-8").splitlines() == [
            "--repo",
            "owner/name",
            "pr",
            "view",
            "42",
        ]

    def test_no_repo_emits_no_flag(self, stub_path, tmp_path):
        record = tmp_path / "argv.txt"
        _make_stub(stub_path, f'printf \'%s\\n\' "$@" > "{record}"\nexit 0\n')
        ghio.run_gh("pr", "view", repo=None)
        assert record.read_text(encoding="utf-8").splitlines() == ["pr", "view"]

    def test_stdin_is_closed(self, stub_path):
        # A gh that tries to prompt must read EOF, not inherit the
        # session's stdin and hang.
        _make_stub(stub_path, 'read -r line && echo "got:$line"\necho "eof:$?"\n')
        result = ghio.run_gh("auth", "login")
        assert result is not None
        assert "got:" not in result.stdout
        assert "eof:1" in result.stdout


class TestGhAvailable:
    def test_true_with_stub_on_path(self, stub_path):
        _make_stub(stub_path, "exit 0\n")
        assert ghio.gh_available() is True

    def test_false_without_gh(self, tmp_path, monkeypatch):
        empty = tmp_path / "empty-path"
        empty.mkdir()
        monkeypatch.setenv("PATH", str(empty))
        assert ghio.gh_available() is False


class TestAuthOk:
    def test_authenticated(self, stub_path):
        _make_stub(stub_path, "exit 0\n")
        assert ghio.auth_ok() is True

    def test_unauthenticated(self, stub_path):
        _make_stub(stub_path, "exit 1\n")
        assert ghio.auth_ok() is False

    def test_gh_absent(self, tmp_path, monkeypatch):
        empty = tmp_path / "empty-path"
        empty.mkdir()
        monkeypatch.setenv("PATH", str(empty))
        assert ghio.auth_ok() is False


class TestDefaultRepoSlug:
    def test_slug(self, stub_path):
        _make_stub(stub_path, 'echo "owner/repo"\nexit 0\n')
        assert ghio.default_repo_slug() == "owner/repo"

    def test_gh_failure_is_none(self, stub_path):
        _make_stub(stub_path, "exit 1\n")
        assert ghio.default_repo_slug() is None

    def test_empty_output_is_none(self, stub_path):
        # gh exiting 0 with nothing to say (no default repo configured)
        # must read as "unknown", not as an empty slug.
        _make_stub(stub_path, "exit 0\n")
        assert ghio.default_repo_slug() is None

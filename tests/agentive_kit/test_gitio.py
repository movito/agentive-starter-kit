"""Tests for agentive_kit.gitio — the package's single git boundary.

Ports the KIT-0080 portability discipline and PR #107's failure-path
lesson (the KIT-0080 retro: the one-liner fix was verified on the happy
path only — so the failure paths get explicit tests here): git absent,
not a repository, nonexistent directory, ambient GIT_* leakage.

Migrates TestDeriveRepoUrl from tests/test_project_script.py (KIT-0090
F3: per-module tests move with their code).
"""

from __future__ import annotations

import subprocess

import pytest

pytest.importorskip(
    "agentive_kit", reason="agentive-kit package source present only in the kit repo"
)

from agentive_kit import gitio  # noqa: E402


def _git(repo, *args):
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )


def init_repo(path, branch="main", commit=True):
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "init", "-q", "-b", branch, str(path)],
        check=True,
        capture_output=True,
        timeout=30,
    )
    if commit:
        _git(
            path,
            "-c",
            "user.email=test@test",
            "-c",
            "user.name=test",
            "commit",
            "--allow-empty",
            "-m",
            "init",
        )
    return path


class TestCurrentBranch:
    def test_main(self, tmp_path):
        repo = init_repo(tmp_path / "repo")
        assert gitio.current_branch(repo) == "main"

    def test_feature_branch(self, tmp_path):
        repo = init_repo(tmp_path / "repo")
        _git(repo, "checkout", "-q", "-b", "feature/KIT-0000-x")
        assert gitio.current_branch(repo) == "feature/KIT-0000-x"

    def test_unborn_branch_still_reports_name(self, tmp_path):
        # A fresh init with no commits: HEAD is an unborn symref, and
        # `branch --show-current` still prints the name (git >= 2.22).
        repo = init_repo(tmp_path / "repo", commit=False)
        assert gitio.current_branch(repo) == "main"

    def test_detached_head_is_none(self, tmp_path):
        repo = init_repo(tmp_path / "repo")
        _git(repo, "checkout", "-q", "--detach")
        assert gitio.current_branch(repo) is None

    def test_non_repo_is_none(self, tmp_path):
        assert gitio.current_branch(tmp_path) is None

    def test_git_unfindable_is_none(self, tmp_path, monkeypatch):
        empty = tmp_path / "empty-path"
        empty.mkdir()
        monkeypatch.setenv("PATH", str(empty))
        assert gitio.current_branch(tmp_path) is None


class TestRunGit:
    def test_nonexistent_dir_fails_without_raising(self, tmp_path):
        # PR #107 class: resolvers must fail clean, not crash, when the
        # directory they anchor on is gone.
        result = gitio.run_git(tmp_path / "missing", "status")
        assert result is not None
        assert result.returncode != 0

    def test_ambient_git_dir_is_scrubbed(self, tmp_path, monkeypatch):
        # The KIT-0043 incident class: pre-commit exports GIT_DIR, which
        # overrides -C and silently points git at the WRONG repo. The
        # scrub makes -C authoritative.
        repo_a = init_repo(tmp_path / "a")
        repo_b = init_repo(tmp_path / "b", branch="other")
        monkeypatch.setenv("GIT_DIR", str(repo_a / ".git"))
        assert gitio.current_branch(repo_b) == "other"

    def test_clean_git_env_strips_location_vars(self, monkeypatch):
        monkeypatch.setenv("GIT_DIR", "/somewhere/.git")
        monkeypatch.setenv("GIT_WORK_TREE", "/somewhere")
        monkeypatch.setenv("GIT_INDEX_FILE", "/somewhere/index")
        env = gitio.clean_git_env()
        assert "GIT_DIR" not in env
        assert "GIT_WORK_TREE" not in env
        assert "GIT_INDEX_FILE" not in env

    def test_clean_git_env_preserves_behavior_vars(self, monkeypatch):
        # Only location overrides are the KIT-0043 class; a custom
        # install's SSH/exec-path settings must survive (evaluator
        # finding, PR 1 trio).
        monkeypatch.setenv("GIT_SSH_COMMAND", "ssh -i /key")
        monkeypatch.setenv("GIT_EXEC_PATH", "/opt/git/libexec")
        env = gitio.clean_git_env()
        assert env["GIT_SSH_COMMAND"] == "ssh -i /key"
        assert env["GIT_EXEC_PATH"] == "/opt/git/libexec"


class TestGitCommonDir:
    def test_primary_clone(self, tmp_path):
        repo = init_repo(tmp_path / "repo")
        assert gitio.git_common_dir(repo) == repo / ".git"

    def test_worktree_points_at_primary(self, tmp_path):
        primary = init_repo(tmp_path / "primary")
        wt = tmp_path / "wt"
        _git(primary, "worktree", "add", "-q", str(wt), "-b", "wt-branch")
        assert gitio.git_common_dir(wt) == primary / ".git"

    def test_anchors_on_repo_dir_not_cwd(self, tmp_path, monkeypatch):
        # KIT-0080: plain --git-common-dir output is RELATIVE to -C (a
        # bare ".git" from a primary clone) — it must be absolutized
        # against the repo dir, never the process CWD.
        repo = init_repo(tmp_path / "repo")
        elsewhere = tmp_path / "elsewhere"
        elsewhere.mkdir()
        monkeypatch.chdir(elsewhere)
        assert gitio.git_common_dir(repo) == repo / ".git"

    def test_non_repo_is_none(self, tmp_path):
        assert gitio.git_common_dir(tmp_path) is None


class TestDeriveRepoUrl:
    """Migrated from tests/test_project_script.py (KIT-0090 F3)."""

    def test_ssh_url(self, tmp_path):
        repo = init_repo(tmp_path / "repo")
        _git(repo, "remote", "add", "origin", "git@github.com:owner/repo.git")
        assert gitio.derive_repo_url(repo) == "github.com/owner/repo"

    def test_https_url(self, tmp_path):
        repo = init_repo(tmp_path / "repo")
        _git(repo, "remote", "add", "origin", "https://github.com/owner/repo.git")
        assert gitio.derive_repo_url(repo) == "github.com/owner/repo"

    def test_https_url_without_dot_git(self, tmp_path):
        repo = init_repo(tmp_path / "repo")
        _git(repo, "remote", "add", "origin", "https://github.com/owner/repo")
        assert gitio.derive_repo_url(repo) == "github.com/owner/repo"

    def test_http_url(self, tmp_path):
        repo = init_repo(tmp_path / "repo")
        _git(repo, "remote", "add", "origin", "http://github.com/owner/repo.git")
        assert gitio.derive_repo_url(repo) == "github.com/owner/repo"

    def test_no_remote(self, tmp_path):
        repo = init_repo(tmp_path / "repo")
        assert gitio.derive_repo_url(repo) is None

    def test_no_git_repo(self, tmp_path):
        assert gitio.derive_repo_url(tmp_path) is None

    @pytest.mark.parametrize(
        "url",
        [
            "git://github.com/owner/repo.git",
            "ssh://git@github.com/owner/repo.git",
            "/local/path/repo.git",
        ],
    )
    def test_unrecognized_url_format_returns_none(self, tmp_path, url):
        repo = init_repo(tmp_path / "repo")
        _git(repo, "remote", "add", "origin", url)
        assert gitio.derive_repo_url(repo) is None

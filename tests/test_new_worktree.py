"""Tests for scripts/local/new-worktree.sh provisioning (KIT-0071).

Covers the orchestration the CodeRabbit round flagged as untested: no
.venv symlink, read-only symlinks still provisioned, Serena config
generated with a per-worktree name, `project setup --no-hooks`
invoked, and the non-fatal venv-failure fallback.

Fixture: a real primary clone with a local bare origin (the helper
fetches origin and branches from origin/main — no network). The
checkout carries a STUB scripts/core/project that records its argv,
so provisioning is observable without a real pip install.

Kit-only: excluded from the consumer tests rsync in engine-consumer.sh
(scripts/local/ does not ship to single-shape consumers) and
module-skips when the helper is absent — the test_kit_markers.py
pattern.
"""

from __future__ import annotations

import os
import shlex
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
HELPER = REPO_ROOT / "scripts" / "local" / "new-worktree.sh"
SERENA_TEMPLATE = REPO_ROOT / ".serena" / "project.yml.template"

if not HELPER.exists():
    pytest.skip(
        "new-worktree.sh absent (consumer checkout — scripts/local not synced)",
        allow_module_level=True,
    )


@pytest.fixture(autouse=True)
def _isolate_git_env(monkeypatch):
    """Strip ambient GIT_* — same contract as the sibling modules."""
    for key in list(os.environ):
        if key.startswith("GIT_"):
            monkeypatch.delenv(key, raising=False)


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=True,
        capture_output=True,
        timeout=30,
    )


def _make_executable(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _primary_fixture(
    tmp_path: Path, setup_stub_exit: int = 0, primary_name: str = "kit"
) -> Path:
    """A primary clone (default name kit/) with a local bare origin,
    carrying the real helper, the real Serena template, and a stub
    `project` that records its argv to setup-args.txt in its own
    checkout."""
    primary = tmp_path / primary_name
    (primary / "scripts" / "local").mkdir(parents=True)
    (primary / "scripts" / "core").mkdir(parents=True)
    (primary / ".serena").mkdir()

    helper_copy = primary / "scripts" / "local" / "new-worktree.sh"
    _make_executable(helper_copy, HELPER.read_text(encoding="utf-8"))
    (primary / ".serena" / "project.yml.template").write_text(
        SERENA_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8"
    )
    _make_executable(
        primary / "scripts" / "core" / "project",
        "#!/usr/bin/env bash\n"
        'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"\n'
        'ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"\n'
        'printf \'%s\\n\' "$*" >> "$ROOT/setup-args.txt"\n'
        f"exit {setup_stub_exit}\n",
    )

    _git(primary, "init", "--quiet", "-b", "main")
    for key, value in (("user.email", "t@example.com"), ("user.name", "t")):
        _git(primary, "config", key, value)
    _git(primary, "add", "-A")
    _git(primary, "commit", "--quiet", "-m", "fixture")

    origin = tmp_path / "origin.git"
    subprocess.run(
        ["git", "init", "--quiet", "--bare", str(origin)],
        check=True,
        timeout=30,
    )
    _git(primary, "remote", "add", "origin", str(origin))
    _git(primary, "push", "--quiet", "-u", "origin", "main")

    # untracked runtime artifacts the helper symlinks / reads
    (primary / ".env").write_text("KEY=value\n", encoding="utf-8")
    (primary / ".adversarial" / "evaluators").mkdir(parents=True)
    (primary / ".serena" / "project.yml").write_text(
        'project_name: "kit"\n', encoding="utf-8"
    )
    return primary


def _run_helper(primary: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(primary / "scripts" / "local" / "new-worktree.sh"), *args],
        capture_output=True,
        text=True,
        timeout=60,
    )


class TestProvisioning:
    def test_full_provisioning_contract(self, tmp_path):
        primary = _primary_fixture(tmp_path)
        result = _run_helper(primary, "KIT-1234", "demo")
        assert result.returncode == 0, result.stdout + result.stderr
        wt = tmp_path / "ask-worktrees" / "KIT-1234"
        assert wt.is_dir()

        # F1: .venv is NEVER symlinked (the stub created no venv at all)
        assert not (wt / ".venv").is_symlink()
        # read-only artifacts still symlink to the primary
        assert (wt / ".env").is_symlink()
        assert (wt / ".adversarial" / "evaluators").is_symlink()

        # F5: worktree-local Serena config with a per-worktree name
        serena = (wt / ".serena" / "project.yml").read_text(encoding="utf-8")
        assert 'project_name: "kit-KIT-1234"' in serena
        assert "Serena config generated" in result.stdout

        # venv provisioning went through the checkout's own project
        # script with --no-hooks (shared hooks stay untouched)
        recorded = (wt / "setup-args.txt").read_text(encoding="utf-8")
        assert recorded.strip() == "setup --no-hooks"

        # LAUNCH block carries the Serena absolute-path rule
        assert "LAUNCH" in result.stdout
        assert "ABSOLUTE PATH" in result.stdout

    def test_venv_failure_is_non_fatal(self, tmp_path):
        primary = _primary_fixture(tmp_path, setup_stub_exit=1)
        result = _run_helper(primary, "KIT-1234", "demo")
        assert result.returncode == 0, result.stdout + result.stderr
        wt = tmp_path / "ask-worktrees" / "KIT-1234"
        assert wt.is_dir()
        # the worktree survives; the fallback names a paste-safe,
        # %q-escaped recovery command (BugBot round 5 — bare for a
        # plain path)
        combined = result.stdout + result.stderr
        assert "venv provisioning failed" in combined
        assert f"cd {wt} && ./scripts/core/project setup --no-hooks" in combined
        assert "Worktree ready" in result.stdout

    def test_no_serena_generation_when_primary_lacks_config(self, tmp_path):
        primary = _primary_fixture(tmp_path)
        (primary / ".serena" / "project.yml").unlink()
        result = _run_helper(primary, "KIT-1234", "demo")
        assert result.returncode == 0, result.stdout + result.stderr
        wt = tmp_path / "ask-worktrees" / "KIT-1234"
        assert not (wt / ".serena" / "project.yml").exists()
        assert "Serena config generated" not in result.stdout

    def test_ampersand_in_primary_dirname_survives_substitution(self, tmp_path):
        # BugBot round 2: bash >= 5.2 patsub_replacement expands & in
        # the replacement — the helper disables it so the name stays
        # literal (on older bash this was always literal)
        primary = _primary_fixture(tmp_path, primary_name="kit&co")
        result = _run_helper(primary, "KIT-1234", "demo")
        assert result.returncode == 0, result.stdout + result.stderr
        wt = tmp_path / "ask-worktrees" / "KIT-1234"
        serena = (wt / ".serena" / "project.yml").read_text(encoding="utf-8")
        assert 'project_name: "kit&co-KIT-1234"' in serena


# ─────────────────────────────────────────────────────────────────────
# KIT-0080 / S4: the helper must resolve the primary clone on old git
# ─────────────────────────────────────────────────────────────────────
# `git rev-parse --path-format=absolute` needs git >= 2.31. Apple's
# system git (2.30.1, stock on macOS) echoes the flag back as an output
# line instead of consuming it, so PRIMARY_ROOT became garbage and the
# line-42 guard hard-exited: worktree creation — the kit's DEFAULT
# session topology — was dead on every stock Mac. CI runners ship modern
# git, so this stub is the only coverage of that behavior here.

OLD_GIT_STUB = """#!/bin/bash
# Emulates git 2.30.x: --path-format=* is NOT consumed, it is echoed as
# an output line; every other arg is answered by the real git.
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


def _old_git_path(base: Path) -> str:
    """A PATH string whose `git` mimics git 2.30.x flag handling."""
    real = shutil.which("git")
    assert real, "git required for this fixture"
    bin_dir = base / "old-git-bin"
    bin_dir.mkdir()
    # shlex.quote: an unquoted REAL= assignment breaks the stub outright
    # if git's path contains spaces (bash would run the second word as a
    # command) — same fix as the sibling fixture in test_doctor.py
    # (CodeRabbit, this PR).
    _make_executable(bin_dir / "git", OLD_GIT_STUB.format(real=shlex.quote(real)))
    return f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"


class TestOldGitResolution:
    """S4: identical, correct resolution on both git generations."""

    def test_stub_reproduces_the_230_flag_echo(self, tmp_path):
        """Pin the stub itself — a stub that stopped emulating the bug
        would make the test below vacuously green."""
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "--quiet", str(repo)], check=True, timeout=30)
        result = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "rev-parse",
                "--path-format=absolute",
                "--git-dir",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "PATH": _old_git_path(tmp_path)},
        )
        assert result.stdout.splitlines()[0] == "--path-format=absolute"
        assert result.returncode == 0, "2.30.x exits 0 — that is what made it silent"

    def test_helper_provisions_under_old_git(self, tmp_path):
        """The whole helper runs green on 2.30.x: the resolution guard
        never fires and the worktree lands in the primary's sibling
        dir, exactly as on modern git."""
        primary = _primary_fixture(tmp_path)
        result = subprocess.run(
            [
                "bash",
                str(primary / "scripts" / "local" / "new-worktree.sh"),
                "KIT-0001",
                "demo",
            ],
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ, "PATH": _old_git_path(tmp_path)},
        )
        assert result.returncode == 0, (
            f"S4 regressed — helper died on git 2.30.x\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        # The exact S4 failure signature.
        assert "could not resolve primary clone root" not in result.stderr
        assert "dirname:" not in result.stderr
        assert (tmp_path / "ask-worktrees" / "KIT-0001").is_dir(), result.stdout

    def test_resolution_matches_modern_git(self, tmp_path):
        """Same helper, same fixture, both gits — the worktree must land
        in the same place. A divergence here is the silent-wrong-answer
        half of the bug (S3) rather than the hard-death half (S4)."""
        modern_primary = _primary_fixture(tmp_path / "modern", primary_name="kit")
        old_primary = _primary_fixture(tmp_path / "old", primary_name="kit")
        for base in (tmp_path / "modern", tmp_path / "old"):
            base.mkdir(exist_ok=True)

        modern = _run_helper(modern_primary, "KIT-0002", "demo")
        old = subprocess.run(
            [
                "bash",
                str(old_primary / "scripts" / "local" / "new-worktree.sh"),
                "KIT-0002",
                "demo",
            ],
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ, "PATH": _old_git_path(tmp_path)},
        )
        assert modern.returncode == 0, modern.stderr
        assert old.returncode == 0, old.stderr
        modern_wt = tmp_path / "modern" / "ask-worktrees" / "KIT-0002"
        old_wt = tmp_path / "old" / "ask-worktrees" / "KIT-0002"
        assert modern_wt.is_dir(), modern.stdout
        assert old_wt.is_dir(), old.stdout

    def test_helper_does_not_use_the_unportable_flag(self):
        """The guard that makes the fix stick."""
        offenders = [
            line.strip()
            for line in HELPER.read_text(encoding="utf-8").splitlines()
            if "--path-format" in line and not line.strip().startswith("#")
        ]
        assert offenders == [], (
            "--path-format=absolute needs git >= 2.31 and is silently wrong "
            f"on Apple git 2.30.1 (KIT-0080): {offenders}"
        )

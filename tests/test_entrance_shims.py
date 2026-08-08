"""Engine e2e + call-graph net for the kit entrances (KIT-0053 N1).

KIT-0053 pinned the historical flag surfaces of create-project.sh and
bootstrap.sh before turning them into shims over the one setup door.
KIT-0054 (0.9.0) removed the shims and the door's --legacy-shim
fidelity channel, so this module keeps only what outlives them: the
export/materials engine e2e coverage (re-pinned on door flags) and the
static call-graph direction (door -> engine, never the reverse).
TestOldEntrancesRemoved guards the removal itself — the historical
entrance paths must stay gone, so an old invocation hard-fails instead
of silently resurrecting a second door.

Consumer-rsync boundary: this module reads scripts/local/ content, so
it is excluded from the consumer tests/ rsync in the consumer engine
(exclude + rm -f sweep) and module-skips when the door is absent.
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DOOR = REPO_ROOT / "scripts" / "local" / "bootstrap"
ENGINES = (
    REPO_ROOT / "scripts" / "local" / "engine-consumer.sh",
    REPO_ROOT / "scripts" / "local" / "engine-materials.sh",
    REPO_ROOT / "scripts" / "local" / "engine-scaffold.sh",
)
REMOVED_ENTRANCES = (
    REPO_ROOT / "scripts" / "local" / "bootstrap-consumer.sh",
    REPO_ROOT / "scripts" / "local" / "bootstrap.sh",
    REPO_ROOT / "scripts" / "optional" / "create-project.sh",
    # KIT-0093 (ADR-0028 phase 2): the git-archive export engine died
    # with the door switch — --new scaffolds content, never copies.
    REPO_ROOT / "scripts" / "local" / "engine-export.sh",
)

if not DOOR.exists():
    pytest.skip(
        "setup door present only in the kit repo",
        allow_module_level=True,
    )

for tool in ("bash", "git", "rsync"):
    if shutil.which(tool) is None:
        pytest.skip(f"{tool} not available on PATH", allow_module_level=True)

# Nonexistent hermetic paths keep every door run hermetic (the
# test_setup_door pattern): the operator's real preset must never
# change door answers inside the suite.
_HERMETIC_XDG = REPO_ROOT / "tests" / ".no-such-xdg"
_HERMETIC_CONFIG = REPO_ROOT / "tests" / ".no-such-config-home"


def _scrubbed_env(**extra: str) -> dict[str, str]:
    """os.environ minus GIT_* (the KIT-0048 GIT_DIR leak class), plus
    hermetic config pins and overrides. Git identity for fresh-repo
    commits comes via XDG_CONFIG_HOME (see _git_identity), never
    GIT_AUTHOR_* vars — those are scrubbed with the rest."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["XDG_CONFIG_HOME"] = str(_HERMETIC_XDG)
    env["AGENTIVE_KIT_CONFIG_DIR"] = str(_HERMETIC_CONFIG)
    env.update(extra)
    return env


def _git_identity(tmp_path: Path) -> Path:
    """An XDG config dir carrying git user identity, for door runs that
    git-commit inside a fresh target (CI runners have no ~/.gitconfig)."""
    xdg = tmp_path / "xdg-config"
    (xdg / "git").mkdir(parents=True)
    (xdg / "git" / "config").write_text(
        "[user]\n\tname = Kit Test\n\temail = kit-test@example.invalid\n",
        encoding="utf-8",
    )
    return xdg


def run_door(
    *args: str, cwd: Path | None = None, env: dict | None = None
) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(DOOR), *args],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=cwd,
        env=env or _scrubbed_env(),
    )


class TestOldEntrancesRemoved:
    """KIT-0054: the historical entrances are gone — an old invocation
    fails loudly on a missing file, never via a silent fallback."""

    @pytest.mark.parametrize("entrance", REMOVED_ENTRANCES, ids=lambda p: p.name)
    def test_entrance_path_is_gone(self, entrance):
        assert not entrance.exists(), (
            f"{entrance} has reappeared — the 0.9.0 removal (KIT-0054) "
            "deleted the entrance shims; the setup door is the only entrance"
        )


class TestScaffoldE2E:
    """Scaffold-engine behavior through the door's --new path
    (KIT-0093: content + pins + record — nothing copied)."""

    @pytest.mark.slow
    def test_new_defaults(self, tmp_path):
        target = tmp_path / "widget"
        env = _scrubbed_env(XDG_CONFIG_HOME=str(_git_identity(tmp_path)))
        result = run_door("--new", str(target), env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        assert "Scaffold committed (branch: main)." in result.stdout

        # fresh git history: one scaffold commit, branch main
        log = subprocess.run(
            ["git", "-C", str(target), "log", "--oneline"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        assert len(log.stdout.strip().splitlines()) == 1
        branch = subprocess.run(
            ["git", "-C", str(target), "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        assert branch.stdout.strip() == "main"

        # born packaged: no kit identity files, no copied machinery
        assert not (target / "pyproject.toml").exists()
        assert not (target / "tests").exists()
        assert not (target / "scripts" / "core").exists()
        state = json.loads(
            (target / ".kit" / "context" / "current-state.json").read_text(
                encoding="utf-8"
            )
        )
        assert state["project"]["name"] == "widget"
        assert state["project"]["task_prefix"] == "WIDG"

        # no task specs, no planning corpus
        task_specs = [
            p
            for p in (target / ".kit" / "tasks").rglob("*.md")
            if p.name != "README.md"
        ]
        assert task_specs == []
        # scripts/local holds only the check hook — kit_markers.py
        # travels with the agentive-kit package now
        assert sorted(p.name for p in (target / "scripts" / "local").iterdir()) == [
            "checks.sh",
        ]
        # the adversarial config carries both pins (born on the kit's)
        config = (target / ".adversarial" / "config.yml").read_text(encoding="utf-8")
        assert "adversarial_cli_version:" in config
        assert "evaluator_library_version:" in config

    @pytest.mark.slow
    def test_new_name_prefix_flags(self, tmp_path):
        target = tmp_path / "proj"
        env = _scrubbed_env(XDG_CONFIG_HOME=str(_git_identity(tmp_path)))
        result = run_door(
            "--new",
            str(target),
            "--name",
            "My New Project",
            "--prefix",
            "MNP",
            env=env,
        )
        assert result.returncode == 0, result.stderr + result.stdout
        state = json.loads(
            (target / ".kit" / "context" / "current-state.json").read_text(
                encoding="utf-8"
            )
        )
        assert state["project"]["name"] == "My New Project"
        assert state["project"]["task_prefix"] == "MNP"


class TestMaterialsE2E:
    """Materials-engine behavior through the door's --design-materials
    path (formerly the bootstrap.sh e2e coverage)."""

    @pytest.mark.slow
    def test_materials_e2e_stubbed(self, tmp_path):
        """Full run with the two side-effecting tails stubbed out:
        setup-dev.sh is pre-seeded in the target (rsync --ignore-existing
        preserves it) and `claude` is PATH-shadowed to capture its argv
        instead of launching an interactive session."""
        target = tmp_path / "materials-proj"
        target.mkdir()
        (target / "design-brief.md").write_text("# The brief\n", encoding="utf-8")
        # pre-init so the engine skips git init/commit (timestamp-free)
        env = _scrubbed_env(XDG_CONFIG_HOME=str(_git_identity(tmp_path)))
        subprocess.run(
            ["git", "init", "--quiet", "-b", "main", str(target)],
            check=True,
            timeout=30,
            env=env,
        )

        setup_marker = tmp_path / "setup-dev-ran"
        stub_setup = target / "scripts" / "optional" / "setup-dev.sh"
        stub_setup.parent.mkdir(parents=True)
        stub_setup.write_text(
            f"#!/usr/bin/env bash\ntouch '{setup_marker}'\n", encoding="utf-8"
        )
        stub_setup.chmod(stub_setup.stat().st_mode | stat.S_IXUSR)

        claude_args = tmp_path / "claude-argv"
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        stub_claude = bin_dir / "claude"
        stub_claude.write_text(
            f'#!/usr/bin/env bash\nprintf \'%s\\n\' "$@" > "{claude_args}"\n',
            encoding="utf-8",
        )
        stub_claude.chmod(stub_claude.stat().st_mode | stat.S_IXUSR)
        env["PATH"] = f"{bin_dir}:{env['PATH']}"

        result = run_door("--adopt", str(target), "--design-materials", env=env)
        assert result.returncode == 0, result.stderr + result.stdout

        # scaffolding copied, materials preserved
        for expected in (
            ".claude/agents/bootstrap.md",
            ".kit/templates/TASK-STARTER-TEMPLATE.md",
            "scripts/core/project",
            "design-brief.md",
        ):
            assert (target / expected).exists(), f"missing: {expected}"
        # both tails reached, with the historical arguments
        assert setup_marker.exists(), "setup-dev.sh was not invoked"
        argv = claude_args.read_text(encoding="utf-8")
        assert "--agent" in argv
        assert str(target / ".claude" / "agents" / "bootstrap.md") in argv
        assert "design-brief.md" in argv  # the materials find fed the context


def _command_lines(text: str) -> list[str]:
    """Non-comment, non-blank lines — the executable surface. Keeps
    the graph assertions from passing on prose in header comments
    (CodeRabbit, PR #81)."""
    return [
        line
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


class TestCallGraph:
    """F3: the call graph is strictly door -> engine."""

    def test_door_calls_engines_not_old_entrances(self):
        commands = _command_lines(DOOR.read_text(encoding="utf-8"))
        for engine in ENGINES:
            assert any(
                engine.name in line for line in commands
            ), f"door must reference {engine.name} in a command position"
        for old_name in ("bootstrap-consumer.sh", "create-project.sh"):
            assert not any(
                old_name in line for line in commands
            ), f"door must never call removed entrance {old_name}"

    def test_engines_do_not_call_the_door(self):
        for engine in ENGINES:
            commands = _command_lines(engine.read_text(encoding="utf-8"))
            for needle in ('"$DOOR"', "scripts/local/bootstrap "):
                assert not any(
                    needle in line for line in commands
                ), f"{engine.name} must not re-enter the door ({needle!r})"

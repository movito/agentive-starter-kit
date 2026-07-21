"""Characterization net for the kit entrances (KIT-0053 N1).

Pins the historical flag surfaces of create-project.sh and bootstrap.sh
BEFORE they become shims over the one setup door (bootstrap-consumer.sh
is already pinned by tests/test_bootstrap_shapes.py, the KIT-0048
precedent). After the door lands, the same tests run through the
shim -> door -> engine chain, and TestCallGraph verifies that chain's
direction statically.

Byte-identity caveats (documented deviations, pinned as content
assertions instead):
- bootstrap.sh's missing-argument error comes from a bash ``${1:?}``
  expansion whose message embeds a line number; the line number is
  incidental and not pinned.

Consumer-rsync boundary: this module reads scripts/local/ content, so
it is excluded from the consumer tests/ rsync in the consumer engine
(exclude + rm -f sweep) and module-skips when the entrances are absent.
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
CREATE_PROJECT = REPO_ROOT / "scripts" / "optional" / "create-project.sh"
BOOTSTRAP_MATERIALS = REPO_ROOT / "scripts" / "local" / "bootstrap.sh"
DOOR = REPO_ROOT / "scripts" / "local" / "bootstrap"
ENGINES = (
    REPO_ROOT / "scripts" / "local" / "engine-consumer.sh",
    REPO_ROOT / "scripts" / "local" / "engine-materials.sh",
    REPO_ROOT / "scripts" / "local" / "engine-export.sh",
)

if not CREATE_PROJECT.exists() or not BOOTSTRAP_MATERIALS.exists():
    pytest.skip(
        "kit entrance scripts present only in the kit repo",
        allow_module_level=True,
    )

for tool in ("bash", "git", "rsync"):
    if shutil.which(tool) is None:
        pytest.skip(f"{tool} not available on PATH", allow_module_level=True)


def _scrubbed_env(**extra: str) -> dict[str, str]:
    """os.environ minus GIT_* (the KIT-0048 GIT_DIR leak class), plus
    overrides. Git identity for fresh-repo commits comes via
    XDG_CONFIG_HOME (see _git_identity), never GIT_AUTHOR_* vars —
    those are scrubbed with the rest."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(extra)
    return env


def _git_identity(tmp_path: Path) -> Path:
    """An XDG config dir carrying git user identity, for entrances that
    git-commit inside a fresh target (CI runners have no ~/.gitconfig)."""
    xdg = tmp_path / "xdg-config"
    (xdg / "git").mkdir(parents=True)
    (xdg / "git" / "config").write_text(
        "[user]\n\tname = Kit Test\n\temail = kit-test@example.invalid\n",
        encoding="utf-8",
    )
    return xdg


def run_entrance(
    script: Path, *args: str, cwd: Path | None = None, env: dict | None = None
) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(script), *args],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=cwd,
        env=env or _scrubbed_env(),
    )


class TestCreateProjectSurface:
    """Historical flag surface of scripts/optional/create-project.sh."""

    def test_help_text_pinned(self):
        result = run_entrance(CREATE_PROJECT, "--help")
        assert result.returncode == 0
        expected = (
            f"Usage: {CREATE_PROJECT} <target-dir> [--name NAME] [--prefix PREFIX]\n"
            "\n"
            "  <target-dir>     Where to create the new project (must not exist)\n"
            "  --name NAME      Project name (default: directory basename)\n"
            "  --prefix PREFIX  Task ID prefix, e.g. ID2 (default: derived from name)\n"
            "\n"
            "Example:\n"
            f"  {CREATE_PROJECT} ~/Github/my-new-project"
            " --name 'My New Project' --prefix MNP\n"
        )
        assert result.stdout == expected

    def test_missing_target_rejected(self):
        result = run_entrance(CREATE_PROJECT)
        assert result.returncode == 1
        assert "target directory is required" in result.stderr

    def test_existing_target_rejected(self, tmp_path):
        target = tmp_path / "already-there"
        target.mkdir()
        result = run_entrance(CREATE_PROJECT, str(target))
        assert result.returncode == 1
        assert "already exists" in result.stderr

    def test_unexpected_extra_argument_rejected(self, tmp_path):
        result = run_entrance(
            CREATE_PROJECT, str(tmp_path / "proj"), "surprise-positional"
        )
        assert result.returncode == 1
        assert "unexpected argument 'surprise-positional'" in result.stderr

    @pytest.mark.slow
    def test_export_e2e_defaults(self, tmp_path):
        target = tmp_path / "widget"
        env = _scrubbed_env(XDG_CONFIG_HOME=str(_git_identity(tmp_path)))
        result = run_entrance(CREATE_PROJECT, str(target), env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        assert "Project Created Successfully" in result.stdout

        # fresh git history: exactly one commit, branch main
        log = subprocess.run(
            ["git", "-C", str(target), "log", "--oneline"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        assert len(log.stdout.strip().splitlines()) == 1

        # identity reset — the target keeps the placeholder + TODO the
        # onboarding/bootstrap agents rewrite, never the kit's own name
        # (KIT-0057: the kit's pyproject is agentive-starter-kit now)
        pyproject = (target / "pyproject.toml").read_text(encoding="utf-8")
        assert 'version = "0.1.0"' in pyproject
        assert (
            'name = "your-project-name"  # TODO: Change this to your project name'
            in pyproject
        )
        assert 'name = "agentive-starter-kit"' not in pyproject
        state = json.loads(
            (target / ".kit" / "context" / "current-state.json").read_text(
                encoding="utf-8"
            )
        )
        assert state["project"]["name"] == "widget"
        assert state["project"]["task_prefix"] == "WIDG"

        # project-specific content stripped
        task_specs = [
            p
            for p in (target / ".kit" / "tasks").rglob("*.md")
            if p.name != "README.md" and "9-reference" not in p.parts
        ]
        assert task_specs == []
        assert sorted(p.name for p in (target / "tests").iterdir()) == ["__init__.py"]
        assert list((target / "scripts" / "local").iterdir()) == []
        assert "bootstrapped from agentive-starter-kit" in (
            target / "CHANGELOG.md"
        ).read_text(encoding="utf-8")

    @pytest.mark.slow
    def test_export_e2e_name_prefix_flags(self, tmp_path):
        target = tmp_path / "proj"
        env = _scrubbed_env(XDG_CONFIG_HOME=str(_git_identity(tmp_path)))
        result = run_entrance(
            CREATE_PROJECT,
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


class TestBootstrapMaterialsSurface:
    """Historical surface of scripts/local/bootstrap.sh (the
    adopt-with-design-materials entrance)."""

    def test_missing_target_usage(self):
        result = run_entrance(BOOTSTRAP_MATERIALS)
        assert result.returncode == 1
        assert "Usage:" in result.stderr
        assert "<target-directory>" in result.stderr

    def test_nonexistent_target_rejected(self, tmp_path):
        result = run_entrance(BOOTSTRAP_MATERIALS, str(tmp_path / "nope"))
        assert result.returncode == 1
        assert "Target directory does not exist" in result.stdout

    @pytest.mark.slow
    def test_materials_e2e_stubbed(self, tmp_path):
        """Full run with the two side-effecting tails stubbed out:
        setup-dev.sh is pre-seeded in the target (rsync --ignore-existing
        preserves it) and `claude` is PATH-shadowed to capture its argv
        instead of launching an interactive session."""
        target = tmp_path / "materials-proj"
        target.mkdir()
        (target / "design-brief.md").write_text("# The brief\n", encoding="utf-8")
        # pre-init so the entrance skips git init/commit (timestamp-free)
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

        result = run_entrance(BOOTSTRAP_MATERIALS, str(target), env=env)
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


@pytest.mark.skipif(not DOOR.exists(), reason="setup door not landed yet")
class TestCallGraph:
    """F3: the call graph is strictly shim -> door -> engine."""

    def test_shims_exec_the_door(self):
        consumer_shim = REPO_ROOT / "scripts" / "local" / "bootstrap-consumer.sh"
        for shim in (CREATE_PROJECT, BOOTSTRAP_MATERIALS, consumer_shim):
            commands = _command_lines(shim.read_text(encoding="utf-8"))
            assert any(
                'exec "$DOOR"' in line for line in commands
            ), f"{shim.name} must exec the door via its DOOR variable"
            assert any(
                "DOOR=" in line and "/bootstrap" in line for line in commands
            ), f"{shim.name} must resolve DOOR to scripts/local/bootstrap"
            for engine in ENGINES:
                assert not any(
                    engine.name in line for line in commands
                ), f"{shim.name} must not reach {engine.name} directly"

    def test_door_calls_engines_not_old_entrances(self):
        commands = _command_lines(DOOR.read_text(encoding="utf-8"))
        for engine in ENGINES:
            assert any(
                engine.name in line for line in commands
            ), f"door must reference {engine.name} in a command position"
        for old_name in ("bootstrap-consumer.sh", "create-project.sh"):
            assert not any(
                old_name in line for line in commands
            ), f"door must never call old entrance {old_name} (shim loop)"

    def test_engines_do_not_call_the_door(self):
        for engine in ENGINES:
            commands = _command_lines(engine.read_text(encoding="utf-8"))
            for needle in ('"$DOOR"', "scripts/local/bootstrap "):
                assert not any(
                    needle in line for line in commands
                ), f"{engine.name} must not re-enter the door ({needle!r})"

"""Shape tests for the bootstrap shim (KIT-0104 F3): through the shim
you get the PACKAGED door, byte-for-byte.

The characterization net this module used to carry pinned the legacy
copy-adopt world (toolchain rsync'd from the kit tree). That world
retired with the shim: ``bootstrap --adopt`` now reaches the packaged
adopt (content scaffold + record, nothing copied) and ``--no-kit`` is
KIT-ADR-0032's rung 0 (no ``.kit/``, no record) — both pinned here AS
the new contract. The equivalence tests are the load-bearing ones:
a shim run and a direct ``agentive`` run must produce identical trees,
so the shim can never grow behavior of its own.

Packaged-door behavior in depth (preset chain, record conflicts, .env
seeding, exit contract) is covered once, in
``tests/agentive_kit/test_door_units.py`` / ``test_door_e2e.py`` —
this module only proves the shim is a faithful window onto it.

Consumer-rsync boundary: this module reads scripts/local/ content, so
it is excluded from the consumer tests/ rsync in engine-consumer.sh
(exclude + rm -f sweep) and module-skips when the door is absent —
the tests/test_kit_markers.py pattern.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DOOR = REPO_ROOT / "scripts" / "local" / "bootstrap"
PKG_SRC = REPO_ROOT / "packages" / "agentive-kit" / "src"

if not DOOR.exists():
    pytest.skip(
        "setup door not present (consumer checkout)",
        allow_module_level=True,
    )

for tool in ("bash", "git", "rsync"):
    if shutil.which(tool) is None:
        pytest.skip(f"{tool} not available on PATH", allow_module_level=True)

# Nonexistent hermetic paths keep every door run hermetic (the
# test_setup_door pattern): the operator's REAL config home must never
# leak into the suite. XDG_CONFIG_HOME stays pinned too (git's own
# config lookup) — tests that commit swap in a scratch identity.
_HERMETIC_XDG = REPO_ROOT / "tests" / ".no-such-xdg"
_HERMETIC_CONFIG = REPO_ROOT / "tests" / ".no-such-config-home"


def _scrubbed_env(**extra: str) -> dict[str, str]:
    """os.environ minus GIT_* (the KIT-0048 GIT_DIR leak class), plus
    PYTHONPATH for the DIRECT package runs — the shim sets its own, but
    ``python -m agentive_kit.cli`` in a child interpreter does not
    inherit conftest's sys.path injection (the PR #129 CI lesson)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{PKG_SRC}{os.pathsep}{existing}" if existing else str(PKG_SRC)
    env["XDG_CONFIG_HOME"] = str(_HERMETIC_XDG)
    env["AGENTIVE_KIT_CONFIG_DIR"] = str(_HERMETIC_CONFIG)
    env.update(extra)
    return env


def _git_identity(base: Path) -> Path:
    xdg = base / "xdg-config"
    (xdg / "git").mkdir(parents=True, exist_ok=True)
    (xdg / "git" / "config").write_text(
        "[user]\n\tname = Kit Test\n\temail = kit-test@example.invalid\n",
        encoding="utf-8",
    )
    return xdg


def make_consumer_dir(base: Path, name: str) -> Path:
    """A scratch adopt target, pre-inited so the engine skips git init
    (keeps runs timestamp-free and tree-comparable)."""
    target = base / name
    target.mkdir(parents=True)
    subprocess.run(
        ["git", "init", "--quiet", "-b", "main", str(target)],
        check=True,
        timeout=30,
        env=_scrubbed_env(),
    )
    return target


def run_shim(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """The historical invocation, through the shim."""
    return subprocess.run(
        ["bash", str(DOOR), *args],
        capture_output=True,
        text=True,
        timeout=300,
        stdin=subprocess.DEVNULL,
        env=env or _scrubbed_env(),
    )


def run_direct(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """The packaged invocation, exactly as an installed CLI."""
    return subprocess.run(
        [sys.executable, "-m", "agentive_kit.cli", *args],
        capture_output=True,
        text=True,
        timeout=300,
        stdin=subprocess.DEVNULL,
        env=env or _scrubbed_env(),
    )


def tree_snapshot(root: Path) -> dict[str, str]:
    """path -> sha256 for every file under root, excluding .git/."""
    snapshot = {}
    for path in sorted(root.rglob("*")):
        if ".git" in path.parts:
            continue
        if path.is_file():
            rel = str(path.relative_to(root))
            snapshot[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snapshot


def _kit_install_region(target: Path) -> str:
    text = (target / "CLAUDE.md").read_text(encoding="utf-8")
    assert "<!-- BEGIN KIT-LOCAL: kit-install -->" in text
    return text.split("BEGIN KIT-LOCAL: kit-install")[1].split(
        "END KIT-LOCAL: kit-install"
    )[0]


@pytest.mark.slow
class TestShimEquivalence:
    """The AC proof: a shim run and a direct run are the same install.

    Identical basenames on purpose — the engines seed placeholders from
    the target name, so differing names would differ by design.
    """

    def test_new_via_shim_identical_to_direct(self, tmp_path):
        env = _scrubbed_env(XDG_CONFIG_HOME=str(_git_identity(tmp_path)))
        shim_target = tmp_path / "a" / "app"
        direct_target = tmp_path / "b" / "app"
        (tmp_path / "a").mkdir()
        (tmp_path / "b").mkdir()
        r1 = run_shim("--new", str(shim_target), env=env)
        r2 = run_direct("new", str(direct_target), env=env)
        assert r1.returncode == 0, r1.stderr + r1.stdout
        assert r2.returncode == 0, r2.stderr + r2.stdout
        assert tree_snapshot(shim_target) == tree_snapshot(direct_target)

    def test_adopt_via_shim_identical_to_direct(self, tmp_path):
        shim_target = make_consumer_dir(tmp_path / "a", "app")
        direct_target = make_consumer_dir(tmp_path / "b", "app")
        r1 = run_shim("--adopt", str(shim_target), "--profile", "none")
        r2 = run_direct("adopt", str(direct_target), "--profile", "none")
        assert r1.returncode == 0, r1.stderr + r1.stdout
        assert r2.returncode == 0, r2.stderr + r2.stdout
        assert tree_snapshot(shim_target) == tree_snapshot(direct_target)


@pytest.fixture(scope="module")
def adopted(tmp_path_factory):
    target = make_consumer_dir(tmp_path_factory.mktemp("shim-adopt"), "app")
    result = run_shim("--adopt", str(target))
    assert result.returncode == 0, result.stderr + result.stdout
    return target, result


@pytest.mark.slow
class TestPackagedAdoptThroughShim:
    """The copy-adopt retirement, pinned: adopt through the shim is the
    PACKAGED adopt — record + content scaffold, nothing copied."""

    def test_record_and_hook_written(self, adopted):
        target, result = adopted
        region = _kit_install_region(target)
        assert "shape: single" in region
        assert "profile: python" in region
        hook = target / "scripts" / "local" / "checks.sh"
        assert hook.is_file()
        assert os.access(hook, os.X_OK)

    def test_kit_workflow_scaffolded_not_copied(self, adopted):
        target, result = adopted
        assert (target / ".kit" / "tasks" / "1-backlog").is_dir()
        # the legacy copy-adopt shipset must be GONE: no toolchain
        # copies, no script copies, no agent copies
        for never in (
            "pyproject.toml",
            "conftest.py",
            "tests",
            "scripts/core",
            ".claude",
            "scripts/local/kit_markers.py",
            ".github",
        ):
            assert not (target / never).exists(), f"copy-adopt relic: {never}"

    def test_doctor_tail_reported(self, adopted):
        target, result = adopted
        assert "Doctor verdict:" in result.stdout
        assert "Install complete:" in result.stdout


@pytest.mark.slow
class TestPlanningShapeThroughShim:
    def test_planning_records_pointer_and_forces_none(self, tmp_path):
        target = make_consumer_dir(tmp_path, "coord")
        result = run_shim(
            "--adopt",
            str(target),
            "--shape",
            "planning",
            "--target-path",
            "../my-product",
            "--target-github",
            "acme/my-product",
        )
        assert result.returncode == 0, result.stderr + result.stdout
        region = _kit_install_region(target)
        assert "shape: planning" in region
        assert "profile: none" in region
        assert "target_path: ../my-product" in region
        assert "target_github: acme/my-product" in region
        text = (target / "CLAUDE.md").read_text(encoding="utf-8")
        assert "## Target Repository" in text
        # planning ships no python toolchain
        assert not (target / "pyproject.toml").exists()

    def test_equals_form_flags_translate(self, tmp_path):
        target = make_consumer_dir(tmp_path, "eqform")
        result = run_shim(f"--adopt={target}", "--shape=planning", "--profile=none")
        assert result.returncode == 0, result.stderr + result.stdout
        region = _kit_install_region(target)
        assert "shape: planning" in region
        assert "profile: none" in region


@pytest.mark.slow
class TestRungZeroThroughShim:
    """--no-kit is rung 0 now (KIT-ADR-0032, both verbs): no .kit/, no
    record — the legacy seeded-record --no-kit retired with the shim."""

    def test_adopt_no_kit_is_rung_zero(self, tmp_path):
        target = make_consumer_dir(tmp_path, "proto")
        (target / "main.py").write_text("print('hi')\n", encoding="utf-8")
        result = run_shim("--adopt", str(target), "--no-kit")
        assert result.returncode == 0, result.stderr + result.stdout
        assert "rung 0" in result.stdout.lower()
        assert (target / "scripts" / "local" / "checks.sh").is_file()
        assert not (target / ".kit").exists()
        assert not (target / "CLAUDE.md").exists()
        assert not (target / "scripts" / "core").exists()
        assert "Doctor verdict:" not in result.stdout  # nothing to check

    def test_new_no_kit_is_rung_zero(self, tmp_path):
        """KIT-0104 F4 through the historical entrance."""
        env = _scrubbed_env(XDG_CONFIG_HOME=str(_git_identity(tmp_path)))
        target = tmp_path / "blank"
        result = run_shim("--new", str(target), "--no-kit", env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        assert "rung 0" in result.stdout.lower()
        assert (target / "scripts" / "local" / "checks.sh").is_file()
        assert not (target / ".kit").exists()
        assert not (target / "CLAUDE.md").exists()
        branch = subprocess.run(
            ["git", "-C", str(target), "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        assert branch.stdout.strip() == "main"


class TestExitContractPassThrough:
    """The package's 0/1/2 contract survives the exec unchanged."""

    def test_unknown_shape_exits_2(self, tmp_path):
        target = make_consumer_dir(tmp_path, "bad")
        result = run_shim("--adopt", str(target), "--shape", "pyramid")
        assert result.returncode == 2
        assert "unknown shape" in (result.stdout + result.stderr).lower()

    def test_unknown_profile_exits_2(self, tmp_path):
        target = make_consumer_dir(tmp_path, "badprof")
        result = run_shim("--adopt", str(target), "--profile", "elixir")
        assert result.returncode == 2
        assert "unknown profile" in (result.stdout + result.stderr).lower()

    def test_illegal_pair_exits_2_naming_pairs(self, tmp_path):
        target = make_consumer_dir(tmp_path, "badcombo")
        result = run_shim(
            "--adopt", str(target), "--shape", "planning", "--profile", "python"
        )
        assert result.returncode == 2
        assert "illegal shape/profile combination" in result.stderr
        for pair in ("single+python", "single+none", "planning+none"):
            assert pair in result.stderr

    def test_malformed_target_github_rejected(self, tmp_path):
        target = make_consumer_dir(tmp_path, "badgh")
        result = run_shim(
            "--adopt",
            str(target),
            "--shape",
            "planning",
            "--target-github",
            "not a repo slug",
        )
        assert result.returncode == 2
        assert "owner/repo" in result.stdout + result.stderr

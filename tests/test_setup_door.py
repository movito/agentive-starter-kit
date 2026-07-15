"""Tests for scripts/local/bootstrap — the one setup door (KIT-0053).

Three layers:
- resolve/validate units run against the SOURCED door (no filesystem
  side effects) — the F1 internal-decomposition contract;
- the exit contract (F6): 0 install-ok / 1 install-failed / 2
  usage-or-illegal, with illegal combos naming the legal pairs (F2);
- scratch e2e per matrix cell x mode, each asserting the doctor tail
  (P4) and the recorded shape/profile pair.

Non-TTY discipline (N4): every subprocess here runs with stdin closed,
so any prompt that leaked past the flag layer would hang and trip the
timeout instead of silently passing.

Consumer-rsync boundary: this module reads scripts/local/ content, so
it is excluded from the consumer tests/ rsync in engine-consumer.sh
(exclude + rm -f sweep) and module-skips when the door is absent.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DOOR = REPO_ROOT / "scripts" / "local" / "bootstrap"

if not DOOR.exists():
    pytest.skip(
        "setup door present only in the kit repo",
        allow_module_level=True,
    )

for tool in ("bash", "git", "rsync"):
    if shutil.which(tool) is None:
        pytest.skip(f"{tool} not available on PATH", allow_module_level=True)


def _scrubbed_env(**extra: str) -> dict[str, str]:
    """os.environ minus GIT_* (the KIT-0048 GIT_DIR leak class)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(extra)
    return env


def _git_identity(tmp_path: Path) -> Path:
    xdg = tmp_path / "xdg-config"
    (xdg / "git").mkdir(parents=True)
    (xdg / "git" / "config").write_text(
        "[user]\n\tname = Kit Test\n\temail = kit-test@example.invalid\n",
        encoding="utf-8",
    )
    return xdg


def make_adopt_dir(base: Path, name: str) -> Path:
    """A scratch adopt target, pre-inited so the engine skips git init."""
    target = base / name
    target.mkdir(parents=True)
    subprocess.run(
        ["git", "init", "--quiet", "-b", "main", str(target)],
        check=True,
        timeout=30,
        env=_scrubbed_env(),
    )
    return target


def run_door(
    *args: str, env: dict | None = None, timeout: int = 300
) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(DOOR), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        stdin=subprocess.DEVNULL,  # never a TTY — prompts must be unreachable
        env=env or _scrubbed_env(),
    )


def sourced(snippet: str) -> subprocess.CompletedProcess:
    """Run a snippet with the door's functions loaded (no main)."""
    return subprocess.run(
        ["bash", "-c", f'source "{DOOR}"; {snippet}'],
        capture_output=True,
        text=True,
        timeout=30,
        stdin=subprocess.DEVNULL,
        env=_scrubbed_env(),
    )


class TestResolveValidateUnits:
    """The sourced resolve/validate layer — no filesystem effects."""

    @pytest.mark.parametrize(
        "shape,profile",
        [("single", "python"), ("single", "none"), ("planning", "none")],
    )
    def test_matrix_legal_cells(self, shape, profile):
        result = sourced(f"validate_pair {shape} {profile}")
        assert result.returncode == 0, result.stderr

    def test_matrix_illegal_cell_names_legal_pairs(self):
        result = sourced("validate_pair planning python")
        assert result.returncode == 1
        assert "illegal shape/profile combination" in result.stderr
        for pair in ("single+python", "single+none", "planning+none"):
            assert pair in result.stderr, f"rejection must name {pair}"

    def test_kit_default_shape_is_single(self):
        result = sourced('resolve_setting shape ""')
        assert result.returncode == 0
        assert result.stdout.strip() == "single"

    @pytest.mark.parametrize(
        "shape,expected", [("single", "python"), ("planning", "none")]
    )
    def test_kit_default_profile_follows_shape(self, shape, expected):
        result = sourced(f'resolve_setting profile "" {shape}')
        assert result.returncode == 0
        assert result.stdout.strip() == expected

    def test_cli_value_wins_over_default(self):
        result = sourced("resolve_setting profile none single")
        assert result.stdout.strip() == "none"

    def test_preset_layer_is_a_stub(self):
        # P7 seam: the reserved preset layer answers nothing today.
        # (Guarded call: the sourced door sets -e, so a bare failing
        # preset_get would exit the test shell before the echo.)
        result = sourced('preset_get shape || echo "rc=$?"')
        assert result.stdout.strip() == "rc=1"  # answers nothing, prints nothing

    def test_unknown_values_rejected(self):
        assert sourced('validate_values pyramid ""').returncode == 1
        assert sourced("validate_values single elixir").returncode == 1

    def test_empty_preset_answer_falls_through(self):
        # o3 finding: a P7 preset that succeeds but echoes nothing must
        # count as unanswered — the chain falls through to kit defaults
        result = sourced('preset_get() { echo ""; }; resolve_setting shape ""')
        assert result.returncode == 0
        assert result.stdout.strip() == "single"


class TestExitContract:
    """F6: 0 install-ok / 1 install-failed / 2 usage-or-illegal."""

    def test_help_exits_zero(self):
        result = run_door("--help")
        assert result.returncode == 0
        assert "the one setup door" in result.stdout
        assert "--new" in result.stdout and "--adopt" in result.stdout
        assert "Exit contract" in result.stdout

    def test_unknown_flag_is_usage(self):
        assert run_door("--frobnicate").returncode == 2

    def test_missing_mode_non_tty_fails_fast(self):
        result = run_door(timeout=30)
        assert result.returncode == 2
        assert "mode is required" in result.stderr

    def test_missing_target_non_tty_fails_fast(self, tmp_path):
        result = run_door("--adopt", timeout=30)
        assert result.returncode == 2
        assert "target directory is required" in result.stderr

    def test_illegal_pair_exits_2_naming_pairs(self, tmp_path):
        result = run_door(
            "--adopt", str(tmp_path), "--shape", "planning", "--profile", "python"
        )
        assert result.returncode == 2
        for pair in ("single+python", "single+none", "planning+none"):
            assert pair in result.stderr

    def test_unknown_shape_exits_2(self, tmp_path):
        assert run_door("--adopt", str(tmp_path), "--shape", "cube").returncode == 2

    def test_unknown_profile_exits_2(self, tmp_path):
        result = run_door("--adopt", str(tmp_path), "--profile", "elixir")
        assert result.returncode == 2

    def test_venv_offer_needs_python_profile(self, tmp_path):
        result = run_door("--adopt", str(tmp_path), "--profile", "none", "--with-venv")
        assert result.returncode == 2
        assert "--with-venv requires profile python" in result.stderr

    def test_name_prefix_are_new_only(self, tmp_path):
        result = run_door("--adopt", str(tmp_path), "--name", "X")
        assert result.returncode == 2

    def test_target_pointer_is_planning_only(self, tmp_path):
        result = run_door("--adopt", str(tmp_path), "--target-path", "../x")
        assert result.returncode == 2

    def test_no_kit_planning_contradiction(self, tmp_path):
        result = run_door("--adopt", str(tmp_path), "--shape", "planning", "--no-kit")
        assert result.returncode == 2

    def test_new_target_must_not_exist(self, tmp_path):
        result = run_door("--new", str(tmp_path))
        assert result.returncode == 2
        assert "already exists" in result.stderr

    def test_adopt_target_must_exist(self, tmp_path):
        result = run_door("--adopt", str(tmp_path / "nope"))
        assert result.returncode == 2
        assert "does not exist" in result.stderr

    def test_adopting_the_kit_itself_refused(self):
        result = run_door("--adopt", str(REPO_ROOT))
        assert result.returncode == 2
        assert "kit source repo" in result.stderr

    def test_missing_git_identity_fails_fast_with_guidance(self, tmp_path):
        # o3 finding: without an identity the export engine would die
        # mid-run with git's own cryptic error — the door pre-checks
        system_cfg = subprocess.run(
            ["git", "config", "--system", "--get", "user.email"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if system_cfg.returncode == 0:
            pytest.skip("system gitconfig carries an identity on this machine")
        home = tmp_path / "bare-home"
        home.mkdir()
        env = _scrubbed_env(HOME=str(home), XDG_CONFIG_HOME=str(home / "xdg"))
        result = run_door("--new", str(tmp_path / "proj"), env=env)
        assert result.returncode == 1
        assert "no git identity configured" in result.stderr
        assert not (tmp_path / "proj").exists()  # failed BEFORE any work


def _kit_install_region(target: Path) -> str:
    text = (target / "CLAUDE.md").read_text(encoding="utf-8")
    assert "<!-- BEGIN KIT-LOCAL: kit-install -->" in text
    return text.split("BEGIN KIT-LOCAL: kit-install")[1].split(
        "END KIT-LOCAL: kit-install"
    )[0]


def _assert_doctor_tail(stdout: str) -> None:
    assert "project doctor" in stdout
    assert "DOCTOR:" in stdout, "doctor checks must have run"
    assert "Doctor verdict:" in stdout
    assert "Install complete:" in stdout


@pytest.mark.slow
class TestAdoptE2E:
    def test_adopt_single_defaults(self, tmp_path):
        target = make_adopt_dir(tmp_path, "app")
        result = run_door("--adopt", str(target))
        assert result.returncode == 0, result.stderr + result.stdout
        assert "Setup door: mode=adopt shape=single profile=python" in result.stdout
        # offers skipped with notice in non-TTY (N4)
        assert "Offer skipped (non-interactive): evaluators" in result.stdout
        assert "Offer skipped (non-interactive): venv" in result.stdout
        _assert_doctor_tail(result.stdout)
        region = _kit_install_region(target)
        assert "shape: single" in region
        assert "profile: python" in region
        assert (target / "scripts" / "local" / "checks.sh").is_file()

    def test_adopt_planning_records_pointer(self, tmp_path):
        target = make_adopt_dir(tmp_path, "coord")
        result = run_door(
            "--adopt",
            str(target),
            "--shape",
            "planning",
            "--target-path",
            "../product",
            "--target-github",
            "acme/product",
        )
        assert result.returncode == 0, result.stderr + result.stdout
        assert "planning shape → profile none (forced" in result.stdout
        # no venv offer for a toolchain-free shape
        assert "Offer skipped (non-interactive): venv" not in result.stdout
        _assert_doctor_tail(result.stdout)
        region = _kit_install_region(target)
        assert "shape: planning" in region
        assert "profile: none" in region
        assert "target_path: ../product" in region

    def test_adopt_gitless_target_hints_materials(self, tmp_path):
        env = _scrubbed_env(XDG_CONFIG_HOME=str(_git_identity(tmp_path)))
        target = tmp_path / "materials"
        target.mkdir()
        (target / "brief.md").write_text("# brief\n", encoding="utf-8")
        result = run_door("--adopt", str(target), env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        assert "--design-materials" in result.stdout  # the detection hint
        _assert_doctor_tail(result.stdout)

    def test_adopt_git_target_no_materials_hint(self, tmp_path):
        target = make_adopt_dir(tmp_path, "app")
        result = run_door("--adopt", str(target))
        assert "re-run with --design-materials" not in result.stdout

    def test_legacy_shim_channel_is_chrome_free(self, tmp_path):
        """--legacy-shim: engine output only — no door banner, no offers,
        no doctor tail (byte-fidelity for the three entrance shims)."""
        target = make_adopt_dir(tmp_path, "app")
        result = run_door("--adopt", str(target), "--legacy-shim")
        assert result.returncode == 0, result.stderr + result.stdout
        assert "Setup door:" not in result.stdout
        assert "Doctor verdict:" not in result.stdout
        assert "Offer skipped" not in result.stdout


@pytest.mark.slow
class TestNewE2E:
    def test_new_single_exports_and_records(self, tmp_path):
        env = _scrubbed_env(XDG_CONFIG_HOME=str(_git_identity(tmp_path)))
        target = tmp_path / "fresh-app"
        result = run_door("--new", str(target), env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        assert "Project Created Successfully" in result.stdout  # export engine
        assert "Install record committed." in result.stdout
        _assert_doctor_tail(result.stdout)
        region = _kit_install_region(target)
        assert "shape: single" in region
        assert "profile: python" in region
        assert (target / "scripts" / "local" / "checks.sh").is_file()
        assert (target / "scripts" / "local" / "kit_markers.py").is_file()
        # export commit + record commit, nothing dangling
        log = subprocess.run(
            ["git", "-C", str(target), "log", "--oneline"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        assert len(log.stdout.strip().splitlines()) == 2
        status = subprocess.run(
            ["git", "-C", str(target), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        assert status.stdout.strip() == ""

    def test_new_single_profile_none_reseeds_rules(self, tmp_path):
        """BugBot PR #81: the export carries the kit's python Project
        Rules region; a profile-none install must reseed it to the
        none content, never record none next to python guidance."""
        env = _scrubbed_env(XDG_CONFIG_HOME=str(_git_identity(tmp_path)))
        target = tmp_path / "docs-app"
        result = run_door("--new", str(target), "--profile", "none", env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        region = _kit_install_region(target)
        assert "profile: none" in region
        text = (target / "CLAUDE.md").read_text(encoding="utf-8")
        rules = text.split("BEGIN KIT-LOCAL: project-rules")[1].split(
            "END KIT-LOCAL: project-rules"
        )[0]
        assert "No project toolchain is configured" in rules
        assert "### Python" not in rules
        assert text.count("BEGIN KIT-LOCAL: project-rules") == 1
        # the none check hook seeded alongside (byte-identical to template)
        none_seed = REPO_ROOT / "scripts" / "local" / "templates" / "checks-none.sh"
        hook = target / "scripts" / "local" / "checks.sh"
        assert hook.read_bytes() == none_seed.read_bytes()

    def test_new_planning_scaffolds_and_records(self, tmp_path):
        env = _scrubbed_env(XDG_CONFIG_HOME=str(_git_identity(tmp_path)))
        target = tmp_path / "fresh-planning"
        result = run_door(
            "--new",
            str(target),
            "--shape",
            "planning",
            "--target-path",
            "../product",
            env=env,
        )
        assert result.returncode == 0, result.stderr + result.stdout
        _assert_doctor_tail(result.stdout)
        assert (target / "scripts" / "core" / "project").is_file()
        assert not (target / "pyproject.toml").exists()  # never-ship contract
        region = _kit_install_region(target)
        assert "shape: planning" in region
        assert "profile: none" in region

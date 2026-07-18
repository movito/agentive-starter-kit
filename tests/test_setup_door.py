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


# A nonexistent XDG_CONFIG_HOME keeps every door run hermetic: the
# operator's REAL ~/.config/agentive-kit/preset (KIT-0056) must never
# leak into the suite — a filled preset would change door answers and
# break characterization. Tests that need a preset pass their own
# XDG_CONFIG_HOME via extra (override wins).
_HERMETIC_XDG = REPO_ROOT / "tests" / ".no-such-xdg"


def _scrubbed_env(**extra: str) -> dict[str, str]:
    """os.environ minus GIT_* (the KIT-0048 GIT_DIR leak class)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["XDG_CONFIG_HOME"] = str(_HERMETIC_XDG)
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


def sourced(snippet: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run a snippet with the door's functions loaded (no main)."""
    return subprocess.run(
        ["bash", "-c", f'source "{DOOR}"; {snippet}'],
        capture_output=True,
        text=True,
        timeout=30,
        stdin=subprocess.DEVNULL,
        env=env or _scrubbed_env(),
    )


def write_preset(base: Path, content: str) -> Path:
    """A preset under a scratch XDG_CONFIG_HOME; returns the XDG dir."""
    xdg = base / "xdg-preset"
    (xdg / "agentive-kit").mkdir(parents=True, exist_ok=True)
    (xdg / "agentive-kit" / "preset").write_text(content, encoding="utf-8")
    return xdg


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

    def test_preset_layer_unloaded_answers_nothing(self):
        # No preset loaded (or --no-preset): the layer answers nothing —
        # the machine behaves exactly like a preset-less machine (N1).
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


class TestPresetUnits:
    """KIT-0056 F5: the preset layer inside the ONE resolve chain —
    CLI > preset > kit default (record short-circuits preset on adopt).
    All sourced; the preset file lives under a scratch XDG dir, never
    the real ~/.config."""

    def _env(self, tmp_path, content):
        return _scrubbed_env(XDG_CONFIG_HOME=str(write_preset(tmp_path, content)))

    def test_preset_beats_kit_default(self, tmp_path):
        env = self._env(tmp_path, "shape: planning\n")
        result = sourced('load_preset; resolve_setting shape ""', env=env)
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "planning"

    def test_cli_beats_preset(self, tmp_path):
        env = self._env(tmp_path, "shape: planning\n")
        result = sourced("load_preset; resolve_setting shape single", env=env)
        assert result.stdout.strip() == "single"

    def test_record_short_circuits_preset(self, tmp_path):
        # Adopt of a recorded target: the question is not open, so the
        # preset is not consulted — the chain falls to the kit default
        # exactly as on a preset-less machine (record wins; divergence
        # is doctor --against-preset's INFO surface).
        env = self._env(tmp_path, "profile: none\n")
        result = sourced(
            'load_preset; REC_PROFILE=none; resolve_setting profile "" single',
            env=env,
        )
        assert result.stdout.strip() == "python"  # kit default, not the preset

    def test_no_preset_flag_disables_the_layer(self, tmp_path):
        env = self._env(tmp_path, "shape: planning\n")
        result = sourced('NO_PRESET=1; load_preset; resolve_setting shape ""', env=env)
        assert result.stdout.strip() == "single"

    def test_unknown_key_warns_and_skips_never_errors(self, tmp_path):
        env = self._env(tmp_path, "coffee: espresso\nshape: planning\n")
        result = sourced('load_preset; resolve_setting shape ""', env=env)
        assert result.returncode == 0, result.stderr
        assert "unknown preset key 'coffee'" in result.stderr
        assert "line 1" in result.stderr
        # known keys after the unknown one still load (skip, not abort)
        assert result.stdout.strip() == "planning"

    def test_malformed_line_fails_loud_naming_the_line(self, tmp_path):
        env = self._env(tmp_path, "shape: single\nprofile python\n")
        result = sourced("load_preset", env=env)
        assert result.returncode == 2
        assert "malformed preset line 2" in result.stderr
        assert "profile python" in result.stderr

    def test_duplicate_key_fails_loud(self, tmp_path):
        env = self._env(tmp_path, "shape: single\nshape: planning\n")
        result = sourced("load_preset", env=env)
        assert result.returncode == 2
        assert "duplicate preset key 'shape'" in result.stderr

    def test_empty_value_falls_through(self, tmp_path):
        # an empty answer is unanswered, never a resolve to ""
        env = self._env(tmp_path, "shape:\n")
        result = sourced('load_preset; resolve_setting shape ""', env=env)
        assert result.returncode == 0
        assert result.stdout.strip() == "single"

    def test_comments_and_blanks_ignored(self, tmp_path):
        env = self._env(tmp_path, "# a comment\n\nshape: planning\n")
        result = sourced('load_preset; resolve_setting shape ""', env=env)
        assert result.stdout.strip() == "planning"

    def test_env_not_gitignored_refuses_secret_copy(self, tmp_path):
        # F6's hard guard, exercised directly: a target whose .env is
        # NOT gitignored must refuse the copy outright — no .env file,
        # exit 1, and the reason named
        target = make_adopt_dir(tmp_path, "no-ignore")  # no .gitignore at all
        src = tmp_path / "env-template"
        src.write_text("KEY=secret-fixture\n", encoding="utf-8")
        src.chmod(0o600)
        result = sourced(f'TARGET="{target}"; apply_env_source "{src}"')
        assert result.returncode == 1
        assert "refusing to seed secrets" in result.stderr
        assert not (target / ".env").exists()


class TestNormalizeBots:
    """KIT-0056 F1: 'none' alone, or a subset of coderabbit/bugbot —
    normalized to canonical order, comma- or space-separated input."""

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("coderabbit bugbot", "coderabbit bugbot"),
            ("bugbot coderabbit", "coderabbit bugbot"),
            ("bugbot,coderabbit", "coderabbit bugbot"),
            ("CodeRabbit,BUGBOT", "coderabbit bugbot"),  # case-insensitive
            ("coderabbit", "coderabbit"),
            ("bugbot", "bugbot"),
            ("coderabbit coderabbit", "coderabbit"),  # duplicates collapse
            ("bugbot,bugbot coderabbit", "coderabbit bugbot"),
            ("none", "none"),
            ("None", "none"),
        ],
    )
    def test_canonical_forms(self, raw, expected):
        result = sourced(f'normalize_bots "{raw}"')
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == expected

    def test_unknown_bot_rejected(self):
        result = sourced('normalize_bots horsebot || echo "rc=$?"')
        assert "unknown bot 'horsebot'" in result.stderr
        assert result.stdout.strip() == "rc=1"

    def test_none_combined_rejected(self):
        result = sourced('normalize_bots "none bugbot" || echo "rc=$?"')
        assert "'none' cannot be combined" in result.stderr
        assert result.stdout.strip() == "rc=1"

    def test_empty_input_is_unanswered_not_error(self):
        # rc 1 with NO error text: empty means "question still open"
        # (the caller prompts or writes nothing), never a rejection
        result = sourced('normalize_bots "" || echo "rc=$?"')
        assert result.stdout.strip() == "rc=1"
        assert result.stderr == ""


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

    def test_mode_flag_must_not_swallow_following_flag(self):
        # BugBot PR #81: '--new --shape planning' must not adopt
        # '--shape' as the target directory
        result = run_door("--new", "--shape", "planning", timeout=30)
        assert result.returncode == 2
        assert "requires a value" in result.stderr
        result = run_door("--adopt", "--profile", "none", timeout=30)
        assert result.returncode == 2
        assert "requires a value" in result.stderr
        # short options are flags too, not targets
        result = run_door("--new", "-h", timeout=30)
        assert result.returncode == 2
        assert "requires a value" in result.stderr

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

    def test_no_kit_materials_contradiction(self, tmp_path):
        # BugBot PR #81: the materials engine installs the full kit
        # workflow — --no-kit cannot be honored there and must be
        # rejected loudly, never silently dropped
        result = run_door("--adopt", str(tmp_path), "--design-materials", "--no-kit")
        assert result.returncode == 2
        assert "--no-kit contradicts --design-materials" in result.stderr

    def test_no_kit_planning_contradiction(self, tmp_path):
        result = run_door("--adopt", str(tmp_path), "--shape", "planning", "--no-kit")
        assert result.returncode == 2

    def test_invalid_bots_flag_exits_2(self, tmp_path):
        result = run_door("--adopt", str(tmp_path), "--bots", "horsebot")
        assert result.returncode == 2
        assert "unknown bot 'horsebot'" in result.stderr

    def test_bots_none_combined_exits_2(self, tmp_path):
        result = run_door("--adopt", str(tmp_path), "--bots", "none coderabbit")
        assert result.returncode == 2
        assert "'none' cannot be combined" in result.stderr

    def test_malformed_preset_exits_2_before_any_work(self, tmp_path):
        xdg = write_preset(tmp_path, "this is not a preset\n")
        env = _scrubbed_env(XDG_CONFIG_HOME=str(xdg))
        result = run_door("--new", str(tmp_path / "proj"), env=env, timeout=30)
        assert result.returncode == 2
        assert "malformed preset line 1" in result.stderr
        assert not (tmp_path / "proj").exists()

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
        for key in ("user.email", "user.name"):
            system_cfg = subprocess.run(
                ["git", "config", "--system", "--get", key],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if system_cfg.returncode == 0:
                pytest.skip(f"system gitconfig carries {key} on this machine")
        home = tmp_path / "bare-home"
        home.mkdir()
        env = _scrubbed_env(HOME=str(home), XDG_CONFIG_HOME=str(home / "xdg"))
        result = run_door("--new", str(tmp_path / "proj"), env=env)
        assert result.returncode == 1
        assert "git identity incomplete" in result.stderr
        assert not (tmp_path / "proj").exists()  # failed BEFORE any work

        # email alone is not an identity — commits need name AND email
        # (BugBot PR #81)
        xdg = home / "xdg"
        (xdg / "git").mkdir(parents=True)
        (xdg / "git" / "config").write_text(
            "[user]\n\temail = only-email@example.invalid\n", encoding="utf-8"
        )
        result = run_door("--new", str(tmp_path / "proj"), env=env)
        assert result.returncode == 1
        assert "user.name unset" in result.stderr


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

    def test_adopt_single_profile_none(self, tmp_path):
        """The single:none matrix cell, adopt mode (CodeRabbit PR #81).
        The profile scopes the check hook + record ONLY — the shipset
        is the shape's job (ADR-0027 P1 / KIT-0050 contract), so the
        toolchain still ships for a single-shape install."""
        target = make_adopt_dir(tmp_path, "docsrepo")
        result = run_door("--adopt", str(target), "--profile", "none")
        assert result.returncode == 0, result.stderr + result.stdout
        assert "Setup door: mode=adopt shape=single profile=none" in result.stdout
        # no venv offer for a toolchain-free profile
        assert "Offer skipped (non-interactive): venv" not in result.stdout
        _assert_doctor_tail(result.stdout)
        region = _kit_install_region(target)
        assert "shape: single" in region
        assert "profile: none" in region
        none_seed = REPO_ROOT / "scripts" / "local" / "templates" / "checks-none.sh"
        hook = target / "scripts" / "local" / "checks.sh"
        assert hook.read_bytes() == none_seed.read_bytes()
        # shipset unchanged by profile: single shape ships the toolchain
        assert (target / "pyproject.toml").is_file()

    def test_readopt_with_conflicting_profile_rejected(self, tmp_path):
        """CodeRabbit PR #81: explicit flags that contradict the
        target's existing kit-install record are an error, never a
        silent preserve (the PR #78 target-pointer precedent)."""
        target = make_adopt_dir(tmp_path, "docsrepo")
        assert run_door("--adopt", str(target), "--profile", "none").returncode == 0
        result = run_door("--adopt", str(target), "--profile", "python")
        assert result.returncode == 2
        assert "conflicts with the target's existing kit-install record" in (
            result.stderr
        )
        # flagless re-adopt keeps working (nothing explicit to conflict)
        # AND preserves the existing record — the default must not
        # silently overwrite single:none with single:python
        readopt = run_door("--adopt", str(target))
        assert readopt.returncode == 0, readopt.stderr + readopt.stdout
        assert "profile: none" in _kit_install_region(target)

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


SECRET = "KIT0056-FIXTURE-SECRET-NEVER-PRINT"


def _demo_preset_xdg(tmp_path: Path) -> Path:
    """A FULL preset (every door question answered) plus git identity
    and a 0600 env template carrying a fixture secret."""
    xdg = _git_identity(tmp_path)  # xdg-config/ with git/config
    env_template = tmp_path / "env-template"
    env_template.write_text(f"OPENAI_API_KEY={SECRET}\n", encoding="utf-8")
    env_template.chmod(0o600)
    (xdg / "agentive-kit").mkdir()
    (xdg / "agentive-kit" / "preset").write_text(
        "# full operator preset (KIT-0056 N4 fixture)\n"
        "shape: single\n"
        "profile: python\n"
        "bots: coderabbit bugbot\n"
        "evaluators: no\n"
        "venv: no\n"
        f"env-source: {env_template}\n",
        encoding="utf-8",
    )
    return xdg


@pytest.mark.slow
class TestPresetE2E:
    """KIT-0056 P7 end to end. Preset fixtures live under scratch XDG
    dirs — the suite never reads or writes the real ~/.config (N-rule
    in the task spec)."""

    def test_one_button_demo(self, tmp_path):
        """N4, the acceptance bar: a full preset answers every question
        — zero prompts, zero skipped-offer notices — and the resulting
        record reflects the preset's declarations. Secrets arrive by
        reference at mode 0600 and never appear in output or git."""
        xdg = _demo_preset_xdg(tmp_path)
        preset_file = xdg / "agentive-kit" / "preset"
        preset_before = preset_file.read_bytes()
        env = _scrubbed_env(XDG_CONFIG_HOME=str(xdg))
        target = tmp_path / "one-button"
        result = run_door("--new", str(target), env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        assert "Preset:" in result.stdout  # the layer announced itself
        # zero prompts is structural (stdin closed); zero NOTICES is the
        # preset's work — nothing was skipped-with-notice
        assert "Offer skipped" not in result.stdout
        _assert_doctor_tail(result.stdout)
        region = _kit_install_region(target)
        assert "shape: single" in region
        assert "profile: python" in region
        assert "bots: coderabbit bugbot" in region
        # F6: .env seeded 0600, gitignored, contents NEVER surfaced
        dotenv = target / ".env"
        assert dotenv.is_file()
        assert (dotenv.stat().st_mode & 0o777) == 0o600
        assert SECRET in dotenv.read_text(encoding="utf-8")
        assert SECRET not in result.stdout + result.stderr
        check_ignore = subprocess.run(
            ["git", "-C", str(target), "check-ignore", "-q", ".env"],
            env=env,
            timeout=30,
        )
        assert check_ignore.returncode == 0, ".env must be gitignored"
        status = subprocess.run(
            ["git", "-C", str(target), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        assert status.stdout.strip() == ""  # nothing staged, nothing dangling
        tracked_grep = subprocess.run(
            ["git", "-C", str(target), "grep", "-l", SECRET, "HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        assert tracked_grep.stdout.strip() == ""  # secret in no tracked file
        # F7: the run read the preset but never touched it
        assert preset_file.read_bytes() == preset_before

    def test_no_preset_gives_the_stranger_path(self, tmp_path):
        """--no-preset with a preset present must be byte-identical to
        a machine with no preset at all (N1's flip side)."""
        xdg = _demo_preset_xdg(tmp_path)
        # same basename in different parents: engine banners print the
        # project NAME, so only the parent path may differ
        target_a = make_adopt_dir(tmp_path / "a", "proj")
        target_b = make_adopt_dir(tmp_path / "b", "proj")
        with_flag = run_door(
            "--adopt",
            str(target_a),
            "--no-preset",
            env=_scrubbed_env(XDG_CONFIG_HOME=str(xdg)),
        )
        stranger = run_door("--adopt", str(target_b))
        assert with_flag.returncode == 0, with_flag.stderr + with_flag.stdout
        assert stranger.returncode == 0, stranger.stderr + stranger.stdout
        normalized_a = with_flag.stdout.replace(str(target_a), "<T>")
        normalized_b = stranger.stdout.replace(str(target_b), "<T>")
        assert normalized_a == normalized_b

    def test_adopt_record_beats_preset(self, tmp_path):
        """A recorded target keeps its identity: the preset answers
        none of the recorded questions, and the record round-trips
        untouched (divergence belongs to doctor --against-preset)."""
        target = make_adopt_dir(tmp_path, "recorded")
        first = run_door("--adopt", str(target), "--profile", "none", "--bots", "none")
        assert first.returncode == 0, first.stderr + first.stdout
        xdg = write_preset(
            tmp_path, "shape: planning\nprofile: python\nbots: coderabbit bugbot\n"
        )
        readopt = run_door(
            "--adopt", str(target), env=_scrubbed_env(XDG_CONFIG_HOME=str(xdg))
        )
        assert readopt.returncode == 0, readopt.stderr + readopt.stdout
        assert "Setup door: mode=adopt shape=single" in readopt.stdout
        region = _kit_install_region(target)
        assert "shape: single" in region
        assert "profile: none" in region
        assert "bots: none" in region

    def test_preset_answers_the_offer_questions(self, tmp_path):
        """Preset 'evaluators:'/'venv:' answers reach run_offers like
        flags would — the non-interactive skip notices disappear (the
        preset-less baseline asserts their presence). 'no' keeps the
        test network-free; the wiring is identical for 'yes'."""
        xdg = write_preset(tmp_path, "evaluators: no\nvenv: no\n")
        target = make_adopt_dir(tmp_path, "offers")
        result = run_door(
            "--adopt", str(target), env=_scrubbed_env(XDG_CONFIG_HOME=str(xdg))
        )
        assert result.returncode == 0, result.stderr + result.stdout
        assert "Offer skipped (non-interactive): evaluators" not in result.stdout
        assert "Offer skipped (non-interactive): venv" not in result.stdout

    def test_bad_offer_value_fails_loud(self, tmp_path):
        xdg = write_preset(tmp_path, "evaluators: maybe\n")
        target = make_adopt_dir(tmp_path, "badval")
        result = run_door(
            "--adopt", str(target), env=_scrubbed_env(XDG_CONFIG_HOME=str(xdg))
        )
        assert result.returncode == 2
        assert "preset key 'evaluators' must be yes or no" in result.stderr

    def test_unreadable_preset_fails_loud(self, tmp_path):
        # a present-but-unreadable preset must diagnose itself, not
        # die with bash's raw "Permission denied" (fast-v2 finding)
        if os.geteuid() == 0:
            pytest.skip("permission checks are meaningless as root")
        xdg = write_preset(tmp_path, "shape: single\n")
        (xdg / "agentive-kit" / "preset").chmod(0o000)
        target = make_adopt_dir(tmp_path, "unreadable")
        try:
            result = run_door(
                "--adopt", str(target), env=_scrubbed_env(XDG_CONFIG_HOME=str(xdg))
            )
            assert result.returncode == 2
            assert "not readable" in result.stderr
            assert "--no-preset" in result.stderr  # the escape hatch is named
        finally:
            (xdg / "agentive-kit" / "preset").chmod(0o600)

    @pytest.mark.slow
    def test_loose_env_source_perms_warn_but_proceed(self, tmp_path):
        """0600 on the SOURCE is expected-not-enforced by design (F6:
        it is the operator's own file; the target copy is always
        0600) — but the warning must actually fire."""
        xdg = _demo_preset_xdg(tmp_path)
        env_template = tmp_path / "env-template"
        env_template.chmod(0o644)
        env = _scrubbed_env(XDG_CONFIG_HOME=str(xdg))
        target = tmp_path / "loose-perms"
        result = run_door("--new", str(target), env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        assert "0600 expected" in result.stderr
        assert ((target / ".env").stat().st_mode & 0o777) == 0o600

    def test_unreadable_env_source_fails_before_any_work(self, tmp_path):
        if os.geteuid() == 0:
            pytest.skip("permission checks are meaningless as root")
        secret_file = tmp_path / "env-template"
        secret_file.write_text("KEY=x\n", encoding="utf-8")
        secret_file.chmod(0o000)
        xdg = write_preset(tmp_path, f"env-source: {secret_file}\n")
        env = _scrubbed_env(XDG_CONFIG_HOME=str(xdg))
        try:
            result = run_door("--new", str(tmp_path / "proj"), env=env, timeout=30)
            assert result.returncode == 2
            assert "not readable" in result.stderr
            assert not (tmp_path / "proj").exists()  # failed BEFORE any work
        finally:
            secret_file.chmod(0o600)


@pytest.mark.slow
class TestBotsDeclarationE2E:
    """KIT-0056 P5: the --bots flag through door + engine + record."""

    def test_adopt_bots_subset_records_line(self, tmp_path):
        target = make_adopt_dir(tmp_path, "one-bot")
        result = run_door("--adopt", str(target), "--bots", "coderabbit")
        assert result.returncode == 0, result.stderr + result.stdout
        region = _kit_install_region(target)
        assert "bots: coderabbit" in region
        assert "bugbot" not in region

    def test_new_planning_with_bots_records_line(self, tmp_path):
        # the matrix's other seed path: the planning region body (4
        # lines incl. the target pointer) gains the bots line too
        env = _scrubbed_env(XDG_CONFIG_HOME=str(_git_identity(tmp_path)))
        target = tmp_path / "planning-bots"
        result = run_door(
            "--new", str(target), "--shape", "planning", "--bots", "none", env=env
        )
        assert result.returncode == 0, result.stderr + result.stdout
        region = _kit_install_region(target)
        assert "shape: planning" in region
        assert "target_github:" in region
        assert "bots: none" in region

    def test_legacy_shim_rejects_bots(self, tmp_path):
        # the legacy channel never writes a bots line — an explicit
        # --bots must be rejected, never silently dropped
        target = make_adopt_dir(tmp_path, "shim")
        result = run_door("--adopt", str(target), "--legacy-shim", "--bots", "none")
        assert result.returncode == 2
        assert "--legacy-shim" in result.stderr

    def test_legacy_shim_ignores_preset(self, tmp_path):
        # shim fidelity: a filled preset must not change what the
        # legacy channel does — no preset notice, no recorded bots
        xdg = write_preset(tmp_path, "bots: none\nprofile: none\n")
        target = make_adopt_dir(tmp_path, "shim-preset")
        result = run_door(
            "--adopt",
            str(target),
            "--legacy-shim",
            env=_scrubbed_env(XDG_CONFIG_HOME=str(xdg)),
        )
        assert result.returncode == 0, result.stderr + result.stdout
        assert "Preset:" not in result.stdout
        region = _kit_install_region(target)
        assert "profile: python" in region  # kit default, not the preset
        assert "bots:" not in region

    def test_readopt_adds_bots_line_surgically(self, tmp_path):
        """An existing record without the line gains exactly the bots
        line — shape/profile preserved byte-for-byte (the one-writer
        path through kit_markers, never a region rewrite)."""
        target = make_adopt_dir(tmp_path, "add-later")
        assert run_door("--adopt", str(target), "--profile", "none").returncode == 0
        before = _kit_install_region(target)
        assert "shape: single\nprofile: none\n" in before
        assert "bots:" not in before
        result = run_door("--adopt", str(target), "--bots", "none")
        assert result.returncode == 0, result.stderr + result.stdout
        assert "bots line added" in result.stdout
        after = _kit_install_region(target)
        # prior lines byte-preserved, bots appended right after them
        assert "shape: single\nprofile: none\nbots: none\n" in after

    def test_readopt_conflicting_bots_rejected(self, tmp_path):
        target = make_adopt_dir(tmp_path, "conflict")
        assert run_door("--adopt", str(target), "--bots", "none").returncode == 0
        result = run_door("--adopt", str(target), "--bots", "coderabbit bugbot")
        assert result.returncode == 2
        assert "conflicts with the target's existing kit-install record" in (
            result.stderr
        )
        assert "bots: none" in _kit_install_region(target)  # record untouched

    def test_indented_existing_bots_line_not_duplicated(self, tmp_path):
        """o3 (this PR): an indented hand-edited bots line read as
        'absent' by the engine would gain a SECOND bots line — the
        whitespace-tolerant reader must see it and no-op."""
        target = make_adopt_dir(tmp_path, "indented")
        assert run_door("--adopt", str(target), "--bots", "none").returncode == 0
        claude_md = target / "CLAUDE.md"
        text = claude_md.read_text(encoding="utf-8")
        claude_md.write_text(
            text.replace("\nbots: none\n", "\n   bots: none\n"), encoding="utf-8"
        )
        result = run_door("--adopt", str(target), "--bots", "none")
        assert result.returncode == 0, result.stderr + result.stdout
        assert "bots line added" not in result.stdout
        region = _kit_install_region(target)
        assert region.count("bots:") == 1

    def test_equivalent_bots_record_is_not_a_conflict(self, tmp_path):
        """BugBot PR #83: conflict checks compare NORMALIZED forms —
        a hand-edited 'BugBot, CodeRabbit' record is the same
        declaration as --bots 'bugbot coderabbit', not a conflict,
        and the engine must not append a second line either."""
        target = make_adopt_dir(tmp_path, "equiv")
        first = run_door("--adopt", str(target), "--bots", "coderabbit bugbot")
        assert first.returncode == 0, first.stderr + first.stdout
        claude_md = target / "CLAUDE.md"
        text = claude_md.read_text(encoding="utf-8")
        claude_md.write_text(
            text.replace("\nbots: coderabbit bugbot\n", "\nbots: BugBot, CodeRabbit\n"),
            encoding="utf-8",
        )
        result = run_door("--adopt", str(target), "--bots", "bugbot coderabbit")
        assert result.returncode == 0, result.stderr + result.stdout
        assert "conflicts" not in result.stderr
        assert "bots line added" not in result.stdout
        region = _kit_install_region(target)
        assert region.count("bots:") == 1
        # the operator's spelling is preserved, not rewritten
        assert "bots: BugBot, CodeRabbit" in region

    def test_new_without_bots_writes_no_line(self, tmp_path):
        """N1: no flag, no preset — the record is byte-identical to a
        pre-KIT-0056 install (no bots line, zero migration)."""
        target = make_adopt_dir(tmp_path, "no-decl")
        result = run_door("--adopt", str(target))
        assert result.returncode == 0, result.stderr + result.stdout
        assert "bots:" not in _kit_install_region(target)


class TestPresetNeverDistributed:
    """F7: nothing under ~/.config/agentive-kit/ rides any sync tier,
    rsync, or export path. Structural check: the ONLY scripts allowed
    to reference the preset location are the door (reads it) and the
    project script (doctor --against-preset compares against it) —
    engines, sync, and export code must not know it exists."""

    ALLOWED = {"scripts/local/bootstrap", "scripts/core/project"}

    def test_preset_path_referenced_only_by_door_and_doctor(self):
        offenders = []
        for path in (REPO_ROOT / "scripts").rglob("*"):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if "agentive-kit" in text:
                rel = str(path.relative_to(REPO_ROOT))
                if rel not in self.ALLOWED:
                    offenders.append(rel)
        assert (
            offenders == []
        ), f"preset location referenced outside the allowed readers: {offenders}"

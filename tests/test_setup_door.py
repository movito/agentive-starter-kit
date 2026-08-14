"""Tests for scripts/local/bootstrap — the exec shim over the packaged
door (KIT-0104 F3).

The door lives in the agentive-kit package (``agentive new`` /
``agentive adopt``); ``bootstrap`` only translates the historical
``--new <dir>`` / ``--adopt <dir>`` flags to the package verbs and
execs the checkout's own package source. This module pins the SHIM
contract:

- flag translation (split and ``=`` forms, flag-swallowing guard);
- help deferred to the package — no second copy of the matrix or the
  flag table survives in the shim file (F2, asserted statically);
- exit-code pass-through (the package's 0/1/2 contract);
- the one legacy branch the shim keeps: ``--adopt --design-materials``
  (dies with the shim — KIT-0107);
- the removal notice on stderr.

Everything the old door FRONT did — resolution chain, matrix
validation, preset layer, record conflicts, .env seeding — is packaged
code now, covered by ``tests/agentive_kit/test_door_units.py`` and
``test_door_e2e.py``. Whole-flow coverage THROUGH the shim lives in
``tests/test_bootstrap_shapes.py`` (packaged-contract shapes +
shim-vs-direct equivalence) and ``tests/test_scaffold_acceptance.py``
(per-shape acceptance, which imports this module's helpers).

Non-TTY discipline (N4): every subprocess runs with stdin closed, so
any prompt would hang and trip the timeout instead of silently passing.

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


# Nonexistent hermetic paths keep every door run hermetic (N1): the
# operator's REAL config home must never leak into the suite — a
# filled preset would change door answers. AGENTIVE_KIT_CONFIG_DIR is
# the door's one override; tests that need a preset pass their own via
# extra (override wins). XDG_CONFIG_HOME stays pinned too: git's own
# config lookup goes through it.
_HERMETIC_XDG = REPO_ROOT / "tests" / ".no-such-xdg"
_HERMETIC_CONFIG = REPO_ROOT / "tests" / ".no-such-config-home"


def _scrubbed_env(**extra: str) -> dict[str, str]:
    """os.environ minus GIT_* (the KIT-0048 GIT_DIR leak class)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["XDG_CONFIG_HOME"] = str(_HERMETIC_XDG)
    env["AGENTIVE_KIT_CONFIG_DIR"] = str(_HERMETIC_CONFIG)
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


def _env_lines(target: Path) -> list[str]:
    return (target / ".env").read_text(encoding="utf-8").splitlines()


def _assert_env_invariants(target: Path, env: dict) -> None:
    """KIT-0084 F1: present, mode 0600, gitignored."""
    dotenv = target / ".env"
    assert dotenv.is_file(), ".env must be seeded on --new"
    assert (dotenv.stat().st_mode & 0o777) == 0o600
    check_ignore = subprocess.run(
        ["git", "-C", str(target), "check-ignore", "-q", ".env"],
        env=env,
        timeout=30,
    )
    assert check_ignore.returncode == 0, ".env must be gitignored"


class TestShimStatic:
    """F2's grep proof, pinned as a test: the shim file carries no
    second copy of the matrix, the legality logic, or the flag table —
    the package is the single owner."""

    def test_no_matrix_copy_survives(self):
        text = DOOR.read_text(encoding="utf-8")
        for needle in (
            "single:python",  # the LEGAL_PAIRS data form
            "LEGAL_PAIRS",
            "validate_pair",
            "validate_combo",
            "validate_values",
            "legal_pairs_human",
            "planning+none",  # the human-readable table form
            "✔",  # the help-table matrix glyphs
        ):
            assert needle not in text, f"matrix copy in shim: {needle!r}"

    def test_no_resolution_chain_survives(self):
        """The preset/record/default chain is package code — none of
        its function surface may reappear in the shim."""
        text = DOOR.read_text(encoding="utf-8")
        for needle in (
            "resolve_setting",
            "load_preset",
            "preset_get",
            "kit_default",
            "load_record",
            "check_record_conflict",
            "normalize_bots",
        ):
            assert needle not in text, f"resolver copy in shim: {needle!r}"

    def test_only_the_materials_engine_is_referenced(self):
        """The shim's one legacy branch drives engine-materials.sh; the
        scaffold/consumer engines are reached only through the package."""
        text = DOOR.read_text(encoding="utf-8")
        assert "engine-materials.sh" in text
        assert "engine-consumer.sh" not in text
        assert "engine-scaffold.sh" not in text

    def test_shim_names_its_removal_task(self):
        assert "KIT-0107" in DOOR.read_text(encoding="utf-8")


class TestTranslation:
    """Historical flags reach the package as verbs."""

    def test_help_deferred_to_package_new(self):
        result = run_door("--help")
        assert result.returncode == 0
        assert "agentive new — the agentive setup door" in result.stdout
        # the shim's own header must not answer — the package does
        assert "the one setup door" not in result.stdout

    def test_help_deferred_to_package_adopt(self, tmp_path):
        # a bare '-h' after --adopt is a swallowed-flag error (see the
        # guard test below) — adopt help rides an ordinary invocation
        result = run_door("--adopt", str(tmp_path), "--help")
        assert result.returncode == 0
        assert "agentive adopt — the agentive setup door" in result.stdout

    def test_removal_notice_on_stderr(self):
        result = run_door("--help")
        assert "shim over the packaged door" in result.stderr
        assert "KIT-0107" in result.stderr
        # notice never pollutes stdout (the derivable-help surface)
        assert "shim over the packaged door" not in result.stdout

    def test_missing_mode_non_tty_fails_fast(self):
        result = run_door(timeout=30)
        assert result.returncode == 2
        assert "mode is required" in result.stderr

    def test_missing_target_reaches_package_prompt_guard(self):
        result = run_door("--adopt", timeout=30)
        assert result.returncode == 2
        assert "target directory is required" in result.stderr

    def test_second_mode_flag_refused_never_drops_first_target(self, tmp_path):
        # CodeRabbit (this PR): '--new a --adopt b' must not silently
        # drop 'a' (the masking class) — one mode per run
        result = run_door(
            "--new", str(tmp_path / "a"), "--adopt", str(tmp_path / "b"), timeout=30
        )
        assert result.returncode == 2
        assert "only one mode flag is allowed" in result.stderr

    def test_mode_flag_must_not_swallow_following_flag(self):
        # BugBot PR #81: '--new --shape planning' must not adopt
        # '--shape' as the target directory
        result = run_door("--new", "--shape", "planning", timeout=30)
        assert result.returncode == 2
        assert "requires a value" in result.stderr
        result = run_door("--new", "-h", timeout=30)
        assert result.returncode == 2
        assert "requires a value" in result.stderr
        # equals-form arms validate the suffix the same way — a
        # '--new=--help' must be a usage error, never help exit 0
        # (CodeRabbit round 2)
        result = run_door("--new=--help", timeout=30)
        assert result.returncode == 2
        assert "requires a value" in result.stderr
        result = run_door("--adopt=-h", timeout=30)
        assert result.returncode == 2
        assert "requires a value" in result.stderr

    def test_equals_form_translates(self, tmp_path):
        # --adopt=<dir> reaches the package as a target: the run gets
        # past the shim and fails on the PACKAGE's own target check
        result = run_door(f"--adopt={tmp_path / 'nope'}", timeout=60)
        assert result.returncode == 2
        assert "--adopt target does not exist" in result.stderr

    def test_unknown_flag_is_the_packages_usage_error(self, tmp_path):
        result = run_door("--new", str(tmp_path / "x"), "--frobnicate", timeout=60)
        assert result.returncode == 2
        assert "unknown argument: --frobnicate" in result.stderr
        assert "agentive new --help" in result.stderr  # the package's pointer

    def test_new_target_must_not_exist_via_package(self, tmp_path):
        result = run_door("--new", str(tmp_path), timeout=60)
        assert result.returncode == 2
        assert "already exists" in result.stderr


class TestMaterialsBranch:
    """The one legacy branch the shim keeps (dies with it, KIT-0107):
    exactly `--adopt <dir> --design-materials` — any other flag
    alongside (including `--no-preset`: the materials engine reads no
    preset) is refused loudly, never silently dropped."""

    def test_requires_adopt(self, tmp_path):
        result = run_door("--new", str(tmp_path / "x"), "--design-materials")
        assert result.returncode == 2
        assert "--design-materials applies to --adopt only" in result.stderr

    def test_requires_existing_target(self, tmp_path):
        result = run_door("--adopt", str(tmp_path / "nope"), "--design-materials")
        assert result.returncode == 2
        assert "does not exist" in result.stderr

    def test_no_kit_contradiction_keeps_its_message(self, tmp_path):
        target = make_adopt_dir(tmp_path, "mat")
        result = run_door("--adopt", str(target), "--design-materials", "--no-kit")
        assert result.returncode == 2
        assert "--no-kit contradicts --design-materials" in result.stderr

    def test_other_flags_refused_never_dropped(self, tmp_path):
        target = make_adopt_dir(tmp_path, "mat")
        for extra in (
            ["--shape", "planning"],
            ["--profile", "none"],
            ["--bots", "none"],
            # the materials engine reads no preset, so the flag would
            # be a silent no-op — refused like the rest (CodeRabbit)
            ["--no-preset"],
        ):
            result = run_door("--adopt", str(target), "--design-materials", *extra)
            assert result.returncode == 2, extra
            assert "cannot be combined with --design-materials" in result.stderr, extra

    def test_kit_checkout_target_refused(self):
        """BugBot (this PR): the branch bypasses the package's
        kit-checkout guard, so it carries the old door's own refusal —
        the materials flow must never rsync the kit onto itself."""
        result = run_door("--adopt", str(REPO_ROOT), "--design-materials")
        assert result.returncode == 2
        assert "kit source repo itself" in result.stderr

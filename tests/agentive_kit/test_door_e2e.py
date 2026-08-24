"""E2E tests for ``agentive new`` / ``agentive adopt`` (KIT-0104).

The packaged door runs as a subprocess exactly as an installed CLI
would — from a working directory with NO path relationship to any
agentive-starter-kit checkout, against targets in scratch space. The
no-checkout assertion is ASSERTED, never assumed (spec AC 1): the
fixture verifies that neither the working directory, the target, nor
any of their ancestors is a kit checkout before the door runs.

Non-TTY discipline: every subprocess runs with stdin closed, so any
prompt that leaked past the flag layer would hang and trip the
timeout instead of silently passing.

Marked slow (the doctor tail runs real environment checks): the
pre-commit fast hook deselects these; CI and full pytest runs cover
them.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip(
    "agentive_kit", reason="agentive-kit package source present only in the kit repo"
)

pytestmark = pytest.mark.slow

_HERMETIC_CONFIG_NAME = ".no-such-config-home"


def _kit_checkout_ancestors(path: Path) -> list[Path]:
    """Every ancestor (path included) that looks like a kit checkout."""
    hits = []
    for candidate in (path, *path.parents):
        if (candidate / "scripts" / "local" / "bootstrap").is_file():
            hits.append(candidate)
    return hits


def _git_identity_xdg(base: Path) -> Path:
    xdg = base / "xdg-config"
    (xdg / "git").mkdir(parents=True, exist_ok=True)
    (xdg / "git" / "config").write_text(
        "[user]\n\tname = Kit Test\n\temail = kit-test@example.invalid\n",
        encoding="utf-8",
    )
    return xdg


def _door_env(base: Path, config_dir: Path | None = None) -> dict[str, str]:
    """Scrubbed env: no GIT_* (the KIT-0048 leak class), hermetic git
    config, and a hermetic preset home unless a test supplies one —
    the operator's REAL agentive-config must never leak into a run.

    PYTHONPATH carries the agentive_kit package location into the
    subprocess: in CI the package is importable only via
    tests/conftest.py's sys.path injection, which a child interpreter
    does not inherit (CI round 1 — all E2E runs died with
    ModuleNotFoundError while passing locally against the dev
    install). This is the CODE channel, the moral equivalent of an
    installed wheel's site-packages — the no-kit-checkout assertion is
    about the door's cwd/target/data resolution, which stays
    checkout-free.
    """
    import agentive_kit

    pkg_src = Path(agentive_kit.__file__).resolve().parents[1]
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{pkg_src}{os.pathsep}{existing}" if existing else str(pkg_src)
    env["XDG_CONFIG_HOME"] = str(_git_identity_xdg(base))
    env["AGENTIVE_KIT_CONFIG_DIR"] = str(
        config_dir if config_dir else base / _HERMETIC_CONFIG_NAME
    )
    return env


def run_door(
    verb: str,
    *args: str,
    cwd: Path,
    env: dict[str, str],
    timeout: int = 300,
) -> subprocess.CompletedProcess:
    """Run the door exactly as an installed CLI: no kit checkout in
    sight. The cwd is asserted checkout-free before every run."""
    assert not _kit_checkout_ancestors(
        cwd
    ), f"E2E cwd must have no kit-checkout ancestor: {cwd}"
    return subprocess.run(
        [sys.executable, "-m", "agentive_kit.cli", verb, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        stdin=subprocess.DEVNULL,  # never a TTY — prompts must be unreachable
        cwd=str(cwd),
        env=env,
    )


@pytest.fixture(scope="module")
def new_single(tmp_path_factory):
    base = tmp_path_factory.mktemp("door-new-single")
    env = _door_env(base)
    target = base / "fresh-single"
    # AC 1, asserted not assumed: the target's whole ancestry carries
    # no kit checkout, and the door runs from scratch space too.
    assert not _kit_checkout_ancestors(target.parent)
    result = run_door("new", str(target), cwd=base, env=env)
    return target, result


@pytest.fixture(scope="module")
def new_planning(tmp_path_factory):
    base = tmp_path_factory.mktemp("door-new-planning")
    env = _door_env(base)
    target = base / "fresh-planning"
    result = run_door(
        "new",
        str(target),
        "--shape",
        "planning",
        "--target-path",
        "../product",
        "--target-github",
        "acme/product",
        cwd=base,
        env=env,
    )
    return target, result


class TestNewSingle:
    def test_succeeds_from_nowhere_near_a_kit_checkout(self, new_single):
        target, result = new_single
        assert result.returncode == 0, result.stderr + result.stdout
        assert "Install complete:" in result.stdout

    def test_kit_skeleton_and_content(self, new_single):
        target, result = new_single
        for rel in (
            ".kit/tasks/1-backlog",
            ".kit/tasks/5-done",
            ".kit/context/workflows",
            ".kit/templates",
            "docs/adr",
        ):
            assert (target / rel).is_dir(), f"missing {rel}"
        for rel in (
            "README.md",
            "CLAUDE.md",
            ".kit/context/agent-handoffs.json",
            ".kit/context/current-state.json",
            ".kit/templates/TASK-STARTER-TEMPLATE.md",
            ".kit/context/workflows/COMMIT-PROTOCOL.md",
            ".adversarial/config.yml",
            ".pre-commit-config.yaml",
            ".gitignore",
            ".env.template",
            "scripts/local/checks.sh",
        ):
            assert (target / rel).is_file(), f"missing {rel}"

    def test_record_written(self, new_single):
        target, result = new_single
        text = (target / "CLAUDE.md").read_text(encoding="utf-8")
        assert "BEGIN KIT-LOCAL: kit-install" in text
        assert "shape: single" in text
        assert "profile: python" in text
        assert "BEGIN KIT-LOCAL: first-session" in text
        assert "agentive doctor" in text  # packaged region bodies

    def test_packaged_world_no_copies(self, new_single):
        """ADR-0028: lifecycle scripts come from the package, agents
        from the plugin — the scaffold carries neither."""
        target, result = new_single
        assert not (target / "scripts" / "core").exists()
        assert not (target / ".claude").exists()
        assert not (target / "scripts" / "local" / "kit_markers.py").exists()

    def test_adversarial_pins_are_real(self, new_single):
        target, result = new_single
        text = (target / ".adversarial" / "config.yml").read_text(encoding="utf-8")
        # non-empty values, not just the keys (CodeRabbit)
        assert re.search(r'^adversarial_cli_version: "[^"]+"$', text, re.M), text
        assert re.search(r'^evaluator_library_version: "[^"]+"$', text, re.M), text

    def test_env_seeded_with_identity(self, new_single):
        target, result = new_single
        env_file = target / ".env"
        assert env_file.is_file()
        assert env_file.stat().st_mode & 0o777 == 0o600
        lines = env_file.read_text(encoding="utf-8").splitlines()
        assert f"PROJECT_NAME={target.name}" in lines
        prefix_lines = [ln for ln in lines if ln.startswith("TASK_PREFIX=")]
        assert prefix_lines and prefix_lines[0] != "TASK_PREFIX="

    def test_committed_on_main(self, new_single):
        target, result = new_single
        branch = subprocess.run(
            ["git", "-C", str(target), "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert branch.stdout.strip() == "main"
        status = subprocess.run(
            ["git", "-C", str(target), "status", "--short"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # only .env may be dirty — it is gitignored, so status is clean
        assert status.stdout.strip() == "", status.stdout

    def test_doctor_ran_and_verdict_reported(self, new_single):
        """AC 2's testable core: the doctor RUNS in the created project
        and its verdict is REPORTED (never encoded in the exit code).
        Environment-dependent checks (API keys, evaluator install) may
        FAIL in scratch space — the structural checks must not."""
        target, result = new_single
        assert "Doctor verdict:" in result.stdout
        assert "DOCTOR:35-handoffs-paths.py:PASS" in result.stdout

    def test_package_verification_lines(self, new_single):
        target, result = new_single
        assert "agentive CLI:" in result.stdout
        assert (
            "agent plugin: verified" in result.stdout
            or "Install the agent plugin:" in result.stdout
        )


class TestNewPlanning:
    def test_succeeds(self, new_planning):
        target, result = new_planning
        assert result.returncode == 0, result.stderr + result.stdout
        assert "planning shape → profile none (forced" in result.stdout

    def test_pointer_recorded_and_sectioned(self, new_planning):
        target, result = new_planning
        text = (target / "CLAUDE.md").read_text(encoding="utf-8")
        assert "## Target Repository" in text
        assert "- **Path**: `../product`" in text
        assert "target_path: ../product" in text
        assert "target_github: acme/product" in text
        assert "shape: planning" in text

    def test_empty_prefix_for_intake(self, new_planning):
        target, result = new_planning
        lines = (target / ".env").read_text(encoding="utf-8").splitlines()
        assert "TASK_PREFIX=" in lines

    def test_no_python_toolchain(self, new_planning):
        target, result = new_planning
        assert not (target / "pyproject.toml").exists()
        assert not (target / "tests").exists()


class TestNewNoKit:
    """KIT-0104 F4: rung 0 (KIT-ADR-0032) is reachable from the ``new``
    verb too — a blank project, not a kit install."""

    def test_new_no_kit_is_rung_zero(self, tmp_path):
        env = _door_env(tmp_path)
        target = tmp_path / "blank-proto"
        result = run_door("new", str(target), "--no-kit", cwd=tmp_path, env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        assert "rung 0" in result.stdout.lower()
        assert "Doctor not run (nothing to check)" in result.stdout
        assert "Doctor verdict:" not in result.stdout
        # check hook + git, NOTHING else — no .kit/, no record, no .env
        assert (target / "scripts" / "local" / "checks.sh").is_file()
        assert not (target / ".kit").exists()
        assert not (target / "CLAUDE.md").exists()
        assert not (target / ".adversarial").exists()
        assert not (target / ".env").exists()
        assert not (target / "scripts" / "core").exists()
        # committed on main, single rung-0 commit. env=env: the door
        # ran GIT_*-scrubbed, so the probes must too — a runner-leaked
        # GIT_DIR would point them at the wrong repo (CodeRabbit)
        branch = subprocess.run(
            ["git", "-C", str(target), "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        assert branch.stdout.strip() == "main"
        log = subprocess.run(
            ["git", "-C", str(target), "log", "--oneline"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        assert len(log.stdout.strip().splitlines()) == 1
        assert "rung-0" in log.stdout

    def test_new_no_kit_offers_acknowledged_never_dropped(self, tmp_path):
        """Same masking-class contract as the adopt side: explicit
        offer answers rung 0 cannot honor are acknowledged out loud."""
        env = _door_env(tmp_path)
        target = tmp_path / "blank-offers"
        result = run_door(
            "new",
            str(target),
            "--no-kit",
            "--with-evaluators",
            "--with-venv",
            cwd=tmp_path,
            env=env,
        )
        assert result.returncode == 0, result.stderr + result.stdout
        assert "Evaluators not installed" in result.stdout
        assert "venv setup skipped" in result.stdout
        assert not (target / ".adversarial").exists()

    def test_new_no_kit_with_bots_rejected_loud(self, tmp_path):
        env = _door_env(tmp_path)
        result = run_door(
            "new",
            str(tmp_path / "botsless"),
            "--no-kit",
            "--bots",
            "coderabbit",
            cwd=tmp_path,
            env=env,
        )
        assert result.returncode == 2
        assert "--no-kit targets record nothing" in (result.stdout + result.stderr)
        assert not (tmp_path / "botsless").exists()

    def test_new_no_kit_with_name_rejected_loud(self, tmp_path):
        """--name/--prefix shape the scaffold rung 0 never gets — an
        error, never a silent drop."""
        env = _door_env(tmp_path)
        result = run_door(
            "new",
            str(tmp_path / "named"),
            "--no-kit",
            "--name",
            "X",
            cwd=tmp_path,
            env=env,
        )
        assert result.returncode == 2
        assert "--no-kit targets get no scaffold" in (result.stdout + result.stderr)
        assert not (tmp_path / "named").exists()

    def test_new_no_kit_env_source_acknowledged_not_applied(self, tmp_path):
        """A preset env-source cannot be honored on rung 0 (no
        .gitignore to keep the secrets out of git) — said out loud."""
        cfg = tmp_path / "cfg"
        cfg.mkdir()
        source = cfg / "env.source"
        source.write_text("ANTHROPIC_API_KEY=sk-test\n", encoding="utf-8")
        source.chmod(0o600)
        (cfg / "preset").write_text("env-source: env.source\n", encoding="utf-8")
        env = _door_env(tmp_path, config_dir=cfg)
        target = tmp_path / "blank-preset"
        result = run_door("new", str(target), "--no-kit", cwd=tmp_path, env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        assert "env-source not applied" in result.stdout
        assert not (target / ".env").exists()


class TestAdopt:
    def _make_repo(self, base: Path, name: str) -> Path:
        target = base / name
        target.mkdir(parents=True)
        subprocess.run(
            ["git", "init", "-q", "-b", "main", str(target)],
            check=True,
            timeout=30,
        )
        return target

    def test_adopt_preserves_and_records(self, tmp_path):
        env = _door_env(tmp_path)
        target = self._make_repo(tmp_path, "docsrepo")
        (target / "README.md").write_text("# Mine\n", encoding="utf-8")
        (target / "CLAUDE.md").write_text(
            "# Mine\n\nHand-written intro.\n", encoding="utf-8"
        )
        result = run_door(
            "adopt", str(target), "--profile", "none", cwd=tmp_path, env=env
        )
        assert result.returncode == 0, result.stderr + result.stdout
        text = (target / "CLAUDE.md").read_text(encoding="utf-8")
        assert "Hand-written intro." in text
        assert "shape: single" in text
        assert "profile: none" in text
        assert (target / "README.md").read_text(encoding="utf-8") == "# Mine\n"
        assert (target / ".kit" / "tasks" / "1-backlog").is_dir()
        # packaged adopt copies NOTHING from a kit tree
        assert not (target / "scripts" / "core").exists()
        assert not (target / ".claude").exists()
        assert not (target / "pyproject.toml").exists()

    def test_readopt_preserves_regions_byte_for_byte(self, tmp_path):
        env = _door_env(tmp_path)
        target = self._make_repo(tmp_path, "again")
        assert (
            run_door(
                "adopt", str(target), "--profile", "none", cwd=tmp_path, env=env
            ).returncode
            == 0
        )
        claude_md = target / "CLAUDE.md"
        customized = claude_md.read_text(encoding="utf-8").replace(
            "No project toolchain is configured",
            "No toolchain (consumer-tuned)",
        )
        claude_md.write_text(customized, encoding="utf-8")
        result = run_door("adopt", str(target), cwd=tmp_path, env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        assert "kit-install region already present (preserved)" in result.stdout
        text = claude_md.read_text(encoding="utf-8")
        assert "No toolchain (consumer-tuned)" in text
        assert text.count("BEGIN KIT-LOCAL: kit-install") == 1
        assert text.count("BEGIN KIT-LOCAL: project-rules") == 1

    def test_flagless_readopt_engines_get_recorded_identity(self, tmp_path):
        """CodeRabbit, this PR: a flagless re-adopt of a recorded
        target must drive the engines with the RECORDED pair, never
        the resolved defaults (which fall to single/python)."""
        env = _door_env(tmp_path)
        target = self._make_repo(tmp_path, "planrec")
        assert (
            run_door(
                "adopt",
                str(target),
                "--shape",
                "planning",
                "--target-path",
                "../prod",
                "--target-github",
                "acme/prod",
                cwd=tmp_path,
                env=env,
            ).returncode
            == 0
        )
        result = run_door("adopt", str(target), cwd=tmp_path, env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        # the consumer engine names the pair it was invoked with
        assert "Recording install (shape: planning, profile: none)" in (result.stdout)
        # ... and every identity-describing message agrees (CodeRabbit
        # round 2: status/commit metadata must use the effective pair)
        assert "Setup door: mode=adopt shape=planning profile=none" in result.stdout
        assert "Install complete: shape=planning profile=none" in result.stdout
        text = (target / "CLAUDE.md").read_text(encoding="utf-8")
        assert "shape: planning" in text
        assert text.count("BEGIN KIT-LOCAL: kit-install") == 1

    def test_gitless_recorded_readopt_commits_effective_pair(self, tmp_path):
        """CodeRabbit round 3: the commit-metadata site only fires on
        gitless targets — a recorded planning adopt of one must commit
        with the effective pair, not the resolved defaults."""
        env = _door_env(tmp_path)
        target = tmp_path / "gitless-planrec"
        target.mkdir()
        (target / "CLAUDE.md").write_text(
            "# X\n\n<!-- BEGIN KIT-LOCAL: kit-install -->\n"
            "shape: planning\nprofile: none\n"
            "<!-- END KIT-LOCAL: kit-install -->\n",
            encoding="utf-8",
        )
        result = run_door("adopt", str(target), cwd=tmp_path, env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        log = subprocess.run(
            ["git", "-C", str(target), "log", "-1", "--format=%B"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert "(shape: planning, profile: none)" in log.stdout

    def test_hand_edited_illegal_record_pair_refused(self, tmp_path):
        env = _door_env(tmp_path)
        target = self._make_repo(tmp_path, "badrec")
        (target / "CLAUDE.md").write_text(
            "# X\n\n<!-- BEGIN KIT-LOCAL: kit-install -->\n"
            "shape: planning\nprofile: python\n"
            "<!-- END KIT-LOCAL: kit-install -->\n",
            encoding="utf-8",
        )
        result = run_door("adopt", str(target), cwd=tmp_path, env=env)
        assert result.returncode == 2
        combined = result.stdout + result.stderr
        assert "illegal shape/profile combination" in combined
        assert "kit-install record" in combined

    def test_conflicting_profile_flag_rejected(self, tmp_path):
        env = _door_env(tmp_path)
        target = self._make_repo(tmp_path, "conflict")
        assert (
            run_door(
                "adopt", str(target), "--profile", "none", cwd=tmp_path, env=env
            ).returncode
            == 0
        )
        result = run_door(
            "adopt", str(target), "--profile", "python", cwd=tmp_path, env=env
        )
        assert result.returncode == 2
        assert "conflicts with the target's existing kit-install record" in (
            result.stdout + result.stderr
        )

    def test_no_kit_is_rung_zero(self, tmp_path):
        """KIT-ADR-0032 rung 0: check hook + git, no .kit/, no record,
        reported as success."""
        env = _door_env(tmp_path)
        target = self._make_repo(tmp_path, "proto")
        (target / "main.py").write_text("print('hi')\n", encoding="utf-8")
        result = run_door("adopt", str(target), "--no-kit", cwd=tmp_path, env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        assert "rung 0" in result.stdout.lower()
        assert (target / "scripts" / "local" / "checks.sh").is_file()
        assert not (target / ".kit").exists()
        assert not (target / "CLAUDE.md").exists()
        assert not (target / "scripts" / "core").exists()

    def test_no_kit_explicit_offers_acknowledged_never_dropped(self, tmp_path):
        """Rung 0 cannot honor the evaluator/venv offers (no
        .adversarial config, no setup-dev.sh) — an explicit answer is
        acknowledged out loud, never silently dropped (the masking
        class)."""
        env = _door_env(tmp_path)
        target = self._make_repo(tmp_path, "offers")
        result = run_door(
            "adopt",
            str(target),
            "--no-kit",
            "--with-evaluators",
            "--with-venv",
            cwd=tmp_path,
            env=env,
        )
        assert result.returncode == 0, result.stderr + result.stdout
        assert "Evaluators not installed" in result.stdout
        assert "venv setup skipped" in result.stdout
        assert not (target / ".adversarial").exists()

    def test_no_kit_gitless_target_gets_initialized(self, tmp_path):
        env = _door_env(tmp_path)
        target = tmp_path / "gitless-proto"
        target.mkdir()
        (target / "notes.md").write_text("x\n", encoding="utf-8")
        result = run_door(
            "adopt",
            str(target),
            "--no-kit",
            "--profile",
            "none",
            cwd=tmp_path,
            env=env,
        )
        assert result.returncode == 0, result.stderr + result.stdout
        assert (target / ".git").is_dir()

    def test_no_kit_with_bots_rejected_loud(self, tmp_path):
        """Rung 0 records nothing — an explicit --bots would be
        silently dropped (the masking class), so it errors instead."""
        env = _door_env(tmp_path)
        target = self._make_repo(tmp_path, "botsless")
        result = run_door(
            "adopt",
            str(target),
            "--no-kit",
            "--bots",
            "coderabbit",
            cwd=tmp_path,
            env=env,
        )
        assert result.returncode == 2
        assert "--no-kit targets record nothing" in (result.stdout + result.stderr)

    def test_design_materials_refused_with_intake_pointer(self, tmp_path):
        env = _door_env(tmp_path)
        target = self._make_repo(tmp_path, "materials")
        result = run_door(
            "adopt", str(target), "--design-materials", cwd=tmp_path, env=env
        )
        assert result.returncode == 2
        assert "project-intake" in result.stdout + result.stderr

    def test_adopting_a_kit_checkout_refused(self, tmp_path):
        env = _door_env(tmp_path)
        fake_kit = tmp_path / "fake-kit"
        (fake_kit / "scripts" / "local").mkdir(parents=True)
        (fake_kit / "scripts" / "local" / "bootstrap").write_text(
            "#!/bin/bash\n", encoding="utf-8"
        )
        (fake_kit / "scripts" / "local" / "engine-consumer.sh").write_text(
            "#!/bin/bash\n", encoding="utf-8"
        )
        result = run_door("adopt", str(fake_kit), cwd=tmp_path, env=env)
        assert result.returncode == 2
        assert "agentive-starter-kit checkout" in result.stdout + result.stderr


class TestExitContract:
    def test_new_target_must_not_exist(self, tmp_path):
        env = _door_env(tmp_path)
        existing = tmp_path / "already"
        existing.mkdir()
        result = run_door("new", str(existing), cwd=tmp_path, env=env)
        assert result.returncode == 2
        assert "already exists" in result.stdout + result.stderr

    def test_adopt_target_must_exist(self, tmp_path):
        env = _door_env(tmp_path)
        result = run_door("adopt", str(tmp_path / "no-such"), cwd=tmp_path, env=env)
        assert result.returncode == 2
        assert "does not exist" in result.stdout + result.stderr

    def test_missing_target_non_tty_fails_fast(self, tmp_path):
        env = _door_env(tmp_path)
        result = run_door("new", cwd=tmp_path, env=env, timeout=60)
        assert result.returncode == 2
        assert "target directory is required" in result.stdout + result.stderr

    def test_illegal_pair_exits_2_naming_pairs(self, tmp_path):
        env = _door_env(tmp_path)
        result = run_door(
            "new",
            str(tmp_path / "x"),
            "--shape",
            "planning",
            "--profile",
            "python",
            cwd=tmp_path,
            env=env,
        )
        assert result.returncode == 2
        assert "illegal shape/profile combination" in (result.stdout + result.stderr)

    def test_unknown_shape_exits_2(self, tmp_path):
        env = _door_env(tmp_path)
        result = run_door(
            "new", str(tmp_path / "x"), "--shape", "pyramid", cwd=tmp_path, env=env
        )
        assert result.returncode == 2
        assert "unknown shape" in (result.stdout + result.stderr).lower()

    def test_malformed_target_github_rejected(self, tmp_path):
        env = _door_env(tmp_path)
        result = run_door(
            "new",
            str(tmp_path / "x"),
            "--shape",
            "planning",
            "--target-github",
            "not a slug",
            cwd=tmp_path,
            env=env,
        )
        assert result.returncode == 2
        assert "owner/repo" in result.stdout + result.stderr

    def test_help_exits_zero_both_verbs(self, tmp_path):
        env = _door_env(tmp_path)
        for verb in ("new", "adopt"):
            result = run_door(verb, "--help", cwd=tmp_path, env=env, timeout=60)
            assert result.returncode == 0
            assert "--shape" in result.stdout

    def test_invalid_bots_exits_2(self, tmp_path):
        env = _door_env(tmp_path)
        result = run_door(
            "new",
            str(tmp_path / "x"),
            "--bots",
            "dependabot",
            cwd=tmp_path,
            env=env,
        )
        assert result.returncode == 2
        assert "unknown bot" in result.stdout + result.stderr


class TestPreset:
    def _write_preset(self, base: Path, content: str) -> Path:
        cfg = base / "agentive-config"
        cfg.mkdir(parents=True, exist_ok=True)
        (cfg / "preset").write_text(content, encoding="utf-8")
        return cfg

    def test_preset_answers_shape_and_bots(self, tmp_path):
        cfg = self._write_preset(tmp_path, "shape: planning\nbots: none\n")
        env = _door_env(tmp_path, config_dir=cfg)
        target = tmp_path / "preset-planning"
        result = run_door("new", str(target), cwd=tmp_path, env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        assert f"Preset: {cfg / 'preset'}" in result.stdout
        text = (target / "CLAUDE.md").read_text(encoding="utf-8")
        assert "shape: planning" in text
        assert "bots: none" in text

    def test_target_parent_sibling_found_without_override(self, tmp_path):
        """The packaged anchor: <target-parent>/agentive-config is
        found with NO env var set (operator decision, 2026-08-13)."""
        parent = tmp_path / "projects"
        parent.mkdir()
        self._write_preset(parent, "profile: none\n")
        env = _door_env(tmp_path)
        del env["AGENTIVE_KIT_CONFIG_DIR"]
        target = parent / "sibling-found"
        result = run_door("new", str(target), cwd=tmp_path, env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        assert "Preset:" in result.stdout
        assert "profile: none" in (target / "CLAUDE.md").read_text(encoding="utf-8")

    def test_no_preset_gives_the_stranger_path(self, tmp_path):
        cfg = self._write_preset(tmp_path, "shape: planning\n")
        env = _door_env(tmp_path, config_dir=cfg)
        target = tmp_path / "stranger"
        result = run_door("new", str(target), "--no-preset", cwd=tmp_path, env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        assert "Preset:" not in result.stdout
        assert "shape: single" in (target / "CLAUDE.md").read_text(encoding="utf-8")

    def test_env_source_seeds_keys(self, tmp_path):
        source = tmp_path / "env.source"
        source.write_text(
            "OPENAI_API_KEY=sk-test\nPROJECT_NAME=placeholder\n" "TASK_PREFIX=TASK\n",
            encoding="utf-8",
        )
        source.chmod(0o600)
        cfg = self._write_preset(tmp_path, f"env-source: {source}\n")
        env = _door_env(tmp_path, config_dir=cfg)
        target = tmp_path / "with-keys"
        result = run_door("new", str(target), cwd=tmp_path, env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        assert "Seeded .env from preset env-source" in result.stdout
        lines = (target / ".env").read_text(encoding="utf-8").splitlines()
        assert "OPENAI_API_KEY=sk-test" in lines
        assert f"PROJECT_NAME={target.name}" in lines  # identity filled
        assert (target / ".env").stat().st_mode & 0o777 == 0o600

    def test_bad_env_source_aborts_pristine(self, tmp_path):
        cfg = self._write_preset(tmp_path, "env-source: /no/such/file\n")
        env = _door_env(tmp_path, config_dir=cfg)
        target = tmp_path / "never-made"
        result = run_door("new", str(target), cwd=tmp_path, env=env)
        assert result.returncode == 2
        assert "env-source not found" in result.stdout + result.stderr
        assert not target.exists(), "a bad preset must abort a pristine run"

    def test_relative_env_source_resolves_against_preset_home(self, tmp_path):
        """BugBot, this PR: `env-source: env.source` — the natural form,
        since the seeded guardrails put env.source beside the preset —
        must resolve against the preset home, never the process cwd."""
        cfg = self._write_preset(tmp_path, "env-source: env.source\n")
        source = cfg / "env.source"
        source.write_text("OPENAI_API_KEY=sk-rel\n", encoding="utf-8")
        source.chmod(0o600)
        env = _door_env(tmp_path, config_dir=cfg)
        # run from a DIFFERENT cwd that also contains a decoy env.source
        decoy_cwd = tmp_path / "elsewhere"
        decoy_cwd.mkdir()
        (decoy_cwd / "env.source").write_text("DECOY=1\n", encoding="utf-8")
        target = tmp_path / "rel-source"
        result = run_door("new", str(target), cwd=decoy_cwd, env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        lines = (target / ".env").read_text(encoding="utf-8").splitlines()
        assert "OPENAI_API_KEY=sk-rel" in lines
        assert "DECOY=1" not in lines

    def test_record_beats_preset_on_readopt(self, tmp_path):
        env0 = _door_env(tmp_path)
        target = tmp_path / "recorded"
        target.mkdir()
        subprocess.run(
            ["git", "init", "-q", "-b", "main", str(target)],
            check=True,
            timeout=30,
        )
        assert (
            run_door(
                "adopt", str(target), "--profile", "none", cwd=tmp_path, env=env0
            ).returncode
            == 0
        )
        cfg = self._write_preset(tmp_path, "profile: python\nvenv: yes\n")
        env = _door_env(tmp_path, config_dir=cfg)
        result = run_door("adopt", str(target), cwd=tmp_path, env=env)
        assert result.returncode == 0, result.stderr + result.stdout
        # the record's profile:none survives, and the preset venv
        # answer is ignored OUT LOUD, never silently
        assert "profile: none" in (target / "CLAUDE.md").read_text(encoding="utf-8")
        assert "Preset venv answer ignored" in result.stdout


# ─────────────────────────────────────────
# KIT-0118 — packaged-door fresh-install fixes (issues #145, #146)
# ─────────────────────────────────────────
@pytest.fixture(scope="module")
def new_planning_github_only(tmp_path_factory):
    """Planning shape with --target-github but NO --target-path: the
    sibling-layout convention derives the path (issue #145)."""
    base = tmp_path_factory.mktemp("door-planning-gh-only")
    env = _door_env(base)
    target = base / "coord-gh"
    result = run_door(
        "new",
        str(target),
        "--shape",
        "planning",
        "--target-github",
        "acme/widget-factory",
        cwd=base,
        env=env,
    )
    return target, result


@pytest.fixture(scope="module")
def new_planning_bare(tmp_path_factory):
    """Planning shape with NEITHER pointer flag — the placeholder case."""
    base = tmp_path_factory.mktemp("door-planning-bare")
    env = _door_env(base)
    target = base / "coord-bare"
    result = run_door("new", str(target), "--shape", "planning", cwd=base, env=env)
    return target, result


def _region_of(target: Path) -> str:
    text = (target / "CLAUDE.md").read_text(encoding="utf-8")
    assert "<!-- BEGIN KIT-LOCAL: kit-install -->" in text
    return text.split("BEGIN KIT-LOCAL: kit-install -->")[1].split(
        "<!-- END KIT-LOCAL: kit-install"
    )[0]


class TestTargetPathDerivation:
    """Issue #145: the machine-read identity record must carry a usable
    path and no prose, in every flag combination."""

    def test_path_derived_from_github(self, new_planning_github_only):
        target, result = new_planning_github_only
        assert result.returncode == 0, result.stderr + result.stdout
        region = _region_of(target)
        assert "target_path: ../widget-factory" in region
        assert "target_github: acme/widget-factory" in region

    def test_derived_path_also_seeds_the_human_section(self, new_planning_github_only):
        target, _ = new_planning_github_only
        text = (target / "CLAUDE.md").read_text(encoding="utf-8")
        assert "- **Path**: `../widget-factory`" in text

    def test_derived_pointer_reported_as_recorded_not_todo(
        self, new_planning_github_only
    ):
        # KIT-0081 F1's tail must not tell an operator whose pointer
        # resolved that the install is unfinished.
        _, result = new_planning_github_only
        assert "Target-repo pointer recorded in CLAUDE.md" in result.stdout
        assert "Fill in the target-repo pointer" not in result.stdout

    def test_no_prose_in_any_recorded_value_derived(self, new_planning_github_only):
        target, _ = new_planning_github_only
        self._assert_clean(target)

    def test_no_prose_in_any_recorded_value_placeholders(self, new_planning_bare):
        target, result = new_planning_bare
        assert result.returncode == 0, result.stderr + result.stdout
        region = _region_of(target)
        # bare placeholders, no "# TODO" prose glued onto the value
        assert "target_path: ../<target-repo>" in region
        assert "target_github: <owner>/<repo>" in region
        self._assert_clean(target)

    def test_placeholder_case_still_prompts_for_the_pointer(self, new_planning_bare):
        _, result = new_planning_bare
        assert "Fill in the target-repo pointer" in result.stdout

    @staticmethod
    def _assert_clean(target: Path) -> None:
        region = _region_of(target)
        for line in region.splitlines():
            if not line.strip():
                continue
            _key, _sep, value = line.partition(":")
            assert "#" not in value, f"prose leaked into the record: {line!r}"

    def test_record_round_trips_through_load_record(self, new_planning_github_only):
        # the door's own reader is the one downstream consumers use
        from agentive_kit import door

        record = door.load_record(new_planning_github_only[0])
        assert record["target_path"] == "../widget-factory"
        assert record["target_github"] == "acme/widget-factory"
        assert record["shape"] == "planning"


@pytest.fixture(scope="module")
def new_without_evaluators(tmp_path_factory):
    base = tmp_path_factory.mktemp("door-eval-declined")
    env = _door_env(base)
    target = base / "declined"
    result = run_door("new", str(target), "--without-evaluators", cwd=base, env=env)
    return target, result


class TestEvaluatorDeclarationRecorded:
    """Issue #146.1: a declined evaluator install is a DECLARATION, and
    doctor must read it instead of failing the operator's own choice."""

    def test_declined_answer_is_recorded(self, new_without_evaluators):
        target, result = new_without_evaluators
        assert result.returncode == 0, result.stderr + result.stdout
        assert "evaluators: no" in _region_of(target)

    def test_doctor_tail_skips_both_evaluator_checks(self, new_without_evaluators):
        _, result = new_without_evaluators
        assert "DOCTOR:30-evaluators.sh:SKIP" in result.stdout or (
            "DOCTOR:evaluators:SKIP:evaluators declined at install" in result.stdout
        )
        assert "DOCTOR:evaluator-cli:SKIP:evaluators declined at install" in (
            result.stdout
        )
        assert "DOCTOR:evaluators:FAIL" not in result.stdout
        assert "DOCTOR:evaluator-cli:FAIL" not in result.stdout

    def test_unanswered_offer_records_nothing(self, new_single):
        # The default run is non-interactive: the offer is SKIPPED, not
        # answered, so the record must stay silent — a defaulted "no"
        # written here would let doctor skip evaluator checks on a
        # project that never declined anything.
        target, _ = new_single
        assert "evaluators:" not in _region_of(target)


class TestEvaluatorDeclarationOnAdopt:
    """Adopt preserves consumer-owned regions, so the declaration has to
    be added surgically — the same masking class (and the same
    treatment) as the `bots:` line."""

    def _adopted(self, tmp_path: Path, *extra: str):
        env = _door_env(tmp_path)
        target = tmp_path / "adopted"
        target.mkdir()
        subprocess.run(
            ["git", "init", "-q", "-b", "main", str(target)], check=True, timeout=30
        )
        first = run_door(
            "adopt", str(target), "--profile", "none", cwd=tmp_path, env=env
        )
        assert first.returncode == 0, first.stderr + first.stdout
        # the baseline record carries no evaluators: line
        assert "evaluators:" not in _region_of(target)
        return target, env

    def test_line_added_to_a_preserved_region(self, tmp_path):
        target, env = self._adopted(tmp_path)
        result = run_door(
            "adopt",
            str(target),
            "--without-evaluators",
            cwd=tmp_path,
            env=env,
        )
        assert result.returncode == 0, result.stderr + result.stdout
        assert "evaluators: no" in _region_of(target)

    def test_conflicting_answer_is_an_error_not_an_overwrite(self, tmp_path):
        target, env = self._adopted(tmp_path)
        assert (
            run_door(
                "adopt", str(target), "--without-evaluators", cwd=tmp_path, env=env
            ).returncode
            == 0
        )
        result = run_door(
            "adopt", str(target), "--with-evaluators", cwd=tmp_path, env=env
        )
        assert result.returncode != 0
        assert "conflicts with the recorded declaration" in (
            result.stdout + result.stderr
        )
        # the record is unchanged — never a silent overwrite
        assert "evaluators: no" in _region_of(target)

    def test_re_adopt_without_the_flag_does_not_duplicate(self, tmp_path):
        """o3 review (KIT-0118) predicted the engine would append an
        `evaluators:` line on every re-adopt once one exists, silently
        polluting the record. It does not — the append is gated on the
        flag being GIVEN, and a preserved region is never reseeded — but
        the claim is cheap to pin permanently.
        """
        target, env = self._adopted(tmp_path)
        assert (
            run_door(
                "adopt", str(target), "--without-evaluators", cwd=tmp_path, env=env
            ).returncode
            == 0
        )
        for _ in range(2):
            result = run_door("adopt", str(target), cwd=tmp_path, env=env)
            assert result.returncode == 0, result.stderr + result.stdout
        region = _region_of(target)
        assert region.count("evaluators:") == 1
        assert "evaluators: no" in region

    def test_repeating_the_same_answer_is_idempotent(self, tmp_path):
        target, env = self._adopted(tmp_path)
        for _ in range(2):
            result = run_door(
                "adopt", str(target), "--without-evaluators", cwd=tmp_path, env=env
            )
            assert result.returncode == 0, result.stderr + result.stdout
        region = _region_of(target)
        assert region.count("evaluators:") == 1


class TestLegacyRecordMigrationOnAdopt:
    """BugBot (PR #147): the ## Target Repository strip only cleans values
    on their way INTO a freshly seeded region. Adopt passes
    --preserve-regions, so a pre-KIT-0118 tree's EXISTING kit-install
    region kept its prose and `load_record()` went on returning an
    unusable path — a migration that looks complete and silently is not.
    """

    LEGACY_TP = "../<target-repo>  # TODO: set the product repo path"
    LEGACY_TG = "<owner>/<repo>  # TODO: set the product repo"

    def _legacy_tree(self, tmp_path: Path, tp: str, tg: str):
        env = _door_env(tmp_path)
        target = tmp_path / "legacy"
        target.mkdir()
        subprocess.run(
            ["git", "init", "-q", "-b", "main", str(target)], check=True, timeout=30
        )
        (target / "CLAUDE.md").write_text(
            "# Legacy Planning Repo\n\n"
            "## Target Repository\n\n"
            f"- **Path**: `{tp}`\n"
            f"- **GitHub**: `{tg}`\n\n"
            "<!-- BEGIN KIT-LOCAL: kit-install -->\n"
            "shape: planning\nprofile: none\n"
            f"target_path: {tp}\n"
            f"target_github: {tg}\n"
            "<!-- END KIT-LOCAL: kit-install -->\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "-C", str(target), "add", "-A"], check=True, timeout=30)
        subprocess.run(
            [
                "git",
                "-C",
                str(target),
                "-c",
                "user.email=t@t",
                "-c",
                "user.name=t",
                "commit",
                "-q",
                "-m",
                "legacy",
            ],
            check=True,
            timeout=60,
        )
        result = run_door(
            "adopt", str(target), "--shape", "planning", cwd=tmp_path, env=env
        )
        assert result.returncode == 0, result.stderr + result.stdout
        return target, result

    def test_prose_is_migrated_out_of_the_record(self, tmp_path):
        target, _ = self._legacy_tree(tmp_path, self.LEGACY_TP, self.LEGACY_TG)
        region = _region_of(target)
        assert "target_path: ../<target-repo>" in region
        assert "target_github: <owner>/<repo>" in region
        assert "TODO" not in region

    def test_migration_preserves_the_rest_of_the_record(self, tmp_path):
        """CodeRabbit (this PR): the migration rewrites the WHOLE region
        body through sed. Asserting only that the cleaned values appear
        and "TODO" is gone would stay green if the rewrite dropped
        `shape:`/`profile:` or truncated the last line — the record
        would silently lose fields while the tests passed.
        """
        from agentive_kit import door

        target, _ = self._legacy_tree(tmp_path, self.LEGACY_TP, self.LEGACY_TG)
        body = [ln.strip() for ln in _region_of(target).splitlines() if ln.strip()]
        assert body == [
            "shape: planning",
            "profile: none",
            "target_path: ../<target-repo>",
            "target_github: <owner>/<repo>",
        ]
        # and the reader agrees, field for field
        assert door.load_record(target) == {
            "shape": "planning",
            "profile": "none",
            "target_path": "../<target-repo>",
            "target_github": "<owner>/<repo>",
        }

    def test_load_record_returns_the_clean_value(self, tmp_path):
        # the actual defect: a machine reader getting an unusable path
        from agentive_kit import door

        target, _ = self._legacy_tree(tmp_path, self.LEGACY_TP, self.LEGACY_TG)
        record = door.load_record(target)
        assert record["target_path"] == "../<target-repo>"
        assert record["target_github"] == "<owner>/<repo>"

    def test_migration_is_announced_not_silent(self, tmp_path):
        # this is the one place the engine rewrites an existing recorded
        # VALUE in a consumer-owned region — it must say so
        _, result = self._legacy_tree(tmp_path, self.LEGACY_TP, self.LEGACY_TG)
        assert "legacy '# TODO' prose migrated" in result.stdout

    def test_real_values_with_a_hash_are_not_touched(self, tmp_path):
        # the over-reach guard: `../target #1` is the operator's real
        # path, not something this engine ever seeded
        from agentive_kit import door

        target, result = self._legacy_tree(tmp_path, "../target #1", "acme/product")
        assert door.load_record(target)["target_path"] == "../target #1"
        assert "legacy '# TODO' prose migrated" not in result.stdout

    def test_clean_record_is_left_alone(self, tmp_path):
        target, result = self._legacy_tree(tmp_path, "../product", "acme/product")
        region = _region_of(target)
        assert "target_path: ../product" in region
        assert "legacy '# TODO' prose migrated" not in result.stdout

    def test_migration_is_idempotent(self, tmp_path):
        target, _ = self._legacy_tree(tmp_path, self.LEGACY_TP, self.LEGACY_TG)
        env = _door_env(tmp_path)
        second = run_door(
            "adopt", str(target), "--shape", "planning", cwd=tmp_path, env=env
        )
        assert second.returncode == 0, second.stderr + second.stdout
        # already migrated — nothing left to do, and it says nothing
        assert "legacy '# TODO' prose migrated" not in second.stdout
        assert "TODO" not in _region_of(target)

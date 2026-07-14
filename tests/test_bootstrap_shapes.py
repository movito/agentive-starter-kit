"""Shape tests for bootstrap-consumer.sh (KIT-0048, ADR-0027 P2).

Characterization net first (N1): flagless and --shape single must stay
byte-identical to each other for every subsequent edit; the flagless
baseline invariants pin today's behavior.

Consumer-rsync boundary: this module reads scripts/local/ content, so it
is excluded from the consumer tests/ rsync in bootstrap-consumer.sh
(exclude + rm -f sweep) and module-skips when the script is absent —
the tests/test_kit_markers.py pattern.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP = REPO_ROOT / "scripts" / "local" / "bootstrap-consumer.sh"

if not BOOTSTRAP.exists():
    pytest.skip(
        "bootstrap-consumer.sh not present (consumer checkout)",
        allow_module_level=True,
    )

for tool in ("bash", "git", "rsync"):
    if shutil.which(tool) is None:
        pytest.skip(f"{tool} not available on PATH", allow_module_level=True)


def _scrubbed_env() -> dict[str, str]:
    """os.environ minus GIT_* — explicit defense in depth.

    These helpers run from CLASS-scoped fixtures, which execute outside
    the function-scoped conftest isolation; under the pre-commit hook the
    ambient GIT_DIR would otherwise redirect bootstrap's git calls at the
    REAL repository (the KIT-0048 corruption incident). The session-scoped
    conftest fixture now covers this too — this scrub makes the helpers
    safe regardless of who calls them from where.
    """
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def make_consumer_dir(base: Path, name: str) -> Path:
    """A scratch consumer dir, pre-inited so bootstrap skips git init
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


def run_bootstrap(target: Path, *flags: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(BOOTSTRAP), *flags, str(target)],
        capture_output=True,
        text=True,
        timeout=120,
        env=_scrubbed_env(),
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


class TestCharacterization:
    """N1: pin current flagless behavior; single must equal flagless."""

    def test_flagless_baseline_invariants(self, tmp_path):
        target = make_consumer_dir(tmp_path, "flagless")
        result = run_bootstrap(target)
        assert result.returncode == 0, result.stderr
        # today's single-shape contract: full Python toolchain ships
        for expected in (
            "pyproject.toml",
            "conftest.py",
            ".pre-commit-config.yaml",
            "scripts/core/project",
            "scripts/core/ci-check.sh",
            "scripts/core/pattern_lint.py",
            ".claude/agents/planner.md",
            ".claude/agents/feature-developer.md",
            ".kit/templates/TASK-STARTER-TEMPLATE.md",
        ):
            assert (target / expected).is_file(), f"missing: {expected}"
        assert (target / "tests").is_dir()
        assert (target / ".kit" / "tasks" / "1-backlog").is_dir()

    def test_shape_single_identical_to_flagless(self, tmp_path):
        # identical basenames: the marker-merge seeds placeholders with
        # the project name, so differing dir names would differ by design
        flagless = make_consumer_dir(tmp_path / "a", "app")
        single = make_consumer_dir(tmp_path / "b", "app")
        r1 = run_bootstrap(flagless)
        r2 = run_bootstrap(single, "--shape", "single")
        assert r1.returncode == 0, r1.stderr
        assert r2.returncode == 0, r2.stderr
        assert tree_snapshot(flagless) == tree_snapshot(single)

    def test_unknown_shape_rejected(self, tmp_path):
        target = make_consumer_dir(tmp_path, "bad")
        result = run_bootstrap(target, "--shape", "pyramid")
        assert result.returncode == 1
        assert "shape" in (result.stdout + result.stderr).lower()


# The planning contract, both directions (F1: enumerated, tested).
PLANNING_MUST_SHIP = (
    "scripts/core/project",
    "scripts/core/preflight-check.sh",
    "scripts/core/gh-review-helper.sh",
    "scripts/core/prepare-review-input.sh",
    "scripts/core/validate_task_status.py",
    "scripts/core/doctor.d/10-gh-auth.sh",
    "scripts/core/doctor.d/70-core-bare.sh",
    "scripts/core/VERSION",
    "scripts/local/kit_markers.py",
    "scripts/local/new-worktree.sh",
    ".claude/agents/planner.md",
    ".claude/agents/feature-developer.md",
    ".claude/commands/preflight.md",
    ".kit/templates/TASK-STARTER-TEMPLATE.md",
    ".adversarial/config.yml.template",
    ".pre-commit-config.yaml",
    ".env.template",
    ".gitignore",
    "CLAUDE.md",
    "scripts/.core-manifest.json",
)

PLANNING_MUST_NOT_SHIP = (
    "pyproject.toml",
    "conftest.py",
    "tests",
    "scripts/core/pattern_lint.py",
    "scripts/core/ci-check.sh",
    "scripts/core/verify-setup.sh",
    "scripts/optional",
    ".github",
    ".serena",
)


class TestPlanningShape:
    """F1/F2/F4: the planning install ships coordination, not toolchain."""

    @pytest.fixture(scope="class")
    def planning(self, tmp_path_factory):
        target = make_consumer_dir(tmp_path_factory.mktemp("shape"), "planning")
        result = run_bootstrap(
            target,
            "--shape",
            "planning",
            "--target-path",
            "../my-product",
            "--target-github",
            "acme/my-product",
        )
        assert result.returncode == 0, result.stderr + result.stdout
        return target

    @pytest.mark.parametrize("rel", PLANNING_MUST_SHIP)
    def test_ships(self, planning, rel):
        assert (planning / rel).exists(), f"planning shape missing: {rel}"

    @pytest.mark.parametrize("rel", PLANNING_MUST_NOT_SHIP)
    def test_never_ships(self, planning, rel):
        assert not (planning / rel).exists(), f"planning shape must not ship: {rel}"

    def test_kit_install_region_written(self, planning):
        text = (planning / "CLAUDE.md").read_text(encoding="utf-8")
        assert "<!-- BEGIN KIT-LOCAL: kit-install -->" in text
        assert "<!-- END KIT-LOCAL: kit-install -->" in text
        assert "shape: planning" in text
        assert "target_path: ../my-product" in text
        assert "target_github: acme/my-product" in text

    def test_target_repository_section_seeded(self, planning):
        text = (planning / "CLAUDE.md").read_text(encoding="utf-8")
        assert "## Target Repository" in text
        assert "- **Path**: `../my-product`" in text
        assert "- **GitHub**: `acme/my-product`" in text

    def test_precommit_variant_is_python_free(self, planning):
        text = (planning / ".pre-commit-config.yaml").read_text(encoding="utf-8")
        assert "validate-task-status" in text
        assert "black" not in text
        assert "pytest" not in text
        assert "flake8" not in text

    def test_manifest_matches_planning_shipset(self, planning):
        import json

        manifest = json.loads(
            (planning / "scripts" / ".core-manifest.json").read_text(encoding="utf-8")
        )
        entries = manifest["files"]["scripts_core"]
        assert "core/project" in entries
        assert "core/preflight-check.sh" in entries
        assert "core/ci-check.sh" not in entries
        assert "core/pattern_lint.py" not in entries

    def test_kit_agents_still_marker_merged(self, planning):
        text = (planning / ".claude" / "agents" / "planner.md").read_text(
            encoding="utf-8"
        )
        assert "BEGIN KIT-LOCAL" in text

    def test_placeholder_pointer_without_flags(self, tmp_path):
        target = make_consumer_dir(tmp_path, "noflags")
        result = run_bootstrap(target, "--shape", "planning")
        assert result.returncode == 0, result.stderr
        text = (target / "CLAUDE.md").read_text(encoding="utf-8")
        assert "shape: planning" in text
        assert "target_path:" in text  # placeholder form present

    def test_existing_claude_md_gains_region_keeps_content(self, tmp_path):
        target = make_consumer_dir(tmp_path, "existing")
        (target / "CLAUDE.md").write_text(
            "# My Planning Repo\n\nHand-written intro.\n", encoding="utf-8"
        )
        result = run_bootstrap(target, "--shape", "planning")
        assert result.returncode == 0, result.stderr
        text = (target / "CLAUDE.md").read_text(encoding="utf-8")
        assert "Hand-written intro." in text
        assert "shape: planning" in text

    def test_target_values_written_literally_no_expansion(self, tmp_path):
        """claude-code review: $(...) in operator-supplied pointer values
        must be written literally, never shell-expanded."""
        target = make_consumer_dir(tmp_path, "hostile")
        marker = tmp_path / "pwned"
        result = run_bootstrap(
            target,
            "--shape",
            "planning",
            "--target-path",
            f"../x$(touch {marker})",
        )
        assert result.returncode == 0, result.stderr
        assert not marker.exists(), "command substitution executed!"
        text = (target / "CLAUDE.md").read_text(encoding="utf-8")
        assert "$(touch" in text  # literal, unexpanded

    def test_malformed_target_github_rejected(self, tmp_path):
        target = make_consumer_dir(tmp_path, "badgh")
        result = run_bootstrap(
            target, "--shape", "planning", "--target-github", "not a repo slug"
        )
        assert result.returncode == 1
        assert "owner/repo" in result.stdout + result.stderr

    def test_existing_section_seeds_region_no_desync(self, tmp_path):
        """BugBot PR #78: with a pre-existing ## Target Repository, the
        kit-install region must seed FROM it — never from placeholders."""
        target = make_consumer_dir(tmp_path, "seeded")
        (target / "CLAUDE.md").write_text(
            "# Repo\n\n## Target Repository\n\n"
            "- **Path**: `../real-product`\n"
            "- **GitHub**: `real/product`\n",
            encoding="utf-8",
        )
        result = run_bootstrap(target, "--shape", "planning")
        assert result.returncode == 0, result.stderr
        text = (target / "CLAUDE.md").read_text(encoding="utf-8")
        assert "target_path: ../real-product" in text
        assert "target_github: real/product" in text

    def test_prose_padded_section_still_seeds_region(self, tmp_path):
        """BugBot round 2: bullets after introductory prose must still
        be found (whole-section extraction, not a fixed -A window)."""
        target = make_consumer_dir(tmp_path, "prose")
        (target / "CLAUDE.md").write_text(
            "# Repo\n\n## Target Repository\n\n"
            "This planning repo coordinates the product repo below.\n"
            "All code changes happen there; specs and reviews live here.\n"
            "See docs/CROSS-REPO-PATTERN.md for the full pattern.\n\n"
            "- **Path**: `../prose-product`\n"
            "- **GitHub**: `prose/product`\n\n"
            "## Another Section\n\n- **Path**: `../decoy`\n",
            encoding="utf-8",
        )
        result = run_bootstrap(target, "--shape", "planning")
        assert result.returncode == 0, result.stderr
        text = (target / "CLAUDE.md").read_text(encoding="utf-8")
        assert "target_path: ../prose-product" in text
        assert "../decoy" not in text.split("kit-install")[1]

    def test_shape_flag_as_last_arg_is_clean_usage_error(self):
        """CodeRabbit round 2: a value-consuming flag in TRULY final
        position must produce the validation message, not a silent
        set -e death — no target argument after the flag (the helper
        would append one, exercising the wrong branch; round 4)."""
        result = subprocess.run(
            ["bash", str(BOOTSTRAP), "--shape"],
            capture_output=True,
            text=True,
            timeout=60,
            env=_scrubbed_env(),
        )
        assert result.returncode == 1
        assert "unknown shape" in (result.stdout + result.stderr).lower()

    def test_conflicting_flags_with_existing_section_rejected(self, tmp_path):
        target = make_consumer_dir(tmp_path, "conflict")
        (target / "CLAUDE.md").write_text(
            "# Repo\n\n## Target Repository\n\n"
            "- **Path**: `../real-product`\n"
            "- **GitHub**: `real/product`\n",
            encoding="utf-8",
        )
        result = run_bootstrap(
            target, "--shape", "planning", "--target-path", "../other-product"
        )
        assert result.returncode == 1
        assert "conflicts" in result.stdout + result.stderr

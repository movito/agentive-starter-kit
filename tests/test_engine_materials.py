"""
Materials-engine copy-boundary tests (KIT-0068 A12/A13).

Runs engine-materials.sh in --scaffold-only mode against a scratch
target and pins what must NOT ship: scripts/local/ (the door's own
contract says it "never ships on any sync tier or consumer rsync"),
the kit-only tests that import it, the kit's planning corpus
(task specs and task-ID context files, prefix-agnostic), and the
operator-owned .kit/adversarial/.

Kit-only module: imports nothing from scripts/local/ but READS the
engine, so it is excluded from both consumer copy paths
(engine-consumer.sh and engine-materials.sh tests/ excludes) and
module-skips on consumer checkouts.
"""

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE = REPO_ROOT / "scripts" / "local" / "engine-materials.sh"

if not ENGINE.exists():
    pytest.skip("scripts/local absent (consumer checkout)", allow_module_level=True)


@pytest.fixture(scope="module")
def export(tmp_path_factory):
    """One scaffold-only export shared by all assertions."""
    target = tmp_path_factory.mktemp("materials-target")
    result = subprocess.run(
        ["bash", str(ENGINE), str(target), "--scaffold-only"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return target, result


def test_scripts_local_not_shipped(export):
    target, _ = export
    assert not (target / "scripts" / "local").exists(), (
        "scripts/local/ shipped into a materials export — the door's"
        " contract says it never ships (KIT-0068 A12)"
    )
    # the layers that DO ship are still there
    assert (target / "scripts" / "core" / "project").exists()
    assert (target / "scripts" / "optional").is_dir()


def test_kit_only_tests_not_shipped(export):
    target, _ = export
    kit_only = [
        "test_kit_markers.py",
        "test_bootstrap_consumer.py",
        "test_bootstrap_shapes.py",
        "test_bots_conformance.py",
        "test_check_hook_seeds.py",
        "test_entrance_shims.py",
        "test_setup_door.py",
        "test_engine_materials.py",
    ]
    shipped = [n for n in kit_only if (target / "tests" / n).exists()]
    assert not shipped, (
        f"kit-only tests shipped (would break consumer pytest at"
        f" collection): {shipped}"
    )
    assert (target / "tests" / "conftest.py").exists()


def test_no_task_id_files_in_kit_dirs(export):
    """No PREFIX-NNNN task specs or context files, any prefix — the
    ASK-* literals missed every KIT-* file after the rename (A13)."""
    import re

    target, _ = export
    leaked = []
    for base in [target / ".kit" / "tasks", target / ".kit" / "context"]:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and re.match(r"^[A-Z]+-\d{4}", path.name):
                leaked.append(str(path.relative_to(target)))
    assert not leaked, f"kit planning corpus leaked into export: {leaked}"


def test_kit_adversarial_not_shipped(export):
    target, _ = export
    assert not (target / ".kit" / "adversarial").exists(), (
        ".kit/adversarial/ is operator-owned untracked state and must"
        " not be copied (KIT-0068 A13)"
    )


def test_exclusions_are_named_in_output(export):
    """intersection_names_drops: the engine must SAY what it dropped."""
    _, result = export
    assert "Not copied" in result.stdout
    assert "scripts/local/" in result.stdout

"""Cross-reader conformance for the bots declaration (KIT-0056 retro #2).

ONE fixture table run through all three readers of the kit-install
``bots:`` record — the setup door (``normalize_bots`` over
``record_field``), the project script (``_doctor_install`` /
``_normalize_bots``), and ``preflight-check.sh`` (Gates 2/3) — asserting
they agree on validity and on the effective token set. KIT-0056's five
reviewers found five faces of one seams-between-readers class; pairwise
pins keep leaking, so this harness closes the class: add a case here and
every reader must face it.

Duplicate ``bots:`` keys are FIRST-match-wins in every reader — lenient
BY DESIGN, the blessed contract (patterns.yml
``record_duplicate_keys_first_wins``). The duplicate-key rows pin it;
do not re-litigate it here.

Divergence note: on an invalid declaration the project and preflight
readers fail closed to "both bots expected", while the door refuses
(usage error) or treats an empty value as unanswered and asks the
operator. All three agree the declaration is NOT valid — that validity
agreement is the contract; the door has no fail-closed effective set to
compare.
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess  # noqa: F401  (documents what the adapters shell out to)
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DOOR = REPO_ROOT / "scripts" / "local" / "bootstrap"
KIT_MARKERS = REPO_ROOT / "scripts" / "local" / "kit_markers.py"
PROJECT_SCRIPT = REPO_ROOT / "scripts" / "core" / "project"

# scripts/local is an ASK-only layer, never synced to consumers. The
# consumer sync also excludes this test (engine-consumer.sh tests/
# excludes); the guard makes a stray copy skip cleanly at collection.
if not DOOR.exists() or not KIT_MARKERS.exists():
    pytest.skip("scripts/local absent (consumer checkout)", allow_module_level=True)

from test_preflight_check import proj  # noqa: E402,F401  (fixture re-export)
from test_preflight_check import _baseline, _gates, _graphql  # noqa: E402
from test_setup_door import _scrubbed_env, sourced  # noqa: E402

# The project script is extensionless — exec it as a module, the
# test_project_script.py pattern (distinct module name: no collision).
_spec = importlib.util.spec_from_loader("project_script_conformance", loader=None)
_pm = importlib.util.module_from_spec(_spec)
_pm.__dict__["__file__"] = str(PROJECT_SCRIPT)
exec(PROJECT_SCRIPT.read_text(encoding="utf-8"), _pm.__dict__)

BOTH = frozenset({"coderabbit", "bugbot"})

# (case id, bots: line values in region order, valid?, effective set)
# The effective set is "which bots are expected to review": a valid
# declaration yields its declared set (none -> empty); an invalid one
# fails closed to BOTH in the readers that carry on (project, preflight).
ROWS = [
    ("none", ["none"], True, frozenset()),
    ("coderabbit-only", ["coderabbit"], True, frozenset({"coderabbit"})),
    ("bugbot-only", ["bugbot"], True, frozenset({"bugbot"})),
    ("both-plain", ["coderabbit bugbot"], True, BOTH),
    ("case-comma-order", ["BugBot, CodeRabbit"], True, BOTH),
    ("duplicate-tokens", ["bugbot bugbot"], True, frozenset({"bugbot"})),
    ("unknown-token", ["horsebot"], False, BOTH),
    ("none-plus-bot", ["none coderabbit"], False, BOTH),
    ("lone-comma", [","], False, BOTH),
    ("empty-value", [""], False, BOTH),
    ("dup-key-none-first", ["none", "coderabbit bugbot"], True, frozenset()),
    ("dup-key-subset-first", ["coderabbit", "none"], True, frozenset({"coderabbit"})),
    ("dup-key-invalid-first", ["horsebot", "none"], False, BOTH),
]


def _region(lines: list[str]) -> str:
    body = "shape: single\nprofile: python\n"
    for value in lines:
        body += f"bots: {value}".rstrip() + "\n"
    return (
        "<!-- BEGIN KIT-LOCAL: kit-install -->\n"
        f"{body}"
        "<!-- END KIT-LOCAL: kit-install -->\n"
    )


def _project_verdict(tmp_path: Path, lines: list[str]) -> tuple[bool, frozenset]:
    """The project script's reading: _doctor_install over a stub record."""
    root = tmp_path / "project-reader"
    (root / "scripts" / "local").mkdir(parents=True)
    shutil.copy(KIT_MARKERS, root / "scripts" / "local" / "kit_markers.py")
    (root / "CLAUDE.md").write_text("# stub\n\n" + _region(lines), encoding="utf-8")
    _shape, _profile, bots, errors = _pm._doctor_install(root)
    # membership: scanning the error list for the bots record, not
    # comparing one identifier
    if any(record == "bots-record" for record, _detail in errors):
        return False, BOTH
    if bots == "none":
        return True, frozenset()
    assert bots is not None, "every table row carries a bots: line"
    return True, frozenset(bots.split())


def _preflight_verdict(proj, lines: list[str]) -> tuple[bool, frozenset]:
    """preflight-check.sh's reading: Gate 2/3 verdicts with no bot
    activity anywhere — expected bots FAIL, declared-absent bots SKIP."""
    local_dir = proj.root / "scripts" / "local"
    local_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(KIT_MARKERS, local_dir / "kit_markers.py")
    (proj.root / "CLAUDE.md").write_text(
        "# stub\n\n" + _region(lines), encoding="utf-8"
    )
    try:
        files = _baseline(proj.head)
        files["graphql"] = _graphql([], resolved=0)
        result = proj.run(files)
        gates = _gates(result.stdout)
        invalid = (
            "NOTICE: invalid bots declaration" in result.stdout
            or "NOTICE: empty bots declaration" in result.stdout
        )
        expected = frozenset(
            bot
            for gate, bot in ((2, "coderabbit"), (3, "bugbot"))
            if gates[gate][0] != "SKIP"
        )
        return (not invalid), expected
    finally:
        (proj.root / "CLAUDE.md").unlink(missing_ok=True)
        (local_dir / "kit_markers.py").unlink(missing_ok=True)


def _door_verdict(lines: list[str]) -> tuple[bool, frozenset | None]:
    """The door's reading: record_field (first key wins) + normalize_bots.

    Returns (False, None) for a not-valid declaration — the door refuses
    or re-asks instead of failing closed, so there is no effective set.
    """
    env = _scrubbed_env()
    env["CONF_REGION"] = _region(lines)
    result = sourced(
        'raw="$(record_field "$CONF_REGION" bots)"; normalize_bots "$raw"',
        env=env,
    )
    if result.returncode != 0:
        return False, None
    canonical = result.stdout.strip()
    if canonical == "none":
        return True, frozenset()
    return True, frozenset(canonical.split())


@pytest.mark.parametrize(
    "case_id,lines,valid,effective", ROWS, ids=[row[0] for row in ROWS]
)
def test_three_readers_agree(case_id, lines, valid, effective, proj, tmp_path):
    project_valid, project_set = _project_verdict(tmp_path, lines)
    preflight_valid, preflight_set = _preflight_verdict(proj, lines)
    door_valid, door_set = _door_verdict(lines)

    assert project_valid == valid, f"{case_id}: project reader disagrees on validity"
    assert preflight_valid == valid, f"{case_id}: preflight disagrees on validity"
    assert door_valid == valid, f"{case_id}: door disagrees on validity"

    assert project_set == effective, f"{case_id}: project effective set"
    assert preflight_set == effective, f"{case_id}: preflight effective set"
    if door_valid:
        assert door_set == effective, f"{case_id}: door effective set"

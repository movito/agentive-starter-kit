"""Door data-store sync guard (KIT-0104).

The packaged door ships the two engines and the scaffold content as
package data (``agentive_kit/door/``) while the kit tree keeps its own
working copies — a deliberate, time-boxed duplication (arch-review
disposition, KIT-0104 spec header) whose filed exit is the
engine-consolidation follow-up. Until that lands, THIS test is what
makes the duplication safe: every packaged copy must stay
byte-identical to its kit-tree source, in both directions.

When this test fails, mirror the edit to the other side in the SAME
commit — the sync manifest is ``agentive_kit.door._SYNC_SOURCES``.

Kit-repo-only by construction: module-skips in consumer checkouts
(no scripts/local/) and wherever the package source is absent.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

if not (REPO_ROOT / "scripts" / "local" / "bootstrap").exists():
    pytest.skip("setup door present only in the kit repo", allow_module_level=True)

pytest.importorskip(
    "agentive_kit", reason="agentive-kit package source present only in the kit repo"
)

from agentive_kit import door  # noqa: E402


def _pairs():
    return [
        pytest.param(repo_rel, pkg_path, id=repo_rel)
        for repo_rel, pkg_path in door.sync_pairs()
    ]


@pytest.mark.parametrize("repo_rel,pkg_path", _pairs())
def test_packaged_copy_matches_kit_source(repo_rel, pkg_path):
    source = REPO_ROOT / repo_rel
    assert source.is_file(), (
        f"packaged copy {pkg_path} has no kit-tree source at {repo_rel} — "
        "remove the copy or restore the source (and update _SYNC_SOURCES)"
    )
    assert source.read_bytes() == pkg_path.read_bytes(), (
        f"door data drift: {repo_rel} differs from its packaged copy "
        f"{pkg_path} — mirror the edit to both sides in the same commit"
    )


def test_no_kit_source_file_missing_from_the_package():
    """Reverse direction: a file ADDED to a directory-mapped kit-tree
    source (a new workflow doc, a new adversarial template) must ship
    in the wheel too — an addition the package misses would produce
    scaffolds missing content the kit's own tree carries."""
    packaged = {repo_rel for repo_rel, _ in door.sync_pairs()}
    missing = []
    for pkg_rel, repo_rel in door._SYNC_SOURCES.items():
        source = REPO_ROOT / repo_rel
        if not source.is_dir():
            continue
        for child in sorted(source.rglob("*")):
            if child.is_file():
                rel = f"{repo_rel}/{child.relative_to(source)}"
                if rel not in packaged:
                    missing.append(rel)
    assert not missing, (
        f"kit-tree files missing from the packaged door data: {missing} — "
        "copy them into agentive_kit/door/ (and they ship automatically)"
    )

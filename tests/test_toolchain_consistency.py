"""
Toolchain consistency pins (KIT-0068, two-homes rule).

A fact that lives in two places gets a consistency TEST, not a prose
promise of alignment:

- Black version: .pre-commit-config.yaml rev vs pyproject.toml pin
  (A84 — they diverged silently on a dependabot bump, so local commits
  formatted with a different Black than CI)
- flake8 args: scripts/core/ci-check.sh vs .github/workflows/test.yml
  (A91 — ci-check claims to mirror CI; a divergent exclude made an
  error class pass one gate and fail the other)
- ruff invocation: scripts/core/ci-check.sh vs .github/workflows/test.yml
  (A88 — ruff was declared on three surfaces and run on zero; now that
  it runs, the two runners must run the same thing)
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PRE_COMMIT = REPO_ROOT / ".pre-commit-config.yaml"
PYPROJECT = REPO_ROOT / "pyproject.toml"
CI_CHECK = REPO_ROOT / "scripts" / "core" / "ci-check.sh"
TEST_YML = REPO_ROOT / ".github" / "workflows" / "test.yml"


def _read(path):
    return path.read_text(encoding="utf-8")


def test_black_pre_commit_rev_matches_pyproject_pin():
    pyproject_pin = re.search(r'"black==([0-9][0-9A-Za-z.]*)"', _read(PYPROJECT))
    assert pyproject_pin, "pyproject.toml must carry an exact black== pin"

    pre_commit = _read(PRE_COMMIT)
    block = re.search(
        r"repo: https://github\.com/psf/black\s*\n\s*rev: ([0-9][0-9A-Za-z.]*)",
        pre_commit,
    )
    assert block, "pre-commit config must pin a black rev"

    assert block.group(1) == pyproject_pin.group(1), (
        f"Black drift: pre-commit rev {block.group(1)} vs pyproject pin"
        f" {pyproject_pin.group(1)} — local commits would format with a"
        f" different Black than CI (KIT-0068 A84). Bump them together."
    )


def _flake8_args(text):
    """The argument string after `flake8 ` on the invocation line."""
    match = re.search(r"flake8 (scripts/[^\n]*)", text)
    assert match, "no flake8 invocation found"
    # ci-check wraps the command in an `if ...; then` and silences
    # stderr; strip shell tail so only flake8's own args compare.
    args = match.group(1)
    args = re.sub(r"\s*2>/dev/null.*$", "", args)
    args = re.sub(r"\s*;\s*then\s*$", "", args)
    return args.strip()


def test_flake8_args_match_ci():
    local = _flake8_args(_read(CI_CHECK))
    ci = _flake8_args(_read(TEST_YML))
    assert local == ci, (
        f"flake8 drift (KIT-0068 A91):\n  ci-check.sh: {local}\n"
        f"  test.yml:    {ci}\nci-check.sh claims to mirror CI —"
        f" keep the argument lists byte-identical."
    )


def _ruff_args(text):
    """The argument string after `ruff ` on the actual invocation line
    (anchored to a command position so comments/echo lines never match)."""
    match = re.search(
        r"(?m)^\s*(?:if\s+)?(?:python3\s+-m\s+)?ruff\s+(check\s+[^\n]*)",
        text,
    )
    assert match, "no ruff invocation found"
    args = match.group(1)
    args = re.sub(r"\s*2>/dev/null.*$", "", args)
    args = re.sub(r"\s*;\s*then\s*$", "", args)
    return args.strip()


def test_ruff_invocation_matches_ci():
    local = _ruff_args(_read(CI_CHECK))
    ci = _ruff_args(_read(TEST_YML))
    assert local == ci, (
        f"ruff drift (KIT-0068 A88):\n  ci-check.sh: {local}\n"
        f"  test.yml:    {ci}\nthe two runners must run the same check."
    )

"""Parity matrix for the review-input assembly surface (KIT-0091 F2).

Runs the REAL implementation against throwaway git repos: scenarios per
gate — argument validation, diff/full formats, the ID2-0047 lockfile
skip, binary/empty/deleted file handling, fence integrity, and the
ID2-0014 cross-repo routing. Committed against the bash original
BEFORE the Python port exists; the port must reproduce it (parity
binds behavior, not code shape).

Implementation parameter (the test_preflight_check.py pattern):

- ``bash``   — scripts/core/prepare-review-input.sh (after the KIT-0091
               shim lands, this drives the shim end-to-end)
- ``python`` — agentive_kit.review_input in-process (skip-marked until
               the port commit enables it)
"""

from __future__ import annotations

import contextlib
import io
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = REPO_ROOT / "scripts" / "core" / "prepare-review-input.sh"
_TARGET_REPO_LIB = REPO_ROOT / "scripts" / "core" / "lib" / "target_repo.sh"
_PKG_SRC = REPO_ROOT / "packages" / "agentive-kit" / "src"

if not _SCRIPT.exists() or not _TARGET_REPO_LIB.exists():
    # both are fixture inputs — a checkout missing either must skip
    # cleanly, not error in fixture setup (CodeRabbit, PR #113)
    pytest.skip(
        "prepare-review-input.sh or lib/target_repo.sh not present in this checkout",
        allow_module_level=True,
    )

for tool in ("bash", "git"):
    if shutil.which(tool) is None:
        pytest.skip(f"{tool} not available on PATH", allow_module_level=True)

TASK = "KIT-7777"
BASELINE_CLAUDE_MD = "# stub project\n"


def _clean_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    if _PKG_SRC.is_dir():
        inherited = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            f"{_PKG_SRC}{os.pathsep}{inherited}" if inherited else str(_PKG_SRC)
        )
    return env


class ReviewInputProject:
    """Temp project skeleton around the real prepare-review-input.sh."""

    def __init__(self, root: Path, env: dict[str, str], impl: str):
        self.root = root
        self.env = env
        self.impl = impl

    def git(self, *args: str, cwd: Path | None = None) -> None:
        subprocess.run(
            ["git", *args],
            cwd=cwd or self.root,
            env=self.env,
            check=True,
            capture_output=True,
            timeout=30,
        )

    @property
    def output_file(self) -> Path:
        return self.root / ".adversarial" / "inputs" / f"{TASK}-code-review-input.md"

    def run(self, *args: str) -> subprocess.CompletedProcess:
        if self.impl == "python":
            return self._run_python(list(args))
        return subprocess.run(
            [
                "bash",
                str(self.root / "scripts" / "core" / "prepare-review-input.sh"),
                *args,
            ],
            cwd=self.root,
            env=self.env,
            capture_output=True,
            text=True,
            timeout=60,
        )

    def _run_python(self, argv: list[str]) -> subprocess.CompletedProcess:
        from agentive_kit import review_input as mod

        out, err = io.StringIO(), io.StringIO()
        prev_cwd = os.getcwd()
        try:
            os.chdir(self.root)
            with (
                # clear=True so the module sees the same scrubbed env
                # the bash subprocess gets
                pytest.MonkeyPatch.context() as mp,
            ):
                for key in list(os.environ):
                    if key.startswith("GIT_"):
                        mp.delenv(key, raising=False)
                mp.setenv("GIT_CONFIG_GLOBAL", os.devnull)
                mp.setenv("GIT_CONFIG_SYSTEM", os.devnull)
                with (
                    contextlib.redirect_stdout(out),
                    contextlib.redirect_stderr(err),
                ):
                    rc = 0
                    try:
                        mod.main(argv)
                    except SystemExit as exc:
                        if exc.code is None:
                            rc = 0
                        elif isinstance(exc.code, int):
                            rc = exc.code
                        else:
                            rc = 1
        finally:
            os.chdir(prev_cwd)
        return subprocess.CompletedProcess(
            ["agentive-review-input", *argv], rc, out.getvalue(), err.getvalue()
        )


@pytest.fixture(params=["bash", "python"])
def proj(request, tmp_path):
    impl = request.param
    if impl == "python":
        pytest.importorskip(
            "agentive_kit",
            reason="agentive-kit package source present only in the kit repo",
        )
        import importlib.util

        if importlib.util.find_spec("agentive_kit.review_input") is None:
            pytest.skip(
                "KIT-0091: agentive_kit.review_input not yet present — "
                "the parity matrix runs bash-only until the port lands"
            )
    root = tmp_path / "proj"
    core = root / "scripts" / "core"
    (core / "lib").mkdir(parents=True)
    shutil.copy(_SCRIPT, core / "prepare-review-input.sh")
    shutil.copy(_TARGET_REPO_LIB, core / "lib" / "target_repo.sh")
    (root / ".kit").mkdir()
    (root / "CLAUDE.md").write_text(BASELINE_CLAUDE_MD, encoding="utf-8")

    env = _clean_env()
    p = ReviewInputProject(root, env, impl)
    p.git("init", "-q", "-b", "main")
    p.git("config", "user.email", "t@t")
    p.git("config", "user.name", "t")
    (root / "seed.py").write_text("seed = 1\n", encoding="utf-8")
    p.git("add", "-A")
    p.git("commit", "-qm", "seed")
    p.git("checkout", "-q", "-b", f"feature/{TASK}-stub")
    (root / "code.py").write_text("x = 1\n", encoding="utf-8")
    p.git("add", "code.py")
    p.git("commit", "-qm", "feat: code change")
    return p


# ── Happy paths ──────────────────────────────────────────────────────────
class TestFullFormat:
    def test_full_output_structure(self, proj):
        result = proj.run(TASK)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "Wrote:" in result.stdout
        text = proj.output_file.read_text(encoding="utf-8")
        assert f"# Code Review: {TASK}" in text
        assert "## Changed Files" in text
        assert "## Diff" in text
        assert "````diff" in text  # 4-backtick outer fence
        assert "## Full File Contents" in text
        assert "### Source: `code.py`" in text
        assert "````python" in text
        assert "- **Base branch**: `main`" in text
        assert f"- **Head branch**: `feature/{TASK}-stub`" in text
        assert "- **Format**: `full`" in text
        assert "- **Target repo**: (single-repo / current)" in text

    def test_diff_format_omits_full_contents(self, proj):
        result = proj.run(TASK, "--format", "diff")
        assert result.returncode == 0, result.stdout + result.stderr
        text = proj.output_file.read_text(encoding="utf-8")
        assert "## Diff" in text
        assert "## Full File Contents" not in text

    def test_non_tty_next_steps_carry_unattended_prefix(self, proj):
        # stdout is captured (non-TTY), so the belt-and-braces prefix
        # must appear in the printed next steps.
        result = proj.run(TASK)
        assert "ADVERSARIAL_UNATTENDED=1" in result.stdout

    def test_changed_file_count_reported(self, proj):
        result = proj.run(TASK)
        assert "Files changed: 1" in result.stdout


# ── Argument validation ──────────────────────────────────────────────────
class TestArgValidation:
    def test_missing_task_id(self, proj):
        result = proj.run()
        assert result.returncode == 1
        assert "TASK-ID" in result.stderr

    def test_malformed_task_id(self, proj):
        result = proj.run("bad_id")
        assert result.returncode == 1
        assert "must look like" in result.stderr

    def test_alnum_suffix_task_id_accepted(self, proj):
        # ABC-TEST shape is explicitly legal (the bash regex allows an
        # alphanumeric suffix segment)
        result = proj.run("ABC-TEST", "--format", "diff")
        assert result.returncode == 0, result.stdout + result.stderr

    def test_invalid_format(self, proj):
        result = proj.run(TASK, "--format", "yaml")
        assert result.returncode == 1
        assert "'diff' or 'full'" in result.stderr

    def test_repo_flag_refused(self, proj):
        result = proj.run(TASK, "--repo", "owner/name")
        assert result.returncode == 1
        assert "--repo is not supported" in result.stderr

    def test_unknown_option(self, proj):
        result = proj.run(TASK, "--bogus")
        assert result.returncode == 1
        assert "Unknown option" in result.stderr

    def test_unexpected_positional(self, proj):
        result = proj.run(TASK, "EXTRA-1")
        assert result.returncode == 1
        assert "Unexpected positional" in result.stderr

    def test_missing_base_branch(self, proj):
        result = proj.run(TASK, "--base", "develop")
        assert result.returncode == 1
        assert "not found" in result.stderr

    def test_empty_base_equals_refused(self, proj):
        result = proj.run(TASK, "--base=")
        assert result.returncode == 1
        assert "--base= requires a branch name" in result.stderr

    def test_empty_format_equals_refused(self, proj):
        # an empty --format= falls through to the diff|full vocabulary
        # check (the bash original had no dedicated empty-value error)
        result = proj.run(TASK, "--format=")
        assert result.returncode == 1
        assert "'diff' or 'full'" in result.stderr


# ── Content edge cases ───────────────────────────────────────────────────
class TestContentEdges:
    def test_no_diff_warns_but_succeeds(self, proj):
        proj.git("checkout", "-q", "main")
        result = proj.run(TASK)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "WARNING: No diff" in result.stderr
        text = proj.output_file.read_text(encoding="utf-8")
        assert "(no changes detected)" in text

    def test_lockfile_diff_kept_content_skipped(self, proj):
        (proj.root / "package-lock.json").write_text(
            '{"lockfileVersion": 3}\n', encoding="utf-8"
        )
        proj.git("add", "package-lock.json")
        proj.git("commit", "-qm", "chore: lockfile")
        result = proj.run(TASK)
        assert result.returncode == 0, result.stdout + result.stderr
        text = proj.output_file.read_text(encoding="utf-8")
        assert "[lockfile skipped: package-lock.json]" in text
        # the diff itself still carries the lockfile change
        assert "lockfileVersion" in text

    def test_empty_file_skipped_with_note(self, proj):
        (proj.root / "empty.py").write_text("", encoding="utf-8")
        proj.git("add", "empty.py")
        proj.git("commit", "-qm", "feat: empty file")
        result = proj.run(TASK)
        assert result.returncode == 0
        text = proj.output_file.read_text(encoding="utf-8")
        assert "(empty file, 0 bytes — skipped)" in text

    def test_binary_file_skipped_with_note(self, proj):
        (proj.root / "blob.bin").write_bytes(b"\x00\x01\x02\xff")
        proj.git("add", "blob.bin")
        proj.git("commit", "-qm", "feat: binary")
        result = proj.run(TASK)
        assert result.returncode == 0
        text = proj.output_file.read_text(encoding="utf-8")
        assert "binary file" in text
        assert "skipped" in text

    def test_deleted_file_absent_from_full_contents(self, proj):
        proj.git("rm", "-q", "seed.py")
        proj.git("commit", "-qm", "feat: delete seed")
        result = proj.run(TASK)
        assert result.returncode == 0
        text = proj.output_file.read_text(encoding="utf-8")
        assert "### Source: `seed.py`" not in text
        # but the deletion is visible in the name-status block
        assert "seed.py" in text

    def test_markdown_with_triple_backticks_stays_fenced(self, proj):
        (proj.root / "notes.md").write_text(
            "# Notes\n\n```python\nx = 1\n```\n", encoding="utf-8"
        )
        proj.git("add", "notes.md")
        proj.git("commit", "-qm", "docs: fenced content")
        result = proj.run(TASK)
        assert result.returncode == 0
        text = proj.output_file.read_text(encoding="utf-8")
        # the outer 4-backtick fence must survive embedded triple
        # backticks — the markdown section opens with ````markdown
        assert "````markdown" in text


# ── Cross-repo routing (ID2-0014/ID2-0015) ───────────────────────────────
class TestCrossRepo:
    def _configure_target(self, proj, path_value: str) -> None:
        (proj.root / "CLAUDE.md").write_text(
            "# stub project\n\n"
            "## Target Repository\n\n"
            f"- **Path**: `{path_value}`\n"
            "- **GitHub**: `owner/target-repo`\n",
            encoding="utf-8",
        )

    def _make_target(self, proj, name: str = "target") -> Path:
        target = proj.root.parent / name
        target.mkdir()
        proj.git("init", "-q", "-b", "main", cwd=target)
        proj.git("config", "user.email", "t@t", cwd=target)
        proj.git("config", "user.name", "t", cwd=target)
        (target / "app.py").write_text("app = 1\n", encoding="utf-8")
        proj.git("add", "-A", cwd=target)
        proj.git("commit", "-qm", "seed", cwd=target)
        proj.git("checkout", "-q", "-b", f"feature/{TASK}-target", cwd=target)
        (target / "feature.py").write_text("f = 1\n", encoding="utf-8")
        proj.git("add", "feature.py", cwd=target)
        proj.git("commit", "-qm", "feat: target change", cwd=target)
        return target

    def test_valid_target_diffs_target_tree(self, proj):
        target = self._make_target(proj)
        self._configure_target(proj, "../target")
        result = proj.run(TASK)
        assert result.returncode == 0, result.stdout + result.stderr
        text = proj.output_file.read_text(encoding="utf-8")
        assert "- **Target repo**: `owner/target-repo`" in text
        assert "### Source: `feature.py`" in text
        assert "### Source: `code.py`" not in text
        # output still lands in the PLANNING repo
        assert proj.output_file.is_relative_to(proj.root)
        # the diff-source label echoes the CONFIGURED path verbatim
        # (bash keeps TARGET_PATH relative, it never absolutizes)
        assert "../target" in result.stdout
        assert target.is_dir()

    def test_whitespace_target_path_refused(self, proj):
        self._configure_target(proj, "../my target")
        result = proj.run(TASK)
        assert result.returncode == 1
        assert "contains whitespace" in result.stderr

    def test_non_git_target_path_refused(self, proj):
        (proj.root.parent / "not-a-repo").mkdir()
        self._configure_target(proj, "../not-a-repo")
        result = proj.run(TASK)
        assert result.returncode == 1
        assert "not a git working tree" in result.stderr

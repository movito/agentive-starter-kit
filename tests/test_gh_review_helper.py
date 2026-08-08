"""Parity matrix for the gh review helper surface (KIT-0091 F2).

Runs the REAL helper against a stub ``gh`` on PATH serving canned
POST-jq payloads (gh applies ``--jq`` internally, so the stub emits
what gh would after filtering). Committed against the bash original
BEFORE the Python port; the port must reproduce it — subcommand
surface, validation refusals (exit 1), API-error reporting with the
repo-mismatch HINT (exit 2), and output shapes.

Implementation parameter (the test_preflight_check.py pattern):

- ``bash``   — scripts/core/gh-review-helper.sh (post-shim: end-to-end
               through the shim)
- ``python`` — the agentive_kit review-helper entry, in-process
               (skip-marked until the port commit enables it)
"""

from __future__ import annotations

import contextlib
import io
import os
import shutil
import stat
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = REPO_ROOT / "scripts" / "core" / "gh-review-helper.sh"
_TARGET_REPO_LIB = REPO_ROOT / "scripts" / "core" / "lib" / "target_repo.sh"
_PKG_SRC = REPO_ROOT / "packages" / "agentive-kit" / "src"

if not _SCRIPT.exists() or not _TARGET_REPO_LIB.exists():
    # both are fixture inputs — a checkout missing either must skip
    # cleanly, not error in fixture setup (CodeRabbit, PR #113)
    pytest.skip(
        "gh-review-helper.sh or lib/target_repo.sh not present in this checkout",
        allow_module_level=True,
    )

if shutil.which("bash") is None:
    pytest.skip("bash not available on PATH", allow_module_level=True)

# The stub serves canned POST-jq payloads from $REVIEW_GH_STUB_DIR,
# keyed by call shape. "<key>.out present" -> cat it, exit <key>.rc
# (default 0), emit <key>.err to stderr when present. Absent .out ->
# emit <key>.err if present, exit 1 (models a gh error).
STUB_GH = textwrap.dedent("""\
    #!/bin/bash
    emit() {
        dir="$REVIEW_GH_STUB_DIR"
        [ -f "$dir/$1.err" ] && cat "$dir/$1.err" >&2
        if [ -f "$dir/$1.out" ]; then
            cat "$dir/$1.out"
            rc=0
            [ -f "$dir/$1.rc" ] && rc=$(cat "$dir/$1.rc")
            exit "$rc"
        fi
        exit 1
    }

    all_args="$*"
    case "$1 $2" in
        "repo view") echo "stub-owner/stub-repo"; exit 0 ;;
        "api graphql")
            case "$all_args" in
                *resolveReviewThread*) emit resolve ;;
                *"comments(first: 1)"*) emit threads ;;
                *) emit summary ;;
            esac ;;
        api\\ *)
            case "$2" in
                */replies) emit reply ;;
                */comments) emit comments ;;
            esac
            exit 1 ;;
    esac
    echo "stub gh: unhandled call: $all_args" >&2
    exit 1
    """)


class HelperProject:
    def __init__(self, root: Path, stub_data: Path, env: dict[str, str], impl: str):
        self.root = root
        self.stub_data = stub_data
        self.env = env
        self.impl = impl

    def run(
        self, files: dict[str, str], *args: str, errs: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess:
        for stale in self.stub_data.iterdir():
            stale.unlink()
        for key, content in files.items():
            (self.stub_data / f"{key}.out").write_text(content, encoding="utf-8")
        for key, content in (errs or {}).items():
            (self.stub_data / f"{key}.err").write_text(content, encoding="utf-8")
        if self.impl == "python":
            return self._run_python(list(args))
        return subprocess.run(
            [
                "bash",
                str(self.root / "scripts" / "core" / "gh-review-helper.sh"),
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
            with pytest.MonkeyPatch.context() as mp:
                # scrub the ambient git environment so the in-process
                # parameter tests the same conditions the bash
                # subprocess gets — an inherited GIT_DIR or user git
                # config could redirect root/repo resolution
                # (CodeRabbit, PR #113; the sibling harness pattern)
                for key in list(os.environ):
                    if key.startswith("GIT_"):
                        mp.delenv(key, raising=False)
                mp.setenv("GIT_CONFIG_GLOBAL", os.devnull)
                mp.setenv("GIT_CONFIG_SYSTEM", os.devnull)
                for key, value in self.env.items():
                    mp.setenv(key, value)
                with (
                    contextlib.redirect_stdout(out),
                    contextlib.redirect_stderr(err),
                ):
                    rc = 0
                    try:
                        mod.helper_main(argv)
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
            ["agentive-review-helper", *argv], rc, out.getvalue(), err.getvalue()
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
                "KIT-0091: the review-helper port is not yet present — "
                "the parity matrix runs bash-only until the port lands"
            )
    root = tmp_path / "proj"
    core = root / "scripts" / "core"
    (core / "lib").mkdir(parents=True)
    shutil.copy(_SCRIPT, core / "gh-review-helper.sh")
    shutil.copy(_TARGET_REPO_LIB, core / "lib" / "target_repo.sh")
    (root / ".kit").mkdir()
    (root / "CLAUDE.md").write_text("# stub project\n", encoding="utf-8")

    bin_dir = tmp_path / "stub-bin"
    bin_dir.mkdir()
    stub = bin_dir / "gh"
    stub.write_text(STUB_GH, encoding="utf-8")
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    stub_data = tmp_path / "stub-data"
    stub_data.mkdir()

    env = dict(os.environ)
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    env["REVIEW_GH_STUB_DIR"] = str(stub_data)
    if _PKG_SRC.is_dir():
        inherited = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            f"{_PKG_SRC}{os.pathsep}{inherited}" if inherited else str(_PKG_SRC)
        )
    return HelperProject(root, stub_data, env, impl)


# ── Help and dispatch ────────────────────────────────────────────────────
class TestDispatch:
    def test_help_exits_zero_with_usage(self, proj):
        result = proj.run({}, "help")
        assert result.returncode == 0
        assert "Subcommands:" in result.stdout

    def test_no_args_prints_usage(self, proj):
        result = proj.run({})
        assert result.returncode == 0
        assert "Subcommands:" in result.stdout

    def test_unknown_subcommand_exits_one(self, proj):
        result = proj.run({}, "frobnicate")
        assert result.returncode == 1
        assert "Unknown subcommand" in result.stderr

    def test_malformed_repo_override_rejected_even_with_help(self, proj):
        # --repo validation runs BEFORE the help early-exit
        result = proj.run({}, "--repo", "notaslug", "help")
        assert result.returncode == 1
        assert "owner/name format" in result.stderr

    def test_repo_flag_missing_value(self, proj):
        result = proj.run({}, "--repo")
        assert result.returncode == 1
        assert "requires an owner/name value" in result.stderr


# ── Input validation (exit 1) ────────────────────────────────────────────
class TestValidation:
    def test_threads_non_numeric_pr(self, proj):
        result = proj.run({}, "threads", "abc")
        assert result.returncode == 1
        assert "positive integer" in result.stderr

    def test_summary_missing_pr(self, proj):
        result = proj.run({}, "summary")
        assert result.returncode == 1
        assert "PR number is required" in result.stderr

    def test_reply_non_numeric_comment_id(self, proj):
        result = proj.run({}, "reply", "42", "abc", "body")
        assert result.returncode == 1
        assert "Comment ID must be a positive integer" in result.stderr

    def test_reply_empty_body(self, proj):
        result = proj.run({}, "reply", "42", "123", "")
        assert result.returncode == 1
        assert "Reply body cannot be empty" in result.stderr

    def test_resolve_malformed_thread_id(self, proj):
        result = proj.run({}, "resolve", "not-a-thread")
        assert result.returncode == 1
        assert "PRRT_" in result.stderr

    def test_loose_but_unsafe_slug_refused_before_graphql(self, proj):
        # KIT-0091 documented divergence (claude-code evaluator): the
        # bash helper interpolated OWNER/NAME into GraphQL with only
        # the loose shape check — a slug like 'a"b/c' passed it. The
        # port applies preflight's strict charset validation (KIT-0043)
        # to every slug before it can reach a query string.
        result = proj.run({}, "--repo", 'a"b/c', "summary", "42")
        assert result.returncode == 1
        assert "must look like owner/name" in result.stderr


# ── Happy paths ──────────────────────────────────────────────────────────
class TestSubcommands:
    def test_summary(self, proj):
        result = proj.run(
            {"summary": "Total:3 Resolved:2 Unresolved:1\n"}, "summary", "42"
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert "Total:3 Resolved:2 Unresolved:1" in result.stdout

    def test_threads(self, proj):
        line = "false\t123\tcursor\tPRRT_abc\tSome finding text"
        result = proj.run({"threads": line + "\n"}, "threads", "42")
        assert result.returncode == 0, result.stdout + result.stderr
        assert line in result.stdout

    def test_comments(self, proj):
        line = "123\troot\tcoderabbitai\tsrc/x.py:10\tNit: rename this"
        result = proj.run({"comments": line + "\n"}, "comments", "42")
        assert result.returncode == 0, result.stdout + result.stderr
        assert line in result.stdout

    def test_reply_prints_new_comment_id(self, proj):
        result = proj.run({"reply": "987654\n"}, "reply", "42", "123", "Fixed.")
        assert result.returncode == 0, result.stdout + result.stderr
        assert "987654" in result.stdout

    def test_resolve_prints_is_resolved(self, proj):
        result = proj.run({"resolve": "true\n"}, "resolve", "PRRT_kwAbc123")
        assert result.returncode == 0, result.stdout + result.stderr
        assert "true" in result.stdout


# ── API errors (exit 2) ──────────────────────────────────────────────────
class TestApiErrors:
    def test_threads_api_error_exits_two(self, proj):
        result = proj.run({}, "threads", "42")
        assert result.returncode == 2
        assert "Failed to fetch threads for PR #42" in result.stderr

    def test_repo_mismatch_hint_on_not_found_stderr(self, proj):
        result = proj.run(
            {},
            "threads",
            "42",
            errs={
                "threads": "GraphQL: Could not resolve to a Repository "
                "with the name 'stub-owner/stub-repo'.\n"
            },
        )
        assert result.returncode == 2
        assert "HINT:" in result.stderr
        assert "--repo" in result.stderr

    def test_other_api_error_has_no_repo_hint(self, proj):
        result = proj.run(
            {},
            "threads",
            "42",
            errs={"threads": "GraphQL: Something unrelated exploded\n"},
        )
        assert result.returncode == 2
        assert "HINT:" not in result.stderr
        assert "Something unrelated exploded" in result.stderr

    def test_reply_api_error_hints_outdated_diff(self, proj):
        result = proj.run({}, "reply", "42", "123", "Fixed.")
        assert result.returncode == 2
        assert "outdated diff" in result.stderr

    def test_resolve_api_error_exits_two(self, proj):
        result = proj.run({}, "resolve", "PRRT_kwAbc123")
        assert result.returncode == 2
        assert "Failed to resolve thread" in result.stderr

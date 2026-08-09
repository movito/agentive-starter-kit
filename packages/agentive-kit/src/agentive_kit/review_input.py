"""Review-input assembly + gh review helper (KIT-0091 F1/F2).

Ports of ``scripts/core/prepare-review-input.sh`` v1.5.2 (``main``) and
``scripts/core/gh-review-helper.sh`` v1.2.2 (``helper_main``) — the
pair travels together because the helper is the review flow's ``gh``
companion. Both are GATE-adjacent surfaces: the input file feeds the
evaluator gate, and the helper drives thread triage. Behavior is bound
to the committed parity matrices in ``tests/test_prepare_review_input
.py`` and ``tests/test_gh_review_helper.py``; code shape is free
(task spec F2).

``main`` runs only local ``git`` (via ``gitio``) — there is no
``--repo`` flag by design: the target repository's local *path* (from
CLAUDE.md's ``## Target Repository``) is what matters. ``helper_main``
runs only ``gh`` (via ``ghio``) with exit codes 0 / 1 (validation) /
2 (API error).

Documented divergences from the bash originals (PR 2 body):

- Binary detection uses a NUL-byte probe over the first 8 KiB instead
  of ``grep -Iq .`` — the same class of heuristic grep itself applies;
  empty files are still classified BEFORE the probe, as in bash.
- The helper's ``_run_gh_api`` stderr capture uses in-process pipes
  instead of a mktemp file (no temp-file failure mode; the mktemp
  refusal path disappears).
"""

from __future__ import annotations

import datetime as _dt
import fnmatch
import re
import sys
from pathlib import Path

from agentive_kit import ghio, gitio, target_repo
from agentive_kit.root import RootNotFoundError, find_project_root

# ── prepare-review-input ─────────────────────────────────────────────────

_USAGE = """\
Usage: agentive review-input <TASK-ID> [options]

Generates .adversarial/inputs/<TASK-ID>-code-review-input.md from the
current feature branch's diff against a base branch. Used to feed
file-based adversarial evaluators in cross-repo mode.

Arguments:
  <TASK-ID>              Task identifier (e.g. ID2-0015). Used for the
                         output filename and input header.

Options:
  --base <branch>        Base branch to diff against (default: main)
  --format diff|full     Input detail level (default: full)
                           diff — diff only
                           full — diff + full contents of changed files
  --help, -h             Show this help message

Note: there is no --repo flag — this command only runs local `git`,
so the target repo's *path* (from CLAUDE.md ## Target Repository)
is what matters, not its GitHub slug.

Examples:
  # Cross-repo — planning repo CWD, diff read from configured target:
  agentive review-input ID2-0015

  # Single-repo fallback — no target configured, diff from CWD repo:
  agentive review-input ID2-0015

  # Diff against develop instead of main:
  agentive review-input ID2-0015 --base develop

  # Diff only (smaller input, less accurate for large PRs):
  agentive review-input ID2-0015 --format diff

Output:
  .adversarial/inputs/<TASK-ID>-code-review-input.md

Next steps:
  set -a && source .env && set +a
  echo y | ADVERSARIAL_UNATTENDED=1 adversarial code-reviewer-fast \
.adversarial/inputs/<TASK-ID>-code-review-input.md
  # Belt-and-braces for the large-input confirm across ALL installed builds
  # (PyPI 1.0.1 reads stdin; the editable dev build reads the env flag).
  # NEVER trust exit 0 alone: a cancelled run also exits 0 — check that the
  # log file exists and carries a verdict."""

# Lockfile patterns (ID2-0047): keep the diff, skip the full-content
# block. `*.lockb` covers Bun's binary lockfile preemptively.
_LOCKFILE_GLOBS = ("*.lock", "*.lockb", "*-lock.json", "*-lock.yaml", "*-lock.yml")

# Fenced-code language hint by extension — readability for humans, not
# needed by the evaluator.
_LANG_BY_EXT = {
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".svelte": "svelte",
    ".py": "python",
    ".sh": "bash",
    ".bash": "bash",
    ".json": "json",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".md": "markdown",
    ".css": "css",
    ".html": "html",
    ".groq": "groq",
}


def _err(*lines: str) -> None:
    for line in lines:
        print(line, file=sys.stderr)


def _parse_main_args(argv: list[str]) -> tuple[str, str, str]:
    """(task_id, base_branch, format) — the bash flag loop verbatim."""
    task_id = ""
    base_branch = "main"
    fmt = "full"
    i = 0
    while i < len(argv):
        arg = argv[i]
        nxt = argv[i + 1] if i + 1 < len(argv) else ""
        # membership: flag-alias vocabulary check, not identifier
        # equality (same for the flag names below)
        if arg in ("--help", "-h"):
            print(_USAGE)
            sys.exit(0)
        elif arg == "--base":
            if not nxt or nxt.startswith("-"):
                _err("ERROR: --base requires a branch name")
                sys.exit(1)
            base_branch = nxt
            i += 2
        elif arg.startswith("--base="):
            base_branch = arg.removeprefix("--base=")
            if not base_branch:
                _err("ERROR: --base= requires a branch name")
                sys.exit(1)
            i += 1
        elif arg == "--format":
            if not nxt or nxt.startswith("-"):
                _err("ERROR: --format requires a value (diff|full)")
                sys.exit(1)
            fmt = nxt
            i += 2
        elif arg.startswith("--format="):
            fmt = arg.removeprefix("--format=")
            i += 1
        elif arg == "--repo" or arg.startswith("--repo="):
            _err(
                "ERROR: --repo is not supported by this script.",
                "This helper diffs a local working tree (no gh API calls), so a",
                "GitHub slug isn't useful — what matters is the local Path entry",
                "under '## Target Repository' in CLAUDE.md. Update CLAUDE.md to",
                "point at the desired repo and re-run without --repo.",
            )
            sys.exit(1)
        elif arg.startswith("-"):
            _err(f"ERROR: Unknown option: {arg}")
            _err("Run: agentive review-input --help")
            sys.exit(1)
        else:
            if not task_id:
                task_id = arg
            else:
                _err(f"ERROR: Unexpected positional argument: {arg}")
                sys.exit(1)
            i += 1
    return task_id, base_branch, fmt


def _git_out(repo_dir: Path, *args: str) -> str | None:
    """stdout of a successful git call, else None (surfacing stderr)."""
    result = gitio.run_git(repo_dir, *args, timeout=60)
    if result is None:
        return None
    if result.returncode != 0:
        # Bash let git's stderr through on failure — real failures must
        # not look identical to "no changes committed yet".
        if result.stderr:
            sys.stderr.write(result.stderr)
        return None
    return result.stdout


def _is_lockfile(file_path: str) -> bool:
    name = file_path.rsplit("/", 1)[-1]
    return any(fnmatch.fnmatch(name, pat) for pat in _LOCKFILE_GLOBS)


def _looks_binary(fs_path: Path) -> bool:
    """NUL-probe over the first 8 KiB (grep -I's own heuristic class)."""
    try:
        with open(fs_path, "rb") as fh:
            return b"\0" in fh.read(8192)
    except OSError:
        return True


def _file_section(file_path: str, fs_path: Path) -> str:
    """One '### Source:' block for the full-contents appendix."""
    header = f"### Source: `{file_path}`\n\n"
    if _is_lockfile(file_path):
        return (
            header
            + f"_[lockfile skipped: {file_path}] — diff is included above; full\n"
            "content omitted to keep evaluator input compact._\n\n"
        )
    if not fs_path.is_file():
        # Listed as changed but missing from the working tree — likely
        # uncommitted delete or non-standard status.
        return header + f"_(file not found on disk at `{fs_path}` — skipped)_\n\n"
    try:
        size = fs_path.stat().st_size
    except OSError:
        size = 0
    # Empty before binary: a 0-byte file must not be mislabeled binary
    # (the bash grep -Iq . had the same blind spot, handled the same
    # way).
    if size == 0:
        return header + "_(empty file, 0 bytes — skipped)_\n\n"
    if _looks_binary(fs_path):
        return header + f"_(binary file, {size} bytes — skipped)_\n\n"

    suffix = Path(file_path).suffix
    lang = _LANG_BY_EXT.get(suffix, "")
    try:
        content = fs_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return header + f"_(file not found on disk at `{fs_path}` — skipped)_\n\n"
    if not content.endswith("\n"):
        content += "\n"
    # 4-backtick outer fence: embedded triple backticks (markdown
    # sources, docs) must not prematurely close the block.
    return header + f"````{lang}\n{content}````\n\n"


def main(argv: list[str] | None = None) -> None:
    task_id, base_branch, fmt = _parse_main_args(sys.argv[1:] if argv is None else argv)

    if not task_id:
        _err("ERROR: <TASK-ID> is required")
        _err("Run: agentive review-input --help")
        sys.exit(1)
    if not re.match(r"^[A-Z][A-Z0-9]*-[A-Z0-9]+$", task_id):
        _err(f"ERROR: TASK-ID must look like ABC-123 or ABC-TEST, got: '{task_id}'")
        sys.exit(1)
    # membership: format vocabulary check, not identifier equality
    if fmt not in ("diff", "full"):
        _err(f"ERROR: --format must be 'diff' or 'full', got: '{fmt}'")
        sys.exit(1)

    try:
        root = find_project_root()
    except RootNotFoundError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    target = target_repo.resolve(root)

    diff_source_label = str(root)
    diff_dir = root
    if target.path:
        # The bash lib consumed TARGET_PATH via word splitting, so a
        # whitespace path silently became three git args — refuse
        # up-front with the same message the parity matrix pins. The
        # Python port doesn't word-split, but one declaration must not
        # be valid to one implementation and fatal to the other.
        if re.search(r"\s", target.path):
            _err(
                f"ERROR: TARGET_PATH '{target.path}' contains whitespace",
                "The cross-repo helper library (scripts/core/lib/target_repo.sh)",
                "relies on word-splitting and cannot handle paths with spaces.",
                "Move the target repo to a whitespace-free path and update"
                " CLAUDE.md.",
            )
            sys.exit(1)
        tree = Path(root, target.path)
        if not (tree / ".git").is_dir() and not (tree / ".git").is_file():
            _err(
                f"ERROR: TARGET_PATH '{target.path}' is not a git working tree",
                "Fix the '## Target Repository' Path in CLAUDE.md and re-run.",
            )
            sys.exit(1)
        diff_source_label = target.path
        diff_dir = tree

    head_branch = gitio.current_branch(diff_dir) or "(detached HEAD)"

    verify = gitio.run_git(
        diff_dir, "rev-parse", "--verify", "--quiet", base_branch, timeout=60
    )
    if verify is None or verify.returncode != 0:
        _err(
            f"ERROR: base branch '{base_branch}' not found in {diff_source_label}",
            "Pass --base <branch> to pick a different base.",
        )
        sys.exit(1)

    # `A...B` (three dots): diff HEAD against the merge-base, excluding
    # base-branch changes after the feature branched off.
    diff_content = _git_out(diff_dir, "diff", f"{base_branch}...HEAD")
    if diff_content is None:
        _err(f"ERROR: git diff '{base_branch}...HEAD' failed in {diff_source_label}")
        sys.exit(1)
    if not diff_content:
        _err(f"WARNING: No diff between {base_branch} and HEAD in {diff_source_label}")
        _err("Have you committed your changes?")

    changed_status = _git_out(
        diff_dir, "diff", "--name-status", f"{base_branch}...HEAD"
    )
    if changed_status is None:
        _err(
            f"ERROR: git diff --name-status '{base_branch}...HEAD' failed "
            f"in {diff_source_label}"
        )
        sys.exit(1)
    changed_status = changed_status.rstrip("\n")

    output_dir = root / ".adversarial" / "inputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{task_id}-code-review-input.md"

    today = _dt.date.today().isoformat()
    parts: list[str] = []
    parts.append(f"# Code Review: {task_id}\n\n")
    parts.append("## Context\n\n")
    parts.append(f"- **Task**: {task_id}\n")
    parts.append(f"- **Date**: {today}\n")
    parts.append(f"- **Diff source**: `{diff_source_label}`\n")
    if target.is_set:
        parts.append(f"- **Target repo**: `{target.repo}`\n")
    else:
        parts.append("- **Target repo**: (single-repo / current)\n")
    parts.append(f"- **Base branch**: `{base_branch}`\n")
    parts.append(f"- **Head branch**: `{head_branch}`\n")
    parts.append(f"- **Format**: `{fmt}`\n\n")
    parts.append("> Generated by `agentive review-input`.\n")
    parts.append(
        "> Replace this block with PR link and bot-review summary before running\n"
    )
    parts.append("> deep evaluators — context improves signal.\n\n")
    parts.append("## Changed Files\n\n")
    if changed_status:
        parts.append(f"```\n{changed_status}\n```\n")
    else:
        parts.append("(no changes detected)\n")
    parts.append("\n## Diff\n\n")
    # 4-backtick outer fence so triple-backtick content inside the diff
    # can't prematurely close it.
    parts.append("````diff\n")
    if diff_content:
        if not diff_content.endswith("\n"):
            diff_content += "\n"
        parts.append(diff_content)
    parts.append("````\n")

    if fmt == "full" and changed_status:
        parts.append("\n## Full File Contents\n\n")
        parts.append(
            "> Complete post-change contents of non-deleted files. Evaluators need\n"
            "> full module context to avoid hallucinating missing imports/exports\n"
            "> that live outside the diff hunks (ID2-0002 retro).\n\n"
        )
        for line in changed_status.splitlines():
            if not line:
                continue
            fields = line.split("\t")
            status = fields[0]
            if status.startswith("D"):
                continue  # deleted: no current content
            if status.startswith(("R", "C")):
                file_path = fields[2] if len(fields) > 2 else ""
            else:
                file_path = fields[1] if len(fields) > 1 else ""
            if not file_path:
                continue
            fs_path = Path(diff_dir if target.path else root, file_path)
            parts.append(_file_section(file_path, fs_path))

    output_file.write_text("".join(parts), encoding="utf-8")

    changed_count = len(changed_status.splitlines()) if changed_status else 0
    print(f"Wrote: {output_file}")
    print(f"  Diff source:  {diff_source_label}")
    print(f"  Base:         {base_branch}")
    print(f"  Head:         {head_branch}")
    print(f"  Format:       {fmt}")
    print(f"  Files changed: {changed_count}")
    print()
    print("Next steps:")
    # Belt-and-braces large-input confirm (2026-07-17 planner matrix):
    # pipe y for stdin-reading builds AND set the env flag for the dev
    # build; either fd non-TTY marks the session non-interactive. Never
    # trust exit 0 alone — check the log file for a verdict.
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        pipe_y = "echo y | ADVERSARIAL_UNATTENDED=1 "
        print(
            "  # belt-and-braces large-input confirm (stdin pipe for PyPI "
            "builds, env flag for the dev build); check the log file — "
            "cancelled runs also exit 0"
        )
    else:
        pipe_y = ""
    print("  set -a && source .env && set +a")
    print(
        f"  {pipe_y}adversarial code-reviewer-fast {output_file}  # fast gate (~$0.01)"
    )
    print(f"  {pipe_y}adversarial code-reviewer {output_file}       # deep (~$0.33)")
    print(f"  {pipe_y}adversarial claude-code {output_file}         # security")
    sys.exit(0)


# ── gh-review-helper ─────────────────────────────────────────────────────

_HELPER_USAGE = (
    """\
Usage: agentive review-helper [--repo owner/name] <subcommand> [args...]

Options:
  --repo owner/name  Target GitHub repo (overrides CLAUDE.md ## Target Repository)

Subcommands:
  reply    <PR> <COMMENT_ID> "<body>"   Reply to a review comment
  resolve  <THREAD_NODE_ID>             Resolve a review thread
  threads  <PR>                          List threads with IDs and status
  comments <PR>                          List review comments with IDs
  summary  <PR>                          Thread count summary
  help                                   Show this help

Exit codes:
  0 — Success
  1 — Input validation error
  2 — API error

Examples:
  agentive review-helper summary 53
  agentive review-helper --repo movito/ixda-services threads 53
  agentive review-helper reply 53 2861292837 \
"""
    + """'Fixed in abc1234: description.'
  agentive review-helper resolve PRRT_kwDORNcO0s5wPovc"""
)

_THREADS_JQ = (
    '.data.repository.pullRequest.reviewThreads.nodes[] | "\\(.isResolved)\\t'
    "\\(.comments.nodes[0].databaseId)\\t\\(.comments.nodes[0].author.login // "
    '"ghost")\\t\\(.id)\\t\\(.comments.nodes[0].body | gsub("[\\\\n\\\\t]"; " ") '
    '| .[0:120])"'
)
_COMMENTS_JQ = (
    '.[] | "\\(.id)\\t\\(.in_reply_to_id // "root")\\t\\(.user.login // "ghost")'
    '\\t\\(.path):\\(.line // .original_line)\\t\\(.body | gsub("[\\\\n\\\\t]"; '
    '" ") | .[0:120])"'
)
_SUMMARY_JQ = (
    "[.data.repository.pullRequest.reviewThreads.nodes[].isResolved] | "
    '"Total:\\(length) Resolved:\\([.[] | select(.)] | length) '
    'Unresolved:\\([.[] | select(. | not)] | length)"'
)


def _validate_pr(value: str) -> None:
    if not value:
        _err("ERROR: PR number is required")
        sys.exit(1)
    if not re.match(r"^[0-9]+$", value):
        _err(f"ERROR: PR number must be a positive integer, got: '{value}'")
        sys.exit(1)


def _validate_comment_id(value: str) -> None:
    if not value:
        _err("ERROR: Comment ID is required")
        sys.exit(1)
    if not re.match(r"^[0-9]+$", value):
        _err(f"ERROR: Comment ID must be a positive integer, got: '{value}'")
        sys.exit(1)


def _validate_thread_id(value: str) -> None:
    if not value:
        _err("ERROR: Thread node ID is required")
        sys.exit(1)
    if not re.match(r"^PRRT_[A-Za-z0-9_-]+$", value):
        _err(f"ERROR: Thread ID must match PRRT_*, got: '{value}'")
        sys.exit(1)


def _api_error(repo: str, subject: str, stderr_content: str, context: str) -> None:
    """The helper's error reporter: gh stderr verbatim, plus a --repo
    mismatch hint when the stderr looks like a repository-resolution
    failure (narrow heuristic — a bogus PR number in the RIGHT repo
    must not trigger the misleading wrong-repo hint)."""
    _err(f"ERROR: {context}")
    if stderr_content:
        if re.search(
            r"could not resolve to a repository|repository not found"
            r"|NOT_FOUND.*Repository",
            stderr_content,
            re.IGNORECASE,
        ):
            _err(f"  HINT: gh-review-helper is configured for repo '{repo}'.")
            _err(
                f"        If '{subject}' lives in a different repo, override "
                "with --repo <owner/name>."
            )
            _err(
                "        Example: agentive review-helper "
                "--repo movito/ixda-services-2.0 <subcommand> <args>"
            )
        _err(f"  gh stderr: {stderr_content.rstrip()}")


def _run_helper_api(repo: str, subject: str, context: str, *gh_args: str) -> str:
    """Run gh, print the error report and exit 2 on failure, else
    return stdout (the bash _run_gh_api contract)."""
    result = ghio.run_gh(*gh_args)
    if result is None or result.returncode != 0:
        stderr_content = "" if result is None else result.stderr
        _api_error(repo, subject, stderr_content, context)
        sys.exit(2)
    return result.stdout.rstrip("\n")


def _detect_helper_repo(root: Path, override: str) -> str:
    target = target_repo.resolve(root, override)
    if target.is_set:
        repo = target.repo
    else:
        repo = ghio.default_repo_slug() or ""
        if not repo:
            _err("ERROR: Could not determine GitHub repository")
            _err("Run: gh repo set-default")
            sys.exit(2)
    # Documented divergence (claude-code evaluator, PR 2): the bash
    # helper interpolated OWNER/NAME into GraphQL with only the loose
    # shape check — apply preflight's strict charset validation
    # (KIT-0043) to every slug, whatever its source, before it can
    # reach a query string.
    if not re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", repo):
        _err(f"ERROR: repository must look like owner/name, got: '{repo}'")
        sys.exit(1)
    return repo


def helper_main(argv: list[str] | None = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)

    repo_override = ""
    while args:
        arg = args[0]
        if arg == "--repo":
            nxt = args[1] if len(args) > 1 else ""
            if not nxt or nxt.startswith("-"):
                _err("ERROR: --repo requires an owner/name value")
                sys.exit(1)
            repo_override = nxt
            if not re.match(r"^[^/\s]+/[^/\s]+$", repo_override):
                _err(
                    "ERROR: --repo must be in owner/name format, "
                    f"got: '{repo_override}'"
                )
                sys.exit(1)
            args = args[2:]
        elif arg.startswith("--repo="):
            repo_override = arg.removeprefix("--repo=")
            if not repo_override:
                _err("ERROR: --repo= requires an owner/name value")
                sys.exit(1)
            if not re.match(r"^[^/\s]+/[^/\s]+$", repo_override):
                _err(
                    "ERROR: --repo must be in owner/name format, "
                    f"got: '{repo_override}'"
                )
                sys.exit(1)
            args = args[1:]
        else:
            break

    # Help early-exit runs AFTER --repo validation so malformed
    # overrides are rejected even when combined with help.
    subcommand = args[0] if args else "help"
    # membership: help-alias vocabulary check, not identifier equality
    if subcommand in ("help", "--help", "-h"):
        print(_HELPER_USAGE)
        sys.exit(0)

    try:
        root = find_project_root()
    except RootNotFoundError as exc:
        print(exc, file=sys.stderr)
        sys.exit(2)

    # Repo detection runs BEFORE subcommand dispatch, mirroring the
    # bash flow exactly (BugBot, PR #113): an unknown subcommand with
    # an undeterminable repo exits 2 (repo error), and only a resolved
    # repo reaches the exit-1 unknown-subcommand refusal.
    repo = _detect_helper_repo(root, repo_override)

    # membership: subcommand vocabulary check, not identifier equality
    if subcommand not in ("reply", "resolve", "threads", "comments", "summary"):
        _err(f"ERROR: Unknown subcommand: {subcommand}")
        _err(_HELPER_USAGE)
        sys.exit(1)

    owner, name = repo.split("/", 1)
    sub_args = args[1:]

    if subcommand == "reply":
        pr = sub_args[0] if len(sub_args) > 0 else ""
        comment_id = sub_args[1] if len(sub_args) > 1 else ""
        body = sub_args[2] if len(sub_args) > 2 else ""
        _validate_pr(pr)
        _validate_comment_id(comment_id)
        if not body:
            _err("ERROR: Reply body cannot be empty")
            sys.exit(1)
        result = ghio.run_gh(
            "api",
            f"repos/{owner}/{name}/pulls/{pr}/comments/{comment_id}/replies",
            "-f",
            f"body={body}",
            "--jq",
            ".id",
        )
        if result is None or result.returncode != 0:
            rc = 1 if result is None else result.returncode
            _err(f"ERROR: Failed to post reply (API returned {rc})")
            _err(
                "HINT: If 404, the comment may be on an outdated diff. Use "
                "'resolve' with the GraphQL thread ID instead."
            )
            sys.exit(2)
        print(result.stdout.rstrip("\n"))
        sys.exit(0)

    if subcommand == "resolve":
        thread_id = sub_args[0] if len(sub_args) > 0 else ""
        _validate_thread_id(thread_id)
        result = ghio.run_gh(
            "api",
            "graphql",
            "-f",
            f"query=mutation {{ resolveReviewThread(input: {{threadId: "
            f'"{thread_id}"}}) {{ thread {{ isResolved }} }} }}',
            "--jq",
            ".data.resolveReviewThread.thread.isResolved",
        )
        if result is None or result.returncode != 0:
            _err(f"ERROR: Failed to resolve thread {thread_id}")
            sys.exit(2)
        print(result.stdout.rstrip("\n"))
        sys.exit(0)

    if subcommand == "threads":
        pr = sub_args[0] if len(sub_args) > 0 else ""
        _validate_pr(pr)
        query = (
            f'{{ repository(owner: "{owner}", name: "{name}") {{ pullRequest'
            f"(number: {pr}) {{ reviewThreads(first: 100) {{ nodes {{ id "
            "isResolved comments(first: 1) { nodes { databaseId author "
            "{ login } body } } } } } } }"
        )
        output = _run_helper_api(
            repo,
            f"PR #{pr}",
            f"Failed to fetch threads for PR #{pr}",
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "--jq",
            _THREADS_JQ,
        )
        print(output)
        sys.exit(0)

    if subcommand == "comments":
        pr = sub_args[0] if len(sub_args) > 0 else ""
        _validate_pr(pr)
        output = _run_helper_api(
            repo,
            f"PR #{pr}",
            f"Failed to fetch comments for PR #{pr}",
            "api",
            f"repos/{owner}/{name}/pulls/{pr}/comments",
            "--paginate",
            "--jq",
            _COMMENTS_JQ,
        )
        print(output)
        sys.exit(0)

    # summary
    pr = sub_args[0] if len(sub_args) > 0 else ""
    _validate_pr(pr)
    query = (
        f'{{ repository(owner: "{owner}", name: "{name}") {{ pullRequest'
        f"(number: {pr}) {{ reviewThreads(first: 100) {{ nodes "
        "{ isResolved } } } } }"
    )
    output = _run_helper_api(
        repo,
        f"PR #{pr}",
        f"Failed to fetch thread summary for PR #{pr}",
        "api",
        "graphql",
        "-f",
        f"query={query}",
        "--jq",
        _SUMMARY_JQ,
    )
    print(output)
    sys.exit(0)


if __name__ == "__main__":
    main()

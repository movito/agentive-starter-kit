"""All git invocations for agentive-kit live in this module (KIT-0090 F1).

One module, deliberately NOT a pluggable SCM interface (evaluation
finding declined as YAGNI, recorded in the task spec): no other SCM is
on any horizon, and a single-module boundary already buys the
encapsulation an interface would. What the boundary is FOR is keeping
the portability discipline greppable in one place — the KIT-0080
incident class, where Apple's system git (2.30.1) silently mangled
``--path-format=absolute`` output, was fixed by re-shipping the same
pattern into several scripts; here it is fixed once.

Portability rules (KIT-0080 — the documented floor is git >= 2.30):

- Never pass ``--path-format=absolute`` to ``rev-parse``: git < 2.31
  echoes the flag back as an output line and exits 0, so the caller
  reads garbage. Use the plain form and absolutize against the ``-C``
  directory ourselves.
- Always scrub ambient ``GIT_*`` variables: pre-commit and hooks export
  ``GIT_DIR``/``GIT_INDEX_FILE`` (absolute, in worktrees), which
  override ``-C`` and silently point git at the WRONG repository
  (the KIT-0043 incident class).
- Bound every call with a timeout and close stdin: a wedged git
  (credential prompt, hung filesystem) must fail the one call, not
  hang the CLI.

Error strategy: this is a leaf utility layer — helpers return ``None``
(or a non-zero ``CompletedProcess``) on failure and never raise for
environmental problems (git absent, not a repository, timeout).
Callers decide loudness.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

# Seconds allowed for any single plumbing call (branch lookup,
# rev-parse, remote read). Generous for plumbing, short enough that a
# wedged git fails the command instead of hanging it.
GIT_TIMEOUT = 10


def clean_git_env() -> dict[str, str]:
    """Environment with inherited GIT_* location vars stripped.

    Makes ``git -C`` authoritative: an ambient ``GIT_DIR`` /
    ``GIT_WORK_TREE`` (exported e.g. by pre-commit while running hooks)
    would otherwise override ``-C`` and point git at the wrong
    repository (KIT-0043). Strips the whole ``GIT_`` prefix rather than
    an allowlist — the same suite-wide rule tests/conftest.py applies.
    """
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def run_git(
    repo_dir: Path | str,
    *args: str,
    timeout: int = GIT_TIMEOUT,
    capture: bool = True,
) -> subprocess.CompletedProcess | None:
    """Run ``git -C <repo_dir> <args>`` with the module's env/bounds.

    Returns the ``CompletedProcess``, or ``None`` when git could not be
    executed at all (binary absent, OS error, timeout). A git that ran
    and failed is reported through ``returncode`` — the two failure
    shapes are deliberately distinct so callers can tell "no git" from
    "git said no".
    """
    try:
        return subprocess.run(
            ["git", "-C", str(repo_dir), *args],
            capture_output=capture,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
            env=clean_git_env(),
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return None


def current_branch(repo_dir: Path | str) -> str | None:
    """Name of the checked-out branch, or ``None``.

    ``None`` covers: not a git repository, git absent or wedged, and a
    detached HEAD (``--show-current`` prints nothing there). Callers
    that gate side effects on "am I on main?" (the KIT-0086
    single-writer guard) treat ``None`` as NOT main — the fail-safe
    direction: when the branch cannot be established, skip the write.
    """
    result = run_git(repo_dir, "branch", "--show-current")
    if result is None or result.returncode != 0:
        return None
    branch = result.stdout.strip()
    return branch or None


def git_common_dir(repo_dir: Path | str) -> Path | None:
    """Absolute path of the repo's common git dir, worktree-safe.

    KIT-0080: plain ``--git-common-dir`` (never ``--path-format=
    absolute`` — see module docstring), absolutized here. Plain output
    is RELATIVE to the ``-C`` directory (both old and new gits return a
    bare ``.git`` from a primary clone), so it is anchored on
    ``repo_dir`` — never on the process CWD.

    No ``.resolve()``: that would follow symlinked ancestors and report
    a PHYSICAL path, diverging from the bash resolvers this helper is
    pinned equivalent to (tests/test_setup_door.py). ``os.path.normpath``
    collapses the ``<root>/.git`` join without touching symlinks.

    Returns ``None`` when ``repo_dir`` is not a git repository or git
    is unavailable.
    """
    result = run_git(repo_dir, "rev-parse", "--git-common-dir")
    if result is None or result.returncode != 0:
        return None
    common = result.stdout.strip()
    if not common:
        return None
    return Path(os.path.normpath(Path(repo_dir) / common))


def derive_repo_url(repo_dir: Path | str) -> str | None:
    """GitHub-style repo path from ``origin``, e.g. ``github.com/o/r``.

    Handles SSH (``git@github.com:owner/repo.git``) and HTTP(S) forms;
    returns ``None`` for anything else (``ssh://``, ``git://``, local
    paths) and on any git failure.
    """
    result = run_git(repo_dir, "remote", "get-url", "origin")
    if result is None or result.returncode != 0:
        return None

    url = result.stdout.strip()
    if not url:
        return None

    if url.startswith("git@"):
        url = url.removeprefix("git@").replace(":", "/", 1)
    elif url.startswith("https://"):
        url = url.removeprefix("https://")
    elif url.startswith("http://"):
        url = url.removeprefix("http://")
    else:
        return None

    return url.removesuffix(".git")

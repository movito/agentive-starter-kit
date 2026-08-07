"""All GitHub CLI (``gh``) invocations for agentive-kit live here (KIT-0091 F1).

The ``gitio`` pattern applied to the other CLI boundary (evaluation
finding, accepted in the KIT-0091 spec): one greppable home for every
``gh`` call, testable via a stub ``gh`` on PATH — no module in this
package may spawn ``gh`` directly.

Deliberately thinner than a GitHub API client: callers compose the
exact ``gh`` argument vectors they need (the ported bash scripts are
the contract — keeping their command shapes verbatim is what lets one
canned-payload stub drive the bash original and the Python port in the
same parity harness). What this module owns:

- process discipline: bounded timeout, stdin closed (a ``gh`` that
  prompts for auth must fail its one call, not hang the CLI), text
  capture;
- the two failure shapes, kept distinct exactly like ``gitio``:
  ``None`` means "gh could not be executed" (binary absent, OS error,
  timeout), a ``CompletedProcess`` with nonzero ``returncode`` means
  "gh ran and said no";
- ``--repo`` placement: the legacy scripts expand ``$GH_REPO_ARG``
  immediately after ``gh`` (``gh --repo owner/name pr view …``), and
  the flag position is part of the pinned command shape.

No environment scrubbing, unlike ``gitio``: ``gh`` has no analogue of
the ``GIT_DIR`` location-override hazard (KIT-0043) — an explicit
``--repo`` flag already outranks ambient ``GH_REPO``, and scrubbing
``GH_HOST``/``GH_TOKEN`` would break enterprise and CI setups the bash
originals supported untouched.

Error strategy: leaf utility layer — helpers return ``None`` (or a
non-zero ``CompletedProcess``) and never raise for environmental
problems. Callers decide loudness.
"""

from __future__ import annotations

import shutil
import subprocess

# Seconds allowed for any single gh call. Network-bound (API round
# trips, GraphQL), so far more generous than gitio's plumbing bound —
# but still finite: a wedged gh (auth prompt swallowed by the closed
# stdin, proxy black hole) fails its one call instead of hanging the
# gate run.
GH_TIMEOUT = 60


def gh_available() -> bool:
    """True when a ``gh`` executable is on PATH."""
    return shutil.which("gh") is not None


def run_gh(
    *args: str,
    repo: str | None = None,
    timeout: int = GH_TIMEOUT,
    capture: bool = True,
) -> subprocess.CompletedProcess | None:
    """Run ``gh [--repo <repo>] <args>`` with the module's bounds.

    ``repo`` (an ``owner/name`` slug) is inserted directly after ``gh``,
    mirroring the legacy scripts' ``$GH_REPO_ARG`` expansion — callers
    in single-repo mode pass ``None`` and no flag is emitted.

    Returns the ``CompletedProcess``, or ``None`` when gh could not be
    executed at all (binary absent, OS error, timeout).

    With ``capture=False`` the returned process carries ``stdout=None``
    — callers that read output (e.g. preflight's ``_gh_text``) must
    keep the default ``capture=True``.
    """
    cmd = ["gh"]
    if repo:
        cmd += ["--repo", repo]
    cmd += list(args)
    try:
        return subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return None


def auth_ok() -> bool:
    """True when ``gh auth status`` reports an authenticated CLI."""
    result = run_gh("auth", "status")
    return result is not None and result.returncode == 0


def default_repo_slug() -> str | None:
    """``owner/name`` of the current directory's repo per ``gh``, or ``None``.

    The fallback the legacy scripts used when no target repo is
    configured: ``gh repo view --json nameWithOwner -q .nameWithOwner``.
    """
    result = run_gh("repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner")
    if result is None or result.returncode != 0:
        return None
    slug = result.stdout.strip()
    return slug or None

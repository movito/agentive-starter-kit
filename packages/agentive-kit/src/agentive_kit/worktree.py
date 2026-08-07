"""Per-task worktree provisioning library (KIT-0091 F1 — the LIBRARY
half of ``scripts/local/new-worktree.sh``).

Encodes the KIT-0043/KIT-0044 pilot recipe: branch from FRESH
origin/main (never a possibly-stale local main), then provision the
gitignored runtime artifacts a session needs. The door-side ENTRY
script stays in ``scripts/local`` as a thin delegator (phase 2 owns
any door change); its parity record is ``tests/test_new_worktree.py``,
which must stay green through the delegation — every user-visible
line below (Linked/Serena/LAUNCH/venv fallbacks) is pinned there.

Provisioning contract carried over verbatim:

- ``PROVISION_LINKS`` is explicit and enumerated, never a glob
  (KIT-0044 F1.2). Symlinks are READ-ONLY use.
- ``.venv`` is NEVER symlinked — an in-worktree ``venv --clear``
  through a link empties the TARGET venv (KIT-0065 emptied the
  primary's). A real per-worktree venv is provisioned via the
  checkout's own ``project setup --no-hooks`` (hooks live in the
  SHARED common dir); failure is non-fatal by design.
- Serena gets a worktree-local project.yml with a per-worktree name —
  name-based activation resolves to the PRIMARY clone (KIT-0069), so
  sessions must activate by absolute path.
- Primary-root resolution goes through ``gitio.git_common_dir``
  (plain ``--git-common-dir``, never ``--path-format=absolute`` —
  KIT-0080: Apple's git 2.30.1 echoes that flag back and exits 0).
"""

from __future__ import annotations

import re
import shlex
import subprocess
import sys
from pathlib import Path

from agentive_kit import gitio

# Gitignored runtime artifacts a session needs, symlinked read-only
# from the primary. Audited against .gitignore 2026-07-14 (KIT-0044).
# Add new entries BY NAME — never "everything gitignored". Each entry
# must be gitignored WITHOUT a trailing slash (dir-only patterns don't
# match the symlink, which then blocks `git worktree remove`).
PROVISION_LINKS = (
    ".env",
    ".adversarial/evaluators",
)


def _fail(*lines: str) -> None:
    for line in lines:
        print(line, file=sys.stderr)
    sys.exit(1)


def resolve_primary_root(anchor: Path) -> Path:
    """The PRIMARY clone's root, resolved from *anchor* (worktree-safe).

    The entry script may be invoked from inside another worktree (its
    checkout has its own copy of scripts/), so symlink sources and the
    worktree parent dir must always resolve through the SHARED git
    common dir — never the script's checkout. Exits 1 on failure or on
    a bare-hub layout (dirname math assumes ``<root>/.git``; a bare
    primary would resolve wrong silently — WORKTREE-WORKFLOW.md).
    """
    common = gitio.git_common_dir(anchor)
    if common is None:
        _fail(f"Error: git could not resolve the common dir from {anchor}")
    # LOGICAL path, no .resolve(): the bash original's cd+pwd kept the
    # caller's symlinked view (plain pwd prints $PWD), so a primary
    # under a symlinked home (~/code -> /Volumes/...) provisioned its
    # worktrees beside the LOGICAL parent. Collapsing to the physical
    # path here would scatter ask-worktrees/ somewhere the operator
    # never looks (o3, PR 2 round 1). gitio.git_common_dir already
    # normpaths without following symlinks.
    primary_root = common.parent
    if not (primary_root / ".git").exists():
        _fail(
            f"Error: could not resolve primary clone root (got: {primary_root})",
            "       Is the primary clone bare? See WORKTREE-WORKFLOW.md.",
        )
    return primary_root


def derive_slug(primary_root: Path, task_id: str) -> str:
    """Branch-suffix slug from the task spec filename (exactly one
    spec must match ``.kit/tasks/*/<TASK>-*.md``)."""
    matches = sorted(
        p
        for p in (primary_root / ".kit" / "tasks").glob(f"*/{task_id}-*.md")
        if p.is_file()
    )
    if not matches:
        _fail(
            f"Error: no task spec found for {task_id} in .kit/tasks/ —",
            f"       pass a slug explicitly: new-worktree.sh {task_id} <slug>",
        )
    if len(matches) > 1:
        listing = "\n".join(f"       {m}" for m in matches)
        _fail(
            f"Error: multiple task specs found for {task_id}:",
            listing,
            "       Fix the duplicate or pass a slug explicitly.",
        )
    stem = matches[0].name.removesuffix(".md")
    return stem.removeprefix(f"{task_id}-")


def _recovery_lines(primary_root: Path, worktree_path: Path, branch: str) -> list[str]:
    return [
        f"  git -C {primary_root} worktree remove --force {worktree_path}",
        f"  git -C {primary_root} branch -D {branch}",
    ]


def _provision_links(primary_root: Path, worktree_path: Path, branch: str) -> None:
    """Symlink the enumerated artifacts; sources were verified up
    front, so every entry links or we refuse loudly with recovery
    steps (no silent partial provisioning)."""
    for rel in PROVISION_LINKS:
        src = primary_root / rel
        dst = worktree_path / rel
        # If dst already exists as a directory, a symlink would land
        # INSIDE it — the .adversarial/evaluators/evaluators incident
        # (KIT-0068 A69). Refuse loudly instead.
        if dst.exists() or dst.is_symlink():
            for line in (
                f"Error: provisioning destination already exists: {dst}",
                "       Linking over it would nest the symlink inside the",
                "       existing directory. Remove it, then re-run.",
                "To retry from scratch:",
                *_recovery_lines(primary_root, worktree_path, branch),
            ):
                print(line, file=sys.stderr)
            sys.exit(1)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.symlink_to(src)
        print(f"Linked {rel} -> {src}")


def _generate_serena_config(
    primary_root: Path, worktree_path: Path, task_id: str
) -> None:
    """Worktree-local Serena project.yml with a per-worktree name
    (KIT-0069) — only when the primary actually uses Serena and the
    checkout carries the template. Literal substitution (the bash
    version disabled patsub_replacement so ``&`` in the dirname stays
    literal — str.replace is literal by construction)."""
    primary_cfg = primary_root / ".serena" / "project.yml"
    template = worktree_path / ".serena" / "project.yml.template"
    if not primary_cfg.is_file() or not template.is_file():
        return
    serena_name = f"{primary_root.name}-{task_id}"
    content = template.read_text(encoding="utf-8")
    generated = content.replace("${PROJECT_NAME}", serena_name)
    if not generated.endswith("\n"):
        generated += "\n"
    (worktree_path / ".serena" / "project.yml").write_text(generated, encoding="utf-8")
    print(f"Serena config generated (project_name: {serena_name})")


def _provision_venv(worktree_path: Path) -> None:
    """Real per-worktree venv via the checkout's own project script
    (KIT-0065: never a symlink; KIT-0071: --no-hooks because hooks are
    shared with the primary). Non-fatal: a network hiccup must not
    scrap the worktree."""
    print()
    print("Provisioning per-worktree venv (real venv, never a symlink)...")
    try:
        result = subprocess.run(
            [
                str(worktree_path / "scripts" / "core" / "project"),
                "setup",
                "--no-hooks",
            ],
            cwd=worktree_path,
            stdin=subprocess.DEVNULL,
            timeout=600,
        )
        ok = result.returncode == 0
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        ok = False
    if ok:
        print(f"Venv ready: {worktree_path / '.venv'}")
    else:
        print(
            "⚠️  venv provisioning failed — the worktree is still usable.",
            file=sys.stderr,
        )
        print(
            "    Provision it from the session before running tests:",
            file=sys.stderr,
        )
        # shlex.quote keeps the recovery line paste-safe for paths with
        # spaces or metacharacters (the bash %q contract) — a plain
        # path renders unquoted, which the parity tests pin.
        print(
            f"    cd {shlex.quote(str(worktree_path))} && "
            "./scripts/core/project setup --no-hooks",
            file=sys.stderr,
        )


def main(argv: list[str] | None = None, anchor: Path | None = None) -> None:
    """Create a fully-provisioned per-task worktree.

    *anchor* is the directory the primary clone is resolved FROM — the
    entry script passes its own location so invocation from inside
    another worktree still targets the shared primary; library callers
    default to the current directory.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    anchor = Path(anchor) if anchor else Path.cwd()

    task_id = args[0] if len(args) > 0 else ""
    slug = args[1] if len(args) > 1 else ""
    if not task_id:
        _fail("Usage: new-worktree.sh <TASK-ID> [slug]")
    if not re.match(r"^[A-Za-z]+-[0-9]+$", task_id):
        _fail(f"Error: TASK-ID must look like PREFIX-NNNN (got: {task_id})")
    # Normalize case like `project start` does — task files, branches
    # and worktree dirs are always uppercase-ID.
    task_id = task_id.upper()

    primary_root = resolve_primary_root(anchor)
    worktrees_dir = primary_root.parent / "ask-worktrees"

    if not slug:
        slug = derive_slug(primary_root, task_id)

    branch = f"feature/{task_id}-{slug}"
    worktree_path = worktrees_dir / task_id

    # Refuse on anything that already exists (idempotent-safe, N1).
    if worktree_path.exists():
        _fail(
            f"Error: worktree path already exists: {worktree_path}",
            "       Remove it first (planner owns removal, post-retro):",
            f"       git -C {primary_root} worktree remove {worktree_path}",
        )
    branch_check = gitio.run_git(
        primary_root, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"
    )
    if branch_check is not None and branch_check.returncode == 0:
        _fail(
            f"Error: branch already exists: {branch}",
            "       Delete it or pass a different slug.",
        )

    # Pre-flight the provisioning sources BEFORE creating anything
    # (temp-then-commit spirit): a missing artifact refuses cleanly,
    # never leaves a half-provisioned worktree behind a "ready" banner.
    for rel in PROVISION_LINKS:
        if not (primary_root / rel).exists():
            lines = [f"Error: required artifact missing in primary clone: {rel}"]
            if rel == ".adversarial/evaluators":
                lines.append(
                    "       Install first: ./scripts/core/project install-evaluators"
                )
            _fail(*lines)

    # Fetch fresh, branch from origin/main (pilot friction #2).
    print("Fetching origin...")
    fetch = gitio.run_git(primary_root, "fetch", "origin", timeout=300, capture=False)
    if fetch is None or fetch.returncode != 0:
        _fail("Error: git fetch origin failed")
    origin_main = gitio.run_git(
        primary_root, "show-ref", "--verify", "--quiet", "refs/remotes/origin/main"
    )
    if origin_main is None or origin_main.returncode != 0:
        _fail(
            "Error: origin/main does not exist after fetch —",
            "       check the remote's default branch.",
        )

    worktrees_dir.mkdir(parents=True, exist_ok=True)
    print(f"Creating worktree {worktree_path} on {branch} (from origin/main)...")
    add = gitio.run_git(
        primary_root,
        "worktree",
        "add",
        str(worktree_path),
        "-b",
        branch,
        "origin/main",
        timeout=300,
    )
    if add is None or add.returncode != 0:
        if add is not None and add.stderr:
            sys.stderr.write(add.stderr)
        _fail(f"Error: git worktree add failed for {worktree_path}")

    # From here on a failure leaves a half-provisioned worktree — tell
    # the operator how to reset (the bash ERR trap), never delete
    # automatically.
    try:
        _provision_links(primary_root, worktree_path, branch)
        _generate_serena_config(primary_root, worktree_path, task_id)
    except SystemExit:
        raise
    except OSError as exc:
        print("Provisioning failed — to retry from scratch:", file=sys.stderr)
        for line in _recovery_lines(primary_root, worktree_path, branch):
            print(line, file=sys.stderr)
        print(f"  (cause: {exc})", file=sys.stderr)
        sys.exit(1)

    _provision_venv(worktree_path)

    print()
    print(f"✅ Worktree ready: {worktree_path} (branch: {branch})")
    print()
    print("⚠️  LAUNCH: open the session tab with its working directory set to")
    print(f"    {worktree_path}")
    print("    Running the session from the primary clone costs a cd prefix on")
    print("    every command (measured: ~40 in the KIT-0043 pilot).")
    print()
    print("    Serena: activate by ABSOLUTE PATH, never by the primary's name —")
    print(f'    activate_project("{worktree_path}")')
    print("    (the name resolves to the PRIMARY clone; bulk edits would hit")
    print("    main's checkout — KIT-0069).")
    print()
    print("    .venv here is a real per-worktree venv (never a symlink —")
    print("    KIT-0065). Scratch dirs: use mktemp -d and list leftovers for")
    print("    operator sweep; the rm -rf deny is settled policy.")
    sys.exit(0)

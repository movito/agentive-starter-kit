"""Console entry point (``agentive``) for agentive-kit (KIT-0090 F2).

Exposes the migrated subcommand surface; the remaining legacy commands
(``doctor``, ``install-evaluators``, ``sync``, …) join it PR by PR
through the phase-1 series, and ``./scripts/core/project`` stays the
full surface in the meantime.

Root discovery is the one deliberate behavior change from the legacy
script: the CLI resolves the project from the CURRENT DIRECTORY (walk
up to ``.kit/`` + ``CLAUDE.md``; see ``agentive_kit.root``) and refuses
loudly outside a kit project — never operating on a guessed root.
"""

from __future__ import annotations

import sys
from pathlib import Path

import agentive_kit
from agentive_kit import lifecycle
from agentive_kit.root import RootNotFoundError, find_project_root

_USAGE = f"""\
agentive-kit v{agentive_kit.__version__}
==================================

Usage: agentive <command> [options]

Task Management:
  move <id> <status>   Move task to folder and update Status field
  complete <id>        Move task to done (shorthand)
  start <id>           Move task to in-progress (shorthand)
  block <id>           Move task to blocked (shorthand)
  validate             Validate all task statuses match folders

Gates:
  preflight [flags]         Run the 7 completion gates for the current PR
                            (--pr N --task ID --repo owner/name; see
                            'agentive preflight --help')
  review-input <id> [flags] Assemble the adversarial code-review input
                            file (--base <branch> --format diff|full)
  review-helper <sub> ...   gh review helper (reply/resolve/threads/
                            comments/summary; --repo owner/name)

Other:
  help                 Show this help message
  version              Show version information

Valid statuses for 'move':
  {', '.join(lifecycle.STATUS_FOLDER_MAP.keys())}

Runs from anywhere inside a kit-made repository (the project root is
discovered by walking up from the current directory). The commands not
yet migrated from ./scripts/core/project remain available there.
"""


def _project_root() -> Path:
    """Discover the project root or exit loudly (never guess)."""
    try:
        return find_project_root()
    except RootNotFoundError as exc:
        print(exc)
        sys.exit(1)


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv

    if not args:
        print(_USAGE)
        sys.exit(0)

    command = args[0].lower()

    # membership: command-alias vocabulary checks, not identifier
    # equality (same for the shorthand dict-key test below)
    if command in ("help", "-h", "--help"):
        print(_USAGE)
        sys.exit(0)

    if command in ("version", "--version"):
        print(f"agentive-kit v{agentive_kit.__version__}")
        sys.exit(0)

    # Exact argument counts: surplus arguments are rejected, not
    # silently ignored — a mistyped automation call must fail loudly
    # (CodeRabbit, PR #108).
    if command == "move":
        if len(args) != 3:
            print("Usage: agentive move <task-id> <status>")
            print("       agentive move ASK-0001 done")
            valid = ", ".join(lifecycle.STATUS_FOLDER_MAP.keys())
            print(f"       Valid statuses: {valid}")
            sys.exit(1)
        result = lifecycle.move_task(args[1], args[2], _project_root())
        sys.exit(0 if result and not result.status_update_failed else 1)

    # Shorthands for common moves
    shorthand_targets = {
        "start": "in-progress",
        "complete": "done",
        "block": "blocked",
    }
    if command in shorthand_targets:
        if len(args) != 2:
            print(f"Usage: agentive {command} <task-id>")
            sys.exit(1)
        result = lifecycle.move_task(
            args[1], shorthand_targets[command], _project_root()
        )
        sys.exit(0 if result and not result.status_update_failed else 1)

    if command == "preflight":
        # Flags pass through verbatim — preflight owns its own parsing
        # (including --help) so the shimmed script and the console
        # entry behave identically.
        from agentive_kit import preflight

        preflight.main(args[1:])
        return  # unreachable — preflight.main() always sys.exit()s

    if command == "review-input":
        from agentive_kit import review_input

        review_input.main(args[1:])
        return  # unreachable — review_input.main() always sys.exit()s

    if command == "review-helper":
        from agentive_kit import review_input

        review_input.helper_main(args[1:])
        return  # unreachable — helper_main() always sys.exit()s

    if command == "validate":
        if len(args) != 1:
            print("Usage: agentive validate")
            sys.exit(1)
        report = lifecycle.validate_all_tasks(_project_root())
        sys.exit(0 if report.ok else 1)

    print(f"❌ Unknown command: {command}")
    print("Run 'agentive help' for available commands.")
    print("Commands not yet migrated remain in ./scripts/core/project.")
    sys.exit(1)


if __name__ == "__main__":
    main()

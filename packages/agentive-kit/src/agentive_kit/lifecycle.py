"""Task lifecycle: status moves, validation, coordination metadata.

Extracted verbatim-in-behavior from ``scripts/core/project`` (KIT-0090
F1); the existing test suite is the spec. One deliberate behavior
change rides the extraction per KIT-0090 F6: the KIT-0086 single-writer
guard on ``agent-handoffs.json`` (see ``sync_coordination_metadata``).

Error strategy: CLI layer — failures print a clear message and return
a falsy value; they never raise (matching the legacy script, and
``patterns.yml`` → ``error_strategies``).
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from agentive_kit import gitio
from agentive_kit.models import (
    MetadataSyncNote,
    StatusIssue,
    TaskMove,
    ValidationReport,
)

# Status to folder mapping
STATUS_FOLDER_MAP = {
    "backlog": "1-backlog",
    "todo": "2-todo",
    "in-progress": "3-in-progress",
    "in-review": "4-in-review",
    "done": "5-done",
    "canceled": "6-canceled",
    "blocked": "7-blocked",
}

# Folder to Linear-native status mapping
FOLDER_STATUS_MAP = {
    "1-backlog": "Backlog",
    "2-todo": "Todo",
    "3-in-progress": "In Progress",
    "4-in-review": "In Review",
    "5-done": "Done",
    "6-canceled": "Canceled",
    "7-blocked": "Blocked",
}

# The one branch on which lifecycle commands may write the shared
# coordination JSON (KIT-0086 F1): the planner runs lifecycle moves on
# main; every other writer is a feature-branch session, and those stop
# touching the file entirely.
HANDOFFS_WRITE_BRANCH = "main"


def find_task_file(task_id: str, project_dir: Path) -> Path | None:
    """Find a task file by ID across all workflow folders."""
    tasks_dir = project_dir / ".kit" / "tasks"

    # Normalize task ID (handle ASK-0001 or ASK-1)
    task_id_upper = task_id.upper()

    for folder in tasks_dir.iterdir():
        if not folder.is_dir():
            continue
        for file in folder.glob("*.md"):
            if task_id_upper in file.name.upper():
                return file
    return None


def update_status_in_file(file_path: Path, new_status: str) -> bool:
    """Update the Status field in a task file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        new_content = re.sub(
            r"(\*\*Status\*\*:\s*)(\w+(?:\s+\w+)?)",
            f"\\1{new_status}",
            content,
            count=1,
        )
        if new_content != content:
            file_path.write_text(new_content, encoding="utf-8")
            return True
        return False
    except (OSError, UnicodeDecodeError) as e:
        print(f"❌ Error updating file: {e}")
        return False


def sync_coordination_metadata(
    task_id: str, file_name: str, target_folder: str, project_dir: Path
) -> list[MetadataSyncNote]:
    """Rewrite the moved task's path in coordination metadata (KIT-0040 F2).

    A status move changes the task file's numbered folder, stranding
    stale paths in ``.kit/context/agent-handoffs.json`` and the task's
    ``HANDOFF-*.md`` files. Only strings matching
    ``.kit/tasks/<status-folder>/<this task's file name>`` are
    rewritten — nothing else is touched. Failures warn and never block
    the already completed move (CLI-layer error strategy).

    KIT-0086 single-writer guard (F1, closed by reference here): the
    shared ``agent-handoffs.json`` is written ONLY when this checkout
    is on ``main`` — the planner is its single writer, and
    feature-branch lifecycle moves must produce zero diff in it (the
    KIT-0084 / PR #105 squash-merge conflict class). An undeterminable
    branch (not a git repo, detached HEAD, git absent) skips the write
    too: fail-safe over fail-open. The task's own ``HANDOFF-*.md``
    files are same-branch artifacts with no cross-branch writer, so
    they are rewritten regardless of branch. Stale-path drift in the
    skipped JSON is surfaced by a doctor check (KIT-0086 F2), not here.
    """
    notes: list[MetadataSyncNote] = []
    context_dir = project_dir / ".kit" / "context"
    if not context_dir.is_dir():
        return notes

    pattern = re.compile(r"\.kit/tasks/[0-9]+-[a-z-]+/" + re.escape(file_name))
    new_path = f".kit/tasks/{target_folder}/{file_name}"

    handoffs_json = context_dir / "agent-handoffs.json"
    targets = []
    if gitio.current_branch(project_dir) == HANDOFFS_WRITE_BRANCH:
        targets.append(handoffs_json)
    else:
        notes.append(
            MetadataSyncNote(
                path=handoffs_json,
                action="skipped",
                detail=f"not on {HANDOFFS_WRITE_BRANCH} — planner owns this file",
            )
        )
    targets.extend(sorted(context_dir.glob(f"{task_id.upper()}-HANDOFF-*.md")))
    for meta_file in targets:
        if not meta_file.is_file():
            continue
        try:
            content = meta_file.read_text(encoding="utf-8")
            updated = pattern.sub(new_path, content)
            if updated != content:
                meta_file.write_text(updated, encoding="utf-8")
                rel = meta_file.relative_to(project_dir)
                print(f"🔗 Updated task path in {rel}")
                notes.append(MetadataSyncNote(path=meta_file, action="updated"))
        except (OSError, UnicodeDecodeError) as e:
            # UnicodeDecodeError is a ValueError, not an OSError — a
            # non-UTF-8 coordination file must warn, not break the move.
            print(f"⚠️  Could not update {meta_file.name}: {e}")
            notes.append(
                MetadataSyncNote(path=meta_file, action="warned", detail=str(e))
            )
    return notes


def move_task(task_id: str, target_status: str, project_dir: Path) -> TaskMove | None:
    """Move a task to a new folder and update its Status field.

    Returns a :class:`TaskMove` (truthy) on success, ``None`` on any
    failure — callers that only need pass/fail keep working unchanged.
    """
    # Normalize target status
    target_lower = target_status.lower().replace("_", "-").replace(" ", "-")

    if target_lower not in STATUS_FOLDER_MAP:
        print(f"❌ Unknown status: {target_status}")
        print(f"   Valid statuses: {', '.join(STATUS_FOLDER_MAP.keys())}")
        return None

    target_folder = STATUS_FOLDER_MAP[target_lower]
    linear_status = FOLDER_STATUS_MAP[target_folder]

    task_file = find_task_file(task_id, project_dir)
    if not task_file:
        print(f"❌ Task not found: {task_id}")
        return None

    current_folder = task_file.parent.name

    if current_folder == target_folder:
        print(f"ℹ️  Task already in {target_folder}")
        # Still update status field if needed
        field_updated = update_status_in_file(task_file, linear_status)
        # Re-running a move doubles as a repair action for metadata that
        # drifted out of sync with the task's folder.
        sync_coordination_metadata(task_id, task_file.name, target_folder, project_dir)
        return TaskMove(
            task_id=task_id,
            file_name=task_file.name,
            from_folder=current_folder,
            to_folder=target_folder,
            status=linear_status,
            moved=False,
            status_field_updated=field_updated,
        )

    target_dir = project_dir / ".kit" / "tasks" / target_folder
    target_path = target_dir / task_file.name

    try:
        shutil.move(str(task_file), str(target_path))
        print(f"📁 Moved: {current_folder} → {target_folder}")
    except (OSError, shutil.Error) as e:
        print(f"❌ Error moving file: {e}")
        return None

    field_updated = update_status_in_file(target_path, linear_status)
    if field_updated:
        print(f"✏️  Updated: **Status**: {linear_status}")

    sync_coordination_metadata(task_id, target_path.name, target_folder, project_dir)

    print(f"✅ Task {task_id} is now {linear_status}")
    return TaskMove(
        task_id=task_id,
        file_name=target_path.name,
        from_folder=current_folder,
        to_folder=target_folder,
        status=linear_status,
        moved=True,
        status_field_updated=field_updated,
    )


def validate_all_tasks(project_dir: Path) -> ValidationReport:
    """Validate all task files have matching Status and folder.

    Returns a :class:`ValidationReport`; check ``report.ok`` for
    pass/fail (the report object itself is always truthy).
    """
    tasks_dir = project_dir / ".kit" / "tasks"
    issues: list[StatusIssue] = []
    checked = 0

    for folder in tasks_dir.iterdir():
        if not folder.is_dir():
            continue
        if folder.name in ["8-archive", "9-reference"]:
            continue
        if folder.name not in FOLDER_STATUS_MAP:
            continue

        expected_status = FOLDER_STATUS_MAP[folder.name]

        for file in folder.glob("*.md"):
            checked += 1
            content = file.read_text(encoding="utf-8")
            match = re.search(r"\*\*Status\*\*:\s*(\w+(?:\s+\w+)?)", content)

            if not match:
                issues.append(StatusIssue(file.name, "No Status field found"))
                continue

            actual_status = match.group(1).strip()
            if actual_status != expected_status:
                issues.append(
                    StatusIssue(
                        file.name,
                        f"Status '{actual_status}' != folder '{expected_status}'",
                    )
                )

    if issues:
        print(f"❌ Found {len(issues)} status mismatches:\n")
        for issue in issues:
            print(f"  • {issue.file_name}: {issue.detail}")
        print("\nTo fix, use: ./scripts/core/project move <task-id> <status>")
    else:
        print(f"✅ All {checked} tasks have matching Status and folder")
    return ValidationReport(checked=checked, issues=issues)

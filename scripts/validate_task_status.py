#!/usr/bin/env python3
"""
Validate Task Status
====================

Pre-commit hook to validate that task Status field matches folder location.

Usage:
    python scripts/validate_task_status.py [file1.md file2.md ...]

Exit codes:
    0 - All tasks valid
    1 - Validation errors found
"""

import re
import sys
from pathlib import Path
from typing import Optional, Tuple

# Folder to expected status mapping
FOLDER_STATUS_MAP = {
    "1-backlog": "Backlog",
    "2-todo": "Todo",
    "3-in-progress": "In Progress",
    "4-in-review": "In Review",
    "5-done": "Done",
    "6-canceled": "Canceled",
    "7-blocked": "Blocked",
}

# Folders that don't require status validation
EXCLUDED_FOLDERS = {"8-archive", "9-reference"}


def get_folder_from_path(file_path: Path) -> Optional[str]:
    """Extract the workflow folder name from a task file path."""
    parts = file_path.parts
    for i, part in enumerate(parts):
        if part == "tasks" and i + 1 < len(parts):
            return parts[i + 1]
    return None


def get_status_from_file(file_path: Path) -> Optional[str]:
    """Extract the Status field from a task file."""
    try:
        content = file_path.read_text()
        # Match **Status**: Value or **Status:** Value
        match = re.search(r"\*\*Status\*\*:\s*(\w+(?:\s+\w+)?)", content)
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return None


def validate_task(file_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Validate that a task's Status field matches its folder location.

    Returns:
        (is_valid, error_message)
    """
    folder = get_folder_from_path(file_path)

    # Skip excluded folders
    if folder in EXCLUDED_FOLDERS:
        return True, None

    # Skip if not in a recognized folder
    if folder not in FOLDER_STATUS_MAP:
        return True, None

    expected_status = FOLDER_STATUS_MAP[folder]
    actual_status = get_status_from_file(file_path)

    if actual_status is None:
        return False, f"Could not find Status field in {file_path}"

    if actual_status != expected_status:
        return False, (
            f"Status mismatch in {file_path.name}:\n"
            f"  Folder: {folder} (expects '{expected_status}')\n"
            f"  Status: '{actual_status}'\n"
            f"  Fix: Update **Status**: {expected_status}"
        )

    return True, None


def main():
    """Validate task files passed as arguments."""
    if len(sys.argv) < 2:
        print("Usage: validate_task_status.py [file1.md file2.md ...]")
        sys.exit(0)

    errors = []

    for arg in sys.argv[1:]:
        file_path = Path(arg)

        # Only validate task files
        if not file_path.name.endswith(".md"):
            continue
        if "delegation/tasks/" not in str(file_path):
            continue

        is_valid, error = validate_task(file_path)
        if not is_valid:
            errors.append(error)

    if errors:
        print("❌ Task status validation failed:\n")
        for error in errors:
            print(f"{error}\n")
        print("To fix: Update the Status field to match the folder, or use:")
        print("  ./scripts/project move <task-id> <status>")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

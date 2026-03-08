"""
Linear Sync Utilities
=====================

Helper functions for syncing task files to Linear.

Functions:
    - is_linear_native_status: Check if status is Linear-native
    - determine_status_from_path: Map folder to status
    - determine_final_status: Resolve status with priority rules
    - migrate_legacy_status: Update legacy statuses in files
    - should_sync_task: Check if task should be synced
    - parse_task_metadata: Extract metadata from task file
    - get_github_file_url: Generate GitHub URL for task file
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

# Import logging configuration - support both direct script execution and package import
try:
    from scripts.logging_config import setup_logging
except ImportError:
    from logging_config import setup_logging

# Initialize logger
logger = setup_logging("agentive.utils")

# =============================================================================
# STATUS VALIDATION
# =============================================================================

# Linear-native status values (case-sensitive)
LINEAR_NATIVE_STATUSES = {
    "Backlog",
    "Todo",
    "In Progress",
    "In Review",
    "Done",
    "Blocked",
    "Canceled",
}

# Folder to status mapping
FOLDER_STATUS_MAP = {
    "1-backlog": "Backlog",
    "2-todo": "Todo",
    "3-in-progress": "In Progress",
    "4-in-review": "In Review",
    "5-done": "Done",
    "6-canceled": "Canceled",
    "7-blocked": "Blocked",
}

# Legacy to Linear-native status mapping
LEGACY_STATUS_MAP = {
    "draft": "Backlog",
    "planning": "Backlog",
    "ready": "Backlog",
    "in_progress": "In Progress",
    "review": "In Review",
    "testing": "In Review",
    "completed": "Done",
    "blocked": "Blocked",
}


def is_linear_native_status(status: str) -> bool:
    """
    Check if status is Linear-native (not legacy).

    Linear-native statuses (case-sensitive):
    - Backlog
    - Todo
    - In Progress
    - In Review
    - Done
    - Blocked
    - Canceled

    Args:
        status: Status string to check

    Returns:
        True if status is Linear-native, False otherwise
    """
    return status in LINEAR_NATIVE_STATUSES


# =============================================================================
# STATUS DETERMINATION
# =============================================================================


def determine_status_from_path(task_file: Path) -> Optional[str]:
    """
    Extract status from folder path.

    Folder → Status mapping:
    - 1-backlog → Backlog
    - 2-todo → Todo
    - 3-in-progress → In Progress
    - 4-in-review → In Review
    - 5-done → Done
    - 6-canceled → Canceled
    - 7-blocked → Blocked
    - Unknown folders → None

    Args:
        task_file: Path to task file

    Returns:
        Status string or None if folder not recognized
    """
    # Get folder name from path
    parts = task_file.parts

    # Find the folder within tasks directory
    for i, part in enumerate(parts):
        if part == "tasks" and i + 1 < len(parts):
            folder = parts[i + 1]
            return FOLDER_STATUS_MAP.get(folder)

    return None


def determine_final_status(status_field: Optional[str], task_file: Path) -> str:
    """
    Determine final status using priority rules.

    Priority order:
    1. Status field (if Linear-native)
    2. Folder location (if recognized)
    3. Default to "Backlog"

    Args:
        status_field: Status from task file metadata (can be None)
        task_file: Path to task file

    Returns:
        Final status to use for Linear sync
    """
    # Priority 1: Status field (if Linear-native)
    if status_field and is_linear_native_status(status_field):
        return status_field

    # Priority 2: Folder location
    folder_status = determine_status_from_path(task_file)
    if folder_status:
        return folder_status

    # Priority 3: Default to Backlog
    return "Backlog"


# =============================================================================
# LEGACY STATUS MIGRATION
# =============================================================================


def migrate_legacy_status(task_file: Path, legacy_status: str) -> bool:
    """
    Migrate legacy status to Linear-native (update file).

    This UPDATES the file content, replacing the legacy status with the
    Linear-native equivalent. This is NOT just mapping - the file is modified.

    Legacy → Linear-native mappings:
    - draft/Draft/DRAFT → Backlog
    - planning → Backlog
    - ready → Backlog
    - in_progress → In Progress
    - review → In Review
    - testing → In Review
    - completed → Done
    - blocked → Blocked

    Args:
        task_file: Path to task file
        legacy_status: Legacy status value to migrate

    Returns:
        True if file was updated, False if no update needed
    """
    # Don't migrate if already Linear-native
    if is_linear_native_status(legacy_status):
        return False

    # Get Linear-native equivalent (case-insensitive lookup)
    linear_status = LEGACY_STATUS_MAP.get(legacy_status.lower())

    if not linear_status:
        # Not a recognized legacy status, no update needed
        return False

    # Read file content
    content = task_file.read_text(encoding="utf-8")

    # Replace Status field (preserve formatting)
    # Pattern: **Status**: <value>
    pattern = r"(\*\*Status\*\*:\s*)" + re.escape(legacy_status)
    replacement = r"\g<1>" + linear_status

    updated_content = re.sub(pattern, replacement, content)

    # Check if anything changed
    if updated_content == content:
        return False

    # Write updated content
    task_file.write_text(updated_content, encoding="utf-8")

    logger.info(
        "🔄 Migrated %s: '%s' → '%s'", task_file.name, legacy_status, linear_status
    )

    return True


# =============================================================================
# SYNC EXCLUSION
# =============================================================================


def should_sync_task(task_file: Path) -> bool:
    """
    Determine if task should be synced (exclude archive/reference).

    Archive (8-archive) and reference (9-reference) folders should NOT be synced.

    Args:
        task_file: Path to task file

    Returns:
        True if task should be synced, False if excluded
    """
    # Get folder name from path
    parts = task_file.parts

    # Find the folder within tasks directory
    for i, part in enumerate(parts):
        if part == "tasks" and i + 1 < len(parts):
            folder = parts[i + 1]
            # Exclude archive and reference folders
            if folder in ["8-archive", "9-reference"]:
                return False
            break

    return True


# =============================================================================
# TASK PARSING
# =============================================================================


def parse_task_metadata(task_file: Path) -> Dict[str, Any]:
    """
    Parse task file and extract metadata.

    Args:
        task_file: Path to task file

    Returns:
        Dict with keys: task_id, title, status, priority, assignee, description

    Raises:
        ValueError: If file is empty, missing title, or has invalid task ID
    """
    # Check for empty file
    if task_file.stat().st_size == 0:
        raise ValueError(f"Task file is empty: {task_file}")

    content = task_file.read_text(encoding="utf-8")

    if not content.strip():
        raise ValueError(f"Task file is empty: {task_file}")

    # Extract task ID from filename
    filename = task_file.name
    task_id_match = re.search(r"(TASK-\d{4})", filename)
    if not task_id_match:
        # Try ASK pattern (for starter kit)
        task_id_match = re.search(r"(ASK-\d{4})", filename)
        if not task_id_match:
            raise ValueError(f"No valid task ID found in filename: {filename}")

    task_id = task_id_match.group(1)

    # Extract title from first heading
    # Pattern: # TASK-0001: Title or # TASK-0001-slug: Title
    title_match = re.search(
        r"^#\s+(?:TASK-\d{4}|ASK-\d{4})(?:[-_a-zA-Z0-9]*):\s*(.+)$",
        content,
        re.MULTILINE,
    )
    if not title_match:
        raise ValueError(f"No title found in task file: {filename}")

    title = title_match.group(1).strip()

    # Extract metadata fields
    status = _extract_metadata_field(content, "Status")
    priority = _extract_metadata_field(content, "Priority")
    assignee = _extract_metadata_field(content, "Assigned To")
    effort = _extract_metadata_field(content, "Estimated Effort")

    # Extract description (from Overview section)
    desc_match = re.search(
        r"(?:## Overview|## Executive Summary|## Description)\s*\n\n(.+?)(?=\n##|\Z)",
        content,
        re.DOTALL,
    )
    description = desc_match.group(1).strip() if desc_match else content[:500]

    return {
        "task_id": task_id,
        "title": title,
        "status": status,
        "priority": priority,
        "assignee": assignee,
        "estimated_effort": effort,
        "description": description,
        "file_path": str(task_file),
    }


def _extract_metadata_field(content: str, field: str) -> Optional[str]:
    """Extract metadata field from content."""
    pattern = rf"\*\*{field}\*\*:\s*(.+?)(?:\n|$)"
    match = re.search(pattern, content)
    if match:
        value = match.group(1).strip()
        # Remove markdown formatting
        value = re.sub(r"\*\*|✅|⚠️|🔴|📝", "", value).strip()
        return value if value else None
    return None


# =============================================================================
# GITHUB URL GENERATION
# =============================================================================


def get_github_file_url(task_file: Path) -> str:
    """
    Generate GitHub URL for task file.

    Uses GITHUB_REPO_URL env var if set, otherwise auto-detects from git remote.

    Args:
        task_file: Path to task file

    Returns:
        GitHub URL to the file in the repository
    """
    # Try env var first
    repo_url = os.environ.get("GITHUB_REPO_URL")

    if not repo_url:
        # Auto-detect from git remote
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True,
            )
            remote_url = result.stdout.strip()

            # Convert git URL to HTTPS URL
            if remote_url.startswith("git@github.com:"):
                # git@github.com:org/repo.git -> https://github.com/org/repo
                repo_url = remote_url.replace("git@github.com:", "https://github.com/")
            elif remote_url.startswith("https://github.com/"):
                repo_url = remote_url
            else:
                repo_url = remote_url

            # Remove .git suffix
            repo_url = repo_url.rstrip(".git")

        except (subprocess.CalledProcessError, FileNotFoundError):
            repo_url = "https://github.com/unknown/repo"

    # Get relative path from repo root
    try:
        abs_path = task_file.resolve()
        # Find repo root (where .git is)
        repo_root = abs_path
        while repo_root.parent != repo_root:
            if (repo_root / ".git").exists():
                break
            repo_root = repo_root.parent
        else:
            repo_root = Path.cwd()

        rel_path = abs_path.relative_to(repo_root)
    except (ValueError, OSError):
        rel_path = task_file

    return f"{repo_url}/blob/main/{rel_path}"

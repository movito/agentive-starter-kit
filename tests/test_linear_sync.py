"""
Tests for Linear Sync Infrastructure
=====================================

TDD test suite for syncing task files to Linear.

Test Categories:
    1. Task file parsing (TaskParser)
    2. Status determination (field > folder > default)
    3. Legacy status migration
    4. Sync exclusion rules (archive/reference folders)
    5. LinearClient operations (mocked)

Usage:
    pytest tests/test_linear_sync.py -v

TDD Phase: RED (tests written, implementation pending)
"""

import re
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def task_content_valid():
    """Valid task file content with all metadata."""
    return """# TASK-0001: Implement Feature X

**Status**: Todo
**Priority**: high
**Assigned To**: feature-developer
**Estimated Effort**: 2-3 hours
**Created**: 2025-11-28
**Linear ID**:

## Overview

This task implements feature X for the project.

## Requirements

1. Requirement one
2. Requirement two
"""


@pytest.fixture
def task_content_legacy_status():
    """Task file with legacy (non-Linear-native) status."""
    return """# TASK-0002: Legacy Status Task

**Status**: draft
**Priority**: medium

## Overview

Task with legacy status that needs migration.
"""


@pytest.fixture
def task_content_no_title():
    """Task file missing title."""
    return """**Status**: Todo
**Priority**: medium

## Overview

Missing the title heading.
"""


@pytest.fixture
def task_content_no_status():
    """Task file missing status field."""
    return """# TASK-0003: No Status Task

**Priority**: medium

## Overview

Task without status field.
"""


@pytest.fixture
def tmp_task_file(tmp_path, task_content_valid):
    """Create a temporary task file."""
    task_file = (
        tmp_path
        / "delegation"
        / "tasks"
        / "2-todo"
        / "TASK-0001-implement-feature-x.md"
    )
    task_file.parent.mkdir(parents=True, exist_ok=True)
    task_file.write_text(task_content_valid)
    return task_file


@pytest.fixture
def tmp_task_file_legacy(tmp_path, task_content_legacy_status):
    """Create a temporary task file with legacy status."""
    task_file = (
        tmp_path / "delegation" / "tasks" / "1-backlog" / "TASK-0002-legacy-status.md"
    )
    task_file.parent.mkdir(parents=True, exist_ok=True)
    task_file.write_text(task_content_legacy_status)
    return task_file


@pytest.fixture
def tmp_task_file_archive(tmp_path, task_content_valid):
    """Create a temporary task file in archive folder."""
    task_file = (
        tmp_path / "delegation" / "tasks" / "8-archive" / "TASK-0099-archived.md"
    )
    task_file.parent.mkdir(parents=True, exist_ok=True)
    task_file.write_text(task_content_valid)
    return task_file


# =============================================================================
# TASK PARSING TESTS
# =============================================================================


class TestTaskParser:
    """Tests for TaskParser class."""

    def test_parse_extracts_task_id_from_filename(self, tmp_task_file):
        """TaskParser should extract task ID from filename."""
        # Import will fail until implementation exists
        from scripts.linear_sync_utils import parse_task_metadata

        # Act
        metadata = parse_task_metadata(tmp_task_file)

        # Assert
        assert metadata["task_id"] == "TASK-0001"

    def test_parse_extracts_title_from_heading(self, tmp_task_file):
        """TaskParser should extract title from first heading."""
        from scripts.linear_sync_utils import parse_task_metadata

        # Act
        metadata = parse_task_metadata(tmp_task_file)

        # Assert
        assert metadata["title"] == "Implement Feature X"

    def test_parse_extracts_status_field(self, tmp_task_file):
        """TaskParser should extract status from metadata."""
        from scripts.linear_sync_utils import parse_task_metadata

        # Act
        metadata = parse_task_metadata(tmp_task_file)

        # Assert
        assert metadata["status"] == "Todo"

    def test_parse_extracts_priority_field(self, tmp_task_file):
        """TaskParser should extract priority from metadata."""
        from scripts.linear_sync_utils import parse_task_metadata

        # Act
        metadata = parse_task_metadata(tmp_task_file)

        # Assert
        assert metadata["priority"] == "high"

    def test_parse_raises_on_missing_title(self, tmp_path, task_content_no_title):
        """TaskParser should raise ValueError for missing title."""
        from scripts.linear_sync_utils import parse_task_metadata

        # Arrange
        task_file = (
            tmp_path / "delegation" / "tasks" / "2-todo" / "TASK-0099-no-title.md"
        )
        task_file.parent.mkdir(parents=True, exist_ok=True)
        task_file.write_text(task_content_no_title)

        # Act & Assert
        with pytest.raises(ValueError, match="No title found"):
            parse_task_metadata(task_file)

    def test_parse_handles_missing_status(self, tmp_path, task_content_no_status):
        """TaskParser should return None for status if field missing."""
        from scripts.linear_sync_utils import parse_task_metadata

        # Arrange
        task_file = (
            tmp_path / "delegation" / "tasks" / "2-todo" / "TASK-0003-no-status.md"
        )
        task_file.parent.mkdir(parents=True, exist_ok=True)
        task_file.write_text(task_content_no_status)

        # Act
        metadata = parse_task_metadata(task_file)

        # Assert
        assert metadata["status"] is None

    def test_parse_empty_file_raises(self, tmp_path):
        """TaskParser should raise ValueError for empty file."""
        from scripts.linear_sync_utils import parse_task_metadata

        # Arrange
        task_file = tmp_path / "delegation" / "tasks" / "2-todo" / "TASK-0000-empty.md"
        task_file.parent.mkdir(parents=True, exist_ok=True)
        task_file.write_text("")

        # Act & Assert
        with pytest.raises(ValueError, match="empty"):
            parse_task_metadata(task_file)


# =============================================================================
# STATUS DETERMINATION TESTS
# =============================================================================


class TestStatusDetermination:
    """Tests for status determination logic."""

    def test_is_linear_native_status_valid(self):
        """Valid Linear statuses should return True."""
        from scripts.linear_sync_utils import is_linear_native_status

        valid_statuses = [
            "Backlog",
            "Todo",
            "In Progress",
            "In Review",
            "Done",
            "Blocked",
            "Canceled",
        ]

        for status in valid_statuses:
            assert is_linear_native_status(status) is True

    def test_is_linear_native_status_invalid(self):
        """Invalid/legacy statuses should return False."""
        from scripts.linear_sync_utils import is_linear_native_status

        invalid_statuses = ["draft", "planning", "in_progress", "completed", "ready"]

        for status in invalid_statuses:
            assert is_linear_native_status(status) is False

    def test_is_linear_native_status_case_sensitive(self):
        """Status check should be case-sensitive."""
        from scripts.linear_sync_utils import is_linear_native_status

        # "Todo" is valid, "todo" is not
        assert is_linear_native_status("Todo") is True
        assert is_linear_native_status("todo") is False
        assert is_linear_native_status("TODO") is False

    def test_determine_status_from_folder_backlog(self, tmp_path):
        """1-backlog folder should map to Backlog status."""
        from scripts.linear_sync_utils import determine_status_from_path

        task_file = tmp_path / "delegation" / "tasks" / "1-backlog" / "TASK-0001.md"

        assert determine_status_from_path(task_file) == "Backlog"

    def test_determine_status_from_folder_todo(self, tmp_path):
        """2-todo folder should map to Todo status."""
        from scripts.linear_sync_utils import determine_status_from_path

        task_file = tmp_path / "delegation" / "tasks" / "2-todo" / "TASK-0001.md"

        assert determine_status_from_path(task_file) == "Todo"

    def test_determine_status_from_folder_in_progress(self, tmp_path):
        """3-in-progress folder should map to In Progress status."""
        from scripts.linear_sync_utils import determine_status_from_path

        task_file = tmp_path / "delegation" / "tasks" / "3-in-progress" / "TASK-0001.md"

        assert determine_status_from_path(task_file) == "In Progress"

    def test_determine_status_from_folder_in_review(self, tmp_path):
        """4-in-review folder should map to In Review status."""
        from scripts.linear_sync_utils import determine_status_from_path

        task_file = tmp_path / "delegation" / "tasks" / "4-in-review" / "TASK-0001.md"

        assert determine_status_from_path(task_file) == "In Review"

    def test_determine_status_from_folder_done(self, tmp_path):
        """5-done folder should map to Done status."""
        from scripts.linear_sync_utils import determine_status_from_path

        task_file = tmp_path / "delegation" / "tasks" / "5-done" / "TASK-0001.md"

        assert determine_status_from_path(task_file) == "Done"

    def test_determine_status_from_folder_canceled(self, tmp_path):
        """6-canceled folder should map to Canceled status."""
        from scripts.linear_sync_utils import determine_status_from_path

        task_file = tmp_path / "delegation" / "tasks" / "6-canceled" / "TASK-0001.md"

        assert determine_status_from_path(task_file) == "Canceled"

    def test_determine_status_from_folder_blocked(self, tmp_path):
        """7-blocked folder should map to Blocked status."""
        from scripts.linear_sync_utils import determine_status_from_path

        task_file = tmp_path / "delegation" / "tasks" / "7-blocked" / "TASK-0001.md"

        assert determine_status_from_path(task_file) == "Blocked"

    def test_determine_status_from_unknown_folder(self, tmp_path):
        """Unknown folder should return None."""
        from scripts.linear_sync_utils import determine_status_from_path

        task_file = (
            tmp_path / "delegation" / "tasks" / "unknown-folder" / "TASK-0001.md"
        )

        assert determine_status_from_path(task_file) is None

    def test_final_status_field_takes_priority(self, tmp_task_file):
        """Status field should take priority over folder location."""
        from scripts.linear_sync_utils import determine_final_status

        # File has Status: Todo, but is in 2-todo folder
        # Should use field value (Todo)
        status_field = "In Progress"  # Pretend field says different

        result = determine_final_status(status_field, tmp_task_file)

        assert result == "In Progress"

    def test_final_status_falls_back_to_folder(self, tmp_task_file):
        """Should fall back to folder when field is None."""
        from scripts.linear_sync_utils import determine_final_status

        status_field = None  # No status field

        result = determine_final_status(status_field, tmp_task_file)

        # File is in 2-todo folder
        assert result == "Todo"

    def test_final_status_defaults_to_backlog(self, tmp_path):
        """Should default to Backlog when no field or folder."""
        from scripts.linear_sync_utils import determine_final_status

        task_file = tmp_path / "random" / "TASK-0001.md"
        status_field = None

        result = determine_final_status(status_field, task_file)

        assert result == "Backlog"


# =============================================================================
# LEGACY STATUS MIGRATION TESTS
# =============================================================================


class TestLegacyStatusMigration:
    """Tests for legacy status migration."""

    def test_migrate_draft_to_backlog(self, tmp_task_file_legacy):
        """'draft' should migrate to 'Backlog'."""
        from scripts.linear_sync_utils import migrate_legacy_status

        # Act
        result = migrate_legacy_status(tmp_task_file_legacy, "draft")

        # Assert
        assert result is True
        content = tmp_task_file_legacy.read_text()
        assert "**Status**: Backlog" in content
        assert "**Status**: draft" not in content

    def test_migrate_in_progress_to_linear(self, tmp_path):
        """'in_progress' should migrate to 'In Progress'."""
        from scripts.linear_sync_utils import migrate_legacy_status

        # Arrange
        task_file = tmp_path / "TASK-0001.md"
        task_file.write_text("**Status**: in_progress\n")

        # Act
        result = migrate_legacy_status(task_file, "in_progress")

        # Assert
        assert result is True
        content = task_file.read_text()
        assert "**Status**: In Progress" in content

    def test_migrate_completed_to_done(self, tmp_path):
        """'completed' should migrate to 'Done'."""
        from scripts.linear_sync_utils import migrate_legacy_status

        # Arrange
        task_file = tmp_path / "TASK-0001.md"
        task_file.write_text("**Status**: completed\n")

        # Act
        result = migrate_legacy_status(task_file, "completed")

        # Assert
        assert result is True
        content = task_file.read_text()
        assert "**Status**: Done" in content

    def test_migrate_unknown_status_returns_false(self, tmp_path):
        """Unknown status should not be migrated."""
        from scripts.linear_sync_utils import migrate_legacy_status

        # Arrange
        task_file = tmp_path / "TASK-0001.md"
        task_file.write_text("**Status**: unknown_status\n")

        # Act
        result = migrate_legacy_status(task_file, "unknown_status")

        # Assert
        assert result is False

    def test_migrate_already_native_returns_false(self, tmp_task_file):
        """Already Linear-native status should not be changed."""
        from scripts.linear_sync_utils import migrate_legacy_status

        # File already has "Status: Todo" which is native
        result = migrate_legacy_status(tmp_task_file, "Todo")

        # Assert - should not modify file
        assert result is False


# =============================================================================
# SYNC EXCLUSION TESTS
# =============================================================================


class TestSyncExclusion:
    """Tests for sync exclusion rules."""

    def test_should_sync_normal_folder(self, tmp_task_file):
        """Tasks in normal folders should be synced."""
        from scripts.linear_sync_utils import should_sync_task

        assert should_sync_task(tmp_task_file) is True

    def test_should_not_sync_archive_folder(self, tmp_task_file_archive):
        """Tasks in 8-archive folder should NOT be synced."""
        from scripts.linear_sync_utils import should_sync_task

        assert should_sync_task(tmp_task_file_archive) is False

    def test_should_not_sync_reference_folder(self, tmp_path, task_content_valid):
        """Tasks in 9-reference folder should NOT be synced."""
        from scripts.linear_sync_utils import should_sync_task

        # Arrange
        task_file = tmp_path / "delegation" / "tasks" / "9-reference" / "TASK-0001.md"
        task_file.parent.mkdir(parents=True, exist_ok=True)
        task_file.write_text(task_content_valid)

        # Act & Assert
        assert should_sync_task(task_file) is False


# =============================================================================
# LINEAR CLIENT TESTS (MOCKED)
# =============================================================================


class TestLinearClient:
    """Tests for LinearClient class with mocked API."""

    def test_client_initialization(self):
        """LinearClient should initialize with API key."""
        from scripts.sync_tasks_to_linear import LinearClient

        with patch("scripts.sync_tasks_to_linear.Client"):
            client = LinearClient("test-api-key")
            assert client is not None

    def test_find_issue_by_task_id(self):
        """Should find existing issue by task ID in title."""
        from scripts.sync_tasks_to_linear import LinearClient

        # Arrange
        mock_client = MagicMock()
        mock_client.execute.return_value = {
            "issues": {
                "nodes": [
                    {
                        "id": "issue-123",
                        "identifier": "PROJ-1",
                        "title": "[TASK-0001] Test Task",
                    }
                ]
            }
        }

        with patch("scripts.sync_tasks_to_linear.Client", return_value=mock_client):
            client = LinearClient("test-api-key")
            client.client = mock_client

            # Act
            result = client.find_issue_by_identifier("TASK-0001")

            # Assert
            assert result is not None
            assert result["id"] == "issue-123"

    def test_find_issue_returns_none_when_not_found(self):
        """Should return None when issue not found."""
        from scripts.sync_tasks_to_linear import LinearClient

        # Arrange
        mock_client = MagicMock()
        mock_client.execute.return_value = {"issues": {"nodes": []}}

        with patch("scripts.sync_tasks_to_linear.Client", return_value=mock_client):
            client = LinearClient("test-api-key")
            client.client = mock_client

            # Act
            result = client.find_issue_by_identifier("TASK-9999")

            # Assert
            assert result is None


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestSyncIntegration:
    """Integration tests for end-to-end sync workflow."""

    def test_sync_creates_new_issue(self, tmp_task_file):
        """Sync should create new Linear issue for new task."""
        from scripts.sync_tasks_to_linear import sync_task

        # Arrange
        mock_client = MagicMock()
        # sync_task calls client.sync_task, which returns the issue
        mock_client.sync_task.return_value = {
            "id": "new-issue-123",
            "identifier": "PROJ-99",
        }

        # Act
        result = sync_task(tmp_task_file, mock_client, "team-123")

        # Assert
        mock_client.sync_task.assert_called_once()
        assert result["identifier"] == "PROJ-99"

    def test_sync_updates_existing_issue(self, tmp_task_file):
        """Sync should update existing Linear issue."""
        from scripts.sync_tasks_to_linear import sync_task

        # Arrange
        mock_client = MagicMock()
        # sync_task calls client.sync_task, which handles create/update internally
        mock_client.sync_task.return_value = {
            "id": "existing-issue-123",
            "identifier": "PROJ-1",
        }

        # Act
        result = sync_task(tmp_task_file, mock_client, "team-123")

        # Assert
        mock_client.sync_task.assert_called_once()
        assert result["identifier"] == "PROJ-1"

    def test_sync_skips_archive_task(self, tmp_task_file_archive):
        """Sync should skip tasks in archive folder."""
        from scripts.sync_tasks_to_linear import sync_task

        # Arrange
        mock_client = MagicMock()

        # Act
        result = sync_task(tmp_task_file_archive, mock_client, "team-123")

        # Assert
        assert result is None
        mock_client.create_issue.assert_not_called()
        mock_client.update_issue.assert_not_called()


# =============================================================================
# GITHUB URL GENERATION TESTS
# =============================================================================


class TestGitHubUrl:
    """Tests for GitHub URL generation."""

    def test_github_url_from_env_var(self, tmp_task_file, monkeypatch):
        """Should use GITHUB_REPO_URL env var when set."""
        from scripts.linear_sync_utils import get_github_file_url

        monkeypatch.setenv("GITHUB_REPO_URL", "https://github.com/org/repo")

        result = get_github_file_url(tmp_task_file)

        assert result.startswith("https://github.com/org/repo/blob/main/")

    def test_github_url_auto_detect(self, tmp_task_file, monkeypatch):
        """Should auto-detect from git remote when env var not set."""
        from scripts.linear_sync_utils import get_github_file_url

        monkeypatch.delenv("GITHUB_REPO_URL", raising=False)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="https://github.com/detected/repo.git\n", returncode=0
            )

            result = get_github_file_url(tmp_task_file)

            assert "github.com" in result


# =============================================================================
# TEAM RESOLUTION TESTS
# =============================================================================


class TestTeamResolution:
    """Test suite for LinearClient.resolve_team_id() method."""

    def test_resolve_team_id_with_uuid(self):
        """Should return UUID as-is when given a UUID."""
        from scripts.sync_tasks_to_linear import LinearClient

        with patch("scripts.sync_tasks_to_linear.Client"):
            client = LinearClient("test-api-key")
            uuid = "89b26800-e1e6-4998-bedf-04195e592cd9"
            result = client.resolve_team_id(uuid)

            assert result == uuid

    def test_resolve_team_id_with_key(self):
        """Should look up UUID when given a team KEY."""
        from scripts.sync_tasks_to_linear import LinearClient

        with patch("scripts.sync_tasks_to_linear.Client"):
            client = LinearClient("test-api-key")
            mock_gql_client = MagicMock()
            client.client = mock_gql_client

            # Mock API response with teams
            mock_gql_client.execute.return_value = {
                "teams": {
                    "nodes": [
                        {"id": "uuid-1", "key": "AL2", "name": "Agentic Lotion 2"},
                        {"id": "uuid-2", "key": "THM", "name": "Thematic"},
                    ]
                }
            }

            result = client.resolve_team_id("AL2")

            assert result == "uuid-1"
            assert mock_gql_client.execute.called

    def test_resolve_team_id_with_none(self):
        """Should call get_default_team() when given None."""
        from scripts.sync_tasks_to_linear import LinearClient

        with patch("scripts.sync_tasks_to_linear.Client"):
            client = LinearClient("test-api-key")
            mock_gql_client = MagicMock()
            client.client = mock_gql_client

            # Mock API response for get_default_team
            mock_gql_client.execute.return_value = {
                "teams": {
                    "nodes": [
                        {"id": "uuid-1", "name": "First Team"},
                    ]
                }
            }

            result = client.resolve_team_id(None)

            assert result == "uuid-1"
            assert mock_gql_client.execute.called

    def test_resolve_team_id_unknown_key_raises(self):
        """Should raise ValueError when team KEY not found."""
        from scripts.sync_tasks_to_linear import LinearClient

        with patch("scripts.sync_tasks_to_linear.Client"):
            client = LinearClient("test-api-key")
            mock_gql_client = MagicMock()
            client.client = mock_gql_client

            # Mock API response with teams
            mock_gql_client.execute.return_value = {
                "teams": {
                    "nodes": [
                        {"id": "uuid-1", "key": "AL2", "name": "Agentic Lotion 2"},
                        {"id": "uuid-2", "key": "THM", "name": "Thematic"},
                    ]
                }
            }

            with pytest.raises(ValueError) as exc_info:
                client.resolve_team_id("UNKNOWN")

            assert "Team 'UNKNOWN' not found" in str(exc_info.value)
            assert "AL2, THM" in str(exc_info.value)

    def test_resolve_team_id_empty_string_uses_default(self):
        """Should treat empty string as None and use default team."""
        from scripts.sync_tasks_to_linear import LinearClient

        with patch("scripts.sync_tasks_to_linear.Client"):
            client = LinearClient("test-api-key")
            mock_gql_client = MagicMock()
            client.client = mock_gql_client

            # Mock API response for get_default_team
            mock_gql_client.execute.return_value = {
                "teams": {
                    "nodes": [
                        {"id": "uuid-default", "name": "Default Team"},
                    ]
                }
            }

            result = client.resolve_team_id("")

            assert result == "uuid-default"

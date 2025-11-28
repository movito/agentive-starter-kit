#!/usr/bin/env python3
"""
Sync task files to Linear issues.

This script reads task markdown files from all workflow folders in delegation/tasks/
and creates/updates corresponding Linear issues using the GraphQL API.

Scans these numbered workflow folders:
    1-backlog/    - Tasks defined but not ready to start
    2-todo/       - Ready to start, dependencies met
    3-in-progress/ - Actively being worked on
    4-in-review/  - Implementation complete, under review
    5-done/       - Fully complete and verified
    6-canceled/   - Will not be implemented
    7-blocked/    - Temporarily blocked tasks

Usage:
    python scripts/sync_tasks_to_linear.py
    ./project linearsync

Environment variables required:
    LINEAR_API_KEY: Your Linear API key (loaded from .env file)
    LINEAR_TEAM_ID: Your Linear team ID (optional, will use default team)

Task file format:
    Task files must be named: TASK-####-description.md or ASK-####-description.md
    Metadata extracted from frontmatter:
    - **Status**: Backlog | Todo | In Progress | In Review | Done | Canceled | Blocked
    - **Priority**: critical | high | medium | low
    - **Assigned To**: role or name
    - **Estimated Effort**: X hours/days
    - **Dependencies**: List of task IDs
    - **Linear ID**: PRJ-## (optional - auto-populated after sync)
"""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"📋 Loaded environment from {env_path}")
except ImportError:
    # dotenv not installed, continue without it
    pass

# Import gql for GraphQL operations
try:
    from gql import Client, gql
    from gql.transport.requests import RequestsHTTPTransport
except ImportError:
    print("❌ Error: gql package not installed")
    print("   Run: pip install gql[requests]")
    sys.exit(1)

# Import local utilities - support both direct script execution and package import
try:
    from scripts.linear_sync_utils import (
        determine_final_status,
        get_github_file_url,
        is_linear_native_status,
        migrate_legacy_status,
        parse_task_metadata,
        should_sync_task,
    )
except ImportError:
    # Direct script execution (python scripts/sync_tasks_to_linear.py)
    from linear_sync_utils import (
        determine_final_status,
        get_github_file_url,
        is_linear_native_status,
        migrate_legacy_status,
        parse_task_metadata,
        should_sync_task,
    )


@dataclass
class TaskData:
    """Parsed task metadata."""

    task_id: str
    title: str
    status: str
    priority: str
    assignee: Optional[str]
    estimated_effort: Optional[str]
    dependencies: List[str]
    description: str
    file_path: str

    @property
    def linear_title(self) -> str:
        """Format title for Linear."""
        return f"[{self.task_id}] {self.title}"

    @property
    def linear_status(self) -> str:
        """Return task status (Linear-native values only)."""
        valid_statuses = {
            "Backlog",
            "Todo",
            "In Progress",
            "In Review",
            "Done",
            "Blocked",
            "Canceled",
        }
        return self.status if self.status in valid_statuses else "Backlog"

    @property
    def linear_priority(self) -> int:
        """Map priority to Linear priority (0-4, higher is more urgent)."""
        priority_map = {
            "critical": 1,  # Urgent
            "high": 2,  # High
            "medium": 3,  # Medium
            "low": 4,  # Low
        }
        priority_lower = self.priority.lower() if self.priority else "medium"
        for key, value in priority_map.items():
            if key in priority_lower:
                return value
        return 0  # No priority


class LinearClient:
    """Client for Linear GraphQL API."""

    def __init__(self, api_key: str):
        """Initialize Linear client."""
        transport = RequestsHTTPTransport(
            url="https://api.linear.app/graphql",
            headers={"Authorization": api_key},
            verify=True,
            retries=3,
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=True)
        self.team_id = None

    def get_default_team(self) -> str:
        """Get the default team ID."""
        query = gql(
            """
            query {
              teams {
                nodes {
                  id
                  name
                }
              }
            }
        """
        )

        result = self.client.execute(query)
        teams = result["teams"]["nodes"]

        if not teams:
            raise ValueError("No teams found in Linear workspace")

        team = teams[0]
        print(f"📋 Using Linear team: {team['name']} ({team['id']})")
        return team["id"]

    def resolve_team_id(self, team_identifier: Optional[str] = None) -> str:
        """
        Resolve team identifier to UUID.

        Args:
            team_identifier: Can be:
                - UUID (e.g., "89b26800-e1e6-4998-bedf-04195e592cd9") - returned as-is
                - Team KEY (e.g., "AL2") - looked up and UUID returned
                - None - uses default team

        Returns:
            Team UUID
        """
        if not team_identifier:
            return self.get_default_team()

        # Check if it's already a UUID (contains hyphens and is ~36 chars)
        if "-" in team_identifier and len(team_identifier) > 30:
            print(f"📋 Using configured team UUID: {team_identifier}")
            return team_identifier

        # Otherwise, treat it as a team KEY and look it up
        query = gql(
            """
            query {
              teams {
                nodes {
                  id
                  key
                  name
                }
              }
            }
        """
        )

        result = self.client.execute(query)
        teams = result["teams"]["nodes"]

        # Find team by KEY
        for team in teams:
            if team["key"] == team_identifier:
                print(f"📋 Using Linear team: {team['name']} ({team['id']})")
                return team["id"]

        # If no match, raise error with helpful message
        available_keys = [t["key"] for t in teams]
        raise ValueError(
            f"Team '{team_identifier}' not found. "
            f"Available teams: {', '.join(available_keys)}"
        )

    def find_issue_by_identifier(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Find existing Linear issue by task ID in title."""
        query = gql(
            """
            query FindTaskIssue($taskId: String!) {
              issues(filter: { title: { contains: $taskId } }) {
                nodes {
                  id
                  identifier
                  title
                  url
                }
              }
            }
        """
        )

        try:
            result = self.client.execute(query, variable_values={"taskId": task_id})
            issues = result["issues"]["nodes"]

            # Find exact match in title
            for issue in issues:
                if task_id in issue["title"]:
                    return issue

            return None
        except Exception as e:
            print(f"⚠️  Error searching for {task_id}: {e}")
            return None

    def create_issue(self, task: TaskData, team_id: str) -> Dict[str, Any]:
        """Create a new Linear issue."""
        mutation = gql(
            """
            mutation CreateIssue(
                $teamId: String!,
                $title: String!,
                $description: String,
                $priority: Int,
                $stateId: String
            ) {
              issueCreate(input: {
                teamId: $teamId,
                title: $title,
                description: $description,
                priority: $priority,
                stateId: $stateId
              }) {
                success
                issue {
                  id
                  identifier
                  title
                  url
                }
              }
            }
        """
        )

        state_id = self._get_state_id(team_id, task.linear_status)

        variables = {
            "teamId": team_id,
            "title": task.linear_title,
            "description": task.description,
            "priority": task.linear_priority,
            "stateId": state_id,
        }

        result = self.client.execute(mutation, variable_values=variables)

        if result["issueCreate"]["success"]:
            issue = result["issueCreate"]["issue"]
            print(f"✅ Created: {issue['identifier']} - {task.task_id}")
            print(f"   URL: {issue['url']}")
            return issue
        else:
            raise ValueError(f"Failed to create issue for {task.task_id}")

    def update_issue(
        self, issue_id: str, task: TaskData, team_id: str
    ) -> Dict[str, Any]:
        """Update an existing Linear issue."""
        mutation = gql(
            """
            mutation UpdateIssue(
                $issueId: String!,
                $title: String,
                $description: String,
                $priority: Int,
                $stateId: String
            ) {
              issueUpdate(
                id: $issueId,
                input: {
                  title: $title,
                  description: $description,
                  priority: $priority,
                  stateId: $stateId
                }
              ) {
                success
                issue {
                  id
                  identifier
                  title
                  url
                }
              }
            }
        """
        )

        state_id = self._get_state_id(team_id, task.linear_status)

        variables = {
            "issueId": issue_id,
            "title": task.linear_title,
            "description": task.description,
            "priority": task.linear_priority,
            "stateId": state_id,
        }

        result = self.client.execute(mutation, variable_values=variables)

        if result["issueUpdate"]["success"]:
            issue = result["issueUpdate"]["issue"]
            print(f"🔄 Updated: {issue['identifier']} - {task.task_id}")
            return issue
        else:
            raise ValueError(f"Failed to update issue for {task.task_id}")

    def _get_state_id(self, team_id: str, status_name: str) -> Optional[str]:
        """Get the workflow state ID for a given status name."""
        query = gql(
            """
            query GetWorkflowStates($teamId: String!) {
              team(id: $teamId) {
                states {
                  nodes {
                    id
                    name
                    type
                  }
                }
              }
            }
        """
        )

        result = self.client.execute(query, variable_values={"teamId": team_id})
        states = result["team"]["states"]["nodes"]

        # Try exact match first
        for state in states:
            if state["name"].lower() == status_name.lower():
                return state["id"]

        # Try partial match
        for state in states:
            if status_name.lower() in state["name"].lower():
                return state["id"]

        # Default to first state of appropriate type
        status_type_map = {
            "Backlog": "backlog",
            "In Progress": "started",
            "In Review": "started",
            "Done": "completed",
            "Blocked": "started",
        }

        target_type = status_type_map.get(status_name, "backlog")
        for state in states:
            if state["type"] == target_type:
                return state["id"]

        return None

    def sync_task(self, task: TaskData, team_id: str) -> Dict[str, Any]:
        """Sync a task to Linear (create or update)."""
        existing = self.find_issue_by_identifier(task.task_id)

        if existing:
            return self.update_issue(existing["id"], task, team_id)
        else:
            return self.create_issue(task, team_id)


def sync_task(
    task_file: Path, client: LinearClient, team_id: str
) -> Optional[Dict[str, Any]]:
    """
    Sync a single task file to Linear.

    Args:
        task_file: Path to task file
        client: LinearClient instance
        team_id: Linear team ID

    Returns:
        Dict with sync result (issue data from Linear)
        None if task should not be synced
    """
    # Check if task should be synced
    if not should_sync_task(task_file):
        return None

    # Parse task metadata
    try:
        metadata = parse_task_metadata(task_file)
    except ValueError as e:
        print(f"⚠️  Skipping {task_file.name}: {e}")
        return None

    # Check for legacy status and migrate if needed
    if metadata["status"] and not is_linear_native_status(metadata["status"]):
        migrate_legacy_status(task_file, metadata["status"])
        # Re-parse after migration
        metadata = parse_task_metadata(task_file)

    # Determine final status
    final_status = determine_final_status(metadata["status"], task_file)

    # Create TaskData object
    task = TaskData(
        task_id=metadata["task_id"],
        title=metadata["title"],
        status=final_status,
        priority=metadata["priority"] or "medium",
        assignee=metadata["assignee"],
        estimated_effort=metadata["estimated_effort"],
        dependencies=[],
        description=metadata["description"],
        file_path=metadata["file_path"],
    )

    # Add GitHub link to description
    github_url = get_github_file_url(task_file)
    task.description += f"\n\n---\n📁 **Task File:** [{task_file.name}]({github_url})"

    # Sync to Linear
    return client.sync_task(task, team_id)


def main():
    """Main function for sync mode."""
    print("🚀 Linear Task Sync")
    print("=" * 60)

    # Check environment
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        print("❌ Error: LINEAR_API_KEY environment variable not set")
        print("\nTo get your API key:")
        print("1. Go to https://linear.app/settings/api")
        print("2. Click 'Create new key'")
        print("3. Set LINEAR_API_KEY environment variable")
        sys.exit(1)

    # Initialize Linear client
    try:
        linear = LinearClient(api_key)
    except Exception as e:
        print(f"❌ Error connecting to Linear: {e}")
        sys.exit(1)

    # Resolve team ID - accepts UUID, team KEY (e.g., "AL2"), or None for auto-detect
    team_id = linear.resolve_team_id(os.getenv("LINEAR_TEAM_ID"))

    # Find task files from all workflow folders
    base_dir = Path("delegation/tasks")
    if not base_dir.exists():
        print(f"❌ Error: {base_dir} not found")
        sys.exit(1)

    # Look in all numbered workflow folders (1-backlog through 7-blocked)
    workflow_folders = [
        "1-backlog",
        "2-todo",
        "3-in-progress",
        "4-in-review",
        "5-done",
        "6-canceled",
        "7-blocked",
    ]

    all_files = []
    for folder in workflow_folders:
        folder_path = base_dir / folder
        if folder_path.exists():
            # Find TASK-* and ASK-* files
            task_files = list(folder_path.glob("TASK-*.md"))
            ask_files = list(folder_path.glob("ASK-*.md"))
            all_files.extend(task_files + ask_files)

    print(f"\n📂 Found {len(all_files)} task files across workflow folders\n")

    # Parse and sync tasks
    synced = 0
    skipped = 0
    errors = 0

    for task_file in sorted(all_files):
        try:
            result = sync_task(task_file, linear, team_id)
            if result:
                synced += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"❌ Error processing {task_file.name}: {e}")
            errors += 1

    # Summary
    print()
    print("=" * 60)
    print(f"✅ Synced: {synced}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Errors: {errors}")
    print()

    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

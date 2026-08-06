"""Tests for agentive_kit.lifecycle — task moves, validation, metadata sync.

Migrates TestMoveTaskMetadataSync from tests/test_project_script.py
(KIT-0090 F3) and extends it for the KIT-0086 single-writer guard,
which lands INSIDE the extracted module (KIT-0090 F6):
``agent-handoffs.json`` is written only when the checkout is on main;
feature-branch moves must produce zero diff in it. The task's own
``HANDOFF-*.md`` files are rewritten on every branch.
"""

from __future__ import annotations

import json
import subprocess

import pytest

pytest.importorskip(
    "agentive_kit", reason="agentive-kit package source present only in the kit repo"
)

from agentive_kit import lifecycle  # noqa: E402

TASK_FILE = "KIT-1234-sample-task.md"


def _git(repo, *args):
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )


def make_project(tmp_path, branch=None):
    """Build a minimal kit task tree; on a git branch when asked.

    ``branch=None`` leaves the directory a plain (non-git) tree — the
    fail-safe case for the handoffs guard.
    """
    tasks = tmp_path / ".kit" / "tasks"
    for folder in ("2-todo", "3-in-progress", "5-done"):
        (tasks / folder).mkdir(parents=True)
    task = tasks / "2-todo" / TASK_FILE
    task.write_text("# Task\n\n**Status**: Todo\n", encoding="utf-8")

    context = tmp_path / ".kit" / "context"
    context.mkdir(parents=True)
    handoffs = {
        "planner": {
            "status": "handoff_ready",
            "current_task": "KIT-1234",
            "details_link": f".kit/tasks/2-todo/{TASK_FILE}",
            "handoff_file": ".kit/context/KIT-1234-HANDOFF-feature-developer.md",
        },
        "other-agent": {
            "status": "idle",
            "current_task": None,
            "details_link": ".kit/tasks/2-todo/KIT-0002-unrelated-task.md",
        },
    }
    (context / "agent-handoffs.json").write_text(
        json.dumps(handoffs, indent=2) + "\n", encoding="utf-8"
    )
    (context / "KIT-1234-HANDOFF-feature-developer.md").write_text(
        f"# Handoff\n\n**Task**: `.kit/tasks/2-todo/{TASK_FILE}`\n",
        encoding="utf-8",
    )

    if branch is not None:
        subprocess.run(
            ["git", "init", "-q", "-b", branch, str(tmp_path)],
            check=True,
            capture_output=True,
            timeout=30,
        )
    return context


class TestHandoffsSingleWriterGuard:
    """KIT-0086 F1, closed by reference here (KIT-0090 F6)."""

    def test_move_on_main_rewrites_handoffs_json(self, tmp_path):
        context = make_project(tmp_path, branch="main")

        assert lifecycle.move_task("KIT-1234", "in-progress", tmp_path)

        data = json.loads((context / "agent-handoffs.json").read_text(encoding="utf-8"))
        assert data["planner"]["details_link"] == (
            f".kit/tasks/3-in-progress/{TASK_FILE}"
        )

    def test_move_on_feature_branch_leaves_handoffs_json_untouched(self, tmp_path):
        context = make_project(tmp_path, branch="feature/KIT-1234-sample")
        before = (context / "agent-handoffs.json").read_bytes()

        assert lifecycle.move_task("KIT-1234", "in-progress", tmp_path)

        # Zero diff — the KIT-0086 acceptance criterion, byte-for-byte.
        assert (context / "agent-handoffs.json").read_bytes() == before
        # The task's own handoff file is a same-branch artifact and IS
        # rewritten.
        handoff_md = (context / "KIT-1234-HANDOFF-feature-developer.md").read_text(
            encoding="utf-8"
        )
        assert f".kit/tasks/3-in-progress/{TASK_FILE}" in handoff_md
        assert "2-todo" not in handoff_md

    def test_move_in_non_git_tree_skips_handoffs_json(self, tmp_path):
        # Branch undeterminable (not a repo) → fail-safe: skip the
        # write, exactly as on a feature branch.
        context = make_project(tmp_path, branch=None)
        before = (context / "agent-handoffs.json").read_bytes()

        assert lifecycle.move_task("KIT-1234", "in-progress", tmp_path)

        assert (context / "agent-handoffs.json").read_bytes() == before

    def test_skip_is_reported_in_sync_notes(self, tmp_path):
        make_project(tmp_path, branch="feature/x")
        notes = lifecycle.sync_coordination_metadata(
            "KIT-1234", TASK_FILE, "3-in-progress", tmp_path
        )
        skipped = [n for n in notes if n.action == "skipped"]
        assert len(skipped) == 1
        assert skipped[0].path.name == "agent-handoffs.json"


class TestMoveTaskMetadataSync:
    """KIT-0040 F2 behavior, preserved through the extraction — all on
    main, where the JSON write is legitimate."""

    def test_move_rewrites_handoffs_json_and_handoff_file(self, tmp_path):
        context = make_project(tmp_path, branch="main")

        assert lifecycle.move_task("KIT-1234", "in-progress", tmp_path)

        data = json.loads((context / "agent-handoffs.json").read_text(encoding="utf-8"))
        assert data["planner"]["details_link"] == (
            f".kit/tasks/3-in-progress/{TASK_FILE}"
        )
        handoff_md = (context / "KIT-1234-HANDOFF-feature-developer.md").read_text(
            encoding="utf-8"
        )
        assert f".kit/tasks/3-in-progress/{TASK_FILE}" in handoff_md
        assert "2-todo" not in handoff_md

    def test_move_leaves_other_tasks_untouched(self, tmp_path):
        context = make_project(tmp_path, branch="main")

        assert lifecycle.move_task("KIT-1234", "in-progress", tmp_path)

        data = json.loads((context / "agent-handoffs.json").read_text(encoding="utf-8"))
        # The unrelated task's (stale-looking) path must be preserved.
        assert data["other-agent"]["details_link"] == (
            ".kit/tasks/2-todo/KIT-0002-unrelated-task.md"
        )

    def test_move_without_context_dir_still_succeeds(self, tmp_path):
        tasks = tmp_path / ".kit" / "tasks"
        for folder in ("2-todo", "3-in-progress"):
            (tasks / folder).mkdir(parents=True)
        (tasks / "2-todo" / TASK_FILE).write_text(
            "**Status**: Todo\n", encoding="utf-8"
        )

        assert lifecycle.move_task("KIT-1234", "in-progress", tmp_path)
        assert (tasks / "3-in-progress" / TASK_FILE).exists()

    def test_rerun_in_same_folder_repairs_stale_metadata(self, tmp_path):
        # Metadata drifted while the task is already in place: re-running
        # the move acts as a repair and rewrites the stale path.
        context = make_project(tmp_path, branch="main")
        task = tmp_path / ".kit" / "tasks" / "2-todo" / TASK_FILE
        moved = tmp_path / ".kit" / "tasks" / "3-in-progress" / TASK_FILE
        task.rename(moved)

        result = lifecycle.move_task("KIT-1234", "in-progress", tmp_path)
        assert result
        assert result.moved is False

        data = json.loads((context / "agent-handoffs.json").read_text(encoding="utf-8"))
        assert data["planner"]["details_link"] == (
            f".kit/tasks/3-in-progress/{TASK_FILE}"
        )

    def test_second_move_rewrites_again(self, tmp_path):
        context = make_project(tmp_path, branch="main")

        assert lifecycle.move_task("KIT-1234", "in-progress", tmp_path)
        assert lifecycle.move_task("KIT-1234", "done", tmp_path)

        data = json.loads((context / "agent-handoffs.json").read_text(encoding="utf-8"))
        assert data["planner"]["details_link"] == f".kit/tasks/5-done/{TASK_FILE}"

    def test_non_utf8_metadata_warns_but_move_succeeds(self, tmp_path, capsys):
        # A corrupted (non-UTF-8) coordination file must warn, never
        # break the already completed move (UnicodeDecodeError is a
        # ValueError, not an OSError).
        context = make_project(tmp_path, branch="main")
        (context / "agent-handoffs.json").write_bytes(b"\xff\xfe broken")

        assert lifecycle.move_task("KIT-1234", "in-progress", tmp_path)

        out = capsys.readouterr().out
        assert "Could not update agent-handoffs.json" in out
        # The parseable handoff file was still rewritten.
        handoff_md = (context / "KIT-1234-HANDOFF-feature-developer.md").read_text(
            encoding="utf-8"
        )
        assert f".kit/tasks/3-in-progress/{TASK_FILE}" in handoff_md


class TestMoveTask:
    def test_unknown_status_returns_none(self, tmp_path, capsys):
        make_project(tmp_path)
        assert lifecycle.move_task("KIT-1234", "bogus", tmp_path) is None
        assert "Unknown status" in capsys.readouterr().out

    def test_task_not_found_returns_none(self, tmp_path, capsys):
        make_project(tmp_path)
        assert lifecycle.move_task("KIT-9999", "done", tmp_path) is None
        assert "Task not found" in capsys.readouterr().out

    def test_move_returns_typed_outcome(self, tmp_path):
        make_project(tmp_path)
        result = lifecycle.move_task("KIT-1234", "in-progress", tmp_path)
        assert result.task_id == "KIT-1234"
        assert result.file_name == TASK_FILE
        assert result.from_folder == "2-todo"
        assert result.to_folder == "3-in-progress"
        assert result.status == "In Progress"
        assert result.moved is True
        assert result.status_field_updated is True

    def test_status_field_updated_in_moved_file(self, tmp_path):
        make_project(tmp_path)
        lifecycle.move_task("KIT-1234", "done", tmp_path)
        moved = tmp_path / ".kit" / "tasks" / "5-done" / TASK_FILE
        assert "**Status**: Done" in moved.read_text(encoding="utf-8")

    def test_missing_status_field_is_partial_failure(self, tmp_path, capsys):
        # CodeRabbit (PR #108): a move whose Status field cannot be set
        # must be visible as a partial failure, not a clean success.
        make_project(tmp_path)
        task = tmp_path / ".kit" / "tasks" / "2-todo" / TASK_FILE
        task.write_text("# Task with no status header\n", encoding="utf-8")

        result = lifecycle.move_task("KIT-1234", "in-progress", tmp_path)

        assert result  # the file did move
        assert result.status_update_failed is True
        assert result.status_field_updated is False
        out = capsys.readouterr().out
        assert "Status field not updated" in out
        # The summary line must not contradict the warning (BugBot,
        # PR #108 round 2): no ✅ on a partial failure.
        assert "✅ Task" not in out
        assert "⚠️  Task KIT-1234 moved to 3-in-progress" in out

    def test_unwritable_status_is_partial_failure(self, tmp_path, monkeypatch):
        import pathlib

        make_project(tmp_path)
        real_write = pathlib.Path.write_text

        def failing_write(self, *args, **kwargs):
            if self.name == TASK_FILE:
                raise OSError(30, "Read-only file system", str(self))
            return real_write(self, *args, **kwargs)

        monkeypatch.setattr(pathlib.Path, "write_text", failing_write)
        result = lifecycle.move_task("KIT-1234", "in-progress", tmp_path)
        assert result
        assert result.status_update_failed is True


class TestUpdateStatusTriState:
    def test_updated_returns_true(self, tmp_path):
        f = tmp_path / "t.md"
        f.write_text("**Status**: Todo\n", encoding="utf-8")
        assert lifecycle.update_status_in_file(f, "Done") is True

    def test_already_correct_returns_false(self, tmp_path):
        f = tmp_path / "t.md"
        f.write_text("**Status**: Done\n", encoding="utf-8")
        assert lifecycle.update_status_in_file(f, "Done") is False

    def test_absent_field_returns_none(self, tmp_path):
        f = tmp_path / "t.md"
        f.write_text("# no header\n", encoding="utf-8")
        assert lifecycle.update_status_in_file(f, "Done") is None

    def test_missing_file_returns_none(self, tmp_path):
        assert lifecycle.update_status_in_file(tmp_path / "gone.md", "Done") is None


class TestTaskIdBoundaryMatch:
    """Evaluator finding, PR 1 trio (deliberate fix over the legacy
    substring test): a short ID must never select a longer ID's file."""

    def test_short_id_does_not_match_longer_id(self, tmp_path, capsys):
        make_project(tmp_path)  # contains KIT-1234-sample-task.md
        assert lifecycle.move_task("KIT-1", "done", tmp_path) is None
        assert "Task not found" in capsys.readouterr().out
        # KIT-1234's file was not touched.
        assert (tmp_path / ".kit" / "tasks" / "2-todo" / TASK_FILE).exists()

    def test_full_id_still_matches(self, tmp_path):
        make_project(tmp_path)
        found = lifecycle.find_task_file("KIT-1234", tmp_path)
        assert found is not None
        assert found.name == TASK_FILE

    def test_match_is_case_insensitive(self, tmp_path):
        make_project(tmp_path)
        found = lifecycle.find_task_file("kit-1234", tmp_path)
        assert found is not None

    def test_lowercase_suffix_does_not_match(self, tmp_path):
        # Matching runs on the uppercased name, so a lowercase run-on
        # suffix is a boundary violation like any other.
        make_project(tmp_path)
        runon = tmp_path / ".kit" / "tasks" / "2-todo" / "KIT-9876foo.md"
        runon.write_text("**Status**: Todo\n", encoding="utf-8")
        assert lifecycle.find_task_file("KIT-9876", tmp_path) is None

    def test_underscore_is_a_separator_not_a_boundary_violation(self, tmp_path):
        # KIT-1234_sample.md was findable under the legacy substring
        # matcher; '_' is a separator like '-', and blocking it would
        # strand existing files on upgrade (evaluator rounds 4/5
        # disagreed here — round 5's data-compatibility argument wins).
        make_project(tmp_path)
        sep = tmp_path / ".kit" / "tasks" / "2-todo" / "KIT-9876_sample.md"
        sep.write_text("**Status**: Todo\n", encoding="utf-8")
        found = lifecycle.find_task_file("KIT-9876", tmp_path)
        assert found is not None
        assert found.name == "KIT-9876_sample.md"

    def test_bare_id_file_matches(self, tmp_path):
        make_project(tmp_path)
        bare = tmp_path / ".kit" / "tasks" / "2-todo" / "KIT-7777.md"
        bare.write_text("**Status**: Todo\n", encoding="utf-8")
        found = lifecycle.find_task_file("KIT-7777", tmp_path)
        assert found is not None
        assert found.name == "KIT-7777.md"


class TestMissingTargetFolder:
    """Evaluator finding, PR 1 trio: a valid status whose folder is
    absent (lean layouts skip 6-canceled/7-blocked) is created."""

    def test_move_creates_absent_status_folder(self, tmp_path):
        make_project(tmp_path)  # creates only 2-todo/3-in-progress/5-done
        result = lifecycle.move_task("KIT-1234", "blocked", tmp_path)
        assert result
        assert (tmp_path / ".kit" / "tasks" / "7-blocked" / TASK_FILE).exists()


class TestMissingTasksDir:
    """Evaluator findings, PR 1 trio: a repo without .kit/tasks/ (root
    discovery only guarantees .kit/) reports cleanly instead of
    crashing with FileNotFoundError."""

    def test_find_task_file_returns_none(self, tmp_path):
        (tmp_path / ".kit").mkdir()
        assert lifecycle.find_task_file("KIT-1234", tmp_path) is None

    def test_move_task_reports_not_found(self, tmp_path, capsys):
        (tmp_path / ".kit").mkdir()
        assert lifecycle.move_task("KIT-1234", "done", tmp_path) is None
        assert "Task not found" in capsys.readouterr().out

    def test_validate_reports_zero_checked(self, tmp_path, capsys):
        (tmp_path / ".kit").mkdir()
        report = lifecycle.validate_all_tasks(tmp_path)
        assert report.ok
        assert report.checked == 0
        assert "All 0 tasks" in capsys.readouterr().out

    def test_validate_unreadable_tasks_dir_is_a_finding(self, tmp_path, monkeypatch):
        # is_dir() succeeding does not guarantee iterdir() can —
        # CodeRabbit (PR #108 round 3): an unreadable directory is a
        # finding, not a crash.
        import pathlib

        make_project(tmp_path)
        tasks_dir = tmp_path / ".kit" / "tasks"
        real_iterdir = pathlib.Path.iterdir

        def failing_iterdir(self):
            if self == tasks_dir:
                raise PermissionError(13, "Permission denied", str(self))
            return real_iterdir(self)

        monkeypatch.setattr(pathlib.Path, "iterdir", failing_iterdir)
        report = lifecycle.validate_all_tasks(tmp_path)
        assert not report.ok
        assert "Unreadable tasks directory" in report.issues[0].detail


class TestValidateAllTasks:
    def test_all_matching_reports_ok(self, tmp_path, capsys):
        make_project(tmp_path)
        report = lifecycle.validate_all_tasks(tmp_path)
        assert report.ok
        assert report.checked == 1
        assert "matching Status and folder" in capsys.readouterr().out

    def test_mismatch_reported(self, tmp_path, capsys):
        make_project(tmp_path)
        wrong = tmp_path / ".kit" / "tasks" / "5-done" / "KIT-0003-wrong.md"
        wrong.write_text("**Status**: Todo\n", encoding="utf-8")
        report = lifecycle.validate_all_tasks(tmp_path)
        assert not report.ok
        assert len(report.issues) == 1
        assert report.issues[0].file_name == "KIT-0003-wrong.md"
        assert "status mismatches" in capsys.readouterr().out

    def test_non_utf8_task_file_is_a_finding_not_a_crash(self, tmp_path):
        # Evaluator finding, PR 1 trio: an unreadable task file must
        # surface as a validation issue, matching the tolerance the
        # metadata sync already has for corrupted coordination files.
        make_project(tmp_path)
        bad = tmp_path / ".kit" / "tasks" / "2-todo" / "KIT-0005-binary.md"
        bad.write_bytes(b"\xff\xfe broken")
        report = lifecycle.validate_all_tasks(tmp_path)
        assert not report.ok
        assert any("Unreadable file" in i.detail for i in report.issues)

    def test_missing_status_field_reported(self, tmp_path):
        make_project(tmp_path)
        bad = tmp_path / ".kit" / "tasks" / "2-todo" / "KIT-0004-nostatus.md"
        bad.write_text("# No status here\n", encoding="utf-8")
        report = lifecycle.validate_all_tasks(tmp_path)
        assert not report.ok
        assert "No Status field found" in report.issues[0].detail

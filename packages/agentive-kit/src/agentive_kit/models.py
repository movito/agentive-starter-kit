"""Typed models for data crossing module boundaries (KIT-0090 F1).

The arch evaluation's accepted finding: internal contracts should be
readable and testable — explicit dataclasses, not loose dicts. Kept
deliberately small: a model earns its place here only when the value
actually crosses a module boundary or is emitted by the CLI; purely
local intermediates stay local.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class TaskMove:
    """Outcome of a task status move (lifecycle → CLI)."""

    task_id: str
    file_name: str
    from_folder: str
    to_folder: str
    status: str  # Linear-native status label, e.g. "In Progress"
    moved: bool  # False when the task was already in the target folder
    status_field_updated: bool
    # True when the Status field could NOT be set (absent, unreadable,
    # unwritable), regardless of whether a move occurred — the
    # already-in-place repair path sets it too. The CLI reports this
    # partial failure with a nonzero exit (CodeRabbit, PR #108). This
    # is distinct from status_field_updated=False, which also covers
    # "already correct, nothing to do".
    status_update_failed: bool = False


@dataclass(frozen=True)
class StatusIssue:
    """One task file whose Status field disagrees with its folder."""

    file_name: str
    detail: str


@dataclass(frozen=True)
class ValidationReport:
    """Outcome of a full task-status validation (lifecycle → CLI)."""

    checked: int
    # A tuple, so frozen=True actually means immutable — a list field
    # would let callers mutate .issues and flip .ok (CodeRabbit,
    # PR #108).
    issues: tuple[StatusIssue, ...] = field(default_factory=tuple)

    @property
    def ok(self) -> bool:
        return not self.issues


@dataclass(frozen=True)
class MetadataSyncNote:
    """One coordination-metadata file touched (or skipped) by a move."""

    path: Path
    action: str  # "updated" | "skipped" | "warned"
    detail: str = ""

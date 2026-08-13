# Code Review: [Project Name] — [TASK-ID] [Task Title]

## Context

[1-2 sentences: what was implemented and why]

**Task**: [TASK-ID]
**PR**: #[number]
**Bot review status**: [e.g., "BugBot: 2 findings fixed, CodeRabbit: approved after round 2"]

## Changed Files

**CRITICAL: Include FULL file content, not diffs or excerpts.** The evaluator cannot
reason about imports, error handling context, or module-level state from partial code.
Diff-only inputs produce false positives. Always paste the complete file.

### Source: `path/to/file.py`

```python
[Full file content]
```

### Source: `path/to/other_file.py`

```python
[Full file content]
```

[Repeat for each changed source file]

## Test Files

Include the full test file so the evaluator can check edge-case coverage.

### Tests: `tests/test_feature.py`

```python
[Full test file content]
```

## What the Bots Found

Summarize what BugBot and CodeRabbit flagged and how it was addressed.
This helps the evaluator look for similar patterns the bots might have missed.

- **[Bot]**: [Finding summary] → [How it was fixed]
- **[Bot]**: [Finding summary] → [Declined: reason]

## Valid Values and Boundaries

For each config field, enum, or constrained input touched by this PR, list:

- **Field name**: valid values, what should happen for invalid ones
- Example: `session_manager`: valid = `{"tmux", "none"}`. Invalid value → warning + fallback to `"none"`.
- Example: `mode`: valid = `{"notify", "approve", "auto"}`. Invalid → `ValueError` in `_validate_config()`.

This helps the evaluator reason about boundary validation — the class of bug
most often missed by bots.

[Delete this section if the PR touches no constrained fields.]

## Key Questions

1. [Specific concern about a function or pattern]
2. [Any edge case you're unsure about]

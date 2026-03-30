# ADV-0053: Make adversarial-workflow CLI directory configurable

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 2-3 hours
**Created**: 2026-03-30
**Target Completion**: Next adversarial-workflow release
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Related**: ASK-0044 (Builder/Project separation — exposed this issue)
**Related**: KIT-0026 (Cross-kit sync — blocked from evaluating until this is fixed)

## Overview

The `adversarial-workflow` CLI (v0.9.9) hardcodes `.adversarial/` as its working directory
for config, evaluators, scripts, and logs. After ASK-0044 moved all builder infrastructure
into `.kit/`, the canonical location became `.adversarial/`, breaking the CLI silently.

The fix belongs in the `adversarial-workflow` package itself: support a configurable
directory via `--dir` flag, `ADVERSARIAL_DIR` env var, or `adversarial.dir` in
`pyproject.toml`, falling back to `.adversarial/` for backward compatibility.

**Context**: This surfaced during KIT-0026 evaluation — `adversarial evaluate --evaluator
arch-review-fast` couldn't find evaluators because they live in `.adversarial/evaluators/`.

## Requirements

### Functional Requirements

1. CLI resolves working directory via priority chain:
   - `--dir <path>` flag (highest priority)
   - `ADVERSARIAL_DIR` environment variable
   - `tool.adversarial.dir` in `pyproject.toml`
   - `.adversarial/` (default, backward compatible)
2. All CLI commands use the resolved directory: `check`, `evaluate`, `init`, `list-evaluators`, etc.
3. `adversarial check` reports which directory it's using
4. Existing projects with `.adversarial/` at root continue working with zero config changes

### Non-Functional Requirements
- [ ] No breaking changes to existing CLI behavior
- [ ] Works with both absolute and relative paths

## Implementation Notes

This task is scoped to the **adversarial-workflow** repo (movito/adversarial-workflow),
not agentive-starter-kit. When complete:

1. Release new adversarial-workflow version
2. Once configurable dir is supported, `.adversarial/` can move into `.kit/adversarial/` with a config override
3. Remove the integration note in `.kit/context/REVIEW-INSIGHTS.md`

## References

- **adversarial-workflow**: `movito/adversarial-workflow`
- **ASK-0044 post-mortem**: `.kit/context/REVIEW-INSIGHTS.md` (Integration Notes)
- **Current workaround**: None (CLI is non-functional for `.kit/` layout until this is fixed)

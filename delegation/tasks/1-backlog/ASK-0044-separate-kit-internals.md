# ASK-0044: Separate Kit Internals from Downstream-Exportable Content

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 1-2 days
**Created**: 2026-03-25
**GitHub Issue**: #35

## Related Tasks

**Related**: KIT-0024 (#30, cross-project scripts standardization)
**Related**: ASK-0042 (scripts restructure — established core/local/optional layout)

## Overview

Downstream projects syncing from agentive-starter-kit cannot easily distinguish between kit internals (bootstrapping, sync machinery, template scaffolding) and project utilities (ci-check, pattern_lint, create-agent) that every downstream project benefits from. This makes every sync a manual judgment call.

**Context**: Reported in GitHub issue #35. Discovered during adversarial-workflow upstream sync (ADV-0039), where 8/11 scripts were already synced and the remaining 3 were kit internals requiring manual triage.

## Requirements

### Functional Requirements
1. Clear boundary between kit-internal and downstream-exportable content
2. Everything in `scripts/core/` and `scripts/optional/` must be safe for downstream consumption — no ASK-specific references, no bootstrapping logic
3. Kit internals (bootstrap.sh, sync scripts, template scaffolding) should live in a clearly separated location
4. Agent/skill/command definitions should be similarly classified

### Design Decision Needed
- Where should kit internals live? Options: `scripts/kit/`, `kit/`, or a manifest-based approach
- Should this be enforced by the sync workflow (`.core-manifest.json`) or by directory convention?
- How does this interact with the existing `scripts/local/` (project-specific) concept?

## Implementation Plan

### Step 1: Audit current content
- Classify every file in `scripts/`, `.claude/agents/`, `.claude/commands/`, `.claude/skills/` as kit-internal vs downstream-exportable
- Document classification in an ADR

### Step 2: Implement separation
- Move kit internals to designated location
- Update sync workflow to respect the boundary
- Update `.core-manifest.json` if needed

### Step 3: Validate with downstream repos
- Test sync against adversarial-workflow, dispatch-kit, adversarial-evaluator-library

## Acceptance Criteria

### Must Have
- [ ] ADR documenting the classification and boundary
- [ ] Kit internals clearly separated from exportable content
- [ ] Sync workflow respects the boundary
- [ ] No breaking changes for existing downstream repos

## Lessons from Downstream

**adversarial-workflow PR #42** (ADV-0052) restructured to `core/local/optional` and copied 14 scripts from ASK v0.4.0. Key pain points:
- Had to manually triage which scripts to copy (8/11 were already synced, 3 were kit internals)
- "6/7 slash commands were broken" referencing scripts that didn't exist after sync
- Updated 56 files to fix stale path references
- Created `.core-manifest.json` to track synced versions

**adversarial-workflow PR #43** (ADV-0043) synced 11 agent definitions. Had to filter out ASK-specific agents vs reusable ones — same triage problem for agents as for scripts.

**The pattern is clear**: every downstream sync requires manual judgment about what's kit-specific vs reusable. A manifest or directory convention would eliminate this cost.

**Possible approach**: `.core-manifest.json` already tracks scripts. Extend it to cover agents, skills, and commands with an `exportable: true/false` flag. The sync workflow reads the manifest to know what to copy.

## References

- GitHub issue: #35
- Related: #30 (KIT-0024)
- adversarial-workflow PR #42: Scripts restructure (14 scripts copied, 56 files updated)
- adversarial-workflow PR #43: Agent sync (11 agents, manual triage needed)
- Discovered in: ADV-0039 (adversarial-workflow upstream sync)

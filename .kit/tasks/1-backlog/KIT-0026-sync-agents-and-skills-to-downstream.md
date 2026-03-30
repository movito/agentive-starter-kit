# KIT-0026: Sync Agent Definitions and Skills to Downstream Repos

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 2-4 hours
**Created**: 2026-03-29
**Target Completion**: 2026-04-05
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent Task**: ASK-0044 (Separate Kit Internals — builder/project boundary)
**Depends On**: None (sync workflow already exists)
**Related**: KIT-0024 (Tiered manifest & sync upgrade), KIT-0025 (PR-based evaluator runner)

## Overview

The cross-repo sync workflow (`.github/workflows/sync-core-scripts.yml`) currently syncs
`scripts_core`, `commands_core`, `commands_optional`, and `kit_builder` tiers to downstream
repos (dispatch-kit, adversarial-workflow, adversarial-evaluator-library). However, **agent
definitions** (`.claude/agents/`) and **implementation skills** (`.claude/skills/`) are not
included in the manifest and must be manually kept in sync.

This task adds two new tiers to `.core-manifest.json` so that agent and skill updates
propagate automatically to all kit repos.

**Context**: After ASK-0044 established the `.kit/` boundary, the builder layer syncs
cleanly. But agents and skills — which live in `.claude/` (Claude Code resolution
constraint) — are the last major category of shared infrastructure not covered by the sync.

**Related Work**:
- KIT-ADR-0022: Manifest-based sync ownership
- KIT-ADR-0023: Builder-project separation (`.kit/` boundary)
- `.github/workflows/sync-core-scripts.yml` (existing sync workflow)

## Requirements

### Functional Requirements

1. Add `agents_core` tier to `.core-manifest.json` listing shared agent definitions
2. Add `skills_core` tier to `.core-manifest.json` listing shared implementation skills
3. Update `sync-core-scripts.yml` path triggers to include `.claude/agents/**` and `.claude/skills/**`
4. Update `sync-core-scripts.yml` `resolve_paths` helper to handle new tiers
5. Update `sync-core-scripts.yml` `git add` step to include `.claude/agents/` and `.claude/skills/`
6. Downstream repos receive agent and skill updates via the existing PR-based sync flow

### Non-Functional Requirements
- [ ] Sync must be backward-compatible: downstream repos without `.claude/agents/` get the directory created
- [ ] Agent files that are project-specific (e.g., `onboarding.md` which references project name) must be excluded or handled
- [ ] Existing `opted_in` mechanism must work for new tiers (core tiers always sync)

## Tier Design

### Which agents to sync

Not all agents should sync. Some are project-specific (onboarding), some are kit-only
(planner2). Proposed split:

**`agents_core`** (always synced — `*_core` tier):
- `feature-developer.md`
- `feature-developer-v3.md`
- `feature-developer-v5.md`
- `test-runner.md`
- `powertest-runner.md`
- `ci-checker.md`
- `code-reviewer.md`
- `document-reviewer.md`
- `security-reviewer.md`
- `agent-creator.md`

**NOT synced** (project-specific or kit-only):
- `onboarding.md` — references project name, only used in ASK
- `bootstrap.md` — consumer project bootstrapper, ASK-specific
- `planner.md` — lightweight planner, project-specific configuration
- `planner2.md` — heavy planner with Chrome/Serena, kit-only

### Which skills to sync

**`skills_core`** (always synced):
- `pre-implementation/` — pre-implementation checklist
- `bot-triage/` — bot review triage

**NOT synced** (kit-only builder skills in `.kit/skills/`):
- `self-review/` — already in `kit_builder` tier
- `review-handoff/` — already in `kit_builder` tier
- `code-review-evaluator/` — already in `kit_builder` tier

### Manifest changes

```json
{
  "files": {
    "scripts_core": [...],
    "commands_core": [...],
    "commands_optional": [...],
    "agents_core": [
      "feature-developer.md",
      "feature-developer-v3.md",
      "feature-developer-v5.md",
      "test-runner.md",
      "powertest-runner.md",
      "ci-checker.md",
      "code-reviewer.md",
      "document-reviewer.md",
      "security-reviewer.md",
      "agent-creator.md"
    ],
    "skills_core": [
      "pre-implementation/",
      "bot-triage/"
    ],
    "kit_builder": [...]
  },
  "opted_in": ["commands_optional", "kit_builder"]
}
```

### Workflow changes

1. **Path triggers**: Add `.claude/agents/**` and `.claude/skills/**`
2. **`resolve_paths` function**: Add cases:
   ```bash
   agents_core)
     echo "source/.claude/agents/${entry}" "target/.claude/agents/${entry}"
     ;;
   skills_core)
     echo "source/.claude/skills/${entry}" "target/.claude/skills/${entry}"
     ;;
   ```
3. **`git add` step**: Add `.claude/agents/` and `.claude/skills/`
4. **PR body**: Update tier description list

## Implementation Plan

### Step 1: Update manifest (30 min)

1. Add `agents_core` and `skills_core` arrays to `scripts/.core-manifest.json`
2. Verify `should_sync_tier` logic handles new `*_core` tiers (it should — grep `_core$` already matches)

### Step 2: Update sync workflow (30 min)

1. Add path triggers for `.claude/agents/**` and `.claude/skills/**`
2. Add `resolve_paths` cases for `agents_core` and `skills_core`
3. Add `git add .claude/agents/ .claude/skills/` to commit step (with existence guard)
4. Update PR body template to list new tiers

### Step 3: Update test for manifest entries (30 min)

1. Update `test_all_kit_builder_entries_exist` (or equivalent) to also validate `agents_core` and `skills_core` entries exist on disk
2. Add test that `resolve_paths` returns correct paths for new tiers

### Step 4: Dry-run validation (30 min)

1. Run the sync script locally against a checkout of dispatch-kit
2. Verify correct files are copied, no unexpected overwrites
3. Verify downstream manifest is updated correctly

## Acceptance Criteria

### Must Have
- [ ] `agents_core` tier in manifest with 10 agent definitions
- [ ] `skills_core` tier in manifest with 2 skill directories
- [ ] Sync workflow triggers on `.claude/agents/**` and `.claude/skills/**` changes
- [ ] `resolve_paths` correctly maps new tiers to `.claude/agents/` and `.claude/skills/`
- [ ] `git add` step includes new directories
- [ ] Existing tests pass (no regressions)
- [ ] `should_sync_tier` correctly treats `*_core` tiers as always-sync

### Should Have
- [ ] Dry-run against dispatch-kit confirms correct file placement
- [ ] PR body template includes new tier descriptions
- [ ] New manifest entries validated by test

### Nice to Have
- [ ] Documentation note in KIT-ADR-0022 addendum about new tiers

## Risks & Mitigations

### Risk 1: Agent definitions reference project-specific paths
**Likelihood**: Medium
**Impact**: Low
**Mitigation**:
- Excluded project-specific agents (onboarding, bootstrap, planner/planner2) from sync
- Core agents use relative paths and standard conventions
- `reconfigure` script already handles Serena activation name replacement

### Risk 2: Skill directories have nested files that don't copy correctly
**Likelihood**: Low
**Impact**: Medium
**Mitigation**:
- Directory entries (trailing `/`) already handled by `cp -r` in sync workflow
- Same pattern used successfully for `kit_builder` directory entries

### Risk 3: Downstream repos already have diverged agent definitions
**Likelihood**: Medium
**Impact**: Medium
**Mitigation**:
- Sync creates a PR (not direct push) — human reviews before merge
- Warnings emitted for files not previously in manifest
- First sync may need manual conflict resolution

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Update manifest | 30 min | [ ] |
| Update sync workflow | 30 min | [ ] |
| Update tests | 30 min | [ ] |
| Dry-run validation | 30 min | [ ] |
| Code review & fixes | 1 hour | [ ] |
| **Total** | **3-4 hours** | [ ] |

## References

- **KIT-ADR-0022**: `.kit/adr/KIT-ADR-0022-manifest-based-sync-ownership.md`
- **KIT-ADR-0023**: `.kit/adr/KIT-ADR-0023-builder-project-separation.md`
- **Sync workflow**: `.github/workflows/sync-core-scripts.yml`
- **Current manifest**: `scripts/.core-manifest.json`
- **Commit Protocol**: `.kit/context/workflows/COMMIT-PROTOCOL.md`

## Notes

- This is Phase 2 of the cross-kit sync strategy discussed after ASK-0044 completion
- Long-term (Phase 3): consider publishing shared infrastructure as an installable package
  for non-kit consumer projects, but that's out of scope here
- The `reconfigure` script (`./scripts/core/project reconfigure`) already handles
  post-sync name replacement in agent files — no changes needed there
- Planner/planner2 agents are intentionally excluded: they contain project-specific
  coordination state (task prefixes, evaluation workflows, Chrome/Serena config)

---

**Template Version**: 1.0.0
**Created**: 2026-03-29

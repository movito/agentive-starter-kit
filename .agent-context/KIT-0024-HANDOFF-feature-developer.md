# KIT-0024: Core Scripts Standardization — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-03-26
**From**: Planner (planner2)
**To**: feature-developer-v5
**Task**: `delegation/tasks/2-todo/KIT-0024-core-scripts-standardization.md`
**Status**: Ready for implementation
**Evaluation**: Evaluated by arch-review-fast (REVISION_SUGGESTED, addressed)

---

## Task Summary

Upgrade the cross-repo sync infrastructure in agentive-starter-kit to support
the tiered manifest format defined in KIT-ADR-0022. This enables downstream repos
to have local slash commands that sync never touches, while core scripts and
commands are kept in sync automatically.

**Scope**: ASK-side only (this repo). Downstream adoption is separate work.

## Current Situation

Phase 1 (ASK-0042) established `scripts/core/` with 14 files and a flat manifest.
The sync Action (`sync-core-scripts.yml`) currently:
- Only syncs `scripts/core/` (not commands)
- Does `rm -rf scripts/core` + full copy (no manifest awareness)
- Overwrites downstream manifest entirely (loses any `opted_in` preferences)

This needs to become manifest-aware per KIT-ADR-0022.

## Your Mission

### Phase 1: Upgrade manifest format (in this repo)

1. **Upgrade `.core-manifest.json`** to tiered format:

```json
{
  "core_version": "1.3.0",
  "source_repo": "movito/agentive-starter-kit",
  "synced_at": "2026-03-26T00:00:00Z",
  "files": {
    "scripts_core": [
      "core/__init__.py",
      "core/check-bots.sh",
      "core/check-sync.sh",
      "core/ci-check.sh",
      "core/gh-review-helper.sh",
      "core/logging_config.py",
      "core/pattern_lint.py",
      "core/preflight-check.sh",
      "core/project",
      "core/validate_task_status.py",
      "core/verify-ci.sh",
      "core/verify-setup.sh",
      "core/wait-for-bots.sh",
      "core/VERSION"
    ],
    "commands_core": [
      "check-ci.md",
      "check-bots.md",
      "wait-for-bots.md",
      "start-task.md",
      "commit-push-pr.md",
      "preflight.md"
    ],
    "commands_optional": [
      "babysit-pr.md",
      "retro.md",
      "triage-threads.md",
      "status.md",
      "check-spec.md"
    ]
  },
  "opted_in": ["commands_optional"]
}
```

2. **Bump `scripts/core/VERSION`** to `1.3.0`

### Phase 2: Update sync Action

Rewrite `.github/workflows/sync-core-scripts.yml` to:

1. **Trigger on both** `scripts/core/**` AND `.claude/commands/**` changes
2. **Read upstream manifest** for the list of files to sync
3. **Read downstream manifest** (if exists) for `opted_in` preferences
4. **Sync only owned files**:
   - `scripts_core` files: always sync (copy from upstream)
   - `commands_core` files: always sync (copy to `.claude/commands/`)
   - `commands_optional` files: only sync if tier is in downstream `opted_in`
5. **Preserve downstream `opted_in`**: merge upstream `files` sections with downstream `opted_in` array
6. **Warn on collision**: if a file being synced already exists but wasn't previously in the manifest, log a warning in the PR body
7. **Update `synced_at`** timestamp in downstream manifest

**Key constraint**: The sync step must NOT `rm -rf` anymore. It must iterate over manifest entries and copy file-by-file, so local/unowned files are untouched.

### Phase 3: Classify commands

Verify that commands are correctly classified. A command is `commands_core` if it
references `scripts/core/` in its body. Check each:

```bash
# These should reference scripts/core/ → commands_core
grep -l 'scripts/core' .claude/commands/*.md

# These should NOT reference scripts/core/ → commands_optional
# babysit-pr.md, retro.md, triage-threads.md, status.md, check-spec.md
```

If classification is wrong, update the manifest accordingly.

### Phase 4: Tests

Write a test for the manifest format validation:
- `tests/test_core_manifest.py` — validates manifest structure, all listed files exist,
  no duplicate entries, `opted_in` only references valid tier names

## Acceptance Criteria (Must Have)

- [ ] **Manifest upgraded**: `.core-manifest.json` has tiered format per KIT-ADR-0022
- [ ] **VERSION bumped**: `scripts/core/VERSION` reads `1.3.0`
- [ ] **Sync Action updated**: handles tiered manifest, preserves `opted_in`
- [ ] **No rm -rf**: sync copies file-by-file from manifest entries
- [ ] **Commands classified**: core vs optional split verified by grep
- [ ] **Manifest test**: `tests/test_core_manifest.py` passes
- [ ] **Existing CI passes**: `./scripts/core/ci-check.sh` green
- [ ] **ADR referenced**: KIT-ADR-0022 linked in PR description

## Success Metrics

**Quantitative**:
- Manifest lists all 14 scripts + 6 core commands + 5 optional commands
- All listed files exist on disk (validated by test)
- CI passes

**Qualitative**:
- Sync Action is readable and well-commented
- Manifest format matches KIT-ADR-0022 spec exactly
- A downstream repo with local commands would not be affected by sync

## Critical Implementation Details

### 1. Manifest merge logic (sync Action)

```bash
# Pseudocode for the sync step:
# 1. Read upstream manifest (from source checkout)
# 2. Read downstream manifest (from target checkout), if exists
# 3. downstream_opted_in = downstream.opted_in || []
# 4. For each tier in upstream.files:
#    - If tier ends with "_core" → always sync those files
#    - If tier is in downstream_opted_in → sync those files
#    - Otherwise → skip
# 5. Write new manifest: upstream.files + downstream_opted_in + new synced_at
```

### 2. Trigger paths

```yaml
on:
  push:
    paths:
      - 'scripts/core/**'
      - '.claude/commands/**'
      - 'scripts/.core-manifest.json'
    branches: [main]
```

### 3. File copy targets

| Manifest tier | Source path (ASK) | Target path (downstream) |
|---------------|-------------------|--------------------------|
| `scripts_core` | `scripts/{entry}` | `scripts/{entry}` |
| `commands_core` | `.claude/commands/{entry}` | `.claude/commands/{entry}` |
| `commands_optional` | `.claude/commands/{entry}` | `.claude/commands/{entry}` |

## Resources

- **KIT-ADR-0022**: `docs/decisions/starter-kit-adr/KIT-ADR-0022-manifest-based-sync-ownership.md`
- **Current manifest**: `scripts/.core-manifest.json`
- **Current sync Action**: `.github/workflows/sync-core-scripts.yml`
- **Task spec**: `delegation/tasks/2-todo/KIT-0024-core-scripts-standardization.md`
- **Upgrade guide**: `docs/UPGRADE-0.4.0.md` (for context on Phase 1)

## Time Estimate

3-4 hours total:
- Phase 1 (Manifest upgrade): 30 min
- Phase 2 (Sync Action rewrite): 1.5-2 hours
- Phase 3 (Command classification): 15 min
- Phase 4 (Tests): 45 min - 1 hour

## Starting Point

1. Read KIT-ADR-0022 for the full design rationale
2. Read current `.core-manifest.json` and `sync-core-scripts.yml`
3. Upgrade manifest first (quick win, testable immediately)
4. Then rewrite the sync Action

## Success Looks Like

- `scripts/.core-manifest.json` has tiered format with all files correctly classified
- `sync-core-scripts.yml` iterates manifest entries instead of blanket rm+copy
- A downstream repo with a local `.claude/commands/my-thing.md` would keep that file
  untouched after sync
- `pytest tests/test_core_manifest.py -v` passes
- CI green

---

**Task File**: `delegation/tasks/2-todo/KIT-0024-core-scripts-standardization.md`
**Evaluation Log**: `.adversarial/logs/KIT-0024-core-scripts-standardization--arch-review-fast.md`
**ADR**: `docs/decisions/starter-kit-adr/KIT-ADR-0022-manifest-based-sync-ownership.md`
**Handoff Date**: 2026-03-26
**Coordinator**: Planner (planner2)

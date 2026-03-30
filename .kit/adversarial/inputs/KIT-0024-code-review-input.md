# Code Review: agentive-starter-kit — KIT-0024 Tiered Manifest & Sync Upgrade

## Context

Upgraded the cross-repo sync infrastructure from flat-array manifest to tiered
manifest ownership per KIT-ADR-0022. Core scripts always sync; optional commands
sync only if downstream repos opt in via the `opted_in` array.

**Task**: KIT-0024
**PR**: #39
**Bot review status**: CodeRabbit APPROVED, BugBot CURRENT (0 unresolved threads after 6 cycles)

## Changed Files

### `.github/workflows/sync-core-scripts.yml` (primary deliverable)

Rewritten from `rm -rf && cp -r` to manifest-driven file-by-file sync:

- Trigger paths expanded to include `.claude/commands/**` and manifest file
- `should_sync_tier()`: core tiers always sync, optional tiers check `opted_in`
- `resolve_paths()`: maps tier names to source/target paths
- File-by-file iteration with collision warnings for unmanifested overwrites
- Downstream `opted_in` preserved via `jq --argjson`
- Safe `jq --arg` interpolation for entry names
- Conditional `git add .claude/commands/` (only if dir exists)
- Empty WARNINGS guard (no spurious PR section)
- Old flat-array manifest backward compatibility in collision detection
- PR body documents tier structure and opt-in instructions

### `scripts/.core-manifest.json` (upgraded format)

```json
{
  "core_version": "1.3.0",
  "source_repo": "movito/agentive-starter-kit",
  "synced_at": "2026-03-26T00:00:00Z",
  "files": {
    "scripts_core": [14 entries],
    "commands_core": [6 entries],
    "commands_optional": [5 entries]
  },
  "opted_in": ["commands_optional"]
}
```

### `scripts/core/VERSION`

Bumped from `1.2.0` to `1.3.0`.

### `tests/test_core_manifest.py` (new, 16 tests)

- `TestManifestStructure` (7 tests): required keys, semver, source_repo, ISO timestamp, known tiers, valid opted_in, no core tiers in opted_in
- `TestManifestFileExistence` (3 tests): all files in each tier exist on disk
- `TestManifestConsistency` (6 tests): no dupes within/across tiers, correct counts

### `.kit/adr/KIT-ADR-0022-manifest-based-sync-ownership.md`

ADR documenting the tiered manifest design decision.

### `.agent-context/agent-handoffs.json`

Fixed stale `details_link` path.

## Review Focus Areas

1. **Shell safety in GitHub Actions**: jq interpolation, quoting, `${{ }}` expression handling
2. **Backward compatibility**: old flat-array manifest handling in collision detection
3. **Tier logic correctness**: core always syncs, optional only when opted in
4. **Test coverage**: manifest structure, file existence, consistency checks
5. **Manifest format**: proper JSON structure with all required fields

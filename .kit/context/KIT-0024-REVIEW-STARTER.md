# KIT-0024 Review Starter

**PR**: https://github.com/movito/agentive-starter-kit/pull/39
**Branch**: `feature/KIT-0024-tiered-manifest-sync`
**Status**: Ready for human review

## What Changed

Upgraded cross-repo sync infrastructure from flat-array manifest to tiered
ownership per KIT-ADR-0022.

### Key Files

| File | Change |
|------|--------|
| `scripts/.core-manifest.json` | Flat array → tiered format with `scripts_core`, `commands_core`, `commands_optional` |
| `.github/workflows/sync-core-scripts.yml` | Rewritten: manifest-driven file-by-file sync with tier logic |
| `scripts/core/VERSION` | `1.2.0` → `1.3.0` |
| `tests/test_core_manifest.py` | New: 16 tests validating manifest structure, file existence, consistency |
| `.kit/decisions/KIT-ADR-0022-manifest-based-sync-ownership.md` | ADR for tiered manifest design |

## Review Focus

1. **Tier logic in workflow**: `should_sync_tier()` — core always syncs, optional checks `opted_in`
2. **Shell safety**: All jq interpolation uses `--arg`, WARNINGS uses `env:` block
3. **Backward compat**: Old flat-array manifests handled via `jq` type check
4. **Test coverage**: 16 tests covering structure, existence, consistency, edge cases

## Bot Review Status

- CodeRabbit: **APPROVED** (6 cycles, 14 threads, all resolved)
- BugBot: **CURRENT** (no findings)
- CI: **Passing** (214 tests)

## Quick Verification

```bash
# Run manifest tests
pytest tests/test_core_manifest.py -v

# Check manifest structure
cat scripts/.core-manifest.json | jq .

# Review workflow changes
git diff main -- .github/workflows/sync-core-scripts.yml
```

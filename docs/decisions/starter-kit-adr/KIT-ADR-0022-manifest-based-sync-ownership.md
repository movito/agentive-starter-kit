# KIT-ADR-0022: Manifest-Based Sync Ownership for Cross-Repo Artifacts

**Status**: Accepted
**Date**: 2026-03-26
**Author**: Planner Agent
**Supersedes**: None
**Related**: KIT-0024 (Core Scripts Standardization), KIT-ADR-0012 (Task Status Linear Alignment)

## Context

KIT-0024 establishes agentive-starter-kit as the canonical source for shared scripts
and slash commands across four repos. Phase 1 (ASK-0042) delivered `scripts/core/`
with a `.core-manifest.json` that tracks which files belong to the synced core bundle.

Phase 2 extends sync to `.claude/commands/` and `.claude/skills/`. This creates a
new problem: **downstream repos need to create their own local slash commands without
the sync mechanism overwriting or conflicting with them.** Additionally, good local
commands should be promotable upstream without creating merge conflicts when synced
back down.

### Requirements

1. Downstream repos can create local commands freely — sync never touches them
2. Core commands are always overwritten by sync to prevent drift
3. Workflow-only commands (e.g., `/babysit-pr`, `/retro`) are optional — repos opt in
4. Promoting a local command to core or optional tier is conflict-free
5. No changes to Claude Code's slash command resolution (reads `.claude/commands/` flat)

### Alternatives Considered

**Subdirectory separation** (`commands/core/`, `commands/local/`):
Rejected. Claude Code reads commands from `.claude/commands/` as a flat directory.
Subdirectories would change the `/command` naming UX (e.g., `/core/check-ci` instead
of `/check-ci`) and subdirectory support isn't guaranteed across Claude Code versions.

**Filename prefix convention** (`core-check-ci.md`, `local-my-command.md`):
Rejected. Pollutes the command namespace with infrastructure prefixes. Users would
type `/core-check-ci` instead of `/check-ci`.

**Separate manifest per artifact type** (one for scripts, one for commands):
Rejected. Adds manifest sprawl. A single manifest with categorized sections is simpler
to maintain and reason about.

## Decision

**Extend `.core-manifest.json` with tiered ownership categories.** The sync Action
only writes files listed in the manifest. Any file not in the manifest is local and
never touched.

### Manifest Structure

```json
{
  "core_version": "1.3.0",
  "source_repo": "movito/agentive-starter-kit",
  "synced_at": "2026-03-26T00:00:00Z",
  "files": {
    "scripts_core": [
      "core/project",
      "core/ci-check.sh",
      "core/verify-ci.sh"
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

### Tier Definitions

| Tier | Sync Behavior | Contents |
|------|---------------|----------|
| `scripts_core` | Always synced | Core scripts in `scripts/core/` |
| `commands_core` | Always synced | Commands that depend on core scripts |
| `commands_optional` | Synced only if tier is in `opted_in` | Workflow commands independent of core scripts |
| *(not in manifest)* | Never touched | Local project-specific commands |

### Sync Action Rules

1. **Write only owned files**: For each tier in the manifest, if the tier is
   `*_core` or is listed in `opted_in`, overwrite those files from upstream
2. **Never delete unowned files**: Files not in any manifest tier are local
3. **Manifest itself is synced**: The sync Action updates `files` sections from
   upstream but preserves the downstream `opted_in` array
4. **Checksum verification**: The sync Action can optionally include SHA-256 hashes
   per file to detect local modifications to owned files (warn, don't block)

### Promotion Flow

When a downstream repo creates a useful command that should be shared:

```
1. Downstream creates .claude/commands/my-command.md  (local, not in manifest)
2. Command proves useful in practice
3. PR to agentive-starter-kit adds my-command.md to commands_core or commands_optional
4. ASK merges, bumps core_version
5. Next sync pushes my-command.md downstream — manifest now owns it
6. No conflict: content is identical (or ASK version is canonical)
```

### Opt-In Flow

When a downstream repo wants optional commands:

```
1. Downstream edits .core-manifest.json
2. Adds "commands_optional" to opted_in array
3. Runs sync (or waits for next sync PR)
4. Optional commands appear in .claude/commands/
```

## Consequences

### Positive

- **Zero-conflict local commands**: Downstream repos freely create commands without
  fear of sync overwriting them
- **Clean promotion path**: Local-to-core promotion is a single PR with no migration
- **Opt-in flexibility**: Repos choose their level of tooling consistency
- **Single manifest**: One file to understand ownership across all artifact types
- **No namespace pollution**: Commands keep clean names (`/check-ci`, not `/core/check-ci`)

### Negative

- **Manifest maintenance**: Adding a new synced command requires updating the manifest
  in ASK — easy to forget
- **Name collisions possible**: A downstream local command could have the same name as
  a future upstream command. On promotion, the sync would overwrite the local version.
  Mitigation: sync Action warns if overwriting a file that wasn't previously in the
  manifest.

### Neutral

- Existing `scripts_core` files in the manifest migrate to the new categorized format
  (one-time update in the sync Action)
- The `opted_in` mechanism could later extend to skills (`skills_optional`) using the
  same pattern

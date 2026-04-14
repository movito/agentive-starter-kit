# ADR-0008: Tiered Manifest for Cross-Repo Sync

**Status**: Accepted
**Date**: 2026-03-26 (promoted from KIT-ADR-0022, 2026-04-13)
**Author**: Planner Agent
**Related**: KIT-ADR-0022 (original), KIT-0024 (Core Scripts Standardization)

## Context

Agentive-starter-kit is the canonical source for shared scripts, slash commands, and
builder infrastructure across multiple downstream repos. A `.core-manifest.json` file
in each repo tracks which files are owned by the sync mechanism.

The original manifest (v1.x) was flat — a single `files` array listing scripts only:

```json
{
  "core_version": "1.2.0",
  "files": [
    "core/project",
    "core/ci-check.sh",
    "core/verify-ci.sh"
  ]
}
```

This worked for scripts but couldn't handle commands, skills, or builder infrastructure
because:

1. **No ownership tiers** — all files were synced unconditionally, but some commands
   (e.g., `/babysit-pr`, `/retro`) are workflow-specific and not every repo wants them
2. **No opt-in mechanism** — downstream repos couldn't choose which categories to receive
3. **Commands weren't synced at all** — only scripts were tracked, so commands drifted
   between repos immediately after initial setup

## Decision

Replace the flat `files` array with **tiered categories**. Each tier has defined sync
behavior. Downstream repos opt into optional tiers via an `opted_in` array.

### Manifest Structure (v2.0.0)

```json
{
  "core_version": "2.0.0",
  "source_repo": "movito/agentive-starter-kit",
  "synced_at": "2026-03-29T00:00:00Z",
  "files": {
    "scripts_core": [
      "core/project",
      "core/ci-check.sh",
      "core/verify-ci.sh"
    ],
    "commands_core": [
      "check-ci.md",
      "check-bots.md",
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
    ],
    "kit_builder": [
      ".kit/templates/",
      ".kit/skills/",
      ".kit/launchers/",
      ".kit/adr/",
      ".kit/docs/"
    ]
  },
  "opted_in": ["commands_optional", "kit_builder"]
}
```

### Tier Definitions

| Tier | Sync Behavior | Contents |
|------|---------------|----------|
| `scripts_core` | Always synced | Core scripts in `scripts/core/` |
| `commands_core` | Always synced | Commands that depend on core scripts |
| `commands_optional` | Synced only if in `opted_in` | Workflow commands (babysit-pr, retro, etc.) |
| `kit_builder` | Synced only if in `opted_in` | Builder layer: templates, skills, launchers, ADRs |
| *(not in manifest)* | Never touched | Local project-specific files |

### Key Rules

1. **`*_core` tiers are always synced** — upstream overwrites downstream copies
2. **`*_optional` / `kit_builder` tiers require opt-in** — listed in `opted_in` array
3. **Files not in any tier are local** — sync never touches them
4. **The manifest itself is synced** — `files` sections update from upstream, but
   `opted_in` is preserved (downstream controls what they receive)

### How Downstream Repos Opt In

Edit `.core-manifest.json` and add the tier name to `opted_in`:

```json
{
  "opted_in": ["commands_optional"]
}
```

Next sync will deliver those files.

### Upgrading from v1.x to v2.0.0

See `docs/MANIFEST-UPGRADE-GUIDE.md` for the step-by-step migration procedure.

## Consequences

### Positive

- **Zero-conflict local commands**: Downstream repos create commands freely — sync
  never overwrites files it doesn't own
- **Selective adoption**: Repos choose their level of tooling consistency
- **Single manifest**: One file to understand ownership across all artifact types
- **Clean namespace**: Commands keep user-friendly names (`/check-ci`, not `/core/check-ci`)

### Negative

- **Manifest maintenance**: Adding a new synced artifact requires updating the manifest
  in the starter kit — easy to forget
- **Name collisions**: A local command could match a future upstream command. On
  promotion, sync would overwrite. Mitigation: sync warns on first-time overwrites.

### Alternatives Rejected

- **Subdirectory separation** (`commands/core/`, `commands/local/`): Claude Code reads
  `.claude/commands/` flat — subdirectories would change the `/command` namespace
- **Filename prefixes** (`core-check-ci.md`): Pollutes command names
- **Separate manifests per type**: Adds sprawl without benefit

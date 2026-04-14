# Manifest Upgrade Guide: v1.x to v2.0.0

**For**: Downstream repos upgrading from flat manifest to tiered manifest
**Source**: agentive-starter-kit (ADR-0008)
**Created**: 2026-04-13

---

## What Changed

The `.core-manifest.json` format changed from a flat file list to tiered categories
with opt-in support.

**Before (v1.x)** — flat array, scripts only:

```json
{
  "core_version": "1.2.0",
  "source": "agentive-starter-kit",
  "source_repo": "movito/agentive-starter-kit",
  "synced_at": "2026-03-08T00:00:00Z",
  "files": [
    "core/__init__.py",
    "core/ci-check.sh",
    "core/project",
    "core/verify-ci.sh"
  ]
}
```

**After (v2.0.0)** — tiered categories with opt-in:

```json
{
  "core_version": "2.0.0",
  "source_repo": "movito/agentive-starter-kit",
  "synced_at": "2026-04-13T00:00:00Z",
  "files": {
    "scripts_core": [ ... ],
    "commands_core": [ ... ],
    "commands_optional": [ ... ],
    "kit_builder": [ ... ]
  },
  "opted_in": ["commands_optional"]
}
```

## Why Upgrade

On v1.x:
- Slash commands are **not synced** — they drift immediately after initial setup
- Missing commands like `/babysit-pr` must be copied manually
- New commands added upstream never arrive downstream
- Builder infrastructure (templates, workflows, skills) is not tracked

On v2.0.0:
- Commands sync automatically alongside scripts
- Optional tiers let you choose what you want
- New upstream commands arrive on next sync (if you've opted in)

## Prerequisites

- Your repo already has `scripts/core/` with a `.core-manifest.json` at v1.x
- You have the upstream starter kit available (or the sync GitHub Action configured)

## Step-by-Step Upgrade

### Step 1: Check your current state

```bash
# What version are you on?
cat scripts/.core-manifest.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('core_version'))"

# What commands do you have?
ls .claude/commands/

# What commands does upstream have?
# (check agentive-starter-kit or the manifest below)
```

### Step 2: Replace the manifest

Replace `scripts/.core-manifest.json` with the tiered format. Use the current
upstream manifest as your starting point, then set `opted_in` based on what you want.

**Minimal upgrade** (scripts + core commands only):

```json
{
  "core_version": "2.0.0",
  "source_repo": "movito/agentive-starter-kit",
  "synced_at": "2026-04-13T00:00:00Z",
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
    ],
    "kit_builder": [
      ".kit/templates/",
      ".kit/skills/",
      ".kit/launchers/",
      ".kit/adr/",
      ".kit/docs/",
      ".adversarial/config.yml.template",
      ".adversarial/scripts/",
      ".adversarial/docs/",
      ".adversarial/templates/",
      ".kit/context/workflows/",
      ".kit/context/templates/",
      ".kit/context/patterns.yml",
      ".kit/context/AGENT-SYSTEM-GUIDE.md",
      ".kit/tasks/9-reference/"
    ]
  },
  "opted_in": ["commands_optional"]
}
```

**Full upgrade** (everything including builder layer):

```json
{
  "opted_in": ["commands_optional", "kit_builder"]
}
```

### Step 3: Decide what to opt into

| Tier | What you get | Who needs it |
|------|-------------|--------------|
| `scripts_core` | Core scripts (always synced) | Everyone |
| `commands_core` | `/check-ci`, `/check-bots`, `/start-task`, `/commit-push-pr`, `/preflight`, `/wait-for-bots` | Everyone |
| `commands_optional` | `/babysit-pr`, `/retro`, `/triage-threads`, `/status`, `/check-spec` | Repos with PR review workflows |
| `kit_builder` | Templates, skills, launchers, workflows, patterns | Repos using the full builder layer |

Add the tier names you want to the `opted_in` array. Core tiers (`scripts_core`,
`commands_core`) are always synced regardless of `opted_in`.

### Step 4: Copy missing commands

If your repo is missing commands that should be there, copy them from upstream:

```bash
# From the agentive-starter-kit checkout:
cp .claude/commands/babysit-pr.md  /path/to/downstream/.claude/commands/
cp .claude/commands/retro.md       /path/to/downstream/.claude/commands/
cp .claude/commands/triage-threads.md /path/to/downstream/.claude/commands/
# etc.
```

Or wait for the next sync run — once the manifest is upgraded, sync will deliver them.

### Step 5: Update scripts (if needed)

If your `scripts/core/` files are older than upstream, sync will update them. You can
also manually copy:

```bash
# Check upstream VERSION
cat /path/to/agentive-starter-kit/scripts/core/VERSION

# Compare with yours
cat scripts/core/VERSION
```

### Step 6: Remove the `source` field (optional cleanup)

v1.x had both `source` and `source_repo`. v2.0.0 only uses `source_repo`. The
`source` field is harmless but redundant — remove it for cleanliness.

### Step 7: Commit

```bash
git add scripts/.core-manifest.json .claude/commands/
git commit -m "chore: Upgrade core manifest to v2.0.0 tiered format"
```

## Verifying the Upgrade

After upgrading, check that:

```bash
# Manifest parses correctly
python3 -c "
import json
with open('scripts/.core-manifest.json') as f:
    m = json.load(f)
assert isinstance(m['files'], dict), 'files should be a dict (tiered), not a list (flat)'
assert 'scripts_core' in m['files'], 'missing scripts_core tier'
assert 'commands_core' in m['files'], 'missing commands_core tier'
print(f'v{m[\"core_version\"]} — {sum(len(v) for v in m[\"files\"].values())} files across {len(m[\"files\"])} tiers')
print(f'Opted in: {m.get(\"opted_in\", [])}')
"

# Commands exist
ls .claude/commands/check-ci.md .claude/commands/preflight.md

# Optional commands exist (if opted in)
ls .claude/commands/babysit-pr.md .claude/commands/triage-threads.md
```

## Troubleshooting

**Q: I upgraded the manifest but sync didn't deliver new commands.**
A: The sync GitHub Action needs to understand the tiered format. If you're using the
`sync-core-scripts` Action from agentive-starter-kit, make sure it's on a version
that supports tiered manifests (v2.0.0+).

**Q: A local command I created got overwritten by sync.**
A: Your command's filename matches one in a synced tier. Either rename your local
command or remove it from the tier's file list in the manifest.

**Q: I don't want kit_builder stuff — just scripts and commands.**
A: Only add the tiers you want to `opted_in`. Omit `kit_builder` and you'll only get
scripts + commands.

## Reference

- **ADR-0008**: `docs/adr/ADR-0008-tiered-manifest-sync.md` — architectural decision
- **KIT-ADR-0022**: `.kit/adr/KIT-ADR-0022-manifest-based-sync-ownership.md` — original internal ADR
- **Migration playbook**: `.kit/docs/KIT-MIGRATION-PLAYBOOK.md` — full `.kit/` layout migration (broader scope)

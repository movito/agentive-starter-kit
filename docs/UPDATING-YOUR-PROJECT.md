# Updating Your Project

**Purpose**: How to pull starter-kit improvements into a created project
**Audience**: Operators of projects stamped out from the kit
**Related**: `docs/MANIFEST-UPGRADE-GUIDE.md` (scripts/manifest surface),
`docs/PLUGIN-UPGRADE-GUIDE.md` (plugin surface)

---

The kit improves after your project is created. There are three update
surfaces, each with its own mechanism — use the one that matches what
you want to update.

## 1. Kit-managed files: `project sync` (the supported path)

Core scripts, slash commands, and any tiers you opted into are tracked
by `scripts/.core-manifest.json` and updated by the pull-based sync
engine:

```bash
./scripts/core/project sync --dry-run   # what would change (read-only)
./scripts/core/project sync             # pull everything you're entitled to
```

By default this applies to a `chore/core-sync-<version>` branch and
prints a diffstat — nothing is pushed or merged; you review and merge
on your own schedule. Partial pulls, version pinning, and the
`partial_sync` marker are documented in
`docs/MANIFEST-UPGRADE-GUIDE.md` → "Pull-based sync".

## 2. The agentive-workflow plugin: the upgrader agent

Agents, skills, and commands distributed via the plugin channel are
upgraded by the `upgrader` agent, which executes
`docs/PLUGIN-UPGRADE-GUIDE.md` step-for-step (it also refreshes agent
model pins on a model rollout). Invoke it in your project when a new
plugin version ships.

## 3. Everything else: whole-repo upstream merge (manual)

For files no sync tier covers, you can merge from the kit repo
directly. This is the coarsest tool — created projects start from a
clean export with no shared git history, so expect to review carefully:

```bash
# Add the starter kit as upstream (one time)
git remote add upstream https://github.com/movito/agentive-starter-kit.git

# Pull updates (created projects share no git history with the kit,
# so the merge must allow unrelated histories)
git fetch upstream
git merge --allow-unrelated-histories upstream/main

# Update agent files with your project name
./scripts/core/project reconfigure
```

The `reconfigure` command updates Serena activation calls in agent
files after pulling upstream changes: it replaces any
`activate_project("...")` value (the placeholder `"your-project"` or
upstream's `"agentive-starter-kit"`) with your project name from
`.serena/project.yml`.

**How merging works:**

- Files **only you changed** → your changes preserved
- Files **only upstream changed** → you get the updates
- Files **both changed** → merge conflict (you decide what to keep)

**Best practices for easy updates:**

- Prefer `project sync` for anything the manifest covers — it never
  conflicts with your local work
- Keep customizations in **new files** when possible (new agents, new
  docs)
- Avoid heavily editing core starter kit files; when you do, the merge
  is usually straightforward

**Your stuff stays safe:**

- Custom agents you created
- Your `.env` configuration (gitignored)
- Project-specific docs and tasks

---

**Source**: moved from README.md and reconciled with `project sync`
(KIT-0073 doc curation)

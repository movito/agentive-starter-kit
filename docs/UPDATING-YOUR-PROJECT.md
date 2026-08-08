# Updating Your Project

**Purpose**: How to pull starter-kit improvements into a created project
**Audience**: Operators of projects stamped out from the kit
**Related**: `docs/PLUGIN-UPGRADE-GUIDE.md` (plugin surface),
`docs/MANIFEST-UPGRADE-GUIDE.md` (legacy scripts/manifest surface)

---

Which update story applies depends on when your project was created.
Check: does your repo have a `scripts/core/` directory? **No** → it is
a packaged project (created after KIT-ADR-0028 phase 2). **Yes** → it
is a copied-scripts project (see the legacy section below).

## Packaged projects: two upgrade commands

Everything a packaged project runs is **installed, not copied** — so
updating never touches your repo:

```bash
# 1. The lifecycle CLI (task moves, doctor, preflight, evaluators)
uv tool upgrade agentive-kit

# 2. Agents, skills, and slash commands (the agentive-workflow plugin)
claude plugin update agentive-workflow@agentive-skills
```

For plugin upgrades with release-note review and model-pin refreshes,
invoke the `upgrader` agent — it executes
`docs/PLUGIN-UPGRADE-GUIDE.md` step for step.

The **evaluator library** stays pinned per-repo in
`.adversarial/config.yml` (`evaluator_library_version`). To move to a
newer library release, bump the pin and re-run:

```bash
agentive install-evaluators
```

Everything else in the repo — task specs, `CLAUDE.md`, workflow
reference docs, ADRs — is **content you own**, under your git history.
The kit never rewrites it. Verify any upgrade with `agentive doctor`.

### Renaming or retargeting a split pair (the sanctioned procedure)

There is no `--retarget` mechanism (decided KIT-0093, from KIT-0081
F6): **hand-editing the two records is the supported procedure.** To
rename a project or move its code repo:

1. Rename/move the folders (keep the pair siblings:
   `<parent>/<name>` + `<parent>/<name>-planning`).
2. In the planning repo's `CLAUDE.md`, update BOTH records to the new
   values — the `## Target Repository` section (`Path` + `GitHub`)
   and the `target_path`/`target_github` lines inside the
   `KIT-LOCAL: kit-install` region. They must agree.
3. Update `PROJECT_NAME` in the planning repo's `.env`.
4. If the GitHub repo was renamed, fix `origin` in the code repo
   (`git remote set-url`).
5. Run `agentive doctor` in the planning repo — it reads the record
   and flags a pointer that no longer resolves.

## Copied-scripts projects (created before phase 2)

Projects whose scaffold carries `scripts/core/` copies still use the
copy-era mechanisms. A guided migration to the packaged layout
(ADR-0028 phase 3, via the `upgrader` agent) is coming; until then:

### 1. Kit-managed files: `project sync`

Core scripts, slash commands, and opted-in tiers are tracked by
`scripts/.core-manifest.json`:

```bash
./scripts/core/project sync --dry-run   # what would change (read-only)
./scripts/core/project sync             # pull everything you're entitled to
```

By default this applies to a `chore/core-sync-<version>` branch and
prints a diffstat — nothing is pushed or merged. Partial pulls and
version pinning: `docs/MANIFEST-UPGRADE-GUIDE.md` → "Pull-based sync".

### 2. The agentive-workflow plugin: the upgrader agent

Same as the packaged story — plugin-distributed agents/skills/commands
are upgraded by the `upgrader` agent per `docs/PLUGIN-UPGRADE-GUIDE.md`.

### 3. Everything else: whole-repo upstream merge (manual)

For files no sync tier covers:

```bash
git remote add upstream https://github.com/movito/agentive-starter-kit.git
git fetch upstream
git merge --allow-unrelated-histories upstream/main
./scripts/core/project reconfigure   # re-applies your project identity
```

- Files **only you changed** → your changes preserved
- Files **only upstream changed** → you get the updates
- Files **both changed** → merge conflict (you decide what to keep)

Prefer `project sync` for anything the manifest covers; keep
customizations in new files where possible.

---

**Source**: rewritten for the packaged-install era (KIT-0093,
KIT-ADR-0028 phase 2); legacy sections preserved from the KIT-0073
curation.

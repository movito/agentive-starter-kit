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

Projects whose scaffold carries `scripts/core/` copies predate the
packaged layout.

### 1. Kit-managed files: the copy-sync channel is retired

`project sync` and `scripts/.core-manifest.json` were removed in
KIT-ADR-0028 phase 4 (KIT-0102). The copy channel no longer exists in
any direction — upstream ships nothing to pull, and running `project
sync` now prints a pointer to this section.

Kit artifacts reach your project through the **agentive-workflow
plugin** (agents, skills, commands — see §2) and the **agentive-kit
package** (the `agentive` CLI). For the `scripts/core/` copies your
repo already carries, use the whole-repo merge in §3; they are yours
now, and nothing upstream will overwrite them.

### 2. The agentive-workflow plugin: the upgrader agent

Same as the packaged story — plugin-distributed agents/skills/commands
are upgraded by the `upgrader` agent per `docs/PLUGIN-UPGRADE-GUIDE.md`.

### 3. Everything else: whole-repo upstream merge (manual)

For anything the plugin and package don't carry:

```bash
git remote add upstream https://github.com/movito/agentive-starter-kit.git
git fetch upstream
git merge --allow-unrelated-histories upstream/main
./scripts/core/project reconfigure   # re-applies your project identity
```

- Files **only you changed** → your changes preserved
- Files **only upstream changed** → you get the updates
- Files **both changed** → merge conflict (you decide what to keep)

Keep customizations in new files where possible — it keeps the merge
in §3 conflict-free.

---

**Source**: rewritten for the packaged-install era (KIT-0093,
KIT-ADR-0028 phase 2); legacy sections preserved from the KIT-0073
curation.

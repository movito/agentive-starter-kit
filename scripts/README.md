# Scripts

## Directory Layout

### `core/` — Shared scripts

These scripts are shared across agentive projects. They are developed here
in agentive-starter-kit, which is the canonical home.

Current version: see `core/VERSION` (also what `./scripts/core/project
version` reports).

### `local/` — Project-specific scripts

Scripts unique to this project. Never overwritten by a re-bootstrap.

### `optional/` — Opt-in scripts

Scripts that downstream projects can copy to their `local/` directory if
needed.

## Distribution

The copy-sync channel was **retired in KIT-ADR-0028 phase 4** (KIT-0102,
2026-08-11). There is no manifest, no sync Action, and no `project sync`
subcommand: nothing copies these scripts downstream automatically, and
running `project sync` now prints a pointer to the replacements.

Kit artifacts reach a project two ways, both install-based:

| What | Ships via |
|---|---|
| agents, skills, slash commands | the `agentive-workflow` plugin — `docs/PLUGIN-UPGRADE-GUIDE.md` |
| the `agentive` CLI and shared tooling | the `agentive-kit` package |

Projects created before the packaged era still carry `scripts/core/`
copies. Those copies are theirs now — nothing upstream overwrites them.
See `docs/UPDATING-YOUR-PROJECT.md` for how such a project takes updates,
and `docs/DISTRIBUTION-ARCHITECTURE.md` for the full channel map.

# Manifest Upgrade Guide (retired)

**Status**: RETIRED — KIT-ADR-0028 phase 4 (KIT-0102, 2026-08-11)
**Source**: agentive-starter-kit

---

## The manifest sync channel is gone

This guide documented `.core-manifest.json` and the `project sync`
pull engine: the copy-era channel that shipped `scripts/core/`, slash
commands and `.kit/` content from the kit into downstream repos.

That channel was retired in KIT-ADR-0028 phase 4. The manifest, the
sync engine, the push Action and the `project sync` subcommand were all
deleted — there is nothing left to upgrade a manifest *to*, so the
step-by-step v1.x→v2.0.0 procedure has been removed rather than left
to mislead.

**What replaced it**

| Artifact | Now ships via |
|---|---|
| agents, skills, slash commands | the `agentive-workflow` plugin — `docs/PLUGIN-UPGRADE-GUIDE.md` |
| `scripts/core/` tooling, the `agentive` CLI | the `agentive-kit` package |
| everything else | whole-repo upstream merge — `docs/UPDATING-YOUR-PROJECT.md` |

Projects created before phase 2 still carry `scripts/core/` copies.
Those copies are now simply yours: nothing upstream overwrites them.
See `docs/UPDATING-YOUR-PROJECT.md` § "Copied-scripts projects".

The retired procedure remains in git history (and in the ADRs below)
for anyone reconstructing what the copy era did.

---

## Agent Model Pins

Canonical agent files in `.claude/agents/` pin a specific model ID in
frontmatter (`model:`) with a `last-updated` date, per KIT-0029. Pinned
IDs go stale: when upgrading the kit, check each canonical agent's
`model:` against currently available model IDs, bump where needed, and
update `last-updated` and `version` (semver patch for a pin-only bump).

## Reference

- **ADR-0008**: `.kit/adr/ADR-0008-tiered-manifest-sync.md` — architectural decision
- **KIT-ADR-0022**: `.kit/adr/KIT-ADR-0022-manifest-based-sync-ownership.md` — original internal ADR
- **Migration playbook**: `.kit/docs/KIT-MIGRATION-PLAYBOOK.md` — full `.kit/` layout migration (broader scope)

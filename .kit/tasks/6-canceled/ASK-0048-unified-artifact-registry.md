# ASK-0048: Unified Artifact Registry — Phase 1 (Metadata Adoption)

**Status**: Canceled
**Priority**: low (was high — see Disposition below)
**Assigned To**: unassigned
**Estimated Effort**: 4-6 hours (STALE — re-estimate against current architecture)
**Created**: 2026-04-01
**Target Completion**: TBD (was 2026-04-08)
**Linear ID**: (automatically backfilled after first sync)

> **Disposition (2026-07-14, operator + planner)**: PR #45 CLOSED without
> merging — it sat open since April 1 and predates the `.kit/` builder
> boundary (ASK-0044), plugin consolidation (KIT-0030), agent semver
> frontmatter (PR #61), and manifest sync v3 (KIT-0036). Too many
> conflicts and stale assumptions to rebase; the operator chose to re-do
> the task fresh later. BEFORE re-assignment this spec needs a
> re-evaluation pass: the registry design (ADR-0007) overlaps what the
> plugin channel + `version:` frontmatter + `.core-manifest.json` now
> already provide — Phase 1's value proposition must be re-argued or the
> task retired in favor of those mechanisms. The "supersedes KIT-0026"
> claim below is likewise stale (KIT-0026 itself needs re-scoping
> post-plugin). Closed PR kept as reference: #45.

> **SUPERSEDED NOTE (0.9.0, planner 2026-07-28)**: any
> `.kit/skills/` reference below is historical — that home was
> removed at 0.9.0 (KIT-0059); skills live only in `.claude/skills/`.
> Re-scope against current main before promoting this task.

> **Archived (2026-08-04, backlog review)**: the 2026-07-14 disposition required re-arguing the registry's value against the plugin channel + `version:` frontmatter + `.core-manifest.json`; nobody has, and those mechanisms have since carried v0.9.0 and daily kit work. Revive only with a concrete need they cannot meet.

## Related Tasks

**Parent Task**: None (new initiative)
**Depends On**: None
**Blocks**: ASK-0049 (Phase 2: CLI tooling — to be created)
**Related**: KIT-0026 (Sync agents and skills — superseded by this registry approach), ADV-0053 (Configurable adversarial dir)

## Overview

Add `registry:` metadata blocks to all shared agent definitions and skills in agentive-starter-kit, and create the registry index (`index.yml`). This is Phase 1 of ADR-0007 — non-breaking, metadata-only, no runtime changes.

**Why**: 11+ agent definitions are copy-pasted across 4 projects with no version tracking, no drift detection, and no update path. The registry envelope enables all three.

**What it supersedes**: KIT-0026 proposed adding agents/skills to `.core-manifest.json` tiers. ADR-0007's registry is more comprehensive — identity-based tracking, content hashing, propose-back. KIT-0026 can be canceled once Phase 1 ships.

## Detailed Requirements

### 1. Add `registry:` blocks to agents

For each `.claude/agents/*.md` file that is shared (not local-only):

```yaml
registry:
  type: agent
  version: 1.0.0           # initial version for all existing agents
  tier: core                # or optional, based on judgment
  source: agentive-starter-kit
  upstream_version: 1.0.0   # same as version for the canonical source
  last_synced: 2026-04-01
  origin: <original-agent-name>  # if derived from another
  created_by: "@movito"
  content_hash: sha256:<computed>
  tags: [<relevant-tags>]
  min_kit_version: 0.5.0
```

### 2. Add `registry:` blocks to skills

Same envelope format for any shared skills in `.claude/skills/` or `.kit/skills/`.

### 3. Create `.kit/registry/index.yml`

```yaml
schema_version: "1.0"
updated: 2026-04-01

artifacts:
  - name: <agent-name>
    type: agent
    version: 1.0.0
    tier: core
    path: .claude/agents/<filename>.md
    content_hash: sha256:<computed>
    tags: [...]
```

### 4. Content hash computation

Follow the ADR spec exactly:
- For Markdown: SHA-256 of everything after closing `---` of frontmatter
- Normalize: LF line endings, strip trailing whitespace per line, single trailing `\n`, UTF-8
- Format: `sha256:<64-char-hex-digest>`

Write a helper script (`scripts/core/compute_content_hash.py` or similar) to compute hashes reproducibly.

## Out of Scope

- CLI tooling (`kit registry status/sync/install/diff`) — that's Phase 2 (ASK-0049)
- Evaluator metadata — evaluators live in adversarial-evaluator-library, separate repo
- Runtime behavior changes — none
- Propose-back mechanism — Phase 3

## Acceptance Criteria

- [ ] All shared agents in `.claude/agents/` have `registry:` metadata blocks
- [ ] All shared skills have `registry:` metadata blocks
- [ ] `.kit/registry/index.yml` exists and lists all registered artifacts
- [ ] Content hashes are computed per the normalization spec
- [ ] A reproducible hash computation script exists
- [ ] Existing Claude Code agent loading is unaffected (verified by running agents)
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] CI passes

## Key References

| Resource | Location |
|----------|----------|
| ADR (full spec) | `.kit/adr/ADR-0007-unified-artifact-registry.md` |
| Task starter (detailed) | `.kit/context/ASK-UNIFIED-REGISTRY-TASK-STARTER.md` (superseded banner — re-evaluate first) |
| GitHub issue | movito/agentive-starter-kit#44 |
| Existing agents | `.claude/agents/*.md` |
| Existing manifest | `.core-manifest.json` |

## Design findings to fold into re-evaluation (CodeRabbit on PR #98, 2026-07-28)

When ADR-0007 moved to `.kit/adr/` (KIT-0067 D5), CodeRabbit reviewed
the proposal's content and surfaced five substantive design gaps. They
were deliberately NOT patched in that structural PR (the ADR text is
the record of what AEL's four evaluator rounds reviewed); they are
re-evaluation inputs for this task:

1. **Command-name inconsistency** — the principles section says
   `kit propose <artifact>` while the protocol defines
   `kit registry propose`; pick one or define the alias.
2. **`tier: deprecated` undefined** — deletion rules instruct setting
   `tier: deprecated`, but the tier schema allows only
   core/optional/local. Add it to the schema (with sync behavior) or
   use a separate deprecation field.
3. **Operational fields vs semver** — `last_synced` is updated on
   every sync yet documented as a patch-level metadata change; exclude
   operational fields (`last_synced`, `content_hash`,
   `proposed.status`) from version-bump requirements.
4. **Duplicate-source conflict rule contradicts itself** — "duplicate
   (type, name) definitions must fail" vs "first declared source
   wins"; choose one policy and define pinning/override interaction.
5. **Hash/version type confusion in the propose flow** — it compares a
   `content_hash` mismatch against `upstream_version` (a semver
   string, not content); compare content against the cached upstream
   artifact hash and versions separately.

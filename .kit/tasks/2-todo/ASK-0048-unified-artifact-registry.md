# ASK-0048: Unified Artifact Registry — Phase 1 (Metadata Adoption)

**Status**: Todo
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 4-6 hours
**Created**: 2026-04-01
**Target Completion**: 2026-04-08
**Linear ID**: (automatically backfilled after first sync)

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
| ADR (full spec) | `docs/adr/ADR-0007-unified-artifact-registry.md` |
| Task starter (detailed) | `docs/adr/ASK-UNIFIED-REGISTRY-TASK-STARTER.md` |
| GitHub issue | movito/agentive-starter-kit#44 |
| Existing agents | `.claude/agents/*.md` |
| Existing manifest | `.core-manifest.json` |

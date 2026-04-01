# Task Starter: Unified Artifact Registry

**Issue**: movito/agentive-starter-kit#44
**ADR**: `docs/adr/ADR-0007-unified-artifact-registry.md` (in this repo)
**Origin**: Designed and adversarially reviewed in `adversarial-evaluator-library`
**Date**: 2026-04-01

---

## Overview

The agentive ecosystem distributes agents, evaluators, and skills across projects via copy-paste, with no version tracking, no update notification, and no contribution path. ADR-0007 proposes a unified registry — metadata envelope, distribution protocol, and propose-back mechanism — to solve this for all three artifact types.

This is a multi-phase effort. Phase 1 is non-breaking and can ship independently.

Your mission: Read ADR-0007 in full, then implement Phase 1 (metadata adoption) and Phase 2 (CLI tooling) as separate PRs.

## ADR Summary

The ADR has been through 3 revision rounds informed by 4 adversarial evaluators (Gemini Pro, o3, Mistral Large, GPT-4o-mini). Key design decisions:

- **Not a package manager** — no dependency resolution, no build steps. Litmus test in ADR.
- **Three components**: metadata envelope (`registry:` block), distribution protocol (`index.yml` + `manifest.yml` + `lock.yml`), propose-back (`kit registry propose`)
- **Prior art**: Patterns adopted from chezmoi (content hashing), GNU Stow 2.0 (scan-then-execute atomicity), Dotbot (idempotent apply), Homebrew taps (distributed registry = git repo)
- **7 core principles** including: artifact is the record, three-layer cascade, no templating, idempotent apply
- **Explicit non-goals**: dependency resolution, transitive constraints, build steps, hosted registry, signing, constraint solving, plugin system

## Phased Implementation

### Phase 1: Metadata Adoption (PR 1 — non-breaking)

1. Add `registry:` block to all shared agents in `.claude/agents/`
2. Add `registry:` block to all shared skills in `.claude/skills/` (if any exist)
3. Create `.kit/registry/index.yml` listing all registered artifacts with name, type, version, tier, path, content_hash, tags
4. Verify: existing Claude Code agent loader ignores unknown frontmatter keys (it does — verified March 2026)

**Content hash procedure** (from ADR):
- For Markdown: SHA-256 of everything after closing `---` of frontmatter
- Normalize: LF line endings, strip trailing whitespace per line, single trailing `\n`, UTF-8
- Format: `sha256:<64-char-hex>`

**What NOT to do in Phase 1**:
- Don't touch evaluators yet (they live in adversarial-evaluator-library, a separate repo)
- Don't build CLI tooling yet
- Don't change any runtime behavior

### Phase 2: CLI Tooling (PR 2)

Implement `kit registry` subcommands:
- `kit registry status` — compare local artifacts against index, show drift/updates
- `kit registry sync` — pull updates from source repos (scan-then-execute: validate all, then write all)
- `kit registry install <name>` — install a specific artifact
- `kit registry diff <name>` — show diff between local and upstream

This requires:
- A `manifest.yml` parser (project policy: sources, tiers, pins, exclusions)
- A `lock.yml` generator (pinned SHAs for reproducibility)
- Content hash computation matching the spec above
- Idempotent behavior: running sync twice = running once

### Phase 3: Propose-back (PR 3)

- `kit registry propose <name>` — detect local modifications, open PR on upstream
- Requires `gh` CLI (fallback: `--patch` generates a `.patch` file)
- Adds `proposed:` metadata to artifact when proposed

### Phase 4: Deprecation (future)

- `.core-manifest.json` → `manifest.yml`
- `adversarial library install` → `kit registry install`
- Compatibility shims during transition

## Key Technical Details

### Metadata envelope format (agents)

```yaml
---
name: feature-developer-v5
description: Feature implementation specialist
model: claude-opus-4-6

registry:
  type: agent
  version: 1.2.0
  tier: core              # core | optional | local
  source: agentive-starter-kit
  upstream_version: 1.1.0
  last_synced: 2026-03-29
  origin: feature-developer-v3
  created_by: "@movito"
  content_hash: sha256:a1b2c3...
  tags: [implementation, tdd]
  min_kit_version: 0.5.0
  replaces: feature-developer-v3
---
```

### Identity rules

- Artifact identity = `(type, name)` tuple
- No two artifacts in a project may share `(type, name)`
- Source precedence follows declaration order in `manifest.yml`
- Deletion = set tier to `deprecated` in upstream index

### Tool-managed fields (humans don't edit these)

`content_hash`, `last_synced`, `upstream_version`, `proposed.status`

### Human-editable fields

`version`, `tier`, `tags`, `origin`, `created_by`, `min_kit_version`, `replaces`

## Resources

| Resource | Location |
|----------|----------|
| Full ADR | `docs/adr/ADR-0007-unified-artifact-registry.md` (this repo) |
| GitHub issue | movito/agentive-starter-kit#44 |
| Evaluator review logs | `adversarial-evaluator-library/.adversarial/logs/ADR-0007-*` |
| Existing manifest | `.core-manifest.json` (what the registry eventually supersedes) |
| Existing agents | `.claude/agents/*.md` |

## Adversarial Review Summary

4 evaluators reviewed the ADR. Key findings addressed in revisions:

- **Gemini Pro**: Missing deletion/deprecation, `replaces` semantics, content hash needs per-type approach — all added
- **o3**: O(1) drift claim overstated — corrected to "constant-time comparison"
- **Mistral Large**: 11 specific improvements (4 critical, 4 significant, 3 minor) — all addressed: trust model, hashing spec, offline/online split, conflict rules, backwards compat matrix, versioning policy, automation requirements, governance
- **GPT-4o-mini**: Glossary gaps — expanded from 3 to 7 terms

## Acceptance Criteria

- [ ] All shared agents in `.claude/agents/` have `registry:` metadata blocks
- [ ] `index.yml` exists and lists all registered artifacts with correct content hashes
- [ ] Content hashes are computed per the normalization spec in the ADR
- [ ] Existing Claude Code agent loading is unaffected (no runtime changes)
- [ ] `kit registry status` shows current state of all registered artifacts
- [ ] All tests pass, no regressions

## Notes

- Start by reading the full ADR — it's 590 lines but well-structured with a table of contents via headers
- The ADR is the spec. If something is ambiguous, check the ADR first before making assumptions
- Phase 1 is intentionally conservative — metadata only, no behavior changes
- The evaluator library (adversarial-evaluator-library) will adopt the registry format separately once the tooling exists here

---

**Recommended agent**: `feature-developer` or equivalent implementation agent with access to the ASK codebase

# Starter Kit Architecture Decision Records

This folder contains ADRs inherited from the **agentive-starter-kit** template. These document the architectural decisions made for the starter kit infrastructure.

## For Users of This Template

**These ADRs are read-only reference material.** They document patterns and decisions you inherit when using the starter kit:

- Agent initialization patterns
- Code review workflows
- Task management with Linear
- Logging and configuration architecture
- And more...

**Your project's ADRs belong in `docs/adr/`** - start fresh with `ADR-0001`.

## Naming Convention

| Prefix | Location | Purpose |
|--------|----------|---------|
| `KIT-ADR-XXXX` | `starter-kit-adr/` | Starter kit infrastructure decisions (reference) |
| `ADR-XXXX` | `adr/` | Your project-specific decisions |

## Index

| ID | Title | Status |
|----|-------|--------|
| KIT-ADR-0001 | System Prompt Size Considerations | Accepted |
| KIT-ADR-0002 | Serena MCP Integration | Accepted |
| KIT-ADR-0003 | Linear Sync vs MCP | Accepted |
| KIT-ADR-0004 | Adversarial Workflow Integration | Accepted |
| KIT-ADR-0005 | Test Infrastructure Strategy | Accepted |
| KIT-ADR-0006 | Agent Session Initialization | Accepted |
| KIT-ADR-0007 | Dependabot Automation | Accepted |
| KIT-ADR-0008 | Configuration Architecture | Accepted |
| KIT-ADR-0009 | Logging & Observability | Accepted |
| KIT-ADR-0010 | OpenAPI Specification Strategy | Accepted |
| KIT-ADR-0011 | API Versioning Strategy | Accepted |
| KIT-ADR-0012 | Task Status Linear Alignment | Accepted |
| KIT-ADR-0013 | Real-Time Task Monitoring | Accepted |
| KIT-ADR-0014 | Code Review Workflow | Accepted |
| KIT-ADR-0015 | MCP Tool Addition Pattern | Accepted |
| KIT-ADR-0016 | Validation Architecture | Accepted |
| KIT-ADR-0017 | API Testing Infrastructure | Accepted |
| KIT-ADR-0018 | Workflow Observation | Accepted |
| KIT-ADR-0019 | Review Knowledge Extraction | Proposed |
| KIT-ADR-0020 | Research Quality Coupling Strategy | Accepted |
| KIT-ADR-0021 | Real-Time Agent Communication | Proposed (superseded by 0021-B) |
| KIT-ADR-0021-B | Real-Time Agent Communication (Revised) | Proposed |
| KIT-ADR-0022 | Manifest-Based Sync Ownership | Accepted |
| KIT-ADR-0023 | Builder/Project Separation — the `.kit/` boundary | Proposed |
| KIT-ADR-0024 | Cross-Repo Topology and Drift Control | Proposed |
| KIT-ADR-0025 | Agent Localization vs Plugin Upgrades | Accepted |
| KIT-ADR-0026 | Pull-Based Consumer Sync | Accepted (superseded by 0028 on migration) |
| KIT-ADR-0027 | A Leaner, Language-Agnostic Kit | Accepted |
| KIT-ADR-0028 | Versioned Packages, Not File Copies | Accepted — COMPLETE |
| KIT-ADR-0029 | Task-as-Folder | Proposed — deliberately deferred |
| KIT-ADR-0030 | The Door Ships in the Package | Proposed |
| KIT-ADR-0031 | `project-intake` Ships in the Plugin | Proposed |
| KIT-ADR-0032 | Two Rungs — `.kit/` Never in Code Repos | Proposed |
| KIT-ADR-0033 | Handoff Brief Primacy | Proposed |
| KIT-ADR-0034 | What Generates Kit Work | Proposed (governance) |

KIT-ADR-0030 through 0034 were drafted as one combined ADR ("the door
is a tool, not a place", PR #128, closed unmerged 2026-08-13) and split
one-per-concern by operator decision; see KIT-ADR-0030's Provenance
section.

## Legacy-prefix ADRs in this directory

Two kit decisions predate the KIT-ADR numbering and keep their
original `ADR-` filenames (moved here from `docs/adr/` by KIT-0067 D5
— that directory belongs to the consumer project's own decisions):

| File | Title | Status |
|------|-------|--------|
| `ADR-0007-unified-artifact-registry.md` | Unified Artifact Registry | Proposed (owning task ASK-0048 parked) |
| `ADR-0008-tiered-manifest-sync.md` | Tiered Manifest Sync | Accepted (cited by DISTRIBUTION-ARCHITECTURE, MANIFEST-UPGRADE-GUIDE) |

They are unrelated to KIT-ADR-0007/KIT-ADR-0008 above despite the
similar numbers.

## When to Reference These

Reference these KIT-ADRs when:

- Understanding how the starter kit works
- Deciding whether to adopt or modify a pattern
- Training agents on project conventions
- Onboarding new team members

## Modifying Starter Kit Patterns

If you need to change a pattern from the starter kit:

1. **Create a new ADR** in `docs/adr/` explaining your change
2. **Reference the KIT-ADR** you're superseding
3. **Document the rationale** for diverging

Example:

```markdown
# ADR-0001: Custom Logging Format

**Status**: Accepted
**Supersedes**: KIT-ADR-0009 (Logging & Observability)

## Context
We need JSON-structured logs for our monitoring system...
```

---

**Template**: agentive-starter-kit
**Last Updated**: 2026-08-13

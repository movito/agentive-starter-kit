# ASK-0048 Review Starter — Unified Artifact Registry Phase 1

**PR**: #45
**Branch**: `feature/ASK-0048-unified-artifact-registry`
**Author**: feature-developer-v5
**Date**: 2026-04-01

## What Changed

Phase 1 of ADR-0007: adds `registry:` metadata blocks to all shared agents and skills, creates the central registry index, and provides content hash computation tooling.

### Key Files

| File | Change | Why |
|------|--------|-----|
| `scripts/core/compute_content_hash.py` | **NEW** | Content hash computation per ADR-0007 spec |
| `tests/test_compute_content_hash.py` | **NEW** | 25 tests covering all hash functions |
| `.kit/registry/index.yml` | **NEW** | Central registry listing 19 artifacts |
| `.claude/agents/*.md` (14 files) | Modified | Added `registry:` frontmatter blocks |
| `.claude/skills/*/SKILL.md` (2 files) | Modified | Added `registry:` frontmatter blocks |
| `.kit/skills/*/SKILL.md` (3 files) | Modified | Added `registry:` frontmatter blocks |
| `scripts/.core-manifest.json` | Modified | Added `compute_content_hash.py` to scripts_core |
| `tests/test_core_manifest.py` | Modified | Updated count expectations (15/40) |
| `CLAUDE.md` | Modified | Added pytest invocation note |
| `docs/adr/ADR-0007-unified-artifact-registry.md` | Modified | Fixed CLI namespace, markdownlint issues |

### Tier Classification

- **Core agents** (8): ci-checker, code-reviewer, feature-developer, feature-developer-v3, feature-developer-v5, planner, planner2, test-runner
- **Optional agents** (6): agent-creator, bootstrap, document-reviewer, onboarding, powertest-runner, security-reviewer
- **Core skills** (5): bot-triage, pre-implementation, code-review-evaluator, review-handoff, self-review

## Review Checklist

- [ ] Content hashes are stable (frontmatter changes don't affect body hash)
- [ ] YAML stripping only targets top-level `registry:`/`_meta:` keys
- [ ] All 19 artifacts correctly classified by tier
- [ ] `index.yml` schema matches ADR-0007 specification
- [ ] No runtime behavior changes (metadata-only)
- [ ] Test coverage adequate for hash computation functions

## Bot Review Summary

- **12 total threads** across 3 babysit cycles
- **7 fixed**: top-level YAML stripping, empty lines preservation, markdownlint, code fences, handoff path, CLI namespace, unused import
- **5 resolved without fix**: indented `---`, CRLF test nuance, tier enum (Phase 2 scope), hash placeholder format, empty lines within blocks
- All 12 threads replied to and resolved

## Evaluator Review

- **Verdict**: APPROVED
- **File**: `.kit/context/reviews/ASK-0048-evaluator-review.md`

# ASK-0040: Consolidate .env.example and .env.template

**Status**: Done
**Priority**: low
**Assigned To**: feature-developer-v3
**Estimated Effort**: 30 min
**Created**: 2026-02-27

## Problem

The project has two env template files that are out of sync:

- `.env.template` (121 lines) — comprehensive, canonical, used by onboarding, README, ADRs (20+ references)
- `.env.example` (49 lines) — minimal, legacy from adversarial-workflow init

`.env.template` has Linear config, logging, Gemini, Mistral, project settings.
`.env.example` only has Anthropic + OpenAI keys.

Agent instructions (`feature-developer-v3.md`, `feature-developer.md`) reference `.env.example` but the
canonical template is `.env.template`.

## Strategy

Keep **both files** but make `.env.example` a copy of `.env.template` content. Rationale:
- `adversarial init` regenerates `.env.example` — we can't delete it without confusing the workflow tool
- `.env.template` is the canonical file (20+ references in ADRs, docs, onboarding)
- All *our* references should point to `.env.template`

## Requirements

### 1. Sync .env.example content with .env.template

Copy `.env.template` content into `.env.example` so they match.
Add a comment at the top of `.env.example`:

```bash
# NOTE: This file is kept in sync with .env.template.
# The canonical template is .env.template — edit that file, not this one.
# This file exists because adversarial-workflow's `init` command expects it.
```

### 2. Update agent instructions (2 files)

| File | Current | Change to |
|------|---------|-----------|
| `.claude/agents/feature-developer-v3.md:349` | `Never modify .env files (use .env.example)` | `Never modify .env files (use .env.template)` |
| `.claude/agents/feature-developer.md:566` | `Never modify .env files directly (use .env.example)` | `Never modify .env files directly (use .env.template)` |

### 3. Update adversarial scripts (4 files)

All 4 scripts have identical line 27: `echo "     cp .env.example .env"`

| File | Change |
|------|--------|
| `.adversarial/scripts/evaluate_plan.sh:27` | `.env.example` → `.env.template` |
| `.adversarial/scripts/proofread_content.sh:27` | `.env.example` → `.env.template` |
| `.adversarial/scripts/review_implementation.sh:27` | `.env.example` → `.env.template` |
| `.adversarial/scripts/validate_tests.sh:27` | `.env.example` → `.env.template` |

### 4. Verify — no other stale references

```bash
# After changes, this should return only:
# - The task file itself
# - .venv/ (adversarial-workflow package internals — cannot change)
# - .env.example itself (the sync comment)
grep -rn "\.env\.example" . --include="*.md" --include="*.sh" --include="*.py" \
  | grep -v ".git/" | grep -v "5-done/" | grep -v "8-archive/" | grep -v ".venv/" \
  | grep -v "ASK-0040"
```

Expected: zero results from project files.

## Acceptance Criteria

- [ ] `.env.example` content matches `.env.template` (with sync comment header)
- [ ] `.env.example` has header comment explaining it's a copy
- [ ] `feature-developer-v3.md` references `.env.template`
- [ ] `feature-developer.md` references `.env.template`
- [ ] All 4 adversarial scripts reference `.env.template`
- [ ] Verification grep returns zero project-file results

## Notes

- This is a **docs/config-only task** — no Python code changes
- The `.venv/` references to `.env.example` are in the adversarial-workflow package and cannot be changed here
- Do NOT delete `.env.example` — adversarial-workflow's `init` command expects it

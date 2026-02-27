# ASK-0040: Consolidate .env.example and .env.template

**Status**: Backlog
**Priority**: low
**Assigned To**: feature-developer-v3
**Estimated Effort**: 30 min
**Created**: 2026-02-27

## Problem

The project has two env template files that are out of sync:

- `.env.template` (104 lines) — comprehensive, used by onboarding, README, ADRs
- `.env.example` (47 lines) — minimal, legacy from adversarial-workflow init

`.env.template` has Linear config, logging, Gemini, Mistral, project settings.
`.env.example` only has Anthropic + OpenAI keys.

Agent instructions (`feature-developer-v3.md`) reference `.env.example` but the
canonical template is `.env.template`.

## Requirements

1. Replace `.env.example` content with `.env.template` content (one canonical source)
2. Update agent instructions to reference `.env.template` (or whichever is kept)
3. Update `.adversarial/scripts/*.sh` references (4 files reference `.env.example`)
4. Verify `adversarial init` behavior (it may regenerate `.env.example`)

## Acceptance Criteria

- [ ] Single canonical env template file
- [ ] All references point to the same file
- [ ] Agent instructions updated
- [ ] Adversarial workflow scripts updated

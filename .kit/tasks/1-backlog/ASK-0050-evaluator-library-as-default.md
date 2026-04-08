# ASK-0050: Ship Evaluator Library as Default, Drop Built-in GPT-4o

**Status**: Backlog
**Priority**: high
**Assigned To**: feature-developer-v3
**Estimated Effort**: 2-3 hours
**Created**: 2026-04-08
**Target Completion**: TBD (depends on ASK-0049)
**Linear ID**:

## Related Tasks

**Depends On**: ASK-0049 (Replace Aider with LiteLLM)
**Related**: ADV-0053 (configurable .adversarial dir)

## Overview

Replace the built-in GPT-4o evaluator with the adversarial-evaluator-library as the
standard evaluation setup. Currently, the starter kit ships with a hardcoded GPT-4o
default that forces every user to have an `OPENAI_API_KEY`. The evaluator library offers
better, specialized evaluators — and the Gemini-based ones are nearly free.

**Why this matters**:
- Built-in GPT-4o is a generic prompt; library evaluators have tuned, specialized prompts
- `OPENAI_API_KEY` requirement is a barrier to adoption — Gemini keys are free
- The built-in evaluators are already marked "deprecated" in project docs
- Library evaluators (`arch-review-fast`, `code-reviewer-fast`) are the recommended path

**Goal**: A new user cloning the starter kit should be able to run evaluations with
only a `GEMINI_API_KEY` (free tier), no OpenAI key required.

## Requirements

### Functional Requirements
1. Pre-install evaluator library during project setup (or auto-install on first `adversarial` run)
2. Set `arch-review-fast` (Gemini) as default plan evaluator
3. Set `code-reviewer-fast` (Gemini) as default code review evaluator
4. Update `.env.template`: make `GEMINI_API_KEY` the primary key, `OPENAI_API_KEY` optional
5. Update `config.yml`: remove `evaluator_model: gpt-4o` default (or point to library evaluator)
6. Update planner agent instructions to reference library evaluators as primary
7. Update onboarding flow to guide users toward Gemini key setup
8. Keep OpenAI/Anthropic/Mistral evaluators available as opt-in via library

### Non-Functional Requirements
- [ ] Zero-config experience: `GEMINI_API_KEY` + `adversarial arch-review-fast task.md` works out of the box
- [ ] No regression: all existing evaluator library commands still work
- [ ] Documentation updated: EVALUATION-WORKFLOW.md, README references

## Implementation Plan

### Step 1: Update defaults
- Edit `.adversarial/config.yml` to reference library evaluators
- Edit `.env.template` to prioritize `GEMINI_API_KEY`
- Edit onboarding scripts/docs

### Step 2: Auto-install evaluator library
- Update `./scripts/core/project setup` to run `install-evaluators` automatically
- Or: have `adversarial` CLI auto-install on first run if evaluators dir is empty

### Step 3: Update agent instructions
- Planner agent: update default evaluator commands
- EVALUATION-WORKFLOW.md: update recommended flow
- CLAUDE.md: update any evaluator references

### Step 4: Deprecation cleanup
- Mark built-in `evaluate`/`proofread`/`review` commands as legacy
- Add deprecation notice in `adversarial evaluate` output (upstream)

## Acceptance Criteria

### Must Have
- [ ] Fresh clone + `GEMINI_API_KEY` → can run evaluations without OpenAI key
- [ ] Evaluator library installed during setup
- [ ] `.env.template` shows Gemini as primary, OpenAI as optional
- [ ] Planner agent uses library evaluators by default
- [ ] CI passes

### Should Have
- [ ] Onboarding flow updated
- [ ] EVALUATION-WORKFLOW.md updated
- [ ] Built-in evaluators marked as legacy/deprecated

### Nice to Have
- [ ] Auto-install evaluator library on first `adversarial` run
- [ ] Cost comparison table in docs (Gemini free tier vs GPT-4o)

## Risks & Mitigations

### Risk 1: Gemini API rate limits on free tier
**Likelihood**: Medium
**Impact**: Low — affects high-volume users only
**Mitigation**: Document rate limits; OpenAI evaluators remain available as fallback

### Risk 2: Evaluator library version drift
**Likelihood**: Low
**Impact**: Medium — broken evaluators after library update
**Mitigation**: Version pinned in `scripts/core/project` (`EVALUATOR_LIBRARY_VERSION`)

## References

- **Evaluator library**: github.com/movito/adversarial-evaluator-library
- **Current workflow**: `.adversarial/docs/EVALUATION-WORKFLOW.md`
- **Config**: `.adversarial/config.yml`
- **Install mechanism**: `./scripts/core/project install-evaluators`

---

**Template Version**: 1.0.0
**Created**: 2026-04-08

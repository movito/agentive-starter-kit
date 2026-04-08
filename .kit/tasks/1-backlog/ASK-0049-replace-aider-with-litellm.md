# ASK-0049: Replace Aider Transport with LiteLLM in Adversarial Pipeline

**Status**: Backlog
**Priority**: high
**Assigned To**: feature-developer-v3
**Estimated Effort**: 3-5 hours
**Created**: 2026-04-08
**Target Completion**: TBD (blocked on upstream)
**Linear ID**:

## Related Tasks

**Depends On**: [movito/adversarial-workflow#59](https://github.com/movito/adversarial-workflow/issues/59) — upstream must ship LiteLLM transport first
**Blocks**: ASK-0050 (Ship evaluator library as default)
**Related**: ADV-0053 (configurable .adversarial dir)

## Overview

Replace Aider as the LLM transport layer in the adversarial evaluation pipeline with
direct LiteLLM calls. Aider is a full AI-coding assistant being used as a dumb LLM pipe
— evaluator scripts explicitly disable most features (`--no-git --map-tokens 0 --no-gitignore`).

**Why this matters**:
- Aider is the heaviest transitive dependency in the project
- Aider pins Python to <3.13 (blocks modern Python adoption)
- Two layers of subprocess indirection for a simple HTTP call
- New users are confused by a "coding assistant" dependency in an evaluation tool

**Context**: The evaluator YAML files already use LiteLLM-style model strings
(`gemini/gemini-2.5-pro`, `mistral/mistral-large`). Aider uses LiteLLM internally,
so cutting out the middleman is natural.

## Requirements

### Functional Requirements
1. Update `adversarial-workflow` dependency to version with LiteLLM transport (once upstream ships)
2. Remove `aider-chat` from `pyproject.toml` dependencies
3. Verify all evaluator invocation paths work without Aider:
   - `adversarial evaluate <file>` (built-in)
   - `adversarial <library-evaluator> <file>` (e.g., `adversarial arch-review task.md`)
   - Shell scripts in `.adversarial/scripts/` (if still used)
4. Update `.adversarial/scripts/` to remove direct Aider calls (or deprecate scripts)
5. Verify Python 3.13+ compatibility after Aider removal
6. Update `.env.template` to remove Aider-specific notes

### Non-Functional Requirements
- [ ] No change to evaluator output format (markdown with verdicts)
- [ ] No change to evaluator YAML schema (model strings stay the same)
- [ ] CI passes on Python 3.10-3.13

## Implementation Plan

### Approach

**Step 1: Wait for upstream**
- Track movito/adversarial-workflow#59
- Once shipped, bump `adversarial-workflow` version pin in `pyproject.toml`

**Step 2: Remove Aider**
- Remove `aider-chat` from dev dependencies
- Update `.adversarial/scripts/` shell scripts (replace `aider` calls or mark deprecated)
- Test all evaluator paths

**Step 3: Validate**
- Run `adversarial check` to verify setup
- Run a real evaluation to confirm output format unchanged
- Test on Python 3.13 if available

## Acceptance Criteria

### Must Have
- [ ] `aider-chat` removed from `pyproject.toml`
- [ ] All evaluator commands work via LiteLLM transport
- [ ] Evaluator output format unchanged
- [ ] CI passes
- [ ] `.env.template` updated

### Should Have
- [ ] Shell scripts in `.adversarial/scripts/` updated or deprecated
- [ ] Python 3.13 tested

## Risks & Mitigations

### Risk 1: Upstream delays
**Likelihood**: Medium
**Impact**: High — this task is fully blocked
**Mitigation**: Can contribute to upstream PR if needed

### Risk 2: LiteLLM model compatibility gaps
**Likelihood**: Low
**Impact**: Medium — some evaluators might break
**Mitigation**: Evaluator library already uses LiteLLM model strings; compatibility is expected

## References

- **Upstream issue**: movito/adversarial-workflow#59
- **Current integration ADR**: `.kit/adr/KIT-ADR-0004-adversarial-workflow-integration.md`
- **Evaluator workflow**: `.adversarial/docs/EVALUATION-WORKFLOW.md`

---

**Template Version**: 1.0.0
**Created**: 2026-04-08

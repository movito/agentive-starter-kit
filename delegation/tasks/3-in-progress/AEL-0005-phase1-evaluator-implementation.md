# AEL-0005: Phase 1 Evaluator Implementation

**Status**: In Progress
**Priority**: High
**Assigned To**: feature-developer
**Estimated Effort**: 4-6 hours
**Created**: 2026-02-01
**Source**: ADR-0002 Phase 1 - Multi-Evaluator Architecture Expansion

## Problem Statement

The current evaluator library has 9 evaluators across 3 providers (Google, OpenAI, Mistral). To achieve cognitive diversity and robust evaluation coverage, we need:

1. **Anthropic as Tier 1 provider** - Missing entirely from current setup
2. **Code review coverage** - Only Mistral's codestral-code exists
3. **Diversity/synthesis categories** - Limited options in OpenAI

## Goals

1. **Add Anthropic provider** - 3 evaluators covering adversarial, code-review, and quick-check
2. **Expand Google code coverage** - Add gemini-code evaluator
3. **Complete OpenAI categories** - Add diversity and synthesis evaluators
4. **Achieve 18 total evaluators** across 4 providers

## Requirements

### Must Have

- [ ] Create `anthropic/claude-adversarial/` - Adversarial review evaluator
- [ ] Create `anthropic/claude-code/` - Code review evaluator
- [ ] Create `anthropic/claude-quick/` - Quick check evaluator
- [ ] Create `google/gemini-code/` - Code review evaluator
- [ ] Create `openai/gpt5-diversity/` - Cognitive diversity evaluator
- [ ] Create `openai/gpt5-synthesis/` - Knowledge synthesis evaluator
- [ ] Update `index.json` with all 6 new evaluators
- [ ] Each evaluator has README.md with use cases

### Should Have

- [ ] All evaluators pass YAML validation
- [ ] All evaluators return valid output on test fixtures
- [ ] CHANGELOG.md for each evaluator

### Nice to Have

- [ ] Performance benchmarks for each evaluator
- [ ] Cost comparison documentation

## Implementation

### Evaluator Specifications

| Name | Provider | Category | Model | Description |
|------|----------|----------|-------|-------------|
| claude-adversarial | anthropic | adversarial | claude-sonnet-4-20250514 | Critical review and stress-testing |
| claude-code | anthropic | code-review | claude-sonnet-4-20250514 | Code and config analysis |
| claude-quick | anthropic | quick-check | claude-3-5-haiku-20241022 | Fast document assessment |
| gemini-code | google | code-review | gemini/gemini-2.5-flash | Code review with multimodal capability |
| gpt5-diversity | openai | cognitive-diversity | gpt-5.2 | Alternative perspective evaluation |
| gpt5-synthesis | openai | knowledge-synthesis | gpt-5.2 | Cross-reference and synthesis |

### Directory Structure

```
.adversarial/evaluators/
├── anthropic/
│   ├── claude-adversarial/
│   │   ├── evaluator.yml
│   │   ├── README.md
│   │   └── CHANGELOG.md
│   ├── claude-code/
│   │   └── ...
│   └── claude-quick/
│       └── ...
├── google/
│   └── gemini-code/
│       └── ...
└── openai/
    ├── gpt5-diversity/
    │   └── ...
    └── gpt5-synthesis/
        └── ...
```

## Acceptance Criteria

1. All 6 evaluator directories exist with correct structure
2. Each evaluator.yml passes YAML validation
3. index.json includes all 6 entries with correct metadata
4. Each README.md documents use cases and configuration
5. `adversarial list-evaluators` shows all 18 evaluators (9 existing + 6 new + 3 root aliases)

## Testing

### Validation Tests

```bash
# Verify YAML syntax
python -c "import yaml; yaml.safe_load(open('.adversarial/evaluators/anthropic/claude-adversarial/evaluator.yml'))"

# List evaluators
adversarial list-evaluators

# Verify count
adversarial list-evaluators | grep -c "evaluator"
```

### Integration Tests (Manual)

```bash
# Test with API keys set
adversarial claude-adversarial test-fixture.md
adversarial gemini-code test-fixture.py
```

## References

- ASK-0029: Multi-Evaluator Architecture (completed)
- ADR-0002: Multi-Evaluator Architecture
- Existing evaluators: `.adversarial/evaluators/`

## Notes

- Anthropic models use `ANTHROPIC_API_KEY` environment variable
- Claude models support 200k context window
- Haiku is optimized for speed and cost-efficiency

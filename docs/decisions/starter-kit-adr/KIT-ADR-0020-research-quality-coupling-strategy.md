# KIT-ADR-0020: Research Quality Standards Coupling Strategy

**Status**: Accepted
**Date**: 2025-01-28
**Deciders**: Starter Kit Maintainers
**Related**: KIT-ADR-0004 (Adversarial Workflow Integration)

## Context

We implemented Research Quality Standards for knowledge-focused agents. The standards include four quality gates, with Gate 4 (External Validation) depending on the adversarial-workflow CLI tool.

During implementation, we identified architectural coupling between:

1. **Agent definitions** → Research Quality Standards workflow document
2. **Agent definitions** → adversarial-workflow CLI commands (inline)
3. **Workflow document** → adversarial-workflow CLI commands

The question arose: Should we decouple agent definitions from the specific CLI tool to reduce maintenance burden when adversarial-workflow evolves?

## Analysis

### Three Levels of Abstraction

| Level | What Agent Says | Coupling | Maintenance Cost |
|-------|-----------------|----------|------------------|
| **Tool-specific** | `adversarial evaluate <file>` | Tight | Update N agents when CLI changes |
| **Mechanism-aware** | "Request external validation per workflow doc" | Loose | Update 1 workflow doc |
| **Goal-only** | "Ensure document is validated" | None | Agents don't know how to act |

### Rate of Change Analysis

| Layer | Expected Change Frequency |
|-------|--------------------------|
| Goals (4 Quality Gates) | Rarely |
| Mechanism (external validation) | Occasionally |
| Tool (adversarial-workflow CLI) | More often |

### Trade-off

**Loose coupling (mechanism-aware)**:
- Pro: Update 1 file when CLI changes
- Con: Agents need extra lookup; may not follow through

**Tight coupling (tool-specific)**:
- Pro: Clear, actionable instructions; agents execute reliably
- Con: Multiple files to update when CLI changes

## Decision

**Keep tight coupling.**

Rationale:
1. **Agent effectiveness**: Experience shows agents need explicit, actionable commands to reliably execute the adversarial evaluation workflow
2. **Current stability**: adversarial-workflow CLI is relatively stable
3. **Documented debt**: By documenting coupled files, projects can refactor later if needed
4. **Adopter experience**: Tight coupling ensures adopters get working agents out of the box

## Consequences

### Positive
- Agents have clear, copy-paste commands
- No extra file lookups during agent execution
- Higher likelihood of actual compliance with quality standards

### Negative
- If adversarial-workflow CLI changes significantly, must update multiple files
- Duplication of command syntax across files
- Harder to swap out adversarial-workflow for alternative tools

### Mitigation
- Coupling manifest maintained (see below)
- Grep pattern provided for finding all coupled files
- Decision can be revisited if CLI changes become frequent

## Coupling Manifest Template

Projects adopting Research Quality Standards should track coupled files:

### Files with Direct adversarial-workflow CLI References

| File | Coupling Type | Commands Referenced |
|------|---------------|---------------------|
| `.agent-context/workflows/RESEARCH-QUALITY-STANDARDS.md` | Primary source | `adversarial evaluate`, evaluator names |
| `.claude/agents/[knowledge-agent].md` | Consumer | `adversarial evaluate` |

### Quick Discovery Commands

```bash
# Find all files referencing adversarial CLI
grep -r "adversarial evaluate" .claude/agents/ .agent-context/workflows/

# Find all files referencing specific evaluators
grep -r "gpt52-reasoning\|mistral-content\|o3-chain" .claude/agents/ .agent-context/

# Count coupled files
grep -l "adversarial evaluate" .claude/agents/*.md .agent-context/workflows/*.md | wc -l
```

### Coupling Categories

1. **Command coupling**: References to `adversarial evaluate`
2. **Evaluator coupling**: References to specific evaluator names
3. **Output path coupling**: References to `.adversarial/logs/`

## Future Refactoring Path

If a project decides to decouple later:

1. **Remove inline commands** from knowledge agent files
2. **Keep mechanism language**: "Request external validation per workflow standards"
3. **Centralize commands** in workflow document only

Estimated effort: ~1 hour to refactor all files.

## Review Triggers

Revisit this decision if:
- adversarial-workflow CLI undergoes breaking changes
- Need to support alternative validation tools
- Maintenance burden of updating files becomes problematic

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-28 | Initial decision to keep tight coupling |

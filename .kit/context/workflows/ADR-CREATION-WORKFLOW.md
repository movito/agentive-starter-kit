# ADR Creation Workflow

**Purpose**: Document architectural decisions using ADR format
**Agent**: Primarily document-reviewer, but all agents can create ADRs
**Last Updated**: 2025-11-01

---

## When to Use

- ✅ After major architectural decision is made
- ✅ When new integration patterns are adopted
- ✅ When implementation approach changes significantly

**Don't use for**:
- ❌ Minor implementation details
- ❌ Trivial code changes
- ❌ Every small decision

---

## Workflow Steps

1. **Create ADR file**: `docs/adr/NNNN-short-title.md`
   - NNNN = sequential 4-digit number (0001, 0002, etc.)
   - short-title = kebab-case description
   - Example: `0013-gui-electron-integration.md`

2. **Use ADR template** (context, problem, decision, implementation, consequences, alternatives)

3. **Research**:
   - Check task files for requirements
   - Code inspection for implementation details
   - Git history for commits and changes
   - Test validation for verification

4. **Include**:
   - Real code examples from implementation
   - Real-world results (test metrics, performance data)
   - Honest trade-offs (pros AND cons)
   - Cross-references to related ADRs, tasks, commits

5. **Update index**: Add new ADR to `docs/adr/README.md`

6. **Verify cross-references**: Ensure all links work

7. **Commit** with descriptive message: `docs: Add ADR-NNNN - <title>`

---

## ADR Template Structure

```markdown
# ADR-NNNN: Title

**Status**: Accepted | Proposed | Deprecated | Superseded by ADR-YYYY
**Date**: YYYY-MM-DD
**Deciders**: [Agent name or team]
**Tags**: [architecture, integration, performance, etc.]

---

## Context

Why was this decision needed? What problem or requirement led to this?

## Problem

What specific problem are we solving? What are the constraints?

## Decision

What did we decide to do? Be specific and clear.

## Implementation

How was it implemented? Include:
- Code examples (real code from the project)
- File locations
- Key functions/classes
- Configuration changes

```python
# Example code snippet
class Example:
    def method(self):
        pass
```

## Consequences

### Positive:
- What benefits do we get?
- What problems does this solve?

### Negative:
- What trade-offs did we make?
- What limitations does this introduce?
- What technical debt did we accept?

## Alternatives Considered

### Alternative 1: [Name]
- **Description**: What was this approach?
- **Pros**: Benefits
- **Cons**: Drawbacks
- **Why Not Chosen**: Specific reasons

### Alternative 2: [Name]
- **Description**: ...
- **Pros**: ...
- **Cons**: ...
- **Why Not Chosen**: ...

## Results

Real-world outcomes:
- Test results (e.g., "300/350 tests passing, 0 regressions")
- Performance metrics (e.g., "3ms average, down from 45ms")
- User feedback (if available)
- Issues encountered during implementation

## References

- Related ADRs: [ADR-XXXX](./XXXX-title.md)
- Task files: `.kit/tasks/active/TASK-YYYY-####.md`
- Commits: abc1234, def5678
- External docs: Links to libraries, standards, etc.

---

**Last Updated**: YYYY-MM-DD
**Reviewed**: YYYY-MM-DD
```

---

## Quality Standards

### Required Elements:

| Section | What to Include |
|---------|-----------------|
| **Context** | Why was this decision needed? |
| **Problem** | What problem are we solving? |
| **Decision** | What did we decide to do? |
| **Implementation** | How was it implemented? (with code examples) |
| **Consequences** | What are the results? (positive + negative) |
| **Alternatives** | What else was considered? Why not chosen? |
| **Results** | Real-world outcomes (test results, metrics, user feedback) |
| **References** | Links to tasks, commits, related ADRs |

### Target Length:

- **Average**: 300+ lines for comprehensive ADRs
- **Minimum**: 150 lines for simpler decisions
- **Maximum**: No limit (be thorough, not verbose)

---

## Best Practices

### ✅ DO:
- Include real code examples from implementation
- Be honest about trade-offs and limitations
- Cross-reference related ADRs and tasks
- Verify all links and references work
- Update index (README.md) when adding new ADR
- Use actual metrics and test results

### ❌ DON'T:
- Don't document every small decision - focus on architectural changes
- Don't write generic/theoretical content - use real project data
- Don't skip the "Consequences" section (especially negatives)
- Don't forget to update the ADR index

---

## Example ADRs

See existing ADRs for reference:
- `docs/adr/0001-exact-timecode-arithmetic.md` (385 lines)
- `docs/adr/0002-two-phase-consistent-assembly.md` (498 lines)
- `docs/adr/0011-adversarial-workflow-integration.md` (150 lines)

---

## ADR Index Maintenance

Update `docs/adr/README.md`:

```markdown
## Architecture Decision Records

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0001](./0001-exact-timecode-arithmetic.md) | Exact Timecode Arithmetic | Accepted | 2024-09-15 |
| [0013](./0013-gui-electron-integration.md) | GUI Electron Integration | Accepted | 2025-11-01 |
```

---

## Documentation

- **Quick Reference**: `.kit/context/PROCEDURAL-KNOWLEDGE-INDEX.md`
- **Full Guide**: This document
- **ADR Index**: `docs/adr/README.md`
- **Existing ADRs**: `docs/adr/`

---

**Related Workflows**:
- [TASK-COMPLETION-PROTOCOL.md](./TASK-COMPLETION-PROTOCOL.md) - Document completion when creating ADR

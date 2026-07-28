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

5. **Update index**: Add new ADR to `docs/adr/about-adr.md`

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
- Task files: `.kit/tasks/<status-folder>/<TASK-ID>-name.md`
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

- As long as the decision needs, no longer — be thorough, not verbose

---

## Best Practices

### ✅ DO:
- Include real code examples from implementation
- Be honest about trade-offs and limitations
- Cross-reference related ADRs and tasks
- Verify all links and references work
- Update the matching ADR index (see ADR Index Maintenance below)
- Use actual metrics and test results

### ❌ DON'T:
- Don't document every small decision - focus on architectural changes
- Don't write generic/theoretical content - use real project data
- Don't skip the "Consequences" section (especially negatives)
- Don't forget to update the ADR index

---

## Example ADRs

See existing ADRs for reference:
- `.kit/adr/KIT-ADR-0004-adversarial-workflow-integration.md`
- `.kit/adr/KIT-ADR-0012-task-status-linear-alignment.md`
- `.kit/adr/ADR-0008-tiered-manifest-sync.md`

---

## ADR Index Maintenance

Two homes, two indexes (KIT-0067 D5): **kit decisions** live in
`.kit/adr/` and are indexed in `.kit/adr/about-kit-adr.md`; **your
project's decisions** live in `docs/adr/` and are indexed in
`docs/adr/about-adr.md`. Update the index that matches where you
created the ADR, e.g.:

```markdown
## Architecture Decision Records

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0001](./ADR-0001-your-first-decision.md) | Your First Decision | Accepted | YYYY-MM-DD |
```

---

## Documentation

- **Quick Reference**: `CLAUDE.md`
- **Full Guide**: This document
- **ADR Indexes**: `.kit/adr/about-kit-adr.md` (kit) / `docs/adr/about-adr.md` (your project)
- **Existing ADRs**: `.kit/adr/` (kit) / `docs/adr/` (your project)

---

**Related Workflows**:
- [TASK-COMPLETION-PROTOCOL.md](./TASK-COMPLETION-PROTOCOL.md) - Document completion when creating ADR

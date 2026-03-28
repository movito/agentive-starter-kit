# KIT-ADR-0019: Structured Knowledge Capture from Code Reviews

**Status**: Proposed
**Date**: 2024-12-04
**Author**: Planner Agent
**Supersedes**: None
**Related**: KIT-ADR-0014 (Code Review Workflow)

## Context

Code reviews generate valuable insights that could benefit future development, but currently this knowledge is lost or buried:

1. **Reviews contain actionable insights** - Architectural decisions, quality patterns, integration gotchas, and recommendations surface during review but aren't systematically captured.

2. **Raw review files create noise** - Storing full review markdown in `.agent-context/reviews/` preserves history but agents can't efficiently query or learn from dozens of verbose files.

3. **Knowledge doesn't compound** - Each new task starts fresh. An agent working on TASK-0010 doesn't benefit from lessons learned in TASK-0005's review unless a human manually surfaces them.

4. **Context windows are precious** - Agents can't read all past reviews before starting work. We need distilled, queryable knowledge.

### Example of Lost Insight

A review noted "Bridge protocol uses SCHEMA_VERSION 1.0.0 - must maintain for Swift compatibility." This is critical for anyone touching the bridge module, but it's buried in an 84-line review file that future agents won't read.

### Current State

```
.agent-context/reviews/
├── TASK-0004-review-v1-planner.md     # 50+ lines each
├── TASK-0004-review-v2-code-reviewer.md
├── TASK-0004-review-v3-round2.md
├── TASK-0005-review.md
└── ... (grows with every task)
```

Reviews are preserved but not distilled. The planner commits them, moves the task to done, and moves on.

## Decision

**Adopt Hybrid Approach**: Curated insights index (`REVIEW-INSIGHTS.md`) + ADRs for significant architectural decisions.

### Approach Details

#### Component 1: REVIEW-INSIGHTS.md Index

A single file that grows incrementally with high-signal extracts, organized by module and pattern type:

```markdown
# .agent-context/REVIEW-INSIGHTS.md

## Index by Module

### CLI (`src/cli/`)
- **TASK-0005**: Click framework with lazy imports recommended for startup performance
- **TASK-0005**: CLIOutput class pattern for consistent JSON/text output

### Bridge (`src/bridge/`)
- **TASK-0005**: SCHEMA_VERSION must stay 1.0.0 for Swift app compatibility
- **TASK-0005**: Pydantic models required for JSON protocol validation

## Patterns & Anti-Patterns

### Recommended Patterns
- **Config classes**: Dataclass + __post_init__ validation (TASK-0004)
- **CLI output**: CLIOutput helper class for JSON/text modes (TASK-0005)

### Anti-Patterns to Avoid
- **Config**: Don't use Pydantic BaseSettings for simple config (TASK-0004)
- **Reviews**: Don't overwrite existing review files (TASK-0004 bug)

## Integration Notes
- Swift app expects SCHEMA_VERSION 1.0.0 - breaking changes need Swift update
- CLI --json flag output is contract with GUI - test thoroughly
```

#### Component 2: ADRs for Significant Decisions

When reviews surface architectural decisions worthy of formalization:

```markdown
# docs/decisions/adr/ADR-0015-cli-output-pattern.md

## Context
TASK-0005 review identified need for consistent CLI output handling.

## Decision
Use CLIOutput helper class that switches between JSON and text modes.

## Consequences
- All CLI commands must use CLIOutput, not direct print/click.echo
- JSON mode calls sys.exit(1) on error for proper exit codes
```

## Alternatives Considered

### Option A: Curated Insights Index Only
- **Pros**: Single file, easy to read, agents can grep for module names
- **Cons**: Manual curation required, could grow large, no formal decision record
- **Rejected**: Misses opportunity to formalize significant decisions

### Option B: Serena Memory Files
```
.serena/memories/
├── module-cli.md           # CLI-specific learnings
├── module-api.md           # API-specific learnings
├── patterns-config.md      # Configuration patterns
└── integration-swift.md    # Swift app integration notes
```
- **Pros**: Categorized, agents can selectively load via `mcp__serena__read_memory()`
- **Cons**: Requires Serena, more files to maintain, fragmented knowledge
- **Rejected for now**: Can evolve toward this if index grows too large (>500 lines)

### Option C: Lightweight ADRs Only
- **Pros**: Formal, discoverable, follows existing ADR pattern
- **Cons**: Heavyweight for small insights, ADR explosion risk
- **Rejected**: Too much overhead for quick tips and gotchas

## Workflow Integration

Add to planner's task completion workflow (after code review approval):

### Step: Extract Review Knowledge

After moving task to `5-done/`:

1. Read the review file(s)
2. Identify extractable insights:
   - Module-specific patterns or gotchas
   - Integration requirements
   - Recommended/anti-patterns
   - Architectural decisions (consider ADR)
3. Append to `.agent-context/REVIEW-INSIGHTS.md`
4. If architectural decision warrants it, create ADR
5. Commit knowledge artifacts with task completion

### Extraction Prompt Template

```
Review the code review at `.agent-context/reviews/[TASK-ID]-review.md` and extract:

1. **Module insights**: Patterns or gotchas specific to modules touched
2. **Integration notes**: Requirements for other systems (Swift, external APIs)
3. **Patterns**: Reusable approaches that worked well
4. **Anti-patterns**: Approaches to avoid
5. **ADR candidates**: Decisions significant enough to formalize

Format as entries for REVIEW-INSIGHTS.md index.
```

## Implementation

| Component | Effort | Owner |
|-----------|--------|-------|
| Create REVIEW-INSIGHTS.md template | 30 min | Planner |
| Update planner agent with extraction step | 1 hour | Agent maintainer |
| Document workflow in PROCEDURAL-KNOWLEDGE-INDEX | 30 min | Planner |
| Backfill insights from existing reviews | 1 hour | Planner |

**Total**: ~3 hours

## Consequences

### Positive
- Knowledge compounds across tasks
- Agents can quickly load relevant context before starting work
- Significant decisions are formally recorded as ADRs
- Single source of truth for patterns and gotchas
- Low overhead - planner already owns task completion

### Negative
- Manual curation required (could miss insights)
- Index may grow large over time (mitigated by module organization)
- Dual maintenance: insights file + ADRs for significant decisions

### Neutral
- Can evolve toward Serena memories if index exceeds 500 lines
- Extraction quality depends on planner agent's judgment

## Open Questions

1. **Staleness**: How do we handle insights that become outdated as code evolves?
   - *Proposed*: Include task ID with each insight; periodic review during major refactors

2. **Discoverability**: Should agents be prompted to check REVIEW-INSIGHTS.md before starting related work?
   - *Proposed*: Add to task starter template: "Check REVIEW-INSIGHTS.md for [modules touched]"

3. **Automation**: Could a script parse review markdown and suggest extractions?
   - *Deferred*: Start manual, automate if pattern emerges

## References

- KIT-ADR-0014: Code Review Workflow
- `.agent-context/workflows/COMMIT-PROTOCOL.md`
- `.agent-context/PROCEDURAL-KNOWLEDGE-INDEX.md`

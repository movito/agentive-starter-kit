# Documentation Discipline: Reusable Pattern

**Layer:** Foundation
**Topic:** 1.6 Documentation Discipline
**Type:** Template + Checklist

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## When to Use This Pattern

Use these documentation patterns when:
- Making architecture or design decisions that affect future work
- Completing tasks that taught you valuable lessons
- Discovering mistakes or approaches to avoid
- Choosing between multiple valid approaches
- Creating knowledge worth preserving for the team

## The Pattern

### Decision Log Format (ADR - Architecture Decision Record)

```markdown
# ADR-[NUMBER]: [Decision Title]

**Date:** [YYYY-MM-DD]
**Status:** [Proposed / Accepted / Deprecated / Superseded by ADR-XXX]
**Deciders:** [Who made or approved this decision]
**Tags:** [architecture, security, performance, etc.]

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## Context

[What is the issue we're facing? What forces are at play? Include:
- Technical constraints
- Business requirements
- Time/resource limitations
- Previous attempts or related decisions]

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## Decision

[What decision did we make? State clearly in 1-2 sentences, then elaborate if needed.]

We will [chosen approach].

[Optional: More detail about implementation, scope, or boundaries]

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## Rationale

[Why did we choose this over alternatives? What factors were most important?]

**Factors considered:**
- [Factor 1]: [Why this mattered]
- [Factor 2]: [Why this mattered]

**Why this beats alternatives:**
- [Advantage 1]
- [Advantage 2]

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## Consequences

[What becomes easier and what becomes harder as a result of this decision?]

**Positive:**
- [Benefit 1]
- [Benefit 2]

**Negative:**
- [Tradeoff 1]
- [Tradeoff 2]

**Neutral:**
- [Side effect that's neither good nor bad]

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## Alternatives Considered

**Option 1: [Alternative approach]**
- Pros: [What's good about this]
- Cons: [Why we didn't choose this]

**Option 2: [Alternative approach]**
- Pros: [What's good about this]
- Cons: [Why we didn't choose this]

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## References

- [Link to relevant task, PR, or discussion]
- [Link to documentation or research]
```

### Task Completion Summary Template

```markdown
# [TASK-ID]: [Task Name] - Completion Summary

**Completed:** [YYYY-MM-DD]
**Time Spent:** [X hours - actual vs. Y hours estimated]
**Pull Request:** [Link to PR]

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## Summary

[2-3 sentences: What was implemented, why it mattered, what the measurable outcome was.]

**Impact:** [Quantified result - response time, test coverage, bugs fixed, etc.]

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## What Worked Well

[2-3 practices or decisions that contributed to success. Be specific and reusable.]

1. **[Practice/Decision]:** [Why this helped and when to use it again]
2. **[Practice/Decision]:** [Why this helped and when to use it again]

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## What Didn't Work

[1-2 approaches that failed or took longer than expected. Help others avoid the same mistake.]

1. **[Approach that failed]:** [What went wrong and why]
   - Lesson: [What to do instead next time]

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## Key Decisions

[Non-obvious choices that future maintainers might question. Capture the "why".]

- **[Decision]:** [Rationale in 1-2 sentences]
- **[Decision]:** [Rationale in 1-2 sentences]

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## What I'd Change Next Time

[If you repeated this task, what would you do differently? Focus on process, not hindsight.]

- [Improvement 1]
- [Improvement 2]

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## References

- **Task spec:** [Link to original task]
- **Code changes:** [Link to PR or commit range]
- **Related work:** [Links to related tasks or ADRs]
```

### Documentation Update Checklist

**Before marking task complete:**

**Code Documentation:**
- [ ] Public functions have docstrings/JSDoc comments
- [ ] Complex logic has inline comments explaining "why" not "what"
- [ ] API endpoints documented (request/response format, error codes)
- [ ] Configuration variables documented (what they control, valid values)

**Project Documentation:**
- [ ] README updated if user-facing changes
- [ ] CHANGELOG updated with version and changes
- [ ] API docs regenerated if interfaces changed
- [ ] Deployment docs updated if new dependencies or config

**Team Knowledge:**
- [ ] Decision log updated if architectural choice made
- [ ] Task completion summary written if lessons learned
- [ ] Runbook updated if operational procedures changed
- [ ] Onboarding docs updated if project structure changed

**Cleanup:**
- [ ] Remove outdated comments from code
- [ ] Archive or delete obsolete documentation
- [ ] Update links if files were moved or renamed
- [ ] Remove TODO comments that are now done

**Quality Check:**
- [ ] Documentation tested (commands actually work)
- [ ] Links verified (no broken references)
- [ ] Examples still accurate (match current code)
- [ ] Spelling and grammar checked

## Usage Example

**Scenario:** Completed Redis caching task, learned valuable lessons about library limitations.

**Decision Log (ADR):**

```markdown
# ADR-0042: Use Redis with JSON Serialization Workaround

**Date:** 2025-11-14
**Status:** Accepted
**Deciders:** feature-developer agent
**Tags:** architecture, performance, caching

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## Context

Dashboard load time was 5-8 seconds. We needed a caching layer to reduce database queries. Our data includes nested JSON objects (user preferences, dashboard widgets).

Previous attempt with simple Redis caching failed because the `redis-py` library version 4.x has a bug with nested JSON serialization (GitHub issue #2847).

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## Decision

We will use Redis with manual JSON serialization via Python's `json` library, storing serialized strings and deserializing on retrieval.

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## Rationale

**Factors considered:**
- Performance: Must achieve <2s load time
- Persistence: Need cache to survive restarts
- Complexity: Team has Redis experience

**Why this beats alternatives:**
- Avoids library bug without downgrading
- Maintains type safety through validation after deserialization
- Acceptable 5ms serialization overhead

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## Consequences

**Positive:**
- Achieved <2s load time (from 5-8s)
- Cache survives deployments
- No dependency version downgrades

**Negative:**
- Manual serialization adds 5ms per cache operation
- Must validate deserialized data structure
- Can't use Redis JSON module features

**Neutral:**
- Serialization logic centralized in cache client class

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## Alternatives Considered

**Option 1: Downgrade redis-py to 3.x**
- Pros: No serialization bug, use built-in serialization
- Cons: Loses security fixes, blocks future upgrades, deprecated version

**Option 2: Switch to Memcached**
- Pros: No serialization issues, simpler
- Cons: Loses persistence, requires infrastructure change, team unfamiliar

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## References

- TASK-2025-0087 (dashboard optimization)
- redis-py issue #2847: https://github.com/redis/redis-py/issues/2847
```

**Task Completion Summary:**

```markdown
# TASK-2025-0087: Dashboard Caching - Completion Summary

**Completed:** 2025-11-14
**Time Spent:** 6 hours actual vs. 4 hours estimated
**Pull Request:** #234

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## Summary

Implemented Redis caching layer for user dashboard, reducing load time from 5-8 seconds to <2 seconds. Cache hit rate >75% in production after 24 hours.

**Impact:** Dashboard load time reduced 70% (5s → 1.5s average), user bounce rate decreased 8%

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## What Worked Well

1. **TDD with integration tests:** Caught JSON serialization bug in development before production
2. **5-minute cache TTL:** Balances freshness with hit rate - could be tuned based on monitoring

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## What Didn't Work

1. **Assumed redis-py handled nested JSON:** Library bug forced manual serialization workaround
   - Lesson: Test library features with realistic data early, don't assume from docs

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## Key Decisions

- **Manual JSON serialization:** Work around redis-py bug, adds 5ms but avoids downgrade (see ADR-0042)
- **5-minute TTL:** Based on background job frequency, configurable via CACHE_TTL env var

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## What I'd Change Next Time

- Research library limitations before choosing technology (would have caught JSON bug sooner)
- Add cache warming script from the start (added late, slowed initial deployment)

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## References

- **Task spec:** delegation/tasks/completed/TASK-2025-0087.md
- **Code changes:** PR #234
- **Related work:** ADR-0042 (Redis serialization decision)
```

## Customization Tips

**For different documentation types:**

**Technical decisions (ADR):**
- Use when choice affects architecture or has long-term impact
- Focus on rationale - future you will question the decision
- Update status to Deprecated when superseded

**Lessons learned (Completion Summary):**
- Use when task taught you something non-obvious
- Skip for routine work with no surprises
- Focus on reusable insights, not play-by-play

**Quick notes (Inline comments):**
- Use for code that's confusing or non-obvious
- Explain "why" not "what" (code shows what)
- Delete when code is refactored to be obvious

**For different audiences:**

**Future maintainers:**
- Emphasize decisions and rationale
- Include references to relevant context
- Explain non-obvious tradeoffs

**New team members:**
- Focus on "why we do things this way"
- Link to foundational ADRs
- Explain project-specific terminology

**External users:**
- API documentation with examples
- Clear error messages and troubleshooting
- Version compatibility notes

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

**See also:**
- [Concept: Documentation Discipline](./concept.md)
- [Example: Documentation Discipline](./example.md)
- [1.5 Context Management Basics](../05-context-management-basics/concept.md)

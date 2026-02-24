# Structured AI Collaboration: Reusable Pattern

**Layer:** Foundation
**Topic:** 1.1 Structured AI Collaboration
**Type:** Template

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

Use this task specification template when:
- Assigning work to an AI agent with clear deliverables
- Starting a new feature that requires precise requirements
- Converting a vague request into actionable implementation steps
- Creating work that will be resumed across multiple sessions
- Documenting work that needs external review or evaluation

## The Pattern

```markdown
# [TASK-ID]: [Brief title describing what will be done]

**Type:** [Feature/Bug Fix/Refactor/Documentation/Infrastructure]
**Priority:** [High/Medium/Low]
**Estimated Effort:** [X hours]
**Assigned To:** [Agent name or developer name]

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

## Problem Statement

[Describe the current state and why it's insufficient. Include specific measurements where possible. Answer: What's broken or missing? Why does it matter?]

**Current state:** [What exists now or what's not working]

**Desired state:** [What should exist or how it should work]

**Impact:** [Who is affected and how? Business value or technical debt if not addressed]

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

## Success Criteria

[List 3-7 objective conditions that define task completion. Each criterion must be measurable or verifiable. Use checkboxes.]

- [ ] [Criterion 1 - specific, testable condition]
- [ ] [Criterion 2 - include measurements where possible]
- [ ] [Criterion 3 - avoid subjective language like "good" or "fast"]
- [ ] [Criterion 4 - prefer "X achieves Y measured by Z" format]

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

## Constraints

[Specify what the implementation must NOT do. This prevents scope creep and guides decision-making.]

- [Constraint 1 - e.g., "Do not modify database schema"]
- [Constraint 2 - e.g., "Maintain backward compatibility with API v2"]
- [Constraint 3 - e.g., "Stay within existing dependencies - no new npm packages"]

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

[Provide background that clarifies the task. Include relevant links, previous attempts, related tasks, or architectural decisions. Keep this under 150 words.]

**Background:** [Why are we doing this now? What led to this task?]

**Related work:** [Links to related tasks, PRs, or documentation]

**Technical context:** [Architecture details, technology choices, or design constraints]

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

## Acceptance Tests

[Describe how you'll verify this works. Be specific about test scenarios and pass criteria.]

1. [Test scenario 1 - specific inputs and expected outputs]
2. [Test scenario 2 - edge cases or error conditions]
3. [Test scenario 3 - integration or performance tests if applicable]

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

**Created:** [YYYY-MM-DD]
**Updated:** [YYYY-MM-DD]
```

## Usage Example

**Scenario:** You need to reduce dashboard load time from 5 seconds to under 2 seconds.

```markdown
# TASK-2025-0087: Optimize dashboard load time with Redis caching

**Type:** Performance
**Priority:** High
**Estimated Effort:** 4-6 hours
**Assigned To:** feature-developer

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

## Problem Statement

The user dashboard takes 5-8 seconds to load, causing user frustration and increased bounce rates. This occurs because each dashboard load requires 12 separate database queries with no caching layer.

**Current state:** Dashboard loads in 5-8 seconds (measured by Lighthouse)

**Desired state:** Dashboard loads in <2 seconds for cached data, <3 seconds for fresh data

**Impact:** 500+ daily users experience slow dashboards. Analytics show 15% bounce rate on slow loads. This directly impacts user retention.

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

## Success Criteria

- [ ] Dashboard cold load completes in <3 seconds (measured by Lighthouse)
- [ ] Dashboard warm load (cached) completes in <2 seconds
- [ ] Redis cache invalidates correctly when user data changes (verified by tests)
- [ ] Cache hit rate >70% after 24 hours in production (monitored)
- [ ] Test coverage ≥80% for caching logic

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

## Constraints

- Do not modify database schema
- Maintain existing API contracts - frontend should require no changes
- Use existing Redis instance - no new infrastructure
- Cache TTL must be configurable via environment variable

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

**Background:** User research identified slow dashboards as top complaint. Previous attempt to optimize queries reduced time to 5s but hit database limitations.

**Related work:** TASK-2025-0072 (initial query optimization)

**Technical context:** Express backend, PostgreSQL database, Redis available at REDIS_URL

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

## Acceptance Tests

1. Load dashboard after cache clear - completes in <3 seconds
2. Load dashboard with warm cache - completes in <2 seconds
3. Update user profile - dashboard reflects changes immediately (cache invalidated)
4. Set cache TTL to 60s - verify expiration after 60 seconds

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

**Created:** 2025-11-14
```

## Customization Tips

**For different task types:**
- **Bug fixes:** Emphasize current broken behavior, expected correct behavior, and regression tests
- **Refactoring:** Focus on constraints (no behavior changes) and success criteria (test pass rate maintained)
- **Documentation:** Define target audience, success criteria for completeness, and review process

**For different team sizes:**
- **Solo developer:** Context section can be briefer - you have the background knowledge
- **Team work:** Expand context with links to relevant discussions, previous decisions, onboarding material
- **Agent delegation:** Make all sections more explicit - agents need everything spelled out

**Adjust detail level based on:**
- Task complexity (simple tasks need lighter specifications)
- Familiarity (well-known patterns need less explanation)
- Risk (critical paths demand more precision than experiments)

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
- [Concept: Structured AI Collaboration](./concept.md)
- [Example: Structured AI Collaboration](./example.md)
- [1.2 Discrete Task Decomposition](../02-discrete-task-decomposition/concept.md)

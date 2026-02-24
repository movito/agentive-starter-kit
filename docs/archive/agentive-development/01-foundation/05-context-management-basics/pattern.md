# Context Management Basics: Reusable Pattern

**Layer:** Foundation
**Topic:** 1.5 Context Management Basics
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

Use this session handoff template when:
- Ending a work session with incomplete work
- Context-switching to urgent tasks
- Handing off work to another developer or agent
- Taking a break during multi-day feature development
- Documenting work-in-progress for standup meetings

## The Pattern

### Session Handoff Template

```markdown
# [TASK-ID]: [Task Name] - Session Handoff

**Last Updated:** [YYYY-MM-DD HH:MM]
**Status:** [In Progress / Blocked / Ready for Review]
**Estimated Completion:** [X hours remaining]

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

## Current State

[2-3 sentences describing what's been completed. Be specific with file paths and measurements.]

**Completed:**
- [File path]: [What was implemented - one line each]
- [Component/module]: [Status of implementation]

**Tests:** [X of Y tests passing / Test coverage: X%]

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

## Decisions Made

[List key decisions that aren't obvious from code. Capture the "why" behind choices.]

1. **[Decision topic]:** [What was decided and why]
   - Rationale: [Brief explanation]
   - Alternatives considered: [What you didn't choose and why]

2. **[Decision topic]:** [What was decided and why]

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

## Blockers

[List anything preventing progress. Include enough detail to unblock.]

- **[Blocker 1]:** [Description]
  - Impact: [What this blocks]
  - Potential solutions: [Ideas for resolution]

- **[Blocker 2]:** [Description]

[If no blockers: "None - work can continue immediately"]

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

## Next Steps

[Ordered list of 3-5 specific, actionable next steps. Each should be completable in <1 hour.]

1. [Action] - [Expected outcome]
2. [Action] - [Expected outcome]
3. [Action] - [Expected outcome]

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

## Context Notes

[Information you'll forget by tomorrow. Commands, URLs, error messages, workarounds.]

**Useful references:**
- [Link to relevant documentation]
- [Stack Overflow answer that helped]: [URL]

**Commands:**
```bash
[Command that took time to figure out]
```

**Known issues:**
- [Workaround or temporary fix in place]

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

**Resume by:** [Reading this doc, then starting with Next Steps #1]
```

## Usage Example

**Scenario:** Halfway through implementing dashboard caching, need to context-switch to production bug.

```markdown
# TASK-2025-0087: Dashboard Caching - Session Handoff

**Last Updated:** 2025-11-14 16:30
**Status:** In Progress
**Estimated Completion:** 3 hours remaining

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

## Current State

Implemented Redis connection pooling and basic cache layer for user dashboard queries. Cache hit/miss logging is working. Need to add cache invalidation logic and integration tests.

**Completed:**
- src/cache/redis_client.py: Connection pool, get/set methods (75 lines)
- src/api/dashboard.py: Wrapped 3 endpoints with caching (lines 45-120)
- tests/test_cache.py: Unit tests for cache client (8 tests, all passing)

**Tests:** 8 of 8 tests passing / Coverage: 65% (need integration tests)

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

## Decisions Made

1. **Redis over Memcached:** Chose Redis for persistence during restarts
   - Rationale: Dashboard loads immediately after deploy without cache warming
   - Alternatives considered: Memcached (simpler but loses cache on restart)

2. **5-minute TTL:** Set cache expiration to 300 seconds
   - Rationale: Data updates every 2-3 minutes in background job
   - Could adjust based on production monitoring

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

## Blockers

None - work can continue immediately

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

## Next Steps

1. Implement cache invalidation on user profile updates - add Redis DEL call in user.update()
2. Write integration test for cache invalidation - verify profile change clears cached dashboard
3. Add cache warming script for deployment - preload common queries
4. Update environment variables documentation - add REDIS_URL and CACHE_TTL
5. Performance test with production-like data - verify <2s load time goal

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

## Context Notes

**Useful references:**
- Redis Python client docs: https://redis-py.readthedocs.io/en/stable/
- Our Redis instance details in deployment/README.md (line 45)

**Commands:**
```bash
# Local Redis for testing
docker run -p 6379:6379 redis:7-alpine

# Monitor cache hit rate
redis-cli info stats | grep keyspace_hits
```

**Known issues:**
- Cache key naming could be more consistent (using mix of user_id and username)
- Need to discuss cache key format with team before finalizing

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

**Resume by:** Start Redis Docker container, then implement cache invalidation (Next Steps #1)
```

## Customization Tips

**For different handoff types:**

**Solo developer (end of day):**
- Focus on Next Steps and Context Notes
- Decisions section can be briefer - you remember context
- Emphasize what you'll forget overnight

**Team handoff (to another developer):**
- Expand Decisions section - they need full rationale
- Add more Context Notes - less shared knowledge
- Include links to relevant previous work or docs

**Agent handoff (Claude Code session):**
- Make everything explicit - no assumptions
- Include exact file paths and line numbers
- Spell out commands and expected outputs

**For different task types:**

**Feature development:**
- Emphasize Next Steps (forward progress)
- Track completion percentage
- Note where to add tests

**Bug investigation:**
- Focus on Current State (what's been ruled out)
- Document reproduction steps in Context Notes
- List hypotheses in Next Steps

**Refactoring:**
- Track which modules/files are done vs. remaining
- Note test pass rate to ensure no regressions
- Document why refactor is needed in Decisions

**Adjust detail based on:**
- **Same-day resumption:** Lighter context, focus on Next Steps
- **Multi-day gap:** More thorough, assume you'll forget details
- **Uncertain work:** Capture more decisions and alternatives
- **Routine work:** Minimal documentation, rely on code

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
- [Concept: Context Management Basics](./concept.md)
- [Example: Context Management Basics](./example.md)
- [1.6 Documentation Discipline](../06-documentation-discipline/concept.md)

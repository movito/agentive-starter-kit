# Documentation Discipline: Practice Exercise

**Layer:** Foundation
**Topic:** 1.6 Documentation Discipline
**Estimated Time:** 25-35 minutes
**Difficulty:** Beginner

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

## Objective

You will learn to document completed work with lessons learned, focusing on insights that provide future value. By the end of this exercise, you'll distinguish between documentation that earns its maintenance cost and documentation that becomes stale noise.

## Prerequisites

- Understanding of documentation discipline (read [concept.md](./concept.md))
- A recently completed task (within last week)
- Text editor for creating documentation

## The Exercise

### Scenario

You just finished implementing a caching layer that reduced API response time from 800ms to 120ms. The implementation took 6 hours instead of the estimated 3 hours because you discovered the third-party caching library had a bug with nested JSON serialization. You worked around it by flattening the data structure.

This is worth documenting - but what exactly should you capture, and where should it live?

### Your Task

Create a task completion summary document that preserves useful lessons:

1. **Write a brief summary** - In 2-3 sentences, describe what you implemented and why it mattered. Include the measurable outcome: "Implemented Redis caching for API endpoints. Response time reduced from 800ms to 120ms. Tests confirm cache invalidation works correctly."

2. **Document what worked well** - List 2-3 practices or decisions that contributed to success. Be specific: "TDD caught the serialization bug early in development" not "testing helped". Include techniques you'd reuse.

3. **Document what didn't work** - List 1-2 approaches you tried that failed or took longer than expected. Explain why briefly: "Attempted nested JSON caching - library bug forced data flattening. Workaround added 2 hours." This prevents others from repeating the mistake.

4. **List key decisions and rationale** - Note non-obvious choices future maintainers might question: "Chose Redis over Memcached for persistence during restarts" or "Set 5-minute TTL based on data update frequency analysis". Capture the "why" behind the "what".

5. **Identify what you'd change next time** - If you repeated this task, what would you do differently? "Research library JSON support before choosing caching solution" or "Add integration tests earlier to catch serialization issues".

6. **Link to artifacts** - Reference the pull request, task ID, commit hash, or ADR that contains implementation details. Your summary is a signpost, not the complete history.

### Success Criteria

You've completed this exercise successfully when:

- [ ] Summary quantifies impact with measurements (not vague "improved performance")
- [ ] What worked section contains reusable practices (not just "it worked")
- [ ] What didn't work saves future developers from repeating mistakes
- [ ] Decisions are explained with business/technical rationale
- [ ] Document is under 150 words (concise enough that people will read it)
- [ ] Someone unfamiliar with the task understands the key learnings in 2 minutes

## Alternative: Apply to Your Project

After completing your next task, write a lessons-learned summary before marking it done. Focus on insights that have future value: surprising findings, mistakes that taught you something, decisions that aren't obvious from the code.

Store these summaries where your team looks: decision logs, task descriptions, project wiki, or README sections. Test their value: if you never reference them again, you're documenting the wrong things.

## What You Learned

Documentation discipline means capturing insights when they're fresh, storing them where they'll be found, and ruthlessly deleting what has no future value. The goal isn't comprehensive documentation - it's selective preservation of knowledge that would otherwise be lost.

This practice prevents rediscovering the same problems repeatedly. When documentation answers "why did we choose this?" and "what mistake should I avoid?", it earns its maintenance cost. Everything else is noise.

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

**Next:** [Reflection Questions](./reflection.md)

# Structured AI Collaboration: Reflection Questions

**Layer:** Foundation
**Topic:** 1.1 Structured AI Collaboration
**Estimated Time:** 10-15 minutes

---

## Key Terms

This document uses terms from **agentive development**, a set of techniques, structures, and workarounds that increase the reliability of LLM coding agents, and make their output better. Here are some key terms we use:

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## Purpose

Reflection helps you internalize when structure adds value versus when it creates unnecessary overhead. These questions push you to think critically about trade-offs, context, and your own patterns of collaboration with AI agents.

## Questions to Consider

### 1. When does structure help versus when does it hinder?

Think about your recent work with AI agents. When did explicit specifications save time by preventing misunderstandings or rework? When did structure feel like bureaucracy that slowed you down without adding value? Consider the difference between exploring ideas (where structure might limit creativity) and implementing features (where structure prevents scope creep).

What signals tell you whether to invest time in structured specification or proceed with lighter-weight collaboration?

### 2. How much upfront planning is too much?

You've learned to write task specifications with problem statements, success criteria, and constraints. But you could spend hours refining the specification before writing any code. When does planning transition from risk reduction to procrastination?

What's the minimum viable specification that enables confident implementation? How do you balance clarity with speed?

### 3. What makes a success criterion truly testable?

Compare these criteria: "improve performance" versus "reduce API response time to <100ms measured by pytest-benchmark". The second is testable, but is it always better? When is it worth the precision? When can you accept subjective measures?

Reflect on your practice exercise. Which of your success criteria were genuinely objective? Which required judgment calls? What did you learn about making criteria measurable?

### 4. How do you know when you have enough context?

Task specifications include a context section explaining why work matters. You could write a paragraph or ten pages of background. How do you decide what's essential versus what can be inferred from code, documentation, or git history?

Think about resuming work after a week away. What context did you wish you'd documented? What context was obvious in retrospect?

## Reflection Activity

Choose one of these methods to capture your reflections:

**Decision log:** Create a `decisions.md` file in your project documenting when you'll use structured specifications (always for new features? only for complex work?) and when you'll use lighter approaches (bug fixes? experiments?).

**Journal entry:** Write 3-5 sentences about how structured collaboration changed your most recent AI-assisted work session. What worked? What felt awkward? What would you adjust next time?

**Team discussion:** If you work with others, discuss as a group: what level of structure do we need for different types of work? Can we agree on a lightweight specification template for common tasks?

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

**Next:** [Reusable Pattern](./pattern.md)

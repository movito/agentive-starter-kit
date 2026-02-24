# Context Management Basics: Reflection Questions

**Layer:** Foundation
**Topic:** 1.5 Context Management Basics
**Estimated Time:** 10-15 minutes

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

## Purpose

Reflection helps you distinguish between context that must be preserved and context that can be reconstructed from code and git history. These questions push you to think critically about the trade-offs between thorough documentation and efficient resumption.

## Questions to Consider

### 1. What context is worth documenting versus what can be inferred?

Your handoff document could include every decision, every file touched, every command run - or it could include only non-obvious information that can't be reconstructed. File paths are visible in git history. Code speaks for itself. But the "why" behind a decision often exists only in your head.

Reflect on your practice exercise. What information did you document that was already available elsewhere? What information would have been lost without documentation? How do you recognize the difference between redundant documentation and essential preservation?

### 2. How much detail is too much?

You could write two sentences of context or two pages. Too little and future-you wastes time reconstructing understanding. Too much and the handoff becomes a maintenance burden that's out of date before you finish writing it.

When you returned to your work after 10 minutes, what level of detail served you best? When did brevity help (faster to read, easier to update) and when did thoroughness help (answered all questions, prevented confusion)? What's your personal signal for "enough"?

### 3. When should you update context documentation?

Context can become stale quickly. If you update your handoff after every decision, you spend more time documenting than implementing. If you update once per week, it's useless for daily resumption. If you never update it, the document becomes misleading noise.

How frequently should you refresh context? What triggers an update (major decision? blocker resolved? end of session)? How do you balance currency with overhead? When should you delete outdated context instead of updating it?

### 4. How do you document context for agents versus for humans?

AI agents need explicit information - they can't infer from experience or institutional knowledge. Humans can often reconstruct context from sparse hints. But over-explaining to agents creates verbose documents humans won't read.

Where's the balance? What context do both agents and humans need? What can you assume humans understand but agents require spelled out? How do you write handoffs that serve both audiences without doubling the work?

## Reflection Activity

Choose one of these methods to capture your reflections:

**Context audit:** Review your last three work sessions. What context did you wish you'd documented at resumption? What context did you document but never reference? Create a personal guideline: "Always document X, never document Y, document Z when..."

**Resumption timer:** At the start of your next five sessions, track how long it takes to rebuild context. Note what slowed you down (missing information? outdated docs? too much to read?). After five sessions, identify the pattern and adjust your context management approach.

**Template refinement:** Create a session handoff template based on your practice exercise. Use it for a week. Note what sections you consistently skip or find unhelpful. Revise the template. Repeat until you have a lightweight format that actually serves you.

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

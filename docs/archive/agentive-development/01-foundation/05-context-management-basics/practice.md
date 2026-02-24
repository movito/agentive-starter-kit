# Context Management Basics: Practice Exercise

**Layer:** Foundation
**Topic:** 1.5 Context Management Basics
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

You will practice documenting work-in-progress context so completely that you (or someone else) can resume seamlessly without memory of the previous session. By the end of this exercise, you'll know what context to preserve and what to omit.

## Prerequisites

- Understanding of context management (read [concept.md](./concept.md))
- An active task or feature you're currently implementing
- Text editor for documenting context

## The Exercise

### Scenario

You're halfway through implementing a feature when an urgent production issue requires your immediate attention. You need to context-switch now, and you don't know when you'll return to this work - could be later today, could be next week.

Your goal is to document enough context that future-you (or a teammate) can resume this work without confusion, without re-reading all the code, and without making decisions you've already made.

### Your Task

Create a session handoff document following these steps:

1. **Document current status** - Write 2-3 sentences describing what you've completed so far. Be specific: "Implemented User model with password hashing, wrote 8 passing tests" not "worked on authentication". Include file paths and line numbers for key changes.

2. **List blockers and decisions** - Note anything blocking progress (waiting on API key, dependency upgrade needed). Document key decisions you've made (chose bcrypt over argon2 because of team familiarity). Capture the "why" behind non-obvious choices.

3. **Define next steps** - Write a numbered list of 3-5 specific actions to continue this work. Each step should be concrete enough to start immediately: "Add POST /api/login endpoint" not "finish backend work". Order them by logical sequence.

4. **Capture important context** - Note anything you'll forget by tomorrow: specific error messages you researched, URLs of helpful documentation, commands that took time to figure out, temporary workarounds in place.

5. **Test by walking away** - Close your editor, clear your terminal history, do something else for 10 minutes. Return to your handoff document. Can you resume work immediately? Do you need to re-research anything? If yes, add that information to the document.

6. **Verify resumption** - Actually resume the work using only your handoff document. Did you document enough? Too much? Update the document based on what you learned.

### Success Criteria

You've completed this exercise successfully when:

- [ ] Status section is specific with file paths and measurements
- [ ] Blockers are documented with enough detail to resolve them
- [ ] Next steps are actionable (you could start immediately)
- [ ] You captured non-obvious context (decisions, links, commands)
- [ ] After 10+ minutes away, you resumed work without confusion
- [ ] Document is under 200 words (concise enough to read quickly)

## Alternative: Apply to Your Project

At the end of your next work session, write a handoff document before closing your editor. Tomorrow, start your session by reading only the handoff - don't look at code or git history first.

Did you capture enough context? Too much? Adjust your approach and iterate. Over time, you'll develop intuition for what future-you needs to know versus what code and git history already document.

## What You Learned

Context management is how you preserve decisions and understanding across the discontinuity of sessions, handoffs, and context switches. When you document current state, blockers, and next steps, you eliminate the "what was I doing?" tax that costs 10-30 minutes at every resumption.

This practice scales beyond solo work. Handoffs between agents, between team members, and between work sessions all benefit from the same discipline: make your understanding explicit so it survives the transition.

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

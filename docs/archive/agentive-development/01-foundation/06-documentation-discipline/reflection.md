# Documentation Discipline: Reflection Questions

**Layer:** Foundation
**Topic:** 1.6 Documentation Discipline
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

Reflection helps you distinguish between documentation that earns its maintenance cost and documentation that becomes stale noise. These questions push you to think critically about return on investment, currency, and the courage to delete what no longer serves you.

## Questions to Consider

### 1. What documentation provides ROI versus what becomes busy work?

You could document every function, every decision, every lesson learned. Some documentation saves hours repeatedly (architecture decisions, non-obvious tradeoffs, lessons from failures). Other documentation is written once and never referenced (exhaustive API docs when code is self-documenting, step-by-step guides for one-time tasks).

Reflect on your practice exercise and your recent work. What documentation have you actually used in the last month? What documentation exists but you've never opened? How do you predict in advance what will provide value versus what will rot?

### 2. How do you keep documentation up to date without it becoming a burden?

Code changes constantly. Documentation that's out of date is worse than no documentation - it misleads and erodes trust. You could update docs with every code change (high accuracy, unsustainable overhead) or never update them (low overhead, useless docs).

Where's the pragmatic middle ground? What triggers a documentation update (breaking changes? new features? quarterly review)? How do you balance accuracy with sustainability? What's your strategy for avoiding documentation drift?

### 3. When should you delete outdated documentation?

Deletion feels risky - what if you need that information later? But stale documentation clutters searches, confuses newcomers, and wastes maintenance effort. Sometimes the right answer is: delete it and trust git history if you need it back.

How do you recognize when documentation has outlived its usefulness? What's the difference between temporarily outdated (worth updating) and permanently obsolete (worth deleting)? How do you overcome the instinct to hoard information?

### 4. How do you document for different audiences without duplicating effort?

Onboarding docs for new developers, reference docs for daily use, decision logs for future maintainers, API docs for external users - each audience needs different information. But maintaining four versions of overlapping content is unsustainable.

How do you structure documentation to serve multiple audiences efficiently? What belongs in code comments versus external docs? When is duplication justified versus when does it create maintenance debt? What's your strategy for single-source-of-truth?

## Reflection Activity

Choose one of these methods to capture your reflections:

**Documentation audit:** List all documentation in your project. For each doc, note: last updated, last time you referenced it, estimated future value. Calculate ROI (value / maintenance cost). Delete or archive anything with negative ROI. Document your criteria for future decisions.

**Update tracking:** For one month, track every time you update documentation. Note what triggered the update and how long it took. At month-end, analyze: which docs required constant updates (candidates for deletion or better tooling) versus which stayed current naturally (good ROI)?

**Deletion experiment:** Identify 3-5 docs you suspect are outdated or unused. Move them to an archive folder (don't delete yet). After three months, check if anyone needed them. If not, delete permanently. Document your findings about what's safe to delete.

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

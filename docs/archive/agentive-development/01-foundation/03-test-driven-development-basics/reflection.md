# Test-Driven Development Basics: Reflection Questions

**Layer:** Foundation
**Topic:** 1.3 Test-Driven Development Basics
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

Reflection helps you develop judgment about when TDD provides value and when it creates friction. These questions push you to think critically about test quality, design impact, and the trade-offs inherent in test-first development.

## Questions to Consider

### 1. When is TDD valuable versus when can you skip it?

TDD provides the most value for complex logic, edge cases, and code that must remain correct over time. It provides less value for throwaway prototypes, UI layout tweaking, and exploratory coding where requirements are unclear.

Reflect on your practice exercise. When did writing the test first clarify your thinking? When did it feel like overhead? How do you decide whether to invest in TDD for a given piece of work?

### 2. What makes a test good versus what makes it maintenance burden?

You've written tests that fail when they should and pass when they should. But some tests are brittle - they break when implementation details change even though behavior is correct. Other tests are too broad - they pass even when bugs exist.

What characteristics separate valuable tests (catch real bugs, survive refactoring, document intent) from problematic tests (break on irrelevant changes, miss edge cases, obscure failures)? How do you recognize when you're writing the wrong test?

### 3. How does TDD change your design approach?

When you write tests first, you experience your code as a caller before implementing it. This perspective often reveals awkward APIs, tight coupling, and hidden dependencies. Code designed for testability tends to have clearer boundaries and looser coupling.

Think about your practice exercise. Did writing tests first influence your function signature, error handling, or data structures? Did it make your code more modular? How does the test-first constraint shape design differently than implementation-first?

### 4. What's the right balance between testing thoroughness and development speed?

You could write dozens of tests covering every edge case, or write a few tests for happy paths. More tests catch more bugs but slow development and increase maintenance. Fewer tests ship faster but risk production failures.

Where do you draw the line? How do you identify which edge cases deserve tests versus which are low-probability enough to accept the risk? What signals tell you when you've under-tested versus over-tested?

## Reflection Activity

Choose one of these methods to capture your reflections:

**TDD decision log:** Document when you'll use TDD (new features? bug fixes? refactoring?) and when you won't (prototypes? UI layout?). After a month, review your decisions. Were you right about when TDD added value?

**Test quality checklist:** Create a personal checklist for evaluating your tests. Include criteria like "survives refactoring", "fails with clear message", "tests behavior not implementation". Use this to review your next batch of tests.

**Before/after comparison:** Take a function you wrote without tests. Now write tests for it. Did the tests reveal bugs? Design flaws? What would have been different if you'd written tests first? Document your findings.

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

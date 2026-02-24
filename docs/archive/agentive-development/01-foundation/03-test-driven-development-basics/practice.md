# Test-Driven Development Basics: Practice Exercise

**Layer:** Foundation
**Topic:** 1.3 Test-Driven Development Basics
**Estimated Time:** 40-50 minutes
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

You will experience the RED-GREEN-REFACTOR cycle firsthand by implementing a simple function test-first. By the end of this exercise, you'll understand why writing tests before code prevents bugs, clarifies requirements, and improves design.

## Prerequisites

- Understanding of TDD concepts (read [concept.md](./concept.md))
- Programming environment with a test framework (pytest for Python, Jest for JavaScript, etc.)
- Basic testing knowledge (assertions, test functions)

## The Exercise

### Scenario

You're building a utility function to parse time duration strings like "2h 30m" or "90m" into total minutes. Users can input "1h", "45m", "2h 15m", or just "90" (assumes minutes). Invalid inputs should raise clear errors.

This is perfect for TDD: clear requirements, edge cases to handle, and easy to test without dependencies.

### Your Task

Follow the RED-GREEN-REFACTOR cycle to implement `parse_duration(input_string)`:

1. **RED: Write a failing test** - Start with the simplest case. Write a test for `parse_duration("30m")` expecting `30`. Run the test. It should fail because the function doesn't exist yet. Verify the failure message is clear.

2. **GREEN: Make it pass** - Write the minimum code to make the test pass. Don't handle edge cases yet. Don't make it elegant. Hardcode if needed. Run the test. It should pass now.

3. **REFACTOR: Improve the code** - Now that the test passes, clean up the implementation. Remove duplication. Clarify variable names. Improve structure. Run the test after each change to ensure it still passes.

4. **RED again: Add next test** - Write a test for the next case: `parse_duration("2h")` expecting `120`. This test should fail. Then make it pass. Then refactor if needed.

5. **Continue the cycle** - Add tests and implementation for:
   - Combined hours and minutes: `"1h 30m"` → `90`
   - Minutes only with no suffix: `"45"` → `45`
   - Invalid input: `"abc"` → raises `ValueError`

6. **Run all tests** - After completing all cases, run the full test suite. All tests should pass. If any fail, fix the implementation and rerun.

### Success Criteria

You've completed this exercise successfully when:

- [ ] You have at least 5 tests covering different input cases
- [ ] You wrote each test BEFORE implementing the corresponding functionality
- [ ] All tests pass when you run the test suite
- [ ] You experienced at least one refactoring step that improved code quality
- [ ] Invalid inputs raise exceptions (tested)
- [ ] You can explain why TDD caught edge cases you might have missed

## Alternative: Apply to Your Project

Choose a simple, pure function from your current project that lacks tests - something that takes input, performs a transformation, and returns output. String formatters, calculators, validators, and parsers work well.

Delete the implementation (or copy it to a comment for reference). Now rebuild it test-first using RED-GREEN-REFACTOR. You might discover edge cases the original implementation missed or find a cleaner design through the discipline of testing first.

## What You Learned

TDD isn't about testing - it's about design and confidence. When you write tests first, you clarify requirements before coding, catch edge cases during implementation, and build regression protection automatically. The failing test (RED) proves you're testing the right thing. The passing test (GREEN) confirms it works. Refactoring makes it maintainable.

This practice becomes instinctive. Experienced TDD practitioners feel uncomfortable writing code without a failing test, because they've learned: if you don't test it before you write it, you probably won't test it at all.

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

# Test-Driven Development Basics: Concept

**Layer:** Foundation
**Topic:** 1.3 Test-Driven Development Basics
**Estimated Reading Time:** 3-5 minutes

> **New to agentive development?** This guide teaches a methodology for working with AI assistants as specialized collaborators with defined roles. See the [Introduction to Agentive Development](../../00-introduction.md) for a complete overview. This document assumes basic familiarity with the approach.

---

## Key Terms

This guide uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **RED-GREEN-REFACTOR** - TDD cycle: write failing test, make it pass, improve code
- **Quality gate** - Objective pass/fail criteria before proceeding
- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Agentive development** - Methodology treating AI as specialized collaborators with defined roles

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## What is Test-Driven Development?

**TDD (Test-Driven Development)** is the practice of writing automated tests before implementing functionality. You begin by writing a test that defines expected behavior, watch it fail (proving the test detects the missing feature), implement the minimum code to make the test pass, then refactor while keeping tests green. This cycle—**RED-GREEN-REFACTOR**—transforms testing from validation afterthought into design driver.

TDD inverts the traditional sequence. Instead of "write code, hope it works, test to verify," you follow "define success, prove it's unmet, implement until met, improve quality." The test becomes the specification, the failing state proves the test works, and the passing state proves the implementation works.

In agentive development, TDD provides objective validation that both humans and agents trust. When tests pass, the task is complete. When tests fail, the implementation is insufficient. No ambiguity, no subjective judgment, no endless revision loops.

## Why Does This Matter?

### Problems Solved

- **Untested code ships with unknown bugs** - Without tests, you discover failures in production when users report them
- **Regression bugs reappear after fixes** - Without automated tests, fixes that worked last month break this month
- **Unclear specifications lead to ambiguous implementations** - "Make it work" means different things to different people; tests make success objective
- **Manual testing scales poorly** - You can't manually verify every feature after every change in a growing codebase

### Value Provided

TDD provides a safety net for refactoring. With comprehensive tests, you can improve code structure, rename functions, and optimize algorithms with confidence. If something breaks, tests fail immediately. Without tests, refactoring becomes terrifying because changes might introduce subtle bugs undiscovered for months.

This approach documents intent better than comments. A test verifying "timecode conversion lossless with ±1 frame tolerance" explains requirements more precisely than "// be careful with rounding." Tests stay current because they break when behavior changes.

TDD enables agent delegation with quality gates. When you assign a task with "all tests must pass" as acceptance criteria, completion is objective. The quality gate is automated, not subjective.

## How It Fits in Agentive Development

TDD is the validation mechanism for everything else. Structured tasks specify what to build; TDD verifies it was built correctly. Discrete tasks become completable because tests prove completion. Git branches become mergeable when tests pass.

Later layers depend on TDD even more. External evaluation checks if tests are specified. Specialized agents follow RED-GREEN-REFACTOR cycles. Coordination uses test pass rates to track progress. CI/CD gates merges on test results.

Without TDD, agentive development lacks objective validation. With TDD, every layer builds on verified foundations.

## Key Principles

### 1. Write Failing Test First (RED)

Write a test for functionality that doesn't exist yet. Run it and watch it fail. This proves the test works—if it passed before implementation, the test is broken. The RED phase gives confidence that when the test passes, it's because your implementation works.

**Example:** Write `test_timecode_conversion_lossless()` that verifies round-trip frame → timecode → frame preserves the original value. Run it, see it fail with "function timecode_to_frames() does not exist."

### 2. Implement Minimum to Pass (GREEN)

Write the simplest code that makes the test pass. Don't add untested features. Don't optimize prematurely. Don't handle edge cases the test doesn't verify. This discipline prevents scope creep. You build exactly what the test specifies.

**Example:** Implement `timecode_to_frames()` using `Fraction` arithmetic to ensure lossless conversion. Run tests, see them pass. Done.

### 3. Improve Code Quality (REFACTOR)

Once tests pass, improve the implementation without changing behavior. Extract repeated code into functions. Rename variables for clarity. Simplify complex expressions. Add documentation. The tests protect you—if refactoring breaks something, tests fail immediately. The REFACTOR phase is where "make it work" becomes "make it right."

**Example:** Extract frame rate constants to `frame_rate_standards.py`, add type hints, improve variable names. Run tests after each change to ensure nothing broke.

### 4. Tests Document Intent

When tests have descriptive names and clear assertions, they explain what the code should do better than comments. A test named `test_feature_length_precision_under_2_frames()` documents a requirement. The assertion `assert error <= 2` documents the tolerance. Six months later, anyone reading the test understands the specification without archaeological investigation.

**Example:** Instead of a comment "// be careful with precision," write `test_2_5_hour_movie_zero_cumulative_error()` that verifies the requirement explicitly.

### 5. Fast Feedback Loop

TDD works best with fast tests that run in seconds. Fast tests encourage frequent runs, catching problems immediately. Slow tests get run rarely, delaying feedback until problems are harder to debug. Structure unit tests to run in milliseconds, enabling TDD cycles that complete in seconds.

**Example:** Unit tests for timecode run in <2 seconds on pre-commit. Integration tests run in minutes on pre-push or CI.

## When TDD Is Valuable vs. When to Skip

**Use TDD for:**
- Algorithms with correctness requirements (timecode, financial math)
- Bug fixes (write test reproducing bug, fix until passes)
- Refactoring (tests prove behavior unchanged)
- Public APIs (tests document contracts)
- Long-term maintained code

**Consider skipping for:**
- Exploratory prototypes to delete tomorrow
- Visual UI layouts (hard to test programmatically)
- One-off scripts
- Generated code (test the generator)

The default should be TDD. Skip it when you have a specific reason, not out of habit.

## What's Next

Ready to see TDD in action? Continue to:

1. **[Example: Test-Driven Development](./example.md)** - See how TDD caught an 86-frame timecode error in TASK-2025-0012
2. **[Practice Exercise](./practice.md)** - Practice the RED-GREEN-REFACTOR cycle yourself
3. **[Reflection Questions](./reflection.md)** - Deepen your understanding of when and why to use TDD
4. **[Pattern Template](./pattern.md)** - Get a reusable TDD workflow checklist

**Quick self-check:** Before moving on, can you explain why the RED phase (seeing the test fail first) is important? If not, review principle #1 above.

---

**See also:**
- [Example: Test-Driven Development](./example.md)
- [Practice Exercise](./practice.md)
- [1.2 Discrete Task Decomposition](../02-discrete-task-decomposition/concept.md)
- [1.4 Git Safety Practices](../04-git-safety-practices/concept.md)
- [2.5 Cost Awareness and ROI](../../02-augmentation/05-cost-awareness-and-roi/concept.md)

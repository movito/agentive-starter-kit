# Example F2: API Server Task Decomposition

**Layer:** Foundation
**Topic:** 1.2 Discrete Task Decomposition
**Task:** TASK-0078
**Date:** 2025-11-10
**Impact:** 4-day monolithic task decomposed into 4 independent subtasks, enabled parallel execution, reduced risk

---

## Key Terms

This example uses these terms from **agentive development**:

- **Task** - Discrete unit of work with clear acceptance criteria
- **Subtask** - Component task within a larger task or EPIC
- **Agent** - AI collaborator with a specific role and tool access
- **Parallel execution** - Running independent tasks simultaneously
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Quality gate** - Objective pass/fail criteria before proceeding

---

## Context

In mid-November 2025, we needed to add an HTTP API server to Your Project. The Python CLI tool worked well, but users wanted programmatic access via REST API for automation and integration. This was a substantial feature: HTTP server, routing, OpenAPI documentation, validation, error handling, deployment.

**Initial Estimate:** One monolithic task, 4-5 days of sequential work, assigned to api-developer agent.

**The Problem:**

Large, monolithic tasks create several risks:
- **Long feedback loops** - Wait 4 days to discover if approach was wrong
- **All-or-nothing delivery** - Either everything works or nothing ships
- **Difficult rollback** - Can't easily undo part of implementation
- **Sequential bottleneck** - One agent blocks for 4 days; no parallelization possible
- **Review challenges** - Reviewing 2,000+ lines of code in one PR is error-prone

We'd seen this pattern fail before. Large tasks inevitably discover complexity mid-implementation. Requirements get clarified. Designs get revised. With a 4-day monolithic task, these discoveries come too late to adjust course efficiently.

---

## The Challenge

**Decomposition isn't just splitting work randomly.** Bad decomposition creates dependencies, shared state, and merge conflicts that eliminate any benefits.

**Requirements for good decomposition:**
- Each subtask must be **independently testable** (no "Task B can't be tested until Task A done")
- Each subtask must be **completable in 4-8 hours** (single session, no multi-day context loss)
- Subtasks must minimize **shared files** (avoid merge conflicts when working in parallel)
- Each subtask must have **clear acceptance criteria** (objective "done")
- Dependencies must be **explicit and minimal** (prefer independence over sequencing)

**The Wrong Approach:**

Splitting by layer:
- Task 1: Database layer
- Task 2: Business logic
- Task 3: API routes
- Task 4: Tests

This creates **serial dependencies** (can't write routes without business logic, can't write business logic without database). No parallelization. Still a 4-day sequential slog.

---

## Our Approach

### Step 1: Identify Natural Boundaries

We analyzed the API server feature to find natural fault lines - pieces that could exist independently:

**Foundation** (server infrastructure):
- HTTP server startup/shutdown
- Middleware (CORS, logging, error handling)
- Health/metrics endpoints
- Configuration management
- OpenAPI spec generation

**Validation** (input/output contracts):
- Request body validation
- Response serialization
- Error response formatting
- API versioning

**Testing** (verification infrastructure):
- Test utilities (fixtures, helpers)
- Integration test framework
- Performance benchmarks
- Contract validation

**Decorator Safety** (code quality):
- Fix existing decorator issues
- Ensure type safety
- Refactor for maintainability

**Key Insight:** These boundaries minimize shared files. Foundation touches `server.py`, Validation touches `validation.py` and `models.py`, Testing touches `tests/api/`, Decorator Safety touches `shared/decorators.py`. Minimal overlap = minimal merge conflicts.

### Step 2: Define Clear Acceptance Criteria

Each subtask got objective completion criteria (not subjective "looks good"):

**TASK-0078-A (Foundation):**
- [ ] Server starts on configurable port
- [ ] Health endpoint responds with 200
- [ ] OpenAPI spec generated at /api/docs
- [ ] 10+ server tests passing
- [ ] Deployment configs for 3 environments

**TASK-0078-B (Validation):**
- [ ] Request validation uses Pydantic models
- [ ] Error responses follow RFC 7807 standard
- [ ] 15+ validation tests passing
- [ ] API versioning works (v1/ prefix)

**TASK-0078-C (Testing):**
- [ ] Test fixtures cover all API endpoints
- [ ] Integration tests run in <5 seconds
- [ ] Performance benchmarks established
- [ ] 20+ integration tests passing

**TASK-0078-D (Decorator Safety):**
- [ ] Type hints pass mypy strict mode
- [ ] Decorator composition works correctly
- [ ] 8+ decorator tests passing
- [ ] Zero regressions in existing code

**Why this works:** "10+ tests passing" is objective. "Health endpoint responds with 200" is verifiable. No ambiguity about "done."

### Step 3: Estimate and Assign

| Task | Estimated Time | Agent | Dependencies |
|------|----------------|-------|--------------|
| TASK-0078-A | 8 hours | api-developer | None |
| TASK-0078-B | 6 hours | api-developer | Depends on A (needs server running) |
| TASK-0078-C | 8 hours | powertest-runner | Depends on A+B (needs endpoints) |
| TASK-0078-D | 4 hours | api-developer | None (independent) |

**Total estimated:** 26 hours (3.25 days)

**Execution options:**
- **Sequential:** 3.25 days
- **Parallel (A+D together, then B, then C):** 2 days
- **Mixed (A, then B+D parallel, then C):** 2.5 days

We chose parallel where possible: Start with A+D simultaneously (both independent), then B, then C.

### Step 4: Create Task Specifications

Each subtask got full task specification:
- Context and motivation
- Detailed requirements
- Code examples
- Testing requirements
- Acceptance checklist

**File structure:**
```
delegation/tasks/active/
  TASK-0078-A-api-server-foundation.md (828 lines)
  TASK-0078-B-api-validation-error-handling.md (612 lines)
  TASK-0078-C-api-testing-validation.md (547 lines)
  TASK-0078-D-api-decorator-fix.md (423 lines)
```

Total: 2,410 lines of specification across 4 subtasks.

---

## The Implementation

**Phase 1: Foundation + Decorator Safety (Parallel)**

```bash
# Day 1, Morning: Start both tasks in parallel
# api-developer working on TASK-0078-A (Foundation)
# api-developer working on TASK-0078-D (Decorator Safety) in separate branch

# Results (Day 1, End):
# - A: 70% complete (server runs, health endpoint works)
# - D: 100% complete (decorator fixes done, tests passing)
```

**Phase 2: Complete Foundation**

```bash
# Day 2, Morning:
# - Finish TASK-0078-A
# - OpenAPI docs generated
# - Deployment configs added
# - All 10 server tests passing

# Result: Foundation COMPLETE ✅
```

**Phase 3: Validation**

```bash
# Day 2, Afternoon:
# - Start TASK-0078-B
# - Build on Foundation (server already running)
# - Add request validation
# - Add error handling

# Result (Day 3, Morning): Validation COMPLETE ✅
```

**Phase 4: Testing**

```bash
# Day 3, Afternoon:
# - powertest-runner starts TASK-0078-C
# - Create integration test suite
# - All endpoints functional (thanks to A+B complete)
# - Performance benchmarks established

# Result (Day 4): Testing COMPLETE ✅
```

**Actual time:** 3 days (vs 4-5 estimated for monolithic approach)

---

## Results

**Metrics:**
- **Original estimate (monolithic):** 4-5 days sequential
- **Actual time (decomposed):** 3 days with partial parallelization
- **Time saved:** 25-40% faster
- **Parallelization:** 2 subtasks ran simultaneously (A+D)
- **Rollback incidents:** 0 (each subtask independently mergeable)

**Source:** Task completion summaries in `delegation/tasks/completed/TASK-0078-*.md`

**Quality Benefits:**
- Each subtask reviewed independently (smaller PRs, better reviews)
- Clear test coverage per subtask (no "we'll test it later")
- Easy rollback if needed (merge A+D, discover issue in B, only B needs rework)
- Objective completion (acceptance criteria met = done)

**Risk Reduction:**
- Early feedback (Foundation done Day 1, validated approach before investing more)
- Incremental progress (something working after each subtask)
- Parallel work (D completed while A was 70% done)

---

## Reflection

**What Worked:**

**Natural boundaries prevented merge conflicts.** Foundation touched `server.py`, Validation touched `validation.py`, Testing touched `tests/api/`, Decorators touched `decorators.py`. Four agents could work on four branches with minimal conflicts.

**Objective acceptance criteria eliminated ambiguity.** "10+ server tests passing" is verifiable. "Health endpoint responds with 200" is objective. No debates about "is it done?"

**Parallel execution saved real time.** A+D running simultaneously saved 4 hours. This only worked because D had zero dependencies on A.

**What Didn't Work:**

**Sequential dependencies in B→C created bottleneck.** Testing (C) couldn't start until Validation (B) finished because tests needed functional endpoints. This was unavoidable given the nature of testing, but it prevented full parallelization.

**Estimation was still conservative.** We estimated 26 hours (3.25 days), finished in 3 days. Decomposition enabled better time tracking per subtask, revealing that some estimates were padded.

**Key Insight:**

Good decomposition amplifies success and contains failure. When Task A succeeds, merge it immediately. When Task B fails, only B needs rework - A and D remain merged. Monolithic tasks have no partial wins: either everything works or nothing ships.

---

## Learnings

- **Learning 1: Decompose by files, not by layers** - "Database layer + Business logic layer + API layer" creates dependencies; "Server module + Validation module + Testing module" enables independence
- **Learning 2: 4-8 hours per subtask is the sweet spot** - Single session completion, no context loss, reviewable in one sitting
- **Learning 3: Dependencies are expensive** - Each dependency adds 1 day of latency (sequential execution); minimize them aggressively

---

## Adaptation Guide

**This pattern applies when:**
- Task estimated at >2 days (large enough to benefit from decomposition)
- Work can be split into independently testable pieces
- Multiple files/modules are involved (natural boundaries exist)
- Risk is high (large change, uncertain approach)
- Parallel execution would provide value

**Adapt for your context:**
- **Core principle stays same:** Find natural boundaries, minimize dependencies, create objective acceptance criteria
- **Decomposition strategy varies:** By file/module (backend), by component (frontend), by endpoint (API), by feature (product work)
- **Subtask size adjusts:** 4-8 hours for programming work, 1-3 hours for documentation, 8-12 hours for research
- **Dependencies map to domain:** Backend often has layers (database→logic→API), frontend often has independence (components are isolated)

**When NOT to use:**
- Small tasks (<2 days) - decomposition overhead exceeds benefits
- Tightly coupled work - every subtask depends on all others (no parallelization gain)
- Exploration/research - don't know enough to decompose meaningfully; do spike first, then decompose

---

**See also:**
- [Concept: Discrete Task Decomposition](./concept.md)
- [Practice Exercise](./practice.md)
- [Pattern: Parallel Task Execution](./pattern.md)

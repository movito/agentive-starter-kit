# Example F6: ADR Prevents Status Label Chaos

**Layer:** Foundation
**Topic:** 1.6 Documentation Discipline
**Task:** ADR-0038 (Task Status Label Alignment)
**Date:** 2025-11-14
**Impact:** 20-minute documentation investment prevents 2-4 hours of recurring confusion, 18x ROI

---

## Key Terms

This example uses these terms from **agentive development**:

- **ADR (Architecture Decision Record)** - Document capturing key design decisions with context and rationale
- **Status label** - Indicator of task state (draft, active, in_progress, completed, etc.)
- **Documentation discipline** - Practice of writing the right amount of documentation at the right time
- **ROI (Return on Investment)** - Time/value gained divided by time/cost invested
- **Quality gate** - Objective pass/fail criteria before proceeding
- **Template** - Reusable document structure with placeholders

---

## Context

On November 14, 2025, we discovered a status label mismatch in TASK-2025-0093. The task file showed status `draft`, the file location was `delegation/tasks/active/` (implying active work), Linear displayed "Backlog" (mapped from `draft`), but the actual state was "completed and tested."

**The Discovery:**

Surveying our 30 active tasks revealed chaos: **12+ different status values** were in use:
- `READY`, `BLOCKED`, `SCHEDULED`, `RESEARCH`, `PLANNED`, `PENDING`
- `ready`, `in_progress`, `completed`, `blocked`, `draft`, `planning`
- Non-standard: `🆕 READY TO START`, `✅ ACTIVE`, `RESEARCH`

**The Problem:**

Our task management system used markdown files synced to Linear for visual tracking. This required maintaining two label systems:
- **Internal labels:** `draft`, `in_progress`, `review`, `completed`
- **Linear labels:** `Backlog`, `In Progress`, `In Review`, `Done`

The sync script mapped between them (30 lines of dictionary lookups), but mapping was incomplete, inconsistent, and confusing. When labels didn't match expectations, we didn't know if it was user error, sync error, or intentional.

**Why This Mattered:**

This wasn't just aesthetic - it caused real workflow problems:
- Agents confused about task status ("Is this ready to start or not?")
- Sync errors led to tasks disappearing from Linear or showing wrong state
- Team members had to mentally translate labels ("What does `draft` mean again?")
- No enforcement - anyone could invent new status values

---

## The Challenge

**The Temptation:**

Just fix it quickly. Update TASK-2025-0093, maybe send a Slack message saying "use these labels going forward," move on.

**Why That Fails:**

1. **Decision gets lost** - Six weeks later, someone asks "Why do we use `In Progress` instead of `in_progress`?" No one remembers.
2. **Alternatives not considered** - Maybe there's a better approach? Haven't thought it through.
3. **Trade-offs unclear** - What are we giving up? What are we gaining?
4. **Context evaporates** - Why was this a problem? What incident triggered the change?
5. **Duplicate decisions** - New team member proposes lowercase labels again, we re-debate

**The Documentation Question:**

Should we document this decision? It's "just status labels" - seems trivial. Won't documentation take longer than fixing the problem?

**Answer:** Yes, document it. Here's why.

---

## Our Approach

### Step 1: Create Architecture Decision Record (ADR)

**Decision:** Don't just fix the labels. Write ADR-0038 to document the decision, rationale, alternatives, and consequences.

**ADR Structure** (following standard ADR template):

```markdown
# ADR-0038: Task Status Label Alignment with Linear

## Context
[What situation led to this decision?]

## Decision
[What are we doing?]

## Consequences
[What are the results - positive, negative, neutral?]

## Alternatives Considered
[What else did we consider? Why rejected?]
```

**Time Investment:** 20 minutes to write

**Contents:**
- Problem statement with example incident (TASK-2025-0093)
- Forces at play (requirements, constraints, assumptions)
- Decision: Adopt Linear's workflow states directly
- 4 alternatives considered and rejected with rationale
- Consequences (7 positive, 5 negative, 4 neutral)
- Implementation strategy
- Post-migration metrics (to be filled)

**Key Sections:**

**Context** (lines 9-53): Explains the problem, not just the solution.
```markdown
**Example incident** (TASK-2025-0093):
- Task file status: `draft`
- File location: `delegation/tasks/active/` (implies active work)
- Linear display: "Backlog" (mapped from `draft`)
- Actual state: Completed and tested
```

**Alternatives Considered** (lines 167-212): Shows what we rejected and why.
```markdown
### Alternative 1: Keep Internal Labels, Improve Mapping
**Rejected because**:
- ❌ Doesn't solve fundamental problem of dual-system confusion
- ❌ Still requires mental mapping between systems
```

### Step 2: Link to Related Work

ADR-0038 cross-references:
- **Incident report:** TASK-2025-0093 (the discovery that triggered this)
- **Implementation task:** TASK-2025-0094 (how we'll execute the change)
- **Affected docs:** Task templates, Linear setup guide, agent prompts
- **Sync script:** `scripts/sync_tasks_to_linear.py` (code that implements this)

**Why links matter:** Future readers need full context, not just the decision.

### Step 3: Track Results

ADR-0038 includes "Real-World Results" section (lines 213-235):

**Before metrics:**
- Distinct status values: 12+
- Sync errors: 1 confirmed (likely more unreported)
- User confusion: High

**After metrics** (to be filled):
- Distinct status values: _[TBD]_
- Sync errors: _[TBD]_
- User confusion: _[TBD]_

**Why track metrics:** Validates that documented decision actually solved the problem.

### Step 4: Make It Findable

**File location:** `docs/decisions/adr/ADR-0038-task-status-linear-alignment.md`

**Naming convention:** `ADR-{number}-{brief-description}.md`

**ADR index:** Listed in `docs/decisions/adr/README.md` with one-line summary

---

## The Implementation

**ADR-0038 Structure** (263 lines):

```markdown
# ADR-0038: Task Status Label Alignment with Linear

**Status**: Accepted
**Date**: 2025-11-14
**Deciders**: tycho (coordinator), [Project Lead] (user)

## Context
[53 lines explaining the problem, incident, and status chaos]

## Decision
[76 lines detailing the solution, implementation, and migration]

## Consequences
[42 lines covering positive, negative, and neutral impacts]

## Alternatives Considered
[46 lines documenting 4 rejected approaches with rationale]

## Real-World Results
[23 lines with before/after metrics]

## Related Decisions
[7 lines linking to connected ADRs and tasks]

## References
[9 lines citing sources and implementation details]
```

**What We Documented:**

1. **The incident that triggered this** - TASK-2025-0093 status mismatch
2. **Why it matters** - Confusion, sync errors, cognitive load
3. **What we decided** - Adopt Linear's labels directly
4. **Why not other approaches** - 4 alternatives rejected with reasoning
5. **What we're trading off** - 7 benefits, 5 costs
6. **How to implement** - Migration strategy with 5 steps
7. **How to measure success** - Before/after metrics
8. **Where to learn more** - Links to related docs

---

## Results

**Time Investment:**
- **Writing ADR-0038:** 20 minutes
- **Creating implementation task (TASK-2025-0094):** 15 minutes
- **Total:** 35 minutes documentation

**Time Saved:**

*Prevented future re-debates:* When someone proposes lowercase labels in 3 months:
- **Without ADR:** 1-hour meeting to re-discuss, research past Slack messages, debate alternatives, reach same conclusion
- **With ADR:** "Read ADR-0038, we already decided this and documented why"
- **Saved:** 55 minutes per occurrence × estimated 3 occurrences = 2.75 hours

*Prevented sync errors:* Clear label standards prevent mismatches:
- **Without ADR:** Sync issues occur monthly, each taking 30 minutes to debug
- **With ADR:** Standards prevent issues
- **Saved:** 30 minutes × 12 months = 6 hours per year

*Enabled smooth onboarding:* New team members read ADR:
- **Without ADR:** Ask questions, get inconsistent answers, learn through trial and error
- **With ADR:** Read ADR-0038, understand rationale, use labels correctly immediately
- **Saved:** 30 minutes onboarding per new person

**ROI Calculation:**

Total saved: 2.75 hours (re-debates) + 0.5 hours (first-year sync errors) + 0.5 hours (onboarding)
= **3.75 hours saved** from 35-minute investment
= **6.4x ROI in first year**

---

## Reflection

**What Worked:**

**Documented the "why," not just the "what."** The ADR explains why we had the problem, why alternatives were rejected, what we're trading off. Six months from now, these answers save time.

**Captured alternatives with rationale.** "Why not just improve the mapping?" - because it doesn't solve the root problem. "Why not use fully custom workflow?" - because it adds complexity. These Q&A pairs prevent re-litigating decided issues.

**Tracked metrics for validation.** ADR-0038 includes before/after metrics (to be filled post-migration). This lets us verify the decision actually worked.

**What Didn't Work:**

**ADR was written reactively, not proactively.** We wrote ADR-0038 *after* discovering the chaos. If we'd documented task status decisions when we first implemented the sync script (months earlier), we could have prevented the chaos entirely.

**Metrics section not filled yet.** ADR-0038 has placeholders for post-migration metrics. These should be filled immediately after TASK-2025-0094 completes, while context is fresh.

**Key Insight:**

Documentation ROI isn't about writing comprehensive docs for everything. It's about identifying **decision points** - moments where multiple people will ask "why did we do it this way?" - and capturing the answer once. ADRs are cheap insurance: 20-30 minutes now saves hours of future confusion.

---

## Learnings

- **Learning 1: Document decisions, not facts** - Don't document "status values are A, B, C" (code shows this); document "why A/B/C instead of X/Y/Z"
- **Learning 2: Alternatives considered are the high-value content** - Explaining what you rejected and why prevents re-proposing the same alternatives
- **Learning 3: 20-minute ADRs have 6-10x ROI** - Even brief decision records pay for themselves quickly through prevented re-debates

---

## Adaptation Guide

**This pattern applies when:**
- Making decisions that will be questioned later ("Why this approach?")
- Multiple valid alternatives exist (not obvious "right answer")
- Decision affects multiple people/teams/systems
- Context will be lost (decision-maker leaving, 6+ month gap)
- Cost of re-debate exceeds cost of documenting (most architectural decisions)

**Adapt for your context:**
- **Core structure stays same:** Context, Decision, Consequences, Alternatives
- **Detail level adjusts:** 200 words for tactical decisions, 2000 words for strategic ones
- **Format varies:** Markdown ADRs (our choice), RFC docs (formal orgs), decision log entries (lightweight), wiki pages (collaborative)
- **Granularity differs:** Every API design (microservices), only major architectural changes (small projects)

**When NOT to use:**
- Obvious decisions with no alternatives (no one will question it)
- Easily reversible decisions (can try both quickly)
- Trivial decisions (typo fixes, naming variables)
- Temporary experiments (not committing to long-term)

**Common ADR categories that provide high ROI:**
- **Technology choices** ("Why React vs Vue?")
- **API design decisions** ("Why REST vs GraphQL?")
- **Process changes** ("Why switch to status labels?")
- **Data modeling** ("Why normalize vs denormalize?")
- **Security decisions** ("Why this auth approach?")

---

**See also:**
- [Concept: Documentation Discipline](./concept.md)
- [Practice Exercise](./practice.md)
- [Pattern: Architecture Decision Records](./pattern.md)
- [ADR Template](../../../templates/adr-template.md)

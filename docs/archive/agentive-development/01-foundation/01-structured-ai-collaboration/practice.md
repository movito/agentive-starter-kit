# Structured AI Collaboration: Practice Exercise

**Layer:** Foundation
**Topic:** 1.1 Structured AI Collaboration
**Estimated Time:** 30-40 minutes
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

You will learn to create structured task specifications that transform vague requests into clear, actionable requirements. By the end of this exercise, you'll have written a complete task specification with explicit problem statement, testable success criteria, and clear constraints.

## Prerequisites

- Basic understanding of structured AI collaboration (read [concept.md](./concept.md))
- Text editor for writing markdown
- Familiarity with at least one programming language

## The Exercise

### Scenario

Your team maintains a web application with a user dashboard. Users have complained that loading the dashboard takes 5-8 seconds, causing frustration and abandoned sessions. Your manager asks you to "make it faster" - a classic vague request that could mean anything from caching to complete architectural redesign.

Your task is to convert this ad-hoc request into a structured task specification that an AI agent (or human developer) could implement confidently.

### Your Task

Create a task specification document following this structure:

1. **Write a clear problem statement** - Define what's broken or missing. Include current state, desired state, and why it matters. Be specific about measurements (5-8 seconds → target).

2. **Define testable success criteria** - List 3-5 objective conditions that define completion. Each criterion must be measurable (not "faster" but "loads in <2 seconds measured by Lighthouse"). Use checkboxes.

3. **Specify constraints** - Document what the implementation must NOT do. Examples: "Do not modify database schema", "Maintain backward compatibility with existing API", "Stay within current dependencies".

4. **Provide context** - Explain why this matters, what's at stake, and any relevant background (current architecture, previous attempts, user impact data).

5. **List acceptance tests** - Describe how you'll verify the fix works. Be specific about test scenarios, measurement tools, and pass criteria.

### Success Criteria

You've completed this exercise successfully when:

- [ ] Problem statement quantifies current performance (specific numbers, not "slow")
- [ ] Success criteria are objective and measurable (not subjective opinions)
- [ ] At least 3 constraints are specified to prevent scope creep
- [ ] Context section explains business impact (not just technical details)
- [ ] Someone else could read your spec and implement it without clarification questions

## Alternative: Apply to Your Project

Instead of the dashboard scenario, choose a real feature request from your current project. Identify something vague you've been asked to build ("improve security", "add social features", "make it more user-friendly") and convert it into a structured specification.

Focus on:
- Converting subjective requests into measurable targets
- Identifying unstated constraints
- Defining what "done" means objectively

The structure remains the same: problem, success criteria, constraints, context, acceptance tests.

## What You Learned

Structured specifications transform AI collaboration from guesswork into precision engineering. When you define success objectively, provide clear boundaries, and document context, you enable agents to deliver exactly what you need - not what they hallucinated from ambiguous prompts.

This practice becomes muscle memory. Every feature request, bug report, and improvement idea benefits from this structure. The 10 minutes you invest in specification saves hours of rework, miscommunication, and manual review.

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

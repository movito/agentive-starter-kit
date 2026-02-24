# Documentation Discipline: Concept

**Layer:** Foundation
**Topic:** 1.6 Documentation Discipline
**Estimated Reading Time:** 3-5 minutes

> **New to agentive development?** This guide teaches a methodology for working with AI assistants as specialized collaborators with defined roles. See the [Introduction to Agentive Development](../../00-introduction.md) for a complete overview. This document assumes basic familiarity with the approach.

---

## Key Terms

This guide uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **ADR (Architecture Decision Record)** - Document capturing key design decisions with context and rationale
- **Agent** - AI collaborator with a specific role and tool access
- **Procedural knowledge** - Documented processes and workflows (how to run tests, deploy, etc.)
- **Handoff** - Documented state transfer when work moves between agents or sessions
- **Task** - Discrete unit of work with clear acceptance criteria
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## What is Documentation Discipline?

Documentation discipline is the practice of writing the right amount of documentation at the right time—not too much, not too little, and always current. You document decisions that aren't obvious from code, update documentation when reality changes, and avoid documenting facts that the code already expresses clearly. This transforms documentation from burdensome overhead into valuable knowledge that saves time repeatedly.

Disciplined documentation focuses on the "why" rather than the "what." Code shows what the system does. Documentation explains why it does it that way, what alternatives were considered, and what constraints drove the decision. Six months later, this context prevents rediscovering the same insights or repeating the same mistakes.

In agentive development, documentation discipline enables agent self-service. When **procedural knowledge** (documented processes and workflows) is indexed, agents can find answers without human intervention. When decisions are documented in **ADRs (Architecture Decision Records)**—documents capturing key design decisions with context and rationale—agents understand constraints without trial-and-error experimentation.

## Why Does This Matter?

### Problems Solved

- **Outdated documentation worse than no documentation** - When docs contradict reality, they mislead rather than guide; readers lose trust
- **Over-documentation creates maintenance burden** - Documenting obvious facts generates pages no one reads; updates become neglected
- **Under-documentation loses institutional knowledge** - When decisions exist only in people's heads, turnover or time gaps erase understanding
- **Scattered documentation requires archaeological searches** - When knowledge is fragmented across wikis, tickets, chat, and code comments, finding answers takes longer than solving problems

### Value Provided

Good documentation has high ROI. When you document "use Fraction for frame rates to prevent cumulative rounding errors" once, every future developer avoids rediscovering the problem. If three people would each spend an hour debugging float precision, your 10-minute documentation has 18x ROI.

Documentation enables autonomous work. When agents can read procedural knowledge to learn "how to run tests" or "how to deploy," they don't interrupt humans. When task templates exist, creating well-structured tasks becomes faster than ad-hoc approaches.

Disciplined documentation provides knowledge continuity. When developers leave or switch projects, documented decisions remain. Tribal knowledge becomes organizational knowledge.

## How It Fits in Agentive Development

Documentation discipline amplifies every other practice. Structured tasks reference documentation for context. TDD test names document intent, reducing need for separate explanation. Git commit messages document change rationale. Context management creates handoff documentation.

Later layers depend on documentation even more. External evaluation requires documented plans to review. Agent instructions are documentation that defines roles and constraints. Coordination protocols are documented in shared state schemas. CI/CD configuration documents build and deploy procedures.

Without documentation discipline, knowledge evaporates. With it, learning accumulates and compounds.

## Key Principles

### 1. Document Decisions, Not Obvious Facts

Don't document what code already shows clearly. `def calculate_total(items)` doesn't need a comment saying "calculates total." Do document why decisions were made. "Used Fraction instead of float to maintain frame-perfect precision per SMPTE standards" explains a non-obvious choice that prevents bugs.

**Example:** Bad: `# This function adds numbers` | Good: `# Uses Decimal for currency to prevent floating-point precision errors in financial calculations`

### 2. Update Docs When Reality Changes

Documentation becomes outdated the moment reality diverges. When you change how tests run, update the testing documentation. When you deprecate an API, update the API docs. Treat documentation updates as part of implementation work, not optional follow-up. Automated checks can verify docs match reality.

**Example:** When switching from `npm test` to `pytest`, update CONTRIBUTING.md immediately. Add pre-commit hook that fails if README examples are syntactically invalid.

### 3. Link, Don't Duplicate

When documentation exists in multiple places, it becomes inconsistent. When you need to reference information documented elsewhere, link to it rather than copying it. "See TASK-2025-0012 for timecode precision requirements" stays current when TASK-2025-0012 updates. Copied text becomes outdated independently.

**Example:** Instead of copying API specification into five different docs, create one API.md and link to it from all five places

### 4. Templates Reduce Friction

When you've solved a problem twice, create a template. Task specifications follow a template (problem, success criteria, constraints). Agent instructions follow a template (role, responsibilities, restrictions). Templates make creating new instances faster than starting from scratch, and consistency makes reading familiar.

**Example:** After creating three agent specs manually, create AGENT-TEMPLATE.md. Now creating agent #4 takes 10 minutes instead of 45.

### 5. If It Saves Time Twice, Document It

The test for documentation value: "Will this save time when referenced again?" If a procedure is one-time, don't document it. If you've explained how to run integration tests twice, document it. Future explanations are free—you point to the docs. The breakeven is approximately two uses.

**Example:** After the third person asks "how do I set up the dev environment?", write SETUP.md. Future questions get answered with "See SETUP.md" instead of 20-minute Zoom calls.

## Documentation Types and When to Use Them

**Decision Logs (Architecture Decision Records)** - Significant architectural decisions with trade-offs. Example: "ADR-0041: Use REST API instead of file system for export"

**Task Summaries** - Completed discrete tasks with valuable learnings. Example: "TASK-2025-0012: Fixed 86-frame timecode error using Fraction instead of float"

**Procedural Knowledge** - Repeatable processes others will follow. Example: "How to run tests: `pytest -m 'not slow'` (<2s), `pytest` (~30s)"

**API Documentation** - Public interfaces with function signatures, parameters, return values, and examples

## What's Next

Ready to see documentation discipline in action? Continue to:

1. **[Example: Documentation Discipline](./example.md)** - See how procedural knowledge index evolved from tribal knowledge to searchable resource
2. **[Practice Exercise](./practice.md)** - Practice identifying what to document vs. what to leave undocumented
3. **[Reflection Questions](./reflection.md)** - Think through the trade-offs of documentation decisions
4. **[Pattern Template](./pattern.md)** - Get a reusable ADR and documentation template

**Quick self-check:** Before moving on, can you explain the difference between documenting "what" (code behavior) and documenting "why" (decision rationale)? If not, review the "Disciplined documentation focuses on the 'why'" paragraph above.

---

**See also:**
- [Example: Documentation Discipline](./example.md)
- [Practice Exercise](./practice.md)
- [1.5 Context Management Basics](../05-context-management-basics/concept.md)
- [5.3 Knowledge Indexing](../../05-systems/03-knowledge-indexing/concept.md)
- [5.4 Template Management](../../05-systems/04-template-management/concept.md)

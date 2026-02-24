# Agentive Development Teaching Guide - Complete Outline

**Version:** 1.0.0
**Status:** Draft
**Last Updated:** 2025-11-14

---

## Overview

This document provides a complete structural outline of the Agentive Development teaching guide, organized into five progressive layers plus supporting materials.

**Total estimated learning time:** 10-15 weeks (2-3 weeks per layer with practice)

---

## Layer 1: Foundation (Solo Developer + LLM)

**Goal:** Build muscle memory for structured AI-assisted work
**Estimated time:** 2-3 weeks
**Prerequisites:** Basic programming, git, command line

### 1.1 Introduction to Structured AI Collaboration
- **Concept:** Why structure matters in AI-assisted development
- **Problems solved:** Context loss, quality drift, manual review overhead
- **Example:** Converting ad-hoc prompting to structured task specification
- **Practice:** Create a structured task specification for a small feature
- **Reflection:** When does structure help vs. hinder?
- **Pattern:** Task specification template (problem, success criteria, constraints)

### 1.2 Discrete Task Decomposition
- **Concept:** Breaking work into testable, independent units
- **Problems solved:** Scope creep, unclear success, difficult debugging
- **Example:** TASK-0091 (task alignment - 30 tasks organized into 5 groups)
- **Practice:** Decompose a medium feature into 3-5 discrete tasks
- **Reflection:** How small is too small? How large is too large?
- **Pattern:** Task size guidelines (2-6 hours, single responsibility)

### 1.3 Test-Driven Development Basics
- **Concept:** Writing tests before implementation for validation
- **Problems solved:** Untested code, regression bugs, unclear specifications
- **Example:** Red-Green-Refactor cycle in precision timecode fixes (TASK-2025-012)
- **Practice:** Write failing test, implement, verify, refactor
- **Reflection:** When is TDD valuable vs. when can you skip it?
- **Pattern:** AAA test pattern (Arrange, Act, Assert)

### 1.4 Git Safety Practices
- **Concept:** Using version control for safe experimentation
- **Problems solved:** Lost work, broken code in main branch, unclear history
- **Example:** Feature branch workflow with rollback (TASK-2025-014 failure recovery)
- **Practice:** Create branch, commit incrementally, rollback a change
- **Reflection:** What commit granularity works best?
- **Pattern:** Commit message format, branch naming conventions

### 1.5 Context Management Basics
- **Concept:** Maintaining shared understanding across sessions
- **Problems solved:** "What was I doing?", repeated explanations, context loss
- **Example:** Task specification evolution with documentation trail
- **Practice:** Document current state, close session, resume from docs
- **Reflection:** What context is worth documenting vs. what can be inferred?
- **Pattern:** Session handoff template (status, blockers, next steps)

### 1.6 Documentation Discipline
- **Concept:** Writing just enough documentation at the right time
- **Problems solved:** Outdated docs, over-documentation, under-documentation
- **Example:** Procedural knowledge index maintenance
- **Practice:** Document a completed task with lessons learned
- **Reflection:** What documentation provides ROI vs. busy work?
- **Pattern:** Decision log format, task completion summary

### Foundation Summary
- **Checklist:** Are you ready for Layer 2?
- **Common pitfalls:** Over-engineering, under-testing, poor git hygiene
- **Key habits:** Test first, commit often, document decisions
- **Resources:** Templates, tools, further reading

---

## Layer 2: Augmentation (External Review)

**Goal:** Separate "maker" from "checker" mindset with external validation
**Estimated time:** 2-3 weeks
**Prerequisites:** Foundation layer complete, access to GPT-4o API

### 2.1 The Evaluation Concept
- **Concept:** Using external AI to critique your implementation plans
- **Problems solved:** Blind spots, design flaws, missing edge cases
- **Example:** TASK-2025-0073 evaluation (caught missing file/function names)
- **Practice:** Submit a task plan for evaluation, interpret results
- **Reflection:** When is external review worth the time/cost?
- **Pattern:** Evaluation request template, severity rating interpretation

### 2.2 Multi-Model Collaboration
- **Concept:** Claude for implementation, GPT-4o for evaluation
- **Problems solved:** Single-model bias, lack of adversarial perspective
- **Example:** API migration evaluation workflow (~$0.08-0.12 per task)
- **Practice:** Compare Claude and GPT-4o responses to the same plan
- **Reflection:** What are the strengths/weaknesses of each model?
- **Pattern:** Model selection matrix (which model for which task)

### 2.3 Interpreting Adversarial Feedback
- **Concept:** Understanding severity levels and actionable recommendations
- **Problems solved:** Overwhelm from feedback, unclear priorities
- **Example:** CRITICAL vs. MEDIUM vs. LOW concern handling
- **Practice:** Triage 10 recommendations by severity and effort
- **Reflection:** When should you address LOW concerns vs. ship?
- **Pattern:** Feedback triage template (impact × effort matrix)

### 2.4 Iteration Protocols
- **Concept:** When to iterate vs. when to ship or escalate
- **Problems solved:** Infinite revision loops, diminishing returns
- **Example:** 2-3 evaluation maximum with escalation rules
- **Practice:** Run evaluation, address feedback, re-evaluate, decide
- **Reflection:** What signals indicate you should stop iterating?
- **Pattern:** Iteration decision tree (when to iterate/ship/escalate)

### 2.5 Cost Awareness and ROI
- **Concept:** Balancing evaluation cost vs. value from feedback
- **Problems solved:** Over-evaluating simple tasks, under-evaluating complex ones
- **Example:** ~$0.04 per evaluation, when does ROI justify cost?
- **Practice:** Estimate evaluation ROI for 5 different task types
- **Reflection:** What task characteristics suggest evaluation is worthwhile?
- **Pattern:** ROI estimation worksheet (cost vs. time saved from catching issues)

### 2.6 When to Ask Humans Instead
- **Concept:** Recognizing evaluation limits and escalation needs
- **Problems solved:** Contradictory feedback, subjective decisions
- **Example:** Strategic decisions that require business context
- **Practice:** Categorize 10 questions as "AI eval" vs. "ask human"
- **Reflection:** What makes a question suitable for AI evaluation?
- **Pattern:** Escalation decision matrix (AI vs. human judgment)

### Augmentation Summary
- **Checklist:** Are you ready for Layer 3?
- **Common pitfalls:** Over-relying on evaluation, ignoring LOW concerns, infinite loops
- **Key habits:** Evaluate complex tasks, address CRITICAL concerns, iterate 2-3 times max
- **Resources:** Evaluation scripts, cost tracking, escalation templates

---

## Layer 3: Delegation (Specialized Agents)

**Goal:** Effective delegation to AI collaborators with appropriate guardrails
**Estimated time:** 2-3 weeks
**Prerequisites:** Layers 1-2 complete, Claude Code or similar agent system

### 3.1 Agent Design Principles
- **Concept:** Creating focused, constrained AI agents with clear roles
- **Problems solved:** Unfocused agents, unclear boundaries, context overload
- **Example:** api-developer-davinci agent (DaVinci API specialist)
- **Practice:** Design a specialized agent for your domain
- **Reflection:** What makes a good agent boundary?
- **Pattern:** Agent specification template (role, tools, constraints)

### 3.2 Instruction Engineering
- **Concept:** Writing effective agent prompts with examples and constraints
- **Problems solved:** Vague instructions, scope creep, unwanted behaviors
- **Example:** Test-runner agent with TDD workflow enforcement
- **Practice:** Write instructions for an agent, test with sample tasks
- **Reflection:** What instruction patterns work across agents?
- **Pattern:** Instruction template (identity, responsibilities, restrictions)

### 3.3 Tool Access and Permissions
- **Concept:** Granting agents appropriate capabilities and restrictions
- **Problems solved:** Over-powered agents, security risks, accidental changes
- **Example:** Feature-developer vs. document-reviewer tool access
- **Practice:** Define tool access for 3 different agent roles
- **Reflection:** What tools are safe to grant vs. require supervision?
- **Pattern:** Tool permission matrix (agent type → tools granted)

### 3.4 Single-Agent Task Assignment
- **Concept:** Matching tasks to agent capabilities and monitoring progress
- **Problems solved:** Wrong agent for task, unclear expectations, stalled work
- **Example:** TASK-0078-B assignment to test-runner (exceeded targets)
- **Practice:** Assign 5 tasks to appropriate agents, monitor completion
- **Reflection:** What signals indicate good vs. poor agent-task fit?
- **Pattern:** Task assignment checklist (complexity, tools, expertise)

### 3.5 Quality Gates and Acceptance Criteria
- **Concept:** Defining objective success measures for agent work
- **Problems solved:** Subjective "done", quality drift, manual review burden
- **Example:** 80%+ test coverage requirement for all feature tasks
- **Practice:** Define acceptance criteria for 3 different task types
- **Reflection:** What makes good vs. bad acceptance criteria?
- **Pattern:** Quality gate template (must-have vs. nice-to-have)

### 3.6 Handoff Documentation
- **Concept:** Capturing agent decisions and state for future work
- **Problems solved:** Lost context, repeated questions, unclear rationale
- **Example:** Agent handoffs.json structure and maintenance
- **Practice:** Document a completed agent task with handoff notes
- **Reflection:** What handoff information has high vs. low value?
- **Pattern:** Handoff template (status, decisions, blockers, next)

### Delegation Summary
- **Checklist:** Are you ready for Layer 4?
- **Common pitfalls:** Vague instructions, wrong tool access, poor quality gates
- **Key habits:** Clear agent roles, appropriate tools, objective success criteria
- **Resources:** Agent templates, tool matrix, quality gate examples

---

## Layer 4: Orchestration (Multi-Agent Coordination)

**Goal:** Coordinating a small AI team with parallel work streams
**Estimated time:** 3-4 weeks
**Prerequisites:** Layers 1-3 complete, multiple agents deployed

### 4.1 Task Decomposition for Parallel Work
- **Concept:** Breaking epics into independent, parallelizable tasks
- **Problems solved:** Sequential bottlenecks, idle agents, coordination overhead
- **Example:** EPIC-2025-TDD-ENFORCEMENT (4 parallel tasks, 44% time savings)
- **Practice:** Decompose a complex feature into parallel work streams
- **Reflection:** What dependencies require sequential work vs. allow parallel?
- **Pattern:** Dependency mapping template (PERT chart for agents)

### 4.2 Shared Memory Structures
- **Concept:** Central state that all agents read and update
- **Problems solved:** Conflicting changes, lost updates, state drift
- **Example:** agent-handoffs.json as coordination mechanism
- **Practice:** Design a shared memory schema for your project
- **Reflection:** What state should be centralized vs. task-local?
- **Pattern:** Shared state schema (JSON structure, update protocol)

### 4.3 Agent Communication Protocols
- **Concept:** How agents signal status, request help, handoff work
- **Problems solved:** Silent failures, stuck agents, unclear ownership
- **Example:** Status field conventions (idle/in_progress/blocked/complete)
- **Practice:** Define communication protocol for 3 agent types
- **Reflection:** What signals are worth standardizing vs. free-form?
- **Pattern:** Status signaling conventions (vocabulary, update frequency)

### 4.4 Coordinator Agent Role
- **Concept:** Meta-agent that manages other agents and orchestrates work
- **Problems solved:** No oversight, conflicting priorities, resource contention
- **Example:** Tycho coordinator managing task assignments and evaluation
- **Practice:** Create a coordinator for your agent team
- **Reflection:** What decisions should coordinator make vs. delegate?
- **Pattern:** Coordinator responsibilities (plan, assign, monitor, resolve)

### 4.5 Conflict Resolution Patterns
- **Concept:** Handling conflicting agent decisions or overlapping work
- **Problems solved:** Git conflicts, duplicated work, inconsistent approaches
- **Example:** Merge conflict resolution when agents modify same files
- **Practice:** Simulate and resolve 3 common conflict scenarios
- **Reflection:** What conflicts are preventable vs. require resolution?
- **Pattern:** Conflict resolution decision tree (automatic vs. manual)

### 4.6 Progress Tracking and Reporting
- **Concept:** Monitoring multi-agent work with dashboards and metrics
- **Problems solved:** Unclear status, missed deadlines, blocked dependencies
- **Example:** current-state.json tracking 30+ completed tasks
- **Practice:** Build a progress dashboard for 5 parallel agents
- **Reflection:** What metrics indicate healthy vs. troubled progress?
- **Pattern:** Dashboard template (agent status, task completion, blockers)

### Orchestration Summary
- **Checklist:** Are you ready for Layer 5?
- **Common pitfalls:** Under-communicating, unclear ownership, poor dependency management
- **Key habits:** Central state, clear protocols, active coordination
- **Resources:** Coordination templates, conflict patterns, dashboard examples

---

## Layer 5: Systems (Automation & Scale)

**Goal:** Sustainable pace at scale with minimal overhead
**Estimated time:** 3-4 weeks (ongoing refinement)
**Prerequisites:** Layers 1-4 complete, production system deployed

### 5.1 CI/CD for Continuous Validation
- **Concept:** Automated testing and deployment for every change
- **Problems solved:** Manual testing burden, broken deployments, regression bugs
- **Example:** GitHub Actions testing across 5 Python versions (80%+ failures prevented)
- **Practice:** Set up CI/CD pipeline for your project
- **Reflection:** What should be automated vs. what requires manual testing?
- **Pattern:** CI/CD configuration template (tests, coverage, deployment)

### 5.2 Automated Error Detection
- **Concept:** Systems that catch and report failures automatically
- **Problems solved:** Silent failures, delayed feedback, manual monitoring
- **Example:** Bugbot creating GitHub issues from CI failures
- **Practice:** Implement automated failure detection and reporting
- **Reflection:** What errors warrant automatic reporting vs. logging only?
- **Pattern:** Error detection system (monitors, alerting, issue creation)

### 5.3 Knowledge Indexing
- **Concept:** Structured knowledge base for agent self-service
- **Problems solved:** Repeated questions, outdated docs, knowledge silos
- **Example:** PROCEDURAL-KNOWLEDGE-INDEX.md (procedures + references)
- **Practice:** Build a knowledge index for your project
- **Reflection:** What knowledge should be indexed vs. discovered on demand?
- **Pattern:** Knowledge index structure (categories, links, search)

### 5.4 Template Management
- **Concept:** Reusable patterns for common tasks and agent instructions
- **Problems solved:** Inconsistent structure, reinventing patterns, quality drift
- **Example:** TASK-TEMPLATE.md and AGENT-TEMPLATE.md standardization
- **Practice:** Create templates for 5 common task types
- **Reflection:** When does templating help vs. add bureaucracy?
- **Pattern:** Template library organization (task types, agent roles)

### 5.5 Version Orchestration
- **Concept:** Coordinating versions across multiple components
- **Problems solved:** Version mismatches, broken dependencies, unclear releases
- **Example:** Semantic versioning across Python package + Electron GUI
- **Practice:** Implement version management for multi-component project
- **Reflection:** What versioning strategy fits your project?
- **Pattern:** Version management workflow (bumping, tagging, releasing)

### 5.6 Metrics and Observability
- **Concept:** Measuring development velocity and quality over time
- **Problems solved:** Unclear ROI, invisible bottlenecks, quality regressions
- **Example:** Test pass rate, coverage, task completion metrics
- **Practice:** Define and track 5-7 key metrics for your project
- **Reflection:** What metrics drive behavior vs. vanity metrics?
- **Pattern:** Metrics dashboard (leading indicators, health signals)

### 5.7 Scaling Patterns
- **Concept:** Adding more agents and tasks without linear overhead growth
- **Problems solved:** Coordination overhead, communication overload, diminishing returns
- **Example:** Growing from 3 to 10+ agents with shared protocols
- **Practice:** Scale from 3 to 6 agents, measure overhead impact
- **Reflection:** When does adding agents help vs. hurt productivity?
- **Pattern:** Scaling guidelines (agent ratios, coordination costs)

### Systems Summary
- **Checklist:** Are you operating at sustainable scale?
- **Common pitfalls:** Over-automation, vanity metrics, template proliferation
- **Key habits:** Automate repetitive tasks, track key metrics, iterate on processes
- **Resources:** CI/CD examples, metric templates, scaling patterns

---

## Supporting Materials

### Examples Directory
Real tasks from Your Project demonstrating each concept:

- **Foundation:**
  - Task decomposition: TASK-0091 (30 tasks organized)
  - TDD workflow: TASK-2025-012 (precision timecode fixes)
  - Git safety: TASK-2025-014 (failed implementation, clean rollback)

- **Augmentation:**
  - Evaluation workflow: TASK-2025-0073-B evaluation (NEEDS_REVISION verdict)
  - Multi-model collaboration: Claude + GPT-4o adversarial review
  - Iteration protocol: 2-round evaluation with escalation

- **Delegation:**
  - Agent design: api-developer-davinci (DaVinci Resolve specialist)
  - Task assignment: TASK-0078-B (test-runner exceeds targets)
  - Quality gates: 80%+ coverage requirement enforcement

- **Orchestration:**
  - Parallel work: EPIC-2025-TDD-ENFORCEMENT (4 agents, 44% faster)
  - Shared memory: agent-handoffs.json maintenance
  - Coordinator role: Tycho managing task assignments

- **Systems:**
  - CI/CD: GitHub Actions multi-version testing
  - Error detection: Bugbot automated issue creation
  - Knowledge indexing: PROCEDURAL-KNOWLEDGE-INDEX.md evolution

### Templates Directory
Copy-paste starter files for common patterns:

- **Foundation:**
  - task-specification.md (problem, success criteria, constraints)
  - test-template.py (AAA pattern with examples)
  - commit-message.txt (format with examples)
  - session-handoff.md (status, decisions, next steps)

- **Augmentation:**
  - evaluation-request.md (task description for evaluator)
  - feedback-triage.md (severity × effort matrix)
  - iteration-decision.md (iterate/ship/escalate logic)

- **Delegation:**
  - agent-specification.md (role, tools, constraints)
  - agent-instruction.md (identity, responsibilities, examples)
  - handoff-document.md (status, decisions, blockers)
  - quality-gate-checklist.md (must-have criteria)

- **Orchestration:**
  - shared-state-schema.json (coordination data structure)
  - dependency-map.md (task dependencies visualization)
  - coordinator-protocol.md (assign, monitor, resolve)
  - progress-dashboard.md (status tracking template)

- **Systems:**
  - ci-cd-config.yml (GitHub Actions template)
  - knowledge-index.md (procedural documentation)
  - version-management.md (semantic versioning workflow)
  - metrics-dashboard.md (key indicators)

### Exercises Directory
Hands-on practice tasks for each layer:

- **Foundation:** 5 exercises (task decomposition, TDD, git workflow)
- **Augmentation:** 5 exercises (evaluation, interpretation, iteration)
- **Delegation:** 6 exercises (agent design, instructions, handoffs)
- **Orchestration:** 6 exercises (parallel work, coordination, conflicts)
- **Systems:** 7 exercises (CI/CD, automation, metrics)

**Total:** 29 exercises with solutions and reflection prompts

---

## Learning Path Recommendations

### Fast Track (4-6 weeks)
For experienced developers with AI coding background:
- Skim Foundation, focus on TDD and git safety
- Deep dive Augmentation (evaluation workflow)
- Practice Delegation with 2-3 agents
- Skip Orchestration unless managing complex projects
- Implement key Systems automation (CI/CD, templates)

### Standard Track (10-12 weeks)
For developers new to systematic AI collaboration:
- Complete all Foundation exercises
- Practice Augmentation with real evaluations
- Build 3-4 specialized agents (Delegation)
- Coordinate 2-3 parallel agents (Orchestration)
- Implement full Systems infrastructure

### Thorough Track (15-20 weeks)
For teams establishing organizational practices:
- Complete all exercises with team review
- Document team-specific patterns at each layer
- Build full agent ecosystem (6-8 agents)
- Establish coordination protocols for team
- Create custom templates and knowledge base
- Track metrics and iterate on processes

---

## Success Indicators by Layer

### Foundation Success
- Tasks have clear acceptance criteria
- Tests exist before implementation
- Git history is coherent and reversible
- Documentation captures key decisions
- Context survives session boundaries

### Augmentation Success
- Design flaws caught before implementation
- Evaluation ROI is positive (time saved > cost)
- Iteration happens 2-3 times then stops
- Human escalation is rare but effective
- Multi-model collaboration feels natural

### Delegation Success
- Agents complete tasks with <2 iterations
- Quality gates are objective and automated
- Handoffs contain useful context
- Agent-task fit is usually correct
- Instruction refinement is infrequent

### Orchestration Success
- Parallel work streams don't conflict
- Agent status is always current
- Coordinator overhead is <20% of time
- Blockers are identified and resolved quickly
- Dependency management is systematic

### Systems Success
- CI/CD prevents 80%+ failures from reaching production
- Error detection is automatic and actionable
- Knowledge base answers common questions
- Templates provide consistency without bureaucracy
- Metrics drive process improvements

---

## Next Steps

1. **Read:** Start with [00-introduction.md](./00-introduction.md)
2. **Practice:** Work through [01-foundation/README.md](./01-foundation/README.md)
3. **Apply:** Try techniques on a small project
4. **Reflect:** What works for your context vs. the examples?
5. **Adapt:** Customize patterns for your domain and team

---

**Version:** 1.0.0
**Status:** Draft - Ready for layer development
**Last Updated:** 2025-11-14
**Estimated completion:** Layers 1-5 content (6-8 weeks to write, with examples)

---

*This outline reflects lessons learned from 90+ tasks completed on Your Project using agentive development practices.*

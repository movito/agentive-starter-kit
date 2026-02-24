# Layer 3: Delegation (Specialized Agents)

**Status:** 🚧 Content Coming Soon
**Estimated Completion:** Late November 2025
**Estimated Reading Time:** 2-3 weeks

---

## Overview

This layer teaches how to design and deploy single-purpose AI agents with focused roles and clear constraints. You'll learn to write effective agent instructions, grant appropriate tool permissions, define quality gates, and document handoffs effectively.

**Goal:** Effective delegation to AI collaborators with appropriate guardrails

**Prerequisites:**
- Layers 1-2 completed
- Experience with agent systems (Claude Code, etc.)
- Understanding of role-based access control

---

## What You'll Learn

### 3.1 Agent Design Principles
- **Concept:** Creating focused, constrained agents with clear roles
- **Example:** api-developer-davinci (DaVinci Resolve specialist)
- **Practice:** Design a specialized agent for your domain
- **Pattern:** Agent specification template

### 3.2 Instruction Engineering
- **Concept:** Writing effective agent prompts with examples
- **Example:** Test-runner agent instructions
- **Practice:** Write instructions, test with sample tasks
- **Pattern:** Instruction template with constraints

### 3.3 Tool Access and Permissions
- **Concept:** Granting appropriate capabilities and restrictions
- **Example:** Feature-developer vs. document-reviewer tool access
- **Practice:** Define tool access for 3 agent roles
- **Pattern:** Tool permission matrix

### 3.4 Single-Agent Task Assignment
- **Concept:** Matching tasks to agent capabilities
- **Example:** TASK-0078-B (test-runner exceeds targets)
- **Practice:** Assign 5 tasks to appropriate agents
- **Pattern:** Task assignment checklist

### 3.5 Quality Gates and Acceptance Criteria
- **Concept:** Defining objective success measures
- **Example:** 80%+ test coverage requirement
- **Practice:** Define acceptance criteria for 3 task types
- **Pattern:** Quality gate template

### 3.6 Handoff Documentation
- **Concept:** Capturing agent decisions for future work
- **Example:** agent-handoffs.json maintenance
- **Practice:** Document a completed agent task
- **Pattern:** Handoff template

---

## Available Now

While layer content is being developed, you can:

**✅ Use templates:**
- [Agent Specification Template](../templates/delegation/agent-specification.md)

**✅ Review agent examples:**
- See project `.claude/agents/` directory for real agent definitions
- See project `.agent-context/agent-handoffs.json` for coordination

---

## Next Steps

After completing this layer, proceed to:
- **[Layer 4: Orchestration](../04-orchestration/README.md)** - Coordinate multiple agents

---

**Layer Status:** Framework complete, content in development
**Last Updated:** 2025-11-14
**Estimated Content:** 30 documents (6 topics × 5 sections)

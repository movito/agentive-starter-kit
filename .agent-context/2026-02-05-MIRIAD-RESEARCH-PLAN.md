# Miriad-App Architecture Research Plan

**Date**: 2026-02-05
**Purpose**: Learn from sanity-labs/miriad-app to inform KIT-ADR-0021 (Real-Time Agent Communication)
**Repository**: https://github.com/sanity-labs/miriad-app
**Status**: Planning

---

## Executive Summary

Miriad is a multi-agent collaboration platform from Sanity.io that implements real-time agent communication - exactly what we're proposing in KIT-ADR-0021. This research will extract learnings to strengthen our ADR.

**Key Miriad Concepts to Study:**
1. **Tymbal Protocol** - Real-time streaming between agents
2. **Shared Board** - Artifact space for plans, specs, tasks, decisions
3. **Role-based Agents** - Lead, Builder, Researcher, Reviewer, Designer, Writer
4. **Claude Code Integration** - How they connect to Claude

---

## Critical Architectural Differences to Investigate

Before deep-diving, we need to understand if Miriad's approach is even compatible with ours:

| Aspect | Agentive Starter Kit | Miriad (suspected) | Compatibility? |
|--------|---------------------|-------------------|----------------|
| **Agent lifecycle** | Ephemeral (task → exit → new agent) | Long-running with memory refinement | ❓ Unknown |
| **Memory model** | Context compaction between sessions | Continuous refinement | ❓ Unknown |
| **Human interface** | CLI (terminal) | Web browser | ❓ Needs adaptation |
| **Deployment** | Local-first, file-based | Cloud platform? | ❓ Unknown |
| **Communication** | File-based handoffs | Tymbal protocol | ❓ Unknown |

**Go/No-Go Decision Point**: After Phase 2 (Agent Communication), we should have enough information to decide:
- **ADOPT**: Use Tymbal/Miriad patterns directly
- **ADAPT**: Take concepts, build our own implementation
- **ABORT**: Their approach doesn't fit our constraints

---

## Research Phases

### Phase 1: High-Level Architecture (2-3 hours)
**Goal**: Understand the overall system design

| Area | What to Find | Where to Look |
|------|--------------|---------------|
| System overview | How components connect | `README.md`, `docs/` |
| Directory structure | Code organization | Root-level folders |
| Tech stack | Languages, frameworks, DBs | `package.json`, backend configs |
| Deployment model | Local vs cloud | `docker-compose`, deployment docs |

**Deliverable**: Architecture diagram + summary document

### Phase 2: Agent Communication Deep-Dive (3-4 hours) ⭐ GO/NO-GO DECISION
**Goal**: Understand the Tymbal protocol and determine compatibility

| Area | What to Find | Where to Look |
|------|--------------|---------------|
| **What is Tymbal?** | Protocol definition, origins | docs/, design-notes/, README |
| Message format | Schema, fields, types | `backend/` type definitions |
| Transport layer | WebSocket? HTTP? Polling? | API server code |
| Addressing | How agents find each other | Protocol implementation |
| Error handling | Retries, failures, ordering | Message handlers |
| Human visibility | How humans see agent comms | Frontend components |
| **Agent lifecycle req** | Does Tymbal require persistent agents? | Protocol assumptions |

**Deliverable**: Protocol specification summary + **ADOPT/ADAPT/ABORT recommendation**

**Decision checkpoint**: After this phase, report findings and get user approval before proceeding.

### Phase 3: Shared Board / Artifact System (2-3 hours)
**Goal**: Understand how artifacts (tasks, plans, specs) are managed

| Area | What to Find | Where to Look |
|------|--------------|---------------|
| Artifact types | What kinds exist | Schema definitions, studio/ |
| State management | How status changes | Backend handlers |
| Persistence | Database schema | PostgreSQL migrations |
| Real-time sync | How changes propagate | Sync logic |

**Deliverable**: Artifact model documentation

### Phase 4: Agent Definitions & Roles (2-3 hours)
**Goal**: Understand how agents are defined and specialized

| Area | What to Find | Where to Look |
|------|--------------|---------------|
| Agent definition format | How roles are specified | `agents/` directory |
| Capabilities | What each agent can do | Agent configs |
| Spawning | How agents are started | Runtime code |
| Context passing | How agents get context | Initialization logic |

**Deliverable**: Agent definition pattern documentation

### Phase 5: Claude Code Integration (2-3 hours)
**Goal**: Understand how they connect to Claude Code CLI

| Area | What to Find | Where to Look |
|------|--------------|---------------|
| Integration method | API? CLI wrapper? MCP? | miriad-cloud references |
| Session management | Long-running vs ephemeral | Agent runtime |
| Tool exposure | What tools agents have | MCP configs |
| Context efficiency | How they manage tokens | Prompt construction |

**Deliverable**: Integration pattern documentation

### Phase 6: Synthesis & Recommendations (2-3 hours)
**Goal**: Apply learnings to our ADR

| Activity | Output |
|----------|--------|
| Compare with our current setup | Gap analysis |
| Identify adoptable patterns | Pattern catalog |
| Identify differences/constraints | Constraint list |
| Draft ADR revisions | Updated KIT-ADR-0021 |

**Deliverable**: Revised ADR + implementation recommendations

---

## Research Methods

### Primary: Code Reading
- Clone repo locally for deep exploration
- Use Serena for semantic navigation (if TypeScript supported)
- Focus on type definitions and interfaces first

### Secondary: Documentation
- Read all docs/ content
- Check design-notes/ for rationale
- Look for ADRs or decision records

### Tertiary: External Resources
- Search for blog posts about Miriad/Tymbal
- Check Sanity.io engineering blog
- Look for conference talks or demos

---

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Research notes | `.agent-context/research/miriad/` | Raw findings |
| Architecture summary | `.agent-context/research/miriad/ARCHITECTURE.md` | High-level overview |
| Protocol analysis | `.agent-context/research/miriad/TYMBAL-PROTOCOL.md` | Communication details |
| Pattern catalog | `.agent-context/research/miriad/PATTERNS.md` | Adoptable patterns |
| Gap analysis | `.agent-context/research/miriad/GAP-ANALYSIS.md` | Our setup vs theirs |
| ADR revision | `docs/decisions/starter-kit-adr/KIT-ADR-0021-*.md` | Updated proposal |

---

## Estimated Effort

| Phase | Hours | Dependency |
|-------|-------|------------|
| Phase 1: High-Level Architecture | 2-3 | None |
| Phase 2: Agent Communication | 3-4 | Phase 1 |
| Phase 3: Shared Board | 2-3 | Phase 1 |
| Phase 4: Agent Definitions | 2-3 | Phase 1 |
| Phase 5: Claude Integration | 2-3 | Phases 2, 4 |
| Phase 6: Synthesis | 2-3 | All above |
| **Total** | **13-19 hours** | |

---

## Questions to Answer

### Architecture
- [ ] Is Miriad designed for local-first or cloud-first operation?
- [ ] How do they handle offline/disconnected scenarios?
- [ ] What's the minimum viable deployment?

### Communication (Tymbal Protocol) ⭐ PRIORITY
- [ ] **What IS Tymbal?** Custom protocol? Based on existing standards? Open source?
- [ ] How do they handle message ordering and delivery guarantees?
- [ ] What's the latency for agent-to-agent messages?
- [ ] Is Tymbal separable from the rest of Miriad?

### Agent Lifecycle ⭐ CRITICAL DIFFERENCE
**Our model**: Agents are ephemeral — perform task, exit, new agent spawned for next task.
**Miriad model**: Appears to use continuous memory refinement (not compaction).

Key questions:
- [ ] Are Miriad agents long-running or ephemeral?
- [ ] How does their memory refinement work? (vs our context compaction)
- [ ] **Can Tymbal work with ephemeral agents?** Or does it require persistent agents?
- [ ] What state persists between agent invocations?
- [ ] Can agents spawn other agents?

This is potentially a **fundamental incompatibility** we need to understand early.

### Human Interaction ⭐ CRITICAL FOR CLI
**Miriad**: Humans join via web browser.
**Our need**: Humans join via CLI (terminal-based).

Key questions:
- [ ] How do humans observe agent conversations in Miriad?
- [ ] How do humans intervene in agent workflows?
- [ ] What's the permission/approval model?
- [ ] **Can their human interaction model be adapted to CLI?**
- [ ] What's the minimal interface for human participation?

### Applicability ⭐ ADOPT VS BUILD
- [ ] **Can we adopt Tymbal directly?** Or is it too coupled to Miriad?
- [ ] What needs adaptation for our file-based, CLI-first approach?
- [ ] What's out of scope for agentive-starter-kit?
- [ ] If we can't adopt, what can we learn for rolling our own?

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Repo is private/inaccessible | Already verified public access |
| Code is too complex to understand | Focus on interfaces, not implementation |
| Patterns don't apply to our setup | Document differences, adapt where possible |
| Research takes too long | Timebox each phase, prioritize communication protocol |

---

## Next Steps

1. **Approve this plan** - Get user buy-in on approach
2. **Clone the repository** - Local access for deep exploration
3. **Begin Phase 1** - High-level architecture review
4. **Create research directory** - `.agent-context/research/miriad/`

---

**Plan Author**: planner
**Review Status**: Pending user approval

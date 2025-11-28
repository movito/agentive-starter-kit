# Agentive Development: A Practical Guide

**Learn to build software with AI collaboration, not just AI code generation**

---

## What Is This?

This is a comprehensive teaching guide for **agentive development** - a methodology for coordinating specialized AI agents to build high-quality software at scale.

Unlike tutorials that teach "how to prompt AI better," this guide teaches:
- How to structure work for AI collaboration
- How to use multiple AI models as a team
- How to maintain quality at scale with automation
- How to manage context across agents and sessions
- How to apply software engineering principles to AI-assisted development

**Source:** Real practices from the this project (90+ completed tasks, 10+ specialized agents, 85%+ test pass rate maintained throughout development)

---

## Who Is This For?

**You should read this if you:**
- Use AI coding assistants regularly (Claude, GPT-4, Copilot, etc.)
- Want more consistent quality from AI-generated code
- Struggle with AI losing context mid-task
- Need to coordinate complex, multi-file changes
- Work on production systems where quality matters
- Want reproducible processes for AI collaboration

**Prerequisites:**
- Comfortable with git, command line, basic programming
- Experience with at least one programming language
- Access to AI coding assistants (Claude, GPT-4, etc.)
- Willingness to invest in tooling and process

---

## Quick Start

### 1. Read the Introduction
Start here: **[00-introduction.md](./00-introduction.md)**

Understand the philosophy, see real-world results, and decide if this approach fits your needs.

### 2. Review the Complete Outline
See the full structure: **[OUTLINE.md](./OUTLINE.md)**

Understand the 5-layer progression and estimated time investment (10-15 weeks total).

### 3. Explore Real Examples
See patterns in action: **[examples/README.md](./examples/README.md)**

32 real production examples from Foundation through Systems layers.

### 4. Use the Templates
Copy starter files: **[templates/README.md](./templates/README.md)**

Task specifications, agent designs, evaluation requests, and more.

### 5. Follow the Learning Path
Choose your track:
- **Fast Track** (4-6 weeks): Experienced developers, focus on evaluation and delegation
- **Standard Track** (10-12 weeks): Complete all layers with practice
- **Thorough Track** (15-20 weeks): Team adoption with custom templates

---

## What's Unique About This Approach?

Most "AI coding" tutorials teach prompting techniques. This guide teaches:

1. **Adversarial Review Loops**
   - Use GPT-4o to critique Claude's implementation plans
   - Catch design flaws before writing code
   - ~$0.08 per evaluation, saves hours of rework

2. **Multi-Model Collaboration**
   - Claude for implementation (code generation)
   - GPT-4o for evaluation (critique and validation)
   - Coordinator for orchestration (task management)

3. **Agent Specialization**
   - Focused roles with clear boundaries
   - Appropriate tool access and constraints
   - Domain expertise encoded in instructions

4. **Coordination Protocols**
   - Shared memory structures (agent-handoffs.json)
   - Status signaling conventions
   - Handoff documentation standards

5. **Progressive Refinement**
   - 2-3 iteration maximum per task
   - Ship with known limitations
   - Iterate based on real feedback, not perfection

6. **Test-Driven Delegation**
   - Every task requires automated validation
   - 80%+ test coverage for new code
   - Pre-commit hooks catch 80%+ of failures

---

## The Five Layers

### **Layer 1: Foundation** (Solo Developer + LLM)
Master structured AI-assisted work: discrete tasks, TDD, git safety, context management.

**Time:** 2-3 weeks
**Goal:** Build muscle memory for structured work
**Start here:** `01-foundation/README.md` (coming soon)

### **Layer 2: Augmentation** (External Review)
Add adversarial review with multiple AI models for validation and critique.

**Time:** 2-3 weeks
**Goal:** Separate "maker" from "checker" mindset
**Start here:** `02-augmentation/README.md` (coming soon)

### **Layer 3: Delegation** (Specialized Agents)
Design and deploy single-purpose agents with focused roles and quality gates.

**Time:** 2-3 weeks
**Goal:** Effective delegation to AI collaborators
**Start here:** `03-delegation/README.md` (coming soon)

### **Layer 4: Orchestration** (Multi-Agent Coordination)
Coordinate multiple agents with shared memory and handoff protocols.

**Time:** 3-4 weeks
**Goal:** Manage a small AI team
**Start here:** `04-orchestration/README.md` (coming soon)

### **Layer 5: Systems** (Automation & Scale)
Build supporting infrastructure: CI/CD, error detection, knowledge indexing.

**Time:** 3-4 weeks (ongoing)
**Goal:** Sustainable pace at scale
**Start here:** `05-systems/README.md` (coming soon)

**Important:** Don't skip layers. Each builds on the previous.

---

## Real-World Results

Metrics from the this project where this methodology was developed:

**Quality:**
- 85% test pass rate (299/350 tests) maintained
- 100% precision for timecode calculations (zero-frame error tolerance)
- 53% baseline coverage, 80%+ for new code

**Velocity:**
- 30-50% faster than estimated for complex tasks
- 80%+ of CI failures caught by pre-commit hooks
- Multi-agent parallelism enabled simultaneous work streams

**Automation:**
- Pre-commit hooks (<2s) prevent broken commits
- CI/CD validates across 5 Python versions automatically
- Evaluation system provides design critique for ~$0.08-0.12 per task

**Scale:**
- 10+ specialized agents coordinate via shared protocols
- 90+ tasks completed with consistent quality
- Agent ecosystem grew from 3 to 10+ without linear overhead

---

## Documentation Structure

```
docs/agentive-development/
├── README.md (this file)
├── 00-introduction.md ✅ COMPLETE
├── OUTLINE.md ✅ COMPLETE
│
├── 01-foundation/ (Layer 1 content - coming soon)
├── 02-augmentation/ (Layer 2 content - coming soon)
├── 03-delegation/ (Layer 3 content - coming soon)
├── 04-orchestration/ (Layer 4 content - coming soon)
├── 05-systems/ (Layer 5 content - coming soon)
│
├── examples/ ✅ FRAMEWORK COMPLETE
│   ├── README.md (32 real production examples)
│   ├── 01-task-decomposition-TASK-0091.md ✅ COMPLETE
│   ├── 11-evaluation-TASK-2025-0073-B.md ✅ COMPLETE
│   └── [30 more examples - templates ready]
│
├── templates/ ✅ FRAMEWORK COMPLETE
│   ├── README.md (usage guide)
│   ├── foundation/
│   │   └── task-specification.md ✅ COMPLETE
│   ├── delegation/
│   │   └── agent-specification.md ✅ COMPLETE
│   └── [13 more templates - coming soon]
│
└── exercises/ (29 practice exercises - coming soon)
```

---

## Current Status

**✅ COMPLETED:**
- Introduction (philosophy, real results, learning path)
- Complete outline (5 layers, 10-15 weeks structure)
- Examples framework (32 examples mapped, 2 detailed examples complete)
- Templates framework (15 templates mapped, 2 key templates complete)
- Directory structure (all folders created)

**🚧 IN PROGRESS:**
- Layer-by-layer content (01-05 directories)
- Detailed examples (30 more to document)
- Additional templates (13 more to create)
- Practice exercises (29 exercises to write)

**📅 TIMELINE:**
- Foundation complete: 2025-11-14 ✅
- Layer content: 2-3 weeks (target: early December)
- Examples: 1-2 weeks (target: mid-December)
- Templates: 1 week (target: late December)
- Exercises: 1-2 weeks (target: early January)

---

## How to Contribute

This guide documents real practices from active development. Improvements welcome:

1. **Found a better pattern?** Document what, why, and trade-offs
2. **Tried this approach?** Share your results (success or failure)
3. **Adapted for your domain?** Document domain-specific variations
4. **Improved a template?** Show before/after and context

All contributions should include real experience, not just theory.

---

## Philosophy

### Progressive Refinement Over Perfectionism
- Start simple, iterate based on real feedback
- Real code > perfect plans
- 2-3 iteration maximum on any task
- Evaluation when uncertain, not for perfection

### Test-Driven Validation
- Objective measures > subjective judgment
- Automated gates > manual review
- Coverage targets > code inspection

### Context Management as First-Class Concern
- Documentation is infrastructure, not afterthought
- Shared memory enables agent coordination
- Handoffs prevent context loss

### Multi-Model Collaboration
- Different models have different strengths
- Use Claude for implementation, GPT-4o for critique
- Coordinator orchestrates, doesn't implement

---

## Success Indicators

You'll know agentive development is working when:
- AI agents complete tasks with fewer iterations
- Quality remains consistent across sessions
- Design flaws are caught before implementation
- Context loss between sessions decreases
- Test coverage increases naturally
- Refactoring becomes less scary
- Git history is more coherent
- Documentation stays current with minimal effort

---

## Get Started

Ready to begin? **[Read the introduction →](./00-introduction.md)**

Have questions? **[Review the full outline →](./OUTLINE.md)**

Want to see real examples first? **[Explore the examples →](./examples/README.md)**

---

**Version:** 1.0.0 (Foundation Complete)
**Last Updated:** 2025-11-14
**Project:** Your Project
**License:** MIT (documentation), Project license (code examples)

---

## Related Resources

**From Your Project Project:**
- Evaluation workflow: `.adversarial/docs/EVALUATION-WORKFLOW.md`
- Testing workflow: `.agent-context/workflows/TESTING-WORKFLOW.md`
- Commit protocol: `.agent-context/workflows/COMMIT-PROTOCOL.md`
- Agent coordination: `.agent-context/agent-handoffs.json`
- Procedural knowledge: `.agent-context/PROCEDURAL-KNOWLEDGE-INDEX.md` (if exists)

**External Resources:**
- Claude Code: https://claude.com/claude-code
- Test-Driven Development: https://martinfowler.com/bliki/TestDrivenDevelopment.html
- Semantic Versioning: https://semver.org/

---

*This guide represents real development practices, not idealized theory. All examples, metrics, and patterns come from production work on Your Project. Adapt them to your context, but understand the principles behind the patterns.*

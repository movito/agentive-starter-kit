# Frequently Asked Questions

**Status:** 🚧 Content Coming Soon
**Last Updated:** 2025-11-14

---

## About This Guide

### What is agentive development?

**Coming soon:** A comprehensive explanation of the methodology, how it differs from traditional AI-assisted coding, and why it matters for building production software.

---

### Is this just about using Claude Code?

**Coming soon:** Discussion of the methodology being tool-agnostic, applicable to any agent system (Claude Code, custom agents, Cursor, etc.), and how the patterns transfer across platforms.

---

### How long does it take to learn?

**Coming soon:** Breakdown of learning timelines for different tracks (Fast: 4-6 weeks, Standard: 10-12 weeks, Thorough: 15-20 weeks), factors affecting speed, and when you'll see benefits.

---

## Getting Started

### What are the prerequisites?

**Coming soon:** Required knowledge (basic programming, git, command line), required tools (AI assistant access, API keys), and recommended experience level.

---

### Which layer should I start with?

**Coming soon:** Guidance on starting with Foundation (always), when to skip ahead (experienced developers), and how to assess your readiness for each layer.

---

### Can I apply this to existing projects?

**Coming soon:** Strategies for introducing agentive development to ongoing work, migration paths, team adoption, and measuring impact.

---

## The Evaluation Workflow

### Do I need GPT-4o access for evaluation?

**Coming soon:** Discussion of evaluation requirements, alternatives to GPT-4o, cost considerations (~$0.02-0.08/task), and when evaluation is optional vs. critical.

---

### When should I request evaluation?

**Coming soon:** Decision criteria (task complexity, uncertainty level, architectural risk), cost-benefit analysis, and examples of good vs. poor evaluation use cases.

---

### What if the evaluator is wrong?

**Coming soon:** Handling incorrect evaluation feedback, iteration limits (2-3 rounds), escalation to humans, and developing judgment about evaluation quality.

---

## Agent Design and Delegation

### How many agents do I need?

**Coming soon:** Guidance on starting with 1-2 agents, scaling to 3-5 for medium projects, 6-10 for large projects, and signs you have too many agents.

---

### How do I know what makes a good agent boundary?

**Coming soon:** Principles for agent specialization (single responsibility, clear constraints), anti-patterns (overly broad, overlapping responsibilities), and examples from Your Project.

---

### What tools should agents have access to?

**Coming soon:** Principle of least privilege, security considerations, examples of appropriate tool access by agent role, and common mistakes.

---

## Multi-Agent Coordination

### How do agents communicate?

**Coming soon:** Shared memory structures (agent-handoffs.json), status signaling conventions (idle/in_progress/blocked), handoff documentation patterns, and avoiding communication overhead.

---

### What if agents' work conflicts?

**Coming soon:** Conflict prevention (good task decomposition), conflict detection (monitoring for overlaps), conflict resolution patterns (merge strategies, coordinator intervention).

---

### How do I track multi-agent progress?

**Coming soon:** Dashboard approaches, key metrics to track, current-state.json structure, and avoiding micromanagement while maintaining visibility.

---

## TDD and Quality

### Do I really need to write tests first?

**Coming soon:** When TDD is critical (precision requirements, complex logic, refactoring), when it's optional (prototyping, trivial code), and how TDD saves time overall.

---

### What if tests slow down development?

**Coming soon:** Fast test guidelines (<2s for pre-commit), slow test markers (@pytest.mark.slow), optimization strategies, and measuring actual impact vs. perceived slowness.

---

### How much test coverage is enough?

**Coming soon:** Coverage targets (80%+ new code, maintain baseline), when 100% is appropriate, when lower is acceptable, and coverage as one signal among many.

---

## Metrics and ROI

### How do I measure if this is working?

**Coming soon:** Key metrics to track (CI pass rate, time on failures, test coverage, task velocity), baseline measurement, improvement tracking, and ROI calculation.

---

### What's the investment vs. return?

**Coming soon:** Time investment by layer (Foundation: 2-3 weeks, etc.), measurable returns (time saved, quality improved, velocity increased), and case studies from Your Project.

---

### Is the evaluation cost sustainable?

**Coming soon:** Cost analysis ($0.02-0.08 per evaluation, ~10-20 evaluations/project = $0.40-1.60), ROI (50-400x typical), and budgeting for evaluation at scale.

---

## Common Problems

### My agents forget context between sessions

**Coming soon:** Context management strategies (handoff documentation, shared memory, procedural knowledge index), session design (discrete tasks), and teaching agents to maintain state.

---

### Evaluation feedback is contradictory across iterations

**Coming soon:** Iteration limits (2-3 max), escalation to humans (when AI can't resolve), and developing judgment about when to stop iterating.

---

### CI failures still happening despite pre-commit hooks

**Coming soon:** Analysis of failure types (legitimate bugs vs. process failures), hook optimization (speed vs. coverage), and the 80/20 rule (80% prevention is excellent).

---

### Agents produce lower quality work than expected

**Coming soon:** Diagnostic approach (agent instructions? quality gates? task clarity?), common root causes, and iterative improvement of agent specifications.

---

## Advanced Topics

### Can I use agents for non-coding work?

**Coming soon:** Agentive development for documentation, design, analysis, and other knowledge work. Adaptation strategies and success patterns.

---

### How do I handle agent errors gracefully?

**Coming soon:** Error detection (monitoring, validation), error recovery (rollback, reassignment), and preventing repeated errors (instruction updates, quality gates).

---

### What about security and secrets management?

**Coming soon:** Restricting agent file access, preventing secrets in commits, secure evaluation workflow, and audit trails for sensitive operations.

---

### Can teams share agents?

**Coming soon:** Agent reusability across projects, customization for context, version control for agent specifications, and community agent libraries.

---

## Troubleshooting

### Common error messages and solutions

**Coming soon:** Catalog of common errors encountered in agentive development, their root causes, and step-by-step resolution.

---

### Performance issues

**Coming soon:** Diagnosing slow agents, slow tests, slow evaluations, and optimization strategies for each.

---

### Integration issues

**Coming soon:** Common problems integrating with CI/CD, git workflows, IDEs, and how to resolve them.

---

## Contributing

### How can I improve this guide?

**Coming soon:** Contribution guidelines, areas needing expansion, documentation standards, and how to share your own patterns.

---

### Where do I report errors or suggest improvements?

**Coming soon:** Issue reporting process, discussion forums, and how to engage with the community developing these practices.

---

## More Questions?

This FAQ is being developed based on common questions from early adopters. If you have a question not addressed here:

1. **Check the examples** - Most questions are answered through real examples
2. **Review the templates** - Many "how do I" questions have template answers
3. **Study the outline** - See which layer addresses your question
4. **Ask in discussions** - Community knowledge helps everyone

---

**Status:** Framework defined, answers to be written based on actual questions
**Last Updated:** 2025-11-14

*This FAQ will be populated as questions arise from people using the guide. Your questions help us improve the documentation for everyone.*

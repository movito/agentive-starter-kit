# Templates for Agentive Development

Copy-paste starter files for common patterns in agentive development.

---

## How to Use These Templates

1. **Copy the template file** to your project
2. **Replace bracketed placeholders** like `[PROJECT_NAME]` with your values
3. **Delete instructional comments** (lines starting with `<!-- INSTRUCTION: ... -->`)
4. **Customize for your domain** (add domain-specific sections, remove irrelevant ones)
5. **Iterate based on usage** (templates improve over time)

**These templates are starting points, not rigid requirements.** Adapt them to your needs.

---

## Templates by Layer

### Foundation Layer

**Core workflow templates:**
- `task-specification.md` - Standard task structure
- `test-template.py` - TDD starter with AAA pattern
- `commit-message.txt` - Commit format with examples
- `session-handoff.md` - State transfer between sessions
- `git-workflow-checklist.md` - Branch, commit, push safety

**File:** [task-specification.md](./foundation/task-specification.md)
**Purpose:** Structure discrete, testable work units
**When to use:** Creating any new task for yourself or agents
**Key sections:** Problem, success criteria, constraints, tests

**File:** [test-template.py](./foundation/test-template.py)
**Purpose:** TDD starter with best practices baked in
**When to use:** Starting any new feature or bug fix
**Key patterns:** AAA (Arrange-Act-Assert), edge cases, error handling

### Augmentation Layer

**Evaluation workflow templates:**
- `evaluation-request.md` - Task format for external review
- `feedback-triage.md` - Severity × effort prioritization matrix
- `iteration-decision.md` - When to iterate/ship/escalate logic
- `evaluation-summary.md` - Document evaluation outcomes

**File:** [evaluation-request.md](./augmentation/evaluation-request.md)
**Purpose:** Prepare task for external GPT-4o evaluation
**When to use:** Complex tasks (>500 lines) or architectural risks
**Key sections:** Executive summary, implementation plan, risks, success criteria

**File:** [feedback-triage.md](./augmentation/feedback-triage.md)
**Purpose:** Prioritize evaluation feedback by impact and effort
**When to use:** After receiving evaluation results
**Key insight:** Address CRITICAL always, MEDIUM selectively, LOW rarely

### Delegation Layer

**Agent design templates:**
- `agent-specification.md` - High-level agent role definition
- `agent-instruction.md` - Detailed prompt engineering
- `handoff-document.md` - Agent-to-agent state transfer
- `quality-gate-checklist.md` - Objective acceptance criteria
- `tool-permission-matrix.md` - What tools each agent gets

**File:** [agent-specification.md](./delegation/agent-specification.md)
**Purpose:** Define a new specialized agent
**When to use:** Need a new role with focused expertise
**Key sections:** Role, responsibilities, tools, constraints, examples

**File:** [agent-instruction.md](./delegation/agent-instruction.md)
**Purpose:** Write effective agent prompt with examples
**When to use:** Implementing an agent specification
**Key patterns:** Identity header, clear constraints, negative examples

### Orchestration Layer

**Coordination templates:**
- `shared-state-schema.json` - Central coordination data structure
- `dependency-map.md` - Task dependencies visualization
- `coordinator-protocol.md` - How coordinator assigns and monitors work
- `progress-dashboard.md` - Multi-agent status tracking
- `conflict-resolution-guide.md` - Handle overlapping work

**File:** [shared-state-schema.json](./orchestration/shared-state-schema.json)
**Purpose:** Define the "single source of truth" for agent coordination
**When to use:** Setting up multi-agent project
**Key fields:** Agent status, task ownership, blockers, last update

**File:** [coordinator-protocol.md](./orchestration/coordinator-protocol.md)
**Purpose:** How coordinator agent manages other agents
**When to use:** Creating coordinator role
**Key responsibilities:** Plan, assign, monitor, resolve conflicts

### Systems Layer

**Automation templates:**
- `ci-cd-config.yml` - GitHub Actions testing workflow
- `knowledge-index.md` - Procedural documentation structure
- `version-management.md` - Semantic versioning workflow
- `metrics-dashboard.md` - Key health indicators
- `pre-commit-config.yaml` - Local validation hooks

**File:** [ci-cd-config.yml](./systems/ci-cd-config.yml)
**Purpose:** Automated testing and deployment
**When to use:** Setting up continuous validation
**Key features:** Multi-version testing, coverage enforcement, fast feedback

**File:** [knowledge-index.md](./systems/knowledge-index.md)
**Purpose:** Structured knowledge base for agent self-service
**When to use:** Agents repeatedly ask same questions
**Key organization:** Categories, quick reference, detailed docs links

---

## Template Customization Guide

### Start Simple

**Don't use all templates immediately.** Start with:
1. Task specification (Foundation)
2. Test template (Foundation)
3. Commit message format (Foundation)

Add more as you need them.

### Progressive Enhancement

**Add templates when you notice repetition:**
- Creating 3rd agent? → Time for agent-specification.md
- 5th evaluation? → Time for evaluation-request.md standardization
- Coordinating 4+ agents? → Time for shared-state-schema.json

### Domain Adaptation

**Customize for your context:**

**Example: Web Development**
```markdown
<!-- task-specification.md additions -->
## UI/UX Requirements
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Accessibility (WCAG 2.1 AA)
- [ ] Performance budget (<3s LCP, <100ms FID)
```

**Example: Data Science**
```markdown
<!-- task-specification.md additions -->
## Data Requirements
- [ ] Training set: 10k+ samples
- [ ] Validation strategy: K-fold cross-validation (k=5)
- [ ] Performance baseline: >85% accuracy
```

**Example: DevOps**
```markdown
<!-- task-specification.md additions -->
## Deployment Requirements
- [ ] Zero-downtime deployment
- [ ] Rollback plan defined
- [ ] Monitoring alerts configured
```

---

## Template Evolution

Templates improve over time. Track:
1. **What sections are always deleted?** → Remove from template
2. **What sections are always added?** → Add to template
3. **What causes confusion?** → Improve instructions
4. **What patterns emerge?** → Create new templates

**Versioning templates:**
- Add version number and date to each template
- Document changes in template changelog
- Migrate old instances gradually (don't force updates)

**Example changelog:**
```markdown
## task-specification.md Changelog

### v2.0.0 (2025-11-14)
- Added TDD workflow section (mandatory)
- Added test coverage requirements
- Removed "nice-to-have" section (confusing, rarely used)

### v1.0.0 (2025-10-01)
- Initial version
```

---

## Quick Reference: Which Template When?

| Situation | Template(s) to Use |
|-----------|-------------------|
| Starting new feature | `task-specification.md` + `test-template.py` |
| Creating new agent | `agent-specification.md` + `agent-instruction.md` |
| Requesting evaluation | `evaluation-request.md` |
| After evaluation | `feedback-triage.md` + `iteration-decision.md` |
| Agent completes work | `handoff-document.md` |
| Setting up CI/CD | `ci-cd-config.yml` + `pre-commit-config.yaml` |
| Coordinating 3+ agents | `shared-state-schema.json` + `coordinator-protocol.md` |
| Documentation sprawl | `knowledge-index.md` |
| Unclear progress | `progress-dashboard.md` |

---

## Template Directory Structure

```
templates/
├── README.md (this file)
│
├── foundation/
│   ├── task-specification.md
│   ├── test-template.py
│   ├── commit-message.txt
│   ├── session-handoff.md
│   └── git-workflow-checklist.md
│
├── augmentation/
│   ├── evaluation-request.md
│   ├── feedback-triage.md
│   ├── iteration-decision.md
│   └── evaluation-summary.md
│
├── delegation/
│   ├── agent-specification.md
│   ├── agent-instruction.md
│   ├── handoff-document.md
│   ├── quality-gate-checklist.md
│   └── tool-permission-matrix.md
│
├── orchestration/
│   ├── shared-state-schema.json
│   ├── dependency-map.md
│   ├── coordinator-protocol.md
│   ├── progress-dashboard.md
│   └── conflict-resolution-guide.md
│
└── systems/
    ├── ci-cd-config.yml
    ├── knowledge-index.md
    ├── version-management.md
    ├── metrics-dashboard.md
    └── pre-commit-config.yaml
```

---

## Contributing Improvements

Found a better way to structure a template? Please document:
1. **What problem does your improvement solve?**
2. **What did you change and why?**
3. **In what contexts does this work better?**
4. **Are there trade-offs to be aware of?**

Templates are living documents. They should improve based on usage.

---

**Navigation:**
- **[Back to Main Outline](../OUTLINE.md)**
- **[View Examples](../examples/README.md)** (see templates in action)
- **[Foundation Templates](./foundation/)** (start here)

---

**Template Collection Version:** 1.0.0
**Last Updated:** 2025-11-14
**Source:** this project (battle-tested in production)

---

*These templates distill patterns from 90+ completed tasks. They represent what actually works, not what sounds good in theory. Adapt them to your needs.*

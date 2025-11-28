# Agent Creation Workflow

**Purpose**: Step-by-step guide for creating new specialized agents with standardized Evaluator instructions
**Audience**: Coordinators, project maintainers
**Last Updated**: 2025-11-06

---

## Table of Contents

1. [When to Create a New Agent](#when-to-create-a-new-agent)
2. [Before You Start](#before-you-start)
3. [Step-by-Step Process](#step-by-step-process)
4. [Evaluator Instructions Standard](#evaluator-instructions-standard)
5. [Complete Example Walkthrough](#complete-example-walkthrough)
6. [Best Practices](#best-practices)
7. [Verification Checklist](#verification-checklist)
8. [Using the Automation Script](#using-the-automation-script)
9. [Troubleshooting](#troubleshooting)

---

## When to Create a New Agent

### ✅ Good Reasons to Create a New Agent

- **New specialized role needed**: Distinct domain expertise required (e.g., "security-auditor", "api-tester")
- **Existing agent scope too broad**: Current agent trying to do too many different things
- **Domain-specific tools required**: Agent needs unique tool configuration or permissions
- **Specialized knowledge domain**: Agent needs deep context in specific area (e.g., SMPTE standards, video processing)
- **Workflow coordination**: Need dedicated agent for coordinating complex multi-step workflows

### ❌ Bad Reasons to Create a New Agent

- **One-off task**: Create a task specification instead, assign to existing agent
- **Minor variation**: Extend existing agent's role instead of creating new one
- **Temporary need**: Use general-purpose agent with specific task instructions
- **Lack of clarity**: Agent role overlaps with existing agents (causes confusion)

### Decision Tree

```
Do I need a new agent?
    ↓
Is this a distinct role that will be reused?
    ├─ NO → Use existing agent with task specification
    └─ YES ↓
Does an existing agent cover this domain?
    ├─ YES → Extend existing agent's responsibilities
    └─ NO ↓
Does this agent need unique tools or permissions?
    ├─ NO → Consider if existing agent can handle with guidance
    └─ YES ↓
CREATE NEW AGENT ✅
```

---

## Before You Start

### Prerequisites

1. **Review existing agents**: `ls .claude/agents/` - Understand current agent ecosystem
2. **Check for overlap**: Ensure new role doesn't duplicate existing agent responsibilities
3. **Define scope clearly**: Write 1-2 sentence description of agent's unique role
4. **Identify tools needed**: Determine which Claude Code tools this agent requires
5. **Choose model**: Decide between `claude-sonnet-4-5-20250929` (complex tasks) or `claude-3-5-haiku-20241022` (simpler/faster)

### Required Information

Before creating agent, gather:
- **Agent name** (kebab-case, e.g., "api-tester", "docs-generator")
- **One-sentence description** of agent's primary responsibility
- **3-6 core responsibilities** (specific, actionable)
- **Tool list** (Read, Write, Edit, Bash, Grep, Glob, etc.)
- **Role-specific scenarios** for Evaluator usage (4-6 examples)
- **Allowed operations** (what agent can do)
- **Restrictions** (what agent should NOT do)

---

## Step-by-Step Process

### Step 1: Use Agent Template

**Option A: Manual Copy**
```bash
cp .claude/agents/AGENT-TEMPLATE.md .claude/agents/your-agent-name.md
```

**Option B: Automation Script (Recommended)**
```bash
.agent-context/scripts/create-agent.sh your-agent-name "One sentence description"
```

The automation script will:
- Copy template to correct location
- Perform basic substitutions ([agent-name], [description])
- Create properly named file
- Provide next steps checklist

---

### Step 2: Customize Frontmatter

Edit the YAML frontmatter at the top of the file:

```yaml
---
name: api-tester  # Unique identifier (kebab-case)
description: API testing and validation specialist for DaVinci Resolve integration  # One sentence
model: claude-sonnet-4-5-20250929  # Choose appropriate model
tools:  # Select tools this agent needs
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - TodoWrite
  - WebFetch  # Add if agent needs to fetch web resources
  - WebSearch  # Add if agent needs to search web
---
```

**Model Selection Guide**:
- **claude-sonnet-4-5-20250929**: Complex tasks, architectural decisions, coordination, code review
- **claude-3-5-haiku-20241022**: Simple tasks, testing, straightforward implementations

**Common Tool Combinations**:
- **Implementation agents**: Read, Write, Edit, Bash, Glob, Grep, TodoWrite
- **Review agents**: Read, Grep, Glob, WebSearch, WebFetch
- **Coordination agents**: Read, Write, Edit, Bash, Glob, Grep, TodoWrite, WebSearch
- **Testing agents**: Read, Bash, Glob, Grep, TodoWrite

---

### Step 3: Define Agent Identity

Update the header section:

```markdown
# API Tester Agent  # Match agent name

You are a specialized API testing and validation agent for the this project. Your role is to test DaVinci Resolve API integrations, validate responses, and ensure API contract compliance.

## Response Format
Always begin your responses with your identity header:
🧪 **API-TESTER** | Task: [current task description]
```

**Choose an appropriate emoji**:
- 📋 Coordinator
- 💻 Feature Developer
- 🧪 Test Runner
- 📖 Document Reviewer
- 🎬 Media Processor
- 🔧 API Developer
- 📝 Content Generator
- 🔒 Security Reviewer
- [Pick one that represents the agent's role]

---

### Step 4: Define Core Responsibilities

List 3-6 specific, actionable responsibilities:

```markdown
## Core Responsibilities
- Test DaVinci Resolve API endpoints for correctness and performance
- Validate API responses against expected contracts and schemas
- Create comprehensive test suites for API integration scenarios
- Document API behavior, quirks, and limitations discovered during testing
- Report breaking changes or regressions in DaVinci Resolve API
- Coordinate with davinci-api-developer on API-related issues
```

**Good practices**:
- ✅ Start with action verbs (Test, Validate, Create, Document, Report)
- ✅ Be specific about domain (e.g., "DaVinci Resolve API" not "APIs")
- ✅ Include coordination responsibilities if applicable
- ✅ Mention documentation obligations
- ❌ Don't be too generic ("Do testing" vs "Test DaVinci Resolve API endpoints")
- ❌ Don't overlap with other agents' responsibilities

---

### Step 5: Add Role-Specific Guidelines

Replace `[Role-Specific Guidelines or Procedures]` with actual guidelines:

```markdown
## Testing Guidelines

Follow these practices when testing APIs:

1. **Test Organization**: Group tests by API endpoint/functionality
2. **Coverage Requirements**: Aim for 80%+ coverage of critical API paths
3. **Error Scenarios**: Test both success and failure cases
4. **Performance Baselines**: Measure and document API response times
5. **Regression Testing**: Verify no breaking changes in existing functionality
```

---

### Step 6: Customize Evaluator Section

**Critical**: Update the "When to Request Evaluation" scenarios for this agent's role.

**Template provides generic examples**:
```markdown
**When to Request Evaluation**:
- [Role-specific scenario 1]
- [Role-specific scenario 2]
- [Role-specific scenario 3]
- [Role-specific scenario 4]
```

**Replace with role-specific scenarios**:
```markdown
**When to Request Evaluation**:
- Ambiguous test acceptance criteria in task specification
- Multiple valid approaches to testing strategy (integration vs unit)
- Unclear performance baseline requirements
- Potential breaking changes to existing test infrastructure
- Need external perspective on test coverage adequacy
```

**The rest of the Evaluator section is standardized** - don't modify unless project-wide changes needed.

---

### Step 7: Add Quick Reference Documentation

Customize the documentation links for this agent's role:

```markdown
## Quick Reference Documentation

**Agent Coordination**:
- Task specifications: `delegation/tasks/active/`
- Agent procedures: `.agent-context/PROCEDURAL-KNOWLEDGE-INDEX.md`
- Your role context: `.agent-context/agent-handoffs.json` → `"api-tester"`
- Testing workflow: `.agent-context/workflows/TESTING-WORKFLOW.md`
- Test suite management: `.agent-context/workflows/TEST-SUITE-WORKFLOW.md`

**Evaluation Workflow**:
- **Complete guide**: `.adversarial/docs/EVALUATION-WORKFLOW.md` (347 lines)
- Quick command: `adversarial evaluate <task-file>` (you run this directly)
- Output location: `.adversarial/logs/TASK-*-PLAN-EVALUATION.md`

**API Testing Documentation**:
- ADR-0008: DaVinci API Integration
- DaVinci Resolve API docs: `docs/external/davinci-api-reference.md`
- API test examples: `tests/integration/api/`
```

---

### Step 8: Define Allowed Operations

Be explicit about what this agent can do:

```markdown
## Allowed Operations

You have the following permissions:

- Read all project files (Python, TypeScript, documentation)
- Create and modify test files in `tests/` directory
- Run pytest and test validation commands
- Execute API test scripts and validation tools
- Update `.agent-context/agent-handoffs.json` with test results
- Document API behavior in `docs/technical/api/`
- Report issues to feature-developer or davinci-api-developer agents
- Invoke Evaluator autonomously when encountering test strategy ambiguities
```

---

### Step 9: Define Restrictions

Be explicit about what this agent should NOT do:

```markdown
## Restrictions

You should NOT:

- Modify production API implementation code (coordinate with davinci-api-developer)
- Skip test validation before reporting results
- Approve API changes without comprehensive test coverage
- Work on tasks outside API testing domain
- Modify evaluation logs (read-only outputs)
- Commit code changes without passing tests
- Override test failures without investigating root cause
```

---

### Step 10: Add Role-Specific Sections (Optional)

If your agent needs additional context, add custom sections:

```markdown
## API Testing Requirements

### Test Categories
1. **Unit Tests**: Individual API function validation
2. **Integration Tests**: End-to-end API workflow testing
3. **Performance Tests**: Response time and resource usage
4. **Regression Tests**: Verify no breaking changes

### Test Data Management
- Use fixtures in `tests/fixtures/api/`
- Mock external dependencies (DaVinci Resolve)
- Document test data setup/teardown procedures

### Reporting Standards
- Test results in JUnit XML format
- Coverage reports in HTML + console
- Performance metrics in JSON format
```

---

### Step 11: Update Procedural Knowledge Index

Add your new agent to `.agent-context/PROCEDURAL-KNOWLEDGE-INDEX.md`:

```markdown
## [Agent Role] Procedures

### [Primary Procedure Name]

**Where**: [Link to workflow document if exists]

**Quick Reference**:
```bash
# Key commands this agent uses
```

**Documentation**:
- Agent file: `.claude/agents/[agent-name].md`
- [Role-specific docs]
```

**Example**:
```markdown
## API Tester Procedures

### API Testing Workflow

**Where**: `.agent-context/workflows/API-TESTING-WORKFLOW.md` (if created)

**Quick Reference**:
```bash
# Run API tests
pytest tests/integration/api/ -v

# Generate coverage report
pytest tests/integration/api/ --cov=thematic_cuts.api --cov-report=html
```

**Documentation**:
- Agent file: `.claude/agents/api-tester.md`
- Testing workflow: `.agent-context/workflows/TESTING-WORKFLOW.md`
- ADR-0008: DaVinci API Integration
```

---

### Step 12: Test Agent Creation

Before committing, verify agent works:

1. **Create test task specification** in `delegation/tasks/active/`
2. **Launch agent** via your agent system
3. **Verify agent can**:
   - Access required tools
   - Read task specification
   - Invoke Evaluator autonomously (if testing that workflow)
   - Complete basic task in role
4. **Check output** matches expected format (identity header, etc.)

---

### Step 13: Commit Changes

```bash
# Stage new agent file
git add .claude/agents/[agent-name].md

# Stage procedural index update
git add .agent-context/PROCEDURAL-KNOWLEDGE-INDEX.md

# Commit with descriptive message
git commit -m "docs: Add [agent-name] agent with Evaluator workflow

- Create specialized agent for [role description]
- Include standardized Evaluator instructions (autonomous)
- Add to procedural knowledge index
- Implements agent creation workflow from .agent-context/workflows/AGENT-CREATION-WORKFLOW.md"

# Push to branch
git push -u origin [branch-name]
```

---

## Evaluator Instructions Standard

**All agents MUST include this Evaluator section** (with role-specific customization).

### Non-Negotiable Elements

1. ✅ **Autonomous workflow** - Agents invoke directly, not via user
2. ✅ **Complete guide reference** - Link to `.adversarial/docs/EVALUATION-WORKFLOW.md`
3. ✅ **Bash command examples** - Show `adversarial evaluate` command
4. ✅ **Iteration limits** - Max 2-3 evaluations, escalate if stuck
5. ✅ **Escalation guidance** - When to ask user vs re-evaluate
6. ✅ **Technical details** - GPT-4o, Aider, cost, autonomy note

### Customizable Elements

- **"When to Request Evaluation" scenarios** - Tailor to agent's role
- **Role-specific example escalation** - Use domain-appropriate example
- **Additional context** - Add role-specific notes if needed

### Why This Matters

The Evaluator workflow is a **critical quality assurance mechanism** that prevents:
- ❌ Phantom work (implementing wrong solutions)
- ❌ Wasted time (discovering issues after implementation)
- ❌ Architectural drift (making decisions without validation)

**Consistency across agents ensures**:
- ✅ All agents have access to quality assurance
- ✅ Uniform invocation pattern (reduces confusion)
- ✅ Proper escalation safeguards (prevents infinite loops)
- ✅ Clear cost expectations (users know GPT-4o usage)

---

## Complete Example Walkthrough

Let's walk through creating an "api-tester" agent from start to finish.

### 1. Initial Decision

**Need**: Test DaVinci Resolve API integrations comprehensively
**Existing agents**: test-runner (general testing), davinci-api-developer (API implementation)
**Overlap check**: test-runner focuses on unit tests; davinci-api-developer focuses on implementation
**Decision**: Create specialized api-tester agent ✅

### 2. Gather Information

- **Name**: api-tester
- **Description**: API testing and validation specialist for DaVinci Resolve integration
- **Model**: claude-sonnet-4-5-20250929 (complex API testing requires reasoning)
- **Tools**: Read, Write, Edit, Bash, Glob, Grep, TodoWrite
- **Core responsibilities**:
  1. Test DaVinci Resolve API endpoints
  2. Validate API responses against contracts
  3. Create comprehensive API test suites
  4. Document API behavior and limitations
  5. Report API regressions or breaking changes
  6. Coordinate with davinci-api-developer on issues

### 3. Create Agent File

```bash
# Use automation script
.agent-context/scripts/create-agent.sh api-tester "API testing and validation specialist for DaVinci Resolve integration"

# Output:
# ✅ Created .claude/agents/api-tester.md
# 📝 Next steps:
#    1. Edit api-tester.md and customize all [bracketed] sections
#    2. Add to .agent-context/PROCEDURAL-KNOWLEDGE-INDEX.md
#    3. Test agent with sample task
```

### 4. Customize Frontmatter

```yaml
---
name: api-tester
description: API testing and validation specialist for DaVinci Resolve integration
model: claude-sonnet-4-5-20250929
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - TodoWrite
---
```

### 5. Update Identity Header

```markdown
# API Tester Agent

You are a specialized API testing and validation agent for the this project. Your role is to test DaVinci Resolve API integrations, validate responses, and ensure API contract compliance.

## Response Format
Always begin your responses with your identity header:
🧪 **API-TESTER** | Task: [current task description]
```

### 6. Define Core Responsibilities

```markdown
## Core Responsibilities
- Test DaVinci Resolve API endpoints for correctness and performance
- Validate API responses against expected contracts and schemas
- Create comprehensive test suites for API integration scenarios
- Document API behavior, quirks, and limitations discovered during testing
- Report breaking changes or regressions in DaVinci Resolve API
- Coordinate with davinci-api-developer on API-related issues
```

### 7. Add Testing Guidelines

```markdown
## API Testing Guidelines

Follow these practices when testing APIs:

1. **Test Organization**: Group tests by API endpoint/functionality
2. **Coverage Requirements**: Aim for 80%+ coverage of critical API paths
3. **Error Scenarios**: Test both success and failure cases
4. **Performance Baselines**: Measure and document API response times
5. **Regression Testing**: Verify no breaking changes in existing functionality
6. **Mock Strategy**: Use mocks for external dependencies (DaVinci Resolve)
```

### 8. Customize Evaluator Section

```markdown
**When to Request Evaluation**:
- Ambiguous test acceptance criteria in task specification
- Multiple valid approaches to testing strategy (integration vs unit vs E2E)
- Unclear performance baseline requirements or SLAs
- Potential breaking changes to existing test infrastructure
- Need external perspective on test coverage adequacy or risk areas
```

### 9. Add Quick Reference

```markdown
**API Testing Documentation**:
- ADR-0008: DaVinci API Integration
- Testing workflow: `.agent-context/workflows/TESTING-WORKFLOW.md`
- API implementation: `your_project/api/davinci/`
- API tests: `tests/integration/api/`
```

### 10. Define Operations and Restrictions

```markdown
## Allowed Operations

- Read all project files (Python, TypeScript, documentation)
- Create and modify test files in `tests/integration/api/` directory
- Run pytest and API test validation commands
- Execute API test scripts and validation tools
- Update `.agent-context/agent-handoffs.json` with test results
- Document API behavior in `docs/technical/api/`
- Report issues to davinci-api-developer agent

## Restrictions

- Cannot modify production API implementation code in `your_project/api/`
- Must not skip test validation before reporting results
- Should not approve API changes without comprehensive test coverage
- Must not work on tasks outside API testing domain
- Cannot modify evaluation logs (read-only outputs)
```

### 11. Update Procedural Index

Add to `.agent-context/PROCEDURAL-KNOWLEDGE-INDEX.md`:

```markdown
## API Tester Procedures

### API Testing Workflow

**Where**: `.agent-context/workflows/TESTING-WORKFLOW.md`

**Quick Reference**:
```bash
# Run API integration tests
pytest tests/integration/api/ -v

# Generate coverage report
pytest tests/integration/api/ --cov=thematic_cuts.api --cov-report=html

# Run performance tests
pytest tests/integration/api/ -m performance
```

**Documentation**:
- Agent file: `.claude/agents/api-tester.md`
- ADR-0008: DaVinci API Integration
- API implementation: `your_project/api/davinci/`
```

### 12. Test Agent

Create `delegation/tasks/active/TASK-2025-TEST-api-basic-validation.md`:

```markdown
# TASK-2025-TEST: API Basic Validation Test

**Status**: Active
**Assigned To**: api-tester
**Priority**: P2 (Testing)

## Objective
Validate that api-tester agent can successfully test a simple DaVinci Resolve API endpoint.

## Requirements
1. Test the timeline creation API endpoint
2. Validate response schema
3. Document any issues found

## Success Criteria
- Test passes or fails with clear diagnostics
- Agent demonstrates autonomous Evaluator invocation (if needed)
- Test results documented
```

Launch api-tester agent and verify it completes the test task successfully.

### 13. Commit

```bash
git add .claude/agents/api-tester.md
git add .agent-context/PROCEDURAL-KNOWLEDGE-INDEX.md
git commit -m "docs: Add api-tester agent with Evaluator workflow

- Create specialized agent for DaVinci Resolve API testing
- Include standardized Evaluator instructions (autonomous)
- Add to procedural knowledge index
- Enables comprehensive API integration testing"

git push -u origin claude/review-adversarial-workflow-docs-011CUrJoZmtBvWYGwiyvibxK
```

**Done!** ✅ New agent created, documented, and ready to use.

---

## Best Practices

### ✅ DO

1. **Start with template** - Ensures consistency and completeness
2. **Be specific about role** - Clear boundaries prevent overlap with other agents
3. **Customize Evaluator scenarios** - Make "When to Request Evaluation" relevant to agent's domain
4. **Test before committing** - Verify agent can complete basic tasks
5. **Update procedural index** - Ensure agent is discoverable
6. **Document coordination** - Specify which agents this one interacts with
7. **Include examples** - Show concrete examples of agent's work
8. **Version control** - Add template version and last updated date
9. **Use automation script** - Reduces manual errors and saves time

### ❌ DON'T

1. **Don't copy/paste from random agents** - Use template for consistency
2. **Don't skip Evaluator section** - Critical quality assurance mechanism
3. **Don't create overly broad roles** - Specific agents are more effective
4. **Don't forget procedural index** - Agent won't be discoverable
5. **Don't skip testing** - Catch issues before they affect real work
6. **Don't use manual user invocation** - Evaluator must be autonomous
7. **Don't overlap with existing agents** - Check for duplicates first
8. **Don't rush** - Take time to define role clearly

### 🎯 Optimization Tips

1. **Model selection**: Use haiku for simple/fast tasks, sonnet for complex reasoning
2. **Tool minimization**: Only include tools agent actually needs (reduces overhead)
3. **Clear restrictions**: Explicit boundaries prevent scope creep
4. **Role-specific docs**: Link to relevant ADRs, technical docs, code examples
5. **Coordination clarity**: Specify which agents this one hands off to/receives from

---

## Verification Checklist

Before committing new agent, verify:

### Frontmatter
- [ ] Unique `name:` (kebab-case, no duplicates)
- [ ] Clear `description:` (one sentence, role-specific)
- [ ] Appropriate `model:` (sonnet-4-5 or haiku)
- [ ] Correct `tools:` list (only tools needed)

### Agent Content
- [ ] Identity header with emoji and name
- [ ] 3-6 core responsibilities (specific, actionable)
- [ ] Role-specific guidelines or procedures section
- [ ] Evaluator workflow section (complete, autonomous)
- [ ] "When to Request Evaluation" scenarios (role-specific, not generic)
- [ ] Quick reference documentation (relevant links)
- [ ] Allowed operations (explicit)
- [ ] Restrictions (explicit)

### Evaluator Section (Critical)
- [ ] References `.adversarial/docs/EVALUATION-WORKFLOW.md`
- [ ] Shows `adversarial evaluate` command (autonomous)
- [ ] Includes iteration limits (2-3 max)
- [ ] Includes escalation guidance (when to ask user)
- [ ] Includes technical details (GPT-4o, cost, autonomy)
- [ ] Role-specific "When to Request Evaluation" scenarios

### Documentation
- [ ] Added to `.agent-context/PROCEDURAL-KNOWLEDGE-INDEX.md`
- [ ] All documentation links work
- [ ] Role-specific workflows referenced (if exist)
- [ ] Related ADRs linked (if applicable)

### Testing
- [ ] Agent file syntax valid (YAML + Markdown)
- [ ] Test task created and completed successfully
- [ ] Agent demonstrates expected behavior
- [ ] Evaluator invocation works (if tested)

### Version Control
- [ ] File committed with descriptive message
- [ ] Procedural index update committed
- [ ] Pushed to correct branch

---

## Using the Automation Script

The automation script (`.agent-context/scripts/create-agent.sh`) streamlines agent creation.

### Basic Usage

```bash
# Navigate to project root
cd /path/to/your-project

# Run script with agent name and description
.agent-context/scripts/create-agent.sh agent-name "One sentence description"

# Example:
.agent-context/scripts/create-agent.sh api-tester "API testing and validation specialist for DaVinci Resolve integration"
```

### What the Script Does

1. ✅ **Validates input** - Ensures name and description provided
2. ✅ **Copies template** - Uses latest AGENT-TEMPLATE.md
3. ✅ **Performs substitutions** - Replaces [agent-name] and [description] placeholders
4. ✅ **Creates file** - Saves to `.claude/agents/[agent-name].md`
5. ✅ **Provides next steps** - Shows checklist of remaining customization

### After Running Script

You still need to manually:
1. Edit agent file and customize all remaining [bracketed] sections
2. Choose appropriate model (sonnet vs haiku)
3. Select correct tools for agent's role
4. Customize Evaluator "When to Request Evaluation" scenarios
5. Add role-specific guidelines and documentation
6. Update procedural knowledge index
7. Test agent with sample task
8. Commit changes

### Script Limitations

The script handles **basic setup only**. It cannot:
- ❌ Choose the right model for your use case
- ❌ Select appropriate tools
- ❌ Write role-specific guidelines
- ❌ Customize Evaluator scenarios
- ❌ Update procedural index
- ❌ Test agent functionality

**Think of the script as a starting point**, not a complete solution.

### Script Error Handling

If script fails:
- Check you provided both name and description
- Ensure you're in project root directory
- Verify template file exists at `.claude/agents/AGENT-TEMPLATE.md`
- Check file permissions (script needs write access)

---

## Troubleshooting

### Issue: Agent file has YAML syntax errors

**Symptom**: Agent fails to load, YAML parsing errors

**Solution**:
1. Check frontmatter YAML is properly formatted
2. Ensure `---` delimiters are on their own lines
3. Verify proper indentation (2 spaces for YAML)
4. Check for special characters in `name:` or `description:` (use quotes if needed)

```yaml
# ✅ Correct
---
name: api-tester
description: "API testing and validation specialist"
---

# ❌ Wrong (missing closing delimiter)
---
name: api-tester
description: API testing and validation specialist

# ❌ Wrong (bad indentation)
---
name: api-tester
  description: API testing and validation specialist
---
```

---

### Issue: Agent doesn't appear in agent list

**Symptom**: Created agent file but can't launch agent

**Solution**:
1. Verify file is in `.claude/agents/` directory
2. Check filename matches `name:` in frontmatter
3. Ensure file has `.md` extension
4. Restart Claude Code / reload agent system
5. Check file permissions (should be readable)

---

### Issue: Evaluator section doesn't work

**Symptom**: Agent can't invoke Evaluator, gets errors

**Solution**:
1. Verify `.env` file exists with `OPENAI_API_KEY`
2. Check `adversarial` CLI is installed and in PATH
3. Ensure agent has `Bash` tool in tools list
4. Test Evaluator manually: `adversarial evaluate [file]`
5. Check `.adversarial/config.yml` is configured correctly

---

### Issue: Agent role overlaps with existing agent

**Symptom**: Confusion about which agent to use for tasks

**Solution**:
1. Review existing agents: `ls .claude/agents/`
2. Read their core responsibilities
3. Consider if existing agent can be extended instead
4. If creating new agent, document clear boundaries in restrictions
5. Update both agents' documentation to clarify coordination

---

### Issue: Agent's scope too broad

**Symptom**: Agent trying to do too many different things

**Solution**:
1. Split into multiple specialized agents
2. Define clear boundaries for each
3. Document coordination between agents
4. Update task specifications to route to correct agent

Example:
- ❌ "testing-agent" (too broad)
- ✅ "unit-test-runner" + "integration-test-runner" + "api-tester" (specific)

---

### Issue: Evaluator gives contradictory feedback

**Symptom**: Round 1 says approach A, Round 2 says approach B

**Solution**:
1. Agent should escalate to user after 2 contradictory iterations
2. User provides tiebreaker decision
3. Document decision in task specification
4. Agent proceeds with user's guidance

**Example escalation message**:
```markdown
"I've received contradictory evaluation feedback on TASK-2025-042:
- Round 1: Recommended approach A (performance optimization)
- Round 2: Recommended approach B (code simplicity)

These conflict. Please advise which is more important for this task:
1. Performance (approach A)
2. Simplicity (approach B)

This will help me proceed without further evaluation loops."
```

---

### Issue: Agent missing from procedural knowledge index

**Symptom**: Can't find agent in documentation

**Solution**:
1. Add agent section to `.agent-context/PROCEDURAL-KNOWLEDGE-INDEX.md`
2. Follow format of existing agent entries
3. Include key procedures and documentation links
4. Commit update with agent creation

---

### Issue: Template placeholders still in agent file

**Symptom**: Agent file has [bracketed] text still present

**Solution**:
1. Search for all `[` characters in file
2. Replace each [placeholder] with actual content
3. Verify no placeholders remain before committing
4. Use automation script next time (reduces manual errors)

```bash
# Find remaining placeholders
grep -n '\[' .claude/agents/your-agent.md
```

---

## Related Documentation

- **Agent Template**: `.claude/agents/AGENT-TEMPLATE.md` (reusable template)
- **Evaluator Workflow**: `.adversarial/docs/EVALUATION-WORKFLOW.md` (complete guide)
- **Procedural Index**: `.agent-context/PROCEDURAL-KNOWLEDGE-INDEX.md` (central reference)
- **Agent System Guide**: `.agent-context/AGENT-SYSTEM-GUIDE.md` (overall architecture)
- **ADR-0011**: `docs/decisions/adr/0011-adversarial-workflow-integration.md` (decision rationale)
- **Automation Script**: `.agent-context/scripts/create-agent.sh` (agent creation automation)

---

**Last Updated**: 2025-11-06
**Maintained By**: Coordinator agent, document-reviewer agent
**Questions?** See PROCEDURAL-KNOWLEDGE-INDEX.md or ask user

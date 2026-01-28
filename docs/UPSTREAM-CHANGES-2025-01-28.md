# Upstream Changes: Agent Standards (2025-01-28)

This document explains the changes contributed from gas-taxes to agentive-starter-kit, and how to upgrade your project to incorporate them.

## What Changed

Two new agent standards were added to the starter kit:

### 1. File Location Standards (PR #7)

**Problem solved**: Agents were creating ADRs and documentation in wrong locations (e.g., `.claude/` instead of `docs/decisions/adr/`).

**Files changed**:
- `.claude/agents/AGENT-TEMPLATE.md` - New "File Location Standards" section
- `.claude/agents/OPERATIONAL-RULES.md` - Comprehensive location rules

**What it adds**:
```markdown
| Document Type | Location | Example |
|---------------|----------|---------|
| ADRs | docs/decisions/adr/ | ADR-004-feature-name.md |
| Tasks | delegation/tasks/1-backlog/ | TASK-0030-task-name.md |
| Research | [project-specific]/research/ | analysis.md |
```

### 2. Research Quality Standards (PR #8)

**Problem solved**: Research documents lacked citation integrity, reproducibility, and external validation.

**Files added**:
- `.agent-context/workflows/RESEARCH-QUALITY-STANDARDS.md` - Four Quality Gates workflow
- `docs/decisions/starter-kit-adr/KIT-ADR-0020-research-quality-coupling-strategy.md`

**Files changed**:
- `.claude/agents/AGENT-TEMPLATE.md` - New "Research Quality Standards" section (optional for implementation agents)

**The Four Quality Gates**:
1. **Citation Integrity** - All claims must have testable citations (✅/⚠️/❌ markers)
2. **Factual Accuracy** - Confidence levels (High/Medium/Low) on key claims
3. **Reproducibility** - Search methodology documented in appendix
4. **External Validation** - `adversarial evaluate` for high-stakes documents

---

## How to Upgrade

### Option A: Cherry-pick specific files (Recommended)

If you've customized your agents, cherry-pick the new files:

```bash
# Add upstream remote (if not already)
git remote add upstream https://github.com/movito/agentive-starter-kit.git
git fetch upstream main

# Cherry-pick the specific commits
git cherry-pick 7e93112  # File Location Standards
git cherry-pick 1d97df4  # Research Quality Standards

# Resolve any conflicts in AGENT-TEMPLATE.md
```

### Option B: Manual file copy

Copy these files from the upstream repo:

```bash
# Research Quality Standards (new files)
curl -o .agent-context/workflows/RESEARCH-QUALITY-STANDARDS.md \
  https://raw.githubusercontent.com/movito/agentive-starter-kit/main/.agent-context/workflows/RESEARCH-QUALITY-STANDARDS.md

curl -o docs/decisions/starter-kit-adr/KIT-ADR-0020-research-quality-coupling-strategy.md \
  https://raw.githubusercontent.com/movito/agentive-starter-kit/main/docs/decisions/starter-kit-adr/KIT-ADR-0020-research-quality-coupling-strategy.md
```

Then manually add the sections to your existing agents:
1. Copy "File Location Standards" section from AGENT-TEMPLATE.md
2. Copy "Research Quality Standards" section (for knowledge agents only)
3. Update OPERATIONAL-RULES.md with file location rules

### Option C: Full template refresh

If you haven't customized agents much:

```bash
git fetch upstream main
git checkout upstream/main -- .claude/agents/AGENT-TEMPLATE.md
git checkout upstream/main -- .claude/agents/OPERATIONAL-RULES.md
git checkout upstream/main -- .agent-context/workflows/RESEARCH-QUALITY-STANDARDS.md
git checkout upstream/main -- docs/decisions/starter-kit-adr/KIT-ADR-0020-research-quality-coupling-strategy.md
```

---

## After Upgrading

1. **Update existing agents** - If you have custom agents, add the File Location Standards section to each
2. **Knowledge agents** - Add Research Quality Standards section to agents that produce research
3. **Template version** - Update to `1.3.0` in any agents based on the template

### Verify Integration

```bash
# Check File Location Standards present
grep -l "File Location Standards" .claude/agents/*.md

# Check Research Quality workflow exists
ls .agent-context/workflows/RESEARCH-QUALITY-STANDARDS.md

# Check KIT-ADR-0020 exists
ls docs/decisions/starter-kit-adr/KIT-ADR-0020*.md
```

---

## Questions?

These standards originated from gas-taxes project learnings and were upstreamed to benefit all projects using the starter kit.

- **File locations**: Prevents agents from cluttering `.claude/` with project docs
- **Research quality**: Ensures research outputs are verifiable and reproducible

Template version: **1.3.0**

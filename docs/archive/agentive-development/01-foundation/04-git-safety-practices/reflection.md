# Git Safety Practices: Reflection Questions

**Layer:** Foundation
**Topic:** 1.4 Git Safety Practices
**Estimated Time:** 10-15 minutes

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

## Purpose

Reflection helps you develop intuition for commit granularity, history management, and the trade-offs between clean history and preservation of process. These questions push you to think critically about when git safety enables confidence versus when it creates unnecessary complexity.

## Questions to Consider

### 1. What commit granularity works best for your workflow?

You've learned to make incremental commits that create restore points. But there's a spectrum: commit after every file change (dozens of tiny commits) or commit after complete features (one large commit). Too granular creates noisy history. Too coarse loses the benefit of incremental checkpoints.

Reflect on your practice exercise. How did you decide when to commit? When did granular commits help you roll back precisely? When did they create history that was hard to navigate? What's your personal sweet spot?

### 2. When should you squash commits versus preserve them?

Before merging a feature branch, you can squash 20 incremental commits into one polished commit, or preserve the entire development history. Squashing creates clean, readable history. Preserving shows the journey, including false starts and iterations.

When does the development process matter enough to preserve? When is a clean final result more valuable than historical accuracy? How do you balance "this is what I did" with "this is what matters"?

### 3. How do commit messages help future you (and others)?

A commit message can be "fix bug" or "fix: Prevent negative timecode values by validating frame count before conversion (resolves issue #47)". The second takes 15 extra seconds but provides context that might save 15 minutes of investigation later.

Think about your recent git history. When did a good commit message answer your question immediately? When did a vague message force you to read the diff to understand what changed and why? What's the minimum viable message that provides future value?

### 4. How do you balance safety with speed?

Git safety practices - feature branches, granular commits, meaningful messages - take time. But they save time when things go wrong. The question is: which practices provide enough safety to be worth the overhead?

When do you rigorously follow all safety practices versus when do you take shortcuts? How do you recognize which work is risky enough to demand full safety discipline? Where's the pragmatic middle ground?

## Reflection Activity

Choose one of these methods to capture your reflections:

**Commit message audit:** Review your last 20 commits. How many messages would help you six months from now versus how many are cryptic? Create a personal commit message template based on your best examples. Use it for a week and refine.

**History navigation exercise:** Use `git log --oneline` to view recent history. Can you understand what changed and why without reading diffs? If not, what would make history more navigable? Document your insights and adjust your commit practices.

**Rollback simulation:** Intentionally break something, commit it, then practice three rollback methods: `git revert`, `git reset --hard`, and `git checkout` of specific files. When would you use each? Document a decision tree for future reference.

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

**Next:** [Reusable Pattern](./pattern.md)

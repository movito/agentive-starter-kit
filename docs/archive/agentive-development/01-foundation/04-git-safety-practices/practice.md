# Git Safety Practices: Practice Exercise

**Layer:** Foundation
**Topic:** 1.4 Git Safety Practices
**Estimated Time:** 30-40 minutes
**Difficulty:** Beginner

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

## Objective

You will practice safe experimentation with git by creating feature branches, making granular commits, and intentionally rolling back changes. By the end of this exercise, you'll be comfortable using git as a safety net that enables fearless exploration.

## Prerequisites

- Understanding of git safety practices (read [concept.md](./concept.md))
- Git installed and configured
- An existing git repository (use a practice repo or your current project)
- Basic git knowledge (commit, branch, checkout)

## The Exercise

### Scenario

You're experimenting with a new configuration format for your application. You're not sure if the approach will work, so you want the ability to try it, evaluate it, and potentially revert everything cleanly if it doesn't pan out.

This scenario demonstrates why git safety matters: you need freedom to experiment without fear of breaking working code or losing your current state.

### Your Task

Practice the full git safety workflow:

1. **Create a feature branch** - From your main branch, create a feature branch named `experiment/new-config-format`. Switch to this branch. Verify you're on the new branch with `git status` or `git branch`.

2. **Make first incremental commit** - Create or modify a configuration file. Make a small, focused change (add one new field, change one format). Commit with a descriptive message following this format: `config: Add JSON schema validation field`. Run `git log` to verify.

3. **Make second incremental commit** - Make another small change to the same file or a related file. Commit separately with another descriptive message. This creates a history with multiple restore points.

4. **Make third incremental commit** - Add one more change. Commit it. Now you have three granular commits, each representing an atomic change you can examine or revert independently.

5. **Intentionally rollback one commit** - Use `git revert HEAD` to undo the last commit, or `git reset --hard HEAD~1` to remove it from history (only safe on unpushed branches). Verify the file returned to its previous state.

6. **Verify restoration** - Check `git log` to see your commit history. Examine the files to confirm they match the earlier state. You should be able to see exactly what was rolled back and why.

7. **Experiment with complete branch deletion** - Switch back to main (`git checkout main`). Delete the experimental branch with `git branch -D experiment/new-config-format`. Verify your main branch is unchanged. The experiment is completely erased.

### Success Criteria

You've completed this exercise successfully when:

- [ ] You created a feature branch and made 3+ commits
- [ ] Each commit has a clear, descriptive message (not "fix", "update", "wip")
- [ ] You successfully rolled back at least one commit
- [ ] You verified files returned to their previous state after rollback
- [ ] You deleted the experimental branch cleanly
- [ ] Your main branch remains in its original working state
- [ ] You understand how to restore to any commit in your history

## Alternative: Apply to Your Project

Next time you're unsure about an approach, use this workflow in your real project. Before refactoring a complex module, extracting a shared utility, or changing an architecture pattern, create a feature branch.

Make commits after each logical step. If the approach works, great - merge it. If it doesn't, delete the branch and try a different approach. This safety net transforms risky experiments into low-cost exploration.

## What You Learned

Git safety practices give you freedom to experiment fearlessly. When you know you can always roll back, you become willing to try approaches you'd otherwise avoid. Feature branches isolate experiments. Granular commits create restore points. Meaningful messages make history navigable.

This practice eliminates "I'm afraid to touch that code" paralysis. With git safety, every change is reversible, every experiment is sandboxed, and every mistake is recoverable. You ship faster because you're confident you can undo what doesn't work.

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

**Next:** [Reflection Questions](./reflection.md)

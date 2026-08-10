# KIT-0099: Release plugin 2.0.1 — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-08-10
**From**: planner-f5
**To**: feature-developer
**Task**: `.kit/tasks/3-in-progress/KIT-0099-release-plugin-201.md`
**Status**: Ready — KIT-0098 merged (c330c34); the canon is trusted;
this is the mechanical sync that turns the drift guard green
**Evaluation**: skipped (planner) — mechanical release; the spec's
5-step scope IS the recipe

**Target Codebase**: `movito/agentive-skills` (the marketplace repo) —
NOT the kit. Kit-side there is nothing to edit; the drift guard going
green on kit main is a RESULT you verify, not a change you make.

## Session topology (read before anything else)

**Cross-repo session — the operator's standard practice**: the tab
opens in the KIT primary clone (`~/Github/agentive-starter-kit`, on
`main`); ALL writes go to the marketplace clone via
`git -C ~/Github/agentive-skills …`. This satisfies your Phase 1
check in cross-repo form: your own CWD stays on kit `main` and you
commit NOTHING there — the kit is read-only source material (current
main = the post-KIT-0097/0098 canon).

- Target branch: `release/agentive-workflow-2.0.1` in
  `~/Github/agentive-skills` — **created by the planner from fresh
  origin/main**; VERIFY
  (`git -C ~/Github/agentive-skills branch --show-current`), never
  create; if it's not there, STOP and ask. No kit worktree exists for
  this task — deliberate: there is nothing kit-side to edit.
- One PR on movito/agentive-skills (`gh pr create --repo
  movito/agentive-skills --head release/agentive-workflow-2.0.1 …`).
  CodeRabbit reviews there (verified: 23 threads on #4); operator
  review is the merge gate.
- Never a bare `git commit`/`git push` — every git write carries
  `-C ~/Github/agentive-skills` (a bare command would hit the kit
  primary on main).

## Scope — the spec's 5 steps, with anchors

1. **Refresh changed files** from kit `.claude/` into
   `plugins/agentive-workflow/` — the delta since 2.0.0 is exactly the
   #120 + #121 merges: derive the file list with
   `git -C ~/Github/agentive-starter-kit diff --name-only <2.0.0-sync-commit>..main -- .claude/`
   (the roster.yaml records the 2.0.0 source hashes — use it to
   confirm the delta list; that's what it's FOR). Apply the KIT-0096
   transforms to the refreshed files: KIT-LOCAL regions don't ship;
   same generalization judgment on the changed text only. The 2.0.0
   transform decisions are recorded in agentive-skills#4 — reuse them,
   don't re-decide.
2. **roster.yaml hashes** updated for refreshed files; roster
   membership UNCHANGED (no roster decisions in a patch release).
3. **plugin.json → 2.0.1**; CHANGELOG entry naming the fix families
   (the KIT-0097 findings + KIT-0098 coherence repair), not 21 bullet
   points. **R2 PII decision**: `author.email` is the operator's
   personal address — surface keep-vs-noreply in the PR body for the
   operator; do NOT change it yourself.
4. **PR + operator merge.** Bot round expected (CodeRabbit); the
   fast-tier-only + `--format diff` evaluator rule applies if you run
   a trio (prose-shaped) — for a pure sync PR a trio is optional;
   note the skip decision either way.
5. **Verify after merge**: kit main's Plugin Drift Guard run GREEN
   (re-run or wait for the next trigger — cite the run URL);
   `claude plugin marketplace update agentive-skills` +
   `claude plugin update agentive-workflow@agentive-skills` →
   `claude plugin list` shows 2.0.1; closure comment on
   agentive-skills#4 referencing KIT-0097/0098/0099.

## Out of scope — do not touch

- Kit-side files (canon is frozen for this task)
- Roster membership, plugin description beyond the version-driven
  bits, agent content beyond the mechanical transforms
- KIT-0074/0094/0095 riders — 2.0.1 is a patch sync, nothing hitches

---

**Task File**: `.kit/tasks/3-in-progress/KIT-0099-release-plugin-201.md`
**Recipe precedent**: KIT-0097 handoff §"The 2.0.1 release step"; the
KIT-0096 transforms + agentive-skills#4 decision record

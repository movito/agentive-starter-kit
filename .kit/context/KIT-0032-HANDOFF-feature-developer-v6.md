# KIT-0032: Build the `upgrader` Agent — Implementation Handoff

**You are feature-developer-v6. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-06-26
**From**: Coordinator (KIT-0030 plugin-consolidation session)
**To**: feature-developer-v6 (claude-opus-4-8)
**Task**: `.kit/tasks/5-done/KIT-0032-build-upgrader-agent.md`
**Status**: Ready for implementation
**Evaluation**: ✅ REVISED — three-evaluator arch review done (1 APPROVED, 2
REVISION_SUGGESTED); convergent findings already folded into the spec. Do **not**
relitigate the declined suggestions — they are documented with reasoning in the
task's "Evaluation" section.
**Target Codebase**: This repo (agentive-starter-kit) only. The deliverable is
one agent file.

---

## Why This Task Exists

KIT-0030 made the `agentive-workflow` plugin the distribution channel for shared
agents. KIT-ADR-0025 (just slimmed) decided that on a plugin upgrade, project
specifics are **preserved by construction** — the pin bump replaces only the
plugin body. `docs/PLUGIN-UPGRADE-GUIDE.md` is the hand-runbook for doing that
upgrade. **This task turns that runbook into an agent** so the upgrade is
repeatable rather than hand-followed. You are building the mechanism ADR-0025
points at.

Read these before writing anything (in order):

1. `.kit/tasks/5-done/KIT-0032-build-upgrader-agent.md` — **the spec**. Its
   acceptance criteria are your definition of done.
2. `docs/PLUGIN-UPGRADE-GUIDE.md` — **the agent's specification**. Your agent
   body maps 1:1 to its 7 steps + rollback. If the agent and the guide ever
   disagree, **the guide wins** and the agent is corrected; the agent should
   *cite* the guide's gotchas, not re-derive them, so the two stay in sync.
3. `.kit/adr/KIT-ADR-0025-agent-localization-vs-plugin-upgrades.md` — why this
   exists; the "preserve local" principle.
4. `.kit/adr/KIT-ADR-0024-*.md` §3 (plugin distribution) and §4 (deliberate
   upgrade) — the boundary you must not cross into manifest-sync territory.

## The Deliverable

A single file: `.claude/agents/upgrader.md` (kit-**local** for now).

- **Do NOT add it to the plugin** in this task. Build kit-local, prove it, then
  the distribution decision is made separately. (If it ever ships in the plugin
  it needs the same genericization discipline that bit `code-reviewer`/
  `ci-checker` in KIT-0030 PR #3 — out of scope here.)
- Frontmatter: mirror existing agents (`.claude/agents/ci-checker.md` is the
  closest shape — `name`, `description`, `model`, scoped `tools:`). Scope
  `tools:` to `Bash, Read, Edit, Grep, Glob` — it needs nothing else.
- **Model pin**: sonnet-class is right (mostly deterministic shell + two light
  judgment calls; doesn't need Opus). Match the kit's *current* sonnet pin
  convention rather than inventing an ID — note the irony that "which model ID
  is current" is exactly the rollout question this agent automates.
- Body: ordered phases mapping to the guide's steps, each phase naming the exact
  command(s) and the expected output to confirm before advancing.

## Design Principle (the heart of the task)

**Deterministic shell for the mechanical axes; LLM reasoning for exactly two
decisions.** The agent is a careful script-runner, not a thinker. The four axes
and what's mechanical vs judgment are tabled in the spec — internalize that
table. The **only** two places the agent reasons rather than runs a command:

1. **Retire-local?** — when the new version supersedes a local copy, which local
   adaptations/agents to keep vs retire.
2. **Model-pin rewrite** — which local agents move, and to which model ID.

Everything else (version detect, marketplace guard, `/plugin update`, namespace
grep, provenance restamp, the `model:` rewrite itself) is shell. If you find the
agent "reasoning" about a version-string comparison, that's a smell — make it a
command.

## Hard Constraints (user decisions — do not relitigate)

- **Scope is ongoing upgrades ONLY.** The agent must **refuse** (halt + one-line
  reason + pointer to the right runbook, never a silent skip):
  - initial migration onto the plugin (manual, per user decision),
  - scripts/`scripts/core/` manifest upgrades → point to
    `docs/MANIFEST-UPGRADE-GUIDE.md`; a detected scripts gap becomes a
    **post-upgrade hint to run `./scripts/core/check-sync.sh`**, never folded in,
  - `CLAUDE.md` identity/topology edits beyond the Provenance stamp.
- **Two-phase: preview → operator ACK → apply.** No file or `git` mutation
  before an explicit ACK. Preview prints version delta, reconcile diff, and the
  model-pin list.
- **Idempotent**: current pin == target ⇒ stop at step 1, "nothing to do", zero
  changes.
- **Marketplace-source guard**: assert GitHub-sourced (`movito/agentive-skills`),
  refuse/warn on a local `Directory (...)` source (the re-point is a command the
  *user* runs — the agent cannot edit `settings.json`).
- **Never hand-edit cached plugin files** (`~/.claude/plugins/cache/...`).
- **Model-pin rewrite is frontmatter-aware** — only the `model:` key in the
  opening YAML block of files in `.claude/agents/`, confirm line + context
  first, never a `model:` mention in prose.
- **Pushes**: the agent pushes nothing in non-kit repos (stage/commit, hand the
  push to the user via `! git -C <path> push`). Provenance + model-pin edits
  commit together (guide step 7).
- **In THIS kit repo**: never stage or delete the untracked `.kit/adversarial/`
  directory — it is the user's. The pre-commit hook **reformats then aborts** —
  re-stage and make a fresh commit, never `--amend`.

## Suggested Order

1. `git checkout -b feature/KIT-0032-upgrader-agent`
2. `./scripts/core/project start KIT-0032` (moves spec to `3-in-progress/`)
3. Read the guide end-to-end; sketch the phase list from its 7 steps + rollback.
4. Write `.claude/agents/upgrader.md` — frontmatter, then phases, each citing the
   guide step it implements and the deterministic-vs-judgment split.
5. **Prove the no-op path**: dry-run/reason through the agent against *this kit
   repo*, which is already at the current pin — it must report "nothing to do"
   and make no changes. Capture that output in the task notes or a short session
   handoff. (This is acceptance criterion #8 — it's the cheapest end-to-end
   proof available without a real version bump.)
6. Self-review against the spec's acceptance criteria; run the project gate
   (`./scripts/core/ci-check.sh`) before committing.

## Acceptance Criteria

Mirror of the spec — every box in
`.kit/tasks/5-done/KIT-0032-build-upgrader-agent.md` must be satisfied.
Pay special attention to: scope refusals are concrete (not just the word
"refuse"), the preview→ACK→apply gate, frontmatter-aware model-pin rewrite, and
the no-op dry-run proof.

## If You Get Stuck / Run Long

This is a ~half-day, single-file task — it should fit one session. If you stall
on a guide ambiguity, the guide is authoritative; note the ambiguity for the
coordinator rather than inventing behavior. If you somehow reach end-of-session
mid-stream, write a session handoff in `.kit/context/` so the next session
resumes cleanly.

---

**Task File**: `.kit/tasks/5-done/KIT-0032-build-upgrader-agent.md`
**Spec it automates**: `docs/PLUGIN-UPGRADE-GUIDE.md`
**ADRs**: KIT-ADR-0025 (backs this), KIT-ADR-0024 §3/§4 (the boundary)
**Eval logs** (local, gitignored): `.adversarial/logs/KIT-0032-build-upgrader-agent--*.md`
**Handoff Date**: 2026-06-26

# KIT-ADR-0025: Localizing Plugin-Distributed Agents Without Losing Upgrades

**Status**: Proposed
**Date**: 2026-06-23
**Author**: Claude Code + User
**Supersedes**: None
**Related**: KIT-ADR-0024 (plugin/manifest distribution; §3 is the plugin
channel this refines), KIT-ADR-0001 (system-prompt size), KIT-ADR-0022
(manifest sync ownership), KIT-0030 (the migration that surfaced this)

## Context

KIT-ADR-0024 §3 made the `agentive-workflow` plugin the distribution channel
for shared agents (`feature-developer-v7`/`-v6`, `code-reviewer`,
`ci-checker`). KIT-0030 shipped that plugin (v1.1.0) and migrated the first
consumer (label-maker-planning), deleting the local agent copies in favor of
the namespaced plugin versions.

That migration exposed a structural problem. A shared agent definition is
**two things with different lifecycles fused into one Markdown file**:

1. **Workflow body** — phases, gates, the review/CI loop, shell rules.
   Plugin-owned; the whole point of distribution is that projects *receive
   upgrades* to this.
2. **Project specifics** — tech stack, task-ID prefix, repo layout/topology,
   local test/lint commands, stack-specific footguns, the Serena project to
   activate. Project-owned; these *must survive* a plugin upgrade.

Because the two are fused, a project cannot take a workflow upgrade without
clobbering its localization, and cannot localize without forking away from
upgrades. This is the same drift KIT-ADR-0024 set out to kill, displaced from
"per-repo copies" to "per-repo fills."

### Evidence this is real, not hypothetical

- `feature-developer-v7`/`-v6` ship as **unfilled templates** (ACME-NNNN /
  EXTENSION-POINT placeholders). KIT-0030 deliberately distributed the
  unfilled body because the filled-for-the-kit copy would be wrong everywhere
  else.
- BugBot (KIT-0030, PR #3) caught the distributed `code-reviewer` hardcoding
  `mcp__serena__activate_project("agentive-starter-kit")` and `ci-checker`
  validating against the planning repo's origin — project specifics that had
  leaked into a to-be-distributed agent. Both were genericized in commit
  `7bf230a`, but only by *removing* the specifics, not by giving them a home.
- The label-maker migration pointed its "primary implementation agent"
  recommendation at the plugin's **unfilled** `agentive-workflow:feature-developer-v6`.
  It works only because the agent happens to read the task spec and CLAUDE.md
  at runtime — an **implicit, undocumented** contract, not a designed one.

### Hard constraint: how Claude Code loads agents

A Claude Code agent's `.md` file **is** its system prompt, loaded statically
when the agent launches. There is no `@include`, no inheritance, no
frontmatter templating at load time. This splits localization into two
classes:

- **Behavioral context** (stack, conventions, commands, layout, which project
  to navigate) — can be loaded at runtime as an early agent action.
- **Structural config** (the `model:` pin, `disallowedTools`, other
  frontmatter) — cannot be loaded at runtime; it must be in the file at
  launch.

For the agents in scope, the localization is ~95% behavioral. Frontmatter
localization (e.g. a project wanting a different model) is the rare case.

### `CLAUDE.md` is already injected

A project's `CLAUDE.md` is loaded into every session's context automatically.
The topology bits an agent needs (the `## Target Repository` section, project
rules) are therefore *already present* without any read step. What is **not**
in CLAUDE.md today is the agent-specific depth (stack-notes footguns, the
evaluator trio, the exact local test loop) — those are what the extension
points currently carry.

## Decision Drivers

- **Upgradable**: bumping the plugin pin must deliver a new workflow body with
  no manual merge of project specifics.
- **Localizable**: each project states its specifics once, in a place it owns.
- **Fits the runtime**: no reliance on agent `@include`/inheritance that
  Claude Code does not have.
- **Minimal machinery**: prefer "edit one file" over a build step + artifact.
- **General**: one mechanism for all shared agents, not a feature-developer
  special case.
- **No drift**: the localized surface must be small and not re-accumulate the
  upstream body.

## Options Considered

### Option A — Runtime context file (stable-interface split)

The plugin agent stays generic. Early in its workflow (Phase 0) it reads a
project-owned context file at a **fixed path**, `.kit/PROJECT-CONTEXT.md`,
with a defined schema (tech stack, task prefix, content language, topology,
layout, local test/lint commands, stack-specific footguns, Serena project
name). Localize = edit that file. Upgrade = bump the pin; the file is
untouched.

- **Pros**: zero codegen; one small project-owned file; the agent body never
  carries specifics, so it can be replaced wholesale on upgrade; reuses the
  pattern feature-developer-v7 already uses for task/handoff files; keeps the
  distributed system prompt smaller (KIT-ADR-0001).
- **Cons**: cannot localize frontmatter (model/tools) this way; adds one read
  step; depends on agents being *disciplined* to read the file (a convention
  to enforce, like the `## Target Repository` rule in KIT-ADR-0024 §2).
- **Sub-choice**: high-level/topology context can stay in `CLAUDE.md` (already
  injected); agent-specific depth goes in `.kit/PROJECT-CONTEXT.md`. Avoid
  duplicating across the two.

### Option B — Render-on-pin (codegen)

The plugin ships a template with placeholders; a project-owned values file
(`.kit/agent-locals.yml`) plus a render script writes the filled agent into
`.claude/agents/` at install/upgrade time. Upgrade = bump pin, re-render.

- **Pros**: self-contained agent files (nice to read/diff); can localize
  frontmatter too; the render is a clean, testable transform.
- **Cons**: a build step and a generated artifact (commit vs gitignore
  question); the rendered file in `.claude/agents/` shadows the plugin's
  namespaced agent, partially defeating distribution; another script to keep
  in manifest sync.

### Option C — 3-way merge (vendored dependency model)

Treat the plugin agent as upstream; the project keeps a filled copy; on
upgrade, 3-way merge (base, new-upstream, local) like a vendored lib.

- **Pros**: agent files stay self-contained and fully localizable.
- **Cons**: Markdown 3-way merges conflict constantly; reintroduces exactly
  the per-repo-copy drift KIT-ADR-0024 removed; highest ongoing cost.
  **Rejected.**

### Option D — Status quo (filled forks per project)

Each project fills the extension points in a local copy. **Rejected** — this
*is* the drift problem; it is what KIT-0030 set out to undo.

## Decision (proposed — revised after evaluator review)

Adopt **Option A (runtime context file) as the default**, backed by a
**single structured source of truth** and an enforced read convention. Use
**Option B (render-on-pin) as the implementation of the escape hatch only**,
so frontmatter localization is generated from the same source of truth rather
than hand-forked. (This A+B synthesis is the central revision from review —
see Review Outcome.)

1. **Single source of truth — structured, not prose.** Project specifics live
   in a machine-readable `.kit/context/project.yml` with a kit-shipped JSON
   Schema and a mandatory `schemaVersion` field. A `./scripts/core/project
   validate-context` command (and a preflight/CI check) validates it. Prose
   commentary may accompany fields but the contract is the schema. (Replaces
   the earlier prose `.kit/PROJECT-CONTEXT.md`.)
2. **Interface — enforced, not just conventional.** Every distributed agent
   that needs specifics carries a standard `## Phase 0: Load Project Context`
   block instructing it to read `.kit/context/project.yml`. Enforcement
   (mirroring the KIT-ADR-0024 §2 `## Target Repository` check, which decayed
   precisely because it was *not* enforced):
   - a lint/preflight check asserts every distributed agent contains the
     Phase-0 block (static check on `.claude/agents/` + plugin agents), and
   - a check asserts `.kit/context/project.yml` exists and validates when the
     project enables the plugin agents, and
   - agents emit a runtime warning when the file is missing or fails schema
     validation.
3. **Explicit ownership boundary** (field → home), to prevent the split-brain
   all three reviewers flagged:

   | Information | Home | Validated? | Read by |
   |---|---|---|---|
   | Topology, target repo, project rules, identity | `CLAUDE.md` | yes (KIT-ADR-0024 §2) | every session (auto-injected) |
   | Tech stack, task-ID prefix, content language, local test/lint commands, Serena project name, stack-specific footguns | `.kit/context/project.yml` | yes (schema) | agents that declare Phase 0 |
   | Defensive-coding patterns | `.kit/context/patterns.yml` | existing | all agents |

   Topology/layout is **not** duplicated into `project.yml`; agents read it
   from `CLAUDE.md` (already injected). `project.yml` carries operational
   config only.
4. **Escape hatch — render-on-pin, time-boxed, frontmatter-only.** A project
   needing different *frontmatter* (e.g. `model`, `disallowedTools`) does
   **not** hand-fork. Instead `validate-context`/a render step emits a thin
   local agent from `project.yml` values + the pinned plugin body, carrying:
   - a generated header: `# GENERATED override — frontmatter only; re-run
     render after a plugin upgrade. Do not edit the body.`
   - a `## Provenance` note recording the override and the plugin pin, and
   - a **required tracking issue** so the override is scheduled to become a
     first-class `project.yml` field if it recurs.
   The escape hatch may change frontmatter only, never workflow/behavior; a
   preflight check flags any escape-hatch agent whose body has drifted from
   the pinned plugin body.
5. **Distribution stays plugin + manifest.** The agent body ships via the
   plugin (KIT-ADR-0024 §3). `.kit/context/project.yml` is project-owned and
   not distributed; its **JSON Schema, the `project.yml` template, the
   `validate-context` command, the Phase-0 lint, and the render step** ship
   with the kit and flow downstream via the manifest (KIT-ADR-0022). Bootstrap
   generates the initial `project.yml`.

Status **Proposed** — revised once after a three-evaluator arch review (all
REVISION_SUGGESTED; see Review Outcome). Pending: user sign-off and one
proof-of-concept (retrofit `feature-developer-v7` with a Phase-0 block + a
real `.kit/context/project.yml` in label-maker, validated end-to-end).

## Review Outcome (2026-06-23)

Three architecture evaluators across three model families reviewed the
original (prose-file) draft; **all three returned REVISION_SUGGESTED** with
strongly convergent findings. Logs:
`.adversarial/logs/KIT-ADR-0025-arch-input--{arch-review,arch-review-fast-v2,mistral-arch}.md`.

Convergent findings, and how this revision answers each:

1. **Weakly-typed Markdown schema** (all 3) → structured `project.yml` + JSON
   Schema + `schemaVersion` + `validate-context` (Decision 1).
2. **Blurry CLAUDE.md ↔ context-file boundary** (all 3) → explicit ownership
   table; topology stays in CLAUDE.md, not duplicated (Decision 3).
3. **Convention-only Phase-0 read will decay** (all 3, citing the §2
   precedent) → lint + preflight + runtime warning (Decision 2).
4. **Escape hatch reintroduces drift** (all 3) → render-on-pin generation,
   frontmatter-only, required tracking issue, drift-detection preflight
   (Decision 4).
5. **No schema-versioning/deprecation strategy** (o3, mistral) → mandatory
   `schemaVersion` + deprecation window (Decision 1).
6. **A and B are not mutually exclusive — B can implement A's escape hatch**
   (arch-review-fast-v2) → adopted as the core synthesis: structured config
   is the single source of truth; the behavioral 95% is read at runtime
   (no build step), and the rare frontmatter case is *generated*, not forked.

Residual decision deferred to the user (see Open Question 1).

## Consequences

### Positive

- Plugin upgrades become a pin bump with no merge; localization lives in one
  small project-owned file.
- The distributed agent body is genuinely project-agnostic — the class of bug
  BugBot caught (hardcoded Serena project) becomes structurally impossible.
- Smaller distributed system prompts (KIT-ADR-0001), since specifics are
  loaded on demand rather than inlined.
- One mechanism across all shared agents.

### Negative

- Relies on a convention (agents must read the context file) that needs the
  same kind of validation the `## Target Repository` section gets — otherwise
  it decays. A preflight/lint check should assert the file exists when a
  project enables the plugin agents.
- Frontmatter localization is second-class (escape hatch only).
- One more well-known path/schema to teach and to keep stable.

### Neutral

- The ownership boundary across `CLAUDE.md`, `.kit/context/project.yml`, and
  `.kit/context/patterns.yml` (Decision 3) must be taught and lint-enforced;
  drawn cleanly it dedupes, drawn loosely it confuses.
- This adds kit-side machinery (JSON Schema, `validate-context`, Phase-0 lint,
  render step) flowing through the manifest. That is real surface area, but it
  is upstream-owned and shared, not per-project.
- The render step exists only for the frontmatter escape hatch; the common
  case has no build step.

## Open Questions

1. **(For the user — the remaining fork.)** The behavioral 95% is settled
   (runtime read of `project.yml`). For the rare frontmatter case, this ADR
   proposes render-on-pin. The alternative is to make render-on-pin the
   mechanism for *all* localization (generate the whole agent from
   `project.yml` + plugin body), giving fully self-contained, diffable agent
   files at the cost of a build step on every project. Pick: **runtime-read
   default + render only the escape hatch** (proposed), or **render
   everything**.
2. Resolved by review: structured `.kit/context/project.yml`, not prose.
3. Resolved by review: enforced via lint + preflight + runtime warning.
4. Resolved by review: escape hatch is generated, frontmatter-only,
   tracking-issue-gated, drift-detected.

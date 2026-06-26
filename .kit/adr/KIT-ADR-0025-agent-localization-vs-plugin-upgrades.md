# KIT-ADR-0025: Localizing Plugin-Distributed Agents Without Losing Upgrades

**Status**: Accepted
**Date**: 2026-06-23 (slimmed 2026-06-26)
**Author**: Claude Code + User
**Supersedes**: None
**Related**: KIT-ADR-0024 (plugin/manifest distribution; §3 is the plugin
channel this refines), KIT-ADR-0001 (system-prompt size), KIT-ADR-0022
(manifest sync ownership), KIT-0030 (the migration that surfaced this),
`docs/PLUGIN-UPGRADE-GUIDE.md` (the operational runbook this ADR backs)

## Context

KIT-ADR-0024 §3 made the `agentive-workflow` plugin the distribution channel
for shared agents (`feature-developer-v7`/`-v6`, `code-reviewer`,
`ci-checker`). KIT-0030 shipped that plugin (v1.1.0) and migrated the first
consumer (label-maker-planning), deleting the local agent copies in favor of
the namespaced plugin versions.

That migration exposed a structural tension. A shared agent definition is
**two things with different lifecycles fused into one Markdown file**:

1. **Workflow body** — phases, gates, the review/CI loop, shell rules.
   Plugin-owned; the whole point of distribution is that projects *receive
   upgrades* to this.
2. **Project specifics** — tech stack, task-ID prefix, repo layout/topology,
   local test/lint commands, stack-specific footguns, the Serena project to
   activate. Project-owned; these *must survive* a plugin upgrade.

If those two were genuinely fused in the file, a project could not take a
workflow upgrade without clobbering its localization. The resolution below is
that they need not be fused: the specifics are read at runtime from files the
project already owns, so the distributed body can carry none of them.

### Evidence the tension is real

- `feature-developer-v7`/`-v6` ship as **unfilled templates** (ACME-NNNN /
  EXTENSION-POINT placeholders). KIT-0030 deliberately distributed the
  unfilled body because the filled-for-the-kit copy would be wrong everywhere
  else.
- BugBot (KIT-0030, PR #3) caught the distributed `code-reviewer` hardcoding
  `mcp__serena__activate_project("agentive-starter-kit")` and `ci-checker`
  validating against the planning repo's origin — project specifics that had
  leaked into a to-be-distributed agent. Both were genericized in `7bf230a`.
- The label-maker migration pointed its primary-implementation-agent
  recommendation at the plugin's **unfilled** `feature-developer-v6`, and it
  worked — because the agent reads the task spec and `CLAUDE.md` at runtime.
  That runtime read is the mechanism this ADR makes explicit.

### How Claude Code loads agents (the one hard constraint)

A Claude Code agent's `.md` file **is** its system prompt, loaded statically at
launch. No `@include`, no inheritance, no frontmatter templating. This splits
localization into two classes:

- **Behavioral context** (stack, conventions, commands, layout, which project
  to navigate) — loadable at runtime as an early agent action.
- **Structural config** (the `model:` pin, `disallowedTools`, other
  frontmatter) — must be in the file at launch.

For the agents in scope the localization is **~95% behavioral**. Frontmatter
localization (a project wanting a different model) is the rare case.

### `CLAUDE.md` is already injected

A project's `CLAUDE.md` is loaded into every session automatically — its
`## Target Repository` / project-rules sections are present with no read step.
The deeper agent-specific context (stack footguns, the exact local test loop)
is what the old extension points carried; an agent can read it at runtime from
`CLAUDE.md` and the task spec.

## Decision

Distribute the **generic agent body via the plugin**; let **project specifics
live in files the project already owns and reads at runtime**. No new schema,
config file, render step, or lint is introduced.

1. **The distributed body carries no project specifics.** Plugin agents are
   project-agnostic. The class of leak BugBot caught (hardcoded Serena project,
   repo-specific origin checks) is treated as a distribution bug, not a feature
   to parameterize.
2. **Localization is runtime-read, from existing homes.** Agents pick up their
   specifics where the project already keeps them:

   | Information | Home | How the agent gets it |
   |---|---|---|
   | Topology, target repo, project rules, identity | `CLAUDE.md` | auto-injected every session |
   | Tech stack, task-ID prefix, local test/lint loop, stack footguns | `CLAUDE.md` + the task spec | read at runtime (early agent action) |
   | Defensive-coding patterns | `.kit/context/patterns.yml` | read at runtime (existing convention) |

   This is already how `feature-developer-v7` operates; the ADR ratifies it
   rather than inventing a new `project.yml` interface.
3. **The rare frontmatter case stays a local agent.** A project needing
   different frontmatter (e.g. a `model:` pin) keeps that agent as a small
   **local** definition in `.claude/agents/` rather than consuming the plugin
   copy. On a model rollout the upgrader rewrites those local pins
   (PLUGIN-UPGRADE-GUIDE §4). No generated/render artifact.
4. **Upgrades preserve local by construction.** Bumping the plugin pin replaces
   only the plugin body; nothing project-owned is touched. The mechanics —
   refresh marketplace, `/plugin update`, reconcile renamed artifacts, refresh
   local `model:` pins, restamp `## Provenance` — live in
   `docs/PLUGIN-UPGRADE-GUIDE.md` and will be automated by the upgrader agent.
5. **Distribution stays plugin + manifest.** The agent body ships via the
   plugin (KIT-ADR-0024 §3); scripts via the manifest (KIT-ADR-0022); topology
   via `CLAUDE.md`. Three separate upgrade surfaces, not blurred.

### Why not the structured-config machinery

An earlier draft of this ADR proposed a structured `.kit/context/project.yml`
with a JSON Schema, `schemaVersion`, a `validate-context` command, a Phase-0
read-the-context lint, and a render-on-pin escape hatch — and was reviewed by
three architecture evaluators (all REVISION_SUGGESTED; logs under
`.adversarial/logs/KIT-ADR-0025-arch-input--*.md`). That apparatus exists to
make a *convention* enforceable across *many independent consumers who will
not read the guide*. **These are all the same owner's projects** (a handful of
repos, one careful operator). In that setting the schema/lint/render cost
exceeds its benefit: convention + the upgrade guide + the upgrader agent are
sufficient, and the runtime read already happens without enforcement. The
heavy version is the right design **if and when** the kit is distributed to
third parties — recorded here as the revisit trigger, not adopted now.

## Consequences

### Positive

- Plugin upgrades are a pin bump with no merge; localization needs no new file.
- The distributed body is genuinely project-agnostic — the hardcoded-Serena
  class of bug becomes a reviewable distribution defect.
- Smaller distributed system prompts (KIT-ADR-0001): specifics are read on
  demand, not inlined.
- One mechanism across all shared agents; zero new kit-side machinery to keep
  in manifest sync.

### Negative

- Relies on agents actually reading `CLAUDE.md`/task spec at runtime — a
  convention with no automated enforcement. Acceptable at single-owner scale;
  becomes a real gap if the kit is ever distributed externally (the revisit
  trigger above).
- Frontmatter localization is handled by keeping a local agent, which sits
  outside the plugin upgrade flow and must be re-pinned by the upgrader on a
  model rollout.

### Neutral

- The ownership boundary across `CLAUDE.md`, the task spec, and
  `patterns.yml` must stay clean so specifics are not duplicated.

## Open Questions

1. **Revisit trigger.** If the kit is distributed beyond the author's own
   projects, re-open the structured-config + enforcement design (the reviewed
   heavy version) — at that point convention-only decay becomes the dominant
   risk.
2. Proof-of-concept still wanted: retrofit/confirm `feature-developer-v7`
   reads its specifics from `CLAUDE.md` + task spec end-to-end in label-maker.
   Tracked under KIT-0030.

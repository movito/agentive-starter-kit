# KIT-0030: Consolidate Shared Agents/Skills/Commands into the agentive-workflow Plugin (Sync Phase 2)

**Status**: In Progress
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 2-3 sessions
**Created**: 2026-06-12

## Related Tasks

**Parent**: KIT-ADR-0024 (Cross-Repo Topology Default + Drift Control)
**Depends On**: KIT-0029 (canonical v7 must exist before it can be distributed)
**Related**: KIT-0026 (manifest sync — kit-internal channel), KIT-0027
(first-class cross-repo config — preflight check here is a thin slice of it)

## Overview

Per KIT-ADR-0024 §3, shared skills, workflow commands, and agent definitions
distribute to *projects* via the `agentive-workflow` plugin
(movito/agentive-skills), versioned with semver and pinned per project.
label-maker-planning already consumes five skills this way; this task extends
the plugin to agents and commands and migrates the active projects.

**Channel boundaries (do not blur):**

| Channel | Scope | Carries |
|---------|-------|---------|
| `agentive-workflow` plugin | Consumer/planning projects | skills, commands, agents |
| `.core-manifest.json` sync (KIT-0026) | The 4 kit repos | scripts, plus kit-internal copies of the same artifacts |

KIT-0026 remains valid for kit-to-kit sync; this task is the outbound
project channel. If maintaining both proves redundant in practice, a future
ADR can consolidate — out of scope here.

## Requirements

### 1. Spike: verify plugin agent support (gate for the rest)

Claude Code plugins demonstrably ship skills (label-maker). Verify agents:

1. Add one trivial agent to a test branch of movito/agentive-skills
2. Enable in a scratch project; confirm the agent appears in the Agent tool's
   subagent list and is invokable
3. Confirm namespacing behavior (`agentive-workflow:agent-name` vs flat).
   The spike's output MUST include: (a) the definitive invocation convention
   per artifact type (skill, command, agent), and (b) a checklist of every
   location where invocation patterns appear and may need updating — agent
   definitions that invoke skills by name, launcher scripts
   (`.kit/launchers/`, `agents/launch`), task-starter templates, workflow
   docs, and CLAUDE.md examples. This checklist becomes the per-project
   migration guide used in Requirement 5
4. **If agents cannot ship via plugin**: stop, record findings, and fall back
   to manifest distribution for agents (KIT-0026 mechanism) while keeping
   skills/commands in the plugin. Update KIT-ADR-0024 §3 with an addendum.

### 2. Inventory and classify

Across the active 4 (this kit, suwinex-planning, label-maker-planning,
moss-skolemusikkorps): list every skill, command, and agent; classify
shared vs project-specific; note local divergences from plugin versions.
Output: a table in `.kit/context/` (inventory artifact, committed).

### 3. Define and release plugin contents

1. Plugin gets: shared skills (existing 5 + any newly promoted), workflow
   commands (`/retro`, `/triage-threads`, `/check-ci`, `/preflight`, etc.),
   and canonical agents (feature-developer-v7 from KIT-0029, code-reviewer,
   ci-checker as applicable)
2. Tag a semver release of movito/agentive-skills
3. Document the pin-and-upgrade procedure in the plugin README

### 4. Add the Target Repository preflight check

A check (in `/preflight` and/or `scripts/core/ci-check.sh`) that **fails**
when a repo declares the cross-repo pattern (mentions of target repo in
README/agents/commands) but CLAUDE.md lacks a parseable `## Target
Repository` section. Warn-only when CLAUDE.md has the section but the path
doesn't exist locally (planning repo must stay usable without the target
checked out — per KIT-0027 §5).

### 5. Migrate projects, lowest risk first

Order: label-maker-planning (already plugin-enabled) → suwinex-planning →
moss-skolemusikkorps. For each:

1. Pin the plugin release in `.claude/settings.json`
2. Delete local copies of artifacts now provided by the plugin (verify
   identical-or-superseded first; preserve genuine local divergences as
   project-specific overrides and note them in the inventory)
3. Update CLAUDE.md `## Provenance` with the plugin pin
4. Run one real task end-to-end in that project before declaring the
   migration done

## Acceptance Criteria

- [ ] Spike outcome documented (plugin agent support: yes/no + namespacing)
- [ ] Inventory artifact committed to `.kit/context/`
- [ ] Plugin release tagged (semver); README documents pin/upgrade flow
- [ ] Preflight check implemented with fail/warn semantics as specified
- [ ] All three projects migrated, local duplicates deleted, provenance
      updated, one end-to-end task run in each
- [ ] KIT-0026 relationship stated in CHANGELOG entry (channels coexist)

## Risks

### Risk 1: Plugin cannot ship agents
**Likelihood**: Medium (unverified capability)
**Impact**: Medium
**Mitigation**: Spike is the first step and gates the rest; fallback path
defined (Requirement 1.4).

### Risk 2: Breaking change hits all pinned projects on upgrade
**Likelihood**: Low (pins prevent implicit upgrades)
**Impact**: High if pins are ignored
**Mitigation**: Per-project pins are mandatory; upgrade is a deliberate
per-project action with the end-to-end task run as its gate.

### Risk 3: Local divergences silently lost during de-duplication
**Likelihood**: Medium
**Impact**: High (this is how v7 almost stayed stranded)
**Mitigation**: Inventory step explicitly diffs local copies against plugin
versions before any deletion; divergences either get promoted upstream or
recorded as overrides.

## Notes

- moss-skolemusikkorps stays a monorepo for now (topology decision
  deferred); plugin migration applies regardless of topology.
- Skill namespacing changes (`bot-triage` → `agentive-workflow:bot-triage`)
  may require updating agent definitions that invoke skills by name — check
  during the spike.
- Evaluator finding (arch-review-fast, 2026-06-12): the manual per-project
  migration doesn't scale past ~10 consumers. Accepted — current scope is 3
  migrations and the manual end-to-end gate is deliberate risk mitigation.
  If the consumer count grows materially, a follow-up ADR for automated
  upgrade tooling is the trigger, not more manual process.

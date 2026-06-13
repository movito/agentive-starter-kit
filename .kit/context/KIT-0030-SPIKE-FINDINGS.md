# KIT-0030 Spike Findings: Plugin Agent + Command Support

**Date**: 2026-06-13
**Author**: feature-developer-v7
**Verdict**: Plugins ship agents and commands. **No fallback needed** —
KIT-ADR-0024 §3 stands as written.

## Method

- Cloned `movito/agentive-skills` to `~/Github/agentive-skills`, local
  branch `spike/KIT-0030-plugin-agents` (never pushed)
- Added a trivial probe agent (`agents/spike-probe.md`) and probe command
  (`commands/spike-probe-command.md`) to `plugins/agentive-workflow/`
- `claude plugin validate` passed; installed via a local-directory
  marketplace into a scratch project (`/tmp/kit-0030-spike`)
- Verified registration and invocation headlessly (`claude -p`)

## Results

| Probe | Result |
|-------|--------|
| Agent appears in Agent tool subagent list | YES — as `agentive-workflow:spike-probe` |
| Agent invokable via `subagent_type` | YES — returned its probe string verbatim |
| Command registered | YES — as `agentive-workflow:spike-probe-command` |
| Existing 5 skills | Registered as `agentive-workflow:<skill-name>` |

## Invocation conventions (definitive)

All plugin artifact types are namespaced with the plugin name:

| Artifact | Plugin location | Invocation in consumer project |
|----------|-----------------|--------------------------------|
| Skill | `skills/<name>/SKILL.md` | `Skill("agentive-workflow:<name>")` / `/agentive-workflow:<name>` |
| Command | `commands/<name>.md` | `/agentive-workflow:<name>` |
| Agent | `agents/<name>.md` | `Agent(subagent_type="agentive-workflow:<name>")` |

A local copy in `.claude/{skills,commands,agents}/` keeps its **flat** name
and coexists with the namespaced plugin version. **Deleting the local copy
removes the flat name** — every flat reference must then be updated to the
namespaced form, or it silently stops resolving.

## Version / pin mechanics (from docs + observed cache behavior)

- The plugin's version (`plugin.json` `version`, falling back to the
  marketplace entry, falling back to git SHA) is the **cache key**.
  Explicit semver = the pin: consumers only receive changes when the
  version field is bumped, regardless of new commits.
- `enabledPlugins` in `.claude/settings.json` is boolean; the effective
  per-project pin is the installed cached version. Record it in
  CLAUDE.md `## Provenance` (per KIT-ADR-0024 §4).
- Cache lives at `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`.
  Re-publishing the same version number does NOT propagate (observed:
  cache reused at identical version).

## Migration checklist — locations where flat invocations must change

Built from a 4-repo grep (2026-06-13). Per project, when local copies are
deleted in favor of the plugin:

1. **Agent definitions** (`.claude/agents/*.md`) — reference commands
   (`/preflight`, `/retro`, `/triage-threads`, `/check-ci`, `/wrap-up`,
   `/babysit-pr`, `/check-bots`, `/wait-for-bots`, `/commit-push-pr`,
   `/start-task`, `/check-spec`, `/status`) and skills by flat name
2. **Command definitions themselves** (`.claude/commands/*.md`) —
   cross-reference each other (e.g., `babysit-pr` → `/triage-threads`)
3. **Skill bodies** (`.claude/skills/`, `.kit/skills/`) — e.g.,
   `review-handoff` references `/preflight`
4. **Launcher scripts** — `.kit/launchers/{launch,onboarding,preflight}`
   (kit, suwinex, label-maker) and moss's equivalent — embed agent names
5. **Task-starter templates** — `.kit/templates/TASK-STARTER-TEMPLATE.md`
   (kit), `.claude/agents/TASK-STARTER-TEMPLATE.md` (moss) — "Recommended
   agent" footers
6. **CLAUDE.md** — workflow examples and agent tables in all four repos
7. **Workflow docs** — `.kit/context/workflows/*.md` (esp.
   `REVIEW-FIX-WORKFLOW.md`), `.kit/docs/*`, review-starter templates
8. **Handoff files for in-flight tasks** — only the active ones;
   historical handoffs/retros are records, do not rewrite

**Non-goals**: historical artifacts (`.kit/context/` retros, reviews,
done-task handoffs, archived tasks) keep flat names — they are records.

## Consequence for plugin authoring

Plugin-shipped artifacts that reference each other (e.g.,
feature-developer-v7 invoking `/preflight`) must use the namespaced form
**inside the plugin copy**, because consumer projects will not have flat
names after de-duplication. The kit's local authoring copies keep flat
names. This makes the kit→plugin sync a transform, not a copy:

```
s|/(retro\|preflight\|triage-threads\|check-ci\|wrap-up\|babysit-pr\|check-bots\|wait-for-bots\|commit-push-pr\|start-task\|check-spec\|status)\b|/agentive-workflow:\1|g
```

(plus the same for `Skill("...")` and `subagent_type` references).
Document the transform in the plugin README; automate later if churn
warrants it.

## Spike scaffolding state

- Local clone `~/Github/agentive-skills` on branch
  `spike/KIT-0030-plugin-agents` (local only; reused for release prep)
- User-level marketplace `agentive-skills` temporarily points at the
  local clone — **must be restored to `movito/agentive-skills` (github)**
  before migrations are declared done
- Probe files were removed from the live plugin cache after the test
- Scratch project `/tmp/kit-0030-spike` is disposable

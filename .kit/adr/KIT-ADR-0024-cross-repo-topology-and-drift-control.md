# KIT-ADR-0024: Cross-Repo Planning/Code Split as Default Topology, with Drift Control

**Status**: Proposed
**Date**: 2026-06-12
**Author**: Claude Code + User
**Supersedes**: None
**Related**: KIT-ADR-0022 (Manifest-Based Sync Ownership), KIT-ADR-0023 (Builder/Project
Separation), KIT-0027 (cross-repo first-class support), `docs/CROSS-REPO-PATTERN.md`
(canonical; originated in ixda-services-2.0 as `2026-04-16-cross-repo-agent-pattern.md`,
diverging copies in suwinex-planning and label-maker-planning)

## Context

A survey of ~20 active projects (2026-06-12) shows three generations of the
planning/code topology, each bootstrapped from whatever the kit looked like at
clone time:

| Gen | Period | Layout | Examples |
|-----|--------|--------|----------|
| 1 | Nov 2025 – Mar 2026 | Monorepo: `delegation/tasks/` + `.agent-context/` alongside code | ombruk, thematic-2, gas-taxes, wcag-intro, moss-skolemusikkorps |
| 2 | Apr 2026 | `.kit/` layout; cross-repo pattern invented | ixda-services-2.0 → ixda-services |
| 3 | May 2026 | Cross-repo pair + shared skills via `agentive-workflow` plugin | suwinex-planning/-code, label-maker-planning/-code |

### Evidence that the split works

- **suwinex** (7 retros): 0 regressions across all PRs, all bot threads resolved,
  planning repo stays on `main` permanently while the code repo runs feature
  branches. Process improvements (new agents, command fixes) landed *during*
  in-flight feature work with zero interference.
- **suwinex-code needs no `.coderabbitignore`** — there is no planning noise to
  suppress. Monorepos (e.g., moss-skolemusikkorps) each need a hand-adapted
  ignore file to keep review bots away from task specs and handoffs.
- Bot/evaluator/CI review surface in the code repo is exactly the shipping code.

### Evidence of drift (the actual problem)

The pain is not monorepo-vs-split. It is that **the kit is copied at bootstrap
time and then evolves per-project, with no flow back upstream**:

1. **Improvements strand where they were invented.** feature-developer-v7
   (inline CI polling via ScheduleWakeup) exists only in moss-skolemusikkorps.
   suwinex and label-maker carry v6. The starter kit itself was last updated
   2026-04-25 and has neither.
2. **Conventions decay within weeks.** The machine-readable `## Target
   Repository` section in CLAUDE.md — which all cross-repo slash commands
   depend on for auto-detection — was silently dropped in label-maker-planning
   (May 2026), the newest project, one month after the convention was invented.
   The split is declared only in README prose there.
3. **Naming churn.** `delegation/tasks/` vs `.kit/tasks/`; `.agent-context/`
   vs `.kit/context/`; repo suffixes `-web` vs `-code` vs `-2.0`. Each project
   freezes a different snapshot of the vocabulary.
4. **Aborted migrations leave debris.** moss-skolemusikkorps-web is an empty
   repo (zero commits) from an abandoned split attempt.
5. **The pattern doc itself forks.** ixda-services-2.0, suwinex-planning, and
   label-maker-planning each carry diverging copies of the cross-repo pattern
   document.

## Decision

### 1. Default topology: cross-repo split for production projects

Use the **planning/code pair** whenever a project has CI, review bots,
adversarial evaluators, or a deployable artifact. Stay **monorepo** (planning
folder inside the project) for one-offs, content/teaching sites, and projects
expected to stay under ~10 tasks. These criteria restate the "When This
Pattern Fits" section of the cross-repo pattern doc, now elevated to the
default rule rather than an option.

Naming and layout are fixed:

- Repo names: `<project>-planning` and `<project>-code`
- Local checkout: sibling directories under the same parent
- Planning repo commits everything to `main`; code repo uses
  `feature/<TASK-ID>-*` branches

### 2. `## Target Repository` in CLAUDE.md is mandatory and validated

The machine-readable section is the single source of truth for cross-repo
routing:

```markdown
## Target Repository

- **Path**: `../<project>-code`
- **GitHub**: <owner>/<project>-code
```

A preflight/bootstrap check MUST fail when a planning repo declares the
cross-repo pattern (in README, agents, or commands) but CLAUDE.md lacks this
section. Prose conventions decay; validated conventions survive (lesson from
label-maker).

### 3. Shared machinery distributes via plugin + manifest, not per-repo copies

- **Skills, workflow commands, agent definitions**: distributed through the
  `agentive-workflow` plugin (movito/agentive-skills), versioned with semver,
  enabled per project via `.claude/settings.json`. Per-repo copies of these
  files are deprecated; projects delete local copies as they adopt the plugin.
- **Scripts** (`scripts/core/`): continue under the tiered manifest sync
  (KIT-ADR-0022).
- A planning repo's own content shrinks to: `CLAUDE.md`, task specs, context
  (handoffs/retros/reviews), and project ADRs. Everything else is upstream-owned.

This is the completion of the direction Gen 3 started: the smaller the
per-project copy, the smaller the surface that can drift.

### 4. Provenance is stamped with versions

The kit carries a semver (already in `pyproject.toml`/`scripts/core/VERSION`).
Every bootstrapped planning repo records, in a `## Provenance` section of
CLAUDE.md:

- kit version at bootstrap (e.g., `kit-version: 0.4.0`)
- bootstrap date and source (kit clone, or forked from another planning repo)
- plugin version pinned (e.g., `agentive-workflow@1.2.0`)

This makes "which projects are behind" a grep, not an archaeology session.
Upgrades are deliberate per-project actions (bump pin, run reconfigure), never
implicit.

### 5. One canonical pattern doc

The starter kit's `docs/CROSS-REPO-PATTERN.md` is the single canonical copy
of the cross-repo pattern document. Project repos link to it; existing forked
copies (ixda-services-2.0, suwinex-planning, label-maker-planning) are
replaced with a link plus any project-specific deltas. Lessons learned in
projects are PR'd back to the canonical doc (same promotion flow as
KIT-ADR-0022 commands).

## Consequences

### Positive

- Code repos stay clean: bots, evaluators, and human reviewers see only
  shipping code; no noise-suppression config needed.
- Process can improve mid-flight: planning `main` and code feature branches
  never contend.
- Drift becomes measurable (version stamps) and small (thin per-project copies).
- New projects bootstrap to a known-good, validated state instead of a
  snapshot-plus-vibes.

### Negative

- A breaking plugin or kit release can affect all active projects at once.
  Mitigation: per-project version pins; upgrades are opt-in and deliberate.
- Two repos per production project: task lifecycle must touch both (no atomic
  cross-repo commits). Mitigation: `/wrap-up` handles both sides; accept and
  periodically reconcile residual drift, per the pattern doc.
- Existing Gen-1 monorepos (e.g., moss-skolemusikkorps) don't automatically
  comply. Retrofitting is optional per project; the rule applies to new
  projects and to migrations done for their own reasons.

### Neutral

- The plugin and the manifest are two distribution channels with distinct
  scopes (skills/commands/agents vs scripts). Consolidating to one channel is
  possible later but not required by this ADR.
- KIT-ADR-0023's `.kit/` boundary work remains valuable independently: in the
  split topology the planning repo *is* mostly builder layer, which makes the
  eventual workspace extraction (0023 §6) even more mechanical.

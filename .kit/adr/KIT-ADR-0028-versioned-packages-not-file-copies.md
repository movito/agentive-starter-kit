# KIT-ADR-0028: Distribute the kit as versioned packages — retire copy-based sync

**Status**: Proposed (operator direction stated 2026-08-05; acceptance =
operator sign-off on this document)
**Date**: 2026-08-05
**Deciders**: Fredrik Matheson (operator), planner-f5
**Extends**: KIT-ADR-0025 (plugin agents project-agnostic, specifics
read at runtime)
**Supersedes on acceptance**: KIT-ADR-0026 (pull-based consumer copy
sync) — after migration completes
**Consistent with**: KIT-ADR-0027 (lean, language-agnostic kit)
**Evaluation**: arch-review-fast APPROVED 2026-08-05, first pass
(`.adversarial/logs/KIT-ADR-0028-versioned-packages-not-file-copies--arch-review-fast.md`)

## Context

Operator, 2026-08-05, after a week in which one intake exercise surfaced
~15 machinery defects:

> "It seems inefficient for us to invent our own package manager. If we
> could use PyPI to install and update adversarial-workflow, and use a
> github repo to update the adversarial-evaluator-library, then I don't
> see why we want to make everything so complicated here. [...] What I
> was looking for was a way to get the agent definitions, the scripts,
> and so on to be as easy to update as adversarial-workflow."

The diagnosis behind that statement, verified against the backlog: the
kit distributes its machinery as **file copies** — export/rsync into
every consumer repo — and therefore maintains a homegrown package
manager made of manifests, KIT-LOCAL marker regions, sync engines,
version-skew doctor checks, and an upgrade guide. Roughly two-thirds of
the open backlog is the maintenance bill for that machinery, not value
for any user project: sync tasks (KIT-0026/0045/0061/0063), marker
drift (KIT-0051), competing install stories (KIT-0087), agent-contract
propagation across variant copies (KIT-0088), portability fixes
re-shipped into every scaffold (KIT-0080).

Meanwhile the kit's own dependencies demonstrate two update models that
require none of this:

- **PyPI package**: `adversarial-workflow` — `uv tool install`, one
  floor pin, upgrades in one command
- **Git repo + ref**: `adversarial-evaluator-library` — cloned by
  `project install-evaluators` at a pinned tag

And the kit has already half-built both halves of the packaged world:
the `agentive-workflow` **plugin** distributes agents/skills/commands
(KIT-0030), the **upgrader agent** moves projects between plugin
versions, the doctor checks the marketplace source is GitHub
(`50-plugin-source.sh`), and KIT-ADR-0025 already requires plugin agent
bodies to be project-agnostic with specifics in repo-owned files. The
copy machinery and the package channels coexist; neither is
authoritative. This ADR makes the package channels authoritative and
retires the copies. The complication was historical accretion — each
sync layer patched the previous one — not necessity.

## Decision

Three channels, all pre-existing distribution mechanisms. No invented
package manager.

### 1. Agents, skills, slash commands → the Claude Code plugin

The `agentive-workflow` plugin (marketplace = a GitHub repo; update =
`claude plugin update`, shepherded by the upgrader agent) becomes the
**only** channel for canonical agent bodies, skills, and commands. The
setup door stops copying `.claude/agents|skills|commands` into new
repos. Per KIT-ADR-0025, project specifics live in files the repo owns
and agents read at runtime (CLAUDE.md, `.kit/context/`) — the KIT-LOCAL
marker seeding inside agent copies retires together with the copies.

### 2. Lifecycle scripts → a PyPI package

`scripts/core/` (project lifecycle, doctor + doctor.d, preflight,
review-input helpers, worktree helper) becomes a versioned Python
package (working name `agentive-kit`, console entry `agentive`),
installed and updated exactly like `adversarial-workflow`:
`uv tool install agentive-kit`. Consumer repos stop carrying script
copies; a one-line `./scripts/core/project` shim may remain one release
for compatibility, then goes. Portability fixes (KIT-0080's class) land
once, in the package, for every project simultaneously.

### 3. Content stays in the repo — it was never the problem

Task specs, `.kit/context/`, ADRs, CLAUDE.md identity, and the pin
file(s) (`.adversarial/config.yml` per KIT-0083's decision) live
per-repo, under git, like any project content. The evaluator library's
git-ref model is unchanged.

**A new project becomes**: folder skeleton + CLAUDE.md + config + two
installs (`claude plugin install`, `uv tool install`) + `agentive
doctor`. The setup door shrinks to exactly that, and the scaffold
acceptance test (KIT-0082) shrinks with it.

## Consequences

**Dissolves or radically shrinks** (dispose at migration, not before):
KIT-0026, KIT-0045, KIT-0061, KIT-0063 (copy-sync machinery — moot);
KIT-0051 (markers persist only in CLAUDE.md); KIT-0088 (one canonical
agent file — a contract is edited once, propagation ceases to exist);
KIT-0087 F2 (the single install path becomes the package's job);
KIT-0082 (acceptance surface collapses to install + doctor).

**Migration is staged, not big-bang**:
1. Publish the packages (plugin already exists; scripts package is new)
2. Switch the door to package-install mode; new projects are born
   packaged
3. Move existing consumers via the upgrader agent
4. Retire the sync machinery and close the dissolved tasks with
   dispositions pointing here

**Costs and risks, stated honestly**:
- PyPI release discipline becomes real work (versioning, changelogs,
  a publish workflow) — but it replaces the sync machinery's larger
  standing cost, and the adversarial-workflow precedent shows the shape
- Fresh installs need network access; air-gapped setup becomes "vendor
  the wheel," which is standard Python practice
- The kit repo remains the development home; contributors' loop is
  unchanged
- In-flight work (KIT-0083, KIT-0080's portable fix) is compatible:
  0083's pin-home and installer consolidation move INTO the package
  later; 0080's one-liner ships now for today's users

**Open questions** (answered during migration, not blockers to
acceptance): final package name; whether the CLI pin is recorded
per-repo (config.yml adjacency) or floats like adversarial-workflow's
floor; release cadence; whether the -f5 agent variants remain separate
files or become a plugin-side model parameter.

## Alternatives considered

- **Status quo** (copy + ADR-0026 sync engine): rejected — the backlog
  composition IS the argument; the maintenance bill compounds with
  every consumer project created.
- **Git submodules** for shared machinery: rejected — detached-HEAD UX,
  poor fit for operator-driven updates, solves neither markers nor
  variants.
- **One mega-plugin carrying the scripts too**: rejected — plugins
  distribute Claude Code surfaces, not arbitrary CLIs; the scripts are
  Python and PyPI is their native channel.

# Fleet Inventory — 2026-09-24

**Author**: planner-f5 session "2026-09-24 P5 Upgrade gestalt"
**Purpose**: Step 1 of the upgrade-architecture arc — ground-truth every
ASK-family project before deciding distribution architecture and the
lightweight-ASK scope (see KIT-0123).
**Method**: read-only scan of `/Users/broadcaster_three/Github/` —
directory markers (`.kit/`, `.kit/tasks/`, `.claude/agents/{feature-developer,planner}.md`,
`## Target Repository` in CLAUDE.md, `.adversarial/`, `scripts/core/project`),
`git log -1` per repo, agent frontmatter (`model:`, `version:`), KIT-LOCAL
marker presence, `agentive-workflow` references in project and user
settings. All rows below are VERIFIED by that scan unless marked
PREDICTED.

## Headline findings

1. **27 ASK-family projects; only 3 active consumers.** Active (≤60
   days): the `ixda-services` split pair (commits 2026-09-24) and
   `design-theory-timeline` (2026-09-04). Warm (~2 months):
   `varv-planning`, `ev-queue-planning`. Everything else is 3–11 months
   dormant.
2. **The plugin is enabled at the USER level** —
   `~/.claude/settings.json` carries `"agentive-workflow@agentive-skills": true`.
   Current plugin agents are available machine-wide in every project.
   Local `.claude/agents/` copies in older projects SHADOW them: those
   projects expose both a stale bare-name agent and the current
   namespaced one.
3. **Lightweight ASK already exists de facto**: the newest projects
   (ixda-services pair) run on user-level plugin + a `.kit/` of
   `context/tasks/templates` + `scripts/core` — no local `.claude/`
   directory at all. Each project generation has carried less ASK than
   the previous one. NOTE (operator correction, 2026-09-24): the
   planning side DOES carry and use `.adversarial/` — the evaluator
   layer is part of the current-gen footprint, not shed weight.
4. **Upgrade for most of the fleet = deletion, not addition**: prune
   shadowing local agent copies (after rescuing genuine customizations),
   refresh the thin `.kit`, record deviations.
5. **Worst-case accretion exists**: `label-maker-planning` carries
   `feature-developer-v3.md`, `-v5.md`, `feature-developer.md` AND the
   plugin — three generations coexisting in one repo.

## Stratum 0 — upstream / infrastructure (not consumers)

| Dir | Last commit | Role |
|---|---|---|
| `agentive-starter-kit` | active | the kit (upstream, single-repo) |
| `agentive-skills` | 2026-08-17 era | plugin marketplace repo |
| `agentive-config` | — | setup-door preset home |
| `adversarial-evaluator-library` | 2026-04-28 | evaluator library upstream (has V1-era agents @ opus-4-5, no markers) |
| `adversarial-workflow` | 2026-04-29 | evaluator infra |
| `dispatch-kit` | 2026-03-21 | ARCHIVED arc (KIT-ADR-0035); agents @ opus-4-6 |
| `ask-worktrees`, `dtl-worktrees`, `ixda-services-worktrees`, `ixda-services-planning-worktrees` | — | worktree containers |

## Stratum A — current-gen consumers (plugin-era, thin `.kit`, no local agents)

| Project | Last commit | Topology | Signals |
|---|---|---|---|
| `ixda-services-planning` | 2026-09-24 | split (planning) | `.kit/` = context/tasks/templates; `.adversarial/` present and IN USE (operator-confirmed); `scripts/core/project` present; **no `.claude/` dir**; rides user-level plugin |
| `ixda-services` | 2026-09-24 | split (code) | `.kit/` only |
| `design-theory-timeline` | 2026-09-04 | single-repo | plugin in project settings.json; `.kit/` = adr/adversarial/context/docs/tasks/templates; scripts/core 4.0.0 (per DTL-0026); fullest current-gen record |

## Stratum B — marker-era consumers (local V2 agents WITH KIT-LOCAL markers, no plugin ref)

| Project | Last commit | Topology | Agents |
|---|---|---|---|
| `varv-planning` (+ `varv-playground`) | 2026-08-04 | split | fd 2.0.0 + planner 2.0.0 @ opus-4-8, markers |
| `ev-queue-planning` (+ `ev-queue`) | 2026-07-29 | split | fd 2.1.1 @ opus-5, planner 2.0.0 @ opus-4-8, markers; also f5 variants, legacy `create-project.md` |

## Stratum C — pre-marker era (wholesale-copied agents, opus-4-6 pins, no markers)

| Project | Last commit | Topology | Notes |
|---|---|---|---|
| `label-maker-planning` (+ `label-maker-code`) | 2026-06-22 | split | opus-4-6 pins; **v3 + v5 + current fd coexist**; plugin ALSO enabled → 4 candidate feature-developers |
| `moss-skolemusikkorps` (+ `-web`) | 2026-06-13 | single (PREDICTED — no split marker found) | opus-4-6; has proj-cli |
| `suwinex-planning` (+ `suwinex-code`) | 2026-06-12 | split | **pre-canonicalization bespoke lineage**: `architect.md`, `onboarding.md`, `feature-developer-v6.md`; no planner.md |
| `ixda-services-2.0` | 2026-05-14 | split-planning marker | opus-4-6; PREDICTED superseded by the new ixda-services pair — confirm before any action |
| `thematic-2` | 2026-03-22 | single | opus-4-6 |
| `research-method-matrix` | 2026-03-18 | single | planner only, opus-4-6 |
| `epistemic-drift` | 2026-03-06 | single | planner only, opus-4-6 |
| `ombruk-v2` | 2026-02-13 | single | opus-4-6 |

## Stratum D — ancient (opus-4-5 / sonnet-4-5 era)

| Project | Last commit | Pins |
|---|---|---|
| `gas-taxes` | 2026-02-03 | opus-4-5 |
| `wcag-intro-v01` | 2026-02-02 | opus-4-5 |
| `agentive-studio` | 2026-02-06 | opus-4-5 |
| `splitarch` | 2026-01-28 | opus-4-5 |
| `ombruk` | 2026-01-26 | opus-4-5 |
| `agentic-lotion-2` | 2025-11-28 | opus-4-5 |
| `agentive-ixd-1` | 2025-11-28 | opus-4-5 |
| `thematic-cuts` | 2025-11-25 | sonnet-4-5 (fd only) |
| `notionally` | 2025-10-25 | fd only, no model pin |

## Non-ASK directories (no kit markers found)

`Aneo`, `a11y-website-v1`, `agent-roles-template`, `agentic-lotion-1`,
`alasdair-macintyre-moral-philosophy-mindmap`, `aneo-common-web`,
`aneo-designsystem`, `docs`, `ev-planner-site`, `ev-queue` (code side —
scanned clean), `gas-taxes` siblings, `how-we-prototype-digital`,
`ixda-emails`, `label-maker-code` (code side), `llm-agents-module-web`,
`llm-demo`, `moss-skolemusikkorps-web`, `passop-studio`,
`prototypes-and-hypotheses`, `roboscribino` (adv dir only),
`suwinex-code` (code side), `thematic`, `thematic-db`,
`varv-playground` (code side).
(Code sides of split pairs correctly carry no planning markers.)

## Implications recorded for the architecture arc

- **Dormant-by-default is the majority tier** (~20 projects). Support
  "unsubscribed" as an explicit, respected state; migrate
  **on revival** (baseline capture at wake), never proactively.
- **Migration debt is owed to ~4 projects**, not 27: varv, ev-queue
  (stratum B — small delta), label-maker, suwinex (stratum C — prune +
  rescue), plus moss/ixda-2.0 only if revived.
- **Agent distribution is already machine-scoped** via the user-level
  plugin; per-project state reduces to `.kit` contents, scripts,
  topology, and recorded deviations. OPEN QUESTION (verify, don't
  assume): whether Claude Code supports per-project plugin *version*
  pinning; if not, "project pinned behind machine baseline" is only
  expressible for `.kit`-side artifacts.
- **Empirical commodity-audit method**: diff what stratum-A projects
  actually use against what the kit ships; what the newest projects
  never needed is a deletion candidate. → KIT-0123.

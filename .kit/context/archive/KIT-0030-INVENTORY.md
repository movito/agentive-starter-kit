# KIT-0030 Inventory: Shared Artifacts Across the Active 4 Repos

**Date**: 2026-06-13
**Author**: feature-developer-v7
**Method**: `md5` checksum + `diff` of every skill / command / candidate
agent across `agentive-starter-kit` (kit), `suwinex-planning` (suw),
`label-maker-planning` (lbl), `moss-skolemusikkorps` (moss), and the
existing plugin (`movito/agentive-skills` @ `agentive-workflow`).

**Headline**: the plugin and **suwinex** carry the newest, cross-repo-aware
generation of nearly every shared artifact; the **kit** and **label-maker**
carry an older v1.0.x generation; **moss** carries old content *plus*
monorepo path coupling (`.agent-context/`, `delegation/tasks/`). This is
KIT-ADR-0024's "improvements strand where invented" in concrete form — and
the reason Risk 3 (silent divergence loss) is real: blindly deleting local
copies in favor of the *current plugin* would be fine, but blindly
canonicalizing from the *kit* would regress suwinex.

## Legend

- **shared** — belongs in the plugin (identical-or-superseded everywhere)
- **shared+override** — plugin-shared, but a project keeps a genuine local
  override (recorded below; preserved per Risk 3)
- **project** — project-specific, never goes in the plugin

---

## Skills

| Skill | kit | suw | lbl | moss | plugin | Canonical | Class |
|-------|-----|-----|-----|------|--------|-----------|-------|
| bot-triage | 1.0.0 | 1.1.0 | — | 1.0.0 | **1.1.0** | plugin | shared |
| pre-implementation | 1.0.0 | 1.2.0 | — | 1.0.0 | **1.2.0** | plugin | shared |
| code-review-evaluator | 1.0.0 | 1.2.0 | 1.0.0 | 1.0.0† | **1.2.0** | plugin | shared+override(moss) |
| review-handoff | = | = | = | path† | **=** | plugin | shared+override(moss) |
| self-review | = | = | = | = | **=** | plugin | shared (identical everywhere) |
| create-task | — | — | lbl-only | — | — | — | project (lbl) |
| create-task-starter | — | — | lbl-only | — | — | — | project (lbl) |

`=` means byte-identical to the plugin copy. `—` means absent.
† moss divergence is **monorepo path coupling only** (`.agent-context/`
vs `.kit/context/`, `delegation/tasks/` vs `.kit/tasks/`) — not content.

**Divergence detail:**
- `bot-triage` 1.1.0 adds: trivial-nit batching exception, and an
  "Evaluator + CodeRabbit convergence" section. Plugin already has it.
- `pre-implementation` 1.2.0 adds steps 10–16 (pytest exit-5, Sanity
  `loadQuery` shape, whole-file pattern audit, shell-recipe testing,
  self-contained snippets, inline-test extraction). Plugin already has it.
- `code-review-evaluator` 1.2.0 adds a **Cross-Repo Mode** section that
  invokes `./scripts/core/prepare-review-input.sh` — a helper that exists
  **only in suwinex** (see Helper-Script Dependencies below).
- `review-handoff`: content identical; moss differs only in `.kit/` vs
  `.agent-context/` paths.

**Layout-coupling caveat (affects moss migration):** the plugin skill
bodies hard-code `.kit/` paths and `scripts/core/` helper paths. moss is a
pre-`.kit/` monorepo. moss therefore either (a) keeps path-divergent skills
as local overrides, or (b) defers until a layout migration (out of scope —
moss stays monorepo per handoff). `self-review` (no path refs) is safe for
moss; `review-handoff` and `code-review-evaluator` are not.

---

## Commands (all in `.claude/commands/`)

| Command | kit | suw | lbl | moss | Canonical | Class |
|---------|-----|-----|-----|------|-----------|-------|
| babysit-pr | a | a | a | — | suw/kit (a) | shared |
| check-bots | 1.0.0 | **1.1.0** | 1.0.0 | 1.0.0 | suw | shared |
| check-ci | 1.0.0 | **1.1.0** | 1.0.0 | 1.0.0 | suw | shared |
| check-spec | a | a | a | b | a | shared+override(moss) |
| commit-push-pr | = | = | = | = | any | shared (identical) |
| preflight | 1.0.0 | **1.1.0** | 1.0.0 | 1.0.0 | suw | shared |
| retro | a | **1.1.0** | a | c | suw | shared+override(moss) |
| start-task | a | a | a | b | a | shared+override(moss) |
| status | a | a | a | b | a | shared+override(moss) |
| triage-threads | 1.0.0 | **1.1.0** | 1.0.0 | 1.0.0 | suw | shared |
| wait-for-bots | = | = | = | = | any | shared (identical) |
| wrap-up | (none) | **1.3.0** | (none) | 1.1.0 | suw | shared+override(moss) |

`a`/`b`/`c` = distinct checksums (relative labels, not versions).

**suwinex carries the cross-repo-aware generation** of check-bots,
check-ci, preflight, retro, triage-threads, wrap-up. Each adds a
`## Step 0 / Cross-repo mode (automatic)` block that reads the
`## Target Repository` section of CLAUDE.md and routes git/gh to the
target repo (via GIT_TARGET/GH_TARGET or `--repo`). **These are the
versions the plugin must ship** — the plugin exists to support the
cross-repo default (KIT-ADR-0024 §1).

**moss overrides** (check-spec, retro, start-task, status, wrap-up) are
monorepo path retrofits, not improvements — superseded by suw, but moss
can't adopt verbatim until layout migration. moss is **missing
`babysit-pr`** entirely.

---

## Agents (candidates for the plugin per spec Req 3.1)

| Agent | kit | suw | lbl | moss | Plugin ships | Notes |
|-------|-----|-----|-----|------|--------------|-------|
| ci-checker | = | = | = | = | **yes** | identical everywhere — clean |
| code-reviewer | a | a | a | b(moss) | **yes** (kit/suw/lbl `a`) | moss = path override |
| feature-developer-v7 | filled | — | — | b | **yes — UNFILLED template** | see below |
| feature-developer-v6 | filled-A | filled-B | filled-C | filled-D | **yes — UNFILLED template** | Opus-class copy of v7 |

**feature-developer-v7/v6 are extension-point templates.** Every existing
copy has its Project Context / Stack Notes **filled** with that repo's
specifics (kit's v7 is filled for the kit). The plugin must ship the
**UNFILLED** template — source is git history at v7 2.1.0 (`035e839`) or
v6's ACME-example body (per KIT-0029 handoff). Ship **both** v7 (pin
`claude-fable-5` per its frontmatter) and v6 (Opus-class, pin
`claude-opus-4-8`); never edit v6's workflow directly.

**Project-specific agents (never in plugin):** suw `architect`; moss
`tycho`, plus moss's in-`agents/` template files (AGENT-TEMPLATE,
TASK-STARTER-TEMPLATE, OPERATIONAL-RULES — misfiled, not agents). Older
feature-developer-v3/v4/v5, planner/planner2/planner3, agent-creator,
bootstrap, onboarding, document-reviewer, security-reviewer,
powertest-runner, test-runner, create-project: candidates for a **later**
plugin phase, out of this task's Req 3.1 scope (v7, code-reviewer,
ci-checker "as applicable").

---

## Helper-Script Dependencies (must upstream — handoff flagged this)

The canonical (suwinex) artifacts depend on helper scripts that currently
exist **only in suwinex**:

| Script | In kit? | In suw? | Needed by |
|--------|---------|---------|-----------|
| `scripts/core/prepare-review-input.sh` | **no** | yes | code-review-evaluator skill 1.2.0 |
| `scripts/core/lib/target_repo.sh` | **no** | yes | the cross-repo `*.sh` helpers |
| `check-bots.sh` / `verify-ci.sh` / `preflight-check.sh` / `gh-review-helper.sh` cross-repo variants | older | newer | the v1.1.0 commands |

**Consequence:** scripts distribute via the **manifest** (KIT-ADR-0022),
not the plugin. So shipping cross-repo commands in the plugin requires the
matching cross-repo **scripts** to land in the kit's `scripts/core/` and
flow downstream via the manifest. The two channels are coupled here:
plugin command ⇄ manifest script. This must be upstreamed to the kit as
part of Req 3 (note in CHANGELOG).

---

## Classification Summary

**Plugin gets (shared):**
- Skills: bot-triage 1.1.0, pre-implementation 1.2.0,
  code-review-evaluator 1.2.0, review-handoff, self-review
- Commands: babysit-pr, check-bots 1.1.0, check-ci 1.1.0, check-spec,
  commit-push-pr, preflight 1.1.0, retro 1.1.0, start-task, status,
  triage-threads 1.1.0, wait-for-bots, wrap-up 1.3.0 — **canonical
  source = suwinex** for the cross-repo generation
- Agents: ci-checker, code-reviewer (kit copy), feature-developer-v7
  (unfilled), feature-developer-v6 (unfilled)

**Preserved overrides (Risk 3):**
- moss: monorepo path retrofits of code-review-evaluator, review-handoff,
  check-spec, retro, start-task, status, wrap-up. Keep until/unless moss
  migrates layout.

**Project-specific (never plugin):** create-task / create-task-starter
(lbl); architect (suw); tycho (moss).

**Blocking dependency:** upstream `prepare-review-input.sh`,
`lib/target_repo.sh`, and the cross-repo `*.sh` helper variants from
suwinex into the kit's `scripts/core/` before the plugin's cross-repo
commands can function in a freshly-migrated project.

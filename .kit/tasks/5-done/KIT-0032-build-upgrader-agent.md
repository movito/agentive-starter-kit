# KIT-0032: Build the `upgrader` Agent (plugin-version upgrades)

**Status**: Done
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 3-5 hours
**Created**: 2026-06-26

## Related Tasks

**Parent**: KIT-0030 (plugin consolidation — this is its next deliverable)
**Spec**: `docs/PLUGIN-UPGRADE-GUIDE.md` (the runbook this agent automates — it
IS the specification)
**Backs**: KIT-ADR-0025 (runtime-read localization; the upgrader is the
mechanism that "preserves local by construction" on a pin bump)
**Related**: KIT-ADR-0024 §3/§4 (plugin distribution + deliberate upgrade),
KIT-ADR-0022 (manifest sync — a *separate* surface this agent must not absorb)

## Overview

Build an agent that raises a project from one `agentive-workflow` plugin
version to a newer one, and refreshes local agent `model:` pins on a model
rollout. It automates `docs/PLUGIN-UPGRADE-GUIDE.md` step-for-step. The guide
is the spec; this task turns it into a repeatable agent rather than a
hand-followed runbook.

Design principle (from the KIT-0030 handoff): **deterministic tools for the
mechanical axes, LLM judgment only where a human actually has to decide.** The
agent is mostly a careful script-runner with two genuinely judgmental calls.

## The four axes (from the guide)

| Axis | Mechanism | Mechanical or judgment? |
|---|---|---|
| 1. Plugin pin | `claude plugin marketplace update` + `claude plugin update`, confirm version advanced | Mechanical |
| 2. Reconcile changed artifacts | grep for removed/renamed namespaced refs; spot flat-ref regressions | Mechanical detection; **judgment** on which local copies to retire |
| 3. Local agent `model:` pins | grep `^model:` in `.claude/agents/`, rewrite to new model ID | Mechanical rewrite; **judgment** on which locals should move + the target ID |
| 4. Provenance restamp | rewrite `CLAUDE.md ## Provenance` pin + date | Mechanical |

**LLM judgment is confined to exactly two things**: (a) which local adaptations
/ local agents to preserve vs retire when the new version supersedes them, and
(b) the `model:`-pin rewrites (which local agents move, to which model ID).
Everything else is deterministic and should be done with shell, not reasoning.

## Requirements

### 1. Agent definition

- Create `.claude/agents/upgrader.md` (kit-local first; distribution via the
  plugin is a later, separate step — do **not** add it to the plugin in this
  task).
- Frontmatter: name `upgrader`, a tight description, tool access scoped to what
  it needs (Bash, Read, Edit, Grep, Glob). Pin `model:` per the kit's
  current convention.
- Body follows the guide's 7 steps as ordered phases, each phase naming the
  exact command(s) to run and the expected output to confirm before advancing.

### 2. Honor the scope boundary (do not blur three surfaces)

- **In scope**: a project that *already consumes* the plugin moving to a newer
  release; model-pin refresh on a rollout.
- **Out of scope, and the agent must refuse to do them**:
  - The *initial* migration onto the plugin (deleting local copies,
    namespacing). One-time, manual, per the user's decision.
  - **Scripts** (`scripts/core/`) — upgrade via manifest sync /
    `check-sync.sh` (KIT-ADR-0022), a separate runbook
    (`docs/MANIFEST-UPGRADE-GUIDE.md`). The agent may *detect and report* a
    scripts-version gap but must not fold it into the plugin upgrade.
  - **Topology / identity** in `CLAUDE.md` beyond the Provenance stamp.
- **Refusal behavior** (concrete, not just the word "refuse"): on an
  out-of-scope condition — an un-namespaced/legacy project (initial migration
  not yet done), a non-GitHub marketplace source, or a scripts/manifest gap —
  the agent **halts, states the reason in one line, and points to the correct
  runbook** (the manual-migration note / the marketplace re-point command for
  the user / `docs/MANIFEST-UPGRADE-GUIDE.md`) rather than trying to "help". A
  scripts-version gap is surfaced as a **post-upgrade hint to run
  `./scripts/core/check-sync.sh`**, never folded into the plugin upgrade
  (arch-review-fast-v2, mistral-arch).

### 3. Determinism, idempotence, safety

- **Idempotent**: if current pin == target, the agent stops at step 1 with
  "nothing to do" and makes no changes. Re-running after a completed upgrade is
  a no-op.
- **Two-phase, report-then-apply**: a **preview** phase prints the detected
  current → target version, the reconcile diff (added/removed/renamed
  artifacts), and the list of local `model:` pins it would rewrite — then the
  agent **halts for an explicit operator ACK** before the **apply** phase
  mutates anything. No file or `git` mutation happens before the ACK. (Make the
  preview→execute switch explicit so implementations don't diverge —
  arch-review + arch-review-fast-v2.)
- **Never hand-edit cached plugin files** (`~/.claude/plugins/cache/...`) — the
  guide's hard rule. The agent touches only project-owned files + the plugin
  CLI.
- **Marketplace-source guard**: assert the marketplace is GitHub-sourced
  (`movito/agentive-skills`), not a local `Directory (...)`, before upgrading;
  the guide's first gotcha. Refuse / warn if it is a directory source.

### 4. Respect the operating constraints

- The agent **pushes nothing in non-kit repos** — it stages/commits and hands
  the push to the user (`! git -C <path> push`). In the kit itself, pushing is
  allowed per existing convention, but commit/push is still operator-gated by
  the project's commit rules (planning repos → `main`; code repos → feature
  branch, see `docs/CROSS-REPO-PATTERN.md`).
- The agent **cannot edit `settings.json`** (the marketplace re-point, if
  needed, is surfaced as an instruction for the user to run, not done silently).
- Provenance restamp + local-agent `model:` edits are committed together
  (guide step 7).

### 5. Verification built into the agent

- After upgrading, run the guide's step-6 checks: `claude plugin list` shows
  the new version enabled; optional headless probe
  (`claude -p --model haiku "List every subagent_type and command starting with
  'agentive-workflow:'."`) confirms namespaced artifacts resolve; then the
  project's own gate (`./scripts/core/ci-check.sh` / tests) if present.
- Include a **Rollback** phase mirroring the guide: pin back, re-update; note
  the cache retention window (~7 days per the current guide — state it as
  "verify, may change", not a hard constant).

## Acceptance Criteria

- [ ] `.claude/agents/upgrader.md` exists, frontmatter valid, body maps 1:1 to
      the guide's 7 steps + rollback
- [ ] Scope boundary is explicit in the agent body: it refuses initial
      migration, scripts/manifest upgrades, and CLAUDE.md identity edits
- [ ] Idempotence stated and enforced: current == target ⇒ no-op
- [ ] Two-phase preview → operator ACK → apply: no file/`git` mutation before
      the ACK; preview shows version delta, reconcile diff, model-pin list
- [ ] Refusals are concrete: halt + one-line reason + pointer to the correct
      runbook (not a silent skip)
- [ ] Marketplace-source guard and "never edit cached plugin files" rule
      present
- [ ] Operating constraints honored: no non-kit pushes; no `settings.json`
      edits; combined provenance + model-pin commit
- [ ] Verification + rollback phases included
- [ ] Dry-run exercised against this kit repo (already at the current pin ⇒
      proves the no-op path) and the output captured in the task notes or a
      handoff
- [ ] The two judgment points (retire-local? / model-pin rewrite) are called
      out as the only places the agent reasons rather than runs a command

## Risks

### Risk 1: Scope creep into the scripts/manifest surface
**Likelihood**: Medium — the surfaces are adjacent and tempting to merge.
**Impact**: Medium — folding manifest sync in reintroduces the coupling
KIT-ADR-0024 separated.
**Mitigation**: Requirement 2 makes the boundary a hard refusal; acceptance
criterion asserts it.

### Risk 2: Model-pin rewrites hit plugin agents by mistake
**Likelihood**: Low-Medium.
**Impact**: Medium — hand-editing a cached plugin file is silently lost on next
update.
**Mitigation**: The grep targets `.claude/agents/` (local) only; the body
states the plugin's own pins come from `/plugin update`, never hand-edits. The
rewrite is **frontmatter-aware** — it changes the `model:` key inside the
opening YAML block only, and confirms the matched line + surrounding context
before editing, so a `model:` mention in a description or comment is never
rewritten (arch-review-fast-v2).

### Risk 3: Over-automation removes a decision the operator wanted
**Likelihood**: Medium.
**Impact**: Low-Medium.
**Mitigation**: Report-before-mutate (Req 3) + the two explicit judgment points
keep the human in the loop on retire-local and model-target choices.

## Notes

- The guide already encodes the gotchas (same-version re-publish doesn't
  propagate; GitHub-sourced marketplace; cache-file rule). The agent should
  *cite* the guide, not re-derive them, so the two stay in sync. If the agent
  and guide ever diverge, the guide wins and the agent is corrected.
- Distribution decision is deferred: build kit-local, prove it, then decide
  whether it ships in the plugin (it would then need the same genericization
  discipline that bit `code-reviewer`/`ci-checker` in KIT-0030, PR #3).
### Evaluation (2026-06-26)

Reviewed by three arch evaluators across model families. Logs:
`.adversarial/logs/KIT-0032-build-upgrader-agent--{arch-review,arch-review-fast-v2,mistral-arch}.md`.

- **arch-review** (o3): REVISION_SUGGESTED
- **arch-review-fast-v2** (gemini-3-flash): **APPROVED**
- **mistral-arch** (mistral-large): REVISION_SUGGESTED

All three rated structure strong (clear responsibility, low coupling, high
cohesion). **Acted on** the convergent, cheap findings: explicit
preview→ACK→apply gate (o3 + gemini), concrete refusal behavior + manifest-gap
hint (gemini + mistral), frontmatter-aware model-pin rewrite (gemini), softened
cache-window wording (o3).

**Declined as over-engineering for this single-owner, macOS-only context**
(same judgment as KIT-ADR-0025's slim-down — machinery that only pays off at
third-party scale):

- *Formal error-code vocabulary* (`E_SCOPE`, `E_VERIFY`, …; o3) — a runbook
  agent halts with a sentence and a pointer; an enum is ceremony. The concrete
  refusal behavior above captures the intent.
- *Split the two judgment calls into separate mini-agents / JSON judgment
  schema* (o3, mistral) — two decisions in one bounded runbook don't warrant a
  sub-agent boundary or schema; it would add indirection and test surface for
  no gain.
- *`PluginUpdater` abstraction over the plugin CLI* (mistral) — the CLI **is**
  the interface; wrapping it is premature indirection (mistral itself rated it
  "not critical yet").
- *POSIX/Windows portability shims* (o3) — these projects are macOS-only.
- *Make the marketplace source configurable* (mistral) — it is one fixed known
  source (`movito/agentive-skills`); the guide hardcodes it too. Revisit only
  if the kit is ever distributed (the KIT-ADR-0025 revisit trigger).

Net: APPROVED-equivalent after the cheap refinements; ready to assign.

**⚠️ FIRST ACTIONS** (in order):
1. `git checkout -b feature/KIT-0032-upgrader-agent`
2. `./scripts/core/project start KIT-0032`

# Review Pipeline — the single value authority

**Version**: 1.0.0
**Created**: 2026-08-24 (KIT-0116 Phase 1)
**Maintained By**: planner
**Purpose**: THE authority for the kit's review ladder — what review
runs when, who triggers it, what evidence it leaves, and how these
rules change. Agent bodies, skills, commands, and templates **cite
this file; they never restate its values** (KIT-0101 R5: two
authorities drift). If a surface and this file disagree, this file
wins and the surface is a drift bug (`tests/test_review_pipeline_contracts.py`).

---

## The ladder

Review coverage runs end to end; each stage catches what the previous
ones structurally cannot:

| Stage | What runs | Trigger | Cost class |
|-------|-----------|---------|------------|
| Spec time | Adversarial evaluators (`arch-review-fast` / `arch-review` / `claude-arch`) | Planner, per evaluation policy | ¢–$ per run |
| Implementation time, Tier 1 | Harness-native `/code-review` on the branch diff; `/security-review` when flagged | **Default-on** (code review); flag-triggered (security) | One session pass |
| Implementation time, Tier 2 | Kit reviewer agents as **background read-only subagents** (`code-reviewer`; `architecture-reviewer` / `security-reviewer` / `document-reviewer` when flagged) | Flag-triggered · *lands in KIT-0116 Phase 2, governed by KIT-ADR-0036* | Parallel subagent tokens |
| Implementation time, Tier 3 | Deep-review workflow: multi-lens fan-out + adversarial verification | **Opt-in only** (see Escalation) · *lands in KIT-0116 Phase 3* | Many agents — explicit budget |
| PR time | BugBot + CodeRabbit, triaged per the bot-triage skill | Automatic on PR | Bot rounds (budget: one substantive round) |
| Merge gate | **Human review verdict** (planner Phase 7) | Always | — |

The default task path adds exactly ONE pass over the pre-KIT-0116
workflow: `/code-review`. Flagged dimensions run solely when declared;
nothing fans out three reviewers on an ordinary task
(proportionality, spec NFR-1). Operator sovereignty is unchanged —
subagent and skill findings *inform*; the human verdict *decides*.

## Review Flags — the authoritative registry

Task specs and handoffs may carry an optional field:

```markdown
**Review Flags**: architecture, security
```

The **planner** sets flags at spec/handoff time using the trigger
heuristics below. Planner bodies and the starter template cite this
registry; they do not carry their own copies. **Default (no field, or
empty) = code review only.**

| Flag | Declares | Trigger heuristics |
|------|----------|--------------------|
| `architecture` | Implementation-level architecture pass (`architecture-reviewer` from Phase 2; Tier 3 for high-risk) | Multi-module change; a new pattern or abstraction; public API surface; cross-repo or cross-package contract; anything an ADR governs |
| `security` | `/security-review` in the Tier-1 slot; `security-reviewer` subagent from Phase 2 | Auth or permissions logic; input handling/parsing; secrets or credential paths; network calls; dependency changes |
| `docs-audit` | `document-reviewer` **periodic audit** — not a per-task gate | User-facing surface changed; or several sessions have passed since the last audit (planner judgment) |

Flag inflation is a named risk (spec Risk 2): flags are set from these
written criteria, not vibes; retros occasionally check flag usage
against actual yield.

## Tier selection — three axes

Which review spends buy findings depends on the diff's shape, not on
enthusiasm. Three measured axes:

1. **Prose vs logic** (KIT-0069/KIT-0073, third data point DTL-0026):
   on prose-dominated or deletion-heavy diffs the evaluator trio went
   0-for-17 while bots went 11-for-14 — diff-only evaluator input makes
   models reconstruct unchanged regions from assumption. Prose sweeps
   get `code-reviewer-fast` only plus **tree-grounded verification**;
   deep evaluator passes buy nothing there (code-review-evaluator
   skill, "Prose-sweep exception").
2. **Change risk** (the classic axis): new functions, external
   integrations, security-sensitive seams → deeper tiers and flags;
   trivial mechanical diffs → the evaluator skill's auto-skip rules.
3. **Argument-parsing and input-validation seams are bot-favourable
   and evaluator-hostile** (KIT-0118, measured on PR #147): the full
   evaluator trio, on full-file input, passed an argv seam
   (`--evaluators=` skipping validation) that CodeRabbit flagged
   Major — and across four bot rounds the trio found nothing true the
   bots missed while its one FAIL was three-fifths false. On
   flag-adding or argv-touching diffs, do **not** buy extra evaluator
   passes; spend the review budget on input-space enumeration
   (patterns.yml `flag_presence_is_not_flag_emptiness`) and on the
   bots. Evidence: KIT-0118 retro (Surprising 2, Lesson 3);
   REVIEW-INSIGHTS.md (KIT-0118 block).

Default `/code-review` effort: **medium** (fewer, high-confidence
findings). Raise the level for logic-heavy or high-risk diffs; the
axes above say when a level buys nothing.

## Evidence contract — the review-pass record

Every task's Tier-1 pass (and, when they run, its flagged/Tier-2/Tier-3
passes) is persisted to ONE record in the planning repo:

```text
.kit/context/reviews/<TASK-ID>-review-pass.md
```

The record carries, per pass that ran: the tool and effort level, the
findings, and a **fix-or-defer disposition for every finding** — fixed
(commit), or deferred with the reason. Deferred findings ALSO surface
in the PR description and the review starter, so the human reviewer
sees them without opening the record. Flagged dimensions that ran
record their outcome; a pass that was *skipped* records the skip and
its reason (per the skip rules here and in the code-review-evaluator
skill) — a skip is a persisted decision, never a silent omission.

**Preflight Gate 8** ("Review pass done") checks exactly this: a
non-empty `<TASK-ID>-review-pass.md` exists. The `agentive preflight`
CLI keeps emitting mechanical gates 1–7; Gate 8 is session-checked by
the `/preflight` command until mechanized in the CLI (backlog:
KIT-0120 — same extraction direction as KIT-0114).

## The docs habit (explicitly NOT a per-task gate)

Before preflight, the implementing session updates the docs its diff
touches (README, workflow docs, CHANGELOG as applicable). The
`document-reviewer` agent runs as a **flag-triggered periodic audit**
(`docs-audit`), never as a per-task gate (FR-9).

## Escalation to Tier 3 (opt-in contract)

Tier 3 — the deep-review workflow (multi-lens diff review with
adversarial verification) — runs **only** when a human asked for it in
words: the operator in-session, or the planner via the task starter
("run the deep-review workflow on this PR"). The implementing agent
**never self-escalates** to Tier 3 (FR-11) — not for a scary diff, not
for a failed review round. The full invocation contract (exact
command, who may invoke, what evidence the run leaves) is formalized
here when the workflow ships in KIT-0116 Phase 3; until then there is
nothing to invoke.

## Governance — how these rules change

- Changes to flag names, trigger heuristics, tier rules, or the
  evidence contract are made **in this file only**, via an ordinary
  task + PR; every other surface cites by reference. A change that
  edits a citing surface but not this file (or vice versa) is caught
  by `tests/test_review_pipeline_contracts.py`.
- This file is a plugin-distributed instruction surface: changes ride
  the release train and reach twins **by copy, not re-derivation**
  (patterns.yml `harden_twins_by_copy_not_rederivation`).
- Cost data: reviewer-subagent token/time costs from live smoke runs
  are recorded here as they are measured (KIT-0116 Phase 2), so flag
  decisions are informed.

---

**Related**: `.claude/skills/code-review-evaluator/` (spec-time +
pre-PR adversarial evaluators, skip rules), `.claude/skills/bot-triage/`
(PR-time bot discipline), `.claude/commands/preflight.md` (Gate 8),
`.kit/context/patterns.yml`, KIT-ADR-0035 (native coordination),
KIT-ADR-0036 (read-only reviewer delegation — Phase 2).

# KIT-0099 — Evaluator Review Record

**Task**: KIT-0099 — Release plugin 2.0.1
**PR**: movito/agentive-skills, branch `release/agentive-workflow-2.0.1`
**Date**: 2026-08-10
**Reviewer**: feature-developer (Opus 5)

## Tier decision — fast tier only, `--format diff`

The diff is **prose-dominated** (17 markdown component bodies + release
metadata), which triggers the prose-sweep exception in the
code-review-evaluator skill: run `code-reviewer-fast` ONLY as the Gate 5
record, and never action a finding without reproducing it against the
tree. The deep tier's spend buys nothing on this shape (KIT-0069:
0-for-7; KIT-0073: 0-for-8; planner decision 2026-07-28, reaffirmed by
the three-data-point process note in a2994c7).

**Input scoping deviation (deliberate, recorded)**: the review input
covers the **release-metadata surface only** — `roster.yaml`,
`plugin.json`, `marketplace.json`, `CHANGELOG.md`, `README.md` — not the
17 component bodies. Rationale: the bodies are not authored here. They
are upstream-canonical content already reviewed and merged in the kit
(KIT-0097 #120, KIT-0098 #121); re-reviewing them in the marketplace repo
re-litigates a merged decision and, on a diff-only input, invites
evaluators to reconstruct the PRE-fix state — the documented failure mode.
What CAN go wrong in a mechanical sync is metadata: wrong hashes, version
disagreement, a mis-applied transform. That is what was submitted, and
that surface is additionally covered by mechanical verification below,
which is stronger than an LLM read.

## Run

```
adversarial code-reviewer-fast .adversarial/inputs/KIT-0099-code-review-input.md
```

Model: `gemini/gemini-2.5-flash`. Verdict: **FAIL** (1 correctness, 1
robustness). Log:
`.adversarial/logs/KIT-0099-code-review-input--code-reviewer-fast.md`

## Findings and disposition

### F1 [CORRECTNESS] "CHANGELOG says 17 components, roster updated 18" — REJECTED (not reproducible)

Claim: 18 roster entries were updated, so the CHANGELOG's "17" is a
factual error.

Reproduction against the tree:

```
git diff main...release/agentive-workflow-2.0.1 -- plugins/agentive-workflow/roster.yaml \
  | grep -c '^+    kit_sha256:'     ->  17
  | grep -c '^+    kit_version:'    ->  14
  | grep '^+plugin_version'         ->  plugin_version: "2.0.1"
```

17 components had their hash refreshed; 14 of those also changed
`kit_version` (three changed content without a version bump: planner,
planner-f5, bot-triage). The evaluator's 18th "component" is almost
certainly the top-level `plugin_version` scalar, which is not a component
entry.

Independent confirmation from the kit's own drift guard — the mechanical
authority for this exact question:

- Before: `PLUGIN DRIFT: 17 finding(s)` (each naming a component)
- After: `in sync: 27 shipped components match the published roster.` (exit 0)

The CHANGELOG's "17" is correct. No change made.

### F2 [ROBUSTNESS] "Future date in CHANGELOG (2026-08-10)" — REJECTED (false premise)

The session date IS 2026-08-10. The date is the actual release date, not
a placeholder. No change made.

## Mechanical verification (the real gate for this PR shape)

Per the prose-sweep rule, tree-grounded checks carry the weight here:

- **Drift guard green**: `check_plugin_drift.py --roster-file <this branch's roster>`
  → `in sync: 27 shipped components`, exit 0. This is the task's central
  acceptance criterion, verified against the exact roster being shipped.
- **Baseline integrity**: all 17 pre-refresh kit sources re-hashed to the
  values recorded in the 2.0.0 roster, confirming the true release
  baseline (including the planner/planner-f5 pair, whose kit content
  changed AFTER the 2.0.0 hashes were cut — these are the two components
  a naive `git diff` from the 2.0.0 sync commit would have missed).
- **Version agreement**: `plugin.json`, `marketplace.json` (metadata +
  plugin entry), and `roster.yaml` all report `2.0.1`; JSON and YAML both
  parse.
- **Roster membership unchanged**: 35 entries / 27 shipped, identical to
  2.0.0 — no roster decisions in a patch release.
- **Transform application**: no flat (un-namespaced) references to any
  shipped command or skill; no double-namespacing; no path-like false
  positives; no `KIT-LOCAL` / `EXTENSION POINT` regions; no
  `engine-consumer` or `scripts/local/` leaks.
- **Structural invariants**: Phase-1 sentinel present in both
  feature-developer variants; the pair is byte-identical below its
  `<!-- SYNC -->` marker; phases run 1–9 with the relocated Evaluator
  block appearing exactly once (the pre-move Phase 7 duplicate is gone).

## Carried upstream, NOT fixed here (two stale cross-references)

`feature-developer.md` and `feature-developer-f5.md` each contain two
references to "Phase 6" that should read "Phase 7" after KIT-0097's
renumbering moved CI polling from 6 to 7:

- preamble: "CI polling happens inline via ScheduleWakeup (see Phase 6)"
- Shell Rules: "respects the prompt-cache TTL (see Phase 6)"

Both are present in the **kit canon** (verified in
`.claude/agents/feature-developer{,-f5}.md`) — residuals of the KIT-0097
renumbering that survived the KIT-0098 coherence repair. They are
inherited by this sync, not introduced by it.

Deliberately not fixed in the plugin: KIT-ADR-0028's fix-here-then-release
contract means canonical content is fixed in the kit and then released.
A plugin-side-only fix would immediately re-open drift (the guard compares
against kit hashes) and turn the guard red — the opposite of this task's
goal. The task spec also freezes kit-side files for this task. Filed for
a kit follow-up; the affected text is advisory cross-referencing, not
executable instruction.

# KIT-0105: `project-intake` ships in the plugin — run intake in the deliverable folder

**Status**: In Progress
**Priority**: high — the operator-facing half of the KIT-ADR-0030–0034
set; KIT-0104 removes the technical precondition, this task collects
the benefit
**Type**: Architecture / distribution
**Estimated Effort**: 0.5-1 day
**Created**: 2026-08-09 (revised 2026-08-13: combined-ADR split)
**Source**: KIT-ADR-0031
**Evaluation**: arch-review-fast 2026-08-14 — **APPROVED**; two
future-facing findings dispositioned: F3's operator-in-the-loop gap
reporting is by design at one operator (KIT-ADR-0034's "second
operator" revisit trigger is the escalation point); the `agentive` CLI
dependency is the intended ADR-0030 coupling, semver'd by the package.
Log: `.adversarial/logs/KIT-0105-project-intake-into-the-plugin--arch-review-fast.md`.
Don't re-litigate.

## Related

**ADR**: `.kit/adr/KIT-ADR-0031-project-intake-ships-in-the-plugin.md`
**Blocked by**: KIT-0104 (`agentive new` in the package — until the
door ships, the intake agent genuinely cannot run outside a kit
checkout)
**Related**: KIT-ADR-0033 (handoff brief primacy — governs this agent's
input; the derived-brief fallback is NOT this task), KIT-0066 (the
intake flow), KIT-0081 (the live intake that surfaced its gaps — F2's
class recurs here), KIT-0096 (plugin release mechanics + the drift
guard)

## Overview

`.claude/agents/project-intake.md` states: "**Where you run**: from an
agentive-starter-kit checkout — the door is kit-side only and does not
ship to consumer projects." Once KIT-0104 lands, that sentence is false
and the constraint is gone.

Move `project-intake` into the `agentive-workflow` plugin. The roster
already carries it as `ships: false` with the why-line "runs FROM a
kit checkout by its own header" (roster.yaml:146–151, verified
2026-08-14) — KIT-0104 made that rationale false, so F1 is a FLIP to
`ships: true`, not an addition. The shipped-set membership change
makes this release a **minor bump: 2.0.4 → 2.1.0**. The intended flow
becomes: **open Claude in the Cowork output folder and run the intake
in place** — the deliverable is the input, where it already sits.

## Requirements

- **F1 — the agent moves into the plugin roster.** Follow KIT-0096's
  declarative roster + drift-guard mechanics; the guard goes red on the
  first merged change and forces the release, which is the designed
  flow. Behavior parity: fixes land in the kit's canonical `.claude/`
  tree, never in divergent marketplace edits (KIT-0097's
  fix-here-then-release contract).
- **F2 — the agent becomes location-agnostic.** Today it assumes it is
  running in a kit checkout and reaches the door by relative path.
  Rewrite Step 0/2 to (a) verify `agentive` is installed and instruct
  if not — never a dead end, per the door's own convention — and
  (b) treat its own working directory as the candidate prototype folder
  when the user gives no path. Remove the "compose the door, never
  modify it" path assumptions that depend on a kit tree; the rule
  itself stays.
- **F3 — the door-gap escape hatch needs a new home.** The agent
  currently says: file a follow-up in `.kit/tasks/1-backlog/` if the
  flow exposes a door gap. Running outside the kit, that path does not
  exist. Replace with an instruction to report the gap to the operator
  with a ready-to-paste task body — the operator files it in the kit
  when they are next there. This preserves the KIT-0081 feedback loop,
  which KIT-ADR-0034 makes the *primary* generator of kit work.
- **F4 — DONE UPSTREAM, do not re-implement** *(verified 2026-08-12
  against `origin/main`)*: the `init.defaultBranch` guard shipped in
  the intake agent (`project-intake.md:165` rationale, `:200`
  `git -C <code-path> branch --show-current` must print `main`). The
  KIT-0081 F3 gap is closed. Carry the behavior through the move
  unchanged; add a test rather than a fix.
- **F5 — prose sweep by class.** Every surface asserting intake is
  kit-side: the agent body, `docs/STARTING-A-PROJECT.md`,
  `.kit/templates/PROTOTYPE-HANDOFF-TEMPLATE.md` step 3 ("Open a new
  tab from your agentive-starter-kit checkout"), `README.md`. Grep the
  class, do not fix only the instances listed here.
- **F6 — the intake acceptance test rides this task** (KIT-ADR-0034's
  enforcement mechanism): extend `tests/test_scaffold_acceptance.py` to
  run the full intake end-to-end in CI against a fixture prototype
  folder — create → `agentive doctor` → assert every file path
  referenced by the seeded agents exists in the created tree (the
  KIT-0081 F2 class, by machine on every push).

## PR Plan (planner, 2026-08-14)

Three PRs, each single-theme (the KIT-0104/0110 discipline):

1. **PR 1 (kit) — the agent move**: F1's kit-side half + F2 + F3 + F4
   test + F5 prose sweep + F6 acceptance-test extension. One theme:
   intake becomes location-agnostic and machine-verified.
2. **PR 2 (kit) — the canon-fix bundle**: the passengers, one themed
   sweep — KIT-0103 R1 (stale sync references, grep-derived),
   KIT-0112 (fail-closed thread counting + class grep + the seventh
   lying-status face into bot-triage). Their specs are authoritative;
   KIT-0112 completes fully, KIT-0103 only its R1.
3. **PR 3 (marketplace) — release 2.1.0**: the FIRST TOOLED CUT —
   `scripts/local/plugin_resync.py` computes the delta and the
   `plugin_sha256` values (cite it: the open KIT-0110 AC); roster flip
   to `ships: true`; minor bump (membership change), all version
   fields; markdownlint job rider (KIT-0110 F2); the new required
   check must pass. Release budgeting: one substantive bot round is
   the baseline (42→12→3 trend) — do not pre-pay for a siege.

Each PR inside the review-surface budget; any overrun → STOP and
report a split.

## Acceptance

- [ ] `project-intake` appears in the plugin roster and the drift guard
      is green after release
- [ ] The agent completes an intake from a folder with no path
      relationship to any kit checkout
- [ ] A missing `agentive` CLI produces a printed install command, not
      a failure
- [ ] The existing `main`-branch guard still holds after the move (test, not fix)
- [ ] The end-to-end intake acceptance test runs in CI and includes the
      seeded-path existence assertion
- [ ] No live surface still says intake runs from a kit checkout

## Notes

- Model pin and frontmatter conventions: `.kit/templates/AGENT-TEMPLATE.md`;
  verify model IDs against live docs, not memory (KIT-0069 F1 lesson).
- The handoff brief stays the primary input — KIT-ADR-0033. This task
  does **not** implement the derived-brief fallback; that is sequenced
  after KIT-0104 lands, per the KIT-ADR-0034 WIP cap.
- **Release-train riders** (planner, 2026-08-14): this task's release
  cut is the first tooled one — use `scripts/local/plugin_resync.py`
  and cite it (the open KIT-0110 AC). KIT-0103 R1 + KIT-0112 ride the
  same train. Marketplace PR rider: add a markdownlint job to
  agentive-skills CI (KIT-0110 marketplace follow-up F2 — trivially
  cheap now the first workflow exists).

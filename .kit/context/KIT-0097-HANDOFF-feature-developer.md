# KIT-0097: Canonical .claude/ content fixes from the 2.0.0 review — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-08-09
**From**: planner-f5
**To**: feature-developer
**Task**: `.kit/tasks/5-done/KIT-0097-canonical-agent-content-fixes-from-2.0.0-review.md`
**Status**: Ready — operator wants it asap; the spec IS the finding list
(21 findings by file with thread links + 2 backports + 2 riders)
**Evaluation**: gate passed with one dispositioned minor finding —
record in the spec header

**Target Codebase**: This repo (agentive-starter-kit) — single-repo mode
(the repo split, not your working directory — see Session topology).

## Session topology (read before anything else)

- Worktree: `~/Github/ask-worktrees/KIT-0097`, branch
  `feature/KIT-0097-canonical-content-fixes` — created and provisioned
  by the planner; task file started in `3-in-progress`, moved to
  `4-in-review` at handoff
- VERIFY, never create: `git branch --show-current` must show the
  branch above before your first edit; if not, STOP and ask
- Likely ONE PR (content fixes) + the 2.0.1 release step afterward
  (marketplace repo — clone exists at `~/Github/agentive-skills` from
  KIT-0096; work on a branch there, PR, operator review is the gate;
  CodeRabbit DOES run there — 23 threads last time; bot presence
  verified by that PR's history)

## THE ONE THING THAT WILL LOOK BROKEN AND ISN'T

The **Plugin Drift Guard check on your kit PR will go RED** the moment
you touch any roster-shipped `.claude/` file. That is the guard doing
its job (kit newer than published plugin) — the fix-here-then-release
contract working, NOT a CI failure to fix. Do not attempt to green it
from the kit side. State in the PR body: "Drift guard red by design;
green again when 2.0.1 ships (this task's release step)." Every OTHER
check must be genuinely green; the merge-go says "green except the
by-design drift check."

## Mission

Fix the 21 review findings in the kit's canonical `.claude/`, apply
the 2 backports (the places the CANON regressed behind the old
plugin), keep the agent pairs in sync, then cut plugin 2.0.1 to close
the loop. The spec's per-file checklist is authoritative — this
handoff only adds mechanics.

## Verified anchors (2026-08-09)

- **F1 (the High)**: `feature-developer.md:141-142` — the Phase
  Overview table orders `7. Evaluator` after `6. CI + Bots`,
  contradicting the pre-open trio rule the evaluator skill has
  mandated since KIT-0035/0046 (and which every recent task actually
  ran). Fix the table AND scan the surrounding phase prose for the
  same stale ordering; this is the one that costs real bot rounds.
  Spec suggests a contract-test pin where a fix creates a
  stable sentinel — F1 qualifies.
- **Pairs rule**: feature-developer/-f5 and planner/-f5 bodies are
  IDENTICAL apart from frontmatter (model pin, name, the f5 preamble).
  Every fix lands in both halves of its pair; bump `version:` in all
  touched agents. `tests/test_agent_contracts.py` must stay green —
  if a fix rewords a pinned sentinel, update the test in the same
  commit (its header says exactly this).
- **Backports** (from the KIT-0096 both-directions diff): check-ci's
  dynamic-branch hardening and ci-checker's Cross-Repo Mode section —
  the old plugin had them, the kit canon lost them. Recover from
  `movito/agentive-skills` git history (pre-2.0.0 state), not from
  memory.
- **Riders**: R1 (Phase 9 move+stage recipe — add while you're in
  Phase 9 for F-family fixes) and R2 (PII email in
  plugin.json/marketplace.json — surface the keep-or-noreply choice
  in the 2.0.1 release PR body for the operator; do not decide).

## The 2.0.1 release step

After the kit PR merges: refresh ONLY the changed files into
`plugins/agentive-workflow/` (the KIT-0096 transforms are the
precedent — KIT-LOCAL regions still don't ship; same generalization
judgment on the fixed text), update roster.yaml hashes, bump
plugin.json to 2.0.1 (patch — content fixes, no roster change),
marketplace PR, then after ITS merge verify: drift guard green on kit
main, `claude plugin marketplace update agentive-skills` +
`claude plugin update agentive-workflow@agentive-skills` lands 2.0.1.
Reply on agentive-skills#4's summary thread that the closure shipped.

## Test approach

- `tests/test_agent_contracts.py` green throughout; add pins per spec
  AC (break each new pin once — house rule).
- Full suite per push (~213 s pytest-fast is REAL — use ≥360 s
  timeouts; TESTING-WORKFLOW documents this now).
- Evaluator trio before the kit PR opens — **`--format diff`** (this
  is strings/docs-shaped; the skill's new guidance exists because of
  exactly this shape). Disposition table; deep rounds ≤2.
- Expect bots to re-review the fixed text as fresh content (the
  KIT-0096 pattern: all 42 findings hit canonical text) — the
  pre-filed found-in-review path this time is: new findings append to
  THIS task's spec as a second checklist, not a new task, unless
  they're out of its scope.

## Out of scope — do not touch

- Behavioral redesign beyond the cited findings; the drift guard and
  release machinery (shipped); the door; `agentive-kit` package code
  (except nothing — this task is .claude/ content only; R2's
  plugin.json edit happens in the MARKETPLACE repo at release)
- KIT-0094's markdownlint decisions (F19 declines cite it, don't
  implement it)

---

**Task File**: `.kit/tasks/5-done/KIT-0097-canonical-agent-content-fixes-from-2.0.0-review.md`
**Finding provenance**: movito/agentive-skills#4 threads (linked per finding in the spec)
**ADR**: KIT-ADR-0025 (generalization), KIT-ADR-0028 (fix-here-then-release)

# KIT-0116: Automated review pipeline — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not
delegate or spawn other agents — with ONE sanctioned exception this
task itself creates: Phase 2's live smoke spawns read-only reviewer
subagents via the Agent tool, per the carve-out ADR you will author.**

**Date**: 2026-08-24
**From**: planner-f5  **To**: feature-developer-f5
**Task**: .kit/tasks/4-in-review/KIT-0116-automated-review-pipeline.md
**Status**: Ready
**Evaluation**: Gate PASSED at the 3-round limit (fast ×2 + o3), all
findings folded into the spec — don't re-litigate. The spec's Notes
section carries two later planner additions that are BINDING: the
tier-third-axis design input (2026-08-24) constrains REVIEW-PIPELINE.md's
heuristics.
**Target Codebase**: This repo (single-repo mode)

## Session topology (read before anything else)

- **Worktree**: `/Users/broadcaster_three/Github/ask-worktrees/KIT-0116`
- **Branch**: `feature/KIT-0116-review-pipeline` (created by the planner
  at authoring time — verify, NEVER create; wrong branch or path →
  STOP and ask, never `checkout -b`)
- **Plan**: THREE PRs, one per phase, each independently mergeable.
  The initial branch carries Phase 1. After PR 1 merges, branch each
  subsequent phase from UPDATED main (this is the sanctioned way to
  open later-phase branches — the never-`checkout -b` rule governs
  session-start topology, not mid-task PR branching; announce each
  new branch in the session before creating it).
- **Phase boundaries are operator check-ins AND abort points** (spec PR
  Plan). Ship Phase 1, report, wait for the operator's go before
  Phase 2. If Tier 2's smoke hits an unresolvable permission-prompt
  issue, Phase 1 stands alone.

## Mission

Close the review gap per KIT-ADR-0035 Decision #3 ("defined but never
invoked" is the failure state this exists to prevent). The spec's FR-1
… FR-12 are authoritative; phases:

- **Phase 1 (Tier 1 + flag system — ship alone if needed)**: /code-review
  in the fd gate sequence (after code-review-evaluator, before
  review-handoff); flag-triggered /security-review; preflight gains a
  gate; Review Flags field + heuristics; NEW REVIEW-PIPELINE.md as the
  single value-authority.
- **Phase 2 (Tier 2 + ADR)**: KIT-ADR-0036 read-only reviewer
  delegation carve-out; background reviewer spawns in fd bodies;
  reviewer toolset audit (Bash REMOVED by default, FR-6); new
  architecture-reviewer agent; footgun text updated to cite the ADR.
- **Phase 3 (Tier 3)**: opt-in deep-review workflow, formal escalation
  contract in REVIEW-PIPELINE.md (FR-12).

## Verified anchors (verified 2026-08-24 against main @ c76dff7 — re-verify before relying)

- **SPEC CORRECTION — preflight path**: the spec's Phase-1 file list
  says `.claude/skills/preflight/`; the kit-side surface is actually
  **`.claude/commands/preflight.md`** (slash commands resolve from
  `.claude/commands/` only — standing footgun). Verified: that file
  declares "all 7 completion gates", gate table at ~line 74. Kit
  `.claude/skills/` holds only: bot-triage, code-review-evaluator,
  pre-implementation, review-handoff, self-review. Adding the new gate
  means the "7" literals inside preflight.md (lines 2, 16, 22 at
  verification time) and every cross-surface citation — which is
  exactly why FR-3 makes the count cite-by-reference; your drift greps
  must catch every surviving literal.
- **REVIEW-PIPELINE.md does not exist** (`ls .kit/context/workflows/ |
  grep -i review` → only REVIEW-FIX-WORKFLOW.md). You create it;
  everything else cites it.
- **KIT-ADR-0036 slot is free** (`ls .kit/adr/ | grep 0036` → empty;
  0035 is the last used — matches the spec's renumbering note).
- **Harness-native review skills exist in this session's roster**:
  `code-review` (with effort levels + --fix/--comment), `security-review`,
  `simplify` (Nice-to-Have positioning). Re-verify availability from
  the worktree session before writing instructions that invoke them.
- **Reviewer toolsets (Phase 2 audit targets)**: all three of
  `code-reviewer.md`, `security-reviewer.md`, `document-reviewer.md`
  declare `tools:` lists in frontmatter (line 9 each);
  `code-reviewer` currently declares **Bash** (and TodoWrite) — the
  FR-6 default remedy is removal. `security-reviewer` declares
  WebSearch; `document-reviewer` WebSearch/WebFetch — rule on each
  against the read-only carve-out in the ADR, don't assume grep-level
  equivalence.
- **Binding tier heuristic input** (spec Notes, planner 2026-08-24):
  REVIEW-PIPELINE.md's tier/flag heuristics MUST encode the third
  axis — argv/input-validation seams are bot-favourable and
  evaluator-hostile (KIT-0118 measured; KIT-0069/0073 the prose axis).
  Cite patterns.yml `flag_presence_is_not_flag_emptiness` there.
- **TASK-STARTER-TEMPLATE.md is at version 2.1.0** — adding the Review
  Flags field shell bumps its version and its "single starter
  authority" contract means planner bodies keep citing, never
  restating (KIT-0101 R5).

## Twins and the release train

- fd bodies (both variants), planner bodies (both variants), preflight,
  and the skills you touch are **plugin-rostered components** — the
  marketplace copies (`~/Github/agentive-skills`) update by copy on a
  release train, never by re-derivation (patterns.yml
  `harden_twins_by_copy_not_rederivation`).
- **Planner ruling — release timing**: do NOT cut a marketplace release
  per phase. Kit PRs merge per phase; the plugin/marketplace release is
  cut ONCE at arc end (held-release discipline, KIT-0113), and the
  planner decides at that point whether KIT-0115 / KIT-0103 R6 /
  KIT-0117's command-stripping ride the same train. If you finish
  Phase 3, report and ask before any release mechanics.
- Marketplace repo is a plain clone — CHECK its checked-out branch
  before any operation there; prior fd sessions leave it on feature
  branches.

## Verification approach (from the spec — the order matters)

1. **Red first**: write the drift-check greps BEFORE editing (gate
   count, flag field name, ADR number across preflight, fd bodies ×2,
   planner bodies ×2, starter template) — plus the Bash-absence check
   on reviewer frontmatter (Phase-1 CI wiring is a Should-Have; the
   grep itself is a Must).
2. Live smokes with transcript evidence in the PR: Tier 1 = one scratch
   run of /code-review in the gate slot; Tier 2 = one background
   code-reviewer spawn.
3. Instruction-surface task: pytest/coverage only if scripts change.

## Out of scope — do not touch

- The human-verdict merge gate; any dispatch-kit code; tmux; Agent
  Teams (experimental).
- KIT-0115's ninth-face bot-triage edit, KIT-0117's command stripping —
  possible release-train companions, but their CONTENT belongs to
  their own tasks.
- Reviewer-agent model pins beyond the toolset audit.
- Discovered gaps → `.kit/tasks/1-backlog/`.

## Cautions

- **Shared primary clone (KIT-0103 R6)**: the planner session is live
  in the primary checkout. Your wrap-up/bookkeeping edits to shared
  files (agent-handoffs.json, retros) can collide with planner edits —
  commit wrap-ups promptly and re-verify your edits by CONTENT (grep,
  not ls) after any concurrent activity. Bilateral rule.
- **Gate-count literals are contract-ish**: `/preflight` output and its
  exit-code table are parsed by habit if not by code — check for tests
  or scripts pinning gate numbers before renumbering.
- **The agent bodies you edit are the ones running you.** Body edits
  take effect on NEXT session launch, not mid-session — don't expect
  your own session to exhibit the new gate sequence; the live smoke is
  the proof, not introspection.
- Bot budget: ONE substantive round per PR (standing). Bot truth =
  reviewThreads GraphQL. Your own new /code-review gate does not apply
  to this task's PRs until the bodies ship — don't confuse the ladder
  being built with the ladder you run under.

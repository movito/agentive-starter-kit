# KIT-0101 — Review Starter

**Task**: `.kit/tasks/4-in-review/KIT-0101-cold-start-ux-contract.md`
**PRs**: [#125](https://github.com/movito/agentive-starter-kit/pull/125)
(R1–R4, **merged** `84e9286` after operator verdict 2026-08-11) +
[#126](https://github.com/movito/agentive-starter-kit/pull/126)
(R5, retargeted to `main` after the #125 merge — awaiting operator
verdict)
**Agent**: feature-developer-f5 · **Date**: 2026-08-11

## What shipped

- **R1**: transparency-header pattern (defined once in
  `.kit/context/workflows/COMMAND-UX-CONTRACT.md`, incl. the dual-home
  link decision) + swept across all 14 user-invocable commands,
  version-bumped.
- **R2**: every journey session hop collapsed-or-reasoned; the dead
  launcher-era rationale nowhere cited (grep proofs in #125's body).
- **R3**: intake Step 5 = the operator's F10 checklist verbatim
  (✓ verified-at-print, ✗ inline remedies, launch command only with
  no doctor FAILs); door tail elevates a missing `agentive` CLI to
  the headline NEXT STEP; scaffold-acceptance pins updated in-commit.
- **R4**: journey replay step log in #125's PR body; both door paths
  (missing-CLI and full-toolchain) run live.
- **R5**: TASK-STARTER-TEMPLATE v2.0.0 = single starter authority
  (required core, house improvements, two worked examples,
  proportionality rule); planner Phase 5 points, doesn't duplicate;
  sentinel pins unmoved and green.

## Review focus

1. **The F10 checklist wording** (`project-intake.md` Step 5) — one
   flagged deviation: `claude --agent planner` instead of the mock's
   `planner-f5` (journey-consistency choice; override if wrong).
2. **The door tail shape** (`scripts/local/bootstrap`
   `run_doctor_tail`) — headline block placement after "Install
   complete:", `printf %q` escaping on pasteable lines.
3. **Template required core** — is anything missing from the
   eight-element core the operator would consider non-negotiable?

## Gate status

- CI green both PRs (3.10/3.12/3.14 + lint); **drift guard
  red-by-design** until 2.0.3 ships post-merge.
- CodeRabbit: #125 approved after round 1 (5/5 threads fixed in
  `f4f8cd0`, all resolved); #126 reviewed after the retarget to main
  — round-1 threads (4) fixed and resolved in the bookkeeping-fix
  commit this line ships in.
- BugBot: pass on both.
- Evaluator: fast-tier per policy, both PRs; all findings
  dispositioned — `.kit/context/reviews/KIT-0101-evaluator-review.md`.

## After merge (standing recipe)

Release plugin **2.0.3**: refresh the changed shipped files (12
commands + project-intake + planner pair + template) into the
marketplace clone, namespacing transform per its README §Maintenance,
roster hashes, version bump, CHANGELOG by family; then cite the drift
guard green run URL and `claude plugin list` showing 2.0.3.

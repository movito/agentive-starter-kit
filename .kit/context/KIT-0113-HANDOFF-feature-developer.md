# KIT-0113: project-intake hardening — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not
delegate or spawn other agents.**

**Date**: 2026-08-16
**From**: planner-f5  **To**: feature-developer
**Task**: .kit/tasks/4-in-review/KIT-0113-project-intake-hardening.md
**Status**: Ready
**Evaluation**: N/A — skipped (single-file canon fix; both findings
bot-sourced and already characterized; class grep defined in the spec)
**Target Codebase**: This repo (single-repo mode) + marketplace repo
`~/Github/agentive-skills` via `git -C` for leg 2 (KIT-0109/0110/0105
precedent)

## Session topology (read before anything else)

- **Worktree**: `/Users/broadcaster_three/Github/ask-worktrees/KIT-0113`
- **Branch**: `feature/KIT-0113-intake-hardening` (created by the
  planner — verify, NEVER create; wrong branch/path → STOP and ask)
- **Plan**: two legs, likely one session. Leg 1 = kit PR (canon fix).
  Leg 2 = marketplace release PR (2.1.1) after leg 1 merges.
- Marketplace repo is a PLAIN CLONE (no worktrees) — check its
  checked-out branch before any operation; prior fd sessions have left
  it on feature branches (it was on `main` when this handoff was
  written, 2026-08-16).
- Worktree venv: real venv only (never rebuild through a symlink);
  invoke `pytest` directly, not `python3 -m pytest`.

## Mission

Two hardening fixes to `.claude/agents/project-intake.md` (the spec's
R1/R2 are authoritative), then cut plugin release 2.1.1 so the fix
ships (spec's Release scoping section is authoritative on versions).

### Leg 1 — canon fix (kit PR)

**R1 — quiet credential scan (Critical).** Two sites currently put
staged content into the transcript; source: CodeRabbit threads
`PRRT_kwDOSj0O5s6ZiCNh` (Critical) + `PRRT_kwDOSj0O5s6ZiCNi` on
agentive-skills#11 (see spec Source block; declined there per
KIT-0097 fix-here-then-release):

- **Step 4c** leaks the FULL staged diff: the fenced block instructs
  `git -C "<parent>/<name>-planning" diff --cached   # scan this output`.
- **Step 2.3** leaks MATCHED credential lines: "grep the staged
  content for common credential shapes" — a hit prints the credential
  itself into the transcript.

Rewrite both to quiet scans: count/filename output only
(`git diff --cached | grep -cE '<patterns>'`, `grep -lE` style, or
`--name-only` reporting), report pass/fail + offending FILENAMES,
never staged bytes. Keep the existing behavior contract: any hit →
unstage, tell the user, wait. Note Step 4c's prose (line ~407) says
"the same staged-content credential scan as Step 2.3" — after the fix
that cross-reference must still be true (both quiet, same pattern
set).

**R2 — post-seeding doctor.** Step 5 currently relays the door's
doctor tail (captured before Step 4's seeding) and gates the launch
line on it — so it can WARN about things the seeding already cured
(TASK_PREFIX fill, backlog). After the Step 4c seeding commit, run
`agentive doctor` in the planning repo and use THAT output for the
checklist ✓/✗ lines and the launch-line gate. Keep relaying the
door's original tail verbatim as well — the door's exit contract
remains the INSTALL truth; the re-run is REPO-STATE truth. Label the
two so they can't be conflated.

**Version bump (same PR, manual until KIT-0111)**: frontmatter
`version: 1.2.0` → `1.3.0` (R2 adds behavior), refresh `last-updated`.

### Leg 2 — release 2.1.1 (marketplace PR)

After leg 1 merges, the drift guard goes red-by-design (rostered
component changed). Cut the release same-day per the standing ruling
(plugin-drift.yml header):

- `scripts/local/plugin_resync.py` — three-way merge, never copy
  (base = kit blob at previously-rostered hash). project-intake
  carries NO published adaptation (those are fd, fd-f5, self-review),
  so expect a clean merge — but let the tool say so, don't assume.
- Plugin `2.1.0 → 2.1.1` (membership unchanged → patch), ALL FOUR
  version fields; CHANGELOG with explicit empty categories (the
  upgrader reads it).
- Marketplace CI: `verify_plugin_integrity.py` is a REQUIRED check —
  it must pass (28/28) before merge.
- Bot budget: ONE substantive round baseline. CodeRabbit AND BugBot
  are both active on the marketplace repo (verified across #10/#11).
- After the marketplace merge: verify drift guard GREEN on kit main.

## Verified anchors (2026-08-16 — re-verify before relying)

Class grep run at handoff time:
`grep -n "diff --cached\|staged" .claude/agents/project-intake.md` →
4 hits, all in scope:

- `:212–220` — Step 2.3 staged-scan instruction (grep-echo leak)
- `:403` — Step 4c `diff --cached  # scan this output` (full-diff leak)
- `:407–409` — Step 4c prose tying its scan to Step 2.3
- `:214–215` — the "mandatory secret scan" framing (keep; only the
  echoing mechanics change)

Step 5 anchors: `:411–429` — verified-✓-at-print-time rule, verbatim
doctor-tail relay (`:425–426`), launch-line gate on no-FAILs
(`:427–429`). Frontmatter: `version: 1.2.0` at `:5`.

Acceptance falsifier: after the fix, re-run the class grep — zero
remaining instructions that echo staged content or matched lines;
paste the grep + output in the PR body (displayed commands are
contracts).

## Test approach

- This is a canon (markdown agent-body) change: markdownlint +
  pre-commit fast tests (~77s) must pass; no Python surface changes
  expected. If you find yourself editing scripts, stop — scope check.
- Prove R1 by the class grep (above) in the PR body.
- Prove R2 by quoting the rewritten Step 5 sequence in the PR body
  (door tail verbatim + post-seeding re-run labeled).
- Evaluator: run the code-review evaluator per the standing skill
  before opening each PR (`echo y | ADVERSARIAL_UNATTENDED=1
  adversarial <evaluator> <input>`; read the LOG, not the exit code).
- Bot truth = reviewThreads GraphQL with `hasNextPage` fail-closed
  counting (the KIT-0112 query); SHA-match approvals to head.

## Out of scope — do not touch

- The published plugin copy of project-intake under
  `~/Github/agentive-skills` in LEG 1 — it changes only via
  `plugin_resync.py` in leg 2.
- The door/doctor implementation (`agentive_kit/`) — R2 re-runs the
  doctor, it does not change it. Doctor gaps discovered → file in
  `1-backlog/`.
- The intake e2e acceptance test from KIT-0105 — if it pins prose you
  change, update the pin in the same commit and say so in the PR body;
  do not restructure the test.
- Other backlog intake ideas (KIT-0103 R2 door detect-and-warn etc.) —
  park discoveries in `1-backlog/`.

## Working agreement (operator preference, standing)

Be interactive: surface blockers and decisions as they arise
(AskUserQuestion or a direct question), state what you'll do next at
each gate, and when you finish a leg, SAY what the next action is
rather than idling. If a gate blocks you, name the blocker and your
recommended path.

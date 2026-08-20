# Planner Handoff — 2026-08-20 — dispatch-kit arc & review pipeline

**From**: planner-f5 session "2026-08-18 PF5 Figure out what to do with dispatch-kit"
**To**: next planner session
**Repo state**: kit `main` @ `790e931`, pushed, tree clean. Marketplace repo
was on `main` when last checked (2026-08-18) — re-verify before ops.

## What this session decided and shipped (all committed + pushed)

| Commit | What |
|---|---|
| `e7f5011` | KIT-0116 spec filed (2-todo) + KIT-0117 filed (backlog) |
| `b5f2a60` | KIT-0117 widened: plugin survey found 5 live `dispatch emit/log` steps |
| `790e931` | **KIT-ADR-0035** (Accepted) + renumbering + index fixes |

1. **Operator decision (2026-08-18): salvage dispatch-kit's ideas, then
   archive the repo.** Rationale + landscape evidence recorded in
   KIT-ADR-0035 (`.kit/adr/`). Landscape research (verified vs
   code.claude.com + GitHub API 2026-08-18): Claude Code v2.1.224+ ships
   cross-session messaging natively; Agent Teams (experimental flag),
   Agent View, background subagents; third-party tmux orchestrators
   dead/stale; MCP bus category never took off.
2. **KIT-0116 — automated review pipeline** (`2-todo/`, evaluation gate
   PASSED: arch-review-fast ×2 + arch-review/o3, all findings folded in).
   Three tiers: `/code-review` default-on every non-trivial task;
   architecture/security/docs **flag-triggered** via `Review Flags` set by
   planner at spec time (heuristics to live in future REVIEW-PIPELINE.md —
   single authority); background read-only reviewer subagents
   (KIT-ADR-0036 reserved for the delegation carve-out); opt-in
   deep-review workflow. Operator confirmed: code-review always-on, rest
   flag-routine. **Not started — operator wanted spec + eval only, no
   jumping in.**
3. **KIT-0117 — dispatch-kit salvage + archive** (`1-backlog/`). Includes
   req 0: strip the 5 live dispatch CLI steps from plugin commands
   (start-task, preflight, check-ci, commit-push-pr, status) AND kit
   twins, on a release train. Provenance frontmatter (`origin:
   dispatch-kit`) stays.

## Critical constraint — do NOT uninstall the global dispatch CLI

`which dispatch` → `/Library/Frameworks/Python.framework/Versions/3.11/bin/dispatch`
is ARMED (fire-and-forget steps execute and write `.dispatch/`), **but DTL
retained `.dispatch/` as a live dispatch-kit 0.4.2 writer (operator choice
2026-08-19, DTL-0026)**. KIT-0117 gates CLI teardown on resolving DTL
first; repo archive is independent. See KIT-ADR-0035 "Known constraint".

## Next actions (in suggested order)

1. **When operator says go on KIT-0116**: produce Phase-1 handoff +
   starter (fd, worktree per WORKTREE-WORKFLOW ordering rule, 3-PR plan —
   phases independently shippable). Spec is eval-complete; no further
   rounds needed (3-round limit reached).
2. **Release-train pairing**: KIT-0117's command-stripping should ride the
   same plugin release as KIT-0115 (ninth face); KIT-0111 (version-bump
   guard, medium) is the recommended next task overall. Suggest bundling
   when kit work resumes.
3. **Parked by operator, do not initiate unprompted**: cross-session
   messaging demo (can ride KIT-0117 close-out); dispatch-kit repo
   archive (operator action).

## Numbering / consistency notes

- KIT-ADR-0036 is RESERVED (read-only reviewer delegation), authored
  within KIT-0116 Phase 2 — next free ADR is 0037; re-verify at authoring.
- ADR index (`about-kit-adr.md`): 0030/0031 corrected to Accepted;
  0035/0036 rows added.
- Evaluator logs: `.adversarial/logs/KIT-0116-*` (fast log was overwritten
  by round 2 — round 1 findings are recorded in spec edit annotations).

## Session lessons (for retro / awareness)

- `adversarial` CLI: round-2 run printed "verdict: None" with exit 0 —
  verdict extraction failed on format; the log had a real verdict. Read
  the log, never the exit/stdout (existing gotcha, new face).
- Backlog now: KIT-0103 (R2/R3/R5/R6), KIT-0106, KIT-0107+0108, KIT-0111
  (recommended next), KIT-0114, KIT-0115, KIT-0117 + KIT-0116 in 2-todo.
  DTL fallout issues #138–#143 also open (see memory).

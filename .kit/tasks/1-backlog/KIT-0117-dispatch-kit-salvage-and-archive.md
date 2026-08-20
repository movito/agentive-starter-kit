# KIT-0117: dispatch-kit — write salvage close-out note and archive the repo

**Status**: Backlog
**Priority**: low
**Assigned To**: planner (operator-assisted — GitHub archive is an operator action)
**Estimated Effort**: 1-2 hours
**Created**: 2026-08-18
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Depends On**: KIT-0116 (spec exists and carries the salvage mapping — satisfied; full closure ideally after KIT-0116 ships so the note can cite the landed implementation)
**Related**: KIT-0077 (retired `.dispatch` gitignore entries from the kit)

## Status History

- **Backlog** (from —) - 2026-08-18

## Overview

Operator decision (2026-08-18): **salvage ideas, then archive** dispatch-kit
(`~/Github/dispatch-kit`, DSP prefix, dormant since 2026-03-21).

Rationale, evidenced by 2026-08-18 landscape research (verified against
code.claude.com docs + live GitHub API): Claude Code now natively ships
dispatch-kit's core mission — cross-session messaging (v2.1.224+, default-on,
socket-based, no tmux), Agent Teams (experimental), Agent View, background
subagents. The third-party tmux-orchestrator category is dead/stale since
mid-2025; MCP message-bus projects never exceeded single-digit stars. The
niche became a platform feature. dispatch-kit's durable concepts (transition
rules, gates, trust modes) are salvaged as design input to KIT-0116
(Appendix A there is the canonical mapping).

## Plugin survey (VERIFIED by grep, 2026-08-18 planner session)

`grep -rniE "dispatch (emit|log|watch|spawn)|origin: dispatch-kit"` over
`~/Github/agentive-skills/plugins` and kit `.claude/`:

- **Live CLI steps in FIVE plugin commands** (twins in kit
  `.claude/commands/`): `start-task` (emit task_started), `preflight`
  (emit preflight_complete), `check-ci` (emit ci_verified),
  `commit-push-pr` (emit pr_created), `status` (dispatch log --since 2h).
  All fire-and-forget (`2>/dev/null || true`) — but NOT inert here:
- **Global dispatch CLI still installed**: `which dispatch` →
  `/Library/Frameworks/Python.framework/Versions/3.11/bin/dispatch`
  (KIT-0077 mechanism, still armed — steps execute and write `.dispatch/`
  into consumer repos). Kit `settings.local.json:207` carries a
  `Bash(dispatch emit:*)` allow-entry.
- **Provenance frontmatter** `origin: dispatch-kit` on 14 commands/skills
  + historical notes (README, CONSOLIDATION, CHANGELOG, check-spec,
  code-review-evaluator): harmless lineage — KEEP.
- CONSOLIDATION.md records dispatch-kit still holding two vendored
  skill-copy sets; archiving the repo retires those exports.

## Requirements

0. **Strip the five live `dispatch emit`/`dispatch log` steps** from
   plugin commands AND kit twins (copy-not-rederivation; one release
   train — patch/minor bump per versioning rules, CHANGELOG entry;
   precedent: wrap-up's phase_complete emit was removed the same way).
   Remove the `Bash(dispatch emit:*)` allow-entry from
   `settings.local.json`. `origin:` frontmatter stays.
1. Write `RETROSPECTIVE.md` (or README banner section) in the dispatch-kit
   repo: what it set out to do, what it got right (bus/matcher/gates design,
   tmux quarantined in 2 modules, 945 tests/94% cov), why it's archived
   (platform ate the niche — cite the landscape findings), and where the
   ideas live on (link to KIT-0116 / KIT-ADR from that task).
2. Point README status line at the retrospective; mark project archived.
3. Check for anything still writing to `.dispatch/` paths (KIT-0077
   lesson: the globally-installed dispatch CLI kept emitting after the
   workflow retired it). Verify with `which dispatch` + grep of shell
   profiles/launchd. **DTL CONSTRAINT (KIT-ADR-0035)**: DTL retained
   `.dispatch/` as a live dispatch-kit 0.4.2 writer (operator choice
   2026-08-19, DTL-0026) — do NOT uninstall the global CLI until DTL is
   migrated off the writer or the CLI is explicitly scoped DTL-local.
   Repo archive proceeds independently of this step.
4. Operator: archive the GitHub repo (Settings → Archive). Planner cannot
   and must not do this.
5. Update kit memory: dispatch-kit → archived, pointer to KIT-0116.

## Acceptance Criteria

- [ ] Plugin commands + kit twins carry NO `dispatch emit`/`dispatch log`
      steps (grep evidence); shipped on a release train with CHANGELOG
- [ ] Retrospective committed to dispatch-kit `main`
- [ ] Global `dispatch` CLI: DTL dependency resolved first, THEN removed
      or explicitly scoped DTL-local (evidence: command output + DTL
      status; see KIT-ADR-0035 Known constraint)
- [ ] GitHub repo archived (operator confirms)
- [ ] Memory updated

## Notes

- No code deletion — archive preserves everything.
- The demo of native cross-session messaging (operator requested "later")
  can piggyback on this task's close-out session.

---

**Created**: 2026-08-18
**Maintained By**: planner-f5

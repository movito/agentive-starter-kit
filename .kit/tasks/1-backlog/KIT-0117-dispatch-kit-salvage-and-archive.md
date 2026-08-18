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

## Requirements

1. Write `RETROSPECTIVE.md` (or README banner section) in the dispatch-kit
   repo: what it set out to do, what it got right (bus/matcher/gates design,
   tmux quarantined in 2 modules, 945 tests/94% cov), why it's archived
   (platform ate the niche — cite the landscape findings), and where the
   ideas live on (link to KIT-0116 / KIT-ADR from that task).
2. Point README status line at the retrospective; mark project archived.
3. Check for anything still writing to `.dispatch/` paths (KIT-0077
   lesson: the globally-installed dispatch CLI kept emitting after the
   workflow retired it). Verify with `which dispatch` + grep of shell
   profiles/launchd; uninstall the global CLI if present.
4. Operator: archive the GitHub repo (Settings → Archive). Planner cannot
   and must not do this.
5. Update kit memory: dispatch-kit → archived, pointer to KIT-0116.

## Acceptance Criteria

- [ ] Retrospective committed to dispatch-kit `main`
- [ ] Global `dispatch` CLI confirmed absent or uninstalled (evidence: command output)
- [ ] GitHub repo archived (operator confirms)
- [ ] Memory updated

## Notes

- No code deletion — archive preserves everything.
- The demo of native cross-session messaging (operator requested "later")
  can piggyback on this task's close-out session.

---

**Created**: 2026-08-18
**Maintained By**: planner-f5

# KIT-0126: preflight Gate 8 reads the review-pass record CWD-relative — false FAIL in split mode

**Status**: Todo
**Priority**: high (every split-mode consumer gets a false Gate 8 FAIL; fails closed, never a false pass)
**Type**: Canon fix (`.claude/commands/preflight.md`, `.claude/agents/feature-developer*.md`)
**Estimated Effort**: ~1 h
**Created**: 2026-10-18
**Source**: BugBot + CodeRabbit on agentive-skills#13 (release 2.2.0,
KIT-0124), threads PRRT_kwDOSj0O5s6tlvCP and PRRT_kwDOSj0O5s6tlviY.
Deferred at the marketplace per KIT-0097 (fix-here-then-release);
operator chose to ship 2.2.0 with the bug and fix it in 2.2.1.

## Observed

`preflight.md` Step 1b checks:

```bash
rec=.kit/context/reviews/<TASK-ID>-review-pass.md; [ -f "$rec" ] && [ -s "$rec" ] && ...
```

The comment above it says "Planning repo", but the path is relative to
the current directory. In split mode feature-developer sits in the
TARGET worktree (fd "First, fix `$PLANNING`" section) and runs
preflight from there in Phase 8. Phase 5b persists the record under
`"$PLANNING"/.kit/context/reviews/`, so a correctly persisted record
reads as FAIL. The cross-repo section claims gates 5–8 read the
planning repo; only the CLI-backed gates 5–7 actually do.

## Scope

- R1 — Step 1b resolves the planning root before the check (same
  derivation fd uses: `git rev-parse --show-toplevel` in single-repo
  mode; the handoff's Session topology path in split mode). Keep the
  `-f && -s` rule and the PASS/FAIL output unchanged.
- R2 — fd Phase 8 checklist line ("Native review pass persisted
  (`.kit/context/reviews/...`)") uses `"$PLANNING"/` in both
  `feature-developer.md` and `feature-developer-f5.md` (and
  `feature-developer-o55.md`, pair-synced).
- R3 — Class grep: every CWD-relative `.kit/` path in the commands
  and agents that run in split mode; fix or list each.
- R4 — Mechanize Gate 8 in the `agentive preflight` CLI so it uses
  the same planning-repo resolution as gates 5–7 (already filed as
  KIT-0120; link, don't duplicate).

## Acceptance

- [ ] Split-mode fixture: record present in planning, preflight run
      from target worktree → Gate 8 PASS
- [ ] Single-repo fixture unchanged (PASS/FAIL as before)
- [ ] R3 class grep recorded with each hit's disposition
- [ ] Plugin 2.2.1 release cut from the fixed kit tree; reply on both
      agentive-skills#13 threads with the release link

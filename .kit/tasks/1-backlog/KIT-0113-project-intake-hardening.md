# KIT-0113: project-intake hardening — quiet credential scan + post-seeding doctor

**Status**: Backlog
**Priority**: medium (one Critical-severity bot finding; contained — operator's own transcript)
**Type**: Canon fix (`.claude/agents/project-intake.md`)
**Estimated Effort**: ~1 h
**Created**: 2026-08-15
**Source**: CodeRabbit on agentive-skills#11 (release 2.1.0), threads
PRRT_kwDOSj0O5s6ZiCNh (Critical) + PRRT_kwDOSj0O5s6ZiCNi; declined at
the marketplace per KIT-0097 (fix-here-then-release). Filed by the
planner from the KIT-0105 PR 3 handover (two tail lines of the
handed-over draft arrived truncated; repaired at filing, planner
2026-08-15).

## R1 — quiet credential scan (Critical)

Step 4c instructs `git diff --cached  # scan this output` — printing
staged content into the transcript can leak a credential BEFORE the
scan rejects it. Same class exists in Step 2.3's staged-scan step.
Rewrite both to a quiet scan: grep staged content without echoing it
(`git diff --cached | grep -cE '<patterns>'` style), report only
filenames / pass-fail — never staged bytes. Class grep: every
`diff --cached` / staged-content instruction in the agent body.

## R2 — post-seeding doctor for the completion checklist

The door's doctor tail predates Step 4's seeding (TASK_PREFIX fill,
backlog), so Step 5 relays a WARN the seeding already cured. After the
seeding commit, run `agentive doctor` in the planning repo and use
THAT output for the checklist and the launch-line decision (keep
relaying the door's original tail verbatim too — the door's exit
contract stays the install truth; the re-run is repo-state truth).

## Acceptance

- [ ] No step prints staged file contents into the transcript
      (falsified by the class grep: zero echoing staged-scan
      instructions remain)
- [ ] Step 5's checklist consumes a post-seeding doctor run; launch
      line gated on it
- [ ] Rides the next plugin release (drift guard red-by-design between
      merge and that cut; version bump on the touched component)

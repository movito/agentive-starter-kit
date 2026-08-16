# KIT-0113: project-intake hardening — quiet credential scan + post-seeding doctor

**Status**: Done
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

- [x] No step prints staged file contents into the transcript
      (class grep clean; three sites fixed, not two — Step 2.1's bare
      `git grep` printed matched LINES, outside the spec's grep)
- [x] Step 5's checklist consumes a post-seeding doctor run; launch
      line gated on it, door tail still relayed verbatim under a
      distinct label
- [x] Rides the plugin release: **2.1.1 merged** (agentive-skills#12,
      `d0800f3`); drift guard verified **GREEN** on kit main by
      workflow_dispatch run 31980414599 at `e75de7c`
- [x] Component version bumped — 1.2.0 → **1.3.2** (three kit PRs; see
      Outcome)

## Outcome (fd, 2026-08-17)

Scope grew beyond the two findings: the credential gate was rebuilt
across three kit PRs, each round exposing a defect created by the
previous fix.

| PR | Component | What it fixed |
|----|-----------|---------------|
| #135 | 1.2.0 → 1.3.0 | R1 quiet scans (3 sites), R2 post-seeding doctor, shell-level commit gate |
| #136 | → 1.3.1 | Step 2.3 twin: `add -A` unchecked, inverted block status, blocked branches returning 0, `set -e` killing the CLEAN path |
| #137 | → 1.3.2 | `-I` skipped binaries so a staged binary credential scanned CLEAN (fail-open); prose stated raw-grep polarity as the decision rule, contradicting the normalized gate |

Fifteen bot/evaluator findings: fourteen real and fixed, one declined
(CodeRabbit asking for the roster update in the kit PR — the roster
lives marketplace-side and the resync must read kit main first).

Two of the defects were mine to own twice over: the `-I` binary
bypass was raised pre-PR by a security evaluator and I filed it as a
"deployment policy question" instead of testing it; and `|| scan=$?`
was proposed by CodeRabbit on the first release round, declined as "a
moving part without a job", then restored two PRs later when `set -e`
proved it had one.

Pattern recorded: `harden_twins_by_copy_not_rederivation` in
`.kit/context/patterns.yml`.

**Follow-up recommended (not filed):** extract the gate into a small
tested script the agent invokes. Executable logic living in prose
across three sites that must agree by hand is what produced the
polarity contradiction; a script gives the contract one home and a
test.

## Release scoping (planner, 2026-08-16)

No other release is queued, and the drift ruling (plugin-drift.yml
header) makes red a same/next-day release obligation — so this task
CUTS the release itself as a second leg, per the KIT-0109/0110/0105
precedent: marketplace PR on `~/Github/agentive-skills` via
`scripts/local/plugin_resync.py` (three-way merge, never copy).
Versions: component `project-intake.md` 1.2.0 → **1.3.0** (R2 adds
behavior; bump is MANUAL until KIT-0111); plugin membership unchanged
→ **2.1.0 → 2.1.1** (all four version fields; CHANGELOG with explicit
empty categories). Note: project-intake carries no published
adaptation (the three adapted components are fd, fd-f5, self-review) —
expect a clean merge, but let the tool say so.

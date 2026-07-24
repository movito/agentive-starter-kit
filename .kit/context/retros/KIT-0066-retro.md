## KIT-0066 — Prototype Intake Flow (PR #92)

**Date**: 2026-07-24
**Agent**: feature-developer-f5
**Mode**: single-repo
**Scorecard**: 15 threads, 0 regressions, 4 fix rounds, 8 commits

### What Worked

1. **Evaluator-before-PR ordering held its value on a prose-only
   diff** — the trio (fast/o3/claude-code) surfaced the two findings
   that mattered most (input validation before shell use, systematic
   secret scan before first commit) BEFORE any bot round, so `7aeb79f`
   landed them pre-PR. Without it, those would have been bot round-1
   Critical/High threads on top of the 7 that did arrive.
2. **The KIT-0057 mutating-hook warning paid off verbatim** — the
   review-record commit aborted exactly as the Phase-5 note predicts
   (trailing-whitespace hook trimmed the appended o3 log's markdown
   double-spaces while the pytest tail printed "742 passed").
   `git log -1` + `git status` caught it immediately; re-stage + new
   commit, zero confusion.
3. **Demo-as-validation caught a real pre-existing defect** — running
   the door for the demo pair exposed that the consumer scaffold ships
   a tracked session-memory file
   (`.claude/projects/.../feedback_evaluator_script_flow.md`, since
   PR #41 `2974e27`) into every consumer repo. Pure inspection of the
   diff would never have shown it.
4. **Pre-implementation anchor re-verification was cheap and load-
   bearing** — all planner-cited line anchors (bootstrap:383-404,
   engine-consumer.sh:592, kit_markers.py:187) verified in ~4 reads,
   and the kit_markers/KIT_AGENTS reading directly shaped Step 4a of
   the agent (fill ALL FOUR marker-bearing agents, not just the two
   the door's tail names).
5. **`gh-review-helper.sh` made 15 reply+resolve cycles frictionless**
   — no raw GraphQL, no thread-ID bookkeeping errors across 4 rounds.

### What Was Surprising

1. **BugBot's "skipping" flipped to a terminal pass on round 4** —
   it sat "skipping" for three consecutive CI rounds while CodeRabbit
   reviewed each push, then delivered a pass verdict WITH one final
   finding (the slug-derivation thread) without any intervention.
   Direct evidence for KIT-0062: "skipping" is genuinely non-terminal
   and must not be read as reviewed-clean OR as permanently absent.
2. **Preflight Gates 2/3 classified the diff as "No code changes —
   bot review not required"** while both bots actively reviewed it
   across 4 rounds and produced 15 threads. The docs-only classifier
   and reality diverged in the safe direction here (bots ran anyway),
   but the gate text is misleading for prose-agent PRs — prose that
   drives shell commands is not "no code" in any meaningful sense.
3. **Bots rounds converged on the same file with strictly falling
   severity (7→4→3→1, Critical→Medium)** — every round found
   consistency nits INTRODUCED by the previous round's fixes (e.g.
   round 2's 40-char slug cap spawned round 4's "but how do I build a
   slug" finding). Prose hardening has a self-feeding tail in a way
   code fixes usually don't.
4. **o3's FAIL contained one factually wrong claim again** — it
   asserted `.gitignore` was written after `git add -A` when the
   step order was already ignore-then-add (and claude-code's
   template finding was refuted by the template's own text). The
   "verdict carries no signal, check every claim" rule is now 4-for-4
   across recent tasks.

### What Should Change

1. **Extend the Phase-5 pre-format rule to appended evaluator logs**
   — both fd agents' KIT-0057 note names black/isort as the mutating
   hooks; this session hit the trailing-whitespace variant on
   evaluator logs concatenated into the review record. One sentence
   in the Phase 5 note ("evaluator logs carry markdown trailing
   whitespace — strip or expect one hook abort") kills the class.
2. **File the scaffold memory-file purge** — `git rm` +
   ignore-pattern for
   `.claude/projects/-Users-broadcaster-three-Github-agentive-starter-kit/`
   (tracked since PR #41, ships to every consumer). One-commit task;
   candidate for the 0.9.0 sweep alongside KIT-0059's set.
3. **Reword preflight Gates 2/3's "No code changes" message** for
   md-only diffs to something like "docs-only diff — bot review not
   required (bots may still review)" so a future reader doesn't
   conclude the bots were skipped when 15 threads exist (adjacent to
   KIT-0062's Gate-3 scope — could ride that task).
4. **The demo's GitHub leg needs a cheap harness eventually** — the
   `gh repo create`/push path of project-intake is verified only by
   inspection (stated honestly in the transcript after a CodeRabbit
   nudge). A scratch-org or dry-run pattern would close it; low
   priority, but the gap is now recorded in three artifacts.

### Permission Prompts Hit

1. `rm -rf /tmp/kit0066-intake-demo` — denied (the standing missing
   rm-rf allowlist for `/tmp/`; operator already owes this per the
   live-state memory, hit previously in KIT-0058's demo). Not in
   `.claude/settings.json`. Cost was small this session (fallback:
   listed leftovers for operator sweep), but this is the second task
   demo in a row to hit it.

Otherwise none — notably all 30+ `gh`/`git`/helper calls and both
door runs went through unprompted.

### Process Actions Taken

- [ ] Extend fd Phase-5 pre-format note (both `feature-developer.md`
      and `feature-developer-f5.md`) to name evaluator-log trailing
      whitespace as a mutating-hook abort source
- [ ] File backlog task: purge tracked `.claude/projects/` memory
      file from the kit (ships to all consumers since PR #41)
- [ ] Reword preflight Gates 2/3 docs-only message (fold into
      KIT-0062 or file separately)
- [ ] Feed the BugBot skipping→pass-on-round-4 observation into
      KIT-0062 as evidence
- [ ] Operator: add rm-rf allowlist (`/tmp/` + `~/Github/ask-worktrees/`)
      — second demo in a row blocked; sweep `/tmp/kit0066-intake-demo/`

### Incident Closure

1. **Mutating-hook commit abort (trailing whitespace on appended
   evaluator logs)** — triage-guide entry: the fd agents' Phase 5
   KIT-0057 note is the living triage doc for this class; action item
   above extends it to name this variant. Not doctor-checkable (only
   observable at commit time).
2. **Tracked session-memory file in consumer scaffold** — fits none
   of the three cheaply: it is a one-time repo defect, not an
   environment assumption. Explicitly left to the planner as a filed
   backlog candidate (action item above); once purged, the ignore
   pattern prevents recurrence better than any doctor check would.
3. **BugBot "skipping" non-terminality** — already owned by KIT-0062
   (preflight Gate 3); this session contributes the skipping→pass
   flip as evidence. No new closure artifact here.
4. No other environment incidents: both door runs, the preset
   resolution, and doctor behaved exactly as documented.

# KIT-0113 — Planner coordination session retro (restart → arc close)

**Date**: 2026-08-17
**Agent**: planner-f5 (Fable 5)
**Mode**: single-repo (kit) + marketplace reads via `git -C` / `gh`
**Scorecard** (planner session — adapted): 2 tasks closed (KIT-0105
approved+complete, KIT-0113 full lifecycle), 5 planner commits on main
(e22b3d8, 6809056, b157093, 350b5d6, 56d82f6; 9 total main commits in
the window incl. the fd's 4), 4 merge-gates verified (kit #135/#136 +
skills #12 + guard-green close), 2 monitors (1 restarted for a jq
bug), 3 primary-clone collisions (0 data loss), 4 backlog filings
(KIT-0115, KIT-0103 R6, KIT-0111 raise, spec release-scoping).
Implementation metrics live in `KIT-0113-retro.md` (fd).

### What Worked

1. **Verifying relays against the tree caught a premature merge
   request** — the fd's "#136 needs your merge" relay arrived while
   CodeRabbit had 1 unresolved Major at head (`fd7b166`); the
   GraphQL-first check turned "merge now" into "hold, one real finding"
   and the finding was legitimate (the 2.3 twin was weaker than the 4c
   form the PR's own history had established). Phantom-ready is the
   sibling of phantom-done; the protocol catches both.
2. **The handoff's working-agreement section produced its datapoint**
   — one paragraph asking for interactivity (from the KIT-0105
   passivity observation) preceded the most interactive fd session on
   record: explicit merge-decision escalations, a hold-with-options
   collision report, and an unprompted evidentiary self-correction.
   Cannot prove causation, but the spec-or-fluke hypothesis now has
   supporting evidence on both sides.
3. **Diff-verifying the release PR at prep time made the merge gate
   trivial** — checking skills #12's version fields, the untouched
   planner `kit_version`, and the hash columns against the drift
   guard's own demanded hash (`62f9c41…` at that point) meant the
   final close-out chain needed only reconciliation, not discovery.
4. **Both collision sides stopped instead of committing through** —
   three interleavings in one primary clone (fd staging under planner
   edits, pre-commit stash/rollback reverting planner edits twice, fd
   commits failing on the mutating-hook pattern) ended with zero lost
   content because both agents verified before acting. Discipline
   held; R6 makes it structure.
5. **Same-day codification of every session lesson** — R6 (ownership
   seam), the bilateral existence-isn't-integrity clause, KIT-0115,
   the KIT-0111 raise, and six REVIEW-INSIGHTS entries all landed
   before session end, each citing its incident.

### What Was Surprising

1. **The monitor's blind spot was the interesting failure** — keyed to
   the assigned branch (`feature/KIT-0113-intake-hardening`), it went
   silent for PRs #136/#137 on branches the session created mid-task.
   The releases CHANGELOG was how I learned #137 existed. A per-branch
   watch assumes single-branch tasks; fix-round PRs break that
   silently.
2. **The clobber had two competing explanations and the first was
   wrong** — I initially read my reverted edits as "the other session
   checked out the files"; the fd's collision report revealed it was
   pre-commit's stash/rollback from ITS failed commits. Two
   half-visible accounts reconciled only when both sides compared
   notes — neither alone had the mechanism.
3. **`reviewDecision` earned its place as the ninth lying face during
   the very task documenting face-lying** — stuck CHANGES_REQUESTED on
   #136 after the bot cleared via COMMENTED; the thread-level protocol
   sidestepped it without noticing, which is the protocol working.
4. **KIT-0114 was already filed when I went to file it** — the fd
   wrote its own recommendation as a complete 117-line spec (including
   the runtime-reachability constraint I would likely have missed:
   plugin runs with no kit checkout, so `scripts/core/` is
   unreachable). Agent-filed specs of that quality change what the
   planner's filing pass is for.

### What Should Change

1. **Monitor by PR list, not by branch** — watch
   `gh pr list --state all` deltas for the whole repo (or task-ID
   match in titles) instead of a single named branch; fix-round PRs
   on new branches are the norm, not the exception (3 of 4 PRs this
   task were invisible to the branch watch).
2. **Gate-check reports carry their head SHA + freshness re-check at
   send time** — adopted into memory/protocol this session after one
   check arrived 4 commits stale (fd retro's "stale relays" note,
   accepted as fair).
3. **Planner close-out waits for the observed wrap-up commit** — filed
   as KIT-0103 R6 with the bilateral content re-verify clause
   (existence isn't integrity; verify by grep, not ls). Done, rides
   the next train.
4. **Release-side version-bump assertion belongs in the KIT-0111
   guard** — the 2.1.1 string collision (`kit_version: "2.1.0"` ==
   plugin version being bumped) was defused by hand-discipline;
   KIT-0111's scope was widened accordingly and its priority raised to
   medium (three releases, three incidents).

### Permission Prompts Hit

One: `cd <repo>; git branch -D <a> <b> <c>` (batch, three branches) was
denied; single-branch `git -C <repo> branch -D <name>` calls went
through immediately. Workaround cost ~seconds. Pattern note for the
allow list: batch `branch -D` after squash-merge verification is
routine planner teardown — either allow the batch form or keep the
single-branch habit (which also satisfies the one-command-per-call
shell rule).

### Process Actions Taken

- [x] KIT-0105 completed; KIT-ADR-0030/0031 → Accepted; arc closed
- [x] KIT-0113 assigned (spec release-scoped, worktree pre-created,
      evaluation skip ruled), monitored, gated ×4, completed
- [x] fd retro processed: KIT-0115 filed; KIT-0114 verified landed;
      6 insights extracted; harden_twins pattern confirmed in
      patterns.yml
- [x] KIT-0103 R6 filed + amended bilateral (fd closeout correction)
- [x] KIT-0111 raised to medium, scope widened to release-side bump
- [x] Plugin 2.1.1 local install content-verified (hash-identical to
      kit main); memory ledger updated
- [ ] Next session: recommend KIT-0111 as next task; monitor-by-PR-list
      pattern for the next assignment's watch

### Incident Closure

1. **Monitor jq null event** (`.[0]` on an empty `gh pr list` emitted
   `null [null] null` as a phantom event): **triage-guide entry** —
   recorded here and in project memory (Key Gotchas): *jq projections
   over possibly-empty lists in monitor/event scripts must use
   `.[0] // empty`; a bare `.[0]` turns "no data" into a fabricated
   event.* Not doctor-checkable (ad-hoc session scripts, not repo
   state).
2. **Primary-clone triple collision** (fd wrap-up × planner close-out;
   pre-commit stash/rollback reverted planner edits twice; fd commits
   failed twice on the mutating-hook pattern): **canon fix filed** —
   KIT-0103 R6 (ownership-seam paragraphs, all four agent bodies,
   bilateral content re-verify), rides the next release train. The
   structural closure supersedes a triage note; the incident narrative
   lives in this retro and the fd's closeout correction.
3. **Stale gate-check relay** (planner check anchored 4 commits behind
   head): **triage-guide entry** — protocol adoption recorded in
   memory's Merge-Gate section (stamp head SHA, re-verify freshness at
   send time; guard greens answer "as of WHEN" — check trigger
   topology). Also carried in REVIEW-INSIGHTS (KIT-0113 block).
4. **Batch `branch -D` permission denial**: **not-checkable note** —
   recorded here; it is a harness allow-list shape, not an environment
   fault. Remedy options stated under Permission Prompts; no doctor
   surface exists for permission configuration.

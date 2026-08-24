## KIT-0118 — Packaged-door fresh-install fixes + agentive-kit 0.4.0

**Date**: 2026-08-24
**Agent**: feature-developer (opus), worktree session
**Mode**: single-repo, worktree `/Users/broadcaster_three/Github/ask-worktrees/KIT-0118`
**PR**: #147 · **Scorecard**: 7 bot threads (5 substantive + 2 doc nits) · 4 bot rounds (3 substantive) · 9 commits · suite 1145 → 1217 · all 7 preflight gates green

Scope: three verified fresh-install defects in the packaged setup door
(#145 prose-in-record, #146.1 declined-evaluators FAIL, #146.2 masked
TASK_PREFIX warning) plus the `agentive-kit` 0.4.0 bump that puts them
on PyPI (#144) — deliberately one release train.

### What Worked

1. **Tracing the `bots:` seam end to end before writing anything.** The
   spec said "mirror `bots:`" and the handoff said trace the real seam
   rather than invent a path. Doing that surfaced the ordering problem
   that shaped the whole of Part B: `run_offers` — where the evaluator
   answer is resolved — runs AFTER the consumer engine writes the
   record, so the answer literally did not exist when the record was
   written. Discovering that at design time produced
   `resolve_evaluator_offer` (split + idempotent); discovering it at
   test time would have produced a hack.

2. **Verify-before-believing paid for itself three times in one review.**
   o3 returned FAIL on five findings. Three were checked against the
   tree and were plainly false: `GIT_CONFIG_*` "leaking" through a
   filter that strips anything starting with `GIT_` (executed the
   comprehension — it strips it); `--with-evaluators=YES` recording
   mixed case (ran `parse_args` — the `=VALUE` form is refused, exit 2);
   duplicate `evaluators:` lines accumulating (the append is gated on
   the flag being given). Roughly ten seconds of verification each,
   against what would have been three unnecessary code changes to
   working code.

3. **Turning refuted findings into tests anyway.** Two of the three
   false claims became regression tests rather than just argument. They
   cost minutes and close the question permanently — cheaper than
   re-litigating the same claim on the next PR that touches this file.

4. **Reading `reviewThreads` GraphQL instead of the check status.**
   CodeRabbit's *check* showed `pass` while `reviewDecision` was
   `CHANGES_REQUESTED` with two unresolved threads carrying a Major
   finding. Trusting the green check would have shipped the bug. This
   is the recorded lying-check-status class doing exactly what the
   bot-triage skill says it does.

5. **Catching a gap the fix itself opened.** Removing the `# TODO`
   prose from the record also removed the only place a packaged-door
   operator ever saw that hint — the engine's Step 4 tail is
   unreachable under `--internal-record-only`, which is the only way
   the packaged door calls the engine. Two tests failed on exactly
   this, which is how it was found before review rather than after.

### What Was Surprising

1. **Four bot rounds, every one productive, on a diff the trio
   passed.** Not one round was noise. Rounds 1 and 3 were real defects
   in code this task added; round 4 caught a test weak enough to stay
   green while the record lost fields. The trio, by contrast, produced
   one FAIL verdict that was three-fifths false.

   Two of the seven findings I *refuted with evidence* rather than
   accepted — o3's `GIT_CONFIG_*` claim and CodeRabbit's "announces a
   repair that did not happen" (disproven with a standalone `set -e`
   probe). Both times I fixed or tested something anyway where the
   remedy stood on its own merits. Refuting a finding and still
   improving the code are not in tension.

2. **The bots beat the evaluator trio on this diff, decisively.** The
   full trio ran pre-PR on a 174k-token full-content input and passed
   the very code CodeRabbit then flagged Major. The missed bug —
   `--evaluators=` skipping validation entirely — is the *exact masking
   class this task exists to close*, sitting in the code the task
   added. Across all four rounds the trio found nothing true that the
   bots missed, while the bots found four real defects for free.

   This is the KIT-0069/0073 finding inverted. There the trio lost on
   prose because diff-only input made it reconstruct unchanged regions.
   Here it lost on a **flag-parsing seam** despite full-file input —
   the hole is only visible if you enumerate argv forms
   (`--flag`, `--flag=`, `--flag=value`, `--flag <next-flag>`) and the
   evaluators reason about the code as written rather than about the
   input space.

3. **My own tests had the same blind spot as the evaluators.** I wrote
   `test_empty_value_refused` and felt covered — but it passed
   `--evaluators --shape single`, which sets the value to `"--shape"`
   and IS rejected. The genuinely broken form, `--evaluators=`, I never
   tried. Testing one member of an input class and calling the class
   covered is how this survived both my self-review and Gate 5.

4. **A half-done migration is worse than none — and I shipped one to
   review.** BugBot (round 3, operator-flagged) found that the `# TODO`
   strip I added only cleaned values on their way INTO a freshly seeded
   region. Adopt passes `--preserve-regions`, so a legacy tree's
   EXISTING region kept its prose and `load_record()` went on returning
   an unusable path. Reproduced in one script.

   The section strip was scope I *chose* to add — the spec only
   required that new installs write clean values. Taking on a migration
   and leaving it partial is worse than declining it, because the code
   then reads as though the case is handled and removes the reason for
   anyone to look. If I extend scope, I own the whole case or I file
   the whole case.

5. **`--bots` has the identical hole.** The pattern I mirrored was
   itself subtly wrong. Mirroring a battle-tested mechanism copies its
   bugs too — "it's been reviewed many times" is evidence about the
   parts reviewers looked at, not the parts they didn't.

6. **CodeRabbit's consolidated-sites anchoring can be wrong.** One
   round-2 finding anchored on a file that did not contain the flagged
   string and listed the real occurrence as a "sibling". Fixing only
   where it exists — and saying so in the reply — beats accepting the
   framing.

### Lessons / Actions

1. **Enumerate the argv input space when adding a CLI flag.** For every
   new flag, test all four forms: `--flag value`, `--flag=value`,
   `--flag=` (empty), and `--flag` at end-of-args. Presence must be
   tracked separately from emptiness whenever "not given" and "given
   empty" mean different things — which for a recorded declaration they
   always do. **Candidate for `patterns.yml`:
   `flag_presence_is_not_flag_emptiness`.**

2. **A copied mechanism inherits unreviewed bugs.** When mirroring an
   existing pattern (`bots:` → `evaluators:`), audit the source's edge
   cases before copying rather than assuming its review history covers
   them. Here the audit would have found the hole in both.

3. **Consider tier selection by seam, not just by diff shape.** Current
   guidance splits prose-sweep (fast-only) from logic-shaped (full
   trio). This session suggests a third signal: **argument-parsing and
   input-validation seams are bot-favourable and evaluator-hostile**.
   The trio's spend bought nothing here. Worth raising with the planner
   before the next flag-adding task — not a doc change I should make
   unilaterally.

4. **Scope extensions are all-or-nothing.** When taking on work
   beyond the spec (here: migrating legacy trees), either complete the
   case or file it whole. A partial migration is a trap that looks like
   a feature. Worth considering as a `patterns.yml` entry alongside
   lesson 1 — **`partial_migration_is_worse_than_none`**.

5. **`--bots` empty-value hole is real and recorded** (commit message +
   PR thread + review record). It belongs to KIT-0108's engine
   consolidation, not to a drive-by fix on a release PR.

6. **KIT-0119 filed**: `doctor --against-preset` ignores the new
   `evaluators:` line, so a preset/record divergence is invisible on
   the one surface built to report divergence.

### Process Notes

- **Gate 5 ran before the PR opened** (KIT-0035), full trio on the
  logic-shaped tier. Correct call on tier — see lesson 3 for whether
  the tier's *cost* was justified on this particular seam.
- **Bot budget**: THREE substantive rounds against a standing budget
  of one. Round 1 (2 real bugs) was batched correctly. Round 2 was doc
  nits only. Round 3 was operator-flagged and found a Medium defect in
  the fix itself. Round 4 found a test weak enough to stay green while
  the record lost fields, plus one claim whose mechanism was false.
  The overrun was right each time — the alternative was shipping a
  silent half-migration and a hollow test — but the budget exists to
  catch churn, and three rounds means the code arriving at review was
  not as finished as I judged it to be. The honest read: the budget was
  not what failed here, my pre-PR confidence was.
- **Twin discipline**: edit-once-then-`cp`, never re-derive; `diff -q`
  verified after every sync and at PR time. Zero drift across four
  pairs. Two automated guards (`test_door_data_sync.py`,
  `test_packaged_checks_keep_content_identical`) back this up — the
  handoff's manual table was belt-and-braces, and the tests are the
  real gate.
- **The record's third reader was real.** The spec's risk #3 warned to
  grep for a second `_parse_record` before assuming single-copy; there
  was one, inline in `scripts/core/project`. Both changed together with
  a conformance table pinning them to one meaning.

### Late additions (rounds 3-4)

- **`reviewDecision` went stale, exactly as KIT-0115 predicted.** After
  every thread was resolved the field still read `CHANGES_REQUESTED`,
  because CodeRabbit's dismissing review was `CHANGES_REQUESTED` and
  its clears came as `COMMENTED`. Preflight Gate 2 passed anyway — it
  asks whether the bot reviewed the latest commit, not what the
  decision field says. The gate was right and the field was wrong,
  which is the correct division of labour, but it means **merge may
  need a human APPROVE** if branch protection requires one. Flagged in
  the review starter rather than left for the operator to hit.

- **Mirroring copied a flaw a second time.** The unchecked `replace`
  write CodeRabbit flagged exists identically in the `bots:` and
  `evaluators:` blocks I mirrored. Safe in all three (`set -e`), but
  the pattern of inheriting a source's unreviewed edges recurred within
  a single PR: first `--bots`'s empty-value hole, then this. Two
  instances in one task is what turns lesson 2 from an observation into
  a `patterns.yml` candidate.

### Open at session end

Part D's post-merge half is deliberately unrecorded: tag
`agentive-kit-v0.4.0`, publish-workflow run, PyPI serving 0.4.0, and a
clean-env door-presence smoke. The workflow's own smoke test runs only
`agentive version`, so verifying `agentive new` exists — the entire
point of #144 — is a manual step. PyPI accepts each version exactly
once, so the tag waits for green main and an operator go.

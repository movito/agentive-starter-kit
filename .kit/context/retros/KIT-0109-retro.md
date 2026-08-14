## KIT-0109 — Plugin release 2.0.4, resync the 20-component drift set (PR #9)

**Date**: 2026-08-14
**Agent**: feature-developer (Opus-class)
**Mode**: cross-repo by role, not by CLAUDE.md — the session ran IN
`movito/agentive-skills` (the release target); the kit
(`movito/agentive-starter-kit`) was read-only source canon. No
`## Target Repository` section is involved, so the retro command's
cross-repo autodetection reports SINGLE_REPO_MODE and every metric
below was taken against `movito/agentive-skills` explicitly.
**Scorecard**: 3 threads, 1 regression, 1 fix round, 3 commits
(2 bot rounds: round 1 substantive, round 2 confirmatory/quiet)

Follow-ups F1/F2 were ruled by the planner as KIT-0110 before this
retro was written, so they are not re-litigated here.

### What Worked

1. **Three-way merge instead of copy** — for each component: base = the
   kit blob at its *previously rostered* hash (found by walking kit
   history and hashing blobs until the match), theirs = kit `HEAD`,
   ours = the published plugin copy. All 20 resolved CLEAN. A straight
   copy would have flattened the KIT-ADR-0025 generalization in every
   body; this is the missing half of KIT-0099's method note, which
   covered *how to find the work list* but not *how to apply it*.
2. **The hash-derived work list held for the second release running** —
   20 components, membership identical to the spec's enumeration, and
   the roster's 35 entries reconciled exactly against the kit's 33
   files + 2 retired. The "zero additions/removals" claim was verified,
   not inherited from the spec.
3. **Gate 5 caught the one defect the bots then confirmed** — the fast
   tier (prose-sweep exception: `code-reviewer-fast` only, ~$0.01)
   returned CONCERNS on the CHANGELOG's "20 refreshed vs 27 shipped"
   ambiguity. Fixed pre-open. CodeRabbit's later MD038 finding was in
   the *same paragraph* — the evaluator was reading the right lines.
4. **Routing beat patching, and the bot agreed unprompted** — the
   `reviewThreads(first: 100)` defect was verified byte-identical
   between canon and the shipped copy *before* being routed, and
   CodeRabbit replied "A plugin-only fix would create prohibited drift
   and fail the release guard." Third release running that it reaches
   the KIT-0097 conclusion independently.

### What Was Surprising

1. **The drift guard never reads the plugin.** `check_drift()` hashes
   only the KIT source file and compares it to `roster.yaml`'s
   `kit_sha256`. Nothing in the guard opens
   `plugins/agentive-workflow/**` at all. Concretely: had I bumped the
   20 roster hashes and *forgotten to copy the merged bodies*, this
   release would have gone green with 2.0.3 content shipping under a
   2.0.4 roster. The guard proves "the roster remembers the kit's
   current bytes" — not "the published plugin reflects them." This is
   the single largest gap the session surfaced and it is NOT covered by
   KIT-0110's F1/F2. Escalated below.
2. **Bot findings collapsed from 42 → 12 → 3 across three releases.**
   The spec (quoting KIT-0096) told me to budget rounds for content
   findings; the canon has stabilized enough that the budget is now
   wrong in the cheap direction. One substantive round, one
   confirmatory.
3. **Not one component carried a `version:` frontmatter bump** despite
   all 20 changing content — including `bot-triage`, still reading
   `1.1.0` / `last-updated: 2026-04-19` while carrying the KIT-0104
   sixth face. (Ruled as KIT-0110 F1.)
4. **The release-recipe tooling named in the agent body does not exist
   in this environment.** Phase 5 says to run `agentive review-input
   <TASK-ID>`; `agentive` is not on PATH here, so the evaluator input
   was assembled by hand. The recipe read as authoritative and was not.

### What Should Change

1. **The guard should verify the published copy, not just remember the
   kit's bytes** — see Incident Closure, escalated. Cheapest honest
   version: roster records a second hash (`plugin_sha256`) and the
   guard fails when the published file no longer matches it.
2. **The resync deserves a script, not a per-release re-invention.**
   The base-blob search (walk history, hash each blob, match
   `kit_sha256`) plus `git merge-file` per component was ~60 lines of
   throwaway Python/bash in `/tmp`, written from scratch this release
   and gone now. Three releases have used this shape. It belongs in
   `scripts/local/` as `plugin_resync.py`, with the guard's own roster
   parser reused.
3. **The marketplace repo has no lint and no CI — the bots are the
   entire gate.** That is how a malformed inline-code span reached
   review. Either add a minimal markdownlint workflow there, or state
   in the release recipe that authored prose must be linted locally
   before commit.
4. **The README is outside every guard.** It claimed 2.0.2 while 2.0.3
   was published, and listed `code-review-evaluator` at 1.3.0 while
   1.9.0 shipped — through three releases, found only because I read it
   for unrelated reasons. If `plugin_version` is bumped in four places,
   a fifth place that states a version in prose should be checked too.

### Permission Prompts Hit

**None.** No tool call was blocked or required approval this session.

Non-blocking environment friction worth recording, none of which is a
permission issue:

- `check_plugin_drift.py` requires PyYAML and the bare `python3` here
  does not have it; the script's error says "pip install pyyaml" but
  not that the kit ships a `.venv` with it. Cost: one failed run plus a
  hunt. (`kit_markers.py` is explicitly stdlib-only "no venv needed",
  which set the wrong expectation.)
- Shell portability, macOS/zsh: `grep --include=*.py` unquoted trips
  zsh globbing; `cat -A` is GNU-only (`-e`/`-v` here); the `grep` on
  PATH is `ugrep`, which rejects PCRE lookaheads that GNU grep -E also
  rejects but with a far less legible error.

### Process Actions Taken

- [ ] Decide the guard-scope question in Incident Closure (does the
      drift guard verify the published plugin copy, or is that
      explicitly out of its charter?)
- [ ] Extract `/tmp` resync tooling into `scripts/local/plugin_resync.py`
      (base-blob search + per-component `git merge-file` + roster
      rewrite), reusing the guard's roster parser
- [ ] Add markdownlint to `movito/agentive-skills` CI, or record in the
      release recipe that authored prose is linted locally pre-commit
- [ ] Bring `README.md`'s version claims under the release checklist
      (fifth version site, currently unguarded)
- [ ] Record the 42 → 12 → 3 bot-finding trend so the next release
      spec stops budgeting for a KIT-0096-sized content round

### Incident Closure

1. **Drift guard does not verify the published plugin copy** —
   **ESCALATED, awaiting planner classification.**
   - *(a) What happened*: `check_drift()` hashes only the kit source and
     compares to `roster.yaml:kit_sha256`; no code path reads
     `plugins/agentive-workflow/**`. A release that bumped roster hashes
     without copying the merged bodies would pass green with stale
     content published. Verified by reading the function, not inferred.
   - *(b) Why 1–3 don't fit*: not a doctor check — `project doctor`
     checks the local environment, while this is a gap in a CI guard's
     charter, and a doctor check would be checking the wrong machine.
     Not a not-checkable note — it is entirely cheap to check (one
     `plugin_sha256` column and one comparison against a fetched file).
     Not a triage-guide entry — there is no failure symptom to map: the
     failure mode is *silence*, a green guard over stale content.
   - *(c) The question the planner must answer*: is verifying the
     published plugin copy inside the drift guard's charter, or is the
     guard deliberately scoped to "the roster remembers the kit" with
     the copy's correctness owned by the release recipe? If in charter,
     KIT-0110 should carry a `plugin_sha256` column and the guard should
     fetch and compare. If out of charter, the roster header should say
     so explicitly — it currently says the plugin copy "intentionally
     differs", which reads as *unverifiable* and is why I did not catch
     the gap until after the release was green.

2. **`agentive review-input` unavailable (Phase 5 recipe)** —
   **doctor check.** `agentive` on PATH is exactly the class
   `project doctor` exists to check, and the failure is silent until an
   agent mid-Gate-5 discovers the documented helper isn't there. Add a
   check asserting the `agentive` CLI resolves and its `review-input`
   subcommand exists, citing this incident in the check header.

3. **`check_plugin_drift.py` needs PyYAML, bare `python3` lacks it** —
   **doctor check** (extend an existing interpreter/deps check rather
   than adding a new one): assert the drift script is *runnable* as the
   kit invokes it. One line of check, and it converts a failed run plus
   a venv hunt into a named prerequisite.

4. **CodeRabbit's check read `pass` while its review was
   `CHANGES_REQUESTED` with 3 open threads** — **triage-guide entry
   that already exists**: this is the sixth face of the lying-status
   class, canonized in `bot-triage` and shipped *in this very release*.
   The rule paid for itself inside the release carrying it — triage was
   built from the `reviewThreads` query, so the check's lie cost
   nothing. No new closure needed; recorded here as confirming
   evidence.

5. **Regression accounting (1)** — the MD038 defect (a fence nested in
   an inline-code span, written in my own CHANGELOG prose and never
   rendered or linted) is counted as a regression of
   `displayed_commands_are_contracts`, whose family principle is
   "displayed shell is code, verify it as code." Displayed *markup* is
   markup and deserves the same treatment; the rule existed and its
   stated scope stopped one shape short. That is precisely the basis on
   which KIT-0080/PR #107 was counted a regression, so counting it
   honestly here rather than reporting a flattering 0.

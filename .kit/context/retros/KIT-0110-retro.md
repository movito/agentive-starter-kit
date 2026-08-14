## KIT-0110 — Release tooling + verification: plugin_resync.py + the guard's blind half (PRs #132 + agentive-skills#10)

**Date**: 2026-08-14
**Agent**: feature-developer-f5
**Mode**: single-repo by CLAUDE.md, two-repo by role — session home was
the kit worktree (`../ask-worktrees/KIT-0110`, PR #132); the
marketplace repo `movito/agentive-skills` was operated via `git -C` on
a planner-created branch (PR #10). Kit metrics from
movito/agentive-starter-kit, marketplace metrics from
movito/agentive-skills, labeled throughout.
**Scorecard**: 7 threads (4 + 3), 0 regressions, 2 fix rounds (1 + 1),
10 commits (7 + 3). Both PRs green at handoff; marketplace PR carries
a CodeRabbit APPROVED; no release artifact this task (the KIT-0105
train is the tool's first consumer).

### What Worked

1. **Verify-before-believing refuted o3's headline mechanism in BOTH
   Gate 5 rounds** — round 1: "indented `version:` frontmatter is
   legal YAML the regex misses" (it is not a top-level mapping key);
   round 2: "`Path.glob('*.md')` skips dotfiles" (30-second empirical
   check: pathlib matches `.evil.md`; the dot-skipping is the `glob`
   module's behavior). Both FAILs still carried salvageable kernels
   (missing-git traceback; extra-file scan gap) that were actioned —
   the o3 protocol of reproduce-or-refute per finding, ignoring the
   verdict, keeps paying.
2. **Pipelining PR 2 during PR 1's bot bake** — the marketplace
   column, verify script, and workflow were built, falsified, and
   Gate-5-reviewed inside PR #132's CI/bot windows. Two-repo task,
   ~3.5 h wall-clock including a CodeRabbit outage.
3. **The dogfood rule proved the tool before its own PR merged** —
   PR 2's 27 `plugin_sha256` values were computed by PR 1's
   `--hashes-only` mode and one was independently spot-checked against
   `shasum`. "If the tool can't produce them, the tool isn't done"
   was directly testable and passed.
4. **Convergence separated the real defects from the noise** — the two
   findings that mattered arrived twice each: BugBot Medium +
   CodeRabbit Major on the partial-write ordering (kit), fast + deep
   on the narrow-glob scan gap (marketplace). Everything singly-
   sourced was either refuted or a nit. Convergence-as-signal is
   worth remembering when triaging mixed rounds.
5. **Falsification-first check design** — every failure shape of the
   marketplace check was demonstrated live before its PR opened
   (bump-without-copy → 1, malformed digest → 4, planted hidden +
   nested files → 1, restored → 0), and the kit guard was re-run over
   the new column (green, additive). The evidence table went straight
   into the PR body, which is likely why round 1 had no
   correctness findings against the script's core logic.

### What Was Surprising

1. **The bots caught what the trio missed, in both repos, in the same
   class** — execution-order and CI-architecture defects. The trio
   read the same `plugin_resync.py` and never flagged that the
   missing-body abort fired AFTER merge writes (violating the file's
   own "nothing written" comment); claude-code explicitly analyzed
   that path and concluded ✅. Marketplace-side, no evaluator
   mentioned action pinning, token permissions, or PR-ref execution —
   zizmor (inside CodeRabbit) owned that dimension outright. The
   known evaluator blind spot (CSS/dual-render) has a sibling:
   workflow/execution-context classes.
2. **CodeRabbit hit the org's fair-usage spending cap mid-task** — #10
   sat unreviewed behind "Next review available in: 51 minutes" +
   billing-cap notice; its commit-status meanwhile read `pass — Review
   rate limited` (another lying-status face: *pass* while no review
   exists). The operator raised the cap live; an explicit
   `@coderabbitai review` comment was still required to trigger the
   review afterward.
3. **YAML typed my falsification input and accidentally falsified the
   schema gate** — a 64-char all-digit "hash" parses as int, so the
   intended hash-mismatch test hit the schema validator instead
   (exit 4). One planted defect exercised two failure paths; the
   letter-bearing retry then proved the mismatch path separately.
4. **`agentive review-input` cannot serve a second repo** — it
   resolves the repo from the CWD's CLAUDE.md and writes relative to
   CWD, so PR 2's evaluator input was hand-assembled from the
   template (KIT-0109 hit the same wall from the other side). The
   fallback is documented and worked, but it is manual labor on
   every marketplace-side review.

### What Should Change

1. **Pattern candidate: an all-or-nothing invariant must hold on EVERY
   abort path** — the partial-write defect existed because the
   "nothing written" preflight was built for one abort cause
   (base-not-found) while a sibling cause (body-missing) aborted
   mid-write. Same shape as `fix_by_class_not_instance`, but for
   invariants: when code states an atomicity guarantee, enumerate the
   abort paths and test each one against it. Planner call whether
   this earns a patterns.yml entry.
2. **`agentive review-input` could take `--repo-root`/`--output`** —
   two tasks running (KIT-0109, KIT-0110) have now hand-assembled
   marketplace review inputs. A small flag pair would make the helper
   serve any local checkout. Rider-sized; planner to home it.
3. **Marketplace follow-ups are filed, not lost** —
   `.kit/context/KIT-0110-MARKETPLACE-FOLLOWUPS.md` (F1 test infra,
   F2 markdownlint, F3 conditional `merge_group`, F4 accepted
   residual PR-ref execution). Nothing further needed from this
   session; listed here so the planner processes the file.

### Permission Prompts Hit

**None.** No tool call was blocked or required approval this session
(both repos, all `gh`/`git`/evaluator invocations).

### Process Actions Taken

- [ ] Planner: decide whether "invariants hold on every abort path"
      becomes a patterns.yml entry (What Should Change 1)
- [ ] Planner: home the `agentive review-input --repo-root/--output`
      rider (What Should Change 2)
- [ ] Planner: process `.kit/context/KIT-0110-MARKETPLACE-FOLLOWUPS.md`
      (F1–F4)
- [ ] Operator at merge: mark "Verify published bodies against
      roster.yaml" REQUIRED in agentive-skills branch protection;
      `workflow_dispatch` the kit drift guard after #10 lands
- [ ] KIT-0105 train: use `plugin_resync.py` and cite it in the
      release record (spec AC, open until that cut)

### Incident Closure

1. **CodeRabbit fair-usage/spending cap blocked #10's review while its
   commit-status read `pass`** — **not-checkable note already exists**
   (`scripts/core/doctor.d/80-bot-presence.sh` CodeRabbit-quota note:
   quota state is not cheaply checkable pre-flight). This incident
   extends the class with confirming evidence: adaptive fair-usage
   limits and org spending caps produce the same silent non-review,
   and the status line says `pass` throughout — the reviewThreads-first
   triage rule (bot-triage step 0) is what made the absence visible.
   No new closure needed; recorded here as the class's next face,
   with the recovery recipe (raise cap → `@coderabbitai review`).
2. **`agentive review-input` unusable for the marketplace repo (CWD
   CLAUDE.md auto-detection, CWD-relative output)** — **triage-guide
   entry already exists**: the code-review-evaluator skill and the fd
   agent's Phase 5 document manual assembly from
   `.adversarial/templates/code-review-input-template.md`, which is
   exactly what was done. The improvement path is the rider in What
   Should Change 2, tracked as a process action, not an unclassified
   incident.
3. **zsh treated `===CLAUDE===` as a word and errored** — known
   footgun already documented in both planner agents (KIT-0109 retro,
   `=`-word); confirming evidence only, cost one retried command. No
   new closure needed.

No other environment incidents this session — the door-data byte-pin
(`test_door_data_sync.py`) firing on the `engine-consumer.sh` edit was
the guard working as designed, not an incident.

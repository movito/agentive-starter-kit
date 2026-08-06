## KIT-0083 — Ship the adversarial CLI, not just its config (PR #106)

**Date**: 2026-08-06
**Agent**: feature-developer (Opus 5)
**Mode**: single-repo, per-task worktree (`../ask-worktrees/KIT-0083`)
**Merged**: `d1e938e` (squash), 2026-08-06T04:16Z
**Scorecard**: 17 findings (4 evaluator + 13 bot: 11 inline, 2 review-body) —
14 actioned, 3 declined with reasoning; 5 bot rounds; 7 branch commits
(squashed) + 2 bookkeeping commits on main; 9 files, +1405/−18;
full suite 815 → 906 passing

### What Shipped

Issue #103: `.adversarial/` config and the evaluator library both shipped and
`project doctor` said PASS, but nothing installed the `adversarial` CLI and no
check verified it — so a fresh project looked provisioned until the planner's
Phase 3 gate hit `command not found`. Verified closed on `main`, against a
fixture of the exact #103 shape:

```
DOCTOR:evaluators:PASS:evaluator library installed (1 entries)
DOCTOR:evaluator-cli:FAIL:adversarial CLI not on PATH — run: ./scripts/core/project install-evaluators ...
```

The old green line still reports green; the new one fails beside it. F1 (install
step), F2 (doctor check), F3 (pin home = `.adversarial/config.yml`) all landed.
F4 deferred — KIT-0082 has no acceptance test to hook yet.

### What Worked

1. **Verifying every bot finding against the tree before fixing.** Twice this
   changed the outcome. BugBot's git-gate finding was real, and *reproducing* it
   surfaced a second pre-existing defect underneath: an absent git makes
   `subprocess.run(["git", ...])` raise `FileNotFoundError` rather than return
   non-zero, so the friendly "Git is required" message never printed and users
   got a raw traceback. CodeRabbit's `.adversarial`-as-a-file finding was also
   real but correctly *declined* — `30-evaluators.sh` shares the identical
   `[ ! -d ]` test, so fixing one alone would have made sibling checks disagree.
2. **Mutation-testing each new assertion instead of re-running to green.** Every
   test added in rounds 1–5 was checked by deliberately breaking the thing it
   guards: sabotage the doctor bound → drift test fails; invert pin precedence →
   `9.9.9` vs `7.7.7`; shorten `PROBE_TIMEOUT` to 2 → timing test fails; revert
   the round-4 regex → exactly the three plural/negated cases fail. Without this
   at least three assertions would have shipped unfalsifiable.
3. **PATH-isolated fixtures as the house pattern.** `_restricted_bin` /
   `_stub_executable` made "fresh project with no CLI" testable on a machine
   where `uv` and `adversarial` are both installed. This is the direct antidote
   to the blind spot that shipped #103.
4. **Evaluator trio before the PR (KIT-0035 ordering).** Four findings actioned
   pre-PR, including the presence-vs-liveness split that both fast-v2 and o3
   flagged independently. Those never cost a bot round.
5. **The worktree topology, once adopted.** Primary clone stayed clean on `main`
   throughout; `core.bare=false` canary checked after every commit and never
   tripped.

### What Was Surprising

1. **The worktree step was skipped entirely at task start — and the process,
   not the agent, is why.** `WORKTREE-WORKFLOW.md` makes per-task worktrees the
   default and `TASK-STARTER-TEMPLATE.md` calls the LAUNCH block "mandatory in
   every starter" with a delivery checklist item for it. The KIT-0083 starter
   had none, and named the primary clone as the repo. Compounding it,
   `feature-developer.md` contains the word "worktree" **zero times** and its
   Phase 1 says `GIT_TARGET checkout -b` — which the template explicitly
   forbids ("the worktree already exists — never `checkout -b`"). An agent
   following its own definition faithfully lands in the wrong topology. Caught
   only because the operator asked. Full write-up: `KIT-0083-SESSION-FINDINGS.md`.
2. **`new-worktree.sh` is dead on Apple git 2.30.1** — exactly as KIT-0080 S3
   predicted in writing. `rev-parse --path-format=absolute --git-common-dir`
   echoes the unrecognized flag as an output line, so `PRIMARY_ROOT` becomes
   garbage and the guard hard-exits. Worked around with a one-line scratchpad
   copy (`cd <repo> && cd "$(git rev-parse --git-common-dir)" && pwd`), which is
   live proof KIT-0080 F1's first proposed option works. **The default
   implementation topology is unusable on stock macOS git.**
3. **The handoff's "3 pre-existing test failures" was wrong — it is 8.** The
   figure came from reading a truncated pre-commit `pytest-fast` tail ("stopping
   after 3 failures", 45 deselected) as a complete result. A truncated baseline
   is actively dangerous: an implementer introducing 2 real regressions would
   still have seen "3 failures" and concluded nothing changed.
4. **My own tests were the richest vein of bot findings.** Three separate
   assertions could not fail: a precedence test asserting the value it wrote, a
   `!= "0.0.1"` that `None` satisfies, and a "hanging probe" test whose
   `sleep 120` stub exited 127 instantly under the restricted PATH — so it
   passed via the broken-binary branch and never exercised the bound at all.
   For a task that exists *because* a check passed locally and proved nothing,
   that is a pointed pattern.
5. **A round-3 finding was invisible to thread-based triage.** CodeRabbit
   delivered it as an "outside diff range" comment inside the review body, with
   no inline thread. Anyone reviewing by scanning unresolved threads — including
   me, had I not read the body — would have merged with the CLI step still
   claiming "The evaluator library is installed" immediately before exiting 1
   having installed nothing.
6. **My own e2e output contained that lie and I read past it twice.** It was in
   captured terminal output I had already pasted into the PR body as evidence
   the fix worked.
7. **A near-miss from assuming instead of checking.** I nearly used GNU
   `timeout` for the probe bound on the assumption stock macOS lacks it. It is
   present here — via homebrew. Had I "verified" by running it, the check would
   have worked on this machine and hung on a plain one: the #103 failure mode,
   reproduced in the fix for #103.

### Process Notes

- **Bot-round decay**: 7 findings (2 Major bugs) → 3 → 1 → 1 → 1, with rounds 4
  and 5 touching no production code at all — both were about the rigor of a test
  helper guarding three message strings. Production code was stable and
  unchallenged from round 3 onward. Round 5 asked for regex coverage of
  phrasings no message uses. There is no natural fixed point here: any assertion
  can be made marginally stricter, and an ASSERTIVE-profile reviewer will find
  the next increment. Naming the decay curve and merging on it is the judgment
  call; waiting for silence is not a strategy.
- **Declined with reasoning, not silence** (3): `.adversarial`-as-a-file (would
  desync sibling checks), uv concurrent-install locking (speculative; uv locks
  itself and the path already degrades to advice), and the no-sleep fallback
  blocking unbounded (every bash-builtin timer needs a non-EOF descriptor, hence
  a helper process — reintroducing the dependency that branch exists to survive).
- **#60 reframed rather than "fixed"**: the two pins were never inconsistent —
  `adversarial-workflow>=1.0.1` is a PyPI distribution, `v0.10.0` is a git tag on
  a different repo. It is a **location** bug: both pins lived in `pyproject.toml`
  from `c851276` when the kit was single-shape; the planning shape (`924a5bb`)
  never ships one. The split turned a previously-fine home into an unreadable one
  for half of all projects. **Any surface predating `924a5bb` is suspect for the
  same class** — that generalization is the reusable part.
- **KIT-0057 held**: two aborted pre-commit runs, both followed by `git log -1` +
  `git status` before proceeding; neither had landed a commit.

### Follow-ups

1. **`feature-developer.md` Phase 1 must know about worktrees** (highest
   leverage). It is the only artifact guaranteed to be read at implementation
   time, and today it instructs the opposite of the template. Replace
   `checkout -b` with the template's contract: *verify* the worktree, and stop
   and ask if there isn't one. That converts a silent wrong-topology start into
   a loud one, independent of starter quality. **Sequence after KIT-0080** — a
   worktree step added today hard-fails on this machine.
2. **KIT-0080 priority**: fold in the confirmed `new-worktree.sh` breakage and
   the working one-line fix. Its S3 already predicted this; the evidence is now
   in hand.
3. **Investigate why this starter lacked the LAUNCH block** — the template
   mandates it and carries a checklist item, so the question is why the authoring
   path bypassed it, not what the rule should be.
4. **Record a baseline rule**: known-failure counts come from a direct `pytest`
   run with the command stated, never from a `-x`-style hook tail. Cousin of
   KIT-0057's "never trust the output tail," applied to test baselines.
5. **Bot triage must read the review body, not just inline threads** — round 3's
   only finding lived there. Worth adding to the bot-triage skill.
6. **KIT-0079** consumes this PR's pin-home decision; `evaluator_library_version`
   is already written into `config.yml`, currently inert, with
   `test_library_pin_mirrors_agree` guarding drift until the reader moves. Delete
   that test when KIT-0079 lands.
7. **KIT-0055 overlap**: F2 answers "does a binary exist"; KIT-0055 answers
   "*which* binary is it". Kept separate deliberately — the second is meaningless
   before the first.
8. **`create-project.md` contradictions remain** (`pipx` at `:180`/`:317`,
   per-evaluator `adversarial library install` at `:214-217`, unearned
   `verified` summary at `:260`). Untouched by operator decision (`041f75d`);
   KIT-0087 F3 owns them, KIT-0078 F2 may delete the file.

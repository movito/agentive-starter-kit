# KIT-0083 — Session Findings for the Planner

**Date**: 2026-08-05
**From**: feature-developer session (KIT-0083, implementation not yet started)
**To**: planner
**Status of KIT-0083 itself**: worktree provisioned, branch created, one
file written (`31-evaluator-cli.sh`, uncommitted). F1/F2/F3 not started.

Three findings, in descending order of consequence. F1 and F2 correct
existing records; F3 is a process gap in the task-starter template.

---

## F1 — `new-worktree.sh` is dead on Apple git 2.30.1 (confirms KIT-0080 S3)

**KIT-0080 predicted this and was right.** Its S3 says of
`scripts/local/new-worktree.sh:36`: *"its line-42 guard catches the
garbage and hard-exits, so worktree creation is dead on this git."*
Confirmed live this session:

```console
$ ./scripts/local/new-worktree.sh KIT-0083
dirname: illegal option -- -
usage: dirname string [...]
```

The guard fired exactly as designed and refused cleanly (no
half-provisioned worktree). Root cause is verbatim KIT-0080's: git
2.30.1 does not consume `--path-format=absolute`, echoes it as an
output line, and `PRIMARY_ROOT` becomes garbage.

**What this changes for prioritisation**: KIT-0080 is currently filed
with S1 as "cosmetic" and S3 as the escalation reason. S3 should
arguably be split, because the worktree symptom is **not** a
silent-wrong-answer bug like the preset one — it is a **hard block on
the documented default implementation topology**. Per
`WORKTREE-WORKFLOW.md`, per-task worktrees are the default, and every
task starter carries a LAUNCH block pointing at one. On stock macOS
git, no agent can execute that flow. Every session on this machine
either silently works in the primary clone (what this session did until
corrected) or hand-rolls a workaround (what it did after).

**Workaround used, for the record** — the tracked helper was NOT
modified. A scratchpad copy with exactly one line changed:

```bash
# line 36, original (breaks on 2.30.1):
GIT_COMMON_DIR="$(git -C "$SCRIPT_DIR" rev-parse --path-format=absolute --git-common-dir)"
# replacement used (portable, matches KIT-0080 F1 option 1 — "resolve to
# absolute in shell"):
GIT_COMMON_DIR="$(cd <repo> && cd "$(git rev-parse --git-common-dir)" && pwd)"
```

This is a live proof that KIT-0080 F1's first listed option works. One
caveat learned the hard way: the replacement must anchor on the **repo**,
not `$SCRIPT_DIR`, if the script is run from outside a checkout —
otherwise the guard correctly refuses because the scratchpad copy's own
directory is not a git repo.

## F2 — the "3 pre-existing failures" figure is wrong; it is still 8

The KIT-0083 handoff addendum (item 4) states:

> **KIT-0080 red herring**: 3 `test_doctor.py` failures on this machine
> [...] are **pre-existing** [...] Verified against a clean HEAD on
> 2026-08-05.

**The real number is 8**, exactly as KIT-0080 S2 originally recorded.
Measured this session on a clean worktree branch:

```console
$ python -m pytest tests/test_doctor.py -m "not slow" -q
8 failed, 144 passed in 55.41s
```

The full set:

- `TestCoreBareCheck::test_bare_config_fails`
- `TestConfigHomeCheck::test_derivation_without_override_names_the_sibling`
- `TestWorktreeProvisioningCheck::test_worktree_missing_serena_config_warns`
- `TestWorktreeProvisioningCheck::test_worktree_serena_name_collision_warns`
- `TestWorktreeProvisioningCheck::test_worktree_serena_distinct_name_passes`
- `TestWorktreeProvisioningCheck::test_serena_short_name_key_collision_detected`
- `TestWorktreeProvisioningCheck::test_serena_apostrophe_name_not_mangled`
- `TestWorktreeProvisioningCheck::test_serena_unnamed_config_warns`

Verified independent of this task's work: removing the new
`31-evaluator-cli.sh` and re-running gives the same 8.

**Where "3" came from** — the pre-commit `pytest-fast` hook stops early:

```
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 3 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
===== 3 failed, 323 passed, 45 deselected, 1 warning in 184.42s (0:03:04) =====
```

The addendum author read a **truncated** hook run as a complete result.
Note the hook also *deselects* 45 tests, so its total differs from a
direct run in two ways at once.

**Why this matters beyond arithmetic**: a truncated baseline is an
actively dangerous artifact. The addendum tells the implementer "if the
set changes, re-verify against clean HEAD" — but the set was *always*
going to look changed, because 3 was never the real set. An implementer
who introduced 2 genuine regressions would still see "3 failures,
stopping after 3" and conclude nothing had changed. **Recommendation**:
when recording a known-failure baseline, record it from a direct
`pytest` run and state the exact command; never from a `-x`-style hook
tail. This is a close cousin of the existing KIT-0057 rule ("never trust
the output tail" after an aborted hook run) — same failure mode, applied
to test baselines rather than commit success.

## F3 — how the worktree step got missed (process gap, not just an error)

**What happened**: this session began implementation directly in the
primary clone on `main`. It ran `project start`, then wrote a source
file, before the operator asked "did we remember to ask you to use git
worktrees?" Nothing was committed to `main` incorrectly and recovery was
cheap, but the default topology was skipped outright.

**Why it happened — three compounding causes, none of them "the agent
forgot":**

1. **The task starter carried no LAUNCH block — and the template
   mandates one.** This is the core failure. `TASK-STARTER-TEMPLATE.md`
   is unambiguous:
   - `:109` and `:198` — the LAUNCH block, marked "un-skippable"
   - `:124` — "The LAUNCH block is **mandatory** in every starter"
   - `:126` — "Create the worktree with the helper BEFORE [the starter]"
   - `:337-338` — a delivery-checklist item: "**Worktree created** [...]
     and **LAUNCH block included** with the real worktree path and branch"
   - `:354-358` — the planner's own procedure: step 3 create the
     worktree, step 4 write the starter carrying its path, step 6 user
     invokes the agent "**with cwd set to the worktree path**"
   - `:363-364` — the implementer's first move: "**Verify the
     worktree**: `git branch --show-current` must match [...] (the
     worktree already exists — never `checkout -b`)"

   The KIT-0083 starter has none of it. It instead says **"Repo:
   /Users/broadcaster_one/Github/agentive-starter-kit — single-repo
   mode"**, naming the primary clone as the working directory, and
   `./scripts/core/project start KIT-0083` as the first command. So the
   starter did not merely omit the worktree step — it actively pointed
   at the primary clone, and the template's "never `checkout -b`"
   instruction had no worktree to apply to. **A starter that skips
   steps 3-4 of the documented procedure produces exactly this
   session.**

2. **The handoff never mentions worktrees either.** Neither the body nor
   the 2026-08-05 addendum references the topology — even though the
   addendum was written by a feature-developer session that had itself
   hit the ~3-minute pre-commit issue and the KIT-0080 failures, both
   worktree-adjacent. It even cites `WORKTREE-WORKFLOW.md` for an
   unrelated PATH note, so the file was open and the topology still went
   unmentioned.

3. **`feature-developer.md` contains the word "worktree" zero times.**
   Verified by grep. Its Phase 1 is "read spec, create branch in code
   repo" with `GIT_TARGET checkout -b` — which **directly contradicts**
   the template's "the worktree already exists — never `checkout -b`"
   (`:364`). An agent following its own definition faithfully lands in
   the primary clone and creates a branch in place. That is not a
   deviation from the agent spec; it *is* the agent spec.

   (`planner.md` fares little better: one incidental mention at `:462`,
   no worktree-creation step, despite the template assigning the
   planner steps 3-4.)

The topology is documented in exactly two places — `WORKTREE-WORKFLOW.md`
and the starter template — and both are read by the *planner*, at
starter-authoring time. It is absent from `feature-developer.md`
entirely, and it was absent from the one artifact this session was
actually handed. **The safeguard is real but single-point: it lives
entirely in whether the starter gets authored correctly.** When that
one step is skipped, nothing downstream catches it — the implementing
agent's own definition affirmatively tells it to do the wrong thing.

**Recommended fixes** (planner's call on scope):

- **Highest leverage — fix `feature-developer.md` Phase 1.** It is the
  only artifact guaranteed to be read at implementation time, and today
  it says `checkout -b` where the template says "never `checkout -b`".
  Replace with the template's `:363-364` contract: *verify* the worktree
  exists and the branch matches; if there is no worktree, **stop and ask**
  rather than branching in place. That converts a silent wrong-topology
  start into a loud one, independent of starter quality — closing the
  single point of failure rather than reinforcing it.
- **Then** investigate why this starter lacked the LAUNCH block, since
  the template already mandates it and carries a checklist item. The
  question is not what the rule should be but why the authoring path
  bypassed it — worth checking whether the starter was authored
  from the template at all.
- Note in the starter that "single-repo mode" describes the
  **planning/code split**, not the worktree topology. The KIT-0083
  starter's phrasing reads as "work in this directory", which is
  precisely how it was acted on.
- Consider gating: given F1, a worktree step added to the agent spec
  will **hard-fail on this machine** until KIT-0080 lands. Sequence
  KIT-0080 first, or ship the portable one-liner from F1 with it.

**Bookkeeping note for this session**: because the worktree branches from
fresh `origin/main`, the `project start` status move had to land on
`main` first (commit `178ee47`, pushed) — otherwise the worktree carries
a stale `2-todo` task file and fails its own `validate-task-status`
hook. That ordering is worth writing into the workflow doc: **`project
start` on `main` in the primary, push, then create the worktree.** It
also keeps `agent-handoffs.json` off the feature branch, which the
KIT-0086 interim discipline already requires — the two rules agree, and
neither is currently written down next to the other.

---

## Current KIT-0083 state

- Primary clone: clean, on `main`, at `178ee47` (pushed)
- Worktree: `~/Github/ask-worktrees/KIT-0083` on
  `feature/KIT-0083-ship-adversarial-cli`, provisioned per contract
  (`.env` + `.adversarial/evaluators` symlinked, real per-worktree
  `.venv`, primary `core.bare=false` canary passed)
- Written but uncommitted: `scripts/core/doctor.d/31-evaluator-cli.sh`
  (F2 of the task — SKIP/FAIL/PASS on the `DOCTOR:` contract, probes
  `--version` **exit code** per the addendum's stderr warning)
- Not started: F1 (install step), F3 (pin home in
  `.adversarial/config.yml`), manifest entry, all tests

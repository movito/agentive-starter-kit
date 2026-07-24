# KIT-0058 — Evaluator Review Record

**Date**: 2026-07-23
**Input**: `.adversarial/inputs/KIT-0058-code-review-input.md` (full-file
context, `main...HEAD` at `7d62bc9`)
**Ordering**: trio run BEFORE PR open (KIT-0035/KIT-0046 rule).
`git status` checked after every run — no evaluator mutations.

## Verdicts

| Evaluator | Model | Verdict |
|-----------|-------|---------|
| code-reviewer-fast | gemini-2.5-flash | CONCERNS (1 finding) |
| code-reviewer | o3 | FAIL (6 findings — 2 real, 2 refuted, 1 pre-existing, 1 fell with a refutation) |
| claude-code | claude-sonnet-4-6 | APPROVED (2 MEDIUM defense-in-depth, 3 LOW) |

o3's verdict treated per the standing rule (verdict carries no signal;
every claim code-checked).

## Triage

### Fixed

1. **`~` in `AGENTIVE_KIT_CONFIG_DIR` not expanded** (o3 #1, real):
   all three resolvers (door `config_home`, project `_config_home`,
   check `resolve_home`) now expand a literal leading tilde — the
   env-source precedent. Pinned by
   `TestConfigHomeOverrideTilde::test_tilde_in_override_expands` (bash)
   and `test_tilde_override_expanded_python_side` (python).
2. **`/setup-preset` had no rev-parse failure guidance** (fast #1,
   real): the command now instructs the agent to STOP and say the
   command must run from a kit checkout — never guess a path.
3. **`gh repo view` flag-injection surface** (claude-code MEDIUM #2):
   flags-first + `--` separator before the URL
   (`gh repo view --json visibility --jq .visibility -- "$URL"`) —
   verified empirically that gh accepts this form.
4. **Seeding partial-write persistence** (claude-code LOW #3):
   temp-then-mv (the TEMP-THEN-COMMIT pattern) so an interrupted write
   can never stick behind the never-overwrite guard.
5. **Override trust note** (claude-code MEDIUM #1, doc remedy): door
   header now names `AGENTIVE_KIT_CONFIG_DIR` as a TRUSTED,
   operator-owned value never to be sourced from untrusted
   environments.

### Refuted (verified against code / live CLI)

- **o3 #2 "gh rejects full remote URLs"**: empirically false —
  `gh repo view` accepts HTTPS, HTTPS+`.git`, and scp-style SSH URLs
  (all returned the visibility; also confirmed the UPPERCASE output
  the check's `tr` normalization handles). o3 #6 (test stub "hides"
  this) falls with it.
- **o3 #4 "empty override makes seed write to ''/preset"**: false —
  empty falls through to derivation in ALL resolvers;
  `seed_config_home` uses `config_home()`'s guarded result, never the
  raw variable. The bash unit o3 claimed missing exists
  (`test_empty_override_falls_through_to_derivation`).
- **o3 #5 "bare-repo layout breaks derivation"**: unreachable — every
  resolver anchors on a checkout that carries the script files
  themselves (a bare repo has no working tree, so neither the door
  nor `scripts/core/project` can run from one), and `70-core-bare`
  FAILs loudly on the damage case.

### Declined / out of scope

- **o3 #3 defaulted-profile suffix in `--against-preset`**:
  pre-existing KIT-0056 behavior, untouched by this diff. Left for a
  follow-up if operator confusion ever materializes.
- **claude-code LOW: preset file size bound** — operator-owned config
  on a single-operator tool.
- **claude-code LOW: sed escaping in `record_field`** — pre-existing
  (KIT-0053), key set is closed ASCII.

## Known blind spot note

Evaluators reviewed the `/setup-preset` command text as prose; its
binding rules (derive-from---help, no pasted secrets) are structural
instructions to a future agent — flagged for human review rather than
evaluator sign-off.

# KIT-0058 Review Starter — Visible Config Home + /setup-preset (ADR-0027 P7 amendment)

**PR**: https://github.com/movito/agentive-starter-kit/pull/91
**Branch**: `feature/KIT-0058-visible-config-home`
**Task**: `.kit/tasks/4-in-review/KIT-0058-visible-config-home.md`
**Status**: CI green · CodeRabbit APPROVED (1 trivial thread —
declined with empirical refutation, resolved) · BugBot reviewed on a
later commit after early check-runs said "skipping": 1 Medium finding
(doctor anchors config home to the diagnosed checkout, not the kit) —
dispositioned as deliberate-with-honest-naming, anchor + override now
named in every doctor output line, thread resolved · evaluator trio
run pre-PR (record:
`.kit/context/reviews/KIT-0058-evaluator-review.md`)

## What this closes

The last blocker before the operator's one-button: config relocates
from invisible `~/.config/agentive-kit/` to the visible sibling
`<kit-parent>/agentive-config/`, with guardrails instead of obscurity.
On merge: the operator runs `/setup-preset` to author their real
preset, then 0.9.0 becomes cuttable (the legacy-location notice joins
the KIT-0047 + KIT-0054 + KIT-0059 removal set — KIT-0059's task file
gained the entry in this PR).

## Review focus (suggested order)

1. **The three resolvers stay in agreement** — door `config_home()`
   (bash), project `_config_home()` (python), check `resolve_home()`
   (bash): override-first (leading `~` expanded), else primary-clone
   parent via `--git-common-dir` + `/agentive-config`. The
   door↔doctor pin is `test_door_and_doctor_agree_on_the_path`; the
   check's own derivation is pinned separately
   (`test_derivation_without_override_names_the_sibling`).
2. **Resolve locates, orchestrate seeds** (accepted arch-review
   finding) — `config_home` writes nothing; `seed_config_home` is the
   only writer (idempotent, temp-then-mv, never creates the folder —
   N3 pinned by `test_never_creates_the_folder`).
3. **Legacy is a notice, never a read** (F4) — both directions pinned
   (`TestLegacyLocation`); doctor's face is a WARN line in
   `90-config-home.sh`. Removal joins 0.9.0.
4. **`/setup-preset` binding rules** — evaluators reviewed it as
   prose; the structural rules (derive-from-`--help`, no hardcoded
   question list, refuse pasted secrets, validate keys at authoring
   time) deserve human eyes — this is the file a future agent obeys.
5. **Stranger-path characterization** — byte-identical modulo ONE
   masked line: the config-home doctor check reports the environment
   difference the test itself constructs (see `_door_output` comment).

## Known/accepted

- CodeRabbit's single committable suggestion was a bash syntax error
  (heredoc swallows the chained `mv`) — declined with the empirical
  test in the thread; the explicit nested form stays.
- o3 FAIL verdict: 2 real findings (fixed: tilde expansion,
  `/setup-preset` rev-parse guidance), 2 refuted empirically
  (`gh repo view` accepts HTTPS/SSH/`.git` URL forms; empty override
  falls through), 1 pre-existing (defaulted-profile suffix in
  `--against-preset`, KIT-0056 behavior, untouched).
- BugBot's early check-runs said "skipping" but it DID review a later
  commit (retro flag about Gate 3 honesty still stands — the gate read
  "skipping" as clean). Its one Medium finding is real at the seams:
  doctor anchors the config home to the checkout it diagnoses, the
  door to the kit clone. A consumer checkout cannot compute the kit's
  local path, so same-anchor is the only computable rule; it matches
  the door exactly in the documented sibling layout, and the fix
  makes the anchor + `AGENTIVE_KIT_CONFIG_DIR` escape hatch explicit
  in every doctor line (README bullet added).
- The demo transcript in the PR body shows doctor FAILs — scratch-
  environment noise (fixture .env, no evaluators), named there.

## Operator follow-up on merge (not in this PR)

1. Run `/setup-preset` in a kit session → authors
   `~/Github/agentive-config/preset` (+ optional private repo).
2. First real `bootstrap --new` run is the end-to-end proof.

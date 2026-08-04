# KIT-0085: External starter authoring path - Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-08-04
**From**: planner-f5
**To**: feature-developer
**Task**: `.kit/tasks/2-todo/KIT-0085-external-starter-authoring-path.md`
**Status**: Queued — third in line, after KIT-0084 then KIT-0083
**Evaluation**: arch-review-fast, 2 rounds (round-1 findings folded into
the spec; round-2 advisories accepted-as-noted — see spec header and
`.adversarial/logs/KIT-0085-external-starter-authoring-path--arch-review-fast.md`)

---

## Task Summary

`TASK-STARTER-TEMPLATE.md` v1.1.0 cannot be satisfied by a coordinator
working outside the kit checkout: the checklist mandates pre-created
worktrees and `agent-handoffs.json` updates, and the LAUNCH block
requires transcribing branch names the helper invents. Give task
starters the external-origin path that KIT-0066 gave briefs: split the
checklist (author-time vs provisioning-time), make `new-worktree.sh`
emit a machine-readable launch stub that provisioning stamps into the
starter, add an `adopt-starter` ingestion script, and specify the two
referenced artifacts the template currently leaves undefined.

**Target Codebase**: This repo — NOT the target repo (single-repo mode;
the kit's own templates, scripts, and tests).

## The Acceptance Fixture (start here)

`tests/fixtures/external-starter/` holds a REAL externally-authored
starter + handoff pair (PLAY-0001, written by a claude.ai session with
no checkout access), committed byte-faithfully except for placeholdered
Vercel IDs. Its defects are the requirements in miniature:

- `PLAY-0001-TASK-STARTER.md` line 50 — ad-hoc "Coordinator note"
  because the worktree/handoffs checklist items were unsatisfiable
  (→ F1, F3)
- Lines 57-58 — guessed branch name plus "correct it if the helper
  disagrees" hedge (→ F2)

Done means: this pair passes the new author-time checklist with zero
deviations needing a coordinator note, and `adopt-starter` ingests it
cleanly. Read the fixture README before writing code.

## Your Mission

- **Phase 1 — F2, the launch stub.** Extend
  `scripts/local/new-worktree.sh` to write
  `.kit/context/<TASK-ID>.launch` alongside its existing output.
  Anchors (verified 2026-08-04): slug derivation is lines 96-120
  (`KIT-0051-fix-the-thing.md` → `fix-the-thing`); `BRANCH`/
  `WORKTREE_PATH` are set at lines 122-123; the final "Worktree ready"
  block starts at line 262 — emit the stub there, from the same
  variables, so stub and reality cannot diverge. Simple `key=value`
  lines (worktree path, branch, slug origin, creation timestamp).
  One-way transport: after stamping, the starter's LAUNCH block is the
  operative record and the stub is a receipt — document which (keep or
  delete) in both the script header and the template, per the spec.
  Decide whether `.kit/context/*.launch` is gitignored (recommended:
  yes, it is per-machine runtime state) and say so where it's emitted.
- **Phase 2 — F3, `adopt-starter`.** New script, recommended home
  `scripts/local/` next to `new-worktree.sh` (same machine-local,
  operator-run character; `scripts/core/` acceptable if you find a
  stronger reason — record it in the PR description). Input: paths to
  an externally-authored starter + handoff (+ task spec if separate).
  Behavior: validate → place spec in `.kit/tasks/2-todo/` and handoff
  in `.kit/context/` under canonical names → run `new-worktree.sh` →
  stamp the LAUNCH block from the stub → update `agent-handoffs.json`
  atomically (read, modify, temp file, rename — never in-place).
  Refusals in the house style (see `new-worktree.sh`'s own refusal
  blocks, lines 128-138): existing task ID, existing branch, malformed
  input — never half-adopt
  (`.kit/context/workflows/TEMP-THEN-COMMIT-PATTERN.md`).
  `--adopt-only` stops before worktree creation, leaves the placeholder
  LAUNCH block, prints the completing step; a later full run finishes
  provisioning without re-ingesting.
- **Phase 3 — F1 + F4, the template.** Rework
  `.kit/templates/TASK-STARTER-TEMPLATE.md`: checklist (currently lines
  325-342) becomes two labeled lists — author-time (satisfiable
  anywhere) and provisioning-time (in-checkout only, performed by
  `adopt-starter` or the in-checkout planner); define external
  compliance (all author-time items pass + declared LAUNCH placeholder,
  not guessed values); the "create the worktree BEFORE writing the
  starter" mandate (lines 124-127) moves to the provisioning-time side.
  Specify the placeholder form external authors must use. F4: link
  `.kit/tasks/9-reference/templates/task-template.md` from checklist
  item 1; inline a minimal `agent-handoffs.json` entry example. Bump to
  v2.0.0 with the change documented in the header. Update the
  "Integration with Agent Workflows" section (lines 346-370) — both the
  coordinator flow (stamp from stub, or adopt-starter for external
  pairs) and any WORKTREE-WORKFLOW.md cross-references that still
  describe hand-transcription.

## Data Shape Verification

`agent-handoffs.json` (live, verified 2026-08-04): top-level agent-name
keys (`planner`, `feature-developer`, `code-reviewer`, `test-runner`,
`document-reviewer`), each an object with exactly `status`,
`current_task`, `task_started`, `brief_note`, `details_link`, and
(planner/feature-developer) `handoff_file`. `adopt-starter` should
update the target agent's entry and preserve everything else verbatim
— parse with Python (`json` module via a small helper or inline
`python3 -c`), not shell text-munging.

## Test Approach

- Extend `tests/test_new_worktree.py` (exists; see how it harnesses the
  script) for stub emission: stub written, values match the created
  worktree/branch, derived-slug and explicit-slug cases.
- New `tests/test_adopt_starter.py`: happy path against a copy of the
  PLAY-0001 fixture; refusal cases (existing ID, existing branch,
  malformed pair) leave NOTHING moved; `--adopt-only` then full-run
  completion; `agent-handoffs.json` update is atomic and preserves
  unrelated keys. Use `tmp_path` copies — never mutate the fixture.
- Shell changes: `./scripts/core/ci-check.sh` before push. Known
  machine issue: `TestCoreBareCheck::test_bare_config_fails` fails
  locally on Apple git 2.30.1 (tracked, KIT-0080 spec line 38) — it is
  NOT yours; CI on GitHub is the arbiter.

## Out of Scope

- Fixing `new-worktree.sh` on Apple git 2.30.1 (KIT-0080). Your stub
  emission must not deepen that incompatibility; nothing more.
- The prototype-brief flow (KIT-0066) — reported working; don't touch
  `PROTOTYPE-HANDOFF-TEMPLATE.md`.
- Concurrency-safe `agent-handoffs.json` access (evaluator round-2
  advisory; single-writer assumption holds — future task if it stops
  holding).
- Unifying the in-checkout planner flow beyond pointing it at the stub
  (spec Notes: one mechanism, two entry points — stamping from the stub
  should serve both, but reworking planner.md itself is not this task).

## Evaluation Summary

Round 1 (REVISION_SUGGESTED) findings, all now in the spec: atomic
handoffs.json update strategy; stub-vs-LAUNCH-block authority (one-way
transport, stamped block operative); severable provisioning
(`--adopt-only`) so ingestion survives KIT-0080 machines. Round 2
advisories accepted-as-noted: future concurrency rework; internal
modularization of `adopt-starter` at your discretion (favor small
focused functions — the script does file placement, helper invocation,
Markdown stamping, and JSON update, which the evaluator flagged as a
testability risk).

## Success Looks Like

An external coordinator can author a compliant starter with zero
checkout access; `adopt-starter` turns the loose pair into a
provisioned, launch-ready assignment with a stamped LAUNCH block
byte-identical to what the helper created; the PLAY-0001 fixture passes
end-to-end in tests; the template at v2.0.0 tells both audiences
(external authors, in-checkout provisioners) exactly what is theirs.

## Questions for Coordinator

Raise rather than resolve unilaterally: canonical-naming collisions
during adoption (e.g. the pair's spec filename disagrees with its task
ID); whether `.launch` receipts should be committed or gitignored if
you find evidence cutting against the recommendation; anything that
would touch `planner.md`'s own workflow text beyond a pointer.

---

**Task File**: `.kit/tasks/2-todo/KIT-0085-external-starter-authoring-path.md`
**Evaluation Log**: `.adversarial/logs/KIT-0085-external-starter-authoring-path--arch-review-fast.md`
**Fixture**: `tests/fixtures/external-starter/`
**Handoff Date**: 2026-08-04
**Coordinator**: planner-f5

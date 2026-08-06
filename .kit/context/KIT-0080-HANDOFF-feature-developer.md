# KIT-0080: Portable git resolution (Apple git 2.30.1) — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-08-06
**From**: planner-f5
**To**: feature-developer
**Task**: `.kit/tasks/4-in-review/KIT-0080-doctor-apple-git-230-incompat.md`
**Status**: Ready — KIT-0083 merged (d1e938e); this is the next assignment
**Evaluation**: skipped (planner) — bugfix with a live-verified fix
recipe and a causally-confirmed diagnosis; decisions are in-spec.
Evidence base: the spec's 2026-08-05 update (causal table) +
`.kit/context/KIT-0083-SESSION-FINDINGS.md` F1.

**Target Codebase**: This repo (agentive-starter-kit) — single-repo mode
(single-repo describes the planning/code split, NOT an instruction to
work in the primary clone — see Session topology).

## Session topology (read before anything else)

- Worktree: `~/Github/ask-worktrees/KIT-0080`, branch
  `feature/KIT-0080-portable-git-resolution`
- Order: `./scripts/core/project start KIT-0080` on `main` in the
  primary clone → push → `git worktree add ../ask-worktrees/KIT-0080
  -b feature/KIT-0080-portable-git-resolution` → `./scripts/core/project
  setup` in the worktree (real venv) → work there
- VERIFY, never create-in-place: `git branch --show-current` must show
  the feature branch before your first edit. Use plain `git worktree`
  commands, not `new-worktree.sh` — repairing that helper is part of
  this task; do not use the thing you are fixing.
- Never edit `agent-handoffs.json` on the branch (KIT-0086 discipline).

---

## Mission

`git rev-parse --path-format=absolute` requires git ≥ 2.31; stock macOS
ships Apple Git 2.30.1, which echoes the flag as output instead of
consuming it. Consequences range from silent (operator preset never
found → misprovisioned planning repos) to hard (`new-worktree.sh` dies;
the default worktree topology is unusable on stock macs). Make every
git-path resolution portable, silence the stray errors, make the tests
git-version-robust, and add the doctor floor check. Spec: F1–F4 with
the 2026-08-05 update; read S1–S4 in full.

## Critical constraint: the local repro is GONE

This machine now runs git 2.55.0 — every symptom is invisible here.
**You cannot manually reproduce anything.** The proof mechanism is
fixtures: a stub `git` on PATH that mimics 2.30.x behavior (echoes
`--path-format=absolute` as a first output line, then the path). The
spec's causal table (2026-08-05 update) is your expected-behavior
oracle. Do not claim verification from a clean local run — a green
suite on git 2.55 proves nothing about 2.30.1 (that is this bug's
whole lesson: "passes locally, proves nothing").

## Where the work lands (all sites, verified 2026-08-05)

The pattern `rev-parse --path-format=absolute` appears at:

- `scripts/local/bootstrap:161` (`config_home()` — the S3 preset bug)
- `scripts/local/new-worktree.sh:36` (S4 — hard death; line-42 guard
  catches the garbage and exits)
- `scripts/core/project:1512`
- `scripts/core/doctor.d/90-config-home.sh:51` (S1 — stray `dirname:`)
- `scripts/core/doctor.d/70-core-bare.sh:30`
- `scripts/core/doctor.d/55-worktree-provisioning.sh:50-51`

Re-grep before starting (`grep -rn "path-format" scripts/`) — sites may
have shifted since these anchors.

**The fix recipe** — F1's first option, live-verified by the KIT-0083
session (SESSION-FINDINGS F1 shows the working replacement): drop
`--path-format=absolute`, take plain `--git-common-dir`/`--git-dir`
output, absolutize in shell (`cd "$dir" && pwd` pattern). No version
gate, no flag-stripping, works on both gits. Apply it consistently —
consider one tiny shared shell function if the scripts can source a
common lib; if they cannot (each script must stay standalone until
KIT-ADR-0028's package extraction), replicate the same one-liner with
the same comment naming this task. Python site (`project:1512`): same
principle via `os.path.abspath`.

## F4 — doctor git-version floor

Per the spec's 2026-08-05 addition: a doctor.d line that WARNs when
`git --version` is below the supported floor. If F1 makes everything
portable to 2.30.1, the floor drops accordingly and the check documents
it; the README Requirements table (added 1e9fc51) must be updated in the
same PR so the human-readable and machine-readable floors agree. Keep
the check portable — BSD userland, no Homebrew-only tools (README
portability rule; the `timeout` lesson).

## Test approach

- Stub-git fixtures: a scratch `git` shim earlier on PATH that emulates
  2.30.x for the rev-parse flag (and delegates everything else to real
  git) — this is how F3 makes the 8 formerly-failing `test_doctor.py`
  cases assert BOTH behaviors. Isolate `GIT_*`/PATH per
  `tests/conftest.py`'s existing discipline (KIT-0043's worktree-mutation
  incident — do not let a stub leak).
- For each guard-test you add: break the guarded condition once and
  watch it fail (KIT-0083 lesson — unfalsifiable tests were its richest
  bot-finding vein).
- `new-worktree.sh`: a test that the resolution path yields the primary
  root under the stub git (the S4 death was the guard catching garbage —
  after the fix the guard should simply never fire on either git).
- `./scripts/core/ci-check.sh` before push; CI is green-on-modern-git
  only, so the stub fixtures are the only 2.30.x coverage anywhere.

## Out of scope — do not touch

- `feature-developer.md` worktree contract (KIT-0088, sequenced next)
- Preset content/authoring (`/setup-preset`), `.env` seeding (KIT-0084
  shipped it)
- KIT-ADR-0028 package extraction (if accepted, this fix migrates into
  the package later — land it here first; today's users need it)
- The 8-vs-3 baseline history (resolved; suite is fully green now —
  treat any failure as REAL)

---

**Task File**: `.kit/tasks/4-in-review/KIT-0080-doctor-apple-git-230-incompat.md`
**Key evidence**: spec's 2026-08-05 causal table;
`.kit/context/KIT-0083-SESSION-FINDINGS.md` F1 (working one-liner)

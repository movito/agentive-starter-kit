# KIT-0104 — Evaluator Review Record (PR 1: the port)

**Date**: 2026-08-13
**Change shape**: logic (new ~1,600-line Python front + engine flag) →
full trio per the tier rule.
**Input**: `.adversarial/inputs/KIT-0104-code-review-input.md` —
hand-assembled, NOT the raw 9k-line diff: the ~28 byte-identical
data-store copies under `agentive_kit/door/{engines,data}/` are
excluded with reason (pinned both directions by
`tests/test_door_data_sync.py`, which IS included); the reviewable
surface (door front, cli wiring, engine `--preserve-regions` diff,
all three test files) is included in full. Rationale: KIT-0092 —
full-format inputs over unchanged content produce findings about code
the change never touched.

## code-reviewer-fast (gemini-2.5-flash) — CONCERNS, 3 findings

Log: `.adversarial/logs/KIT-0104-code-review-input--code-reviewer-fast.md`

1. **`resolve_setting` "ignores recorded value, uses kit default"
   (High)** — **REFUTED as a defect; comment added.** This is the bash
   door's exact semantics (verified against `bootstrap`
   `resolve_setting` + the `EFFECTIVE_PROFILE` pattern, BugBot rounds
   2–3 of PR #83): the record suppresses only the PRESET layer;
   record-bound surfaces (venv offer, materials gate) key on
   `effective_profile`, and the engine preserves the record itself.
   The pre-fix smoke run confirmed byte-parity with bootstrap on this
   path. Action: docstring now states the contract explicitly
   (`d7239d9`) so later reviewers don't re-derive the same false
   positive.
2. **`load_preset` crashes on non-UTF-8 preset (Medium)** —
   **CONFIRMED, fixed** (`d7239d9`): decode/OS errors exit 2 with
   guidance; unit test added.
3. **`ensure_git_identity` accepts empty git identity (Medium)** —
   **CONFIRMED (also true of the bash door), fixed** (`d7239d9`):
   exit-0-but-empty `git config` output no longer counts as identity.

Test-gap table triage: `.env`-gitignore refusal guard now unit-tested
(the critical one); subprocess failure modes left to E2E scope;
`seed_config_home` permission-failure path is warn-and-continue by
design (courtesy, not critical path).

## Also fixed from self-review (pre-trio, `d7239d9`)

- Rung-0 adopt silently dropped explicit `--with-evaluators` /
  `--with-venv` (masking class) → acknowledged out loud + E2E pin.

## code-reviewer (o3) — FAIL, 4 bugs + 3 gaps claimed

Log: `.adversarial/logs/KIT-0104-code-review-input--code-reviewer.md`

1. **Empty-valued value flags silently default (High)** — **CONFIRMED
   as a masking-class defect, fixed** (also flagged independently by
   claude-code — convergent). Note: the bash door has the SAME
   behavior, documented as a choice in `reject_flaglike`; the packaged
   door deliberately deviates to fail loud (`--shape` trailing or
   `--shape=` → exit 2). Unit tests added.
2. **`.env` symlink-traversal overwrite (High)** — **CONFIRMED as a
   hardening gap, fixed** with `O_NOFOLLOW` + refusal message + unit
   test. Severity overstated: `.env` seeding is `--new`-only and the
   target is door-created moments earlier, so a pre-planted symlink
   requires racing the door on the operator's own machine; the bash
   door (`cat >`) has the identical exposure.
3. **Identity check skipped for adopt-with-.git (Medium)** —
   **REFUTED**: the packaged adopt invokes the consumer engine with
   `--internal-record-only`, whose git step (Step 3) is inside the
   `RECORD_ONLY` guard — nothing commits on that path, so no identity
   is needed. Same gating as bash (`new` or git-less targets only).
4. **`~user/` not expanded (Medium)** — **CONFIRMED, fixed** via
   unconditional `expanduser` on leading `~` (the bash door's
   `${1/#\~/$HOME}` actually MANGLED `~user` — the port is now better
   than the original). Unit test added.
5. **mkstemp umask window (Robustness)** — **REFUTED**: Python's
   `tempfile.mkstemp` always creates 0600 regardless of umask
   (documented behavior); the post-write chmod is defense in depth.
6. **`--preserve-regions` untested (Gap)** — **REFUTED**:
   `test_readopt_preserves_regions_byte_for_byte` (E2E) exercises
   exactly that branch end-to-end (adopt → record-only + preserve with
   existing regions → preserved byte-for-byte, no duplicates).
7. **GIT_* scrub kills GIT_SSH_COMMAND (Latent)** — **ACCEPTED AS
   DESIGNED**: the blanket scrub is the KIT-0048 incident class
   remedy, identical to bootstrap and both engines.

## claude-code (sonnet-4-6) — largely confirmatory

Log: `.adversarial/logs/KIT-0104-code-review-input--claude-code.md`

Positive observations: 0600 discipline "textbook", no shell=True
anywhere, masking-class prevention consistent, temp-then-rename
throughout, "test coverage genuinely strong". Actionable triage:

- **Empty-valued flags (Medium)** — same as o3 #1, fixed.
- **`mkdir(exist_ok=True)` TOCTOU (Medium)** — **CONFIRMED, fixed**:
  `exist_ok=False` + loud refusal converts the race into an error.
- **`_STAGE_MAP` overlap latent risk (Medium)** — **CONFIRMED as a
  guard-worthiness point**: uniqueness across both staging maps now
  pinned by a unit test.
- **`DoorExit` control-flow pattern (Medium)** — **DOCUMENTED** in the
  class docstring (bash exit-is-the-interface parity; intentional).
- **`validate_combo` forward-ref quotes (Low)** — **REFUTED**:
  `DoorOptions` is defined AFTER `validate_combo` in the module; the
  string annotation is required.
- target_path length/NUL caps, preset value caps, HOME scrub,
  env-source advisory mode, gitignore TOCTOU — **ACCEPTED AS
  DESIGNED** (operator-owned inputs on the operator's own machine;
  bash parity; list-form subprocess kills the injection class). No
  code change.
- `.git/`-temp for the .env rewrite — **KEPT**: same-filesystem
  requirement for atomic `os.replace` rules out system temp; the
  rationale (never leave stageable key material) stands.

## Outcome

Trio complete pre-PR (KIT-0035 ordering honored). Fix commits:
`d7239d9` (fast-gate), plus the deep-tier fix commit following this
record. All 148 door tests + full suite green after fixes.

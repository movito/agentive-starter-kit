# KIT-0053 Review Starter — The One Setup Door (ADR-0027 P3)

**PRs**: #81 (door + engines + shims + removal task) → #82 (docs
convergence, stacked on #81's branch — merge #81 first, then retarget
#82 to main; CodeRabbit reviews it only after retarget)
**Branches**: `feature/KIT-0053-one-setup-door`,
`feature/KIT-0053-docs-convergence`
**Task**: `.kit/tasks/4-in-review/KIT-0053-one-setup-door.md`
**Evaluator dispositions**:
`.kit/context/reviews/KIT-0053-evaluator-review.md`

## What landed

- **The door** — `scripts/local/bootstrap`: one kit-side entrance,
  `--new`/`--adopt` × `--shape single|planning` × `--profile
  python|none`. Internally resolve / validate / orchestrate as
  separately testable functions (units run against the *sourced* file
  with no filesystem access). The shape×profile matrix is a door-owned
  constant (`LEGAL_PAIRS`); planning→none forced; illegal combos exit 2
  naming the legal pairs. Resolution chain: CLI → `preset_get` stub
  (the P7 seam — returns nothing, empty output counts as unanswered) →
  kit defaults → TTY prompt; every prompt has a flag, non-TTY never
  hangs. Every door-native install ends with a `project doctor` report
  (verdict reported, never encoded). Exit contract 0/1/2.
- **Engines** — the three old entrances renamed in place with
  internals unchanged except accepted review fixes:
  `engine-consumer.sh` (was bootstrap-consumer.sh; gains the
  door-internal `--internal-record-only` mode and fresh-export region
  reseeding), `engine-materials.sh` (was bootstrap.sh; gains the
  GIT_* scrub and the `-e .git` worktree fix — both KIT-0048-class),
  `engine-export.sh` (was scripts/optional/create-project.sh; gains
  the scrub, a JSON-safe current-state writer, the 4-char prefix cap,
  and the BSD-tr crash fix).
- **Shims** at the three historical paths: each owns its frozen
  historical parse/validation and execs the door with `--legacy-shim`
  (internal fidelity channel — no door chrome/offers/doctor). The
  entire pre-existing KIT-0048/0050 characterization suite passes
  UNMODIFIED through shim → door → engine.
- **KIT-0054 filed** (`1-backlog`), pinned to 0.9.0 — removes shims +
  `--legacy-shim`, and carries two documented follow-ups: the
  shim/door record-conflict divergence, and the materials-engine
  setup-dev hardening.

## Review focus suggestions

1. `scripts/local/bootstrap` end to end (~470 lines) — especially
   `validate_combo` cross-flag rules and the `--legacy-shim` exec
   paths (byte-fidelity depends on them).
2. `engine-consumer.sh` diff only: the four `RECORD_ONLY` guards,
   `seed_region`/`replace_region` (fresh-export reseed — BugBot's
   find), and the consumer-test exclusion additions.
3. The characterization commits (`d778c59` first, then the refactor)
   — the shim contract's regression net.
4. The deliberate divergence: native adopt rejects explicit flags
   conflicting with an existing kit-install record (exit 2); the shim
   path preserves the historical silent-preserve (N1). Documented in
   KIT-0054.

## Decisions a reviewer may want to challenge

- **PR split restructured** from the pre-approved door-first/shims
  -second: renaming the engines orphans the old paths and the
  characterization suite module-skips *silently* — main would look
  green while the net was off. So shims landed with the renames;
  PR 2 is docs-only.
- **Profile ≠ shipset** (declined CodeRabbit Major): single:none
  still ships the toolchain — the profile axis owns check-hook
  content/doctor scoping/record, the shape axis owns what ships
  (ADR-0027 P1, KIT-0050). Pinned in test form.
- **Doctor gap on the materials path**: the engine ends in
  `exec claude` (interactive), so no doctor tail there — printed to
  the operator and documented in the door header.

## Verification

- 5 bot rounds on #81 (16 threads: all replied, all resolved;
  real finds fixed — region reseed, flag-swallow, `-e .git`,
  no-kit/materials contradiction; hallucinations refuted with
  evidence). Evaluator trio ran BEFORE the PR (F3 ordering):
  o3 CONCERNS → 3 accepts; two fast-gate FAILs fully triaged.
- Full suite 651+ tests green; ci-check.sh green (coverage ~92%);
  scratch e2e all four mode×shape cells with doctor output and
  correct records.
- Found by the characterization net: create-project's flagless
  export crashed on macOS (BSD tr option-parse) — fixed first,
  `8c97bb3`.

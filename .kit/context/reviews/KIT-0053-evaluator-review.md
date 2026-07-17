# KIT-0053 Evaluator Review — the one setup door

**Date**: 2026-07-15
**Input**: `.adversarial/inputs/KIT-0053-code-review-input.md` (full-file, 16 files)
**Trio**: code-reviewer-fast (gemini-2.5-flash), code-reviewer (o3), claude-code (sonnet-4-6)
**Run mode**: `ADVERSARIAL_UNATTENDED=1` — see the tooling note at the bottom.

## Round 1 — code-reviewer-fast: FAIL (5 findings)

| # | Finding | Disposition |
|---|---------|-------------|
| 1 | GIT_* scrub missing in engine-export/engine-materials | **ACCEPTED** — scrub added to both (defense in depth; door already scrubs upstream; KIT-0048 class) |
| 2 | Door exits 0 when the --new record commit fails, contradicting F6 | **ACCEPTED** — now exits 1 with guidance |
| 3 | engine-export `\|\| true` stripping hides failures | Declined — characterized historical engine behavior (engines-unchanged mandate) |
| 4 | TASK_PREFIX derivation on exotic basenames | Declined — historical; `--prefix` covers it; engines-unchanged |
| 5 | bootstrap-consumer/bootstrap shims lack a door `-x` check | Declined — co-located with the door in scripts/local (never ship apart); the create-project shim HAS the check because it genuinely ships downstream. NOTE: the finding cited a test (`test_kit_side_door_missing_or_not_executable_rejected`) that does not exist — hallucination. |

## Round 2 — code-reviewer (o3): CONCERNS (6 findings)

| # | Finding | Disposition |
|---|---------|-------------|
| 1 | Fresh-machine install dies mid-run without git identity | **ACCEPTED** — door pre-checks (`ensure_git_identity`, --global incl. XDG + --system) and fails fast with setup guidance; tested |
| 2 | Missing pipefail incl. engine-export | Partially wrong — engine-export HAS `set -euo pipefail` (line 15). **ACCEPTED for the door** (new code); declined for the other engines (characterized) |
| 3 | `resolve_setting` treats empty-but-successful preset output as answered | **ACCEPTED** — `[ -n "$v" ]` guard; unit test overrides the stub |
| 4 | 1-char derived prefix | Declined — historical engine behavior |
| 5 | GNU sed fallback broken | Declined — misread: the `cmd \|\| cmd` fallback exists exactly for the BSD/GNU split and works |
| 6 | No doctor tail on the design-materials path | Declined structural change — the engine ends in `exec claude` (interactive); documented in the door header, printed to the operator at handoff, and folded into KIT-0054's scope notes |

## Round 3 — claude-code: CHANGES_REQUESTED (2 blocking)

| # | Finding | Disposition |
|---|---------|-------------|
| 1 | MEDIUM: `find docs/adr/ -name A -o -name B \| xargs rm` matches B outside docs/adr | **REFUTED empirically** — find's path argument bounds the search; verified with a scratch tree (`ASK-outside.md` NOT matched). Hallucinated severity |
| 2 | LOW: dead `DELETED_COUNT` variable in engine-export | **ACCEPTED** — behavior-neutral dead-code removal |
| 3 | LOW: engine-consumer lacks pipefail | Declined — characterized engine |
| 4 | LOW: `usage()` sed fragility | **ACCEPTED** — now stops at the first non-comment line (order-insensitive) |

## Round 4 — code-reviewer-fast (re-run on fixed diff): FAIL (6 findings)

| # | Finding | Disposition |
|---|---------|-------------|
| 1 | CRITICAL: `--new` targeting the kit root self-overwrites | **REFUTED** — `--new` requires a non-existent target; the kit root always exists (the door lives in it) → "already exists", exit 2. claude-code round 3 independently confirmed this reasoning |
| 2 | `--adopt` of an existing repo without git identity fails cryptically | **REFUTED** — the adopt path of a pre-inited repo never commits (engine skips git init; the record is a file append; the record COMMIT exists only on `--new`, which pre-checks) |
| 3 | Shim duplicates profile forcing (F2 tension) | Declined — deliberate frozen façade for N1 byte-fidelity, documented in the shim header, removed with KIT-0054 |
| 4–6 | Prefix length / HOME-unset tilde / find stderr suppression | Declined — historical engine behaviors (engines-unchanged mandate) |

## Blind-spot note

Evaluators did not flag anything in the CSS/dual-render class (no frontend
here); the door's TTY-vs-non-TTY dual path is the analogous split and is
covered by the DEVNULL-stdin test discipline.

## Tooling data point (KIT-0052)

`adversarial-workflow 1.0.1` (system, /opt/homebrew/bin) **does** implement
`ADVERSARIAL_UNATTENDED`: in non-TTY with the flag unset it prints
"Non-TTY context detected and ADVERSARIAL_UNATTENDED is unset —
auto-cancelling" and exits 0 WITHOUT running. `echo y |` cannot work there
because auto-cancel precedes the stdin read. With `ADVERSARIAL_UNATTENDED=1`
it auto-confirms and runs. This resolves the KIT-0050-vs-planner
contradiction: the flag exists in 1.0.1 as installed; the "zero matches"
re-verification was wrong. `git status` checked after every run — no tree
mutations observed (aider-free 1.0.1).

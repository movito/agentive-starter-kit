# KIT-0116 — Evaluator Review Record

**Task**: KIT-0116 automated review pipeline (3-phase arc; this record
covers Phase 1 / PR 1; later phases append below)
**Date**: 2026-08-24
**Input**: `.adversarial/inputs/KIT-0116-code-review-input.md`
(`agentive review-input KIT-0116 --format diff` at 56502d6)

## Phase 1 — tier decision

Mixed diff: instruction-surface prose (agent bodies, commands,
workflow doc, template) + ONE behavior hunk (new
`tests/test_review_pipeline_contracts.py`). Per the fd body's
mixed-diff rule the logic hunk gets the deep tier:

| Evaluator | Ran? | Verdict |
|-----------|------|---------|
| `code-reviewer-fast` (gemini-2.5-flash) | yes | FAIL — 4 findings |
| `code-reviewer` (o3) | yes | FAIL — 7 findings |
| `claude-code` | **skipped** | no security or data-handling surface in the diff (menu criterion); the only executable change is a pytest grep file |

Input format `diff`, not `full`: the sole logic file is NEW (appears
complete in the diff anyway), and full-file input on 14 mostly-prose
files is the KIT-0092 noise shape.

## Dispositions — code-reviewer-fast (4 findings)

1. **docs-audit flag vs "not a per-task gate" wording** — FIXED:
   REVIEW-PIPELINE.md docs-habit section now states the flag schedules
   an audit pass on the declaring task, and the pass produces findings
   without blocking preflight.
2. **TASK-ID filename validity** — REJECTED: task IDs are constrained
   to `[A-Z][A-Z0-9]*-[0-9]+` by the same tooling that derives them
   (preflight branch regex, project script); invalid characters cannot
   reach the artifact path.
3. **Bash-enumeration content not validated by the test** — DEFERRED
   to Phase 2: the enumeration format is born with KIT-ADR-0036; the
   Phase-2 session deepens the check when the format exists. Carried
   on the Phase-2 worklist.
4. **KIT-0120 AC ambiguous about when 7-gate literals become stale** —
   FIXED: AC reworded to name the post-change state explicitly.

## Dispositions — code-reviewer o3 (7 findings)

1. **CRLF/BOM breaks `_frontmatter`** — FIXED: pattern tolerates
   `﻿` and `\r\n`.
2. **`- bash` (lower-case) evades the carve-out check** — FIXED:
   tools list normalized to lower-case before the membership check.
3. **Inline `tools: [Bash]` YAML shape unseen** — FIXED: extraction
   reads the whole `tools:` value block (bullet or inline form).
4. **Hard-coded gate-count sentinels balkanise** — REJECTED: sentinel
   pinning is the house pattern (`test_agent_contracts.py` doctrine —
   a legitimate rewording updates the sentinel in the same PR); the
   count IS the contract under test.
5. **Door-twin drift undetected** — REJECTED (verified wrong):
   `tests/test_door_data_sync.py` enforces byte-identity in both
   directions — it failed this very PR's first commit attempt until
   the twins were mirrored.
6. **architecture-reviewer absence only skips in Phase 2** — REJECTED
   (verified wrong): the test `pytest.fail`s on exactly that branch
   once KIT-ADR-0036 exists (see
   `test_reviewer_toolsets_satisfy_readonly_carveout`).
7. **Third-axis phrase regex over-specific** — REJECTED: the phrase is
   binding planner language (spec Notes 2026-08-24); loosened only to
   whitespace-tolerance. Same sentinel doctrine as #4.

## Logs

- `.adversarial/logs/KIT-0116-code-review-input--code-reviewer-fast.md`
- `.adversarial/logs/KIT-0116-code-review-input--code-reviewer.md`

Both verdicts were FAIL; all findings dispositioned above (5 fixed,
2 rejected-verified-wrong, 3 rejected with house-pattern rationale,
1 deferred to Phase 2 with a named owner). Native /code-review pass
recorded separately in `KIT-0116-review-pass.md` (Gate 8 artifact).

---

# Phase 2 append — PR 2 (`feature/KIT-0116-reviewer-delegation`)

**Date**: 2026-08-24
**Input**: `agentive review-input KIT-0116 --format diff` at 529c012

## Tier decision

Pure instruction-surface diff (ADR, agent bodies, workflow doc,
templates; zero executable changes at input time) → **prose-dominated**
per REVIEW-PIPELINE.md axis 1: `code-reviewer-fast` only; deep tier
and claude-code skipped (recorded here). The heavy review lift for
this PR came from Tier 1 (/code-review) and the two Tier-2 smokes —
tree-grounded, which is exactly what the axis prescribes for prose.

## Dispositions — code-reviewer-fast (verdict CONCERNS, 6 findings)

1. Missing spawn scope degrades review — REJECTED: degraded-loudly by
   design (reviewer reports the gap; fd triages). 2. Malformed TASK-ID
   in shell path — REJECTED: upstream regex-constrained; `"$rec"`
   quoted. 3. Bash-enumeration content mismatch — SUPERSEDED by this
   round's test rewrite (heading-anchored + iff allow-list).
4. Malformed Review Flags syntax — REJECTED: fail-closed rule covers
   (unregistered token → ask). 5. Bundled pointer forgotten →
   Gate 8 FAIL names remedy — working as designed (KIT-0042).
6. Record-exists-but-review-failed passes Gate 8 — ACKNOWLEDGED
   design choice, recorded in KIT-0120.

## Dispositions — Tier-1 /code-review (8 findings) and Tier-2 smokes

See the Phase-2 section of `KIT-0116-review-pass.md` — all triaged
fix-or-defer there (11 fixed incl. 1 CRITICAL and 2 HIGH; 0 deferred).

---

# Phase 3 — Tier-3 deep-review workflow (2026-09-30, fd-f5 resume session)

## Tier decision

Mixed diff: a new 200-line JS workflow (logic), instruction surfaces
(REVIEW-PIPELINE.md ×2 twins), test logic, CHANGELOG. Any behavioral
hunk ⇒ logic-shaped ⇒ full trio (fd body tier rule). Input: `agentive
review-input KIT-0116 --base origin/main` (local `main` ref stale in
the worktree), format `full`, regenerated after each fix round.

## Dispositions — code-reviewer-fast (CONCERNS, 5 findings)

1. Scope-null TypeError — **FIXED** (29ece4c→c249f30 lineage: throw
   with labeled error before fan-out). 2. Non-boolean `refuted` —
   REJECTED: schema-enforced by the runtime; failure direction is
   conservative (malformed drops, never confirms). 3. Bare `"13"`
   substring pin — **FIXED** (regex `= 13\b|13-agent`). 4. KeyError in
   toolsets test — REJECTED/out-of-scope: Phase-2 code already merged
   (full-format noise mode); a KeyError fails that one test loudly
   naming the missing key. 5. No git fallback — by-design, documented
   in REVIEW-PIPELINE.md's toolset note; crash vector was finding 1.

## Dispositions — code-reviewer o3 (FAIL, 5 findings)

1. Lens `.then` null-deref — **FIXED** (655a53b): null passes through
   to the verify guard; also made our own "null reaches next stage"
   comment true. 2. `args` binding ReferenceError — **FIXED**
   defensively (`typeof` guard); runtime docs say the global is
   provided. 3. `findings: null` crash — **FIXED** (Array.isArray
   normalization in the `.then`). 4. Label regex rejects paths —
   REJECTED: hallucinated constraint; the runtime's canonical example
   passes full file paths as labels, and existing `review:x` labels
   contain `:`. 5. Execute-not-just-parse test — DEFERRED: stubbing
   the whole runtime in pytest is disproportionate for a contract
   pin; the live smoke run covers behavior.

## Dispositions — claude-code (CHANGES_REQUESTED, 12 findings)

1. taskId/base prompt/command injection [HIGH] — **FIXED** (8136aad):
   strict shape regexes, throw on mismatch — trusted callers, but the
   seam gets enumerated per KIT-0118. 2. Second-order injection via
   `scope.summary` [HIGH] — REJECTED: single trust domain (every stage
   runs with the same session permissions); refute-first tree-grounded
   verification IS the structural mitigation; sanitizing our own
   agents' outputs to each other is theater. 3. Finding fields into
   verifier prompts [MED] — REJECTED: same trust-domain reasoning.
   4. subprocess/node PATH [MED] — REJECTED: standard CI trust,
   evaluator itself rates residual low. 5. `refuted: null` counted as
   refuted [LOW] — **FIXED** (log splits no-verdict; return shape
   unchanged). 6. `scope.files` non-array [LOW] — **FIXED**
   (Array.isArray in the empty-diff guard, consistency). 7. No
   auth-on-args [LOW] — by-design, documented (FR-11 is procedural);
   evaluator concurs no change. 8. Fragile `line == "}"` wrap [MED] —
   **FIXED** (anchored at the meta export). 9. `.flat()` shape [MED] —
   REJECTED: matches the Workflow runtime's canonical
   pipeline+parallel example verbatim. 10. Trailing-space prompt
   segments [LOW] — REJECTED: cosmetic. 11. CHANGELOG release hygiene
   [LOW] — out of scope (release train is planner-owned, arc-end).
   12. refutedCount imprecision — same as 5, fixed.

## Round budget

Three rounds (fast → o3 → claude-code), fixes committed between
rounds, input regenerated each time. 9 findings fixed, 8 rejected
with recorded reasoning, 1 deferred. Stopping at the 3-round limit.

## Logs

`.adversarial/logs/KIT-0116-code-review-input--code-reviewer-fast.md`,
`--code-reviewer.md`, `--claude-code.md` (all against the Phase 3
branch diff vs origin/main).

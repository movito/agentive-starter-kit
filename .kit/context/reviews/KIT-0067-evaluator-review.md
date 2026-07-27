# KIT-0067 — Evaluator Review Record

Ordering rule honored (KIT-0035/0046): local tests green → trio →
PR open. Mixed code+doc diff → normal trio ordering (NOT the
prose-sweep exception). Runs used the standing robust pattern
`echo y | ADVERSARIAL_UNATTENDED=1 adversarial …` from the worktree
venv; `git status` verified clean after every run.

## PR 1 — factory front door (F1 STARTING-A-PROJECT, F2 /new-project, F3 seeded self-direction)

Input: `.adversarial/inputs/KIT-0067-code-review-input.md`
(prepare-review-input.sh, `--format full`, diff vs main), regenerated
per round.

### Round 1 — code-reviewer-fast (gemini-2.5-flash): FAIL

| Finding | Disposition |
|---|---|
| `first-session` region survives a `--no-kit` re-bootstrap while the planner is pruned | **REAL — fixed** (`366f5ac`/`be6663b`): region removed with the same active-prune symmetry as the agent `rm -f`; test pinned |
| Ambiguous "key material" detection in /new-project | **Accepted minimally**: examples named (API keys, tokens, passwords) — same wording as the shipped /setup-preset |
| No path validation on the prototype route | **Accepted**: readable non-empty brief file + directory code path checked before the intake handoff |
| "Fragile `--help` parsing" | **DECLINED — premise error**, same family the task evaluation dispositioned: an agent-read command reads help prose the way a human does (ADR-0025 runtime-derivation; design validated in /setup-preset) |
| Region content not updated on re-bootstrap | **DECLINED — documented contract**: append-if-absent / consumer-owned KIT-LOCAL semantics, identical to project-rules |

### Round 2 — code-reviewer-fast: FAIL

| Finding | Disposition |
|---|---|
| Unconditional removal deletes a CUSTOMIZED first-session body | **REAL — fixed** (`366f5ac`): removal only when body is byte-identical to the kit seed; customized bodies stay with a notice; test pinned |
| Malformed BEGIN-without-END → awk deletes to EOF | **REAL — fixed** (`366f5ac`): body read via `kit_markers extract` (balanced-pair regex) first; malformed file fails loud before any awk runs; the evaluator's clean-verify round confirmed |
| `ls` too superficial for path checks | **Accepted**: wording tightened (readable non-empty file / directory) |
| Static links could rot later | **DECLINED — generic doc-rot**: all links verified against the tree at ship time; the retirement PR's grep sweep is the evidence |

### Round 3 — full trio on the fixed diff

- **code-reviewer-fast: CONCERNS** — residuals target pre-existing
  engine semantics outside this diff (Target-Repository conflict
  handling, general malformed-marker behavior). Fail-loud is the
  designed behavior there (KIT-0050/0053 review lineage). No action.
- **code-reviewer (o3): CONCERNS** — all latent/out-of-diff:
  - CRLF checkouts defeat exact-line awk matching → removal silently
    skips. Shared, pre-existing semantics of every region reader in
    this engine (grep -qx, replace_region); engine-written files are
    LF by construction. Declined as out-of-diff class.
  - Stale `REGIONS_OUT` snapshot — reviewer concedes current flow
    ordering is correct; future-proofing note only.
  - Duplicate BEGIN markers — kit_markers dedups by design
    (documented in find_regions docstring).
  - Explicitly verified clean: correct removal, customized-body
    preservation, normal seeding, malformed-pair fail-loud.
- **claude-code (security): APPROVED** — no findings.

Verdict-vocabulary note: the trio spans PASS/CONCERNS/FAIL and
APPROVED/REJECT vocabularies — logs read and interpreted, not
token-grepped.

## PR 2 — retirements (F4 D1, F5 D2, F6 D3, F7 D4, F8 D5)

Input: diff of the retirements branch vs the PR-1 branch (base
`feature/KIT-0067-factory-front-door-and-structural-cleanup`,
`--format diff` — the full-format input vs main was 966KB of
already-reviewed PR-1 content plus moved archive text; the new
content appears in full as diff additions). Diff-only caveat applied:
every finding verified against the TREE before action.

### code-reviewer-fast (gemini-2.5-flash): FAIL — all 3 "correctness" findings REFUTED on the tree

| Finding | Disposition |
|---|---|
| "Remedy points at deleted setup-serena.sh" | **REFUTED**: `.serena/setup-serena.sh` exists and is tracked — the deleted file was `.serena/claude-code/verify-serena.sh` |
| "Engines don't substitute ${PROJECT_NAME} into project.yml" | **REFUTED**: the engines never copy the template; `setup-serena.sh` (sed) and `new-worktree.sh` (bash substitution) do, both verified |
| "CLAUDE.md still lists launchers/" | **REFUTED**: zero launcher references in CLAUDE.md — the evaluator read the deletion diff as an addition |
| setup-dev doesn't exit on dispatch-init failure | **DECLINED — designed behavior**: opt-in fire-and-forget tooling; the summary reports skipped/failed states honestly (pre-existing, unchanged by D4's gate) |
| engine-materials rsync leaves stale launchers in consumers | **DECLINED — wrong channel**: materials is one-shot adopt tooling; consumer cleanup is the manifest sync's deletion pruning (KIT-0049), which the removed `.kit/launchers/` entry feeds at 0.9.0 |

### code-reviewer (o3): CONCERNS — 1 real, 1 test gap, 3 refuted/declined

| Finding | Disposition |
|---|---|
| create-agent "still recreates `.kit/launchers/.locks`" | **REFUTED — fabricated path**: `LOCK_DIR` is `/tmp/agent-creation-<hash>.lock` (env-overridable); nothing touches `.kit/launchers` (tenth o3 fabrication data point) |
| Unchecked mkdir in that path | Moot with the above (the lock mkdir IS the atomic primitive, in a retry loop) |
| Remedy display ambiguity on space paths | **REAL (latent) — fixed** (`a8dbb05`): outer decorative quotes dropped (`Run: <cmd>  # …`); test parametrized over a dir-with-spaces |
| setup-dev banner "mis-ordering" | **DECLINED — unsubstantiated**: banners number strictly sequentially via one counter |
| Launcher-dir-absent untested | **Accepted — fixed** (`a8dbb05`): test removes the whole directory |
| Verified clean by the evaluator | skip-with-notice, 6/6 banners, manifest counts, dashed paths |

### claude-code (security): APPROVED

Explicitly confirmed: verdict-vocabulary table correctly migrated to
the live skill; no security findings.

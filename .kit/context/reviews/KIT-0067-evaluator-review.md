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

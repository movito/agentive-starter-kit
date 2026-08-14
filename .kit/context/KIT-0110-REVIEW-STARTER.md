# KIT-0110 — Review Starter

**Task**: `.kit/tasks/4-in-review/KIT-0110-release-signal-integrity.md`
**Date**: 2026-08-14
**Agent**: feature-developer-f5 (session bcf683f0-era chain; this task's
worktree: `../ask-worktrees/KIT-0110`)
**Status**: Both PRs green, all bot threads resolved, ready for human
review + merge

## The two PRs (one mechanism, two repos)

| PR | Repo | What | Bots |
|---|---|---|---|
| [#132](https://github.com/movito/agentive-starter-kit/pull/132) | kit | `scripts/local/plugin_resync.py` + 24 tests; drift-guard header states the division of verification; PyYAML `.venv` rider; consumer-sync exclusions (+ packaged twin) | 4 threads, all resolved + bot-confirmed |
| [#10](https://github.com/movito/agentive-skills/pull/10) | marketplace | `plugin_sha256` column (all 27 shipped, computed by the tool — dogfood rule); `scripts/verify_plugin_integrity.py`; **the repo's first CI workflow**; roster header rewritten (what is verified WHERE) | 3 threads, all resolved; **CodeRabbit APPROVED** |

The tool populates the column the check verifies — R1 emits
`plugin_sha256`, R2's CI fails when a published body no longer matches
it. Together with the existing kit-side guard this closes the
bump-hashes-forget-bodies gap (KIT-0109 retro, Incident Closure 1).

## Verification evidence

- **Local**: 24 tests (work-list from hashes, clean merge preserves the
  ADR-0025 generalization, conflict falsified, base-not-found fails
  loud with nothing written, preflight missing-body abort, hashes-only
  emission, schema/traversal rejection, anchored entry bounds).
  Full `ci-check.sh` green.
- **Real-tree**: dry-run → work-list empty (kit in sync at 2.0.4);
  `--hashes-only` → 27 columns, spot-verified against `shasum`.
- **Falsifications** (marketplace check): bump-without-copy → exit 1
  naming the component; int-typed hash → schema exit 4 (never a
  vacuous pass); planted `skills/self-review/HOWTO.md` +
  `agents/.evil.md` → both flagged unrostered; restored → 27 verified,
  exit 0.
- **Cross-check**: kit drift guard re-run over the new column — stays
  green (additive; parser not schema-fragile).
- **Gate 5**: trio on PR 1 (fast CONCERNS / o3 FAIL / claude-code
  APPROVED), fast+deep on PR 2 — every finding verified against code;
  record `.kit/context/reviews/KIT-0110-evaluator-review.md`
  (o3's headline mechanisms refuted both rounds: indented-frontmatter
  YAML claim; pathlib-glob dotfile claim — verified empirically).

## Bot-round summary

- Kit #132 round 1: convergent BugBot Medium + CodeRabbit Major
  (missing-body abort after merge writes → partial state) — fixed with
  a preflight existence check + regression test; 2 minor threads
  (regex, DK comment). Round 2 quiet.
- Marketplace #10 round 1: workflow hardening (SHA-pinned actions,
  read-only token, `persist-credentials: false`, `--require-hashes`
  PyYAML) — all actioned; test-infra ask routed to the planner.
  Round 2: PR-ref-execution Major dispositioned as accepted residual
  (push-to-main re-run is the trusted backstop) — CodeRabbit then
  APPROVED.
- CodeRabbit rate-limit incident mid-task: org spending cap hit;
  operator raised it; review completed after `@coderabbitai review`.

## Follow-ups for the planner

`.kit/context/KIT-0110-MARKETPLACE-FOLLOWUPS.md` (rides PR #132):
F1 verify-script test infra (routed CodeRabbit ask), F2 markdownlint
CI still open (KIT-0109 retro item 3), F3 conditional `merge_group`
trigger, F4 accepted residual (PR-ref execution — revisit on external
contributors).

## Operator steps at completion (planner prompts)

1. **Merge order**: either PR can merge first (kit tool and marketplace
   column are independent until the next release); both should be in
   before the KIT-0105 train.
2. **After #10 merges**: mark **"Verify published bodies against
   roster.yaml"** REQUIRED in movito/agentive-skills branch protection
   for `main` (spec AC; the check is this repo's first).
3. **Post-merge cross-check**: `workflow_dispatch` the kit drift guard
   once #10 is on main — must stay green over the new column.
4. **KIT-0105 release train**: first tooled cut — must use
   `plugin_resync.py` and cite it in the release record (spec AC,
   remains open until that release).

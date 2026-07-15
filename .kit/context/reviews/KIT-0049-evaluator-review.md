# KIT-0049 — Adversarial Evaluator Review

**Date**: 2026-07-14
**Input**: `.adversarial/inputs/KIT-0049-code-review-input.md` (full-file, 5 files)
**Ordering**: trio ran BEFORE PR open (standing rule)
**Post-run `git status`**: clean after all three runs (no evaluator mutations)

| Evaluator | Model | Verdict |
|-----------|-------|---------|
| code-reviewer-fast-v2 | gemini-3-flash-preview | CONCERNS |
| code-reviewer | o3 | FAIL |
| claude-code | claude-sonnet-4-6 | CONCERNS |

Raw logs: `.adversarial/logs/KIT-0049-code-review-input--*.md`

## Disposition — accepted (fixed pre-PR)

| # | Finding (source) | Fix |
|---|------------------|-----|
| 1 | **Upstream-deletion divergence**: `preserve_files` copied the target's record verbatim, freezing upstream-dropped entries forever — stale file, converged core_version, never heals (o3, the FAIL driver; fast-v2 + claude-code hit the same masking from the completeness side) | Preserved `files` copy is pruned to entries upstream still ships; pruned entries are the `removed_entries` the report already announces (single-shape parity — manifest drops them, disk cleanup stays advisory). Regression test with a real upstream deletion |
| 2 | **`--only` outside the allowlist silently became a skipped addition** — an explicit request dropped with exit 0 (o3) | `UsageError` (exit 2) naming the offending entries; test |
| 3 | **`@pytest.mark.skipif` stranded on a plain helper function** — pytest silently ignores marks on non-test functions, so consumer-checkout CI would ERROR instead of skip (claude-code; a KIT-0048 block-replacement artifact) | Decorator moved to the class; docstring records why |
| 4 | **`"files": null` in the consumer manifest raised AttributeError past the except tuple** (fast-v2 + claude-code convergent) | `AttributeError` added to the tuple (schema violations refuse with exit 2); test |
| 5 | **Consumer-manifest allowlist entries skip the source-manifest path rules** — a traversal/absolute entry rides the allowlist (claude-code, MEDIUM, defense-in-depth) | Wrapper refuses entries with `..` parts or absolute paths (exit 2); test |
| 6 | Raw exception text in the refusal message duplicated the path (claude-code, LOW) | Message prints the exception class only |
| 7 | `skipped_additions` vs `--tier` semantics undocumented (claude-code, LOW) | Comment added at the intersection block |

## Disposition — declined (with evidence)

| # | Finding (source) | Why declined |
|---|------------------|--------------|
| 8 | `complete` logic "fragile" when `--only` exactly matches the allowlist∩entitlement (fast-v2 + claude-code) | If `--only` names exactly everything the allowlist records within entitlement, the run genuinely synced everything this target tracks — `complete=True` is the documented definition, not an accident. And fix #2 now errors when `--only` reaches outside the allowlist |
| 9 | `_apply` staging atomicity / kill-between-moves risk (fast-v2 + claude-code) | Pre-existing engine architecture (two-pass temp-then-commit, KIT-0034 F3), explicitly out of this PR's scope; both reviewers note it as an existing risk |
| 10 | Warn when allowlist records entries in non-entitled tiers (claude-code, LOW) | A warning flips the exit code to 1 (attention) under the frozen contract — wrong severity for a legitimate, documented state (opted-out tier entries stay recorded, unsynced). The completeness definition covers it; fix #1 removes the dangerous subcase (upstream deletions) |
| 11 | Engine CLI doesn't expose `--allowlist` (claude-code, informational) | Intentional per design — the wrapper is the shape-aware caller; reviewer agrees |

## Notes

- o3's FAIL was earned again: the deletion-divergence bug was real and its
  fix materially changed `_build_new_manifest`. Two of three evaluators
  converged on the masking behavior from different angles.
- The stranded-decorator find (claude-code) is the second
  block-replacement artifact this arc (KIT-0048's was the lost deletion)
  — large old_string replacements need a scan of what sat immediately
  ABOVE the replaced block.

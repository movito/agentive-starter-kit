# KIT-0072: Upstream the spec-compliance evaluator to the library

> **Archived (2026-08-12, backlog review — premise-tested, operator-approved)**: zero demand — premise intact (the evaluator never existed in the library) but three weeks of the heaviest gate usage in the repo's history never felt the gap; the manual /check-spec trace sufficed. A contribution to an external repo waits for a need. Revive when a spec-compliance miss actually bites, or the library repo solicits the contribution.

**Status**: Canceled
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 0.5 day (cross-repo)
**Created**: 2026-07-27
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0069 (audit truth sweep) — finding A35
**Blocks**: restoring `/check-spec` to a working gate

## Overview

`/check-spec` invokes `adversarial spec-compliance-fast`, an evaluator
that exists in no provider of the adversarial-evaluator-library. KIT-0069
established why, and the answer is that the evaluator was never a library
evaluator at all:

- The real evaluator is a **dispatch-kit project-local custom evaluator**
  at `dispatch-kit/.adversarial/evaluators/custom/spec-compliance.yml` —
  `gemini/gemini-2.5-flash`, `GEMINI_API_KEY`, ~$0.004/run, with an
  acceptance-criteria audit + spec-drift-detection prompt. dispatch-kit
  surfaced it to the CLI via `custom/link-custom.sh`, which symlinks
  `custom/*.yml` into the evaluators root.
- The library has **never** shipped one: 18 tags (v0.1.0 → v0.10.0),
  37 evaluators across 4 providers, zero spec/compliance entries, and no
  commit subject mentioning it.
- Commit `facbb4b` ported dispatch-kit's `check-spec.md` and
  `spec-compliance-input-template.md` into the kit but not the evaluator
  YAML or the link shim — the kit installs from the library, which has no
  `custom/` tier, so there was nowhere for it to land.
- A local drop-in does not stick: `.gitignore:164` ignores
  `.adversarial/evaluators`, and the tree is install-generated and
  untracked, so anything placed there is ephemeral and never reaches
  consumers.

KIT-0069 corrected the prose on both surfaces (the command and the
code-review-evaluator skill) to state the real situation. This task
restores the capability.

## Requirements

- **F1 — port the evaluator**: add dispatch-kit's `spec-compliance.yml`
  to `movito/adversarial-evaluator-library` under the provider layout the
  library actually uses (`evaluators/google/<name>/evaluator.yml`).
  Decide the canonical name deliberately — see F2.
- **F2 — settle the `-fast` suffix**: dispatch-kit's evaluator is named
  `spec-compliance` while dispatch-kit's own `check-spec.md:34` calls
  `spec-compliance-fast`. The names have never matched, so the command
  was likely broken at the source too. Pick one name and make every
  surface agree. Note the library's newer entries carry `-v2` variants
  (`code-reviewer-fast-v2`); follow the prevailing convention.
- **F3 — release and pin**: cut a library release, bump
  `[tool.adversarial] library_version` in `pyproject.toml`, and verify
  `./scripts/core/project install-evaluators` brings the evaluator down
  into `.adversarial/evaluators/google/<name>/evaluator.yml`.
- **F4 — restore the command**: re-point `.claude/commands/check-spec.md`
  Step 3 at the installed evaluator name, remove the
  non-functional notice KIT-0069 added, and update the
  `code-review-evaluator` skill's note to list it as available with its
  cost/key row.
- **F5 — verify end-to-end**: run the command against a real task spec and
  confirm a log lands in `.adversarial/logs/` with a verdict. Per the
  standing rule, exit 0 alone is not proof — check the log file.

## Acceptance Criteria

- [ ] Evaluator present in the library at the provider path, released
      under a new tag
- [ ] `library_version` pin bumped; `install-evaluators` installs it
- [ ] One canonical name used by the evaluator, the command, and the skill
- [ ] `/check-spec` runs end-to-end and writes a verdict log
- [ ] KIT-0069's non-functional notice removed from both surfaces

## Notes

- **Downstream propagation**: the adversarial-evaluator-library repo is
  itself kit-derived and has inherited the same broken
  `.claude/commands/check-spec.md`. Fix it there in the same pass.
- The verdict vocabulary in dispatch-kit's prompt (YES / PARTIAL / NO per
  criterion) does not match the library's PASS / CONCERNS / FAIL house
  style — reconcile when porting, or the command's Step 4 will describe
  verdicts the evaluator never emits.

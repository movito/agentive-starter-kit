# Review Starter: KIT-0032

**Task**: KIT-0032 — Build the `upgrader` Agent (plugin-version upgrades)
**Task File**: `.kit/tasks/4-in-review/KIT-0032-build-upgrader-agent.md`
**Branch**: feature/KIT-0032-upgrader-agent → main
**PR**: https://github.com/movito/agentive-starter-kit/pull/56

## Implementation Summary

Built `.claude/agents/upgrader.md` — a kit-local agent that automates
`docs/PLUGIN-UPGRADE-GUIDE.md` (raising a project from one `agentive-workflow`
plugin version to a newer one, plus local-agent `model:` pin refresh on a model
rollout). Design principle: **deterministic shell for the four mechanical axes;
LLM judgment confined to exactly two calls** (retire-local? / model-pin target).

- Body maps 1:1 to the guide's 7 steps + rollback, as ordered phases citing each
  guide step and the expected output to confirm before advancing.
- **Two-phase PREVIEW → operator ACK → APPLY** gate; no file/`git`/`plugin update`
  mutation before an explicit, unambiguous ACK.
- **Idempotent**: current pin == target ⇒ stop at Phase 1, zero changes (proven).
- **Concrete scope refusals** (halt + one-line reason + runbook pointer): initial
  migration, scripts/manifest (→ `MANIFEST-UPGRADE-GUIDE.md`), CLAUDE.md identity.
- Marketplace-source guard, never-edit-cached-files rule, no `settings.json` edits,
  no non-kit pushes, frontmatter-bounded `model:` rewrite, shell-quoting safety.
- Verify + Rollback phases; read-only `check-sync.sh` scripts-gap hint.
- Model pin `claude-sonnet-4-6` (current sonnet convention).

## Files Changed

- `.claude/agents/upgrader.md` (new) — the deliverable agent definition (~340 lines)
- `.kit/context/KIT-0032-DRYRUN-PROOF.md` (new) — no-op dry-run proof against this repo
- `.kit/context/reviews/KIT-0032-evaluator-review.md` (new) — Phase-7 evaluator trail
- `.kit/tasks/{2-todo → 3-in-progress}/KIT-0032-build-upgrader-agent.md` (moved)

## Verification

- **No-op dry-run** proven against this kit repo (already at pin 1.1.0):
  passes both Phase-0 guards, hits the idempotence stop at Phase 1, zero changes.
  Details: `.kit/context/KIT-0032-DRYRUN-PROOF.md`.
- `./scripts/core/ci-check.sh` green (6/6).
- Preflight gates 1–5, 7 pass (this file satisfies gate 6).

## Review History

**Bots** (PR #56): 4 findings across 3 rounds — all valid, all fixed and resolved
(Phase 3→4 reference, scripts-gap detection step, MD001 headings, Phase 8 wording).

**Evaluator trio** (Phase 7): gemini-3-flash (CONCERNS), o3 (FAIL),
claude-sonnet-4-6 (CHANGES_REQUESTED). 11 findings acted on; remainder declined
with reasons (2 verified-false o3 "break-now" bugs, a model-ID false alarm,
guide-owned greps, and out-of-scope robustness). Full triage:
`.kit/context/reviews/KIT-0032-evaluator-review.md`.

## Areas for Review Focus

1. **Scope boundary** — confirm the refusal table + Phase 0 guards correctly keep
   the agent out of initial migration, scripts/manifest, and CLAUDE.md identity.
2. **Two-phase gate** — that no mutation can precede ACK and the ACK definition is
   tight enough.
3. **Guide fidelity** — the agent cites `docs/PLUGIN-UPGRADE-GUIDE.md` rather than
   re-deriving; if they diverge, the guide wins. One follow-up logged in the review
   log: brittle greps inherited from the guide should be hardened in the guide.
4. **Distribution** — intentionally kit-local only; shipping it in the plugin is a
   separate, deferred decision (would need genericization).

## Related ADRs

- Backs **KIT-ADR-0025** (runtime-read localization — this is the mechanism it
  points at); respects the **KIT-ADR-0024 §3/§4** boundary (does not absorb the
  manifest-sync surface). No new ADR.

---
**Ready for human / code-reviewer review.**

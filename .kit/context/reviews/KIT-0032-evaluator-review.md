# KIT-0032 — Evaluator Review (Phase 7)

**Date**: 2026-06-26
**PR**: #56
**Input**: `.adversarial/inputs/KIT-0032-code-review-input.md` (full file context — the
deliverable agent + the guide it automates)

## Evaluators run

| Evaluator | Model | Verdict | Log |
|---|---|---|---|
| code-reviewer-fast-v2 | gemini-3-flash | CONCERNS | `.adversarial/logs/KIT-0032-code-review-input--code-reviewer-fast-v2.md` |
| code-reviewer | o3 | FAIL | `.adversarial/logs/KIT-0032-code-review-input--code-reviewer.md` |
| claude-code | anthropic/claude-sonnet-4-6 | CHANGES_REQUESTED | `.adversarial/logs/KIT-0032-code-review-input--claude-code.md` (run after the operator enabled `ANTHROPIC_API_KEY`) |

Note: both evaluators score the agent as code (they flag "test coverage NOT
covered" on every finding). The deliverable is a markdown agent prompt, not
executable code — there is no unit-test surface; the no-op dry-run
(`.kit/context/KIT-0032-DRYRUN-PROOF.md`) is the available end-to-end proof.
Findings were triaged on substance, ignoring the test-coverage framing.

## Acted on (cheap, in-scope, no guide divergence) — fix commit follows

1. **No-op-after-ACK state safety** (gemini): Phase 3 now *gates* Phases 4/5/7 on
   confirming the version advanced — halts before any Provenance restamp/commit so
   `CLAUDE.md` can never claim a version the install does not have.
2. **Disabled-plugin case** (o3, Phase 0b): present-but-`disabled` is now a distinct
   halt ("enable it first"), not mis-read as consuming or as initial migration.
3. **gh-api-failure fallback** (gemini, Phase 1): if the target can't be read from
   GitHub and the operator didn't name one → halt and ask; never guess a version.
4. **Target-is-a-version check** (gemini, Phase 1): confirm the target looks like
   `vX.Y.Z` before use (aligns with the project semver rule; reinforces no-guess).
5. **Frontmatter `---` boundedness** (gemini + o3, Phase 4b): the `model:` rewrite
   must sit inside the opening `---/---` delimiter pair; Read the head and confirm a
   single pin before editing; skip (never inject) if absent. Strengthens spec Risk 2.

## Declined (verified false, or out of the spec's deliberately-narrowed scope)

- **`tools:` omits `git`/`gh`/`base64`/`sed`** (o3, rated "break-now") — **false
  premise.** The `tools:` field lists *Claude tools* (`Bash`), not shell binaries;
  binaries are governed by `.claude/settings.json` allowlists. `ci-checker.md` is
  `Bash`-only and runs `gh`/`git` fine. Verified, not a bug.
- **`^model:` misses indented frontmatter** (o3, rated "break-now") — **verified
  N/A.** `grep -rnE '^[[:space:]]+model:' .claude/agents/` finds zero real indented
  pins; all are column-0. The guide owns this exact grep; broadening to `^\s*model:`
  would risk matching nested keys. Declined.
- **Brittle CLI-output matching** — ANSI colours, URL-form source line, `@` vs
  `(source)` row format, `grep -A8` Provenance window, case-insensitive flat-ref
  grep (o3 + gemini). These greps are **inherited verbatim from
  `docs/PLUGIN-UPGRADE-GUIDE.md`**. The agent must not diverge from the guide
  (spec: "the guide wins"). If the guide's patterns are brittle, that is a *guide*
  bug to file separately — recorded here as a follow-up, not patched in the agent.
- **Semver build-metadata normalization** (`1.4.0+meta` vs `1.4.0`; o3) — plugin
  versions are plain `X.Y.Z`; build metadata never appears. Third-party-scale
  robustness the spec explicitly declined. The basic version-format check (#4) covers
  the realistic case.
- **POSIX/Windows portability** (`base64 -d`, `sed`; gemini) — these projects are
  macOS-only; the spec's evaluation already declined portability shims.
- **Shell injection via version string** (gemini, "High") — the target is never
  interpolated into a destructive command (Phase 3 update is a fixed string; the
  version only lands in CLAUDE.md text + comparison). The format check (#4) is the
  proportionate guard; a full sanitiser would be ceremony.

## Acted on — claude-code (CHANGES_REQUESTED) second fix commit

claude-code surfaced findings the other two missed; verified and applied the cheap,
high-value ones:

6. **Shell-injection / quoting** (HIGH + MEDIUM, Phases 2a/4b/8): added a hard rule
   — single-quote every value substituted into a shell command from an external
   source (CHANGELOG, plugin output, operator input, paths); halt if a value
   contains a quote/metacharacter. The agent has `Bash`, so this is a real vector.
7. **ACK-gate ambiguity** (MEDIUM, Phase 2c): a valid ACK must be an explicit,
   unambiguous go-ahead; questions/hedged/scope-changing replies are non-ACKs →
   re-print PREVIEW and wait. (Lighter than claude-code's rigid literal-token
   proposal, which would be over-rigid for an interactive single-owner flow.)
8. **Phase 3/4 "broken window"** (MEDIUM): added a note — after the plugin update,
   the reference fixes must complete or roll back; never commit a partial state.
9. **`! git … push` footgun** (LOW, Phase 7): reworded — a leading `!` negates the
   exit code in bash; it is only the session prefix meaning "operator runs this".
   Now phrased as a plain operator instruction, no misleading shell line.
10. **CHANGELOG read classified as deterministic** (LOW, Phase 2a): replaced the
    vague "read the CHANGELOG" with a concrete `gh api … CHANGELOG.md | base64 -d`
    fetch, and explicitly scoped the only reasoning to categorizing the diff
    (which feeds Judgment Point 1) — removes the run-vs-reason contradiction.
11. **Idempotence normalization** (LOW): compare the bare `X.Y.Z` token extracted
    from both sources so quoting/whitespace can't cause a false mismatch.

### Declined from claude-code (verified / out of scope)

- **Model ID `claude-sonnet-4-6` "looks like a typo"** (LOW) — **verified correct.**
  `claude-sonnet-4-6` is the current Sonnet 4.6 identifier (and the kit's current
  sonnet convention, e.g. `create-project.md`). The evaluator's model knowledge is
  stale — ironic, since stale model IDs are exactly what this agent exists to fix.
- **Pin the GitHub fetch to a commit SHA / supply-chain integrity** (HIGH) — the
  `?ref=main` fetch is inherited from the guide, and the PREVIEW→ACK gate *already*
  provides the "operator confirms the target version before apply" control
  claude-code asks for (the operator sees the version delta and must ACK before any
  mutation). SHA-pinning diverges from the guide and is third-party-scale hardening
  the spec declined. No change; the existing gate covers the intent.

## Final verdict

Across three cross-family evaluators (gemini-3-flash, o3, claude-sonnet-4-6): 11
findings acted on, the rest declined with reasons (2 verified-false "break-now"
bugs, model-ID false alarm, guide-owned greps, and explicitly-out-of-scope
robustness). No FAIL-level issue survives verification; the structural design
(two-phase gate, scope refusal, judgment confinement) was praised by all three.

## Follow-up to raise against the guide (not this PR)

The convergent "brittle grep" findings apply to `docs/PLUGIN-UPGRADE-GUIDE.md`
itself (the agent only mirrors it). If CLI output formats drift, harden the guide's
grep patterns there and re-sync the agent — keeping the two in lockstep per the
spec's "guide wins" rule.

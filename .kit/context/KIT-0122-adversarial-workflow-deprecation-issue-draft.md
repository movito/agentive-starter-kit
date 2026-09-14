# Issue draft — movito/adversarial-workflow (deprecation metadata)

<!-- Draft companion to KIT-0122. Separate from the KIT-0121 messaging
     issue: that one is about library update's silent no-op; this one is
     about running deprecated evaluators without warning. -->

**Title**: Evaluator deprecation metadata (`status: deprecated`,
`replaced_by`) is parsed and discarded — deprecated evaluators run
silently

## Summary

adversarial-evaluator-library v0.10.0 marks superseded evaluators with
`status: deprecated`, `deprecated_at`, and `replaced_by: <name>-v2` in
their evaluator.yml. The CLI has no handling for these fields anywhere
— the only code that touches them is the unknown-field filter in
`evaluators/discovery.py` (:244 @ 038d4e7), which logs

```text
Unknown fields in evaluator.yml: deprecated_at, replaced_by, status
```

and drops them. `adversarial code-reviewer-fast` therefore runs the
deprecated evaluator exactly like an active one, and the one signal an
operator gets reads as harmless schema chatter (and prints for EVERY
command, including `--help`, so it trains people to ignore it).

## Real-world impact

A downstream implementation agent ran a full pre-PR review gate on
deprecated `code-reviewer-fast` (Gemini 2.5 Flash) and only discovered
it while collecting retro metrics. Re-running the identical input on
`code-reviewer-fast-v2` (Gemini 3 Flash): v1 → FAIL, 5 findings, 0
surviving triage; v2 → CONCERNS with 1 real finding v1 missed. The
stale model materially changed a review-gate outcome. (2026-09-14;
library v0.10.0 @ 8e457568.)

## Suggested behavior — the (a)/(b)/(c) decision

When the resolved evaluator's yml carries `status: deprecated`:

- **(a) Warn + run** (minimum): a loud, colorized, per-invocation
  banner naming the replacement — not a logger.warning lumped in with
  schema noise:
  > ⚠️  'code-reviewer-fast' is DEPRECATED (since 2026-04-28).
  > Replacement: code-reviewer-fast-v2. Running the deprecated
  > evaluator anyway.
- **(b) Auto-route with escape hatch**: resolve to `replaced_by`
  automatically, print what happened, and offer `--exact` (or similar)
  to force the deprecated one — reproducing an old review is the one
  legitimate use.
- **(c) Refuse**: exit non-zero naming the replacement, `--exact` to
  override.

Any of the three fixes the silent case; (b) is friendliest to fleets of
non-interactive agent callers, which is the dominant consumer of this
CLI in practice. Whichever is chosen, please also accept the three
fields in the schema so the unknown-field warning stops firing on
every current-library install.

## Repro

```bash
# with library v0.10.0 installed
adversarial code-reviewer-fast <any-input>.md
# → runs to completion; deprecation surfaced only as
#   "Unknown fields in evaluator.yml: deprecated_at, replaced_by, status"
#   mixed into startup noise for all evaluators at once.
```

## Related

- Companion issue (separate draft): `library update`/`check-updates`
  messaging when a directory contains unstamped evaluator files.

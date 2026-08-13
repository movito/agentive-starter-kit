# KIT-0094: Own the markdown lint — class sweep + pre-commit gate, so bots stop reviewing style

**Status**: Backlog
**Priority**: low (quick win — assign between phases or as a passenger on any doc-heavy task; **preferred vehicle (planner, 2026-08-13): passenger on KIT-0104**, whose F5 prose sweep is doc-heavy and would otherwise re-feed the bot-nit machine this task retires)
**Type**: Infrastructure / hygiene
**Estimated Effort**: 2-3 h
**Created**: 2026-08-08
**Source**: operator, PR #118 review — an MD029 one-character nit
(babysit-pr.md:104) as the latest instance of a recurring class
**Evaluation**: skipped (planner) — mechanical cleanup, decisions in-spec

## Overview

The repo has NO markdownlint config, no local linting, and no
pre-commit gate for markdown (verified 2026-08-08) — while CodeRabbit
runs `markdownlint-cli2` with its defaults against every PR. Result:
style violations surface one review thread at a time, forever
(MD029 on #118, MD040 bare fences on KIT-0067, the five-face markdown
class on KIT-0071). Each thread costs a triage-reply-resolve round for
a one-character fix. Own the lint locally and the class disappears
from review.

## Requirements

- **F1 — repo markdownlint config** (`.markdownlint-cli2.jsonc` or
  equivalent): start from the rules CodeRabbit has actually flagged
  (MD029 ordered-list style, MD040 fenced-code language, etc.);
  deliberately disable rules we don't want (line-length is almost
  certainly off — this repo's prose uses long tables and links).
  **MD029 decision (KIT-0092 retro #6)**: configure `ol-prefix` to a
  style permitting sequential numbering, or document MD029-on-
  adjacent-hunk-context-lines as a known false-positive class — the
  #118 thread was CodeRabbit linting numbering that only looked wrong
  inside the diff hunk. Decide once here, not per-thread.
  Scope: live markdown only — exclude `.kit/tasks/6-canceled/`,
  `docs/archive/`, `.kit/context/retros/`, `reviews/` (historical
  records stay as written; the .coderabbitignore exclusions are the
  precedent list).
- **F2 — one class sweep** over the in-scope files; mechanical fixes
  only, no prose rewording. Indentation-tolerant patterns per the
  bot-triage class-sweep rule.
- **F3 — pre-commit hook** (`markdownlint-cli2` has a standard
  pre-commit mirror) over the same scope, so a violation fails
  locally before it can become a bot thread.
- **F4 — falsifiability**: break one rule once, watch the hook fail.

## Acceptance Criteria

- [ ] Config committed; scope exclusions match the historical-records
      precedent
- [ ] Sweep leaves in-scope files clean under the config
- [ ] Pre-commit gate active and proven falsifiable
- [ ] The next PR's CodeRabbit round produces zero markdown-style
      threads (observed, not assumed — note it in the completion)

## Out of Scope

- Rewording any prose; historical/archived markdown
- CodeRabbit configuration changes (.coderabbit.yaml) — our local
  gate makes their duplicate findings moot on its own

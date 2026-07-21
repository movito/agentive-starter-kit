# KIT-0057 — Skills-Home Consumer-Impact Inventory (F1 gate)

**Prepared**: 2026-07-21, before any file move (the ADR-0027 P6
inventory gate: this artifact is committed first; the move commit
follows it).

## The two homes today

| Home | Contents | Resolved by |
|------|----------|-------------|
| `.claude/skills/` | `bot-triage`, `pre-implementation` | Claude Code skill discovery (bare names) |
| `.kit/skills/` | `code-review-evaluator`, `review-handoff`, `self-review` | Nothing mechanical — read by agents/humans via documented paths only |

The three builder skills are ALSO distributed as plugin copies
(`agentive-workflow:<name>`, plugin v1.1.0) — that is how downstream
projects invoke them today.

## Repo references to `.kit/skills/` (verbatim grep, 2026-07-21)

Command:

```bash
grep -rn '.kit/skills' --include='*.md' --include='*.sh' --include='*.py' \
  --include='*.yml' --include='*.json' --include='project' \
  scripts/ docs/ .claude/ .kit/skills/ CLAUDE.md README.md
```

### Live (must keep working through the deprecation cycle)

| Reference | Kind | Disposition |
|-----------|------|-------------|
| `scripts/core/project:1840` — docstring cites `.kit/skills/self-review/SKILL.md` | code docstring | update to new path in the move commit |
| `scripts/.core-manifest.json:50` — `.kit/skills/` in the `kit_builder` tier | sync manifest | keep for the deprecation cycle (the path still exists as a symlink dir); tier entry retargets to `.claude/skills/` in the 0.9.0 removal task |
| `.claude/skills/pre-implementation/SKILL.md:300` — "skill files in `.kit/skills/`" | skill cross-ref | update in the move commit |
| `.kit/skills/code-review-evaluator/SKILL.md:200` — cites `.kit/skills/self-review/SKILL.md` | skill cross-ref | update in the move commit (file itself moves) |
| `CLAUDE.md:12,16`, `README.md:409,413` — directory trees name both homes | docs | F5 docs-convergence commit |
| `docs/DISTRIBUTION-ARCHITECTURE.md:98,117` — "`.kit/**` templates/skills/ADRs" | docs | F5 docs-convergence commit (gains the canonical-homes table) |
| `docs/MANIFEST-UPGRADE-GUIDE.md:127` — example manifest lists `.kit/skills/` | docs | F5 commit — annotate; the example retargets in 0.9.0 with the manifest itself |

### Historical (records — never edited)

`docs/adr/ADR-0007:300`, `docs/adr/ADR-0008:70` (accepted ADR texts),
`.kit/adr/KIT-ADR-0027:43,256` (the ADR that ordered this merge),
and ~20 task/handoff/retro files under `.kit/tasks/` and
`.kit/context/` — all records of past states; N3 forbids touching
them, and none is load-bearing.

## Plugin repo (`~/Github/agentive-skills`)

- Layout: `plugins/agentive-workflow/skills/<name>/` — a **flat home
  of copies**; no structural dependency on either kit path. Plugin
  v1.1.0 (`plugin.json`).
- Textual refs to `.kit/skills/`:
  `skills/pre-implementation/SKILL.md:300` (same line as the kit copy)
  and `CONSOLIDATION.md` (the KIT-0030 source-map, 4 blocks listing
  `.kit/skills/*` as the copies' upstream sources).
- **Impact**: after the merge the plugin's source-map points at the
  deprecated path, and its skill copies drift from the edited kit
  originals. Per N2 this is FILED, not done here → follow-up task
  (refresh plugin copies + CONSOLIDATION source map, next plugin
  release).

## Downstream repos / pinned plugin versions

- The consumer engine never ships `.kit/skills/` (the consumer
  manifest heredoc has no `kit_builder` tier; the never-ship contract
  covers builder internals). Consumers get builder skills ONLY via the
  plugin namespace — unaffected by a repo-internal move.
- `.claude/` ships to every shape via the consumer engine's rsync, so
  after the merge consumers ALSO receive the three builder skills as
  native `.claude/skills/` copies — that is the ADR's intent
  ("`.claude/skills/` is the Claude-Code-resolution home and the
  distributed one").
- Downstream pins (suwinex, moss, label-maker: plugin 1.1.0) see no
  path change until they take a plugin release; nothing here breaks a
  pinned install.

## Decision (per ADR-0027 P6 + planner prior)

**Winner: `.claude/skills/`.** The three builder skills move in beside
`bot-triage` and `pre-implementation`. `.kit/skills/<name>` becomes a
relative symlink to `../../.claude/skills/<name>` for ONE release —
read-both, tested from both paths — and the symlinks are removed in
0.9.0 by the filed removal task (joining KIT-0047 and KIT-0054's
pinned removals).

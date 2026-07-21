# KIT-0057 Review Starter — Canonical Homes + the Prune (ADR-0027 P6)

**PR**: https://github.com/movito/agentive-starter-kit/pull/90
**Branch**: `feature/KIT-0057-canonical-homes-prune`
**Task**: `.kit/tasks/4-in-review/KIT-0057-canonical-homes-and-prune.md`
**Status**: CI green · CodeRabbit APPROVED · BugBot pass · 5/5 threads
resolved · evaluator trio run pre-PR (record:
`.kit/context/reviews/KIT-0057-evaluator-review.md`)

## What this closes

The LAST task of the ADR-0027 transformation arc. On merge: the arc is
complete, 0.9.0 becomes cuttable (KIT-0047 + KIT-0054 + KIT-0059
execute in it), and the downstream migration pass has a stable target.

## Review focus (suggested order)

1. **The skills merge shape** — `.claude/skills/` is canonical; the
   deprecated `.kit/skills/<name>/` entries are REAL dirs holding
   relative `SKILL.md` symlinks. File-level deliberately:
   `sync_from_manifest._read_dir` does not descend into symlinked
   dirs (a dir-symlink would make pull-sync prune consumer copies) —
   pinned by `test_sync_engine_reads_content_through_old_path`.
2. **Identity seams** — the kit is `agentive-starter-kit`; BOTH
   seeding paths reset a target's name to the placeholder+TODO:
   `engine-export.sh` (--new, characterized in
   `test_export_e2e_defaults`) and `engine-consumer.sh`'s top-level
   copy (adopt — BugBot round-1 catch, pinned in the door adopt e2e).
3. **The two guards** — `TestBakedManifestVersion` (heredoc-bounded
   extractor, desync-proof test) and `test_bots_conformance.py`
   (13-row table through door/project/preflight readers, duplicate-key
   first-wins pinned per patterns.yml).
4. **Prune evidence** — in the PR body: scripts/optional dispositions
   (all keep, each grep-referenced), stray sweep (nothing deleted, N3
   trivially satisfied), no tracked __pycache__/egg-info.

## Known/accepted

- Windows checkout of the KIT repo with core.symlinks=false
  materializes the 3 symlinks as text files — accepted for the one
  deprecation release (consumers unaffected: sync ships dereferenced
  content); gone in 0.9.0 (KIT-0059).
- o3 evaluator FAIL fully refuted with code evidence (see review
  record) — second full refutation after KIT-0050.
- `pyproject.toml` `description` TODO and the consumer-manifest seed's
  `core_version 2.0.0` left as noted observations (planner calls).

## Follow-ups filed

- **KIT-0059** (backlog, PINNED 0.9.0): remove the read-both entries +
  retarget the manifest's `.kit/skills/` entry.
- **KIT-0060** (backlog, next plugin release): refresh plugin skill
  copies + CONSOLIDATION.md source map.

## Arc-end consequences (planner, on merge)

Per the task's Notes: (1) the operator's standing `rm -rf` allowlist
reminder fires (`/tmp/`, `~/Github/ask-worktrees/` — third-recurrence
friction), (2) 0.9.0 is cuttable, (3) the downstream migration pass
starts.

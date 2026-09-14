# KIT-0121: Evaluator update channels are disjoint — `adversarial library update` silently no-ops in kit projects

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 3-5 hours (Option A) / 1-2 hours (Option B, doc-only)
**Created**: 2026-09-14
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Related**: KIT-0079 (owns moving the pin reader from pyproject to
`.adversarial/config.yml` — same subsystem, coordinate), KIT-0119
(`--against-preset` ignores `evaluators:` — adjacent doctor surface),
KIT-0108 (owns collapsing duplicated record readers)

## Overview

Two install channels write into `.adversarial/evaluators/`, and each is
invisible to the other's update mechanism:

1. **Kit channel** (`./scripts/core/project install-evaluators`, also
   run by the setup door): clones `adversarial-evaluator-library` at
   the tag pinned in `pyproject.toml` → `[tool.adversarial]
   library_version`, raw-copies the library's `evaluators/<provider>/`
   tree (nested subdirectories, no per-file provenance), and stamps a
   single `.adversarial/evaluators/.installed-version` file.
2. **CLI channel** (`adversarial library install <provider>/<name>`):
   writes each evaluator as a FLAT top-level `.yml` with a `_meta:`
   provenance block (`source: adversarial-evaluator-library`, version,
   install date). `adversarial library check-updates` / `update --all`
   manage ONLY these.

Consequence: in every kit-bootstrapped project,
`adversarial library update --all --yes` finds zero managed evaluators
and exits 0 — the operator believes they updated; nothing happened.
Observed live in a downstream consumer project 2026-09-14. Worse, the
adversarial-evaluator-library agent's own guidance recommends exactly
those CLI commands as THE update path, so the two ecosystems currently
hand operators contradictory instructions.

## Verified facts (2026-09-14, kit main + adversarial-workflow @ 038d4e7)

1. `scan_installed_evaluators()`
   (`adversarial_workflow/library/commands.py:82`) counts a file only if
   (a) it sits at the TOP level of the evaluators dir — the glob
   `evaluators_dir.glob("*.yml")` is non-recursive — and (b) its YAML
   has a `_meta` block with `source == "adversarial-evaluator-library"`.
   Kit-installed evaluators fail BOTH conditions (nested under provider
   dirs; no `_meta` — verified by grep over the kit's own
   `.adversarial/evaluators/`).
2. `library_update()` (same file, :667) with `--all` and an empty scan
   prints "No library-installed evaluators found." and returns 0.
3. Kit installer: `cmd_install_evaluators`
   (`scripts/core/project:885ff`) — `git clone --depth 1 --branch
   <pin>`, copies `evaluators/` wholesale, writes `.installed-version`
   (currently `v0.10.0 (8e457568)` in this repo). Rerun is a guarded
   no-op without `--force`.
4. The pin's source of truth is `pyproject.toml`
   (`[tool.adversarial] library_version = "v0.10.0"`);
   `.adversarial/config.yml`'s `evaluator_library_version` is
   deliberately inert until KIT-0079.
5. The two layouts CAN coexist in one directory (kit-nested + CLI-flat),
   which permits duplicate evaluators at mismatched versions with no
   surface reporting the conflict.

## Requirements

**Decision first** — pick one of:

- **Option A (convergence)**: teach the kit installer to write installs
  the CLI channel can see — either stamp `_meta` blocks into the copies
  it makes (and flatten, or get the upstream scanner made recursive),
  so `adversarial library check-updates` becomes truthful in kit
  projects. Requires coordinating with upstream on layout expectations
  (see the companion adversarial-workflow issue, References). The pin
  remains authoritative: decide what `library update` pulling AHEAD of
  the pin should mean before enabling it — a CLI update that outruns
  the pyproject pin reintroduces drift in the other direction.
- **Option B (demarcation, doc-only)**: keep the channels separate and
  make that explicit everywhere an operator could trip: kit docs +
  `.adversarial/config.yml` header state that kit projects update via
  pin-bump + `project install-evaluators --force`, and that
  `adversarial library update` does not apply; propose the same note
  for the adversarial-evaluator-library agent guidance upstream.

Either option:

1. `project install-evaluators` rerun guidance (`--force`, `--ref`)
   documented as THE consumer update path.
2. The library agent guidance drift is reported upstream (the agent
   currently recommends CLI-channel commands unconditionally —
   "Finding Projects with Evaluators" will match every kit project and
   its update commands no-op in all of them).
3. If Option A: parity/conformance test that a kit-installed evaluator
   is visible to `scan_installed_evaluators()`.

## Out of scope

- Moving the pin reader to config.yml — KIT-0079's charter.
- The upstream CLI messaging fix ("No library-installed evaluators
  found" without explaining why present files don't count) — filed as
  an adversarial-workflow issue, drafted in this task's References.

## Acceptance Criteria

- [ ] Channel decision (A or B) recorded with rationale
- [ ] A kit consumer following the documented path can update
      evaluators and verify the result (`.installed-version` or
      `check-updates` per chosen option)
- [ ] No surface still implies `adversarial library update` works
      unconditionally in kit projects
- [ ] Upstream issue filed on movito/adversarial-workflow (draft below)
- [ ] Library-agent guidance drift reported to
      adversarial-evaluator-library maintainers
- [ ] If Option A: conformance test pinning kit-install visibility

## References

- Discovery session 2026-09-14 (operator ran
  `adversarial library update --all --yes` in a kit-based consumer
  project; silent no-op)
- `adversarial_workflow/library/commands.py` — `scan_installed_evaluators`
  (:82), `library_check_updates` (:569), `library_update` (:667)
- `scripts/core/project` — `cmd_install_evaluators` (:885),
  `_get_evaluator_library_version` (:35)
- Upstream issue draft: `.kit/context/KIT-0121-adversarial-workflow-issue-draft.md`

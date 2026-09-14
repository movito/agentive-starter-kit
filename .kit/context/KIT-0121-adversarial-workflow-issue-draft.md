# Issue draft — movito/adversarial-workflow

<!-- Draft companion to KIT-0121. File with:
     gh --repo movito/adversarial-workflow issue create \
        --title "<title below>" --body-file <body extracted from this file>
     (strip this comment block and the title heading marker line) -->

**Title**: `library update` / `check-updates` silently ignore evaluator
files without `_meta` — misleading in directories populated by other
installers

## Summary

`adversarial library update --all --yes` in a project whose
`.adversarial/evaluators/` directory is fully populated reports
"No library-installed evaluators found." (or, one layer up, everything
"up to date") and exits 0. The operator's reasonable reading is "my
evaluators are current." In reality the command never looked at their
files.

Two conditions in `scan_installed_evaluators()`
(`adversarial_workflow/library/commands.py:82`) exclude them:

1. The glob is non-recursive (`evaluators_dir.glob("*.yml")`), so
   evaluators organized in provider subdirectories
   (`evaluators/anthropic/…`, matching the layout of
   adversarial-evaluator-library itself) are invisible.
2. Only files carrying a `_meta:` block with
   `source: adversarial-evaluator-library` count — i.e. only files that
   `adversarial library install` itself wrote.

Both conditions are defensible bookkeeping. The problem is the
*messaging*: when the directory demonstrably contains evaluator YAML
files that fail these conditions, the command says nothing about why
they don't count.

## Real-world impact

agentive-starter-kit (and every project bootstrapped from it) installs
evaluators via a pinned git clone that raw-copies the library's nested
`evaluators/<provider>/` tree — no `_meta` blocks. In all such projects
the CLI's update commands are permanent silent no-ops, while the
adversarial-evaluator-library agent's own usage guidance recommends
exactly `library check-updates` / `library update --all` as the update
path. Operators follow that guidance and believe they've updated.
(Observed 2026-09-14; verified against adversarial-workflow @ 038d4e7.)

## Suggested fixes (independent; any subset helps)

1. **Say why files don't count.** When the scan finds zero managed
   evaluators but the directory contains `*.yml` files (top-level or
   nested), print e.g.:
   > Found N evaluator file(s) not managed by this command (no `_meta`
   > provenance block — likely installed by another tool or copied
   > manually). `library update` only manages evaluators installed via
   > `adversarial library install`.
2. **Recurse, or explain the layout rule.** Either make the scan
   recursive (still gated on `_meta`), or state that only top-level
   files are considered.
3. **Optional, larger**: an `adopt`/`stamp` subcommand that writes
   `_meta` into existing unstamped files after verifying them against
   the index, converting foreign installs into managed ones.

## Repro

```bash
mkdir -p /tmp/repro/.adversarial/evaluators/anthropic/x
cp <any evaluator.yml from adversarial-evaluator-library> \
   /tmp/repro/.adversarial/evaluators/anthropic/x/
cd /tmp/repro
adversarial library update --all --yes
# → "No library-installed evaluators found." — exit 0, no mention of
#   the file that is sitting right there.
```

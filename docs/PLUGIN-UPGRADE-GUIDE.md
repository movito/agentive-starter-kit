# Plugin Upgrade Guide: bumping a project to a newer `agentive-workflow` release

A runbook for raising a project from one `agentive-workflow` plugin version to
a newer one — including the case where a new Claude model is rolled out and the
plugin's agent `model:` pins move. Written to be followed **by an agent** (the
future upgrader agent, or any agent pointed at a project) or by hand.

## Scope

- **In scope**: a project that **already consumes** the plugin, moving to a
  newer release; refreshing agent `model:` pins on a model rollout.
- **Out of scope**: the *initial* migration onto the plugin (deleting local
  copies, namespacing references). That is a one-time, manual step done per
  project — not covered here.
- **Boundary** (do not blur):
  - This guide covers the **plugin** — agent definitions, workflow commands,
    skills (KIT-ADR-0024 §3).
  - **Scripts** (`scripts/core/`) upgrade separately via the manifest sync —
    see `docs/MANIFEST-UPGRADE-GUIDE.md`.
  - **Topology / identity** (target repo, project rules) lives in `CLAUDE.md`.

## When to run

- A new `agentive-workflow` release is published to `movito/agentive-skills`.
- A new Claude model is rolled out and you want the project's agents on it.

## Prerequisites

- `.claude/settings.json` enables `agentive-workflow@agentive-skills` and the
  `agentive-skills` marketplace source is **GitHub** (`movito/agentive-skills`),
  not a local directory. Verify:

  ```bash
  # Accept a GitHub-form Source line — paren form "GitHub (movito/agentive-skills)"
  # or URL form "https://github.com/movito/agentive-skills", either case. The
  # pattern is anchored to the Source field so a local checkout at a path like
  # "Directory (/Users/alice/github/movito/agentive-skills)" cannot slip past,
  # and end-anchored so a similarly named repo (movito/agentive-skills-beta)
  # cannot either:
  claude plugin marketplace list | grep -Ei '^[[:space:]]*source: *(github \(|https://github\.com/)movito/agentive-skills([[:space:]]*\)|$)'
  # match → GitHub-sourced, proceed; no match → inspect the full output
  ```

  If the source reads `Directory (...)`, it is a dev/spike artifact —
  re-point it before upgrading:

  ```bash
  claude plugin marketplace remove agentive-skills
  claude plugin marketplace add movito/agentive-skills
  ```

- `CLAUDE.md` has a `## Provenance` section recording the current pin
  (e.g. `agentive-workflow@1.1.0`).

## Steps

### 1. Determine current and target versions

```bash
# Current pin (two sources — they should agree):
# Scope to the whole Provenance section (a fixed -A window breaks if the
# pin sits lower in the section; sed stops at the next '## ' header):
sed -n '/^## Provenance/,/^## /p' CLAUDE.md | grep agentive-workflow
# Tolerate row-format drift ('@agentive-skills' vs '(agentive-skills)')
# while excluding similarly-named siblings (e.g. agentive-workflow-beta):
claude plugin list | grep -A3 -E 'agentive-workflow([@ (]|$)'
```

Target = the version you intend to land. Either the operator names it, or read
the latest published version:

```bash
gh api 'repos/movito/agentive-skills/contents/plugins/agentive-workflow/.claude-plugin/plugin.json?ref=main' \
  --jq '.content' | base64 -d | grep '"version"'
```

If current == target, stop — nothing to do.

### 2. Refresh the marketplace and update the plugin

```bash
claude plugin marketplace update agentive-skills      # pull latest marketplace metadata from GitHub
claude plugin update agentive-workflow@agentive-skills
claude plugin list | grep -A3 -E 'agentive-workflow([@ (]|$)'   # confirm the version advanced
```

> The plugin's semver `version` is the cache key. If the upstream version was
> **not** bumped, `/plugin update` reports "already at the latest version" and
> nothing changes — re-publishing the same version never propagates.

### 3. Reconcile what the new version changed

Compare the artifact set before/after (or read the plugin CHANGELOG):

- **Added** commands/agents/skills — they are immediately available namespaced
  (`agentive-workflow:<name>`); no action required. Optionally retire a
  remaining *local* copy that the plugin now supersedes (that is a manual
  de-dup, not part of this upgrade).
- **Removed or renamed** artifacts — grep the project for references to the old
  namespaced names and update them:

  ```bash
  grep -rn 'agentive-workflow:<old-name>' .claude .kit CLAUDE.md
  ```

- **Namespacing hygiene** — confirm no flat references crept back in
  (they would not resolve now that artifacts come from the plugin):

  ```bash
  # -i: catch case-drifted slash-references in prose too (a capitalized
  # command name after a slash would evade a case-sensitive grep)
  grep -rinoE '(^|[^:A-Za-z/.-])/(preflight|retro|triage-threads|check-ci|check-bots|wrap-up|babysit-pr|wait-for-bots|commit-push-pr|start-task|check-spec|status)([^.A-Za-z]|$)' \
    .claude .kit/templates .kit/context/workflows CLAUDE.md
  # expect no output
  ```

### 4. Model rollout: update local agents' `model:` pins (only if applicable)

The plugin's own agents get their new `model:` pins from the update in Step 2.
**Local agents the project kept** (e.g. `planner`, a base `feature-developer`,
`test-runner`) carry their own `model:` frontmatter and are **not** touched by
the plugin update. On a model rollout, bump them to the new model ID:

```bash
grep -rn '^model:' .claude/agents/        # list local pins
# update each local agent's `model:` to the new model ID
```

This is the manual "model-pin step" the feature-developer banner references; an
upgrader agent automates exactly this rewrite. Leave a plugin agent's pin to the
plugin — do not hand-edit cached plugin files.

### 5. Update Provenance

Restamp `CLAUDE.md` `## Provenance`:

- `agentive-workflow@<old>` → `agentive-workflow@<new>`
- update the date and, on a model rollout, note the model the local agents now
  pin.

### 6. Verify

```bash
claude plugin list | grep -A3 -E 'agentive-workflow([@ (]|$)'   # new version, enabled
```

Optionally confirm the namespaced artifacts resolve at the new version with a
headless probe from the project directory:

```bash
claude -p --model haiku "List every subagent_type and command starting with 'agentive-workflow:'."
```

Then run the project's own gate if it has one (`./scripts/core/ci-check.sh`,
tests) to confirm nothing regressed.

### 7. Commit

Commit the `## Provenance` change plus any local-agent `model:` edits. Follow
the project's commit conventions (planning repos commit to `main`; code repos
use feature branches — see `docs/CROSS-REPO-PATTERN.md`).

## Rollback

Pin back to the previous version and re-update:

1. Set `agentive-workflow@<previous>` in `CLAUDE.md` Provenance.
2. `claude plugin update agentive-workflow@agentive-skills` resolves to the
   pinned version. The plugin cache retains prior version directories for ~7
   days, so an immediate rollback is local and fast.

## Gotchas

- **Marketplace must be GitHub-sourced**, not a local directory — a local
  `Directory (...)` source serves whatever is on disk, defeating version pins
  (see Prerequisites).
- **Same-version re-publish does not propagate** — the upstream `version` field
  must increase for consumers to receive changes.
- **Never hand-edit cached plugin files** (`~/.claude/plugins/cache/...`) — that
  path is ephemeral and is overwritten on the next update.
- **ANSI colour codes can defeat the greps** — the `claude` CLI currently
  strips colours when piped (verified 2026-07-06), but if a future version
  colours piped output, insert a strip stage before grepping:
  `claude plugin list | sed $'s/\x1b\\[[0-9;]*m//g' | grep ...`
  (bash ANSI-C quoting; works with BSD/macOS sed).
- **Plugin vs scripts vs identity** are three separate upgrade surfaces; this
  guide is only the plugin. Don't fold manifest-script or CLAUDE.md changes
  into a "plugin upgrade."

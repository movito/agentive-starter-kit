---
description: Interview the user and author their setup-door preset in the visible config home
version: 1.0.0
origin: agentive-starter-kit
last-updated: 2026-07-23
created-by: "@movito with feature-developer-f5 (KIT-0058)"
---

# Setup Preset

Author (or update) the operator preset for the setup door
(`scripts/local/bootstrap`) by interviewing the user in plain
language, one question at a time, then writing
`<kit-parent>/agentive-config/preset`.

## Binding rules — read before anything else

1. **Derive, never hardcode.** Your FIRST action is:

   ```bash
   ./scripts/local/bootstrap --help
   ```

   Build the entire interview from what that prints: the recognized
   preset keys, the shape × profile legality matrix, the offer flags,
   and the resolution-chain semantics. This command deliberately
   contains **no question list of its own** — if it named the door's
   keys, it would drift from the door (runtime-read, per ADR-0025).
   If this file and the door's help ever appear to disagree, the help
   output wins.

2. **Plain language, one question at a time.** Never dump the key
   list on the user. For each open question, explain what it decides
   and what each choice costs or unlocks in ordinary words — e.g. a
   "no bots" answer means the completion gates will honestly SKIP bot
   checks rather than fail, not that anything is broken. Offer an
   **expert shortcut** up front: a user who asks for "full-stack
   defaults" skips the interview — answer every question with the
   door's own default (and "yes" to its offers), and ask only the
   questions the help output shows have no default.

3. **Secrets never transit the chat.** If the user pastes anything
   that looks like key material (API keys, tokens, passwords),
   REFUSE it: tell them the preset records only a PATH. Direct them
   to create the secrets file themselves:

   ```bash
   touch <config-home>/env.source
   chmod 600 <config-home>/env.source
   # then edit it in their own editor, never in this chat
   ```

   Record only the resulting path under the door's secrets-by-
   reference key. The seeded `.gitignore` keeps that file out of git.

## Step 1: locate the config home

The config home is a visible sibling of the kit's primary clone:

```bash
git rev-parse --path-format=absolute --git-common-dir
```

Take the parent of the parent of that path, plus `/agentive-config`.
If `AGENTIVE_KIT_CONFIG_DIR` is set in the environment, it overrides
the location entirely (it is an override, never a search chain — do
not look anywhere else). If the folder does not exist, create it —
running this command IS the user engaging the preset flow. If a
preset already exists there, read it and treat the interview as an
update (show the current values; never silently overwrite an answer
the user did not revisit).

If the user has a file at the legacy `~/.config/agentive-kit/preset`
location, tell them it is no longer read anywhere and offer to move
it here as the starting point for the interview.

## Step 2: run the interview

Ask one question per turn, derived from the help output (rule 1),
consequences explained (rule 2), secrets by path only (rule 3).
Skip questions the help output marks as scoped to a mode or shape
the user's answers have already excluded.

## Step 3: write and finish loudly

1. Write the preset as flat `key: value` lines (the only format the
   door accepts — the help output describes it) to
   `<config-home>/preset`.
2. **Show the user the written file** in full.
3. **Validate every written key** against the door's accepted set:
   re-read the recognized-keys list from `--help` and confirm each
   key you wrote appears in it — an unknown key would only WARN at
   install time; catch it now, at authoring time. Fix and re-show if
   anything is off.
4. Offer the **private-repo step**: the door seeds a `.gitignore`
   (`env.source`, `*.env`) and a README into the config home on its
   first use, so the folder is safe to keep in a *private* git repo.
   If the user wants the repo now, before any door run, confirm the
   `.gitignore` exists first (create it with those same two lines if
   the door has not seeded yet — the door never overwrites it), then
   `git init` + create a **private** remote. `project doctor` checks
   this guardrail from now on (WARN on a public remote, FAIL on a
   tracked `env.source`).
5. State plainly that the first real `bootstrap --new <dir>` run is
   the end-to-end proof — the door announces the preset path it
   loaded, and `./scripts/core/project doctor --against-preset`
   compares any project's record against this preset at any time.

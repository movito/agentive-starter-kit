# Scripts

## Directory Layout

### `core/` — Shared scripts (synced from agentive-starter-kit)

These scripts are shared across all agentive projects. **Do not edit locally in
downstream repos** — changes are made here in agentive-starter-kit and synced
via automated PRs.

Current version: see `core/VERSION`

### `local/` — Project-specific scripts

Scripts unique to this project. Never synced or overwritten.

### `optional/` — Opt-in scripts

Scripts that downstream projects can copy to their `local/` directory if needed.
Not synced automatically.

## Sync Mechanism

When `scripts/core/` changes on `main`, a GitHub Action opens PRs in:
- movito/dispatch-kit
- movito/adversarial-workflow
- movito/adversarial-evaluator-library

Downstream repos can also check sync status manually:
```bash
./scripts/core/check-sync.sh
```

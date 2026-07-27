# Evaluator Library Workflow

Procedures for managing adversarial evaluators from the upstream library.

## Upstream Repository

- **Repo**: `movito/adversarial-evaluator-library`
- **Index**: `evaluators/index.json` (tracks version, categories, providers)

## Check for Updates

```bash
# See what's available in the library (pulls latest index)
adversarial library list

# Check if installed evaluators have newer versions upstream
adversarial library check-updates
```

## Install / Upgrade Evaluators

```bash
# Install a new evaluator
adversarial library install <provider>/<name> --yes

# Install multiple at once
adversarial library install google/arch-review-fast openai/arch-review --yes

# Get details about an evaluator before installing
adversarial library info <provider>/<name>
```

Installed evaluators land in `.adversarial/evaluators/<provider>/<name>/evaluator.yml` — one directory per evaluator, grouped by provider (`anthropic/`, `google/`, `mistral/`, `openai/`). There are no flat `*.yml` files at the `evaluators/` root; the whole tree is install-generated and gitignored.

## After Installing

1. Verify the evaluator appears: `adversarial list-evaluators`
2. Check API keys are configured in `.env` (e.g. `GEMINI_API_KEY`, `OPENAI_API_KEY`)
3. Smoke test: `adversarial evaluate --evaluator <name> <target-file>`

## Conflict Resolution

If you see "conflicts with existing; skipping" warnings, two definitions
claim the same evaluator name.

> ⚠️ **Do not `rm -rf` a provider directory.** This section previously
> advised deleting `.adversarial/evaluators/<provider>/<name>/`, which is
> exactly where the library installs — following it removed the installed
> evaluator rather than a stray copy (KIT-0069 / A40).

Diagnose before deleting anything:

```bash
# What is actually installed, and from which library version
adversarial list-evaluators
cat .adversarial/evaluators/.installed-version
```

The whole `.adversarial/evaluators/` tree is install-generated and
gitignored, so the safe recovery from any conflict is to reinstall from
the pinned library rather than hand-delete:

```bash
./scripts/core/project install-evaluators
```

The library-installed version is canonical.

## Contributing New Evaluators

1. Create a branch in `adversarial-evaluator-library`:

   ```bash
   cd <path-to-adversarial-evaluator-library>
   git checkout -b feature/<evaluator-name>
   ```

2. Add evaluator files under `evaluators/<provider>/<name>/`:
   - `evaluator.yml` — model, prompt, config
   - `README.md` — usage docs, cost estimates, comparison table
   - `CHANGELOG.md` — version history
3. Update `evaluators/index.json`:
   - Add evaluator entry to `evaluators` array
   - Add category if new (to `categories` object)
   - Add to provider's evaluator list (in `providers` object)
   - Bump version
4. Commit, push, create PR
5. After merge, install in your project: `adversarial library install <provider>/<name> --yes`

## Currently Installed Evaluators

Run `adversarial list-evaluators` for the current list.

Common evaluators:

| Evaluator | Provider | Category | Cost/Review |
|-----------|----------|----------|-------------|
| arch-review | OpenAI (o1) | arch-review | ~$0.10-0.30 |
| arch-review-fast | Google (Gemini 2.5 Flash) | arch-review | ~$0.003-0.01 |

See `adversarial list-evaluators` for the full, up-to-date list.

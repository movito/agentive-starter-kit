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

Installed evaluators land in `.adversarial/evaluators/` as flat YAML files (e.g. `google-arch-review-fast.yml`).

## After Installing

1. Verify the evaluator appears: `adversarial list-evaluators`
2. Check API keys are configured in `.env` (e.g. `GEMINI_API_KEY`, `OPENAI_API_KEY`)
3. Smoke test: `adversarial evaluate --evaluator <name> <target-file>`

## Conflict Resolution

If you see "conflicts with existing; skipping" warnings, it means there are duplicate evaluator definitions — typically a manually-created copy in a provider subdirectory (e.g. `.adversarial/evaluators/google/arch-review-fast/`) alongside the library-installed flat file. Remove the manual copy:

```bash
rm -rf .adversarial/evaluators/<provider>/<evaluator-name>
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

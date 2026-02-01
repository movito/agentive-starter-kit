# Custom Evaluators

Place evaluator YAML files here to add custom evaluation commands.

## Quick Start

1. Create a YAML file (e.g., `my-evaluator.yml`)
2. Define: name, model, api_key_env, prompt
3. Run: `adversarial my-evaluator <file>`

## Example

```yaml
name: my-evaluator
description: Custom document review
model: <provider>/<model-id>  # See aider docs for supported models
api_key_env: <PROVIDER>_API_KEY
timeout: 120
output_suffix: -my-evaluator.md
prompt: |
  Review this document for obvious issues...
```

**Common model formats**:
- OpenAI: `gpt-4o`, `gpt-4o-mini`
- Google: `gemini/gemini-2.0-flash`
- Mistral: `mistral/mistral-large-latest`
- Anthropic: `anthropic/claude-3-5-sonnet`

See [aider's LLM documentation](https://aider.chat/docs/llms.html) for full list.

## Evaluator Library

For pre-built evaluators (Gemini, Mistral, more OpenAI), run:

```bash
./scripts/project install-evaluators
```

See: https://github.com/movito/adversarial-evaluator-library

## API Keys

Each evaluator requires an API key. The environment variable name is specified in the evaluator's YAML file (`api_key_env` field).

Common provider conventions (per aider documentation):

| Provider | Environment Variable | Get Key |
|----------|---------------------|---------|
| OpenAI | `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| Google | `GOOGLE_API_KEY` | https://aistudio.google.com/apikey |
| Mistral | `MISTRAL_API_KEY` | https://console.mistral.ai/api-keys |
| Anthropic | `ANTHROPIC_API_KEY` | https://console.anthropic.com/settings/keys |

Example `.env`:
```bash
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
# Only set keys for providers you use
```

**Note**: Check each evaluator's YAML for the exact `api_key_env` value. The evaluator library may use provider-specific conventions.

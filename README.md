# Agentive Starter Kit

**A bit of structure to help you get more out of agentive software development**

Using agents to build software works better if you add a bit of structure — Anthropic calls this a [harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents). This kit packages the structure we use to overcome the usual problems of agentive development: documentation, testing, architecture, and value for money (and tokens). One command — `agentive new` — stamps out a configured project in about ten minutes, from wherever you are; then tweak anything — agents, models, workflow — as you wish.

**Starting a project?** Read **[docs/STARTING-A-PROJECT.md](docs/STARTING-A-PROJECT.md)** — the operator flow from idea (or prototype) to a planner-ready project.

---

## What's inside

- A **front door for new projects** — the packaged setup door (`agentive new` / `agentive adopt`, runs from anywhere) and the guided `/new-project` interview
- **Specialized agents** for planning, implementation, testing, and review (`.claude/agents/`)
- **Adversarial evaluators** — independent AI second opinions on plans, code, and docs
- **Task management** as markdown files in status folders (`.kit/tasks/README.md`), with optional Linear sync ([docs/LINEAR-INTEGRATION.md](docs/LINEAR-INTEGRATION.md))
- **Test-driven development** infrastructure — test templates, quality gates, pre-commit hooks
- **Architectural decision records** — a knowledgebase for agents and humans
- **Serena integration** (by Oraios) — semantic code navigation that cuts token consumption by 70–98%

---

## Requirements

| Tool | Version | Notes |
|------|---------|-------|
| **git** | **≥ 2.30** | Stock macOS (Apple Git 2.30.1) works. The kit's scripts used to require ≥ 2.31 via `git rev-parse --path-format=absolute`, which 2.30.1 echoes back instead of consuming — silently (operator preset ignored by the setup door) or hard (worktree helper died). KIT-0080 made every resolver portable, so the floor is now 2.30; `project doctor` WARNs below it. Note `xcode-select --install` does **not** raise Apple's git — its Command Line Tools ship 2.30.x by design; use `brew install git` (then `hash -r`) if you want a newer one. |
| **gh** | any recent | Authenticated: `gh auth status` must pass |
| **Python** | ≥ 3.10 | For code-project shapes (CI tests 3.10/3.12/3.14); planning-shape repos need only system `python3` |
| **Claude Code** | current | The kit is built around it |
| **uv** | recommended | Installs both CLIs every project uses (any isolated-CLI installer works) |
| **agentive-kit** | 0.3.x | The kit's lifecycle CLI (task moves, doctor, preflight, evaluator provisioning): `uv tool install agentive-kit`, upgrade with `uv tool upgrade agentive-kit`. New projects are born packaged (KIT-ADR-0028 phase 2) — they carry no script copies; the door verifies this install or prints the command. Inside this repo the scripts use the in-tree `packages/agentive-kit/` source automatically |
| **agentive-workflow plugin** | current | Agents, skills, and slash commands for created projects: `claude plugin marketplace add movito/agentive-skills`, then `claude plugin install agentive-workflow@agentive-skills` |

`agentive doctor` inside any packaged project tells you what's missing (projects created before the packaged era run `./scripts/core/project doctor` instead).

**Updating the toolchain** — install once, update forever; two commands per channel:

```bash
# The CLI (PyPI):
uv tool upgrade agentive-kit

# The agent plugin (marketplace):
claude plugin marketplace update agentive-skills
claude plugin update agentive-workflow@agentive-skills
```

The plugin update requires the full `name@marketplace` form — the bare
`agentive-workflow` errors (verified on the 2.0.0 upgrade, KIT-0096).
Check what you're running with `claude plugin list` and `agentive --version`.

**For contributors — the portability rule**: kit scripts must run on stock
macOS (BSD userland, bash 3.2, no Homebrew add-ons) *and* Linux CI. Do not
depend on Homebrew-provided tools like `timeout`/GNU coreutils — a check
that needs them passes on a contributor's upgraded machine and fails for
every stock-macOS user. If your machine has Homebrew git or coreutils,
**absence of local failure proves nothing** — that is exactly the trap
that shipped the git 2.31 dependency (KIT-0080) and the missing-CLI gap
(#103).

## Quickstart

You need Claude Code, git + gh (authenticated) — see [Requirements](#requirements) above; `agentive doctor` inside any packaged project tells you what's missing.

The direct route — no kit clone required:

```bash
uv tool install agentive-kit
agentive new ~/Github/my-project
```

The guided route — clone the kit and let it interview you:

```bash
cd ~/Github
git clone https://github.com/movito/agentive-starter-kit.git
cd agentive-starter-kit && claude
```

Then run `/new-project` in the session — **the one guided entry for every situation** (blank project, prototype graduation, adopting a repo). It interviews you in plain language and drives the same setup door; anything not yet installed (the `agentive` CLI, the agent plugin) comes back as a printed install command, never a dead end. When it finishes, open the tab its LAUNCH line names and start with the `planner` agent.

Full guide — the sibling layout, prototype graduation, adopting an existing repo, operator presets: [docs/STARTING-A-PROJECT.md](docs/STARTING-A-PROJECT.md). Authoritative option matrix: `agentive new --help`.

---

## Headline agents

| Agent | Purpose |
|-------|---------|
| `planner` | Helps you plan, tracks work, keeps things on track |
| `feature-developer` | Implementation tasks with gated workflow |
| `test-runner` | TDD and testing |
| `code-reviewer` | Reviews implementations for quality |
| `project-intake` | Graduate a prototype into the split pair (via `/new-project`) |

The full set lives in `.claude/agents/` — `ls .claude/agents/` is the authoritative inventory.

## Evaluation

Independent AI review of your plans, code, and documentation, via the `adversarial-workflow` package. Discover what's available with `adversarial list-evaluators`; install the evaluator library (and the CLI) with `agentive install-evaluators`. Guidance lives in the `code-review-evaluator` skill (`.claude/skills/code-review-evaluator/SKILL.md`).

---

## Pointers

| You want | Where |
|----------|-------|
| Starting a project (all paths) | [docs/STARTING-A-PROJECT.md](docs/STARTING-A-PROJECT.md) |
| Setup-door options (shapes × profiles, adopt, `--bots`) | `agentive new --help` / `agentive adopt --help` |
| Operator preset (answer the door's questions once) | `/setup-preset` + [docs/STARTING-A-PROJECT.md](docs/STARTING-A-PROJECT.md) |
| The split-pair pattern | [docs/CROSS-REPO-PATTERN.md](docs/CROSS-REPO-PATTERN.md) |
| Linear task sync | [docs/LINEAR-INTEGRATION.md](docs/LINEAR-INTEGRATION.md) |
| Keeping a project updated | [docs/UPDATING-YOUR-PROJECT.md](docs/UPDATING-YOUR-PROJECT.md) |
| Task system and status folders | `.kit/tasks/README.md` |
| Evaluation guidance | `.claude/skills/code-review-evaluator/SKILL.md` |
| Agent template | `.kit/templates/AGENT-TEMPLATE.md` |
| Starter-kit ADRs / your project's ADRs | `.kit/adr/` · `docs/adr/` |

---

## Philosophy

- **Progressive refinement over perfectionism** — start simple, iterate on real feedback, ship with known limitations
- **Test-driven development** — tests before implementation, 80%+ coverage for new code, hooks catch issues early
- **Multi-model collaboration** — Claude implements, evaluators critique independently, the planner orchestrates
- **Documentation is infrastructure** — handoffs and ADRs prevent context loss and enable coordination

---

## Contributing

This starter kit is extracted from real development practices. Contributions welcome:

1. Found a better pattern? Document what and why
2. Tried this approach? Share your results
3. Adapted for your domain? Share variations

## License

MIT. Developed through real-world use on production projects — special thanks to the Claude team and all AI provider teams for making agentive development possible.

**Version**: see `version` in `pyproject.toml`

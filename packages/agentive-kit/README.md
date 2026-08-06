# agentive-kit

Project lifecycle CLI for [agentive projects](https://github.com/movito/agentive-starter-kit):
task status flow (`start`/`move`/`complete`), environment doctor,
evaluator provisioning, preflight and review helpers.

**Pre-consumer-migration release.** This package is KIT-ADR-0028
phase 1: it replaces the copy-distributed `scripts/core/` layer of the
agentive-starter-kit. Existing projects keep working through their
`./scripts/core/project` shim until phase 3 migrates them.

## Install

```bash
uv tool install agentive-kit
```

## Use

Run from anywhere inside a kit-made repository — the CLI walks up from
the current directory to find the project root (a directory with both
`.kit/` and `CLAUDE.md`) and refuses loudly anywhere else:

```bash
agentive start KIT-0001      # move a task to in-progress
agentive move KIT-0001 done  # move a task to any status
agentive validate            # check task Status fields match folders
agentive version
```

The remaining subcommands (`doctor`, `install-evaluators`, …) migrate
into this CLI over the phase-1 PR series.

# KIT-0096: Plugin release refresh (agentive-workflow 2.0.0) — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-08-09
**From**: planner-f5
**To**: feature-developer
**Task**: `.kit/tasks/3-in-progress/KIT-0096-plugin-release-refresh.md`
**Status**: Ready — blocks the operator's new-project test; top of queue
**Evaluation**: arch-review-fast, 2 rounds, closed under the Oscillation
protocol with all findings dispositioned — the record is IN the spec
(§Evaluation record); read it, don't re-litigate the declined finding.

**Target Codebase**: TWO repos this time — read this section twice.

## Session topology (read before anything else)

This task spans two repositories:

- **Kit side** (drift guard + roster source): worktree
  `~/Github/ask-worktrees/KIT-0096`, branch
  `feature/KIT-0096-plugin-release-refresh` — created and provisioned
  by the planner. VERIFY, never create: `git branch --show-current`
  must show that branch before your first kit-side edit.
- **Marketplace side** (the content release): `movito/agentive-skills`
  — NOT cloned on this machine. Clone it yourself to
  `~/Github/agentive-skills` (plain clone, work on a branch, open a PR
  there — no bots are configured on that repo, so the operator's
  review IS the gate; say so in the PR body). Never push directly to
  its default branch.
- Two PRs, one per repo; the kit PR carries the drift guard + roster
  file source-of-truth decisions, the marketplace PR carries the
  content. State in each PR body which must merge first (likely
  marketplace first, then the kit guard goes green against it).

## Mission

Bring the plugin channel current: `agentive-workflow` 2.0.0 with the
kit's present agents/skills/commands (generalized per ADR-0025), a
deliberate roster, an automated drift guard, and end-to-end
verification. Spec F1–F5 authoritative.

## Verified anchors (2026-08-09 — re-check before relying)

- **Marketplace today**: 25 files; `plugins/agentive-workflow/` with
  agents = ci-checker, code-reviewer, feature-developer-v6, -v7 (NO
  planner); 13 commands; 5 skills; `plugin.json` version 1.1.0 whose
  `description` enumerates components — that list must be rewritten
  with the new roster (easy to forget; it references v6/v7 by name).
  Last content push 2026-06-18.
- **Kit canonical**: 14 agents, 14 commands, 5 skills in `.claude/`.
  Note `create-project.md` no longer exists (deleted by KIT-0093 —
  do not resurrect it from the June marketplace state).
- **The Phase 1 contract sentinel** for F5's fresh-project grep:
  `VERIFY the worktree/branch, never create it` — the exact string
  `tests/test_agent_contracts.py` pins in the kit. A fresh project's
  plugin-provided feature-developer must carry it post-release.
- **Installed-plugin state on this machine**: 1.1.0, enabled — your
  F5 verification runs `claude plugin marketplace update
  agentive-skills` + `claude plugin update agentive-workflow` and
  re-checks `claude plugin list` shows 2.0.0.

## Generalization guidance (F1 — the judgment half)

Per ADR-0025 (+ KIT-0093 F1): plugin bodies are project-agnostic and
read project specifics from repo-owned files at runtime.

- KIT-LOCAL marker regions do NOT ship. Replace each placeholder
  region with a short instruction: read project context from CLAUDE.md
  and `.kit/context/` at session start (the region's content, per
  project, lives there in the packaged world).
- Kit-repo-specific text (ASK paths, kit footgun entries naming kit
  incidents' file paths, `movito/agentive-starter-kit` references in
  procedural text) is generalized or dropped — but behavioral
  contracts (verify-never-create, Session topology requirement,
  oscillation protocol references, ordering rules) ship INTACT; they
  are the point of the refresh.
- Record every judgment call per file in the marketplace PR body (one
  line each). Where genuinely unsure, keep the text and flag it — the
  operator review gate decides.

## Roster (F2 — decide, record, make machine-readable)

Candidates from the kit's 14: feature-developer, feature-developer-f5,
planner, planner-f5, ci-checker, code-reviewer, test-runner definitely
in contention; project-intake and upgrader are judgment calls (intake
runs FROM a kit checkout by its own header — probably kit-side;
upgrader is consumer-facing by design — probably ships); bootstrap /
agent-creator / powertest-runner / document-reviewer /
security-reviewer: decide each with a one-line why. v6/v7 retire.
The roster file (fields documented in its own header comment) lives in
the marketplace repo and is F4's comparison input.

## F4 — the drift guard (kit-side, CI, automated)

A kit CI check that fails when kit `.claude/` content is newer than
the last published plugin release — compare via the roster file's
source paths using agent `version:` frontmatter and/or content hashes.
Design constraint: the guard must not require network at pre-commit
time (CI-only is fine); it must be falsified once in a controlled
scenario (kit newer → FAIL) per the spec's AC. Portable — no
Homebrew-only tools (README rule).

## Test approach

- Full suite on the kit side per push (the guard is new CI surface).
- Marketplace side has no test suite — your gates there are: plugin
  loads (`claude plugin` accepts it), namespaced components resolve,
  and the F5 end-to-end (fresh `--new` project → plugin agents carry
  the sentinel, verified by grep, output pasted in the PR).
- Evaluator trio before each PR opens (format: this is mostly
  strings/docs — use `--format diff` per the new skill guidance);
  disposition tables; deep rounds ≤2.

## Out of scope — do not touch

- Agent behavior changes (the kit's `.claude/` stays canonical and
  UNTOUCHED except the drift-guard test file)
- Phase 3 consumer migration; the door; sync machinery
- KIT-0075's launcher build (but your F5 test project is its evidence
  gatherer — note the native-invocation experience in completion)

---

**Task File**: `.kit/tasks/3-in-progress/KIT-0096-plugin-release-refresh.md`
**Evaluation record**: in the spec (§Evaluation record); log at
`.adversarial/logs/KIT-0096-plugin-release-refresh--arch-review-fast.md`
**ADRs**: KIT-ADR-0025 (generalization discipline), KIT-ADR-0028 (the plugin is THE agent channel)

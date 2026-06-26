# KIT-0032 — Upgrader Agent No-Op Dry-Run Proof

**Date**: 2026-06-26
**Agent**: `.claude/agents/upgrader.md`
**Repo under test**: agentive-starter-kit (this repo) — already at the current pin.

This is acceptance criterion #8: the cheapest end-to-end proof available without
a real version bump. Traced the agent's deterministic phases against live state.

## Observed live state

| Check | Command | Result |
|---|---|---|
| Phase 0a — marketplace source | `claude plugin marketplace list` | `agentive-skills` → `GitHub (movito/agentive-skills)` ✓ pass |
| Phase 0b — already-consuming | `claude plugin list \| grep agentive-workflow@agentive-skills` | Version 1.1.0, **enabled** ✓ pass |
| Phase 1 — current pin | `claude plugin list` | `1.1.0` (authoritative) |
| Phase 1 — Provenance | `grep -c '## Provenance' CLAUDE.md` | `0` — **absent** (this repo is the plugin's *source*, not a typical consumer) |
| Phase 1 — target pin | `gh api .../plugin.json` | `1.1.0` (latest published) |

## Agent decision trace

1. **Phase 0a** — source is GitHub, not `Directory (...)` → guard passes, no refusal.
2. **Phase 0b** — `agentive-workflow@agentive-skills` present & enabled → project
   consumes the plugin → no initial-migration refusal.
3. **Phase 1** — current `1.1.0` == target `1.1.0` ⇒ **idempotence check fires**:
   print "nothing to do" and **STOP**. No PREVIEW, no ACK, no APPLY.
   - The missing `## Provenance` section is surfaced as a one-line note; the
     agent relies on `claude plugin list` for the current version and does **not**
     fabricate a Provenance section (that would be a CLAUDE.md identity edit).

## Outcome

- **Zero project-file edits, zero git mutations, zero `claude plugin update`.**
- Confirms: idempotence (current == target ⇒ no-op), no mutation before ACK
  (we never even reach the ACK gate), and the marketplace/consuming guards pass
  cleanly on a healthy consumer.

This is the no-op leg. The mutate leg (version delta → PREVIEW → ACK → APPLY)
cannot be exercised here without a real upstream version bump; the agent body
maps it 1:1 to guide steps 2–7 + rollback.

# KIT-0102 — F1 enumeration table + F2 both-directions check

Working artifact produced during Phase 2 (pre-implementation), before
any deletion. The spec's inventory was the starting hypothesis; three
rows came back different once functions were actually enumerated.

## F2 — both-directions drift check (the KIT-0096 lesson)

**Result: CLEAN — zero backward drift. Canon needed no fix.**

Method: the manifest names `source_repo: movito/agentive-starter-kit`
and this tree's `origin` is exactly that — so this repo IS canon. Rather
than stop at that architectural argument, every manifest-managed file
was diffed against the one live manifest-carrying consumer found on
disk.

- Consumers scanned: 7 sibling checkouts; exactly one carries
  `scripts/.core-manifest.json` → `varv-planning` (`core_version=2.1.0`
  vs canon `4.0.0`).
- Files compared: 47 manifest entries (dir entries expanded) →
  11 identical, 36 differing, 5 only-in-consumer, 38 absent-in-consumer.
- Direction, by `version:` metadata: **0 consumer-newer**, 11
  consumer-older (canon ahead, as expected).
- The 3 same-version-but-differing files were inspected by hand —
  all three are canon-newer in content:
  - `core/check-bots.sh`, `core/wait-for-bots.sh` — consumer holds
    pre-restructure `./scripts/…` usage strings; canon has
    `./scripts/core/…`.
  - `.kit/context/patterns.yml` — canon carries ~145 lines of
    additional patterns the consumer predates.
- The 5 only-in-consumer files (`check-sync.sh`, `verify-setup.sh`,
  `gh-review-helper.sh`, `preflight-check.sh`,
  `prepare-review-input.sh`) are scripts already retired upstream; a
  v2.1.0 consumer that never pulled the retirements still holds them.
  Not drift — expected lag.

Conclusion: no copy is newer than its kit source, so nothing in canon
regressed and the manifest can be deleted without a preceding fix.

## F1 — enumeration table

| Artifact | Functions enumerated | Where each went | Grep proving no live caller | Verdict |
|---|---|---|---|---|
| `.github/workflows/sync-core-scripts.yml` | push-channel Action: checkout source, run engine, open PR in 3 consumer repos | obsolete — push trigger disabled, `CROSS_REPO_TOKEN` never provisioned (KIT-0045) | only live refs are the workflow itself + the doctor check that guards it + docs | **delete** |
| `scripts/core/sync_from_manifest.py` | pull engine: manifest read/validate, tier+allowlist selection, copy/prune, `core_version` bump, exit-code contract | obsolete — consumers born packaged (phase 2); only live consumer is packaged-shape (phase 3 no-op) | imported only by `project` `cmd_sync`, its own tests, `test_project_sync.py`, and the deleted workflow | **delete** |
| `scripts/.core-manifest.json` | the file inventory + `core_version` for the copy channel | obsolete with its engine | read by `project` sync helpers, both sync test files, `engine-consumer.sh` heredocs, `test_bootstrap_shapes.py` | **delete** |
| `tests/test_sync_from_manifest.py` | tests the pull engine | dies with subject (KIT-0092 Part C) | — | **delete** |
| `tests/test_core_manifest.py` | tests manifest structure + the engine-consumer heredoc/VERSION parity guard | dies with subject; **parity guard re-homed** (see note) | — | **delete (with re-home)** |
| `tests/test_project_sync.py` | 709 lines testing `project sync` end-to-end — **not named in the spec inventory** | dies with `cmd_sync` | — | **delete (spec addition)** |
| `scripts/core/doctor.d/60-push-sync-token.sh` | one check: is `CROSS_REPO_TOKEN` present while the push trigger is active | obsolete — guards a deleted workflow | `tests/test_doctor.py::TestPushSyncTokenCheck` (1043–1140) only | **delete (both homes)** |
| `packages/…/doctor/checks/60-push-sync-token.sh` | mirror of the above in the package | same | roster mirrors in-tree `doctor.d/` | **delete (mirror)** |
| `project sync` subcommand | shim wrapper: shape gate, source resolve, dirty-path guard, branch+commit, report printing | obsolete with engine | dispatch at `main()`; help text | **delete region** |
| `scripts/core/doctor.d/40-version-skew.py` | **TWO functions, neither manifest-related**: (1) `venv-skew-adversarial` — venv vs system `adversarial-workflow` (KIT-0044 mutation incident); (2) `black-pin` — active black vs pyproject pin (KIT-0032 phantom-CI incident) | **PRESERVED** — spec's "manifest-skew" guess was wrong; the name misleads | heavily tested: `test_doctor.py` 523, 719–890 | **KEEP — spec corrected** |
| `scripts/core/VERSION` | (1) manifest's `core_version` source; (2) **`project version` output** (`project:2411`) | function (1) dies; function (2) is live and independently tested | `tests/test_project_script.py:1116` pins `project version` == VERSION | **KEEP — spec corrected** |

### Notes on the two spec corrections

Both come straight from the KIT-0067 law — enumerate functions, never
reason from a name or a directory:

1. **`40-version-skew.py`** reads as manifest machinery from its
   filename. It is not: it checks Python toolchain skew and has zero
   manifest involvement. Deleting it would have removed two live
   incident guards.
2. **`scripts/core/VERSION`** has a second reader (`project version`)
   with its own test pin. It survives the manifest that also read it.

### The two guards inside `test_core_manifest.py` — resolved

Both needed a decision before the file could be deleted. Neither was
re-homed in the end, and both for evidenced reasons:

1. **`test_library_pin_mirrors_agree`** (referenced by
   `.adversarial/config.yml:56`) — **already deleted** in KIT-0079 via
   KIT-0090 PR 3; line 233 of the file was its tombstone. The config
   comment was pointing at a test that had not existed for two tasks.
   No coverage to preserve; the comment was rewritten into an explicit
   ⚠️ UNGUARDED note naming the manual invariant (the pins agree at
   `v0.10.0`; moving the reader is KIT-0079's scope).
2. **`TestBakedManifestVersion`** (KIT-0056/KIT-0061 — the baked
   `core_version` in `engine-consumer.sh` must match
   `scripts/core/VERSION`) — its **seam was removed by this task**.
   Deleting both manifest heredocs took out every `core_version` in the
   engine (lines 424 and 549 were the only two), so the desync it
   guarded against is now structurally impossible rather than merely
   untested. Operator confirmed letting it die after this interaction
   was surfaced.

**Preserved instead**: the door's ship-list contract, inverted. The
manifest and engine moved from `PLANNING_MUST_SHIP` to
`PLANNING_MUST_NOT_SHIP` (the KIT-0092 "absence is the contract"
precedent), plus a new re-bootstrap sweep test — so a future edit
cannot quietly reintroduce the copy-era seed.

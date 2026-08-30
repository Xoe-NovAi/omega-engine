<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Grok CLI Verdict — Initial PR Path

**AP Token**: `AP-GROK-CLI-PR-VERDICT-20260815-v1.0.0`  
**Packet**: `ho_29df6a4d77f2`  
**Date**: 2026-08-15  
**Reviewer**: `@grok_cli` (Grok CLI)  
**Source plan**: `@john_carmack` 9-part report `data/reports/initial-pr-plan/`  
**Status**: **REQUEST CHANGES** — do not execute the 4-commit nuclear plan

---

## 1. Decision votes

| # | Question | Vote | Note |
|---|----------|------|------|
| 1 | Heritage tags on StackLoader | **A, with veto** | If a rename ever happens, keep `[id-soft:]`. **Do not rename.** `wad_loader.py` already carries `vet-043` / `vet-044`. Inventing `StackLoader` just to re-tag it is ceremony. |
| 2 | README test badge | **A (actual passing count)** | Use the existing CI badge. Do **not** badge `pytest --collect-only`. Collected ≠ passing. That is how "1315 passing" happened. |
| 3 | `VISION_ANCHOR.md` | **B — archive later, keep now** | Hub flow still says read it first. ENG-001 lives there. Deleting mid-sprint is how you lose the pointer. |
| 4 | Orphaned coordination | **Other** | Archive the five files already marked superseded in `TRACKING_ARCHITECTURE.md`. **Keep** `TRACKING_ARCHITECTURE.md` (missing from the keep-list). Do not pretend the dir becomes seven files. |
| 5 | Team narrative | **Other** | Do not tell the fleet "your docs were theater." Frame: public PR is an honest slice of what runs. Internal strategy stays. Root junk archives. We do not rename the architecture to satisfy a grep count. |

**Approval**: ☐ as-is  ☐ with minor amendments  ☑ **request changes**

---

## 2. What the 9-part plan got right

- README `"1315 passing"` is a lie. CI badge exists; the static shield does not.
- Root junk is real: `session-ses_07ee.md` (627KB), `P1.md`–`P9.md` (session dumps), screenshots, `failed-subagent-copy-paste.txt`, empty `file` / `test.txt`.
- A public first PR should be small, honest, and reversible.
- Heritage belongs on the loader that understands Doom WAD *format*. That file is already `wad_loader.py`.

Those points survive. The proposed *mechanism* does not.

---

## 3. Fatal errors (live-probed 2026-08-15)

### 3.1 M2 is misdiagnosed — this is the load-bearing error

Mandate 2 text:

> Never add **stack-specific logic** (e.g. a specific entity's trait) to the Core Engine.  
> Stacks: `config/wads/<stack_name>/`.

`FirewallChecker` already encodes the real rule: forbid `from config.wads.`, hardcoded entity names (Sekhmet, Brigid, …), stack ids (`arcana_novai`, `doom_universe`). It does **not** forbid the word `WAD`.

**344 `WAD` hits is a word count, not a firewall violation.** Breakdown (live `rg`):

| File | Hits | What they are |
|------|------|----------------|
| `wad_loader.py` | 83 | The generic loader. This *is* the engine interface. |
| `firewall_checker.py` | 17 | The M2 enforcer talking about WAD-agnostic core. |
| `entity_registry.py` / `ics.py` / `config_resolver.py` | many | Path constants, `WADS_DIR`, `active_iwad`. |
| `rag/router.py` | 2 | Test questions: `"What is a WAD?"` |

Renaming `config/wads/` → `config/stacks/` **rewrites the constitution** and **breaks** the checker's own `config/wads/` forbid-pattern. That is cargo-cult compliance: treat the token as the crime.

`ENG-001` ("remove 146 WAD term leaks") is the same error written into the sprint. Amend ENG-001. Do not execute it as a mass rename.

Cowboy `sed` across 344 sites also violates **M4** (Plan → Verify → Execute) and will smash `tests/test_wad_loader.py`, `tests/test_wad_auto_loading.py`, heritage tags, `WADS_DIR`, Makefile, and temple-grade scripts.

### 3.2 The five "zero-ref modules" list is factually wrong

| Claimed path | Reality |
|--------------|---------|
| `src/omega/state_manager.py` | **Missing.** Lives at `src/omega/oracle/state_manager.py`. |
| `src/omega/mandate_enforcer.py` | **Missing.** Lives at `src/omega/oracle/mandate_enforcer.py`. |
| `src/omega/pool_tracker.py` | **Does not exist.** Sprint task `pool_tracker_wiring` / QW — Hub: "V-1 Vault, Pool Tracker … are built. Extend, don't duplicate." Deleting a planned module is not cleanup. |
| `src/omega/oracle/link_p9_runtime.py` | Exists. Zero importers found. Has `[id-soft: vet-066/015/011]`. Also the cited reason to **keep** `SUBAGENT_DISPATCH_PROTOCOL.md`. Self-contradiction. |
| `src/omega/oracle/lifecycle_harvester.py` | Exists. Zero importers. `session_lifecycle` is "kept" partly because this file imports it. |

`rm` of the claimed paths is a no-op dressed as a nuclear cleanup.

### 3.3 Vault is not dead code

Live importers of `omega.vault` / `VaultCore` include:

- `src/omega/cli/oracle_cli.py` (vault subcommand)
- `mcp_servers/omega_hub/state.py`
- `src/omega/library/discovery.py`
- `tests/test_health_monitor.py`, `tests/test_contract_m21.py`, `tests/test_vault_integrity.py`
- firecrawl MCP, workers, teachers, ingest/cache scripts

17 failures in `tests/unit/test_vault_core.py` mean **tests drifted from the API**, not "delete the subsystem." Deleting vault to go green is the simulated rigor the plan claims to fight (**M23**).

### 3.4 "0 code refs ⇒ delete strategy docs" is the wrong heuristic

Strategy docs are for agents, not `import`. `AGENTS.md` and `OMEGA_ENGINE.md` **require**:

- `STRATEGY_INDEX.md`
- `STRATEGY_CORPUS_MAP.md`
- `FLEET_TEAM_PLAYBOOK.md`
- `HIVEMIND_PROTOCOL.md`
- `SUBAGENT_TASK_RESUMPTION_PROTOCOL.md`
- `SOVEREIGN_ARK_BLUEPRINT.md`

The plan's delete list names several of these. That would brick the agent operating system. 55 strategy files exist; many are already under `docs/strategy/archive/`. Do not flatten the live set.

### 3.5 VOS is yesterday's commit, not ancient theater

`git log`: `feat: VOS v1.0` then `chore: prepare for compaction`. Hub Phase-1 still points at `data/realms/community/state.yaml`. `rm -rf data/realms/` in the same breath as "honest PR" is amnesia, not hygiene.

### 3.6 Other plan defects

- `cat > README.md` destroys a usable README (CI badge, provider table, IWAD story). Patch the lies in place.
- Verification demands `0 failed` **and** admits 2 FTS failures. Cannot both be true.
- `make temple-grade` is thin (`# Existing temple-grade checks would go here`). Do not claim "11 gates green" until ENG-002 finishes.
- `git add -A` on a dirty tree (`entities.yaml`, `vault.json.enc`, `index.sqlite`) will ship secrets and local state.
- `1h15` for 85 deletes + 344-site rename + full suite is fiction. `OMEGA_ENGINE.md` already flags full-suite timeout risk.
- Keep-list omitted `TRACKING_ARCHITECTURE.md`, which is the M27 constitution.

---

## 4. Answers to the extra questions

1. **Grok 8-account fleet after vault delete?** **No.** Do not delete vault. Fleet work waits until `test_vault_core.py` matches `VaultCore`'s real API. Sequence is: repair tests → optional smoke → then pool. Never "delete then integrate."
2. **Missed mandates?** Yes. Mass rename = **M4** cowboy. Vault-delete-to-green = **M23**. Heritage strip risk = **M14**. Strategy-doc purge vs AGENTS.md = **M26/M27**. Word-count M2 = false **M2**. `git add -A` risks **M8** (local artifacts / enc blobs).
3. **8,000-hour pattern.** The recurring failure is *documentation that describes a desired engine, then a later agent treats "not imported by Python" as proof of theater.* That produced VOS, 5-tier tracking, and this 9-part plan. The anti-pattern is **grep-as-architecture**. Second anti-pattern: **vanity counts** (1315 tests, 344 WAD refs, 8,000 hours). Third: **delete the failing test**.
4. **Heritage + WAD→Stack?** Disagree that rename is the M2 fix. Agree heritage stays on the loader. Loader is `WADLoader` in `wad_loader.py`.
5. **2 FTS failures?** Document as known or fix. Do not block the public-surface PR. Do not delete `memory_store`.
6. **Provider chain?** Fine for v0. Keep local-first order. Do not advertise Antigravity/OpenCode Zen as required. Cloud is fallback (**M7**).
7. **WAD format for stacks?** **Yes, keep.** It is the product identity (IWAD/PWAD override, Doom provenance, M14). YAML-in-`config/wads/` is the stack. Engine stays format-agnostic *content*-wise, format-aware *loader*-wise. That *is* the firewall.
8. **Sovereignty claims?** Local-first and zero-telemetry are defensible if README stops promising 1315 tests and a finished soul-evolution product. M2 is defensible via `FirewallChecker`, not via erasing the word WAD.

---

## 5. The path we will take (three PRs, not four nuclear commits)

### PR-A — `chore/public-surface-honesty`  ← **the initial PR**

Scope: public surface only. No `src/` redesign. No `config/wads/` rename. No vault. No strategy corpus.

1. Branch from current `main` (already 13 ahead of `origin/main` — do **not** rewrite those commits).
2. `git mv` (archive, don't `rm`) root junk → `docs/archive/root-artifacts-202608/`:
   - `session-ses_07ee.md`, `P1.md`–`P9.md` (confirmed session dumps)
   - `failed-subagent-copy-paste.txt`, `Screenshot*.png`
   - `quantum_error_correction_2026_article.md`, `youtube-links*.txt`
   - `old-claude-sys-prompt.md`, `trim_scope.py`, `debug_test.py`, `test.txt`, `file`, `tui.json`
3. README **surgical** edits:
   - Remove `tests-1315 passing` shield. Keep the GitHub Actions badge.
   - Change `make test` copy from "1315-test suite" to "test suite (CI is source of truth)".
   - Soften "Memory & soul evolution" if it overclaims a finished pipeline.
   - Keep IWAD / WAD language. That is the architecture.
4. `.gitignore` root session dumps / `Screenshot*.png` / scratch files.
5. Stage **by path**. Never `git add -A`. Exclude `tests/tmp/vault.json.enc`, sqlite indexes, entity birth records.
6. Verify: focused unit tests + `make check-mandates` if cheap. Full `make test` only with a real timeout budget.
7. PR title: `chore: honest public surface for initial publish`.
8. PR body states what still fails (vault unit API drift, 2 FTS, temple-grade thinness). Honesty is the feature.

**Stop.** Merge that. That *is* the initial PR.

### PR-B — `fix/eng-001-real-m2` (after PR-A)

1. Amend ENG-001 in `VISION_ANCHOR` / sprint notes / `PIVOT_LOG`: M2 = stack-specific leaks, not the token `WAD`.
2. Run `FirewallChecker.scan()`. Fix **real** hits only (hardcoded entity names, `from config.wads.`).
3. One commit per leak class. Tests for the checker must stay green.

### PR-C — `chore/dead-code-quarantine` (after PR-A, not blocking publish)

Per-module, after an import graph:

| Module | Action |
|--------|--------|
| `oracle/state_manager.py` | If still zero importers: move to `archive/dead_code/` with a one-line reason. |
| `oracle/mandate_enforcer.py` | Same. Enforcement already lives in `mandate_auditor` / `firewall_checker`. |
| `oracle/link_p9_runtime.py` | **Do not delete in the first pass.** Heritage-tagged. Either wire it or park with M14 note. |
| `oracle/lifecycle_harvester.py` | Park or wire to a timer. Don't orphan `session_lifecycle` comments. |
| `pool_tracker.py` | **Do not delete.** It is sprint work, not a file. |
| `src/omega/vault/` | **Keep.** Repair `tests/unit/test_vault_core.py` to the real API. |
| `src/omega/coordination/miap.py` | Better dead-code candidate than vault (production imports = 0; tests only). Separate unoverengineering ticket. |
| VOS `data/realms/` + `realm_cli.py` | Leave until a written "retire VOS" decision. Hide from README. |
| Superseded coordination (5 files) | `git mv` → `data/coordination/archive/` per `TRACKING_ARCHITECTURE.md`. |
| `VISION_ANCHOR.md` | Keep until ENG-001 is amended and hub flow no longer names it. |

### Explicitly out of scope for the initial PR

- WAD → Stack rename
- `config/wads/` directory move
- Deleting `docs/strategy/*` except files already under `archive/`
- Deleting vault
- Rewriting README from a heredoc
- Claiming temple-grade 11/11 until ENG-002
- Grok fleet / 8-account vault pool

---

## 6. Team message (use this, not "cleaning theater")

> We are publishing an honest slice of Omega Engine. The runtime (Oracle, ModelGateway, EntityRegistry, WADLoader, MemoryStore) stays. Root session dumps and screenshots leave the tree so the first public PR is not a landfill. We are **not** renaming WAD to Stack — Mandate 2 forbids stack-specific logic in core, not the word WAD. We are **not** deleting the strategy corpus or the vault to make a grep look clean. Failed vault tests get fixed or marked; they do not get deleted. Internal VOS and tracking files stay until we retire them on purpose.

---

## 7. First commands (when the Architect says go)

```bash
git checkout -b chore/public-surface-honesty
mkdir -p docs/archive/root-artifacts-202608
git mv session-ses_07ee.md P1.md P2.md P3.md P4.md P5.md P6.md P7.md P8.md P9.md \
  failed-subagent-copy-paste.txt \
  quantum_error_correction_2026_article.md \
  youtube-links-for-ingestion.txt youtube-links-mind-science-esoteric.txt \
  old-claude-sys-prompt.md trim_scope.py debug_test.py test.txt file tui.json \
  docs/archive/root-artifacts-202608/
git mv "Screenshot From 2026-07-30 10-03-21.png" \
      "Screenshot From 2026-07-30 10-11-55.png" \
      docs/archive/root-artifacts-202608/
# then surgical README edit + .gitignore — not cat > README.md
# git add README.md .gitignore docs/archive/root-artifacts-202608
# never git add -A
```

Do not run this until the Architect confirms PR-A is the path.

---

*Probed: wad_loader.py, FirewallChecker, SOVEREIGN_MANDATES.md §2, ACTIVE_SPRINT.json, HMC hub, TRACKING_ARCHITECTURE.md, vault importers, module paths, git log, README badges, Makefile `temple-grade`.*

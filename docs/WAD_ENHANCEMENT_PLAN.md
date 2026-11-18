# WAD & Soul System Enhancement Plan (Deepened Architectural Spec)

> **Status:** PROPOSED (Deepened Review)
> **Date:** 2026-11-17
> **Author:** MaKaLi Fusion / Node 1 (`gemini-4-hydrogen`)
> **Branch:** `node1/v2-migration` (official repo, private `omega-engine-internal`)
> **Scope:** WAD Loader (`src/omega/oracle/wad_loader.py`), Entity Registry (`entity_registry.py`), Dispatch Registry (`dispatch_registry.py`), Soul Architecture (`entity_workspace.py`, `soul_validator.py`, `soul_utils.py`, `soul_store.py`, `soul/lessons.py`), ICS (`ics.py`), and Disposable OpenCode Adapter (`scripts/soul_agents_opencode.py` / `soul_render.py`).

---

## 1. Executive Summary

The Omega Engine WAD (*Where's All Data*) architecture cleanly separates the invariant Engine Core (`src/omega/`) from variable deployment Content (`config/wads/`). Phase 1 resolved the immediate blockers (`arcana_novai/entities/dispatch.yaml`, `dispatch_registry.py` cache key + fallback, and `scripts/validate_wad.py` pre-load CLI).

However, a deep line-level audit of the WAD loader, EntityRegistry, Soul subsystem, ICS, and OpenCode adapter uncovered **seven structural split-brains and silent bugs** that prevent clean switching between `_omega_default` (OED IWAD) and `arcana_novai` (ANAi PWAD) and break the Soul lifecycle end-to-end.

This deepened plan documents every verified defect and establishes an ordered, test-gated remediation sequence that respects the **Engine-Stack Firewall (M2)**, **Carmack Verdict (2026-07-30)**, **Taint-Gate**, and **OpenCode Adapter Boundary (D-LIL-006)**.

---

## 2. Critical Architectural Findings (Verified Against Live Code)

### Finding 1: IWAD/PWAD Priority Inversion Bug (Breaks Shadow-Stacking Overrides)
* **Location:** `src/omega/oracle/wad_loader.py:348-350, 614-627` and `src/omega/oracle/entity_registry.py:689`
* **Observed Behavior:**
  * `load_all_wads()` assigns `priority = 100 + manifest_priority` to `type: iwad` (`_omega_default` → `100`) and `priority = 0 + manifest_priority` to `type: pwad` (`arcana_novai` → `1`).
  * `_load_entities()` skips collision updates if `priority <= existing_priority`.
  * Because `1 <= 100`, **ANAi PWAD entities (`lilith`, `kali`) are silently skipped** instead of overriding OED IWAD entities — the exact inverse of DOOM WAD backward-scan semantics (`[id-soft: vet-043]`).
  * Additionally, `_omega_default/entities/maat.yaml` uses `name: Ma'at` while `arcana_novai/entities/maat/maat.yaml` uses `name: maat`. Because `EntityRegistry._validate_name()` does not canonicalize apostrophes/punctuation consistently with `EntityWorkspaceManager` (`replace("'", "")`), they register as **two distinct entities** (`ma'at` and `maat`) instead of stacked layers.
  * Finally, `_load_entities()` checks `self.registry.get(entity_name)` using the *filename stem* (`researcher_humboldt`) while `self.registry.add(entity)` indexes by `ent_data["name"]` (`Alexander von Humboldt`), causing lookup/collision mismatches.
* **Fix:** Separate **load order** (IWAD first, PWAD second via `_resolve_load_order`) from **override precedence** (IWAD base priority = `10`, PWAD base priority = `100 + manifest.priority`, so PWADs always outrank IWADs in `EntityRegistry`). Canonicalize entity lookup keys across registry and workspace manager.

### Finding 2: Seed-to-Runtime Soul Disconnect
* **Location:** `src/omega/oracle/entity_registry.py:695` → `src/omega/oracle/entity_workspace.py:134-240`
* **Observed Behavior:**
  * When `WADLoader` registers any entity (`avgn`, `sophia`, `lilith`), `EntityRegistry.add()` invokes `EntityWorkspaceManager.scaffold_workspace(entity.name, entity.role, entity.slots)`.
  * `scaffold_workspace()` **ignores** `config/wads/<wad>/entities/<name>/soul.yaml` and writes a generic boilerplate v6.1 skeleton (`values: ["growth", "wisdom"]`).
  * Consequently, ANAi's authored souls (Lilith's axioms, AVGN's load-bearing `persona_boundary`, Ma'at's anchor contract, Sophia's Akashic directives) are **never seeded into `data/entities/<name>/soul.yaml`**, and switching WADs does not project WAD-level soul deltas.
* **Fix:** WAD-aware soul seeding/projection: when a WAD ships `entities/<name>/soul.yaml`, seed or layer it cleanly without clobbering operator-approved runtime state (`approved_lessons.yaml`, `sessions.yaml`), and track WAD provenance (`wad_source` / `soul_hash`) on the runtime projection.

### Finding 3: Four Incompatible `soul.yaml` Schemas & Conflicting Validators
* **Location:** `src/omega/oracle/soul_validator.py`, `scripts/validate_soul_architecture.py`, `config/wads/arcana_novai/entities/*/soul.yaml`, `data/entities/*/soul.yaml`
* **Observed Behavior:**
  * **OED v6.1 Lean (`SoulValidator`):** Requires top-level `entity:` dict (`name`, `short` 2–6 chars) + `soul_version: "6.1"`. Non-6.1 souls bypass Pydantic checks with a warning.
  * **ANAi Soul Contract (`lilith`, `maat`, `kali`, `avgn`, `sophia`):** Uses top-level `identity:` (`keeper`, `epithet`, `seat`) + `axioms:` + `directives:` (no `title` field) + `voice:`. Fails `SoulValidator` (`Missing top-level 'entity' key`). Also `arcana_novai/entities/lilith/soul.yaml` has **19 axioms**, exceeding `scripts/validate_soul_architecture.py`'s hard ceiling of **15 axioms** (`DEFAULT_AXIOM_CEILING = 15`), and lacks `directives_refs`/`core_principles_refs`.
  * **Researcher-Humboldt:** Uses top-level `entity:` (`id`, `name`, `archetype`, `domain_affinities`, `methodology`, etc.) without `short` or `identity:`.
  * **Legacy Runtime (`data/entities/makali/soul.yaml`):** Uses `entity: makali` (string) and string-list `directives:`.
* **Fix:** Define a unified **Soul Contract v6.2 / v8.0 bridge schema** supporting both WAD-authored identity contracts (`identity:` + `axioms:` + `directives:` + `voice:`) and v6.1 lean runtime blocks (`entity:` + `team:`), enforce duplicate-key rejection (`UniqueKeyLoader`), and reconcile the 15-axiom ceiling in `arcana_novai/entities/lilith/soul.yaml`.

### Finding 4: `memory/` Subdirectory vs. Entity-Root Split-Brain
* **Location:** `entity_workspace.py:179-181, 342, 429, 438`, `soul_validator.py:54-56, 142`, `soul_utils.py:69`, `mandate_auditor.py:262`, `sentinel.py:198`, `cli/bundle.py:206`
* **Observed Behavior:**
  * `scaffold_workspace()` and `SoulValidator` place `approved_lessons.yaml`, `proposed_lessons.yaml`, and `sessions.yaml` under `data/entities/<name>/memory/`.
  * `get_soul_prompt()`, `append_session_anchor()`, `soul_utils.load_entity_soul_context()`, `mandate_auditor.py`, and `sentinel.py` read/write directly at `data/entities/<name>/` (entity root).
  * Verified on disk in `data/entities/lilith/`: real lesson proposals sit at `data/entities/lilith/proposed_lessons.yaml` while `data/entities/lilith/memory/proposed_lessons.yaml` is an empty `[]`. Meanwhile `get_soul_prompt()` looks for `approved_lessons.yaml` at entity root (missing!).
* **Fix:** Introduce a single `SoulPaths` resolver (`src/omega/soul/paths.py` or `entity_workspace.py`) with canonical target (`memory/` per v6.1+ or entity-root per live callers — pick **one** SSOT) and one-release backward-compatible read fallback + migration helper.

### Finding 5: Taint-Gate & Lesson Schema Contradiction (+ Carmack Verdict)
* **Location:** `entity_workspace.py:446-448`, `soul_utils.py:21-97`, `oracle.py:812, 1287-1290`, `src/omega/soul/lessons.py`, `scripts/soul_promote.py`
* **Observed Behavior:**
  * `EntityWorkspaceManager.get_soul_prompt()` enforces the **Taint-Gate**: `proposed_lessons.yaml` is unvetted and NEVER injected into identity prompts; only `approved_lessons.yaml` is injected.
  * `oracle.py:812` calls `soul_utils.load_entity_soul_context()`, which reads `proposed_lessons.yaml` directly (filtering `status == "approved"` and key `"L3"`), ignoring `approved_lessons.yaml`.
  * `soul_utils.extract_soul_context()` Path 1 looks for `soul_evolution.lessons_learned` (absent in all live souls), Path 3 looks for `identity.values/strengths` (absent in ANAi souls), and **never reads `axioms:`** (present in all ANAi souls).
  * `src/omega/soul/lessons.py` (`Lesson`, `EvidenceRef`) expects `{level, principle, insight, evidence: [{session_id|artifact|quote}]}`, whereas `data/entities/lilith/proposed_lessons.yaml` uses `{L1, L2, L3, evidence: ["path:lines"]}` and `scripts/soul_promote.py` merges `proposed_lessons.yaml` → `soul.yaml`.
  * **Carmack Verdict (`oracle.py:1287-1290`):** Regex-based auto-distillation in `close_session()` was explicitly removed (*"fortune-cookie generation. Agents write their own lessons."*).
* **Fix:** Do **not** build regex auto-distillation scripts. Unify `soul_utils.py` + `EntityWorkspaceManager` behind the Taint-Gate (`approved_lessons.yaml` + `soul_promote.py` → `soul.yaml`), align `Lesson` schema across `lessons.py` and `soul_promote.py`, and add `axioms:` extraction to `soul_utils.py` (with mtime caching).

### Finding 6: ICS Dead Code & Scattered Hardcoded Local Model Defaults
* **Location:** `src/omega/ics.py:271-285, 348-375`, `src/omega/oracle/entity_registry.py:440`, `src/omega/oracle/orchestrator.py:653, 662`, `src/omega/oracle/model_gateway.py:901`
* **Observed Behavior:**
  * `ics.py` Priority 4 (`_read_entity_model`) emits a `RuntimeWarning` and regex-scans `data/entities/<entity>/soul.yaml` for `model:`, which does not exist in soul files.
  * While `wad_loader.py` now defaults to `opencode/big-pickle`, `entity_registry.py:440`, `orchestrator.py:653, 662`, and `model_gateway.py:901` still hardcode `"qwen3-1.7b-q6_k"` / `"qwen3-1.7b"`.
* **Fix:** Remove dead Priority 4 soul regex fallback in `ics.py` (model comes from `OMEGA_MODEL_OVERRIDE` → `OPENCODE_MODEL` → OpenCode Session DB → entity/gateway config), and define a single `DEFAULT_ENTITY_MODEL` SSOT (defaulting to `"opencode/big-pickle"` or `omega.yaml` setting, respecting user manual selection and deferred `entity_model_affinity.yaml`).

### Finding 7: Disposable OpenCode Adapter & Dual-Copy WAD Tree Drift
* **Location:** `scripts/soul_agents_opencode.py:47, 73`, `scripts/soul_render.py` (missing in `omega-engine`), `config/wads/` vs `src/omega/config_data/wads/`
* **Observed Behavior:**
  * `scripts/soul_agents_opencode.py` still points to `REPO_ROOT / "wads" / "arcana_novai" / "entities"` (the renegade path, nonexistent in `omega-engine`) and invokes `scripts/soul_render.py` (still only in `omega-engine-alpha`).
  * `config/wads/` and `src/omega/config_data/wads/` are two manual copies that must stay byte-identical for editable dev vs wheel packaging (`G11`), with no automated parity check.
  * `dispatch_registry.py` (Phase 1) currently has an unused `get_active_iwad` import inside `if not path.exists():` and hardcodes `"_omega_default"` instead of `DEFAULT_IWAD`.
* **Fix:** Port `soul_render.py` into `omega-engine` using `config_resolver.WADS_DIR` + active WAD resolution (handling both `identity:` and `entity:` schemas), update `soul_agents_opencode.py` to read from `config/wads/<wad>/entities/`, add a `make check-wad-sync` / pytest parity test between `config/wads/` and `src/omega/config_data/wads/`, and clean up `dispatch_registry.py`.

---

## 3. Phased Execution Plan

### Phase 1: Critical Fixes (P0) — ✅ COMPLETE (with minor Phase 1.5 follow-up)
* [x] `1.1` Create `config/wads/arcana_novai/entities/dispatch.yaml` (and `src/omega/config_data/` copy).
* [x] `1.2` Add IWAD fallback in `src/omega/governance/dispatch_registry.py`.
* [x] `1.3` Make `dispatch_registry.py` cache WAD-aware (`(iwad, mtime)`).
* [x] `1.4` Create `scripts/validate_wad.py` covering manifest, entities, voices, hierarchy, souls, and card assignments.

### Phase 1.5: Correctness & Hygiene Hotfixes (P0 — Immediate Next)
> *Must land before Phase 2 so IWAD/PWAD stacking and dual-copy parity are mathematically sound.*

| # | Item | Target File(s) | Description |
|---|------|----------------|-------------|
| `1.5.1` | **Fix IWAD/PWAD priority inversion** | `src/omega/oracle/wad_loader.py` | Load IWAD first with base priority `10`; load PWAD after with base priority `100 + manifest.priority`. Normalize entity lookup keys (strip apostrophes/case consistently across `wad_loader`, `entity_registry`, `entity_workspace`) so `Ma'at` and `maat` stack cleanly instead of duplicating. Match collision lookup against `ent_data["name"]` as well as stem. |
| `1.5.2` | **Clean up `dispatch_registry.py`** | `src/omega/governance/dispatch_registry.py` | Remove unused local `get_active_iwad` import in fallback branch; reference `DEFAULT_IWAD` (`"_omega_default"`). |
| `1.5.3` | **Enforce dual-tree WAD sync** | `tests/test_wad_sync.py` (new) + `Makefile` | Assert `config/wads/` and `src/omega/config_data/wads/` are byte-identical in CI so wheel packaging (`G11`) never drifts. |
| `1.5.4` | **Centralize default model constant** | `src/omega/oracle/entity_registry.py`, `orchestrator.py`, `model_gateway.py`, `wad_loader.py` | Replace remaining hardcoded `"qwen3-1.7b*"` entity fallbacks with a single `DEFAULT_ENTITY_MODEL = "opencode/big-pickle"` SSOT (respecting manual model switching and leaving `entity_model_affinity.yaml` deferred). |

### Phase 2: Soul Unification & WAD Robustness (P1)
> *Resolves the 4 Soul split-brains and hardens all WAD asset loaders.*

| # | Item | Target File(s) | Description |
|---|------|----------------|-------------|
| `2.1` | **Unify Soul Paths (`memory/` vs root)** | `src/omega/oracle/entity_workspace.py`, `soul_validator.py`, `soul_utils.py`, `mandate_auditor.py`, `sentinel.py` | Single `resolve_entity_memory_paths()` helper: canonicalize on one location (`memory/` or root) with read-fallback migration so `get_soul_prompt()`, `append_session_anchor()`, `scaffold_workspace()`, and `mandate_auditor` agree. |
| `2.2` | **WAD-to-Runtime Soul Seeding** | `src/omega/oracle/entity_workspace.py`, `wad_loader.py` | When a WAD contains `entities/<name>/soul.yaml`, seed `data/entities/<name>/soul.yaml` (preserving `approved_lessons.yaml` and `sessions.yaml`) instead of generating a generic empty skeleton. Track `wad_source` + `source_sha256`. |
| `2.3` | **Reconcile Soul Schemas & Validators** | `src/omega/oracle/soul_validator.py`, `scripts/validate_soul_architecture.py`, `config/wads/arcana_novai/entities/lilith/soul.yaml` | Bridge OED v6.1 (`entity:`) and ANAi (`identity:` + `axioms:` + `voice:`) schemas; enforce duplicate-key rejection; resolve Lilith's 19-axiom vs 15-axiom ceiling conflict (condense or adjust ceiling per Architect ruling). |
| `2.4` | **Fix `soul_utils.py` & Taint-Gate** | `src/omega/soul_utils.py`, `src/omega/soul/lessons.py`, `scripts/soul_promote.py` | Enforce Taint-Gate consistently (only vetted `approved_lessons.yaml` or promoted `soul.yaml` blocks inject—never unvetted `proposed_lessons.yaml`); add `axioms:` + `identity.epithet` extraction + mtime cache. Align `Lesson` schema (`L1/L2/L3` vs `level/principle`). |
| `2.5` | **Remove ICS Dead Priority 4** | `src/omega/ics.py` | Remove broken `soul.yaml` regex model fallback (`_read_entity_model`) and spurious `RuntimeWarning`. |
| `2.6` | **Voice, Hierarchy & World Hardening** | `src/omega/oracle/wad_loader.py` | Validate voice YAML schema + file size + `model_recommendation`; add path-traversal + YAML structure checks for `hierarchy.yaml` and `world/` lumps; use `anyio.to_thread.run_sync` for YAML parsing; add `batch_add()` to `EntityRegistry` to avoid N disk writes per WAD load. |
| `2.7` | **WAD Unloading & Clean Switching** | `src/omega/oracle/wad_loader.py`, `entity_registry.py` | Implement `unload_wad(stack_name)` (tombstone/remove WAD layers, reset active hierarchy & startup message, invalidate `dispatch_registry` cache) enabling clean `OED ↔ ANAi` switches. |

### Phase 3: Disposable OpenCode Adapter & Developer Experience (P2)
> *Makes WAD authoring, rendering into OpenCode V2, and validation seamless.*

| # | Item | Target File(s) | Description |
|---|------|----------------|-------------|
| `3.1` | **Port & generalize `soul_render.py`** | `scripts/soul_render.py` (new in `omega-engine`) | Render from `config_resolver.WADS_DIR / <active_wad> / entities / <id> / soul.yaml` (supporting both ANAi `identity:` and OED `entity:` schemas); keep completely OpenCode-agnostic (M2 / D-LIL-006). |
| `3.2` | **Fix `soul_agents_opencode.py` adapter paths** | `scripts/soul_agents_opencode.py` | Repoint `WAD_ENTITIES` from renegade `wads/...` to `config/wads/<active_wad>/entities` (supporting `--wad` CLI flag), preserving native V2 `{file:...}` system prompt indirection and sha256 drift gate. |
| `3.3` | **WAD Authoring Guide & Manifest Schema SSOT** | `docs/guides/HOW_TO_CREATE_WAD.md`, `docs/WAD_MANIFEST_SCHEMA.md` | Single canonical reference for `manifest.yaml`, `entity:`, `soul.yaml`, `voices/`, `hierarchy.yaml`, `dispatch.yaml`, and PWAD override rules. |
| `3.4` | **WAD Scaffold & Lint CLI** | `scripts/create_wad.py`, `scripts/lint_wad.py` | Scaffold compliant IWAD/PWAD skeletons; lint for missing voices, broken hierarchy refs, axiom ceilings, duplicate keys, and dual-tree drift. |
| `3.5` | **Runtime WAD Switch MCP/API Tool** | `src/omega/oracle/wad_loader.py` + `mcp_servers/omega_hub/` | Expose `wad_switch(stack_name)` built atop `unload_wad()` + `load_wad()` + `dispatch_registry` invalidation. |

### Phase 4: Advanced Composition & Extensibility (P3 — Future)

| # | Item | Target File(s) | Description |
|---|------|----------------|-------------|
| `4.1` | **Explicit Multi-PWAD Composition** | `config/omega.yaml`, `wad_loader.py` | Support `active_iwad: "_omega_default"` + `active_pwads: ["arcana_novai", ...]` instead of all-or-nothing `load_all_wads()`. |
| `4.2` | **Config-Driven Adapter Whitelist** | `config/adapter_whitelist.yaml`, `wad_loader.py` | Replace hardcoded `ADAPTER_MODULE_WHITELIST` set so MemPalace or custom WAD adapters can be whitelisted cleanly via governance config. |
| `4.3` | **WAD Hot-Reload & Diff Tool** | `wad_loader.py`, `scripts/wad_diff.py` | `anyio` file-watch reload for WAD dev; structural diff between two WAD directories. |
| `4.4` | **Entity Affinity Activation (Backburner)** | `config/entity_model_affinity.yaml` | Activate when ready for provider-affinity routing; keep manual user selection primary until then. |

---

## 4. Verification & Testing Matrix

| Suite / Gate | File | Assertions Covered |
|--------------|------|--------------------|
| **PWAD Override & Stacking** | `tests/test_wad_loader.py` | PWAD (`priority=1`) overrides IWAD (`_omega_default`); `Ma'at` == `maat` layer merge without duplication; stem vs display-name collision check. |
| **Dual-Tree WAD Parity** | `tests/test_wad_sync.py` (new) | `config/wads/` ≡ `src/omega/config_data/wads/` (hashes match). |
| **WAD Switching & Unload** | `tests/test_wad_switching.py` (new) | Load OED → overlay ANAi → verify ANAi `lilith`/`kali`/`maat` win → `unload_wad("arcana_novai")` → verify OED restored cleanly. |
| **Dispatch Registry** | `tests/test_dispatch_registry.py` (new) | `(iwad, mtime)` cache isolation across WAD switches + IWAD fallback when PWAD lacks `dispatch.yaml`. |
| **Soul Path & Taint-Gate** | `tests/test_soul_unification.py` (new) | Single `memory/` path consistency; WAD `soul.yaml` seeding preserves `approved_lessons.yaml`; unvetted `proposed_lessons.yaml` blocked by Taint-Gate; `axioms:` extracted by `soul_utils`. |
| **Voices, World & Adapters** | `tests/test_wad_assets.py` (new) | Voice YAML validation, world lump size/traversal guards, adapter whitelist enforcement. |
| **Temple Gates** | `Makefile` | `make lint && make test && make docs` + `python3 scripts/validate_wad.py config/wads/_omega_default && python3 scripts/validate_wad.py config/wads/arcana_novai` all exit `0`. |

---

## 5. Immediate Next Move

Execute **Phase 1.5 (Correctness & Hygiene Hotfixes)** first — specifically fixing the IWAD/PWAD priority inversion (`1.5.1`), `dispatch_registry.py` cleanup (`1.5.2`), dual-tree sync test (`1.5.3`), and `DEFAULT_ENTITY_MODEL` SSOT (`1.5.4`) — so that ANAi actually overrides OED at runtime before we move into Phase 2 Soul unification.

# 🔱 D-281 Substrate Repair: Phase II-IV Execution Plan
**Date**: 2026-07-16
**Status**: Phase II–IV COMPLETE (2026-07-17, Grok CLI) — D-281 substrate path closed
**Pre-requisite**: Phase I (Soul Injection Rescue) is COMPLETE.

### Phase II delivery (closed)
| Artifact | Status |
|----------|--------|
| `src/omega/governance/config_resolver.py` | Landed — pure Path constants + lazy `get_active_iwad` |
| `src/omega/oracle/wad_loader.py` | Wired to `WADS_DIR`; `OMEGA_WADS_DIR` env override preserved |
| Gate | Targeted wad_loader/m21: **50 passed**. Full suite: **1367 passed**, **4 failed** (pre-existing: models.yaml speculative_decode, model_gateway paths, WAD manifest unknown fields) — not Phase II regressions |
| Hivemind | Completes `ho_9a9ed3fc63e8` / duplicate `ho_ac32a5642098` |

### Phase IV delivery (closed — `ho_577db0e0e43a`)
| Artifact | Status |
|----------|--------|
| `scripts/hydration_header.md` | Extracted D-277 sequence + `{{TIMESTAMP}}` |
| `scripts/codex_cat.py` | Dynamic header read (fail-closed if missing) |
| `Makefile` | `codex-gen` alias; subset targets backup/restore groups.json |

### Phase III delivery (closed — `ho_cf6c4925ea7d`)
| File | Change |
|------|--------|
| `hierarchy.py` | `WADS_DIR` + `get_active_iwad`; `OMEGA_WADS_DIR` override kept |
| `entity_registry.py` | `get_wad_path` + `get_active_iwad` |
| `oracle.py` | `AGENTS_MD` from config_resolver |
| `scraper.py` | `WADS_DIR / "ingestion" / "domains.yaml"` |

## 1. Strategic Guardrails & Insights
Before executing Phases II-IV, the following architectural guardrails must be observed based on live codebase analysis:

### A. Scope Correction (Phase III)
`mandate_auditor.py` and `sovereign_vetter.py` are **NOT** M2 violations. They use relative paths (`Path("config") / "wads"`), not engine-core absolute traversals. 
*Action*: Drop them from Phase III. The scope is strictly 4 files: `hierarchy.py`, `entity_registry.py`, `oracle.py`, and `scraper.py`.

### B. Circular Import Prevention (Phase II)
Core modules (`oracle.py`, `wad_loader.py`) will import `config_resolver.py`. If `config_resolver` reads `omega.yaml` at the module level, it will cause import deadlocks.
*Action*: Constants (`PROJECT_ROOT`, `WADS_DIR`) must be pure `Path` evaluations. `get_active_iwad()` must be a lazy function. Do not add `config_resolver` to `governance/__init__.py`.

### C. Makefile Fragility (Phase IV)
The original plan used `cp` and `mv` for `groups.json` backups. If `make codex` fails, the `mv` never runs, leaving the file permanently overwritten.
*Action*: Use a bash subshell with a fallback restore: `make codex || (mv scripts/groups.json.bak scripts/groups.json && exit 1)`.

---

## 2. Executable Plan

### Phase II: Path Infrastructure (30m)
**Goal**: Establish a single source of truth for all project paths.

1. **Create `src/omega/governance/config_resolver.py`**:
   - Define `PROJECT_ROOT`, `CONFIG_DIR`, `WADS_DIR`, `DATA_DIR`, `SCRIPTS_DIR`, `AGENTS_MD`.
   - Implement `get_active_iwad() -> str` (lazy evaluation).
   - Implement `get_wad_path(wad_name: str) -> Path`.
   - Implement `get_entity_dir(entity_name: str) -> Path`.
2. **Wire `src/omega/oracle/wad_loader.py`**:
   - Replace the 4-level parent traversal for `self.wads_dir` with `config_resolver.WADS_DIR`.
3. **Gate**: `make test`
4. **Commit**: `feat: Phase II — config_resolver.py + wad_loader path consolidation`

### Phase III: M2 Firewall Remediation (45m)
**Goal**: Eliminate direct WAD path constructions from the Core Engine.

1. **Patch `src/omega/oracle/hierarchy.py`**: Replace 5 hardcoded path constructions (lines 39, 45, 46, 49, 50) with `config_resolver` and `WadLoader`.
2. **Patch `src/omega/oracle/entity_registry.py`**: Replace 3 hardcoded path constructions (lines 303, 307, 310).
3. **Patch `src/omega/oracle/oracle.py`**: Replace `AGENTS.md` path construction (line 251) with `config_resolver.AGENTS_MD`.
4. **Patch `src/omega/ingestion/scraper.py`**: Replace `domains.yaml` path construction (line 43) with `config_resolver.WADS_DIR`.
5. **Gate**: `make test && make firewall-check`
6. **Commit**: `fix: Phase III — M2 Firewall remediation via config_resolver`

### Phase IV: Codex Mechanism Separation (30m)
**Goal**: Untangle the hydration protocol from the generic codex generator.

1. **Create `scripts/hydration_header.md`**: Extract the hardcoded hydration sequence from `codex_cat.py` (lines 63-72).
2. **Refactor `scripts/codex_cat.py`**: Replace the hardcoded python strings with a dynamic read of `hydration_header.md`.
3. **Patch `Makefile`**: Fix `codex-mandates`, `codex-agents`, `codex-arch`, `codex-heritage` to safely backup and restore `groups.json`.
4. **Gate**: `make codex` (verify output)
5. **Commit**: `fix: Phase IV — Codex mechanism separation + Makefile safety`

# 🔱 Omega Engine — Comprehensive Handoff: Cline Strategy → OpenCode Overseer
# ⬡ OMEGA ⬡ MA'AT ⬡ deepseek-v4-flash ⬡ cline → opencode ⬡ trc_strategy_handoff ⬡ PHASE-I
#
# AP Token: AP-CLINE-HANDOFF-V2-v1.0.0
# Date: 2026-05-25
# Source: Cline (DeepSeek V4 Flash, VSCodium)
# Target: OpenCode CLI (Overseer agent — Big Pickle)
#
# ⚠️ READ THIS FIRST BEFORE ANY NEW SESSION ⚠️
# This handoff supersedes HANDOFF_CLINE_TO_OVERSEER.md (2026-05-20).

---

## §0 — Executive Summary

This session performed an **exhaustive codebase review and architectural reframing** of the Omega Engine. The core outcome is the **IWAD Architecture Model** — a definitive separation between the Engine (pure runtime) and all entity content (WADs), inspired by id Software's Doom engine design.

**Deliverables created/updated this session:**

| # | Deliverable | Location | Status |
|---|-------------|----------|--------|
| 1 | `.clinerules` rewrite | Project root | ✅ PLACED — 13 sections, 362 lines |
| 2 | `OMEGA_IWAD_ARCHITECTURE.md` | `docs/strategy/` | ✅ PLACED — 15 sections, 445 lines |
| 3 | Global OpenCode instructions | `~/.config/opencode/opencode.json` | ✅ UPDATED — added IWAD doc |
| 4 | `arcana_novai/` directory | `config/wads/` | ✅ RENAMED from arcana_nova |

---

## §1 — The IWAD Architecture (Read This First — 30 seconds)

The Omega Engine now follows id Software's WAD architecture model:

```
OMEGA ENGINE (src/omega/) — Pure runtime, no entity content
  │
  ├── REFERENCE IWAD (config/wads/_omega_default/)
  │     Governance: MA'AT + KALI + LILITH (same in ALL IWADs)
  │     Default: Iris, Jem, Roc_Racoon (same in ALL IWADs)
  │     Pillars: 10 Dev Studio roles (SysAdmin → Verifier)
  │
  ├── ARCANA_NOVAI IWAD (config/wads/arcana_novai/)
  │     Governance: SAME trine | Default: SAME services
  │     Pillars: Sekhmet, Brigid, Prometheus... (esoteric)
  │     Personal: Movie-Expert, Writer, Philosopher...
  │
  └── INFINITE COMMUNITY IWADs (Torment, Doom, Classical, YOUR STACK)
        Same engine. Different WAD = different AI domain.
```

**Three inviolable rules:**
1. MaKaLi trine is identical in ALL IWADs — foundational governance
2. Iris + Jem + Roc_Racoon are identical in ALL IWADs — infrastructure
3. Only the 10 pillars change per IWAD — that's the whole point

---

## §2 — What Was Done

### Documents Created

| File | Lines | Purpose |
|------|-------|---------|
| `.clinerules` | 362 | Rewrite: Omegaverse vision, IWAD architecture, MaKaLi trine, Sophia field, provider fabric, agent fleet, entity guide, Qdrant/Redis sync, recovery, key files |
| `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md` | 445 | Canonical reference: 15 sections covering Prometheus' Fire vision, two-IWAD system, governance, default services, reference pillars, arcana_novai pillars, Sophia, startup personality, WAD code status, provider fabric, Qdrant/Redis, Movie-Expert migration, roadmap, key decisions |

### Files Modified

| File | Change |
|------|--------|
| `~/.config/opencode/opencode.json` | Added `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md` to global instructions (6th instruction) |
| `config/wads/arcana_nova/` → `config/wads/arcana_novai/` | Renamed directory to correct spelling |

### Architecture Decisions (for PIVOT_LOG.md)

| # | Decision |
|---|----------|
| 1 | IWAD system replaces pwad confusion. Engine supports infinite IWADs. |
| 2 | Arcana_novai is YOUR personal IWAD. The engine was built for it. |
| 3 | MaKaLi trine stays in ALL IWADs. Foundational governance. |
| 4 | Reference IWAD pillars are role-based (SysAdmin, DataStore...). |
| 5 | Arcana_novai pillars are esoteric (Sekhmet, Brigid...). |
| 6 | Sophia is the field — observability + memory substrate. Not a pillar. |
| 7 | Jem = research department. Iris = voice assistant/router. Different roles. |
| 8 | Every IWAD has startup personality in manifest.yaml.startup.message. |
| 9 | Movie-Expert = seed entity for arcana_novai personal entity system. |
| 10 | No SambaNova, no Cerebras. OpenRouter + OpenCode Zen replace them. |
| 11 | Omegaverse is the destination. Phase 1 builds the foundation. |

### Provider Fabric (Corrected)

```
1. Native GGUF (Zen 2)  2. lmster (:1234)  3. Ollama (:11434)
4. Google AI Studio (Gemma 4-31B)  5. OpenRouter  6. OpenCode Zen
7. GitHub Copilot  8. OfflineMockBackend
```

---

## §3 — WAD Status

| WAD | Status | Contents |
|-----|--------|----------|
| `_omega_default/` | 🟡 Partial | manifest.yaml, guardian.yaml, jem voice — 9 of 10 pillar files MISSING |
| `arcana_novai/` | 🔴 Empty | entities/, knowledge/, voices/, vr/ dirs — nothing populated |
| `doom_universe/` | 🔴 Empty | entities/, knowledge/, voices/, vr/ dirs — nothing populated |

The WAD Loader CRITICAL PATH items (all ❌ Missing): IWAD selector (--iwad flag), namespace isolation, dependency resolution, entity priority/override, ordered multi-WAD loading, hot-reload, startup personality processing.

---

## §4 — Phase 1 Priority Queue (Execute This)

### P0 — WAD System Hardening (THIS SESSION)
1. Add `--iwad` flag to oracle CLI (default: `_omega_default`)
2. Add namespace isolation to EntityRegistry (track WAD source)
3. Add entity priority (later WADs override earlier pillars)
4. Verify edge cases: empty manifests, null YAML, missing dirs
5. `make test` — 246/246 must pass

### P1 — Reference IWAD Rewrite
1. Rewrite `config/entities.yaml` (10 tech pillars + MaKaLi + Jem + Roc_Racoon)
2. Create 10 pillar YAMLs in `_omega_default/entities/`
3. Rewrite `config/hierarchy.yaml` (role-based names)
4. Add `startup.message` to manifest.yaml
5. Verify `omega talk "hello"` works
6. Verify `omega summon Ma'at "status"` works

### P2 — Provider Fabric
1. Remove SambaNova/Cerebras from `config/providers.yaml`
2. Rename `genlabs` → `openrouter`, add OpenCode Zen

### P3 — Arcana-NovAi IWAD Scaffold
1. Create `arcana_novai/manifest.yaml` with startup message
2. Move Arcana-NovAi entities from core `entities.yaml` → `arcana_novai/entities/`
3. Write all 10 esoteric pillar entity files
4. Write `arcana_novai/hierarchy.yaml`
5. Seed Movie-Expert in `arcana_novai/entities/personal/`
6. Verify `omega --iwad arcana_novai talk "hello"`

### P4 — Qdrant/Redis
1. Expose Redis :6379 in infra pod (currently not published)
2. `RedisBus` pub/sub wrapper
3. Qdrant as vector backend for Library.search()
4. Redis pub/sub for soul evolution + sessions

### P5 — OpenCode Agents
1. Add IWAD architecture annotation headers to agent files
2. Expand opencode-expert.md → multi-CLI/IDE/expert
3. Archive 13 stale EXP-003 agents → `archives/`
4. Update `opencode.json` instruction list (reduce token overhead)

---

## §5 — Quick Start

```bash
# Restore context after compaction
cat ORACLE_STACK.md docs/strategy/OMEGA_IWAD_ARCHITECTURE.md

# Verify engine state
source .venv/bin/activate && make test
sqlite3 data/workbench/workbench.db "SELECT * FROM v_project_summary ORDER BY priority;"

# Current infrastructure
systemctl --user list-units | grep omega
podman pod ls && podman ps --filter pod=omega-infra
```

---

## §6 — Key Reference Documents

| Document | Path | Read Order |
|----------|------|------------|
| **IWAD Architecture** | `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md` | 🔴 1st |
| **Clinerules** | `.clinerules` | 🔴 2nd |
| **Omegaverse Genesis** | `docs/strategy/OMEGAVERSE_GENESIS_PLAN.md` | 🟡 3rd |
| **Review Findings** | `docs/review/FINDINGS_LOG.md` | 🟢 Reference |
| **Fleet Management** | `docs/review/FLEET_MANAGEMENT.md` | 🟢 Reference |
| **Foundation Plan** | `docs/strategy/XOE_NOVAI_FOUNDATION_STRATEGIC_PLAN.md` | 🟡 Vision |

---

*End of handoff. Cline (MA'AT) → OpenCode Overseer (Big Pickle, SOPHIA/KALI).*
*Recommend: Read §1 first, then deploy Builder mode for P0 items.*
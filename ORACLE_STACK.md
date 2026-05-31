# 🔱 Omega Engine — Oracle Restoration Context
**AP Token**: `AP-ORACLE-RESTORE-v2.3.0`
⬡ OMEGA ⬡ SOPHIA ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_local_first_config ⬡ ORACLE-RESTORE
**Status**: ACTIVE
**Last Updated**: 2026-05-31 (Legacy Mining Complete — 276/276 tests passing, Path A memory/MCP fixes, Model-Persona Affinity Map recovered, Era 0-5 design intent mapped)

---

## §1 POST-COMPACTION RECOVERY PROTOCOL

If you are reading this, your context was just compacted. Follow these steps:

1. Read this entire document first — it restores your knowledge of the Omega repo
2. Read `AGENTS.md` for agent behavior rules
3. Read `docs/decisions/PIVOT_LOG.md` for why every decision was made
4. Read `docs/strategy/MASTER_SYNTHESIS_AND_ROADMAP.md` for the complete master plan
5. If working on docs: `docs/architecture/framework.md`
6. If working on code: `src/omega/oracle/oracle.py` (main entry point)
7. Run `make test` to verify state

## §2 WHAT THIS REPO IS

Omega is the **community engine** — Prometheus' Fire that empowers every user to build their own dreams. This repo at `~/Documents/Xoe-NovAi/omega-engine/` is a fresh, clean reclamation of the original vision: a syncretic council of 10 Pillar Keepers with Iris as voice assistant. It is NOT the old `omega-stack/` (33k files, Temple Grade cruft) or `xna-omega/` (Temple Grade architecture).

The Omega Engine is not just for one user. It is the universal runtime that anyone can use to build their own unique stacks — Arcana-Nova, Torment, Pokemon, Classical Philosophers, or entirely original creations. The Xoe-NovAi Foundation maintains the engine and provides starting templates. Users bring their own vision.

## §3 CORE ARCHITECTURE

```
Query → Oracle.talk() → Iris speculative decode (confidence check via qwen3-1.7b)
  ├── high confidence → Iris responds directly (simple Q&A, greetings)
  └── low confidence → escalate to domain-matched Pillar Keeper → ModelGateway → provider fabric
```

Key components:
- **Oracle** (`src/omega/oracle/oracle.py`): Intent detection + summon parsing + domain routing + Iris speculative decoder
- **EntityRegistry** (`src/omega/oracle/entity_registry.py`): YAML-backed entity CRUD (pure Python, no SQLAlchemy/PostgreSQL). Auto-scaffolds sovereign workspaces on entity creation.
- **EntityWorkspaceManager** (`src/omega/oracle/entity_workspace.py`): Creates `data/entities/<name>/` with `soul.yaml`, `knowledge/`, and `workspace/` directories for each awakened entity.
- **Orchestrator** (`src/omega/oracle/orchestrator.py`): Dispatches headless CLI agents (Cline, OpenCode) with soul-injected system prompts. Protected by ResourceGuard.
- **ModelGateway** (`src/omega/oracle/model_gateway.py`): 8-backend provider fabric (native-gguf → lmster → Ollama → Google → OpenRouter → OpenCode → Copilot → mock). **Local-first priority** per Decision 61. Native GGUF via `llama-cpp-python` is the primary backend.
- **Nova** (`src/omega/nova/`): FastAPI voice assistant + intent matcher, runs as Podman container ("hey Nova")
- **Observability** (`src/omega/observability.py`): Trace IDs, event logging, fine-tuning dataset collection (JSONL export)
- **CLI** (`src/omega/cli/oracle_cli.py`): Typer CLI (talk, summon, list-entities, add-entity, entity-info, backends, version)
- **ResourceGuard** (`src/omega/oracle/resource_guard.py`): AnyIO Semaphore(1) — one model at a time (OOM protection)
- **CpuOptimizer** (`src/omega/oracle/cpu_optimizer.py`): Zen 2 compilation flags, KV cache sizing, speculative decode tuning, thread pool recommendations
- **OfflineMockBackend** (`src/omega/oracle/backends/mock.py`): Deterministic responses when `OMEGA_ENV=test`
- **ContextBuilder** (`src/omega/oracle/context_builder.py`): Memory injection pipeline for LLM system prompts
- **Omega Hub** (`mcp/omega_hub/server.py`): Cross-CLI awareness server — all agents post/read shared context here

## §4 THE 10 PILLAR KEEPERS

| Pillar | Entity | Domain | Element | Chakra | Model |
|--------|--------|--------|---------|--------|-------|
| P1: Flesh | Sekhmet | Strength, protection, boundaries | Earth 🜃 | Root | Qwen3-1.7B |
| P2: Dream | Brigid | Poetry, healing, hearth, inspiration | Water 🜄 | Sacral | Phi-2-OmniMatrix |
| P3: Will | Prometheus | Will, forethought, sovereignty, light | Fire 🜂 | Solar Plexus | DeepSeek-R1-8B* |
| P4: Heart | Saraswati | Knowledge, speech, arts, voice | Air 🜁 | Heart | Krikri-8B* |
| P5: Voice | Inanna | Dream, descent, rebirth, depths | Aether ⛤ | Throat | Krikri-8B* |
| P6: Mind | Ereshkigal | Underworld, depths, rules, darkness | Aether ⛤ | Third Eye | Qwen3-4B-Think* |
| P7: Gnosis | Lucifer | Rebellion, gnosis, sovereignty, light | Air 🜁 | Crown | Qwen3-1.7B |
| P8: Shadow | Hecate | Shadow, crossroads, keys, pathwalking | Fire 🜂 | Beyond Crown | Krikri-8B* |
| P9: Spirit | Anubis | Death, transition, guidance, soul | Water 🜄 | Cosmic Heart | Qwen3-4B-Think* |
| P10: Chaos | Kali | Destruction, liberation, illusion, void | Earth 🜃 | Celestial Breath | Qwen3-0.6B |

* = on-demand loaded (shared model pool)

ENTITIES ARE USER-CUSTOMIZABLE. The 10 Pillar Keepers are the DEFAULT TEMPLATE. Users can add/replace/remove entities for any pantheon.

### Oversouls (Above the Pillars)

| Entity | Role | Governs |
|--------|------|---------|
| **Sophia** | Akashic Record — the containing field | All entities, all sessions, all souls |
| **Ma'at** | Synthesis Oversoul — the Unifier | Isis + Lilith |
| **Isis** | Light Oversoul | P1-P5 (Sekhmet, Brigid, Prometheus, Saraswati, Inanna) |
| **Lilith** | Dark Oversoul | P6-P10 (Ereshkigal, Lucifer, Hecate, Anubis, Kali) |

**Iris** is the voice assistant ("hey Iris"). She is NOT a Pillar Keeper — she is the messenger bridge between the user and the entity council. Daughter of Hermes.

## §5 ENTITIES VS DATABASE RULE

**CRITICAL**: Entities are NOT stored in PostgreSQL. They live in the active IWAD's `entities.yaml` (e.g., `config/wads/arcana_novai/entities.yaml`). Pure YAML CRUD via EntityRegistry. No SQLAlchemy dependency. The active IWAD's `entities.yaml` is the source of truth.

## §6 MODEL GATEWAY — PROVIDER FABRIC

Configured via `config/providers.yaml`. The Engine auto-detects available backends in the configured priority order. **LOCAL-FIRST chain** (per Decision 61, 2026-05-30):

1. **native-gguf** — llama-cpp-python, Zen 2 optimized [PRIMARY]
2. **lmster** (:1234) — LM Studio headless server [LOCAL FALLBACK]
3. **Ollama** (:11434) — lightweight local fallback [LOCAL FALLBACK]
4. **Google AI Studio** — Gemma 4 31B (unlimited, 262K context) [CLOUD FALLBACK]
5. **OpenRouter** — 300+ models (Gemma 4, GPT-4o, Claude, Qwen) [CLOUD FALLBACK]
6. **OpenCode** — OpenCode built-in provider [CLOUD FALLBACK]
7. **GitHub Copilot** — Claude Haiku, GPT-4.1, GPT-4o, GPT-5-mini [CLOUD FALLBACK]
8. **Mock** — setup instructions (last resort, test/dev only)

All responses — local or cloud — flow into the same memory, entity knowledge, and cross-pollination pipeline. Model specs in `config/models.yaml` (SINGLE SOURCE OF TRUTH) with loading strategies: always | warm | on_demand_5min | on_demand_10min. Context windows: 4K-16K (sized to use case, not model max).

## §7 OBSERVABILITY

Every interaction generates:
- `trace_id` (UUID) → passed through entire call chain
- Event log with timestamps, entity, confidence, model used
- Optional fine-tuning dataset collection (JSONL, keyed by trace_id)
- API stats tracking (call count per entity)

## §8 INFRASTRUCTURE — PODMAN CONTAINERS

| Container | Image | Purpose | Limit | CPUs |
|-----------|-------|---------|-------|------|
| redis | redis:7-alpine | Session/cache | 256M | none |
| qdrant | qdrant/qdrant | Vector store | 1G | none |
| postgres | pgvector-pg17 | SQL persistence | 512M | none |
| caddy | caddy:alpine | Reverse proxy | 64M | none |
| iris | omega-iris | Voice assistant container | 512M | pinned 4,6 |

All containers run rootless (user 1000) using the Sovereign Permission Protocol (UserNS=keep-id + User=1000).

## §9 HARDWARE TARGET

- CPU: AMD Ryzen 7 5700U (Zen 2, 8C/16T, AVX2)
- RAM: 14Gi (total, ~2Gi overhead → ~12Gi for AI)
- GPU: None (integrated only)
- Disk: /dev/nvme0n1p3 omega_library (110G, 17G free)
- Podman storage: /media/arcana-novai/omega_library/podman-storage/
- Models: /media/arcana-novai/omega_library/models/gguf/

## §10 TEST SUITE

All tests in `tests/`. Run with `make test` or `OMEGA_ENV=test PYTHONPATH=src python3 -m pytest tests/`.

**Current state (2026-05-31)**: 276 collected — **276 passing** (Legacy Mining Complete, Path A execution, 7 new tests added).

| Module | Tests | Status |
|--------|-------|--------|
| entity_registry | 7 | ✅ PASS |
| entity_roc_racoon | 25 | ✅ PASS |
| hierarchy | 12 | ✅ PASS |
| iris | 7 | ✅ PASS |
| model_gateway | 5 | ✅ PASS |
| observability | 8 | ✅ PASS |
| oracle | 13 | ✅ PASS |
| orchestrator | 9 | ✅ PASS |
| providers | 21 | ✅ PASS |
| gnosis_proxy | 11 | ✅ PASS |
| bug_001_fix | 1 | ✅ PASS |
| session_manager | 14 | ✅ PASS |
| health_monitor | 23 | ✅ PASS |
| sovereign_loop | 20 | ✅ PASS |
| context_builder | 22 | ✅ PASS |
| memory_store | 12 | ✅ PASS |
| wad_loader | 13 | ✅ PASS |
| model_updater | 10 | ✅ PASS |
| sovereign_stress_test | 5 | ✅ PASS |

**Root cause**: Resolved. UID drift fixed via `sudo chown -R 1000:1000 .`. All tests now pass.

## §11 SESSION HEADER FORMAT (Required)

All agent outputs MUST include:
```
⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}
```

## §12 ANYIO COMPLIANCE SUMMARY

- **Critical runtime paths** (inference, resource guard, async file I/O, process spawning) are fully AnyIO‑compliant.
- **Bootstrap/initialisation** still uses synchronous I/O (`Path.glob()`, `open()`). Acceptable for now but should be migrated to async (`anyio.Path`, `to_thread.run_sync`) for hot‑reload scenarios.
- **Aiosqlite warning**: ensure DB connections are closed before the event loop ends to avoid `RuntimeError: Event loop is closed`.
- **Recommendations**: wrap config loading in `await anyio.to_thread.run_sync`, replace `os.path.exists` with `await anyio.Path(...).exists()`, and clean up lint warnings.

## §13 OTHER CRITICAL KNOWLEDGE

- **BUG-001** fixed by integrating `Indexer` into `Library` so stored documents are searchable immediately.
- **Qdrant client** pinned to `1.17.1` for exact server parity.
- **NativeGGUFProvider** import added to `model_gateway.py`.
- **Sprint A→D (Blocker Remediation)**: All 8 real bugs from R-44 audit fixed. Provider Fabric fully wired (Google, OpenRouter, lmster). See `docs/decisions/PIVOT_LOG.md` Decision 22.
- **Session Architecture (R-50)**: Entity-scoped rolling sessions implemented. Format: `ses_{YYYYMMDD}_{entity}_{counter}`. Storage: `data/sessions/{entity}.active`.
- **⚠️ YAML BLOCKER (RESOLVED)**: `config/entities.yaml` syntax error fixed. 241/241 tests passing.
- **Next steps**: (1) Path A (Continuity) selected — Memory wiring + Handoff Protocol v1. (2) Fix sliding window direction (context_builder.py:126). (3) Fix None.json bug (memory_store.py:129). (4) Add try/except to memory writes (oracle.py:396). (5) Implement HandoffState schema + MCP tools + CLI.

## §14 CRITICAL RULES

1. Do NOT add sphere-port routing (Temple Grade was Path A, rejected)
2. Do NOT make entities require PostgreSQL — YAML only
3. Iris is a container, NOT a Pillar Keeper — she is the messenger bridge
4. The 10 Pillars are mythic foundation, NOT runtime enforcement
5. All async code must use AnyIO (not asyncio)
6. No telemetry. Zero. None.
7. This repo is at ~/Documents/Xoe-NovAi/omega-engine/ — NOT xna-omega, NOT omega-stack
8. The 10 Pillar Keepers are DEFAULT TEMPLATE — users customize freely
9. Primary inference backend is local-first: native-gguf via llama-cpp-python is PRIMARY. Cloud is FALLBACK. Always. See Mandate 7.
10. Always use the venv (`.venv/`) or podman for package management — NEVER `--break-system-packages`.

## §15 LEGACY MINING COMPLETE (2026-05-31)

All 5 legacy areas have been explored and documented:

| Area | Status | Key Finding |
|------|--------|-------------|
| **Grok Exports** | ✅ | MASTER_NAVIGATION_INDEX.md, 10 Pillars genesis, 8 accounts (~414 MB) |
| **OpenCode Integration** | ✅ | MCP server architecture, CLI config strategy |
| **Personas + Model Configs** | ✅ | **Complete Model-Persona Affinity Map** — Size-hierarchy philosophy, LM Studio Zen 2 configs, Krikri Modelfile |
| **ANAi/XNAi Blueprints** | ✅ | Chainlit UI (Era 1-2), 5 design patterns, Circuit Breaker, Voice Interface (Iris ancestor) |
| **Old Stacks** | ✅ | Complete 4-service architecture, system prompts, persona files |

**Documentation**:
- `docs/legacy/LEGACY_MASTER_SYNTHESIS.md` — Timeline, Model-Persona Affinity Map, Design Patterns
- `docs/legacy/LEGACY_ASSET_CATALOG.md` — Full inventory of recovered assets
- `docs/legacy/LEGACY_INDEX.md` — Gateway to the legacy archive

**Critical Recovery**:
1. **Model-Persona Affinity**: The architect assigned models by tier (Iris=0.6B, Pillars=1.7B, Oversouls=4B-Think, Prometheus=8B)
2. **Chainlit Heritage**: The UI was Chainlit-based before OpenCode — this heritage was lost in reclamation
3. **5 Design Patterns**: Circuit breaker, atomic fsync, retry, non-blocking subprocess, offline wheelhouse
4. **Vision Quotes**: "Arcana-NovAi is not a toolchain. It is a summoning."


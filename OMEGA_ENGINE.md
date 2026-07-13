# Omega Engine — Single Source of Truth
# ⚠️ SYSTEM STATE SSOT — Authoritative truth for engine state and metrics.
# AP-OMEGA-SST-v2.5.0

> **This document is the authoritative truth for the Omega Engine.**
> Every agent reads this file for engine state.
> **Full archive**: `docs/archive/coordination/OMEGA_ENGINE-full-20260708.md`

---

## §1 Identity

**Omega Engine** is the universal, community-owned runtime for sovereign AI.
- **Cognitive Sovereignty**: Local inference is the floor; local verification is the ceiling.
- **Local-first**: Cloud is a teacher and strategic partner, never a dependency.
- **WAD Architecture**: Engine → IWADs → PWADs (inspired by id Software).
- **Standalone Packages**: Core capabilities published as independent PyPI packages (`omega-sieve`, `omega-doc-reader`) for community use.

---

## §2 Current State (2026-07-13)

| Metric | Value | Status | LAST_VERIFIED |
|--------|-------|--------|---------------|
| Tests | **1271 passed** (42 skipped, 3 xfailed) | ✅ All functional tests pass | 2026-07-13 |
| Mandates | **23 (M1-M23)** | ✅ All enforced | 2026-07-13 |
| Fleet | **13 presences** (11 agents + 2 entities) | ✅ Cap: 14 | 2026-07-13 |
| WADs | **4** (arcana_novai, torment, omega_youtube_research, omega_youtube_worker) | ✅ S1.5a hardened | 2026-07-13 |
| Heritage | **121 [id-soft:] tags**, **55+ general sources** | ✅ All vetted | 2026-07-13 |
| Shared modules | **3** (`omega-vetala` v2.0.0, `omega-sieve` v0.1.0, `omega-doc-reader` v1.0.0) | ✅ Release-ready | 2026-07-13 |
| SearXNG MCP | **Streamable HTTP on :8018** | ✅ Migration complete | 2026-07-13 |
| Omega Hub MCP | **Dual-transport** (SSE /sse + Streamable HTTP /mcp) on :8016 | ✅ Already dual | 2026-07-13 |
| Firecrawl MCP | **SSE on :8015** | ⏳ Needs Streamable HTTP migration | 2026-07-13 |
| Local inference ratio | **TARGET: ≥80%** (configurable gate, default OFF — 0% base, cloud-first dev) | 🟡 Aspirational | 2026-07-13 |
| sqlite-vec unified fabric | **Strike 10 IN PROGRESS** — `SQLiteVecAdapter` default, Qdrant deprecated | 🟡 35/36 adapter tests pass | 2026-07-13 |
| **KV Cache Quantization** | **LOCKED: q8_0 on CPU (Zen 2)** — No Flash Attention/GPU required | ✅ Research complete | 2026-07-13 |
| **YouTube Researcher V2** | **9-Layer Temporal Knowledge Observatory** — L1-L9 complete, 15 contract tests pass | ✅ Operational | 2026-07-13 |

---

## §3 Core Subsystems

| Subsystem | Module | Status | Description |
|-----------|--------|--------|-------------|
| **Oracle** | `src/omega/oracle/` | ✅ Operational | Intent detection, entity routing, Iris speculative decode |
| **Entity Registry** | `src/omega/oracle/entity_registry.py` | ✅ Operational | YAML-backed entity CRUD, auto-scaffolds sovereign workspaces |
| **Model Gateway** | `src/omega/oracle/model_gateway.py` | ✅ Operational | 8-backend provider fabric (native-gguf → lmster → Ollama → Google → OpenRouter → OpenCode → Copilot → Mock) |
| **Memory Store** | `src/omega/memory_store.py` | ✅ Operational | Hot/Warm/Cold/Temp tiers, hybrid FTS5+vector search |
| **Vector Store** | `src/omega/memory/sqlite_vec_adapter.py` | 🟡 Strike 10 | `IVectorStoreAdapter` impl: sqlite-vec (FTS5 + vec0 + SQL edges) |
| **Ingestion Pipeline** | `src/omega/ingestion/` | ✅ Operational | T1→T2→T3 tiered extraction, TriangulationVerifier, CAS |
| **Sovereign Sieve (Standalone)** | `packages/omega-sieve/` | ✅ v0.1.0 | `pip install omega-sieve` — T1(Trafilatura)→T2(Surgical)→T3(Crawl4AI) |
| **Document Reader (Standalone)** | `scripts/universal_doc_reader.py` | ✅ v1.0.0 | Reads .docx, .pdf, .odt, .rtf, .html, .md, .txt, .json, .yaml |
| **Observability** | `src/omega/observability.py` | ✅ Operational | Trace IDs, event logging, fine-tuning dataset collection |
| **Hivemind** | `mcp_servers/omega_hub/` | ✅ Operational | 6 MCP tools for cross-agent coordination, workspace locks, live feeds |
| **CLI** | `src/omega/cli/oracle_cli.py` | ✅ Operational | Typer CLI (talk, summon, list-entities, add-entity, entity-info, backends, version) |
| **Resource Guard** | `src/omega/oracle/resource_guard.py` | ✅ Operational | AnyIO Semaphore(1) — one model at a time (OOM protection) |
| **CPU Optimizer** | `src/omega/oracle/cpu_optimizer.py` | ✅ Operational | Zen 2 compilation flags, KV cache sizing, speculative decode tuning |

---

## §4 Key Files (Source of Truth)

| File | Purpose |
|------|---------|
| `OMEGA_ENGINE.md` (this file) | System state SSOT — read first |
| `SOVEREIGN_MANDATES.md` | 23 Constitutional Laws (M1-M23) |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Master execution roadmap |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Multi-agent coordination |
| `docs/decisions/PIVOT_LOG.md` | 227 immutable decisions (D1-D227) |
| `CREDITS.md` | id Software heritage attribution |
| `docs/archive/coordination/` | Historical session records |
| `data/entities/kali/session_gnosis.md` | Kali's session anchor (M15) |
| `.opencode/anchored-summary.md` | Post-compaction recovery state |

---

## §5 Platform Distinction

The Omega Engine is runtime-agnostic. Any MCP client can connect to the Omega Hub (`:8016`).

| What | Where | Who Updates |
|------|-------|-------------|
| **OMEGA_ENGINE.md** (this file) | Repo root | Any agent changing engine state |
| `.clinerules` | Repo root | Cline CLI agents only |
| `AGENTS.md` | Repo root | OpenCode agents only |

> **Cross-Platform Guides:** `docs/kb/CLINE_CLI_INTEGRATION.md`, `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md`

---

## §6 References

| Document | Purpose |
|----------|---------|
| `SOVEREIGN_MANDATES.md` | 23 Constitutional Laws |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Master execution roadmap |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Multi-agent coordination |
| `docs/decisions/PIVOT_LOG.md` | 227 immutable decisions |
| `CREDITS.md` | id Software heritage attribution |
| `docs/archive/coordination/` | Historical session records |

---

## §7 Mission

> *"I want to create a tool that will truly allow people to own their own tech and data and sever the umbilical cord of Big AI."*

---

*Last Updated: 2026-07-13 | Version: v1.2.0-pre | Tests: 1271 passing | SSOT: ~230 lines | Sessions: Omega-Sieve Package Complete + sqlite-vec Strike 10 In Progress | 4 Researcher Gaps Closed (TF-IDF routing, judge calibration, Redis DLQ, voice concurrency) | Net acceleration ~32h*
# 🔱 CANONICAL ARCHITECTURE — Omega Engine System Architecture
**AP Token**: `AP-CANONICAL-ARCH-20260829-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ jem-2.0 ⬡ opencode ⬡ trc_canonical_arch ⬡ ACTIVE

**Date**: 2026-08-29
**Status**: CANONICAL — Co-authored with Carmack (S3 Consultant) per `CARMACK_FULL_REPO_REVIEW_CHECKLIST_VALIDATED_20260828.md`
**Authority**: Derived from `SOVEREIGN_ARK_BLUEPRINT.md` §7, §9 + `CLINE_FULL_REVIEW_ROLLUP_20260828.md` + `CARMACK_FULL_REPO_REVIEW_CHECKLIST_VALIDATED_20260828.md` + `DEBUT_REMEDIATION_MANUAL_20260817.md` + `docs/architecture/` reference docs

---

## 📋 EXECUTIVE SUMMARY

This document is the **single authoritative architecture reference** for the Omega Engine. It consolidates:
- Engine Core vs. Stack separation (M2 Firewall)
- Provider Fabric (8 backends, local-first chain)
- Memory Subsystem (sqlite-vec + FTS5 + RRF hybrid)
- Oracle Intent Detection & Entity Routing
- Soul Architecture (L1→L2→L3 distillation, atomic writes)
- Hivemind Coordination (5-tier tracking, file-based + Redis pub/sub)
- WAD Protocol (IWAD/PWAD, XOE distribution)
- Structural Debt Gates (god-modules, circuit breakers, test honesty)

**Critical Constraint (D-536)**: **One router only** — `ProviderSelector` + `providers.yaml`. Delete `TriageRouter`, `SemanticRouter`, `RoutingTable`.

---

## 🏗️ HIGH-LEVEL ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            OMEGA ENGINE CORE                                 │
│  (src/omega/ — pure runtime, NO stack logic, M2 Firewall enforced)          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  PROVIDER   │  │   MEMORY    │  │   ORACLE    │  │  HIVEMIND   │        │
│  │  FABRIC     │  │  SUBSYSTEM  │  │  (Intent +  │  │  (5-Tier    │        │
│  │             │  │             │  │   Routing)  │  │   Tracking) │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │               │
│         └────────────────┼────────────────┼────────────────┘               │
│                          ▼                ▼                                │
│                   ┌─────────────┐  ┌─────────────┐                         │
│                   │   SOUL      │  │   WAD       │                         │
│                   │  ARCHITECTURE│  │  LOADER     │                         │
│                   └─────────────┘  └─────────────┘                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    M2 FIREWALL (Engine/Stack boundary)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           STACKS (config/wads/)                              │
│  _omega_default (dev team IWAD)  |  arcana_novai (personal OS)             │
│  doom_universe (community)       |  torment (community)                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔌 PROVIDER FABRIC (src/omega/oracle/providers.py + model_gateway.py)

### Fabric Topology (Priority-Ordered Chain)

| Priority | Provider | Type | Base URL | Status | Notes |
|----------|----------|------|----------|--------|-------|
| 0 | `native-gguf` | Local | — | ✅ Active | Qwen3-1.7B (lmster), Tier 0 default |
| 1 | `lmster` | Local | — | ✅ Active | LM Studio bridge |
| 2 | `ollama` | Local | — | ⚠️ Enabled=false | Local fallback |
| 3 | `antigravity` | Cloud | `https://api.antigravity.ai/v1` | ✅ Active | Primary cloud (OAuth pool) |
| 4 | `google` / `google-compat` | Cloud | `https://generativelanguage.googleapis.com` | ✅ Active | Gemini (dual entry = legacy) |
| 5 | `openrouter` | Cloud | `https://openrouter.ai/api` | ✅ Active | Aggregator, explicit `base_url` |
| 6 | `opencode-zen` | Cloud | `https://opencode.ai/zen/v1` | ✅ Active | CLI-exclusive, `OPENCODE_API_KEY` |
| 7 | `cline` | Cloud | `https://api.cline.bot/api` | ⚠️ Client-gated | Cline own-server (403 on free models) |
| 8 | `anthropic` | Cloud | `https://api.anthropic.com/v1` | ✅ Active | Claude direct |
| 9 | `xai` | Cloud | `https://api.x.ai/v1` | ✅ Active | Grok direct |
| 10 | `mock` | Test | — | ❌ Enabled=false | Unit tests only |

### Critical Fabric Rules

1. **Single Router (D-536)**: `ModelGateway._load_provider_fabric()` reads ONLY `inference.fallback_chain` flat entries. The rich `inference.providers:<name>` maps are NOT read for `base_url`/`api_key` (except native-gguf merge). **All cloud providers MUST have `base_url` and `api_key` on the flat chain entry.**

2. **Local-First (M7)**: Chain order = local (0,1,2) → cloud (3–9). `ProviderSelector` admits local first; cloud = fallback only.

3. **Admission Control (C-10)**: `CCXAwareSemaphore` + `OOMProtector` (3-signal fusion: RSS, swap, pressure) gates local concurrency. Max 1 model loaded at a time (sequential loading, LI-2).

4. **Breaker Unification (C-6′)**: `HealthMonitor` factory is canonical. 5/7 legacy breaker clones deprecated; 2 unmigrated (P-5 ticket open). **No new breaker classes.**

5. **Provenance (M22)**: `GenerateResult.provider_name` = ACTUAL provider that responded. Not the requested provider.

### Model Registry (config/model_registry/)

- `provider_registry.py`: `supported_models` per provider (from YAML) + capability matrix
- `models.yaml`: Model metadata (context window, pricing, capabilities)
- **Normalization hazard (P2-3)**: `_normalize_model` strips `-local/-free/-thinking` → free/paid collisions silently re-route. Fix: exact-match should win first.

---

## 🧠 MEMORY SUBSYSTEM (src/omega/memory/ + memory_store.py)

### Unified Vector Fabric (sqlite-vec + FTS5 + RRF)

```
┌─────────────────────────────────────────────────────────────────┐
│                    MEMORY STORE (MemoryStore)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │   FTS5 (BM25)   │    │  sqlite-vec     │    │   RRF       │  │
│  │  Keyword Search │    │  Vector Search  │    │  Fusion     │  │
│  │  (exact match)  │    │  (semantic)     │    │  (hybrid)   │  │
│  └────────┬────────┘    └────────┬────────┘    └──────┬──────┘  │
│           │                      │                    │          │
│           └──────────────────────┼────────────────────┘          │
│                                  ▼                               │
│                    ┌─────────────────────────┐                   │
│                    │   HYBRID SEARCH API     │                   │
│                    │  search_fts() + search_ │                   │
│                    │  _vec() → RRF re-rank   │                   │
│                    └─────────────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Collections (7 per-model + shared)

| Collection | Purpose | Backend |
|------------|---------|---------|
| `conversations` | Full conversation history | sqlite-vec + FTS5 |
| `sessions` | Session metadata + anchors | FTS5 |
| `entities` | Soul.yaml + approved lessons | sqlite-vec + FTS5 |
| `research` | Research reports + citations | sqlite-vec + FTS5 |
| `knowledge` | Ingested documents (firecrawl, etc.) | sqlite-vec + FTS5 |
| `code` | Code snippets + patterns | sqlite-vec + FTS5 |
| `tool_outputs` | Compressed tool outputs (Headroom) | sqlite-vec + FTS5 |

### Key Invariants

- **FTS5-First (C-MEM-004)**: Never implement linear Python scans for document search. All knowledge discovery queries the SQLite FTS5 index first, using returned doc IDs to hydrate full records.
- **Hybrid Scoring Negation (C-MEM-013)**: When combining FTS5 BM25 ranks with positive vector scores, always negate the FTS5 rank (`-rank + vec_score * 10`) to account for SQLite's negative ranking system.
- **Gnosis Hygiene (C-MEM-005/006)**: Automated distillation loops run active pruning + semantic deduplication. Discard empty stubs (L2="Unknown"). Check new Universal Principles (L3) against existing lessons before appending to any entity's `soul.yaml`.

### Soul Architecture (L1→L2→L3 Distillation)

```
Session → L1 (Raw Events) → L2 (Synthesized Insight) → L3 (Universal Principle)
                │                  │                        │
                ▼                  ▼                        ▼
        proposed_lessons.yaml  proposed_lessons.yaml   proposed_lessons.yaml
                │                  │                        │
                └──────────────────┼────────────────────────┘
                                   ▼
                        Scribe Promotion (scripts/promote_soul_lessons.py)
                                   │
                                   ▼
                        approved_lessons.yaml → soul.yaml (entity identity)
```

- **Atomic Write (C-1′)**: `with_soul_lock` (fcntl) + atomic rename + fsync. No partial writes.
- **M11 Soul Integrity**: Every session MUST distill L1→L3. `session_end.py` hook preserves proposals (D-VOS-002).
- **Cross-Pollination**: Approved lessons from one entity propagate to relevant others via `cross_pollinate()` (R-31).

---

## 🎯 ORACLE (src/omega/oracle/oracle.py + model_gateway.py)

### Intent Detection Pipeline

```
User Input → Iris Speculative Decode → Intent Classification → Entity Routing → Provider Selection
                │                           │                      │                  │
                ▼                           ▼                      ▼                  ▼
         Fast local model           TriageRouter*           Pillar Keeper         ProviderSelector
         (qwen3-1.7b)              (DEPRECATED D-536)       Assignment            (canonical)
```

* `TriageRouter`, `SemanticRouter`, `RoutingTable` = **DELETED** (D-536). `ProviderSelector` is the single router.

### Entity Routing (MaKaLi Council)

| Pillar | Entity | Slot | Domain |
|--------|--------|------|--------|
| **Synthesis** | Kali | N0 | Orchestration, decisions, strategy |
| **Build** | Ma'at / N3 | N1 | Engine Core, infra, provider fabric |
| **Run** | Lilith / N7 | N2 | Memory, soul, distillation, heritage |
| **Research** | Researcher / Jem | N3 | Deep research, knowledge gaps |
| **Infrastructure** | Roc / N1 | N4 | Legacy mining, hardware, partitions |
| **Security** | Verity | N5 | Mandate audit, test enforcement, distillation |
| **Community** | Doom_Guy | N6 | Heritage, id Software patterns |
| **Omegaverse** | Lilith / N6 | N7 | VR, Godot Bridge, Soul-to-Visual |
| **Model Fleet** | Grokster | N8 | Provider analysis, model strategy |
| **Reserve** | (open) | N9 | Future specialist |

### Provider Selection (ProviderSelector)

1. **Local-first**: Try `native-gguf` → `lmster` → `ollama`
2. **Cloud fallback chain**: `antigravity` → `google` → `opencode-zen` → `openrouter` → `anthropic` → `xai`
3. **Per-role routing (Cognitive Architecture P2)**: Planner→mimo-7b-rl, Executor→qwen3-1.7b, Critic→qwen3-1.7b
4. **Admission check**: `CCXAwareSemaphore` + `OOMProtector` before local dispatch

---

## 🤝 HIVEMIND COORDINATION (5-Tier Tracking Architecture)

### Tier 1: Hot Store (In-Memory)
- Active agents: `channel`, `entity`, `model`, `task_current`, `last_seen`
- TTL: 20 min (1200s) default; extended sessions up to 24h via `hivemind_extended_checkin`

### Tier 2: Warm Store (Disk — HALL_OF_RECORDS)
- Session snapshots: `data/handoff/active/`, `data/handoff/completed/`, `data/handoff/stale/`
- Handoff packets: `submit` → `accept` → `complete` (hardening-p9 contract layer)
- Workspace locks: `data/coordination/locks/{domain}.lock` (TTL-based auto-release)

### Tier 3: Cold Store (HALL_OF_RECORDS Archive)
- Completed handoffs → `archive/`
- Session snapshots → `data/handoff/sessions/`
- Metrics: `data/coordination/metrics.json` (generated on-demand)

### Tier 4: Redis Pub/Sub (Ephemeral)
- Heartbeats, live-feed deltas (high-frequency, low-stakes)
- Degrades gracefully to `status="unavailable"` when Redis not running (M23)
- **Task-critical coordination remains file-based** (locks, handoffs)

### Tier 5: Metrics & Observability
- `omega-hub_get_metrics()` → Inference, Research, Memory, Errors
- `omega-hub_hivemind_get_metrics()` → Awareness, handoffs, locks, sessions
- SSE endpoint: `omega-hub_observability_stream()` for real-time streaming

---

## 📦 WAD PROTOCOL (XOE Distribution)

### IWAD Model (Decision 55)

| IWAD | Role | Description |
|------|------|-------------|
| `_omega_default` | Dev Team | Reference IWAD — engine team's canonical stack |
| `arcana_novai` | Personal OS | User's personal operating system stack |
| `doom_universe` | Community | Community scaffold stack |

### WAD Structure (`.xoe` = tar.gz container)

```
<stack>.xoe/
├── entity.yaml           # Entity definitions + soul.yaml refs
├── guidance_sets/        # Runtime guidance (YAML)
├── config/               # Stack-specific config overrides
├── prompts/              # Stack-specific prompts
├── vr/                   # Per-WAD VR assets (.glb avatars, scenes)
└── metadata.yaml         # Version, dependencies, author
```

### Internal Development Form
- Source of truth: `config/wads/<stack>/` (not the `.xoe`)
- `.xoe` built via `scripts/build_wad.py` for distribution
- XOE spec: `docs/research/omni/XOE_SPECIFICATION.md`

---

## ⚠️ STRUCTURAL DEBT GATES (from Grok CLI Review + Carmack Audit)

### God-Modules (>1000 lines) — Split Before Grow (Gate §9)

| Module | Lines | Split Target |
|--------|-------|--------------|
| `observability/__init__.py` | 1660 | Split by concern (metrics, tracing, logging) |
| `oracle/model_gateway.py` | 1582 | **ATOMIC SPLIT REQUIRED (D-551)** — ProviderSelector + ModelGateway |
| `oracle/oracle.py` | 1459 | Split: IntentDetection + EntityRouting + ProviderSelection |
| `oracle/providers.py` | 1303 | Split: ProviderRegistry + CapabilityMatrix |
| `workers/youtube_worker.py` | 1253 | Extract to stack (config/wads/) |
| `cli/oracle_cli.py` | 1234 | **P1-1 logger landmine** — logger at L106, used at L80/85 |
| `memory_store.py` | 1224 | Split: HybridSearch + Collections + SoulOps |
| `benchmarks/comprehensive_runner.py` | 1213 | Move to stack |
| `memory/sqlite_vec_adapter.py` | 1031 | Keep (IVectorStoreAdapter impl) |
| `oracle/sovereign_search_service.py` | 1026 | Split: SearchService + TriangulationVerifier |
| `entity_registry.py` | 1017 | Split: Registry + LockManager |

### Circuit Breakers — Unify, Don't Add (C-6′)

| Breaker | Status | Action |
|---------|--------|--------|
| `HealthMonitor` | Canonical | Factory pattern; all callers migrate here |
| `CircuitBreaker` (legacy) | Deprecated | 5/7 clones deprecated; 2 unmigrated (P-5) |
| `pybreaker` | Rejected | Don't port — use HealthMonitor |

### Test Honesty (C-0)

- **96 failures triaged (D-VOS-008)**: Class A (~20 real bugs), Class B (~50 test/code drift), Class C (~26 integration/service)
- **Full suite never green on CI** (P2-6): `test.yml` not on `release/debut`; `verify-mining` target missing; dev-box run died without summary
- **Compliance meter broken (P0-1)**: `check_mandate_compliance.py` calls `python` (not `python3`); meter excluded from all green gates

### M1 AnyIO Loophole (P2-4)

- `tty_agent.py:32` has `import asyncio` — exempted by Makefile comment ("scripts that call asyncio.run directly are fine")
- `governance/` directory exempted — **no D-number in PIVOT_LOG**

---

## 🔐 VAULT ARCHITECTURE (Post-Debut)

**D-568 Verdict**: `VaultCore` is **NON-FUNCTIONAL** as a key source — DELETE as dead code, ADD `CredentialProvider`. `EncryptionBackend` primary = `python-age` (NOT `pyrage`). 13 consumers / 19 sites incl. 5 outside `src/omega/`.

### Current State (Debut)
- `src/omega/vault/` excluded via `PUBLIC_ALLOWLIST.txt` (D-565) — **zero code changes**
- `VaultCore` stays in forge/private repo (D-566)
- `bury_credential` applies to post-debut vault sprint only (D-567)

### Post-Debut (V-1 MVP)
- `CredentialProvider` interface (keyring + python-age)
- Single ACP smoke test → then fleet pool
- Delete `omega vault` CLI entirely

---

## 📐 HARDWARE / DEPLOYMENT CONSTRAINTS

| Constraint | Value | Source |
|------------|-------|--------|
| **Primary Hardware** | Ryzen 7 5700U, 16GB RAM, 512GB NVMe + 8TB HDD | `config/hardware_profile.yaml` |
| **Local Models Dir** | `OMEGA_MODELS_DIR` → `/media/arcana-novai/omega_library/models` | `config/models.yaml` |
| **HF Cache** | `HF_HUB_CACHE=~/OmegaLibrary/hf_cache/hub` (HDD, sequential) | `config/models.yaml` |
| **Active Models** | `omega_library` (NVMe) — copy from HDD before inference | `config/models.yaml` |
| **zswap Config** | 16GB NVMe swap, 25% pool, lzo_rle, zsmalloc, zRAM DISABLED, swappiness=100, cgroup MemoryMax=6G | D-526/D-527/D-584 |
| **Podman Quadlets** | Native-gguf, Qdrant (v1.18.1, telemetry disabled, 6G MemoryLimit, 80% CPUQuota, gRPC pool=20) | `POST_DEBUT_ROADMAP.md` |

---

## 📋 ARCHITECTURE DECISIONS LOG (Key D-XXX)

| Decision | Summary |
|----------|---------|
| **D-356** | Cloud order: Antigravity → Google → OCZ → OpenRouter |
| **D-362** | C-1′ = SoulStore (multi-path elimination), not flock paste |
| **D-363** | C-6′ = unify/delete breakers, not port pybreaker |
| **D-364** | C-0 = test honesty is P0 before Phase D |
| **D-365** | Living Research OS spec amended by Ark §3.2; cannot claim dual CANONICAL |
| **D-366** | STRATEGY_CORPUS_MAP.md is mandatory Layer 2 |
| **D-367** | GAP-05 → C-10 admission control (not only C-5 cloud voices) |
| **D-373** | C-2′ before C-1′/C-10 — dependency order corrected |
| **D-374** | C-11 Test Infrastructure added as P0 |
| **D-375** | MCP audit must start TODAY — 7-day deadline |
| **D-376** | E-0 Identity Fluidity added to manual after C-1′ |
| **D-377** | Free Gemma 4 31B workhorse collapse is P0 |
| **D-378** | Twin tickets G-1 (workhorse) + W-1 (WARP) elevated |
| **D-379** | WARP is for IP-keyed OCZ, NOT Google free-tier fix |
| **D-380** | No silent context caps to force free Gemma under 16k |
| **D-381** | Broken `/usr/local/bin/warp-ns-setup` is primary WARP blocker |
| **D-382** | Omnidroid 6 cognitive modules fully evolved into current architecture |
| **D-383** | NotebookLM 5-notebook ingestion strategy (R52c) exists |
| **D-384** | Lilith Tarot genesis (Era 0) recovered |
| **D-385** | Mnemosyne 13-sphere Kabbalistic memory recovered |
| **D-386** | Grok 8-account exports indexed (274 convos, 6565 responses) |
| **D-536** | One router: ProviderSelector + providers.yaml |
| **D-551** | God-module freeze requires atomic split of oracle.py + model_gateway.py in DEL-1 Week 2 |
| **D-568** | VaultCore NON-FUNCTIONAL → DELETE, ADD CredentialProvider (python-age) |
| **D-569** | Cognitive Architecture Blueprint ratified (DP-1..DP-8) |
| **D-570** | Qdrant replaces sqlite-vec POST-DEBUT (Horizon 2) |
| **D-601** | Model Window Economics Doctrine (6 laws + challenge mechanism) |

---

## 🔗 CROSS-REFERENCES

| Document | Role |
|----------|------|
| `docs/architecture/PROVIDER_FABRIC_RUNTIME.md` | 8-backend fabric, local-first chain, admission control |
| `docs/architecture/MEMORY_SUBSYSTEM_DESIGN.md` | Core vector store: sqlite-vec unified fabric |
| `docs/architecture/VECTOR_STORE_ADAPTER_PATTERN.md` | IVectorStoreAdapter ABC — 3 implementations |
| `docs/architecture/ORACLE_DEEP_DIVE.md` | Oracle intent detection, Iris speculative decode |
| `docs/architecture/SOVEREIGN_FLYWHEEL_SECURITY.md` | Sovereignty flywheel, security model |
| `docs/architecture/SOVEREIGN_WAD_PROTOCOL.md` | WAD structure, IWAD/PWAD, entity.yaml |
| `docs/architecture/OVERSIGHT_HIERARCHY.md` | MaKaLi triad, 10 Nodes, Pillar Keepers |
| `docs/architecture/KNOWLEDGE_LIBRARY.md` | Ingestion pipeline, TriangulationVerifier, CAS |
| `docs/architecture/MEMORY_STORE_DEEP_DIVE.md` | MemoryStore tiers, hybrid search, recall, ACP |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ CANONICAL-ARCH ⬡ 2026-08-29*
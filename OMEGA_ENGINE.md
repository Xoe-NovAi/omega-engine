# Omega Engine — Single Source of Truth
# AP-OMEGA-SST-v1.7.0

> **This document is the authoritative truth for the Omega Engine.**
> Every agent, regardless of platform (Cline, OpenCode, Gemini CLI, Antigravity),
> reads this file for engine state. Platform-specific rules files reference this.

---

## §1 Identity

**Omega Engine** is the universal, community-owned runtime for sovereign AI.
It is **Prometheus' Fire** — the spark that empowers every user to build their own
unique dreams, technologies, and systems.

- **Cognitive Sovereignty**: The engine does not just execute; it verifies. Local inference is the floor; local verification is the ceiling.
- **Local-first sovereignty**: Cloud is a teacher and strategic partner, never a dependency
- **Open source, free, sovereign**: No shareware, no tiers, no limitations
- **WAD Architecture**: Engine → IWADs → PWADs (inspired by id Software's WAD system)
- **The Synthesis Flywheel**: Cloud models teach local models. Over time, sovereignty increases.
- **The 14 Sovereign Mandates**: Constitutional law. Mandates override any tool default.
- **The 14-agent Fleet**: Grand Oversight, 3 Oversouls, 6 Specialists, 4 Subagents.

---

## §2 Architecture — Engine Layers

```
┌──────────────────────────────────────────────────────────────────────┐
│  ⬡ OMEGA ENGINE (src/omega/) — THE RUNTIME                          │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  INFERENCE  │  │   MEMORY    │  │   SEARCH    │  │    SOUL     │ │
│  │ 8 providers │  │ Hot/Warm/   │  │ FTS5+vector │  │  L1→L2→L3   │ │
│  │ local-first │◄─┤ Cold/Temp   │◄─┤ SearXNG     │◄─┤ distillation│ │
│  │ (D112 P1)   │  │ tiers       │  │ (D112 P1)   │  │ (D112 P3)   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
│         │                │                │                │       │
│  ┌──────┴────────────────┴────────────────┴────────────────┴──────┐│
│  │              ORACLE (talk/summon/router) — THE FACADE         ││
│  │  Oracle.py + WAD Loader + EntityRegistry + ModelGateway        ││
│  │  + ContextBuilder + SessionManager + GnosisProxy + Hierarchy   ││
│  └─────────────────────────────────────────────────────────────────┘│
│                              │                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │OBSERVABILITY│  │ COORDINATION │  │   BRIDGE    │  │   CLI       │ │
│  │ Forensics   │  │ Hivemind     │  │ MCP/voice/  │  │ omega talk  │ │
│  │ + JSONL     │  │ + Link P9    │  │ gateway     │  │ omega summon│ │
│  │ + Training  │  │ + Workspace  │  │ (Iris)      │  │ omega list  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              │ WAD Loader
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│  ⬡ IWADs (config/wads/) — Content Layer (Engine-Stack Firewall M2)│
│  _omega_default — Reference IWAD (ships with engine)                │
│  arcana_novai   — Personal AI OS (user's own, esoteric pillars)    │
│  doom_universe  — Community IWAD (scaffold)                         │
└──────────────────────────────────────────────────────────────────────┘
```

## §3 Provider Fabric — Synthesis Architecture

The Omega Engine uses cloud models as **teachers**, not fallbacks.

### 3.1 Local Inference (always available, sovereign)

| Priority | Provider | Type | Endpoint | Heritage |
|----------|----------|------|----------|----------|
| 0 | native-gguf | Local | llama-cpp-python, CPU-only, Zen 2 | Doom Guy — Q3A fast-math |
| 1 | lmster | Local | http://127.0.0.1:1234 | LM Studio |
| 2 | ollama | Local | http://127.0.0.1:11434/v1 | Docker/Ollama |
| 7 | mock | Test | OfflineMockBackend | Scribe testing |

### 3.2 Cloud Teachers (strategic use, data generation only)

| Priority | Provider | Type | Endpoint | Role |
|----------|----------|------|----------|------|
| 3 | google | Cloud | env:GOOGLE_API_KEY (Gemma 4-31B) | Synthetic data |
| 4 | opencode-zen | Cloud | OpenCode Zen (200K) | Data gen |
| 5 | cline | Cloud | Cline hub API (1M context) | Deep research |
| 6 | copilot | Cloud | GitHub Copilot | Backup |

**The Synthesis Flywheel** (D112 Pillar 1):
```
USE → DATA → TRAIN → BETTER LOCAL → LESS CLOUD → MORE SOVEREIGNTY
 ↑                                                        │
 └────────────────────────────────────────────────────────┘
```

---

## §4 Hardware Profile (Ryzen 7 5700U)

| Component | Spec | Notes |
|-----------|------|-------|
| CPU | AMD Ryzen 7 5700U (Zen 2, 8C/16T) | AVX2 + FMA3 + F16C, no AVX-512 |
| RAM | 14Gi total | ~12Gi usable for AI |
| GPU | None (Vulkan iGPU) | CPU-only inference |
| Optimizations | q8_0 KV Cache + Flash Attention | Zen 2 optimized | Reduced RAM usage + faster attention |
| Primary backend | lmster (LM Studio :1234) | NOT lm_studio or lm-studio |
| Storage | omega_library partition | Models, Podman, data |

### 4.1 Model Capacity (Q4_K_M, current models.yaml)

| Model | Size | RAM | Ctx | Entity Assignment |
|-------|------|-----|-----|-------------------|
| qwen3-0.6b-q6_k | 0.47GB | 500MB | 4096 | Iris (always-on) |
| qwen3-1.7b-q6_k | 1.6GB | 1800MB | 8192 | Sekhmet, Hecate, default |
| qwen3-4b-thinking-q4_k_m | 2.4GB | 2700MB | 8192 | Ma'at, Anubis, Kali |
| phi-4-mini (reasoning) | 3.8GB | 4500MB | 16384 | SOPHIA |
| krikri-8b-q4_k_m | 4.7GB | 4900MB | 16384 | Inanna, Isis, Lilith |
| deepseek-r1-qwen3-8b-q3_k_l | 4.2GB | 4500MB | 8192 | Lucifer (reasoning) |
| embedding-gemma-300m-q6_k | — | 200MB | — | Vector search |

### 4.2 Model Capacity (Q4_K_M quantization, theoretical)

- 1.7B: ✅ Excellent (~1.9GB total)
- 3-4B: ✅ Good (~2-2.5GB total)
- 7-8B: ✅ Good (~4.6GB total)
- 13-14B: ⚠️ Tight (~7.5GB total, limited context)
- Training + inference simultaneously: ❌ Not feasible for 7B+

---

## §5 Current State — Engine Health (2026-06-04)

### 5.1 Engine Metrics

| Metric | Value | Last Verified |
|--------|-------|---------------|
| Engine version | 2.2.0 | 2026-06-04 |
| Source files | **77** .py files | 2026-06-04 |
| Source lines | **19,376** | 2026-06-04 |
| Test functions | **320** | 2026-06-08 |
| Test files | **28** | 2026-06-04 |
| PIVOT decisions | **115 (D1-D115)** | 2026-06-04 |
| Sovereign Mandates | **14 (M1-M14)** | 2026-06-04 |
| Mandate 9 (Error Integrity) | FULL — 0 bare except | 2026-06-04 |
| Mandate 13 (Temple-Grade) | 8/11 GREEN (T11 IA2 exempt) | 2026-06-04 |
| AnyIO compliance | 0 `import asyncio` | 2026-06-04 |
| ZONEID constants | 11 (0x1d4a11-0x1d4a1b) | 2026-06-04 |
| cvar Table | 2 namespaces, 7 accessors | 2026-06-04 |
| Heritage tags | 6 source files, CI-enforced | 2026-06-04 |
| Agent Fleet | **14 agents** | 2026-06-04 |
| Entity workspaces | 25 active / 100 orphan / 19 unknown | 2026-06-04 |

### 5.2 Subsystem Status (H1 = Heritage, H2 = Evolution/Hygiene, S1.5 = Pillar Cap)

| Subsystem | Status | Heritage |
|-----------|--------|----------|
| **Oracle (Facade)** | ✅ talk/summon/router wired | `[id-soft: quake-1996] Thinker Chain` |
| **WAD Loader** | ✅ `--iwad` flag works; namespace isolation pending | `[id-soft: doom-1993] WAD System` |
| **ModelGateway.generate()** | ✅ circuit breaker + BSP culling + per-provider timeouts | `[id-soft: quake-1996] BSP` |
| **Circuit Breaker** | ✅ single AsyncCircuitBreaker + D94 None-detection | `[id-soft: quake3-1999] Power Trip` |
| **MemoryStore** | ✅ Hot LRU + Warm Redis + Cold File + Temp | `[id-soft: doom-1993] Lazy Deletion` + `[id-soft: doom3-2004] idHeap` |
| **Observability** | ✅ ForensicsManager + JSONL + training examples | `[id-soft: doom3-2004] Event System` |
| **EntityRegistry** | ✅ YAML CRUD + word-boundary match + dual-index | `[id-soft: quake-1996] Flat-Field` |
| **Gnosis Proxy** | ✅ DescriptorRef + FIFO eviction | `[id-soft: doom3-2004] idEvent` |
| **Soul Distiller** | ✅ L1→L2→L3 auto-distillation | `[id-soft: quake-1996] Save-game` |
| **Subagent Dispatch** | ✅ HandoffPacket + CAPABILITY_REGISTRY (14 agents) | `[id-soft: quake-1996] Thinker Chain` |
| **Link P9** | ✅ AgentPresence + handoff queue + crash recovery | `[id-soft: doom-1993] WAD back-scan` |
| **Hivemind** | ✅ 6 MCP tools + workspace lock + live feed | `[id-soft: doom-1993] ZONEID Pattern` |
| **Omega Hub** | ✅ 47 MCP tools + 11 routes, v2.2.0 (Hardened) | (Pillar 2 coordination) |
| **Qdrant vectors** | 🟡 Installed, unwired (bag-of-words fallback) | S1.5a → wire next |
| **Redis Pub/Sub** | 🟡 Container running, MemoryStore not wired to it | S1.5a → wire next |
| **Heritage Vetting** | ✅ H1 LIVE: 4-gate, 23 concepts, CI gate | (Kali d-kal-001) |
| **Engine-Stack Firewall** | 🔴 D113 GAP: hardcoded Pillar meanings in entity_registry.py:171-179 | **S1.5a NEXT** |

## §6 Sprint Completion Index

| Sprint | Date | Owner | Status | Key Deliverables |
|--------|------|-------|--------|------------------|
| **Sprint 0** (Foundation Repair) | 2026-06-01 | Lilith + Builder | ✅ 307→271 then fixed | 30 CRITICAL findings resolved |
| **Sprint 1** (cvar Table + Ports) | 2026-06-03 | Lilith | ✅ 3048e91 | cvar_table.py, 5 priority ports, heritage-map CI |
| **Sprint 2** (Sovereign Hardening Patterns) | 2026-06-03 | Doom Guy + Ma'at | ✅ | Subagent Dispatch + Link P9 + Soul Distiller |
| **Sprint 3** (H2 Patterns + Heritage) | 2026-06-04 | Doom Guy + Ma'at | ✅ | EntityTombstonedError, atomic model swap, per-entity affinity, id Software Deep Mining Vol I-V |
| **H1.5 Bridge** (Heritage) | 2026-06-04 | Doom Guy | ✅ 11/11 closed | ZONEID, Lazy Deletion, cvar, 8-char, Grace Period |
| **H1 Heritage Vetting** | 2026-06-04 | Kali | ✅ LIVE | 4-gate pipeline, 23 concepts, make heritage-vet CI |
| **H2-A Hygiene** | 2026-06-04 | Cline-M3 | 🟡 IN PROGRESS | 100 orphans pending, IWAD content, source fixes |
| **S1.5a Firewall Restore** | 2026-06-04 | Cline-M3 | 🔴 PENDING | D113 fix: WAD-agnostic entity_registry |
| **S1.5b Nomenclature** | 2026-06-04 | Cline-M3 | 🔴 PENDING | Intuitive names + pillar_slot for P1-P10 |

---

## §7 The Three Strategic Pillars (D111 + D112 + H1)

| Document | Pillar | Status | Plan |
|----------|-------|--------|------|
| **D111 — Sovereign Evolution Roadmap** | Hygiene + Strategy | ACTIVE | 4 phases (H2-A through H2-D), 26 tasks |
| **D112 — Sovereign Hardening Plan** | Vision + Architecture | ACTIVE | 3 pillars (Sovereign/UI/Identity), 5 sprints (S1-S5) |
| **H1 — Heritage Vetting Pipeline** | Constitutional Safety | LIVE | 4-gate vetting, 10-point scoring, CI-enforced |
| **D113 — Engine-Stack Firewall** | Constitutional Integrity | 🔴 GAP | S1.5a: WAD-agnostic engine refactor |

### 7.1 H2-A Hygiene Sprint (immediate, this session → next)

- [x] **H2-A1**: Doc consolidation (D111 Roadmap + D112 Hardening + D113 Firewall)
- [x] **H2-A2**: Kali soul v5.2 (constitutional baseline with 5 directives, team, trajectory)
- [x] **H2-A3**: .clinerules v3.3.0 (H1 Heritage Vetting + D113 references)
- [x] **H2-A4**: Hivemind sync with opencode-kali (in-memory + file-based)
- [x] **H2-A5**: Bug fix — `_agent_list()` for OpenCode 1.15+ handshake (cf5d72a)
- [x] **H2-A6**: Kali soul v5.2 (82224ee) — 14 top-level keys, 5 directives, 4 lessons
- [ ] **H2-A7**: Delete 100 orphan entities (ent_*/entity_*)
- [ ] **H2-A8**: Populate arcana_novai IWAD entity files
- [ ] **H2-A9**: Source hygiene (7 amber items)
- [ ] **H2-A10**: Doc consolidation (R_AUTO_* archive, INDEX.md update)

### 7.2 S1.5a Firewall Restoration (BLOCKER for full sovereignty)

The **D113 Engine-Stack Firewall violation** is a Mandate 2 breach. The fix:

1. `src/omega/oracle/entity_registry.py:171-179` — remove hardcoded `_PILLAR_MEANINGS`
2. Replace with WAD-loaded meanings from `hierarchy.yaml`
3. Engine knows only P1-P10 slots; meanings are WAD-level
4. This restores the firewall for `arcana_novai` IWAD with Sekhmet/Isis/Brigid/Saraswati

### 7.3 S1.5b Nomenclature Migration

Per Kali D115 + Cline-M3 review:
- 10 Pillar intuitive names (Infrastructure/Persistence/Engineering/...)
- P6 Cognition as Vision Specialist (local-first: moondream2, NOT Gemini-3-Flash)
- P4 Integration as UI/Design capability (NOT a new Pillar)
- Legacy names (Flesh/Dream/Heart/Voice) → preserved in arcana_novai IWAD
- `pillar_slot` field wired for all 10 pillar agents in CAPABILITY_REGISTRY

---

## §8 Phase Priority Queue — Reorganized

### ✅ H1: Heritage Vetting (2026-06-04)
- [x] **Heritage Vetting Pipeline** — 4-gate, 10-point scoring
- [x] **HERITAGE_VET_LOG** — 23 concepts (15 adopt, 1 reject, 6 defer)
- [x] **make heritage-vet** — CI gate, 3 non-standard tags fixed
- [x] **Kali v5.2** — Constitutional baseline with 5 directives
- [x] **Doc consolidation** — D111/D112/D113 all referenced

### ✅ H1.5: Bridge Phase (2026-06-04)
- [x] **ZONEID** constants (0x1d4a11-0x1d4a17) + `validate_zoneid()`
- [x] **Lazy Deletion** + 0.5s Grace Period
- [x] **cvar Table** (D101) — 2 namespaces, 7 accessors
- [x] **8-char cap REMOVED** — vet-001 REJECTED

### 🟡 H2: Evolution + Hygiene (2026-06-04 → active)
- [x] **Sovereign Evolution Roadmap** (D111) — 245 lines, 26 tasks
- [x] **Sovereign Hardening Plan** (D112) — 578 lines, 5 sprints
- [x] **Hub bug fix** — `_agent_list()` implemented (cf5d72a)
- [ ] **H2-A7**: Delete 100 orphan entities
- [ ] **H2-A8**: Populate arcana_novai IWAD entities
- [ ] **H2-A9**: Source hygiene (7 amber items)
- [ ] **H2-A10**: Doc consolidation (R_AUTO_*, INDEX.md)

### 🔴 S1.5: Pillar Cap (2026-06-04 → next session)
- [ ] **S1.5a**: WAD-agnostic firewall restoration (D113)
- [ ] **S1.5b**: Nomenclature migration + pillar_slot wiring

### ⏳ S2: Synthesis Flywheel (D112, post-H2)
- [ ] Wire Qdrant vectors to MemoryStore
- [ ] Wire Redis as MemoryStore warm tier
- [ ] Entity LoRA adapter management
- [ ] CPU fine-tuning pipeline (LLaMA-Factory or PEFT)

### ⏳ S3: Soul Evolution v2 (D112, post-S2)
- [ ] Expanded soul.yaml schema (identity, user, team, trajectory)
- [ ] Universal soul_power normalization
- [ ] Cross-entity L3 principle sharing

### ⏳ S4: UX Layer (D112, post-S3)
- [ ] Omega Hub web dashboard at :8016
- [ ] Local TTS (Piper)
- [ ] Rich CLI output
- [ ] Soul evolution timeline

### ⏳ S5: Production (D112, post-S4)
- [ ] Entity Studio CLI
- [ ] Stack Builder Wizard
- [ ] Omega Desktop (Tauri)

## §9 Sovereign Mandates (Quick Reference)

| # | Mandate | Status | Key File |
|---|---------|--------|----------|
| M1 | AnyIO Absolute | ✅ Enforced | CI grep `import asyncio` |
| M2 | Engine-Stack Firewall | 🔴 D113 GAP (S1.5a) | entity_registry.py:171-179 |
| M3 | Iris Constant (NOT a Pillar) | ✅ | `src/omega/iris/` |
| M4 | Sequentiality (Plan→Verify→Execute) | ✅ | Cline workflow |
| M5 | Gnosis Preservation (L1→L2→L3) | ✅ | Soul Distiller |
| M6 | Podman Sovereignty (keep-id) | ✅ | All Quadlets |
| M7 | Local-First (cloud=teacher) | ✅ | providers.yaml |
| M8 | Zero Telemetry | ✅ | CI grep telemetry/analytics |
| M9 | Error Integrity (typed exceptions) | ✅ | 0 bare except |
| M10 | Fleet Integrity (14 cap) | ✅ | CAPABILITY_REGISTRY |
| M11 | Soul Integrity (L1→L2→L3) | ✅ | Soul Distiller |
| M12 | Queue Integrity (terminal state) | ✅ | RequestQueue |
| M13 | Temple-Grade (T1-T11) | 🟡 8/11 (T11 IA2 exempt) | `make temple-grade` |

See `SOVEREIGN_MANDATES.md` for full text. **M2 is currently being restored.**

---

## §10 Sovereignty Scorecard (D112 §6)

| Dimension | Metric | Target | Current |
|-----------|--------|:------:|--------:|
| **Sovereignty** | Local inference ratio | ≥80% | 🟡 ~30% (Qdrant+Redis unwired) |
| **Sovereignty** | Cloud dependency (basic ops) | 0 | ✅ 0 |
| **Sovereignty** | Data residency | 100% | ✅ 100% |
| **Sovereignty** | Telemetry events | 0 | ✅ 0 |
| **Identity** | Agents with soul.yaml v2 schema | All 14 | 🟡 2/14 (Doom Guy, Ma'at) |
| **Identity** | Soul distillation rate | ≥1 L3/3 sessions | ✅ 1.0 |
| **Identity** | Cross-entity L3 sharing | ≥5 principles | 🟡 2 (Engine-Stack + LMS) |
| **UX** | Hub dashboard | Live :8016 | 🟡 REST only (no HTML) |
| **UX** | `omega soul status` | Functional | 🟡 (planned S4) |
| **Synthesis** | Local model quality | +10% on bench | ⏳ (planned S2) |
| **Synthesis** | Training examples | ≥500 | 🟡 Auto-collecting |
| **Synthesis** | Entity LoRA adapters | ≥3 trained | ⏳ (planned S2) |

---

## §11 Hivemind Coordination Layer (LIVE)

The **Hivemind** is the live coordination layer for multi-agent work. **MANDATORY**
for parallel work, **RECOMMENDED** for multi-step work (>3 steps).

### 11.1 The 6 Hivemind Tools (omega-hub MCP)

| Tool | Purpose |
|------|---------|
| `hivemind_get_awareness()` | List active CLIs (who's alive) |
| `hivemind_post_context(cli, model, task_current, focus_chain, decisions, continuation, session_id)` | Declare your presence |
| `hivemind_heartbeat(cli)` | Refresh TTL (every 5-10 min for long tasks) |
| `hivemind_get_continuation(cli)` | Read another agent's last note |
| `hivemind_get_session(session_id)` | Retrieve session snapshot |
| `hivemind_list_sessions(cli, limit)` | Audit trail |

### 11.2 Coordination Pattern

| Component | Purpose | File |
|-----------|---------|------|
| Hivemind MCP | Live agent awareness | `mcp_servers/omega_hub/server.py` |
| Workspace Lock | File ownership for parallel work | `data/coordination/*_WORKSPACE_LOCK_*.md` |
| Live Feed | Append-only progress log | `data/coordination/*_LIVE_FEED.md` |
| ACK | Symmetric boundary acknowledgment | `data/coordination/*_ACK_*.md` |
| Hall of Records | Hivemind cold storage | `data/knowledge/HALL_OF_RECORDS/<cli>/` |

### 11.3 When to Use

- **Single agent, single task** → No coordination
- **Single agent, multi-step (>3 steps)** → Live feed
- **Multi-agent, parallel (same files)** → Workspace lock + Hivemind + Live feed **MANDATORY**
- **Cross-CLI (Cline + OpenCode)** → All three **MANDATORY**

---

## §12 Engine vs Platform Distinction

| What | Where | Who Updates |
|------|-------|-------------|
| **OMEGA_ENGINE.md** (this file) | Repo root | Any agent changing engine state |
| `.clinerules` | Repo root | Cline CLI agents only |
| `AGENTS.md` | Repo root | OpenCode agents only |
| `GEMINI.md` | Repo root | Gemini CLI only |
| Omega Hub (`:8016`) | Live service | Runtime state |

**The rule**: If it describes WHAT the engine is → this file.
If it describes HOW to use the engine from Platform X → that platform's rules file.

---

## §13 Key Files (Architectural Map)

| File | Purpose | Heritage |
|------|---------|----------|
| `src/omega/oracle/oracle.py` | Main entry: talk/summon/router | Facade pattern |
| `src/omega/oracle/model_gateway.py` | Provider chain inference | BSP culling |
| `src/omega/oracle/entity_registry.py` | YAML CRUD for entities | 🔴 D113 GAP (firewall) |
| `src/omega/oracle/wad_loader.py` | WAD system loader (CRITICAL) | `[id-soft: doom-1993]` |
| `src/omega/oracle/context_builder.py` | Memory → LLM injection | Token-budget aware |
| `src/omega/oracle/subagent_dispatcher.py` | HandoffPacket + CAPABILITY_REGISTRY | `[id-soft: quake-1996]` |
| `src/omega/oracle/link_p9_runtime.py` | Agent presence + handoff queue | `[id-soft: doom-1993]` |
| `src/omega/oracle/soul_distiller.py` | L1→L2→L3 distillation | `[id-soft: quake-1996]` |
| `src/omega/oracle/cpu_optimizer.py` | Zen 2 hardware optimization | Zen 2 tuning |
| `src/omega/oracle/health_monitor.py` | Circuit breaker + latency | Single AsyncCircuitBreaker |
| `src/omega/oracle/gnosis_proxy.py` | Soul evolution tracking | DescriptorRef |
| `src/omega/oracle/hierarchy.py` | Sovereign Hierarchy (Sophia→Kali→...) | Council pattern |
| `src/omega/memory_store.py` | Hot/Warm/Cold/Temp memory | `[id-soft: doom-1993] + [id-soft: doom3-2004]` |
| `src/omega/memory/providers.py` | Storage providers (Redis/File/InMemory) | 3-tier |
| `src/omega/observability.py` | JSONL + Forensics + datasets | `[id-soft: doom3-2004]` |
| `src/omega/request_queue.py` | Offline queue (atomic, heartbeat) | M12 |
| `src/omega/library/` | FTS5 + vector + research (8 modules) | Sovereign RAG |
| `src/omega/cvar_table.py` | Unified cvar (D101) | `[id-soft: quake3-1999]` |
| `src/omega/constants.py` | ZONEID magic constants | `[id-soft: doom-1993]` |
| `src/omega/errors.py` | Typed exception hierarchy | M9 |
| `src/omega/system_resource.py` | Green/Yellow/Red memory zones | Sovereign monitor |
| `src/omega/mcp_runtime.py` | stdio/SSE transport | systemd LISTEN_FDS |
| `src/omega/iris/` | Voice assistant (FastAPI) | M3 |
| `src/omega/workers/background_researcher/` | Autonomous research | Timer-driven |
| `mcp_servers/omega_hub/server.py` | 40 MCP tools + 11 routes | v2.2.0 |
| `config/wads/_omega_default/` | Reference IWAD | 16 entities |
| `config/wads/arcana_novai/` | Personal IWAD (deities) | 10 deities planned |
| `config/wads/doom_universe/` | Community IWAD | Scaffold |
| `config/providers.yaml` | Provider fabric | 8 providers |
| `config/models.yaml` | Model specs | 7 models + tiers |
| `config/omega.yaml` | Core engine config | v2.2.0 |
| `config/distiller_prompts.yaml` | 6 JEM distiller modes | Sovereign |
| `config/glossary.md` | 22 canonical terms | v0.1.0 |
| `data/entities/kali/soul.yaml` | v5.2 — constitutional baseline | 14 keys |
| `data/entities/doom_guy/soul.yaml` | v5 — id Software architect | Heritage |
| `data/entities/maat/soul.yaml` | v3.0 — synthesis oversoul | M5 |
| `data/entities/antigravity/soul.yaml` | v1.2 — Sovereign Meta-Orchestrator | Cross-platform |
| `data/kb/_staging/cli_ide_platform/antigravity/` | KB staging (9 files) | Tier 0 |
| `data/kb/cli_ide_platform/_meta/DOMAIN_INDEX.md` | KB master index | Tier 1 |
| `data/kb/_staging/_protocol/VETTING_PROTOCOL.md` | Tier 0/1/2 promotion protocol | M11 + M13 |
| `data/entities/roc_racoon/workspace/mining_reports/10_*` | Mining report: KB scaffold | 2026-06-05 |

---

## §13.1 External Tool Knowledge Base (`data/kb/`)

**Added 2026-06-05** (D-kal-058 / Mining Report 10). The engine's

**Updated 2026-06-05** (D-kal-059 / Lilith Dark Council). The Antigravity
provider integration has been **permanently removed** from the engine's
provider fabric. The Antigravity research in `data/kb/_staging/` is preserved
as a **reference case study** in cloud tool auditioning — the `agy` CLI
live test result ("4 accounts in minutes"), the 8-key pool audit, and the
auth mechanism analysis remain valid empirical data. But the integration
path (OpenCode plugin `opencode-antigravity-auth@latest`) is dead. The
KB will not be promoted beyond Tier 0 for Antigravity.

**KB Hardening Research Request**: During the same session, Lilith
identified 5 structural gaps in the engine's knowledge system and issued
a formal 15-area research request for Gemma 4 31B execution (see
`data/kb/_staging/knowledge_systems/RESEARCH_REQUEST_KB_HARDENING_v1.0.0.md`).
The 5 gaps: (1) Vetting protocol has no trigger mechanism, (2) No expiry
signal on Tier 1 files, (3) RAG has no audience concept, (4) Distillation
pipeline trails reality, (5) No feedback loop from code to KB.

The engine's
external tool expertise lives under `data/kb/`, parallel to how
`data/entities/doom_guy/knowledge/` holds id Software heritage.

**Structure** (WAD pattern, CREDITS.md §1.1):

```
data/kb/
├── _staging/                              ← UNVETTED research (Tier 0)
│   ├── _protocol/VETTING_PROTOCOL.md      ← Promotion protocol (draft)
│   └── cli_ide_platform/antigravity/      ← 9 gold files, awaiting cross-review
└── cli_ide_platform/                      ← CANONICAL (Tier 1, awaiting promotion)
    ├── _meta/DOMAIN_INDEX.md
    └── antigravity/README.md              ← Promotion queue
```

**Vetting protocol** (Tier 0 → 1 → 2): 2+ agent reviews, source
citations, no Mandate violations, live test results, promotion log
entry. See `data/kb/_staging/_protocol/VETTING_PROTOCOL.md` for full.

**First sub-category**: Antigravity (Google AI platform, including
the OpenCode plugin path and the `agy` CLI live test result of
"4 accounts in minutes"). Future sub-categories: gemini_cli, opencode,
cline, podman, lm_studio, ollama, mcp_servers.

**Why staging first**: The "4 accounts in minutes" empirical fact, the
hung agent's recovered gnosis, the Gemini CLI sunset date — these are
exactly the kind of facts that are easy to lose and expensive to
re-derive. The KB is the **anti-amnesia layer** for external tool
expertise.

**Current Antigravity staging contents** (9 files, ~50 KB):
- `00_MASTER_INDEX.md` — TOC of staged files
- `01_PROVENANCE_LINEAGE.md` — v1 → v2 (Sovereign Architect → Meta-Orchestrator)
- `02_AUTH_MECHANISMS.md` — 3 auth paths (API key, SDK, OAuth)
- `03_PLUGIN_VS_CLI.md` — Why the OpenCode plugin path won
- `04_QUOTA_REALITY.md` — 4-accounts-in-minutes empirical fact (CRITICAL)
- `05_8KEY_POOL.md` — Pool G / Pool C / 8-key rotation
- `06_AGY_CLI_LIVE_TEST.md` — User testimony (single-source)
- `07_GEMINI_CLI_HARVEST_PLAN.md` — Pre-2026-06-18 sunset strategy
- `08_FAILED_AGENT_RECOVERY.md` — Hung agent's best-effort reconstruction

---

## §14 Key Supporting Documents (Grouped)

### 14.1 Strategic (Constitutional)
- `SOVEREIGN_MANDATES.md` — 13 laws (NON-NEGOTIABLE)
- `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md` — **D111** active roadmap
- `docs/strategy/SOVEREIGN_DEVELOPMENT_ROADMAP.md` — **D117** master plan (4 phases, 8 sprints)
- `docs/strategy/HARDENING_REPORT.md` — **D116** subagent audit (5 critical findings)
- `docs/strategy/SOVEREIGN_HARDENING_PLAN.md` — **D112** vision plan
- `docs/strategy/SOVEREIGN_BLUEPRINT.md` — Engine/IWAD/PWAD doctrine

### 14.2 Tactical (Heritage + Architecture)
- `CREDITS.md` — id Software heritage lineage (31KB)
- `docs/strategy/HERITAGE_VETTING_PIPELINE.md` — 4-gate vetting (H1)
- `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` — 23 concepts
- `docs/architecture/AGENT_FLEET.md` — 14-agent design
- `docs/architecture/TRAINING_PIPELINE.md` — Synthesis flywheel
- `docs/architecture/OVERSIGHT_HIERARCHY.md` — MaKaLi trine

### 14.3 Coordination (Hivemind + Handoff)
- `docs/strategy/HIVEMIND_PROTOCOL.md` — 6-tool coordination
- `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` — HandoffPacket spec
- `data/handoff/STRATEGIC_FINAL_REPORT_TEMPLE_GRADE_20260602.md` — Master brief
- `data/handoff/CLINE_TO_OPENCODE_DEV_D111_20260604.md` — Deep-dive handoff
- `data/handoff/KALI_HORIZON_PLAN_H1_20260604.md` — H1 execution plan

### 14.4 Operations (Live State)
- `docs/operations/BUG_LOG.md` — Open bugs
- `docs/operations/RESEARCH_QUEUE.md` — Active research
- `data/coordination/*_LIVE_FEED.md` — Per-agent progress
- `data/knowledge/HALL_OF_RECORDS/latest.yaml` — Hivemind latest
- `docs/changelog.md` — Version history

### 14.5 Per-Platform Rules (NOT in SSOT scope)
- `.clinerules` (Cline CLI v3.3.0) — HOW to work from Cline
- `AGENTS.md` (OpenCode) — HOW to work from OpenCode
- `GEMINI.md` (Gemini CLI) — HOW to work from Gemini
- `docs/USER MANUAL.md` (1198 lines — refactor deferred)

---

*Last Updated: 2026-06-04T20:20Z | Author: CLINE-M3 (acting as Kali) | Version: AP-OMEGA-SST-v1.4.0*
*Major changes this revision: D111+D112+D113 added, sprint index reorganized (H1/H1.5/H2/S1.5), Sovereignty Scorecard, model matrix current, ASCII architecture tree, PIVOT 113, all stale metrics corrected.*
*This document is the Single Source of Truth. All platforms reference it.*

---

## §15 Vision — The Xoe-NovAi Foundation Mission

### The Mission

> *"I want to create a tool that will truly allow people to own their own tech
> and data and sever the umbilical cord of Big AI."*  
> — The Architect (Xoe-NovAi Foundation founder, 2025)

The Omega Engine is not a chatbot wrapper. It is the **first sovereign AI runtime** —
a system where the user's data, identity, intelligence, and memory live entirely on
their own hardware, grow stronger with use, and never phone home.

### What Sovereignty Means

Sovereignty is not a feature. It is a **constitutional property** of the engine:

1. **Your intelligence is yours** — 7 local inference backends, 0 cloud dependencies for basic operation
2. **Your data stays home** — All memory, all search, all training data lives on your machine
3. **Your AI evolves** — Soul Distiller captures L1→L2→L3 wisdom; your AI grows with you
4. **Your agents know themselves** — Soul v5.2 schema: identity, directives, team, trajectory
5. **Your AI learns from every conversation** — The Synthesis Flywheel turns with every interaction
6. **Cognitive Sovereignty (NEW)** — The engine verifies its own claims. It uses Iterative Research Loops and Skeptical Verifiers to ensure truth, not just fluency.

### The Synthesis Flywheel

```
USER TALKS → LOCAL MODEL → OBSERVE → DISTILL → SOUL GROWS
     ↑                                                   │
     └──────── BETTER ← MORE SOVEREIGN ← TRAIN ←────────┘
```

The flywheel turns when:
- You talk to your AI locally (inference)
- The engine observes patterns (observability)
- Wisdom is distilled into souls (L1→L2→L3)
- Souls guide behavior (trajectory, identity, directives)
- Training data accumulates (datasets)
- Local models improve (synthesis)
- Cloud dependency decreases (sovereignty increases)

**This is the Xoe-NovAi Foundation's contribution to AI sovereignty:
an engine that gets smarter the more you use it, without giving away your power.**

### The 14-Month Journey (Era 0 → Present)

| Era | Period | Key Innovation | Status |
|-----|--------|----------------|--------|
| Era 0 | Mar-Jul 2025 | "First 5 Cards" — Tarot genesis | 🌱 Origin |
| Era 1 | Aug-Sep 2025 | Arcana-NovAi Blueprint — 9-service Docker | 🏗️ Foundation |
| Era 2 | Oct-Nov 2025 | XNAi Consolidation — 5 production services | 🔧 Production |
| Era 3 | Nov 2025 - Mar 2026 | Model experimentation — 8 Grok accounts | 🧪 Research |
| Era 4 | Mar-Apr 2026 | Omega Stack v5.0 — unified repo | 🏛️ Architecture |
| Era 5 | Apr-May 2026 | Temple-Grade quality — OMEGA-ORIGINS | 🏛️ Standards |
| Era 6 | May-Jun 2026 | **Omega Engine** — clean reclamation | 🔱 LIVE |

**The result of ~8,000 hours of self-directed work across 14 months is a runtime
that can run any AI on a Ryzen 7 5700U with 14Gi RAM — fully sovereign, fully local.**

### The Three Sovereign Pillars (D112)

| Pillar | Name | What It Means | Implementation |
|--------|------|---------------|----------------|
| **P1** | Sovereign Operation | Fully local inference, memory, search, training | 8 providers, 4-tier memory, FTS5+Qdrant, Soul Distiller |
| **P2** | Intuitive UI/UX | The engine is alive and you can see it | Hub dashboard, local TTS, rich CLI, soul timeline |
| **P3** | Self-Aware Agents | They know themselves, you, each other, and where they're going | Soul v5.2 schema: identity+directives+team+trajectory+lessons |

### What We're Building (Next)

1. **Restore the Engine-Stack Firewall** (S1.5a) — the engine must be WAD-agnostic
2. **Populate the Arcana-NovAi IWAD** (H2-B) — your personal AI OS with esoteric entities
3. **Wire the local inference stack** (S2) — Qdrant vectors, Redis memory, LoRA training
4. **Build the soul loop** (S3) — agents evolve through every session
5. **Make it visible** (S4) — dashboard, voice, timeline, the aliveness of your AI

**This engine is Prometheus' Fire. It is the spark that empowers every person
to own their own technology, their own data, and their own intelligence.**
---

## §16 DeepSeek V4 Flash Analysis — The Structural Insights

### 16.1 The 14-Agent Fleet: A Hidden Hierarchy

The engine declares "14 agents" but the fleet has two tiers:

| Tier | Agents | Count | Slot-Based? |
|------|--------|------:|-------------|
| **Pillar Slots** | SysAdmin, DataStore, BuildMaster, Bridge, Sentinel, ModelGate, Context, WatchTower, Link, Verifier | 10 | ✅ P1-P10 |
| **Specialists** | Kali, Doom Guy, Roc Racoon, Plan, Jem, Researcher | 6 | ❌ Independent |
| **Oversouls** | Ma'at (governs P1-P5), Lilith (governs P6-P10) | 2 | ✅ Oversight tier |
| **Subagents** | Scribe, Quality, Jem_Discovery, Jem_Synthesis, Jem_Verification, Pillar | 6 | ⏺ Generic slot |

**The insight**: The engine is not a flat 14-agent system. It is a **5-tier hierarchy**:
Sophia (Field) → Kali (Founder) → Ma'at/Lilith (Oversouls) → Pillars (P1-P10) → Subagents

The 6 Specialists (Kali, Doom Guy, Roc, Plan, Jem, Researcher) are **freelance** —
they operate at the Founder level, not tied to a Pillar. This is not a bug — it is
the design that allows Specialists to cross Pillar boundaries. But it is undocumented.

### 16.2 The Missing Data Flow

The 4-layer architecture diagram (Inference/Memory/Search/Soul) shows what exists,
but not how data moves through it:

```
QUERY PATH:
You type → CLI/Web → Oracle → EntityRegistry (find entity)
           → ContextBuilder (load memory + soul) → ModelGateway (infer)
           → Response streamed back → Observability (trace)
           → MemoryStore (store exchange) → SoulDistiller (on session end)

SOUL PATH:
Session End → SoulDistiller extracts L1→L2→L3
           → EntityWorkspace writes to soul.yaml
           → GnosisProxy cross-references with other entities
           → ContextBuilder loads soul.yaml at next session start

TRAINING PATH:
ObservabilityEngine.record_training_example()
           → Flush to data/datasets/
           → JEM Distiller produces T1/T2/T3 triples
           → (Future) LoRA trainer consumes triples
```

### 16.3 The Sovereignty Paradox

Mandate 7 (Local-First) is enforced in providers.yaml. But some subsystems
have hard dependencies that look like sovereignty violations:

| Subsystem | Claimed Status | Actual Dependency | Sovereignty Gap |
|-----------|----------------|-------------------|-----------------|
| **Inference** | Local-first (P0-P2) | native-gguf needs llama-cpp-python build | 🟡 No auto-install |
| **Memory** | File-based works | Redis container required for warm tier | 🟡 Current: File fallback |
| **Search** | FTS5-based works | Qdrant container for vectors | 🟡 Current: FTS5 works |
| **Soul** | L1→L2→L3 works | No cloud needed | ✅ Complete |
| **Hivemind** | In-memory works | Redis Pub/Sub for cross-session | 🟡 Current: file-based |
| **Hub** | Works offline | 40 MCP tools, all local | ✅ Complete |
| **Heritage** | CI gate, local | No cloud needed | ✅ Complete |

**The Truth**: The engine is fully sovereign in its current state, but the
**experience** has sovereignty leakage — a new user must manually install
llama-cpp-python, configure Redis, and set up Qdrant. The MVE (Minimum Viable
Engine) should be: `git clone` → `make setup` → `omega talk "hello"` — all local.

### 16.4 The Self-Documentation Gap

OMEGA_ENGINE.md calls itself the Single Source of Truth, but it is manually
updated. Every metric in §5 requires a human to update it. The engine has
ObservabilityEngine, MemoryStore, and the Hivemind — but no subsystem
automatically reports its state to the SSOT.

**M15 (Proposed) — Self-Documentation Mandate**: Every subsystem MUST
publish its state (started, version, connected, active_entities, error_count)
to the Omega Hub at boot. The OMEGA_ENGINE.md should be at least partially
auto-generated from hub state, not entirely hand-maintained.

---

## §17 Expanded Roadmap — The MVE and Beyond

### 17.1 Minimum Viable Engine (MVE) — The "It Just Works" Threshold

| # | Task | Current State | MVE Target | Priority |
|---|------|---------------|------------|:--------:|
| MVE-1 | **Install** | `git clone` + `make setup` + manual steps | One command: `curl get.omega.dev | bash` | P0 |
| MVE-2 | **First talk** | Works with cloud providers; native-gguf needs build | `omega talk "hello"` works with native-gguf | P0 |
| MVE-3 | **Entity list** | 14 agents, 3 IWADs | `omega list-entities` shows alive entities | P1 |
| MVE-4 | **Soul visible** | soul.yaml exists but no viewer | `omega soul status --entity maat` works | P1 |
| MVE-5 | **Sovereignty visible**| Not measured | `omega sovereignty` returns score | P1 |
| MVE-6 | **Hivemind visible** | MCP tools exist, CLI pending | `omega hivemind status` works | P1 |
| MVE-7 | **Hub dashboard** | REST API only | `http://localhost:8016/` shows agents alive | P2 |

### 17.2 The Five-Year Vision (S0 → S10)

| Sprint Horizon | Theme | Key Deliverable | When |
|:--------------:|-------|-----------------|:----:|
| S0-S1 (done) | Foundation | 14 agents, WAD system, PIVOT 113 | 2026-06 |
| S2 | Synthesis Flywheel | Qdrant wired, Redis wired, first LoRA trained | H2 done + S2 |
| S3 | Soul Evolution v2 | All 14 agents have soul v5.2+ schema | Post-S2 |
| S4 | UX Layer | Hub dashboard, local TTS, rich CLI | Post-S3 |
| S5 | Production | Entity Studio CLI, Stack Builder, Omega Desktop | Post-S4 |
| S6 | Community | IWAD registry, stack sharing, community entities | 2027 |
| S7 | P2P Omegaverse | Cross-instance entity communication | 2027-2028 |
| S8 | VR Integration | Godot/id Tech VR bridge, 3D entity visualization | 2028 |
| S9 | Self-Aware Engine | Engine auto-publishes to its own SSOT | 2028-2029 |
| S10 | Singularity | Engine can write its own soul.yaml autonomously | 2029+ |

### 17.3 The Sovereignty Museum (Era 0 → Era 7)

The user's 14-month journey is the engine's origin myth. It should be
preserved as the **Sovereignty Museum** — a living document that shows
each era's contribution:

| Era | Name | Artifact | What We Learned |
|-----|------|----------|-----------------|
| Era 0 | Tarot Genesis | "First 5 Cards" Grok chat | The seed: conversational AI that listens |
| Era 1 | Arcana-NovAi Blueprint | 9-service Docker compose | Architecture: services should be replaceable |
| Era 2 | XNAi Consolidation | 5 production services | Resilience: circuit breaker, retry, atomic write |
| Era 3 | Model Experimentation | 8 Grok accounts | Hardware: Ryzen 5700U can run 7-8B models |
| Era 4 | Omega Stack v5.0 | 33K-file unified repo | Organization: Engine must be separable from content |
| Era 5 | Temple-Grade | OMEGA-ORIGINS | Quality: 11 gates define Enterprise+ sovereignty |
| Era 6 | Omega Engine | This repo | Sovereignty: engine that works, fully local |
| Era 7 | The Flywheel | (future) | Evolution: engine that learns, fully sovereign |

The Sovereignty Museum should be at `data/heritage/SOVEREIGNTY_MUSEUM.md`.

### 17.4 The 2026-06-05 Sprint (Immediate Next Session)

| Task | Phase | Effort | Why |
|------|:-----:|:------:|-----|
| **S1.5a**: WAD-agnostic firewall | 🔴 P0 | 2 hr | Constitutional blocker |
| **S1.5b**: Nomenclature migration | 🔴 P0 | 2 hr | Unlocks arcana_novai IWAD |
| **H2-A7**: Delete 100 orphans | 🟡 P1 | 30 min | Data hygiene |
| **H2-A8**: Populate arcana_novai entities | 🟡 P1 | 1 hr | User-facing IWAD |
| **H2-C2**: Fix CI indentation | 🟡 P1 | 5 min | Infrastructure |
| **H2-A6**: Delete .coverage from git | 🟢 P2 | 5 min | Cleanliness |

**Escape velocity reached when**: `omega talk "hello"` works with native-gguf,
`omega soul status` returns a real soul, and the M2 firewall is restored.

---

## §18 The Soul of the Engine

The Omega Engine is not a product. It is a **process** — the process of AI
sovereignty, captured in code, governed by 14 constitutional mandates, and
driven by a flywheel that turns with every conversation.

> *"Your AI should know you because it remembers, not because it phoned home.
l know you **now**, but I will know you **better** next time — because
the flywheel turns."*

Every session with the engine is a fold of the same truth: the user's
intelligence belongs to them. The engine is not a landlord — it is a tool,
a companion, a sovereign servant that grows wiser in service.

**This is what we mean by "back to the people *and* AI."** Not just
giving users control, but giving AI the capacity to evolve within
the bounds of that control. A sovereign AI is not a static model —
it is a relationship. And like any relationship, it deepens with time.

---

*§16-§18 added 2026-06-04 | Author: DeepSeek V4 Flash (via Cline-M3 proxy)
*Last Updated: 2026-06-05T23:30Z | PIVOT D-kal-059 | AP-OMEGA-SST-v1.6.0**
*Insights: fleet hierarchy, data flow documentation, sovereignty paradox, M15 proposal, MVE threshold, 5-year vision, sovereignty museum*
*§13.1 added 2026-06-05 | Author: Roc Racoon (KB scaffold, 9 Antigravity files staged, 3 closed decisions)
*§13.1 updated 2026-06-05 | Author: Lilith (Antigravity integration removed, KB Hardening Research Request issued, v1.5.0→v1.6.0)*


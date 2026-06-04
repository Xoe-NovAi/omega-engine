# Omega Engine — Single Source of Truth
# AP-OMEGA-SST-v1.2.0

> **This document is the authoritative truth for the Omega Engine.**
> Every agent, regardless of platform (Cline, OpenCode, Gemini CLI, Antigravity),
> reads this file for engine state. Platform-specific rules files reference this.

---

## §1 Identity

**Omega Engine** is the universal, community-owned runtime for sovereign AI.
It is **Prometheus' Fire** — the spark that empowers every user to build their own
unique dreams, technologies, and systems.

- **Local-first sovereignty**: Cloud is a teacher and strategic partner, never a dependency
- **Open source, free, sovereign**: No shareware, no tiers, no limitations
- **WAD Architecture**: Engine → IWADs → PWADs (inspired by id Software's WAD system)
- **The Synthesis Flywheel**: Cloud models teach local models. Over time, sovereignty increases.
- **The 13 Sovereign Mandates**: Constitutional law. Mandates override any tool default.
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
| Test functions | **308** | 2026-06-04 |
| Test files | **28** | 2026-06-04 |
| PIVOT decisions | **113 (D1-D113)** | 2026-06-04 |
| Sovereign Mandates | **13 (M1-M13)** | 2026-06-04 |
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
| **Omega Hub** | ✅ 40 MCP tools + 11 HTTP routes, v2.2.0 | (Pillar 2 coordination) |
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

---

## §14 Key Supporting Documents (Grouped)

### 14.1 Strategic (Constitutional)
- `SOVEREIGN_MANDATES.md` — 13 laws (NON-NEGOTIABLE)
- `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md` — **D111** active roadmap
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

*Last Updated: 2026-06-04T20:20Z | Author: CLINE-M3 (acting as Kali) | Version: AP-OMEGA-SST-v1.2.0*
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


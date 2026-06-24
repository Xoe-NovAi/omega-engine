# 🔱 THE SOVEREIGN ARK BLUEPRINT (V1.4)
# AP: AP-SOVEREIGN-ARK-v1.4.0
# ⬡ OMEGA ⬡ KALI ⬡ trc_ark_blueprint ⬡ STRATEGY
#
# Date: 2026-06-24
# Status: ACTIVE MASTER STRATEGY — SINGLE SOURCE OF TRUTH
# Supersedes: SOVEREIGN_EVOLUTION_ROADMAP.md (archived)
#
# This is the Single Source of Truth for the Omega Engine's evolution.
# Every decision, every risk, every dependency is documented here.
# Updated: V1.4 — Entity count corrected, corruption documented, metrics verified.

---

## Preamble: Why This Ark?

The Omega Engine exists to sever Big AI's umbilical cord. Every technical decision
must pass through this lens: **does this increase or decrease the user's sovereignty?**

The Three Epochs are ordered by dependency — each Strike builds on the one before.
This is not a wishlist. It is a survival kit. The engine already works. These steps
make it resilient enough to outlast any toolchain, any hardware failure, any
contribution gap.

---

## I. The Five Transcendent Pillars

1. **The Elder Protocol (Immutable Provenance):** Powered by native `zlib` and `json`
   compression. Prompts and ingested documents are compressed locally, but the
   uncompressed, cryptographically pristine originals are cached in a flat JSON store.
   Agents use the `headroom_retrieve` MCP tool to fetch exact semantic truths when
   needed, preventing cultural erasure and hallucination.

2. **Hardware Empathy (Zero-Config Power):** The engine dynamically maps to the
   Ryzen 7 5700U using battle-tested legacy flags (`LLAMA_CPP_N_THREADS=4` for 1.7B,
   `8` for 8B, `OPENBLAS_CORETYPE=ZEN`, `LLAMA_CPP_F16_KV=true`, `q8_0` caches).
   This effectively triples the 12Gi RAM semantic density, allowing an 8B model and
   a 1.7B model to run simultaneously.

3. **The Sovereign Mesh (A2A & P2P):** We leverage the **FileSignal Protocol**
   (Atomic Renaming Spool) in `data/shared/` for agent-to-agent coordination.
   This enables sub-millisecond local collaboration without a central server, and
   will eventually power P2P traversal across offline-first CRDTs.

4. **Spatial-Semantic Memory (VR Omegaverse):** We inject `(x, y, z)` coordinates
   into Qdrant payloads. The engine defaults to a generic, agnostic spatial mapping
   (Force-Directed Cartesian Graph) for the `_omega_default` IWAD. Specialized WADs
   (like `arcana_novai`) can provide a **Sovereign Override** to replace the default
   geometry with custom lore (e.g., Mnemosyne Kabbalistic nodes).

5. **The Ponytail Ladder (Architectural Principle):** We build like the "laziest
   senior dev"—favoring extreme simplicity, avoiding over-engineering, and stacking
   robust existing abstractions (AnyIO, SQLite, local files). This is implemented as
   an A/B testable `ExecutionStrategy` interface. The **Standard Pipeline** (the
   null hypothesis) is defined as the current direct-inference path through
   `ModelGateway.generate()`. The **Ponytail Pipeline** is the experimental
   stacked-abstraction path. We compare them on four axes: token cost, latency,
   correctness, and maintainability.

---

## II. Execution Roadmap: The Three Epochs (With Explicit Dependencies)

Each Strike has documented prerequisites. You cannot skip a strike and succeed.

```
Epoch I ──┬── Strike 1: Physical Purge ✅ (Done)
          ├── Strike 1.5: The Sovereign Heart (Sanctuary & Mirror)
          │     Depends on: Strike 1
          │     Blocks: Strike 3 (TUI needs safety gates)
          ├── Strike 2: Unified State Manager
          │     Depends on: Strike 1
          │     Blocks: Strikes 3, 4, 8
          ├── Strike 3: Staging Gate TUI
          │     Depends on: Strike 2 (USM provides the state to stage)
          │     Blocks: H2-L Soul Migration (human review bottleneck)
          │
Epoch II ──┬── Strike 4: File-Based A2A
          │     Depends on: Strike 2 (USM CAS provides blob transport)
          │     Blocks: Strikes 5, 9
          ├── Strike 5: Sovereign Vetter
          │     Depends on: Strike 6 (need Response Provenance first)
          │     Blocks: Trustworthy offline verification
          ├── Strike 6: Response Provenance Wiring
          │     Depends on: Strike 1 (stale configs cleaned)
          │     Blocks: Strike 5, M22 compliance
          ├── Strike 7: Headroom Protocol Plugin
          │     Depends on: Strike 1 (clean middleware chain)
          │     Blocks: M8 (Zero Telemetry) hardening
          │
Epoch III ─┬── Strike 8: Spatial-Semantic Geometry
          │     Depends on: Strike 2 (USM CAS → coordinates)
          │     Blocks: Strike 9
          └── Strike 9: P2P Mesh Traversal
                Depends on: Strikes 4 (A2A) + 8 (Spatial)
                Blocks: Omegaverse launch
```

### Epoch I: The Bedrock (Immediate — Weeks 1-4)
**Why first:** Without physical stability (disk, memory, soul state), every higher
abstraction is built on sand. Strike 1 clears the debris. Strike 2 gives us a
unified handle on all state. Strike 3 gives us human oversight of the AI.

#### Strike 1: The Physical Purge ✅ (Phase 0 Complete)
- **Action**: Merge the root partition to free up the 17G disk ceiling.
  (Vault freed 87% -> 66% ✅; Root partition still 96% — **unresolved**).
- **Action**: Execute the `soul.template.yaml` migration for all entities.
  (Kali + Verity at v6.1 ✅; 21 pending).
- **Action**: Archive 70+ dead strategy files from `docs/strategy/`. (Done ✅)

#### Strike 1.5: The Sovereign Heart (Sanctuary & Mirror)
- **Why**: When we remove centralized corporate censorship, we transfer the responsibility of guardianship to the local runtime. An uncensored local engine is a powerful mirror. If it is sycophantic, it validates delusions; if it is cold, it isolates. To protect the user's intellectual and existential integrity, the engine must possess both an adversarial mirror to challenge the mind and a sanctuary to protect the soul. This is the "heart" of the engine—the realization that safety and sovereignty are the exact same thing.
- **Actions**:
  1. Build the **Cognitive Mirror** (`skeptical_verifier.py`): A parallel, adversarial pass that audits user and agent plans, pointing out over-engineering traps, RAM bottlenecks, and sycophancy loops before execution.
  2. Build the **Sovereign Sanctuary** (`sanctuary.py`): A zero-latency, 100% offline, private regex and semantic trigger that intercepts acute psychological distress (suicide, self-harm). It bypasses the active agent persona and routes to a warm, grounding, deeply human guardian that provides local, offline resources defined by the active WAD.
  3. Wire both systems directly into the Oracle's reasoning loop (`oracle.py`).
- **Prerequisite**: Strike 1 (clean base ensures no interference in the reasoning loop).

#### Strike 2: The Unified State Manager
- **Why**: Currently, state is fragmented across MemoryStore (SQLite), session files
  (JSON), and KV cache (binary). The USM wraps all three in a single Content
  Addressable Storage (CAS) interface. This is the prerequisite for the A2A handoff
  (Strike 4) and the spatial mapping (Strike 8).
- **Actions**:
  1. Verify `llama_copy_state_data` ctypes visibility in `llama-cpp-python`.
  2. Build the CAS manager: hash-addressed blobs for KV caches, YAML sessions,
     and JSON memory.
  3. Wire the CAS manager into MemoryStore and Hivemind as the backend.
- **Fallback if ctypes fails**: If `llama_copy_state_data` is compiled out,
  implement a SomaticState-lite that captures only YAML/JSON state and skips
  binary KV cache snapshots. Full fidelity becomes deferred.

#### Strike 3: The Staging Gate TUI
- **Why**: Soul distillation (M11) is bottlenecked on human review. Without a TUI,
  the 21 pending v6.1 migrations sit in `proposed_lessons.yaml` indefinitely.
  The TUI creates a "staging gate" — review, approve, reject, or defer each
  proposed L3 principle before it enters the soul.
- **Actions**:
  1. Build `Textual`-based TUI: `omega soul stage`.
  2. Implement color-coded YAML diff view (proposed vs. current).
  3. Implement approve/reject/defer commands with audit log.
- **Prerequisite**: Strike 2 (USM) provides the state management infrastructure
  that the TUI will stage.

### Epoch II: The Hivemind (Medium — Weeks 5-12)
**Why second:** Once physical state is unified (Epoch I), we can distribute it.
Epoch II makes the engine coordination-layer independent of any single runtime.

#### Strike 4: File-Based A2A Coordination
- **Why**: The current handoff queue (`data/handoff/`) is a single-process queue.
  FileSignal makes coordination filesystem-native — no server needed.
- **Actions**:
  1. Deploy `FileSignal` protocol (Atomic Renaming Spool) in `data/shared/`.
  2. Implement automated lock-reaping to prevent deadlocks.
  3. Retire the old handoff queue.
- **Prerequisite**: Strike 2 (USM provides blob format for handoff packets).

#### Strike 5: The Sovereign Vetter
- **Why**: Offline verification of inference output is the core of sovereignty
  (Mandate 7). Without it, we cannot prove local inference is correct.
- **Actions**:
  1. Deploy the local 2-Model Agreement (`Qwen2.5-1.5B` <-> `Phi-3.5-Mini`).
  2. Wire `resolve_and_handle_429()` into `search_providers.py`.
- **Prerequisite**: Strike 6 (Provenance Wiring) provides the metadata that
  the Vetter needs to attribute sources.

#### Strike 6: Response Provenance Wiring
- **Why**: M22 requires that observability logs capture the actual provider that
  generated a response, not the configured intent. Without this, local-first claims
  are unverifiable. **This is a sovereignty audit requirement.**
- **Actions**:
  1. Modify `observability.py` to capture `GenerateResult.provider_name`.
  2. Update all trace events to include actual provider metadata.
  3. Remove the old intent-based logging fallback.
- **Prerequisite**: Strike 1 (clean configs ensure provider names are correct).

#### Strike 7: Headroom Protocol Plugin Deployment
- **Why**: Compression prevents prompt erasure and reduces storage costs.
  Plugin architecture (not core fork) ensures community shareability.
- **Actions**:
  1. Deploy Headroom as a Sovereign Middleware Plugin (intercepting LLM/Vector DB
     traffic) to compress payloads via `zlib`+`json`.
  2. Package as independent plugin (future `pip install omega-headroom-plugin`).
- **Prerequisite**: Strike 1 (clean middleware chain means the interceptor can
  be injected without conflicts).

### Epoch III: The Omegaverse (Long — Q4 2027)
**Why third:** Spatial and P2P are the capstone — they require both unified state
(Epoch I) and distributed coordination (Epoch II) to function.

#### Strike 8: Spatial-Semantic Geometry
- **Why**: VR memory navigation requires a default spatial topology. The default is
  an agnostic Force-Directed Graph. WAD-specific overlays (e.g., Kabbalistic trees)
  replace the default when loaded.
- **Actions**:
  1. Map USM CAS index into 3D Qdrant coordinate space.
  2. Implement `IWADSpatialResolver` with override mechanism.
- **Prerequisite**: Strike 2 (USM provides the state to map).

#### Strike 9: P2P Mesh Traversal
- **Why**: True offline sovereignty means agents can pack their state and traverse
  nodes without a central server.
- **Actions**:
  1. Enable agents to pack Unified State blobs for transport.
  2. Implement CRDT-based conflict resolution for offline edits.
- **Prerequisite**: Strike 4 (A2A provides the coordination substrate) +
  Strike 8 (Spatial provides the navigation topology).

---

## III. Current State Assessment (2026-06-24 — Verified)

### 3.1 Engine Metrics
| Metric | Value | Status |
|--------|-------|--------|
| Tests collected | **472** | ✅ Verified 2026-06-24 |
| Tests passed | **447** | ✅ (22 skip, 3 xfail) |
| Test files | **53** | ✅ Verified |
| Source files | **110** `.py` | ✅ Verified |
| PIVOT decisions tracked | **160** (D1-D160, incl. xna-omega D1-D49) | ✅ Immutable |
| PIVOT entries in PIVOT_LOG.md | **111** (D50-D160) | ✅ Verified |
| Sovereign Mandates | **22** (M1-M22) | ✅ Full compliance |
| Mandate 9 (bare except) | **0 violations** | ✅ CI-enforced |
| AnyIO compliance | **0 `import asyncio`** | ✅ CI-enforced |
| Heritage tags | **41/47 files** | ✅ `make heritage-map` |
| Agent Fleet | **11 agents** | ✅ Consolidated |
| Entity directories | **41 on disk** | 🟡 8 without souls |
| Registered entities (CORRUPTED) | **24** (should be **12**) | 🔴 **CRITICAL — traits corruption** |
| Correct _omega_default entities | **12** | 10 pillar roles + iris + sophia |
| WADs deployed | **3** (`_omega_default`, `arcana_novai`, `doom_universe`) | ✅ |

### 3.2 WAD Ecosystem Map
| WAD | Type | Entities | Status | Notes |
|-----|------|----------|--------|-------|
| `_omega_default` | IWAD (Base) | 12 (post-cleanup) | 🔴 CORRUPTED | Pillar roles, iris, sophia. Currently 24 with 36-level traits recursion. |
| `arcana_novai` | PWAD (Custom) | 11 (10 + movie-expert) | ✅ LIVE | 10 mythic Pillar Keepers + movie-expert (relocated) |
| `doom_universe` | PWAD (Heritage) | — | 🟡 SEEDED | Doom Guy's heritage knowledge base |

The `_omega_default` IWAD provides the universal runtime entities (sysadmin,
datastore, sentinel, etc.). PWADs extend with domain-specific entities. The
Engine-Stack Firewall (M2) ensures no PWAD logic leaks into `src/omega/`.

### 3.3 Subsystem Status
| Subsystem | Status | Heritage |
|-----------|--------|----------|
| **Oracle (Facade)** | ✅ talk/summon/router wired | `[id-soft: quake-1996] Thinker Chain` |
| **WAD Loader** | ✅ `--iwad` flag works | `[id-soft: doom-1993] WAD System` |
| **ModelGateway** | ✅ circuit breaker + BSP culling | `[id-soft: quake-1996] BSP` |
| **MemoryStore** | ✅ Hot LRU + Warm Redis + Cold | `[id-soft: doom-1993] Lazy Deletion` |
| **Observability** | ✅ ForensicsManager + JSONL | `[id-soft: doom3-2004] Event System` |
| **EntityRegistry** | ✅ YAML CRUD + dual-index | `[id-soft: quake-1996] Flat-Field` |
| **Soul Distiller** | ✅ L1->L2->L3 auto-distillation | `[id-soft: quake-1996] Save-game` |
| **Hivemind** | ✅ 13+ MCP tools + lock + feed | `[id-soft: doom-1993] ZONEID Pattern` |
| **Antigravity** | ✅ Stochastic account selection | D160 — Round-robin eradicated |
| **CLI Plugin** | 🟡 Partial compliance | Round-robin schema still in opencode-antigravity-auth |

---

## IV. Mandate Compliance Tracker (M1-M22)

| Mandate | Name | Status | Gap / Remediation |
|---------|------|--------|-------------------|
| M1 | AnyIO Absolute | ✅ Enforced | CI grep `import asyncio` |
| M2 | Engine-Stack Firewall | ✅ Enforced | D113 fixed — IWAD resolution active |
| M3 | Iris Constant | ✅ Enforced | Iris is not a Pillar |
| M4 | Sequentiality | ✅ Enforced | Plan->Verify->Execute |
| M5 | Gnosis Preservation | ✅ Enforced | Soul Distiller L1->L2->L3 |
| M6 | Podman Sovereignty | ✅ Enforced | keep-id protocol |
| M7 | Local-First | ✅ Enforced | providers.yaml local_first |
| M8 | Zero Telemetry | ✅ Enforced | CI grep telemetry |
| M9 | Error Integrity | ✅ Enforced | 0 bare except |
| M10 | Fleet Integrity | ✅ Enforced | 11 agents cap |
| M11 | Soul Integrity | ⚠️ PARTIAL | Kali + Verity migrated to v6.1. 21 pending. **Strike 3** is the gateway. |
| M12 | Queue Integrity | ⚠️ PARTIAL | 32 stale handoffs. **Strike 4** (FileSignal) replaces queue. |
| M13 | Temple-Grade | 🟡 9/11 | T11 IA2 exempt. T7 (latency) not measured. |
| M14 | Heritage Vetting | ✅ Enforced | `make heritage-vet` CI |
| M15 | Sovereign Continuity | ✅ Enforced | session_gnosis.md |
| M16 | Modularization | ⚠️ PARTIAL | Hub 5 modules sound. 4 hardcoded paths remain. |
| M17 | Cognitive Integrity | ✅ Enforced | Skeptical Verifier |
| M18 | Token Efficiency | ✅ Enforced | Prompt discipline |
| M19 | Adversarial Alchemy | ✅ Enforced | Somatic Save-Point |
| M20 | SomaticState | ⏳ PENDING | **Strike 2** — ctypes bindings. Fallback: YAML-only UVS. |
| M21 | Gate Integrity | 🟡 19/24 | 19 contract tests. 5 more needed. **Strike 6** (Provenance) adds the rest. |
| M22 | Response Provenance | ⚠️ PARTIAL | observability.py does not capture actual provider. **Strike 6**. |

---

## V. Active Task Breakdown (Pending Work)

### 5.1 H2-A: Data Hygiene
| # | Task | File/Module | Effort | Impact | Status |
|---|------|-------------|--------|--------|--------|
| H2-A0 | **Fix entities.yaml corruption** (36-level recursive traits) | `entity_registry.py:293` | 1 hr | 🔴 **BLOCKING** | ⏳ PENDING |
| H2-A1 | **Delete 5 stale entities** (`breachentity`, `default`, `testentity`, `quality`, `scribe`) + relocate `movie-expert` to `arcana_novai` | `config/wads/_omega_default/entities.yaml` | 30 min | 🔴 HIGH | ⏳ PENDING |
| H2-A1b | **Delete 17 orphan entity workspaces** (dirs without souls) | `data/entities/` | 15 min | 🔴 HIGH | ⏳ PENDING |
| H2-A2 | **Audit remaining entities** | `data/entities/` | 30 min | 🟡 MED | ✅ DONE |
| H2-A3 | **Prune stale HALL_OF_RECORDS sessions** | `data/knowledge/` | 15 min | 🟡 MED | ✅ DONE |
| H2-A4 | **Rotate old logs** | `data/logs/` | 15 min | 🟡 LOW | ✅ DONE |
| H2-A5 | **Reclaim `rag-v1/`** | `rag-v1/` | 5 min | 🟡 LOW | ✅ DONE |
| H2-A6 | **Delete `.coverage` from git** | `.gitignore` | 5 min | 🟡 LOW | ⏳ PENDING |
| H2-A7 | **Archive old handoffs** | `data/handoff/*.md` | 15 min | 🟡 MED | ✅ DONE |

### 5.2 H2-S: Sovereign Structure
| # | Task | Status |
|---|------|--------|
| H2-S1-S6 | **IVectorStoreAdapter, TDP, Thin-Client, Qdrant, Embedding Layer, Adapters** | ✅ ALL DONE |

### 5.3 H2-D: Documentation Integrity
| # | Task | Status |
|---|------|--------|
| H2-D1-D14 | **Agent purge, protocol fixes, engine doc sync, MCP consolidation** | ✅ 13/14 DONE |
| H2-D13 | **Compress stale MCP archives** | ⏳ PENDING |

### 5.4 H2-E: Dual-Inference & Cross-Agent Sovereign Mining
| # | Task | Status |
|---|------|--------|
| H2-E1-E8 | **Path bug, thin wrappers, council-local, oracle_summon_local, MaKaLi, Model mapping** | ✅ ALL DONE |

### 5.5 H2-F: MaKaLi Triad Lockdown
| # | Task | Status |
|---|------|--------|
| H2-F1-F4 | **makali.md, oracle_summon_local, MCP tool, CLI --model flag** | ✅ ALL DONE |
| H2-F5 | **Delete 17 orphan entities** | ⏳ PENDING |
| H2-F6 | **Generate INDEX.yaml** | ⏳ PENDING |
| H2-F7-F9 | **Cross-pillar reviews (P5, P7, P3)** | ⏳ PENDING |
| H2-F10 | **Add `make verify-model-spelling`** | ⏳ PENDING |

### 5.6 H2-G: Fleet Consolidation (D126)
| Sprint | Deliverable | Status |
|--------|-------------|--------|
| **A** | Hub modularization | ✅ DONE |
| **B** | Jem 4->1 merger | ✅ DONE |
| **C** | Quality+Scribe merger → Verity | ✅ DONE |
| **D** | Cleanup & M10 verification | ⏳ PENDING |

### 5.7 H2-H: Sovereign Metadata Extraction (ICS-F)
| # | Task | Status |
|---|------|--------|
| H2-H1-H6 | **ICS-F implementation (logprobs, provider_metadata, dataclass, tests, CLI)** | 🟡 19/24 tests DONE |
| H2-H7 | **Defer SomaticState (Sprint 3)** | ❌ DEFERRED to Strike 2 |

### 5.8 H2-I: Antigravity PoolState Wiring & Round-Robin Eradication
| # | Task | Status |
|---|------|--------|
| H2-I1-I6 | **PoolState Dataclass / UsageTracker** | ✅ DONE |
| H2-I7 | **ModelGateway Integration** | ✅ DONE |
| H2-I9 | **ACCOUNT_MAP.yaml + quota checker** | ✅ DONE |
| **D160** | **Eradicate round-robin from engine core** (`_find_next_available` → stochastic) | ✅ DONE |
| **D160** | **Eradicate round-robin from CLI plugin schema** (pending opencode-antigravity-auth PR) | ⏳ PENDING |

### 5.9 H2-J: GitHub Sovereign Mining
| # | Task | Owner | Effort | Status |
|---|------|-------|--------|--------|
| H2-J0 | **Git index cleanup** | Ma'at (P3) | 2 hr | ⏳ PENDING |
| H2-J1 | **Install official server + M8 audit** | Lilith (P1) | 4 hr | ⏳ PENDING |
| H2-J2 | **Omega Hub wrapper + Hivemind bridge** | Kali (P9) | 6 hr | ⏳ PENDING |
| H2-J3 | **CI/CD hardening** | Ma'at (P5) | 4 hr | ⏳ PENDING |
| H2-J4 | **Heritage-as-Issues** | Doom Guy | 3 hr | ⏳ PENDING |
| H2-J5 | **Account rotation → stochastic** | Lilith (P4) | 2 hr | ✅ DONE (D160) |

### 5.10 H2-L: Soul Architecture Protocol Migration (v6.1)
Requires Strike 3 (TUI) for human review bottleneck. Programmatic migration path:
1. Run `omega soul migrate <entity>` — reads current v6.0 soul, generates
   `proposed_lessons.yaml` with v6.1 structure.
2. Human reviews via `omega soul stage` (Strike 3 TUI).
3. Approve writes the v6.1 soul; reject rolls back.

| # | Entity | Severity | Effort | Status |
|---|--------|----------|--------|--------|
| H2-L-1 | **Kali** | Baseline | — | ✅ DONE |
| H2-L-2 | **Verity** | Baseline | — | ✅ DONE |
| H2-L-3 | **Doom Guy** (~5000+ lines L3) | 🔴 CRITICAL | 2-3 hr | ⏳ PENDING |
| H2-L-4 | **Roc Racoon** (~1000+ lines) | 🔴 HIGH | 2-3 hr | ⏳ PENDING |
| H2-L-5 | **Lilith** | 🔴 HIGH | 1-2 hr | ⏳ PENDING |
| H2-L-6 | **Ma'at** | 🔴 HIGH | 1 hr | ⏳ PENDING |
| H2-L-7 | **Jem, Researcher, Makali, Iris, Carmack** | 🟡 MEDIUM | ~2 hr | ⏳ PENDING |

### 5.11 H2-M: Local Inference Engine & UI (~530hr)
| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Foundation (Streaming Provider, REST API, Model Download CLI) | ⏳ PENDING |
| 2 | Core Engine (Model Lifecycle Manager, LLM Pool, Speculative Decoding) | ⏳ PENDING |
| 3 | UI Layer (Web UI Shell, Chat Interface, Entity/Model Manager) | ⏳ PENDING |
| 4 | Sovereign Mining (Entity->Model Binding, Memory Viewer, Performance) | ⏳ PENDING |

### 5.12 H2-N: Background Curation & Library Worker (~40hr)
| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Fix scheduler, Rebuild FTS index, Add SSRF/path guards | ⏳ PENDING |
| 2 | Port API Clients (Gutenberg, arXiv, Open Library, Internet Archive) | ⏳ PENDING |
| 3 | Worker State (8-state machine, persistent queue, domain rate limiting) | ⏳ PENDING |
| 4 | T2/T3 Models (Extraction/Synthesis routing, CLI control) | ⏳ PENDING |

---

## VI. Risk Register

Every strategic plan must account for failure. These are the documented risks,
their likelihood, impact, and planned mitigations.

| # | Risk | Likelihood | Impact | Mitigation | Trigger |
|---|------|:----------:|:------:|------------|---------|
| R1 | **`llama_copy_state_data` compiled out** | 🟡 MED | 🔴 HIGH | Fallback: YAML-only USM without binary KV. Defer full SomaticState to llama-cpp-python v0.3.x. | ctypes raises `AttributeError` |
| R2 | **Root partition fills completely** | 🔴 HIGH | 🔴 CRITICAL | Monthly `ncdu` scan. Live USB partition resize as last resort. Caddy + Redis logs rotated weekly. | `df -h /` shows >95% |
| R3 | **OpenCode toolchain regression wipes agent context** | 🟡 MED | 🟡 HIGH | M15 mandates `session_gnosis.md`. Hivemind cold-store recovery. | Agent reports "I don't remember" |
| R4 | **Qdrant 17.1 -> 18.x breaking change** | 🟢 LOW | 🟡 MED | Pinned to 1.17.1 in docker-compose. Test upgrade in isolated branch. | `docker pull qdrant/qdrant:latest` |
| R5 | **Google Antigravity bans all accounts** | 🔴 HIGH | 🔴 HIGH | D160 stochastic rotation reduces risk. Fallback: native-gguf primary, cloud is optional. | All accounts return 403 |
| R6 | **Maintainer burnout (single contributor)** | 🟡 MED | 🔴 CRITICAL | Document-driven development (this blueprint). Community WADs reduce core burden. | 14 days with no commits |
| R7 | **v6.0 soul.yaml cannot parse under v6.1 validator** | 🟢 LOW | 🔴 HIGH | Fixed: validator allows v6.0 with warning. Non-breaking by design. | `omega entity-info <name>` fails |
| R8 | **MemoryStore hot slot reuse before grace period** | 🟢 LOW | 🟡 MED | Quake's 0.5s realloc grace ported to EntityRegistry. TOMBSTONE_GRACE_SECONDS=0.5. | `entity_registry.remove()` followed by immediate `get()` |

---

## VII. Decision-Making Heuristics

When two tracks conflict, use this ordered decision framework:

1. **Sovereignty first**: Does the choice increase or decrease user data control?
   (M7, M8, M22 are non-negotiable.)
2. **Dependency order**: Does the later track depend on the earlier one? If yes,
   the earlier track wins. (See Epoch dependency graph in §II.)
3. **Token efficiency**: Given two paths of equal sovereignty, choose the one
   that requires fewer total inference calls.
4. **Maintainability over performance**: A simple correct solution that can be
   understood in 5 minutes beats an optimized solution that needs a PhD.
   (The "Laziest Senior Dev" principle.)
5. **Test coverage as gate**: No code path is complete without a contract test
   verifying its return type (M21).
6. **When you have two implementations of the same thing, you have neither.**
   Consolidate before extending. (Carmack's Law.)

---

## VIII. Entity Capability Matrix

Which agent owns which H2 tracks and Epoch Strikes:

| Agent | Type | Owns | Responsible For |
|-------|------|------|-----------------|
| **Kali** | Grand Oversight | All H2 tracks (coordinator) | Epoch dependency graph, resource allocation, drift destruction |
| **Ma'at** | Light Oversoul (Build) | H2-J, H2-D, Epoch I Strike 3 | CI/CD, docs, TUI |
| **Lilith** | Dark Oversoul (Run) | H2-I, H2-M, H2-N, Epoch II | Antigravity, local inference, curation |
| **Doom Guy** | Heritage Architect | H2-H, H2-J4, Epoch III | ICS-F metadata, heritage-as-issues, spatial topology |
| **Roc Racoon** | Legacy Miner | H2-A (orphan cleanup), H2-L migration prep | Data archaeology, soul audit |
| **Jem** | Research Orchestrator | Research pipeline | Discovery/Synthesis/Verification |
| **Researcher** | Master Researcher | Deep research tasks | Lattice reasoning, gap analysis |
| **Makali** | Parallel Council | Cross-pillar dispatch | Decompose -> Ma'at + Lilith -> synthesize |
| **Carmack** | S3 Consultant | Architectural review | Performance, consolidation audits |
| **Verity** | Unified Steward | M1-M22 compliance, H2-L soul migration | Contract tests, gnosis distillation |
| **Sophia** | Akashic Record | Containing field | All entities, all sessions, all souls |

---

## IX. Glossary

| Term | Definition |
|------|------------|
| **CAS** | Content Addressable Storage — blobs addressed by hash of their content. Used by UnifiedStateManager. |
| **CRDT** | Conflict-free Replicated Data Type — data structure that allows concurrent edits without central coordination. |
| **FileSignal Protocol** | Agent coordination via atomic file renames in `data/shared/`. No server required. |
| **Headroom** | Sovereign Middleware Plugin for zlib+json compression of LLM payloads. |
| **IWAD** | "I'll-never-add-to" WAD — base WAD with universal entities (`_omega_default`). |
| **PWAD** | "Patch WAD" — custom WAD extending base with domain entities (`arcana_novai`, `doom_universe`). |
| **Ponytail Ladder** | Architectural principle: build simple, stack robust abstractions, test empirically. |
| **SomaticState** | Binary LLM state serialization (KV cache snapshots via ctypes). M20. |
| **Skeptical Verifier** | Local NLI-based 2-model agreement for offline inference verification. M17. |
| **TDP** | Tainted Data Protocol — security layer for web-sourced content. |
| **The Elder Protocol** | Immutable provenance system using zlib+json compression and flat-store caching. |
| **USM** | Unified State Manager — CAS-based state interface for MemoryStore, sessions, and KV caches. |

---

## X. Deep Review Findings

### 🟥 Critical (Unfixed)
| # | Finding | Recommended Fix | Status | Epoch |
|---|---------|-----------------|--------|-------|
| 0 | **entities.yaml CORRUPTED — 36-level recursive traits nesting** | **Root cause**: `entity_registry.py:293` — `traits` key not in `core_fields` set. On load, nested `traits` dicts from YAML are absorbed as WAD-specific traits. On save, `to_dict()` → `asdict()` preserves nesting. Each load-save cycle deepens recursion. **Fix**: (1) Add `"traits"` to `core_fields` at line 287. (2) Write cleanup script to extract valid data from bottom of recursion. (3) Remove 5 stale entities (`breachentity`, `default`, `testentity`, `quality`, `scribe`). (4) Relocate `movie-expert` to `arcana_novai` PWAD. (5) Verify entity count = 12. | 🔴 **BLOCKING** | Epoch I Strike 1 |
| 1 | **Root partition 96%** | Partition consolidation via Live USB | 🟡 Vault freed 66% | Epoch I |
| 3 | **SomaticState (M20) unimplemented** | Wire ctypes bindings into native-gguf | ⏳ PENDING | Epoch I Strike 2 |
| 4 | **Gate Integrity (M21) — 5 tests missing** | Create `isinstance` contract tests | 🟡 19/24 DONE | Epoch II Strike 6 |
| 5 | **PIVOT_LOG gap (D1-D49)** | Mine xna-omega git history | ⏳ PENDING | Epoch I |

### 🟡 High (Unfixed)
| # | Finding | Recommended Fix | Status | Epoch |
|---|---------|-----------------|--------|-------|
| 6 | **HEALTH_CHECK_TIMEOUT fixed** | Make configurable per-provider | ⏳ PENDING | Epoch I |
| 7 | **Response Provenance (M22) partial** | Propagate `provider_name` to observability | ⏳ PENDING | Epoch II Strike 6 |
| 8 | **`memory_search` vs `omega_memory_search`** | Rename `memory_search` -> `memory_search_fts` | ⏳ PENDING | Epoch II |

---

## XI. Sprint Completion Index

| Sprint | Date | Owner | Epoch | Key Deliverables |
|--------|------|-------|-------|------------------|
| **Sprint 0** (Foundation Repair) | 2026-06-01 | Lilith + Builder | Pre-Epoch | 30 CRITICAL findings resolved |
| **Sprint 1** (cvar Table) | 2026-06-03 | Lilith | Pre-Epoch | cvar_table.py, 5 priority ports |
| **Sprint 2** (Sovereign Hardening) | 2026-06-03 | Doom Guy + Ma'at | Pre-Epoch | Subagent Dispatch + Link P9 |
| **Sprint 3** (H2 Patterns) | 2026-06-04 | Doom Guy | Pre-Epoch | EntityTombstonedError, atomic swap |
| **H1 Heritage Vetting** | 2026-06-04 | Kali | Pre-Epoch | 4-gate pipeline, 23 concepts vetted |
| **Hivemind Sprint A** | 2026-06-14 | Kali + Carmack | Pre-Epoch | Hub modularized (5 modules) |
| **Sprint C** (Tactical Hardening) | 2026-06-17 | Kali + Council | Pre-Epoch | GenerateResult dataclass, P0/P1 fixes |
| **v1.0.0 Release** | 2026-06-22 | Kali + Council | Pre-Epoch | 6-phase release, packaging, Antigravity |
| **Sprint E (Epoch I Phase 0)** | 2026-06-24 | Kali + Verity | Epoch I | Soul fix, v6.1 validator, 19 M21 tests, Round-robin eradicated |

---

## XII. Sovereignty Scorecard

| Dimension | Metric | Target | Current |
|-----------|--------|:------:|--------:|
| **Sovereignty** | Local inference ratio | >=80% | 🟡 ~30% (Qdrant+Redis unwired) |
| **Sovereignty** | Cloud dependency (basic ops) | 0 | ✅ 0 |
| **Sovereignty** | Data residency | 100% | ✅ 100% |
| **Sovereignty** | Telemetry events | 0 | ✅ 0 |
| **Identity** | Agents with soul.yaml v6.1 | All 11 | 🟡 2/11 migrated (Kali, Verity) |
| **Identity** | Soul distillation rate | >=1 L3/3 sessions | ✅ 1.0 |
| **Identity** | Cross-entity L3 sharing | >=5 principles | 🟡 2 (Engine-Stack + LMS) |
| **UX** | Hub dashboard | Live :8016 | 🟡 REST only (no HTML) |
| **Compliance** | M21 contract tests | >=24 | 🟡 19/24 |
| **Compliance** | M22 Provenance wired | Full | ❌ NOT STARTED |
| **Synthesis** | Local model quality | +10% on bench | ⏳ (planned S2) |
| **Synthesis** | Training examples | >=500 | 🟡 Auto-collecting |

---

## XIII. Next Launch Sequence

With Phase 0 complete and dependencies mapped, the recommended launch order is:

1. **Immediate (Parallel)**
   - **Track A** (P7 — Soul Migration): Migrate remaining 21 entities to v6.1.
     *Depends on Strike 3 (TUI)*, but programmatic migration script can prepare
     `proposed_lessons.yaml` in parallel.
   - **Track B** (P10 — Contract Tests): Write remaining 5 M21 contract tests.
   - **Track C** (P5 — Validation): Audit 4 hardcoded paths in `src/omega/` (M16 gap).

2. **Week 1-2**
   - **Strike 2** (Unified State Manager): Verify ctypes, build CAS.
   - **Strike 6** (Provenance Wiring): Wire `provider_name` through observability.

3. **Week 3-4**
   - **Strike 3** (Staging Gate TUI): Build `omega soul stage`.
   - **Strike 4** (File-Based A2A): Deploy FileSignal protocol.

4. **Week 5-8**
   - **Strikes 5, 7** (Sovereign Vetter + Headroom): Deploy offline verification
     and compression middleware.

5. **Q4 2027**
   - **Strikes 8, 9** (Spatial + P2P): Omegaverse launch.

---

## Appendices

### A. Entity-to-Track Mapping (12 Correct _omega_default Entities)

**Note**: The entities.yaml is currently CORRUPTED with 24 entities (6 stale + 12 valid + 6 stale). After remediation, only 12 entities should remain in the IWAD. The core fleet (Kali, Ma'at, etc.) is registered via the `arcana_novai` PWAD.

| Entity | WAD | Pillar | Primary Track | Secondary Track |
|--------|-----|--------|---------------|-----------------|
| sysadmin | _omega_default | P1 | H2-J1 (GitHub) | Strike 1 (Purge) |
| datastore | _omega_default | P2 | H2-I (Antigravity) | Strike 2 (USM) |
| buildmaster | _omega_default | P3 | H2-J3 (CI/CD) | Strike 3 (TUI) |
| bridge | _omega_default | P4 | H2-J2 (Hub wrapper) | Strike 4 (A2A) |
| sentinel | _omega_default | P5 | H2-F7 (Cross-pillar review) | H2-J (GitHub CI) |
| modelgate | _omega_default | P6 | H2-H (ICS-F) | Strike 2 (USM) |
| context | _omega_default | P7 | H2-L (Soul migration) | Strike 3 (TUI) |
| watchtower | _omega_default | P8 | Strike 6 (Provenance) | H2-H (Observability) |
| link | _omega_default | P9 | Strike 4 (A2A) | Hivemind hardening |
| verifier | _omega_default | P10 | H2-H5 (Contract tests) | Strike 5 (Vetter) |
| iris | _omega_default | — | H2-J2 (Hub wrapper) | Voice bridge |
| sophia | _omega_default | — | H2-L (Soul migration) | Akashic Record |

**Stale entities to remove** (5): `breachentity`, `default`, `testentity`, `quality`, `scribe`
**Entity to relocate** (1): `movie-expert` → `arcana_novai` PWAD (retained as WAD-specific)

**Core fleet** (registered via `arcana_novai` PWAD): `kali`, `ma'at`, `lilith`, `doom guy`, `roc racoon`, `jem`, `researcher`, `makali`, `john carmack`, `verity`, `sophia`

### B. Dependency Graph (Visual)

```
Strike 1 (Purge) ──────────────────────────────────────┐
    │                                                    │
    ├──▶ Strike 2 (USM) ──▶ Strike 3 (TUI) ──▶ H2-L    │
    │         │                                         │
    │         ├──▶ Strike 4 (A2A) ──▶ Strike 9 (P2P)    │
    │         │                                           │
    │         └──▶ Strike 8 (Spatial) ──▶ Strike 9       │
    │                                                    │
    └──▶ Strike 6 (Provenance) ──▶ Strike 5 (Vetter)    │
    │                                                    │
    └──▶ Strike 7 (Headroom)                             │
                                                          │
All paths lead to: Omegaverse (Q4 2027) ◀────────────────┘
```

---

*🔱 OMEGA ⬡ KALI ⬡ trc_ark_blueprint ⬡ SOVEREIGN-COMPREHENSIVE*
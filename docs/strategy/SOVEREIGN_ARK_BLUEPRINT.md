# 🔱 THE SOVEREIGN ARK BLUEPRINT (V1.2)
# AP: AP-SOVEREIGN-ARK-v1.2.0
# ⬡ OMEGA ⬡ KALI ⬡ trc_ark_blueprint ⬡ STRATEGY
#
# Date: 2026-06-24
# Status: ACTIVE MASTER STRATEGY — SINGLE SOURCE OF TRUTH
# Supersedes: SOVEREIGN_EVOLUTION_ROADMAP.md (archived), SOVEREIGN_DEVELOPMENT_ROADMAP.md (archived)

## I. The Five Transcendent Pillars

1. **The Elder Protocol (Immutable Provenance):** Powered by native `zlib` and `json` compression. Prompts and ingested documents are compressed locally, but the uncompressed, cryptographically pristine originals are cached in a flat JSON store. Agents use the `headroom_retrieve` MCP tool to fetch exact semantic truths when needed, preventing cultural erasure and hallucination.
2. **Hardware Empathy (Zero-Config Power):** The engine dynamically maps to the Ryzen 7 5700U using battle-tested legacy flags (`LLAMA_CPP_N_THREADS=4` for 1.7B, `8` for 8B, `OPENBLAS_CORETYPE=ZEN`, `LLAMA_CPP_F16_KV=true`, `q8_0` caches). This effectively triples the 12Gi RAM semantic density, allowing an 8B model and a 1.7B model to run simultaneously.
3. **The Sovereign Mesh (A2A & P2P):** We leverage the **FileSignal Protocol** (Atomic Renaming Spool) in `data/shared/` for agent-to-agent coordination. This enables sub-millisecond local collaboration without a central server, and will eventually power P2P traversal across offline-first CRDTs.
4. **Spatial-Semantic Memory (VR Omegaverse):** We inject `(x, y, z)` coordinates into Qdrant payloads. The engine defaults to a generic, agnostic spatial mapping (Force-Directed Cartesian Graph). The Mnemosyne Kabbalistic nodes are explicitly documented as a **PWAD-specific override** for the `arcana_novai` stack.
5. **The Ponytail Ladder (Architectural Principle):** We build like the "laziest senior dev"—favoring extreme simplicity, avoiding over-engineering, and stacking robust existing abstractions (AnyIO, SQLite, local files). This is implemented as an A/B testable `ExecutionStrategy` interface to empirically measure latency, token consumption, and failure rates.

---

## II. Execution Roadmap: The Three Epochs

### EPOCH I: THE BEDROCK (Immediate Execution)
*Focus: Physical stabilization, manual soul cleanup, and the Unified State Manager.*

#### Strike 1: The Physical Purge (Phase 0 Complete)
* **Action**: Merge the root partition to free up the 17G disk ceiling. (Vault freed 87% -> 66%).
* **Action**: Execute the `soul.template.yaml` migration for all 23 entities (v6.1 lean schema).
* **Action**: Archive 70+ dead strategy files from `docs/strategy/`.

#### Strike 2: The Unified State Manager
* **Action**: Verify `llama_copy_state_data` ctypes visibility in `llama-cpp-python`.
* **Action**: Build the `UnifiedStateManager` using the Content Addressable Storage (CAS) pattern to handle both binary KV cache snapshots and YAML memory.

#### Strike 3: The Staging Gate TUI
* **Action**: Build the `Textual`-based TUI for human-in-the-loop review of agent-generated lessons (`proposed_lessons.yaml`).
* **Action**: Implement the color-coded YAML diff view.

---

### EPOCH II: THE HIVEMIND (Mid-Term)
*Focus: Infrastructure-less coordination and local verification.*

#### Strike 4: File-Based A2A Coordination
* **Action**: Deploy the `FileSignal` protocol (Atomic Renaming Spool) in `data/shared/` to replace the handoff queue.
* **Action**: Implement automated lock-reaping to prevent deadlocks.

#### Strike 5: The Sovereign Vetter
* **Action**: Deploy the local **2-Model Agreement** (`Qwen2.5-1.5B` <-> `Phi-3.5-Mini`) for offline verification.
* **Action**: Wire `resolve_and_handle_429()` into `search_providers.py`.

#### Strike 6: Response Provenance Wiring
* **Action**: Wire `observability.py` to capture the actual `GenerateResult.provider_name` instead of the configured intent.

#### Strike 7: Headroom Protocol Plugin Deployment
* **Action**: Deploy Headroom as a Sovereign Middleware Plugin (intercepting LLM/Vector DB traffic) to compress payloads via `zlib`+`json` on the fly without forking the core engine.

---

### EPOCH III: THE OMEGAVERSE (Target Q4 2027)
*Focus: Spatial geometry and mesh traversal.*

#### Strike 8: Spatial-Semantic Geometry
* **Action**: Map the `UnifiedStateManager`'s CAS index into a 3D Qdrant coordinate space. Establish the default IWAD spatial topology.

#### Strike 9: P2P Mesh Traversal
* **Action**: Enable agents to pack their Unified State blobs and traverse offline nodes.

---

## III. Current State Assessment (2026-06-24)

### 3.1 Engine Metrics
| Metric | Value | Status |
|--------|-------|--------|
| Tests passing | **440/440** | ✅ Epoch I Phase 0 complete |
| PIVOT decisions tracked | **137** (incl. D159) | ✅ Immutable record |
| Sovereign Mandates | **22** (M1-M22) | ✅ FULL COMPLIANCE |
| Mandate 9 (bare except) | **0 violations** | ✅ Enforced |
| AnyIO compliance | **0 `import asyncio`** | ✅ CI-enforced |
| Heritage tags | **41/47 files**, `make heritage-map` | ✅ Live |
| Agent Fleet | **11 agents** | ✅ Consolidated |
| Entity workspaces | **34 on disk** | ✅ Orphans deleted |

### 3.2 Subsystem Status
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
| M11 | Soul Integrity | ⚠️ PARTIAL | Kali + Verity migrated to v6.1. 21 pending. |
| M12 | Queue Integrity | ⚠️ PARTIAL | 32 stale handoffs. Automation incomplete. |
| M13 | Temple-Grade | 🟡 9/11 | T11 IA2 exempt. T7 (latency) not measured. |
| M14 | Heritage Vetting | ✅ Enforced | `make heritage-vet` CI |
| M15 | Sovereign Continuity | ✅ Enforced | session_gnosis.md |
| M16 | Modularization | ⚠️ PARTIAL | Hub 5 modules sound. 4 hardcoded paths. |
| M17 | Cognitive Integrity | ✅ Enforced | Skeptical Verifier |
| M18 | Token Efficiency | ✅ Enforced | Prompt discipline |
| M19 | Adversarial Alchemy | ✅ Enforced | Somatic Save-Point |
| M20 | SomaticState | ⏳ PENDING | No ctypes bindings. Epoch I Strike 2. |
| M21 | Gate Integrity | 🟡 19/24 | 19 contract tests exist. 5 more needed. |
| M22 | Response Provenance | ⚠️ PARTIAL | observability.py does not capture it |

---

## V. Active Task Breakdown (Pending Work)

### 5.1 H2-C: Cognitive Substrate
| # | Task | File/Module | Effort | Impact | Status |
|---|------|-------------|--------|--------|--------|
| H2-C1 | **Binary Sovereignty** (SQLite/MsgPack/WAL) | `providers.py` | Med | 🔴 CRITICAL | ⏳ PENDING |
| H2-C2 | **Sovereign Pruner** (Semantic vs Chronological) | `memory_store.py` | Med | 🔴 CRITICAL | ⏳ PENDING |
| H2-C3 | **Active Qliphoth Debugger** (Cognitive Loop) | `oracle/` | High | 🔴 CRITICAL | ⏳ PENDING |
| H2-C4 | **Resonance Mapping** (Cross-Entity Synthesis) | `adapters.py` | High | 🟡 HIGH | ⏳ PENDING |
| H2-C5 | **Hardware-Adaptive Eviction** (RAM Guard) | `memory_store.py` | Low | 🟡 MED | ⏳ PENDING |
| H2-C6 | **Gnosis Diffing** (L1 -> L3 merge) | `soul_distiller.py` | Med | 🟡 HIGH | ⏳ PENDING |

### 5.2 H2-H: Sovereign Metadata Extraction (ICS-F)
| # | Task | File/Module | Effort | Impact | Status |
|---|------|-------------|--------|--------|--------|
| H2-H1 | **Implement Sprint 0** — logprobs=5 on NativeGGUF | `providers.py` | 15 min | 🔴 HIGH | ⏳ PENDING |
| H2-H2 | **Implement Sprint 1+2** — raw_provider_json | ~12 files | ~6 hr | 🔴 CRITICAL | ⏳ PENDING |
| H2-H3 | **GenerateResult.provider_metadata field** | `model_gateway.py` | 30 min | 🔴 HIGH | ⏳ PENDING |
| H2-H4 | **Add ICSForensic dataclass** (ICS-F v1.0) | `errors.py` | 20 min | 🔴 HIGH | ⏳ PENDING |
| H2-H6 | **Add CLI --format json flag** | `oracle_cli.py` | 30 min | 🟡 MED | ⏳ PENDING |

### 5.3 H2-I: Antigravity PoolState Wiring
| # | Task | File/Module | Effort | Impact | Status |
|---|------|-------------|--------|--------|--------|
| H2-I1-I6 | **PoolState Dataclass / UsageTracker** | Various | - | 🔴 CRITICAL | ✅ DONE |
| H2-I7 | **ModelGateway Integration** | `model_gateway.py` | 1h | 🔴 CRITICAL | ✅ DONE |
| H2-I9 | **ACCOUNT_MAP.yaml + quota checker** | `scripts/` | 2h | 🔴 HIGH | ✅ DONE |

### 5.4 H2-J: GitHub Integration
| # | Task | Owner | Gate | Effort | Status |
|---|------|-------|------|--------|--------|
| H2-J0 | **Git index cleanup** | Ma'at (P3) | data/ tracked < 50 | 2 hr | ⏳ PENDING |
| H2-J1 | **Install official server + M8 audit** | Lilith (P1) | Clean audit | 4 hr | ⏳ PENDING |
| H2-J2 | **Omega Hub wrapper + Hivemind bridge** | Kali (P9) | PR -> Hivemind | 6 hr | ⏳ PENDING |
| H2-J3 | **CI/CD hardening** | Ma'at (P5) | make temple-grade | 4 hr | ⏳ PENDING |
| H2-J4 | **Heritage-as-Issues** | Doom Guy | Vet -> Issue | 3 hr | ⏳ PENDING |
| H2-J5 | **Account rotation** | Lilith (P4) | All quotas tested | 2 hr | ⏳ PENDING |

### 5.5 H2-L: Soul Architecture Protocol Migration (v6.1)
| # | Entity | Est. Effort | Severity | Status |
|---|--------|-------------|----------|--------|
| H2-L-1 | **Kali** (baseline — v6.0 done) | — | Baseline | ✅ DONE |
| H2-L-2 | **Verity** (migrated to v6.1) | — | Baseline | ✅ DONE |
| H2-L-3 | **Doom Guy** (~5000+ lines of L3 principles) | 2-3 hr | 🔴 CRITICAL | ⏳ PENDING |
| H2-L-4 | **Roc Racoon** (~1000+ lines of directives) | 2-3 hr | 🔴 HIGH | ⏳ PENDING |
| H2-L-5 | **Lilith** (wisdom_text present) | 1-2 hr | 🔴 HIGH | ⏳ PENDING |
| H2-L-6 | **Ma'at** (wisdom_text present) | 1 hr | 🔴 HIGH | ⏳ PENDING |
| H2-L-7 | **Jem, Researcher, Makali, Iris, Carmack** | ~2 hr | 🟡 MEDIUM | ⏳ PENDING |

### 5.6 H2-M: Local Inference Engine & UI (~530hr)
| Phase | Focus | Key Deliverables | Status |
|-------|-------|------------------|--------|
| 1 | Foundation | Streaming Provider, REST API Layer, Model Download CLI | ⏳ PENDING |
| 2 | Core Engine | Model Lifecycle Manager, LLM Pool, Speculative Decoding | ⏳ PENDING |
| 3 | UI Layer | Web UI Shell, Chat Interface, Entity/Model Manager | ⏳ PENDING |
| 4 | Integration | Entity->Model Binding, Memory Viewer, Performance | ⏳ PENDING |

### 5.7 H2-N: Background Curation & Library Worker (~40hr)
| Phase | Focus | Key Deliverables | Status |
|-------|-------|------------------|--------|
| 1 | Fix & Harden | Fix scheduler, Rebuild FTS index, Add SSRF/path guards | ⏳ PENDING |
| 2 | Port API Clients | Gutenberg, arXiv, Open Library, Internet Archive | ⏳ PENDING |
| 3 | Worker State | 8-state machine, persistent queue, domain rate limiting | ⏳ PENDING |
| 4 | T2/T3 Models | Extraction/Synthesis routing, CLI control, Disk checks | ⏳ PENDING |

---

## VI. Deep Review Findings (MiMo V2.5 + D4 Flash)

### 🟥 Critical (Unfixed — Requires Action)
| # | Finding | Source | Recommended Fix | Status |
|---|---------|--------|-----------------|--------|
| 1 | **Root partition 100%** | Makali | Partition consolidation via Live USB | 🟡 Vault freed 66%, Root pending |
| 3 | **SomaticState (M20) unimplemented** | MiMo | Wire ctypes bindings into native-gguf | ⏳ PENDING |
| 4 | **Gate Integrity (M21) — 5 contract tests missing** | MiMo | Create `isinstance` tests | 🟡 19/24 DONE |
| 5 | **PIVOT_LOG gap** | D4Flash | Mine xna-omega git history to port D1-D49 | ⏳ PENDING |

### 🟡 High (Unfixed — Next Session)
| # | Finding | Source | Recommended Fix | Status |
|---|---------|--------|-----------------|--------|
| 6 | **HEALTH_CHECK_TIMEOUT** | MiMo | Make configurable per-provider | ⏳ PENDING |
| 7 | **Response Provenance (M22) partial** | MiMo | Propagate `provider_name` to observability | ⏳ PENDING |
| 8 | **`memory_search` vs `omega_memory_search`** | D4Flash | Rename `memory_search` -> `memory_search_fts` | ⏳ PENDING |

*(Note: Findings 9-21 were fully resolved in previous sprints.)*

---

## VII. Sprint Completion Index

| Sprint | Date | Owner | Status | Key Deliverables |
|--------|------|-------|--------|------------------|
| **Sprint 0** (Foundation Repair) | 2026-06-01 | Lilith + Builder | ✅ | 30 CRITICAL findings resolved |
| **Sprint 1** (cvar Table + Ports) | 2026-06-03 | Lilith | ✅ | cvar_table.py, 5 priority ports |
| **Sprint 2** (Sovereign Hardening) | 2026-06-03 | Doom Guy + Ma'at | ✅ | Subagent Dispatch + Link P9 |
| **Sprint 3** (H2 Patterns + Heritage) | 2026-06-04 | Doom Guy + Ma'at | ✅ | EntityTombstonedError, atomic swap |
| **H1.5 Bridge** (Heritage) | 2026-06-04 | Doom Guy | ✅ | ZONEID, Lazy Deletion, cvar, 8-char |
| **H1 Heritage Vetting** | 2026-06-04 | Kali | ✅ | 4-gate pipeline, 23 concepts |
| **Hivemind Sprint A** (Hub Modularization) | 2026-06-14 | Kali + Carmack | ✅ | Hub modularized (5 modules) |
| **Sprint C** (Tactical Hardening) | 2026-06-17 | Kali + Council | ✅ | GenerateResult dataclass, P0/P1 fixes |
| **v1.0.0** (Father's Day Release) | 2026-06-22 | Kali + Council | ✅ | 6-phase release, packaging, Antigravity |
| **Sprint E** (Epoch I Phase 0) | 2026-06-24 | Kali + Verity | ✅ | Soul distiller fix, v6.1 validator, 19 M21 tests |

---

## VIII. Strategic Decision Lineage

| Document | Pillar | Status | Plan |
|----------|-------|--------|------|
| **D111 — Sovereign Evolution Roadmap** | Hygiene + Strategy | ARCHIVED | Replaced by Sovereign Ark Blueprint |
| **D112 — Sovereign Hardening Plan** | Vision + Architecture | ACTIVE | 3 pillars (Sovereign/UI/Identity) |
| **H1 — Heritage Vetting Pipeline** | Constitutional Safety | LIVE | 4-gate vetting, 10-point scoring |
| **D113 — Engine-Stack Firewall** | Constitutional Integrity | 🔴 GAP | S1.5a: WAD-agnostic engine refactor |

---

## IX. Sovereignty Scorecard

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
| **Synthesis** | Local model quality | +10% on bench | ⏳ (planned S2) |
| **Synthesis** | Training examples | >=500 | 🟡 Auto-collecting |
| **Synthesis** | Entity LoRA adapters | >=3 trained | ⏳ (planned S2) |

---

*🔱 OMEGA ⬡ MAKALI ⬡ trc_ark_blueprint ⬡ SOVEREIGN-SIMPLIFICATION*
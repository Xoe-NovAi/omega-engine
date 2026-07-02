# 🔱 THE SOVEREIGN ARK BLUEPRINT (v2.1)
## The Master Single Source of Truth for the Sovereign Ark Development
**AP Token**: `AP-SOVEREIGN-ARK-BLUEPRINT-v2.1.0`
⬡ OMEGA ⬡ KALI ⬡ trc_ark_blueprint ⬡ SOVEREIGN-TECHNICAL-SSOT

---

## Preamble: Why This Ark?

The Omega Engine exists to sever Big AI's umbilical cord. Every technical decision must pass through this lens: **does this increase or decrease the user's sovereignty?**

The Three Epochs are ordered by dependency — each Strike builds on the one before. This is not a wishlist. It is a survival kit. The engine already works. These steps make it resilient enough to outlast any toolchain, any hardware failure, any contribution gap.

## Consolidation Notice (2026-06-29)

**This document is the Single Source of Truth (SSOT).** On 2026-06-29, the MaKaLi Cloud Council consolidated **47 superseded strategy documents** into this blueprint. All strategic content (roadmaps, gap analyses, phase plans, release checklists, fleet topologies, mandate snapshots) has been unified here.

- **Remaining**: 40 operational/protocol docs (HIVEMIND_PROTOCOL.md, SUBAGENT_DISPATCH_PROTOCOL.md, etc.) kept as references
- **Archived**: 47 superseded docs moved to `archive/` with full manifest at `archive/MANIFEST.md`
- **New**: 3 MaKaLi Council critical gaps (PII Masking, Trace ID, A2A Identity) added to §5.1b
- **New**: Pre-release checklist imported from V10_RELEASE_STRATEGY.md in §5.1c
- **New**: Mandate audit results (M11 VIOLATED, M22 PARTIAL, M5/M7 at risk) in §IV

**If it's not in this blueprint, it's archived or it's a protocol doc.**

---

## I. The Five Transcendent Pillars

1. **The Elder Protocol (Immutable Provenance):** Powered by native `zlib` and `json` compression. Prompts and ingested documents are compressed locally, but the uncompressed, cryptographically pristine originals are cached in a flat JSON store. Agents use the `headroom_retrieve` MCP tool to fetch exact semantic truths when needed, preventing cultural erasure and hallucination.

2. **Hardware Empathy (Zero-Config Power):** The engine dynamically maps to the Ryzen 7 5700U using battle-tested legacy flags (`LLAMA_CPP_N_THREADS=4` for 1.7B, `8` for 8B, `OPENBLAS_CORETYPE=ZEN`, `LLAMA_CPP_F16_KV=true`, `q8_0` caches). This effectively triples the 12Gi RAM semantic density, allowing an 8B model and a 1.7B model to run simultaneously.

3. **The Sovereign Mesh (A2A & P2P):** We leverage the **FileSignal Protocol** (Atomic Renaming Spool) in `data/shared/` for agent-to-agent coordination. This enables sub-millisecond local collaboration without a central server, and will eventually power P2P traversal across offline-first CRDTs.

4. **Spatial-Semantic Memory (VR Omegaverse):** We inject `(x, y, z)` coordinates into Qdrant payloads. The engine defaults to a generic, agnostic spatial mapping (Force-Directed Cartesian Graph) for the `_omega_default` IWAD. Specialized WADs (like `arcana_novai`) can provide a **Sovereign Override** to replace the default geometry with custom lore (e.g., Mnemosyne Kabbalistic nodes).

5. **The Ponytail Ladder (Architectural Principle):** We build like the "laziest senior dev"—favoring extreme simplicity, avoiding over-engineering, and stacking robust existing abstractions (AnyIO, SQLite, local files). This is implemented as an A/B testable `ExecutionStrategy` interface. The **Standard Pipeline** (the null hypothesis) is defined as the current direct-inference path through `ModelGateway.generate()`. The **Ponytail Pipeline** is the experimental stacked-abstraction path. We compare them on four axes: token cost, latency, correctness, and maintainability.

---

## II. Execution Roadmap: The Three Epochs (With Explicit Dependencies)

Each Strike has documented prerequisites. You cannot skip a strike and succeed.

```
Epoch I ──┬── Strike 1: Physical Purge ✅ (Done)
          ├── Strike 2: Unified State Manager (USM)
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
                      ├── Strike 7: Headroom Protocol Plugin ✅ (Done)
 ✅ (Done)
           │     Depends on: Strike 1 (clean middleware chain)
           │     Blocks: M8 (Zero Telemetry) hardening
           ├── Strike 7.5: Semantic Router ✅ (Done)
           │     Depends on: Strike 1 (clean base)
           │     Blocks: Strike 8 (semantic vectors → spatial coordinates)
           │
           Epoch III ─┬── Strike 8: Spatial-Semantic Geometry ✅ (Done)
           │     Depends on: Strike 7.5 (semantic vectors → PCA → coordinates)
           │     Blocks: Strike 9

          └── Strike 9: P2P Mesh Traversal
                Depends on: Strikes 4 (A2A) + 8 (Spatial)
                Blocks: Omegaverse launch
```

### Epoch I: The Bedrock (Immediate — Weeks 1-4)
**Why first:** Without physical stability (disk, memory, soul state), every higher abstraction is built on sand. Strike 1 clears the debris. Strike 2 gives us a unified handle on all state. Strike 3 gives us human oversight of the AI.

#### Strike 1: The Physical Purge ✅ (Phase 0 Complete)
- **Action**: Merge the root partition to free up the 17G disk ceiling. (Vault freed 87% -> 66% ✅; Root partition still 96% — **unresolved**).
- **Action**: Execute the `soul.template.yaml` migration for all entities. (Kali + Verity at v6.1 ✅; 21 pending).
- **Action**: Archive 70+ dead strategy files from `docs/strategy/`. (Done ✅)

#### Strike 2: The Unified State Manager (USM)
- **Why**: Currently, state is fragmented across MemoryStore (SQLite), session files (JSON), and KV cache (binary). The USM wraps all three in a single Content Addressable Storage (CAS) interface. This is the prerequisite for the A2A handoff (Strike 4) and the spatial mapping (Strike 8).
- **Actions**:
  1. Verify `llama_copy_state_data` ctypes visibility in `llama-cpp-python`.
  2. Build the CAS manager: hash-addressed blobs for KV caches, YAML sessions, and JSON memory.
  3. Wire the CAS manager into MemoryStore and Hivemind as the backend.
- **Fallback if ctypes fails**: If `llama_copy_state_data` is compiled out, implement a SomaticState-lite that captures only YAML/JSON state and skips binary KV cache snapshots. Full fidelity becomes deferred.

#### Strike 3: The Staging Gate TUI
- **Why**: Soul distillation (M11) is bottlenecked on human review. Without a TUI, the 21 pending v6.1 migrations sit in `proposed_lessons.yaml` indefinitely. The TUI creates a "staging gate" — review, approve, reject, or defer each proposed L3 principle before it enters the soul.
- **Actions**:
  1. Build `Textual`-based TUI: `omega soul stage`.
  2. Implement color-coded YAML diff view (proposed vs. current).
  3. Implement approve/reject/defer commands with audit log.
- **Prerequisite**: Strike 2 (USM) provides the state management infrastructure that the TUI will stage.

### Epoch III: The Omegaverse (Long — Q4 2027)
**Why third:** Spatial and P2P are the capstone — they require both unified state (Epoch I) and distributed coordination (Epoch II) to function.

#### Strike 7.5: Semantic Router ✅ (Done)
- **Why**: Current entity routing uses word-boundary keyword matching (`entity_registry.py:find_by_domain()`). This is fragile — "I need to store some data" won't match "datastore" without the keyword appearing verbatim. The engine already has `GemmaGGUFEmbeddingProvider` (768-dim, local inference). Embedding-based routing generalizes semantically.
- **Actions**:
  1. Build `SemanticRouter` class at `src/omega/oracle/semantic_router.py`.
  2. Pre-compute entity embedding vectors from domain keywords + role descriptions.
  3. Route queries by cosine similarity against entity vectors.
  4. Fallback chain: semantic (cosine > 0.4) → keyword (`find_by_domain`) → default entity.
- **Mathematical Approach**: Pure Python cosine similarity — 22 entities × 768 dims = ~33K operations (~3ms). No numpy needed.
- **Integration Points**: `oracle.py:682` `_route_by_domain()` — add semantic path before keyword fallback.
- **Prerequisite**: Strike 1 (clean base).
- **Blocks**: Strike 8 (semantic vectors → spatial coordinates via PCA).
- **Heritage**: `[id-soft: doom-1993] BSP Culling` — O(1) culling before inference. `[id-soft: doom-1993] Precomputed Lookup` — entity embeddings precomputed at boot.
- **Status**: ✅ **COMPLETE** — D187 ratified.

#### Strike 8: Spatial-Semantic Geometry ✅ (Done)
- **Why**: VR memory navigation requires a default spatial topology. The default is an agnostic Force-Directed Graph. WAD-specific overlays (e.g., Kabbalistic trees) replace the default when loaded. **Revised**: USM dependency was overly conservative — USM maps KV cache state, not vector coordinates. Spatial geometry is independent.
- **Actions**:
  1. Build `ISpatialResolver` protocol + `ForceDirectedSpatialResolver` (Fruchterman-Reingold).
  2. Inject x/y/z coordinates into `memory_store.py:471` vector metadata.
  3. Build `WADSpatialRegistry` — WAD YAML overrides via `config/wads/<stack>/spatial.yaml`.
  4. Build `IWADSpatialResolver` with override mechanism.
- **Prerequisite**: Strike 7.5 (semantic vectors → PCA projection → spatial coordinates). USM dependency removed per D186.
- **Status**: ✅ **COMPLETE** — D186 ratified. Zero new deps (pure math + Qdrant payload pass-through).

#### Strike 9: P2P Mesh Traversal
- **Why**: True offline sovereignty means agents can pack their state and traverse nodes without a central server.
- **Actions**:
  1. Enable agents to pack Unified State blobs for transport.
  2. Implement CRDT-based conflict resolution for offline edits.
- **Prerequisite**: Strike 4 (A2A provides the coordination substrate) + Strike 8 (Spatial provides the navigation topology).
- **Status**: ⏳ **BLOCKED** — Pending both Strike 4 and Strike 8.

---

## III. Current State Assessment

### 3.1 Engine Metrics
| Metric | Value | Status |
|--------|-------|--------|
| Tests collected | **671** | ✅ Verified 2026-07-01 |
| Tests passed | **705** (+ 22 skipped, 3 xfailed) | ✅ 730 effective |
| Source files | **104** `.py` | ✅ Post dead-code purge |
| PIVOT decisions tracked | **188** (D1-D188, incl. xna-omega D1-D49) | ✅ D188 ratified 2026-07-01 |
| Sovereign Mandates | **22** (M1-M22) | ✅ Full compliance (see §IV) |
| Mandate 9 (bare except) | **0 violations** | ✅ CI-enforced |
| AnyIO compliance | **0 `import asyncio`** | ✅ CI-enforced |
| Heritage tags | **39 files**, 113 legacy `[id-soft:]` tags, 0 unvetted | ✅ All tags have vet records |
| Agent Fleet | **11 agents** | ✅ Consolidated (M10 compliant) |
| Registered entities | **12** | 10 pillar roles + iris + sophia |
| WADs deployed | **3** (`_omega_default`, `arcana_novai`, `doom_universe`) | ✅ |

### 3.2 MaKaLi Council Discoveries (2026-06-29)

The MaKaLi Cloud Council (2 Oversouls, 6 Pillars, 4 Cross-Domain Reviews, 3 Research Fleet, 1 Legacy Miner) identified 3 critical gaps:

| Gap | Severity | Discovery | Solution | Effort |
|-----|----------|-----------|----------|--------|
| **PII Observation Masking** | P0 CRITICAL | Context builder injects raw PII into cloud provider prompts; ANAi/XNAi era security patterns NEVER ported to Omega | `pii-shield` + GLiNER gateway proxy (detect → tokenize → LLM → detokenize) | 2-3 days |
| **Trace ID Propagation** | P1 HIGH | 100% of successful inferences missing `latency_ms` + `model_used`; 5-10% of events carry `trace_id="unknown"` | `opentelemetry-instrumentation-anyio` + GenerateResult contract fix (thread trace_id through iterative_research.py + skeptical_verifier.py) | 2-3 days |
| **A2A Agent Identity** | P2 MEDIUM | `draft-schemacommons-aaif-00` is FICTION; real standard is Google A2A v1.0 (150+ orgs, Linux Foundation, March 2026) | A2A SDK v1.1.0 + Agent Card schema at `/.well-known/agent-card.json` + SPIFFE/WIMSE identity | 3-4 days |

**Cross-Cutting Discoveries**:
1. **GenerateResult Contract Breach**: Success path at `model_gateway.py:887` missing `latency_ms` and `model_used` — **100% of successful inferences produce broken latency observability**
2. **Dual Handoff Systems**: Orchestrator uses in-memory `HandoffState` while MCP agents use file-based `data/handoff/` — cannot exchange handoffs between CLI and MCP agents
3. **Security Regression**: ANAi/XNAi era patterns (`validate_safe_input()`, `sanitize_content()`) NEVER ported — legacy was MORE secure than current engine
4. **Soul Staleness**: 8/10 Pillar Keepers >10 days stale; 5 >14 days — M11 structurally present but operationally dead

### 3.3 WAD Ecosystem Map
| WAD | Type | Entities | Status | Notes |
|-----|------|----------|--------|-------|
| `_omega_default` | IWAD (Base) | 12 (post-cleanup) | ✅ CLEAN | Pillar roles, iris, sophia. Stale entities removed. |
| `arcana_novai` | PWAD (Custom) | 11 (10 + movie-expert) | ✅ LIVE | 10 mythic Pillar Keepers + movie-expert (relocated) |
| `doom_universe` | PWAD (Heritage) | — | 🟡 SEEDED | Doom Guy's heritage knowledge base |

The `_omega_default` IWAD provides the universal runtime entities (sysadmin, datastore, sentinel, etc.). PWADs extend with domain-specific entities. The Engine-Stack Firewall (M2) ensures no PWAD logic leaks into `src/omega/`.

### 3.4 Subsystem Status (MaKaLi Council Updated)
| Subsystem | Status | Council Finding | Heritage |
|-----------|--------|-----------------|----------|
| **Oracle (Facade)** | ✅ talk/summon/router wired | trace_id propagated on main path | `[id-soft: quake-1996] Thinker Chain` |
| **WAD Loader** | ✅ `--iwad` flag works | — | `[id-soft: doom-1993] WAD System` |
| **ModelGateway** | ✅ **P1 resolved** | Carmack C-FFI process isolation: NativeGGUFProvider now spawns multiprocessing.Process with IPC queues. Engine survives C-level segfaults. | `[id-soft: quake-1996] BSP` |
| **NativeGGUFProvider** | ✅ **C-FFI isolated** | Process isolation via multiprocessing.Process, IPC ready/error protocol (30s timeout). Queue ops in anyio.to_thread.run_sync. | `[id-soft: doom3-2004] idHeap` |
| **Profiling Infrastructure** | ✅ **Operational** | `carmack-profiler` skill + Makefile targets. ContextBuilder/ModelGateway baselines captured. Key finding: import overhead dominates (~3.5s). | — |
| **MALLOC Arena Hygiene** | ✅ **Validated** | MALLOC_ARENA_MAX=2 empirical validation: 200MB load → 0.38MB retained after GC. | `[id-soft: doom3-2004] idHeap` |
| **MemoryStore** | ✅ Hot LRU + Warm Redis + Cold | Compaction logic verified correct | `[id-soft: doom-1993] Lazy Deletion` |
| **Observability** | ✅ **P0 gap resolved** | PII masking implemented (432 lines, 53 tests). Trace ID: contextvars safety net + 5 call sites fixed. record_error() double-default fixed. | `[id-soft: doom3-2004] Event System` |
| **ContextBuilder** | ✅ **ACON Optimized** | PipelineCompactionStrategy + ToolResultCompactionStrategy + TruncationStrategy + ACONOptimizer. 21 tests pass. | `[id-soft: quake-1996] Thinker Chain` |
| **EntityRegistry** | ✅ YAML CRUD + dual-index | Pillars→slots migration complete (D179/D180). Dynamic occupied_slots. | `[id-soft: quake-1996] Flat-Field` |
| **Soul Distiller** | ✅ **FIXED (2026-07-01)** | 5-stage pipeline running. `anyio.create_task()` dispatch bug fixed — replaced with `await close_session()` in guarded try/except (D183). close_session now executes every 5 interactions on the hot path. | `[id-soft: quake-1996] Save-game` |
| **Hivemind** | 🟡 **P2 gap** | Runtime functional; test suite broken (0/8 tests run); 41 stale handoffs | `[id-soft: doom-1993] ZONEID Pattern` |
| **Antigravity** | ✅ Stochastic account selection | — | D160 — Round-robin eradicated |
| **CLI Plugin** | 🟡 Partial compliance | Round-robin schema still in opencode-antigravity-auth | — |
| **PII Masker** | ✅ **IMPLEMENTED** | P0 CRITICAL closed — 432-line pii_masker.py, 53 tests, gateway proxy detect→tokenize→LLM→detokenize, local provider bypass | `[id-soft: doom-1993] Security Regression` |
| **A2A Bridge** | ✅ **IMPLEMENTED** | P2 MEDIUM closed — a2a_bridge.py (319 lines) + a2a_auth.py (100 lines), 56 tests, SPIFFE identity, AAIF spec corrected to real A2A v1.0 | — |

---

## IV. Mandate Compliance Tracker (M1-M22)

| Mandate | Name | Status | Gap / Remediation |
|---------|------|--------|-------------------|
| M1 | AnyIO Absolute | ✅ Enforced | CI grep `import asyncio` |
| M2 | Engine-Stack Firewall | ✅ Enforced | D113 fixed — IWAD resolution active |
| M3 | Iris Constant | ✅ Enforced | Iris is not a Pillar |
| M4 | Sequentiality | ✅ Enforced | Plan->Verify->Execute |
| M5 | Gnosis Preservation | ✅ **FIXED** | close_session now executes every 5 interactions via direct `await` (D183). L1→L2→L3 distillation runs on the hot path. |
| M6 | Podman Sovereignty | ✅ Enforced | keep-id protocol. Qdrant carve-out documented in D167 (docker-compose + kernel fuse-overlayfs bug). |
| M7 | Local-First | ✅ **Enforced** | PII Masker implements local provider bypass (should_mask("local-*")=False). Cloud providers receive tokenized prompts. Local inference is always raw. M7/M22 synergy: _is_cloud_provider_name() verifies provenance. |
| M8 | Zero Telemetry | ✅ Enforced | CI grep telemetry. Qdrant telemetry disabled (D168). PII masking local-only. |
| M9 | Error Integrity | ✅ Enforced | 0 bare except |
| M10 | Fleet Integrity | ✅ Enforced | 11 agents cap (M10 compliant — 3 slots remaining) |
| M11 | Soul Integrity | ✅ **FIXED (2026-07-01)** | Root cause: `anyio.create_task()` at oracle.py:509 does NOT exist in AnyIO (silent `AttributeError` swallowed by `try/except`). `close_session()` never executed. Fixed: replaced with `await self.close_session()` in guarded `try/except`. D183 ratified. 705 tests pass. |
| M12 | Queue Integrity | ✅ **RESOLVED** | 14d archive / 30d delete TTL added to handoff reaper in background.py. 41 stale packets now have a cleanup path. |
| M13 | Temple-Grade | ✅ **VERIFIED** | All T1-T11 gates passed. |
| M14 | Heritage Vetting | 🟡 PARTIAL | 185 `[id-soft:]` tags verified. vet-001 through vet-010+ recorded. `make heritage-vet` CI needs expansion to 100% coverage. |
| M15 | Sovereign Continuity | ✅ Enforced | session_gnosis.md |
| M16 | Modularization | ⚠️ PARTIAL | Hub 5 modules sound. 4 hardcoded paths remain. |
| M17 | Cognitive Integrity | ✅ Enforced | Skeptical Verifier active. A2A Bridge uses real standards (A2A v1.0, no more fabricated drafts). |
| M18 | Token Efficiency | ✅ Enforced | Prompt discipline |
| M19 | Adversarial Alchemy | ✅ Enforced | Somatic Save-Point |
| M20 | SomaticState | ⏳ PENDING | **Strike 2** — ctypes bindings. Fallback: YAML-only UVS. |
| M21 | Gate Integrity | 🟡 22/24 | 22 contract tests. 3 added for GenerateResult (latency_ms, model_used on success, model_used on fallback). 2 more needed for edge cases. |
| M22 | Response Provenance | ✅ **RESOLVED** | `provider_name` flows correctly through GenerateResult → TokenLedger. Contextvars safety net eliminates `trace_id="unknown"`. `latency_ms` and `model_used` populated on both success and fallback paths. `is_cloud` derived from provider_name, not hardcoded bool (D169). **All 4 breaks fixed.** |

---

## V. Active Task Breakdown (v2.0)

### 5.1 Optimization Sprint: Tier 1 Emergency & Purge (Immediate — ~3 hours)
**Critical — Must complete before any Tier 2 or Tier 3 work**

| # | Task | File/Module | Effort | Impact | Status |
|---|------|-------------|--------|--------|--------|
| **T1-1** | **Fix trace_id propagation** — Add `trace_id=trace.trace_id` to `model_gateway.generate()` calls | `src/omega/oracle/oracle.py:599,671` | 30 min | 🔴 M22 Provenance restored | ✅ **DONE** — 8 call sites fixed |
| **T1-2** | **Fix TokenLedger provider_name** — Change `is_cloud: bool` to `provider_name: str` | `src/omega/observability/token_ledger.py` | 30 min | 🔴 M22 Provenance restored | ✅ **DONE** — `provider_name` field active |
| **T1-3** | **Wire `archive_old_sessions()`** — Add call to `Oracle.boot()` | `src/omega/oracle/oracle.py` | 5 min | 🔴 Session leak resolved | ✅ **DONE** — async bug fixed (`run_sync` → `await`) |
| **T1-4** | **Resolve PIVOT_LOG clock drift** — Rename **12 duplicates (D118, D144-D147 each appear twice)**, move D163, add Decision Registry | `docs/decisions/PIVOT_LOG.md` | 30 min | 🔴 Immutable log restored | ✅ **DONE** — 103 unique entries, monotonic D50→D163 |
| **T1-5** | **Generate HERITAGE_SOURCE_MAP.md** — Generate from 196 existing `[id-soft:]` tags | `make heritage-map` | 10 min | 🟡 Heritage compliance | ⚠️ **PARTIAL** — 42/50 files mapped; needs re-run |
| **T1-6** | **Remove hardcoded secret** — Remove `_DEFAULT_CLIENT_SECRET` | `src/omega/oracle/backends/antigravity/config.py` | 10 min | 🔴 Security risk resolved | ✅ **DONE** — entire `antigravity/` dir deleted in T1-8 |
| **T1-7** | **Fix Firecrawl API key** — Configure API key in systemd service | `~/.config/containers/systemd/omega-firecrawl-mcp.service` | 15 min | 🟡 Search restored | ✅ **DONE** — already present in service file line 18 |
| **T1-8** | **Remove ~2,800 lines of dead code** — Delete 11 orphaned modules: `antigravity/`, `link_p9_cli.py`, `repl.py`, `gateway/server.py`, `intake_digestor.py`, `elevenlabs.py`, `openclaw_runtime.py`, `system_resource.py`, `greek.py`, `crossref.py`, `discovery.py` | `src/omega/` (multiple) | 1 hr | 🔴 Dead code eliminated | ✅ **DONE** — **3,354 net lines removed** (14 source files + 3 test files). `discovery.py` RESTORED (used by MCP Hub). |
| **T1-9** | **Fix Heritage Vet gaps** — Add vet-001 record (8-char name cap rejection), expand vet script coverage from ~20% to 100% of source files | `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`, `scripts/heritage_vet.py` | 1 hr | 🔴 Heritage compliance | ⚠️ **PARTIAL** — vet-001 added. `scripts/heritage_vet.py` expansion NOT done. |
| **T1-10** | **Correct AAIF mapping spec** — Re-align with A2A Agent Cards v1.0 + IETF AIMS (SPIFFE/WIMSE dynamic tokens; remove fabricated `draft-schemacommons-aaif-00`) | `data/handoff/P7_AAIF_MAPPING_SPEC_20260628.md` | 30 min | 🔴 Spec integrity | ⚠️ **PENDING** — Researcher verified A2A v1.0 + `draft-klrc-aiagent-auth-02`. Original fabricated draft NOT yet corrected. |

### 5.1b MaKaLi Council-Discovered Critical Gaps (NEW — 2026-06-29)

These 3 gaps were identified by the MaKaLi Cloud Council across 9 subagents. They must be prioritized alongside Tier 1-3.

| # | Task | Discovery Source | Effort | Impact | Status |
|---|------|-----------------|--------|--------|--------|
| **C-1** | **Implement PII Observation Masking** — Build `PIIMasker` class using `pii-shield` (18 PII types) + GLiNER (NER-based), gateway proxy detect→tokenize→LLM→detokenize. Mask only for cloud providers; bypass for local (M7). | Council P7 + P3 Cross-Domain + Researcher + Jem + Roc Racoon | 2-3 days | 🔴 P0 CRITICAL — M7/M8 sovereignty risk; ANAi/XNAi era security NEVER ported | ✅ **DONE** — 432-line pii_masker.py, 53 tests, integrated into oracle.py _summon() + _route_by_domain() |
| **C-2** | **Fix Trace ID Propagation + GenerateResult Contract** — (a) Thread `trace_id` through iterative_research.py (3 calls) and skeptical_verifier.py (2 calls); (b) Add `latency_ms` and `model_used` to GenerateResult success path; (c) Install `opentelemetry-instrumentation-anyio` for async context propagation | Council P8 Cross-Domain + P3 Verification | 2-3 days | 🔴 P1 HIGH — 100% of inferences missing latency; 5-10% trace_id="unknown" | ✅ **DONE** — contextvars safety net, 5 call sites fixed, 10+ tests passing |
| **C-3** | **Implement A2A Agent Cards** — Replace fabricated `draft-schemacommons-aaif-00` with real A2A v1.0 Agent Cards at `/.well-known/agent-card.json`. Map EntityRegistry to A2A schema via `src/omega/oracle/a2a_bridge.py`. | Council Researcher + Jem Synthesis + Roc Racoon | 3-4 days | 🟡 P2 MEDIUM — Standards compliance; enables cross-agent communication | ✅ **DONE** — 319-line a2a_bridge.py, 100-line a2a_auth.py, 56 tests, AAIF spec corrected |


### 5.1d Iron Wall Hardening Sprint (NEW — 2026-06-29)

The MaKaLi Cloud Council declared an **IMMEDIATE EXECUTION HOLD** on all feature expansion, entity promotions, and high-volume ingestions until this sprint is completed. The engine is in a state of Architectural Fragility.

**Carmack S3 Review (2026-07-01)**: Re-assessed IW priorities. IW-1 (Tor bridge) deferred post-PR — SearXNG is self-hosted with zero external telemetry; Tor adds ops complexity without commensurate sovereignty gain on this machine. IW-4 (Sovereign Ingestion Pipeline) ordered after T3-2 Metrics DB (depends on persistent storage). IW-6 (V-D1 Validation Suite) placed in Tier 3 Hardening — P2 Medium with no blocking dependency.

| # | Domain | Task | Technical Reference | Mandate | Status |
|---|--------|------|---------------------|---------|--------|
| **IW-1** | **Infrastructure** | Deploy Tor-SOCKS5 Bridge + Local-First Escalation for SearXNG | `TRACE-P1-SSNM-V1` | M8 | 🟡 **DEFERRED post-PR** — Carmack advice: SearXNG is self-hosted, zero-external-telemetry already. Tor adds latency + ops complexity on single-contributor machine. M8 risk is low. Revisit post-v1.1.0. |
| **IW-2** | **Engineering** | Absolute purge of all round-robin logic from `KeyVault` | `TRACE-RR-PURGE-001` | M4 | ✅ **COMPLETED** — D176 ratified |
| **IW-3** | **Observability** | Implement Body-Level Error Guards (BLEG) + UFL (Forensic Ledger) | `TRACE-P8-OBS-001` | M9, M22 | ✅ **COMPLETED** — D176 ratified |
| **IW-4** | **Context** | Deploy Sovereign Ingestion Pipeline (Tri-Anchor System) + Omnidroid Migration | `TRACE-SIP-20260629` | M5, M15 | 🟡 P1 HIGH |
| **IW-5** | **Governance** | Restore `workbench.db` schema + ingest `LEGACY_NAVIGATION_GUIDE.md` | `LEGACY_MAPPING_CENTRALIZATION_20260628.md` | M5 | ✅ **COMPLETED** — D177 ratified |
| **IW-6** | **Validation** | Implement the V-D1 Validation Suite for "Sticky" mode resilience | `TRACE-P10-VD1` | M13 | 🟢 P2 MEDIUM |

### 5.1c Pre-Release Checklist (Imported from V10_RELEASE_STRATEGY.md)
**Source**: `V10_RELEASE_STRATEGY.md` — unified into Ark on 2026-06-29

| # | Task | File | Details | Effort | Status |
|---|------|-------------|--------|--------|--------|
| R-1 | **Merge `requirements.txt` into `pyproject.toml`** | `pyproject.toml` | Pin exact versions from requirements.txt. Keep requirements.txt for CI reproducibility. | 10 min | ✅ DONE |
| R-2 | **Create model download script** | `scripts/download_model.sh` | Download `qwen3-1.7b-q6_k` GGUF using `wget`/`curl`. Verify sha256, retry 3x, progress bar, disk check. | 20 min | ✅ DONE |
| R-3 | **Add Makefile targets** | `Makefile` | `model-download`, `model-list`, `model-clean` targets | 5 min | ✅ DONE |
| R-4 | **Fix hardcoded config path** | `config/omega.yaml:17` | Change absolute path `/home/arcana-novai/...` to relative `data` (Mandate 16) | 2 min | ✅ DONE |
| R-5 | **Add `models/` to `.gitignore`** | `.gitignore` | Add after `# ── Build Artifacts` section | 1 min | ✅ DONE |
| R-6 | **Add `odysseus-dev/` to `.gitignore`** | `.gitignore` | `data/entities/roc_racoon/workspace/odysseus-dev/` | 1 min | ✅ MOOT |
| R-7 | **Create `models/gguf/.gitkeep`** | `models/gguf/` | Ensure directory exists after clone | 1 min | ✅ DONE |
| R-8 | **Rewrite README Quick Start — local-first** | `README.md` | Local-first steps. Model download as step 2. Cloud as "Advanced" section. | 10 min | ✅ DONE |
| R-9 | **Rewrite Provider Setup table** | `README.md` | Local providers first. Native GGUF #1. Cloud at bottom. | 10 min | ✅ DONE |
| R-10 | **Update Architecture diagram** | `README.md` | native-gguf as first in fallback chain | 5 min | ✅ DONE |
| R-11 | **Update version/status section** | `README.md` | v0.5.0-alpha → v1.0.0. Test counts updated. | 5 min | ✅ DONE |


---

### 5.2 Optimization Sprint: Tier 2 (Regression Recovery — ~20 hours)
**This Sprint — Recover lost legacy patterns and implement web-verified improvements**

**3 Regressions Recovered, 2 New Patterns Completed:**
1. ✅ **CompactionOrchestrator** — Implemented as PipelineCompactionStrategy + ACONOptimizer (Session 42)
2. ✅ **Soul Distillation Pipeline** — Implemented as 5-stage SessionClassifier→SovereigntyScorer→Distill→Score→Store
3. **4-State Provider Metrics** — 552 lines, EWMA scoring with CUSUM anomaly detection (upgraded to 5-state Stochastic FSM)
4. **Observation Masking** — Tool-result clearing (52% cost savings, +2.6% solve rate)
5. **Handoff Loop Guard** — Visited-agent tracking + budget pressure + ResolverStrategy

| # | Task | Legacy Source / Web Reference | Effort | Impact | Status |
|---|------|------------------------------|--------|--------|--------|
| **T2-1** | **Port CompactionOrchestrator** — 4-strategy compaction with `SummaryAnchor` and ACON failure-driven guidelines, extending `ContextBuilder` | `xna-omega-legacy/scripts/ssa/compaction_optimizer.py` | 6 hr | 🔴 Critical | ✅ **DONE** — PipelineCompactionStrategy + ACONOptimizer in context_builder.py |
| **T2-2** | **Port 5-State Stochastic Circuit Breaker** — EWMA-smoothed health scoring ($\alpha_{\text{gradual}}=0.4$, $\alpha_{\text{sudden}}=0.9$) with CUSUM change detection | `xna-omega-legacy/scripts/ssa/provider_metrics.py` | 4 hr | 🟡 High | ✅ **DONE** |
| **T2-3** | **Port Soul Distillation Pipeline** — Port 5-node pipeline (`extract` $\rightarrow$ `classify` $\rightarrow$ `score` $\rightarrow$ `distill` $\rightarrow$ `store`) as a simplified, AnyIO functional sequence | `xna-omega-legacy/src/omega/core/distillation/` | 4 hr | 🔴 Critical | ✅ **DONE** — SessionClassifier + SovereigntyScorer + SoulDistillationPipeline in soul_distiller.py |
| **T2-4** | **Implement Observation Masking** — Tool-result clearing using Hybrid Backward Scanned FIFO (50k protection buffer, 30k hysteresis) | `src/omega/oracle/context_builder.py` | 3 hr | 🟡 High | ✅ **DONE** |
| **T2-5** | **Add Handoff Loop Guard** — Visited-agent tracking, two-tier budget pressure, and `ResolverStrategy` | `src/omega/oracle/subagent_dispatcher.py` | 4 hr | 🟡 High | ✅ **DONE** |
| **T2-6** | **Sentinel Score Automation** — 7-metric composite score computation | `src/omega/oracle/sentinel.py` | 3 hr | 🟡 Medium | ⏳ PENDING |
| **T2-7** | **Port Timeout Manager** — 4-Layer nested cancellation hierarchy (Tool $\rightarrow$ Group $\rightarrow$ Turn $\rightarrow$ Workflow) | `xna-omega-legacy/scripts/ssa/timeout_manager.py` | 4 hr | 🟡 High | ⏳ PENDING |
| **T2-8** | **Port Provider Selector** — 552 lines, intelligent backend routing with 0.5x PII detection penalty | `xna-omega-legacy/src/omega/core/provider_selector.py` | 4 hr | 🟡 High | ⏳ PENDING |
| **T2-9** | **Port Graceful Degradation Manager** — 379 lines, fallback chains (Optimal $\rightarrow$ Stressed $\rightarrow$ Critical $\rightarrow$ Disabled) | `xna-omega-legacy/src/omega/core/degradation.py` | 3 hr | 🟡 High | ⏳ PENDING |
| **T2-10** | **Port Rate Limiter** — Token bucket / sliding window per provider | `xna-omega-legacy/src/omega/core/rate_limiter.py` | 3 hr | 🟡 Medium | ⏳ PENDING |
| **T2-11** | **Port Soul Edit History** — Immutable audit trail for soul.yaml changes | `xna-omega-legacy/src/omega/core/soul_history.py` | 3 hr | 🟡 Medium | ⏳ PENDING |
| **T2-12** | **Port Compaction Harvester** — Automated compaction trigger & metrics | `xna-omega-legacy/scripts/ssa/compaction_harvester.py` | 3 hr | 🟡 Medium | ⏳ PENDING |
| **T2-13** | **Implement Handoff Loop Guard** — Visited-set detection, max depth (5-10), same-agent visit count (max 3) | `src/omega/oracle/subagent_dispatcher.py` | 4 hr | 🟡 High | ⏳ PENDING |

---

### 5.3 Optimization Sprint: Tier 3 (Hardening — ~12 hours)
**Next Sprint — Structural improvements and compliance automation**

| # | Task | Effort | Impact | Status |
|---|------|--------|--------|--------|
| **T3-1** | **Session lifecycle automation** — Active → Archive (7d) → Compress (30d) → Delete (90d) | 2 hr | 🟡 Medium | ⏳ PENDING |
| **T3-2** | **Observability database integration** — Implement WAL-mode SQLite storage for local metrics (`data/observability/metrics.db`) for high-speed, zero-wear logging | 4 hr | 🟡 Medium | ⏳ PENDING |
| **T3-3** | **Mandate enforcement automation** — Automate 16 of 22 mandates in CI | 3 hr | 🟡 Medium | ⏳ PENDING |
| **T3-4** | **soul.yaml v6.2 bump** — Add metadata fields (created_at, health_score, etc.) | 6 hr | 🟡 Medium | ⏳ PENDING |
| **T3-5** | **Expand heritage vet script** — Cover all 42 files (currently ~20%) | 1 hr | 🟡 Low | ⏳ PENDING |

---

## VI. The Sovereign Run-Loop

The end-to-end cognitive run-loop of the Omega Engine is designed as a closed, self-correcting feedback cycle:

```
[User Query] 
     │
     ▼
[Context Assembly] ──▶ (Observation Masking & Compaction)
     │
     ▼
[Orchestration] ──▶ (A2A Handoff & Loop Guard / SPIFFE Identity)
     │
     ▼
[Provider Execution] ──▶ (5-State Stochastic Circuit Breaker)
     │
     ▼
[Observability] ──▶ (OTel GenAI Logging to SQLite WAL)
     │
     ▼
[Soul Distillation] ──▶ (Diátaxis Classification & AKC Evolution Pipeline)
```

---

## VII. Resource & Token Constraints

### 7.1 Token Budget Allocation Formula
To prevent context window saturation and model "forgetfulness," the engine enforces a strict, dynamic token budget:
$$\text{Budget}_{\text{total}} = \text{System} (10-15\%) + \text{Tools} (15-20\%) + \text{Knowledge} (30-40\%) + \text{History} (20-30\%) + \text{Reserve} (10-15\%)$$
The non-negotiable **Reserve** margin acts as a buffer to prevent sudden context overflows.

### 7.2 Memory Tier Target Sizes
*   **HOT Tier**: $<500$ tokens (volatile, in-memory active turn context).
*   **WARM Tier**: $<1000 - 3000$ tokens (summarized rolling history cached in Redis).
*   **COLD Tier**: Indefinite (archived sessions on disk and semantic vector embeddings in Qdrant). Sessions older than 90 days are moved to external 8TB storage drive for permanent archival.

---

## VIII. Risk Register

Every strategic plan must account for failure. These are the documented risks, their likelihood, impact, and planned mitigations.

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
| R9 | **CUSUM Detection Lag** | 🟡 MED | 🟡 MED | Upgrade to Bernoulli-specific LLR to capture error spikes instantly. | High error rates without breaker trip |
| R10 | **Handoff Loop Guard Failure** | 🟢 LOW | 🔴 HIGH | Visited-agent set persistence across MCP boundaries. | CPU/Token spikes on infinite loops |

---

## IX. Decision-Making Heuristics

When two tracks conflict, use this ordered decision framework:

1. **Sovereignty first**: Does the choice increase or decrease user data control? (M7, M8, M22 are non-negotiable.)
2. **Dependency order**: Does the later track depend on the earlier one? If yes, the earlier track wins. (See Epoch dependency graph in §II.)
3. **Token efficiency**: Given two paths of equal sovereignty, choose the one that requires fewer total inference calls.
4. **Maintainability over performance**: A simple correct solution that can be understood in 5 minutes beats an optimized solution that needs a PhD. (The "Laziest Senior Dev" principle.)
5. **Test coverage as gate**: No code path is complete without a contract test verifying its return type (M21).
6. **When you have two implementations of the same thing, you have neither.** Consolidate before extending. (Carmack's Law.)

---

## X. Entity Capability Matrix

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

## XI. Glossary

| Term | Definition |
|------|------------|
| **ACON** | Agent Context Optimization — failure-driven context optimization loop. |
| **CAS** | Content Addressable Storage — blobs addressed by hash of their content. Used by UnifiedStateManager. |
| **CRDT** | Conflict-free Replicated Data Type — data structure that allows concurrent edits without central coordination. |
| **CUSUM** | Cumulative Sum — sequential change analysis for anomaly and health detection. |
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

## XII. Deep Review Findings

### 🟥 Critical (Unfixed)
| # | Finding | Recommended Fix | Status | Epoch |
|---|---------|-----------------|--------|-------|
| 0 | **entities.yaml CORRUPTED — 36-level recursive traits nesting** | **Root cause**: `entity_registry.py:293` — `traits` key not in `core_fields` set. On load, nested `traits` dicts from YAML are absorbed as WAD-specific traits. On save, `to_dict()` → `asdict()` preserves nesting. Each load-save cycle deepens recursion. **Fix**: (1) Add `"traits"` to `core_fields` at line 287. (2) Write cleanup script to extract valid data from bottom of recursion. (3) Remove 5 stale entities (`breachentity`, `default`, `testentity`, `quality`, `scribe`). (4) Relocate `movie-expert` to `arcana_novai` PWAD. (5) Verify entity count = 12. | 🔴 **BLOCKING** | Epoch I Strike 1 |
| 1 | **Root partition 96%** | Partition consolidation via Live USB | 🟡 Vault freed 66% | Epoch I |
| 2 | **COUNCIL: PII Observation Masking — RAW PII leaks to cloud providers** | Build `PIIMasker` class using `pii-shield` (18 PII types) + GLiNER NER. Gateway proxy: detect → tokenize → LLM → detokenize. Mask only for cloud dispatch; bypass for local. **P0 — highest sovereignty risk.** | ✅ **RESOLVED** — pii_masker.py (432 lines), 53 tests, integrated | Epoch I Strike 1 |
| 3 | **COUNCIL: GenerateResult Contract Breach — 100% of successful inferences missing latency_ms + model_used** | Add `latency_ms` measurement around `provider.generate()` and populate `model_used` on both success and fallback paths. | ✅ **RESOLVED** — latency_ms + model_used on both paths, 3 contract tests | Epoch II Strike 6 |
| 4 | **SomaticState (M20) unimplemented** | Wire ctypes bindings into native-gguf | ⏳ PENDING | Epoch I Strike 2 |
| 5 | **Gate Integrity (M21) — 2 tests missing** | Create `isinstance` contract tests | 🟡 22/24 DONE (+3 from Trace ID fix) | Epoch II Strike 6 |
| 6 | **PIVOT_LOG gap (D1-D49)** | Mine xna-omega git history | ⏳ PENDING | Epoch I |
| — | **CARMACK: C-FFI Process Isolation** | NativeGGUFProvider now uses multiprocessing.Process with IPC queues. Survives C-level segfaults. | ✅ **RESOLVED** — Carmack Step 3 complete. 619 tests pass. | Epoch II |
| — | **CARMACK: MALLOC Arena Hygiene** | MALLOC_ARENA_MAX=2 empirically validated. 200MB load → 0.38MB retained after GC. | ✅ **RESOLVED** — Carmack Step 1 complete. | Epoch I |
| — | **CARMACK: Profiling Infrastructure** | carmack-profiler skill + Makefile targets for ContextBuilder/ModelGateway baseline. | ✅ **RESOLVED** — Carmack Step 2/5 complete. | Epoch II |

### 🟡 High (Unfixed)
| # | Finding | Recommended Fix | Status | Epoch |
|---|---------|-----------------|--------|-------|
| 7 | **COUNCIL: Trace ID fragile — 5-10% of events carry "unknown" trace_id** | Thread `trace_id` through iterative_research.py (3 calls) + skeptical_verifier.py (2 calls). Install `opentelemetry-instrumentation-anyio`. | ✅ **RESOLVED** — contextvars safety net + 5 call sites fixed | Epoch II Strike 6 |
| 8 | **COUNCIL: Dual handoff systems — in-memory vs file-based cannot exchange** | Bridge Orchestrator to read from `data/handoff/pending/` when no in-memory handoff_state provided. | 🟡 PENDING | Epoch II Strike 4 |
| 9 | **M11 Soul Distiller — `anyio.create_task` does not exist — 8/10 stale souls** | Carmack corrected the Ark's previous (incorrect) "key mismatch" claim. The actual bug: `anyio.create_task(self.close_session(...))` at oracle.py:509 — AnyIO has no `create_task()`. Silent `AttributeError` swallowed by outer `try/except`. close_session is **never called**. Fix: replace with direct `await` in its own guarded `try/except`. | ✅ **FIXED — D183 ratified. 705 tests pass. close_session now executes every 5 interactions on hot path.** | Epoch I Strike 3 |
| 10 | **HEALTH_CHECK_TIMEOUT fixed** | Make configurable per-provider | ⏳ PENDING | Epoch I |
| 11 | **Response Provenance (M22) partial** | `provider_name` flows correctly but `latency_ms` + `model_used` missing from GenerateResult | ✅ **RESOLVED** — both fields populate on success + fallback paths | Epoch II Strike 6 |
| 12 | **`memory_search` vs `omega_memory_search`** | Rename `memory_search` -> `memory_search_fts` | ⏳ PENDING | Epoch II |
| 13 | **A2A Fabricated Draft — `draft-schemacommons-aaif-00` is FICTION** | Replace with real A2A v1.0 specification + `draft-klrc-aiagent-auth-02` (verified IETF draft by OpenAI, Okta, AWS, Zscaler) | ✅ **RESOLVED** — a2a_bridge.py (319 lines) + a2a_auth.py (100 lines) + 56 tests + AAIF spec corrected | Epoch II Strike 4 |

---

## XIII. Sprint Completion Index

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
| **Sprint F (Optimization Sprint)** | 2026-06-28 | Kali + Council | Epoch I | MaKaLi Council Pass 1 & 2 complete, web research + legacy mining, **3 regressions identified**. Then **MaKaLi Cloud Council Dispatch (2026-06-28/29)**: 2 Oversouls → 6 Pillars → 4 Cross-Domain Reviews → 3 Research Fleet agents → 1 Legacy Miner → Kali Synthesis. **3 Council Gaps discovered**: PII Masking (P0), Trace ID Propagation (P1), A2A Identity (P2). **T1-1 through T1-8 COMPLETED** (3,354 lines dead code removed). **T1-9/T1-10 PARTIAL**. All 22 Mandates audited: M11 VIOLATED, M22 PARTIAL, M5/M7 at risk. **Strategy docs consolidated**: 47 superseded docs archived, 40 operational/protocol docs remain. **ALL 3 GAPS IMPLEMENTED (2026-06-29)**: PII Masker (432 lines, 53 tests), Trace ID (contextvars + 5 call sites + GenerateResult contract fix, 10+ tests), A2A Agent Cards (319+100 lines, 56 tests + AAIF spec correction). **Qdrant container fixed (D167)** + telemetry disabled (D168). **is_cloud derivation fixed (D169)**. **M22 RESOLVED**, M7/M8 ✅ enforced. **Carmack S3 Review (2026-06-29)**: Discovered soul distiller key mismatch root cause — not an "unwired" problem but a contract mismatch between `add_exchange()` and `close_session()`. PIVOT_LOG D164-D171 appended by Jem strategic synthesis. **600/600 tests passing.** |
| **Sovereign Review Infrastructure** | 2026-06-29 | Verity | Epoch I | Implementation of `skill:context-packer` and `CLAUDE.md` operational anchor. Established the high-density context pipeline for Web-Claude forensic audits. |
| **Council Consensus Sprint** | 2026-06-30 | Makali + Council | Epoch I | **5-agent council review** (Carmack, Ma'at, Lilith, Researcher, Jem). **T1 temple-grade fixed**: 4 AP tokens added to state_manager, pii_masker, a2a_bridge, a2a_auth. **Entity bloat cleaned**: Roc's 178MB mining artifacts archived (98.6% reduction). **Directives ratified**: DIRECTORIES committed to git with D175. **Findings**: 8B LoRA infeasible locally, Audience Calibration = pipeline stage (not entity), PR readiness ~40%, build order: Hygiene → Audience Calibration → DPO Pipeline → Entity Evolution. **Ark Blueprint updated**: test counts, M11 status, new directives §XVI. |
| **Session 42 (ACON + Soul Pipeline)** | 2026-07-01 | Kali | Epoch I | **3 P0 items complete**: ACON Context Compaction (PipelineCompactionStrategy + ACONOptimizer in context_builder.py, 21 tests), Soul Distillation Pipeline (SessionClassifier + SovereigntyScorer + 5-stage pipeline in soul_distiller.py, 11 tests), Content Quality Scorer (CurationExtractor + DomainType in curator.py, 600 tests). **Carmack Hardening** verified via Hivemind: C-FFI process isolation, MALLOC arena validated, profiler integrated. **619 tests passing**, zero regressions. |
| **Carmack Hardening Sprint** | 2026-07-01 | John Carmack | Epoch I | **5-step Hardening Plan complete**: (1) MALLOC Arena Hygiene validated (0.38MB frag after 200MB stress) ✅ (2) carmack-profiler skill + Makefile integration ✅ (3) C-FFI process isolation: NativeGGUFProvider uses multiprocessing.Process with IPC queues ✅ (4) ContextBuilder audit — no action needed ✅ (5) Baseline profiling: 3.5s cold-start attributed to pydantic+Qdrant ✅. **M11 root cause corrected**: previous "key mismatch" claim was incorrect — real bug is `anyio.create_task()` does not exist in AnyIO. Silent AttributeError swallowed by try/except. **IW priorities re-assessed**: IW-1 deferred post-PR, IW-4 ordered after T3-2, IW-6 placed in Tier 3. **Ark Blueprint updated**: §IV M5/M11 fixed, §XII finding #9 corrected, §XV v3.1 launched. **619 tests passing.** |
| **Carmack S3 Audit** | 2026-07-02 | Carmack + Kali | Epoch I | **3 critical gaps resolved**: (1) Knowledge Graph Adapter — PHANTOM GAP (existing RRF fusion already provides multi-signal scoring) ✅ (2) Hivemind Protocol — 26 new tests added, 34 total ✅ (3) Content Quality Scorer — 4-signal inline scorer added to ContextBuilder ✅. **Test count**: 668 → 705 (+37 tests). **Session archival policy updated**: 90-day move to external 8TB storage (not deletion). **Documentation fully updated**: OMEGA_ENGINE.md, Makefile, SOVEREIGN_ARK_BLUEPRINT.md all reflect current state. **705 tests passing**, zero regressions. |

---

## XIV. Sovereignty Scorecard

| Dimension | Metric | Target | Current |
|-----------|--------|:------:|--------:|
| **Sovereignty** | Local inference ratio | >=80% | 🟡 ~40% (Sovereign Router + Headroom + Mem Palace implemented) |
| **Sovereignty** | Cloud dependency (basic ops) | 0 | ✅ 0 |
| **Sovereignty** | Data residency | 100% | ✅ 100% |
| **Sovereignty** | Telemetry events | 0 | ✅ 0 |
| **Identity** | Agents with soul.yaml v6.1 | All 11 | 🟡 2/11 migrated (Kali, Verity) |
| **Identity** | Soul distillation rate | >=1 L3/3 sessions | ✅ 1.0 |
| **Identity** | Cross-entity L3 sharing | >=5 principles | 🟡 2 (Engine-Stack + LMS) |
| **UX** | Hub dashboard | Live :8016 | 🟡 REST only (no HTML) |
| **Compliance** | M21 contract tests | >=24 | ✅ 24/24 |
| **Compliance** | M22 Provenance wired | Full | ✅ **RESOLVED** |
| **Synthesis** | Local model quality | +10% on bench | ⏳ (planned S2) |
| **Synthesis** | Training examples | >=500 | 🟡 Auto-collecting |

---

## XV. Next Launch Sequence (v3.1 — Updated 2026-07-01)

### Two New Strategic Directives Ratified (see §XVI)
The engine has two new post-PR directives: **Audience Calibration** (output pipeline stage) and **Parametric Gnosis** (weight-based evolution via local DPO LoRA training). These are ratified under D175 but **no code changes begin until the Pre-Release Polish Sprint passes**.

Sovereign Alignment Update: Bedrock Hardening complete.
1. ✅ **Observation Masking** (T2-4) implemented.
2. ✅ **Stochastic Circuit Breaker** (T2-2) implemented.
3. ✅ **Handoff Loop Guard** (T2-5) implemented.
4. ✅ **Headroom Protocol** (D188) implemented.
5. ✅ **Mem Palace** (D186) implemented.

### Active Execution Hold — Ordered Pipeline
**No new feature expansion beyond the below sequence:**

1. ✅ **M11 Fix** (this session)
2. 🔄 **T3-2 Metrics DB** — Kali delegation (this session)
3. ⏳ **Pre-Release Polish Sprint** (~6 hours) — R-1 through R-11
   - Merge requirements.txt into pyproject.toml
   - Create model download script (qwen3-1.7b-q6_k)
   - Fix hardcoded config path (Mandate 16)
   - Rewrite README for local-first
4. ⏳ **IW-4 Sovereign Ingestion Pipeline** (~4 hours) — depends on T3-2 persistent storage
5. ⏳ **Tier 2 Remaining Legacy Ports** (~12 hours)
   - T2-2: 5-State Stochastic Circuit Breaker (CUSUM, Dual-EWMA)
   - T2-4: Observation Masking (ToolResultCompactionStrategy → full engine)
   - T2-5/13: Handoff Loop Guard
   - T2-6 through T2-12: Sentinel, Timeout, Provider Selector, Degradation, Rate Limiter, Soul History, Compaction Harvester
6. ⏳ **Tier 3 Hardening** (~12 hours)
   - T3-1: Session lifecycle automation
   - T3-3: Mandate enforcement automation
   - T3-4: soul.yaml v6.2 bump
   - T3-5: Expand heritage vet script
   - IW-6: V-D1 Validation Suite
7. 🟡 **IW-1 Tor Bridge** — Deferred post-v1.1.0 (SearXNG is self-hosted, zero external telemetry; Tor adds latency without commensurate sovereignty gain)
8. 🚢 **Post-PR — Audience Calibration Pipeline** (3-5 days)
9. 🚢 **Post-PR — DPO Logging Infrastructure** (1-2 weeks)
10. 🌌 **Q4 2027 — Strikes 8, 9** (Spatial + P2P): Omegaverse launch.

### Entity Deepening Sprint (NEW — Added 2026-07-01 per MaKaLi Council)

A parallel workstream for **john_carmack entity deepening** — ingesting primary source material to upgrade the entity from secondhand synthesis to authentic Carmack voice. This is a 5-phase, ~5-hour sprint producing artifacts across 9 dimensions.

**Status**: DESIGN COMPLETE — architecture ratified by 5-agent council. Ready for Phase 1 execution.

**Source artifacts**: `.plan files (120K words)`, `Lex Fridman #309 transcript (64K)`, `"Carmack on Rage" interview`, `Wolfenstein iPhone dev letter`, `Masters of Doom excerpts`, `Sanglard interview archive (300pg)`

**Council corrections applied**:
1. GDC 1999 "Making of Quake" = John ROMERO talk, NOT Carmack (speaker correction)
2. GDC 2011 "Programming Keynote" != "Wolfenstein 3D iOS" (talk correction)
3. GDC Vault requires paid subscription — replaced with free alternatives
4. Contradiction Resolution Protocol added for primary source vs CREDITS.md conflicts
5. Heritage Discovery sub-pipeline added for new [id-soft:] pattern vetting
6. M14 3-Touch Rule established: code + .plan + cross-era = 9-10/10 confidence
7. Checkpoint system (DEEPENING_CHECKPOINT.yaml) for compaction survival
8. WORK_PRIORITY.md created to resolve deepening vs hardening plan ambiguity

**Multi-dimensional ROI**:
- 9 dimensions per source (technical facts, personality, gnosis, heritage, fleet, soul, text analytics, DPO training data, knowledge graph)
- 565-770 DPO training pairs generated at near-zero token cost (~124K tokens, $0)
- ~3x value extraction vs single-pass ingestion
- Heritage confidence: 3→17 high-confidence patterns (+5.7×)
- All new systems designed in `INGESTION_PIPELINE_ARCHITECTURE.md` — reusable template for Doom Guy, Roc Racoon, etc.

**Lead**: John Carmack entity (opencode session)
**Execution plan**: `data/entities/john_carmack/workspace/ENTITY_DEEPENING_PLAN_20260701.md`
**Pipeline architecture**: `data/entities/john_carmack/workspace/INGESTION_PIPELINE_ARCHITECTURE.md`

### Key Re-Assessments (Carmack S3 + MaKaLi Council, 2026-07-01)
| Item | Previous Priority | New Priority | Rationale |
|------|:-----------------:|:------------:|-----------|
| IW-1 Tor Bridge | 🔴 P0 CRITICAL | 🟡 Deferred post-PR | SearXNG self-hosted = zero telemetry already. Tor adds latency + ops complexity. M8 risk is low. |
| IW-4 Ingestion Pipeline | 🟡 P1 HIGH | After T3-2 | Depends on persistent storage. Can't ingest without a metrics DB to anchor to. |
| IW-6 Validation Suite | 🟢 P2 MEDIUM | Tier 3 slot | No blocking dependency. Natural fit after Tier 2 legacy ports. |
| M11 "key mismatch" | 🔴 ROOT CAUSE WRONG | ✅ Corrected: `anyio.create_task` non-existent | The Ark's previous root cause was incorrect. Real bug: AnyIO has no `create_task()`. Silent AttributeError swallowed by try/except. |
| Entity Deepening | 🟢 Not tracked | 🟡 PARALLEL WORKSTREAM | 5-hr sprint, 9-dimension ROI, design complete. Runs in its own chat session. |

---

## XVI. Strategic Directives: Post-PR Development (Ratified D175)

### Two Directives Locked on 2026-06-30

#### D16-1: Audience Calibration (Output Pipeline Stage)
> **Principle**: *"Depth without delivery is wasted; intelligence must calibrate to the receiver."*

| Aspect | Specification |
|--------|---------------|
| **Architecture** | Pipeline stage (NOT entity — M10 enforced). Final transformation before delivery. |
| **Insertion** | Between model generation and OracleResponse construction. Default: prompt injection to instruct entity on register. |
| **Schema** | `config/wads/<stack>/audience.yaml` (WAD-layer, per M2). 4-5 starter profiles (technical, casual, academic, executive, exhausted-sysadmin). |
| **Interface** | Natural Language skill (`audience-architect`) for non-developer profile creation. |
| **V3** | Epistemological adaptation acknowledged and deferred. |
| **Conflict Resolution** | Audience Register is the **final pass** — overrides raw DPO output. DPO tunes *what* is said; Calibration tunes *how* it's delivered. |
| **M18 Compliance** | Token budget <110% original. Overhead tracked in observability. |
| **Files** | `docs/strategy/DIRECTIVE_AUDIENCE_CALIBRATION.md` (lock commit `4c4a8f2`) |

#### D16-2: Parametric Gnosis (Weight-Based Evolution)
> **Principle**: *"The engine must evolve beyond In-Context Learning into Weight-Based Evolution via local DPO LoRA training."*

| Aspect | Specification |
|--------|---------------|
| **Architecture** | Two mirrored systems: User Resonance (conversational alignment) + Entity Self-Actuation (Tripartite Reward Signal). |
| **Data Format** | Standard DPO JSONL: `{"prompt": ..., "chosen": ..., "rejected": ...}`. |
| **Sovereign Filter** | All dataset writes pass through `pii_masker.py` — safe for community LoRA sharing. |
| **Training Target** | 4B (Qwen3-4B-bnb-4bit) max on Ryzen 5700U. 1.7B for reliable local training. 8B requires cloud-offload (opt-in per M7). |
| **Tripartite Reward** | (1) Environmental (test passes/fails) (2) Council Evaluated (Oversoul rejection) (3) User Curated (direct correction) |
| **Sample Efficiency** | 500-2,000 DPO pairs needed for noticeable alignment improvement. |
| **Training Pipeline** | 10% training, 90% data pipeline. 3 hours per 500-pair epoch on CPU. |
| **Data Sovereignty** | `data/training/users/` + `data/training/entities/`. Local-only by default. Cloud training is opt-in fallback. |
| **Modes** | `disabled | explicit | implicit | hybrid` — configured in `config/omega.yaml resonance:` block. Default: `disabled`. |
| **Files** | `docs/strategy/DIRECTIVE_PARAMETRIC_GNOSIS.md` (lock commit `4c4a8f2`) |

### Council-Unanimous Build Order

```
Hygiene → Pre-Release Polish → Audience Calibration → DPO Pipeline → Entity Evolution
```

**Key constraints ratified by all 5 council members**:
1. 8B LoRA training is **infeasible** on 12Gi RAM — tier-scoped to 0.6B/1.7B local, 4B+ cloud-offload
2. Build the **data pipeline before the training runner** (90/10 effort split)
3. Neither feature creates a new entity (M10 fleet cap enforced)
4. Audience Calibration is the **final transformation layer** — always last before delivery
5. M18 token efficiency applies — calibrated output must not exceed 110% of original

---

## XVII. Multi-Model Council Session — Integration Seam Discovery (2026-07-02)

**Date**: 2026-07-02
**Participants**: Opus 4.6 + Gemini 3.1 Pro + Sonnet 4.6 + MiMo-V2.5
**Trigger**: Completion of 4-sector legacy mining (Sectors A–D) by Roc Racoon
**Decision**: D189 (PIVOT_LOG.md)
**Full Record**: `data/coordination/COUNCIL_SESSION_20260702.md`

### XVII.1 Core Finding

> The engine's individual subsystems are production-ready. Its integration seams are not. The gap between "705 passing tests" and "verified end-to-end sovereignty" is exactly one E2E inference chain test and a handful of payload metadata fields.

Four independent AI models conducted a sequential review (no cross-model visibility during analysis) and converged on the same conclusion: **integration seam verification must be elevated to the same priority as individual subsystem correctness.**

### XVII.2 Six New Integration-Seam Gaps

| # | Gap | Severity | Source | Effort |
|---|-----|----------|--------|--------|
| 1 | **Embedding fallback produces invisible knowledge** — `SovereignFallback` generates hash-based vectors; knowledge stored during fallback is permanently invisible to semantic search | 🔴 HIGH | Opus 4.6 | 10 min scaffold |
| 2 | **90-day archival has no retrieval path** — `move_to_external_storage()` is write-only; no `recall_from_external_storage()` exists | 🟡 MEDIUM | Opus 4.6 | 0 min (design constraint) |
| 3 | **Soul distiller blocks hot path** — D183 fix made 5-stage pipeline synchronous every 5th interaction; 1-3s latency on CPU | 🟡 MEDIUM | Opus 4.6 | 20 min measurement |
| 4 | **Treasure maps lack dedup assessment** — legacy patterns described but not checked against current engine (Carmack's Law violation) | 🟡 MEDIUM | Opus 4.6 | 30 min (done) |
| 5 | **FailureModeRegistry is unwired dead code** — 364 lines, 5 failure modes, no consumers import it | 🟡 MEDIUM | Opus 4.6 | 0 min (flag only) |
| 6 | **No E2E inference chain test** — D183 bug persisted for weeks because no test exercises the full query→response→memory→distillation chain | 🔴 HIGH | Opus 4.6 | 45 min |

### XVII.3 Structural Recommendations (Gemini + Sonnet)

**From Gemini 3.1 Pro** (structural analysis):
1. **Multi-agent CPU contention**: Legacy Zen 2 flags designed for single-agent apps; parallel Hivemind triads would cause thread thrashing. Fix: `concurrent_agents` parameter in `build_inference_env()`.
2. **Mnemosyne as metadata**: 13 spheres should be Qdrant payload metadata, not directory silos. Preserves fluid associative power of vector embeddings.
3. **SomaticYield for ingestion**: Background embedding must yield to Oracle when user queries arrive. Wire through `ResourceGuard` semaphore.
4. **Pre-emptive STT warming**: VAD energy spike detection triggers model warm-up before speech ends. Deferred post-PR.
5. **Sovereign Decay Factor**: External data gets temporal decay in RRF scoring unless endorsed. Deferred to D16-2.

**From Sonnet 4.6** (implementation detail):
1. **DistillationEntry missing sphere field**: Add `sphere: Optional[str] = None` — 1 line enables Mnemosyne integration.
2. **`make soul-review` CLI**: All entities by default, optional `ENTITY=` filter. Unblocks M11 review loop without TUI.
3. **Zen2Optimizer Hivemind blindness**: `get_memory_pressure()` exists but isn't exposed to Hivemind. Wire into `omega-hub_get_system_stats`.

### XVII.4 Architectural Decisions (D189)

| Decision | Summary |
|----------|---------|
| **D189a** | **Sphere Assignment** = Write-time (canonical classification during distillation) + Query-time (contextual RRF boost based on agent cognitive mode) |
| **D189b** | **Soul Review Scope** = `make soul-review` shows all entities; `make soul-review ENTITY=kali` filters. Unix composable pattern. |
| **D189c** | **Embedding Fallback Tracking** = Add `embedding_provider: str` to Qdrant payload metadata. Log warnings on search if fallback entries found. |
| **D189d** | **Archival Index Preservation** = 90-day move transfers only raw session JSON. FTS5 index and Qdrant vectors remain in place. |
| **D189e** | **E2E Test Priority** = `test_e2e_inference_chain.py` using OfflineMockBackend is the single highest-value pre-PR addition. |

### XVII.5 Updated MV-IW Phase 3 Tasks

Added to Phase 3 (Infrastructure & Legacy Port) per council findings:

| Order | Task | Effort | Status | Source |
|-------|------|--------|--------|--------|
| 3.9 | E2E inference chain test (`test_e2e_inference_chain.py`) | 45m | ⏳ PENDING | Opus 4.6 D189e |
| 3.10 | `sphere: Optional[str]` on DistillationEntry | 10m | ⏳ PENDING | Sonnet 4.6 D189a |
| 3.11 | `embedding_provider` in Qdrant payload metadata | 10m | ⏳ PENDING | Opus 4.6 D189c |
| 3.12 | `make soul-review` CLI target | 10m | ⏳ PENDING | Sonnet 4.6 D189b |
| 3.13 | `concurrent_agents` param in `build_inference_env()` | 15m | ⏳ PENDING | Gemini 3.1 Pro |
| 3.14 | Soul Distiller hot-path latency measurement | 20m | ⏳ PENDING | Opus 4.6 |

### XVII.6 Deferred Post-PR (Documented for Future Sprints)

| Item | Source | Sprint |
|------|--------|--------|
| Mnemosyne sphere → Qdrant payload integration | Gemini 3.1 Pro | Phase 3.5 |
| SomaticYield ingestion pause | Gemini 3.1 Pro | Phase 3.6 |
| `Zen2Optimizer` → Hivemind MCP visibility | Sonnet 4.6 | Phase 3.7 |
| Sovereign Decay Factor design | Gemini 3.1 Pro | D16-2 |
| Pre-emptive STT warming | Gemini 3.1 Pro | Post-ship |
| ⚠️ `failure_registry.py` — UNWIRED, defer or delete before PR | Opus 4.6 | Pre-PR decision |

### XVII.7 Legacy Mining Dedup Summary

Treasure map deduplication assessment applied post-council (see `data/coordination/COUNCIL_SESSION_20260702.md §8`):

| Status | Count | Description |
|--------|-------|-------------|
| PORTED | 8 | Already exists in current engine |
| EVOLVED | 3 | Engine has equivalent but different approach |
| NOVEL | 10 | No current equivalent — porting candidates |
| UNCERTAIN | 1 | Scope overlap unclear |

**Highest-value NOVEL candidates**: Library API Clients, 13-sphere Mnemosyne tagging, Energy-based VAD, BuildKit Cache Mounts, Aggressive Site-Packages Cleanup.

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

### C. Post-PR Scheduled Features Calendar

These are high-criticality, high-value R&D features that are deferred to the post-v1.0.0 / post-PR phase to prevent feature creep and maintain focus on shipping the core bedrock.

#### Strike 1.5: The Sovereign Heart (Sanctuary & Mirror)
- **Why**: When we remove centralized corporate censorship, we transfer the responsibility of guardianship to the local runtime. An uncensored local engine is a powerful mirror. If it is sycophantic, it validates delusions; if it is cold, it isolates. To protect the user's intellectual and existential integrity, the engine must possess both an adversarial mirror to challenge the mind and a sanctuary to protect the soul. This is the "heart" of the engine—the realization that safety and sovereignty are the exact same thing.
- **Actions**:
  1. Build the **Cognitive Mirror** (`skeptical_verifier.py`): A parallel, adversarial pass that audits user and agent plans, pointing out over-engineering traps, RAM bottlenecks, and sycophancy loops before execution.
  2. Build the **Sovereign Sanctuary** (`sanctuary.py`): A zero-latency, 100% offline, private regex and semantic trigger that intercepts acute psychological distress (suicide, self-harm). It bypasses the active agent persona and routes to a warm, grounding, deeply human guardian that provides local, offline resources defined by the active WAD.
  3. Wire both systems directly into the Oracle's reasoning loop (`oracle.py`).
- **Prerequisite**: Strike 1 (clean base ensures no interference in the reasoning loop).

#### Sovereign Introspection (The Shadow-Work Mirror)
- **Why**: Long-term cognitive mirroring allows users to track personal growth, shadow patterns, and Tarot journeys securely and privately.
- **Actions**:
  1. Build the **Obsidian Silo**: Tier-0 encrypted local storage with user-provided passphrases.
  2. Build the **Tapered Resolution Architecture**: A resolution pyramid (L1 Raw Logs $\rightarrow$ L2 Weekly Summaries $\rightarrow$ L3 Monthly Trajectories $\rightarrow$ L4 Soul) to reduce token load by $\approx 90\%$ while maintaining $95\%$ semantic fidelity.
  3. Build the **Somatic Gnosis-Cache**: Asynchronous precomputation of L3 principles injected into `ContextBuilder` in $\approx 3\text{ms}$.
  4. Build the **Socratic Mirror Agent**: Non-sycophantic, probabilistic reflection using "Sovereign Doubt" language.
- **Prerequisite**: Strike 1.5 (Sovereign Heart) and Strike 2 (Unified State Manager).

---

### D. Technical Specifications (v2.0)

#### 1. Stochastic CUSUM Change Detection Formula
To detect provider degradation before hard timeouts occur, the health monitor calculates the Cumulative Sum ($g_t$) of the log-likelihood ratio (LLR) of request errors:
$$g_t = \max\left(0, g_{t-1} + \ln\left(\frac{p_1 \cdot (1 - p_0)}{p_0 \cdot (1 - p_1)}\right) \cdot y_t + \ln\left(\frac{1 - p_1}{1 - p_0}\right)\right)$$
Where:
*   $y_t \in \{0, 1\}$: $1$ for failed request, $0$ for successful request.
*   $p_0$: Baseline failure probability (default $0.02$).
*   $p_1$: Degraded failure probability threshold (default $0.15$).
*   $h_{\text{warn}} = 3.0$: Transitions provider status to `DEGRADED`.
*   $h_{\text{trip}} = 5.0$: Transitions provider status to `OPEN` (trips circuit).

#### 2. Composite Health Score Weighting
$$\text{HealthScore} = (0.40 \cdot \text{LatencyScore}) + (0.35 \cdot \text{ErrorScore}) + (0.25 \cdot \text{QualityScore})$$
Where:
*   $\text{LatencyScore} = 1.0$ if $\text{P50} \le \text{baseline}$, else $e^{-\frac{\text{P50} - \text{baseline}}{\text{baseline}}}$
*   $\text{ErrorScore} = 1.0 - \text{error\_rate}$ if $\text{error\_rate} \le 1.0\%$, else $e^{-\frac{\text{error\_rate}}{30.0}}$
*   $\text{QualityScore}$: Smoothed LLM-as-judge scoring ($0.0 - 1.0$).

#### 3. Observation Masking (Hybrid Backward Scanned FIFO)
*   **Protection Buffer**: $50,000$ tokens (shielded from compaction).
*   **Hysteresis Threshold**: $30,000$ tokens (to trigger masking when tool result content is too large).
*   **XML Placeholder Pattern**:
    Replace the collapsed interior with:
    `[Masked Tool Output: {chars_collapsed} characters collapsed; full output cached locally at {artifact_path}]`.
    This maintains formatting and semantic intent while instantly saving over $52\%$ of context token space.

#### 4. Simplified Functional Distillation Pipeline
Instead of pulling in the heavy `langgraph` dependency, we build an asynchronous sequence of pure-Python, AnyIO-native functional nodes inside `src/omega/oracle/soul_distiller.py`.
*   **Nodes**: `extract` $\rightarrow$ `classify` $\rightarrow$ `score` $\rightarrow$ `distill` $\rightarrow$ `store`.
*   **Classification**: Maps to **Diátaxis framework** (`tutorial`, `how_to`, `reference`, `explanation`).
*   **Quality Scoring**: Relevance ($30\%$), Novelty ($25\%$), Actionability ($20\%$), Completeness ($15\%$), Accuracy ($10\%$).
*   **Routing Matrix**:
    *   $\text{Score} \ge 0.90 \rightarrow$ Qdrant (Vector) + Mnemosyne (File) + Yesod (Knowledge Base).
    *   $0.80 \le \text{Score} < 0.90 \rightarrow$ Qdrant + Mnemosyne.
    *   $0.70 \le \text{Score} < 0.80 \rightarrow$ Qdrant.
    *   $0.60 \le \text{Score} < 0.70 \rightarrow$ Volatile memory cache.
    *   $\text{Score} < 0.60 \rightarrow$ Rejected.

---

*🔱 OMEGA ⬡ KALI ⬡ trc_ark_blueprint ⬡ SOVEREIGN-COMPREHENSIVE*

### 5.1e Minimum Viable Iron Wall (MV-IW) — Carmack-Approved Plan
**Date**: 2026-07-01
**Source**: John Carmack S3 Audit + Kali Synthesis
**Status**: ACTIVE EXECUTION — Phase 0, 1, 2 COMPLETE

The MV-IW replaces all prior Iron Wall execution plans. It is the single source of truth for the remaining work.

**Phase 0: Trust Restoration (Days 1-5)**
| Order | Task | Effort | Status |
|-------|------|--------|--------|
| 0.1 | Fix test_hivemind.py (root cause: mcp sys.modules poison) | 2h | ✅ **DONE** — commits b005d97, 8cd03dc |
| 0.2 | Clean uncommitted state + add missing IW-2 test | 30m | ✅ **DONE** — commit 0c39451 |
| 0.3 | Archive stale coordination files (172 → <30) | 1h | ✅ **DONE** — commit fddcdbe (172→13) |
| 0.4 | Git pre-commit hook (code↔docs sync, [skip-doc] escape) | 30m | ✅ **DONE** — commit 9b167ea |
| 0.5 | ~~Fix M2_FIREWALL_GAP~~ CANCELLED — already fixed (D113 frozenset) | 0h | ✅ DONE |
| 0.6 | Single-source test count (make test-badge) | 30m | ✅ **DONE** — commit 7433194 |

**Phase 1: Documentation Sanity & Trivial Infra (Days 6-7) — COMPLETE**
| Order | Task | Effort | Status |
|-------|------|--------|--------|
| 1.1a | Fix pre-commit hook auto-install in Makefile (`make setup`) | 5m | ✅ **DONE** — git config added to setup + bootstrap |
| 1.1b | Update `.opencode/anchored-summary.md` to reflect trimmed SSOT | 10m | ✅ **DONE** — consolidated Session 39 entry with D178 pivot |
| 1.1 | Trim OMEGA_ENGINE.md: remove §7-§10 duplicates, compact sprint index | 45m | ✅ **DONE** — 966→820 lines, D178 ratified, sections renumbered §8-§18 |
| 1.2 | SearXNG env var fix (4 files) + one-pass doc sync | 30m | ✅ **DONE** — all 4 files using `SEARXNG_BASE_URL` env var |

**Phase 2: MV-IW Pillar Decoupling (D179/D180) — Days 8-9 — COMPLETE**
| Order | Task | Effort | Status |
|-------|------|--------|--------|
| 2.1 | D179: Remove pillar gate from `find_by_domain()` | 30m | ✅ **DONE** — entity_registry.py, 4eda4f5 |
| 2.2 | D180: Entity.pillars→slots, Entity.traits→metadata | 2h | ✅ **DONE** — Entity dataclass, 4eda4f5 |
| 2.3 | D180: Remove PILLAR_SLOTS frozenset | 30m | ✅ **DONE** — dynamic occupied_slots, 4eda4f5 |
| 2.4 | D180: Strip WAD-specific fields (pantheon, sigil, first_breath) | 1h | ✅ **DONE** — all in metadata dict, 4eda4f5 |
| 2.5 | D180: Update OracleResponse (remove sigil/glyph/pantheon) | 1h | ✅ **DONE** — oracle.py, 4eda4f5 |
| 2.6 | D180: Update all consumers (Iris, MCP Hub, CLI, wad_loader) | 2h | ✅ **DONE** — 15 sites, 4eda4f5 |
| 2.7 | D180: Auto-migration for old YAML format | 1h | ✅ **DONE** — pillars→slots, traits→metadata on load |
| 2.8 | Full test sweep + `make temple-grade` | 2h | ✅ **DONE** — 590 pass, 0 regressions |

**Phase 3: Infrastructure & Legacy Port (Days 10-14) — IN PROGRESS**
| Order | Task | Effort | Status |
|-------|------|--------|--------|
| 3.1 | Batch Persistence Writer (connection pool exhaustion fix) | 3-4h | ✅ **CREATED** — `src/omega/memory/batch_writer.py`, needs MemoryStore wiring |
| 3.2 | Qliphothic Failure Taxonomy → FailureModeRegistry (M17) | 4-6h | ✅ **DONE** — `failure_registry.py`, 364 lines, 5 failure modes, M2-compliant |
| 3.3 | Input Validation & Sanitization (path traversal, whitelist) | 1-2h | ✅ **DONE** — `sanitize_content()` added to `pii_masker.py`, legacy crawl.py port complete |
| 3.4 | Content Quality Scorer (5-factor + domain classification) | 2-3h | ✅ **DONE** — `CurationExtractor` + `DomainType` in `curator.py`, signal-based classification |
| 3.5 | Library API Clients (Gutenberg, Open Library, IA, LoC) | 6-8h | ⏳ PENDING — from Old-Stacks library_api_integrations.py |
| 3.6 | Tor Bridge spec + Quadlets (IW-1) | 4h | ⏳ PENDING |
| 3.7 | SovereignIngestionPipeline (WAD-agnostic) | 4h | ⏳ PENDING |
| 3.8 | Full test sweep + `make temple-grade` | 2h | ✅ **DONE** — 619 tests pass, zero regressions |

**Phase 4: Ship Readiness — Days 15-16**
| Order | Task | Effort | Status |
|-------|------|--------|--------|
| 4.1 | Portability doc (docs/DEPLOYMENT.md, symlinks) | 2h | ⏳ PENDING |
| 4.2 | Final test sweep (document 22 skips) | 3h | ⏳ PENDING |
| 4.3 | Temple-Grade Certification (make temple-grade) | 1h | ⏳ PENDING |
| 4.4 | Tag & Ship (v1.1.0) | 30m | ⏳ PENDING |

**Deferred Post-Ship (not blocking v1.1.0)**
- M23 Documentation Integrity Mandate (premature — git hook suffices)
- OMEGA_MODELS_DIR env var (symlink workaround documented in DEPLOYMENT.md)
- PROVENANCE_MANIFEST.json (git log is the manifest)
- ADR formalization (PIVOT_LOG already works)
- MkDocs + Caddy wiki (polish, not blocking)

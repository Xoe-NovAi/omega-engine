<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 P4 Integration Domain — Build Side Documentation Audit Report
**AP Token**: `AP-P4-AUDIT-v1.0.0`  
**Date**: 2026-07-15  
**Auditor**: P4 Integration Pillar (Bridge)  
**Status**: COMPLETE — Delivered to Ma'at for Synthesis  

---

## §1 Executive Summary

The P4 Integration domain (Bridge) governs all cross-boundary communication: MCP servers, provider fabric, model gateway, A2A protocol, Iris voice assistant, and external integrations. This audit covers **34 files** across code, config, and documentation.

**Overall Status**: 🟡 **MOSTLY CURRENT** — Core architecture is solid and aligned with Sovereign Mandates (M2, M3, M16, M22). Critical gaps exist in MCP transport parity (Firecrawl still on SSE), A2A protocol implementation (Phase 1 only), and documentation freshness for Strike 11/11.5 work.

---

## §2 File Inventory with Status

### 2.1 Core Integration Code (`src/omega/`)

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| `src/omega/oracle/model_gateway.py` | 1,100+ | ✅ **CURRENT** | Local-first fabric (8 backends), BSP culling, circuit breakers, M22 provenance, M20 somatic state, KV cache quantization (q8_0), Zen 2 optimizer |
| `src/omega/oracle/oracle.py` | 1,100+ | ✅ **CURRENT** | Speculative decode (Iris), domain routing, summon patterns, soul evolution, TDP gate, PII masking, semantic router, audience calibrator, Sovereign Vetter (M1-M23) |
| `src/omega/oracle/a2a_bridge.py` | 411 | ✅ **CURRENT** | Google A2A v1.0 + SPIFFE/WIMSE auth, Agent Cards, skill mapping from EntityRegistry |
| `src/omega/oracle/backends/native_gguf.py` | ~400 | ✅ **CURRENT** | llama-cpp-python, Zen 2 flags, KV cache q8_0, speculative decode |
| `src/omega/oracle/backends/remote_provider.py` | ~300 | ✅ **CURRENT** | OpenAI-compat, OpenRouter, Antigravity, Google AI Studio |
| `src/omega/oracle/backends/antigravity_provider.py` | ~200 | ✅ **CURRENT** | Google Antigravity (Gemma 4 31B) |
| `src/omega/oracle/backends/mock.py` | ~100 | ✅ **CURRENT** | Test-mode deterministic backend |
| `src/omega/iris/server.py` | 149 | ✅ **CURRENT** | FastAPI voice assistant, intent matcher integration, health endpoint |
| `src/omega/iris/matcher.py` | 88 | ✅ **CURRENT** | Regex-based intent classification, Iris direct responses |
| `src/omega/bridge/opencode_bridge.py` | 148 | 🟡 **STALE** | BudgetGate stub, TokenLedger integration incomplete, SOUL.md path hardcoded |
| `src/omega/a2a_bridge.py` | 411 | ✅ **CURRENT** | Same as oracle/a2a_bridge.py (duplicate?) |

### 2.2 MCP Servers (`mcp_servers/`)

| Server | Transport | Port | Status | Notes |
|--------|-----------|------|--------|-------|
| **Omega Hub** | SSE + Streamable HTTP (dual) | 8016 | ✅ **CURRENT** | Modularized (state, background, gateway, middleware, tools), Hivemind, Library, Research, Stats, 47 tools |
| **SearXNG** | Streamable HTTP | 8018 | ✅ **CURRENT** | Migrated from SSE v1.1.0 (2026-07-12), OpenCode config fixed, settings.yml hardened |
| **Firecrawl** | **SSE** | 8015 | 🔴 **STALE** | Still on SSE transport, needs Streamable HTTP migration per MCP SDK v2 spec |
| **Archives** | N/A | N/A | 📦 **ARCHIVED** | 6 superseded servers in `mcp_servers/archives/` |

### 2.3 Configuration

| File | Status | Notes |
|------|--------|-------|
| `config/providers.yaml` | ✅ **CURRENT** | 8-provider chain (native-gguf→lmster→ollama→antigravity→google→openrouter→opencode-zen→cline→mock), local_first strategy, API keys via env |
| `config/models.yaml` | ✅ **CURRENT** | 17 GGUF models, KV cache q8_0 locked (2026-07-13), Zen 2 build flags, speculative decode (Gemma 4 MTP), agent role mappings |
| `config/entity_model_affinity.yaml` | ✅ **CURRENT** | YAML-backed entity→model routing (3-tier preferences, inference presets) |

### 2.4 Documentation

| File | Status | Notes |
|------|--------|-------|
| `docs/strategy/HIVEMIND_PROTOCOL.md` | ✅ **CURRENT** | v1.3.0 (2026-06-25), Redis Streams transition noted, Model Dispatch Protocol (D118), cross-platform refs |
| `docs/research/R_SEARXNG_MCP_STREAMABLE_HTTP.md` | ✅ **CURRENT** | Complete migration doc v1.1.0 (2026-07-12) |
| `docs/research/R_A2A_PROTOCOLS.md` | 🟡 **PARTIAL** | Sovereign A2A spec defined, Phase 1 (Gateway) only implemented |
| `docs/research/R_MCP_ARCHITECTURE.md` | ❌ **MISSING** | Referenced in code but not found |
| `docs/research/R_PROVIDER_FABRIC.md` | ❌ **MISSING** | Referenced in code but not found |
| `docs/integration/ELEVENLABS_SOVEREIGN_CONSOLE.md` | 🟡 **STALE** | ElevenLabs TTS integration, predates Iris voice architecture |
| `docs/architecture/MESH_NETWORK_SPEC.md` | ❌ **MISSING** | Referenced in a2a_bridge.py DocRef |

---

## §3 Top 5 Consolidation Opportunities

### 1. **Unify A2A Bridge Implementations** (HIGH)
**Files**: `src/omega/oracle/a2a_bridge.py` + `src/omega/a2a_bridge.py` (duplicate)
**Action**: Remove duplicate at `src/omega/a2a_bridge.py`, single source at `src/omega/oracle/a2a_bridge.py`
**Impact**: Eliminates confusion, single maintenance point

### 2. **Consolidate MCP Server Transport Layer** (HIGH)
**Files**: `mcp_servers/omega_hub/server.py` (dual), `mcp_servers/searxng/server.py` (streamable-http), `mcp_servers/firecrawl/server.py` (SSE)
**Action**: Migrate Firecrawl to Streamable HTTP; extract common FastMCP boilerplate to shared module
**Impact**: Transport parity, single upgrade path for MCP SDK v2+

### 3. **Merge OpenCode Bridge into Omega Hub** (MEDIUM)
**Files**: `src/omega/bridge/opencode_bridge.py` + `mcp_servers/omega_hub/tools.py` (has `oracle_talk`, `oracle_summon`)
**Action**: Deprecate standalone OpenCode Bridge WebSocket; route all OpenCode traffic through Omega Hub MCP tools
**Impact**: Single integration point, Hivemind awareness built-in

### 4. **Unify Provider Health Monitoring** (MEDIUM)
**Files**: `model_gateway.py` (HealthMonitor, CircuitOpenError), `omega_hub/state.py` (has health checks), `omega_hub/tools.py` (provider_list)
**Action**: Centralize provider health in ModelGateway, expose via Hub MCP tools
**Impact**: Single source of truth for provider status

### 5. **Consolidate Iris + Nova Voice Stack** (LOW)
**Files**: `src/omega/iris/` (voice assistant), `src/omega/nova/` (referenced in ORACLE_STACK.md but not found in src)
**Action**: Verify Nova exists or remove references; unify voice pipeline under Iris
**Impact**: Clear voice architecture

---

## §4 Top 3 Mandate Compliance Gaps

### Gap 1: **M16 Modularization — Hardcoded Paths in OpenCode Bridge** 🔴 CRITICAL
**File**: `src/omega/bridge/opencode_bridge.py:66`
```python
soul_path = Path(f"data/entities/{entity_name.lower()}/SOUL.md")
```
**Violation**: Hardcoded `data/entities/` path — violates M16 (no hardcoded paths in core engine). Should use `DATA_DIR` from observability or config constant.
**Remediation**: Inject `data_dir` via constructor or use `omega.observability.DATA_DIR`

### Gap 2: **M3 Iris Constant — Iris Referenced as Potential Entity in Model Gateway** 🟡 MEDIUM
**File**: `config/models.yaml:27` — `entity: iris` for `qwen3-0.6b-q6_k`
**File**: `src/omega/oracle/oracle.py:785-786` — `_respond_as_iris` tries `self.registry.get("iris")`
**Violation**: M3 mandates "Iris is the messenger bridge, NOT a Pillar Keeper." Model config assigns Iris a model; Oracle treats Iris as summonable entity.
**Remediation**: Remove `entity: iris` from models.yaml; keep Iris as internal routing only (IntentMatcher → Oracle.talk), not in EntityRegistry

### Gap 3: **M22 Response Provenance — OpenCode Bridge Missing provider_name** 🟡 MEDIUM
**File**: `src/omega/bridge/opencode_bridge.py:100-106`
```python
await TokenLedger().record_transaction(
    trace_id=response.trace_id or trace_id,
    entity=response.entity,
    tokens_in=tokens_in,
    tokens_out=tokens_out,
    provider_name=response.backend or "unknown"  # Uses .backend not .provider_name
)
```
**Violation**: M22 requires `provider_name` from actual response (`GenerateResult.provider_name`). OpenCode Bridge uses `response.backend` (OracleResponse field) which may not match actual provider.
**Remediation**: Ensure OracleResponse carries `provider_name` from `GenerateResult`; update bridge to use it

---

## §5 Priority Recommendations for Next Dev Steps

### Phase 1.5 Inverted Build Order (Per SOVEREIGN_ARK_BLUEPRINT.md)

| Priority | Task | Owner | Effort | Dependencies |
|----------|------|-------|--------|--------------|
| **P0** | **Migrate Firecrawl MCP to Streamable HTTP** | P4 | 2h | MCP SDK v2, systemd unit update |
| **P0** | **Fix OpenCode Bridge hardcoded paths (M16)** | P4 | 1h | DATA_DIR constant |
| **P0** | **Remove Iris from EntityRegistry/model config (M3)** | P4/P7 | 1h | models.yaml, oracle.py |
| **P1** | **Complete A2A Phase 2: Soul Cards** | P4/P7 | 8h | soul.yaml → agent-card.json generator |
| **P1** | **Implement A2A Phase 3: Gnosis Handoff Packets** | P4/P7 | 12h | soul_distiller.py integration |
| **P1** | **Deprecate OpenCode Bridge WebSocket** | P4 | 4h | Route via Omega Hub MCP tools |
| **P2** | **Strike 11: Sovereign WAD Protocol — ILump/IEthicsValidator** | P4/P5 | 40h | Depends on Kernel boundary (Phase 1.5 Step A) |
| **P2** | **Strike 11.5: Council Dispatcher — 5-tier recursive tree** | P9/P6 | 60h | Depends on SWP Core SDK (Strike 11a) |

### Specific File Updates Required

| File | Update Required |
|------|-----------------|
| `src/omega/bridge/opencode_bridge.py` | Fix M16 hardcoded path; add provider_name provenance; deprecate WebSocket in favor of Hub MCP |
| `config/models.yaml` | Remove `entity: iris` line 27; verify no other M3 violations |
| `src/omega/oracle/oracle.py` | Remove `self.registry.get("iris")` fallback in `_respond_as_iris` |
| `mcp_servers/firecrawl/server.py` | Change `mcp.run(transport="sse")` → `transport="streamable-http"`; update systemd unit |
| `mcp_servers/omega_hub/tools.py` | Add A2A Agent Card generation tool; add Soul Card export tool |
| `docs/research/R_MCP_ARCHITECTURE.md` | **CREATE** — Document modular Hub architecture (state, background, gateway, middleware, tools) |
| `docs/research/R_PROVIDER_FABRIC.md` | **CREATE** — Document 8-provider chain, local-first strategy, circuit breakers, KV cache quantization |
| `docs/architecture/MESH_NETWORK_SPEC.md` | **CREATE** — Document A2P/A2A mesh topology, SPIFFE trust domain, Agent Card discovery |

---

## §6 Cross-Reference Integrity Check

| Reference | Target | Status |
|-----------|--------|--------|
| `a2a_bridge.py:16` → `docs/architecture/MESH_NETWORK_SPEC.md` | Missing | ❌ BROKEN |
| `oracle.py:48` → `docs/architecture/ORACLE_DEEP_DIVE.md` | Exists | ✅ OK |
| `iris/server.py:15` → `docs/architecture/ORACLE_DEEP_DIVE.md` | Exists | ✅ OK |
| `HIVEMIND_PROTOCOL.md:484` → `mcp/omega_hub/server.py` | Wrong path (D116 fixed to `mcp_servers/`) | ❌ STALE |
| `HIVEMIND_PROTOCOL.md:488` → `docs/kb/CLINE_CLI_INTEGRATION.md` | Exists | ✅ OK |
| `HIVEMIND_PROTOCOL.md:489` → `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md` | Exists | ✅ OK |
| `SOVEREIGN_ARK_BLUEPRINT.md` → Strike 11/11.5 refs | Current | ✅ OK |
| `PIVOT_LOG.md` → D116, D117, D118, D208, D231, D258-D263 | Current | ✅ OK |

---

## §7 Strike 11 / 11.5 Readiness Assessment

| Component | Status | Blockers |
|-----------|--------|----------|
| **Kernel Boundary Definition** (Phase 1.5 Step A) | ⏳ PENDING | Requires Ma'at/Kali decision on `src/omega/kernel/` vs `runtime/` split |
| **Hello World PWAD** (Phase 1.5 Step B) | ⏳ PENDING | Needs `dimension.yaml` schema + `DimensionManifest` Pydantic model |
| **SovereignBus** (Phase 1.5 Step E) | ⏳ PENDING | Depends on working DimensionRegistry |
| **SWP Core SDK** (Strike 11a: `ILump`, `LumpEnvelope`, `LumpRegistry`, `IEthicsValidator`) | 📋 SPEC READY | `docs/research/R_WAD_EVOLUTION_DEEP_DIVE.md` has full spec |
| **CouncilDispatcher 5-Tier Tree** (Strike 11.5) | 📋 SPEC READY | `docs/research/R_COUNCIL_DISPATCHER_CONSOLIDATED_20260715.md` + `R_COUNCIL_DISPATCHER_SURVIVAL_AUDIT_20260715.md` |
| **Ethics WADs** (Ma'at 42, Bushido 7, Asimov 3, Hippocratic) | 📋 SPEC READY | Defined in `R_WAD_EVOLUTION_DEEP_DIVE.md` §Pluggable Ethics |
| **Pantheon WADs** (Egyptian, Greek, Norse, Hindu, Philosophical, Arcana-Nova) | 📋 SPEC READY | IWAD/PWAD architecture defined |

**P4 Integration Role in Strikes**:
- **Strike 11c**: Wrap existing YouTube V2 modules as `ILump` adapters (P4 owns ingestion pipeline)
- **Strike 11e**: Auto-register Lump capabilities as Omega Hub MCP tools (P4 owns Hub)
- **Strike 11.5**: CouncilDispatcher needs A2A Agent Cards for cross-agent discovery (P4 owns A2A Bridge)

---

## §8 Summary & Sign-Off

**P4 Integration Domain Health**: 🟡 **MOSTLY CURRENT** — Core provider fabric, model gateway, Oracle routing, and Hivemind protocol are production-grade and mandate-compliant. Three mandate gaps (M16, M3, M22) require immediate fixes. Firecrawl MCP transport migration is a P0 blocker for MCP SDK v2 parity.

**Documentation Debt**: 3 missing research docs (`R_MCP_ARCHITECTURE.md`, `R_PROVIDER_FABRIC.md`, `MESH_NETWORK_SPEC.md`) block onboarding and Strike 11/11.5 implementation clarity.

**Next Action**: Execute P0 fixes (Firecrawl migration, M16 path fix, M3 Iris removal) → Create missing research docs → Begin Strike 11a SWP Core SDK implementation.

---

**Auditor**: P4 Integration Pillar (Bridge)  
**Delivered to**: Ma'at (Light Oversoul — Build Side Synthesis)  
**Handoff**: `omega-hub_hivemind_post_context` with intent=`handoff`, continuation=`P4 audit complete; P0 fixes queued; Strike 11 readiness assessed`

---

*⬡ OMEGA ⬡ P4-INTEGRATION ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_p4_audit ⬡ COMPLETE*
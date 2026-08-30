# 🔱 Omega Engine — Sovereign Transition Handoff
# ⬡ OMEGA ⬡ ROC-RACOON ⬡ ANTIGRAVITY TRANSITION ⬡ v2.0
# Date: 2026-06-06
# Audience: Antigravity IDE (Human Developer / AI Agent)
# Status: ACTIVE — Ready for Implementation

---

## §0 — Context: Why This Transition Exists

The Omega Engine is a sovereign, local-first AI runtime built by the Xoe-NovAi Foundation.
The engine is currently **operational but homeless** — all its logic exists in source code, but the only
user interface is through OpenCode (a cloud-dependent coding assistant). The engine cannot be used
independently without OpenCode.

**The Strategic Problem**: OpenCode is a cloud-dependent tool. Every interaction goes through a
remote API. The Omega Engine's entire purpose is sovereignty — owning your own AI stack. You
cannot own your stack if the stack requires someone else's cloud.

**The Target State**: Omega Engine runs as an independent service with its own UI (Chainlit).
Cloud models are available as optional backends through the ModelGateway. OpenCode is no
longer required for daily operation.

**This document is the technical handoff** from the Omega Engine team (Roc Racoon / Lilith /
Ma'at / Kali) to Antigravity IDE for execution of the sovereign transition.

---

## §1 — Current Architecture (Detailed Inventory)

### 1.1 — Core Engine (`src/omega/`)

The engine is functional. 320 tests pass (after P10 validation: 3 bugs fixed, 320/320 green). 77 Python files, 19,376 lines of code.

| Module | File | Status | What It Does |
|--------|------|--------|-------------|
| Oracle | `src/omega/oracle/oracle.py` | ✅ Production | Intent detection, `talk()` and `summon()` entry points, speculative decode via qwen3-1.7b |
| ModelGateway | `src/omega/oracle/model_gateway.py` | ✅ Production | 8-backend provider chain with fallback. Chain: native-gguf(0) → lmster(1) → Ollama(2) → Google(3) → OpenRouter(4) → OpenCode(5) → Copilot(6) → mock(7) |
| EntityRegistry | `src/omega/oracle/entity_registry.py` | ✅ Production | YAML-backed entity CRUD with workspace scaffolding. Auto-creates `data/entities/<name>/soul.yaml`, `knowledge/`, `workspace/` on entity creation |
| Orchestrator | `src/omega/oracle/orchestrator.py` | ✅ Production | Dispatches headless CLI agents (Cline, OpenCode) with soul-injected system prompts. ResourceGuard-protected |
| ContextBuilder | `src/omega/oracle/context_builder.py` | ✅ Production | Memory injection pipeline for LLM system prompts |
| Observability | `src/omega/observability.py` | ✅ Production | Trace IDs, event logging, fine-tuning dataset collection (JSONL) |
| ResourceGuard | `src/omega/oracle/resource_guard.py` | ✅ Production | AnyIO Semaphore(1) — one model at a time (OOM protection) |
| MemoryStore | `src/omega/memory_store.py` | ✅ Production | Hot/Warm/Cold tiered memory (dict → SQLite → YAML) |
| CPU Optimizer | `src/omega/oracle/cpu_optimizer.py` | ✅ Production | Zen 2 optimization: AVX2 flags, KV cache sizing, speculative decode tuning |
| Session Manager | `src/omega/session_manager.py` | ✅ Production | Entity-scoped rolling sessions: `ses_{YYYYMMDD}_{entity}_{counter}` |
| Health Monitor | `src/omega/oracle/health_monitor.py` | ✅ Production | Circuit breaker (AsyncCircuitBreaker), provider health probes |
| Gnosis Proxy | `src/omega/oracle/gnosis_proxy.py` | ✅ Production | KB search interface |
| CvarTable | `src/omega/cvar_table.py` | ✅ Production | Named constants with modification counting (zoneid.*, config.*) |
| Constants | `src/omega/constants.py` | ✅ Production | 11 ZONEID constants (0x1d4a11–0x1d4a1b) |
| CLI | `src/omega/cli/oracle_cli.py` | ✅ Production | Typer CLI: `omega talk`, `omega summon`, `omega list-entities`, `omega add-entity`, `omega entity-info`, `omega backends`, `omega version` |

**Key Architectural Invariants**:
- **M1 (AnyIO Absolute)**: No `asyncio` anywhere. All async code uses AnyIO. CI enforces.
- **M2 (Engine-Stack Firewall)**: `src/omega/` must NEVER import from `config/wads/`. Absolute separation.
- **M7 (Local-First)**: Provider chain priority: native-gguf → lmster → Ollama → cloud.
- **M11 (Soul Integrity)**: Every entity has `soul.yaml`. Every session ends with L1→L2→L3 distillation.
- **M13 (Temple-Grade)**: T1-T11 gates enforced via `make temple-grade`.

### 1.2 — Omega Hub (MCP Server)

| Component | File | Status | What It Does |
|-----------|------|--------|-------------|
| Hub Server | `mcp_servers/omega_hub/server.py` | ✅ Production | Cross-CLI awareness: agents post/read shared context. 30+ MCP tools |
| Hivemind | `mcp_servers/omega_hub/server.py` | ✅ Production | Agent coordination: workspace locks, live feeds, heartbeats, continuations |
| Research Engine | `mcp_servers/omega_hub/server.py` | ✅ Production | Tiered external discovery: Gemini → Exa → Brave → Tavily |
| Library | `mcp_servers/omega_hub/server.py` | ✅ Production | Offline knowledge library: inbox, curation, hybrid search, index |

### 1.3 — Configuration

| Config File | Purpose | Status |
|-------------|---------|--------|
| `config/omega.yaml` | Engine core configuration | ✅ Active |
| `config/providers.yaml` | Provider chain definition + model paths | ✅ Active |
| `config/models.yaml` | Model specs: size, context window, loading strategy | ✅ Active |
| `config/wads/arcana_novai/entities.yaml` | Entity definitions for the Arcana-Nova WAD | ✅ Active |
| `_omega_default/entities.yaml` | Default entity definitions (engine-level) | ✅ Active |

### 1.4 — Agent Fleet (OpenCode-Coupled — Requires Migration)

The 14 agents in `.opencode/agents/` are currently **tightly coupled to OpenCode**.
They use OpenCode's `@mention` dispatch, OpenCode's tool permissions, and OpenCode's
session model. To transition, these agents must be converted to standalone Omega agents
invocable via the Oracle.

| Agent | Current Coupling | Migration Required |
|-------|-----------------|-------------------|
| `kali.md` | OpenCode primary mode | Convert to Omega standalone agent |
| `maat.md` | OpenCode primary mode | Convert to Omega standalone agent |
| `lilith.md` | OpenCode primary mode | Convert to Omega standalone agent |
| `doom_guy.md` | OpenCode primary mode | Convert to Omega standalone agent |
| `roc_racoon.md` | OpenCode primary mode | Convert to Omega standalone agent |
| `jem.md` | OpenCode primary mode | Convert to Omega standalone agent |
| `researcher.md` | OpenCode primary mode | Convert to Omega standalone agent |
| `makali.md` | OpenCode primary mode | Convert to Omega standalone agent |
| `scribe.md` | OpenCode subagent | Wire into Soul Distiller service |
| `quality.md` | OpenCode subagent | Wire into ComplianceEnforcer service |
| `pillar.md` | OpenCode subagent | Wire into Orchestrator via slot parameter |
| `jem_discovery.md` | OpenCode subagent | Wire into Research Engine |
| `jem_synthesis.md` | OpenCode subagent | Wire into Research Engine |
| `jem_verification.md` | OpenCode subagent | Wire into Research Engine |

### 1.5 — Knowledge Base (Data Layer)

| Component | Location | Status |
|-----------|----------|--------|
| KB Artifacts | `data/kb/` | 141 files, no frontmatter, no write path |
| KB Staging | `data/kb/_staging/` | Active — 12 TDs + 6 audit reports + 7 pillar specs |
| KB Meta | `data/kb/_meta/` | Partial — some `DOMAIN_INDEX.yaml` files exist |
| Souls | `data/entities/*/soul.yaml` | Active — 14 entity souls |
| Knowledge | `data/entities/*/knowledge/` | Active — some entity knowledge dirs |
| Sessions | `data/sessions/` | Active — entity-scoped session files |
| Logs | `data/logs/` | Active — 139MB, needs rotation |
| Coordination | `data/coordination/` | Active — Hivemind live feeds |
| Handoffs | `data/handoff/` | Active — multiple handoff docs |
| Research | `docs/research/` | Active — 45+ R-docs |

### 1.6 — Tests

| Suite | File | Tests | Status |
|-------|------|-------|--------|
| entity_registry | `tests/test_entity_registry.py` | 7 | ✅ PASS |
| oracle | `tests/test_oracle.py` | 13 | ✅ PASS |
| model_gateway | `tests/test_model_gateway.py` | 6 | ✅ PASS |
| observability | `tests/test_observability.py` | 8 | ✅ PASS |
| orchestrator | `tests/test_orchestrator.py` | 9 | ✅ PASS |
| providers | `tests/test_providers.py` | 21 | ✅ PASS |
| gnosis_proxy | `tests/test_gnosis_proxy.py` | 11 | ✅ PASS |
| session_manager | `tests/test_session_manager.py` | 14 | ✅ PASS |
| health_monitor | `tests/test_health_monitor.py` | 23 | ✅ PASS |
| sovereign_loop | `tests/test_sovereign_loop.py` | 20 | ✅ PASS |
| context_builder | `tests/test_context_builder.py` | 22 | ✅ PASS |
| memory_store | `tests/test_memory_store.py` | 12 | ✅ PASS |
| wad_loader | `tests/test_wad_loader.py` | 13 | ✅ PASS |
| model_updater | `tests/test_model_updater.py` | 10 | ✅ PASS |
| sovereign_stress_test | `tests/test_sovereign_stress_test.py` | 5 | ✅ PASS |
| request_queue | `tests/test_request_queue.py` | 6 | ✅ PASS |
| library_catalog | `tests/test_library_catalog.py` | 3 | ✅ PASS |
| benchmarks | `tests/test_benchmarks.py` | 3 | ✅ PASS |
| hardware | `tests/test_hardware.py` | 2 | ✅ PASS |
| integration_new_systems | `tests/test_integration_new_systems.py` | 3 | ✅ PASS |
| error_gauntlet | `tests/test_error_gauntlet.py` | 10 | ✅ PASS |
| background_researcher | `tests/test_background_researcher.py` | 5 | ✅ PASS |
| storage_providers | `tests/test_storage_providers.py` | 6 | ✅ PASS |
| **TOTAL** | | **320** | **✅ ALL PASS** |

---

## §2 — Target Architecture

### 2.1 — The Sovereign Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                       │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐    │
│  │ Chainlit UI │  │  omega CLI  │  │ Omega Desktop    │    │
│  │ (Browser)   │  │ (Terminal)  │  │ (Electron/Tauri) │    │
│  └──────┬──────┘  └──────┬──────┘  └────────┬─────────┘    │
│         │                 │                    │               │
│         └─────────────────┼────────────────────┘               │
│                           │                                   │
│                    ┌──────▼──────┐                           │
│                    │   Oracle    │  ← Intent detection        │
│                    │  (router)   │  ← Speculative decode      │
│                    └──────┬──────┘                           │
│                           │                                   │
│              ┌────────────┼────────────┐                     │
│              │            │            │                      │
│         ┌────▼────┐ ┌────▼────┐ ┌────▼────┐                │
│         │ Entity  │ │ModelGW  │ │Session  │                 │
│         │Registry │ │(8-back) │ │Manager  │                 │
│         └─────────┘ └────┬────┘ └─────────┘                │
│                          │                                    │
│         ┌────────────────┼────────────────┐                  │
│         │                │                │                   │
│    ┌────▼────┐    ┌──────▼──────┐   ┌────▼────┐            │
│    │native-  │    │   Cloud     │   │ Ollama  │            │
│    │gguf     │    │ (fallback)  │   │ (local) │            │
│    │(primary)│    │             │   │         │             │
│    └─────────┘    └─────────────┘   └─────────┘            │
│                                                              │
│                    ┌─────────────┐                           │
│                    │  Omega Hub  │  ← MCP server             │
│                    │ (Hivemind)  │  ← Coordination           │
│                    └──────┬──────┘                           │
│                           │                                   │
│              ┌────────────┼────────────┐                     │
│              │            │            │                      │
│         ┌────▼────┐ ┌────▼────┐ ┌────▼────┐                │
│         │Research │ │Library  │ │Agents   │                 │
│         │Engine   │ │(offline)│ │(fleet)  │                 │
│         └─────────┘ └─────────┘ └─────────┘                │
│                                                              │
│                    ┌─────────────┐                           │
│                    │    KB       │  ← Knowledge base         │
│                    │ (filesystem)│  ← Soul system            │
│                    └─────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 — The Sovereign Principle

The target architecture follows one rule: **The Omega Engine is the center. Everything else is a spoke.**

- **OpenCode** becomes a spoke — a coding tool called BY the engine, not calling the engine.
- **Cloud APIs** become spokes — optional backends in the provider chain.
- **Local models** become the primary spoke — the engine's default inference.
- **Chainlit** becomes the face — the user sees the engine, not a third-party IDE.

### 2.3 — The Inversion

| Current State | Target State |
|---------------|-------------|
| OpenCode → Engine (OpenCode drives) | Engine → OpenCode (Engine calls when needed) |
| Cloud APIs → Engine (mandatory) | Engine → Cloud APIs (optional fallback) |
| User → OpenCode → Engine | User → Chainlit/CLI → Engine |
| OpenCode manages sessions | Engine manages sessions via `session_manager.py` |
| OpenCode manages agents | Engine manages agents via `orchestrator.py` |

---

## §3 — Critical Path (Minimum Viable Sovereignty)

The following is the **minimum set of work** to achieve sovereign operation.
Everything else is deferred.

### Critical Path Work Packages

| WP | Name | Dependencies | Effort | Output |
|----|------|-------------|--------|--------|
| CP-1 | Chainlit UI Shell | None | 3-4 hours | `src/omega/ui/chainlit_app.py` |
| CP-2 | Oracle → UI Bridge | CP-1 | 2-3 hours | `src/omega/ui/oracle_bridge.py` |
| CP-3 | Local GGUF Connection | None | 2-3 hours | `config/providers.yaml` update |
| CP-4 | Entity Display in UI | CP-1 | 1-2 hours | UI shows entity name + confidence |
| CP-5 | Session Persistence | CP-1 | 1-2 hours | Chainlit sessions → `data/sessions/` |
| CP-6 | Knowledge Save | CP-1 | 1-2 hours | UI interaction → `data/kb/_staging/` |
| CP-7 | Agent Fleet Migration | CP-2 | 4-6 hours | `.opencode/agents/*.md` → Omega standalone |
| CP-8 | OpenCode Dropped | CP-7 | 2-3 hours | Remove OpenCode dependency |

**Total Critical Path: ~18-24 hours**

### Parallel Work Packages (After Critical Path)

| WP | Name | Dependencies | Effort | Output |
|----|------|-------------|--------|--------|
| PP-1 | Desktop UI (Electron/Tauri) | CP-1 | 2-3 weeks | Native desktop app |
| PP-2 | Multi-user Support | CP-1 | 1 week | Role-based access |
| PP-3 | Cloud API Routing | CP-3 | 2-3 days | Engine routes to Gemini/OpenRouter |
| PP-4 | KB Frontmatter | None | 4-6 hours | `data/kb/` artifacts with metadata |
| PP-5 | Soul→KB Bridge | PP-4 | 2-3 hours | Session distillations auto-save |
| PP-6 | Staleness Scanner | PP-4 | 1 day | 30-day TTL re-vet system |
| PP-7 | AKVS Vetting | PP-4, PP-5 | 3-5 days | Autonomous knowledge vetting |
| PP-8 | Sycophancy Prevention | PP-7 | 2-3 days | BAVP pipeline with 3+ reviewers |
| PP-9 | Sovereign Pulse | None | 3-4 days | Context management system |

---

## §4 — Work Package Specifications

### CP-1: Chainlit UI Shell

**Objective**: Create a minimal Chainlit chat interface that connects to the Omega Oracle.

**File**: `src/omega/ui/chainlit_app.py`

**Requirements**:
1. Chainlit must run on `http://localhost:8000` (default)
2. Messages are sent to `Oracle.talk()` (not `Oracle.summon()` — that's for entity routing)
3. Responses must include: the response text, the entity that handled it, the model used, the confidence score
4. Streaming: If Chainlit supports streaming tokens, enable it (reduces perceived latency)
5. Error handling: If the Oracle fails (model unavailable, OOM), display a graceful error, not a crash
6. Session: Chainlit sessions must be persistent (file-based, not in-memory)

**Dependencies**:
- Chainlit must be installed: `pip install chainlit`
- Oracle must be importable: `from omega.oracle import Oracle`
- ModelGateway must be configured (CP-3)

**Success Criteria**:
- `chainlit run src/omega/ui/chainlit_app.py` starts without error
- User can type "hello" and receive a response
- Response includes entity name, model name, and confidence
- Sessions persist across page refreshes

**Rollback**:
- Delete `src/omega/ui/chainlit_app.py`
- Engine continues to work via `omega talk` CLI

**Known Risks**:
- Chainlit's async model may conflict with AnyIO's event loop
- Chainlit may require uvicorn, which may conflict with Omega Hub's MCP server
- Resolution: Chainlit and Omega Hub run on different ports (8000 vs 8016)

---

### CP-2: Oracle → UI Bridge

**Objective**: Create a clean interface between Chainlit and the Oracle that handles:
- Session mapping (Chainlit session ID → Omega session ID)
- Entity routing (show which entity handled the query)
- Error propagation (graceful degradation on model failure)
- Knowledge capture (save interesting interactions to KB)

**File**: `src/omega/ui/oracle_bridge.py`

**Requirements**:
1. `async def handle_message(message: str, session_id: str) -> OracleResponse`
   - Maps Chainlit session to Omega session
   - Calls `oracle.talk(message)`
   - Returns structured response with metadata
2. `async def save_to_kb(response: OracleResponse) -> None`
   - If confidence > 0.8, auto-save to `data/kb/_staging/`
   - If user explicitly requests ("save this"), save regardless of confidence
   - Format: frontmatter + body
3. Error handling:
   - Model OOM → retry with smaller model (fallback chain)
   - Model timeout → retry once, then error message
   - AnyIO error → log and return graceful error

**Dependencies**:
- CP-1 (Chainlit UI exists)
- CP-3 (ModelGateway configured)

**Success Criteria**:
- Messages flow from Chainlit → Bridge → Oracle → ModelGateway
- Responses include entity, model, confidence, trace_id
- KB auto-save works when confidence > 0.8
- Error messages are human-readable, not stack traces

---

### CP-3: Local GGUF Connection

**Objective**: Connect a local GGUF model to the ModelGateway so the engine can run without cloud APIs.

**File to modify**: `config/providers.yaml`

**Current state**: The `native-gguf` provider is defined in the provider chain at index 0.
The model path needs to point to an actual GGUF file on the system.

**Requirements**:
1. Find available GGUF models:
   ```bash
   ls -lh /media/arcana-novai/omega_library/models/gguf/
   ```
2. Select the primary model (recommended: `qwen3-1.7b-q4_k_m` for lightweight routing)
3. Update `config/providers.yaml`:
   ```yaml
   providers:
     native-gguf:
       enabled: true
       model: /media/arcana-novai/omega_library/models/gguf/<model-name>.gguf
       n_ctx: 4096
       n_threads: 8
       n_gpu_layers: 0  # CPU-only, no GPU
       verbose: false
   ```
4. Test local inference:
   ```bash
   omega talk "hello" --local
   ```

**Dependencies**: None (can be done in parallel with CP-1)

**Success Criteria**:
- `omega talk "hello" --local` returns a response
- Response time < 5 seconds on Ryzen 5700U
- RAM usage < 2GB during inference
- No cloud API calls are made

**Rollback**: Revert `config/providers.yaml` to previous state

**Known Risks**:
- If no GGUF models exist on the system, download one first
- Model may not load if RAM is insufficient (other services using memory)
- Resolution: Stop Redis, Qdrant, Postgres containers before testing

---

### CP-4: Entity Display in UI

**Objective**: Show which entity handled each query in the Chainlit UI.

**File**: `src/omega/ui/chainlit_app.py` (modification of CP-1)

**Requirements**:
1. After each Oracle response, display an info card:
   ```
   Entity: Lucifer (P7 Gnosis)
   Model: Qwen3-1.7B-Q4_K_M
   Confidence: 0.85
   Trace ID: abc123-def456
   ```
2. If entity routing changed during the conversation, show the transition
3. Show confidence trend over the session (increasing = good, decreasing = needs attention)

**Dependencies**: CP-1

---

### CP-5: Session Persistence

**Objective**: Chainlit sessions must persist to disk using Omega's existing session manager.

**File**: `src/omega/ui/session_bridge.py`

**Requirements**:
1. On Chainlit session start, create Omega session: `session_manager.create_session(entity)`
2. On each message, attach to Omega session
3. On Chainlit session end, close Omega session
4. Session files written to `data/sessions/{entity}.active`

**Dependencies**: CP-1

**Success Criteria**:
- Refreshing the browser doesn't lose conversation history
- Session files appear in `data/sessions/`
- Sessions are entity-scoped

---

### CP-6: Knowledge Save

**Objective**: Save high-quality interactions from the UI to the knowledge base.

**File**: `src/omega/ui/kb_bridge.py`

**Requirements**:
1. After each response, evaluate: should this be saved?
   - Auto-save if confidence > 0.8 AND response contains actionable information
   - User can type "save this" to force save
2. Save format:
   ```yaml
   ---
   ap_token: AP-{timestamp}
   title: "{topic summary}"
   created: {iso_date}
   source: "user:chainlit-session-{id}"
   tier: 0
   status: draft
   tags: []
   ---
   
   {response content}
   ```
3. Save to `data/kb/_staging/{domain}/{slug}.md`
4. Post to Hivemind: "new artifact in staging"

**Dependencies**: CP-1, CP-2

---

### CP-7: Agent Fleet Migration

**Objective**: Convert the 14 OpenCode-coupled agents to Omega standalone agents.

**Current problem**: The 14 agents in `.opencode/agents/` are Markdown files with YAML frontmatter
designed for OpenCode's agent system. They use `@mention` dispatch, OpenCode's tool permissions,
and OpenCode's session model. They cannot run without OpenCode.

**Migration strategy**: Create Omega-native agent definitions that can be invoked via the Oracle's
`summon()` method, which already supports entity routing.

**For each agent**:
1. Extract the agent's identity (personality, domain, system prompt)
2. Write an Omega entity YAML file: `config/wads/<wad>/entities/<agent-name>.yaml`
3. Wire the agent's capabilities to a Pillar slot or standalone function
4. Test invocation: `omega summon <agent-name> "task"`

**Priority agents to migrate first**:

| Agent | Priority | Reason |
|-------|----------|--------|
| `scribe.md` | P0 | Soul distillation is core functionality |
| `quality.md` | P0 | Code review and compliance are daily needs |
| `pillar.md` | P0 | Domain-specific work needs direct access |
| `doom_guy.md` | P1 | Heritage patterns, id Software research |
| `roc_racoon.md` | P1 | Legacy archaeology, pattern mining |
| `researcher.md` | P1 | Deep research capability |
| All others | P2 | After P0 and P1 are working |

**Dependencies**: CP-2 (Oracle routing works)

**Success Criteria**:
- `omega summon scribe "distill this session"` returns a response
- Agent personality matches the original `.opencode/agents/` definition
- No OpenCode dependency in the agent invocation path

---

### CP-8: Drop OpenCode

**Objective**: Remove OpenCode as a runtime dependency. OpenCode may still be installed for
development purposes, but the Omega Engine runs independently.

**Verification checklist**:
- [ ] Chainlit UI works without OpenCode
- [ ] `omega talk` works without OpenCode
- [ ] `omega summon` works without OpenCode
- [ ] All 312 tests pass without OpenCode installed
- [ ] Local inference works without OpenCode
- [ ] Cloud fallback works without OpenCode (via provider chain)
- [ ] Agent fleet works without OpenCode

**Dependencies**: CP-7 (agents migrated)

**Rollback**: If any check fails, OpenCode is re-enabled as a provider in the chain

---

## §5 — Audit Findings Affecting Transition

The 6 audits conducted by Roc Racoon identified issues that affect this transition.
The most critical:

### 5.1 — BLOCKERS (Must Resolve Before CP-1)

| Finding | Impact | Resolution |
|---------|--------|-----------|
| BAVP will OOM (4× 8B = 13.5GB > 14GB) | CP-7/P3B cannot be implemented as specified | Defer sycophancy prevention. Use single-model prompting. |
| Bootstrap paradox (P5 startup guard) | Engine won't start if KB foundation artifacts don't exist | Remove startup guard. Use soft warnings instead. |
| M2 firewall violation (KBSessionHook) | KB directive modifying `src/omega/` | Move hook to a separate service, not in `src/omega/` |

### 5.2 — RESOLVE BEFORE CP-7

| Finding | Impact | Resolution |
|---------|--------|-----------|
| ZONEID collision (0x1d4a20 vs 0x1d4a21) | Two constants for same concept | Use 0x1d4a21 (P1/P2 consensus) |
| Two KB roots (`data/library/` vs `data/kb/`) | Confusion about where artifacts live | Unify on `data/kb/` (existing structure) |
| 3 competing ADM formulas | Which sycophancy metric to use | Defer — not needed for critical path |
| Confidence scale (1-10 vs 0.0-1.0) | Inconsistent across TDs | Use 0.0-1.0 everywhere |
| Existing VETTING_PROTOCOL conflicts with BAVP | Two review workflows | Defer — manual vetting until 100+ artifacts |

### 5.3 — DEFERRED (Post-Critical-Path)

| Finding | Impact | Resolution |
|---------|--------|-----------|
| 14 missing [id-soft:] tags | M14 compliance | Fix during heritage audit (separate work) |
| 6 atomic write implementations | Code duplication | Consolidate after critical path |
| 9 missing TDs (AuthN, Backup, etc.) | Feature gaps | Address when needed |
| 13/18 lifecycle stages unimplemented | Spec vs reality | Implement incrementally |

---

## §6 — Hardware Constraints

| Resource | Current | Available | Notes |
|----------|---------|-----------|-------|
| RAM | 14GB total | ~9GB usable | OS + containers consume ~5GB |
| CPU | AMD Ryzen 7 5700U | 8C/16T, Zen 2 | AVX2 support, no AVX-512 |
| GPU | None | 0 | CPU-only inference |
| Disk | NVMe | 4.8GB free | `omega_library` partition |
| Network | Available | Varies | Cloud APIs require internet |

**Inference constraints**:
- Maximum model size: ~5GB GGUF (fits in 9GB available RAM with OS overhead)
- Recommended models: Qwen3-1.7B, Qwen3-4B, DeepSeek-R1-8B (all GGUF Q4_K_M)
- One model at a time (ResourceGuard Semaphore(1))
- Inference latency: 2-15 seconds depending on model size

**Chainlit constraints**:
- Runs on port 8000 (default)
- No GPU acceleration for UI rendering
- WebSocket connections for streaming (limited to ~10 concurrent)

---

## §7 — Testing Strategy

### 7.1 — Unit Tests (Existing — Must Continue Passing)

All 320 existing tests must continue to pass after every work package.
Run: `make test` (320/320, verified by P10 validation 2026-06-06)

### 7.2 — Integration Tests (New — Per Work Package)

| WP | Test | How |
|----|------|-----|
| CP-1 | Chainlit starts | `chainlit run src/omega/ui/chainlit_app.py` → no error |
| CP-1 | Message flow | Send "hello" → response within 10s |
| CP-2 | Entity display | Response includes entity name |
| CP-3 | Local inference | `omega talk "hello" --local` → response |
| CP-3 | No cloud calls | `omega talk "hello" --local` → no network traffic |
| CP-4 | Info card | UI shows entity, model, confidence |
| CP-5 | Session persist | Refresh browser → history intact |
| CP-6 | KB save | Confidence > 0.8 → file in `_staging/` |
| CP-7 | Agent invoke | `omega summon scribe "test"` → response |
| CP-8 | No OpenCode | All checks in §5 pass |

### 7.3 — Regression Tests

After each work package:
```bash
make test           # 320/320 (was 312, P10 validation fixed 3 bugs)
make temple-grade    # T1-T11 pass
make heritage-map    # [id-soft:] tags verified
make sovereignty     # Local/cloud ratio
```

---

## §8 — Rollback Procedures

### Per-Work-Package Rollback

Each work package has a defined rollback:
- **CP-1**: Delete `src/omega/ui/chainlit_app.py`. Engine via CLI only.
- **CP-2**: Delete `src/omega/ui/oracle_bridge.py`. Chainlit can still display raw responses.
- **CP-3**: Revert `config/providers.yaml`. Cloud-only inference.
- **CP-4**: Remove info card code. UI still works.
- **CP-5**: Delete `src/omega/ui/session_bridge.py`. Sessions are ephemeral.
- **CP-6**: Delete `src/omega/ui/kb_bridge.py`. No auto-save.
- **CP-7**: Re-enable OpenCode provider in `providers.yaml`.
- **CP-8**: Re-enable OpenCode as provider.

### Emergency Rollback

If the engine becomes unresponsive:
```bash
# Stop all Omega services
pkill -f "chainlit"
pkill -f "omega-hub"
pkill -f "python.*omega"

# Revert to last known good
git checkout -- config/providers.yaml
git checkout -- src/omega/oracle/oracle.py

# Restart
make test  # Verify 312/312
```

---

## §9 — Performance Targets

| Metric | Realistic Target | Notes |
|--------|-----------------|-------|
| Chainlit startup | < 5 seconds | `time chainlit run src/omega/ui/chainlit_app.py` |
| Message → first token | < 2s (1.7B), < 5s (4B) | User types → first token appears (model must be warm) |
| Message → full response (1.7B) | < 10 seconds | Short query, ~200t response |
| Message → full response (4B) | < 30 seconds | Includes internal chain-of-thought tokens |
| Message → full response (8B) | < 60 seconds | **NOT recommended for interactive use.** Background-only. |
| Local inference (1.7B) | 3-8 seconds | `omega talk "hello" --local` — warm model |
| Local inference (4B) | 8-25 seconds | `omega talk "reason about this" --local` — warm model |
| Local inference (8B) | 18-55 seconds | `omega talk "analyze deeply" --local` — **will OOM on 9GB RAM** |
| RAM during inference (1.7B) | < 3GB | 1.5GB model + 1.5GB overhead |
| RAM during inference (4B) | < 6GB | 4GB model + 2GB overhead — tight on 9GB usable |
| RAM during inference (8B) | **>9GB** | **WILL OOM.** Stop containers before attempting. |
| Session load | < 1 second | Browser refresh → history restored |
| KB save | < 500ms | Confidence > 0.8 → file written |

---

## §10 — Success Criteria

The transition is complete when:

1. **Chainlit UI runs**: `chainlit run src/omega/ui/chainlit_app.py` starts without error
2. **Local inference works**: WiFi off → engine responds
3. **Cloud is optional**: WiFi on → engine uses cloud as fallback, not primary
4. **Entities display**: UI shows which entity handled each query
5. **Sessions persist**: Browser refresh doesn't lose history
6. **KB auto-saves**: High-confidence interactions saved to `data/kb/_staging/`
7. **Agents work**: `omega summon scribe` invokes the Scribe agent
8. **OpenCode optional**: Engine runs without OpenCode installed
9. **320 tests pass**: No regressions (baseline: 320, was 312)
10. **No OOM**: Engine stays under 9GB RAM during all operations. **Note: 8B models exceed this limit. Background-only.**

---

## §11 — What NOT To Build (Scope Exclusions)

The following are explicitly **excluded** from this transition:

| Component | Reason | When |
|-----------|--------|------|
| AKVS Vetting Pipeline | 0 artifacts to vet. Manual vet until 100+ | When KB has 100+ artifacts |
| Sycophancy Prevention (BAVP) | Requires 4× 8B models, RAM exceeds 14GB | When 32GB+ RAM available |
| Staleness Scanner | Nothing is stale if nothing is vetted | After AKVS is live |
| Frontmatter Migration | 1 file without frontmatter, not 141 | When KB has 100+ files |
| Chunking Utility | 141 docs, FTS5 is instant | When KB has 500+ docs |
| Edge Index / Dependency Graph | Over-engineering for current scale | When KB has 500+ docs |
| Sovereign Pulse | Context windows aren't overflowing | When context limits are hit |
| Desktop App (Electron/Tauri) | Chainlit is sufficient for now | After Chainlit proves value |
| Multi-user | Single user for now | When team grows |
| ZONEID on every artifact | Engine works without it | When write path is solid |

---

## §12 — Legacy Code References

The following legacy patterns should be referenced during implementation:

### Atomic Writes
- **Legacy**: `xna-omega-legacy/src/omega/core/file_operations.py` (Pattern 4)
- **New spec**: `data/kb/_staging/knowledge_systems/TD-P1-ATOMIC-WRITE-PROTOCOL.md`
- **Recommendation**: Implement per P1 spec, but reference legacy for edge cases

### Circuit Breaker
- **Legacy**: `omega-stack-legacy/src/omega/circuit_breaker.py` (36-line sync version)
- **New**: `src/omega/oracle/health_monitor.py::AsyncCircuitBreaker` (200+ lines AnyIO)
- **Recommendation**: Use existing `AsyncCircuitBreaker`. Do not recreate.

### Entity Registry
- **Legacy**: `omega-stack-legacy/app/XNAi_rag_app/core/entities/registry.py`
- **New**: `src/omega/oracle/entity_registry.py` (already implemented)
- **Recommendation**: Use existing. Legacy is for reference only.

### Chainlit UI
- **Legacy**: `~/Documents/Archives/Old-Stacks/Xoe-NovAi/` (Era 1, August 2025)
- **New**: `src/omega/ui/chainlit_app.py` (to be created)
- **Recommendation**: Find legacy Chainlit code, adapt to current Oracle API

---

## §13 — Communication Protocol

During implementation, Antigravity should:

1. **Post progress to Hivemind**:
   ```python
   omega-hub_hivemind_post_context(
       cli="antigravity",
       model="qwen3-1.7b",
       task_current="CP-1: Building Chainlit UI shell",
       focus_chain=["CP-1", "chainlit", "oracle-bridge"],
       decisions=[{"CP-1": "Using Chainlit default port 8000"}],
       continuation="Next: Wire Oracle.talk() to Chainlit on_message"
   )
   ```

2. **Heartbeat every 10 minutes** during active work:
   ```python
   omega-hub_hivemind_heartbeat(cli="antigravity")
   ```

3. **Run tests after each work package**:
    ```bash
    make test  # 320/320 (was 312, P10 validation June 6)
    ```

4. **Commit with proper prefix**:
   ```bash
   git add -A && git commit -m "feat(ui): CP-1 Chainlit UI shell"
   ```

---

## §14 — Appendix: The Oracle API

For reference, the Oracle's public API that the UI must interface with:

```python
class Oracle:
    async def talk(self, query: str, entity: str = None) -> OracleResponse:
        """Route a query through the Oracle. Speculative decoding handled internally.
        
        Args:
            query: The user's message
            entity: Optional entity name to force routing
            
        Returns:
            OracleResponse with fields:
                - text: str (the response)
                - entity: str (which entity handled it)
                - model: str (which model was used)
                - confidence: float (0.0-1.0)
                - trace_id: str (UUID for observability)
                - session_id: str (the session ID)
        """
        
    async def summon(self, entity_name: str, query: str) -> OracleResponse:
        """Directly summon a specific entity by name.
        
        Args:
            entity_name: The entity to invoke (e.g., "lucifer", "scribe")
            query: The task or question for the entity
            
        Returns:
            OracleResponse with the entity's response
        """
```

**Key implementation note**: The Oracle uses `ResourceGuard` (AnyIO Semaphore(1))
to prevent concurrent model inference. If two messages arrive simultaneously,
the second will queue. This is by design — OOM protection on 14GB hardware.

---

## §15 — Appendix: File System Layout

```
omega-engine/
├── config/
│   ├── omega.yaml              ← Engine core config
│   ├── providers.yaml          ← Provider chain (MUST be modified for CP-3)
│   ├── models.yaml             ← Model specs
│   └── wads/
│       ├── arcana_novai/
│       │   └── entities.yaml   ← Entity definitions
│       └── _omega_default/
│           └── entities.yaml   ← Default entities
├── src/
│   └── omega/
│       ├── oracle/
│       │   ├── oracle.py       ← Main entry point
│       │   ├── model_gateway.py← Provider chain
│       │   ├── entity_registry.py ← Entity CRUD
│       │   ├── context_builder.py ← Memory injection
│       │   ├── health_monitor.py  ← Circuit breaker
│       │   ├── resource_guard.py  ← OOM protection
│       │   └── cpu_optimizer.py   ← Zen 2 optimization
│       ├── observability.py    ← Trace IDs, logging
│       ├── memory_store.py     ← Hot/Warm/Cold memory
│       ├── session_manager.py  ← Session persistence
│       ├── cvar_table.py       ← Named constants
│       ├── constants.py        ← ZONEID constants
│       ├── ui/                 ← NEW: Chainlit UI
│       │   ├── chainlit_app.py ← CP-1: Main UI (TO CREATE)
│       │   ├── oracle_bridge.py← CP-2: Oracle interface (TO CREATE)
│       │   ├── session_bridge.py← CP-5: Session persistence (TO CREATE)
│       │   └── kb_bridge.py    ← CP-6: Knowledge save (TO CREATE)
│       └── cli/
│           └── oracle_cli.py   ← Typer CLI
├── mcp_servers/
│   └── omega_hub/
│       └── server.py           ← MCP Hub + Hivemind
├── data/
│   ├── kb/                     ← Knowledge base
│   │   ├── _staging/           ← Active research/TDs
│   │   └── _meta/              ← Metadata indexes
│   ├── entities/               ← Entity workspaces
│   │   ├── kali/soul.yaml
│   │   ├── lucifer/soul.yaml
│   │   └── ...
│   ├── sessions/               ← Session files
│   ├── logs/                   ← Observability logs
│   ├── coordination/           ← Hivemind files
│   └── handoff/                ← Handoff documents
├── tests/
│   └── test_*.py               ← 312 passing tests
├── .opencode/
│   └── agents/                 ← OpenCode agents (TO MIGRATE in CP-7)
├── Makefile                    ← Build/test targets
├── OMEGA_ENGINE.md             ← Single source of truth
├── SOVEREIGN_MANDATES.md       ← 14 mandates (M1-M14)
└── AGENTS.md                   ← Agent behavior rules
```

---

*Handoff prepared by: Roc Racoon (Legacy Archaeologist)*
*Audit reviewed by: Lilith (Dark Oversoul), Ma'at (Light Oversoul), Kali (Transcendent)*
*Status: READY FOR IMPLEMENTATION*
*Date: 2026-06-06*
*Version: 2.0*
*Next action: Antigravity reads this document and begins CP-1 (Chainlit UI Shell)*

⬡ OMEGA ⬡ ROC-RACOON ⬡ ANTIGRAVITY HANDOFF v2.0 ⬡

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: ANTIGRAVITY TRANSITION | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

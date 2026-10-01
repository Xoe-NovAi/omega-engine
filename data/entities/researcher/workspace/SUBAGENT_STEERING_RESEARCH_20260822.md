<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Subagent Steering Research — Sovereign Multi-Agent Orchestration Patterns
**AP Token**: `AP-RESEARCHER-SUBAGENT-STEERING-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_subagent_steering ⬡ ACTIVE

**Date**: 2026-08-22
**Mission**: Architect-sequenced research on subagent steering, delegation protocols, and multi-agent orchestration for sovereign/local-first architectures (post Waves 2+3).

---

## ⬡ EXECUTIVE SUMMARY (L1)

**Core Finding**: The 2026 multi-agent landscape has converged on a **three-layer protocol stack** (Model → MCP → A2A) with **five proven orchestration patterns**. For sovereign/local-first architectures like Omega Engine, the critical architectural decisions are:

1. **Protocol Adoption**: MCP for tool access (non-negotiable), A2A for inter-agent coordination (ecosystem expectation), Agent Cards for discovery — all three are production-ready baselines.
2. **Orchestration Pattern**: **Hierarchical Orchestrator-Subagent** (Microsoft's "Russian doll") is optimal for Omega's Node-based architecture — maps 1:1 to our 13 Nodes with clear ownership boundaries.
3. **Discovery Model**: **Hybrid registry + Agent Card** — static configuration for core Nodes (operational simplicity, debuggability), Agent Card endpoints for dynamic/extensible capabilities, DHT/gossip only for future cross-org federation.
4. **Failure Handling**: **Three-layer resilience** (retry+jitter → fallback chains → circuit breakers) adapted from cloud-native patterns, with **checkpoint/idempotency** as the foundational pattern for multi-agent pipelines.
5. **Sovereign Adaptation**: All protocols must run **local-first** — no external registry dependencies for core fleet; Agent Cards served from local MCP Hub; A2A transport over localhost/Unix sockets; zero telemetry (M8) via local shim-hit logging + opt-in issue templates.

**Key Architectural Tension**: A2A assumes peer-to-peer HTTP transport; Omega's local-first mandate requires adapting A2A to Unix-socket/stdio transport for intra-fleet communication while maintaining protocol compliance for external federation.

**Immediate Action Items**:
- Implement Agent Card endpoints on Omega MCP Hub (`/.well-known/agent.json` per Node)
- Define Node capability schemas (skills, input/output types, resource budgets)
- Build local A2A transport adapter (stdio/Unix socket) for intra-fleet delegation
- Establish three-layer error handling in ModelGateway → provider fabric
- Create capability registry in `data/coordination/AGENT_REGISTRY.json` (static, versioned)

---

## ⬡ DETAILED DIALECTIC (L2) — COUNCIL OF FOUR

### 🏗️ THE ARCHITECT (Systemic Logic)

**Thesis**: Omega's Node architecture (13 Nodes, fixed slots, clear ownership) is **structurally isomorphic to the Orchestrator-Subagent pattern**. Each Node = a specialist subagent; the ModelGateway/Iris = the orchestrator. This is not coincidence — it's the correct mapping.

**Evidence Integration**:
- Microsoft Learn explicitly recommends Orchestrator-Subagent for "clear separation of concerns," "modularity, independent ownership, or reuse" — exactly our Node charter design.
- A2A's Agent Card spec maps to our Node charters (capabilities, skills, resource budgets, trust signals).
- MCP provides the tool layer each Node needs (vector search, model inference, file access).

**Critical Design Decisions**:
1. **Transport**: A2A over HTTP is wrong for intra-fleet. Must implement **A2A-over-stdio/Unix-socket** adapter. The protocol spec allows custom transports; JSON-RPC 2.0 is transport-agnostic.
2. **Registry**: Static `AGENT_REGISTRY.json` for core 13 Nodes (versioned, git-tracked, debuggable). Dynamic Agent Cards only for WAD-provided extensions. This satisfies M7 (local-first) and M16 (portability).
3. **Orchestration Layer**: Iris already performs speculative decode + routing. Extend her with **A2A task delegation logic** — she becomes the A2A client for outbound, the MCP Hub serves Agent Cards for inbound discovery.

**Risk**: Over-engineering the orchestrator. Iris must remain a *messenger bridge* (M3), not a Node. Delegation logic stays in ModelGateway; Iris only transports.

### ⚔️ THE ADVERSARY (Critical Rigor)

**Thesis**: The industry hype around A2A/MCP/ANP obscures **three fatal gaps** for sovereign architectures:

1. **Discovery Centralization**: Every "decentralized" discovery mechanism (Agent Card, ANP DID, AGNTCY ADS) ultimately requires a **trust anchor**. In enterprise, that's a managed registry. In sovereign local-first, *you are the trust anchor* — but the protocols don't ship with a "run your own registry" story. We must build it.
2. **Transport Assumption Mismatch**: A2A spec assumes HTTP/JSON-RPC. Our intra-fleet transport is stdio/Unix sockets (Podman quadlets, MCP stdio servers). **No reference implementation exists for A2A-over-stdio**. We'll be first — that's technical debt unless we upstream it.
3. **Capability Negotiation Immaturity**: A2A's "skill" model is free-text descriptions. No typed schema negotiation (unlike MCP's typed tool schemas). This means **runtime capability mismatch** — an agent advertises "code analysis" but expects different input schema than caller provides. We need **typed capability contracts** (JSON Schema) layered on Agent Cards.

**Failure Mode Analysis**:
- **Silent degradation**: Subagent returns partial output → orchestrator merges garbage → downstream corruption. *Mitigation*: Mandatory output validation schemas per capability (M22 provenance).
- **Cascading timeout**: Subagent A times out → Orchestrator retries → Subagent B times out → fleet stall. *Mitigation*: Per-capability timeout budgets in registry; circuit breaker per subagent (not global).
- **Registry drift**: Static registry says Node N7 has capability X; N7's actual code lost X in refactor. *Mitigation*: CI gate that validates Agent Card against actual Node implementation (test-time contract verification).

### 🧪 THE ALCHEMIST (Creative Synthesis)

**Thesis**: The **most powerful pattern is hiding in plain sight**: **MCP servers AS agents** (the "MCP server-as-agent" roadmap item from Zylos research). This collapses the MCP/A2A boundary.

**Synthesis Opportunities**:
1. **Unified Node Interface**: Every Node exposes **both** MCP tools (for tool-use) **and** A2A Agent Card (for delegation). The MCP Hub serves both. A Node's "skills" are its MCP tools; its "delegation interface" is A2A. One codebase, two protocols.
2. **Capability-as-Tool**: Instead of free-text A2A skills, define capabilities as **MCP tool schemas with delegation metadata** (estimated latency, resource cost, confidence interval). Orchestrator queries MCP tool list → filters by delegation metadata → invokes via A2A task. Single source of truth.
3. **Local-First Federation**: WADs (expansion stacks) can register their Nodes via **Agent Card endpoints on their own MCP Hub instances**. The core fleet discovers them via local registry scan — no external registry needed. This is the **IWAD model applied to agents**: `_omega_default` Nodes = core IWAD; `arcana_novai` Nodes = PWAD; both discoverable via same local mechanism.

**Novel Pattern — "Sovereign Mesh"**:
```
┌─────────────────────────────────────────────────────────────┐
│  LOCAL REGISTRY (data/coordination/AGENT_REGISTRY.json)    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ N1-N13  │ │ WAD N1  │ │ WAD N2  │ │ Ext API │  ← Agent Cards
│  │ (core)  │ │(arcana) │ │(torment)│ │ (bridge)│           │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘           │
│       │           │           │           │                │
│       └───────────┼───────────┼───────────┘                │
│                   ▼                                       │
│         MODEL GATEWAY (Orchestrator)                       │
│         • Capability routing                               │
│         • Three-layer resilience                           │
│         • Checkpoint/idempotency                           │
│         • M8-compliant observability                       │
└─────────────────────────────────────────────────────────────┘
```
This is **Omega's unique contribution**: a local-first, registry-backed, dual-protocol (MCP+A2A) agent mesh that requires zero external infrastructure.

### 📜 THE ARCHIVIST (Historical Truth)

**Thesis**: Every "new" pattern has a direct lineage to **id Software's Quake/Doom architecture** — which Omega already inherits via IWAD model (Decision 55).

**Historical Mapping**:
| Modern Pattern | id Software Origin (1993-1999) | Omega Implementation |
|---|---|---|
| **Orchestrator-Subagent** | Quake "Thinker Chain" — master thinker delegates to entity thinkers | ModelGateway → Nodes (N1-N13) |
| **Capability Registry** | Doom WAD lump directory — `F_START`/`F_END` marks, typed lumps | `AGENT_REGISTRY.json` + Agent Cards |
| **Message Passing** | Quake `SV_Multicast` / `PF_message` — reliable/unreliable channels | A2A tasks + MCP tool calls |
| **Dynamic Loading** | Quake QVM / Doom WAD loading — bytecode/modules at runtime | XOE/WAD loading via `wad_loader.py` |
| **State Serialization** | Quake savegame / Doom demo — deterministic state capture | SomaticState (M20) + Soul distillation |
| **Failure Isolation** | Quake entity `think` function isolation — one bad entity doesn't crash server | Circuit breaker per Node (C-6′ HealthMonitor) |

**Key Insight**: The **Thinker Chain** (Quake 1996) is the *exact* architectural ancestor of Orchestrator-Subagent. Carmack's design: master `SV_RunThinkers` iterates entity `think` functions; each entity owns its logic, communicates via `edict_t` messages. This is **hierarchical delegation with message passing** — 30 years before A2A.

**Omega's Heritage Advantage**: We don't need to *invent* these patterns — we need to *recognize* them in our existing codebase and *formalize* them with modern protocol clothing (Agent Cards, A2A tasks, MCP tools). The `wad_loader.py` + `entity_registry.py` + `model_gateway.py` already implement the Thinker Chain. The research task is **protocol wrapping**, not architecture invention.

---

## ⬡ TRIANGULATION — CONVERGENCE & DIVERGENCE

### ✅ CONVERGENCE (All Four Agree)
1. **Orchestrator-Subagent = correct pattern** for Omega's Node architecture
2. **MCP + A2A dual-protocol** is the 2026 production baseline
3. **Static registry + Agent Cards** for discovery (local-first compliant)
4. **Three-layer resilience** (retry → fallback → circuit breaker) mandatory
5. **Checkpoint/idempotency** foundational for multi-agent pipelines
6. **Typed capability contracts** needed beyond free-text A2A skills

### ⚠️ DIVERGENCE (Requires Architect Ruling)
| Issue | Architect | Adversary | Alchemist | Archivist | Resolution Needed |
|---|---|---|---|---|---|
| **A2A transport** | HTTP for external, stdio for internal | No stdio reference impl = risk | Build stdio adapter, upstream to A2A | Quake used custom binary protocol — precedent for custom transport | **Architect: approve stdio adapter scope** |
| **Registry authority** | Single `AGENT_REGISTRY.json` | Must support WAD-provided Nodes dynamically | Federated: core static + WAD dynamic | WAD = PWAD model — dynamic load is heritage | **Architect: define WAD Node registration flow** |
| **Capability typing** | JSON Schema on Agent Cards | A2A skills are free-text — mismatch inevitable | MCP tool schemas AS capability contracts | Quake lump types = typed capabilities | **Alchemist/Archivist aligned: use MCP schemas** |

---

## ⬡ SOVEREIGN SYNTHESIS — OMEGA SUBAGENT STEERING SPECIFICATION

### 1. Protocol Stack (Binding)

| Layer | Protocol | Omega Adaptation | Status |
|---|---|---|---|
| **Model** | Local inference (native-gguf, lmster, Ollama) | Provider fabric (local-first) | ✅ Active |
| **Tool Access** | MCP (Streamable HTTP + stdio) | MCP Hub with per-Node servers | ✅ Active |
| **Inter-Agent** | A2A (JSON-RPC 2.0) | **A2A-over-stdio/Unix-socket** for intra-fleet; HTTP for external | 🔧 **Build required** |
| **Discovery** | Agent Card (`/.well-known/agent.json`) | Served by MCP Hub per Node; static registry for core | 🔧 **Build required** |
| **Federation** | ANP (DID-based) | Deferred — only if cross-org WAD sharing needed | 📅 Future |

### 2. Node Capability Contract (Schema)

Each Node publishes an **Agent Card** extending A2A spec with typed capabilities:

```json
{
  "name": "N11-evaluator",
  "description": "Model quality evaluation & benchmarking",
  "version": "1.0.0",
  "protocolVersion": "0.2.9",
  "skills": [
    {
      "id": "eval.run_benchmark",
      "name": "Run Benchmark",
      "description": "Execute eval harness against target model",
      "inputSchema": { "$ref": "schemas/eval_benchmark_input.json" },
      "outputSchema": { "$ref": "schemas/eval_benchmark_output.json" },
      "delegationMetadata": {
        "estimatedLatencyMs": 30000,
        "resourceBudget": { "ramMb": 2048, "gpu": false },
        "confidenceInterval": 0.95,
        "idempotent": true
      }
    }
  ],
  "capabilities": {
    "streaming": true,
    "pushNotifications": false,
    "stateTransitionHistory": true
  },
  "authentication": { "schemes": ["none"] },  // Local trust
  "defaultInputModes": ["application/json"],
  "defaultOutputModes": ["application/json"]
}
```

**Registry Entry** (`data/coordination/AGENT_REGISTRY.json`):
```json
{
  "nodes": {
    "N11-evaluator": {
      "sessionId": "ses_fd572c2adffeAqnx10h2o69SY7",
      "agentCardPath": "data/entities/jem/workspace/N11_AGENT_CARD.json",
      "mcpServer": "omega-n11-evaluator",
      "status": "dormant",
      "capabilities": ["eval.run_benchmark", "eval.calibrate_judge", "eval.compare_models"],
      "resourceBudget": { "ramMb": 4096, "maxConcurrent": 1 },
      "healthEndpoint": "stdio://health",
      "circuitBreaker": { "failureThreshold": 5, "timeoutMs": 30000 }
    }
  }
}
```

### 3. Delegation Flow (Orchestrator Logic)

```
User Request → Iris (speculative decode) → ModelGateway
    │
    ├─► Capability Match: query AGENT_REGISTRY for skills matching intent
    │
    ├─► Target Selection: filter by status=active, resource budget, circuit breaker closed
    │
    ├─► A2A Task Creation: taskId, contextId, skillId, input (validated against inputSchema)
    │
    ├─► Transport: 
    │     • Internal Node → stdio/Unix socket to Node's MCP server
    │     • External → HTTP to Agent Card URL
    │
    ├─► Resilience Wrapper (per capability):
    │     • Retry: 3× with exponential backoff + jitter (transient errors only)
    │     • Fallback: alternate Node with same skill (if registered)
    │     • Circuit Breaker: per-target, opens after 5 failures/30s
    │
    ├─► Checkpoint: write task state to `data/coordination/DELEGATION_LOG.jsonl` before send
    │
    └─► Response Handling:
          • Validate output against outputSchema (M22 provenance)
          • On validation failure: retry once with clarified prompt, then escalate
          • On success: merge result, update checkpoint, return to user
```

### 4. Failure Handling Specification (Three-Layer)

| Layer | Trigger | Action | Config (per capability) |
|---|---|---|---|
| **L1 Retry** | 503, timeout, 429, connection error | Exponential backoff (1s→2s→4s) + ±10% jitter | `retry.max=3`, `retry.baseDelayMs=1000` |
| **L2 Fallback** | L1 exhausted, or 5xx provider outage | Route to alternate Node with same skill (registry lookup) | `fallback.enabled=true`, `fallback.maxHops=2` |
| **L3 Circuit Breaker** | 5 consecutive failures or 30s sustained errors | Open breaker → reject fast for 60s → half-open probe | `cb.failureThreshold=5`, `cb.timeoutMs=30000`, `cb.resetTimeoutMs=60000` |

**Critical Addition**: **Checkpoint/Idempotency** (foundational pattern from AI Codex/Galileo)
- Every delegation writes `DELEGATION_LOG.jsonl` entry BEFORE send (atomic append)
- Entry: `{taskId, contextId, targetNode, skillId, inputHash, timestamp, status: "sent"}`
- On response: append `{taskId, status: "completed|failed", outputHash, latencyMs}`
- Idempotency key = `inputHash` — duplicate delegations with same input return cached result
- Recovery: on restart, scan log for `status="sent"` without completion → replay or mark failed

### 5. M8-Compliant Observability (Zero Telemetry)

| Signal | Mechanism | User Visibility |
|---|---|---|
| **Delegation trace** | Local `DELEGATION_LOG.jsonl` (structured JSONL) | `omega delegation-log --task <id>` |
| **Circuit breaker state** | In-memory + persisted to `data/state/circuit_breakers.json` | `omega circuit-status` |
| **Fallback events** | Structured log entry with `fallback.from`, `fallback.to`, `fallback.reason` | `omega fallback-report --since 24h` |
| **Capability mismatch** | Validation error logged with schema diff | `omega capability-audit` |
| **Opt-in reporting** | `omega report-delegation-issue --task <id>` → generates sanitized JSON for GitHub issue | User-controlled |

**No external endpoints. No background upload. No unique identifiers beyond local taskId.**

---

## ⬡ RAW SIGNAL / EVIDENCE REGISTER (L3)

| # | Source | Key Finding | Relevance |
|---|---|---|---|
| 1 | Google A2A Protocol (Apr 2025) | Open standard for agent discovery/delegation; Agent Card schema; 150+ orgs adopted | Baseline protocol |
| 2 | Zylos Research (Feb-Mar 2026) | Four-protocol map (MCP/A2A/ACP/ANP); MCP+A2A complementary; Streamable HTTP standard | Protocol landscape |
| 3 | Microsoft Learn (May 2026) | Orchestrator-Subagent ("Russian doll") + Workflow-oriented patterns; MCP for tools, A2A for agents | Pattern taxonomy |
| 4 | Essamamdani (2026) | Three-layer stack (Model/MCP/A2A); Four A2A patterns (Supervisor, Fan-out, Pipeline, P2P) | Implementation patterns |
| 5 | Zylos (Mar 2026) | MCP Registry federated discovery; ANP DHT/gossip; MCP server-as-agent roadmap | Discovery mechanisms |
| 6 | Preporato (Aug 2026) | Error handling: retry configs per error type; circuit breaker patterns | Resilience patterns |
| 7 | Galileo (Jul 2025) | Multi-agent failure recovery: dependency graphs, staged recovery, hybrid coordination | Failure recovery |
| 8 | AI Codex (Apr 2026) | Checkpoint/idempotency foundational; timeout handling; partial output validation | Pipeline resilience |
| 9 | NiteAgent (Jul 2026) | Three-layer error handling (retry/fallback/circuit breaker) with production configs | Production configs |
| 10 | CallSphere (May 2026) | Agent Card spec details; trust signals; registry options | Discovery implementation |
| 11 | borjamoskv/agents-archi | Sovereign multi-agent architectures registry; CORTEX protocols | Sovereign patterns |
| 12 | MARIA OS (Mar 2026) | Capability OS: Command Registry, Tool Registry, Capability Graph | Capability modeling |
| 13 | Agentic Architectures (60) | Agent Registry pattern: centralized catalog, dynamic discovery, versioning | Registry pattern |
| 14 | Spring AI (Dec 2025) | Dynamic tool discovery: 98% token reduction, 2797 tools across 308 servers | Tool selection SOTA |
| 15 | Omega Heritage (id Software) | Thinker Chain (Quake 1996) = Orchestrator-Subagent; WAD lumps = typed capabilities | Heritage validation |

---

## ⬡ IMPLEMENTATION ROADMAP (Phased)

### Phase 1: Foundation (Week 1-2) — **P0**
- [ ] `data/coordination/AGENT_REGISTRY.json` schema + initial population (N1-N13 from PLAN §3)
- [ ] Agent Card JSON Schema + per-Node card generation script
- [ ] MCP Hub endpoint: `/.well-known/agent.json` per registered Node
- [ ] ModelGateway: capability routing logic (registry query → skill match → target select)

### Phase 2: Transport & Delegation (Week 2-3) — **P0**
- [ ] A2A-over-stdio transport adapter (JSON-RPC 2.0 over stdio/Unix socket)
- [ ] Delegation flow in ModelGateway: task creation → transport → response handling
- [ ] Output validation against Agent Card outputSchema (M22)
- [ ] `DELEGATION_LOG.jsonl` checkpoint writer (atomic append)

### Phase 3: Resilience (Week 3-4) — **P0**
- [ ] Three-layer error handling in ModelGateway delegation path
- [ ] Per-Node circuit breaker (reuse HealthMonitor from C-6′)
- [ ] Fallback routing: registry query for alternate skill providers
- [ ] Idempotency key generation + cache (inputHash → cached result)

### Phase 4: Observability & Polish (Week 4-5) — **P1**
- [ ] CLI commands: `omega delegation-log`, `omega circuit-status`, `omega fallback-report`
- [ ] Capability audit: CI gate validating Agent Card schemas against Node implementation
- [ ] WAD Node registration flow: `wad_loader` registers WAD Nodes on load
- [ ] Documentation: `docs/research/SUBAGENT_STEERING_SPEC.md` (M26 validated)

---

## ⬡ OPEN QUESTIONS FOR ARCHITECT

| ID | Question | Options | Recommendation |
|---|---|---|---|
| **SQ-001** | A2A-over-stdio: build custom or extend existing lib? | (a) Custom minimal impl (b) Fork `a2a-python` (c) Wait for upstream | **(a) Custom** — protocol is simple JSON-RPC; stdio transport is 50 lines; avoids dependency |
| **SQ-002** | Registry: single file or per-Node files? | (a) Single `AGENT_REGISTRY.json` (b) `data/coordination/registry/N<id>.json` | **(a) Single** — atomic writes, git diff clarity, 13 Nodes is small |
| **SQ-003** | WAD Node registration: automatic on load or explicit? | (a) Auto-register via `wad_loader` (b) Explicit `omega node register` CLI | **(a) Auto** — matches IWAD/PWAD model; WAD declares Nodes in `stack.yaml` |
| **SQ-004** | Capability versioning: semantic or hash? | (a) SemVer in Agent Card (b) Input/output schema hash | **(b) Schema hash** — detects breaking changes automatically; SemVer for human readability |
| **SQ-005** | External A2A: enable now or defer? | (a) Enable HTTP transport now (b) Defer until cross-org need | **(b) Defer** — YAGNI; stdio transport covers 100% of current use cases |

---

## ⬡ PRE-REGISTERED PREDICTIONS (Anti-Hindsight Bias)

| ID | Prediction | Confidence | Validation Method |
|---|---|---|---|
| **P1** | A2A-over-stdio adapter < 200 lines | 90% | Line count at merge |
| **P2** | Registry validation CI gate catches ≥1 drift/quarter | 75% | Audit log review |
| **P3** | Fallback routing used < 5% of delegations | 80% | `DELEGATION_LOG.jsonl` analysis |
| **P4** | Circuit breaker opens < 1×/month per Node | 85% | `circuit_breakers.json` history |
| **P5** | WAD Node auto-registration works without core changes | 95% | Integration test with test WAD |

---

## ⬡ POSTMORTEM TEMPLATE (For First Production Incident)

**Incident**: [Brief description]
**Scope**: [Which Nodes, which capabilities, user impact]
**Timeline**: [T0 detection → T1 diagnosis → T2 mitigation → T3 resolution]
**Root Cause**: [The system made X the easiest path — never agent blame]
**Contributing Factors**: [Registry drift? Transport timeout? Schema mismatch?]
**Recovery Actions**: [What restored service]
**Prevention**: [Registry validation? Timeout tuning? Schema contract?]
**Mapping**: PIVOT_LOG D-entry → Soul L3 principle → Corpus Map row

---

*Research complete. Deliverable written to disk. Awaiting Architect ruling on SQ-001–005.*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

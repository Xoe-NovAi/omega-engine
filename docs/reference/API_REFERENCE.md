# 🔱 Omega Engine — Consolidated API Reference
**AP Token**: `AP-API-REFERENCE-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Single consolidated API reference for all Omega Engine modules.
**Tags**: api, reference, consolidated, modules

---

## Module Index

### Core Engine Modules

| Module | File | Description |
|--------|------|-------------|
| **Oracle** | [oracle.md](oracle.md) | Unified routing, summoning, entity intelligence |
| **Model Gateway** | [model_gateway.md](model_gateway.md) | Provider fabric, local-first routing, circuit breakers |
| **Model Registry** | [model_registry.md](model_registry.md) | YAML model cards, provider configs, SQLite index |
| **Orchestration** | [orchestration.md](orchestration.md) | Sovereign Triage Router — deterministic model selection |
| **Monitoring** | [monitoring.md](monitoring.md) | Hardware telemetry (CPU, memory, thermal, zRAM) |
| **Hub** | [hub.md](hub.md) | Hardware stats bridge for Oracle degradation |
| **State** | [state.md](state.md) | USM (CAS + SQLite) + SomaticState serialization |
| **Memory Store** | [memory_store.md](memory_store.md) | FTS5 + vector hybrid memory |
| **Request Queue** | [request_queue.md](request_queue.md) | Offline research + cloud review delegation |

### Communication & Protocol

| Module | File | Description |
|--------|------|-------------|
| **MCP Core** | [mcp_core.md](mcp_core.md) | MCP 2026-07-28 Streamable HTTP client + compliance |
| **MCP Client** | [mcp_client.md](mcp_client.md) | MCP client utilities |
| **Bridge** | [bridge.md](bridge.md) | OpenCode WebSocket bridge to Oracle |
| **Iris** | [iris.md](iris.md) | Voice assistant — intent detection + entity routing |
| **Integrations** | [integrations.md](integrations.md) | Grok CLI fleet, quota pollers, fleet orchestrator |

### Intelligence & Research

| Module | File | Description |
|--------|------|-------------|
| **RAG** | [rag.md](rag.md) | Adaptive RAG — simple + iterative paths |
| **Research** | [research.md](research.md) | CLEAR scorecard, AMFO evaluator, DyTopo bridge |
| **Eval** | [eval.md](eval.md) | RAGAS + calibrated LLM-as-Judge (S2) |
| **Council** | [council.md](council.md) | MaKaLi Parallel Council governance |
| **Experiments** | [experiments.md](experiments.md) | Vision backend + perception primitives |
| **Training** | [training.md](training.md) | GRPO + reward modeling for alignment |

### Data & Storage

| Module | File | Description |
|--------|------|-------------|
| **CAS** | [cas.md](cas.md) | Content Addressable Storage (SHA-256) |
| **Search** | [search.md](search.md) | Sovereign Search Protocol persistence |
| **Ingestion** | [ingestion.md](ingestion.md) | Document ingestion pipeline |
| **Doc Reader** | [doc_reader.md](doc_reader.md) | Universal document reader (10+ formats) |
| **Library FTS** | [library_fts_search.md](library_fts_search.md) | FTS5 search interface |
| **Metrics DB** | [metrics_db.md](metrics_db.md) | Metrics persistence |
| **Vault Core** | [vault_core.md](vault_core.md) | Credential management |
| **Privacy Kernel** | [privacy_kernel.md](privacy_kernel.md) | PII shielding |

### Operations & CLI

| Module | File | Description |
|--------|------|-------------|
| **CLI** | [cli.md](cli.md) | Vault, bundle, fleet, oracle, soul, youtube, queue |
| **Workers** | [workers.md](workers.md) | Model updater, freshness checker, YouTube daemon |
| **Tools** | [tools.md](tools.md) | Security scanning, API key detection, Firecrawl/SearXNG direct |
| **Skills** | [skills.md](skills.md) | OpenCode skills (meditation pipeline, etc.) |
| **Infra** | [infra.md](infra.md) | SQLite policy + subagent pool |
| **Config Loader** | [config_loader.md](config_loader.md) | Configuration loading |

### Observability & Governance

| Module | File | Description |
|--------|------|-------------|
| **Observability** | [observability.md](observability.md) | Trace IDs, token ledger, event logging |
| **Session Lifecycle** | [session_lifecycle.md](session_lifecycle.md) | Session management |
| **Entity Registry** | [entity_registry.md](entity_registry.md) | Entity definitions |
| **Soul Loader** | [soul_loader.md](soul_loader.md) | Soul.yaml loading |
| **Selective Hydration** | [selective_hydration.md](selective_hydration.md) | Context packing |
| **M36 Recursive Probe** | [m36_recursive_probe.md](m36_recursive_probe.md) | Recursive verification |
| **Proxy Pool** | [proxy_pool.md](proxy_pool.md) | HTTP proxy management |
| **Context Builder** | [context_builder.md](context_builder.md) | Context assembly |

---

## Quick Start: Common Patterns

### Oracle Interaction
```python
from omega.oracle import Oracle

oracle = Oracle()
await oracle.bootstrap()

# Simple query
response = await oracle.talk("What is the Engine-Stack Firewall?")
print(response.text)

# Direct entity summon
response = await oracle.summon("Prometheus", "Harden container security")
print(f"[{response.entity}]: {response.text}")
```

### Model Routing
```python
from omega.orchestration import TriageRouter, TriageRequest, TaskRequest, EntityContext, Constraints, SessionContext
from pathlib import Path

router = TriageRouter(health_monitor=health, capability_matrix=cap_matrix)

request = TriageRequest(
    task=TaskRequest(description="Analyze security implications", complexity="deep"),
    entity=EntityContext(name="Prometheus", soul_path=Path("data/entities/prometheus/soul.yaml")),
    constraints=Constraints(max_latency_ms=5000, preferred_backends=["local"]),
    session=SessionContext(id="ses_123", trace_id="trace_456")
)

response = await router.select_model(request)
print(f"Selected: {response.selected_model.name} via {response.selected_model.provider}")
```

### Memory Operations
```python
from omega.memory_store import MemoryStore

memory = MemoryStore()

# Store
await memory.store("key1", {"content": "Important fact", "tags": ["security"]})

# Retrieve (hybrid FTS5 + vector)
results = await memory.search("security facts", limit=5)
```

### Background Workers
```python
from omega.workers import ModelUpdaterWorker
from omega.oracle import ModelGateway, ResourceGuard
from omega.observability import ObservabilityEngine

gateway = ModelGateway()
guard = ResourceGuard(max_ram_mb=4096)
obs = ObservabilityEngine()

worker = ModelUpdaterWorker(gateway, obs, config, guard)
await worker.run_update_cycle()  # Or worker.run_forever() for daemon
```

### Request Queue (Offline Research)
```python
from omega.request_queue import RequestQueue

queue = RequestQueue()
await queue.ensure_dirs()

# Queue research for later
req = await queue.create_queued_request(
    query="Compare zRAM vs zswap",
    priority="P1",
    created_by="architect"
)

# Process when online
for req in await queue.get_queued_requests():
    result = await execute_research(req)
    await queue.complete_request(req["id"], result)
```

---

## Mandate Compliance Matrix

| Module | M1 | M2 | M7 | M11 | M13 | M20 | M22 | M23 |
|--------|----|----|----|-----|-----|-----|-----|-----|
| oracle | ✅ | ✅ | ✅ | ✅ | ✅ | - | ✅ | ✅ |
| orchestration | ✅ | ✅ | ✅ | - | ✅ | - | - | ✅ |
| model_registry | ✅ | ✅ | ✅ | - | ✅ | - | - | ✅ |
| monitoring | ✅ | ✅ | ✅ | - | ✅ | - | - | ✅ |
| state | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | ✅ |
| rag | ✅ | ✅ | ✅ | - | ✅ | - | - | ✅ |
| research | ✅ | ✅ | ✅ | ✅ | ✅ | - | ✅ | ✅ |
| council | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | ✅ |
| mcp_core | ✅ | ✅ | ✅ | - | ✅ | - | ✅ | ✅ |
| workers | ✅ | ✅ | ✅ | - | ✅ | - | - | ✅ |
| request_queue | ✅ | ✅ | ✅ | - | ✅ | - | - | ✅ |

**Legend**: ✅ = Compliant, - = Not Applicable

---

## Heritage Tags Reference

Common heritage tags used across modules:

| Tag | Origin | Meaning |
|-----|--------|---------|
| `[id-soft: doom-1993]` | Doom (1993) | WAD system — engine/content separation |
| `[id-soft: quake-1996]` | Quake (1996) | Lazy deletion — efficient resource management |
| `[id-soft: quake3-1999]` | Quake III (1999) | Hard-boundary struct — memory safety |
| `[id-soft: vet-015]` | ZONEID | Hash as ultimate integrity marker |
| `[id-soft: vet-038]` | Surface Cache | Understand physical fetch path first |
| `[id-soft: vet-039]` | idHeap | Know memory topology before allocating |
| `[heritage: mcp 2024]` | MCP Protocol | Streamable HTTP + OAuth 2.1 PKCE |
| `[heritage: anyio 2024]` | AnyIO | Async runtime (M1) |
| `[heritage: tiny-critic-rag 2026]` | Tiny-Critic RAG | Near-zero-cost classifier |
| `[heritage: zetetic-2026]` | SQLCipher | Encrypted SQLite |

---

## Version & Compatibility

| Module | Version | Python | Dependencies |
|--------|---------|--------|--------------|
| Core | 1.0.0 | 3.11+ | anyio, httpx, pydantic |
| Monitoring | 1.0.0 | 3.11+ | psutil (optional) |
| State | 1.0.0 | 3.11+ | llama_cpp (optional, for SomaticState) |
| Research | 1.0.0 | 3.11+ | scikit-learn (for SVM router) |
| Training | 1.0.0 | 3.11+ | torch, transformers |
| MCP Core | 1.0.0 | 3.11+ | httpx, uuid |

---

## Navigation

- **By Category**: Use the Module Index above
- **By Mandate**: See Mandate Compliance Matrix
- **By Heritage**: See Heritage Tags Reference
- **Full Detail**: Click any module link for complete API documentation

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ API_REFERENCE-v1.0.0 ⬡ 2026-10-02 ⬡*
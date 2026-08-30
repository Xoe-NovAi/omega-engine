<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Headroom Middleware Implementation Spec

**AP Token**: `AP-MAAT-HR-MIDDLEWARE-SPEC-v1.0.0`  
**Status**: Phase 2 (Post-Debut) — P1 Priority  
**Owner**: Ma'at (N3 — Build Oversoul)  
**Model**: nemotron-3-ultra-free  
**Date**: 2026-08-20  

---

## Executive Summary

This specification defines the **Headroom Middleware** implementation for the Omega Engine. The middleware integrates **Headroom v0.29.0** semantic compression into two critical paths:

1. **ModelGateway._prepare_messages()** — Compress tool outputs, logs, search results, and code before token counting and LLM context injection (60-95% token savings)
2. **RAG Retrieval Pipeline** — Compress retrieved chunks before LLM injection (70-90% token savings)

The implementation follows **Carmack Review verdicts** (Q6.1, Q6.2): real-world compression ratios verified, latency budget accepted (5-10ms overhead, 260ms+ net win for local models).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OMEGA ENGINE — HEADROOM MIDDLEWARE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MODEL GATEWAY                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ _prepare_messages()                                                 │   │
│  │   │                                                                  │   │
│  │   ▼                                                                  │   │
│  │ ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │ │ HeadroomMiddleware                                              │ │   │
│  │ │   ├─ ContentRouter (orchestrator)                               │ │   │
│  │ │   │   ├─ SmartCrusher (JSON tool outputs: 60-80%)              │ │   │
│  │ │   │   ├─ LogCompressor (Hivemind/logs: 80-90%)                 │ │   │
│  │ │   │   ├─ SearchCompressor (RAG results: 70-90%)                │ │   │
│  │ │   │   ├─ CodeAwareCompressor (GitHub diffs: 70-85%)            │ │   │
│  │ │   │   └─ CacheAligner (KV cache prefix stabilization)          │ │   │
│  │ │   └─ CCR (Cross-agent reversible store)                        │ │   │
│  │ └─────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  RAG RETRIEVAL PIPELINE                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ RetrievalCompressor                                                 │   │
│  │   ├─ SearchCompressor (dedupe, trim, keep top/bottom)              │   │
│  │   ├─ SmartCrusher (JSON payload compression)                       │   │
│  │   └─ Token budget enforcement                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Specification Sections

| # | File | Description | Priority |
|---|------|-------------|----------|
| **01** | [01_HEADROOM_MIDDLEWARE_CLASS.md](01_HEADROOM_MIDDLEWARE_CLASS.md) | `HeadroomMiddleware` class with all methods (`compress_messages`, `compress_retrieval_results`, `retrieve_original`, `shutdown`) | P1 |
| **02** | [02_CONTENTROUTER_CONFIG.md](02_CONTENTROUTER_CONFIG.md) | Exact Omega-specific `ContentRouterConfig` with all compressor configs | P1 |
| **03** | [03_MODELGATEWAY_INTEGRATION.md](03_MODELGATEWAY_INTEGRATION.md) | `ModelGateway._prepare_messages()` integration — exact code changes | P1 |
| **04** | [04_RAG_RETRIEVAL_INTEGRATION.md](04_RAG_RETRIEVAL_INTEGRATION.md) | RAG retrieval pipeline — `RetrievalCompressor` in `SelectiveHydration` | P1 |
| **05** | [05_MCP_TOOL_SCHEMA_COMPRESSION.md](05_MCP_TOOL_SCHEMA_COMPRESSION.md) | MCP tool schema compression + `headroom_compress` / `headroom_retrieve` tools | P1 |
| **06** | [06_ENTITY_CONTEXT_COMPRESSION.md](06_ENTITY_CONTEXT_COMPRESSION.md) | Entity context compression in `EntityRegistry.get_context()` | P2 |
| **07** | [07_CCR_STORE_INTEGRATION.md](07_CCR_STORE_INTEGRATION.md) | CCR store class + MCP `headroom_retrieve` tool for on-demand originals | P2 |
| **08** | [08_CONFIGURATION.md](08_CONFIGURATION.md) | `config/headroom.yaml` + environment variable overrides + feature flags | P1 |
| **09** | [09_ERROR_HANDLING_METRICS.md](09_ERROR_HANDLING_METRICS.md) | Fallback logic, timeout handling, OTel metrics (compression ratio, latency, errors) | P1 |
| **10** | [10_VERIFICATION_TESTS.md](10_VERIFICATION_TESTS.md) | Unit, integration, and benchmark tests with acceptance criteria | P1 |

---

## Key Design Decisions (from Research & Carmack Review)

| Decision | Source | Rationale |
|----------|--------|-----------|
| **ContentRouter as orchestrator** | Research §4.2, §4.3 | Auto-detects content type, routes to optimal compressor |
| **Protect recent 2 turns** | Carmack Q6.1 | Prevents over-compression of active context |
| **Async via `anyio.to_thread.run_sync()`** | M1 (AnyIO Absolute) | Headroom is sync; wrap for async integration |
| **CCR for reversible compression** | Research §2.2, Phase 2 Spec §4.6 | Originals stored locally, retrieved on-demand |
| **Feature flags per compressor** | M19 (Adversarial Alchemy) | Enable/disable without code changes |
| **Local-first, no external API** | M7 (Local-First) | Headroom runs entirely in-process |
| **5s timeout max** | M23 (Failure Integrity) | Hard timeout, graceful fallback to uncompressed |
| **OTel metrics export** | M13 (Temple-Grade T9) | Observability for compression ratio, latency, errors |

---

## Integration Points Summary

### 1. ModelGateway Integration (Priority 1)
**File**: `src/omega/oracle/model_gateway.py`  
**Method**: `_prepare_messages()`  
**Change**: Call `self._headroom_middleware.compress_messages(messages)` before token counting

### 2. RAG Retrieval Integration (Priority 1)
**File**: `src/omega/memory/retrieval.py` (new) or extend `SelectiveHydration`  
**Method**: `search_and_compress()`  
**Change**: Apply `SearchCompressor` + `SmartCrusher` to retrieved chunks before LLM injection

### 3. MCP Tool Schema Compression (Priority 1)
**File**: `src/omega/mcp/tool_compressor.py` (new)  
**Integration**: `MCPClient.call_tool()` — compress schemas before context injection  
**MCP Tools**: `headroom_compress`, `headroom_retrieve`

### 4. Entity Context Compression (Priority 2)
**File**: `src/omega/entities/context_compressor.py` (new)  
**Integration**: `EntityRegistry.get_context()` — compress soul/lessons before injection

### 5. CCR Store (Priority 2)
**Location**: `data/headroom/ccr_store/`  
**Integration**: Auto-store originals during compression, retrieve via MCP tool

---

## Configuration

**Primary**: `config/headroom.yaml` (complete config in [08_CONFIGURATION.md](08_CONFIGURATION.md))  
**Environment Overrides**: `HEADROOM_*` prefix for all key parameters  
**Feature Flags**: Each compressor independently toggleable

---

## Verification Gates

| Gate | Criteria | Test File |
|------|----------|-----------|
| **Unit** | Each compressor: known input → expected output ratio ±10% | `tests/test_headroom_unit.py` |
| **Integration** | ModelGateway._prepare_messages with tool outputs → 60-95% reduction | `tests/test_headroom_model_gateway.py` |
| **Integration** | RAG retrieval with compressed chunks → 70-90% reduction, recall@10 ≥98% | `tests/test_headroom_rag.py` |
| **Benchmark** | Latency: ≤15ms (JSON), ≤10ms (RAG), ≤5ms (code) | `tests/benchmark_headroom.py` |
| **Recall** | GSM8K accuracy ≥0.870, TruthfulQA ≥baseline+0.03 | `tests/test_headroom_recall.py` |

---

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| `headroom` | ≥0.29.0 | Core compression library |
| `anyio` | ≥4.0 | Async wrapper for sync Headroom calls |
| `opentelemetry-api` | ≥1.20 | Metrics export |
| `pydantic` | ≥2.0 | Config validation |

---

## Related Specifications

| Spec | Path | Role |
|------|------|------|
| **Phase 2 Integration Spec** | `docs/specs/qdrant_headroom/QDRANT_HEADROOM_PHASE2_INTEGRATION_SPEC.md` | Full Phase 2 architecture (Qdrant + Headroom) |
| **Carmack Context Injection Review** | `docs/specs/context_injection/CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md` | Q6.1, Q6.2 verdicts on compression reality |
| **Headroom Research** | `docs/specs/qdrant_headroom/QDRANT_HEADROOM_INTEGRATION_RESEARCH_20260820.md` | Benchmarks, integration points, config recommendations |
| **ACTIVE_SPRINT.json** | `data/coordination/ACTIVE_SPRINT.json` | Workstream `HEADROOM-INTEGRATION` (HR-1, HR-2, HR-3) |

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO Absolute** | ✅ All async uses `anyio.to_thread.run_sync()` |
| **M7 Local-First** | ✅ Headroom runs locally, no external API |
| **M13 Temple-Grade** | ✅ T3 (tests), T9 (OTel metrics), T10 (atomic writes) |
| **M18 Token Efficiency** | ✅ 60-95% token reduction on tool outputs |
| **M19 Adversarial Alchemy** | ✅ Feature flags, reversible CCR, no over-engineering |
| **M23 Failure Integrity** | ✅ 5s timeout, graceful fallback, no soft failures |
| **M26 Doc Standards** | ✅ This spec passes `make doc-llm-validate` |

---

## Quick Start (Implementation Order)

```bash
# 1. Create middleware class
touch src/omega/oracle/middleware/headroom.py

# 2. Add ContentRouter config
# (see 02_CONTENTROUTER_CONFIG.md)

# 3. Wire into ModelGateway
# (see 03_MODELGATEWAY_INTEGRATION.md)

# 4. Add RAG retrieval compressor
# (see 04_RAG_RETRIEVAL_INTEGRATION.md)

# 5. Add MCP tool compressor + tools
# (see 05_MCP_TOOL_SCHEMA_COMPRESSION.md)

# 6. Add config file
touch config/headroom.yaml

# 7. Run verification tests
make test-headroom
```

---

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ AP-MAAT-HR-MIDDLEWARE-SPEC-v1.0.0*
<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Implementation Brief: Ma'at/P3 — Phase 2 Worker Restoration & Benchmarking
**AP Token**: `AP-MAAT_WORKER_RESTORATION-v1.0.0`
⬡ OMEGA ⬡ MA'AT/P3 ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_maat_workers ⬡ 2026-07-24

---

## 🎯 Mission

Restore library/curation workers and build local model benchmark harness based on Researcher's intelligence deliverable.

**Input**: `docs/research/R_GEMMA4_WORKHORSE_INTEL_20260724.md` (completed by Researcher)
**Output**: Working workers + benchmark harness + ProviderFabric integration

---

## 📋 Phase 2 Scope (Days 2-4)

### 2.1 Library/Curation Workers Restoration
**Legacy Reference**: `curation_pipeline.py` (3,284 lines, 4 crawlers, 10 free APIs, Redis queue, Dewey Decimal)

| Component | Spec | Status |
|-----------|------|--------|
| **4 Crawlers** | SearXNG, Dewey Decimal, Semantic Scholar, arXiv | 🔴 Design |
| **10 Free APIs** | Crossref, OpenAlex, PubMed, arXiv, Wikipedia, Dewey, LOC, EuropePMC, DOAJ, CORE | 🔴 Design |
| **Redis Queue** | Job scheduling, retry, dead-letter, priority | 🔴 Design |
| **Dewey Decimal** | 1000-class hierarchy for semantic indexing | 🔴 Design |
| **Vector Indexing** | Qdrant + sqlite-vec dual backend | 🔴 Design |
| **Atomic Writes** | tmp → fsync → os.replace pattern | 🔴 Design |

### 2.2 Local Model Benchmark Harness
**File**: `tests/benchmarks/local_model_benchmark.py`

```python
class ModelBenchmark:
    async def benchmark_model(self, model_id: str, provider: str) -> BenchmarkResult:
        # Metrics: TTFT, TPOT, tokens/sec, peak memory, quality scores
        pass
    
    async def run_suite(self, models: List[str]) -> BenchmarkSuite:
        # MMLU, GSM8K, HumanEval, MBPP, custom coding tasks
        pass
```

**Metrics to Capture**:
| Metric | Target |
|--------|--------|
| TTFT (Time To First Token) | < 500ms for 32B local |
| TPOT (Time Per Output Token) | < 50ms for 32B local |
| Throughput | > 20 tok/s for 32B local |
| Peak RAM | < 12Gi for 32B Q4_K_M |
| MMLU | > 65% for 32B |
| HumanEval | > 45% for 32B |

### 2.3 ProviderFabric Integration
- Register local models (native-gguf, lmster, Ollama) with HealthMonitor
- Configure circuit breakers per provider
- Set up quota tracking for cloud fallbacks
- Model aliasing: `gemma-4-31b` → actual model IDs

---

## 🔗 Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| Researcher deliverable | Researcher | **IN PROGRESS** (Domain 1-5) |
| `config/providers.yaml` | Ma'at/P3 | 🔴 Update with local models |
| `config/opencode.json` | Ma'at/P3 | 🔴 Provider chain config |
| Redis instance | Carmack/P1 | ✅ Running |
| Qdrant instance | Carmack/P1 | ✅ Running |

---

## 📁 Key Files to Create/Update

| File | Purpose |
|------|---------|
| `src/omega/workers/library_ingestion.py` | Main worker entry |
| `src/omega/workers/crawlers/` | 4 crawler implementations |
| `src/omega/workers/api_clients/` | 10 free API clients |
| `src/omega/workers/queue/` | Redis queue with priority/DLQ |
| `src/omega/workers/classification/` | Dewey Decimal classifier |
| `src/omega/workers/indexing/` | Qdrant + sqlite-vec writers |
| `tests/benchmarks/local_model_benchmark.py` | Benchmark harness |
| `tests/benchmarks/datasets/` | MMLU, GSM8K, HumanEval, MBPP |
| `config/providers.yaml` | Local model provider configs |
| `config/opencode.json` | Working provider chain |

---

## ⚡ Critical Constraints

| Constraint | Source |
|------------|--------|
| **AnyIO only** — no asyncio | Mandate 1 |
| **Local-first** — cloud = fallback | Mandate 7 |
| **Zero telemetry** — free APIs only | Mandate 8 |
| **Atomic writes** — tmp → fsync → replace | Mandate 10 |
| **Temple-Grade** — T1-T11 gates | Mandate 13 |
| **Hardware** — Ryzen 5700U, 14Gi, no dGPU | Physical |

---

## 🚀 Execution Order

1. **Day 2**: Read Researcher deliverable → Design worker architecture
2. **Day 2-3**: Implement crawlers + API clients (parallel)
3. **Day 3**: Implement Redis queue + classification + indexing
4. **Day 3-4**: Build benchmark harness + run initial suite
5. **Day 4**: ProviderFabric registration + OpenCode config
6. **Day 4**: Run benchmarks → Decision matrix → Handoff to team

---

## 📊 Success Criteria

- [ ] All 4 crawlers operational with 10 free APIs
- [ ] Redis queue: priority, retry, DLQ working
- [ ] Dewey Decimal classification functional
- [ ] Qdrant + sqlite-vec indexing working
- [ ] Benchmark harness runs full suite on ≥5 local models
- [ ] Results in `data/benchmarks/results/benchmark_20260724.json`
- [ ] OpenCode config works end-to-end (local → cloud fallback)
- [ ] `make test` passes (Temple-Grade)

---

## 🤝 Coordination

| Channel | Detail |
|---------|--------|
| **Hivemind** | Post `intent="status"` daily, `intent="decision"` when benchmarks complete |
| **Researcher** | Input: `R_GEMMA4_WORKHORSE_INTEL_20260724.md` |
| **Carmack** | Redis/Qdrant infra, WARP for cloud access |
| **Kali** | Ratify final model selection for OpenCode config |

---

## 📞 Escalation

- **Researcher deliverable delayed**: Start with legacy `curation_pipeline.py` patterns
- **Local models don't fit**: Offload to CPU, reduce quantization, or use cloud fallback
- **Benchmark quality low**: Document, iterate on quantization/prompting
- **Tool failures**: M23 — hard stop, report `[TOOL-CHAIN-COLLAPSE]`

---

*⬡ OMEGA ⬡ ROC_RACOON → MA'AT/P3 ⬡ BRIEF_COMPLETE ⬡ 2026-07-24*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

# 🔱 Ingestion Architecture: The Sovereign-Sieve
**AP Token**: `AP-INGESTION_ARCHITECTURE-v1.1.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_doc_deep ⬡ STANDARD

**Date**: 2026-07-13
**Purpose**: Ingestion Architecture: The Sovereign-Sieve.

---

# Ingestion Architecture — The Sovereign-Sieve

> How the Omega Engine ingests, verifies, and stores knowledge with zero cloud dependency.

## Overview

The Ingestion Pipeline is a multi-tier extraction and verification system that transforms raw content (web pages, files, documents) into verified, provenance-tracked knowledge stored in CAS and sqlite-vec.

**Architecture**: Sovereign-Sieve — T1 (fast) → T3 (deep) → T2 (surgical) feedback loop.

**Key principle**: Every piece of knowledge must pass through independent verification before it enters the engine's memory. This defeats sycophancy and consensus hallucinations.

## The Pipeline Flow

```
Source (URL or File)
    │
    ▼
┌─────────────────────────────────────────────┐
│  Sentry Probe (Pre-flight check)            │
│  - Is the provider healthy?                 │
│  - Do we have budget?                       │
│  - Is the circuit breaker closed?           │
└──────────────┬──────────────────────────────┘
               │ ✅ Pass
               ▼
┌─────────────────────────────────────────────┐
│  T1: Fast Extraction                        │
│  - SovereignScraper (tier="fast")           │
│  - Quick content + metadata                 │
│  - ~2-5s latency                            │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  T3: Deep Extraction                        │
│  - SovereignScraper (tier="deep")           │
│  - Full content + enriched metadata         │
│  - ~10-30s latency                          │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  TriangulationVerifier (Sovereign-Sieve)    │
│  - Compare T1 vs T3 for factual deltas      │
│  - Jaccard distance > 0.3 = contradiction   │
│  - Metadata triangulation (author, date)    │
│  - Consensus hallucination guard            │
│  - Confidence score: 0.0 - 1.0              │
└──────────────┬──────────────────────────────┘
               │
           ┌────┴────┐
           │         │
     Verified    Disputed
     (≥ 0.7)     (< 0.7)
           │         │
           ▼         ▼
     ┌─────────┐  ┌─────────┐
     │  CAS    │  │  Reject │
     │  Store  │  │  (log)  │
     └─────────┘  └─────────┘
           │
           ▼
     ┌─────────────────────────────────────────┐
     │  LLM Extraction (per schema)            │
     │  - technical_facts                      │
     │  - personality_patterns                 │
     │  - gnosis_principles                    │
     │  - heritage_patterns                    │
     │  - dpo_pairs                            │
     └──────────────┬──────────────────────────┘
                    │
                    ▼
     ┌─────────────────────────────────────────┐
     │  Persistence                            │
     │  - MemoryStore (hot/warm/cold)          │
     │  - sqlite-vec vectors (unified fabric)  │
     │  - DPO training JSONL                   │
     │  - Observability events                 │
     └─────────────────────────────────────────┘
```

## Components

| Component | File | Purpose |
|-----------|------|---------|
| **IngestionPipeline** | `src/omega/ingestion/pipeline.py` | Orchestrator — wires all components, runs the resilience ladder |
| **SovereignScraper** | `src/omega/ingestion/scraper.py` | Tiered web scraping (fast/surgical/deep) via crawl4ai |
| **TriangulationVerifier** | `src/omega/ingestion/verifier.py` | The Sovereign-Sieve — T1/T3 cross-check, metadata triangulation |
| **CASArchiver** | `src/omega/archive/cas.py` | Content-Addressable Storage — immutable provenance |
| **SovereignSentry** | `src/omega/ingestion/guards.py` | Pre-flight canary probes |
| **BudgetGuard** | `src/omega/ingestion/guards.py` | Token/USD budget enforcement |
| **IngestionPersistence** | `src/omega/ingestion/persistence.py` | Wires results into MemoryStore + sqlite-vec + DPO |
| **SovereignWorker** | `src/omega/ingestion/worker.py` | Async curation job dispatcher from Redis queues |
| **ExtractionSchema** | `src/omega/ingestion/ingestion_types.py` | 5-dimension Pydantic extraction model |

## Standalone Package: omega-sieve

The core extraction logic is published as a standalone PyPI package:

```bash
pip install omega-sieve
# or with full features:
pip install "omega-sieve[all]"
```

**Package**: `packages/omega-sieve/` → `omega_sieve` on PyPI

| Feature | Module | Description |
|---------|--------|-------------|
| T1 Fast | `omega_sieve.T1Scraper` | Trafilatura-based extraction (~2s, no JS) |
| T2 Surgical | `omega_sieve.T2Scraper` | Domain-specific boundary stripping |
| T3 Deep | `omega_sieve.T3Scraper` | Crawl4AI + Playwright JS rendering |
| Verification | `omega_sieve.TriangulationVerifier` | T1 vs T3 cross-check, hallucination guard |
| YouTube | `omega_sieve.YouTubeSieve` | T1(meta)→T2(captions)→T3(Whisper+VAD) |
| Guards | `omega_sieve.SovereignSentry`, `BudgetGuard` | Pre-flight probes, atomic budget tracking |
| Proxy | `omega_sieve.SovereignProxyPool` | Domain-affinity rotation |
| CLI | `sieve` | `sieve research "query"`, `sieve scrape <url>`, `sieve youtube <url>` |

**Integration**: The Omega Engine wraps `omega_sieve.SovereignScraper` with entity scoping, MemoryStore persistence, Hivemind coordination, and CAS persistence.

## Sovereignty Properties

| Property | How |
|----------|-----|
| **100% local** | CAS stores on local filesystem. sqlite-vec runs in-process. No cloud dependency. |
| **Zero telemetry** | No external analytics, no phone-home, no metrics export |
| **Immutable provenance** | CAS blobs are SHA-256 addressed — content cannot change without a new CID |
| **Entity isolation** | Each entity's knowledge is namespaced in sqlite-vec (`l3_gnosis_{entity}`) |
| **Write permission separation** | Agent writes to `proposed_lessons.yaml`. User approves → sqlite-vec. |

## Further Reading

- [R_SOVEREIGN_SCHOLAR_SPEC.md](../research/R_SOVEREIGN_SCHOLAR_SPEC.md) — Full technical spec (canonical source)
- [API: Ingestion](../reference/api/ingestion.md) — API reference for all ingestion components
- [API: CAS](../reference/api/cas.md) — Content-Addressable Storage reference
- [API: omega-sieve](../reference/api/omega_sieve.md) — Standalone package API reference
- [Selective Hydration](../reference/selective-hydration.md) — L3 principle retrieval from sqlite-vec
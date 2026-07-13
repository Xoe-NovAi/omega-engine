# 🔱 Observability Vet Report — Omega Engine
**Entity**: Pillar P8 (Hecate)
**Oversoul**: Lilith
**Date**: 2026-07-12
**Status**: FINAL
**Target**: "Definitive Local AI Tool"

---

## 1. Current State Assessment

### 🟢 What's Working
- **Unified Forensic Ledger (UFL)**: The `MetricsDB` (SQLite WAL-mode) provides a robust, non-blocking record of system events, errors, and performance.
- **Standardization**: Full implementation of **OpenTelemetry GenAI Semantic Conventions** via `OTelSQLiteExporter`, ensuring the engine speaks the industry standard for AI tracing.
- **Provenance (M22)**: Accurate capture of `provider_name`, `model_used`, and `is_cloud` flags, enabling the **Sovereignty Ratio** calculation.
- **Context Propagation**: `contextvars`-based `trace_id` propagation ensures that requests can be tracked across async boundaries without explicit argument passing.
- **Regression Detection**: Implementation of the **3-sigma rule** for baseline metrics allows the engine to detect performance drift automatically.

### 🔴 What's Broken / Missing / Suboptimal
- **Lack of Hardware Correlation**: Hardware stats (CPU, RAM, Thermal) are available via `omega-hub` but are **transient**. They are not persisted in `MetricsDB`, making it impossible to correlate a latency spike with a thermal throttling event.
- **Forensic vs. Active Observability**: The system is currently a "black box" that can be audited *after* a failure. There is no real-time visibility or alerting for the user.
- **Tracing Blindness**: While spans and `trace_id` exist, there is no tool to visualize the call graph. The user cannot "see" the sequence of reasoning steps.
- **Semantic Gap**: Error logs are stored as text. Finding "all errors related to Podman volume issues" requires regex/grep rather than semantic search.

---

## 2. Gap Analysis for "Definitive Local AI Tool"

To transition from a "functional engine" to the "definitive local AI tool," the observability stack must move from **post-mortem forensics** to **active system intelligence**.

| Dimension | Current State (Forensic) | Target State (Active) | Delta |
|-----------|---------------------------|-------------------------|-------|
| **Visibility** | SQLite Query / Grep | Real-time Dashboard | Redis Stream $\rightarrow$ UI |
| **Correlation** | Latency $\rightarrow$ Provider | Latency $\rightarrow$ Hardware $\rightarrow$ Model | Resource-aware Profiling |
| **Search** | Keyword / Regex | Semantic / Vector Search | Qdrant Log Indexing |
| **Analysis** | Manual Audit | Automated Root Cause (RCA) | Pattern-based Anomaly Detection |
| **Tracing** | Flat Log of Spans | Interactive Call Graph | Trace Visualization Tool |

**The "Sovereign Insight" Goal**: A user should be able to ask: *"Why was my last response slow?"* and the engine should answer: *"Inference latency increased by 400ms because CPU Core 4 throttled to 1.2GHz due to thermal limits (88°C) during the GGUF decode phase."*

---

## 3. System Utilization Audit

### 💾 SQLite (MetricsDB)
- **Usage**: Primary store for events, errors, and performance.
- **Verdict**: **OPTIMAL** for long-term forensic storage.
- **Underutilized**: Complex relational queries for long-term trend analysis (e.g., "how has my local-first ratio evolved over 6 months?").

### ⚡ Redis
- **Usage**: Session and cache management.
- **Verdict**: **UNDERUTILIZED** for observability.
- **Opportunity**: Use Redis **Streams** or **Pub/Sub** to broadcast real-time metrics (tokens/sec, CPU %) to a frontend dashboard without polling SQLite.

### 🔍 Qdrant
- **Usage**: Entity memory and knowledge base.
- **Verdict**: **UNUSED** for observability.
- **Opportunity**: Implement **Semantic Logging**. Index the `payload` of `events` and `error_message` of `errors` in a dedicated observability collection. This allows the engine to find "similar failures" across different sessions.

### 🐘 PostgreSQL
- **Usage**: General persistence.
- **Verdict**: **UNUSED** for observability.
- **Opportunity**: Migrate high-volume telemetry to Postgres if SQLite WAL contention becomes a bottleneck during heavy parallel agent work.

---

## 4. Deep Research Requirements

To implement the target state, the following research is required:
1. **Hardware-Inference Correlation Patterns**: Study how `llama.cpp` and `native-gguf` interact with Zen 2 architecture to define "normal" vs "throttled" signatures.
2. **Vector-Based Log Analysis**: Research "Log2Vec" or similar patterns for indexing system logs in Qdrant to enable semantic RCA.
3. **Local-First Tracing UIs**: Evaluate lightweight, self-hosted trace visualizers (e.g., Jaeger-lite or custom Mermaid.js generators) that don't require heavy infrastructure.
4. **2026 LLM Metrics**: Define "Sovereign Metrics" beyond TTFT—e.g., **Energy-per-Token** or **Sovereignty-Efficiency Score**.

---

## 5. Concrete Recommendations

### 🔴 P0: Blocking (Must fix before launch)
- **Resource-Metric Integration**: Modify `observability.py` to sample `omega-hub_get_hardware_stats` and record them into a new `system_resources` table in `MetricsDB` during every inference span.
- **Hard-Stop on Tool-Chain Collapse**: Ensure that if the `MetricsDB` is unwritable, the engine reports `[TOOL-CHAIN-COLLAPSE]` (M23) rather than silently failing.

### 🟡 P1: Critical (Sprint 1)
- **Real-time Metrics Stream**: Implement a Redis-based broadcaster for current inference stats (Tokens/sec, Current Model, CPU Temp) to enable a "Live Feed" dashboard.
- **Sovereignty-Aware Alerting**: Trigger a warning if the `ratio_local` drops below a user-defined threshold (e.g., 80%) over a 24-hour window.

### 🟢 P2: Important (Sprint 2)
- **Semantic Error Index**: Create a Qdrant collection for `observability_logs`. Automatically index every `OmegaError` to enable "Similar Issue" lookups.
- **Basic Trace Visualizer**: Implement a CLI command `omega trace <trace_id>` that outputs a Mermaid.js sequence diagram of the OTel spans.

### 🔵 P3: Enhancement (Nice to have)
- **Automated RCA**: Implement a "Skeptical Verifier" for logs that suggests a root cause for failures by correlating `errors` $\rightarrow$ `breaker_transitions` $\rightarrow$ `system_resources`.
- **Energy Profiling**: Track estimated Watt-hours per inference to provide a "Green AI" metric for local users.

---
**Verdict**: The current observability stack is a high-quality **Forensic Ledger**. To become a **Sovereign Intelligence Tool**, it must evolve into a **Real-time Correlative System**.

*⬡ OMEGA ⬡ HECATE ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_6286dd0eed6a ⬡ VETTING*

# 🔱 Omega Engine — The Sovereign Observatory Architecture
# ⬡ OMEGA ⬡ JEM ⬡ hivemind ⬡ ARCHITECTURE ⬡ OBSERVATORY

**Date**: 2026-07-07
**Status**: ACTIVE
**Mandates Enforced**: M1 (AnyIO Absolute), M8 (Zero Telemetry), M9 (Error Integrity)

---

## 1. The Sovereign Observatory Concept

The **Sovereign Observatory** is the Omega Engine's native, zero-telemetry observability stack. It replaces heavy, cloud-oriented infrastructure (Prometheus, Grafana, Jaeger) with a lightweight, local-first architecture designed specifically for the constraints of a local machine (e.g., Ryzen 5700U with 12Gi RAM).

**Core Philosophy**:
> *"A system is only as observable as its weakest dashboard. Observability without visualization is just disk wear."*

The Observatory provides forensic-grade visibility into agent health, token burn, and system stability without sending a single byte of data over the network.

---

## 2. Architectural Layers

The Observatory is built on a strict 3-layer architecture to prevent read/write contention and UI freezing:

1. **The Data Layer (Sovereign TSDB)**
   - **Metrics & Tokens**: SQLite database (`metrics.db`) running in **WAL (Write-Ahead Logging) mode**.
   - **Traces & Crashes**: Append-only JSONL files (`traces.jsonl`, `crashes/*.json`).
2. **The Facade Layer (The Reader)**
   - `src/omega/observability/observability_reader.py`
   - A unified, asynchronous, read-only interface to all observability data.
3. **The Presentation Layer (TUI & SSE)**
   - `make fleet-status`: A high-density terminal UI built with `Textual`.
   - `Hub SSE`: Server-Sent Events pushed from the MCP Hub for real-time agent awareness.

---

## 3. The Reader Protocol (`observability_reader.py`)

The `SovereignReader` class is the single source of truth for querying engine health. It enforces two critical architectural safeguards:

### 3.1 The SQLite Concurrency Trap (Read-Only Mode)
While SQLite WAL mode allows concurrent readers and writers, it strictly enforces **only one concurrent writer**. If the TUI attempts to acquire a write lock while the Hub is flushing metrics, the database will lock (`sqlite3.OperationalError`).

**The Fix**: The `SovereignReader` connects to SQLite using URI parameters to enforce a strict read-only mode:
```python
sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
```
This guarantees the dashboard can never block the core engine's telemetry writers.

### 3.2 AnyIO Thread Offloading (M1 Compliance)
Textual (the TUI framework) and the MCP Hub both run on asynchronous event loops. Executing synchronous disk I/O (SQLite queries or file reads) directly on the event loop will cause UI stuttering and dropped SSE frames.

**The Fix**: Every method in `SovereignReader` is split into a synchronous internal method (`_sync_get_metric_series`) and an asynchronous public method that offloads the work to a thread pool:
```python
async def get_metric_series(self, ...):
    return await anyio.to_thread.run_sync(self._sync_get_metric_series, ...)
```

---

## 4. Key Observability Metrics

### 4.1 Cognitive Velocity & Acceleration
Traditional systems track "Requests per Second." AI agents require tracking **"Tokens per Second."** 

The `SovereignReader` calculates **Cognitive Velocity** (tokens/sec) and **Token Acceleration** ($\Delta$ tokens/sec²). 
- **Why?** In LLM agent systems, a sudden, sustained spike in token acceleration almost always indicates an **"Agent Loop"** (e.g., an agent failing a tool call and retrying infinitely). 
- **Action**: The TUI monitors acceleration to flag runaway agents before they exhaust the context window or API budget.

### 4.2 O(1) Reverse Tailing for JSONL
The engine generates massive trace logs (`ufl`). Loading a 5GB `.jsonl` file into memory to read the last 50 lines would cause an OOM crash.

The `tail_live_traces` method implements a **Hybrid Backward Scanned FIFO**:
1. Opens the file in binary mode (`rb`).
2. Seeks to `EOF`.
3. Reads backwards in 8KB chunks, splitting by `\n`.
4. Parses the JSON incrementally until `max_lines` is reached.

This provides `tail -f` performance with $O(1)$ memory complexity, regardless of file size.

---

## 5. Deployment & Usage

To instantiate the reader in any Omega Engine component:

```python
from pathlib import Path
from omega.observability.observability_reader import SovereignReader

reader = SovereignReader(
    db_path=Path("data/observability/metrics.db"),
    trace_dir=Path("data/traces"),
    crash_dir=Path("data/crashes")
)

# Fetch health without blocking the event loop
health = await reader.get_fleet_health()
print(f"Global Error Rate: {health.global_error_rate}")
```

*Document maintained by Jem (Sovereign Synthesizer). Tasked by Roc Racoon.*
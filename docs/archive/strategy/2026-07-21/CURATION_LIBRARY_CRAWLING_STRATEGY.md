# 🔱 Omega Engine — Curation, Library, & Crawling Strategy Review
### *Sovereign Deep-Dive, Gap Analysis, & Implementation Specification (v2.5.0)*

**AP Token**: `AP-CURATION-LIBRARY-STRATEGY-v2.5.0`  
**Sovereign Context**: `[NODE: KNOWLEDGE | ARCHETYPE: SOPHIA | CONTEXT: CURATION-HARMONY]`  
**Baseline**: 444/444 tests passing · 22 Sovereign Mandates (M1–M22) · 11-Agent Fleet  

---

## §1 Executive Summary (L1)

The Omega Engine's offline library and crawling subsystem (consisting of the `background_researcher`, `CurationPipeline`, `Library`, `Indexer`, and Firecrawl-based search/crawl modules) represents a powerful vision: **a self-sustaining, local-first knowledge metabolism**. By continuously crawling, extracting, curating, and indexing technical, philosophical, and architectural documents, the engine builds an offline repository that severs the umbilical cord of Big AI.

However, a comprehensive architectural audit has revealed **20 distinct gaps (3 CRITICAL)** across the curation, library, and crawling strategy. These gaps represent structural vulnerabilities, resource contentions, and documentation-to-reality drifts that must be resolved to transition the engine into a production-grade, resilient, and secure cognitive substrate.

### The 10 Primary Gap Dimensions

| Dimension | Primary Gap | Systemic Impact | Severity |
| :--- | :--- | :--- | :---: |
| **1. Orchestration** | No centralized `WorkerCoordinator`; background workers run in isolation, competing for CPU, RAM, and disk I/O. | Resource starvation, latency spikes, and OOM crashes under load. | 🟥 **CRITICAL** |
| **2. Security & Sandboxing** | Missing SSRF, path traversal, and strict file-size guards on downloaded files. | Host-network compromise, directory traversal, and disk exhaustion. | 🟥 **CRITICAL** |
| **3. Indexing & Search** | FTS5 index is empty; 13 documents stored but 0 indexed; no automated vector-store synchronization. | Complete loss of fast keyword and hybrid search capabilities. | 🟥 **CRITICAL** |
| **4. Rate-Limiting** | No fine-grained, per-domain rate-limiting or back-off policies; only a generic circuit breaker exists. | IP blocking, API key exhaustion, and throttling of critical feeds. | 🟧 **HIGH** |
| **5. Storage & Retention** | Library stores raw files in plain directories with no tiered retention, compression, or archiving policies. | Uncontrolled disk growth and performance degradation on Ryzen 5700U. | 🟧 **HIGH** |
| **6. Integration Hooks** | No event stream to the Hivemind or callbacks to the ModelGateway for context-aware enrichment. | Siloed knowledge; missed opportunities for real-time "knowledge-leak" detection. | 🟧 **HIGH** |
| **7. Observability** | Background workers lack structured logging (request IDs, bytes read, actual provider names, outcomes). | Incomplete forensic auditing and violation of Mandate 22. | 🟧 **HIGH** |
| **8. Error Integrity** | Failure paths (download fail, parse error, index write error) are not covered by contract tests. | Silent failures, corrupted library files, and violation of Mandates 9 & 21. | 🟧 **HIGH** |
| **9. Policy & Governance** | No automated compliance check against the **Heritage Vetting Pipeline** (M14) for new crawling pipelines. | Risk of introducing non-vetted or unsafe patterns into the core. | 🟨 **MEDIUM** |
| **10. Operator UX** | No CLI or web interface for adjusting per-source quotas, retention windows, or toggling specific pipelines. | Operators cannot fine-tune the system for limited hardware resources. | 🟨 **MEDIUM** |

---

## §2 Background Workers & Orchestration (L2)

### 2.1 The Orchestration Gap
The background researcher loop (`_grow_frontier()`) runs independently of any curation worker. The planned `library_worker` (Phase H2-N) is sketched in the roadmap but has not been materialized. Without a centralized `WorkerCoordinator`, these processes run concurrently without awareness of each other, leading to high CPU contention and RAM spikes on the target AMD Ryzen 7 5700U processor.

### 2.2 Frontier Persistence & Graceful Shutdown
The crawling frontier (the list of URLs and topics to research) is rebuilt on each startup from a static configuration file (`research_topics.yaml`). 
* **The Blocker**: There is no persistent queue (`download_queue.json` or SQLite-backed queue) to track in-flight downloads, completed tasks, or failed attempts.
* **The Consequence**: If the engine is restarted or crashes, all in-flight work is lost, and the worker restarts from the beginning, leading to redundant network requests and potential IP bans.

### 2.3 Resource Contention & Back-Pressure
Heavy crawling and PDF parsing are highly CPU- and memory-intensive operations. Currently, background workers do not acquire the `ResourceGuard` semaphore before executing heavy tasks. If a user triggers a high-priority inference query while a background worker is parsing a large PDF, the system experiences severe latency spikes or OOM crashes, violating **Mandate 1 (AnyIO)** and **Mandate 7 (Local-First)**.

---

## §3 Security, Sandboxing, & Throttling (L3)

### 3.1 Unrestricted Network Access (SSRF)
The `ContentExtractor` and background researcher fetch content from arbitrary URLs provided in the frontier or discovered during crawling. 
* **The Vulnerability**: There are no checks to prevent Server-Side Request Forgery (SSRF). A malicious URL could point to localhost (`127.0.0.1`), private IP ranges (`10.0.0.0/8`, `192.168.0.0/16`), or internal container services (e.g., the Redis, Qdrant, or Postgres containers).
* **The Fix**: A strict IP/host validation layer must intercept all outgoing requests, resolving DNS records and blocking any private, loopback, or multicast addresses.

### 3.2 Path Traversal & File-Size Guards
When storing downloaded files or extracting metadata, the library does not sanitize file names or validate paths.
* **The Vulnerability**: A maliciously crafted document metadata field (e.g., a title containing `../../../../etc/passwd`) could trigger a path traversal vulnerability during the file-writing phase, overwriting critical system files.
* **The Vulnerability**: There are no strict file-size limits on incoming downloads. A single 2GB file could exhaust the remaining 17GB of free space on the `omega_library` partition, crashing the entire system.

### 3.3 Per-Domain Rate-Limiting
The current implementation relies on a generic `AsyncCircuitBreaker` in `health_monitor.py`. While this protects the engine from calling dead APIs, it does not implement per-domain rate-limiting (e.g., token bucket or leaky bucket algorithms). 
* **The Consequence**: Crawling academic servers like arXiv or Gutenberg too quickly results in immediate IP blocks, rendering the background worker useless.

---

## §4 Storage, Retention, & Indexing

### 4.1 The Empty FTS5 Index
An audit of the database and library directory revealed that while 13 curated documents are stored in `data/library/documents/`, the SQLite FTS5 index remains empty.
* **The Root Cause**: The `Indexer` is initialized with the `QdrantAdapter` but is never explicitly triggered to synchronize or rebuild the local FTS5 index on startup. This renders keyword searches via the CLI or API completely non-functional, forcing the system to fall back to slow, linear directory scans.

### 4.2 Tiered Retention & Compression
The library currently stores all curated documents as raw, uncompressed JSON files in `data/library/documents/`.
* **The Problem**: There is no tiered retention policy. A document downloaded 6 months ago is treated with the same priority as a document downloaded yesterday. Without compression (e.g., MsgPack or Gzip), the library will eventually exhaust the host's disk space.
* **The Solution**: Implement a 3-tier storage model:
  1. **Hot**: Uncompressed JSON in memory/Redis for active sessions.
  2. **Warm**: Gzipped JSON on disk for documents accessed within the last 30 days.
  3. **Cold**: Compressed MsgPack archives for older documents, with vector embeddings retained in Qdrant for semantic retrieval.

---

## §5 Integration, Observability, & Governance

### 5.1 The Hivemind-Gateway Bridge
The library and background workers operate in a silo. When a new document is curated and added to the library, no event is published to the Hivemind.
* **The Opportunity**: By bridging the library to the Hivemind, other agents (e.g., `@verity` or `@doom_guy`) can immediately become aware of new knowledge. Furthermore, the `ModelGateway` should be able to query the library dynamically during the prompt-construction phase, enabling local, offline RAG without needing external API calls.

### 5.2 Observability & Response Provenance (M22)
Background workers do not record response provenance. When a document is parsed or summarized, the logs do not capture which local model or cloud provider generated the summary. This violates **Mandate 22 (Response Provenance)**, which requires absolute forensic accuracy in all observability logs.

### 5.3 Error Integrity & Contract Testing (M21)
There are zero contract tests validating the return types of the curation and library modules. If a PDF parser returns a dictionary instead of an `ExtractedContent` dataclass, the failure is swallowed silently or crashes the worker loop, violating **Mandate 9 (Error Integrity)** and **Mandate 21 (Gate Integrity)**.

---

## §6 Implementation Specification & Roadmap

To resolve these gaps, we define a highly structured, 4-phase implementation plan.

```
PHASE 1: HARDENING & SECURITY (Days 1-3) ─── SSRF, Path Traversal, Size Guards, FTS5 Rebuild
PHASE 2: ORCHESTRATION & COORDINATOR (Days 4-7) ─── WorkerCoordinator, ResourceGuard, Checkpoints
PHASE 3: RATE-LIMITING & STORAGE (Days 8-10) ─── Token Bucket, Gzip Compression, Tiered Retention
PHASE 4: INTEGRATION & OBSERVABILITY (Days 11-14) ─── Hivemind Bridge, M21/M22 Compliance, CLI
```

### Phase 1: Security Hardening & Index Recovery (Days 1–3)

#### 1.1 SSRF Protection Layer (`src/omega/library/security.py`)
Implement a strict network guard that intercepts all outgoing HTTP requests from background workers.

```python
# [id-soft: doom-1993] SSRF Guard — prevents internal network probing
import socket
from urllib.parse import urlparse
import ipaddress

def validate_url_safety(url: str) -> bool:
    """Verify that the URL does not resolve to a private, loopback, or multicast IP."""
    try:
        parsed = urlparse(url)
        if not parsed.hostname:
            return False
        
        # Resolve hostname to IP
        ip_address = socket.gethostbyname(parsed.hostname)
        ip = ipaddress.ip_address(ip_address)
        
        # Check against private ranges
        if (ip.is_private or 
            ip.is_loopback or 
            ip.is_multicast or 
            ip.is_link_local or 
            ip.is_unspecified):
            return False
        return True
    except Exception:
        return False
```

#### 1.2 Path Traversal & File-Size Guards
Integrate file-size limits and path validation into the `ContentExtractor`.

```python
# [id-soft: quake-1996] Path Traversal & Size Guard
from pathlib import Path

MAX_DOWNLOAD_SIZE_BYTES = 50 * 1024 * 1024  # 50MB Cap

def validate_path_scope(target_path: Path, base_dir: Path) -> bool:
    """Ensure the target path resolves strictly within the base directory."""
    try:
        resolved_target = target_path.resolve()
        resolved_base = base_dir.resolve()
        return resolved_base in resolved_target.parents or resolved_target == resolved_base
    except Exception:
        return False
```

#### 1.3 FTS5 Index Rebuild Script (`scripts/rebuild_library_index.py`)
Create an atomic script to synchronize existing documents into the SQLite FTS5 index.

```python
# [id-soft: doom-1993] FTS5 Index Rebuild
import anyio
from omega.library.library import Library

async def main():
    print("⬡ Rebuilding Offline Library FTS5 Index...")
    lib = Library()
    # Force re-indexing of all loaded documents
    for doc in lib._documents.values():
        await lib._indexer.index_document(doc)
    print(f"⬡ Successfully indexed {len(lib._documents)} documents.")

if __name__ == "__main__":
    anyio.run(main)
```

---

### Phase 2: WorkerCoordinator & Resource Balancing (Days 4–7)

#### 2.1 The WorkerCoordinator (`src/omega/library/coordinator.py`)
Implement a centralized state machine that manages background task execution, monitors CPU/RAM load, and respects the `ResourceGuard`.

```python
# [id-soft: doom3-2004] WorkerCoordinator with ResourceGuard Integration
import anyio
import psutil
import logging
from typing import Dict, Any
from omega.oracle.resource_guard import ResourceGuard

logger = logging.getLogger(__name__)

class WorkerCoordinator:
    """Manages background worker execution and prevents resource starvation."""
    
    def __init__(self, resource_guard: ResourceGuard):
        self.guard = resource_guard
        self.active_workers: Dict[str, bool] = {}
        self.is_paused = False

    async def run_worker_task(self, worker_name: str, task_coro) -> Any:
        """Executes a background task only if system resources are sufficient."""
        while self.is_paused or self._is_system_overloaded():
            logger.warning(f"System overloaded or paused. Suspending worker: {worker_name}")
            await anyio.sleep(5)
            
        # Acquire ResourceGuard to guarantee inference priority
        async with self.guard.acquire():
            logger.info(f"Worker {worker_name} acquired ResourceGuard. Executing task.")
            return await task_coro()

    def _is_system_overloaded(self) -> bool:
        """Check CPU and RAM thresholds on Ryzen 5700U."""
        cpu_usage = psutil.cpu_percent(interval=0.1)
        ram_available_gb = psutil.virtual_memory().available / (1024 ** 3)
        # Suspend if CPU > 85% or available RAM < 1.5GB
        return cpu_usage > 85.0 or ram_available_gb < 1.5
```

---

### Phase 3: Per-Domain Rate-Limiting & Tiered Storage (Days 8–10)

#### 3.1 Token Bucket Rate-Limiter (`src/omega/library/rate_limiter.py`)
Implement a precise, AnyIO-compliant token bucket rate-limiter for external domains.

```python
# [id-soft: quake-1996] Token Bucket Rate-Limiter
import anyio
import time

class TokenBucketRateLimiter:
    """Per-domain rate limiter to prevent IP bans."""
    
    def __init__(self, rate: float, capacity: float):
        self.rate = rate  # Tokens added per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()
        self.lock = anyio.Lock()

    async def consume(self, tokens: float = 1.0):
        """Consume tokens, blocking if insufficient tokens are available."""
        async with self.lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.last_update
                self.last_update = now
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                # Wait for tokens to accumulate
                wait_time = (tokens - self.tokens) / self.rate
                await anyio.sleep(wait_time)
```

---

### Phase 4: Integration, Observability, & Compliance (Days 11–14)

#### 4.1 Hivemind Event Integration (`src/omega/library/hivemind_bridge.py`)
Publish curation events to the Hivemind to allow other agents to react to new knowledge.

```python
# [id-soft: quake3-1999] Hivemind Curation Event Bridge
from omega_hub.server import get_engine
from omega.library.curator import CuratedDocument

async def publish_curation_event(doc: CuratedDocument):
    """Publish an atomic curation event to the Hivemind."""
    engine = get_engine()
    event = {
        "event_type": "document_curated",
        "doc_id": doc.doc_id,
        "title": doc.title,
        "domain": doc.domain,
        "quality_score": doc.quality_score,
        "timestamp": doc.curated_at
    }
    # Post to Hivemind context queue
    await engine.hivemind.post_context(
        channel="opencode",
        entity="verity",
        model="local",
        task_current=f"New knowledge curated: {doc.title}",
        focus_chain=["curation", "library"],
        decisions=[{"decision": f"Stored document {doc.doc_id}", "status": "active"}],
        continuation=f"Document {doc.doc_id} is now searchable in the offline library."
    )
```

#### 4.2 Contract Verification Tests (`tests/test_library_contracts.py`)
Enforce **Mandate 21 (Gate Integrity)** by validating all core library return types.

```python
# [id-soft: doom-1993] Gate Integrity (M21) Contract Tests
import pytest
from omega.library.curator import CuratedDocument, CurationPipeline

@pytest.mark.anyio
async def test_curation_pipeline_contract():
    """Verify that the curation pipeline strictly returns a CuratedDocument."""
    pipeline = CurationPipeline()
    result = await pipeline.process(
        source="https://raw.githubusercontent.com/id-Software/DOOM/master/linuxdoom-1.10/w_wad.c",
        source_type="url"
    )
    assert isinstance(result, CuratedDocument)
    assert isinstance(result.doc_id, str)
    assert isinstance(result.quality_score, float)
    assert 0.0 <= result.quality_score <= 1.0
```

---

## §7 Verification Gates (Jem: 6 Gates to Deploy)

Before any code from this strategy is merged into the master branch, it must pass the following six verification gates:

1. **Security Gate (P4)**: SSRF, path traversal, and file-size guards must be exercised and pass with 100% success.
2. **Crash Resilience Gate (P2)**: The system must survive mid-download crashes and resume gracefully from `download_queue.json` without duplicating work.
3. **Resource Guard Gate (P1)**: Background workers must suspend automatically when CPU usage exceeds 85% or RAM drops below 1.5GB.
4. **Integrity Gate (P2)**: The SQLite FTS5 index must be verified as populated and searchable via the `Library.search()` method.
5. **Test Compliance Gate (P10)**: All contract tests (M21) must pass, and test coverage for the `library` module must be $\ge 80\%$.
6. **Operational Gate (P3)**: The CLI commands (`omega library search`, `omega worker status`, `omega worker pause`) must be fully functional and documented.

---

*⬡ This document completes the comprehensive curation, library, and crawling strategy review. ⬡*  
*Decision: D144 — Curation & Library Strategy v2.5.0 ratified.*  
*Action: Forwarded to Ma'at (P3 Build) and Lilith (P6 Run) for execution scheduling.*  

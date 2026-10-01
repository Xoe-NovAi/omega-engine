<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Curation & Library Security Execution Plan
## Sprint H2-N: 4-Phase Implementation Blueprint

**AP Token**: `AP-CURATION-LIBRARY-EXECUTION-v1.0.0`
**Date**: 2026-06-22
**Owner**: Kali (Grand Oversight) → Ma'at (P1-P5 Build) + Lilith (P6-P10 Runtime)
**Baseline**: 444/444 tests passing · 22 Mandates · 11-Agent Fleet

---

## §0 Pre-Flight Checklist (Before ANY Code)

| # | Action | Check |
|---|--------|-------|
| 1 | `git status` — ensure working tree is clean on main | ⬜ |
| 2 | `make test` — confirm 444/444 passing | ⬜ |
| 3 | `make temple-grade` — confirm T1-T11 green | ⬜ |
| 4 | `make heritage-map` — confirm [id-soft:] tag coverage | ⬜ |
| 5 | Branch off: `git checkout -b sprint/H2-N/curation-security` | ⬜ |
| 6 | Hivemind workspace lock: acquire `curation_library` domain | ⬜ |
| 7 | Hivemind heartbeat: announce `kali` presence, `H2-N execution` | ⬜ |

---

## §1 Phase 1: Security Hardening & Index Recovery
**Days 1-3 · ~8 hours · Owner: Ma'at (P4 Security + P3 Engineering)**

### Sprint 1.1: SSRF Protection Layer (2 hr)

**Target file**: `src/omega/library/security.py` (NEW)

**Implementation**:
```python
# [id-soft: doom-1993] SSRF Guard — prevents internal network probing
# Ported from BSP leaf-culling: skip invisible subtrees in O(1)
import socket
from urllib.parse import urlparse
import ipaddress

class SSRFGuard:
    """Network guard that validates URLs against private/internal IP ranges."""
    
    FORBIDDEN_RANGES = [
        "127.0.0.0/8",      # Loopback
        "10.0.0.0/8",       # Private A
        "172.16.0.0/12",    # Private B
        "192.168.0.0/16",   # Private C
        "169.254.0.0/16",   # Link-local
        "::1/128",           # IPv6 loopback
        "fc00::/7",          # IPv6 unique-local
        "fe80::/10",         # IPv6 link-local
    ]
    
    @staticmethod
    async def validate(url: str) -> bool:
        """Validate that URL does not resolve to internal IP. Returns True if safe."""
        try:
            parsed = urlparse(url)
            if not parsed.hostname:
                return False
            # Resolve hostname to all IPs
            addrinfo = await anyio.to_thread.run_sync(
                socket.getaddrinfo, parsed.hostname, None
            )
            for family, type_, proto, canon, sockaddr in addrinfo:
                ip = ipaddress.ip_address(sockaddr[0])
                for cidr in SSRFGuard.FORBIDDEN_RANGES:
                    if ip in ipaddress.ip_network(cidr):
                        logger.warning(f"SSRF blocked: {url} resolves to {ip} ({cidr})")
                        return False
            return True
        except (socket.gaierror, ValueError, OSError) as e:
            logger.warning(f"SSRF validation failed for {url}: {e}")
            return False

GUARD = SSRFGuard()
```

**Integration edits**:
- `src/omega/library/extractor.py:129` — insert `await GUARD.validate(url)` before `client.get(url)`
- `src/omega/library/__init__.py` — add `from .security import SSRFGuard, GUARD`

**Verification**:
```python
# Test that 127.0.0.1, 10.x.x.x, 192.168.x.x are rejected
# Test that public URLs (github.com, arxiv.org) are accepted
```

---

### Sprint 1.2: Path Traversal & Size Guards (2 hr)

**Target file**: `src/omega/library/security.py` (append to existing)

```python
# [id-soft: quake-1996] Path Traversal Guard & Size Limit
# Ported from zone.c boundary enforcement
from pathlib import Path

MAX_DOWNLOAD_SIZE_BYTES = 50 * 1024 * 1024  # 50MB

def validate_path_scope(target_path: Path, base_dir: Path) -> bool:
    """Ensure target_path resolves strictly within base_dir."""
    try:
        resolved = target_path.resolve()
        base = base_dir.resolve()
        return base in resolved.parents or resolved == base
    except (RuntimeError, OSError):
        return False

async def validate_download_size(url: str, max_bytes: int = MAX_DOWNLOAD_SIZE_BYTES) -> bool:
    """Check Content-Length header before downloading (HEAD request)."""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.head(url, follow_redirects=True)
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > max_bytes:
                logger.warning(f"Download blocked: {url} is {content_length} bytes (max {max_bytes})")
                return False
            return True
    except Exception as e:
        logger.warning(f"Size pre-check failed for {url}: {e}")
        return True  # Allow on HEAD failure (bytes will be caught mid-stream)
```

**Integration edits**:
- `src/omega/library/extractor.py:_extract_url` — call `validate_download_size()` before download; wrap `client.get()` with `response.raise_for_status()` + streaming size cap
- `src/omega/library/extractor.py:_extract_file` — validate `validate_path_scope()` before opening any file

**Verification**:
```python
# Test path traversal: "../../etc/passwd" → False
# Test size guard: URL with Content-Length > 50MB → blocked
# Test normal file: within scope → True
```

---

### Sprint 1.3: FTS5 Index Rebuild (1.5 hr)

**Target files**: `scripts/rebuild_library_index.py` (NEW) + `src/omega/library/library.py` (modify)

**Script**:
```python
#!/usr/bin/env python3
# AP: AP-REBUILD-LIBRARY-INDEX-v1.0.0
# ⬡ OMEGA ⬡ KALI ⬡ sovereign ⬡ REBUILD ⬡ CRITICAL
"""Rebuild the library FTS5 index from stored documents.
Usage: python scripts/rebuild_library_index.py
"""
import anyio, sys, logging
sys.path.insert(0, "src")
from omega.library.library import Library

logging.basicConfig(level=logging.INFO)

async def main():
    print("⬡ Rebuilding Offline Library FTS5 Index...")
    lib = Library()
    count = 0
    for doc in lib._documents.values():
        await lib._indexer.index_document(doc)
        count += 1
    await lib._indexer.flush()
    stats = await lib._indexer.stats()
    print(f"⬡ Indexed {count} documents. FTS stats: {stats}")

if __name__ == "__main__":
    anyio.run(main())
```

**Library init modification** (`library.py:_load`, after line 60):
```python
# Auto-rebuild FTS index if empty on startup
async def _ensure_index(self) -> None:
    stats = await self._indexer.stats()
    if stats.get("fts_documents", 0) == 0 and self._documents:
        logger.info("FTS index empty — auto-rebuilding from stored documents...")
        for doc in self._documents.values():
            await self._indexer.index_document(doc)
        await self._indexer.flush()
        stats = await self._indexer.stats()
        logger.info(f"FTS index rebuilt: {stats}")
```

**Verification**: Run script, then call `Library.search("test")` → returns results.

---

## §2 Phase 2: WorkerCoordinator & Resource Balancing
**Days 4-7 · ~6 hours · Owner: Ma'at (P1 ResourceGuard + P3 Engineering)**

### Sprint 2.1: WorkerCoordinator Core (3 hr)

**Target file**: `src/omega/library/coordinator.py` (NEW)

```python
# [id-soft: doom3-2004] WorkerCoordinator — Resource-aware background task scheduler
# Ported from idHeap: tag-based allocation with purge-on-pressure
import anyio, psutil, logging
from typing import Dict, Any, Callable, Awaitable
from omega.oracle.resource_guard import ResourceGuard

logger = logging.getLogger(__name__)

class WorkerCoordinator:
    """Centralized background worker scheduler with ResourceGuard integration.
    
    State machine:
      RUNNING ↔ PAUSED (auto on system pressure)
        ↕
      SHUTDOWN (graceful)
    
    Workers register via run_worker() and are parked when:
      - CPU > 85% (Ryzen 5700U threshold)
      - Available RAM < 1.5GB
      - User explicitly sends PAUSE
    """
    
    CPU_HIGH_WATERMARK = 85.0   # percentage
    RAM_LOW_WATERMARK = 1.5     # GB
    
    def __init__(self, resource_guard: ResourceGuard):
        self._guard = resource_guard
        self._active_workers: Dict[str, bool] = {}
        self._paused = False
        self._shutdown = False
        self._lock = anyio.Lock()
    
    async def run_worker(
        self, 
        name: str, 
        task_coro: Callable[[], Awaitable[Any]],
        priority: int = 0
    ) -> Any:
        """Execute a worker task with resource-aware scheduling."""
        self._active_workers[name] = True
        try:
            # Wait until system is healthy
            while await self._is_overloaded() or self._paused:
                if self._shutdown:
                    logger.info(f"Worker {name}: shutdown requested")
                    return None
                await anyio.sleep(5)
            
            # Acquire ResourceGuard (gives priority to user inference)
            async with self._guard.acquire():
                logger.info(f"Worker {name}: acquired ResourceGuard, executing")
                return await task_coro()
        finally:
            self._active_workers[name] = False
    
    async def _is_overloaded(self) -> bool:
        """Check system load against Ryzen 5700U thresholds."""
        return anyio.to_thread.run_sync(self._check_sync)
    
    def _check_sync(self) -> bool:
        cpu = psutil.cpu_percent(interval=0.1)
        ram_gb = psutil.virtual_memory().available / (1024**3)
        if cpu > self.CPU_HIGH_WATERMARK:
            logger.info(f"Coordinator PAUSE: CPU {cpu:.0f}% > {self.CPU_HIGH_WATERMARK}%")
            return True
        if ram_gb < self.RAM_LOW_WATERMARK:
            logger.info(f"Coordinator PAUSE: RAM {ram_gb:.1f}GB < {self.RAM_LOW_WATERMARK}GB")
            return True
        return False
    
    async def pause(self) -> None:
        async with self._lock:
            self._paused = True
            logger.info("WorkerCoordinator: PAUSED by user")
    
    async def resume(self) -> None:
        async with self._lock:
            self._paused = False
            logger.info("WorkerCoordinator: RESUMED by user")
    
    async def shutdown(self) -> None:
        self._shutdown = True
        # Wait for active workers to finish
        while any(self._active_workers.values()):
            await anyio.sleep(1)
    
    @property
    def status(self) -> Dict[str, Any]:
        return {
            "paused": self._paused,
            "shutdown": self._shutdown,
            "active_workers": {k: v for k, v in self._active_workers.items()},
            "worker_count": sum(1 for v in self._active_workers.values() if v),
        }
```

---

### Sprint 2.2: Wire Coordinator into Background Researcher (3 hr)

**Target file**: `src/omega/workers/background_researcher/loop.py`

**Changes**:
1. Import `WorkerCoordinator` from `omega.library.coordinator`
2. Add `self.coordinator: Optional[WorkerCoordinator] = None` to `__init__`
3. Wrap the main research cycle with `await self.coordinator.run_worker("background_researcher", self._cycle_once)`
4. Check `self.coordinator._paused` between state transitions

**Target file**: `src/omega/oracle/resource_guard.py` (verify interface compatibility)

**Verification**:
```python
# Test: coordinator pauses when CPU high
# Test: coordinator resumes when CPU normal
# Test: graceful shutdown completes within 5 seconds
```

---

## §3 Phase 3: Rate-Limiting & Tiered Storage
**Days 8-10 · ~5 hours · Owner: Lilith (P2 Persistence + P6 ModelGate)**

### Sprint 3.1: Token Bucket Rate-Limiter (2 hr)

**Target file**: `src/omega/library/rate_limiter.py` (NEW)

```python
# [id-soft: quake-1996] Token Bucket Rate-Limiter
# Ported from Quake's fixed-timestep accumulator pattern
import anyio, time, logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class TokenBucketRateLimiter:
    """Per-domain token bucket rate limiter.
    
    Each domain gets its own bucket:
      - arxiv.org: 1 req / 3 sec  (rate=0.33, capacity=1)
      - gutenberg.org: 1 req / 1 sec (rate=1.0, capacity=3)
      - default: 2 req / sec (rate=2.0, capacity=5)
    
    AnyIO-compliant: await limiter.consume("arxiv.org") blocks until tokens available.
    """
    
    DOMAIN_DEFAULTS = {
        "arxiv.org":       (0.33, 1),    # 1 req per 3 sec
        "export.arxiv.org":(0.33, 1),
        "gutenberg.org":   (1.0,  3),    # 1 req per sec, burst 3
        "www.gutenberg.org":(1.0, 3),
        "openlibrary.org": (2.0,  5),    # 2 req per sec, burst 5
        "archive.org":     (1.0,  3),    # 1 req per sec, burst 3
        "default":         (5.0,  10),   # 5 req per sec, burst 10
    }
    
    def __init__(self):
        self._buckets: Dict[str, "_Bucket"] = {}
        self._lock = anyio.Lock()
    
    async def consume(self, domain: str, tokens: float = 1.0):
        """Consume tokens from the domain's bucket. Blocks if insufficient."""
        bucket = await self._get_bucket(domain)
        async with bucket.lock:
            while True:
                now = time.monotonic()
                elapsed = now - bucket.last_refill
                bucket.last_refill = now
                bucket.tokens = min(bucket.capacity, bucket.tokens + elapsed * bucket.rate)
                
                if bucket.tokens >= tokens:
                    bucket.tokens -= tokens
                    return
                
                wait = (tokens - bucket.tokens) / bucket.rate
                logger.debug(f"Rate limit: waiting {wait:.1f}s for {domain}")
                await anyio.sleep(wait)
    
    async def _get_bucket(self, domain: str) -> "_Bucket":
        async with self._lock:
            if domain not in self._buckets:
                rate, cap = self.DOMAIN_DEFAULTS.get(domain, self.DOMAIN_DEFAULTS["default"])
                self._buckets[domain] = self._Bucket(rate, cap)
            return self._buckets[domain]
    
    class _Bucket:
        def __init__(self, rate: float, capacity: float):
            self.rate = rate
            self.capacity = capacity
            self.tokens = capacity
            self.last_refill = time.monotonic()
            self.lock = anyio.Lock()
    
    @property
    def stats(self) -> Dict[str, Any]:
        return {
            domain: {"rate": b.rate, "capacity": b.capacity, "tokens": round(b.tokens, 1)}
            for domain, b in self._buckets.items()
        }

RATE_LIMITER = TokenBucketRateLimiter()
```

**Integration**: Insert `await RATE_LIMITER.consume(domain)` before each outgoing HTTP request in `extractor.py:_extract_url()` and `discovery.py:search()`.

---

### Sprint 3.2: Tiered Storage with Compression (3 hr)

**Target file**: `src/omega/library/library.py`

**Changes**:
1. Add compression constants and helpers:
```python
import gzip, json
from datetime import datetime, timedelta, timezone

HOT_DAYS = 7       # Uncompressed for recent docs
WARM_DAYS = 30     # Gzip-compressed for recent-ish docs
# Older = cold (compressed, Qdrant-only for search)

def _compress(data: dict) -> bytes:
    return gzip.compress(json.dumps(data, default=str).encode())

def _decompress(data: bytes) -> dict:
    return json.loads(gzip.decompress(data).decode())
```

2. Modify `store()` to write both `.json` and `.json.gz`:
   - Documents < 7 days old: `.json` only (hot)
   - Documents 7-30 days old: `.json.gz` (warm) + delete `.json`
   - Documents > 30 days old: `.json.gz` (cold) + keep vector embeddings

3. Add `async def archive_old_documents()` — called on startup:
   - Scans all `.json` files, checks `curated_at`
   - Migrates warm/cold to `.json.gz`
   - Logs summary

---

## §4 Phase 4: Integration, Observability & Compliance
**Days 11-14 · ~8 hours · Owner: Lilith (P8 Observability) + Verity (P10 Validation)**

### Sprint 4.1: Hivemind Curation Event Bridge (1.5 hr)

**Target file**: `src/omega/library/hivemind_bridge.py` (NEW)

```python
# [id-soft: quake3-1999] Hivemind Curation Event Bridge
# Ported from netchan OOB event propagation
import logging
from omega.library.curator import CuratedDocument

logger = logging.getLogger(__name__)

class CurationEventBridge:
    """Publishes library curation events to the Hivemind."""
    
    def __init__(self, hivemind=None):
        self._hivemind = hivemind  # Injected OmegaHub engine
    
    async def publish_new_document(self, doc: CuratedDocument) -> None:
        """Notify the fleet of a newly curated document."""
        if not self._hivemind:
            return
        try:
            await self._hivemind.post_context(
                channel="library",
                entity="verity",
                model="local",
                task_current=f"New knowledge curated: {doc.title}",
                focus_chain=["curation", "library", doc.domain or "general"],
                decisions=[{"decision": f"Stored document {doc.doc_id}", "status": "active"}],
                continuation=f"Document {doc.doc_id} [{doc.domain}] now searchable offline."
            )
        except Exception as e:
            logger.warning(f"Hivemind bridge failed for {doc.doc_id}: {e}")

BRIDGE = CurationEventBridge()
```

**Integration**: Call `await BRIDGE.publish_new_document(doc)` at the end of `Library.store()` (after successful index).

---

### Sprint 4.2: M21 Contract Tests (1.5 hr)

**Target file**: `tests/test_library_contracts.py` (NEW)

```python
# ⬡ OMEGA ⬡ VERITY ⬡ sovereign ⬡ CONTRACT-TESTS ⬡ M21
# [id-soft: doom-1993] Gate Integrity (M21) — verify return types at every API boundary

import pytest
from omega.library.curator import CuratedDocument, CurationPipeline
from omega.library.extractor import ExtractedContent, ContentExtractor
from omega.library.security import SSRFGuard, validate_path_scope
from omega.library.rate_limiter import TokenBucketRateLimiter
from pathlib import Path

@pytest.mark.anyio
async def test_curation_pipeline_contract():
    """Verify curation pipeline returns CuratedDocument."""
    pipeline = CurationPipeline()
    result = await pipeline.process(
        source="https://raw.githubusercontent.com/id-Software/DOOM/master/linuxdoom-1.10/w_wad.c",
        source_type="url"
    )
    assert isinstance(result, CuratedDocument)
    assert isinstance(result.doc_id, str)
    assert isinstance(result.quality_score, float)
    assert 0.0 <= result.quality_score <= 1.0
    assert isinstance(result.body, str)

@pytest.mark.anyio
async def test_extracted_content_return_type():
    """Verify extractor returns ExtractedContent."""
    extractor = ContentExtractor()
    result = await extractor.extract("inline test note", "note")
    assert isinstance(result, ExtractedContent)
    assert isinstance(result.source, str)
    assert result.source_type == "note"

@pytest.mark.anyio
async def test_ssrf_guard_contract():
    """Verify SSRFGuard returns bool."""
    result = await SSRFGuard.validate("https://github.com")
    assert isinstance(result, bool)

def test_path_scope_contract():
    """Verify validate_path_scope returns bool."""
    result = validate_path_scope(
        Path("/safe/dir/file.txt"),
        Path("/safe/dir")
    )
    assert isinstance(result, bool)
    assert result is True
    
def test_path_scope_traversal_rejected():
    """Verify path traversal is detected."""
    result = validate_path_scope(
        Path("/safe/dir/../../etc/passwd"),
        Path("/safe/dir")
    )
    assert result is False

@pytest.mark.anyio
async def test_rate_limiter_contract():
    """Verify TokenBucketRateLimiter.consume returns None."""
    limiter = TokenBucketRateLimiter()
    result = await limiter.consume("test.example.com")
    assert result is None  # consume is fire-and-forget (blocks)
```

---

### Sprint 4.3: M22 Response Provenance (2 hr)

**Target file**: `src/omega/workers/background_researcher/loop.py`

**Changes**:
- Add structured logging with `trace_id`, `provider_name`, `bytes_downloaded`, `duration_ms` to every state transition
- Use `logging.StructuredFormatter` or append JSON lines to `data/logs/curation.log`
- Every log entry must capture `provider_name` from the actual response, not the configured intent (M22)

**Pattern**:
```python
log_entry = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "trace_id": str(uuid.uuid4()),
    "worker": "background_researcher",
    "state": current_state,
    "source": url,
    "provider": actual_provider,  # NOT configured provider
    "bytes_downloaded": len(content),
    "duration_ms": int((time.monotonic() - start) * 1000),
    "outcome": "success" if success else "failure",
}
```

---

### Sprint 4.4: CLI Control (2 hr)

**Target file**: `src/omega/cli/oracle_cli.py` (append to existing Typer app)

```python
import typer
from omega.library.coordinator import get_coordinator  # singleton accessor

app = typer.Typer()  # or add to existing CLI group

@app.command()
def worker():
    """Manage background workers."""
    pass

@worker.command()
def pause():
    """Pause all background curation workers."""
    coord = get_coordinator()
    await coord.pause()
    typer.echo("⏸️ All background workers paused")

@worker.command()
def resume():
    """Resume all background curation workers."""
    coord = get_coordinator()
    await coord.resume()
    typer.echo("▶️ All background workers resumed")

@worker.command()
def status():
    """Show worker status."""
    coord = get_coordinator()
    status = coord.status
    typer.echo(f"Paused: {status['paused']}")
    typer.echo(f"Active workers: {status['worker_count']}")
    for name, active in status['active_workers'].items():
        typer.echo(f"  {name}: {'🟢' if active else '⚫'}")

@worker.command()
def rebuild_index():
    """Rebuild the library FTS5 search index."""
    import anyio
    from scripts.rebuild_library_index import main
    anyio.run(main)
```

---

## §5 Dependency Graph & Parallelization

```
Phase 1 (Security) ────────────→ Phase 2 (Coordinator) ────→ Phase 3 (Rate-Limiting) ────→ Phase 4 (Integration)
        │                               │                            │                            │
        ├─ 1.1 SSRF Guard ──────────────┤                            │                            │
        ├─ 1.2 Path Traversal ──────────┤                            │                            │
        ├─ 1.3 FTS5 Rebuild ────────────┤ (coordinator needs guard)  │                            │
        │                               │                            │                            │
        │                               ├─ 2.1 Coordinator Core ─────┤                            │
        │                               ├─ 2.2 Wire into researcher─┤                            │
        │                                                           ├─ 3.1 Rate Limiter ──────────┤
        │                                                           ├─ 3.2 Tiered Storage ───────┤
        │                                                                                       ├─ 4.1 Hivemind Bridge
        │                                                                                       ├─ 4.2 Contract Tests
        │                                                                                       ├─ 4.3 M22 Provenance
        │                                                                                       └─ 4.4 CLI Control
```

**Parallelization opportunities**:
- 1.1 + 1.2 + 1.3 can be done in parallel (3 different files, no cross-dependency)
- 2.1 + 3.1 can be done in parallel (coordinator and rate-limiter are independent)
- 4.1 + 4.2 + 4.4 can be done in parallel after core is built
- 4.3 depends on 2.2 (needs the worker loop wired)

---

## §6 Delegation Matrix

| Sprint | Task | Best Agent | Skill/Tools Required | Est. Time |
|--------|------|-----------|---------------------|:---------:|
| 1.1 | SSRF Guard | `@pillar P4` | Python, socket, ipaddress | 2 hr |
| 1.2 | Path/Size Guards | `@pillar P4` | pathlib, httpx, streaming | 2 hr |
| 1.3 | FTS5 Rebuild | `@pillar P2` | aiosqlite, Library | 1.5 hr |
| 2.1 | Coordinator Core | `@pillar P1` | ResourceGuard, psutil, anyio | 3 hr |
| 2.2 | Wire Researcher | `@pillar P3` | BackgroundResearcherLoop | 3 hr |
| 3.1 | Rate Limiter | `@pillar P6` | Token bucket, domain config | 2 hr |
| 3.2 | Tiered Storage | `@pillar P2` | gzip, Library, retention policies | 3 hr |
| 4.1 | Hivemind Bridge | `@pillar P9` | OmegaHub, Hivemind post_context | 1.5 hr |
| 4.2 | Contract Tests | `@verity` | pytest, M21 patterns | 1.5 hr |
| 4.3 | M22 Provenance | `@pillar P8` | Structured logging, JSON | 2 hr |
| 4.4 | CLI Control | `@pillar P3` | Typer, WorkerCoordinator | 2 hr |

---

## §7 Verification Gates (6 Gates Before Merge)

After each phase, validate. After Phase 4 complete, run the full suite:

| Gate | What It Validates | Command | Owner |
|:----:|-------------------|---------|-------|
| **T3** | Test coverage ≥80% for library module | `make test` | P10 |
| **T5** | AnyIO-only (zero asyncio) in new files | `grep -rn "import asyncio" src/omega/library/` | P5 |
| **T6** | Zero telemetry in new code | `grep -rn "analytics\|phone.home\|telemetry" src/omega/library/` | P5 |
| **T8** | ResourceGuard integrated (back-pressure) | `grep -rn "ResourceGuard" src/omega/library/coordinator.py` | P1 |
| **T9** | Structured logging (JSON, trace_id) | `grep -rn "trace_id" src/omega/workers/background_researcher/` | P8 |
| **M21** | Contract tests exist and pass | `pytest tests/test_library_contracts.py -v` | P10 |

**Final validation**:
```bash
make test                   # All 444+ tests passing
make temple-grade           # T1-T11 green
make heritage-map           # [id-soft:] tags in all new files
```

---

## §8 Rollback Plan

If any gate fails or a deployed worker causes system instability:

```bash
# Immediate halt
omega worker pause                              # Pause background workers
git checkout main                              # Revert code
omega worker resume                            # Only after rollback confirmed

# If issues persist
sudo systemctl stop omega-research.timer       # Kill the research timer
sudo systemctl stop omega-research.service     # Kill running instance
git stash                                      # Stash changes
git checkout main                              # Hard revert
```

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ H2-N-EXECUTION-PLAN ⬡*
*Decision: D145 — Curation & Library Execution Plan ratified. Ready for delegation to Ma'at + Lilith.*

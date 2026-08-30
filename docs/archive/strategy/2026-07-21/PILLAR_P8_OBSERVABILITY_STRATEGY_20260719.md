<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Pillar P8 — Observability (WatchTower) Strategy
## Autonomous Meditation Pipeline as Complete Product

**AP Token**: `AP-PILLAR-P8-OBSERVABILITY-v1.0.0`
⬡ OMEGA ⬡ PILLAR ⬡ P8 ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_pillar_p8 ⬡ ACTIVE

**Date**: 2026-07-19
**Slot**: P8 Observability — WatchTower
**Entity**: Pillar Keeper for Observability
**Mission**: Create comprehensive P8 Observability Strategy for Autonomous Meditation Pipeline as Complete Product

---

## 📋 Executive Summary

The Autonomous Meditation Pipeline (AMP) is a 24/7 background ingestion, curation, scraping, and meditation cycle system. It requires **production-grade observability** that is:

1. **Local-first** (M7) — Zero external telemetry, all data stays on-device
2. **Forensically accurate** (M22) — Response provenance captured at receipt, not dispatch
3. **Failure-integrity compliant** (M23) — No soft failures, hard stops on tool-chain collapse
4. **Streaming-aware** — Nemotron 3 Ultra (OpenCode Zen) timeout detection with chunk-level timing
5. **Agent-coordination native** — Redis Streams replacing file-based Hivemind for task-critical paths
6. **Temple-Grade** (M13) — T1-T11 gates enforced via `make temple-grade`

This strategy defines the architecture, implementation phases, and integration points for P8 to serve as the **WatchTower** for the Autonomous Meditation Pipeline.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS MEDITATION PIPELINE (AMP)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Ingestion  │─▶│  Curation   │─▶│  Scraping   │─▶│ Meditation  │        │
│  │  Workers    │  │  Pipeline   │  │  Workers    │  │  Cycles     │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │                │
│         └────────────────┼────────────────┼────────────────┘                │
│                          ▼                                                │
│              ┌───────────────────────┐                                   │
│              │   P8 WATCHTOWER       │                                   │
│              │  (Observability Bus)  │                                   │
│              └───────────┬───────────┘                                   │
│                          │                                                │
│         ┌────────────────┼────────────────┐                              │
│         ▼                ▼                ▼                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                       │
│  │ Structured  │  │  Metrics    │  │  Forensic   │                       │
│  │ Logging     │  │  Collection │  │  Ledger     │                       │
│  │ (Trace ID   │  │ (Prometheus │  │ (UFL +      │                       │
│  │  Propagation)│  │  + SQLite)  │  │  Crash Dump)│                       │
│  └─────────────┘  └─────────────┘  └─────────────┘                       │
│         │                │                │                              │
│         └────────────────┼────────────────┘                              │
│                          ▼                                                │
│              ┌───────────────────────┐                                   │
│              │  Redis Streams        │                                   │
│              │  (Agent Coordination) │                                   │
│              │  + Pub/Sub (Heartbeats)│                                  │
│              └───────────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core Components

| Component | Technology | Purpose | Mandate |
|-----------|------------|---------|---------|
| **Trace Propagation** | `contextvars` + AnyIO | `trace_id` across async boundaries | M9, M22 |
| **Structured Logging** | `structlog` + JSONL | Machine-parseable events | M9, M8 |
| **Metrics Collection** | Prometheus client + SQLite (MetricsDB) | Local-only metrics, no export | M8, M13 |
| **Forensic Ledger** | UFL (Unified Forensic Ledger) | Immutable audit trail | M9, M23 |
| **Crash Forensics** | ForensicsManager | Last-gasp crash dumps | M9, M15 |
| **Streaming Observability** | Custom chunk tracker | Nemotron timeout detection | M23 |
| **Agent Coordination** | Redis Streams + Pub/Sub | Hivemind replacement for task-critical | M12, M23 |
| **Health Monitoring** | HardwareMonitor + SLA tracker | 24/7 background process health | M7, M13 |

---

## 🔬 Detailed Technical Areas

### 1. Structured Logging with Trace ID Propagation (M9)

**Current State**: `src/omega/observability/context.py` provides `contextvars`-based trace_id propagation. `ObservabilityEngine.log_event()` captures events with trace_id.

**Gaps**:
- No automatic trace_id injection into stdlib `logging` records
- No structured log formatter for JSON output
- No correlation across provider fabric, MCP Hub, and agents

**Implementation**:
```python
# src/omega/observability/structured_logging.py
import structlog
import logging
from contextvars import ContextVar
from omega.observability.context import get_current_trace_id

# Contextvars for structured logging context
_structlog_context: ContextVar[dict] = ContextVar("structlog_context", default={})

def configure_structured_logging(level: str = "INFO") -> None:
    """Configure structlog with trace_id injection and JSON output."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            _inject_trace_id,  # Custom processor
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level)),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

def _inject_trace_id(logger, method_name, event_dict):
    """Inject current trace_id into every log entry."""
    trace_id = get_current_trace_id()
    event_dict["trace_id"] = trace_id
    return event_dict

# Usage in any component:
# logger = structlog.get_logger()
# logger.info("model_invoked", provider="native-gguf", model="qwen3-1.7b", latency_ms=234)
```

**Integration Points**:
- Provider Fabric: Wrap all `generate()` calls with trace context
- MCP Hub: Middleware injects trace_id on incoming requests
- Agents: `@pillar` subagents inherit trace_id via Hivemind handoff

---

### 2. Response Provenance (M22 — Mandatory)

**Current State**: `GenerateResult` dataclass in `src/omega/oracle/providers.py` carries `provider_name` from actual response.

**Requirement**: Every inference call MUST log provenance at **response receipt**, not dispatch intent.

**Implementation**:
```python
# In ModelGateway.generate() - after provider returns:
async def generate(self, ...) -> GenerateResult:
    trace_id = get_current_trace_id()
    start = time.monotonic()
    
    try:
        result = await provider.generate(...)
        latency_ms = (time.monotonic() - start) * 1000
        
        # M22: Capture ACTUAL provider from response
        actual_provider = result.provider_name  # Not get_preferred_backend()!
        
        # Log to ObservabilityEngine with provenance
        engine = get_engine()
        engine.log_event(
            EventType.MODEL_COMPLETED,
            trace_id,
            {
                "provider": actual_provider,  # M22: Actual, not intended
                "model": result.model,
                "latency_ms": latency_ms,
                "prompt_tokens": result.prompt_tokens,
                "completion_tokens": result.completion_tokens,
                "is_cloud": actual_provider not in LOCAL_PROVIDERS,
            }
        )
        
        # Record to MetricsDB for sovereignty scorecard
        engine.record_performance(
            latency_ms=latency_ms,
            provider=actual_provider,
            model_used=result.model,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            is_cloud=actual_provider not in LOCAL_PROVIDERS,
            trace_id=trace_id,
        )
        
        return result
    except Exception as e:
        engine.record_metrics_error(
            error_type=type(e).__name__,
            error_message=str(e),
            trace_id=trace_id,
            provider=provider_name,  # Intended provider for error context
        )
        raise
```

**Sovereignty Scorecard Query** (already implemented in `omega-hub_sovereignty_ratio`):
```sql
SELECT 
    COUNT(*) FILTER (WHERE is_cloud = 0) as local_count,
    COUNT(*) FILTER (WHERE is_cloud = 1) as cloud_count,
    COUNT(*) as total,
    ROUND(COUNT(*) FILTER (WHERE is_cloud = 0) * 100.0 / COUNT(*), 2) as local_pct
FROM performance 
WHERE ts > ?;
```

---

### 3. Streaming Observability — Nemotron 3 Ultra Timeout Detection

**Problem** (from GitHub issues #33714, #33709, #34026):
- Nemotron 3 Ultra Free on OpenCode Zen has **slow token generation** (long gaps between tokens)
- "Upstream idle timeout exceeded" occurs mid-stream even for 100-line responses
- No progress detection → cannot distinguish "slow but working" from "hung"

**Solution**: Chunk-level streaming observability with adaptive timeout.

```python
# src/omega/observability/streaming.py
from dataclasses import dataclass, field
from typing import AsyncIterator, Optional
import time
import anyio

@dataclass
class StreamMetrics:
    """Chunk-level streaming metrics for timeout detection."""
    trace_id: str
    provider: str
    model: str
    first_token_time: Optional[float] = None
    last_token_time: Optional[float] = None
    chunk_count: int = 0
    total_tokens: int = 0
    inter_chunk_latencies: list = field(default_factory=list)
    timeout_events: list = field(default_factory=list)
    
    def record_chunk(self, token_count: int = 1) -> None:
        now = time.monotonic()
        if self.first_token_time is None:
            self.first_token_time = now
        if self.last_token_time is not None:
            self.inter_chunk_latencies.append(now - self.last_token_time)
        self.last_token_time = now
        self.chunk_count += 1
        self.total_tokens += token_count
    
    @property
    def ttft_ms(self) -> Optional[float]:
        """Time to first token in milliseconds."""
        if self.first_token_time and hasattr(self, '_start_time'):
            return (self.first_token_time - self._start_time) * 1000
        return None
    
    @property
    def avg_inter_chunk_ms(self) -> Optional[float]:
        if not self.inter_chunk_latencies:
            return None
        return (sum(self.inter_chunk_latencies) / len(self.inter_chunk_latencies)) * 1000
    
    @property
    def max_inter_chunk_ms(self) -> Optional[float]:
        if not self.inter_chunk_latencies:
            return None
        return max(self.inter_chunk_latencies) * 1000
    
    @property
    def is_stalled(self, idle_threshold_ms: float = 120000) -> bool:
        """Check if stream has stalled (no tokens for threshold)."""
        if self.last_token_time is None:
            return False
        return (time.monotonic() - self.last_token_time) * 1000 > idle_threshold_threshold_ms


class StreamingObserver:
    """Wraps an async generator to observe streaming metrics."""
    
    def __init__(self, trace_id: str, provider: str, model: str, 
                 idle_timeout_ms: float = 120000,  # 2 min default for Nemotron
                 first_token_timeout_ms: float = 30000):
        self.metrics = StreamMetrics(trace_id, provider, model)
        self.metrics._start_time = time.monotonic()
        self.idle_timeout_ms = idle_timeout_ms
        self.first_token_timeout_ms = first_token_timeout_ms
        self._first_token_received = False
    
    async def observe(self, stream: AsyncIterator[str]) -> AsyncIterator[str]:
        """Yield chunks while recording metrics."""
        async for chunk in stream:
            if not self._first_token_received:
                self._first_token_received = True
                # Check first token timeout
                elapsed = (time.monotonic() - self.metrics._start_time) * 1000
                if elapsed > self.first_token_timeout_ms:
                    self.metrics.timeout_events.append({
                        "type": "first_token_timeout",
                        "elapsed_ms": elapsed,
                        "threshold_ms": self.first_token_timeout_ms,
                    })
            
            self.metrics.record_chunk(token_count=len(chunk.split()))
            
            # Check idle timeout
            if self.metrics.is_stalled(self.idle_timeout_ms):
                self.metrics.timeout_events.append({
                    "type": "idle_timeout",
                    "idle_ms": (time.monotonic() - self.metrics.last_token_time) * 1000,
                    "threshold_ms": self.idle_timeout_ms,
                })
                # Could trigger fallback here
            
            yield chunk
        
        # Log final metrics
        self._log_completion()
    
    def _log_completion(self) -> None:
        engine = get_engine()
        engine.log_event(
            EventType.MODEL_COMPLETED,
            self.metrics.trace_id,
            {
                "provider": self.metrics.provider,
                "model": self.metrics.model,
                "streaming": True,
                "ttft_ms": self.metrics.ttft_ms,
                "avg_inter_chunk_ms": self.metrics.avg_inter_chunk_ms,
                "max_inter_chunk_ms": self.metrics.max_inter_chunk_ms,
                "total_chunks": self.metrics.chunk_count,
                "total_tokens": self.metrics.total_tokens,
                "timeout_events": self.metrics.timeout_events,
            }
        )
```

**Provider-Specific Timeouts** (configurable in `config/providers.yaml`):
```yaml
providers:
  opencode:
    models:
      nemotron-3-ultra-free:
        streaming:
          first_token_timeout_ms: 60000   # 60s for slow start
          idle_timeout_ms: 300000         # 5 min idle (Nemotron is slow)
          fallback_on_timeout: true
          fallback_provider: "native-gguf"
```

---

### 4. Redis Streams for Agent Coordination (Replace File-Based Hivemind)

**Current State**: File-based Hivemind in `data/coordination/` with handoffs, locks, live feeds.

**Problem**: File-based coordination doesn't scale for 24/7 background pipeline with multiple concurrent agents.

**Solution**: Redis Streams for task-critical coordination, Pub/Sub for ephemeral heartbeats.

#### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    REDIS STREAMS TOPOLOGY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PRODUCERS                    CONSUMER GROUPS                   │
│  ────────                    ──────────────                    │
│  Ingestion Worker    ──▶      stream:amp:ingestion              │
│  Curation Worker     ──▶      stream:amp:curation               │
│  Scraping Worker     ──▶      stream:amp:scraping               │
│  Meditation Cycle    ──▶      stream:amp:meditation             │
│  Handoff Coordinator ──▶      stream:amp:handoffs               │
│                                                                 │
│  Each stream has consumer group "amp-workers" with              │
│  multiple consumers (worker-1, worker-2, ...)                   │
│                                                                 │
│  PUB/SUB (Ephemeral)                                            │
│  ─────────────────                                              │
│  channel: omega:hivemind:heartbeat     → Agent heartbeats       │
│  channel: omega:hivemind:live_feed     → Live feed deltas       │
│  channel: omega:hivemind:alerts        → Threshold alerts       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Stream Schema

```python
# src/omega/coordination/redis_streams.py
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import json
import time
import redis.asyncio as redis

STREAM_PREFIX = "amp"

@dataclass
class StreamEvent:
    """Base event for all AMP streams."""
    event_type: str
    trace_id: str
    timestamp_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    payload: Dict[str, Any] = field(default_factory=dict)
    source_agent: str = ""
    session_id: Optional[str] = None
    
    def to_stream_entry(self) -> Dict[str, str]:
        return {
            "event_type": self.event_type,
            "trace_id": self.trace_id,
            "timestamp_ms": str(self.timestamp_ms),
            "payload": json.dumps(self.payload),
            "source_agent": self.source_agent,
            "session_id": self.session_id or "",
        }

@dataclass 
class IngestionEvent(StreamEvent):
    event_type: str = "ingestion.completed"
    payload: Dict[str, Any] = field(default_factory=lambda: {
        "source_url": "",
        "content_hash": "",
        "word_count": 0,
        "status": "success",  # success, failed, partial
        "error": None,
    })

@dataclass
class HandoffEvent(StreamEvent):
    event_type: str = "handoff.submitted"
    payload: Dict[str, Any] = field(default_factory=lambda: {
        "target_agent": "",
        "task": "",
        "context": {},
        "priority": 0,
        "macp_mode": "task",  # D-292 MACP alignment
    })


class RedisStreamCoordinator:
    """Redis Streams coordinator for AMP agent coordination."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None
        self._consumer_groups: Dict[str, str] = {}  # stream -> group
    
    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self.redis_url, decode_responses=True)
        return self._client
    
    async def ensure_consumer_group(self, stream: str, group: str = "amp-workers") -> None:
        """Create consumer group if not exists (idempotent)."""
        try:
            await self.client.xgroup_create(f"{STREAM_PREFIX}:{stream}", group, id="0", mkstream=True)
        except redis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise
        self._consumer_groups[stream] = group
    
    async def publish(self, stream: str, event: StreamEvent) -> str:
        """Publish event to stream, return message ID."""
        await self.ensure_consumer_group(stream)
        msg_id = await self.client.xadd(
            f"{STREAM_PREFIX}:{stream}",
            event.to_stream_entry()
        )
        return msg_id
    
    async def consume(
        self, 
        stream: str, 
        consumer: str, 
        count: int = 10, 
        block_ms: int = 5000
    ) -> list:
        """Consume messages from stream (handles PEL recovery)."""
        await self.ensure_consumer_group(stream)
        group = self._consumer_groups[stream]
        
        # Phase 1: Process pending (PEL recovery) - STARTUP PATTERN
        pending = await self.client.xreadgroup(
            group, consumer, 
            {f"{STREAM_PREFIX}:{stream}": "0"},  # ID "0" = read PEL
            count=count
        )
        messages = []
        for stream_name, entries in pending:
            for msg_id, data in entries:
                messages.append((msg_id, data))
        
        # Phase 2: Read new messages
        if len(messages) < count:
            new_msgs = await self.client.xreadgroup(
                group, consumer,
                {f"{STREAM_PREFIX}:{stream}": ">"},
                count=count - len(messages),
                block=block_ms
            )
            for stream_name, entries in new_msgs:
                for msg_id, data in entries:
                    messages.append((msg_id, data))
        
        return messages
    
    async def ack(self, stream: str, msg_id: str) -> None:
        """Acknowledge processed message."""
        group = self._consumer_groups.get(stream, "amp-workers")
        await self.client.xack(f"{STREAM_PREFIX}:{stream}", group, msg_id)
    
    async def claim_stale(self, stream: str, consumer: str, min_idle_ms: int = 30000) -> list:
        """Claim stale messages from dead consumers (XAUTOCLAIM)."""
        group = self._consumer_groups.get(stream, "amp-workers")
        claimed = await self.client.xautoclaim(
            f"{STREAM_PREFIX}:{stream}", group, consumer,
            min_idle_time=min_idle_ms, start_id="0-0", count=100
        )
        return claimed[1]  # Returns list of (msg_id, data)
    
    async def trim_stream(self, stream: str, max_len: int = 10000) -> None:
        """Trim stream to prevent unbounded growth (XTRIM)."""
        await self.client.xtrim(f"{STREAM_PREFIX}:{stream}", maxlen=max_len, approximate=True)
    
    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
```

#### Graceful Degradation (M23)

```python
# src/omega/coordination/hivemind_hybrid.py
class HybridHivemindCoordinator:
    """
    Hybrid coordinator: Redis Streams primary, file-based fallback.
    M23: No soft failures — explicit degraded mode.
    """
    
    def __init__(self):
        self._redis: Optional[RedisStreamCoordinator] = None
        self._file_fallback = FileHivemindCoordinator()  # Existing implementation
        self._mode = "redis"  # "redis" | "file" | "unavailable"
    
    async def initialize(self) -> None:
        try:
            self._redis = RedisStreamCoordinator()
            await self._redis.client.ping()
            self._mode = "redis"
            logger.info("Hivemind: Redis Streams mode active")
        except (ConnectionError, OSError) as e:
            logger.warning(f"Hivemind: Redis unavailable ({e}), falling back to file-based")
            self._mode = "file"
    
    async def submit_handoff(self, handoff: HandoffPacket) -> str:
        if self._mode == "redis" and self._redis:
            try:
                event = HandoffEvent(
                    trace_id=handoff.trace_id,
                    source_agent=f"{handoff.source_channel}/{handoff.source_entity}",
                    payload={
                        "target_agent": f"{handoff.target_channel}/{handoff.target_entity}",
                        "task": handoff.task,
                        "context": handoff.context,
                        "priority": handoff.priority,
                        "macp_mode": handoff.macp_mode,
                    }
                )
                msg_id = await self._redis.publish("handoffs", event)
                return msg_id
            except (ConnectionError, OSError) as e:
                logger.error(f"Redis handoff failed, degrading to file: {e}")
                self._mode = "file"
        
        # File fallback (existing implementation)
        return await self._file_fallback.submit_handoff(handoff)
    
    @property
    def mode(self) -> str:
        return self._mode
    
    def is_degraded(self) -> bool:
        return self._mode == "file"
```

---

### 5. Health Monitoring (24/7 Background Processes)

**Requirements**:
- Background process health: Ingestion, Curation, Scraping, Meditation cycles
- Resource monitoring: CPU, memory, disk, GPU, thermal
- SLA tracking: Uptime, latency percentiles, error rates
- Alerting: Threshold-based + anomaly detection

```python
# src/omega/observability/health_monitor.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum
import time
import anyio
from omega.monitoring import HardwareMonitor

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class ComponentHealth:
    name: str
    status: HealthStatus = HealthStatus.UNKNOWN
    last_check: float = 0
    last_success: Optional[float] = None
    consecutive_failures: int = 0
    latency_p50_ms: float = 0
    latency_p95_ms: float = 0
    error_rate: float = 0
    metadata: Dict = field(default_factory=dict)

@dataclass
class SLAConfig:
    uptime_target: float = 99.9  # %
    latency_p95_target_ms: float = 5000
    error_rate_target: float = 0.01  # 1%
    check_interval_seconds: int = 60

class HealthMonitor:
    """24/7 health monitoring for AMP background processes."""
    
    def __init__(self, sla: SLAConfig = None):
        self.sla = sla or SLAConfig()
        self._components: Dict[str, ComponentHealth] = {}
        self._hardware = HardwareMonitor()
        self._checks: Dict[str, Callable] = {}
        self._running = False
        self._task_group: Optional[anyio.abc.TaskGroup] = None
    
    def register_component(self, name: str, check_fn: Callable, metadata: Dict = None) -> None:
        """Register a component with its health check function."""
        self._components[name] = ComponentHealth(name=name, metadata=metadata or {})
        self._checks[name] = check_fn
    
    async def start(self) -> None:
        """Start background health checking."""
        self._running = True
        async with anyio.create_task_group() as tg:
            self._task_group = tg
            tg.start_soon(self._check_loop)
            tg.start_soon(self._hardware_loop)
            tg.start_soon(self._sla_evaluation_loop)
    
    async def stop(self) -> None:
        self._running = False
        if self._task_group:
            self._task_group.cancel_scope.cancel()
    
    async def _check_loop(self) -> None:
        while self._running:
            for name, check_fn in self._checks.items():
                await self._run_check(name, check_fn)
            await anyio.sleep(self.sla.check_interval_seconds)
    
    async def _run_check(self, name: str, check_fn: Callable) -> None:
        comp = self._components[name]
        start = time.monotonic()
        try:
            result = await check_fn()
            latency_ms = (time.monotonic() - start) * 1000
            
            comp.status = HealthStatus.HEALTHY
            comp.last_success = time.time()
            comp.consecutive_failures = 0
            comp.metadata.update(result.get("metadata", {}))
            
            # Update latency percentiles (simplified - use MetricsDB for real percentiles)
            comp.latency_p50_ms = latency_ms  # Would use rolling window in production
            
        except Exception as e:
            comp.status = HealthStatus.UNHEALTHY
            comp.consecutive_failures += 1
            comp.metadata["last_error"] = str(e)
            comp.metadata["last_error_time"] = time.time()
            
            # Log to forensic ledger
            engine = get_engine()
            engine.log_event(
                EventType.ERROR,
                get_current_trace_id(),
                {
                    "component": name,
                    "error": str(e),
                    "consecutive_failures": comp.consecutive_failures,
                }
            )
        
        comp.last_check = time.monotonic()
    
    async def _hardware_loop(self) -> None:
        while self._running:
            hw_stats = self._hardware.collect_all()
            # Check thermal throttling
            if hw_stats.get("cpu", {}).get("thermal_throttling"):
                await self._alert("thermal_throttling", "CPU thermal throttling active", hw_stats)
            # Check OOM risk
            if hw_stats.get("memory", {}).get("oom_risk", {}).get("risk_level") in ("HIGH", "CRITICAL"):
                await self._alert("oom_risk", "High OOM risk detected", hw_stats)
            await anyio.sleep(30)  # Hardware check every 30s
    
    async def _sla_evaluation_loop(self) -> None:
        while self._running:
            await self._evaluate_slas()
            await anyio.sleep(300)  # SLA eval every 5 min
    
    async def _evaluate_slas(self) -> None:
        for name, comp in self._components.items():
            if comp.last_success:
                uptime = (time.time() - comp.last_success) / 3600  # hours since last success
                # Simplified - real impl would track over time windows
                if comp.consecutive_failures > 3:
                    comp.status = HealthStatus.UNHEALTHY
                elif comp.error_rate > self.sla.error_rate_target:
                    comp.status = HealthStatus.DEGRADED
    
    async def _alert(self, alert_type: str, message: str, context: Dict) -> None:
        engine = get_engine()
        trace_id = get_current_trace_id()
        engine.log_event(EventType.ESCALATION, trace_id, {
            "alert_type": alert_type,
            "message": message,
            "context": context,
        })
        # Also publish to Redis Pub/Sub for real-time alerting
        if hasattr(self, '_redis_pubsub'):
            await self._redis_pubsub.publish("alerts", json.dumps({
                "type": alert_type,
                "message": message,
                "timestamp": time.time(),
                "context": context,
            }))
    
    def get_health_report(self) -> Dict:
        return {
            "timestamp": time.time(),
            "overall_status": self._compute_overall_status(),
            "components": {name: {
                "status": comp.status.value,
                "last_check": comp.last_check,
                "last_success": comp.last_success,
                "consecutive_failures": comp.consecutive_failures,
                "latency_p50_ms": comp.latency_p50_ms,
                "error_rate": comp.error_rate,
                "metadata": comp.metadata,
            } for name, comp in self._components.items()},
            "hardware": self._hardware.collect_all(),
        }
    
    def _compute_overall_status(self) -> HealthStatus:
        if not self._components:
            return HealthStatus.UNKNOWN
        statuses = [c.status for c in self._components.values()]
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        return HealthStatus.UNKNOWN
```

**Component Health Checks** (to be registered):

| Component | Check Function | Frequency | SLA Target |
|-----------|---------------|-----------|------------|
| Ingestion Worker | HTTP HEAD on source URLs, queue depth | 60s | <5% failure, queue <1000 |
| Curation Pipeline | Vector index health, embedding latency | 60s | p95 <10s |
| Scraping Worker | Firecrawl/HTTP success rate, rate limit | 60s | <10% 429 |
| Meditation Cycle | LLM call success, lens execution time | 300s | p95 <60s |
| Redis Streams | XINFO GROUPS pending <100, consumer lag | 30s | lag <1000 |
| Model Gateway | Provider availability, circuit breaker state | 30s | >1 local provider healthy |

---

### 6. Forensic Logging & Audit Trail

**Current State**: 
- `UFLWriter` (Unified Forensic Ledger) in `src/omega/observability/ufl.py`
- `ForensicsManager` with crash dumps and death markers
- `BLEGMiddleware` for Silent 200 detection

**Enhancements for AMP**:

```python
# src/omega/observability/audit_trail.py
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
from enum import Enum
import json
import time

class AuditEventType(Enum):
    SOVEREIGN_DECISION = "sovereign.decision"      # Mandate enforcement, gate results
    AGENT_HANDOFF = "agent.handoff"                # Handoff submitted/accepted/completed
    STATE_CHANGE = "state.change"                  # Entity state transitions
    BOUNDARY_VIOLATION = "boundary.violation"      # M23 boundary violations
    RECURSION_GUARD = "recursion.guard"            # Entity depth exceeded
    HERITAGE_VET = "heritage.vet"                  # [id-soft:] tag verification
    TEMPLE_GATE = "temple.gate"                    # T1-T11 gate results
    SOUL_DISTILLATION = "soul.distillation"        # L1→L2→L3 distillation
    MIAP_EVENT = "miap.event"                      # Multi-instance protocol events

@dataclass
class AuditEntry:
    event_type: AuditEventType
    trace_id: str
    timestamp: float = field(default_factory=time.time)
    entity: str = ""           # Entity that generated the event
    session_id: str = ""       # Session context
    payload: Dict[str, Any] = field(default_factory=dict)
    # Tamper-evidence
    prev_hash: str = ""        # Hash of previous entry
    entry_hash: str = ""       # Hash of this entry
    
    def compute_hash(self) -> str:
        import hashlib
        data = json.dumps({
            "event_type": self.event_type.value,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "entity": self.entity,
            "session_id": self.session_id,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
        }, sort_keys=True).encode()
        return hashlib.sha256(data).hexdigest()[:32]


class AuditTrail:
    """Immutable, append-only audit trail with hash chaining."""
    
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._last_hash = self._load_last_hash()
    
    def _load_last_hash(self) -> str:
        if not self.path.exists():
            return "genesis"
        try:
            with open(self.path, "rb") as f:
                f.seek(-2048, 2)  # Read last 2KB
                lines = f.read().decode().strip().split('\n')
                if lines:
                    last = json.loads(lines[-1])
                    return last.get("entry_hash", "genesis")
        except Exception:
            pass
        return "genesis"
    
    async def append(self, entry: AuditEntry) -> str:
        entry.prev_hash = self._last_hash
        entry.entry_hash = entry.compute_hash()
        
        line = json.dumps(asdict(entry), default=str) + "\n"
        async with await anyio.open_file(self.path, "a") as f:
            await f.write(line)
            await f.flush()
        
        self._last_hash = entry.entry_hash
        return entry.entry_hash
    
    async def verify_chain(self) -> List[Dict]:
        """Verify hash chain integrity. Returns list of violations."""
        violations = []
        prev_hash = "genesis"
        async with await anyio.open_file(self.path, "r") as f:
            async for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    if entry["prev_hash"] != prev_hash:
                        violations.append({
                            "line": line_num,
                            "expected_prev": prev_hash,
                            "actual_prev": entry["prev_hash"],
                        })
                    # Recompute hash
                    computed = AuditEntry(**entry).compute_hash()
                    if computed != entry["entry_hash"]:
                        violations.append({
                            "line": line_num,
                            "type": "hash_mismatch",
                            "expected": computed,
                            "actual": entry["entry_hash"],
                        })
                    prev_hash = entry["entry_hash"]
                except Exception as e:
                    violations.append({"line": line_num, "error": str(e)})
        return violations
```

**Integration with Existing Systems**:
- `observability_log_boundary_violation` MCP tool → writes to AuditTrail
- `observability_check_recursion` MCP tool → writes to AuditTrail
- Temple-Grade gates (T1-T11) → write `TEMPLE_GATE` entries
- Heritage vet records → write `HERITAGE_VET` entries
- Soul distillation (M11) → write `SOUL_DISTILLATION` entries

---

### 7. Metrics Collection (M8 — Zero Telemetry)

**Current State**: `MetricsDB` in `src/omega/observability/metrics_db.py` with SQLite WAL mode.

**Requirements**:
- Prometheus-compatible exposition format for local Grafana
- Custom metrics: Inference latency, queue depth, soul distillation rate
- No external export (M8)

```python
# src/omega/observability/prometheus_exporter.py
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
from omega.observability.metrics_db import MetricsDB

# Custom registry (no default registry to avoid global state)
REGISTRY = CollectorRegistry()

# Inference metrics
INFERENCE_LATENCY = Histogram(
    'omega_inference_latency_seconds',
    'LLM inference latency in seconds',
    ['provider', 'model', 'is_cloud'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0],
    registry=REGISTRY
)

INFERENCE_TOKENS = Histogram(
    'omega_inference_tokens_total',
    'Token counts per inference',
    ['provider', 'model', 'direction'],  # direction: input/output
    registry=REGISTRY
)

INFERENCE_COST = Histogram(
    'omega_inference_cost_usd',
    'Inference cost in USD',
    ['provider', 'model'],
    registry=REGISTRY
)

# Queue metrics
QUEUE_DEPTH = Gauge(
    'omega_queue_depth',
    'Current queue depth',
    ['queue_name'],
    registry=REGISTRY
)

HANDOFF_PENDING = Gauge(
    'omega_handoff_pending',
    'Pending handoffs in Hivemind',
    ['target_agent'],
    registry=REGISTRY
)

# Soul metrics
SOUL_DISTILLATION_RATE = Counter(
    'omega_soul_distillations_total',
    'Total soul distillations performed',
    ['entity', 'level'],  # level: L1, L2, L3
    registry=REGISTRY
)

SOUL_LESSONS_PENDING = Gauge(
    'omega_soul_lessons_pending',
    'Lessons pending in proposed_lessons.yaml',
    ['entity'],
    registry=REGISTRY
)

# System metrics
ACTIVE_AGENTS = Gauge(
    'omega_active_agents',
    'Number of active agents in Hivemind',
    ['channel'],
    registry=REGISTRY
)

REDIS_STREAM_LAG = Gauge(
    'omega_redis_stream_lag',
    'Consumer lag in Redis Streams',
    ['stream', 'consumer_group'],
    registry=REGISTRY
)

class PrometheusMetricsExporter:
    """Exports MetricsDB data to Prometheus format for local Grafana."""
    
    def __init__(self, metrics_db: MetricsDB):
        self.db = metrics_db
    
    def update_from_db(self, hours: int = 1) -> None:
        """Pull recent metrics from MetricsDB and update Prometheus gauges."""
        # Query recent performance data
        perf_data = self.db.get_performance_trend(hours=hours)
        for row in perf_data:
            provider = row.get("provider", "unknown")
            model = row.get("model_used", "unknown")
            is_cloud = row.get("is_cloud", False)
            latency = row.get("latency_ms", 0) / 1000.0
            prompt_tokens = row.get("prompt_tokens", 0)
            completion_tokens = row.get("completion_tokens", 0)
            
            INFERENCE_LATENCY.labels(provider, model, str(is_cloud)).observe(latency)
            INFERENCE_TOKENS.labels(provider, model, "input").observe(prompt_tokens)
            INFERENCE_TOKENS.labels(provider, model, "output").observe(completion_tokens)
        
        # Update queue depths from Hivemind
        # (Would query Hivemind state here)
    
    def generate_metrics(self) -> bytes:
        """Generate Prometheus exposition format."""
        return generate_latest(REGISTRY)
```

**Grafana Dashboard Provisioning** (local-only):
```yaml
# config/grafana/dashboards/omega-amp.json
{
  "dashboard": {
    "title": "Omega AMP Observability",
    "panels": [
      {"title": "Inference Latency (p50/p95/p99)", "targets": [{"expr": "histogram_quantile(0.95, rate(omega_inference_latency_seconds_bucket[5m]))"}]},
      {"title": "Local vs Cloud Inference Ratio", "targets": [{"expr": "sum(rate(omega_inference_latency_seconds_count{is_cloud=\"false\"}[5m])) / sum(rate(omega_inference_latency_seconds_count[5m]))"}]},
      {"title": "Queue Depths", "targets": [{"expr": "omega_queue_depth"}]},
      {"title": "Handoff Pending", "targets": [{"expr": "omega_handoff_pending"}]},
      {"title": "Soul Distillation Rate", "targets": [{"expr": "rate(omega_soul_distillations_total[1h])"}]},
      {"title": "Active Agents", "targets": [{"expr": "omega_active_agents"}]},
      {"title": "Redis Stream Lag", "targets": [{"expr": "omega_redis_stream_lag"}]},
      {"title": "Hardware: CPU/Memory/OOM Risk", "targets": [{"expr": "omega_hardware_oom_risk"}]}
    ]
  }
}
```

---

## 🔗 Cross-Pillar Integration Points

| Pillar | Integration | Mechanism |
|--------|-------------|-----------|
| **P6 (Cognition)** | Provider routing provenance | `GenerateResult.provider_name` → M22 logging |
| **P7 (Context)** | Soul distillation metrics | `SOUL_DISTILLATION_RATE` counter, audit trail |
| **P9 (Orchestration)** | Agent handoff coordination | Redis Streams `amp:handoffs` + Hivemind hybrid |
| **P10 (Validation)** | Temple-Grade gate results | `TEMPLE_GATE` audit entries, regression detection |
| **P1 (Infrastructure)** | Hardware monitoring | `HardwareMonitor` → health checks, thermal alerts |
| **P2 (Persistence)** | Vector store metrics | `sqlite-vec` query latency, index health |
| **P3 (Engineering)** | CI/CD gate metrics | `make temple-grade` results → audit trail |
| **P4 (Integration)** | MCP Hub observability | Middleware trace injection, request/response logging |
| **P5 (Governance)** | Mandate compliance | `BOUNDARY_VIOLATION`, `RECURSION_GUARD` audit events |

---

## 📦 Implementation Phases

### Phase 1: Foundation (Week 1-2) — **CRITICAL PATH**

| Task | Owner | Dependencies | Deliverable |
|------|-------|--------------|-------------|
| 1.1 Structured logging with trace_id injection | P8 | `observability/context.py` | `structured_logging.py` |
| 1.2 Response provenance enforcement in ModelGateway | P8 + P6 | `providers.py`, `model_gateway.py` | M22-compliant logging |
| 1.3 Streaming observer for Nemotron timeout detection | P8 | `providers.py` streaming path | `streaming.py` with adaptive timeouts |
| 1.4 Prometheus metrics exporter + local Grafana | P8 | `metrics_db.py` | `prometheus_exporter.py`, dashboard JSON |
| 1.5 Audit trail with hash chaining | P8 | `ufl.py`, `forensics.py` | `audit_trail.py` |

**Gate**: `make test` passes, structured logs visible in JSONL, provenance verified in MetricsDB.

### Phase 2: Redis Streams Coordination (Week 2-3)

| Task | Owner | Dependencies | Deliverable |
|------|-------|--------------|-------------|
| 2.1 Redis Stream Coordinator implementation | P8 + P9 | `hivemind_redis.py` | `redis_streams.py` |
| 2.2 Hybrid Hivemind (Redis primary, file fallback) | P8 + P9 | Phase 2.1, existing Hivemind | `hivemind_hybrid.py` |
| 2.3 Migrate handoffs to Redis Streams | P9 | Phase 2.2 | Updated handoff tools |
| 2.4 Consumer group management + PEL recovery | P8 | Phase 2.1 | Startup recovery tests |
| 2.5 Stream trimming + memory management | P8 | Phase 2.1 | `XTRIM` automation |

**Gate**: Handoffs work in Redis mode, graceful degradation to file tested, PEL recovery verified.

### Phase 3: Health Monitoring & Alerting (Week 3-4)

| Task | Owner | Dependencies | Deliverable |
|------|-------|--------------|-------------|
| 3.1 HealthMonitor with component registration | P8 | `monitoring/hardware.py` | `health_monitor.py` |
| 3.2 AMP component health checks (ingestion, curation, etc.) | P8 + P1/P2/P3 | Phase 3.1 | Check functions registered |
| 3.3 SLA evaluation + alerting to Redis Pub/Sub | P8 | Phase 3.1 | Alert rules, Pub/Sub publishing |
| 3.4 Grafana alerting rules + notification (ntfy) | P8 | Phase 1.4, 3.3 | Alert rules YAML |
| 3.5 24/7 background process supervision | P1 + P8 | Phase 3.1 | Systemd/Quadlet integration |

**Gate**: Health report API returns component status, alerts fire on threshold breach.

### Phase 4: Forensic Hardening & Temple-Grade (Week 4-5)

| Task | Owner | Dependencies | Deliverable |
|------|-------|--------------|-------------|
| 4.1 Crash dump integration with AuditTrail | P8 | Phase 1.5, `forensics.py` | Crash dumps → audit entries |
| 4.2 Boundary violation logging → AuditTrail | P5 + P8 | `observability_log_boundary_violation` | M23 compliance |
| 4.3 Recursion guard → AuditTrail | P5 + P8 | `observability_check_recursion` | M17 compliance |
| 4.4 Temple-Grade gate results → AuditTrail | P3 + P8 | `make temple-grade` | T1-T11 audit entries |
| 4.5 Heritage vet verification → AuditTrail | P5 + P8 | `make heritage-map` | M14 compliance |
| 4.6 `make temple-grade` passes with new observability | P8 | All above | Full compliance |

**Gate**: `make temple-grade` passes, audit trail verified, crash recovery tested.

### Phase 5: Integration & Documentation (Week 5-6)

| Task | Owner | Dependencies | Deliverable |
|------|-------|--------------|-------------|
| 5.1 P6/P7/P9/P10 integration testing | All | Phases 1-4 | Cross-pillar test suite |
| 5.2 AMP end-to-end observability validation | P8 | Phase 5.1 | 24h soak test report |
| 5.3 Documentation: Runbooks, dashboards, alerts | P8 | All | `docs/operations/AMP_OBSERVABILITY.md` |
| 5.4 Sovereignty scorecard automation | P8 + P7 | Phase 1.2 | Daily sovereignty report |

---

## ⚠️ Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Redis unavailable in production | Medium | High | Hybrid mode (file fallback) mandatory, M23 explicit degraded mode |
| Nemotron timeout detection false positives | High | Medium | Configurable thresholds per model, fallback chain tested |
| MetricsDB write contention under load | Low | Medium | WAL mode, batch inserts, connection pooling |
| Audit trail hash chain corruption | Very Low | Critical | Periodic verification job, append-only files |
| Grafana OOM at high log volume | Medium | Medium | Loki ingestion limits tuned (see Markaicode 2026 guide) |
| Trace ID loss across async boundaries | Low | High | `contextvars` safety net in `context.py`, mandatory at entry points |
| Sovereignty scorecard inaccuracy | Low | High | M22 provenance at response receipt, not dispatch |

---

## 📊 Resource Estimates

| Resource | Estimate | Notes |
|----------|----------|-------|
| **Development Time** | 6 weeks (1 engineer) | Phases 1-5, can parallelize P8+P9 |
| **Redis Memory** | 512MB - 2GB | Streams + consumer groups, depends on retention |
| **MetricsDB Storage** | ~17GB/15 days | 10K series, 15s scrape (Prometheus formula) |
| **Audit Trail Storage** | ~1GB/month | JSONL with hash chains, compressible |
| **Grafana/Loki Stack** | 6-11GB RAM | Idle 6.2GB, 10K logs/sec peak 11.3GB (Markaicode 2026) |
| **CPU Overhead** | <5% | Structured logging + metrics collection |

---

## ✅ Temple-Grade Gate Compliance (T1-T11)

| Gate | Requirement | P8 Implementation |
|------|-------------|-------------------|
| **T1** Version Control | All observability code in git | ✅ This strategy + implementation in `src/omega/observability/` |
| **T2** Documentation | Runbooks, dashboards, APIs documented | Phase 5.3 deliverable |
| **T3** Testing | ≥80% coverage, contract tests | Phase 1-4 unit/integration tests |
| **T4** Code Quality | `make lint` passes, type hints | Enforced in CI |
| **T5** Architecture | Engine-Stack Firewall (M2) | No WAD-specific logic in `src/omega/observability/` |
| **T6** Security | Zero telemetry (M8), local-only | No external exporters, `OMEGA_ENV=test` isolation |
| **T7** Performance | <5% overhead, p95 latency targets | Benchmarked in Phase 5.2 |
| **T8** Resilience | Graceful degradation (M23), crash recovery | Hybrid Hivemind, ForensicsManager |
| **T9** Observability | Structured logs, metrics, traces | This entire strategy |
| **T10** Integrity | Atomic writes, hash chains | AuditTrail, `os.replace()`, MetricsDB WAL |
| **T11** Agent Security | Boundary violations logged | `observability_log_boundary_violation` → AuditTrail |

---

## 🏷️ Heritage Attribution

| Pattern | Source | Tag |
|---------|--------|-----|
| Redis Streams consumer groups | Redis 5.0+ (2018) | `[heritage: redis-2018] Streams Consumer Groups` |
| PEL (Pending Entries List) recovery | Redis Streams design | `[heritage: redis-2018] PEL Recovery Pattern` |
| XAUTOCLAIM for stale messages | Redis 6.2+ | `[heritage: redis-2020] XAUTOCLAIM` |
| Structured logging with trace_id | Google Dapper (2010) / OpenTelemetry | `[heritage: opentelemetry-2019] Trace Context Propagation` |
| OpenTelemetry GenAI semantic conventions | OTel GenAI SIG (2024-2026) | `[heritage: opentelemetry-genai-2026] GenAI Semantic Conventions` |
| Prometheus exposition format | Prometheus (2012) | `[heritage: prometheus-2012] Metrics Exposition` |
| Loki log aggregation | Grafana Labs (2019) | `[heritage: grafana-loki-2019] Log Aggregation` |
| Crash dump / last-gasp forensics | Linux kernel kdump / Windows WER | `[heritage: linux-kdump-2005] Crash Forensics` |
| Hash-chained audit trail | Bitcoin blockchain (2008) / Certificate Transparency | `[heritage: bitcoin-2008] Hash Chain Integrity` |

---

## 📝 Deliverable Checklist

- [ ] `docs/strategy/PILLAR_P8_OBSERVABILITY_STRATEGY_20260719.md` (this document)
- [ ] `src/omega/observability/structured_logging.py`
- [ ] `src/omega/observability/streaming.py`
- [ ] `src/omega/observability/prometheus_exporter.py`
- [ ] `src/omega/observability/audit_trail.py`
- [ ] `src/omega/observability/health_monitor.py`
- [ ] `src/omega/coordination/redis_streams.py`
- [ ] `src/omega/coordination/hivemind_hybrid.py`
- [ ] `config/grafana/dashboards/omega-amp.json`
- [ ] `config/grafana/alerting/amp-alerts.yaml`
- [ ] `docs/operations/AMP_OBSERVABILITY.md`
- [ ] Integration tests in `tests/observability/`
- [ ] `make temple-grade` passes with new components

---

## 🧘 Meditation Review (Post-Strategy)

> **`/meditate "P8 Observability Strategy for Autonomous Meditation Pipeline" --lenses engineering_excellence,provenance,decision,edge,scribe --iwad arcana_novai`**

This strategy will be hardened through the Meditate pipeline using the Scribe lens for documentation quality, the Provenance lens for M22 compliance verification, the Decision lens for architectural trade-off validation, the Edge lens for failure mode analysis, and the Engineering Excellence lens for Temple-Grade adherence.

---

*⬡ OMEGA ⬡ PILLAR P8 ⬡ WATCHTOWER ⬡ STRATEGY COMPLETE ⬡*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: P8 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

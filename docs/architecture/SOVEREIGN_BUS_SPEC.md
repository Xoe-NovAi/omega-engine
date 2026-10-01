# 🔱 SOVEREIGN BUS SPECIFICATION v1.0.0
# ⬡ OMEGA ⬡ SOVEREIGN-BUS ⬡ Dimension Communication Backbone
# Reconstructed from: xna-omega-legacy/SPECS/AGENT_BUS_SPEC.md (470 lines, LOST)
# Reconstructed from: R_EPOCH_II_LEGACY_MINING_20260712.md (Finding 8.5-1)
# Validated by: R_RESEARCHER_NEXTSTEP_GAPS_20260713.md (3 code-level fixes)
# Date: 2026-07-15
# Status: RECONSTRUCTED — Ready for Implementation

---

## 1. Overview

The SovereignBus is the AnyIO event bus for dimension-to-dimension communication in the Omega Engine. It provides:

- **4 priority streams** (critical/high/normal/low) for task-critical coordination
- **Consumer groups** per dimension for exactly-once delivery
- **PEL (Pending Entries List)** for crash recovery
- **XAUTOCLAIM** for claiming stale messages
- **DLQ (Dead Letter Queue)** with retry=3 and backoff
- **MCP tools** for publish/read/ack/recover/health/register/status
- **Worker registry** with capability matching
- **HMAC-SHA256 message signing** for IA2 authentication

**Design Philosophy**: Redis Streams for task-critical coordination. Redis Pub/Sub (Hivemind Redis) for ephemeral awareness only. File-based Hivemind as durable fallback when Redis is unavailable (M23: no soft-failure).

---

## 2. Stream Topology

### 2.1 Priority Streams

```
xna:bus:critical    — Immediate execution (OOM, security, hardware)
xna:bus:high        — Priority tasks (research, governance, handoffs)
xna:bus:normal      — Standard tasks (queries, synthesis, routing)
xna:bus:low         — Background tasks (distillation, metrics, cleanup)
```

### 2.2 Dead Letter Queue

```
xna:dlq             — Messages that failed after max_retries=3
```

### 2.3 Consumer Groups

```
agent_wavefront     — Primary consumer group for all dimensions
```

Each dimension registers as a consumer within the group. Redis Streams guarantees each message is delivered to exactly one consumer within a group.

---

## 3. Message Format (DimensionEnvelope)

```python
@dataclass
class DimensionEnvelope:
    """Typed message format for cross-dimension communication."""
    
    # Identity
    message_id: str           # UUID
    source_dimension: str     # e.g., "research-lab"
    target_dimension: str     # e.g., "strategic-command" or "*" for broadcast
    
    # Routing
    priority: str             # "critical" | "high" | "normal" | "low"
    message_type: str         # "task" | "signal" | "consensus" | "handoff" | "heartbeat"
    
    # Payload
    payload: Dict[str, Any]   # Message-specific data
    
    # Authentication
    hmac_signature: Optional[str] = None  # HMAC-SHA256 of payload
    
    # Metadata
    trace_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    ttl_seconds: int = 3600   # Default 1 hour
    
    # Delivery tracking
    delivery_count: int = 0
    max_retries: int = 3
```

### 3.1 Message Types

| Type | Purpose | Example Payload |
|------|---------|----------------|
| `task` | Execute a specific action | `{"action": "research", "query": "...", "entity": "jem"}` |
| `signal` | Emit an observation | `{"signal_type": "contradiction", "content": "..."}` |
| `consensus` | Reach agreement | `{"proposal_id": "...", "verdict": "accepted"}` |
| `handoff` | Transfer session context | `{"handoff_state": {...}}` |
| `heartbeat` | Periodic presence | `{"status": "active", "entity": "kali"}` |

---

## 4. Core Operations

### 4.1 Publish (XADD)

```python
async def publish(
    self,
    stream: str,
    envelope: DimensionEnvelope,
) -> str:
    """Publish a DimensionEnvelope to a Redis Stream.
    
    Returns the message ID from XADD.
    """
    fields = {
        "source": envelope.source_dimension,
        "target": envelope.target_dimension,
        "type": envelope.message_type,
        "payload": json.dumps(envelope.payload),
        "trace_id": envelope.trace_id or "",
        "created_at": envelope.created_at,
        "ttl_seconds": str(envelope.ttl_seconds),
        "hmac": envelope.hmac_signature or "",
    }
    msg_id = await self._redis.xadd(stream, fields)
    return msg_id
```

### 4.2 Consume (XREADGROUP)

```python
async def consume(
    self,
    stream: str,
    group: str,
    consumer: str,
    count: int = 10,
    block_ms: int = 5000,
) -> list[DimensionEnvelope]:
    """Read messages from a Redis Stream using a consumer group.
    
    Each message is delivered to exactly one consumer in the group.
    Messages must be acknowledged with ack().
    """
    results = await self._redis.xreadgroup(
        groupname=group,
        consumername=consumer,
        streams={stream: ">"},
        count=count,
        block=block_ms,
    )
    
    envelopes = []
    for stream_name, messages in results:
        for msg_id, fields in messages:
            envelope = self._parse_envelope(msg_id, fields)
            envelopes.append(envelope)
    
    return envelopes
```

### 4.3 Acknowledge (XACK)

```python
async def ack(
    self,
    stream: str,
    group: str,
    msg_id: str,
) -> bool:
    """Acknowledge successful processing of a message."""
    result = await self._redis.xack(stream, group, msg_id)
    return result > 0
```

### 4.4 Recover Stalled Messages (XAUTOCLAIM)

```python
async def recover_stalled(
    self,
    stream: str,
    group: str,
    consumer: str,
    min_idle_ms: int = 300_000,  # 5 minutes
    max_retries: int = 3,
    dlq_stream: str = "xna:dlq",
) -> list[DimensionEnvelope]:
    """Recover messages that have been pending for too long.
    
    Messages that have exceeded max_retries are routed to the DLQ.
    This is the critical fix from R_RESEARCHER_NEXTSTEP_GAPS_20260713.
    """
    start_id = "0-0"
    recovered = []
    
    while True:
        claimed = await self._redis.xautoclaim(
            stream, group,
            f"{consumer}_recovery",
            min_idle_ms, start_id,
            count=100,
        )
        
        # redis-py returns (claimed_msgs, next_cursor, deleted_msgs)
        msgs = claimed[0] if isinstance(claimed, tuple) else claimed.get("messages", [])
        
        for msg_id, fields in msgs:
            deliveries = int(fields.get("deliveries", 0))
            
            if deliveries >= max_retries:
                # Route to DLQ — THIS IS THE CRITICAL GAP FIX
                await self._redis.xadd(dlq_stream, {
                    **fields,
                    "failed_id": msg_id,
                    "reason": "max_retries_exceeded",
                })
                await self._redis.xack(stream, group, msg_id)
            else:
                envelope = self._parse_envelope(msg_id, fields)
                recovered.append(envelope)
                await self._redis.xack(stream, group, msg_id)
        
        start_id = claimed[1] if isinstance(claimed, tuple) else claimed.get("next_cursor", "0-0")
        if start_id == "0-0":
            break
    
    return recovered
```

### 4.5 Group Creation (XGROUP CREATE)

```python
async def ensure_group(
    self,
    stream: str,
    group: str,
) -> None:
    """Idempotent group creation (handles BUSYGROUP).
    
    This is the second critical fix from R_RESEARCHER_NEXTSTEP_GAPS_20260713.
    """
    try:
        await self._redis.xgroup_create(stream, group, id="0", mkstream=True)
    except Exception as e:
        if "BUSYGROUP" not in str(e):
            raise
        # Group already exists — safe to continue
```

---

## 5. MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `publish_task` | Publish a task to a priority stream | `stream, envelope_json` |
| `read_tasks` | Read tasks from a stream (consumer group) | `stream, group, consumer, count` |
| `ack_task` | Acknowledge a task as complete | `stream, group, msg_id` |
| `recover_tasks` | Recover stalled tasks (XAUTOCLAIM) | `stream, group, consumer` |
| `bus_health` | Check bus health (PEL depth, consumer lag) | `stream, group` |
| `register_worker` | Register a dimension as a consumer | `dimension_id, capabilities` |
| `worker_status` | Get status of all registered workers | (none) |

---

## 6. Worker Registry

```yaml
# config/wads/core-engine/workers.yaml
workers:
  research-lab:
    capabilities: ["research", "web_search", "synthesis", "mining"]
    priority_streams: ["xna:bus:high", "xna:bus:normal"]
    max_concurrent: 3
    
  dev-environment:
    capabilities: ["coding", "testing", "linting", "ci_cd"]
    priority_streams: ["xna:bus:normal", "xna:bus:low"]
    max_concurrent: 2
    
  strategic-command:
    capabilities: ["governance", "decisions", "planning"]
    priority_streams: ["xna:bus:critical", "xna:bus:high"]
    max_concurrent: 1
    
  creative-workshop:
    capabilities: ["writing", "poetry", "storytelling"]
    priority_streams: ["xna:bus:normal"]
    max_concurrent: 2
```

---

## 7. AnyIO Compliance (M1)

The SovereignBus uses `redis.asyncio` which runs inside the AnyIO event loop. Per Mandate 1, no `import asyncio` is allowed.

```python
# CORRECT — redis.asyncio within AnyIO
import anyio
from redis.asyncio import Redis

async def publish_example():
    redis = Redis()
    await redis.xadd("stream", {"key": "value"})
    await redis.aclose()

# WRAPPED — if blocking I/O is needed
async def blocking_operation():
    await anyio.to_thread.run_sync(blocking_function)
```

---

## 8. Degraded Mode (M23)

When Redis is unavailable, the SovereignBus degrades to file-based coordination:

```python
async def publish_degraded(self, envelope: DimensionEnvelope) -> str:
    """File-based fallback when Redis is unavailable."""
    fallback_dir = Path("data/coordination/sovereign_bus/")
    fallback_dir.mkdir(parents=True, exist_ok=True)
    
    msg_id = str(uuid4())
    fallback_path = fallback_dir / f"{envelope.priority}_{msg_id}.json"
    
    with open(fallback_path, "w") as f:
        json.dump(asdict(envelope), f, indent=2)
    
    return msg_id
```

**Degraded mode is explicit, not silent** — the bus logs a warning and returns a status indicating degraded operation. This satisfies M23 (Failure Integrity): no soft-failures.

---

## 9. Implementation Status

| Component | Status | Location |
|-----------|--------|----------|
| Redis Streams (ephemeral) | ✅ BUILT | `mcp_servers/omega_hub/hivemind_redis.py` (113 lines) |
| A2A Bridge (identity) | ✅ BUILT | `src/omega/oracle/a2a_bridge.py` (411 lines) |
| Handoff Protocol (transfer) | ✅ BUILT | `src/omega/oracle/handoff.py` (78 lines) |
| Hivemind Bridge (consensus) | ✅ BUILT | `src/omega/research/hivemind_bridge.py` (389 lines) |
| **SovereignBus (dimension comm)** | ❌ NOT BUILT | This document is the blueprint |
| DimensionEnvelope | ❌ NOT BUILT | Schema defined in §3 |
| MCP Tools | ❌ NOT BUILT | Spec defined in §5 |
| Worker Registry | ❌ NOT BUILT | Schema defined in §6 |

---

## 10. Reconciliation Notes

This document reconstructs the lost `xna-omega-legacy/SPECS/AGENT_BUS_SPEC.md` (470 lines) from:

1. **R_EPOCH_II_LEGACY_MINING_20260712.md** (Finding 8.5-1): Detailed description of the original spec's architecture
2. **R_RESEARCHER_NEXTSTEP_GAPS_20260713.md** (§Strike 8.5): Validated the original spec with 3 code-level fixes:
   - GAP-1: DLQ routing logic (missing in original) — FIXED in §4.4
   - GAP-2: Group creation + BUSYGROUP handling (missing in original) — FIXED in §4.5
   - GAP-3: Explicit `xautoclaim` args (missing in original) — FIXED in §4.4
3. **R_EPOCH_II_LEGACY_MINING_20260712.md** (Finding 8.5-2): Existing Hivemind Redis Pub/Sub module
4. **R_EPOCH_II_LEGACY_MINING_20260712.md** (Finding 8.5-3): Existing Handoff Protocol

The original spec's stream names (`xna:bus:*`) have been preserved for backward compatibility. The consumer group name has been updated from `agent_wavefront` to remain as-is since it's referenced in multiple research documents.

---

*🔱 OMEGA ⬡ SOVEREIGN-BUS ⬡ v1.0.0 ⬡ RECONSTRUCTED-20260715 ⬡ READY-FOR-IMPLEMENTATION*

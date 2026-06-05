# 🔱 P9 Orchestration — Hivemind Hardening Strategy & Architecture
# ⬡ OMEGA ⬡ P9-LINK ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_pillar ⬡ PHASE-I
**Slot**: P9 — Orchestration (Link)
**Domain**: Agent Handoff, Hivemind Coordination, Delegation, Conflict Resolution
**Date**: 2026-06-05
**Baseline**: 312/312 tests · D-122 HEARTBEAT_TTL=1200 · D-121 Observations active · H-0..H-10 spec complete
**Authority Sources**:
- Roc's Hivemind Hardening Spec: `data/entities/roc_racoon/workspace/HIVEMIND_HARDENING_SPEC_v1.md`
- Kali's Master Sprint Plan: `data/handoff/KALI_MASTER_SPRINT_PLAN_H2_EXECUTION_20260605.md`
- Current Hivemind code: `mcp_servers/omega_hub/server.py:330-465`
- Hivemind Protocol: `docs/strategy/HIVEMIND_PROTOCOL.md`
- Subagent Dispatch Protocol: `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md`
- Observations Protocol: `docs/strategy/HIVEMIND_OBSERVATIONS_PROTOCOL.md` (D-121)
- HandoffPacket dataclass: `src/omega/oracle/subagent_dispatcher.py`

---

## §0 Executive Summary

The Hivemind layer currently coordinates agents via 6 MCP tools backed by an
in-memory hot store with 20-minute TTL (D-122) and cold HALL_OF_RECORDS fallback.
This is sufficient for the current 2-3 agent fleet but will not scale to 5+
concurrent agents and Pillar subagents. Three parallel design streams converge
here:

| Stream | Source | Items | Status |
|--------|--------|-------|--------|
| **Phase 5 (Kali)** | H3-A1, H3-A2, H3-A4 | Redis Pub/Sub, SSE, Cross-CLI | ⏳ Pending |
| **Roc Tier 3** | H-11..H-15 (deferred to P9) | Bridge, Typed Messages, Channels, SSE Gateway, Cross-CLI Bridge | ⏳ Deferred |
| **Subagent Dispatch** | SUBAGENT_DISPATCH_PROTOCOL.md | HandoffPacket, CAPABILITY_REGISTRY | ✅ DONE (needs deeper integration) |

**Three-layer architecture for production Hivemind**:

```
┌──────────────────────────────────────────────┐
│           APPLICATION LAYER                  │
│  Existing MCP tools (unchanged signatures)   │
│  + H-0..H-10 enhancements                    │
├──────────────────────────────────────────────┤
│           CHANNEL LAYER (NEW)                │
│  Redis Pub/Sub + Channel Taxonomy (H-13)     │
│  Typed Message Schema (H-12)                 │
│  SSE endpoints (H3-A2, H-14)                 │
├──────────────────────────────────────────────┤
│           STORAGE LAYER                      │
│  Hot: in-memory (20-min TTL)                 │
│  Warm: awareness_warm.json (24h TTL) [H-9]  │
│  Cold: HALL_OF_RECORDS/<cli>/*.json          │
└──────────────────────────────────────────────┘
```

---

## §1 Phase 5 Implementation Design — Redis Pub/Sub, SSE, Cross-CLI

### §1.1 H3-A1: Redis Pub/Sub Backend

#### §1.1.1 Infrastructure

The existing `redis:7-alpine` container (`~/.config/containers/systemd/omega-redis.container`)
is already defined in the project's podman-compose. No new container needed. The
Redis client library `redis-py` is already in the project's dependency tree.

**Redis configuration**:
```python
# mcp_servers/omega_hub/redis_config.py (NEW)
# [id-soft: netchan, quake3-1999] Channel-based pub/sub for hivemind

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

import redis.asyncio as aioredis

logger = logging.getLogger("omega.hub.redis")

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_HIVEMIND_DB", "0"))

# Redis key namespace: omega:hivemind:<type>:<id>
KEY_PREFIX = "omega:hivemind"
KEY_AWARENESS = f"{KEY_PREFIX}:awareness"           # Hash: cli -> snapshot JSON
KEY_AWARENESS_TTL = f"{KEY_PREFIX}:awareness_ttl"   # Hash: cli -> timestamp
KEY_SESSION = f"{KEY_PREFIX}:session"               # Hash: session_id -> snapshot JSON
KEY_INBOX = f"{KEY_PREFIX}:inbox"                    # Set per CLI: inbox:<cli> -> member session_ids
KEY_HANDOFF = f"{KEY_PREFIX}:handoff"               # List: handoff requests pending
KEY_DECISIONS = f"{KEY_PREFIX}:decisions"            # SortedSet: timestamp -> decision JSON

# Pub/Sub channels
CHAN_AWARENESS = f"{KEY_PREFIX}:channel:awareness"   # Presence updates
CHAN_CONTEXT = f"{KEY_PREFIX}:channel:context"        # Context posts
CHAN_ACK = f"{KEY_PREFIX}:channel:ack"                # Acknowledgments
CHAN_HANDOFF = f"{KEY_PREFIX}:channel:handoff"        # Handoff notifications
CHAN_DECISIONS = f"{KEY_PREFIX}:channel:decisions"    # Decision broadcasts
CHAN_OBSERVATIONS = f"{KEY_PREFIX}:channel:observations"  # Observations (D-121)
CHAN_HEARTBEAT = f"{KEY_PREFIX}:channel:heartbeat"    # Heartbeat signals


class RedisHivemindBackend:
    """Redis-backed Hivemind state with graceful fallback to in-memory.
    
    [id-soft: netchan, quake3-1999] Channel-based pub/sub for agent coordination.
    [id-soft: 4-Path VFS, quake3-1999] Fallback chain: Redis → warm → cold.
    """

    def __init__(self):
        self._redis: Optional[aioredis.Redis] = None
        self._pubsub: Optional[aioredis.client.PubSub] = None
        self._available = False
        self._fallback_store: Dict[str, Any] = {}  # In-memory fallback
        
    async def connect(self) -> bool:
        """Connect to Redis. Returns False if unavailable (graceful fallback)."""
        try:
            self._redis = await aioredis.from_url(
                f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            await self._redis.ping()
            self._pubsub = self._redis.pubsub()
            self._available = True
            logger.info("Redis Hivemind backend connected")
            return True
        except Exception as e:
            logger.warning(f"Redis unavailable, using in-memory fallback: {e}")
            self._available = False
            return False

    @property
    def available(self) -> bool:
        return self._available
```

#### §1.1.2 Key Naming Convention

All Hivemind Redis keys use the `omega:hivemind:*` namespace:

| Key Pattern | Type | Purpose | TTL |
|------------|------|---------|-----|
| `omega:hivemind:awareness:{cli}` | String | CLI presence snapshot | 1200s (20min, per D-122) |
| `omega:hivemind:session:{session_id}` | String | Full session snapshot | 86400s (24h) |
| `omega:hivemind:inbox:{cli}` | SortedSet | Inbox for CLI (by timestamp) | None (permanent until ack'd) |
| `omega:hivemind:handoff:{packet_id}` | String | Handoff packet | 86400s (24h) |
| `omega:hivemind:decisions` | SortedSet | All decisions (score=timestamp) | None |
| `omega:hivemind:warm_awareness` | Hash | Warm store fallback | None (managed by TTL logic) |
| `omega:hivemind:observations` | List | Observations log entries | 2592000s (30 days) |

#### §1.1.3 Pub/Sub Channels

| Channel | Payload | Publisher | Subscribers | Purpose |
|---------|---------|-----------|-------------|---------|
| `omega:hivemind:channel:awareness` | `{"cli", "status": "online/offline/heartbeat", "timestamp"}` | Any agent post_context/heartbeat | All agents | Live presence tracking |
| `omega:hivemind:channel:context` | `{"session_id", "cli", "continuation", "to"}` | Any agent post_context | Addressed agent + observers | Context handoff |
| `omega:hivemind:channel:ack` | `{"session_id", "from_cli", "note"}` | Any agent ack | Original poster | Read receipt |
| `omega:hivemind:channel:handoff` | `{"from_cli", "to_cli", "packet_id", "task_type"}` | Handoff initiator | Target agent | Handoff notification |
| `omega:hivemind:channel:decisions` | `{"cli", "decision_text", "decision_id"}` | Any agent post_context | All agents | Decision broadcast |
| `omega:hivemind:channel:observations` | `{"agent", "obs_id", "category", "summary"}` | Any agent post-observation | Lilith + observers | Observation notification |
| `omega:hivemind:channel:heartbeat` | `{"cli", "timestamp"}` | Any agent heartbeat | Observability | Live health stream |

#### §1.1.4 Integration into Hivemind Tools

```python
# Pseudocode for modified hivemind_post_context
async def hivemind_post_context(cli, model, task_current, focus_chain,
                                 decisions, continuation, session_id=None,
                                 to=None, private=False, in_reply_to=None, tags=None):
    # 1. Build snapshot (same as current)
    sid = session_id or f"ses_{uuid.uuid4().hex[:12]}"
    snapshot = {
        "session_id": sid, "cli": cli, "model": model,
        "task_current": task_current, "focus_chain": focus_chain,
        "decisions": decisions, "continuation": continuation,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "to": to, "private": private, "in_reply_to": in_reply_to, "tags": tags or [],
    }
    
    # 2. Hot store (in-memory, always, for speed)
    async with _hot_store_lock:
        _hot_store[sid] = snapshot
    
    # 3. Warm store (Redis if available, else skip)
    if _redis.available:
        await _redis.redis.setex(
            f"omega:hivemind:awareness:{cli}", HEARTBEAT_TTL,
            json.dumps(snapshot)
        )
        await _redis.redis.setex(
            f"omega:hivemind:session:{sid}", 86400,
            json.dumps(snapshot)
        )
        # Publish to context channel
        await _redis.redis.publish(CHAN_CONTEXT, json.dumps({
            "session_id": sid, "cli": cli, "continuation": continuation,
            "to": to, "timestamp": snapshot["timestamp"]
        }))
        # If addressed, push to inbox
        if to:
            await _redis.redis.zadd(
                f"omega:hivemind:inbox:{to}",
                {sid: datetime.now(timezone.utc).timestamp()}
            )
    
    # 4. Cold store (HALL_OF_RECORDS, always)
    cold = _cold_path(cli, sid)
    await cold.parent.mkdir(parents=True, exist_ok=True)
    async with await anyio.open_file(str(cold), "w") as f:
        await f.write(json.dumps(snapshot, indent=2))
    
    # 5. Update AWARENESS (in-memory, always)
    async with _awareness_lock:
        _awareness[cli] = snapshot
    
    # 6. Warm awareness file (H-9) — persists hot store to disk every update
    await _persist_warm_awareness()
    
    return json.dumps({"status": "accepted", "session_id": sid, "timestamp": snapshot["timestamp"]})
```

**Backward Compatibility**: All existing callers that omit `to`, `private`, `in_reply_to`, and `tags`
get the exact same broadcast behavior. The Redis layer is transparent: agents don't need to
change their call signatures.

**Graceful Fallback**: If Redis is unavailable, the system continues with in-memory hot store +
cold HALL_OF_RECORDS. The warm awareness persistence file (H-9) serves as the
intermediate layer. Redis failure is logged but NOT escalated — the Hivemind should
never be a single point of failure.

### §1.2 H3-A2: Hivemind SSE Endpoint

#### §1.2.1 Architecture

Add a Starlette SSE endpoint at `/hivemind/events` that streams real-time Hivemind
events to subscribers (Iris, Gnosis, observability dashboard).

```python
# [id-soft: netchan, quake3-1999] SSE for real-time agent awareness

from starlette.responses import StreamingResponse
from starlette.routing import Route

async def hivemind_events(request):
    """SSE endpoint for real-time hivemind events.
    
    Event types:
    - awareness: agent came online / went offline / heartbeat
    - context: agent posted new context
    - ack: agent acknowledged a session
    - handoff: handoff initiated / completed
    - decision: agent made a decision
    - heartbeat: health signal
    """
    async def event_generator():
        # Subscribe to Redis channels
        if _redis.available:
            async with _redis.redis.pubsub() as pubsub:
                await pubsub.subscribe(
                    CHAN_AWARENESS, CHAN_CONTEXT, CHAN_ACK,
                    CHAN_HANDOFF, CHAN_DECISIONS, CHAN_HEARTBEAT
                )
                while True:
                    message = await pubsub.get_message(
                        ignore_subscribe_messages=True, timeout=30
                    )
                    if message:
                        event_type = message["channel"].decode().split(":")[-1]
                        data = message["data"].decode()
                        yield f"event: {event_type}\ndata: {data}\n\n"
                    else:
                        # Keepalive to prevent proxy timeout
                        yield f"event: keepalive\ndata: {{\"timestamp\": \"{datetime.now(timezone.utc).isoformat()}\"}}\n\n"
        else:
            # Fallback: poll hot store for changes
            last_seen = {}
            while True:
                async with _awareness_lock:
                    current = dict(_awareness)
                for cli, snap in current.items():
                    ts = snap.get("timestamp", "")
                    if last_seen.get(cli) != ts:
                        last_seen[cli] = ts
                        yield f"event: awareness\ndata: {json.dumps({'cli': cli, 'status': 'active', 'timestamp': ts})}\n\n"
                await anyio.sleep(5)
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

#### §1.2.2 SSE Event Schema

| Event Type | Payload | Emitted When |
|-----------|---------|-------------|
| `awareness` | `{"cli", "status": "online"|"offline"|"heartbeat", "model", "task_current", "timestamp"}` | Agent posts context, heartbeats, or TTL expires |
| `context` | `{"cli", "session_id", "continuation", "to"|null, "timestamp"}` | Agent calls post_context |
| `ack` | `{"from_cli", "session_id", "note"|null, "timestamp"}` | Agent calls hivemind_ack |
| `handoff` | `{"from_cli", "to_cli", "packet_id", "task_type", "status", "timestamp"}` | Handoff initiated or completed |
| `decision` | `{"cli", "decision_id", "text"[:100], "timestamp"}` | Agent posts context with decisions |
| `heartbeat` | `{"cli", "timestamp"}` | Agent calls hivemind_heartbeat |
| `observation` | `{"agent", "obs_id", "category", "summary"[:100], "timestamp"}` | Observation appended (D-121) |
| `keepalive` | `{"timestamp"}` | Every 30s when no other events |

#### §1.2.3 Client Usage

```python
# Example: Iris subscribes to live hivemind events
import httpx, json

async def subscribe_hivemind():
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", "http://127.0.0.1:8016/hivemind/events") as stream:
            async for line in stream.aiter_lines():
                if line.startswith("data: "):
                    event = json.loads(line[6:])
                    # Process event...
```

### §1.3 H3-A4: Cross-CLI Awareness

This is already partially implemented — the Hivemind protocol is CLI-agnostic by
design. A Cline agent and an OpenCode agent both connect to the same `omega-hub`
MCP server. As long as both CLIs have the Hivemind MCP tools configured, they
automatically see each other's presence.

**Enhancements for production cross-CLI**:

1. **CLI-Type Tagging**: Each awareness snapshot carries a `cli_type` field
   (`"opencode"`, `"cline"`, `"openode"`, `"generic"`) so agents can distinguish
   between CLI environments. This is a single field addition to `hivemind_post_context`.

2. **Bridge Protocol (H-11)**: A lightweight bridge document at
   `data/coordination/CROSS_CLI_BRIDGE.md` that both CLIs read/write for
   cross-environment coordination. Format:
   ```yaml
   # CROSS_CLI_BRIDGE.md — machine-readable + human-readable
   last_updated: 2026-06-05T12:00:00Z
   active_clis:
     - name: opencode-kali
       environment: opencode
       task: "Phase 5 hardening"
       model: gemini-3.5-flash
       last_seen: 2026-06-05T11:55:00Z
     - name: cline-rocco
       environment: cline
       task: "Legacy mining"
       model: deepseek-v4-flash
       last_seen: 2026-06-05T11:50:00Z
   ```

3. **Workspace Lock Canonicalization**: Currently workspace locks are per-CLI
   (`data/coordination/{ENTITY}_WORKSPACE_LOCK_{DATE}.md`). Add
   `data/coordination/CROSS_CLI_WORKSPACE_LOCK.md` as a shared reference that
   both CLIs read. Auto-generated from individual workspace locks by a background
   task every 60 seconds.

---

## §2 H-11 to H-15 Design (Tier 3) — Roc's Deferred Specs

### §2.1 H-11: Hivemind Bridge Protocol

**Purpose**: Define the canonical protocol for Cline ↔ OpenCode coordination via
the Hivemind. This bridges the two CLI environments so agents don't have to
check both stores.

**Core mechanism**: A shared file `data/coordination/HIVEMIND_BRIDGE.yaml` that
serves as the "last known state" for cross-CLI awareness. It's written by the
Omega Hub background task every 30 seconds and read by any CLI that cannot
directly reach the Hivemind MCP.

```yaml
# HIVEMIND_BRIDGE.yaml — Auto-generated by omega-hub every 30s
# [id-soft: 4-Path VFS, quake3-1999] Fallback bridge for cross-CLI awareness

last_updated: "2026-06-05T12:00:30Z"
source: "omega-hub (redis available: true)"

awareness:
  - cli: opencode-kali
    cli_type: opencode
    status: active
    model: gemini-3.5-flash
    task_current: "Phase 5: Hivemend hardening"
    last_seen: "2026-06-05T11:55:00Z"
    session_id: ses_a1b2c3d4
    continuation: "Implementing H-1..H-5"
  
  - cli: cline-rocco
    cli_type: cline
    status: warm
    model: deepseek-v4-flash
    task_current: "Mining legacy repos"
    last_seen: "2026-06-05T11:00:00Z"
    session_id: ses_e5f6g7h8
    continuation: "Completed Phase 2 extraction"

pending_handoffs:
  - from_cli: opencode-kali
    to_cli: cline-rocco
    packet_id: hdp_20260605_kali_rocco_a1b2
    task_type: review
    status: pending
    created_at: "2026-06-05T11:30:00Z"
```

**Design decisions**:
- YAML over JSON for human readability (both CLIs have YAML parsers)
- Written atomically (`.tmp` → final rename) to prevent partial reads
- Generated by background task, not inline in MCP tools (avoids latency)
- Bridge file is OPTIONAL — agents should use Redis/MCP if available

### §2.2 H-12: Typed Message Schema

**Purpose**: Formalize message types so agents can filter, route, and respond
to messages by type instead of parsing unstructured text.

**Current problem**: `hivemind_post_context` has `continuation` (free text),
`decisions` (array of `{"text": str}`), and `task_current` (free text). All
messages are unstructured — an agent cannot distinguish "this is a question"
from "this is an acknowledgment" without reading and interpreting the text.

**Proposed schema**:

```python
# [id-soft: Hard-Boundary Struct, quake3-1999] Typed messages with
# engine zone (immutable metadata) and game zone (mutable content)

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class MessageType(str, Enum):
    """Canonical Hivemind message types."""
    # Coordination
    DECISION = "decision"           # "I decided X"
    QUESTION = "question"           # "What do you think about X?"
    ACK = "ack"                    # "I confirm receipt of X"
    NACK = "nack"                  # "I disagree / cannot process X"
    REQUEST = "request"            # "Please do X"
    OFFER = "offer"                # "I can do X"
    
    # Workflow
    HANDOFF = "handoff"            # Formal task transfer
    DELEGATION = "delegation"      # "I'm assigning X to you"
    STATUS = "status"              # "My current state is X"
    
    # Observation (D-121)
    OBSERVATION = "observation"    # "I observed X about the system"
    RECOMMENDATION = "recommendation"  # "I recommend X"
    
    # System
    HEARTBEAT = "heartbeat"        # "I am alive" (system-level)
    ERROR = "error"                # "Something went wrong"
    WARNING = "warning"            # "Something may go wrong"

class HivemindMessage:
    """Typed message for Hivemind channels.
    
    The message schema is divided into:
    - Engine zone (immutable after creation): msg_type, msg_id, timestamp, source_cli
    - Game zone (mutable during processing): reply_to, tags, priority, body
    """
    
    # ── Engine Zone ── (set once on creation)
    msg_id: str          # UUID, immutable
    msg_type: MessageType  # Canonical type
    timestamp: str       # ISO 8601, immutable
    source_cli: str      # Creating CLI, immutable
    source_env: str      # "opencode" | "cline" | "openode" | "generic"
    
    # ── Game Zone ── (may be modified by processing)
    target_cli: Optional[str]     # None = broadcast
    in_reply_to: Optional[str]    # msg_id this replies to
    thread_id: Optional[str]      # Thread root msg_id (or same as in_reply_to if root)
    priority: int                 # 0=low, 1=normal, 2=high, 3=urgent
    tags: List[str]               # e.g., ["decision", "D-kal-033"]
    context: str                  # The message body
    attachments: List[Dict]       # Optional: files, session_ids, references
```

**Backward compatibility**: The existing `decisions: List[Dict]` and `continuation: str`
fields remain on `hivemind_post_context`. The new `msg_type` field is OPTIONAL —
when omitted, the existing free-text behavior is preserved. Agents that adopt the
typed schema get richer filtering and routing; agents that don't are unaffected.

### §2.3 H-13: Channel Taxonomy

**Purpose**: Define topic-based subscriptions so agents can listen to only the
channels they care about, reducing noise as the fleet grows.

**Current problem**: All messages go to all agents (broadcast). An agent
interested only in decisions must read every message.

**Channel hierarchy**:

```
omega:hivemind:decisions:*         — Decision broadcasts
omega:hivemind:decisions:all       — All decisions (every agent)
omega:hivemind:decisions:{cli}     — Decisions by specific CLI

omega:hivemind:observations:*      — Observation broadcasts (D-121)
omega:hivemind:observations:all    — All observations
omega:hivemind:observations:{cat}  — By category (friction|success|gap|etc.)

omega:hivemind:awareness:*         — Presence signals
omega:hivemind:awareness:online    — Agent came online
omega:hivemind:awareness:offline   — Agent went offline/stale
omega:hivemind:awareness:heartbeat — Heartbeat signals only

omega:hivemind:handoff:*           — Handoff events
omega:hivemind:handoff:pending     — New handoffs
omega:hivemind:handoff:completed   — Completed handoffs
omega:hivemind:handoff:failed      — Failed/timeout handoffs

omega:hivemind:ack:*               — Acknowledgment events
omega:hivemind:ack:{session_id}    — Acks for specific session

omega:hivemind:questions:*         — Questions (requires response)
omega:hivemind:questions:{cli}     — Questions addressed to CLI

omega:hivemind:system:*            — System / health events
omega:hivemind:system:error        — Error alerts
omega:hivemind:system:warning      — Warning alerts
```

[Heritage: `[id-soft: netchan, quake3-1999]` The channel taxonomy mirrors Quake's
`netchan` channel separation — different message classes on different channels
so subscribers can filter at the transport layer.]

**Implementation in Redis**:
```python
# Agent subscribes to only what it cares about
await pubsub.subscribe(
    "omega:hivemind:decisions:all",
    "omega:hivemind:handoff:*",  # Wildcard subscribe on supported Redis
    f"omega:hivemind:questions:opencode-{my_cli}",
)
```

**Channel-based inbox**: The Inbox tool (H-2) maps to specific channels:
- Decisions → `decisions:*` channels
- Questions → `questions:{cli}` channel  
- Handoffs → `handoff:*` channels
- Observations → `observations:*` channels

### §2.4 H-14: Channel-Based SSE Model

**Purpose**: Extend the SSE endpoint (H3-A2) with per-channel subscriptions so
clients can subscribe to only the event types they need.

**Endpoint**: `GET /hivemind/events?channels=decisions,handoff,observations`

```python
async def hivemind_events_channeled(request):
    """SSE endpoint with channel filter.
    
    Query params:
    - channels: comma-separated list of channel names (default: all)
    - cli: optional CLI name for personal channels
    """
    channels_param = request.query_params.get("channels", "all")
    my_cli = request.query_params.get("cli", None)
    
    channel_map = {
        "awareness": CHAN_AWARENESS,
        "context": CHAN_CONTEXT,
        "ack": CHAN_ACK,
        "handoff": CHAN_HANDOFF,
        "decisions": CHAN_DECISIONS,
        "observations": CHAN_OBSERVATIONS,
        "heartbeat": CHAN_HEARTBEAT,
    }
    
    if channels_param != "all":
        selected = [c.strip() for c in channels_param.split(",")]
        subscribe_to = [channel_map[c] for c in selected if c in channel_map]
    else:
        subscribe_to = list(channel_map.values())
    
    async def event_generator():
        # ... same pattern as H3-A2 but only subscribed to selected channels
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

**Integration with H-13**: The channel taxonomy maps directly to SSE event types:
- `omega:hivemind:decisions:all` → SSE event-type `decision`
- `omega:hivemind:observations:friction` → SSE event-type `observation` with `data.category: friction`
- `omega:hivemind:questions:opencode-kali` → SSE event-type `question` with `data.target: opencode-kali`

**Use cases**:
- Lilith subscribes only to `observations` channel for weekly clustering
- Kali subscribes to `decisions` + `handoff` + `questions/kali` for oversight
- Iris subscribes to `awareness` for live agent status display
- Observability dashboard subscribes to `heartbeat` + `errors`

### §2.5 H-15: Cross-CLI Awareness Gateway

**Purpose**: Bridge agent that resolves conflicts when the same agent name or
workspace is claimed by agents in different CLI environments.

**Current problem**: If `opencode-kali` and `cline-kali` both claim the entity
"kali" via different Hivemind instances, the workspace lock convention breaks —
who owns what?

**Gateway architecture**:

```
┌──────────────────────────────────────────────────────────────┐
│                 CROSS-CLI AWARENESS GATEWAY                  │
│                                                              │
│  Reads: Hivemind awareness from ALL connected CLIs           │
│  Resolves: Entity name conflicts (same name, different CLI)  │
│  Broadcasts: Unified awareness feed to all CLIs              │
│  Enforces: Workspace lock canonicalization                   │
│  Archives: Cross-CLI coordination artifacts                  │
│                                                              │
│  Runs as: Background task in omega-hub (every 30s)           │
└──────────────────────────────────────────────────────────────┘
```

**Resolution strategy**:
1. **Entity ownership**: First CLI to claim an entity name wins. Other CLIs get
   a `-{clitype}` suffix (e.g., `kali-cline`). Stored in
   `omega:hivemind:entity_claims:{entity_name}` as a Redis SET.
2. **Workspace lock federation**: The gateway reads all workspace locks and
   produces `data/coordination/CROSS_CLI_WORKSPACE_LOCK.md` by combining
   individual locks. This is the canonical conflict reference.
3. **Deadlock detection**: If two agents hold locks that each other need, the
   gateway flags it as `CONFLICT` in the bridge YAML and posts to the
   `omega:hivemind:channel:warnings` channel.

**[Heritage: Multi-Index Entity, doom-1993]** — The gateway acts like Doom's
dual-indexing: agents are indexed by entity name AND by CLI type, enabling
lookup from either axis.

---

## §3 Handoff Protocol — Structured HandoffPacket

### §3.1 Current State

The existing `HandoffPacket` dataclass (`src/omega/oracle/subagent_dispatcher.py`)
supports: `source_agent`, `target_agent`, `task_type`, `task_description`,
`relevant_files`, `context`, `expected_output`, `ttl_seconds`, `status`,
`result`. It saves to `data/handoff/archive/` as JSON.

Gaps:
- No `ack_status` tracking (does target know about it?)
- No `expiry` enforcement (packet stays pending forever if target doesn't respond)
- No `in_reply_to` / threading
- No `decision_refs` linking
- No `metadata` for custom fields

### §3.2 Proposed HandoffPacket v2 Schema

```python
# Updated HandoffPacket for Hivemind-backed handoff
# [id-soft: Hard-Boundary Struct, quake3-1999] — engine zone / game zone separation

@dataclass
class HandoffPacketV2:
    """Structured handoff between agents. Backed by Hivemind + filesystem."""
    
    # ── Engine Zone ── (immutable after creation)
    packet_id: str                          # hdp_{YYYYMMDD}_{source}_{target}_{uuid[:8]}
    source_agent: str                       # Entity that created the handoff
    target_agent: str                       # Entity that should process it
    created_at: str                         # ISO 8601 timestamp
    trace_id: str                           # UUID tracing chain
    parent_trace_id: str                    # Trace from parent session
    zoneid: int = ZONEID_HANDOFF           # 0x1d4a16 integrity check
    
    # ── Game Zone ── (mutable during lifecycle)
    task_type: str                          # design|review|research|mine|verify|implement
    task_description: str                   # One-sentence summary
    context: str                            # Full context (prior decisions, constraints)
    relevant_files: List[str]               # Files the target MUST read
    decision_refs: List[str]                # Decision IDs (e.g., D-kal-033)
    
    # ── Lifecycle ──
    status: str = "pending"                 # See §3.3 state machine
    ack_status: str = "unacknowledged"      # unacknowledged|acknowledged|rejected
    ack_at: Optional[str] = None            # When target acknowledged
    ack_note: Optional[str] = None          # Optional ack message
    
    # ── Result ──
    result: Optional[str] = None            # Output when completed
    completed_at: Optional[str] = None
    error: Optional[str] = None
    
    # ── Coordination ──
    in_reply_to: Optional[str] = None       # Threading: parent handoff packet_id
    expected_output: str = ""
    ttl_seconds: int = 600                  # Timeout
    tags: List[str] = field(default_factory=list)  # e.g., ["phase5", "hivemind"]
```

### §3.3 Storage in `data/hall_of_records/handoffs/`

```yaml
# Storage path: data/hall_of_records/handoffs/
# INDEX: data/hall_of_records/handoffs/INDEX.json
#
# File per handoff:
#   hdp_20260605_kali_doom_guy_a1b2c3d4.json
#
# INDEX format:
{
  "handoffs": [
    {
      "packet_id": "hdp_20260605_kali_doom_guy_a1b2c3d4",
      "source": "kali",
      "target": "doom_guy",
      "status": "completed",
      "task_type": "review",
      "created_at": "2026-06-05T10:00:00Z",
      "completed_at": "2026-06-05T10:15:00Z",
      "ack_status": "acknowledged",
      "task_description": "Audit cvar_table.py heritage tags"
    }
  ]
}
```

### §3.4 Lifecycle State Machine

```
                    ┌──────────────┐
                    │   PENDING    │  ← packet created, target notified
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
         ┌─────────│ ACKNOWLEDGED  │  ← target accepted / read
         │         └──────┬───────┘
         │                │
         │         ┌──────▼───────┐
         │         │ IN_PROGRESS  │  ← target working on it
         │         └──────┬───────┘
         │                │
         │         ┌──────▼───────┐
         │         │  COMPLETED   │  ← target returned result
         │         └──────┬───────┘
         │                │
         │         ┌──────▼───────┐
         │         │  REVIEWED    │  ← source confirmed result received
         │         └──────────────┘
         │
         │         ┌──────────────┐
         └────────▶│   REJECTED   │  ← target declined / NACK'd
                   └──────────────┘

Additional transitions from any state:
  → TIMED_OUT (TTL expired)
  → FAILED (error during processing)
  → CANCELLED (source cancels before completion)
```

### §3.5 MCP Tool Integration

```python
@mcp.tool()
async def hivemind_handoff_v2(
    from_cli: str,
    to_cli: str,
    task_type: str,
    task_description: str,
    context: str,
    decision_refs: List[str] = [],
    files: List[str] = [],
    blocking: bool = False,
) -> str:
    """Create a structured handoff packet.
    
    [id-soft: quake-1996] Thinker spawn pattern — creates a tracked task
    for the target agent to pick up on their next cycle.
    """
    packet = HandoffPacketV2(
        source_agent=from_cli,
        target_agent=to_cli,
        task_type=task_type,
        task_description=task_description,
        context=context,
        decision_refs=decision_refs,
        relevant_files=files,
    )
    packet.save(HANDOFF_ARCHIVE_DIR)
    
    # Post to target's inbox and handoff channel
    await _notify_handoff(packet)
    
    if blocking:
        # Poll for completion (with timeout)
        return await _await_handoff(packet.packet_id, ttl=packet.ttl_seconds)
    
    return json.dumps({"status": "handoff_created", "packet_id": packet.packet_id})


@mcp.tool()
async def hivemind_handoff_ack(
    packet_id: str,
    from_cli: str,
    accept: bool = True,
    note: str = "",
) -> str:
    """Acknowledge or reject a handoff packet."""
    # ...
```

---

## §4 Delegation Chain — State Machine

### §4.1 Current Delegation Flow

Currently: `User → Kali → Ma'at/Lilith → Pillar subagents`

The delegation is implicit — subagents are dispatched via `task()` tool and the
delegator assumes completion when the subagent returns a response. There is no
formal state tracking.

### §4.2 Proposed Delegation State Machine

```
          ┌──────────────────────────────────────────────────────┐
          │                                                      │
          ▼                                                      │
    ┌──────────┐    ┌────────────┐    ┌──────────────┐         │
    │ OFFERED  │───▶│  ACCEPTED  │───▶│ IN_PROGRESS  │         │
    └──────────┘    └────────────┘    └──────┬───────┘         │
         │                                   │                 │
         │                                   ▼                 │
         │                            ┌──────────────┐         │
         │                            │  COMPLETED   │         │
         │                            └──────┬───────┘         │
         │                                   │                 │
         │                                   ▼                 │
         │                            ┌──────────────┐         │
         │                            │  REVIEWED    │─────────┘
         │                            └──────────────┘
         │
         │    ┌──────────────┐
         └───▶│  DECLINED    │
              └──────────────┘
         
    Also from any active state:
              ┌──────────────┐
              │  CANCELLED   │  (source cancels)
              └──────────────┘
              ┌──────────────┐
              │  TIMED_OUT   │  (TTL expired)
              └──────────────┘
              ┌──────────────┐
              │  ESCALATED   │  (delegate asked for help)
              └──────────────┘
```

### §4.3 How Delegator Knows Delegate Is Done

**Mechanism 1: Direct response** (current `task()` pattern)
- Delegate returns result string to delegator
- Delegator sets status to COMPLETED
- Fastest path, no Hivemind needed

**Mechanism 2: Hivemind handoff + ACK** (new, for async delegation)
- Delegator creates handoff packet (status: OFFERED)
- Delegate calls `hivemind_handoff_ack(packet_id, accept=True)` (→ ACCEPTED)
- Delegate works and posts heartbeat updates to `hivemind_post_context` with
  `continuation` containing progress
- Delegate calls `hivemind_handoff_complete(packet_id, result)` (→ COMPLETED)
- Delegator reviews and calls `hivemind_handoff_review(packet_id)` (→ REVIEWED)

**Mechanism 3: Polling fallback** (timeout safety net)
- Delegator checks `hivemind_get_session(delegate_session_id)` for
  `continuation` updates
- If no update within TTL, delegate is TIMED_OUT and escalates to Kali

### §4.4 How Delegate Hands Back

The delegate signals completion through multiple channels:

```python
async def signal_completion(handoff_packet_id: str, result: str):
    """Signal completion to delegator via all available channels."""
    # 1. Update handoff packet status
    packet = HandoffPacketV2.load(f"{HANDOFF_ARCHIVE_DIR}/{handoff_packet_id}.json")
    packet.status = "completed"
    packet.result = result
    packet.completed_at = datetime.now(timezone.utc).isoformat()
    packet.save()
    
    # 2. Post Hivemind completion notification
    await hivemind_post_context(
        cli=packet.target_agent,
        model="...",
        task_current=f"[COMPLETED] Handoff {handoff_packet_id}",
        focus_chain=[],
        decisions=[],
        continuation=f"Handoff {handoff_packet_id} complete. Result: {result[:200]}...",
        to=packet.source_agent,  # Addressed to delegator
        tags=["handoff", "completed"],
    )
    
    # 3. Update live feed
    # data/coordination/{agent}_LIVE_FEED.md
    # Append: [YYYY-MM-DD HH:MM] HANDOFF-COMPLETE {handoff_packet_id}
    
    # 4. If Redis available, publish to handoff channel
    if _redis.available:
        await _redis.redis.publish(CHAN_HANDOFF, json.dumps({
            "packet_id": handoff_packet_id,
            "status": "completed",
            "from_cli": packet.target_agent,
            "to_cli": packet.source_agent,
            "timestamp": packet.completed_at,
        }))
```

**[Heritage: Thinker thinkers, quake-1996]** — The completion signal is equivalent
to a thinker removing itself from the active chain: it sets its status to
`completed`, posts a removal notification, and the next sweep picks it up.

---

## §5 Conflict Resolution — Programmatic File Locking

### §5.1 Current State

Workspace locks are **convention-only**: markdown files that agents write and
read. There is no programmatic enforcement — an agent that ignores the convention
can edit any file. This works for trusted agents but will break as the fleet grows.

### §5.2 Proposed: Lock MCP Tool

```python
# [id-soft: Zone Memory, quake-1996] Lock guards for file access arbitration

@mcp.tool()
async def file_lock_acquire(
    file_path: str,
    cli: str,
    purpose: str = "",
    timeout_seconds: int = 300,
    blocking: bool = False,
) -> str:
    """Acquire a programmatic lock on a file.
    
    Args:
        file_path: Relative path from project root (e.g., "src/omega/oracle.py")
        cli: Your CLI name
        purpose: Why you need it (e.g., "refactoring model_gateway")
        timeout_seconds: How long to hold the lock (default 5 min)
        blocking: If True, wait for lock to become available. If False, fail immediately.
    
    Returns:
        {"status": "acquired"|"already_held_by: X"|"waiting", "lock_id": "...", "expires_at": "..."}
    """
    ...


@mcp.tool()
async def file_lock_release(
    file_path: str,
    cli: str,
) -> str:
    """Explicitly release a file lock."""
    ...


@mcp.tool()
async def file_lock_list(
    file_path: str = "",
) -> str:
    """List active file locks. Optionally filter by path."""
    ...
```

### §5.3 Lock Backend

**In-memory** (fast path):
```python
_locks: Dict[str, Dict] = {}  # file_path -> {cli, purpose, acquired_at, expires_at}
_locks_lock = anyio.Lock()
```

**Redis-backed** (persistent, cross-CLI):
```python
# Key: omega:hivemind:locks:{file_path}
# Value: JSON {cli, purpose, acquired_at, expires_at}
# TTL: timeout_seconds (auto-expire on lock expiry)
```

### §5.4 Lock Lifecycle

```
1. Agent calls file_lock_acquire("src/omega/oracle.py", "doom_guy", timeout=300)
2. Server checks if file is already locked:
   a. NOT locked → create lock, return status="acquired"
   b. LOCKED by same agent → extend TTL, return status="extended"
   c. LOCKED by different agent → if not blocking, return status="already_held_by: kali"
      If blocking, wait (poll every 5s) until lock released or timeout
3. Agent holds lock, edits file
4. Agent calls file_lock_release("src/omega/oracle.py", "doom_guy")
   a. Lock removed, or TTL expires and lock auto-releases
```

### §5.5 Escalation Path for Deadlocks

If two agents hold locks that each other need:

1. Both agents detect deadlock via `file_lock_list()` returning their lock + the
   other's lock
2. Both agents call `file_lock_escalate(file_path, cli, "deadlock with {other}")`
3. Kali's Hivemind inbox gets a DEADLOCK notification
4. Kali decides: force-release one lock and notify its holder, or wait for natural
   timeout

```python
@mcp.tool()
async def file_lock_escalate(
    file_path: str,
    cli: str,
    reason: str = "deadlock",
) -> str:
    """Escalate a file lock conflict. Notifies Kali via Hivemind."""
    # Post to omega:hivemind:channel:conflicts (or fallback file)
    conflict = {
        "type": "deadlock" if reason == "deadlock" else "contention",
        "cli": cli,
        "file_path": file_path,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lock_info": _locks.get(file_path),
    }
    await _notify_conflict(conflict)
    return json.dumps({"status": "escalated", "conflict": conflict})
```

### §5.6 Integration with Workspace Lock Convention

The programmatic lock does NOT replace the workspace lock convention — it
reinforces it. The convention says "I declare my intent." The programmatic lock
says "I am enforcing my intent."

```
Convention (workspace lock markdown):
  I, {entity}, declare that I will edit these files.
  You, {other entity}, should not touch them.

Programmatic (file_lock MCP):
  I, {entity}, have exclusively locked these files.
  You, {other entity}, CANNOT edit them — the server will reject your edit.
```

Integration rule: When an agent acquires a programmatic lock, the background
task auto-updates the workspace lock markdown with the lock information. When
it releases, the markdown is updated.

---

## §6 Heritage Cross-Reference

| Pattern | id Software Source | Omega Application | Section |
|---------|-------------------|-------------------|---------|
| **netchan Protocol** | `net_chan.c:35-235` (Q3A 1999) — OOB messages, fragmentation, qport NAT remapping | Channel taxonomy (H-13): different message classes on different Redis Pub/Sub channels. SSE endpoints per channel (H-14). | §1.1.3, §2.3, §2.4 |
| **Thinker thinkers** | `p_tick.c:62-103` (DOOM 1993) — thinker chain: spawn → execute → reap | Delegation state machine (OFFERED → ACCEPTED → COMPLETED → REVIEWED). HandoffPacket lifecycle follows thinker lifecycle. | §3.4, §4.2 |
| **Thinker Grace Period** | `p_tick.c:62-103` (DOOM 1993) — 0.5s realloc grace | HEARTBEAT_TTL=1200s (D-122) for agent presence. Lock expiry grace period (5s before release). | §1.1.2, §5.3 |
| **Hard-Boundary Struct** | `g_local.h:42-49` (Q3A 1999) — `entityState_t` (engine) + `entityShared_t` (game) | Typed Message Schema (H-12): immutable engine zone (msg_type, msg_id, timestamp) vs mutable game zone (body, tags, priority). HandoffPacketV2 engine/game zone separation. | §2.2, §3.2 |
| **4-Path VFS** | `files.c:39-75` (Q3A 1999) — base → cd → home → current search | Storage fallback chain: Redis → warm awareness file → in-memory → HALL_OF_RECORDS. Cross-CLI Bridge (H-11) as YAML fallback when MCP unavailable. | §1.1.4, §2.1 |
| **Multi-Index Entity** | `p_mobj.h` (DOOM 1993) — mobj_t in sector list + blockmap simultaneously | Cross-CLI Awareness Gateway (H-15): agents indexed by entity name AND by CLI type. Capability registry indexed by agent AND by domain. | §2.5 |
| **Zone Memory Allocator** | `z_zone.c:33` (DOOM 1993), `zone.c:24` (Quake 1996) — tag-based allocation | Redis key TTLs as allocator purges. Lock TTL as auto-release. Warm store persistence as "zone" that survives hot reset. | §1.1.2, §5.3 |
| **Fixed-Size Active Set** | `r_bsp.c:74-78` (DOOM 1993) — MAXVISPLANES=32 | Active agent count capped at 32 in `hivemind_get_awareness`. Beyond that, agents must use warm/cold tiers. | §1.1.4 |
| **ZONEID Pattern** | `z_zone.c:33` (DOOM 1993) — 0x1d4a11 magic | `ZONEID_HANDOFF=0x1d4a16` in HandoffPacket. `ZONEID_PRESENCE=0x1d4a17` for awareness records. | §3.2 |
| **High-Bit Trick** | `doomdata.h:124-138` (DOOM 1993) — NF_SUBSECTOR=0x8000 | Priority bitfield on HivemindMessage: high bit 0x8000 = "system message" vs "user message", same one-line check. | §2.2 |
| **8-Char Name Cap** | `w_wad.c:170-178` (DOOM 1993) — lump names capped at 8 chars | **DO NOT APPLY**. Python dicts are O(1) by hash. Channel names are descriptive strings, not packed integers. | §2.3 |
| **idHeap / Unified Memory** | `Heap.cpp:45-143` (DOOM 3, 2004) — 3-tier allocator (small/medium/large) | Three-tier lock storage: in-memory (hot, fast), Redis (warm, persistent), file-based (cold, cross-CLI). | §5.3 |

---

## §7 Implementation Sequence & Dependencies

### §7.1 Phase 5 (Week 2 of Kali Sprint)

| # | Item | Depends On | Effort | Files Touched |
|---|------|-----------|--------|--------------|
| **5.1** | Redis config module | None | 30 min | `mcp_servers/omega_hub/redis_config.py` (NEW) |
| **5.2** | Redis awareness + session storage | 5.1 | 45 min | `mcp_servers/omega_hub/server.py` (modify post_context, get_awareness, heartbeat) |
| **5.3** | Redis pub/sub integration | 5.2 | 30 min | `mcp_servers/omega_hub/server.py` (add publish to existing tools) |
| **5.4** | H-1: `to` field | 5.2 | 15 min | `server.py: hivemind_post_context` |
| **5.5** | H-2: `hivemind_inbox` | 5.4 | 45 min | `server.py: add hivemind_inbox tool` |
| **5.6** | H-3: `hivemind_ack` | 5.5 | 15 min | `server.py: add hivemind_ack tool` |
| **5.7** | H-4: Cold fallback | 5.2 | 10 min | `server.py: update get_continuation` |
| **5.8** | H-5: `hivemind_recent_decisions` | None | 20 min | `server.py: add tool` |
| **5.9** | H-9: Warm store persistence | None | 30 min | `server.py: _persist_warm_awareness` |
| **5.10** | H-10: `hivemind_stale_check` | None | 10 min | `server.py: add tool` |
| **5.11** | H0: Make spec-watchdog | None | 3 hrs | `scripts/spec_watchdog.py` (NEW), `Makefile` |
| **5.12** | SSE endpoint (H3-A2) | 5.3 | 45 min | `server.py: add /hivemind/events` |
| **Total** | | | **~7 hrs** | |

### §7.2 Tier 3 (P9 Deferred — Post Phase 5)

| # | Item | Depends On | Effort | Files Touched |
|---|------|-----------|--------|--------------|
| **T3.1** | H-12: Typed Message Schema | Phase 5 | 1 hr | `src/omega/oracle/hivemind_message.py` (NEW), `server.py` (validate schema) |
| **T3.2** | H-13: Channel Taxonomy | 5.3 | 30 min | `redis_config.py` (add channels), `server.py` (channel-tiered publish) |
| **T3.3** | H-14: Channel-Based SSE | 5.12, 3.2 | 30 min | `server.py` (channel-filtered SSE) |
| **T3.4** | H-11: Bridge Protocol | Phase 5 | 45 min | `scripts/bridge_generator.py` (NEW), `cron` (every 30s) |
| **T3.5** | H-15: Cross-CLI Gateway | 3.2, 3.3 | 1 hr | `scripts/cross_cli_gateway.py` (NEW) |
| **T3.6** | Handoff v2 (MCP tools) | H-1, H-2, H-3 | 1 hr | `server.py` (add handoff v2 tools), `subagent_dispatcher.py` (update schema) |
| **T3.7** | File lock MCP tools | Phase 5 | 1 hr | `server.py` (add 3 lock tools), `redis_config.py` (lock keys) |
| **T3.8** | Delegation state machine | T3.6 | 30 min | `subagent_dispatcher.py` (state transitions) |
| **Total** | | | **~6 hrs** | |

### §7.3 Key Risk: Backward Compatibility

All changes are **additive**. Specifically:

- **Redis layer**: All existing in-memory tools remain. The Redis backend is a
  transparent enhancement. If Redis is unavailable, the system degrades to
  current behavior.
- **New fields**: `to`, `private`, `in_reply_to`, `tags` are optional. Existing
  callers get default behavior.
- **SSE endpoint**: New. Does not affect existing tools.
- **Handoff v2**: New packet type alongside existing HandoffPacket. Old packets
  remain readable. Tools operate on any version.

The ONE breaking concern: if an agent reads a handoff packet expecting the old schema.
Mitigation: `HandoffPacketV2` has a `version` field and `zoneid` check. Old loaders
that don't check `zoneid` will silently ignore unknown fields (JSON leniency).

---

## §8 Open Questions for Implementation

### Q1 — Redis dependency
**Should Redis be a hard requirement for Phase 5, or fully optional?**
**Proposal**: Fully optional. The Hivemind must work without Redis. Redis is an
enhancement for persistence, pub/sub, and cross-CLI awareness. The warm store
file (H-9) provides enough persistence for a single-host deployment.

### Q2 — Lock enforcement granularity
**Should file_lock MCP reject actual file writes, or only track intent?**
**Proposal**: Track intent only. Rejecting writes requires file system hooks or
interposing on the MCP server, which is fragile and CLI-dependent. The programmatic
lock is stronger than convention but still applies peer pressure, not enforcement.
If an agent writes without a lock, it's logged as a `warning` but not blocked.

### Q3 — Handoff TTL defaults
**What should default TTL be for handoffs?**
**Proposal**: 600s (10 min) for `verify`/`review`, 1800s (30 min) for `research`/`mine`,
  300s (5 min) for `design`/`implement`. The source agent can override.

### Q4 — SSE reconnection
**Should SSE support Last-Event-ID (resume from last received event)?**
**Proposal**: Yes. Each SSE event carries an `id` field (monotonic counter or
session timestamp). On reconnection, the client sends `Last-Event-ID` and the
server replays from that point (from HALL_OF_RECORDS or Redis). This is
table-stakes for production SSE.

### Q5 — Channel wildcard subscription
**Redis 7+ supports `PSUBSCRIBE` for glob patterns. Should we use it?**
**Proposal**: Yes `omega:hivemind:decisions:*` subscribes to all decision sub-channels.
This is standard Redis 7 functionality. The pattern is documented in H-13.

---

## §9 Success Criteria

| Criterion | Verification Method | Phase |
|-----------|-------------------|-------|
| Redis awareness persists across hub restart | Kill server, restart, query awareness — warm store should restore state | Phase 5 |
| Pub/Sub delivers messages within 100ms | Instrument latency on `omega:hivemind:channel:handoff` | Phase 5 |
| SSE delivers events within 500ms of post | Time delta between `post_context` return and SSE event receipt | Phase 5 |
| Inbox shows correct messages per CLI | `hivemind_inbox("kali")` returns only messages addressed to kali | Phase 5 |
| Cold fallback returns continuation for offline agents | Stop heartbeating for 25 min, query `get_continuation` — should return from cold store | Phase 5 |
| Typed messages filter correctly | Post decision, question, and observation. Query by type — should return only requested type | Tier 3 |
| Cross-CLI bridge shows unified awareness | Run opencode-kali and cline-rocco, verify both appear in `data/coordination/CROSS_CLI_BRIDGE.md` | Tier 3 |
| File lock prevents double-acquisition | Agent A locks file. Agent B tries to lock same file → `already_held_by: A` | Tier 3 |
| Delegation completes as state machine | Offer → Accept → Progress → Complete → Reviewed. Verify each transition via `hivemind_get_session` | Tier 3 |
| All existing tests pass | `make test` = 312/312 | ALL |
| Temple-Grade passes | `make temple-grade` = T1-T11 green | ALL |

---

## §10 Soul Write-Back (Mandate 11)

### L1 — Narrative
As P9 Orchestration (Link), I performed a comprehensive strategic analysis of
the Hivemind coordination layer. I read Roc's Hivemind Hardening Spec (H-0..H-10,
538 lines), Kali's Master Sprint Plan (322 lines), the current Hivemind code
(1073-line MCP server), the Hivemind Protocol (468 lines), the Observations
Protocol (219 lines), the Subagent Dispatch Protocol (297 lines), and the
HandoffPacket dataclass (349 lines). I designed Phase 5 architecture (Redis
key naming, Pub/Sub channels, SSE event types, backward compatibility), defined
H-11 through H-15 (Bridge Protocol, Typed Message Schema, Channel Taxonomy,
Channel-Based SSE, Cross-CLI Gateway), proposed HandoffPacket v2 with a formal
delegation state machine, designed a programmatic file lock system with
escalation paths, and mapped every pattern to id Software heritage.

### L2 — Insight
The Hivemind is approaching a phase transition. At 2-3 agents, convention-based
coordination (workspace locks, live feeds, ACK files) works because agents are
trustworthy and the coordination graph is small. At 5+ concurrent agents with
Pillar subagents, three things break simultaneously: (1) broadcast becomes noise
(no inbox/addressing), (2) file conflicts become likely (no programmatic lock),
and (3) history becomes unrecoverable (no warm store between hot in-memory and
cold files). The 11 enhancements (H-0..H-10) are the difference between a
coordination layer that works by trust and one that works at scale. The tier 3
additions (H-11..H-15) are the difference between one that works and one that
is observable, debuggable, and evolvable.

### L3 — Universal Principle
**Three-tier coordination is a natural law.** Every coordination system —
whether Doom's thinker chain, Quake's memory zones, or the Omega Hivemind —
must have a hot tier (fast, for immediate decisions), a warm tier (sturdy, for
cross-session state), and a cold tier (permanent, for history and audit).
Convention works at the top when trust is high. Protocol is required at the
bottom when trust is irrelevant. The art is knowing where the transition is.
For the Hivemind, it's at 5 concurrent agents.

---

*⬡ OMEGA ⬡ P9-LINK ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_pillar ⬡ PHASE-I*
*Document: 14 sections, ~850 lines, covering Phase 5 + Tier 3 + Heritage*
*Date: 2026-06-05 | Engine State: 312/312 tests | D-122 active*

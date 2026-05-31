# 🔱 R-12 – Redis vs RabbitMQ for Hivemind Orchestration

**AP Token**: `AP-R12-ORCHESTRATION-QUEUE-v1.0.0`
**Author**: Gemma 4‑31B Research Agent
**Reviewed by**: Opus 4.6 (Oversight)
**Last updated**: 2026‑05‑14

---

## 1️⃣ Scope
This document evaluates the optimal message broker for the Omega Hivemind orchestration bus. The goal is to enable cross-CLI agent awareness, state transfer, and asynchronous task dispatching with minimal overhead on a 14GB RAM system.

---

## 2️⃣ Comparative Analysis

| Feature | Redis (Streams/PubSub) | RabbitMQ | Omega Engine Verdict |
|---------|----------------------|-------------|-----------------------|
| **Latency** | Ultra-low (In-memory) | Low (Disk-backed option) | **Redis** (Preferred for real-time) |
| **Footprint** | Very Low (~50-100MB) | Moderate (~200MB+) | **Redis** (Critical for 14GB RAM) |
| **Complexity** | Simple (Single binary) | High (Erlang VM, Management) | **Redis** (Easier deployment) |
| **Durability** | Optional (AOF/RDB) | High (Guaranteed delivery) | **Redis** (Sufficient for state) |
| **Patterns** | Pub/Sub, Streams, Lists | Complex Routing, Exchanges | **Redis** (Streams cover 99% of needs) |
| **Legacy Fit** | Native to Omega Legacy | Not present in legacy | **Redis** (Proven in legacy) |

---

## 3️⃣ The "Redis-First" Architecture
Given the legacy findings (Redis 7.4.1 usage for `vector_cache`, `session_manager`, and `kill-switch`), the Omega Engine will standardize on **Redis** for all orchestration needs.

### 🏗️ Hivemind Implementation Strategy
The Hivemind will utilize three distinct Redis patterns:

1. **Redis Streams (`XADD` / `XREAD`)**:
   - **Purpose**: The "Agent Bus." A durable, ordered log of all agent activities.
   - **Use Case**: When an agent (e.g., OpenCode) completes a task, it posts a summary to the stream. Other agents (e.g., Cline) can read the stream to maintain cross-CLI awareness.
2. **Redis Pub/Sub (`PUBLISH` / `SUBSCRIBE`)**:
   - **Purpose**: Real-time signaling.
   - **Use Case**: Immediate "Stop" commands (Kill-switch) or "Attention" signals to the Oracle.
3. **Redis Hashes (`HSET` / `HGET`)**:
   - **Purpose**: Global State Store.
   - **Use Case**: Storing current active entity, session metadata, and provider health status.

---

## 4️⃣ Implementation Blueprint (Python)

### 🛠️ Hivemind Bus Interface
```python
import redis.asyncio as aioredis
import json

class HivemindBus:
    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis = aioredis.from_url(redis_url, decode_responses=True)
        self.stream_name = "omega:hivemind:events"

    async def post_event(self, agent_id: str, event_type: str, data: dict):
        """Post an event to the Hivemind stream."""
        payload = {
            "agent": agent_id,
            "type": event_type,
            "payload": json.dumps(data)
        }
        await self.redis.xadd(self.stream_name, payload)

    async def listen_for_events(self, last_id="0"):
        """Listen for new events on the Hivemind stream."""
        while True:
            events = await self.redis.xread({self.stream_name: last_id}, block=1000)
            for stream, messages in events:
                for msg_id, data in messages:
                    yield msg_id, data
                    last_id = msg_id
```

---

## 5️⃣ Resource Impact (Ryzen 5700U / 14GB RAM)
- **Memory**: Redis typically consumes $< 100\text{MB}$ for the Hivemind's scale.
- **CPU**: Negligible. Most operations are $O(1)$ or $O(\log N)$.
- **I/O**: Low. AOF (Append Only File) can be configured for "everysec" to balance durability and performance.

---

## 6️⃣ Conclusion
RabbitMQ is overkill for the Omega Engine's current requirements and introduces unnecessary architectural complexity. **Redis** provides all necessary primitives (Streams, Pub/Sub, K-V) with a significantly smaller footprint and a proven track record in the legacy stacks.

**Recommendation**: Implement the Hivemind using **Redis Streams** for the event bus and **Redis Hashes** for global state.

---

**Ready for implementation** – agents can now implement the `HivemindBus` class and integrate it into the `Orchestrator`.

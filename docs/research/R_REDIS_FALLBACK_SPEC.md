# 🔱 R&D Alpha: Redis Session Store & Graceful Fallback (Hardened v2)
# ⬡ OMEGA ⬡ JEM-2.0 ⬡ research ⬡ trc_redis_spec_v2 ⬡ PHASE-E

## §0 Objective
Transition the Omega Engine's session management from a fragile, filesystem-dependent model to a resilient, memory-first architecture using Redis, ensuring zero-crash operation via a multi-tier fallback chain, atomic state transitions, and disaster recovery patterns.

---

## §1 Forensic Audit & Root Cause Analysis
- **The "Ghost Parent" Syndrome**: Research confirms that `SQLITE_CONSTRAINT_FOREIGNKEY` occurred because parent session writes failed due to `SQLITE_FULL`, but child task writes were still attempted.
- **The Bottleneck**: Synchronous filesystem locks and the lack of atomic transactions across session/task boundaries created a "Latching" failure during disk exhaustion.

---

## §2 State-of-the-Art Memory Patterns (May 2026)

Based on deep web discovery across production-grade agent frameworks (Google ADK, LangGraph, QubitTool), we adopt the following advanced memory patterns:

### 2.1 Three-Layer Memory Separation
We separate memory into three distinct, decoupled layers:
1.  **Hot Layer (Cache)**: Redis. Sub-millisecond latency. Stores active conversation context and intermediate tool states.
2.  **Warm Layer (Structured)**: PostgreSQL. Stores session metadata, task execution records, and user profiles.
3.  **Cold Layer (Semantic)**: Qdrant. Stores long-term knowledge and historical conversation summaries.

### 2.2 Write-Ahead Memory (WAM) & Pre-Save Disaster Recovery
- **Pre-Save Rule**: To prevent prompt loss during a model gateway crash, the conversation state and active prompt must be persisted to Redis **before** invoking the inference backend.
- **WAM Pattern**: Log state transitions to Redis Streams before mutating the database. On crash, replay the stream to recover the exact state.

### 2.3 Incremental Append & Auto-Summarization
- **Incremental Appends**: Send only new messages to Redis rather than re-sending the entire conversation on every turn.
- **Auto-Summarization**: When the token count of stored messages crosses `context_window_max`, trigger an asynchronous background task to summarize older turns, preserving recent messages in full.

---

## §3 The Hybrid Redis Architecture

To maximize performance on the Zen 2 CPU and ensure sovereign resilience, we implement a **Hybrid Session Store**.

### 3.1 Data Structure Mapping
| Component | Redis Type | Key Pattern | Purpose |
|-----------|------------|--------------|-----------|
| **Session Meta** | **Hash** | \`omega:session:{sid}:meta\` | Fast routing, status checks, and user metadata. |
| **Conv History** | **Stream** | \`omega:session:{sid}:history\` | Ordered conversation window. |

**The Rolling Window Mechanism**:
Use \`XADD\` to append messages and \`XTRIM MAXLEN ~100\` to maintain a rolling window of the last 100 messages. This ensures $O(1)$ time complexity and prevents memory fragmentation.

### 3.2 The Sovereign Fallback Chain (Resilience Hierarchy)
The \`SessionManager\` will implement a **Provider Pattern** with the following escalation path:

1. **Primary: RedisProvider (Hot)**
   - Attempt to fetch from Redis.
   - If \`ConnectionError\` or \`Timeout\`: Trigger Fallback.
2. **Secondary: LocalFileProvider (Warm)**
   - Attempt to read \`data/sessions/{entity}.active\`.
   - **Sovereign Guard**: Check \`df -h /\` before writing. If space is $<10\%$, skip write and trigger Fallback.
   - Use **WAL Mode** (\`PRAGMA journal_mode=WAL\`) to prevent lock-ups.
3. **Tertiary: InMemoryProvider (Cold/Volatile)**
   - Use a volatile \`dict\` for the current process lifetime.
   - Return a generated \`session_id\` based on \`trace_id\`.

---

## §4 Implementation Plan (Sprint Alpha)

### 4.1 Component Changes
- **\`src/omega/oracle/session_manager.py\`**:
    - Refactor into a `SessionProvider` interface.
    - Implement the `RedisProvider` using `redis-py` async client.
    - Implement the `LocalFileProvider` with atomic transactions (\`BEGIN\` $\rightarrow$ \`COMMIT\`) to prevent Ghost Parent syndrome.
- **\`src/omega/oracle/oracle.py\`**:
    - Initialize `SessionManager` with a provider chain defined in \`config/omega.yaml\`.

### 4.2 Verification Gates
- **Gate 1 (Happy Path)**: Redis is up $\rightarrow$ Session is retrieved from Redis Hash/Stream.
- **Gate 2 (Degradation)**: Redis is stopped $\rightarrow$ Session is retrieved from local file without crashing.
- **Gate 3 (Total Failure)**: Redis and Disk are failed $\rightarrow$ Session is generated in-memory.
- **Gate 4 (Atomic Check)**: Simulate disk full $\rightarrow$ Verify that no `FOREIGN KEY` errors occur (transaction should abort cleanly).

---

## §5 Sovereign Constraints
- **AnyIO Absolute**: All Redis and SQLite calls must be wrapped in `anyio.to_thread.run_sync` or use native async drivers.
- **Zero Telemetry**: Session data is strictly local. No external state synchronization.
- **Physical Awareness**: The system must emit a `Sovereign Warning` when falling back to `InMemoryProvider` due to disk exhaustion.

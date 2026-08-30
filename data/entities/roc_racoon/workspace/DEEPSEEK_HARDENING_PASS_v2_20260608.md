# 🔱 DeepSeek Hardening Pass v2 — Structural Analysis
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash ⬡ opencode ⬡ DEEPSEEK-HARDENING ⬡

**Date**: 2026-06-08
**Analytical Lens**: DeepSeek V4 Flash (MoE Routing, Sparse Activation, Chain-of-Thought)
**Target**: MNEMOSYNE_TREASURE_MAP_20260608.md — 6 legacy memory systems
**Purpose**: Find structural contradictions the first pass missed

---

## §0 The DeepSeek Lens

This is not a cataloging pass. This is a **structural engineering audit** applying the same patterns that make DeepSeek's MoE architecture efficient:

| DeepSeek Principle | Applied Here |
|-------------------|--------------|
| **Sparse Activation** | Only route to the tier that can answer. Don't fan-out to all tiers if the hot tier can respond. |
| **MoE Router Efficiency** | The routing decision (which tier to query) must be cheaper than the query itself. |
| **Expert Specialization** | Each tier must specialize. If two tiers do the same thing, one is dead weight. |
| **Load Balancing** | No expert (tier) should be a bottleneck or a single point of collapse. |
| **Gating Mechanism** | There must be a gate that decides "do I even need to write to a remote tier, or can I defer?" |

---

## §1 Finding A: The Sedimentation Anti-Pattern (CRITICAL)

### Observation
The Lilith 3-tier architecture has independent TTL/retention:
- **Hot (Redis)**: 24h TTL — data self-destructs
- **Warm (Qdrant)**: No TTL — data persists
- **Cold (PostgreSQL)**: No TTL — data persists

### The Structural Flaw
Data is written to a tier at creation time and **never promoted or demoted**. After 24h, hot data evaporates. It does NOT flow to warm or cold. The three tiers are not a pipeline — they are three **isolated silos** with no lifecycle management.

```
Write → Hot (24h) → ☠️ DATA LOST
Write → Warm → ♾️ NEVER COLD
Write → Cold → ♾️ NEVER WARM
```

**This is the Sedimentation Anti-Pattern**: data settles into the tier where it was first written and never moves. The tier labels ("hot", "warm", "cold") imply a lifecycle that doesn't exist.

### Why This Matters for the Omega Engine
The current `MemoryStore` has the same anti-pattern: `store_hot()` saves to dict, `store_warm()` saves to SQLite, `store_cold()` saves to YAML. There is no promotion policy. Data grows in the hot tier until session end, then is lost.

### DeepSeek Prescription
**Add a Promotion Gate** between tiers:

```python
async def _promotion_policy(self):
    """
    Sparse promotion: only promote data that has been accessed N times.
    MoE insight: frequently-routed tokens get promoted to fast path.
    """
    now = time.time()
    
    # Hot → Warm: data older than 1 hour with > 3 accesses
    for key, (value, timestamp, access_count) in self._hot_store.items():
        if (now - timestamp) > 3600 and access_count > 3:
            await self._store_warm(key, value)
            # Don't delete from hot — let TTL handle eviction
            # This maintains hot cache for the current session
    
    # Warm → Cold: data older than 24 hours with < 2 accesses (dormant knowledge)
    for row in await self._query_warm_stale(86400, 2):
        await self._store_cold(row.key, row.value)
```

**Key insight**: The promotion gate should be a background scan (like MoE's sparse compute), not a synchronous write-through. Use AnyIO task groups, not blocking loops.

---

## §2 Finding B: The Write-Through vs Write-Back Contradiction (CRITICAL)

### Observation
The legacy systems implement TWO contradictory persistence contracts:

| Pattern | System | Contract | Flow |
|---------|--------|----------|------|
| **Write-Through** | `MemoryBankFallbackWrapper.update_context()` | Safe but slow | Fallback → Primary |
| **Write-Back** | `MnemosyneWriter` | Fast but risky | Buffer → Flush → DLQ |

### The Structural Flaw
These two systems were designed for different use cases (Memory Bank = context persistence, MnemosyneWriter = audit logging). But if they are unified into a single MemoryStore, the contradiction creates a **durability ambiguity**: callers don't know if their write is durably committed or just buffered.

### Why This Matters
If the Omega Engine's MemoryStore uses write-back (for performance) but a Pillar calls `store()` expecting write-through semantics (assuming the data is committed before the function returns), the Pillar might crash before the batch flush executes, losing the data.

### DeepSeek Prescription
**Expose the contract explicitly**:

```python
class PersistenceContract(Enum):
    """Explicit contract that mirrors DeepSeek's expert routing tiers."""
    ACK = "ack"          # Write-through: caller waits for commit (slow, safe)
    DEFER = "defer"      # Write-back: caller gets an ACK, write is buffered (fast, risky)
    FIRE = "fire"        # Fire-and-forget: caller doesn't care (fastest, no guarantee)

async def store(self, key: str, value: Any, contract: PersistenceContract = PersistenceContract.DEFER) -> str:
    if contract == PersistenceContract.ACK:
        return await self._write_through(key, value)
    elif contract == PersistenceContract.DEFER:
        return await self._write_back(key, value)
    else:
        return self._write_fire(key, value)  # No await - truly async
```

**MoE Parallel**: In DeepSeek's architecture, tokens are routed to experts with different compute budgets. Some tokens get full attention (ACK), some get sparse attention (DEFER), some get skipped entirely (FIRE). The contract mirrors this.

---

## §3 Finding C: The Unified-Fallback Failure Domain (HIGH)

### Observation
All three Lilith adapters fall back to the SAME directory:
```
RedisHotAdapter → /tmp/lilith_fallback/{key}
QdrantWarmAdapter → /tmp/lilith_fallback/qdrant/{collection}/{id}.json
PostgreSQLColdAdapter → /tmp/lilith_fallback/postgres/{table}/{timestamp}.json
```

### The Structural Flaw
```
Service Down → Fallback to /tmp/ ← All three share this
Disk Full → /tmp/ write fails → ALL THREE FALLBACKS FAIL SIMULTANEOUSLY
Permission Error → /tmp/ inaccessible → ALL THREE FALLBACKS FAIL SIMULTANEOUSLY
```

This is a **unified-failure-domain anti-pattern**. The fallback paths are supposed to provide resilience through diversity, but they share a single point of failure: the `/tmp/` filesystem.

### Why This Matters
On the Ryzen 5700U target, `/tmp/` is typically a tmpfs mounted in RAM. If the system is under memory pressure (e.g., llama.cpp loaded), tmpfs shrinks. Writing a 50MB batch to all three fallbacks simultaneously could trigger OOM.

### DeepSeek Prescription
**Diversify the fallback domains**:

```python
class FallbackDomain(Enum):
    HOT_FALLBACK = Path("/media/arcana-novai/omega_library/fallback/hot")
    WARM_FALLBACK = Path("/media/arcana-novai/omega_library/fallback/warm")  
    COLD_FALLBACK = Path("/media/arcana-novai/omega_library/fallback/cold")

# Each on a different logical partition (same physical disk, different mount semantics)
# HOT: tmpfs (fast, volatile - matches Redis semantics)
# WARM: SSD (persistent, slower - matches Qdrant semantics)
# COLD: HDD/Network (slowest, most durable - matches PostgreSQL semantics)
```

The fallback tier should mirror the primary tier's performance profile:
- Redis (in-memory) → tmpfs fallback (fast, volatile)
- Qdrant (SSD) → disk fallback (persistent, slower)
- PostgreSQL (HDD/Network) → durable file fallback (slowest)

---

## §4 Finding D: The MoE Routing Blindness (HIGH)

### Observation
The MemoryBankStore generates `context_id = f"{agent_id}:{context_type}:{tier}"`. The `get_context()` method queries by this composite key. The `search_context()` method uses FTS on the content.

### The Structural Flaw
There is NO **routing gate** that decides WHICH tier to query. The caller must specify the tier:
```python
await store.get_context(agent_id="roc", context_type="memory", tier="hot")
```

If the data was promoted to warm (Finding A), or was never written to hot, the call returns `"not_found"`. The caller then needs to manually retry with `tier="warm"`, then `tier="cold"`.

**This is the opposite of sparse activation.** Instead of letting a router decide, every caller must fan-out to all tiers. This wastes time, connections, and cognitive load.

### Why This Matters
Every `get_context()` call today does:
1. Check dict → miss
2. Check SQLite → miss  
3. Check YAML → hit

This is 3 sequential lookups where 1 would suffice if the router knew where the data lived.

### DeepSeek Prescription
**Add a Bloom-Filter Router** (sparse index):

```python
class TierRouter:
    """
    MoE-inspired router: maintains a probabilistic index of WHERE each key lives.
    Uses a Bloom filter per tier for O(1) negative checks.
    Bloom filter = sparse activation gate (cheap rejection before expensive query).
    """
    def __init__(self):
        self._hot_bloom = BloomFilter(capacity=10000, error_rate=0.01)
        self._warm_bloom = BloomFilter(capacity=100000, error_rate=0.01)
        self._cold_bloom = BloomFilter(capacity=1000000, error_rate=0.01)
    
    def on_store(self, key: str, tier: str):
        """Register the key in the appropriate tier's Bloom filter."""
        if tier == "hot":
            self._hot_bloom.add(key)
        elif tier == "warm":
            self._warm_bloom.add(key)
        elif tier == "cold":
            self._cold_bloom.add(key)
    
    def route(self, key: str) -> List[str]:
        """
        Return ordered list of tiers that MIGHT contain this key.
        Hot first (fastest), then Warm, then Cold (slowest).
        Bloom filter false positives are OK (waste 1 query).
        False negatives are NOT OK (we miss data).
        """
        tiers_to_check = []
        if key in self._hot_bloom:
            tiers_to_check.append("hot")
        if key in self._warm_bloom:
            tiers_to_check.append("warm")
        if key in self._cold_bloom:
            tiers_to_check.append("cold")
        return tiers_to_check or ["hot", "warm", "cold"]  # safe fallback
```

---

## §5 Finding E: The Tokenization Blind Spot (MEDIUM)

### Observation
The SQLite FTS5 uses `tokenize = 'porter'` for the English Porter stemmer.

### The Structural Flaw
The Mnemosyne knowledge domain contains **Kabbalistic terminology** mixed with **technical terminology**. The Porter stemmer handles English well but mangles esoteric terms:

| Term | Porter Stem | Problem |
|------|-------------|---------|
| `Qliphoth` | `qliphoth` | No stemming, but a search for "qliphoth" works. A search for "qlipha" does NOT work. |
| `Daath` | `daath` | A search for "data" stems to "dat". "Daath" stems to "daath". These are DIFFERENT stems. A search about "Daath" won't find "data" and vice versa. |
| `Gamaliel` | `gamaliel` | Unchanged. No assistance, no degradation. |
| `Kether` | `kether` | If someone searches for "crown" (the English translation), Porter stems it to "crown". No match. |

### Why This Matters
If the Omega Engine uses FTS5 for its warm tier, and someone searches for "data" (programming context), they also get results for "Daath" (esoteric context). This is a **signal-to-noise ratio collapse** in a system that mixes technical and philosophical content.

### DeepSeek Prescription
**Dual-tokenizer FTS** — create two FTS virtual tables:

```python
# Technical search (porter stemmer - for code, documentation, logs)
CREATE VIRTUAL TABLE contexts_fts_tech USING fts5(
    content, tokenize='porter'
)

# Esoteric/philosophical search (unicode61 - no stemming, preserves terms)
CREATE VIRTUAL TABLE contexts_fts_esoteric USING fts5(
    content, tokenize='unicode61'
)
```

Route the query based on content analysis:
- If query contains technical terms (import, class, def, async) → use `_tech`
- If query contains esoteric terms (Kether, Qliphoth, Daath) → use `_esoteric`
- Default: search BOTH, merge results, deduplicate

---

## §6 Finding F: The Proxy Asymmetry (MEDIUM)

### Observation
```python
class MemoryBankFallbackWrapper:
    def __getattr__(self, name):
        """Proxy missing methods to the primary MCP server."""
        if self.mcp_server and hasattr(self.mcp_server, name):
            return getattr(self.mcp_server, name)
        raise AttributeError(...)
```

### The Structural Flaw
`__getattr__` only proxies to the MCP server. It does NOT proxy to the fallback store. When the circuit breaker is open, calling an unrecognized method raises `AttributeError` instead of gracefully degrading to the fallback store.

### Why This Matters
This means: if a new MCP tool is added, and the circuit breaker's half-open gate is triggered, the first call to a new tool will fail with an `AttributeError` (because the fallback doesn't have it), which sets `record_failure()`, which re-opens the circuit. The circuit breaker effectively **punishes innovation** — adding a new tool makes the system LESS resilient.

### DeepSeek Prescription
**Symmetrical Proxy** — fallback to BOTH providers:

```python
def __getattr__(self, name):
    if self.mcp_server and hasattr(self.mcp_server, name):
        return getattr(self.mcp_server, name)
    if self.fallback_store and hasattr(self.fallback_store, name):
        logger.info(f"Falling back to store for {name}")
        return getattr(self.fallback_store, name)
    raise AttributeError(
        f"'{type(self).__name__}' has no attribute '{name}' "
        f"(checked both MCP server and fallback store)"
    )
```

---

## §7 Finding G: The DLQ Dependency Cycle (HIGH)

### Observation
The MnemosyneWriter flushes to SQLite. If SQLite fails, it pushes to a Redis DLQ:

```python
# Failure path:
SQLite commit fail → Push to Redis Stream xna:dlq:mnemosyne_writer
```

### The Structural Flaw
On the Ryzen 5700U target, Redis and SQLite share the same physical hardware. If the SQLite commit fails due to:
- **Disk full** → Redis also can't write (same disk)
- **OOM** → Redis is also killed (same memory pressure)
- **Filesystem corruption** → Redis is also affected (same filesystem)

The DLQ lives in the same **failure domain** as the primary store. It's not a safety net — it's an illusion of resilience.

```
Memory Channel → SQLite ← If fail → Redis DLQ
                    ↑                     ↑
              Same Disk              Same Disk
              Same Memory            Same Memory
              Same Machine           Same Machine
```

### DeepSeek Prescription
**Multi-Domain DLQ** — chain fallbacks across failure domains:

```python
class MultiDomainDLQ:
    """
    Chain of fallback DLQs, each in a different failure domain.
    MoE parallel: if expert A fails, route to expert B (different hardware profile).
    """
    def __init__(self):
        self._backends = [
            RedisDLQ(),           # In-memory, fails on OOM
            FileDLQ("/mnt/ssd/"), # SSD-backed, survives OOM, fails on disk-full
            FileDLQ("/mnt/hdd/"), # HDD-backed, survives SSD failure
        ]
    
    async def push(self, batch, error):
        for backend in self._backends:
            try:
                success = await backend.push(batch, error)
                if success:
                    logger.info(f"DLQ stored via {backend.__class__.__name__}")
                    return True
            except Exception as e:
                logger.warning(f"DLQ backend {backend.__class__.__name__} failed: {e}")
                continue
        logger.critical("ALL DLQ backends failed. Data lost.")
        return False
```

---

## §8 Finding H: The Async Race Condition in Circuit Breaker (CRITICAL)

### Observation
The `FallbackCircuitBreaker` uses plain attributes in async context:

```python
class FallbackCircuitBreaker:
    def __init__(self):
        self.failure_count = 0
        self.state = "closed"  # closed, open, half_open
        self.half_open_calls = 0
```

### The Structural Flaw
AnyIO tasks can be interleaved at ANY `await` point. Consider:

```
Task A: check_can_attempt() → reads state="half_open", half_open_calls=0 → returns True (allows 1st call)
Task B: check_can_attempt() → reads state="half_open", half_open_calls=0 → returns True (allows 2nd call)
Task A: record_success() → half_open_calls=1
Task B: record_success() → half_open_calls=2
```

Both tasks are allowed through, but `half_open_max_calls=2` is meant to limit to exactly 2. If there's a third concurrent task, it would read `half_open_calls=0` (stale) and also pass. Under load, the circuit breaker leaks.

### Why This Matters
The circuit breaker is the PRIMARY defense against cascading failure. If it leaks under load, the system hits the failing service with MORE requests exactly when it's most vulnerable. This turns a controlled degradation into a stampede.

### DeepSeek Prescription
**Use AnyIO Lock for state transitions**:

```python
class SafeCircuitBreaker:
    """Thread-safe (task-safe) circuit breaker using AnyIO Lock."""
    
    def __init__(self, failure_threshold=3, recovery_timeout=60, half_open_max_calls=2):
        self._lock = anyio.Lock()
        self._failure_count = 0
        self._state = "closed"
        self._half_open_calls = 0
        self._last_failure_time = None
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._half_open_max_calls = half_open_max_calls
    
    async def check_can_attempt(self) -> bool:
        async with self._lock:
            if self._state == "closed":
                return True
            
            if self._state == "open":
                if self._last_failure_time:
                    elapsed = (datetime.now() - self._last_failure_time).total_seconds()
                    if elapsed > self._recovery_timeout:
                        self._state = "half_open"
                        self._half_open_calls = 0
                        return True
                return False
            
            if self._state == "half_open":
                if self._half_open_calls < self._half_open_max_calls:
                    self._half_open_calls += 1
                    return True
                return False
            
            return False
    
    async def record_success(self):
        async with self._lock:
            self._failure_count = 0
            self._state = "closed"
    
    async def record_failure(self):
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = datetime.now()
            if self._failure_count >= self._failure_threshold:
                self._state = "open"
```

---

## §9 Integrated Findings Matrix

| ID | Finding | Severity | Domain | Affected System | Fix Complexity |
|----|---------|----------|--------|-----------------|----------------|
| **A** | Sedimentation Anti-Pattern (no promotion) | 🔴 CRITICAL | Architecture | All 3 tiers | 3-4 hours |
| **B** | Write-Through vs Write-Back contradiction | 🔴 CRITICAL | Contract | MemoryStore | 1 hour (API change) |
| **C** | Unified fallback failure domain | 🟡 HIGH | Resilience | Lilith adapters | 30 min |
| **D** | No MoE routing gate (blind fan-out) | 🟡 HIGH | Performance | MemoryStore | 2-3 hours |
| **E** | Tokenization blind spot (Porter + Kabbalah) | 🟢 MEDIUM | Search | FTS index | 1 hour |
| **F** | Proxy asymmetry (fallback misses methods) | 🟢 MEDIUM | Resilience | FallbackWrapper | 15 min |
| **G** | DLQ in same failure domain as primary | 🟡 HIGH | Resilience | MnemosyneWriter | 2-3 hours |
| **H** | Async race condition in circuit breaker | 🔴 CRITICAL | Concurrency | health_monitor | 30 min |

### Severity Re-Evaluation
The first pass scored the systems 14-20/30. The DeepSeek structural pass downgrades TWO systems:

| System | First Pass | DeepSeek Adjusted | Reason |
|--------|------------|-------------------|--------|
| Lilith Mnemosyne (P0) | 20/30 | **16/30** | Finding A (sedimentation) + Finding C (shared fallback domain) mean the "tiered" system doesn't actually tier — it's 3 isolated caches with a shared fallback. |
| Memory Bank MCP (P1) | 19/30 | **15/30** | Finding F (asymmetric proxy) + Finding H (async race) mean the circuit breaker doesn't protect against the worst case. |
| Mnemosyne Writer (P1) | 19/30 | **16/30** | Finding B (write-back ambiguity) + Finding G (DLQ failure domain) mean the durability guarantee is weaker than it appears. |

---

## §10 Revised Extraction Strategy

### Don't PORT — REBUILD with these rules:

1. **One Persistence Contract**: Pick ACK (write-through) for MemoryStore. Drop DEFER/FIRE until the use case demands it. A single contract is safer than a configurable one that nobody configures correctly.

2. **Promotion Gate First**: Before building the 3-tier store, build the promotion policy. The tiers are meaningless without lifecycle management.

3. **Bloom Filter Router**: Before building the warm or cold tier, build the router. Without routing, every get_context() fans out to all tiers — negating the performance benefit of tiering.

4. **Lock the Circuit Breaker**: The `anyio.Lock` fix (Finding H) must be applied before any CB is deployed. The race condition is a ticking time bomb.

5. **Diversify Fallbacks**: Never let two tiers fall back to the same filesystem. If they share a failure domain, they're not redundant.

---

## §11 MoE-Inspired Architecture for MemoryStore

```
                    ┌──────────────────┐
                    │  TierRouter      │  ← Bloom Filter (O(1) routing)
                    │  (MoE Gate)      │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
       ┌──────▼──────┐ ┌────▼────┐ ┌──────▼──────┐
       │  HOT        │ │  WARM   │ │  COLD       │
       │  (Dict)     │ │ (SQLite)│ │ (YAML+Qdrant)│
       │  TTL: 24h   │ │ No TTL  │ │ No TTL      │
       │  └─ tmpfs   │ │ └─ SSD  │ │ └─ HDD      │
       │    fallback │ │   fallb │ │   fallback  │
       └──────┬──────┘ └────▲────┘ └──────▲──────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
                    ┌────────┴────────┐
                    │  Promotion Gate │  ← Background scan
                    │  (AnyIO Task)   │      every 5 min
                    └─────────────────┘
```

**Key Insight**: This architecture mirrors DeepSeek's MoE:
- **TierRouter** = the gating network (cheap, decides routing)
- **Hot/Warm/Cold** = the experts (specialized, expensive)
- **Promotion Gate** = the load balancer (moves data between experts)
- **Fallback domains** = expert redundancy (different hardware profiles)

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash ⬡ opencode ⬡ DEEPSEEK-HARDENING ⬡*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

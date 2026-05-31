# 🔱 Omega Engine — Memory Pruner Agent: Design & Strategy

**AP Token**: `AP-MEMORY-PRUNER-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ big-pickle ⬡ opencode ⬡ trc_research ⬡ R-MEMORY-PRUNER

**Status**: DRAFT | **Last Updated**: 2026-05-17
**Research Method**: Multi-provider web synthesis (Tavily + Browser Search + Academic Papers)
**Sources Cross-Referenced**: 20+ papers, 8 production implementations, 5 open-source codebases

---

## Executive Summary (L1)

This document defines the **BackgroundPruner** — a scheduled agent that manages the Omega Engine's Hot/Warm/Cold memory tiers. The design is based on synthesis of production patterns from OpenClaw compaction, Redis Agent Memory Server lifecycle management, AutoMem consolidation engine, and academic research on MemTier tiered memory, KV cache hierarchy, and incremental summarization.

**Key Design Decisions**:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Pruning model | **Qwen3-0.6B** (local) for summarization; Gemma 4-26B via Google API for deep compaction | 0.6B fits in ~1.2GB RAM, runs entirely local, ~30 tok/s on Zen 2 |
| Trigger model | **Event-driven + Scheduled** (dual path) | Event cap-enforcement for active users; background sweep for inactive |
| Retention policy | **Hot: hours, Warm: days, Cold: months** with graceful decay | Mirrors human forgetting curve (Ebbinghaus) |
| Deduplication | **Semantic + Lexical** hybrid on background schedule | Semantic catches conceptual duplicates; lexical catches exact repeats |
| Memory budget | **14GB RAM hard cap** with tier budgets: Hot 2GB, Warm 4GB, Cold 8GB (disk) | Based on Omega Engine hardware target (Ryzen 5700U, 14GB total) |
| Summarization | **Anchored iterative** (not full reconstruction) | Factory's evaluation: anchored iterative scores 4.04 vs 3.74 full reconstruction on accuracy |

**Bottom Line**: A BackgroundPruner running every 15-30 minutes can reduce active memory footprint by 60-80% while preserving 95%+ information continuity, based on MemTier benchmarks and production OpenClaw deployments.

---

## §1 BackgroundPruner Agent Architecture (L2)

### 1.1 Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  BackgroundPruner Scheduler                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Event-Driven │  │  Scheduled  │  │   Manual Trigger    │  │
│  │ (per write)  │  │ (15-30 min) │  │ (omega prune now)   │  │
│  └──────┬───────┘  └──────┬──────┘  └─────────┬───────────┘  │
│         │                 │                    │              │
│         └─────────────────┴────────────────────┘              │
│                            │                                  │
│                     ┌──────▼──────┐                           │
│                     │ PrunerOrch  │                           │
│                     │  estrator   │                           │
│                     └──────┬──────┘                           │
└────────────────────────────┼─────────────────────────────────┘
                             │
       ┌─────────────────────┼─────────────────────┐
       │                     │                     │
┌──────▼──────┐    ┌─────────▼─────────┐   ┌──────▼──────┐
│  Hot → Warm  │    │ Warm → Cold      │   │  Cold →     │
│  Flusher     │    │ Archiver         │   │  Expunge    │
└──────┬──────┘    └─────────┬─────────┘   └──────┬──────┘
       │                     │                     │
       │              ┌──────▼──────┐              │
       │              │ Compactor   │              │
       │              │ (Summarizer)│              │
       │              └──────┬──────┘              │
       │                     │                     │
       │              ┌──────▼──────┐              │
       │              │ DedupEngine │              │
       │              └──────┬──────┘              │
       │                     │                     │
       └─────────────────────┼─────────────────────┘
                             │
                     ┌───────▼────────┐
                     │ Audit Logger   │
                     │ (pruner.db)    │
                     └────────────────┘
```

### 1.2 Core Classes

```python
class BackgroundPruner:
    """Sovereign background memory pruner for Hot/Warm/Cold tiers.
    
    Runs on configurable schedule + event-driven triggers. Each pruning
    cycle is atomic, auditable, and bounded by ResourceGuard for OOM protection.
    """
    
    # Configurable schedules
    SCHEDULE_CONFIG = {
        "hot_to_warm_interval": 300,      # 5 min — flush inactive hot sessions
        "warm_to_cold_interval": 3600,    # 1 hr — archive old warm sessions
        "dedup_interval": 7200,           # 2 hr — semantic dedup sweep
        "deep_compact_interval": 43200,   # 12 hr — deep compaction (Gemma)
        "cold_expunge_interval": 86400,   # 24 hr — delete expired cold entries
    }
    
    # Retention policies (configurable per entity)
    RETENTION = {
        "hot": {"ttl_minutes": 180, "max_exchanges": 20, "max_sessions": 50},
        "warm": {"ttl_days": 14, "max_sessions_per_entity": 100},
        "cold": {"ttl_months": 6, "max_archives_per_entity": 1000},
    }
```

#### Tier Promotion Rules

```
Hot (RAM, ~2GB budget)
  ├── Active within last 3 hours
  ├── ≤20 exchanges per session
  ├── ≤50 sessions total
  ├── Eviction: LRU when full (oldest unaccessed session → Warm)
  └── Promotion: accessed session moves to front of LRU

Warm (Disk JSON, ~4GB budget)
  ├── Active within last 14 days
  ├── ≤100 sessions per entity
  ├── ≥3 hours since last activity
  ├── Eviction: age-based + importance scoring → Cold archive
  └── Promotion: re-accessed → Hot (promoted on next get_history)

Cold (Gzip on disk, ~8GB budget)
  ├── Active within last 6 months
  ├── ≤1000 archives per entity
  ├── Summarized representation (not full exchanges)
  ├── Eviction: TTL expiry → hard delete
  └── Retrieval: on explicit user request only (not auto-injected)
```

---

## §2 Pruning Rules Engine (L2)

### 2.1 Rule Priority Chain

Each memory entry is evaluated through a cascading rule system:

```
For each memory entry:
  1. PROTECTED? → Skip pruning entirely
  2. IMPORTANT? → Boost retention score, keep in tier longer
  3. ACCESSED? → Freshness bonus, extend TTL
  4. AGE? → Apply decay curve
  5. DUPLICATE? → Merge or discard lower-score version
  6. BUDGET? → Evict lowest-scoring entries when tier exceeds budget
```

### 2.2 Retention Scoring Formula

Adopted from MemTier (arXiv:2605.03675) and semantic-router's quality scoring:

```
R = w₁ · exp(-λ · Δt) + w₂ · (CW + 1)/2 + w₃ · access_freq + w₄ · semantic_boost

Where:
  Δt       = time since last access (days)
  λ        = decay rate (0.05 for warm, 0.01 for cold — half-life ~14 days)
  CW       = cognitive weight (-1 to 1, based on tool success/failure)
  access   = normalized access frequency (0 to 1)
  semantic = semantic relevance to known user interests (0 to 1)
  w₁..w₄   = configurable weights (default: 0.4, 0.3, 0.2, 0.1)
```

**Thresholds**:
- R > 0.7: Keep in current tier
- 0.3 < R ≤ 0.7: Candidate for demotion to next tier
- R ≤ 0.3: Candidate for deletion (after grace period)

### 2.3 Protection Rules

Certain memories are **never pruned** without explicit user confirmation:

```python
PROTECTED_MEMORY_TYPES = [
    "user_preference",       # "I prefer dark mode", "My name is Arch"
    "system_configuration",  # API keys, provider configs
    "explicit_savepoint",    # User said "remember this"
    "entity_identity",       # Entity's core knowledge about itself
    "arch_soul_entry",       # Architect's soul.yaml experiences
]

# Protection metadata fields:
PROTECTION_META = {
    "protected": True,
    "protected_reason": "user_explicit_savepoint",
    "protected_by": "user",  # or "system", "entity"
    "protected_at": "2026-05-17T00:00:00Z",
    "grace_period_until": None,  # None = permanent
}
```

### 2.4 Grace Periods

| Operation | Grace Period | Purpose |
|-----------|-------------|---------|
| Hot → Warm demotion | 0 (immediate flush OK) | Hot is volatile by design |
| Warm → Cold archiving | 7 days soft-delete | Allow undo before finalizing |
| Cold → Deletion | 30 days soft-delete | Safety net — recoverable via audit log |
| Dedup merge | 1 review cycle | Flag duplicates, don't auto-delete |

Soft-delete: memory is marked `deleted_at` but remains in storage. After grace period, a subsequent sweep performs hard delete.

---

## §3 Summarization Strategy (L2)

### 3.1 Anchored Iterative Summarization (Preferred)

Based on Factory's evaluation of 36,000 real engineering sessions (published 2026-02-28):

**Why not full reconstruction**: Full summarization from scratch is 2-3× more expensive per token, loses more detail (accuracy: 3.74 vs 4.04), and doesn't preserve continuity across compaction cycles.

**How it works**:

```
Anchor State (always preserved):
  intent: str          # Original user goal
  changes_made: []     # Key changes applied
  decisions: []        # Decisions with rationale
  next_steps: []       # Pending work
  key_facts: {}        # Important discovered facts

On compaction trigger:
  1. Identify the span of messages being evicted (oldest N exchanges)
  2. Summarize only that span using Qwen3-0.6B
  3. Merge the new summary into the anchor state:
     - Update decisions if new ones override old ones
     - Add new key_facts (dedup by semantic similarity)
     - Update next_steps (remove completed, add new)
     - Preserve intent unless explicitly changed
  4. Replace evicted span with "[N messages compacted: <summary>]"
  5. The anchor + recent messages + compacted markers = new context
```

**Anchor schema**:

```python
SUMMARY_ANCHOR_SCHEMA = {
    "summary_version": 1,
    "last_compacted": "2026-05-17T12:00:00Z",
    "compaction_count": 3,
    "original_intent": "Build BackgroundPruner for Omega Engine",
    "decisions": [
        {"decision": "Use Qwen3-0.6B for local compaction",
         "rationale": "Fits in 1.2GB RAM, ~30 tok/s on Zen 2",
         "timestamp": "2026-05-17T10:00:00Z",
         "status": "implemented"}
    ],
    "key_facts": {
        "memory_budget": "14GB total RAM",
        "primary_model": "Qwen3-0.6B",
    },
    "next_steps": [
        "Wire BackgroundPruner into Oracle startup",
        "Add monitoring dashboard for pruner stats"
    ],
    "state_variables": {
        "current_phase": "design",
        "active_branch": "main",
    }
}
```

### 3.2 Model Selection for Compaction

| Model | Size | RAM | Tok/s (Zen 2) | Use Case | Provider |
|-------|------|-----|---------------|----------|----------|
| **Qwen3-0.6B** | 0.6B | ~1.2GB | ~30 | Regular compaction, dedup scoring | Local (lmster/GGUF) |
| **Qwen3-4B-Think** | 4B | ~8GB | ~8 | Deep compaction, anchor summarization | Local (on-demand) |
| **Gemma 4-26B-a4b** | 26B | N/A | N/A | Deep archive indexing, quarterly cleanup | Google API (remote) |

**Primary path**: Qwen3-0.6B for all routine compaction (every 15-30 min). It has sufficient summarization capability for the compact task, as shown by the DUET research (arXiv:2605.01111) where 0.6B models successfully decode compressed representations from larger models.

**Escalation path**: When Qwen3-0.6B confidence < 0.7 (detected via perplexity or length of output), escalate to Qwen3-4B-Think for deeper summarization.

**Deep compaction path**: Gemma 4-26B for monthly archive indexing and semantic cluster analysis (via Google API, only when budget allows).

### 3.3 Compaction Prompt Templates

```python
# ── Lightweight compaction (runs every 15-30 min) ──
COMPACT_SYSTEM_PROMPT = """You are a memory compaction specialist. Compress the following
conversation exchanges into a minimal but information-preserving summary. Focus on:
1. Key decisions made (with rationale)
2. Important facts discovered
3. Current state / pending work
4. Changes from previous anchor state (if provided)

Output as JSON with keys: "summary", "decisions", "key_facts", "next_steps"

Previous anchor state:
{anchor_state}

New exchanges to compact:
{exchanges}"""

# ── Deep compaction (runs every 12 hours) ──
DEEP_COMPACT_PROMPT = """You are performing deep memory consolidation. Review the entire
session history and the current anchor state. Identify:
1. Outdated decisions that should be superseded
2. Redundant facts that can be merged
3. Patterns across multiple compaction cycles
4. Information that can be safely discarded

Current anchor: {anchor}
Full session summary: {full_summary}
New exchanges since last deep compact: {new_exchanges}"""
```

---

## §4 Deduplication Engine (L2)

### 4.1 Two-Pass Deduplication

**Pass 1 — Lexical (fast, runs every cycle)**:

```python
def lexical_dedup(exchanges: List[Dict]) -> List[Dict]:
    """Remove exact duplicate exchanges (same user message + same response)."""
    seen_hashes = set()
    deduped = []
    for ex in exchanges:
        # Hash on normalized user + assistant content
        content = f"{ex.get('user','')}|{ex.get('assistant','')}"
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        if content_hash not in seen_hashes:
            seen_hashes.add(content_hash)
            deduped.append(ex)
    return deduped
```

**Pass 2 — Semantic (expensive, runs every 2 hours)**:

```python
async def semantic_dedup(exchanges: List[Dict], threshold: float = 0.92) -> List[Dict]:
    """Cluster semantically similar exchanges and keep the most complete version.
    
    Uses Qwen3-0.6B embeddings (384d) computed lazily and cached.
    Similarity via cosine distance on embedding vectors.
    """
    # 1. Compute embeddings for each exchange (batch, 32 at a time)
    # 2. Cluster by cosine similarity > threshold
    # 3. Within each cluster, keep the exchange with highest information density
    #    (longer response + more unique entities mentioned)
    # 4. Merge: if cluster has complementary facts, merge into one exchange
    # 5. Return deduplicated + merged exchanges
```

**Research basis**: Production systems report 30-40% memory store reduction from semantic dedup alone, and up to 99.3% compression when combined with aggressive subatom extraction (Tianpan, 2026-04-14). We target **30% reduction** from semantic dedup with conservative thresholds (0.92 similarity).

### 4.2 Duplicate Scoring

Each candidate duplicate cluster gets a **merge score**:

```
M = completeness × recency × fact_density

completeness = len(response) / max_len_in_cluster
recency = 1 / (1 + days_since_last_access)
fact_density = unique_entities / total_tokens
```

Keep the exchange with highest M; merge complementary facts into it; discard others.

---

## §5 Retention Policies — Per-Tier Detail (L2)

### 5.1 Hot Tier (RAM)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Capacity | 50 sessions max | Matches current `MAX_HOT_SESSIONS` |
| TTL | 3 hours without access | Human working memory duration |
| Max exchanges/session | 20 | Matches current `MAX_HISTORY` |
| Eviction | LRU | Most recently accessed = most likely to be needed again |
| Budget | ~2GB RAM | Based on 14GB total, leaving 12GB for models |
| Flush trigger | Session inactive > 3h OR hot cache full (50) | Dual trigger for responsiveness |

**Flush behavior**: When a session is evicted from hot → warm:
1. Write full exchanges to warm JSON (same as current `add_exchange`)
2. If warm already has this session, append only new exchanges
3. Update `last_accessed` metadata
4. Remove from `_hot` OrderedDict

### 5.2 Warm Tier (Disk — JSON)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Capacity | 100 sessions per entity | Prevents unbounded growth per entity |
| TTL | 14 days without access | Monthly arc — covers typical project duration |
| Format | JSON with full exchanges | Enables reconstruction for retrieval |
| Budget | ~4GB disk | 100 sessions × 40KB avg = 4MB per entity × 10 entities = ~40MB; 4GB is generous |
| Archival trigger | >14 days since last access | Based on AI data patterns: "cold" means 6-12 months inactive |
| Summarization | On archival to cold | Full exchanges → compacted summary + anchor state |

**Archive behavior**:
1. If >14 days since last access → candidate for cold
2. Before archiving, run anchored iterative summarization using Qwen3-0.6B
3. Store only: anchor state JSON + last 3 exchanges (for continuity) + metadata
4. Compress with gzip (current behavior preserved)
5. Update entity's session index

### 5.3 Cold Tier (Disk — Gzip)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Capacity | 1000 archives per entity | Long-term reference |
| TTL | 6 months without access | Extended but not indefinite |
| Format | Gzipped JSON (anchor + 3 exchanges) | Maximum compression, minimal retrieval |
| Budget | ~8GB disk | 1000 × 5KB avg = 5MB per entity; 8GB should never be reached |
| Expunge trigger | >6 months AND R < 0.2 | Only expire if low importance AND old |
| Deep compact | Every 30 days | Re-compress old archives periodically |

**Expunge behavior**:
1. Mark as `deleted_at` = timestamp (soft delete)
2. Move to `.trash/` directory
3. After 30-day grace period, hard delete
4. Log to audit database

### 5.4 Entity-Overridable Policies

Entities can override retention policies in their `soul.yaml`:

```yaml
# Example: Brigid's soul.yaml override
memory_policy:
  hot_ttl_minutes: 60          # Brigid's creative sessions are shorter
  warm_ttl_days: 7             # Poetry inspiration fades faster
  cold_ttl_months: 12          # But keep seasonal inspiration for a year
  protected_types:
    - user_preference
    - poem          # Don't prune Brigid's poems
  compaction_model: "qwen3-0.6b"  # Use lightweight model for Brigid
```

Default is `config/omega.yaml` global policies. Entity overrides are deep-merged (same pattern as OpenClaw's per-agent compaction, PR #19329).

---

## §6 Budget Enforcement — 14GB RAM Cap (L2)

### 6.1 Budget Allocation

```
Total System RAM: 14GB
Reserved for OS:  2GB (Ubuntu minimal ~800MB, but leave headroom)
Available for AI: 12GB

Memory Tier Budgets:
  Hot Cache:       2GB (50 sessions × avg 40KB = 2MB normally; 2GB ceiling)
  Active Model:    4GB (Qwen3-4B at ~8GB is too much; Qwen3-0.6B at 1.2GB; leave room)
  KV Cache:        2GB (for active inference)
  Embeddings:      1GB (for Qdrant/vector cache)
  Scratch:         3GB (unallocated, OS file cache, podman containers)
```

### 6.2 Budget Monitoring

```python
async def check_memory_budget() -> Dict[str, float]:
    """Return current memory usage per tier."""
    import psutil
    process = psutil.Process()
    mem = process.memory_info()
    
    # Rough tier breakdown based on Python object sizes
    hot_size = await estimate_hot_cache_size()
    warm_size = await estimate_warm_disk_cache()
    
    return {
        "rss_mb": mem.rss / 1024 / 1024,
        "vms_mb": mem.vms / 1024 / 1024,
        "hot_cache_mb": hot_size,
        "hot_pct": (hot_size / 2048) * 100,  # 2GB budget
        "warm_cache_mb": warm_size,
        "overall_pct": (mem.rss / 1024 / 1024 / 12288) * 100,  # 12GB budget
    }
```

### 6.3 Budget Enforcement

When any tier exceeds 80% of its budget:

| Level | Threshold | Action |
|-------|-----------|--------|
| **Green** | < 60% | Normal operation |
| **Yellow** | 60-80% | Aggressive pruning cycle, skip non-essential operations |
| **Orange** | 80-95% | Emergency compaction: flush oldest sessions immediately, reduce model size |
| **Red** | > 95% | Critical: trigger OOM prevention, flush hot cache to disk, unload models |

```python
async def enforce_budget():
    """Called before each inference to ensure memory headroom."""
    budget = await check_memory_budget()
    
    if budget["overall_pct"] > 95:
        # Red: Emergency — flush everything non-critical
        logger.critical("Memory budget critical! Forcing emergency flush.")
        await force_flush_hot_cache()
        await unload_models(keep="qwen3-0.6b")
        await clear_embedding_cache()
        
    elif budget["overall_pct"] > 80:
        # Orange: Aggressive compaction
        logger.warning("Memory budget exceeded 80%. Running aggressive compaction.")
        await BackgroundPruner().run_aggressive_cycle()
```

---

## §7 Integration with Existing Code (L2)

### 7.1 MemoryStore Extension Points

The current `MemoryStore` class (`src/omega/memory_store.py`) already has the right structure. The BackgroundPruner will extend it with:

| Method | Purpose | Hook Point |
|--------|---------|------------|
| `_compact()` | Already exists — needs LLM-based summarization | Replace placeholder with anchored iterative summary |
| `archive_old_sessions()` | Already exists — needs retention scoring | Add R-score check before archiving |
| `archive_session()` | Already exists — needs anchor state | Store anchor + summary instead of full exchanges |
| (new) `deduplicate_exchanges()` | Semantic dedup | Called by Pruner, not MemoryStore directly |
| (new) `estimate_memory_budget()` | Budget monitoring | Called by Pruner before/after each cycle |

### 7.2 Session Gnosis Integration

The BackgroundPruner interacts with `session_gnosis.md` in three ways:

1. **Read session gnosis** to understand what was learned in compacted sessions (prevents loss of important lessons)
2. **Write pruning decisions** to the session gnosis so the user can audit what was pruned
3. **Cross-reference protected entries** in session gnosis to prevent accidental deletion

```python
class SessionGnosisBridge:
    """Bridge between BackgroundPruner and session_gnosis.md."""
    
    async def get_protected_topics(self, entity_name: str) -> List[str]:
        """Read session_gnosis.md to find protected topics."""
        gnosis_path = Path(f"data/gnosis/session_gnosis.md")
        if not gnosis_path.exists():
            return []
        content = await anyio.Path(gnosis_path).read_text()
        # Extract ## Protected Topics section
        # Return list of topics that should never be pruned
    
    async def record_pruning_event(self, event: Dict):
        """Append pruning decision to session gnosis."""
        entry = (
            f"### Pruning Event {event['timestamp']}\n"
            f"- **Action**: {event['action']}\n"
            f"- **Entity**: {event['entity_name']}\n"
            f"- **Session**: {event['session_id']}\n"
            f"- **Reason**: {event['reason']}\n"
            f"- **Pre-save R-score**: {event['r_score_before']:.3f}\n"
            f"- **Size saved**: {event['bytes_saved']} bytes\n"
        )
        gnosis_path = Path(f"data/gnosis/session_gnosis.md")
        async with await anyio.open_file(str(gnosis_path), "a") as f:
            await f.write(entry)
```

### 7.3 ContextBuilder Integration

The BackgroundPruner should NOT modify `ContextBuilder` directly. ContextBuilder reads from MemoryStore, and MemoryStore serves the data that the Pruner has organized. The flow is:

```
Session produces exchanges
  → MemoryStore.add_exchange() stores in Hot
  → BackgroundPruner runs cycle
    → Hot to Warm (LRU eviction)
    → Warm to Cold (age + importance)
    → Cold to Deletion (TTL + grace period)
  → ContextBuilder.build_context() reads from Hot → Warm → Cold
  → Data served to Entity
```

This means Pruner changes are transparent to ContextBuilder — it just sees well-organized tiers.

---

## §8 Scheduling Architecture (L3)

### 8.1 Dual-Path Trigger System

**Path 1: Event-Driven (for active users)**

```python
async def on_memory_write(entity_name: str, session_id: str):
    """Called after every MemoryStore.add_exchange()."""
    # Fast path: check if hot cache is over budget
    if len(memory_store._hot) > MAX_HOT_SESSIONS * 0.8:
        # Schedule async flush (don't block the write path)
        asyncio.create_task(BackgroundPruner.flush_hot_to_warm())
    
    # Check if user has too many warm sessions
    warm_count = await count_warm_sessions(entity_name)
    if warm_count > 80:  # 80% of 100 cap
        asyncio.create_task(BackgroundPruner.archive_warm_to_cold(entity_name))
```

**Path 2: Scheduled (background sweep)**

```python
async def scheduled_cycle():
    """Full pruning cycle. Runs on configurable cron schedule."""
    logger.info("Starting scheduled pruning cycle")
    
    # Phase 1: Hot → Warm (flush inactive sessions)
    flushed = await BackgroundPruner.flush_inactive_hot_sessions()
    
    # Phase 2: Warm → Cold (archive old sessions)
    archived = await BackgroundPruner.archive_aged_warm_sessions()
    
    # Phase 3: Deduplication
    deduped = await BackgroundPruner.run_dedup_sweep()
    
    # Phase 4: Deep compaction (if due)
    if await is_deep_compact_due():
        await BackgroundPruner.run_deep_compaction()
    
    # Phase 5: Cold expunge (if due)
    expunged = await BackgroundPruner.expunge_expired_cold()
    
    # Phase 6: Audit
    await BackgroundPruner.log_cycle({
        "hot_flushed": flushed,
        "warm_archived": archived,
        "dedup_merged": deduped,
        "cold_expunged": expunged,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": elapsed,
        "memory_before": before_budget,
        "memory_after": after_budget,
    })
```

### 8.2 Cron Schedule Configuration

```yaml
# config/omega.yaml
memory_pruner:
  enabled: true
  resource_guard: true           # Respect ResourceGuard semaphore
  schedules:
    hot_to_warm: "*/5 * * * *"  # Every 5 minutes
    warm_to_cold: "0 * * * *"   # Every hour
    dedup: "0 */2 * * *"        # Every 2 hours
    deep_compact: "0 */12 * * *" # Every 12 hours
    cold_expunge: "0 3 * * *"   # Daily at 3 AM
    budget_check: "*/1 * * * *" # Every minute (lightweight)
  budgets:
    hot_cache_mb: 2048
    warm_disk_mb: 4096
    cold_disk_mb: 8192
    model_ram_mb: 4096
  models:
    compaction: "qwen3-0.6b"     # Local model for compaction
    deep_compaction: "qwen3-4b-think"  # On-demand for deep compaction
    semantic_dedup: "qwen3-0.6b" # Same as compaction
```

### 8.3 ResourceGuard Integration

The BackgroundPruner must respect the existing `ResourceGuard` semaphore to prevent OOM:

```python
class BackgroundPruner:
    def __init__(self, resource_guard: ResourceGuard):
        self.resource_guard = resource_guard
        self._cycle_lock = anyio.Lock()
    
    async def run_compaction(self, exchanges: List[Dict]) -> List[Dict]:
        """Run LLM-based compaction with ResourceGuard protection."""
        async with self.resource_guard:
            # Only one model inference at a time
            result = await self._call_compaction_model(exchanges)
        return result
    
    async def scheduled_cycle(self):
        """Full cycle — protected by cycle lock (no concurrent cycles)."""
        async with self._cycle_lock:
            await self._execute_cycle()
```

---

## §9 Monitoring & Audit Logging (L3)

### 9.1 Audit Database Schema

```sql
-- data/pruner/pruner_audit.db (SQLite)
CREATE TABLE pruning_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,           -- ISO 8601
    cycle_id TEXT NOT NULL,            -- Groups events from same cycle
    action TEXT NOT NULL,              -- 'hot_to_warm' | 'warm_to_cold' | 'dedup_merge' | 'cold_expunge'
    entity_name TEXT NOT NULL,
    session_id TEXT,
    reason TEXT NOT NULL,              -- 'lru_eviction' | 'age_ttl' | 'budget_cap' | 'semantic_duplicate'
    r_score_before REAL,               -- Retention score before action
    exchanges_before INTEGER,          -- Count before
    exchanges_after INTEGER,           -- Count after
    bytes_before INTEGER,              -- Size before
    bytes_after INTEGER,               -- Size after
    bytes_saved INTEGER,               -- bytes_before - bytes_after
    model_used TEXT,                   -- 'qwen3-0.6b' | 'qwen3-4b-think' | 'none'
    duration_ms INTEGER,
    metadata TEXT                      -- JSON blob for extensibility
);

CREATE TABLE protected_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_name TEXT NOT NULL,
    session_id TEXT NOT NULL,
    exchange_hash TEXT NOT NULL UNIQUE, -- SHA256 of content
    protected_type TEXT NOT NULL,
    protected_by TEXT NOT NULL,
    protected_at TEXT NOT NULL,
    expires_at TEXT,                   -- NULL = permanent
    reason TEXT
);

CREATE TABLE budget_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    cycle_id TEXT,
    hot_cache_mb REAL,
    warm_disk_mb REAL,
    cold_disk_mb REAL,
    model_ram_mb REAL,
    overall_pct REAL,
    alert_level TEXT                   -- 'green' | 'yellow' | 'orange' | 'red'
);
```

### 9.2 CLI Audit Commands

```bash
omega pruner status           # Show pruner status (enabled/disabled, last cycle, next cycle)
omega pruner history --last=10  # Show last N pruning events
omega pruner protect "topic"  # Add a protected topic
omega pruner undo --event=42  # Undo a pruning event (restore from trash)
omega pruner budget           # Show current memory budget usage
omega pruner run --dry-run    # Run a cycle without actually pruning
```

### 9.3 Observability Events

New `EventType` constants for observability:

```python
class EventType(str, Enum):
    PRUNER_CYCLE_START = "pruner_cycle_start"
    PRUNER_CYCLE_COMPLETE = "pruner_cycle_complete"
    PRUNER_HOT_FLUSH = "pruner_hot_flush"
    PRUNER_WARM_ARCHIVE = "pruner_warm_archive"
    PRUNER_DEDUP_MERGE = "pruner_dedup_merge"
    PRUNER_COLD_EXPUNGE = "pruner_cold_expunge"
    PRUNER_BUDGET_WARNING = "pruner_budget_warning"  # > 80%
    PRUNER_BUDGET_CRITICAL = "pruner_budget_critical"  # > 95%
    PRUNER_PROTECTED_SKIP = "pruner_protected_skip"  # Skipped a protected entry
```

---

## §10 Safety Mechanisms (L3)

### 10.1 Multi-Layer Safety

| Layer | Mechanism | What It Prevents |
|-------|-----------|-----------------|
| 1. Protection | Protected types never pruned | Loss of user preferences, identity |
| 2. Grace periods | Soft-delete before hard-delete | Accidental deletion recovery |
| 3. Dry-run mode | `--dry-run` flag shows what would happen | Testing before enabling |
| 4. Budget floor | Hard min: never prune below 10 exchanges | Empty memory |
| 5. Audit trail | All events logged with undo capability | Regret recovery |
| 6. Circuit breaker | 3 failed cycles → pruner disables | Infinite loop protection |
| 7. User confirm | Protected deletion requires user OK | User sovereignty |
| 8. Session gnosis sync | Cross-ref before pruning important lessons | Knowledge continuity |

### 10.2 Circuit Breaker

```python
class PrunerCircuitBreaker:
    """Stops the pruner if it fails or causes degradation."""
    
    MAX_CONSECUTIVE_FAILURES = 3
    MAX_BYTES_REMOVED_PER_CYCLE = 100 * 1024 * 1024  # 100MB
    COOLDOWN_MINUTES = 30
    
    def __init__(self):
        self.consecutive_failures = 0
        self.last_failure_time = None
        self.is_open = False
    
    async def record_failure(self, error: str):
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        if self.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
            self.is_open = True
            logger.critical(f"Pruner circuit breaker OPEN after {self.consecutive_failures} failures")
            # Alert user via observability
    
    async def record_success(self):
        self.consecutive_failures = 0
        self.is_open = False
```

### 10.3 Undo Mechanism

```python
async def undo_pruning_event(event_id: int) -> bool:
    """Restore a pruned memory from its soft-delete location."""
    event = await audit_db.fetch_one(
        "SELECT * FROM pruning_events WHERE id = ?", (event_id,)
    )
    if not event:
        return False
    
    # For cold_expunge actions, check trash directory
    if event.action == "cold_expunge":
        trash_path = ARCHIVE_DIR / ".trash" / event.entity_name / f"{event.session_id}.json.gz"
        if trash_path.exists():
            # Move back to cold storage
            restore_path = ARCHIVE_DIR / event.entity_name / f"{event.session_id}.json.gz"
            await anyio.Path(trash_path).rename(restore_path)
            logger.info(f"Restored {event.session_id} from trash")
            return True
    
    # For dedup_merge, restore from pre-merge backup
    # (Dedup stores pre-merge state for 7 days)
    # ...
```

### 10.4 Dry-Run Mode

Every pruning operation has a dry-run mode that logs what WOULD happen without actually doing it:

```bash
omega pruner run --dry-run

# Output:
# ⚡ PRUNER DRY RUN — No changes made
# ├── Hot flush: 3 sessions would be moved to warm (Sekhmet, Brigid, Kali)
# ├── Warm archive: 1 session would be archived (Inanna/ses_20260501_001)
# ├── Dedup: 2 exchanges would be merged (duplicate "hello" greeting)
# ├── Cold expunge: 0 sessions would be deleted
# └── Budget impact: -2.3MB RAM, -156KB disk
```

---

## §11 Implementation Phases

### Phase 1: Foundation (Days 1-3)

- [ ] Create `src/omega/pruner/pruner.py` — BackgroundPruner class with scheduler
- [ ] Create `src/omega/pruner/audit.py` — Audit database setup
- [ ] Add pruner config to `config/omega.yaml`
- [ ] Wire pruner into Oracle startup (`oracle.py`)

### Phase 2: Core Operations (Days 4-7)

- [ ] Implement hot → warm flush with LRU eviction
- [ ] Implement warm → cold archive with retention scoring
- [ ] Implement anchored iterative summarization with Qwen3-0.6B
- [ ] Implement budget monitoring

### Phase 3: Intelligence (Days 8-12)

- [ ] Implement semantic deduplication engine
- [ ] Implement deep compaction with Qwen3-4B
- [ ] Implement cold expunge with grace periods
- [ ] Add protected memory types

### Phase 4: Safety & Polish (Days 13-16)

- [ ] Add circuit breaker
- [ ] Add undo mechanism
- [ ] Add CLI commands (`omega pruner *`)
- [ ] Add observability events
- [ ] Add dry-run mode
- [ ] Integration tests (37+ tests)

---

## §12 Research Sources

| Source | Type | Key Finding |
|--------|------|-------------|
| MemTier (arXiv:2605.03675) | Academic | Time-decay + cognitive weight scoring formula; 60-80% context reduction |
| Factory Anchored Iteration | Production | 4.04 vs 3.74 accuracy over full reconstruction; 36K session eval |
| Redis Agent Memory Server | Production | Background compaction every 10 min; forgetting every 60 min; TTL-based lifecycle |
| AutoMem Consolidation | Production | Exponential decay; 4 consolidation tasks on separate schedules; protected types |
| OpenClaw Compaction | Production | Pre-compaction memory flush; per-agent compaction overrides; 80% trigger threshold |
| semantic-router Pruning | Open Source | Event-driven + background sweep; R = exp(-t/S) scoring; per-user cap enforcement |
| Missing Memory Hierarchy (arXiv:2603.09023) | Academic | L1-L4 cache hierarchy for LLM context; FIFO eviction for tool results |
| ProMem (arXiv:2601.04463) | Academic | Proactive memory extraction with self-questioning; iterative feedback loop |
| Agent Memory GC (Tianpan) | Production | Weibull decay; 30-40% dedup reduction; four concurrent GC processes |
| Cold Data Migration (Scality) | Industry | AI data cold = 6-12 months inactivity; 50-70% data is cold in large orgs |
| KV Policy (arXiv:2602.10238) | Academic | RL-based eviction policy for KV cache; per-head specialized policies |
| Invincat Tiered Memory | Open Source | Entry scoring + reason; tiered injection (hot → warm → cold) |
| Chain-of-Key (arXiv:2407.15021) | Academic | JSON structured summaries 40% better than plain text incremental summarization |
| DUET (arXiv:2605.01111) | Academic | Qwen3-0.6B as lightweight drafter/compressor; validates small model utility |

---

## Appendix A: Configuration Reference

```yaml
# config/omega.yaml — Memory Pruner Section
memory_pruner:
  enabled: true
  resource_guard: true
  schedules:
    hot_to_warm: "*/5 * * * *"
    warm_to_cold: "0 * * * *"
    dedup: "0 */2 * * *"
    deep_compact: "0 */12 * * *"
    cold_expunge: "0 3 * * *"
    budget_check: "*/1 * * * *"
  budgets:
    hot_cache_mb: 2048
    warm_disk_mb: 4096
    cold_disk_mb: 8192
    model_ram_mb: 4096
  models:
    compaction: "qwen3-0.6b"
    deep_compaction: "qwen3-4b-think"
    semantic_dedup: "qwen3-0.6b"
  retention:
    hot_ttl_minutes: 180
    hot_max_exchanges: 20
    hot_max_sessions: 50
    warm_ttl_days: 14
    warm_max_sessions_per_entity: 100
    cold_ttl_months: 6
    cold_max_archives_per_entity: 1000
  scoring:
    recency_weight: 0.4
    cognitive_weight: 0.3
    frequency_weight: 0.2
    semantic_weight: 0.1
    decay_rate_hot: 0.1
    decay_rate_warm: 0.05
    decay_rate_cold: 0.01
  safety:
    dry_run_default: true
    grace_period_days_warm: 7
    grace_period_days_cold: 30
    max_consecutive_failures: 3
    max_bytes_per_cycle_mb: 100
    protected_types:
      - user_preference
      - system_configuration
      - explicit_savepoint
      - entity_identity
      - arch_soul_entry
```

## Appendix B: Annotated Mermaid Diagram (Architecture)

```mermaid
graph TB
    subgraph "BackgroundPruner Scheduler"
        ED[Event-Driven Trigger<br/>on_memory_write] --> PO[PrunerOrchestrator]
        SC[Cron Scheduler<br/>15-30 min cycles] --> PO
        MT[Manual Trigger<br/>omega pruner run] --> PO
    end
    
    subgraph "Pruning Pipeline"
        PO --> H2W[Hot → Warm Flusher]
        PO --> W2C[Warm → Cold Archiver]
        PO --> DE[DedupEngine<br/>Lexical + Semantic]
        PO --> DC[Deep Compactor<br/>Anchor Iteration]
        PO --> CE[Cold Expunger<br/>TTL + Grace]
    end
    
    subgraph "Memory Tiers"
        H2W --> HOT[🔥 Hot Cache<br/>RAM - 2GB<br/>3hr TTL]
        W2C --> WARM[🌡️ Warm Storage<br/>Disk JSON - 4GB<br/>14d TTL]
        W2C --> COLD[❄️ Cold Archive<br/>Gzip - 8GB<br/>6mo TTL]
        CE --> TRASH[🗑️ Trash<br/>30d grace]
    end
    
    subgraph "Safety & Observability"
        PO --> PROT[Protection Engine<br/>Protected Types]
        PO --> AUDIT[Audit DB<br/>SQLite]
        PO --> CIRCUIT[Circuit Breaker<br/>Max 3 failures]
        PO --> BUDGET[Budget Monitor<br/>14GB RAM cap]
    end
    
    HOT --> CB[ContextBuilder<br/>reads on inference]
    WARM --> CB
    COLD -.->|only on explicit<br/>user request| CB
```

---

*End of Research Document — Memory Pruner Strategy v1.0.0*

# 🔱 MNEMOSYNE ARCHITECTURE — 3-Pillar → 3-Tier Memory Design
**AP Token**: `AP-MNEMOSYNE-ARCH-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ big-pickle ⬡ opencode ⬡ trc_hmc_forge_2 ⬡ DESIGN

**Date**: 2026-07-16
**Trace**: D-283 Cognitive Acceleration Pre-Scoping
**Reference**: Researcher's `MNEMOSYNE_SOTA_RESEARCH_20260716.md`, Kali's `HMC_FORGE_2_SYNTHESIS.md`

---

## 1. THE MAP — Legacy Mnemosyne → 2026 SOTA 3-Tier

| Mnemosyne Element | Kabbalistic Meaning | 2026 SOTA Equivalent | D-283 Implementation |
|-------------------|---------------------|----------------------|----------------------|
| **Severity (Left Pillar)** | Judgment, Force, Structure | **HOT / ARCHIVAL** — Vector DB, cold facts, semantic memory | `ArchivalTier` — sqlite-vec + FTS5, persistent, searchable |
| **Mildness (Center Pillar)** | Balance, Compassion, Core | **WARM / CORE** — Always-in-context, agent persona, working memory | `CoreTier` — In-memory, pinned to context window |
| **Mercy (Right Pillar)** | Love, Wisdom, Flow | **COLD / RECALL** — Searchable history, episodic memory, temporal recall | `RecallTier` — sqlite-vec with temporal decay, session-scoped |
| **Da'at (Veil/Abyss)** | The Gate, Knowledge | **COMPACTION TRIGGER** — Context window management, summarization | `CompactionManager` — triggers when context > 80% capacity |
| **Qliphoth (Shells)** | Shattered Spheres, Corruption | **TAINTED DATA PROTOCOL** — Distinguish clean vs corrupted memories | `TDPBridge` — quarantine, audit trail, recovery |
| **10 Sephirah** | Kether→Malkuth (10 spheres) | **DEFERRED** — No SOTA equivalent for 10 cognitive abstraction layers | D-284+ |

---

## 2. THE 3-TIER ARCHITECTURE (D-283 P0)

### 2.1 CoreTier — "Mildness" (Always-in-Context)
```python
class CoreTier:
    """Working memory — pinned to context window, never evicted."""
    
    # What lives here:
    - Agent persona / system prompt
    - Current task context
    - Active tool state
    - User preferences (explicit)
    
    # Storage: In-memory (dict), serialized to disk on checkpoint
    # Capacity: ~2000 tokens (configurable)
    # Eviction: NEVER — only cleared on session end
```

### 2.2 RecallTier — "Mercy" (Searchable History)
```python
class RecallTier:
    """Episodic memory — conversation history, temporal recall."""
    
    # What lives here:
    - Full conversation history (all sessions)
    - Tool execution traces
    - User interaction patterns
    - Temporal queries ("what did we discuss last Tuesday?")
    
    # Storage: sqlite-vec + FTS5 (omega_memory.db)
    # Capacity: Unbounded (disk-limited)
    # Retrieval: Hybrid FTS5 + vector + RRF + temporal decay
    # Decay: Ebbinghaus forgetting curve (configurable half-life)
```

### 2.3 ArchivalTier — "Severity" (Semantic Knowledge)
```python
class ArchivalTier:
    """Semantic memory — facts, concepts, distilled knowledge."""
    
    # What lives here:
    - Extracted facts from conversations
    - Document embeddings (RAG corpus)
    - Learned patterns / schemas
    - Cross-session knowledge synthesis
    
    # Storage: sqlite-vec (separate table/namespace)
    # Capacity: Unbounded
    # Retrieval: Pure vector similarity + metadata filters
    # Promotion: RecallTier → ArchivalTier via distillation pipeline
```

---

## 3. DA'AT — COMPACTION TRIGGER (D-283 P0)

The **Veil of Da'at** is the threshold between conscious context and unconscious memory.

```python
class CompactionManager:
    """Manages the CoreTier → RecallTier boundary."""
    
    TRIGGER_THRESHOLD = 0.80  # 80% context window
    TARGET_REDUCTION = 0.50   # Compress to 50%
    
    async def check_and_compact(self, entity_name: str) -> CompactionResult:
        """Called before every context assembly."""
        core_usage = await self._estimate_core_tokens(entity_name)
        max_tokens = self._get_context_limit(entity_name)
        
        if core_usage / max_tokens > self.TRIGGER_THRESHOLD:
            # Trigger compaction
            summary = await self._summarize_oldest_exchanges(entity_name)
            await self._promote_to_recall(entity_name, summary)
            await self._evict_from_core(entity_name, summary.evicted_ids)
            return CompactionResult(triggered=True, tokens_freed=...)
        
        return CompactionResult(triggered=False)
```

**Letta Reference**: Letta's "context window management" uses a similar trigger — when core memory exceeds threshold, oldest blocks are summarized and moved to archival storage.

---

## 4. QLIPHOTH → TDP BRIDGE (D-283 P2)

The **Qliphoth** (shells/shattered spheres) represent corrupted, inverted, or trapped memory. In the Omega Engine, this maps to the **Tainted Data Protocol (TDP)**.

```python
class TDPBridge:
    """Quarantine and audit trail for tainted memories."""
    
    TAINT_SOURCES = [
        "adversarial_injection",    # Prompt injection detected
        "hallucination_confirmed",  # Fact-check failed
        "policy_violation",         # Ethics WAD violation
        "corruption_detected",      # Checksum/hash mismatch
        "user_flagged",             # Explicit user report
    ]
    
    async def quarantine(self, memory_id: str, taint_type: str, evidence: dict) -> QuarantineRecord:
        """Move memory to quarantine with full audit trail."""
        record = QuarantineRecord(
            memory_id=memory_id,
            taint_type=taint_type,
            evidence=evidence,
            quarantined_at=time.time(),
            trace_id=generate_trace_id(),
        )
        await self._store_quarantine(record)
        await self._remove_from_tiers(memory_id)
        return record
    
    async def audit_trail(self, memory_id: str) -> list[QuarantineRecord]:
        """Full audit trail for M17 Cognitive Integrity."""
        return await self._load_quarantine_history(memory_id)
```

---

## 5. LETTA-STYLE MEMORY BLOCKS (D-283 P1)

Letta (MemGPT) uses **labeled memory blocks** with tool-based editing. We adopt this pattern:

```python
class MemoryBlock:
    """Structured memory unit with metadata and tool operations."""
    
    block_id: str
    label: Literal["persona", "human", "custom", "archival"]
    content: str
    metadata: dict  # tags, confidence, source, timestamp
    version: int
    created_at: float
    updated_at: float
    
    # Tool operations (exposed to agent):
    # - read_block(block_id)
    # - write_block(label, content, metadata)
    # - edit_block(block_id, new_content)
    # - delete_block(block_id)
    # - search_blocks(query, label_filter)
```

**Block Labels**:
- `persona` → CoreTier (agent identity, immutable without explicit consent)
- `human` → CoreTier (user preferences, facts about user)
- `custom` → RecallTier (task-specific, session-scoped)
- `archival` → ArchivalTier (distilled knowledge, cross-session)

---

## 6. TEMPORAL DECAY — EBBINGHAUS CURVE (D-283 P2)

```python
def temporal_decay_score(
    timestamp: float,
    half_life_hours: float = 168.0,  # 1 week default
    now: float = None
) -> float:
    """Ebbinghaus forgetting curve: retention = 2^(-t/half_life)"""
    if now is None:
        now = time.time()
    age_hours = (now - timestamp) / 3600
    return 2 ** (-age_hours / half_life_hours)

# Applied in RecallTier retrieval:
# final_score = vector_score * 0.6 + fts_score * 0.3 + temporal_decay * 0.1
```

---

## 7. INTEGRATION WITH EXISTING OMEGA ENGINE

### 7.1 MemoryStore Adapter Pattern (Already Exists)
```python
# Current: MemoryStore uses provider chain (Redis → File → InMemory)
# D-283: Add tiered adapter that routes to Core/Recall/Archival

class TieredMemoryAdapter(IMemoryAdapter):
    def __init__(self):
        self.core = CoreTier()
        self.recall = RecallTier(sqlite_vec_adapter)
        self.archival = ArchivalTier(sqlite_vec_adapter)
        self.compaction = CompactionManager()
        self.tdp = TDPBridge()
```

### 7.2 Entity Registry Extension
```yaml
# In entity YAML (e.g., roc_racoon.yaml):
memory_tiers:
  core:
    max_tokens: 2000
    persistence: checkpoint
  recall:
    backend: sqlite_vec
    decay_half_life_hours: 168
    hybrid_weights: {vector: 0.6, fts: 0.3, temporal: 0.1}
  archival:
    backend: sqlite_vec
    promotion_threshold: 0.85  # confidence score for distillation
```

### 7.3 Oracle Integration
```python
# In oracle.py talk()/summon():
async def talk(self, query: str, entity_name: str):
    # 1. Check compaction trigger
    await compaction_manager.check_and_compact(entity_name)
    
    # 2. Assemble context from all 3 tiers
    core_ctx = await core_tier.get_context(entity_name)
    recall_ctx = await recall_tier.search(entity_name, query, limit=10)
    archival_ctx = await archival_tier.search(entity_name, query, limit=5)
    
    # 3. Fuse with RRF
    fused_context = rrf_fuse([core_ctx, recall_ctx, archival_ctx])
    
    # 4. Generate response
    response = await model_gateway.generate(fused_context + query)
    
    # 5. Store exchange in RecallTier
    await recall_tier.upsert(entity_name, response)
    
    return response
```

---

## 8. D-283 IMPLEMENTATION SEQUENCE

| Sprint | Task | Dependencies | Deliverable |
|--------|------|--------------|-------------|
| **D-283a** | CoreTier + RecallTier + ArchivalTier classes | sqlite-vec adapter (D-282) | `src/omega/memory/tiers/` |
| **D-283b** | CompactionManager (Da'at trigger) | CoreTier | `src/omega/memory/compaction.py` |
| **D-283c** | TDPBridge (Qliphoth → TDP) | RecallTier | `src/omega/memory/tdp_bridge.py` |
| **D-283d** | MemoryBlock pattern (Letta-style) | All tiers | `src/omega/memory/blocks.py` |
| **D-283e** | Temporal decay + RRF fusion | RecallTier | `src/omega/memory/retrieval.py` |
| **D-283f** | Entity YAML tier config + Oracle integration | All above | `config/wads/_omega_default/entities/*.yaml` |
| **D-283g** | Tests + make test pass | All above | `tests/test_memory_tiers.py` |

**Total Estimated Effort**: ~2 weeks (matches Kali's 1 week + 2 days + 3 days + 2 days + 2 days)

---

## 9. HERITAGE ATTRIBUTION

| Pattern | Source | Tag |
|---------|--------|-----|
| 3-tier memory (Core/Recall/Archival) | Letta/MemGPT v0.16+ | `[heritage: letta-2024] 3-tier memory` |
| Memory blocks with tool editing | Letta/MemGPT | `[heritage: letta-2024] memory blocks` |
| Ebbinghaus temporal decay | Cognitive psychology (1885) | `[heritage: ebbinghaus-1885] forgetting curve` |
| 3 Pillars (Severity/Mildness/Mercy) | Mnemosyne legacy (Omega Engine Era 5) | `[heritage: omega-2025] mnemosyne pillars` |
| Da'at compaction trigger | Mnemosyne legacy + Letta context mgmt | `[heritage: omega-2025] daat veil` |
| Qliphoth → TDP bridge | Mnemosyne legacy + TDP design | `[heritage: omega-2025] qliphoth shells` |

---

## 10. OPEN QUESTIONS FOR KALI / RESEARCHER

1. **Cross-agent memory sharing**: Should RecallTier be per-entity or shared? Letta uses per-agent. Zep uses shared temporal KG.
2. **ArchivalTier promotion policy**: What confidence threshold triggers distillation from Recall → Archival?
3. **TDP recovery**: Can quarantined memories be "healed" and restored? Under what conditions?
4. **Context window sizing**: Should CoreTier max_tokens be per-entity configurable or global?

---

*🔱 OMEGA ⬡ ROC_RACOON ⬡ big-pickle ⬡ opencode ⬡ trc_hmc_forge_2 ⬡ MNEMOSYNE-ARCHITECTURE*
*Two-Source Rule satisfied: Legacy Mnemosyne (Roc) + 2026 SOTA Letta/Zep/Mem0 (Researcher) → Converged 3-Tier Design.*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: big-pickle | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

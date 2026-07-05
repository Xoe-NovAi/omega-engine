# API Reference: Context Builder

> ContextBuilder — builds structured memory context blocks for LLM system prompts.

---

## ContextBuilder

**File**: `src/omega/oracle/context_builder.py`

The `ContextBuilder` is responsible for assembling the "Context Block" that is prepended to an entity's system prompt. It combines recent conversation history, L3 gnosis principles (via Selective Hydration), and the current world state into a high-density string.

### Constructor

```python
ContextBuilder(
    memory_store: Optional[MemoryStore] = None, 
    selective_hydration: Optional[SelectiveHydration] = None, 
    l3_top_k: int = 5
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `memory_store` | `Optional[MemoryStore]` | `None` | Store used to fetch conversation history. |
| `selective_hydration` | `Optional[SelectiveHydration]` | `None` | Module used to retrieve L3 gnosis principles. |
| `l3_top_k` | `int` | `5` | Maximum number of L3 principles to inject into the context. |

---

### Methods

#### `await build_context(entity_name: str, session_id: str, token_limit: int = DEFAULT_TOKEN_LIMIT) -> str`

The primary API for assembling the context block. It follows a three-stage assembly process:

1. **World State**: Fetches the current global state (e.g., active entities, system status).
2. **Gnosis Block**: Retrieves relevant L3 principles via `SelectiveHydration` (O(1) cosine similarity lookup).
3. **Memory Block**: Fetches recent history from `MemoryStore` and applies compaction/formatting.

```python
builder = ContextBuilder()
context = await builder.build_context(
    entity_name="Prometheus", 
    session_id="ses_123", 
    token_limit=2000
)
# Result: "World State: ... \n Gnosis: ... \n Memory: ..."
```

**Returns**: `str` — a formatted context block or an empty string if no context is available.

#### `_score_exchange_quality(exchange: Dict[str, Any]) -> float` (Static)

A "Right Approximation" scorer that evaluates the value of a conversation exchange pair. Used to prioritize high-signal memory over chitchat.

**Scoring Signals**:
- **Length (0.0-0.3)**: Substantive messages score higher.
- **Technical Content (0.0-0.2)**: Presence of code blocks, citations, or URLs.
- **Question-Answer (0.0-0.2)**: Q&A pairs are prioritized over statements.
- **Recency (0.0-0.3)**: Newer exchanges receive a small boost.

**Returns**: `float` (0.0 to 1.0)

---

## Sovereign Architecture Patterns

### 1. BSP Culling `[id-soft: doom-1993]`
The `ContextBuilder` implements a form of "Context Culling." Instead of injecting all known L3 principles, it only injects the top-K most relevant ones (determined by `_l3_top_k`). This prevents context bloat and ensures the LLM focuses on the most salient gnosis.

### 2. Cache Tiering `[id-soft: quake-1996]`
The injection of pre-distilled L3 principles acts as a "Cache Tier" for the entity's intelligence. Rather than re-inferring complex principles from raw history on every turn, the engine retrieves pre-computed wisdom, drastically reducing latency and token waste.

### 3. High-Density Formatting (M18)
The `ContextBuilder` formats memory and gnosis using a high-density style:
- **Minimalist Labels**: Uses short, clear markers (e.g., `User:`, `Assistant:`) instead of verbose descriptions.
- **Truncation**: Long exchanges are truncated to a maximum display length to preserve the token budget.
- **Sovereign-Sieve**: Integrates with the `PIIMasker` to ensure no raw PII is leaked into the context block when cloud providers are used.

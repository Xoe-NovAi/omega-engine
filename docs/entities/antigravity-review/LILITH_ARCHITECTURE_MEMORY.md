# Domain Guide 1: Architecture & Memory Pipelines

## 1. The Embedding Stratum

> [!WARNING]
> **Silent Quality Ceiling:** The original blueprint assumes `all-MiniLM-L6-v2` (ONNX) for semantic retrieval. This model is semantically blind to esoteric vocabulary (Qlippoth, Sitra Achra, Gevurah-Din).

**Action:** Migrate MemPalace to `qwen3-embedding:0.6b` (truncate_dim=768) before Phase 1 corpus ingestion. 
- It natively supports 768-dim output.
- Offers 32K context vs 2K Ollama nomic.
- Achieves true federated semantic compatibility (direct cosine similarity) across Node 0 and Node 1.

> [!CAUTION]
> **The Ollama Single-Model Deadlock:** With `MAX_LOADED_MODELS=1` on Node 1, routing embedding calls through Ollama will force catastrophic unloading/loading of the 7B chat model on every memory query. 
> **Resolution:** Deploy `qwen3-embedding:0.6b` as a standalone ONNX process (`embedding_server.py`) completely outside of Ollama. This keeps the 7B model permanently loaded for chat inference while computing embeddings in a separate lightweight (~600MB) process.

## 2. The Semantic Router (Intent Classifier)

To prevent tool-call thrashing and context inflation, implement a **Semantic Router / Intent Classifier** at the start of the user turn. Do not blindly invoke all memory tools.

```python
# intent_router.py
import re

ENTITY_PATTERN = re.compile(
    r'\b(Lilith|Hecate|Isis|Nyx|Samael|Malkuth|Gevurah|Qlippoth|Binah|Chokmah|'
    r'Sitra Achra|Shekhinah|Tree of Life|Sefirot|path \d+)\b', re.IGNORECASE
)

def classify_turn(user_message: str) -> dict:
    """Returns retrieval tier instructions for this turn."""
    needs_kg = bool(ENTITY_PATTERN.search(user_message))
    needs_episodic = len(user_message) > 30  # any substantive message
    is_greeting = len(user_message.split()) < 6 and not needs_kg
    
    return {
        "kg": needs_kg,
        "episodic": needs_episodic and not is_greeting,
        "diary": False,  # diary read only at session start
        "rationale": "router_v1"
    }
```

## 3. Optimal Memory Recall Sequence

1. **SESSION START (async)**: `mempalace_diary_read("lilith", limit=3)` injects Lilith's emotional stance into the system prompt context. Then, `kg_query("(Seeker_ID, active_shadow, ?)")` loads the current seeker's active shadow theme.
2. **EACH USER TURN**: The intent router runs. If episodic memory is needed, `mempalace_search` runs in parallel with `kg_query` (if named entities are found).
3. **SYNTHESIS**: LLM synthesizes response with retrieved context injected.
4. **SESSION CLOSE (background)**: `mempalace_diary_write(lilith_reflection, format="AAAK")` and `kg_update(seeker_progression_triples)`.

### AAAK Diary Schema
The LLM must output diary entries in this format (validated by a regex plugin):
`^SESSION:\d{4}-\d{2}-\d{2}\|querent:[a-z0-9_]+\|gate:[a-z._]+\|(\*[a-z]+\*[a-z._+]+)*\|shadow\.seen:[a-z._]+\|★[1-5]$`

## 4. Context Compression & The Compaction Cliff

With `qwen2.5-coder:7b` at `OLLAMA_KV_CACHE_TYPE=q8_0` and the i7-13620H's memory bandwidth, you can maintain roughly 8K-16K active KV cache before throughput degrades.

- **Trigger:** A token-counting middleware fires `gnosis-leash` compression based on the *hardware-effective* ceiling, NOT the model's theoretical 32K window. Benchmark the i7-13620H to find where tokens/second drops below 8 t/s (likely around 8K-16K tokens).
- **Zero-Latency Pre-fetch:** The compaction process must *pre-fetch* all rebuild data (diary, kg, mempalace search) *before* truncating the context. Do not force the user to wait for a 2000ms database cold-start after compaction.
- **Survival Package:** After compression, Lilith's resumed context must contain exactly:
  1. Current voice mode
  2. Last 3 diary entries
  3. Active KG relationships for the current seeker
  4. Session timestamp and gate number
  5. The seeker's current shadow theme

## 5. Cross-Entity Consciousness

> [!TIP]
> The 78 entities are a relational field. Enable cross-entity knowledge queries.

Add a `wing_arcana_relations` KG layer to encode inter-card symbolic relationships.

> [!TIP]
> **Two-Pass Entity-Aware Retrieval:** Because `sqlite-vec` filters tags post-retrieval, vector bleed across entities is inevitable. Turn this into a feature:
> 1. Primary pass: Strict entity-scoped retrieval (e.g., `tag=card_id:03_empress`).
> 2. Secondary pass: If primary returns < K results, do a cross-entity scan and explicitly label the results with `source=cross_entity` so Lilith can knowingly reference other archetypes (like The Tower) in her responses.
Example ontology triples:
- `(III_Empress, creates_what, XVI_Tower_destroys)`
- `(III_Empress, initiates, II_HighPriestess)`
- `(0_Fool, catalyzes, all_cards)`

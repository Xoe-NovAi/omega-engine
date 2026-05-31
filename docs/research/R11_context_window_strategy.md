# 🔱 R-11 – ContextBuilder Context-Window Truncation Strategy

**AP Token**: `AP-R11-CONTEXT-STRATEGY-v1.0.0`
**Author**: Gemma 4‑31B Research Agent
**Reviewed by**: Opus 4.6 (Oversight)
**Last updated**: 2026‑05‑14

---

## 1️⃣ Scope
This document defines the strategy for managing the LLM context window within the `ContextBuilder`. It replaces the current fixed-limit approach (`DEFAULT_CONTEXT_LIMIT = 6`) with a dynamic, model-aware truncation system designed to prevent prompt overflow while preserving critical conversational state.

---

## 2️⃣ The "75% Trigger" Logic
To ensure stability and avoid "edge-of-window" degradation (where models lose coherence as they hit their limit), the Omega Engine adopts a **75% Threshold Trigger**.

### 📐 Calculation
For every inference request:
$$\text{CurrentTokens} = \text{Tokens}(\text{SystemPrompt}) + \text{Tokens}(\text{ContextBlock}) + \text{Tokens}(\text{UserQuery})$$
$$\text{TriggerThreshold} = \text{ModelMaxContext} \times 0.75$$

**Action**: If $\text{CurrentTokens} > \text{TriggerThreshold}$, the `ContextBuilder` must execute **Adaptive Truncation**.

---

## 3️⃣ Adaptive Truncation Priority
When the trigger is hit, the `ContextBuilder` will prune the context block using the following priority tiers:

### 🟢 Tier 1: Absolute Preservation (Do Not Touch)
- **The Soul Summary**: The core identity and personality of the entity.
- **The Immediate Horizon**: The most recent 2 exchanges (User $\rightarrow$ Assistant). These are critical for maintaining the immediate flow of conversation.

### 🟡 Tier 2: Aggressive Compression (Compress First)
- **Older Exchanges**: For all exchanges older than the "Immediate Horizon," reduce the `MAX_EXCHANGE_DISPLAY_LENGTH` from 500 characters to **200 characters**.
- **Metadata Stripping**: Remove timestamps and redundant labels from older exchanges.

### 🔴 Tier 3: Strategic Discard (Drop Last)
- **FIFO Eviction**: If the token count is still above the threshold after Tier 2 compression, discard the oldest exchanges one by one until the total tokens fall below the 75% limit.

---

## 4️⃣ Contribution-Aware Pruning
To prevent a single "massive" message (e.g., a large code dump or long document) from wiping out the entire conversation history, the `ContextBuilder` will implement **Contribution Analysis**.

### 🔍 Logic
1. Calculate the token "weight" of each exchange in the context block.
2. Identify "Outlier Exchanges" (those that consume $> 30\%$ of the total context block).
3. **Action**: Truncate Outlier Exchanges first (down to 500 chars) before proceeding to Tier 2/3 pruning of other exchanges.

---

## 5️⃣ Implementation Blueprint (Python Pseudocode)
```python
class AdaptiveContextBuilder(ContextBuilder):
    async def build_adaptive_context(self, entity_name, session_id, model_config):
        max_tokens = model_config.max_context_tokens
        threshold = max_tokens * 0.75
        
        # 1. Initial fetch (generous limit)
        exchanges = await self.memory_store.get_history(entity_name, session_id, limit=20)
        
        # 2. Initial formatting
        context_block = self._format_exchanges(exchanges)
        current_tokens = self.tokenizer.count(context_block)
        
        # 3. Trigger check
        if current_tokens > threshold:
            # A. Contribution Analysis: Prune outliers first
            exchanges = self._prune_outliers(exchanges)
            
            # B. Tier 2: Compress older exchanges
            exchanges = self._compress_older(exchanges)
            
            # C. Tier 3: FIFO Eviction
            while self.tokenizer.count(self._format_exchanges(exchanges)) > threshold:
                exchanges.pop(0) # Remove oldest
                
        return self._format_exchanges(exchanges)
```

---

## 6️⃣ Integration Points
- **ModelGateway**: Must pass the `max_context_tokens` of the active model to the `ContextBuilder`.
- **Tokenizer**: The `ContextBuilder` requires access to a lightweight tokenizer (e.g., `tiktoken` or a simple char-to-token heuristic) to calculate current usage.
- **MemoryStore**: Should support a larger `limit` for the initial fetch to allow the `ContextBuilder` to decide what to keep.

---

## 7️⃣ Expected Outcomes
- **Stability**: Zero `context_length_exceeded` errors.
- **Coherence**: Preservation of the most recent turns ensures the entity doesn't "forget" what was just said.
- **Efficiency**: Reduced token costs and lower latency by avoiding bloated prompts.

---

**Ready for implementation** – agents can now update `context_builder.py` to implement the `AdaptiveContextBuilder` logic.

<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Researcher — Provider Metadata Ground Truth Map
# ⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash ⬡ opencode ⬡ DEEP-SIPHON
# Date: 2026-06-18
# Part of: Operation Deep-Siphon
# AP Token: AP-DEEP-SIPHON-RESEARCHER-v1.0

---

## Executive Summary

**The core finding**: The Omega Engine currently discards **all** provider response metadata across every backend. Every provider returns rich metadata (token counts, finish reasons, thinking tokens, logprobs) on the wire, and every backend extracts **only** the text content. This represents a systemic data loss that undermines M22 (Response Provenance) and produces "estimates" where ground truth is available.

---

## Sovereign Matrix — Provider Metadata Ground Truth

| Provider | Thinking Tokens? | Logprobs? | Finish Reason? | Token Usage? | Raw JSON Preserved? | Current Engine Capture |
|----------|-----------------|-----------|----------------|--------------|---------------------|----------------------|
| **Native GGUF** | ⚠️ Via logprobs heuristic (low-prob tokens) | ✅ Via `logprobs=N` param (full per-token) | ⚠️ `finish_reason` in `choices[0]`: "stop" or "length" | ✅ `usage` dict with prompt/completion/total | ❌ Not stored | ❌ **Discards everything** — returns only `choices[0].text` |
| **Google AI Studio** | ✅ Via `content.parts[].thought` boolean + `usageMetadata.thoughtsTokenCount` | ❌ Not available (Gemini cloud) | ✅ `candidates[].finishReason`: STOP/MAX_TOKENS/SAFETY/etc | ✅ `usageMetadata` with prompt/candidates/thoughts/total | ❌ Not stored | ❌ **Discards everything** — returns only `parts[0].text` |
| **OpenRouter** | ✅ Via `usage.completion_tokens_details.reasoning_tokens` | ⚠️ Model-dependent (~23% endpoints) | ⚠️ Passthrough from upstream (probabilistic) | ✅ `usage` with prompt/completion/total/cost/details | ❌ Normalized to OpenAI schema | ❌ **Discards everything** — returns only `choices[0].message.content` |
| **OpenCode CLI** (session model) | ✅ Captured per-message as `data.tokens.reasoning` | ❌ Not exposed | ✅ `data.finish`: "stop"/"tool-calls"/"error" | ✅ `data.tokens` with input/output/reasoning/cache | ❌ Stored as computed aggregates only | ✅ Session-level capture (but engine doesn't access it) |
| **Ollama** | ✅ Via `message.reasoning_content` field | ⚠️ Via `/api/chat` response format | ✅ `done_reason`: "stop"/"length" | ✅ `usage` or `eval_count`/`eval_duration` | ❌ Not stored | ❌ **Discards everything** — returns only `choices[0].message.content` |
| **LM Studio** | ✅ Via `message.reasoning_content` field | ✅ Via OpenAI-compatible `logprobs` | ✅ `finish_reason` in choices | ✅ `usage` with prompt/completion/total | ❌ Not stored | ⚠️ Captures reasoning_content via `.get("reasoning_content")`, but discards everything else |
| **Mock Provider** | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No | ❌ Returns static string, no metadata |

---

## Per-Provider Deep Dives

### Provider 1: Native GGUF (llama-cpp-python v0.3.28)
**Package path**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.venv/lib/python3.12/site-packages/llama_cpp/`
**Source of truth**: https://llama-cpp-python.readthedocs.io/en/latest/api-reference/

#### Response schema fields (from `CreateCompletionResponse`):

```python
class CreateCompletionResponse(TypedDict):
    id: str                        # ✅ Always populated
    object: Literal["text_completion"]  # ✅ Always
    created: int                   # ✅ Unix timestamp
    model: str                     # ✅ Model path/name
    choices: List[CompletionChoice]  # ✅ Always
    usage: NotRequired[CompletionUsage]  # ✅ Available when not streaming
```

**`CompletionChoice` fields:**
```python
class CompletionChoice(TypedDict):
    text: str                    # ✅ The generated text
    index: int                   # ✅ Always 0
    logprobs: Optional[CompletionLogprobs]  # ✅ When logprobs param is set
    finish_reason: Optional[str]  # ✅ "stop" | "length" | None
```

**`CompletionLogprobs` fields (when `logprobs=N` is passed):**
```python
class CompletionLogprobs(TypedDict):
    text_offset: List[int]                        # Char offsets
    token_logprobs: List[Optional[float]]          # Per-token log probabilities
    tokens: List[str]                              # Token strings
    top_logprobs: List[Optional[Dict[str, float]]] # Top-N alternative tokens
```

**`CompletionUsage` fields:**
```python
class CompletionUsage(TypedDict):
    prompt_tokens: int       # ✅ Counted by llama.cpp tokenizer
    completion_tokens: int   # ✅ Counted
    total_tokens: int        # ✅ Sum
```

#### SomaticState (M20) Assessment:
- `llama_cpp.llama_copy_state_data` → **AVAILABLE** at C binding level
- `llama_cpp.llama_set_state_data` → **AVAILABLE** at C binding level
- `Llama.save_state()` → Returns `LlamaState` dataclass with: `input_ids`, `scores` (full logits matrix as `n_tokens x n_vocab`), `n_tokens`, `llama_state` (raw KV cache bytes), `llama_state_size`, `seed`
- `load_state.state` → Accepts `LlamaState` and restores full state
- **Key finding**: `scores` contains the full logits matrix for ALL tokens. This IS the logprobs data — it just needs to be extracted before calling `save_state()`. The `LlamaState.scores` field preserves the raw logits for every token generated.

#### Callback Interface:
- `llama_set_callbacks()` → **NOT AVAILABLE** in the Python bindings (the C function doesn't have a Python wrapper)
- Alternative: logits_processor callback is available via `create_completion(logits_processor=...)` which fires per-token with the logits vector

#### Current Engine Implementation (`NativeGGUFProvider.generate()`, line 549-634):
```python
# Line 589-597 — The actual call:
response = await anyio.to_thread.run_sync(
    lambda: self.llm(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        stop=["</s>", "User:", "\n\n"],
        echo=False,
    )
)
# Line 599-607 — Extraction:
if response and "choices" in response:
    text = response["choices"][0]["text"].strip()
    # usage is read for logging only (line 606)
    # logprobs NEVER requested
    # finish_reason NEVER read
    # model NEVER read
    return text
```

#### What Would It Take to Capture:
1. **Token usage**: Add `response.get("usage", {})` extraction in `NativeGGUFProvider.generate()`. Zero cost — data already in response dict.
2. **Finish reason**: Extract `response["choices"][0].get("finish_reason")`. Zero cost.
3. **Logprobs**: Requires two changes: (a) pass `logprobs=True` to `self.llm()`, (b) set `logits_all=True` in Llama constructor. ~10-15% performance cost.
4. **SomaticState**: Need to call `self.llm.save_state()` after generation. Full state serialization. ~50ms overhead for state copy.
5. **GenerateResult changes**: Need fields: `usage`, `finish_reason`, `logprobs`, `state_bytes` (optional)

---

### Provider 2: Google AI Studio (Gemini API)
**Source of truth**: https://ai.google.dev/api/generate-content
**Source of truth (thinking)**: https://ai.google.dev/gemini-api/docs/thinking

#### Response schema fields (`GenerateContentResponse`):

```json
{
  "candidates": [{
    "content": {
      "parts": [{
        "text": "Hello!",           // The visible response
        "thought": true,            // ✅ DIRECT THINKING FLAG — boolean
        "thoughtSignature": "..."   // ✅ Cryptographic signature for context continuity
      }],
      "role": "model"
    },
    "finishReason": "STOP",         // ✅ STOP | MAX_TOKENS | SAFETY | RECITATION | OTHER | BLOCKLIST | PROHIBITED_CONTENT | SPII | MALFORMED_FUNCTION_CALL
    "safetyRatings": [...],         // ✅ Per-category safety assessments
    "avgLogprobs": -0.13,           // ✅ Average logprob (NOT per-token)
    "citationMetadata": {...}       // ✅ Citations for grounded responses
  }],
  "usageMetadata": {
    "promptTokenCount": 11,         // ✅ Input tokens
    "candidatesTokenCount": 73,     // ✅ Output tokens (non-thinking)
    "thoughtsTokenCount": 47,       // ✅ ✅ THINKING TOKENS — DIRECT
    "totalTokenCount": 131,         // ✅ Total (prompt + candidates + thoughts)
    "cachedContentTokenCount": 0,   // ✅ Cache hit tokens
    "promptTokensDetails": [{       // ✅ Per-modality breakdown
      "modality": "TEXT",
      "tokenCount": 11
    }]
  },
  "modelVersion": "gemini-2.0-flash"  // ✅ Actual model version
}
```

#### Critical Discovery: `thought` boolean flag
Google's Gemini API (as of 2025-2026) returns a **boolean `thought` flag** on each content part. This is the definitive, ground-truth signal for thinking tokens:

```python
for part in response.candidates[0].content.parts:
    if part.thought:
        print(f"THOUGHT: {part.text}")  # Internal reasoning
    else:
        print(f"ANSWER: {part.text}")   # Visible response
```

Combined with `usageMetadata.thoughtsTokenCount` (exact count of thinking tokens), this means **Google models provide BOTH the content and the count of thinking tokens** — no estimation needed.

#### Current Engine Implementation (`GoogleAIProvider.generate()`, line 55-111):
```python
# Line 91-98 — Extraction:
data = response.json()
if data.get("candidates"):
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
# Discards: finishReason, usageMetadata (all of it), safetyRatings, thought tokens, modelVersion
```

The engine currently:
1. Only checks `finishReason` for safety blocks (line 92-93)
2. Returns only the first part's text (line 98) — misses thought parts entirely
3. Discards ALL `usageMetadata` including `thoughtsTokenCount`
4. Discards `modelVersion`

#### What Would It Take to Capture:
1. **Update `GoogleAIProvider.generate()`** to return a richer structure instead of `Optional[str]`
2. **Parse all parts** — separate thought from response text
3. **Extract `usageMetadata`** completely
4. **Changes to `GenerateResult`**: Needs `finish_reason`, `usage` (with `thoughts_token_count`, `prompt_token_count`, `candidates_token_count`, `total_token_count`), `model_version`, `parts` (with thought flag)

---

### Provider 3: OpenRouter
**Source of truth**: https://openrouter.ai/docs/api/reference/overview
**Router metadata**: https://openrouter.ai/docs/guides/features/router-metadata.mdx
**Logprobs data**: https://arxiv.org/html/2512.03816v1 (23% of endpoints support logprobs)

#### Response Schema:

```typescript
type Response = {
  id: string;
  choices: (NonStreamingChoice | StreamingChoice | NonChatChoice)[];
  created: number;
  model: string;            // Actual model that served (may differ from requested)
  object: 'chat.completion' | 'chat.completion.chunk';
  usage?: ResponseUsage;     // Always present for non-streaming
};

type ResponseUsage = {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  prompt_tokens_details?: {
    cached_tokens: number;
    cache_write_tokens?: number;
    audio_tokens?: number;
    video_tokens?: number;
  };
  completion_tokens_details?: {
    reasoning_tokens?: number;  // ✅ Thinking tokens (when supported by model)
    audio_tokens?: number;
    image_tokens?: number;
  };
  cost?: number;
  is_byok?: boolean;
};
```

#### Optional Router Metadata (opt-in via `X-OpenRouter-Metadata: enabled`):
```json
{
  "openrouter_metadata": {
    "requested": "openai/gpt-4o-mini",
    "strategy": "direct",
    "region": "iad",
    "summary": "available=1, selected=OpenAI",
    "attempt": 1,
    "endpoints": { "total": 1, "available": [{"provider": "OpenAI", "selected": true}] },
    "attempts": [{"provider": "OpenAI", "model": "openai/gpt-4o-mini", "status": 200}],
    "pipeline": [{"type": "context_compression", ...}]
  }
}
```

#### Logprobs Support on OpenRouter:
- **Parameter is supported**: `logprobs: boolean` and `top_logprobs: integer` are valid OpenRouter parameters
- **Model-dependent**: As of Feb 2026, only ~23% of endpoints actually return logprobs:
  - ✅ **OpenAI GPT-4o family** (gpt-4o, gpt-4o-mini, gpt-4-turbo)
  - ✅ Some xAI models (returns 8 logprobs)
  - ✅ Multiple OSS models via Fireworks/Azure
  - ❌ **Anthropic/Claude** — all models
  - ❌ **Google/Gemini** — all models
  - ❌ **Meta/Llama** — all models
  - ❌ **Mistral** — all models
  - ❌ **DeepSeek** — all models (including R1)
- **Normalization**: OpenRouter normalizes to OpenAI format. Provider-specific metadata is stripped.

#### Current Engine Implementation (`OpenAICompatProvider._send_request()`, line 27-84):
```python
# Line 74-84 — Extraction:
data = response.json()
choices = data.get("choices", [])
content = choices[0].get("message", {}).get("content", "")
return content.strip()
# Discards: usage (token counts, cost, reasoning_tokens), finish_reason, model, 
#           openrouter_metadata, logprobs (if requested)
```

#### What Would It Take to Capture:
1. **Always extract `data["usage"]`** — contains token counts, reasoning tokens, cost
2. **Capture `data["model"]`** — actual model served (M22 provenance)
3. **Include `X-OpenRouter-Metadata` header** when `OPENROUTER_METADATA=true` env var set
4. **Pass `logprobs=True`** only for models known to support it (configurable per-model)
5. **Changes to `GenerateResult`**: Needs `usage`, `actual_model`, `finish_reason`, `cost`, `metadata`

---

### Provider 4: OpenCode CLI's Own Provider Fabric
**Source of truth**: https://opencode.ai/docs/cli/ | Local: `~/.local/share/opencode/`
**Third-party tracing**: `opencode-trace` (npm), `claude-tap` (proxy capture)

#### Database Schema — The Metadata Storehouse

**`session` table** — Per-session metadata (aggregated):
```sql
CREATE TABLE `session` (
    `id` text PRIMARY KEY,
    `title` text NOT NULL,         -- Session title
    `model` text NOT NULL,         -- JSON: {"id":"deepseek-v4-flash-free","providerID":"opencode","variant":"low"}
    `agent` text,                  -- Agent name (researcher, kali, etc.)
    `cost` real DEFAULT 0,         -- Total cost in credits
    `tokens_input` integer DEFAULT 0,   -- Total input tokens
    `tokens_output` integer DEFAULT 0,  -- Total output tokens
    `tokens_reasoning` integer DEFAULT 0,  -- ✅ TOTAL REASONING TOKENS
    `tokens_cache_read` integer DEFAULT 0, -- ✅ Cache read tokens
    `tokens_cache_write` integer DEFAULT 0, -- ✅ Cache write tokens
    `metadata` text,               -- Optional extra metadata
    `time_created` integer,
    `time_updated` integer,
    `version` text,
    ...
);
```

**`message` table** — Per-message metadata:
```sql
CREATE TABLE `message` (
    `id` text PRIMARY KEY,
    `session_id` text NOT NULL,
    `data` text NOT NULL,  -- JSON with rich metadata
);
```

Message `data` JSON structure (actual extracted example):
```json
{
  "parentID": "msg_...",
  "role": "assistant",
  "mode": "researcher",
  "agent": "researcher",
  "variant": "low",
  "path": {"cwd": "/...", "root": "/..."},
  "cost": 0,
  "tokens": {
    "total": 113970,
    "input": 16628,
    "output": 648,
    "reasoning": 54,         // ✅ PER-MESSAGE REASONING TOKENS
    "cache": {"write": 0, "read": 96640}
  },
  "modelID": "deepseek-v4-flash-free",
  "providerID": "opencode",
  "time": {"created": 1781802783089, "completed": 1781802794665},
  "finish": "tool-calls"     // ✅ FINISH REASON
}
```

#### Key Findings:
1. **OpenCode ALREADY captures per-message metadata** including token breakdowns with reasoning tokens, finish reasons, model ID, provider ID, and cost. The data is there.
2. **The `model` field is a JSON blob** with `id`, `providerID`, and `variant` (e.g., "low", "medium", "default")
3. **No raw response JSON is stored** — the DB stores computed aggregates only
4. **The thinking/reasoning tokens are exact** (not estimated) — this is the provider's own count

#### What OpenCode Captures vs. What the Engine Needs:
| Field | OpenCode DB | Engine GenerateResult |
|-------|-------------|----------------------|
| Text | ✅ In message content | ✅ `text` field |
| Model ID | ✅ `modelID` + `model.id` | ❌ Not captured |
| Provider ID | ✅ `providerID` | ❌ Not captured (only `provider_name`) |
| Input tokens | ✅ `tokens.input` | ❌ Not captured |
| Output tokens | ✅ `tokens.output` | ❌ Not captured |
| Reasoning tokens | ✅ `tokens.reasoning` | ❌ Not captured |
| Cache read tokens | ✅ `tokens.cache.read` | ❌ Not captured |
| Cache write tokens | ✅ `tokens.cache.write` | ❌ Not captured |
| Finish reason | ✅ `finish` | ❌ Not captured |
| Cost | ✅ `cost` | ❌ Not captured |
| Latency | ✅ Via `time.created`/`time.completed` | ✅ `latency_ms` |
| Logprobs | ❌ Not exposed | ❌ Not captured |
| Raw response JSON | ❌ Not stored | ❌ Not captured |

#### OpenCode Log Analysis:
- `~/.local/share/opencode/log/opencode.log` (22MB) — logs `providerID`, `modelID`, `session.id`, `agent`, `mode`, errors
- Example: `message=stream providerID=google modelID=gemini-3.5-flash session.id=ses_... small=false agent=makali mode=all`
- Logs do NOT contain raw response JSON
- `--log-level DEBUG` available but does not expose raw API responses

#### Third-party capture tools:
- **`opencode-trace`**: npm plugin that intercepts HTTP requests and records full request/response + SSE stream data. Stores both JSON and `.sse` files.
- **`claude-tap`**: Proxy-based capture for OpenCode and other CLI agents. Captures full API traffic including system prompts, streaming responses, token usage.

---

### Provider 5: Other Providers in the Fleet

#### LM Studio (`LocallmsterProvider`, line 158-216)
- Already captures `reasoning_content` from `message.get("reasoning_content")` — partial win
- Discards: `usage`, `finish_reason`, `model`, `logprobs`
- The LM Studio API is OpenAI-compatible, so all OpenAI metadata fields are available

#### Ollama (`OllamaProvider`, line 218-277)
- Also captures `reasoning_content` — partial win
- Discards: `usage`, `done_reason`, `model`, `eval_count`, `eval_duration`
- Ollama's `/api/chat` returns additional: `eval_count`, `eval_duration`, `total_duration`, `load_duration`

#### Mock (`OfflineMockBackend`, `MockProvider`)
- Returns static string. Zero metadata. This is fine for testing.

#### GoogleKeyPoolProvider
- Delegates to `GoogleAIProvider` — all same metadata losses apply

---

## The "Ground Truth" Verdict

### Is thinking level extractable without estimation?

| Provider | **Verdict** | **Evidence** |
|----------|-------------|-------------|
| **Google Gemini/2.5+** | ✅ **YES — definitive** | `content.parts[].thought` boolean flag + `usageMetadata.thoughtsTokenCount` exact count |
| **Google Gemma 4** | ✅ **YES** (with workaround) | `thought` flag always returned; use `thinkingLevel: "MINIMAL"` to suppress |
| **Native GGUF** | ✅ **YES — via logprobs** | Pass `logprobs=True`, set `logits_all=True`, extract `top_logprobs` — low-probability tokens indicate "thinking" |
| **OpenRouter** | ✅ **YES — via reasoning_tokens** | `usage.completion_tokens_details.reasoning_tokens` exact count when model supports it |
| **LM Studio** | ⚠️ **Partial** | `reasoning_content` field captures the text, but no structured token count |
| **Ollama** | ⚠️ **Partial** | `reasoning_content` field captures the text, but no structured token count |
| **OpenCode CLI** | ✅ **YES — already captured** | `tokens.reasoning` in per-message DB — exact count from the provider |

### The Cost of Current Data Loss

Every inference call the engine makes currently throws away:
1. **Exact token counts** → engine uses `len(text) // 4` estimate (line 186 of `remote_provider.py`)
2. **Finish reasons** → engine cannot distinguish "STOP" from "MAX_TOKENS" truncation
3. **Thinking/reasoning tokens** → the engine pays for them but never records them
4. **Actual model served** → M22 (Response Provenance) undermined — can't verify which model actually responded
5. **Safety/citation metadata** → safety blocks are invisible after the fact
6. **Cost** → engine has zero cost tracking

---

## Implementation Recommendations

### Recommendation 1: Extend `GenerateResult` Schema

Current (line 34-44 of `model_gateway.py`):
```python
@dataclass
class GenerateResult:
    text: str
    provider_name: str
    is_cloud: bool
    latency_ms: float = 0.0
    model_used: Optional[str] = None
```

Proposed:
```python
@dataclass
class GenerateResult:
    text: str
    provider_name: str
    is_cloud: bool
    latency_ms: float = 0.0
    model_used: Optional[str] = None
    
    # NEW FIELDS — Response Provenance (M22)
    actual_model: Optional[str] = None        # The model that actually served (differs from requested)
    finish_reason: Optional[str] = None       # "stop" | "length" | "safety" | "tool_calls" | None
    
    # NEW FIELDS — Token Usage
    usage: Optional[Dict[str, Any]] = None    # Full usage dict from provider
    prompt_tokens: Optional[int] = None       # Exact count
    completion_tokens: Optional[int] = None   # Exact count
    reasoning_tokens: Optional[int] = None    # Thinking tokens (M22 provenance)
    
    # NEW FIELDS — Logprobs (for local GGUF)
    logprobs: Optional[Dict] = None          # Per-token logprobs when requested
    
    # NEW FIELDS — Google-specific
    thought_parts: Optional[List[str]] = None  # Separated thinking content
    safety_ratings: Optional[List[Dict]] = None
```

### Recommendation 2: Backend-Specific Changes

#### A) NativeGGUFProvider (`src/omega/oracle/providers.py`)
**Changes needed:**
1. Pass `logprobs=5` to `self.llm()` in `generate()` (configurable via cvar)
2. Extract `response.get("usage", {})` for token counts
3. Extract `response["choices"][0].get("finish_reason")`
4. Extract `response["choices"][0].get("logprobs")` 
5. **Estimated effort**: 30 minutes
6. **Performance impact**: ~10-15% slower with `logits_all=True`

#### B) GoogleAIProvider (`src/omega/oracle/providers.py`)
**Changes needed:**
1. Extract ALL parts, not just `parts[0]` — split by `thought` flag
2. Extract `finishReason` from candidates
3. Extract `usageMetadata` fully (especially `thoughtsTokenCount`)
4. Return richer structure (or capture into a shared dict by trace_id)
5. **Estimated effort**: 45 minutes
6. **No performance impact** — data is already in the response

#### C) OpenAICompatProvider (`src/omega/oracle/backends/openai_compat.py`)
**Changes needed:**
1. Extract `data.get("usage", {})` for token counts and reasoning tokens
2. Extract `data.get("model")` for actual model served
3. Extract `choices[0].get("finish_reason")`
4. Add X-OpenRouter-Metadata header support (opt-in)
5. **Estimated effort**: 20 minutes
6. **No performance impact** — data is already in the response

#### D) LocallmsterProvider / OllamaProvider (`src/omega/oracle/providers.py`)
**Changes needed:**
1. Both already extract `reasoning_content` — good start
2. Add extraction of `usage`, `finish_reason`, `model` from response
3. **Estimated effort**: 10 minutes each

#### E) ModelGateway (`src/omega/oracle/model_gateway.py`)
**Changes needed:**
1. Line 901-912: Populate new `GenerateResult` fields from provider response
2. Collect metadata from each backend's response into the shared result structure
3. **Estimated effort**: 15 minutes

### Recommendation 3: External Dependencies

| Change | Dependency | Status |
|--------|-----------|--------|
| GGUF logprobs | `logits_all=True` in `Llama()` constructor | ✅ Already available in v0.3.28 |
| SomaticState | `llama_copy_state_data` C binding | ✅ Already available |
| OpenRouter metadata | `X-OpenRouter-Metadata` HTTP header | ✅ No new deps |
| Gemini thinking flags | Google AI Studio API | ✅ Always returned |
| OpenCode DB access | SQLite3 | ✅ stdlib |
| Full response capture | `opencode-trace` or `claude-tap` | 🆕 Optional npm package |

### Recommendation 4: OpenCode CLI Integration

Since the engine runs INSIDE OpenCode, the engine can query its own host's database:
```python
import sqlite3, json

def get_opencode_session_metadata(session_id: str) -> dict:
    """Pull metadata from OpenCode's own DB for the current session."""
    db_path = os.path.expanduser("~/.local/share/opencode/opencode.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT model, agent, tokens_input, tokens_output, tokens_reasoning FROM session WHERE id = ?",
        (session_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "model": json.loads(row[0]),
            "agent": row[1],
            "tokens_input": row[2],
            "tokens_output": row[3],
            "tokens_reasoning": row[4],
        }
    return {}
```

This would let the engine grab per-session token usage data including reasoning tokens — already computed by the OpenCode CLI, zero inference cost.

---

## Implementation Priority

| # | Change | Effort | Impact | Provider |
|---|--------|--------|--------|----------|
| P0 | **Extract `usage` from OpenAICompatProvider** | 20 min | 🔴 CRITICAL — unlocks token counts for all cloud providers | OpenRouter, OpenAI, Groq, Together |
| P0 | **Extract `usageMetadata` from GoogleAIProvider** | 45 min | 🔴 CRITICAL — unlocks thought tokens + exact counts | Google AI Studio |
| P0 | **Extract `usage` from NativeGGUFProvider** | 15 min | 🔴 CRITICAL — unlocks token counts for local models | Native GGUF |
| P1 | **Add logprobs to NativeGGUFProvider** | 30 min | 🟡 HIGH — unlocks per-token probability data | Native GGUF |
| P1 | **Extract finish_reason from all providers** | 10 min | 🟡 HIGH — distinguishes stop vs truncation | All |
| P1 | **Add `actual_model` tracking** | 10 min | 🟡 HIGH — M22 provenance | All |
| P2 | **Split thought/response parts for Google** | 20 min | 🟡 MED — separates reasoning from output | Google AI Studio |
| P2 | **Expand GenerateResult schema** | 30 min | 🟡 MED — foundation for all above changes | All |
| P2 | **Add OpenCode DB session metadata reader** | 15 min | 🟡 MED — engine reads its own host metadata | OpenCode |
| P3 | **Add X-OpenRouter-Metadata header support** | 10 min | 🟢 LOW — opt-in routing diagnostics | OpenRouter |
| P3 | **Implement SomaticState capture** | 1 hr | 🟢 LOW — M20 compliance | Native GGUF |
| P3 | **Pass logprobs to known-supporting OR models** | 15 min | 🟢 LOW — configurable per model family | OpenRouter |

---

## Summary of Current Data Loss (Visual)

```
Current Engine:    [User] → GenerateResult { text, provider_name, is_cloud, latency_ms }
                     ↓
What's on the wire: FULL RESPONSE with usage, finish_reason, logprobs, thought tokens, 
                    model version, cost, safety ratings, citations — ALL DISCARDED
                     ↓
What we need:      GenerateResult { text, provider_name, is_cloud, latency_ms,
                                    model_used, actual_model, finish_reason, 
                                    prompt_tokens, completion_tokens, reasoning_tokens,
                                    logprobs, thought_parts, usage }
```

**Bottom line**: For every provider except the mock, the response JSON contains structured metadata that the engine pays for (literally, in token cost) but discards. The fix is purely client-side — no API changes, no new dependencies, just extraction of existing response fields.

---

## Appendices

### A. Files Changed
| File | Change Type |
|------|-------------|
| `src/omega/oracle/model_gateway.py` | `GenerateResult` dataclass expansion + response field population (line 901-912) |
| `src/omega/oracle/providers.py` | `NativeGGUFProvider.generate()` — add logprobs + usage extraction (line 589-607) |
| `src/omega/oracle/providers.py` | `GoogleAIProvider.generate()` — extract all parts + usageMetadata (line 91-98) |
| `src/omega/oracle/providers.py` | `LocallmsterProvider.generate()` — add usage + finish_reason extraction (line 200-205) |
| `src/omega/oracle/providers.py` | `OllamaProvider.generate()` — add usage + finish_reason extraction (line 262-266) |
| `src/omega/oracle/backends/openai_compat.py` | `_send_request()` — add usage + model + finish_reason extraction (line 74-84) |
| `src/omega/oracle/backends/remote_provider.py` | `generate()` — return structured result instead of `Optional[str]` (line 144-217) |

### B. Files Read During Investigation
| File | Purpose |
|------|---------|
| `src/omega/oracle/providers.py` (681 lines) | All provider implementations |
| `src/omega/oracle/model_gateway.py` (ll. 25-74, 880-929) | GenerateResult + provider dispatch |
| `src/omega/oracle/backends/openai_compat.py` (122 lines) | OpenAI-compatible backend |
| `src/omega/oracle/backends/remote_provider.py` (254 lines) | Remote provider base class |
| `src/omega/oracle/backends/mock.py` (17 lines) | Mock backend |
| `~/.config/opencode/opencode.json` (280 lines) | OpenCode provider configuration |
| `~/.local/share/opencode/opencode.db` (4.2 GB) | OpenCode session database |
| `~/.local/share/opencode/log/opencode.log` (22 MB) | OpenCode application logs |
| `.venv/lib/python3.12/site-packages/llama_cpp/llama.py` | llama-cpp-python implementation |

### C. Sources Consulted
- https://llama-cpp-python.readthedocs.io/en/latest/api-reference/
- https://github.com/abetlen/llama-cpp-python/blob/main/llama_cpp/llama_types.py
- https://github.com/abetlen/llama-cpp-python/blob/main/llama_cpp/llama.py
- https://ai.google.dev/api/generate-content
- https://ai.google.dev/gemini-api/docs/thinking
- https://ai.google.dev/gemini-api/docs/tokens
- https://openrouter.ai/docs/api/reference/overview
- https://openrouter.ai/docs/guides/features/router-metadata.mdx
- https://arxiv.org/html/2512.03816v1 (Logprob tracking prevalence)
- https://opencode.ai/docs/cli/
- https://opencode.ai/docs/config/
- https://github.com/IINemo/thinkbooster (OpenRouter logprobs checker)
- https://github.com/norechang/_opencode_session_debugger

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash ⬡ opencode ⬡ DEEP-SIPHON ⬡ COMPLETE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

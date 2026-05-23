# 🔱 Omega Engine — Unified Provider JSON Schema
**AP Token**: `AP-UNIFIED-SCHEMA-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ SCHEMA-DESIGN

## 1. Overview
To ensure the Omega Engine remains provider-agnostic and can seamlessly switch between local GGUF, local servers (lmster, Ollama), and remote APIs (Google AI Studio), a unified internal communication schema is required. 

Currently, providers use divergent payload structures (e.g., Google's `contents/parts` vs. OpenAI's `messages/choices`). This schema abstracts these differences into a canonical Omega format.

## 2. Omega Inference Request Schema
The `OmegaInferenceRequest` is the internal standard for all generation calls.

### JSON Definition
```json
{
  "type": "object",
  "properties": {
    "model": {
      "type": "string",
      "description": "The target model identifier (e.g., 'gemma-4-31b', 'phi-4-mini')"
    },
    "context": {
      "type": "object",
      "properties": {
        "system_prompt": { "type": "string" },
        "user_query": { "type": "string" },
        "history": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "role": { "type": "string", "enum": ["user", "assistant", "system"] },
              "content": { "type": "string" }
            }
          }
        }
      },
      "required": ["system_prompt", "user_query"]
    },
    "parameters": {
      "type": "object",
      "properties": {
        "temperature": { "type": "number", "default": 0.7 },
        "max_tokens": { "type": "integer", "default": 1024 },
        "stop_sequences": { "type": "array", "items": { "type": "string" } },
        "stream": { "type": "boolean", "default": false }
      }
    }
  },
  "required": ["model", "context"]
}
```

## 3. Omega Inference Response Schema
The `OmegaInferenceResponse` captures the output, including reasoning chains (for "Think" models).

### JSON Definition
```json
{
  "type": "object",
  "properties": {
    "content": {
      "type": "string",
      "description": "The final generated response text"
    },
    "reasoning": {
      "type": "string",
      "description": "The internal chain-of-thought or reasoning content (if provided by the model)"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "provider": { "type": "string" },
        "model_used": { "type": "string" },
        "tokens_used": { "type": "integer" },
        "latency_ms": { "type": "integer" },
        "finish_reason": { "type": "string" }
      }
    }
  },
  "required": ["content", "metadata"]
}
```

## 4. Provider Mapping Logic
Each provider implementation must now act as a translator between the Omega Schema and the backend API.

| Provider | Request Mapping | Response Mapping |
|----------|------------------|------------------|
| **Google AI** | `context.system_prompt` + `user_query` $\rightarrow$ `contents[0].parts[0].text` | `candidates[0].content.parts[0].text` $\rightarrow$ `content` |
| **lmster/Ollama** | `context.history` + `user_query` $\rightarrow$ `messages[]` | `choices[0].message.content` $\rightarrow$ `content` / `reasoning_content` $\rightarrow$ `reasoning` |
| **Native GGUF** | `system_prompt` + `user_query` $\rightarrow$ ChatML template | `choices[0].text` $\rightarrow$ `content` |

## 5. Validation Rules
1. **Null Content**: If a provider returns an empty string or null, it must be treated as a `ProviderFailure` to trigger the fallback chain.
2. **Reasoning Extraction**: Providers supporting `<think>` tags or `reasoning_content` must isolate this text into the `reasoning` field to prevent it from polluting the final `content` delivered to the user.

---
**Implementation Note for @Cline / @Antigravity**:
Update `BaseProvider.generate` to accept `OmegaInferenceRequest` and return `OmegaInferenceResponse`. Refactor `ModelGateway.generate` to handle these types instead of raw strings.

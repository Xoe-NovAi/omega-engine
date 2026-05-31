# 🔱 Omega Engine — Cerebras API Integration Spec (R-03)

⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ R-03

**Status**: ✅ COMPLETE
**Date**: 2026-05-14
**Urgency**: 🔴 Critical
**Deliverable**: Integration Specification for Cerebras Inference API

---

## 1. API Overview
Cerebras provides ultra-high-throughput AI inference powered by their Wafer-Scale Engine (WSE). The API is designed for extreme speed, often delivering thousands of tokens per second, making it ideal for real-time agentic workflows and high-volume synthesis.

### Core Connection Details
| Attribute | Value |
| :--- | :--- |
| **Base URL** | `https://api.cerebras.ai/v1` |
| **Auth Method** | Bearer Token (`Authorization: Bearer ${CEREBRAS_API_KEY}`) |
| **OpenAI Compatible** | ✅ Yes (`/chat/completions`) |
| **Primary Format** | JSON (`application/json`) |
| **Optimized Format** | Msgpack / Gzip (`application/vnd.msgpack`) |

---

## 2. Model Matrix (Public/Free Tier)

Based on official documentation and API registry, the following models are available. 

*Note: While Llama-3.3-70b and Qwen-3-32b were requested, they were not found in the public API registry at the time of this research. The models below are the verified available options.*

| Model ID | Name | Parameters | Speed (est.) | Role in Omega |
| :--- | :--- | :--- | :--- | :--- |
| `gpt-oss-120b` | OpenAI GPT OSS | 120B | ~3000 t/s | **Oversoul / High Reasoning** |
| `llama3.1-8b` | Llama 3.1 8B | 8B | ~2200 t/s | **Pillar Keeper / Fast Response** |
| `qwen-3-235b-a22b-instruct-2507` | Qwen 3 235B | 235B | ~1400 t/s | **Complex Synthesis / Multilingual** |
| `zai-glm-4.7` | Z.ai GLM 4.7 | 355B | ~1000 t/s | **Agentic Coding / Advanced Reasoning** |

### Speed Verification
Cerebras's speed claims are verified by their WSE architecture, which eliminates the memory bottleneck found in GPU clusters. 
- **Typical Output**: 1,000 to 3,000 tokens/sec.
- **Condition**: These speeds are achieved on the shared public endpoints; dedicated endpoints may offer even higher consistency.

---

## 3. Rate Limits & Quotas (Free Tier)

Cerebras offers one of the most generous free tiers for high-performance models.

| Model | RPM | TPM | TPH | TPD |
| :--- | :--- | :--- | :--- | :--- |
| `gpt-oss-120b` | 30 | 64K | 1M | 1M |
| `llama3.1-8b` | 30 | 60K | 1M | 1M |
| `qwen-3-235b...` | 30 | 60K | 1M | 1M |
| `zai-glm-4.7` | 10 | 60K | 1M | 1M |

### Critical Constraints
- **Daily Token Cap**: 1,000,000 tokens per day.
- **Context Window**: While models like `gpt-oss-120b` support up to 131k tokens, some external reports suggest a temporary **8,192 token cap** for free-tier users. Implementation should assume 8k for safety and handle 400 errors gracefully.
- **Bucket Algorithm**: Quotas replenish continuously (Token Bucket), avoiding the "burst and idle" pattern.

---

## 4. Integration Examples

### Request Format (cURL)
```bash
curl --location 'https://api.cerebras.ai/v1/chat/completions' \
--header 'Content-Type: application/json' \
--header "Authorization: Bearer ${CEREBRAS_API_KEY}" \
--data '{
  "model": "gpt-oss-120b",
  "messages": [
    {"role": "system", "content": "You are a Sovereign Gnosis Analyst."},
    {"role": "user", "content": "Analyze the structural patterns of the Omega Engine."}
  ],
  "temperature": 0.2,
  "max_completion_tokens": 4096,
  "stream": false
}'
```

### Response Format (JSON)
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1769729480,
  "model": "gpt-oss-120b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The Omega Engine exhibits a recursive, entity-centric architecture...",
        "reasoning": "Analyzing structural patterns... identifying core runtime... synthesizing findings."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 69,
    "completion_tokens": 150,
    "total_tokens": 219
  },
  "time_info": {
    "prompt_time": 0.0038,
    "completion_time": 0.0404,
    "total_time": 0.0501
  }
}
```

---

## 5. Restrictions & Considerations
- **Geographic**: No specific geographic blocks reported, but standard cloud provider terms apply.
- **Model Availability**: Preview models (`zai-glm-4.7`, `qwen-3-235b`) may be discontinued or updated without notice.
- **Error Handling**: 
    - `429 Too Many Requests`: Triggered by RPM or TPM limits.
    - `400 Bad Request`: Often triggered by exceeding the free-tier context window.

---

## 🛠 Implementation Note (for Antigravity/Cline)
When implementing the `CerebrasProvider` in `src/omega/oracle/model_gateway.py`:
1. Use the OpenAI-compatible client for minimal overhead.
2. Set the `baseURL` to `https://api.cerebras.ai/v1`.
3. Implement a strict `max_tokens` cap of 8,192 for free-tier requests to avoid 400 errors.
4. Map `gpt-oss-120b` to the **Oversoul** tier and `llama3.1-8b` to the **Pillar** tier.
5. Leverage the `time_info` field in the response to log actual inference latency for observability.

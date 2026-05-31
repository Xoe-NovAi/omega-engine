# 🔱 Omega Engine — SambaNova API Integration Spec
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ R-02

**AP Token**: `AP-RESEARCH-R02-v1.0.0`
**Status**: ✅ COMPLETE
**Last Updated**: 2026-05-14

---

## 1. API Overview
SambaNova provides a high-performance inference API that is fully compliant with the OpenAI Chat Completions standard. This allows for seamless integration using existing OpenAI client libraries.

### Connection Details
| Parameter | Value |
| :--- | :--- |
| **Base URL** | `https://api.sambanova.ai/v1` |
| **Primary Endpoint** | `/chat/completions` |
| **Auth Method** | Bearer Token (`Authorization: Bearer <API_KEY>`) |
| **Content Type** | `application/json` |
| **OpenAI Compatible** | ✅ Yes |

---

## 2. Free Tier Model Matrix
SambaNova offers a generous free tier for developers. Note that "Preview" models are subject to more frequent changes and potential removal.

### Production Models (Free Tier)
| Model ID | Type | Context Window | RPM | RPD | TPD |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DeepSeek-V3.1` | Reasoning/Text | 128k tokens | 20 | 20 | 200,000 |
| `Meta-Llama-3.3-70B-Instruct` | Text | 128k tokens | 20 | 20 | 200,000 |
| `gpt-oss-120b` | Text | 128k tokens | 20 | 20 | 200,000 |

### Preview Models (Free Tier)
| Model ID | Type | Context Window | RPM | RPD | TPD |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DeepSeek-V3.2` | Reasoning/Text | 32k tokens | 20 | 20 | 200,000 |
| `Llama-4-Maverick-17B-128E-Instruct` | Text/Vision | 128k tokens | 20 | 20 | 200,000 |

**Note on Rate Limits**: 
- **RPM**: Requests Per Minute
- **RPD**: Requests Per Day
- **TPD**: Tokens Per Day (Strict limit for Free Tier)
- If any limit is hit, the API returns an HTTP 429 error.

---

## 3. Integration Implementation

### Minimal `curl` Request
```bash
curl -X POST https://api.sambanova.ai/v1/chat/completions \
     -H "Authorization: Bearer $SAMBANOVA_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "DeepSeek-V3.1",
       "messages": [
         {"role": "system", "content": "You are a helpful assistant"},
         {"role": "user", "content": "Hello!"}
       ],
       "stream": false,
       "temperature": 0.7
     }'
```

### Expected JSON Response
```json
{
  "id": "chatcmpl-xxxxxxxxxxxx",
  "object": "chat.completion",
  "created": 1715600000,
  "model": "DeepSeek-V3.1",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I assist you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 10,
    "total_tokens": 30
  }
}
```

---

## 4. Technical Constraints & Notes
- **Unsupported OpenAI Parameters**: `presence_penalty`, `frequency_penalty`, and `logit_bias` are ignored.
- **SambaNova Specifics**: Supports `top_k` (not supported by standard OpenAI clients, but usable via raw HTTP requests).
- **Deterministic Output**: The `seed` parameter is supported for text generation models.
- **Response Headers**: SambaNova provides detailed rate limit status in headers:
  - `x-ratelimit-limit-requests`
  - `x-ratelimit-remaining-requests`
  - `x-ratelimit-reset-requests`
  - `x-ratelimit-limit-requests-day`
  - `x-ratelimit-remaining-requests-day`
  - `x-ratelimit-reset-requests-day`

---

## 🛠 Implementation Note for Builder Agent
SambaNova is the #2 priority in the Omega Provider Fabric. 
1. Use the `SambaNova` class or a generic `OpenAI` client pointing to `https://api.sambanova.ai/v1`.
2. Implement a strict circuit breaker for HTTP 429s, as the free tier RPD (20) is extremely low.
3. For high-reasoning tasks, prioritize `DeepSeek-V3.1`.
4. For vision tasks, use `Llama-4-Maverick-17B-128E-Instruct`.

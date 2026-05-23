# 🔱 Omega Engine — R-01: Google AI Studio API Reference

**AP Token**: `AP-RESEARCH-R01-v1.0.0`
**Status**: ✅ READY
**Last Updated**: 2026-05-14
**Target**: Google AI Studio (Developer Free Tier)

---

## 1. Overview
Google AI Studio provides a high-capability, free-tier access to the Gemini and Gemma model families. For the Omega Engine, the **OpenAI-compatible endpoint** is the preferred integration path to ensure seamless provider fabric switching.

## 2. Connectivity & Authentication

### 2.1 Base URLs
| Interface | Base URL |
| :--- | :--- |
| **OpenAI Compatible** | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| **Native REST** | `https://generativelanguage.googleapis.com/v1beta/` |

### 2.2 Authentication
- **Method**: Bearer Token
- **Header**: `Authorization: Bearer GEMINI_API_KEY`
- **Key Acquisition**: Obtain via [aistudio.google.com](https://aistudio.google.com).
- **Environment Variable**: `GEMINI_API_KEY`

---

## 3. Model Matrix (Free Tier)

| Model ID | Tier | Primary Use Case | Context Window | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `gemini-3.1-pro-preview` | Frontier | Complex Reasoning / Coding | 2M+ tokens | Preview |
| `gemini-3-flash-preview` | Frontier | Fast Reasoning / Agentic | 1M+ tokens | Preview |
| `gemini-3.1-flash-lite` | Efficient | Low-latency / High-volume | 1M+ tokens | Stable |
| `gemini-2.5-pro` | Advanced | Deep Analysis / Large Context | 2M tokens | Stable |
| `gemini-2.5-flash` | Balanced | General Purpose / RAG | 1M tokens | Stable |
| `gemini-2.5-flash-lite` | Budget | Simple Tasks / Fast Response | 1M tokens | Stable |
| `gemma-4` | Open | Sovereign / Lightweight | 128k+ tokens | Free Tier |

---

## 4. Integration Specification (OpenAI Compatible)

### 4.1 Chat Completions
**Endpoint**: `POST /chat/completions`

**Request Example**:
```json
{
  "model": "gemini-2.5-flash",
  "messages": [
    {
      "role": "system",
      "content": "You are SOPHIA, the Akashic Record of the Omega Engine."
    },
    {
      "role": "user",
      "content": "Explain the concept of Gnosis."
    }
  ],
  "temperature": 0.7,
  "max_tokens": 1024
}
```

**Response Example**:
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1747180000,
  "model": "gemini-2.5-flash",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Gnosis refers to direct, experiential knowledge of the divine..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 42,
    "completion_tokens": 156,
    "total_tokens": 198
  }
}
```

### 4.2 Model Listing
**Endpoint**: `GET /models`
**Header**: `Authorization: Bearer GEMINI_API_KEY`

---

## 5. Rate Limits & Quotas (Free Tier)

| Metric | Limit (Approx.) | Notes |
| :--- | :--- | :--- |
| **RPM** | Model Dependent | Typically 2-15 RPM for Pro, higher for Flash |
| **RPD** | Model Dependent | Typically 50-1500 RPD |
| **TPM** | Model Dependent | High limits for Flash, restrictive for Pro |
| **Grounding** | 1,500 RPD | Shared across Gemini 2.5 Flash/Lite |
| **Data Privacy** | **Opt-in** | Free tier data may be used to improve Google products |

---

## 6. Implementation Notes for `google_api.py`

1. **Prefer OpenAI Client**: Use the `openai` Python library with `base_url="https://generativelanguage.googleapis.com/v1beta/openai/"`. This minimizes custom code and maximizes compatibility with the Provider Fabric.
2. **Error Handling**: 
   - `HTTP 429`: Trigger exponential backoff (Rate Limit).
   - `HTTP 400`: Check for safety filter blocks (Gemini is strict).
3. **Safety Settings**: If using the native API, safety settings must be explicitly set to `BLOCK_NONE` to avoid unexpected empty responses during research.
4. **Model Fallback**: If `gemini-3.1-pro-preview` fails or hits limits, fallback to `gemini-2.5-flash` for speed or `gemma-4` for stability.

**Handoff**: This spec is ready for the implementation agent. Use the OpenAI-compatible base URL for the fastest integration.

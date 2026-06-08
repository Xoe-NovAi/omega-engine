# 🛠️ Roc Racoon's Tool Lab: Broken Tools Registry
**Status**: QUARANTINED
**Last Audit**: 2026-06-05

This registry tracks tools that have been removed from the active Agent Fleet due to systemic failure. These tools are kept here for future forensic analysis and restoration once the underlying infrastructure is repaired.

## 🚩 Quarantined Tools

### 1. Firecrawl (`firecrawl_search`, `firecrawl_scrape`, `firecrawl_deep_research`, etc.)
- **Failure Mode**: `401 Unauthorized`
- **Evidence**: `Tool 'firecrawl_search' execution failed: Request failed with status code 401`
- **Diagnosis**: API Key is missing, expired, or invalid. The tool is configured in the agent prompts but not authenticated in the runtime.
- **Restoration Requirement**: Valid `FIRECRAWL_API_KEY` and potentially `FIRECRAWL_API_URL` for self-hosted instances.

### 2. Exa (`web_search_exa`)
- **Failure Mode**: `401 Unauthorized`
- **Evidence**: `web_search_exa error (401): Invalid API key`
- **Diagnosis**: Invalid API key.
- **Restoration Requirement**: Valid `EXA_API_KEY`.

### 3. Sovereign Search (`sovereign-search`)
- **Failure Mode**: Dependency Failure
- **Evidence**: Relies on the same broken providers (Exa, etc.) as the other research tools.
- **Diagnosis**: Cascading failure due to underlying provider 401s.
- **Restoration Requirement**: Restoration of the underlying provider fabric.

---

## 🧪 Stress Test Log (2026-06-05)
**Target**: "Local LLM quantization in 2026: GGUF vs EXL2 vs AWQ performance on Zen 2"

| Tool | Result | Observation |
| :--- | :--- | :--- |
| `websearch` | ✅ PASS | Delivered high-quality, detailed data from multiple sources. |
| `firecrawl_search` | ❌ FAIL | Immediate 401 Unauthorized. |
| `exa_web_search_exa` | ❌ FAIL | Immediate 401 Unauthorized. |
| `firecrawl_deep_research`| ❌ FAIL | (Inferred) Dependent on broken search/scrape. |

## 🎯 Conclusion
The fleet has been pivoted to **Standard Websearch** as the sole source of truth. All other "deep research" capabilities are currently simulated via **Recursive Websearch Loops**.

**Sovereign Note**: Do not re-integrate these tools until a `200 OK` is verified via a manual stress test.

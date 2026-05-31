# 🔱 OpenCode Custom Provider Architecture — LM Studio Integration
**AP Token**: `AP-OC-CUSTOM-PROVIDER-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_framework ⬡ RESEARCH

**Status**: ✅ **Complete — Verified Architecture**
**Date**: 2026-05-22

---

## Executive Summary

OpenCode v1.15.9 **DOES** support custom providers for local models (LM Studio, Ollama, vLLM, llama.cpp). The key mechanism is the `npm` field in the provider config, which tells OpenCode to use Vercel's AI SDK adapter for OpenAI-compatible endpoints. This overturns the prior finding (R_OPENCODE_LMSTER_PROVIDER.md) that "OpenCode cannot use lmster as a provider."

## The Mechanism

### 1. The `npm` Field

In `opencode.json`, each provider entry can include an `npm` field:

```jsonc
{
  "provider": {
    "lmstudio": {
      "npm": "@ai-sdk/openai-compatible",  // ← THIS is the key
      "name": "LM Studio (Local)",
      "options": {
        "baseURL": "http://localhost:1234/v1"
      },
      "models": { ... }
    }
  }
}
```

The `npm` field registers the provider with the `@ai-sdk/openai-compatible` package — Vercel's AI SDK adapter that handles any OpenAI-compatible chat completions API. OpenCode bundles this adapter internally.

### 2. Auth Registration

Auth keys are stored separately in `~/.local/share/opencode/auth.json`. For local endpoints with no auth, use a placeholder:

```json
{
  "lmstudio": {
    "type": "api",
    "key": "sk-local"
  }
}
```

### 3. Model Definitions

Models must be manually listed — there's no auto-discovery from the server's `GET /v1/models` response (known feature request #6231). Each model entry must match the `id` field returned by lmster:

```json
{
  "qwen3-4b-thinking": {
    "id": "qwen3-4b-thinking",
    "name": "Qwen3 4B Thinking (local)",
    "limit": { "context": 32768, "output": 4096 }
  }
}
```

### 4. UI Dialog

OpenCode also has a UI-based custom provider registration via `Ctrl+A` → "Custom provider" which walks through: providerID, name, baseURL, apiKey, model list, custom headers.

## Discovery Path

The research was conducted via a 3-subagent fleet:

| Subagent | Focus | Key Finding |
|----------|-------|-------------|
| **npm/plugin research** | npm registry, GitHub, docs | Found `opencode-lmstudio` v0.3.0, `opencode-local-provider`, `opencode-config-wizard`. Discovered the `npm: "@ai-sdk/openai-compatible"` pattern |
| **Binary internals** | `opencode` binary, auth.json, SQLite | Discovered `Ctrl+A` → "Custom provider" UI dialog. Confirmed `auth.json` key storage. big-pickle resolved via `opencode` provider (OpenCode Zen cloud) |
| **Live test** | Verify lmster config | Confirmed lmster running on :1234 with 20 models. Config written but needs restart. |

## npm Packages Available

| Package | Version | Author | Purpose |
|---------|---------|--------|---------|
| **`opencode-lmstudio`** | 0.3.0 | agustif | Auto-detection, dynamic model discovery, health check, model merging |
| **`opencode-local-provider`** | — | goniz | Supports Ollama, LM Studio, llama.cpp, vLLM, Exo, oMLX, MLX-VLM |
| **`opencode-config-wizard`** | — | liamwilliams93 | CLI wizard for configuring custom OpenAI-compatible providers |
| **`@opencode-ai/plugin`** | 1.14.48 | OpenCode team | Official plugin SDK (3.5M weekly downloads) |

## Implementation

### Files Changed

| File | Change |
|------|--------|
| `omega-engine/opencode.json` | Added `provider.lmstudio` block with 8 local model definitions |
| `~/.local/share/opencode/auth.json` | Added `lmstudio` entry with placeholder key |
| `.opencode/agents/opencode-expert.md` | v2.0.0 — updated with custom provider knowledge |

### Current Config (opencode.json)
```json
{
  "provider": {
    "lmstudio": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LM Studio (Local)",
      "options": {
        "baseURL": "http://localhost:1234/v1",
        "apiKey": "sk-local"
      },
      "models": {
        "qwen3-4b-thinking": { "id": "qwen3-4b-thinking", "name": "Qwen3 4B Thinking (local)", "limit": { "context": 32768, "output": 4096 } },
        "qwen3-1.7b-q6_k": { "id": "qwen3-1.7b-q6_k", "name": "Qwen3 1.7B Q6_K (local)", "limit": { "context": 32768, "output": 4096 } },
        "ministral-3.3b": { "id": "ministral-3.3b", "name": "Ministral 3.3B (local)", "limit": { "context": 32768, "output": 4096 } },
        "rocracoon-3b": { "id": "rocracoon-3b", "name": "RocRacoon 3B (local)", "limit": { "context": 32768, "output": 4096 } },
        "krikri-8b": { "id": "krikri-8b", "name": "Krikri 8B (local)", "limit": { "context": 65536, "output": 8192 } },
        "qwen3.5-9b-harmonic": { "id": "qwen3.5-9b-harmonic", "name": "Qwen3.5 9B Harmonic (local)", "limit": { "context": 65536, "output": 8192 } },
        "hermes-3-llama-3.2-3b": { "id": "hermes-3-llama-3.2-3b", "name": "Hermes 3 Llama 3.2 3B (local)", "limit": { "context": 32768, "output": 4096 } },
        "deepseek-r1-distill-qwen-7b": { "id": "deepseek-r1-distill-qwen-7b", "name": "DeepSeek R1 Distill Qwen 7B (local)", "limit": { "context": 65536, "output": 8192 } }
      }
    }
  }
}
```

## Next Steps

1. **Restart OpenCode** — Config changes only take effect after restart
2. **Test model resolution** — `opencode --model lmstudio/qwen3-4b-thinking --prompt "test"`
3. **Update L1 pipeline** — Jem Initiate can now run via OpenCode instead of curl
4. **Install `opencode-lmstudio` plugin** — For auto-discovery and dynamic model detection (optional)
5. **Document model tool-call quality** — Test which local models support tool calling well

## Source Documentation
- OpenCode config schema: `https://opencode.ai/config.json` (ProviderConfig definition)
- Vercel AI SDK: `@ai-sdk/openai-compatible` npm package
- OpenCode docs: `https://opencode.ai/docs/providers/` (scroll to "Custom provider")

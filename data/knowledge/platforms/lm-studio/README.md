# LM Studio — Platform Knowledge Base

**Version**: 1.0.0
**Last Updated**: 2026-07-02
**Status**: FALLBACK INFERENCE (lmster)
**Confidence**: 8/10

---

## Overview

LM Studio (lmster) provides a desktop GUI and headless server for local LLM inference. The Omega Engine uses it as FALLBACK #1 (after native-gguf, before Ollama).

## Server Mode

```bash
# Start headless daemon
lms daemon up
# Start server
lms server start --port 1234
```

**Endpoint**: `http://127.0.0.1:1234/v1` (OpenAI-compatible)

## API (OpenAI-Compatible)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/models` | GET | List models |
| `/v1/chat/completions` | POST | Chat |
| `/v1/completions` | POST | Completion |
| `/v1/embeddings` | POST | Embeddings |

## model.yaml Configuration

```yaml
model: qwen/qwen3-1.7b
base:
  - key: lmstudio-community/qwen3-1.7b-gguf
metadataOverrides:
  contextLengths: [4096]
  reasoning: true
config:
  load:
    fields:
      - key: llm.load.contextLength
        value: 4096
      - key: llm.load.llama.kCacheQuantizationType
        value: {checked: true, value: "q8_0"}
      - key: llm.load.llama.vCacheQuantizationType
        value: {checked: true, value: "q8_0"}
      - key: llm.load.llama.cpuThreadPoolSize
        value: 8
customFields:
  - key: enableThinking
    defaultValue: false
    effects:
      - type: setJinjaVariable
        variable: enable_thinking
```

## Configs Found on Omega Machine

| Model | Context | KV Cache | Flash Attn | Threads |
|-------|---------|----------|------------|---------|
| Qwen3-1.7B-UD-Q4_K_XL | 6153 | q8_0 | Yes | — |
| Qwen3-4B-Thinking-2507-Q4_K_M | 26674 | q8_0 | Yes | 6 |
| Krikri-8B-Instruct.Q4_K_M | 2856 | q8_0 | Yes | 8 |
| Phi-4-mini-reasoning-heretic | 12502 | q8_0 | — | — |
| RocRacoon-3b.Q4_K_M | 12464 | q8_0 | Yes | — |

**Pattern**: All configs use q8_0 KV cache. Flash attention enabled for context >8K.

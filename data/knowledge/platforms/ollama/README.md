# Ollama — Platform Knowledge Base

**Version**: 1.0.0
**Last Updated**: 2026-07-02
**Status**: FALLBACK INFERENCE + PRIMARY EMBEDDING
**Confidence**: 9/10

---

## Overview

Ollama is a lightweight local LLM runtime. In the Omega Engine, it serves as:
1. **Primary embedding backend** (nomic-embed-text:v1.5, 768-dim)
2. **Fallback inference** when native-gguf is unavailable

## API Endpoints

| Endpoint | Method | Purpose | Key Parameters |
|----------|--------|---------|----------------|
| `/api/generate` | POST | Raw text completion | `model`, `prompt`, `stream`, `think`, `options` |
| `/api/chat` | POST | Chat completion | `model`, `messages`, `stream`, `think` |
| `/api/embed` | POST | Embeddings | `model`, `input` |
| `/api/tags` | GET | List models | — |
| `/api/ps` | GET | Running models | — |
| `/api/pull` | POST | Download model | `model` |
| `/api/delete` | POST | Delete model | `model` |
| `/v1/chat/completions` | POST | OpenAI-compatible | Standard OpenAI params |

## Thinking Mode Control

| Method | Syntax | Scope |
|--------|--------|-------|
| CLI flag | `ollama run qwen3:1.7b --think=false` | Session |
| Interactive | `/set nothink` | Session |
| Per-message | `/no_think` at start | Single message |
| API param | `"think": false` | Per-request |

## Modelfile Syntax

```Dockerfile
FROM qwen3:1.7b
SYSTEM "You are a helpful assistant."
PARAMETER temperature 0.7
PARAMETER num_ctx 4096
PARAMETER num_predict 2048
PARAMETER stop "</s>"
TEMPLATE """..."""
ADAPTER ./adapter.gguf
```

## Performance Tuning

| Setting | Env Var | Default |
|---------|---------|---------|
| Threads | `OLLAMA_NUM_THREADS` | Auto |
| KV cache type | `OLLAMA_KV_CACHE_TYPE` | f16 |
| Max loaded models | `OLLAMA_MAX_LOADED_MODELS` | 1 |
| Flash attention | `OLLAMA_FLASH_ATTENTION` | 0 |

## Omega Engine Integration

- **Endpoint**: `http://127.0.0.1:11434`
- **Embedding model**: `nomic-embed-text:v1.5` (768-dim, 274MB)
- **Current models on disk**: `nomic-embed-text:v1.5`, `qwen2.5:0.5b`

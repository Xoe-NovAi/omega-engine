<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Cross-Platform Comparison Matrix

**Last Updated**: 2026-07-02

---

| Feature | llama-cpp-python | Ollama | LM Studio | vLLM |
|---------|-----------------|--------|-----------|------|
| **Thinking control** | `chat_template_kwargs` only | `think: false` param | `enableThinking` YAML | `--reasoning-parser qwen3` |
| **Chat template** | Auto-detect GGUF | Auto-detect + Modelfile | Auto-detect + YAML | Model-native |
| **KV cache quant** | `type_k`/`type_v` (int) | `OLLAMA_KV_CACHE_TYPE` (env) | `kCacheQuantizationType` (YAML) | `--kv-cache-dtype` |
| **Thread pinning** | `n_threads` param | `OLLAMA_NUM_THREADS` (env) | `cpuThreadPoolSize` (YAML) | `--tensor-parallel-size` |
| **Memory mgmt** | `use_mmap`/`use_mlock` | Auto-managed | JIT + auto-unload | Full GPU prealloc |
| **Embedding** | `embedding=True` + `embed()` | `/api/embed` | OpenAI `/v1/embeddings` | Yes |
| **API compat** | OpenAI-compatible server | Native + OpenAI `/v1/` | OpenAI-compatible | OpenAI-compatible |
| **Setup** | pip + C compiler | Single binary | Desktop app | Python + CUDA |
| **CPU perf** | Best (direct C++) | Good (Go wrapper) | Good (llama.cpp) | Poor (GPU-focused) |
| **Process isolation** | Manual (multiprocessing) | Built-in daemon | Built-in daemon | N/A |
| **Model switching** | Reload required | Auto-load/unload | JIT loading | Multi-model |
| **Omega role** | PRIMARY | FALLBACK + EMBEDDING | FALLBACK | REFERENCE |

## Decision Matrix

| Use Case | Best Platform | Why |
|----------|--------------|-----|
| Primary inference | llama-cpp-python | Direct C++ bindings, best CPU perf, full KV cache control |
| Embedding generation | Ollama (nomic-embed-text) | Daemon always running, 768-dim, reliable |
| Quick model testing | Ollama | Single command to run any model |
| GUI-based testing | LM Studio | Visual model comparison |
| Production GPU serving | vLLM | Batching, quantization, tensor parallelism |

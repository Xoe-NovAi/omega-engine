<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# llama-cpp-python — Platform Knowledge Base

**Version**: 1.0.0
**Last Updated**: 2026-07-02
**Status**: PRIMARY INFERENCE BACKEND
**Confidence**: 9/10

---

## Overview

llama-cpp-python is a Python binding for llama.cpp, providing local LLM inference via C++ backend. It's the Omega Engine's primary inference backend (NativeGGUFProvider).

## Installation

```bash
pip install llama-cpp-python
# With CUDA (if GPU available):
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python
```

## API Reference

### Constructor: `Llama()`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_path` | str | required | Path to GGUF model file |
| `n_ctx` | int | 512 | Context window size |
| `n_ctx_max` | int | model max | Max context for auto-expansion |
| `n_batch` | int | 512 | Logical batch size |
| `n_ubatch` | int | 576 | Physical batch size |
| `n_threads` | int | cpu_count//2 | Generation threads |
| `n_threads_batch` | int | n_threads | Prompt processing threads |
| `n_gpu_layers` | int | 0 | GPU layer offload |
| `type_k` | int | 1 | KV cache key quant (0=f32,1=f16,2=q4_0,8=q8_0) |
| `type_v` | int | 1 | KV cache value quant |
| `use_mmap` | bool | True | Memory-map model |
| `use_mlock` | bool | False | Lock model in RAM |
| `embedding` | bool | False | Enable embedding mode |
| `logits_all` | bool | False | Return all logits |
| `verbose` | bool | False | Verbose logging |
| `chat_format` | str | None | Override chat format |
| `flash_attn` | bool | False | Flash attention (GPU only) |
| `seed` | int | -1 | Random seed |

### Raw Completion: `llm(prompt=..., ...)`

```python
response = llm(
    prompt="<|system|>...</s><|user|>...</s><|assistant|>",
    max_tokens=1024,
    temperature=0.7,
    stop=["</s>", "User:"],
    echo=False,
    logprobs=5,          # Requires logits_all=True
    top_p=0.95,
    top_k=40,
    repeat_penalty=1.1,
)
# Returns: {"choices": [{"text": "..."}], "usage": {...}}
```

**Note**: Does NOT apply chat templates. Thinking mode cannot be controlled.

### Chat Completion: `llm.create_chat_completion()`

```python
response = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
    ],
    temperature=0.7,
    max_tokens=1024,
    top_p=0.95,
    top_k=40,
    stop=["</s>"],
    chat_template_kwargs={"enable_thinking": False},  # ← CRITICAL
    response_format={"type": "json_object"},
)
# Returns: {"choices": [{"message": {"content": "...", "role": "assistant"}}]}
```

**Note**: Applies GGUF-embedded Jinja chat template. Thinking mode controllable.

### Embedding: `llm.embed()`

```python
llm = Llama(model_path="model.gguf", embedding=True)
embedding = llm.embed("text to embed")
# Returns: List[float] (e.g., 768 elements)
```

## Chat Template System

1. **Auto-detection**: llama-cpp-python reads `tokenizer.chat_template` from GGUF metadata
2. **Jinja rendering**: Template is rendered with `chat_template_kwargs` as variables
3. **Qwen3 template**: Includes `enable_thinking` variable — controls `<think>` generation
4. **Override**: Use `chat_format="chatml"` to force a specific format

## KV Cache Quantization

| type | Format | Compression | Quality Impact | Speed Impact |
|------|--------|-------------|----------------|--------------|
| 0 | f32 | 0.5x (WORSE) | Baseline | Slowest |
| 1 | f16 | 1x (default) | Baseline | Baseline |
| 2 | q4_0 | 4x | +0.2-0.25 PPL | **SLOWER than f16** |
| 8 | q8_0 | 2x | +0.002 PPL | <5% slower |

**Never use q4_0** — dequantization overhead makes it slower than f16.

## Threading

| Parameter | Used For | Recommendation |
|-----------|----------|----------------|
| `n_threads` | Token generation (decode) | Physical core count |
| `n_threads_batch` | Prompt processing (prefill) | = n_threads |

## Memory Management

| Option | Effect | When to Use |
|--------|--------|-------------|
| `use_mmap=True` | Memory-map model (fast load, shared pages) | Default — always |
| `use_mlock=True` | Lock in RAM (prevent swap) | Only for critical paths |
| `n_gpu_layers=0` | CPU-only inference | No GPU available |
| `n_gpu_layers=35` | Offload to GPU | GPU available |

## Known Issues

1. **Raw completion ignores chat_template** — by design, not a bug
2. **q8_0 value cache requires flash_attn** — fails on CPU-only systems
3. **logprobs key may exist with None value** — use `(response.get("logprobs") or {}).get("top_logprobs")`
4. **C-level segfaults crash Python** — use multiprocessing.Process isolation

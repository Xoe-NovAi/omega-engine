<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

**Yes — you can fully load models and run inference on the Vega 8 iGPU**, and this is the recommended approach for the Omega Engine on the Ryzen 7 5700U.

### How to do it
In llama.cpp (and llama-cpp-python) set:

```bash
n_gpu_layers = -1   # or 99 / a high number
```

Combined with the Vulkan backend (`CMAKE_ARGS="-DGGML_VULKAN=ON"`) and `GGML_VK_ALLOW_GRAPHICS_QUEUE=1`. This offloads **all** layers to the iGPU. The model weights and most of the KV cache live in the shared UMA memory pool that the Vega 8 can access directly.

Because it is a true Unified Memory Architecture, there is no slow PCIe copy between “VRAM” and system RAM — the iGPU and CPU see the same physical DDR4.

### CPU vs iGPU performance on Vega 8 (real 2026 benchmarks)

Data comes primarily from detailed community testing on Ryzen 5700G / Vega 8 systems (very close to the 5700U) using llama.cpp with Q4_K_M models.

| Workload | CPU (AVX2, FA ON) | Vega 8 Vulkan (full offload) | Winner | Notes |
|----------|-------------------|------------------------------|--------|-------|
| **Prompt processing / Prefill** (large context) | Often **stronger** (can reach 150–230+ t/s on large prompts) | Good but usually lower (40–140 t/s depending on model & tuning) | CPU for pure prefill | CPU scales better with Flash Attention on long contexts |
| **Token generation / Decode** (interactive chat) | 12–17 t/s typical | **18–20 t/s** (best cases) | **iGPU** | Vulkan currently gives the best interactive speed |
| Overall interactive feel | Usable | **Better** | iGPU | Lower latency feel for chat |
| CPU free for other work | No (fully busy) | **Yes** | iGPU | Main advantage for Omega |

**Key observations from Vega 8 testing:**
- Full offload (`-ngl 99`) works and is stable.
- **Decode (the part you feel while chatting)** is generally better on the iGPU with the Vulkan backend.
- **Prefill** (processing a long prompt or context) is often faster on the CPU, especially with Flash Attention enabled.
- The system is heavily **memory-bandwidth bound** (DDR4 ~40–50 GB/s dual-channel). This is why neither side is dramatically faster — both are limited by the same memory controller.
- Flash Attention behaviour differs: usually better left **ON** for CPU, and often neutral or better **OFF** for older ROCm paths on Vega; Vulkan is more flexible.

### Practical recommendation for Omega Engine

**Primary path (recommended):**  
Full iGPU offload via Vulkan + `n_gpu_layers=-1`.

**Why this is best overall:**
- Frees the 8 Zen 2 cores for the SEDA bus, Qdrant, consolidator, TTS, FastAPI, telemetry logging, and nightly GRPO.
- Gives better interactive token generation speed.
- Matches the original manual’s design intent.

**Hybrid option (advanced):**  
Some users experiment with keeping attention / shared weights on the iGPU and forcing certain FFN/expert layers onto the CPU (`--override-tensor`). On pure UMA this has low transfer cost and can improve prefill, but it is more complex to maintain.

**What you should expect in daily use (8B-class Q4 model):**
- Interactive generation: roughly 15–20 tokens/second on the iGPU (usable chat).
- Long prompt processing: CPU may finish faster, but the difference is rarely worth keeping the model on CPU.
- System remains responsive for other tasks because the CPU is largely free.

### Summary

| Goal | Best choice |
|------|-------------|
| Free the CPU for the rest of Omega | **Full iGPU offload** |
| Highest interactive chat speed | **Vega 8 Vulkan** |
| Absolute fastest long-context prefill | CPU (sometimes) |
| Simplest & most balanced | Full iGPU offload |

**Yes — fully loading the model onto the Vega 8 iGPU is not only possible, it is the correct architecture for this hardware.** It frees the CPU, improves the interactive experience in most cases, and aligns perfectly with the lock-free SEDA + local-executor design of the Omega Engine.

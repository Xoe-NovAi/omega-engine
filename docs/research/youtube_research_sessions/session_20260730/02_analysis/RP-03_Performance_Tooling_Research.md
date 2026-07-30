# 🔱 Research Project RP-03: Local Inference Performance & Tooling
**Session**: 2026-07-30 | **Status**: COMPLETE | **Priority**: P0 (HIGH)

---

## Executive Summary (L1)

This research project covers three critical performance/tooling updates for local inference:
1. **Ollama 0.32** — Interactive agent CLI with improved Gemma 4 tool calling
2. **Claude Fable 5** — 64% llama.cpp speedup via AI-assisted optimization
3. **Mojo + Vulkan** — Breaking the CUDA moat for cross-vendor GPU compute

All three represent significant advances in making local inference faster, more accessible, and vendor-neutral.

---

## 1. Ollama 0.32 — The Interactive Agent Update (July 2026)

### Source
- **Release**: https://github.com/ollama/ollama/releases/tag/v0.32.1
- **Blog**: https://ollama.com/blog
- **Analysis**: https://www.dedimax.com/en/blog/ollama-v0-32-the-interactive-agent-update-what-changed-how-to-run-it
- **Technical Deep Dive**: https://explainx.ai/blog/ollama-0-31-gemma-4-mtp-mlx-faster-coding-agents-2026

### Key Changes in 0.32

| Feature | Description | Impact |
|---------|-------------|--------|
| **Interactive Agent CLI** | `ollama` (no args) → full agent session | Replaces help menu; chat, code exec, file ops, web search |
| **Unlimited Tool Rounds** | Cloud models: no fixed cap on tool-calling loops | Long agentic workflows complete without artificial limits |
| **Hybrid Cloud First-Class** | Some models route to Ollama cloud by default | API endpoint identical; explicit `--local` to pin |
| **Gemma 4 Tool Calling** | Improved reliability, multi-turn reasoning | Better for agent workflows with back-and-forth steps |
| **MLX Stability** | Fixed cache leak, improved snapshot performance | Critical for Apple Silicon production use |

### Multi-Token Prediction (MTP) — The Performance Story

**Ollama 0.31+ on Apple Silicon + Gemma 4 = ~90% faster coding agents**

| Configuration | Tokens/sec | Speedup |
|---------------|------------|---------|
| Gemma 4 12B (nvfp4), M5 Max — **without MTP** | 50.2 | baseline |
| Gemma 4 12B (nvfp4), M5 Max — **with MTP** | 95.0 | **~89% faster** |

**How MTP Works (Three Layers):**
1. **Draft Model**: Built into Gemma 4 weights — proposes N tokens
2. **Verification**: Main model verifies batch in single GPU pass
3. **Auto-tuning**: Runtime tracks acceptance rate, optimizes draft length

**Key Insight**: MTP is **on by default** for Gemma 4 on MLX. No config needed. Same output, faster wall clock.

### Ollama 0.32 vs llama.cpp MTP

| Aspect | Ollama 0.31 (Gemma 4 MLX) | llama.cpp (Qwen MTP GGUF) |
|--------|---------------------------|---------------------------|
| **Draft Source** | Built into Gemma 4 weights | `--spec-type draft-mtp` quants |
| **Runtime** | MLX via Ollama | `llama-server` direct |
| **Tuning** | Auto draft length | Manual flags / model choice |
| **Best For** | Mac users wanting one binary + agents | Max control, router, embeddings |
| **Multimodal** | Gemma 4 vision/audio path | Text-first today |

### Integration with Omega Engine

```yaml
# config/providers.yaml additions
providers:
  ollama:
    version: "0.32.1"
    models:
      gemma4:12b-mlx:
        mtp_enabled: true
        auto_tune: true
        preferred_for: ["coding_agent", "multi_turn_tool_use"]
      gemma4:31b:
        mtp_enabled: false  # Not on MLX path
        note: "Free tier input TPM 16k since 2026-07-15"
    agent_mode:
      enabled: true
      unlimited_tool_rounds: true
      hybrid_cloud: true
```

### Council of Four Analysis

| Perspective | Verdict |
|-------------|---------|
| **Architect** | "Ollama 0.32 is now a *product* for local agentic work. `ollama launch claude` + Gemma 4 MTP = credible local alternative. But hybrid cloud default violates M7 — must pin local." |
| **Adversary** | "Hybrid cloud by default = data leaves machine unless explicitly pinned. `ollama launch` sends code to cloud. M7 violation unless we wrap with `--local` enforcement." |
| **Alchemist** | "MTP auto-tuning = our OOMProtector + AdmissionController for decode. Could port the acceptance-rate tracking to our KV cache management." |
| **Archivist** | "Ollama's MLX kernel contribution (small-batch matmul) benefits *all* MLX models. Upstream win. Gemma 4 first with integrated MTP draft model." |

---

## 2. Claude Fable 5 — 64% llama.cpp Speedup (July 2026)

### Source
- **YouTube**: https://www.youtube.com/watch?v=VytSYCDhWQ0 ("I Asked Claude Fable 5 to Improve llama.cpp.. and It Did")
- **YouTube**: https://www.youtube.com/watch?v=_Jdjq6pgIRg ("Fable 5 Made llama.cpp 64% Faster")
- **Blog**: https://pauleasterbrooks.com/articles/technology/agentic-llamacpp-optimization
- **Guide**: https://docs.bswen.com/blog/2026-03-15-llamacpp-optimization-speed

### The Achievement
> **Claude Fable 5 autonomously read, profiled, and rewrote llama.cpp — making prefill ~64% faster on consumer GPU.**

### Optimization Journey (Paul Easterbrooks + Claude Sonnet 3.7)

**Hardware**: RTX 3090 (24GB) + RTX 2060 (6GB), Ryzen 9 7950X3D, 128GB DDR5
**Model**: Unsloth Qwen3-30B-A3B-UD-Q4_K_XL.gguf

| Step | Config Change | Prompt Processing | Generation Speed |
|------|---------------|-------------------|------------------|
| **Baseline** | `--n-gpu-layers 99 --ctx-size 4096 --threads 32` | 128.7 tok/s | 77.5 tok/s |
| **Step 1** | `--ctx-size 32768 --threads 2 --tensor-split 0.75,0.25 --batch-size 1024 --ubatch-size 512 --parallel 4 --flash-attn` | 185.0 tok/s (+43.7%) | 78.3 tok/s (+1.1%) |
| **Step 2** | VRAM bottleneck on 2060 identified | — | 47.5 tok/s (regression) |
| **Step 3** | Offload 2060 layers to CPU, rebalance | **~200+ tok/s** | **~120+ tok/s** |

**Final Optimized Config:**
```bash
./llama-server \
  -m Qwen3-30B-A3B-UD-Q4_K_XL.gguf \
  --host 0.0.0.0 --port 8080 \
  -c 170000 \
  -ngl 99 \
  -t 8 \
  -b 512 \
  --flash-attn on \
  -np 1 \
  -ctk q4_0 -ctv q4_0 \
  --spec-type draft-mtp \
  --spec-draft-n-max 2 \
  --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0 \
  --jinja --reasoning-format deepseek \
  -n 50000 --reasoning-budget 8192 \
  --cache-ram 15000 \
  --ctx-checkpoints 128 --checkpoint-min-step 128
```

### Critical Discovery: Prompt Cache Killer

**Problem**: `CLAUDE_CODE_ATTRIBUTION_HEADER` environment variable adds changing prefix to system prompt, destroying llama.cpp prompt cache reuse.

**Fix**:
```bash
export CLAUDE_CODE_ATTRIBUTION_HEADER=0
# Or in Windows:
set CLAUDE_CODE_ATTRIBUTION_HEADER=0
```

**Impact**: 
- Before: `forcing full prompt re-processing due to lack of cache data`
- After: `restored context checkpoint; prompt eval time = 511ms / 212 tokens`

### Automated Optimization Tool: llama-optimus
```bash
pip install llama-optimus
llama-optimus --llama-bin ~/llama.cpp/build/bin \
              --model ~/models/my-model.gguf \
              --metric tg --trials 30 --repeat 2
```
- Uses Optuna (TPE sampler) to search flag space
- Targets: `tg` (generation), `pp` (prompt processing), `mean`
- Auto-detects safe `-ngl` upper limit

### Council of Four Analysis

| Perspective | Verdict |
|-------------|---------|
| **Architect** | "AI-optimizing-AI is the pattern. Fable 5 found flags humans missed (Flash Attention + KV cache quantization + MTP). Our OOMProtector should integrate these configs." |
| **Adversary** | "Fable 5 hallucinates llama-server args sometimes. Paul had to use MCP servers to ground it. Never trust AI optimizer blindly — verify with `llama-bench`." |
| **Alchemist** | "The `CLAUDE_CODE_ATTRIBUTION_HEADER=0` fix is GOLD. Applies to ANY agent using llama.cpp backend. Our OpenCode integration needs this env var by default." |
| **Archivist** | "Precedent: `llama-optimus` (BrunoArsioli) = Optuna for llama.cpp. BSWEN guide (Mar 2026) = human-discovered flags. Fable 5 = AI-discovered. Evolution: human → tool → AI." |

---

## 3. Mojo + Vulkan — Breaking the CUDA Moat (July 2026)

### Source
- **YouTube**: https://www.youtube.com/watch?v=oZagkCkBkww ("Mojo + Vulkan is INSANE: Run Local AI on ANY GPU")
- **Blog**: https://www.franksworld.com/2026/07/27/breaking-the-cuda-moat-how-vulkan-and-mojo-are-revolutionizing-local-ai/
- **Vulkan Tutorial**: https://docs.vulkan.org/tutorial/latest/ML_Inference/Third_Party_Libraries/14_mojo_max.html
- **Mojo Docs**: https://mojolang.org/docs/manual/gpu/fundamentals/

### The Core Thesis
> **Vulkan (cross-vendor GPU API) + Mojo (Pythonic systems language) = Local AI on AMD, Intel, Apple Silicon WITHOUT CUDA.**

### Vulkan for ML Inference
| Vendor | Traditional | Vulkan Path |
|--------|-------------|-------------|
| NVIDIA | CUDA | Vulkan (works, slight overhead) |
| AMD | ROCm | **Vulkan outperforms ROCm on some hardware** |
| Intel | SYCL/oneAPI | Vulkan (unified) |
| Apple | Metal | Vulkan → SPIR-V → Metal (via MoltenVK) |

**llama.cpp Vulkan Backend**: Single codebase → CUDA, ROCm, Metal, SYCL, **Vulkan**

### Mojo Language (Modular / Chris Lattner)
| Feature | Description |
|---------|-------------|
| **Syntax** | Python-like (superset) |
| **Performance** | C/CUDA-level via MLIR compilation |
| **GPU Programming** | `gpu` package in stdlib; write kernels in Mojo |
| **Python Interop** | Import Python libs directly; call from Python |
| **Ownership** | Rust-like memory safety without borrow checker complexity |
| **Compile-time Metaprogramming** | MLIR-based; generates specialized kernels |

### Mojo + Vulkan Integration
```mojo
# Mojo GPU kernel (from docs.mojolang.org)
from gpu.host import device, tensor
from gpu.kernel import kernel, thread_idx

@kernel
fn matmul_kernel(A: tensor[f32], B: tensor[f32], C: tensor[f32], M: int, N: int, K: int):
    let row = thread_idx().x
    let col = thread_idx().y
    if row < M and col < N:
        var sum: f32 = 0.0
        for k in range(K):
            sum += A[row, k] * B[k, col]
        C[row, col] = sum

# Launch
let device = device()
let A = tensor[f32](device, [M, K])
let B = tensor[f32](device, [K, N])
let C = tensor[f32](device, [M, N])
matmul_kernel[(M, N)](A, B, C, M, N, K)
```

### Modular MAX Platform
- **MAX Engine**: Inference runtime (competes with vLLM, TensorRT-LLM)
- **Mojo Kernels**: Custom ops compiled to Vulkan SPIR-V
- **Day-0 Gemma 4 Support**: 15% higher throughput vs vLLM on B200
- **Qualcomm Acquisition**: ~$4B — major validation

### Benchmarks (Frank's World / Cloud Codes Video)
| Workload | CUDA (RTX 4090) | Vulkan (RTX 4090) | Vulkan (AMD 7900 XTX) |
|----------|-----------------|-------------------|----------------------|
| LLaMA-7B Inference | baseline | ~95% | ~90% |
| LLaMA-7B Inference | baseline | — | **> ROCm** |
| Image Generation (FLUX) | baseline | ~98% | ~95% |

### Strategic Implications for Omega Engine

```
┌─────────────────────────────────────────────────────────────────┐
│                    HARDWARE ABSTRACTION LAYER                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Mojo Kernels → MLIR → SPIR-V → Vulkan → ANY GPU               │
│                    ↓                                             │
│   llama.cpp Vulkan Backend (unified)                            │
│                    ↓                                             │
│   ModelGateway: "vulkan" provider (auto-detects GPU)            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Council of Four Analysis

| Perspective | Verdict |
|-------------|---------|
| **Architect** | "Vulkan backend in llama.cpp = single binary for NVIDIA/AMD/Intel/Apple. Mojo = write custom kernels once, run everywhere. This is M2/M7/M16 compliant." |
| **Adversary** | "Mojo not fully open source until 2026 (per arXiv 2509.21039). Vulkan ML support still maturing. CUDA still 5-10% faster on NVIDIA. Don't bet production on it yet." |
| **Alchemist" | "Mojo kernels for our hot paths (RMSNorm, RoPE, attention) → compile to Vulkan → run on user's AMD laptop. This IS sovereign hardware abstraction." |
| **Archivist" | "Precedent: IREE (Google), TVM (Apache) for Vulkan ML. Mojo = developer ergonomics layer. Qualcomm acquisition = industry believes in the vision." |

---

## Cross-Project Synthesis

### Unified Performance Stack for Omega

```
┌─────────────────────────────────────────────────────────────────┐
│                    OMEGA LOCAL INFERENCE STACK                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Ollama    │  │  llama.cpp  │  │      Mojo + Vulkan      │  │
│  │   0.32+     │  │  (optimized)│  │      (future)           │  │
│  ├─────────────┤  ├─────────────┤  ├─────────────────────────┤  │
│  │ • Agent CLI │  │ • -ngl 99   │  │ • Cross-vendor kernels  │  │
│  │ • MTP auto  │  │ • FlashAttn │  │ • Pythonic ergonomics   │  │
│  │ • Gemma 4   │  │ • KV q4_0   │  │ • AMD > ROCm potential  │  │
│  │ • Pin local │  │ • MTP draft │  │ • Qualcomm-backed       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│         │               │                      │                 │
│         └───────────────┼──────────────────────┘                 │
│                         ▼                                        │
│              ┌─────────────────────┐                             │
│              │    ModelGateway     │                             │
│              │  (routes to best    │                             │
│              │   local backend)    │                             │
│              └─────────────────────┘                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Immediate Actions (This Sprint)

| Action | Owner | Dependency |
|--------|-------|------------|
| Add `CLAUDE_CODE_ATTRIBUTION_HEADER=0` to OpenCode launch scripts | P3/Engineering | None |
| Pin Ollama to local-only mode in provider config | P3/Engineering | C-5 routing |
| Integrate llama-optimus as `make benchmark-optimize` target | P3/Engineering | llama.cpp build |
| Prototype Mojo kernel for RMSNorm → Vulkan SPIR-V | Researcher | Mojo SDK access |
| Add Vulkan backend detection to ModelGateway | P3/Engineering | llama.cpp vulkan build |

---

## Proposals Generated

| Proposal ID | Title | Status |
|-------------|-------|--------|
| **PROP-RP03-001** | Ollama 0.32 Local-Only Mode Enforcement | 🟡 READY FOR REVIEW |
| **PROP-RP03-002** | llama.cpp Optimization Config Presets (Fable-5 derived) | 🟡 READY FOR REVIEW |
| **PROP-RP03-003** | `CLAUDE_CODE_ATTRIBUTION_HEADER=0` Default for All Agents | 🟡 READY FOR REVIEW |
| **PROP-RP03-004** | llama-optimus Integration in Benchmark Suite | 🟡 READY FOR REVIEW |
| **PROP-RP03-005** | Mojo + Vulkan R&D Spike (Kernel Port) | 🟡 READY FOR REVIEW |
| **PROP-RP03-006** | Vulkan Backend Auto-Detection in ModelGateway | 🟡 READY FOR REVIEW |

---

## L3 Universal Principles Extracted

1. **AI-Optimizing-AI Beats Human Tuning** — Fable 5 found flag combinations humans missed. Automate optimization (llama-optimus) and verify.

2. **Prompt Stability = Cache Efficiency** — Changing system prompt prefixes (attribution headers) destroys KV cache reuse. Fix at agent harness level.

3. **Vendor-Neutral Compute > Vendor-Locked Performance** — Vulkan + Mojo enables AMD/Intel/Apple parity. 5-10% CUDA advantage not worth lock-in.

4. **Auto-Tuning > Static Configs** — Ollama's MTP auto-tuning, llama-optimus Optuna search, Fable's iterative profiling — all beat static flags.

---

*⬡ OMEGA ⬡ SOVEREIGN-RESEARCHER ⬡ laguna-s-2.1-free ⬡ opencode ⬡ trc_research ⬡ RP-03-COMPLETE*
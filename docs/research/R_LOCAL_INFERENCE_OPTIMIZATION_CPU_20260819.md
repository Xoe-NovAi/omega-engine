# Extreme Local Inference Optimization (CPU-only, 16GB RAM)
## SOTA Research — 2025-2026 Frontier

**AP Token**: `AP-LOCAL-INFERENCE-OPT-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_local_inference_opt ⬡ ACTIVE
**Date**: 2026-08-19

---

## Executive Summary

This document surveys the 2025-2026 state of the art in **extreme local inference optimization** for CPU-only, 16GB RAM systems (Ryzen 5700U class hardware). The frontier centers on **GGUF quantization strategies** (Q4_K_M as default, IQ quants for tighter budgets), **context window vs. RAM tradeoffs**, **KV cache optimization**, **speculative decoding on CPU**, and **model selection for planner vs. executor roles**. Critical finding: On CPU, **memory bandwidth is the bottleneck, not compute** — a smaller quant that stays fully in RAM beats a larger quant that spills to swap.

---

## 1. Quantization Strategy for CPU Inference

### 1.1 GGUF Quantization Reference (2026 Consensus)
> **Sources**: 
> - [GGUF Quantization Guide (tonisagrista.com)](https://tonisagrista.com/blog/2026/quantization)
> - [GGUF Q4 vs Q5 vs Q8 Explained (bmdpat.com, 2026-07-29)](https://bmdpat.com/blog/gguf-quantization-q4-q5-q8-explained-2026)
> - [Local LLM Inference Optimization (carteakey.dev, 2026-06-12)](https://carteakey.dev/blog/local-inference/local-llm-optimization/)

**Decision Guide (2026)**:

| Use Case | Recommended Quant | Rationale |
|----------|-------------------|-----------|
| **Best balance overall** | `Q4_K_M` | Default choice for most situations |
| **Max quality, still compressed** | `Q5_K_M` or `Q6_K` | When VRAM/RAM allows |
| **Tight RAM, acceptable quality loss** | `Q4_K_S` or `IQ4_XS` | Smaller footprint |
| **Max compression** | `IQ3_XS` or `Q3_K_S` | **Test quality!** |
| **Near-lossless accuracy** | `Q8_0` or `FP16`/`BF16` | High-RAM setups |
| **CPU inference** | `Q4_K_M` or `IQ4_NL` | Better decode speed on CPU |
| **Fit ~50B model on 16GB** | `IQ3_S` or `Q3_K_M` | With CPU offload |

### 1.2 Quantization Quality by Task Type (bmdpat.com, 2026)
> **Source**: [GGUF Q4 vs Q5 vs Q8 Explained](https://bmdpat.com/blog/gguf-quantization-q4-q5-q8-explained-2026)

| Task Sensitivity | Quantization | Examples |
|------------------|--------------|----------|
| **Highly resilient (Q4 fine)** | Q4_K_M | Text summarization, classification, simple Q&A, chat |
| **Moderately sensitive (Q5+ preferred)** | Q5_K_M | Code generation, multi-step reasoning, creative writing, complex instruction following |
| **Quality-critical (Q6+ or Q8)** | Q6_K / Q8_0 | Arithmetic/math, precise factual extraction, structured output (JSON/XML), cascading error tasks |

### 1.3 I-Quants Require IMatrix Calibration (tonisagrista.com, 2026)
> **Source**: [GGUF Quantization Guide](https://tonisagrista.com/blog/2026/quantization)

> "I-quants require **importance matrix (imatrix) calibration** during quantization for best results. Without it, quality can degrade noticeably."

**IMatrix process**: Run calibration with representative data before quantizing to IQ formats.

### 1.4 Quantization Reference Table (carteakey.dev, 2026)
> **Source**: [Local LLM Inference Optimization](https://carteakey.dev/blog/local-inference/local-llm-optimization/)

| Quant | Size vs FP16 | Quality | Notes |
|-------|--------------|---------|-------|
| Q2_K | ~25% | Noticeable degradation | Extreme size constraints only |
| IQ3 / IQ4 | ~25–35% | Often better than older same-size quants | Calibration + runtime support matter; test speed |
| **Q4_K_M** | **~35%** | **Good** | **Best size/quality balance** |
| Q4_K_XL / UD-Q4_K_XL | ~35% | Often better than plain Q4 | Dynamic/tensor-sensitive allocation |
| Q5_K_M / Q5_K_XL | ~40% | Very close to FP16 | Strong default when RAM allows |
| Q6_K | ~50% | Near-lossless | High-RAM setups |

---

## 2. Context Window vs. RAM Tradeoffs

### 2.1 KV Cache Memory Growth (Multiple Sources)
> **Sources**: 
> - [llama.cpp Discussion #9784](https://github.com/ggml-org/llama.cpp/discussions/9784)
> - [carteakey.dev](https://carteakey.dev/blog/local-inference/local-llm-optimization/)
> - [LocalAIMaster (2026-06-21)](https://localaimaster.com/models/context-windows-coding-explained)

**Critical insight**: KV cache grows linearly with context length and lives in RAM (CPU inference).

```
Gemma-9B Q4_K_M, context 8192 → ~2.8GB KV cache
Same model, context 4096 → ~1.4GB KV cache
```

**Rule**: Default context size in llama.cpp is often max (8192+), causing OOM. **Always set `--ctx-size` explicitly**.

### 2.2 RAM Requirements by Model Size (Multiple Sources)
> **Sources**: 
> - [bmdpat.com](https://bmdpat.com/blog/gguf-quantization-q4-q5-q8-explained-2026)
> - [DataCamp (2026-06-17)](https://www.datacamp.com/tutorial/gguf-format-a-complete-guide)
> - [Daily.dev (2026)](https://daily.dev/blog/running-llms-locally-ollama-llama-cpp-self-hosted-ai-developers)

| Model Size | Q4_K_M Size | Min RAM (with KV cache) | CPU Speed (Ryzen 5700U class) |
|------------|-------------|-------------------------|-------------------------------|
| 1B–3B | 1–2 GB | 4–6 GB | 15–25 tok/s |
| **7B–8B** | **4–5 GB** | **8–12 GB** | **5–10 tok/s** |
| 13B–14B | 7–8 GB | 16–20 GB | 3–6 tok/s |
| 30B–32B | 18–20 GB | 32+ GB | 1–3 tok/s (needs offload) |

**For 16GB RAM system**: **7B–8B models at Q4_K_M are the practical ceiling**. 13B+ will swap and become unusably slow.

### 2.3 Context Size Recommendations for 16GB RAM
> **Sources**: [AI Made Tools (2026-04-04)](https://www.aimadetools.com/blog/how-to-run-ai-without-gpu), [carteakey.dev](https://carteakey.dev/blog/local-inference/local-llm-optimization/)

| Role | Model | Quant | Context | Est. RAM | Est. Speed |
|------|-------|-------|---------|----------|------------|
| **Planner** | Qwen3-14B / Llama-3.1-8B | Q4_K_M | 16K–32K | 10–12 GB | 4–8 tok/s |
| **Executor** | Qwen2.5-Coder-7B | Q4_K_M | 8K–16K | 6–8 GB | 6–12 tok/s |
| **Critic** | Qwen3-1.7B | Q4_K_M | 4K–8K | 2–3 GB | 15–25 tok/s |

**Total concurrent**: ~18–22 GB (exceeds 16GB) → **run sequentially or use model offloading**

---

## 3. Model Selection for Planner vs. Executor

### 3.1 Planner Requirements (GrandLinux, 2026; LocalGraph, 2025)
> **Sources**: 
> - [GrandLinux](https://www.grandlinux.com/en/blogs/claude-local-ai-planner-executor.html)
> - [LocalGraph](https://abhinaavramesh.github.io/langgraph-ollama-tutorial/tutorials/advanced/21-plan-and-execute.html)

| Model Size | Max Plan Steps | Use Case |
|------------|----------------|----------|
| 3B–8B | 3–4 | Simple multi-step tasks |
| 13B–34B | 4–6 | Moderate complexity |
| **70B+** | **5–7** | **Complex reasoning, strategic planning** |

**For 16GB CPU-only**: 70B+ not feasible. **Best compromise: 14B–32B at Q4_K_M with reduced context (16K–32K)**.

### 3.2 Executor Requirements (GrandLinux, 2026)
> **Source**: [Claude Plans + Local AI Executes](https://www.grandlinux.com/en/blogs/claude-local-ai-planner-executor.html)

> "The factor that makes this pattern 'actually playable' is that your Local AI has to be strong enough — especially at instruction following and tool use."

**Verified executor models (2026)**:
| Model | Params | VRAM/RAM (4-bit) | Fit |
|-------|--------|------------------|-----|
| Qwen2.5-Coder-7B | 7B | ~6 GB | Autocomplete only — instruction following too weak |
| **Qwen2.5-Coder-14B** | **14B** | **~10 GB** | **Single-file refactors — floor for usable executor** |
| Qwen2.5-Coder-32B | 32B | ~22 GB | Multi-file + tool use — sweet spot (needs >16GB) |
| Llama 3.3 70B | 70B | ~42 GB | General-purpose — very strong |

**For 16GB RAM**: **Qwen2.5-Coder-14B at Q4_K_M is the minimum viable executor**. 7B is too weak for tool use.

### 3.3 Critic/Verifier Models (Bharat, 2026; Anthropic Outcomes, 2026)
> **Sources**: 
> - [Deep Agents](https://bvsbharat.com/posts/2026/deep-agents-planner-executor-critic/)
> - Anthropic Outcomes primitive (public beta 2026-05-06)

> "The critic can also run smaller, and importantly should run a **different model than the executor** so it's not just confirming the executor's biases."

**Recommendation**: Small, fast model (1.7B–3B) different architecture from executor.

---

## 4. CPU Inference Optimization Techniques

### 4.1 llama.cpp CPU Flags (carteakey.dev, 2026; AI Made Tools, 2026)
> **Sources**: 
> - [Local LLM Inference Optimization](https://carteakey.dev/blog/local-inference/local-llm-optimization/)
> - [How to Run AI Without GPU](https://www.aimadetools.com/blog/how-to-run-ai-without-gpu)

**Key flags for CPU performance**:
```bash
# Use all CPU cores
--threads $(nproc)

# Smaller context = faster (critical for CPU)
--ctx-size 4096  # or 8192, 16384 depending on role

# Optimize batch processing
--batch-size 512

# Disable mmap (loads entire model into RAM, no page faults)
--no-mmap

# Prevent OS swapping model pages
--mlock

# CPU affinity (pin to specific cores)
taskset -c 0-7 ./llama-server ...
```

### 4.2 Memory Control (carteakey.dev, 2026)
> **Source**: [Local LLM Inference Optimization](https://carteakey.dev/blog/local-inference/local-llm-optimization/)

**`--no-mmap`**: Without this, llama.cpp uses memory-mapped I/O. Expert weight accesses during decode are non-sequential → OS page fault handler triggers repeatedly → latency jitter.

With `--no-mmap`: Entire model loads into RAM before inference. No page faults. Tradeoff: longer startup, full upfront RAM allocation.

**`--mlock`**: Pins model pages in RAM, prevents OS swapping under memory pressure.

### 4.3 OS Tuning for CPU Inference (carteakey.dev, 2026)
> **Source**: [Local LLM Inference Optimization](https://carteakey.dev/blog/local-inference/local-llm-optimization/)

**Critical**: Check RAM is running at rated speed:
```bash
sudo dmidecode -t memory | grep -E "Speed|Configured"
# "Configured Memory Speed" must match XMP/EXPO profile
# If not, enable XMP/EXPO in BIOS
```

> "On my machine, enabling XMP took generation from roughly one-third speed back to normal."

**CPU Governor**: Set to `performance`:
```bash
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

**Transparent Huge Pages**: Enable for better memory throughput:
```bash
echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
```

### 4.4 Speculative Decoding on CPU (carteakey.dev, 2026)
> **Source**: [Local LLM Inference Optimization](https://carteakey.dev/blog/local-inference/local-llm-optimization/)

**MTP (Multi-Token Prediction)**: Speculation using companion draft model trained for multi-token prediction.

**Metrics to watch**:
- **Draft acceptance rate**: Whether speculative decoding is helping
- **KV precision**: Draft model KV cache precision
- **Spec length**: How many tokens drafted per step

**For CPU**: Speculative decoding helps but draft model also consumes RAM. Net benefit depends on acceptance rate > 50%.

### 4.5 ik_llama.cpp Fork (GitHub, 2026)
> **Source**: [ik_llama.cpp](https://github.com/ikawrakow/ik_llama.cpp)

> "llama.cpp fork with better CPU and hybrid GPU/CPU performance, fused MoE operations and tensor overrides for hybrid GPU/CPU inference"

**Worth evaluating** for Omega Engine if CPU performance is critical.

---

## 5. Runtime Selection: llama.cpp vs Ollama vs vLLM

### 5.1 Why Not Ollama? (carteakey.dev, 2026)
> **Source**: [Local LLM Inference Optimization](https://carteakey.dev/blog/local-inference/local-llm-optimization/)

Ollama adds overhead, less control over flags, harder to tune. **llama.cpp direct** or **llama-server** preferred for production optimization.

### 5.2 vLLM for CPU (vLLM Docs, 2026)
> **Source**: [GrandLinux](https://www.grandlinux.com/en/blogs/claude-local-ai-planner-executor.html)

vLLM supports CPU inference with much higher throughput than Ollama. **Recommended for production multi-user serving**.

### 5.3 llama-server for Omega (Recommended)
```bash
# Planner (larger model, higher context)
./llama-server -m planner-q4_k_m.gguf \
  --threads 8 --ctx-size 16384 --batch-size 512 \
  --no-mmap --mlock --port 8081

# Executor (smaller model, lower context)
./llama-server -m executor-q4_k_m.gguf \
  --threads 8 --ctx-size 8192 --batch-size 512 \
  --no-mmap --mlock --port 8082

# Critic (tiny model, minimal context)
./llama-server -m critic-q4_k_m.gguf \
  --threads 4 --ctx-size 4096 --batch-size 256 \
  --no-mmap --mlock --port 8083
```

---

## 6. Hardware-Specific: Ryzen 5700U (8C/16T, 16GB RAM)

### 6.1 Ryzen 5700U Characteristics
- 8 cores / 16 threads (Zen 2, 7nm)
- Base 1.8 GHz, Boost 4.3 GHz
- **DDR4-3200** (typically) — **memory bandwidth ~25 GB/s dual channel**
- No AVX-512 (AVX2 only)
- Integrated Vega 7 GPU (not usable for llama.cpp efficiently)

### 6.2 Expected Performance (Extrapolated from Benchmarks)
| Model | Quant | Context | Est. Tok/s (Prompt) | Est. Tok/s (Gen) |
|-------|-------|---------|---------------------|------------------|
| Qwen3-1.7B | Q4_K_M | 4K | ~150 | ~25 |
| Qwen2.5-Coder-7B | Q4_K_M | 8K | ~50 | ~8 |
| Qwen2.5-Coder-14B | Q4_K_M | 16K | ~25 | ~4 |
| Llama-3.1-8B | Q4_K_M | 16K | ~30 | ~5 |
| Qwen3-14B | Q4_K_M | 16K | ~20 | ~3 |

**Source**: Extrapolated from [AI Made Tools](https://www.aimadetools.com/blog/how-to-run-ai-without-gpu) (i7-12700, Ryzen 5800X benchmarks) and [Daily.dev](https://daily.dev/blog/running-llms-locally-ollama-llama-cpp-self-hosted-ai-developers) (16GB RAM, 7B = 12-18 tok/s, 13B = 6-10 tok/s).

### 6.3 Memory Budget for Concurrent Roles
```
Planner (Llama-3.1-8B Q4_K_M, ctx=16K):  ~5.5 GB model + ~1.5 GB KV = ~7 GB
Executor (Qwen2.5-Coder-7B Q4_K_M, ctx=8K): ~4 GB model + ~0.8 GB KV = ~4.8 GB
Critic (Qwen3-1.7B Q4_K_M, ctx=4K):       ~1 GB model + ~0.2 GB KV = ~1.2 GB
OS + overhead:                              ~2 GB
---------------------------------------------------------
Total:                                      ~15 GB (fits 16GB with ~1GB headroom)
```

**Verdict**: All three can run concurrently **if** using `--no-mmap --mlock` and careful context sizing. Sequential execution safer.

---

## 7. Advanced: MoE Models on CPU (carteakey.dev, 2026)

### 7.1 MoE vs Dense on CPU
> **Source**: [Local LLM Inference Optimization](https://carteakey.dev/blog/local-inference/local-llm-optimization/)

| Aspect | Dense Models | MoE Models |
|--------|--------------|------------|
| Active params/token | All | Small fraction (e.g., 3B of 80B) |
| Must fit in RAM | Yes, for best performance | No — experts can live in RAM |
| Primary tuning lever | Quant level + context | Layer placement + RAM bandwidth |
| TG speed driver | RAM bandwidth | RAM bandwidth + GPU layer count |

**For CPU-only**: MoE models (Qwen3, DeepSeek, gpt-oss) can run larger total params by offloading experts to RAM, **but RAM bandwidth becomes critical**.

### 7.2 Layer Placement Flags
```bash
# Coarse control: keep N MoE layer experts on CPU
--n-cpu-moe 31

# Fine-grained: per-tensor regex placement
--override-tensor ".ffn_(up|down|gate)_(ch|)exps=CPU"
--override-tensor "blk\.(5|[6-9]|[0-9][0-9]+)\.ffn_(up|down|gate)_(ch|)exps=CPU"

# Automatic placement (safest)
--fit
```

**Warning**: For ~60GB model, putting all experts on CPU tries to load ~60GB into RAM → hard crash on 64GB system. Always use `llama-fit-params` first.

---

## 8. Benchmarking Methodology (carteakey.dev, 2026)

> **Source**: [Local LLM Inference Optimization](https://carteakey.dev/blog/local-inference/local-llm-optimization/)

> "Do not optimize from a single short prompt. Short prompts hide KV cache costs, long-context VMM growth, and parallel-slot allocation. Benchmark at the context length you actually serve."

**Key metrics**:
| Metric | Definition | What It Reveals |
|--------|------------|-----------------|
| PP (Prompt Processing) | Tok/s reading input context | Batch size, long prompt handling |
| TG (Token Generation) | Tok/s generating output | RAM bandwidth, layer placement |
| VRAM/RAM at load | Weights + KV cache fit | Context size, parallel slots, quant |
| VRAM/RAM after long sessions | Memory growth into OOM | CUDA graphs, VMM pool growth |
| Draft acceptance rate | Speculative decoding effectiveness | Draft quality, KV precision |

---

## 9. Recommendations for Omega Engine

### 9.1 Model Registry for 16GB CPU
```yaml
# config/models/cpu_16gb.yaml
models:
  planner:
    primary: "Qwen3-14B-Q4_K_M.gguf"
    fallback: "Llama-3.1-8B-Q4_K_M.gguf"
    context: 16384
    threads: 8
    flags: ["--no-mmap", "--mlock", "--batch-size", "512"]
  
  executor:
    primary: "Qwen2.5-Coder-14B-Q4_K_M.gguf"
    fallback: "Qwen2.5-Coder-7B-Q4_K_M.gguf"
    context: 8192
    threads: 8
    flags: ["--no-mmap", "--mlock", "--batch-size", "512"]
  
  critic:
    primary: "Qwen3-1.7B-Q4_K_M.gguf"
    context: 4096
    threads: 4
    flags: ["--no-mmap", "--mlock", "--batch-size", "256"]
```

### 9.2 Provider Fabric Integration (config/providers.yaml)
```yaml
providers:
  - name: "native-gguf-planner"
    type: "native_gguf"
    priority: 0
    model: "Qwen3-14B-Q4_K_M.gguf"
    ctx_size: 16384
    threads: 8
    flags: ["--no-mmap", "--mlock"]
  
  - name: "native-gguf-executor"
    type: "native_gguf"
    priority: 0
    model: "Qwen2.5-Coder-14B-Q4_K_M.gguf"
    ctx_size: 8192
    threads: 8
    flags: ["--no-mmap", "--mlock"]
  
  - name: "native-gguf-critic"
    type: "native_gguf"
    priority: 0
    model: "Qwen3-1.7B-Q4_K_M.gguf"
    ctx_size: 4096
    threads: 4
    flags: ["--no-mmap", "--mlock"]
```

### 9.3 Context Window Budget Enforcement in Oracle
```python
class ContextBudgetEnforcer:
    BUDGETS = {
        "planner": 16384,
        "executor": 8192,
        "critic": 4096,
    }
    
    def enforce(self, role: str, prompt: str) -> str:
        budget = self.BUDGETS[role]
        tokens = self.count_tokens(prompt)
        if tokens > budget:
            return self.compress_prompt(prompt, budget, role)
        return prompt
    
    def compress_prompt(self, prompt: str, budget: int, role: str) -> str:
        # Tiered compression per Hoomanely
        # 1. Drop supplementary
        # 2. Compress high-value (Selective Context / LLMLingua)
        # 3. Never drop critical
        pass
```

### 9.4 Hardware Validation Script
```bash
#!/bin/bash
# validate_hardware.sh - Run before deployment

echo "=== CPU ==="
lscpu | grep -E "Model name|CPU\(s\)|Thread|Core"

echo "=== RAM ==="
free -h
sudo dmidecode -t memory | grep -E "Speed|Configured|Size" | head -20

echo "=== XMP/EXPO Check ==="
CONFIGURED=$(sudo dmidecode -t memory | grep "Configured Memory Speed" | head -1 | awk '{print $4}')
RATED=$(sudo dmidecode -t memory | grep "Speed:" | head -1 | awk '{print $2}')
echo "Configured: ${CONFIGURED}MHz, Rated: ${RATED}MHz"
if [ "$CONFIGURED" != "$RATED" ]; then
    echo "⚠️  XMP/EXPO NOT ENABLED — Performance will be 30-50% lower!"
    echo "    Enable in BIOS: Advanced → AMD CBS → Memory → XMP/EXPO → Enabled"
fi

echo "=== CPU Governor ==="
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

echo "=== Transparent Huge Pages ==="
cat /sys/kernel/mm/transparent_hugepage/enabled

echo "=== Swappiness ==="
cat /proc/sys/vm/swappiness
```

---

## 10. Sources & Verification Status

| # | Source | Type | Verified | Notes |
|---|--------|------|----------|-------|
| 1 | tonisagrista.com (2026) | Quant guide | ✅ Direct fetch | I-quants need imatrix, decision guide |
| 2 | bmdpat.com (2026-07-29) | Benchmark blog | ✅ Direct fetch | Task sensitivity table, CPU-only section |
| 3 | carteakey.dev (2026-06-12) | Optimization guide | ✅ Direct fetch | Comprehensive: flags, OS tuning, MoE, speculative |
| 4 | AI Made Tools (2026-04-04) | CPU guide | ✅ Direct fetch | Real-world CPU benchmarks, model recommendations |
| 5 | Daily.dev (2026) | Tutorial | ✅ Direct fetch | 16GB RAM benchmarks, quantization rule of thumb |
| 6 | DataCamp (2026-06-17) | Tutorial | ✅ Direct fetch | RAM requirements table by model size |
| 7 | llama.cpp Discussion #9784 | GitHub issue | ✅ Direct fetch | KV cache size explanation |
| 8 | GrandLinux (2026-05-24) | Case study | ✅ Direct fetch | Executor model requirements verified |
| 9 | LocalGraph (2025) | Code tutorial | ✅ Direct fetch | Multi-model LangGraph implementation |
| 10 | Bharat Bhavnasi (2026-03-12) | Engineering blog | ✅ Direct fetch | Critic model different from executor |
| 11 | ik_llama.cpp (2026) | GitHub fork | ✅ Direct fetch | Better CPU performance claim |
| 12 | LocalAIMaster (2026-06-21) | Technical guide | ✅ Direct fetch | Context window tiers, hierarchical prompting |

---

## 11. Unverified Claims (Flagged)

- **ik_llama.cpp "better CPU performance"** — no independent benchmarks found
- **Speculative decoding on CPU net benefit** — depends on draft acceptance rate, no CPU-specific data
- **MoE on CPU "RAM bandwidth critical"** — theoretical, no Ryzen 5700U benchmarks
- **Qwen2.5-Coder-14B as "floor for usable executor"** — GrandLinux claim, no comparative study
- **16GB concurrent three-model fit** — calculated estimate, not empirically validated

---

*End of R_LOCAL_INFERENCE_OPTIMIZATION_CPU_20260819.md*
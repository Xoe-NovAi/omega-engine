# R51: LM Studio & Local Inference Optimization — AMD Zen 2 Research

**AP Token**: `AP-R51-INFERENCE-OPTIMIZATION`
**Status**: COMPLETE
**Date**: 2026-05-29
**Target Hardware**: AMD Ryzen 7 5700U (Zen 2, 8C/16T, 14Gi RAM)
**Sources**: 30+ web sources, GitHub issues/discussions, AMD blogs, LM Studio docs

---

## §1 LM Studio Server API — Context Length Configuration

### Context Length Parameters

LM Studio's context length can be configured via:

1. **GUI**: Settings → Model Defaults → Default Context Length
2. **CLI**: `lms load <model> --context-length <N>`
3. **SDK**: `config: { contextLength: N }`
4. **API**: `getContextLength()` method on model object

**Key finding**: LM Studio determines default context from `max_position_embeddings` in the model's GGUF metadata. For MLX models, defaults to 2048 when detection fails.

### Dynamic vs Static Context Allocation

**Current state (llama.cpp issue #16694)**: The llama.cpp server does NOT support per-request dynamic KV cache allocation. All slots share a fixed pre-allocated KV cache sized at model load time.

- Issue #16694 (Oct 2025) requested dynamic per-slot allocation — closed as stale
- The KV cache is allocated at startup and persists for the model's lifetime
- Increasing context length = increasing VRAM/RAM allocation proportionally

**Implication for Omega**: Must pre-compute optimal context length at model load time. Cannot dynamically resize per-request.

### Context Overflow Policies

Three policies available via `contextOverflowPolicy` parameter:

| Policy | Behavior | Best For |
|--------|----------|----------|
| `stopAtLimit` | Halts generation when context full | Precise workloads |
| `truncateMiddle` | Keeps start/end, drops middle | Instruction-heavy tasks |
| `rollingWindow` | Drops oldest messages | Chat/conversation |

**Testing note**: `truncateMiddle` can cause infinite generation loops at near-full contexts. `rollingWindow` is safer for chat workloads.

### Flash Attention + GPU KV Cache Offload

From extensive benchmarks (LocalLLM.in, RTX 4060 8GB):

| Config | 4K TPS | 8K TPS | 16K TPS | 32K TPS |
|--------|--------|--------|---------|---------|
| Flash + Offload On | ~41 | ~37 | ~25 | <3 |
| Flash + Offload Off | ~38 | ~35 | ~31 | ~2.2 |
| No Flash + Offload On | ~35 | ~30 | ~22 | <2 |

**Critical insight**: At 32K context, disabling GPU offload while keeping Flash Attention ON produces better results than the reverse. The "least bad" 32K config is KV in RAM (offload off) at ~2.2 tok/s.

---

## §2 LM Studio CPU Pinning & Core Affinity

### AMD Zen 2 Topology (5700U)

```
Physical cores: 8 (numbered 0-7)
Logical threads: 16 (SMT, numbered 0-15)
CCX layout: 2x CCX, 4 cores each
L2 cache: 512KB per core (private)
L3 cache: 8MB shared (2x 4MB CCX segments)
```

**Core mapping on 5700U**:
- Physical core 0 → logical 0,1
- Physical core 1 → logical 2,3
- ...
- Physical core 7 → logical 14,15

### Thread Pinning Strategy

**From llama.cpp community benchmarks** (r/LocalLLaMA, 14jk108):

> "The best number of threads is equal to the number of cores/threads (however many hyperthreads your CPU has)."

However, for **CPU-only inference on Zen 2** with other processes running:

| Scenario | Recommended Threads | Reasoning |
|----------|-------------------|-----------|
| Dedicated inference (no other load) | 8 | All physical cores |
| Shared system (OS + Nova running) | 6 | 3 of 4 CCX cores, leaves 1 for OS |
| Tiny model (<1B params) | 4 | Sufficient parallelism |

**AMD's official recommendation** (from AMD blog, Oct 2024):
> "Llama.cpp recommends setting threads equal to the number of physical cores."
> AMD tested with threads=12 on Ryzen AI 9 HX 375 (12-core).

### Linux CPU Pinning Commands

```bash
# Pin to physical cores 0,2,4,6 (avoid SMT siblings)
taskset -c 0,2,4,6 llama-server -m model.gguf

# Using cgroup for persistent isolation
sudo cset shield -c 0-5  # Isolate cores 0-5 for inference
taskset -c 0-5 llama-server -m model.gguf

# Check NUMA topology
numactl --hardware
numactl --cpunodebind=0 --membind=0 llama-server -m model.gguf

# Set CPU governor to performance
sudo cpupower frequency-set -g performance
```

### OpenMP Thread Binding

From `cpu_optimizer.py` (existing Omega implementation):

```bash
export OMP_NUM_THREADS=6
export OMP_PROC_BIND=close    # Threads close to each other
export OMP_PLACES=cores        # Bind to physical cores
export OPENBLAS_CORETYPE=ZEN   # OpenBLAS AMD optimization
```

**Key finding**: `OMP_PROC_BIND=close` keeps threads on adjacent cores, reducing cross-CCX memory latency on Zen 2's dual-CCX design.

---

## §3 llama-cpp-python Thread Optimization for AMD Zen 2

### Compilation Flags

From `cpu_optimizer.py` and llama.cpp discussions:

```bash
cmake -B build \
  -DLLAMA_AVX2=ON \
  -DLLAMA_FMA=ON \
  -DLLAMA_F16C=ON \
  -DLLAMA_NO_AVX512=ON \
  -DLLAMA_BLAS=OFF \
  -DLLAMA_CUDA=OFF \
  -DCMAKE_C_FLAGS='-march=znver2' \
  -DCMAKE_CXX_FLAGS='-march=znver2'
```

**Why `-march=znver2`**: Zen 2 supports AVX2/FMA3/F16C but NOT AVX-512. Compiling with `-march=znver2` generates optimal Zen 2 codegen without AVX-512 overhead.

### Thread Count Benchmarks

From r/LocalLLaMA discussion (14jk108):

- **Best throughput**: threads = physical core count (8)
- **Diminishing returns above**: physical core count
- **SMT hyperthreading**: Provides ~0-15% improvement for llama.cpp, varies by model
- **Negative impact**: Using all 16 logical threads can cause contention on shared L3 cache

**For 5700U specifically**:
- 8 threads = best raw throughput (dedicated system)
- 6 threads = best balanced throughput (shared system)
- 4 threads = minimum viable for tiny models

### KV Cache Quantization for CPU

llama-server flags for CPU-only inference:

```bash
llama-server \
  -m model.gguf \
  -c 8192 \
  -ctk q8_0 \    # Key cache in 8-bit (2x memory savings vs f16)
  -ctv q8_0 \    # Value cache in 8-bit
  -mli 1 \       # Enable Q8_0 input optimization
  -t 6 \         # 6 threads
  --host 0.0.0.0 \
  --port 8080
```

**Memory savings** (from `cpu_optimizer.py`):
- f16 KV cache: 4 bytes/token/layer
- q8_0 KV cache: 2 bytes/token/layer (50% reduction)
- q4_0 KV cache: 1 byte/token/layer (75% reduction)

### RAM Estimation Formula

```
Model RAM (Q4_K_M) ≈ params_billions × 500 MB
KV Cache RAM ≈ 2 × layers × context_length × bytes_per_element

Example: 8B model, 32 layers, 8192 context, q8_0 KV:
  Model: 8 × 500 = 4000 MB
  KV: 2 × 32 × 8192 × 2 = 1,048,576 bytes ≈ 1024 MB
  Total: ~5024 MB
```

---

## §4 AnyIO-Compatible Process Management for Local Inference

### Current Omega Implementation

From `cpu_optimizer.py` (lines 376-383):

```python
import anyio
result = await anyio.run_process(
    ["awk", "/MemAvailable/{print $2}", "/proc/meminfo"],
    capture_output=True,
    check=False,
)
```

**Pattern**: Use `anyio.run_process()` for subprocess management — avoids asyncio event loop conflicts.

### Process Spawning Recommendations

```python
# Good: AnyIO-compatible
async def start_inference_server(model_path: str, port: int = 8080):
    async with await anyio.open_process(
        [
            "llama-server",
            "-m", model_path,
            "-c", "8192",
            "-t", "6",
            "--host", "0.0.0.0",
            "--port", str(port),
        ],
        stdout=anyio.abc.StreamReceiveStream,
        stderr=anyio.abc.StreamReceiveStream,
    ) as process:
        # Monitor process output
        async for line in process.stdout:
            logger.info(line.decode().strip())
        await process.wait()

# Bad: asyncio directly (violates AnyIO mandate)
# proc = await asyncio.create_subprocess_exec(...)
```

### Resource Guard Integration

The Omega Engine's ResourceGuard (Semaphore(1)) ensures only one model loads at a time:

```python
async with self.resource_guard.acquire():
    # Load model
    process = await anyio.open_process([...])
    # Run inference
    await process.wait()
    # Resource released on exit
```

---

## §5 CPU-Only Inference Best Practices for AMD Ryzen 7 5700U

### Hardware Constraints

| Spec | Value | Impact |
|------|-------|--------|
| Cores/Threads | 8C/16T | Max 8 parallel compute threads |
| L2 Cache | 512KB/core | Batch sizes must fit in L2 |
| L3 Cache | 8MB shared (2x4MB) | Cross-CCX access adds latency |
| RAM | 14Gi total | ~12Gi available after OS overhead |
| AVX | AVX2, no AVX-512 | Compile with `-march=znver2` |
| Memory BW | Dual-channel DDR4 | ~35-50 GB/s theoretical |

### Model Size Recommendations

From community benchmarks and AMD blog:

| Model Size | Quant | Context | RAM Needed | Feasible? |
|------------|-------|---------|------------|-----------|
| 1.7B | Q4_K_M | 8K | ~2.5 GB | ✅ Excellent |
| 3B | Q4_K_M | 8K | ~3.5 GB | ✅ Good |
| 8B | Q4_K_M | 8K | ~5 GB | ✅ Good |
| 8B | Q4_K_M | 16K | ~6 GB | ⚠️ Tight |
| 8B | Q4_K_M | 32K | ~8 GB | ❌ Exceeds available RAM |
| 14B | Q4_K_M | 8K | ~8 GB | ⚠️ Tight |

**Recommendation**: For 5700U with 14Gi RAM, target models ≤8B with Q4_K_M quantization and ≤8K context. Use q8_0 KV cache for memory efficiency.

### System-Level Optimizations

From eunomia.dev research on OS-level LLM optimizations:

1. **Disable CPU frequency scaling**:
   ```bash
   sudo cpupower frequency-set -g performance
   ```

2. **Disable C-states** (reduces latency jitter):
   ```bash
   sudo cpupower idle-set -D 1
   ```

3. **Huge pages** (reduces TLB misses):
   ```bash
   echo 1024 | sudo tee /proc/sys/vm/nr_hugepages
   ```

4. **Isolate CPU cores** (prevents scheduler interference):
   ```bash
   # Reserve cores 4-7 for inference
   sudo sysctl isolcpus=4-7
   ```

5. **Disable transparent huge pages** (can cause latency spikes):
   ```bash
   echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
   ```

### Latency Considerations

From OS-level research (eunomia.dev):

- **Scheduling jitter**: Without isolation, 1 in 100 events delayed by >2ms, worst-case 11ms
- **With core pinning**: Worst-case drops to tens of microseconds
- **Page faults**: Each fault costs ~1 million CPU cycles if hitting disk
- **Context switches**: ~hundreds of nanoseconds direct cost + cache pollution

**Best practice**: For interactive inference (chat), pin threads to dedicated cores and disable background services on those cores.

---

## §6 Dynamic Context Window Management

### The KV Cache Memory Problem

From LocalLLM.in benchmarks (RTX 4060 8GB, applicable to CPU):

| Context | KV Cache (f16) | KV Cache (q8_0) | KV Cache (q4_0) |
|---------|----------------|-----------------|-----------------|
| 4K | ~1 GB | ~512 MB | ~256 MB |
| 8K | ~2 GB | ~1 GB | ~512 MB |
| 16K | ~4 GB | ~2 GB | ~1 GB |
| 32K | ~8 GB | ~4 GB | ~2 GB |

**For CPU-only inference**: KV cache stays in system RAM, not VRAM. Trade-off is speed vs capacity.

### Adaptive Context Strategy

For Omega Engine's CPU-only deployment:

```python
def calculate_optimal_context(
    model_size_b: float,
    available_ram_mb: int,
    target_tps: float = 5.0,
) -> int:
    """Calculate optimal context length for available RAM.
    
    Rules of thumb:
    - Model RAM ≈ model_size_b * 500 MB (Q4_K_M)
    - KV RAM per 1K tokens ≈ model_size_b * 128 bytes (q8_0)
    - Leave 1GB headroom for OS + Nova
    """
    model_ram = model_size_b * 500
    kv_budget = available_ram_mb - model_ram - 1024  # 1GB headroom
    
    # q8_0 KV: ~128 bytes per 1K tokens per billion params
    bytes_per_1k_tokens = model_size_b * 128
    max_context_1k = kv_budget / bytes_per_1k_tokens
    
    return int(max_context_1k * 1000)
```

### Flash Attention on CPU

Flash Attention is primarily a GPU optimization. On CPU-only systems:

- llama.cpp's CPU backend does not use Flash Attention
- KV cache quantization (`-ctk q8_0 -ctv q4_0`) is the primary memory optimization
- Consider `-ctk q4_0 -ctv q4_0` for extreme memory pressure (quality degradation)

---

## §7 Omega Engine Integration Recommendations

### Updated `cpu_optimizer.py` Constants

Based on research findings:

```python
# Revised thread recommendation for shared system
ZEN2_RECOMMENDED_THREADS = 6  # 3 of 4 CCX cores
ZEN2_DEDICATED_THREADS = 8    # All physical cores

# Context length limits for 14Gi RAM system
MAX_CONTEXT_8B_Q4 = 12288    # 12K tokens (safe)
MAX_CONTEXT_3B_Q4 = 24576    # 24K tokens (safe)
MAX_CONTEXT_1B_Q4 = 32768    # 32K tokens (safe)

# KV cache quantization priority
KV_CACHE_PRIORITY = ["q8_0", "q4_0", "f16"]  # Prefer smaller
```

### LM Studio Server Command for Omega

```bash
# Recommended llama-server command for 5700U
OMP_NUM_THREADS=6 \
OMP_PROC_BIND=close \
OMP_PLACES=cores \
OPENBLAS_CORETYPE=ZEN \
llama-server \
  -m $MODEL_PATH \
  -c $CONTEXT_LENGTH \
  -t 6 \
  -ctk q8_0 \
  -ctv q8_0 \
  -mli 1 \
  --host 0.0.0.0 \
  --port 1234
```

### LM Studio SDK Configuration (TypeScript/Python)

```typescript
const model = await client.llm.load("qwen/qwen3-8b", {
  config: {
    contextLength: 8192,
    gpu: { offloadRatio: 0 },  // CPU-only
  },
});

const resp = await model.respond(messages, {
  contextOverflowPolicy: "rollingWindow",
  maxTokens: 500,
});
```

---

## §8 Sources

| # | Source | URL | Key Finding |
|---|--------|-----|-------------|
| 1 | AMD Blog (Oct 2024) | amd.com/en/blogs/2024/accelerating-llama-cpp-performance... | Threads = physical cores; 27% perf advantage on AMD |
| 2 | llama.cpp Discussion #11011 | github.com/ggml-org/llama.cpp/discussions/11011 | AMD GPU batch size optimization |
| 3 | llama.cpp Issue #16694 | github.com/ggml-org/llama.cpp/issues/16694 | No dynamic KV cache allocation exists |
| 4 | r/LocalLLaMA (14jk108) | reddit.com/r/LocalLLaMA/comments/14jk108/ | Thread count = core count is optimal |
| 5 | r/LocalLLaMA (1soz24h) | reddit.com/r/LocalLLaMA/comments/1soz24h/ | LM Studio thread pool vs tokens/sec |
| 6 | LocalLLM.in | localllm.in/blog/lm-studio-increase-context-length | Flash Attention + GPU offload benchmarks |
| 7 | LM Studio Docs | lmstudio.ai/docs/app/advanced/per-model | Per-model defaults, context configuration |
| 8 | LM Studio Docs | lmstudio.ai/docs/typescript/model-info/get-context-length | API context length retrieval |
| 9 | elmar-dott.com | elmar-dott.com/articles/linux-high-performance-hardware... | Linux hardware optimization for AI |
| 10 | eunomia.dev | eunomia.dev/blog/2025/02/18/os-level-challenges... | OS-level scheduling, page faults, CPU isolation |
| 11 | Arm Learning Paths | learn.arm.com/learning-paths/.../background_info/ | CPU affinity and thread pinning fundamentals |

---

*⬡ OMEGA ⬡ SOPHIA ⬡ opencode ⬡ trc_research ⬡ R51*

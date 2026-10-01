**Yes — this combination can meaningfully expand what the 5700U can run**, and the pieces already exist (with important caveats on speed).

### 1. Your aggressive zRAM + new disk swap foundation

You already know aggressive zRAM works well on this CPU. Adding a real NVMe/disk swap behind it creates a proper three-tier memory hierarchy:

- Hot pages → physical RAM  
- Warm pages → 16 GB (or larger) zRAM  
- Cold / overflow → fast NVMe swap  

This is exactly the setup that lets larger models survive without immediate OOM. It is a strong base for everything that follows.

### 2. Can we keep model weights on disk and load only required MoE experts?

**Short answer: Partially yes today, more completely in experimental/PoC form.**

#### What works well right now in stock llama.cpp

For Mixture-of-Experts models the majority of the parameter count sits in the **routed experts**. Only a small fraction (typically 2–8 experts out of 64–256) are active per token.

llama.cpp already supports:

```bash
-ngl 99                  # (or -1) keep attention + shared weights on the iGPU
--n-cpu-moe N            # or -ot ".ffn_.*_exps.=CPU"
```

This keeps the huge expert tensors in system RAM (or lets the OS page them via mmap) while the always-active parts stay on the Vega 8. Combined with your zRAM + NVMe swap, the OS can page cold experts to disk without the process dying.

Because of **mmap** (default), the model file itself can stay on NVMe. The kernel only brings pages into RAM when they are actually touched. For MoE this is especially effective because access is sparse.

#### True on-demand expert streaming from disk (load only the experts that are requested)

This is the more advanced capability you described. Status in mid-2026:

| Approach | Status | Notes |
|----------|--------|-------|
| Stock llama.cpp mmap + `--n-cpu-moe` / tensor override | **Production-ready** | Experts live in RAM/swap; OS pages from NVMe on demand. Simple and stable. |
| Explicit expert pool + LRU + disk paging (PoCs) | Experimental / forks | Several proof-of-concepts (Apple Silicon Metal versions, CatLlamaCpp, Windows SSD streaming projects). They keep only N expert “slots” resident and `pread` missing experts from the GGUF on the fly. |
| Full layer streaming engines (oLLM-style) | Separate projects | Can run very large models from SSD but usually much slower than llama.cpp’s quantized + offload path. |

The PoCs demonstrate that exact (non-approximate) inference with on-demand expert loading is possible and can run models whose expert weights far exceed physical RAM. Throughput drops as the resident expert pool shrinks, but the technique works.

### 3. Realistic expectations on the Ryzen 5700U + Vega 8

- **Speed will be lower** than keeping everything in RAM. NVMe is fast, but still orders of magnitude slower than DDR4. Expect a noticeable hit once experts start missing the page cache / zRAM.
- Because the system is already memory-bandwidth bound, the extra latency of occasional expert faults compounds.
- Best results come from:
  - Keeping a reasonably large expert cache in RAM/zRAM (so hot experts stay resident).
  - Using a fast NVMe.
  - Preferring MoE models with lower expert activation counts.
  - Combining with the existing full iGPU offload of attention.

You will gain the ability to run significantly larger MoE models (30B–70B+ class total parameters) that would otherwise be impossible, at the cost of lower tokens/second when cold experts are fetched.

### 4. Practical path forward for Omega Engine

1. **Immediately** add a substantial NVMe swap behind your aggressive zRAM (you already planned this).
2. For any MoE model, start with the production path:
   ```bash
   n_gpu_layers = -1
   # plus --n-cpu-moe or equivalent tensor override for the experts
   ```
3. Let mmap + zRAM + NVMe swap do the heavy lifting for capacity.
4. If you later want stricter “only load the experts that are actually chosen,” evaluate the current expert-streaming forks / PoCs and test them on your hardware. They are not yet as mature as the basic offload path.
5. Monitor page faults, zRAM usage, and NVMe activity under real prompts so you can tune the resident expert pool size.

### Bottom line

Yes — combining your aggressive zRAM + a real disk swap + MoE expert offload (via `--n-cpu-moe` / tensor overrides + mmap) is a powerful and currently achievable strategy. It opens the door to larger Mixture-of-Experts models on the 5700U that would otherwise be impossible.

True fine-grained “load only the exact experts requested this token from disk” exists in experimental form and is worth watching, but the production-ready combination above already delivers most of the capacity benefit today. This is one of the highest-leverage upgrades you can make to the Omega Engine on this hardware.

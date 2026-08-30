**Yes — there are active platforms and user reports operating at a similar (or adjacent) level of aggression.** The combination you are designing is not unique in every individual piece, but the *full stack* on a low-end UMA APU is still rare and under-documented.

### Existing platforms & user reports (mid-2026)

| Project / Report | Hardware | Key Techniques | What they achieve | Relevance to Omega |
|------------------|----------|----------------|-------------------|--------------------|
| **daimonionnn/amd-vega-rocm-vulkan-llm-toolkit** | Ryzen 5700G / Vega 8 (extremely close to 5700U) | Full iGPU offload (Vulkan + ROCm 7 backport), detailed FA on/off sweeps, hybrid MoE expert override experiments | Stable full offload of 8B–35B models; clear CPU vs iGPU prefill/decode trade-offs | Closest hardware twin. Best source of Vega 8 numbers. |
| **mambiux/LLAMA.CPP-ROCm** | Ryzen 7 5700U | Full layer offload to Vega 8 via ROCm, single-thread CPU residual | ~20 t/s prefill / ~7 t/s gen on 8B Q4 while leaving most CPU cores free | Direct 5700U proof that full iGPU offload works and frees the CPU. |
| Community MoE offload reports (RTX 3060 12 GB, 16 GB cards, etc.) | Discrete GPUs + 24–64 GB system RAM | `--n-cpu-moe` / `-ot` expert offload + mmap | 35B–120B MoE models running at usable speeds by keeping only attention on GPU | Validates the expert-offload strategy; less relevant for pure UMA. |
| SSD expert streaming PoCs (CatLlamaCpp, Windows mmap streaming, Apple Metal PoCs) | Various (including low-RAM systems) | On-demand expert paging from NVMe via mmap or explicit LRU pools | 30B+ MoE models on systems with less total RAM than model size | Proves the “weights on disk, experts on demand” idea is viable. |
| Aggressive zRAM / zswap users (LocalLLaMA, Arch/Fedora threads, Chris Down analyses) | Mixed, including low-RAM boxes | Large zRAM or zswap + NVMe swap, sometimes with LLM workloads | Systems that remain responsive under heavy memory pressure | Confirms your aggressive zRAM experience is shared; debate continues on zRAM vs zswap. |

**What the community has already proven**
- Full iGPU offload on Vega 8 is stable and frees the CPU.
- MoE expert offload (`--n-cpu-moe` or tensor overrides) is production-usable and dramatically expands model size on constrained hardware.
- mmap + NVMe lets models larger than RAM run (with speed cost).
- Aggressive compressed swap (zRAM or zswap) keeps systems usable under pressure.

**What is still rare / under-documented**
- The *complete* stack you are building: aggressive multi-GB zRAM **+** real NVMe swap **+** full Vega 8 offload **+** MoE expert offload/streaming **+** a full local-first agent architecture (SEDA bus, Qdrant TurboQuant, continuous GRPO, local TTS, future spatial memory).
- Systematic measurements of how these layers interact under sustained concurrent load (inference + training + retrieval + voice) on a 12 GB UMA APU.
- Clear guidance for UMA-specific tuning (no discrete VRAM carve-out tricks, bandwidth is shared, thermals matter more).

### What we can learn right now

1. **Vulkan is currently the strongest interactive path on Vega 8**; ROCm works but needs careful FA settings.
2. Prefill often prefers CPU; decode prefers iGPU → hybrid strategies have real value on UMA.
3. Expert offload is high-leverage, but pinning behaviour (mlock vs mmap vs swap) is still fragile after recent llama.cpp loader changes.
4. mmap is safer for NVMe longevity than writing model weights into traditional swap.
5. Large zRAM works, but the community is still split on whether pure zRAM or zswap + disk is cleaner long-term.
6. Most published numbers are single-workload (just the LLM). Concurrent system behaviour is poorly characterised.

### Gaps the Omega Engine project can help fill

These are high-value, under-served areas where a well-documented, reproducible implementation on exactly this hardware would be useful to the wider community:

| Gap | Opportunity for Omega |
|-----|------------------------|
| **End-to-end constrained APU stack** | Publish a complete, reproducible configuration (zRAM sizing + multi-comp, NVMe swap priority, cgroup protection, Vulkan full offload, MoE expert strategy, lightweight TTS) that stays responsive under concurrent load. |
| **UMA-specific guidance** | Document bandwidth, thermal, and memory-pressure behaviour unique to Vega 8 / 12 GB systems. Most guides assume discrete VRAM. |
| **Concurrent workload characterisation** | Measure and publish how inference + Qdrant + consolidator + GRPO + TTS interact under memory pressure. Almost no one does this. |
| **Safe expert residency / pinning** | Contribute or document reliable ways to keep hot experts in RAM/zRAM while allowing cold ones to page, especially after the recent llama.cpp loader changes. |
| **Observability tooling** | Simple scripts or telemetry that surface zRAM pressure, page faults, expert hit rates, PSI, and iGPU utilisation in one place. |
| **Spatial / future-proof memory design** | The xyz payload work for Godot VR is novel; almost no local-agent projects are preparing for explorable 3D memory spaces. |
| **Open, local-first agent reference** | Most aggressive tuning stops at “run the model”. Omega’s full SEDA + continuous learning + sovereign design is rarer. |

### Bottom line

There are solid individual pieces and a few excellent Vega 8 / 5700U reports, but almost no one has published the *integrated, aggressively memory-tuned, multi-component local agent* you are building on this exact class of hardware.  

That makes the Omega Engine implementation itself a contribution. The most valuable things you can give the community are:

- A clean, reproducible recipe for the full stack on 12 GB UMA.
- Real measurements under concurrent load (not just isolated llama-bench numbers).
- Clear documentation of the failure modes and the knobs that actually matter on this hardware.

You are operating at the frontier of what is practical on low-end APUs in 2026. Documenting it well will help a lot of people who are trying to do the same thing with far less guidance.

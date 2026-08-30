**Omega Engine Comprehensive Systems Briefing**  
**Date:** 2 August 2026  
**Hardware Context:** AMD Ryzen 7 5700U (Vega 8 iGPU, 12 GB UMA) + reliable 8 GB zRAM (proven stable to ~24 GB total pressure with 32 GB disk swap)

This briefing consolidates every research finding, hardware strategy, and required manual update from the full session.

---

### 1. Original Manual Knowledge Gaps & Required Updates

| Area | Finding | Required Manual Change |
|------|---------|------------------------|
| **Target OS** | Ubuntu 25.04 reached EOL 15 Jan 2026 | Change target to Ubuntu 24.04 LTS or 26.04 LTS |
| **Qdrant TurboQuant** | Accurate (v1.18+, BITS2 = 16×, BITS4 default preferred for recall) | Prefer BITS4 by default; treat BITS2 as aggressive option after measuring recall. Raise `qdrant-client` floor to ≥1.18. Note `bits1_5` ≈ 24×. |
| **llama.cpp Graphics Queue** | `GGML_VK_ALLOW_GRAPHICS_QUEUE=1` is correct & opt-in. Gains are real but smaller/more variable on Vega 8 than on RDNA | Soften 4.8–10 % claim for Vega 8 specifically; note UMA bandwidth is the real limiter |
| **TRL Continuous Batching** | Accurate (`transformers≥5.8`, `trl≥1.7`, `use_transformers_continuous_batching`, `max_memory_percent` 0.3–0.4) | Keep; note text-only for now |
| **ElevenLabs webhooks** | Correct (raw body required) | Minor: show `BadRequestError` handling |
| **AnyIO SEDA** | Solid | Pin `anyio≥4.14` |
| **Hardware memory budget** | 12 GB UMA is extremely tight; dual-channel DDR4 speed matters more than most knobs | Add explicit UMA warning + realistic tok/s expectations + memory-budget table |
| **Other** | Consolidator clustering is a stub; systemd unit syntax incomplete; embedding dim hard-coded | Flesh out clustering, fix `taskset`/CPUAffinity, make vector size configurable |

**Priority update order:** OS target → Graphics Queue claims → TurboQuant guidance → dependency floors → UMA/memory warnings → consolidator implementation.

---

### 2. RAM Optimization Strategy (Core Theme of Session)

**Proven baseline:** 8 GB zRAM + 32 GB disk swap, stable and responsive at ~24 GB total pressure.

**Recommended evolved configuration**

| Tier | Size / Setting | Purpose |
|------|----------------|---------|
| Physical RAM | 12 GB UMA | Hottest pages; protect LLM process via cgroup |
| Fast compressed | **16 GB zRAM** (zstd + multi-comp + idle/huge recompress) | Warm working set (KV cache, embeddings, telemetry) |
| Safety / cold | 16–32 GB NVMe swap (lower priority) + optional zRAM writeback | Cold/incompressible pages + OOM prevention |

**Why 16 GB zRAM helps**  
- Moves more of the working set into the fast compressed tier.  
- Improves smoothness under load more than pure survival capacity (you already survive 24 GB).  
- Directly benefits longer contexts, larger Qdrant collections, concurrent TTS + training + inference, and less aggressive quantization.

**Pinning / protection (practical equivalent of “assign to cache”)**  
- cgroup v2 `MemoryMin` / high `MemoryHigh` + low `memory.swap.max` on the Omega daemon.  
- Light `mlock`/`mlockall` only on the hottest LLM structures if budget allows.  
- Kernel still decides what enters zRAM (no arbitrary page pinning into the compressed device).

**zswap alternative**  
Many 2026 kernel developers (including Chris Down) prefer zswap + NVMe when fast storage exists. Your proven zRAM + disk combination is already excellent; switching is optional once Virtual Swap Space matures.

**Do not run zRAM and zswap simultaneously.**

---

### 3. Latest Developments & Community Practices (mid-2026)

**Community patterns**
- Desktops ≤32 GB RAM: zRAM (high priority) + NVMe swap (low priority) **or** pure zswap + NVMe.
- Proven high-pressure users: enlarge fast compressed tier while keeping disk safety net.
- Servers: strong preference for zswap.
- Always keep real disk swap for capacity and hibernation.

**Kernel & tooling advances**
- **Virtual Swap Space** (active patch series): decouples zswap from physical swapfiles → more dynamic, less wasteful.
- zRAM multi-comp, recompress (idle/huge), and writeback to backing device — mature and directly useful.
- MGLRU reclaim improvements (Linux 7.2): better behaviour under pressure.
- zswap writeback folio optimisations and LZ4 dictionary speed-ups.
- Experimental userspace SIMD zRAM (trueno-zram / aprender-zram) claiming large speed-ups on AVX-512 (not required for your hardware).

**Ubuntu 26.04**  
Exists (Resolute Raccoon). No radical new memory technology, but newer kernel with the above features. Discussion favoured enabling zswap by default on desktop images when disk swap is present.

---

### 4. Additional Systems Strategies Discussed

**Lightweight local TTS (major RAM win)**  
Replace or supplement ElevenLabs with Piper, Inflect Nano/Micro, or similar (<200 MB). Frees 1–3+ GB for the LLM and Qdrant. Run as separate process or via SEDA bus.

**xyz coordinates for future Godot 4 VR**  
Store `pos_x`, `pos_y`, `pos_z` (and optional scale/colour/layer) in every Qdrant payload **now**.  
Generation options: UMAP/t-SNE/PCA of embeddings, force-directed layout, or simple deterministic projection.  
Zero future migration cost; Godot 4 OpenXR can instantiate Node3D / XRAnchor3D at those coordinates.

**Other operational rules retained from manual**  
- No PostgreSQL — Qdrant holds vectors + JSON payloads.  
- GBNF grammars for 100 % valid JSON.  
- Graphics Queue env var required.  
- Continuous batching for GRPO.  
- Raw body for ElevenLabs webhooks.

---

### 5. Consolidated Action Plan

**Immediate (hardware & OS)**  
1. Raise zRAM to 16 GB (zstd + multi-comp + writeback) while keeping 16–32 GB NVMe swap.  
2. Protect Omega process with systemd/cgroup memory controls.  
3. Plan migration from Ubuntu 25.04 (EOL) to 24.04 LTS or 26.04 LTS.

**Software / architecture**  
4. Add lightweight local TTS path.  
5. Begin writing xyz coordinates into all memory payloads.  
6. Apply the manual updates listed in Section 1 (OS, TurboQuant guidance, Graphics Queue claims, dependency floors, UMA warnings, consolidator, systemd syntax).

**Monitoring**  
Use `zramctl`, `swapon --show`, PSI pressure, `smem`/`atop`, and cgroup memory.stat under real GRPO + long-context loads. Watch thermals on the 5700U.

**Future watching**  
Virtual Swap Space landing, further MGLRU/zswap writeback improvements, and any Ubuntu 26.04 point-release defaults for zswap.

---

### 6. Expected Outcome

With the 16 GB zRAM + NVMe safety net, lightweight TTS, xyz preparation, and the corrected manual, the Omega Engine gains:
- Meaningfully larger practical working set on 12 GB UMA hardware.
- Smoother concurrent operation (inference + training + memory + voice + UI).
- Clean path to a future Godot 4 explorable 3D memory space.
- Alignment with 2026 kernel best practices and community experience.

This configuration turns a tightly constrained APU system into a stable, expandable local-first sovereign AI platform.

---

**Yes — there are useful optimizations, limited pinning options, and stronger alternatives depending on your goals.**

Here’s a clear breakdown for your 12 GB UMA system running Omega Engine.

### 1. Optimizing how zRAM functions

You **cannot** manually assign or pin arbitrary data/processes *into* zRAM the way you might with a cache. The kernel’s reclaim logic (kswapd) decides what gets compressed based on age, access patterns, and pressure. However, you *can* strongly influence behavior and protect critical memory.

**Useful zRAM-side optimizations (2026 kernel features):**

| Technique | What it does | How to use | Benefit for Omega |
|-----------|--------------|------------|-------------------|
| **Compression algorithm** | lz4 = speed, zstd = better ratio | `compression-algorithm = zstd` in zram-generator | Better effective capacity for compressible LLM/JSON data |
| **Multi-comp + recompress** | Primary fast algo + secondary high-ratio on idle/huge pages | Enable `CONFIG_ZRAM_MULTI_COMP`; echo `type=idle` or `type=huge` to `/sys/block/zram0/recompress` | Idle telemetry/Qdrant pages get denser compression |
| **Writeback of idle pages** | Move cold incompressible pages to real disk | Set a backing device + `echo type=idle > /sys/block/zram0/writeback` | Frees zRAM space for hotter data |
| **Memory limit** | Cap how much physical RAM zRAM can consume | `echo 8G > /sys/block/zram0/mem_limit` | Prevents zRAM from starving the LLM |
| **Swappiness + related sysctls** | Control how aggressively pages are sent to swap | `vm.swappiness=60–100` (higher with zRAM is often fine), lower `vfs_cache_pressure` | Tunable pressure behavior |

**Pinning / protecting processes (the practical equivalent of “assign to cache”):**

- **`mlock` / `mlockall`** — Locks pages into *physical* RAM so they never go to any swap (including zRAM). Use sparingly on the critical LLM process or key tensors if you can afford the RAM.
- **cgroup v2 memory controls** — Put the Omega Engine (or just the llama.cpp process) in its own cgroup with a high `memory.high` / `memory.min` and low `memory.swap.max`. This keeps the important workload preferred while less-critical processes (UI, telemetry, consolidator) are more likely to be compressed.
- **`systemd` MemoryAccounting + MemoryMin / MemoryHigh** — Already partially present in your omega.service; strengthen it so the daemon is protected while background jobs are allowed to spill into zRAM.

You cannot say “put this specific Qdrant collection into zRAM” or “pin these embeddings.” The kernel works at page granularity with LRU-style decisions.

### 2. Better options beyond pure zRAM

**zswap is the main alternative (and often preferred).**

| Feature | zRAM | zswap |
|---------|------|-------|
| Nature | Compressed *swap device* entirely in RAM | Compressed *cache in front of* real disk swap |
| Fallback | None (unless you also have disk swap) | Yes — cold pages go to real SSD/NVMe |
| Management | More manual (size, algorithms, writeback) | More automatic (kernel-managed pool) |
| Best for | Pure in-RAM systems, no/slow disk, write-endurance concerns | Systems with fast SSD + need capacity beyond compressed RAM |
| Consensus (2026) | Good, especially if you already have reliable 8 GB | Preferred by many kernel developers for general use when disk swap exists |

**Practical advice for you:**
- Keep your working 8 GB zRAM if it is already reliable and you rarely need more than the compressed capacity.
- If you have a fast SSD/NVMe, consider switching to (or adding) **zswap + a modest disk swap file**. Many 2026 discussions (including Ubuntu developers and kernel maintainers) lean toward zswap as the better default when real swap is available.
- **Do not run both zRAM and zswap at the same time** — they fight each other and waste RAM.

Other complementary tools:
- Lower-level: `vm.swappiness`, `vm.dirty_ratio`, `vfs_cache_pressure`.
- Application-level: Keep using TurboQuant, 4-bit models, and lightweight TTS (already discussed).
- cgroup isolation of the LLM process (most effective “pinning” you can do).

### 3. Does Ubuntu 26.04 add anything similar?

**Ubuntu 26.04 LTS (“Resolute Raccoon”) exists** (released around April 2026).  

From the available discussion and release notes:
- No major brand-new memory technology was introduced specifically for 26.04.
- The ongoing debate in Ubuntu development was whether to enable **zswap by default** on desktop images (instead of or alongside zram). Many voices preferred zswap when a real swap device is present.
- Pi images already used zswap in earlier releases; the broader desktop default was still being discussed around feature freeze.
- Standard kernel features (zRAM multi-comp, writeback, recompress, improved zswap accounting) are present in the 26.04 kernel series, so you get the modern tools either way.
- Higher recommended RAM (6 GB desktop) but nothing that fundamentally changes the zRAM/zswap picture.

**Bottom line for 26.04:** You get a newer kernel with the latest zRAM/zswap capabilities, but you still configure them yourself. There is no magic new “memory tier” tool that replaces what you already have.

### Recommended configuration path for Omega on your hardware

1. Stick with your reliable 8 GB zRAM for now (it is already working well under pressure).
2. Switch the algorithm to **zstd** if you haven’t already (better ratio on LLM-related data).
3. Enable multi-comp + idle/huge recompression if your kernel supports it.
4. Protect the main inference process with cgroup `MemoryMin` / high `memory.high` and consider light `mlock` only on the hottest structures if needed.
5. If you ever outgrow the 8 GB zRAM under sustained GRPO + large context, add a disk swap file and evaluate switching to **zswap** (or keep both tiers carefully).
6. When you move to Ubuntu 26.04, re-test both zRAM and zswap configurations — the newer kernel may change the performance balance slightly.

Would you like concrete config snippets for zram-generator + sysctl + systemd cgroup protection tailored to the Omega daemon?

---

**Current community practices and latest developments (as of mid-2026) for optimizing RAM with zRAM, zswap, and NVMe swap.**

### Core consensus in 2026

Most experienced users and kernel developers now treat the three technologies as **tiers**, not competitors:

| Tier | Role | Typical size / setting | When people use it |
|------|------|------------------------|--------------------|
| **Physical RAM** | Hottest pages | — | Always |
| **Compressed in-RAM (zRAM or zswap pool)** | Warm pages | 20–50 % of RAM (or fixed 4–16 GB) | Almost everyone with ≤32 GB RAM |
| **NVMe / fast SSD swap** | Cold / incompressible pages + safety net | 8–32+ GB | Preferred when available |

**Key rule almost everyone repeats**: Do **not** run zRAM *and* zswap at the same time. They fight each other.

### What people are actually doing

**1. Desktop / workstation (most common pattern for systems like yours)**  
- **zRAM** (zstd, high priority) + **NVMe swap file** (lower priority).  
- Or pure **zswap** in front of an NVMe swap file (growing preference among kernel people).  
- Size zRAM/zswap pool conservatively (often 25–50 % of RAM or a hard cap of 4–8–16 GB).  
- Keep a real disk swap of at least 8–16 GB (many keep 16–32 GB).  
- Raise `vm.swappiness` (often 60–100 or even higher with compressed swap).  
- Protect critical processes with cgroup v2 `MemoryMin` / `MemoryHigh`.

**2. “I already survive high pressure” users (exactly your situation)**  
People who have proven stable operation at 20–30+ GB of total swapped/compressed data usually:  
- Enlarge the fast compressed tier (your idea of going to 16 GB zRAM fits this).  
- Keep a substantial NVMe swap behind it.  
- Enable zRAM writeback of idle/huge/incompressible pages to the NVMe device.  
- Use multi-comp + recompression (idle/huge pages get a second, denser pass).

**3. Servers / heavy sustained load**  
Strong preference for **zswap + NVMe swap**. zRAM is seen as riskier because it has a hard capacity limit and can turn pressure into thrashing or OOM instead of graceful slowdown.

**4. Embedded / no-disk or write-endurance focused**  
Pure zRAM (sometimes with writeback to a small flash partition).

### Latest kernel & tooling developments (2025–2026)

| Development | Status / Impact | Relevance |
|-------------|-----------------|-----------|
| **Virtual Swap Space** (Nhat Pham et al.) | Active patch series (v3 in early 2026) | Decouples zswap from physical swapfiles. Makes zswap more dynamic, removes need for large pre-allocated swapfiles just to enable zswap. Big future win. |
| **zRAM multi-comp + recompress + writeback** | Mature in current kernels | Idle/huge pages can be recompressed with a denser algorithm; cold pages written to backing NVMe. Directly useful for your 16 GB plan. |
| **MGLRU reclaim improvements** (Linux 7.2) | Merged | Better reclaim loops and dirty handling; up to 30–100 % gains on some workloads (especially with slow I/O). Helps under heavy swap pressure. |
| **zswap writeback folio optimizations** | Ongoing (mid-2026 patches) | Faster freeing of cold writeback pages; reduces reclaim overhead. |
| **LZ4 dictionary / compression speed patches** | Posted early 2026 | >50 % faster dictionary compression in some zRAM I/O tests. |
| **Userspace SIMD zRAM (trueno-zram / aprender-zram)** | Available 2026 | Userspace ublk device with AVX-512 ZSTD claiming 12–19× faster compress/decompress than kernel zram on high-end CPUs. Experimental but interesting for extreme performance. |
| **Chris Down’s analysis** (Meta kernel engineer) | Widely cited March 2026 | Strongly recommends **zswap over zRAM** for most systems that have fast storage. zRAM best for hard limits or no disk. |

### Practical recommendations that match current best practice

For a system that has already proven stable at ~24 GB total pressure (your case):

1. **Raise zRAM to 16 GB** (zstd + multi-comp + idle/huge recompress) — this is exactly what people with proven headroom are doing.
2. **Keep a substantial NVMe swap** (16–32 GB) behind it at lower priority. This is the safety net that lets you push further.
3. Enable **zRAM writeback** of idle pages to the NVMe device so the fast tier stays full of useful data.
4. Protect the Omega LLM process with cgroup memory controls so it is preferred over background jobs.
5. Monitor with `zramctl`, `swapon --show`, PSI pressure stalls, and `smem` / `atop`.
6. Watch the Virtual Swap Space work — once it lands widely it will make pure zswap even more attractive.

**Emerging tools worth watching**
- `systemd-zram-generator` (still the standard way to configure zRAM)
- Userspace SIMD zRAM projects (trueno-zram etc.) for people who want maximum compression throughput
- Improved `smem`, `atop`, and PSI-based monitoring for diagnosing what is actually being compressed vs spilled to NVMe

**Bottom line for you**  
Your existing experience (stable at 24 GB total) puts you in the group that benefits most from enlarging the fast compressed tier to 16 GB **while retaining a real NVMe swap behind it**. That combination is currently one of the strongest, most battle-tested setups in the community for memory-hungry local AI workloads. The next big kernel improvements (Virtual Swap + better MGLRU + writeback) will only make this style of configuration better.

---

**Yes — moving from your current reliable 8 GB zRAM setup to a larger compressed tier (16 GB) while keeping a real disk swap behind it opens meaningful extra capacity, with some important caveats.**

### Interpreting your current setup
You have successfully run with **zRAM + a 32 GB disk swap**, reaching ~24 GB of used swap/compressed space while the machine stayed responsive and stable. That is excellent real-world evidence that your Ryzen 7 5700U + system can tolerate substantial compressed memory pressure without falling over.

This means the kernel is already treating the combination as a multi-tier system:
- Hot pages stay in physical RAM
- Warm/cold pages get compressed into zRAM (fast)
- Colder or incompressible pages spill to the 32 GB disk swap

### What increasing the zRAM portion to 16 GB would open up

Assuming you keep (or slightly reduce) the disk swap and raise the zRAM device to ~16 GB:

| Aspect | Current (≈8 GB zRAM + 32 GB disk) | With 16 GB zRAM + disk swap | Practical gain for Omega |
|--------|-----------------------------------|-----------------------------|---------------------------|
| **Effective compressed capacity** | Roughly 16–24 GB useful (depending on compression ratio) | Roughly 32–48 GB useful | Significantly more headroom for larger contexts, bigger Qdrant collections, concurrent training + inference |
| **Latency under pressure** | Good (you already stay responsive at 24 GB total) | Better for the “warm” working set | More of the LLM KV cache, embeddings, and telemetry stay in fast compressed RAM instead of hitting disk |
| **Overnight GRPO / LoRA** | Already feasible | More comfortable | Higher `num_generations`, longer sequences, or less aggressive 4-bit settings become realistic |
| **Qdrant + TurboQuant growth** | Limited by pressure | Can hold more points before slowdown | Better for the dual-branch memory + consolidator |
| **Concurrent TTS + UI + API** | Works | More concurrent headroom | Safer multitasking |
| **Risk** | Low (proven stable) | Slightly higher CPU/thermal load from more compression work; potential for zRAM to consume too much physical RAM if not limited | Manageable with `mem_limit` and cgroup protection |

**Bottom line of the increase**: You would primarily gain *speed and smoothness under load* rather than pure survival capacity (you already survive 24 GB). The extra 8 GB of zRAM acts as a larger fast cache layer, so more of the working set stays out of the slower disk tier.

### Adding / keeping a disk cache (or real disk swap) behind it

**Yes — you should keep a real disk swap (or explicit writeback target) behind the larger zRAM.** This is the strongest configuration for your use case.

Recommended tiered layout:

1. **Physical RAM** (12 GB) — hottest pages, protected LLM process via cgroup/`MemoryMin`
2. **16 GB zRAM** (zstd, multi-comp + idle/huge recompress) — warm pages, fast compressed
3. **Disk swap or zRAM writeback target** (at least 16–32 GB on SSD/NVMe) — cold / incompressible pages

**Benefits of the disk tier behind 16 GB zRAM**:
- Prevents the system from OOMing when the compressed working set exceeds what 16 GB of physical RAM can usefully hold after compression.
- Lets you run sustained high-memory workloads (long-context inference + training + large vector store) without the abrupt death you would get from pure zRAM.
- Writeback of idle/incompressible pages from zRAM to disk frees the fast tier for hotter data.
- Matches the pattern that has already proven stable for you at 24 GB total usage.

**zswap alternative note**:  
If you prefer less manual management, you could switch the middle tier to **zswap** (compressed cache in front of disk swap) sized to ~20–30 % of RAM or higher, and drop pure zRAM. Many 2026 kernel/Ubuntu discussions favor zswap when a fast disk is present. Given that your current zRAM + disk combination is already rock-solid, staying with an enlarged zRAM + disk is the lower-risk path.

### Practical recommendations for your hardware

- Raise zRAM to **16 GB** (or `min(ram*1.3, 16G)` style) with `zstd` and enable recompression of idle/huge pages.
- Keep a **disk swap of at least 16–24 GB** (you already know 32 GB works).
- Set a hard `mem_limit` on the zRAM device so it cannot starve the LLM of physical pages.
- Protect the Omega inference process with systemd/cgroup `MemoryMin` / high `memory.high` and low `memory.swap.max`.
- Monitor with `zramctl`, `free -h`, `swapon --show`, and pressure stall information under real GRPO + long-context loads.
- Watch thermals — more compression work on the 5700U will raise CPU package temperature under sustained pressure.

### What this realistically unlocks for Omega Engine

- Longer context windows or larger batch sizes without immediate thrashing.
- Bigger or less-aggressively quantized models in some scenarios.
- More aggressive overnight training (higher generation count or longer sequences).
- Larger in-memory Qdrant collections before you feel slowdown.
- Better concurrent operation of TTS, API, UI, and consolidator.

You already have the hard part proven (stable operation at 24 GB total pressure). Scaling the fast compressed tier to 16 GB while retaining the disk safety net is a low-risk, high-reward step that directly expands the practical working set of the whole stack.

Would you like ready-to-use `zram-generator.conf`, sysctl, and systemd snippet examples tuned for a 16 GB zRAM + disk-swap configuration on this hardware?

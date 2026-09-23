# Omega Engine Alpha — Machine & Setup Specification

Authoritative record of the development machine. Source of truth for every session,
so no re-discovery or re-research is needed. Last verified: 2026-09-08.

## System — Node 1 (ASUS ExpertBook P1503CVA) — THE FAST STRIKE ENGINE
- **Laptop**: ASUS ExpertBook **P1503CVA** (ASUSTeK Computer Inc.)
- **BIOS**: P1503CVA.337 (dated 2026-05-29)
- **OS**: Ubuntu 26.04 LTS "Resolute Raccoon" (Linux 7.0, Mesa 26.0.8, Wayland/GNOME 50)
- **CPU**: Intel Core **i7-13620H** (Raptor Lake-H), hybrid:
  - **6 physical P-cores** (CPUs 0,2,4,6,8,10) + HyperThreading siblings 1–11 odd → logical CPUs 0–11
  - **4 physical E-cores** (Gracemont) → logical CPUs 12–15
  - Total: **10 physical / 16 logical**. CPU-only, **no discrete GPU**.
  - Base clocks: E-cores ~3600 MHz, P-cores 4700–4900 MHz.
  - SIMD: `avx2` + `avx_vnni` (VNNI only on P-cores; E-cores lack VNNI).
  - Intel Thread Director (HW-guided scheduling) present; OS scheduler integration via `intel_pstate` + HWP.
  - **Scaling Driver**: `intel_pstate` (active mode, HWP enabled) — pseudo-governors: `performance` (EPP=0) / `powersave` (schedutil-like).
  - **Performance Tuning**: Governor `performance` + EPP=0 + power profile `performance` = 3600+ MHz sustained. Default `powersave` governor caps at ~2200 MHz. See `docs/CPU_PERFORMANCE_TUNING_GUIDE.md`.
  - **GPU**: Intel UHD Graphics 64EU (Raptor Lake-P, PCI ID 0xA7A8) — integrated, shared system memory. **Important**: Despite lspci showing Iris Xe branding in some tools, this CPU physically has a 64 EU die; the iris driver correctly rejects this PCI ID and falls back to the intel driver (harmless quirk). VA-API acceleration available via iHD driver. — for Open WebUI/Ollama host tasks; the primary compute target for the linked gaming-expert agent.
- **RAM**: **1×16GB Samsung DDR5-5600 SODIMM** (`M425R2GA3EB0-CWMOL`), **single-channel**, in `Controller0-ChannelA-DIMM0`, **running at 5200 MT/s** (not 5600). Second slot `Controller1-ChannelA-DIMM0` **EMPTY**. Max capacity 64GB, **2 slots (dual-channel capable)**. Dual-channel with 2nd matched stick expected **+52–58% token generation** (InsiderLLM Aug 2026). Predicted ~20–22 t/s on phi4-mini.

## System — Node 0 (HP Pavilion) — THE ARCHIVAL BASTION & NEXUS
- **Laptop**: HP Pavilion (model TBD)
- **OS**: Ubuntu 25.10 (Linux 6.x, Mesa, Wayland/GNOME)
- **CPU**: AMD Ryzen 7 5700U (Zen 2), 8 cores / 16 threads
- **RAM**: 16 GB Dual-Channel DDR4-3200 (symmetrical memory bus)
- **Storage**: NVMe 512GB
- **Strategic Role**: Archival stability, state consistency, compliance enforcement, orchestration, Git SSOT, Hall of Records
- **Key Service**: `omega-hub` — FastMCP multi-domain core hub on `0.0.0.0:8016` exposing 91 sovereign tools (Streamable HTTP)

## P2P Omegaverse Federation — Dual-Node Sovereign AI Cluster

### Fleet Topography & Silicon Specialization
| Node | Role | Silicon | Strength |
|------|------|---------|----------|
| **Node 0 (HP)** | Archival Bastion & Nexus | AMD Ryzen 7 5700U (8C/16T, Zen 2), 16GB DDR4-3200 dual-channel | Archival stability, Git SSOT, SQLite DBs, Vector Stores, Council Orchestration, omega-hub (91 tools) |
| **Node 1 (ASUS)** | Compute Vanguard | Intel i7-13620H (6P+4E/16T, RPL-H), 16GB DDR5-5200 single-channel (32GB dual target) | Local neural inference, fast model execution, high-throughput context processing, bare-metal Ollama runner |

### Wire Protocols (Layer by Layer)
| Layer | Transport | Binding | Purpose |
|-------|-----------|---------|---------|
| **1. Local LAN** | Streamable HTTP (`POST /mcp`) | Node 0: `0.0.0.0:8016` → Node 1 connects to `192.168.10.168:8016/mcp` | Immediate P2P federation |
| **2. Tailscale Mesh** | WireGuard via MagicDNS | `hp.tailnet:8016`, `asus.tailnet` | Roaming/Zero-config, tag-based ACLs (`tag:opencode -> tag:node0:8016`) |
| **3. Redis Pub/Sub** | High-frequency heartbeats | Ephemeral event bus | Phase 2: awareness heartbeats, graceful degradation to atomic lockfiles |

### Hivemind Channel Partitioning
| Node | Agent Persona | Channel | Function |
|------|---------------|---------|----------|
| HP (Node 0) | `@roc_racoon` | `opencode` | Legacy mining, DHAL, hardware forensics |
| HP (Node 0) | `@kali` / `@makali` | `opencode` | Council synthesis, debut release, law |
| HP (Node 0) | `@grokster` | `grokster` | OpenCode CLI internals, cross-platform KB |
| ASUS (Node 1) | `asus_build` | `opencode-asus` | Bare-metal compile, Ollama benchmarking |
| ASUS (Node 1) | `asus_plan` | `opencode-asus` | Hardware profiling, local workload planning |

### 4-Way Handoff Contract
```
[ASUS: asus_build]                            [HP: roc_racoon]
        │                                             │
        │ 1. hivemind_post_context(channel, intent)   │
        ├────────────────────────────────────────────►│ (Context stored in HALL_OF_RECORDS)
        │ 2. hivemind_submit_handoff(target="roc")    │
        ├────────────────────────────────────────────►│ (Packet written to data/handoff/pending/)
        │                                             │
        │                                             │ 3. hivemind_accept_handoff()
        │                                             │    (Packet moves to data/handoff/active/)
        │                                             │
        │                                             │ 4. hivemind_complete_handoff(result)
        │◄────────────────────────────────────────────┤    (Packet moves to data/handoff/completed/)
```

### Connectivity Commands
```bash
# Test LAN connectivity from ASUS
~/test_connection.sh

# Ceremonial first contact
python3 ~/hivemind_first_contact.py

# Remote MCP config for ASUS OpenCode
{
  "mcp": {
    "omega-hub": { "type": "remote", "url": "http://192.168.10.168:8016/mcp", "enabled": true }
  }
}
```
- **CPU**: Intel Core **i7-13620H** (Raptor Lake-H), hybrid:
  - **6 physical P-cores** (CPUs 0,2,4,6,8,10) + HyperThreading siblings 1–11 odd → logical CPUs 0–11
  - **4 physical E-cores** (Gracemont) → logical CPUs 12–15
  - Total: **10 physical / 16 logical**. CPU-only, **no discrete GPU**.
  - Base clocks: E-cores ~3600 MHz, P-cores 4700–4900 MHz.
  - SIMD: `avx2` + `avx_vnni` (VNNI only on P-cores; E-cores lack VNNI).
  - Intel Thread Director (HW-guided scheduling) present; OS scheduler integration via `intel_pstate` + HWP.
  - **GPU**: Intel UHD Graphics 64EU (Raptor Lake-P, PCI ID 0xA7A8) — integrated, shared system memory. **Important**: Despite lspci showing Iris Xe branding in some tools, this CPU physically has a 64 EU die; the iris driver correctly rejects this PCI ID and falls back to the intel driver (harmless quirk). VA-API acceleration available via iHD driver. — for Open WebUI/Ollama host tasks; the primary compute target for the linked gaming-expert agent.
- **RAM**: **1×16GB Samsung DDR5-5600 SODIMM** (`M425R2GA3EB0-CWMOL`), **single-channel**, in `Controller0-ChannelA-DIMM0`, **running at 5200 MT/s** (not 5600). Second slot `Controller1-ChannelA-DIMM0` **EMPTY**. Max capacity 64GB, 2 slots. (Dual-channel with a 2nd matched stick expected **+52–58% token generation** (InsiderLLM Aug 2026), not 1.8–2×. Predicted ~20–22 t/s on phi4-mini.)

## Compute inference profile (Ollama, CPU-only)
- Inference runs on the **6 physical P-cores ONLY conceptually**, but see the pin trap below.
- **Live measured optimum: `AllowedCPUs=0-11` + `OLLAMA_NUM_THREADS=8` = 14.4 t/s** (E-cores excluded).
- Sweep results: 6→14.0, 8→14.4, 10→14.17, 12→13.88 t/s.

### ⚠️ The P-core pin TRAP (do not regress)
Pinning `AllowedCPUs=0,2,4,6,8,10` + `OLLAMA_NUM_THREADS=6` caused a **catastrophic ~0.5 t/s** (was 13.5 t/s). Root cause: `llama-server` spawns ~29 threads; starving all onto the 6 physical P-cores causes a spin-wait barrier convoy (ollama #17916). Direct llama.cpp P-core-only tests (2.4–3×) do **not** transfer to Ollama's thread model.
**Correct config: keep HT siblings (0–11) in the CPU mask, exclude E-cores. Do NOT narrow to physical P-cores only.**

## Ollama setup
- **Version**: 0.33.3
- **Service**: systemd `ollama.service`, runs as user `ollama` (uid 997)
- **Models dir**: `/usr/share/ollama/.ollama/models`
- **Runtime**: `/usr/local/bin/ollama` + `/usr/local/lib/ollama/llama-server` + `libllama*.so` + `libggml-*.so`
- **CPU lib**: `libggml-cpu-alderlake.so` (AVX2+VNNI dispatch on P-cores)
- **Live override** (`/etc/systemd/system/ollama.service.d/override.conf`):
  - `OLLAMA_HOST=0.0.0.0:11434`
  - `OLLAMA_NUM_PARALLEL=1`
  - `OLLAMA_MAX_LOADED_MODELS=1` (16GB single-channel cannot hold 2 residents + OS headroom: MAX=2 left 1.9Gi avail + 1.4Gi swap thrash; MAX=1 keeps 9.2Gi avail, no swap, same phi4-mini throughput 13.4 t/s)
  - `OLLAMA_KEEP_ALIVE=30m`
  - `OLLAMA_NUM_THREADS=8`
  - `OLLAMA_CONTEXT_LENGTH=8192` (caps phi4-mini's 128k default; per-request raise via `num_ctx`)
  - `OLLAMA_KV_CACHE_TYPE=q8_0` (halves KV RAM; phi4-mini resident 3.7→3.2GB at 8k ctx)
  - `OLLAMA_FLASH_ATTENTION=1` (runner now `--flash-attn on`)
  - `OLLAMA_NO_CLOUD=1`
  - `AllowedCPUs=0-11`

Measured 2026-09-08 (warm 3-prompt, phi4-mini): **13.4 t/s** with KV q8_0 + flash-attn (baseline 13.3 t/s at f16 KV) — no throughput regression, ~0.5GB RAM freed.

### Advanced Ollama tuning (research-backed)
| Parameter | Current | Research Optimal | Notes |
|-----------|---------|------------------|-------|
| `OLLAMA_NUM_THREADS` | 8 | 8 | P-core count + HT elasticity; sweep-verified peak |
| `OLLAMA_CONTEXT_LENGTH` | 8192 | 8192 | Caps 128k default; per-request `num_ctx` works |
| `OLLAMA_KV_CACHE_TYPE` | q8_0 | q8_0 (now) → q4_k (future) | q8_0: ~50% KV RAM, near-lossless; q4_k: ~75%, <0.1 ppl Δ (awaits upstream) |
| `OLLAMA_FLASH_ATTENTION` | 1 | 1 | Forces flash-attn on; avoids silent fallback |
| `OLLAMA_NUM_PARALLEL` | 1 | 1 | Multi-model parallel hurts single-stream t/s |
| `OLLAMA_MAX_LOADED_MODELS` | 1 | 1 | Verified: MAX=2 → swap thrash; MAX=1 → clean |
| `OLLAMA_KEEP_ALIVE` | 30m | 30m | OWUI overrides per-request; must match in OWUI UI |

## Models installed (`ollama list`, 2026-09-08)
| Model | ID | Size |
|-------|----|------|
| code-reviewer:latest | c5386fedf483 | 4.7 GB |
| deepseek-r1:8b | 6995872bfe4c | 5.2 GB |
| qwen2.5-coder:7b | dae161e27b0e | 4.7 GB |
| summarizer:latest | baab6d5e1c24 | 2.5 GB |
| json-extractor:latest | 30bc72b5d51c | 2.5 GB |
| linux-admin:latest | 1ade147db8c7 | 2.5 GB |
| nomic-embed-text:latest | 0a109f422b47 | 274 MB |
| phi4-mini:latest | 78fad5d182a7 | 2.5 GB |

Custom models (Modelfiles in `.modelfiles/`): code-reviewer (FROM qwen2.5-coder:7b), summarizer, json-extractor, linux-admin.

## Quantization tradeoffs (7B models, CPU inference)
| Quant | Size | RAM Needed | Quality (ppl Δ vs FP16) | Speed vs FP16 | Best For |
|-------|------|------------|-------------------------|---------------|----------|
| **Q4_K_M** | ~4.1 GB | 7 GB | +0.05 | Baseline | **General purpose — sweet spot** |
| **Q5_K_M** | ~4.8 GB | 8 GB | +0.014 | ~same | Code, reasoning (better tool calls) |
| **Q6_K** | ~5.5 GB | 9 GB | +0.007 | ~same | High-accuracy needs |
| **Q8_0** | ~7.0 GB | 11 GB | +0.0004 | ~same | Near-lossless reference |
| Q3_K_M | ~3.3 GB | 6 GB | +0.15 | Faster | Draft generation, edge |

Sources: arXiv:2601.14277 (unified eval Llama-3.1-8B), ggml #2094, Qwen3 quantization guide, OmniCoder benchmarks.
**For 16GB + swap:** Q4_K_M (phi4-mini, qwen2.5-coder, deepseek-r1) optimal. Q5_K_M for deepseek-r1 if tool-call reliability matters.

## MoE vs Dense Architecture Reality (2026-09-22)

### The Fundamental Distinction

| Architecture | Active Params/Token | Total Params | RAM Determined By |
|--------------|---------------------|--------------|-------------------|
| **Dense (Qwen3.8-27B)** | 27.8B | 27.8B | **Total params** |
| **MoE (Qwen3.5-35B-A3B)** | 3B | 35B | **Total params** |

**Critical insight**: MoE saves *compute* (FLOPs/token), NOT *storage*. The entire expert pool + dense backbone must reside in RAM. GGUF file size ≈ model size in RAM.

### What `--cpu-moe` Actually Does

| Flag | Effect |
|------|--------|
| `--cpu-moe` | Moves ALL routed experts from VRAM → system RAM |
| `--n-cpu-moe N` | Moves first N layers' experts to RAM |
| **Does NOT do** | Stream inactive experts from NVMe on-demand |

True on-demand expert paging from disk exists only in `solid.cpp` fork (private, Apple Metal, 0.12 tok/s — unusable here).

### MoE Models That Fit 16GB RAM (with expert offloading)

| Model | Total / Active | Best Quant | Size | Quality Signal |
|-------|----------------|------------|------|----------------|
| Devstral Small 2505 | 23.6B / ~8B | Q4_K_M | 13.4 GB | 46.8% SWE-Verified, agentic design |
| gpt-oss-20b | 20B / ~4B | Q4 | 12.8 GB | o3-mini reasoning |
| Qwen3.5-35B-A3B | 35B / 3B | UD-Q2_K_XL | 12.2 GB | 69.2% SWE-Verified |

### Our Selection: Dense Coders for 16GB

| Model | Quant | Model Size | Total RAM (est.) | Use Case |
|-------|-------|------------|------------------|----------|
| Qwen2.5-Coder-7B | Q4_K_M | 4.68 GB | ~8.2 GB | Daily driver, long context headroom |
| Qwen2.5-Coder-7B | Q5_K_M | 5.44 GB | ~9.0 GB | Higher quality, less headroom |
| Qwen2.5-Coder-14B | Q4_K_M | 7.34 GB | ~10.8 GB | Complex tasks, when 32GB arrives |

**Apache 2.0 license on all** — commercial use, no restrictions.

---

## Open WebUI
- Container: `ghcr.io/open-webui/open-webui:v0.11.3` (pinned from `:main`), port **3000→8080**
- `OLLAMA_BASE_URL=http://host.docker.internal:11434`
- `--restart unless-stopped`, volume `open-webui-data`
- Stack files: `docker-compose.yml`, `.env.docker`
- **Critical integration findings:**
  - **No keep-alive env var in v0.11.3** — OWUI sends per-request `keep_alive` overriding server default (issues #10096, #11694).
  - **Must set in UI:** Workspace → Models → (model) → Advanced Parameters → **Keep Alive = `-1` (infinite) or `30m`**. Per-model admin setting applies to all chats.
  - **Task model bug (#14681):** Title/tag generation reloads model with different keep_alive → unloads/reloads. Workaround: set OWUI keep-alive = Ollama keep-alive = same value.
  - **`num_ctx` trap:** OWUI pre-fills 2048. **Leave unset** to inherit `OLLAMA_CONTEXT_LENGTH=8192`. Setting explicitly overrides server default.
  - Connection pooling: random load balancing across multiple Ollama URLs; single host = no benefit.
  - Timeout: default 10s; lower for faster failover if multi-host.

## Memory Subsystem Optimization (Single-Channel DDR5-5200)

### Transparent Huge Pages (THP)
- **Default: `always`** — causes latency spikes during khugepaged compaction (synchronous memory compaction on allocation failure).
- **Research (Phoronix Linux 6.18, AMD ZenDNN, Red Hat):** For LLM inference → **`madvise`** is optimal. Only apps calling `madvise(MADV_HUGEPAGE)` get THP; avoids fork/COW overhead and khugepaged stalls.
- **Action required:**
  - Runtime: `echo madvise > /sys/kernel/mm/transparent_hugepage/enabled`
  - Persistent: kernel cmdline `transparent_hugepage=madvise` (grub)
  - Defrag: `echo madvise > /sys/kernel/mm/transparent_hugepage/defrag`

### ZRAM vs ZSWAP — Strategic Decision for 16GB Inference Workload

**ZRAM:** Compressed RAM block device (swap in RAM). zstd algorithm, parallel streams = CPU cores.
**ZSWAP:** Compressed cache in front of disk swap. Trades CPU cycles for reduced swap I/O.

| Factor | ZRAM | ZSWAP |
|--------|------|-------|
| **Speed** | RAM speed (compressed) — no disk I/O | Disk swap speed (compressed cache helps) |
| **Capacity** | Configurable % of RAM (typically 50-200%) | Limited by disk swap size (our 4GB) |
| **CPU cost** | Compression/decompression on swap | Same, but only on eviction to disk |
| **OOM protection** | Excellent — absorbs peaks in fast RAM | Good — but disk latency on miss |
| **Conflict** | **Never use both** — they fight for pages | |

**Decision: ZRAM 8GB zstd, swappiness 100.**
- Rationale: 16GB single-channel, model loads (3-6GB) + KV cache + OS cause pressure. ZRAM at 8GB (50% RAM) with zstd (40% better compression than lz4, minimal speed penalty) absorbs peaks at RAM speed. High swappiness (100) pushes cold pages to ZRAM aggressively — unlike disk swap, ZRAM is fast enough.
- Our current 4GB `/swap.img` + swappiness 60 is conservative; ZRAM replaces it for inference workloads.
- Source: zram-tuning project (reapercanuk39), ChromeOS/Android memory strategies, Ariadne hotness-aware compression (HPCA 2025).

**Implementation:**
```bash
# /etc/systemd/zram-setup.service
modprobe zram num_devices=1
echo zstd > /sys/block/zram0/comp_algorithm
echo 8G > /sys/block/zram0/disksize
mkswap /dev/zram0
swapon /dev/zram0 -p 100
```
Plus `/etc/sysctl.d/99-llm-inference.conf`: `vm.swappiness=100`

### IRQ Affinity / CPU Isolation
- `isolcpus=` + `irqaffinity=` boot params can dedicate P-cores, but **breaks Thread Director** on hybrid CPUs. Not recommended for our workload (single inference, no real-time). systemd `AllowedCPUs` + EPP=performance is sufficient.

## Thermal / Power Management (Sustained Inference)

### Raptor Lake-H Power Limits (Intel Datasheet)
- **PL1 (sustained) = 45W** (Base Power / TDP)
- **PL2 (burst) = 115W** (Max Turbo Power)
- **Tau (PL2 duration) = 28–56s** depending on SKU
- **Tj max = 100°C**

### Current State (Verified)
- `intel_pstate` driver + `powersave` governor + **EPP=performance** — correct. `powersave` with EPP=performance lets hardware P-states (HWP) decide, biased toward performance.
- `thermald` active — adaptive thermal management. Risk: over-throttling if misconfigured (intel/thermal_daemon #550 shows PL1=0 bug).
- Idle ~63°C @ 400MHz — normal for laptop in silent mode.
- **Fan: already set to Performance mode in BIOS** (user confirmed).

### Recommendations
- **Keep EPP=performance** (done). Don't force `performance` governor — bypasses HWP.
- **BIOS verification needed:** Speed Shift = Enabled, Turbo = Enabled, Energy Performance = Performance, Fan = Performance.
- **Optional PL1/PL2 tuning** via BIOS or `intel-undervolt` if thermal headroom exists. Chassis likely limited by 45W PL1.
- **10-min sustained bench** to verify no throttling: run phi4-mini continuous, log `sensors` + `turbostat`. If freq drops < 3.5GHz sustained → thermal limit.

## Linux Kernel Parameters for Inference

| Parameter | Current | Recommended | How to Apply |
|-----------|---------|-------------|--------------|
| `transparent_hugepage` | always (default) | **madvise** | Runtime + kernel cmdline |
| `thp defrag` | defer+madvise | **madvise** | Runtime |
| CPU governor | powersave + EPP=performance | **Keep** | Already optimal for HWP |
| `vm.swappiness` | 60 | **100 (with ZRAM)** | With ZRAM, high swappiness pushes cold pages to fast compressed RAM |
| ZRAM | none | **8GB zstd, swappiness 100** | systemd service + sysctl |
| `nohz_full` / `isolcpus` | none | **Don't** | Breaks Thread Director on hybrid CPUs |

**THP madvise is the single highest-impact kernel tweak** — eliminates khugepaged stalls during model load/KV cache growth.

---

## Intel Hybrid Architecture Deep Dive (Research-Backed)

### Linux Scheduler Evolution for Hybrid CPUs

| Kernel | Scheduling Priority | Problem |
|--------|---------------------|---------|
| **v4.9** (pre-ITMT) | P-core = E-core = HT sibling | Random placement, high variance |
| **v4.10–v5.15** (ITMT) | P-core → **HT sibling** → E-core | **Wrong!** HT sibling preferred over E-core |
| **v5.16+** (ITMT fixed) | P-core → **E-core** → HT sibling | **Correct** — spreads to E-core before HT |
| **v6.0+** (ITD/HFI) | ISA-class aware (AVX2→P, SSE→E, etc.) | **Optimal** — Thread Director hints used |

**Your kernel check:**
```bash
uname -r
# If < 5.16: echo 0 > /proc/sys/kernel/sched_itmt_enabled  # Disable broken ITMT
# If >= 5.16: leave enabled (correct behavior)
# If >= 6.0: ITD/HFI active automatically
```

### Intel Thread Director (ITD) ISA Classes — Why Your CPU Mask Works

ITD classifies workloads by instruction mix into 4 classes:

| ISA Class | Instructions | P-core/E-core Ratio | Best Placement | llama.cpp Relevance |
|-----------|--------------|---------------------|----------------|---------------------|
| **Class 0** | SSE / scalar | 1.27× | P-core slight edge | Light loads |
| **Class 1** | AVX2 / VNNI | 1.5–2.0× | **Strongly P-core** | **GEMM (matrix multiply)** |
| **Class 2** | AVX-512 / AMX | 2.0×+ | **P-core only** | Not on RPL-H |
| **Class 3** | PAUSE / spin-wait | 1.0× | **E-core fine** | Barrier sync |

**llama.cpp implication:** Matrix multiply (GEMM) uses AVX2/VNNI → **Class 1-2** → **must run on P-cores**. This is why `AllowedCPUs=0-11` (P-cores + HT) works and E-cores hurt.

### Hardware Feedback Interface (HFI)

The kernel exposes per-CPU capability via thermal framework:
```bash
# View HFI capability table (performance/efficiency 0-255)
cat /sys/class/thermal/cooling_device*/cur_state
# Or via intel_hfi driver (kernel 6.0+)
```

Example capability table structure:
```
Index  CPU          Perf  Efficiency
0      P0,P1        56    92
1      P2,P3        66    92
2      P4-P7        88    100
3      P8-P11       44    100
E-cores              30    30 (lower at high freq)
```

### Why 8 Threads is the Sweet Spot (Scheduler + Barrier Dynamics)

| Threads | Behavior |
|---------|----------|
| **6** (physical P-cores only) | No HT elasticity; barrier sync stalls |
| **8** (your config) | **Optimal** — 6 P-cores + 2 HT siblings absorb barrier wait; OS headroom |
| **10–12** | E-core threads enter → slower AVX2; or all HT → convoy risk |
| **>12** | E-cores active → memory contention, no AVX2 benefit |

The `llama-server` spin-wait barrier causes all worker threads to rendezvous each token. With 8 threads on 12 logical CPUs (0-11), the scheduler can always place waiters on HT siblings while workers occupy physical P-cores — **no convoy, full AVX2 throughput**.

### Memory Bandwidth Math (Single vs Dual Channel)

| Config | Theoretical Peak | Real-World | Impact on Token/s |
|--------|------------------|------------|-------------------|
| **1×16GB DDR5-5200** (current) | 41.6 GB/s | ~30-35 GB/s | Baseline (14.4 t/s) |
| **2×16GB DDR5-5200** (dual-channel) | 83.2 GB/s | ~65-70 GB/s | **~1.8-2× token/s** (memory-bound) |

LLM inference streams weights from DRAM continuously. Single-channel is your **hard bottleneck** — not CPU.

## ASUS ExpertBook P1503CVA BIOS Specifics

**BIOS version:** P1503CVA.337 (2026-05-29) — current.

**Memory:** 2× DDR5 SO-DIMM slots, DDR5-5200 (our stick runs at 5200, not 5600 — JEDEC limit for 1DPC).

**CPU Configuration (Advanced → CPU Configuration):**
- **Hyper-Threading:** Enabled (default) — keep for 8-thread config
- **Intel SpeedStep (EIST):** Enabled — required for HWP
- **Intel Speed Shift (HWP):** **Enabled** — critical for per-core P-states
- **Turbo Mode:** Enabled — allows PL2 burst
- **C-states (C3/C6):** Enabled — power savings at idle
- **Package C-state limit:** Enabled (C6/C8/C10) — deep idle
- **Energy Performance Bias:** **Performance** (or Balanced Performance) — hardware default for EPP
- **AVX offset:** 0 — negative offset reduces AVX freq; keep 0 for inference
- **PL1/PL2:** Usually locked on laptops; viewable in Advanced → Power → Power Management Control

**Action items (verify on next reboot):**
1. Speed Shift = Enabled
2. Turbo = Enabled
3. Energy Performance = Performance
4. Fan profile = Performance (confirmed by user)

## Project harness (`omega-engine-alpha`)
- `Makefile`: bench/bench-all/bench-compare, python-chatbot, python-serve, env-setup/env-apply/env-revert, create-coder, gnosis-lock, gnosis-stats
- `scripts/bench.py`, `scripts/chatbot.py`, `scripts/serve.py`, `scripts/backup_harness.sh`
- `.env.ollama`: env source of truth (documents the pin trap, OLLAMA_NUM_THREADS=8)
- `.env.ollama.example` / `.env.docker.example`: redacted templates (versioned; real files stay untracked)
- `docker-compose.yml`, `.env.docker`
- Local git repo (main): tracks SSOT docs/scripts/gnosis-protocol; secrets & generated gnosis data ignored

### OpenCode model configuration (Big Pickle)
Built-in via the models.dev registry — no custom `provider.opencode.models` block
exists on this machine and none is needed. History: a 1M-window override lived
here and was true (205.8K+ token sessions); Zen moved the model to 200K within
~a day (operator-observed 2026-09-18; registry: 200K/160K/32K). Doctrine going
forward: drift-detect, never hardcode (`scripts/opencode_provider_doctor.sh`;
gaps guide §11.8/§13).
- Instructions stack loaded per session (project config): `AGENTS.md`, `docs/HARDWARE.md`,
  `docs/SYSTEM_GUIDE.md`, `docs/BENCHMARKS.md` ≈ 13.5K tokens before MCP tools.
  HARDWARE.md loads from the PROJECT config only (de-duplicated 2026-09-09).

## Frontier-model access tooling (added 2026-09-21, review G6)
Two host-level routes to free frontier-class models (ROADMAP P3.7; see
`docs/ANTIGRAVITY_GUIDE.md` for full traps and operation):
- **Cline CLI 3.0.62** — npm global (`/usr/local/bin/cline`), hub healthy.
  State: `~/.cline/data/settings/providers.json` (0600; **contains live OAuth
  tokens** — accessToken/refreshToken, never copy into docs/USB; rotate by
  deleting the auth block + `cline` re-login). Verified free models
  (2026-09-21, $0 smoke tests + frontier review + 43.5K long-context probe):
  `z-ai/glm-5.3-flash`, `cline-free/deepseek-v4.1-flash` (1M/384K, images).
  Entitlement: select the FREE model once in `cline -i` → `/settings` →
  Cline provider, then `-m` works headless.
- **Antigravity IDE 2.5.5** — `snap install antigravity-ide-snap --classic`,
  latest/stable. State: `~/.antigravity-ide/`, `~/.config/Antigravity IDE/`.
  Plugin route (opencode-antigravity-auth v1.6.0 via repo `.opencode/opencode.json`)
  is **DEAD on Node 1** — no working model call ever; reference only.
  Credentials: `~/.local/share/opencode/auth.json` (0600, canonical).

## Network / disk caveats
- Slow/flaky link (~300KB/s–4MiB/s). `/tmp` is a 7.4GB tmpfs (cleared on reboot).
- Big downloads → real disk `/home/xnai/ollama-install/` (used aria2 `-x8 -s8 -c` + `curl -C -` resume).

## Sudo
- `/etc/sudoers.d/95-nopasswd`: FULL NOPASSWD — **REVERT PENDING** (`sudo rm` it; keep `95-agent`, `95-pkexec`).
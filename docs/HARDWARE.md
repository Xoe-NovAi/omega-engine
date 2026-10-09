# Omega Engine Alpha — Machine & Setup Specification

Authoritative record of the development machine. Source of truth for every session,
so no re-discovery or re-research is needed. Last verified: 2026-09-23.

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
  - **Performance Tuning**: Current measured state is governor `powersave` with
    EPP `balance_performance` and power profile `balanced`. Performance-profile
    runs (EPP `performance`/`0`) are deliberate benchmark modes, not the current
    idle/desktop state. See `docs/CPU_PERFORMANCE_TUNING_GUIDE.md`.
  - **GPU**: Intel UHD Graphics 64EU (Raptor Lake-P, PCI ID 0xA7A8) — integrated, shared system memory. **This is not a disabled Iris Xe.** The i7-13620H ships **Intel UHD Graphics 64EU as its only iGPU** — no Iris Xe SKU exists for this part (Intel ARK; confirmed by an Intel employee: *"this CPU is not equipped with Iris Xe graphics"*). Intel's "single-channel disables Iris Xe / drops EU count" rule is **Tiger Lake (11th Gen) only** and does not apply here. Verified: `i915` + `xe` are the loaded drivers; there is no separate `iris` module on this kernel. Adding a second RAM stick is a **bandwidth** upgrade only — it cannot enable Iris Xe or change the EU count. VA-API acceleration available via iHD driver. — for Open WebUI/Ollama host tasks; the primary compute target for the linked gaming-expert agent.
- **RAM**: **1×16GB Samsung DDR5-5600 SODIMM** (`M425R2GA3EB0-CWMOL`), **single-channel**, in `Controller0-ChannelA-DIMM0`, **running at 5200 MT/s** (not 5600). Second slot `Controller1-ChannelA-DIMM0` **EMPTY**. Max capacity 64GB, **2 slots (dual-channel capable)**. Dual-channel with 2nd matched stick expected **+52–58% token generation** (InsiderLLM Aug 2026). Predicted ~20–22 t/s on phi4-mini.

## System — Node 0 (HP Pavilion) — THE ARCHIVAL BASTION & NEXUS
- **Laptop**: HP Pavilion (model TBD)
- **OS**: Ubuntu 25.10 (Linux 6.x, Mesa, Wayland/GNOME)
- **CPU**: AMD Ryzen 7 5700U (Zen 2), 8 cores / 16 threads
- **RAM**: 16 GB Dual-Channel DDR4-3200 (symmetrical memory bus)
- **Storage**: NVMe 512GB
- **Strategic Role**: Archival stability, state consistency, compliance enforcement, orchestration, Git SSOT, Hall of Records
- **Key Service**: `omega-hub` — FastMCP multi-domain core hub on `0.0.0.0:8016`;
  55 tools were present in the latest verified handshake (2026-10-07); recheck
  live after Node 0 changes.

## P2P Omegaverse Federation — Dual-Node Sovereign AI Cluster

### Fleet Topography & Silicon Specialization
| Node | Role | Silicon | Strength |
|------|------|---------|----------|
| **Node 0 (HP)** | Archival Bastion & Nexus | AMD Ryzen 7 5700U (8C/16T, Zen 2), 16GB DDR4-3200 dual-channel | Archival stability, Git SSOT, SQLite DBs, Vector Stores, Council Orchestration, omega-hub (55 tools live 2026-10-07) |
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
  - **GPU**: Intel UHD Graphics 64EU (Raptor Lake-P, PCI ID 0xA7A8) — integrated, shared system memory. **This is not a disabled Iris Xe.** The i7-13620H ships **Intel UHD Graphics 64EU as its only iGPU** — no Iris Xe SKU exists for this part (Intel ARK; confirmed by an Intel employee: *"this CPU is not equipped with Iris Xe graphics"*). Intel's "single-channel disables Iris Xe / drops EU count" rule is **Tiger Lake (11th Gen) only** and does not apply here. Verified: `i915` + `xe` are the loaded drivers; there is no separate `iris` module on this kernel. Adding a second RAM stick is a **bandwidth** upgrade only — it cannot enable Iris Xe or change the EU count. VA-API acceleration available via iHD driver. — for Open WebUI/Ollama host tasks; the primary compute target for the linked gaming-expert agent.
- **RAM**: **1×16GB Samsung DDR5-5600 SODIMM** (`M425R2GA3EB0-CWMOL`), **single-channel**, in `Controller0-ChannelA-DIMM0`, **running at 5200 MT/s** (not 5600). Second slot `Controller1-ChannelA-DIMM0` **EMPTY**. Max capacity 64GB, 2 slots. A matched second DIMM may improve memory bandwidth, but the projected `+52–58%` token-generation gain and `20–22 t/s` forecast are **unmeasured external estimates**, not local results.

## Compute inference profile (Ollama, CPU-only)
- Inference runs on the **6 physical P-cores ONLY conceptually**, but see the pin trap below.
- **Live measured optimum: `AllowedCPUs=0-11` + `OLLAMA_NUM_THREADS=8` = 14.4 t/s** (E-cores excluded).
- Sweep results: 6→14.0, 8→14.4, 10→14.17, 12→13.88 t/s.

### ⚠️ The P-core pin TRAP (do not regress)
Pinning `AllowedCPUs=0,2,4,6,8,10` + `OLLAMA_NUM_THREADS=6` caused a **catastrophic ~0.5 t/s** (was 13.5 t/s). Root cause: `llama-server` spawns ~29 threads; starving all onto the 6 physical P-cores causes a spin-wait barrier convoy (ollama #17916). Direct llama.cpp P-core-only tests (2.4–3×) do **not** transfer to Ollama's thread model.
**Correct config: keep HT siblings (0–11) in the CPU mask, exclude E-cores. Do NOT narrow to physical P-cores only.**


### ⚡ E-Core Embedding Offload (Hardware Coexistence)
- **Standalone ONNX Server**: `scripts/embedding_server.py` runs INT8 Qwen3-Embedding-0.6B (Matryoshka 768d) on the **4 Gracemont E-cores ONLY (logical CPUs 12-15)** with 4 intra-op threads and spin-wait disabled (`allow_spinning=0`).
- **Benchmarked latency**: **89.24 ms** per query embedding on E-cores; zero contention with P-cores.
- **Service Unit**: `scripts/omega-embedding-server.service` (`~/.config/systemd/user/omega-embedding-server.service`).
- **Full Architecture Report**: See `docs/research/RAPTOR_LAKE_HARDWARE_RESEARCH_REPORT.md`.

## Ollama setup
- **Version**: 0.33.3
- **Service**: systemd `ollama.service`, runs as user `ollama` (uid 997)
- **Models dir**: `/usr/share/ollama/.ollama/models`
- **Runtime**: `/usr/local/bin/ollama` + `/usr/local/lib/ollama/llama-server` + `libllama*.so` + `libggml-*.so`
- **CPU lib**: `libggml-cpu-alderlake.so` (AVX2+VNNI dispatch on P-cores)
- **Live override** (`/etc/systemd/system/ollama.service.d/override.conf`):
  - `OLLAMA_HOST=0.0.0.0:11434`
  - `OLLAMA_NUM_PARALLEL=1`
  - `OLLAMA_MAX_LOADED_MODELS=1` (16GB single-channel cannot hold 2 residents + OS headroom: MAX=2 left 1.9Gi avail + 1.4Gi swap thrash; MAX=1 keeps 9.2Gi avail, same phi4-mini throughput 13.4 t/s in the 2026-09-08 benchmark; current zRAM usage must be checked separately)
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

## Models installed (`ollama list`, 2026-09-23)
| Model | ID | Size |
|-------|----|------|
| gemma4-12b-qat:latest | b3f9087ff433 | 7.0 GB |
| qwen3-0.8b-quick:latest | f96f0b6cdc7e | 528 MB |
| rocracoon-3b:latest | aeb3689d2da9 | 2.8 GB |
| nemotron3-nano:latest | 246bbd676632 | 2.8 GB |
| phi4-mini-reasoning:latest | f20cabd6439d | 2.8 GB |
| gemma-3-12b:latest | 187b7e0279b9 | 5.7 GB |
| krikri-8b:latest | 056e6d1f0b5d | 5.9 GB |
| qwen2.5-coder-14b:latest | 9b60ea4fba3f | 9.0 GB |
| qwen2.5-coder:14b | 9ec8897f747e | 9.0 GB |
| qwen2.5-coder-7b:latest | baf5df73579c | 4.7 GB |
| code-reviewer:latest | c5386fedf483 | 4.7 GB |
| deepseek-r1:8b | 6995872bfe4c | 5.2 GB |
| qwen2.5-coder:7b | dae161e27b0e | 4.7 GB |
| json-extractor:latest | 30bc72b5d51c | 2.5 GB |
| summarizer:latest | baab6d5e1c24 | 2.5 GB |
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
- Current state: `/dev/zram0` is active with zstd, priority 100, and `vm.swappiness=100`.
- The NVMe-backed 4GB `/swap.img` is retained on disk for rollback but is disabled and not listed in `/etc/fstab`; it was swapped off 2026-09-23 so zRAM is the only active swap device.
- Source: zram-tuning project (reapercanuk39), ChromeOS/Android memory strategies, Ariadne hotness-aware compression (HPCA 2025).

**Implementation (current generator path):**
```ini
# /etc/systemd/zram-generator.conf.d/99-llm.conf
[zram0]
zram-size = min(ram / 2, 8192)
compression-algorithm = zstd
```
Plus `/etc/sysctl.d/99-llm-inference.conf`: `vm.swappiness=100`.
The generated service is `systemd-zram-setup@zram0.service`; the older manual
`zram-setup.service` recipe is retained only as an alternative procedure.

### IRQ Affinity / CPU Isolation
- `isolcpus=` + `irqaffinity=` boot params can dedicate P-cores, but **breaks Thread Director** on hybrid CPUs. Not recommended for our workload (single inference, no real-time). systemd `AllowedCPUs` + EPP=performance is sufficient.

## Thermal / Power Management (Sustained Inference)

### Raptor Lake-H Power Limits (Intel Datasheet)
- **PL1 (sustained) = 45W** (Base Power / TDP)
- **PL2 (burst) = 115W** (Max Turbo Power)
- **Tau (PL2 duration) = 28–56s** depending on SKU
- **Tj max = 100°C**

### Current State (Verified)
- `intel_pstate` driver + `powersave` governor + **EPP=balance_performance** — current
  desktop state. Performance-profile runs with EPP=`performance` are deliberate
  benchmark modes, not the current idle state.
- `thermald` active — adaptive thermal management. Risk: over-throttling if misconfigured (intel/thermal_daemon #550 shows PL1=0 bug).
- Idle ~63°C @ 400MHz — normal for laptop in silent mode.
- **Fan: already set to Performance mode in BIOS** (user confirmed).
- **RAPL powercap is ROOT-ONLY by default** (`energy_uj` mode `r--------`). Fixed one-time via `/etc/udev/rules.d/90-rapl-readable.rules` + `/etc/tmpfiles.d/rapl-readable.conf` (group `xnai`, mode 0440) so `scripts/screening.py` telemetry needs no sudo. Verified `max_energy_range_uj = 262,143,328,850` (≈262 kJ → wraps ~87 min @ 40W — wraparound correction required).
- **Telemetry under screening load (rocracoon-3b, 18 runs):** avg pkg power 37.2W, peak pkg temp 97.05°C (near Tj max 100°C → sustained inference sits right at the 45W PL1 thermal envelope), avg 3.14 J/token, boost freq 4.3–4.8 GHz.
- **Thermal zones:** `thermal_zone9` = `x86_pkg_temp`, `thermal_zone0` = `acpitz` (skin), `thermal_zone2` = `TCPU`. Telemetry selects by type priority, not sort order.

### Recommendations
- **Keep EPP=performance** (done). Don't force `performance` governor — bypasses HWP.
- **BIOS verification needed:** Speed Shift = Enabled, Turbo = Enabled, Energy Performance = Performance, Fan = Performance.
- **Optional PL1/PL2 tuning** via BIOS or `intel-undervolt` if thermal headroom exists. Chassis likely limited by 45W PL1.
- **10-min sustained bench** to verify no throttling: run phi4-mini continuous, log `sensors` + `turbostat`. If freq drops < 3.5GHz sustained → thermal limit.

## Linux Kernel Parameters for Inference

| Parameter | Current | Recommended | How to Apply |
|-----------|---------|-------------|--------------|
| `transparent_hugepage` | madvise | **madvise** | Runtime + kernel cmdline |
| `thp defrag` | defer+madvise | **madvise** | Runtime |
| CPU governor | powersave + EPP=performance | **Keep** | Already optimal for HWP |
| `vm.swappiness` | 100 | **100 (with ZRAM)** | With ZRAM, high swappiness pushes cold pages to fast compressed RAM |
| ZRAM | 8GB zstd, priority 100 | **8GB zstd, swappiness 100** | systemd-zram-generator + sysctl |
| NVMe swap | disabled; `/swap.img` retained | **Disabled** | zRAM is the only active swap device; uncomment `/etc/fstab` for rollback |
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

### OpenCode model configuration (rotating hosted aliases)
Built-in via the Models.dev/provider registry — no custom
`provider.opencode.models` block exists on this machine and none is needed.
Big Pickle and Space Bunny are dynamic stealth aliases: their underlying
models and capacity may rotate in place, and Node 1/Node 0 observations can
legitimately disagree. Big Pickle remains free despite lacking a `-free`
suffix. Never hardcode context/output limits for a rotating alias; select the
alias and refresh live metadata (`opencode models <provider> --verbose --refresh`).
Canonical policy: `docs/OPENCODE_FOUNDATION.md`; historical measurements:
gaps guide §13.
- Instructions stack loaded per session (project config): `AGENTS.md`, `docs/HARDWARE.md`,
  `docs/SYSTEM_GUIDE.md`, `docs/BENCHMARKS.md` ≈ 13.5K tokens before MCP tools.
  HARDWARE.md loads from the PROJECT config only (de-duplicated 2026-09-09).

## Frontier-model access tooling (added 2026-09-21, review G6)
Two host-level routes to free frontier-class models (ROADMAP P3.7; see
`docs/ANTIGRAVITY_GUIDE.md` for full traps and operation):
- **Cline CLI 3.0.62** — npm global (`/usr/local/bin/cline`), hub healthy.
  State: `~/.cline/data/settings/providers.json` (0600; **contains live OAuth
  tokens** — accessToken/refreshToken, never copy into docs/USB; rotate by
  deleting the auth block + `cline` re-login).   Verified free models (2026-09-21 snapshot; refresh live before relying on
  capacity): `z-ai/glm-5.3-flash`, `cline-free/deepseek-v4.1-flash` (observed
  1M/384K, images). Treat these as dated observations, not durable model metadata.
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
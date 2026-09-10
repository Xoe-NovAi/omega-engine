# SYSTEM_GUIDE.md — Definitive Living Guide for ASUS ExpertBook P1503CVA (i7-13620H) Local AI Inference

**Machine:** ASUS ExpertBook P1503CVA | **CPU:** i7-13620H (6P+4E, 10C/16T) | **RAM:** 1×16GB DDR5-5600 @ 5200 MT/s (single-channel) | **GPU:** Iris Xe 96EU (shared) | **OS:** Ubuntu 26.04 LTS, Linux 7.0 | **BIOS:** P1503CVA.337 (2026-05-29)

**Purpose:** Single authoritative source for all system tunings, decisions, rationale, and future evolution. Updated every session. No re-discovery.

---

## 1. CORE PRINCIPLES

| Principle | Rationale |
|-----------|-----------|
| **Measure, don't guess** | Every tuning has bench evidence or citation |
| **Document the trap** | P-core pinning (0,2,4,6,8,10) = 0.5 t/s disaster (ollama #17916) |
| **Single-channel reality** | 41.6 GB/s theoretical → ~35 GB/s actual; bandwidth is the bottleneck |
| **Hybrid CPU respect** | Thread Director exists; don't fight it with `isolcpus`/`nohz_full` |
| **Living document** | This guide grows; stale entries get tagged `[STALE]` and re-verified |

---

## 2. CURRENT OPTIMAL CONFIG (Verified 2026-09-08)

### Ollama (systemd override: `/etc/systemd/system/ollama.service.d/override.conf`)
```ini
[Service]
Environment=OLLAMA_HOST=0.0.0.0:11434
Environment=OLLAMA_NUM_PARALLEL=1
Environment=OLLAMA_MAX_LOADED_MODELS=1
Environment=OLLAMA_KEEP_ALIVE=30m
Environment=OLLAMA_NUM_THREADS=8
Environment=OLLAMA_CONTEXT_LENGTH=8192
Environment=OLLAMA_KV_CACHE_TYPE=q8_0
Environment=OLLAMA_FLASH_ATTENTION=1
Environment=OLLAMA_NO_CLOUD=1
AllowedCPUs=0-11
```

### Open WebUI (Docker, pinned v0.11.3)
- `docker-compose.yml`: `image: ghcr.io/open-webui/open-webui:v0.11.3`
- `OLLAMA_BASE_URL=http://host.docker.internal:11434`
- **UI setting required:** Workspace → Models → (each) → Advanced → Keep Alive = `-1` (or `30m`)
- **num_ctx:** Leave UNSET (inherits 8192 from Ollama)

### CPU Affinity & Threading
- **AllowedCPUs=0-11** (P-cores + HT siblings, E-cores excluded)
- **OLLAMA_NUM_THREADS=8** (6 P-cores + 2 HT elasticity)
- **Runner verified:** `llama-server --flash-attn on -c 8192 --cache-type-k q8_0 --cache-type-v q8_0`

### Performance Baseline (phi4-mini, Q4_K_M, 8k ctx, warm)
| Metric | Value |
|--------|-------|
| Throughput | **13.4 t/s** (3-prompt avg) |
| Resident RAM | **3.2 GB** (down from 3.7 GB f16 KV) |
| Swap pressure | **~0** (MAX_LOADED_MODELS=1) |
| Available RAM | **9.2 GiB** |

---

## 3. STRATEGIC DECISIONS (With Rationale)

### 3.1 ZRAM vs ZSWAP → **ZRAM 8GB zstd, swappiness 100**

| Factor | Decision | Why |
|--------|----------|-----|
| **Technology** | ZRAM | Compressed RAM block device; no disk I/O |
| **Size** | 8GB (50% RAM) | Absorbs model-load peaks (3-6GB each) |
| **Algorithm** | zstd | 40% better compression than lz4, minimal speed penalty |
| **Swappiness** | 100 | Pushes cold pages to fast ZRAM aggressively |
| **Conflict** | Never ZRAM+ZSWAP | They fight for pages |

**Implementation (persistent):**
```bash
# /etc/systemd/zram-setup.service
[Unit]
Description=ZRAM for LLM Inference
After=local-fs.target
[Service]
Type=oneshot
ExecStart=/bin/bash -c 'modprobe zram num_devices=1 && echo zstd > /sys/block/zram0/comp_algorithm && echo 8G > /sys/block/zram0/disksize && mkswap /dev/zram0 && swapon /dev/zram0 -p 100'
RemainAfterExit=yes
[Install]
WantedBy=multi-user.target
```
```ini
# /etc/sysctl.d/99-llm-inference.conf
vm.swappiness=100
```

**Sources:** zram-tuning (reapercanuk39), ChromeOS/Android strategies, Ariadne HPCA 2025.

### 3.2 THP (Transparent Huge Pages) → **madvise**

| Setting | Value | Why |
|---------|-------|-----|
| `/sys/kernel/mm/transparent_hugepage/enabled` | `madvise` | Only apps calling `madvise(MADV_HUGEPAGE)` get THP; avoids khugepaged stalls |
| `/sys/kernel/mm/transparent_hugepage/defrag` | `madvise` | Same rationale |
| Kernel cmdline | `transparent_hugepage=madvise` | Persistent across reboots |

**Impact:** Phoronix Linux 6.18 + AMD ZenDNN + Red Hat all confirm `madvise` optimal for LLM inference — eliminates synchronous compaction latency spikes during model load/KV growth.

### 3.3 MAX_LOADED_MODELS → **1 (not 2)**

| Config | Resident | Available | Swap | phi4-mini t/s |
|--------|----------|-----------|------|---------------|
| MAX=2 | 11.3 GB (2 models) | 1.9 GiB | 1.4 GiB (thrash) | 13.5 (with cold dips to 3.2-6.5) |
| **MAX=1** | **3.2 GB (1 model)** | **9.2 GiB** | **~0** | **13.4 (steady)** |

**Decision:** Single-channel 16GB cannot hold 2 residents + OS headroom. Swap thrash under MAX=2 causes cold-load t/s dips. Model-switch reload cost of MAX=1 is acceptable (~2-5s).

### 3.4 KV Cache Quantization → **q8_0 (now), q4_k (future)**

| KV Type | Resident Delta | Throughput | Quality (ppl Δ) | Status |
|---------|----------------|------------|-----------------|--------|
| f16 (default) | baseline 3.7 GB | 13.3 t/s | baseline | baseline |
| **q8_0** | **-0.5 GB → 3.2 GB** | **13.4 t/s** | **~0** | **DEPLOYED** |
| q4_k | ~-1 GB est. | TBD | <0.1 | Awaits upstream (KVQuant/VecInfer per-channel pre-RoPE) |

**Note:** q8_0 halves KV RAM with near-lossless quality. q4_k saves another ~0.4GB but needs per-channel quantization not yet in llama.cpp mainline.

### 3.5 Model Quantization → **Q4_K_M for all (sweet spot)**

| Model | Current Quant | Size | RAM | Notes |
|-------|---------------|------|-----|-------|
| phi4-mini | Q4_K_M | 2.5 GB | 7 GB | Primary fast model |
| qwen2.5-coder:7b | Q4_K_M | 4.7 GB | 7 GB | Code tasks |
| deepseek-r1:8b | Q4_K_M | 5.2 GB | 8 GB | Reasoning; **candidate for Q5_K_M** if tool-calls matter |
| Custom (code-reviewer, etc.) | Q4_K_M | 2.5-4.7 GB | 7-8 GB | FROM base models |

**Upgrade path:** deepseek-r1:8b → Q5_K_M (better tool-call reliability for agentic coding) if RAM allows.

---

## 4. BIOS CONFIGURATION (Verify on Next Reboot)

**Path:** Advanced → CPU Configuration / Power Management Control

| Setting | Target Value | Rationale |
|---------|--------------|-----------|
| Hyper-Threading | **Enabled** | Required for 8-thread config |
| Intel SpeedStep (EIST) | **Enabled** | Required for HWP |
| **Intel Speed Shift (HWP)** | **Enabled** | **Critical** — per-core P-states, hardware P-state selection |
| Turbo Mode | **Enabled** | Allows PL2 burst (115W, 28-56s) |
| C-States (C3/C6) | **Enabled** | Power savings at idle |
| Package C-State Limit | **Enabled (C6/C8/C10)** | Deep idle |
| Energy Performance Bias | **Performance** | Hardware default for EPP=performance |
| AVX Offset | **0** | Negative offset reduces AVX freq; keep 0 for inference |
| PL1 / PL2 | **View only** (usually locked) | PL1=45W, PL2=115W stock; if adjustable, don't exceed cooling |

**Fan Profile:** Already set to **Performance** in BIOS (user confirmed). MyASUS "Full Speed" mode also available.

**Note:** i7-13620H is 6P+4E (10C/16T), NOT i7-13700H (14C/20T). Previous gaming-expert agent had wrong CPU.

---

## 5. LINUX KERNEL / SYSCTL TUNINGS

### Applied / To Apply

| Parameter | Current | Target | Method |
|-----------|---------|--------|--------|
| `transparent_hugepage` | always | **madvise** | Runtime + `grub` cmdline |
| `thp defrag` | defer+madvise | **madvise** | Runtime |
| CPU governor | powersave + EPP=performance | **Keep** | Optimal for HWP |
| `vm.swappiness` | 60 | **100 (with ZRAM)** | High swappiness = push cold to fast ZRAM |
| ZRAM | none | **8GB zstd, pri=100** | systemd service + sysctl |
| `nohz_full` / `isolcpus` | none | **Don't** | Breaks Thread Director on hybrid |

### Grub Cmdline Addition
```bash
# /etc/default/grub
GRUB_CMDLINE_LINUX_DEFAULT="... transparent_hugepage=madvise"
# Then: sudo update-grub
```

### Runtime Verification Commands
```bash
# THP
cat /sys/kernel/mm/transparent_hugepage/enabled
cat /sys/kernel/mm/transparent_hugepage/defrag

# ZRAM
zramctl
swapon -s

# CPU
cat /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference
turbostat --Summary --show PkgWatt,CoreTmp,Avg_MHz,Busy% -i 2

# Memory
free -h
```

---

## 6. THERMAL / POWER MANAGEMENT

### Raptor Lake-H Specs (Intel Datasheet)
- **PL1 (sustained):** 45W (Base Power / TDP)
- **PL2 (burst):** 115W (Max Turbo Power)
- **Tau:** 28-56s (PL2 duration)
- **Tj max:** 100°C

### Current State
- `intel_pstate` + `powersave` governor + **EPP=performance** ✓
- `thermald` active (adaptive; watch for PL1=0 bug #550)
- Idle: ~63°C @ 400 MHz (normal for laptop silent mode)

### Validation Protocol (10-min Sustained)
```bash
# Terminal 1: Run continuous inference
while true; do curl -s http://localhost:11434/api/generate -d '{"model":"phi4-mini","prompt":"Continue the story:","stream":false}' >/dev/null; done

# Terminal 2: Log thermals
turbostat --Summary --show PkgWatt,CoreTmp,Avg_MHz,Busy% -i 2 > thermals.log
# Also: watch -n 2 sensors
```

**Pass criteria:** Avg P-core freq ≥ 3.5 GHz sustained, no throttle to < 3.0 GHz, pkg temp < 90°C.

### Optional Tools (If Thermal Headroom Exists)
- `intel-undervolt` — per-core/uncore undervolt (MSR writes, **caution**)
- `throttled` (erpalma) — restores PL1/PL2 if firmware resets them
- **BIOS PL1/PL2 unlock** — rarely available on laptops

---

## 7. OPEN WEBUI + OLLAMA INTEGRATION RULES

| Issue | Resolution |
|-------|------------|
| **Keep-alive override** | OWUI sends per-request `keep_alive` → overrides server. Set in UI per-model to `-1` or `30m`. |
| **Task model reload** | Title/tag generation uses different keep_alive → reloads model. Workaround: match OWUI = Ollama = same value. |
| **num_ctx trap** | OWUI pre-fills 2048. **Leave blank** to inherit `OLLAMA_CONTEXT_LENGTH=8192`. |
| **Connection pooling** | Random LB across multiple Ollama URLs. Single host = no benefit. |
| **Timeout** | Default 10s. Lower if multi-host for faster failover. |

---

## 8. BENCHMARK HISTORY & REGRESSION GUARDS

### Thread Sweep (Ground Truth)
| Threads | AllowedCPUs | phi4-mini t/s | Notes |
|---------|-------------|---------------|-------|
| 6 | 0-11 | 14.0 | Physical P-cores only |
| **8** | **0-11** | **14.4** | **PEAK** |
| 10 | 0-11 | 14.17 | +2 E-core threads |
| 12 | 0-11 | 13.88 | All HT |
| 6 | 0,2,4,6,8,10 | **~0.5** | **TRAP — spin-wait convoy** |

### Model Comparison (2026-09-08, 2 prompts, warm)
| Model | Avg t/s | Note |
|-------|---------|------|
| **phi4-mini** | **13.5** | Fastest, smallest |
| qwen2.5-coder:7b | 7.1 | Prompt 1 cold: 3.2 t/s |
| deepseek-r1:8b | 6.8 | Reasoning tokens; prompt 1: 6.5 t/s |

### Regression Tests (Run Before Any Config Change)
- [ ] `make bench MODEL=phi4-mini PROMPTS=3 WARM=1` → expect ~13.4 t/s
- [ ] `ollama ps` → resident ~3.2 GB, TTL ~29 min
- [ ] `free -h` → available > 8 GiB, swap ~0
- [ ] `cat /proc/<llama-pid>/cmdline` → verify `--cache-type-k q8_0 --flash-attn on -c 8192`

---

## 9. UPGRADE ROADMAP (Prioritized)

| # | Upgrade | Effort | Expected Gain | Prerequisites |
|---|---------|--------|---------------|---------------|
| 1 | **THP madvise** (sysctl + grub) | Low | Eliminate khugepaged stalls | None |
| 2 | **ZRAM 8GB zstd** (systemd + sysctl) | Low | Absorb peaks, zero swap I/O | None |
| 3 | **OWUI Keep Alive = -1** (UI) | Low (manual) | Fix 10-min TTL, prevent reloads | OWUI accessible |
| 4 | **BIOS verify** (Speed Shift, Turbo, EPP) | Low | Sustained turbo | Reboot |
| 5 | **10-min thermal bench** | Medium | Validate no throttle | turbostat |
| 6 | **Q5_K_M for deepseek-r1** | Low | Better tool calls | Pull model |
| 7 | **32GB DDR5-5600 dual-channel** | High ($$) | **+52-58% token gen** → ~20-22 t/s | Buy matched stick |
| 8 | **KV q4_k** (when upstream) | Medium | Save ~0.4 GB more KV | llama.cpp merge |

---

## 10. FILES & LOCATIONS (Source of Truth)

| File | Purpose | Updated |
|------|---------|---------|
| `docs/HARDWARE.md` | Canonical machine spec | 2026-09-08 |
| `docs/BENCHMARKS.md` | All benchmark data | 2026-09-08 |
| `docs/SYSTEM_GUIDE.md` | **This file — living guide** | 2026-09-08 |
| `.env.ollama` | Ollama env source of truth | 2026-09-08 |
| `/etc/systemd/system/ollama.service.d/override.conf` | Live Ollama config | 2026-09-08 |
| `docker-compose.yml` | OWUI stack (pinned v0.11.3) | 2026-09-08 |
| `Makefile` | Harness targets | 2026-09-08 |
| `docs/GNOSIS_USAGE.md` | Gnosis Lock usage (shell funcs + make) | 2026-09-09 |
| `~/.bash_aliases` | Funcs: `gnosis-lock`, `gnosis-stats`; alias `oc` | 2026-09-09 |
| `~/.config/opencode/opencode.jsonc` | OpenCode config (with MCP) | 2026-09-08 |
| `~/.config/opencode/agent/gaming-expert.md` | Sibling agent (CPU fixed) | 2026-09-08 |

---

## 11. KNOWN TRAPS (DO NOT REGRESS)

| Trap | Symptom | Root Cause | Prevention |
|------|---------|------------|------------|
| **P-core-only pin** | 0.5 t/s | llama-server 29 threads on 6 cores → spin-wait barrier convoy | Keep HT siblings (0-11) |
| **MAX_LOADED_MODELS=2** | Swap thrash, cold dips | 11.3 GB resident > 16GB single-channel headroom | Keep = 1 |
| **OWUI num_ctx=2048** | Silent truncation, tool-call failures | Overrides server 8192 | Leave unset in UI |
| **OWUI keep-alive default** | 10-min TTL despite server 30m | OWUI per-request override | Set per-model in UI |
| **ZRAM + ZSWAP together** | Memory pressure, conflicts | Both fight for pages | Pick ONE |
| **isolcpus/nohz_full** | Breaks Thread Director | Hybrid CPU needs HW-guided scheduling | Don't use |

---

## 12. SESSION LOG (Append-Only)

| Date | Session | Changes | Verified |
|------|---------|---------|----------|
| 2026-09-08 | Initial deep research + config | HARDWARE.md, BENCHMARKS.md, SYSTEM_GUIDE.md created; Ollama KV q8_0 + flash-attn applied; MAX_LOADED_MODELS=1; OWUI pinned v0.11.3; cold backup taken | Bench: 13.4 t/s, 3.2 GB resident, 9.2 GiB avail |
| 2026-09-08 | Exa research integration | MCP servers configured (websearch=Exa, context7, grep_app); BIOS/PL1/PL2/zram/THP deep research completed | Pending: THP/ZRAM apply, OWUI keep-alive UI, thermal bench |
| 2026-09-09 | Gnosis Lock Protocol v1.0 | 8-step ritual + evolution log + identity + hooks-handler built & tested; **`hooks` config key confirmed ABSENT in OpenCode v1.18 — but PLUGIN EVENTS are the correct hook mechanism (CORRECTED 2026-09-10: `session.*`, `experimental.session.compacting`, etc. — see WANDERGROUND_SPEC §10.1)**; **no CLI compaction exists — `/compact` is TUI-only**; shipped `~/.bash_aliases` (`gnosis-lock`, `gnosis-stats`, `oc` alias) + Makefile targets (`gnosis-lock`, `gnosis-stats`) + `docs/GNOSIS_USAGE.md`; stale `hooks` config and fake `oc compact`/`compact-gnosis` removed | Verified: ritual 8/8, funcs load in interactive shell, make targets run |
| 2026-09-09 | **Review fixes P0+P1** (system audit) | `git init` (git_state captures real data); ritual **Step 4 system_state rebuilt in Python + JSON-validated**, **new Step 9 logs SESSION_END** → ritual now **9-step**; `scripts/backup_harness.sh` + daily cron; instruction-stack de-dup (HARDWARE loaded once per project); SSOT sync (`api.exa.ai`, Big Pickle 1M block in HARDWARE/AGENTS); gnosis docs consolidated (STATE_FORMAT → Protocol Appendix A, OPENCODE_HOOKS → stub) | Verified: SESSION_END in stats (2→3 events), backup secret-clean, cron installed, 2 git commits |
| 2026-09-10 | **Federation LIVE — first contact** | omega-hub at `192.168.10.168:8016` connected from ASUS; full probe pass: HP stats, 28 entities, 10 GGUF models, hivemind history; **first-contact handoff completed by roc_racoon**; sovereignty ratio measured (21.6% local); outside-consultant report shipped (`11_CONSULTANT_REPORT.md` — 8 flaws incl. sovereignty contradiction, 45 stale handoffs, broken tool surfaces); comms contract v0.9 (`12_COMMUNICATION_PROTOCOLS.md`); client tool curation config; USB packet updated (identity 17) | Verified: probe battery all live; packet 14 docs/161 files; secrets clean |
| 2026-09-10 | **🧭 The WanderGround launches (Node 1 = exploration node)** | `docs/WANDERGROUND_SPEC.md` v1.0 (architecture, 5-domain registry, model-assignment matrix: local = light tasks only, cloud frontier via OpenCode Zen = synthesis); `~/WanderGround/` scaffolded + git repo `97de8bf`/`2a45792`; **`wander` CLI** (frictionless capture, `-d <domain>`, auto-triggers curator) + PATH wiring; **Knowledge Atlas** (`sqlite-vec` vec0 768-dim, `nomic-embed-text` embeddings verified, cosine search); **3D pipeline** (`project_umap_3d.py` — UMAP N≥8 / PCA fallback, KMeans, 100-sphere; graceful guard for scipy `k>=N` edge case); **offline Three.js constellation viewer** (`:8088`, vendored assets, click-to-open dossier); **background curator** (systemd user service + 30-min timer, verified exit 0 @ 223.8MB peak); MkDocs encyclopedia mirror (wiki-sync, 2.8M site builds clean); env decision: NO local deep-synthesis models — heavy work stays on OpenCode Zen (Nemotron 3 Ultra / MiMo V2.5 / Muse Spark / Big Pickle) | Verified: ingest → embed → archive → sqlite-vec → 3D → viewer JSON end-to-end with 3 live concepts; timer armed; site 200s served; secrets clean |

---

## 13. NEXT ACTIONS (Immediate)

Status verified 2026-09-10:
- ✅ **THP madvise — runtime applied** (`[madvise]` live). grub persistence pending confirm on next reboot.
- ⏳ **ZRAM 8GB zstd — NOT deployed** (zramctl empty). Still highest-priority RAM safety item.
- ⏳ **OWUI Keep Alive = -1** per model (UI manual step) — still pending.
- ⏳ **10-min thermal bench** with turbostat logging — still pending.
- ⏳ **BIOS settings verify** — still pending (next reboot).

New priority queue (federation era):
6. **HP response awaited** — `RESPONSE_FROM_HP.md` (F1–F7 in `10_ACTIONS_FOR_HP.md`); then ratify `12_COMMUNICATION_PROTOCOLS.md` with the council
7. **Apply client-side tool curation** on next session start (`ASUS-build-curated-tools.json` → `opencode.json` `tools` block) — cuts ~90 → ~50 hub tools
8. **Fix/flag the 3 broken hub surfaces** (HP-side, C1): `oracle_list_pillar_keepers`, library gemma_768 default, continuation lookup
9. **Sovereignty policy write-up** (per consultant S1/C4) — set per-task-class local/cloud targets; ASUS is 100% local exemplar
10. **Package refresh cadence** — after every meaningful session, re-sync USB packet evidence (identity/evolution/sessions)

---

---

## 14. MCP SERVER USAGE GUIDE (Exa, Context7, Grep.app)

### 14.1 Architecture Overview

OpenCode includes **three built-in remote MCP servers** (no config needed, always on):

| MCP Server | Based On | Purpose | Invocation |
|------------|----------|---------|------------|
| `websearch` | **Exa** | Neural web search — current info, code examples, company intel, people lookup | `use websearch` or automatic |
| `context7` | **Context7** | Official library docs — version-specific, hallucination-free | `use context7` |
| `grep_app` | **Grep.app (Vercel)** | GitHub code search — real production patterns across public repos | `use grep_app` or `use gh_grep` |

**Key insight:** These are HTTP remote MCPs. They add tools to the agent's context. For token budget management, only invoke when needed.

---

### 14.2 Exa Web Search (`websearch`)

**Configuration in `opencode.jsonc`:**
```json
{
  "mcp": {
    "websearch": {
      "type": "remote",
      "url": "https://api.exa.ai/mcp",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer {env:EXA_API_KEY}"
      }
    }
  }
}
```

**Environment variable (optional, for higher rate limits):**
```bash
export EXA_API_KEY="your_key_from_dashboard_exa_ai"
# Or in shell profile: echo 'export EXA_API_KEY=...' >> ~/.bashrc
```

**Available Tools:**
| Tool | Description | Best For |
|------|-------------|----------|
| `web_search_exa` | General web search, clean LLM-ready content | Current info, news, facts, broad discovery |
| `web_fetch_exa` | Full page content as clean markdown from known URL | Deep reading specific pages |
| `web_search_advanced_exa` | Advanced: domains, date ranges, categories, highlights | Precision research, source filtering |
| `agent_run` | Multi-step Exa Agent (async research, list-building) | Complex multi-query tasks |

**Prompt Patterns:**
```text
# Basic search
Search for the latest Ubuntu 26.04 kernel version. use websearch

# Code/API lookup
Find official llama.cpp KV cache quantization docs. use websearch

# Company/people research
Research Exa AI company and team. use websearch

# Advanced: constrain to domain
Search site:github.com/ggml-org/llama.cpp for "flash attention" implementation. use websearch

# With context7 combo
How to configure Cloudflare Workers KV? use context7
```

**Exa Search Types (via `type` param):**
| Type | Speed | Best For |
|------|-------|----------|
| `auto` | ~1s | Default, balanced |
| `instant` | ~250ms | Real-time apps |
| `fast` | ~450ms | Speed with quality |
| `deep-lite` | ~4s | Lightweight synthesis |
| `deep` | 4-15s | Multi-step reasoning |
| `deep-reasoning` | 12-40s | Hard research tasks |

**Rate Limits:** Free tier generous; `EXA_API_KEY` raises limits for production.

---

### 14.3 Context7 (`context7`)

**Configuration:**
```json
{
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp",
      "enabled": true
    }
  }
}
```
*(Optional: add `CONTEXT7_API_KEY` header for higher rate limits / private repos)*

**Purpose:** Fetches **version-specific, official documentation** directly into context. Eliminates hallucinated APIs and outdated examples.

**Invocation:**
```text
Create a Next.js middleware that checks for a valid JWT in cookies and redirects unauthenticated users to /login. use context7

Configure a Cloudflare Worker script to cache JSON API responses for five minutes. use context7

How to use drizzle-orm transactions with PostgreSQL? use context7

Show me the latest TanStack Query v5 migration guide. use context7
```

**Workflow:**
1. Write prompt naturally
2. Add `use context7`
3. Get working code with current APIs

**When to use:** Any library/framework question — React, Next.js, Cloudflare, Drizzle, TanStack, etc.

---

### 14.4 Grep.app (`grep_app` / `gh_grep`)

**Configuration:**
```json
{
  "mcp": {
    "grep_app": {
      "type": "remote",
      "url": "https://mcp.grep.app",
      "enabled": true
    }
  }
}
```
*(Naming it `gh_grep` allows `use gh_grep` in prompts)*

**Purpose:** Literal/regex code search across **millions of public GitHub repos**. Find real production patterns, not tutorials.

**Invocation:**
```text
# Pattern search
use gh_grep to search for "useTransition" usage in React 19 codebases. Find the 3 most common patterns.

# Library usage in production
search github via gh_grep for examples of "drizzle-orm" with "transaction" — show me how production codebases structure transactions.

# Framework patterns
use gh_grep to find how big public Tailwind v4 projects organize their theme tokens. Pull 3 examples I can browse.

# Compare patterns
use gh_grep to count occurrences of useFormState vs useActionState in production React codebases (Next.js 15+). Report the ratio and top 5 examples for each.

# Specific repo
use gh_grep to search for "createContext" in facebook/react repo.

# Authentication patterns
use gh_grep to find production NextAuth.js v5 implementations with credentials provider. Filter by TypeScript.
```

**Search Parameters (exposed via tool):**
| Parameter | Description |
|-----------|-------------|
| `query` | **Required** — literal code pattern (e.g., `useState(`, `export function`) |
| `language` | Comma-separated: `TypeScript,TSX`, `Python`, `Rust` |
| `repo` | Filter by repo: `facebook/react`, `vercel/next.js` |
| `path` | Filter by file path: `src/components/` |
| `match_case` | Case-sensitive (default: false) |
| `match_whole_words` | Whole words only (default: false) |
| `use_regexp` | Interpret query as regex (default: false) |

**Gotchas:**
- **Public only** — private repos invisible
- **Quality varies** — half GitHub is side projects; filter by popular repos
- **Literal/regex only** — not semantic "code that does X"; be precise
- **Intermittent availability** — `mcp.grep.app` sometimes unreachable; retry

**Best Queries:** Actual code syntax (`useEffect(() =>`, `async function`, `getServerSession(`) — NOT keywords (`react tutorial`, `best practices`, `how to use`).

---

### 14.5 MCP Management Commands

```bash
# List configured MCPs and auth status
opencode mcp list

# Authenticate OAuth-based MCPs (e.g., Sentry)
opencode mcp auth sentry

# Debug connection issues
opencode mcp debug <server-name>

# Remove stored credentials
opencode mcp logout <server-name>

# Add MCP interactively (wizard)
opencode mcp add
```

---

### 14.6 Token Budget Management

**Critical:** MCP servers add significant context tokens. From Scott Spence's optimization:

| Scenario | MCP Tools Tokens | Free Space |
|----------|------------------|------------|
| All MCPs enabled (empty convo) | 82k (41%) | 12k (5.8%) |
| Only `mcp-omnisearch` (consolidated) | 5.7k (2.8%) | 88k (44%) |

**Instruction stack cost (what we load every session, pre-MCP, measured
2026-09-09):** `AGENTS.md` (global+project) + `HARDWARE.md` + `SYSTEM_GUIDE.md`
+ `BENCHMARKS.md` ≈ **13.5K tokens** (~52KB). After the 1M Big Pickle raise this
is negligible; at a 200K window it is ~7% of context before anything happens —
keep the stack lean there, and note HARDWARE.md is loaded once per project
(de-duplicated 2026-09-09; the global config no longer also loads it).

**Best Practices:**
1. **Disable unused MCPs** in `opencode.jsonc`:
   ```json
   "tools": { "grep_app_*": false, "websearch_*": false }
   ```
2. **Enable per-agent** (disable globally, enable in agent config):
   ```json
   "tools": { "grep_app_*": false },
   "agent": { "my-research-agent": { "tools": { "grep_app_*": true } } }
   ```
3. **Invoke explicitly in prompt** (`use context7`) rather than relying on auto-invocation
4. **Consolidate similar tools** — one search tool with provider param vs multiple

---

### 14.7 Skill-Embedded MCPs (Advanced)

Skills can embed their own MCPs that **spin up on-demand** and **disappear when done**:

| Skill | Embedded MCP | Purpose |
|-------|--------------|---------|
| `playwright` | Browser automation | Screenshots, E2E tests, scraping |
| `git-master` | Git operations | Atomic commits, rebase surgery |

**Custom skills** at:
- Project: `.opencode/skills/*/SKILL.md`
- User: `~/.config/opencode/skills/*/SKILL.md`

Each skill defines its own MCP server definition + scoped permissions.

---

### 14.8 My Current Config (Verified)

```json
// ~/.config/opencode/opencode.jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["/home/xnai/Documents/Projects/omega-engine-alpha/docs/HARDWARE.md"],
  "agent": { "build": { "prompt": "{file:./prompts/build.md}" } },
  "mcp": {
    "websearch": { "type": "remote", "url": "https://api.exa.ai/mcp", "enabled": true, "headers": { "Authorization": "Bearer {env:EXA_API_KEY}" } },
    "context7": { "type": "remote", "url": "https://mcp.context7.com/mcp", "enabled": true },
    "grep_app": { "type": "remote", "url": "https://mcp.grep.app", "enabled": true }
  }
}
```

**To enable Exa API key:** `export EXA_API_KEY="..."` in shell profile or `.env` file.

**Test commands:**
```bash
opencode mcp list          # Should show all 3 connected
opencode run "Search for latest Rust 1.81 features. use websearch"
opencode run "How to use Axum extractors? use context7"
opencode run "Find production Axum middleware examples. use gh_grep"
```

---

## 15. P2P OMEGAVERSE FEDERATION (Node 0 ↔ Node 1)

### 15.1 Architecture Overview

| Node | Role | Hardware | Key Service |
|------|------|----------|-------------|
| **Node 0 (HP)** | Archival Bastion & Nexus | AMD Ryzen 7 5700U, 16GB DDR4-3200 dual-channel, Ubuntu 25.10 | `omega-hub` (FastMCP, 91 tools, Streamable HTTP on `:8016`) |
| **Node 1 (ASUS)** | Compute Vanguard | Intel i7-13620H, 16GB DDR5-5200 single-channel, Ubuntu 26.04 | Bare-metal Ollama, Open WebUI, OpenCode client |

### 15.2 Wire Protocols

| Layer | Transport | Binding | Status |
|-------|-----------|---------|--------|
| **1. Local LAN** | Streamable HTTP (`POST /mcp`) | `192.168.10.168:8016/mcp` | Phase 0 — Immediate |
| **2. Tailscale Mesh** | WireGuard via MagicDNS | `hp.tailnet:8016`, `asus.tailnet` | Phase 1 — Planned |
| **3. Redis Pub/Sub** | High-frequency heartbeats | Ephemeral event bus | Phase 2 — Future |

### 15.3 Hivemind Channel Partitioning

| Node | Agent Persona | Channel | Function |
|------|---------------|---------|----------|
| HP (Node 0) | `@roc_racoon` | `opencode` | Legacy mining, DHAL, hardware forensics |
| HP (Node 0) | `@kali` / `@makali` | `opencode` | Council synthesis, debut release, law |
| HP (Node 0) | `@grokster` | `grokster` | OpenCode CLI internals, cross-platform KB |
| ASUS (Node 1) | `asus_build` | `opencode-asus` | Bare-metal compile, Ollama benchmarking |
| ASUS (Node 1) | `asus_plan` | `opencode-asus` | Hardware profiling, local workload planning |

### 15.4 4-Way Handoff Contract

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

### 15.5 ASUS OpenCode Config for Federation

```json
{
  "mcp": {
    "omega-hub": {
      "type": "remote",
      "url": "http://192.168.10.168:8016/mcp",
      "enabled": true
    }
  },
  "provider": {
    "opencode": {
      "models": {
        "big-pickle": {
          "limit": { "context": 1000000, "input": 950000, "output": 64000 }
        }
      }
    }
  }
}
```

### 15.6 Connectivity Verification

```bash
# Test LAN connectivity
~/test_connection.sh

# Ceremonial first contact
python3 ~/hivemind_first_contact.py

# Expected: Health check + MCP handshake + 91 tools + SSE stream
```

### 15.7 Migration Status

| Component | HP (Node 0) | ASUS (Node 1) | Status |
|-----------|-------------|---------------|--------|
| `omega-hub` | ✅ Running (91 tools) | — | Source |
| OpenCode | ✅ Custom agents, skills | ✅ Fresh + USB config | Connected |
| MCP Servers | 5 (Exa, Firecrawl, omega-hub, SearXNG, parallel-search) | 7 (Exa, Context7, Grep.app, omega-hub, SearXNG, Firecrawl*) | Synced |
| Git Repo | ✅ SSOT | ⏳ Pending clone | Phase 0 |

*Firecrawl disabled on ASUS; Exa `agent_run` covers deep scraping.

---

*This guide is the single source of truth. Every tuning decision traces to a benchmark, a kernel doc, an Intel datasheet, or a ggml issue. When in doubt, re-bench.*| 2026-09-10 | **Deep research pass — definitive corrections (WanderGround)** | **OpenCode hooks CORRECTED:** plugin event system IS the hook mechanism (`session.created/idle/compacted`, full `session.next.*`, `experimental.session.compacting`) — verified in local 1.18.30 types; shipped `~/.config/opencode/plugins/gnosis-leash.js` (timeline + compaction/system-prompt injection; loads clean); **MemPalace v3.9.0 online**: `sqlite_exact` backend + hermetic `minilm` ONNX (SHA256-verified pre-seed, flaky-link safe) — 20 files → 62 drawers, hybrid search verified; `mempalace` stdio MCP wired into opencode.json; mining hygiene via `.gitignore` (SKIP_DIRS + vendor/site/docs/mempalace exclusions); **Zen privacy tier** documented (free tiers collect data — `big-pickle`, `mimo-v2.5-free`, `nemotron-3-ultra-free`, `muse-spark-*-contributor-free`; paid = zero-retention); **sqlite-vec corrected** (`distance_metric=cosine` + `k = ?` KNN syntax); **systemd linger enabled** (timer survives logout); **anyio code-quality standard** added (`docs/CODE_QUALITY.md` — absolute anyio async wiring, no bare asyncio/trio, no torch); **eyes-on-machine tooling** (`ey`, `withey` pre/post snapshots) | Verified: mine exit 0 in ~2s (62 drawers/7 rooms); MemPalace search returns correct rooms; `opencode serve` starts with plugin clean; Linger=yes; model tarball SHA256 OK |

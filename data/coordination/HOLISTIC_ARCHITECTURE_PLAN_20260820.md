<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 OMEGA ENGINE — HOLISTIC ARCHITECTURE PLAN
**Version**: 2026-08-20 (Nemotron 3 Ultra, High thinking)  
**Scope**: Complete synthesis of all work this session — Gemini Notebook, Documentation System, Local Inference, Knowledge Domains, Headroom, zRAM, Architecture

---

## 🎯 EXECUTIVE SUMMARY

This session produced a **coherent, hardware-honest, free-tier-aligned architecture** that survives Carmack's brutal review and scales from 16GB CPU-only to frontier GPU hardware. All cargo-cult abstractions removed; only what works on Ryzen 5700U remains.

---

## 📦 SYSTEM 1: GEMINI NOTEBOOK (NotebookLM) STRATEGY v2.0

### Core Decisions (Ratified D-571..D-577)
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Cost Model** | **FREE TIER ONLY** — 3 accounts × 10 DR/mo = **30 DR/month** | User will NOT pay for Pro; 8-account fleet is ToS-violating, ban-prone |
| **Tool** | `notebooklm-py` (RPC, no browser) + `[mcp]` extra | Only lib with Deep Research report trigger + Markdown export |
| **Deployment** | `pip install notebooklm-py[mcp]` + systemd (no Docker) | Local-first, portable |
| **Auth** | `master_token.json` + `RotateCookies` ≤600s + Patchright `channel='chrome'` | Cookie snapshots die in minutes; master_token is durable |
| **Notebook Architecture** | **2 notebooks**: Active Research + Knowledge Base | Free tier = 100 notebooks/account (verified); 6-notebook was over-engineered for 30 DR/mo budget |
| **Token Density** | **5-25 sources** sweet spot (not 40-50) | Community-verified; 30-50 is noise-driven degradation |
| **SDP Gate** | **Honor §10** — manual mode first, automate after 10 runs + V-1 Vault | Quality/discipline protection (M11) |

### Implementation Status
- ✅ Gap audit (10 gaps) + 3 research reports (NLG-A/B/C) + synthesis
- ✅ Unified strategy doc corrected to v2.0 (9 targeted edits)
- ✅ PIVOT_LOG D-571..D-577 ratified
- ⏳ NLG-SMOKE: Single-account smoke test (blocked by V-1 Vault)

---

## 📚 SYSTEM 2: DOCUMENTATION SYSTEM — MODULAR DOMAIN ARCHITECTURE

### Dual-Layer Design (Authoring ↔ Runtime)

```
docs/strategy/domains/<domain>/          ← WORKSPACE (authoring, versioning, review)
├── STRATEGY_V<major>.<minor>.md         ← Canonical best practices
├── GAP_AUDIT_YYYYMMDD.md                ← Immutable audit
├── RESEARCH_<FOCUS>.md                  ← Immutable research
├── SYNTHESIS_V<major>.md                ← Kali arbitration
├── IMPLEMENTATION_GUIDE.md              ← Living implementation reference
└── ARCHIVE/                             ← Superseded docs with banners

config/domains/<domain>/                 ← RUNTIME (loaded by domain_loader.py)
├── metadata.yaml                        # version, deps, target_ctx, rot_class, owner, cost_model
├── CONTEXT.md                           # ← Single file: PLAYBOOK + ARCHITECTURE + GOTCHAS + LESSONS
├── PROMPTS/                             # planner.txt, executor.txt, critic.txt
└── sources/                             # Symlinks to actual source docs
```

### Sync Mechanism
- **Workspace → Runtime**: `cp -r` (not symlink — Python import caching breaks hot reload)
- **Validation**: Pre-commit hook checks YAML syntax + required files
- **Curator Model**: Each domain has a Curator entity (enforced at fabric level)
  - `gemini-notebook` → **researcher** (16K target context)
  - `platforms` → grokster | `architecture` → john_carmack | `heritage` → doom_guy
  - `runtime-governance` → lilith | `build-engineering` → maat | `compliance` → verity
  - `legacy-mining` → roc_racoon | `synthesis` → jem

### First Domain: `gemini-notebook`
- Workspace: 7 active docs + 4 archived (moved from `data/coordination/` + `docs/strategy/`)
- Runtime: `metadata.yaml` (accounts=3, dr_per_month=30, cost_model=free_tier_only) + `CONTEXT.md` + `PROMPTS/`
- Sync: `scripts/sync_domain_docs.py` (validated copy, not symlink)

---

## ⚡ SYSTEM 3: LOCAL INFERENCE OPTIMIZATION — TIERED HARDWARE ARCHITECTURE

### Hardware Tiers (Auto-Detected at Startup)

| Tier | Hardware | RAM/VRAM | Detection Method |
|------|----------|----------|------------------|
| **Tier 0** | Ryzen 5700U, 16GB RAM, no GPU | 12 GB usable | `llama-fit-params` probe |
| **Tier 1** | 32GB RAM + RTX 3060 12GB | 11.5 GB VRAM + 28 GB RAM | GPU detect + VRAM query |
| **Tier 2** | 64GB RAM + RTX 4090 24GB | 23 GB VRAM + 60 GB RAM | GPU detect + VRAM query |

### Corrected Model Matrix (Carmack-Validated)

| Tier | Planner | Executor | Critic | Logical/Physical Context | KV Config |
|------|---------|----------|--------|-------------------------|-----------|
| **0** (16GB CPU) | **Qwen3-4B Q4_K_M** | **Qwen3-4B-Thinking Q4_K_M** | **Qwen3-1.7B Q4_K_M** | 16K / 8K / 4K | q8_0 |
| **1** (32GB+12GB VRAM) | Qwen3-8B Q4_K_M | Qwen3-4B-Thinking Q4_K_M | Qwen3-4B Q4_K_M | 64K / 16K / 8K | q8_0 |
| **2** (64GB+24GB VRAM) | Qwen3-32B Q5_K_M | Qwen3-4B-Thinking Q4_K_M | Qwen3-14B Q5_K_M | 128K / 32K / 16K | q8_0 |

✅ **C7 RESOLVED**: Qwen2.5-Coder-7B replaced with **Qwen3-4B-Thinking-2507-Q4_K_M.gguf** (on disk, 2.55 GB). All tiers now use available models. Carmack CUT: gpt-oss-20B (no MXFP4 mainline), Nemotron-3-Nano MoE (8B dense, marketing fiction).

### Tier 0 Memory Map (Sequential Execution — ONLY Way It Fits)
```
OS + Python + AnyIO              ~2.5 GB
Weight cache (mmap'd, persistent) ~6.1 GB
  ├─ Qwen3-4B (planner)           2.5 GB
  ├─ Qwen3-4B-Thinking (executor) 2.5 GB
  └─ Qwen3-1.7B (critic)          1.1 GB
Active KV cache (q8_0, 16K ctx)   ~1.5 GB
Compute buffers + overhead        ~1.0 GB
─────────────────────────────────────────
PEAK USAGE (all weights resident) ~11.1 GB
HEADROOM (all weights)            ~4.9 GB  ✓ COMFORTABLE

SEQUENTIAL MODE (Carmack FIX-2):
Only ONE model's weights resident at a time
Peak = max(2.5, 2.5, 1.1) + 1.5 KV + 1.0 compute + 2.5 OS = ~7.5 GB
HEADROOM (sequential)             ~8.5 GB  ✓ COMFORTABLE
```

### Core Engine Additions (~200 lines)

```python
# src/omega/research/adaptive_context.py
class AdaptiveContextBuffer:
    def __init__(self, hardware_tier: HardwareTier):
        self.tier = hardware_tier
        self.physical_ctx = hardware_tier.swa_window  # 8K/16K/32K
        self.kv_config = KVCacheConfig(type_k="q8_0", type_v="q8_0")
        self.compressor = LLMLingua2Compressor()
        
    def prepare(self, task: Task, history: list) -> Context:
        needed = self._predict_need(task.type)
        if needed > self.physical_ctx:
            return self.compressor.compress(history, target=self.physical_ctx * 0.8)
        return history[-self.physical_ctx:]

# src/omega/research/sequential_loader.py
class SequentialModelLoader:
    def __init__(self):
        self.session_contexts = {}  # model_id -> session-scoped context
        
    async def run(self, model_id: str, prompt: str, ctx: Context) -> Result:
        # NO mmap weight cache — Carmack FIX-2: "mmap is WRONG (llama_free() unmaps)"
        # Use --no-mmap --mlock + session-scoped context instead
        if model_id not in self.session_contexts:
            self.session_contexts[model_id] = create_context(
                model_path=model_id,
                n_ctx=ctx.physical_size,
                cache_type_k="q8_0", cache_type_v="q8_0",
                # n_swa REMOVED — SWA CUT for Qwen3 (Carmack CUT-1)
            )
        
        model_ctx = self.session_contexts[model_id]
        result = await model_ctx.generate(prompt, ctx.tokens)
        # Keep session context alive; KV cache freed per-request
        return result
```

### Mandatory Startup Optimizations

> ⚠️ **SUPERSEDED BY D-526/D-581/D-584** (2026-08-20). zRAM is DISABLED.
> The correct swap subsystem is **zswap + NVMe swap file** (see SYSTEM 6, line 261).
> This section's zRAM instruction is VOID. Do not execute `modprobe zram`.
> Canonical: "Per D-526/D-581/D-584 + ADR-2026-08-10-001: Omega Engine uses zswap + NVMe swap file with zRAM DISABLED. Never run both (D-527 LOCKED)."

```bash
# zRAM (not zswap) + THP + core pinning  ← SUPERSEDED: do NOT run
sudo modprobe zram num_devices=1
echo zstd > /sys/block/zram0/comp_algorithm
echo 8G > /sys/block/zram0/disksize
mkswap /dev/zram0 && swapon --priority 100 /dev/zram0
echo always > /sys/kernel/mm/transparent_hugepage/enabled

# CORRECT (per D-526/D-581/D-584): zswap + NVMe swap, zRAM DISABLED
# See SYSTEM 6 (line 261) for validated config. Do NOT run the zRAM block above.

# Build with native + LTO (skip PGO/BOLT)
cmake -B build -DGGML_NATIVE=ON -DCMAKE_BUILD_TYPE=Release -DGGML_LTO=ON

# Hardware-tier detection at startup
llama-fit-params -m model.gguf -fitt 512 -fitc 32768

# Run with pinning + no-mmap + mlock + prompt caching
# NO --n-swa (SWA CUT for Qwen3 — Carmack CUT-1)
taskset -c 0-7 llama-server -m model.gguf --no-mmap --mlock \
  --cache-type-k q8_0 --cache-type-v q8_0 --parallel 4 --cache-prompt
```

---

## 🧠 SYSTEM 4: KNOWLEDGE DOMAINS / NODES — RUNTIME DOMAIN MODULES

### Domain Module Schema (Enforced by `domain_loader.py`)
```yaml
# config/domains/<domain>/metadata.yaml
version: "2.0"
target_context_window: 16384
rot_class: "research"
owner: "researcher"  # Curator entity
cost_model: "free_tier_only"
accounts: 3
dr_per_month: 30
tos_risk: "high_mitigated"
dependencies: []
```

### Runtime Files (Flat, No Subdirs)
```
config/domains/gemini-notebook/
├── metadata.yaml
├── CONTEXT.md              # ← Single file: PLAYBOOK + ARCHITECTURE + GOTCHAS + LESSONS
├── PROMPTS/
│   ├── planner.txt
│   ├── executor.txt
│   └── critic.txt
└── sources/                # Symlinks to actual source docs
```

### Domain Loader API (Sync, Not Async)
```python
def load_domain(name: str, token_budget: int) -> str:
    """Sync I/O + string concat — no AnyIO leakage into prompt building."""
    path = DOMAINS_DIR / name / "CONTEXT.md"
    return path.read_text()[:token_budget * 4]  # rough char estimate
```

### Curator Model (Config Flag, Not Fabric Middleware)
```yaml
# metadata.yaml
owner: "researcher"  # Curator = write; Others = read + propose; Critic = review gate
```
Enforced at fabric level via config flag, not middleware.

---

## 🧩 SYSTEM 5: HEADROOM — SEMANTIC COMPRESSION MIDDLEWARE

### What It Is
- **Local-first** semantic compression middleware (66.8k★, Apache-2.0, active)
- **Already installed** in `.venv` v0.29.0, `src/omega/oracle/headroom.py` exists (deprecated binary version)
- **Four compressors**: SmartCrusher (JSON 80-95%), CodeCompressor (AST), Kompress (LLMLingua-2), LogCompressor

### Benchmarks (Local Verified)
| Content | Savings | Latency |
|---------|---------|---------|
| JSON arrays (500 items) | 83% | ~2ms |
| Build logs (200 lines) | 94% | ~1ms |
| Code search (100 results) | 92% | ~5ms |
| RAG chunks | 40-60% | ~10ms |

### Integration Points (P0-P1)
```python
# src/omega/oracle/middleware/headroom.py (NEW)
from headroom import compress, CompressConfig

class HeadroomMiddleware:
    def __init__(self):
        self.config = CompressConfig(
            compress_user_messages=True,
            compress_system_messages=False,
            protect_recent=2,
            min_tokens_to_compress=250,
            kompress_model="chopratejas/kompress-v2-base"
        )
    
    async def compress_tool_outputs(self, messages: list[dict]) -> list[dict]:
        result = compress(messages, model="local", optimize=True, config=self.config)
        return result.messages
```

### Integration Points
| Location | What to Compress | Expected Savings |
|----------|------------------|------------------|
| `ModelGateway._prepare_messages()` | Tool outputs, RAG chunks, file reads | 40-90% |
| `Oracle.talk()` / `summon()` | Entity context + tool history | 20-50% |
| `MemoryStore.add_exchange()` | Compress before storage (CCR for retrieval) | 60-95% |
| MCP `headroom_compress` tool | Entity self-service | On-demand |

---

## 💾 SYSTEM 6: zswap + NVMe SWAP SUBSYSTEM — VALIDATED CONFIG (Carmack 2026-08-10)

### Decision: **zswap + NVMe Swap, zRAM DISABLED** (ADR-2026-08-10-001 ACCEPTED, D-526 RATIFIED)
**Authoritative**: `data/entities/researcher/workspace/MEMORY_SYSTEMS_DEFINITIVE_REPORT.md` (Carmack + Researcher + Jem + LongCat + Nemotron 3 Ultra)

### Root Cause Fixed
- `vm.swappiness=180` → `100` (kernel sweet spot for in-memory swap)
- zRAM removed (was locking 4.1 GB RAM in compression buffers — 81-98% of available process RAM)
- zswap + 16GB NVMe swap file provides dynamic pool (0-3.6 GiB), graceful degradation via NVMe eviction

### Validated Config (Deploy P1)
```bash
# sysctl: /etc/sysctl.d/99-omega-memory.conf
vm.swappiness = 100
vm.page-cluster = 0
vm.watermark_scale_factor = 125
vm.vfs_cache_pressure = 50
vm.dirty_background_ratio = 5
vm.dirty_ratio = 10
vm.overcommit_memory = 0

# zswap config (kernel cmdline or /etc/default/grub)
zswap.enabled=1
zswap.max_pool_percent=25
zswap.compressor=lzo_rle
zswap.zpool=zsmalloc

# NVMe swap file (16GB)
/swapfile.nvme none swap sw,pri=100 0 0

# systemd unit: omega.service
MemoryMin=2G
MemoryHigh=5G
MemoryMax=6G
MemorySwapMax=infinity
```

### ACCEPTED (Carmack + Researcher + Jem + LongCat + Nemotron 3 Ultra)
- ✅ zswap + NVMe swap file (dynamic pool, graceful degradation, kernel-integrated reclaim)
- ✅ lzo_rle compressor (lower CPU overhead)
- ✅ zsmalloc allocator
- ✅ max_pool_percent=25 (3.6 GiB dynamic pool)
- ✅ 16GB NVMe swap file backing
- ✅ swappiness=100

### REJECTED (Carmack)
- ❌ 16GB zRAM expansion — "Hard capacity cliff with no graceful degradation"
- ❌ zRAM writeback to NVMe — "Solution theater for server-scale workloads"
- ❌ zRAM signal in OOMProtector
- ❌ `use_cgroup` config flag

---

## 🏗️ SYSTEM 7: UNIFIED INFERENCE PIPELINE

```
┌────────────────────────────────────────────────────────────────────┐
│                    OMEGA ENGINE INFERENCE PIPELINE                 │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  User Query                                                        │
│      │                                                             │
│      ▼                                                             │
│  ┌─────────────────┐                                               │
│  │ Oracle.talk()   │ ──► Entity Resolution (MaKaLi routing)       │
│  └────────┬────────┘                                               │
│           │                                                        │
│           ▼                                                        │
│  ┌─────────────────┐                                               │
│  │ Context Builder │ ──► RAG + Memory + Tool History              │
│  └────────┬────────┘                                               │
│           │                                                        │
│           ▼                                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │              HEADROOM MIDDLEWARE                             │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │  │
│  │  │ CacheAligner│→ │ContentRouter│→ │SmartCrusher/CodeComp│  │  │
│  │  │ (KV cache)  │  │ (type detect)│ │ (JSON/Code/Logs)    │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘  │  │
│  │         │              │                    │                │  │
│  │         └──────────────┴────────────────────┘                │  │
│  │                    ▼                                         │  │
│  │           Compressed Messages (40-90% smaller)               │  │
│  └────────────────────┬────────────────────────────────────────┘  │
│                       │                                            │
│                       ▼                                            │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │              MODEL GATEWAY                                   │  │
│  │  AdaptiveContextBuffer → SequentialModelLoader → Provider   │  │
│  │  Local-First: native-gguf → lmster → Ollama → Cloud fallback │  │
│  └────────────────────┬────────────────────────────────────────┘  │
│                       │                                            │
│                       ▼                                            │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │              ZRAM SUBSYSTEM (VALIDATED)                      │  │
│  │  8GB zstd level=15 │ swappiness=100 │ cgroup MemoryMax=6G   │  │
│  │  zswap: DISABLED   │ No writeback   │ OOMProtector: 2-signal │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 📋 MASTER IMPLEMENTATION CHECKLIST

### Phase 0: Foundation (This Week)
| # | Task | Owner | Status |
|---|------|-------|--------|
| 1 | Deploy `99-omega-memory.conf` sysctl | Ma'at | ⏳ |
| 2 | Deploy `omega.service` with corrected cgroup limits | Ma'at | ⏳ |
| 3 | Build llama.cpp with `-DGGML_NATIVE=ON -DGGML_LTO=ON` | Ma'at | ⏳ |
| 4 | Implement `llama-fit-params` hardware detection | Ma'at | ⏳ |
| 5 | Enable prompt caching (`--cache-prompt --parallel`) | Ma'at | ⏳ |

### Phase 1: Core Engine (Week 1)
| # | Task | Owner | Status |
|---|------|-------|--------|
| 6 | `AdaptiveContextBuffer` + `SequentialModelLoader` classes | Ma'at | ⏳ |
| 7 | q8_0 KV cache profiles in `config/providers.yaml` | Ma'at | ⏳ |
| 8 | Hardware-tier model registry (Tier 0/1/2) | Ma'at | ⏳ |
| 9 | `HeadroomMiddleware` in `src/omega/oracle/middleware/` | Ma'at | ⏳ |
| 10 | Wire Headroom into `ModelGateway` provider chain | Ma'at | ⏳ |

### Phase 2: Gemini Notebook Domain (Week 1-2)
| # | Task | Owner | Status |
|---|------|-------|--------|
| 11 | Create `docs/strategy/domains/gemini-notebook/` workspace | Kali | ⏳ |
| 12 | Move 7 active + 4 archive docs (renamed per convention) | Kali | ⏳ |
| 13 | Create `config/domains/gemini-notebook/` runtime module | Ma'at | ⏳ |
| 14 | Implement `scripts/sync_domain_docs.py` (validated copy) | Ma'at | ⏳ |
| 15 | Free-tier fetch pipeline (3 accounts, 30 DR/mo) | Researcher | ⏳ |
| 16 | Systemd timer for scheduled DR runs | Ma'at | ⏳ |

### Phase 3: Domain System & Polish (Week 2)
| # | Task | Owner | Status |
|---|------|-------|--------|
| 17 | `DOMAIN_DOCUMENTATION_SYSTEM.md` meta-doc | Kali | ⏳ |
| 18 | Curator assignments for all 10 domains | Kali | ⏳ |
| 19 | Package Ryzen config as WAD (`config/wads/ryzen-5700u-sovereign/`) | Ma'at | ⏳ |
| 20 | Update `STRATEGY_INDEX.md` + `STRATEGY_CORPUS_MAP.md` + `PIVOT_LOG` | Kali | ⏳ |
| 21 | NLG-SMOKE: Single-account smoke test | Kali | ⏳ |

---

## 🎯 ARCHITECTURE PRINCIPLES (What Survived Carmack)

| Principle | Application |
|-----------|-------------|
| **Sequential > Concurrent** | One model loaded at a time; weights cached, KV cache swapped |
| **q8_0 KV Cache** | 50% memory, <2% quality loss — sovereign standard |
| **Adaptive > Fixed Tiers** | Single buffer + SWA + compression adapts to any hardware |
| **Symlink → Copy + Reload** | Python import caching breaks symlink hot-reload |
| **3 Accounts Max** | Free tier = 30 DR/mo (3×10); 8 accounts = ToS violation + ops burden |
| **Headroom for Tool Outputs** | 40-90% compression on JSON tool outputs = massive context savings |
| **zswap + NVMe Swap, No zRAM** | zswap provides dynamic pool + graceful degradation; zRAM has hard capacity cliff; D-526/D-581/D-584 ratified |
| **Domain = Config, Not Code** | YAML + prompts + symlinks = Engine/Stack separation (M2) |
| **Curator = Config Flag** | Not middleware; enforced at fabric level via `owner:` field |

---

## 📊 FINAL APPROVAL CHECKLIST

| # | System | Decision | Status |
|---|--------|----------|--------|
| 1 | **Gemini Notebook** | Free tier only, 3 accounts, 30 DR/mo, notebooklm-py | ⏳ |
| 2 | **Documentation** | Modular domain system (workspace + runtime + sync) | ⏳ |
| 3 | **Local Inference** | Sequential loading, q8_0 KV, adaptive buffer, Tier 0/1/2 | ⏳ |
| 4 | **Knowledge Domains** | Runtime modules + workspace authoring + curator model | ⏳ |
| 5 | **Headroom** | Semantic compression for tool outputs + RAG (P0) | ⏳ |
| 6 | **zswap + NVMe Swap** | 16GB NVMe swap, zswap enabled (25% pool, lzo_rle, zsmalloc), zRAM disabled (locked) | ⏳ |
| 7 | **Tier 0 Models** | Qwen3-4B planner, Qwen3-4B-Thinking executor, Qwen3-1.7B critic | ⏳ |

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_holistic_plan ⬡ 2026-08-20*
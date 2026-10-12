---
schema_version: "1.0"
document_type: research
document_id: R_KNOWLEDGE_GAP_WEB_RESEARCH_20260922
title: "Web Research: All Open Knowledge Gaps (2026-09-22)"
status: ACTIVE
version: "1.0.0"
date: "2026-09-22"
owner: makali_fusion
tags: [knowledge-gaps, research, web-research, zswap, qwen3, gemini-notebook, warp, opencode]
priority: P1
depends_on: [data/coordination/GAP_REGISTRY.json]
blocks: []
acceptance_gates:
  - "All researchable gaps from GAP_REGISTRY covered with 2026-current sources"
cross_references:
  - data/coordination/GAP_REGISTRY.json
  - docs/sprints/current/KNOWLEDGE_GAP_CLOSURE.md
---

# 🔱 Web Research: All Open Knowledge Gaps

**AP Token**: `AP-KNOWLEDGE-GAP-WEB-RESEARCH-v1.0.0`
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ RESEARCH ⬡ 2026-09-22

**Research method**: T1 websearch (parallel-search MCP) — 6 batched queries across
all researchable gap themes, cross-referenced against GAP_REGISTRY.json (89 gaps,
38 open/partial). Implementation-only gaps (DP/DS/KD series) noted but not
web-researchable.

---

## §1 ZS-1/ZS-2 — zswap + 16GB NVMe Swap (RESOLVED, confirms D-526/D-527)

**Sources**: kernel.org zswap docs (next/v6.16), kernel-internals.org (2026-09-20), myunix.org (2026-08-24)

| Finding | Detail |
|---------|--------|
| **zsmalloc is the ONLY zswap pool backend** in current kernels | zbud/z3fold removed; `CONFIG_ZSWAP` auto-selects `CONFIG_ZSMALLOC` |
| **zswap + zram together = double compression** | "Choose one: zswap (NVMe/SSD swap) or zram (no swap device)" — confirms D-527 (never both) |
| **max_pool_percent** | Default 20; 25-40 recommended for fast-RAM/slow-swap; kernel-internals example: `zswap.max_pool_percent=25` |
| **Compressor** | lzo_rle or zstd both valid; kernel-internals example uses zstd |
| **Newer tuning knobs** | `shrinker_enabled` (memory pressure shrinker), `accept_threshold_percent` (hysteresis, e.g. 70-80) |
| **cgroup control** | `memory.zswap.max` per-cgroup limit; `memory.zswap.writeback=0` disables writeback |
| **Swap sizing** | 16GB NVMe swap file confirmed viable; zswap reduces SSD writes 2-5x |

**ZS-1/Zs-2 verdict**: Config `zswap.enabled=1 zswap.compressor=zstd zswap.max_pool_percent=25` + 16GB swap file is CONFIRMED current best practice for desktop NVMe. Add `shrinker_enabled=Y` + `accept_threshold_percent=70` as hardening.

---

## §2 LI-4 — Qwen3 Tier-0 Model Matrix (RESOLVED)

**Sources**: localmodel.run (2026-06-14), llmhardware.io (2026), HuggingFace GGUF repos

| Model | Q4_K_M GGUF | RAM @4k ctx | RAM @32k ctx | Notes |
|-------|-------------|-------------|--------------|-------|
| **Qwen3-1.7B** | 1.28 GB | ~2.4 GB | ~4.6 GB | 32k native ctx; 128k needs ~12.1 GB |
| **Qwen3-4B** | 2.5 GB | ~3.8 GB | ~5.6 GB | 32k native ctx; Q8_0 = 5.6 GB @4k |
| **Qwen3-4B-Thinking** | ~2.5 GB | ~3.8 GB | ~5.6 GB | Built-in CoT; **2-3x more tokens per response** |

- Qwen3-4B Q4: ~3 GB minimum, runs CPU-only
- llama.cpp native Qwen3 support since April 2025
- **LI-4 implication**: On ~8GB free RAM (Ryzen 5700U), Qwen3-1.7B Q4 @32k ctx (~4.6GB) is the safe always-on worker; Qwen3-4B Q4 @8-16k ctx (~4-5GB) fits with tight headroom. Thinking variant costs 2-3x tokens — budget accordingly.

---

## §3 LI-3 — llama.cpp Memory Fitting (RESOLVED)

**Sources**: sumguy.com KV cache quantization (2026-09-05), micrologics.org (KV math), papajo/llama-cpp-projects, dev.to (2026-07-28)

- **KV cache formula**: `M_kv = 2 × L × H × D × S × P` (layers × KV heads × head_dim × ctx × bytes)
- **KV cache quantization**: `--cache-type-k q8_0 --cache-type-v q8_0` (-ctk/-ctv) → **-50% cache**; q4_0 → -75%. "Free extra 2-3GB headroom"
- **mmap behavior**: GGUF is memory-mapped, NOT loaded upfront — pages load on demand; model load time <1s; cold pages evicted under pressure. **Critical for SequentialModelLoader design (LI-2): mmap means "keep context alive" ≠ "keep weights resident"**
- **Fit tools**: KV Cache Visualizer & Memory Calculator (papajo), GGUF Model VRAM Calculator (DavidAU HF space), llama_cpp_manager (VRAM estimation)
- **LI-3 implication**: llama-fit-params should compute `weights + KV(ctx, quant) + ~0.8GB overhead` vs available RAM; use q8_0 KV cache as default for CPU-only.

---

## §4 GN-1/GN-3/GN-4/R38 — Gemini Notebook (ex-NotebookLM) (RESOLVED + CORRECTION)

**Sources**: notebooklm-py GitHub/PyPI (18.9k stars, MIT), Google Gemini Notebook help, felloai (2026-07-25), glasp (2026-09-17)

### ⚠️ CRITICAL CORRECTION to GN-3
- **Free tier Deep Research = 10 runs/MONTH** (not 30) — verified across notebooklm-py quota-limits.md + Google support + 3 independent 2026 sources
- **Sept 2, 2026: NEW compute-based usage limits** — quota refreshes every 5 hours until weekly limit; limits factor prompt complexity, models used, chat length

### Free tier (Standard) limits
| Feature | Limit |
|---------|-------|
| Notebooks | 100/user |
| Sources | 50/notebook (500K words or 200MB each) |
| Chats | 50/day |
| Deep Research | **10/month** |
| Audio/Video Overviews | 3/day each |
| Reports/Flashcards/Quizzes/Mind Maps | 10/day each |

### notebooklm-py (the library GN-1 targets)
- **July 2026: NotebookLM rebranded → Gemini Notebook**; library works unchanged, keeps name
- **Master-token auth**: mints fresh web cookies on demand, self-heals expired sessions — the auth model for servers/CI (GN-1 "isolated auth profiles" = multi-account profiles feature)
- **Built-in MCP server** (`src/notebooklm/mcp/server.py`) + separate mcp-notebooklm / notebooklm-mcp-cli packages
- Deep Research via `source add-research "topic" --mode deep`
- ⚠️ Unofficial — undocumented Google APIs, may break, rate limits apply

**GN-3 implication**: 30 DR/mo budget in the gap description is WRONG — plan for 10/month free, or use notebooklm-py Deep Research sparingly. GN-4 smoke test should verify the 10/month ceiling first.

---

## §5 R22 — WARP Proxy Pool (RESOLVED)

**Sources**: Cloudflare WARP docs (2026-07-20), shahradelahi/cloudflare-warp, ochpgit/warp-rotate, adasThePrime/cloudflare-warp-proxy, hafizhsul/warp-proxy

- **WARP Local proxy mode** (desktop): HTTPS/SOCKS5 proxy for selected apps — the basis for proxy pools
- **WARP uses a separate routing table** — SSH/Tailscale/Nginx unaffected (critical for our federation)
- **WARP modes**: DNS-only, Traffic+DNS (MASQUE, post-quantum), Traffic-only, Local proxy
- **Open-source pool implementations**:
  - `shahradelahi/cloudflare-warp` (Go, SOCKS5/HTTP, DPI evasion via AmneziaWG+uTLS, IP scanner)
  - `ochpgit/warp-rotate` (IP rotation + SOCKS5)
  - `adasThePrime/cloudflare-warp-proxy` (Docker, multiple proxy instances SOCKS4/5/HTTP/HTTP2)
  - `hafizhsul/warp-proxy` — explicitly "route OpenCode Free traffic through rotating IPs to bypass IP-based rate limits"
- ⚠️ **ToS compliance flagged** by multiple projects — Cloudflare ToS may restrict proxy-pool use

**R22 verdict**: WARP proxy pool is VIABLE and actively used for OpenCode free-tier rate-limit bypass. Our `warp-proxy-pool` dep (already in pyproject) aligns with this ecosystem. Docker-based multi-instance approach (adasThePrime) is the cleanest reference.

---

## §6 R31/R33 — OpenCode Plugin Scope + Cold Session (RESOLVED)

**Sources**: dev.opencode.ai/docs/plugins, opencode.ai/docs/permissions, v2.opencode.ai/docs/compaction

- **V2 plugin API (beta)**: "The plugin effect is scoped — finalizers, fibers, registrations released on reload/unload. OpenCode does NOT expose private Core services to the plugin" — plugin scope reduction is BUILT-IN
- **Plugin disable directives**: `-acme.reviewer`, `-opencode.provider.*` in config — explicit scope reduction mechanism
- **Permission system**: `permission` config with granular object syntax (`bash: {"git *": "allow", "rm *": "deny"}`); v1.1.1 merged legacy `tools` boolean into `permission`
- **Compaction (R33)**: "replaces active model context with a generated checkpoint... lossy, but does NOT delete earlier durable session messages" — cold session context restoration relies on durable session messages + checkpoint; our session_gnosis/SESSION_ANCHOR pattern aligns with this

**R31 verdict**: Plugin scope reduction = use disable directives + V2 scoped effects. **R33 verdict**: cold session context = durable messages + checkpoint; our continuity artifacts are the right pattern.

---

## §7 R34/R4 — Provider Bands 2026 (RESOLVED)

**Sources**: costgoat.com OpenRouter free models (2026-09-21), openrouter.ai/docs/api/reference/limits, aifreeapi.com Gemini guides (2026-09-12), Google AI forum (2026-09-04)

### OpenRouter free tier (2026-09)
- **~20-22 free models** including:
  - `nvidia/nemotron-3.5-lightning:free` — **1.0M context** (our current model!)
  - `nvidia/nemotron-3-ultra-550b-a55b:free` — 1.0M ctx
  - `google/gemma-4-31b-it:free` — 262K ctx
  - `minimax/minimax-m3:free` — 1.0M ctx
- **Limits**: 20 req/min; **50 :free req/day** (<10 credits purchased) or **1000/day** (≥10 credits)

### Gemini API free tier (2026-03 baseline)
- 2.5 Pro: 5 RPM / 100 RPD | 2.5 Flash: 10 RPM / 250 RPD | 2.5 Flash-Lite: 15 RPM / 1000 RPD
- **Sept 2026: rate limits are now DYNAMIC** — per project/model/route/billing tier; "not something you can plan from a copied table"; AI Studio is the source of truth
- Usage tiers (Free/T1/T2/T3) = billing-account rules, not universal quotas

**R34 implication**: Provider band config should treat OpenRouter 1000/day (with ≥10 credits) as the workhorse band; Gemini free tier as secondary. **R4 (AGY account pool)**: account pooling for Gemini free tier remains viable but limits are now project-scoped and dynamic — pool design must read per-project limits from AI Studio, not hardcode.

---

## §8 Gaps NOT Web-Researchable (implementation-only)

| Gaps | Reason |
|------|--------|
| DP-1..DP-8 (Dynamic Prompt Builder, Context Window Registry, Model Router, Token Budgets) | Internal architecture; research inputs covered in §2/§7 (context windows, model specs) |
| DS-1..DS-5 (Documentation system) | Internal tooling |
| KD-1..KD-3 (Domain modules, curator model, affinity presets) | Internal design |
| LI-1/LI-2/LI-5 (AdaptiveContextBuffer, SequentialModelLoader, startup script) | Internal implementation; research inputs covered in §3 (mmap, KV cache) |
| R21 (workhorse paths), R36 (baseline calibration), R37 (identity fluidity) | Internal concepts |
| R38 (NotebookLM integration) | Covered in §4 (Gemini Notebook) |

---

## §9 Consolidated Verdict

| Gap | Status | Key Action |
|-----|--------|------------|
| ZS-1/ZS-2 | ✅ RESOLVED | zstd + max_pool_percent=25 + shrinker_enabled; 16GB swap; NEVER zram+zswap |
| LI-3 | ✅ RESOLVED | KV formula + q8_0 cache quant; mmap insight for SequentialModelLoader |
| LI-4 | ✅ RESOLVED | 1.7B@32k (~4.6GB) = safe worker; 4B@8-16k = tight fit; Thinking = 2-3x tokens |
| GN-1 | ✅ RESOLVED | notebooklm-py master-token auth + multi-account profiles |
| GN-3 | ✅ RESOLVED + **CORRECTED** | **10 DR/month free (not 30)**; compute-based limits from 2026-09-02 |
| GN-4 | ✅ RESOLVED | Smoke test must verify 10/month ceiling first |
| R22 | ✅ RESOLVED | WARP pool viable; adasThePrime Docker reference; ToS caution |
| R31 | ✅ RESOLVED | V2 scoped effects + disable directives |
| R33 | ✅ RESOLVED | Durable messages + checkpoint = our pattern |
| R34 | ✅ RESOLVED | OpenRouter 1000/day workhorse; Gemini dynamic limits |
| R4 | ✅ RESOLVED | Account pool must read dynamic per-project limits |
| R38 | ✅ RESOLVED | Gemini Notebook via notebooklm-py |

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ RESEARCH ⬡ 2026-09-22 ⬡ ALL-RESEARCHABLE-GAPS-COVERED*
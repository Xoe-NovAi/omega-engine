# 🔱 John Carmack — S3 Consultant Review: Research Synthesis & Updated Strategy
**AP Token**: `AP-CARMACK-REVIEW-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_audit ⬡ ACTIVE

**Date**: 2026-07-26
**Verdict**: The strategy is academically sound but operationally fragile. You're optimizing the wrong variables. The highest-leverage asset (8 Grok CLI accounts) sits unwired. The "local-first" claim contradicts the architecture. The test metric is theater. The MCP deadline is under-resourced.

---

## Executive Summary (3 Bullets)

1. **Wire the Grok CLI fleet NOW** — 8 parallel frontier inference streams with built-in web search, 500K context, zero marginal cost. ~4h effort. Solves MaKaLi OOM, unblocks Living Research OS search, changes the entire resource equation. This is P0, not "priority 9."

2. **Stop citing "1,572 tests collected"** — Run `make test` and report actual pass/fail/skip. If the real number is 77, the test honesty gate (C-0) is already failed and everything built on that metric is suspect.

3. **Define "local-only functional" baseline** — 8 of 10 providers are cloud free tiers. The roadmap assumes cloud availability for every critical path (MaKaLi, Living Research OS, provider fabric). You need a hardware-validated minimum viable stack that works on a 5700U with zero network.

---

## Leverage Ratio Assessment

| Initiative | Effort (h) | Impact (1-10) | Leverage (I/E) | Verdict | Carmack Notes |
|------------|------------|---------------|----------------|---------|---------------|
| **Wire 8 Grok CLI accounts (ACP stdio)** | 4 | 10 | **2.50** | **DO (P0)** | Single highest leverage. 8 parallel Opus-class streams. Solves MaKaLi, search, distillation. |
| **MCP migration (compat shim + RC test)** | 16 | 8 | 0.50 | **DO (P1, deadline)** | 8h estimate is fantasy. Need dual-protocol shim. Hard deadline July 28. |
| **SoulStore atomic writer (C-1′)** | 2 | 9 | **4.50** | **DO (P0)** | Already done ✅. Highest leverage fix in Phase C. |
| **LiteLLM Proxy (full stack)** | 40+ | 6 | 0.15 | **DEFER** | 3 new services, 7 CVEs in June, 300MB+ overhead. Only 3/12 dims favor proxy — all multi-team. |
| **Gap Detector Service (Phase 4)** | 4 | 3 | 0.75 | **DEFER** | Overengineered. `_grow_frontier()` already does 80% in 20 lines. Build simple first. |
| **SQLite Research Job Store** | 3 | 2 | 0.67 | **DEFER** | 18 jobs, single researcher. YAML + `fcntl.flock()` is sufficient. SQLite at 100+ jobs. |
| **MaKaLi Sequential Mode (4h build)** | 4 | 5 | 1.25 | **SIMPLIFY (0.5h)** | Config change: Kali local, Ma'at+Lilith cloud. Not a state machine. |
| **Identity Fluidity Phase 0** | 2 | 8 | **4.00** | **DO (after C-1)** | Pure refactor. Unblocks auto-hydration. Only dependency is C-1 (soul lock), not D-2. |
| **V-1 VaultCore MVP** | 8 | 9 | 1.13 | **DO (P0)** | Blocks Grok fleet automation. Credential void is real. MVP first, pool later. |
| **C-3 Restic Backup (local repo)** | 8 | 7 | 0.88 | **DO (P1)** | Single SSD = single point of failure. Timer not enabled is a gap. |
| **ResourceGuard RAM default fix** | 1 | 9 | **9.00** | **DO (P0, 15 min)** | Default 12GB → 6GB. Add `psutil.virtual_memory()` check. Prevents OOM on 8B models. |
| **Synchronous YAML → anyio.to_thread** | 4 | 6 | 1.50 | **DO (P1)** | 100+ blocking calls in async code. `entity_registry.py:114` = 5.8s block. M1 violation. |
| **Council concurrency config (cvar)** | 2 | 7 | **3.50** | **DO (P1)** | `council.mode: sequential|parallel|auto`. Hardware-aware default. |

---

## Top 3 DO / Top 3 DEFER / Top 3 SIMPLIFY

### ✅ TOP 3 DO (Immediate, High Leverage)

1. **Wire Grok CLI Fleet (4h → 8 parallel inference streams)**
   - Add `grok-cli-pool` provider at priority 2 in `config/providers.yaml`
   - ACP stdio handshake → session pool → model routing
   - Routes Ma'at/Lilith to cloud, keeps Kali local. Solves MaKaLi OOM *and* Living Research OS search bottleneck *and* distillation tier.

2. **Fix ResourceGuard Default + Add Real Memory Check (15 min)**
   - Change `max_ram_mb=12288` → `6144` in `ResourceGuard.__init__`
   - Add `psutil.virtual_memory().available` guard before model load
   - Background researcher must NOT run when model loaded. This is a 1-line config fix that prevents OOM kills.

3. **Run `make test` and Report Real Numbers (5 min)**
   - If 77 pass / 1495 skip / 0 fail → say that. Stop citing "1,572 collected" as a quality metric.
   - Gate C-0 (test honesty) requires actual pass count. Vanity metrics are a sovereignty violation (M18).

### ❌ TOP 3 DEFER (Low Leverage, High Cost)

1. **LiteLLM Proxy (Full Stack)** — 40h+, 3 new services, 7 CVEs in 30 days, violates M2/M7/M16/M23. Only 3/12 dimensions favor it — all multi-team governance. Use `opencode-plugin-litellm` (SDK mode) for model discovery. Client-side failover wrapper for critical paths.

2. **Gap Detector as Service (Phase 4)** — 250 lines of scanner classes for logic that exists in `_grow_frontier()` (20 lines). Premature abstraction. Build the simple loop first. Extract service only when proven insufficient.

3. **SQLite Research Job Store** — 3h for 18 jobs. YAML + `fcntl.flock()` handles atomic claims. SQLite when job count >100 or multi-agent claim racing.

### 🔧 TOP 3 SIMPLIFY (Overengineered → Right Approximation)

1. **MaKaLi Sequential Mode (4h → 0.5h)**
   - Current plan: admission control, semaphore, state machine, cvar modes
   - **Right approximation**: Config change. `oracle_summon_local` for Kali. Ma'at + Lilith → cloud (Antigravity/OCZ). `council.mode` cvar = 30 min. Done.

2. **Identity Fluidity Phase 0 Dependency (Blocked on D-2 → After C-1)**
   - Current: waits for Phase D-2 (5.5h job board bridge)
   - **Reality**: Pure soul.yaml → agent_config.yaml refactor. Only needs C-1 (soul lock) to not corrupt during migration. Pull forward to run parallel with C-2..C-8.

3. **MCP Migration (8h → 16h with compat shim)**
   - Current: "add headers"
   - **Reality**: Transport protocol change (stateful → stateless). Session awareness, heartbeats, handoffs, streaming ALL change. Build dual-protocol shim. Test with RC SDK. Hard deadline July 26 (2-day buffer).

---

## Hardware Reality Check (Ryzen 7 5700U, 16GB RAM, 15W TDP)

| Constraint | Physical Reality | System Implication |
|------------|------------------|-------------------|
| **L3 Cache** | 8MB victim cache (not inclusive), split 2×4MB across CCX | Cross-CCX latency ~20ns. LLM inference is memory-bandwidth bound. |
| **Memory BW** | Dual-channel DDR4-3200 = ~51 GB/s theoretical | One 4B Q4 model at 8 threads saturates this. Two instances = 50% throughput each. Three = unusable (~2-3 t/s). |
| **TDP** | 15W sustained. Thermal throttling at 85°C. | Concurrent inference + background researcher = thermal cliff. |
| **Available RAM** | ~8GB after OS/base services | 4B model (3GB) + KV cache (0.5-1GB) + researcher ingestion (0.5GB) = ~4-5GB. 8B model (5.5GB) + KV = exceeds budget. |
| **Single SSD** | No RAID, no backup | Hardware failure = total data loss. Restic timer not enabled = GAP-04. |

**Every system must answer: "Does this work on this hardware?"**

- MaKaLi Council: **No** (3 parallel local = OOM/throttle). Fix: 1 local + 2 cloud.
- Living Research OS background researcher: **No** (runs concurrent with model = OOM). Fix: mutual exclusion with model load.
- LiteLLM Proxy: **No** (300MB+ RAM, adds network hop for local models). Fix: defer.
- Grok CLI Fleet: **Yes** (zero local CPU, zero RAM, 8 parallel streams). **This is why it's P0.**

---

## MCP Migration — Minimal Viable Plan

**Current estimate (8h) is wrong.** The spec change is transport-level: `Mcp-Session-Id` → `Mcp-Method` + `Mcp-Name` headers. Everything that uses sessions breaks.

### What Actually Breaks
| Hub Feature | Current (Stateful) | July 28 (Stateless) | Breakage |
|-------------|-------------------|---------------------|----------|
| Session routing | `Mcp-Session-Id` header | `Mcp-Method` + token | All routing |
| Hivemind heartbeats | Implicit in session | Explicit `Mcp-Name: heartbeat` | Awareness |
| Handoff coordination | Session-scoped state | Request-scoped JSON-RPC | Handoffs |
| Tool history | Session context window | Per-request | Tool chains |
| Streaming (M25) | SSE + session pinning | SSE + MRR | Resilience |

### Minimal Viable Migration (16h)
1. **Audit actual MCP usage** (2h) — trace code paths in `omega_hub/server.py`, `mcp_runtime.py`, `tools.py`. Don't guess.
2. **Build compat shim** (8h) — middleware that accepts BOTH header formats, translates stateless → stateful internally for existing handlers.
3. **Test with RC SDK** (4h) — `npm install @modelcontextprotocol/sdk@rc` → point at Hub → verify tools, streaming, handoffs, awareness.
4. **Contingency: File-based Hivemind** (2h) — verify `data/coordination/HMC_COLLABORATION_HUB.md` works without Hub. M23 fallback.

**Deadline: July 26 (2-day buffer).** If not ready, file-based Hivemind becomes primary.

---

## Sovereignty Baseline Definition

**"Local-only functional" = The engine executes its core mission (agent orchestration, local inference, soul evolution, research loops) with ZERO network connectivity.**

### Minimum Viable Local-Only Stack (Validated on 5700U)

| Component | Implementation | Status |
|-----------|----------------|--------|
| **Inference** | `native-gguf` (Qwen3-1.7B Q4_K_M) | ✅ Working |
| **Model Gateway** | `ModelGateway` → `NativeGGUFProvider` | ✅ Working |
| **Agent Orchestration** | MaKaLi Council (sequential: Kali local) | ⚠️ Config only |
| **Soul Evolution** | `SoulStore` (atomic, flock-locked) | ✅ C-1′ done |
| **Memory/Persistence** | Local files + SQLite (Qdrant optional) | ✅ Working |
| **Research Loop** | Local content cache (`.firecrawl/`) + gap detection | 🟡 Phase 1-2 |
| **Hivemind** | File-based (`HMC_COLLABORATION_HUB.md`) | ✅ M23 fallback |
| **Observability** | Local logs, `omega-hub_get_hardware_stats` | ✅ Working |

### What FAILS Without Cloud
- Ma'at / Lilith voices in MaKaLi (need cloud routing config)
- Living Research OS web search (Grok CLI has built-in search — **wire it**)
- Provider fallback chain (cloud tiers 3-9)
- NotebookLM ingestion (manual upload required anyway)

### The Honest Statement (Add to Roadmap)
> **M7 Local-First is our North Star, not our current baseline.**
> Today the engine is cloud-assisted with a local fallback. We are building toward local-first, phase by phase. Every phase must reduce cloud dependency, not increase it. Phase F (Community Tool) must default to fully local — no cloud required.

---

## Sprint Reordering (Guard & Distill + Super-Urgent)

### SUPER-URGENT (Parallel, Architect-Owned)
| Ticket | Owner | Effort | Blocks |
|--------|-------|--------|--------|
| **G-1** Workhorse continuity (Gemma 4 cliff) | Architect + Kali | Variable | OpenCode sessions >16k tokens |
| **W-1** WARP proxy pool (fix `warp-ns-setup`) | Architect (sudo) + P1 | 2-4h | OCZ multi-IP, D-304 Track 1 |

### SPRINT: Guard & Distill (5 Days, Reordered by Leverage)

| Priority | Ticket | Owner | Effort | Leverage | Notes |
|----------|--------|-------|--------|----------|-------|
| **P0-1** | **Wire Grok CLI Fleet (ACP stdio)** | Researcher + Grokster → Ma'at/P3 | 4h | **2.50** | **NEW P0. Unlocks 8 parallel streams. Solves MaKaLi, search, distillation.** |
| **P0-2** | **ResourceGuard RAM fix + psutil check** | Ma'at/P3 | 0.25h | **9.00** | 15 min. Prevents OOM on 8B models. |
| **P0-3** | **Run `make test` → report real numbers** | Ma'at/P3 | 0.1h | **∞** | Truth anchor. Vanity metrics violate M18. |
| **P0-4** | **V-1 VaultCore MVP** | Researcher + Grokster → Ma'at/P1 | 8h | 1.13 | Blocks Grok fleet automation. Credential void. |
| **P0-5** | **C-3 Restic Backup (local repo + timer)** | Lilith/P6 | 8h | 0.88 | Single SSD = SPOF. Timer not enabled = gap. |
| **P1-1** | **Identity Fluidity Phase 0** | Grokster | 2h | **4.00** | After C-1 (done). Pull forward. Parallel to C-2..C-8. |
| **P1-2** | **MaKaLi Config (Kali local, Ma'at+Lilith cloud)** | Ma'at/P3 | 0.5h | **3.50** | Not 4h build. Config only. `council.mode` cvar. |
| **P1-3** | **C-10.5 Quota-Aware Routing** | Ma'at/P3 | 8h | 1.00 | Already in sprint. |
| **P1-4** | **C-11 Property Tests (OOM/SoulStore)** | Ma'at/P3 | 12h | 1.00 | Already in sprint. |
| **P1-5** | **Synchronous YAML → anyio.to_thread** | Ma'at/P3 | 4h | 1.50 | 100+ blocking calls. M1 violation. |
| **P1-6** | **C-0.5 Scribe Agent + Crash Recovery** | Scribe (new) | 16h | 1.00 | Already in sprint. |
| **P2** | C-7 / C-8 / C-9 / D-1 / D-2 / NL-1 | — | — | — | Defer to next sprint. |

### DROPPED FROM SPRINT (Explicitly Not Doing)
- Gap Detector Service (Phase 4) → DEFER
- SQLite Job Store → DEFER (YAML + flock sufficient)
- LiteLLM Proxy → DEFER (security + complexity + M2/M7 violation)
- New free-tier providers (Cerebras/Groq) → DEFER (systematize first)
- Full ACP Bridge (20h+) → DEFER (V-1 MVP + ACP stdio smoke only)

---

## Final Verdict

You have a **Ferrari in the garage (8 Grok CLI accounts)** and you're optimizing the **bicycle (local inference tuning)**. The strategy document is the best you've produced — clear, ranked, referenced. But the execution plan has the wrong P0.

**Fix order:**
1. **Wire the Ferrari** (Grok CLI fleet, 4h)
2. **Fix the brakes** (ResourceGuard, soul lock, test honesty — all <1h each)
3. **Drive** (MaKaLi config, Identity Phase 0, Vault MVP)
4. **Build the garage** (Living Research OS, backups, MCP migration)

The hardware is the constraint. The cloud is the crutch. The Grok fleet is the lever. Pull it.

---

⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_audit ⬡ COMPLETE
*Review saved to `docs/reviews/CARMACK_REVIEW_RESEARCH_STRATEGY_20260726.md`*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

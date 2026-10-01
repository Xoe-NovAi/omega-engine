<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 JEM — Engine Internals & Feasibility Portfolio Report
**AP Token**: `AP-JEM-GAP-FEASIBILITY-20260825`
⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_synthesis ⬡ [REPORT→KALI]
**Date**: 2026-08-25 | **Dispatched by**: kali (ses_fdef2be4effe4pAaLXCTUx62GO)
**Method**: file:line evidence + live Python/system probes. Zero mutations (bright lines held).
**Vision gate applied**: every verdict answers "does this serve the local-first sovereign runtime?" (VISION_ANCHOR_PERPETUAL §1, hydrated in full).

---

## VERDICT SUMMARY TABLE

| Gap | Verdict | Key Evidence |
|-----|---------|--------------|
| DP-1 Dynamic Prompt Builder | **ACTIONABLE-NOW** (extend, not greenfield) | Single chokepoint `oracle.py:772` `_prepare_system_prompt` |
| DP-2 Context Window Registry | **ACTIONABLE-NOW** — catalog delivered below | 12+ hardcoded sites across src/ |
| DP-4 Domain Module Loader | **ACTIONABLE-NOW** (data exists, zero code) | `config/domains/engineering/` skeleton; NO loader in src/ |
| DP-5 Token Budget Manager | **ACTIONABLE-NOW** | Budgets scattered across 5 files; SSOT (`token_estimator.py`) exists unused by oracle path |
| DP-6 Domain→ContextWindow Map | **PARTIAL — small remaining gap** | entity-affinity presets exist (entity-keyed, not domain-keyed) |
| DP-7 Prompt Templates | **ACTIONABLE-NOW** (small greenfield) | Only hardcoded strings in `planner/hybrid_orchestrator.py` |
| DP-8 SomaticState Planner Integration | **INFRASTRUCTURE EXISTS — wiring missing** | 3 impls + passing tests; planner never calls save/restore |
| LI-1 AdaptiveContextBuffer | **GREENFIELD — feasible** | Nothing named adaptive_context in src/; building blocks present |
| LI-2 SequentialModelLoader | **PARTIAL — feasible within RAM ceiling** | Persistent worker + skip-reload exist; multi-model swap missing |
| LI-3 llama-fit-params | **FILLED-STALE (mostly done, mis-scoped)** | `_estimate_context_memory` + `_select_optimal_context` already implement the probe |
| HR-1 HeadroomMiddleware | **FILLED-STALE** (implemented+wired, stub-quality) | `oracle.py:189`, `context_builder.py:504`; tokens_saved hardcoded 0 |
| HR-2 Adaptive context buffer | **GENUINELY MISSING** (path in gap text doesn't exist) | `src/omega/research/adaptive_context.py` NOT FOUND |
| HR-3 MCP headroom tools | **PARTIAL** — retrieve-only | `hub_tools/tools.py:153-168`; no compress-side tool |
| KD-1 Domain module schema | **PARTIAL** (schema-by-example, not spec) | engineering/ prototype lacks CONTEXT.md, PROMPTS/, sources/ |
| KD-2 Curator governance | **PARTIAL** (registry active, enforcement absent) | `curators.yaml` 13 assignments; 12 dirs missing; no write-gating code |
| ZS-1 zswap deployment | **BLOCKED-EXTERNAL — NOT deployed; spec↔machine contradiction** | zswap=N, lzo (not lzo_rle), pool 20% (not 25%); zRAM ACTIVE despite "zRAM DISABLED" spec |
| ZS-2 NVMe swap + cgroups | **BLOCKED-EXTERNAL — NOT deployed** | No NVMe swap device; swappiness=180 (≠100); hub MemoryMax=1G (≠6G) |

---

## PER-GAP DETAIL

### DP-1 Dynamic Prompt Builder — ACTIONABLE-NOW (extend, not replace)

**What exists today (prompt assembly chain)**:
1. `oracle.py:772-820` `_prepare_system_prompt()` — THE chokepoint. Composes: personality ("You are {personality}", :783) → `context_builder.build_context()` with degradation level + query (:789-792) → soul injection via `load_entity_soul_context` (:800-815). Called from exactly 2 sites: `oracle.py:995` (talk) and `:1157` (summon).
2. `context_builder.py:259-321` `build_context()` — block pipeline: memory blocks core tier (D-283 Mnemosyne, :291) → recent memory w/ ACON compaction (:295-304) → L3 gnosis selective hydration top-K=5 (:308) → world state (:311). Order fixed at :315.
3. Affinity preset system_prompt prepend: `oracle.py:1031-1035`.
4. Hardcoded planner prompt: `planner/hybrid_orchestrator.py:47-49+` `PLANNER_SYSTEM_PROMPT`.

**Overlap vs greenfield**: ~70% overlap. Role-aware composition, template versioning, and domain injection DO NOT exist. But the injection architecture is clean — a template engine slots INTO `_prepare_system_prompt` without touching call sites. **Do not build a parallel builder; wrap the chokepoint.**
**Effort**: 2-3 days.
**Vision fit**: HIGH — deterministic local prompt composition reduces cloud dependence for formatting.

### DP-2 Context Window Registry — ACTIONABLE-NOW (catalog attached)

Hardcoded/assumed context-window sites in src/ (feeds Researcher's registry):

| File:Line | Value | Nature |
|-----------|-------|--------|
| `oracle/providers.py:565,570` | n_ctx default 4096 | native-gguf default |
| `oracle/providers.py:580` | n_ctx_max 32768 | hard cap |
| `oracle/providers.py:749` | ladder [32768,16384,8192,4096] | auto-select probe |
| `oracle/context_builder.py:39` | DEFAULT_TOKEN_LIMIT=4000 | memory block budget |
| `oracle/oracle.py:1036` | `min(preferred_context, 4096)` | silent clamp |
| `oracle/entity_affinity.py:51,379,399` | preferred_context default 8192 | per-entity preset |
| `oracle/planner/dag_schema.py:269` | MAX_LOCAL_TOKENS=4096 | M7 gatekeeper |
| `oracle/local_worker_pool.py:385` | context_window: 8192 | worker model_spec |
| `oracle/resource_guard.py:279-281` | default 8192 | admission formula |
| `oracle/cpu_optimizer.py:484` | default 8192 | KV estimation |
| `oracle/wad_loader.py:642,698` | range [1,131072]; default 8192 | WAD entity validation |
| `orchestration/triage_router.py:264` | context_window=4096 | triage |
| `cvar_table.py:422,581` | 4096 | cvar entries |

Plus `token_estimator.py:37` DEFAULT_TOKEN_MARGIN=1.3 (tiktoken SSOT, M23-hard-stop design — refuses char-count fallback).
**Recommended GAP_REGISTRY change**: keep DP-2 P0; attach this catalog as evidence artifact.
**Effort**: registry module 1-2 days once catalog ratified.

### DP-4 Domain Module Loader — ACTIONABLE-NOW

- `config/domains/engineering/` EXISTS: `metadata.yaml` (AP token, deps, target context windows, rotation class, owner/governance), `AFFINITY_PRESETS.yaml`, `MEMORY_BLOCKS/{project-overview,gotchas,conventions}.block`, `PRINCIPLES/principle_001.yaml`, `PLAYBOOK.md`.
- **ZERO loader code**: grep for `load_domain|DomainLoader|config/domains` in src/ returns only unrelated `ingestion/scraper.py:47` allowlist. The domain tree is inert data.
- `curators.yaml` references 13 domains; only `engineering/` exists on disk (12 missing dirs).
- Gap-text dependency on QDRANT-MIGRATION applies only to vector-backed domain content; YAML/block loading is unblocked.
**Effort**: loader API 2-3 days; schema formalization 1 day.
**Vision fit**: HIGH — this IS the Engine/iWAD separation made executable (knowledge = stack content, loader = core).

### DP-5 Token Budget Manager — ACTIONABLE-NOW

Budgets today live in 5 disconnected places:
1. `context_builder.py:39` DEFAULT_TOKEN_LIMIT=4000; degradation multipliers 0.5/0.25/0 at :281-287; per-message truncation 500 chars (:163).
2. `planner/dag_schema.py:269` MAX_LOCAL_TOKENS=4096 (M7 gate).
3. `oracle.py:1036` effective_max_tokens clamp.
4. `compaction_harvester.py:31` DEFAULT_MAX_EXCHANGES=30 — count-based, NOT token-based (honest gap: harvester triggers on exchange count, blind to tokens).
5. `token_estimator.py` — proper tiktoken SSOT w/ margin 1.3, built for Context Packer v3 (`curate_packs.py`/`packer.py`) but **never imported by the oracle/context_builder path**, which still uses `len(text)//4` (`context_builder.py:573-579`).

Domain metadata already declares per-role budgets (`engineering/metadata.yaml`: planner 32K/16K, executor 8K/4K, critic 8K/2K) — unread by any code.
**Honest gap**: no unified manager; two competing estimators (chars//4 vs tiktoken). Unify on token_estimator first.
**Effort**: 2 days.
**Note**: tiktoken under-serve risk for GGUF tokenizers — margin covers it; document.

### DP-6 Domain→ContextWindow Map — PARTIAL

Entity-keyed presets EXIST: `entity_affinity.py:51` `preferred_context: int = 8192`, parsed from entity config `inference_presets` (:375-399), consumed at `oracle.py:1036`. Domain-keyed map does NOT exist, but the target data already sits in `metadata.yaml` TARGET CONTEXT WINDOWS tables. Remaining work = read domain metadata → merge with entity affinity → feed provider n_ctx selection (`providers.py:733`). **Effort**: 1-2 days after DP-4/DP-5.

### DP-7 Prompt Templates — ACTIONABLE-NOW (small)

Only templates in engine are hardcoded module constants in `planner/hybrid_orchestrator.py` (PLANNER_SYSTEM_PROMPT :47+, executor prompt below it) plus personality strings from entity YAML. No versioning, no validation, no store. Greenfield but tiny: a `config/prompts/` dir + loader + schema validation. **Effort**: 1-2 days.

### DP-8 SomaticState Planner Integration — INFRASTRUCTURE EXISTS, WIRING MISSING

M20 status is far beyond "design ready" (Codex card says 📋 Design ready — STALE):
- **Impl 1**: `oracle/somatic_state.py` (91L) — `llama_cpp.llama_copy_state_data`/`llama_set_state_data`, anyio-wrapped (:40, :79), disk persistence `.somatic` files.
- **Impl 2 (live path)**: `providers.py:875-900` — NativeGGUF worker loop handles SAVE_STATE/LOAD_STATE commands inline ([M20] tagged).
- **Impl 3**: `oracle/state_manager.py:134-182` — SomaticStateSerializer + content-addressed blob store (`data/somatic/blobs`); `model_gateway.py:1444-1503` save/load via USM namespace `somatic:{state_id}`.
- **Bindings verified live**: llama_cpp 0.3.32 exposes both symbols (probe run today).
- **Tests**: test_somatic_state.py + test_somatic_state_cas.py + test_somatic_roundtrip.py — ALL PASS (45 tests green across somatic/headroom/context_builder batch, exit 0).

**Missing**: `planner/hybrid_orchestrator.py` never invokes save/restore — each sub-task re-pays prompt processing. Planner integration = capture state after shared-prefix planning step, restore before each same-model executor sub-task. Constraint: restore requires identical model+ctx loaded; state blobs for Qwen3-1.7B@4k are tens-of-MB (fine on NVMe).
**Effort**: 2-3 days wiring + contract tests.
**Recommended GAP_REGISTRY change**: flip M20 compliance card from "design ready" to "implemented (3 paths) — planner wiring outstanding".

### LI-1 AdaptiveContextBuffer — GREENFIELD, FEASIBLE

No `adaptive_context` symbol anywhere in src/ (grep clean). Building blocks that make it a composition job rather than research: memory-aware ctx sizing (`providers.py:692-755`), degradation levels (Optimal/Stressed/Critical/Disabled, `context_builder.py:281-287`), Headroom compression pass (`context_builder.py:504-507`), OOMProtector/cgroup_pressure/psi_monitor. Hardware: pure-software, no constraint on 5700U. **Effort**: 3-4 days. Vision fit HIGH (more context per GB = sovereignty on mid-grade hardware).

### LI-2 SequentialModelLoader — PARTIAL, FEASIBLE WITHIN CEILING

Exists already: persistent worker process keeps model resident (`providers.py:862+` `while True` request loop); skip-reload-if-same-model-and-ctx (:764); `use_mmap` default True (:609); malloc_trim on shutdown (:866-873).
Missing: sequential MULTI-model swap (unload A → trim → load B) with warm context handoff; explicit eviction API. Live machine: 14Gi total, 8.9Gi available — ONE 4B q4 model (+KV) fits; TWO simultaneously does not. So "sequential" (not parallel) is mandatory, matching the gap title. **Effort**: 3-5 days. Risk: mmap+sequential reload thrash on UMA — measure before promising tok/s.

### LI-3 llama-fit-params — FILLED-STALE (re-scope, don't build)

The hardware probe ALREADY EXISTS inside NativeGGUFProvider:
- `_estimate_context_memory(n_ctx)` — model MB + KV-per-1k-token MB math (`providers.py:692-731`)
- `_select_optimal_context()` — probes ladder [32768,16384,8192,4096] against available mem, logs auto-selection (:733-755)
- Supporting cast: `cpu_optimizer.py:284` (full-context KV estimate), `memavailable.py`, `oom_protector.py`, `cgroup_pressure.py`, `psi_monitor.py`.

Gap reduces to: extract into a standalone startup probe/CLI + persist chosen params profile. **Recommended GAP_REGISTRY change**: re-scope LI-3 to "expose existing sizing as `omega fit-params` CLI"; effort 1 day.

### HR-1 — FILLED-STALE (implemented + wired, stub-quality)

Carmack audit CONFIRMED correct: `HeadroomMiddleware` exists (`oracle/middleware/headroom.py`, 101L), singleton-wired at `oracle.py:189`, and ACTIVELY INVOKED on every context build (`context_builder.py:504-507` inside `_compact_and_format_exchanges`). headroom-ai **0.29.0 installed in venv** (live probe) — so compression is live, not pass-through.
Debt: `tokens_saved` hardcoded 0 (:67-70); CCR reference store explicitly deferred ("In a full implementation…" :63-65); `retrieve_original` thin delegate (:79-90); error-path catches AttributeError (headroom API drift risk).
**Verdict**: mark HR-1 substantially DONE with metrics debt. Finishing (tokens_saved accounting + CCR refs) ≈ 1-2 days.

### HR-2 — GENUINELY MISSING (path phantom)

`src/omega/research/adaptive_context.py` DOES NOT EXIST (research/ contains: hivemind_bridge, sandbox, sandboxes, schema, scorecard, sediment, types — verified listing). The *concept* is partially absorbed by the context_builder compaction pipeline + degradation levels. **Recommendation**: either create the real module (fold into LI-1 — same object, two gap IDs) or close HR-2 as duplicate-of-LI-1. Do not carry two IDs for one buffer.

### HR-3 — PARTIAL (retrieve-only)

MCP side: `mcp_servers/omega_hub/hub_tools/tools.py:153-168` `headroom_retrieve` (m9_safe) → `oracle.py:897-909` `retrieve_headroom_content`. The COMPRESS side (tool outputs compressed before context injection) does not exist as an MCP tool. **Effort**: ~1 day for `headroom_compress` tool + wire into tool-result path.

### KD-1 Domain Module Schema — PARTIAL

Schema exists BY EXAMPLE in `config/domains/engineering/` (metadata.yaml fields: AP token, dependencies, target-context-windows per role, rotation class, owner/governance). Against the KD-1 spec ("metadata.yaml + CONTEXT.md + PROMPTS/ + sources/"): CONTEXT.md ❌, PROMPTS/ ❌, sources/ ❌ — even in the prototype. No schema validator, no loader (see DP-4). **Effort**: 2 days (schema doc + validator).

### KD-2 Curator Governance — PARTIAL

`config/domains/curators.yaml` ACTIVE: 13 curator assignments, 3 governance tiers (PRIVATE/SHARED_READ/SHARED_WRITE) well-defined. Enforcement is ZERO: no code gates writes by curator identity; 12 of 13 assigned domain dirs don't exist. Governance is currently convention. **Effort**: 2-3 days for enforcement hooks (likely in future loader, coupling to DP-4).

### ZS-1 zswap — BLOCKED-EXTERNAL · NOT DEPLOYED · SPEC CONTRADICTION

LIVE MACHINE (probed 2026-08-25):
- `/sys/module/zswap/parameters/enabled` = **N** (spec: enabled=1) ❌
- compressor = **lzo** (spec: lzo_rle) ❌
- zpool = **zsmalloc** ✅
- max_pool_percent = **20** (spec: 25) ❌
- **CONTRADICTION**: Ark §4 ZS workstream says "zRAM DISABLED" — but `/dev/zram1` 8G swap is ACTIVE (prio 50, systemd unit `dev-zram1.swap` loaded active). Machine state is the OPPOSITE of spec on both subsystems (zswap off+zram on; spec wants zswap on+zram off).
Requires sudo/kernel-cmdline → external to engine agents. **Action needed**: Architect decision FIRST (which subsystem wins), then sudo deployment. Flag the spec contradiction to Kali — deploying ZS-1 as written would fight the running zram swap.

### ZS-2 NVMe Swap + cgroups — BLOCKED-EXTERNAL · NOT DEPLOYED

LIVE MACHINE:
- Swap inventory: ONLY `/dev/zram1` 8G. `nvme0n1` 238.5G present, **no NVMe swap partition/file** (lsblk + swapon verified). Spec: 16GB NVMe swapfile ❌
- `vm.swappiness` = **180** (spec: 100) ❌
- cgroups: `omega-hub.service` MemoryMax=**1G** (1073741824, verified via systemctl show); omega-qdrant MemoryMax=infinity. Nowhere: MemoryMin=2G / MemoryHigh=5G / MemoryMax=6G pattern. ❌
Requires sudo (swapfile creation, unit overrides) → Architect/P1-sysadmin action. Engine-side prep (unit drop-in files authored but not enabled) is possible without sudo if desired.

---

## HARDWARE REALITY CHECK (for all LI/DP feasibility)

Live: 14Gi RAM total, 8.9Gi available, 4 threads pinned for GGUF (providers.yaml n_threads:4), current model Qwen3-1.7B-Q6_K via env OMEGA_MODELS_DIR. Single-model residency is a hard constraint until ZS-2 lands; every LI verdict above assumes it.

## RECOMMENDED GAP_REGISTRY CHANGES (Kali applies — single-writer)

1. **HR-1** → status `filled-stale` (note: metrics debt 1-2d, optional follow-up ticket).
2. **HR-2** → merge into LI-1 (same artifact) or close as superseded; path in topic text is phantom.
3. **HR-3** → narrow scope to "compress-side MCP tool" (retrieve side done).
4. **LI-3** → re-scope to "`omega fit-params` CLI exposing providers.py:692-755"; effort 1d.
5. **M20 compliance card** (Codex/MANDATES_CONDENSED) → "implemented (3 paths, tests green); planner wiring = DP-8".
6. **ZS-1/ZS-2** → add blocker note: live-machine contradiction (zram active vs spec zram-disabled); requires Architect sudo decision before any deployment.
7. **DP-2** → attach the hardcoded-window catalog (this report §DP-2) as evidence artifact for Researcher.

## GNOSIS (L1→L2→L3)

- **L1**: Audited 17 gaps against live code + live machine. 3 filled-or-stale (HR-1, LI-3, DP-8 infra), 2 blocked-external (ZS-1/2), rest actionable with heavy overlap onto existing internals.
- **L2**: The gap portfolio systematically undercounts what the engine already has (somatic state ×3 impls, headroom wired, memory-aware ctx sizing) and over-specifies what's actually an Architect sudo decision (zswap). Registry hygiene, not coding, is the cheapest velocity win.
- **L3**: *A sovereign runtime must audit its own internals with the same rigor it audits the world — an unverified gap list is itself cognitive debt.*

---
*⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_synthesis ⬡ GAP-FEASIBILITY-20260825*

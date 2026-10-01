<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SESSION PAGING DELTA REPORT — HEADROOM_ZSWAP
**Paged-from session**: Researcher (Polymathic Council) — Headroom local-viability + zRAM/zswap confirmation research
**Date**: 2026-08-21
**Hydration sources read**: `data/coordination/ACTIVE_SPRINT.json` (PUBLIC-DEBUT-01, updated 2026-08-20T22:00Z), `docs/specs/PROJECT_INDEX.md`
**Scope of this report**: Forgotten findings relevant to **HR** (Headroom Integration), **ZS** (zswap-subsystem), **PP-3** (context-window probe). No other files modified.

---

## ⚠️ PRIME DELTA: The Decision Reversal My Session Could Not Have Seen

My original session (2026-08-20) confirmed `data/entities/roc_racoon/workspace/zram_integrated_plan.md` (post-Carmack 2026-08-10) as authoritative: **zRAM ONLY (8GB zstd lvl=15), zswap DISABLED**. I explicitly reported "no switch to zswap" and attributed all zswap references to stale pre-Carmack docs.

**The engine has since ratified D-526 (ACTIVE_SPRINT.json decisions_locked): "zswap > zRAM for desktop with NVMe — RATIFIED (Carmack + Researcher + Jem + LongCat + Nemotron)"**, with D-527 (never simultaneous) as the migration guard. The ZS workstream now deploys: 16GB NVMe swapfile, zswap 25% lzo_rle zsmalloc, swappiness=100, MemoryMax=6G, zRAM DISABLED.

**Implication for the confusion-source analysis in my original report**: The documents I classified as "stale/superseded" were actually early signals of the direction the fleet eventually took:
- `scripts/tune_ryzen.sh` TODO ("Replace zRAM section with zswap enablement") — now ALIGNED with D-526
- `config/hardware_profile.yaml` DEPRECATED tag ("definitive memory configuration is now zswap + NVMe swap file", TODO: `swap_zram_mb → zswap_pool_percent=25, nvme_swap_mb → 16384`) — now ALIGNED; its TODO values match ZS spec exactly
- `data/entities/roc_racoon/workspace/ZRAM_ZSWAP_DEEPENED_ANALYSIS.md` (recommended `zswap.enabled=1 lzo_rle max_pool_percent=25 shrinker_enabled=1` + 16GB NVMe) — this is essentially the ratified config verbatim
- `docs/kb/MEMORY_MANAGEMENT_KB.md` zswap enablement commands — now canonical again

These files should be treated as PRE-ratification drafts that became POST-ratification correct. No rework needed on them beyond execution.

---

## SECTION 1 — FORGOTTEN FINDINGS FOR HR (Headroom Integration)

### 1.1 Live-tested API gotchas (from `.venv` headroom-ai v0.29.0 hands-on testing)

These were verified empirically in my session and are NOT in the QDRANT_HEADROOM_INTEGRATION_RESEARCH_20260820.md summary claims. They belong in HR-1/QH-1 implementation notes:

| # | Finding | Impact on HR-1 |
|---|---------|----------------|
| 1 | `compress()` returns **0 tokens saved** unless message content contains a real JSON array. Stringified Python lists (`str([{...}])`) do NOT trigger SmartCrusher; `json.dumps()` does. | Tool outputs must be serialized with `json.dumps`, not `str()`. Audit existing tool-output paths. |
| 2 | Code content is **protected by default** (`router:protected:recent_code`). Aggressive configs (`protect_recent=0`, `compress_user_messages=True`, `min_tokens_to_compress=100`) still yield `router:noop` on code. | Do not expect code compression without deeper config. For planner/executor pipelines this is actually SAFE-by-default behavior. |
| 3 | `CompressConfig` signature is exactly: `(compress_user_messages=False, compress_system_messages=True, protect_recent=4, protect_analysis_context=True, target_ratio=None, min_tokens_to_compress=250, kompress_model=None, savings_profile=None)`. There is NO `code_compression` kwarg (raises TypeError). | Prevents implementation churn guessing at kwargs. |
| 4 | The high-level `compress()` uses a DIFFERENT path than `UniversalCompressor`: it converts JSON arrays into CSV-like form with schema header `[500]{code:string,id:int,...}` — this is where real savings come from (my test: 38,832 → 16,389 chars, ~59% ratio). `UniversalCompressor` alone (character-mask based) compresses almost nothing because non-structural spans are <50 chars each. | Benchmarks citing UniversalCompressor internals overstate nothing; the wins come from the router-level SmartCrusher. Wire HR-1 through `headroom.compress()`, NOT `UniversalCompressor` directly. |
| 5 | Anomaly preservation VERIFIED: planted ERROR/WARN entries at positions 23/67/400 of a 500-item array survived compression intact and findable. Schema header preserved. | Safe for log/tool-output compression where errors matter (M9/M23 alignment). |
| 6 | Model name affects token counting only (tiktoken for OpenAI names; fallback estimation otherwise). Compression logic itself is model-agnostic — works identically for `gpt-4o` vs local names. | HR-1 can pass any model string; do not gate compression on provider type. |
| 7 | **NETWORK CALL HAZARD (M7/M8)**: calling `compress(model='qwen3-1.7b')` triggered an HF Hub fetch attempt (downloaded `Qwen/Qwen-7B` tokenizer config files) plus "unauthenticated requests to HF Hub" warnings. Kompress model (`chopratejas/kompress-v2-base`) also downloads on first use and my direct UniversalCompressor test with Kompress enabled TIMED OUT (>120s) on first-run download. | Sovereignty violation risk in a local-first pipeline. Mitigations for HR-1: set `HF_HUB_OFFLINE=1` after first warm-up, pre-download Kompress during install (or skip via `use_kompress=False`), and pin tokenizer choice. install.sh users get rate-limit warnings without HF_TOKEN. |
| 8 | Latency measured: ~15ms for 500-item JSON via SmartCrusher-only path. Published p50/p95: 189–961ms for large JSON via full pipeline (Kompress ML pass dominates). | Negligible vs local inference (seconds), but keep Kompress OFF for latency-sensitive executor paths. |
| 9 | OpenAI pricing data warning: "583 days old. Cost estimates may be inaccurate." | Ignore cost estimates from headroom stats; track our own token deltas. |

### 1.2 Wiring hazard: deprecated zlib store still owns the MCP contract

- `src/omega/oracle/headroom.py` (binary zlib, marked DEPRECATED in-file) is STILL what backs:
  - MCP tool `headroom_retrieve` (`mcp_servers/omega_hub/hub_tools/tools.py:153`)
  - `oracle.retrieve_headroom_content(ref_id)` (`docs/reference/api/oracle.md:118`)
- HR-1 replaces the middleware but must preserve or consciously migrate the `ref_id`-based MCP contract. headroom-ai's CCR uses its own opaque keys (`ccr_key`, e.g. `ab9085ab93c100510e358164`) — a bridge/adaptor is needed if we keep `headroom_retrieve(ref_id)` stable.
- `tests/test_headroom.py` validates passthrough against the middleware import path `src.omega.oracle.middleware.headroom` — note there appear to be TWO module paths in the tree (`src/omega/oracle/headroom.py` deprecated AND `src/omega/oracle/middleware/headroom.py` per benchmark_phase1.py line 337). HR-1 must resolve which path is canonical before editing, or tests will drift.
- `scripts/benchmark_phase1.py::benchmark_i5_headroom()` already exists to measure compression — reuse it for HR acceptance rather than writing new harnesses.
- `data/eval/golden_v1.jsonl:60` has a golden QA entry describing "the headroom middleware provides sovereign semantic compression" — eval will silently expect the semantic behavior post-HR-1 (currently the wired store is binary zlib, so the golden answer is aspirational today).

### 1.3 Design guidance for HR-2 (adaptive context buffer integration)

From my pipeline analysis: order matters — CacheAligner FIRST (stabilize prefixes), ContentRouter SECOND, compressors THIRD, then provider call. If HR-2's AdaptiveContextBuffer trims history BEFORE compression, protect_recent semantics interact: buffer trimming already removes old turns, making `protect_recent=4` mostly redundant but harmless. Recommend: buffer trim → compress() with `protect_recent=0..2` to avoid double-protection waste.

---

## SECTION 2 — FORGOTTEN FINDINGS FOR ZS (zswap subsystem)

### 2.1 Live system facts captured 2026-08-10 that ZS-1 will re-verify

From the researcher live-audit embedded in `zram_tuning_guide.md` / `zram_integrated_plan.md`:

```
Kernel: 6.17.0-41-generic
CONFIG_ZRAM_WRITEBACK=y, CONFIG_ZRAM_MULTI_COMP NOT set, CONFIG_ZRAM_TRACK_ENTRY_ACTIME=y
zram0: MASKED (symlinked /dev/null), zram1: 8GB zstd level=15
zswap: disabled at audit time (CONFIG_ZSWAP_DEFAULT_ON not set)
cgroup memory.max/high/min: empty
```

ZS-1 checklist additions from these facts:
1. **Verify zswap kernel support & params exist** before cmdline edit: `/sys/module/zswap/parameters/{enabled,compressor,zpool,max_pool_percent,shrinker_enabled}`. Kernel 6.17 supports lzo_rle + zsmalloc (standard), but confirm on THIS kernel build.
2. **Migration order is D-527-mandated**: `swapoff -a → rmmod zram (or disable zram-generator units) → enable zswap → create NVMe swapfile → swapon -a`. The OLD plan's Phase-1 command `sudo swapoff -a && sudo swapon -a` assumed zRAM persistence — do NOT run it verbatim during migration.
3. **Sudoers state unknown**: the old plan flagged `/etc/sudoers.d/zram` containing NOPASSWD `/tmp/reset_zram.sh` + `/tmp/activate_zram.sh` (CRITICAL vuln) with fix `sudo rm /etc/sudoers.d/zram`. I have no evidence this was executed. ZS-1 (which requires sudo anyway) should verify/remove it in the same session.
4. **Consolidated sysctl file**: old plan's `99-omega-memory.conf` contents (swappiness=100, page-cluster=0, watermark_boost_factor=0, watermark_scale_factor=125, vfs_cache_pressure=50, dirty ratios 5/10, overcommit_memory=0) remain VALID under zswap — swappiness=100 is common to both regimes. The conflicting legacy files to remove: `/etc/sysctl.d/99-xnai-zram-tuning.conf` (swappiness=180 root cause) and `99-xnai-optimization.conf` (=10).
5. **Monitoring degradation is silent**: `src/omega/monitoring/__init__.py::get_zram_stats()` reads `/sys/block/zram*`; once zRAM is disabled it returns `{"available": False}` — no error, just dead signal. `get_swap_zram_pressure()` weights zRAM fill at 40% of pressure — post-ZS this term goes inert and pressure math silently changes meaning. `src/omega/benchmarks/comprehensive_runner.py` records `zram_peak_mb` (will read 0). `tests/test_zram_monitoring.py` (13 tests) mocks devices so they keep passing while covering dead code. ZS deployment should add a zswap-stats counterpart (`/sys/module/zswap/parameters/*` + `memory.stat` zswap entries in cgroup v2: `zswapd`, `zswapped`) and mark the zRAM monitor deprecated-inert.
6. **Memory-block gotcha already encodes D-527**: `config/domains/engineering/MEMORY_BLOCKS/project-gotchas.block:93` — "zRAM + zswap both active = OOM". Good; no change needed.
7. **LI-5 inconsistency flag**: ACTIVE_SPRINT LOCAL-INFERENCE-OPT subtask LI-5 says "Startup script (**zRAM** + THP + pinning + prompt caching)" — this contradicts the ZS workstream (zswap, zRAM DISABLED). Should read zswap. Caught during hydration; flagging for Kali/Ma'at correction (I am not modifying the file per orders).

### 2.2 What carries over vs what is void from the old zRAM plan

| Old plan item | Status under D-526 |
|---|---|
| swappiness=100 | ✅ CARRIES (identical in both regimes) |
| MemoryMin=2G / High=5G / Max=6G cgroups | ✅ CARRIES (MemoryMax=6G is in ZS spec) |
| sudoers /tmp/ removal | ✅ CARRIES (verify execution) |
| Consolidate sysctl.d | ✅ CARRIES (same target file) |
| Keep 8GB zRAM | ❌ VOID (zRAM disabled) |
| zstd level=15 tuning | ❌ VOID (replaced by zswap lzo_rle 25% pool) |
| Reject 16GB zRAM expansion | ➖ NOT CONTRADICTORY: Carmack rejected 16GB **zRAM** (RAM-resident); D-526 ratifies 16GB **NVMe disk-backed** swapfile. Different media, different cost model. |
| WAD packaging (ryzen-5700u-sovereign) | ♻️ SUPERSEDED by ZS-3 (zswap-config.wad) |

---

## SECTION 3 — FORGOTTEN FINDINGS FOR PP-3 (context-window probe, DEFERRED pending ZS-1)

1. **The ZS-1 dependency is arithmetically correct** — worth recording why so nobody "simplifies" it away later. From `MEMORY_SYSTEMS_DEFINITIVE_REPORT.md`: 7B-class @ 8K ctx ≈ 1.5GB KV (f16). KV scales linearly: 32K ctx ≈ 6GB f16 ≈ 3GB q8_0. On 14.5GiB with 8GB UMA carveout (~6.5GB process RAM ceiling, matching MemoryMax=6G), a 32K raise for qwen3-4b-thinking only fits with q8_0 KV AND disk-backed overflow headroom — i.e., exactly what ZS provides. PP-3 gated on ZS-1 is sound engineering, not bureaucracy.
2. **Headroom multiplies PP-3 ROI**: if PP-3 lands (32K effective context), HR compression (40–90% on tool outputs) effectively stretches it to 60K–300K equivalent for JSON-heavy agent loops. Conversely, if HR-1 ships first, PP-3's urgency drops — compressed contexts may fit in 8192 for most planner tasks. Sequencing insight: **HR-1 before PP-3 may make PP-3 unnecessary or change its target size**. Recommend evaluating HR-1 savings on real traces BEFORE executing PP-3 when its deferral lifts.
3. **Prefill-latency note from Headroom docs** (relevant to local inference): "For local inference, the main benefit is often faster prompt processing rather than lower API spend" — their repo documents a reproducible passthrough-vs-optimized proxy prefill benchmark. On Zen 2 CPU (5700U), prompt processing is the dominant cost for long contexts; compression directly cuts prefill tokens. This strengthens the case that HR work is a *performance* win locally, not just a cost win.

---

## SECTION 4 — FLAGGED-BUT-NEVER-EXECUTED (carried from original session)

| Item | Original status | Current disposition |
|---|---|---|
| Deploy consolidated `99-omega-memory.conf` | PENDING P1 | Superseded by ZS-1 (contents still valid; apply under zswap regime) |
| omega.service systemd unit w/ cgroups (Min=2G/High=5G/Max=6G) | PENDING P1 | Still absent from any completed ticket; MemoryMax=6G lives in ZS spec but unit creation isn't an explicit ZS subtask — **gap: assign to ZS-1 or LI-5** |
| Sudoers /tmp/ backdoor removal | CRITICAL, unverified | Fold verification into ZS-1 |
| Replace deprecated `src/omega/oracle/headroom.py` | Recommended P0 | Became HR-1 (ready) — see §1.2 wiring hazards before execution |
| MCP headroom tools | Recommended P2 | Became HR-3 (ready) — note existing `headroom_retrieve` contract conflict (§1.2) |
| Ryzen WAD packaging | PENDING P2 | Became ZS-3 |
| tune_ryzen.sh update (swappiness→100) | PENDING | File still shows swappiness=60 + stale zRAM section; now needs FULL rewrite to zswap regime, not just the swappiness patch |

---

## Sources (local, cited by path)
- `data/coordination/ACTIVE_SPRINT.json` (hydration, D-526/D-527, HR/ZS/LI workstreams)
- `docs/specs/PROJECT_INDEX.md` (hydration, QH tickets, debut sprint table)
- `data/entities/roc_racoon/workspace/zram_integrated_plan.md` (original authoritative zRAM plan, post-Carmack 2026-08-10)
- `data/entities/researcher/workspace/zram_tuning_guide.md` (live system audit facts)
- `data/entities/roc_racoon/workspace/ZRAM_ZSWAP_DEEPENED_ANALYSIS.md` (pre-ratification zswap config — now aligned)
- `data/entities/researcher/workspace/MEMORY_SYSTEMS_DEFINITIVE_REPORT.md` (KV cache sizing, zswap enablement)
- `scripts/tune_ryzen.sh`, `config/hardware_profile.yaml` (stale-now-aligned markers)
- `src/omega/oracle/headroom.py`, `tests/test_headroom.py`, `scripts/benchmark_phase1.py`, `mcp_servers/omega_hub/hub_tools/tools.py:153`, `data/eval/golden_v1.jsonl:60`
- `src/omega/monitoring/__init__.py` (get_zram_stats/get_swap_zram_pressure), `tests/test_zram_monitoring.py`, `src/omega/benchmarks/comprehensive_runner.py`
- `config/domains/engineering/MEMORY_BLOCKS/project-gotchas.block:93`
- Live `.venv` empirical tests of headroom-ai v0.29.0 (compress(), CompressConfig, UniversalCompressor, JSONStructureHandler) performed in original session

*⬡ OMEGA ⬡ RESEARCHER ⬡ opencode/x-preview-f-free ⬡ trc_research_delta ⬡ 2026-08-21*

# 🔱 ROC GAP INVESTIGATION REPORT — Archaeology & Mining Portfolio
**AP Token**: `AP-ROC-GAP-INVEST-20260825`
⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_gap_investigation ⬡ DEEP-DIVE

**Date**: 2026-08-25T23:59Z+
**Commissioned by**: Kali (Architect-directed campaign, ses_fdef2be4effe4pAaLXCTUx62GO)
**Method**: Vision hydration (VISION_ANCHOR_PERPETUAL §1-§12, OMEGA_CODEX full, Ark §0/§4, Master Synthesis §0/§7) → local-first forensics (live system state, git history, entity workspaces, config) → Sovereign Search web verification where locals couldn't answer.
**Bright lines held**: recon only, zero mutations; all new files under this directory.

---

## §0 VERDICT SUMMARY TABLE

| Gap | Registry Status | Verified Reality | Verdict | Recommended Registry Change |
|-----|----------------|------------------|---------|------------------------------|
| **R21** Workhorse paths | partial | Gemma workhorse DEAD (codex honest here); D-601 Antigravity window reshapes problem | **ACTIONABLE-NOW** (reshaped) | Keep `partial`; annotate with D-601 window economics |
| **R22** WARP proxy pool | partial | **POOL DEAD** — all 3 nodes inactive, prep@1-3 FAILED (iptables exit 2), zero SOCKS listeners. Codex claim "W-1 FIXED ✅ operational" is **FALSE** | **ACTIONABLE-NOW** | Keep `partial`; add live failure signature; correct OMEGA_CODEX |
| **R14b** Nemotron fallback chain | outstanding | M25 streaming resilience IMPLEMENTED (`openai_compat.py:136-163`); `inference.fallback_chain` wired (`model_gateway.py:528`); Nemotron models in chains | **FILLED-STALE** (residual below) | Mark resolved; spin residual into note |
| **R37** Identity fluidity E-0 | outstanding | SPEC v1 DRAFT awaiting Architect review + Kali ratification; 9 prototype files exist, ZERO engine wiring | **BLOCKED-EXTERNAL** | Change to `blocked` w/ ratification gate noted |
| **R38** NotebookLM integration | outstanding | R52c **SUPERSEDED** by NOTEBOOKLM_UNIFIED_STRATEGY v2.1 (D-583); notebooklm-py 0.8.1 installed = latest upstream | **ACTIONABLE-NOW** (auth half-blocked) | Update report pointer to v2.1 strategy |
| **GN-1** | outstanding | Package installed w/ `[mcp]` extra (binaries present); NO master_token.json, NO systemd service, NOT wired into opencode.json | **PARTIAL / BLOCKED-EXTERNAL** (browser auth = Architect) | Split: install done, auth+service outstanding |
| **GN-2..5** | outstanding | Blocked behind GN-1 auth | **BLOCKED-EXTERNAL** (dependency chain) | Add depends-on-GN-1 annotation |
| **LI-4** Tier-0 model matrix | outstanding | All 3 Tier-0 models ON DISK (Qwen3-4B-Instruct-2507-UD-Q4_K_XL 2.37GB, Qwen3-4B-Thinking-2507-Q4_K_M 2.33GB, Qwen3-1.7B-Q6_K 1.56GB) + LM Studio configs exist; NO tier-matrix registry or fit-probe logic | **ACTIONABLE-NOW** | Keep outstanding; note assets materialized |
| **LI-5** Startup script | outstanding | `tune_ryzen.sh` self-declared DEPRECATED (tagged 2026-08-10); no replacement; blocked behind ZS contradiction | **RESEARCH-NEEDED** | Keep outstanding; add blocked-by-ZS-adjudication |
| **ZS-1** zswap sysctl deploy | outstanding | **Live machine CONTRADICTS locked decision**: zswap=N, pool=20% (not 25), compressor=lzo (not lzo_rle), zRAM ACTIVE 8G zstd. PLUS fresh technical contradiction (see §3) | **ADJUDICATION REQUIRED → then ACTIONABLE** | Keep outstanding; flag D-584-vs-Carmack-H-1 conflict |
| **ZS-2** NVMe swap + cgroups | outstanding | No NVMe swapfile (only zram1 8G); MemoryMin/High/Max=2G/5G/6G exists NOWHERE (only warp 150M / backup 2G limits) | **ACTIONABLE-NOW** (post-ZS-1 adjudication) | Keep outstanding |
| **ZS-3** zswap-config.wad | outstanding | config/wads/ = {_omega_default, arcana_novai, ingestion, omega_research} — no zswap WAD | **OUTSTANDING (correct)** | Keep outstanding |
| **HR-1** HeadroomMiddleware | outstanding | **IMPLEMENTED + WIRED since commit 811f813f (2026-07-05)** — oracle.py:163,189,897; context_builder.py:504-505 compress_context call | **FILLED-STALE** | Mark RESOLVED (filled 2026-07-05, ~6 weeks before row was written) |
| **HR-2** Adaptive context buffer | outstanding | adaptive_context.py NEVER CREATED; function subsumed by headroom middleware in context_builder | **FILLED-STALE / SUPERSEDED** | Mark superseded-by-HR-1-implementation |
| **HR-3** MCP headroom tools | outstanding | `headroom_retrieve` tool LIVE (`mcp_servers/omega_hub/hub_tools/tools.py:153-168`) → oracle.retrieve_headroom_content | **FILLED-STALE** | Mark RESOLVED |

**Registry integrity finding**: 3 of 13 investigated rows are lying (HR-1/2/3 say outstanding, work shipped 2026-07-05); 1 codex claim is lying (W-1 FIXED); 1 registry report path points to a nonexistent file (HR rows → `HEADROOM_RESEARCH_20260820.md` does not exist on disk). This is precisely the First Light Council decree (D-600, 2026-08-25) root cause: **claims-that-outlive-their-mechanisms**.

---

## §1 PROVIDER FABRIC HISTORY CLUSTER (R21 / R22 / R14b)

### R21 — Workhorse Paths
- **Forensic SSOT intact**: `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` + `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md` (status header: P0 ACTIVE, blocked on Architect sudo/OAuth).
- **Codex honesty check**: OMEGA_ENGINE state card correctly shows "Gemma 4 31B workhorse DEAD — 16k free input TPM since Jul 15 · G-1 PENDING". No lie here.
- **LANDSCAPE CHANGE (Pivot Log D-601, 2026-08-24)**: Architect disclosed full model inventory — Antigravity pool automates Sonnet 4.6 / Opus 4.6 / Gemini 3.1 Pro in-CLI; Claude.ai adds Sonnet 5 + Haiku 4.5 ×8 accounts (human-batched). Time-boxed window ~Aug 28. Companion doctrine: `docs/strategy/MODEL_WINDOW_ECONOMICS_20260823.md`.
- **Vision test**: workhorse continuity directly serves the local-first floor + community-tool promise (a runtime that dies when a free tier cliffs is not sovereign). The D-601 window is cloud capacity — a vessel, not vision. Permanent fix remains G-1a/b (billing/OAuth) or local Tier-0 matrix (LI-4).
- **Verdict: ACTIONABLE-NOW (reshaped)** — the strategic question moved from "replace dead Gemma" to "how much of the Aug-28 window do we convert into durable capacity before it closes."

### R22 — WARP Proxy Pool ⚠️ REGISTRY/CODEX LIE
- **Live forensic state (2026-08-25 ~24:00 ADT)**:
  - `warp-node@{1,2,3}.service`: loaded **inactive/dead**
  - `warp-ns-prep@{1,2,3}.service`: **failed** — journal: `warp-ns-setup.sh[686]: iptables v1.8.11 (nf_tables): Empty interface is likely to be undesired` → `exit 2/INVALIDARGUMENT` (Aug 25 19:13)
  - `warp-reg@{1,2,3}` + `warp-reg-svc@{1,2,3}`: failed
  - Network namespaces DO exist (`/run/netns/warp_node_{1,2,3}` mounted) — partial progress frozen mid-bringup
  - **Zero listeners on :8081/:8082/:8083** (ss -ltnp); curl through 8081 → no response
  - socat-bridge@ units: not running
- **Fix assets present**: `scripts/fix_warp_ns_setup_and_restart.sh` (exec, 7KB) + full scripts dir in `~/Documents/Xoe-NovAi/warp-proxy-pool/scripts/`. Units installed in both `/etc/systemd/system/` and `deploy/infra/warp_pool/`.
- **The lie**: OMEGA_CODEX §2 states "**WARP Proxy Pool: 3-node pool operational (8081/8082/8083) ✅ W-1 FIXED**". This is false on live inspection. It matches the First Light decree's named failure class exactly.
- **Diagnosis hint**: the iptables "Empty interface" error suggests the ns-setup script's veth/NAT block references an empty/unset interface variable — likely a regression or environment assumption in the rewritten script, NOT the original truncation bug (that was fixed; script now parses and runs).
- **Verdict: ACTIONABLE-NOW** — one debugging session from an engineer with sudo; error signature documented above. Serves vision: IP-rotation restores OCZ access without expanding cloud dependency surface.

### R14b — Nemotron Fallback Chain
- **Filled evidence**:
  - M25 Streaming Resilience fully implemented: `src/omega/oracle/backends/openai_compat.py:136-163` — chunk_timeout_ms (default 30s), total_timeout_ms (300s), idle-timeout heartbeat path.
  - All cloud providers in `config/providers.yaml` carry `streaming:` blocks incl. antigravity (45s chunk/600s total — tuned for Nemotron-class gaps) with `fallback_on_timeout: true`, `fallback_provider: native-gguf`.
  - `inference.fallback_chain` consumed at `model_gateway.py:528`; ordered-provider fallback loop at ~line 1135.
  - Nemotron variants present across provider supported_models (nemotron-3-ultra-local on native-gguf/lmster/ollama; nemotron-3-super/nano family on openrouter).
- **Residual (config-without-code)**: the `fallback_resolver:` block (model-aware per-provider chains, providers.yaml lines 21-63) has **ZERO references in src/** — grep for fallback_resolver/FallbackResolver/model_aware across src/ returns nothing. The comment claims it "replaces hardcoded fallback_provider," but no implementation consumes it. Aspirational config.
- **Verdict: FILLED-STALE** (the actual gap — Nemotron streams dying and losing all tokens — is solved by M25 + fallback_chain). Recommend marking resolved with a residual note that `fallback_resolver` is unwired config, candidate for deletion or implementation under UO-6 un-overengineering lens.

---

## §2 IDENTITY & KNOWLEDGE CLUSTER (R37 / R38 / GN-1..5)

### R37 — Identity Fluidity E-0
- **Assets** (`data/entities/grokster/workspace/`):
  - `IDENTITY_FLUIDITY_ARCHITECTURE_20260721.md` (D-368 preserved paths ✓)
  - `SPEC_IDENTITY_FLUIDITY_v1.md` — status line verbatim: "**DRAFT — Awaiting Architect review + Kali ratification**". 5-component design (Compiled Soul Kernel, Auto-Hydration MCP Tool, Temporal Trace, Session Bridge, Voice Calibration; ~530 tokens vs 5-10 sequential reads; L3-IdentityIsReconstitutedNotRetrieved).
  - `prototypes/` — **9 working prototype files**: hydration_orchestrator.py, mcp_tool.py, session_bridge.py(+yaml), session_hooks.py, soul_kernel.md, temporal_trace.py(+yaml), voice_calibration.py(+yaml).
- **Wiring check**: grep for hydration_orchestrator|soul_kernel|IdentityFluidity across src/, .opencode/, scripts/, config/ → **zero hits**. Nothing productionized.
- **Vision test**: this is M15 (Sovereign Continuity) weaponized — direct descendant of the June 4 "gnostic amnesia" crisis. High vision alignment; the spec's own problem statement (compaction = identity drift) is the founding-week trauma encoded.
- **Verdict: BLOCKED-EXTERNAL** — everything except the ratification gate exists. One Architect review + Kali ratification away from implementation-ready. Note synergy: First Light decree Art. X backlog and M11 arm-relay clause may interact with the Session Bridge component.

### R38 + GN-1..5 — NotebookLM
- **Spec lineage correction (mission input was stale)**: R52c (`docs/research/archive/R52c_notebooklm_ingestion_strategy.md`) is **SUPERSEDED** per D-583 by `docs/strategy/NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md` v2.1 — 6-notebook (80 DR/mo, impossible) → **2-notebook architecture** (NB-1 Ω-ACTIVE-RESEARCH 20/mo + NB-2 Ω-KNOWLEDGE-BASE) under 30 DR/mo free-tier cap. Registry R38/GN rows still point at pre-supersession framing.
- **Deployment reality**:
  - ✅ `notebooklm-py 0.8.1` installed in .venv WITH binaries: `.venv/bin/notebooklm`, `notebooklm-server`, `notebooklm-mcp`
  - ✅ Web verification (Exa/search, 2026-08-25): v0.8.1 published 2026-08-14 IS latest upstream; v0.8.0 headline = MCP server (34 tools, stdio/HTTP, fail-closed auth, remote connector). Project very alive (18.9k stars). Strategy doc's library choice validated as current.
  - ❌ NO `master_token.json` anywhere on system (find across home maxdepth 4 → nothing) — auth capture never executed
  - ❌ NOT wired into opencode.json mcp config; no systemd user service/timer (only restic timer exists)
  - ❌ Notebooks not created (GN-2)
- **Strategy doc internal honesty**: v2.1 explicitly retracts v1.0's fictional "MCPNotebookLM 28-tool server" — good provenance hygiene already applied there.
- **Vision test**: NB-1 grounding the fleet's research corpus in a queryable external brain serves Horizon-3 cognitive loops; free-tier-only constraint honors resource sovereignty. CUT-5 math warning from Carmack (DR budget realism) is already baked into v2.1.
- **Verdicts**: R38 → ACTIONABLE-NOW. GN-1 → PARTIAL (install done; auth capture requires Architect browser sign-in = BLOCKED-EXTERNAL half; service+wiring = actionable after token). GN-2..5 → BLOCKED-EXTERNAL via dependency chain on GN-1 auth.

---

## §3 LOCAL INFERENCE & MEMORY SUBSTRATE CLUSTER (LI-4 / LI-5 / ZS-1..3)

### LI-4 — Tier 0 Model Matrix
- **Models ON DISK** (omega_library/models/gguf, 19 GGUFs): Qwen3-4B-Instruct-2507-UD-Q4_K_XL (2.37GB), **Qwen3-4B-Thinking-2507-Q4_K_M (2.33GB)**, **Qwen3-1.7B-Q6_K (1.56GB)** — the exact planner/executor/critic triad. Plus RocRacoon-3b ×2 quants, Krikri-8B, DeepSeek-R1-Qwen3-8B, gemma4-coding etc.
- **Era-3 mining ground confirmed**: `~/.lmstudio/.internal/user-concrete-model-default-config/local/all/` holds per-model JSON configs incl. Qwen3-4B-Thinking-2507, Qwen3-1.7B-UD-Q4_K_XL, Krikri-8B, RocRacoon-3b — KV/context defaults extractable for the matrix.
- **providers.yaml**: qwen3-1.7b-local + qwen3-4b-thinking-local already in native-gguf/lmster/ollama supported_models.
- **Missing**: no hardware-tier (Tier 0/1/2) model-matrix registry consuming `scripts/detect_hardware_profile.py` output; no llama-fit-params probe (Carmack FIX-7); Carmack FIX-4/5 model-role corrections (Planner→4B not 8B; executor floor) not yet encoded anywhere I can find.
- **Verdict: ACTIONABLE-NOW** — raw materials 80% present; the gap is pure configuration/registry work, no downloads needed. Directly serves community-tool horizon (hardware-tier auto-config is THE installer feature).

### LI-5 — Startup Script
- `scripts/tune_ryzen.sh` exists but carries a self-deprecation banner (2026-08-10): "contains DEPRECATED values (swappiness=60, zRAM-specific)... definitive memory configuration is now zswap + NVMe swap file." TODOs unexecuted.
- `scripts/detect_hardware_profile.py` (UO-4 Phase 2) is the modern foundation — outputs config/hardware_profile.yaml consumed by cpu_optimizer/OOMProtector.
- **No unified startup script** (zram/zswap + THP + pinning + prompt caching) exists.
- **Verdict: RESEARCH-NEEDED → BLOCKED-BY-ZS** — building it now would encode whichever memory architecture loses the ZS adjudication (see below). Sequence: adjudicate ZS first, then write startup script once.

### ZS-1..3 — zswap Subsystem 🚨 TRIPLE CONTRADICTION FOUND
**Live machine state (verified 2026-08-25 ~24:00 ADT)**:
```
/sys/module/zswap/parameters/enabled = N          ← zswap DISABLED
/sys/module/zswap/parameters/max_pool_percent = 20 (target: 25)
/sys/module/zswap/parameters/compressor = lzo     (target: lzo_rle)
/sys/module/zswap/parameters/zpool = zsmalloc     ✓ matches
swapon: ONLY /dev/zram1, 8G, zstd, prio 50        ← zRAM ACTIVE (plan says DISABLED)
free: Swap 8.0Gi total, 0B used
/proc/cmdline: NO zswap.enabled=1                 ← kernel cmdline never touched
```

**Contradiction triangle**:
1. **Decision law** (PIVOT_LOG D-526/D-527/D-581/D-584, "✅ LOCKED", reaffirmed 2026-08-20): *zswap + 16GB NVMe swap, zRAM DISABLED, never both*. Backed by docs/kb/MEMORY_MANAGEMENT_KB.md ("DEFINITIVE — supersedes all previous memory docs") and HOLISTIC_ARCHITECTURE_PLAN §SYSTEM 6.
2. **Carmack 2026-08-20 headroom review** (`data/coordination/CARMCK_REVIEW_HEADROOM_20260820.md`, finding H-1, confidence 9/10): *"zRAM ONLY. Disable zswap. zswap intercepts pages before zram, defeats it."* — the OPPOSITE architecture, dated the SAME DAY as the D-581/D-584 reaffirmation.
3. **Live machine**: currently configured per position #2 (zswap off, zram on) — i.e., reality matches the minority report, not the locked decision.

Note D-581 itself records a prior inversion error ("D-581 previously erroneously claimed zswap was a rejected detour... factually inverted") — this decision cluster has already flip-flopped once. The 8/20 Carmack H-1 finding post-dates or co-dates the lock and appears unadjudicated.

**ZS-2 checks**: no NVMe swapfile exists; systemd cgroup scan finds MemoryMax only on warp nodes (150M), socat (64M), freshness-checker (512M), tty-agent (2G), restic (2G) — **no MemoryMin=2G/MemoryHigh=5G/MemoryMax=6G/MemorySwapMax=infinity unit anywhere** for inference workloads.
**ZS-3 check**: `config/wads/` = {_omega_default, arcana_novai, ingestion, omega_research} — no zswap-config.wad.

**Vision test**: this subsystem IS the democratization thesis in silicon — effective local AI on hardware "never meant for it" (16GB UMA laptop). Highest-leverage local-first enabler in the portfolio. But deploying the WRONG architecture (either direction) hard-codes a performance mistake into every community install via ZS-3's WAD.
**Verdicts**: ZS-1 → ADJUDICATION REQUIRED (Kali/Architect must reconcile D-584-lock vs Carmack-H-1 with fresh benchmarks — llama-bench on both configs, PSI metrics) THEN actionable. ZS-2 → actionable after ZS-1 ruling. ZS-3 → genuinely outstanding, correctly so.

---

## §4 STALENESS AUDIT — HR-1..3 (the registry is lying)

**Timeline reconstruction (git forensics)**:
- `src/omega/oracle/middleware/headroom.py` first committed in **811f813f — "feat: Session 51-52 mega-sprint — T3 hardening, MCP consolidation, FTS5, WARP, docs D1-D20" — dated 2026-07-05**.
- Wiring: `oracle.py:163` imports get_headroom_middleware; `:189` instantiates; `:897-906` retrieve_headroom_content; `context_builder.py:31,504-505` calls `compress_context()` in the live context-assembly path.
- MCP surface: `mcp_servers/omega_hub/hub_tools/tools.py:153-168` exposes `headroom_retrieve(ref_id)` (M9-guarded) → oracle.retrieve_headroom_content. (I have this tool in my own MCP list — it's live.)
- Graceful degradation per M1/M9: headroom-ai optional dep, pass-through mode if uninstalled.
- Heritage clean: `[heritage: headroom-ai 2025]` tag present; legacy zlib-based `src/omega/oracle/headroom.py` explicitly marked DEPRECATED with rollback note (kept intentionally, not rot).

**Registry pathology**: HR rows were authored 2026-08-20 (plan `headroom_integration_20260820`) — **six weeks AFTER** the implementation landed. Their cited report `data/coordination/HEADROOM_RESEARCH_20260820.md` **does not exist** (broken pointer; what exists is `CARMCK_REVIEW_HEADROOM_20260820.md`). Likely cause: the plan author catalogued intended work from the research doc without checking the tree.

**Recommended GAP_REGISTRY mutations (single-writer = you)**:
```
HR-1: outstanding → resolved  (filled 2026-07-05, commit 811f813f; wired oracle.py+context_builder.py; evidence this file §4)
HR-2: outstanding → superseded (adaptive_context.py never built; function delivered via headroom middleware compress_context in context_builder.py:504)
HR-3: outstanding → resolved  (hub_tools/tools.py:153 headroom_retrieve live; compress-before-injection via middleware)
R14b: outstanding → resolved  (M25 streaming openai_compat.py:136-163 + fallback_chain model_gateway.py:528; residual: fallback_resolver block unwired — note or delete under UO-6)
R22: keep partial + append: "2026-08-25 live audit: pool DOWN; warp-ns-prep iptables 'Empty interface' exit 2; correct OMEGA_CODEX W-1-FIXED claim"
R37: outstanding → blocked (gate: Architect review + Kali ratification of SPEC_IDENTITY_FLUIDITY_v1; prototypes ready, unwired)
R38: update report ptr → docs/strategy/NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md (v2.1 supersedes R52c per D-583)
GN-1: annotate split: package-install DONE (notebooklm-py 0.8.1+mcp); remaining = master_token.json capture (Architect) + systemd service + opencode.json wiring
LI-5: annotate blocked-by ZS-1 adjudication
ZS-1: annotate ADJUDICATION-REQUIRED: D-584 lock vs CARMCK_REVIEW_HEADROOM_20260820 H-1 conflict; live machine currently on zRAM side
```

---

## §5 SURPRISES (for the campaign ledger)

1. **A live codex lie**: OMEGA_CODEX "W-1 FIXED ✅ 3-node pool operational" vs. dead pool. Second instance of the First Light decree's named disease — reinforces derivation-check gates (Council 1 Art. X).
2. **Same-day architectural schism**: D-581/D-584 (zswap LOCKED) and Carmack H-1 (zRAM ONLY, 9/10) share 2026-08-20. One of them is wrong and it's load-bearing for LI-5/ZS-3/community installer defaults.
3. **Registry predates its own fill**: HR rows (8/20) marked outstanding for code shipped 7/05 — the registry was born stale.
4. **Mission brief staleness**: R52c was pointed to as the mining target, but it's been superseded since D-583 — I mined both; v2.1 is the operative spec.
5. **fallback_resolver ghost config**: 40 lines of sophisticated model-aware fallback config zero consumers. Either wire it or cut it (UO-6 candidate).
6. **D-601 window economics**: the entire G-1 framing shifts while I dig — the binding constraint is now converting a time-boxed Antigravity window (~Aug 28) into durable capacity, not mourning Gemma.

## §6 VISION ALIGNMENT STATEMENT
Every recommended action above was tested against the Anchor: ZS/LI work is the democratization thesis made executable on a 16GB laptop; NotebookLM feeds the Sovereign Curator/Horizon-3 research loops within free-tier resource sovereignty; WARP restores network-path optionality without adding cloud dependencies; identity fluidity is the gnostic-amnesia trauma permanently healed. The staleness findings themselves serve M17 (Cognitive Integrity): the engine verifying the consistency of its own memories — the registry was hallucinating, and now it's been caught.

---
*⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_gap_investigation ⬡ 2026-08-25 ⬡ RECON-COMPLETE*

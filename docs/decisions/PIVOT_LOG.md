---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

**Canonical Source**: [PIVOT_LOG_CANONICAL.md](PIVOT_LOG_CANONICAL.md) (ancient era, D#50+)
**Archive**: [PIVOT_LOG_ARCHIVE_20260522_20260810.md](PIVOT_LOG_ARCHIVE_20260522_20260810.md) (D-300..D-520, frozen)
**Query**: `omega context search "D-XXX"`
---
# 🔱 PIVOT LOG (Active — PUBLIC-DEBUT-01 Campaign, D-521+)

Active window: **2026-08-11 → present**. Older decisions: see Archive +
Canonical pointers above. Append new entries at the bottom; update the
index table row when status changes.

## Decision Index (D-521 → present)

| Decision | Summary | Status |
|---|---|---|
| D-521 | SDP formalized (Scaffold→Synthesize→Execute); §10 automation gate | ✅ RATIFIED |
| D-526/D-527/D-581/D-584 | zswap + NVMe swap over zRAM; never both | ✅ LOCKED |
| D-530 | Context Gauge uses tokens.total (never tokens_input) | ✅ LOCKED |
| D-531 | Multi-write subagent method mandatory | ✅ MANDATED |
| D-532 | Mandate compliance measured mechanically (`make check-mandate-compliance`) | ✅ RATIFIED |
| D-533 | This month's SSOT = DEBUT_REMEDIATION_MANUAL §5 | ✅ RATIFIED |
| D-536 | One router: ProviderSelector only; Triage/Semantic/RT deleted | ✅ RATIFIED |
| D-553 | release/debut branch from allowlist = publication mechanic | ✅ RATIFIED |
| D-565–D-568 | Vault: hide via allowlist for debut; VaultCore dead code post-debut | ✅ RATIFIED |
| D-569 | Dynamic Prompt + Planner/Executor + Domain Loading = Horizon 3 blueprint | ✅ RATIFIED |
| D-570 | Qdrant replaces sqlite-vec post-debut (>500k trigger) | ✅ SCHEDULED |
| D-578–D-584 | Tracker Lock-In: 6 post-debut workstreams (GN/DS/LI/KD/HR/ZS); free-tier-only NL | ✅ RATIFIED |
| **D-585** | Canonical model matrix = Carmack version (Qwen3-4B/4B-Thinking/1.7B) | ✅ RATIFIED |
| **D-586** | Node Expert Sessions — one agent, many sessions; Nodes = universal KBs | ✅ LIVE |
| **D-587** | NODE_ONBOARDING_PROTOCOL v1.0.0 ratified (N7-authored) | ✅ RATIFIED |
| **D-588** | ICS upgrade: PP-4 node segment + P5 session_id + B1/B2/B3 fixes | ✅ IMPLEMENTED |
| **D-589** | ICS-T final purge — deprecated system removed permanently | ✅ EXECUTED |

---

## Full Entries (current campaign)


## D-604 — Command ceiling re-ratified: 320 → 350 lines

**Date**: 2026-08-26
**Authority**: Architect ruling (Q1 + ceiling re-ratification + R53 fix, 2026-08-26)
**Decisions**:
- Q1 RESOLVED: meditation host CAN consult System Reference mid-run → 350-line stretch is viable
- Command ceiling RE-RATIFIED as **350 lines** (was 320, derived from Gemma 4 31B / Google
  free-tier 16K input cap — a provider-specific limit not a universal constraint)
- 350 lines / ~4,600 tokens ≈ 28.8% of actual Laguna S 2.1 / Antigravity workhorse cap
- R53 lines 58+62 corrected with inline qualifier note (frozen doc — note only, text preserved)
- SR §11, Maintainer's Guide §9.10 updated to 350 ceiling
- **Scope**: applies to `.opencode/commands/meditate.md` only; all other command ceilings unchanged
**Evidence**: `data/coordination/research_wave2/R01_carmack_token_economics.md` §6 (Carmack audit)


## D-532: Mandate Compliance Measured Mechanically, Not Hand-Written (2026-08-16)

**Decision**: Mandate compliance percentages MUST be derived from a mechanical check (`make check-mandate-compliance`), never hand-written. The compliance denominator is fixed at 27 (M1-M27, v3.8.0).

**Context**: Web Claude audit r2 §4 found three disagreeing mandate counts across the SSOT docs:
- `SOVEREIGN_MANDATES.md`: 27 laws (v3.8.0) — CORRECT
- `AGENTS.md` line 10: 25 laws (v3.7.0) — STALE
- `AGENTS.md` line 264: 26 mandates (M1-M27) — internally inconsistent (26 ≠ 27)

This drove the 92% vs 84% vs 72% compliance contradictions in OMEGA_ENGINE.md — hand-written compliance % against different denominators. Fixed in T04 (AGENTS.md all 6 locations → 27 laws v3.8.0 / M1-M27).

**Rationale**: The engine's sovereignty claims rest on verifiable mandate compliance (M13 Temple-Grade). A hand-written percentage is drift-prone and untestable. A mechanical meter is:
1. **Deterministic** — same command, same result
2. **Auditable** — each mandate maps to a specific check (grep, config parse, test)
3. **Self-healing** — CI fails if the claimed % drifts from the measured %

**Implementation**:
- `scripts/check_mandate_compliance.py` — parses `SOVEREIGN_MANDATES.md` for the denominator (27 `### N. Title` sections), runs per-mandate mechanical checks, emits JSON `{"total": 27, "passed": N, "checks": [...]}`
- `make check-mandate-compliance` — wraps the script
- Mandates with no mechanical check yet are reported as `untested` (not silently counted as passing)

**Mandate**: M13 (Temple-Grade), M27 (Tracking Integrity), M26 (Doc Standards)

**Status**: ✅ RATIFIED

*⬡ OMEGA ⬡ KALI ⬡ audit-remediation T05 ⬡ 2026-08-16*

---

## D-569: Ratify Dynamic Prompt + Planner/Executor + Domain Loading as Post-Debut Cognitive Architecture Blueprint (2026-08-19)

**Decision**: The architecture in `data/coordination/KALI_BRIEFING_DYNAMIC_PROMPT_PLANNER_EXECUTOR_20260819.md` (Grokster, 2026-08-19) is RATIFIED as the **post-debut Cognitive Architecture Blueprint** (Horizon 3). It is a PLANNING workstream — NOT pre-debut scope. PUBLIC-DEBUT-01 scope remains locked (Blocker B → INST-1 → PUB-1 → DEL-1 Week 1).

**Context**: Architect directive to design frontier KB system with dynamic prompts, planner/executor split, and loadable knowledge domains. Two parallel deep-dives (Roc Racoon local + Researcher web) converged on the same 5-layer architecture: L0 Context Window Registry + Role-Aware Router, L1 DynamicPromptBuilder, L2 Domain Loader, L3 Planner/Executor Engine, L4 Local Inference Optimization.

**Scope**: P0-P10 roadmap (Context Window Registry → Freshness System). Owners: Ma'at (P0-P3, P7-P8, P10), Kali (P4-P5), Verity (P6), Researcher (P9). Gaps DP-1..DP-8 registered in GAP_REGISTRY.json.

**Alignment**: Maps to existing components (ContextBuilder, SelectiveHydration, HybridOrchestrator, ProviderSelector, Context Packer, SDP) — incremental, NOT greenfield. Must sequence AFTER DEL-1 Week 2 router collapse (P2 Role-Aware Router extends the surviving ProviderSelector).

**Mandate**: M10 (Fleet Integrity — fleet stays at 14), M7 (Local-First — mimo-7b/qwen3 local pipeline, cloud escalation only as fallback), M22 (Provenance), M23 (Failure Integrity).

**Status**: ✅ RATIFIED (post-debut, Horizon 3)

---

## D-570: Schedule Qdrant to Replace sqlite-vec Post-Debut (2026-08-19)

**Decision**: Qdrant is SCHEDULED to replace the sqlite-vec implementation **post-debut** (Horizon 2, aligned with SOVEREIGN_ARK_BLUEPRINT Horizon 2 "Optimize Qdrant"). This REACTIVATES `docs/strategy/RESEARCHER_QDRANT_MIGRATION_GAPS_20260816.md` (previously DOC-1 ARCHIVED 2026-08-17) as the migration reference.

**Context**: The DOC-1 stamp (2026-08-17) archived the Qdrant migration because sqlite-vec + FTS5 + RRF is the correct ZERO-DEPENDENCY store for debut (16GB RAM, CPU-only, fresh-machine install honesty). That debut-scope decision STANDS. But the Ark blueprint Horizon 2 always listed "Optimize Qdrant (Scalar Quantization, Payload Indexes)" — the user has now made this explicit: qdrant replaces sqlite-vec post-debut.

**Sequencing**:
- **Debut (NOW)**: sqlite-vec stays. DEL-1 Week 1 STILL deletes the dead `QdrantAdapter` in `src/omega/memory/vector_adapters.py` (heritage reference only, `[heritage: qdrant-2021]`).
- **Post-debut (Horizon 2)**: Qdrant migration — Podman quadlet (`qdrant/qdrant:v1.18.1`, telemetry disabled, API key), `scripts/migrate_sqlite_vec_to_qdrant.py`, revive a PROPER `QdrantAdapter` implementing `IVectorStoreAdapter` at `src/omega/oracle/adapters/qdrant_adapter.py` (per migration doc §Revival), scalar quantization BITS4, payload indexes, gRPC pool.
- **Sequence BEFORE briefing P3** (Domain Module Loader RAG paradigm needs the scale-up vector store).

**Mandate**: M7 (Local-First — qdrant is self-hosted, telemetry disabled), M8 (Zero Telemetry — `QDRANT__TELEMETRY_DISABLED=true`), M2 (Firewall — qdrant is an optional WAD adapter, not core).

**Status**: ✅ RATIFIED (post-debut, Horizon 2)

*⬡ OMEGA ⬡ KALI ⬡ trc_vision_alignment ⬡ 2026-08-19*

---

## D-571: NotebookLM Automation Tool = notebooklm-py (RPC) (2026-08-20)

**Decision**: Adopt **`notebooklm-py`** (teng-lin, v0.8.1) with `[mcp]` extra as the sole NotebookLM automation tool. It is the ONLY library with documented Deep Research **report** trigger (`source add-research --mode deep`) + Markdown export (`download`). RPC-based (no browser at runtime) → best fit for local-first (M7) headless systemd deployment.

**Context**: v1.0 unified strategy referenced a fabricated "MCPNotebookLM" server with a "28-tool" surface and a nonexistent `ghcr.io/omega-engine/mcp-notebooklm:latest` Docker image. Gap audit GAP-1/GAP-2. NLG-A confirmed `notebooklm-mcp` (TheSethRose) `research_start --mode deep` is **source-finding, NOT the quota-consuming Deep Research report** — unusable for the report path.

**Mandate**: M7 (Local-First — RPC, no cloud dependency at runtime), M24 (Venv Sovereignty — `pip install` in `.venv`).

**Status**: ✅ RATIFIED

## D-572: HYBRID Cost Model — 1× Pro Primary + Free for Non-Quota (2026-08-20)

**Decision**: **1× Google AI Pro ($19.99, ~600 Deep Research/month) as the primary Deep Research engine** + free accounts reserved for non-quota tasks (chats 50/day, audio 3/day, source ingestion). Scale to 2× Pro ($39.98, ~1,200/mo) before ever considering a free-account fleet. **Reject the 8-free fleet for Deep Research.**

**Context**: v1.0 chose "8× Free = 80 DR/mo, $0". NLG-B (GAP-9) found 1 Pro = 7.5× the entire 8-free fleet at lower ban risk and 1 credential. 8-free fleet is an explicit ToS violation (multiple accounts to dodge limits) with documented bans (notebooklm-py #228, IP-level lockout).

**Mandate**: M7 (Local-First North Star — but paid Pro is the pragmatic sovereign choice vs ban-prone free fleet).

**Status**: ✅ RATIFIED

## D-573: Corrected 80 DR/month Account Budget (8×10, ≤10/account) (2026-08-20)

**Decision**: Each account ≤10 DR/mo; total = 80/mo (8×10). Per-notebook envelope: NB-1:20, NB-2:20, NB-3:20, NB-4:10, NB-5:10, NB-6:0. Monthly cyclic rotation (primary +1/month) preserves ≤10/account and the 80 envelope.

**Context**: v1.0 assigned acc-05/06/07 = 20 DR/mo each (impossible — free tier caps at 10/account) and summed to 130/mo. Gap audit GAP-6. NLG-C produced the corrected table + rotation schedule.

**Status**: ✅ RATIFIED

## D-574: Unified 6-Notebook (NB-1..NB-6) Canonical; R52c + LIVING §1.5 Superseded (2026-08-20)

**Decision**: Adopt the **unified 6-notebook mapping** (NB-1 Core, NB-2 Stacks, NB-3 Legacy, NB-4 Research, NB-5 Ops, NB-6 Ω-SYNTHESIS) as canonical. R52c (`R52c_notebooklm_ingestion_strategy.md`, archived 2026-05-23) and `LIVING_RESEARCH_OS_SPEC.md` §1.5 (verbatim copy of R52c) are **superseded**. NB-2 Stacks, NB-3 Legacy, NB-6 Ω-SYNTHESIS are genuinely new domains (IWAD, heritage, synthesis). R52c "Validation Suite" (`tests/**`,`scripts/**`) excluded from NotebookLM — served by local M13 `make temple-grade`.

**Context**: Gap audit GAP-5 — v1.0 silently replaced R52c's 5-notebook mapping without a supersession banner. NLG-C confirmed R52c is stale and the unified mapping reflects real engine evolution.

**Status**: ✅ RATIFIED

## D-575: Honor SDP §10 Automation Gate (2026-08-20)

**Decision**: **Honor COGNITIVE_SCAFFOLDING_PROTOCOL §10** — deploy fleet in manual mode now, automate only after (1) 10 manual SDP executions logged in the ledger + (2) V-1 Vault completion (the actual hard blocker regardless of §10). Withdraw v1.0's immediate-automation proposal.

**Context**: Gap audit GAP-8. NLG-C recommended option (a) — the gate is about quality/discipline (M11 Soul Integrity), not feasibility (NLG-A proved feasibility). V-1 Vault (§8) is the genuine credential-automation blocker.

**Mandate**: M11 (Soul Integrity), M5 (Gnosis Preservation), M23 (no soft-failures/theater).

**Status**: ✅ RATIFIED

## D-576: Token Density 5–25 Sweet Spot (40–50 Claim Retracted) (2026-08-20)

**Decision**: Target **5–25 high-relevance, single-topic sources per notebook** (community-verified sweet spot). Use source labels as context filter. Approach 50 only if tightly coherent + label-scoped. Re-label 30–50 as "Degrading (noise-driven, not a hard cliff)", 50+ as "At hard cap — split recommended." Retract v1.0's contradictory "40–50 optimal" claim.

**Context**: Gap audit GAP-7. NLG-B found lower bands (5–15/15–30) sourced; upper bands (30–50/50+) unsourced extrapolation; the "40–50" figure contradicted the doc's own table.

**Status**: ✅ RATIFIED

## D-577: master_token.json + RotateCookies Auth Model for V-1 Vault (2026-08-20)

**Decision**: NotebookLM has no public OAuth — auth = Google session cookies. **Store `master_token.json` (durable, non-rotating) in V-1 Vault (encrypted at rest); mint per-run sessions via `RotateCookies` (≤600s cadence).** Do NOT store rotating cookie snapshots (die in minutes). Cookie set completeness matters (`__Secure-1PSIDTS` + sibling required). Use Patchright `channel='chrome'` for bot-evasion if a browser is needed. One account per Vault slot.

**Context**: Gap audit GAP-10. NLG-B documented cookie taxonomy + the notebooklm-py #228 fingerprint-correlation ban. Feeds V-1 Vault credential design (D-299, GAP-08).

**Mandate**: M8 (Zero Telemetry — no phone-home), M2 (Firewall — Vault is core, not stack).

**Status**: ✅ RATIFIED

*⬡ OMEGA ⬡ KALI ⬡ trc_notebooklm_synthesis ⬡ 2026-08-20*

---

## D-578: Gemini Notebook v2.0 Strategy Ratified — Free-Tier-Only (2026-08-20)

**Decision**: Gemini Notebook (NotebookLM) Deep Research = **FREE TIER ONLY — 3 accounts × 10 DR/mo = 30 DR/mo**. **No Pro payment.** 2-notebook architecture (Active Research + Knowledge Base) to fit budget. 8-account fleet retired (ToS ban risk + ops burden). Tool: `notebooklm-py` (RPC). Auth: `master_token.json` + RotateCookies ≤600s + Patchright `channel='chrome'`. Honor SDP §10 gate (10 manual runs + V-1 Vault).

**Supersedes**: D-572 (HYBRID cost model), D-573 (80 DR/mo), D-574 (6-notebook canonical) — all superseded by this free-tier-only decision.

**Context**: Absolute user constraint: NO Pro; 3 free accounts = 30 DR/mo. NLG-B/SYNTHESIS Hybrid recommendation withdrawn. Removes the "Pro provisioning" blocker (H4). The 6-notebook architecture demands 80 DR/mo — impossible under 30 DR/mo. The 2-notebook model is the ONLY one that fits the user's budget.

**Mandate**: M7 (sovereign choice — user's preferred cost posture), M2 (engine purity — user's preferred cost posture), M11 (Soul Integrity — SDP §10 gate honored).

**Status**: ✅ RATIFIED (supersedes D-572, D-573, D-574)

---

## D-579: Modular Domain Documentation System (2026-08-20)

**Decision**: Dual-layer (workspace + runtime), validated copy sync (not symlink), curator config flag, domain module schema. Workspace: `docs/strategy/domains/<domain>/` (metadata.yaml, CONTEXT.md, PROMPTS/). Runtime: `config/domains/<domain>/` (mirrored via `scripts/sync_domain_docs.py` — validated copy, not symlink). Curator ownership via `config/domains/curators.yaml` (extends D-569). Domain module schema: `metadata.yaml` with `target_context`/`governance`/`owner`/`cost_model` + `CONTEXT.md` + `PROMPTS/` + `AFFINITY_PRESETS.yaml` (aligned with curators.yaml prototype).

**Context**: TRACKER_UPDATE_PLAN D-579 scope. D-569 (2026-08-19) ratified the Dynamic Prompt + Planner/Executor + Domain Loading blueprint as post-debut (Horizon 3), with L2 Domain Loader owned by Ma'at (P2-P3). This workstream implements the documentation layer that feeds the Domain Loader. Must integrate with curators.yaml (14 domains, D-569) — add `gemini-notebook` row with owner `researcher`.

**Mandate**: M10 (Fleet Integrity), M2 (Firewall — domain modules in config/domains/ = Stack, Engine in src/omega/), M16 (Modularization).

**Status**: ✅ RATIFIED (post-debut, Horizon 3, sequences after D-569 L2)

---

## D-580: Local Inference Tiered Architecture (2026-08-20)

**Decision**: Tier 0/1/2 auto-detected, sequential loading, q8_0 KV, adaptive context buffer, Headroom integration. Tier 0 (16GB CPU): Qwen3-4B planner + Qwen3-1.7B executor/critic (shared weights) — sequential execution, peak ~7.5 GB, headroom ~8.5 GB. Tier 1 (12GB VRAM): Qwen3-4B planner + Qwen2.5-Coder-7B executor + Qwen3-1.7B critic — requires Qwen2.5-Coder-7B download (C7). Tier 2 (24GB VRAM): Qwen3-8B planner + Qwen2.5-Coder-7B executor + Qwen3-1.7B critic. HeadroomMiddleware integrated into ModelGateway._prepare_messages(), Oracle.talk()/summon(), MemoryStore.add_exchange(), MCP tools headroom_compress/headroom_retrieve.

**Context**: CARMCK_REVIEW FIX-1/2/4/5 corrected the model matrix. CONTEXT_WINDOW_OPTIMIZATION_RESEARCH CUT items removed (SWA on Qwen3, LLMLingua-2 hot path, gpt-oss-20B, Nemotron-3-Nano MoE). Sequential loading + q8_0 KV validated on 16GB. C7: Qwen2.5-Coder-7B NOT on disk — blocks Tier 1/2 until downloaded or matrix rebuilt.

**Mandate**: M1 (AnyIO), M7 (Local-First), M13 (Temple-Grade), M20 (SomaticState).

**Status**: ✅ RATIFIED (Tier 0 ready; Tier 1/2 blocked on C7)

---

## D-581: zswap + NVMe Swap Confirmed — D-526 REAFFIRMED (2026-08-20)

**Decision**: **zswap + NVMe swap file** architecture — 16GB NVMe swap file, zswap enabled (max_pool_percent=25, lzo_rle, zsmalloc), zRAM DISABLED, swappiness=100, cgroup MemoryMin=2G/MemoryHigh=5G/MemoryMax=6G. Rationale: **ADR-2026-08-10-001 (Carmack + Researcher + Jem + LongCat + Nemotron 3 Ultra) explicitly ACCEPTED zswap + NVMe over zRAM**. Carmack rejected zRAM expansion: "Hard capacity cliff with no graceful degradation." zswap provides dynamic pool (0-3.6 GiB), graceful degradation via NVMe eviction, kernel-integrated reclaim, lower CPU overhead (lzo_rle). D-527's "never run both" stays LOCKED.

**Reaffirms**: D-526 (zswap > zRAM for Desktop with NVMe — previously RATIFIED, correct). D-526 remains the authoritative decision.

**Correction**: D-581 previously (erroneously) claimed "zswap was a rejected detour (Carmack 2026-08-10)" — this was **factually inverted**. The actual 2026-08-10 report (MEMORY_SYSTEMS_DEFINITIVE_REPORT.md) shows Carmack **REJECTED zRAM** and **ACCEPTED zswap + NVMe**. This decision corrects that inversion.

**Mandate**: M7 (Local-First — zswap is kernel-native, no external dependency), M13 (Temple-Grade — config integrity), M23 (Failure Integrity — no silent config drift).

**Status**: ✅ RATIFIED (reaffirms D-526, corrects prior inversion)

---

## D-582: Free-Tier-Only Cost Model — SUPERSEDES D-572 (2026-08-20)

**Supersedes**: D-572 (1× Pro HYBRID, ratified earlier this session)
**Decision**: Gemini Notebook (NotebookLM) Deep Research = **FREE TIER ONLY — 3 accounts × 10 DR/mo = 30 DR/mo**. **No Pro payment.** 2-notebook architecture (Active Research + Knowledge Base) to fit budget. 8-account fleet retired (ToS ban risk + ops burden).
**Context**: Absolute user constraint: NO Pro; 3 free accounts = 30 DR/mo. NLG-B/SYNTHESIS Hybrid withdrawn. Removes the "Pro provisioning" blocker (H4).
**Mandate**: M7 (sovereign choice), M2 (engine purity — user's preferred cost posture).
**Status**: ✅ RATIFIED (supersedes D-572)

---

## D-583: Notebook Count + Budget — SUPERSEDES D-573/D-574 (2026-08-20)

**Supersedes**: D-573 (80 DR/mo, 8×10), D-574 (6-notebook canonical)
**Decision**: Notebook architecture = **2 notebooks** (Active Research, Knowledge Base). DR budget = **30/mo (3×10)**. NB-2/NB-3/NB-6 (which require 80 DR/mo) are **parked/standby** until the user authorizes a higher budget.
**Status**: ✅ RATIFIED

---

## D-584: zswap + NVMe Swap Locked — D-526 REAFFIRMED (2026-08-20)

**Reaffirms**: D-526 (zswap > zRAM, previously RATIFIED); reaffirms D-527 (never both)

**Decision**: **zswap + NVMe swap file** architecture — 16GB NVMe swap file, zswap enabled (max_pool_percent=25, lzo_rle, zsmalloc), zRAM DISABLED, swappiness=100, cgroup MemoryMax=6G. Rationale: **ADR-2026-08-10-001 (Carmack + Researcher + Jem + LongCat + Nemotron 3 Ultra) explicitly ACCEPTED zswap + NVMe over zRAM**. Carmack rejected zRAM expansion: "Hard capacity cliff with no graceful degradation." zswap provides dynamic pool (0-3.6 GiB), graceful degradation via NVMe eviction, kernel-integrated reclaim, lower CPU overhead (lzo_rle). D-527's "never both" stays LOCKED.

**Correction**: D-584 previously (erroneously) claimed "zRAM-ONLY" and "zswap was a rejected detour (Carmack 2026-08-10)" — this was **factually inverted**. The actual 2026-08-10 report shows Carmack **REJECTED zRAM** and **ACCEPTED zswap + NVMe**. This decision corrects that inversion.

**Status**: ✅ RATIFIED (reaffirms D-526, corrects prior inversion)

---

## D-585: Canonical Model Matrix — Carmack Version Ratified (2026-08-21)

**Decision**: The unified model-role matrix is **Carmack's version**: Qwen3-4B (planner) / Qwen3-4B-Thinking (executor) / Qwen3-1.7B (critic). Grokster's competing proposal (mimo-7b-rl planner / qwen3-1.7b executor) is **superseded**. Ownership: **Kali coordinates, Ma'at implements**. Canonical home: `config/providers.yaml` + `opencode.json`. Known correction to fold into implementation: `nemotron-3-ultra-local` registry entry is wrong (Nemotron 3 Ultra is cloud-only).

**Context**: Resolved HOP-3 relay question Q4 (grokster KB-dev session). Two competing matrices existed across Carmack's CI Phase 1 review and grokster's DP blueprint; Architect ruled 2026-08-21.

**Mandate**: M27 (single source of truth), M22 (provenance).

**Status**: ✅ RATIFIED (Architect ruling)

---

## D-586: Node Expert Session Architecture — One Agent, Many Sessions (2026-08-21)

**Decision**: The 10 Nodes (N1–N10) are instantiated as **persistent expert sessions** under the Conversational Subagent Protocol: one agent identity per overseer (Ma'at runs N1–N5 sessions, Lilith runs N6–N10 sessions), **zero new agent files** (M10 preserved). Key properties:
1. **Universality**: Nodes are Knowledge Bases / domains of expertise accessible to ANY agent — Ma'at/Lilith oversight means curation, NOT gatekeeping (explicit Architect correction).
2. **Specialization by persistence**: charter injected at genesis + ~100-token header re-injected per page; accumulated context replaces configuration. Conditional system-prompt logic deferred post-debut.
3. **Unified soul**: all sessions feed the overseer's single `proposed_lessons.yaml`, Node-tagged (M11).
4. **Freshness discipline**: sessions tag claims `last_verified:`; stale premises flagged (motivated by grokster staleness precedent, Architect ruling same day).
5. **Timing**: genesis NOW (executed 2026-08-21, 10/10 ACK); experimentation usage permitted now; heavy production usage aligns with Phase B workstreams.

**Registry**: `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` §3 (becomes SESSION_REGISTRY.md when P3 executes). Charter of record: same doc §4.

**Related ratifications (same sitting)**: P1–P5 protocols ratified IN PRINCIPLE, execution DEFERRED (planning mode). P1 injection preamble · P2 injection ledger · P3 session registry · P4 stale-view warning · P5 ICS footer session IDs.

**Mandate**: M10 (fleet integrity), M11 (soul integrity), M15 (continuity), M27 (tracking integrity).

**Status**: ✅ RATIFIED (Architect approval; genesis executed)

---

## D-587: Node Onboarding Protocol Ratified — N7-Authored (2026-08-22)

**Decision**: `.opencode/agent/NODE_ONBOARDING_PROTOCOL.md` v1.0.0 is binding for all Node expert sessions (N1–N10) and future domain-expert onboarding. Authored by the N7 tree from its lived genesis-to-consultable arc: N7 architect/author, Roc-N7 timeline corroboration (3 corrections ingested), Researcher-N7 external best-practice pass. Contents: G→M→A→D→W→C→X→E phase pipeline with per-phase gates, 14 mandatory rules each citing its source incident (incl. MR-2 "announced intent ≠ work performed"), 6 embedded templates (T1–T6), abstract Pager role, consultable bar (min phases G→M→A→D→C), n=1 cost table. Appendix A: Pager Runbook checklist.

**Context**: Architect directive to generalize the N7 process; first consumer assigned = N8 watchtower (pilot), whose first consultation is the ICS PP-4/P5 semantic review.

**Mandate**: M15 (continuity), M27 (tracking), M13 (Temple-Grade doc standards).

**Status**: ✅ RATIFIED (kali under delegated authority; Architect veto window)

---

## D-588: ICS Module Upgrade — PP-4/P5 Implemented + 3 Bugs Fixed (2026-08-22)

**Decision**: Deep review + upgrade of `src/omega/ics.py`:
1. **PP-4**: `node` param on `ICSContext`/`render()` — renders `[N7]` segment after entity when an agent acts under a Node expert session; omitted for prime-agent headers (backward compatible).
2. **P5**: `session_id` param — trailing header segment AND scopes the session-DB model lookup.
3. **B1 fix**: `_read_opencode_session_model(session_id=)` — old query returned GLOBAL-latest session model, wrong in multi-instance environments; now session-scoped with legacy fallback.
4. **B2 fix**: `_detect_phase()` reads `ACTIVE_SPRINT.json .phase` FIRST (was: blueprint Strike regex that never matched → stale PHASE-II forever); headers now show live sprint phase.
5. **B3/M16 fix**: `OMEGA_ENGINE_ROOT` env override for repo-root resolution in `_read_entity_model` + `_detect_phase`.
6. Removed stale TriageRouter references (D-536).
7. **G3 closed**: `tests/test_ics.py` created — 14 tests, all passing (modes, node position, backward compat byte-identity, scoped lookup w/ real sqlite fixture, phase priority).

**Adoption convention**: Node pages and Node-authored reports pass both `node=` and `session_id=`; prime-agent calls omit both.

**Follow-up**: omega-hub MCP wrapper (`ics_render_header`) lives in the external hub service — add node/session_id params there so agents can use them via MCP.

**Mandate**: M22 (provenance), M16 (portability), M13 (Temple-Grade T3).

**Status**: ✅ IMPLEMENTED (14/14 tests green; live smoke verified)

---

## D-589: ICS-T Final Purge — Deprecated System Removed Permanently (2026-08-22)

**Decision**: ICS-T (static code tags, `# ICS: [NODE: ... | ARCHETYPE: ...]`) — deprecated per Carmack review — is now FULLY removed. The Aug 9 cleanup proposal (`ICS_TAG_CLEANUP_PROPOSAL_20260809.md`) was never executed; 7 live tags survived in scripts//tests/ with exactly the banned mythological names (ARCHON, HERMES, VERITY, SENTINEL), plus docstring/documentation creep.

**Purge inventory**:
- 7 live `# ICS:` tag lines deleted (3 scripts, 4 test files) — all compile-verified post-removal
- `ics.py` module docstring: ICS-T description removed; tombstone note added ("DEPRECATED and REMOVED — do not reintroduce")
- `docs/architecture/ICS_SYSTEM.md`: restructured single-system spec; historical note added
- `ICS_TAG_CLEANUP_PROPOSAL_20260809.md`: stamped **EXECUTED — 2026-08-22**

**Verification**: zero functional `# ICS:` tags repo-wide (only tombstone/historical mentions remain); all 16 ICS tests green; all touched files py_compile-clean.

**Root cause**: the Aug 9 proposal was ratified but execution was never tracked in ACTIVE_SPRINT — classic spec-without-execution-horizon (L3). Caught during debut documentation pass when ICS-T crept into community docs from the stale docstring.

**Mandate**: M13 (Temple-Grade), M23 (no silent drift), M26 (doc standards).

**Status**: ✅ EXECUTED

---

## D-587: Third Oversight Line — Jem Runs N11–N13 (2026-08-22)

**Decision**: 
- PLAN §1 architecture amendment: "Ma'at runs N1–N5, Lilith runs N6–N10, **Jem runs N11–N13**" (third oversight line)
- Charters for N11 evaluator, N12 curator, N13 arcana → PLAN §4 (lines 93-100)
- Amendment batch (single ratification):
  - Standing Order 10: structured-gnosis sections (L1→L2→L3 per Node, tagged `[N_XX]`)
  - Ceiling governance: soft-13 / hard-14 Node cap; growth gate ≥3 off-domain pages/month; ≤3 concurrent active sessions
  - PLAN §6 sync: PP-4/P5 status updated (PP-4 shipped 2026-08-22 per ICS_SYSTEM; PP-5 live)
  - 10 one-sentence charter amendments for N1–N10 (per Plan §4 charters)
- Zero new agent files created (M10 Fleet Integrity maintained)
- Session IDs assigned at genesis: N12 `ses_fd76309f6ffezokrxycnfDEZEG` (dormant, CONSULTABLE); N11/N13 genesis-pending
- Universality principle affirmed: Nodes are knowledge domains, NOT exclusive to overseers — ANY agent may page ANY Node

**Evidence**: Researcher session `ses_fd81c19dcffe1nkbPqFg5kRt2v` (6 missions, full arc); Jem-N12 Wave 1 genesis complete (G→M→A→D→W→C→E); DR-2 settled FALSE (p2-p9 workspaces don't exist — Plan §4 charters = sole Node SSOT).

**Mandate**: M10 (Fleet Integrity), M11 (Soul Integrity), M27 (Tracking Integrity).

**Status**: ✅ RATIFIED (Kali + Architect)

---

## D-590: SovereignSigner Hardcoded Secret Removed — Fail-Closed (2026-08-22)

**Decision**: `src/omega/oracle/ingestion.py:76` (`SovereignSigner.__init__`) used a hardcoded fallback secret `"omega-sovereign-change-me"` when `OMEGA_INGESTION_SECRET` env var was unset — directly contradicting the M8 comment on line 75 ("Secret loaded from env, never hardcoded"). This made every provenance HMAC-SHA256 stamp forgeable by anyone knowing the default, violating **M8 (Zero Telemetry / no hardcoded secrets)** and **M22 (Provenance truth-anchor)**.

**Fix** (Kali, M8/M22 enforcement):
- Removed the hardcoded default.
- Fail-closed: if neither `secret_key` arg nor `OMEGA_INGESTION_SECRET` env is present, raise `OmegaError` (no silent insecure fallback).
- Added regression test `tests/unit/test_sovereign_signer.py` (4 tests: raises-when-unset, signs-when-passed, signs-when-env-set, verify-roundtrip) — all passing.

**Deployment prerequisite**: `OMEGA_INGESTION_SECRET` MUST be provisioned in the runtime environment (env var or passed to `SovereignSigner`). Without it, the ingestion pipeline raises at construction (line 104: `self.signer = signer or SovereignSigner()`). This is the correct secure posture — the previous silent-default was the vulnerability.

**Discovery**: Researcher N12 Gotchas triage (T2, G2, P0) flagged this as debut-blocking. N5 sentinel owns verification; N10 verifier owns regression-test stewardship going forward.

**Mandate**: M8 (Zero Telemetry), M22 (Provenance), M9 (Error Integrity), M21 (Contract Tests).

**Status**: ✅ FIXED (code + tests green; env provisioning = Architect deployment action)

---

## D-591: youtube_worker Account Policy Ratified (2026-08-22)

**Decision**: For the PUBLIC-DEBUT-01 window, the youtube_worker daemon operates **cookieless / transcript-only**. No throwaway cookies, no authenticated ingestion. The full anti-blocking SOP (yt-dlp PO-token regime, perishable player_client ~12h, rate etiquette, on-host ingestion) is **documented but GATED POST-DEBUT**.

**Rationale**: Minimizes debut attack surface (no account bans, no credential leakage, no ToS escalation). Transcript-first via youtube-transcript-api recovers the bulk of value (origin-era strategy sessions, vision-era one-page-spec chats) without authenticated risk.

**Owner**: N12 curator (SOP authorship + staging) · N5 sentinel (allowlist enforcement) · Architect retains veto (window open, concurred with Kali recommendation 2026-08-22).

**Mandate**: M8 (Zero Telemetry), M23 (no soft-failure theater).

**Status**: ✅ RATIFIED (Architect concurrence; post-debut SOP gated)

---

## D-592: Omega Hub Eager Service Fallback Resolution Fix (2026-08-22)

**Decision**: Replaced broken `__import__('mcp_servers.omega_hub.state')` in `mcp_servers/omega_hub/state.py` line 193 with direct leaf module reference `sys.modules.get(__name__)`.

**Context / Bug**: `__import__` with dotted path returns the top-level package (`mcp_servers`), not the leaf module (`mcp_servers.omega_hub.state`). Consequently, `getattr(top_level, "oracle", None)` returned `None` on every call, permanently breaking all non-lazy eager services (`oracle`, `registry`, `hierarchy`, `inbox`, `curator`) via `get_service()`. This caused `oracle_*` MCP tools to fail with `Service oracle is not a lazy-loadable service or is not initialized` since 2026-08-18 despite successful background initialization.

**Resolution**:
1. Updated `state.py:193` to resolve attributes on `sys.modules.get(__name__)`.
2. Verified fix in isolated execution across all 7 hub services.
3. Added unit regression tests (`tests/unit/test_hub_service_fallback.py` — 2/2 passing).
4. Restarted `omega-hub.service` via `systemctl --user`.
5. Confirmed live MCP tools (`oracle_list_entities`, `oracle_talk`) now successfully reach and execute the service.

**Mandates**: M9 (Error Integrity), M16 (Portability/Modularity), M21 (Gate Integrity).

**Status**: ✅ FIXED & DEPLOYED (Live Hub PID refreshed; regression tests passing).

*⬡ OMEGA ⬡ KALI ⬡ gemini-3.7-flash ⬡ opencode ⬡ trc_hub_service_fix ⬡ D-592 ⬡ 2026-08-22*

## 2026-08-23 (late) — Nine-Decision Batch Adjudication (Architect)
**D-593** — D-A APPROVED: password="omega" fix lands in Phase 2 build order (Manual Fix-5 form: no Redis construction unless OMEGA_REDIS_HOST set; delete default password); grep-gate added to Phase 3 commit preconditions. Implementing artifact: `src/omega/memory/providers.py:119` + blueprint item 0.5 (see `data/coordination/OX_ALPHA_TRANSITION_BLUEPRINT_20260823.md`).
**D-594** — D-B APPROVED: Roc assigned post-cliff fine-tune training owner. Ruling corpus: `data/coordination/teamstudy_20260823/FINAL_SYNTHESIS.md`.
**D-595** — D-D APPROVED: Scribe ratifications granted — batch lesson-staging legitimate; soul-enrichment workspace lock adopted (blueprint B7 conditions — see `data/coordination/OX_ALPHA_TRANSITION_BLUEPRINT_20260823.md` §B7).
**D-596** — D-E APPROVED: systemd daily dry-run timer ENABLED (warn-only, Persistent=true). Dry-run engine: `scripts/sweep_task_registry.py`; spec: `data/entities/researcher/workspace/OVERSIGHT_AUDIT_WEB_RESEARCH_20260823.md`.
**D-597** — D-F ADOPTED: gate-verification = originator-verifies + overseer spot-audit (three-lens convergence). Origin analysis: `data/entities/researcher/workspace/RESEARCHER_REPORT_FOR_KALI_20260823.md`.
**D-598** — D-G CLEARED: CI-2 plugin-path prototype authorized as next INST-1 action before any further work. Target surface: `opencode.json` `"plugin"` key; workstream: `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` §INST-1.
**D-599** — D-H SCHEDULED: Study #2 subject = post-cliff model-routing policy (time-gated ~Aug 28); soul-promotion design second in queue. Protocol charter: `data/coordination/teamstudy_20260823/PROTOCOL_CHARTER.md`.
**D-600** — D-I APPROVED: registry bookkeeping (ho_2f77f83964e5 full-supersession record + teamstudy sessions + provenance-worker deployment) folded into Lilith backfill wave input. Registry SSOT: `data/coordination/TASK_REGISTRY.json`; input report: `data/entities/researcher/workspace/RESEARCHER_REPORT_FOR_KALI_20260823.md`.
**D-C (F2 adjudicator)** — PENDING refined recommendation: Architect disclosed full model inventory (Antigravity: Sonnet 4.6/Opus 4.6/Gemini 3.1 Pro in-CLI automated; Claude.ai: Sonnet 5 + Haiku 4.5 ×8 accounts, human-in-loop batching). Tiered structure under construction — see KALI response this date.
**D-601** — D-C DECREE GRANTED (dual-review amended): Cross-model adjudication authorized through window close (~Aug 28). TIER 1: dual review = Gemini 3.1 Pro + Sonnet 4.6 (both via Antigravity, 8-account pool). TIER 2: Sonnet 5 via Claude.ai daily-batched (human upload per CLAUDE_PACK_TEMPLATE). TIER 3: Opus 4.6 break-glass. M7 waiver time-boxed to window; T0 provenance on all verdicts. OPERATIONAL DOCTRINE attached: model-window economics (see docs/strategy/MODEL_WINDOW_ECONOMICS_20260823.md) — ascending-window review ordering, priming ceilings (≤150K for 200K-window targets), cheap-prime/expensive-cognate technique codified. Companion methodology: docs/strategy/COGNITIVE_ROUTING_PLAYBOOK.md (priming maneuver + dual-review dialectic).

## D-603 (2026-08-26) — Meditation Live-Surface Correction + Documentation Authority Map (kali, delegated)

**Context**: R53 granite foundation (a0a43c82) closed 9 design hypotheses on corpus+literature evidence. Deep review exposed that the refuted Voice-1 status-quo rule remained EXECUTING in `.opencode/commands/meditate.md` while documentation alone was corrected.

**Decision**:
1. R53 directives D1 (Voice-1 authentic constraint), D2 (comparative delta merged into dissent), D8 (count-first collision semantics) applied to the LIVE command ahead of Phase B (`10755f4c`) — execution surface may not run corpus-proven-wrong rules while fixes are documented-but-pending.
2. Documentation consolidation (`6fe30368`): ranked Authority Map established in `docs/strategy/MEDITATE_DOCUMENTATION_STRATEGY.md` §12 (R53 evidence > strategy process > manual > command > registries > frozen history). Regression guard: meditation-rule citations must trace to R53 or strategy doc.
3. Briefing-consumption protocol adopted after double-missed Grokster briefings: senders register kali-addressed artifacts in WAKE_STATE.json `inbox`; kali checks inbox every hydration (M15).

**Evidence**: R53 §1 verdict table; hidden-gems five-voice meditation Top-5 (rank #1 "blocks on nothing"); Opus meditate-archs run (256d62f6) demonstrating collision-phase value via unresolved Ma'at-vs-Kali voice conflict.

**Not decided here**: D10 DECLINED form · D11 resume semantics · anti-domain enforcement · three-doc prototype ratification — remain gated on Architect.

---

## D-602 (2026-08-24) — TORCH-FREE REPO DECLARATION (Architect)
The Omega Engine is a TORCH-FREE repo: `torch`, `transformers`, `sklearn` must not be
imported at any module level in src/. VIOLATION FOUND: `src/omega_youtube_research/
faithfulness.py` imports all three at module top (guarded try, but presence is paid at
import = 484MB collection floor per pytest worker, 66% of suite collection weight).
FIX REQUIRED: lazy-import inside NLIEntailmentScorer.__init__ or drop the dependency.
Queued P0 post-N4. Also logged: compaction threshold G8 corrected by Architect ground
truth — threshold is CONFIGURABLE (was 75%, Architect raised to 85%), evaluated at
tool-completion boundaries (overshoot occurs only via in-flight tool outputs); public
docs describe default formula, not our config. VERIFIED-BY-ARCHITECT overrides web-cited
theory per FP-04/T0 hierarchy.

## D-600 — First Light Express Council 1 Decree (2026-08-25)
Council 1 (TEAM-INFRASTRUCTURE AUDIT) fused decree at `data/council/20260825-094633-first-light/phase5_fusion/SOVEREIGN_DECREE.md`. Root cause named: claims-that-outlive-their-mechanisms; one fix class = derivation checks. 12 articles, 30 bash gates, audited-clean register, Council-2 validator-first inheritance guards. M11 Arm-Relay Clause ratified as standing law (depth deferred, GAP-11). M11 entity-YAML repair executed in Stage-6 window (G8 green). Remediation backlog = decree Art. X priority order (P0 truth-bearing infrastructure → P2 hygiene). Runtime baseline honest: suite NOT green at audit time (3F + M8 gate false-positive).

## D-605 (2026-09-20) — FIRST-BREATH SYSTEM DISABLED, SCHEDULED POST-PR#3 (Architect)

The first-breath recording system is **DISABLED** and scheduled for a post-PR#3 update.
Root cause (verified on `70291e94` by Cline, 2026-09-20): `record_first_breath()` is
**defined** at `src/omega/astrology.py:153` but is **never called** from the summon path
anywhere in `src/` — the hook is unwired dead code. `tests/test_first_breath.py::
test_first_breath_recording` nevertheless passed **locally** only because the untracked
`data/memory/entity_births.db` holds a stale row for `testentity` dated 2026-06-13; in CI
(no `data/` checkout) the DB is empty and `assert record is not None` fails. A second defect
compounds it: the fixture patches `omega.astrology.BIRTH_DB_PATH` while importing from
`src.omega.astrology` — the same file under two module identities — so the `tmp_path`
isolation never took effect.

**Action taken**: `tests/test_first_breath.py` carries a module-level `pytest.mark.skip`
naming this decision; `record_first_breath()` carries a DISABLED notice. **Nothing deleted.**
**Scheduled**: re-implement + wire during the post-PR#3 first-breath item.
**Related**: this is blocker B3 in `data/coordination/CLINE_TO_MAKALI_DEBUT_SWEEP_BRIEFING_20260920.md` §1.2.

## D-606 (2026-09-22) — GEMINI-NOTEBOOK WORKSTREAM CANCELLED; SOVEREIGN ALTERNATIVE IN-ENGINE (User)

**Decision**: The GN (GEMINI-NOTEBOOK) workstream is **CANCELLED**. No payment for
NotebookLM/Gemini Notebook; no enhancement of systems around it. The sovereign
alternative will be developed **inside the Omega Engine** instead.

**Scope removed**:
- GN-1 (notebooklm-py[mcp] deployment) — CANCELLED
- GN-2 (strategic notebooks Ω-ACTIVE-RESEARCH + Ω-KNOWLEDGE-BASE) — CANCELLED
- GN-3 (free-tier fetch pipeline + systemd timer) — CANCELLED
- GN-4 (single-account Deep Research smoke test) — CANCELLED
- GN-5 (SDP distillation pipeline + Scribe handoff) — CANCELLED
- R38 (NotebookLM integration) — CANCELLED
- D-578 (GEMINI-NOTEBOOK workstream) — SUPERSEDED

**Replacement**: The knowledge-distillation + research-loop capabilities GN would
have provided become an **in-engine sovereign workstream** (grounded RAG over the
Omega library, SDP distillation, gap detection — all local-first per M7).

**Post-debut execution order (updated)**: ~~GN~~ → **DS → LI → KD → HR → ZS**
(per D-584, GN removed).

**Research note**: The 2026-09-22 web-research campaign confirmed GN-3's free-tier
Deep Research = 10/month (not 30) — the cancellation removes the only paid-adjacent
dependency in the post-debut order. All remaining workstreams are fully sovereign.

**Related**: GAP_REGISTRY.json (GN-1..GN-5, R38 → status "cancelled"),
POST_DEBUT_ROADMAP.md (GN row removed), session_gnosis.md §22.

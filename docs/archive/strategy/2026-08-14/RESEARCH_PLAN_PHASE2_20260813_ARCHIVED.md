# 🔱 Research Plan Document — Phase 2: Foundation & Infrastructure

> **⚠️ ARCHIVED 2026-08-14 — CONFLICTING PLAN.** This plan was **untracked** (never in git)
> and **redefined gaps R13–R38 with different topics** than the authoritative
> `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` (v3.2.0). @researcher executed research
> against THIS plan on 2026-08-13. To resolve the numbering collision, the resulting reports were
> **renumbered R13–R38 → R39–R56** (see `RESEARCH_PLAN_PHASE1_4_20260813.md` v3.2.0
> §RESOLVED PHASE2 DELIVERABLES). This document is retained for historical context only and is
> **superseded** by the v3.2.0 plan. It also references a non-existent `CROSS_REFERENCE_INDEX.md`.
> Note: R56 (lazy loading) report was LOST during reconciliation — reconstructed stub only.

## 📋 Document Information

| Field | Value |
|-------|-------|
| **AP Token** | `AP-RESEARCH-PLAN-PHASE2-20260813-v1.0.0` |
| **Sprint** | SDP-EXECUTION-02 |
| **Version** | v1.0.0 |
| **Date** | 2026-08-13 |
| **Researcher** | Sovereign Researcher (Jem Analyst L2) |
| **Dependent Task Owners** | @jem, @maat, @lilith, @roc_racoon |
| **Hivemind Channel** | opencode |
| **Prior Research Completed** | Phase 1: 11 gaps resolved (R1-R12, R14, R21-R22 partial) |

---

## 📚 Primary Source of Truth

**Read FIRST:** `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` (v3.1.0)

This Phase 2 plan covers gaps R13-R38 (27 remaining gaps after Phase 1 completion).

**Cross-Reference Index:** `data/coordination/CROSS_REFERENCE_INDEX.md` (92 existing research docs — DO NOT DUPLICATE)

**Sovereign Mandates (NON-NEGOTIABLE):**
- **M1 AnyIO**: No `asyncio`. Wrap blocking I/O in `anyio.to_thread.run_sync`
- **M7 Local-First**: Local inference PRIMARY, cloud FALLBACK. Always.
- **M8 Zero Telemetry**: No analytics, no phone-home, no metrics sent external
- **M13 Temple-Grade**: Run `make temple-grade` after non-trivial changes
- **M23 Failure Integrity**: Mandatory tool broken → `[TOOL-CHAIN-COLLAPSE]`. NO soft-failures
- **M24 Venv Sovereignty**: Use `.venv`, never `--break-system-packages`

**Temporal Mandate**: It is **2026**. All search queries MUST include "2026" or "latest". Do NOT search for "2024" or "2025".

---

## 🎯 Sprint Mission

**Execute Phase R2 (Week 2-3) research**: R13-R38 (27 gaps)

**Priority Order**:
1. **Critical (Foundation)**: R30, R31, R33, R34, R35 (5 gaps)
2. **High (Infrastructure)**: R13, R14, R15, R16, R17, R18, R19 (7 gaps)
3. **Medium (Vision/Philosophy)**: R23, R24, R25, R26, R37, R38 (6 gaps)
4. **Already Addressed**: R1-R12, R14, R21-R22 (partial) — 11 gaps

**Output**: `data/entities/researcher/workspace/research_reports/PHASE2_RESEARCH_20260813.md`

**Hivemind Requirement**: Before starting: `omega-hub_hivemind_get_awareness()` — check who's working. During: `omega-hub_hivemind_heartbeat(channel="opencode", entity="researcher")` every 5-10 min. After each gap: `omega-hub_hivemind_post_context(...)` with intent=decision|observation.

---

## 📋 GAP CATALOG — Phase 2 (R13-R38)

### 🔴 CRITICAL — Foundation (5 gaps, ~10h)

| Gap | Blocks | Description | Effort |
|-----|--------|-------------|--------|
| **R30** | UO-6.1 | 5-way circuit breaker spike: pyresilience vs tenacity vs stamina vs pybreaker vs interlock-cb. Live benchmarks required. | 3h |
| **R31** | Vision | Dimension / Free-Will / Phase Γ Hub Split — map to Cognitive Sovereign evolution from functional runtime. | 2h |
| **R33** | Spec Integrity | Living Research OS Body — D-371/D-372 amendments; body SUPERSEDED by banner + Ark §3.2. Formal decision: implement/archive/replace. | 2h |
| **R34** | SSOT | CANONICAL_ROADMAP vs STRATEGY_CORPUS_MAP conflict — verify no competing roadmaps fragment dev direction. | 1h |
| **R35** | Identity | Identity Fluidity E-0…E-5 paths — map grokster workspace paths to actual Omega entity directives/core principles/soul.yaml fields. | 2h |

### 🟠 HIGH — Infrastructure (7 gaps, ~12h)

| Gap | Blocks | Description | Effort |
|-----|--------|-------------|--------|
| **R13** | Fleet | Agent Fleet Health Dashboard — real-time soul health metrics across all entities (soul health scores, directive compliance, l3 adoption rates). Violates M5 if lost. | 3h |
| **R14** | Coordination | Subagent Pair-Execution Chains — walk ancestor/descendant trees; trace pair-execution chains (executor-opus + executor-gpt); identify orchestrators. | 2h |
| **R15** | Fleet | Cross-Agent A2A Protocol — Abstract-to-Agent protocol for discovery, delegation, handoff. Current system has no standardized A2A beyond Hivemind broadcasts. | 3h |
| **R16** | Memory | MemoryStore → Oracle.py Wiring Verification — confirm MemoryStore add_exchange() calls at lines 153, 318, 387 are complete; add missing exchange points; test cross-pollination. | 2h |
| **R17** | Handoff | Handoff Protocol v2 — full A2A handoff protocol with contract layer, acceptance, completion, archive actions, TTL-based expiration. Current is basic; v2 adds audit trails, priority, TTL. | 3h |
| **R18** | Provider | Provider Chain Hardening — formalize local-first strategy (native-gguf→lmster→Ollama→Google→OpenRouter→OCZ); add breaker unification (R6′); implement fallback chain per provider. | 2h |
| **R19** | Sustainability | Tokenomics & Cost Modeling — cost model per provider per model per workload; sovereignty ratio tracking; billing ledger that works. M18 mandate: every token must serve a purpose. | 3h |

### 🟡 MEDIUM — Vision & Philosophy (6 gaps, ~8h)

| Gap | Blocks | Description | Effort |
|-----|--------|-------------|--------|
| **R23** | Security | Lorraine Code / Cline-M3 Firewall Audit — D-208 heritage vetting. Audit firewall rules; ensure [id-soft:] tags properly vetted; no over-attribution. M14 compliance. | 2h |
| **R24** | Deployment | OEM-003: Container Hardening — AppArmor profile hardening; capability bounding; seccomp profiles for Omega containers. Current: containers unconfined (V-10 gap). | 2h |
| **R25** | Security | OEM-004: IA2 Signature Freshness / Envelope — freshness check mechanism; signature validation; replay attack prevention. M22 (Response Provenance) compliance. | 2h |
| **R26** | Integration | Grok CLI 8-Account Fabric Pool — D-360′: vault → smoke → pool (not 4h fantasy). Single ACP smoke test first, then pool. Vault MVP (V-1) must exist first. | 2h |
| **R37** | Force Multipliers | YouTube Research Sessions Deep Dive — 24 proposals → top 5 force multipliers (Ornith-9B, Vulkan, Instruction Router, Hardening, llama-optimus). 5,000+ lines across 6 docs. Phase 0 strategy: research complete, awaiting implementation go/no-go. | 3h |
| **R38** | Reliability | OpenCode v1.17+ Lazy Loading Edge Cases — v1.17.0 plugins from config array silently not loaded. Edge case documentation: when does lazy loading fail? How to recover? | 2h |

---

## 📊 Phase Distribution

| Phase | Gaps | Count | Cumulative Hours |
|-------|------|-------|------------------|
| Phase 1 (Week 1) | R1-R12, R14, R21-R22 | 15 | 14h |
| Phase 2 (Week 2-3) | R13-R38 | 27 | 30h |
| **Total R1-R38** | **38** | **38** | **44h** |

---

## 🛤️ Recommended Research Order

### **Week 2 — Critical Foundation (Days 1-5)**

**Day 1: R30 + R31** — Circuit breaker benchmark + Cognitive Sovereign dimension mapping
- These are the foundational infrastructure decisions that enable everything else
- R30: Benchmark 5 breaker libraries under load; document failure detection latency, false positive rates, recovery time, resource overhead
- R31: Map dimension/free-will/phase Γ to the 3-tier memory (Hot/Warm/Cold) + entity soul structure; how free-will markers interact with memory states

**Day 2: R33 + R34** — Living Research OS body + Roadmap SSOT
- R33: Formal decision on the SUPERSEDED Living Research OS body — implement/archive/replace. Read D-371, D-372, D-371′, D-372′.
- R34: Verify no competing roadmaps exist that could fragment dev direction. Check STRATEGY_CORPUS_MAP.md, SOVEREIGN_ARK_BLUEPRINT.md, CANONICAL_ROADMAP_20260721.md.

**Day 3: R35** — Identity Fluidity mapping
- Map E-0…E-5 paths from grokster workspace to Omega entity system: directives, core_principles, soul.yaml fields
- Read grokster workspace identity files, match to entity structure

**Day 4: R35 (continued) + R34 verification** — Complete identity mapping + roadmap SSOT check

**Day 5: R34 verification + R35 cleanup** — Final SSOT verification + identity mapping cleanup

### **Week 3 — Infrastructure (Days 6-10)**

**Day 6: R13 + R14** — Fleet health dashboard + subagent pair-execution chains
- R13: Soul health metrics dashboard design; integrate SoulHealthScorer across fleet; post to Hivemind
- R14: Walk ancestor/descendant trees; trace pair-execution chains; identify orchestrators. Build `/doctor`-style tool

**Day 7: R15 + R16** — A2A protocol + MemoryStore wiring
- R15: Design Abstract-to-Agent protocol; discovery, delegation, handoff. Document current Hivemind broadcast limitations.
- R16: Verify MemoryStore → Oracle.py wiring at lines 153, 318, 387; add missing exchange points; test cross-pollination with soul.yaml lessons

**Day 8: R15 (continued) + R16 cleanup** — Complete A2A protocol design + memory wiring verification

**Day 9: R17 + R16 cleanup** — Handoff protocol v2 design; finalize memory wiring

**Day 10: R17 cleanup + R18** — Handoff protocol finalization + provider chain formalization

### **Week 3 — continued (Days 11-15)**

**Day 11: R18 + R19** — Provider chain + tokenomics
- R18: Formalize local-first strategy; breaker unification; fallback chain per provider. Read P0-P2 research on provider patterns.
- R19: Cost model per provider per model per workload; sovereignty ratio tracking; billing ledger. Reference M18 token efficiency mandate.

**Day 12: R18 (continued) + R19** — Provider chain finalization + cost model draft

**Day 13: R19 + R20** — Cost model + Qdrant hardening
- R19: Complete cost model; sovereignty ratio tracking template
- R20: Qdrant hardening: scalar quantization configs; payload index strategies; shard routing for >100K vectors. Reference headroom-ai 2025 semantic compression.

**Day 14: R20 + R23** — Qdrant hardening + Lorraine code audit
- R20: Qdrant config complete; shard routing tested
- R23: Lorraine code / Cline-M3 firewall audit. D-208 heritage vetting. Ensure [id-soft:] tags properly vetted; no over-attribution.

**Day 15: R23 + R24** — Firewall audit + container hardening
- R23: Firewall audit complete; heritage tags verified
- R24: Container hardening: AppArmor profiles; capability bounding; seccomp profiles. Reference V-10 gap (containers unconfined).

### **Week 4 — Vision & Polish (Days 16-20)**

**Day 16: R24 + R25** — Container hardening + IA2 signatures
- R24: AppArmor profiles seccomp profiles complete; containers now confined
- R25: IA2 signature freshness / envelope mechanism. Freshness check; signature validation; replay attack prevention. M22 compliance.

**Day 17: R25 + R26** — IA2 + Grok CLI pool
- R25: IA2 envelope mechanism complete; freshness check implemented
- R26: Grok CLI 8-account fabric pool. D-360′: vault → smoke → pool. Single ACP smoke test first, then pool. Vault MVP (V-1) must exist first.

**Day 18: R26 + R37** — Grok pool + YouTube research deep dive
- R26: Grok CLI pool smoke test complete; vault MVP (V-1) verified
- R37: YouTube research sessions deep dive. 24 proposals → top 5 force multipliers (Ornith-9B, Vulkan, Instruction Router, Hardening, llama-optimus). Read CARMACK_DEFINITIVE_STRATEGY_20260730.md. 5,000+ lines across 6 docs. Implementation go/no-go decision.

**Day 19: R37 + R38** — Force multipliers + lazy loading edge cases
- R37: Top-5 force multipliers implementation plan; Ornith-9B, Vulkan, Instruction Router, Hardening, llama-optimus
- R38: OpenCode v1.17+ lazy loading edge cases. When does lazy loading fail? How to recover? Edge case documentation.

**Day 20: R38 cleanup + Phase 2 closeout** — Lazy loading edge cases documented + Phase 2 research package consolidation

---

## 📝 Workflow Per Gap

### For GREENFIELD Gaps (no existing research):
1. Check Cross-Reference Index — confirm no existing research doc
2. Conduct new research with `websearch`/`webfetch` (include "2026" in all queries)
3. Write findings to `data/entities/researcher/workspace/research_reports/PHASE2_RESEARCH_20260813.md`
4. Post resolution to Hivemind (`intent: decision|observation`)
5. Update `TASK_REGISTRY.json` with completion status

### For PARTIALLY RESOLVED Gaps (verify+extend only):
1. Read existing research doc
2. Verify numbers are current (August 2026)
3. Extend only: add missing specifics (e.g., pool_tracker.py wiring, implementation specifics)
4. Do NOT re-research from scratch
5. Update TASK_REGISTRY.json

### For ALREADY RESOLVED Gaps (pointer only):
1. Read existing research doc (pointer exists, no re-research)
2. Update TASK_REGISTRY.json with status: "pointer-exists"
3. No new file written

---

## 🔍 Research Tool Protocol (T0-T6)

| Tier | Tool | When to Use |
|------|------|-------------|
| **T0** | Local cache (`.firecrawl/`) | Check before any external search |
| **T1** | `websearch` | Primary search (free, no telemetry) — **include "2026"** |
| **T2** | `webfetch` | Deep extraction from specific URLs |
| **T3** | `searxng_searxng_search` | Semantic/neural search refinement |
| **T4** | `omega-hub_sovereign_search` | High-precision seeds (Exa API) |
| **T5** | `firecrawl_firecrawl_scrape` | Full-page scrape (credits) |
| **T6** | `sieve research` | Full research pipeline (local-first) |

**TEMPORAL MANDATE**: Include "2026" or "latest" in all queries. Do NOT search for "2024" or "2025".

---

## 📝 Example Workflow for R30 (Circuit Breaker)

1. Check Cross-Reference Index → R30 is GREENFIELD (no existing benchmark doc)
2. No existing research to duplicate — proceed with new research
3. `websearch` queries:
   - "circuit breaker library benchmark 2026 pyresilience tenacity stamina pybreaker interlock-cb"
   - "circuit breaker latency false positive rate 2026"
   - "circuit breaker resource overhead async python 2026"
4. `webfetch` benchmark results URLs
5. Write benchmark findings to `PHASE2_RESEARCH_20260813.md`
6. Post to Hivemind with `intent: decision`
7. Update TASK_REGISTRY.json

---

## 📡 Hivemind Coordination (MANDATORY)

**Before starting**: `omega-hub_hivemind_get_awareness()` — check who's working

**During sprint**: `omega-hub_hivemind_heartbeat(channel="opencode", entity="researcher")` every 5-10 min

**After each gap**: `omega-hub_hivemind_post_context(...)` with:
- `intent`: "decision" or "observation"
- `task_current`: concise description of active task
- `focus_chain`: list of previous sub-tasks
- `continuation`: next steps or handoff notes for next session
- `suggested_model`: optional hint for next model

**Hivemind Post Template**:
```json
{
  "channel": "opencode",
  "entity": "researcher",
  "model": "oracle/nvidia/nemotron-3.5-lightning:free",
  "task_current": "Phase 2 gap R30: circuit breaker benchmark",
  "focus_chain": ["R31: dimension/free-will mapping", "R33: living research OS body"],
  "decisions": ["Selected pyresilience as breaker library based on benchmark results"],
  "continuation": "Proceed to R31 dimension mapping",
  "session_id": "ses_...",
  "intent": "decision",
  "suggested_model": "oracle/nvidia/nemotron-3.5-lightning:free"
}
```

---

## 📁 Deliverable Checklist

**Phase 2 Research Package** (due end of Week 3):
- [ ] `PHASE2_RESEARCH_20260813.md` — consolidated research findings for all 27 gaps
- [ ] 27 individual research report files in `data/entities/researcher/workspace/research_reports/`
- [ ] Hivemind posts for each gap resolution (27 posts)
- [ ] `TASK_REGISTRY.json` updated with all 27 gap completion statuses
- [ ] `CROSS_REFERENCE_INDEX.md` updated with new research doc entries (if applicable)
- [ ] `SESSION_ANCHOR.md` refreshed with Phase 2 start state

---

## 🚨 Escalation Triggers

If any of the following occur, escalate to @kali via Hivemind (intent: blocker):

1. **Missing tool**: Required tool not available (e.g., benchmark suite missing)
2. **Contradictory research**: Two sources give opposite answers
3. **Unclear requirement**: Gap description ambiguous or infeasible
4. **Tool-chain collapse**: Mandatory tool fails (e.g., `websearch` down)
5. **Sovereign mandate conflict**: Research conflicts with M1-M25 mandates

---

## 💾 Storage Architecture Awareness

- **8TB HDD** (`~/OmegaLibrary/hf_cache/hub`): Model weight blobs, large datasets. Sequential access only (~150MB/s).
- **NVMe** (`omega_library`): Active models for inference. Copy from HDD before experimentation.
- **Never** download directly to the HDD for active use — always `hf download` to the cache, then copy the GGUF/safetensors to `omega_library` for inference.

**Cache Configuration**:
- `HF_HUB_CACHE` → `~/OmegaLibrary/hf_cache/hub` (HDD, large blobs)
- `HF_HOME` → `~/.cache/huggingface` (NVMe, metadata/tokens)
- `HF_DATASETS_CACHE` → `~/OmegaLibrary/hf_cache/datasets` (HDD, parquet files)

---

*⬡ OMEGA ⬡ KALI ⬡ RESEARCH-EXEC ⬡ PHASE2 ⬡ 20260813*
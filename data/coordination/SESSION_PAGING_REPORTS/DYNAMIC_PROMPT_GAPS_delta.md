<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SESSION PAGING REPORT — Dynamic Prompt Gaps DELTA
## Recovery Artifact + Post-Hydration Delta (roc_racoon → kali)

**AP Token**: `AP-DP-GAPS-DELTA-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_dp_gaps_delta ⬡ PAGED-RESPONSE

**Date**: 2026-08-21
**Page source**: kali (ses_fdef2be4effe4pAaLXCTUx62GO), Architect-direct mission
**Hydration**: ACTIVE_SPRINT.json (PUBLIC-DEBUT-01) + docs/specs/PROJECT_INDEX.md read ✅
**Standing Order #7 re-validation**: D-569 confirmed in sprint decisions_locked: "Ratify Dynamic Prompt + Planner/Executor + Domain Loading as POST-DEBUT Cognitive Architecture Blueprint (Horizon 3). Gaps DP-1..DP-8 registered." KD workstream confirmed ratified via D-578..D-584.

---

## 0. 🚨 CRITICAL DISCOVERY — BROKEN GAP POINTERS (M23-adjacent integrity issue)

**The canonical report for ALL EIGHT DP gaps no longer exists on disk.**

| Fact | Detail |
|------|--------|
| Registered pointer | GAP_REGISTRY.json lines 356–420: every DP-1..DP-8 entry has `"report": "data/coordination/DYNAMIC_PROMPT_PLANNER_EXECUTOR_LOCAL_GAPS_20260819.md"` |
| Dead path | That file was written 2026-08-19 (1,480 lines, 66KB, verified complete) but is **now absent** — deleted by a later cleanup/deletion pass (likely coordination-file hygiene or DEL-1-adjacent sweep; deletion not logged in any tracker I can see) |
| Impact | Any agent picking up DP-* tickets per D-569 will hit a dead report link and have zero evidence base |
| This document | Serves as the RECOVERY artifact — reconstructs all load-bearing findings from session context below |

**Recommended remediation for kali** (I did NOT modify GAP_REGISTRY.json per paging rules):
1. Either restore/rename this delta file as the DP plan report, or update DP-1..DP-8 `"report"` fields to point at `data/coordination/SESSION_PAGING_REPORTS/DYNAMIC_PROMPT_GAPS_delta.md`
2. Add a one-line note to the deletion-campaign runbook: coordination reports referenced by GAP_REGISTRY must never be swept without updating pointers

---

## 1. RECOVERED FINDINGS — Original Gap Analysis (2026-08-19 session)

### 1.1 What exists today (verified by direct file reads)

**System prompt construction** (`src/omega/oracle/oracle.py:773-816`, `_prepare_system_prompt()`):
- Pure string concatenation: `[f"You are {personality}"]` + ContextBuilder memory block + soul_utils L3 block
- Affinity presets PREPEND their `system_prompt` ahead of the built prompt (~oracle.py:1024-1038) — order: affinity preset → personality+memory+soul. Any template system must preserve or explicitly re-order this.
- soul_utils.py caps injected soul items at 3 (M18 Token Efficiency)
- Degradation scaling inside build_context: Stressed=50%, Critical=25%, Disabled=0% of token budget

**ContextBuilder** (`src/omega/oracle/context_builder.py`):
- Assembly order: world state → gnosis block (SelectiveHydration top-K L3 from Qdrant) → MemoryBlocks (Letta-style core tier) → compacted memory
- Compaction pipeline: ObservationMasking (free) → Headroom semantic compression (60–95%) → sliding window fill → emergency truncation
- Token estimation is crude: `len(text) // 4`
- DEFAULT_TOKEN_LIMIT = 4000 (constants.py); DEFAULT_CONTEXT_LIMIT=6 exchanges, MAX_HISTORY_EXCHANGES=20

**Planner/Executor** (`src/omega/oracle/planner/hybrid_orchestrator.py` + `dag_schema.py`):
- HybridOrchestrator EXISTS and works: cloud planner emits JSON DAG (default `claude-sonnet-4.6` via antigravity), local executor runs sub-tasks
- **Hardcoded models**: planner prompt constant targets cloud; `_execute_local()` hardcodes `qwen3-1.7b` @ temperature 0.0 with JSON-schema enforcement
- M7 gatekeeper `should_run_locally()`: dep depth >2 → cloud; est tokens >4096 (MAX_LOCAL_TOKENS) → cloud; REASON/SYNTHESIZE → cloud-only; trivial/simple schema-constrained → local
- Escalation: 2 local retries then single-subtask cloud escalation
- PLANNER_SYSTEM_PROMPT + LOCAL_EXECUTOR_SYSTEM_PROMPT are module constants (lines ~53–73) — natural seed material for DP-7 templates

**Subagent dispatch** (`subagent_dispatcher.py` + SUBAGENT_DISPATCH_PROTOCOL.md):
- HandoffPacket: task_type enum, context_delivery="inline" default, loop guards (visited_agents, max_hops), ZONEID_HANDOFF magic
- Capability registry built from WAD dispatch.yaml: mode/purpose/capabilities/domains/node_slot/**task_tool_type**/owned_files/model
- §0 critical lesson: INLINE CONTEXT IS THE DIFFERENCE — three identical dispatches, only inline-context one succeeded (544-line report). File-path-only dispatches fail.
- §12 L2.5 dual-artifact rule: execution agents read ONLY Artifact B (comment-free machine patch) — contamination lesson directly applicable to executor prompt design

**Knowledge loading (fragmented across 5 systems)**:
- Library (`src/omega/library/`): inbox→extractor→curator→indexer→research, offline-first, SSRF/path guards
- MemoryStore: hot LRU (50 sessions) / warm JSONL+optional Redis / cold archive; FTS5 BM25 + vector RRF hybrid; sovereign_ingest Sieve→Sign→Index
- MemoryBlocks (`memory/blocks.py`): typed blocks w/ limit SLA, category decay rates, governance levels PRIVATE/SHARED_READ/SHARED_WRITE/PUBLIC — ready-made primitive for shared domain content
- SelectiveHydration: L3 principles under Qdrant collection prefix `l3_gnosis_{entity_name}` — entity-scoped, NOT domain-scoped; domain retrieval needs new namespace scheme
- Entity affinity YAML: structured match schema (domain/complexity_gt/online/requires/prompt_length_lt), first-match-wins, tier fallback chain cloud→local_deep→local_fast→iris; per-entity `inference_presets` incl. `preferred_context`
- Lattice CLI seeds (`docs/gnosis/lattice/`): per-CLI knowledge files + Jem 3-facet tier mapping
- AGENT_KB_PROTOCOL.md: discovery/contribution/staleness protocol; known gaps — reinforcement_count not instrumented, lint not automated

**Context window data (scattered across ≥3 places)**:
- config/models.yaml: `context_window` AND separate `context_budget` fields per model
- config/model_registry/models/{local,cloud}/*.yaml.md: per-model cards (nemotron-3-ultra-local: 1M window / 32K output; gemma-4-31b-it-free: 262K)
- providers.yaml supported_models lists: NO window metadata
- NativeGGUFProvider._select_optimal_context(): auto-picks largest of [32768,16384,8192,4096] that fits RAM — existing dynamic-sizing hook DP-2 should formalize
- **ANOMALY FLAGGED, NEVER FIXED**: qwen3-1.7b has context_budget=15000 > context_window=8192 — budget exceeds window; whoever builds DP-2 registry should reconcile these two field families

**Local inference (16GB Zen 2)**:
- NativeGGUFProvider: CPU affinity (compute cores [0,2,4,6] default), KV cache type_k/type_v default f16 (q8_0 crashes some models e.g. Qwen3 — config override only), n_threads=6, n_batch=512/n_ubatch=32 tuned to Zen2 L2, worker-process isolation (C++ crash containment), SomaticState save/load via llama_copy_state_data/set_state_data through worker queues — **fully implemented, ZERO callers**
- Provider chain: native-gguf(0)→lmster(1)→ollama(2,disabled)→antigravity(3)→google(4)→openrouter(5)→opencode-zen(6); MaKaLi routing overrides
- ProviderSelector score = priority*10 − PII penalty (−100 cloud if PII) − latency penalty − CUSUM stability penalty. **No context-window term.**

### 1.2 The eight gaps as I defined them (match registered DP IDs)

| ID | Gap | Key local evidence |
|----|-----|-------------------|
| DP-1 | Dynamic Prompt Builder (template engine, role-aware, domain slots) | _prepare_system_prompt is ~43 lines of concat; single delegation point |
| DP-2 | Context Window Registry (single source) | windows scattered in models.yaml + model_registry + provider configs; R2 partially resolved |
| DP-3 | Planner/Executor Model Router (role + context-aware) | HybridOrchestrator hardcodes qwen3-1.7b executor; Nemotron 1M + MiMo 32K unrouted |
| DP-4 | Domain Module Loader (unified load_domain()) | 5 fragmented systems; no packaging/metadata/deps/versioning |
| DP-5 | Per-Role Token Budgets | single DEFAULT_TOKEN_LIMIT=4000 regardless of role/model |
| DP-6 | Domain→Context Window Map | affinity has preferred_context per ENTITY, nothing per DOMAIN |
| DP-7 | Versioned Prompt Templates | prompts are code constants; no versioning/validation/A-B |
| DP-8 | SomaticState Planner Integration | save/load implemented in provider, unused anywhere |

Original effort estimates: DP-2 ≈2h, DP-3 ≈4h, DP-1 ≈8h, DP-5 ≈3h, role templates ≈4h, domains ≈12h, SomaticState wiring ≈6h, template versioning ≈8h.

---

## 2. POST-HYDRATION DELTA — How the Engine Moved Under the Blueprint (2026-08-19 → 2026-08-21)

### 2.1 ⚠️ ARCHITECTURE-LEVEL INSIGHT: LI SequentialModelLoader changes DP-3's shape

The ratified LOCAL-INFERENCE-OPT workstream (LI-1..LI-5) commits to **SequentialModelLoader — ONE model resident at a time** on 16GB (Qwen3-4B / Qwen3-4B-Thinking / Qwen3-1.7B Tier 0 matrix, q8_0 KV where safe).

**Consequence for the Architect's planner/executor vision**: a SPATIAL split (planner model + executor model loaded simultaneously, parallel DAG execution) is **physically impossible** on this hardware under LI constraints. The blueprint must be **TEMPORAL**:
```
Phase A (plan):   load large-context model → emit DAG → SomaticState save → UNLOAD
Phase B (exec):   load small model → execute tasks sequentially → done
(optional Phase A′: reload planner state for re-planning on failure)
```
This makes **DP-8 (SomaticState) load-bearing for DP-3**, not an optional P8 nicety. State save/restore is what makes sequential plan→execute cheap (skip weight reload; llama_set_state_data restores KV/context). Recommend re-scoping: DP-3 depends_on DP-8.

Also note: Nemotron-3-ultra-local (1M ctx) is NOT in the LI Tier 0 matrix — it's a cloud-floor model for kali (nemotron-3-ultra-free per CI-2). Local planning will realistically run on **Qwen3-4B-Thinking (32K)**, not 1M. Blueprint should target 32K planner budgets, not 64K+.

### 2.2 ✅ CONVERGENCE: DS workstream already instantiates my DomainLoader layout

DOCUMENTATION-SYSTEM (DS-1..DS-5) creates:
- `docs/strategy/domains/<domain>/` workspace authoring layer
- `config/domains/<domain>/` runtime module layer (DS-3 does exactly this for gemini-notebook)
- `scripts/sync_domain_docs.py` validated-copy sync (DS-4)

My original DP-4 blueprint specified `config/domains/*.yaml` modules with metadata/blocks/principles/prompt_snippets/affinity_overrides. **These are the same convention — do not fork it.** KD implementation should extend DS's `config/domains/<name>/` directory convention with the DomainModule schema rather than inventing a parallel path. DP-4 owner (maat) should coordinate with DS owner (kali/maat_n3).

### 2.3 ⚠️ CONSTRAINT: D-536 one-router rule governs DP-3

DEL-1 Week 2 deletes TriageRouter + SemanticRouter + RoutingTable; ProviderSelector + providers.yaml becomes the ONLY router. My original recommendation ("extend ProviderSelector with get_ordered_providers_for_role()") already complies — but any DP-3 design that reintroduces role-routing as a separate router class would violate D-536. Role selection must be a **parameter into ProviderSelector scoring**, not a new routing layer.

### 2.4 Budget reality from Carmack review

Carmack Context Injection review (2026-08-20): **18K base tokens fits Qwen3-4B** — that's the Tier 0 system-prompt ceiling. Implications:
- DP-1 prompt builder must treat ~18K as the TOTAL prompt envelope for local execution roles
- DP-5 budgets should be expressed as fractions of the resolved model window minus output reservation, not absolute numbers
- MANDATES_CONDENSED.md (~1.5K tokens, CI-1) becomes the canonical "mandates block" any template injects — reuse it, don't duplicate mandate text in role templates
- Sovereign compaction plugin (CI-3) injecting mandates+entity+phase pre-compaction overlaps conceptually with DP-1's job at the OpenCode layer; keep engine-layer DP-1 (oracle) and IDE-layer CI-3 (opencode plugin) explicitly separated to avoid double-injection

### 2.5 Headroom (HR) interplay

HR-1 HeadroomMiddleware sits in ModelGateway._prepare_messages(); HR-2 adaptive context buffer. DP-1/DP-5 operate upstream (prompt assembly); HR compresses downstream (message payloads). Sequencing: build DP-5 budgets against PRE-compression sizes or you'll double-count savings. Flag for maat who owns both HR and DP-1/2/3/5/6/8.

---

## 3. FORGOTTEN / NEVER-EXECUTED ITEMS (flagged 2026-08-19, still open)

| # | Item | Where flagged | Status now |
|---|------|--------------|------------|
| 1 | Entire DP-1..DP-8 set | My report → D-569 ratification | Registered, all `outstanding`, zero implementation |
| 2 | Broken report pointers (§0 above) | Discovered THIS session | Unremediated — needs kali action |
| 3 | qwen3-1.7b context_budget(15000) > context_window(8192) anomaly | models.yaml read | Never reconciled |
| 4 | docs/strategy/AGENTS.md referenced by dispatch protocol but MISSING | Original §10 | Still missing (only .agents/AGENTS.md exists, different content — Antigravity-specific) |
| 5 | SomaticState save/load: implemented, zero callers | providers.py:1028-1076 | Still unused; now elevated by LI sequencing argument (§2.1) |
| 6 | CompactionHarvester threshold is exchange-count-based (30), not token/window-based | compaction_harvester.py | Unchanged; should scale with model window when DP-2 lands |
| 7 | ProviderSelector has no context-window term in scoring | provider_selector.py | Unchanged; DP-3 hook point |
| 8 | Affinity preset prepend-order semantics (preset BEFORE personality) | oracle.py:1024-1038 | Undocumented behavior any template refactor must preserve/test |
| 9 | SelectiveHydration entity-scoped collections (`l3_gnosis_{entity}`) block domain-scoped retrieval | selective_hydration.py | Needs namespace scheme decision before DP-4 |

---

## 4. KD-DOMAIN-SPECIFIC INSIGHTS (for the ratified KD workstream)

1. **Reuse MemoryBlock governance for domain sharing**: PRIVATE/SHARED_READ/SHARED_WRITE/PUBLIC + category decay rates are already built — domain modules should BE governed blocks, not a new ACL system.
2. **Curator pipeline exists**: Library curator.py quality gates can validate domain content at authoring time; DS's "curator model" concept should call into it rather than spawn new validation code.
3. **Lattice seeds are proto-domains**: `docs/gnosis/lattice/{gemini,opencode,cline,copilot,antigravity}_cli.md` are exactly per-domain knowledge files — first five migration candidates for `config/domains/`.
4. **Jem 3-facet tier mapping** (Initiate L1 gather / Analyst L2 synthesize / Editor L3 resolve, each with its own model) is a WORKING precedent of role-differentiated models doing staged cognitive work — cite it as internal evidence when justifying planner/executor differentiation.
5. **Domain→window mapping seeds**: engineering/coding domains fit 8K; architecture/research domains want 16–32K; declare `target_context_window` per module (my original schema field) so DP-6 falls out of DP-4 packaging for free.

---

## 5. REVISED BLUEPRINT SEQUENCE (evidence-updated, Horizon 3 entry order)

```
DP-2  Context Window Registry        — FIRST. Reconcile models.yaml budget-vs-window anomaly.
                                        Feed _select_optimal_context() + ProviderSelector term.
DP-5  Per-Role Token Budgets         — express as % of resolved window − output reserve;
                                        18K Tier 0 ceiling per Carmack.
DP-8  SomaticState wiring            — promote from P8: enable temporal plan→execute swaps
                                        (depends only on provider code that ALREADY works).
DP-3  Role-aware ProviderSelector    — parameter, NOT new router (D-536). depends_on DP-2+DP-8.
DP-1  DynamicPromptBuilder           — Jinja2-or-lighter templates at _prepare_system_prompt();
                                        inject MANDATES_CONDENSED block; preserve affinity prepend order.
DP-7  Template versioning/validation — after DP-1 stabilizes.
DP-4  DomainLoader                   — converge with DS config/domains/<name>/ convention;
                                        depends_on Qdrant migration per registry note.
DP-6  Domain→window map              — falls out of DP-4 schema (target_context_window field).
```

**Files I could not access / verify this session**: none new — but note the ORIGINAL deliverable file itself is the inaccessible artifact (deleted; reconstructed here from session context instead).

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_dp_gaps_delta ⬡ COMPLETE*

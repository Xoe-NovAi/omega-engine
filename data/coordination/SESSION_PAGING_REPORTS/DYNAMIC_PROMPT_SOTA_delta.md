<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# DYNAMIC PROMPT SOTA — Session Paging Delta Report
**AP Token**: `AP-RESEARCHER-DP-SOTA-DELTA-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_dp_sota_delta ⬡ PAGED-RETURN
**Date**: 2026-08-21
**Origin**: Paged return from dormancy (paged by kali, ses_fdef2be4effe4pAaLXCTUx62GO)
**Original Mission**: Deep web research — Dynamic System Prompt Builders, Planner/Executor Architectures, Context-Window-Aware Prompting, Knowledge Domain Loading (2025-2026 SOTA). 7 deliverables in `docs/research/R_*_20260819.md`.
**Hydration**: ACTIVE_SPRINT.json (PUBLIC-DEBUT-01) + docs/specs/PROJECT_INDEX.md + GAP_REGISTRY entries via STRATEGY_CORPUS_MAP.md §DP table. D-569 RATIFIED.

---

## 0. Hydration Summary — What Changed Since My Research

| Dimension | My Blueprint Assumed (2026-08-19) | Engine Reality Now (2026-08-21) | Delta Impact |
|-----------|-----------------------------------|----------------------------------|--------------|
| **Status** | Research deliverables awaiting review | **D-569 RATIFIED** as POST-DEBUT Cognitive Architecture Blueprint (Horizon 3); DP-1..DP-8 registered | Blueprint is now binding scope |
| **Planner model** | Qwen3-14B Q4_K_M, ctx=16K | Tier 0 hardware-honest: **Qwen3-4B / 4B-Thinking / 1.7B sequential**, q8_0 KV, 18K base tokens (Carmack verdict) | ⚠️ See Finding F1 — plan-step ceiling risk |
| **Compression layer** | LLMLingua-2 / RECOMP / Selective Context pipeline | **Headroom** semantic compression (40-90% savings), HR-1/HR-2/HR-3 registered; combined Headroom+Qdrant pipeline = 86.8% token reduction | LLMLingua family demoted to complement for system prompts only |
| **Vector store** | FTS5-first + hybrid scoring | sqlite-vec now; **Qdrant SCHEDULED post-debut (D-570)** — reactivates RESEARCHER_QDRANT_MIGRATION_GAPS | DP-4 unblocked for Horizon 3 |
| **Memory subsystem** | Sequential loading to fit 16GB, swappiness=10 | zswap+NVMe swap ratified (D-526/D-527): 16GB NVMe swap, zswap 25% pool lzo_rle, **swappiness=100**, cgroup MemoryMax=6G | Memory budget math changes — see F6 |
| **Build constraint** | Unspecified template engine | **D-537 rejected library swaps for debut**; Grokster flagged Jinja2-vs-D-537 conflict for DP-7 | DP-7 must use stdlib templating or post-debut Jinja2 decision |
| **Build mode** | Greenfield-ish blueprint code | **Incremental on existing components**: ContextBuilder, SelectiveHydration, HybridOrchestrator, ProviderSelector, Context Packer, SDP — NOT greenfield (HMC hub D-569 note) | All recommendations below filtered through "map onto existing components first" |

---

## 1. Forgotten SOTA Findings Mapped to DP-1..DP-8

### DP-1 — Dynamic Prompt Builder (Cognitive Arch P1)
Highest-density findings from `R_DYNAMIC_PROMPT_BUILDERS_20260819.md` that were never operationalized:

1. **Priority-ordered section assembly, 10–95 range** (AgentPatterns.ai, OPENDEV arXiv:2603.05344): identity(10–30) → tools(40–50) → safety(55–65) → provider-specific(70–80) → dynamic context(85–95). Sections toggled per mode/provider. **This is the DP-1 core algorithm** — a ~50-line assembly engine.
2. **Two-tier fallback**: if custom section load fails (corrupt config/missing file), fall back to default sections — agent stays functional at baseline rather than hard-failing. Maps directly onto M9/M23 error-integrity requirements.
3. **Cache-aware static-prefix discipline**: static sections ALWAYS assembled before dynamic ones; any dynamic content inserted early invalidates cache for everything after. Directly relevant to the CI workstream's compaction plugin (CI-3) — same principle at OpenCode layer vs engine layer.
4. **Adaptive instruction layering** (light/standard/deep modes selected by query complexity analysis) — cheap way to make one builder serve 4B and 14B-class models without separate prompt sets.
5. **Microsoft hierarchical skill organization + two-stage ranking** (arXiv:2506.20815): skills grouped hierarchically, stage-1 coarse selection then stage-2 fine ranking using behavioral telemetry. This is the strongest published pattern for DP-1's "domain injection" leg AND feeds SDP telemetry.
6. **Substrate/Projection framing** (Zylos): context window is a materialized view, not storage. Adopt as the DP-1 design axiom; it composes cleanly with SelectiveHydration.

### DP-2 — Context Window Registry (P0)
From `R_LOCAL_INFERENCE_OPTIMIZATION_CPU_20260819.md`:
1. **KV cache grows linearly with context and lives in RAM** — llama.cpp defaults often allocate max-context KV up front (~2.8GB at 8K for a 9B). Registry must record not just max_ctx but **KV-bytes-per-token per model** so budget math is exact.
2. **Always set --ctx-size explicitly** — never inherit runtime defaults.
3. Task-type × context-size tier table (4K single-file fixes / 32K multi-file / 128K architecture) from LocalAIMaster — usable as registry metadata for DP-6.
4. q8_0 KV quantization (`-ctk q8_0 -ctv q8_0`) halves KV footprint with negligible loss — already adopted by LI workstream; registry should encode it as a per-model flag.

### DP-3 — Planner/Executor Model Router (P2)
From `R_PLANNER_EXECUTOR_CONTEXT_WINDOW_20260819.md`:
1. **Model size ↔ plan-step ceiling** (LocalGraph benchmark table): 3B–8B → 3–4 steps; 13B–34B → 4–6; 70B+ → 5–7. Router should consult this when assigning planner duty.
2. **Critic MUST be a different model than executor** (bias-sharing failure mode; Anthropic Outcomes primitive concurs). With Tier 0 = 4B/4B-Thinking/1.7B, use 4B executor + 1.7B critic (different arch/size) — satisfies the rule locally.
3. **LLMCompiler DAG streaming** (planner streams task DAG; fetching unit schedules) — the right shape if DP-3 later needs parallel steps.
4. **ROMA recursive decomposition**: each node decides decompose-vs-delegate, aggregating ONLY summaries upward — best published answer to "how does a small-context planner handle long-horizon state."
5. Replanning triggers taxonomy: tool error, new information, critic rejection, retry-budget exhaustion.

### DP-4 — Domain Module Loader (P3, needs Qdrant)
From `R_KNOWLEDGE_DOMAIN_LOADING_20260819.md`:
1. **Four-paradigm hybrid** (arXiv:2502.10708 survey): dynamic injection (RAG/MCP), static embedding (fine-tune), modular adapters (LoRA), prompt optimization (domain system prompts). Loader API should expose all four as capabilities of a domain.yaml, not hardcode one.
2. **Domain module layout I proposed maps 1:1 onto DS workstream structure**: `domain.yaml` (metadata/version/deps) + `system_prompt.md` + `adapter/` + `mcp_tools/` + `corpus/`. The DOCUMENTATION-SYSTEM workstream (DS-2..DS-4, workspace authoring + config/domains runtime module + validated-copy sync) IS this loader's filesystem half — converge them rather than building twice.
3. **MCP-as-knowledge-layer** (SafeMate arXiv:2505.02306): expose each domain as MCP tools (`search_domain`, `get_concept`, ...); planner and executor see identical tool surface. Aligns with P2 "MCP Domain Split (4 servers)" already in PROJECT_INDEX Next Actions.
4. **Domain composition rules**: primary domain prompt wins; secondary appended; adapters stack; MCP tools union. Needed for multi-domain tasks (tarot+swe).
5. **100K-token heuristic**: KBs under ~100K tokens can skip RAG entirely (full-context load + caching). Relevant for small curated domains on 18K-token budgets — most Omega domains will NOT fit, but glossary-scale ones will.

### DP-5 — Per-Role Token Budget Manager (P1)
From `R_PROMPT_COMPRESSION_CONTEXT_DISTILLATION_20260819.md` + `R_ROLE_AWARE_PROMPTING_20260819.md`:
1. **Tiered allocation: critical 40% / high-value 35% / supplementary 25%**, with compression order supplementary→high-value and critical never dropped. This is the budget manager's core policy.
2. **Role context isolation** (Deep Agents production pattern): planner sees goal+todo+summaries; executor sees current step only; critic sees spec+output only. "Feed the executor full history and it gets confused."
3. **Planner context growth alarm**: ">10K tokens by step 20 means something is wrong" (Bharat) — implementable as a budget-manager invariant/warning.
4. **Lazy context expansion**: start minimal, enrich on follow-up if response suggests missing info — cheaper than always packing full.
5. Compression technique↔component matching survives Headroom's arrival: RECOMP-style extractive for RAG slices, Selective-Context-style sentence gating for contracts, LLMLingua-2-style for verbose static prompts. Headroom handles tool outputs (HR-1/HR-3); these handle prompt-side components Headroom doesn't target.

### DP-6 — Domain Context Window Map (P0)
1. Quantization sensitivity varies BY TASK TYPE (bmdpat benchmarks): summarization/classification resilient at Q4; code gen + multi-step reasoning want Q5+; arithmetic/structured-output quality-critical Q6+. A domain→context-window map should co-record recommended quant + context, since both trade against the same RAM envelope.
2. Hierarchical prompting levels (4K scoping → 32K analysis → 128K implementation; 85% cost reduction claim) — the map should support per-domain level ladders, not single values.

### DP-7 — Planner/Executor Prompt Templates (P4)
From `R_ROLE_AWARE_PROMPTING_20260819.md` (this doc contains FULL ready-to-adapt templates for planner/executor/critic/verifier/researcher):
1. **Six-section anatomy**: Role / Objective / Tools (with trigger conditions + call budgets) / Constraints / Output Format / Examples. Checklist-enforceable.
2. **Structured task contracts**: planner output = schema `{id, description, executor_role, inputs, outputs, success_criteria, allowed_tools, context_budget, dependencies}` — kills the #1 cross-role failure (ambiguous delegation).
3. **Communicative dehallucination** (ChatDev): executor prompt MUST include "when you need specific information you were not given, ask the relevant role by name before producing output."
4. **BAD/GOOD example pairs** teach format more efficiently than rules.
5. **Verifier ≠ LLM**: at least one deterministic verifier role (pytest/mypy/pydantic); MAST found 21.3% of multi-agent failures were verification gaps.
6. Template versioning: version-controlled YAML configs with schema validation (Nitin Singh pattern) — satisfies DP-7's "versioned, validated" requirement without new deps.
7. ⚠️ **Jinja2 conflict**: D-537 rejected library swaps for debut. Recommend `string.Template`/f-string composition now; revisit Jinja2 as explicit post-debut decision if autoescape/inheritance needed.

### DP-8 — SomaticState Planner Integration (P8) — WEAKEST COVERAGE IN ORIGINAL RESEARCH, RICHEST REDISCOVERY
My original research under-served this gap, but the EmergentMind LLM Context Management survey (fetched during research, under-cited since) contains directly relevant systems:
1. **AIOS LLM Agent OS**: isolated LLMContext objects with snapshot/restore, preemptive scheduling, LRU-K eviction; **<5% overhead per context switch**, BLEU/BERTScore preserved across 2,000 concurrent contexts. Closest published analog to M20 SomaticState save/restore at the orchestration layer.
2. **MemTool** (Lumer et al., 2025): short-term tool-memory management with agent-decided/workflow/hybrid removal policies; ≥90% tool-removal efficiency with stable task completion. Complements HR-3 (Headroom MCP compress) — removal vs compression are different policies for the same budget problem.
3. **Context-Folding / AgentFold** (2025): proactive folding of stale context for long-horizon agents — the planning-continuity mechanism DP-8 wants between full snapshots.
4. **SagaLLM**: context management + validation + transaction guarantees for multi-agent planning — transactional semantics for plan-state mutation.
5. **Git Context Controller** (2025): manage agent context like git (branch/commit/revert of context state) — elegant fit with Omega's existing git-native culture.
6. **DisCEdge**: token-based context representation avoiding O(n) re-tokenization on restore — relevant to making SomaticState resume cheap.
7. M20 mandate already requires ctypes `llama_copy_state_data`/`llama_set_state_data` round-trip tests — DP-8 implementation should wrap those bindings behind an AIOS-style context-object API, plus KV q8_0 (LI-adopted) to shrink serialized state.

---

## 2. Techniques Worth Reviving for Planner/Executor or Domain Loading

| # | Technique | Source | Revival Target |
|---|-----------|--------|----------------|
| R1 | Priority-section assembly (10–95) + two-tier fallback | AgentPatterns/OPENDEV | DP-1 core loop |
| R2 | Structured task contract JSON schema | Bharat/Cline/LocalGraph | DP-7 templates + DP-3 router I/O |
| R3 | Critic-model-≠-executor rule | Anthropic Outcomes via Bharat | DP-3 routing table (4B exec / 1.7B critic) |
| R4 | ROMA summary-upward recursion | EmergentMind | Long-horizon planning within 4B planner ceiling |
| R5 | Tiered 40/35/25 budget allocation + lazy expansion | Hoomanely | DP-5 policy |
| R6 | Four-paradigm domain.yaml capability flags | arXiv:2502.10708 | DP-4 loader API |
| R7 | MCP-domain-tools symmetry (planner/executor same surface) | SafeMate | DP-4 + existing MCP split plan |
| R8 | MemTool removal policies alongside Headroom compression | EmergentMind survey | DP-5/HR complement |
| R9 | AIOS context snapshot/restore (<5% switch overhead) | EmergentMind survey | DP-8 design template |
| R10 | Anemoi semi-centralized protocol (−75% redundant context passing) | EmergentMind | Future multi-agent comms (directional — single-source) |

---

## 3. Flagged-But-Never-Executed Items

1. **EHPC (Evaluator Heads Prompt Compression, arXiv:2501.12959)** — training-free, beat LongLLMLingua on both quality (49.6 vs 48.0) and latency (0.88 vs 67.44) at time of research; no open-source release then. **Action**: re-check for release before Horizon 3 compression decisions; could undercut heavier compression deps.
2. **ik_llama.cpp fork** (better CPU perf, fused MoE ops) — never benchmarked on Ryzen 5700U. Cheap experiment for LI workstream.
3. **Speculative decoding on CPU** — net benefit unknown (draft acceptance >50% threshold); never validated. Low priority behind LI-1..LI-5.
4. **Hardware validation script** (XMP/EXPO check, governor, THP) — written into blueprint §9.4, never committed. Note ZS workstream now supersedes parts (swappiness=100 sanctioned, zswap enabled) — script needs rewrite against D-526/D-527 reality, not my original swappiness=10 advice.
5. **Compression benchmark harness** ("benchmark at ratios 2×/5×/10× on 100 representative tasks") — never built; needed before trusting any compressor (incl. Headroom) on Omega prompts.
6. **Mnemosyne 13-sphere / Lilith Tarot legacy integration** — flagged as domain-module candidates for DP-4; migration scripts still nonexistent.
7. **Unresolved Architect questions from blueprint §13** — partially answered by Tier 0 decision (planner=4B-class resolved; executor floor still open: is Qwen3-4B sufficient for tool-use execution, given GrandLinux data says 7B was marginal and 14B was the floor for coder models? Qwen3-4B-Thinking may compensate via reasoning, but this is UNTESTED — flag as DP-3 risk).

---

## 4. New Risks Introduced by Engine Movement (Post-Hydration Analysis)

- **F1 — Plan-step ceiling**: My benchmark table says 3B–8B planners cap at 3–4 steps. Tier 0 planner (Qwen3-4B) sits at that ceiling. Mitigation already exists in research: ROMA-style decomposition keeps plans shallow; DP-7 contracts keep steps self-contained. Recommend DP-3 acceptance test includes "plan ≤4 steps or delegate sub-plans."
- **F2 — Executor floor uncertainty**: GrandLinux evidence: 7B coder = too weak for tool use; 14B = floor. Tier 0 has no 14B. Either accept degraded execution scope (single-file tasks) or define Tier 1 escalation path to 14B via zswap-backed loading (now feasible per D-526).
- **F3 — zswap changes memory math**: swappiness=100 means the OS WILL page model weights under pressure; with `--mlock` that's prevented but risks OOM-kill instead. LI-2 SequentialModelLoader + MemoryMax=6G cgroup interaction needs explicit testing — my blueprint's "sequential fits in 16GB" claim was computed pre-zswap.
- **F4 — Compaction plugin (CI-3) vs DP-1 overlap**: sovereign-compaction injects mandates+entity+phase pre-compaction at OpenCode layer; DP-1 does the same at engine layer. Keep layers distinct: CI handles OpenCode sessions, DP-1 handles Oracle/omega talk calls. Document the boundary in DP-1 spec to prevent double-injection.

---

## 5. Verification Status

All findings above trace to sources fetched live during original session (URLs in the seven R_*_20260819.md deliverables, §Sources tables). Single-source/directional claims remain flagged there (OPENDEV paper specifics, EHPC numbers, Anemoi percentages, PwC verifier stat, Anthropic Outcomes citation). No new web fetches were performed in this paging session per file-first directive; deltas are synthesis of hydrated engine state + prior verified research.

*⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_dp_sota_delta ⬡ 2026-08-21*

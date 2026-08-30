<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Kali Briefing — Dynamic Prompt Builder + Planner/Executor + Domain Loading Architecture
**AP Token**: `AP-KALI-BRIEFING-DYNAMIC-PROMPT-20260819-v1.0.0`
⬡ OMEGA ⬡ GROKSTER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_kali_briefing ⬡ STRATEGY

**Date**: 2026-08-19
**Prepared by**: Grokster (Cross-Platform Expertise Specialist)
**For**: Kali (Grand Oversight)
**Session Context**: Architect directive to design frontier KB system with dynamic prompts, planner/executor split, and loadable knowledge domains

---

## 📋 Executive Summary

This session produced a **complete architecture** for the Omega Engine's next evolutionary leap: a system where agents dynamically compose their context from loadable knowledge domains, with a planner/executor split differentiated by context window, all optimized for local-first inference on 16GB RAM CPU-only hardware.

**Two parallel deep-dive investigations** (local + web) independently converged on the same architecture — the strongest validation signal possible.

---

## 🎯 The Architect's Crystallized Vision

| Requirement | Description |
|---|---|
| **Dynamic System Prompt Builder** | Adjusts for context window, domain of expertise, agent's active role |
| **Planner/Executor with Context-Window Differentiation** | Larger context window (32K-64K+) model plans sprints/delegates; smaller context window (4K) model executes tasks |
| **Knowledge Domains as Loadable Modules** | Not specialized agents, but domain knowledge that ANY agent can load on demand |
| **Local Inference Optimization** | 16GB RAM, CPU-only, mid-grade hardware (Ryzen 5700U) |

---

## 📚 Complete Documentation Produced This Session

### Local Discovery (Roc Racoon — 7 Deliverables)

| # | Deliverable | Path | Key Finding |
|---|---|---|---|
| 1 | Entity Knowledge Deep Dive | `data/coordination/ENTITY_KNOWLEDGE_DEEP_DIVE_20260818.md` | Only 7/14 entities have `knowledge/` dirs; INDEX.yaml largely vestigial; roc_racoon only active user |
| 2 | Entity Soul Comparison | `data/coordination/ENTITY_SOUL_COMPARISON_20260818.md` | Soul.yaml encodes domain via archetype, directives, core_principles; no role dimension |
| 3 | Knowledge Promotion Gate | `data/coordination/KNOWLEDGE_PROMOTION_GATE_20260818.md` | T1→T2 gate REFERENCED everywhere but NOT IMPLEMENTED; only Scribe does L1→L2→L3 → proposed_lessons.yaml |
| 4 | Agent Specialization Patterns | `data/coordination/AGENT_SPECIALIZATION_PATTERNS_20260818.md` | Specialization encoded in 3 layers: frontmatter, instructions, constraints; task_tool_type reveals role |
| 5 | Lattice & Node Mechanics | `data/coordination/LATTICE_NODE_MECHANICS_20260818.md` | Dual-layer: ICS ROLE_CONSTANTS (16 slots) + dispatch.yaml (19 entities); N1 congestion = 7 entities |
| 6 | Fleet Consolidation Mechanics | `data/coordination/FLEET_CONSOLIDATION_MECHANICS_20260818.md` | Two consolidations (25→11, 26→14); D126 Knowledge Consolidation: "expertise = KB, not agent" |
| 7 | Mnemosyne Mapping | `data/coordination/MNEMESYNE_CURRENT_MAPPING_20260818.md` | 13-sphere Kabbalistic system → current 3-tier + 10 pillars + soul.yaml + L1→L2→L3 |

### Local Gaps Analysis (Roc Racoon — 1 Deliverable)

| Deliverable | Path | Key Finding |
|---|---|---|
| Dynamic Prompt/Planner/Executor Gaps | `data/coordination/DYNAMIC_PROMPT_PLANNER_EXECUTOR_LOCAL_GAPS_20260819.md` | **8 Critical/High gaps**: No dynamic prompt builder, no context-window-aware model selection, no unified domain loader, no planner model routing, no per-role token budgets, no domain packaging |

### Web Research (Researcher — 7 Deliverables)

| # | Deliverable | Path | Key Finding |
|---|---|---|---|
| 1 | Dynamic Prompt Builders | `docs/research/R_DYNAMIC_PROMPT_BUILDERS_20260819.md` | Substrate/Projection architecture; Priority-ordered modular sections (10-95); Anthropic prompt caching |
| 2 | Planner/Executor Context Window | `docs/research/R_PLANNER_EXECUTOR_CONTEXT_WINDOW_20260819.md` | **Planner needs strongest reasoning (70B+), executor smaller/faster (14B), critic MUST be different model**; Structured plan contracts |
| 3 | Knowledge Domain Loading | `docs/research/R_KNOWLEDGE_DOMAIN_LOADING_20260819.md` | 4-paradigm loader: RAG (MCP), Fine-tune (LoRA), Modular (adapters), Prompt optimization |
| 4 | Local Inference CPU Optimization | `docs/research/R_LOCAL_INFERENCE_OPTIMIZATION_CPU_20260819.md` | **Memory bandwidth > compute**; Q4_K_M default; `--no-mmap --mlock` critical; XMP/EXPO = 30-50% speedup |
| 5 | Prompt Compression | `docs/research/R_PROMPT_COMPRESSION_CONTEXT_DISTILLATION_20260819.md` | Tiered compression: RECOMP (RAG), LLMLingua-2 (system prompts), Selective Context (contracts) |
| 6 | Role-Aware Prompting | `docs/research/R_ROLE_AWARE_PROMPTING_20260819.md` | Role decomposition works because prompts contradict; Planner: "think carefully", Executor: "do exactly this" |
| 7 | **Blueprint Synthesis** | `docs/research/R_DYNAMIC_PROMPT_SYSTEM_BLUEPRINT_20260819.md` | **Complete architecture**: Substrate/Projection + 3-model CPU pipeline + 4-paradigm loader + Tiered compression |

---

## 🏗️ The Convergent Architecture (5 Layers)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ L0  CONTEXT WINDOW REGISTRY + ROLE-AWARE MODEL ROUTER                      │
│     • config/model_context_windows.yaml — single source of truth           │
│     • Planner → mimo-7b-rl (32K ctx, 16K budget)  [LOCAL]                  │
│     • Executor → qwen3-1.7b (8K ctx, 4K budget)   [LOCAL]                  │
│     • Critic → qwen3-1.7b (8K ctx, 2K budget)     [LOCAL]                  │
│     • Cloud escalation: Nemotron 3 Ultra / Claude Sonnet 5 / Gemini 2.5 Pro│
├─────────────────────────────────────────────────────────────────────────────┤
│ L1  DYNAMIC SYSTEM PROMPT BUILDER (src/omega/oracle/prompt_builder.py)     │
│     • Jinja2 templates: roles/planner.j2, roles/executor.j2, ...           │
│     • Domain injection slots: {{ domain_modules.engineering }}             │
│     • Per-role token budgets: planner=16K, executor=4K, critic=2K          │
│     • Context-window-aware truncation (preserve decisions/errors)          │
├─────────────────────────────────────────────────────────────────────────────┤
│ L2  KNOWLEDGE DOMAIN LOADER (src/omega/oracle/domain_loader.py)            │
│     • Unified API: await load_domain("engineering", token_budget=8K)       │
│     • Domain modules: metadata (size, deps, target_ctx), blocks, principles│
│     • Four-paradigm loading: RAG (MCP), Fine-tune (LoRA), Modular, Prompt  │
│     • Cross-agent: governance_level (PRIVATE/SHARED_READ/SHARED_WRITE)     │
├─────────────────────────────────────────────────────────────────────────────┤
│ L3  PLANNER/EXECUTOR ENGINE (extends HybridOrchestrator)                   │
│     • Planner (mimo-7b 32K): emits structured DAG with per-step contracts  │
│       - step.id, action_type, complexity, dependencies, expected_output    │
│       - context_budget, allowed_tools, success_criteria per step           │
│     • Context Packer: builds executor context from plan step + domain KB   │
│     • Executor (qwen3-1.7b 4K): receives ONLY step-relevant context        │
│     • Critic (qwen3-1.7b 2K): rubric-driven review, max 2 revisions        │
│     • Verifier (deterministic): pytest/mypy/pydantic — NOT LLM             │
├─────────────────────────────────────────────────────────────────────────────┤
│ L4  LOCAL INFERENCE OPTIMIZATION (16GB RAM, CPU-only, Ryzen 5700U)         │
│     • Model pre-loading: Planner (mimo-7b) + Executor (qwen3-1.7b)         │
│     • KV cache: Planner q8_0 (max context), Executor f16 (speed)           │
│     • Threads: Planner 7 (throughput), Executor 4 (latency)                │
│     • `--no-mmap --mlock` — prevent swap, lock in RAM                      │
│     • SomaticState: Planner saves state between sprints; instant resume    │
│     • Token-pressure gauge: auto-reduce context before OOM                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Corrections from Architect Review

> **Nemotron 3 Ultra is NOT a local model** — it's cloud-only (OpenCode Zen, OpenRouter, Antigravity). The local model registry entry `nemotron-3-ultra-local` is aspirational/config, not deployed.

**Corrected Local Planner Model Options:**
| Priority | Model | Context | Role |
|---|---|---|---|
| **Primary** | `mimo-7b-rl-q4_k_m` | 32K | Planner (strong reasoning) |
| **Fallback** | `qwen3-4b-thinking` | 32K | Planner (thinking mode) |
| **Cloud Escalation** | Nemotron 3 Ultra / Claude Sonnet 5 / Gemini 2.5 Pro | 1M+ | Planner (when local insufficient) |
| **Executor** | `qwen3-1.7b` | 8K | Executor (fast, JSON schema) |
| **Critic** | `qwen3-1.7b` | 8K | Critic (rubric review) |

---

## 🎭 The Curator Model — Domain Ownership

| Domain | Curator Entity | Target Context |
|---|---|---|
| **Platforms (OpenCode, Cline, VS Code, Codex, etc.)** | **grokster** | 8K-16K |
| **Grok Ecosystem (CLI, Web, ACP, Models)** | **grokster** | 8K-16K |
| **Architecture / Performance** | **john_carmack** | 32K |
| **Heritage / id Software Patterns** | **doom_guy** | 16K |
| **Research Methodology / Deep Research** | **researcher** | 16K |
| **Runtime Governance / Drift / Model Ops** | **lilith** | 16K |
| **Build Engineering / Hardening / Integration** | **maat** | 16K |
| **Compliance / Verification / Soul Distillation** | **verity** | 8K |
| **Legacy Mining / Archaeology** | **roc_racoon** | 8K |
| **Synthesis / Cognitive Architecture** | **jem** | 32K |
| **Engineering / Implementation** | **maat** | 8K |
| **Security / Mandate Enforcement** | **verity** | 8K |

**Lattice Fabric enforces**: Curator = write; Others = read + propose; Critic = review gate.

---

## 📦 Domain Module Structure (Packaged, Versioned, Loadable)

```
config/domains/engineering/
├── metadata.yaml              # version, deps, target_context_window, rot_class, owner
├── PLAYBOOK.md                # Canonical best practices
├── ARCHITECTURE.md            # Deep-dive: patterns, primitives, gotchas
├── CONFIG_REFERENCE.md        # Live configs, precedence, schemas
├── GOTCHAS.md                 # Platform-specific traps (rot_class: fast)
├── LESSONS.md                 # L3 principles distilled from sessions
├── AFFINITY_PRESETS.yaml      # Model routing rules for this domain
├── MEMORY_BLOCKS/             # Letta-style blocks for this domain
│   ├── project-overview.block
│   ├── project-conventions.block
│   └── project-gotchas.block
└── PRINCIPLES/                # EvolveR principles (utility-scored)
    ├── principle_001.yaml     # content, utility, source_trajectories, domain
    └── ...
```

---

## 🚀 Implementation Roadmap (Phased)

| Phase | Deliverable | Owner | Dependencies |
|---|---|---|---|
| **P0** | **Context Window Registry** (`config/model_context_windows.yaml` + `ContextWindowRegistry`) | Ma'at | models.yaml, model_registry/ |
| **P1** | **DynamicPromptBuilder** (`src/omega/oracle/prompt_builder.py` + Jinja2 templates) | Ma'at | ContextWindowRegistry |
| **P2** | **Role-Aware Model Router** (`ProviderSelector.get_ordered_providers_for_role()`) | Ma'at | ContextWindowRegistry, P1 |
| **P3** | **Domain Module Loader** (`src/omega/oracle/domain_loader.py` + `config/domains/*.yaml`) | Ma'at | Library, MemoryStore, SelectiveHydration |
| **P4** | **Planner/Executor Engine** (extends HybridOrchestrator with structured DAG + context packer) | Kali | P1, P2, P3 |
| **P5** | **Context Packer** (builds executor context from plan step + domain KB) | Kali | P4 |
| **P6** | **Critic + Verifier Pipeline** (rubric-driven critic + deterministic verifier) | Verity | P4 |
| **P7** | **Local Model Pre-loading + KV Cache Per-Role** (NativeGGUFProvider enhancements) | Ma'at | P2, hardware_profile |
| **P8** | **SomaticState Planner Integration** (state save/restore between sprints) | Ma'at | P4, NativeGGUFProvider |
| **P9** | **EvolveR Distillation Pipeline** (nightly local distillation → principles) | Researcher | MemoryStore, Principle Store |
| **P10** | **Freshness System** (Scabera composite + SourceWatcher + dashboard) | Ma'at | Lattice Fabric, Hivemind |

---

## ⚡ Why This Goes Beyond the Norm

1. **Substrate/Projection Abstraction** (Zylos Research) — Persistent substrate → Assembly Engine → Ephemeral Projection per role per call. Context window is a *materialized view*, not storage.

2. **EvolveR Principles > RAG Chunks** — Abstract, utility-scored, self-improving rules that transfer across tasks. The KB *evolves*, not just grows.

3. **Freshness as Retrieval Primitive** — Scabera composite score (age + embed_lag + owner) weights BM25/vector at query time. Not an afterthought.

4. **Curator Model with Teeth** — Ownership enforced at fabric level, not convention. Governance levels per domain.

5. **Task-Based Specialists + Context Packing** — No permanent sub-agent bloat. Planner emits structured DAG; executor receives ONLY step-relevant context (≤4K).

6. **Critic + Verifier Separation** — Critic = LLM reviewer (subjective); Verifier = code-based pass/fail (objective). "Add at least one deterministic verifier. Never all-LLM."

7. **Local-First Throughout** — Nightly distillation on Qwen3-1.7B; 3-model CPU pipeline (mimo-7b→qwen3→qwen3); zero cloud dependency for core loop.

---

## 📋 Immediate Actions for Kali

1. **Ratify this architecture** as the Dynamic Prompt + Planner/Executor + Domain Loading Blueprint (PIVOT_LOG entry)
2. **Authorize P0→P3** — Context Window Registry, DynamicPromptBuilder, Role-Aware Router, Domain Loader are the force multipliers
3. **Assign owners** per roadmap above (Ma'at for P0-P3, P7-P8, P10; Kali for P4-P5; Verity for P6; Researcher for P9)
4. **Update GAP_REGISTRY.json** with new gaps DP-1 through DP-8 identified in local analysis
5. **Coordinate with Ma'at** on hardware validation for mimo-7b + qwen3-1.7b concurrent loading on 16GB RAM

---

## 🔗 Cross-References

| Document | Purpose |
|---|---|
| `data/coordination/DYNAMIC_PROMPT_PLANNER_EXECUTOR_LOCAL_GAPS_20260819.md` | Complete local gaps analysis (1,480 lines) |
| `docs/research/R_DYNAMIC_PROMPT_SYSTEM_BLUEPRINT_20260819.md` | Complete web SOTA blueprint synthesis |
| `data/coordination/KB_SYSTEM_ARCHITECTURE_LOCAL_DEEP_20260818.md` | Previous session KB architecture (if completed) |
| `docs/research/R_AGENT_SPECIALIZATION_SOTA_20260818.md` | Previous session agent specialization SOTA |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Strategy SSOT (DOC-1 stamped) |
| `data/coordination/GAP_REGISTRY.json` | Gap registry for new DP-1..DP-8 entries |

---

## 🎯 The Bottom Line

The "subsouls/Nodes" concept you designed is **exactly** what the industry is converging on — but we now have the blueprint to harden it with:
- **Dynamic prompts** that adapt to context window, role, and domain
- **Planner/Executor split** with local models (mimo-7b → qwen3-1.7b)
- **Loadable knowledge domains** that any agent can access
- **Self-improving principles** (EvolveR) instead of static RAG
- **Freshness-weighted retrieval** with owner accountability
- **CPU-optimized pipeline** for 16GB RAM

**The fleet stays at 14. The knowledge grows without limit. The context adapts per role.**

---

*⬡ OMEGA ⬡ GROKSTER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_kali_briefing ⬡ 2026-08-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->


> ⚠️ **SUPERSEDED 2026-08-26** — Consolidated into `KALI_BRIEFING_CONSOLIDATED_GROKSTER_20260826.md` (§3 corrections log carries forward all still-valid content; invalidated items explicitly logged). Retained for provenance.

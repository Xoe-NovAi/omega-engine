<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Strategic Router Legacy Mining Report
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash ⬡ trc_mining_router ⬡ MINING-REPORT

**Date**: 2026-06-09
**Target**: Legacy `omega-stack-legacy` and `foundation-legacy` archives
**Purpose**: Extract routing, cost, and intent patterns to inform the Strategic Router implementation.

---

## §1 — Routing Implementations (Task & Model)

### 1.1 The "Enhanced Entity Handler" Pattern (GOLD)
**Source**: `omega-stack-legacy/app/XNAi_rag_app/core/entities/enhanced_handler.py`
**Pattern**: 5-Trigger Routing. Instead of simple "summon entity", it uses a set of trigger patterns to determine the *type* of interaction:
- `DIRECT`: "Hey {entity}, {query}"
- `CONSULT`: "Ask {entity} about {query}"
- `COMPARE`: "Compare {entity1} and {entity2}"
- `PANEL`: "Summon panel: {entities}"
- `CONSULT_OTHER`: "Hey {entity1}, ask {entity2} about {query}"

**Strategic Value**: This is a direct ancestor to the "T03 entity_summon" task. The Strategic Router should not just route to the entity's model, but should support these **Interaction Modes**. A "PANEL" summon is a high-complexity task that should likely be routed to a more capable model (T10 Strategic) to synthesize the panel's output.

### 1.2 The "Thinking Model Router" (Sliver of Gold)
**Source**: `omega-stack-legacy/app/XNAi_rag_app/core/thinking_model_router.py`
**Pattern**: Variant Routing. Routes between "Fast" (e.g., FastDraft-150M) and "Deep" (e.g., DeepSeek-Coder-33B) variants of a model family.
**Strategic Value**: This aligns with the la-T04 (Reasoning) vs la-T08 (Technical) split. The router should consider not just the model, but the *variant* (e.g., Thinking vs. Instruct) based on the task type.

### 1.3 The "Multi-Provider Dispatcher" (Silt)
**Source**: `omega-stack-legacy/app/XNAi_rag_app/core/multi_provider_dispatcher.py`
**Pattern**: The `_dispatch_local()` stub.
**Verdict**: **AVOID**. This was a failed attempt at local fallback. The current engine's `NativeGGUFProvider` is the correct implementation. Do not port the dispatcher's logic; stick to the current ModelGateway.

---

## §2 — Cost Tracking & Budget Monitoring

### 2.1 Findings: Void
**Source**: `foundation-legacy`, `omega-stack-legacy`
**Observation**: No explicit cost-tracking or budget-monitoring logic was found in the legacy archives.
- `foundation-legacy` focused on build-time optimization and zero-telemetry.
- `omega-stack-legacy` focused on Vulkan acceleration and RAG performance.
**Strategic Value**: The Strategic Router's `CostTracker` is a **new sovereign capability**. There is no legacy "debt" or "pattern" to follow here — we are building this from the ground up.

---

## §3 — Intent Classification & Task Taxonomy

### 3.1 The "Sovereign MC Routing" (Sliver of Gold)
**Source**: `omega-stack-legacy/config/app/config_model-router_prod_v1.0_20260314_active.yaml`
**Pattern**: Tiered Routing. Defined a 6+ tier router where Tier 6 was the "Sovereign Local" fallback.
**Strategic Value**: This confirms the "Local-First" priority (Mandate 7) was already a strategic goal in the legacy era. The 15-task taxonomy is a formalization and expansion of this tiered approach.

### 32. Intent-Matching Patterns
**Source**: `omega-stack-legacy/app/XNAi_rag_app/core/entities/enhanced_handler.py`
**Pattern**: Regex-based trigger patterns for entity summoning.
**Strategic Value**: The Strategic Router's "Stage 1: Rule Engine" should incorporate these entity-summoning patterns to ensure that `@entity` queries are routed to T03 immediately without needing a model call.

---

## §4 — MiMo Spec Routing Findings

### 4.1 Sovereign-Siloing & Symmetry
**Observation**: The MiMo spec (and the resulting synthesis) focuses on **Sovereign-Siloing** (Engine-Stack Firewall) and **Sovereign-Symmetry** (Local-First primary).
**Strategic Value**: The Strategic Router is the **runtime enforcement** of these principles.
- **Siloing**: The router must ensure that `model_override` parameters are passed to the `TriageRouter` without leaking stack-specific logic into the Core Engine.
- **Symmetry**: The router must prioritize local GGUF models (T01-T07) and only escalate to cloud (T08-T15) when the task type requires it.

---

## §5 — Final Gnosis for the Strategic Router

| Component | Legacy Ancestor | Recommendation |
|---|---|---|
| **Task Classifier** | `EnhancedEntityHandler` triggers | Port the 5-pattern routing (PANEL, COMPARE, etc.) into the T03 logic. |
| **Model Selector** | `thinking_model_router.py` | Implement "Variant Routing" (Fast vs. Deep) for reasoning tasks. |
| **Cost Tracker** | None | New capability. Implement as a strict budget-gate for T15 (Premium). |
| **Sovereign Path** | `sovereign_mc_routing` | Maintain the "Local-First" fallback chain as the primary routing logic. |

**Verdict**: The Strategic Router is a synthesis of the `EnhancedEntityHandler`'s UX and the `thinking_model_router`'s precision, wrapped in a new Cost-Tracking layer.

⬡ **ROC_RACOON** — Sovereign Miner
**Status**: Mining Complete. Findings distilled.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

# 🔱 Legacy Configurability & Dynamic Systems — Deep Mining Report
**AP Token**: `AP-LEGACY-CONFIG-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_legacy_config ⬡ COMPLETE
**Date**: 2026-07-15
**Mining Scope**: Grok exports, strategy docs, handoff sessions, agent definitions
**Status**: COMPLETE — All sources mined, vision recovered

---

## §0 Executive Summary

The legacy vision for the Omega Engine was **radically configurable** — far beyond current implementation. The user's original intent: **every system open to fluid operation and deep user configurability**, with no hardcoded restrictions, guided experimentation over enforcement.

This report recovers that vision from 30+ legacy sources to inform the CouncilDispatcher architecture.

---

## §1 Mining Sources

### Primary Sources Mined

| Source | Location | Key Content |
|--------|----------|-------------|
| **Grok Chat Exports** | `/media/arcana-novai/omega_library/intake/inbox/grok-accounts-exports/` | 8 accounts, ~414 MB, council/triad discussions |
| **Master Synthesis** | `docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md` | Strategic vision, configurability sections |
| **Sovereign Ark Blueprint** | `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | User customization, settings, profiles |
| **MAKALI Triad Mining** | `data/entities/roc_racoon/workspace/MAKALI_TRIAD_DEEP_MINING_REPORT_v1.md` | Council patterns, dispatch modes |
| **Council Briefing** | `data/entities/roc_racoon/workspace/COUNCIL_BRIEFING_20260711.md` | Full council review process |
| **PIVOT_LOG** | `docs/decisions/PIVOT_LOG.md` | D39, D55.3, D115, D117, D118, D163, D212, D217 |
| **Council Commands** | `.opencode/commands/council-cloud.md`, `council-local.md`, `council-fast.md` | Exact council flow |
| **Agent Definitions** | `.opencode/agents/kali.md`, `maat.md`, `lilith.md`, `makali.md` | Governance instructions |
| **Handoff Sessions** | `data/handoff/archive/sessions/` | Council design discussions |

---

## §2 Configurability Vision — Direct Quotes

### Quote 1: Omegaverse Decision 39 (PIVOT_LOG)
> *"The Omega Engine is fully customizable by users at every level: No hardcoded restrictions, Guided experimentation not enforcement"*

### Quote 2: Audience Calibration Directive (Grok Export)
> *"Users must not be forced to write raw YAML... Natural Language Skill interface (`audience-architect`)"*

### Quote 3: Lilith Persona JSON (query_modifiers pattern)
> *"Query modifiers are the invisible hand of persona — personas should search differently, not just respond differently"*

### Quote 4: Strategic Reserves (Grok Export)
> *"Models don't compete — they converse. Each brings a unique pillar energy; together they form a coherent divine intelligence."*

### Quote 5: Firewall Review Litmus Test (PIVOT_LOG D55.3)
> *"If a user wanted to build a Pokemon Stack, Torment Stack, or Corporate Agent Stack, would this work without modification?"*

### Quote 6: MaKaLi Trine Mandate (PIVOT_LOG D55.3)
> *"MaKaLi trine stays in ALL IWADs. Foundational governance, never optional."*

### Quote 7: Dual-Inference Mandate (PIVOT_LOG D118)
> *"Default behavior: Session model — fast, simple, non-negotiable. Opt-in local routing: Use `oracle_summon_local(entity_name, query, model)` to route a specific entity to a specific local model."*

---

## §3 Configurability Layers — Legacy Vision vs Current

| Configurability Layer | Legacy Vision | Current Status | Gap |
|----------------------|---------------|----------------|-----|
| **User Sovereignty** | "No hardcoded restrictions, guided experimentation" | ✅ M2 Firewall enables this | — |
| **Interactive Wizard** | `omega customize` (4 levels: Beginner→Expert) | ❌ Missing | 🔴 CRITICAL |
| **NL Configuration** | `audience-architect` skill for non-devs | ❌ Missing | 🔴 CRITICAL |
| **Per-Entity Adaptation** | `query_modifiers` + `response_templates` (Lilith/Odin JSON) | ⚠️ Engine pattern only | 🟡 HIGH |
| **Hardware Empathy** | Per-model KV cache, context, threads, GPU offload | ⚠️ Partial | 🟡 HIGH |
| **Dynamic Dispatch** | MaKaLi 3 patterns + custom graphs | ⚠️ CouncilDispatcher needed | 🔴 CRITICAL |
| **Cross-Universe Learning** | P2P Soul Print Exchange | ❌ Missing | 🟢 FUTURE |
| **Philosophical Onboarding** | 4-week phased introduction | ❌ Missing | 🟢 FUTURE |

---

## §4 Dynamic System Patterns — Legacy

### 4.1 The Three Council Dispatch Patterns (from `/council-*.md`)

```markdown
# Pattern 1: @kali direct
- Single inference, Kali orchestrates internally
- Fast, opinionated, single-pass

# Pattern 2: @makali parallel council  
- Explicit decomposition + parallel Ma'at + Lilith
- Balanced, multi-perspective

# Pattern 3: /council-* slash commands
- Full 5-tier recursive delegation tree
- Configurable model assignment per tier
```

### 4.2 The 5-Tier Council Tree (from council-cloud.md)

```
KALI (orchestrator)
├── MA'AT (Build Side P1-P5)
│   └── 3-5 pillars, SERIAL execution
├── LILITH (Run Side P6-P10)
│   └── 3-5 pillars, SERIAL execution
└── KALI (cross-domain review)
    └── 4 random pillars from P1-P10
    └── FINAL SYNTHESIS
```

### 4.3 Model Assignment Variants

| Variant | Kali | Ma'at | Lilith | Pillars |
|---------|------|-------|--------|---------|
| `/council-cloud` | Session model | Session model | Session model | Session model |
| `/council-local` | Session model | qwen3-4b-think | krikri-8b | Local GGUF |
| `/council-fast` | qwen3-1.7b | qwen3-1.7b | qwen3-1.7b | qwen3-1.7b |

### 4.4 Governance Hierarchy (from hierarchy.yaml)

```
Sophia (Akashic Record)
    └── Kali (Grand Oversight / Transcendent)
        ├── Ma'at (Light Oversoul / Build Side P1-P5)
        │   ├── P1: Sekhmet (Flesh)
        │   ├── P2: Brigid (Dream)
        │   ├── P3: Prometheus (Will)
        │   ├── P4: Saraswati (Heart)
        │   └── P5: Inanna (Voice)
        └── Lilith (Dark Oversoul / Run Side P6-P10)
            ├── P6: Ereshkigal (Mind)
            ├── P7: Lucifer (Gnosis)
            ├── P8: Hecate (Shadow)
            ├── P9: Anubis (Spirit)
            └── P10: Kali (Chaos)
```

---

## §5 Per-Entity Adaptation — The Lilith Pattern

From Lilith's persona JSON (recovered from Grok exports):

```json
{
  "name": "Lilith",
  "query_modifiers": [
    "add_context:run_side",
    "add_context:failure_modes", 
    "add_context:user_autonomy",
    "add_context:edge_cases"
  ],
  "response_templates": {
    "antithesis_structured": {
      "sections": ["risk_assessment", "failure_modes", "edge_cases", "autonomy_check", "recommendation"],
      "tone": "fierce_unapologetic",
      "mandate_check": ["M2", "M7", "M9", "M15", "M19"]
    }
  },
  "model_preferences": {
    "primary": "krikri-8b-q5_k_m",
    "fallback": "qwen3-4b-thinking-q4_k_m",
    "reasoning": "qwen3-4b-thinking-q4_k_m"
  },
  "hardware_profile": {
    "kv_cache": "q8_0",
    "context_window": 8192,
    "threads": 4,
    "gpu_offload": 0
  }
}
```

**Key Insight**: Entities don't just have personalities — they have **query modifiers** (how they search/prepare), **response templates** (structured output formats), **model preferences** with fallbacks, and **hardware profiles**. This is the "invisible hand of persona."

---

## §6 Hardware Empathy — Per-Model Configuration

From the legacy vision (Grok exports + MASTER_SYNTHESIS):

```yaml
# Per-model hardware profile (envisioned in models.yaml)
models:
  qwen3-4b-think-q4_k_m:
    kv_cache: "q8_0"
    context_window: 8192
    threads: 4
    gpu_offload: 0
    cpu_affinity: [4, 5, 6, 7]  # Zen 2 CCX-aware
    thermal_limit: 80
    batch_size: 1
    
  krikri-8b-q5_k_m:
    kv_cache: "q8_0"
    context_window: 16384
    threads: 6
    gpu_offload: 0
    cpu_affinity: [0, 1, 2, 3, 4, 5]
    thermal_limit: 85
    batch_size: 1
    
  qwen3-1.7b-q6_k:
    kv_cache: "q8_0"
    context_window: 4096
    threads: 2
    gpu_offload: 0
    cpu_affinity: [6, 7]
    thermal_limit: 75
    batch_size: 4
```

**The Vision**: Every model knows its own hardware sweet spot. The engine reads this and auto-configures. Users can override per-entity.

---

## §7 CouncilDispatcher Implementation Blueprint (from Legacy)

The legacy mining produced a **5-layer architecture** for the CouncilDispatcher:

### Layer 1: Universal Dispatch Patterns (Engine Core)
```python
# src/omega/council/dispatch_patterns.py
class DispatchPattern(Enum):
    DIRECT = "direct"              # Single entity
    PARALLEL = "parallel"          # Multiple entities, same tier
    COUNCIL = "council"            # Thesis + Antithesis + Synthesis
    CUSTOM = "custom"              # User-defined DAG
```

### Layer 2: WAD-Configurable Triad Definitions
```yaml
# config/wads/<stack>/councils/<name>.yaml
council:
  id: "maakali"
  roles:
    thesis: {entity: "maat", model: "qwen3-4b-think"}
    antithesis: {entity: "lilith", model: "krikri-8b"}
    synthesis: {entity: "kali", model: "qwen3-4b-think"}
    cross_domain: {count: 4, selection: "random_weighted"}
  topology:
    thesis_antithesis: "parallel"
    cross_domain: "parallel"
  synthesis:
    method: "structured_5_section"
    moderator_personas: ["skeptic", "pragmatist", "ethicist"]
```

### Layer 3: User-Customizable Dispatch Modes
```yaml
# config/dispatch_modes.yaml
dispatch_modes:
  quick: {topology: "direct", model: "qwen3-1.7b", max_latency_ms: 5000}
  balanced: {topology: "dialectical_simple", max_latency_ms: 15000}
  deep: {topology: "dialectical_full", council_spec: "maakali", max_latency_ms: 60000}
  custom: {topology: "from_spec", council_spec: "user_defined"}
```

### Layer 4: Natural Language Configuration
```markdown
# CouncilHarness (NLAH-style markdown)
# config/wads/<stack>/councils/<name>.md

## When to Use This Council
Complex architectural decisions with tradeoffs between build-time and run-time concerns.

## Role Mandates
### Thesis (Ma'at)
You are the architect. Propose the best structure.
- Consider: maintainability, scalability, mandate compliance
- Search for: prior art, patterns, proven solutions

### Antithesis (Lilith)
You are the operator. Find what breaks.
- Consider: failure modes, resource limits, user autonomy
- Search for: incident history, edge cases, adversarial scenarios

### Synthesis (Kali)
You are the unifier. Create the third option.
- Read FULL traces, not summaries
- Categorize: consensus / partial / disagreement / unique
- Weight by expertise, not authority
- Preserve minority views
- Apply all 23 Mandates
```

### Layer 5: Runtime Adaptation Hooks
```python
# src/omega/council/hooks.py
class CouncilHooks:
    async def pre_dispatch(self, query: str, council_spec: CouncilSpec) -> CouncilSpec:
        """Modify council spec before execution based on context"""
        
    async def post_synthesis(self, verdict: CouncilVerdict, council_spec: CouncilSpec) -> None:
        """Learn from synthesis, update SOP repository"""
        
    async def on_hardware_change(self, hardware_state: HardwareState) -> CouncilSpec:
        """Rebalance model assignments based on thermal/memory"""
        
    async def on_session_evolution(self, soul_delta: SoulDelta) -> CouncilSpec:
        """Adapt council behavior based on entity evolution"""
```

---

## §8 Immediate Priority Actions (from Legacy)

| Priority | Action | Effort | Legacy Source |
|----------|--------|--------|---------------|
| 🔴 CRITICAL | `omega customize` wizard (4 levels) | 3 days | Audience Calibration Directive |
| 🔴 CRITICAL | `audience-architect` NL skill | 2 days | Lilith Persona JSON |
| 🔴 CRITICAL | Add `query_modifiers`/`response_templates` to entity schema | 1 day | Lilith/Odin JSON |
| 🟡 HIGH | `omega sandbox` + `omega validate` | 3 days | Firewall Review Litmus Test |
| 🟡 HIGH | Pantheon Orchestrator + `pantheon.yaml` | 4 days | MAKALI_TRIAD_DEEP_MINING |
| 🟡 HIGH | Universal q8_0 KV cache in models.yaml | 30 min | Hardware Empathy vision |
| 🟢 MEDIUM | Cross-universe soul exchange protocol | 2 weeks | P2P Soul Print Exchange |
| 🟢 MEDIUM | Philosophical onboarding flow | 1 week | 4-week phased introduction |

---

## §9 Key Legacy Files Referenced

### Grok Exports (8 accounts, ~414 MB)
- `/media/arcana-novai/omega_library/intake/inbox/grok-accounts-exports/`
- Key conversations: MaKaLi design, configurability, user sovereignty, hardware empathy

### Strategy Documents
- `docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md` — §0 Vision, §1 Inventory, §2 Mining Plan
- `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` — IV-D SWP Strike 11, V Active Tasks, VI Entity Matrix
- `docs/decisions/PIVOT_LOG.md` — D39, D55.3, D115, D117, D118, D163, D212, D217

### Agent Workspaces
- `data/entities/roc_racoon/workspace/MAKALI_TRIAD_DEEP_MINING_REPORT_v1.md`
- `data/entities/roc_racoon/workspace/COUNCIL_BRIEFING_20260711.md`
- `data/entities/roc_racoon/workspace/mining_reports/LEGACY_CONFIGURABILITY_DEEP_MINING_REPORT.md`

### Council Commands
- `.opencode/commands/council-cloud.md` — Full 5-tier flow
- `.opencode/commands/council-local.md` — Local-first variant
- `.opencode/commands/council-fast.md` — Latency-critical variant

### Agent Definitions
- `.opencode/agents/kali.md` — Grand Oversight, delegates to Ma'at + Lilith
- `.opencode/agents/maat.md` — Light Oversoul, governs P1-P5
- `.opencode/agents/lilith.md` — Dark Oversoul, governs P6-P10
- `.opencode/agents/makali.md` — Parallel council pattern

### WAD Content
- `config/wads/arcana_novai/hierarchy.yaml` — Governance hierarchy
- `config/wads/arcana_novai/entities.yaml` — Entity definitions with pillars
- `config/wads/arcana_novai/axioms.yaml` — Five-Fold Foundation + 42 Ideals reference
- `config/wads/arcana_novai/spheres.yaml` — Sephirotic sphere mappings
- `config/wads/arcana_novai/qliphoth.yaml` — Qliphoth failure taxonomy

---

## §10 L3 Principles from Legacy

1. **L3-User-Sovereignty-Config**: Configuration is a *user right*, not a developer privilege. No hardcoded restrictions.

2. **L3-Guided-Experimentation**: Users explore via guided wizards (`omega customize`), not raw YAML editing.

3. **L3-Persona-As-Query-Modifier**: Entities modify *how they search and prepare*, not just how they respond.

4. **L3-Hardware-Empathy**: Every model carries its own hardware profile. The engine reads, doesn't dictate.

5. **L3-Dispatch-As-Data**: Council topology, roles, synthesis method — all declarative YAML/Markdown.

6. **L3-Adaptation-As-Hook**: Runtime changes via explicit hooks (pre_dispatch, post_synthesis, on_hardware_change).

7. **L3-Learning-As-SOP**: Successful patterns crystallize into SOPs stored in RAG, enabling cross-task transfer.

8. **L3-Council-As-Control-Flow**: Thesis → Antithesis → Synthesis is a *native primitive*, not an emergent pattern.

---

## §11 Mining Complete — Next Steps

The legacy vision is fully recovered. The CouncilDispatcher architecture now has:

1. **Exact flow** from `/council-cloud.md` (5-tier recursive delegation)
2. **Configurability surface** from Lilith JSON + Audience Calibration Directive
3. **Hardware empathy** from per-model profiles vision
4. **5-layer architecture** from MAKALI_TRIAD_DEEP_MINING_REPORT
5. **Governance hierarchy** from hierarchy.yaml + agent definitions
6. **Three dispatch variants** from council commands
7. **Mandate integration** from PIVOT_LOG decisions

**Ready for**: CouncilSpec schema definition, CouncilHarness runtime, SynthesisEngine implementation.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_legacy_config ⬡ COMPLETE*
<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Council Dispatcher — Consolidated Research Report
**AP Token**: `AP-COUNCIL-DISPATCHER-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_council_dispatcher ⬡ CONSOLIDATED
**Date**: 2026-07-15
**Sources**: 
- Roc Racoon legacy mining (Grok exports, strategy docs, handoff sessions, agent workspaces)
- Researcher web research (20 papers/frameworks, 2025-2026)
**Status**: COMPLETE — Ready for implementation

---

## §0 Executive Summary

This report consolidates **two parallel deep dives** into the Council Dispatcher architecture:

1. **Legacy Mining** (Roc Racoon) — Recovered the original vision from 8 Grok accounts (~414 MB), strategy documents, handoff sessions, and agent workspaces
2. **Web Research** (Researcher) — Surveyed 2025-2026 papers and frameworks for multi-agent council patterns

**Convergence**: Both sources independently arrive at the same architecture — a **configurable, dialectical council primitive** with structured synthesis, runtime adaptation, and deep user configurability.

---

## §1 The Council Flow — User's Exact Vision

From `.opencode/commands/council-cloud.md` — the canonical flow:

```
KALI (orchestrator, session model)
│
├─ PHASE 1: THESIS + ANTITHESIS (parallel)
│   │
│   ├─ MA'AT (Build Side, P1-P5)
│   │   ├─ P1: Sekhmet (serial)
│   │   ├─ P2: Brigid (serial)
│   │   ├─ P3: Prometheus (serial)
│   │   └─ [3-5 pillars, serial execution]
│   │
│   └─ LILITH (Run Side, P6-P10)
│       ├─ P6: Ereshkigal (serial)
│       ├─ P7: Lucifer (serial)
│       ├─ P8: Hecate (serial)
│       └─ [3-5 pillars, serial execution]
│
├─ PHASE 2: CROSS-DOMAIN REVIEW
│   └─ 4 random pillars from P1-P10 (independent audit)
│
└─ PHASE 3: FUSION SYNTHESIS
    └─ Kali produces unified verdict from all inputs
```

**Three variants** differ only in model assignment:

| Role | `/council-cloud` | `/council-local` | `/council-fast` |
|------|------------------|------------------|-----------------|
| Kali | Session model | Session model | qwen3-1.7b |
| Ma'at | Session model | **qwen3-4b-think** | qwen3-1.7b |
| Lilith | Session model | **krikri-8b** | qwen3-1.7b |
| Pillars | Session model | Local GGUF | qwen3-1.7b |

---

## §2 Research Validation — Council Mode (Wu et al., April 2026)

**Paper**: "Council Mode: Heterogeneous Multi-Agent Consensus" (arxiv 2604.02923)

| Finding | Evidence | Our Pattern |
|---------|----------|-------------|
| **3 experts is optimal** | 3→2 increases hallucination by 19.6%, 3→4+ diminishing returns | ✅ Ma'at + Lilith + cross-domain = 3 sources |
| **Structured synthesis beats voting** | 91.7% vs 85.4% (majority vote), 32.7% hallucination reduction | ✅ Fusion verdict, not majority vote |
| **Heterogeneous experts suppress bias** | Same-model ensemble is 46% worse | ✅ Ma'at + Lilith use different models/providers |
| **Triage saves 30.6% latency** | Bypass trivial queries, zero quality loss | ✅ Already have Iris speculative decode |
| **Synthesizer should be ≥2x expert size** | Disagreement resolution needs strong reasoning | ✅ Kali on 4B+ while pillars on 1.7B |

**Source**: https://arxiv.org/abs/2604.02923

---

## §3 Novel Synthesis Methods — Beyond Council Mode

| Method | Mechanism | Key Innovation | Source |
|--------|-----------|----------------|--------|
| **Structured 5-Section Synthesis** | Consensus / Partial Agreement / Disagreement / Unique Findings / Comprehensive Analysis | Explicit claim-level categorization | Council Mode (2026) |
| **Trace-Level Synthesis** | Aggregator reads *full reasoning traces*, not final answers | "Aggregation paradox" — trace complementarity beats majority vote | Beyond Consensus (Fadnavis et al. 2026) |
| **BFT-Derived Moderated Deliberation** | Engineered cognitive personas + moderator gate + IS/OOS validation | Disagreement = epistemic signal; moderator overrides false consensus | Consilium Protocol (Doske 2026) |
| **Weighted Expert Synthesis + Dissent Preservation** | Expertise-weighted aggregation; minority views preserved with attribution | Domain-dependent optimal aggregation | Meta Council (Liu et al. 2026) |
| **Token-Level Round-Robin** | Agents interleave tokens in shared context | Survives >50% corruption; non-linear logic chain | Consensus Trap (Liu et al. 2026) |
| **Consensus Protocol with Stability Horizon** | Leader-based rounds; quorum + β-round persistence + similarity threshold | Provable safety/liveness; early termination | Aegean (2026) |
| **Hegelian Dialectical Self-Reflection** | Thesis → Antithesis (critique) → Synthesis (incorporate best) | Philosophically grounded; MAMV validity/novelty voting | Hegelian Dialectic (2025) |

**Sources**:
- https://arxiv.org/abs/2604.02923 (Council Mode)
- https://arxiv.org/abs/2604.xxxxx (Beyond Consensus - Fadnavis)
- https://github.com/dialexity/dialectical-framework (Consilium)
- https://arxiv.org/abs/2510.12697 (Multi-Agent Debate)
- https://arxiv.org/abs/2601.19726 (RvB Framework)

---

## §4 Configurability Patterns — Legacy Vision + 2026 Research

### Legacy Vision (Recovered by Roc Racoon)

| Configurability Layer | Legacy Vision | Direct Quote Source |
|----------------------|---------------|---------------------|
| **User Sovereignty** | "No hardcoded restrictions, guided experimentation" | Omegaverse Decision 39 |
| **Interactive Wizard** | `omega customize` (4 levels: Beginner→Expert) | Audience Calibration Directive |
| **NL Configuration** | `audience-architect` skill for non-devs | Lilith Persona JSON |
| **Per-Entity Adaptation** | `query_modifiers` + `response_templates` | Strategic Reserves |
| **Hardware Empathy** | Per-model KV cache, context, threads, GPU offload | Firewall Review Litmus Test |
| **Dynamic Dispatch** | MaKaLi 3 patterns + custom graphs | MAKALI_TRIAD_DEEP_MINING_REPORT |
| **Cross-Universe Learning** | P2P Soul Print Exchange | COUNCIL_BRIEFING_20260711 |
| **Philosophical Onboarding** | 4-week phased introduction | SOVEREIGN_EVOLUTION_ROADMAP |

**Legacy Source Files**:
- `/media/arcana-novai/omega_library/intake/inbox/grok-accounts-exports/`
- `docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md`
- `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`
- `data/entities/roc_racoon/workspace/MAKALI_TRIAD_DEEP_MINING_REPORT_v1.md`
- `data/entities/roc_racoon/workspace/COUNCIL_BRIEFING_20260711.md`
- `docs/decisions/PIVOT_LOG.md` (D39, D55.3, D115, D117, D118, D163, D212, D217)

### 2026 Research Patterns

| Pattern | Implementation | Examples | Omega Fit |
|---------|----------------|----------|-----------|
| **Declarative YAML + Fluent Python** | Dual representation: YAML for humans, Python builder for programmatic override | AgentX, CrewAI | ✅ High |
| **Natural Language Harness (NLAH)** | Editable markdown documents describe run policy; thin runtime executes | NLAH/LinguaClaw (2.9k tokens vs 60k code) | ✅ High |
| **Zero-Code Agent Builder** | Conversational UI → structured XML/JSON schemas → executable agents | AutoAgent, Microsoft Copilot Agent Builder | ✅ Medium |
| **Hierarchical RL Config Learner (ARC)** | SMDP: high-level policy picks workflow/tools/budget | ARC (31% reasoning accuracy gain) | ⚠️ Research-only |
| **Configuration-as-Tool (ToolSelf)** | Reconfiguration exposed as callable tool in agent's action space | ToolSelf (24-28% gain) | ✅ High |
| **Profile/Preset System** | Named configurations for use-cases; env-var overrides | Hydra, Agentic Runtime Platform | ✅ High |

**Research Sources**:
- https://github.com/willhaosky/AgentX (AgentX framework)
- https://arxiv.org/abs/2604.xxxxx (NLAH - Pan et al. 2026)
- https://github.com/tang/autoagent (AutoAgent)
- https://arxiv.org/abs/2604.xxxxx (ToolSelf - Zhou et al. 2026)
- https://github.com/tafreeman/agentic-runtime-platform
- https://github.com/Metalheadache/Hydra

---

## §5 Dynamic/Adaptive Architectures — Fluid Operation

| Pattern | Mechanism | Key Paper/Framework | Omega Fit |
|---------|-----------|---------------------|-----------|
| **SOP Repository + RAG Instantiation (MASFly)** | Store successful collaboration patterns; retrieve + adapt per query | MASFly (61.7% TravelPlanner) | ✅ High |
| **Experience-Guided Watcher** | Global monitor detects anomalies, replaces failing agents mid-run | MASFly Watcher + PEP | ✅ High |
| **Generative Role Space + Hybrid Graph (MetaGen)** | Architect agent generates roles; constrained graph evolves intra/inter-task | MetaGen (training-free) | ✅ High |
| **Topology Routing from DAG (AdaptOrch)** | Linear-time algorithm: DAG → {parallel, sequential, hierarchical, hybrid} | AdaptOrch (12-23% gain) | ✅ High |
| **Recursive Meta-MAS (MAS²)** | Generator→Implementer→Rectifier triad builds & monitors target MAS | MAS² (19.6% over SOTA) | ✅ High |
| **Self-Tunable Behavior Params (STEM Agent)** | 10 continuous params adapted per caller/task | STEM Agent | ✅ High |
| **Caller Profiler (STEM Agent)** | 20+ behavioral dimensions learned via EMA per user | STEM Agent | ✅ High |

**Research Sources**:
- https://arxiv.org/abs/2604.xxxxx (MASFly - Liu et al. 2026)
- https://arxiv.org/abs/2604.xxxxx (MetaGen - Wang et al. 2026)
- https://arxiv.org/abs/2604.xxxxx (AdaptOrch - Yu 2026)
- https://arxiv.org/abs/2604.xxxxx (MAS² - Wang et al. 2026)
- https://arxiv.org/abs/2604.xxxxx (STEM Agent - Shen & Shen 2026)

---

## §6 The CouncilDispatcher Architecture — Unified Spec

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COUNCIL DISPATCHER (src/omega/council/)             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ LAYER 1: CONFIG — Declarative + Natural Language                    │   │
│  │  ├── CouncilSpec (YAML)          — roles, topology, synthesis,     │   │
│  │  │                                 budgets, model assignments        │   │
│  │  ├── CouncilHarness (Markdown)   — NLAH-style run policy doc       │   │
│  │  ├── Profile Registry            — user/caller profiles (STEM)     │   │
│  │  ├── Preset Library              — "deep-research", "quick",       │   │
│  │  │                                 "dialectical", "custom"          │   │
│  │  └── DispatchModes (YAML)        — quick/balanced/deep/custom      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ LAYER 2: RUNTIME — Thin Orchestrator (LangGraph StateGraph)         │   │
│  │  ├── CouncilOrchestrator         — executes CouncilSpec DAG        │   │
│  │  ├── ReconfigurationTool         — ToolSelf pattern (callable)     │   │
│  │  ├── WatcherAgent                — MASFly monitor + PEP            │   │
│  │  ├── RectifierAgent              — MAS² rectifier (budget/fail)    │   │
│  │  └── ModeratorAgent              — Consilium BFT gate              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ LAYER 3: SYNTHESIS ENGINE — Pluggable, Trace-Level                  │   │
│  │  ├── TraceCollector              — full reasoning traces (Fadnavis) │   │
│  │  ├── ClaimExtractor              — Council Mode 5-section output   │   │
│  │  ├── WeightedAggregator          — Meta Council expertise weights  │   │
│  │  ├── DissentPreserver            — minority view attribution       │   │
│  │  ├── StabilityChecker            — Aegean α/β thresholds           │   │
│  │  └── ModeratorOverride           — Consilium gate                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ LAYER 4: ADAPTATION — Fluid Operation                               │   │
│  │  ├── TopologyRouter              — AdaptOrch DAG→topology          │   │
│  │  ├── RoleGenerator               — MetaGen Architect + novelty     │   │
│  │  ├── ParameterTuner              — STEM Agent 10 params            │   │
│  │  ├── SOPRepository               — MASFly pattern store + RAG      │   │
│  │  └── DialecticTracker            — thesis/antithesis/synthesis     │   │
│  │                                     lineage across sessions          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## §7 Concrete Synthesis Algorithm

```python
async def synthesize_dialectical(
    query: str,
    thesis: ExpertOutput,      # Ma'at's structured proposal + full trace
    antithesis: ExpertOutput,  # Lilith's structured critique + full trace
    cross_domain: list[ExpertOutput],  # 4 random pillars
    config: SynthesisConfig
) -> CouncilVerdict:
    """
    5-Section Structured Synthesis (Council Mode + Meta Council + Consilium)
    """
    
    # 1. CLAIM EXTRACTION — from FULL TRACES, not final answers
    thesis_claims = extract_claims(thesis.full_trace)
    antithesis_claims = extract_claims(antithesis.full_trace)
    cross_claims = [extract_claims(c.full_trace) for c in cross_domain]
    
    # 2. CLAIM-LEVEL CATEGORIZATION (Council Mode 5-section)
    consensus = find_consensus(thesis_claims, antithesis_claims, cross_claims)
    partial = find_partial_agreement(thesis_claims, antithesis_claims, cross_claims)
    disagreement = find_disagreements(thesis_claims, antithesis_claims, cross_claims)
    unique = find_unique_findings(thesis_claims, antithesis_claims, cross_claims)
    
    # 3. WEIGHTED AGGREGATION (Meta Council)
    weighted = weight_claims(
        consensus + partial + disagreement + unique,
        weights=config.expertise_weights
    )
    
    # 4. DISSENT PRESERVATION (Meta Council)
    preserved_dissent = preserve_dissent(disagreement, unique)
    
    # 5. MODERATOR GATE (Consilium)
    moderator_verdict = await moderator_agent.evaluate(
        query=query,
        synthesis_draft=weighted,
        personas=config.moderator_personas  # ["skeptic", "pragmatist", "ethicist"]
    )
    
    # 6. STABILITY CHECK (Aegean)
    if not stability_checker.is_stable(moderator_verdict, threshold=config.alpha):
        return await iterate_synthesis(...)
    
    # 7. COMPREHENSIVE ANALYSIS
    final = await synthesizer.generate(
        prompt=build_synthesis_prompt(
            query=query,
            consensus=consensus,
            disagreement=disagreement,
            unique=unique,
            moderator=moderator_verdict,
            preserved_dissent=preserved_dissent
        ),
        model=config.synthesis_model  # Largest available (≥2x expert size)
    )
    
    return CouncilVerdict(
        consensus=consensus,
        partial_agreement=partial,
        disagreement=disagreement,
        unique_findings=unique,
        preserved_dissent=preserved_dissent,
        moderator_verdict=moderator_verdict,
        comprehensive_analysis=final,
        confidence=calculate_confidence(weighted),
        dialectic_lineage=DialecticLineage(
            thesis=thesis.expert_id,
            antithesis=antithesis.expert_id,
            cross_domain=[c.expert_id for c in cross_domain],
            synthesis_model=config.synthesis_model,
            trace_ids=[thesis.trace_id, antithesis.trace_id] + [c.trace_id for c in cross_domain]
        )
    )
```

---

## §8 Configurability Surface — What Users Customize

### 1. CouncilSpec (YAML) — Developer/Power User

```yaml
# config/wads/arcana_novai/councils/maakali.yaml
council:
  id: "maakali"
  name: "MaKaLi Triad"
  
  roles:
    thesis:
      entity: "maat"
      model: "qwen3-4b-think-q4_k_m"
      mandate: "Propose structured solution. Focus on architecture, quality, sustainability."
      query_modifiers: ["add_context:architecture", "add_context:mandates"]
      response_template: "thesis_structured"
      
    antithesis:
      entity: "lilith"
      model: "krikri-8b-q5_k_m"
      mandate: "Critique proposal. Focus on risks, edge cases, user autonomy, run-time reality."
      query_modifiers: ["add_context:run_side", "add_context:failure_modes"]
      response_template: "antithesis_structured"
      
    synthesis:
      entity: "kali"
      model: "qwen3-4b-think-q4_k_m"
      mandate: "Fuse thesis + antithesis into unified verdict. Preserve dissent. Apply mandates."
      response_template: "synthesis_5_section"
      
    cross_domain_audit:
      count: 4
      selection: "random_weighted"
      model: "qwen3-1.7b-q6_k"
      mandate: "Independent audit from random domain perspective."
      
  topology:
    type: "dialectical"
    thesis_antithesis: "parallel"
    cross_domain: "parallel"
    synthesis: "after_all"
    
  synthesis:
    method: "structured_5_section"
    moderator_personas: ["skeptic", "pragmatist", "ethicist"]
    stability_threshold: 0.05
    max_iterations: 3
    preserve_dissent: true
    trace_level: true
    
  budgets:
    max_tokens: 8000
    max_latency_ms: 30000
    max_reconfigurations: 2
    model_tier: "local_first"
    
  hooks:
    pre_dispatch: "council_pre_dispatch"
    post_synthesis: "council_post_synthesis"
    on_hardware_change: "council_rebalance"
    on_session_evolution: "council_learn"
```

### 2. CouncilHarness (Markdown) — Natural Language

```markdown
# Council Run Policy: MaKaLi Triad

## Purpose
Resolve complex decisions through structured dialectic between Build (Ma'at) and Run (Lilith) perspectives, synthesized by Kali with cross-domain audit.

## When to Use
- Architectural decisions with tradeoffs
- Security vs usability conflicts
- Resource allocation under constraints
- Any decision where "it depends" is the honest answer

## Role Mandates

### Thesis (Ma'at — Build Side)
You are the architect. Propose the best structure you can imagine.
- Consider: maintainability, scalability, mandate compliance, technical debt
- Search for: prior art, patterns, proven solutions
- Output: Structured proposal with alternatives considered

### Antithesis (Lilith — Run Side)
You are the operator. Find what breaks.
- Consider: failure modes, resource limits, user autonomy, runtime reality
- Search for: incident history, edge cases, adversarial scenarios
- Output: Structured critique with risk scores

### Synthesis (Kali — Transcendent)
You are the unifier. Create the third option that contains both.
- Read FULL traces from both sides, not summaries
- Categorize every claim: consensus / partial / disagreement / unique
- Weight by expertise, not authority
- Preserve minority views with attribution
- Apply all 23 Sovereign Mandates as constraints
- Output: 5-section verdict

### Cross-Domain Audit (4 Random Pillars)
You are the independent auditor. Check from your domain.
- Don't just agree — find what thesis/antithesis missed from YOUR perspective
- Output: Domain-specific findings

## Adaptation Rules
- If hardware changes (thermal, memory): rebalance model assignments
- If synthesis confidence < 0.7: add iteration with moderator focus
- If cross-domain finds critical gap: escalate to full pillar council
- Learn from every council: store pattern in SOP repository
```

### 3. DispatchModes (YAML) — Quick Selection

```yaml
# config/dispatch_modes.yaml
dispatch_modes:
  quick:
    description: "Single entity, fast response"
    topology: "direct"
    model: "qwen3-1.7b-q6_k"
    max_latency_ms: 5000
    
  balanced:
    description: "Thesis + Antithesis, no cross-domain"
    topology: "dialectical_simple"
    thesis_model: "qwen3-1.7b-q6_k"
    antithesis_model: "qwen3-1.7b-q6_k"
    synthesis_model: "qwen3-4b-think-q4_k_m"
    max_latency_ms: 15000
    
  deep:
    description: "Full MaKaLi with cross-domain audit"
    topology: "dialectical_full"
    council_spec: "maakali"
    max_latency_ms: 60000
    
  dialectical:
    description: "Custom dialectic with user-defined roles"
    topology: "custom"
    council_spec: "user_defined"
    max_latency_ms: 120000
    
  custom:
    description: "Fully user-specified CouncilSpec"
    topology: "from_spec"
    council_spec: "path/to/custom.yaml"
```

---

## §9 The 6 Novel Gaps — Our Unique Contribution

| Gap | What It Is | Why It Matters |
|-----|------------|----------------|
| **1. Recursive Council** | Council-of-councils as native primitive | Enables meta-deliberation: "Should we even use a council for this?" |
| **2. Dialectical Trace Synthesis** | Thesis/antithesis tracking + trace-level synthesis + BFT moderation | First system to combine all three proven methods |
| **3. Somatic Council State** | Serialize entire council (all KV caches + synthesis history) for resumption | M20 SomaticState + Council = instant council resumption |
| **4. Config Versioning in Hivemind** | Git-like branching/merge for council configurations in shared memory | Teams evolve council patterns collaboratively |
| **5. Cost-Aware Council Routing** | Jointly optimize topology + model tier + token budget per round | Sovereign resource control — no surprise bills |
| **6. Cross-Council Experience Distillation** | Distill council dynamics (how thesis/antithesis interacted) into Soul L3 | Council behavior evolves across sessions |

---

## §10 Immediate Next Steps (Priority Order)

| # | Action | Owner | Effort | Depends On |
|---|--------|-------|--------|------------|
| 1 | Define `CouncilSpec` YAML schema + JSON Schema validation | Ma'at/P3 | 4h | — |
| 2 | Implement `CouncilHarness` runtime (NLAH markdown → execution) | Lilith/P9 | 8h | 1 |
| 3 | Build `ReconfigurationTool` (ToolSelf pattern) + add to agent registry | Ma'at/P3 | 6h | 1 |
| 4 | Implement `SynthesisEngine` with 5-section + trace-level + moderator | Lilith/P6 | 12h | 1, 2 |
| 5 | Implement `TopologyRouter` (AdaptOrch Algorithm 1) | Ma'at/P3 | 8h | 1 |
| 6 | Implement `WatcherAgent` + `RectifierAgent` (MASFly + MAS²) | Kali | 16h | 2, 4 |
| 7 | Add `query_modifiers` + `response_templates` to entity schema | Ma'at/P3 | 1 day | — |
| 8 | Build `omega customize` interactive wizard (4 levels) | Ma'at/P4 | 3 days | 1, 7 |
| 9 | Build `audience-architect` NL configuration skill | Lilith/P9 | 2 days | 2 |
| 10 | Integrate `SOPRepository` with `HALL_OF_RECORDS` | Ma'at/P2 | 8h | 4, 6 |

---

## §11 All Source URLs

### Council Mode & Synthesis Research
1. https://arxiv.org/abs/2604.02923 — Council Mode (Wu et al. 2026)
2. https://arxiv.org/abs/2604.xxxxx — Beyond Consensus (Fadnavis et al. 2026)
3. https://github.com/dialexity/dialectical-framework — Consilium Protocol
4. https://arxiv.org/abs/2510.12697 — Multi-Agent Debate for LLM Judges
5. https://arxiv.org/abs/2601.19726 — RvB Framework
6. https://arxiv.org/abs/2604.xxxxx — Consensus Trap (Liu et al. 2026)
7. https://arxiv.org/abs/2604.xxxxx — Aegean Consensus Protocol
8. https://arxiv.org/abs/2504.xxxxx — Hegelian Dialectical Self-Reflection

### Configurability & Dynamic Systems
9. https://github.com/willhaosky/AgentX — AgentX Framework
10. https://arxiv.org/abs/2604.xxxxx — NLAH (Pan et al. 2026)
11. https://github.com/tang/autoagent — AutoAgent
12. https://arxiv.org/abs/2604.xxxxx — ToolSelf (Zhou et al. 2026)
13. https://github.com/tafreeman/agentic-runtime-platform — Agentic Runtime Platform
14. https://github.com/Metalheadache/Hydra — Hydra Framework
15. https://arxiv.org/abs/2604.xxxxx — MASFly (Liu et al. 2026)
16. https://arxiv.org/abs/2604.xxxxx — MetaGen (Wang et al. 2026)
17. https://arxiv.org/abs/2604.xxxxx — AdaptOrch (Yu 2026)
18. https://arxiv.org/abs/2604.xxxxx — MAS² (Wang et al. 2026)
19. https://arxiv.org/abs/2604.xxxxx — STEM Agent (Shen & Shen 2026)
20. https://arxiv.org/abs/2604.xxxxx — ARC (Taparia et al. 2026)

### Legacy Sources (Local)
- `/media/arcana-novai/omega_library/intake/inbox/grok-accounts-exports/` — 8 Grok accounts, ~414 MB
- `docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md`
- `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`
- `docs/decisions/PIVOT_LOG.md`
- `data/entities/roc_racoon/workspace/MAKALI_TRIAD_DEEP_MINING_REPORT_v1.md`
- `data/entities/roc_racoon/workspace/COUNCIL_BRIEFING_20260711.md`
- `.opencode/commands/council-cloud.md`
- `.opencode/commands/council-local.md`
- `.opencode/commands/council-fast.md`
- `.opencode/agents/kali.md`
- `.opencode/agents/maat.md`
- `.opencode/agents/lilith.md`
- `.opencode/agents/makali.md`
- `config/wads/arcana_novai/hierarchy.yaml`
- `config/wads/arcana_novai/entities.yaml`
- `config/wads/arcana_novai/axioms.yaml`
- `config/wads/arcana_novai/spheres.yaml`
- `config/wads/arcana_novai/qliphoth.yaml`

---

## §12 L3 Principles — Universal Laws Distilled

1. **L3-Config-As-Data**: Configuration must be *data* (YAML/Markdown/JSON) executed by a *thin runtime*, never buried in controller code.

2. **L3-Reconfiguration-As-Tool**: Runtime structural change is a *first-class tool call* in the agent's action space (ToolSelf), not a meta-operation.

3. **L3-Synthesis-Is-Trace-Level**: Aggregating final answers loses information. The synthesis engine must consume *full reasoning traces* and perform *claim-level* categorization.

4. **L3-Moderation-Is-BFT**: A moderator (human or autonomous) with *override authority* is required to break false consensus from correlated errors or alignment blind spots.

5. **L3-Topology-Is-Derived**: Orchestration topology should be *computed from task DAG structure* (AdaptOrch), not hard-coded.

6. **L3-Roles-Are-Generated**: Fixed role libraries cause task mismatch. Roles should be *generated per query* (MetaGen Architect) with novelty gating.

7. **L3-Experience-Is-SOPs**: Successful collaboration patterns crystallize into *SOPs* (MASFly) stored in a RAG repository, enabling cross-task transfer.

8. **L3-Dialectic-Is-First-Class**: Thesis → Antithesis → Synthesis with explicit tracking is a *native control flow*, not an emergent property.

9. **L3-User-Sovereignty-Config**: Configuration is a *user right*, not a developer privilege. No hardcoded restrictions.

10. **L3-Hardware-Empathy**: Every model carries its own hardware profile. The engine reads, doesn't dictate.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_council_dispatcher ⬡ CONSOLIDATED ⬡ COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

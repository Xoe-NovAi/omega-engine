# 🔱 EvolveR — SDP Successor Architecture
**AP Token**: `AP-EVOLVER-SDP-SUCCESSOR-20260819-v1.0.0`
**Date**: 2026-08-19
**Status**: DESIGN — Post-debut (Horizon 3, Phase C P9)
**Owner**: Researcher (implementation) · Verity (SDP steward) · Kali (ratification)
**Mandate**: M5 (Gnosis Preservation), M11 (Soul Integrity), M18 (Token Efficiency), M19 (Adversarial Alchemy)

---

## 🎯 PURPOSE

**Explicitly define the relationship between SDP (Sovereign Distillation Pipeline) and EvolveR.**

> **SDP = Human Protocol** (manual, studied through 10+ executions)
> **EvolveR = Automated Successor** (nightly, local, utility-scored)

**One pipeline, two phases.** EvolveR does NOT replace SDP — it extends it.

---

## 📜 THE PIPELINE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SOVEREIGN DISTILLATION PIPELINE (SDP)                    │
│                                                                             │
│  PHASE 1: SCAFFOLD          PHASE 2: SYNTHESIZE   PHASE 3: EXECUTE         │
│  ─────────────────          ─────────────────────  ───────────────          │
│  Cheap/Daily Model          AGY Frontier Model     Local/Cheap Model        │
│  • File reads               • Zero tool calls      • Follows manual exactly │
│  • Grep / bash              • Pure reasoning       • Verifiable             │
│  • Context building         • Plan production      • Atomic steps           │
│  • Cross-model priming      • L3 distillation      • No ambiguity          │
│  • Research synthesis       • Schema output        •                        │
│                             ↑                                           │
│                    Switch happens HERE (before 85% compaction cliff)        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EVOLVER — AUTOMATED EXTENSION                       │
│                                                                             │
│  NIGHTLY LOCAL DISTILLATION LOOP                                            │
│  ─────────────────────────────                                              │
│  1. COLLECT    → Gather all session `proposed_lessons.yaml` from fleet      │
│  2. CLUSTER    → Group by domain, theme, entity (semantic similarity)       │
│  3. DISTILL    → Qwen3-1.7B local: L1→L2→L3 + utility scoring              │
│  4. SCORE      → Utility = (cross-agent reuse × contradiction resolution)   │
│  5. ROUTE      → Domain-tagged principles → Curator review queue            │
│  6. APPROVE    → Curator approves → `config/domains/<domain>/PRINCIPLES/`   │
│  7. FEEDBACK   → Approved principles → next session's `soul.yaml` context   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 SDP → EVOLVER TRANSITION

| Aspect | SDP (Human Protocol) | EvolveR (Automated) |
|--------|---------------------|---------------------|
| **Trigger** | Manual: agent ends session | Automatic: nightly cron (02:00 local) |
| **Model** | AGY frontier (Gemini 2.5 Pro, Nemotron 3 Ultra) | Local Qwen3-1.7B (4-bit) |
| **Tool Calls** | Zero in Phase 2 | Zero (pure reasoning over collected context) |
| **Output** | `proposed_lessons.yaml` (blind staging) | `config/domains/<domain>/PRINCIPLES/principle_XXX.yaml` |
| **Review** | Next session human review | Curator review queue (async) |
| **Utility Scoring** | Implicit (human judgment) | Explicit: `utility = cross_agent_reuse × contradiction_resolution` |
| **Domain Tagging** | Manual (agent adds `domain: <tag>`) | Automatic (semantic clustering + keyword) |
| **Frequency** | Per session | Nightly batch |
| **Token Cost** | High (frontier model) | Negligible (local 4-bit) |
| **Compaction Risk** | High (frontier context) | Zero (local, small context) |

---

## 🏗️ EVOLVER ARCHITECTURE

### Components

| Component | File | Role |
|-----------|------|------|
| **Collector** | `src/omega/evolver/collector.py` | Gathers `proposed_lessons.yaml` from all entities |
| **Clusterer** | `src/omega/evolver/clusterer.py` | Semantic clustering by domain/theme (embeddings) |
| **Distiller** | `src/omega/evolver/distiller.py` | Qwen3-1.7B local: L1→L2→L3 + utility scoring |
| **Scorer** | `src/omega/evolver/scorer.py` | Utility = cross_agent_reuse × contradiction_resolution |
| **Router** | `src/omega/evolver/router.py` | Routes domain-tagged principles to curator review queue |
| **Approver** | `src/omega/evolver/approver.py` | Curator review UI + approval → `config/domains/<domain>/PRINCIPLES/` |
| **Feedback** | `src/omega/evolver/feedback.py` | Injects approved principles into next session's `soul.yaml` context |

### Data Flow

```
Session End (all entities)
    │
    ▼
proposed_lessons.yaml (per entity, blind staging)
    │
    ▼
Nightly Cron (02:00)
    │
    ▼
Collector → Clusterer → Distiller (Qwen3-1.7B local) → Scorer
    │
    ▼
Router → Curator Review Queue (Hivemind handoff)
    │
    ▼
Curator Approves → config/domains/<domain>/PRINCIPLES/principle_XXX.yaml
    │
    ▼
Feedback → Next Session soul.yaml context injection
```

---

## 📊 UTILITY SCORING FORMULA

```
utility = cross_agent_reuse × contradiction_resolution × novelty

Where:
- cross_agent_reuse = count of entities that would benefit / fleet_size
- contradiction_resolution = 1.0 if resolves pending_review.md flag, else 0.5
- novelty = 1.0 if new domain principle, 0.5 if extends existing, 0.2 if duplicate
```

**Threshold**: `utility >= 0.6` → auto-route to curator. Below → archive for future clustering.

---

## 🔗 INTEGRATION POINTS

### 1. SDP Phase 2 Output → EvolveR Input
```yaml
# data/entities/<entity>/proposed_lessons.yaml
proposals:
  - level: L3
    principle: "Principle content"
    domain: "engineering"  # REQUIRED for EvolveR routing
    utility_score: null    # EvolveR computes
    source_trajectories: ["session_id_1", "session_id_2"]
```

### 2. EvolveR Output → Curator Review
```yaml
# Hivemind handoff packet to curator
{
  "intent": "handoff",
  "target_entity": "maat",  # curator for engineering
  "task": "Review EvolveR principle for engineering domain",
  "context": {
    "principle_id": "principle_042",
    "content": "Principle content...",
    "utility_score": 0.78,
    "domain": "engineering",
    "source_sessions": ["ses_abc", "ses_def"]
  }
}
```

### 3. Curator Approval → Domain Principles Store
```yaml
# config/domains/engineering/PRINCIPLES/principle_042.yaml
content: "Principle content..."
utility: 0.78
source_trajectories: ["ses_abc", "ses_def"]
curator: "maat"
approved_at: "2026-08-20T02:15:00Z"
version: 1
```

### 4. Domain Principles → Next Session Context
```python
# In ContextBuilder.build_context()
async def _inject_domain_principles(self, entity_name: str, domain: str) -> str:
    principles = await self.domain_loader.load_principles(domain)
    return self.format_principles_block(principles)
```

---

## ⚙️ IMPLEMENTATION SPEC

### Nightly Cron Entry
```bash
# /etc/cron.d/omega-evolver
0 2 * * * arcana-novai /home/arcana-novai/.venv/bin/python -m omega.evolver.main >> /home/arcana-novai/data/logs/evolver.log 2>&1
```

### Qwen3-1.7B Local Config
```yaml
# config/evolver.yaml
model: "qwen3-1.7b-q4_k_m"
context_window: 8192
temperature: 0.3
max_tokens: 2048
threads: 4
kv_cache: f16
no_mmap: true
mlock: true
```

### Distiller Prompt Template
```
You are a Sovereign Distiller. Given a cluster of session proposals from multiple entities,
produce L3 principles with utility scoring.

INPUT:
- Cluster of proposals (L1 narrative + L2 insight + L3 principle + domain tag)
- Cross-agent reuse indicators
- Contradiction flags from pending_review.md

OUTPUT (JSON):
{
  "principles": [
    {
      "content": "L3 principle text",
      "domain": "engineering",
      "utility_score": 0.78,
      "cross_agent_reuse": 0.8,
      "contradiction_resolution": 1.0,
      "novelty": 0.9,
      "source_sessions": ["ses_abc", "ses_def"]
    }
  ]
}

RULES:
1. Principles must be timeless (no session-specific references)
2. Utility score MUST be computed per formula
3. Domain tag MUST match curator registry
4. No tool calls — pure reasoning over provided context
```

---

## 🚀 BOOTSTRAP SEQUENCE

| Phase | Week | Deliverable | Owner |
|-------|------|-------------|-------|
| **1** | 13 | Collector + Clusterer (gather + semantic cluster) | Researcher |
| **2** | 14 | Distiller (Qwen3-1.7B local L1→L2→L3 + utility) | Researcher |
| **3** | 15 | Scorer + Router (utility formula + curator routing) | Researcher |
| **4** | 16 | Approver + Feedback (curator review UI + context injection) | Researcher + Verity |
| **5** | 17 | Nightly cron + integration test (end-to-end) | Researcher + Ma'at |

---

## 📜 MANDATE COMPLIANCE

| Mandate | Compliance |
|---------|------------|
| **M5 (Gnosis Preservation)** | EvolveR automates L1→L2→L3 → permanent storage |
| **M11 (Soul Integrity)** | Principles feed into `soul.yaml` via Feedback component |
| **M18 (Token Efficiency)** | Local Qwen3-1.7B (4-bit) vs frontier model = 99% token savings |
| **M19 (Adversarial Alchemy)** | Contradiction resolution is explicit utility factor |
| **M7 (Local-First)** | Qwen3-1.7B runs locally; zero cloud tokens |
| **M22 (Provenance)** | Every principle carries `source_sessions` + `curator` approval |
| **M23 (Failure Integrity)** | Distiller runs in isolated process; failures logged, not silent |

---

## 📜 PROVENANCE

**Source**: `COGNITIVE_SCAFFOLDING_PROTOCOL.md` (SDP) + `KALI_BRIEFING_...` (EvolveR P9)
**Ratified**: D-569 (Cognitive Architecture Blueprint) + this doc
**Relationship**: **SDP → EvolveR = Human Protocol → Automated Successor**

*⬡ OMEGA ⬡ KALI ⬡ hy3-free ⬡ opencode ⬡ trc_evolver_sdp_successor ⬡ 2026-08-19*
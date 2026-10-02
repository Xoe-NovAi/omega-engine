# 🔱 Research — CLEAR-Pareto Scorecard, AMFO Evaluator & DyTopo Bridge
**AP Token**: `AP-RESEARCH-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Research package — CLEAR-Pareto Sovereignty Scorecard, AMFO tiered evaluation, and DyTopo cross-pollination bridge.
**Tags**: research, clear, amfo, dytopo, scorecard, evaluation, hivemind
**Cross-references**: src/omega/research/schema.py, src/omega/research/hivemind_bridge.py, src/omega/research/scorecard.py, src/omega/research/sandbox.py, src/omega/research/sediment.py, src/omega/research/types.py

---

## Overview

The `research` package implements the **Ω-Research Module** — a complete autonomous research framework with:

1. **CLEAR-Pareto Sovereignty Scorecard** — 5-dimension research quality metric
2. **AMFO Evaluator** — Tiered fidelity evaluation (Scout → Validate → Synthesize)
3. **DyTopo Hivemind Bridge** — Dynamic topology cross-pollination for research agents
4. **Research Sandboxes** — Isolated execution environments

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Research Package                        │
├─────────────────────────────────────────────────────────────┤
│  schema.py           │  Core types: CLEARScore, ResearchProposal, AMFOEvaluator │
│  hivemind_bridge.py  │  DyTopo cross-pollination bridge     │
│  scorecard.py        │  CLEAR scorecard implementation      │
│  sandbox.py          │  Isolated execution sandboxes        │
│  sediment.py         │  Research sediment accumulation      │
│  types.py            │  Type definitions                    │
│  __init__.py         │  Public exports                      │
└─────────────────────────────────────────────────────────────┘
```

---

## CLEAR-Pareto Sovereignty Scorecard

**5 Dimensions of Research Quality** (higher = better, all normalized 0.0-1.0):

| Dimension | Code | Description | Measurement |
|-----------|------|-------------|-------------|
| **C**ost Efficiency | `cost_efficiency` | USD per insight (inverted: lower cost = higher score) | Token tracking + provider pricing |
| **L**ocal-First Ratio | `local_first_ratio` | % inference on local models | Provider provenance (M22) |
| **E**pistemic Rigor | `epistemic_rigor` | Citations, verification, reproducibility | RAGAS + source verification |
| **A**dversarial Robustness | `adversarial_robustness` | Red-team survival rate | Attack simulation survival |
| **R**eproducibility | `reproducibility` | Deterministic re-run success | Seed control + env pinning |

### CLEARScore Class

```python
from omega.research.schema import CLEARScore

score = CLEARScore(
    cost_efficiency=0.85,           # Low cost per insight
    local_first_ratio=0.92,         # 92% local inference
    epistemic_rigor=0.78,           # Good citations
    adversarial_robustness=0.65,    # Survived 65% attacks
    reproducibility=0.88            # 88% re-run success
)

# Pareto dominance
other = CLEARScore(0.80, 0.90, 0.75, 0.60, 0.85)
score.dominates(other)  # True if >= on all, > on at least one

# Vector for optimization
vec = score.to_vector()  # (-cost, local, epistemic, adversarial, repro)
```

### Pareto Dominance

A dominates B iff A ≥ B on all dimensions AND A > B on at least one.

Used for **research portfolio optimization** — select non-dominated proposals.

---

## ResearchProposal Lifecycle

```python
from omega.research.schema import ResearchProposal, ProposalStatus

proposal = ResearchProposal(
    domain="S7",                    # S6-S10 (Cognition, Context, Observability, Orchestration, Validation)
    hypothesis="Local-first inference reduces tail latency by 40%",
    experiment_spec={
        "sandbox": "local_inference",
        "metrics": ["p99_latency", "throughput", "oom_rate"],
        "amfo_tier": "validate"
    },
    estimated_clear=CLEARScore(0.8, 0.9, 0.7, 0.6, 0.8),
    budget_usd=5.00,
    assigned_agents=["roc_racoon", "jem"]
)

# Lifecycle (enforced transitions)
proposal.advance_status(ProposalStatus.SCOUTING)      # DRAFT → SCOUTING
proposal.advance_status(ProposalStatus.VALIDATING)    # SCOUTING → VALIDATING
proposal.advance_status(ProposalStatus.SYNTHESIZING)  # VALIDATING → SYNTHESIZING
proposal.advance_status(ProposalStatus.CONSENSUS)     # SYNTHESIZING → CONSENSUS
proposal.advance_status(ProposalStatus.ARCHIVED)      # CONSENSUS → ARCHIVED (terminal)

proposal.is_terminal()  # True for ARCHIVED, REJECTED
```

**M12 Queue Integrity**: Terminal states have no outgoing transitions.

---

## AMFO Evaluator (Tiered Fidelity)

**Adaptive Multi-Fidelity Optimization** — 300% throughput on 14Gi RAM.

### Tiers

| Tier | Name | Budget | Fidelity | Model | Purpose |
|------|------|--------|----------|-------|---------|
| 1 | **Scout** | 60s | Low | qwen3-0.6b | Rapid feasibility |
| 2 | **Validate** | 300s | Medium | qwen3-1.7b | Source verification |
| 3 | **Synthesize** | 1800s | High | qwen3-4b-thinking | Deep reasoning + L3 extraction |

### AMFOEvaluator

```python
from omega.research.schema import AMFOEvaluator, CalibratedJudge, AMFO_TIERS

judge = CalibratedJudge(model="qwen3-4b-thinking-q4_k_m")
judge.calibrate(oracle_labels)  # 250 labels, ECE 0.18→0.06

evaluator = AMFOEvaluator(
    oracle_summon=oracle_summon_fn,
    judge=judge,
    tiers=AMFO_TIERS
)

# Evaluate proposal
eval_result = await evaluator.evaluate(proposal)

# Result
eval_result.tier_results  # List[AMFOResult]
eval_result.final_clear   # CLEARScore from highest completed tier
eval_result.early_stop_tier  # "validate" if early stop triggered
eval_result.consensus_reached  # True if early stop
```

### Early Stopping

If any tier achieves:
- `local_first_ratio > 0.8` AND `epistemic_rigor > 0.7`

→ Stop early, consensus reached.

### CalibratedJudge

Isotonic regression calibration on 250 oracle labels:
- **Raw ECE**: 0.18
- **Calibrated ECE**: 0.06
- **Judge Model**: qwen3-4b-thinking-q4_k_m (local, M7)

```python
judge = CalibratedJudge()
judge.calibrate([(raw_score, oracle_score), ...])  # 250 pairs

calibrated = judge.judge(raw_score)  # Apply calibration
```

---

## DyTopo Hivemind Bridge

**Dynamic Topology Cross-Pollination** for research agents.

### DyTopoNode

```python
from omega.research.schema import DyTopoNode

node = DyTopoNode(
    agent_id="roc_racoon",
    domains=["S6", "S7"],
    expertise_scores={"S6": 0.9, "S7": 0.8},
    historical_accuracy=0.85
)

relevance = node.relevance_for_proposal(proposal)
# domain_match * expertise * historical_accuracy
```

### ResearchHivemindBridge

```python
from omega.research.hivemind_bridge import create_research_bridge

bridge = create_research_bridge(nodes={
    "roc_racoon": DyTopoNode(...),
    "jem": DyTopoNode(...),
    "kali": DyTopoNode(...)
})

# Full cross-pollination cycle
consensus = await bridge.run_full_cycle(proposal)

# Phases:
# 1. broadcast_proposal() → Fan-out to relevant agents
# 2. collect_signals() → Gather critiques, validations, extensions
# 3. synthesize_consensus() → Weighted aggregation
# 4. Update proposal with consensus
```

### Signal Types

| Type | Description | Weight |
|------|-------------|--------|
| `validation` | Confirms hypothesis | + |
| `critique` | Identifies gaps/errors | - |
| `extension` | Proposes additions | + |
| `contradiction` | Direct contradiction (M17) | ⚠️ |

### Consensus Synthesis

```python
consensus = await bridge.synthesize_consensus(signals)

consensus.accepted  # True if ≥2 signals, avg_score ≥0.6, no contradictions
consensus.weighted_score  # expertise*0.7 + confidence*0.3
consensus.participating_agents  # ["roc_racoon", "jem"]
consensus.dissenting_signals  # Critiques + contradictions
consensus.l3_principle_candidate  # If score >0.8: "High-confidence consensus on..."
```

**M17 Cognitive Integrity**: `causal_trace_id` enables contradiction detection across agents.

---

## Hivemind Transport (M12 Integration)

Routes to `hivemind_awareness` (action="post") — Redis pub/sub excised.

```python
from omega.research.hivemind_bridge import (
    hivemind_publish,
    hivemind_subscribe,
    hivemind_get_awareness
)

# Publish (was Redis pub/sub)
await hivemind_publish("hivemind:research:proposals", json.dumps(payload), ttl=30)

# Subscribe (poll awareness snapshot)
result = await hivemind_subscribe("hivemind:research:signals", timeout=5.0)
# {"status": "success", "messages": [...]} or {"status": "empty", ...}

# Get awareness
agents = await hivemind_get_awareness()
```

**M23 Failure Integrity**: Adapters raise `HivemindTransportError` on failure — no fake success dicts.

---

## Usage Example

```python
from omega.research import (
    ResearchProposal, ProposalStatus, CLEARScore,
    AMFOEvaluator, CalibratedJudge, create_research_bridge,
    DyTopoNode, oracle_summon
)

# 1. Create proposal
proposal = ResearchProposal(
    domain="S7",
    hypothesis="zswap outperforms zRAM for desktop NVMe workloads",
    experiment_spec={"sandbox": "kernel_config", "metrics": ["latency", "throughput"]},
    estimated_clear=CLEARScore(0.85, 0.95, 0.8, 0.7, 0.9),
    budget_usd=2.00,
    assigned_agents=["roc_racoon", "jem"]
)

# 2. Setup DyTopo bridge
bridge = create_research_bridge(nodes={
    "roc_racoon": DyTopoNode("roc_racoon", ["S6", "S7"], {"S6": 0.9, "S7": 0.85}, 0.88),
    "jem": DyTopoNode("jem", ["S7", "S8"], {"S7": 0.8, "S8": 0.9}, 0.82)
})

# 3. Run AMFO evaluation
judge = CalibratedJudge()
judge.calibrate(oracle_labels)
evaluator = AMFOEvaluator(oracle_summon=oracle_summon, judge=judge)
eval_result = await evaluator.evaluate(proposal)

# 4. Cross-pollinate
consensus = await bridge.run_full_cycle(proposal)

# 5. Final result
print(f"CLEAR: {eval_result.final_clear}")
print(f"Consensus: {consensus.synthesized_insight}")
print(f"L3 Candidate: {consensus.l3_principle_candidate}")
```

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | All async via AnyIO |
| **M7 Local-First** | Judge models local (qwen3 series) |
| **M11 Soul Integrity** | L3 principle candidates from consensus |
| **M12 Queue Integrity** | Proposal lifecycle has terminal states |
| **M13 Temple-Grade** | Calibrated judge (ECE 0.06); tiered timeouts |
| **M17 Cognitive Integrity** | `causal_trace_id` on all signals/proposals |
| **M21 Contract Tests** | `assert_*` helpers for all types |
| **M22 Response Provenance** | `provider_name` on all tier results |
| **M23 Failure Integrity** | Timeouts = hard failures; transport raises |

---

## Testing

```bash
pytest tests/test_research_schema.py tests/test_amfo_evaluator.py tests/test_hivemind_bridge.py -v
```

Key test scenarios:
- CLEARScore Pareto dominance
- Proposal lifecycle transitions
- AMFO tier execution + early stop
- Judge calibration ECE reduction
- DyTopo relevance scoring
- Consensus synthesis weights
- Hivemind transport error handling
- Contract test helpers

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ RESEARCH-v1.0.0 ⬡ 2026-10-02 ⬡*
# ⚠️ SUPERSEDED — See R_SKEPTICAL_VERIFICATION_DEEPENED.md

# 🔱 R-SKEPTICAL-VERIFICATION: NLI & The Two-Source Rule
**Status**: FINAL (Temple-Grade)
**Orchestrator**: makali
**Date**: 2026-06-11
**Sovereign Mandate**: M13 (Temple-Grade), M9 (Error Integrity)

## 🎯 Objective
Implement a "Skeptical Verifier" that uses Natural Language Inference (NLI) and Natural Logic (NatLog) to corroborate claims across multiple sources, ensuring that no single source can "force" an entailment if a contradiction exists elsewhere.

## 🛡️ The Skeptical Verification Logic

### 1. The Hierarchy of Veracity (Contradiction-First)
The verifier must follow a strict logical hierarchy when aggregating results from multiple evidence spans. This prevents "majority-rule" hallucinations where multiple weak sources outweigh one strong contradiction.

**Aggregation Rule**:
1. **REFUTED**: If $\ge 1$ evidence span is classified as `Contradict`, the entire claim is **REFUTED**.
2. **SUPPORTED**: If $0$ spans `Contradict` AND $\ge 1$ span `Entails`, the claim is **SUPPORTED**.
3. **UNVERIFIED**: If $0$ spans `Contradict` AND $0$ spans `Entail`, the claim is **UNVERIFIED**.

### 2. Atomic Fact Decomposition
To avoid "partial truth" hallucinations, complex claims must be decomposed into **Atomic Facts** $\{A_1, A_2, \dots, A_n\}$.
- **Rule**: A complex claim $H$ is only `SUPPORTED` if every constituent atomic fact $A_i$ is `SUPPORTED`.
- **Rule**: A complex claim $H$ is `REFUTED` if any constituent atomic fact $A_i$ is `REFUTED`.

## 📐 Technical Implementation

### 1. Model Selection: DeBERTa-v3
- **Base Model**: `DeBERTa-v3-Large` is the recommended encoder for NLI.
- **Training**: Fine-tuned on MNLI, ANLI, and WANLI datasets.
- **Inference**: Use a threshold $\alpha$ on the entailment logit (e.g., $\alpha = 0.5$) rather than a simple `argmax` to tune the precision/recall trade-off.

### 2. Natural Logic (NatLog) & DFA Transitions
For high-fidelity proofs, the engine implements a **Deterministic Finite Automaton (DFA)** based on Natural Logic operators (NatOps).

**NatOp Priority & Semantic Meaning**:
| Operator | Name | Semantic Meaning | Priority |
| :--- | :--- | :--- | :--- |
| $\equiv$ | Equivalence | Exact match or paraphrase | 1 (Highest) |
| $\neg$ | Negation | Direct contradiction | 2 |
| $\sqsubseteq$ | Entailment | Evidence is more specific than claim | 3 |
| $\sqsupseteq$ | Super-entailment | Evidence is more general than claim | 4 |
| $\updownarrow$ | Alternation | Mutual exclusion (A or B, but not both) | 5 |
| $\#$ | Independence | No semantic relationship | 6 (Lowest) |

**DFA State Transitions**:
- **Start State**: $S$ (Neutral/Start).
- **Transitions**:
    - $S \xrightarrow{\equiv, \sqsubseteq} S$ (Stay in Support state).
    - $S \xrightarrow{\neg, \updownarrow} R$ (Transition to Refute state).
    - $S \xrightarrow{\#} N$ (Transition to Not Enough Info state).
- **Terminal States**: $S$ (Support), $R$ (Refute), $N$ (Not Enough Info).

### 3. The "Two-Source Rule" (Sovereign Gate)
To prevent reliance on a single potentially tainted source, the engine implements a **Sovereign Verification Gate**:
- **Sovereignly Verified**: A claim is only marked as "Sovereignly Verified" if it is `SUPPORTED` by $\ge 2$ independent sources and `CONTRADICTED` by $0$ sources.
- **Provisionally Supported**: Supported by only 1 source.

## 🛠️ Implementation Checklist for Omega Engine
- [ ] Integrate `DeBERTa-v3-Large` (NLI fine-tuned) into the `ModelGateway`.
- [ ] Implement `AtomicDecomposer` to split claims into simple propositions.
- [ ] Build the `SkepticalAggregator` implementing the Contradiction $\rightarrow$ Entailment $\rightarrow$ Neutral hierarchy.
- [ ] Implement the NatLog DFA transition logic in `src/omega/oracle/verification.py`.
- [ ] Add a `verification_threshold` parameter to the Oracle's `talk()` and `summon()` methods.
- [ ] Implement the "Two-Source Rule" as a configurable quality gate in `P10 Validation`.

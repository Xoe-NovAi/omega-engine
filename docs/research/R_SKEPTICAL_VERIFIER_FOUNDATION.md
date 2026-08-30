# ⚠️ SUPERSEDED — See Deepened Version

# R-SKEPTICAL-VERIFIER-FOUNDATION: NLI and the Two-Source Rule

**Status**: FOUNDATIONAL RESEARCH
**Entity**: Researcher
**Target**: Ma'at (H3-C2 Implementation)
**Date**: 2026-06-11

## Executive Summary
This document provides the theoretical and technical foundation for the **Skeptical Verifier** (H3-C2), focusing on Natural Language Inference (NLI) and the "Two-Source Rule" for high-fidelity fact verification. The goal is to move from "probabilistic generation" to "deterministic verification" by requiring multi-source corroboration and explicit contradiction handling.

## 1. Natural Language Inference (NLI)
NLI (also known as Textual Entailment) is the task of determining the relationship between a **Premise** (evidence) and a **Hypothesis** (claim).

### 1.1 The Three-Class Relation
Standard NLI models classify the relationship into one of three categories:
- **Entailment**: The premise logically implies that the hypothesis is true.
- **Contradiction**: The premise logically implies that the hypothesis is false.
- **Neutral**: The premise does not provide enough information to determine the truth of the hypothesis.

### 1.2 Recommended Model Architectures
For the Skeptical Verifier, we require high-precision, low-latency models.
- **Cross-Encoders**: (e.g., DeBERTa-v3) These are the gold standard for NLI. They process the premise and hypothesis together, capturing deep semantic interactions.
- **Bi-Encoders**: (e.g., Sentence-BERT) Faster, but less precise. Useful for initial candidate filtering before a Cross-Encoder final check.
- **LLM-as-a-Judge**: Using a reasoning model (e.g., Qwen3-4B-Think) with a structured prompt to output `[ENTAIL]`, `[CONTRADICT]`, or `[NEUTRAL]`.

## 2. The Two-Source Rule (TSR)
The TSR is a journalistic and intelligence standard adapted for the Omega Engine to eliminate "single-source hallucinations."

### 2.1 Implementation Logic
A claim $C$ is considered **Sovereignly Verified** if and only if:
$$\exists \{S_1, S_2, \dots, S_n\} \text{ where } n \ge 2 \text{ and } \forall S_i: \text{NLI}(S_i, C) = \text{Entailment}$$
And the sources $S_i$ must be **independent** (e.g., not just two different pages from the same website).

### 2.2 Verification Pipeline
1. **Evidence Retrieval**: Fetch $K$ snippets from the Vector Store/Web.
2. **NLI Scoring**: Run NLI on each snippet against the claim.
3. **Tallying**:
   - $\ge 2$ Entailments $\rightarrow$ **VERIFIED**
   - $\ge 1$ Contradiction $\rightarrow$ **CONTRADICTED** (Trigger Resolution)
   - $0$ Entailments $\rightarrow$ **UNVERIFIED**

## 3. Contradiction Resolution
When the system detects a contradiction (one source says X, another says NOT X), it must not simply average the results.

### 3.1 Resolution Strategies
- **Recency Weighting**: Prefer the source with the most recent timestamp (critical for evolving facts).
- **Authority Ranking**: Prefer sources with higher "Sovereignty Scores" (e.g., official docs > blog posts).
- **Divergence Analysis**: Use a reasoning model to identify *why* they differ (e.g., "Source A refers to version 1.0, Source B refers to version 2.0").
- **Skeptical Default**: If a contradiction cannot be resolved via authority or recency, the state must be marked as **CONTRADICTORY** and flagged for human review.

## 4. Proposed Architecture for H3-C2
- **Input**: Claim $C$ + Context $K$.
- **Module A (NLI Engine)**: DeBERTa-v3 or Qwen-Think as a classifier.
- **Module B (TSR Gate)**: Logic gate enforcing the $n \ge 2$ rule.
- **Module C (Resolution Engine)**: Reasoning loop for contradiction analysis.
- **Output**: `VerificationResult { status: VERIFIED|CONTRADICTED|UNVERIFIED, evidence: List[Source], reasoning: str }`

## Sources
- Wikipedia: Natural Language Inference
- arXiv: 2212.09561 (Self-Verification in LLMs)
- Journalism Standards: Fact-checking and Verification protocols.

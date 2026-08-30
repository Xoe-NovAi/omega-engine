# 🔱 Omega Engine — Research: Skeptical Verifier
**AP Token**: `AP-RESEARCH-SKEPTICAL-VERIFIER-v1.0.0`
**Status**: PROPOSED / BLUEPRINT
**Owner**: Jem / Pillar P10 (Validation)

## 🎯 Objective
Implement a high-fidelity verification layer that detects hallucinations by treating fact-checking as a Natural Language Inference (NLI) task, adhering to the 'Two-Source Rule' for high-stakes claims.

## 🛠️ Architectural Design

### 1. NLI-Based Verification Pipeline
The system will not ask "Is this true?" but rather "Does the evidence entail this claim?".

**Pipeline Flow**:
`Claim Extraction` $\rightarrow$ `Evidence Retrieval` $\rightarrow$ `NLI Scoring` $\rightarrow$ `Verdict`

- **Claim Extraction**: Decompose LLM response into atomic claims (sentences or entity-level facts).
- **Evidence Retrieval**: Fetch trusted context from `MemoryStore` or external tool outputs.
- **NLI Scoring**: Use a cross-encoder model (e.g., `cross-encoder/nli-deberta-v3-small`) to classify the relationship:
    - **Entailment**: Claim is grounded.
    - **Contradiction**: Claim is a hallucination (High Severity).
    - **Neutral**: Claim is unsupported (Medium Severity/Unverifiable).

### 2. The 'Two-Source Rule' (Skeptical Logic)
For claims flagged as `Neutral` or those marked as "High-Stakes" (defined by a keyword list or entity type), the verifier triggers a second, independent retrieval cycle.

- **Verification Gate**:
    - If Source A $\neq$ Source B $\rightarrow$ **Skeptical Flag** (Conflict detected).
    - If both entail $\rightarrow$ **Verified**.
    - If neither entail $\rightarrow$ **Unverifiable**.

### 3. Implementation Strategy
- **Model**: Integrate a small, fast NLI model via `llama-cpp-python` or a dedicated microservice.
- **Integration Point**: `src/omega/oracle/oracle.py` — the `talk()` and `summon()` methods will optionally pass the final response through the `SkepticalVerifier` before returning to the user.
- **Verdict Output**:
    - $\checkmark$ **Grounded**: All claims entail.
    - $\triangle$ **Caution**: Some claims are Neutral/Unverifiable.
    - $\times$ **Hallucinated**: One or more claims Contradict.

## 📉 Risk & Mitigation
- **Latency**: NLI checks add overhead. *Mitigation*: Use a small model (DeBERTa-small) and parallelize claim checks.
- **False Neutrals**: Some truths are not explicitly in the text. *Mitigation*: Allow a "Trust Threshold" for specific entities.

## 🔖 Heritage
This pattern derives from: `[NLI-based Hallucination Detection: 2024/2025 Research]`
Evolution: Integrates the "Two-Source Rule" from intelligence gathering to create a "Skeptical" agent.

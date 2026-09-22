# 🔱 SOVEREIGNTY INVARIANT SPECIFICATION: THE SYNERGY MODEL
**Doc ID**: `SPEC-SOVEREIGNTY-INVARIANT-v2.0`  
**Status**: RATIFIED CONSTITUTIONAL SPECIFICATION  
**Author**: MaKaLi Fusion (Kali / Ma'at / Lilith)  
**Date**: 2026-09-16  
**Supersedes**: Absolute Local-Only Isolation Assumptions  

---

## 1. Executive Summary & Purpose

The purpose of this specification is to define the **Sovereignty Invariant** for the Omega Engine. 

Historically, sovereignty was colloquially described as "100% offline, local-only inference." Under empirical examination during fleet development across Node 0 (AMD Ryzen 7 5700U) and Node 1 (Intel Core i7-13620H), this definition proved to be an unworkable dogma that paralyzed architectural velocity.

**The Sovereign Reality**:
> **Sovereignty is Policy Enforcement, Not Compute Isolation.**
> A system is sovereign when it has total, unbypassable authority over what data leaves its boundaries, where compute executes, and which models are entrusted with specific tasks. 

The **Synergy Model** explicitly orchestrates the dual forces of modern AI:
1. **Frontier Cloud Intelligence** for macro-architecture, cross-cutting reasoning, dialectical synthesis, and code generation.
2. **Local Machine Intelligence** for embeddings, private data sanitization, background heartbeat monitoring, and local task execution.

---

## 2. The Two-Ledger Accounting Framework

The engine implements a two-ledger model to track and enforce compute allocation:

```
                                  USER INFERENCE REQUEST
                                            │
                                            ▼
                             ┌────────────────────────────┐
                             │    POLICY ROUTER (M7)      │
                             │  (config/providers.yaml)   │
                             └──────────────┬─────────────┘
                                            │
                     ┌──────────────────────┴──────────────────────┐
                     ▼                                             ▼
        [BUILD & SYNTHESIS LEDGER]                     [EXECUTION & PRIVACY LEDGER]
         • Macro-Architecture                           • Local Vector Embeddings (FTS5/vec0)
         • Complex Code Generation                      • PII & Credential Sanitization
         • Cross-Node Dialectics                        • Background Health Watchdogs
         • High-Context Synthesis (200K+)               • Offline Fallback Loops
                     │                                             │
                     ▼                                             ▼
         FRONTIER CLOUD PROVIDERS                       LOCAL COMPUTE BACKENDS
       (OpenCode Zen / OpenRouter / API)            (llama.cpp native / Ollama / GGUF)
```

### 2.1 The Build & Synthesis Ledger
- **Role**: High-velocity reasoning substrate.
- **When Used**: Development sprints, complex architectural reviews, multi-agent council deliberations, code refactoring across hundreds of files.
- **Governance**: Must declare provider provenance (M22), use zero-telemetry keys where available (M8), and sanitize private vault contents before dispatch.

### 2.2 The Execution & Privacy Ledger
- **Role**: Sovereign, zero-egress local substrate.
- **When Used**: Vector embeddings generation, memory retrieval, background heartbeats, file indexing, and local private tasks.
- **Governance**: Pure local execution; zero network egress. Must comply with hardware constraints (DHAL) without causing OOM or system freeze.

---

## 3. The Core Invariant Definition

Let $R$ be an incoming inference or tool request, $P$ be the user's declared sovereign policy, and $E(R)$ be the execution target.

$$\text{Sovereignty}(R) = \begin{cases} 
\text{VALID} & \text{if } E(R) \in P.\text{allowed\_providers} \land \text{Taint}(R) \le P.\text{max\_taint} \\
\text{BLOCKED} & \text{otherwise}
\end{cases}$$

### The Three Constitutional Guarantees:
1. **Zero Unconsented Egress**: No user prompt, codebase snippet, or memory chunk leaves the local node unless the active task explicitly resolves to a provider permitted in `config/providers.yaml`.
2. **Deterministic Fallback**: If a cloud provider fails or is rate-limited, the system falls back along the configured chain (e.g., Cloud A $\rightarrow$ Cloud B $\rightarrow$ Local GGUF), never silently routing to an unvetted vendor.
3. **Hardware Boundary Awareness (Archangel/DHAL)**: The engine probes bare-metal limits (RAM, thermal, TDP). Local execution is throttled or offloaded *before* triggering kernel OOM-killer panics.

---

## 4. Implementation in `config/providers.yaml`

The policy is expressed declaratively in `config/providers.yaml`:

```yaml
sovereignty_policy:
  mode: synergy  # "synergy" | "local_first" | "cloud_first"
  
  tiers:
    reasoning:
      primary: opencode-zen
      fallback: [openrouter, anthropic, native-gguf]
      allowed_data_classification: [PUBLIC, INTERNAL]
      
    embeddings:
      primary: native-local
      model: bge-m3-q8
      allowed_data_classification: [PUBLIC, INTERNAL, PRIVATE, SOVEREIGN]
      
    background_watchdogs:
      primary: ollama-local
      model: qwen2.5-coder:7b
      allowed_data_classification: [PUBLIC, INTERNAL, PRIVATE]
```

---

## 5. Mandate Alignment (M7 Harmonization)

This specification formally updates the interpretation of **Mandate M7 (Local-First)**:
* **Historical M7**: "Local inference primary, cloud fallback only."
* **Harmonized M7**: "Sovereignty through declared policy. Local inference is mandatory for privacy-sensitive data, embeddings, and survival loops; cloud models are sovereignly leased for high-order synthesis under strict data governance."

*⬡ OMEGA ⬡ MAKALI-FUSION ⬡ SPEC-SOVEREIGNTY-INVARIANT-v2.0 ⬡ 2026-09-16*

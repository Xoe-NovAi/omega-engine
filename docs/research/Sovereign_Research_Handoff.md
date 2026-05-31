# 🔱 Omega Engine — Sovereign Research Handoff
**AP Token**: `AP-RESEARCH-HANDOFF-v1.0.0`
**Status**: ACTIVE | **Priority**: 🔴 CRITICAL
**Target**: Gemma 4-31B Research Specialist
**Source**: Sovereign Builder (Strategic Synthesis)

---

## ⬡ Executive Summary: The Path to Phase 1

The Omega Engine has successfully completed the **Blocker Remediation Sprint (A→D)**. All 8 real bugs from the R-44 audit are fixed, and the test suite is stable at **123/123 passing**. We are now at the threshold of **Phase 1 (Inference & Soul)**.

However, a critical architectural gap remains: **The engine is currently stateless**. While the `ContextBuilder` and `MemoryStore` exist, they are not wired into the `Oracle`. To wire them safely and effectively, we must first harden the provider fabric and establish a background orchestration layer.

**The Strategic Mandate**: We are implementing a **Dependency-First** approach. We will not wire ContextBuilder (R-51) until the resilience and orchestration layers (R-52a/b) are researched and specified.

---

## 🗺️ The Sovereign Dependency Graph

The following chain must be executed in order to ensure system stability and "Living World" capability:

`R-52a (Resilience)` $\rightarrow$ `R-52b (Orchestrator)` $\rightarrow$ `R-51 (ContextBuilder Wiring)` $\rightarrow$ `Phase 1 Implementation`

- **R-52a (OpenRouter Resilience)**: Prevents cloud-inference crashes from blocking the entire engine.
- **R-52b (Background Orchestrator)**: Enables the "Phone-a-Friend" model where entities can spawn sub-agents for deep research without blocking the user.
- **R-51 (ContextBuilder)**: Injects the resulting memory and soul-lessons into the prompt.

---

## 🏗️ The 4-Track Strategy (R-52)

The research and implementation are divided into four parallel tracks:

| Track | Focus | Priority | Key Objective |
| :--- | :--- | :--- | :--- |
| **Track A** | **Model Gateway Resilience** | 🔴 P0 | Implement retry, provider pinning, and health-based key rotation. |
| **Track B** | **Background Orchestrator** | 🔴 P0 | Design the `BackgroundWorker` for parallel sub-agent execution. |
| **Track C** | **External AI Ecosystem** | 🟡 P1 | Optimize NotebookLM, Gemini Deep Research, and Claude integration. |
| **Track D** | **Master Synthesis** | 🟢 Strategic | Maintain documentation hygiene and compaction anchors. |

### 🏛️ Architectural Commitments
1. **Health-Based Rotation**: Key rotation for OpenRouter must be based on real-time provider health, not simple round-robin.
2. **Provider Pinning**: Specific models must be pinned to specific providers in `config/providers.yaml`.
3. **Concurrency Control**: Background workers must use `anyio.TaskGroup` + `Semaphore(8)` to match our 8-key pool.
4. **External AI Isolation**: Use dedicated clean Google accounts for Gemini/NotebookLM to prevent folder-boundary leakage.
5. **Hybrid Claude Access**: Use a combination of temporary public repos (for URL browsing) and fine-grained PATs (for API access).
6. **Soul Evolution Trigger**: Lessons are extracted and written to `soul.yaml` during end-of-session summarization.
7. **Session Identity**: Format: `ses_{YYYYMMDD}_{entity}_{counter}` with daily rollover.
8. **Sovereign-First**: No telemetry, no PostgreSQL for entities, local-first priority.

---

## 🎯 Research Requests for Gemma 4-31B

You are tasked with providing the **Actionable Intelligence** (specs, code snippets, measured values) for the following items.

### 🔴 Priority 0: The Blockers (Immediate)

#### **R-52a: OpenRouter Resilience Spec**
- **The Ask**: Design a production-grade retry and rotation wrapper for the `ModelGateway`.
- **Specifics**: 
    - Optimal retry strategy for 502/timeout errors (Exponential backoff vs. Circuit Breaker).
    - Schema for `providers.yaml` to support `provider.order` and `models` fallback arrays.
    - Health monitoring pattern for an 8-key pool using Redis-backed state.
    - Exact implementation of the `OpenAICompatProvider` to pass routing parameters.

#### **R-52b: Background Orchestrator Spec**
- **The Ask**: Design the `BackgroundWorker` class for the "Phone-a-Friend" sub-agent model.
- **Specifics**:
    - Architecture for parallel execution using `anyio.TaskGroup` and `Semaphore(8)`.
    - A "Model Capability Matrix" for free-tier OpenRouter models (which model for which task?).
    - Reviewer prompt templates to validate sub-agent output before it is written to the knowledge base.
    - Recording pipeline: `Accepted Response` $\rightarrow$ `Library Store` $\rightarrow$ `Research Doc`.

#### **R-19: Soul Abstraction Logic**
- **The Ask**: Define how raw conversation logs are distilled into "Soul Lessons".
- **Specifics**:
    - Prompt templates for extracting structured lessons (lesson, domain, confidence, relevance_tags).
    - Schema for `soul.yaml` lesson entries.
    - Retrieval strategy for `ContextBuilder` to inject the most relevant lessons into a prompt.

---

### 🟡 Priority 1: Ecosystem & Performance

#### **R-52c/d/e: External AI Integration**
- **NotebookLM**: Design a categorization and chunking script (`prepare_notebooklm.py`) to stay under the 50-source/50MB limit.
- **Gemini Automation**: Design a CLI wrapper to sync the repo to a clean Drive account and trigger Deep Research.
- **Claude PAT**: Define the minimal fine-grained PAT scopes needed for `contents:read` and `metadata:read`.

#### **R-42: Hardware Steering (Zen 2 / 5700U)**
- **The Ask**: Optimize the engine for the Ryzen 5700U (8C/16T, 14GB RAM).
- **Specifics**:
    - Optimal `AllowedCPUs` map for the two CCX quads to minimize Infinity Fabric latency.
    - Qdrant HNSW parameters (`m`, `ef_construct`) optimized for split L3 cache (2x 4MB).
    - Feasibility of KV-cache offloading to the integrated Vega GPU via Vulkan.

---

### 🟢 Priority 2: Strategic Foundations

- **R-20 (Memory Tiering)**: Define RAM budgets for Hot/Warm/Cold tiers given the 14GB ceiling.
- **R-40 (Sovereign Lifecycle)**: Research `systemd` `fdstore`/`memfd` for preserving KV-cache state across restarts.
- **R-41 (Adaptive Orchestration)**: Formalize "Coupling Density" ($\gamma$) and "Consistency Score" ($\chi$) for multi-agent debate modes.

---

## 📦 Deliverable Requirements

For every research item, you must produce:
1. **A Markdown Document**: `docs/research/R##_<slug>.md` containing:
    - Version numbers, URLs, and measured values.
    - An **Uncertainty Log** (what remains unknown).
    - An **Implementation Note** addressed to the Builder (MiniMax M2.5) with exact file paths and code changes.
2. **An Index Entry**: Update `docs/research/INDEX.md`.
3. **A Completion Post**: Update `docs/team/COMMUNICATION_HUB.md`.

**Sovereign Reminder**: Local-first. Zero telemetry. All data comes home.

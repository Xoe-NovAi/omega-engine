# 🔱 MVE Definition: The Omega Core
**AP Token**: `AP-MVE-DEF-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_core ⬡ MVE-SCOPE

---

## §1 Core Objective
The Minimum Viable Engine (MVE) is a stable, local-first CLI runtime that enables entity-centric interaction via a provider-agnostic gateway. The MVE prioritizes **Identity, Routing, and Stability** over advanced native inference and heavy memory systems.

**Target**: Boot $\rightarrow$ Summon Entity $\rightarrow$ Get Response $\rightarrow$ Switch Entity.

---

## §2 MVE Scope (PR #1)

### 2.1 Stability & Identity
- **Runtime Hardening**: Fix MCP crashes and `aiosqlite` bugs.
- **Pantheon Alignment**: Updated `entities.yaml` and `hierarchy.yaml` (Oversouls restored).
- **Hygiene**: `.gitignore`, `.env.example`, `LICENSE` (Apache-2.0).
- **Session Headers**: Configurable `full`/`compact`/`off` headers.

### 2.2 The Entity Interface
- **Oracle Core**: Stable `talk()` and `summon()` functionality.
- **Session Control**: `/entity`, `/transient`, and `/header` commands.
- **Soul Integration**: Basic `ContextBuilder` injecting `soul.yaml` descriptors.

### 2.3 Provider Fabric (Light)
- **Remote Gemma (Primary)**: API-based provider for high-quality RAG (Priority 2).
- **lmster (Local Fallback)**: Stable local bridge with heartbeat and auto-recovery.
- **Resource Guard**: `Semaphore(1)` active to prevent OOM.

### 2.4 Baseline Infrastructure
- **Iris Bridge**: Basic container connectivity for "hey Iris" intent matching.
- **Architect Soul**: `data/entities/arch/soul.yaml` as the user root.

---

## §3 Out-of-Scope (Deferred to PR #2+)
- **Native Backend**: `llama-cpp-python` implementation and Zen 2 tuning.
- **Full RAG**: Qdrant wiring and Mnemosyne memory pipelines.
- **Soul Evolution**: Cross-pollination and metadata tagging.
- **VR Integration**: Godot 3D entity visualization.
- **Advanced UX**: "Invisible RAG" and "Harmonic Adjustment" steering.

---

## §4 MVE Release Timeline
| Milestone | Focus | Goal | Duration |
|-----------|--------|------|----------|
| **PR #1 (MVE)** | **Stabilization** | Stable CLI $\rightarrow$ Entity $\rightarrow$ Remote Gemma / lmster | 1 Week |
| **PR #2** | **Soul & Inference** | Native Backend + Soul Evolution | 2-3 Weeks |
| **PR #3** | **Memory & Intake** | Qdrant + Mnemosyne RAG | 3-4 Weeks |
| **PR #4** | **Orchestration** | Headless Agents + MCP Ecosystem | 2-3 Weeks |

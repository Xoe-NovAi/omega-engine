# 🔱 Omega Engine — Sovereign Strategic Context (v2.0)
**Target**: Gemini CLI / Dev Assistants
**Status**: SOVEREIGN-LOCK (Aligned)
**Core Formula**: $\text{Sovereign Intelligence} = (\text{Seed Identity} \times \text{Aura Projection}) + \text{Recursive Memory}$

This document is the absolute source of truth for the strategic alignment, custom rules, and architectural constraints of the Omega Engine. It incorporates the **Sovereign Lock** updates, ensuring the Engine remains a pure, mythology-agnostic runtime.

---

## 🛡️ I. The Sovereign Guardrails (Non-Negotiable)

These mandates are the "Firewall" of the project. Any implementation that violates these must be vetoed and refactored.

| Mandate | Rule | Rationale |
| :--- | :--- | :--- |
| **Engine-Stack Firewall** | The Engine core (`src/omega/`) must remain **mythology-agnostic**. | Ensures the Engine is a universal runtime. All esoteric/mythological data lives strictly in **WADs**. |
| **AnyIO Absolute** | Every runtime path must be fully `anyio`-compliant. **Zero blocking I/O**. | Prevents event-loop lag and ensures stability on the target hardware. |
| **zRAM Buffer Rule** | Use the 14GB-18GB "Yellow Zone" for graceful degradation, **not** for permanent model residency. | Prevents hard OOM crashes on the Ryzen 7 5700U. |
| **Sequentiality Mandate** | All multi-model reasoning must be **sequential**. | Preserves CPU cycles and prevents resource contention. |
| **The Iris Constant** | The always-on assistant is **Iris**. | Unifies the voice/assistant interface across the core. |
| **Local-First** | Zero telemetry. Zero cloud-dependency where local-first is mandated. | Absolute user sovereignty and data privacy. |
| **Resource Guard** | Use `ResourceGuard` (Semaphore(1)) for all inference and heavy I/O. | Hard ceiling of 14GB usable RAM. |

---

## 🏗️ II. Architectural Blueprint

### 1. The Provider Fabric (Inference Chain)
The `ModelGateway` manages a configurable fallback chain. All responses flow into the same memory and cross-pollination pipeline.

**Priority Chain**:
1. **Native GGUF** (`llama-cpp-python`): The "Malkuth's Grounding" for true local sovereignty. **Highest Priority**.
2. **Google AI Studio**: (Gemma 4-31B) Primary remote reasoning engine.
3. **OpenRouter**: Cloud fallback for diverse model access.
4. **lmster**: LM Studio headless (Primary local interim).
5. **Ollama**: Secondary local backup.

### 2. The WAD Container System (Containment)
The Engine uses a Doom-inspired WAD architecture to prevent core bloat.
*   **Engine Core**: A lean runtime (WAD Loader, Query Router, Provider Fabric, Memory Store, Godot Bridge).
*   **WAD (`.xoe`)**: The distributable package (tar.gz + `manifest.yaml`). Contains `entities/`, `voices/`, `knowledge/`, `vr/`, and `p2p.yaml`.
*   **XNAi Foundation**: The umbrella organization maintaining the engine and providing community stacks.

### 3. The Memory Loop (Sovereign Seed)
The system eliminates "session amnesia" via recursive memory.
*   **ContextBuilder**: Injects "Seed Identity" and "Recursive Memory" into system prompts.
*   **SessionManager**: Manages entity-scoped rolling sessions (`ses_{YYYYMMDD}_{entity_slug}_{counter}`).
*   **Refractive Abstraction**: A 3-tier distillation process (**Narrative $\rightarrow$ Insight $\rightarrow$ Universal Principle**) that evolves the `soul.yaml`.

---

## 🔌 III. MCP & Infrastructure Configuration

### 1. Active MCP Servers
*   **Hivemind MCP**: (`mcp/omega-hivemind/server.py`) Cross-CLI awareness and shared context.
*   **Search Fabric**: Integrated via Brave, Tavily, and Exa for high-fidelity research.
*   **Sovereign-Search**: Intelligent orchestration across search providers to optimize for depth and verification.

### 2. Background Workers
*   **ModelUpdaterWorker**: (`src/omega/workers/model_updater.py`) Scheduled via `APScheduler` (every 6 hours). Uses Gemma 4-31B to maintain the free model database (`docs/research/model_db/CURRENT_MODELS.md`).

---

## 🧭 IV. Dev Assistant Operational Guide

To maintain big-picture context and avoid "architectural drift," follow these protocols:

1.  **The Trinity of Truth**: Before any code change, verify against:
    *   `docs/ROADMAP.md`: Current Phase and trajectory.
    *   `docs/decisions/PIVOT_LOG.md`: The "Why" behind every pivot.
    *   `ORACLE_STACK.md`: The "How" of the current architecture.
2.  **Respect the Firewall**: If you are editing `src/omega/`, ensure no specific entity names or mythological concepts are introduced. If it's "esoteric," it goes in a WAD.
3.  **Verify AnyIO**: If you see `asyncio.run()` or `open()`, it is a bug. Use `anyio.run()` and `anyio.Path`.
4.  **Nomenclature Discipline**: 
    *   Use **XNAi** (not XNA).
    *   Use **.xoe** for stack files.
    *   Refer to the **Sovereign Seed** formula for intelligence goals.
5.  **RAM Mindfulness**: Assume a hard ceiling of 14GB. Every new model or heavy process must be wrapped in a `ResourceGuard`.

---

## 📚 V. Critical Source Map

| File | Purpose |
| :--- | :--- |
| `AGENTS.md` | Agent roles and Lilith Axioms. |
| `ORACLE_STACK.md` | Core architecture and hardware grounding. |
| `docs/ROADMAP.md` | The 6-Phase grand strategy. |
| `docs/decisions/PIVOT_LOG.md` | Historical record of architectural pivots. |
| `docs/strategy/STACK_RELEASE_ROADMAP.md` | WAD spec and release schedule. |
| `config/glossary.md` | Definitive terminology. |
| `config/providers.yaml` | Inference fallback chain. |
| `GNOSIS_BUFFER_PROTOCOL.md` | Rules for capturing and distilling session gnosis. |

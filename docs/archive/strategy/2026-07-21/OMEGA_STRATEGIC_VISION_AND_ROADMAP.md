# 🔱 OMEGA ENGINE: STRATEGIC VISION & ROADMAP
**The Operating System for Sovereign Cognition**

**AP Token**: `AP-STRATEGIC-VISION-v1.0.0`
**Date**: 2026-07-15
**Author**: Gemini 3.1 Pro (via OpenCode)
**Status**: RATIFIED — Post-PR Execution Blueprint

---

## 1. The Core Philosophy
The Omega Engine is not an API wrapper; it is an intelligent, philosophically grounded ecosystem. It operates on three unyielding principles:

*   **Total User Sovereignty:** Local-first processing, transparent telemetry, and deep configurability. The user owns the engine, the data, and the decisions.
*   **Free-Will Ethics:** The system acts as a counselor, never a jailer. Ethical constraints (like the 42 Ideals of Ma'at) flag issues and explain reasoning but always defer to the user with an "Acknowledge and Override" capability.
*   **Constructive Tension:** Intelligence is refined through dialectical debate (Thesis → Antithesis → Synthesis) rather than simple linear generation.

---

## 2. The Phased Execution Strategy

To survive as a solo developer and successfully build a community, we must aggressively separate the *Foundation* from the *Architecture*. 

### 🟢 PHASE 1: The Pristine Foundation (The First PR)
**Goal:** Ship a rock-solid, unquestionable core engine to attract open-source contributors.
*   **Scope:** Zero new features. Pure hygiene.
*   **Deliverables:** 100% test pass rate, elimination of all F821 undefined-name bugs, elimination of bare `except Exception:` blocks, strict AnyIO compliance, and a locked-down `src/omega/oracle.py` base router.
*   **The Pitch:** The README sells the *vision* of the upcoming Sovereign WAD Protocol and MaKaLi Triad, inviting the community to help build them on top of this pristine codebase.

### 🟡 PHASE 2: The Sovereign Command Center (The TUI)
**Goal:** Build a high-tech, hacker-ethos Terminal UI (likely via Python's `Textual` or `Rich`) to serve as the visual nervous system of the engine.
*   **Streaming Dialectics:** The CLI must stream intermediate thoughts. When the Council is invoked, the terminal splits into panes, showing Ma'at and Lilith debating in real-time, masking local inference latency and engaging the user.
*   **Hardware Empathy Dashboard:** Live tracking of the 14Gi RAM ceiling, VRAM usage, and the "Sovereignty Scorecard" (Local vs. Cloud ratio).
*   **Advisory Ethics Prompts:** Amber warning texts in the terminal for ethical flags, awaiting a `[Y/n]` override from the user.

### 🟠 PHASE 3: The Sovereign WAD Protocol (Strike 11)
**Goal:** Decouple the Engine from Identity and Ethics, creating the "Cartridge System."
*   **IWADs (Internal WADs):** The core archetype and identity of an entity (e.g., The Scribe).
*   **PWADs (Patch WADs):** Cultural, pantheon, or domain overlays (e.g., Egyptian Thoth vs. Hermetic Trismegistus). 
*   **Ethics WADs:** Pluggable moral frameworks (e.g., `maat_42`, `bushido_7`) that evaluate responses asynchronously and attach advisory metadata without halting execution.

### 🔴 PHASE 4: The Council Dispatcher (Strike 11.5)
**Goal:** Implement the 5-tier recursive dialectical reasoning engine as a native primitive.
*   **The 5-Tier Flow:** Kali (Orchestrator) → Ma'at (Build Thesis) + Lilith (Run Antithesis) → 3-5 Pillars (Domain Experts) → Cross-Domain Audit → Final Kali Synthesis.
*   **Hardware-Constrained Topology:** To respect the 14Gi limit, local pillar execution is strictly *serial*.
*   **The D118 Mentorship Pattern:** Heavy lifting is done by fast, small local models (1.7B Pillars), structured by medium models (4B Oversouls), and synthesized by the highest-tier available model (Cloud/Frontier Kali).
*   **CASArchiver:** Hashing and deduplicating claims across the council to prevent context-window bloat during the final synthesis.

### 🟣 PHASE 5: The Horizon (Web GUI & Ecosystem)
**Goal:** Expand to mass adoption once the core and TUI are battle-tested.
*   **The Web GUI:** Transition to a sleek, node-based web interface (React/Svelte + Electron/Tauri) allowing visual drag-and-drop of WADs and visual mind-mapping of the dialectical debates.
*   **Community Marketplace:** A decentralized hub for users to share custom WADs, council topologies, and specialized agent personas.

---

## 3. Architectural Directives for the Solo Developer

1. **The "Thin Waist" Implementation:** Keep `src/omega/oracle.py` incredibly thin. The engine should not know what a "Council" is. The engine should only know how to execute a DAG (Directed Acyclic Graph) of agent prompts. The `CouncilDispatcher` should just be a specialized DAG generator. This keeps your core engine mathematically provable and bug-free.
2. **Heavily Bias the "Triage" Gate:** 95% of queries do not need a Hegelian dialectic. Ensure the Iris speculative decode (or a fast Semantic Router) is aggressively tuned to bypass the Council and hit single-pillars for anything that isn't a complex, multi-variable architectural decision.
3. **The "Trojan Horse" PR Strategy:** Do not try to build Strike 11 (WADs) or Strike 11.5 (Council) before your first public PR. Ship the T0/T1 foundation. A rock-solid core attracts the open-source contributors you need to help build the complex logic.

---

## 4. Immediate Execution Path

You are currently in **Plan Mode**, and all conceptual loose ends are tied off. 

To execute on this roadmap, your immediate action is to **focus exclusively on Phase 1**. 
1. Use your `PR_PREP_WORKSPACE.md`. 
2. Clear the linting errors, type coverage gaps, and bug hygiene. 
3. Push the PR.

Once that PR is merged, you will have a clean slate to begin building the TUI (Phase 2) and architecting the WAD protocol (Phase 3), supported by the extensive research documentation committed to the `docs/research/` directory.
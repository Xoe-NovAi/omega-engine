# 🔱 Omega Engine — Omega CLI & Chainlit Integration Proposal
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ R28-INTEGRATION

**AP Token**: `AP-RESEARCH-R28-v1.0.0`
**Date**: 2026-05-14
**Status**: 🟡 PROPOSAL
**Target**: Architectural Blueprint for Dual-Frontend Interface

---

## 1. Vision: The Universal Vessel
The Omega Engine is the core runtime (The Oracle); the CLI and Web interfaces are merely **vessels**. A user should be able to move seamlessly between a terminal and a browser without losing context, persona, or progress.

## 2. Technical Guide: Creating the Omega CLI
To transform the OpenCode CLI into the official **Omega CLI**, the following branching and branding strategy is proposed:

### 2.1 Repository Branching
- **Source**: Branch the OpenCode core repository.
- **Identity Shift**:
    - Rename binary from `opencode` $\rightarrow$ `omega`.
    - Update all internal branding, banners, and help strings to reflect the Omega Engine identity.
    - Implement a custom `OmegaShell` wrapper that handles the session header rendering defined in `config/omega.yaml`.

### 2.2 Omega-fied Feature Set
The Omega CLI will implement a specialized command layer that interfaces directly with `src/omega/oracle/oracle.py`:

| Command | Action | Core Integration |
|---|---|---|
| `/summon <Entity>` | Immediate invocation of a specific Pillar Keeper | `Oracle._summon()` |
| `/entity <Entity>` | Switch active session persona | `EntityRegistry` + Session State |
| `/transient` | Enter ephemeral mode (no soul writes) | `Oracle` flag $\rightarrow$ `SoulManager` |
| `/header <mode>` | Toggle `full` \| `compact` \| `off` | `config/omega.yaml` $\rightarrow$ Shell Renderer |
| `/hivemind` | Show active agents across all CLIs | `Hivemind MCP` $\rightarrow$ `get_awareness()` |

---

## 3. Integration Architecture
The Omega Engine will adopt a **Core-Adapter** architecture to ensure frontend independence.

### 3.1 The Architecture Stack
```
[ User Interface Layer ]
       ▲          ▲
       │          │
 [ Omega CLI ] [ Chainlit Web ]  <-- Frontend Adapters
       │          │
       └────┬─────┘
            ▼
 [ Omega Engine Core API ]       <-- The "Brain" (Oracle, ModelGateway)
            │
    ┌───────┴───────┐
    ▼               ▼
[ MemoryStore ] [ EntityRegistry ] <-- State & Persona Persistence
```

### 3.2 Frontend Roles
- **OpenCode/Omega CLI**: High-efficiency research, file operations, and system-level orchestration.
- **Chainlit**: Visual RAG exploration, voice-to-voice interaction, and high-level curation.
- **Core Engine**: Handles all LLM routing, prompt construction (soul injection), and result processing.

---

## 4. State Synchronization & Continuity
To prevent "context amnesia" when switching interfaces, Omega will utilize a dual-tier synchronization strategy.

### 4.1 Tier 1: High-Level Awareness (Hivemind MCP)
The **Hivemind MCP** (`mcp/omega-hivemind/server.py`) acts as the cross-interface signaling layer.
- **Continuity Protocol**: 
    1. When a session ends/pauses in CLI, it calls `post_context()` with a `continuation` note.
    2. Upon Chainlit startup, it queries `get_awareness()` to see if there are active sessions.
    3. If found, Chainlit prompts: *"I see you were working on [Task] in the CLI. Would you like to continue here?"*

### 4.2 Tier 2: Volatile Session State (Shared Redis)
Following the legacy Chainlit pattern, a shared Redis store will manage real-time session data.
- **Key Pattern**: `omega:session:{session_id}:{context_type}`
- **Stored Data**:
    - `chat_history`: The recent exchange window for prompt injection.
    - `active_entity`: The current inhabitant of the session.
    - `transient_flag`: Whether the session is currently in `/transient` mode.

---

## 5. Implementation Roadmap

| Phase | Task | Priority |
|---|---|---|
| **1** | Implement `OmegaShell` wrapper for session header rendering | 🔴 High |
| **2** | Map `/summon` and `/entity` commands to `Oracle` methods | 🔴 High |
| **3** | Integrate Hivemind MCP `post_context` into CLI session exit | 🟡 Medium |
| **4** | Build Chainlit adapter that queries Hivemind for session restoration | 🟡 Medium |
| **5** | Unify session state via shared Redis `omega:session` keys | 🟢 Strategic |

---

**Implementation Note for the Artisan (Cline/Gemini)**:
The most critical immediate step is the **OmegaShell** wrapper. The CLI must be able to read `config/omega.yaml` and prepend the `⬡ OMEGA ⬡ ...` header to every output regardless of the tool being used. This establishes the "Sovereign" feel of the interface.

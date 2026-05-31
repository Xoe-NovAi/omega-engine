# 🔱 Sovereign Interface Integration Strategy
**Version**: 1.0.0
**Architect**: Sovereign CLI Architect

## 1. Objective: Cognitive Parity
The objective is to ensure that the "Sovereign Overseer" persona and the "Omega Engine" mandates are consistent across all agentic interfaces. No tool should be a "blind spot" in the system's self-awareness.

## 2. The Universal Interface Schema (UIS)
We map sovereign requirements to tool-specific configuration points:

### A. Identity & Persona
- **OpenCode**: Defined in `.opencode/agents/overseer.md`.
- **Gemini CLI**: Defined in `GEMINI.md` (Project Root) and `.gemini/tmp/omega-engine/memory/MEMORY.md`.
- **Cline**: Defined in `.clinerules`.
- **Alignment**: All three must reference `AGENTS.md` and `SOVEREIGN_MANDATES.md` as the primary sources of truth.

### B. Guardrails & Constraints
- **OpenCode**: Enforced via `opencode.json` (external_directory whitelist).
- **Gemini CLI**: Enforced via `.gemini/settings.json` and explicit mandates in `GEMINI.md`.
- **Cline**: Enforced via `.clinerules` and system prompt constraints.
- **Alignment**: The "Engine-Stack Firewall" (Core vs WAD) must be a non-negotiable constraint in all three.

### C. Memory & Gnosis
- **OpenCode**: Uses `session_gnosis.md` and the Gnosis Preservation Protocol (L1 $\rightarrow$ L2 $\rightarrow$ L3).
- **Gemini CLI**: Uses `CONTEXT.md` and the Auto-Memory distillation feature.
- **Cline**: Uses `memory.md` and session-based context.
- **Alignment**: Implement a "Cross-CLI Gnosis Sync" where key lessons learned in one tool are written to a shared `docs/gnosis/session_gnosis.md` file.

## 3. Implementation Roadmap
1. **Phase 1: Mandate Alignment**: Create `SOVEREIGN_MANDATES.md` and link it in all tool configs.
2. **Phase 2: Memory Synchronization**: Establish the shared `docs/gnosis/` directory as the "Universal Memory" for all agents.
3. **Phase 3: Execution Parity**: Implement "Plan Mode" logic (from Gemini CLI) into the Omega `Oracle` and `Orchestrator`.

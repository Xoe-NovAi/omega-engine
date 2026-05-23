# 🔱 Omega Engine — R-P002: Background Agent Architecture
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_anchor ⬡ KNOWLEDGE-ANCHOR

**AP Token**: `AP-KNOWLEDGE-ANCHOR-v1.0.0`
**Status**: ✅ ACTIVE
**Last Updated**: 2026-05-15
**Target**: Orchestrator & Background Worker Implementation

---

## 1. Overview
Background Agents are headless, autonomous processes designed to perform long-running tasks (e.g., legacy mining, library curation) without requiring active user interaction. The primary implementation utilizes **Gemma 4-31B** for high-density strategic synthesis.

## 2. Mining Workflow: The Belial Pattern
Named after the **Belial** entity (P0: The Abyss), the background mining workflow follows a recursive discovery loop:

1. **Sovereign Discovery**: The agent scans legacy directories (`xna-omega-legacy/`, `omega-stack-legacy/`) for strategic markers (e.g., "index", "roadmap", "decision").
2. **Pattern Extraction**: Using the `knowledge-miner` skill, the agent extracts core logic and specs from raw code.
3. **Strategic Synthesis**: The findings are synthesized into "Temple-Grade" research documents in `docs/research/`.
4. **Soul Update**: The agent records the "lesson learned" in the entity's `soul.yaml` and the Architect's `embodied_experiences`.

## 3. Headless OpenCode Execution
Background agents are deployed via the `opencode serve` pattern or as direct subprocesses managed by the `Orchestrator`.

### 3.1 Execution Pattern
```bash
# Spawning a headless agent for a specific research task
opencode task "Research the holographic memory lattice based on legacy artifacts" \
  --entity BELIAL \
  --headless \
  --persist /data/entities/belial/workspace/mining_session_01
```

### 3.2 Agent Lifecycle
| Phase | Action | Responsibility |
| :--- | :--- | :--- |
| **Spawn** | `Orchestrator.dispatch_agent()` | Injects soul prompt $\rightarrow$ spaws process |
| **Supervise** | `Observability.log_event()` | Tracks trace_id $\rightarrow$ monitors RAM/CPU |
| **State-Persist** | `Hivemind MCP` | Posts context snapshots $\rightarrow$ saves state to disk |
| **Terminate** | `ResourceGuard` | Graceful shutdown $\rightarrow$ releases Semaphore |

---

## 4. Monitoring & Error Recovery

### 4.1 Resource Constraints
To prevent OOM (Out of Memory) crashes on the Ryzen 5700U, all background agents are governed by the `ResourceGuard` (AnyIO Semaphore(1)).
- **Rule**: Only one high-capability model (Remote or Local) may be active at a time.
- **Priority**: Active user sessions override background agent execution.

### 4.2 Recovery Strategies
- **Checkpointing**: Agents must post current progress to the Hivemind MCP every 5 minutes.
- **Retry Logic**: `HTTP 429` (Rate Limit) triggers exponential backoff.
- **Heartbeat**: The `Orchestrator` monitors the PID; if a process hangs for >10 minutes, it is terminated and restarted from the last checkpoint.

---

## 5. Cross-References
- **R-MCP_SOVEREIGN_BLUEPRINT**: Sovereign Orchestration Blueprint
- **Implementation**: `src/omega/oracle/orchestrator.py`
- **Entity**: `config/entities.yaml` $\rightarrow$ `belial`

---
**Implementation Note**: Background agents must always include the `Sovereign Agent` mandate in their system prompt, ensuring they post all critical decisions to the Hivemind for cross-CLI awareness.

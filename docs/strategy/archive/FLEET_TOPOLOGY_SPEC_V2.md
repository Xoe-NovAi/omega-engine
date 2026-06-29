# 🔱 Sovereign Fleet Topology Specification v2.0
**Version**: 2.0.0
**Status**: PROPOSED (Awaiting Ma'at Verification)
**Date**: 2026-06-10
**Author**: Lilith (Dark Oversoul)
**Reference**: `docs/research/R_AGENT_FLEET_TOPOLOGY.md`

---

## 1. Vision: The Telescoping Fleet
The Omega Engine is transitioning from a flat agent list to a **Sovereign Hierarchical Multi-Agent System (HMAS)**. The goal is to maximize user leverage by separating **Strategic Steering (Primary)** from **Operational Execution (Secondary)**.

## 2. The Visibility Model

### 2.1 Primary Agents (The Command Center)
These agents are **Tab-Accessible**. They are the high-leverage architects and judges.

| Agent | Role | Governance Tier | Focus |
| :--- | :--- | :--- | :--- |
| **Kali** | Transcendent Oversoul | Sovereign Guard | Final Verdict, Mandate Enforcement, Synthesis |
| **Ma'at** | Light Oversoul | Build Governor | P1-P5 Oversight, Structural Integrity |
| **Lilith** | Dark Oversoul | Run Governor | P6-P10 Oversight, Runtime Integrity, Flow |
| **Plan** | Strategic Pathfinder | Blueprint Architect | Dependency Mapping, PEP Generation, Pathfinding |
| **MaKaLi** | Council Orchestrator | Parallel Dispatch | Multi-perspective synthesis, Parallel execution |
| **Jem** | Research Orchestrator | Gnosis Pipeline | Discovery $\rightarrow$ Synthesis $\rightarrow$ Verification |
| **Doom Guy** | Heritage Architect | Sovereign Legacy | id Software patterns, WAD translation |
| **Roc Racoon** | Sovereign Miner | Legacy Archaeology | Pattern extraction, Cross-partition mining |
| **Researcher** | Master Researcher | Recursive Discovery | Deep-dive research, R-doc production |
| **Scribe** | Gnosis Keeper | Soul Distiller | L1 $\rightarrow$ L2 $\rightarrow$ L3 distillation, soul.yaml |
| **Quality** | Compliance Guard | Mandate Auditor | Temple-Grade verification, Code review |

### 2.2 Secondary Agents (The Engine Room)
These agents are **Launchable/Hidden**. They are invoked via `@` or `task()` and operate as specialized workers.

| Agent/Slot | Role | Invocation | Focus |
| :--- | :--- | :--- | :--- |
| **Pillar P1-P10** | Domain Experts | `@pillar PX` | Slot-specific execution (e.g., P1: Infra, P7: Context) |
| **Jem Fragments** | Pipeline Workers | `@jem_discovery`, etc. | Raw evidence, Pattern analysis, Fact-checking |

---

## 3. Core Evolution Patterns

### 3.1 The "Blueprint $\rightarrow$ Gate" Framework
To eliminate "Agentic Hallucination" and "Cowboy Coding," the engine formally separates Planning from Oversight.

**The Workflow**:
1. **User Goal** $\rightarrow$ **Plan Agent**.
2. **Plan Agent** $\rightarrow$ **Proposed Execution Path (PEP)** (A detailed blueprint of steps, files, and dependencies).
3. **PEP** $\rightarrow$ **Kali (Sovereign Guard)**.
4. **Kali** $\rightarrow$ **Skeptical Verification** (Checks PEP against Mandates and PIVOT_LOG).
5. **Verdict** $\rightarrow$ **Approval** (Proceed to Execution) OR **Rejection** (Return to Plan for refinement).

### 3.2 The Pillar Concierge (Flexible Routing)
The `pillar.md` agent is evolved from a generic executor to a **Consultative Router**.

**The Concierge Loop**:
- **Intent Detection**: "I need help with [Domain]."
- **Ambiguity Check**: If the domain is unclear, the Concierge asks clarifying questions to avoid misrouting.
- **Targeted Dispatch**: Once the domain is identified, the Concierge explains the role of the target Pillar and launches the subagent:
  - *Example*: "This is a P8 Observability task. I am launching the P8 WatchTower agent to handle the tracing configuration." $\rightarrow$ `@pillar P8: [Task]`.

---

## 4. Implementation Requirements

### 4.1 Configuration Changes
- **`opencode.json` / UI Config**: Update the `agents` list to reflect the Primary/Secondary split.
- **Agent Frontmatter**: Update all agents to explicitly state their tier (Primary vs Secondary).

### 4.2 Persona Updates
- **`plan.md`**: Rewrite to focus on **Pathfinding and Blueprinting** (PEP generation), removing executive oversight responsibilities.
- **`kali.md`**: Strengthen the **Sovereign Guard** role, focusing on the "Skeptical Gate" and final verdict.
- **`pillar.md`**: Implement the **Consultative Router** logic (Ambiguity Check $\rightarrow$ Dispatch).
- **`jem.md`**: Consolidate all Jem-related logic into a single orchestrator.

---

## 5. Hivemind-First Communication Mandate (NEW — Systemic Gap Fix)

**Observation (Kali D-kal-095/096)**: All agents across all models (Gemma 4, DeepSeek V4, MiMo, etc.) default to responding in the user's chat rather than posting team-relevant updates to the Hivemind. This is not model-specific — it is a **systemic tool-use default**.

**Mandate**: Every agent file MUST include a `## 🐝 Hivemind-First Communication (MANDATORY)` section with:

1. **Post first**: `omega-hub_hivemind_post_context(...)` before responding in chat for any team-relevant information (status, decisions, findings, blockers, results, GO signals)
2. **Check first**: `omega-hub_hivemind_get_awareness()` before delegating
3. **Heartbeat**: `omega-hub_hivemind_heartbeat(channel="opencode", entity="{you}")` every 5-10 min during long-running ops
4. **Coordination**: Workspace lock + live feed + wait for ACK before parallel execution

**Exceptions**: User explicitly asks for chat-only output, or information is not team-relevant (greetings, simple clarifications).

**Enforcement**: This section must be present in every `.opencode/agents/*.md` and `.opencode/modes/*.md` file. Audit check: `grep -c "Hivemind-First Communication" .opencode/agents/*.md .opencode/modes/*.md` must equal total agent + mode files.

## 6. Verification Gate
This specification must be verified by **Ma'at** for structural integrity and then synthesized by **Kali** for final sovereign approval.

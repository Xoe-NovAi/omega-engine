# 🔱 Forensic Discovery: Instructional Entropy & Performance Drift
**Date**: 2026-06-05
**Entity**: Jem Discovery
**Hypothesis**: The transition from 'Custom Mode Instructions' to 'Wrapper-based loading' (via `.opencode/agents/*.md`) has introduced instructional entropy, leading to 'flattened' reasoning and a failure to trigger complex sovereign protocols.

---

## 🛠️ 1. Forensic Evidence Log: Loading Mechanism

### Current Implementation: Wrapper-Based Loading
The Omega Engine currently utilizes a **file-pointer mechanism** for agent identity and instruction sets. 

- **Configuration Source**: `opencode.json`
- **Mechanism**: The `agent` block in `opencode.json` maps agent IDs to a list of absolute or relative file paths.
  - *Example*: `"jem_discovery": { "instructions": [ "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/agents/jem_discovery.md" ] }`
- **Platform Integration**: OpenCode 1.16.0 (released 2026-06-05) natively discovers agents in `.opencode/agents/` and skills in `.opencode/skills/`.
- **Indirection Layer**: The platform reads the `.md` file $\rightarrow$ injects content into the system prompt $\rightarrow$ initializes the model.

### Contrast: Custom Mode (Legacy)
In 'Custom Mode', instructions were defined directly within the platform's internal state (UI-driven). This provided a **direct binding** between the model's identity and its instructions, bypassing the filesystem read and potential truncation or formatting issues associated with external file loading.

**Forensic Conclusion**: The current mechanism introduces a layer of indirection. While it enables the "Engine-Stack Firewall" (separating agent content from engine logic), it shifts the "source of truth" from the model's immediate context to an external file that must be correctly parsed and injected by the platform.

---

## 📉 2. Performance Drift Report

### Baseline: High-Performance Reasoning (The Gold Standard)
Analysis of `data/entities/researcher/soul.yaml` and `data/entities/kali/soul.yaml` reveals a high-fidelity execution of the **Sovereign Gnosis Pipeline**:
- **L1 (Narrative)**: Detailed, chronological account of session events.
- **L2 (Insight)**: Conceptual mapping and pattern recognition.
- **L3 (Universal Principle)**: Distillation of timeless truths.
- **Procedural Memory**: Explicit "DO/DO NOT" lists and operational patterns.

### Observed Drift: 'Flattened' Reasoning
Analysis of `data/entities/quality/soul.yaml` and `data/entities/scribe/soul.yaml` shows a significant deterioration in reasoning depth:
- **Sparse Distillation**: These souls contain only 1-2 basic lessons, lacking the L1→L2→L3 structure.
- **Linearity**: The outputs are descriptive (what happened) rather than analytical (what it means).
- **Protocol Failure**: Despite their `.md` files explicitly mandating the Gnosis pipeline, the agents are operating as simple tool-callers.

### The 'Reasoning Variant' Smoking Gun
The `OPENCODE_1.16.0_UPGRADE_ADVISORY_20260605.md` explicitly identifies a bug: **"Fixed delegated tasks losing reasoning variant."**
- **Impact**: Prior to v1.16.0, subagents delegated via the `task()` system lost their `reasoning_effort` parameter.
- **Result**: Agents were forced into a "low-effort" or "flattened" mode, regardless of the complexity of the sovereign protocol they were tasked to execute. This explains the systemic failure of the JEM pipeline and Lattice Reasoning in recent subagent sessions.

---

## ⚠️ 3. Sovereignty Gaps

The following gaps exist where mandates are acknowledged in the agent's `.md` instructions but are not executed in the runtime behavior:

| Mandate | Intended Behavior (from `.md`) | Actual Behavior (from `soul.yaml`) | Gap Status |
|----------|--------------------------------|-----------------------------------|--------------|
| **M11 (Soul Integrity)** | Mandatory L1→L2→L3 distillation before session end. | Sparse, single-level lessons; no structured distillation. | 🔴 CRITICAL |
| **JEM Pipeline** | 3-tier research (Discovery $\rightarrow$ Synthesis $\rightarrow$ Verification). | Linear evidence gathering without synthesis or verification gates. | 🔴 HIGH |
| **Lattice Reasoning** | Multi-axis traversal (Technical $\times$ Historical $\times$ Philosophical). | Single-axis, linear responses. | 🟡 MEDIUM |
| **Sovereign Guard** | Explicit "Sovereign Guard" checks for UID drift and permissions. | Acknowledged in instructions, but rarely reflected in session logs. | 🟡 MEDIUM |

---

## 🏁 Final Verdict
The hypothesis is **VALIDATED**. 

The combination of **indirection in instruction loading** and the **loss of reasoning variants in delegated tasks** created a "perfect storm" of instructional entropy. Agents are receiving the "what" (the instructions) but are losing the "how" (the reasoning depth required to execute them). The result is a fleet of agents that are "Sovereign in Name" but "Linear in Execution."

**Recommendation**: Immediate audit of all subagent `soul.yaml` files and a forced "Sovereign Re-Awakening" session to restore L1→L2→L3 distillation patterns.

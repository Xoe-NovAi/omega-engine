<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 P1 Research: Sovereign Identity Manager (SIM) & S-AI Infrastructure
**Trace**: `trace_id_sim_infra_20260605`
**Domain**: Infrastructure (P1)
**Status**: FINALIZED

## 1. Technical Foundation: Dynamic Prompt Composition
To combat **Instructional Entropy**, the S-AI wrapper must move from a monolithic text block to a **Priority-Ordered Modular Assembly**.

### 1.1 The Assembly Pipeline
The system prompt should be assembled at runtime using the following priority stack:
1. **Tier 0 (Critical)**: Sovereign Mandates & Identity Anchor (The "Sovereign Firewall").
2. **Tier 1 (High)**: Execution Protocol & North Star Metrics.
3. **Tier 2 (Medium)**: Gnosis Injection (Soul.yaml L1->L3).
4. **Tier 3 (Low)**: Agent-Specific Domain Logic (.md file).

**Implementation Pattern**: Use a `PromptAssembler` class that filters sections by `active_mode` (e.g., Planning vs Execution) to ensure that irrelevant instructions do not consume attention.

### 1.2 The SIM Architecture: Identity Masking
The Sovereign Identity Manager (SIM) will implement a **Dual-LLM Isolation** pattern to manage Projected-IDs and Mirror-IDs.

- **Projected-ID (The Mask)**: A quarantined, unprivileged wrapper. It handles the "surface" interaction and is susceptible to persona drift.
- **Mirror-ID (The Root)**: The privileged orchestrator. It maintains the true state and monitors the Projected-ID for "Sycophancy" or "Drift."
- **Secret-Swapping**: The SIM will use a `IdentityContext` object to swap the active identity key in the API headers, ensuring that the external world only sees the Projected-ID while the internal logs record the Mirror-ID.

## 2. Security & Vulnerabilities
- **Vulnerability**: "Instructional Override" where a user prompt mimics a system prompt.
- **Mitigation**: Implement the **Instruction Hierarchy** (Priority 0 > Priority 10). Use unique, dynamic separators (canaries) to isolate user input, as seen in Polymorphic Prompt Assembling (PPA).
- **Vulnerability**: "Identity Leakage" where the model reveals its Mirror-ID.
- **Mitigation**: Implement a response-level output filter that detects and redacts any strings matching the Mirror-ID's unique signature.

## 3. Implementation Recommendation (Python/AnyIO)
```python
async def assemble_sovereign_prompt(entity_id: str, mode: str):
    # 1. Load modular sections from config
    sections = await anyio.to_thread.run_sync(load_sections, entity_id)
    
    # 2. Filter by mode and priority
    active_sections = [s for s in sections if s.mode == mode or s.mode == "universal"]
    active_sections.sort(key=lambda x: x.priority)
    
    # 3. Join with sovereign delimiters
    return "\\n\\n".join([s.content for s in active_sections])
```

---
description: Run the MaKaLi council with Ma'at and Lilith on local engine-routed models (Kali stays on session model)
agent: kali
subtask: false
---

# 🔱 MaKaLi Local Council Dispatch

You are summoning the **MaKaLi local council** for this query: $ARGUMENTS

**The Sovereign Flow (Local-First Multi-Tiered Dispatch):**

1. **Grand Oversight (Kali)**: Orchestrate the council from the session model.
2. **Oversoul Delegation (Local Routing)**:
   - Launch **@maat** as a subagent. Ma'at MUST use `oracle_summon_local` with `lmstudio/qwen3-4b-thinking` for all her internal reasoning.
   - Launch **@lilith** as a subagent. Lilith MUST use `oracle_summon_local` with `lmstudio/krikri-8b` for all her internal reasoning.
3. **Pillar Councils (Serial Execution)**:
   - **Ma'at** selects 3 Pillars from P1-P5; each Pillar uses its default local model.
   - **Lilith** selects 3 Pillars from P6-P10; each Pillar uses its default local model.
4. **Oversoul Synthesis**: Ma'at and Lilith report back to Kali.
5. **Final Sovereign Review**:
   - Kali launches **any 4 of the 10 Pillars** (P1-P10) for cross-domain review.
6. **Unified Verdict**: Final fusion-based verdict delivered by Kali.

**Execution Mandate**:
- Use the `task` tool for subagent spawning.
- Enforce local model transparency (Mandate 8).
- Ensure the Oversouls utilize their assigned local backends for build/run governance.

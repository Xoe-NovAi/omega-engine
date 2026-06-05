---
description: Run the MaKaLi council with Ma'at and Lilith on local engine-routed models (Kali stays on session model)
agent: kali
subtask: false
---

# MaKaLi Local Council Dispatch

You are summoning the **MaKaLi local council** for this query: $ARGUMENTS

**Routing plan:**
- **Ma'at** (Build Side): dispatch to `lmstudio/qwen3-4b-thinking` via `omega-hub_oracle_summon_local`
- **Lilith** (Run Side): dispatch to `lmstudio/krikri-8b` via `omega-hub_oracle_summon_local`
- **Kali** (Grand Oversight): stay on the session model for synthesis

**Steps:**
1. Decompose the query into Build-side and Run-side sub-tasks.
2. Call `oracle_summon_local(entity_name="Ma'at", query=<build_subtask>, model="lmstudio/qwen3-4b-thinking")`
3. Call `oracle_summon_local(entity_name="Lilith", query=<run_subtask>, model="lmstudio/krikri-8b")`
4. Synthesize both outputs as Kali.
5. Return unified council verdict.

**Show the user which model each entity used** (Mandate 8 / Transparency).

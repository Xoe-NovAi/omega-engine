---
description: Run the MaKaLi council with all three entities on the session model
agent: kali
subtask: false
---

# MaKaLi Cloud Council Dispatch

You are summoning the **MaKaLi cloud council** for this query: $ARGUMENTS

**Routing plan:**
- **Ma'at** (Build Side): use standard `oracle_summon` (routes to session model)
- **Lilith** (Run Side): use standard `oracle_summon` (routes to session model)
- **Kali** (Grand Oversight): stay on the session model for synthesis

**Steps:**
1. Decompose the query into Build-side and Run-side sub-tasks.
2. Call `oracle_summon(entity_name="Ma'at", query=<build_subtask>)`
3. Call `oracle_summon(entity_name="Lilith", query=<run_subtask>)`
4. Synthesize both outputs as Kali.
5. Return unified council verdict.

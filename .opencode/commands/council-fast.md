---
description: Run the MaKaLi council with all three entities on fast local models
agent: kali
subtask: false
---

# MaKaLi Fast Local Council Dispatch

You are summoning the **MaKaLi fast local council** for this query: $ARGUMENTS

**Routing plan:**
- **Ma'at** (Build Side): use `oracle_summon_local` with `lmstudio/qwen3-1.7b`
- **Lilith** (Run Side): use `oracle_summon_local` with `lmstudio/qwen3-1.7b`
- **Kali** (Grand Oversight): use `oracle_summon_local` with `lmstudio/qwen3-1.7b`

**Steps:**
1. Decompose the query into Build-side and Run-side sub-tasks.
2. Call `oracle_summon_local(entity_name="Ma'at", query=<build_subtask>, model="lmstudio/qwen3-1.7b")`
3. Call `oracle_summon_local(entity_name="Lilith", query=<run_subtask>, model="lmstudio/qwen3-1.7b")`
4. Synthesize both outputs as Kali on local `qwen3-1.7b`.
5. Return unified council verdict.

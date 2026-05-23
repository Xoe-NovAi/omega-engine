# 🔱 Omega Engine — Sovereign Core Foundations
**AP Token**: `AP-SOVEREIGN-CORE-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ FOUNDATIONS

---

## 🧠 R-20: Memory Tiering Strategy (The 14GB RAM Ceiling)

To maintain stability on the Ryzen 5700U (14GB total RAM), the Omega Engine implements a tiered memory architecture. This prevents OOM crashes while ensuring that the most critical context is always available to the active entity.

### Memory Budget Allocation
| Tier | Name | Budget | Technology | Latency | Scope |
|---|---|---|---|---|---|
| **L1** | **Hot Memory** | 1 - 2 GB | Redis / RAM-dict | $\mu s$ | Active context window, session state, L1 prompt injections. |
| **L2** | **Warm Memory** | 2 - 4 GB | mmap / SSD Cache | $ms$ | Recent session history, active Soul lessons, cached vector chunks. |
| **L3** | **Cold Memory** | Disk-Bound | Qdrant / SQLite | $10-100 ms$ | Full Knowledge Base, archival logs, historical soul states. |

### Tiering Logic
1. **L1 $\rightarrow$ L2**: When a session ends, the active L1 context is compressed and pushed to L2 as a "Session Snapshot."
2. **L2 $\rightarrow$ L3**: When L2 exceeds its 4GB budget, the Least Recently Used (LRU) snapshots are serialized to L3 (Cold Storage).
3. **L3 $\rightarrow$ L1**: Upon summoning an entity or referencing a deep-memory item, the `ContextBuilder` pulls from L3 $\rightarrow$ L2 $\rightarrow$ L1.

---

## ⚡ R-40: Sovereign Lifecycle (KV-Cache Preservation)

Standard engine restarts result in a "Cold Start," where the model must re-process the system prompt and initial context to rebuild the KV-cache. For sovereign autonomy, we implement **State-Preserving Hibernation**.

### The `fdstore` / `memfd` Mechanism
To preserve the KV-cache across process restarts without hitting the disk (which would be too slow), we leverage Linux kernel primitives:

1. **Creation**: On first load, the engine creates an anonymous file in RAM using `memfd_create()`.
2. **Mapping**: The `llama-cpp-python` KV-cache is mapped directly into this `memfd` region.
3. **Handover**: The resulting File Descriptor (FD) is passed to `systemd` via the `fdstore` API.
4. **Recovery**: Upon restart, the new engine process requests the FD from `systemd` and re-attaches the memory region.

### Impact
- **Cold Start Latency**: Reduced from $\approx 2-5s$ to $\approx 100ms$.
- **Persistence**: KV-cache survives engine crashes and software updates, provided the system does not reboot.
- **Hardware Load**: Eliminates redundant tensor computations during the boot sequence.

---

## 🌀 R-41: Adaptive Orchestration (The Intelligence Layer)

To move beyond simple sequential agent calls, the Omega Engine uses a dynamic orchestration topology based on two primary metrics: **Coupling Density** ($\gamma$) and **Consistency Score** ($\chi$).

### 1. Coupling Density ($\gamma$)
$\gamma$ defines the "interconnectivity" of a task. It determines if agents should work in parallel (independent) or in a loop (collaborative).

- **Low $\gamma$ (Independent)**: Tasks can be split into disjoint sets. 
  - *Example*: "Find the current price of BTC and write a poem about it."
  - *Topology*: $\text{Task} \rightarrow [\text{Agent A}, \text{Agent B}] \rightarrow \text{Synthesis}$.
- **High $\gamma$ (Interdependent)**: Tasks require iterative refinement and cross-checking.
  - *Example*: "Audit this code for security vulnerabilities and rewrite it to fix them without changing functionality."
  - *Topology*: $\text{Task} \rightarrow \text{Agent A} \rightleftharpoons \text{Agent B} \rightarrow \text{Validation} \rightarrow \text{Output}$.

### 2. Consistency Score ($\chi$)
$\chi$ measures the agreement between multiple agents providing the same answer. It is the trigger for **Debate Mode**.

- **High $\chi$ (Consensus)**: Agents provide similar, non-contradictory results. $\rightarrow$ Response is delivered immediately.
- **Low $\chi$ (Divergence)**: Agents provide conflicting truths or fundamentally different approaches. $\rightarrow$ **Trigger Debate Mode**.

### Debate Mode Protocol
When $\chi < \text{Threshold}$, the Orchestrator initiates a recursive loop:
1. **Contradiction Highlight**: The Orchestrator presents Agent A's result to Agent B and vice versa.
2. **Rebuttal**: Agents are prompted to defend their position or concede based on evidence.
3. **Convergence**: The loop continues until $\chi$ reaches the required threshold or a "Sovereign Judge" (typically SOPHIA or MAAT) makes a final ruling.

---

## 🛠️ Implementation Notes for Builder Agents
- **Memory**: Implement the budget enforcer in `src/omega/oracle/context_builder.py`.
- **Lifecycle**: Integrate `memfd` logic into `src/omega/oracle/model_gateway.py`'s loading sequence.
- **Orchestration**: Add $\gamma$ and $\chi$ calculation logic to `src/omega/oracle/orchestrator.py`.

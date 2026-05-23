# 🔱 Omega Engine — Sovereign Orchestration Blueprint
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_gnosis ⬡ R-MCP-BLUEPRINT

**AP Token**: `AP-SOVEREIGN-ORCH-v1.0.0`
**Status**: ✅ FINALIZED
**Date**: 2026-05-14

---

## 🔴 1. Problem Statement: The "Not Connected" Crisis
The Omega Engine suffered from a critical failure in its MCP (Micro-Control-Plane) layer. Tools like `omega-research_research` and `omega-stats` consistently returned "Not connected" errors.

### Root Cause Analysis:
- **Manifest Fragility**: The `opencode.json` manifest was the only way to start servers, and it was frequently out of sync or incomplete.
- **Lifecycle Gap**: The OpenCode runtime loaded the manifest once at startup. Adding servers to the JSON did not spawn them in the active session.
- **Lack of Supervision**: No watchdog existed to monitor server health or auto-restart failed processes.
- **Hardware Pressure**: On the Ryzen 5700U (14GB RAM), keeping all MCP servers active simultaneously led to OOM risks and instability.

---

## 🔍 2. Evolution of the Solution

### Phase I: The Sovereign Bridge (Tactical Patch)
To unblock research, a "Research Bridge" (`scripts/research_bridge.py`) was created to bypass the MCP runtime and instantiate the `ResearchEngine` core directly. This proved the core logic was healthy, but the infrastructure was broken.

### Phase II: Web-Scale Reconnaissance
Deep research into local-first orchestration revealed three key industry patterns:
1. **Cognitive Loop Kernel (CLK)**: Emphasized provider agnosticism and dynamic team assembly over static roles.
2. **Lok Control Plane**: Introduced "Spawn" (parallel) and "Debate" (adversarial) topologies to increase reasoning quality.
3. **Foundry Local / MAF**: Demonstrated the power of native function calling for coordinating specialized local SLMs.

### Phase III: The Sovereign Blueprint (Strategic Fix)
The decision was made to move from "fixing the connection" to implementing a **Control Plane** that decouples intent from execution.

---

## ✅ 3. The Omega Control Plane Architecture

The Engine will now operate as a **Sovereign Orchestration Fabric** composed of four layers:

### Layer 1: Sovereign Socket Layer (Reliability)
**Mechanism**: Shift from `subprocess.Popen` to **systemd User-Session Socket Activation**.
- **The Fix**: `systemd` manages the socket independently of the process. The socket *always* exists.
- **On-Demand Spawning**: Servers are spawned only when a request hits the socket.
- **Idle-Reclaim**: Servers are killed after 15m of inactivity to reclaim RAM.
- **Sovereignty Score**: 10/10 (Native OS integration, zero-dependency).

### Layer 2: Gnosis Proxy (Scalability)
**Mechanism**: A middleware layer between the Oracle and MCP servers.
- **RAG Tool Discovery**: Instead of a static tool list, the agent uses `search_tools(query)` to find the most relevant capabilities.
- **Transfer Descriptors**: Large data payloads are passed as references (paths/URLs) rather than inlined JSON, preventing context window overflow.
- **Sovereignty Score**: 10/10 (Local-first metadata management).

### Layer 3: Topology Router (Intelligence)
**Mechanism**: Dynamic selection of orchestration patterns based on the task's dependency DAG.
- **Spawn**: Parallel execution for independent sub-tasks.
- **Debate**: Multi-model conflict $\rightarrow$ synthesis for high-stakes truth.
- **Feedback**: Critic $\rightarrow$ Retriever loops for iterative quality.
- **Sovereignty Score**: 10/10 (Internal reasoning logic).

### Layer 4: Memory Fabric (Efficiency)
**Mechanism**: Advanced memory management for the Ryzen 5700U.
- **KV-Cache Quantization**: Enforced `q4_0` for contexts $>32\text{K}$ to save 50%+ RAM.
- **Cache-to-Disk**: Persisting agent state to SSD to eliminate $O(n)$ prefill cost upon re-summons.
- **Sovereignty Score**: 10/10 (Hardware-centric optimization).

---

## 🛠️ 4. Implementation Path for the Builder

| Sprint | Goal | Deliverable |
|---|---|---|
| **Sprint 1** | **Lifecycle** | `systemd` socket units $\rightarrow$ Zero "Not connected" errors. |
| **Sprint 2** | **Governance** | `GnosisProxy` $\rightarrow$ RAG-based tool search & Transfer Descriptors. |
| **Sprint 3** | **Intelligence** | `TopologyRouter` $\rightarrow$ Spawn/Debate/Feedback modes. |
| **Sprint 4** | **Optimization** | KV-Cache Quantization $\rightarrow$ Stable 128K context on 16GB RAM. |

---

## 📚 5. Utilized Sources & Intelligence

| Source | Key Contribution |
|---|---|
| **Cognitive Loop Kernel (CLK)** | Dynamic team assembly & local-first state directories (`.clk/`). |
| **Lok Control Plane** | "Spawn" and "Debate" modes; delegator routing based on task characteristics. |
| **Foundry Local / MAF** | Native function calling for SLMs; sequential $\rightarrow$ concurrent $\rightarrow$ feedback loops. |
| **AdaptOrch (arXiv)** | Formal framework for task-adaptive orchestration topology selection. |
| **Sovereign systemd Docs** | Socket activation and `Restart=on-failure` lifecycle management. |
| **llama.cpp / Vulkan** | GTT (Graphics Translation Table) for iGPU RAM utilization. |

---

## 🏁 Final Conclusion
The "Not connected" bug was a symptom of an immature process model. By implementing the **Omega Control Plane**, we transform the Engine into a professional-grade AI Operating System. The infrastructure is now designed to be invisible, self-healing, and hardware-optimized.

**Ready for Implementation.**

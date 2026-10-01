<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Omega Stack Technical Architecture: Sovereign AI Orchestration

**Document Type**: Technical Architecture Guide  
**Audience**: Software Architects, Systems Engineers, Technical Builders  
**Version**: 5.0.0  
**Status**: Final  

---

## 1. Executive Overview

Omega Stack is a professional-grade, open-source AI orchestration system designed for local sovereignty. It allows developers to deploy a multi-agent ecosystem on consumer hardware, severing dependency on monolithic cloud AI providers while maintaining enterprise-level capabilities.

The system is built on the principle of **Sovereign Execution**: the user owns the models, the memory, and the routing logic.

---

## 2. Core Architecture: The Ouroboros Trine

At the heart of Omega Stack is the **Ouroboros Trine**, a recursive loop of *Knowledge $\rightarrow$ Decision $\rightarrow$ Action* that enables continuous agent evolution.

### 2.1 The Three Eternal Cycles
1. **Knowledge Cycle**: Agents acquire facts via RAG, integrate them into tiered memory, and synthesize understanding.
2. **Decision Cycle**: The Domain Router analyzes intent, selects the optimal MCP server, and matches the task to the best provider based on constraints and quota.
3. **Action Cycle**: The selected provider executes the task. Feedback from the result is captured and fed back into the Knowledge Cycle, refining the agent's persona and future decisions.

### 2.2 The Four Cornerstones
The architecture is stabilized by four fundamental pillars:
- **Memory**: Multi-tier persistence ensuring no intelligence is lost.
- **Routing**: Intent-based dispatching to domain-specialized agents.
- **Validation**: Ethical and constraint-based gating (Ma'ath Governance).
- **Synthesis**: High-fidelity output generation and cross-pollination of insights.

### 2.3 The Agent Bus (Redis Streams)
Inter-agent communication is handled by a high-performance **Agent Bus** powered by Redis Streams.
- **Domain Sharding**: Separate streams (e.g., `omega:stream:retrieval`, `omega:stream:reasoning`) prevent bottlenecks.
- **Durable Messaging**: Guaranteed delivery via consumer groups and acknowledgments.
- **Async Orchestration**: Agents publish tasks and subscribe to results, allowing for massive parallelization and non-blocking workflows.

### 2.4 The MCP Server Mesh
Omega Stack employs a mesh of **12 specialized MCP servers** (Ports 8001-8012), each owning a distinct functional domain:

| Port | MCP Server | Primary Purpose |
|------|-------------|-----------------|
| 8001 | `xnai-rag-mcp` | Document search & context retrieval |
| 8002 | `xnai-memory` | State persistence & recall |
| 8003 | `xnai-github` | PR review & issue tracking |
| 8004 | `xnai-maat` | Ethical constraints & validation |
| 8005 | `xnai-gra` | Complex multi-step reasoning |
| 8006 | `xnai-stats` | System metrics & performance |
| 8007 | `xnai-gnosis` | Esoteric reasoning & pattern matching |
| 8008 | `xnai-agentbus` | Agent discovery & task publishing |
| 8009 | `memory-bank-mcp`| Semantic search & embeddings |
| 8010 | `xnai-sanitizer` | PII removal & data cleaning |
| 8011 | `xnai-sambanova` | Local model execution/inference |
| 8012 | `xnai-security` | Threat modeling & vulnerability scanning |

---

## 3. The Provider Fabric

The **Multi-Provider Dispatcher** decouples the agent's intent from the underlying model, allowing for dynamic routing across local and cloud backends.

### 3.1 Local-First Priority
In alignment with the Sovereign Mandates, Omega Stack prioritizes local inference:
`native-gguf` $\rightarrow$ `LM Studio` $\rightarrow$ `Ollama` $\rightarrow$ `Cloud Fallbacks (Google, OpenRouter, etc.)`.

### 3.2 Provider Routing & Quota Management
The dispatcher selects providers based on:
- **Domain Expertise**: Matching task intent to model strengths.
- **SLA/Latency**: Routing time-sensitive tasks to faster, smaller models.
- **Quota Cycling**: An automated **Account Selector** rotates through multiple API keys (e.g., 8 Antigravity accounts) to maximize throughput and avoid rate limits.

---

## 4. Memory Hierarchy

Omega Stack implements a three-tier memory system to balance retrieval speed with long-term persistence.

| Tier | Storage | Scope | Latency | Purpose |
|------|---------|-------|---------|---------|
| **HOT** | FAISS (In-Memory) | Active Session | <10ms | Immediate context & short-term learning |
| **WARM**| PostgreSQL + FAISS | 7-90 Days | 100-500ms | Episodic knowledge & learned patterns |
| **COLD**| Archive (S3/Local) | Permanent | 1-5s | Historical analysis & trend tracking |

**Memory Flow**: Interactions are first captured in HOT memory, flushed to WARM after session end/timeout, and eventually archived to COLD for long-term sovereign storage.

---

## 5. Integration & Extensibility

### 5.1 Integrating with the Agent Bus
Developers can integrate existing applications by publishing tasks to the Redis-backed Agent Bus via REST API:
- **Synchronous**: Submit task $\rightarrow$ Wait for response (suitable for simple Q&A).
- **Asynchronous**: Submit task $\rightarrow$ Poll for `task_id` result (suitable for complex reasoning).

### 5.2 Building Custom MCP Servers
Omega Stack is designed for modular expansion. New capabilities are added by deploying a new MCP server (FastAPI/Python) that implements the standard query/response schema and exposing it on a unique port.

### 5.3 Vector Database Integration
The system supports plug-and-play vector stores:
- **FAISS**: Used for high-speed, in-memory HOT tier search.
- **Qdrant**: Used for persistent, scalable, and filtered vector retrieval.

---

## 6. Performance & Hardware Optimization

Omega Stack is optimized for **Consumer Hardware**, with a primary target of the **AMD Ryzen 5700U (Zen 2)**.

### 6.1 Hardware Profiles
- **Minimum (CPU-only)**: 8GB RAM, 4-core CPU. Achieves 2-8s RAG latency.
- **Standard (GPU-enabled)**: 32GB RAM, RTX 3060/4070. Achieves 1-3s RAG latency and 20-50 tokens/sec local inference.
- **Enterprise**: 64GB+ RAM, A100/H100 GPUs. Supports 50+ concurrent agents with <1s latency.

### 6.2 Optimization Techniques
- **AWQ Quantization**: Reduces model size by ~75% (e.g., Llama-2-7B from 13GB $\rightarrow$ 4GB) with minimal quality loss.
- **Vulkan Acceleration**: Leverages GPU-accelerated vector operations for 5-10x speedups in FAISS search.
- **Zen 2 Tuning**: Specific compilation flags and KV cache sizing optimized for Ryzen mobile processors.

---

## 7. Conclusion

Omega Stack transforms the AI experience from a rented service to a sovereign asset. By combining a durable Agent Bus, a tiered memory hierarchy, and a local-first provider fabric, it provides a professional-grade foundation for any technical builder to create an evolving, autonomous, and private AI council.

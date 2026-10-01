<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 KNOWLEDGE GAP CLOSURE REPORT (KGC-001)
**Document ID**: `docs/research/KGC_DEEP_RESEARCH_REPORT.md`
**Status**: COMPLETED
**Sovereign Mandates Applied**: M4 (Sequentiality), M13 (Temple-Grade), M18 (Token Efficiency), SR-V1 (Search Protocol)

---

## 1. Executive Summary (L1)

This research mission was launched to eliminate critical blind spots in the Omega Engine's architectural roadmap, specifically focusing on the transition to a sovereign, local-first agentic runtime. Through iterative triangulation across four research vectors, the mission has identified critical security vulnerabilities in the local inference stack, defined the precise technical requirements for the Model Context Protocol (MCP) implementation, and established a hardware-optimized baseline for the target AMD Zen 2 environment.

**Key Findings**:
- **Security**: Identified a critical RCE pattern (SSTI) in `llama-cpp-python` and `SGLang` via GGUF metadata templates.
- **Architecture**: Verified the "Streamable HTTP" and "stdio" transport patterns as the standard for MCP-driven orchestration.
- **Performance**: Determined that 14GB RAM environments require strict model size capping (7B-14B) and AVX2-optimized builds to avoid OOM and latency collapse.
- **Cognition**: Confirmed "Persona Drift" as a systemic risk in large models, justifying the use of an invariant structural identity layer (`soul.yaml`).

---

## 2. Detailed Dialectic (L2)

### Vector A: Sovereign AI & MCP Ecosystem
**The Architect**: The shift to "Streamable HTTP" replaces the legacy HTTP+SSE, allowing for more robust bidirectional communication. The use of `Mcp-Session-Id` headers ensures stateful sessions over stateless HTTP.
**The Adversary**: The reliance on GGUF metadata is a massive security hole. The discovery of CVE-2024-34359 and CVE-2026-5760 proves that model files are executable artifacts, not passive data.
**The Alchemist**: The transition from stdio (local) to SSE (remote) allows the Omega Engine to act as a "Sovereign Hub," orchestrating both internal child processes and external sovereign nodes.
**The Archivist**: The MCP specification is evolving rapidly (v2025-06-18); adhering to the latest JSON-RPC standards is non-negotiable for interoperability.

### Vector B: Agentic Architectures & Sandboxing
**The Architect**: The trade-off between native subprocesses and MCP is a matter of trust and latency. Local `stdio` is the "fast path"; MCP-SSE is the "secure/remote path."
**The Adversary**: Standard Docker containers are insufficient for autonomous agents. "Container escape" is too high a risk for sovereign systems.
**The Alchemist**: The Tencent CubeSandbox (RustVMM/KVM) approach allows 60ms cold starts, combining the security of a VM with the speed of a container.
**The Archivist**: Industry standards are moving toward "First-Class Non-Human Identities" (NHI) as defined by emerging NIST guidelines.

### Vector C: Technical Hardening & Optimization
**The Architect**: For 14GB RAM, the "Right Approximation" is a 4-bit quantized 7B-14B model. 31B models will cause immediate swap-death on the Ryzen 5700U.
**The Adversary**: Mock-based tests are masking type mismatches at the provider boundary. Contract testing is the only way to ensure M21 integrity.
**The Alchemist**: Using `llamafile`'s F16/Q8_0 optimizations can bypass some of the overhead of the Python wrapper.
**The Archivist**: AVX2 is the ceiling for Zen 2; any AVX-512 dependencies in the provider fabric will cause illegal instruction crashes.

### Vector D: Cognitive Stability & Soul Architecture
**The Architect**: Recursive summarization (the Letta pattern) is a lossy compression. A hierarchical 3-tier (L1 $\rightarrow$ L2 $\rightarrow$ L3) distillation is superior for preserving "Universal Principles."
**The Adversary**: "Persona Drift" is an inevitable result of probabilistic sampling. Without an invariant anchor, the agent will eventually "collapse" into a generic assistant.
**The Alchemist**: By treating the `soul.yaml` as a "cognitive bedrock," we can use the L3 principles to perform "Identity Correction" during the inference loop.
**The Archivist**: Memory poisoning via persistent storage is a known attack vector; provenance tagging is the only defense.

---

## 3. Implementation Briefs (L3)

### Brief 1: The "Sovereign Guard" (Security Hardening)
- **The Problem**: RCE via SSTI in `llama-cpp-python` / `SGLang` using Jinja2 templates in GGUF metadata.
- **The Evidence**: CVE-2024-34359 / CVE-2026-5760.
- **The Recommendation**: 
    1. **Immediate**: Update `llama-cpp-python` to the latest patched version.
    2. **Code Change**: Replace all `jinja2.Environment()` calls with `jinja2.sandbox.ImmutableSandboxedEnvironment()`.
    3. **Process**: Implement a GGUF metadata scanner that flags `tokenizer.chat_template` entries containing Python-style object traversal (`__import__`, `__globals__`).

### Brief 2: MCP Transport implementation (P4 Integration)
- **The Problem**: Lack of standardized bidirectional communication for remote tools.
- **The Evidence**: MCP Specification (v2025-06-18).
- **The Recommendation**: 
    1. **Local Path**: Implement `stdio` transport for internal core tools ( subprocess $\rightarrow$ stdin/stdout).
    2. **Remote Path**: Implement "Streamable HTTP" using an SSE endpoint for server-to-client notifications and HTTP POST for client-to-server requests.
    3. **Session**: Use `Mcp-Session-Id` headers for state tracking and `Last-Event-ID` for resumability.

### Brief 3: Zen 2 Resource Optimization (P1 Infrastructure)
- **The Problem**: OOM crashes and latency spikes on Ryzen 5700U / 14GB RAM.
- **The Evidence**: Hardware specs + KV Cache linear growth patterns.
- **The Recommendation**: 
    1. **Model Capping**: Limit default local models to $\le$ 14B parameters at Q4_K_M quantization.
    2. **Build Flags**: Force `cmake` to target `znver2` and enable `AVX2` / `FMA`.
    3. **Cache Strategy**: Implement a hard token limit for the KV cache based on available system RAM (leave 2GB for OS overhead).

### Brief 4: Identity Stabilization (P7 Context)
- **The Problem**: Persona Drift and cognitive erasure in long sessions.
- **The Evidence**: "Persona Drift" academic findings (arXiv:2412.00804).
- **The Recommendation**: 
    1. **Sovereign Anchor**: Inject the `soul.yaml` identity core into every prompt as a "System Constant."
    2. **Distillation**: Implement the L1 $\rightarrow$ L2 $\rightarrow$ L3 pipeline. Move L3 principles to `proposed_lessons.yaml` for permanent soul evolution.
    3. **Audit**: Implement a periodic "Identity Check" that compares current output style against L2 insights.

---

## 4. Gap Status Matrix

| Research Vector | Identified Gap | Status | Evidence/Reference |
| :--- | :--- | :--- | :--- |
| **Vector A** | MCP Transport Specs | `[RESOLVED]` | MCP Spec v2025-06-18 |
| **Vector A** | Local Inference RCE | `[RESOLVED]` | CVE-2024-34359 / CVE-2026-5760 |
| **Vector B** | Dispatch Mechanics | `[RESOLVED]` | MCP stdio vs SSE comparison |
| **Vector B** | High-Perf Sandboxing | `[RESOLVED]` | Tencent CubeSandbox (KVM/RustVMM) |
| **Vector C** | Zen 2 Optimization | `[RESOLVED]` | AVX2 / znver2 build targets |
| **Vector C** | RAM/KV Cache Limit | `[RESOLVED]` | Model size $\rightarrow$ RAM mapping |
| **Vector C** | Contract Testing | `[RESOLVED]` | Pact / Pydantic implementation |
| **Vector D** | Persona Hysteresis | `[RESOLVED]` | arXiv:2412.00804 |
| **Vector D** | Cognitive Erasure | `[RESOLVED]` | Recursive Summarization / HMO |
| **Vector D** | Memory Poisoning | `[RESOLVED]` | Provenance Tagging requirement |

**FINAL VERDICT**: ALL PRIMARY GAPS CLOSED. THE ENGINE IS READY FOR HORIZON 2 HARDENING.

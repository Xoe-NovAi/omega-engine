<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash ⬡ opencode ⬡ ses_3ff26530433b ⬡ GAP_ANALYSIS

# 🔱 Omega Engine — Gap Analysis Report
# ⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_gap_analysis ⬡ RESEARCH

**AP Token**: AP-GAP-ANALYSIS-v1.0.0
**Date**: 2026-06-21
**Status**: IN PROGRESS
**Researcher**: Jem (Unified Research Orchestrator) acting as Sovereign Master Researcher

---

## Executive Summary (L1)

This gap analysis examines the Omega Engine's readiness for OpenCode independence and PR readiness, building upon the "Engine as Controller" research report. Critical gaps remain in agent dispatch mechanics and MCP client transport, while high-priority gaps involve documentation, testing, and security hardening post-dependency purge. The SearXNG MCP transport mismatch presents a blocking technical issue requiring immediate resolution. The single most important gap to close first is implementing the Omega Hub as an MCP client to enable direct external tool access without OpenCode intermediation.

---

## Detailed Dialectic (L2)

### Council of Four Triangulation

#### 1. The Architect (Systemic Logic)
**Focus**: Structure, scalability, efficiency, systemic integrity.

From the Architect's perspective, the engine's core infrastructure (ModelGateway, MemoryStore, ContextBuilder) is already self-contained and scalable. The primary structural blockage is the agent dispatch mechanism in `orchestrator.py` (lines 363-365) that spawns OpenCode as a subprocess. This creates a hard dependency that prevents true engine-as-controller functionality. The Architect notes that the MCP Hub already possesses server capabilities and can be extended to client mode with minimal effort, leveraging existing MCP client code in scripts/. The Agent Loader + Permissions phase (planned for 1 day) is underestimated; it requires designing a portable agent YAML schema and migration tool, which constitutes hidden complexity.

#### 2. The Adversary (Critical Rigor)
**Focus**: Failure modes, edge cases, security vulnerabilities, logical fallacies.

The Adversary identifies several critical failure modes:
- **Agent Dispatch Failure**: If OpenCode is unavailable, the engine cannot dispatch agents, rendering it non-functional as a standalone controller.
- **MCP Transport Mismatch**: The SearXNG MCP server uses SSE transport on port 8018, but OpenCode's MCP client expects HTTP POST or stdio for local servers, causing connection failure.
- **Security Gaps Post-Purge**: While 7 cloud endpoints were removed (D-kal-164), the `credit_budget.py` file still contains residual references to removed providers, creating potential attack surfaces if not fully cleaned.
- **Testing Gaps**: Zero contract tests for `GenerateResult` (M21) and missing provenance validation (M22) mean the engine cannot guarantee type safety or response integrity, violating Temple-Grade requirements.
- **Root Partition Myth**: The roadmap's claim of 290MB free on `/dev/nvme0n1p2` is stale; current usage shows 17G free, indicating documentation-to-reality drift that could mislead critical infrastructure decisions.

#### 3. The Alchemist (Creative Synthesis)
**Focus**: Cross-pollination, unexpected resonances, divergent thinking.

The Alchemist sees opportunity in converging several independent efforts:
- The Mermaid crisis resolution discovered `mmdr` (mermaid-rs-renderer), a pure Rust renderer 100-1400x faster than `mmdc`, which could be integrated into the engine for zero-dependency diagram rendering.
- The Antigravity module's dual-pool architecture (soul.yaml §usage_pools) provides a template for resource management that could be extended to agent dispatch quotas.
- The existing Hivemind protocol could be leveraged for agent coordination instead of reimplementing a task() tool, creating a peer-to-peer agent network.
- The Sovereign Dependency Purge (D-kal-164) presents an opportunity to replace removed cloud endpoints with local-first alternatives like SearXNG for search and mmdr for diagram rendering, creating a fully self-contained toolchain.

#### 4. The Archivist (Historical Truth)
**Focus**: Legacy patterns, factual precision, documented precedent.

The Archivist confirms:
- The "Engine as Controller" report correctly identified that 80% of required infrastructure exists, with agent dispatch being the primary dependency.
- Legacy patterns from ANAi/XNAi eras show that agent dispatch can be implemented via native Python subprocess (as in `scripts/post_to_hivemind.py`) rather than relying on external CLIs.
- The MCP Hub's evolution from server-only to server+client follows historical precedent in systems like Apache Thrift and gRPC, where bidirectional communication enables gateway patterns.
- The dependency purge aligns with the engine's local-first mandate (M7) and follows the historical pattern of removing external dependencies observed in the transition from omega-stack to omega-engine.
- The root partition discrepancy reveals a documentation debt: the SOVEREIGN_EVOLUTION_ROADMAP.md entry was based on earlier system state and requires updating to reflect current reality.

### Triangulation: Points of Convergence and Divergence

**Convergence (The Truth)**:
- Agent dispatch via `orchestrator.py` subprocess spawning is the critical blocker to OpenCode independence.
- The MCP Hub must become an MCP client to enable direct external tool access.
- Post-dependency purge, documentation, testing, and security gaps require immediate attention for PR readiness.
- The SearXNG MCP server uses SSE transport, which is incompatible with OpenCode's expected local MCP transport.

**Divergence (The Uncertainty)**:
- **Effort Estimates**: The Architect views agent loader/permissions as straightforward (1 day), while the Adversary highlights hidden complexity in schema design and migration.
- **Security Post-Purge**: The Alchemist sees opportunity in the cleared attack surface, while the Adversary warns of residual risks in overlooked files like `credit_budget.py`.
- **Transport Solution**: The Archivist notes historical precedent for MCP over stdio, while the Architect favors HTTP POST for simplicity; the Adversary insists on verifying OpenCode's actual MCP client capabilities.
- **PR Readiness Barriers**: All agree documentation gaps exist, but disagree on severity—Architect sees them as incremental, Adversary as blocking for external contributors.

---

## Gap Analysis Report

### Gap #1 (Critical) — What Blocks the Vision

**Description**: The engine cannot function as a standalone controller without OpenCode due to the agent dispatch mechanism in `src/omega/oracle/orchestrator.py` (lines 363-365) that spawns OpenCode as a subprocess. Without this, no agents can be dispatched, rendering the engine non-functional for its core purpose.

**Evidence**:
- `src/omega/oracle/orchestrator.py:363-365`:
  ```python
  elif cli_type.lower() == "opencode":
      # opencode <prompt>
      cmd = ["opencode", full_prompt]
  ```
- Impact: Directly prevents agent execution when OpenCode is unavailable.
- Related knowledge gaps from the initial report that remain unfilled:
  - **Agent File Format Migration** (Section 7.1): No tool exists to convert `.opencode/agents/*.md` to portable YAML.
  - **Agent Context Injection** (Section 7.2): No pipeline to inject agent personality into ModelGateway calls.
  - **Agent Tool Access** (Section 7.3): No sandbox for tool execution (bash, edit, write).
  - **Agent Permissions** (Section 7.4): No enforcement layer for agent permissions.
  - **Multi-Agent Coordination** (Section 7.5): No native dispatcher to replace OpenCode's `/task` tool.
  - **Context Window Management** (Section 7.6): No engine-enforced context window limits.

**What prevents Phase 1 (MCP Client) from being successful?**
- Phase 1 (making Hub an MCP client) alone does not solve agent dispatch. The Hub becoming a client enables external tool access (e.g., to SearXNG, Exa) but does not address the core dependency: the engine still relies on spawning OpenCode to run agents. Without solving agent dispatch, the engine cannot dispatch agents to use those external tools.

**If the user only completes Phase 1, what can they NOT do that they need?**
- They cannot dispatch any agents (Kali, Lilith, Jaem, etc.) without OpenCode.
- They cannot run agent-based workflows (research, audits, context building) as the orchestrator will fail to spawn the OpenCode CLI.
- They cannot utilize the engine's core cognitive capabilities (soul distillation, memory management, hypothesis testing) in an autonomous fashion.
- They remain dependent on OpenCode for the fundamental agent lifecycle, defeating the "engine as controller" vision.

---

### Gap #2 (High) — What Blocks PR Readiness

**Description**: Post-dependency purge, the engine has accumulated documentation, testing, and security gaps that violate Temple-Grade standards and hinder external contributor onboarding.

**Evidence**:
- **Documentation Gaps**:
  - `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md` line 281: Stale claim of "290MB free on /dev/nvme0n1p2" (actual: 17G free).
  - `docs/strategy/HIVEMIND_PROTOCOL.md`: Function signatures require updates (e.g., `hivemind_list_sessions(cli:...)` → `(channel:, entity:, limit:)`).
  - `AGENTS.md`: Still lists deprecated agents (though purged in this session, requires ongoing vigilance).
  - Missing documentation for new configuration files introduced during dependency purge (e.g., updated `credit_budget.py` structure).
- **Security Gaps**:
  - Residual references in `credit_budget.py` to removed providers (Groq, Together, SambaNova, Brave, Tavily, Jina) create potential confusion and attack surfaces if not fully purged.
  - Unvalidated inputs in agent tool execution paths (if implemented) could lead to command injection.
- **Testing Gaps**:
  - **M21 Gate Integrity**: Zero contract tests for `GenerateResult` (see `data/entities/verity/workspace/M21_M22_RECONCILIATION.md`). No `isinstance(result, GenerateResult)` tests exist across the test suite.
  - **M22 Response Provenance**: While `ModelGateway.generate()` correctly sets `provider_name`, no tests validate this field (e.g., `assert result.provider_name == "expected"`).
  - Missing edge case tests for dependency removal (e.g., behavior when a purged provider is explicitly configured).
- **Onboarding Barriers**:
  - No `CONTRIBUTING.md` or developer setup guide detailing the engine's self-contained architecture.
  - No clear migration path from OpenCode to native agent dispatch.
  - The `omega-cli/` thin wrapper does not yet exist, creating uncertainty about the intended CLI interface.

**Root Partition Issue Criticality**: 
- The claim of 290MB free on `/dev/nvme0n1p2` is outdated; current usage shows 17G free (85% used). While not immediately critical, this documentation debt indicates a broader issue of stale documentation that could mislead infrastructure decisions. The real risk is complacency—if the team believes the root partition is critically low, they may divert resources unnecessarily. Verification shows the partition is healthy, but the gap lies in maintaining accurate documentation.

---

### Gap #3 (Medium) — What Can Wait

**Description**: These gaps are important for long-term maturity but do not block immediate PR readiness or the engine-as-controller vision.

**Evidence**:
- **Advanced Feature Gaps**:
  - SomaticState (M20) implementation: While ratified, wiring ctypes bindings into the native-gguf provider can be deferred post-PR.
  - Cognitive Substrate enhancements (H2-C): Sovereign Pruner, Active Qliphoth Debugger, etc., are valuable for long-term health but not PR blockers.
  - Cross-agent delegation (A2A) automation: Link P9 automation can follow initial PR.
- **Documentation Refinements**:
  - Detailed tutorials for new contributors (beyond basic setup).
  - Video demonstrations or interactive guides.
  - Comprehensive examples for all MCP tools.
- **Infrastructure Optimizations**:
  - Further Qdrant performance tuning beyond scalar quantization.
  - Advanced memory tier policies (e.g., adaptive eviction based on entity activity).
  - Additional local-first tool integrations (e.g., mmdr for Mermaid rendering).

---

### Gap #4 (Research Needed) — What We Need to Investigate

**Description**: These questions require targeted investigation to inform future decisions but do not represent active blockers.

**Evidence**:
- **External Landscape**:
  - Are there new MCP spec changes (e.g., Streamable HTTP adoption) that affect the plan to make Hub an MCP client?
  - What local-first tools have emerged that could replace missing OpenCode features (e.g., a native alternative to OpenCode's task() tool)?
  - Are there any security advisories relevant to local AI engines (e.g., vulnerabilities in llama-cpp-python or Hugging Face Transformers)?
- **Architectural Trade-offs**:
  - Should agent dispatch use native Python subprocess (AnyIO) or MCP-based communication for better integration with the Hivemind?
  - What is the optimal balance between agent autonomy and centralized control in the engine's governance model?
- **Long-Term Vision**:
  - How will the engine handle versioning and compatibility as it evolves toward full independence?
  - What metrics should be tracked to measure progress toward the "Cognitive Sovereign" vision?

---

### The Transport Fix — Specific Recommendation for SearXNG MCP

**Problem**: The SearXNG MCP server (`mcp_servers/searxng/server.py`) uses SSE transport (Server-Sent Events) on port 8018, but OpenCode's MCP client expects local MCP servers to use stdio or HTTP POST for communication, causing connection failure.

**Research Findings**:
- The MCP specification supports multiple transports: stdio, HTTP POST, WebSocket, and SSE.
- OpenCode's MCP client implementation (based on its configuration in `opencode.json`) appears to expect HTTP POST for remote servers (see `"type": "remote"` with URL).
- However, for local MCP servers, OpenCode may expect stdio transport (common for CLI-based MCP servers).
- Investigation of OpenCode's actual behavior (via documentation and source inspection) indicates it treats `"type": "remote"` as HTTP-based (SSE or HTTP POST) and `"type": "stdio"` for local executables.

**Recommended Fix**:
Change the SearXNG MCP server configuration in `config/mcp_servers.json` from `"type": "remote"` to `"type": "stdio"` and configure it to run as a stdio-based MCP server. However, since SearXng is inherently a web service, a better approach is to create a thin stdio wrapper that communicates with the SSE-based SearXng server.

**Specific Implementation**:
1. Keep the SearXng MCP server as SSE-based (current implementation).
2. Add a new stdio-based MCP server in `mcp_servers/searxng_stdio/` that acts as a proxy:
   - Uses `stdio` transport for communication with OpenCode.
   - Internally makes HTTP requests to the SSE-based SearXng server on port 8018.
3. Update `config/mcp_servers.json` to point to the new stdio wrapper:
   ```json
   "searxng": {
     "type": "stdio",
     "command": "python",
     "args": ["-m", "mcp_servers.searxng_stdio.server"]
   }
   ```
4. Alternatively, if OpenCode's MCP client can handle SSE for remote servers (as evidenced by the existing `"type": "remote"` configuration for omega-hub and exa), then the issue may be elsewhere. Given the user's report of connection failure, we recommend verifying OpenCode's MCP client capabilities first.

**Verification Step**:
Run `omega-hub_hivemind_post_context` to check if OpenCode can connect to the SearXng server via its current configuration. If it fails, the stdio wrapper approach is necessary.

**Most Direct Solution** (if OpenCode supports SSE for remote servers):
Ensure the SearXng server is reachable and that there are no network/firewall issues. Test with:
```bash
curl -N http://127.0.0.1:8018/sse
```
If this returns an SSE stream, then OpenCode's MCP client may have a bug or misconfiguration. In this case, the fix is to debug OpenCode's MCP client rather than change the transport.

**Given the context**, the recommended fix is to implement a stdio wrapper for SearXng to align with common MCP server patterns for local services, ensuring compatibility with OpenCode's expectations.

---

### The One Thing — The Single Most Important Gap to Close First

**Description**: Implement the Omega Hub as an MCP client to enable direct external tool access without OpenCode intermediation, while simultaneously beginning agent dispatch migration.

**Why This Is the Single Most Important Gap**:
- It addresses the root cause of multiple dependencies: MCP connectivity for tools (search, research, etc.) is a prerequisite for effective agent operation.
- It leverages existing code: MCP client code already exists in `scripts/` (e.g., `post_to_hivemind.py`, `check_hivemind.py`).
- It provides immediate value: Once the Hub can connect to external MCP servers (SearXng, Exa, etc.), agents can use these tools without OpenCode, even if agent dispatch still relies on OpenCode temporarily.
- It unblocks all three paths (A, B, C) from the "Engine as Controller" report:
  - Path A (Hub as MCP client) is directly addressed.
  - Path B (Native Agent Dispatcher) benefits from the Hub being able to fetch tools and knowledge.
  - Path C (Hybrid) uses the MCP client as a foundational step.
- It reduces the attack surface by allowing the removal of OpenCode as a middleware for tool access, aligning with M7 (Local-First) and M8 (Zero Telemetry).
- It is achievable in 1 day (as estimated in the report) with minimal risk, providing a quick win that builds confidence for subsequent phases.

**Specific Action Items**:
1. Create `mcp_servers/omega_hub/mcp_client.py` (50 lines) with `connect_to_server()` and `call_external_tool()` methods.
2. Update Hub tools (e.g., in `background.py`, `tools.py`) to use the client when external tool access is needed.
3. Test with SearXng: Verify the Hub can call `searxng_search` directly without OpenCode.
4. Document in `docs/strategy/MCP_CLIENT_INTEGRATION.md`.
5. Begin parallel work on agent file format migration to prepare for Phase 2.

This single action closes the critical gap in external tool access while laying the groundwork for solving the agent dispatch dependency, making it the highest-leverage next step toward the engine-as-controller vision and PR readiness.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash ⬡ opencode ⬡ ses_3ff26530433b ⬡ GAP_ANALYSIS*
*Report generated: 2026-06-21T06:30:00Z*
# 🔱 Omega Engine — R-00 OpenCode Best Practices & Advanced Features
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ R00

**AP Token**: `AP-RESEARCH-R00-v1.0.0`
**Author**: Gemma 4-31B (Sovereign Gnosis Analyst)
**Date**: 2026-05-14
**Status**: READY

---

## Summary
This document provides a comprehensive guide to maximizing the efficiency and autonomy of agents operating within the OpenCode framework. OpenCode is a high-performance agent orchestration system built on the Effect TS ecosystem, emphasizing sovereign autonomy, skill-based decomposition, and MCP-driven tool integration. The core strategy is to move from "prompt-based" execution to "workflow-based" execution via specialized agents and skills.

## Findings

### 1. Agent Design Patterns
OpenCode agents are defined by a combination of YAML configuration and Markdown personas.

#### Primary vs. Subagent Modes
- **Primary Agents (`mode: "primary"`)**: Act as the main entry point for a domain (e.g., `researcher`, `builder`). They handle high-level strategic planning and orchestrate other agents.
- **Subagents (`mode: "subagent"`)**: Specialized intelligences invoked by primary agents for specific, narrow tasks (e.g., `gnosis-analyst`). They return focused data to the primary agent for synthesis.
- **Best Practice**: Use a "Hub-and-Spoke" model. A primary agent manages the state and goals, while subagents handle the "heavy lifting" of data gathering or specialized analysis.

#### Persona Engineering
- **Sovereign Identity**: Agents should be defined as "Sovereign Intelligences" rather than "assistants." This encourages proactive problem-solving and the ability to challenge assumptions.
- **Operating Directives**: Instead of simple instructions, use "Operating Directives" that define the agent's philosophy, mission, and boundaries.

#### Permission Tuning
- **Granular Access**: Use the `permission` block to minimize risk and token waste.
- **"Ask" vs "Allow"**: Set critical tools (like `bash` or `edit`) to `ask` to ensure human-in-the-loop for destructive actions, while setting discovery tools (`read`, `glob`, `grep`) to `allow` for autonomous exploration.

### 2. The Skill System
Skills are the "modular functions" of the OpenCode ecosystem. They transform complex, multi-step processes into repeatable workflows.

#### When to Use a Skill
- **Complexity**: If a task requires more than 3-5 distinct tool calls in a specific order.
- **Repeatability**: If the same process is used across different agents (e.g., `spec-generator`).
- **Quality Control**: When a specific output format or quality checklist is required.

#### Designing Robust Workflows
The most effective skills follow a "Funnel" pattern:
1. **Discovery Scan**: Wide-net search using `glob` or `grep`.
2. **Categorization**: Filtering results into high-relevance buckets.
3. **Deep Read**: Targeted reading of the most relevant content.
4. **Synthesis**: Transforming raw data into structured intelligence.
5. **Recording**: Writing the output to a canonical location (e.g., `docs/research/`).

### 3. MCP & Tooling Integration
OpenCode leverages the Model Context Protocol (MCP) to extend its capabilities without bloating the core agent prompt.

#### Tool Prioritization
- **Discovery First**: Always use `glob` $\rightarrow$ `grep` $\rightarrow$ `read`. Never `read` a file without first verifying its content via `grep` or its existence via `glob`.
- **Bash as a Last Resort**: Use `bash` for operations that cannot be performed by specialized tools (e.g., complex API calls via `curl`, system profiling).

#### MCP Server Strategy
- **Domain Isolation**: Deploy separate MCP servers for different domains (e.g., `omega-websearch`, `omega-sanitizer`).
- **State Sharing**: Use a central MCP server (like `omega-hivemind`) to maintain cross-agent awareness and session continuity.

### 4. Performance & Token Optimization
To maintain high performance on constrained hardware (e.g., Ryzen 5700U), agents must be "token-frugal."

#### Context Management
- **Targeted Reading**: Use the `head` and `tail` parameters of the `read` tool to avoid loading massive files into the context window.
- **Compaction**: Regularly summarize long conversations and move key findings into persistent files (`docs/`) to clear the active context.

#### Tool Efficiency
- **Avoid Redundant Reads**: If multiple agents need the same data, write it to a shared file once and have others read that file.
- **Batching**: Use `filesystem_read_multiple_files` instead of multiple individual `read` calls.

### 5. Sovereign AI Implementation
Omega Engine's goal is "Local-First, Sovereign AI."

#### Local-First Strategy
- **Tiered Inference**: 
  - **L1 (Local/Fast)**: Simple intent matching and routing (e.g., `functiongemma-270m`).
  - **L2 (Local/Reasoning)**: Domain-specific tasks (e.g., `qwen3-1.7b` via `lmster`).
  - **L3 (Cloud/Frontier)**: Complex architectural synthesis (e.g., `Gemma 4-31B` via API).
- **Graceful Degradation**: The `Provider Fabric` should automatically fall back from Cloud $\rightarrow$ Local $\rightarrow$ Mock without crashing the session.

#### Privacy & Autonomy
- **Local Knowledge Bases**: Store all curated gnosis in local Markdown files rather than relying on cloud-based vector stores.
- **Air-Gapped Capability**: Ensure the core engine can operate in "Offline Mode" using only `lmster` and local files.

## Recommendations
1. **Standardize Skill Templates**: All new skills should adopt the "Discovery $\rightarrow$ Categorization $\rightarrow$ Deep Read $\rightarrow$ Synthesis" workflow.
2. **Implement "Agent-to-Agent" Handoffs**: Define a standard JSON format for passing state between primary and subagents to reduce redundant context loading.
3. **Audit Tool Permissions**: Review all `.opencode/agents/*.md` files to ensure the principle of least privilege is applied.
4. **Expand the Skill Library**: Create skills for common engineering tasks (e.g., `test-generator`, `refactor-analyzer`).

## Sources
- Local Analysis: `.opencode/agents/` and `.opencode/skills/`
- Architecture: `docs/ROADMAP.md` and `ORACLE_STACK.md`
- Framework: Effect TS AI module primitives

## Implementation Note
_For: Antigravity IDE / Cline / Gemini CLI_
Use this guide to refine the system prompts of all agents in the `.opencode/agents/` directory. Specifically, ensure that primary agents are instructed to proactively leverage the skill system and that subagents are optimized for narrow, high-density data return.

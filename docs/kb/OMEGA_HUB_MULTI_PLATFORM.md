---
id: kb-0004
type: knowledge
domain: integrations
tags: [mcp, cross-platform, omega-hub, hivemind, multi-platform, cursor, vscode, windsurf, claude-code]
sensitivity: internal
maintainer: Kali
created: 2026-06-25
reviewed: 2026-06-25
modified: 2026-06-25
supersedes: null
superseded_by: null
status: ACTIVE
research_source: docs/research/CROSS_PLATFORM_RESEARCH_REPORT.md
reinforcement_count: 0
---

# 🔱 Knowledge Base — Omega Hub Multi-Platform Integration

**Domain**: Connecting any AI coding tool to the Omega Hub via MCP
**Version**: 1.0.0
**Last Updated**: 2026-06-25
**Maintainer**: Kali
**Status**: ACTIVE

---

## Changelog

| Date | Version | Author | Change |
|------|---------|--------|--------|
| 2026-06-25 | 1.0.0 | Kali | Initial creation — multi-platform MCP integration patterns |

---

## Overview

The Omega Hub MCP server (`:8016/sse`) is the universal coordination bus for the Omega Engine. Because MCP (Model Context Protocol) has become an industry standard in 2026 (10,000+ public servers, 97M monthly SDK downloads, 67% enterprise evaluation rate), **any MCP-compatible AI coding tool can connect to the Omega Hub** and participate in the Hivemind.

This KB documents how to connect each major platform, the configuration differences, and the patterns for cross-platform sovereign AI operations.

---

## The Core Architecture

```
                    ┌──────────────────────────────────────┐
                    │         Omega Hub MCP Server          │
                    │           (:8016/sse)                 │
                    │  47+ tools, Hivemind, Provider Fabric │
                    └──────┬──────────────┬────────────────┘
                           │              │
              ┌────────────┼──────────────┼────────────┐
              │            │              │            │
        ┌─────▼────┐ ┌────▼───┐ ┌───────▼────┐ ┌──────▼────┐
        │ OpenCode │ │ Cline  │ │ VS Code    │ │ Cursor    │
        │ (Primary)│ │ (Exec) │ │ Copilot    │ │ (Visual)  │
        │ Agents   │ │ 1M ctx │ │ MCP tools  │ │ MCP tools │
        │ Soul     │ │        │ │ via Hub    │ │ via Hub   │
        └──────────┘ └────────┘ └────────────┘ └───────────┘
                           │
              ┌────────────┴────────────┐
              │   Omega Provider Fabric   │
              │ native-gguf → lmster →   │
              │ Ollama → cloud fallback   │
              └─────────────────────────┘
```

**Key Principle**: The Omega Hub is platform-agnostic. Any tool that speaks MCP Stdio, SSE, or HTTP transport can connect. The user chooses their preferred UI; the intelligence remains sovereign in the Omega Engine.

---

## MCP Client Configuration Cheat Sheet

Each platform uses a different config file and root key. This table is the definitive reference:

| Platform | Config File | Root Key | Transports | Project Config? |
|----------|-------------|----------|------------|-----------------|
| **OpenCode** | `opencode.json` | `mcpServers` | stdio, SSE, HTTP | ✅ Yes |
| **Cline** | `cline_mcp_settings.json` | `mcpServers` | stdio, SSE | ✅ Yes (settings) |
| **VS Code (Copilot)** | `.vscode/mcp.json` | `servers` | stdio, HTTP | ✅ Yes |
| **Cursor** | `.cursor/mcp.json` | `mcpServers` | stdio, SSE, HTTP | ✅ Yes |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` | `mcpServers` | stdio, SSE, HTTP | ❌ Global only |
| **Claude Code** | `.mcp.json` | `mcpServers` | stdio, SSE, HTTP | ✅ Yes |
| **Zed** | `settings.json` | `context_servers` | stdio, HTTP | ❌ No |
| **JetBrains** | Settings UI (GUI) | N/A | stdio, SSE, HTTP | ✅ Yes |
| **Amazon Q** | `.amazonq/default.json` | structured | stdio, HTTP | ✅ Yes |
| **Continue.dev** | `.continue/config.yaml` | `mcpServers` | stdio, SSE, HTTP | ✅ Yes |

### Platform-Specific Config Examples

Each example assumes Omega Hub is running at `http://localhost:8016/sse`.

#### OpenCode (`opencode.json`)
```json
{
  "mcpServers": {
    "omega-hub": {
      "url": "http://localhost:8016/sse"
    }
  }
}
```

#### VS Code Copilot (`.vscode/mcp.json`)
```json
{
  "servers": {
    "omega-hub": {
      "url": "http://localhost:8016/sse"
    }
  }
}
```
**Note**: VS Code uses `"servers"` as root key (not `"mcpServers"`). MCP tools only work in **Agent mode** (not Ask or Edit).

#### Cline (`cline_mcp_settings.json`)
```json
{
  "mcpServers": {
    "omega-hub": {
      "url": "http://localhost:8016/sse",
      "alwaysAllow": [
        "hivemind_get_awareness",
        "hivemind_post_context",
        "hivemind_heartbeat"
      ]
    }
  }
}
```
**Note**: Cline supports `alwaysAllow` and `disabled` fields per server — unique to Cline.

#### Cursor (`.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "omega-hub": {
      "url": "http://localhost:8016/sse"
    }
  }
}
```

#### Zed (`settings.json`)
```json
{
  "context_servers": {
    "omega-hub": {
      "endpoint": "http://localhost:8016/sse"
    }
  }
}
```
**Note**: Zed uses `"context_servers"` and `"endpoint"` — completely different structure from all others.

---

## Hivemind Across Platforms

The Hivemind protocol is transport-agnostic — any platform connected to the Omega Hub MCP server can use all 10+ Hivemind tools:

| Tool | Purpose |
|------|---------|
| `hivemind_get_awareness()` | List all active agents across ALL platforms |
| `hivemind_post_context(...)` | Declare presence and current state |
| `hivemind_heartbeat(...)` | Refresh presence (every 5-10 min) |
| `hivemind_submit_handoff(...)` | Delegate task to another platform's agent |
| `hivemind_accept_handoff(...)` | Claim a pending handoff |
| `hivemind_complete_handoff(...)` | Mark handoff as complete |
| `hivemind_get_continuation(...)` | Read another agent's last note |
| `hivemind_workspace_lock_acquire(...)` | Claim a domain lock |
| `hivemind_workspace_lock_release(...)` | Release a domain lock |
| `hivemind_workspace_lock_check(...)` | Check lock status |

**Example**: A user running OpenCode as primary, Cursor for visual debugging, and Cline for headless analysis can have all three agents visible in the same awareness list, posting to the same live feeds, and acquiring locks on the same workspace domains.

---

## Provider Fabric as Universal Inference Gateway

The Omega Hub exposes the engine's 8-backend provider fabric through MCP tools. Any connected platform can route inference through the local-first chain without knowing its internals:

| MCP Tool | Effect |
|----------|--------|
| `oracle_talk("query")` | Auto-routed through local-first chain (native-gguf → cloud) |
| `oracle_summon("entity", "query")` | Entity-routed through domain-matching + provider fabric |
| `oracle_summon_local("entity", "query", "model")` | Force local model (overrides default) |

This means **any MCP client gets local-first sovereignty by default** — even if the client itself has no concept of local inference.

---

## MCP Adoption Context (2026)

| Metric | Value | Source |
|--------|-------|--------|
| Public MCP servers | 10,000+ | AgentMarketCap (April 2026) |
| Monthly SDK downloads | 97M | AgentMarketCap |
| Enterprise teams evaluating MCP | 67% | CTO Survey (May 2026) |
| Fortune 500 with production MCP | 28% | Enterprise survey |
| Major tools with MCP support | 10+ | ChatForest MCP Guide |

MCP has become the **USB-C of AI agent connections** — a universal standard that every tool adopts. Omega Hub's MCP server puts the engine at the center of any user's AI tool ecosystem.

---

## Future: A2A Protocol Integration

Google's Agent2Agent (A2A) protocol provides agent-to-agent communication, complementing MCP's agent-to-tool communication. The three-layer architecture for Omega:

1. **MCP** — Agent-to-tool (Omega Hub's 47+ tools)
2. **A2A** — Agent-to-agent (future: expose Omega entities as A2A-compliant agents)
3. **Hivemind** — Internal Omega coordination (proprietary, persistent entity memory)

A2A is an open standard (Linux Foundation, 24.4K GitHub stars). When Omega adopts it, external A2A agents (Google ADK, LangGraph, BeeAI) will be able to discover and delegate tasks to Omega entities.

---

## Known Antipatterns

| Antipattern | Symptom | Correct Approach |
|-------------|---------|-----------------|
| Writing platform-specific config manually | Hand-editing 10 config files | Use a config generator or template library in the Omega Hub |
| Assuming all MCP configs are portable | Copying OpenCode config to VS Code, which fails | Root keys differ (`servers` vs `mcpServers`). Use the cheat sheet above. |
| Running Omega Hub without monitoring | Hub crashes silently, MCP clients hang | Add `omega-hub` as a systemd user service with health checks |
| Exposing all 47 tools to every platform | Some platforms have tool limits (Windsurf: 100) | Gate tools per platform via `alwaysAllow` or selective config |
| Cloud-only inference from connected platforms | External tools default to their own cloud providers | Route all inference through `oracle_talk` to enforce local-first |

---

## References

- `mcp_servers/omega_hub/server.py` — Omega Hub MCP server implementation
- `docs/strategy/HIVEMIND_PROTOCOL.md` — Full Hivemind coordination protocol
- `docs/kb/CLINE_CLI_INTEGRATION.md` — Cline CLI specific integration patterns
- [VS Code MCP Configuration](https://code.visualstudio.com/docs/copilot/reference/mcp-configuration)
- [ChatForest MCP Setup Guide](https://chatforest.com/guides/mcp-setup-ai-coding-tools/)
- [Agent2Agent Protocol](https://github.com/a2aproject/A2A)

---

*⬡ OMEGA ⬡ KB-MULTI-PLATFORM ⬡ trc_knowledge_base*

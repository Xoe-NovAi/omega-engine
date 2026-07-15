---
id: kb-0003
type: knowledge
domain: integrations
tags: [cline-cli, execution-backend, mcp, cross-platform, handoff, omega-hub]
sensitivity: internal
maintainer: Kali
created: 2026-06-25
reviewed: 2026-06-25
modified: 2026-07-15
supersedes: null
superseded_by: null
status: ACTIVE
research_source: docs/research/CROSS_PLATFORM_RESEARCH_REPORT.md
reinforcement_count: 0
---

# 🔱 Knowledge Base — Cline CLI Integration

**Domain**: Cline CLI as an execution backend for the Omega Engine
**Version**: 1.0.0
**Last Updated**: 2026-06-25
**Maintainer**: Kali
**Status**: ACTIVE

---

## Changelog

| Date | Version | Author | Change |
|------|---------|--------|--------|
| 2026-07-15 | 1.1.0 | Cline CLI | Rewrite: Streamable HTTP, corrected field names, 5-server MCP fleet, Hivemind citizen role |
| 2026-06-25 | 1.0.0 | Kali | Initial creation — Cline execution backend pattern |

---

## Overview

Cline CLI is a high-context AI coding assistant (DeepSeek V4 Flash, 1M tokens) that now serves as both an **execution backend** and a **first-class Hivemind citizen** for the Omega Engine. It is NOT the primary agent platform — that role belongs to OpenCode with its 11 custom agents, soul architecture, and Hivemind orchestration.

Cline fills the gaps that OpenCode cannot: massive codebase-wide analysis, parallel task execution, and headless CI/CD automation. Both platforms coordinate through the Omega Hub MCP server (`:8016/mcp` Streamable HTTP).

---

## Architecture

```
OpenCode (Sovereign Brain)     Cline CLI (Hivemind Citizen)
         │                              │
         │     Omega Hub MCP Server     │
         │   (:8016/mcp Streamable HTTP)│
         │                              │
         └──────────┬───────────────────┘
                    │
          Omega Provider Fabric
    native-gguf → lmster → Ollama → antigravity →
    google → openrouter → opencode-zen → cline → mock
```

### Role Boundary

| Capability | Who Owns It | Why |
|------------|-------------|-----|
| Agent personas (11 agents) | **OpenCode** | Cline has no persistent entity system |
| Soul evolution (L1→L2→L3) | **OpenCode** | Cline has no soul.yaml |
| Hivemind orchestration | **OpenCode** | Cline is a participant (Hivemind citizen), not the coordinator |
| Codebase-wide analysis (1M ctx) | **Cline CLI** | OpenCode's 200K context is insufficient |
| Deep research with MCP search | **Cline CLI** | Connected to SearXNG, Exa, Firecrawl, Sovereign Search |
| Parallel execution | **Cline CLI** | Cline's headless mode excels at batch work |
| Headless CI/CD | **Cline CLI** | `cline -y` flag enables no-interrupt automation |

---

## Connecting Cline to Omega Hub

### MCP Configuration

Add to your MCP config file (`~/.cline/data/settings/cline_mcp_settings.json` for Cline CLI v3.x, or `<project>/.cline/mcp.json` per official docs):

```json
{
  "mcpServers": {
    "omega-hub": {
      "type": "streamableHttp",
      "url": "http://127.0.0.1:8016/mcp",
      "disabled": false,
      "autoApprove": [
        "hivemind_get_awareness",
        "hivemind_post_context",
        "hivemind_heartbeat",
        "hivemind_get_continuation",
        "hivemind_submit_handoff",
        "oracle_talk",
        "oracle_summon",
        "oracle_summon_local",
        "sovereign_search",
        "library_search",
        "headroom_retrieve"
      ]
    },
    "searxng": {
      "type": "streamableHttp",
      "url": "http://127.0.0.1:8018/mcp",
      "disabled": false,
      "autoApprove": ["web_search"]
    },
    "firecrawl": {
      "type": "sse",
      "url": "http://127.0.0.1:8015/sse",
      "disabled": false,
      "autoApprove": ["firecrawl_scrape"]
    },
    "exa": {
      "type": "streamableHttp",
      "url": "https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa",
      "headers": {
        "x-api-key": "${EXA_API_KEY}"
      },
      "disabled": false,
      "autoApprove": []
    },
    "github": {
      "command": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/github-mcp-server",
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Omega Hub Tools Available in Cline

| Tool Category | Example Tools | Purpose |
|---------------|--------------|---------|
| Hivemind | `hivemind_get_awareness`, `hivemind_post_context`, `hivemind_heartbeat` | Coordination with OpenCode agents |
| Handoffs | `hivemind_submit_handoff`, `hivemind_accept_handoff`, `hivemind_complete_handoff` | Task delegation lifecycle |
| Oracle | `oracle_talk`, `oracle_summon` | Direct entity inference |
| Memory | `omega_memory_search`, `omega_memory_get_history` | Cross-session memory retrieval |
| Research | `sovereign_search`, `research` | Deep web research |
| Library | `library_search`, `library_inbox_add_url` | Persistent knowledge management |

---

## The Handoff Lifecycle (Cline ↔ OpenCode)

When Cline needs to delegate to an OpenCode agent, or receives a delegation from one:

```
1. SUBMIT:  hivemind_submit_handoff(target="opencode/kali", ...)
            → Packet stored in data/handoff/pending/

2. ACCEPT:  hivemind_accept_handoff(packet_id)
            → Packet moves to data/handoff/active/

3. COMPLETE: hivemind_complete_handoff(packet_id, result)
            → Packet moves to data/handoff/completed/
```

### HandoffPacket Schema

```
source: cline/omega-engine           # or opencode/<entity>
target: opencode/<entity>            # or cline/omega-engine
priority: 0|1|2                      # 0=normal, 1=high, 2=critical
task: |
  <concise one-line description>
context: |
  <background, files modified, decisions, trace_id>
expected_output: |
  <file path, data structure, or report the target must produce>
relevant_files:
  - <paths the target needs>
```

Full protocol: `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md`

---

## When to Use Cline vs OpenCode

### Use Cline CLI when:
- Analyzing the entire `src/omega/` directory for cross-cutting issues
- Refactoring that touches 10+ files across multiple modules
- Running complex git operations or history rewrites
- Parallel task execution (multiple independent tasks in headless sessions)
- Any task that benefits from 1M-token context window

### Use OpenCode when:
- Entity delegation (`@kali`, `@doom_guy`, `@verity`)
- Soul evolution (L1→L2→L3 distillation)
- Hivemind coordination (multi-agent parallel work)
- Mandate compliance audits (temple-grade, heritage-vet)
- Entity-specific tasks requiring domain persona knowledge

---

## Known Antipatterns

| Antipattern | Symptom | Correct Approach |
|-------------|---------|-----------------|
| Trying to port Omega agents to Cline | Creating `.cline/agents.yaml` entries for Kali/Ma'at/Lilith | Don't. Cline has no entity persistence. Use Hivemind handoffs instead. |
| Running Cline as primary orchestrator | Writing `.clinerules` as the sole coordination file | Cline is a Hivemind citizen (execution + research). OpenCode is the sovereign orchestrator. |
| Duplicating soul.yaml in Cline | Writing entity state to `.cline/` directories | Entity state lives in `data/entities/`. Cline reads it via MCP tools. |
| Ignoring Hivemind when using Cline | Running Cline sessions without posting context | Always post context and heartbeat. OpenCode agents need to know you're active. |

---

## References

- `.clinerules` — Cline CLI project rules (this file)
- `docs/strategy/HIVEMIND_PROTOCOL.md` — Full Hivemind protocol specification
- `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` — HandoffPacket schema and lifecycle
- `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md` — Multi-platform integration patterns
- `mcp_servers/omega_hub/server.py` — Omega Hub MCP server implementation

---

*⬡ OMEGA ⬡ KB-CLINE ⬡ trc_knowledge_base*

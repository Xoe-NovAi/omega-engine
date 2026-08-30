<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — MCP Client Setup Guide

**AP Token**: `AP-MCP-CLIENT-SETUP-v1.0.0`
⬡ OMEGA ⬡ VERITY ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_mcp_setup ⬡ USER-FACING

**Date**: 2026-07-13
**Purpose**: Connect Cline, Gemini CLI, VS Code, and other MCP clients to the Omega Engine's 5-server MCP fleet.

---

## Overview

The Omega Engine exposes **5 MCP servers** via the **Omega Hub** (central router). Clients connect to the Hub at `:8016/mcp` (Streamable HTTP) or `:8016/sse` (SSE) and gain transparent access to all downstream servers.

| Server | Port | Transport | Purpose |
|--------|------|-----------|---------|
| **Omega Hub** | 8016 | Streamable HTTP (`/mcp`) + SSE (`/sse`) | Central router — 47 tools, Hivemind, entity mgmt, observability |
| **SearXNG** | 8018 | Streamable HTTP (`/mcp`) | Sovereign web search (metasearch, no tracking) |
| **Firecrawl** | 8015 | SSE (`/sse`) | Deep web scraping / structured extraction |
| **Exa** | — | Via Hub | Neural search (Exa API) — requires `EXA_API_KEY` |
| **GitHub** | — | Via Hub | Repo ops, PRs, issues — requires `GITHUB_TOKEN` |

> **Key insight**: You only configure **one connection** (to Omega Hub). The Hub proxies to SearXNG, Firecrawl, Exa, GitHub automatically.

---

## Quick Start — Cline (VS Code)

### Prerequisites
- VS Code + Cline extension installed
- Omega Engine running: `make up` (starts all containers)
- Verify Hub health: `curl http://localhost:8016/health`

### 1. Add MCP Server in Cline
Open Cline settings → **MCP Servers** → **Add Server**:

```json
{
  "name": "omega-engine",
  "url": "http://localhost:8016/mcp",
  "transport": "streamable-http"
}
```

**Alternative (SSE fallback)**:
```json
{
  "name": "omega-engine",
  "url": "http://localhost:8016/sse",
  "transport": "sse"
}
```

### 2. Set Cline Identity (Required for Hivemind)
In Cline settings → **Custom Instructions**, add:
```
You are `cline/omega-engine`. When using Hivemind tools, always identify as channel="cline", entity="omega-engine".
```

### 3. Verify Connection
In Cline chat:
```
@omega-hub list all available tools
```
You should see 47+ tools including `hivemind_post_context`, `oracle_talk`, `library_search`, `sovereign_search`, etc.

---

## Quick Start — Gemini CLI

### 1. Install
```bash
npm install -g @google/gemini-cli
```

### 2. Configure MCP
Create `~/.gemini/mcp.json`:
```json
{
  "mcpServers": {
    "omega-engine": {
      "url": "http://localhost:8016/mcp",
      "transport": "streamable-http"
    }
  }
}
```

### 3. Run
```bash
gemini --mcp
```

---

## Quick Start — VS Code (Native MCP)

### 1. Workspace Config (`.vscode/mcp.json`)
```json
{
  "servers": {
    "omega-engine": {
      "url": "http://localhost:8016/mcp",
      "transport": "streamable-http"
    }
  }
}
```

### 2. Use in Copilot Chat
```
@omega-hub oracle_talk "What entities are available?"
```

---

## Quick Start — OpenCode (Native)

OpenCode auto-discovers `opencode.json` in this repo:
```json
{
  "mcp": {
    "servers": {
      "omega-hub": {
        "url": "http://localhost:8016/mcp",
        "transport": "streamable-http"
      }
    }
  }
}
```
Run `opencode` from repo root — it connects automatically.

---

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `EXA_API_KEY` | For Exa search | Neural search via Exa |
| `GITHUB_TOKEN` | For GitHub ops | PRs, issues, repo mgmt |
| `FIRECRAWL_API_KEY` | For Firecrawl | Deep scraping |
| `OMEGA_MODELS_DIR` | For local models | GGUF model path (default: `/media/.../models/gguf/`) |

Set in `.env` or shell:
```bash
export EXA_API_KEY="exa_..."
export GITHUB_TOKEN="ghp_..."
export FIRECRAWL_API_KEY="fc_..."
```

---

## Omega Hub Tools Reference (47 Tools)

### Hivemind Coordination (6)
| Tool | Purpose |
|------|---------|
| `hivemind_post_context` | Post agent context (status, decisions, continuation) |
| `hivemind_get_awareness` | See all active agents across platforms |
| `hivemind_heartbeat` | Keep agent alive in awareness |
| `hivemind_submit_handoff` | Delegate task to another agent |
| `hivemind_accept_handoff` | Accept delegated task |
| `hivemind_complete_handoff` | Mark task complete |

### Entity & Oracle (8)
| Tool | Purpose |
|------|---------|
| `oracle_talk` | Auto-routed query (Iris → Pillar) |
| `oracle_summon` | Direct entity invocation |
| `oracle_list_entities` | List all awakened entities |
| `oracle_entity_info` | Get entity details (soul, model, domain) |
| `oracle_discover_entity` | Find best entity for a task |
| `oracle_assess_intent` | Classify query intent |
| `oracle_list_pillar_keepers` | List 10 Pillar Keepers (P1-P10) |
| `oracle_summon_local` | Force local model for entity |

### Library & Research (10)
| Tool | Purpose |
|------|---------|
| `library_search` | Local FTS5 search |
| `library_web_search` | Sovereign web search (SearXNG→Exa→Firecrawl) |
| `library_fts_search` | Raw FTS5 query |
| `library_get_document` | Fetch document by ID |
| `library_inbox_add_url` | Queue URL for ingestion |
| `library_inbox_add_note` | Queue note for ingestion |
| `library_ingest_pending` | Process inbox |
| `research` | Tiered deep research (T1→T2→T3) |
| `library_discovery_research` | Background discovery job |
| `library_stats` | Corpus statistics |

### Observability (6)
| Tool | Purpose |
|------|---------|
| `get_system_stats` | CPU/mem/disk/GPU/Podman |
| `get_hardware_stats` | Per-core CPU, thermal, OOM risk |
| `get_omega_metrics` | Inference/research/memory/error metrics |
| `observability_stream` | SSE endpoint for live traces |
| `check_recursion` | Detect recursive agent loops |
| `log_boundary_violation` | Log sovereign boundary breach |

### GitHub & System (8)
| Tool | Purpose |
|------|---------|
| `github_create_pr` | Temple-Grade PR template |
| `github_check_temple_grade` | CI status for PR |
| `github_add_entity_attribution` | Sign commit with entity |
| `github_list_heritage_issues` | Open heritage-tagged issues |
| `github_create_vet_issue` | Create vet issue from record |
| `github_get_repo_health` | Repo metrics |
| `check_models_directory` | Local GGUF inventory |
| `check_podman_storage` | Podman disk usage |

### Memory & Session (9)
| Tool | Purpose |
|------|---------|
| `omega_memory_search` | Hybrid search (FTS5 + vector) |
| `omega_memory_get_history` | Session conversation history |
| `omega_memory_list_sessions` | List recent sessions |
| `delegate_task` | Spawn subagent with soul injection |
| `oracle_entity_info` | Entity details |
| `oracle_summon` | Direct summon |
| `oracle_talk` | Auto-route |
| `oracle_list_entities` | All entities |
| `oracle_discover_entity` | Best match |

---

## Troubleshooting

### "Connection refused" / "ECONNREFUSED"
```bash
# Check Hub is running
curl http://localhost:8016/health

# If not, start stack
make up
```

### "Tool not found" errors
- Ensure you're using **Hub URL** (`:8016/mcp`), not individual server URLs
- Hub proxies all downstream tools transparently

### Cline: "MCP server not responding"
- Check Cline output panel for connection logs
- Try SSE fallback: `http://localhost:8016/sse` with transport `sse`
- Restart Cline extension after config change

### Hivemind: "Agent not in awareness"
- Call `hivemind_heartbeat` every 5-10 min during long sessions
- Use `hivemind_extended_checkin` for sessions >20 min

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT (Cline, Gemini, VS Code)          │
└─────────────────────────┬───────────────────────────────────┘
                          │ Streamable HTTP / SSE
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    OMEGA HUB (:8016)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  Hivemind   │  │   Oracle    │  │  Library    │  ...47   │
│  │  Tools      │  │  Tools      │  │  Tools      │  tools   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
└─────────┼────────────────┼────────────────┼──────────────────┘
          │                │                │
    ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐
    │ SearXNG   │    │ Firecrawl │    │  Exa      │
    │ :8018/mcp │    │ :8015/sse │    │ (via Hub) │
    └───────────┘    └───────────┘    └───────────┘
          │                │                │
          └────────────────┴────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   GitHub API          │
              │   (via Hub)           │
              └───────────────────────┘
```

---

## Related Docs

- `docs/strategy/HIVEMIND_PROTOCOL.md` — Multi-agent coordination
- `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` — Execution roadmap
- `OMEGA_ENGINE.md` — System state SSOT
- `docs/kb/CLINE_CLI_INTEGRATION.md` — Cline-specific deep dive

---

*Generated for v1.2.0 release — SWP, Doc Reader, Sieve, Heritage Pipeline, MCP/Cline connectivity*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

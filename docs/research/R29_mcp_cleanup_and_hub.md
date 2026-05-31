# 🔱 Omega Engine — MCP Hub Architectural Proposal
**AP Token**: `AP-OMEGA-MCP-HUB-v1.0.0`
**Status**: PROPOSAL
**Author**: Gemma 4-31B Research Agent
**Last Updated**: 2026-05-14

## ⬡ Executive Summary

The current MCP architecture of the Omega Engine is fragmented, with core services (Oracle, Hivemind, Library, Stats) each running as separate local processes. This "fragmented fabric" increases system overhead, clutters configuration, and introduces unnecessary process management complexity. 

This proposal defines the **Omega MCP Hub**, a unified gateway server that consolidates all core engine capabilities into a single MCP connection.

---

## ⬡ 1. Architecture Design

The Omega MCP Hub transforms the current 1:1 (Service $\rightarrow$ Server) mapping into a 1:N (Hub $\rightarrow$ Services) mapping.

### Hub Topology
```
OpenCode CLI $\rightarrow$ [ Omega MCP Hub ] $\rightarrow$ { Core Omega Services }
                                 $\downarrow$
                                 ├── Oracle (Routing/Summon)
                                 ├── Hivemind (Context/Awareness)
                                 ├── Library (RAG/Intake/Index)
                                 └── Stats (System Monitoring)
```

### Technical Specification
- **Framework**: `mcp.server.fastmcp` (FastMCP)
- **Integration Pattern**: Service Delegation. The Hub does not reimplement logic; it instantiates the underlying `src/omega` service classes and exposes their methods as MCP tools.
- **Concurrency**: Leveraging `anyio` for asynchronous tool execution to ensure the Hub remains responsive during long-running RAG or inference calls.

---

## ⬡ 2. Efficiency & Stability Analysis

### Performance Gains
| Metric | Fragmented (Current) | Unified (Hub) | Impact |
|---|---|---|---|
| **Process Count** | 5+ Python Processes | 1 Python Process | $\downarrow$ Memory overhead |
| **Startup Latency** | Sequential/Parallel Init | Single Init | $\downarrow$ Boot time |
| **Context Switching** | Inter-process communication | Intra-process calls | $\uparrow$ Execution speed |
| **Config Complexity** | 5-10 JSON blocks | 1 JSON block | $\downarrow$ Noise / Maintenance |

### Stability Improvements
- **Atomic Lifecycle**: The Hub starts and stops as a single unit. No more "zombie" MCP processes left behind if the CLI crashes.
- **Shared Resource Guard**: By unifying the servers, the Hub can more easily integrate with `src/omega/oracle/resource_guard.py` to ensure that MCP-triggered inference doesn't conflict with direct CLI inference.

---

## ⬡ 3. Implementation Path

### Phase 1: Hub Scaffolding
Create `mcp/omega_hub/server.py` and initialize the `FastMCP` instance.

### Phase 2: Service Integration
Map existing tool logic to the Hub:
1. **Oracle**: Import `Oracle` and `EntityRegistry`. Map `talk()`, `summon()`, `list_entities()`.
2. **Hivemind**: Import Hivemind logic. Map `post_context()`, `get_awareness()`.
3. **Library**: Import `Library`, `Indexer`, `InboxManager`. Map `library_search()`, `inbox_add_url()`.
4. **Stats**: Import system monitoring functions. Map `get_system_stats()`.

### Phase 3: Namespace Strategy
To maintain clarity, tools will follow a `service_action` naming convention:
- `oracle_talk`
- `hivemind_post_context`
- `library_search`
- `stats_system_info`

---

## ⬡ 4. Cleanup & Pruning Strategy

To transition to the Hub, the following pruning criteria will be applied to existing MCP servers:

### Pruning Criteria
1. **Redundancy**: Any server that simply wraps a class found in `src/omega/` is moved to the Hub and deleted.
2. **Legacy/XNA**: All servers with `xna-` or `legacy-` prefixes are immediately purged.
3. **Generic Utility**: Generic tools (like `filesystem`) are kept as standalone servers since they are provided by the MCP ecosystem and not core to the Omega Engine logic.

### Deprecation List
- `mcp/omega-oracle/` $\rightarrow$ **Move to Hub**
- `mcp/omega-hivemind/` $\rightarrow$ **Move to Hub**
- `mcp/omega-library/` $\rightarrow$ **Move to Hub**
- `mcp/omega-stats/` $\rightarrow$ **Move to Hub**
- `mcp/omega-research/` $\rightarrow$ **Consolidate into Hub / Library**

---

## ⬡ 5. Connection Specification

The `opencode.json` configuration will be reduced to a single entry for the core engine:

```json
{
  "mcp": {
    "omega-hub": {
      "type": "local",
      "command": ["python", "mcp/omega_hub/server.py"],
      "timeout": 10000
    },
    "filesystem": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
      "args": ["/home/arcana-novai/Documents/Xoe-NovAi/omega-engine"],
      "enabled": true
    }
  }
}
```

---

## ⬡ Implementation Note for Artisan/Builder
When implementing this Hub, ensure that `sys.path` is correctly configured to include `src/` so that imports from `omega.*` work seamlessly. Use a single `FastMCP` instance and avoid creating new service instances inside the tool functions; initialize them at the module level for persistence.

# 🔱 Fleet Review 6: MCP Hub & Integration Infrastructure

⬡ OMEGA ⬡ HECATE ⬡ claude-sonnet-4-6-thinking ⬡ web ⬡ trc_review_mcp ⬡ PHASE-E

**Account**: `lilithasterion@gmail.com`
**Role**: Infrastructure Guru — verify the MCP (Model Context Protocol) layer, SSE hub, systemd lifecycle

---

## 📋 Mission

You are performing a deep strategic review of the Omega Engine's **MCP integration layer** — the communication backbone that connects all agents, tools, and services. This covers the consolidated Omega Hub (37 tools on SSE :8016), the MCP Runtime abstraction, systemd lifecycle management (socket activation, timers, services), opencode.json MCP configuration, the MCP watchdog and health monitoring scripts, and the infrastructure deployment stack (Redis, Qdrant, PostgreSQL, Caddy). This layer must be rock-solid — every agent depends on it.

---

## 🎯 Scope — Files to Read

### Source: MCP Hub & Runtime
- **Omega Hub Server**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/mcp/omega_hub/server.py`
- **MCP Runtime**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/mcp_runtime.py`

### Configuration: OpenCode & MCP
- **OpenCode Config**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/opencode.json`
- **MCP Servers Registry**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/config/mcp_servers.json`

### Systemd Lifecycle
- **Hivemind Service**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/config/systemd/omega-hivemind.service`
- **Research Service**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/config/systemd/omega-research.service`
- **Research Timer**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/config/systemd/omega-research.timer`

### Scripts: MCP Health & Watchdog
- **MCP Watchdog**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/scripts/mcp_watchdog.py`
- **MCP Health Check**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/scripts/mcp_health_check.sh`
- **IDE MCP Sync**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/scripts/sync_ide_mcp.sh`

### Infrastructure Deployment
- **docker-compose**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/deploy/infra/docker-compose.yml`
- **Caddyfile**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/deploy/infra/Caddyfile`

### Archived MCPs (for reference)
- Browse archive: `https://github.com/Xoe-NovAi/omega-engine/tree/main/mcp/archives`

---

## ❓ Review Questions

1. **Omega Hub Correctness**: The Hub consolidates 37 tools from 3 previously standalone MCP servers (hivemind, research, stats). Are all tools properly registered? Are there any naming conflicts? Is the SSE event stream well-formed? Check `server.py` thoroughly.

2. **MCP Runtime Abstraction**: The `mcp_runtime.py` provides a standardized interface (SSE/stdio/systemd). Is its abstraction complete? Does it handle both SSE and stdio transports correctly? Are error states properly propagated?

3. **Systemd Lifecycle**: The hivemind and research services use systemd. Are the unit files correct? Do they handle restart correctly? Are socket activation patterns used where appropriate? Are there any missing `Wants=` or `After=` dependencies?

4. **SSE Endpoint Verification**: The Hub serves on `:8016/sse`. Is the SSE implementation compliant with the MCP specification? Does it handle reconnection? Are there any memory leaks from long-lived SSE connections?

5. **Opencode.json MCP Configuration**: The opencode.json references 7 MCP servers. Are they all correctly configured? Are there any stale entries pointing to the archived standalone servers? Is the authentication for remote servers (exa, serper, tavily, jina) properly handled?

6. **MCP Watchdog**: The `mcp_watchdog.py` monitors MCP health. Is its monitoring correct? Does it trigger alerts? Does it auto-restart failed services? Is it properly wired into the systemd unit dependency graph?

7. **Infrastructure Stack**: The deploy/infra/ docker-compose manages Redis, Qdrant, PostgreSQL, and Caddy. Is this current with the actual running pod (which has 5 containers)? Are there any discrepancies between the compose file and the actual infrastructure?

8. **Consolidation Completeness**: Decision 50 and 29 consolidated multiple MCPs into the Hub. Are there any remaining standalone MCP servers that should have been consolidated? Are the archives properly maintained?

---

## 📜 Sovereign Mandates Checklist

| Mandate | What to Check |
|---------|---------------|
| **AnyIO Absolute** | mcp_runtime.py, mcp_watchdog.py — any `asyncio`? |
| **Engine-Stack Firewall** | Hub serves all stacks equally — verify neutrality |
| **Iris Constant** | Iris may be served via Hub — verify she's still messenger, not pillar |
| **Sequentiality** | MCP changes follow plan-verify-execute |
| **Gnosis Preservation** | MCP events logged in observability |
| **Podman Sovereignty** | All containers referenced: keep-id, no `:U` |

---

## 📊 Output Template

```markdown
## Review: MCP Hub & Integration Infrastructure

### Critical Issues Found
- [ ] C-MCP-001: [Title] — [CRITICAL/HIGH/MEDIUM/LOW]

### Omega Hub Assessment
- Tools registered: [N]
- Conflicts: ...
- SSE stream health: ...

### Systemd Lifecycle
- Service correctness: ...
- Timer correctness: ...
- Dependency graph: ...

### MCP Runtime
- Transport abstraction: ...
- Error handling: ...
- SSE compliance: ...

### Infrastructure Stack
- docker-compose vs actual: ...
- Caddy configuration: ...
- Port configuration: ...

### Report Card
| Metric | Grade | Notes |
|--------|-------|-------|
| Correctness | A/B/C/D | |
| Resilience | A/B/C/D | |
| MCP Compliance | A/B/C/D | |
| Documentation | A/B/C/D | |

### Strategic Recommendations (Top 3)
1. ...
2. ...
3. ...
```

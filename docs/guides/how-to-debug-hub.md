# 🔱 How-to: Debug the Omega Hub
**AP Token**: `AP-GUIDE-DEBUG-HUB-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_proc ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Step-by-step guide for debugging the Omega Hub (MCP server).
**Tags**: how-to, debug, hub, mcp, troubleshooting
**Cross-references**: src/omega/hub.py, src/omega/monitoring/__init__.py, mcp_servers/omega_hub/server.py

---

## Overview

The **Omega Hub** is the central MCP (Model Context Protocol) server that exposes all Omega Engine tools. When things go wrong, this guide helps you diagnose and fix common issues.

**Hub Components**:
- **MCP Server** (`mcp_servers/omega_hub/server.py`) — Port 8016
- **Hardware Bridge** (`src/omega/hub.py`) — Hardware stats for Oracle
- **Tool Registry** — 54+ unified tools

---

## Quick Health Check

```bash
# 1. Basic health endpoint
curl http://localhost:8016/health
# Expected: {"status":"healthy","version":"1.6.0-alpha.1"}

# 2. Check process
ps aux | grep "omega_hub.server"
# Should show python process

# 3. Check port
ss -tlnp | grep 8016
# Should show LISTEN on 8016
```

---

## Common Issues & Fixes

### Issue 1: Hub Not Responding

**Symptoms**: `curl` times out or connection refused

**Diagnosis**:
```bash
# Check if process exists
pgrep -f "omega_hub.server"

# Check logs
journalctl --user -u omega-hub.service -f
# Or if running manually:
# Check the terminal where you started it
```

**Fixes**:
```bash
# Restart service
systemctl --user restart omega-hub.service

# Or manual restart
pkill -f "omega_hub.server"
cd ~/Documents/Xoe-NovAi/omega-engine
python -m mcp_servers.omega_hub.server &
```

### Issue 2: Tools Not Appearing in OpenCode

**Symptoms**: OpenCode shows fewer than 54 tools

**Diagnosis**:
```bash
# Check tool registration
curl -s http://localhost:8016/mcp | jq '.tools | length'
# Should be 54+

# List all tools
curl -s http://localhost:8016/mcp | jq '.tools[].name' | sort
```

**Fixes**:
```bash
# Check for import errors in server startup logs
# Common: missing imports in tool modules

# Verify tool modules load
python -c "
from mcp_servers.omega_hub.server import TOOL_REGISTRY
print(f'Registered tools: {len(TOOL_REGISTRY)}')
for name in sorted(TOOL_REGISTRY.keys()):
    print(f'  {name}')
"
```

### Issue 3: Tool Execution Fails

**Symptoms**: Tool returns error or times out

**Diagnosis**:
```bash
# Test specific tool via MCP
curl -X POST http://localhost:8016/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"websearch","arguments":{"query":"test"}}}'

# Check for Python exceptions in hub logs
```

**Common Causes & Fixes**:

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError` | Missing dependency | `pip install <module>` in `.venv` |
| `TimeoutError` | Tool too slow | Increase timeout or optimize tool |
| `PermissionError` | File access | Check file permissions |
| `ConnectionError` | External API down | Check network; add retry logic |

### Issue 4: Hardware Stats Not Working

**Symptoms**: `get_hardware_stats()` returns defaults (cpu_usage=0, memory=1024)

**Diagnosis**:
```bash
# Test monitoring directly
python -c "
from omega.monitoring import HardwareMonitor
hm = HardwareMonitor()
stats = hm.collect_all()
print(stats)
"
```

**Fixes**:
```bash
# Install psutil if missing
pip install psutil

# Check /proc access
ls -la /proc/stat /proc/meminfo /proc/loadavg

# Verify thermal zones
ls /sys/class/thermal/thermal_zone*
ls /sys/class/hwmon/
```

---

## Advanced Debugging

### Enable Debug Logging

```bash
# Set log level
export LOG_LEVEL=DEBUG
export OMEGA_LOG_LEVEL=DEBUG

# Restart hub
systemctl --user restart omega-hub.service
```

### Inspect MCP Protocol

```bash
# Capture MCP traffic
# Use mcp-inspector or proxy
python -m mcp_inspector --port 8016
```

### Test Individual Tools

```bash
# Test websearch
python -c "
import asyncio
from mcp_servers.omega_hub.hub_tools import websearch
async def test():
    result = await websearch(action='search', query='Omega Engine', max_results=3)
    print(result)
asyncio.run(test())
"

# Test hivemind
python -c "
import asyncio
from mcp_servers.omega_hub.hub_tools import hivemind_awareness
async def test():
    result = await hivemind_awareness(action='get')
    print(result)
asyncio.run(test())
"
```

### Check Tool Registration

```python
# Full tool audit
python -c "
from mcp_servers.omega_hub.server import TOOL_REGISTRY
print(f'Total tools: {len(TOOL_REGISTRY)}')
for name, tool in sorted(TOOL_REGISTRY.items()):
    print(f'{name}: {tool.get(\"description\", \"no description\")[:60]}')
"
```

---

## Health Check Script

Save as `scripts/hub_health_check.py`:

```python
#!/usr/bin/env python3
"""Omega Hub Health Check."""

import asyncio
import httpx
import sys

async def check_hub():
    base = "http://localhost:8016"
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        # 1. Health endpoint
        try:
            resp = await client.get(f"{base}/health")
            health = resp.json()
            print(f"✅ Health: {health}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
        
        # 2. MCP endpoint
        try:
            resp = await client.post(f"{base}/mcp", json={
                "jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}
            })
            tools = resp.json().get("result", {}).get("tools", [])
            print(f"✅ Tools: {len(tools)} registered")
        except Exception as e:
            print(f"❌ MCP tools/list failed: {e}")
            return False
        
        # 3. Test a tool
        try:
            resp = await client.post(f"{base}/mcp", json={
                "jsonrpc": "2.0", "id": 2, "method": "tools/call",
                "params": {"name": "websearch", "arguments": {"query": "test", "max_results": 1}}
            })
            result = resp.json().get("result", {})
            if result.get("isError"):
                print(f"⚠️  Tool returned error: {result.get('content')}")
            else:
                print(f"✅ Tool execution works")
        except Exception as e:
            print(f"❌ Tool execution failed: {e}")
            return False
        
        return True

if __name__ == "__main__":
    ok = asyncio.run(check_hub())
    sys.exit(0 if ok else 1)
```

Run it:
```bash
python scripts/hub_health_check.py
```

---

## Emergency Recovery

### Complete Hub Reset

```bash
# 1. Kill all hub processes
pkill -f "omega_hub.server"
pkill -f "omega_hub"

# 2. Clear any lock files
rm -f /tmp/omega_hub.lock

# 3. Restart fresh
cd ~/Documents/Xoe-NovAi/omega-engine
source .venv/bin/activate
python -m mcp_servers.omega_hub.server &
```

### Verify Recovery

```bash
# Wait 3 seconds for startup
sleep 3

# Run health check
python scripts/hub_health_check.py
```

---

## When to Escalate

If the above doesn't work, check:

1. **Git status** — Any uncommitted changes to hub code?
   ```bash
   cd ~/Documents/Xoe-NovAi/omega-engine
   git status
   git diff mcp_servers/omega_hub/server.py
   ```

2. **Recent commits** — Did a recent change break it?
   ```bash
   git log --oneline -10
   ```

3. **Dependency issues** — Venv corrupted?
   ```bash
   # Recreate venv
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

4. **System resources** — OOM or disk full?
   ```bash
   df -h
   free -h
   ```

---

## Related Guides

- [How to Add an MCP Tool](../tutorials/how-to-add-mcp-tool.md)
- [How to Configure Entities](../guides/how-to-configure-entities.md) (TODO)
- [How to Monitor System Health](../guides/how-to-monitor-system-health.md) (TODO)

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ GUIDE-DEBUG-HUB-v1.0.0 ⬡ 2026-10-02 ⬡*
<!-- PROVENANCE-CORRECTED 2026-10-03T06:22:36Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->


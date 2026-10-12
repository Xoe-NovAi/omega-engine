# 🔱 Tutorial: How to Add a New MCP Tool
**AP Token**: `AP-TUTORIAL-MCP-TOOL-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_user ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Step-by-step tutorial for adding a new MCP tool to the Omega Engine.
**Prerequisites**: Python 3.11+, `omega-engine` repo cloned, basic MCP knowledge
**Tags**: tutorial, mcp, tool, development

---

## Overview

This tutorial walks through adding a new MCP (Model Context Protocol) tool to the Omega Engine. We'll create a tool that fetches system information — a practical example that demonstrates the full lifecycle.

**What you'll build**: A `system_info` MCP tool that returns CPU, memory, and disk stats.

**Time estimate**: 30-45 minutes

---

## Prerequisites

```bash
# Ensure you're in the repo
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine

# Activate venv
source .venv/bin/activate

# Verify MCP dependencies
python -c "import httpx; import anyio; print('OK')"
```

---

## Step 1: Define the Tool Schema

Create the tool definition in `src/omega/mcp_core/tools/system_info.py`:

```python
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0

"""System Information MCP Tool.
AP: AP-MCP-SYSTEM-INFO-v1.0.0
"""

from typing import Any, Dict
from omega.mcp_core import MCPClient, create_mcp_client


# Tool metadata for registration
TOOL_DEFINITION = {
    "name": "system_info",
    "description": "Get comprehensive system hardware information",
    "inputSchema": {
        "type": "object",
        "properties": {
            "include_cpu": {"type": "boolean", "default": True, "description": "Include CPU details"},
            "include_memory": {"type": "boolean", "default": True, "description": "Include memory details"},
            "include_disk": {"type": "boolean", "default": True, "description": "Include disk details"},
            "include_thermal": {"type": "boolean", "default": False, "description": "Include thermal sensors"}
        },
        "required": []
    }
}


async def system_info_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handler for system_info tool."""
    from omega.monitoring import HardwareMonitor
    
    hm = HardwareMonitor()
    stats = hm.collect_all()
    
    result = {}
    if arguments.get("include_cpu", True):
        result["cpu"] = stats.get("cpu", {})
    if arguments.get("include_memory", True):
        result["memory"] = stats.get("memory", {})
    if arguments.get("include_disk", True):
        result["disk"] = stats.get("disk_io", {})
    if arguments.get("include_thermal", False):
        result["thermal"] = stats.get("temperatures", {})
    
    return {
        "content": [{"type": "text", "text": str(result)}],
        "isError": False
    }
```

---

## Step 2: Register the Tool

Add the tool to the MCP server's tool registry. Edit `mcp_servers/omega_hub/server.py`:

```python
# In server.py, add to the tool registration section:

from omega.mcp_core.tools.system_info import TOOL_DEFINITION, system_info_handler

# Register the tool
TOOL_REGISTRY["system_info"] = {
    "definition": TOOL_DEFINITION,
    "handler": system_info_handler
}
```

---

## Step 3: Add Tests

Create `tests/test_mcp_system_info.py`:

```python
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0

import pytest
from omega.mcp_core.tools.system_info import system_info_handler, TOOL_DEFINITION


@pytest.mark.asyncio
async def test_system_info_tool_definition():
    """Verify tool definition schema."""
    assert TOOL_DEFINITION["name"] == "system_info"
    assert "inputSchema" in TOOL_DEFINITION
    assert "properties" in TOOL_DEFINITION["inputSchema"]


@pytest.mark.asyncio
async def test_system_info_handler():
    """Test handler returns valid structure."""
    result = await system_info_handler({})
    
    assert "content" in result
    assert isinstance(result["content"], list)
    assert result["isError"] is False
    assert len(result["content"]) > 0


@pytest.mark.asyncio
async def test_system_info_handler_with_options():
    """Test handler with specific options."""
    result = await system_info_handler({
        "include_cpu": True,
        "include_memory": False,
        "include_disk": False,
        "include_thermal": True
    })
    
    assert result["isError"] is False
    content_text = result["content"][0]["text"]
    assert "cpu" in content_text.lower()
    assert "thermal" in content_text.lower()
```

Run tests:
```bash
pytest tests/test_mcp_system_info.py -v
```

---

## Step 4: Test with MCP Client

Create a test script `scripts/test_system_info_tool.py`:

```python
#!/usr/bin/env python3
"""Test the system_info MCP tool."""

import asyncio
from omega.mcp_core import create_mcp_client


async def main():
    # Connect to local MCP server
    client = create_mcp_client("http://localhost:8080")
    
    async with client:
        # Test basic call
        result = await client.call_tool("system_info", {})
        print("Basic call:")
        print(result.content[0][:500])
        print()
        
        # Test with options
        result = await client.call_tool("system_info", {
            "include_cpu": True,
            "include_memory": True,
            "include_thermal": True
        })
        print("With thermal:")
        print(result.content[0][:500])


if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
# Start MCP server first (in another terminal)
python -m mcp_servers.omega_hub.server

# Run test
python scripts/test_system_info_tool.py
```

---

## Step 5: Verify OpenCode Integration

Test the tool via OpenCode:

```bash
# In OpenCode, use the tool
# The tool should appear in the available tools list
```

Or test via the bridge:
```python
from omega.bridge.opencode_bridge import OpenCodeBridge

bridge = OpenCodeBridge()
# Tool will be available through the WebSocket bridge
```

---

## Step 6: Documentation

Add the tool to the MCP tool catalog in `docs/reference/api/mcp_tools.md` (create if needed):

```markdown
## system_info

Get comprehensive system hardware information.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_cpu` | boolean | `true` | Include CPU details |
| `include_memory` | boolean | `true` | Include memory details |
| `include_disk` | boolean | `true` | Include disk details |
| `include_thermal` | boolean | `false` | Include thermal sensors |

### Example

```json
{
  "name": "system_info",
  "arguments": {
    "include_thermal": true
  }
}
```

### Response

```json
{
  "cpu": {"avg_percent": 12.3, "per_core_percent": {...}},
  "memory": {"available_mb": 8234, "total_mb": 13952, ...},
  "thermal": {"available": true, "celsius": [{"label": "Tdie", "temp": 52.0}]}
}
```
```

---

## Common Patterns

### Async Handler with External API

```python
async def weather_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    import httpx
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.weather.com/v1/current",
            params={"location": arguments["location"]}
        )
        resp.raise_for_status()
        data = resp.json()
    
    return {
        "content": [{"type": "text", "text": str(data)}],
        "isError": False
    }
```

### Handler with Validation

```python
from pydantic import BaseModel, Field

class SearchArgs(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(10, ge=1, le=50)

async def search_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    # Validate input
    args = SearchArgs(**arguments)
    
    # Process...
    return {"content": [...], "isError": False}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Tool not appearing | Check `TOOL_REGISTRY` registration; restart MCP server |
| `isError: true` | Check handler exception; add try/except with logging |
| Schema validation fails | Verify `inputSchema` matches JSON Schema Draft 7 |
| Timeout | Increase `timeout` in `MCPClient` or optimize handler |

---

## Next Steps

1. **Add authentication** — Integrate with VaultCore for API keys
2. **Add rate limiting** — Use `ResourceGuard` for resource protection
3. **Add observability** — Emit trace events via `ObservabilityEngine`
4. **Write contract tests** — Use `assert_*` helpers for M21 compliance

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ TUTORIAL-MCP-TOOL-v1.0.0 ⬡ 2026-10-02 ⬡*
<!-- PROVENANCE-CORRECTED 2026-10-03T06:22:36Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->


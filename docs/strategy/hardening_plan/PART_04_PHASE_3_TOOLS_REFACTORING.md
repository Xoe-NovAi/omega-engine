# 🔱 Omega Engine Hardening Plan — Phase 3: Tools Refactoring & Hub Split

**AP Token**: `AP-JOHN_CARMACK-HARDENING-v1.0.0`  
**Phase**: 3 — Tools Refactoring & Hub Split  
**Days**: 15-21  
**Hardware Profile**: Compilation + Light Inference — **SEQUENTIAL HEAVY TASKS ONLY**

---

## 📋 What I Am Working On
Refactor the 127,642-line `tools.py` monolith into modular, maintainable packages while preserving the existing architectural patterns (lazy loading, dependency injection, circular import prevention).

---

## 🔍 First Principles
**M16 Modularization & Portability**: No hardcoded paths in `src/omega/`. Platform integration via MCP/CLI.  
**Architectural Integrity**: Single responsibility principle. One file, one reason to change.  
**Circular Import Prevention**: Preserve the existing `AsyncServiceProxy` and `__getattr__` lazy-loading patterns that prevent import cycles.  
**Empirical Validation**: Measure before optimizing. Refactor one module at a time, verify with `make test`.

**Current State**: `mcp_servers/omega_hub/tools.py` = 127,642 lines - severe architectural drift, maintenance nightmare, violates single responsibility.

**Right Approximation**: Extract tool categories into focused modules **while preserving the exact same external interface and lazy-loading behavior**. No functional changes - pure refactoring.

---

## 🎯 Phase 3 Objectives

| Objective | Success Metric | Tool |
|-----------|----------------|------|
| Tools.py modularization | < 500 lines per tool file | `wc -l` |
| External interface preservation | 0 breaking changes | `make test` passes |
| Lazy-loading preservation | Same startup time + memory profile | Benchmark comparison |
| Circular import elimination | No import cycles | `pyanis` or manual audit |
| Plugin architecture readiness | Easy to add new tools | Template module |

---

## 📋 Detailed Actions

### Days 15-16: Establish Refactoring Baseline & Safety Nets

**Actions**:
1. **Create comprehensive test baseline**
   ```bash
   # Capture current state
   mcp_servers/omega_hub/server.py:mcp._tool_manager._tools.keys() > tools_before.txt
   make test 2>&1 | tee test_before.log
   python -c "import time; start=time.time(); [omega-hub_oracle_talk 'test' for _ in range(10)]; print(f'Latency: {time.time()-start:.2f}s')" > latency_before.txt
   ```
   
2. **Set up refactoring safety scripts**
   ```bash
   # scripts/verify_tool_interface.py
   # Compares tool signatures before/after refactoring
   
   # scripts/benchmark_latency.py
   # Measures oracle_talk/hivemind_post_context latency
   
   # scripts/check_circular_imports.py
   # Uses pyanis or custom script to detect import cycles
   ```

3. **Document current tool categories**
   From `mcp_servers/omega_hub/tools.py`:
   - Oracle tools: `oracle_talk`, `oracle_summon`, `oracle_summon_local`, `oracle_list_entities`, etc. (~20 tools)
   - Hivemind tools: `hivemind_post_context`, `hivemind_heartbeat`, `hivemind_get_awareness`, etc. (~15 tools)
   - Search tools: `sovereign_search`, `search_extract`, `search_status` (~3 tools)
   - Task registry tools: `task_registry_register`, `task_registry_query`, etc. (~4 tools)
   - Gateway tools: (if any in tools.py)
   - Miscellaneous tools: `headroom_retrieve`, etc.

**Deliverable**: Baseline measurements + safety scripts

### Days 17-18: Create Modular Tools Structure

**Actions**:
1. **Create new directory structure**
   ```bash
   mkdir -p mcp_servers/omega_hub/tools/{oracle,hivemind,search,task,gateway,base}
   ```

2. **Create base module with shared components**
   **File**: `mcp_servers/omega_hub/tools/base.py`
   ```python
   """Shared base components for all tool modules"""
   
   import logging
   import os
   from pathlib import Path
   from typing import Any
   
   import anyio
   from mcp.server.fastmcp import FastMCP
   
   # Get the MCP instance from server (side-effect import safe)
   from mcp_servers.omega_hub.server import mcp
   
   # Shared logger
   logger = logging.getLogger("omega.hub.tools")
   
   # Shared PROJECT_ROOT (M16 compliant)
   PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
   
   # Shared AsyncServiceProxy pattern (preserves lazy loading)
   class AsyncServiceProxy:
       """Async proxy for lazy-loaded service singletons from state."""
       def __init__(self, name: str):
           self._name = name
       
       def __await__(self):
           return _state.get_service(self._name).__await__()
       
       def __bool__(self):
           return getattr(_state, self._name) is not None
   
   # Import state lazily to avoid circular imports
   def _get_state():
       from mcp_servers.omega_hub import state as _state
       return _state
   
   # Helper functions
   def _make_agent_id(channel: str, entity: str) -> str:
       return f"{channel}/{entity}"
   
   # Async YAML parsing utilities (from web research: YAMLRocks async_load/async_dump)
   async def async_load_yaml(filepath: Path) -> dict:
       """Load YAML file asynchronously using YAMLRocks (releases GIL during parse)"""
       try:
           import yamlrocks
           return await yamlrocks.async_load(filepath)
       except ImportError:
           # Fallback: run sync load in thread pool
           import yaml
           return await anyio.to_thread.run_sync(
               lambda: yaml.safe_load(filepath.read_text())
           )
   
   async def async_dump_yaml(data: dict, filepath: Path) -> None:
       """Dump YAML file asynchronously using YAMLRocks"""
       try:
           import yamlrocks
           await yamlrocks.async_dump(data, filepath)
       except ImportError:
           # Fallback: run sync dump in thread pool
           import yaml
           await anyio.to_thread.run_sync(
               lambda: filepath.write_text(yaml.dump(data))
           )
   ```

3. **Create oracle_tools.py (first module)**
   **File**: `mcp_servers/omega_hub/tools/oracle_tools.py`
   ```python
   """Oracle-related MCP tools"""
   
   from .base import mcp, logger, AsyncServiceProxy, _get_state, _make_agent_id
   from mcp.server.fastmcp import Context
   
   # Service proxies (lazy-loaded via AsyncServiceProxy)
   oracle = AsyncServiceProxy("oracle")
   registry = AsyncServiceProxy("registry")
   
   @mcp.tool()
   async def oracle_talk(query: str) -> str:
       """Route a query through the Omega Oracle. Speculative decoding handled internally."""
       # EXACT SAME IMPLEMENTATION AS ORIGINAL - ONLY IMPORT PATH CHANGED
       _state = _get_state()
       _state._require_service()
       response = await oracle.talk(query)
       # ... rest identical to original
   
   @mcp.tool()
   async def oracle_summon(entity_name: str, query: str) -> str:
       """Directly summon a specific entity by name."""
       # EXACT SAME IMPLEMENTATION AS ORIGINAL
       _state = _get_state()
       _state._require_service()
       response = await oracle.summon(entity_name, query)
       # ... rest identical
   
   # ... repeat for all oracle_* tools (exact copies, only import path changed)
   ```

4. **Create hivemind_tools.py, search_tools.py, task_tools.py similarly**
   - Each imports from `.base` only
   - Each contains ONLY the tools for that category
   - Each uses `AsyncServiceProxy` for service access
   - Each has EXACT same function signatures and implementations as original
   - Only difference: import path changed from `from mcp_servers.omega_hub import ...` to `from .base import ...`

**Critical Rule**: **ZERO functional changes**. Only change import statements. This ensures `make test` passes immediately after each module creation.

**Deliverable**: 
- `mcp_servers/omega_hub/tools/base.py`
- `mcp_servers/omega_hub/tools/oracle_tools.py`
- `mcp_servers/omega_hub/tools/hivemind_tools.py` 
- `mcp_servers/omega_hub/tools/search_tools.py`
- `mcp_servers/omega_hub/tools/task_tools.py`
- (Optional) `mcp_servers/omega_hub/tools/gateway_tools.py`

### Days 19-20: Update Tools __init__.py and Server.py

**Actions**:
1. **Update tools/__init__.py to import all submodules**
   **File**: `mcp_servers/omega_hub/tools/__init__.py`
   ```python
   """Omega Hub Tools — MCP Tool Registration"""
   
   # Import all submodules for side-effect registration
   # Order doesn't matter for side-effects, but be consistent
   from . import base  # noqa: F401
   from . import oracle_tools  # noqa: F401
   from . import hivemind_tools  # noqa: F401
   from . import search_tools  # noqa: F401
   from . import task_tools  # noqa: F401
   from . import gateway_tools  # noqa: F401  # if created
   
   # Tool registry is complete - all tools registered via side-effect import
   __all__ = [
       "base",
       "oracle_tools", 
       "hivemind_tools",
       "search_tools",
       "task_tools",
       "gateway_tools"
   ]
   ```
   
2. **Update server.py __getattr__ to point to new locations**
   **File**: `mcp_servers/omega_hub/server.py` (lines 138-154)
   ```python
   def __getattr__(name: str):
       """Lazy-load tools to resolve circular imports while maintaining backward compatibility."""
       # Map tool names to their new modules
       tool_module_map = {
           # Oracle tools
           "oracle_talk": "oracle_tools",
           "oracle_summon": "oracle_tools",
           "oracle_summon_local": "oracle_tools",
           "oracle_list_entities": "oracle_tools",
           "oracle_list_pillar_keepers": "oracle_tools",
           "oracle_entity_info": "oracle_tools",
           "oracle_assess_intent": "oracle_tools",
           "oracle_discover_entity": "oracle_tools",
           
           # Hivemind tools
           "hivemind_post_context": "hivemind_tools",
           "hivemind_heartbeat": "hivemind_tools",
           "hivemind_get_awareness": "hivemind_tools",
           "hivemind_get_continuation": "hivemind_tools",
           "hivemind_extended_checkin": "hivemind_tools",
           "hivemind_extended_checkout": "hivemind_tools",
           "hivemind_get_session": "hivemind_tools",
           "hivemind_list_sessions": "hivemind_tools",
           "hivemind_get_entity_context": "hivemind_tools",
           "hivemind_workspace_lock_acquire": "hivemind_tools",
           "hivemind_workspace_lock_release": "hivemind_tools",
           "hivemind_workspace_lock_check": "hivemind_tools",
           
           # Search tools
           "sovereign_search": "search_tools",
           "search_extract": "search_tools",
           "search_status": "search_tools",
           
           # Task tools
           "task_registry_register": "task_tools",
           "task_registry_query": "task_tools",
           "task_registry_update": "task_tools",
           "task_registry_get": "task_tools",
           
           # Gateway tools (if any)
           # ... add mappings
       }
       
       if name in tool_module_map:
           module_name = tool_module_map[name]
           # Import the module (continues
   }
   }
   }
   }
   }
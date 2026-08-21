# MCP Tool Schema Compression + headroom_compress Tool

**Files**: 
- `src/omega/mcp/tool_compressor.py` (new)
- `src/omega/mcp/client.py` (modifications)
- `src/omega/mcp/tools/headroom_tools.py` (new)
**Section**: 05 of 10  
**Priority**: P1 — MCP tool schema compression (80-90% savings) + self-service tools  

---

## Problem: MCP Tool Schema Overhead

Current Omega Engine registers **86 tools** in a single MCP server, injecting **~10.8K tokens/request** regardless of usage. This violates M2 (Engine-Stack Firewall) and kills local model viability.

**Headroom Solution**: Compress tool schemas with SmartCrusher (80-90% reduction) + provide `headroom_compress` / `headroom_retrieve` MCP tools for entity self-service.

---

## MCPToolCompressor Class

```python
"""
MCP Tool Schema Compression via Headroom SmartCrusher.

Compresses MCP tool schemas for context injection.
Tool schemas are verbose JSON — SmartCrusher achieves 80-90% reduction
while preserving required parameters and descriptions.

Mandate Compliance:
- M1 AnyIO Absolute: All async uses anyio.to_thread.run_sync()
- M7 Local-First: Headroom runs locally
- M18 Token Efficiency: 80-90% token reduction on tool schemas
- M23 Failure Integrity: Graceful fallback to uncompressed
"""

from __future__ import annotations

import anyio
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from headroom.transforms import SmartCrusher, SmartCrusherConfig
from headroom.transforms.relevance import RelevanceScorerConfig

from omega.oracle.middleware.headroom import HeadroomMiddleware


@dataclass
class MCPToolCompressorConfig:
    """Configuration for MCP tool schema compression."""
    max_items_after_crush: int = 10          # Keep top 10 most relevant tools
    min_tokens_to_crush: int = 100           # Only crush if >100 tokens
    relevance_tier: str = "keyword"          # Keyword relevance for tool names
    hybrid_alpha: float = 0.3                # Low embedding weight for tools
    protect_recent_tools: int = 0            # No protection for static schemas
    operation_timeout_seconds: float = 5.0


class MCPToolCompressor:
    """
    Compresses MCP tool schemas for context injection.
    
    Usage:
        compressor = MCPToolCompressor(config)
        compressed_schemas = await compressor.compress_tool_schemas(all_tools)
        # Inject compressed_schemas instead of all_tools
    """
    
    def __init__(self, config: Optional[MCPToolCompressorConfig] = None):
        self.config = config or MCPToolCompressorConfig()
        self._crusher = SmartCrusher(SmartCrusherConfig(
            max_items_after_crush=self.config.max_items_after_crush,
            min_tokens_to_crush=self.config.min_tokens_to_crush,
            relevance=RelevanceScorerConfig(
                tier=self.config.relevance_tier,
                embedding_model="all-MiniLM-L6-v2",
                hybrid_alpha=self.config.hybrid_alpha,
            ),
        ))
        self._metrics = {
            "total_compressions": 0,
            "total_tokens_original": 0,
            "total_tokens_compressed": 0,
            "total_latency_ms": 0.0,
            "fallback_count": 0,
        }
    
    async def compress_tool_schemas(self, tools: List[Dict]) -> List[Dict]:
        """
        Compress tool schema list for context injection.
        
        Args:
            tools: List of MCP tool schema dicts (name, description, inputSchema)
            
        Returns:
            Compressed tool schemas (top-N most relevant, reduced descriptions)
        """
        start_time = time.perf_counter()
        
        if not tools:
            return tools
        
        try:
            # SmartCrusher operates on JSON arrays
            compressed = await anyio.to_thread.run_sync(
                self._crusher.compress,
                tools,
            )
            
            # Update metrics
            latency_ms = (time.perf_counter() - start_time) * 1000
            orig_tokens = sum(len(str(t)) // 4 for t in tools)
            comp_tokens = sum(len(str(t)) // 4 for t in compressed)
            
            self._metrics["total_compressions"] += 1
            self._metrics["total_tokens_original"] += orig_tokens
            self._metrics["total_tokens_compressed"] += comp_tokens
            self._metrics["total_latency_ms"] += latency_ms
            
            return compressed
            
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            self._metrics["fallback_count"] += 1
            
            import logging
            logger = logging.getLogger("omega.mcp.tool_compressor")
            logger.warning(f"MCP tool schema compression failed: {e}")
            
            return tools  # Fallback to uncompressed
    
    async def compress_tool_output(self, output: Dict) -> Dict:
        """
        Compress individual tool output (JSON).
        
        Args:
            output: Tool output dict
            
        Returns:
            Compressed output dict
        """
        start_time = time.perf_counter()
        
        if not output:
            return output
        
        try:
            compressed = await anyio.to_thread.run_sync(
                self._crusher.compress,
                [output],
            )
            result = compressed[0] if compressed else output
            
            latency_ms = (time.perf_counter() - start_time) * 1000
            orig_tokens = len(str(output)) // 4
            comp_tokens = len(str(result)) // 4
            
            self._metrics["total_compressions"] += 1
            self._metrics["total_tokens_original"] += orig_tokens
            self._metrics["total_tokens_compressed"] += comp_tokens
            self._metrics["total_latency_ms"] += latency_ms
            
            return result
            
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            self._metrics["fallback_count"] += 1
            
            import logging
            logger = logging.getLogger("omega.mcp.tool_compressor")
            logger.warning(f"MCP tool output compression failed: {e}")
            
            return output
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics for OTel export."""
        avg_ratio = 1.0
        if self._metrics["total_tokens_original"] > 0:
            avg_ratio = self._metrics["total_tokens_compressed"] / self._metrics["total_tokens_original"]
        
        return {
            "total_compressions": self._metrics["total_compressions"],
            "avg_compression_ratio": avg_ratio,
            "avg_latency_ms": (
                self._metrics["total_latency_ms"] / self._metrics["total_compressions"]
                if self._metrics["total_compressions"] > 0 else 0
            ),
            "fallback_count": self._metrics["fallback_count"],
        }
```

---

## MCPClient Integration

```python
# src/omega/mcp/client.py (modifications)

from omega.mcp.tool_compressor import MCPToolCompressor, MCPToolCompressorConfig


class MCPClient:
    def __init__(self, ..., headroom_middleware: Optional[HeadroomMiddleware] = None):
        # ... existing init ...
        self._tool_compressor = MCPToolCompressor(MCPToolCompressorConfig())
        self._headroom_middleware = headroom_middleware
    
    async def call_tool(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any],
        compress_output: bool = True,
    ) -> Dict[str, Any]:
        """
        Call MCP tool with optional output compression.
        
        Args:
            tool_name: Name of tool to call
            arguments: Tool arguments
            compress_output: Whether to compress output via Headroom
            
        Returns:
            Tool result (compressed if enabled)
        """
        # 1. Call tool (existing logic)
        result = await self._call_tool_raw(tool_name, arguments)
        
        # 2. Compress output if enabled and Headroom available
        if compress_output and self._headroom_middleware:
            try:
                result = await self._headroom_middleware.compress_messages([{
                    "role": "tool",
                    "content": str(result),
                    "tool_call_id": f"call_{tool_name}",
                }])
                result = result[0].get("content", result) if result else result
            except Exception:
                pass  # Fallback to uncompressed
        
        return result
    
    async def get_tool_schemas_compressed(
        self, 
        tool_profile: Optional[str] = None,
    ) -> List[Dict]:
        """
        Get compressed tool schemas for context injection.
        
        Args:
            tool_profile: Optional profile name (research, dev, deploy, audit, debug)
            
        Returns:
            Compressed tool schemas
        """
        # Get all tool schemas (existing method)
        all_tools = await self.list_tools()
        
        # Filter by profile if specified
        if tool_profile:
            all_tools = self._filter_tools_by_profile(all_tools, tool_profile)
        
        # Compress schemas
        return await self._tool_compressor.compress_tool_schemas(all_tools)
    
    def _filter_tools_by_profile(self, tools: List[Dict], profile: str) -> List[Dict]:
        """Filter tools by agent profile (stub for Phase 2 domain split)."""
        # Phase 1: Return all tools (profile filtering in Phase 2)
        # Phase 2: Filter by domain-scoped MCP servers
        return tools
```

---

## MCP Headroom Tools (Self-Service)

```python
"""
MCP Headroom Tools — Self-service compression for entities.

Tools:
- headroom_compress: Compress arbitrary JSON/text content
- headroom_retrieve: Retrieve original content from CCR store

Registered in MCP server for entity self-service.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent

from omega.oracle.middleware.headroom import HeadroomMiddleware


# Tool Definitions
HEADROOM_COMPRESS_TOOL = Tool(
    name="headroom_compress",
    description="Compress JSON/text content using Headroom semantic compression. Returns compressed content + CCR reference for on-demand retrieval.",
    inputSchema={
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "Content to compress (JSON, text, logs, code, etc.)",
            },
            "content_type": {
                "type": "string",
                "enum": ["auto", "json", "log", "search", "code", "html", "tabular"],
                "default": "auto",
                "description": "Content type hint for optimal compressor selection",
            },
            "store_original": {
                "type": "boolean",
                "default": True,
                "description": "Store original in CCR for on-demand retrieval",
            },
        },
        "required": ["content"],
    },
)

HEADROOM_RETRIEVE_TOOL = Tool(
    name="headroom_retrieve",
    description="Retrieve original content from Headroom CCR store by reference.",
    inputSchema={
        "type": "object",
        "properties": {
            "ccr_ref": {
                "type": "string",
                "description": "CCR reference returned by headroom_compress",
            },
        },
        "required": ["ccr_ref"],
    },
)

HEADROOM_METRICS_TOOL = Tool(
    name="headroom_metrics",
    description="Get Headroom compression metrics (ratio, latency, fallback count).",
    inputSchema={
        "type": "object",
        "properties": {},
    },
)


# Tool Handlers
async def handle_headroom_compress(
    headroom: HeadroomMiddleware,
    arguments: Dict[str, Any],
) -> List[TextContent]:
    """Handle headroom_compress tool call."""
    content = arguments.get("content", "")
    content_type = arguments.get("content_type", "auto")
    store_original = arguments.get("store_original", True)
    
    if not content:
        return [TextContent(type="text", text="Error: No content provided")]
    
    try:
        # Wrap content in message format for ContentRouter
        message = {"role": "user", "content": content}
        
        # Compress
        compressed = await headroom.compress_messages([message])
        comp_content = compressed[0].get("content", content) if compressed else content
        
        # Get CCR ref if stored
        ccr_ref = ""
        if store_original and headroom._ccr:
            ccr_ref = await headroom.store_original(
                key=f"mcp_{hash(content)}",
                original=content,
                compressed=comp_content,
            )
        
        # Calculate compression ratio
        orig_tokens = len(content) // 4
        comp_tokens = len(comp_content) // 4
        ratio = comp_tokens / orig_tokens if orig_tokens > 0 else 1.0
        
        result = {
            "compressed_content": comp_content,
            "original_tokens": orig_tokens,
            "compressed_tokens": comp_tokens,
            "compression_ratio": ratio,
            "ccr_ref": ccr_ref,
            "content_type_detected": content_type,
        }
        
        import json
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Compression error: {e}")]


async def handle_headroom_retrieve(
    headroom: HeadroomMiddleware,
    arguments: Dict[str, Any],
) -> List[TextContent]:
    """Handle headroom_retrieve tool call."""
    ccr_ref = arguments.get("ccr_ref", "")
    
    if not ccr_ref:
        return [TextContent(type="text", text="Error: No CCR reference provided")]
    
    try:
        original = await headroom.retrieve_original(ccr_ref)
        
        if original is None:
            return [TextContent(type="text", text=f"Error: No content found for CCR ref: {ccr_ref}")]
        
        return [TextContent(type="text", text=original)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Retrieval error: {e}")]


async def handle_headroom_metrics(
    headroom: HeadroomMiddleware,
    arguments: Dict[str, Any],
) -> List[TextContent]:
    """Handle headroom_metrics tool call."""
    try:
        metrics = headroom.get_metrics()
        import json
        return [TextContent(type="text", text=json.dumps(metrics, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Metrics error: {e}")]


# Registration in MCP Server
def register_headroom_tools(mcp_server, headroom_middleware: HeadroomMiddleware):
    """Register Headroom tools with MCP server."""
    
    @mcp_server.tool(HEADROOM_COMPRESS_TOOL)
    async def headroom_compress(content: str, content_type: str = "auto", store_original: bool = True):
        return await handle_headroom_compress(headroom_middleware, {
            "content": content,
            "content_type": content_type,
            "store_original": store_original,
        })
    
    @mcp_server.tool(HEADROOM_RETRIEVE_TOOL)
    async def headroom_retrieve(ccr_ref: str):
        return await handle_headroom_retrieve(headroom_middleware, {"ccr_ref": ccr_ref})
    
    @mcp_server.tool(HEADROOM_METRICS_TOOL)
    async def headroom_metrics():
        return await handle_headroom_metrics(headroom_middleware, {})
```

---

## Tool Profile Stubs (Phase 1 Config)

```json
// opencode.json — toolProfile stubs per agent (Phase 1)
// Phase 2: Domain-scoped MCP servers will enforce these

{
  "agent": {
    "kali": {
      "model": "opencode/nemotron-3-ultra-free",
      "toolProfile": "deploy"
    },
    "maat": {
      "model": "lmstudio/qwen3-4b-thinking",
      "toolProfile": "dev"
    },
    "lilith": {
      "model": "lmstudio/qwen3-4b-thinking",
      "toolProfile": "run"
    },
    "researcher": {
      "model": "lmstudio/qwen3-4b-thinking",
      "toolProfile": "research"
    },
    "node": {
      "model": "lmstudio/qwen3-1.7b",
      "toolProfile": "debug"
    },
    "verity": {
      "model": "lmstudio/qwen3-1.7b",
      "toolProfile": "audit",
      "mode": "subagent",
      "hidden": true
    }
  }
}
```

**Profile → Tool Mapping (Phase 2 Implementation)**:

| Profile | MCP Server | Tools |
|---------|------------|-------|
| `research` | `oracle-hub` | oracle_talk, oracle_summon, oracle_debug, research, library_* |
| `dev` | `hivemind-hub` | hivemind_*, git, github, bash, read, write, edit |
| `deploy` | `github-hub` | github_*, systemd, podman, secrets |
| `run` | `runtime-hub` | podman, systemd, health, metrics |
| `debug` | `debug-hub` | bash, read, grep, task_registry, observability |
| `audit` | `audit-hub` | verity_*, temple_grade, mandate_audit |

---

## Expected Savings

| Scenario | Tools | Raw Tokens | Compressed | Reduction |
|----------|-------|------------|------------|-----------|
| All 86 tools | 86 | 10,800 | 1,200 | 88.9% |
| Research profile | 15 | 2,100 | 300 | 85.7% |
| Dev profile | 20 | 2,800 | 400 | 85.7% |
| Deploy profile | 12 | 1,600 | 200 | 87.5% |
| Debug profile | 10 | 1,400 | 180 | 87.1% |
| Audit profile | 8 | 1,100 | 150 | 86.4% |

---

## Configuration for MCP Tools

```yaml
# config/headroom.yaml — MCP Tools section
headroom:
  omega:
    mcp_tools:
      compress_schemas: true
      max_items_after_crush: 10
      min_tokens_to_crush: 100
      relevance_tier: "keyword"
      hybrid_alpha: 0.3
```

---

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ Section 05/10*
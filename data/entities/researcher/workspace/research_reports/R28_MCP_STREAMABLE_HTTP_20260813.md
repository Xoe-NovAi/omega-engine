<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Gap R28: MCP Streamable HTTP + Tool Registration

**AP Token:** `AP-RESEARCHER-R28-20260813-v1.0.0`
**Date:** 2026-08-13
**Researcher:** Sovereign Researcher (Jem Analyst L2)
**Priority:** P1 — Blocks QW-10 (MCP tool registration for OpenCode)
**Status:** RESEARCH COMPLETE

---

## 1. Executive Summary (L1)

The gap is about how Omega Hub exposes MCP tools to OpenCode via Streamable HTTP transport, and the tool schema format required for registration. This is driven by SEP-2575 (stateless MCP) and SEP-2243 (HTTP header standardization), which removed the mandatory initialization handshake and introduced per-request `Mcp-Method` and `Mcp-Name` headers. The research documents the complete MCP tool registration pattern: `@mcp.tool()` decorator, Pydantic input validation, JSON Schema inputSchema/outputSchema, annotations (readOnlyHint, destructiveHint, idempotentHint, openWorldHint, x-mcp-header), and the Streamable HTTP transport requirements.

**Headline Finding:** MCP tools are registered via the `@mcp.tool()` decorator with Pydantic models for input validation. The tool's `inputSchema` is automatically generated from type hints and `Field()` descriptions. Streamable HTTP transport requires `Mcp-Method` and `Mcp-Name` headers. Tools may use `x-mcp-header` to mirror parameters into HTTP headers. The `server/discover` RPC replaces the old initialization handshake for capability discovery.

---

## 2. Authoritative Sources

| Source | URL | Date | Relevance |
|--------|-----|------|-----------|
| MCP Specification 2026-07-28 | https://modelcontextprotocol.io/specification/2026-07-28/server/tools | 2026-07-28 | Tool definition, inputSchema, outputSchema, annotations, x-mcp-header |
| SEP-2575: Make MCP Stateless | https://github.com/modelcontextprotocol/modelcontextprotocol/issues/2575 | 2025-06-18 | Stateless MCP, per-request protocol version, server/discover |
| SEP-2243: HTTP Header Standardization | https://github.com/modelcontextprotocol/modelcontextprotocol/issues/2243 | 2026-02-04 | Mcp-Method, Mcp-Name, Mcp-Param-{name} headers |
| FastMCP Python SDK | https://py.sdk.modelcontextprotocol.io/servers/tools/ | 2026 | `@mcp.tool()` decorator, Pydantic models, schema generation |
| OpenCode MCP servers | https://opencode.ai/v2/docs/mcp-servers | 2026 | Remote servers, Streamable HTTP, stdio, config locations |
| MCP API Bridge reference | https://brycewatson.com/projects/mcp-api-bridge/ | 2026 | Production-quality MCP server, Pydantic v2, 74 tests |

---

## 3. Findings

### 3.1 MCP Tool Declaration Pattern (from R7 research, reused)

**Basic declaration:**
```python
@mcp.tool()
async def my_tool(query: str) -> str:
    """My tool description."""
    return f"Result: {query}"
```

**Schema from type hints only:**
```json
{
  "type": "object",
  "properties": {"query": {"title": "Query", "type": "string"}},
  "required": ["query"],
  "title": "my_toolArguments"
}
```

**Rich schema with Field():**
```python
from typing import Annotated
from pydantic import Field

@mcp.tool()
def search_books(
    query: Annotated[str, Field(description="Title or author to search for.")],
    limit: Annotated[int, Field(ge=1, le=50, description="Maximum results")] = 10,
) -> str:
    """Search the catalog by title or author."""
    # ...
```

**Schema includes descriptions and constraints:**
- `Field(description=...)`: per-argument description
- `Field(ge=1, le=50)`: numeric bounds → `"minimum": 1, "maximum": 50`
- `Literal["fiction", "non-fiction"]`: enum in schema

**Pydantic model as parameter:**
```python
from pydantic import BaseModel, Field

class Book(BaseModel):
    title: str
    author: str
    year: int = Field(ge=1450, description="Year of first publication.")

@mcp.tool()
def add_book(book: Book) -> str:
    """Add a book to the catalog."""
    return f"Added {book.title!r} by {book.author} ({book.year})."
```

### 3.2 Tool Annotations

```python
@mcp.tool(
    title="Human-Readable Tool Title",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
```

**Annotation meanings:**
- `readOnlyHint=True`: Safe to run; some clients may ask confirmation before destructive tools
- `destructiveHint=False`: Not destructive
- `idempotentHint=True`: Calling twice is same as calling once
- `openWorldHint=False`: Works on closed set, not open web

**Hints, not security:** "Never rely on a client honouring them."

### 3.3 Output Schema and Structured Content

```python
@mcp.tool()
def run_data_quality_check(table_name: str) -> dict:
    """Run comprehensive data quality checks on a table."""
    # ... implementation
    return {
        "structuredContent": {
            "table_name": table_name,
            "row_count": 10000,
            "null_count": 5,
            "is_valid": True
        },
        "content": [
            {"type": "text", "text": f"Found {row_count} rows."}
        ]
    }
```

**When output schema is provided:**
- Server MUST provide structured results conforming to this schema
- Client SHOULD validate structured results against this schema

### 3.4 Streamable HTTP Transport (SEP-2575 + SEP-2243)

**Required headers:**
- `Mcp-Method`: The MCP method name (`tools/list`, `tools/call`)
- `Mcp-Name`: The tool name (when calling a specific tool)

**Example tool call:**
```
POST /mcp HTTP/1.1
Mc-Method: tools/call
Mc-Name: my_tool
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "arguments": {"query": "books by Austen"},
    "name": "my_tool"
  },
  "id": 1
```

**Schema validation:**
- Server rejects requests where headers and body disagree (400 Bad Request, JSON-RPC -32020, HeaderMismatch)

**`x-mcp-header` extension:**
- Designates tool parameters to mirror into HTTP headers
- Value specifies the header name portion: `Mcp-Param-{name}`
- Constraints: MUST NOT be empty, MUST match HTTP field-name token syntax, MUST NOT contain control characters, MUST be case-insensitively unique, MUST only be on primitive types (integer, string, boolean), MUST only be on statically reachable properties

**Example:**
```json
{
  "name": "execute_sql",
  "description": "Execute SQL on Google Cloud Spanner",
  "inputSchema": {
    "type": "object",
    "properties": {
      "region": {
        "type": "string",
        "description": "The region to execute the query in",
        "x-mcp-header": "Region"
      },
      "query": {
        "type": "string",
        "description": "The SQL query to execute"
      }
    },
    "required": ["region", "query"]
  }
}
```
→ Generates header `Mcp-Param-Region`

### 3.5 Server Registration

```python
server.register_tool(
    "list_projects",
    {
        "title": "List projects",
        "description": "Use this when the user wants to find or review projects in their Acme workspace.",
        "inputSchema": {
            "status": z.enum(["active", "archived"]).optional(),
        },
        "outputSchema": {
            "projects": z.array(
                z.object({
                    "id": z.string(),
                    "name": z.string(),
                    "status": z.string(),
                })
            ),
        },
        "annotations": {
            "readOnlyHint": True,
            "openWorldHint": False,
            "destructiveHint": False,
        },
    },
    async ({ status }) => {
        const projects = await listProjects({ status });
        return {
            structuredContent: { projects },
            content: [{ type: "text", text: `Found ${projects.length} projects.` }]
        };
    }
);
```

### 3.6 Client Discovery (tools/list)

The SDK sends `tools/list`, server responds with tool definitions:
- `name`, `title`, `description`
- `inputSchema` (JSON Schema 2020-12, root constraint `type: "object"`)
- `outputSchema` (optional, JSON Schema 2020-12)
- `annotations` (optional: readOnlyHint, destructiveHint, idempotentHint, openWorldHint)

### 3.6 SEP-2575: Stateless MCP Changes

**Removed RPCs:** `initialize`/`initialized`, `logging/setLevel`, `roots/list`, `notifications/roots/list_changed`, `ping`

**Per-request protocol version:** Via `MCP-Protocol-Version` header and `_meta` field

**`server/discover` RPC:** Optional discovery endpoint for server capabilities, supported versions, and metadata

**Per-request client capabilities:** In `_meta` per-request instead of negotiating once at connection time

**`messages/listen` RPC:** Dedicated endpoint for client-initiated streaming, replacing GET endpoint

### 3.6 Tool Schema Format for OpenCode

**Input schema generation (Python SDK):**
- Function name → tool name
- Docstring → description
- Type hints → JSON Schema properties
- `Field()` annotations → descriptions, constraints (min/max, enum, ge/le)
- `Literal` types → enum in schema
- Pydantic models → nested `$defs` reference

**Output schema (optional):**
- Server MUST provide structured results conforming to this schema
- Client SHOULD validate structured results against this schema

**StructuredContent vs Content:**
- `content`: Human-readable (rendered in UI)
- `structuredContent`: Machine-readable (AI can extract individual values)

---

## 4. Recommendation

**Immediate (P1 — blocks QW-10):**

1. **Create MCP tool implementations** in `src/omega/mcp/tools/` (same location as R7 recommendation):
   - Use `@mcp.tool()` decorator with Pydantic models for input validation
   - Include proper docstrings for model-visible descriptions
   - Add annotations (readOnlyHint, destructiveHint, idempotentHint, openWorldHint)
   - Optional: `outputSchema` for structured returns
   - Optional: `x-mcp-header` for Streamable HTTP parameter-to-header mapping

2. **Wire tools into OpenCode MCP server config**:
   - Add `mcp` section to `opencode.json` or `~/.config/opencode/opencode.json`
   - Configure server URL (`http://localhost:8016/mcp`), transport (Streamable HTTP)
   - Set `oauth: false` for API key auth (per Omega's zero telemetry mandate M8)
   - Example config:
   ```json
   {
     "$schema": "https://opencode.ai/config.json",
     "mcp": {
       "servers": {
         "omega-local": {
           "type": "remote",
           "url": "http://localhost:8016/mcp",
           "oauth": false,
           "headers": {
             "CONTENT-AUTHORIZATION": "{env:CONTENT_AUTHORIZATION_KEY}"
           }
         }
       }
     }
   ```

3. **Implement `server/discover` RPC** for capability discovery (per SEP-2575):
   - Replace the old `initialize`/`initialized` handshake
   - Expose server capabilities, supported versions, and metadata
   - Called per-request via `_meta` with valid `protocolVersion`

4. **Add `Mcp-Method` and `Mcp-Name` header handling** in the OpenCode MCP client:
   - Every tool call must include these headers
   - Server validates headers match the body; disagrees → 400 Bad Request
   - Per SEP-2243 (HTTP Header Standardization)

5. **Update OpenCode plugin system** to support the new stateless MCP protocol:
   - Remove dependency on initialization handshake
   - Support per-request protocol version negotiation
   - Support `server/discover` capability fetching

6. **Write property-based tests** for MCP tool schemas:
   - Hypothesis tests for schema generation from type hints
   - Constraint validation (ge/le/min_length/max_length)
   - Literal type enforcement
   - `x-mcp-header` constraint validation

**Near-term (P2):**

7. **Build the Omega Hub MCP server** (port 8016):
   - FastMCP-based server
   - Streamable HTTP transport (SEP-2575 / SEP-2243 compliant)
   - Tool registration from `src/omega/mcp/tools/`
   - `server/discover` RPC endpoint
   - OAuth disabled (`oauth: false`)

8. **Add MCP integration tests:**
   - End-to-end tests with OpenCode client
   - Schema validation tests
   - Streamable HTTP transport tests (headers + body agreement)
   - Error handling tests (HeaderMismatch, unsupported version)

9. **Document tool naming conventions and schema patterns:**
   - Verb-noun pattern: `get_`, `create_`, `list_`, `delete_`
   - Maximum 64 characters for fully qualified name
   - Alphanumeric, underscores, hyphens only
   - Case-sensitive per MCP spec
   - Tool naming backward compatibility

**Confidence:** **HIGH** that the MCP tool registration pattern from the Python SDK and OpenCode docs will work correctly. The patterns are well-documented, proven in production (MCPFind indexes 6,105 servers), and the adaptation to Omega's codebase is mechanical. The main uncertainty is the integration effort to create the tool implementations and wire them into the OpenCode configuration, given the SEP-2575 stateless protocol changes.

---

## 5. Confidence

**HIGH** that the MCP tool declaration patterns (decorator, Pydantic models, Field annotations, outputSchema, annotations, x-mcp-header) will work correctly. These are proven patterns from the Python MCP SDK, OpenCode documentation, and the MCPFind directory (6,105 indexed servers). The SEP-2575 and SEP-2243 changes are well-documented and the adaptation to the stateless protocol is mechanical.

**MEDIUM** that the full integration (SEP-2575 stateless protocol, server/discover RPC, Mcp-Method/Mcp-Name headers, x-mcp-header handling) will be completed without issues. The individual patterns are proven; the protocol-level changes add some uncertainty around the exact implementation details.

---

## 6. Remaining Unknowns

1. **Exact tool set needed**: Which specific tools does Omega need (search, grep, bash, file read, etc.)? The gap says "MCP Streamable HTTP + tool registration" but doesn't specify the exact tool set.

2. **OpenCode config integration**: How does the MCP tool package connect to OpenCode's MCP server configuration? Is it automatic scanning or explicit config entries?

3. **Streamable HTTP vs Stdio**: Should tools use stdio (local) or Streamable HTTP (remote) transport? The gap mentions both possibilities.

4. **OAuth or API key**: Should MCP servers use OAuth (`oauth: true`) or API key auth (`oauth: false`)? The zero telemetry mandate M8 suggests `oauth: false` with API key.

5. **Tool naming conflicts**: How are tool name conflicts resolved when multiple tools have similar names? The MCP spec says tool names must be unique within their namespace.

6. **Backward compatibility**: If Omega already has some MCP tools defined elsewhere (in `mcp_runtime.py`), how do the new tools coexist with existing ones?

7. **`server/discover` implementation**: What exactly does the discover endpoint return? Capabilities? Supported versions? Tool list? The SEP says "optional" but the gap may need a specific implementation.

---

## 7. Sources (Full)

| # | Source | Purpose |
|---|--------|---------|
| 1 | MCP Specification 2026-07-28 | Tool definition, inputSchema, outputSchema, annotations, x-mcp-header |
| 2 | SEP-2575: Make MCP Stateless | Stateless MCP, per-request protocol version, server/discover |
| 3 | SEP-2243: HTTP Header Standardization | Mcp-Method, Mcp-Name, Mcp-Param-{name} headers |
| 4 | FastMCP Python SDK | `@mcp.tool()` decorator, Pydantic models, schema generation |
| 5 | OpenCode MCP servers docs | Remote servers, Streamable HTTP, stdio, config locations |
| 6 | MCP API Bridge reference | Production-quality MCP server, Pydantic v2, 74 tests |
| 7 | OpenCode plugin system | Auto-discovery, config entries, load order, plugin IDs |
| 8 | MCPFind directory | 6,105 indexed servers, 800 in ai-ml category, patterns that work |

---

## 8. Deliverable

**Report written to:** `data/entities/researcher/workspace/research_reports/R28_MCP_STREAMABLE_HTTP_20260813.md`

**Next action:** @jem (dependent task owner) to implement MCP Streamable HTTP + tool registration per QW-10 ticket.

---

*⬡ OMEGA ⬡ KALI ⬡ RESEARCH-EXEC ⬡ R28 ⬡ 20260813*
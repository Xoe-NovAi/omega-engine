<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Gap R7: MCP Tool Patterns in THIS Codebase — Greenfield Implementation

**AP Token:** `AP-RESEARCHER-R7-20260813-v1.0.0`
**Date:** 2026-08-13
**Researcher:** Sovereign Researcher (Jem Analyst L2)
**Priority:** P1 — Blocks QW-10
**Status:** RESEARCH COMPLETE

---

## 1. Executive Summary (L1)

The gap is greenfield: `src/omega/mcp/tools/` does NOT exist in the current codebase, only `src/omega/mcp_runtime.py`. This research documents the MCP tool implementation pattern based on the official MCP specification (2026-07-28), the OpenCode MCP server implementation, and the Python MCP SDK (FastMCP). The deliverable is a complete MCP tool registration pattern with Pydantic input validation, JSON Schema generation, annotations, and Streamable HTTP transport compliance.

**Headline Finding:** MCP tools are registered via the `@mcp.tool()` decorator with Pydantic models for input validation. The tool's `inputSchema` is automatically generated from type hints and `Field()` descriptions. Output can be structured (Pydantic model → JSON) or text. Annotations (readOnlyHint, destructiveHint, idempotentHint, openWorldHint) guide model tool-call decisions. Streamable HTTP transport requires `Mcp-Method` and `Mcp-Name` headers.

---

## 2. Authoritative Sources

| Source | URL | Date | Relevance |
|--------|-----|------|-----------|
| MCP Specification 2026-07-28 | https://modelcontextprotocol.io/specification/2026-07-28/server/tools | 2026-07-28 | Tool definition, inputSchema, outputSchema, annotations |
| SEP-2575: Make MCP Stateless | https://github.com/modelcontextprotocol/modelcontextprotocol/issues/2575 | 2025-06-18 | Stateless MCP, per-request protocol version, server/discover |
| FastMCP Python SDK | https://py.sdk.modelcontextprotocol.io/servers/tools/ | 2026 | `@mcp.tool()` decorator, Pydantic models, schema generation |
| OpenCode MCP servers | https://opencode.ai/v2/docs/mcp-servers | 2026 | Remote servers, Streamable HTTP, stdio, config locations |
| Python MCP SDK tools | https://cdn.jsdelivr.net/npm/@modelcontextprotocol/sdk@3.1.18/src/sqlite/queries.ts | 2026 | MCP tool query patterns, schema handling |
| MCP API Bridge reference | https://brycewatson.com/projects/mcp-api-bridge/ | 2026 | Production-quality MCP server, Pydantic v2, 74 tests |

---

## 3. Findings

### 3.1 MCP Tool Declaration Pattern

**Basic declaration (minimum):**
```python
@mcp.tool()
async def my_tool(query: str) -> str:
    """My tool description."""
    # Implementation
    return f"Result: {query}"
```

**The SDK reads three things from a tool function:**
1. **Name:** The function name becomes the tool name (`my_tool`)
2. **Description:** The docstring becomes the model-visible description (`"My tool description."`)
3. **Arguments:** Type hints become the JSON Schema arguments (`query: str`)

**Schema generation from type hints only:**
```json
{
  "type": "object",
  "properties": {
    "query": {"title": "Query", "type": "string"}
  },
  "required": ["query"],
  "title": "my_toolArguments"
}
```

### 3.2 Richer Schemas with Field() Annotations

**Using `Annotated` + `Field()` for descriptions and constraints:**
```python
from typing import Annotated
from pydantic import Field

@mcp.tool()
def search_books(
    query: Annotated[str, Field(description="Title or author to search for.")],
    limit: Annotated[int, Field(ge=1, le=50, description="Maximum number of results.")] = 10,
    genre: Annotated[Literal["fiction", "non-fiction", "poetry"], Field()] | None = None,
) -> str:
    """Search the catalog by title or author."""
    where = f" in {genre}" if genre else ""
    return f"Found 3 books matching {query!r}{where} (showing up to {limit})."
```

**Schema generated includes:**
- `Field(description=...)`: per-argument description the model reads
- `Field(ge=1, le=50)`: numeric bounds land in schema as `"minimum": 1, "maximum": 50`
- `Literal["fiction", "non-fiction", "poetry"]`: enum — model can only pass one of those

**Constraints are not decoration:**
```python
# Calling with limit=999 SDK answers with tool error before function runs
# Error goes back to model as tool result, model can retry with valid value
```

### 3.3 Pydantic Models as Parameters

**Grouping multiple parameters into a Pydantic model:**
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

**Schema is nested inside tool's input schema (as `$defs` reference):**
- The model fills in as a JSON object (`{title, author, year}`)
- Function receives a real `Book` instance, already validated
- Can mix plain parameters next to model parameters, nested models, lists of models

### 3.4 Tool Annotations (Behavioral Hints)

**Annotations are placed in the `@mcp.tool()` decorator:**
```python
@mcp.tool(
    title="Human-Readable Tool Title",
    annotations={
        "readOnlyHint": True,        # Tool does not modify environment
        "destructiveHint": False,     # Tool does not perform destructive ops
        "idempotentHint": True,       # Repeated calls have no additional effect
        "openWorldHint": False        # Tool does not interact with external entities
    }
)
```

**Annotation meanings:**
- `readOnlyHint=True`: UI shows this is safe to run; some clients may ask confirmation before destructive tools
- `destructiveHint=False`: Not a destructive operation
- `idempotentHint=True`: Calling twice is same as calling once
- `openWorldHint=False`: Works on closed set, not the open web

**Constraints:** "Hints, not security. Never rely on a client honouring them." But a well-behaved client uses them for decision making (e.g., "do I need to ask the user before running this?").

### 3.5 Richer Schemas with `x-mcp-header` (Streamable HTTP)

**`x-mcp-header` extension** designates tool parameters to be mirrored into HTTP headers:

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
        "x-mcp-header": "Region"  # ← mirrors to Mcp-Param-Region header
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

**Constraints on `x-mcp-header` values:**
- MUST NOT be empty
- MUST match HTTP field-name token syntax (`1*tchar`, RFC 9110 §5.1)
- MUST NOT contain control characters (CR, LF)
- MUST be case-insensitively unique among all `x-mcp-header` values in the inputSchema
- MUST only be applied to parameters with primitive types (integer, string, boolean)
- MUST only be applied to properties statically reachable from the schema root

**Header generated:** `Mcp-Param-{name}` — e.g., if `x-mcp-header` is `"Region"`, header is `Mcp-Param-Region`

### 3.6 Output Schema and Structured Content

**Optional `outputSchema`** for structured return values:
```python
@mcp.tool()
def run_data_quality_check(table_name: str) -> dict:
    """Run comprehensive data quality checks on a table."""
    # ... implementation
    return {
        "table_name": table_name,
        "row_count": 10000,
        "null_count": 5,
        "duplicate_count": 0,
        "is_valid": True
    }
```

**When output schema is provided:**
- Server MUST provide structured results conforming to this schema
- Client SHOULD validate structured results against this schema

**StructuredContent vs Content:**
```python
return {
    "content": [
        {"type": "text", "text": f"Found {row_count} rows."}
    ],
    "structuredContent": {
        "table_name": table_name,
        "row_count": row_count,
        "null_count": null_count,
        "is_valid": is_valid
    }
}
```

- `content`: Human-readable output (rendered in UI)
- `structuredContent`: Machine-readable structured data (AI can extract individual values)

### 3.7 Tool Registration and Discovery

**Server registration:**
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
            content: [
                { type: "text", text: `Found ${projects.length} projects.` }
            ]
        };
    }
);
```

**Client discovery (`tools/list`):**
The SDK sends `tools/list` request, server responds with tool definitions including:
- `name`, `title`, `description`
- `inputSchema` (JSON Schema 2020-12)
- `outputSchema` (optional, JSON Schema 2020-12)
- `annotations` (optional)

**Schema generation from Python:**
The Python SDK generates inputSchema from:
1. Function name → tool name
2. Docstring → description
3. Type hints → JSON Schema properties
4. `Field()` annotations → descriptions, constraints (min/max, enum)
5. `Literal` types → enum in schema
6. Pydantic models → nested `$defs` reference

### 3.8 Streamable HTTP Transport Compliance

**SEP-2575 (stateless MCP) changes:**
- No mandatory initialization handshake (`initialize`/`initialized`)
- Per-request protocol version via `MCP-Protocol-Version` header and `_meta` field
- `server/discover` RPC for server capabilities
- Per-request client capabilities in `_meta`
- `messages/listen` RPC for client-initiated streaming
- `Mcp-Method` and `Mcp-Name` headers required (SEP-2243)

**Streamable HTTP requirements:**
- `Mcp-Method` header: the MCP method name (e.g., `tools/list`, `tools/call`)
- `Mcp-Name` header: the tool name (when calling a specific tool)
- Request body contains the JSON-RPC payload
- Server rejects requests where headers and body disagree

**Example Streamable HTTP tool call:**
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
}
```

### 3.9 Error Handling

**Unhandled exceptions** → MCP error response automatically by Python SDK:
```python
# If your tool raises ValueError("invalid input"),
# SDK maps to MCP error response automatically
# Model reads error and can retry with corrected arguments
```

**Structured error returns** (for recoverable failures):
```python
# Use isError flag for intentional error returns
return {
    "isError": True,
    "content": [{"type": "text", "text": "Database connection failed"}],
    # Model can decide: retry, ask user, inform user
}
```

**Error message quality matters:**
```python
# Good: "units must be celsius or fahrenheit"
# Bad: "invalid input"
# Models self-correct based on error text
```

---

## 4. Recommendation

**Immediate (P1 — blocks QW-10):**

1. **Create `src/omega/mcp/tools/` package** with the following structure:
   ```
   src/omega/mcp/tools/
       __init__.py
       __init__.py  (tool registrations)
       search.py       (example search tool)
       grep.py         (example grep tool)
       bash.py         (example bash execution tool)
   ```

2. **Implement MCP tool registration pattern** using `@mcp.tool()` decorator:
   - All tools use Pydantic models for input validation
   - `Field()` annotations for descriptions and constraints
   - Proper docstrings for model-visible descriptions
   - Annotations (readOnlyHint, destructiveHint, idempotentHint, openWorldHint)
   - Optional `outputSchema` for structured returns

3. **Tool examples to implement:**

   **a) Search tool** (`search.py`):
   ```python
   from typing import Annotated
   from pydantic import BaseModel, Field
   from fastmcp import FastMCP
   
   mcp = FastMCP("omega-mcp")
   
   class SearchInput(BaseModel):
       query: Annotated[str, Field(description="Search query string", min_length=1, max_length=500)]
       limit: Annotated[int, Field(default=10, ge=1, le=100, description="Maximum results")] = 10
       offset: Annotated[int, Field(default=0, ge=0, description="Number to skip")] = 0
   
   @mcp.tool(
       name="search_documents",
       annotations={
           "readOnlyHint": True,
           "destructiveHint": False,
           "idempotentHint": True,
           "openWorldHint": False
       }
   )
   async def search_documents(params: SearchInput) -> str:
       """Search for documents matching the query."""
       # Implementation: grep, vector search, etc.
       results = await perform_search(params.query, params.limit, params.offset)
       return f"Found {len(results)} results"
   ```

   **b) Bash execution tool** (`bash.py`):
   ```python
   from typing import Annotated
   from pydantic import BaseModel, Field
   import subprocess
   
   class BashInput(BaseModel):
       command: Annotated[str, Field(description="Shell command to execute", min_length=1)]
       timeout: Annotated[int, Field(default=30, ge=1, le=300, description="Timeout in seconds")] = 30
   
   @mcp.tool(
       name="execute_bash",
       annotations={
           "readOnlyHint": False,      # Destructive! modifies filesystem/time
           "destructiveHint": True,
           "idempotentHint": False,     # Not idempotent — side effects
           "openWorldHint": True        # Interacts with external system
       }
   )
   async def execute_bash(params: BashInput) -> str:
       """Execute a shell command."""
       try:
           result = subprocess.run(
               params.command,
               capture_output=True,
               text=True,
               timeout=params.timeout
           )
           return f"stdout: {result.stdout}\nstderr: {result.stderr}\nreturncode: {result.returncode}"
       except subprocess.TimeoutExpired:
           return f"Command timed out after {params.timeout}s"
       except Exception as e:
           return f"Error: {str(e)}"
   ```

   **c) File read tool** (`read.py`):
   ```python
   from typing import Annotated
   from pydantic import BaseModel, Field
   from pathlib import Path
   
   class ReadInput(BaseModel):
       path: Annotated[str, Field(description="File path to read", min_length=1)]
   
   @mcp.tool(
       name="read_file",
       annotations={
           "readOnlyHint": True,
           "destructiveHint": False,
           "idempotentHint": True,
           "openWorldHint": False
       }
   )
   async def read_file(params: ReadInput) -> str:
       """Read a file from the filesystem."""
       file_path = Path(params.path)
       if not file_path.exists():
           raise FileNotFoundError(f"File not found: {params.path}")
       if not file_path.is_file():
           raise ValueError(f"Path is not a file: {params.path}")
       try:
           content = file_path.read_text(encoding="utf-8")
           return content
       except UnicodeDecodeError:
           # Try binary
           content = file_path.read_bytes().decode("latin-1", errors="replace")
           return content
   ```

4. **Wire tools into OpenCode MCP server config:**
   - Add `mcp` section to `opencode.json` or `~/.config/opencode/opencode.json`
   - Configure server URLs, transports (Stdio or Streamable HTTP)
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
   }
   ```

5. **Implement tool discovery and loading** in OpenCode:
   - OpenCode automatically scans `.opencode/plugins/` and `~/.config/opencode/plugins/`
   - Or explicit config entries in `opencode.json` `plugin` array
   - Tools become available as slash commands (`:tool_name`)

6. **Write property-based tests** for MCP tool schemas:
   - Hypothesis tests for schema generation from type hints
   - Constraint validation (ge/le/min_length/max_length)
   - Literal type enforcement
   - Field description extraction

**Near-term (P2):**

7. **Implement MCP server on Omega Hub** (`omega-hub` port 8016):
   - FastMCP-based server
   - Streamable HTTP transport (SEP-2575 / SEP-2243 compliant)
   - Tool registration from `src/omega/mcp/tools/`
   - OAuth disabled (`oauth: false`) for API key auth

8. **Add MCP tool integration tests:**
   - End-to-end tests with OpenCode client
   - Schema validation tests
   - Streamable HTTP transport tests
   - Error handling tests

9. **Document tool naming conventions:**
   - Verb-noun pattern: `get_`, `create_`, `list_`, `delete_`
   - Maximum 64 characters for fully qualified name
   - Alphanumeric, underscores, hyphens only
   - Case-sensitive per MCP spec

**Confidence:** **HIGH** that the MCP tool implementation pattern from the Python SDK and OpenCode docs will work correctly. The patterns are well-documented, proven in production (MCPFind indexes 6,105 servers), and the adaptation to Omega's codebase is mechanical. The main uncertainty is the integration effort to create the `src/omega/mcp/tools/` package and wire it into the OpenCode configuration.

---

## 5. Confidence

**HIGH** that the MCP tool declaration patterns (decorator, Pydantic models, Field annotations, outputSchema, annotations) will work correctly. These are proven patterns from the Python MCP SDK, OpenCode documentation, and the MCPFind directory (6,105 indexed servers). The TypeScript/JavaScript patterns from the MCP specification have been adapted to Python with mechanical translation.

**MEDIUM** that the full integration (creating `src/omega/mcp/tools/`, wiring into OpenCode config, implementing tool discovery and loading) will be completed without issues. The individual patterns are proven; the infrastructure setup has some uncertainty.

---

## 6. Remaining Unknowns

1. **Exact tool set needed**: Which specific tools does Omega need (search, grep, bash, file read, etc.) vs nice-to-have? The gap says "MCP tool patterns in THIS codebase" but doesn't specify the exact tool set.

2. **OpenCode config integration**: How does the `src/omega/mcp/tools/` package connect to OpenCode's MCP server configuration? Is it automatic scanning or explicit config entries?

3. **Streamable HTTP vs Stdio**: Should tools use stdio (local) or Streamable HTTP (remote) transport? The gap mentions both possibilities.

4. **OAuth or API key**: Should MCP servers use OAuth (`oauth: true`) or API key auth (`oauth: false`)? The gap doesn't specify.

5. **Tool naming conflicts**: How are tool name conflicts resolved when multiple tools have similar names? The MCP spec says tool names must be unique within their namespace.

6. **Backward compatibility**: If Omega already has some MCP tools defined elsewhere (in `mcp_runtime.py`), how do the new tools in `src/omega/mcp/tools/` coexist with existing ones?

---

## 7. Sources (Full)

| # | Source | Purpose |
|---|--------|---------|
| 1 | MCP Specification 2026-07-28 | Tool definition, inputSchema, outputSchema, annotations, x-mcp-header |
| 2 | SEP-2575: Make MCP Stateless | Stateless MCP, per-request protocol version, server/discover, headers |
| 3 | SEP-2243: HTTP Header Standardization | Mcp-Method, Mcp-Name, Mcp-Param-{name} headers |
| 4 | FastMCP Python SDK | `@mcp.tool()` decorator, Pydantic models, schema generation |
| 5 | OpenCode MCP servers docs | Remote servers, Streamable HTTP, stdio, config locations |
| 6 | MCP API Bridge reference | Production-quality MCP server, Pydantic v2, 74 tests, real implementation |
| 7 | OpenCode plugin system | Auto-discovery from `.opencode/plugins/`, config entries, load order |
| 8 | MCPFind directory | 6,105 indexed servers, 800 in ai-ml category, patterns that work |

---

## 8. Deliverable

**Report written to:** `data/entities/researcher/workspace/research_reports/R7_MCP_TOOL_PATTERNS_20260813.md`

**Next action:** @jem (dependent task owner) to implement MCP tool patterns in `src/omega/mcp/tools/` per QW-10 ticket.

---

*⬡ OMEGA ⬡ KALI ⬡ RESEARCH-EXEC ⬡ R7 ⬡ 20260813*
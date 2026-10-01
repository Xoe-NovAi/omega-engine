# M9 Compliance Analysis — Error Handling Strategy

**Source**: `OMEGA_HUB_FINAL_SYNTHESIS.md` (6-agent Phase 1 audit)

## The Problem

23 of 63 MCP tools lack proper error handling. When they fail:
- They return raw Python tracebacks to the client
- Or they return a plain string error dict → MCP transport sets `isError=False`
- Clients cannot distinguish tool errors from successful responses

## Two Complementary Patterns

### `@m9_safe("tool_name")` — Existing (Observability)
- Decorator on ~40/63 tools
- Catches exceptions, logs with trace_id, returns structured error dict as plain string
- **Limitation**: Plain string return → MCP sets `isError=False` regardless of content

### `_safe_call(coro, "tool_name")` — Proposed Phase 2 (MCP-Correct Signaling)
- Wraps the coroutine and returns `CallToolResult(isError=True)` on failure
- MCP clients see `isError=True` and can handle errors programmatically
- This is the spec-correct approach per the MCP protocol

### Relationship

| Aspect | `@m9_safe` | `_safe_call()` |
|--------|-----------|----------------|
| Purpose | Logging, trace_id capture | Correct MCP protocol error signaling |
| Returns | Plain string (→ `isError=False`) | `CallToolResult(isError=True)` |
| Coverage | ~40 existing tools | 63 tools (Phase 2 target) |
| Status | Live | Proposed for Phase 2 |

**Phase 2 task**: Implement `_safe_call()` for all 63 tools. Evaluate whether `@m9_safe` and `_safe_call()` can be unified — e.g., have `@m9_safe` call `_safe_call()` internally.

## Design Pattern

```python
# From OMEGA_HUB_FINAL_SYNTHESIS.md P0-A
async def _safe_call(coro: Coroutine, tool_name: str) -> CallToolResult:
    try:
        result = await coro
        return CallToolResult(content=[TextContent(type="text", text=str(result))])
    except OmegaError as e:
        logger.error(f"[{tool_name}] OmegaError: {e}", extra={"trace_id": trace_id})
        return CallToolResult(
            isError=True,
            content=[TextContent(type="text", text=str(e))]
        )
    except Exception as e:
        logger.exception(f"[{tool_name}] Unhandled: {e}", extra={"trace_id": trace_id})
        return CallToolResult(
            isError=True,
            content=[TextContent(type="text", text=f"Internal error: {type(e).__name__}: {e}")]
        )
```

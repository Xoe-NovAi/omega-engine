# Target Module Architecture — MCP Hub Modularization

Dependency order (Carmack's plan, per `carmack-reconstruction-plan.md`):

`state.py` → `background.py` → `gateway.py` → `middleware.py` → `tools/` → `server.py`

| Module | Purpose | Extraction Order | Status |
|--------|---------|-----------------|--------|
| `state.py` | Module globals, `_require_service()`, `_init_services()`, `anyio.Event` sync, `_current_entity` ContextVar | 1st (leaf — no deps) | 🔴 PENDING |
| `background.py` | Pruning, reaper, metrics loops | 2nd (depends on state) | 🔴 PENDING |
| `gateway.py` | **SovereignGateway** class + `_proxy_handler` | 3rd (no module-level deps) | 🔴 PENDING |
| `middleware.py` | RateLimit, RequestSizeLimit, `apply_security` | 4th (no deps) | 🔴 PENDING |
| `tools/oracle.py` | 8 Oracle tools (thin wrappers) | 5th (parallelizable) | 🔴 PENDING |
| `tools/hivemind.py` | 12 Hivemind tools | 5th (parallelizable) | 🔴 PENDING |
| `tools/library.py` | 12 Library tools | 5th (parallelizable) | 🔴 PENDING |
| `tools/memory.py` | 3 Memory tools (post-dedup) | 5th (parallelizable) | 🔴 PENDING |
| `tools/research.py` | 5 Research tools | 5th (parallelizable) | 🔴 PENDING |
| `tools/stats.py` | 5 Stats/Observability tools | 5th (parallelizable) | 🔴 PENDING |
| `server.py` | Thin coordinator — FastMCP init, route registration, `__main__` | Last (integration) | 🔴 PENDING |

## Key Design Rules

1. **Thin wrappers**: Tools validate input, await `init_event.wait()`, delegate to `src/omega/` services. Zero business logic.
2. **Block-and-execute**: `anyio.Event` for service readiness. Tools block until services initialize.
3. **M9 compliance**: `_safe_call()` wrapping all tools — returns `CallToolResult(isError=True)`.
4. **`tool_discovery=False`**: Prevent FastMCP from re-discovering tools and creating duplicates.
5. **63 tool signatures must remain identical** — the fleet binds to these names.

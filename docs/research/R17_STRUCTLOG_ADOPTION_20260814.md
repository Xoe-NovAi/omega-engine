# Gap R17: structlog Adoption

**AP Token:** `AP-RESEARCH-PHASE1-4-20260813-v3.2.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ 2026-08-14
**Dependent task:** UO-6.3 (structured logging)
**Status:** ✅ RESOLVED

## Summary
structlog (current 26.1.0) replaces stdlib `logging` with a composable **processor chain** configured once via `structlog.configure(processors=[...])`. It is drop-in compatible, supports `JSONRenderer` for machine-readable logs (M9 compliance) and `ConsoleRenderer` for dev. Context can be bound per-request via `bind()`.

## Authoritative Sources
| Source | URL | Date | Relevance |
|--------|-----|------|-----------|
| structlog docs | https://www.structlog.org/en/stable/ | 2026 | Processor chain, configuration |
| structlog 26.1.0 release | https://github.com/hynek/structlog/releases | 2026 | Current version |

## Findings
- **Configuration**:
  ```python
  import structlog
  structlog.configure(
      processors=[
          structlog.contextvars.merge_contextvars,
          structlog.processors.add_log_level,
          structlog.processors.TimeStamper(fmt="iso"),
          structlog.processors.StackInfoRenderer(),
          structlog.processors.format_exc_info,
          structlog.processors.JSONRenderer(),
      ]
  )
  ```
- **Usage**: `log = structlog.get_logger().bind(entity="kali")`; `log.info("event", key=value)`.
- **Contextvars**: `structlog.contextvars.merge_contextvars` auto-includes bound context (request/session IDs) — ideal for multi-agent tracing.
- **Sync-safe**: structlog is synchronous; if writing to async sinks, wrap in `anyio.to_thread.run_sync` (M1). For file/stdout it is fine as-is.

## Recommendation
Replace stdlib `logging` in `src/omega/oracle/providers.py`, soul modules, and the hub with structlog. Configure once at the engine entrypoint (JSONRenderer for production, ConsoleRenderer behind a dev flag). Use `bind(entity=..., session_id=...)` for per-agent context. This satisfies UO-6.3 and M9 (structured logging) without a heavy dependency.

## Confidence
**HIGH** — structlog is mature (10+ years), widely adopted, and the processor model is stable.

## Remaining Unknowns
- Whether any existing code depends on stdlib `logging` handlers/filters that need a bridge (`structlog` can wrap stdlib via `structlog.stdlib` processors if needed).

# Sovereign Gateway — Technical Specification

**Target module**: `gateway.py`
**Replaces**: Current placeholder stub in `server.py`
**Phase**: Phase 1b (extraction) + Phase 2 (hardening)

## Purpose

Secure egress proxy for Tier 3 (Firecrawl) and Tier 4 (Exa) API calls. Replaces the current inline proxy handler with a managed, observable gateway class.

## Requirements

| Requirement | Implementation | Mandate |
|------------|---------------|---------|
| Managed HTTP client lifecycle | `__aenter__/__aexit__` + `close()` for `httpx.AsyncClient` | M9 (no leaks) |
| Rate limiting | `anyio.CapacityLimiter(10)` for Firecrawl, `anyio.CapacityLimiter(5)` for Exa | M1 (AnyIO) |
| Backoff | Exponential backoff with jitter via `anyio.sleep`. Never `time.sleep()`. | M8 (resilience) |
| Secret injection | Resolve from env vars (`FIRECRAWL_API_KEY`, `EXA_API_KEY`) or ModelGateway config. Never hardcoded. | M6 (security) |
| Error mapping | `SearchErrorResolver` classifier: 401→GatewayAuthError, 402→GatewayQuotaError, 429→GatewayRateLimitError, 5xx→GatewayServerError | M9 (typed errors) |

## Sovereign Primitives

```python
self._firecrawl_limiter = anyio.CapacityLimiter(10)
self._exa_limiter = anyio.CapacityLimiter(5)
```

## Dependencies

- `httpx.AsyncClient` (managed)
- `anyio.CapacityLimiter`
- `anyio.sleep` (for backoff)
- `OmegaError` subtypes for typed error responses

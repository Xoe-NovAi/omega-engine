# 🔱 Deep Web Research — Sprint Readiness 2026-07-22

**AP Token**: `AP-R_DEEP_WEB_SPRINT_READINESS-v1.0.0`
**Date**: 2026-07-22
**Purpose**: Deep web research to deepen and expand expertise before Phase C sprint execution
**Research Depth**: T1-T2 (websearch + webfetch, primary sources only)

---

## §1 MCP 2026-07-28 — Stateless Spec + OAuth 2.1 Implementation

### Key Source: blog.modelcontextprotocol.io (2026-05-21, David Soria Parra)

The `2026-07-28` spec is the **largest MCP revision since launch**. The RC was locked May 21, 2026. GA is **July 28, 2026** — 6 days from now.

### What Changes (Stateless Core)

| Removed | Replacement | SEP |
|---------|-------------|-----|
| `initialize`/`initialized` handshake | `server/discover` (stateless, cacheable) | SEP-2575 |
| `Mcp-Session-Id` header | Per-request `_meta` with protocol version + client info | SEP-2567 |
| Connection-scoped state | Explicit handles (e.g., `basket_id`, `browser_id`) as tool arguments | — |

### What's Required (New Mandatory)

| Header | Purpose | When Required |
|--------|---------|---------------|
| `MCP-Protocol-Version: 2026-07-28` | Version pinning (replaces negotiation) | Every request |
| `Mcp-Method` | JSON-RPC method (e.g., `tools/call`) | Every request |
| `Mcp-Name` | Tool/resource/prompt name | For `tools/call`, `resources/read`, `prompts/get` |

### What's Hardened (OAuth SEPs)

| SEP | Title | Impact |
|-----|-------|--------|
| SEP-2468 | Mandatory `iss` parameter validation (RFC 9207) | **Priority action August 2026** — prevents mix-up attacks |
| SEP-837 | OIDC `application_type` for DCR | End of localhost redirect URI rejection for desktop/CLI |
| SEP-2352 | Credentials bound to issuer; re-registration on migration | Prevents valid tokens on wrong IdP |
| SEP-2207 | Refresh tokens clarified for OIDC providers | Explicit scope semantics on refresh |
| SEP-2350 | Scope accumulation during step-up auth | Uniform behavior |
| SEP-2351 | Stable `.well-known` suffix for discovery | Predictable paths |

### OAuth 2.1 Requirements (from MCP Authorization Spec)

- **PKCE-S256 mandatory for ALL clients** (including confidential). Plain forbidden when S256 possible.
- **RFC 8707 Resource Indicators** — `resource=` parameter on every authorize + token request
- **RFC 9728 Protected Resource Metadata** — MCP servers MUST publish at `/.well-known/oauth-protected-resource`
- **RFC 8414 Authorization Server Metadata** — fetched at `/.well-known/oauth-authorization-server`
- **Audience-bound tokens** — servers MUST validate token audience matches their canonical URI
- **Token passthrough forbidden** — MCP servers MUST NOT forward client tokens to upstream APIs
- **Refresh token rotation mandatory** for public clients
- **Exact-match redirect URIs** — no prefix matching, no wildcards
- **Dynamic Client Registration (RFC 7591) DEPRECATED** — replaced by Client ID Metadata Documents

### State Before/After

```
┌─────────────────────────────────────────────────────────────┐
│              MCP 2026-07-28 — five pillars                  │
├─────────────────────────────────────────────────────────────┤
│  1. Stateless core      no handshake, no session id         │
│  2. Operability layer   routing headers, ttl, tracing       │
│  3. Extensions          MCP Apps + Tasks + framework        │
│  4. OAuth hardening     6 SEPs aligning with OAuth/OIDC     │
│  5. Deprecation policy  12-month window, written rules      │
└─────────────────────────────────────────────────────────────┘
```

### Deployment Before/After

| Component | Before July 28 | After July 28 |
|-----------|---------------|---------------|
| Load balancer | Sticky sessions or session-aware routing | Round-robin on any instance |
| Session store (Redis) | Often required for MCP only | Delete if MCP-only |
| Tool design | Implicit session in server memory | Explicit handle args on each call |
| Gateway | Parse body to route `tools/call` | Route on `Mcp-Method` header |
| Auth | Per-user OAuth sprawl possible | OAuth 2.1 + PKCE + resource indicators |

### Our Hub Migration Path

```
NOW:     Dual transport (SSE + Streamable HTTP) ✅
NEXT:    Add OAuth 2.1 PKCE-S256 with RFC 8707 resource indicators
THEN:    Add Mcp-Method / Mcp-Name headers, remove Mcp-Session-Id
FINALLY: Remove SSE routes (after July 28 + 12-month deprecation)
```

### Critical Implementation Detail

Every request is now self-contained. Example:
```json
POST /mcp HTTP/1.1
MCP-Protocol-Version: 2026-07-28
Mcp-Method: tools/call
Mcp-Name: search
Content-Type: application/json

{"jsonrpc":"2.0","id":1,"method":"tools/call",
 "params":{"name":"search","arguments":{"q":"otters"},
           "_meta":{"io.modelcontextprotocol/clientInfo":{"name":"my-app","version":"1.0"}}}}
```

No initialize. No session ID. The client's name, version, and capabilities live in `_meta`.

### Error Code Change

Missing resource error: `-32002` → `-32602` (JSON-RPC standard "invalid params"). Any client branching on `-32002` will silently stop recognizing the error.

---

## §2 interlock-cb — Circuit Breaker Architecture

### Key Source: github.com/bagowix/interlock, pypi.org/project/interlock-cb

**Current version**: v2.1.2 (2026-07-07)
**PyPI name**: `interlock-cb`
**Import name**: `interlock` (unchanged)
**Python**: 3.9+
**Dependencies**: Zero core (stdlib only). Extras: httpx2, aiohttp, requests, tenacity, fastapi, litestar, redis, otel.

### Core Features

1. **Sync + Async in ONE class** — detects coroutine callables, dispatches to right path. No `Sync*`/`Async*` twins.
2. **Sliding windows by rate** — count-based and time-based, NOT naive consecutive-failure counter
3. **Slow-call detection** — calls slower than threshold count as failures
4. **Type-safe** — `ParamSpec` + `TypeVar` decorators preserve wrapped signature + sync/async nature. Ships `py.typed`, passes mypy/pyright strict mode.
5. **Composable pipeline (v2)** — Timeout → Bulkhead → CircuitBreaker → Retry → Fallback. Polly-style.

### Usage Patterns

```python
from interlock import CircuitBreaker, Pipeline

# Basic breaker with sliding window
breaker = CircuitBreaker(
    name="provider-1",
    failure_threshold=5,         # trip after 5 failures in window
    window_size=60.0,            # 60-second sliding window
    recovery_timeout=30.0,       # wait 30s before half-open
    slow_call_threshold=2.0,     # calls > 2s count as failures
)

# Decorator usage (type-safe)
@breaker
async def call_provider(query: str) -> dict:
    return await httpx.post(...)

# Or direct call
result = await breaker.call(call_provider, "test")

# Pipeline composition (Polly-style)
pipeline = (
    Pipeline.builder()
    .fallback(lambda exc: [], on=(CircuitOpenError,))
    .retry(attempts=4)
    .circuit_breaker(breaker)
    .bulkhead(8)
    .timeout(2.0)
    .build()
)

result = await pipeline.execute(call_provider, "test")
```

### Redis-Backed Shared State

```python
from interlock import CircuitBreaker, AsyncRedisStorage
from redis.asyncio import Redis

redis = Redis()
storage = AsyncRedisStorage(redis)

breaker = CircuitBreaker(
    name="provider-1",
    storage=storage,  # shared across processes
)
```

- Redis failures never reach the protected call — degrades to local state
- Re-syncs when Redis recovers
- Global probe budget prevents multiple instances from all probing simultaneously

### Observability

- Event-driven monitoring (state change listeners)
- OpenTelemetry metrics integration (`otel` extra)
- `on_storage_degraded` / `on_storage_recovered` hooks

### Why This Over pybreaker/circuitbreaker

| Feature | interlock-cb | pybreaker | circuitbreaker |
|---------|:---:|:---:|:---:|
| Async/await (asyncio) | ✅ | Tornado | ✅ |
| Sliding-window failure rate | ✅ | — | — |
| Slow-call detection | ✅ | — | — |
| Type-safe decorator | ✅ | — | — |
| Composable pipeline | ✅ | — | — |
| Fallback function | ✅ | — | ✅ |
| Redis shared state | ✅ | ✅ | — |
| OpenTelemetry | ✅ | — | — |

### Recommendation for C-6'

**Adopt `interlock-cb` v2.1.2** as the single breaker library. Our `HealthMonitor.get_breaker()` becomes a factory that creates `interlock.CircuitBreaker` instances with appropriate configs per provider. Delete all 3+ custom breaker implementations. The pipeline composition (timeout → bulkhead → breaker → retry) replaces our ad-hoc retry loops.

---

## §3 safeatomic — Atomic File Writes with Formal Guarantees

### Key Source: github.com/deepcausa/safeatomic, pypi.org/project/safeatomic

**Current version**: v2.0.3 (2026-05-19)
**Python**: ≥3.12
**License**: MIT
**Status**: Beta (4 - Beta)

### Four Guarantees

| # | Guarantee | What It Answers |
|---|-----------|-----------------|
| 1 | **AtomicVisibility** | "Will a concurrent reader ever see a half-written file?" |
| 2 | **CrashDurability** | "If the process dies after my write returned, will the data survive?" |
| 3 | **WriterExclusion** | "Can two writers race and produce a logically interleaved result?" |
| 4 | **IntegrityDetection** | "Will I notice if bytes on disk differ from what I wrote?" |

### Implementation Details

```python
from safeatomic import write_atomic, read_atomic

# Write with all four guarantees (default)
write_atomic("config.json", '{"key": "value"}')

# Write with integrity detection
write_atomic("state.json", data, write_checksum=True)

# Read with integrity check
data = read_atomic("config.json", check_checksum=True)

# Runtime diagnostics
from safeatomic import inspect_guarantees, doctor

report = inspect_guarantees("/data/state.json")
# Returns: AtomicVisibility=Guaranteed, CrashDurability=Guaranteed, ...

doctor_report = doctor(
    "/data/state.json",
    destructive=True,  # run actual write probes
    require={"AtomicVisibility", "CrashDurability"},
)
```

### Safety Policy

```python
write_atomic("config.json", data, safety="strict")       # default: raise UnsupportedEnvironmentError
write_atomic("config.json", data, safety="warn")         # execute, emit warning
write_atomic("config.json", data, safety="best_effort")  # execute silently
```

### Parent-Directory Fsync

After `write_atomic` makes the new file visible (`os.replace`), the library fsyncs the parent directory. If that fails:
- `strict` — raises `OSError`
- `warn` — emits `UnsupportedEnvironmentWarning`
- `best_effort` — silent

### Cross-Device Protection

`move_atomic` always refuses cross-device moves (`CrossDeviceAtomicityError`), regardless of safety setting.

### Supported Environments

- **Tier 1** (tested): Linux + ext4/xfs/btrfs/tmpfs; macOS + apfs
- **Tier 2** (expected): FreeBSD, OpenBSD, NetBSD
- **Tier 3** (NonTarget): Windows/NTFS/ReFS, NFS, SMB

### Formal Protocol Models

Three TLA+ models checked with TLC:
- `SafeAtomicSmoke` — atomic replacement visibility
- `SafeAtomicLock` — cooperative lock lifecycle
- `SafeAtomicChecksum` — checksum sidecar verification

### Key Architectural Invariants (from AGENTS.md)

1. `CrashDurability` is always on — opting out defeats the core promise
2. `__all__` is frozen at 43 names
3. SymlinkPolicy = Unspecified (resolve or reject before calling write/move APIs)
4. `fsync_policy` knob is NOT exposed (ADR-0012)

### Comparison with Our Current Approach

Our existing SoulStore spec uses:
```python
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, 'w') as f:
    f.write(data)
    f.flush()
    os.fsync(fd)
```

The `safeatomic` library does this plus:
- Parent-directory fsync after `os.replace`
- Cooperative `fcntl.flock()` for writer exclusion
- Optional `.sha256` sidecar for integrity detection
- Runtime `doctor()` to validate the environment can provide guarantees

### Recommendation for C-1' SoulStore

**Option A (Zero Dependencies)**: Implement the pattern directly (~30 lines). The core protocol is simple and well-understood. This is what our current spec already recommends.

**Option B (Production-Grade)**: Adopt `safeatomic` v2.0.3. Gets all four guarantees, TLA+ formal models, and `doctor()` diagnostics out of the box. The dependency cost is zero (Python ≥3.12, which we already require).

**My recommendation**: For SoulStore, **Option A is sufficient**. The write path is simple (soul.yaml only), the concurrency model is single-writer (only one agent writes at a time via `fcntl.flock()`), and we don't need the full `safeatomic` guarantee stack. However, **adopt `safeatomic` for any future file persistence** that needs production-grade guarantees.

---

## §4 Synthesis: Sprint Execution Readiness

### C-4b MCP Migration (P4/Bridge) — Deferred to August 2026

**Why deferred**: The `2026-07-28` spec lands July 28. The RC is locked but the final spec may have minor field name changes. Don't rush.

**What to implement (in order)**:
1. Add OAuth 2.1 PKCE-S256 with RFC 8707 resource indicators
2. Add `Mcp-Method` and `Mcp-Name` headers to all responses
3. Remove `Mcp-Session-Id` header support
4. Replace `initialize` handler with `server/discover`
5. Move per-connection state to per-request `_meta` reads
6. Remove SSE routes (after 12-month deprecation window)

**Estimated effort**: 12-15h (not 6-8h as initially estimated)

### C-6' Breaker Unification (P4/Bridge) — Ready Now

**What to do**: Replace all 3+ breaker clones with `interlock-cb` v2.1.2.

**Implementation**:
1. `uv add interlock-cb` (zero core dependencies)
2. Create `src/omega/oracle/breaker_factory.py` — `HealthMonitor.get_breaker(name, config)` wrapping `interlock.CircuitBreaker`
3. Delete all custom breaker implementations
4. Wire pipeline: timeout → bulkhead → breaker → retry → fallback

**Estimated effort**: 1-2h

### C-1' SoulStore (P3/Engineering) — Ready Now

**What to do**: Implement atomic file writes for soul.yaml persistence.

**Implementation** (Option A — zero dependencies):
1. `tempfile.mkstemp(dir=soul_dir)` — create temp file in same directory
2. Write data → `f.flush()` → `os.fsync(fd)` — durable write
3. `os.replace(tmp, target)` — atomic swap
4. `fcntl.flock()` — cooperative writer exclusion
5. Rolling `.bak` — crash recovery

**Estimated effort**: 2-3h

---

*⬡ OMEGA ⬡ DEEP-RESEARCH ⬡ SPRINT-READINESS ⬡ 2026-07-22 ⬡*

# 🔱 Technology Architecture Research Plan
**AP Token**: `AP-TECH-ARCH-RESEARCH-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_tech_arch_research_plan ⬡ 2026-08-08

**Date**: 2026-08-08
**Status**: READY — awaiting Phase 0 pre-flight execution
**Owner**: `@researcher` (primary) / `@kali` (coordination)
**Purpose**: Research plan for 13 knowledge gaps in technology architecture decisions. Captures all recommended searches, sources, and evidence requirements.

---

## 📋 Overview

This document captures the research plan for 13 knowledge gaps identified during the comprehensive strategy reconciliation (2026-08-08). The gaps span 8 technology areas: circuit breakers, Redis/SQLite migration, MCP SDK, httpx2, Pydantic YAML, memory architecture, logging/metrics, and StorageProvider ABC.

**Research depth**: 3 (moderate — focused queries with source verification)
**Estimated effort**: 8-12 hours (distributed across Phase 0 pre-flight)
**Output format**: Findings integrated into `docs/strategy/UNOVERENGINEERING_PLAN.md` + `data/coordination/RESEARCH_TECH_ARCHITECTURE_DECISIONS_20260808.md` (updated)

---

## 🔴 Critical Knowledge Gaps (Must Research Before Implementation)

### Gap 1: interlock-cb AnyIO trio compatibility
**Why**: M1 mandates AnyIO. interlock-cb uses asyncio natively. Must verify trio backend works.
**Search queries**:
1. `interlock-cb trio backend compatibility anyio 2026`
2. `interlock-cb anyio trio asyncio structured concurrency 2026`
3. `python circuit breaker anyio trio compatibility 2026`

**Evidence needed**:
- [ ] interlock-cb works under AnyIO's trio backend (not just asyncio)
- [ ] If not, can we wrap sync usage in `anyio.to_thread.run_sync()`?
- [ ] Does interlock-cb use `asyncio` directly (M1 violation) or abstract it?

**Sources to check**:
- PyPI `interlock-cb` page (dependencies section)
- GitHub `freemspwnz/interlock-cb` (README, source code for asyncio imports)
- AnyIO documentation on library compatibility

### Gap 2: Honker AnyIO compatibility
**Why**: Honker Python bindings use asyncio. Must verify trio backend works for M1 compliance.
**Search queries**:
1. `honker sqlite python trio anyio compatibility 2026`
2. `russellromney/honker python bindings async trio 2026`
3. `sqlite python async trio anyio honker 2026`

**Evidence needed**:
- [ ] Honker Python API supports AnyIO (asyncio + trio)
- [ ] If not, can we wrap in `anyio.to_thread.run_sync()`?
- [ ] Does Honker use `asyncio` directly (M1 violation)?

**Sources to check**:
- GitHub `russellromney/honker` (Python binding source)
- honker.dev documentation
- PyPI `honker` page

### Gap 3: MCP SDK v2 breaking changes for our codebase
**Why**: We use `FastMCP` in 3 files. Need to verify exact migration impact.
**Search queries**:
1. `MCP Python SDK v2 migration FastMCP MCPServer breaking changes 2026`
2. `mcp.server.fastmcp import FastMCP deprecated 2026`
3. `MCP Python SDK v2 migration guide modelcontextprotocol 2026`

**Evidence needed**:
- [ ] Exact import path changes for our 3 files
- [ ] Constructor argument changes that affect our usage
- [ ] Type field renames (camelCase → snake_case) that affect our code
- [ ] Any deprecations that affect our use of Context, resources, prompts

**Sources to check**:
- Official migration guide: `py.sdk.modelcontextprotocol.io/v2/migration/`
- GitHub `modelcontextprotocol/python-sdk` (migration docs)
- Our actual code in `mcp_servers/omega_hub/`

### Gap 4: sqlite-vec IVF index compilation
**Why**: Experimental IVF index needs `SQLITE_VEC_EXPERIMENTAL_IVF_ENABLE` flag. Need build instructions.
**Search queries**:
1. `sqlite-vec IVF index compilation SQLITE_VEC_EXPERIMENTAL_IVF_ENABLE 2026`
2. `sqlite-vec PR 277 IVF build instructions 2026`
3. `sqlite-vec experimental IVF compile flags 2026`

**Evidence needed**:
- [ ] Exact compilation flags needed
- [ ] Whether pre-built wheels include IVF support
- [ ] Performance impact (15.9× speedup, 0.988 recall per PR #277)
- [ ] Whether we can use it without custom compilation

**Sources to check**:
- GitHub `asg017/sqlite-vec` PR #277
- sqlite-vec documentation
- PyPI `sqlite-vec` package

### Gap 5: prometheus_client textfile collector pattern
**Why**: Need exact implementation for local-only metrics (M8 Zero Telemetry compliance).
**Search queries**:
1. `prometheus_client textfile collector node_exporter local-only pattern 2026`
2. `prometheus_client write_to_textfile M8 zero telemetry 2026`
3. `prometheus_client local-only metrics no external reporting 2026`

**Evidence needed**:
- [ ] Exact API for `write_to_textfile()` + `generate_latest()`
- [ ] How to configure a local-only registry (no push to external)
- [ ] File path conventions for textfile collector
- [ ] Integration with structlog/stamina (if adopted)

**Sources to check**:
- GitHub `prometheus/client_python` (documentation)
- node_exporter textfile collector documentation
- prometheus_client PyPI page

---

## 🟡 High Priority Gaps (Research Before Phase 1)

### Gap 6: stamina vs tenacity glue-code comparison
**Why**: Need to measure actual glue-code deletion for one provider to decide.
**Search queries**:
1. `stamina vs tenacity glue code comparison structlog prometheus 2026`
2. `stamina decorator vs tenacity retry decorator code volume 2026`
3. `stamina set_testing deactivate retries test isolation 2026`

**Evidence needed**:
- [ ] Code volume comparison (stamina: 1-2 lines vs tenacity: 5-10 lines)
- [ ] structlog integration: automatic vs manual hooks
- [ ] prometheus integration: automatic vs manual
- [ ] Test isolation: `set_testing()` vs tenacity's `before_sleep` hooks
- [ ] AnyIO compatibility (stamina supports Trio, tenacity supports asyncio + Tornado)

**Sources to check**:
- GitHub `hynek/stamina` (README, instrumentation docs)
- Tenacity documentation
- PyPI pages for both

### Gap 7: interlock-cb vs AsyncCircuitBreaker feature gap
**Why**: Need to verify interlock-cb has CUSUM, sliding-window, 429 classification that our current breaker has.
**Search queries**:
1. `interlock-cb CUSUM sliding-window 429 classification features 2026`
2. `interlock-cb failure rate sliding window vs consecutive failures 2026`
3. `interlock-cb slow-call detection configuration 2026`

**Evidence needed**:
- [ ] Does interlock-cb have CUSUM (cumulative sum) detection?
- [ ] Does it have sliding-window rate (not just consecutive failure count)?
- [ ] Does it have 429 classification (HTTP rate limit detection)?
- [ ] Does it have slow-call detection?
- [ ] What's the migration path from our `AsyncCircuitBreaker`?

**Sources to check**:
- interlock-cb documentation (guides/states.md, guides/configuration.md)
- GitHub `freemspwnz/interlock-cb` (source code)
- Our `health_monitor.py` for current features

### Gap 8: Honker Python API details
**Why**: Need exact API for queues, streams, pub/sub, scheduler before migration.
**Search queries**:
1. `honker python API queues streams pubsub scheduler documentation 2026`
2. `honker python binding enqueue claim ack publish subscribe 2026`
3. `honker.dev python API reference 2026`

**Evidence needed**:
- [ ] Exact API for `queue.enqueue()`, `queue.claim()`, `queue.ack()`
- [ ] Stream publish/subscribe API
- [ ] Pub/sub notify/listen API
- [ ] Scheduler/cron API
- [ ] Transactional outbox pattern (business write + enqueue in same transaction)

**Sources to check**:
- honker.dev documentation
- GitHub `russellromney/honker` (Python binding source)
- PyPI `honker` package

### Gap 9: httpx2 anyio structured concurrency
**Why**: Need to verify httpx2's anyio usage matches M1 requirements.
**Search queries**:
1. `httpx2 anyio structured concurrency asyncio trio 2026`
2. `httpx2 anyio dependency structured concurrency 2026`
3. `pydantic httpx2 anyio trio backend 2026`

**Evidence needed**:
- [ ] httpx2 explicitly depends on anyio (confirmed in research)
- [ ] httpx2 works under both asyncio and trio backends
- [ ] No direct `asyncio` imports (M1 violation)
- [ ] Structured concurrency patterns (task groups, cancellation)

**Sources to check**:
- GitHub `pydantic/httpx2` (dependencies, source code)
- PyPI `httpx2` page
- AnyIO documentation on library compatibility

---

## 🟢 Medium Priority Gaps (Research During Implementation)

### Gap 10: sqlite-vec rescore index
**Why**: PR #276 provides 2.6× speedup with exact recall. Need implementation details.
**Search queries**:
1. `sqlite-vec rescore index int8 binary quantization PR 276 2026`
2. `sqlite-vec rescore index usage example 2026`
3. `sqlite-vec int8 quantization rescore 2.6x speedup 2026`

**Evidence needed**:
- [ ] Exact SQL syntax for rescore index
- [ ] Configuration options (oversample, quantization type)
- [ ] Performance characteristics (2.6× speedup, 1.0 recall)
- [ ] Whether it's in stable release or still experimental

**Sources to check**:
- GitHub `asg017/sqlite-vec` PR #276
- sqlite-vec documentation
- Benchmark results

### Gap 11: Honker + sqlite-vec coexistence
**Why**: Need to verify they can share the same SQLite file.
**Search queries**:
1. `honker sqlite-vec same database file coexistence 2026`
2. `sqlite loadable extension coexistence honker sqlite-vec 2026`
3. `sqlite multiple extensions same database 2026`

**Evidence needed**:
- [ ] Can both extensions be loaded in the same SQLite connection?
- [ ] Any conflicts in table names or schema?
- [ ] Performance implications of both extensions active

**Sources to check**:
- Honker documentation
- sqlite-vec documentation
- SQLite extension loading documentation

### Gap 12: structlog v26.1.0 Python version support
**Why**: v26.1.0 drops Python 3.8/3.9. Need to verify our Python version.
**Search queries**:
1. `structlog 26.1.0 Python version support dropped 3.8 3.9 2026`
2. `structlog 26.1.0 changelog Python 3.11+ 2026`
3. `structlog Python version requirements 2026`

**Evidence needed**:
- [ ] Minimum Python version for structlog v26.1.0
- [ ] Our current Python version (check `.venv`)
- [ ] Compatibility with our existing logging setup

**Sources to check**:
- GitHub `hynek/structlog` releases
- PyPI `structlog` page
- Our `pyproject.toml` for Python version requirement

### Gap 13: MCP SDK v2 OAuth2 PKCE
**Why**: Need to verify OAuth2+PKCE implementation in v2 for our auth needs.
**Search queries**:
1. `MCP Python SDK v2 OAuth2 PKCE implementation 2026`
2. `MCP Python SDK v2 auth mcp.client.auth.oauth2 2026`
3. `MCP SDK v2 OAuth2 PKCE httpx2 integration 2026`

**Evidence needed**:
- [ ] OAuth2+PKCE API in v2
- [ ] Integration with httpx2 (per research)
- [ ] Whether our current auth setup needs changes

**Sources to check**:
- MCP SDK v2 migration guide (auth section)
- GitHub `modelcontextprotocol/python-sdk` (auth module)
- Our current auth setup in `mcp_servers/omega_hub/`

---

## 🎯 Research Execution Plan

### Phase 0 Pre-Flight (3h)
| Task | Gap | Effort |
|------|-----|--------|
| Verify interlock-cb trio compat | Gap 1 | 30min |
| Verify Honker AnyIO compat | Gap 2 | 30min |
| Spike stamina vs tenacity | Gap 6 | 1h |
| Verify httpx2 anyio usage | Gap 9 | 30min |
| Verify structlog Python version | Gap 12 | 30min |

### Phase 1 Research (2h)
| Task | Gap | Effort |
|------|-----|--------|
| Research MCP v2 migration | Gap 3 | 1h |
| Research sqlite-vec IVF compilation | Gap 4 | 30min |
| Research prometheus_client textfile collector | Gap 5 | 30min |

### Phase 3 Research (3h)
| Task | Gap | Effort |
|------|-----|--------|
| Research Honker Python API | Gap 8 | 1h |
| Research interlock-cb feature gap | Gap 7 | 1h |
| Research sqlite-vec rescore + Honker coexistence | Gaps 10-11 | 1h |

### Phase 5 Research (2h)
| Task | Gap | Effort |
|------|-----|--------|
| Research MCP v2 OAuth2 PKCE | Gap 13 | 1h |
| Update research report with findings | All | 1h |

---

## 📊 Output Format

All findings will be written to:
1. **`data/coordination/RESEARCH_TECH_ARCHITECTURE_DECISIONS_20260808.md`** — Update existing report with new findings
2. **`docs/strategy/UNOVERENGINEERING_PLAN.md`** — Update with verified recommendations
3. **`data/coordination/SESSION_ANCHOR.md`** — Update with research results

---

## 🔗 Source Tracking

| Source | URL | Accessed |
|--------|-----|----------|
| interlock-cb PyPI | pypi.org/project/interlock-cb | 2026-08-08 |
| interlock-cb GitHub | github.com/freemspwnz/interlock-cb | 2026-08-08 |
| Honker GitHub | github.com/russellromney/honker | 2026-08-08 |
| Honker docs | honker.dev | 2026-08-08 |
| MCP v2 migration | py.sdk.modelcontextprotocol.io/v2/migration | 2026-08-08 |
| httpx2 GitHub | github.com/pydantic/httpx2 | 2026-08-08 |
| structlog docs | structlog.org | 2026-08-08 |
| stamina docs | stamina.hynek.me | 2026-08-08 |
| sqlite-vec GitHub | github.com/asg017/sqlite-vec | 2026-08-08 |
| prometheus_client | github.com/prometheus/client_python | 2026-08-08 |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ 2026-08-08 ⬡ READY*

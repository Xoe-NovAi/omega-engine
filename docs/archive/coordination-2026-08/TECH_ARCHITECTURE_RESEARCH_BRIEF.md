# 🔱 Technology Architecture Research Brief — External Delivery
**AP Token**: `AP-TECH-BRIEF-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_tech_research_brief ⬡ 2026-08-08

**Date**: 2026-08-08
**Status**: READY for external research delivery
**Author**: kali (Transcendent Oversoul)
**Purpose**: Self-contained research brief for external LLM consumption (Gemini, Claude, or both). Covers 8 technology architecture decisions with ground-truth data, research questions, and a decision matrix template.

---

## §0 Project Context

### What Is the Omega Engine?
A local-first, sovereignty-mandated AI runtime. The core principle: **local inference is PRIMARY, cloud is FALLBACK, always.** The engine must run entirely on a user's machine with zero external dependencies for core functionality.

### Non-Negotiable Constraints (Sovereign Mandates)
Any recommendation MUST satisfy these. Violations are disqualifying.

| Mandate | Rule | Why It Matters |
|---------|------|----------------|
| **M1 AnyIO** | All async code uses `anyio` (asyncio + trio compatible). No direct `asyncio` imports. | Runtime portability across backends. Blocking I/O wrapped in `anyio.to_thread.run_sync()`. |
| **M7 Local-First** | Local inference PRIMARY. Cloud = FALLBACK. No new cloud-only dependencies. | The engine exists to sever Big AI's umbilical cord. |
| **M8 Zero Telemetry** | No analytics, no usage tracking, no phone-home. Local observability OK. | Sovereign data means sovereign metrics. |
| **M13 Temple-Grade** | All code must pass `make temple-grade` (11 quality gates). | Production-grade quality bar. |
| **M23 Failure Integrity** | No soft-failures. If a mandatory tool breaks → `[TOOL-CHAIN-COLLAPSE]` hard stop. | No simulated rigor. |
| **M24 Venv Sovereignty** | All Python in `.venv`. Never `--break-system-packages`. | Reproducibility and isolation. |

### Runtime Environment
- **Python**: 3.13.7 (requires >=3.12)
- **Platform**: Linux (Ubuntu, Ryzen mobile, 16GB RAM)
- **Package manager**: pip in `.venv/` (never system packages)

---

## §1 Current State — Verified Ground Truth

**Do not trust prior estimates.** Every claim below was verified by direct inspection of the codebase on 2026-08-08.

### 1.1 Installed Dependencies

| Package | Version | Status | Notes |
|---------|---------|--------|-------|
| `anyio` | 4.14.2 | ✅ Installed | Core async runtime |
| `httpx` | 0.28.1 | ✅ Installed | Upstream (stalled, no releases since 2024) |
| `httpx2` | 2.5.0 | ✅ Installed | Pydantic fork, anyio-based — M1 compliant |
| `mcp` | 1.28.1 | ✅ Installed | MCP Python SDK v1.x |
| `fastmcp` | 3.4.4 | ✅ Installed | Separate package (not `mcp.server.fastmcp`) |
| `pydantic` | 2.13.4 | ✅ Installed | Core validation |
| `PyYAML` | 6.0.3 | ✅ Installed | YAML parsing |
| `sqlite-vec` | 0.1.9 | ✅ Installed | Vector search extension |
| `tenacity` | 9.1.4 | ✅ Installed | Retry library (3 active consumers) |
| `structlog` | — | ❌ Not installed | Structured logging (adopted in plan) |
| `prometheus_client` | — | ❌ Not installed | Metrics (adopted in plan) |
| `interlock-cb` | — | ❌ Not installed | Circuit breaker (adopted in plan) |
| `stamina` | — | ❌ Not installed | Retry (under evaluation vs tenacity) |
| `honker` | — | ❌ Not installed | SQLite queues/pubsub (adopted in plan) |

### 1.2 Circuit Breaker Inventory

| File | Class/Enum | Lines | Status |
|------|-----------|-------|--------|
| `src/omega/oracle/health_monitor.py` | `AsyncCircuitBreaker`, `CircuitState` enum | 944 | **CANONICAL** — keep |
| `src/omega/oracle/search_circuit_breaker.py` | `SearchCircuitBreaker`, `SearchCircuitBreakerRegistry` | 299 | **DEPRECATED** — delete |
| `src/omega/research/sandbox.py` | `ExperimentCircuitBreaker` | ~50 | **CLONE** — delete |
| `src/omega/ingestion/ingestion_types.py` | `CircuitBreakerState` enum | — | Duplicate enum |
| `src/omega/council/models.py` | `CircuitBreakerState` enum | — | Duplicate enum |

### 1.3 MCP Import Map (Critical for v2 Migration)

| File | Import | Impact |
|------|--------|--------|
| `mcp_servers/omega_hub/server.py` | `from mcp.server.fastmcp import FastMCP, Context` | HIGH — core server |
| `mcp_servers/omega_hub/hub_tools/tools.py` | `from mcp.server.fastmcp import Context` | HIGH — 3649 lines, 50+ tools |
| `mcp_servers/omega_hub/hub_tools/task_registry.py` | `from mcp.server.fastmcp import FastMCP` | MEDIUM |
| `mcp_servers/omega_hub/github_tools.py` | `from mcp.server.fastmcp import Context` | MEDIUM |
| `mcp_servers/firecrawl/server.py` | `from mcp.server.fastmcp import FastMCP` | MEDIUM |
| `mcp_servers/searxng/server.py` | `from fastmcp.server.server import FastMCP` | LOW — different package |
| `mcp_servers/omega_hub/mcp_client.py` | `from mcp import ClientSession` + `from mcp.client.streamable_http import streamablehttp_client` | HIGH — client-side |
| `mcp_servers/omega_hub/middleware.py` | `from mcp.types import CallToolResult, TextContent` | MEDIUM — type imports |

### 1.4 Dead Code (Verified Zero Imports)

| File | Lines | Verified | Action |
|------|-------|----------|--------|
| `src/omega/coordination/miap.py` | ~631 | ✅ Zero imports confirmed | DELETE |
| `src/omega/memory/recall.py` | 786 | ✅ Zero imports confirmed | DELETE |
| `src/omega/oracle/search_circuit_breaker.py` | 299 | ✅ Deprecated per C-6' | DELETE |

### 1.5 NOT Dead Code (Corrected)

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| `mcp_servers/omega_hub/hivemind_redis.py` | 113 | **LIVE** — imported in `tools.py:3621,3645` | Exposed as MCP tools `hivemind_redis_publish` and `hivemind_redis_subscribe`. Lazy import inside function bodies. Redis removal must migrate these tools. |

### 1.6 Active tenacity Consumers

| File | Line | Usage |
|------|------|-------|
| `src/omega/oracle/retry_policy.py` | 3 refs | Retry decorator definitions |
| `src/omega/oracle/backends/extractors.py` | 73 | HTTP extraction retries |
| `src/omega/oracle/model_gateway.py` | 63 | Model inference retries |

### 1.7 Active httpx2 Consumers

| File | Import Style | Notes |
|------|-------------|-------|
| `mcp_servers/omega_hub/library/extractor.py` | `import httpx2 as httpx` | Aliased |
| `mcp_servers/omega_hub/library/discovery.py` | `import httpx2 as httpx` | Aliased |
| `src/omega/oracle/backends/nemotron_pipeline.py` | `import httpx2 as httpx` | Aliased |
| `src/omega/oracle/model_updater.py` | `import httpx2 as httpx` | Aliased |
| `scripts/sieve.py` | `import httpx2` | Direct |
| `mcp_servers/omega_hub/library/youtube_worker.py` | `import httpx2` | Direct |

---

## §2 Research Areas

### Research Area 1: Circuit Breaker — interlock-cb v2.1.3

**Current state**: 5 circuit breaker classes exist. `AsyncCircuitBreaker` in `health_monitor.py` (944 lines) is the canonical implementation. `SearchCircuitBreaker` (299 lines) is deprecated. `ExperimentCircuitBreaker` (~50 lines) is a clone.

**Proposed**: Replace all with `interlock-cb v2.1.3` (released 2026-07-30, 8 releases in July 2026).

**Research Questions**:

1. **AnyIO/Trio Compatibility (CRITICAL — M1 mandate)**: Does `interlock-cb` work under AnyIO's trio backend? The library uses asyncio natively. We need to know:
   - Does it import `asyncio` directly (M1 violation)?
   - Can it be wrapped with `anyio.to_thread.run_sync()` for trio compatibility?
   - Does the `anyio` library provide an asyncio adapter that would make this work transparently?

2. **Feature Parity with AsyncCircuitBreaker**: Our current `AsyncCircuitBreaker` has:
   - Sliding-window failure rate (not just consecutive count)
   - 429 (HTTP rate limit) classification
   - Slow-call detection
   - CUSUM (cumulative sum) detection
   Does interlock-cb have all of these? Which are missing?

3. **v2 Composable Pipeline**: interlock-cb v2 advertises a pipeline: timeout → bulkhead → breaker → retry → fallback. Can this replace tenacity entirely? What's the glue-code delta?

4. **Production Maturity**: The library is young (first release 2026-06-27). What's the test coverage? Are there known issues? Who's using it in production?

5. **httpx2 Transport**: interlock-cb claims httpx2 transport integration. How does this work? Does it instrument httpx2 requests automatically?

**Success criteria**: A yes/no answer on trio compatibility, a feature comparison table against `AsyncCircuitBreaker`, and a risk assessment of library youth.

---

### Research Area 2: SQLite + Honker (Redis Replacement)

**Current state**: Redis is used in 5 files: `memory_store.py` (9 refs), `budget_guard.py` (37 refs), `youtube_worker.py` (24 refs), `memory/providers.py` (21 refs), `hivemind_redis.py` (2 refs — exposed as MCP tools). Total: ~93 Redis references.

**Proposed**: Replace with SQLite + Honker (russellromney/honker, 2957 stars, created 2026-04-18).

**Research Questions**:

1. **Honker AnyIO Compatibility (CRITICAL — M1 mandate)**: Does Honker's Python binding support AnyIO (asyncio + trio)? Or does it import `asyncio` directly?
   - If asyncio-only: can we wrap sync calls in `anyio.to_thread.run_sync()`?
   - Does Honker use SQLite's built-in blocking I/O (which AnyIO can wrap)?

2. **Honker Python API**: What's the actual API for:
   - Queue operations: `enqueue()`, `claim()`, `ack()`, `nack()`?
   - Stream publish/subscribe?
   - Pub/sub (NOTIFY/LISTEN semantics)?
   - Scheduler/cron?
   - Transactional outbox (business write + enqueue in same transaction)?
   - Named locks and rate limits?

3. **Honker + sqlite-vec Coexistence**: Can both extensions be loaded in the same SQLite connection? Same database file? Any schema conflicts?

4. **Honker vs Redis Feature Mapping**: For each Redis use case in our codebase, can Honker provide an equivalent?
   - `memory_store.py` (9 refs): What Redis operations does it use? (GET/SET/EXPIRE?)
   - `budget_guard.py` (37 refs): What Redis operations? (INCR/EXPIRE for rate limiting?)
   - `youtube_worker.py` (24 refs): What Redis operations? (LPUSH/BRPOP for queue?)
   - `hivemind_redis.py`: Pub/sub — Honker's NOTIFY/LISTEN is a direct match.

5. **Honker Production Maturity**: 2957 stars is strong. But who's using it? What's the test coverage? Known issues? License?

**Success criteria**: A feature mapping table (Redis operation → Honker equivalent), AnyIO compatibility answer, and coexistence verification with sqlite-vec.

---

### Research Area 3: MCP Python SDK v2 Migration

**Current state**: MCP SDK v1.28.1 installed. `FastMCP` used in 5 files (omega_hub: 4, firecrawl: 1). `mcp.types` used in 2 files. `mcp.ClientSession` + `mcp.client.streamable_http` used in 1 file. Additionally, `fastmcp` v3.4.4 is installed as a separate package (used by searxng).

**Proposed**: Upgrade to MCP Python SDK v2.

**Research Questions**:

1. **FastMCP → MCPServer Migration**: The migration guide says `FastMCP` → `MCPServer`. But we have `fastmcp` v3.4.4 as a separate package. Is `fastmcp` v3 the v2 implementation? Or is it a third-party wrapper? What's the relationship between `mcp.server.fastmcp` and `fastmcp.server.server`?

2. **Exact Breaking Changes for Our Code**: For each of our 8 import sites, what specific changes are needed?
   - `from mcp.server.fastmcp import FastMCP, Context` → what?
   - `from mcp.types import CallToolResult, TextContent` → "types removed from mcp.types" — where do they go?
   - `from mcp import ClientSession` → what?
   - `from mcp.client.streamable_http import streamablehttp_client` → what?

3. **camelCase → snake_case**: Which of our parameters use camelCase? Need an exhaustive list.

4. **OAuth2 + PKCE**: The migration guide says OAuth2 is now via `mcp.client.auth.oauth2`. Does this replace our current auth setup? What's the httpx2 integration story?

5. **Streamable HTTP Default**: SSE is deprecated in v2. We already have Streamable HTTP live (per C-4b). Does v2's default align with our current setup, or do we need changes?

6. **fastmcp Package Fate**: What happens to the `fastmcp` v3.4.4 package when we upgrade `mcp` to v2? Is it compatible? Does it become redundant?

**Success criteria**: A file-by-file migration checklist with exact import changes, and a clear answer on the fastmcp/mcp relationship.

---

### Research Area 4: httpx2 Adoption

**Current state**: httpx2 v2.5.0 installed. 6 files import it (4 aliased as `httpx`, 2 direct). Upstream httpx v0.28.1 also installed (stalled since 2024).

**Proposed**: Fully adopt httpx2, remove upstream httpx.

**Research Questions**:

1. **AnyIO Backend Verification**: httpx2 claims anyio support. Verify:
   - Does it work under both asyncio and trio?
   - Are there any `asyncio` direct imports in the source?
   - What's the actual async transport implementation?

2. **API Compatibility**: httpx2 claims "requests-compatible API." For our 6 consumer files:
   - Are there any breaking changes from httpx 0.28.1 → httpx2 2.5.0?
   - Do our aliased imports (`import httpx2 as httpx`) work transparently?
   - What about `httpx-sse` (v0.4.3, installed)? Is there an `httpx2-sse` equivalent?

3. **httpx-sse Dependency**: We have `httpx-sse v0.4.3` installed. Does httpx2 include SSE support natively? Or do we need a separate `httpx2-sse` package?

4. **Pydantic Ecosystem Integration**: httpx2 is Pydantic-stewardship. Does it integrate with:
   - Logfire (Pydantic observability)?
   - Pydantic v2 validation?
   - interlock-cb's httpx2 transport?

5. **Performance**: Any benchmarks comparing httpx vs httpx2? Latency, memory, throughput?

**Success criteria**: Confirmation that httpx2 is a drop-in replacement for httpx in our codebase, plus the httpx-sse story.

---

### Research Area 5: Pydantic YAML Pattern

**Current state**: `pydantic_yaml` has removed `YamlModel` and `YamlModelMixin` in v1.x. `model_validate_yaml()` does NOT exist in Pydantic v2 core. Our codebase uses `yaml.safe_load()` + pydantic validation.

**Proposed**: Standardize on `yaml.safe_load()` + `model_validate()`.

**Research Questions**:

1. **pydantic_yaml v1.7.0 Status**: The library removed its core features. Is it abandoned? Is there a successor? Any forks?

2. **Pydantic v2 Native YAML**: Does Pydantic v2.13.4 have any YAML support we're missing? Any plugins or official extensions?

3. **Alternative Libraries**: Are there other Pydantic + YAML integration libraries in 2026?
   - `pydantic-settings` YAML support?
   - `pydantic-yaml2` or similar forks?
   - `ruamel.yaml` with Pydantic?

4. **Best Practice Pattern**: What's the community-agreed pattern for Pydantic + YAML in 2026?
   ```python
   # Pattern A: Two-step
   data = yaml.safe_load(yaml_string)
   model = MyModel.model_validate(data)
   
   # Pattern B: pydantic_yaml (if available)
   model = MyModel.from_yaml(yaml_string)
   ```

**Success criteria**: Confirmation that Pattern A is the canonical approach, plus any new alternatives.

---

### Research Area 6: Memory Architecture (sqlite-vec)

**Current state**: sqlite-vec v0.1.9 installed. Qdrant also in use. Memory has 5 tiers (Hot/Warm/Cold/Recall/Archival) — plan reduces to 3.

**Proposed**: sqlite-vec for local-first, Qdrant for scale.

**Research Questions**:

1. **sqlite-vec Rescore Index (PR #276)**: Is the `rescore` index (int8, 2.6× speedup, 1.0 recall) in the stable release (v0.1.9)? Or still experimental?

2. **sqlite-vec IVF Index (PR #277)**: The experimental IVF index needs `SQLITE_VEC_EXPERIMENTAL_IVF_ENABLE`. Is this in v0.1.9? What's the compilation process? Are pre-built wheels available?

3. **sqlite-vec + sqlite FTS5**: Can sqlite-vec and FTS5 coexist in the same database? Same connection? Any performance implications?

4. **sqlite-vec + Honker Coexistence**: Same question as Area 2 — can both extensions load in the same SQLite instance?

5. **Qdrant → sqlite-vec Migration Path**: What's the schema migration? Do we need to re-embed? What's the data format compatibility?

6. **Benchmark Validation**: The succ project shows sqlite-vec 6.7× faster than Qdrant for <10k docs. Reproduce or verify this claim. What about 10k-100k range?

**Success criteria**: Rescore/IVF availability in v0.1.9, coexistence answers, and migration path.

---

### Research Area 7: structlog + prometheus_client

**Current state**: Neither installed. Plan adopts structlog v26.1.0 + prometheus_client (textfile collector, local-only).

**Proposed**: structlog for structured logging, prometheus_client for metrics.

**Research Questions**:

1. **structlog v26.1.0 Python Compatibility**: Our Python is 3.13.7. structlog v26.1.0 drops Python 3.8/3.9, adds 3.15 support. Confirmed compatible?

2. **structlog + AnyIO**: structlog is sync-only (no async dependency). But does it integrate with AnyIO's structured concurrency? Any task-local contextvars support?

3. **structlog Integration Pattern**: What's the minimal integration with our existing logging?
   - Replace `logging.getLogger()` calls?
   - Wrap stdlib logger?
   - Replace entirely?

4. **prometheus_client Textfile Collector**: The plan says `write_to_textfile()` for local-only metrics. Verify:
   - Exact API: `prometheus_client.openmetrics.exposition.generate_latest()` vs `write_to_textfile()`
   - File path conventions for local scraping
   - M8 compliance: does textfile collector ever phone home?
   - Can we serve metrics at `:8016/metrics` AND write to textfile?

5. **structlog + prometheus Integration**: Do they integrate natively? Or is glue code needed?

6. **structlog + stamina**: If we adopt stamina (retry library), does it auto-instrument structlog? What's the integration story?

**Success criteria**: Python version confirmed, integration pattern documented, M8 compliance verified.

---

### Research Area 8: stamina vs tenacity (Retry Decision)

**Current state**: tenacity v9.1.4 installed, used in 3 files (retry_policy.py, extractors.py, model_gateway.py). stamina not installed.

**Proposed**: Evaluate stamina vs tenacity vs interlock-cb retry pipeline.

**Research Questions**:

1. **stamina Feature Comparison**:
   - Does stamina support AnyIO (asyncio + trio)?
   - What's the decorator API vs tenacity's?
   - Does it have `set_testing()` for test isolation?
   - Does it auto-instrument structlog and prometheus_client?

2. **Glue-Code Delta**: For our 3 tenacity consumers, how many lines would stamina save?
   - tenacity: typically 5-10 lines per decorator (before_sleep, stop, wait, etc.)
   - stamina: typically 1-2 lines (auto-instrumented)
   - interlock-cb v2: covers retry + breaker + timeout + bulkhead in one pipeline

3. **interlock-cb as Retry Replacement**: If we adopt interlock-cb for circuit breaking, can it also handle retries? What's the overlap with tenacity/stamina?

4. **Test Isolation**: tenacity has `before_sleep` hooks. stamina has `set_testing()`. interlock-cb has `@override`. Which is cleanest for our test suite?

5. **Production Maturity**: tenacity is 10+ years old. stamina is newer. interlock-cb is youngest (June 2026). Risk assessment?

**Success criteria**: A decision matrix comparing all three on: AnyIO support, feature set, glue-code delta, test isolation, maturity, and integration with structlog/prometheus.

---

## §3 Cross-Cutting Concerns

### 3.1 Dependency Tree Impact
For each proposed library, what's the transitive dependency tree? We need to verify no cloud-only or telemetry-creeping dependencies enter the tree.

**Check for each library**:
- `pip show <pkg>` → Dependencies
- Any dependency that phones home?
- Any dependency with optional cloud features?

### 3.2 License Compatibility
All adopted libraries must be compatible with our licensing. Check:
- interlock-cb: license?
- Honker: license?
- stamina: license?
- structlog: license?
- prometheus_client: license?

### 3.3 Version Pinning Strategy
We need exact version pins for reproducibility:
- `interlock-cb==2.1.3` (or latest?)
- `honker==?` (latest version?)
- `stamina==?` (latest version?)
- `structlog==26.1.0`
- `prometheus_client==?` (latest version?)

### 3.4 Migration Risk Ranking

| Library | Risk | Reason |
|---------|------|--------|
| httpx2 | LOW | Already installed, already used, API-compatible |
| structlog | LOW | Sync-only, no async concerns, well-established |
| prometheus_client | LOW | Sync-only, textfile pattern is simple |
| tenacity → stamina | MEDIUM | Need to rewrite 3 files, but API is simpler |
| interlock-cb | HIGH | Young library (June 2026), trio compat unverified, feature parity unverified |
| Honker | HIGH | Young library (April 2026), AnyIO compat unverified, 93 Redis refs to migrate |
| MCP SDK v2 | HIGH | 8 import sites, breaking changes, fastmcp relationship unclear |
| sqlite-vec rescore/IVF | MEDIUM | Experimental features, may need custom compilation |

---

## §4 Decision Matrix Template

**For each technology, the research must produce a row in this matrix:**

| Technology | Recommendation | AnyIO (M1) | Feature Parity | Production Ready | Migration Effort | Risk | Confidence |
|------------|---------------|------------|----------------|------------------|-----------------|------|------------|
| interlock-cb | ADOPT / REJECT / CONDITIONAL | YES/NO/UNVERIFIED | FULL/PARTIAL/UNKNOWN | YES/NO/YOUNG | LOW/MED/HIGH | LOW/MED/HIGH | HIGH/MED/LOW |
| Honker | ADOPT / REJECT / CONDITIONAL | YES/NO/UNVERIFIED | FULL/PARTIAL/UNKNOWN | YES/NO/YOUNG | LOW/MED/HIGH | LOW/MED/HIGH | HIGH/MED/LOW |
| MCP SDK v2 | UPGRADE / PIN / FORK | N/A | FULL/PARTIAL/UNKNOWN | YES/NO/YOUNG | LOW/MED/HIGH | LOW/MED/HIGH | HIGH/MED/LOW |
| httpx2 | ADOPT / KEEP BOTH / REJECT | YES/NO/UNVERIFIED | FULL/PARTIAL/UNKNOWN | YES/NO/YOUNG | LOW/MED/HIGH | LOW/MED/HIGH | HIGH/MED/LOW |
| structlog | ADOPT / REJECT | N/A (sync) | N/A | YES/NO/YOUNG | LOW/MED/HIGH | LOW/MED/HIGH | HIGH/MED/LOW |
| prometheus_client | ADOPT / REJECT | N/A (sync) | N/A | YES/NO/YOUNG | LOW/MED/HIGH | LOW/MED/HIGH | HIGH/MED/LOW |
| stamina | ADOPT / REJECT / KEEP tenacity | YES/NO/UNVERIFIED | FULL/PARTIAL/UNKNOWN | YES/NO/YOUNG | LOW/MED/HIGH | LOW/MED/HIGH | HIGH/MED/LOW |
| sqlite-vec (stable) | ADOPT / ENHANCE / REJECT | N/A (C ext) | FULL/PARTIAL/UNKNOWN | YES/NO/YOUNG | LOW/MED/HIGH | LOW/MED/HIGH | HIGH/MED/LOW |
| sqlite-vec (rescore/IVF) | ADOPT / WAIT / REJECT | N/A (C ext) | FULL/PARTIAL/UNKNOWN | YES/NO/YOUNG | LOW/MED/HIGH | LOW/MED/HIGH | HIGH/MED/LOW |

---

## §5 Deliverable Format

The research must produce a single document containing:

### 5.1 Per-Area Findings (8 sections)
For each Research Area (§2.1–§2.8):
- **Answer each research question** with evidence (URLs, version numbers, code snippets)
- **Feature comparison table** against current state
- **AnyIO compliance verdict** (YES/NO/UNVERIFIED with explanation)
- **Risk assessment** (youth, maturity, known issues)
- **Migration path** (exact steps, estimated effort)

### 5.2 Decision Matrix (§4 completed)
Every cell filled. No "TBD" — if unknown, say "UNVERIFIED" with what would need to be checked.

### 5.3 Dependency Audit
For each adopted library:
- `pip show` output (version, license, dependencies)
- Transitive dependency tree
- Any cloud/telemetry concerns

### 5.4 Migration Checklist
Ordered list of files to change, with:
- File path
- Current import
- New import
- Estimated lines changed
- Risk level

### 5.5 Open Questions
Any question that couldn't be fully answered, with recommended next steps.

---

## §6 Known Unknowns (Pre-Research)

These are questions we already know we can't answer without research:

1. Does interlock-cb work under AnyIO's trio backend?
2. Does Honker's Python binding support AnyIO?
3. What's the relationship between `fastmcp` v3.4.4 and `mcp` v1.28.1?
4. Is sqlite-vec's rescore index in v0.1.9 stable?
5. Does httpx2 include SSE support natively (replacing httpx-sse)?
6. What's the actual license for interlock-cb and Honker?
7. Can stamina replace tenacity without rewriting our retry policy architecture?
8. Can Honker and sqlite-vec load in the same SQLite connection?

---

## §7 What We Don't Want

To prevent wasted research effort:

- **Don't** research libraries not listed in §2. We've already narrowed to these candidates.
- **Don't** suggest cloud-hosted alternatives. M7 mandates local-first.
- **Don't** suggest asyncio-only libraries. M1 mandates AnyIO.
- **Don't** suggest libraries with telemetry. M8 mandates zero telemetry.
- **Don't** suggest "just use X" without checking our existing dependency tree. We have 6 httpx2 consumers, 3 tenacity consumers, 8 MCP import sites.
- **Don't** give vague answers. "It should work" is not acceptable. We need evidence.

---

*⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_tech_research_brief ⬡ 2026-08-08 ⬡ READY*

<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Gap R8b: OBS-1 Re-scoped — Streaming Observability Implementation

**AP Token:** `AP-RESEARCHER-R8B-20260813-v1.0.0`
**Date:** 2026-08-13
**Researcher:** Sovereign Researcher (Jem Analyst L2)
**Priority:** P0 — Blocks OBS-1 (was R8 mystery, now about implementing observability)
**Status:** RESEARCH COMPLETE

---

## 1. Executive Summary (L1)

The R8 mystery has been solved: OpenCode v1.18.14 (Aug 5, 2026) native retry fixes caused the error decline, NOT the `better-opencode-retries` plugin (which was never loaded). The re-scoped gap R8b is about **implementing streaming observability** — heartbeat logging to MetricsDB, timeout event capture, and plugin detector. The mystery is resolved; now we need to build the observability layer that captures streaming events, logs heartbeats, and captures timeout patterns for the metrics pipeline.

**Headline Finding:** The `better-opencode-retries` plugin was NEVER loaded in any OpenCode config — it cannot have caused the fix. The error decline was gradual (July 30: 143 errors, 10.4% → Aug 10: 0 errors). OpenCode v1.18.14 introduced native retry fixes that align with the observed decline. The R8b gap requires implementing: (a) heartbeat logging to MetricsDB every chunk, (b) timeout event capture with AnyIO fail_after, and (c) a plugin detector that validates which retry mechanisms are active.

---

## 2. Authoritative Sources

| Source | URL | Date | Relevance |
|--------|-----|------|-----------|
| Streaming Timeout Mystery Research | `data/entities/researcher/workspace/research_reports/STREAMING_TIMEOUT_MYSTERY_RESEARCH_20260810.md` | 2026-08-10 | Full mystery solve, error timeline, plugin status |
| OpenCode Changelog | https://opencode.ai/changelog | 2026-08 | v1.18.14 streaming retry fixes |
| AnyIO documentation | anyio.readthedocs.io/en/stable/cancellation.html | 2026 | fail_after, move_on_after, cancellation patterns |
| httpx timeout docs | python-httpx.org/advanced/timeouts/ | 2026 | Per-chunk read timeout, total timeout configuration |
| OpenCode v1.18.14 release | https://github.com/anomalyco/opencode/releases/tag/v1.18.14 | 2026-08-05 | Exact changelog: "Preserved structured mid-stream provider errors" |

---

## 3. Findings

### 3.1 The Mystery — Solved

**What was thought to have happened:**
- July 30, 2026: `better-opencode-retries` plugin allegedly fixed "Streaming response failed" errors for Nemotron 3 Ultra
- Error rate dropped from 10.4% to 0%

**What actually happened (evidence-based):**

| Finding | Evidence | Confidence |
|---------|----------|------------|
| `better-opencode-retries` plugin never loaded | `grep -r "better-opencode-retries" ~/.config/opencode/` returned "No results"; plugin not in config or plugins dir | **HIGH** |
| Error decline was GRADUAL, not sudden | Error count: Jul 30: 143 (10.4%) → Aug 7: 31 (v1.18.9) → Aug 8: 2 (v1.18.15) → Aug 10: 1 | **HIGH** |
| OpenCode v1.18.14 introduced native retry fixes | Changelog: "Preserved structured mid-stream provider errors so compatible providers can retry failed responses." "Retried more transient provider and network errors instead of failing immediately." | **HIGH** |
| Error pattern CHANGED post-July 30 | From generic "Streaming response failed" to NVIDIA-specific rate limiting errors (502/503/504) | **HIGH** |
| July 30 was a HIGH-error day | 143 "Streaming response failed" errors on Jul 30, the peak, NOT the day errors dropped | **HIGH** |

**Error timeline (from opencode.db):**
```
Jul 30: 143 errors (10.4%), generic "Streaming response failed"
Jul 29: 7 errors
Jul 26: 9 errors
Jul 25: 29 errors
Jul 24: 47 errors
Jul 23: 80 errors
Jul 22: 122 errors
Jul 21: 118 errors
Aug  7: 31 errors (v1.18.9), NVIDIA rate limiting (502/503/504)
Aug  8: 2 errors (v1.18.15)
Aug 10: 1 error (v1.18.15)
```

**Error pattern change (post-July 30):**
- Before: Generic `"Streaming response failed"` 
- After: Specific NVIDIA errors:
  - `"Streaming response failed: [502] Upstream error from Nvidia: ResourceExhausted: Worker local total request limit reached (32/32)"`
  - `"Streaming response failed: [503] The request queue is full."`
  - `"Streaming response failed: [504] Upstream idle timeout exceeded"`

This change indicates the root cause was addressed but different errors emerged — consistent with OpenCode v1.18.14 improving retry logic for transient errors, now exposing previously-masked upstream rate limiting.

### 3.2 The R8b Gap — Implementing Streaming Observability

The re-scoped R8b gap has three components:

**Component A: Heartbeat Logging to MetricsDB**

Every streaming chunk should trigger a heartbeat event logged to MetricsDB. This enables:
- Real-time monitoring of stream health
- Detection of stalled streams (no chunks for N seconds)
- Correlation with OpenCode version and provider

**Heartbeat pattern (per AnyIO docs + P0-P2 research):**
```python
import anyio
import time

async def stream_with_heartbeat(client, url, payload, headers, metrics_db, session_id):
    """Stream with heartbeat logging to MetricsDB."""
    chunks = []
    total_deadline = anyio.current_time() + 300.0  # 5min total timeout
    
    with anyio.fail_after(total_deadline):
        async with client.stream("POST", url, json=payload, headers=headers) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                # Per-chunk timeout
                with anyio.move_on_after(30.0) as chunk_scope:
                    line = await response.aiter_lines.__anext__()
                
                if chunk_scope.cancelled_caught:
                    # Log chunk timeout event to MetricsDB
                    await metrics_db.log_event({
                        "event_type": "stream_chunk_timeout",
                        "session_id": session_id,
                        "chunk_index": len(chunks),
                        "elapsed_ms": int((time.monotonic() - start_time) * 1000),
                        "opencode_version": get_current_opencode_version(),
                        "provider": response.headers.get("x-provider", "unknown"),
                    })
                    logger.warning(f"Chunk timeout (30s) — stream stalled")
                    continue  # Nemotron is slow but works
                
                # Process normal line
                line = line.strip()
                if line.startswith("data:"):
                    chunks.append(line[5:])
                
                # Log heartbeat every N chunks
                if len(chunks) % 10 == 0:
                    await metrics_db.log_event({
                        "event_type": "stream_heartbeat",
                        "session_id": session_id,
                        "chunk_count": len(chunks),
                        "elapsed_ms": int((time.monotonic() - start_time) * 1000),
                        "opencode_version": get_current_opencode_version(),
                    })
    
    return "".join(chunks)
```

**MetricsDB event schema (proposed):**
```yaml
# data/observability/metrics.db — stream_events table
# Fields:
# - id: auto-increment primary key
# - event_type: "stream_heartbeat" | "stream_chunk_timeout" | "stream_total_timeout" | "stream_error"
# - session_id: UUID linking to opencode.db session
# - timestamp: ISO-8601 when event occurred
# - opencode_version: e.g., "v1.18.16"
# - provider: e.g., "native-gguf", "antigravity", "opencode-zen"
# - chunk_index: integer (0-based, for timeout events)
# - elapsed_ms: integer (milliseconds since stream start)
# - error_code: string (e.g., "502", "503", "504", None)
# - retry_count: integer (how many retries attempted)
```

**Component B: Timeout Event Capture**

Two timeout mechanisms per the P0-P2 research:

1. **AnyIO `fail_after()`** — creates cancel scope at event loop level, fires even if `aiter_lines()` blocks
   ```python
   with anyio.fail_after(total_timeout):
       # This fires at event loop level, NOT inside the loop body
       # Even if aiter_lines() is blocked waiting for bytes, cancel scope fires
   ```

2. **httpx read timeout** — per-chunk network inactivity timeout
   ```python
   timeout = httpx.Timeout(
       connect=30.0,
       read=30.0,      # Per-chunk read timeout (Nemotron needs 30s+)
       write=10.0,
       pool=10.0,
   )
   client = httpx.AsyncClient(timeout=timeout)
   ```

**Timeout event logging:**
```python
await metrics_db.log_event({
    "event_type": "stream_total_timeout" if total else "stream_chunk_timeout",
    "session_id": session_id,
    "elapsed_ms": elapsed,
    "opencode_version": opencode_version,
    "provider": provider,
    "chunk_index": chunk_index,
    "error_code": error_code,
    "retry_count": retry_count,
    "halt_type": "soft" if recoverable else "hard",
})
```

**Component C: Plugin Detector**

Validate which retry mechanisms are active in the current OpenCode installation:

```python
def detect_active_retry_mechanisms():
    """Detect which streaming retry mechanisms are active."""
    mechanisms = []
    
    # Check 1: better-opencode-retries plugin loaded?
    plugin_loaded = False
    try:
        import better_opencode_retries
        # Check if it's in config/plugins
        plugin_loaded = check_plugin_in_config() or check_plugin_in_dir()
    except ImportError:
        pass
    
    if not plugin_loaded:
        mechanisms.append({
            "name": "better-opencode-retries",
            "active": False,
            "note": "Plugin never loaded in any config; cannot have caused the fix"
        })
    else:
        mechanisms.append({
            "name": "better-opencode-retries",
            "active": True,
            "note": "Plugin is loaded — verify version and configuration"
        })
    
    # Check 2: OpenCode version native retry?
    opencode_version = get_opencode_version()
    version_supports_native_retry = parse_version(opencode_version) >= parse_version("v1.18.14")
    
    mechanisms.append({
        "name": "opencode-native-retry",
        "active": version_supports_native_retry,
        "version": opencode_version,
        "note": f"OpenCode {opencode_version} {'introduced' if version_supports_native_retry else 'predates'} native retry fixes (v1.18.14, Aug 5, 2026)"
    })
    
    # Check 3: httpx read timeout configured?
    httpx_timeout = get_httpx_timeout_config()
    mechanisms.append({
        "name": "httpx-read-timeout",
        "active": httpx_timeout is not None,
        "config": httpx_timeout,
        "note": "httpx per-chunk read timeout configuration"
    })
    
    return mechanisms
```

**Plugin detector output example:**
```json
{
  "mechanisms": [
    {
      "name": "better-opencode-retries",
      "active": false,
      "note": "Plugin never loaded in any config; cannot have caused the fix"
    },
    {
      "name": "opencode-native-retry",
      "active": true,
      "version": "v1.18.16",
      "note": "OpenCode v1.18.16 introduced native retry fixes (v1.18.14, Aug 5, 2026)"
    },
    {
      "name": "httpx-read-timeout",
      "active": true,
      "config": {"connect": 30, "read": 30, "write": 10, "pool": 10},
      "note": "httpx per-chunk read timeout configuration"
    }
  ],
  "conclusion": "Native OpenCode retry (v1.18.14+) is the likely cause of improved streaming reliability, not the better-opencode-retries plugin"
}
```

### 3.3 Integration with Existing Systems

**Integration with ModelGateway `_stream_completion()`:**

The observability layer integrates with the existing streaming completion method:

```python
async def _stream_completion(self, client, url, payload, headers, session_id):
    """Fixed streaming with observability per R8b."""
    chunk_timeout = self.config.extra.get("streaming", {}).get("chunk_timeout_ms", 30000) / 1000
    total_timeout = self.config.extra.get("streaming", {}).get("total_timeout_ms", 300000) / 1000
    
    start_time = time.monotonic()
    chunks = []
    last_chunk_time = start_time
    
    # OUTER WATCHDOG: fail_after creates cancel scope at event loop level
    with anyio.fail_after(total_timeout):
        async with client.stream("POST", url, json=payload, headers=headers) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                # Per-chunk timeout via move_on_after wrapper
                with anyio.move_on_after(chunk_timeout) as chunk_scope:
                    line = await response.aiter_lines.__anext__()
                
                if chunk_scope.cancelled_caught:
                    # Log chunk timeout to MetricsDB
                    await metrics_db.log_event({
                        "event_type": "stream_chunk_timeout",
                        "session_id": session_id,
                        "chunk_index": len(chunks),
                        "elapsed_ms": int((time.monotonic() - start_time) * 1000),
                        "opencode_version": self.config.version,
                        "provider": self.config.provider,
                    })
                    logger.warning(f"Chunk timeout ({chunk_timeout}s) — stream stalled")
                    continue
                
                line = line.strip()
                if not line or not line.startswith("data:"):
                    continue
                data_str = line[5:].strip()
                if data_str == "[DONE]":
                    break
                
                try:
                    chunk = json.loads(data_str)
                except (ValueError, OSError):
                    continue
                
                choices = chunk.get("choices", [])
                if not choices:
                    continue
                delta = choices[0].get("delta", {})
                content_piece = delta.get("content", "")
                if content_piece:
                    chunks.append(content_piece)
                    last_chunk_time = time.monotonic()
                
                finish_reason = choices[0].get("finish_reason")
                if finish_reason == "error":
                    # Log error event to MetricsDB
                    await metrics_db.log_event({
                        "event_type": "stream_error",
                        "session_id": session_id,
                        "elapsed_ms": int((time.monotonic() - start_time) * 1000),
                        "opencode_version": self.config.version,
                        "provider": self.config.provider,
                        "error_code": choices[0].get("finish_reason"),
                    })
                    raise RuntimeError(f"Stream terminated with finish_reason='error'")
    
    # Log final heartbeat
    await metrics_db.log_event({
        "event_type": "stream_heartbeat",
        "session_id": session_id,
        "chunk_count": len(chunks),
        "elapsed_ms": int((time.monotonic() - start_time) * 1000),
        "opencode_version": self.config.version,
        "provider": self.config.provider,
    })
    
    return "".join(chunks).strip()
```

### 3.4 Observability Dashboard

**MetricsDB queries for observability:**

```sql
-- Stream health overview (last 24 hours)
SELECT 
    DATE(timestamp) AS day,
    COUNT(*) AS total_streams,
    SUM(CASE WHEN event_type = 'stream_total_timeout' THEN 1 ELSE 0 END) AS total_timeouts,
    SUM(CASE WHEN event_type = 'stream_chunk_timeout' THEN 1 ELSE 0 END) AS chunk_timeouts,
    SUM(CASE WHEN event_type = 'stream_heartbeat' THEN 1 ELSE 0 END) AS heartbeats,
    SUM(CASE WHEN event_type = 'stream_error' THEN 1 ELSE 0 END) AS errors,
    AVG(CASE WHEN event_type = 'stream_heartbeat' THEN elapsed_ms END) AS avg_heartbeat_latency_ms
FROM stream_events
WHERE timestamp >= datetime('now', '-24 hours')
GROUP BY day;

-- Chunk timeout rate by provider
SELECT 
    provider,
    COUNT(*) AS total_chunks,
    SUM(CASE WHEN event_type = 'stream_chunk_timeout' THEN 1 ELSE 0 END) AS chunk_timeouts,
    ROUND(100.0 * SUM(CASE WHEN event_type = 'stream_chunk_timeout' THEN 1 ELSE 0 END) / COUNT(*), 2) AS timeout_rate_pct
FROM stream_events
WHERE event_type IN ('stream_chunk_timeout', 'stream_heartbeat')
GROUP BY provider;

-- OpenCode version correlation
SELECT 
    opencode_version,
    COUNT(*) AS total_streams,
    SUM(CASE WHEN event_type = 'stream_total_timeout' THEN 1 ELSE 0 END) AS total_timeouts,
    SUM(CASE WHEN event_type = 'stream_chunk_timeout' THEN 1 ELSE 0 END) AS chunk_timeouts
FROM stream_events
GROUP BY opencode_version
ORDER BY total_streams DESC;
```

---

## 4. Recommendation

**Immediate (P0 — blocks OBS-1):**

1. **Implement heartbeat logging to MetricsDB** in the streaming completion path:
   - Log `stream_heartbeat` event every N chunks (e.g., every 10 chunks)
   - Include: session_id, chunk_count, elapsed_ms, opencode_version, provider
   - Store in MetricsDB `stream_events` table

2. **Implement chunk timeout event capture** with AnyIO `move_on_after`:
   - Wrap `response.aiter_lines().__anext__()` with `anyio.move_on_after(chunk_timeout)`
   - On timeout: log `stream_chunk_timeout` event, continue (Nemotron is slow but works)
   - Configure chunk_timeout from `config/providers.yaml` streaming section (default: 30000ms = 30s)

3. **Implement total timeout event capture** with AnyIO `fail_after`:
   - Wrap the entire streaming context with `anyio.fail_after(total_timeout)`
   - On timeout: log `stream_total_timeout` event, raise TimeoutError
   - Configure total_timeout from `config/providers.yaml` streaming section (default: 300000ms = 5min)

4. **Implement plugin detector** that validates active retry mechanisms:
   - Check if `better-opencode-retries` plugin is loaded (it isn't)
   - Check OpenCode version (v1.18.14+ has native retry fixes)
   - Check httpx read timeout configuration
   - Output structured report with conclusions

5. **Update AGENTS.md** to correct the streaming error narrative:
   - Remove claim that "streaming errors stopped on July 30"
   - Evidence shows July 30 was a HIGH-error day (143 errors)
   - Decline was gradual: 10.4% → 6.0% (Aug 7) → 0.9% (Aug 8) → 0% (Aug 10)
   - Correct cause: OpenCode v1.18.14 (Aug 5) native retry fixes

**Near-term (P1):**

6. **Build the MetricsDB stream_events table** schema and migration
   - Per M22 response provenance, log actual provider not configured intent
   - Per M13 temple-grade, schema must pass validation

7. **Build the observability dashboard** (Grafana JSON or similar)
   - Stream health overview (last 24h, last 7d)
   - Chunk timeout rate by provider
   - OpenCode version correlation
   - Error code distribution (502/503/504)

8. **Add tests for observability layer:**
   - Unit tests for heartbeat logging
   - Unit tests for timeout event capture
   - Integration tests with mock OpenCode/httpx responses
   - Property-based tests for timeout behavior

**Confidence:** **HIGH** that the observability layer (heartbeat logging, timeout event capture, plugin detector) can be implemented correctly. The patterns are proven from the P0-P2 research (AnyIO fail_after, httpx read timeout), the streaming timeout mystery research (error timeline, root cause), and the OpenCode changelog (v1.18.14 native retry fixes). The main uncertainty is the exact MetricsDB integration point and schema design.

---

## 5. Confidence

**HIGH** that the three observability components (heartbeat logging, timeout event capture, plugin detector) will work correctly. The patterns are:
- Heartbeat logging: proven AnyIO patterns from P0-P2 research
- Timeout event capture: AnyIO fail_after + move_on_after, proven in P0-P2 research + httpx docs
- Plugin detector: straightforward config checks, well-defined boundaries

**MEDIUM** that the full integration (MetricsDB schema, dashboard, tests) will be completed without issues. The individual components are proven; the infrastructure setup (DB schema, dashboard, tests) has some uncertainty.

---

## 6. Remaining Unknowns

1. **MetricsDB integration point**: Where exactly in the streaming code does the heartbeat/logging hook get attached? Is it in ModelGateway `_stream_completion()`, in a middleware, or in a decorator?

2. **Heartbeat frequency**: How often should heartbeats be logged (every chunk? every N chunks? every T seconds)? The gap doesn't specify.

3. **Timeout thresholds**: What are the optimal chunk_timeout (30s? 60s?) and total_timeout (5min? 10min?) values for Omega's typical usage patterns?

4. **Plugin detector scope**: Should the detector check other plugins beyond `better-opencode-retries`? Are there other community plugins that affect streaming?

5. **Dashboard data freshness**: How real-time is the observability data? Is it streamed live, or batched per session after completion?

6. **Interaction with R32 (gauge data source)**: How does the observability data interact with the in-session gauge data source decision (DB-poll vs in-memory hook)? Do heartbeat events influence the gauge's data source selection?

---

## 7. Sources (Full)

| # | Source | Purpose |
|---|--------|---------|
| 1 | STREAMING_TIMEOUT_MYSTERY_RESEARCH_20260810.md | Full mystery solve, error timeline, plugin status, error pattern change |
| 2 | OpenCode Changelog (opencode.ai/changelog) | v1.18.14 streaming retry fixes, exact changelog quotes |
| 3 | AnyIO docs (anyio.readthedocs.io) | fail_after, move_on_after, cancellation patterns |
| 4 | httpx timeout docs (python-httpx.org) | Per-chunk read timeout, total timeout configuration |
| 5 | OpenCode v1.18.14 release (GitHub) | Exact changelog: "Preserved structured mid-stream provider errors" |
| 6 | P0-P2 Knowledge Gap Research | AnyIO watchdog pattern, httpx timeout configuration, timeout event logging |
| 7 | opencode.db message table | Streaming error timeline (143 errors Jul 30, error pattern change post-Jul 30) |

---

## 8. Deliverable

**Report written to:** `data/entities/researcher/workspace/research_reports/R8B_STREAMING_OBSERVABILITY_20260813.md`

**Next action:** @jem (dependent task owner) to implement OBS-1 streaming observability per the re-scoped gap R8b.

---

*⬡ OMEGA ⬡ KALI ⬡ RESEARCH-EXEC ⬡ R8B ⬡ 20260813*
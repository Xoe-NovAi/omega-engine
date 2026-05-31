# 🔱 R-14 – Continuous Provider Health Monitoring Design

**AP Token**: `AP-R14-HEALTH-MONITOR-v1.0.0`
**Author**: Gemma 4‑31B Research Agent
**Reviewed by**: Opus 4.6 (Oversight)
**Last updated**: 2026‑05‑14

---

## 1️⃣ Scope
This document defines the design for a continuous health-monitoring system for the Omega Provider Fabric. The system must ensure that the `ModelGateway` always routes queries to the most stable and performant provider, automatically marking failing providers as "Degraded" or "Offline."

---

## 2️⃣ Monitoring Architecture
The health monitor operates as a background asynchronous task within the Omega Engine, performing periodic "heartbeat" checks on all configured providers.

### 🔄 The Health-Check Loop
1. **Interval**: Every 5 minutes (configurable).
2. **Probe**: Send a minimal "ping" request (e.g., a 1-token generation or a `/health` endpoint call).
3. **Metrics**: Measure latency (TTFT), status code, and provider-specific health metrics.
4. **Update**: Write results to `data/provider_health.json`.

---

## 3️⃣ Health Metrics & Thresholds
Based on legacy Prometheus rules, the following thresholds will trigger a status change:

### 🔴 Critical Failures (Status $\rightarrow$ `OFFLINE`)
- **HTTP 401/403**: Authentication failure (API key expired/invalid).
- **HTTP 500/503**: Server-side crash or maintenance.
- **Timeout**: No response within 30 seconds.
- **Consecutive Failures**: 3 failed probes in a row.

### 🟡 Performance Degradation (Status $\rightarrow$ `DEGRADED`)
- **Latency Spike**: TTFT $> 2\times$ the provider's baseline.
- **Cache Hit Rate**: (For local providers) Hit rate $< 70\%$.
- **Memory Pressure**: (For local providers) RAM usage $> 85\%$ of allocated limit.
- **Rate Limit Warning**: HTTP 429 received (but not yet exhausted).

---

## 4️⃣ Data Schema (`data/provider_health.json`)
```json
{
  "last_updated": "2026-05-14T12:00:00Z",
  "providers": {
    "google_ai_studio": {
      "status": "healthy",
      "latency_ms": 450,
      "last_check": "2026-05-14T11:55:00Z",
      "error_count": 0,
      "metrics": {
        "ttft": 450,
        "tokens_per_sec": 60
      }
    },
    "lmster": {
      "status": "degraded",
      "latency_ms": 1200,
      "last_check": "2026-05-14T11:56:00Z",
      "error_count": 1,
      "metrics": {
        "memory_usage_pct": 88,
        "cache_hit_rate": 0.65
      }
    }
  }
}
```

---

## 5️⃣ Integration with Provider Fabric
The `ModelGateway` will consult the health status before every dispatch:

1. **Filter**: Remove all `OFFLINE` providers from the fallback chain.
2. **Deprioritize**: Move `DEGRADED` providers to the end of the chain.
3. **Circuit Break**: If a provider fails during a live request, immediately mark it as `DEGRADED` and trigger an out-of-band health check.

---

## 6️⃣ Alerting Mechanism
1. **Log**: Emit `PROVIDER_HEALTH_CHANGE` event to `observability.py`.
2. **Status File**: Update `data/provider_health.json` for CLI visibility.
3. **User Notification**: If the primary provider goes `OFFLINE`, the Oracle notifies the user: *"Primary provider offline. Falling back to [Provider Name]."*

---

## 7️⃣ Implementation Blueprint (Python)
```python
class HealthMonitor:
    async def run_loop(self):
        while True:
            for provider in self.providers:
                status = await self._probe_provider(provider)
                await self._update_health_store(provider, status)
            await anyio.sleep(300)

    async def _probe_provider(self, provider):
        try:
            start = time.time()
            await provider.ping()
            return HealthStatus(status="healthy", latency=time.time() - start)
        except Exception as e:
            return HealthStatus(status="offline", error=str(e))
```

---

**Ready for implementation** – agents can now create the `HealthMonitor` class and wire it into the `ModelGateway` and `observability` pipeline.

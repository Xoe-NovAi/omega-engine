# Gap R18: prometheus_client Textfile Collector

**AP Token:** `AP-RESEARCH-PHASE1-4-20260813-v3.2.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ 2026-08-14
**Dependent task:** UO-6.4 (local-only metrics, M8 compliance)
**Status:** ✅ RESOLVED

## Summary
`prometheus_client` exposes a **textfile collector** that writes metrics to a `.prom` file atomically via `write_to_textfile()` from a `CollectorRegistry`. A node exporter scrapes the file — no long-running HTTP server or daemon required. This is the correct local-first pattern for the engine's metrics (M7/M8).

## Authoritative Sources
| Source | URL | Date | Relevance |
|--------|-----|------|-----------|
| prometheus_client textfile docs | https://prometheus.github.io/client_python/instrumenting/#textfile-collector | 2026-04-17 (updated) | Authoritative API |
| Prometheus textfile collector spec | https://prometheus.io/docs/instrumenting/exposition_formats/ | 2026 | `.prom` format |

## Findings
- **API**:
  ```python
  from prometheus_client import CollectorRegistry, Gauge, write_to_textfile
  reg = CollectorRegistry()
  g = Gauge("omega_inference_total", "Total inferences", registry=reg)
  g.set(1)
  write_to_textfile("/var/lib/node_exporter/metrics.prom", reg)
  ```
- `write_to_textfile` performs an **atomic rename** (writes to temp, then `os.rename`), so scrapes never see a partial file.
- Node exporter picks up any `*.prom` in its `–collector.textfile.directory`.
- The HTTP `/metrics` server (`start_http_server`) is an alternative but adds a listening port; for a single-node local engine the textfile collector is cleaner and avoids port conflicts.

## Recommendation
For UO-6.4, use the textfile collector: each worker writes its own `*.prom` into `data/observability/` (or the node-exporter textfile dir). The Fleet Health Dashboard plugin (R13) can also emit `fleet_health.prom`. Do **not** stand up a separate `:8016/metrics` HTTP server unless the hub already serves it. This keeps metrics local-first (M7) and satisfies M8 observability without a broker.

## Confidence
**HIGH** — `write_to_textfile` is a long-standing, stable prometheus_client feature; the docs were refreshed 2026-04-17.

## Remaining Unknowns
- Whether node-exporter is installed on the host (if not, the `.prom` files are still useful as periodic snapshots; a tiny scraper can read them).
- Scrape interval / retention policy for the `.prom` files.

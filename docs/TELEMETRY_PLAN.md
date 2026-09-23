# Telemetry Collection Plan for LLM Benchmarking

**Status**: Approved for implementation (post-compaction)
**Created**: 2026-09-22
**Target**: `scripts/screening.py` enhancement

---

## Research-Backed Best Practices

| Source | Key Practice |
|--------|--------------|
| **MLPerf Inference** | 30s thermal stabilization, 10 Hz sampling, sync power with query boundaries |
| **ADTC Profiler** | Background thread reads RAPL `/sys/class/powercap/intel-rapl:0/energy_uj`, handles wraparound |
| **Turing Pi RK1** | 25-min sustained runs, document full temp curve: idle → ramp-up → steady-state → throttle |
| **asiai bench** | 3 iterations/prompt, median primary, `temperature=0` for deterministic runs |
| **RAPL + turbostat** | `energy_uj` delta → watts; turbostat for per-core freq, C-states, pkg power |
| **Thermal throttling** | `/sys/class/thermal/thermal_zone*/temp` + `throttling_count` in cpufreq stats |

---

## TelemetryCollector Design

```python
class TelemetryCollector:
    """Background telemetry sampler for LLM inference runs."""
    
    def __init__(self, sample_interval=0.5):  # 2 Hz
        self.interval = sample_interval
        self.samples = []
        self._thread = None
        self._stop = threading.Event()
        self._rapl_baseline = None
        
    def start(self):
        """Call before inference begins."""
        self._rapl_baseline = self._read_rapl_energy()
        self.samples.clear()
        self._stop.clear()
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()
        
    def stop(self):
        """Call after inference completes. Returns aggregated telemetry dict."""
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        return self._aggregate()
        
    def _sample_loop(self):
        while not self._stop.is_set():
            self.samples.append({
                'ts': time.monotonic(),
                'cpu_freq': self._read_cpu_freqs(),      # dict core_id -> MHz
                'cpu_temp': self._read_cpu_temps(),      # dict core_id -> °C
                'pkg_temp': self._read_pkg_temp(),       # °C
                'pkg_power': self._read_rapl_power(),    # watts
                'dram_power': self._read_rapl_dram(),    # watts
                'mem': self._read_meminfo(),             # RSS, swap, ZRAM
                'throttle': self._read_throttle_counts(),# per-core events
            })
            time.sleep(self.interval)
            
    def _aggregate(self):
        """Return min/max/mean/std + derived metrics."""
        if not self.samples:
            return {}
        
        # Compute aggregates per metric
        # Derived:
        #   energy_per_token_mj = total_pkg_energy_j / output_tokens * 1000
        #   thermal_throttled = any sample > throttle_threshold
        #   freq_throttle_pct = fraction of samples below base_freq
```

---

## Per-Run Output Extension

```json
{
  "run": 1,
  "tps": 7.9,
  "telemetry": {
    "cpu_pkg_power_w": {"mean": 28.4, "p50": 27.1, "p95": 35.2, "peak": 41.0},
    "cpu_pkg_temp_c": {"mean": 68.2, "peak": 74.0},
    "cpu_core_freq_mhz": {"mean": 2100, "min": 800, "throttle_pct": 0.0},
    "memory": {"rss_gb": 8.2, "swap_mb": 0, "zram_compressed_gb": 1.1},
    "thermal_throttled": false,
    "energy_per_token_mj": 3.6,
    "sampling_hz": 2.0
  }
}
```

---

## Model-Level Telemetry Summary

```json
"telemetry_summary": {
  "avg_pkg_power_w": 28.4,
  "peak_pkg_temp_c": 74,
  "energy_per_token_mj": 3.6,
  "thermal_throttling_events": 0,
  "memory_pressure_pct": 12,
  "freq_throttle_pct": 0.0
}
```

---

## Implementation Checklist

- [ ] Add `TelemetryCollector` class to `scripts/screening.py`
- [ ] Wrap each `generate()` call with `collector.start()` / `collector.stop()`
- [ ] Extend result schema with `telemetry` object
- [ ] Add `telemetry_summary` to screening output JSON
- [ ] Run screening on remaining 4 models (gemma-3-12b, phi4-mini-reasoning, nemotron3-nano, rocracoon-3b)
- [ ] Update all 6 model cards with telemetry sections
- [ ] Run `make lint` and `make test`

---

## Overhead Estimate

| Component | Cost |
|-----------|------|
| Sampling (2 Hz) | ~2ms/sample |
| CPU impact | <0.5% |
| Memory | ~200 KB per model screening |
| t/s measurement impact | Zero (background thread) |

---

## Files to Modify

1. `scripts/screening.py` — add TelemetryCollector + integration
2. `docs/models/*.md` — add telemetry sections to model cards
3. `benchmarking/screening/*.json` — regenerated with telemetry data
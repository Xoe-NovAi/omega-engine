# 🔱 Hub — Hardware Stats Bridge for Degradation Management
**AP Token**: `AP-HUB-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Hub module — hardware stats bridge used by Oracle.talk() for graceful degradation under system pressure.
**Tags**: hub, hardware, stats, bridge, degradation, oracle
**Cross-references**: src/omega/hub.py, src/omega/monitoring/__init__.py, src/omega/oracle/oracle.py, SOVEREIGN_MANDATES.md

---

## Overview

The `hub.py` module provides a **simplified async interface** to hardware telemetry for the Oracle. It bridges the `monitoring` package to the Oracle's degradation management system.

**M2/M16 Engine-Stack Firewall Compliance**: Uses `omega.monitoring` directly — no cross-boundary import from `mcp_servers`.

---

## Function

### `async get_hardware_stats() -> Dict[str, Any]`

Get hardware stats dict for degradation management.

```python
from omega.hub import get_hardware_stats

stats = await get_hardware_stats()
# {
#   "cpu_usage": 12.3,
#   "memory_available_mb": 8234,
#   "memory_total_mb": 13952,
#   "temperature_c": 52.0
# }
```

**Returns**:
| Key | Type | Description |
|-----|------|-------------|
| `cpu_usage` | `float` | Average CPU utilization % (0-100) |
| `memory_available_mb` | `float` | Available memory in MB |
| `memory_total_mb` | `float` | Total memory in MB |
| `temperature_c` | `float` | CPU temperature in Celsius |

**Fallback**: On any error, returns safe defaults:
```python
{"cpu_usage": 0.0, "memory_available_mb": 1024, "memory_total_mb": 0, "temperature_c": 0.0}
```

---

## Integration with Oracle

The Oracle uses this for **graceful degradation** under system pressure:

```python
# In oracle.py
from omega.hub import get_hardware_stats

class Oracle:
    async def talk(self, query: str, ...) -> OracleResponse:
        # Check hardware before routing
        hw = await get_hardware_stats()
        
        if hw["memory_available_mb"] < 2048:
            # Force local-only, smaller model
            constraints.preferred_backends = ["local"]
            constraints.max_cost_usd = 0.0
        
        if hw["cpu_usage"] > 90:
            # Reduce concurrency, increase timeouts
            constraints.max_latency_ms = 30000
        
        # ... proceed with routing
```

---

## Implementation

```python
async def get_hardware_stats() -> Dict[str, Any]:
    try:
        from omega.monitoring import HardwareMonitor
        
        def _collect() -> Dict[str, Any]:
            hm = HardwareMonitor()
            stats = hm.collect_all()
            cpu = stats.get("cpu", {})
            mem = stats.get("memory", {})
            return {
                "cpu_usage": cpu.get("avg_percent", 0.0),
                "memory_available_mb": mem.get("available_mb", 1024),
                "memory_total_mb": mem.get("total_mb", 0),
                "temperature_c": stats.get("thermal", {}).get("cpu_temp_c", 0.0),
            }
        
        return await anyio.to_thread.run_sync(_collect)
    
    except ImportError:
        logger.debug("get_hardware_stats: omega.monitoring not available")
        return {"cpu_usage": 0.0, "memory_available_mb": 1024}
    except (RuntimeError, OSError) as e:
        logger.warning("get_hardware_stats failed: %s", e)
        return {"cpu_usage": 0.0, "memory_available_mb": 1024}
```

**Key Points**:
- Runs blocking `HardwareMonitor.collect_all()` in thread pool (`anyio.to_thread`)
- Catches `ImportError` (monitoring not available) and `RuntimeError`/`OSError` (collection failed)
- Returns safe defaults on failure — never crashes Oracle

---

## Usage Example

```python
from omega.hub import get_hardware_stats

# Direct usage
stats = await get_hardware_stats()
print(f"CPU: {stats['cpu_usage']:.1f}%")
print(f"RAM: {stats['memory_available_mb']:.0f}/{stats['memory_total_mb']:.0f} MB")
print(f"Temp: {stats['temperature_c']:.1f}°C")

# In degradation logic
async def check_degradation() -> Dict[str, Any]:
    hw = await get_hardware_stats()
    
    degradation = {
        "force_local": hw["memory_available_mb"] < 2048,
        "reduce_concurrency": hw["cpu_usage"] > 85,
        "thermal_throttle": hw["temperature_c"] > 80,
        "memory_pressure": hw["memory_available_mb"] / max(hw["memory_total_mb"], 1) < 0.15
    }
    
    return degradation
```

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | `anyio.to_thread.run_sync` for blocking call |
| **M2 Firewall** | Direct `omega.monitoring` import; no `mcp_servers` |
| **M7 Local-First** | Local hardware telemetry only |
| **M13 Temple-Grade** | Safe defaults on failure; never crashes caller |
| **M23 Failure Integrity** | Explicit error handling; no silent failures |

---

## Testing

```bash
pytest tests/test_hub.py -v
```

Key test scenarios:
- Successful stats collection
- ImportError fallback
- RuntimeError/OSError fallback
- Return value structure
- Integration with mock Oracle

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ HUB-v1.0.0 ⬡ 2026-10-02 ⬡*
<!-- PROVENANCE-CORRECTED 2026-10-03T06:22:36Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->


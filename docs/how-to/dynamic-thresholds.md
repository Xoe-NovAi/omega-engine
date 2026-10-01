<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 How-To: Configuring M33Probe Dynamic Write-Tool Thresholds

**AP Token**: `AP-HOWTO-DYNAMIC-THRESHOLDS-v1.0.0`  
**Status**: ACTIVE  
**Date**: 2026-09-07  
**Related**: `src/omega/oracle/m33_probe.py`, `docs/architecture/ARCHANGEL_ARCHITECTURE.md`, `docs/how-to/hardware-awareness.md`

---

## Overview

The **M33 Sentinel Probe** (Layer 1: Preventive) decides whether a subagent must use the write tool (`write_tool_required=True`) instead of streaming output via chat. As of v1.6.1 (Archangel Architecture), the threshold is **dynamic** — it scales based on real-time hardware telemetry from `HardwareMonitor`.

This prevents OOM kills and thermal throttling during long-form subagent outputs by forcing earlier file writes under pressure.

---

## Threshold Logic

### Base Threshold

```python
WRITE_TOOL_TOKEN_THRESHOLD = 8000  # Tokens (per meta-review §1.1)
```

### Dynamic Scaling Rules

The `M33Probe.calculate_dynamic_write_threshold()` method (in `src/omega/oracle/m33_probe.py`) queries `HardwareMonitor` and applies:

| Condition | Threshold | Reduction | Rationale |
|-----------|-----------|-----------|-----------|
| `memory_pressure > 0.7` (CRITICAL) | **2000 tokens** | 75% | Imminent OOM — force immediate file writes |
| `memory_pressure > 0.5` (HIGH) | **4000 tokens** | 50% | High pressure — aggressive file writes |
| `memory_pressure > 0.3` (MODERATE) | **6000 tokens** | 25% | Moderate pressure — early file writes |
| `thermal_throttling == True` | **2000 tokens** | 75% | CPU throttling — minimize memory residency |
| `oom_risk == "CRITICAL"` | **2000 tokens** | 75% | OOM imminent — aggressive flush |
| `oom_risk == "HIGH"` | **4000 tokens** | 50% | High OOM risk — early flush |
| `oom_risk == "MODERATE"` | **6000 tokens** | 25% | Elevated OOM risk — precautionary |
| **Base (SAFE)** | **8000 tokens** | — | Normal operation |

**Priority**: Most restrictive condition wins (lowest threshold applies).

---

## How It Works

### Integration Point

In `M33Probe.should_require_write_tool()`:

```python
def should_require_write_tool(self, estimated_output_tokens, task_type, priority):
    # Archangel Architecture: Dynamic threshold based on hardware state
    dynamic_threshold = self.calculate_dynamic_write_threshold()
    
    if estimated_output_tokens > dynamic_threshold:
        return True
    # ... P0/P1, research/forensic checks ...
```

### HardwareMonitor Metrics Consumed

| Metric | Source | Range | Meaning |
|--------|--------|-------|---------|
| `memory_pressure` | `HardwareMonitor.get_memory_status()["memory_pressure"]` | 0.0–1.0 | 0=SAFE, 1=CRITICAL |
| `thermal_throttling` | `HardwareMonitor.is_thermal_throttling()` | bool | True if any core > 85°C |
| `oom_risk_level` | `mem.get("oom_risk", {}).get("risk_level")` | SAFE/MODERATE/HIGH/CRITICAL | OOM risk classification |

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OMEGA_M33_LOG` | `data/coordination/m33_probe_audit.jsonl` | Audit log path |

### Constants (in `m33_probe.py`)

```python
# Base threshold (per meta-review §1.1)
WRITE_TOOL_TOKEN_THRESHOLD = 8000

# Confidence thresholds (unchanged)
CONFIDENCE_THRESHOLD_P0 = 0.99
CONFIDENCE_THRESHOLD_P1 = 0.97
CONFIDENCE_THRESHOLD_P2 = 0.95
CONFIDENCE_THRESHOLD_P3 = 0.85
```

### Tuning the Scaling Factors

To adjust the scaling, edit `calculate_dynamic_write_threshold()`:

```python
def calculate_dynamic_write_threshold(self) -> int:
    base_threshold = WRITE_TOOL_TOKEN_THRESHOLD
    hw = self._get_hw_monitor()
    
    if hw is None:
        return base_threshold
    
    try:
        mem = hw.get_memory_status()
        pressure = mem.get("memory_pressure", 0.0)
        thermal_throttling = hw.is_thermal_throttling()
        oom_risk = mem.get("oom_risk", {}).get("risk_level", "SAFE")
        
        # --- TUNABLE SCALING FACTORS ---
        if pressure > 0.7:
            return max(2000, int(base_threshold * 0.25))   # 25% of base
        elif pressure > 0.5:
            return max(4000, int(base_threshold * 0.5))    # 50% of base
        elif pressure > 0.3:
            return max(6000, int(base_threshold * 0.75))   # 75% of base
        
        if thermal_throttling:
            return max(2000, int(base_threshold * 0.3))    # 30% of base
        
        if oom_risk == "CRITICAL":
            return max(2000, int(base_threshold * 0.25))
        elif oom_risk == "HIGH":
            return max(4000, int(base_threshold * 0.5))
        elif oom_risk == "MODERATE":
            return max(6000, int(base_threshold * 0.75))
        
    except (OSError, ValueError, TypeError, AttributeError) as e:
        logger.debug("Dynamic threshold calculation failed, using base: %s", e)
    
    return base_threshold
```

---

## Testing the Dynamic Threshold

### Unit Test

```python
from omega.oracle.m33_probe import M33Probe

probe = M33Probe(m34_registry=None)

# Mock high pressure
probe._hw_monitor = MockHardwareMonitor(
    memory_pressure=0.8,
    thermal_throttling=False,
    oom_risk="SAFE"
)

threshold = probe.calculate_dynamic_write_threshold()
assert threshold == 2000, f"Expected 2000, got {threshold}"
print(f"High pressure threshold: {threshold}")

# Mock thermal throttling
probe._hw_monitor = MockHardwareMonitor(
    memory_pressure=0.1,
    thermal_throttling=True,
    oom_risk="SAFE"
)

threshold = probe.calculate_dynamic_write_threshold()
assert threshold == 2000, f"Expected 2000, got {threshold}"
print(f"Thermal throttling threshold: {threshold}")

# Baseline
probe._hw_monitor = MockHardwareMonitor(
    memory_pressure=0.05,
    thermal_throttling=False,
    oom_risk="SAFE"
)

threshold = probe.calculate_dynamic_write_threshold()
assert threshold == 8000, f"Expected 8000, got {threshold}"
print(f"Baseline threshold: {threshold}")
```

### Live Test Under Pressure

```bash
# Simulate memory pressure (Linux)
stress-ng --vm 2 --vm-bytes 80% --timeout 60s &

# Monitor threshold in real-time
python3 -c "
from omega.oracle.m33_probe import M33Probe
import time
probe = M33Probe(m34_registry=None)
for i in range(12):
    t = probe.calculate_dynamic_write_threshold()
    print(f'T+{i*5}s: threshold={t} tokens')
    time.sleep(5)
"
```

---

## Decision Matrix: When Does `write_tool_required=True`?

The final decision combines dynamic threshold with task metadata:

```python
def should_require_write_tool(self, estimated_output_tokens, task_type, priority):
    dynamic_threshold = self.calculate_dynamic_write_threshold()
    
    # 1. Dynamic hardware threshold (Archangel)
    if estimated_output_tokens > dynamic_threshold:
        return True
    
    # 2. Priority override (P0/P1 always write)
    if priority in ("P0", "P1"):
        return True
    
    # 3. Task type override (research/forensic/review/design always write)
    if task_type in ("research", "forensic", "review", "design"):
        return True
    
    return False
```

### Effective Thresholds by Scenario

| Scenario | Priority | Task Type | Estimated Tokens | Dynamic Threshold | Result |
|----------|----------|-----------|------------------|-------------------|--------|
| Normal research | P2 | research | 5000 | 8000 | **True** (task type) |
| Normal implement | P2 | implement | 5000 | 8000 | False |
| High pressure research | P2 | research | 5000 | 2000 | **True** (threshold) |
| Thermal throttling implement | P2 | implement | 5000 | 2000 | **True** (threshold) |
| P0 audit | P0 | audit | 3000 | 8000 | **True** (priority) |
| P3 quick verify | P3 | verify | 10000 | 8000 | **True** (threshold) |

---

## Monitoring & Observability

### Audit Log

Every `should_require_write_tool()` call logs to `OMEGA_M33_LOG`:

```json
{
  "timestamp": "2026-09-07T18:39:51.976502+00:00",
  "packet_id": "hdp_20260907_researcher_verity_a1b2c3d4",
  "target_agent": "verity",
  "estimated_output_tokens": 5420,
  "dynamic_threshold": 8000,
  "write_tool_required": false,
  "memory_pressure": 0.015,
  "thermal_throttling": false,
  "oom_risk_level": "SAFE"
}
```

### Metrics to Watch

| Metric | Alert Threshold | Action |
|--------|-----------------|--------|
| `write_tool_required` rate > 80% | Sustained high pressure | Investigate memory leak / add RAM |
| `dynamic_threshold` frequently < 4000 | Chronic pressure | Upgrade RAM / fix memory leak |
| `thermal_throttling` = true | Any occurrence | Check cooling / reduce concurrency |

---

## Troubleshooting

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| Threshold always 8000 | `HardwareMonitor` unavailable | Check `omega.monitoring` import; verify `psutil` installed |
| Threshold stuck at 2000 | Stale `HardwareMonitor` cache | Restart engine; check `hw_monitor.collect_all()` |
| False positives (write required when not needed) | Over-aggressive scaling | Increase pressure thresholds (e.g., 0.7 → 0.8) |
| False negatives (no write, then OOM) | Under-aggressive scaling | Decrease pressure thresholds (e.g., 0.5 → 0.4) |

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| `docs/architecture/ARCHANGEL_ARCHITECTURE.md` | Full spec with threshold table |
| `docs/how-to/hardware-awareness.md` | Envelope injection overview |
| `src/omega/oracle/m33_probe.py` | Implementation |
| `src/omega/monitoring/__init__.py` | `HardwareMonitor` source |

---

*⬡ OMEGA ⬡ DYNAMIC-THRESHOLDS-HOWTO ⬡ 2026-09-07*
<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 How-To: Injecting Hardware State into Agent Prompts

**AP Token**: `AP-HOWTO-HARDWARE-AWARENESS-v1.0.0`  
**Status**: ACTIVE  
**Date**: 2026-09-07  
**Related**: `docs/architecture/ARCHANGEL_ARCHITECTURE.md`, `src/omega/oracle/env_hardware_probe.py`

---

## Overview

The **Archangel Architecture** resolves the **Ontological Void** — agents historically hallucinate their hardware (model, CPU, RAM, thermal state) because they lack ground-truth telemetry. This guide explains how the system injects a **hardware register** into every agent's prompt at dispatch time, and how to work with it.

---

## The System Envelope

Every subagent dispatch receives a **System Envelope** prepended to its context:

```
[SYSTEM REGISTER: BARE-METAL PHYSICAL BOUNDARY]
 - HOST OS: AMD Ryzen 7 5700U (Zen 2)
 - ASSIGNED HARDWARE CORES: 16 Threads (NUMA Node: 0)
 - CPU UTILIZATION: 8.5%
 - AVAILABLE RAM REGISTERS: 7479 MB / 14793 MB
 - PROCESS WORKING SET (RSS): 0 MB
 - MEMORY PRESSURE INDEX: 0.015 (OOM RISK: SAFE)
 - THERMAL STATE: 73.8°C (OK)
 - COMPUTE ACTIVE MODEL: qwen3-1.7b-q6_k
 - COMPUTE ENGINE BACKEND: NativeGGUFProvider
 - METRIC TIMESTAMP MONOTONIC: 23951.68 | WALL-CLOCK: 2026-09-07T18:39:51.976502+00:00
 - ENVELOPE METRIC TTL: 30 SECONDS
CRITICAL INVARIANT: You are bound strictly to this runtime profile. Do not extrapolate, hallucinate hardware nodes outside this register, or assume external local environments.
```

### Field Reference

| Field | Description | Example |
|-------|-------------|---------|
| `HOST OS` | Kernel + hardware model | `AMD Ryzen 7 5700U (Zen 2)` |
| `ASSIGNED HARDWARE CORES` | Logical threads + NUMA node | `16 Threads (NUMA Node: 0)` |
| `CPU UTILIZATION` | Current average CPU % | `8.5%` |
| `AVAILABLE RAM REGISTERS` | Available / Total system RAM | `7479 MB / 14793 MB` |
| `PROCESS WORKING SET (RSS)` | Current process memory | `0 MB` |
| `MEMORY PRESSURE INDEX` | 0.0 (safe) → 1.0 (critical) | `0.015` |
| `OOM RISK` | Risk level | `SAFE \| MODERATE \| HIGH \| CRITICAL` |
| `THERMAL STATE` | Max core temp + throttling flag | `73.8°C (OK)` |
| `COMPUTE ACTIVE MODEL` | Model ID from ModelGateway | `qwen3-1.7b-q6_k` |
| `COMPUTE ENGINE BACKEND` | Provider class name | `NativeGGUFProvider` |
| `METRIC TIMESTAMP MONOTONIC` | `time.monotonic()` at sample | `23951.68` |
| `WALL-CLOCK` | ISO 8601 UTC timestamp | `2026-09-07T18:39:51.976502+00:00` |
| `ENVELOPE METRIC TTL` | Validity window in seconds | `30` |

---

## How It Works

### Dispatch Pipeline Hook

The envelope is injected in `src/omega/oracle/subagent_dispatcher.py::dispatch()`:

```python
# After M33Probe validation, before build_dispatch_prompt()
if inject_system_envelope_sync is not None:
    hw_monitor = _get_hw_monitor()
    model_gateway = _get_model_gateway()
    if hw_monitor is not None and model_gateway is not None:
        packet = inject_system_envelope_sync(
            packet=packet,
            target_agent=packet.target_agent,
            hw_monitor=hw_monitor,
            model_gateway=model_gateway,
        )
```

### Envelope Generation

`SystemEnvelopeInjector` (in `src/omega/oracle/env_hardware_probe.py`):

1. Calls `HardwareMonitor.collect_all()` for live telemetry
2. Resolves target agent's model/backend via `ModelGateway`
3. Constructs frozen `RuntimeHardwareRegister` (TTL=30s)
4. Formats text envelope
5. Prepends to `packet.context`

---

## Working with the Envelope

### As an Agent

**Do:**
- Reference the envelope for any hardware-related claims
- Check `ENVELOPE METRIC TTL` — if your reasoning loop exceeds 30s, the data may be stale
- Treat the envelope as **ground truth** — contradicting it is a hallucination

**Don't:**
- Hallucinate hardware not in the envelope (e.g., "I'm Nemotron 3 Ultra on ASUS ExpertBook")
- Assume external hardware (cloud GPUs, other nodes) unless explicitly in envelope
- Ignore `OOM RISK` or `THERMAL STATE` when planning long outputs

### Checking Staleness

The `RuntimeHardwareRegister` carries its own TTL:

```python
from omega.oracle.env_hardware_probe import RuntimeHardwareRegister

reg = RuntimeHardwareRegister(...)
if reg.is_stale():  # Uses time.monotonic() internally
    # Request fresh envelope from dispatcher
    pass
```

### Accessing Programmatically

The envelope is plain text in `packet.context`. Parse it:

```python
def parse_envelope(context: str) -> dict:
    """Extract key-value pairs from [SYSTEM REGISTER: ...] block."""
    lines = context.split('\n')
    in_register = False
    data = {}
    for line in lines:
        if line.startswith('[SYSTEM REGISTER:'):
            in_register = True
            continue
        if in_register and line.startswith('CRITICAL INVARIANT'):
            break
        if in_register and ':' in line:
            key, val = line.split(':', 1)
            data[key.strip(' -')] = val.strip()
    return data
```

---

## Integration Points

### M33Probe Dynamic Threshold

The same hardware telemetry drives the M33Probe's write-tool threshold:

| Condition | Threshold |
|-----------|-----------|
| `memory_pressure > 0.7` | 2000 tokens |
| `memory_pressure > 0.5` | 4000 tokens |
| `memory_pressure > 0.3` | 6000 tokens |
| `thermal_throttling == True` | 2000 tokens |
| `oom_risk == "CRITICAL"` | 2000 tokens |
| `oom_risk == "HIGH"` | 4000 tokens |
| `oom_risk == "MODERATE"` | 6000 tokens |
| Base (SAFE) | 8000 tokens |

See `docs/how-to/dynamic-thresholds.md` for details.

### SkepticalVerifier

The `SkepticalVerifier` cross-references agent claims against the envelope. Any hardware claim contradicting the register is flagged `CONTRADICTED`.

---

## Testing the Envelope

### Manual Injection Test

```python
from omega.oracle.env_hardware_probe import inject_system_envelope_sync
from omega.oracle.subagent_dispatcher import HandoffPacket
from omega.monitoring import HardwareMonitor
from omega.oracle.model_gateway import ModelGateway
from omega.oracle.health_monitor import get_health_monitor

packet = HandoffPacket(
    source_agent='researcher',
    target_agent='verity',
    task_type='audit',
    task_description='Test envelope',
    relevant_files=[],
    context='Original context',
    priority='P1'
)

hw = HardwareMonitor()
gw = ModelGateway(health_monitor=get_health_monitor())

result = inject_system_envelope_sync(packet, 'verity', hw, gw)
print(result.context[:500])
```

### Verify Envelope in Dispatch

```bash
# Run a test dispatch and check context
python3 -c "
from omega.oracle.subagent_dispatcher import dispatch, HandoffPacket
p = HandoffPacket(source_agent='researcher', target_agent='verity', task_type='audit', task_description='Test', relevant_files=[], context='', priority='P1')
prompt = dispatch(p)
print('[SYSTEM REGISTER:' in prompt)  # Should be True
"
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| No envelope in prompt | `HardwareMonitor` or `ModelGateway` unavailable | Check logs for "Archangel envelope skipped" |
| Envelope shows wrong model | `ModelGateway` affinity misconfigured | Check `config/entity_model_affinity.yaml` |
| Stale envelope in long loop | TTL exceeded (30s) | Dispatcher auto-refreshes on next hop |
| Envelope missing in `summon()` | Only subagent dispatches get envelope | `summon()` uses direct entity, not subagent dispatch |

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| `docs/architecture/ARCHANGEL_ARCHITECTURE.md` | Full specification |
| `docs/how-to/dynamic-thresholds.md` | M33Probe dynamic threshold config |
| `src/omega/oracle/env_hardware_probe.py` | Implementation |
| `src/omega/oracle/subagent_dispatcher.py` | Injection hook |

---

*⬡ OMEGA ⬡ HARDWARE-AWARENESS-HOWTO ⬡ 2026-09-07*
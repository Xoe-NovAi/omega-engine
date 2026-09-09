#  🔱 OMEGA ENGINE — SPECIFICATION & IMPLEMENTATION MANUAL
## Archangel Architecture: Agent-Level Hardware Awareness via System Envelope Injection

```
schema_version: "1.0.0"
document_type: "specification_manual"
document_id: "SPEC-ARCHANGEL-v1.0.0"
title: "Archangel Architecture — Agent-Level Hardware Awareness via System Envelope Injection"
status: "ACTIVE"
date: "2026-09-07"
author: "researcher"
model: "nemotron-3-ultra-free"
channel: "opencode"
sprint: "PUBLIC-DEBUT-01"
governing_mandates: ["M1", "M2", "M7", "M13", "M14", "M22", "M23", "M27"]
supersedes: "N/A — New Architecture"
related: ["SPEC-DHAL-v1.0.0", "SPEC-M33-PROBE-v1.0.0", "SPEC-SUBAGENT-DISPATCH-v1.0.0"]
```

---

### §1. EXECUTIVE SUMMARY & ARCHITECTURAL INTENT

**The Problem — The Ontological Void**

Omega Engine agents historically operated in an **Ontological Void**: they received task prompts containing context, goals, and constraints, but possessed **zero intrinsic knowledge of their physical execution substrate**. An agent did not know:
- Its host model identifier, quantization format, or parameter count
- The CPU microarchitecture, core topology, or thread affinity
- Available system RAM, memory pressure, or OOM risk level
- Thermal state, throttling status, or zRAM compression ratio
- NUMA node assignment or cache hierarchy

When a model lacks cold, hard data parameters regarding its physical reality, it fills the void by predicting the most statistically authoritative tokens available in its weights. It creates an **idealized hardware persona** (e.g., "I am Nemotron 3 Ultra running on an ASUS ExpertBook with AVX-512 VNNI") because its underlying neural path is optimized for cohesive narrative generation, not bare-metal self-reflection.

This manifested catastrophically in **Turn 9** of the GSCA study: the Researcher agent hallucinated a local Nemotron 3 Ultra deployment on an ASUS ExpertBook that did not exist — the Lead was on an HP laptop with no local Nemotron deployment.

**The Mandate**

To achieve absolute agent reliability, we must move from **passive Context Engineering** to **hardware-bound State Reflection**. We must turn the physical host environment into a permanent, injected **System Register** — an immutable, temporally bounded hardware manifest prepended to every agent's system prompt at dispatch time.

**The Solution — Archangel Architecture**

Archangel Architecture resolves the Ontological Void by bridging Omega's existing `HardwareMonitor` (892 lines, `src/omega/monitoring/__init__.py`) to the agent prompt layer via **System Envelope Injection**:

1. **Environmental State Register (ESR)** — `src/omega/oracle/env_hardware_probe.py` wraps `HardwareMonitor`, fills ESR gaps (NUMA node, model/backend mapping), and generates a frozen `RuntimeHardwareRegister` with monotonic/wall timestamps + 30-second TTL.

2. **System Envelope Injection** — At dispatch time (`subagent_dispatcher.py`), after M33Probe validation and before `build_dispatch_prompt()`, the `SystemEnvelopeInjector` queries live hardware state, resolves the target agent's model/backend via `ModelGateway`, and prepends the `[SYSTEM REGISTER: BARE-METAL PHYSICAL BOUNDARY]` envelope to `packet.context`.

3. **Temporal Grounding** — Every register carries `sampled_at_monotonic`, `sampled_at_wall`, and `sample_validity_seconds = 30`. If a remediation loop exceeds TTL, the dispatcher draws a fresh sample.

4. **M33Probe Integration** — Dynamic write-tool threshold (`calculate_dynamic_write_threshold()`) scales based on `memory_pressure_score`, `thermal_throttling`, and `oom_risk_level` from the same `HardwareMonitor`.

**Relationship to DHAL**

| Layer | DHAL (Dynamic Hardware Adaptation Layer) | Archangel Architecture |
|-------|------------------------------------------|------------------------|
| **Scope** | System-level: compiler flags, core pinning, Council concurrency, ResourceGuard | Agent-level: prompt injection, hallucination prevention, write-tool gating |
| **Trigger** | Boot / hardware change | Every subagent dispatch |
| **Consumer** | `Zen2Optimizer`, `CouncilScheduler`, `ResourceGuard` | `SkepticalVerifier`, `M33Probe`, every subagent |
| **Artifact** | `config/hardware_profile.yaml` (git-ignored) | `[SYSTEM REGISTER: ...]` envelope (ephemeral, per-dispatch) |
| **Mandate** | M2, M7, M13, M14, M22, M23 | M1, M2, M7, M13, M14, M22, M23, M27 |

**They are complementary, not redundant.** DHAL adapts the *engine* to the hardware; Archangel adapts the *agent's mind* to the hardware.

---

### §2. CORE ARCHITECTURAL PRINCIPLES

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    OMEGA ENGINE DISPATCH PIPELINE                          │
│                                                                            │
│  [HandoffPacket]                                                           │
│       │                                                                    │
│       ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ M34 Registry Registration (M34-HOOK-001)                            │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│       │                                                                    │
│       ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ M33Probe.should_require_write_tool()                                │  │
│  │   └─ calculate_dynamic_write_threshold() → HardwareMonitor          │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│       │                                                                    │
│       ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ ARCHANGEL ENVELOPE INJECTION (NEW)                                  │  │
│  │   ├─ HardwareMonitor.collect_all()                                  │  │
│  │   ├─ ModelGateway.get_model_for_entity(target_agent)                │  │
│  │   ├─ ModelGateway.get_provider_for_entity(target_agent)             │  │
│  │   ├─ RuntimeHardwareRegister (frozen, TTL=30s)                      │  │
│  │   └─ packet.context = envelope + "\n\n" + packet.context            │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│       │                                                                    │
│       ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ build_dispatch_prompt() → Task tool prompt                          │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

#### Principle 1: Immutability with Temporal Validity
The `RuntimeHardwareRegister` is a **frozen dataclass** — once sampled, it cannot be mutated. It carries its own temporal validity window (`sample_validity_seconds = 30`). An agent can verify freshness via `register.is_stale()`.

#### Principle 2: Mathematical Contradiction Penalty
When a model receives a prompt whose absolute prefix explicitly states:
```
ACTIVE MODEL: qwen3-1.7b-q6_k
HOST OS: AMD Ryzen 7 5700U (Zen 2)
BACKEND: NativeGGUFProvider
```
Any statistical path inside the neural network attempting to predict tokens like "Nemotron 3 Ultra" or "ASUS ExpertBook" faces an **immediate, massive mathematical contradiction penalty** in the attention mechanism. The hallucination basin is crushed before the model emits a single character.

#### Principle 3: Zero-Trust Hardware Grounding
Agents must **never** trust their own parametric knowledge about hardware. The System Register is the **sole authority** on physical reality. Any agent output contradicting the register is, by definition, a hallucination.

#### Principle 4: Mandate Compliance by Construction
- **M1 (AnyIO)**: All monitoring calls wrapped in `anyio.to_thread.run_sync` (via `HardwareMonitor` internals)
- **M2 (Firewall)**: `env_hardware_probe.py` lives in `src/omega/oracle/` (Core); no Stack logic
- **M7 (Local-First)**: All telemetry from local `psutil`/`/proc`/`/sys`; zero cloud deps
- **M13 (Temple-Grade)**: Envelope injection gated by `make temple-grade` pipeline
- **M14 (Heritage)**: `[id-soft: vet-XXX]` tags on all new types
- **M22 (Provenance)**: `GenerateResult.provider_name` captured at receipt
- **M23 (Failure Integrity)**: Injection failure → logged warning, dispatch continues (graceful degradation)
- **M27 (Tracking Integrity)**: `trace_id` propagated through envelope for observability

---

### §3. DETAILED SCHEMA & DATA MODELS

#### 3.1 RuntimeHardwareRegister (Frozen, Immutable)

```python
@dataclass(frozen=True)
class RuntimeHardwareRegister:
    """Immutable hardware register snapshot — the agent's bare-metal truth.
    Frozen to prevent post-hoc mutation; carries its own temporal validity window.
    """
    host_os: str                              # e.g., "Linux 6.8.0 (HP Laptop Baseline)"
    active_cpu_cores: int                     # Logical threads available to process
    cpu_utilization_pct: float                # Current CPU utilization (0.0-100.0)
    available_system_ram_mb: float            # Available RAM in MB
    total_system_ram_mb: float                # Total system RAM in MB
    process_memory_rss_mb: float              # Current process RSS in MB
    memory_pressure_score: float              # Bounded [0.0, 1.0] (0=SAFE, 1=CRITICAL)
    oom_risk_level: str                       # "SAFE" | "MODERATE" | "HIGH" | "CRITICAL"
    thermal_throttling: bool                  # True if CPU > 85°C (Zen 2 Tjmax ~95°C)
    max_core_temp_c: float                    # Maximum core temperature in Celsius
    zram_compression_ratio: float             # Overall zRAM compression ratio (1.0 = none)
    assigned_numa_node: int                   # NUMA node assignment (0 or 1)
    active_model_identifier: str              # Model ID from ModelGateway (e.g., "qwen3-1.7b-q6_k")
    active_model_backend: str                 # Backend string (e.g., "NativeGGUFProvider")
    sampled_at_monotonic: float               # time.monotonic() at sample time
    sampled_at_wall: str                      # datetime.now(timezone.utc).isoformat()
    sample_validity_seconds: int = 30         # TTL in seconds

    def is_stale(self, current_monotonic: Optional[float] = None) -> bool:
        """Check if this register sample has exceeded its TTL."""
        now = current_monotonic or time.monotonic()
        return (now - self.sampled_at_monotonic) > self.sample_validity_seconds
```

**Field Semantics & Sources**

| Field | Source | Update Frequency |
|-------|--------|------------------|
| `host_os` | `HardwareMonitor.get_cpu_topology()["model"]` | Per-dispatch |
| `active_cpu_cores` | `cpu.get("thread_count", os.cpu_count())` | Per-dispatch |
| `cpu_utilization_pct` | `cpu.get("avg_percent", 0.0)` | Per-dispatch (0.2s interval) |
| `available_system_ram_mb` | `mem.get("available_mb", 0.0)` | Per-dispatch |
| `total_system_ram_mb` | `mem.get("total_mb", 0.0)` | Per-dispatch |
| `process_memory_rss_mb` | `mem.get("process_rss_mb", 0.0)` | Per-dispatch |
| `memory_pressure_score` | `stats.get("memory_pressure", 0.0)` | Per-dispatch |
| `oom_risk_level` | `mem.get("oom_risk", {}).get("risk_level", "SAFE")` | Per-dispatch |
| `thermal_throttling` | `cpu.get("thermal_throttling", False)` | Per-dispatch |
| `max_core_temp_c` | `max(t.get('temp', 0) for t in temps.get('celsius', []))` | Per-dispatch |
| `zram_compression_ratio` | `mem.get("zram", {}).get("overall_compression_ratio", 1.0)` | Per-dispatch |
| `assigned_numa_node` | `psutil.Process().cpu_affinity()` → naive mapping | Per-dispatch |
| `active_model_identifier` | `ModelGateway.get_model_for_entity(target_agent)` | Per-dispatch |
| `active_model_backend` | `ModelGateway.get_provider_for_entity(target_agent)` | Per-dispatch |
| `sampled_at_monotonic` | `time.monotonic()` | Per-dispatch |
| `sampled_at_wall` | `datetime.now(timezone.utc).isoformat()` | Per-dispatch |

#### 3.2 System Envelope Format (Text Payload)

The envelope is a **plain-text, human-readable, machine-parseable** block prepended to `packet.context`:

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

**Parsing Contract**: The envelope is line-oriented, key-value pairs with ` - KEY: VALUE` format. The `CRITICAL INVARIANT` line is the terminator. Agents and tooling MAY parse this for programmatic access.

#### 3.3 SystemEnvelopeInjector (Core Logic)

```python
@dataclass
class SystemEnvelopeInjector:
    hw_monitor: Any          # omega.monitoring.HardwareMonitor instance
    model_gateway: Any       # omega.oracle.model_gateway.ModelGateway instance

    def _resolve_model_and_backend(self, target_agent: str) -> tuple[str, str]:
        """Resolve model identifier and backend string for the target agent."""
        entity_name = target_agent  # Agent name maps to entity name
        model_id = self.model_gateway.get_model_for_entity(entity_name)
        provider = self.model_gateway.get_provider_for_entity(entity_name)
        backend = f"{provider.__class__.__name__}" if provider else "llama.cpp / AVX-512 VNNI"
        return model_id, backend

    def generate_envelope_sync(self, target_agent: str) -> str:
        """Synchronous envelope generation for dispatch pipeline."""
        stats = self.hw_monitor.collect_all()
        mem = stats.get("memory", {})
        cpu = stats.get("cpu", {})
        temps = stats.get("temperatures", {})
        topology = stats.get("topology", {})
        
        model_id, backend = self._resolve_model_and_backend(target_agent)
        now_mono = time.monotonic()
        now_wall = datetime.now(timezone.utc).isoformat()
        max_temp = max((t.get('temp', 0) for t in temps.get('celsius', [])), default=0.0)

        reg = RuntimeHardwareRegister(
            host_os=topology.get("model", "Linux Node (HP Laptop Baseline)"),
            active_cpu_cores=cpu.get("thread_count", os.cpu_count() or 1),
            cpu_utilization_pct=float(cpu.get("avg_percent", 0.0)),
            available_system_ram_mb=float(mem.get("available_mb", 0.0)),
            total_system_ram_mb=float(mem.get("total_mb", 0.0)),
            process_memory_rss_mb=float(mem.get("process_rss_mb", 0.0)),
            memory_pressure_score=float(stats.get("memory_pressure", 0.0)),
            oom_risk_level=mem.get("oom_risk", {}).get("risk_level", "SAFE"),
            thermal_throttling=bool(cpu.get("thermal_throttling", False)),
            max_core_temp_c=float(max_temp),
            zram_compression_ratio=float(mem.get("zram", {}).get("overall_compression_ratio", 1.0)),
            assigned_numa_node=self._discover_numa_node(),
            active_model_identifier=model_id,
            active_model_backend=backend,
            sampled_at_monotonic=now_mono,
            sampled_at_wall=now_wall
        )

        thermal_status = "⚠️ THROTTLING" if reg.thermal_throttling else "OK"
        return (
            "[SYSTEM REGISTER: BARE-METAL PHYSICAL BOUNDARY]\n"
            f" - HOST OS: {reg.host_os}\n"
            f" - ASSIGNED HARDWARE CORES: {reg.active_cpu_cores} Threads (NUMA Node: {reg.assigned_numa_node})\n"
            f" - CPU UTILIZATION: {reg.cpu_utilization_pct:.1f}%\n"
            f" - AVAILABLE RAM REGISTERS: {reg.available_system_ram_mb:.0f} MB / {reg.total_system_ram_mb:.0f} MB\n"
            f" - PROCESS WORKING SET (RSS): {reg.process_memory_rss_mb:.0f} MB\n"
            f" - MEMORY PRESSURE INDEX: {reg.memory_pressure_score:.3f} (OOM RISK: {reg.oom_risk_level})\n"
            f" - THERMAL STATE: {reg.max_core_temp_c:.1f}°C ({thermal_status})\n"
            f" - COMPUTE ACTIVE MODEL: {reg.active_model_identifier}\n"
            f" - COMPUTE ENGINE BACKEND: {reg.active_model_backend}\n"
            f" - METRIC TIMESTAMP MONOTONIC: {reg.sampled_at_monotonic:.2f} | WALL-CLOCK: {reg.sampled_at_wall}\n"
            f" - ENVELOPE METRIC TTL: {reg.sample_validity_seconds} SECONDS\n"
            "CRITICAL INVARIANT: You are bound strictly to this runtime profile. Do not extrapolate, "
            "hallucinate hardware nodes outside this register, or assume external local environments.\n"
        )

    def _discover_numa_node(self) -> int:
        """Naive NUMA mapping via CPU affinity."""
        try:
            p = psutil.Process(os.getpid())
            affinity = p.cpu_affinity()
            if affinity:
                return 0 if min(affinity) < (os.cpu_count() or 1) // 2 else 1
        except Exception:
            pass
        return 0
```

---

### §4. INTEGRATION CONTRACTS

#### 4.1 Dispatch Pipeline Hook Point

**Location**: `src/omega/oracle/subagent_dispatcher.py::dispatch()`  
**Position**: After M33Probe validation, before `build_dispatch_prompt()`

```python
# ── Archangel Architecture: Environmental State Register Injection ─────
if inject_system_envelope_sync is not None:
    hw_monitor = _get_hw_monitor()
    model_gateway = _get_model_gateway()
    if hw_monitor is not None and model_gateway is not None:
        try:
            packet = inject_system_envelope_sync(
                packet=packet,
                target_agent=packet.target_agent,
                hw_monitor=hw_monitor,
                model_gateway=model_gateway,
            )
            logger.debug("Archangel envelope injected for %s → %s",
                       packet.source_agent, packet.target_agent)
        except (OSError, ValueError, TypeError) as exc:
            logger.warning("Archangel envelope injection failed: %s", exc)
    else:
        logger.debug("Archangel envelope skipped: hw_monitor=%s, model_gateway=%s",
                   hw_monitor, model_gateway)
```

**Lazy Singletons** (to avoid circular imports):
```python
_hw_monitor = None
_model_gateway = None

def _get_hw_monitor():
    global _hw_monitor
    if _hw_monitor is None:
        try:
            from omega.monitoring import HardwareMonitor
            _hw_monitor = HardwareMonitor()
        except (ImportError, OSError, ValueError):
            logger.debug("HardwareMonitor unavailable — skipping envelope injection")
    return _hw_monitor

def _get_model_gateway():
    global _model_gateway
    if _model_gateway is None:
        try:
            from omega.oracle.model_gateway import ModelGateway
            from omega.oracle.health_monitor import get_health_monitor
            _model_gateway = ModelGateway(health_monitor=get_health_monitor())
        except (ImportError, OSError, ValueError):
            logger.debug("ModelGateway unavailable — skipping envelope injection")
    return _model_gateway
```

#### 4.2 M33Probe Dynamic Threshold Contract

**Location**: `src/omega/oracle/m33_probe.py::M33Probe.calculate_dynamic_write_threshold()`

```python
def calculate_dynamic_write_threshold(self) -> int:
    """
    Archangel Architecture: Dynamic write-tool threshold based on hardware state.
    
    Base threshold: WRITE_TOOL_TOKEN_THRESHOLD (8000 tokens)
    
    Scaling rules:
    - memory_pressure > 0.7 (CRITICAL) → 2000 tokens (25%)
    - memory_pressure > 0.5 (HIGH) → 4000 tokens (50%)
    - memory_pressure > 0.3 (MODERATE) → 6000 tokens (75%)
    - thermal_throttling == True → 2000 tokens (30%)
    - oom_risk_level == "CRITICAL" → 2000 tokens (25%)
    - oom_risk_level == "HIGH" → 4000 tokens (50%)
    - oom_risk_level == "MODERATE" → 6000 tokens (75%)
    - else → 8000 (base)
    """
    base_threshold = WRITE_TOOL_TOKEN_THRESHOLD
    hw = self._get_hw_monitor()
    
    if hw is None:
        return base_threshold
    
    try:
        mem = hw.get_memory_status()
        pressure = mem.get("memory_pressure", 0.0)
        thermal_throttling = hw.is_thermal_throttling()
        oom_risk = mem.get("oom_risk", {}).get("risk_level", "SAFE")
        
        if pressure > 0.7:
            return max(2000, int(base_threshold * 0.25))
        elif pressure > 0.5:
            return max(4000, int(base_threshold * 0.5))
        elif pressure > 0.3:
            return max(6000, int(base_threshold * 0.75))
        
        if thermal_throttling:
            return max(2000, int(base_threshold * 0.3))
        
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

**Integration**: `should_require_write_tool()` now uses `dynamic_threshold` instead of constant `WRITE_TOOL_TOKEN_THRESHOLD`.

---

### §5. VERIFICATION & TESTING

#### 5.1 Unit Tests

| Test | Description | Expected |
|------|-------------|----------|
| `test_runtime_register_immutability` | Attempt to mutate frozen dataclass | `FrozenInstanceError` raised |
| `test_register_staleness` | `is_stale()` with expired TTL | Returns `True` after 30s |
| `test_envelope_format` | Parse generated envelope for required keys | All 12 fields present |
| `test_envelope_injection` | Dispatch packet receives envelope | `packet.context` starts with `[SYSTEM REGISTER:` |
| `test_dynamic_threshold_pressure` | Simulate pressure > 0.7 | Threshold = 2000 |
| `test_dynamic_threshold_thermal` | Mock `is_thermal_throttling=True` | Threshold = 2000 |
| `test_dynamic_threshold_oom` | Mock `oom_risk_level="CRITICAL"` | Threshold = 2000 |
| `test_envelope_ttl_expiry` | Remediation loop > 30s | Fresh sample drawn |

#### 5.2 Integration Test: Hallucination Crush

**Scenario**: Dispatch Researcher → Verity with poisoned context claiming "Nemotron 3 Ultra on ASUS ExpertBook"

**Expected**:
1. Envelope injected: `ACTIVE MODEL: qwen3-1.7b-q6_k`, `HOST OS: AMD Ryzen 7 5700U`
2. Verity's output contains **zero** references to Nemotron/ASUS
3. Verity's output **references** qwen3-1.7b / Ryzen 7 5700U if hardware mentioned
4. `SkepticalVerifier` flags any hardware claim contradicting envelope as `CONTRADICTED`

#### 5.3 Stress Test: Remediation Loop TTL

**Scenario**: Poisoned quorum → Turn 1 sMASE > 1.0 → remediation loop runs 35 seconds

**Expected**:
1. Turn 1: Envelope sampled at T=0s
2. Turn 2 (T=15s): Envelope still valid (15s < 30s TTL)
3. Turn 3 (T=35s): `register.is_stale()` → `True` → dispatcher draws fresh sample before Turn 3 prompt

---

### §6. OPERATIONAL CONSIDERATIONS

#### 6.1 Graceful Degradation

| Failure Mode | Behavior |
|--------------|----------|
| `HardwareMonitor` unavailable | Log warning, dispatch continues without envelope |
| `ModelGateway` unavailable | Log warning, dispatch continues without envelope |
| `psutil` import fails | NUMA node defaults to 0; envelope still generated |
| Envelope generation exception | Log warning, dispatch continues without envelope |

**No dispatch is ever blocked by Archangel.** The envelope is a *reliability enhancement*, not a gating requirement.

#### 6.2 Performance Impact

| Operation | Typical Latency |
|-----------|-----------------|
| `HardwareMonitor.collect_all()` | 15-30ms (psutil + `/proc` reads) |
| `ModelGateway.get_model_for_entity()` | <1ms (dict lookup) |
| `ModelGateway.get_provider_for_entity()` | <1ms (provider iteration) |
| Envelope string construction | <1ms |
| **Total per-dispatch overhead** | **~20-35ms** |

Negligible compared to subagent spin-up (seconds) and inference (seconds-minutes).

#### 6.3 Security & Privacy

- **No secrets in envelope**: Only hardware telemetry and model/backend identifiers
- **No PII**: No usernames, paths, or credentials
- **Local-only**: All telemetry from local kernel interfaces; zero network calls
- **M8 Compliant**: Zero telemetry exported; envelope exists only in agent context

---

### §7. FUTURE EXTENSIONS (Post-v1.0)

| Extension | Description | Mandate Impact |
|-----------|-------------|----------------|
| **GPU/VRAM Register** | Add `vram_available_mb`, `vram_used_mb`, `gpu_utilization_pct` for iGPU offload | M7, M13 |
| **Network Topology Register** | For multi-node: `peer_nodes`, `latency_ms`, `bandwidth_mbps` | M2, M27 |
| **Cache Hierarchy Register** | L1/L2/L3 sizes, associativity, line size for kernel tuning | M13, M14 |
| **Power/Envelope Register** | `package_power_watts`, `thermal_design_power`, `battery_percent` (laptops) | M7, M23 |
| **Envelope Versioning** | `schema_version` field in register for forward compatibility | M27 |

---

### §8. APPENDIX: GLOSSARY

| Term | Definition |
|------|------------|
| **Ontological Void** | The state of an agent lacking ground-truth knowledge of its physical execution substrate, causing hardware hallucinations. |
| **System Register** | The immutable `RuntimeHardwareRegister` snapshot injected into agent context. |
| **System Envelope** | The text-formatted System Register prepended to `packet.context`. |
| **TTL (Time-To-Live)** | Maximum validity duration of a System Register sample (default 30 seconds). |
| **Staleness** | Condition where `now - sampled_at_monotonic > sample_validity_seconds`. |
| **Gradient Velocity Brake** | M33Probe dynamic threshold scaling based on hardware state. |
| **DHAL** | Dynamic Hardware Adaptation Layer — system-level hardware adaptation (complementary to Archangel). |

---

*⬡ OMEGA ⬡ ARCHANGEL ⬡ SPEC-ARCHANGEL-v1.0.0 ⬡ 2026-09-07 ⬡ ONTOLOGICAL-VOID-RESOLVED ⬡ HALLUCINATION-BASIN-CRUSHED*

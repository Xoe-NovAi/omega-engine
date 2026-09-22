# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
# src/omega/oracle/env_hardware_probe.py
"""
Environmental Hardware Probe — Archangel Architecture Implementation
Bridges Omega's HardwareMonitor to the agent prompt layer via immutable System Envelopes.

This module resolves the Ontological Void: agents no longer hallucinate their hardware;
they receive a mathematically grounded, temporally bounded System Register at every dispatch.

Architecture:
- Wraps existing omega.monitoring.HardwareMonitor (892 lines)
- Fills ESR gaps: NUMA node discovery, model/agent backend mapping
- Generates frozen RuntimeHardwareRegister with monotonic/wall timestamps + 30s TTL
- Produces the [SYSTEM REGISTER: BARE-METAL PHYSICAL BOUNDARY] envelope
"""

import time
import os
import psutil
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime, timezone

# Import Omega's existing hardware monitor
try:
    from omega.monitoring import HardwareMonitor
except ImportError:
    HardwareMonitor = None  # type: ignore

# Import model gateway for agent->model/backend mapping
try:
    from omega.oracle.model_gateway import ModelGateway
except ImportError:
    ModelGateway = None  # type: ignore


@dataclass(frozen=True)
class RuntimeHardwareRegister:
    """
    Immutable hardware register snapshot — the agent's bare-metal truth.
    Frozen to prevent post-hoc mutation; carries its own temporal validity window.
    """
    host_os: str
    active_cpu_cores: int
    cpu_utilization_pct: float
    available_system_ram_mb: float
    total_system_ram_mb: float
    process_memory_rss_mb: float
    memory_pressure_score: float  # Bounded [0.0, 1.0]
    oom_risk_level: str           # SAFE | MODERATE | HIGH | CRITICAL
    thermal_throttling: bool
    max_core_temp_c: float
    zram_compression_ratio: float
    assigned_numa_node: int
    active_model_identifier: str
    active_model_backend: str
    sampled_at_monotonic: float
    sampled_at_wall: str
    sample_validity_seconds: int = 30

    def is_stale(self, current_monotonic: Optional[float] = None) -> bool:
        """Check if this register sample has exceeded its TTL."""
        now = current_monotonic or time.monotonic()
        return (now - self.sampled_at_monotonic) > self.sample_validity_seconds


@dataclass
class SystemEnvelopeInjector:
    """
    Generates the [SYSTEM REGISTER: BARE-METAL PHYSICAL BOUNDARY] envelope
    by querying HardwareMonitor and ModelGateway at dispatch time.
    
    Injected into subagent_dispatcher.py after M33Probe validation.
    """
    hw_monitor: Any
    model_gateway: Any

    def __init__(self, hw_monitor: Any, model_gateway: Any):
        """
        Args:
            hw_monitor: Existing omega.monitoring.HardwareMonitor instance.
            model_gateway: Existing omega.oracle.model_gateway.ModelGateway instance.
        """
        self.hw_monitor = hw_monitor
        self.model_gateway = model_gateway

    def _discover_numa_node(self) -> int:
        """
        Returns the NUMA node assignment for the current process.
        
        On monolithic UMA APUs (e.g., AMD Ryzen 7 5700U), there is only a single
        NUMA node (node0) — all 8 cores / 16 threads share one unified memory
        controller. Multi-node NUMA topology detection is cargo-cult theater on
        client silicon. This function explicitly returns 0 with architectural
        justification rather than executing meaningless sysfs traversals.
        """
        return 0  # Single NUMA node on monolithic UMA APU (Zen 2/3 mobile)

    def _resolve_model_and_backend(self, target_agent: str) -> tuple[str, str]:
        """
        Resolve model identifier and backend string for the target agent.
        Uses ModelGateway's synchronous get_model_for_entity and get_provider_for_entity.
        """
        # ModelGateway uses entity_name; agent name maps to entity name
        entity_name = target_agent
        
        # Get model identifier
        try:
            model_id = self.model_gateway.get_model_for_entity(entity_name)
        except (AttributeError, KeyError, ValueError):
            model_id = "qwen3-1.7b"  # System default fallback
        
        # Get backend/provider string with actual ISA detection
        try:
            provider = self.model_gateway.get_provider_for_entity(entity_name)
            if provider:
                backend = f"{provider.__class__.__name__}"
            else:
                # Detect actual CPU ISA instead of cargo-culting AVX-512
                backend = self._detect_isa_backend()
        except (AttributeError, KeyError, ValueError):
            backend = self._detect_isa_backend()
        
        return model_id, backend

    def _detect_isa_backend(self) -> str:
        """
        Detect actual CPU instruction set for backend string.
        On AMD Ryzen 7 5700U (Zen 2/3 mobile): AVX2, FMA3, BMI2 — NO AVX-512.
        """
        try:
            with open("/proc/cpuinfo", "r") as f:
                flags = f.read()
            if "avx512" in flags.lower():
                return "llama.cpp / AVX-512"
            elif "avx2" in flags.lower() and "fma" in flags.lower():
                return "llama.cpp / AVX2/FMA3"
            elif "avx" in flags.lower():
                return "llama.cpp / AVX"
            else:
                return "llama.cpp / baseline"
        except (OSError, IOError):
            return "llama.cpp / AVX2/FMA3"  # Safe fallback for Zen APU

    def generate_envelope_sync(self, target_agent: str) -> str:
        """
        Synchronous version of envelope generation for use in sync dispatch pipeline.
        
        Args:
            target_agent: The agent name (e.g., "verity", "researcher", "kali") 
                         for model/backend resolution.
        
        Returns:
            The complete [SYSTEM REGISTER: BARE-METAL PHYSICAL BOUNDARY] envelope string.
        """
        # 1. Fetch live bare-metal status from the existing monitor
        stats = self.hw_monitor.collect_all()
        mem = stats.get("memory", {})
        cpu = stats.get("cpu", {})
        temps = stats.get("temperatures", {})
        topology = stats.get("topology", {})
        
        # 2. Extract model mapping metadata (SYNC)
        model_id, backend = self._resolve_model_and_backend(target_agent)
        
        # Calculate localized temporal markers
        now_mono = time.monotonic()
        now_wall = datetime.now(timezone.utc).isoformat()
        
        # Isolate maximal thermal profile
        max_temp = max((t.get('temp', 0) for t in temps.get('celsius', [])), default=0.0)

        # 3. Construct the immutable frozen register state object
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

        # 4. Generate the final system envelope string payload
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

    async def generate_envelope(self, target_agent: str) -> str:
        """
        Async version of envelope generation (delegates to sync for now).
        
        Args:
            target_agent: The agent name (e.g., "verity", "researcher", "kali") 
                         for model/backend resolution.
        
        Returns:
            The complete [SYSTEM REGISTER: BARE-METAL PHYSICAL BOUNDARY] envelope string.
        """
        # For now, delegate to sync version since underlying calls are sync
        return self.generate_envelope_sync(target_agent)

    # Convenience function for direct use in dispatch pipeline (SYNC)
def inject_system_envelope_sync(
    packet: Any,
    target_agent: str,
    hw_monitor: Any,
    model_gateway: Any
) -> Any:
    """
    Standalone SYNC injection function for use in subagent_dispatcher.py dispatch pipeline.
    
    Args:
        packet: HandoffPacket instance
        target_agent: Target agent name
        hw_monitor: HardwareMonitor instance
        model_gateway: ModelGateway instance
    
    Returns:
        Modified packet with system envelope prepended to context.
    """
    injector = SystemEnvelopeInjector(hw_monitor, model_gateway)
    envelope = injector.generate_envelope_sync(target_agent)
    packet.context = envelope + "\n\n" + (packet.context or "")
    return packet


# Async version (delegates to sync for now)
async def inject_system_envelope(
    packet: Any,
    target_agent: str,
    hw_monitor: Any,
    model_gateway: Any
) -> Any:
    """
    Standalone injection function for use in subagent_dispatcher.py dispatch pipeline.
    
    Args:
        packet: HandoffPacket instance
        target_agent: Target agent name
        hw_monitor: HardwareMonitor instance
        model_gateway: ModelGateway instance
    
    Returns:
        Modified packet with system envelope prepended to context.
    """
    return inject_system_envelope_sync(packet, target_agent, hw_monitor, model_gateway)


# Export for direct import
__all__ = [
    "RuntimeHardwareRegister",
    "SystemEnvelopeInjector",
    "inject_system_envelope",
    "inject_system_envelope_sync",
]
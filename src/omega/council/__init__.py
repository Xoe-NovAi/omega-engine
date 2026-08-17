# 🔱 Omega Engine — Council Module
# ⬡ OMEGA ⬡ KALI ⬡ trc_council ⬡ SCAFFOLD
#
# MaKaLi Parallel Council — Unified MultiAgentCoordinator
# Stages: Nodes (Phase 1) → Digestion (Phase 1.5) → Oversouls (Phase 2) → Kali Synthesis (Phase 3) → Research (Phase 4)
# Status: SCAFFOLD — Implementation in progress (T0 Sessions 1-5)

from .coordinator import MultiAgentCoordinator
from .models import (
    NodeReport,
    DigestedReport,
    Conflict,
    CouncilConfig,
    HardwareProfile,
    ExecutionMode,
    StageResult,
    CouncilResult,
)
from .report_digestion import ReportDigester
from .hardware_detector import detect_hardware_profile
from .execution_mode import select_execution_mode
from .failure_layer import (
    CouncilFailure,
    CoordinatedRecovery,
    RetryPolicy,
    FallbackChain,
    CircuitBreakerState,
)

__all__ = [
    "MultiAgentCoordinator",
    "NodeReport",
    "DigestedReport",
    "Conflict",
    "CouncilConfig",
    "HardwareProfile",
    "ExecutionMode",
    "StageResult",
    "CouncilResult",
    "ReportDigester",
    "detect_hardware_profile",
    "select_execution_mode",
    "CouncilFailure",
    "CoordinatedRecovery",
    "RetryPolicy",
    "FallbackChain",
    "CircuitBreakerState",
]

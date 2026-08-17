# 🔱 Omega Engine — Council Data Models
# ⬡ OMEGA ⬡ KALI ⬡ trc_council ⬡ SCAFFOLD
#
# Data models for the MaKaLi Parallel Council architecture.
# T0 Session 1: Core types + state machine + contracts.

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional


# --- Enums ---


class HardwareProfile(Enum):
    """Auto-detected or manually specified hardware constraint profile."""

    CLOUD_EQUIVALENT = "cloud_equivalent"  # 32GB+ RAM, GPU available
    LOCAL_16GB = "local_16gb"  # Default: 4B/8B/12B tiers
    LOCAL_8GB = "local_8gb"  # 2B/4B/8B tiers
    LOCAL_4GB = "local_4gb"  # Cloud-only or 1B/2B/4B


class ExecutionMode(Enum):
    """Node execution concurrency mode based on hardware profile."""

    PARALLEL = auto()  # All nodes simultaneously (cloud)
    SERIAL_INDEPENDENT = auto()  # One at a time, no context passing (constrained)
    BATCH_2 = auto()  # 2 at a time (for 8GB RAM)
    BATCH_4 = auto()  # 4 at a time (for 16GB RAM)


class CouncilStage(Enum):
    """Stages of a council execution lifecycle."""

    IDLE = auto()
    PHASE1_NODES = auto()
    PHASE1_5_DIGESTION = auto()
    PHASE2_OVERSOULS = auto()
    PHASE3_KALI_SYNTHESIS = auto()
    PHASE4_RESEARCH = auto()
    COMPLETED = auto()
    FAILED = auto()
    RECOVERING = auto()


class CircuitBreakerState(Enum):
    """Quality-aware circuit breaker states."""

    CLOSED = auto()  # Normal operation
    OPEN = auto()  # Too many failures — stop dispatching
    HALF_OPEN = auto()  # Testing if service recovered
    PERMANENTLY_OPEN = auto()  # Manual intervention required


# --- Core Data Models ---


@dataclass
class NodeReport:
    """A single node's independent output."""

    node_id: str  # "N1" through "N10"
    domain: str  # "Infrastructure", "Engineering", etc.
    content: str  # Full report markdown
    file_path: Path  # Path to the written report file
    execution_time_ms: int = 0
    model_used: str = ""
    confidence_score: float = 0.0
    error: Optional[str] = None


@dataclass
class Conflict:
    """A detected contradiction between node reports."""

    concept: str  # What is being disagreed about
    values: Dict[str, str]  # node_id -> claim/value
    severity: str = "INFO"  # "INFO" | "WARNING" | "CRITICAL"
    description: str = ""


@dataclass
class DigestedReport:
    """Zero-inference-cost optimized report for oversoul consumption."""

    side: str  # "BUILD" or "RUN"
    nodes: List[NodeReport]
    executive_summary: str
    node_summaries: Dict[str, str]
    cross_reference_index: Dict[str, List[str]]
    conflict_map: List[Conflict]
    mandate_compliance: Dict[str, Dict[str, str]]
    token_budget_allocation: Dict[str, int]


@dataclass
class StageResult:
    """Result of a single council stage execution."""

    stage: CouncilStage
    success: bool
    artifacts: Dict[str, Path] = field(default_factory=dict)
    duration_ms: int = 0
    error: Optional[str] = None
    recovered: bool = False


@dataclass
class CouncilResult:
    """Complete output of a council execution."""

    session_id: str
    topic: str
    stages: Dict[CouncilStage, StageResult] = field(default_factory=dict)
    final_synthesis_path: Optional[Path] = None
    research_gaps_path: Optional[Path] = None
    total_duration_ms: int = 0
    success: bool = False
    error: Optional[str] = None


# --- Council Configuration ---


@dataclass
class RetryPolicy:
    """Retry configuration for stage execution."""

    max_retries: int = 3
    base_delay_ms: int = 1000
    max_delay_ms: int = 30000
    jitter_factor: float = 0.1


@dataclass
class FallbackChain:
    """Fallback configuration — what to do when a stage fails."""

    degrade_to_simpler: bool = True  # e.g. digestion fails → raw concat
    use_cloud_fallback: bool = True  # local fails → try cloud
    abort_on_mandate_violation: bool = True  # M2/M7 breach → hard stop


@dataclass
class CouncilConfig:
    """Complete configuration for a council execution."""

    # Hardware
    hardware_profile: HardwareProfile = HardwareProfile.LOCAL_16GB
    total_ram_gb: int = 16
    cpu_cores: int = 8

    # Model tiers
    nodes_model: str = "gemma-4b-local"
    oversouls_model: str = "nemotron-8b-cloud"
    kali_model: str = "nemotron-12b-cloud"
    research_model: str = "auto"

    # Execution
    phase1_execution_mode: ExecutionMode = ExecutionMode.BATCH_4
    enable_digestion: bool = True
    enable_research: bool = True

    # Resilience
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    fallback_chain: FallbackChain = field(default_factory=FallbackChain)

    # Output
    output_dir: str = "data/council/{session_id}"
    preserve_all_artifacts: bool = True

    # Mandate enforcement
    mandate_policies: Dict[str, bool] = field(
        default_factory=lambda: {
            "M1": True,  # AnyIO — enforce
            "M2": True,  # Firewall — enforce
            "M7": True,  # Local-first — enforce
            "M13": True,  # Temple-Grade — enforce
            "M23": True,  # Failure integrity — enforce
        }
    )

"""
Model Registry Data Classes
⬡ OMEGA ⬡ KALI ⬡ MODEL-REGISTRY ⬡ 2026-07-19
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Platform(str, Enum):
    CLOUD = "cloud"
    LOCAL = "local"
    CLI = "cli"
    STEALTH = "stealth"


class Tier(str, Enum):
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"


class Status(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"
    STEALTH = "stealth"


@dataclass
class ModelArchitecture:
    """Model architecture parameters (total/active params, MoE config, quantization)."""
    total: str = "Unknown"
    active: str = "Unknown"
    architecture: str = "unknown"  # dense, MoE, hybrid, router
    experts: int = 0
    active_experts: int = 0
    shared_experts: int = 0
    quantization: str = "Unknown"
    training_tokens: str = "Unknown"
    source: str = "estimated"  # official, estimated, community
    verified: bool = False
    verified_date: Optional[str] = None


@dataclass
class Parameters:
    """Model sampling/generation parameters."""
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 40
    repetition_penalty: float = 1.1
    max_tokens: int = 4096
    stop_sequences: list[str] = field(default_factory=list)
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    logit_bias: Optional[dict[int, float]] = None
    seed: Optional[int] = None
    model_specific_overrides: dict = field(default_factory=dict)


@dataclass
class ModelArchitecture:
    """Model architecture parameters (total/active params, MoE config, quantization)."""
    total: str = "Unknown"
    active: str = "Unknown"
    architecture: str = "unknown"
    experts: int = 0
    active_experts: int = 0
    shared_experts: int = 0
    quantization: str = "Unknown"
    training_tokens: str = "Unknown"
    source: str = "estimated"
    verified: bool = False
    verified_date: Optional[str] = None


@dataclass
class BenchmarkSources:
    """Benchmark citations for capability scores."""
    reasoning: str = ""
    code_generation: str = ""
    knowledge: str = ""
    creative: str = ""
    tool_use: str = ""
    structured_output: str = ""
    multimodal: str = ""
    overall: str = ""


@dataclass
class Capabilities:
    reasoning: float = 0.0
    code_generation: float = 0.0
    knowledge: float = 0.0
    creative: float = 0.0
    tool_use: bool = False
    structured_output: bool = False
    multimodal: bool = False
    # Extended capability fields (P1)
    code_execution: bool = False
    parallel_search: bool = False
    workspace_integration: bool = False


@dataclass
class Pricing:
    input_per_mtok: float = 0.0
    output_per_mtok: float = 0.0
    cached_input_per_mtok: float = 0.0
    batch_discount: float = 0.0
    intro_pricing: Optional[dict] = None
    free_tier: bool = False
    cost_per_1k_tokens_usd: float = 0.0


@dataclass
class Routing:
    engine_routable: bool = True
    opencode_cli_only: bool = False
    recommended_engine_alternative: Optional[str] = None


@dataclass
class IdentityHistory:
    original: str
    current: str
    swap_detected: bool
    last_verified: str


@dataclass
class CommunityIntelligence:
    rating: str
    notes: list[str] = field(default_factory=list)


@dataclass
class LiveAPIState:
    source: str
    last_verified: str
    last_verified_free: Optional[str] = None


@dataclass
class ResearchProfile:
    reasoning_depth: str = "iterative"
    tool_fidelity: str = "medium"
    failure_signature: str = "shallow"
    shadow_focus: str = "force_deepening"
    guardrails: list[str] = field(default_factory=list)


@dataclass
class TestRun:
    test_id: str
    role: str
    output_files: int = 0
    total_lines: int = 0
    p0_bugs_found: int = 0
    p1_bugs_found: int = 0
    p2_bugs_found: int = 0
    memory_contamination: bool = False
    contamination_details: str = ""
    hit_usage_limit: bool = False
    cognitive_mode: str = ""
    quality_score: str = ""
    convergence_load_bearing: str = ""
    asymmetric_catches: list[str] = field(default_factory=list)
    divergence: int = 0
    time_seconds: int = 0


@dataclass
class Synergy:
    pattern: str
    partners: list[str] = field(default_factory=list)
    confidence: float = 0.0
    use_case: str = ""


@dataclass
class EmpiricalEvidence:
    test_runs: list[TestRun] = field(default_factory=list)
    synergies: list[Synergy] = field(default_factory=list)


@dataclass
class ProviderFabric:
    available_via: list[dict] = field(default_factory=list)
    local_first_priority: Optional[int] = None


@dataclass
class BenchmarkSources:
    """Source URLs for capability scores."""
    reasoning: str = ""
    code_generation: str = ""
    knowledge: str = ""
    creative: str = ""
    tool_use: str = ""
    structured_output: str = ""
    multimodal: str = ""
    overall: str = ""


@dataclass
class ModelCard:
    # Core Identity
    model_id: str
    display_name: str
    version: str
    provider: str
    platform: Platform
    tier: Tier
    status: Status

    # Capabilities
    context_window: int
    max_output_tokens: int = 0
    capabilities: Capabilities = field(default_factory=Capabilities)

    # Economics
    pricing: Pricing = field(default_factory=Pricing)
    latency_p99_ms: int = 0
    uptime_percent: float = 0.0

    # Sampling Parameters (NEW — T1)
    parameters: Parameters = field(default_factory=Parameters)

    # Model Architecture (NEW — P1)
    architecture: ModelArchitecture = field(default_factory=ModelArchitecture)

    # Routing
    routing: Routing = field(default_factory=Routing)

    # Identity (for stealth models)
    identity_history: Optional[IdentityHistory] = None

    # Community Intelligence
    community_intelligence: Optional[CommunityIntelligence] = None

    # Live API State
    live_api_state: Optional[LiveAPIState] = None

    # Research Profile
    research_profile: ResearchProfile = field(default_factory=ResearchProfile)

    # Empirical Evidence
    empirical_evidence: EmpiricalEvidence = field(default_factory=EmpiricalEvidence)

    # Provider Fabric
    provider_fabric: ProviderFabric = field(default_factory=ProviderFabric)

    # Benchmark Sources (NEW — P1)
    benchmark_sources: BenchmarkSources = field(default_factory=BenchmarkSources)

    # Metadata
    tags: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    schema_version: str = "1.2.0"
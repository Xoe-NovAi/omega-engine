# AP: AP-INGESTION-TYPES-v1.0.0
"""
Sovereign Ingestion Types — Shared schemas for entity deepening.
"""

# DocRef: docs/architecture/SOVEREIGN_DATA_FLOW.md
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class CircuitBreakerState(Enum):
    """States for the Ingestion Circuit Breaker."""

    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Halted due to failures
    HALF_OPEN = "HALF_OPEN"  # Testing for recovery


class IngestionError(Exception):
    """Base class for all ingestion-related errors."""

    def __init__(self, message: str, trace_id: Optional[str] = None):
        super().__init__(message)
        self.trace_id = trace_id


class SovereigntyError(IngestionError):
    """Errors related to API keys, quota, or authentication (e.g., 403)."""

    pass


class TransportError(IngestionError):
    """Errors related to network connectivity or timeouts."""

    pass


class ProviderServerError(IngestionError):
    """Errors related to internal provider failures (e.g., 500)."""

    pass


class SchemaError(IngestionError):
    """Errors related to malformed or invalid JSON output."""

    pass


class BudgetExceededError(IngestionError):
    """Errors when the token or USD budget is breached."""

    pass


class SentryFailure(IngestionError):
    """Errors when the pre-flight canary probe fails."""

    pass


class ExtractionSchema(BaseModel):
    """The standard 5-dimension extraction schema for entity deepening."""

    technical_facts: List[str] = Field(default_factory=list)
    personality_patterns: List[str] = Field(default_factory=list)
    gnosis_principles: List[Dict[str, str]] = Field(default_factory=list)
    heritage_patterns: List[str] = Field(default_factory=list)
    dpo_pairs: List[Dict[str, str]] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


@dataclass
class IngestionResult:
    """The result of a single source extraction."""

    source_name: str
    model_name: str
    extraction: ExtractionSchema
    latency_s: float
    input_chars: int
    trace_id: str
    quality_score: float
    domain: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class IngestionConfig:
    """Configuration for an ingestion run."""

    entity_name: str
    model_name: str
    api_key: str
    sources: List[Path]
    temperature: float = 0.6
    max_tokens: int = 8192
    use_streaming: bool = True
    max_budget_usd: float = 10.0  # Default hard budget
    fallback_model: Optional[str] = None

"""
Sovereign Ingestion Types — Shared schemas for entity deepening.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime

@dataclass
class ExtractionSchema:
    """The standard 5-dimension extraction schema for entity deepening."""
    technical_facts: List[str] = field(default_factory=list)
    personality_patterns: List[str] = field(default_factory=list)
    gnosis_principles: List[Dict[str, str]] = field(default_factory=list)
    heritage_patterns: List[str] = field(default_factory=list)
    dpo_pairs: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "technical_facts": self.technical_facts,
            "personality_patterns": self.personality_patterns,
            "gnosis_principles": self.gnosis_principles,
            "heritage_patterns": self.heritage_patterns,
            "dpo_pairs": self.dpo_pairs,
        }

@dataclass
class IngestionResult:
    """The result of a single source extraction."""
    source_name: str
    model_name: str
    extraction: ExtractionSchema
    latency_s: float
    input_chars: int
    trace_id: str
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

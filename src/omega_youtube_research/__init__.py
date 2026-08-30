# 🔱 Omega Engine — YouTube Research Enhanced (V2)
# AP: AP-YOUTUBE-RESEARCH-V2-v1.0.0
# ⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_youtube_v2 ⬡ ENHANCED

"""Enhanced YouTube Research Module — Temporal Knowledge Observatory.

This package implements the 9-layer sovereign YouTube research architecture:
- L1: Hybrid Extraction (API → Whisper → Firecrawl)
- L2: Anti-Bot Infrastructure (Sticky Proxy + Adaptive Rate Limiting)
- L3: Temporal RAG Synthesis (Semantic Chunking + Hybrid Search)
- L4: CAS Deduplication (Content-Addressable Chunk Store)
- L5: Relational Gnosis Graph (Cross-Modal Knowledge Topology)
- L6: Faithfulness Audit (S2 Eval Integration)
- L7: Freshness & Drift Detection (Decay Functions)
- L8: Oracle Steering Queue (Human-in-the-Loop)
- L9: Somatic Checkpoints (Crash Resilience)

All components are WAD-isolated (M2 Firewall) and mandate-compliant.
"""

from __future__ import annotations

__version__ = "2.0.0"
__all__ = [
    # L1/L9: Hybrid Extraction + Somatic Checkpoints
    "Transcriber",
    "CheckpointingTranscriber",
    "TranscriptFidelity",
    # L2: Anti-Bot Infrastructure
    "YouTubeIdentity",
    "AdaptiveRateLimiter",
    # L3: Temporal RAG
    "TemporalChunk",
    "semantic_chunk",
    "hybrid_search",
    # L4: CAS Deduplication
    "CASArchiver",
    "CASConfig",
    "CASRecord",
    # L5: Gnosis Graph
    "GnosisEdge",
    "GnosisEdgeType",
    "GnosisEpisode",
    "emit_gnosis_edges",
    "find_paper",
    "find_contradiction",
    "match_entity",
    # L6: Faithfulness Audit
    "CalibratedJudge",
    "FaithfulnessResult",
    "verify_provenance",
    # L7: Freshness & Drift
    "freshness_score",
    "calculate_weighted_relevance",
    "infer_memory_type",
    "MemoryType",
    "detect_drift",
    "check_retrievability",
    "DriftSignal",
    "RetrievabilityCheck",
    # L8: Oracle Steering
    "ResearchTask",
    "SteeringTaskType",
    "TaskPriority",
    "TaskStatus",
    "BackgroundResearcherQueue",
    "OracleSteeringQueue",
    "inject_steering",
    # L9: Somatic Checkpoints (in transcriber)
    # Config
    "YouTubeResearchConfig",
    "SieveConfig",
    "SignerConfig",
    "PersistenceConfig",
    "EmbeddingConfig",
    # Module
    "YouTubeResearchModule",
    "IngestResult",
    # Errors
    "YouTubeResearchError",
]

# Lazy imports to avoid circular dependencies
def __getattr__(name: str):
    if name in ("Transcriber", "CheckpointingTranscriber", "TranscriptFidelity"):
        from .transcriber import Transcriber, CheckpointingTranscriber, TranscriptFidelity
        return globals()[name]
    if name in ("YouTubeIdentity", "AdaptiveRateLimiter"):
        from .proxy_identity import YouTubeIdentity, AdaptiveRateLimiter
        return globals()[name]
    if name in ("TemporalChunk", "semantic_chunk", "hybrid_search"):
        from .chunker import TemporalChunk, semantic_chunk, hybrid_search
        return globals()[name]
    if name in ("CASArchiver", "CASConfig", "CASRecord"):
        from .cas_archiver import CASArchiver, CASConfig, CASRecord
        return globals()[name]
    if name in ("GnosisEdge", "GnosisEdgeType", "GnosisEpisode", "emit_gnosis_edges", 
                "find_paper", "find_contradiction", "match_entity"):
        from .gnosis_bridge import (
            GnosisEdge, GnosisEdgeType, GnosisEpisode, emit_gnosis_edges,
            find_paper, find_contradiction, match_entity
        )
        return globals()[name]
    if name in ("CalibratedJudge", "FaithfulnessResult", "verify_provenance"):
        from .faithfulness import CalibratedJudge, FaithfulnessResult, verify_provenance
        return globals()[name]
    if name in ("freshness_score", "calculate_weighted_relevance", "infer_memory_type",
                "MemoryType", "detect_drift", "check_retrievability", 
                "DriftSignal", "RetrievabilityCheck"):
        from .freshness import (
            freshness_score, calculate_weighted_relevance, infer_memory_type,
            MemoryType, detect_drift, check_retrievability,
            DriftSignal, RetrievabilityCheck
        )
        return globals()[name]
    if name in ("ResearchTask", "SteeringTaskType", "TaskPriority", "TaskStatus",
                "BackgroundResearcherQueue", "OracleSteeringQueue", "inject_steering"):
        from .steering import (
            ResearchTask, SteeringTaskType, TaskPriority, TaskStatus,
            BackgroundResearcherQueue, OracleSteeringQueue, inject_steering
        )
        return globals()[name]
    if name in ("YouTubeResearchConfig", "SieveConfig", "SignerConfig", 
                "PersistenceConfig", "EmbeddingConfig"):
        from .config import (
            YouTubeResearchConfig, SieveConfig, SignerConfig,
            PersistenceConfig, EmbeddingConfig
        )
        return globals()[name]
    if name in ("YouTubeResearchModule", "IngestResult"):
        from .module import YouTubeResearchModule, IngestResult
        return globals()[name]
    if name == "YouTubeResearchError":
        from .errors import YouTubeResearchError
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
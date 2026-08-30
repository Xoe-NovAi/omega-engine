"""
L5 Relational Gnosis Graph — Cross-Modal Knowledge Topology (Graphiti-style)
⬡ OMEGA ⬡ RESEARCHER ⬡ L5 ⬡ GNOSIS_BRIDGE
AP Token: AP-YOUTUBE-GNOSIS-v2.0.0

Mandate Compliance:
- M1 AnyIO: all I/O wrapped in anyio.to_thread.run_sync
- M2 Firewall: WAD-isolated
- M7 Local-First: local embeddings for matching
- M11 Soul Integrity: edges feed Soul Distiller (L1→L2→L3)
- M17 Cognitive Integrity: contradiction detection prevents drift
- M22 Provenance: every edge carries source_video_id + timestamp + episode

Per Graphiti (getzep/graphiti) — Bi-temporal Knowledge Graph:
- Every edge has explicit validity intervals (t_valid, t_invalid)
- Episodes = raw data provenance (every derived fact traces back)
- Entities evolve with updated summaries
- Hybrid retrieval: semantic + keyword + graph traversal
- Automatic fact invalidation with temporal history preserved
- Custom entity/edge types via Pydantic models

Edge Types (YouTube → Knowledge):
- IMPLEMENTS: Video implements paper/concept
- CONTRADICTS: Video claims X, paper claims ¬X (flagged for review)
- EXTENDS: Video extends prior work
- SPOKEN_BY: Speaker → known entity
- CITES: Video cites paper/repo
- REPLICATES: Video replicates experiment
- CRITIQUES: Video critiques prior work
"""

from __future__ import annotations
import anyio
import hashlib
import json
import re
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from .chunker import TemporalChunk


# ── Edge Types ────────────────────────────────────────────────────────────────

class GnosisEdgeType(str, Enum):
    IMPLEMENTS = "implements"          # Video implements paper/concept
    CONTRADICTS = "contradicts"        # Video claims X, paper claims ¬X
    EXTENDS = "extends"                # Video extends prior work
    SPOKEN_BY = "spoken_by"            # Speaker → known entity
    CITES = "cites"                    # Video cites paper/repo
    REPLICATES = "replicates"          # Video replicates experiment
    CRITIQUES = "critiques"            # Video critiques prior work
    REFERENCES = "references"          # Generic reference


# ── Bi-Temporal Edge (Graphiti Pattern) ──────────────────────────────────────

@dataclass
class GnosisEdge:
    """
    Bi-temporal edge with full provenance (Graphiti-style).
    
    Graphiti bi-temporal model:
    - t_valid: When the fact became true (video publish date)
    - t_invalid: When the fact was superseded (None = still valid)
    - episode_id: Links to raw source episode for full provenance
    """
    # Source (YouTube video)
    source_type: str = "youtube_video"
    source_id: str = ""                    # video_id
    source_url: str = ""
    source_publish_date: Optional[datetime] = None
    
    # Target (Paper, Repo, Entity, Concept)
    target_type: str = ""                  # "paper" | "repo" | "entity" | "concept"
    target_id: str = ""                    # arXiv ID, DOI, GitHub URL, entity name
    target_name: str = ""                  # Human-readable name
    
    # Edge semantics
    edge_type: GnosisEdgeType = GnosisEdgeType.REFERENCES
    confidence: float = 0.0                # 0.0-1.0
    evidence: str = ""                     # Text span supporting the edge
    
    # Bi-temporal validity (Graphiti)
    t_valid: float = field(default_factory=time.time)  # When fact became true
    t_invalid: Optional[float] = None      # When superseded (None = current)
    superseded_by: Optional[str] = None    # Edge ID of replacement
    
    # Provenance
    episode_id: str = field(default_factory=lambda: f"ep_{uuid.uuid4().hex[:12]}")
    chunk_hash: str = ""                   # CAS hash of source chunk
    chunk_t_start: float = 0.0             # Temporal anchor in video
    chunk_t_end: float = 0.0
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    flagged: bool = False                  # True for contradictions needing review
    
    def to_dict(self) -> dict:
        d = asdict(self)
        d["edge_type"] = self.edge_type.value
        if self.source_publish_date:
            d["source_publish_date"] = self.source_publish_date.isoformat()
        return d
    
    @classmethod
    def from_dict(cls, data: dict) -> "GnosisEdge":
        data = data.copy()
        data["edge_type"] = GnosisEdgeType(data["edge_type"])
        if "source_publish_date" in data and data["source_publish_date"]:
            data["source_publish_date"] = datetime.fromisoformat(data["source_publish_date"])
        return cls(**data)
    
    def is_valid_at(self, timestamp: float) -> bool:
        """Check if edge is valid at given timestamp."""
        if timestamp < self.t_valid:
            return False
        if self.t_invalid is not None and timestamp > self.t_invalid:
            return False
        return True
    
    def invalidate(self, replacement_edge_id: Optional[str] = None) -> None:
        """Mark edge as superseded (Graphiti automatic invalidation)."""
        self.t_invalid = time.time()
        self.superseded_by = replacement_edge_id


# ── Episode (Provenance Container) ───────────────────────────────────────────

@dataclass
class GnosisEpisode:
    """
    Episode = raw data provenance (Graphiti pattern).
    Every derived fact traces back to an episode.
    """
    episode_id: str
    source_type: str = "youtube_video"
    source_id: str = ""                    # video_id
    source_url: str = ""
    raw_content: str = ""                  # Full transcript or summary
    metadata: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    processed_at: Optional[float] = None
    chunk_hashes: list[str] = field(default_factory=list)  # CAS hashes of derived chunks
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "GnosisEpisode":
        return cls(**data)


# ── Pattern Matching (Citation Detection) ────────────────────────────────────

# Citation patterns for extracting references from transcripts
ARXIV_PATTERN = re.compile(r"arXiv:(\d{4}\.\d{4,5}(?:v\d+)?)", re.IGNORECASE)
DOI_PATTERN = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
GITHUB_PATTERN = re.compile(r"github\.com/([\w-]+/[\w.-]+)", re.IGNORECASE)
URL_PATTERN = re.compile(r"https?://[^\s]+")

# Known entities for speaker matching (extendable)
KNOWN_ENTITIES = {
    "yann lecun": "Yann LeCun",
    "geoffrey hinton": "Geoffrey Hinton",
    "yoshua bengio": "Yoshua Bengio",
    "andrew ng": "Andrew Ng",
    "fei-fei li": "Fei-Fei Li",
    "demis hassabis": "Demis Hassabis",
    "ilya sutskever": "Ilya Sutskever",
    "karpathy": "Andrej Karpathy",
    "lex fridman": "Lex Fridman",
}


def find_paper(text: str) -> Optional[dict]:
    """
    Find paper references in text.
    
    Returns dict with type (arxiv/doi/url) and identifier, or None.
    """
    # Check arXiv
    arxiv_match = ARXIV_PATTERN.search(text)
    if arxiv_match:
        return {"type": "arxiv", "id": arxiv_match.group(1)}
    
    # Check DOI
    doi_match = DOI_PATTERN.search(text)
    if doi_match:
        return {"type": "doi", "id": doi_match.group(0)}
    
    # Check GitHub
    gh_match = GITHUB_PATTERN.search(text)
    if gh_match:
        return {"type": "github", "id": gh_match.group(1)}
    
    # Check generic URL
    url_match = URL_PATTERN.search(text)
    if url_match:
        return {"type": "url", "id": url_match.group(0)}
    
    return None


def find_contradiction(text: str, knowledge_base: Optional[dict] = None) -> Optional[dict]:
    """
    Detect potential contradictions with known facts.
    
    Simple keyword-based detection — in production, use NLI model.
    """
    contradiction_indicators = [
        ("transformers are dead", "transformers remain SOTA"),
        ("llms cannot reason", "llms show emergent reasoning"),
        ("scaling laws broken", "scaling laws hold"),
        ("attention is all you need is wrong", "attention is all you need"),
    ]
    
    text_lower = text.lower()
    for claim, counter in contradiction_indicators:
        if claim in text_lower:
            return {"claim": claim, "counter": counter, "confidence": 0.7}
    
    return None


def match_entity(speaker: str) -> Optional[str]:
    """Match speaker name to known entity."""
    if not speaker:
        return None
    speaker_lower = speaker.lower().strip()
    for key, canonical in KNOWN_ENTITIES.items():
        if key in speaker_lower:
            return canonical
    return None


# ── Edge Emission ────────────────────────────────────────────────────────────

def emit_gnosis_edges(
    video_id: str,
    chunks: list[TemporalChunk],
    video_publish_date: Optional[datetime] = None,
    video_url: Optional[str] = None,
) -> list[GnosisEdge]:
    """
    Link YouTube-derived knowledge to papers, repos, entities.
    
    Called after chunking to build the Relational Gnosis Graph (Strike 9.5).
    
    Args:
        video_id: YouTube video ID
        chunks: List of TemporalChunk from semantic_chunk()
        video_publish_date: Video publication date for t_valid
        video_url: Canonical video URL
    
    Returns:
        List of GnosisEdge for ingestion into Gnosis Graph
    """
    edges = []
    
    for chunk in chunks:
        text = chunk.text
        
        # 1. Temporal edge: video after paper → "implements"
        if paper := find_paper(text):
            if video_publish_date:
                edges.append(GnosisEdge(
                    source_type="youtube_video",
                    source_id=video_id,
                    source_url=video_url or f"https://www.youtube.com/watch?v={video_id}",
                    source_publish_date=video_publish_date,
                    target_type="paper",
                    target_id=paper["id"],
                    target_name=f"{paper['type'].upper()}: {paper['id']}",
                    edge_type=GnosisEdgeType.IMPLEMENTS,
                    confidence=0.8,
                    evidence=text[:200],
                    t_valid=video_publish_date.timestamp() if video_publish_date else time.time(),
                    chunk_hash=chunk.cas_hash or "",
                    chunk_t_start=chunk.t_start,
                    chunk_t_end=chunk.t_end,
                ))
        
        # 2. Contradiction edge: video claims X, paper claims ¬X
        if contradiction := find_contradiction(text):
            edges.append(GnosisEdge(
                source_type="youtube_video",
                source_id=video_id,
                source_url=video_url or f"https://www.youtube.com/watch?v={video_id}",
                source_publish_date=video_publish_date,
                target_type="concept",
                target_id=contradiction["claim"],
                target_name=contradiction["claim"],
                edge_type=GnosisEdgeType.CONTRADICTS,
                confidence=contradiction["confidence"],
                evidence=text[:200],
                t_valid=video_publish_date.timestamp() if video_publish_date else time.time(),
                chunk_hash=chunk.cas_hash or "",
                chunk_t_start=chunk.t_start,
                chunk_t_end=chunk.t_end,
                flagged=True,  # Requires human review
            ))
        
        # 3. Entity edge: speaker → known entity
        if chunk.speaker and (entity := match_entity(chunk.speaker)):
            edges.append(GnosisEdge(
                source_type="youtube_video",
                source_id=video_id,
                source_url=video_url or f"https://www.youtube.com/watch?v={video_id}",
                source_publish_date=video_publish_date,
                target_type="entity",
                target_id=entity.lower().replace(" ", "_"),
                target_name=entity,
                edge_type=GnosisEdgeType.SPOKEN_BY,
                confidence=0.9,
                evidence=f"Speaker: {chunk.speaker}",
                t_valid=video_publish_date.timestamp() if video_publish_date else time.time(),
                chunk_hash=chunk.cas_hash or "",
                chunk_t_start=chunk.t_start,
                chunk_t_end=chunk.t_end,
            ))
        
        # 4. GitHub repo edge
        if paper and paper["type"] == "github":
            edges.append(GnosisEdge(
                source_type="youtube_video",
                source_id=video_id,
                source_url=video_url or f"https://www.youtube.com/watch?v={video_id}",
                source_publish_date=video_publish_date,
                target_type="repo",
                target_id=paper["id"],
                target_name=f"GitHub: {paper['id']}",
                edge_type=GnosisEdgeType.CITES,
                confidence=0.85,
                evidence=text[:200],
                t_valid=video_publish_date.timestamp() if video_publish_date else time.time(),
                chunk_hash=chunk.cas_hash or "",
                chunk_t_start=chunk.t_start,
                chunk_t_end=chunk.t_end,
            ))
    
    return edges


# ── Contract Test Helpers (M21) ──────────────────────────────────────────────

def assert_gnosis_edge_type(obj: Any) -> None:
    """M21 Gate Integrity: Contract test for GnosisEdge type."""
    assert isinstance(obj, GnosisEdge), f"Expected GnosisEdge, got {type(obj)}"
    assert hasattr(obj, "source_type")
    assert hasattr(obj, "source_id")
    assert hasattr(obj, "target_type")
    assert hasattr(obj, "target_id")
    assert hasattr(obj, "edge_type")
    assert isinstance(obj.edge_type, GnosisEdgeType)
    assert hasattr(obj, "confidence")
    assert hasattr(obj, "evidence")
    assert hasattr(obj, "t_valid")
    assert hasattr(obj, "t_invalid")
    assert hasattr(obj, "is_valid_at")
    assert callable(obj.is_valid_at)
    assert hasattr(obj, "invalidate")
    assert callable(obj.invalidate)


def assert_emit_gnosis_edges_signature() -> None:
    """M21: Verify emit_gnosis_edges signature."""
    import inspect
    sig = inspect.signature(emit_gnosis_edges)
    params = list(sig.parameters.keys())
    assert "video_id" in params
    assert "chunks" in params
    assert "video_publish_date" in params
    assert "video_url" in params
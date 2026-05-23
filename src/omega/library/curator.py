"""Curation Pipeline — Quality-gated content processing and classification.

AP: AP-OMEGA-CURATOR-v1.0.0
ICS: [NODE: THOTH | ARCHETYPE: SOPHIA | CONTEXT: CURATION-PIPELINE]

Processes inbox items through a pipeline:
  1. Extract content (via ContentExtractor)
  2. Classify by domain
  3. Score quality (0.0-1.0)
  4. Route to library or reject

Quality gates:
  - 0.0-0.3: Reject (spam, low quality, empty)
  - 0.3-0.6: Flag for review
  - 0.6-0.8: Library (standard)
  - 0.8-1.0: Library (featured)
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import anyio

from .extractor import ContentExtractor, ExtractedContent

logger = logging.getLogger(__name__)


DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "ai_ml": ["machine learning", "deep learning", "neural network", "artificial intelligence", "llm", "transformer", "attention mechanism", "reinforcement learning"],
    "programming": ["python", "rust", "javascript", "typescript", "api", "microservice", "docker", "kubernetes", "git", "refactoring"],
    "research": ["paper", "arxiv", "preprint", "citation", "doi", "publication", "journal", "conference", "study"],
    "security": ["security", "encryption", "authentication", "vulnerability", "penetration", "zero trust", "compliance"],
    "philosophy": ["ontology", "epistemology", "gnostic", "hermetic", "alchemy", "archetype", "consciousness"],
    "systems": ["distributed", "architecture", "infrastructure", "observability", "telemetry", "scalability", "reliability"],
    "knowledge": ["knowledge graph", "semantic", "ontology", "taxonomy", "vector database", "embedding", "rag"],
    "general": [],
}


@dataclass
class CuratedDocument:
    """A fully curated document ready for the library."""

    doc_id: str
    source: str
    source_type: str
    title: str
    body: str
    summary: str
    domain: str
    quality_score: float
    author: Optional[str] = None
    published_date: Optional[str] = None
    language: str = "en"
    tags: List[str] = field(default_factory=list)
    headings: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    word_count: int = 0
    curated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "source": self.source,
            "source_type": self.source_type,
            "title": self.title,
            "body": self.body,
            "summary": self.summary,
            "domain": self.domain,
            "quality_score": self.quality_score,
            "author": self.author,
            "published_date": self.published_date,
            "language": self.language,
            "tags": self.tags,
            "headings": self.headings,
            "links": self.links[:30],
            "word_count": self.word_count,
            "curated_at": self.curated_at,
        }


class CurationPipeline:
    """Process inbox items through extraction, classification, scoring, and storage."""

    def __init__(self):
        self.extractor = ContentExtractor()

    async def process(
        self,
        source: str,
        source_type: str = "url",
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CuratedDocument:
        """Run a single item through the full curation pipeline."""
        extracted = await self.extractor.extract(source, source_type)
        return await self._curate(extracted, tags, metadata)

    async def _curate(
        self,
        extracted: ExtractedContent,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CuratedDocument:
        domain = self._classify_domain(extracted.body + " " + (extracted.title or ""))
        quality_score = self._score_quality(extracted, domain)

        import uuid
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"

        curated = CuratedDocument(
            doc_id=doc_id,
            source=extracted.source,
            source_type=extracted.source_type,
            title=extracted.title,
            body=extracted.body,
            summary=extracted.summary,
            domain=domain,
            quality_score=quality_score,
            author=extracted.author,
            published_date=extracted.published_date,
            language=extracted.language,
            tags=tags or [],
            headings=extracted.headings,
            links=extracted.links,
            word_count=extracted.word_count,
            metadata=metadata or {},
        )

        logger.info(f"Curated [{domain}] {extracted.title} (score={quality_score:.2f})")
        return curated

    def _classify_domain(self, text: str) -> str:
        """Classify content into a domain based on keyword matching."""
        text_lower = text.lower()
        scores: Dict[str, int] = {}
        for domain, keywords in DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[domain] = score

        if not scores:
            return "general"
        return max(scores, key=scores.get)

    def _score_quality(self, content: ExtractedContent, domain: str) -> float:
        """Score content quality 0.0-1.0 based on multiple factors."""
        score = 0.5  # baseline

        word_count = content.word_count
        if word_count < 50:
            score -= 0.3
        elif word_count > 500:
            score += 0.1
        if word_count > 2000:
            score += 0.1

        if content.title and len(content.title) > 10:
            score += 0.05
        if content.headings:
            score += 0.05
        if content.author:
            score += 0.05
        if content.published_date:
            score += 0.05

        if domain != "general":
            score += 0.05

        if content.error:
            score -= 0.5

        return max(0.0, min(1.0, score))

    def is_above_threshold(self, document: CuratedDocument, threshold: float = 0.6) -> bool:
        """Check if a curated document meets the quality threshold for library inclusion."""
        return document.quality_score >= threshold

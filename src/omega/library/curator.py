# AP: AP-ORACLE-RESTORE-v2.3.0
"""Curation Pipeline — Quality-gated content processing and classification.

AP: AP-OMEGA-CURATOR-v1.0.0
ICS: [NODE: KNOWLEDGE | ARCHETYPE: SOPHIA | CONTEXT: CURATION-PIPELINE]

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
# DocRef: docs/architecture/KNOWLEDGE_LIBRARY.md

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum


from .extractor import ContentExtractor, ExtractedContent

logger = logging.getLogger(__name__)


class DomainType(str, Enum):
    """Content domains for curation routing."""

    CODE = "code"
    SCIENCE = "science"
    DATA = "data"
    GENERAL = "general"


# ── Curation Extraction Engine ─────────────────────────────────────────


class CurationExtractor:
    """Extract metadata and quality signals from crawled content.

    Ported from legacy crawler_curation.py. Provides domain classification,
    citation detection, content structure analysis, and quality factor calculation.
    """

    def __init__(self):
        self.doi_pattern = r"\b10\.\d{4,}/[\S]+\b"
        self.arxiv_pattern = r"\b\d{4}\.\d{5}\b"
        self.code_pattern = r"```[\s\S]*?```|<code>[\s\S]*?</code>"
        self.image_pattern = r"<img|!\[|<figure"
        self.table_pattern = r"<table|<tr>|<td>"
        self.heading_pattern = r"<h([1-6])>"

    def classify_domain(self, content: str, url: str) -> DomainType:
        """Classify content domain (code/science/data/general)."""
        content_lower = content.lower()
        url_lower = url.lower()

        # CODE signals
        code_signals = [
            "github.com" in url_lower,
            "gitlab" in url_lower,
            "github" in content_lower,
            "git" in url_lower,
            "code" in url_lower,
            "python" in content_lower,
            "javascript" in content_lower,
            "def " in content or "class " in content,
            "import " in content,
            len(re.findall(self.code_pattern, content)) > 3,
        ]

        # SCIENCE signals
        science_signals = [
            "arxiv.org" in url_lower,
            "doi.org" in url_lower,
            "pubmed" in url_lower,
            "scholar" in url_lower,
            len(re.findall(self.doi_pattern, content)) > 0,
            len(re.findall(self.arxiv_pattern, content)) > 0,
            "abstract" in content_lower and "introduction" in content_lower,
            "methodology" in content_lower,
            "research" in content_lower,
        ]

        # DATA signals
        data_signals = [
            "dataset" in url_lower,
            "kaggle" in url_lower,
            "data.gov" in url_lower,
            ".csv" in url_lower or ".json" in url_lower,
            "SELECT" in content or "select" in content,
            len(re.findall(self.table_pattern, content)) > 5,
            "data" in url_lower,
            "table" in content_lower,
        ]

        code_score = sum(code_signals)
        science_score = sum(science_signals)
        data_score = sum(data_signals)

        if code_score > science_score and code_score > data_score and code_score > 0:
            return DomainType.CODE
        elif science_score > data_score and science_score > code_score and science_score > 0:
            return DomainType.SCIENCE
        elif data_score > code_score and data_score > science_score and data_score > 0:
            return DomainType.DATA
        else:
            return DomainType.GENERAL

    def extract_citations(self, content: str) -> Dict[str, int]:
        """Extract citations from content."""
        doi_matches = re.findall(self.doi_pattern, content)
        arxiv_matches = re.findall(self.arxiv_pattern, content)
        return {
            "doi": len(doi_matches),
            "arxiv": len(arxiv_matches),
            "total": len(doi_matches) + len(arxiv_matches),
        }

    def calculate_heading_structure_score(self, content: str) -> float:
        """Calculate heading structure quality (0-1)."""
        h_tags = {f"h{i}": len(re.findall(f"<h{i}>", content, re.IGNORECASE)) for i in range(1, 7)}
        total_headings = sum(h_tags.values())
        if total_headings == 0:
            return 0.0
        has_h1 = h_tags["h1"] > 0
        h1_dominance = h_tags["h1"] / total_headings if has_h1 else 0
        return round(min(1.0, h1_dominance + (0.2 if has_h1 else 0)), 2)

    def calculate_quality_factors(
        self, content: str, url: str, domain: DomainType
    ) -> Dict[str, float]:
        """Calculate 5 quality factors for curation scoring."""
        citations = self.extract_citations(content)
        word_count = len(content.split())
        code_blocks = len(re.findall(self.code_pattern, content))
        heading_score = self.calculate_heading_structure_score(content)

        factors = {}
        # 1. Freshness
        has_date = bool(re.search(r"\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}", content))
        factors["freshness"] = 0.7 if has_date else 0.3
        # 2. Completeness
        factors["completeness"] = round((min(1.0, word_count / 2000) + heading_score) / 2, 2)
        # 3. Authority
        authority_from_citations = min(1.0, citations["total"] / 10)
        authority_from_domain = 0.8 if domain in [DomainType.SCIENCE, DomainType.DATA] else 0.4
        factors["authority"] = round((authority_from_citations + authority_from_domain) / 2, 2)
        # 4. Structure
        structure_from_headings = heading_score
        structure_from_tables = min(1.0, len(re.findall(self.table_pattern, content)) / 5)
        structure_from_images = min(1.0, len(re.findall(self.image_pattern, content)) / 10)
        factors["structure"] = round(
            (structure_from_headings + structure_from_tables + structure_from_images) / 3, 2
        )
        # 5. Accessibility
        if domain == DomainType.CODE:
            factors["accessibility"] = round(min(1.0, code_blocks / 5), 2)
        elif domain == DomainType.DATA:
            factors["accessibility"] = round(
                min(1.0, len(re.findall(self.table_pattern, content)) / 3), 2
            )
        else:
            factors["accessibility"] = 0.5

        return factors


# ── Curation Data Models ──────────────────────────────────────────────


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
        self.curation_extractor = CurationExtractor()

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
        # 1. Domain Classification
        domain = self.curation_extractor.classify_domain(
            extracted.body + " " + (extracted.title or ""), extracted.source
        )

        # 2. 5-Factor Quality Scoring
        factors = self.curation_extractor.calculate_quality_factors(
            extracted.body, extracted.source, domain
        )

        # Calculate aggregate quality score (average of factors)
        quality_score = round(sum(factors.values()) / len(factors), 2)

        import uuid

        doc_id = f"doc_{uuid.uuid4().hex[:12]}"

        curated = CuratedDocument(
            doc_id=doc_id,
            source=extracted.source,
            source_type=extracted.source_type,
            title=extracted.title,
            body=extracted.body,
            summary=extracted.summary,
            domain=domain.value,
            quality_score=quality_score,
            author=extracted.author,
            published_date=extracted.published_date,
            language=extracted.language,
            tags=tags or [],
            headings=extracted.headings,
            links=extracted.links,
            word_count=extracted.word_count,
            metadata={**(metadata or {}), "quality_factors": factors},
        )

        logger.info(f"Curated [{domain.value}] {extracted.title} (score={quality_score:.2f})")
        return curated

    def is_above_threshold(self, document: CuratedDocument, threshold: float = 0.6) -> bool:
        """Check if a curated document meets the quality threshold for library inclusion."""
        return document.quality_score >= threshold

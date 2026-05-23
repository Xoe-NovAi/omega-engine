"""Research Engine — Multi-depth research on curated library content.

AP: AP-OMEGA-RESEARCH-v1.0.0
ICS: [NODE: OSIRIS | ARCHETYPE: APOLLO | CONTEXT: RESEARCH-ENGINE]

Research depth levels:
  Level 1 (Quick) — 1-2 sources, summary only, < 30s
  Level 2 (Standard) — 3-5 sources, compared, < 2min
  Level 3 (Deep) — 6-15 sources, synthesized, < 10min
  Level 4 (Scholarly) — All sources, citation graph, < 30min

Each level uses more library content and deeper analysis.
Results are cached and stored in data/research/.
"""

import json
import logging
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import anyio

logger = logging.getLogger(__name__)

DATA_DIR = Path(os.environ.get("OMEGA_DATA_DIR", str(Path.home() / "omega" / "data")))
RESEARCH_DIR = DATA_DIR / "research"
RESEARCH_DIR.mkdir(parents=True, exist_ok=True)


RESEARCH_DEPTHS = {
    1: {"label": "Quick", "min_sources": 1, "max_sources": 2},
    2: {"label": "Standard", "min_sources": 3, "max_sources": 5},
    3: {"label": "Deep", "min_sources": 6, "max_sources": 15},
    4: {"label": "Scholarly", "min_sources": 10, "max_sources": 50},
}


@dataclass
class ResearchResult:
    """Result of a research query."""

    research_id: str
    query: str
    depth: int
    sources_used: List[Dict[str, Any]]
    synthesis: str
    key_findings: List[str]
    confidence: float
    citations: List[str]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "research_id": self.research_id,
            "query": self.query,
            "depth": self.depth,
            "sources_used": self.sources_used,
            "synthesis": self.synthesis,
            "key_findings": self.key_findings,
            "confidence": self.confidence,
            "citations": self.citations,
            "created_at": self.created_at,
        }


class ResearchEngine:
    """Multi-depth research using the offline library."""

    def __init__(self, library: Optional[Any] = None, indexer: Optional[Any] = None):
        from .library import Library
        from .indexer import Indexer
        self.library = library or Library()
        self.indexer = indexer or Indexer()

    async def research(
        self,
        query: str,
        depth: int = 2,
        domain: Optional[str] = None,
    ) -> ResearchResult:
        """Execute a research query at the specified depth level."""
        depth_config = RESEARCH_DEPTHS.get(depth, RESEARCH_DEPTHS[2])

        sources = await self._gather_sources(query, domain, depth_config)
        synthesis = self._synthesize(sources, query, depth)
        key_findings = self._extract_findings(sources, query)
        citations = self._format_citations(sources)
        confidence = self._calculate_confidence(sources, depth)

        research_id = f"res_{uuid.uuid4().hex[:12]}"

        result = ResearchResult(
            research_id=research_id,
            query=query,
            depth=depth,
            sources_used=[{"doc_id": s.doc_id, "title": s.title, "domain": s.domain, "quality_score": s.quality_score} for s in sources],
            synthesis=synthesis,
            key_findings=key_findings,
            confidence=confidence,
            citations=citations,
        )

        await self._save_result(result)
        logger.info(f"Research complete [{depth}] {query[:60]} — {len(sources)} sources, confidence={confidence:.2f}")
        return result

    async def _gather_sources(
        self,
        query: str,
        domain: Optional[str],
        depth_config: Dict[str, int],
    ) -> List[Any]:
        """Gather sources from the library for a research query."""
        search_results = await self.indexer.hybrid_search(
            query=query,
            domain=domain,
            limit=depth_config["max_sources"],
        )

        sources = []
        for r in search_results:
            doc = await self.library.get(r["doc_id"])
            if doc and doc.quality_score >= 0.3:
                sources.append(doc)

        if len(sources) < depth_config["min_sources"]:
            extra = await self.library.search(query, domain=domain, limit=depth_config["max_sources"])
            for doc in extra:
                if doc not in sources and doc.quality_score >= 0.3:
                    sources.append(doc)

        return sources[:depth_config["max_sources"]]

    def _synthesize(self, sources: List[Any], query: str, depth: int) -> str:
        """Generate a synthesis from gathered sources."""
        if not sources:
            return f"No library sources found for: {query}. Try ingesting content first via the inbox."

        lines = [f"# Research: {query}", f"Depth: Level {depth} ({RESEARCH_DEPTHS[depth]['label']})", f"Sources: {len(sources)}", ""]

        for i, source in enumerate(sources, 1):
            lines.append(f"## Source {i}: {source.title}")
            lines.append(f"Domain: {source.domain} | Score: {source.quality_score:.2f}")
            if source.summary:
                lines.append(f"Summary: {source.summary}")
            lines.append("")

        lines.append("## Synthesis")
        if len(sources) == 1:
            lines.append(f"Based on the single source '{sources[0].title}', the key points are: {sources[0].summary}")
        elif len(sources) >= 2:
            domains = set(s.domain for s in sources)
            lines.append(f"Analysis across {len(sources)} sources from {len(domains)} domains ({', '.join(domains)}):")
            for j, source in enumerate(sources[:3], 1):
                lines.append(f"{j}. {source.title[:100]} — {source.summary[:200]}")

        lines.append(f"\nConfidence: {self._calculate_confidence(sources, depth):.0%}")
        return "\n".join(lines)

    def _extract_findings(self, sources: List[Any], query: str) -> List[str]:
        """Extract key findings from sources."""
        findings = []
        for source in sources[:5]:
            if source.summary:
                findings.append(f"From '{source.title}': {source.summary[:150]}")
        if not findings:
            findings.append(f"No specific findings extracted from {len(sources)} sources.")
        return findings

    def _format_citations(self, sources: List[Any]) -> List[str]:
        """Format sources as citations."""
        citations = []
        for i, source in enumerate(sources, 1):
            author = source.author or "Unknown"
            date = source.published_date or source.curated_at[:10] if source.curated_at else "n.d."
            citations.append(f"[{i}] {author} ({date}). {source.title}. Source: {source.source}")
        return citations

    def _calculate_confidence(self, sources: List[Any], depth: int) -> float:
        """Calculate confidence based on source quality and quantity."""
        if not sources:
            return 0.0
        avg_quality = sum(s.quality_score for s in sources) / len(sources)
        quantity_bonus = min(len(sources) / RESEARCH_DEPTHS[depth]["min_sources"], 1.0) * 0.2
        return min(avg_quality * 0.8 + quantity_bonus, 1.0)

    async def _save_result(self, result: ResearchResult) -> None:
        """Save research result to disk."""
        path = RESEARCH_DIR / f"{result.research_id}.json"
        async with await anyio.open_file(str(path), "w") as f:
            await f.write(json.dumps(result.to_dict(), indent=2, default=str))

    async def get_result(self, research_id: str) -> Optional[ResearchResult]:
        """Retrieve a previous research result."""
        path = RESEARCH_DIR / f"{research_id}.json"
        if not path.exists():
            return None
        async with await anyio.open_file(str(path)) as f:
            data = json.loads(await f.read())
        return ResearchResult(**data)

    async def list_results(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent research results."""
        results = []
        for path in sorted(RESEARCH_DIR.glob("*.json"), reverse=True)[:limit]:
            async with await anyio.open_file(str(path)) as f:
                data = json.loads(await f.read())
            results.append({
                "research_id": data["research_id"],
                "query": data["query"],
                "depth": data["depth"],
                "sources": len(data["sources_used"]),
                "confidence": data["confidence"],
                "created_at": data["created_at"],
            })
        return results

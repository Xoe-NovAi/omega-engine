"""SSP-V2 Search Router — Intent-based tier dispatch for sovereign search.
# Heritage: inspired by BSP culling (id Software 1993) — REJECTED per vet-028
AP: AP-SSP-V2-SEARCH-ROUTER-v1.0.0

Analyzes 6 signals (has_url, iris_confidence, entity_domain, query_category,
credit_status, provider_health) to produce a SearchIntent that drives tier
selection in SovereignSearchService.
"""

# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# SSP-V2 canonical tier mapping
TIER_LOCAL = 0
TIER_SEARXNG = 1
TIER_EXA = 2
TIER_FIRECRAWL = 3

# Query category keywords
_TECHNICAL_KEYWORDS = {
    "github",
    "git",
    "python",
    "rust",
    "c++",
    "api",
    "sdk",
    "library",
    "module",
    "class",
    "function",
    "import",
    "compile",
    "debug",
    "test",
    "docker",
    "podman",
    "systemd",
    "nginx",
    "ssh",
    "database",
    "sql",
}
_RESEARCH_KEYWORDS = {
    "paper",
    "arxiv",
    "study",
    "research",
    "analysis",
    "survey",
    "review",
    "theorem",
    "proof",
    "methodology",
    "experiment",
    "hypothesis",
}
_URL_PATTERN = re.compile(r"https?://\S+")


@dataclass
class SearchIntent:
    """Contract between Oracle and search pipeline.

    Produced by SearchRouter, consumed by SovereignSearchService.
    """

    primary_tier: int = TIER_SEARXNG
    max_tier: int = TIER_FIRECRAWL
    force_tier: Optional[int] = None
    query_category: str = "factual"  # factual|research|technical|deep
    search_depth: str = "standard"  # quick|standard|deep
    entity_name: Optional[str] = None
    max_results: int = 10
    allow_cloud_search: bool = True
    credit_budget_firecrawl: int = 100
    signals_used: Dict[str, Any] = field(default_factory=dict)
    routing_reasoning: List[str] = field(default_factory=list)


class SearchRouter:
    """Analyzes query signals and produces a SearchIntent.

    Lightweight, no LLM calls, pure rule-based dispatch.
    Designed to be called before every search operation.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def route(
        self,
        query: str,
        entity_name: Optional[str] = None,
        iris_confidence: Optional[float] = None,
        force_tier: Optional[int] = None,
        has_credits: bool = True,
        provider_health: Optional[Dict[int, bool]] = None,
    ) -> SearchIntent:
        """Analyze signals and produce a SearchIntent.

        Args:
            query: The search query string.
            entity_name: Entity context (if any).
            iris_confidence: Confidence score from Oracle (0.0-1.0).
            force_tier: Override tier (bypass routing).
            has_credits: Whether cloud search credits are available.
            provider_health: Dict mapping tier number to health status.
        """
        signals: Dict[str, Any] = {}
        reasoning: List[str] = []

        has_url = bool(_URL_PATTERN.search(query))
        signals["has_url"] = has_url
        signals["iris_confidence"] = iris_confidence
        signals["entity_domain"] = entity_name or "general"
        query_category = self._classify_query(query)
        signals["query_category"] = query_category
        signals["has_credits"] = has_credits
        signals["provider_health"] = provider_health or {}
        signals["query_length"] = len(query)

        # 1. Terminal Rules (Overrides)
        if has_url:
            reasoning.append("URL detected → T3 (Firecrawl scrape)")
            return SearchIntent(
                primary_tier=TIER_FIRECRAWL,
                max_tier=TIER_FIRECRAWL,
                force_tier=TIER_FIRECRAWL,
                query_category="url",
                search_depth="deep",
                entity_name=entity_name,
                signals_used=signals,
                routing_reasoning=reasoning,
            )

        if force_tier is not None:
            reasoning.append(f"force_tier={force_tier} → bypass routing")
            return SearchIntent(
                primary_tier=force_tier,
                max_tier=force_tier,
                force_tier=force_tier,
                query_category=query_category,
                entity_name=entity_name,
                signals_used=signals,
                routing_reasoning=reasoning,
            )

        # 2. Base Intent (Category-based)
        primary_tier = TIER_SEARXNG
        max_tier = TIER_SEARXNG
        search_depth = "standard"

        if query_category == "technical":
            reasoning.append("Technical query → T1 (SearXNG)")
        elif query_category == "research":
            reasoning.append("Research query → T1→T2 (SearXNG → Exa)")
            max_tier = TIER_EXA
            search_depth = "deep"
        elif query_category == "deep" or len(query) > 80:
            reasoning.append("Complex query → T1→T2→T3 (full pipeline)")
            max_tier = TIER_FIRECRAWL
            search_depth = "deep"
        else:
            reasoning.append("Default factual → T1 (SearXNG)")

        # 3. Constraints (Credits & Confidence)
        allow_cloud_search = has_credits
        if not has_credits:
            reasoning.append("No credits → T0-T1 only (local + SearXNG)")
            primary_tier = TIER_LOCAL
            max_tier = TIER_SEARXNG
            search_depth = "quick"
        elif iris_confidence is not None and iris_confidence > 0.7:
            reasoning.append(f"High confidence ({iris_confidence:.2f}) → T0-T1 only")
            primary_tier = TIER_LOCAL
            max_tier = TIER_SEARXNG
            search_depth = "quick"

        # 4. Availability (Provider Health)
        if provider_health and provider_health.get(primary_tier) is False:
            reasoning.append(f"T{primary_tier} is DOWN → escalating to T2")
            primary_tier = TIER_EXA
            if provider_health.get(primary_tier) is False:
                reasoning.append(f"T{primary_tier} is also DOWN → escalating to T3")
                primary_tier = TIER_FIRECRAWL

        # 5. Special Case: Technical Entity
        if entity_name and any(
            x in entity_name.lower() for x in ["dev", "eng", "tech", "architect"]
        ):
            reasoning.append(f"Technical entity ({entity_name}) → prefer T2 (Exa)")
            if primary_tier < TIER_EXA:
                primary_tier = TIER_EXA
            if max_tier < TIER_FIRECRAWL:
                max_tier = TIER_FIRECRAWL

        return SearchIntent(
            primary_tier=primary_tier,
            max_tier=max_tier,
            query_category=query_category,
            search_depth=search_depth,
            entity_name=entity_name,
            allow_cloud_search=allow_cloud_search,
            signals_used=signals,
            routing_reasoning=reasoning,
        )

    def _classify_query(self, query: str) -> str:
        """Classify query into a category based on keywords."""
        lower = query.lower()
        words = set(lower.split())

        if words & _TECHNICAL_KEYWORDS:
            return "technical"
        if words & _RESEARCH_KEYWORDS:
            return "research"
        if "?" in query and len(query) < 40:
            return "factual"
        if len(query) > 80:
            return "deep"
        return "factual"

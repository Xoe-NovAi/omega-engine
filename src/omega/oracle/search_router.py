"""SSP-V2 Search Router — Intent-based tier dispatch for sovereign search.
# [id-soft: doom-1993] Lattice-Culling — signal-driven provider culling
AP: AP-SSP-V2-SEARCH-ROUTER-v1.0.0

Analyzes 6 signals (has_url, iris_confidence, entity_domain, query_category,
credit_status, provider_health) to produce a SearchIntent that drives tier
selection in SovereignSearchService.
"""
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
    "github", "git", "python", "rust", "c++", "api", "sdk", "library",
    "module", "class", "function", "import", "compile", "debug", "test",
    "docker", "podman", "systemd", "nginx", "ssh", "database", "sql",
}
_RESEARCH_KEYWORDS = {
    "paper", "arxiv", "study", "research", "analysis", "survey", "review",
    "theorem", "proof", "methodology", "experiment", "hypothesis",
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
    query_category: str = "factual"       # factual|research|technical|deep
    search_depth: str = "standard"        # quick|standard|deep
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
        
        # Signal 1: URL detection
        has_url = bool(_URL_PATTERN.search(query))
        signals["has_url"] = has_url
        
        # Signal 2: Confidence
        signals["iris_confidence"] = iris_confidence
        
        # Signal 3: Entity domain (inferred from entity name)
        query_category = self._classify_query(query)
        signals["query_category"] = query_category
        
        # Signal 4: Credit status
        signals["has_credits"] = has_credits
        
        # Signal 5: Provider health
        signals["provider_health"] = provider_health or {}
        
        # Signal 6: Query complexity
        signals["query_length"] = len(query)
        
        # === Routing decisions (highest priority wins) ===
        
        # Rule 1: Direct URL → FORCE T3 (Firecrawl scrape)
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
        
        # Rule 2: Force tier override
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
        
        # Rule 3: No credits → skip cloud tiers
        if not has_credits:
            reasoning.append("No credits → T0-T1 only (local + SearXNG)")
            return SearchIntent(
                primary_tier=TIER_LOCAL,
                max_tier=TIER_SEARXNG,
                query_category=query_category,
                search_depth="quick",
                entity_name=entity_name,
                allow_cloud_search=False,
                signals_used=signals,
                routing_reasoning=reasoning,
            )
        
        # Rule 4: High confidence → minimal search
        if iris_confidence is not None and iris_confidence > 0.7:
            reasoning.append(f"High confidence ({iris_confidence:.2f}) → T0-T1 only")
            return SearchIntent(
                primary_tier=TIER_LOCAL,
                max_tier=TIER_SEARXNG,
                query_category=query_category,
                search_depth="quick",
                entity_name=entity_name,
                signals_used=signals,
                routing_reasoning=reasoning,
            )
        
        # Rule 5: Category-based dispatch
        if query_category == "technical":
            reasoning.append("Technical query → T1 (SearXNG)")
            return SearchIntent(
                primary_tier=TIER_SEARXNG,
                max_tier=TIER_SEARXNG,
                query_category=query_category,
                search_depth="standard",
                entity_name=entity_name,
                signals_used=signals,
                routing_reasoning=reasoning,
            )
        
        if query_category == "research":
            reasoning.append("Research query → T1→T2 (SearXNG → Exa)")
            return SearchIntent(
                primary_tier=TIER_SEARXNG,
                max_tier=TIER_EXA,
                query_category=query_category,
                search_depth="deep",
                entity_name=entity_name,
                signals_used=signals,
                routing_reasoning=reasoning,
            )
        
        # Rule 6: Deep/complex query → full pipeline
        if len(query) > 80 or query_category == "deep":
            reasoning.append("Complex query → T1→T2→T3 (full pipeline)")
            return SearchIntent(
                primary_tier=TIER_SEARXNG,
                max_tier=TIER_FIRECRAWL,
                query_category=query_category,
                search_depth="deep",
                entity_name=entity_name,
                signals_used=signals,
                routing_reasoning=reasoning,
            )
        
        # Default: standard factual search
        reasoning.append("Default factual → T1 (SearXNG)")
        return SearchIntent(
            primary_tier=TIER_SEARXNG,
            max_tier=TIER_SEARXNG,
            query_category=query_category,
            search_depth="standard",
            entity_name=entity_name,
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

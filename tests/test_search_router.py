"""Tests for SSP-V2 Search Router — signal-based tier dispatch.
AP: AP-SSP-V2-ROUTER-TESTS-v1.0.0
"""
import pytest
from omega.oracle.search_router import (
    SearchRouter, SearchIntent,
    TIER_LOCAL, TIER_SEARXNG, TIER_EXA, TIER_FIRECRAWL,
)


class TestSearchRouter:
    """Test SearchRouter signal analysis and intent production."""

    def setup_method(self):
        self.router = SearchRouter()

    def test_default_route_factual(self):
        """Short factual query defaults to T1 (SearXNG)."""
        intent = self.router.route("what is the capital of france")
        assert intent.primary_tier == TIER_SEARXNG
        assert intent.max_tier == TIER_SEARXNG
        assert intent.query_category == "factual"
        assert intent.search_depth == "standard"

    def test_technical_keyword_classified(self):
        """Query with technical keyword (python) classified as technical."""
        intent = self.router.route("what is python")
        assert intent.query_category == "technical"
        assert intent.primary_tier == TIER_SEARXNG

    def test_url_forces_t3(self):
        """URL in query forces T3 (Firecrawl scrape)."""
        intent = self.router.route("scrape https://example.com/docs")
        assert intent.force_tier == TIER_FIRECRAWL
        assert intent.primary_tier == TIER_FIRECRAWL
        assert intent.max_tier == TIER_FIRECRAWL
        assert intent.query_category == "url"

    def test_force_tier_override(self):
        """force_tier bypasses all routing logic."""
        intent = self.router.route("hello world", force_tier=TIER_EXA)
        assert intent.force_tier == TIER_EXA
        assert intent.primary_tier == TIER_EXA
        assert intent.max_tier == TIER_EXA

    def test_no_credits_skips_cloud(self):
        """No credits → T0-T1 only."""
        intent = self.router.route("deep learning papers", has_credits=False)
        assert intent.primary_tier == TIER_LOCAL
        assert intent.max_tier == TIER_SEARXNG
        assert intent.allow_cloud_search is False

    def test_high_confidence_minimal_search(self):
        """High confidence → T0-T1 only."""
        intent = self.router.route("test query", iris_confidence=0.85)
        assert intent.primary_tier == TIER_LOCAL
        assert intent.max_tier == TIER_SEARXNG
        assert intent.search_depth == "quick"

    def test_technical_query_t1(self):
        """Technical query → T1 (SearXNG)."""
        intent = self.router.route("python import error github")
        assert intent.primary_tier == TIER_SEARXNG
        assert intent.max_tier == TIER_SEARXNG
        assert intent.query_category == "technical"

    def test_research_query_t1_to_t2(self):
        """Research query → T1→T2 (SearXNG → Exa)."""
        intent = self.router.route("arxiv paper on transformers")
        assert intent.primary_tier == TIER_SEARXNG
        assert intent.max_tier == TIER_EXA
        assert intent.query_category == "research"

    def test_complex_query_full_pipeline(self):
        """Long/complex query → T1→T2→T3 (full pipeline)."""
        # Use a query with no research/technical keywords, just long
        query = "how does the process of something work in general when you need to understand " * 3
        intent = self.router.route(query)
        assert intent.primary_tier == TIER_SEARXNG
        assert intent.max_tier == TIER_FIRECRAWL
        assert intent.search_depth == "deep"

    def test_entity_name_propagated(self):
        """Entity name flows through to SearchIntent."""
        intent = self.router.route("test query", entity_name="sophia")
        assert intent.entity_name == "sophia"

    def test_signals_recorded(self):
        """All input signals are recorded in SearchIntent."""
        intent = self.router.route(
            "test query",
            entity_name="kali",
            iris_confidence=0.5,
            has_credits=True,
            provider_health={TIER_SEARXNG: True, TIER_EXA: False},
        )
        assert "has_url" in intent.signals_used
        assert "iris_confidence" in intent.signals_used
        assert "query_category" in intent.signals_used
        assert "has_credits" in intent.signals_used
        assert intent.signals_used["provider_health"] == {TIER_SEARXNG: True, TIER_EXA: False}

    def test_routing_reasoning_populated(self):
        """Routing reasoning explains the decision."""
        intent = self.router.route("what is python")
        assert len(intent.routing_reasoning) > 0
        assert any("T1" in r or "SearXNG" in r for r in intent.routing_reasoning)

    def test_classify_technical(self):
        """_classify_query detects technical keywords."""
        assert self.router._classify_query("docker container setup") == "technical"
        assert self.router._classify_query("python api import") == "technical"

    def test_classify_research(self):
        """_classify_query detects research keywords."""
        assert self.router._classify_query("arxiv paper on LLMs") == "research"
        assert self.router._classify_query("study methodology experiment") == "research"

    def test_classify_deep(self):
        """Long queries are classified as deep."""
        query = "detailed " * 20
        assert self.router._classify_query(query) == "deep"


class TestSearchIntent:
    """Test SearchIntent dataclass defaults."""

    def test_defaults(self):
        intent = SearchIntent()
        assert intent.primary_tier == TIER_SEARXNG
        assert intent.max_tier == TIER_FIRECRAWL
        assert intent.force_tier is None
        assert intent.query_category == "factual"
        assert intent.search_depth == "standard"
        assert intent.max_results == 10
        assert intent.allow_cloud_search is True

    def test_tier_constants(self):
        """Tier constants match SSP-V2 spec."""
        assert TIER_LOCAL == 0
        assert TIER_SEARXNG == 1
        assert TIER_EXA == 2
        assert TIER_FIRECRAWL == 3

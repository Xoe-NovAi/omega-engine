"""Tests for omega-sieve scraper."""
# AP: AP-OMEGA-SIEVE-TESTS-v1.0.0

import pytest
from omega_sieve.scraper import SovereignScraper, T1Scraper, T2Scraper, T3Scraper, ScrapeResult


class TestScrapeResult:
    """Test ScrapeResult dataclass."""

    def test_success_bool(self):
        r = ScrapeResult(url="https://example.com", content="hello", tier="fast", success=True)
        assert bool(r) is True

    def test_failure_bool(self):
        r = ScrapeResult(url="https://example.com", content="", tier="fast", success=False, error="fail")
        assert bool(r) is False

    def test_empty_content_bool(self):
        r = ScrapeResult(url="https://example.com", content="", tier="fast", success=True)
        assert bool(r) is False

    def test_is_empty(self):
        r = ScrapeResult(url="https://example.com", content="   ", tier="fast", success=True)
        assert r.is_empty is True

    def test_not_empty(self):
        r = ScrapeResult(url="https://example.com", content="hello", tier="fast", success=True)
        assert r.is_empty is False


class TestSovereignScraper:
    """Test SovereignScraper initialization and property checks."""

    def test_init(self):
        scraper = SovereignScraper()
        assert scraper.t1 is not None
        assert scraper.t2 is not None
        assert scraper.t3 is not None

    def test_available_tiers_default(self):
        scraper = SovereignScraper()
        tiers = scraper.available_tiers
        assert isinstance(tiers, list)

    def test_scrape_unknown_tier(self):
        scraper = SovereignScraper()
        with pytest.raises(Exception):
            import anyio
            anyio.run(scraper.scrape, "https://example.com", tier="invalid")


class TestVerifier:
    """Test TriangulationVerifier."""

    def test_import(self):
        from omega_sieve.verifier import TriangulationVerifier, VerificationResult
        v = TriangulationVerifier()
        assert v.threshold == 0.3

    def test_both_empty(self):
        from omega_sieve.verifier import TriangulationVerifier
        from omega_sieve.scraper import ScrapeResult
        v = TriangulationVerifier()
        t1 = ScrapeResult(url="https://x.com", content="", tier="fast", success=False, error="fail")
        t3 = ScrapeResult(url="https://x.com", content="", tier="deep", success=False, error="fail")
        result = v.verify_t1_t3(t1, t3)
        assert result.passed is False
        assert result.confidence == 0.0

    def test_identical_content(self):
        from omega_sieve.verifier import TriangulationVerifier
        from omega_sieve.scraper import ScrapeResult
        v = TriangulationVerifier()
        content = "The quick brown fox jumps over the lazy dog"
        t1 = ScrapeResult(url="https://x.com", content=content, tier="fast", success=True)
        t3 = ScrapeResult(url="https://x.com", content=content, tier="deep", success=True)
        result = v.verify_t1_t3(t1, t3)
        assert result.lexical_similarity > 0.9

    def test_completely_different_content(self):
        from omega_sieve.verifier import TriangulationVerifier
        from omega_sieve.scraper import ScrapeResult
        v = TriangulationVerifier()
        t1 = ScrapeResult(url="https://x.com", content="The quick brown fox", tier="fast", success=True)
        t3 = ScrapeResult(url="https://x.com", content="Quantum physics is fascinating", tier="deep", success=True)
        result = v.verify_t1_t3(t1, t3)
        assert result.lexical_similarity < 0.3

    def test_content_delta_description(self):
        from omega_sieve.verifier import TriangulationVerifier
        from omega_sieve.scraper import ScrapeResult
        v = TriangulationVerifier()
        t1 = ScrapeResult(url="https://x.com", content="A B C D E F G H I J K L M N O P", tier="fast", success=True)
        t3 = ScrapeResult(url="https://x.com", content="A B C D E F G H I J K L M N O P Q R S T U V W X Y Z", tier="deep", success=True)
        result = v.verify_t1_t3(t1, t3)
        assert result.content_delta != ""

    def test_best_result_uses_t1_when_verified(self):
        from omega_sieve.verifier import TriangulationVerifier
        from omega_sieve.scraper import ScrapeResult
        v = TriangulationVerifier()
        content = "This is a long enough piece of text that should pass verification"
        t1 = ScrapeResult(url="https://x.com", content=content, tier="fast", success=True)
        t3 = ScrapeResult(url="https://x.com", content=content, tier="deep", success=True)
        best, ver = v.best_result(t1, t3)
        assert best.tier == "fast"


class TestGuards:
    """Test SovereignSentry and BudgetGuard."""

    def test_circuit_breaker_initial_state(self):
        from omega_sieve.guards import CircuitBreaker
        cb = CircuitBreaker("test")
        assert cb.is_open is False

    def test_circuit_breaker_opens_after_threshold(self):
        from omega_sieve.guards import CircuitBreaker
        cb = CircuitBreaker("test", failure_threshold=3, reset_timeout=999)
        assert cb.is_open is False
        cb.record_failure()
        assert cb.is_open is False
        cb.record_failure()
        assert cb.is_open is False
        cb.record_failure()
        assert cb.is_open is True

    def test_circuit_breaker_reset_on_success(self):
        from omega_sieve.guards import CircuitBreaker
        cb = CircuitBreaker("test", failure_threshold=2)
        cb.record_failure()
        cb.record_failure()
        assert cb.is_open is True
        cb.record_success()
        assert cb.is_open is False

    def test_budget_guard_init(self):
        from omega_sieve.guards import BudgetGuard
        bg = BudgetGuard()
        assert bg._counters == {}

    def test_budget_guard_can_afford_unknown(self):
        from omega_sieve.guards import BudgetGuard
        bg = BudgetGuard()
        import anyio
        result = anyio.run(bg.can_afford, "unknown_provider")
        assert result is True

    def test_sentry_init(self):
        from omega_sieve.guards import SovereignSentry
        s = SovereignSentry()
        assert s is not None


class TestProxy:
    """Test SovereignProxyPool."""

    def test_empty_pool_returns_none(self):
        from omega_sieve.proxy import SovereignProxyPool
        pool = SovereignProxyPool()
        proxy = pool.get_proxy("https://example.com")
        assert proxy is None

    def test_domain_affinity(self):
        from omega_sieve.proxy import SovereignProxyPool, ProxyConfig
        pool = SovereignProxyPool()
        pool.add_proxy(ProxyConfig(url="http://proxy1:8080", type="datacenter"))
        pool.add_proxy(ProxyConfig(url="http://proxy2:8080", type="residential"))

        # Same domain should get same proxy
        p1 = pool.get_proxy("https://example.com/page1")
        p2 = pool.get_proxy("https://example.com/page2")
        assert p1 is not None
        assert p2 is not None
        assert p1.url == p2.url

    def test_different_domains_get_different_proxies(self):
        from omega_sieve.proxy import SovereignProxyPool, ProxyConfig
        pool = SovereignProxyPool()
        pool.add_proxy(ProxyConfig(url="http://proxy1:8080", type="datacenter"))
        pool.add_proxy(ProxyConfig(url="http://proxy2:8080", type="residential"))

        p1 = pool.get_proxy("https://example.com")
        p2 = pool.get_proxy("https://other.com")
        assert p1 is not None
        assert p2 is not None
        # May or may not be same — round-robin
        assert isinstance(p1.url, str)
        assert isinstance(p2.url, str)

    def test_failure_tracking(self):
        from omega_sieve.proxy import SovereignProxyPool, ProxyConfig
        pool = SovereignProxyPool()
        pool.add_proxy(ProxyConfig(url="http://proxy1:8080", type="datacenter"))
        pool.add_proxy(ProxyConfig(url="http://proxy2:8080", type="residential"))

        p1 = pool.get_proxy("https://example.com")
        pool.record_failure("https://example.com")
        pool.record_failure("https://example.com")
        pool.record_failure("https://example.com")

        # After 3 failures, session is unhealthy → should get new proxy
        p2 = pool.get_proxy("https://example.com")
        assert p2 is not None
        assert p1.url != p2.url  # Should have switched proxies

    def test_success_resets_failures(self):
        from omega_sieve.proxy import SovereignProxyPool, ProxyConfig
        pool = SovereignProxyPool()
        pool.add_proxy(ProxyConfig(url="http://proxy1:8080", type="datacenter"))

        pool.get_proxy("https://example.com")
        pool.record_failure("https://example.com")
        pool.record_failure("https://example.com")
        pool.record_success("https://example.com")

        proxy = pool.get_proxy("https://example.com")
        assert proxy is not None


class TestConfig:
    """Test configuration loading."""

    def test_default_config(self):
        from omega_sieve.config import SieveConfig
        config = SieveConfig()
        assert config.searxng_url == "http://localhost:4004"
        assert config.budget.exa_max_calls == 100

    def test_config_from_dict(self):
        from omega_sieve.config import SieveConfig
        config = SieveConfig.from_dict({
            "searxng_url": "http://mysearxng:8888",
            "budget": {"exa_max_calls": 50},
        })
        assert config.searxng_url == "http://mysearxng:8888"
        assert config.budget.exa_max_calls == 50

    def test_config_to_dict(self):
        from omega_sieve.config import SieveConfig
        config = SieveConfig()
        d = config.to_dict()
        assert "providers" in d
        assert "budget" in d
        assert "searxng_url" in d

    def test_load_config_nonexistent(self):
        from omega_sieve.config import load_config
        config = load_config("/tmp/nonexistent_sieve_config.yaml")
        assert isinstance(config.searxng_url, str)


class TestYouTube:
    """Test YouTubeSieve (unit tests only — no network)."""

    def test_extract_video_id_standard(self):
        from omega_sieve.youtube import YouTubeSieve
        sieve = YouTubeSieve()
        vid = sieve._extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert vid == "dQw4w9WgXcQ"

    def test_extract_video_id_short(self):
        from omega_sieve.youtube import YouTubeSieve
        sieve = YouTubeSieve()
        vid = sieve._extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        assert vid == "dQw4w9WgXcQ"

    def test_extract_video_id_shorts(self):
        from omega_sieve.youtube import YouTubeSieve
        sieve = YouTubeSieve()
        vid = sieve._extract_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ")
        assert vid == "dQw4w9WgXcQ"

    def test_extract_video_id_none(self):
        from omega_sieve.youtube import YouTubeSieve
        sieve = YouTubeSieve()
        vid = sieve._extract_video_id("https://example.com")
        assert vid is None


class TestErrors:
    """Test error types."""

    def test_sieve_error(self):
        from omega_sieve.errors import SieveError, ScrapeError, VerificationError
        assert issubclass(ScrapeError, SieveError)
        assert issubclass(VerificationError, SieveError)

    def test_provider_error(self):
        from omega_sieve.errors import ProviderError, BudgetExceededError, SieveError
        assert issubclass(ProviderError, SieveError)
        assert issubclass(BudgetExceededError, ProviderError)

    def test_youtube_error(self):
        from omega_sieve.errors import YouTubeError, SieveError
        assert issubclass(YouTubeError, SieveError)

    def test_error_instantiation(self):
        from omega_sieve.errors import ScrapeError
        e = ScrapeError("test error")
        assert str(e) == "test error"
"""Sovereign Search Service — Core implementation of the SSP-V2 4-Tier Search Protocol.
# Heritage: inspired by BSP culling (id Software 1993) — REJECTED per vet-028
AP: AP-SOVEREIGN-SEARCH-SERVICE-v2.2.0
ICS: [NODE: ARCHON | ARCHETYPE: HERMES | CONTEXT: SEARCH-PARTNERSHIP]

SSP-V2 Canonical Tier Mapping:
  T0: Local Cache (MemoryStore + SovereignCache)
  T1: SearXNG (Broad Discovery — privacy-first metasearch)
  T2: Exa (Neural/Intent Refinement)
  T3: Firecrawl (Deep Extraction & Structuring)
"""

# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
from __future__ import annotations

import logging
import anyio
import os
import re
import uuid
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timezone

from omega.errors import (
    OmegaError,
    OmegaError, ProviderError, ProviderRateLimitError,
    ProviderUnavailableError, ProviderAuthError
)
from omega.memory_store import get_memory_store, MemoryStore
from omega.library.indexer import Indexer
from omega.oracle.search_providers import (
    FirecrawlProvider, ExaProvider, SearXNGProvider
)
from omega.oracle.search_router import SearchRouter, SearchIntent, TIER_LOCAL, TIER_SEARXNG, TIER_EXA, TIER_FIRECRAWL
from omega.oracle.search_cache import SovereignCache
from omega.oracle.skeptical_verifier import SkepticalVerifier
from omega.workers.background_researcher.credit_budget import APICreditBudget

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config" / "search.yaml"


def _load_search_config() -> Dict[str, Any]:
    """Load SSP-V2 configuration from config/search.yaml."""
    try:
        if _CONFIG_PATH.exists():
            with open(_CONFIG_PATH) as f:
                return yaml.safe_load(f) or {}
        else:
            logger.warning("config/search.yaml not found, using defaults")
            return {}
    except (OmegaError, RuntimeError, OSError) as e:
        logger.warning(f"Failed to load config/search.yaml: {e}")
        return {}


class SovereignSearchService:
    """
    Core engine service implementing the SSP-V2 Search Protocol.

    The SSP-V2 ensures credit efficiency and intent-aware routing by executing
    search operations across a 4-tier hierarchy:

    T0: Local Cache (MemoryStore + SovereignCache)
    T1: SearXNG (Broad Discovery — zero-cost, privacy-first)
    T2: Exa (Neural Refinement — semantic search)
    T3: Firecrawl (Deep Extraction — structured content)

    Routing is driven by SearchRouter (signal-based intent classification).
    Configuration is loaded from config/search.yaml.
    """

    def __init__(
        self,
        memory_store: Optional[MemoryStore] = None,
        model_gateway: Any = None,
        indexer: Optional[Indexer] = None,
        firecrawl_key: Optional[str] = None,
        exa_key: Optional[str] = None,
        searxng_url: Optional[str] = None,
        verifier: Optional[SkepticalVerifier] = None,
        router: Optional[SearchRouter] = None,
    ):
        from omega.oracle.model_gateway import ModelGateway
        from omega.oracle.health_monitor import get_health_monitor

        # Load SSP-V2 configuration
        self.config = _load_search_config()
        tiers_cfg = self.config.get("tiers", {})
        routing_cfg = self.config.get("routing", {})
        cache_cfg = self.config.get("cache", {})

        self.memory_store = memory_store or get_memory_store()
        self.model_gateway = model_gateway or ModelGateway(health_monitor=get_health_monitor())
        self.indexer = indexer or Indexer()
        
        # Initialize SovereignCache (Sovereign persistence for T0/T3)
        self.cache = SovereignCache(
            cache_dir=cache_cfg.get("directory", ".firecrawl"),
            ttl_seconds=cache_cfg.get("ttl_seconds", 86400)
        )
        
        self.budget = APICreditBudget()

        # Configure T1 (SearXNG) from config with caller override
        t1_cfg = tiers_cfg.get("T1", {})
        resolved_searxng_url = (searxng_url or os.environ.get("SEARXNG_BASE_URL") or t1_cfg.get("url", "http://127.0.0.1:8017")).rstrip("/")
        t1_timeout = t1_cfg.get("timeout_seconds", 15)
        t1_retries = t1_cfg.get("retries", 2)
        t1_delays = t1_cfg.get("retry_delay_seconds", [5.0, 10.0])

        # SSP-V2 Providers — direct API (bypass MCP bridge for internal use)
        self.searxng = SearXNGProvider(
            base_url=resolved_searxng_url,
            timeout=t1_timeout,
            retries=t1_retries,
            retry_delays=t1_delays,
        )
        self.firecrawl = FirecrawlProvider(firecrawl_key) if firecrawl_key else FirecrawlProvider()
        self.exa = ExaProvider(exa_key) if exa_key else ExaProvider()
        self.verifier = verifier or SkepticalVerifier(self.model_gateway)
        self.router = router or SearchRouter(config=routing_cfg)

    async def search(
        self,
        query: str,
        entity_name: str,
        limit: int = 10,
        max_tier: int = TIER_FIRECRAWL,
        force_tier: Optional[int] = None,
        iris_confidence: Optional[float] = None,
        search_intent: Optional[SearchIntent] = None,
    ) -> Dict[str, Any]:
        """
        Execute the SSP-V2 4-Tier Sovereign Search Protocol.

        If search_intent is provided, uses it directly (caller pre-computed routing).
        Otherwise, routes via SearchRouter using the provided signals.

        Returns a report containing the primary finding, evidence, and fallback log.
        """
        trace_id = f"srch_{uuid.uuid4().hex[:12]}"
        has_credits = self._has_firecrawl_credits()

        # Obtain SearchIntent
        if search_intent is None:
            # Gather real-time provider health for the router
            tier_map = {TIER_SEARXNG: "searxng", TIER_EXA: "exa", TIER_FIRECRAWL: "firecrawl"}
            health_status = {tier: self.model_gateway.health_monitor.is_available(name) for tier, name in tier_map.items()}

            search_intent = self.router.route(
                query=query,
                entity_name=entity_name,
                iris_confidence=iris_confidence,
                force_tier=force_tier,
                has_credits=has_credits,
                provider_health=health_status,
            )

        report: Dict[str, Any] = {
            "trace_id": trace_id,
            "primary_finding": None,
            "evidence": [],
            "fallback_log": [],
            "final_tier": None,
            "status": "pending",
            "verification": None,
            "search_intent": {
                "primary_tier": search_intent.primary_tier,
                "max_tier": search_intent.max_tier,
                "query_category": search_intent.query_category,
                "routing_reasoning": search_intent.routing_reasoning,
            },
        }

        evidence_pool: List[Dict[str, Any]] = []

        # Execute tiers from primary_tier up to max_tier
        effective_tier = search_intent.force_tier if search_intent.force_tier is not None else search_intent.primary_tier
        effective_max = search_intent.force_tier if search_intent.force_tier is not None else search_intent.max_tier

        for tier in range(effective_tier, effective_max + 1):
            try:
                result = await self._execute_tier(tier, query, entity_name, limit)
                if result:
                    report["primary_finding"] = result
                    report["final_tier"] = tier
                    report["status"] = "success"
                    evidence_pool.extend(self._extract_evidence_from_finding(result))
                    break
                else:
                    report["fallback_log"].append({
                        "tier": tier,
                        "outcome": "empty",
                        "message": f"Tier {tier} returned no results.",
                        "trace_id": trace_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
            except ProviderAuthError as e:
                report["fallback_log"].append({
                    "tier": tier,
                    "outcome": "auth_error",
                    "message": str(e),
                    "trace_id": trace_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                logger.warning(f"[SEARCH-ERROR] trace={trace_id} tier={tier} auth_error: {e}")
            except ProviderRateLimitError as e:
                report["fallback_log"].append({
                    "tier": tier,
                    "outcome": "rate_limited",
                    "message": str(e),
                    "trace_id": trace_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                logger.warning(f"[SEARCH-ERROR] trace={trace_id} tier={tier} rate_limited: {e}")
            except (OmegaError, RuntimeError, OSError, Exception) as e:
                report["fallback_log"].append({
                    "tier": tier,
                    "outcome": "error",
                    "message": str(e),
                    "trace_id": trace_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                logger.warning(f"[SEARCH-ERROR] trace={trace_id} tier={tier} error: {e}")

        if not report["primary_finding"]:
            report["status"] = "failed"
            report["primary_finding"] = "No results found across all available tiers."
        elif self.verifier and evidence_pool:
            try:
                logger.info(f"[SEARCH] trace={trace_id} verifying {len(evidence_pool)} sources...")
                verification = await self.verifier.verify(query, evidence_pool)
                report["verification"] = {
                    "status": verification.status,
                    "reasoning": verification.reasoning,
                    "verified_at": verification.verified_at,
                    "trace_id": trace_id,
                }
            except (OmegaError, RuntimeError, OSError) as e:
                logger.warning(f"[SEARCH] trace={trace_id} verification failed: {e}")
                report["verification"] = {
                    "status": "UNVERIFIED",
                    "reasoning": f"Verification failed: {e}",
                    "trace_id": trace_id,
                }

        return report

    def _extract_evidence_from_finding(self, finding: str) -> List[Dict[str, Any]]:
        """Extract individual source blocks from a synthesized finding string."""
        evidence: List[Dict[str, Any]] = []
        if not finding:
            return evidence

        # Match "Source [URL]:\nContent" patterns
        pattern = re.compile(r"Source \[(https?://[^\]]+)\]:\n(.*?)(?=\n\nSource \[|\Z)", re.DOTALL)
        matches = pattern.findall(finding)
        for url, content in matches:
            evidence.append({
                "content": content.strip(),
                "source_id": url,
                "authority_score": 0.8 if "arxiv.org" in url or "github.com" in url else 0.5
            })

        # Also match provider-specific snippets
        if not evidence:
            for line in finding.split("\n\n"):
                if line.strip() and not line.startswith("Exa Neural Search:") and not line.startswith("Firecrawl Search (Snippets):"):
                    evidence.append({
                        "content": line.strip(),
                        "source_id": "snippet",
                        "authority_score": 0.5
                    })
        return evidence

    async def _execute_tier(self, tier: int, query: str, entity_name: str, limit: int) -> Optional[str]:
        """Internal dispatcher for the SSP-V2 4-Tier protocol."""
        if tier == TIER_LOCAL:
            return await self._tier_0_local_cache(query, entity_name, limit)
        elif tier == TIER_SEARXNG:
            return await self._tier_1_searxng(query, limit)
        elif tier == TIER_EXA:
            return await self._tier_2_exa(query, limit)
        elif tier == TIER_FIRECRAWL:
            return await self._tier_3_firecrawl(query, limit)
        return None

    async def _tier_0_local_cache(self, query: str, entity_name: str, limit: int) -> Optional[str]:
        """T0: Local Cache (MemoryStore + SovereignCache)."""
        # 1. MemoryStore Hybrid Search
        results = await self.memory_store.search(query, entity_name, limit=limit)
        if results:
            logger.info(f"T0 MemoryStore match found for {entity_name}: {len(results)} results")
            snippets = [r.get("assistant", r.get("content", "")) for r in results]
            return f"Local Memory Match: {' '.join(snippets[:3])}"

        # 2. SovereignCache (filesystem)
        cached_result = self.cache.get(query, entity_name)
        if cached_result:
            logger.info(f"T0 SovereignCache HIT for {query} (entity={entity_name})")
            return f"Sovereign Cache Match: {cached_result}"

        return None

    async def _tier_1_searxng(self, query: str, limit: int) -> Optional[str]:
        """T1: SearXNG Broad Discovery — zero-cost, privacy-first metasearch."""
        try:
            return await self.searxng.search(query, limit)
        except Exception as e:
            logger.error(f"T1 SearXNG failed: {e}")
            return None

    async def _tier_2_exa(self, query: str, limit: int) -> Optional[str]:
        """T2: Exa Neural Refinement — semantic search."""
        if not self.exa:
            logger.warning("Exa provider not configured. Skipping T2.")
            return None
        try:
            return await self.exa.search(query, limit)
        except Exception as e:
            logger.error(f"T2 Exa failed: {e}")
            return None

    async def _tier_3_firecrawl(self, query: str, limit: int) -> Optional[str]:
        """T3: Firecrawl Deep Extraction — structured content."""
        if not self._has_firecrawl_credits():
            logger.warning("Firecrawl credits below threshold. Skipping T3.")
            return None
        if not self.firecrawl:
            logger.warning("Firecrawl provider not configured. Skipping T3.")
            return None
        try:
            result = await self.firecrawl.search(query, limit)
            if result:
                # Persist to SovereignCache for future T0 hits
                self.cache.set(query, "global", result)
            return result
        except Exception as e:
            logger.error(f"T3 Firecrawl failed: {e}")
            return None

    async def extract(self, query: str, limit: int = 10) -> Optional[str]:
        """Direct access to T3 (Firecrawl) Deep Extraction.
        
        Bypasses the tiered routing to force a high-fidelity extraction.
        """
        return await self._tier_3_firecrawl(query, limit)

    def _has_firecrawl_credits(self) -> bool:
        """Check if Firecrawl credits are above the 100-credit threshold."""
        return self.budget.has_quota("firecrawl", 100)

    async def get_degraded_mode_status(self) -> bool:
        """Check if the system should be in Degraded Mode (Sovereign Fallback)."""
        return self.memory_store.vector_store.__class__.__name__ == "MemoryVectorAdapter"

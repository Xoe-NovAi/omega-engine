"""Sovereign Search Service — Core implementation of the 5-Tier Search Protocol.
AP: AP-SOVEREIGN-SEARCH-SERVICE-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: HERMES | CONTEXT: SEARCH-PARTNERSHIP]
"""
from __future__ import annotations

import logging
import anyio
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime

from omega.errors import (
    OmegaError, ProviderError, ProviderRateLimitError, 
    ProviderUnavailableError, ProviderAuthError
)
from omega.memory_store import get_memory_store, MemoryStore
from omega.library.indexer import Indexer
from omega.oracle.search_providers import FirecrawlProvider, ExaProvider

logger = logging.getLogger(__name__)

class SovereignSearchService:
    """
    Core engine service implementing the Sovereign Search Protocol (SSP).
    
    The SSP ensures absolute resilience and credit efficiency by executing 
    search operations across a 5-tier hierarchy:
    T0: Local Cache (.firecrawl/ + MemoryStore Hybrid)
    T1: WebSearch (Broad Discovery)
    T2: Firecrawl (Deep Extraction)
    T3: Omega Hub (Sovereign Gnosis)
    T4: Neural Search (Exa/Tavily)
    """

    def __init__(
        self, 
        memory_store: Optional[MemoryStore] = None,
        model_gateway: Optional['ModelGateway'] = None,
        indexer: Optional[Indexer] = None,
        firecrawl_key: Optional[str] = None,
        exa_key: Optional[str] = None
    ):
        from omega.oracle.model_gateway import ModelGateway
        self.memory_store = memory_store or get_memory_store()
        self.model_gateway = model_gateway or ModelGateway()
        self.indexer = indexer or Indexer()
        self.cache_dir = Path(".firecrawl")
        self.cache_dir.mkdir(exist_ok=True)

        
        # Initialize Direct Providers (Bypass MCP Bridge)
        self.firecrawl = FirecrawlProvider(firecrawl_key) if firecrawl_key else None
        self.exa = ExaProvider(exa_key) if exa_key else None

    async def search(
        self, 
        query: str, 
        entity_name: str, 
        limit: int = 10,
        max_tier: int = 4,
        force_tier: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute the 5-Tier Sovereign Search Protocol.
        
        Returns a report containing the primary finding, evidence, and fallback log.
        """
        report = {
            "primary_finding": None,
            "evidence": [],
            "fallback_log": [],
            "final_tier": None,
            "status": "pending"
        }

        if force_tier is not None:
            tier = force_tier
            result = await self._execute_tier(tier, query, entity_name, limit)
            if result:
                report["primary_finding"] = result
                report["final_tier"] = tier
                report["status"] = "success"
            return report

        # Sequential Tier Execution
        for tier in range(max_tier + 1):
            try:
                result = await self._execute_tier(tier, query, entity_name, limit)
                if result:
                    report["primary_finding"] = result
                    report["final_tier"] = tier
                    report["status"] = "success"
                    break
                else:
                    report["fallback_log"].append(f"Tier {tier} returned no results.")
            except Exception as e:
                report["fallback_log"].append(f"Tier {tier} failed: {str(e)}")
                logger.warning(f"[SEARCH-ERROR] tier={tier} error={str(e)}")

        if not report["primary_finding"]:
            report["status"] = "failed"
            report["primary_finding"] = "No results found across all available tiers."

        return report

    async def _execute_tier(self, tier: int, query: str, entity_name: str, limit: int) -> Optional[str]:
        """Internal dispatcher for the 5-Tier protocol."""
        if tier == 0:
            return await self._tier_0_local_cache(query, entity_name, limit)
        elif tier == 1:
            return await self._tier_1_websearch(query, limit)
        elif tier == 2:
            return await self._tier_2_firecrawl(query, limit)
        elif tier == 3:
            return await self._tier_3_omega_hub(query, entity_name, limit)
        elif tier == 4:
            return await self._tier_4_neural_search(query, limit)
        return None

    async def _tier_0_local_cache(self, query: str, entity_name: str, limit: int) -> Optional[str]:
        """T0: Local Cache (.firecrawl/ + MemoryStore Hybrid)."""
        # 1. Check .firecrawl/ cache
        # Simplified: Search for files containing query keywords
        # In production, this would use a proper index of the .firecrawl/ directory
        
        # 2. MemoryStore Hybrid Search (The "Sovereign" part of T0)
        results = await self.memory_store.search(query, entity_name, limit=limit)
        if results:
            logger.info(f"T0 match found for {entity_name}: {len(results)} results")
            # Synthesize the top results into a finding
            snippets = [r.get("assistant", r.get("content", "")) for r in results]
            return f"Local Memory Match: {' '.join(snippets[:3])}"
        
        return None

    async def _tier_1_websearch(self, query: str, limit: int) -> Optional[str]:
        """T1: WebSearch (Broad Discovery)."""
        # This would call the 'websearch' provider via ModelGateway or a dedicated SearchProvider
        # For now, we simulate the call to the provider fabric
        try:
            # We assume a provider named 'websearch' exists in the fabric
            # result = await self.model_gateway.generate(model="websearch", ...)
            return None # Placeholder for actual provider integration
        except Exception as e:
            logger.error(f"T1 WebSearch failed: {e}")
            return None

    async def _tier_2_firecrawl(self, query: str, limit: int) -> Optional[str]:
        """T2: Firecrawl (Deep Extraction)."""
        if not self.firecrawl:
            logger.warning("Firecrawl provider not configured. Skipping T2.")
            return None
        
        try:
            return await self.firecrawl.search(query, limit)
        except Exception as e:
            logger.error(f"T2 Firecrawl failed: {e}")
            return None

    async def _tier_3_omega_hub(self, query: str, entity_name: str, limit: int) -> Optional[str]:
        """T3: Omega Hub (Sovereign Gnosis)."""
        try:
            # Use the Indexer's hybrid search
            results = await self.indexer.hybrid_search(query, domain=entity_name, limit=limit)
            if results:
                snippets = [r.get("summary", r.get("body", "")) for r in results]
                return f"Omega Hub Gnosis: {' '.join(snippets[:3])}"
        except Exception as e:
            logger.error(f"T3 Omega Hub failed: {e}")
        return None

    async def _tier_4_neural_search(self, query: str, limit: int) -> Optional[str]:
        """T4: Neural Search (Exa/Tavily)."""
        if not self.exa:
            logger.warning("Exa provider not configured. Skipping T4.")
            return None
            
        try:
            return await self.exa.search(query, limit)
        except Exception as e:
            logger.error(f"T4 Neural Search failed: {e}")
            return None

    def _has_firecrawl_credits(self) -> bool:
        """Check if Firecrawl credits are above the 100-credit threshold."""
        # In a real implementation, this would call the Firecrawl API /status
        # For now, we assume True or check an env var
        return True

    async def get_degraded_mode_status(self) -> bool:
        """Check if the system should be in Degraded Mode (Sovereign Fallback)."""
        # Degraded mode is active if all cloud providers are unavailable
        # and we are relying solely on MemoryVectorAdapter.
        return self.memory_store.vector_store.__class__.__name__ == "MemoryVectorAdapter"

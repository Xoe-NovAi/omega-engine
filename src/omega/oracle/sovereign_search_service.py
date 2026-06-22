"""Sovereign Search Service — Core implementation of the 5-Tier Search Protocol.
# [id-soft: doom-1993] Lattice-Culling — tiered search dispatch
AP: AP-SOVEREIGN-SEARCH-SERVICE-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: HERMES | CONTEXT: SEARCH-PARTNERSHIP]
"""
from __future__ import annotations

import logging
import anyio
import re
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
from omega.oracle.skeptical_verifier import SkepticalVerifier

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
     T4: Neural Search (Exa)
    """

    def __init__(
        self, 
        memory_store: Optional[MemoryStore] = None,
        model_gateway: Any = None,
        indexer: Optional[Indexer] = None,
        firecrawl_key: Optional[str] = None,
        exa_key: Optional[str] = None,
        verifier: Optional[SkepticalVerifier] = None
    ):
        from omega.oracle.model_gateway import ModelGateway
        from omega.oracle.health_monitor import get_health_monitor
        self.memory_store = memory_store or get_memory_store()
        self.model_gateway = model_gateway or ModelGateway(health_monitor=get_health_monitor())
        self.indexer = indexer or Indexer()
        self.cache_dir = Path(".firecrawl")
        self.cache_dir.mkdir(exist_ok=True)

        
        # Initialize Direct Providers (Bypass MCP Bridge)
        self.firecrawl = FirecrawlProvider(firecrawl_key) if firecrawl_key else None
        self.exa = ExaProvider(exa_key) if exa_key else None
        self.verifier = verifier or SkepticalVerifier(self.model_gateway)

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
            "status": "pending",
            "verification": None
        }

        evidence_pool = []

        if force_tier is not None:
            tier = force_tier
            result = await self._execute_tier(tier, query, entity_name, limit)
            if result:
                report["primary_finding"] = result
                report["final_tier"] = tier
                report["status"] = "success"
                evidence_pool.extend(self._extract_evidence_from_finding(result))
        else:
            # Sequential Tier Execution
            for tier in range(max_tier + 1):
                try:
                    result = await self._execute_tier(tier, query, entity_name, limit)
                    if result:
                        report["primary_finding"] = result
                        report["final_tier"] = tier
                        report["status"] = "success"
                        evidence_pool.extend(self._extract_evidence_from_finding(result))
                        break
                    else:
                        report["fallback_log"].append(f"Tier {tier} returned no results.")
                except Exception as e:
                    report["fallback_log"].append(f"Tier {tier} failed: {str(e)}")
                    logger.warning(f"[SEARCH-ERROR] tier={tier} error={str(e)}")

        if not report["primary_finding"]:
            report["status"] = "failed"
            report["primary_finding"] = "No results found across all available tiers."
        elif self.verifier and evidence_pool:
            try:
                logger.info(f"Running skeptical verification on search findings with {len(evidence_pool)} sources...")
                verification = await self.verifier.verify(query, evidence_pool)
                report["verification"] = {
                    "status": verification.status,
                    "reasoning": verification.reasoning,
                    "verified_at": verification.verified_at
                }
            except Exception as e:
                logger.warning(f"Skeptical verification failed: {e}")
                report["verification"] = {
                    "status": "UNVERIFIED",
                    "reasoning": f"Verification failed: {e}"
                }

        return report

    def _extract_evidence_from_finding(self, finding: str) -> List[Dict[str, Any]]:
        """Extract individual source blocks from a synthesized finding string."""
        evidence = []
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
            
        # Also match "Exa Neural Search" or "Local Memory Match" snippets if any
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

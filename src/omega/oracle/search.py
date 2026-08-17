"""Sovereign Search Engine — Semantic Retrieval for Omega.
AP: AP-SOVEREIGN-SEARCH-v1.0.0
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

import logging
from typing import Any, Dict, List, Optional
from ..memory_store import get_memory_store
from .security import TDPGate, TaintedData
from .sovereign_search_service import SovereignSearchService

logger = logging.getLogger(__name__)


class SovereignSearcher:
    """Sovereign Search Wrapper.

    Wires the high-level Sovereign Search Protocol (SSP) to the
    underlying SovereignSearchService.
    """

    def __init__(self, memory_store=None):
        self.memory_store = memory_store or get_memory_store()
        self.service = SovereignSearchService(memory_store=self.memory_store)

    async def search_knowledge(
        self, entity_name: str, query: str, limit: int = 5, filter: Optional[Dict[str, Any]] = None
    ) -> List[TaintedData]:
        """Perform a sovereign search across all tiers and return TaintedData.

        This replaces the old semantic-only search with the full 5-Tier Protocol.
        """
        # 1. Execute the 5-Tier Protocol via the service
        report = await self.service.search(query, entity_name, limit=limit)

        if not report["primary_finding"]:
            return []

        # 2. Wrap the finding in TaintedData for security
        # In a full implementation, we would return multiple snippets from the evidence list.
        return [
            TaintedData(
                content=report["primary_finding"],
                source=f"SovereignSearch (Tier {report['final_tier']})",
                metadata={"report": report},
                taint_level=1,
            )
        ]

    def format_knowledge_block(self, results: List[TaintedData]) -> str:
        """Format search results into an isolated knowledge block for the prompt."""
        if not results:
            return ""

        blocks = []
        for i, res in enumerate(results, 1):
            # Use TDPGate to isolate each snippet
            isolated = TDPGate.isolate(res)
            blocks.append(f"Knowledge Source {i}:\n{isolated}")

        return "## Relevant Knowledge\n\n" + "\n\n".join(blocks) + "\n\n---\n"

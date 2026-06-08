"""Sovereign Search Engine — Semantic Retrieval for Omega.
AP: AP-SOVEREIGN-SEARCH-v1.0.0
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from ..memory_store import get_memory_store
from .security import TDPGate, TaintedData

logger = logging.getLogger(__name__)

class SovereignSearcher:
    """Implements the Thin-Client Search Pattern for RAM-efficient retrieval.
    
    Instead of loading large documents, it performs a semantic query via 
    the IVectorStoreAdapter, reranks the results, and returns only the 
    most relevant snippets.
    """

    def __init__(self, memory_store=None):
        self.memory_store = memory_store or get_memory_store()

    async def search_knowledge(
        self, 
        entity_name: str, 
        query_vector: List[float], 
        limit: int = 5, 
        filter: Optional[Dict[str, Any]] = None
    ) -> List[TaintedData]:
        """Perform a semantic search and return results as TaintedData.
        
        Args:
            entity_name: The entity to search within.
            query_vector: The embedding of the search query.
            limit: Number of results to return.
            filter: Additional metadata filters.
            
        Returns:
            A list of TaintedData objects containing the most relevant snippets.
        """
        if not self.memory_store.vector_store:
            logger.warning("No vector store configured; skipping semantic search.")
            return []

        try:
            # 1. Semantic Search (The "Thin" part: get IDs and scores first)
            results = await self.memory_store.vector_store.query(
                entity_name=entity_name,
                vector=query_vector,
                limit=limit * 2, # Fetch more for reranking
                filter=filter
            )

            if not results:
                return []

            # 2. Reranking (Simple score-based for now, can be upgraded to Cross-Encoder)
            # results is List[Tuple[score, payload]]
            results.sort(key=lambda x: x[0], reverse=True)
            top_results = results[:limit]

            # 3. Wrap in TaintedData for security
            tainted_results = []
            for score, payload in top_results:
                content = payload.get("content", payload.get("text", ""))
                if content:
                    tainted_results.append(TaintedData(
                        content=content,
                        source=f"SemanticMemory (score={score:.4f})",
                        metadata=payload,
                        taint_level=1
                    ))
            
            return tainted_results

        except Exception as e:
            logger.error(f"SovereignSearcher failed for {entity_name}: {e}", exc_info=True)
            return []

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

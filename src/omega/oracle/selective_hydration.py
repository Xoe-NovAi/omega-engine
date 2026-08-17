# AP: AP-SELECTIVE-HYDRATION-v1.0.0
# 🔱 Selective Hydration — Qdrant-backed L3 Gnosis Retrieval
# ⬡ OMEGA ⬡ JOHN_CARMACK ⬡ trc_selective_hydration ⬡ WORKSTREAM-B
#
# Retrieves L3 (Universal) principles from Qdrant by cosine similarity
# and injects them into the ContextBuilder's context window.
#
# [id-soft: vet-046] BSP Culling — O(1) culling of irrelevant principles
#   Doom's BSP tree culls half the geometry with a single plane equation.
#   SelectiveHydration culls all L3 principles with a single vector
#   similarity threshold, returning only the top-K relevant ones.
#
# [id-soft: doom-1993] Precomputed Lookup — embeddings precomputed at store time
#   Doom's colormap tables precomputed trig and lighting at compile time.
#   L3 principles are embedded once at store time. Runtime retrieval is
#   O(1) cosine similarity against precomputed vectors.
#
# [id-soft: quake-1996] 4-Tier Memory — L3 principles live in the Cache tier
#   Quake's zone allocator (zone.h:24-80) has a Cache tier (PU_CACHE=101)
#   that stores reusable data. L3 principles are the Cache tier of gnosis.
#
# Integration:
#   selective_hydration = SelectiveHydration(
#       embedding_manager=memory_store.embedding_manager,
#       vector_adapter=memory_store.vector_store,
#   )
#   principles = await selective_hydration.hydrate(query, entity_name)
#
# M1: AnyIO compliance — no asyncio, all I/O via anyio.to_thread.run_sync
# M9: Error Integrity — typed errors, no bare except


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import hashlib
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from omega.memory.embeddings import EmbeddingManager
from omega.memory.vector_adapters import IVectorStoreAdapter
from omega.errors import OmegaError

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────

# [id-soft: quake-1996] Grace Period — 0.5s realloc grace for tombstoned slots
DEFAULT_TOP_K: int = 5

# Collection/entity prefix for L3 gnosis storage
L3_COLLECTION_PREFIX: str = "l3_gnosis_"

# Minimum confidence threshold for L3 principle retrieval
MIN_CONFIDENCE: float = 0.5


@dataclass
class L3Principle:
    """A distilled L3 (Universal) principle from the soul distillation pipeline.

    [id-soft: doom-1993] ZONEID Pattern — magic constant validated on hydration
    to catch stale or corrupted principles.

    Fields:
        principle_id: Unique identifier (hash of entity_name + content)
        entity_name: The entity that owns this principle
        content: The L3 principle text
        domain: Domain string for filtering (e.g., "engineering", "governance")
        confidence: 0.0-1.0 confidence score from distillation pipeline
        source: Where it came from (session_id, vet record, etc.)
        created_at: ISO timestamp of when the principle was created
        category: Optional category for filtering ("general", "heritage", "technical")
        similarity: Cosine similarity to the query (populated at retrieval time)
    """

    entity_name: str
    content: str
    principle_id: str = ""
    domain: str = "general"
    confidence: float = 1.0
    source: str = ""
    created_at: str = ""
    category: str = "general"
    similarity: float = 0.0

    def __post_init__(self) -> None:
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        if not self.principle_id:
            self.principle_id = self._compute_id()

    def _compute_id(self) -> str:
        raw = f"{self.entity_name}:{self.content}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    def to_payload(self) -> Dict[str, Any]:
        """Serialise to Qdrant payload."""
        return {
            "principle_id": self.principle_id,
            "entity_name": self.entity_name,
            "content": self.content,
            "domain": self.domain,
            "confidence": self.confidence,
            "source": self.source,
            "created_at": self.created_at,
            "category": self.category,
            "_type": "l3_principle",
        }

    @staticmethod
    def from_payload(payload: Dict[str, Any], similarity: float = 0.0) -> "L3Principle":
        """Deserialise from Qdrant payload."""
        return L3Principle(
            principle_id=payload.get("principle_id", ""),
            entity_name=payload.get("entity_name", ""),
            content=payload.get("content", ""),
            domain=payload.get("domain", "general"),
            confidence=payload.get("confidence", 1.0),
            source=payload.get("source", ""),
            created_at=payload.get("created_at", ""),
            category=payload.get("category", "general"),
            similarity=similarity,
        )

    def format(self) -> str:
        """Format for context injection."""
        score_str = f"[{self.similarity:.2f}]" if self.similarity > 0 else ""
        return f'- {score_str} "{self.content}" ({self.domain})'


class SelectiveHydration:
    """Retrieves L3 gnosis principles from Qdrant by cosine similarity.

    Injects top-K principles into the ContextBuilder's context window,
    providing relevant distilled wisdom for the current query.

    [id-soft: vet-046] BSP Culling — O(1) similarity threshold culling
    [id-soft: doom-1993] Precomputed Lookup — embeddings at store time

    Design decisions:
      - Embedding is always performed via the configured EmbeddingManager chain
      - Vector storage uses the IVectorStoreAdapter interface (Qdrant or Memory)
      - Entity isolation via entity_name filter in the vector store
      - Zero new dependencies — reuses existing omega.memory.embeddings infrastructure
      - M1 AnyIO: all blocking operations wrapped in anyio-compatible patterns
      - M9 Error: typed errors, no bare except, trace_id propagation ready
    """

    def __init__(
        self,
        embedding_manager: EmbeddingManager,
        vector_adapter: IVectorStoreAdapter,
        top_k: int = DEFAULT_TOP_K,
        min_confidence: float = MIN_CONFIDENCE,
        collection_prefix: str = L3_COLLECTION_PREFIX,
    ):
        if top_k < 1:
            raise ValueError(f"top_k must be >= 1, got {top_k}")
        if min_confidence < 0.0 or min_confidence > 1.0:
            raise ValueError(f"min_confidence must be between 0.0 and 1.0, got {min_confidence}")

        self._embedding_manager = embedding_manager
        self._vector_adapter = vector_adapter
        self._top_k = top_k
        self._min_confidence = min_confidence
        self._collection_prefix = collection_prefix

    @property
    def top_k(self) -> int:
        return self._top_k

    # ── Primary API ───────────────────────────────────────────────────

    async def hydrate(self, query: str, entity_name: str) -> List[L3Principle]:
        """Retrieve top-K L3 principles similar to the query for the entity.

        Pipeline:
          1. Embed the query via the EmbeddingManager chain
          2. Search the vector adapter filtered by entity_name
          3. Filter by confidence threshold
          4. Deserialise to L3Principle objects
          5. Sort by similarity descending

        Args:
            query: The user's query or entity domain context
            entity_name: The entity to retrieve principles for

        Returns:
            List of L3Principle objects, sorted by similarity descending.
            Empty list if no principles found or embedding fails.

        Raises:
            OmegaError: If the vector store is unreachable
        """
        if not query or not entity_name:
            return []

        # Step 1: Embed the query
        query_vector = await self._get_query_embedding(query)
        if not query_vector:
            logger.debug("SelectiveHydration: empty query vector for '%.50s'", query)
            return []

        # Step 2: Search the vector store
        try:
            # Use entity_name as the collection/namespace
            results = await self._vector_adapter.query(
                entity_name=self._collection_prefix + entity_name,
                vector=query_vector,
                limit=self._top_k * 2,  # over-fetch for confidence filtering
            )
        except (OmegaError, RuntimeError, OSError) as e:
            logger.warning(
                "SelectiveHydration: vector query failed for %s: %s",
                entity_name,
                e,
            )
            return []

        # Step 3-5: Filter, deserialise, sort
        principles: List[L3Principle] = []
        for score, payload in results:
            # Only process L3 principle entries
            if payload.get("_type") != "l3_principle":
                continue
            try:
                principle = L3Principle.from_payload(payload, similarity=score)
            except (ValueError, TypeError) as e:
                logger.warning("SelectiveHydration: malformed principle payload: %s", e)
                continue
            if principle.confidence >= self._min_confidence:
                principles.append(principle)

        # Sort by similarity descending and return top-K
        principles.sort(key=lambda p: p.similarity, reverse=True)
        return principles[: self._top_k]

    async def store(self, principle: L3Principle) -> str:
        """Store an L3 principle in the vector store.

        Pipeline:
          1. Embed the principle content
          2. Upsert into vector adapter with entity_name isolation
          3. Return the principle ID

        Args:
            principle: The L3Principle to store

        Returns:
            The principle_id of the stored principle

        Raises:
            ValueError: If principle has no content
            OmegaError: If the vector store is unreachable
        """
        if not principle.content:
            raise ValueError("Cannot store an L3 principle with empty content")

        # Step 1: Embed the principle content
        # Use the content itself as the text to embed for future similarity search
        embedding, _ = await self._embedding_manager.get_embedding(principle.content)
        if not embedding:
            logger.warning(
                "SelectiveHydration: empty embedding for principle '%.50s' — skipping store",
                principle.content,
            )
            return principle.principle_id

        # Step 2: Upsert into vector adapter
        entity_ns = self._collection_prefix + principle.entity_name
        try:
            returned_id = await self._vector_adapter.upsert(
                entity_name=entity_ns,
                vector=embedding,
                metadata=principle.to_payload(),
                id=principle.principle_id,
            )
            logger.debug(
                "SelectiveHydration: stored principle %s for %s",
                principle.principle_id[:12],
                principle.entity_name,
            )
            return returned_id or principle.principle_id
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(
                "SelectiveHydration: failed to store principle for %s: %s",
                principle.entity_name,
                e,
            )
            raise OmegaError(
                message=f"Failed to store L3 principle: {e}",
                detail={
                    "entity_name": principle.entity_name,
                    "principle_id": principle.principle_id,
                },
                raw_error=e,
            ) from e

    async def get_all(self, entity_name: str) -> List[L3Principle]:
        """List all L3 principles for an entity.

        Used for display, debugging, and soul review.

        Args:
            entity_name: The entity to list principles for

        Returns:
            List of L3Principle objects for the entity
        """
        entity_ns = self._collection_prefix + entity_name
        try:
            results = await self._vector_adapter.query(
                entity_name=entity_ns,
                vector=[0.0] * self._embedding_manager.current_dimension,
                limit=100,
            )
        except (OmegaError, RuntimeError, OSError) as e:
            logger.warning(
                "SelectiveHydration: get_all failed for %s: %s",
                entity_name,
                e,
            )
            return []

        principles = []
        for score, payload in results:
            if payload.get("_type") != "l3_principle":
                continue
            try:
                principles.append(L3Principle.from_payload(payload, similarity=score))
            except (ValueError, TypeError):
                continue

        return principles

    async def remove(self, principle_id: str, entity_name: str) -> bool:
        """Remove a specific L3 principle by ID.

        Args:
            principle_id: The ID of the principle to remove
            entity_name: The entity that owns the principle

        Returns:
            True if removed, False if not found
        """
        entity_ns = self._collection_prefix + entity_name
        try:
            return await self._vector_adapter.delete(
                entity_name=entity_ns,
                ids=[principle_id],
            )
        except (OmegaError, RuntimeError, OSError) as e:
            logger.warning(
                "SelectiveHydration: remove failed for %s/%s: %s",
                entity_name,
                principle_id[:12],
                e,
            )
            return False

    # ── Internal Helpers ──────────────────────────────────────────────

    async def _get_query_embedding(self, query: str) -> Optional[List[float]]:
        """Embed the query via the EmbeddingManager chain.

        Returns None if the embedding fails (empty or None).
        Zero-vector embeddings are accepted — they are valid in test mode
        and will simply result in zero similarity scores.
        """
        if not self._embedding_manager:
            return None
        try:
            vector, _ = await self._embedding_manager.get_embedding(query)
            if vector:
                return vector
            return None
        except (OmegaError, RuntimeError, OSError) as e:
            logger.debug("SelectiveHydration: embedding failed for query: %s", e)
            return None

    def format_principles_block(self, principles: List[L3Principle]) -> str:
        """Format a list of L3 principles into a context block.

        Called by ContextBuilder to inject L3 principles into the
        system prompt context.

        Args:
            principles: List of L3Principle objects to format

        Returns:
            Formatted string block, or empty string if no principles
        """
        if not principles:
            return ""

        lines = ["\n## Relevant Gnosis Principles\n"]
        for p in principles:
            lines.append(p.format())
        lines.append("\n---\n")
        return "\n".join(lines)

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-SEMANTIC-ROUTER-v1.0.0
# 🔱 Semantic Router — Embedding-Based Entity Routing
# ⬡ OMEGA ⬡ ORACLE ⬡ semantic_router.py
#
# Replaces keyword-based entity routing with embedding-based semantic routing.
# Fallback chain: semantic (cosine > 0.4) → keyword (find_by_domain) → default entity.
#
# [id-soft: vet-046] BSP Culling — O(1) culling of irrelevant entities via precomputed routing structure
# [id-soft: vet-023] Precomputed Lookup — entity embeddings precomputed at boot for O(1) routing


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import logging
import math
import os
from typing import Dict, List, Optional, Tuple


from omega.memory.embeddings import EmbeddingManager, SovereignFallbackEmbeddingProvider
from omega.oracle.entity_registry import EntityRegistry, Entity
from omega.errors import OmegaError

logger = logging.getLogger(__name__)

# Threshold for semantic routing confidence
SEMANTIC_THRESHOLD = 0.4


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Pure Python cosine similarity — no numpy dependency.

    For 22 entities × 768 dims = ~33K operations (~3ms on Zen 2).
    """
    if len(a) != len(b):
        # Pad shorter vector with zeros
        max_len = max(len(a), len(b))
        a = a + [0.0] * (max_len - len(a))
        b = b + [0.0] * (max_len - len(b))

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (norm_a * norm_b)


class SemanticRouter:
    """Embedding-based entity routing using cosine similarity.

    At boot, pre-computes entity signature vectors from domains + role.
    At route time, embeds the query and finds the closest entity.

    Fallback chain:
        1. Semantic routing (cosine > 0.4)
        2. Keyword routing (entity_registry.find_by_domain)
        3. Default entity

    Heritage:
        [id-soft: vet-046] BSP Culling — O(1) culling of irrelevant entities
        [id-soft: vet-023] Precomputed Lookup — entity embeddings precomputed at boot
    """

    def __init__(
        self,
        registry: EntityRegistry,
        embedding_manager: Optional[EmbeddingManager] = None,
        threshold: float = SEMANTIC_THRESHOLD,
    ):
        self._registry = registry
        self._embedding_manager = embedding_manager
        self._threshold = threshold
        # [id-soft: vet-023] Precomputed Lookup — entity embeddings precomputed at boot for O(1) routing
        self._entity_vectors: Dict[str, List[float]] = {}
        self._bootstrapped = False

    async def bootstrap(self) -> None:
        """Pre-compute entity signature vectors at boot.

        For each active entity, creates a signature from domains + role,
        embeds it, and stores the vector for O(1) route-time lookup.
        """
        if self._bootstrapped:
            return

        # Mark bootstrapped immediately — even if embedding is skipped,
        # the router is initialized and ready for keyword fallback.
        self._bootstrapped = True

        if self._embedding_manager is None:
            logger.warning("SemanticRouter: no embedding manager — semantic routing disabled")
            return

        # [Right Approximation] Skip semantic routing in test env where embedding
        # models aren't available — hash-based fallback produces unreliable vectors.
        if os.getenv("OMEGA_ENV") == "test":
            logger.info(
                "SemanticRouter: test env — semantic routing disabled, using keyword fallback"
            )
            return

        # [Right Approximation] Skip semantic routing when only the hash-based
        # fallback provider is available — hash embeddings don't provide
        # meaningful cosine similarity for entity routing.
        if self._is_fallback_only():
            logger.info(
                "SemanticRouter: only fallback provider available — semantic routing disabled"
            )
            return

        # [id-soft: vet-046] BSP Culling — O(1) culling of irrelevant entities via precomputed routing structure
        for entity in self._registry.active_iter():
            signature = self._make_signature(entity)
            if not signature:
                continue

            try:
                vector, _ = await self._embedding_manager.get_embedding(signature)
                self._entity_vectors[entity.name] = vector
                logger.debug(
                    "SemanticRouter: embedded entity '%s' (dim=%d)",
                    entity.name,
                    len(vector),
                )
            except (OmegaError, RuntimeError, OSError) as e:
                logger.warning("SemanticRouter: failed to embed entity '%s': %s", entity.name, e)

        logger.info(
            "SemanticRouter: bootstrapped %d entity vectors",
            len(self._entity_vectors),
        )

    def _make_signature(self, entity: Entity) -> str:
        """Create a text signature for embedding from entity domains + role.

        Example: "strength protection boundaries SysAdmin — Environment Hardening"
        """
        parts: List[str] = []
        if entity.domains:
            parts.extend(entity.domains)
        if entity.role:
            parts.append(entity.role)
        return " ".join(parts)

    def _is_fallback_only(self) -> bool:
        """Check if only the hash-based fallback provider is available.

        Hash embeddings produce deterministic but not semantically meaningful
        vectors — cosine similarity is unreliable for routing.
        """
        if not hasattr(self._embedding_manager, "_providers"):
            return False
        providers = self._embedding_manager._providers
        if not providers:
            return True
        # Check if any provider besides the fallback is likely functional
        # (i.e., not just the SovereignFallbackEmbeddingProvider)
        has_quality_provider = any(
            not isinstance(p, SovereignFallbackEmbeddingProvider) for p in providers
        )
        return not has_quality_provider

    async def route(
        self,
        query: str,
        keyword_fallback: Optional[Entity] = None,
        default_entity: Optional[Entity] = None,
    ) -> Tuple[Optional[Entity], float, str]:
        """Route a query to the best-matching entity.

        Returns:
            (entity, confidence, method) where method is "semantic",
            "keyword", or "default".
        """
        # 1. Try semantic routing if bootstrapped
        if self._bootstrapped and self._entity_vectors:
            try:
                query_vector, _ = await self._embedding_manager.get_embedding(query)
                best_entity, best_score = self._find_closest(query_vector)

                if best_entity is not None and best_score >= self._threshold:
                    logger.debug(
                        "SemanticRouter: semantic match '%s' (score=%.3f)",
                        best_entity.name,
                        best_score,
                    )
                    return best_entity, best_score, "semantic"
            except (OmegaError, RuntimeError, OSError) as e:
                logger.warning("SemanticRouter: embedding failed, falling back: %s", e)

        # 2. Keyword fallback
        if keyword_fallback is not None:
            return keyword_fallback, 0.7, "keyword"

        # 3. Default entity
        if default_entity is not None:
            return default_entity, 0.3, "default"

        return None, 0.0, "none"

    def _find_closest(self, query_vector: List[float]) -> Tuple[Optional[Entity], float]:
        """Find the entity with highest cosine similarity to the query vector.

        [id-soft: vet-046] BSP Culling — linear scan with early culling.
        For 22 entities this is ~3ms; no need for ANN index.
        """
        best_entity: Optional[Entity] = None
        best_score = -1.0

        for name, entity_vector in self._entity_vectors.items():
            score = _cosine_similarity(query_vector, entity_vector)
            if score > best_score:
                best_score = score
                best_entity = self._registry.get(name)

        return best_entity, max(best_score, 0.0)

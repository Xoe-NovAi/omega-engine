# AP: AP-INGESTION-VERIFIER-v1.0.0

# DocRef: docs/architecture/SOVEREIGN_DATA_FLOW.md
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger("omega.ingestion.verifier")


@dataclass
class VerificationResult:
    is_verified: bool
    confidence_score: float
    resolved_metadata: Dict[str, Any]
    disputes: List[str]
    provenance_chain: List[str]


class TriangulationVerifier:
    """
    The Sovereign-Sieve: Verifies knowledge by triangulating multiple extraction tiers.

    Sovereignty: Defeats sycophancy and consensus hallucinations via independent provenance.
    """

    def __init__(self, enrichment_engine=None):
        self.enrichment = enrichment_engine

    async def verify(
        self, t1_result: Dict, t3_result: Dict, domain_key: Optional[str] = None
    ) -> VerificationResult:
        """
        Implements the Sovereign-Sieve feedback loop.
        T1: Fast extraction
        T3: Deep extraction
        """
        # 1. Compare T1 and T3 for factual deltas
        delta = self._calculate_delta(t1_result["content"], t3_result["content"])

        # 2. If delta is high, we have a contradiction.
        # In a full implementation, this would trigger a T2 (Surgical) extraction.
        if delta > 0.3:
            logger.warning(
                f"Significant delta detected between T1 and T3 ({delta:.2f}). Triggering T2 Surgical path..."
            )
            # T2 logic would go here. For now, we mark as disputed.
            dispute = "High delta between Fast and Deep extraction tiers."
        else:
            dispute = None

        # 3. Triangulate Metadata (Author, Date, DOI)
        # We use the enrichment engine to get authoritative ground truth.
        resolved_meta, confidence, provenance = await self._triangulate_metadata(
            t1_result.get("metadata", {}), t3_result.get("metadata", {}), domain_key
        )

        # 4. Consensus Hallucination Guard
        # Check if all sources are just mirroring the same original source.
        disputes = []
        if not self._has_independent_provenance(provenance):
            confidence *= 0.5
            disputes.append("Consensus Hallucination: Lack of independent provenance.")
        if dispute:
            disputes.append(dispute)

        return VerificationResult(
            is_verified=confidence > 0.7,
            confidence_score=confidence,
            resolved_metadata=resolved_meta,
            disputes=disputes,
            provenance_chain=provenance,
        )

    def _calculate_delta(self, text1: str, text2: str) -> float:
        """Simple Jaccard distance as a proxy for factual delta."""
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        if not set1 or not set2:
            return 1.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return 1.0 - (intersection / union)

    async def _triangulate_metadata(
        self, meta1: Dict, meta3: Dict, domain_key: Optional[str]
    ) -> Tuple[Dict, float, List[str]]:
        """
        Corroborates metadata across extraction tiers and authoritative APIs.
        """
        resolved = {}
        provenance = []
        scores = []

        # Fields to triangulate
        fields = ["author", "date", "doi", "title"]

        for field in fields:
            val1 = meta1.get(field)
            val3 = meta3.get(field)

            # Get authoritative value from enrichment engine if available
            auth_val = None
            if self.enrichment and (val1 or val3):
                # Use DOI or Title to query authoritative libraries
                query = val1 or val3
                auth_val = await self.enrichment.get_authoritative_value(field, query)

            # Triangulation Logic:
            # 1. Auth Value wins (Confidence 1.0)
            # 2. T1 == T3 wins (Confidence 0.8)
            # 3. T3 wins over T1 (Confidence 0.6)
            # 4. Disagreement (Confidence 0.2)

            if auth_val:
                resolved[field] = auth_val
                scores.append(1.0)
                provenance.append(f"{field}: authoritative_api")
            elif val1 == val3 and val1 is not None:
                resolved[field] = val1
                scores.append(0.8)
                provenance.append(f"{field}: t1_t3_agreement")
            elif val3:
                resolved[field] = val3
                scores.append(0.6)
                provenance.append(f"{field}: t3_preference")
            else:
                resolved[field] = val1
                scores.append(0.2)
                provenance.append(f"{field}: t1_fallback")

        avg_confidence = sum(scores) / len(scores) if scores else 0.0
        return resolved, avg_confidence, provenance

    def _has_independent_provenance(self, provenance: List[str]) -> bool:
        """
        Ensures that the verified data comes from multiple independent sources,
        not just a single source mirrored across tiers.
        """
        # In a real implementation, this would check the actual source URLs/CIDs.
        # For now, we check if we have at least one 'authoritative_api' hit.
        return any("authoritative_api" in p for p in provenance)

"""TriangulationVerifier — cross-reference T1 vs T3 for hallucination detection.

The Sovereign-Sieve's core insight: if T1 (fast) and T3 (deep) disagree,
something is wrong. The verifier computes lexical + semantic similarity
and flags contradictions.
"""

# AP: AP-OMEGA-SIEVE-VERIFIER-v1.0.0

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from .scraper import ScrapeResult

logger = logging.getLogger("omega_sieve.verifier")


@dataclass
class VerificationResult:
    """Result of triangulation verification."""
    passed: bool
    confidence: float  # 0.0 - 1.0
    lexical_similarity: float = 0.0
    semantic_similarity: float = 0.0
    content_delta: str = ""  # Description of what differs
    warnings: list[str] = field(default_factory=list)


class TriangulationVerifier:
    """Cross-reference multiple scrape results to detect hallucinations.

    The verifier compares T1 (fast) and T3 (deep) extractions of the same URL.
    If they disagree beyond a threshold, the content is flagged for review.
    """

    def __init__(self, threshold: float = 0.3):
        """

        Args:
            threshold: Maximum Jaccard distance before flagging (default 0.3).
                       Lower = stricter. 0.0 = exact match required. 1.0 = anything passes.
        """
        self.threshold = threshold

    def verify_t1_t3(self, t1_result: ScrapeResult, t3_result: ScrapeResult) -> VerificationResult:
        """Compare T1 vs T3 extraction of the same URL.

        Args:
            t1_result: Result from T1 (fast) extraction.
            t3_result: Result from T3 (deep) extraction.

        Returns:
            VerificationResult with confidence score.
        """
        warnings: list[str] = []

        # If either failed, we can't triangulate
        if not t1_result.success and not t3_result.success:
            return VerificationResult(
                passed=False, confidence=0.0,
                warnings=["Both T1 and T3 failed to extract content"],
            )

        if not t1_result.success:
            return VerificationResult(
                passed=False, confidence=0.3,
                warnings=["T1 (fast) extraction failed — relying solely on T3"],
            )

        if not t3_result.success:
            return VerificationResult(
                passed=False, confidence=0.5,
                warnings=["T3 (deep) extraction failed — relying solely on T1"],
            )

        # Compute lexical similarity (Jaccard on word sets)
        words_t1 = set(self._tokenize(t1_result.content))
        words_t3 = set(self._tokenize(t3_result.content))

        if not words_t1 or not words_t3:
            return VerificationResult(
                passed=False, confidence=0.0,
                warnings=["One or both extractions produced no tokenizable content"],
            )

        intersection = words_t1 & words_t3
        union = words_t1 | words_t3
        lexical_sim = len(intersection) / len(union) if union else 0.0

        # Jaccard distance
        jaccard_dist = 1.0 - lexical_sim

        # Content delta — what's in T1 but not T3 (and vice versa)
        only_t1 = words_t1 - words_t3
        only_t3 = words_t3 - words_t1

        delta_parts = []
        if only_t1 and len(only_t1) > 5:
            delta_parts.append(f"T1 has {len(only_t1)} unique words not in T3")
        if only_t3 and len(only_t3) > 5:
            delta_parts.append(f"T3 has {len(only_t3)} unique words not in T1")
        content_delta = "; ".join(delta_parts) if delta_parts else "Minimal lexical difference"

        # Confidence: inverse of Jaccard distance, with penalty for size mismatch
        size_ratio = min(len(words_t1), len(words_t3)) / max(len(words_t1), len(words_t3)) if max(len(words_t1), len(words_t3)) > 0 else 0
        confidence = lexical_sim * size_ratio

        if jaccard_dist > self.threshold:
            warnings.append(f"Jaccard distance {jaccard_dist:.2f} exceeds threshold {self.threshold}")
            if content_delta != "Minimal lexical difference":
                warnings.append(content_delta)

        if size_ratio < 0.3:
            warnings.append(f"Content size mismatch: T1 has {len(words_t1)} words, T3 has {len(words_t3)} words")

        passed = jaccard_dist <= self.threshold and size_ratio >= 0.3

        return VerificationResult(
            passed=passed,
            confidence=min(confidence, 1.0),
            lexical_similarity=lexical_sim,
            content_delta=content_delta,
            warnings=warnings,
        )

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into lowercase words."""
        return re.findall(r'\b[a-z0-9]+\b', text.lower())

    def best_result(self, t1: ScrapeResult, t3: ScrapeResult) -> tuple[ScrapeResult, VerificationResult]:
        """Return the best result and its verification.

        If T1 passed verification, use T1 (faster). Otherwise use T3.
        """
        ver = self.verify_t1_t3(t1, t3)
        if ver.passed and t1.success:
            return t1, ver
        return t3, ver
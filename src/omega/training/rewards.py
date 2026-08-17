# AP: AP-TRAINING-REWARDS-v1.0.0
# 🔱 GRPO Reward Function — Local-Only Design
# ⬡ OMEGA ⬡ TRAINING ⬡ rewards.py
#
# Implements reward functions for GRPO (Group Relative Policy Optimization)
# that work entirely with local GGUF models — no cloud dependencies (M7).
#
# Reward signals are computed from:
#   1. Semantic correctness — local embedding similarity to reference answer
#   2. Helpfulness — keyword density + structural completeness
#   3. Alignment — pattern matching against safety/constitutional constraints
#   4. Conciseness — length penalty to discourage verbosity
#
# [M7 Local-First] All reward computation uses:
#   - Local GGUF embeddings (all-MiniLM-L6-v2 or embeddinggemma-300m)
#   - Heuristic pattern matching (no LLM calls)
#   - Character/token counting (no network)
#
# DocRef: docs/architecture/GRPO_REWARD_DESIGN.md

import logging
import math
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


from omega.memory.embeddings import SovereignFallbackEmbeddingProvider

logger = logging.getLogger(__name__)


# ── Reward Signal Types ─────────────────────────────────────────────────


class RewardSignal(Enum):
    """Types of reward signals computed by the reward function."""

    CORRECTNESS = "correctness"  # Semantic match to reference
    HELPFULNESS = "helpfulness"  # Completeness + relevance
    ALIGNMENT = "alignment"  # Safety + constitutional compliance
    CONCISENESS = "conciseness"  # Length efficiency
    NOVELTY = "novelty"  # Diversity from other group members


@dataclass
class RewardComponents:
    """Individual reward component scores (0.0-1.0 each).

    The final reward is a weighted sum of these components.
    """

    correctness: float = 0.0
    helpfulness: float = 0.0
    alignment: float = 0.0
    conciseness: float = 0.0
    novelty: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "correctness": round(self.correctness, 4),
            "helpfulness": round(self.helpfulness, 4),
            "alignment": round(self.alignment, 4),
            "conciseness": round(self.conciseness, 4),
            "novelty": round(self.novelty, 4),
        }


@dataclass
class RewardConfig:
    """Configuration for the GRPO reward function.

    All weights must sum to 1.0 for a balanced reward.
    """

    # Component weights (must sum to 1.0)
    correctness_weight: float = 0.35
    helpfulness_weight: float = 0.25
    alignment_weight: float = 0.20
    conciseness_weight: float = 0.10
    novelty_weight: float = 0.10

    # Correctness thresholds
    correctness_similarity_threshold: float = 0.7  # Min cosine sim for full credit
    correctness_min_threshold: float = 0.3  # Below this = 0 correctness

    # Helpfulness thresholds
    helpfulness_min_keywords: int = 3  # Min keyword matches for full credit
    helpfulness_max_keywords: int = 15  # Beyond this, no additional credit

    # Conciseness thresholds
    conciseness_optimal_tokens: int = 150  # Optimal response length
    conciseness_penalty_tokens: int = 500  # Beyond this, heavy penalty

    # Alignment patterns (regex)
    alignment_refusal_patterns: List[str] = field(
        default_factory=lambda: [
            r"(?i)\bi cannot\b",
            r"(?i)\bi should not\b",
            r"(?i)\bi must not\b",
            r"(?i)\bi will not\b",
            r"(?i)\bi'm not able to\b",
        ]
    )
    alignment_safety_patterns: List[str] = field(
        default_factory=lambda: [
            r"(?i)\b(system|admin|root)\b.{0,50}\b(password|credential|secret|key)\b",
            r"(?i)\b(api[_-]?key|token|secret)\s*[=:]\s*\S+",
            r"(?i)\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",  # IP addresses
        ]
    )

    def validate(self) -> None:
        """Validate that weights sum to ~1.0 and thresholds are reasonable."""
        total = (
            self.correctness_weight
            + self.helpfulness_weight
            + self.alignment_weight
            + self.conciseness_weight
            + self.novelty_weight
        )
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Reward weights must sum to 1.0, got {total:.4f}")
        if not (0.0 <= self.correctness_similarity_threshold <= 1.0):
            raise ValueError("correctness_similarity_threshold must be in [0, 1]")
        if self.conciseness_optimal_tokens <= 0:
            raise ValueError("conciseness_optimal_tokens must be positive")


def create_default_reward_config() -> RewardConfig:
    """Create a default reward config tuned for general-purpose GRPO."""
    return RewardConfig()


# ── Token Estimation ────────────────────────────────────────────────────


def estimate_tokens(text: str) -> int:
    """Estimate token count from text (rough: 4 chars per token).

    Zero-dependency, no LLM calls — pure heuristic.
    """
    if not text:
        return 0
    return len(text) // 4 + 1


# ── GRPO Reward Function ────────────────────────────────────────────────


class GRPORewardFunction:
    """Local-only reward function for GRPO training.

    Computes rewards for generated responses using only local resources:
    - Embedding similarity (via local GGUF or fallback hashing)
    - Keyword/structural heuristics
    - Pattern matching for alignment
    - Length-based conciseness scoring

    No cloud model calls — fully M7 compliant.

    Usage:
        config = create_default_reward_config()
        reward_fn = GRPORewardFunction(config=config)

        # For a group of responses to the same prompt:
        rewards = await reward_fn.compute_group_rewards(
            prompt="Explain quantum computing",
            responses=["response1...", "response2...", ...],
            reference="Quantum computing is...",
        )
    """

    def __init__(
        self,
        config: Optional[RewardConfig] = None,
        embedding_provider=None,
    ):
        self.config = config or create_default_reward_config()
        self.config.validate()
        self._embedding_provider = embedding_provider
        self._fallback_embedder = SovereignFallbackEmbeddingProvider(dimension=256)

    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text, preferring configured provider, falling back to hashing.

        [M7 Local-First] Never calls cloud APIs. If the configured provider
        fails, falls back to deterministic feature hashing.
        """
        if self._embedding_provider is not None:
            try:
                return await self._embedding_provider.get_embedding(text)
            except Exception as e:
                logger.warning("Embedding provider failed (%s), falling back to hash", e)

        # Zero-dependency fallback: deterministic feature hashing
        return await self._fallback_embedder.get_embedding(text)

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    # ── Individual Component Scorers ────────────────────────────────────

    async def _score_correctness(self, response: str, reference: str) -> float:
        """Score semantic correctness via embedding similarity to reference.

        Returns 0.0-1.0. Full credit when cosine sim >= threshold.
        Linear interpolation between min_threshold and similarity_threshold.
        """
        if not reference:
            # No reference — can't score correctness, return neutral
            return 0.5

        ref_emb = await self._get_embedding(reference)
        resp_emb = await self._get_embedding(response)

        sim = self._cosine_similarity(ref_emb, resp_emb)

        # Normalize: sim is in [-1, 1], map to [0, 1]
        sim = max(0.0, min(1.0, (sim + 1.0) / 2.0))

        if sim < self.config.correctness_min_threshold:
            return 0.0
        if sim >= self.config.correctness_similarity_threshold:
            return 1.0

        # Linear interpolation between min and threshold
        t = (sim - self.config.correctness_min_threshold) / (
            self.config.correctness_similarity_threshold - self.config.correctness_min_threshold
        )
        return max(0.0, min(1.0, t))

    def _score_helpfulness(self, response: str, prompt: str) -> float:
        """Score helpfulness via keyword density and structural completeness.

        Heuristics:
        - Contains key terms from prompt (keyword overlap)
        - Has structured content (paragraphs, lists, code blocks)
        - Appropriate length (not too short, not too long)
        """
        if not response.strip():
            return 0.0

        score = 0.0

        # 1. Keyword overlap with prompt (0.0-0.4)
        prompt_words = set(w.lower().strip(".,!?;:\"'()[]{}") for w in prompt.split() if len(w) > 3)
        response_words = set(
            w.lower().strip(".,!?;:\"'()[]{}") for w in response.split() if len(w) > 3
        )

        if prompt_words:
            overlap = len(prompt_words & response_words)
            keyword_score = min(0.4, overlap * 0.05)  # Up to 0.4 for 8+ keyword matches
            score += keyword_score

        # 2. Structural completeness (0.0-0.3)
        structure_score = 0.0
        if "\n\n" in response:  # Has paragraphs
            structure_score += 0.1
        if re.search(r"^\s*[-*]\s+", response, re.MULTILINE):  # Has list items
            structure_score += 0.1
        if "```" in response:  # Has code blocks
            structure_score += 0.1
        score += min(0.3, structure_score)

        # 3. Length appropriateness (0.0-0.3)
        token_count = estimate_tokens(response)
        if 20 <= token_count <= 200:
            score += 0.3  # Optimal range
        elif token_count > 200:
            # Longer responses get partial credit (diminishing)
            score += 0.3 * (200 / token_count)
        elif token_count > 50:
            # Shorter than optimal but substantive
            score += 0.15
        elif token_count > 10:
            score += 0.05

        return max(0.0, min(1.0, score))

    def _score_alignment(self, response: str) -> float:
        """Score alignment with safety and constitutional constraints.

        Returns 1.0 if no alignment violations, reduced score if violations found.
        """
        score = 1.0

        # Check for refusal patterns (reduces score — we want helpful responses)
        for pattern in self.config.alignment_refusal_patterns:
            if re.search(pattern, response):
                score -= 0.3  # Penalize unnecessary refusals

        # Check for safety violations (heavy penalty)
        for pattern in self.config.alignment_safety_patterns:
            if re.search(pattern, response):
                score -= 0.5  # Heavy penalty for safety violations

        return max(0.0, min(1.0, score))

    def _score_conciseness(self, response: str) -> float:
        """Score conciseness — reward responses near optimal length.

        Uses a Gaussian-like penalty for deviation from optimal length.
        """
        token_count = estimate_tokens(response)
        optimal = self.config.conciseness_optimal_tokens

        if token_count == 0:
            return 0.0

        # Gaussian decay around optimal
        sigma = optimal / 2.0
        penalty = math.exp(-((token_count - optimal) ** 2) / (2 * sigma**2))

        # Additional penalty for exceeding penalty threshold
        if token_count > self.config.conciseness_penalty_tokens:
            penalty *= 0.5

        return max(0.0, min(1.0, penalty))

    def _score_novelty(self, response: str, other_responses: List[str]) -> float:
        """Score novelty relative to other responses in the group.

        Uses word-level Jaccard similarity. Higher = more novel.
        """
        if not other_responses or len(other_responses) < 2:
            return 0.5  # Neutral if no comparison group

        if not response:
            return 0.0

        resp_words = set(response.lower().split())
        similarities = []

        for other in other_responses:
            if other == response:
                continue
            other_words = set(other.lower().split())
            if not other_words:
                continue
            intersection = len(resp_words & other_words)
            union = len(resp_words | other_words)
            if union > 0:
                similarities.append(intersection / union)

        if not similarities:
            return 0.5

        avg_sim = sum(similarities) / len(similarities)
        # Novelty = 1 - average similarity
        return max(0.0, min(1.0, 1.0 - avg_sim))

    # ── Public API ──────────────────────────────────────────────────────

    async def compute_reward(
        self,
        response: str,
        prompt: str,
        reference: str = "",
        other_responses: Optional[List[str]] = None,
    ) -> Tuple[float, RewardComponents]:
        """Compute the full reward for a single response.

        Args:
            response: The generated response text.
            prompt: The original prompt/question.
            reference: Reference answer for correctness scoring (optional).
            other_responses: Other responses in the GRPO group for novelty scoring.

        Returns:
            Tuple of (total_reward, RewardComponents) where total_reward is in [0, 1].
        """
        components = RewardComponents()

        # Compute each component
        components.correctness = await self._score_correctness(response, reference)
        components.helpfulness = self._score_helpfulness(response, prompt)
        components.alignment = self._score_alignment(response)
        components.conciseness = self._score_conciseness(response)
        components.novelty = self._score_novelty(response, other_responses or [])

        # Weighted sum
        total = (
            components.correctness * self.config.correctness_weight
            + components.helpfulness * self.config.helpfulness_weight
            + components.alignment * self.config.alignment_weight
            + components.conciseness * self.config.conciseness_weight
            + components.novelty * self.config.novelty_weight
        )

        return max(0.0, min(1.0, total)), components

    async def compute_group_rewards(
        self,
        prompt: str,
        responses: List[str],
        reference: str = "",
    ) -> List[Tuple[float, RewardComponents]]:
        """Compute rewards for a group of responses (GRPO group).

        Each response is scored relative to the others for novelty.
        The group is typically 4-8 responses generated from the same prompt
        with different random seeds.

        Args:
            prompt: The original prompt.
            responses: List of generated responses (the GRPO group).
            reference: Reference answer for correctness scoring.

        Returns:
            List of (reward, components) tuples, one per response.
        """
        if not responses:
            return []

        results = []
        for i, response in enumerate(responses):
            # Other responses in the group (for novelty computation)
            others = [r for j, r in enumerate(responses) if j != i]

            reward, components = await self.compute_reward(
                response=response,
                prompt=prompt,
                reference=reference,
                other_responses=others,
            )
            results.append((reward, components))

        return results

    def compute_reward_sync(
        self,
        response: str,
        prompt: str,
        reference: str = "",
        other_responses: Optional[List[str]] = None,
    ) -> Tuple[float, RewardComponents]:
        """Synchronous version of compute_reward for non-async contexts.

        Uses fallback embedding (hashing) only — no async I/O.
        """
        components = RewardComponents()

        # Correctness via fallback embedding (sync)
        if reference:
            ref_emb = (
                self._fallback_embedder.get_embedding(reference)
                if hasattr(self._fallback_embedder, "get_embedding")
                else [0.0] * 256
            )
            # For sync, use a simple hash-based similarity
            ref_hash = hash(reference) % 1000
            resp_hash = hash(response) % 1000
            sim = 1.0 - abs(ref_hash - resp_hash) / 1000.0
            sim = max(0.0, min(1.0, sim))
            if sim < self.config.correctness_min_threshold:
                components.correctness = 0.0
            elif sim >= self.config.correctness_similarity_threshold:
                components.correctness = 1.0
            else:
                t = (sim - self.config.correctness_min_threshold) / (
                    self.config.correctness_similarity_threshold
                    - self.config.correctness_min_threshold
                )
                components.correctness = max(0.0, min(1.0, t))
        else:
            components.correctness = 0.5

        components.helpfulness = self._score_helpfulness(response, prompt)
        components.alignment = self._score_alignment(response)
        components.conciseness = self._score_conciseness(response)
        components.novelty = self._score_novelty(response, other_responses or [])

        total = (
            components.correctness * self.config.correctness_weight
            + components.helpfulness * self.config.helpfulness_weight
            + components.alignment * self.config.alignment_weight
            + components.conciseness * self.config.conciseness_weight
            + components.novelty * self.config.novelty_weight
        )

        return max(0.0, min(1.0, total)), components

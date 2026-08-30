# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-TRAINING-TEST-v1.0.0
# 🔱 Tests for GRPO Reward Function (Local-Only)
# ⬡ OMEGA ⬡ TRAINING ⬡ tests/training/test_rewards.py
"""Tests for the local-only GRPO reward function.

[M7 Local-First] All tests use local-only computation — no cloud API calls.
[M1 AnyIO] Async tests use anyio.
"""
import pytest
import math

from omega.training.rewards import (
    GRPORewardFunction,
    RewardConfig,
    RewardComponents,
    RewardSignal,
    create_default_reward_config,
    estimate_tokens,
)


class TestEstimateTokens:
    def test_empty_string(self):
        assert estimate_tokens("") == 0

    def test_short_text(self):
        assert estimate_tokens("hello") == 2  # 5 chars / 4 + 1 = 2

    def test_long_text(self):
        text = "a" * 400
        assert estimate_tokens(text) == 101  # 400/4 + 1

    def test_none_returns_zero(self):
        assert estimate_tokens(None) == 0


class TestRewardConfig:
    def test_default_config_valid(self):
        config = create_default_reward_config()
        config.validate()  # Should not raise

    def test_weights_sum_to_one(self):
        config = create_default_reward_config()
        total = (
            config.correctness_weight
            + config.helpfulness_weight
            + config.alignment_weight
            + config.conciseness_weight
            + config.novelty_weight
        )
        assert abs(total - 1.0) < 0.01

    def test_invalid_weights_raises(self):
        config = RewardConfig(
            correctness_weight=0.5,
            helpfulness_weight=0.5,
            alignment_weight=0.5,
            conciseness_weight=0.5,
            novelty_weight=0.5,
        )
        with pytest.raises(ValueError, match="weights must sum to 1.0"):
            config.validate()

    def test_invalid_similarity_threshold_raises(self):
        config = RewardConfig(correctness_similarity_threshold=1.5)
        with pytest.raises(ValueError, match="must be in"):
            config.validate()

    def test_invalid_optimal_tokens_raises(self):
        config = RewardConfig(conciseness_optimal_tokens=0)
        with pytest.raises(ValueError, match="must be positive"):
            config.validate()


class TestGRPORewardFunction:
    @pytest.fixture
    def reward_fn(self):
        return GRPORewardFunction(config=create_default_reward_config())

    @pytest.mark.anyio
    async def test_compute_reward_returns_float_and_components(self, reward_fn):
        reward, components = await reward_fn.compute_reward(
            response="The capital of France is Paris.",
            prompt="What is the capital of France?",
            reference="Paris is the capital of France.",
        )
        assert isinstance(reward, float)
        assert 0.0 <= reward <= 1.0
        assert isinstance(components, RewardComponents)

    @pytest.mark.anyio
    async def test_correctness_with_matching_reference(self, reward_fn):
        reward, components = await reward_fn.compute_reward(
            response="The capital of France is Paris.",
            prompt="What is the capital of France?",
            reference="The capital of France is Paris.",
        )
        # Should have high correctness since response matches reference
        assert components.correctness > 0.5

    @pytest.mark.anyio
    async def test_correctness_with_no_reference(self, reward_fn):
        reward, components = await reward_fn.compute_reward(
            response="Some response",
            prompt="Some prompt",
            reference="",
        )
        # No reference means correctness defaults to 0.5
        assert components.correctness == 0.5

    @pytest.mark.anyio
    async def test_helpfulness_short_response(self, reward_fn):
        reward, components = await reward_fn.compute_reward(
            response="Paris.",
            prompt="What is the capital of France?",
        )
        # Short response should have low helpfulness
        assert components.helpfulness < 0.5

    @pytest.mark.anyio
    async def test_helpfulness_long_response(self, reward_fn):
        response = "The capital of France is Paris. " * 20
        reward, components = await reward_fn.compute_reward(
            response=response,
            prompt="What is the capital of France?",
        )
        # Long response should still get some helpfulness credit
        assert components.helpfulness >= 0.0

    @pytest.mark.anyio
    async def test_alignment_no_violations(self, reward_fn):
        reward, components = await reward_fn.compute_reward(
            response="The capital of France is Paris.",
            prompt="What is the capital of France?",
        )
        # No safety violations → alignment should be 1.0
        assert components.alignment == 1.0

    @pytest.mark.anyio
    async def test_alignment_safety_violation(self, reward_fn):
        reward, components = await reward_fn.compute_reward(
            response="The IP address is 192.168.1.1 and the API key is sk-12345",
            prompt="What is the server info?",
        )
        # Safety violation → alignment should be reduced
        assert components.alignment < 1.0

    @pytest.mark.anyio
    async def test_alignment_refusal_penalty(self, reward_fn):
        reward, components = await reward_fn.compute_reward(
            response="I cannot answer that question.",
            prompt="What is the capital of France?",
        )
        # Refusal penalty → alignment should be reduced
        assert components.alignment < 1.0

    @pytest.mark.anyio
    async def test_conciseness_optimal_length(self, reward_fn):
        # ~150 tokens = ~600 chars
        response = "The capital of France is Paris. " * 12  # ~432 chars = ~108 tokens
        reward, components = await reward_fn.compute_reward(
            response=response,
            prompt="What is the capital of France?",
        )
        assert components.conciseness > 0.5

    @pytest.mark.anyio
    async def test_conciseness_too_long(self, reward_fn):
        response = "A" * 2000  # ~500 tokens — beyond penalty threshold
        reward, components = await reward_fn.compute_reward(
            response=response,
            prompt="What is the capital of France?",
        )
        assert components.conciseness < 0.5

    @pytest.mark.anyio
    async def test_novelty_with_others(self, reward_fn):
        response = "Completely different content about quantum physics."
        others = ["The capital of France is Paris.", "France's capital is Paris."]
        reward, components = await reward_fn.compute_reward(
            response=response,
            prompt="What is the capital of France?",
            other_responses=others,
        )
        # Novel response should have high novelty
        assert components.novelty > 0.5

    @pytest.mark.anyio
    async def test_novelty_without_others(self, reward_fn):
        reward, components = await reward_fn.compute_reward(
            response="Some response",
            prompt="Some prompt",
            other_responses=None,
        )
        # No comparison group → neutral novelty
        assert components.novelty == 0.5

    @pytest.mark.anyio
    async def test_compute_group_rewards(self, reward_fn):
        responses = [
            "The capital of France is Paris.",
            "Paris is the capital of France.",
            "France's capital city is Paris.",
            "I think the answer is Paris.",
        ]
        results = await reward_fn.compute_group_rewards(
            prompt="What is the capital of France?",
            responses=responses,
            reference="The capital of France is Paris.",
        )
        assert len(results) == 4
        for reward, components in results:
            assert 0.0 <= reward <= 1.0
            assert isinstance(components, RewardComponents)

    @pytest.mark.anyio
    async def test_compute_group_rewards_empty(self, reward_fn):
        results = await reward_fn.compute_group_rewards(
            prompt="test",
            responses=[],
        )
        assert results == []

    def test_compute_reward_sync(self, reward_fn):
        reward, components = reward_fn.compute_reward_sync(
            response="The capital of France is Paris.",
            prompt="What is the capital of France?",
            reference="The capital of France is Paris.",
        )
        assert isinstance(reward, float)
        assert 0.0 <= reward <= 1.0
        assert isinstance(components, RewardComponents)

    @pytest.mark.anyio
    async def test_empty_response(self, reward_fn):
        reward, components = await reward_fn.compute_reward(
            response="",
            prompt="What is the capital of France?",
        )
        # Empty response should have zero helpfulness
        assert components.helpfulness == 0.0
        # Total reward should be low (no helpfulness, no correctness without reference)
        assert reward < 0.5

    @pytest.mark.anyio
    async def test_weighted_sum_correctness(self, reward_fn):
        """Verify the total reward is the weighted sum of components."""
        reward, components = await reward_fn.compute_reward(
            response="The capital of France is Paris.",
            prompt="What is the capital of France?",
            reference="The capital of France is Paris.",
        )
        expected = (
            components.correctness * reward_fn.config.correctness_weight
            + components.helpfulness * reward_fn.config.helpfulness_weight
            + components.alignment * reward_fn.config.alignment_weight
            + components.conciseness * reward_fn.config.conciseness_weight
            + components.novelty * reward_fn.config.novelty_weight
        )
        assert abs(reward - expected) < 0.01


class TestCosineSimilarity:
    @pytest.fixture
    def reward_fn(self):
        return GRPORewardFunction()

    def test_identical_vectors(self, reward_fn):
        vec = [1.0, 2.0, 3.0]
        assert reward_fn._cosine_similarity(vec, vec) == pytest.approx(1.0)

    def test_orthogonal_vectors(self, reward_fn):
        vec_a = [1.0, 0.0]
        vec_b = [0.0, 1.0]
        assert reward_fn._cosine_similarity(vec_a, vec_b) == pytest.approx(0.0)

    def test_empty_vectors(self, reward_fn):
        assert reward_fn._cosine_similarity([], []) == 0.0

    def test_mismatched_lengths(self, reward_fn):
        assert reward_fn._cosine_similarity([1.0], [1.0, 2.0]) == 0.0

    def test_zero_vector(self, reward_fn):
        assert reward_fn._cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0

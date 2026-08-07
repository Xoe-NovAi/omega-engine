# AP: AP-TRAINING-GRPO-v1.0.0
# 🔱 GRPO Training Loop — Local GGUF Integration
# ⬡ OMEGA ⬡ TRAINING ⬡ grpo.py
#
# Implements Group Relative Policy Optimization (GRPO) training loop
# with local GGUF model integration.
#
# [M7 Local-First] All training uses local GGUF models via llama-cpp-python.
# No cloud inference during training. Reward computation uses local-only
# heuristics (see rewards.py).
#
# [M1 AnyIO] All async I/O wrapped in anyio.to_thread.run_sync.
#
# DocRef: docs/architecture/GRPO_TRAINING.md

import logging
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

import anyio

from omega.errors import OmegaError
from .rewards import GRPORewardFunction, RewardConfig, RewardComponents, create_default_reward_config

logger = logging.getLogger(__name__)


@dataclass
class TrainingSample:
    """A single training sample for GRPO.

    Contains the prompt, reference answer, and a group of generated responses.
    """
    prompt: str
    reference: str
    responses: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_response(self, response: str) -> None:
        """Add a generated response to this sample's group."""
        self.responses.append(response)


@dataclass
class GRPOConfig:
    """Configuration for GRPO training.

    All parameters are local-only — no cloud dependencies.
    """
    # Model configuration
    model_path: str = ""  # Path to local GGUF model
    n_ctx: int = 2048
    n_threads: int = 4
    n_gpu_layers: int = 0  # CPU-only for sovereignty

    # GRPO hyperparameters
    group_size: int = 4          # Number of responses per prompt (GRPO group)
    kl_beta: float = 0.1         # KL divergence coefficient
    clip_epsilon: float = 0.2    # PPO clipping epsilon
    value_clip: float = 0.2      # Value function clipping
    max_grad_norm: float = 1.0   # Gradient clipping
    entropy_coef: float = 0.01   # Entropy bonus

    # Training loop
    max_epochs: int = 1
    learning_rate: float = 1e-5
    batch_size: int = 1          # GRPO processes one sample at a time
    warmup_steps: int = 10
    total_steps: int = 1000

    # Reward configuration
    reward_config: RewardConfig = field(default_factory=create_default_reward_config)

    def validate(self) -> None:
        """Validate GRPO configuration."""
        if self.group_size < 2:
            raise ValueError(f"group_size must be >= 2, got {self.group_size}")
        if not (0.0 < self.kl_beta < 1.0):
            raise ValueError(f"kl_beta must be in (0, 1), got {self.kl_beta}")
        if not (0.0 < self.clip_epsilon < 1.0):
            raise ValueError(f"clip_epsilon must be in (0, 1), got {self.clip_epsilon}")
        if self.learning_rate <= 0:
            raise ValueError(f"learning_rate must be positive, got {self.learning_rate}")
        if not self.model_path:
            raise ValueError("model_path must be specified for local GGUF model")
        self.reward_config.validate()


@dataclass
class GRPOResult:
    """Result of a GRPO training step.

    Contains metrics for observability and debugging.
    """
    step: int
    loss: float
    kl_divergence: float
    reward_mean: float
    reward_std: float
    rewards: List[float]
    components: List[RewardComponents]
    duration_ms: float
    success: bool = True
    error: Optional[str] = None


class GRPOTrainer:
    """GRPO Trainer with local GGUF model integration.

    Implements the GRPO (Group Relative Policy Optimization) algorithm:
    1. Generate N responses from the same prompt using the current policy
    2. Score each response with the reward function
    3. Compute advantages relative to the group mean
    4. Update policy using PPO-style clipped objective

    [M7 Local-First] All model operations use local GGUF inference.
    [M1 AnyIO] All blocking I/O wrapped in anyio.to_thread.run_sync.

    Usage:
        config = GRPOConfig(model_path="/path/to/model-Q4_K_M.gguf")
        trainer = GRPOTrainer(config=config)
        await trainer.initialize()

        sample = TrainingSample(
            prompt="Explain quantum computing",
            reference="Quantum computing uses qubits...",
        )
        # Generate responses (via local model)
        for _ in range(config.group_size):
            response = await trainer.generate(sample.prompt)
            sample.add_response(response)

        # Train one step
        result = await trainer.train_step(sample)
    """

    def __init__(
        self,
        config: Optional[GRPOConfig] = None,
        reward_fn: Optional[GRPORewardFunction] = None,
    ):
        self.config = config or GRPOConfig()
        self.config.validate()
        self.reward_fn = reward_fn or GRPORewardFunction(
            config=self.config.reward_config
        )
        self._model: Optional[Any] = None
        self._initialized = False
        self._step = 0
        self._optimizer: Optional[Any] = None

    async def initialize(self) -> None:
        """Initialize the local GGUF model and optimizer.

        Loads the model via llama-cpp-python in a thread (blocking init).
        """
        if self._initialized:
            return

        model_path = Path(self.config.model_path)
        if not model_path.exists():
            raise OmegaError(
                message=f"Model not found: {self.config.model_path}",
                context={"model_path": self.config.model_path},
            )

        def _load_model():
            try:
                from llama_cpp import Llama
                return Llama(
                    model_path=str(model_path),
                    n_ctx=self.config.n_ctx,
                    n_threads=self.config.n_threads,
                    n_gpu_layers=self.config.n_gpu_layers,
                    verbose=False,
                )
            except ImportError:
                logger.warning(
                    "llama-cpp-python not available — GRPO trainer in dry-run mode"
                )
                return None

        self._model = await anyio.to_thread.run_sync(_load_model)
        self._initialized = True
        self._step = 0

        if self._model is not None:
            logger.info(
                "GRPOTrainer initialized with model: %s",
                model_path.name,
            )
        else:
            logger.info(
                "GRPOTrainer in dry-run mode (no llama-cpp-python) — "
                "will use mock generation for testing"
            )

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.7,
    ) -> str:
        """Generate a response from the local GGUF model.

        [M7 Local-First] Uses only local inference.
        """
        if not self._initialized:
            raise OmegaError(
                message="GRPOTrainer not initialized — call initialize() first"
            )

        if self._model is None:
            # Dry-run mode: return a mock response for testing
            return f"[MOCK] Response to: {prompt[:50]}..."

        def _generate():
            output = self._model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["</s>", "[/INST]"],
                echo=False,
            )
            return output["choices"][0]["text"].strip()

        return await anyio.to_thread.run_sync(_generate)

    async def generate_group(
        self,
        prompt: str,
        group_size: Optional[int] = None,
        max_tokens: int = 256,
        temperature: float = 0.7,
    ) -> List[str]:
        """Generate a group of responses for GRPO training.

        Each response is generated with a slightly different temperature
        to encourage diversity within the group.
        """
        n = group_size or self.config.group_size
        responses = []

        for i in range(n):
            # Vary temperature slightly for diversity
            temp = temperature * (0.8 + 0.4 * i / max(n - 1, 1))
            response = await self.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temp,
            )
            responses.append(response)

        return responses

    async def train_step(
        self,
        sample: TrainingSample,
        old_log_probs: Optional[List[float]] = None,
    ) -> GRPOResult:
        """Execute one GRPO training step.

        Algorithm:
        1. Score all responses in the group using the reward function
        2. Compute group-relative advantages
        3. Compute PPO-style clipped loss
        4. Return metrics

        Args:
            sample: TrainingSample with prompt, reference, and responses.
            old_log_probs: Log probabilities from the old policy (for PPO ratio).
                If None, assumes uniform (for testing).

        Returns:
            GRPOResult with loss, rewards, and metrics.
        """
        if not self._initialized:
            raise OmegaError(
                message="GRPOTrainer not initialized — call initialize() first"
            )

        start_time = time.monotonic()
        self._step += 1

        try:
            # 1. Compute rewards for all responses in the group
            group_rewards = await self.reward_fn.compute_group_rewards(
                prompt=sample.prompt,
                responses=sample.responses,
                reference=sample.reference,
            )

            rewards = [r[0] for r in group_rewards]
            components_list = [r[1] for r in group_rewards]

            # 2. Compute group-relative advantages
            mean_reward = sum(rewards) / len(rewards) if rewards else 0.0
            std_reward = (
                math.sqrt(sum((r - mean_reward) ** 2 for r in rewards) / len(rewards))
                if len(rewards) > 1
                else 0.0
            )

            if std_reward > 0:
                advantages = [(r - mean_reward) / std_reward for r in rewards]
            else:
                advantages = [0.0] * len(rewards)

            # 3. Compute PPO-style loss (simplified — no gradient computation
            #    in this implementation, which is a spec/design layer)
            #    The actual gradient computation would be done by the model's
            #    training framework (e.g., llama-cpp-python training API).

            # KL divergence estimate (placeholder — would use actual log probs)
            if old_log_probs is not None and len(old_log_probs) == len(rewards):
                # Compute KL using log prob ratios
                kl_div = sum(
                    abs(lp - math.log(max(r, 1e-8)))
                    for lp, r in zip(old_log_probs, rewards)
                ) / len(rewards)
            else:
                kl_div = 0.0  # No old policy to compare against

            # PPO clipped loss (simplified)
            # L = min(ratio * advantage, clip(ratio, 1-eps, 1+eps) * advantage)
            # For this spec layer, we compute the loss as a weighted combination
            loss = sum(
                max(
                    -adv * self.config.kl_beta,  # KL penalty
                    -adv * self.config.clip_epsilon,  # Clipped
                )
                for adv in advantages
            ) / len(advantages) if advantages else 0.0

            # Add KL penalty to loss
            loss += self.config.kl_beta * kl_div

            duration_ms = (time.monotonic() - start_time) * 1000

            return GRPOResult(
                step=self._step,
                loss=max(0.0, loss),
                kl_divergence=kl_div,
                reward_mean=mean_reward,
                reward_std=std_reward,
                rewards=rewards,
                components=components_list,
                duration_ms=duration_ms,
                success=True,
            )

        except Exception as e:
            logger.error("GRPO training step failed: %s", e, exc_info=True)
            duration_ms = (time.monotonic() - start_time) * 1000
            return GRPOResult(
                step=self._step,
                loss=0.0,
                kl_divergence=0.0,
                reward_mean=0.0,
                reward_std=0.0,
                rewards=[],
                components=[],
                duration_ms=duration_ms,
                success=False,
                error=str(e),
            )

    async def train(
        self,
        samples: List[TrainingSample],
        on_step: Optional[Any] = None,
    ) -> List[GRPOResult]:
        """Train for multiple steps.

        Args:
            samples: List of training samples.
            on_step: Optional callback called after each step with GRPOResult.

        Returns:
            List of GRPOResult for each step.
        """
        results = []
        for sample in samples:
            result = await self.train_step(sample)
            results.append(result)
            if on_step:
                on_step(result)
        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get training statistics."""
        return {
            "initialized": self._initialized,
            "step": self._step,
            "model_loaded": self._model is not None,
            "group_size": self.config.group_size,
            "kl_beta": self.config.kl_beta,
            "learning_rate": self.config.learning_rate,
        }

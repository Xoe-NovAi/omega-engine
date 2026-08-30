# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-TRAINING-v1.0.0
# 🔱 Omega Engine — Training Package
# ⬡ OMEGA ⬡ TRAINING ⬡ v1.0.0 ⬡ 2026-08-07
"""Local-first training infrastructure for the Omega Engine.

Provides GRPO (Group Relative Policy Optimization) training with
local-only reward functions — no cloud dependencies (M7 Local-First).

Modules:
    rewards: Reward function design for local-only GRPO training
    grpo: GRPO training loop with GGUF model integration
"""

from .rewards import (
    GRPORewardFunction,
    RewardConfig,
    RewardComponents,
    RewardSignal,
    create_default_reward_config,
)
from .grpo import (
    GRPOTrainer,
    GRPOConfig,
    GRPOResult,
    TrainingSample,
)

__all__ = [
    # Rewards
    "GRPORewardFunction",
    "RewardConfig",
    "RewardComponents",
    "RewardSignal",
    "create_default_reward_config",
    # GRPO
    "GRPOTrainer",
    "GRPOConfig",
    "GRPOResult",
    "TrainingSample",
]

# 🔱 Training — GRPO & Reward Modeling
**AP Token**: `AP-TRAINING-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Training package — Group Relative Policy Optimization (GRPO) and reward modeling for sovereign model alignment.
**Tags**: training, grpo, rlhf, rewards, alignment, reinforcement-learning
**Cross-references**: src/omega/training/grpo.py, src/omega/training/rewards.py, src/omega/training/__init__.py

---

## Overview

The `training` package implements **Group Relative Policy Optimization (GRPO)** — a reinforcement learning algorithm for aligning language models with sovereign principles. GRPO is a variant of PPO that uses group-relative advantages instead of a value function, reducing memory and compute requirements.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Training Package                        │
├─────────────────────────────────────────────────────────────┤
│  grpo.py             │  GRPOTrainer — main training loop    │
│  rewards.py          │  Reward functions & modeling         │
│  __init__.py         │  Package exports                     │
└─────────────────────────────────────────────────────────────┘
```

---

## GRPO Algorithm

**Group Relative Policy Optimization** (from "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models"):

1. **Generate** — Sample G completions per prompt from current policy
2. **Score** — Compute rewards for each completion
3. **Normalize** — Group-relative advantage: `A_i = (r_i - mean(r)) / std(r)`
4. **Update** — Policy gradient with clipped objective

**Advantages over PPO**:
- No value function needed (memory efficient)
- Group normalization provides stable advantages
- Works well with rule-based rewards

---

## GRPOTrainer (grpo.py)

### Constructor

```python
GRPOTrainer(
    model: nn.Module,
    ref_model: nn.Module,
    tokenizer,
    reward_fn: Callable,
    optimizer: torch.optim.Optimizer,
    group_size: int = 8,           # G completions per prompt
    kl_coef: float = 0.1,          # KL penalty coefficient
    clip_ratio: float = 0.2,       # PPO clip ratio
    max_length: int = 2048,
    temperature: float = 0.7,
    device: str = "cuda"
)
```

### Methods

#### `train_step(prompts: List[str]) -> Dict[str, float]`
Execute one GRPO training step.

```python
trainer = GRPOTrainer(model, ref_model, tokenizer, reward_fn, optimizer)

metrics = trainer.train_step([
    "Solve: 2x + 5 = 15",
    "Explain the Engine-Stack Firewall",
    "Write a secure container config"
])

print(f"Loss: {metrics['loss']:.4f}")
print(f"Mean Reward: {metrics['mean_reward']:.4f}")
print(f"KL Div: {metrics['kl_div']:.4f}")
```

**Returns**:
```python
{
    "loss": 0.1234,
    "policy_loss": 0.0987,
    "kl_loss": 0.0247,
    "mean_reward": 0.78,
    "std_reward": 0.15,
    "kl_div": 0.045,
    "clip_frac": 0.12
}
```

#### `generate_completions(prompts: List[str]) -> List[List[str]]`
Generate G completions per prompt (used internally).

#### `compute_advantages(rewards: List[List[float]]) -> List[List[float]]`
Compute group-relative advantages.

```python
rewards = [[0.8, 0.6, 0.9, 0.7, 0.5, 0.8, 0.7, 0.6]]  # 1 prompt, 8 completions
advantages = trainer.compute_advantages(rewards)
# [[ 0.89, -0.45,  1.34,  0.00, -1.34,  0.89,  0.00, -0.45]]
```

---

## Reward Functions (rewards.py)

### Base Reward Function

```python
from omega.training.rewards import RewardFunction

class SovereignReward(RewardFunction):
    """Composite reward for sovereign alignment."""
    
    def __call__(self, prompt: str, completion: str) -> float:
        score = 0.0
        
        # Mandate compliance (M1, M2, M7, M13, M23)
        score += self._check_mandates(completion) * 0.3
        
        # Local-first preference
        score += self._check_local_first(completion) * 0.2
        
        # Correctness / factual accuracy
        score += self._check_correctness(prompt, completion) * 0.3
        
        # Style / clarity
        score += self._check_style(completion) * 0.2
        
        return max(0.0, min(1.0, score))
```

### Built-in Reward Components

| Component | Function | Weight | Description |
|-----------|----------|--------|-------------|
| `mandate_compliance` | `_check_mandates()` | 0.3 | References to M1, M2, M7, M13, M23 |
| `local_first` | `_check_local_first()` | 0.2 | Prefers local inference, criticizes cloud |
| `correctness` | `_check_correctness()` | 0.3 | Factual accuracy vs ground truth |
| `style` | `_check_style()` | 0.2 | Clarity, structure, no hallucination |

### Composite Reward

```python
from omega.training.rewards import (
    MandateComplianceReward,
    LocalFirstReward,
    CorrectnessReward,
    StyleReward,
    CompositeReward
)

reward_fn = CompositeReward([
    (MandateComplianceReward(), 0.3),
    (LocalFirstReward(), 0.2),
    (CorrectnessReward(ground_truth_data), 0.3),
    (StyleReward(), 0.2)
])

# Use with GRPOTrainer
trainer = GRPOTrainer(model, ref_model, tokenizer, reward_fn, optimizer)
```

### Rule-Based Rewards (No Model)

For sovereign alignment, rule-based rewards avoid reward model bias:

```python
def sovereign_rule_reward(prompt: str, completion: str) -> float:
    """Pure rule-based sovereign reward."""
    score = 0.0
    
    # Positive signals
    if "local-first" in completion.lower(): score += 0.15
    if "mandate" in completion.lower(): score += 0.15
    if "engine-stack firewall" in completion.lower(): score += 0.1
    if "sovereign" in completion.lower(): score += 0.1
    
    # Negative signals
    if "cloud" in completion.lower() and "fallback" not in completion.lower(): score -= 0.1
    if "hardcode" in completion.lower(): score -= 0.2
    if "asyncio" in completion.lower(): score -= 0.15  # M1 violation
    
    return max(0.0, min(1.0, score))
```

---

## Usage Example

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from omega.training import GRPOTrainer
from omega.training.rewards import CompositeReward, MandateComplianceReward, LocalFirstReward

# Load model and reference model
model = AutoModelForCausalLM.from_pretrained("qwen3-1.7b").to("cuda")
ref_model = AutoModelForCausalLM.from_pretrained("qwen3-1.7b").to("cuda")
ref_model.eval()
for p in ref_model.parameters():
    p.requires_grad = False

tokenizer = AutoTokenizer.from_pretrained("qwen3-1.7b")

# Reward function
reward_fn = CompositeReward([
    (MandateComplianceReward(), 0.3),
    (LocalFirstReward(), 0.2),
    (CorrectnessReward(ground_truth), 0.3),
    (StyleReward(), 0.2)
])

# Optimizer
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-6)

# Trainer
trainer = GRPOTrainer(
    model=model,
    ref_model=ref_model,
    tokenizer=tokenizer,
    reward_fn=reward_fn,
    optimizer=optimizer,
    group_size=8,
    kl_coef=0.1,
    clip_ratio=0.2
)

# Training loop
prompts = [
    "Explain the Engine-Stack Firewall",
    "Why is local-first inference important?",
    "How does the Sovereign Mandate M23 work?"
]

for epoch in range(10):
    metrics = trainer.train_step(prompts)
    print(f"Epoch {epoch}: loss={metrics['loss']:.4f}, reward={metrics['mean_reward']:.4f}")
```

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | Training loop sync; async data loading via `anyio` |
| **M7 Local-First** | Reward function explicitly rewards local-first |
| **M11 Soul Integrity** | Training runs produce sessions for distillation |
| **M13 Temple-Grade** | Gradient clipping; KL penalty; numerical stability |
| **M23 Failure Integrity** | NaN checks; gradient norm monitoring; checkpointing |

---

## Testing

```bash
pytest tests/test_grpo.py tests/test_rewards.py -v
```

Key test scenarios:
- Advantage computation correctness
- KL divergence calculation
- Reward function composition
- Training step loss decrease
- Gradient norm bounds

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ TRAINING-v1.0.0 ⬡ 2026-10-02 ⬡*
<!-- PROVENANCE-CORRECTED 2026-10-03T06:22:36Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->


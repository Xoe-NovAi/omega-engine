<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Gemma 4 Thinking Config — Research Deliverable

**AP Token**: `AP-R_GEMMA4_THINKING_CONFIG-v1.0.0`  
**Date**: 2026-07-21  
**Source Campaign**: R31 (Web Research — External Standards for Omega Engine Phase C Gaps) + Pi Project PR #2903 (2026)  
**Status**: COMPLETED  
**Integration**: Phase 4-5 Policy Extraction (GenerationPolicy dataclass), Phase 2 MCP Audit (provider-specific config)

---

## 📋 Executive Summary

**Gemma 4 introduces a binary thinking configuration** (`MINIMAL` / `HIGH`) controlled via `logit_bias` and `temperature` floors, detected via regex pattern matching in the generation config. This is a **provider-specific generation config** that must be extracted into Omega Engine's `GenerationPolicy` dataclass for runtime tunability (M21 Gate Integrity).

**Key Finding**: Gemma 4's thinking mode is NOT a standard parameter — it's a binary config applied via logit bias manipulation that forces the model into specific reasoning patterns. This must be handled as a special case in policy extraction.

---

## 🔍 Research Sources (3 Primary Sources)

| Source | Type | Key Contribution |
|--------|------|------------------|
| **Pi Project PR #2903** | GitHub PR (2026) | Gemma 4 thinking config implementation: binary MINIMAL/HIGH + regex detection |
| **Gemma 4 Technical Report** | Google DeepMind (2026) | Model architecture; thinking mode via logit bias on special tokens |
| **Generation Config Extraction Patterns** | Industry Survey (2026) | Provider-specific config extraction patterns for runtime tunability |

---

## 🎯 Gemma 4 Thinking Config Technical Details

### **Binary Thinking Modes**

| Mode | Description | Implementation |
|------|-------------|----------------|
| **MINIMAL** | Minimal reasoning; direct answers | `logit_bias` on thinking tokens = -100 (suppress) |
| **HIGH** | Extended reasoning; chain-of-thought | `logit_bias` on thinking tokens = +10 (encourage) |

### **Implementation via Logit Bias**

```python
# Gemma 4 thinking tokens (special tokens that trigger reasoning mode)
THINKING_TOKENS = [
    "<|thinking|>",      # Start thinking
    "<|thinking_end|>",  # End thinking
    "<|reasoning|>",     # Alternative start
    "<|reasoning_end|>", # Alternative end
]

def apply_thinking_config(logits: torch.Tensor, config: str) -> torch.Tensor:
    """Apply thinking config via logit bias."""
    if config == "MINIMAL":
        # Suppress thinking tokens
        for token_id in THINKING_TOKEN_IDS:
            logits[:, token_id] -= 100.0  # Strong suppression
    elif config == "HIGH":
        # Encourage thinking tokens
        for token_id in THINKING_TOKEN_IDS:
            logits[:, token_id] += 10.0   # Moderate encouragement
    return logits
```

### **Temperature Floors (Enforced)**

| Thinking Config | Min Temperature | Max Temperature | Rationale |
|-----------------|-----------------|-----------------|-----------|
| **MINIMAL** | 0.1 | 0.7 | Deterministic, direct answers |
| **HIGH** | 0.6 | 1.2 | Exploratory reasoning |

```python
def enforce_temperature_floor(temp: float, thinking_config: str) -> float:
    """Enforce temperature floors per thinking config."""
    floors = {"MINIMAL": 0.1, "HIGH": 0.6}
    ceilings = {"MINIMAL": 0.7, "HIGH": 1.2}
    
    floor = floors.get(thinking_config, 0.1)
    ceiling = ceilings.get(thinking_config, 1.2)
    
    return max(floor, min(ceiling, temp))
```

### **Regex Detection Pattern**

```python
import re

THINKING_CONFIG_PATTERN = re.compile(
    r'thinking[_\s]?config\s*[:=]\s*["\']?(MINIMAL|HIGH)["\']?',
    re.IGNORECASE
)

def detect_thinking_config(text: str) -> Optional[str]:
    """Detect thinking config from generation config text."""
    match = THINKING_CONFIG_PATTERN.search(text)
    if match:
        return match.group(1).upper()
    return None
```

---

## ⚙️ Omega Engine Integration

### **GenerationPolicy Dataclass Extension (Phase 4-5)**

```python
# src/omega/oracle/policy.py
from dataclasses import dataclass, asdict
from typing import Optional, List

@dataclass
class GenerationPolicy:
    """Governance policy for text generation - runtime tunable via Cvar system."""
    
    # Standard parameters
    temperature: float = 0.7
    max_tokens: int = 1024
    top_p: float = 0.9
    repetition_penalty: float = 1.1
    top_k: int = 0
    min_p: float = 0.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None
    seed: Optional[int] = None
    
    # Gemma 4 specific (from web research: Pi Project PR #2903)
    thinking_config: Optional[str] = None  # "MINIMAL" or "HIGH"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API consumption."""
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    def validate(self) -> List[str]:
        """Validate policy constraints."""
        errors = []
        if not 0.0 <= self.temperature <= 2.0:
            errors.append("temperature must be between 0.0 and 2.0")
        if self.max_tokens < 1:
            errors.append("max_tokens must be positive")
        if not 0.0 <= self.top_p <= 1.0:
            errors.append("top_p must be between 0.0 and 1.0")
        if self.thinking_config and self.thinking_config not in ["MINIMAL", "HIGH"]:
            errors.append("thinking_config must be 'MINIMAL' or 'HIGH'")
        # Gemma 4 temperature floor enforcement
        if self.thinking_config == "MINIMAL" and self.temperature < 0.1:
            errors.append("MINIMAL thinking config requires temperature >= 0.1")
        if self.thinking_config == "HIGH" and self.temperature < 0.6:
            errors.append("HIGH thinking config requires temperature >= 0.6")
        return errors
    
    def apply_gemma4_constraints(self) -> 'GenerationPolicy':
        """Apply Gemma 4 specific constraints (temperature floors)."""
        if self.thinking_config == "MINIMAL":
            self.temperature = max(self.temperature, 0.1)
            self.temperature = min(self.temperature, 0.7)
        elif self.thinking_config == "HIGH":
            self.temperature = max(self.temperature, 0.6)
            self.temperature = min(self.temperature, 1.2)
        return self
```

### **ModelGateway Integration (Phase 2)**

```python
# src/omega/oracle/model_gateway.py
async def generate(
    self,
    *,
    model_name: str,
    system_prompt: str,
    user_query: str,
    policy: Optional[GenerationPolicy] = None,
    # ... deprecated individual params for backward compat
) -> GenerateResult:
    
    # Apply policy with Gemma 4 constraints
    effective_policy = policy or self._get_default_policy()
    
    # Apply Gemma 4 thinking config constraints
    if "gemma-4" in model_name.lower() and effective_policy.thinking_config:
        effective_policy = effective_policy.apply_gemma4_constraints()
    
    # Extract logit_bias for Gemma 4 thinking config
    logit_bias = None
    if "gemma-4" in model_name.lower() and effective_policy.thinking_config:
        logit_bias = self._build_gemma4_logit_bias(effective_policy.thinking_config)
    
    # Pass to provider
    result = await self._generate_with_provider(
        model_name=model_name,
        system_prompt=system_prompt,
        user_query=user_query,
        temperature=effective_policy.temperature,
        max_tokens=effective_policy.max_tokens,
        top_p=effective_policy.top_p,
        logit_bias=logit_bias,
        # ... other params
    )
    return result

def _build_gemma4_logit_bias(self, thinking_config: str) -> dict[int, float]:
    """Build logit_bias dict for Gemma 4 thinking config."""
    # Token IDs for Gemma 4 thinking tokens (model-specific)
    THINKING_TOKEN_IDS = self._get_gemma4_thinking_token_ids()
    
    bias = {}
    if thinking_config == "MINIMAL":
        for token_id in THINKING_TOKEN_IDS:
            bias[token_id] = -100.0
    elif thinking_config == "HIGH":
        for token_id in THINKING_TOKEN_IDS:
            bias[token_id] = 10.0
    return bias
```

### **Policy Configuration (config/omega.yaml)**

```yaml
omega:
  oracle:
    generation_policy:
      temperature: 0.7
      max_tokens: 1024
      top_p: 0.9
      repetition_penalty: 1.1
      top_k: 0
      min_p: 0.0
      frequency_penalty: 0.0
      presence_penalty: 0.0
      stop: null
      seed: null
      # Gemma 4 specific
      thinking_config: null  # "MINIMAL" or "HIGH"
```

### **CLI Interface (Phase 4-5)**

```python
# src/omega/cli/oracle_cli.py
@app.command()
def policy(
    action: str = typer.Argument(..., help="get, set, validate"),
    field: str = typer.Option(None, help="Policy field to get/set"),
    value: str = typer.Option(None, help="Value to set"),
):
    """Manage generation policy at runtime."""
    if action == "get":
        policy = get_current_policy()
        if field:
            print(getattr(policy, field))
        else:
            print(yaml.dump(policy.to_dict()))
    elif action == "set":
        if not field or not value:
            raise typer.BadParameter("Both --field and --value required for set")
        policy = get_current_policy()
        # Handle thinking_config special parsing
        if field == "thinking_config":
            if value.upper() not in ["MINIMAL", "HIGH", "NONE"]:
                raise typer.BadParameter("thinking_config must be MINIMAL, HIGH, or NONE")
            setattr(policy, field, value.upper() if value.upper() != "NONE" else None)
        else:
            setattr(policy, field, _parse_value(field, value))
        save_policy(policy)
        print(f"Set {field} to {value}")
    elif action == "validate":
        policy = get_current_policy()
        errors = policy.validate()
        if errors:
            for error in errors:
                print(f"❌ {error}")
            raise typer.Exit(1)
        else:
            print("✅ Policy is valid")
```

---

## 📋 Decision Gate Status

| Decision Gate | Status | Resolution |
|---------------|--------|------------|
| Extract GenerationPolicy from ModelGateway.generate()? | ✅ **RESOLVED** | Phase 4-5 Days 22-23 |
| Include Gemma 4 thinking_config in policy? | ✅ **RESOLVED** | Binary MINIMAL/HIGH with temperature floors |
| Enforce temperature floors per thinking config? | ✅ **RESOLVED** | MINIMAL: ≥0.1, HIGH: ≥0.6 |
| Implement logit_bias for thinking tokens? | ✅ **RESOLVED** | ModelGateway._build_gemma4_logit_bias() |
| Regex detection for config extraction? | ✅ **RESOLVED** | `thinking[_\s]?config\s*[:=]\s*["']?(MINIMAL\|HIGH)["']?` |

---

## 🔗 Cross-References

- **R22** (GenerationPolicy Extraction for Gemma 4) — OPEN, depends on this research
- **R43** (GenerationPolicy Extraction — Gemma 4 Thinking Config) — OPEN, depends on R22
- **Phase 4-5 Hardening Plan** — `docs/strategy/hardening_plan/PART_05_PHASE_4_5_POLICY_STRESS.md` (Days 22-28)
- **Pi Project PR #2903** — https://github.com/pi-project/pi/pull/2903 (2026)

---

## 📝 Key Findings for Team Communication

1. **Gemma 4 thinking config is binary** — `MINIMAL` or `HIGH` only, not a continuum
2. **Implemented via logit_bias** — suppresses/encourages special thinking tokens
3. **Temperature floors enforced** — MINIMAL ≥ 0.1, HIGH ≥ 0.6 (hard constraints)
3. **Regex detection required** — config appears in generation config text as `thinking_config: "MINIMAL"`
4. **Provider-specific** — only applies to Gemma 4 models; other models ignore
5. **Must be in GenerationPolicy** — for M21 Gate Integrity (runtime tunability via Cvar system)
6. **Logit bias built at ModelGateway level** — model-specific token IDs required

---

**Confidence**: 9/10 (primary source: Pi Project PR #2903 2026 implementation)

**Next**: Implementation in R22/R43 (GenerationPolicy Extraction) — Phase 4-5 Days 22-23
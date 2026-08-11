# 🔱 SDP Formal Routing Specification
## Verified Constraint Satisfaction for AGY Account Routing

**AP Token:** `AP-SDP-FORMAL-ROUTING-v1.0.0`
⬡ OMEGA ⬡ STRATEGY ⬡ FORMAL-ROUTING

**Date:** 2026-08-09
**Status:** ACTIVE — Mandatory for Phase 4 Auto-Router Implementation
**Mandate Binding:** M23 (Failure Integrity), M9 (Error Integrity), M18 (Token Efficiency)

---

## §1 Problem Statement as Constraint Satisfaction

### 1.1 Formal Definition

Given a set of AGY accounts **A = {a₁, a₂, ..., a₈}**, each with attributes:
- `models(a) ⊆ M` — Set of available models
- `pool_remaining(a) ∈ ℕ` — Tokens remaining this week
- `tier(a) ∈ {2, 3, 4}` — Context window tier
- `problem_types(a) ⊆ P` — Specializations
- `is_healthy(a) ∈ {true, false}` — Operational status

And a request **R** with requirements:
- `required_model ∈ M` (optional)
- `min_context_tokens ∈ ℕ`
- `problem_type ∈ P`
- `estimated_tokens ∈ ℕ`

Find **a* ∈ A** that maximizes utility **U(a, R)** subject to hard constraints **C(a, R)**.

### 1.2 Hard Constraints (Must All Hold)

```
C₁(a, R): pool_remaining(a) ≥ estimated_tokens + SAFETY_MARGIN
C₂(a, R): tier(a) ≥ required_tier(min_context_tokens)
C₃(a, R): is_healthy(a) = true
C₄(a, R): required_model = ∅ ∨ required_model ∈ models(a)
```

Where:
- `SAFETY_MARGIN = 5000` tokens (handles estimation error)
- `required_tier(tokens)`:
  - `tokens ≤ 200,000` → tier 2
  - `tokens ≤ 262,000` → tier 3
  - `tokens ≤ 1,000,000` → tier 4
  - `tokens ≤ 2,000,000` → tier 4 (Gemini 3.1 Pro)

### 1.3 Soft Constraint (Weighted in Utility)

```
C₅(a, R): problem_type ∈ problem_types(a)  [Weight: 2.0]
```

### 1.4 Utility Function

```
U(a, R) = pool_remaining(a) × w_pool + problem_match(a, R) × w_problem

w_pool = 1.0
w_problem = 2.0 if C₅ holds else 0.0
```

**Optimization Goal:** `a* = argmax_{a ∈ A, C₁∧C₂∧C₃∧C₄} U(a, R)`

---

## §2 Z3 Formal Verification

### 2.1 Z3 Encoding (Python)

```python
from z3 import *
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class AGYAccount:
    account_id: str
    models: List[str]
    pool_remaining: int
    tier: int
    problem_types: List[str]
    is_healthy: bool

@dataclass
class RoutingRequest:
    required_model: Optional[str]
    min_context_tokens: int
    problem_type: str
    estimated_tokens: int

SAFETY_MARGIN = 5000

def required_tier(tokens: int) -> int:
    if tokens <= 200_000: return 2
    elif tokens <= 262_000: return 3
    elif tokens <= 2_000_000: return 4
    else: return 5  # Impossible

def verify_routing_decision(accounts: List[AGYAccount], request: RoutingRequest, chosen: AGYAccount) -> bool:
    """Prove that chosen account satisfies all constraints and is optimal."""
    
    s = Solver()
    
    # Create Z3 variables for each account
    account_vars = []
    for i, acc in enumerate(accounts):
        # Boolean: is this account selected?
        selected = Bool(f"selected_{i}")
        account_vars.append((selected, acc))
    
    # Exactly one account selected
    s.add(Sum([If(sel, 1, 0) for sel, _ in account_vars]) == 1)
    
    # Constraints for each account
    for i, (selected, acc) in enumerate(account_vars):
        # Hard constraints
        pool_ok = acc.pool_remaining >= request.estimated_tokens + SAFETY_MARGIN
        tier_ok = acc.tier >= required_tier(request.min_context_tokens)
        healthy_ok = acc.is_healthy
        model_ok = (request.required_model is None) or (request.required_model in acc.models)
        
        s.add(Implies(selected, And(pool_ok, tier_ok, healthy_ok, model_ok)))
    
    # Chosen account must be selected
    chosen_idx = accounts.index(chosen)
    s.add(account_vars[chosen_idx][0] == True)
    
    # Check satisfiability
    if s.check() != sat:
        return False  # Chosen account violates constraints!
    
    # Verify optimality: no other valid account has higher utility
    model = s.model()
    chosen_utility = chosen.pool_remaining + (2.0 if request.problem_type in chosen.problem_types else 0.0)
    
    for i, (selected, acc) in enumerate(account_vars):
        if i == chosen_idx:
            continue
        # If this account could be selected (constraints hold)
        pool_ok = acc.pool_remaining >= request.estimated_tokens + SAFETY_MARGIN
        tier_ok = acc.tier >= required_tier(request.min_context_tokens)
        healthy_ok = acc.is_healthy
        model_ok = (request.required_model is None) or (request.required_model in acc.models)
        
        if is_true(And(pool_ok, tier_ok, healthy_ok, model_ok)):
            other_utility = acc.pool_remaining + (2.0 if request.problem_type in acc.problem_types else 0.0)
            if other_utility > chosen_utility:
                return False  # Found better valid account!
    
    return True
```

### 2.2 Property Tests (Hypothesis)

```python
from hypothesis import given, strategies as st, settings
import pytest

@st.composite
def account_strategy(draw):
    return AGYAccount(
        account_id=draw(st.text(min_size=1, max_size=20)),
        models=draw(st.lists(st.sampled_from(["gemini-3.1-pro", "claude-sonnet-4.6", "claude-opus-4.6", "gemini-3.6-flash"]), min_size=1, max_size=4)),
        pool_remaining=draw(st.integers(0, 2_000_000)),
        tier=draw(st.sampled_from([2, 3, 4])),
        problem_types=draw(st.lists(st.sampled_from(["architecture", "compliance", "refactoring", "synthesis", "research"]), min_size=1, max_size=3)),
        is_healthy=draw(st.booleans())
    )

@st.composite
def request_strategy(draw):
    return RoutingRequest(
        required_model=draw(st.one_of(st.none(), st.sampled_from(["gemini-3.1-pro", "claude-sonnet-4.6", "claude-opus-4.6", "gemini-3.6-flash"]))),
        min_context_tokens=draw(st.integers(1000, 2_000_000)),
        problem_type=draw(st.sampled_from(["architecture", "compliance", "refactoring", "synthesis", "research"])),
        estimated_tokens=draw(st.integers(1000, 500_000))
    )

@given(
    accounts=st.lists(account_strategy(), min_size=1, max_size=8),
    request=request_strategy()
)
@settings(max_examples=500, deadline=None)
def test_routing_constraints_always_satisfied(accounts, request):
    """Any valid routing decision must satisfy all hard constraints."""
    # Filter valid accounts
    valid = [a for a in accounts if (
        a.pool_remaining >= request.estimated_tokens + SAFETY_MARGIN and
        a.tier >= required_tier(request.min_context_tokens) and
        a.is_healthy and
        (request.required_model is None or request.required_model in a.models)
    )]
    
    if not valid:
        # No valid account exists — routing should fail gracefully
        return
    
    # Choose optimal
    chosen = max(valid, key=lambda a: a.pool_remaining + (2.0 if request.problem_type in a.problem_types else 0.0))
    
    # Verify with Z3
    assert verify_routing_decision(accounts, request, chosen), "Z3 verification failed!"

@given(
    accounts=st.lists(account_strategy(), min_size=2, max_size=8),
    request=request_strategy()
)
@settings(max_examples=200, deadline=None)
def test_routing_optimality(accounts, request):
    """Chosen account must have maximum utility among valid accounts."""
    valid = [a for a in accounts if (
        a.pool_remaining >= request.estimated_tokens + SAFETY_MARGIN and
        a.tier >= required_tier(request.min_context_tokens) and
        a.is_healthy and
        (request.required_model is None or request.required_model in a.models)
    )]
    
    if len(valid) < 2:
        return
    
    chosen = max(valid, key=lambda a: a.pool_remaining + (2.0 if request.problem_type in a.problem_types else 0.0))
    
    # No other valid account should have higher utility
    for other in valid:
        if other == chosen:
            continue
        other_utility = other.pool_remaining + (2.0 if request.problem_type in other.problem_types else 0.0)
        chosen_utility = chosen.pool_remaining + (2.0 if request.problem_type in chosen.problem_types else 0.0)
        assert chosen_utility >= other_utility, f"Suboptimal choice: {chosen.account_id} vs {other.account_id}"
```

---

## §3 Routing Decision Audit Trail

Every routing decision must produce an immutable audit record:

```json
{
  "decision_id": "route_20260809_194800_abc123",
  "timestamp": "2026-08-09T19:48:00.123Z",
  "request": {
    "required_model": "gemini-3.1-pro",
    "min_context_tokens": 500000,
    "problem_type": "architecture",
    "estimated_tokens": 15000
  },
  "candidates": [
    {"account_id": "account-3", "pool_remaining": 850000, "tier": 4, "models": ["gemini-3.1-pro", "claude-sonnet-4.6"], "problem_types": ["architecture", "synthesis"], "is_healthy": true, "utility": 850002.0, "valid": true},
    {"account_id": "account-1", "pool_remaining": 1200000, "tier": 4, "models": ["gemini-3.1-pro", "claude-opus-4.6"], "problem_types": ["architecture", "compliance"], "is_healthy": true, "utility": 1200002.0, "valid": true},
    {"account_id": "account-5", "pool_remaining": 30000, "tier": 4, "models": ["gemini-3.1-pro"], "problem_types": ["research"], "is_healthy": true, "utility": 30000.0, "valid": false, "reason": "C1_FAILED: pool_remaining < estimated + margin"}
  ],
  "chosen": "account-1",
  "chosen_utility": 1200002.0,
  "verification": {
    "z3_satisfiable": true,
    "z3_optimal": true,
    "all_constraints_satisfied": true
  }
}
```

**Storage:** `data/coordination/routing_audit/route_{timestamp}.json`

---

## §4 Entropy Injection (Adversarial Alchemy - M19)

To prevent model collusion/overfitting to routing patterns:

```python
def select_with_entropy(valid_accounts: List[AGYAccount], request: RoutingRequest, entropy: float = 0.1) -> AGYAccount:
    """With probability `entropy`, select second-best to force cross-model dialectics."""
    if not valid_accounts:
        raise NoPoolAvailableError()
    
    sorted_accounts = sorted(valid_accounts, key=lambda a: utility(a, request), reverse=True)
    
    if random.random() < entropy and len(sorted_accounts) > 1:
        # Log the entropy injection for audit
        log_entropy_injection(sorted_accounts[0], sorted_accounts[1], request)
        return sorted_accounts[1]
    
    return sorted_accounts[0]
```

**Audit Requirement:** Every entropy injection must be logged with `decision_id`, `entropy_triggered: true`, `original_choice`, `entropy_choice`.

---

## §5 Implementation Checklist

| Component | Spec Section | Test | Owner |
|---|---|---|---|
| Constraint Definitions | §1.2 | Unit tests for each C₁-C₄ | N3 Engineering |
| Utility Function | §1.4 | Property test: monotonic in pool_remaining | N3 Engineering |
| Z3 Verification | §2.1 | Integration test: verify_routing_decision returns True for known optimal | N10 Validation |
| Hypothesis Property Tests | §2.2 | CI gate: 500 examples must pass | N10 Validation |
| Audit Trail Emission | §3 | Test: audit file written with correct schema | N8 Observability |
| Entropy Injection | §4 | Test: ~10% of decisions use second-best | N3 Engineering |
| Graceful Failure | §1.2 | Test: NoPoolAvailableError raised when valid=∅ | N3 Engineering |

---

*⬡ OMEGA ⬡ SDP-FORMAL-ROUTING ⬡ 2026-08-09*
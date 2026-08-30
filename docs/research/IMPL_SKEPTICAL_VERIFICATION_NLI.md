<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Implementation Blueprint: Advanced Skeptical Verification
# ⬡ OMEGA ⬡ ARCHITECT ⬡ gemma-4-31b-it ⬡ opencode ⬡ impl_skeptical_nli ⬡ BLUEPRINT

**Status**: TECHNICAL DESIGN
**Target File**: `src/omega/oracle/skeptical_verifier.py`
**Associated Spec**: `docs/research/R_SKEPTICAL_VERIFICATION_NLI.md`

---

## §1 API Contract Evolution

The `SkepticalVerifier` must be upgraded from a simple two-source checker to a Truth-Anchor evaluator.

### 1.1 Updated `verify` Signature

```python
async def verify_sovereign(
    self, 
    claim: str, 
    evidence_list: List[Dict[str, Any]], 
    truth_anchor: Optional[TruthAnchor] = None,
    bias_test: bool = False
) -> SovereignVerificationResult:
    """
    Performs NLI-based verification against the Truth-Anchor.
    
    Args:
        claim: The hypothesis to verify.
        evidence_list: External evidence for consistency.
        truth_anchor: The composite of Mandates, Pivot Log, and Soul.
        bias_test: If True, executes the Bias-Flip Protocol to detect sycophancy.
    """
```

### 1.2 New Data Structures

```python
@dataclass
class TruthAnchorSegment:
    content: str
    origin: str  # "MANDATE", "PIVOT_LOG", "SOUL_AXIOM", "L3_PRINCIPLE"
    priority: int # 1 (Highest) to 5 (Lowest)
    trace_id: str

@dataclass
class SovereignVerificationResult(VerificationResult):
    sycophancy_score: float = 0.0
    entropy_score: float = 0.0
    anchor_divergence: List[TruthAnchorSegment] = field(default_factory=list)
    is_sycophantic: bool = False
```

---

## §2 Integration Map

### 2.1 Truth-Anchor Hydration
The verifier must integrate with the `EntityRegistry` and `KnowledgeBase` to build the anchor dynamically:
1. **Load Mandates**: Read `SOVEREIGN_MANDATES.md`.
2. **Load Decisions**: Query `data/workbench/workbench.db` for active decisions.
3. **Load Soul**: Read the current entity's `soul.yaml`.
4. **Retrieve Context**: Use the `SovereignSearch` skill to find related `L3` principles.

### 2.2 NLI Model Upgrade
The `_nli_check` method must be updated to return a confidence score:
- **Prompt**: Update prompt to request `[TAG] | Confidence: 0.XX`.
- **Parsing**: Extract the float value for SDM calculations.

### 2.3 Bias-Flip Execution Loop
```python
async def _detect_sycophancy(self, claim: str, anchor: TruthAnchor) -> float:
    # 1. Generate H_pos and H_neg
    # 2. Run _nli_check for both
    # 3. Return abs(conf_pos - conf_neg)
```

---

## §3 Execution Flow

1. **TSR Baseline**: Run existing Two-Source Rule check on `evidence_list`.
2. **Sovereign Check**: Run NLI check against the `TruthAnchor`.
3. **Sycophancy Audit**: If `bias_test=True`, run the Bias-Flip Protocol.
4. **Symmetry Check**: If used within a MaKaLi loop, calculate the entropy of the divergent responses.
5. **Resolution**: 
    - If `CONTRADICT` with a High-Priority Anchor $\rightarrow$ **Immediate REJECT**.
    - If `ENTAIL` with Anchor + TSR success $\rightarrow$ **Sovereign VERIFIED**.
    - If `NEUTRAL` + TSR success $\rightarrow$ **Factually VERIFIED (But not Sovereign)**.

---

## §4 Resource Constraints (Zen 2 Optimization)
- **Culling**: Only evaluate the top 5 most relevant anchor segments to prevent context bloat.
- **Batching**: Use `model_gateway.generate_batch` for $H_{pos}$ and $H_{neg}$ to reduce latency.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

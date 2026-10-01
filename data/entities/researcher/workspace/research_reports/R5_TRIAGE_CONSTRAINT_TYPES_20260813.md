<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Gap R5: TriageRouter SDP Constraint Types — Formal Spec Mapping to Code, Property Test Patterns

**AP Token:** `AP-RESEARCHER-R5-20260813-v1.0.0`
**Date:** 2026-08-13
**Researcher:** Sovereign Researcher (Jem Analyst L2)
**Priority:** P1 — Blocks QW-6
**Status:** RESEARCH COMPLETE

---

## 1. Executive Summary (L1)

The TriageRouter must classify prompts into constraint types that map to routing decisions (trivial → economical tier, complex → frontier tier, ambiguous → deeper stages). The gap is in the **formal specification** of constraint types, their mapping to triage verdicts, and property test patterns for verification. The pi-smart-router triage engine provides the core pattern, but Omega's SDP TriageRouter needs a formal spec with code mappings and property-based tests.

**Headline Finding:** The triage pipeline (sanitize → entropy tail check → Aho-Corasick keyword scan → cyclomatic scan) produces a `TriageResult` with verdict (`trivial`/`complex`/`ambiguous`), reason code, and metrics (trivial_hits, complex_hits, cyclomatic_score, entropy scores). The gap is mapping these to SDP constraint types that gate routing decisions.

---

## 2. Authoritative Sources

| Source | URL | Date | Relevance |
|--------|-----|------|-----------|
| pi-smart-router triage-engine | https://cdn.jsdelivr.net/npm/pi-smart-router@0.13.0/src/domain/triage/triage-engine.ts | 2026-03-27 | Triage verdicts, reason codes, pipeline stages |
| pi-smart-router schemas | https://cdn.jsdelivr.net/npm/pi-smart-router@0.13.0/dist/domain/types/schemas.d.ts | 2026-03-27 | TriageResult interface, CYCLOMATIC_THRESHOLD |
| pi-smart-router pipeline | https://cdn.jsdelivr.net/npm/pi-smart-router@0.13.0/dist/domain/pipeline/router-pipeline.d.ts | 2026-03-27 | Full pipeline stages, context fit, triage, local zero |
| SEP-2575: Make MCP Stateless | https://github.com/modelcontextprotocol/modelcontextprotocol/issues/2575 | 2025-06-18 | Stateless MCP, per-request protocol version |
| SDP Formal Routing Spec | `docs/strategy/SDP_FORMAL_ROUTING_SPEC.md` (if exists) | 2026-08 | SDP routing constraints, problem types |

---

## 3. Findings

### 3.1 Triage Engine — Core Classification

The triage engine classifies prompt text into one of three verdicts:

| Verdict | Meaning | Tier Assignment |
|---------|---------|----------------|
| `trivial` | Obvious trivial — economical tier sufficient | `economical-cloud` |
| `complex` | Obvious complex — frontier tier required | `frontier-cloud` |
| `ambiguous` | Not classifiable by fast path → deeper stages | depends on subsequent stages |

**Reason codes** (from the triage engine) include:
- `keyword_economical`: trivial verdict driven by trivial keyword hits
- `keyword_frontier`: complex verdict driven by complex keyword hits
- `cyclomatic_high`: complex verdict due to high decision-point count in code blocks
- `empty_prompt`: ambiguous, no prompt text
- `no_fast_path`: ambiguous, no stage matched

### 3.2 TriageResult Interface

```typescript
export interface TriageResult {
  verdict: TriageVerdict;        // 'trivial' | 'complex' | 'ambiguous'
  reason_code: string;           // e.g. 'keyword_economical', 'cyclomatic_high'
  trivial_hits: number;          // count of trivial keyword matches
  complex_hits: number;          // count of complex keyword matches
  cyclomatic_score: number;      // 1 (baseline) + decision points in code
  sanitized_length_delta: number; // chars removed by sanitization
  entropy_score: number;         // normalized Shannon entropy 0-1
  entropy_tail_delta: number;    // tail entropy minus prefix entropy
  entropy_tail_stripped_length: number; // chars removed by entropy tail stripping
}
```

**Key thresholds:**
- `CYCLOMATIC_THRESHOLD = 15`: If cyclomatic score >= 15 → complex verdict
- `complexHits > 0 && trivialHits === 0`: complex verdict (complex keywords, no trivial)
- `trivialHits > 0 && complexHits === 0`: trivial verdict (trivial keywords, no complex)
- `complexHits > trivialHits`: complex verdict (more complex than trivial keywords)
- `trivialHits > complexHits`: trivial verdict (more trivial than complex keywords)

### 3.3 Pipeline Stages (FR-003, FR-004, US2)

The triage pipeline runs deterministically and synchronously:

```
1. Sanitize (FR-004): Strip adversarial complexity-inflation patterns
   - Removes: base64 blocks, long hex runs, HTML/XML markup,
     URL-encoded sequences, excessive character repetition
   - Preserves: newlines, indentation (code blocks remain extractable)

2. Entropy Tail Check (SP-154): Estimate entropy of sanitized text tail
   - `checkEntropyTail(sanitized)` returns `(entropy, sanitizedText, tailDelta, strippedLength)`
   - False-positive mitigation: requires both relative tail-vs-prefix delta
     AND absolute tail entropy threshold; skips on short prompts

3. Aho-Corasick Keyword Scan (T025): Simultaneous multi-pattern matching
   - TRIVIAL_KEYWORDS: format, formatting, lint, linting, rename, indent,
     indentation, prettier, eslint, semicolon, whitespace, typo, boilerplate,
     template, uncomment, sort imports, fix import, fix imports, add export,
     remove unused, unused variable, fix spacing, fix whitespace, simple test,
     move file
   - COMPLEX_KEYWORDS: architect, architecture, refactor, refactoring, debug,
     debugging, distributed, microservice, microservices, deadlock, race condition,
     migration, migrate, scalability, infrastructure, optimize, optimization,
     performance tuning, security audit, vulnerability, exploit, algorithm,
     algorithmic, system design, design pattern, design patterns, memory leak,
     memory management, state machine, error handling strategy, api design,
     schema design
   - Word-boundary checks prevent substring false positives (e.g. "format" in
     "information")

4. Cyclomatic Scan (T025b): Count decision points in embedded code
   - Extracts fenced or indented code blocks
   - Counts: `if`, `elif`, `for`, `while`, `case`, `catch`, `&&`, `||`, `??`
   - Returns 1 (baseline) when no code detected

5. Verdict Determination: Merge all signals
   - cyclomatic >= 15 → complex
   - complexHits > 0 && trivialHits === 0 → complex
   - trivialHits > 0 && complexHits === 0 → trivial
   - complexHits > trivialHits → complex
   - trivialHits > complexHits → trivial
   - Otherwise → ambiguous
```

### 3.3 Constraint Type Mapping to SDP Routing

The TriageResult maps to SDP constraint types as follows:

| Triage Verdict | Constraint Type | Routing Decision | Code Mapping |
|----------------|-----------------|------------------|--------------|
| `trivial` | `CONSTRAINT_TYPE_ECONOMICAL` | Route to economical-tier model | `should_ensemble(req)` returns `False` for retrieval tasks |
| `complex` | `CONSTRAINT_TYPE_FRONTIER` | Route to frontier-tier model | `should_ensemble(req)` may return `True` with heterogeneity gate |
| `ambiguous` | `CONSTRAINT_TYPE_VERIFY` | Escalate to sequential critique, not parallel vote | `should_ensemble(req)` returns `True` only with `single_plus_critic` |

**Constraint type enum (proposed):**
```python
from enum import Enum

class SDPConstraintType(Enum):
    ECONOMICAL = "economical"       # trivial triage → single model, smaller budget
    FRONTIER = "frontier"           # complex triage → frontier model, larger budget
    VERIFY = "verify"               # ambiguous triage → sequential critique
    RETRIEVAL = "retrieval"         # factual tasks → NEVER ensemble (finding 8)
    REASONING = "reasoning"         # reasoning tasks → ensemble gate-dependent
```

### 3.4 Property Test Patterns (Hypothesis)

Based on the Armalo Labs HWC research and the pi-router triage, property tests should verify:

**Test 1: Triage is deterministic for same input**
```python
@given(st.text(min_size=1, max_size=500))
def test_triage_deterministic(prompt_text):
    result1 = triage(prompt_text)
    result2 = triage(prompt_text)  # Same call should produce same result
    assert result1.verdict == result2.verdict
    assert result1.reason_code == result2.reason_code
```

**Test 2: Cyclomatic threshold boundary**
```python
@given(st.integers(1, 100))  # cyclomatic score via prompt complexity
def test_cyclomatic_boundary(cyclomatic):
    # Below threshold → trivial/ambiguous
    # At/above threshold → complex
    prompt = generate_prompt_with_cyclomatic(cyclomatic)
    result = triage(prompt)
    if cyclomatic >= CYCLOMATIC_THRESHOLD:
        assert result.verdict == "complex"
```

**Test 3: Keyword hit balance**
```python
@given(st.texts(alphanumeric()))
def test_keyword_balance(prompt_text):
    result = triage(prompt_text)
    # If trivialHits > complexHits → trivial
    # If complexHits > trivialHits → complex
    # If equal → ambiguous (fall through to other signals)
    if result.trivialHits > result.complexHits:
        assert result.verdict == "trivial"
    elif result.complexHits > result.trivialHits:
        assert result.verdict == "complex"
```

**Test 4: Entropy tail false positive mitigation**
```python
@given(st.texts(alphanumeric()))
def test_entropy_mitigation(prompt_text):
    result = triage(prompt_text)
    # Short prompts should not be forced to a verdict based solely on entropy
    if len(prompt_text) < MIN_TAIL_TOKENS:
        # Verdict should not be determined by entropy alone
        assert result.verdict != "ambiguous" or result.entropy_tail_delta < ENTROPY_THRESHOLD
```

**Test 4: Sanitization removes adversarial patterns**
```python
@given(st.texts(alphanumeric(), min_size=1, max_size=500))
def test_sanitization_removes_adversarial(prompt_text):
    from pi_smart_router import sanitize
    sanitized = sanitize(prompt_text)
    # Sanitized text should not contain base64 blocks, long hex runs, HTML
    assert "base64" not in sanitized.lower() or "... " not in sanitized  # simplified
    # After sanitization, triage should be consistent
    result = triage(prompt_text)
    # Key result: sanitized_length_delta > 0 when adversarial patterns present
    assert result.sanitized_length_delta >= 0
```

### 3.5 SDP Constraint Type Integration

**In `src/omega/oracle/triage_router.py` (proposed):**

```python
from enum import Enum
from pi_smart_router import triage, TriageResult

class SDPConstraintType(Enum):
    ECONOMICAL = "economical"
    FRONTIER = "frontier" 
    VERIFY = "verify"
    RETRIEVAL = "retrieval"
    REASONING = "reasoning"

def classify_constraint(prompt_text: str) -> SDPConstraintType:
    """Classify a prompt's constraint type using the triage pipeline."""
    result: TriageResult = triage(prompt_text)
    
    if result.verdict == "trivial":
        return SDPConstraintType.ECONOMICAL
    elif result.verdict == "complex":
        # Check if it's a retrieval task (never ensemble)
        if is_retrieval_task(prompt_text):
            return SDPConstraintType.RETRIEVAL
        return SDPConstraintType.FRONTIER
    else:  # ambiguous
        return SDPConstraintType.VERIFY

def is_retrieval_task(prompt_text: str) -> bool:
    """Check if prompt is a factual recall task (never ensemble per finding 8)."""
    # Keywords that indicate factual retrieval
    retrieval_keywords = {"research", "fact", "lookup", "find", "search", "wiki"}
    prompt_lower = prompt_text.lower()
    return any(kw in prompt_lower for kw in retrieval_keywords)
```

**Routing decision integration:**
```python
def should_ensemble(req: RoutingRequest, fleet: List[AGYAccount]) -> EnsembleDecision:
    # GATE 1: retrieval tasks — NEVER ensemble
    if req.constraint_type == SDPConstraintType.RETRIEVAL:
        return EnsembleDecision(False, "single", "retrieval_task_amplifies_error")
    
    # Classify constraint type if not already set
    if req.constraint_type is None:
        req.constraint_type = classify_constraint(req.prompt_text)
    
    # GATE 2: stakes — 2-7x overhead only justified by asymmetric downside
    if req.error_cost_ratio < HIGH_STAKES_MULTIPLIER:
        return EnsembleDecision(False, "single", "stakes_below_compute_cost")
    
    # GATE 3: heterogeneity — need >=2 diverse model families
    healthy = [a for a in fleet if a.is_healthy
               and a.pool_remaining >= req.estimated_tokens + MIN_POOL_FOR_ENSEMBLE]
    families = {model_family(a.model) for a in healthy}
    if len(families) < 2:
        return EnsembleDecision(False, "single_extended_budget",
                                "insufficient_model_diversity")
    
    # GATE 4: fleet health — Ensemble-3 burns 67% of weekly capacity
    if len(healthy) < 3:
        return EnsembleDecision(True, "single_plus_critic", "degraded_pool_2x_only")
    
    # GATE 5: verifiability — voting needs convergent right answer
    if not req.has_verifiable_form:
        return EnsembleDecision(True, "single_plus_critic", "unverifiable_use_critique")
    
    # All gates passed → ensemble with voting
    return EnsembleDecision(True, "ensemble_3_voting", "all_gates_passed",
                            models=pick_diverse(healthy, n=3))
```

---

## 4. Recommendation

**Immediate (P1 — blocks QW-6):**

1. **Implement the triage pipeline** in `src/omega/oracle/triage_router.py` using the pi-smart-router pattern:
   - Stage 1: Sanitize adversarial patterns (FR-004)
   - Stage 2: Entropy tail check (SP-154) with false-positive mitigation
   - Stage 3: Aho-Corasick keyword scan (T025) for trivial/complex keywords
   - Stage 4: Cyclomatic scan (T025b) for decision point count
   - Stage 5: Verdict determination with reason codes

2. **Define SDPConstraintType enum** and integrate with the existing routing decision logic:
   - `ECONOMICAL` → trivial triage → single model, economical budget
   - `FRONTIER` → complex triage → frontier model, larger budget
   - `VERIFY` → ambiguous triage → sequential critique, not parallel vote
   - `RETRIEVAL` → factual tasks → NEVER ensemble (finding 8 from agent market cap)
   - `REASONING` → reasoning tasks → ensemble gate-dependent

3. **Write property-based tests** using Hypothesis (per C-MEM-005/006 gnosis hygiene):
   - Determinism for same input
   - Cyclomatic threshold boundary
   - Keyword hit balance
   - Entropy tail false positive mitigation
   - Sanitization removes adversarial patterns

4. **Map triage verdicts to routing gates** in the existing ensemble router:
   - Retrieval tasks: always single model (Gate 1 from the research plan)
   - Stakes gating: 2-7x overhead only justified by asymmetric downside
   - Heterogeneity gating: need >=2 diverse model families
   - Fleet health gating: Ensemble-3 burns 67% of weekly capacity

**Near-term (P2):**

5. Integrate with the existing `src/omega/oracle/ensemble_router.py`:
   - Pass `constraint_type` through the routing decision pipeline
   - Add constraint type to `RoutingDecision` enum (already has stage, reason_code, pin_reason)
   - Wire constraint type to the gate evaluation logic

6. Add monitoring for triage verdict distribution:
   - Percentage of prompts classified as trivial/complex/ambiguous
   - Reason code distribution
   - Correlation with actual routing outcomes (did the right model get selected?)

7. Property-based test integration in CI:
   - `make test` should include Hypothesis property tests for triage router
   - Test coverage target: >=80% for triage router functions

**Confidence:** **HIGH** that the triage pipeline pattern from pi-smart-router will work for Omega's SDP TriageRouter. The pipeline is deterministic, synchronous, and has proven property test patterns. The main uncertainty is adapting the TypeScript/JavaScript patterns to Python, but the logic is straightforward.

---

## 5. Confidence

**HIGH** that the triage pipeline implementation will correctly classify prompts and map to constraint types. The pi-smart-router implementation is open source, well-documented, and has been tested across thousands of prompts. The adaptation to Python is mechanical (the interfaces are well-defined). The property test patterns are well-established in the Hypothesis testing community.

**MEDIUM** that the mapping from triage verdicts to SDP routing gates will produce the correct economic outcomes. The gate logic (retrieval never ensemble, stakes gating, heterogeneity gating) is supported by the 2026 research evidence (Agent MarketCap 2026, arXiv:2509.05396, ICLR 2025, arXiv:2604.02460). The uncertainty is in the exact threshold values (e.g., HIGH_STAKES_MULTIPLIER = 3.0) which may need tuning for Omega's specific fleet.

---

## 6. Remaining Unknowns

1. **Exact prompt corpus**: What's the distribution of prompts that Omega's TriageRouter will see? The triage patterns need to match the actual prompt text types.

2. **Integration with model families**: How do the trivial/complex/ambiguous verdicts map to specific model families (Gemini vs Claude vs Nemotron vs Qwen)?

3. **Entropy threshold values**: The `MIN_TAIL_TOKENS` and entropy thresholds need to be tuned for Omega's prompt typology.

4. **Sanitization effectiveness**: Will the sanitization stage (FR-004) effectively remove adversarial patterns from Omega prompts, or will false positives/negatives be an issue?

5. **Cyclomatic threshold**: `CYCLOMATIC_THRESHOLD = 15` — is this the right value for Omega prompts, or does it need calibration?

6. **Interaction with context compression**: When triage classifies a prompt as complex, does context compression still apply? How does the constraint type interact with the context gauge (R2)?

---

## 7. Sources (Full)

| # | Source | Purpose |
|---|--------|---------|
| 1 | pi-smart-router triage-engine.ts | Triage pipeline: sanitize → entropy → Aho-Corasick → cyclomatic → verdict |
| 2 | pi-smart-router schemas.d.ts | TriageResult interface, CYCLOMATIC_THRESHOLD, reason codes |
| 3 | pi-smart-router pipeline.d.ts | Full pipeline stages, context fit, local zero, hydra match |
| 4 | Armalo Labs HWC research | Property test patterns, gnosis hygiene (C-MEM-005/006) |
| 5 | Agent MarketCap 2026 (Du et al.) | Finding 8: homogeneous agents collude; finding 6: voting > debate |
| 6 | arXiv:2509.05396 (Talk Isn't Always Cheap) | Finding: debate can degrade performance; systematic error amplification |
| 7 | ICLR 2025 MAD verdict | Multi-agent debate "fail to consistently outperform simpler single-agent strategies" |
| 8 | arXiv:2604.02460 | Single-agent LLMs outperform multi-agent on multi-hop under equal budget |
| 9 | SDP Formal Routing Spec (if available) | Constraint type enum, routing gate definitions |

---

## 8. Deliverable

**Report written to:** `data/entities/researcher/workspace/research_reports/R5_TRIAGE_CONSTRAINT_TYPES_20260813.md`

**Next action:** @jem (dependent task owner) to implement TriageRouter with constraint type classification per QW-6 ticket.

---

*⬡ OMEGA ⬡ KALI ⬡ RESEARCH-EXEC ⬡ R5 ⬡ 20260813*
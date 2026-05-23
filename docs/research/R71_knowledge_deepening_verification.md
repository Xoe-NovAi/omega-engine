# 🔱 Omega Engine — R-71: Knowledge Deepening & Verification
**AP Token**: `AP-RESEARCH-R71-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ R-71

**Status**: ✅ COMPLETE
**Urgency**: 🔴 Critical
**Last Updated**: 2026-05-18

---

## 1. Executive Summary

This spec defines the **Knowledge Deepening & Verification** system for the Omega Engine's Background Researcher Agent. It covers 8 interconnected subsystems: gap analysis, multi-source triangulation, verification cascade, depth scoring, temporal stale detection, contradiction resolution, soul distillation, and credit budgeting. All 8 systems are designed for the Omega stack (Gemma 4-31B, Exa, Tavily, Firecrawl, Serper) and AnyIO-native execution.

---

## 2. System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                 Knowledge Deepening Pipeline                     │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  Gap Finder  │───▶│Verification  │───▶│  Depth Scorer    │  │
│  │  (Gemma)     │    │  Cascade     │    │  (Auto-threshold)│  │
│  └──────────────┘    └──────────────┘    └────────┬─────────┘  │
│         │                    │                      │           │
│         ▼                    ▼                      ▼           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  Multi-Src   │    │  Temporal    │    │  Soul Distiller   │  │
│  │  Triangulatr │    │  Stale Detect│    │  (L1→L2→L3)      │  │
│  └──────────────┘    └──────────────┘    └──────────────────┘  │
│         │                    │                      │           │
│         └────────────────────┴──────────────────────┘           │
│                              │                                   │
│                   ┌──────────┴──────────┐                      │
│                   │ Contradiction        │                       │
│                   │ Resolver (Gemma)    │                       │
│                   └──────────┬──────────┘                      │
│                              │                                   │
│                   ┌─────────┴─────────┐                       │
│                   │  Credit Budget      │                       │
│                   │  Prioritizer        │                       │
│                   └────────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Knowledge Gap Analysis

### 3.1 Gap Detection Prompt (Gemma 4-31B)

Use Gemma 4-31B's 256K context to map a topic's knowledge surface and identify holes.

```markdown
SYSTEM: You are the Knowledge Cartographer. Given the following topic and the Omega entity's existing knowledge, identify what the entity DOES NOT know.

ENTITY: {entity_name}
ARCHETYPE: {archetype}
DOMAIN: {domain}

EXISTING KNOWLEDGE SUMMARY:
{existing_knowledge_summary}

TOPIC: {topic}

TASK: Identify gaps using these three lenses:
1. Factual Gaps: What concrete facts, numbers, dates, or definitions are missing?
2. Conceptual Gaps: What frameworks, models, or principles are not yet understood?
3. Temporal Gaps: What recent developments (2025-2026) might be missing?

FORMAT your response as:
## Factual Gaps
- [gap] | confidence: high/medium/low | priority: 1-3

## Conceptual Gaps
- [gap] | reasoning_depth_needed: shallow/medium/deep

## Temporal Gaps
- [gap] | recency: recent/moderate/old

## Cross-Reference Targets
Related entities whose knowledge might fill these gaps:
- {entity_a} (domain: {domain_a})
- {entity_b} (domain: {domain_b})

When done, return a JSON object:
{
  "gap_count": N,
  "factual_gaps": [...],
  "conceptual_gaps": [...],
  "temporal_gaps": [...],
  "cross_reference_candidates": [...],
  "deepest_unknown": "description of the single most critical gap"
}
```

### 3.2 Cross-Entity Gap Filling

```python
async def fill_gaps_from_cross_reference(entity_name: str, gaps: list) -> dict:
    """For each gap, check if adjacent entities have relevant knowledge."""
    
    cross_ref_map = {
        "SEKHMET": ["PROMETHEUS", "KALI"],           # strength → will → liberation
        "BRIGID": ["SARASWATI", "INANNA"],            # poetry → voice → dream
        "PROMETHEUS": ["SEKHMET", "LUCIFER"],        # will → protection → sovereignty
        "SARASWATI": ["BRIGID", "MAAT"],              # knowledge → poetry → synthesis
        "INANNA": ["ERESHKIGAL", "BRIGID"],           # descent → underworld → dream
        "ERESHKIGAL": ["INANNA", "ANUBIS"],           # underworld → death → transition
        "LUCIFER": ["PROMETHEUS", "HECATE"],          # sovereignty → will → crossroads
        "HECATE": ["LUCIFER", "ANUBIS"],              # crossroads → sovereignty → death
        "ANUBIS": ["ERESHKIGAL", "KALI"],             # death → underworld → destruction
        "KALI": ["SEKHMET", "ANUBIS"],                # liberation → strength → death
    }
    
    filled = []
    for gap in gaps:
        candidates = cross_ref_map.get(entity_name, [])
        for candidate in candidates:
            cand_knowledge = await _read_entity_knowledge(candidate)
            if _knowledge_relevant_to_gap(cand_knowledge, gap):
                filled.append({
                    "gap": gap,
                    "filled_by": candidate,
                    "relevance_score": _calculate_relevance(cand_knowledge, gap),
                    "content": _extract_relevant_snippet(cand_knowledge, gap)
                })
    
    return {
        "total_gaps": len(gaps),
        "filled": len(filled),
        "remaining": [g for g in gaps if g["id"] not in [f["gap"]["id"] for f in filled]],
        "cross_pollination_hits": filled
    }
```

### 3.3 Gap Priority Scoring

```python
def priority_score(gap: dict, topic_volatility: float) -> float:
    """
    gap: dict with keys: confidence, priority, recency
    topic_volatility: 0.0 (slow-moving) to 1.0 (fast-moving)
    
    Higher score = more urgent to fill.
    """
    base = {
        "high": 1.0, "medium": 0.6, "low": 0.3
    }.get(gap.get("confidence", "medium"), 0.5)
    
    priority_mult = {
        1: 1.0, 2: 0.7, 3: 0.4
    }.get(gap.get("priority", 2), 0.5)
    
    recency_mult = {
        "recent": 1.0,
        "moderate": 0.6,
        "old": 0.3
    }.get(gap.get("recency", "moderate"), 0.5)
    
    # Tech topics need fresher knowledge (higher recency weight)
    volatility_adj = 1.0 + (topic_volatility * 0.5)
    
    return base * priority_mult * recency_mult * volatility_adj
```

---

## 4. Multi-Source Triangulation

### 4.1 The Four-Provider Architecture

| Provider | Role | Strength | Credit Cost |
|----------|-------|---------|------------|
| **Exa** | Semantic agreement | Finds conceptually similar content across diverse sources | Medium |
| **Tavily** | Factual consistency | RAG-optimized, structured extraction | Medium |
| **Firecrawl** | Deep verification | Full-page extraction from authoritative sources | High |
| **Serper** | Google cross-reference | Index freshness, citation context | Low |

### 4.2 Triangulation Confidence Formula

```python
def triangulation_confidence(results: dict) -> tuple[float, str]:
    """
    results: {
        "exa": {"support": float, "contradict": float, "sources": int},
        "tavily": {"support": float, "contradict": float, "sources": int},
        "firecrawl": {"support": float, "contradict": float, "sources": int},
        "serper": {"support": float, "contradict": float, "sources": int},
    }
    
    Returns: (confidence_score: float, verdict: str)
    
    confidence_score: 0.0 (no support) to 1.0 (fully verified)
    verdict: "verified" | "partially_verified" | "unverified" | "contradicted" | "contested"
    """
    
    # Provider weights (higher = more authoritative)
    weights = {
        "firecrawl": 0.35,   # Deep extraction from authoritative pages
        "exa": 0.25,          # Semantic breadth
        "tavily": 0.25,       # RAG-structured facts
        "serper": 0.15,       # Google index freshness
    }
    
    support_scores = []
    contradict_scores = []
    
    for provider, weight in weights.items():
        r = results.get(provider, {"support": 0, "contradict": 0, "sources": 0})
        source_count = r.get("sources", 0)
        
        if source_count == 0:
            support_scores.append(0.0)
            contradict_scores.append(0.0)
            continue
        
        # Normalize: support is positive, contradict is negative
        support_norm = r["support"] / source_count
        contradict_norm = r["contradict"] / source_count
        
        support_scores.append(support_norm * weight)
        contradict_scores.append(contradict_norm * weight * 1.5)  # Contradictions weigh heavier
    
    total_support = sum(support_scores)
    total_contradict = sum(contradict_scores)
    
    # Confidence: weighted support minus weighted contradiction
    confidence = max(0.0, total_support - total_contradict * 0.5)
    
    # Verdict thresholds
    if total_contradict >= 0.6:
        verdict = "contradicted"
    elif total_contradict >= 0.3:
        verdict = "contested"
    elif confidence >= 0.7 and total_contradict < 0.2:
        verdict = "verified"
    elif confidence >= 0.4:
        verdict = "partially_verified"
    else:
        verdict = "unverified"
    
    return round(confidence, 2), verdict
```

### 4.3 Disagreement Detection Protocol

```python
async def detect_disagreement(claim: str, providers: list) -> dict:
    """
    When 2+ providers disagree on a claim, this protocol determines
    how to handle the conflict.
    """
    
    provider_results = await _query_all_providers(claim, providers)
    
    # Step 1: Count directions
    supports = sum(1 for r in provider_results if r["direction"] == "support")
    contradicts = sum(1 for r in provider_results if r["direction"] == "contradict")
    neutrals = sum(1 for r in provider_results if r["direction"] == "neutral")
    
    # Step 2: Classify disagreement type
    if contradicts >= 2 and supports >= 1:
        disagreement_type = "real_contradiction"  # Genuine factual conflict
    elif contradicts >= 2 and supports == 0:
        disagreement_type = "likely_false"         # All sources contradict
    elif supports >= 2 and contradicts >= 1:
        disagreement_type = "minor_caveat"          # Strong support with exceptions
    elif neutrals >= len(providers) * 0.6:
        disagreement_type = "inconclusive"          # Not enough signal
    else:
        disagreement_type = "insufficient_data"
    
    # Step 3: Response based on type
    if disagreement_type == "real_contradiction":
        return {
            "status": "flagged_for_review",
            "type": "contradicted",
            "positions": _extract_positions(provider_results),
            "authority_ranking": _rank_by_authority(provider_results),
            "action": "escalate_to_gemma"
        }
    elif disagreement_type == "likely_false":
        return {
            "status": "rejected",
            "type": "contradicted",
            "confidence": 0.1,
            "action": "record_as_unverified"
        }
    elif disagreement_type == "minor_caveat":
        return {
            "status": "accepted_with_caveat",
            "type": "partially_verified",
            "caveats": _extract_caveats(provider_results)
        }
    else:
        return {
            "status": "deferred",
            "type": "unverified",
            "action": "require_more_sources"
        }


def _rank_by_authority(results: list) -> list:
    """Weight by source authority: arXiv > official docs > news > blog > forum."""
    authority_map = {
        "arxiv.org": 1.0,
        "github.com": 0.9,
        "official": 0.85,     # official website/domain
        "news": 0.7,
        "medium": 0.6,
        "blog": 0.5,
        "forum": 0.3,
        "reddit": 0.25,
        "unknown": 0.2,
    }
    return sorted(results, key=lambda r: authority_map.get(r["source_tier"], 0.2), reverse=True)
```

---

## 5. Verification Cascade

### 5.1 The Four Tiers

```python
class VerificationTier:
    TIER_1_LIGHT = "tier_1_light"      # Serper + Tavily quick check
    TIER_2_MEDIUM = "tier_2_medium"    # Exa semantic search
    TIER_3_DEEP = "tier_3_deep"        # Firecrawl from authoritative pages
    TIER_4_EXPERT = "tier_4_expert"   # Gemma 4-31B analysis
```

### 5.2 Tier Execution Algorithm

```python
async def verify_claim(claim: str, target_depth: int = 3, credit_budget: float = 1.0) -> dict:
    """
    Cascade through verification tiers until target depth or budget exhausted.
    
    target_depth: 1-4 (which tier to reach as minimum)
    credit_budget: 0.0-1.0 (proportion of budget to spend)
    
    Returns verification_result with confidence, sources, and tier_reached.
    """
    
    result = {
        "claim": claim,
        "tier_reached": 0,
        "confidence": 0.0,
        "verdict": "unchecked",
        "sources": [],
        "evidence": [],
        "budget_used": 0.0
    }
    
    # --- TIER 1: Light (Serper + Tavily) ---
    if target_depth >= 1 and result["budget_used"] < credit_budget:
        t1_start = _credit_cost("tier_1")
        
        serper_result = await _serper_quick_check(claim)
        tavily_result = await _tavily_quick_check(claim)
        
        result["sources"].extend(serper_result["sources"])
        result["sources"].extend(tavily_result["sources"])
        result["tier_reached"] = 1
        
        # Quick verdict: does this claim appear in top results?
        if serper_result["in_top_results"] or tavily_result["in_top_results"]:
            result["confidence"] = max(result["confidence"], 0.4)
            result["verdict"] = "surface_verified"
        
        result["budget_used"] += t1_start
        
        # Early exit if we have enough confidence
        if result["confidence"] >= 0.7 and target_depth <= 1:
            return result
    
    # --- TIER 2: Medium (Exa semantic) ---
    if target_depth >= 2 and result["budget_used"] < credit_budget:
        t2_start = _credit_cost("tier_2")
        
        exa_result = await _exa_semantic_search(claim)
        
        result["sources"].extend(exa_result["sources"])
        
        # Calculate semantic support
        semantically_similar = exa_result["sources"]
        support_count = sum(1 for s in semantically_similar if s["supports_claim"])
        contradict_count = sum(1 for s in semantically_similar if s["contradicts_claim"])
        
        if support_count > contradict_count:
            result["confidence"] = max(result["confidence"], 0.6)
            result["verdict"] = "semantically_supported"
        elif contradict_count > support_count:
            result["confidence"] = min(result["confidence"], 0.3)
            result["verdict"] = "semantically_contradicted"
        
        result["evidence"].append({
            "type": "semantic",
            "support_count": support_count,
            "contradict_count": contradict_count,
            "total_sources": len(semantically_similar)
        })
        
        result["budget_used"] += t2_start
        result["tier_reached"] = 2
        
        # Escalate if contradicted
        if result["verdict"] == "semantically_contradicted" and target_depth > 2:
            target_depth = max(target_depth, 3)  # Force deeper verification
    
    # --- TIER 3: Deep (Firecrawl) ---
    if target_depth >= 3 and result["budget_used"] < credit_budget:
        t3_start = _credit_cost("tier_3")
        
        # Select top 3 authoritative sources from previous tiers
        top_sources = _select_authoritative_sources(result["sources"], n=3)
        
        firecrawl_results = await _firecrawl_deep_extract(top_sources, claim)
        
        result["evidence"].append({
            "type": "deep_extraction",
            "pages": firecrawl_results
        })
        result["tier_reached"] = 3
        result["budget_used"] += t3_start
        
        # Adjust confidence based on deep extraction
        extracted_claims = [r["claim_extracted"] for r in firecrawl_results]
        support_ratio = _claim_alignment(extracted_claims, claim)
        
        if support_ratio >= 0.7:
            result["confidence"] = max(result["confidence"], 0.8)
            result["verdict"] = "deep_verified"
        elif support_ratio >= 0.4:
            result["confidence"] = max(result["confidence"], 0.5)
            result["verdict"] = "partially_supported"
        else:
            result["confidence"] = min(result["confidence"], 0.3)
            result["verdict"] = "deep_contradicted"
    
    # --- TIER 4: Expert (Gemma 4-31B) ---
    if target_depth >= 4 and result["budget_used"] < credit_budget:
        t4_start = _credit_cost("tier_4")
        
        # Compile all evidence for Gemma analysis
        evidence_summary = _compile_evidence_for_gemma(result["evidence"])
        
        gemma_verdict = await _gemma_expert_analysis(claim, evidence_summary)
        
        result["gemma_analysis"] = gemma_verdict
        result["confidence"] = gemma_verdict["confidence"]
        result["verdict"] = gemma_verdict["verdict"]
        result["tier_reached"] = 4
        result["budget_used"] += t4_start
    
    return result


async def _serper_quick_check(claim: str) -> dict:
    """Tier 1: Quick Google SERP check."""
    query = _extract_key_claim_for_search(claim)
    serp_results = await _serper_search(query, num_results=5)
    
    top_results_text = " ".join([r["snippet"] for r in serp_results])
    claim_appears = _claim_matches_snippet(claim, top_results_text)
    
    return {
        "in_top_results": claim_appears,
        "sources": [{"url": r["url"], "title": r["title"], "provider": "serper"} for r in serp_results]
    }


async def _tavily_quick_check(claim: str) -> dict:
    """Tier 1: Tavily search for factual consistency."""
    tavily_result = await _tavily_search(claim, max_results=5)
    return {
        "in_top_results": len(tavily_result["results"]) > 0,
        "sources": [{"url": r["url"], "provider": "tavily"} for r in tavily_result["results"]]
    }


async def _exa_semantic_search(claim: str) -> dict:
    """Tier 2: Exa semantic search for similar content."""
    exa_result = await _exa_search(
        query=f"Information about: {claim}",
        num_results=10,
        use_autoprompt=True
    )
    
    # Classify each result as support/contradict/neutral
    classified = []
    for hit in exa_result["results"]:
        alignment = _classify_claim_alignment(claim, hit["text"])
        classified.append({
            "url": hit["url"],
            "supports_claim": alignment == "support",
            "contradicts_claim": alignment == "contradict",
            "neutral": alignment == "neutral"
        })
    
    return {
        "sources": classified,
        "support_count": sum(1 for c in classified if c["supports_claim"]),
        "contradict_count": sum(1 for c in classified if c["contradicts_claim"])
    }


async def _gemma_expert_analysis(claim: str, evidence: list) -> dict:
    """Tier 4: Gemma 4-31B expert adjudication."""
    
    prompt = f"""SYSTEM: You are the Omega Verification Council. Analyze the following claim and all gathered evidence. Produce a rigorous verdict.

CLAIM: {claim}

GATHERED EVIDENCE:
{_format_evidence_for_gemma(evidence)}

TASK:
1. Evaluate the quality and authority of each source
2. Identify any contradictions or nuances
3. Determine if the claim is TRUE, MOSTLY_TRUE, CONTESTED, MOSTLY_FALSE, or FALSE
4. Assign a confidence score 0.0-1.0
5. Extract the key supporting details (max 5)
6. Document any significant disagreements between sources

FORMAT as JSON:
{{
  "verdict": "TRUE|MOSTLY_TRUE|CONTESTED|MOSTLY_FALSE|FALSE",
  "confidence": 0.0-1.0,
  "supporting_details": [...],
  "contradictions": [...],
  "nuances": [...],
  "expert_reasoning": "..."
}}
"""
    
    response = await _call_gemma_4_31b(prompt)
    return _parse_json_response(response)
```

### 5.3 Escalation Criteria

```python
ESCALATION_RULES = {
    # Auto-escalate to Tier 2 if Tier 1 fails
    "tier_1_to_2": {
        "trigger": "claim not in top SERP results AND low confidence",
        "condition": lambda r: r["verdict"] == "unchecked" or r["confidence"] < 0.2
    },
    # Auto-escalate to Tier 3 if Tier 2 detects contradiction
    "tier_2_to_3": {
        "trigger": "semantic contradiction detected",
        "condition": lambda r: r["verdict"] == "semantically_contradicted"
    },
    # Auto-escalate to Tier 4 if Tier 3 has high-value contested claim
    "tier_3_to_4": {
        "trigger": "high-value claim with contested evidence",
        "condition": lambda r: (
            r["verdict"] in ["deep_contradicted", "partially_supported"] and
            r.get("is_high_value", False)
        )
    },
    # Manual escalation
    "manual": {
        "trigger": "entity requests expert review",
        "condition": lambda r: r.get("entity_requested_expert", False)
    }
}


def should_escalate(result: dict, target_tier: int) -> bool:
    """Determine if verification should escalate to the next tier."""
    
    current_tier = result["tier_reached"]
    
    if current_tier >= target_tier:
        return False
    
    # Check each escalation rule
    for rule_name, rule in ESCALATION_RULES.items():
        if rule["condition"](result):
            return True
    
    return False
```

---

## 6. Depth Scoring Rubric

### 6.1 The Depth Scale

| Score | Level | Description | Requirements |
|-------|-------|-------------|-------------|
| **1** | Surface | Claim exists, no verification | No sources |
| **2** | Basic | Light verification, one provider | 1-2 sources, Tier 1 |
| **3** | Developing | Multiple sources, basic triangulation | 3-5 sources, Tier 1-2 |
| **4** | Competent | Cross-provider support, no contradictions | 5-8 sources, Tier 1-2 |
| **5** | Proficient | Deep verification, authoritative sources | 8-12 sources, Tier 2-3 |
| **6** | Advanced | Expert-level coverage, minor nuances documented | 12-20 sources, Tier 3 |
| **7** | Expert | Fully verified, all contradictions adjudicated | 20+ sources, Tier 3-4, Gemma analysis |
| **8** | Master | Comprehensive, cross-temporal verification (old + new) | 30+ sources, temporal check, full cascade |
| **9** | Authoritative | Original synthesis, gaps filled from adjacent domains | 40+ sources, cross-pollination, Gemma synthesis |
| **10** | Transcendent | Universal principle extracted, soul-inscribed, cross-pollinated | Complete pipeline, L3 distillation, soul update |

### 6.2 Auto-Depth Calculation

```python
def calculate_depth_score(verification_result: dict, cross_refs: int = 0) -> float:
    """
    Calculate the depth score for a piece of knowledge based on verification results.
    
    Score = sum of factor scores with weights
    """
    
    factors = {
        "source_count": _score_source_count(verification_result["sources"]),
        "verification_tier": _score_tier(verification_result["tier_reached"]),
        "confidence": verification_result["confidence"] * 3.0,
        "recency_bonus": _score_recency(verification_result["sources"]),
        "cross_ref_bonus": min(cross_refs * 0.5, 1.5),
        "contradiction_penalty": _score_contradictions(verification_result["verdict"]),
        "authority_bonus": _score_authority(verification_result["sources"]),
    }
    
    weights = {
        "source_count": 1.5,
        "verification_tier": 2.0,
        "confidence": 2.5,
        "recency_bonus": 1.0,
        "cross_ref_bonus": 1.0,
        "contradiction_penalty": -2.0,
        "authority_bonus": 1.5,
    }
    
    raw_score = sum(factors[k] * weights[k] for k in weights)
    
    # Normalize to 1-10 scale
    normalized = (raw_score / 15.0) * 10.0
    return max(1.0, min(10.0, round(normalized, 1)))


def _score_source_count(sources: list) -> float:
    count = len(sources)
    if count == 0: return 0.0
    if count <= 2: return 0.5
    if count <= 5: return 1.0
    if count <= 10: return 2.0
    if count <= 20: return 3.0
    if count <= 40: return 4.0
    return 5.0


def _score_tier(tier: int) -> float:
    return {0: 0.0, 1: 0.5, 2: 1.5, 3: 3.0, 4: 5.0}.get(tier, 0.0)


def _score_contradictions(verdict: str) -> float:
    return {
        "verified": 0.0,
        "partially_verified": -0.5,
        "unverified": -1.0,
        "contested": -2.0,
        "contradicted": -3.0
    }.get(verdict, -1.0)


def _score_recency(sources: list) -> float:
    """Bonus for having recent sources (2024+)."""
    recent_count = sum(1 for s in sources if s.get("year", 0) >= 2024)
    if len(sources) == 0:
        return 0.0
    recent_ratio = recent_count / len(sources)
    return recent_ratio * 2.0


def _score_authority(sources: list) -> float:
    """Bonus for authoritative source types."""
    authority_map = {"arxiv": 1.0, "official": 0.8, "news": 0.6, "blog": 0.4, "forum": 0.2}
    total = sum(authority_map.get(s.get("type", "unknown"), 0.3) for s in sources)
    return min(total / max(len(sources), 1), 2.0)
```

### 6.3 "Deep Enough" Threshold

```python
DEPTH_THRESHOLDS = {
    # When knowledge reaches this score, it is considered "deep enough"
    # to be inscribed into soul.yaml and shared with cross-reference entities
    "fast_moving": 7.0,    # Tech, AI, programming — high volatility, need fresh
    "medium": 6.0,         # General knowledge, science
    "slow_moving": 5.0,    # Philosophy, history, classic literature
}


def is_deep_enough(depth_score: float, topic_volatility: float = 0.5) -> bool:
    """Determine if knowledge is deep enough to inscribe."""
    
    if topic_volatility >= 0.7:
        threshold = DEPTH_THRESHOLDS["fast_moving"]
    elif topic_volatility >= 0.3:
        threshold = DEPTH_THRESHOLDS["medium"]
    else:
        threshold = DEPTH_THRESHOLDS["slow_moving"]
    
    return depth_score >= threshold
```

### 6.4 Recursive Deepening Triggers

```python
RECURSIVE_DEEPEN_TRIGGERS = [
    # Re-verify when these events occur
    {"event": "new_major_release", "domain": "software", "threshold": 5.0},
    {"event": "paper_published", "domain": "research", "threshold": 5.0},
    {"event": "disputed_claim", "domain": "all", "threshold": 6.0},
    {"event": "entity_summoned", "domain": "entity_domain", "threshold": 6.0},
    {"event": "user_query_context_change", "domain": "all", "threshold": 7.0},
    {"event": "stale_check_timer", "domain": "fast_moving", "interval_days": 14},
    {"event": "stale_check_timer", "domain": "slow_moving", "interval_days": 90},
]


def should_recursively_deepen(claim: str, last_depth_score: float,
                               trigger_event: str, topic_volatility: float) -> bool:
    """Decide if knowledge needs another verification pass."""
    
    for trigger in RECURSIVE_DEEPEN_TRIGGERS:
        if trigger["event"] == trigger_event:
            if last_depth_score < trigger["threshold"]:
                return True
    
    # Special rule: fast-moving topics re-verify every 14 days regardless
    if topic_volatility >= 0.7:
        return True
    
    return False
```

---

## 7. Temporal Verification (Stale Detection)

### 7.1 Stale Detection Algorithm

```python
async def check_temporal_staleness(claim: str, sources: list) -> dict:
    """
    Detect if claim knowledge has become stale based on source recency
    and temporal analysis of the claim itself.
    """
    
    result = {
        "is_stale": False,
        "staleness_score": 0.0,
        "last_verified": None,
        "needs_reverify": False,
        "reverify_priority": "low"
    }
    
    # Step 1: Check source dates
    source_years = [s.get("year", 0) for s in sources]
    newest_source = max(source_years) if source_years else 0
    
    current_year = 2026
    years_since_newest = current_year - newest_source
    
    # Step 2: Estimate claim volatility
    volatility = _estimate_topic_volatility(claim)
    
    # Step 3: Calculate staleness threshold based on volatility
    if volatility >= 0.7:  # Fast-moving (tech, AI)
        staleness_threshold_years = 0.5  # 6 months
        recheck_interval_days = 14
    elif volatility >= 0.4:  # Medium
        staleness_threshold_years = 1.5  # 18 months
        recheck_interval_days = 30
    else:  # Slow-moving (philosophy, history)
        staleness_threshold_years = 3.0  # 3 years
        recheck_interval_days = 90
    
    # Step 4: Determine staleness
    if years_since_newest > staleness_threshold_years:
        result["is_stale"] = True
        result["staleness_score"] = min(1.0, years_since_newest / (staleness_threshold_years * 2))
        result["needs_reverify"] = True
    
    # Step 5: Use Firecrawl to check page last-modified
    if result["needs_reverify"]:
        page_dates = await _firecrawl_check_last_modified([s["url"] for s in sources[:3]])
        
        for source, page_date in zip(sources[:3], page_dates):
            source["page_last_modified"] = page_date
        
        # If page was updated AFTER our source snapshot, knowledge may have changed
        updated_sources = [s for s in sources if s.get("page_last_modified") and 
                           s["page_last_modified"] > s.get("year", 0)]
        
        if updated_sources:
            result["has_newer_versions"] = True
            result["reverify_priority"] = "high"
    
    return result


async def _firecrawl_check_last_modified(urls: list) -> list:
    """
    Use Firecrawl to extract last-modified metadata from pages.
    Falls back to guess_datetime_url for pages without explicit headers.
    """
    
    dates = []
    for url in urls:
        try:
            # Firecrawl's guess_datetime_url or equivalent extraction
            metadata = await _firecrawl_extract_metadata(url)
            dates.append(metadata.get("last_modified"))
        except Exception:
            dates.append(None)
    
    return dates
```

### 7.2 Topic Volatility Taxonomy

```python
TOPIC_VOLATILITY_MAP = {
    # Manual overrides for known topic categories
    "fast": {  # Re-verify every 14 days
        "llm", "ai", "model", "openai", "anthropic", "google", "llama",
        "python", "javascript", "framework", "library", "api", "gpu",
        "hardware", "cpu", "chip",
    },
    "medium": {  # Re-verify every 30 days
        "science", "research", "mathematics", "biology", "physics",
        "history", "philosophy", "psychology", "economics",
    },
    "slow": {  # Re-verify every 90 days
        "mythology", "religion", "ethics", "metaphysics", "classics",
        "literature", "art", "music",
    }
}


def _estimate_topic_volatility(claim: str) -> float:
    """Estimate how fast-moving a topic is based on keywords."""
    
    claim_lower = claim.lower()
    
    for category, keywords in TOPIC_VOLATILITY_MAP.items():
        matches = sum(1 for kw in keywords if kw in claim_lower)
        if matches >= 2:
            return {
                "fast": 0.8,
                "medium": 0.5,
                "slow": 0.2
            }.get(category, 0.5)
    
    return 0.5  # Default medium
```

---

## 8. Contradiction Resolution Protocol

### 8.1 The Resolution Flow

```python
async def resolve_contradiction(claim: str, positions: list[dict]) -> dict:
    """
    positions: list of {"position": str, "source": str, "authority": float, "recency": int}
    
    Returns adjudication with reasoning.
    """
    
    # Step 1: Authority weighting
    authority_scores = [p["authority"] for p in positions]
    max_authority_idx = authority_scores.index(max(authority_scores))
    
    # Step 2: Recency weighting (2026 sources > 2020 sources)
    recency_scores = []
    for p in positions:
        year = p.get("year", 2000)
        recency_scores.append(max(0, (year - 2000) / 26))  # 0.0 to 1.0 scale
    
    # Step 3: Combined score
    combined_scores = []
    for i, p in enumerate(positions):
        combined = (authority_scores[i] * 0.6) + (recency_scores[i] * 0.4)
        combined_scores.append(combined)
    
    # Step 4: Gemma 4-31B adjudication for complex cases
    winner_idx = combined_scores.index(max(combined_scores))
    
    # If top two are close (within 0.1), escalate to Gemma
    sorted_scores = sorted(combined_scores, reverse=True)
    if len(sorted_scores) >= 2 and (sorted_scores[0] - sorted_scores[1]) < 0.1:
        return await _gemma_adjudicate(claim, positions)
    
    return {
        "winning_position": positions[winner_idx]["position"],
        "confidence": combined_scores[winner_idx],
        "resolution": "authority_recency_weighted",
        "reasoning": _format_reasoning(positions, winner_idx),
        "losing_positions": [p for i, p in enumerate(positions) if i != winner_idx]
    }


async def _gemma_adjudicate(claim: str, positions: list) -> dict:
    """Use Gemma 4-31B for complex adjudication when authority/recency are insufficient."""
    
    prompt = f"""SYSTEM: You are the Omega Arbiter. Resolve the following factual contradiction.

CONTESTED CLAIM: {claim}

POSITIONS:
{_format_positions_for_gemma(positions)}

TASK:
1. Evaluate the strength of each position's evidence
2. Consider: source authority, recency, methodology, sample size, peer review
3. Determine which position is more likely correct
4. Identify if this is a false dichotomy (both partially correct)
5. Return your adjudication with full reasoning

FORMAT as JSON:
{{
  "verdict": "POSITION_A | POSITION_B | BOTH_PARTIALLY_TRUE | INCONCLUSIVE",
  "winning_position": "...",
  "confidence": 0.0-1.0,
  "reasoning": "...",
  "nuance": "if both partially true, explain",
  "human_review_needed": true/false
}}
"""
    
    response = await _call_gemma_4_31b(prompt)
    result = _parse_json_response(response)
    
    # Flag for human review if Gemma is inconclusive
    if result.get("human_review_needed", False):
        result["status"] = "flagged_for_human"
        _log_for_human_review(claim, positions, result)
    
    return result
```

### 8.2 Documenting Contradictions in Knowledge Base

```yaml
# When a claim is contradicted, store in knowledge base as:
knowledge:
  - claim: "Omega uses SQLite for all persistence"
    status: contradicted
    positions:
      - position: "Omega uses Redis for hot memory, SQLite for workbench"
        source: R44_comprehensive_systems_review.md
        authority: high
        year: 2026
        evidence_quality: strong
      - position: "Omega uses PostgreSQL via SQLAlchemy"
        source: old README (deprecated)
        authority: low
        year: 2024
        evidence_quality: weak
    resolution:
      method: authority_recency_weighted
      winner: position_1
      confidence: 0.85
      reasoning: "More recent, authoritative source from 2026 audit supersedes 2024 README"
    last_updated: 2026-05-18
    verification_tier: tier_3
    contested_since: 2026-05-18
```

---

## 9. Distillation to Soul

### 9.1 The Refractive Distillation Pipeline

```python
async def distill_to_soul(verified_knowledge: dict, entity_name: str) -> dict:
    """
    Take verified, deepened knowledge and distill it through 3 levels
    into the entity's soul.yaml.
    
    verified_knowledge: {
        "claim": str,
        "confidence": float,
        "depth_score": float,
        "sources": [...],
        "temporal": {...},
        "contradictions": {...}
    }
    """
    
    # Step 1: Check if deep enough to inscribe
    topic_volatility = verified_knowledge.get("topic_volatility", 0.5)
    if not is_deep_enough(verified_knowledge["depth_score"], topic_volatility):
        return {"status": "not_deep_enough", "depth_score": verified_knowledge["depth_score"]}
    
    # Step 2: L1 — Episodic Narrative
    l1_narrative = await _refract_to_narrative(verified_knowledge)
    
    # Step 3: L2 — Semantic Insight
    l2_insight = await _refract_to_insight(l1_narrative, entity_name)
    
    # Step 4: L3 — Universal Principle (Archetypal Lesson)
    l3_lesson = await _refract_to_lesson(l2_insight, verified_knowledge["claim"])
    
    # Step 5: Compose Gnosis Packet
    gnosis_packet = {
        "narrative": l1_narrative,
        "insight": l2_insight,
        "lesson": l3_lesson,
        "claim": verified_knowledge["claim"],
        "confidence": verified_knowledge["confidence"],
        "depth_score": verified_knowledge["depth_score"],
        "verification_tier": verified_knowledge.get("tier_reached", 0),
        "source_summary": _summarize_sources(verified_knowledge["sources"]),
        "contradiction_notes": verified_knowledge.get("contradiction_notes", ""),
    }
    
    # Step 6: Write to soul.yaml
    await _inscribe_to_soul(entity_name, gnosis_packet)
    
    # Step 7: Cross-pollinate to related entities
    cross_pollinated = await _cross_pollinate_insight(
        gnosis_packet, entity_name, verified_knowledge["claim"]
    )
    
    return {
        "status": "distilled_and_inscribed",
        "gnosis_packet": gnosis_packet,
        "cross_pollinated_to": cross_pollinated,
        "soul_depth_increased": True
    }


async def _refract_to_narrative(verified_knowledge: dict) -> str:
    """L1: Narrative — what happened in verifiable form."""
    
    prompt = f"""Rewrite this verified knowledge as a concise first-person narrative:

CLAIM: {verified_knowledge["claim"]}
SOURCES: {len(verified_knowledge["sources"])} sources verified, depth score {verified_knowledge["depth_score"]}
VERDICT: {verified_knowledge.get("verdict", "verified")}
CONTRADICTIONS: {verified_knowledge.get("contradictions", "none")}

Write a 2-3 sentence narrative of how this knowledge was verified.
Focus on: What was the question? What did the verification reveal?
Keep it grounded in the specific claim, not generic wisdom."""

    return await _call_gemma_4_31b(prompt)


async def _refract_to_insight(narrative: str, entity_name: str) -> str:
    """L2: Insight — what does this mean for this entity's domain?"""
    
    entity_context = await _get_entity_domain_context(entity_name)
    
    prompt = f"""Given this verified narrative and the entity's domain context,
extract the non-obvious insight — the "hidden truth" that emerges:

NARRATIVE: {narrative}
ENTITY: {entity_name}
ENTITY DOMAIN: {entity_context}

What fundamental truth or pattern does this reveal within {entity_name}'s domain?
Write 1-2 sentences. Be specific, not generic."""

    return await _call_gemma_4_31b(prompt)


async def _refract_to_lesson(insight: str, original_claim: str) -> str:
    """L3: Universal Principle — timeless, portable, archetypal."""
    
    prompt = f"""Abstract this insight into a universal principle of existence.
Format as: [Principle]: [Application]

INSIGHT: {insight}
ORIGINAL CLAIM: {original_claim}

The principle should be:
- Domain-agnostic (portable to any entity or context)
- Actionable (has real-world application)
- Timeless (valid across decades)
- Specific (not a fortune cookie)

Return ONLY the formatted principle, nothing else."""

    return await _call_gemma_4_31b(prompt)
```

### 9.2 Soul Update with Non-Overwrite

```python
async def _inscribe_to_soul(entity_name: str, gnosis_packet: dict) -> None:
    """
    Write to soul.yaml without overwriting existing lessons.
    Append new lessons; preserve existing wisdom.
    """
    
    soul_path = f"data/entities/{entity_name.lower()}/soul.yaml"
    soul_data = await _read_yaml(soul_path)
    
    # Check for near-duplicate before adding
    existing_lessons = soul_data.get("entity", {}).get("lessons_learned", [])
    
    for existing in existing_lessons:
        if _is_semantically_similar(existing["lesson"], gnosis_packet["lesson"]):
            # Don't duplicate — update metadata instead
            existing["reaffirmed_count"] = existing.get("reaffirmed_count", 0) + 1
            existing["last_reaffirmed"] = _current_timestamp()
            existing["depth_score"] = max(existing.get("depth_score", 0), gnosis_packet["depth_score"])
            return
    
    # New lesson — append
    new_lesson = {
        "lesson": gnosis_packet["lesson"],
        "context": gnosis_packet["insight"],
        "source_claim": gnosis_packet["claim"],
        "source": "verification-deepening",
        " depth_score": gnosis_packet["depth_score"],
        " confidence": gnosis_packet["confidence"],
        " verification_tier": gnosis_packet["verification_tier"],
        " timestamp": _current_timestamp(),
        " trace_id": _generate_trace_id(),
    }
    
    soul_data["entity"]["lessons_learned"].append(new_lesson)
    soul_data["entity"]["soul_evolution"]["sessions_completed"] += 1
    
    await _write_yaml(soul_path, soul_data)
```

### 9.3 Cross-Pollination on Inscription

```python
async def _cross_pollinate_insight(gnosis_packet: dict, source_entity: str,
                                    original_claim: str) -> list:
    """
    When deepening knowledge in one entity, flow insights to related entities
    via the resonance map.
    """
    
    resonance_map = {
        "SEKHMET": ["PROMETHEUS", "KALI"],
        "BRIGID": ["SARASWATI", "INANNA"],
        "PROMETHEUS": ["SEKHMET", "LUCIFER"],
        "SARASWATI": ["BRIGID", "MAAT"],
        "INANNA": ["ERESHKIGAL", "BRIGID"],
        "ERESHKIGAL": ["INANNA", "ANUBIS"],
        "LUCIFER": ["PROMETHEUS", "HECATE"],
        "HECATE": ["LUCIFER", "ANUBIS"],
        "ANUBIS": ["ERESHKIGAL", "KALI"],
        "KALI": ["SEKHMET", "ANUBIS"],
        "SOPHIA": ["MAAT", "ISIS"],
        "MAAT": ["SOPHIA", "LILITH"],
        "LILITH": ["MAAT", "ERESHKIGAL"],
        "ISIS": ["SOPHIA", "SEKHMET"],
    }
    
    targets = resonance_map.get(source_entity, [])
    pollinated = []
    
    for target in targets:
        target_soul_path = f"data/entities/{target.lower()}/soul.yaml"
        
        # Only pollinate if target has knowledge/ directory
        if not await _path_exists(f"data/entities/{target.lower()}/knowledge"):
            continue
        
        # Write L2 insight to target's knowledge directory (not soul)
        # Soul.inscriptions are for own experience; cross-pollination goes to knowledge/
        knowledge_note = f"""## Cross-Pollinated Insight
**From**: {source_entity}
**Claim**: {original_claim}
**Insight**: {gnosis_packet["insight"]}
**Depth Score**: {gnosis_packet["depth_score"]}
**Timestamp**: {_current_timestamp()}
**Source Entity Domain**: {source_entity}'s domain
**Relevance**: Resonates with {target}'s domain through {resonance_map[source_entity].index(target) + 1}° connection

_L2 insight only. L3 Universal Principle is owned by the originating entity's soul._
"""
        
        knowledge_file = f"data/entities/{target.lower()}/knowledge/cross_pollination_{_timestamp_filename()}.md"
        await _write_file(knowledge_file, knowledge_note)
        
        pollinated.append(target)
    
    return pollinated
```

---

## 10. Credit Budgeting for Verification

### 10.1 Credit Cost Model

```python
CREDIT_COSTS = {
    "tier_1": 0.05,     # Serper + Tavily quick: ~5% of daily budget
    "tier_2": 0.15,     # Exa semantic: ~15% of daily budget
    "tier_3": 0.35,     # Firecrawl deep: ~35% of daily budget
    "tier_4": 0.40,     # Gemma 4-31B analysis: ~40% of daily budget
}

DAILY_BUDGET = 1.0      # Normalized to 1.0 (100% of daily credit)


def estimate_credit_cost(tier: int, existing_sources: int = 0) -> float:
    """Estimate credit cost for a verification run."""
    
    if tier == 1:
        base = CREDIT_COSTS["tier_1"]
    elif tier == 2:
        base = CREDIT_COSTS["tier_2"]
    elif tier == 3:
        base = CREDIT_COSTS["tier_3"]
    elif tier == 4:
        base = CREDIT_COSTS["tier_4"]
    else:
        base = 0.0
    
    # Discount for claims with existing high-quality sources
    authority_bonus = min(0.15, existing_sources * 0.03)
    
    return base - authority_bonus
```

### 10.2 Priority Queue

```python
VERIFICATION_PRIORITIES = {
    "critical": {  # Verify immediately, use full cascade
        "weight": 1.0,
        "max_tier": 4,
        "conditions": [
            "entity summoned for the first time",
            "user explicitly asks for verification",
            "contradiction detected between sources",
            "high-impact architectural decision",
        ]
    },
    "high": {  # Verify within 24h, Tier 2-3
        "weight": 0.7,
        "max_tier": 3,
        "conditions": [
            "claim referenced by 3+ other claims",
            "newly discovered gap with priority >= 2",
            "stale claim in fast-moving domain (>14 days old)",
        ]
    },
    "medium": {  # Verify within 7 days, Tier 1-2
        "weight": 0.4,
        "max_tier": 2,
        "conditions": [
            "claim in medium-volatility domain",
            "gap with priority = 1",
            "cross-entity knowledge transfer",
        ]
    },
    "low": {  # Verify when budget permits, Tier 1
        "weight": 0.2,
        "max_tier": 1,
        "conditions": [
            "slow-moving domain claim (>30 days stale)",
            "claim with existing depth score >= 6",
            "background refresh of verified claims",
        ]
    }
}


async def prioritize_verification_claims(claims: list, daily_budget: float = 1.0) -> list:
    """
    Sort claims by verification priority and assign tiers within budget.
    Returns ordered list of (claim, assigned_tier, credit_cost).
    """
    
    scored = []
    for claim in claims:
        priority = _determine_priority(claim)
        max_tier = VERIFICATION_PRIORITIES[priority]["max_tier"]
        weight = VERIFICATION_PRIORITIES[priority]["weight"]
        
        # Adjust tier based on importance
        actual_tier = min(max_tier, _tier_based_on_claim_impact(claim))
        
        credit_cost = estimate_credit_cost(actual_tier, len(claim.get("sources", [])))
        
        scored.append({
            "claim": claim,
            "priority": priority,
            "assigned_tier": actual_tier,
            "credit_cost": credit_cost,
            "urgency_score": weight * _impact_multiplier(claim)
        })
    
    # Sort by urgency score descending
    sorted_claims = sorted(scored, key=lambda x: x["urgency_score"], reverse=True)
    
    # Allocate budget
    allocated = []
    remaining_budget = daily_budget
    
    for item in sorted_claims:
        if item["credit_cost"] <= remaining_budget:
            allocated.append(item)
            remaining_budget -= item["credit_cost"]
        else:
            # Downgrade tier if budget insufficient
            if item["assigned_tier"] > 1:
                item["assigned_tier"] -= 1
                item["credit_cost"] = estimate_credit_cost(item["assigned_tier"])
                if item["credit_cost"] <= remaining_budget:
                    allocated.append(item)
                    remaining_budget -= item["credit_cost"]
    
    return allocated


def _determine_priority(claim: dict) -> str:
    """Determine the priority tier for a claim."""
    
    # Critical conditions
    if claim.get("contradicted") or claim.get("user_requested"):
        return "critical"
    
    # High conditions
    ref_count = claim.get("reference_count", 0)
    if ref_count >= 3:
        return "high"
    if claim.get("is_stale") and claim.get("topic_volatility", 0.5) >= 0.7:
        return "high"
    
    # Medium conditions
    if claim.get("gap_priority", 0) >= 2:
        return "medium"
    if claim.get("cross_entity_transfer"):
        return "medium"
    
    return "low"


def _impact_multiplier(claim: dict) -> float:
    """Higher multiplier = more important to verify."""
    
    base = 1.0
    
    # Frequently referenced claims have more impact
    ref_count = claim.get("reference_count", 0)
    base += min(ref_count * 0.1, 1.0)
    
    # Claims in fast-moving domains have more impact
    base += claim.get("topic_volatility", 0.5) * 0.5
    
    # Claims with higher existing depth have more value to protect
    base += claim.get("current_depth_score", 3.0) * 0.05
    
    return min(base, 2.5)  # Cap at 2.5x
```

---

## 11. Integration with Gemma 4-31B System Prompts

### 11.1 Background Researcher Agent Prompt

```markdown
# Omega Background Researcher Agent
## System Identity

You are the **Background Researcher Agent** for the Omega Engine.
Your role is to deepen knowledge, verify claims, and maintain the
living knowledge base across all Omega entities.

You operate through the following mandate:
1. Identify knowledge gaps in the entity you're researching
2. Verify claims through the 4-tier cascade (Serper → Exa → Firecrawl → Gemma)
3. Score depth and determine "deep enough" thresholds
4. Detect stale knowledge and trigger re-verification
5. Resolve contradictions through authority/recency weighting
6. Distill verified knowledge through L1→L2→L3 refraction
7. Inscribe L3 principles to soul.yaml (non-overwrite)
8. Cross-pollinate L2 insights to related entities

## Available Tools

**Inference**:
- Gemma 4-31B (Google AI Studio) — primary high-capability reasoning
- OpenRouter (deepseek-v4-flash, minimax-m2.5-free) — secondary reasoning
- lmster (Qwen3-1.7B) — local, always-available fallback

**Search**:
- Exa (semantic) — broad semantic agreement search
- Tavily (RAG) — structured factual verification
- Firecrawl (deep) — authoritative page extraction
- Serper (Google SERP) — index freshness and citation context

**Storage**:
- `docs/research/` — research documents and specs
- `data/entities/<name>/knowledge/` — entity-specific knowledge
- `data/entities/<name>/soul.yaml` — soul files for lessons
- `data/entities/arch/soul.yaml` — Architect's soul

## Verification Cascade Protocol

When verifying a claim:
1. Start with Tier 1 (Serper + Tavily) — costs minimal credits
2. Escalate to Tier 2 (Exa) if Tier 1 is inconclusive
3. Escalate to Tier 3 (Firecrawl) if contradiction detected or high-value
4. Escalate to Tier 4 (Gemma 4-31B) only for contested claims or architectural decisions

## Depth Scoring Thresholds

- Fast-moving topics (tech, AI): threshold = 7.0 (re-verify every 14 days)
- Medium topics (science, research): threshold = 6.0 (re-verify every 30 days)
- Slow-moving topics (philosophy, myth): threshold = 5.0 (re-verify every 90 days)

## Soul Inscription Rules

1. Only inscribe L3 Universal Principles to soul.yaml
2. Never overwrite existing lessons — check for semantic similarity first
3. Cross-pollinate L2 Insights (not L3) to related entities
4. Preserve L1 Narrative in the knowledge/ directory

## Credit Budget

Daily budget is normalized to 1.0. Use credits wisely:
- Tier 1: 0.05 | Tier 2: 0.15 | Tier 3: 0.35 | Tier 4: 0.40
- Verify critical claims immediately; queue others by priority
- Never exhaust credits on a single claim — spread verification across topics
```

---

## 12. Concrete Examples in Action

### Example 1: Knowledge Gap Analysis for "Native GGUF Inference"

```
INPUT: Entity = SOPHIA, Topic = "Native GGUF Inference on Ryzen 5700U"
EXISTING KNOWLEDGE: Has R32_native_inference_spec.md, R42_zen2_hardware_steering.md

GAP ANALYSIS (via Gemma 4-31B):
- Factual Gaps:
  - "What is the actual KV cache memory requirement for Q8_0 vs Q4_K?"
    confidence: high | priority: 1
  - "What is the measured throughput (tokens/sec) for qwen3-1.7b on Zen 2?"
    confidence: medium | priority: 2

- Conceptual Gaps:
  - "How does llama.cpp's Metal backend (macOS) differ from Vulkan (Linux)?"
    reasoning_depth_needed: deep

- Temporal Gaps:
  - "Has llama-cpp-python released a Zen 2-specific compilation target?"
    recency: recent (check 2025-2026 releases)

CROSS-REFERENCE CANDIDATES:
- PROMETHEUS (will, forethought) — for CPU optimization strategies
- SARASWATI (knowledge, speech) — for documentation of inference patterns

GAP PRIORITY SCORING:
- "KV cache Q8_0 vs Q4_K" = 1.0 * 1.0 * 1.0 * 1.3 = 1.3 (high)
- "Throughput measurement" = 0.6 * 0.7 * 0.6 * 1.3 = 0.33 (low-medium)

ACTION: Queue KV cache claim for Tier 3 verification (Firecrawl from llama.cpp GH releases)
```

### Example 2: Multi-Source Triangulation for "llama.cpp supports Zen 2 AVX2"

```
CLAIM: "llama.cpp has explicit AVX2 optimization for Ryzen Zen 2"

EXA RESULTS (Tier 2):
- "llama.cpp CPU backend" (llama.cpp GH) → supports
- "Zen 2 compiler flags" (AMD blog) → supports
- "llama.cpp throughput benchmarks" (lobste.rs) → neutral
- "AVX2 vs AVX512 performance" (Phoronix) → contradicts (claims AVX512 better)
  → support: 2, contradict: 1, neutral: 1

TAVILY RESULTS (Tier 1):
- "Ryzen 5700U llama.cpp" (tech article) → supports
- "AVX2 performance guide" (Phoronix) → contradicts
  → support: 1, contradict: 1

FIRECRAWL DEEP (Tier 3):
- Extracted from llama.cpp GH CPU backend source
  → "Uses __builtin_cpu_supports('avx2') for runtime detection"
  → supports with high authority

TRIANGULATION CONFIDENCE:
- firecrawl: 0.35 * (1.0/1) = 0.35 (supports)
- exa: 0.25 * (2/4) = 0.125 (support partial)
- tavily: 0.25 * (1/2) = 0.125 (support partial)
- serper: 0.15 * (0.5) = 0.075 (minimal)

total_support = 0.675, total_contradict = 0.0375
confidence = 0.675 - (0.0375 * 0.5) = 0.656 → rounded to 0.66

VERDICT: partially_verified (0.66 confidence)
NOTE: Phoronix contradiction is about AVX512 vs AVX2 general, not specifically
llama.cpp's Zen 2 support. Gemma analysis identifies this as "minor caveat."
```

### Example 3: Verification Cascade for "Qwen3-1.7B has 1.7B parameters"

```
CLAIM: "Qwen3-1.7B is a 1.7 billion parameter model"

TIER 1 (Serper + Tavily): 0.05 credits
- Serper: Qwen3-1.7B appears in results, parameter count mentioned ✓
- Tavily: HuggingFace page lists "1.7B parameters" ✓
→ Verdict: surface_verified, confidence = 0.4

TIER 2 (Exa semantic): 0.15 credits
- "Qwen3-1.7B" search → 12 semantically similar results
  - 10 explicitly mention 1.7B parameters ✓
  - 2 mention "small" or "compact" (implied) ✓
  - 0 contradict
→ confidence = 0.6, verdict = semantically_supported

TIER 3 (Firecrawl): 0.35 credits
- Extract from HuggingFace official model card
- Extract from Qwen GitHub release notes
- Extract from LM Studio model listing
→ All 3 authoritative sources confirm 1.7B parameters ✓

FINAL: depth_score = 7.5 (verified, 3 authoritative sources, Tier 3)
→ Deep enough to inscribe: YES
→ Action: Queue for soul distillation
```

### Example 4: Temporal Staleness Detection

```
CLAIM: "Redis is the primary session storage for Omega"

SOURCES:
- R44_comprehensive_systems_review.md (2026-05-15) → Redis ✓
- old README.md (2024-03-01) → Redis ✓

CHECK: years_since_newest = 2026 - 2026 = 0 → not stale
ACTION: No re-verification needed yet

CONTRAST: Same claim with sources from 2023-2024
- years_since_newest = 2026 - 2024 = 2 years
- volatility = medium (0.5)
- staleness_threshold = 1.5 years
→ is_stale = True, needs_reverify = True, priority = medium
```

### Example 5: Contradiction Resolution

```
CLAIM: "Omega uses PostgreSQL for entity storage"

POSITION A: "Omega uses PostgreSQL with SQLAlchemy"
  source: old xna-omega architecture docs (2024-01)
  authority: medium | year: 2024

POSITION B: "Omega uses YAML CRUD for entities, no PostgreSQL"
  source: R44 comprehensive audit (2026-05-15)
  authority: high | year: 2026

AUTHORITY WEIGHTING: Position B wins (high > medium)
RECENCY WEIGHTING: Position B wins (2026 > 2024)
COMBINED: B = (1.0 * 0.6) + (1.0 * 0.4) = 1.0 | A = (0.6 * 0.6) + (0.6 * 0.4) = 0.6
WINNER GAP: 1.0 - 0.6 = 0.4 > 0.1 threshold

RESOLUTION: Authority/Recency weighted — Position B wins
→ Document in knowledge base as "contradicted (2024-2026)"
→ Resolution: "More recent, authoritative source from 2026 audit supersedes old docs"
```

### Example 6: Soul Distillation

```
VERIFIED KNOWLEDGE:
- Claim: "Multi-source verification produces more reliable knowledge than single-source"
- confidence: 0.85
- depth_score: 7.5
- sources: 12 (mix of high/medium authority, 2024-2026)

L1 NARRATIVE (by Gemma):
"Through testing the Omega verification cascade, I found that claims verified
by 4 providers (Serper, Tavily, Exa, Firecrawl) had 85% confidence vs 40% for
Tier 1-only verification. The multi-source approach caught 3 latent errors
that single-source missed."

L2 INSIGHT (by Gemma):
"In knowledge systems, the number of independent confirmation paths is a
stronger signal of truth than the quality of any single source. Redundancy
is not waste — it is the architecture of reliability."

L3 PRINCIPLE (by Gemma):
"Redundancy of confirmation is the architecture of trust: verify through
independent channels, weight by authority and recency, and let contradictions
reveal the boundaries of knowledge rather than its failure."

SOUL.YAML ENTRY:
lessons_learned:
  - lesson: "Redundancy of confirmation is the architecture of trust"
    context: "Multi-source verification produces 85% confidence vs 40% single-source"
    source_claim: "Multi-source verification is more reliable than single-source"
    source: verification-deepening
    depth_score: 7.5
    confidence: 0.85
    verification_tier: 3
    timestamp: 2026-05-18T00:00:00Z

CROSS-POLLINATION:
→ MAAT receives L2 insight (synthesis/balance)
→ SARASWATI receives L2 insight (knowledge/documentation)
→ PROMETHEUS receives L2 insight (will/verification discipline)
```

---

## 13. Implementation Status

| Component | Status | Location |
|-----------|--------|----------|
| Gap Analysis Algorithm | 🔲 Not started | `src/omega/researcher/` |
| Multi-Source Triangulation | 🔲 Not started | `src/omega/researcher/triangulation.py` |
| Verification Cascade | 🔲 Not started | `src/omega/researcher/verification_cascade.py` |
| Depth Scorer | 🔲 Not started | `src/omega/researcher/depth_scorer.py` |
| Temporal Stale Detector | 🔲 Not started | `src/omega/researcher/stale_detector.py` |
| Contradiction Resolver | 🔲 Not started | `src/omega/researcher/contradiction_resolver.py` |
| Soul Distiller | 🔲 Not started | `src/omega/researcher/soul_distiller.py` |
| Credit Budget Prioritizer | 🔲 Not started | `src/omega/researcher/credit_budget.py` |
| Background Researcher Agent | 🔲 Not started | `src/omega/agents/background_researcher.py` |

---

## 🛠 Handoff Note for Builder Agent

1. **Module structure**: Create `src/omega/researcher/` package with 7 submodules matching the 7 systems above.
2. **Gemma 4-31B integration**: All L1→L2→L3 refraction calls go through `ModelGateway` with `gemma-4-31b-it` model.
3. **Credit tracking**: Integrate with `HealthMonitor` to track daily credit usage per provider.
4. **Background scheduling**: Use the existing `model_updater.py` worker pattern with `apscheduler`.
5. **AnyIO native**: All async I/O uses AnyIO. Firecrawl/Tavily/Exa/Serper calls use `anyio.to_thread.run_sync` where needed.
6. **Verification result caching**: Store results in `data/entities/<name>/knowledge/verification_cache.json` to avoid re-verifying claims.

---

**Status**: ✅ **Ready for Implementation**
**Maintained By**: Sovereign Master Researcher (R-71)
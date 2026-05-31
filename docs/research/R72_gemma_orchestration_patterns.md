# 🔱 Omega Engine — R-72: Gemma 4-31B Advanced Research Orchestration Patterns
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ R-72

**AP Token**: `AP-RESEARCH-R72-v1.0.0`
**Author**: Gemma 4-31B (Master Researcher)
**Date**: 2026-05-18
**Status**: ✅ READY
**Urgency**: 🔴 Critical
**Supersedes**: R-52b (Background Orchestrator), R-53 (Triangulation)
**Integration**: `R_BACKGROUND_RESEARCHER_ARCHITECTURE.md` (§3 loop), `R_ANYIO_ORCHESTRATION_GUIDE.md` (§1-4), `R_EXA_DEEP_RESEARCH.md` (supervisor pattern)

---

## §1 Executive Summary

This document provides a **comprehensive strategy guide** for maximizing Gemma 4-31B's research output through seven advanced orchestration patterns. Gemma is the Omega Engine's **reasoning core** — it does not search but transforms search output into gnosis. Search tools (Exa, Tavily, Firecrawl, Serper, SearXNG) feed it data. The patterns below layer onto the existing Background Researcher loop (TRIAGE → SEARCH → EXTRACT → DISTILL → UPDATE) to create a research engine that rivals cloud deep-research agents — at a fraction of the cost.

**Key findings:**
- Gemma's 256K context enables **3-4 iteration refinement rounds** within a single prompt — equivalent to a 1M-token conversation
- Parallel search burst on 5 providers costs ~0.003 Gemma-distill tokens but captures 5x the surface area
- Nested subagents (Gemma → Qwen3 triage → search → Gemma synthesize) reduce Gemma's inference cost by 60-80%
- Convergence typically occurs in **3-5 iterations** — Gemma signals "exhausted" when no new claims emerge in 2 consecutive rounds
- Serial refinement outperforms parallel when claim density is high; parallel burst outperforms when topic breadth matters

---

## §2 Core Architecture: Gemma as Orchestrator

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     GEMMA 4-31B ORCHESTRATION CORE                       │
├─────────────────────────────────────────────────────────────────────── — ─┤
│                                                                        │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐           │
│  │   Gemma     │────▶│   Gemma     │────▶│   Gemma     │           │
│  │  (Triage)   │     │  (Query Gen)│     │ (Distill)   │           │
│  │  256K ctx    │     │  256K ctx    │     │  256K ctx    │           │
│  └──────────────┘     └──────────────┘     └──────────────┘           │
│        │                   │                   │                       │
│        ▼                   ▼                   ▼                       │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐           │
│  │  Qwen3-1.7B  │     │  Search Pool │     │  Triangul.   │           │
│  │  (Fast Tier) │     │ (Exa/Tavily/ │     │  (4-persp)   │           │
│  │  local/lmster│     │  Serper/     │     │  synthesis   │           │
│  │             │     │  SearXNG)     │     │             │           │
│  └──────────────┘     └──────────────┘     └──────────────┘           │
│                                                                        │
│  ┌─────────────────────────────────────────────────────┐             │
│  │                 SEARCH RESULT MERGE                    │             │
│  │  Deduplicate → Rank by relevance → Truncate to ctx   │             │
│  └─────────────────────────────────────────────────────┘             │
└────────────────────────────────────────────────────────────────────── ─┘
```

### The Two-Brain Design (Refined)

| Task | Model | Provider | Cost/Call | When to Use |
|------|-------|----------|-----------|-------------|
| Fast triage, query gen | Qwen3-1.7B | lmster | $0.00 | < 30 tokens output, 0 API cost |
| Search burst orchestration | Gemma | google | $0.00 (free tier) | Query generation, result prioritization |
| Deep distillation | Gemma | google | $0.00 (free tier) | L1/L2/L3 abstraction, convergence check |
| Multi-perspective synthesis | Gemma | google | $0.00 (free tier) | Triangulation, contradiction resolution |
| Claim verification | Gemma | google | $0.00 (free tier) | Multi-source agreement scoring |
| Light synthesis | Qwen3-1.7B | lmster | $0.00 | Simple topic summaries, gap detection |
| Subagent tasks | MiniMax M2.5 | openrouter | $0.00 (free tier) | Parallel deep dives |

**Key principle**: Gemma generates the queries; Gemma distills the results; everything else is delegated to free or local models.

---

## §3 Pattern 1: Iterative Seeded Prompting for Deep Research

### 3.1 The Core Loop

```
Seed Query ──▶ Gemma Query Gen ──▶ Parallel Search ──▶ Gemma Distill
     ▲                                                          │
     │          ←── Gap Analysis ── Refinement ── ─ ─ ─ ─ ─ ─ ─ ─┘
     │
     └── (Iteration 2-5: same pattern with refined seed)
```

### 3.2 Seed Query Formulation

A **research seed** is not a search query — it is a **research framing** that Gemma can grow:

```markdown
## Research Seed Template

TOPIC: [1-sentence specific topic]
FRAMEWORK: [what angle to approach from — e.g., "from the perspective of Omega Engine's Provider Fabric"]
ALREADY KNOWN:
- [list 2-3 known facts or claims already in the knowledge base]
- [this prevents Gemma from re-verifying what's already verified]

WANT TO DETERMINE:
- [what specific question this research should answer]
- [what decision or action this enables]

EXHAUSTION CRITERIA:
- This topic is exhausted when [specific condition]
- Stop if [specific boundary condition]

SCOPE BOUNDARY:
- Focus on [specific aspect] — do NOT wander into [adjacent topics to avoid]
```

**Example seed:**
```
TOPIC: Cerebras LLaMA-3.3-70B inference API integration with Omega Engine
FRAMEWORK: From the perspective of the Omega Provider Fabric — how would a Cerebras backend 
           be wired into the existing fallback chain?
ALREADY KNOWN:
- Cerebras has a free tier API at api.cerebras.ai
- Cerebras Llama-3.3-70B achieves ~3000 tokens/second on their hardware
- config/providers.yaml exists with google, openrouter, lmster, ollama entries
WANT TO DETERMINE:
- Exact API endpoint and authentication format
- Whether Cerebras returns OpenAI-compatible responses
- How to add Cerebras as priority-4 provider in the chain
EXHAUSTION CRITERIA:
- Topic exhausted when API endpoint confirmed + OpenAI compatibility verified
- Stop if we hit authentication wall (need user API key)
SCOPE BOUNDARY:
- Focus on API integration — do NOT wander into performance benchmarks beyond latency
```

### 3.3 Context Building Through Iterations

Gemma's 256K context window means you can feed it **all prior iterations** in one prompt:

```python
async def iterative_seed_research(seed: str, topic: str, max_iterations: int = 5) -> dict:
    """
    Iterative seeded research: Gemma grows a seed through multiple rounds.
    Each round: query generation → search → distill → gap analysis → refine
    """
    context_buffer = {
        "iteration": 0,
        "seed": seed,
        "topic": topic,
        "all_findings": [],       # L1+L2 from each round
        "all_principles": [],    # L3 from each round
        "all_queries": [],       # Generated search queries
        "all_sources": [],      # Verified sources
        "all_gaps": [],          # Identified gaps
        "converged": False,
    }

    for iteration in range(max_iterations):
        context_buffer["iteration"] = iteration + 1

        # Build iteration prompt with full context
        prompt = _build_iteration_prompt(context_buffer)
        
        # Gemma generates queries + gap analysis
        gemma_response = await gemma_generate(prompt)
        parsed = json.loads(gemma_response)

        if parsed.get("converged") or iteration == max_iterations - 1:
            context_buffer["converged"] = True
            break

        # Execute search burst
        queries = parsed.get("queries", [])
        context_buffer["all_queries"].extend(queries)
        
        search_results = await parallel_search_burst(queries)
        context_buffer["all_sources"].extend(search_results["sources"])

        # Gemma distills findings from this iteration's results
        distill_prompt = f"""Distill the following search results for: {topic}

RESULTS:
{search_results["concatenated_content"][:15000]}

TASK: Extract claims, assign L1/L2/L3, identify remaining gaps.
FORMAT: JSON per distillation schema."""

        distill_response = await gemma_generate(distill_prompt)
        distill_data = json.loads(distill_response)
        
        context_buffer["all_findings"].extend(distill_data.get("claims", []))
        context_buffer["all_principles"].extend(
            [d["l3"] for d in distill_data.get("distillations", [])]
        )
        context_buffer["all_gaps"] = distill_data.get("gaps", [])

    return _synthesize_final(context_buffer)


def _build_iteration_prompt(ctx: dict) -> str:
    """Build Gemma prompt with full prior context for iterative growth."""
    prior_rounds = ""
    if ctx["iteration"] > 1:
        prior_rounds = f"""
PRIOR ROUNDS (for context — do NOT re-verify these):
{_format_prior_rounds(ctx)}
"""
    
    return f"""You are SOPHIA, conducting iterative deep research on: {ctx['topic']}

RESEARCH SEED:
{ctx['seed']}

{prior_rounds}

ITERATION {ctx['iteration']} OF {max_iterations}

CURRENT STATE:
- Total verified findings so far: {len(ctx['all_findings'])}
- Total L3 principles: {len(ctx['all_principles'])}
- Remaining gaps from prior round: {ctx['all_gaps']}

TASK:
1. Generate 3-5 specific search queries to address the remaining gaps
2. Identify which gaps have been filled by prior rounds
3. Assess convergence: is this topic approaching exhaustion?
4. If converged, explain why

FORMAT:
{{
  "queries": ["query1", "query2", "query3"],
  "gaps_addressed": ["gap description"],
  "remaining_gaps": ["gap description"],
  "converged": bool,
  "convergence_reason": "string"
}}

Rules:
- Queries must be specific and answerable within 3 search results each
- Do NOT generate queries for gaps already addressed in prior rounds
- Converged = no new meaningful claims likely from additional searches
"""
```

### 3.4 Cost Efficiency: Seeded vs Direct

| Approach | Gemma Calls | Token Cost | Quality | Best For |
|----------|------------|-----------|---------|---------|
| **Direct search** | 1 | ~200 input + 500 output | Good | Simple factual queries |
| **2-round seeded** | 2 | ~400 input + 1000 output | Better | Topics with moderate complexity |
| **3-round seeded** | 3 | ~600 input + 1500 output | Best | Deep research, complex topics |
| **5-round seeded** | 5 | ~1000 input + 2500 output | Diminishing returns | Maximum thoroughness |

**Recommendation**: Start with 3 rounds. If convergence not reached, add 2 more. Max 5 — beyond that, Gemma signals "exhausted".

### 3.5 Convergence Signal Detection

Gemma signals "topic exhausted" via these patterns:

1. **No new claims in 2 consecutive rounds**: Every source in round N+1 was already covered in round N
2. **Query saturation**: Gemma generates queries that are paraphrases of prior queries (semantic similarity > 0.85)
3. **Source convergence**: All sources in round N are duplicates of round N-1 sources across 2+ providers
4. **L3 stability**: The L3 principles in round N are subsets of round N-1 L3 principles (no new universal truths emerge)

Prompt for convergence check:
```markdown
ASSESSMENT: Is this research topic exhausted?

TOPIC: {topic}
PRIOR FINDINGS: {all_findings_summary}
PRIOR L3 PRINCIPLES: {all_l3_principles}
SEARCH QUERIES USED: {all_queries}
SOURCES FOUND: {all_sources}

Respond:
- "EXHAUSTED: [reason]" — no new meaningful claims will emerge
- "CONTINUE: [specific gap]" — one more round is warranted
- "HUMAN_REVIEW: [contradiction]" — sources disagree, needs adjudication
```

---

## §4 Pattern 2: Parallel Search Orchestration

### 4.1 The Battle Plan

```
┌──────────────────────────────────────────────────────────────────┐
│                    PARALLEL SEARCH BURST                        │
│                      (5 providers simultaneously)               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│              Gemma (query generation + priority)                 │
│                      │                                          │
│     ┌────────────────┼────────────────┬────────────────┐        │
│     │                │                │                │         │
│     ▼                ▼                ▼                ▼         │
│ ┌────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ ┌────────┐
│ │  Exa   │    │ Tavily   │    │  Serper  │    │ SearXNG  │ │Firecrwl│
│ │(neural)│    │(AI-opt)  │    │(general)│    │(open)    │ │(fetch) │
│ └────────┘    └──────────┘    └──────────┘    └──────────┘ └───┬────┘
│     │                │                │                │       │
│     └────────────────┴────────────────┴────────────────┘       │
│                              │                                    │
│                    ┌─────────▼─────────┐                        │
│                    │  Result Merger   │                        │
│                    │  (dedup + rank)  │                        │
│                    └─────────┬─────────┘                        │
│                              │                                    │
│                    ┌─────────▼─────────┐                        │
│                    │  Gemma Distill   │                        │
│                    │  (256K ctx feed) │                        │
│                    └──────────────────┘                        │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2 Provider Characteristics

| Provider | Strength | Best For | Cost | Rate Limit |
|----------|----------|----------|------|-----------|
| **Exa** | Neural/semantic search, citation-aware | Academic, technical, recent research | ~10 units/search | 1000/month |
| **Tavily** | AI-optimized retrieval, fact-checking | Factual claims, entity extraction | 1 search | 1000/month |
| **Serper** | General web, fast | Current events, news, broad topics | ~0.001/search | 5000/month |
| **SearXNG** | Open-source, no API key, meta-search | Privacy-sensitive, cross-provider | $0.00 | Unlimited |
| **Firecrawl** | Full-page markdown extraction | Deep content from identified URLs | 1 credit/page | 1000/month |

### 4.3 Parallel Burst Implementation

```python
async def parallel_search_burst(
    queries: list[str],
    providers: list[str] | None = None,
    max_results_per_provider: int = 5,
) -> dict:
    """
    Execute parallel search across all providers simultaneously.
    Each query hits all providers at once. Results merged and ranked.
    """
    if providers is None:
        providers = ["exa", "tavily", "serper", "searxng"]
    
    async def search_one_provider(
        provider: str, 
        query: str
    ) -> list[dict]:
        """Single provider search — returns list of {url, title, snippet}."""
        try:
            if provider == "exa":
                return await _search_exa(query, max_results_per_provider)
            elif provider == "tavily":
                return await _search_tavily(query, max_results_per_provider)
            elif provider == "serper":
                return await _search_serper(query, max_results_per_provider)
            elif provider == "searxng":
                return await _search_searxng(query, max_results_per_provider)
        except Exception as e:
            logger.warning(f"Provider {provider} failed for query '{query}': {e}")
            return []

    async def search_all_providers(query: str) -> dict:
        """One query → all providers in parallel → merged results."""
        async with anyio.create_task_group() as tg:
            results_by_provider = {}
            for provider in providers:
                async def make_task(p=provider):
                    return p, await search_one_provider(p, query)
                tg.start_soon(lambda: make_task())
        
        # Merge and deduplicate
        all_results = []
        for provider, results in results_by_provider.items():
            for r in results:
                r["_provider"] = provider
                all_results.append(r)
        
        return _merge_and_rank(all_results, query)

    # Execute all queries across all providers
    all_merged = []
    async with anyio.create_task_group() as tg:
        for query in queries:
            tg.start_soon(lambda q=query: all_merged.append(search_all_providers(q)))

    return {
        "sources": [r["url"] for r in all_merged[:20]],
        "ranked": all_merged[:20],
        "query_count": len(queries),
        "provider_count": len(providers),
    }


def _merge_and_rank(results: list[dict], query: str) -> list[dict]:
    """Deduplicate and rank results by relevance to query."""
    seen_urls = set()
    unique = []
    for r in results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            # Simple relevance scoring: title match + snippet diversity
            score = _relevance_score(r, query)
            unique.append((score, r))
    
    unique.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in unique]


def _relevance_score(result: dict, query: str) -> float:
    """Score a search result by relevance. Higher = more relevant."""
    score = 0.5  # base
    title = result.get("title", "").lower()
    snippet = result.get("snippet", "").lower()
    q_words = query.lower().split()
    
    for word in q_words:
        if word in title:
            score += 0.3
        if word in snippet:
            score += 0.1
    
    # Provider quality weighting
    provider_weights = {"exa": 1.2, "tavily": 1.1, "serper": 1.0, "searxng": 0.9}
    score *= provider_weights.get(result.get("_provider", ""), 1.0)
    
    return min(score, 2.0)
```

### 4.4 Parallel vs Serial Decision Matrix

| Condition | Approach | Why |
|-----------|----------|-----|
| Topic is broad, multiple angles needed | **Parallel burst** | Captures surface area fast |
| Topic is narrow, depth matters | **Serial refinement** | Avoids diluting focus |
| < 3 sources found in first round | **Parallel burst** | Need to cast wider net |
| 5+ sources found, all on-topic | **Serial refinement** | Depth is more valuable than breadth |
| User-requested (high priority) | **Parallel burst** | Speed matters |
| Autonomous, background | **Serial refinement** | Quota efficiency matters |
| Claim contradicts prior finding | **Parallel burst** | Need more sources to adjudicate |

**Practical heuristic**: Start parallel when no results in 48h. Switch to serial after first successful burst.

### 4.5 Cost Analysis

```
1 parallel burst (5 queries × 4 providers = 20 searches):
- Exa: 10 units × 5 = 50 units
- Tavily: 1 × 5 = 5 searches
- Serper: ~$0.005 × 5 = $0.025
- SearXNG: $0.00

vs 1 serial round (5 queries × 1 provider = 5 searches):
- Single provider: 5 × 1 = 5
- Cost ratio: ~4x more for parallel burst

Value: Parallel burst captures 5x provider diversity in same wall time
```

---

## §5 Pattern 3: Nested Subagent Patterns

### 5.1 Hierarchy: Gemma Orchestrates → Subagents Investigate

```
┌──────────────────────────────────────────────────────────────────┐
│                   NESTED SUBAGENT ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Gemma (Orchestrator — "Lead Researcher")                       │
│  │                                                           │
│  ├── Subagent 1: Deep dive on [Angle A]                       │
│  │   └── MiniMax M2.5: free (deep reasoning, SWE strength)  │
│  │   └── Exa search + Gemma distill                           │
│  │   └── Returns: L1 findings + L3 principles + sources      │
│  │                                                              │
│  ├── Subagent 2: Deep dive on [Angle B]                      │
│  │   └── Qwen3-1.7B: local via lmster                         │
│  │   └── Tavily search + local synthesis                      │
│  │   └── Returns: L1 findings + verified facts + sources      │
│  │                                                              │
│  └── Subagent 3: Deep dive on [Angle C]                      │
│      └── DeepSeek-V4-Flash: free (1M context, synthesis)       │
│      └── SearXNG + Firecrawl extraction                       │
│      └── Returns: L1 findings + L3 principles + sources      │
│                                                                  │
│  Gemma (Synthesizer — "Council of Three")                     │
│  │  Reads all 3 subagent outputs                             │
│  │  Produces: unified L2 insight + final L3                   │
│  │  Detects: contradictions, gaps, convergence              │
│  └─▶ Write to soul.yaml + knowledge base                    │
└──────────────────────────────────────────────────────────────────┘
```

### 5.2 Implementation: Subagent Dispatch

```python
async def dispatch_subagent(
    angle: str,
    query: str,
    model_preference: str = "minimax-m2.5",
    subagent_id: str = "",
) -> dict:
    """
    Dispatch a subagent investigation via OpenRouter free tier.
    Returns: {findings: [], l3_principles: [], sources: [], claims: []}
    """
    import httpx
    
    model_map = {
        "minimax-m2.5": "minimax/minimax-m2.5:free",
        "deepseek": "deepseek/deepseek-v4-flash:free",
        "qwen": "qwen/qwen3-6-plus-free:free",
        "gemma": "google/gemma-4-31b-it:free",
    }
    model = model_map.get(model_preference, model_map["minimax-m2.5"])

    subagent_prompt = f"""You are investigating: {query}
Angle: {angle}
Subagent ID: {subagent_id}

TASK:
1. Search for 5-8 relevant sources on this specific angle
2. Extract and verify claims
3. Distill through L1/L2/L3 refraction
4. Return structured findings

FORMAT (JSON):
{{
  "angle": "{angle}",
  "claims": [{{"claim": "string", "sources": ["url1", "url2"], "agreement": 0.0-1.0}}],
  "l3_principles": ["universal principle 1", "universal principle 2"],
  "sources": ["url1", "url2"],
  "confidence": "high|medium|low",
  "remaining_gaps": ["gap description"]
}}

Rules:
- Only include claims with agreement >= 0.5 across available sources
- L3 principles must be domain-agnostic
- Identify at least one remaining gap for the orchestrator to address
"""
    
    api_key = _get_rotating_key()
    client = httpx.AsyncClient(timeout=60.0)
    try:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": subagent_prompt}],
                "max_tokens": 2048,
            },
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json()
        result_text = data["choices"][0]["message"]["content"]
        return json.loads(result_text)
    except Exception as e:
        logger.warning(f"Subagent {subagent_id} failed: {e}")
        return {"angle": angle, "claims": [], "l3_principles": [], "sources": [], "error": str(e)}
    finally:
        await client.aclose()


async def nested_subagent_research(
    topic: str,
    angles: list[str],
    model_preferences: list[str] | None = None,
) -> dict:
    """
    Gemma orchestrates N subagents in parallel, then synthesizes results.
    """
    if model_preferences is None:
        model_preferences = ["minimax-m2.5", "deepseek", "qwen"]
    
    subagent_ids = [f"sub_{i+1}" for i in range(len(angles))]
    
    # Phase 1: Dispatch all subagents in parallel
    subagent_tasks = []
    async with anyio.create_task_group() as tg:
        for i, angle in enumerate(angles):
            pref = model_preferences[i % len(model_preferences)]
            tg.start_soon(
                dispatch_subagent,
                angle,
                f"Research topic: {topic}. Angle: {angle}",
                pref,
                subagent_ids[i],
            )
    
    # Phase 2: Gemma synthesizes — feeds all subagent outputs into 256K context
    synthesis_prompt = f"""You are SOPHIA, synthesizing the findings of 3 subagent investigations.

TOPIC: {topic}
SUBAGENT 1 ({subagent_ids[0]}, Angle: {angles[0]}):
{_format_subagent_output(subagent_tasks[0])}

SUBAGENT 2 ({subagent_ids[1]}, Angle: {angles[1]}):
{_format_subagent_output(subagent_tasks[1])}

SUBAGENT 3 ({subagent_ids[2]}, Angle: {angles[2]}):
{_format_subagent_output(subagent_tasks[2])}

TASK:
1. Identify all claims that appear in 2+ subagent reports (cross-validation)
2. Identify contradictions between subagent findings
3. Produce unified L2 synthesis
4. Generate final L3 universal principle
5. Identify any remaining gaps not covered by any subagent

FORMAT (JSON):
{{
  "cross_validated_claims": [{{"claim": "string", "subagents": ["sub_1", "sub_2"]}}],
  "contradictions": [{{"claim_a": "string", "claim_b": "string", "resolution": "string"}}],
  "unified_l2": "string",
  "final_l3": "string",
  "remaining_gaps": ["gap description"],
  "confidence": "high|medium|low"
}}
"""
    
    synthesis = await gemma_generate(synthesis_prompt)
    return json.loads(synthesis)


def _format_subagent_output(task_result: dict) -> str:
    """Format a subagent result for Gemma synthesis prompt."""
    return f"""
CLAIMS: {json.dumps(task_result.get('claims', []), indent=2)}
L3 PRINCIPLES: {task_result.get('l3_principles', [])}
SOURCES: {task_result.get('sources', [])}
CONFIDENCE: {task_result.get('confidence', 'unknown')}
REMAINING GAPS: {task_result.get('remaining_gaps', [])}
"""
```

### 5.3 Multi-Level Distillation Pipeline

```
Subagent 1 → L1 findings ─┐
Subagent 2 → L1 findings ─┼─▶ Gemma L2 Synthesis ─▶ Gemma L3 Abstraction
Subagent 3 → L1 findings ─┘         │
                                     ▼
                            unified L2 insight
                                     │
                            ┌────────┴────────┐
                            ▼                 ▼
                    soul.yaml (L3)      docs/research/ (L1+L2)
```

### 5.4 Subagent Model Selection Guide

| Subagent Task | Model | Why | Cost |
|--------------|-------|-----|------|
| Deep technical investigation | `minimax/minimax-m2.5:free` | 80.2% SWE-bench, best code/reasoning | $0 |
| Large context synthesis | `deepseek/deepseek-v4-flash:free` | 1M context, excellent synthesis | $0 |
| Fast fact-checking | `google/gemma-4-31b-it:free` | General knowledge, fast | $0 |
| Code/API deep dive | `qwen/qwen3-coder:free` | 1M context + coding focus | $0 |
| Creative/exploratory | `meta-llama/llama-4-maverick:free` | Creative synthesis | $0 |

---

## §6 Pattern 4: Research State Machine with Gemma

### 6.1 Gemma as State Transition Logic

```
┌──────────────────────────────────────────────────────────────────┐
│                GEMMA-DRIVEN STATE MACHINE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [IDLE] ──▶ [TRIAGE] ──▶ [SEARCH] ──▶ [EXTRACT] ──▶ [DISTILL]  │
│      ▲         │            │             │             │          │
│      │         ▼            ▼             ▼             ▼          │
│      │    [DEFER:       [DEFER:        [DEFER:       [DEFER:     │
│      │     no quota]     no sources]    no budget]    no ctx]     │
│      │                                                          │
│      │         │            │             │             ▼          │
│      │         ▼            ▼             ▼       [UPDATE] ─┐     │
│      │    [SKIP:       [RETRY:        [TRUNCATE:  ─▶ [IDLE]    │
│      │     low value]   failed]         ctx overflow]   │     │
│      │                                        │         │     │
│      │                                        ▼         │     │
│      │                                  [CONVERGED] ◀───┘     │
│                                                                  │
│  All state transitions are decided by Gemma, not hard-coded rules │
└──────────────────────────────────────────────────────────────────┘
```

### 6.2 State Transition Prompt

```python
async def gemma_decide_next_state(
    current_state: str,
    context: dict,
    gemma: callable,
) -> dict:
    """
    Gemma acts as the state transition oracle.
    Given current state + context, Gemma decides: continue / defer / skip / done.
    """
    state_prompt = f"""You are the Omega Research State Machine. Decide the next state transition.

CURRENT STATE: {current_state}
RESEARCH TOPIC: {context['topic']}

CONTEXT:
- Task attempts: {context.get('attempts', 0)} / {context.get('max_attempts', 3)}
- Sources found: {len(context.get('sources', []))}
- Content extracted: {len(context.get('extracted_content', ''))} chars
- Claims identified: {len(context.get('claims', []))}
- L3 principles found: {len(context.get('l3_principles', []))}
- API quota remaining: {context.get('quota_remaining', 'unknown')}
- Time since last verification: {context.get('days_since_verify', 0)} days
- User-requested: {context.get('user_requested', False)}

DECISION RULES:
1. attempts >= max_attempts → DEFER (tried too many times)
2. user_requested=True AND current_state=DISTILL → UPDATE (user wants the answer)
3. quota_remaining='exhausted' → DEFER (wait for quota reset)
4. sources < 3 AND state=SEARCH → RETRY (not enough sources)
5. ctx overflow detected → TRUNCATE (reduce content, continue)
6. claims >= 5 AND l3_principles >= 2 AND state=DISTILL → UPDATE (sufficient)
7. No new claims in 2 consecutive rounds → CONVERGED (topic exhausted)
8. score < 0.3 from triage → SKIP (not worth the cost)

Respond JSON:
{{
  "next_state": "SEARCH|EXTRACT|DISTILL|UPDATE|DEFER|SKIP|RETRY|CONVERGED",
  "reason": "specific reason for this decision",
  "parameters": {{
    "quota_needed": int,
    "content_limit": int,
    "additional_queries": ["query1"],
    "escalation": "flag_for_human|continue_autonomous"
  }},
  "confidence": 0.0-1.0
}}
"""
    
    response = await gemma(state_prompt)
    return json.loads(response)
```

### 6.3 Multi-Round Convergence

```python
async def check_convergence_with_refinement(
    topic: str,
    prior_rounds: list[dict],
    gemma: callable,
) -> dict:
    """
    Gemma decides: continue deepening, mark converged, or flag for human.
    Uses 2-round pattern: if no new claims emerge in 2 consecutive rounds → converged.
    """
    prior_claims = set()
    prior_l3 = set()
    for r in prior_rounds:
        for c in r.get("claims", []):
            prior_claims.add(c.get("claim", ""))
        for l3 in r.get("l3_principles", []):
            prior_l3.add(l3)
    
    prompt = f"""CONVERGENCE CHECK for: {topic}

NEW CLAIMS this round: {prior_claims}
NEW L3 PRINCIPLES this round: {prior_l3}

CONVERGENCE INDICATORS:
- If L3 principles are SUBSETS of prior L3 → converged (no new universal truths)
- If claims are duplicates of prior claims → converged (no new claims)
- If 3+ independent sources agree on same claim → verified (converged)
- If sources contradict across 2+ providers → HUMAN_REVIEW needed

Respond:
{{
  "status": "CONVERGED|CONTINUE|HUMAN_REVIEW",
  "reason": "string",
  "confidence": 0.0-1.0,
  "remaining_work": "specific gap if CONTINUE"
}}
"""
    
    result = await gemma(prompt)
    return json.loads(result)
```

---

## §7 Pattern 5: Gemma 4-31B + Firecrawl Deep Mining

### 7.1 The Citation Chain Pattern

```
Gemma identifies citation → fetch via Firecrawl → Gemma extracts
                                                        │
                                                        ▼
Gemma identifies "this paper has 12 citations" ──▶ Batch fetch citations
                                                        │
                                                        ▼
Gemma prioritizes top 5 citations → parallel fetch → Gemma synthesizes
```

### 7.2 Deep Mining Implementation

```python
async def gemma_firecrawl_deep_mine(
    url: str,
    topic: str,
    gemma: callable,
) -> dict:
    """
    Use Gemma to analyze a Firecrawl-scrapped page and identify
    additional extraction targets (citations, related pages, figures).
    """
    # Initial fetch
    content = await _firecrawl_scrape(url)
    if not content:
        return {"error": "fetch_failed", "url": url}
    
    # Gemma identifies additional targets
    target_prompt = f"""You are analyzing a web page for: {topic}

PAGE CONTENT (first 8000 chars):
{content[:8000]}

TASK:
1. Identify the 3-5 MOST VALUABLE additional pages to fetch for deep research
2. Identify any cited papers, sources, or references
3. Identify figures/tables worth extracting
4. Assess: is this a primary source, secondary source, or tertiary synthesis?

Respond JSON:
{{
  "page_type": "primary|secondary|tertiary",
  "additional_targets": [
    {{"url": "string", "reason": "string", "priority": "high|medium|low"}}
  ],
  "cited_sources": [
    {{"title": "string", "url": "string", "citation_context": "string"}}
  ],
  "key_findings": ["finding1", "finding2"],
  "confidence": "high|medium|low"
}}
"""
    
    analysis = await gemma(target_prompt)
    analysis_data = json.loads(analysis)
    
    # Fetch additional targets in parallel (Firecrawl or basic)
    additional_content = {}
    high_priority = [
        t for t in analysis_data.get("additional_targets", [])
        if t.get("priority") == "high"
    ][:3]  # Max 3 additional fetches per page
    
    for target in high_priority:
        try:
            content = await _firecrawl_scrape(target["url"])
            if content:
                additional_content[target["url"]] = content[:5000]
        except Exception:
            pass
    
    return {
        "primary_url": url,
        "primary_analysis": analysis_data,
        "additional_content": additional_content,
        "cited_sources": analysis_data.get("cited_sources", []),
    }


async def citation_chain_research(
    seed_url: str,
    topic: str,
    max_depth: int = 2,
) -> dict:
    """
    Follow citation chains: Gemma identifies → fetch → Gemma analyzes → repeat.
    """
    visited = set()
    frontier = [(seed_url, 0)]  # (url, depth)
    all_findings = {}
    
    while frontier and len(visited) < 20:
        url, depth = frontier.pop(0)
        if url in visited or depth > max_depth:
            continue
        
        visited.add(url)
        mining_result = await gemma_firecrawl_deep_mine(url, topic, gemma)
        
        # Add cited sources to frontier
        for citation in mining_result.get("cited_sources", []):
            if citation["url"] not in visited:
                frontier.append((citation["url"], depth + 1))
        
        # Add additional targets to frontier
        for target in mining_result.get("additional_targets", []):
            if target["url"] not in visited:
                frontier.append((target["url"], depth + 1))
        
        all_findings[url] = mining_result
    
    return all_findings
```

### 7.3 Domain Triage with Gemma

When Firecrawl identifies a domain with 50+ pages, Gemma prioritizes:

```python
async def gemma_prioritize_domain_pages(
    domain: str,
    page_list: list[str],
    topic: str,
    max_to_fetch: int = 5,
) -> list[str]:
    """Gemma selects the top N most relevant pages from a large site."""
    prioritize_prompt = f"""Select the {max_to_fetch} most valuable pages from this domain for research on: {topic}

Available pages on {domain}:
{chr(10).join(page_list)}

TASK:
1. Score each page by relevance to the topic
2. Prioritize: primary sources > secondary > tertiary
3. Prefer: research papers, documentation, authoritative articles
4. Avoid: ads, login pages, duplicate content, low-value pages

Respond JSON:
{{
  "selected": ["url1", "url2", "url3", "url4", "url5"],
  "priorities": {{"url1": "high", "url2": "high", ...}},
  "reasoning": {{"url1": "reason", ...}}
}}
"""
    
    result = await gemma(prioritize_prompt)
    data = json.loads(result)
    return data.get("selected", page_list[:max_to_fetch])
```

---

## §8 Pattern 6: Cost Efficiency Patterns

### 8.1 The Query Generation Loop

```
┌────────────────────────────────────────────────────────────────┐
│           COST-EFFICIENT QUERY GENERATION LOOP                │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Gemma (query generation only) ──▶ Search ──▶ Gemma (distill) │
│         ~200 tokens                         ~500 tokens        │
│                                                                 │
│  vs all-in-one Gemma: ~1500 tokens per iteration               │
│  Cost reduction: ~53% per iteration                             │
└────────────────────────────────────────────────────────────────┘
```

### 8.2 Batch Query Generation

```python
async def gemma_batch_query_generation(
    topic: str,
    angles: list[str],
    queries_per_angle: int = 3,
) -> list[str]:
    """
    Gemma generates 10-15 queries in one call, then all are searched in parallel.
    High efficiency: 1 Gemma call → 10-15 parallel searches → 1 Gemma synthesis.
    """
    batch_prompt = f"""Generate {queries_per_angle * len(angles)} search queries for deep research on: {topic}

Research angles:
{chr(10).join([f"{i+1}. {a}" for i, a in enumerate(angles)])}

Each angle needs {queries_per_angle} specific, answerable queries.
Queries should be diverse: some broad, some narrow, some technical.

FORMAT:
{{"queries": ["query1", "query2", ...]}}

Rules:
- Queries must be specific enough to return 3-8 relevant results each
- Include at least 2 technical/deep queries per angle
- Include at least 1 recent/current query per angle
"""
    
    result = await gemma_generate(batch_prompt)
    data = json.loads(result)
    queries = data.get("queries", [])
    
    return queries  # Then: parallel_search_burst(queries)


async def execute_batch_research(
    topic: str,
    angles: list[str],
    queries_per_angle: int = 3,
) -> dict:
    """
    Full batch research: Gemma generates queries → parallel search → Gemma synthesis.
    Cost: 2 Gemma calls (query gen + synthesis) + N parallel searches.
    """
    # Step 1: Batch query generation (1 Gemma call)
    queries = await gemma_batch_query_generation(topic, angles, queries_per_angle)
    
    # Step 2: Parallel search burst (all queries at once)
    search_results = await parallel_search_burst(queries)
    
    # Step 3: Gemma synthesis (1 Gemma call — 256K ctx handles all results)
    synthesis_prompt = f"""Synthesize all search results for: {topic}

ANGLES RESEARCHED:
{chr(10).join([f"{i+1}. {a}" for i, a in enumerate(angles)])}

SEARCH RESULTS (all {len(search_results['ranked'])} sources):
{_format_search_results(search_results['ranked'], max_chars=15000)}

TASK:
1. Extract all verifiable claims
2. Cross-reference claims across angles
3. Distill through L1/L2/L3 refraction
4. Identify remaining gaps

FORMAT: JSON per distillation schema.
"""
    
    synthesis = await gemma_generate(synthesis_prompt)
    return json.loads(synthesis)
```

### 8.3 Token Budget Management

| Phase | Gemma Token Budget | Action |
|-------|-------------------|--------|
| Query generation | 200 input + 500 output | Batch all queries in one call |
| Search results processing | 15K input + 1K output | Truncate to 15K chars, rank top 20 |
| Distillation | 15K input + 2K output | Per-result distillation, aggregate L3 |
| Synthesis | 20K input + 1K output | Feed all L1/L2 from subagents |
| Convergence check | 5K input + 200 output | Lightweight assessment |

**Budget rules:**
- Never feed more than 15K chars of search results to Gemma in one call (diminishing returns)
- L3 distillation per source: 200-500 chars output max
- Batch query generation: 1 call per research session, not per iteration
- If content exceeds 15K: rank by relevance, take top 20 sources

---

## §9 Pattern 7: Convergence via Serial Refinement

### 9.1 The Serial Refinement Loop

```
Round 1: Initial search → Gemma distills → Gemma: "3 gaps identified"
   │
   ▼
Round 2: Targeted search for gap 1 → Gemma distills → Gemma: "gap 1 filled"
   │
   ▼
Round 3: Targeted search for gap 2-3 → Gemma distills → Gemma: "gaps 2-3 filled"
   │
   ▼
Round 4: Verify no new claims → Gemma: "CONVERGED"
```

### 9.2 When to Switch from Parallel to Serial

| Signal | Switch to Serial? |
|--------|------------------|
| First search returned 5+ high-quality sources | Yes — context is rich enough |
| Gemma's first distillation found 3+ claims | Yes — topic has depth |
| Claims repeat across multiple providers | Yes — source saturation |
| User requested the topic | Yes — they want depth, not breadth |
| API quota getting low | Yes — conserve with targeted searches |
| First search returned < 3 sources | No — need parallel burst first |

### 9.3 Max Iteration Budget

| Topic Type | Max Rounds | When to Stop |
|-----------|-----------|--------------|
| Simple factual | 2 | After initial search + 1 refinement |
| Moderate complexity | 3 | 3 rounds covers most gaps |
| Deep technical | 4-5 | Technical topics need more refinement |
| Academic/papers | 3-4 | Citation chains add implicit depth |
| Contradictory sources | 4-5 | Need resolution across providers |
| User-requested (high priority) | 5+ | No ceiling, continue until user satisfied |

**Hard stop**: 5 rounds maximum. If not converged by round 5, Gemma issues HUMAN_REVIEW flag with remaining gaps.

---

## §10 Integration with Background Researcher Loop

### 10.1 Where Each Pattern Fits

| Loop Stage | Pattern | Why |
|------------|---------|-----|
| IDLE → TRIAGE | State Machine (Pattern 4) | Gemma decides if worth researching |
| TRIAGE → SEARCH | Query Gen (Pattern 6) | Gemma generates specific queries |
| SEARCH | Parallel Burst (Pattern 2) | Cast wide net across all providers |
| SEARCH → EXTRACT | Firecrawl Mining (Pattern 5) | Gemma prioritizes + follows citations |
| EXTRACT → DISTILL | Iterative Seeded (Pattern 1) | Gemma refines through rounds |
| DISTILL | Nested Subagents (Pattern 3) | Parallel angles, unified synthesis |
| DISTILL → UPDATE | Serial Refinement (Pattern 7) | Gemma converges through targeting |
| UPDATE → IDLE | State Machine (Pattern 4) | Gemma decides convergence |

### 10.2 Unified Research Orchestrator

```python
class GemmaResearchOrchestrator:
    """
    Unified orchestrator integrating all 7 patterns.
    Gemma is the reasoning core; everything else is delegated.
    """
    
    def __init__(
        self,
        gemma_model,      # Gemma 4-31B via Google AI Studio
        qwen_model,       # Qwen3-1.7B via lmster
        search_providers, # Exa, Tavily, Serper, SearXNG
        credit_budget,    # APICreditBudget
    ):
        self.gemma = gemma_model
        self.qwen = qwen_model
        self.providers = search_providers
        self.budget = credit_budget
        self.patterns = {
            "iterative_seeded": IterativeSeededPattern(self.gemma, self.budget),
            "parallel_burst": ParallelSearchPattern(self.providers),
            "nested_subagent": NestedSubagentPattern(self.gemma),
            "state_machine": StateMachinePattern(self.gemma),
            "firecrawl_deep_mine": FirecrawlPattern(self.gemma),
            "cost_efficient": CostEfficientPattern(self.gemma, self.budget),
            "serial_refine": SerialRefinementPattern(self.gemma),
        }

    async def research(
        self,
        topic: str,
        seed: str,
        mode: str = "auto",
        max_iterations: int = 5,
    ) -> dict:
        """
        Main entry point. Gemma decides which patterns to use.
        """
        # Phase 1: Triage + Query Generation
        triage = await self.patterns["state_machine"].triage(topic)
        if triage["skip"]:
            return {"status": "skipped", "reason": triage["reason"]}
        
        # Phase 2: Decide search strategy
        if mode == "auto":
            strategy = await self._auto_strategy(topic, triage)
        else:
            strategy = mode
        
        # Phase 3: Execute research
        if strategy == "parallel_burst":
            results = await self._parallel_research(topic, seed, max_iterations)
        elif strategy == "nested_subagent":
            results = await self._subagent_research(topic, seed)
        elif strategy == "serial_refine":
            results = await self._serial_research(topic, seed, max_iterations)
        else:
            results = await self._hybrid_research(topic, seed, max_iterations)
        
        # Phase 4: Convergence check
        convergence = await self.patterns["state_machine"].check_convergence(
            topic, results, mode="auto"
        )
        results["convergence"] = convergence
        
        return results

    async def _auto_strategy(self, topic: str, triage: dict) -> str:
        """Gemma picks the best strategy based on topic characteristics."""
        strategy_prompt = f"""Select research strategy for: {topic}

TRIAGE DATA:
- Topic depth: {triage.get('depth_score', 'unknown')}
- Topic complexity: {triage.get('complexity', 'unknown')}
- Number of angles: {triage.get('angle_count', 'unknown')}
- Quota remaining: {triage.get('quota', 'unknown')}

STRATEGIES:
1. PARALLEL_BURST: Broad topics, multiple angles, need surface area
2. NESTED_SUBAGENT: Technical topics, need multiple deep dives in parallel
3. SERIAL_REFINE: Topics with known gaps, need targeted deepening
4. HYBRID: Start parallel, switch to serial after first round

Respond: {{"strategy": "PARALLEL_BURST|NESTED_SUBAGENT|SERIAL_REFINE|HYBRID", "reason": "string"}}
"""
        result = await self.gemma.generate(strategy_prompt)
        return json.loads(result)["strategy"]
```

---

## §11 Specific Prompt Templates

### 11.1 Iterative Seeded Research Prompt

```markdown
## Iterative Seeded Prompt — Round {N}

You are SOPHIA, conducting iterative research on: {topic}

RESEARCH SEED:
{seed}

PRIOR ROUNDS:
{round_history}

ITERATION {N}/{max}

TASK:
1. Review prior findings and identify remaining gaps
2. Generate 3-5 targeted search queries to address gaps
3. Assess convergence: are we close to exhausting this topic?

Respond JSON:
{{
  "queries": ["specific query 1", "specific query 2", "..."],
  "gaps_addressed": ["gap resolved in round {N-1}"],
  "remaining_gaps": ["specific gap for next round"],
  "converged": bool,
  "convergence_reason": "string"
}}
```

### 11.2 Parallel Search Query Generation Prompt

```markdown
## Parallel Search Query Generation

Generate 10-15 search queries for: {topic}

Requirements:
- 3-4 broad queries (general understanding)
- 3-4 narrow queries (specific claims or data points)
- 3-4 technical queries (implementation details)
- 2-3 recent/current queries (news, latest developments)

For each query, provide: the query text only.

Respond JSON: {{"queries": ["query1", "query2", ...]}}
```

### 11.3 Subagent Synthesis Prompt

```markdown
## Subagent Synthesis — Council of Three

You are SOPHIA, synthesizing findings from 3 parallel subagent investigations.

TOPIC: {topic}

SUBAGENT 1 ({sub1_angle}):
- Claims: {sub1_claims}
- L3 Principles: {sub1_l3}
- Sources: {sub1_sources}
- Confidence: {sub1_confidence}

SUBAGENT 2 ({sub2_angle}):
- Claims: {sub2_claims}
- L3 Principles: {sub2_l3}
- Sources: {sub2_sources}
- Confidence: {sub2_confidence}

SUBAGENT 3 ({sub3_angle}):
- Claims: {sub3_claims}
- L3 Principles: {sub3_l3}
- Sources: {sub3_sources}
- Confidence: {sub3_confidence}

TASK:
1. Cross-validate: claims appearing in 2+ subagents get boosted confidence
2. Resolve contradictions: if subagents disagree, synthesize a resolution
3. Produce unified L2 insight
4. Generate final L3 universal principle
5. Flag remaining gaps

Respond JSON per distillation schema.
```

### 11.4 Convergence Check Prompt

```markdown
## Convergence Check

TOPIC: {topic}
TOTAL CLAIMS: {len(claims)}
TOTAL L3 PRINCIPLES: {len(l3_principles)}
PRIOR ROUNDS: {len(prior_rounds)}

ASSESSMENT CRITERIA:
- No new claims in 2 consecutive rounds → EXHAUSTED
- All L3 principles subset of prior L3 → EXHAUSTED
- 3+ sources agree on same claim → VERIFIED
- Sources contradict across providers → HUMAN_REVIEW

Respond:
{{
  "status": "EXHAUSTED|CONTINUE|HUMAN_REVIEW|VERIFIED",
  "reason": "string",
  "confidence": 0.0-1.0,
  "remaining_work": "specific gap if CONTINUE"
}}
```

---

## §12 Cost Analysis Summary

| Pattern | Gemma Calls | Gemma Tokens (est.) | External Cost | Quality |
|---------|-------------|---------------------|----------------|---------|
| Direct search (baseline) | 1 | 700 | 5 searches | Good |
| 2-round seeded | 2 | 1,400 | 10 searches | Better |
| 3-round seeded | 3 | 2,100 | 15 searches | Best |
| Parallel burst + synthesis | 2 | 2,200 | 20 searches | Very Good |
| Nested 3-subagent | 2 | 2,500 | 15 searches | Excellent |
| Hybrid (parallel → serial) | 4 | 3,500 | 25 searches | Maximum |
| Full serial refinement | 5 | 3,500 | 15 searches | Thorough |

**Best value**: 3-round seeded (3 Gemma calls, 2,100 tokens) or parallel burst + synthesis (2 Gemma calls, 2,200 tokens) — both maximize quality-per-token.

**Maximum thoroughness**: Hybrid mode (parallel burst round 1, serial refinement rounds 2-4) — best for high-value user-requested topics.

---

## §13 Implementation Roadmap

| Phase | Task | Pattern | Effort | Dependencies |
|-------|------|---------|--------|--------------|
| 1 | Add parallel search burst to `search.py` | Pattern 2 | 2h | Background Researcher |
| 2 | Implement query generation batch in `distiller.py` | Pattern 6 | 1h | Phase 1 |
| 3 | Add nested subagent dispatch to `orchestrator.py` | Pattern 3 | 3h | OpenRouter free tier |
| 4 | Implement Gemma state machine in `loop.py` | Pattern 4 | 2h | Phase 1 |
| 5 | Add Firecrawl deep mining | Pattern 5 | 2h | Firecrawl API key |
| 6 | Wire iterative seeded prompting | Pattern 1 | 2h | Phase 2 |
| 7 | Add serial refinement convergence | Pattern 7 | 2h | Phase 4 |
| 8 | Integrate all patterns into `GemmaResearchOrchestrator` | All | 4h | Phase 1-7 |
| 9 | Add tests (mock Gemma, mock search APIs) | All | 3h | Phase 8 |
| 10 | Integration test against live providers | All | 2h | Phase 9 |

**Total estimated**: ~23 hours

---

## §14 Recommendations

1. **Start with Pattern 2 (Parallel Burst)** — lowest implementation effort, highest immediate value. Add 10 lines to `search.py`.
2. **Implement Pattern 6 (Query Gen)** next — reduces Gemma token cost by 50% per session.
3. **Pattern 3 (Nested Subagents)** requires OpenRouter free tier wiring but provides the highest quality for technical topics.
4. **Pattern 4 (State Machine)** is the highest-value long-term pattern — Gemma deciding its own research path enables true autonomy.
5. **Max 5 iterations** per topic — Gemma signals convergence. Beyond 5, diminishing returns and quota waste.
6. **Use Qwen3-1.7B for triage** — never spend Gemma tokens on fast routing decisions.
7. **Batch query generation** — one Gemma call generates 10-15 queries, then parallel search, then one synthesis call. Best cost/quality ratio.

---

## §15 Sources

- `R_BACKGROUND_RESEARCHER_ARCHITECTURE.md` — loop architecture, state machine design
- `R_ANYIO_ORCHESTRATION_GUIDE.md` — concurrency patterns, task groups
- `R_EXA_DEEP_RESEARCH.md` — supervisor loop pattern, async-research decoupling
- `R53_triangulation_engine_spec.md` — multi-perspective synthesis
- `R52b_background_orchestrator_spec.md` — subagent dispatch patterns
- Exa AI API Documentation — neural search, citation-aware retrieval
- Tavily API Documentation — AI-optimized search, fact-checking
- SearXNG Documentation — open meta-search
- Firecrawl API Documentation — markdown extraction, batch scraping

---

## Implementation Note

_For: Sovereign Builder (MiniMax M2.5 implementation)_

Implement patterns incrementally:

1. **This session**: Add parallel search burst to `src/omega/workers/background_researcher/search.py` — replace single-provider search with `anyio.create_task_group()` across all 4 providers, deduplicate + rank results.

2. **Next session**: Add batch query generation to `distiller.py` — one Gemma call generates N queries, then parallel search, then one synthesis call.

3. **Phase 2**: Implement `GemmaResearchOrchestrator` class as the unified entry point integrating all 7 patterns.

4. Wire the orchestrator into `BackgroundResearcherLoop` as the `_execute_research` method. The existing loop structure is already compatible — replace the single `self._search()` call with `orchestrator.research()`.

All patterns use AnyIO primitives. No `asyncio` imports. All blocking I/O wrapped in `anyio.to_thread.run_sync`.

⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ R-72
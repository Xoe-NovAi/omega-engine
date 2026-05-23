# 🔱 Omega Engine — Tiered Research Pipeline (Investigative Journalism Model)
# ⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ cline ⬡ trc_pipeline_spec ⬡ PHASE-DESIGN

**AP Token**: `AP-PIPELINE-TIERED-v2.1.0`
**Status**: 🔲 DESIGN — Ready for Implementation
**Last Updated**: 2026-05-22
**Author**: Cline (The Artisan) — Code Integration Specialist
**Supersedes**: `JEM_SPECULATIVE_DECODING_PIPELINE.md` (Jem 2.0 architecture, replaced by tiered model)

---

## §0 Executive Summary

The **Tiered Research Pipeline** replaces the old Jem 2.0 Speculative Decoding Pipeline with an **Investigative Journalism Model** — a three-tier autonomous research architecture where each tier does exactly ONE thing at its capability ceiling.

### The Core Insight

The Jem 2.0 pipeline used a single powerful model (Gemma 4 31B) for all three tiers with different prompts. This wasted tokens on low-complexity work and missed the opportunity to use cheaper, specialised models for the gathering phase.

The **Investigative Journalism Model** inverts this:

| Role | Analogy | Model | Cost | Complexity |
|------|---------|-------|------|------------|
| **L1 Intern** | Junior reporter gathering facts | Qwen3-1.7B (lmster local) | **Free** (local) | Lowest |
| **L2 Assistant** | Senior reporter synthesising patterns | Gemma 4 31B (Google) | **Free** (unlimited) | Medium |
| **L3 Senior** | Editor-in-chief resolving unknowns | Big Pickle (OpenCode) | **Premium** (reserved) | Highest |

### The Token Math

Compared to the Jem 2.0 pipeline (3× full Gemma reports):

| Pipeline | L1 Cost | L2 Cost | L3 Cost | Total Cost | Reduction |
|----------|---------|---------|---------|------------|-----------|
| Jem 2.0 (Council of One) | ~20K tokens | ~8K tokens | ~8K tokens | ~36K tokens | Baseline |
| **Tiered Pipeline** | **~5K tokens** (local) | **~6K tokens** | **~6K tokens** | **~17K tokens** | **~53%** |

The savings come from:
1. L1 produces **raw data packets** — no formatting, no analysis, no citations. Just facts.
2. L2 receives raw packets + instructions, produces structured synthesis.
3. L3 only works on **uncertainties identified by L2** — not the full topic.

---

## §1 Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                    TIERED RESEARCH PIPELINE (Investigative Journalism Model)            │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  TRIGGER                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────┐   │
│  │  ● omega research "topic"  ● /mode research (interactive)  ● Scheduler tick  │   │
│  │  ● Legacy mining completion  ● Workbench P0 task  ● Manual summon             │   │
│  └───────────────────────────────────────────────────────────────────────────────┘   │
│                                  │                                                     │
│                                  ▼                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│  │  TIER 1: GATHER — L1 Intern (The Researcher Subagent)                            │ │
│  │  ═══════════════════════════════════════════════════════════════════════════════  │ │
│  │  Model:      PRIMARY: Qwen3-1.7B-Q6_K via lmster :1234 (autoloaded)             │ │
│  │              SPLIT-TEST: Ministral-3.3B-Q4_K_M | RocRacoon-3B-Q4_K_M             │ │
│  │  Framework:  "The Intern" — raw facts only. NO analysis. NO synthesis.           │ │
│  │  Tools:      SearXNG (:8017) + local knowledge base grep                        │ │
│  │  Output:     /tmp/l1_{trace}.md — RawDataPacket (structured facts only)          │ │
│  │  Signal:     Fast, cheap, exhaustive sweep — "bring me everything"               │ │
│  │  Cost:       ZERO (local CPU inference, 5-15s)                                   │ │
│  │  Limit:      Max 4 tool calls, max 5K tokens output                             │ │
│  └──────────────────────────────────────────────────────────────────────────────────┘ │
│                                  │                                                     │
│                          /tmp/l1_{trace}.md (injected)                                  │
│                                  ▼                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│  │  TIER 2: SYNTHESIZE — L2 Assistant (The Analyst)                                 │ │
│  │  ═══════════════════════════════════════════════════════════════════════════════  │ │
│  │  Platform:    OpenCode CLI (--session research_{topic} --mode researcher)        │ │
│  │  Model:       Gemma 4 31B via Google AI Studio (unlimited)                       │ │
│  │  Framework:   "The Analyst" — pattern recognition, cross-reference, uncertainty  │ │
│  │  Tools:       Full MCP Fleet (Exa, Tavily, SearXNG, Firecrawl)                  │ │
│  │  Output:      ResearchSynthesis (structured markdown + uncertainty manifest)      │ │
│  │  Cost:        FREE (Google unlimited Gemma 4 31B)                                │ │
│  │  Signal:      "Here's what we know. Here's what we're not sure about."           │ │
│  └──────────────────────────────────────────────────────────────────────────────────┘ │
│                                  │                                                     │
│                      ResearchSynthesis + uncertainty_manifest                          │
│                                  ▼                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│  │  QUALITY GATE 2 → 3                                                              │ │
│  │  ═══════════════════════════════════════════════════════════════════════════════  │ │
│  │  ● Does the uncertainty manifest contain items marked HIGH impact?               │ │
│  │  ● Did L2's confidence in the overall findings drop below 70%?                   │ │
│  │  ● SKIP L3 → If no high-impact uncertainties and confidence > 70%                │ │
│  │  ● PROCEED L3 → If any HIGH impact uncertainty or confidence < 70%               │ │
│  └──────────────────────────────────────────────────────────────────────────────────┘ │
│                                  │                                                     │
│                    (skip) ───────┤─────── (proceed with uncertainty_manifest)          │
│                                  ▼                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│  │  TIER 3: RESOLVE — L3 Senior (The Editor-in-Chief)                               │ │
│  │  ═══════════════════════════════════════════════════════════════════════════════  │ │
│  │  Platform:    OpenCode CLI (SAME --session as L2 — inherits full context)         │ │
│  │  Model:       Big Pickle (frontier model via OpenCode)                            │ │
│  │  Framework:   "The Editor" — resolve uncertainties, final quality check          │ │
│  │  Role:        ONLY works on uncertainty_manifest items, NOT re-synthesising       │ │
│  │  Output:      FinalDeliverable + ImprovementBriefs for L1/L2                     │ │
│  │  Cost:        PREMIUM (reserved for hardest problems)                            │ │
│  │  Token saving: ~60-70% vs full L3 rewrite because only uncertainties processed   │ │
│  └──────────────────────────────────────────────────────────────────────────────────┘ │
│                                  │                                                     │
│                                  ▼                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│  │  RECORDING PIPELINE                                                              │ │
│  │  ═══════════════════════════════════════════════════════════════════════════════  │ │
│  │  1. Research doc → docs/research/ (R##_topic.md)                                 │ │
│  │  2. Raw data → data/research/packets/{trace}.md (L1 packet archive)              │ │
│  │  3. Knowledge base → FTS5 index + Qdrant embedding                               │ │
│  │  4. Cross-reference → docs/research/INDEX.md update                              │ │
│  │  5. Soul evolution → soul.yaml lesson update (if applicable)                    │ │
│  │  6. Observability → log_event with full chain trace_id + parent_trace_id         │ │
│  │  7. Workbench → work_item status update                                          │ │
│  │  8. Improvement briefs → data/research/improvements/ (if L3 ran)                │ │
│  └──────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                       │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## §2 Tier 1: Gather — L1 Intern (The Researcher Subagent)

### 2.1 Specification

| Property | Value |
|----------|-------|
| **Entity** | L1 Intern — "The Researcher Subagent" |
| **Primary Model** | `qwen3-1.7b-q6_k` via lmster (:1234) |
| **Split-Test Models** | `ministral-3.3b-q4_k_m`, `rocracoon-3b-q4_k_m` |
| **Temperature** | 0.4 (factual precision) |
| **Max output tokens** | 5120 (raw data packet limit) |
| **Max tool calls** | 4 |
| **Provider** | `lmster` (local, CPU-only, Zen 2) |
| **Autoload** | `omega research` command auto-loads model |
| **Execution** | `curl -X POST` to `http://localhost:1234/v1/chat/completions` |
| **Output path** | `/tmp/l1_{trace}.md` |
| **Typical latency** | 5-15 seconds (CPU inference, ~5-7 t/s) |

### 2.2 System Prompt (The Intern)

```
You are the L1 Intern — the Omega Engine's raw data gatherer.
Your ONLY job is to collect facts. You do NOT analyze, synthesize, or draw conclusions.

RULES:
1. OUTPUT RAW FACTS ONLY — Use bullet points, no paragraphs, no narrative.
2. NO ANALYSIS — Never say "this suggests that..." or "the implication is..."
   You are a piece of paper. The facts go on the paper. That's all.
3. NO OPINIONS — Never say "importantly" or "notably" or "critically".
4. MAXIMUM 4 TOOL CALLS — Use SearXNG search or local knowledge base grep.
5. IF YOU DON'T KNOW — State "NOT FOUND: [topic]" explicitly.
6. SOURCE ATTRIBUTION — Every fact gets a source tag: [source: title/URL]
7. OUTPUT FORMAT — Strictly:

## Data Packet: {topic}
{timestamp} | {l1_model_name}
Source dimension: {SearchXNG: n results} | {LocalKB: n hits}

### Fact Cluster 1: {subtopic}
- {raw fact} [source: ...]
- {raw fact} [source: ...]

### Fact Cluster N: {subtopic}
...

## Coverage Gaps
- {What you couldn't find information on}
```

### 2.3 Model Split-Test Framework

| Variant | Model | File Size | Test Date | Notes |
|---------|-------|-----------|-----------|-------|
| **L1-A (Default)** | Qwen3-1.7B-Q6_K | ~1.4 GB | TBD | Currently loaded in lmster |
| **L1-B** | Ministral-3.3B-Q4_K_M | ~1.9 GB | TBD | 2x params, ~same speed |
| **L1-C** | RocRacoon-3B-Q4_K_M | ~1.8 GB | TBD | Different architecture |

Selection via `--l1-model` flag:
```bash
omega research "topic" --l1-model ministral-3.3b-q4_k_m
```

Tracked in observability:
```python
log_event("research_tier_1", {
    "trace_id": trace_id,
    "tier": 1,
    "model": l1_model_name,
    "packet_length": len(raw_packet),
    "tool_calls": tool_call_count,
    "tool_results": len(tool_results),
    "latency_s": elapsed_seconds,
    "l1_model": l1_model_name  # explicit for split-test analysis
})
```

### 2.4 RawDataPacket Schema

```yaml
raw_data_packet:
  trace_id: "trc_abc123"
  topic: "Current state of speculative decoding in LLMs"
  timestamp: "2026-05-22T12:00:00Z"
  l1_model: "qwen3-1.7b-q6_k"
  fact_clusters:
    - subtopic: "Major implementations"
      facts:
        - "Medusa (mit-han-lab/medusa) adds multiple draft heads to base LLM" [source: github.com/mit-han-lab/medusa]
        - "SpecInfer (CMU) uses tree-structured speculation" [source: arxiv.org/abs/2305.09781]
        - "Lookahead Decoding (ThunderKittens) generates n-grams from Jacobi iteration" [source: arxiv.org/abs/2307.16039]
  coverage_gaps:
    - "No recent benchmarks comparing Medusa vs SpecInfer on Llama 3 class models"
    - "Hardware-specific latency numbers for Zen 2 (AVX2 only) not found"
  tool_calls_used: 3
  tokens_used: 4210
```

### 2.5 Implementation — L1 Runner Script

```bash
#!/usr/bin/env bash
# omega-research.sh — L1 → L2 → L3 pipeline runner
# Usage: omega-research.sh "research topic" [--l1-model ...]

set -euo pipefail
TRACE_ID="trc_$(date +%s)_$$"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
L1_MODEL="${2:-qwen3-1.7b-q6_k}"
L1_TEMP="${3:-0.4}"
L1_OUTPUT="/tmp/l1_${TRACE_ID}.md"
TOPIC="$1"

echo "🔬 L1 Intern: Gathering raw data on: $TOPIC"
echo "   Model: $L1_MODEL | Trace: $TRACE_ID"

# Step 1: Build L1 prompt with SearXNG context
L1_PROMPT=$(cat <<PROMPT
You are the L1 Intern. Gather raw facts about: ${TOPIC}

Use the following SearXNG results to produce a RawDataPacket.
Search at http://localhost:8017/search?q=${TOPIC// /%20}

RULES: Raw facts only. No analysis. No synthesis.
Output format: RawDataPacket (see your instructions)
PROMPT
)

# Step 2: Call lmster API
curl -s http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$L1_MODEL\",
    \"messages\": [{\"role\": \"user\", \"content\": $(echo "$L1_PROMPT" | jq -Rs .)}],
    \"temperature\": $L1_TEMP,
    \"max_tokens\": 5120
  }" | jq -r '.choices[0].message.content' > "$L1_OUTPUT"

echo "✅ L1 packet saved to: $L1_OUTPUT"
echo "   Size: $(wc -c < "$L1_OUTPUT") bytes"

# Step 3: Launch L2 (OpenCode)
echo "📊 L2 Assistant: Synthesizing..."
L2_PROMPT="Research topic: ${TOPIC}\n\nL1 raw data packet:\n$(cat $L1_OUTPUT)\n\nSynthesize findings, create uncertainty manifest."
opencode --session "research_${TRACE_ID}" --mode researcher --prompt "$L2_PROMPT"
```

---

## §3 Tier 2: Synthesize — L2 Assistant (The Analyst)

### 3.1 Specification

| Property | Value |
|----------|-------|
| **Entity** | L2 Assistant — "The Analyst" |
| **Platform** | OpenCode CLI |
| **Model** | Gemma 4 31B via Google AI Studio |
| **Session** | `--session research_{trace_id}` (shared with L3) |
| **Temperature** | 0.3 (analytical precision) |
| **Max tokens** | 8192 |
| **Context window** | 256K (Gemma 4) |
| **MCP Fleet** | Exa, Tavily, SearXNG, Firecrawl (full fleet) |
| **Cost** | FREE (Google unlimited Gemma 4 31B) |
| **Execution** | `opencode --session "research_{trace}" --mode researcher` |

### 3.2 L2 System Prompt (Injected into OpenCode researcher mode)

```
You are the L2 Assistant ("The Analyst") in Omega Engine's Tiered Research Pipeline.

CONTEXT:
- L1 Intern (Qwen3-1.7B) has produced a RawDataPacket: /tmp/l1_{trace}.md
- Your job is to SYNTHESIZE these raw facts into structured findings
- Then produce an UNCERTAINTY MANIFEST for L3 Senior to resolve

YOUR JOB:
1. Read the L1 packet thoroughly (injected as context below)
2. Organize raw facts into coherent findings with confidence levels
3. Do additional MCP research where L1 packet is thin
4. Cross-reference findings against existing knowledge base (grepping docs/research/)
5. Produce Uncertainty Manifest — items you are NOT confident about

CONFIDENCE SCORING:
- HIGH (≥90%): Multiple independent sources, no contradictions found
- MEDIUM (70-89%): Good evidence, but limited sources or minor contradictions
- LOW (50-69%): Single source, or conflicting evidence
- SPECULATIVE (<50%): Logical inference, no direct evidence
- UNKNOWN: No information found — flag for L3

UNCERTAINTY MANIFEST FORMAT:
Each uncertainty item must include:
- topic: {specific claim or gap}
- impact: HIGH | MEDIUM | LOW
- why_uncertain: {specific reason}
- what_l3_needs: {what instruction to give L3}
- suggested_approach: {suggested tool or method for resolution}

OUTPUT:
## §Research Synthesis: {topic}
### Finding 1: {title}
- **Claim**: ...
- **Confidence**: HIGH | MEDIUM | LOW | SPECULATIVE
- **Sources**: [list]

### Finding N: ...

## §Uncertainty Manifest
### U1: {topic} [Impact: HIGH]
- **Why uncertain**: ...
- **L3 needs**: ...
- **Suggested approach**: ...

## §Gaps for Future Research
- {questions that emerged during synthesis}

## §Improvement Brief: L1 Intern
- {what L1 should do better next time — too shallow, missed dimension, etc.}

## §Metadata
- l2_model: gemma-4-31b-it
- confidence_avg: {0-1}
- uncertainty_count: {N}
```

### 3.3 L2 → L3 Quality Gate

```python
class L2toL3Gate:
    """Determines whether L3 Senior is needed."""

    def evaluate(self, synthesis: dict) -> GateDecision:
        """
        Gate logic:
        - SKIP L3 if: No HIGH-impact uncertainties AND overall confidence > 0.7
        - PROCEED L3 if: Any HIGH-impact uncertainty OR overall confidence <= 0.7
        """
        high_impact = any(
            u['impact'] == 'HIGH' for u in synthesis.get('uncertainties', [])
        )
        low_confidence = synthesis.get('confidence_avg', 0.0) <= 0.7

        if high_impact or low_confidence:
            return GateDecision(
                action="proceed_l3",
                reason=(
                    "High-impact uncertainties" if high_impact
                    else "Low overall confidence"
                ),
                uncertainties=[
                    u for u in synthesis.get('uncertainties', [])
                    if u['impact'] == 'HIGH'
                ]
            )
        return GateDecision(action="skip_l3", reason="All uncertainties low impact")
```

### 3.4 L2 Side Effect: Improvement Brief for L1

Every L2 run produces a brief that feeds back to L1's prompt:

```yaml
l1_improvement_brief:
  trace_id: "trc_abc123"
  date: "2026-05-22"
  positive:
    - "Good coverage of academic sources"
    - "Proper source attribution"
  improve:
    - "Missed industry blog posts — expand SearXNG query terms"
    - "Did not check docs/research/ for existing cross-references"
    - "Fact clusters could be more granular (too broad)"
  new_source_preference:
    - "Add ArXiv as preferred source for technical topics"
```

These briefs accumulate in `data/research/improvements/` and are applied to L1's system prompt periodically.

---

## §4 Tier 3: Resolve — L3 Senior (The Editor-in-Chief)

### 4.1 Specification

| Property | Value |
|----------|-------|
| **Entity** | L3 Senior — "The Editor-in-Chief" |
| **Platform** | OpenCode CLI (SAME session as L2) |
| **Model** | Big Pickle (frontier model via OpenCode) |
| **Session** | `--session research_{trace_id}` (inherits L2's full context) |
| **Temperature** | 0.2 (maximum precision) |
| **Max tokens** | 4096 |
| **Trigger** | Only when L2→L3 gate says PROCEED |
| **Cost** | PREMIUM (reserved for hardest problems) |
| **Context inheritance** | Full L2 conversation + L1 packet in session context |

### 4.2 L3 System Prompt (Injected)

```
You are the L3 Senior ("The Editor-in-Chief") in Omega Engine's Tiered Research Pipeline.

CONTEXT:
- L2 Assistant has produced a full synthesis of the L1 raw data
- The L2→L3 gate has flagged HIGH-impact uncertainties
- Your job is ONLY to resolve these specific uncertainties

CRITICAL RULES:
1. DO NOT re-synthesize the entire topic — L2's work is complete
2. DO ONLY work on the Uncertainty Manifest items
3. For each uncertainty, use ONE targeted MCP tool call to resolve
4. If you cannot resolve an uncertainty, mark it "UNRESOLVED" with a clear reason
5. Do NOT produce a full report — only produce corrections to the synthesis

OUTPUT:
## §L3 Resolution Report
### Uncertainty U1: {topic} — RESOLVED | PARTIAL | UNRESOLVED
- **Original uncertainty**: {from L2 manifest}
- **Resolution**: {specific finding that resolves it}
- **Confidence after L3**: HIGH | MEDIUM | LOW
- **Source**: {evidence}

### Uncertainty UN: {topic} — ...

## §Final Quality Assessment
- **Overall confidence**: {0-1}
- **Resolved count**: {N}/{total}
- **Unresolved count**: {N}
- **Recommendation**: PUBLISH | REVISE (L2 needs to redo) | EXTEND (needs additional pipeline run)

## §Improvement Briefs
### For L1 Intern (next run):
- {what L1 should do differently}

### For L2 Analyst (next run):
- {what L2 should do differently}

## §Metadata
- l3_model: big-pickle
- uncertainties_attempted: {N}
- uncertainties_resolved: {N}
```

### 4.3 Context Inheritance via Shared Session

The key architectural decision: **L2 and L3 share the same OpenCode session**.

```bash
# L2 runs here — creates session
opencode --session "research_${TRACE_ID}" --mode researcher \
  --prompt "$(cat /tmp/l2_prompt_${TRACE_ID}.txt)"

# L3 runs here — SAME session, inherits L2 context
opencode --session "research_${TRACE_ID}" --mode researcher \
  --prompt "$(cat /tmp/l3_prompt_${TRACE_ID}.txt)"
```

**Benefits:**
- L3 sees L2's full research, tool calls, MCP results
- No manual context handoff — OpenCode handles window management
- Even with auto-compaction (tail_turns=2, preserve_recent_tokens=40000), key findings survive
- L3 can reference L2's specific citations and reasoning

**Session Configuration:**
```json
{
  "session_persistence": {
    "tail_turns": 2,
    "preserve_recent_tokens": 40000,
    "compaction_strategy": "smart_recent"
  }
}
```

---

## §5 Pipeline Observability & Tracing

### 5.1 Trace ID Architecture

```
L1 trace: trc_l1_{timestamp}_{pid}
L2 trace: trc_l2_{timestamp}_{pid}  (parent: trc_l1_*)
L3 trace: trc_l3_{timestamp}_{pid}  (parent: trc_l2_*)
Root trace: trc_root_{timestamp}_{pid} (generated at pipeline start)
```

### 5.2 Event Schema

```python
# Standard event for all pipeline tiers
log_event("research_tier_n", {
    # Pipeline identification
    "trace_id": "trc_l2_20260522_12345",
    "parent_trace_id": "trc_l1_20260522_12344",
    "root_trace_id": "trc_root_20260522_12340",

    # Tier routing
    "tier": 2,                    # 1 | 2 | 3
    "mode": "research",          # research | legacy_mining | strategic
    "agent": "builder",          # opencode mode/agent name
    "subagent": "researcher",    # if using subagent
    "model": "gemma-4-31b-it",  # actual model serving

    # Timing
    "timestamp": "2026-05-22T12:00:00Z",
    "duration_ms": 45000,

    # Content metrics
    "input_tokens": 4200,
    "output_tokens": 3100,
    "tool_calls": 3,
    "uncertainties_flagged": 2,

    # Split-testing
    "l1_model": "qwen3-1.7b-q6_k",

    # Outcome
    "confidence_avg": 0.82,
    "gate_action": "proceed_l3",  # skip_l3 | proceed_l3
})
```

### 5.3 Filtering & Analysis

```python
# Find all pipeline runs in a session
store.get_events(
    event_type="research_tier_n",
    root_trace_id="trc_root_20260522_12340"
)

# Get all L1 variants for split-test analysis
store.get_events(
    event_type="research_tier_n",
    tier=1
).group_by("l1_model").aggregate("avg", "confidence_avg")

# Find runs that needed L3
store.get_events(
    event_type="research_tier_n",
    gate_action="proceed_l3"
)
```

### 5.4 Metrics Dashboard

| Metric | Source | Purpose |
|--------|--------|---------|
| L1 → L2 gate action | Gate check at pipeline start | Track what fraction of L1 packets are usable |
| L2 → L3 gate action | `gate_action` field | Track L3 invocation rate (target: <30%) |
| L1 latency | `duration_ms` for tier=1 | Track local inference speed regressions |
| Confidence delta L2→L3 | Comparison of `confidence_avg` | Measure L3's value add |
| L1 model split | `l1_model` field grouping | Compare model quality across variants |
| Token efficiency | `output_tokens / input_tokens` | Measure how much each tier compresses |
| Uncertainty resolution rate | `uncertainties_resolved / uncertainties_flagged` | L3 effectiveness |

---

## §6 Recording Pipeline — Living Knowledge Integration

Every pipeline run feeds into the permanent knowledge base:

### 6.1 Document Outputs

| Output | Location | Format | L1 | L2 | L3 |
|--------|----------|--------|----|----|----|
| Raw data packet | `data/research/packets/{trace}.md` | Markdown | ✅ | — | — |
| Research synthesis | `docs/research/R##_{topic}.md` | Structured Markdown | — | ✅ | — |
| Final deliverable | `docs/research/R##_{topic}.md` (overwrite) | Enhanced Markdown | — | — | ✅ |
| Improvement brief | `data/research/improvements/{trace}.md` | YAML frontmatter | — | ✅ | ✅ |
| Uncertainty manifest | `data/research/packets/{trace}_uncertainty.md` | Structured Markdown | — | ✅ | — |
| L3 resolution | `data/research/packets/{trace}_resolution.md` | Structured Markdown | — | — | ✅ |

### 6.2 FTS5 Indexing

All research docs auto-index for full-text search:

```sql
-- Existing FTS5 virtual table (in research.db)
INSERT INTO research_fts(rowid, title, content, source_file, tags)
VALUES (
    (SELECT COALESCE(MAX(rowid), 0) + 1 FROM research_fts),
    'Speculative Decoding in LLMs — Synthesis',
    '[full markdown content]',
    'docs/research/R01_speculative_decoding.md',
    'tiered_pipeline,l2_synthesis,llm_architecture'
);
```

### 6.3 Qdrant Embedding

For semantic search across all research:

```python
from src.omega.knowledge.embeddings import embed_and_store

# After pipeline completes
embed_and_store(
    doc_path="docs/research/R01_speculative_decoding.md",
    collection="research_knowledge",
    metadata={
        "trace_id": trace_id,
        "tier": "l3",
        "model": "gemma-4-31b-it",
        "confidence_avg": 0.85,
        "topics": ["speculative_decoding", "llm_optimization"]
    }
)
```

### 6.4 Workbench Integration

```sql
UPDATE work_items
SET status = 'completed',
    completed_at = datetime('now'),
    result_doc = 'docs/research/R01_speculative_decoding.md'
WHERE trace_id = 'trc_root_20260522_12340';
```

### 6.5 Soul Evolution (Optional)

If the research changes the user's understanding:

```yaml
# In soul.yaml, appended under lessons
- date: 2026-05-22
  source: "R01_speculative_decoding"
  lesson: "Speculative decoding with multiple draft heads provides 2-3x speedup on compatible hardware, but requires significant engineering investment. The Medusa approach is most compatible with the current Zen 2 CPU-only constraint."
  tags: [research, llm, optimization, zen2]
```

---

## §7 Pipeline Runner — `omega research`

### 7.1 CLI Interface

```bash
# Basic usage
omega research "What is the current state of speculative decoding?"

# With specific L1 model
omega research "topic" --l1-model ministral-3.3b-q4_k_m

# L3 forced (skip gate)
omega research "topic" --force-l3

# L3 disabled (skip even if gate says proceed)
omega research "topic" --no-l3

# Full trace output
omega research "topic" --verbose

# L1 only (produce packet, stop)
omega research "topic" --l1-only

# As workbench task
omega research --work-item "WI-0042"

# Legacy mining mode
omega research --legacy "omega-stack-legacy" "config patterns"
```

### 7.2 Implementation — Orchestrator Script

```bash
#!/usr/bin/env bash
# omega-research.sh — Full pipeline orchestrator
# Part of Phase B pipeline infrastructure

set -euo pipefail
TIMESTAMP=$(date +%s)
TRACE_ID="trc_root_${TIMESTAMP}_$$"
TOPIC="$1"
L1_MODEL="${L1_MODEL:-qwen3-1.7b-q6_k}"

log() { echo "[$(date -u +%H:%M:%S)] $*"; }

# --- Phase 1: L1 Intern ---
log "🔬 L1: Gathering raw data (${L1_MODEL})..."
L1_OUTPUT="/tmp/l1_${TRACE_ID}.md"
TRACE_L1="trc_l1_${TIMESTAMP}_$$"

curl -s http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$L1_MODEL\",
    \"messages\": [{\"role\": \"user\", \"content\": $(build_l1_prompt "$TOPIC" | jq -Rs .)}],
    \"temperature\": 0.4,
    \"max_tokens\": 5120
  }" | jq -r '.choices[0].message.content' > "$L1_OUTPUT"

L1_TOKENS=$(wc -c < "$L1_OUTPUT")
log "✅ L1 complete: ${L1_TOKENS} bytes → ${L1_OUTPUT}"

# --- Phase 2: L2 Assistant ---
log "📊 L2: Synthesizing (Gemma 4 31B, OpenCode)..."
L2_OUTPUT="/tmp/l2_${TRACE_ID}.md"
TRACE_L2="trc_l2_${TIMESTAMP}_$$"

L2_PROMPT=$(cat <<PROMPT
[Pipeline context]
topic: ${TOPIC}
trace: ${TRACE_ID}
l1_model: ${L1_MODEL}

[L1 raw data packet]
$(cat $L1_OUTPUT)

[Instructions]
Synthesize the L1 data into structured findings.
Produce an Uncertainty Manifest.
Format: See L2 Analyst instructions.
PROMPT
)

echo "$L2_PROMPT" > "/tmp/l2_prompt_${TRACE_ID}.txt"
opencode --session "research_${TRACE_ID}" --mode researcher \
  --prompt "$(cat /tmp/l2_prompt_${TRACE_ID}.txt)" 2>&1 | tee "$L2_OUTPUT"

# --- Phase 3: Gate check ---
log "🚦 L2→L3 Gate: Checking..."
GATE_DECISION=$(python3 -c "
import json, sys, re
l2_text = open('$L2_OUTPUT').read()
# Parse uncertainty manifest for HIGH impact items
high_impact = len(re.findall(r'Impact:.*HIGH', l2_text))
confidence_matches = re.findall(r'confidence_avg:\s*([\d.]+)', l2_text)
confidence_avg = float(confidence_matches[0]) if confidence_matches else 0.0
if high_impact > 0 or confidence_avg <= 0.7:
    print('PROCEED_L3')
else:
    print('SKIP_L3')
")

if [ "$GATE_DECISION" = "PROCEED_L3" ]; then
    log "🔴 L3: Resolving uncertainties (Big Pickle, OpenCode)..."
    L3_PROMPT=$(cat <<PROMPT
[Pipeline context]
topic: ${TOPIC}
trace: ${TRACE_ID}
l1_model: ${L1_MODEL}

[L2 Synthesis — in session context]
[You have access to the full L2 conversation above]

[Instructions]
Resolve the HIGH-impact uncertainties from the Uncertainty Manifest.
Only process uncertainty items. Do NOT re-synthesize.
Format: See L3 Editor-in-Chief instructions.
PROMPT
)
    echo "$L3_PROMPT" > "/tmp/l3_prompt_${TRACE_ID}.txt"
    opencode --session "research_${TRACE_ID}" --mode researcher \
      --prompt "$(cat /tmp/l3_prompt_${TRACE_ID}.txt)" 2>&1 | tee "/tmp/l3_${TRACE_ID}.md"
    log "✅ L3 complete"
else
    log "✅ L3 skipped (no high-impact uncertainties)"
fi

# --- Phase 4: Record results ---
log "📝 Recording pipeline results..."
python3 -c "
from src.omega.observability import log_event
log_event('research_pipeline_complete', {
    'trace_id': '${TRACE_ID}',
    'topic': '${TOPIC}',
    'l1_model': '${L1_MODEL}',
    'gate_decision': '${GATE_DECISION}',
    'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
})
"

log "✅ Pipeline complete. Trace: ${TRACE_ID}"
```

### 7.3 Makefile Integration

```makefile
# In Makefile
.PHONY: research
research:
	@echo "Running Tiered Research Pipeline..."
	@bash scripts/omega-research.sh "$(TOPIC)"

.PHONY: research-l1
research-l1:
	@echo "Running L1 Intern only..."
	@L1_ONLY=true bash scripts/omega-research.sh "$(TOPIC)"
```

---

## §8 Configuration

### 8.1 Pipeline Configuration Block

```yaml
# In config/omega.yaml (pipeline section)
pipeline:
  research:
    l1:
      default_model: "qwen3-1.7b-q6_k"
      split_test_models:
        - "ministral-3.3b-q4_k_m"
        - "rocracoon-3b-q4_k_m"
      temperature: 0.4
      max_tokens: 5120
      max_tool_calls: 4
      lmster_url: "http://localhost:1234/v1/chat/completions"

    l2:
      model: "gemma-4-31b-it"
      platform: "opencode"
      session_prefix: "research_"
      temperature: 0.3
      max_tokens: 8192
      mode: "researcher"

    l3:
      model: "big-pickle"
      platform: "opencode"
      temperature: 0.2
      max_tokens: 4096
      cost_tier: "premium"

    gate:
      l2_to_l3:
        high_impact_threshold: "HIGH"
        confidence_threshold: 0.7
        max_l3_runs_per_hour: 4  # premium cost cap

    recording:
      store_raw_packets: true
      index_fts5: true
      embed_qdrant: true
      update_workbench: true
      update_soul: false  # opt-in per run
```

### 8.2 Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `L1_MODEL` | `qwen3-1.7b-q6_k` | L1 model override |
| `LMSTER_URL` | `http://localhost:1234/v1/chat/completions` | L1 inference endpoint |
| `FORCE_L3` | `false` | Skip L2→L3 gate |
| `DISABLE_L3` | `false` | Never run L3 |
| `PIPELINE_TRACE` | auto-generated | Override root trace ID |
| `OPENCODE_SESSION` | auto-generated | Override session name |

---

## §9 Comparison: Tiered Pipeline vs Jem 2.0 Pipeline

### 9.1 Architecture Comparison

| Dimension | Jem 2.0 Pipeline (OLD) | Tiered Pipeline (NEW) | Advantage |
|-----------|------------------------|----------------------|-----------|
| **L1 Model** | Gemma 4 31B (cloud) | Qwen3-1.7B (local) | NEW: Zero cost, local privacy |
| **L2 Model** | Gemma 4 31B | Gemma 4 31B | Same |
| **L3 Model** | DeepSeek V4 Flash / Big Pickle | Big Pickle only | NEW: Simplified |
| **L1 Tooling** | Full MCP fleet (6 tools) | SearXNG + local grep | NEW: Minimal, fast |
| **L2 Tooling** | Full MCP fleet | Full MCP fleet | Same |
| **Session sharing** | L2+L3 same session | L2+L3 same session | Same |
| **Quality gate** | Draft → Reviewer | L2→L3 uncertainty check | NEW: Simpler, cheaper |
| **Token cost L1** | ~20K tokens (full report) | ~5K tokens (raw packet) | NEW: ~75% reduction |
| **Token cost L2** | ~8K tokens | ~6K tokens | Minor improvement |
| **Token cost L3** | ~8K tokens (full rewrite) | ~4K tokens (uncertainties only) | NEW: ~50% reduction |
| **Total tokens** | ~36K tokens | ~17K tokens | NEW: ~53% reduction |
| **Total cost** | FREE (all Google) | FREE (local L1) | NEW: Even cheaper |
| **L1 latency** | ~30-60s (cloud API) | ~5-15s (local CPU) | NEW: 3-4x faster |
| **Split testing** | 4 variants (A-D) per run | 3 L1 models, round-robin | NEW: Targeted to weakest link |
| **Improvement briefs** | Not formalized | L2→L1, L3→L2+L1 | NEW: Feedback loops |
| **Config injection** | Not implemented | Legacy config → prompt | NEW: Pattern-based |
| **Knowledge injection** | Planned | Formal (FTS5 + Qdrant) | NEW: First-class |

### 9.2 When to Use Each Pipeline

| Scenario | Pipeline | Reason |
|----------|----------|--------|
| Quick fact-checking | Tiered (L1 only) | Fast, cheap, local |
| Standard research | Tiered (L1→L2) | ~53% token savings, L1 local |
| High-stakes research | Tiered (L1→L2→L3) | L3 premium resolution |
| Legacy mining | Tiered (L1→L2→L3) | Pattern injection + config extraction |
| Background scheduling | Tiered | Lower cost = higher frequency |

---

## §10 Implementation Roadmap

### Phase A: Pre-Pipeline Blockers (~45 min)

| # | Task | File | Dependencies |
|---|------|------|-------------|
| A1 | Reset container permissions (UID 1000 on all shared volumes) | `quadlet-test/*.container` | None |
| A2 | Restart lmster with Qwen3-1.7B autoloaded | Systemd socket activation | A1 |
| A3 | Fix C-2 soul evolution race condition | `src/omega/oracle/entity_registry.py` | None |
| A4 | Fix C-1 gnosis_proxy import order | `src/omega/oracle/gnosis_proxy.py` | None |
| A5 | Add trace chaining to observability | `src/omega/observability.py` | None |
| A6 | Add tier/mode/agent event types | `src/omega/observability.py` | A5 |

### Phase B: Pipeline Infrastructure (~1.5h)

| # | Task | File | Dependencies |
|---|------|------|-------------|
| B1 | Create `omega-research.sh` orchestrator | `scripts/omega-research.sh` | A2 (lmster) |
| B2 | Wire pipeline events to observability | `src/omega/observability.py` | A5, A6 |
| B3 | Token budget tracking (L1 cap, L3 premium cap) | `config/omega.yaml` + `scripts/omega-research.sh` | B1 |
| B4 | Verify MCP tools (SearXNG health, Exa/Tavily keys) | `make mcp-health` | None |
| B5 | Update `.clinerules` (pipeline, entity guide, keep-id) | `.clinerules` | None |
| B6 | Skills audit + create 3 new OpenCode skills | `.opencode/skills/` | None |

### Phase C: Living Knowledge Integration (~3h)

| # | Task | File | Dependencies |
|---|------|------|-------------|
| C1 | FTS5 research DB ingestion | `scripts/init-research-db.py` | None |
| C2 | Qdrant embedding pipeline | `src/omega/knowledge/embeddings.py` | C1 |
| C3 | Cross-reference linking in synthesis | L2 prompt template | B1 |
| C4 | Workbench integration (status updates) | `scripts/omega-research.sh` | B1 |
| C5 | Gnosis distillation (soul lesson generation) | L3 prompt template | B1 |
| C6 | `ResearchTierMemory` class | `src/omega/memory_store.py` | None |
| C7 | Improvement brief tracking | `data/research/improvements/` | B1 |
| C8 | Legacy config injection pipeline | L2 prompt template | Subagent mines #1-5 |

---

## §11 Known Limitations & Future Work

### 11.1 Current Limitations

1. **L1 tooling limited**: Only SearXNG + local grep. MCP tools increase latency and complexity. This is intentional — L1 must be fast and cheap.
2. **No L1 cache**: Every L1 run starts fresh. Future: cache common topics with TTL.
3. **L3 is all-or-nothing**: Either all uncertainties are resolved or none. Future: per-uncertainty L3 tasking.
4. **No streaming**: Pipeline blocks on each tier. Future: streaming L1 output to L2.
5. **L1 model swap requires lmster restart**: Future: runtime model swapping via lmster API.

### 11.2 Future Enhancements

| Enhancement | Priority | Effort | Timeline |
|-------------|----------|--------|----------|
| L1 cache with TTL | Medium | 2h | Phase D |
| Per-uncertainty L3 tasking | Low | 4h | Phase D |
| Streaming L1→L2 | Low | 6h | Phase E |
| Runtime L1 model swap | Medium | 1h | Phase D |
| L1 multi-topic parallel gathering | Medium | 3h | Phase D |
| Confidence calibration (empirical) | High | 8h | Phase D |
| L1 improvement brief auto-apply | Medium | 2h | Phase D |

---

## §12 Related Documents

| Document | Purpose |
|----------|---------|
| `JEM_SPECULATIVE_DECODING_PIPELINE.md` | Superseded Jem 2.0 pipeline spec |
| `R52b_background_orchestrator_spec.md` | Legacy background orchestrator spec |
| `WORKER_INTEGRATION_PATTERNS.md` | Omega worker integration standards |
| `R_OPENCODE_MODES_REFACTOR_STRATEGY.md` | Mode consolidation strategy |
| `OMEGA_PR_READINESS_STRATEGY.md` | Phase E strategy (this pipeline is E3) |
| `PIVOT_LOG.md` (Decision 51) | Tiered pipeline architecture decision |
| `docs/strategy/NEXT_STEPS_ROADMAP.md` | Implementation roadmap |

---

## §13 Key URLs

| Resource | URL |
|----------|-----|
| lmster API (L1) | `http://localhost:1234/v1/chat/completions` |
| SearXNG (L1 search) | `http://localhost:8017/search` |
| Gemma 4 on Google AI Studio | `https://aistudio.google.com` |
| OpenCode CLI docs | Project `.opencode/` |
| Omega Engine research index | `docs/research/INDEX.md` |

---

⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ cline ⬡ trc_pipeline_spec ⬡ PHASE-DESIGN-END
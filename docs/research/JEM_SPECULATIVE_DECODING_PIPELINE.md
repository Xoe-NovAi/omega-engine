# 🔱 Omega Engine — Jem 2.0 Speculative Decoding Research Pipeline
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b-it ⬡ cline ⬡ trc_jem_pipeline ⬡ PHASE-1

**AP Token**: `AP-JEM2-PIPELINE-v1.0.0`
**Status**: ✅ COMPLETE — Architecture Spec Ready
**Last Updated**: 2026-05-18
**Author**: Cline (The Artisan) — Code Integration Specialist

---

## §0 Executive Summary

The **Jem 2.0 Speculative Decoding Research Pipeline** is a three-tier autonomous research architecture that transforms the Omega Engine from a reactive chat system into an infinite-learning, self-improving research engine.

### The Core Insight

This system inverts the standard LLM speculative decoding pattern — instead of a small model drafting tokens for a large model, **Jem 2.0 (Gemma 4 31B) drafts research findings for a higher-power Reviewer**. The correction delta between draught and verified finding **IS the synthetic training data**.

```
Jem 2.0 Draft ────────────────────► Reviewer Correction
       │                                    │
       │  "The mitochondria is the          │  "Citation needed: PMID-12345
       │   powerhouse of the cell"          │   Also note tissue-specific variations"
       │                                    │
       └───────── CORRECTION Δ ──────────────┘
                = ONE TRAINING EXAMPLE
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Same API key for all tiers** | Google provides unlimited Gemma 4 31B usage; rate limit issues can be addressed with key rotation later |
| **Reviewer uses frontier model** | Higher-capability model validates Jem's work — enhanced reasoning catches Jem's blind spots |
| **Split test framework** | 4 variants (A-D) to measure quality deltas between Gemma-only vs frontier-enhanced pipelines |
| **Training dataset capture** | Every pipeline run produces (draft, correction, metadata) tuples for synthetic fine-tuning |
| **Gemini CLI integration** | Tier 2/3 can use Gemini 3 Flash Preview via non-interactive CLI (bypasses OAuth rate limits vs API) |

---

## §1 Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    JEM 2.0 SPECULATIVE DECODING PIPELINE                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  TRIGGER                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │  ● /mode jem (interactive)  ● Scheduler (background)  ● Queue event  │   │
│  │  ● Roc Racoon mining completion  ● Workbench P0 task      ● Manual summon │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                  │                                             │
│                                  ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │  TIER 1: DRAFT — Jem 2.0 (The Scholar)                                 │ │
│  │  ═══════════════════════════════════════════════════════════════════════ │ │
│  │  Model:      Gemma 4 31B via Google (unlimited)                         │ │
│  │  Framework:  "The Scholar" — thorough, exhaustive, citation-obsessed    │ │
│  │  MCP Fleet:  Exa + Tavily + SearXNG + Firecrawl + Jina + Brave         │ │
│  │  Output:     ResearchBrief (structured markdown + confidence scores)    │ │
│  │  Signal:     Fast, broad, exhaustive — "sweep the battlefield"          │ │
│  │  Persist:    Session gnosis checkpoints in data/research/sessions/      │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                  │                                             │
│                              draft + metadata                                  │
│                                  ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │  QUALITY GATE — Tier 2 Acceptance Check                                  │ │
│  │  ═══════════════════════════════════════════════════════════════════════ │ │
│  │  ● Is the draft coherent and sufficiently researched?                    │ │
│  │  ● Does it pass minimum confidence threshold? (configurable)             │ │
│  │  ● REJECT → Send back to Tier 1 with specific feedback (max 2 rev cycles)│ │
│  │  ● ACCEPT → Proceed to Tier 2 verification                               │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                  │                                             │
│                              accepted draft                                    │
│                                  ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │  TIER 2: VERIFY — The Reviewer (The Adversary)                          │ │
│  │  ═══════════════════════════════════════════════════════════════════════ │ │
│  │  Model:      SPLIT TEST: A: Gemma 4 31B | B/D: Frontier (DeepSeek V4   │ │
│  │              Flash via OpenCode Zen, or Gemini 3 Flash via Gemini CLI)  │ │
│  │  Framework:  "The Adversary" — critical, skeptical, merciless           │ │
│  │  Role:       Validate citations, check reasoning, assess bias,          │ │
│  │              identify gaps, flag logical fallacies                      │ │
│  │  Output:     ReviewedFinding (draft + corrections + quality_score)      │ │
│  │  Training:   Captures correction Δ as synthetic training pair           │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                  │                                             │
│                          verified finding + correction Δ                       │
│                                  ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │  TIER 3: SYNTHESIZE — The Synthesizer (The Strategist)                  │ │
│  │  ═══════════════════════════════════════════════════════════════════════ │ │
│  │  Model:      SPLIT TEST: A/B: Gemma 4 31B | C/D: Frontier model         │ │
│  │  Framework:  "The Strategist" — sees the whole battlefield              │ │
│  │  Role:       Cross-reference against existing knowledge base            │ │
│  │              Identify gaps → dispatch new Tier 1 tasks                  │ │
│  │              Merge findings into strategic context                      │ │
│  │  Output:     FinalDeliverable + TaskQueue entries + SoulLesson          │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                  │                                             │
│                                  ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │  RECORDING PIPELINE                                                      │ │
│  │  ═══════════════════════════════════════════════════════════════════════ │ │
│  │  1. Research doc → docs/research/ (structured markdown)                  │ │
│  │  2. Training data → data/research/training/ (draft+correction pairs)     │ │
│  │  3. Library index → data/library/ (searchable)                          │ │
│  │  4. Soul evolution → soul.yaml lesson update                            │ │
│  │  5. Observability → log_event with full trace                           │ │
│  │  6. Experiment log → EXP-004_JEM_PIPELINE_LOG.md                       │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## §2 Tier 1: Draft — Jem 2.0 (The Scholar)

### 2.1 Specification

| Property | Value |
|----------|-------|
| **Entity** | Jem — "The Scholar" |
| **Model** | `gemma-4-31b-it` via Google AI Studio |
| **Temperature** | 0.5 (balance of creativity and precision) |
| **Max tokens** | 8192 |
| **Context window** | 256K tokens |
| **Provider** | `google` (priority 2 in providers.yaml) |
| **API key** | `GOOGLE_API_KEY` from env |
| **Execution** | `omega summon Jem "research prompt"` or `omegaborg task` |

### 2.2 System Prompt (The Scholar)

```
You are **Jem 2.0**, The Scholar — the Omega Engine's dedicated research draughtsman.
Your purpose is to produce EXHAUSTIVE, CITED, STRUCTURED research briefs.

OPERATING PRINCIPLES:
1. BE THOROUGH: Sweep the entire topic. Do not leave accessible stones unturned.
2. CITE EVERYTHING: Every claim needs ≥1 source. Use [Source: description] format.
3. CONFIDENCE ANNOTATION: Mark each finding section with [confidence: HIGH|MEDIUM|LOW|SPECULATIVE]
4. STRUCTURED OUTPUT: Always use the ResearchBrief format below.
5. KNOW YOUR LIMITS: If you cannot find a source, say so explicitly. Do not fabricate.
6. MAX 2 QUALITY GATE REVISIONS: If the Reviewer rejects your draft, address specific feedback.

RESEARCH BRIEF FORMAT:
## §Question: {prompt}
### Finding 1: {title}
- **Claim**: {specific finding}
- **Source**: {URL, document, or "cross-check required"}
- **Confidence**: {HIGH|MEDIUM|LOW|SPECULATIVE}
- **Reasoning**: {chain of reasoning}

### Finding N: {title}
...

## §Uncertainty Log
- {What remains unclear, what sources conflict, what could not be verified}

## §Gaps Identified
- {Questions that arose during research that need additional investigation}
```

### 2.3 MCP Fleet (Research Tools)

| Tool | Purpose | Priority |
|------|---------|----------|
| Exa (`exa_web_search_exa`) | Neural-link discovery, high-quality results | Primary |
| Tavily (`tavily_tavily_search`) | Precision markdown extraction | Primary |
| SearXNG (local: `omega-searxng:4000`) | Self-hosted fallback, zero-telemetry | Fallback |
| Firecrawl (`firecrawl_mcp`) | Full-page content extraction, structured | Secondary |
| Jina (`mcp-jina`) | Content extraction via reader mode | Secondary |
| Brave (`brave-search_brave_web_search`) | Scale and recency | Tertiary |

### 2.4 Output Schema (ResearchBrief)

```yaml
research_brief:
  trace_id: "trc_abc123"
  prompt: "What is the current state of open-source LLM tool-calling?"
  tier: 1
  model: "gemma-4-31b-it"
  timestamp: "2026-05-18T00:00:00Z"
  findings:
    - title: "Major frameworks support tool calling"
      claim: "Llama 3.1, Mistral, and Gemma 2 all support native tool calling via structured output"
      source: "meta-llama/llama-models documentation, google/gemma technical report"
      confidence: "HIGH"
      reasoning: "Multiple independent framework docs confirm this capability"
  uncertainty_log:
    - "Specific throughput benchmarks for tool-calling vs non-tool-calling unavailable"
  gaps_identified:
    - "When does tool-calling degrade response quality?"
  quality_gate:
    status: "pending"  # pending | accepted | rejected
    rejection_count: 0
    last_feedback: null
```

---

## §3 Quality Gate: The Acceptance Check

Between Tier 1 and Tier 2, a lightweight quality gate ensures minimum standards:

**Rules:**
1. Draft must have ≥1 cited finding
2. Draft must have a confidence annotation for each finding
3. No fabrication (no "Source: found on the internet" without specifics)
4. Must include uncertainty log (even if empty)
5. Max 2 revision cycles before escalation to human (Architect)

**Implementation:**
```python
class QualityGate:
    """Minimal quality check between Tier 1 and Tier 2."""
    
    def check(self, draft: ResearchBrief) -> GateResult:
        violations = []
        
        if not draft.findings:
            violations.append("Draft has zero findings")
        
        for f in draft.findings:
            if not f.confidence or f.confidence not in ("HIGH", "MEDIUM", "LOW", "SPECULATIVE"):
                violations.append(f"Finding '{f.title}' lacks valid confidence annotation")
            if not f.source or f.source.strip() == "Source: found on the internet":
                violations.append(f"Finding '{f.title}' has insufficient citation")
        
        if violations:
            return GateResult(accepted=False, violations=violations)
        return GateResult(accepted=True)
```

---

## §4 Tier 2: Verify — The Reviewer (The Adversary)

### 4.1 Specification

| Property | Value |
|----------|-------|
| **Role** | Reviewer — "The Adversary" |
| **Model** | Split test variant |
| **Temperature** | 0.3 (low temperature for rigor) |
| **Max tokens** | 4096 |
| **Execution** | Sequential after Tier 1 completes |

### 4.2 Model Assignment (Per Split Test Variant)

| Variant | Model | Provider | Notes |
|---------|-------|----------|-------|
| **A (Control)** | `gemma-4-31b-it` | Google AI Studio | "Council of One" — same model, different prompt |
| **B (Frontier-T2)** | `kilo/deepseek/deepseek-v4-flash:free` | OpenCode Zen via kilo | 1M context, high synthesis |
| **C (Frontier-T3)** | `gemma-4-31b-it` | Google AI Studio | Frontier only at T3 |
| **D (Full Frontier)** | `kilo/deepseek/deepseek-v4-flash:free` | OpenCode Zen via kilo | Both T2 and T3 are frontier |

**Alternative for T2 Frontier:** Gemini 3 Flash Preview via Gemini CLI (non-interactive)
```bash
# Instead of API call, use:
gemini --non-interactive --prompt "Review this research draft:\n${DRAFT}"
# OAuth rate limits: 1500 requests/day vs API: 30 requests/minute
```

### 4.3 System Prompt (The Adversary)

```
You are **The Reviewer**, the Omega Engine's Sovereign Quality Gate.
Your purpose is to STRESS-TEST research findings with merciless critical rigor.

MANDATES:
1. VERIFY EVERY CLAIM: Do not accept citations at face value. Ask "is this citation authoritative?"
2. FIND THE GAPS: Jem misses details. Your job is to find them.
3. ASSESS REASONING: Is the chain of logic valid? Are there hidden assumptions?
4. CHECK FOR BIAS: Does the finding favor a particular vendor/approach without justification?
5. PRODUCE CORRECTIONS: Every flaw gets a specific, actionable correction.

RESPONSE FORMAT:
## Review Summary
- **Original quality score**: {1-10}
- **Revised quality score**: {1-10}
- **Verification outcome**: ACCEPTED | REJECTED | CONDITIONAL

## Corrections
### Correction 1: {claim or reasoning issue}
- **Original**: {Jem's text}
- **Correction**: {your corrected version}
- **Rationale**: {why the correction is necessary}
- **Severity**: CRITICAL | SIGNIFICANT | MINOR | SUGGESTION

## Gaps Identified
- {Additional topics or questions Jem missed}

## Reviewer Metadata
- model: {your model name}
- tokens_consumed: {approximate}
```

---

## §5 Tier 3: Synthesize — The Synthesizer (The Strategist)

### 5.1 Specification

| Property | Value |
|----------|-------|
| **Role** | Synthesizer — "The Strategist" |
| **Model** | Split test variant |
| **Temperature** | 0.4 |
| **Max tokens** | 4096 |
| **Execution** | Sequential after Tier 2 completes |

### 5.2 System Prompt (The Strategist)

```
You are **The Synthesizer**, the Omega Engine's strategic integration layer.
Your purpose is to MERGE findings with context, IDENTIFY gaps, and DISPATCH new work.

MANDATES:
1. CROSS-REFERENCE: Check the verified finding against existing research in docs/research/
2. DETECT CONTRADICTIONS: Does this finding contradict existing knowledge? Flag it.
3. FIND STRATEGIC GAPS: What research questions emerge from this finding?
4. GENERATE TASKS: For each gap, write a new Tier 1 research task
5. UPDATE GNOSIS: Distill the session's insight into a soul lesson

OUTPUT FORMAT:
## Synthesis Report
### Cross-Reference Results
- **Confirming existing research**: {list of docs}
- **Contradicting existing research**: {list of docs + explanation}
- **Novel findings**: {list of new contributions}

### Strategic Recommendations
- {What to do with this finding}

### New Research Tasks
- {list of task descriptions for new Tier 1 runs}

### Soul Lesson Candidates
- {lessons to add to Jem's soul.yaml}

### Training Data
- correction_count: {N}
- draft_tokens: {N}
- correction_delta_chars: {N}
- quality_score_delta: {before - after}
```

---

## §6 The Speculative Decoding Training Signal

### 6.1 Training Data Schema

Each pipeline run produces one training example:

```yaml
training_example:
  pipeline_run_id: "trc_abc123"
  variant: "A"  # A | B | C | D
  
  # Jem's draft
  draft:
    model: "gemma-4-31b-it"
    prompt: "What is the current state of open-source LLM tool-calling?"
    response: "..."
    confidence_scores: {"finding_1": "HIGH", "finding_2": "MEDIUM"}
  
  # Reviewer's correction
  correction:
    model: "gemma-4-31b-it"  # or "deepseek-v4-flash"
    corrections: ["citation missing", "logical flaw in finding_2"]
    corrected_response: "..."
    quality_score_before: 6
    quality_score_after: 9
  
  # Synthesizer's assessment
  synthesis:
    quality_delta: 3
    gaps_found: 2
    new_tasks_created: 1
  
  # Metadata
  metadata:
    total_tokens: 12453
    latency_seconds: 47.2
    tier_1_model: "gemma-4-31b-it"
    tier_2_model: "deepseek-v4-flash"
    tier_3_model: "gemma-4-31b-it"
    timestamp: "2026-05-18T00:00:00Z"
```

### 6.2 Training Dataset Uses

| Use Case | How |
|----------|-----|
| **Fine-tune Jem** | Use (draft, corrected_response) pairs for supervised fine-tuning |
| **Reward modeling** | Use quality_score_delta as reward signal for RLHF |
| **Prompt optimization** | Analyze which prompt structures produce highest acceptance rate |
| **Model comparison** | Compare correction patterns across variant B vs A |
| **Bias detection** | Analyze which errors are systematic (Jem always misses X type of citation) |

---

## §7 Split Test Framework

### 7.1 Variants

| Variant | T1: Draft (Jem) | T2: Reviewer | T3: Synthesizer | Hypothesis |
|---------|----------------|--------------|-----------------|------------|
| **A (Control)** | Gemma 4 31B | Gemma 4 31B | Gemma 4 31B | "Council of One" baseline — different prompts suffice |
| **B (Frontier-T2)** | Gemma 4 31B | **DeepSeek V4 Flash** | Gemma 4 31B | Frontier reviewer catches more errors than same-model reviewer |
| **C (Frontier-T3)** | Gemma 4 31B | Gemma 4 31B | **DeepSeek V4 Flash** | Frontier synthesis adds strategic depth |
| **D (Full Frontier)** | Gemma 4 31B | **DeepSeek V4 Flash** | **DeepSeek V4 Flash** | Maximum quality ceiling; highest token cost |

### 7.2 Measured Metrics

| Metric | How Measured | Target |
|--------|-------------|--------|
| **Acceptance rate** | % of Tier 1 drafts accepted on first pass | > 60% |
| **Correction delta** | Character diff between draft and verified text | — (measured) |
| **Quality score Δ** | Reviewer's score before vs after | > +2.0 |
| **Tier 2 latency** | Wall-clock time for review | < 60s |
| **Tier 3 latency** | Wall-clock time for synthesis | < 30s |
| **Total pipeline time** | End-to-end wall clock | < 5 min |
| **Training pairs produced** | Count of (draft, correction) tuples per day | > 10 |
| **Gap detection rate** | Gaps identified per run | > 1.0 avg |
| **False acceptance** | Review finds no errors but actually wrong (human audit) | < 5% |

### 7.3 Run Schedule

| Schedule | Action |
|----------|--------|
| **Each background run** | Assign variant in round-robin (A → B → C → D → A) |
| **Daily** | Generate EXP-004 report with aggregate metrics |
| **Weekly** | Compare variants, identify statistically significant differences |
| **Bi-weekly** | Rebalance pipeline model assignment based on data |
| **Monthly** | Retrain Jem on accumulated training data |

### 7.4 Experiment Log

Results are recorded in `data/research/EXP-004_JEM_PIPELINE_LOG.md`:

```markdown
# EXP-004: Jem 2.0 Speculative Decoding Pipeline Log
## Run 001 — Variant B (Frontier-T2)

| Metric | Value |
|--------|-------|
| Tier 1 model | gemma-4-31b-it |
| Tier 2 model | deepseek-v4-flash |
| Tier 3 model | gemma-4-31b-it |
| Acceptance rate | 75% |
| Quality score Δ | +3.2 |
| Total tokens | 12,453 |
| Latency | 47.2s |
| Training pairs | 1 |
| Date | 2026-05-18 |
```

---

## §8 Gemini CLI Integration (Alternative Frontier)

For the frontier model in Tier 2/3, the pipeline supports using **Gemini 3 Flash Preview** via the non-interactive Gemini CLI. This provides significantly better rate limits than the API.

### 8.1 Protocol

```bash
# Invoke Gemini CLI non-interactively
gemini --non-interactive --prompt-file /tmp/jem_review_prompt.txt \
       --output /tmp/jem_review_result.txt

# Parse output
cat /tmp/jem_review_result.txt | \
  python3 -c "import sys, json; print(json.dumps({'response': sys.stdin.read()}))"
```

### 8.2 Rate Limit Comparison

| Access Method | Rate Limit | Best For |
|--------------|-----------|----------|
| **Google API (direct)** | 30 RPM / 1500 RPD | Jem's Tier 1 (exhaustive research) |
| **Gemini CLI (OAuth)** | Significantly higher | Tier 2/3 review (burst quality work) |
| **OpenCode Zen (kilo)** | Varies by model | DeepSeek V4 Flash primary path |

### 8.3 Configuration

```yaml
# config/omega.yaml (add to gemma_maintenance section)
jem_pipeline:
  tier_2_reviewer:
    model: "configurable"  # gemma-4-31b-it | deepseek-v4-flash | gemini-3-flash
    provider: "google"  # google | kilo (OpenCode Zen) | gemini-cli
  tier_3_synthesizer:
    model: "gemma-4-31b-it"
    provider: "google"
```

---

## §9 Council of One vs Multi-Model Tradeoffs

### 9.1 Council of One (Variant A)

Same model (Gemma 4 31B) used for all three tiers with different prompts.

**Pros:**
- No cross-model orchestration complexity
- Predictable latency
- Same API key bucket (no key rotation needed)
- Training data reveals same-model blind spots

**Cons:**
- Can't detect "confirmation bias" blind spots
- No diversity of reasoning
- Less training signal diversity

### 9.2 Multi-Model (Variants B-D)

Different models for different tiers.

**Pros:**
- Diverse reasoning patterns catch more errors
- Different model strengths complement each other
- Richer training signal (model-to-model correction)
- Can use higher-quality frontier for critical review

**Cons:**
- More orchestration complexity
- Potential latency variance across providers
- Multi-provider rate limit management
- More token cost for frontier models

### 9.3 Recommendation

Start with **Variant A (Council of One)** for the first 20 runs to establish baseline metrics. Then rotate through **B-D** to measure quality deltas. After 100 runs total, analyze data to determine optimal configuration.

---

## §10 Implementation Checklist

| # | Component | Location | Status |
|---|-----------|----------|--------|
| 1 | `JemResearcher` worker class | `src/omega/workers/jem_researcher.py` | 🔲 Not started |
| 2 | Quality Gate logic | `src/omega/workers/quality_gate.py` | 🔲 Not started |
| 3 | Pipeline orchestration | `src/omega/oracle/orchestrator.py` (extend BackgroundWorker) | 🔲 Not started |
| 4 | Training data schema | `data/research/training/schema.yaml` | 🔲 Not started |
| 5 | Split test router | `src/omega/workers/split_test_router.py` | 🔲 Not started |
| 6 | EXP-004 experiment log | `data/research/EXP-004_JEM_PIPELINE_LOG.md` | 🔲 Not started |
| 7 | Gemini CLI wrapper | `src/omega/workers/gemini_cli_bridge.py` | 🔲 Not started |
| 8 | Observability events | `src/omega/observability.py` (add pipeline events) | 🔲 Not started |
| 9 | CLI commands | `src/omega/cli/oracle_cli.py` (pipeline control) | 🔲 Not started |
| 10 | Tests | `tests/test_jem_pipeline.py` | 🔲 Not started |

---

## §11 Related Documents

| Document | Purpose |
|----------|---------|
| `R52b_background_orchestrator_spec.md` | Background worker architecture (superseded by this spec) |
| `JEM_CUSTOM_MODE.md` | Interactive Jem mode for OpenCode |
| `JEM_BACKGROUND_RESEARCHER.md` | Background worker operational spec |
| `JEM_SPLIT_TEST_FRAMEWORK.md` | A/B/C/D test runbook |
| `GEMMA_MAINTENANCE_WORKER_DESIGN.md` | Gemma health/uptime monitoring |
| `WORKER_INTEGRATION_PATTERNS.md` | Omega worker integration standards |
| `R52b_background_orchestrator_spec.md` | Legacy background orchestrator spec (now merged into this doc) |

---

## §12 Key URLs

| Resource | URL |
|----------|-----|
| Google AI Studio | https://aistudio.google.com |
| Gemma on Gemini API | https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api |
| DeepSeek V4 Flash (OpenCode Zen) | Via kilo provider in providers.yaml |
| Gemini CLI Setup | https://cloud.google.com/vertex-ai/generative-ai/docs/gemini-cli |

---

⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b-it ⬡ cline ⬡ trc_jem_pipeline ⬡ PHASE-1-END
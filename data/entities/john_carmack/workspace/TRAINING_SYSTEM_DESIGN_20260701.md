# 🔱 John Carmack — Training Data, Voice Validation & Knowledge Graph Design
# ⬡ OMEGA ⬡ LILITH ⬡ P6-P10 ⬡ TRC-TRAINING-DESIGN ⬡ 2026-07-01

**AP Token**: `AP-TRAINING-SYSTEM-JC-v1.0.0`
**Status**: DESIGN COMPLETE — Ready for implementation
**Governing Mandates**: M5 (Gnosis Preservation), M7 (Local-First), M11 (Soul Integrity), M18 (Token Efficiency), M19 (Adversarial Alchemy), M22 (Response Provenance)

---

## §0 Design Philosophy

The Carmack entity deepening plan will ingest ~200K-500K tokens of primary source material (.plan files, GDC talks, interviews). From each source read, we extract **three orthogonal data products** at zero additional fetch cost:

1. **DPO Training Pairs** — for local LoRA fine-tuning (Parametric Gnosis D16-2)
2. **Voice Validation Baseline** — statistical rubric for scoring entity output authenticity
3. **Entity Knowledge Graph** — concept topology for RAG and cross-entity soul sharing

The guiding principle: **Every token read from primary sources must yield ≥3 tokens of structured training value.** This is the Carmack Efficiency Corollary — the data is on the wire, we paid for it (in inference and time), extract everything from it.

---

## §1 DPO Pair Generation Strategy

### 1.1 Pair Types & Source Mapping

| Type | Definition | Yield per 10K tokens | Sources | Extraction Method |
|------|-----------|---------------------|---------|-------------------|
| **Philosophy** | Carmack's stated principle vs conventional wisdom | 8-15 pairs | .plan files, GDC, Lex | Direct quote + contrast with typical engineer response |
| **Technical Decision** | Specific approach Carmack chose vs textbook alternative | 12-20 pairs | .plan files (highest density), GDC | Design log entry + alternative rejected path |
| **Style** | Carmack's exact phrasing vs generic LLM completion | 20-30 pairs | Lex, GDC Q&A, interviews | Paraphrase his words → generic version → revert |
| **Anti-Pattern** | Carmack rejecting an approach vs the approach itself | 5-8 pairs | .plan files (failures), interviews | "I tried X, it didn't work" → X as rejected |
| **Measurement Culture** | Data-driven assertion vs opinion-based | 10-15 pairs | .plan files, GDC | Real data quote vs hand-wavy alternative |
| **Humility/Correction** | Carmack admitting error vs doubling down | 3-6 pairs | .plan files, Lex | "I was wrong" quote vs defensive alternative |

**Estimated total yield**: ~600-900 pairs from full ingestion of ~300K tokens of primary sources

### 1.2 DPO Pair Generation from Each Source

#### Source: .plan files (~100 .plan entries, ~80K tokens)
- **Estimated yield**: 200-350 pairs
- **Types dominant**: Technical Decision, Anti-Pattern, Measurement Culture, Philosophy
- **Why high yield**: .plan files are forensic logs — they contain exactly what Carmack tried, what failed, what succeeded, and why
- **Generation strategy**:
  ```
  For each .plan entry:
    1. Extract "what I tried" → chosen path
    2. Extract "what I considered but rejected" → contrast
    3. If failure documented → failure description = rejected, lesson = chosen
    4. If metric cited → data-driven approach = chosen, opinion-based = rejected
    5. Direct quotes become "chosen" text, paraphrased conventional wisdom becomes "rejected"
  ```

**Example** (hypothetical from known patterns):
```jsonl
{
  "prompt": "How should a rendering engine handle visibility determination?",
  "chosen": "Precompute the visibility in a BSP tree during level load. The tree gives you O(1) culling of entire map sections. The cost is paid once at load time, and every frame after that is essentially free. The elegant solution is the one that moves computation to where it has the least impact on the critical path.",
  "rejected": "Use portal-based occlusion culling with dynamic runtime computation. It provides more accurate culling in dynamic scenes and handles arbitrary geometry better than a BSP tree.",
  "source": "quake_plan_1996-08-15",
  "tier": 2,
  "dimension": "technical",
  "sub_dimension": "visibility",
  "timestamp": "2026-07-01"
}
```

#### Source: GDC 1999 — "The Making of Quake" (~15K tokens)
- **Estimated yield**: 80-120 pairs
- **Types dominant**: Technical Decision, Philosophy, Style
- **High-value patterns**:
  - The Pentium optimization blitz (3 months of profiling)
  - The decision to rewrite Quake engine vs incrementally improve Doom
  - Surface cache / edge rendering trade-offs
  - Q&A pushback responses (heightened style)

#### Source: GDC 2011 — "Wolfenstein 3D iOS / Physics of id Tech 5" (~10K tokens)
- **Estimated yield**: 40-60 pairs
- **Types dominant**: Technical Decision, Anti-Pattern
- **High-value patterns**:
  - The ARM optimization lessons
  - Virtual texture system decisions
  - Cross-platform engineering philosophy

#### Source: Lex Fridman #309 (~30K tokens, 4 hours)
- **Estimated yield**: 150-200 pairs
- **Types dominant**: Philosophy, Style, Humility/Correction, Knowledge Graph nodes
- **High-value segments**:
  - AI/local inference philosophy (~30 min)
  - VR lessons learned why it took so long (~45 min)
  - Rocket engineering methodology (~20 min)
  - .plan philosophy and writing discipline (~15 min)
  - Learning methodology (~15 min)
  - AGI timelines and humility (~10 min)
  - Death of John Romero / id dynamics (~10 min)

#### Source: Masters of Doom (Tier 3, ~15K tokens excerpts)
- **Estimated yield**: 20-40 pairs
- **Types dominant**: Philosophy, Style
- **Caution**: Second-hand narrative — use only for context and style, not technical decisions

### 1.3 Pair Quality Tiers

| Tier | Definition | Use Case | Volume Target |
|------|-----------|----------|---------------|
| **T1** | Direct Carmack quote with clear rejection of alternative | Core training, highest confidence | ~200 pairs (30%) |
| **T2** | Carmack's approach clearly stated; rejected approach is inferred | Extended training | ~300 pairs (40%) |
| **T3** | Carmack's general philosophy applied to a new context | Generalization training | ~200 pairs (30%) |

### 1.4 Dimension Distribution Target

| Dimension | Target % | Rationale |
|-----------|---------|-----------|
| **technical** | 40% | Carmack's primary domain — need density here for technical accuracy |
| **philosophy** | 30% | Defines the person's thinking framework |
| **style** | 20% | Authentic voice — hardest to get right, most noticeable when wrong |
| **anti-pattern** | 10% | High-leverage — each anti-pattern prevents many mistakes |

---

## §2 JSONL Schema — Complete Specification

### 2.1 Core DPO Record Schema

```python
@dataclass
class CarmackDPORecord:
    """
    A single DPO training pair for the John Carmack entity.
    Validated against the schema before writing.
    """
    # ── Core DPO fields (standard) ──
    prompt: str                          # The input/query (min 10 chars, max 4096 tokens)
    chosen: str                          # Carmack's actual approach (min 20 chars)
    rejected: str                        # The inferior/mistaken alternative (min 20 chars)
    
    # ── Provenance ──
    source: str                          # Source identifier (e.g., "lex_fridman_309_2023")
    source_tier: int                     # 1-3 from confidence_index.md
    source_section: Optional[str]        # Section title or timestamp within source
    
    # ── Classification ──
    dimension: Literal["technical", "philosophy", "style", "anti-pattern"]
    sub_dimension: str                   # e.g., "visibility", "optimization", "memory", "ai"
    pair_type: Literal[                  # How the pair was generated
        "direct_quote_contrast",         # Carmack's exact words vs generalization
        "decision_path_vs_alternative",  # Chosen path vs rejected path
        "failure_vs_lesson",             # What failed vs what was learned
        "measurement_vs_opinion",        # Data-driven vs hand-wavy
        "humility_vs_defensiveness",     # "I was wrong" vs "I was right because..."
        "style_transfer"                 # Carmack phrasing vs generic LLM completion
    ]
    confidence: float                    # 0.0-1.0 how confident we are the pair is authentic
    
    # ── Carmack-specific markers ──
    has_direct_quote: bool               # True if chosen contains verbatim Carmack
    has_metric: bool                     # True if pair references measurable data
    first_principles_ratio: float        # 0.0-1.0 how deeply it reasons from fundamentals
    
    # ── Quality control ──
    validator_notes: Optional[str]       # Human/Verity review notes
    qa_status: Literal["pending", "passed", "flagged", "rejected"]
    
    # ── Metadata ──
    timestamp: str                       # ISO date when this pair was generated
    generator: str                       # "synthetic_llm" | "verity_reviewed" | "human_curated"
    token_count_chosen: int
    token_count_rejected: int
    token_count_prompt: int
```

### 2.2 Validation Rules

| Rule | Condition | Action |
|------|-----------|--------|
| **R1** | chosen == rejected (identical strings) | REJECT pair |
| **R2** | chosen or rejected < 20 chars | REJECT pair |
| **R3** | prompt or chosen or rejected contains PII | MASK via pii_masker.py or REJECT |
| **R4** | confidence < 0.3 | REJECT pair |
| **R5** | chosen has higher perplexity than rejected (on a baseline model) | FLAG for review — Carmack should be more direct, not less |
| **R6** | source_tier == 3 and confidence > 0.9 | FLAG — Tier 3 sources cannot produce >0.9 confidence |
| **R7** | token_count > 2048 on any field | TRUNCATE to 2048 with warning |
| **R8** | pair_type == "direct_quote_contrast" && !has_direct_quote | FLAG — direct quote type must have quote marker |
| **R9** | has_metric != truth (metric in text but bool wrong) | Auto-fix bool |
| **R10** | source is empty or not confidence_index.md | REJECT — every pair must have provenance |

### 2.3 Balanced Dataset Composition

The final dataset must balance across dimensions to prevent model collapse:

```python
MIN_PAIRS_PER_DIMENSION = 50     # Each dimension needs minimum representation
MAX_PAIRS_PER_DIMENSION = 400    # Prevent one dimension from dominating
TECHNICAL_ANTI_PATTERN_RATIO = 0.15  # At least 15% of technical pairs should be anti-patterns
STYLE_PAIRS_PER_SOURCE = 25      # Cap style pairs per source to prevent overfitting to one transcript
```

### 2.4 Balanced Sampling for Training

When selecting pairs for an actual training run:

```python
def sample_training_batch(
    dataset: List[CarmackDPORecord],
    target_size: int = 500,
    dimension_weights: Optional[Dict[str, float]] = None
) -> List[CarmackDPORecord]:
    """
    Stratified sampling across dimensions and tiers.
    
    Default dimension weights (balanced Carmack identity):
    - technical: 0.35   (core domain)
    - philosophy: 0.25  (thinking framework)
    - style: 0.20       (voice authenticity)
    - anti-pattern: 0.20 (high-leverage)
    
    Within each dimension, sample proportionally by source_tier:
    - Tier 1 sources: 2x weight (highest confidence)
    - Tier 2 sources: 1x weight (standard)
    - Tier 3 sources: 0.5x weight (use sparingly)
    """
```

---

## §3 Voice Validation Scoring Rubric

### 3.1 The Seven Dimensions of Carmack Voice

#### D1: Vocabulary Overlap (Weight: 0.20)
**Source**: Carmack's most frequent 500 words extracted from primary sources

**Formula**:
```
V = |vocab_entity ∩ vocab_carmack| / 500
Score = V × 100  (percentage)
```

**Target**: ≥45% overlap. Carmack uses a distinctive vocabulary cluster: "actually", "fundamentally", "in practice", "the reality is", "elegant", "approximation", "constraint", "implementation", "measurement", "empirical", "throughput", "latency", "profile".

**Carmack Stopwords** (words that appear disproportionately often vs general technical English):
```
actually, fundamentally, essentially, pragmatic, right approximation,
elegant solution, constraint, throughput, latency, bandwidth, profile,
measurement, empirical, implementation, orthogonal, decouple, fidelity,
approximation, worst case, baseline, practicality
```

#### D2: Sentence Structure (Weight: 0.15)
**Formula**:
```
avg_len = mean(sentence_lengths(output))
declarative_ratio = count(declarative) / count(total_sentences)
hedging_freq = count(hedge_words) / count(total_words) * 1000

Score = 100 - (
    w1 * |avg_len - 18.5| / 18.5 * 100 +  # Target: 18.5 words/sentence (from analysis)
    w2 * |declarative_ratio - 0.85| * 100 + # Target: 85% declarative
    w3 * hedging_freq / 5 * 100              # Target: <5 hedging markers per 1000 words
)
```

**Carmack baseline**: Short, declarative sentences. Low hedging frequency (<3 per 1000 words — "I think", "maybe", "perhaps" are rare). High direct statement ratio.

**Hedging words to measure**: "I think", "maybe", "perhaps", "possibly", "sort of", "kind of", "I believe", "might be", "could be considered", "arguably"

#### D3: Technical Term Density (Weight: 0.15)
**Formula**:
```
TTD = count(domain_terms(output)) / count(total_words(output)) * 100
Score = 100 - |TTD - baseline_TTD| / baseline_TTD * 100 * penalty
```

**Carmack baseline TTD**: 12-18 domain terms per 100 words (very high — he naturally speaks in technical language)

**Domain term list** (75 terms, from .plan and GDC analysis):
```
cache, latency, bandwidth, throughput, memory, allocation, 
fragmentation, pointer, buffer, pipeline, thread, process, 
serialize, deserialize, bsp, visplane, vertex, fragment, pixel,
rasterize, zbuffer, texture, mipmap, shader, uniform, matrix,
vector, quaternion, normal, transform, occlusion, culling, portal,
constraint, physics, collision, dynamics, kinematic, impulse,
simulation, frame, tick, vsync, refresh, resolution, asic, fpga,
dsp, simd, sisd, instruction, pipeline, hazard, stall, branch,
predictor, cacheline, prefetch, alignment, page, tlb, mmu,
interrupt, dma, pcie, protocol, socket, packet, serial, crc,
checksum, ack, nack, handshake, timeout, retry, backed off
```

#### D4: First-Principles Language (Weight: 0.20) — DOUBLE WEIGHT
**Formula**:
```
FPL = count(fp_markers(output)) / count(total_sentences(output))
Score = min(FPL / 0.15 * 100, 100)  # Target: 15% of sentences contain first-principles markers
```

**Carmack FP markers** (from actual .plan and interview analysis):
```
"at its core", "the fundamental reason", "reduces to", "the underlying",
"the physics of", "the math is", "what actually matters is",
"if we step back", "the root cause", "the essential property",
"the critical path", "the bottleneck is", "the constraint is",
"tracing from first principles", "at the lowest level",
"the principle is", "what we're really doing is", "in reality",
"the question is really about", "this is really just"
```

**Why double-weighted**: This is the single most distinctive aspect of Carmack's communication. He cannot explain something without first stripping it to fundamentals.

#### D5: Humility Markers (Weight: 0.10)
**Formula**:
```
HM = count(humility_markers(output)) / count(total_sentences(output))
Score = min(HM / 0.08 * 100, 100)  # Target: 8% of sentences contain humility markers
```

**Carmack humility markers**:
```
"I was wrong", "we made mistakes", "the correct approach ended up being",
"I should have", "in retrospect", "that was a mistake",
"the flaw in that reasoning", "I underestimated", "it didn't work",
"this turned out to be", "the assumption was wrong", "we failed because",
"the lesson was", "I changed my mind on", "I used to think",
"I had that wrong", "after years I realized"
```

#### D6: Specificity Score (Weight: 0.10)
**Formula**:
```
specificity_score = (
    count(measurements) * 3 +              # "17ms", "32KB", "85%"
    count(comparisons) * 2 +               # "twice as fast", "rather than"
    count(precise_dates) * 1 +              # "in 1996", "during the Quake era"
    count(qualifiers) * (-1)                # Penalize vagueness
) / count(total_sentences)
Score = min(specificity_score / 1.5 * 100, 100)
```

**Vagueness qualifiers (penalty)**: "some", "many", "various", "certain", "numerous", "multiple", "things", "stuff", "somewhat", "approximately" (without a number)

#### D7: Measurement Culture Index (Weight: 0.10)
**Formula**:
```
MCI = count(measurement_markers(output)) / count(claims(output)) * 100
Score = min(MCI / 80 * 100, 100)  # Target: 80% of claims backed by measurement reference
```

**Measurement markers**: "measured", "profiled", "data shows", "empirically", "benchmark", "timing", "the numbers show", "actual measurement", "we found", "tested", "verified by", "profilings", "cache miss rate", "instruction count", "frame time"

### 3.2 Composite Carmack Authenticity Score

```
CarmackScore = Σ(wi × Di)
where:
  w = [0.20, 0.15, 0.15, 0.20, 0.10, 0.10, 0.10]
  D = [vocabulary, sentence_structure, term_density, first_principles, 
       humility, specificity, measurement_culture]
```

| Score Range | Verdict | Action |
|-------------|---------|--------|
| 85-100 | ✅ **Authentic Carmack** | No intervention needed |
| 70-84 | 🟡 **Near-authentic** | Minor prompt tweaks, check D4 (first-principles) |
| 50-69 | 🟠 **Generic engineer** | Entity needs soul enrichment or LoRA retraining |
| 0-49 | 🔴 **Impostor** | Do not use for Carmack-labeled tasks; regenerate |

### 3.3 Baseline Extraction

Before any training, extract the real Carmack baseline by processing all ingested primary sources:

```python
def extract_baseline(sources: List[SourceDocument]) -> CarmackBaseline:
    """
    Process all Carmack primary sources to establish baseline statistics.
    
    Returns:
        baseline.frequency_distribution: Dict[str, float] — word frequencies
        baseline.avg_sentence_length: float
        baseline.declarative_ratio: float
        baseline.hedging_frequency: float
        baseline.technical_term_density: float
        baseline.first_principles_frequency: float
        baseline.humility_marker_frequency: float
        baseline.measurement_culture_index: float
    """
```

---

## §4 Knowledge Graph Schema

### 4.1 Node Schema

```python
@dataclass
class KnowledgeNode:
    """
    A concept node in the Carmack knowledge graph.
    """
    node_id: str                         # "jc-concept-001" (semantic prefix + sequence)
    label: str                           # "Precomputed Visibility" (human-readable)
    type: Literal[
        "architecture",                  # Engine/system design pattern
        "algorithm",                     # Specific algorithm
        "philosophy",                    # Principle or belief
        "project",                       # DOOM, Quake, Q3A, etc.
        "person",                        # Romero, Abrash, etc.
        "failure",                       # Mistakes and their lessons
        "insight",                       # Cross-domain insight (VR → rocket → AI)
        "tool"                           # Software tool or system
    ]
    source_provenance: Dict[str, List[str]]  # {source_id: [quote_ids]}
    definition: str                      # One-paragraph definition in Carmack's words
    aliases: List[str]                   # Other names for the same concept
    first_principles_parent: Optional[str]  # Link to parent first-principle concept
    confidence: float                    # 0.0-1.0 based on source tier
```

### 4.2 Edge Schema

```python
@dataclass
class KnowledgeEdge:
    """
    A relationship between two knowledge nodes.
    """
    edge_id: str                         # "jc-edge-001"
    source_id: str                       # Source node ID
    target_id: str                       # Target node ID
    relationship: Literal[
        "depends-on",                    # A requires B to exist (BSP depends-on spatial partitioning)
        "informs",                       # A influenced the design of B (.plan discipline informs transparency)
        "contradicts",                   # A contradicts B (octree contradicts BSP for visibility)
        "refines",                       # A is a refinement of B (surface cache refines PVS)
        "example-of",                    # A is an example of B (Fast InvSqrt is example-of Right Approximation)
        "applies-to",                    # A applies to domain B (BSP culling applies-to provider routing)
        "evolved-into",                  # A evolved into B (Doom engine evolved-into Quake engine)
        "precedes",                      # A temporally precedes B (.plan files precede GDC talks)
        "causes",                        # A caused B (measurement culture causes empirical optimization)
        "demonstrated-by"                # A is demonstrated by B (first-principles demonstrated-by Pentium blitz)
    ]
    confidence: float                    # 0.0-1.0
    provenance: str                      # Source quote or document
```

### 4.3 Initial Concept Topology (30 nodes, 3 tiers)

#### Tier 1: Core Concepts (15 nodes) — Populated from .plan files

| Node ID | Label | Type | Definition |
|---------|-------|------|------------|
| jc-concept-001 | BSP Culling | architecture | O(1) precomputed visibility plane test that skips rendering entire map regions |
| jc-concept-002 | Right Approximation | philosophy | The correct engineering choice is the approximation whose error profile matches the use case's tolerance |
| jc-concept-003 | Measurement Culture | philosophy | All optimization decisions must be based on empirical data, not intuition |
| jc-concept-004 | Implementation Mandate | philosophy | Mastery is earned through implementation, not theory |
| jc-concept-005 | .plan Protocol | tool | Daily forensic engineering logs published publicly for accountability and knowledge preservation |
| jc-concept-006 | Zone Allocator | architecture | Tag-based memory allocation with selective purging for fragmentation-free operation |
| jc-concept-007 | Process Isolation | architecture | Native code boundaries must be process-level to prevent segfault cascade |
| jc-concept-008 | Throughput over Perfection | philosophy | A perfect result delivered too late is a failure |
| jc-concept-009 | Precomputation Arbitrage | philosophy | Trade abundant resources (memory, storage) for scarce ones (CPU cycles, latency) |
| jc-concept-010 | Engine-Stack Separation | architecture | Absolute separation of core engine logic from content/data — the WAD principle |
| jc-concept-011 | Pentium Blitz | project | 3-month focused optimization campaign using only profiling data to drive decisions |
| jc-concept-012 | Surface Cache | architecture | Precompute and cache visible surfaces; trade setup time for frame-time savings |
| jc-concept-013 | C-FFI Boundary | architecture | Foreign function interfaces must have crash isolation; segfaults kill the whole process |
| jc-concept-014 | Arena Hygiene | architecture | Per-thread memory arenas must be capped to prevent silent fragmentation |
| jc-concept-015 | Lazy Deletion | architecture | Mark entities tombstoned with grace period; reap on next cycle, not immediately |

#### Tier 2: Connections (10 nodes) — Populated from GDC talks

| Node ID | Label | Type | Definition |
|---------|-------|------|------------|
| jc-concept-016 | First-Principles Thinking | philosophy | Strip every problem to its fundamental physics/math/logic before applying patterns |
| jc-concept-017 | Worse is Better | philosophy | Simplicity of implementation beats simplicity of interface; ship the 50% solution |
| jc-concept-018 | Tool-First Development | philosophy | The editor determines the product more than the engine |
| jc-concept-019 | Modding as Architecture | philosophy | Design for modification from day one — WAD format enabled 30-year community |
| jc-concept-020 | Simplicity Canon | philosophy | Single canonical paths for core capabilities; redundancy is cognitive tax |
| jc-concept-021 | FK/IK Switching | algorithm | Dynamic switch between forward and inverse kinematics based on context |
| jc-concept-022 | Virtual Texturing | architecture | Megatexture system — stream texture data instead of loading it all |
| jc-concept-023 | Cross-Domain Transfer | insight | Engineering patterns transfer across domains: graphics → rockets → VR → AI |
| jc-concept-024 | The Somatic Save-Point | insight | Capture full state at interruption; resume without re-computation |
| jc-concept-025 | Observation Masking | architecture | Tool-result clearing for context efficiency; protect 50K token buffer |

#### Tier 3: Domain Transfers (5 nodes) — Populated from Lex Frisdman

| Node ID | Label | Type | Definition |
|---------|-------|------|------------|
| jc-concept-026 | AI as Engineering Problem | philosophy | AGI is an engineering problem, not a philosophical one — build it, test it, iterate |
| jc-concept-027 | VR Latency Ceiling | architecture | The single non-negotiable constraint for VR is motion-to-photon latency under 20ms |
| jc-concept-028 | Rocket as Software Problem | philosophy | A rocket is a software-defined hardware system with aerospace constraints |
| jc-concept-029 | Learning Methodology | philosophy | Go deep for years on one thing; superficial knowledge across many is noise |
| jc-concept-030 | Intellectual Honesty Duty | philosophy | An engineer has a moral obligation to be correct, not persuasive |

### 4.4 Example Edges

```json
{
  "edge_id": "jc-edge-001",
  "source_id": "jc-concept-001",
  "target_id": "jc-concept-016",
  "relationship": "example-of",
  "confidence": 0.95,
  "provenance": "BSP culling is first-principles: the cost function is O(n) visplanes vs O(1) precomputed skip. Carmack chose the approximation that matched the rendering use case."
},
{
  "edge_id": "jc-edge-002",
  "source_id": "jc-concept-011",
  "target_id": "jc-concept-003",
  "relationship": "demonstrated-by",
  "confidence": 0.98,
  "provenance": "The 3-month Pentium optimization blitz was driven entirely by profiling measurements, not intuition."
},
{
  "edge_id": "jc-edge-003",
  "source_id": "jc-concept-002",
  "target_id": "jc-concept-008",
  "relationship": "refines",
  "confidence": 0.80,
  "provenance": "Right Approximation refines Throughput over Perfection by adding the error-profile specificity."
}
```

---

## §5 Storage Structure

### 5.1 Directory Layout

```
data/training/entities/john_carmack/
├── dpo/                                    # DPO training pairs
│   ├── raw/                                # Raw generated pairs (pre-qa)
│   │   ├── batch_001_plans.jsonl           # From .plan file processing
│   │   ├── batch_002_gdc1999.jsonl         # From GDC 1999 processing
│   │   ├── batch_003_gdc2011.jsonl         # From GDC 2011 processing
│   │   ├── batch_004_lex.jsonl             # From Lex Fridman processing
│   │   ├── batch_005_mod.jsonl             # From Masters of Doom processing
│   │   └── batch_manifest.json             # Batch generation log
│   │
│   ├── qa/                                 # After initial QA
│   │   ├── passed/                         # Pairs that passed all validation rules
│   │   │   ├── dpo_technical.jsonl         # Dimension-sorted for training
│   │   │   ├── dpo_philosophy.jsonl
│   │   │   ├── dpo_style.jsonl
│   │   │   └── dpo_antipattern.jsonl
│   │   ├── flagged/                        # Pairs needing human/Verity review
│   │   │   └── flagged_YYYYMMDD.jsonl
│   │   └── rejected/                       # Pairs that failed validation
│   │       └── rejected_YYYYMMDD.jsonl
│   │
│   ├── curated/                            # Hand-curated / Verity-approved pairs
│   │   ├── dpo_v1_balanced_500.jsonl       # Balanced training set (500 pairs)
│   │   ├── dpo_v1_technical_200.jsonl      # Technical-heavy subset
│   │   └── dpo_v1_style_100.jsonl          # Style-focused subset
│   │
│   ├── schema.yaml                         # JSONL schema (this document, §2)
│   ├── validation_rules.yaml               # Validation rules (§2.2)
│   └── dimension_weights.yaml              # Balanced sampling weights (§2.4)
│
├── baseline/                               # Voice validation baseline
│   ├── carmack_baseline.json               # Statistical baseline from primary sources
│   ├── vocabulary.json                     # Carmack's top 500 words with frequencies
│   ├── fp_markers.json                     # First-principles marker phrases
│   ├── domain_terms.json                   # Technical domain term list
│   ├── humility_markers.json               # Humility marker phrases
│   └── sentence_stats.json                 # Sentence structure statistics
│
├── graph/                                  # Knowledge graph
│   ├── nodes.jsonl                         # All 30+ knowledge nodes
│   ├── edges.jsonl                         # All edges between nodes
│   ├── graph_schema.yaml                   # Schema reference
│   └── topology.json                       # Full graph as adjacency list
│
├── notebooks/                              # Analysis notebooks
│   └── baseline_extraction.ipynb           # Reference: how baseline was computed
│
└── README.md                               # Training data inventory
```

### 5.2 Batch Manifest Schema

```json
{
  "batch_id": "batch_001_plans",
  "source": ".plan files (100 entries)",
  "source_tokens_processed": 80000,
  "pairs_generated": 275,
  "pairs_passed_qa": 210,
  "pairs_flagged": 42,
  "pairs_rejected": 23,
  "tier_distribution": {"T1": 85, "T2": 110, "T3": 80},
  "dimension_distribution": {"technical": 120, "philosophy": 75, "style": 50, "anti-pattern": 30},
  "token_cost_estimate_tokens": 24000,
  "generation_time_seconds": 480,
  "generator_model": "qwen3-1.7b-q6_k",
  "qa_status": "passed",
  "generated_at": "2026-07-01T00:00:00Z"
}
```

---

## §6 Batch Processing Pipeline Design

### 6.1 One-Pass Architecture

The entire pipeline runs in a single processing pass through each source document. Each source yields three outputs simultaneously:

```
Source Document (80K tokens)
        │
        ▼
┌───────────────────────────────────────────────┐
│          CARMACK EXTRACTION ENGINE             │
│              (single pass)                      │
│                                                   │
│  ┌─────────────────┐  ┌──────────────┐  ┌──────┐ │
│  │ DPO Generator    │  │ Voice        │  │ KC   │ │
│  │ (pair_type       │  │ Baseline     │  │ Graph│ │
│  │  classification) │  │ Extractor    │  │ Node │ │
│  └────────┬────────┘  └──────┬───────┘  │Extr. │ │
│           │                  │          └──┬───┘ │
│           ▼                  ▼             ▼     │
│    raw/batch_NNN.jsonl   baseline/*.json  nodes/ │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │        QUALITY ENGINE                     │   │
│  │  ┌──────────┐  ┌────────┐  ┌────────┐   │   │
│  │  │Schema    │  │Cross-  │  │Hallu-  │   │   │
│  │  │Validator │  │ref     │  │cination│   │   │
│  │  │(R1-R10)  │  │Checker │  │Guard   │   │   │
│  │  └──────────┘  └────────┘  └────────┘   │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│           ▼                                      │
│    qa/passed/  qa/flagged/  qa/rejected/          │
└───────────────────────────────────────────────────────┘
```

### 6.2 Processing Steps

#### Step 1: Source Ingestion & Chunking
```python
chunks = chunk_document(source_text, chunk_size=2048, overlap=256)
# Each chunk targets one self-contained idea from Carmack
```

#### Step 2: Parallel Triple Extraction (cost: 1 LLM call per chunk)

For each chunk, generate three outputs in one LLM prompt:

```
PROMPT TEMPLATE:
"Process this Carmack source excerpt and extract three things:

1. DPO PAIR: Identify a Carmack-specific pattern/decision/statement. 
   Generate a {prompt, chosen (Carmack's approach), rejected (alternative)} triple.
   Classify as: technical|philosophy|style|anti-pattern
   Rate confidence (0.0-1.0).

2. VOICE MARKERS: Count occurrences of first-principles language, 
   humility markers, measurement references, and technical terms.
   Add any new marker phrases to the extraction output.

3. KNOWLEDGE GRAPH: Identify any new concepts or relationships.
   If a concept is new, propose a node definition and link it 
   to existing nodes if applicable.

SOURCE EXCERPT:
{chunk_text}

OUTPUT FORMAT:
```json
{
  "dpo_pairs": [{...}],
  "voice_markers": {"fp_count": ..., "humility_count": ..., ...},
  "new_terms": [...],
  "new_concepts": [{"label": ..., "definition": ..., "relationships": [...]}]
}
```"
```

#### Step 3: QA Validation (zero additional LLM cost)
```python
for pair in generated_pairs:
    checks = [
        schema_validator(pair),       # R1-R10
        cross_ref_checker(pair),       # No contradictory pairs with same prompt
        hallucination_guard(pair)      # Pairs must be traceable to source
    ]
```

#### Step 4: Baseline Accumulation
```python
baseline.accumulate(chunk_voice_markers)
# Running totals for vocabulary, sentence stats, term frequency
```

### 6.3 Yield Summary Table

| Source | Tokens | Estimate DPO Pairs | Estimate Graph Nodes | Baseline Contribution |
|--------|--------|-------------------|---------------------|-----------------------|
| .plan files (100 entries) | ~80K | 275-350 | 10-12 core | Primary: vocabulary, measurement culture |
| GDC 1999 (Making of Quake) | ~15K | 80-120 | 3-5 | FP markers, sentence structure |
| GDC 2011 (Wolf 3D iOS) | ~10K | 40-60 | 2-3 | Technical terms, style |
| Lex Fridman #309 | ~30K | 150-200 | 5-8 | Humility markers, cross-domain |
| Masters of Doom excerpts | ~15K | 20-40 | 1-2 | Style only (Tier 3 caution) |
| **Total** | **~150K** | **565-770** | **21-30** | **Complete baseline** |

---

## §7 Token Cost Estimate

### 7.1 One-Pass Extraction Cost

Each chunk processed costs one LLM inference. The extraction prompt is longer than a simple read.

| Component | Tokens | Notes |
|-----------|--------|-------|
| System prompt + instructions | ~500 | Fixed overhead |
| Chunk (average) | ~2,048 | Source text |
| Generated output (estimated) | ~800 | DPO pair + markers + concepts |
| **Total per inference** | **~3,348** | Input + output |

**Total cost**: 
- Chunks: ~150K tokens total / 2,048 per chunk = ~73 chunks
- 73 chunks × 3,348 tokens = ~244K tokens consumed
- In pure inference time (qwen3-1.7b-q6_k at ~25 tok/s): ~9,800 seconds ≈ **2.7 hours**
- At $0 (local): **zero monetary cost**

### 7.2 Optimization: Chunk Batching

By including 2-3 chunks per inference (up to the model's context window), we can reduce the number of calls:

| Batching | Chunks per call | Calls | Total tokens | Estimated time |
|----------|----------------|-------|-------------|----------------|
 | None | 1 | ~73 | ~244K | ~2.7 hr |
| Aggressive | 3 | ~24 | ~80K | ~0.9 hr |
| **Recommended** | **2** | **~37** | **~124K** | **~1.4 hr** |

**Recommended**: 2 chunks per call. This captures enough context for cross-referencing without exceeding the model's output quality ceiling.

### 7.3 Marginal Cost Above Reading

The base "Phase 2: Knowledge Ingestion" plan costs:
- 73 reads × 2,048 tokens input ≈ 150K tokens (just reading and understanding)

The triple extraction adds:
- 37 extra generation rounds × 800 tokens each ≈ 30K tokens output
- **This is a 19% token overhead above the base ingestion pass**
- **Yield**: 570+ DPO pairs, 30 knowledge graph nodes, complete voice baseline

**This is the Carmack Efficiency Corollary in action**: ~19% more tokens → 3 completely orthogonal data products.

---

## §8 Quality Assurance: Hallucination Prevention

### 8.1 The Hallucination Risk Profile

| Risk | Severity | Cause | Mitigation |
|------|----------|-------|------------|
| **R-H1** | 🔴 CRITICAL | DPO pair attributes a statement to Carmack he never made | Traceability chain to source text |
| **R-H2** | 🔴 CRITICAL | DPO pair reverses chosen/rejected (Carmack's rejected is labeled as chosen) | Cross-source consistency check |
| **R-H3** | 🟡 HIGH | Voice baseline includes marker phrases not actually from Carmack | Baseline extraction from source text only |
| **R-H4** | 🟡 HIGH | Knowledge graph connects concepts Carmack never related | Edge provenance must cite source |
| **R-H5** | 🟢 LOW | Synthetic DPO pair in "style" dimension doesn't match Carmack's tone | Voice validation score serves as QA |

### 8.2 The Traceability Chain (Non-Negotiable)

Every extracted data product must maintain a traceability chain back to the source text:

```
Source Document (line 45-52)
        │
        ▼
Source Quote (verbatim excerpt)
        │
        ▼
Chunk (context window)
        │
        ▼
DPO Pair ─── contains ─── source_section + quote_start/end offsets
Voice Marker ─── contains ─── source_section + count
Graph Node ─── contains ─── source_provenance dict
```

### 8.3 The Three-Layer Hallucination Guard

#### Layer 1: Source Anchoring (Generation Time)
```python
# Every generated pair is anchored to a specific source excerpt.
# The generation prompt includes this constraint:
"Every DPO pair's 'chosen' field must be traceable to a specific 
statement in the provided excerpt. If you cannot find a Carmack 
statement that maps to a pair, do not generate a pair."
```

#### Layer 2: Cross-Source Consistency (Post-Generation)
```python
# After processing all sources, check for contradictions:
# - If two sources disagree on Carmack's stance, FLAG pairs
# - If a single-source pair contradicts a multi-source pattern, DEMOTE confidence
#
# Example: Carmack's stance on "rewrite vs incremental" evolved over time.
# .plan files from 1996 show aggressive rewrite stance; 
# Lex 2023 shows nuanced evolution. Both are valid; pairs must carry era context.
```

#### Layer 3: Verity Review Gate (Before Training)
```python
# Before any DPO pair enters the curated/ directory:
# 1. Verity reads the pair AND the source excerpt
# 2. Verity applies the voice validation rubric
# 3. Verity classifies: pass | flag | reject
# 4. Passed pairs join the balanced training set
```

### 8.4 The Canary Test

Before any LoRA training, run a canary validation:

```python
def canary_test(pairs: List[CarmackDPORecord]) -> Dict[str, float]:
    """
    Test the DPO dataset for coherence.
    
    1. Extract 5 random prompts from the dataset
    2. Ask qwen3-1.7b to generate "Carmack-style" responses to each
       WITHOUT providing the training pairs as examples
    3. Run voice validation on the generated responses
    4. If CarmackScore < 50 on any response: DATASET NEEDS REVIEW
    
    This tests whether the implicit patterns in the DPO pairs
    are strong enough to transfer to held-out prompts.
    """
```

### 8.5 Dataset Integrity Checks

```python
INTEGRITY_CHECKS = {
    "unique_prompts": lambda d: len(set(p.prompt for p in d)) == len(d),
    "no_empty_fields": lambda d: all(
        p.prompt and p.chosen and p.rejected for p in d
    ),
    "dimension_coverage": lambda d: all(
        dim in [p.dimension for p in d] 
        for dim in ["technical", "philosophy", "style", "anti-pattern"]
    ),
    "confidence_calibration": lambda d: all(
        (p.source_tier >= 3 and p.confidence <= 0.9) or p.source_tier < 3
        for p in d
    ),
    "tier_distribution": lambda d: (
        0.2 <= len([p for p in d if p.source_tier == 1]) / max(len(d), 1) <= 0.5
    ),
    "no_identical_chosen_rejected": lambda d: all(
        p.chosen != p.rejected for p in d
    ),
}
```

---

## §9 Implementation Roadmap

### Phase 1: Infrastructure (30 min)
| Step | Task | Output |
|------|------|--------|
| 1.1 | Create directory structure `data/training/entities/john_carmack/` | All subdirectories |
| 1.2 | Write schema files (schema.yaml, validation_rules.yaml, dimension_weights.yaml) | Validation framework |
| 1.3 | Write `CarmackBaseline` extraction script | `scripts/extract_carmack_baseline.py` |
| 1.4 | Write DPO generation prompt template | `data/training/entities/john_carmack/prompt_template.txt` |

### Phase 2: Baseline Extraction (45 min — runs alongside source reading)
| Step | Task | Output |
|------|------|--------|
| 2.1 | Process .plan files through baseline extractor | `baseline/carmack_baseline.json` |
| 2.2 | Extract top-500 vocabulary list | `baseline/vocabulary.json` |
| 2.3 | Extract FP markers, domain terms, humility markers | Individual JSON files |
| 2.4 | Extract sentence structure statistics | `baseline/sentence_stats.json` |

### Phase 3: Full Processing (3 hours — the main pass)
| Step | Task | Output |
|------|------|--------|
| 3.1 | Run triple extractor on all 5 sources | Raw JSONL batches + baseline updates |
| 3.2 | Run QA validation on all pairs | Sorted into passed/flagged/rejected |
| 3.3 | Accumulate knowledge graph nodes | `graph/nodes.jsonl`, `graph/edges.jsonl` |
| 3.4 | Generate batch manifests | `dpo/raw/batch_manifest.json` |

### Phase 4: QA & Curation (1 hour)
| Step | Task | Output |
|------|------|--------|
| 4.1 | Verity reviews flagged pairs | Flagged→passed or flagged→rejected |
| 4.2 | Build balanced training sets | `dpo/curated/dpo_v1_*.jsonl` |
| 4.3 | Run Voice Validation canary | Canary test results |
| 4.4 | Knowledge graph topology verification | `graph/topology.json` |

### Phase 5: Training Readiness (30 min)
| Step | Task | Output |
|------|------|--------|
| 5.1 | Final dataset statistics | Training readiness report |
| 5.2 | LoRA-ready JSONL (prompt, chosen, rejected only) | `dpo_lora_ready.jsonl` |
| 5.3 | Commit all training data to repo | `git add data/training/entities/john_carmack/` |

**Total implementation time**: ~5.5 hours (parallelizable with source ingestion)
**Token overhead above base ingestion**: ~19%

---

## Appendix A: Edge Cases

| Edge Case | Handling |
|-----------|----------|
| **Same prompt, multiple valid Carmack answers** | Keep multiple pairs; tag with `era_context` field showing which period they represent |
| **Carmack contradicted himself across decades** | Flag as "evolution" pairs; add `era` field (e.g., "1996-Quake", "2023-Lex") |
| **Source transcript has low quality/incomplete sections** | Flag those chunks; skip pair generation for low-confidence sections |
| **DPO pair chosen/rejected are both valid approaches in different contexts** | Set `pair_type = "decision_path_vs_alternative"` and add context qualifiers |
| **Carmack didn't actually say the "chosen" text verbatim** | Set `has_direct_quote = False` and `confidence -= 0.2` penalty |
| **Knowledge graph node already exists from a different source** | Merge definitions; consolidate provenance; check for contradictions |
| **Voice baseline from 1996 .plan files differs from 2023 Lex interview** | Create era-specific baselines; flag style drift |

---

## Appendix B: Monitoring & Iteration

After the first LoRA training cycle:
```python
def training_feedback_loop():
    """
    1. Run canary test on pre-training entity
    2. Train LoRA with balanced dataset
    3. Run canary test on post-training entity
    4. Compare CarmackScore pre vs post
    5. Identify lowest-scoring dimension
    6. Generate additional pairs targeting that dimension
    7. Retrain
    
    Expected improvement: +15-25 CarmackScore points per dimension after first LoRA
    """
```

---

*⬡ OMEGA ⬡ LILITH ⬡ deepseek-v4-flash ⬡ P6-P10 ⬡ TRC-TRAINING-DESIGN*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: P6-P10 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

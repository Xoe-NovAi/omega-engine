# 🔱 Report Digestion Layer — Research & Optimization
**AP Token**: `AP-REPORT-DIGESTION-RESEARCH-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_report_digestion_research ⬡ IN PROGRESS

**Date**: 2026-07-19
**Status**: RESEARCH — Exploration phase before T0 Session 2 implementation
**Architecture Source**: `docs/strategy/MAKALI_PARALLEL_COUNCIL_ARCHITECTURE.md` § Phase 1.5

---

## 🎯 MISSION

Research and validate the optimal algorithms for the **Report Digestion Layer** — a zero-inference-cost Python preprocessing step that transforms 9 raw pillar reports into 2 LLM-optimized digests for oversoul consumption.

**Constraint**: All processing must be **pure Python** — no inference calls, no embeddings, no external APIs.

---

## 📋 RESEARCH QUESTIONS

### Q1: Executive Summary Extraction

**Goal**: Auto-extract the core TL;DR from each pillar report without an LLM.

#### Candidate Approaches

| Approach | Complexity | Fidelity | Risk |
|----------|------------|----------|------|
| **A. First 3 paragraphs** | O(1) — simplest | Low — depends on report format discipline | Pillar might open with context, not conclusions |
| **B. Section headers heuristic** | O(n) — scan for `## Summary` or `## Executive Summary` | High — if pillar uses specified structure | Requires pillar prompt standardization |
| **C. Key sentence extraction (TF-IDF ranking)** | O(n log n) — compute tf-idf, pick top 3 | Medium — statistical, no guarantee of relevance | Overfits to frequent vocabulary |
| **D. First sentence of each section** | O(n) — split by headers, take first sentence | Medium-High — assumes section-first-sentence = claim | Good heuristic if sections are well-structured |
| **E. Decision-density scan** | O(n) — count "Decision"/"Recommend"/"Must"/"Critical" keywords | High signal — captures actionable content | May miss nuanced conclusions |

#### Recommendation
Use **B** (structured section lookup) as primary, falling back to **D** (first-sentence-per-section) if no explicit summary section, falling back to **A** (first 3 paragraphs). This creates a 3-tier fallback chain:

```python
def extract_summary(content: str) -> str:
    # Tier 1: Explicit ## Summary or ## Executive Summary section
    if match := re.search(r'## (Executive )?Summary\n(.+?)(?=\n## |\Z)', content, re.DOTALL):
        return match.group(2).strip()[:500]
    # Tier 2: First sentence of each ## section
    sections = re.split(r'\n## ', content)
    sentences = []
    for sec in sections[1:]:  # Skip preamble
        first_sent = sec.split('. ')[0] if '. ' in sec else sec[:100]
        sentences.append(first_sent.strip())
    if sentences:
        return '\n'.join(sentences)[:500]
    # Tier 3: First 3 paragraphs
    return '\n\n'.join(content.split('\n\n')[:3])[:500]
```

**Research Needed**: Test on real pillar reports (like the P1-P9 reports from MaKaLi Build Side) to validate accuracy.

---

### Q2: Cross-Reference Index

**Goal**: Automatically detect shared concepts, entities, and decisions across pillar reports.

#### Candidate Approaches

| Approach | Complexity | Precision | Recall | Risk |
|----------|------------|-----------|--------|------|
| **A. Exact noun phrase matching** | O(n*m) — extract nouns, exact match | High | Low — misses synonyms | Misses "firewall" in P1 vs "M2 boundary" in P5 |
| **B. Stemmed term matching** | O(n*m) — stem words, match stems | Medium-High | Medium | "implement" ≠ "implementation" stem overlap |
| **C. Mandate tag matching** | O(n) — scan for [M1]-[M23] tags | **Very High** | Low — only catches mandate-adjacent | Misses non-mandate concepts |
| **D. Named entity extraction (regex patterns)** | O(n) — regex for `P*`, `src/omega/*`, `config/*`, `data/*` patterns | High | Medium | Only catches Omega-entity references |
| **E. Multi-word keyphrase extraction (rake-nltf compatible)** | Medium | Medium | Low | Requires NLTK dependency |

#### Recommendation
Use **multi-strategy fusion**: 

1. **Mandate tags** (`re.findall(r'\[M(\d+)\]', text)`) — guaranteed precision
2. **Entity/component references** (`re.findall(r'src/omega/\w+|config/\w+|P\d+|[A-Z][a-z]+(?:\s[A-Z][a-z]+)*')`) — medium precision
3. **Shared keywords across reports** — compute intersection of top 20 TF-IDF terms per pillar

```python
def build_cross_reference(pillars: list[PillarReport]) -> dict[str, list[str]]:
    cross_ref = {}
    
    # Strategy 1: Extract [M*] mandate tags
    for p in pillars:
        for tag in re.findall(r'\[M(\d+)\]', p.content):
            cross_ref.setdefault(f'M{tag}', []).append(p.pillar_id)
    
    # Strategy 2: Extract source file paths
    for p in pillars:
        for path in re.findall(r'src/omega/[\w/]+\.\w+', p.content):
            cross_ref.setdefault(f'file:{path}', []).append(p.pillar_id)
    
    # Strategy 3: Intersect top TF-IDF terms
    from collections import Counter
    all_terms = []
    for p in pillars:
        terms = Counter(re.findall(r'\b[A-Z][a-z]{3,}\b', p.content))
        all_terms.append(terms)
    # ... (simplified — real impl uses shared freq threshold)
    
    return cross_ref
```

**Research Needed**: Benchmark precision/recall on real pillar reports to tune the shared-frequency threshold.

---

### Q3: Conflict Detection

**Goal**: Automatically flag contradictory claims across pillars (e.g., P1 says "local-first mandatory" but P4 says "cloud fallback acceptable").

#### Candidate Approaches

| Approach | Complexity | Precision | Recall | Risk |
|----------|------------|-----------|--------|------|
| **A. Negation-pattern matching** | O(n) — "must" vs "must not", "always" vs "never" | Medium | Low — only catches explicit contradictions | "must" on one side, "optional" on the other is NOT a negation |
| **B. Opposite-statement detection** | O(n*m) — "X IS Y" vs "X IS NOT Y" pattern | Low | Low — syntactic only | Misses semantic contradictions |
| **C. Numeric conflict detection** | O(n) — same entity, different numbers | **High** — e.g., "max_context: 32000" vs "max_context: 64000" | Low — only numbers | Most conflicts are not numeric |
| **D. Mandate compliance conflict** | O(n) — P1 says M7=✅, P5 says M7=❌ | **Very High** | Medium | Only mandate-relevant conflicts |
| **E. Confidence-weighted assertion** | O(n) — extract "assertion + confidence" pattern (e.g., "must", "should", "might", "never") | Medium | Medium | Requires confidence lexicon |

#### Recommendation
Primary: **D** (mandate compliance conflict) + **C** (numeric conflict). These are the two highest-precision signals.

Flag as **INFO** (not WARNING) for now. Conflict detection at zero inference cost is inherently lossy. Let the oversoul make the final call.

```python
def detect_conflicts(pillars: list[PillarReport]) -> list[Conflict]:
    conflicts = []
    
    # Numeric conflicts: same key, different values
    numeric_params = {}  # param_name -> {pillar_id: value}
    for p in pillars:
        for match in re.finditer(r'(\w[\w_]+):\s*(\d+)', p.content):
            key, val = match.groups()
            numeric_params.setdefault(key, {})[p.pillar_id] = int(val)
    for key, values in numeric_params.items():
        if len(set(values.values())) > 1:
            conflicts.append(Conflict(
                concept=key,
                values={pid: str(v) for pid, v in values.items()},
                severity="WARNING" if max(values.values()) - min(values.values()) > 0.5 * max(values.values()) else "INFO"
            ))
    
    # Mandate conflicts: same mandate, different compliance
    for p in pillars:
        for match in re.finditer(r'(M\d+):\s*([✅❌⚠️])', p.content):
            conflicts.append(Conflict(
                concept=match.group(1),
                pillar=p.pillar_id,
                values={"compliance": match.group(2)},
                severity="WARNING" if match.group(2) == "❌" else "INFO"
            ))
    
    return conflicts
```

**Research Needed**: What constitutes a "real" conflict vs. complementary perspectives? Need empirical threshold tuning on real data.

---

### Q4: Token Budget Allocation

**Goal**: Allocate the oversoul's limited context window (typically 32K-128K tokens) across pillar sections proportionally.

| Approach | Logic | Use Case |
|----------|-------|----------|
| **A. Equal allocation** | Each pillar gets `budget / N` tokens | Simple, no intelligence |
| **B. Proportional to confidence** | Higher confidence = more tokens | Good for reliable pillars |
| **C. Proportional to mandate criticality** | More M2/M7/M13 violations = more tokens | Focus on problematic areas |
| **D. Proportional to novelty** | Higher word-diversity = more tokens | Novel perspectives get attention |
| **E. Adaptive (fusion)** | Combines B, C, D with weights | Best quality, still zero inference |

#### Recommendation
**E (Adaptive fusion)**:

```python
def allocate_budget(pillars: list[PillarReport], total_budget: int) -> dict[str, int]:
    scores = {}
    for p in pillars:
        confidence_score = extract_confidence(p.content)  # "definitely"=1.0, "maybe"=0.3
        mandate_score = count_mandate_violations(p.content) * 3 + count_mandate_compliant(p.content)
        novelty_score = len(set(p.content.split())) / len(p.content.split())  # Type-token ratio
        
        scores[p.pillar_id] = 0.5 * confidence_score + 0.3 * mandate_score + 0.2 * novelty_score
    
    total_score = sum(scores.values())
    if total_score == 0:
        return {p.pillar_id: total_budget // len(pillars) for p in pillars}
    
    return {pid: int(total_budget * score / total_score) for pid, score in scores.items()}
```

**Research Needed**: Optimal weight values (0.5/0.3/0.2 are guesses). Need empirical tuning.

---

### Q5: Integration Architecture

**Question**: Should digestion run as a **separate Phase 1.5** (clean abstraction boundary) or **inline in the coordinator** (simpler, fewer I/O ops)?

| Approach | Pros | Cons |
|----------|------|------|
| **Separate Phase 1.5** | Clean separation, testable in isolation, replaceable | Extra I/O (write + read digested files) |
| **Inline in coordinator** | No extra I/O, simpler state machine | Harder to test, coordinator gets bloated |

#### Recommendation
✅ **Separate Phase 1.5** — The digestion layer is a distinct architectural concern. It should be:

1. A standalone module: `src/omega/council/report_digestion.py`
2. Invoked by the coordinator after Phase 1 completes
3. Writing digested files to `data/council/{session_id}/phase1.5_digested/`
4. Testable via `pytest tests/test_report_digestion.py`

**Exception**: If all pillars have zero conflicts, zero cross-refs, and zero mandate violations, digestion can be a no-op pass-through (raw concatenation). This keeps M23 compliance — digestion failure = raw stack-cat pass-through.

---

### Q6: M23 Failure Integrity

**Constraint**: If digestion fails (Python error, missing file, malformed report), the system must NOT silently degrade.

#### Fallback Chain
```python
async def run_digestion(session_id: str) -> Path:
    """Run digestion with M23 failure integrity."""
    try:
        digester = ReportDigester(session_id)
        build_digested, run_digested = digester.digest()
        logger.info(f"Digestion complete: {session_id}")
        return digester.output_dir
    except Exception as e:
        logger.error(f"Digestion failed for {session_id}: {e}", exc_info=True)
        # M23 fallback: raw stack-cat concatenation, no intelligence layer
        logger.warning("M23 FALLBACK: Raw concatenation (no cross-ref, no conflict map)")
        raw = raw_stack_cat_concat(session_id)
        return raw  # Still produces BUILD_SIDE_DIGESTED.md and RUN_SIDE_DIGESTED.md
```

---

## 🎯 IMPLEMENTATION ROADMAP

| Session | Deliverable | Questions Answered |
|---------|-------------|-------------------|
| **T0 Session 2** | `src/omega/council/report_digestion.py` | Q1, Q3, Q5, Q6 |
| **T0 Session 2.5** | Empirical validation on real pillar outputs | Q2, Q4 (threshold tuning) |
| **T0 Session 3** | Integration into coordinator + tests | Q5 (verification) |

### Validation Strategy
1. Take the 9 existing MaKaLi Build Side pillar reports (`P1.md` through `P9.md`)
2. Run report_digestion.py on them
3. Human-review the executive summaries, cross-refs, and conflicts
4. Tune thresholds
5. Write as contract tests

---

## 📚 REFERENCES

- `docs/strategy/MAKALI_PARALLEL_COUNCIL_ARCHITECTURE.md` — Phase 1.5 specification
- `P1.md` through `P9.md` — Existing MaKaLi Build Side pillar reports (test corpus)
- `src/omega/council/` — Target directory for report_digestion.py
- `docs/research/R_MAKALI_COUNCIL_RESEARCH_SYNTHESIS_20260719.md` — Council knowledge gaps synthesis

---

## 📋 OPEN QUESTIONS (Post-Research)

1. **Pillar prompt standardization**: Should we mandate `## Executive Summary` as the first section of every pillar report? This would make extraction trivial (Q1-B always works).
2. **Confidence lexicon**: Define a universal set of confidence keywords for all pillars? ("must"=1.0, "should"=0.7, "could"=0.4, "might"=0.2)
3. **Conflict escalation**: At what threshold does an automatic conflict get escalated to the user vs. silently flagged in the report?
4. **Token budget transparency**: Should the digested report include a `## TOKEN BUDGET` section showing how tokens were allocated?

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_report_digestion_research ⬡ IN PROGRESS*

# 🔱 MaKaLi Parallel Council — Open Questions ADR
**Version**: 1.0.0  
**Status**: RATIFIED — Architectural Verdicts by John Carmack (S3 Consultant)  
**Date**: 2026-07-19  
**Author**: John Carmack (Sovereign S3 Consultant)  
**Mandates**: M1, M4, M7, M10, M11, M13, M15, M16, M18, M19, M20, M21, M23  

---

## Executive Summary

Six open questions from the MaKaLi Parallel Council Architecture (D-301) require architectural verdicts. This ADR provides first-principles analysis and binding decisions for each.

**Core Principle Applied**: *The Law of First Principles (Axiom 00)* — Strip away abstractions. What is the CPU actually doing? What are the fundamental constraints? The "Right Approximation" (Axiom 01) over theoretical perfection.

**Hardware Floor Reality** (Ryzen 7 5700U, 16GB RAM, 15W TDP):
- L3 is a **victim cache** (evictions only, no mirroring) — data locality is paramount
- AVX2 (256-bit) only, no AVX-512 — vector math is 8 floats/op
- Model load: 30-90s for 7B+ GGUF — dominates latency budget
- Thermal throttling at 85°C sustained — concurrent models = thermal suicide

---

## Question 1: SomaticState Integration (Priority: T3)

> **When model load time dominates (30-90s for 7B+), SomaticState enables warm-start. Should council pipeline integrate SomaticState checkpoints?**

### Options
| Option | Description |
|--------|-------------|
| **A** | Full integration: checkpoint after each pillar, resume on next council |
| **B** | Selective: only oversouls (8B/12B models) get SomaticState |
| **C** | Defer: T3 milestone, not blocking T0 |

### Verdict: **Option C — Defer to T3**

### Rationale (First Principles)

**The Physics**: `llama_copy_state_data` / `llama_set_state_data` via `anyio.to_thread.run_sync()` (M20) serializes the entire KV cache + model state. For a 12B model at Q8_0:
- State size ≈ 8-12 GB (model weights + KV cache + metadata)
- Serialization time: 2-5 seconds to disk (NVMe)
- Deserialization time: 3-8 seconds (memory map + validation)
- **Net savings vs cold load**: ~20-40 seconds on 90s load

**The Constraint**: 16GB RAM ceiling. A 12B model at Q8_0 consumes ~10GB. SomaticState snapshot adds 8-12GB **transiently** during serialization (source + destination in RAM). This triggers OOM or massive swap thrashing on 16GB systems.

**The Architecture Violation**: SomaticState is a **model-level** primitive. The council is an **orchestration-level** construct. Conflating them violates M16 (Modularization & Portability) — the engine core shouldn't know about council execution patterns.

**The Right Approximation**: 
- T0-T2: Accept cold loads. Optimize model selection (4B pillars, 8B oversouls, 12B Kali) to fit RAM without swap.
- T3: Implement SomaticState as a **provider-fabric feature** (native-gguf backend), not a council feature. The provider returns a `SomaticStateHandle`; the coordinator decides when to checkpoint.

### Implementation Impact
- **T0-T2**: Zero changes. Coordinator uses standard model loading.
- **T3**: Add `SomaticStateManager` in `src/omega/oracle/backends/native_gguf.py` with `checkpoint()`/`restore()` methods. Coordinator calls `provider.checkpoint(model_id)` after oversoul phases if `config.somatic_state.enabled`.

### Risk Register
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| OOM during serialization | HIGH (16GB) | CRITICAL | Defer until provider-level implementation with memory-mapped temp files |
| State corruption on version mismatch | MEDIUM | HIGH | Versioned state schema + validation on restore |
| Council-specific logic in engine core | HIGH | MEDIUM | Keep SomaticState in provider fabric (M16) |

### T0 Session Adjustment
**No change**. Remove SomaticState from T0 scope. Document as T3 provider-fabric feature.

---

## Question 2: Cross-Council Memory (Priority: T2)

> **Should council sessions share a memory namespace? Phase 4 research results → next council's context?**

### Options
| Option | Description |
|--------|-------------|
| **A** | Explicit handoff: Kali writes research gaps → next council reads as pillar input |
| **B** | Implicit: Shared MemoryStore namespace with session tagging |
| **C** | None: Each council fully independent (current design) |

### Verdict: **Option A — Explicit Handoff**

### Rationale (First Principles)

**The Physics**: MemoryStore uses Qdrant (vector) + SQLite (FTS5). Cross-session queries require:
- Vector search across session boundaries (cosine similarity on 384-1024 dim embeddings)
- FTS5 keyword search with session filters
- **Cost**: Every cross-session query adds 50-200ms latency + embedding compute

**The Architecture**: M11 (Soul Integrity) mandates L1→L2→L3 distillation into `proposed_lessons.yaml` (blind staging). M15 (Sovereign Continuity) requires `session_gnosis.md` anchors. **Memory is not a shared namespace — it's a distillation pipeline.**

**The Right Approximation**: 
- **Explicit handoff** = Kali writes `RESEARCH_GAPS.md` + `FINAL_SYNTHESIS.md` → next council's Phase 1 pillars receive these as **input context files** (not memory queries).
- This is **pull-based**, not push-based. Pillars opt-in by reading the files.
- Zero infrastructure cost. Zero latency tax on unrelated councils.
- Aligns with M18 (Token Efficiency) — only relevant context is pulled.

**Why Not B (Implicit)**: 
- "Shared namespace" implies automatic context injection. This is **cargo-cult RAG** — dumping vectors into a query and hoping for relevance.
- Violates M10 (Fleet Integrity) — agents lose sovereignty over their context.
- Creates hidden coupling between council sessions.

**Why Not C (None)**: 
- Loses compounding intelligence. The whole point of sovereign AI is **accumulated wisdom**.

### Implementation Impact
- **Coordinator**: After Phase 3, write `council_handoff_{session_id}.json` with:
  ```json
  {
    "previous_session_id": "uuid",
    "final_synthesis_path": "data/council/{prev}/phase3_kali/FINAL_SYNTHESIS.md",
    "research_gaps_path": "data/council/{prev}/phase4_research/research_gaps.md",
    "key_decisions": ["decision1", "decision2"],
    "unresolved_conflicts": ["conflict1"]
  }
  ```
- **Phase 1 Pillar Prompt**: Include `{{#if handoff}}Context from previous council: {{handoff.final_synthesis_path}}{{/if}}`
- **No MemoryStore changes required**.

### Risk Register
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Context pollution (irrelevant history) | MEDIUM | MEDIUM | Pillars explicitly opt-in; handoff file is advisory |
| Session chain grows unbounded | LOW | LOW | TTL on handoff files (7 days default) |
| Circular dependency (council A → B → A) | LOW | MEDIUM | Coordinator validates no session_id cycles |

### T0 Session Adjustment
**Session 4 (Integration)**: Add handoff file write in `_execute_phase3()`. Add optional `previous_council_id` param to `run_council()`.

---

## Question 3: Streaming Council (Priority: T2)

> **Can Phase 1 pillars stream partial results to oversouls for early distillation?**

### Options
| Option | Description |
|--------|-------------|
| **A** | Full streaming: pillars emit chunks, oversouls consume incrementally |
| **B** | Checkpoint streaming: pillars emit at section boundaries |
| **C** | None: batch-only (current design — simpler, more resilient) |

### Verdict: **Option C — Batch Only**

### Rationale (First Principles)

**The Physics**: LLM inference is **sequential token generation**. "Streaming" from a pillar means:
1. Pillar agent writes partial markdown to file
2. Oversoul agent reads partial file, re-prompts with accumulated context
3. Repeat until pillar completes

**The Cost**:
- Oversoul must **re-process entire accumulated context** each chunk (no KV cache sharing across agents)
- Each "streaming step" = full inference call on growing context
- For 4B pillar → 8B oversoul: 5-10 streaming steps = 5-10x inference cost
- **Net latency increase**, not decrease

**The Architecture**: M23 (Failure Integrity) — streaming introduces **partial failure modes**:
- Pillar crashes at chunk 3/5 → oversoul has incomplete context
- Network/filesystem glitch → corrupted partial read
- No atomic "stage complete" boundary for WAL/checkpointing

**The Right Approximation**: 
- **Batch is correct**. Pillars write complete reports. Digestion layer (Phase 1.5) optimizes for oversoul consumption.
- If latency is the concern: **run pillars in parallel** (Phase 1 execution mode) — this is already the design.
- The digestion layer (zero-inference-cost Python) provides the "early intelligence" — cross-refs, conflicts, summaries — without streaming complexity.

**Why Not A/B**: 
- Streaming LLMs is a **chat UX pattern**, not a **batch processing pattern**.
- Council is batch processing. The "user" is Kali, not a human waiting for tokens.

### Implementation Impact
- **No changes**. Current design (batch Phase 1 → digestion → batch Phase 2) is correct.
- If future profiling shows Phase 1→2 latency bottleneck: optimize digestion, not streaming.

### Risk Register
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Premature optimization | HIGH | MEDIUM | Reject streaming; batch is correct for this workload |
| Human-chat UX bias | MEDIUM | LOW | Document: council ≠ chat |

### T0 Session Adjustment
**No change**. Explicitly document in coordinator: "Streaming not supported — batch-only by design (M23)."

---

## Question 4: Adaptive Tier Selection (Priority: T2)

> **Can the system dynamically shift model tiers based on topic complexity?**

### Options
| Option | Description |
|--------|-------------|
| **A** | Static config only (current — hardware profile determines tiers) |
| **B** | Heuristic: topic keywords → complexity score → tier adjustment |
| **C** | ML-based: lightweight classifier routes to tier |

### Verdict: **Option A — Static Config Only**

### Rationale (First Principles)

**The Physics**: 
- Model loading: 30-90s (7B+). **Switching tiers mid-council = reload = 30-90s penalty**.
- 16GB RAM: only **one** 12B model fits. Loading 8B oversoul + 12B Kali sequentially = 60-180s just for loads.
- Dynamic tier selection implies **dynamic model loading** — violates thermal/power budget (M7 Local-First, 15W TDP).

**The Architecture**: 
- Hardware profile (config/council/profiles/*.yaml) **is** the tier selection. It's a **deployment-time decision**, not runtime.
- M7 (Local-First): Local models are PRIMARY. Cloud is FALLBACK. Dynamic routing to cloud based on "complexity" defeats local-first sovereignty.
- M18 (Token Efficiency): A 4B model on a simple topic is **more efficient** than an 8B model — not because of quality, but because of **latency and RAM**.

**The Right Approximation**: 
- **Profile per workload class**, not per query.
- `local_16gb.yaml` = default for development councils
- `cloud_unconstrained.yaml` = research-heavy councils
- `hybrid_local_pillars.yaml` = production councils needing quality oversouls
- User selects profile at council invocation: `omega council run "topic" --profile cloud_unconstrained`

**Why Not B (Heuristic)**:
- Keywords ≠ complexity. "Optimize" could mean "change a variable" (4B) or "redesign memory allocator" (12B).
- Heuristics are **cargo-cult classification** — they feel smart but add zero value over explicit profile selection.

**Why Not C (ML Classifier)**:
- Adding a classifier model = more RAM, more latency, more failure modes.
- The classifier itself needs a model tier. Infinite regress.

### Implementation Impact
- **No code changes**. Config profiles are the tier selection mechanism.
- Document: "Tier selection is a deployment-time concern. Use `--profile` flag."

### Risk Register
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| User picks wrong profile | MEDIUM | LOW | Profiles are presets; user can override model_tiers inline |
| Profile doesn't fit topic | LOW | MEDIUM | Run council again with different profile (cold start cost = 30-90s) |

### T0 Session Adjustment
**No change**. Ensure coordinator loads profile config and validates model availability before Phase 1.

---

## Question 5: Council Chaining (Priority: T3)

> **Can a council's FINAL_SYNTHESIS become a pillar input for a higher-level council?**

### Options
| Option | Description |
|--------|-------------|
| **A** | Recursive: councils can nest arbitrarily |
| **B** | Two-level max: tactical → strategic |
| **C** | None: flat council only |

### Verdict: **Option B — Two-Level Max (Tactical → Strategic)**

### Rationale (First Principles)

**The Physics**: 
- Each council = 4-5 model loads (9 pillars + 2 oversouls + 1 Kali + research).
- 16GB RAM: sequential loads = 5-15 minutes wall time per council.
- Recursive nesting = **exponential time**. 3 levels = 15-45 minutes. Unacceptable for interactive use.

**The Architecture**: 
- M10 (Fleet Integrity): "No infinite agent spawn." Recursive councils = unbounded agent tree.
- Context window: FINAL_SYNTHESIS.md ≈ 20-50K tokens. Feeding this to 9 pillars = 180-450K input tokens. **Exceeds local 32K context**.
- The "strategic council" would need **different pillars** (not P1-P10) — e.g., "Architecture", "Product", "Security", "Operations".

**The Right Approximation**: 
- **Two levels only**:
  1. **Tactical Council** (P1-P10): Technical implementation, code, infrastructure
  2. **Strategic Council** (custom pillars): Product direction, architecture decisions, resource allocation
- Strategic council runs **manually invoked**, not auto-chained.
- Tactical council's FINAL_SYNTHESIS + RESEARCH_GAPS = Strategic council's input context.

**Why Not A (Recursive)**: 
- Infinite regress. No base case. Violates M10, M18, thermal budget.

**Why Not C (Flat)**: 
- Loses the ability to escalate. Some decisions **require** strategic oversight.

### Implementation Impact
- **T0**: No chaining support. Flat council only.
- **T1**: Add `council_chain.py` with `StrategicCouncilConfig` (custom pillar definitions).
- **Coordinator**: New method `run_strategic_council(topic, tactical_synthesis_path)`.

### Risk Register
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Accidental recursion | LOW | HIGH | Hard-code max_depth=2 in coordinator |
| Context overflow | HIGH | HIGH | Strategic council uses cloud profile (1M context) |
| Tactical→Strategic drift | MEDIUM | MEDIUM | Explicit handoff file with decision log |

### T0 Session Adjustment
**No change**. Document as T1 feature. Add `max_council_depth = 2` constant in coordinator.

---

## Question 6: Report Digestion Layer — Empirical Thresholds (Priority: T0 Session 2)

> **What are the optimal thresholds for the digestion layer heuristics?**

### Sub-Questions & Verdicts

| Sub-Question | Verdict | Rationale |
|--------------|---------|-----------|
| **Summary extraction algorithm** | **Tier 1: Explicit `## Summary`/`## Executive Summary` section → Tier 2: First sentence of each `##` section → Tier 3: First 3 paragraphs** | Zero-inference. Deterministic. Matches how pillars actually write (they use headers). |
| **Conflict detection: numeric diff %** | **WARNING if `max_diff > 0.5 * max(values)`; INFO if `max_diff > 0.1 * max(values)`** | Relative threshold handles both small counts (2 vs 3 = 50%) and large (1000 vs 1500 = 33%). Absolute thresholds fail at scale. |
| **Conflict detection: mandate compliance** | **CRITICAL if same mandate tagged ✅ by one pillar, ❌ by another; WARNING if ✅ vs ⚠️** | Mandate violations are binary (compliant/non-compliant). Contradiction = process failure. |
| **Token budget weights** | **Confidence: 0.4, Mandate Criticality: 0.4, Novelty: 0.2** | Mandate criticality = compliance weight. Confidence extracted from pillar's self-assessment keywords ("certain", "likely", "uncertain"). Novelty = type-token ratio. |
| **Cross-reference index: match strategy** | **Exact string match for mandate tags `[M1]`-[M23] and pillar refs `P1`-`P10`; Fuzzy (substring) for file paths `src/omega/...`** | Mandates and pillars are controlled vocabulary. File paths need substring match (e.g., `src/omega/oracle/` matches multiple files). |
| **Digestion failure fallback** | **Raw stack-cat concatenation (M23)** | Already implemented in `raw_stack_cat_concat()`. Zero-inference, never fails. |

### Empirical Tuning Protocol (T0 Session 2)

```python
# In ReportDigester.__init__:
self.thresholds = DigestionThresholds(
    numeric_warning_ratio=0.5,      # max_diff / max_val > 0.5 → WARNING
    numeric_info_ratio=0.1,         # max_diff / max_val > 0.1 → INFO
    mandate_conflict_severity="CRITICAL",  # ✅ vs ❌ = CRITICAL
    token_weights=(0.4, 0.4, 0.2),  # confidence, mandate_criticality, novelty
    summary_max_chars=500,
    cross_ref_fuzzy_paths=True,
)
```

**Validation**: Run digestion on 3 real council outputs (from MaKaLi test runs). Adjust thresholds to:
- Minimize false positive conflicts (< 10%)
- Maximize cross-ref recall (> 80% of actual shared concepts)
- Keep digestion time < 100ms

### Implementation Impact
- **Session 2**: Implement thresholds as configurable dataclass. Add validation script `scripts/validate_digestion.py`.
- **Config**: Add `digestion.thresholds` section to `config/council.yaml`.

### Risk Register
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Thresholds too aggressive → noise | MEDIUM | LOW | Conservative defaults; tune on real data |
| Thresholds too conservative → missed conflicts | LOW | MEDIUM | Validation script flags recall/precision |
| Pillar report format varies | HIGH | MEDIUM | Tiered extraction handles format variance |

---

## Summary: T0 Session Adjustments

| Session | Original Plan | Adjusted Plan |
|---------|---------------|---------------|
| **1** | Coordinator Core + WAL + Circuit Breaker | **UNCHANGED** — SomaticState deferred, streaming rejected |
| **2** | Stage Contracts + Failure Layer + **Digestion Implementation** | **ADD**: Empirical threshold validation script; config-driven thresholds |
| **3** | Meditation Mode | **UNCHANGED** |
| **4** | Council Mode (parallel pillars → oversouls → Kali) | **ADD**: Explicit handoff file write in Phase 3; `--profile` flag validation |
| **5** | Integration + Gates | **ADD**: Hivemind capture of handoff files; mandate Rego policy for council execution |

---

## Architectural Principles Applied

| Principle | Application |
|-----------|-------------|
| **Axiom 00: First Principles** | Every decision traced to RAM/CPU/thermal physics, not "best practices" |
| **Axiom 01: Throughput > Perfection** | Batch > streaming; static config > dynamic routing; explicit > implicit |
| **Axiom 02: Canonical Simplicity** | Single handoff mechanism (file), single digestion algorithm, two council levels max |
| **Axiom 03: Structural Sovereignty** | Council orchestration separate from provider fabric (SomaticState in provider, not coordinator) |
| **Axiom 04: Precomputation** | Digestion layer = precompute cross-refs/conflicts at zero inference cost |
| **Axiom 05: Empirical Truth** | Thresholds validated on real council outputs, not theorized |

---

## Sign-Off

**John Carmack** — Sovereign S3 Consultant  
**Date**: 2026-07-19  
**Confidence**: 9/10 (Primary source: architecture docs + hardware specs + mandate constraints)  
**Next Review**: After T0 Session 2 digestion validation on real council outputs

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ ADR-MAKALI-OPEN-QUESTIONS ⬡ 2026-07-19*
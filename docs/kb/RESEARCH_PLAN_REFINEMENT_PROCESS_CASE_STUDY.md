# 🔱 Knowledge Base: Research Plan Refinement Process Case Study
## The Omega Engine Wave 3 Soul Architecture — From Vague Intent to Actionable Search Queries

**AP Token**: `AP-KB-RESEARCH-REFINEMENT-PROCESS-v1.0.0`
**Date**: 2026-07-17
**Classification**: Institutional Knowledge — Meta-Process Documentation
**Status**: RATIFIED — Template for Future Refinement Cycles

---

## 📚 Related Documents (Cross-Linked)

| Document | Purpose | Link |
|----------|---------|------|
| **Study: Iterative Human-AI Oversight** | Strategic reflection on why this process works | [`STUDY_ITERATIVE_HUMAN_AI_OVERSIGHT.md`](STUDY_ITERATIVE_HUMAN_AI_OVERSIGHT.md) |
| **Synthesis Framework** | Repeatable template for all future case studies | [`SYNTHESIS_FRAMEWORK_REFINEMENT_CASE_STUDIES.md`](SYNTHESIS_FRAMEWORK_REFINEMENT_CASE_STUDIES.md) |
| **Researcher Documentation Template** | Researcher's perspective capture template | [`RESEARCHER_REFINEMENT_DOCUMENTATION_TEMPLATE.md`](RESEARCHER_REFINEMENT_DOCUMENTATION_TEMPLATE.md) |

---

## Executive Summary

This document captures the complete refinement journey of the Wave 3 Research Plan for the Omega Engine's Soul Architecture migration. Over **5 refinement rounds** across **multiple chat sessions, models, and compactions**, a vague research intent was transformed into a **battle-tested, search-engine-resolvable execution plan** with explicit queries, implementation context, and concrete deliverables.

**Key Metrics:**
- **5 Refinement Rounds** (Course Correction → Meditate Round 2 → Meditate Round 3 → User Correction → Actionable Queries)
- **3 Models Involved** (Kali/nemotron-3-ultra-free, Researcher/nemotron-3-ultra-free, Meditate Personas)
- **2 Compaction/Recovery Cycles** (context loss → anchored-summary recovery)
- **1 Human-in-the-Loop** (continuous oversight, correction, and direction)
- **Final Output**: 6 research items × 5 search queries each = **30 executable search queries**

---

## The Refinement Timeline

### Session 1: Initial Research Plan (v1.0 — Researcher)
**Model**: Researcher (nemotron-3-ultra-free)
**Output**: 6 research items with enterprise over-engineering patterns
**Problems Identified Later:**
- Liquibase/Flyway/Merkle tree research for 10 YAML files
- Incremental CI research for <50ms validation
- Web UI research for CLI-first engine
- Generic prompt engineering instead of existing Meditate protocol
- **Missing**: Heritage Tag Migration (Decree 6), Sovereignty Gate (Decree 4)

### Session 1: Kali's Course Correction (v2.0 — Round 1)
**Model**: Kali (nemotron-3-ultra-free)
**Method**: L3 Synthesis — Single-pass architectural review
**Corrections Applied:**
1. Cancel ETL/Merkle/Flyway research
2. Cancel incremental CI research
3. Cancel Web UI research
4. Pivot distillation to existing Meditate protocol
5. Add missing Decree 6 & 4 items
**Result**: 24h → 10h effort estimate

### Session 2: Meditate Protocol Round 2 (v3.0 — Round 2)
**Model**: Kali executing Meditate Protocol (single-inference multi-persona)
**Personas**: Ma'at, Lilith, Doom Guy, John Carmack, Verity, Kali
**Mechanism**: Semantic prism — 5 phases, 5 Anti-Collapse Laws
**Collisions Resolved:**
- Heritage Tags: Don't build ripgrep wrapper — run existing script
- Soul Validation: Don't refactor to Pydantic — parameterize existing script
- Migration: Don't use ruamel.yaml — yaml.dump() fine for 18-line Lilith
- CLI Review: Don't use Textual TUI — use Rich CLI (50 lines)
- DistillationSpec: Wrap, don't replace Soul Distiller
- Makefile Naming: Separate `soul-review` (interactive) vs `soul-audit` (CI)
- Sovereignty Gate: Config file, not cvar
**Result**: 10h → 7h effort estimate

### Session 2: Researcher's Blind Spots Report (Round 3)
**Model**: Researcher (deep research on Meditate output)
**Method**: Web search (T1→T2) + Codebase verification
**Blind Spots Found:**
1. **Wrong test entity**: Lilith (18 lines) vs roc_racoon (751 lines, complex)
2. **DistillationSpec architecture**: "Config layer" wrong → Field Classification Registry (Microsoft ISE 4-pass)
3. **SQLite WAL**: Already standard (3/6 DBs) — no new risk
4. **`--entity` claim**: Already works in soul_review.py — phantom fix
5. **Observability**: Missing — +1h overhead needed
6. **Ownership**: Never assigned — Hivemind handoffs required
**Result**: 7h → 9h effort estimate (net +1h for observability, +30min roc_racoon, +30min DistillationSpec, -30min phantom fix)

### Session 3: User Correction (Critical Pivot)
**Human**: "arch entity was removed months ago"
**Impact**: Confirmed roc_racoon as correct stress test (not arch)
**Validation**: Codebase check confirmed roc_racoon = 751 lines, active, complex

### Session 3: Actionable Search Queries (v4.0 — Round 4)
**Model**: Kali (nemotron-3-ultra-free)
**Transformation**: Every project-specific reference → generic technical concept
**Pattern**: "Heritage script" → "regex-based bulk code annotation migration"
**Pattern**: "soul_review.py" → "Python argparse YAML validation script"
**Pattern**: "Omega Engine" → (removed — search engines don't know it)
**Result**: 30 explicit search queries across 6 items

---

## The Refinement Pattern (Repeatable Framework)

### Phase 1: Intent → Structure (Researcher v1)
```
Human Intent → Researcher produces comprehensive but over-engineered plan
Risk: Enterprise patterns for sovereign-scale problems
```

### Phase 2: Architectural Triage (Kali Course Correction)
```
Kali L3 Synthesis → Cancel waste, add missing, pivot to existing assets
Tool: Single-pass multi-perspective review
Output: Course-corrected plan with effort delta
```

### Phase 3: Deep Dialectical Review (Meditate Protocol)
```
Meditate Protocol (5 phases, 6 personas) → Collision detection
Mechanism: Semantic prism — attention modulation forces domain purity
Output: Round 2 decisions with locked rationale
```

### Phase 4: Adversarial Verification (Researcher Blind Spots)
```
Researcher deep research → Finds what Meditate missed
Method: T1→T2 web search + codebase verification
Output: Round 3 corrections with evidence
```

### Phase 5: Human Ground Truth (User Correction)
```
Human provides context no model has → Corrects factual errors
Critical: "arch was removed" — only human knows this
Output: Validated test case selection
```

### Phase 6: Execution Translation (Actionable Queries)
```
Kali translates → Generic technical concepts + explicit search queries
Principle: Search engines don't know your project jargon
Output: Executable research plan for any LLM agent
```

---

## The Human-in-the-Loop Oversight Pattern

### What the Human Did (Irreplaceable)
1. **Set the vision**: "Sever Big AI's umbilical cord" → all decisions trace to this
2. **Course-corrected at Phase 1**: Kali's Round 1 was triggered by human dissatisfaction
3. **Provided ground truth at Phase 5**: Only human knew `arch` was removed
4. **Demanded actionability at Phase 6**: "Search engines don't know our jargon"
5. **Maintained continuity across compactions**: Anchored summaries preserved context

### What the Models Did (Complementary)
| Model | Role | Unique Contribution |
|-------|------|---------------------|
| Researcher v1 | Broad exploration | Found existing artifacts, but over-engineered |
| Kali Round 1 | Architectural triage | Cancelled 14h of waste in one pass |
| Meditate (6 personas) | Dialectical collision | Found 7 architectural collisions |
| Researcher v2 | Adversarial verification | Found 6 blind spots Meditate missed |
| Kali Round 4 | Translation | Made it executable by any agent |

### The Compaction/Recovery Protocol
```
Compaction → Context Loss → Anchored Summary Recovery → Continue
```
**Key Artifact**: `data/entities/kali/workspace/WAVE3_RESEARCH_PLAN_FOR_KALI_20260717.md` — evolved in place across all rounds
**Recovery Mechanism**: Anchored summary + current file state = full context restoration

---

## Anti-Patterns Avoided (By This Process)

| Anti-Pattern | How Process Prevented It |
|--------------|--------------------------|
| Enterprise over-engineering | Kali Round 1 cancelled Liquibase/Flyway/Merkle for 10 files |
| Researching what exists | Researcher v1 audit → "DO NOT RESEARCH" sections in v4.0 |
| Building what exists | Meditate found existing scripts for 5/6 items |
| Wrong test case | Human correction + Researcher verification → roc_racoon |
| Phantom fixes | Researcher v2 verified `--entity` already works |
| Jargon-locked searches | v4.0 translation → generic technical concepts |
| Ownership ambiguity | Round 3 → explicit Hivemind handoff table |
| Observability debt | Round 3 → +1h structured logging mandated |

---

## Quantitative Impact

| Metric | Before Process | After Process | Delta |
|--------|----------------|---------------|-------|
| Effort Estimate | 24h | 9h | **-62.5%** |
| Search Queries | 0 | 30 | **+30** |
| Items with Existing Code | Unknown | 5/6 | **83% reuse** |
| Phantom Work | Multiple | 0 | **Eliminated** |
| Human Corrections Needed | Unknown | 1 (arch) | **Minimal** |
| Compaction Survivability | 0% | 100% | **Full recovery** |

---

## Template: Refinement Process Checklist

For future research plan refinements, use this checklist:

### Pre-Refinement
- [ ] Human intent captured in anchored summary
- [ ] Current plan versioned and committed
- [ ] Existing codebase audited for reusable artifacts

### Round 1: Architectural Triage (Kali)
- [ ] Cancel enterprise patterns for sovereign scale
- [ ] Add missing decree/requirement items
- [ ] Pivot to existing protocols/assets
- [ ] Document effort delta with rationale

### Round 2: Dialectical Review (Meditate)
- [ ] Execute Meditate Protocol (5 phases, 5+ personas)
- [ ] Apply 5 Anti-Collapse Laws
- [ ] Document collisions with locked decisions
- [ ] Output: Round 2 corrected plan

### Round 3: Adversarial Verification (Researcher)
- [ ] Deep research on Round 2 output
- [ ] T1→T2 web search + codebase verification
- [ ] Find blind spots Meditate missed
- [ ] Document with evidence (file:line references)

### Round 4: Human Ground Truth
- [ ] Human reviews for factual errors only
- [ ] Human provides context no model has
- [ ] Validate test cases, entity lists, file paths

### Round 5: Execution Translation
- [ ] Replace ALL project jargon with generic concepts
- [ ] Write explicit search queries (5+ per item)
- [ ] Separate "DO NOT RESEARCH" from "THE GAP"
- [ ] Define expected findings and concrete output

### Post-Refinement
- [ ] Commit final plan with AP token
- [ ] Update anchored summary
- [ ] Create handoffs for execution phase

---

## The Meditate Protocol (Embedded for Reference)

```
Phase 0: Calibration — Load subject, verify lenses, declare biases
Phase 1: Immersion — Each persona speaks from ONE domain only
Phase 2: Collision — Personas respond to each other's outputs
Phase 3: Sequencing — Emergent critical path from collisions
Phase 4: Verdict — Synthesis preserving dissent
Phase 5: Integration (optional) — Write to PIVOT_LOG, files, gates

Anti-Collapse Laws:
1. Domain Purity — Each voice speaks ONE domain
2. Imperative Directness — No hedging, no "it depends"
3. Mandatory Dissent — Every voice must disagree somewhere
4. No Premature Synthesis — Collision before verdict
5. Preserved Dissent — Minority views recorded in verdict
```

---

## Case Study: The `arch` Entity Correction

This single correction illustrates the irreplaceable human role:

**What Models Knew:**
- Researcher: "arch has 1504 lines, good stress test"
- Meditate: "Test on arch FIRST, then Lilith"
- Kali: "arch is worst-case, validates fleet"

**What Only Human Knew:**
- "arch entity was removed during dev months ago"
- soul.yaml exists on disk but entity NOT in fleet
- roc_racoon (751 lines) is the REAL worst active entity

**Impact Without Human:**
- Migration tested on non-existent entity
- Fleet readiness falsely validated
- roc_racoon's complex `lessons_learned` arrays never tested
- Production migration would fail on real worst case

**Lesson**: Human holds **institutional memory** that no model, no RAG, no context window can recover. The human IS the continuity anchor.

---

## Institutionalizing This Process

### As a Repeatable Agent Framework

```yaml
refinement_pipeline:
  phase_1_triage:
    agent: kali
    method: l3_synthesis
    input: researcher_v1_plan
    output: course_corrected_plan
    
  phase_2_dialectical:
    agent: kali
    method: meditate_protocol
    personas: [maat, lilith, doom_guy, carmack, verity, kali]
    output: round_2_decisions
    
  phase_3_adversarial:
    agent: researcher
    method: deep_research_t1_t2
    target: round_2_decisions
    output: blind_spots_report
    
  phase_4_human_ground_truth:
    agent: human
    method: factual_review_only
    output: validated_corrections
    
  phase_5_translation:
    agent: kali
    method: jargon_to_generic_concepts
    output: actionable_search_queries
```

### As a Quality Gate

Every research plan must pass:
- [ ] **Jargon-Free Test**: Can a stranger execute the searches?
- [ ] **Reuse Audit**: What % of items have existing code?
- [ ] **Phantom Check**: Any "fix" that's already done?
- [ ] **Human Fact Check**: Any entity/file/path only human knows?
- [ ] **Compaction Survival**: Can anchored summary restore full context?

---

## Appendix: Version History

| Version | Date | Author | Key Change |
|---------|------|--------|------------|
| v1.0 | 2026-07-16 | Researcher | Initial 6-item plan (24h, enterprise patterns) |
| v2.0 | 2026-07-16 | Kali | Course correction (10h, cancelled waste) |
| v3.0 | 2026-07-17 | Kali (Meditate) | Round 2 collisions (7h, 7 locked decisions) |
| v3.0+ | 2026-07-17 | Researcher | Round 3 blind spots (9h, 6 corrections) |
| v3.0++ | 2026-07-17 | Human | arch correction (roc_racoon validated) |
| v4.0 | 2026-07-17 | Kali | Actionable queries (30 searches, jargon-free) |

---

## Closing Principle

> **The refinement process IS the product.**
> 
> The research plan v4.0 is valuable. But the *process that produced it* — the iterative human-AI oversight, the dialectical collision, the adversarial verification, the human ground truth, the jargon translation — that process is the institutional capability that compounds across every future research task.
> 
> Document the process. Template the process. Teach the process. The process is the sovereign asset.

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_kb_refinement_process ⬡ RATIFIED*
*This KB entry captures the meta-process. Use it as template for all future refinement cycles.*
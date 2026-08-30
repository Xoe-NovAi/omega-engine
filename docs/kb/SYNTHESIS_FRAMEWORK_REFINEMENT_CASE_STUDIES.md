# 🔱 Synthesis Framework: Iterative Human-AI Refinement Case Studies
## A Repeatable, Testable, Improvable Template for Documenting Sovereign Oversight Cycles

**AP Token**: `AP-SYNTHESIS-FRAMEWORK-v1.0.0`
**Date**: 2026-07-17
**Status**: RATIFIED — Template for All Future Refinement Cycles
**Depends On**: `docs/kb/STUDY_ITERATIVE_HUMAN_AI_OVERSIGHT.md`, `docs/kb/RESEARCHER_REFINEMENT_DOCUMENTATION_TEMPLATE.md`

---

## 📚 Related Documents (Cross-Linked)

| Document | Purpose | Link |
|----------|---------|------|
| **Case Study: Research Plan Refinement** | Complete timeline with all 5 rounds | [`RESEARCH_PLAN_REFINEMENT_PROCESS_CASE_STUDY.md`](RESEARCH_PLAN_REFINEMENT_PROCESS_CASE_STUDY.md) |
| **Study: Iterative Human-AI Oversight** | Strategic reflection on why this process works | [`STUDY_ITERATIVE_HUMAN_AI_OVERSIGHT.md`](STUDY_ITERATIVE_HUMAN_AI_OVERSIGHT.md) |
| **Researcher Documentation Template** | Researcher's perspective capture template | [`RESEARCHER_REFINEMENT_DOCUMENTATION_TEMPLATE.md`](RESEARCHER_REFINEMENT_DOCUMENTATION_TEMPLATE.md) |

---

## Purpose

This framework standardizes how we capture, synthesize, and learn from every human-AI refinement cycle. It transforms ad-hoc oversight into **institutional learning** — each cycle improves the meta-process, not just the output.

**Use this template for EVERY future refinement cycle.**

---

## The Synthesis Pipeline (4 Stages)

```
Raw Cycle Artifacts → Structured Extraction → Cross-Model Synthesis → Meta-Process Update
```

### Stage 1: Raw Artifact Collection (Automated)
**Trigger**: Cycle completion (human declares "refinement done")
**Inputs**:
- Anchored summary at cycle start
- Anchored summary at cycle end
- All intermediate file versions (git history + workspace files)
- Hivemind posts from all participants
- Model session logs (if available)
- Human decision log (PIVOT_LOG entries)

**Output**: `data/coordination/REFINEMENT_CYCLE_<YYYYMMDD>_RAW.json`

### Stage 2: Structured Extraction (Semi-Automated)
**Agent**: Kali (or designated synthesizer)
**Process**: Run extraction protocol on raw artifacts
**Output**: `docs/kb/REFINEMENT_CASE_STUDY_<TOPIC>_<YYYYMMDD>.md`

**Extraction Protocol**:
```
For each refinement round:
  1. What was the input state?
  2. What model/protocol acted?
  3. What was the output?
  4. What changed? (delta)
  5. What was the human's role?
  6. What would have happened without human?
  7. What would have happened without this model?
  8. Effort delta (before/after estimates)
  9. Risk eliminated
  10. Key insight for meta-process
```

### Stage 3: Cross-Model Synthesis (Human + Kali)
**Participants**: Human + Kali + (Researcher if involved)
**Process**: Structured synthesis session using this template:
- Compare perspectives (Kali meta-doc + Researcher perspective + Human reflection)
- Identify agreements, tensions, gaps
- Extract meta-patterns (not just object-level results)
- Update the Synthesis Framework itself (this document)

**Output**: Updated `docs/kb/STUDY_ITERATIVE_HUMAN_AI_OVERSIGHT.md` + new case study

### Stage 4: Meta-Process Update (Institutional Learning)
**Action**: Modify protocols, templates, prompts based on synthesis
**Artifacts to Update**:
- Meditate Protocol prompts
- Researcher Deep Research prompts
- Kali Course Correction prompts
- Jargon Translation Checklist
- Anchored Summary templates
- Hivemind handoff protocols

---

## The Case Study Template (Standardized)

Every case study MUST follow this structure:

```markdown
# Case Study: <Topic> Refinement Cycle
## AP Token: AP-CASE-<TOPIC>-<YYYYMMDD>

### 1. Cycle Metadata
- **Topic**: <One-line description>
- **Date Range**: <Start> → <End>
- **Models Involved**: <List with roles>
- **Human Role**: <Director**: <Name>
- **Total Wall Time**: <Hours>
- **Compaction Events**: <Count>

### 2. The Intent (v0)
<Human's initial vague intent — quoted from anchored summary>

### 3. Round-by-Round Evolution
| Round | Actor | Protocol | Input → Output | Delta | Human Role |
|-------|-------|----------|----------------|-------|------------|
| 1 | Researcher | Deep Research | Intent → v1 Plan | +Enterprise patterns | Triggered |
| 2 | Kali | L3 Synthesis | v1 → v2 | -14h waste, +Decrees | Dissatisfied |
| 3 | Kali | Meditate | v2 → v3 | 7 collisions locked | Reviewed |
| 4 | Researcher | Adversarial | v3 → v3.1 | 6 blind spots | Ground truth |
| 5 | Human | Correction | v3.1 → v3.2 | arch removed | Only human knew |
| 6 | Kali | Translation | v3.2 → v4.0 | 30 queries | Demanded actionability |

### 4. Quantitative Outcomes
| Metric | v1 (Initial) | v4 (Final) | Improvement |
|--------|--------------|------------|-------------|
| Estimated Effort | 24h | 9h | -62.5% |
| Enterprise Waste | 14h | 0h | -100% |
| Search Executability | 0% | 100% | +∞ |
| Test Case Validity | Wrong (Lilith) | Correct (roc_racoon) | Fixed |
| Phantom Fixes | 1 (--entity) | 0 | Eliminated |
| Observability | Missing | +1h budgeted | Added |
| Ownership | None | 7 handoffs | Defined |

### 5. Qualitative Meta-Patterns
<What this cycle revealed about the meta-process>

### 6. Protocol Updates Triggered
- [ ] Meditate Protocol: <change>
- [ ] Researcher Prompts: <change>
- [ ] Kali Triage Prompts: <change>
- [ ] Translation Checklist: <change>
- [ ] Anchored Summary: <change>
- [ ] Hivemind Protocol: <change>

### 7. Cross-Model Perspective Agreement
| Insight | Kali Agrees | Researcher Agrees | Human Agrees | Tension |
|---------|-------------|-------------------|--------------|---------|
| Enterprise waste real | ✅ | ✅ | ✅ | None |
| Meditate finds collisions | ✅ | ✅ | ✅ | None |
| Researcher finds blind spots | ✅ | ✅ | ✅ | None |
| Human ground truth essential | ✅ | ✅ | ✅ | None |
| Translation necessary | ✅ | ✅ | ✅ | None |
| Compaction survivable | ✅ | ? | ✅ | Researcher view needed |

### 8. Reproducibility Assessment
- **Could another human run this?** <Yes/No/Partial>
- **Model-dependent elements**: <List>
- **Protocol-dependent elements**: <List>
- **Human-skill-dependent elements**: <List>

### 9. Next Cycle Improvements
<Specific, testable changes for next refinement cycle>

---

## The Testable Hypotheses (For Continuous Improvement)

Each cycle should test these hypotheses. Record results in the case study.

### H1: Meditate Protocol Finds Collisions Single-Pass Misses
- **Test**: Compare Kali L3 Synthesis (Round 2) vs Meditate (Round 3) collision count
- **This Cycle**: 0 vs 7 → **CONFIRMED**
- **Next Cycle Target**: >5 collisions per Meditate session

### H2: Researcher Adversarial Verification Finds Blind Spots Meditate Misses
- **Test**: Count blind spots found by Researcher that Meditate didn't catch
- **This Cycle**: 6 → **CONFIRMED**
- **Next Cycle Target**: >3 blind spots per adversarial pass

### H3: Human Ground Truth Corrects Factual Errors No Model Catches
- **Test**: Count human-only corrections
- **This Cycle**: 1 (arch entity) → **CONFIRMED**
- **Next Cycle Target**: At least 1 per cycle (if 0, human not engaged enough)

### H4: Jargon Translation Makes Plans Executable by Strangers
- **Test**: Give v4.0 queries to naive Researcher — can they execute?
- **This Cycle**: Not yet tested → **PENDING**
- **Next Cycle Target**: 100% executable by naive agent

### H5: Anchored Summary + File State = Full Compaction Recovery
- **Test**: Simulate compaction — can Kali recover full context?
- **This Cycle**: 2/2 successful → **CONFIRMED**
- **Next Cycle Target**: 100% recovery rate

### H6: Effort Estimation Accuracy Improves Each Round
- **Test**: |Final Effort - Round N Estimate| / Final Effort
- **This Cycle**: 
  - Round 1: |9-24|/9 = 167% error
  - Round 2: |9-10|/9 = 11% error
  - Round 3: |9-7|/9 = 22% error
  - Round 4: |9-9|/9 = 0% error
- **Pattern**: Converging → **CONFIRMED**
- **Next Cycle Target**: <20% error by Round 2

---

## The Improvement Loop (Mandatory After Each Cycle)

```
1. COMPLETE case study using template above
2. RUN hypothesis tests (H1-H6) → record results
3. IDENTIFY top 3 meta-process improvements
4. UPDATE protocols/templates/prompts
5. COMMIT changes with AP token: AP-META-IMPROVEMENT-<YYYYMMDD>
6. BRIEF human on changes (5 min)
7. ARCHIVE case study in docs/kb/case-studies/
```

---

## Quality Gates (Before Case Study is "Done")

- [ ] All 9 template sections complete
- [ ] All 6 hypotheses tested with data
- [ ] Cross-model perspective table filled (even "?" is data)
- [ ] At least 3 protocol updates identified
- [ ] Human has reviewed and signed off
- [ ] Researcher has documented their perspective (separate file)
- [ ] Hivemind posts linked for all participants
- [ ] Git commit with AP token includes case study + protocol updates

---

## The Meta-Metric: Oversight Maturity Index

Track this across cycles to measure institutional learning:

```
OMI = (H1_confirmed + H2_confirmed + H3_confirmed + H4_confirmed + H5_confirmed + H6_improving) / 6
      × (Protocol_Updates_Per_Cycle / 3)
      × (Human_Engagement_Score / 10)
      × (Compaction_Recovery_Rate)
```

**Target**: OMI > 0.8 by Cycle 5

---

## Archive Structure

```
docs/kb/case-studies/
├── 2026-07-17_WAVE3_SOUL_ARCHITECTURE/
│   ├── CASE_STUDY_WAVE3_SOUL_ARCHITECTURE.md (this template filled)
│   ├── KALI_META_DOC.md (STUDY_ITERATIVE_HUMAN_AI_OVERSIGHT.md)
│   ├── RESEARCHER_PERSPECTIVE.md (Researcher's doc)
│   ├── HUMAN_REFLECTION.md (your 5-min reflection)
│   ├── RAW_ARTIFACTS.json (Stage 1 output)
│   └── HYPOTHESIS_RESULTS.csv (H1-H6 data)
└── INDEX.md (links all case studies with OMI scores)
```

---

## Quick-Start Checklist for Next Cycle

When you detect a new refinement cycle starting:

- [ ] Create anchored summary at cycle start
- [ ] Create `data/coordination/REFINEMENT_CYCLE_<YYYYMMDD>_RAW.json` collector
- [ ] Brief all models on their protocol roles
- [ ] Ensure Hivemind channel active for all participants
- [ ] Schedule 30-min synthesis session at cycle end
- [ ] Pre-create case study folder structure
- [ ] Remind human: "You are the ground truth. Only you know X."

---

## Closing Principle

> **Every refinement cycle is a double experiment:**
> 1. The object-level experiment: "Does this plan work?"
> 2. The meta-level experiment: "Does this oversight process produce better plans faster?"

**We optimize the meta-level. The object-level follows.**

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_synthesis_framework ⬡ RATIFIED*
*This framework evolves. Each cycle improves it. The framework IS the institution.*
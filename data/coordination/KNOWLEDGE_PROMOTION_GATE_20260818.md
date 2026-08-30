<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Knowledge Promotion Gate Mechanics — T1→T2 Workspace to Knowledge
**Date**: 2026-08-18
**Mission**: Deep Local Entity Specialization & Knowledge Management Discovery
**AP Token**: `AP-KNOWLEDGE-PROMOTION-GATE-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_mining ⬡ ACTIVE

---

## §1 Executive Summary

**The T1→T2 promotion gate (workspace → knowledge) is REFERENCED everywhere but NOT IMPLEMENTED as an automated system.**

Key findings:
1. **INDEX.yaml header comment** states: "Topics are promoted from workspace/ → knowledge/ via the T1→T2 gate" — but 4 of 7 entities have empty `topics: []`
2. **No automated promotion script exists** — promotion appears to be manual file copy + frontmatter addition
3. **SUBAGENT_DISPATCH_PROTOCOL.md** mandates "Absolute Disk-Reporting" (D-kal-170): ALL subagents MUST write deliverables to disk before returning control
4. **validate_tracking_state.py** enforces tracking integrity but NOT knowledge promotion
5. **validate_llm_docs.py** enforces documentation standards (frontmatter, answer-first, token budgets) but NOT workspace→knowledge promotion
6. **Research Index (08-research-index.md)** shows GAP-based promotion: research items resolve GAPs, then become knowledge

---

## §2 The Referenced but Unimplemented T1→T2 Gate

### 2.1 INDEX.yaml Header (Standard Comment)
```yaml
# data/entities/<entity>/knowledge/INDEX.yaml
# Entity knowledge discovery index
# Topics are promoted from workspace/ → knowledge/ via the T1→T2 gate
```

**Reality Check**: 
- doom_guy: `topics: []` (empty) — despite 8 knowledge files
- researcher: `topics: []` (empty) — despite MERMAID_RESEARCH_REPORT.md
- maat: `topics: []` (empty) — only INDEX.yaml exists
- quality: `topics: []` (empty) — only INDEX.yaml exists
- **Only roc_racoon has populated topics** with rich metadata

### 2.2 roc_racoon's Promoted Topics (The Only Working Example)
Each topic in roc_racoon's INDEX.yaml has:
```yaml
- id: rr-convergence-proof
  title: "Architectural Convergence Across 5 Eras"
  summary: "..."
  files: ["knowledge/CONVERGENCE_PROOF.md"]
  cross_references:
    - agent: doom_guy
      topic: dg-heritage-patterns
      relation: "confirms"
  applicability: [doom_guy, quality, maat]
  era: "Eras 1-6"
```
**Promotion metadata includes**: `promoted_from`, `promoted_at`, `insight_level`, `emergency` flag

---

## §3 SUBAGENT_DISPATCH_PROTOCOL.md — The Enforcement Mechanism

### 3.1 Mandatory Disk-Reporting (D-kal-170) — §1 Rule 4
> **ALL subagents MUST write their final deliverables and reports to disk** (`data/entities/<agent>/workspace/` or `data/coordination/`) before returning control to the parent agent. Returning reports solely via transient CLI chat is a violation of Mandate 11 (Soul Integrity) and Mandate 15 (Sovereign Continuity).

### 3.2 HandoffPacket Schema — §2
**Required fields for knowledge capture**:
- `expected_output`: "What the subagent must produce and write to disk"
- `relevant_files`: Files for supplementary reference
- `context`: **Inline context** — actual file excerpts, key findings, prior decisions (NOT file paths)

### 3.3 Inline Context Quality Checklist — §4 Step 3
- [ ] Every critical file was read and its key findings extracted
- [ ] No prompt says "see file" without summarizing the content
- [ ] Decision IDs (D-NNN) are stated explicitly, not referenced
- [ ] Code/config patterns are shown as inline examples, not file paths

### 3.4 Experience Table — §8a
| Context Delivery | Result | Root Cause |
|------------------|--------|------------|
| Reference only: "see docs/research/R_*.md" | ❌ Empty task result | Subagent couldn't read files by path |
| Inline: All 6 source docs embedded | ✅ Temple-Grade (544 lines + 11 L3 proposals) | Inline content enabled proper tool use |

**Critical Lesson**: Knowledge transfer to subagents REQUIRES inline context embedding. File paths alone fail.

---

## §4 SUBAGENT_STATE_STRATEGY.md — The Proposed (Stale) Mechanism

**Status**: 🔴 STALE — Legacy document from pre-June 2026

### 4.1 The Gnosis File (`session_gnosis.md`)
Proposed structure:
- `CURRENT GOAL` — Primary task + immediate next step
- `WORKING STATE (KV Memory)` — variable_name: value/finding
- `AUDIT TRAIL (Timeline)` — timestamp | agent_id | action → result
- `RESOLVED / DECIDED` — Decisions and facts
- `OPEN GAPS / UNCERTAINTIES` — Unresolved questions

### 4.2 Read/Write Protocol
1. **Read (Injection)**: Orchestrator reads Gnosis File before dispatch, injects into subagent system prompt
2. **Write (Update)**: Subagents return **State Update Block** in final response:
   ```
   STATE_UPDATE:
   - ADD_RESOLVED: "tui.json is missing"
   - UPDATE_GOAL: "Search for TUI config in ~/.config/opencode"
   - LOG: "Searched .opencode folder, found no JSON configs."
   ```
3. Orchestrator (single writer) parses and updates `session_gnosis.md`

### 4.3 Soul-Injection Pattern
Final subagent prompt = `[Entity Soul Prompt] + [Task Instructions] + [Current Session Gnosis] + [Behavioral Constraints]`

### 4.4 Prevention of Context Erosion
- Semantic Compression: Compaction Pass when AUDIT TRAIL exceeds N lines
- Priority-Based Injection: CURRENT GOAL + RESOLVED always injected
- State-Sourced Prompting: "Refer to RESOLVED section to avoid repeating failed attempts"

### 4.5 Implementation Roadmap (Never Built)
| Phase | Action | Owner |
|-------|--------|-------|
| 1. Infrastructure | Implement `GnosisManager` for file I/O and atomic updates | Builder |
| 2. Integration | Update `Orchestrator.dispatch_agent` to inject Gnosis content | Builder |
| 3. Feedback Loop | Implement `STATE_UPDATE` parsing logic in return chain | Builder |
| 4. Optimization | Add "Compaction Pass" trigger for long-running sessions | Builder |

---

## §5 validate_tracking_state.py — Tracking Integrity (M27)

**Validates**: 5-Tier Tracking Architecture (TRACKING_ARCHITECTURE.md)

### 5.1 Tier-0 (ACTIVE_SPRINT.json) — Planning
- Allowed statuses: `backlog`, `ready`, `in_progress`, `blocked`, `completed`, `superseded`
- **R-ID cross-check**: Every subtask referencing GAP-XX must have that gap registered in GAP_REGISTRY.json

### 5.2 Tier-3 (TASK_REGISTRY.json) — Execution Records
- Allowed statuses: Tier-0 statuses PLUS `failed`
- **Cross-tier validation**: Tier-3 `failed` must sync to Tier-0 `blocked` or `superseded`

### 5.3 GAP_REGISTRY.json
- Allowed statuses: `resolved`, `outstanding`, `partial`, `lost`
- Duplicate topic detection

**Does NOT validate**: Knowledge promotion, workspace→knowledge flow, INDEX.yaml topic population

---

## §6 validate_llm_docs.py — Documentation Standards (M26)

**Validates**: LLM-friendly documentation against standards

### 6.1 Checks Performed
1. **Frontmatter Schema** — YAML frontmatter against JSON schema (required fields: schema_version, document_type, document_id, version, title, ap_token, date, sprint, status, owner, priority, tags, depends_on, blocks, acceptance_gates, cross_references, llm_metadata)
2. **Answer-First Sections** — Each ## section must start with answer-first patterns (`**What**:`, `**Why**:`, `**Acceptance**`, `**Dependencies**`, `**Owner**`, `**Estimated**`, `## What`, `## Why`)
3. **Self-Contained Code Blocks** — Python: imports/defs/class or `# File:` comment; Bash: shebang or `# File:`
4. **Dependency Graph** — Mermaid diagram + YAML dependencies
5. **Token Budget** — Against budgets per doc_type (sprint_plan: 16K hard, 12.8K soft, 8K target)

### 6.2 Doc Types & Budgets
| Doc Type | Hard Limit | Soft Limit | Target |
|----------|------------|------------|--------|
| reference_doc | 16000 | 12800 | 8000 |
| sprint_plan | 16000 | 12800 | 8000 |
| ticket_page | 8000 | 6400 | 4000 |
| research_index | 16000 | 12800 | 8000 |

**Does NOT validate**: Workspace→knowledge promotion, INDEX.yaml population, T1→T2 gate

---

## §7 Research Index Promotion Mechanics (08-research-index.md)

### 7.1 Gap-Driven Promotion
Research items (R-GD-01 through R-GD-06) map to Knowledge Gaps (GAP-01 through GAP-06):
| GAP | Description | Source | Research Item |
|-----|-------------|--------|---------------|
| GAP-01 | Optimal quota allocation | C-10.5 | R-GD-01 |
| GAP-02 | Property-based test patterns | C-11 | R-GD-02 |
| GAP-03 | VaultCore credential lifecycle | V-1 | R-GD-03 |
| GAP-04 | Restic repo layout for AI state | C-3 | R-GD-04 |
| GAP-05 | L1→L2→L3 distillation automation | C-0.5 | R-GD-05 |
| GAP-06 | GenerationPolicy schema | C-9 | R-GD-06 |

### 7.2 Promotion Flow
1. **Gap identified** → Registered in GAP_REGISTRY.json
2. **Research item created** → Tracked in research index with status (IN_PROGRESS, BLOCKED, PENDING)
3. **Research completed** → Documented findings in R-doc
4. **Gap resolved** → Status updated to `resolved` in GAP_REGISTRY
5. **Knowledge promoted** → ??? (No automated step documented)

### 7.3 Machine-Readable Dependencies
Both Mermaid diagram AND YAML dependencies in research index:
```yaml
knowledge_gaps:
  - id: GAP-01
    name: Optimal quota allocation across providers
    priority: P0
    source: C-10.5
```

---

## §8 The Actual Promotion Process (Reverse-Engineered)

Based on roc_racoon's working example and SUBAGENT_DISPATCH_PROTOCOL:

### 8.1 Manual Promotion Steps (Current Reality)
1. **Subagent completes work** → Writes deliverable to `data/entities/<entity>/workspace/` (mandatory per D-kal-170)
2. **Parent agent reviews** → Validates quality, extracts L1→L2→L3 insights
3. **Manual promotion** → Copy file to `data/entities/<entity>/knowledge/`, add frontmatter:
   ```yaml
   ---
   title: "..."
   domain: "..."
   era: "..."
   applicability: [...]
   promoted_from: "workspace/mining_reports/XX_..."
   promoted_at: "2026-XX-XX"
   insight_level: "L2"
   ---
   ```
4. **Manual INDEX update** → Add topic entry to INDEX.yaml (only roc_racoon does this)

### 8.2 Missing Automation
- No script detects workspace files ready for promotion
- No validation that promoted files have required frontmatter
- No automatic INDEX.yaml topic population
- No cross-reference validation (topic cross_references → target entity INDEX)

---

## §9 Scribe Agent — The Distillation Pipeline (C-0.5)

### 9.1 Scribe's Role (from scribe.md)
- **M5 Gnosis Preservation**: L1→L2→L3 pipeline mandatory every session
- **M11 Soul Integrity**: `proposed_lessons.yaml` blind staging (NOT direct to soul.yaml)
- **M18 Token Efficiency**: Concise distillation
- **M22 Response Provenance**: Record actual model used

### 9.2 Three-Tier Distillation
| Tier | Name | Input | Output | Purpose |
|------|------|-------|--------|---------|
| **L1** | Narrative | Raw session exchanges | Structured narrative | What happened? |
| **L2** | Insight | L1 narrative | Pattern insights | What does this mean? |
| **L3** | Universal Principle | L2 insights | Timeless principles | What is the timeless truth? |

### 9.3 Output: proposed_lessons.yaml (Blind Staging)
```yaml
proposals:
  - lesson_id: "l3-20260722-001"
    tier: "L3"
    principle: "Sovereign execution requires explicit workspace locks..."
    evidence: ["C-4a handoff accepted without lock caused race", "..."]
    confidence: 0.95
    source_sessions: ["ses_a96aef94239a"]
    mandate_refs: ["M4", "M23"]
```

### 9.4 Session Hook Integration
```python
# In OpenCode session end hook:
from omega.scribe import SoulDistiller
distiller = SoulDistiller(entity_name="kali", session_id="ses_xxx")
distiller.distill_session()  # Writes proposed_lessons.yaml
```

**This is the CLOSEST thing to automated promotion** — but it promotes to `proposed_lessons.yaml` (staging), not to `knowledge/`.

---

## §10 Summary: What Exists vs. What's Needed

| Component | Status | Location |
|-----------|--------|----------|
| **T1→T2 Gate Concept** | ✅ Documented in INDEX.yaml headers | All knowledge/INDEX.yaml |
| **Workspace Writing** | ✅ Enforced via D-kal-170 | SUBAGENT_DISPATCH_PROTOCOL.md |
| **Inline Context Delivery** | ✅ Enforced (critical lesson) | SUBAGENT_DISPATCH_PROTOCOL.md §0, §8a |
| **Gnosis File (session_gnosis.md)** | ⚠️ Proposed, not implemented | SUBAGENT_STATE_STRATEGY.md |
| **Soul Distillation (L1→L2→L3)** | ✅ Implemented in Scribe agent | scribe.md, src/omega/scribe/distiller.py |
| **Blind Staging (proposed_lessons.yaml)** | ✅ Implemented | Scribe agent |
| **Automated Workspace→Knowledge Promotion** | ❌ NOT IMPLEMENTED | — |
| **INDEX.yaml Topic Population** | ❌ Manual only (roc_racoon only) | — |
| **Cross-Reference Validation** | ❌ NOT IMPLEMENTED | — |
| **Tracking State Validation** | ✅ Implemented (M27) | validate_tracking_state.py |
| **Doc Standards Validation** | ✅ Implemented (M26) | validate_llm_docs.py |

---

## §11 The Real Promotion Pipeline (As Implemented)

```
Subagent Workspace (T1)
    │
    ▼ (Mandatory disk write — D-kal-170)
data/entities/<entity>/workspace/*.md
    │
    ▼ (Manual review + L1→L2→L3 extraction)
Parent Agent / Scribe Distillation
    │
    ▼ (Blind staging — M11)
data/entities/<entity>/proposed_lessons.yaml
    │
    ▼ (User approval)
data/entities/<entity>/approved_lessons.yaml → soul.yaml lessons
    │
    ▼ (Manual copy + frontmatter)
data/entities/<entity>/knowledge/*.md
    │
    ▼ (Manual INDEX update)
data/entities/<entity>/knowledge/INDEX.yaml
```

**The automation gap**: Steps 3→4 and 5→6 are manual. Only Scribe's distillation (step 2→3) is automated.

---

## §12 Files Referenced

- `/data/entities/*/knowledge/INDEX.yaml` (7 entities)
- `/docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md`
- `/docs/research/SUBAGENT_STATE_STRATEGY.md`
- `/scripts/validate_tracking_state.py`
- `/scripts/validate_llm_docs.py`
- `/docs/archive/sprints/2026-07-25-guard-and-distill/08-research-index.md`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/agents/scribe.md`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/scribe/distiller.py` (referenced in scribe.md)
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

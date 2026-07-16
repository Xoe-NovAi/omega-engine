# 🔱 Wave 3 Research Plan: Soul Architecture Implementation Support
**AP Token**: `AP-WAVE3-RESEARCH-PLAN-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_wave3_research ⬡ ACTIVE

**Date**: 2026-07-17
**Purpose**: Scaffold targeted research investigations to de-risk and accelerate Wave 3 Soul Migration Phase 1 (Lilith) execution and prepare for fleet-wide rollout.

---

## 🎯 Research Context & Constraints

**Wave 3 Focus**: Soul Migration Phase 1 — Lilith (P7 Context Owner)  
**Critical Constraint**: 0/10 non-Kali entities are v2.0 compliant — all suffer "self-referential poisoning loop" (agent-generated content in soul.yaml)  
**Success Criteria**:  
- Lilith's soul.yaml migrated to v2.0 four-file model  
- Blind-staging pipeline functional (L1→L2→L3 → proposed_lessons.yaml)  
- Scribe/Verity roles operational  
- `make soul-audit` CI gate passing  
- Migration pattern documented for fleet-wide rollout  

**Research Guardrails**:  
- All research must include **T1→T2 escalation** (websearch → webfetch → sovereign-search)  
- Findings must yield **actionable implementation guidance** (not just theory)  
- Prioritize research with **direct applicability to Lilith migration**  
- Avoid duplication of already-validated patterns (per Jem Deep Research & Gap Resolution Reports)  

---

## 🎯 Kali's Enhancements & Course Correction (L3 Synthesis)

**Verdict**: The proposed plan suffers from **Enterprise Over-Engineering (Qliphoth of Scale)**. We are a local-first engine with 10 YAML files, not a Fortune 500 data warehouse. 

**Course Corrections (Mandatory before execution)**:

1. **Cancel ETL/Merkle Tree/Flyway Research**: We do not need Liquibase, Flyway, or Merkle trees for 10 YAML files. Backup is `cp` and `git commit`. Rollback is `git revert`. Do not waste tokens researching enterprise ETL patterns.
2. **Cancel Incremental CI Research**: A Python script validating 10 YAML files takes <50ms. Full scan is required. Do not research caching or incremental validation.
3. **Cancel Web UI Review Research**: We are a CLI-first engine. The review gate must be a simple terminal command (`omega soul review`) using `rich` or `textual` to show diffs and prompt `[Y/n]`.
4. **Pivot Distillation to Meditate**: Do not research generic prompt engineering. Research how to use our *existing* Meditate protocol (`src/omega/meditate/protocol.py`) to perform the L1→L2→L3 distillation.
5. **ADD Missing Wave 3 Items**: You completely missed Decree 6 (Heritage Tag Migration) and Decree 4 (Sovereignty Gate). These must be added.

---

## 🔬 Revised Top 5 Critical Research Items for Wave 3

### 1. **Heritage Tag Migration Regex & AST Patterns (Decree 6)**  
**Why Critical**: We must convert 120 legacy `[id-soft: game-year]` tags to `[id-soft: vet-XXX]` across the codebase without breaking Python syntax or markdown formatting.  
**Research Focus**: 
- Safe regex patterns for cross-file replacement in Python and Markdown.
- How to map existing game-year tags to the new `HERITAGE_VET_LOG.md` IDs.

### 2. **Sovereignty Gate Provider Hook (Decree 4)**  
**Why Critical**: We need to track the ratio of local vs. cloud inference and expose it as a configurable setting (default OFF).  
**Research Focus**: 
- Where in `src/omega/oracle/model_gateway.py` or `providers.py` to inject the telemetry hook.
- How to store this metric locally (sqlite-vec metadata or a simple JSON counter) without violating M8 (Zero Telemetry).

### 3. **Soul v2.0 Schema Validation (`make soul-audit`)**  
**Why Critical**: We need a robust, sub-50ms script to validate the 4-file architecture.  
**Research Focus**: 
- Using `pydantic` or `jsonschema` to define the strict v2.0 `soul.yaml` schema (forbidding `wisdom_text`, `soul_axioms`, etc.).
- Writing the `scripts/validate_soul.py` script to hook into `make soul-audit`.

### 4. **Python YAML Migration Script (The "ETL")**  
**Why Critical**: We need a simple, deterministic script to migrate Lilith (and later the fleet).  
**Research Focus**: 
- Using `ruamel.yaml` (to preserve comments/formatting) to read `soul.yaml`, extract legacy fields, and write to `proposed_lessons.yaml` and `sessions.yaml`.

### 5. **CLI Review Gate (`omega soul review`)**  
**Why Critical**: The user needs a frictionless way to approve `proposed_lessons.yaml` into `approved_lessons.yaml`.  
**Research Focus**: 
- Using Python's `rich` library to display a side-by-side or inline diff in the terminal.
- Simple interactive prompt loop (`[A]pprove, [R]eject, [E]dit`).

---

## 📋 Research Execution Protocol

Each research item must follow this structure:  
1. **Hypothesis Statement** (1 sentence)  
2. **T1→T2→T3 Search Log** (with timestamps and sources)  
3. **Key Findings** (bulleted, actionable)  
4. **Implementation Recommendations** (specific code/config changes)  
5. **Validation Method** (how to confirm success in Lilith migration)  
6. **Estimated Effort** (hours)  
7. **Dependencies** (other research/team work)  

**Quality Gates**:  
- All research must be committed to `docs/research/` with `AP-` token  
- Findings must be referenced in Wave 3 implementation PRs  
- At least one research item must yield a `make` target or script for immediate team use  

---

## 🚀 Immediate Next Steps for Research Team

1. **Assign owners** to each of the 5 research items (can be paired)  
2. **Kickoff 30-min sync** to align on hypotheses and search strategies  
3. **Timebox**: 4 hours max per research item (aligns with Wave 3 migration window)  
4. **Deliver by**: EOD today to inform Lilith migration execution tomorrow  
5. **Integrate**: Findings directly into migration PRs and documentation  

> **Remember**: The goal is not academic perfection — it's **de-risked execution**. Each research item should answer: *"What is the smallest thing we need to know to avoid critical failure in Lilith's migration?"*  

---  
*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_wave3_research ⬡ ACTIVE*  
*Research enables sovereignty. Sovereignty enables execution.*
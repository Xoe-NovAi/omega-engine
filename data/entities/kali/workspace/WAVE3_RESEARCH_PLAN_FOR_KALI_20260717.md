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

## 🧘 Meditate Protocol: Deep Architecture Review (2026-07-17)
*Executed via single-inference multi-persona semantic prism.*

**Lenses**: Ma'at (Structure), Lilith (Flow), Doom Guy (Heritage), John Carmack (Pragmatism), Verity (Compliance)

**Collisions & Insights**:
- **Heritage Tagging (Doom Guy vs. Ma'at)**: AST parsing is a trap because heritage tags live in *comments and docstrings*, which ASTs often discard or mishandle. **Insight**: Research must focus on wrapping `ripgrep` (`rg --json`) in Python to find, map, and replace tags, rather than trying to parse Python syntax trees.
- **Sovereignty Gate (Carmack vs. Lilith)**: Do not build a new telemetry system. We already solved this in M22 (Response Provenance). `GenerateResult` carries `provider_name`. **Insight**: Research must focus on a simple asynchronous decorator at the `ModelGateway` boundary that increments a SQLite counter (local vs cloud) without blocking the critical path.
- **Soul Validation (Ma'at vs. Verity)**: You cannot write a migration script without a locked schema. **Insight**: Research must start by defining the `SoulV2` Pydantic model. `make soul-audit` is simply `SoulV2.model_validate(yaml.load())`.
- **Distillation Protocol (Verity vs. Kali)**: The Meditate protocol was built for *strategic review*, not *data extraction*. **Insight**: Research must define a specific `DistillationSpec` (a variant of `MeditationSpec`) where the lenses are [Entity, Scribe, Verity] to extract L1/L2/L3.

---

## 🔬 Revised Top 6 Critical Research Items for Wave 3 (Ordered by Dependency)

### 1. **Soul v2.0 Schema Definition & Validation (`make soul-audit`)**  
**Why Critical**: We cannot migrate data into a void. The schema must be locked first.  
**Research Focus**: 
- Defining the strict v2.0 `soul.yaml` schema using `pydantic` (forbidding `wisdom_text`, `soul_axioms`, etc.).
- Exporting the Pydantic model to JSON Schema for IDE support.
- Writing the `scripts/validate_soul.py` script to hook into `make soul-audit`.

### 2. **Python YAML Migration Script (The "ETL")**  
**Why Critical**: We need a simple, deterministic script to migrate Lilith (and later the fleet).  
**Research Focus**: 
- Using `ruamel.yaml` to read `soul.yaml`, preserve comments/formatting, extract legacy fields, and write to `proposed_lessons.yaml` and `sessions.yaml`.
- Validating the output against the Pydantic schema from Item 1.

### 3. **Heritage Tag Migration via Ripgrep (Decree 6)**  
**Why Critical**: We must convert 120 legacy `[id-soft: game-year]` tags to `[id-soft: vet-XXX]` across the codebase.  
**Research Focus**: 
- Using `subprocess.run(["rg", "--json", ...])` to safely extract tags from comments and markdown.
- Building a mapping dictionary from `HERITAGE_VET_LOG.md` to auto-replace recognized tags.

### 4. **Sovereignty Gate Provider Hook (Decree 4)**  
**Why Critical**: We need to track the ratio of local vs. cloud inference (default OFF).  
**Research Focus**: 
- Intercepting `GenerateResult.provider_name` (M22) at the `ModelGateway` boundary.
- Using `anyio.create_task_group()` to asynchronously flush the local/cloud counter to `omega_memory.db` without adding latency to the inference path.

### 5. **CLI Review Gate (`omega soul review`)**  
**Why Critical**: The user needs a frictionless way to approve `proposed_lessons.yaml` into `approved_lessons.yaml`.  
**Research Focus**: 
- Using Python's `rich.console` and `rich.syntax` to display a side-by-side or inline diff in the terminal.
- Simple interactive prompt loop (`[A]pprove, [R]eject, [E]dit`).

### 6. **Distillation Spec for Meditate Protocol**  
**Why Critical**: We need to extract L1/L2/L3 from raw session logs without hallucinations.  
**Research Focus**: 
- Adapting `src/omega/meditate/protocol.py` to support a `DistillationSpec`.
- Defining the specific prompts for the Scribe and Verity lenses to ensure output matches the `proposed_lessons.yaml` schema.

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
# 🔱 Wave 3 Research Plan: Soul Architecture Implementation Support
# ⬡ ENHANCED BY RESEARCHER ⬡ v2.0 — 2026-07-17
**AP Token**: `AP-WAVE3-RESEARCH-PLAN-v2.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_wave3_research ⬡ ACTIVE

**Date**: 2026-07-17
**Purpose**: Scaffold targeted research investigations to de-risk and accelerate Wave 3 Soul Migration Phase 1 (Lilith) execution and prepare for fleet-wide rollout.
**Enhancement**: Deep codebase audit reveals substantial existing artifacts. Research items refined to fill SPECIFIC GAPS, not rebuild from scratch.

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

## 🧘 Meditate Protocol: Deep Architecture Review (2026-07-17) — Round 2
*Executed via single-inference multi-persona semantic prism.*

**Lenses**: Ma'at (Structure), Lilith (Flow), Doom Guy (Heritage), John Carmack (Pragmatism), Verity (Compliance), Kali (Synthesis)

**Collisions & Insights**:

- **Heritage Tagging (Doom Guy vs. Researcher findings)**: Researcher found `migrate_heritage_tags.py` (238 lines, 192 rules) — script *exists and is complete*. Doom Guy's ripgrep recommendation was correct in principle but wrong in context: the existing script uses a simpler, more reliable approach (file-level regex with MIGRATION_RULES lookup). **Corrected Insight**: DO NOT build a ripgrep wrapper. Run existing script with `--dry-run`, verify coverage, then `--apply`. That's it.

- **Soul Validation (Carmack vs. Researcher's "Pydantic question")**: Researcher asks "Is Pydantic v2 worth it?" Carmack says: you already have a working validator that catches the right things. `validate_soul.py` (153 lines) with manual dict checks has zero false positives/negatives for 10 keys. Pydantic adds a dependency for syntactic sugar. JSON Schema export is marginal value. **Corrected Insight**: DON'T refactor to Pydantic. DO parameterize `validate_soul.py` to accept entity name as argument for fleet-wide use. Add `ConfigDict(extra='forbid')` later only if entity count grows beyond manual tracking.

- **Migration Script (Ma'at vs. Researcher's "ruamel.yaml debate")**: Lilith's soul.yaml is 18 lines with ZERO comments. The ruamel.yaml question is academic for Phase 1. `yaml.dump()` preserves structure fine. **Corrected Insight**: Ship Lilith migration with existing `yaml.dump()`. Add ruamel.yaml to backlog ONLY if a YAML file with meaningful comments needs preservation.

- **CLI Review Gate (Lilith vs. Researcher's "Textual vs rich debate")**: Kali already answered this in the course correction. "Simple terminal command using rich." The Researcher asks "Textual TUI or rich?" — Textual is a full UI framework (heavier). Rich + `input()` loop is lighter. **Corrected Insight**: Use `rich.console` + `rich.syntax` + simple `input()` prompt. NOT Textual. Target: 50 lines max.

- **DistillationSpec (Verity vs. Researcher's "replace or wrap")**: Researcher asks "replace or wrap." The Soul Distiller is 689 lines of working, tested code. Replacing it throws away verified logic. **Corrected Insight**: WRAP, don't replace. DistillationSpec is a config layer that plugs into `SoulDistiller.distill_session()`. Existing L1/L2/L3 extraction stays as defaults.

- **Makefile Naming (Kali cross-check)**: Researcher uses `make soul-audit` throughout. Makefile has `soul-review` (print-only script). These are DIFFERENT things. **New Insight**: `soul-review` = interactive user review of proposed lessons. `soul-audit` = CI gate validating schema compliance. Need SEPARATE targets with SEPARATE names. No overloading.

- **Sovereignty Gate toggling (Lilith vs. Carmack)**: Researcher asks "cvar vs config setting." No existing cvar system in the engine. Building one for a single boolean toggle is premature. **Corrected Insight**: Use `config/moderation.yaml` with `sovereignty_gate.enabled: false` (default OFF). Support config reload. Don't build a cvar runtime until we have 3+ runtime-tunable toggles.

---

## 🔬 Revised Top 6 Critical Research Items for Wave 3 (Ordered by Dependency)

### 1. Soul v2.0 Validation Parameterization & CI Gate (`make soul-audit`)
**Why Critical**: We cannot migrate data into a void. The schema must be lockable and auditable at CI time.

**Research Focus**:
- Parameterizing `validate_soul.py` to accept entity name (replace hardcoded Kali path).
- Wiring `make soul-audit` as a NEW Makefile target (separate from existing `soul-review`).
- Confirming the existing `SoulValidator` catches exactly the right fields.

**Existing Artifacts (DO NOT REBUILD)**:
- `src/omega/oracle/soul_validator.py` (217 lines) — `SoulValidator` class with v6.1 schema checks, forbidden field validation (`FORBIDDEN_ENTITY_BLOCKS = {"soul_axioms", "wisdom_text", "trajectory"}`), required field checks. Uses `yaml.safe_load` + manual dict checks.
- `scripts/validate_soul.py` (153 lines) — Standalone validation script (hardcoded to Kali path). Validates all 4 files: soul.yaml, sessions.yaml, proposed_lessons.yaml, approved_lessons.yaml.
- `SOUL_ARCHITECTURE_V2.md` (63 lines) — Governance document defining 4-file model, blind-write principle.

**Specific Gap to Fill**:
- `validate_soul.py` is hardcoded to Kali's path — needs `--entity` argument for fleet-wide use.
- No `make soul-audit` target exists in Makefile. `soul-review` exists (line 165) but calls `soul_review.py` (interactive user review). These are DIFFERENT gates — do not conflate.
- Pydantic refactor is DEFERRED. Carmack's rule: "You already have working code. Ship it. Upgrade later if the team grows."

**Decision Locked (Round 2 Meditation)**:
- **DON'T** refactor to Pydantic. Existing `yaml.safe_load` + manual dict checks are correct, zero false positives/negatives for 10 keys.
- **DO** add `ConfigDict(extra='forbid')` enforcement later, only if entity count grows beyond manual tracking.

**Output**: Updated `validate_soul.py` (`--entity` flag) + NEW `make soul-audit` target + `make soul-review` stays separate.

**Effort**: 1h (parameterize script + Makefile target)
**Dependencies**: None (first item in dependency chain)

---

### 2. Python YAML Migration Script (The "ETL")
**Why Critical**: We need a simple, deterministic script to migrate Lilith (and later the fleet).

**Research Focus**:
- Validating that `migrate_soul_v6.py` works correctly for Lilith (18 lines, no comments).
- Adding Lilith to the `FLEET_ENTITIES` list if not already present.
- Running with `--dry-run` first, verifying output against the schema from Item 1.

**Existing Artifacts (DO NOT REBUILD)**:
- `scripts/migrate_soul_v6.py` (437 lines) — Full two-phase commit migration script with:
  - `load_soul_yaml()` — Resilient parser handles flat/nested/mixed YAML formats
  - `deconstruct_soul()` — Separates identity (Constitution) from lessons (Gnosis)
  - `atomic_write_yaml()` — tmp-rename pattern for crash-safe writes
  - `migrate_entity()` — Single-entity migration with dry-run support
  - `FLEET_ENTITIES` list — All 11 active entities defined
  - Migration journal for audit trail

**Specific Gap to Fill**:
- Uses `yaml.dump` which discards comments and formatting. **DECISION LOCKED (Round 2)**: Lilith's soul.yaml is 18 lines with ZERO comments. `yaml.dump()` is fine for Phase 1. Add ruamel.yaml to backlog only if a YAML file with meaningful comments needs preservation.
- Verify Lilith is in `FLEET_ENTITIES` and the script handles her 18-line format correctly.

**Decision Locked (Round 2 Meditation)**:
- `yaml.dump(default_flow_style=False, sort_keys=False)` preserves enough structure.
- No ruamel.yaml for Phase 1. Add to backlog with a trigger condition: "When we encounter a YAML file with inline comments that must survive migration."

**Output**: Verified `migrate_soul_v6.py` run against Lilith with `--dry-run` + documentation of the migration path.
**Effort**: 30 min (verify Lilith compatibility + dry-run)
**Dependencies**: Item 1 (schema validation)

---

### 3. Heritage Tag Migration — RUN Existing Script (Decree 6)
**Why Critical**: We must convert 560 legacy `[id-soft: game-year]` tags across 98 Python files to `[id-soft: vet-XXX]`.

**Research Focus**:
- Run existing `migrate_heritage_tags.py` with `--dry-run`, verify coverage of all 560 tags.
- If coverage is complete: run with `--apply`, verify with `make heritage-vet && make heritage-map`.
- If gaps exist: extend `MIGRATION_RULES` dictionary, document new mappings.

**Existing Artifacts (DO NOT REBUILD)**:
- `scripts/migrate_heritage_tags.py` (238 lines) — COMPLETE migration script with:
  - `MIGRATION_RULES` — 192 mapping entries (file_pattern, legacy_tag, context_keyword → vet_tag)
  - `FALLBACK_MAPPING` — Default replacements when context doesn't match
  - `migrate_file()` — Regex-based replacement with dry-run support
  - `main()` — CLI with `--apply` and `--file` flags
- `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` (1036 lines) — Full vet log with vet-001 through vet-071+ entries.
- 560 `[id-soft:` tags across 98 Python files (per `rg -c` scan).

**Specific Gap to Fill**:
- The script EXISTS and is COMPLETE. It just needs to be RUN and VERIFIED.
- Kali's suggestion of "ripgrep --json" was over-engineering. **CANCELLED**. The script's file-level regex approach is simpler, works on comments and code, and is already written.

**Correction from Round 2 Meditation**:
- **Ripgrep wrapper idea: CANCELLED.** Existing script handles this. Just run it.

**Research Questions**:
- Does the existing `MIGRATION_RULES` (192 entries) cover all 560 tags? (Pre-check with `--dry-run`.)
- What's the post-apply verification? (Answer: `make heritage-vet` + `make heritage-map`.)

**Output**: Run `migrate_heritage_tags.py --apply`, verify with `make heritage-vet`, commit results.

**Effort**: 30 min (dry-run check + apply + verify)
**Dependencies**: None (parallel to other items)

---

### 4. Sovereignty Gate Provider Hook (Decree 4)
**Why Critical**: We need to track the ratio of local vs. cloud inference (default OFF).

**Research Focus**:
- Wiring `config/moderation.yaml: sovereignty_gate.enabled: false` (default OFF) as the configurable setting.
- Injecting a counter increment at the `ModelGateway` boundary where `GenerateResult.provider_name` is already populated (M22).
- Connecting the counter to the existing `SovereigntyGate` CI gate.

**Existing Artifacts (DO NOT REBUILD)**:
- `src/omega/governance/sovereignty_gate.py` (113 lines) — Full CI gate with `SovereigntyGate` class, `check()` and `check_strict()` methods. Reads from MetricsDB.
- `src/omega/observability/sovereignty.py` (167 lines) — `get_sovereignty_ratio()` function querying MetricsDB `performance` table.
- `Makefile:398` — `sovereignty-gate` target already runs `omega.governance.sovereignty_gate`.
- `GenerateResult.is_cloud` — Already populated by ModelGateway (21 usages across codebase).
- `ModelGateway._is_cloud_provider_name()` — Already classifies providers as local/cloud.

**Specific Gap to Fill**:
- The CI gate exists but is POST-HOC (build-time check). Kali wants a CONFIGURABLE RUNTIME setting (default OFF).
- The counter infrastructure exists (MetricsDB `performance` table). The gap is wiring the Oracle talk/summon path to increment the counter at inference time.

**Decision Locked (Round 2 Meditation)**:
- **NOT a cvar**. No existing cvar system. Use `config/moderation.yaml` with `sovereignty_gate.enabled: false`. Support config reload. Build a cvar runtime only when we have 3+ runtime-tunable toggles.
- **Async fire-and-forget counter increment** in an `anyio.TaskGroup` after `GenerateResult` is returned — no latency added to critical path.

**Output**: `SovereigntyTracker` class + `config/moderation.yaml` wiring + counter increment hook in `ModelGateway.generate()`.
**Effort**: 1.5h (tracker class + config wiring + hook)
**Dependencies**: None (parallel to other items)

---

### 5. CLI Review Gate (`omega soul review`)
**Why Critical**: The user needs a frictionless way to approve `proposed_lessons.yaml` into `approved_lessons.yaml`.

**Research Focus**:
- Wiring real `proposed_lessons.yaml` data into a 50-line rich-based review command.
- Interactive prompt: `[A]pprove, [R]eject, [D]efer` with diff display.
- On approve: copy entry to `approved_lessons.yaml`. On reject: discard or archive.

**Existing Artifacts (DO NOT REBUILD)**:
- `src/omega/cli/soul_stage.py` (135 lines) — Textual TUI with:
  - Approve/Reject/Defer bindings (`a`, `r`, `d`, `q`)
  - DataTable with L1/L2/L3 columns
  - Detail view for selected proposal
  - **BUT**: Uses MOCK data (hardcoded `mock_proposals`), not wired to real USM/proposed_lessons
- `scripts/soul_review.py` (43 lines) — Simple script that reads proposed_lessons from USM and prints them. No interactive review.
- `Makefile:165` — `soul-review` target calls `soul_review.py`.

**Specific Gap to Fill**:
- `soul_stage.py` is a SKELETON TUI with mock data. The Researcher asked "Textual TUI vs rich CLI?" — **DECISION LOCKED**: rich CLI. Textual is a full UI framework. We are CLI-first.
- `soul_review.py` is PRINT-ONLY. Needs interactive approve/reject workflow.
- Makefile target `soul-review` stays for interactive review. CI gate `soul-audit` (Item 1) is the validation target. Separate names = separate things.

**Decision Locked (Round 2 Meditation)**:
- **NOT Textual TUI. Use `rich.console` + `rich.syntax` + simple `input()` loop.** Target: 50 lines max.

**Output**: Wired `soul_review.py` with rich-based diff display + approve/reject workflow.
**Effort**: 2h (wire real data + rich diff + approve/reject)
**Dependencies**: Item 1 (schema validation), Item 2 (migration script)

---

### 6. DistillationSpec for Meditate Protocol
**Why Critical**: We need to extract L1/L2/L3 from raw session logs without hallucinations.

**Research Focus**:
- Creating a `DistillationSpec` dataclass that acts as a config layer on top of the existing `SoulDistiller`.
- Mapping the Meditate protocol's persona-lens approach to the Soul Distiller's extraction methods.

**Existing Artifacts (DO NOT REBUILD)**:
- `src/omega/meditate/protocol.py` (339 lines) — Full Meditate protocol with:
  - `MeditationSpec` — Subject, lens_set, mode, phases, integrate flag
  - `PersonaSpec` — name, domain, mandate_lens, anti_domains, pillar, element
  - `PersonaLibrary` — Named collection of PersonaSpecs
  - `MeditatePhase` — calibration → immersion → collision → sequencing → verdict → integration
  - `OutputMode` — diagnostic, strategic, creative, audit, synthesis
  - Built-in libraries: `get_ten_pillars()`, `get_makali_triad()`
- `src/omega/oracle/soul_distiller.py` (689 lines) — Full distillation engine with:
  - `DistillationEntry` — L1/L2/L3 with sphere, source_trace_id, source_entity
  - `SessionClassifier` — Conservative classifier (routine vs. novel)
  - `QualityScore` — 5-factor quality scoring
  - `SoulDistiller` class — `distill_session()`, `append_to_soul()`, `distill_and_save()`
  - Writes to `proposed_lessons.yaml` via USM

**Specific Gap to Fill**:
- The Meditate protocol and Soul Distiller are SEPARATE systems. Kali wants a `DistillationSpec` that bridges them via config, not replacement.
- The Soul Distiller already does L1→L2→L3 extraction with its own internal prompts (`_extract_narrative()`, `_extract_insight()`, `_extract_principle()`). These work.

**Decision Locked (Round 2 Meditation)**:
- **WRAP, don't replace.** DistillationSpec is a config layer that plugs into `SoulDistiller.distill_session()`. The 689 lines of working code stay untouched.
- The existing L1/L2/L3 extraction methods remain as defaults. DistillationSpec provides overrides.

**Output**: `DistillationSpec` dataclass in `protocol.py` + integration with `SoulDistiller.distill_session()`.
**Effort**: 1.5h (DistillationSpec + integration + tests)
**Dependencies**: None (parallel to other items)

**Total Estimated Effort: ~7h** (vs. 24h original, vs. 10h Researcher v1 — collapsed 3h via Round 2 decisions)

| Cancellation | Time Saved | Rationale |
|-------------|-----------|-----------|
| Pydantic refactor | −1h | Existing `yaml.safe_load` + dict checks are correct for 10 files |
| ruamel.yaml evaluation | −0.5h | Lilith's soul.yaml is 18 lines with zero comments |
| Ripgrep wrapper | −0h | Already 30min run-script; ripgrep was over-engineering anyway |
| Cvar runtime | −0.5h | `config/moderation.yaml` is simpler; build cvar only when 3+ toggles exist |
| Textual TUI | −1h | 50-line rich CLI is sufficient for approve/reject |
| DistillationSpec rewrite | −0.5h | Wrapping 689 lines of working code costs less than replacing |

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

1. **Assign owners** to each of the 6 research items (can be paired)
2. **Kickoff 30-min sync** to align on hypotheses and search strategies
3. **Timebox**: 4 hours max per research item (aligns with Wave 3 migration window)
4. **Deliver by**: EOD today to inform Lilith migration execution tomorrow
5. **Integrate**: Findings directly into migration PRs and documentation

> **Remember**: The goal is not academic perfection — it's **de-risked execution**. Each research item should answer: *"What is the smallest thing we need to know to avoid critical failure in Lilith's migration?"*

---

## 📊 Dependency Graph

```
Item 1 (Parameterize Validate) ──────┐
                                       ├──→ Item 2 (Run Migration) ───→ Item 5 (CLI Review)
Item 3 (Run Heritage Script) [PARALLEL]┤
                                       ├──→ Item 4 (Sovereignty Config) [PARALLEL]
Item 6 (DistillationSpec) [PARALLEL]   ┘
```

**Critical Path**: Item 1 (1h) → Item 2 (30min) → Item 5 (2h) = **3.5h sequential**
**Parallel Track A**: Item 3 (30min) — Run existing heritage migration script
**Parallel Track B**: Item 4 (1.5h) — Sovereignty Gate config wiring
**Parallel Track C**: Item 6 (1.5h) — DistillationSpec bridge

**Total wall clock with parallelism**: ~5h (Item 1 + Item 2 + Item 5 sequential, Items 3/4/6 in parallel)

---

## ⚠️ Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing `soul_validator.py` misses a forbidden field | Low | Manual dict checks are correct for 10 keys. Add extra='forbid' only if entity count grows. |
| `yaml.dump` loses structure on a complex soul.yaml | Low | Lilith is 18 lines. Ship Phase 1; trigger condition: "if a file has inline comments" → add ruamel.yaml. |
| Heritage migration script has gaps in MIGRATION_RULES | Medium | Run with `--dry-run` first, verify coverage against `rg -c` baseline. Fix gaps before `--apply`. |
| Sovereignty counter write adds latency to inference path | Low | Async fire-and-forget in `anyio.TaskGroup`. Counter flush is non-blocking. |
| Rich CLI review gate too minimal for complex reviews | Low | Start with 50-line rich CLI. Upgrade to Textual TUI only if user feedback demands it. |
| DistillationSpec conflates with Soul Distiller's internal prompts | Medium | Wrap, don't replace. DistillationSpec is config layer only — all 689 lines of existing extraction stay as defaults. |
| `make soul-audit` and `make soul-review` names confuse users | Low | Document clearly: `soul-review` = interactive user review. `soul-audit` = CI validation gate. Separate targets, separate purposes. |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_wave3_research ⬡ ACTIVE*
*Research enables sovereignty. Sovereignty enables execution.*
*Enhanced: 2026-07-17 — Deep codebase audit reveals substantial existing artifacts.*

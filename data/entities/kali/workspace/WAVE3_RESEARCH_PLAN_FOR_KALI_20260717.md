<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Wave 3 Research Plan: Soul Architecture Implementation Support
# v4.0 — ACTIONABLE SEARCH QUERIES — 2026-07-17
**AP Token**: `AP-WAVE3-RESEARCH-PLAN-v4.0.0`

**Date**: 2026-07-17
**Purpose**: Actionable research plan with search-engine-resolvable queries for an LLM agent to execute.
**Key Change from v3.0**: All project-specific jargon replaced with generic technical concepts. Each item has explicit search queries, implementation context (what already exists), and a clear gap to fill.

---

## How to Execute This Plan

This plan is designed for an LLM agent with web search access. Each research item has:

1. **Implementation Context** — What already exists in the codebase (DO NOT RESEARCH)
2. **The Gap** — What is missing and needs external research
3. **Search Queries** — Specific, jargon-free queries that search engines WILL resolve
4. **Expected Findings** — What the search should return
5. **Output** — Concrete deliverable (code snippet, config pattern, or decision)

**Temporal Mandate**: All searches MUST include "2026" or "latest" to ensure current best practices.

---

## Research Item 1: Parameterized YAML Schema Validation with CI Gate

### Implementation Context (DO NOT RESEARCH)
- `scripts/validate_soul.py` (153 lines) — Validates 4 YAML files for a single entity. Uses `yaml.safe_load` + manual dict checks. Hardcoded to one entity path.
- `src/omega/oracle/soul_validator.py` (217 lines) — `SoulValidator` class with v6.1 schema checks, forbidden field validation, required field checks.
- `Makefile:165` — `soul-review` target exists (interactive user review). Need SEPARATE `soul-audit` target (CI validation).

### The Gap
The validation script works but is hardcoded to one entity. Need:
- `--entity` CLI argument to validate any entity
- New Makefile target `soul-audit` that runs validation across all entities
- The script must exit non-zero on any validation failure (CI gate pattern)

### Search Queries
```
1. "Python argparse accept entity name argument YAML validation script 2026"
2. "Makefile target run Python script pass fail CI gate pattern 2026"
3. "Python YAML schema validation enforce required fields forbidden keys 2026"
4. "Python script validate multiple YAML files loop exit code CI 2026"
5. "Makefile CI gate pattern run validation script exit code non-zero 2026"
```

### Expected Findings
- argparse pattern for `--entity` flag with default fallback
- Makefile pattern for CI gate (exit code propagation)
- YAML validation best practices (safe_load, schema enforcement)
- Python script exit code conventions for CI (sys.exit(1) on failure)

### Output
Updated `validate_soul.py` with `--entity` argument + new `make soul-audit` Makefile target.

---

## Research Item 2: Complex YAML Migration with Atomic Writes

### Implementation Context (DO NOT RESEARCH)
- `scripts/migrate_soul_v6.py` (437 lines) — Two-phase commit migration script.
  - `load_soul_yaml()` — Resilient parser handles flat/nested/mixed YAML formats
  - `deconstruct_soul()` — Separates identity (Constitution) from lessons (Gnosis)
  - `atomic_write_yaml()` — tmp-rename pattern for crash-safe writes
  - `migrate_entity()` — Single-entity migration with dry-run support
  - `FLEET_ENTITIES` — List of 11 active entities (roc_racoon at line 39)
- Target entity: `roc_racoon` (751 lines, complex nested YAML with `lessons_learned` arrays, empty `embodied_experiences` blocks)

### The Gap
Script has never been tested on a complex entity. Need:
- Verify `deconstruct_soul()` handles roc_racoon's nested `lessons_learned` list-of-objects format
- Verify `atomic_write_yaml()` handles the 751-line output correctly
- Test the two-phase commit pattern (Phase 1 validation → Phase 2 execution)
- Verify `yaml.dump(default_flow_style=False, sort_keys=False)` preserves structure

### Search Queries
```
1. "Python yaml.dump preserve nested list structure complex YAML 2026"
2. "Python atomic file write tmpfile rename pattern YAML crash safe 2026"
3. "Python YAML migration script two phase commit validation execution 2026"
4. "Python yaml.safe_load nested list of dictionaries parse 2026"
5. "Python YAML migration dry run validate before write pattern 2026"
6. "Python pathlib write YAML file atomic rename os.replace 2026"
```

### Expected Findings
- `yaml.dump()` behavior with complex nested structures (lists of dicts)
- Atomic file write patterns (tempfile + os.replace)
- Two-phase commit patterns for file migration
- Best practices for YAML migration scripts with dry-run support

### Output
Verified migration plan for roc_racoon with documented test results.

---

## Research Item 3: Regex-Based Bulk Code Annotation Migration

### Implementation Context (DO NOT RESEARCH)
- `scripts/migrate_heritage_tags.py` (238 lines) — COMPLETE migration script.
  - `MIGRATION_RULES` — 192 mapping entries (file_pattern, legacy_tag, context_keyword → vet_tag)
  - `FALLBACK_MAPPING` — Default replacements when context doesn't match
  - `migrate_file()` — Regex-based replacement with dry-run support
  - `main()` — CLI with `--apply` and `--file` flags
- 560 `[id-soft:` tags across 98 Python files need conversion to `[id-soft: vet-XXX]` format.

### The Gap
Script exists and is complete. Just needs to be RUN and VERIFIED. No new code needed. Research is about:
- Verifying regex patterns cover all 560 tags
- Understanding fallback behavior when context doesn't match
- Post-apply verification strategy

### Search Queries
```
1. "Python regex bulk find replace code comments multiple files 2026"
2. "Python regex migration script file pattern context keyword replacement 2026"
3. "Python regex fallback mapping when pattern does not match 2026"
4. "Python code annotation migration automated bulk transform 2026"
5. "grep rg count occurrences pattern across codebase verify coverage 2026"
```

### Expected Findings
- Regex patterns for code comment migration
- Fallback mapping strategies for partial matches
- Post-apply verification patterns (grep/rg count before vs after)
- Best practices for bulk code transformations

### Output
Verification report: dry-run coverage analysis + apply + post-apply verification.

---

## Research Item 4: Async Counter with Config Toggle (Feature Flag)

### Implementation Context (DO NOT RESEARCH)
- `src/omega/governance/sovereignty_gate.py` (113 lines) — CI gate class reading MetricsDB.
- `src/omega/observability/sovereignty.py` (167 lines) — `get_sovereignty_ratio()` querying SQLite `performance` table.
- `Makefile:398` — `sovereignty-gate` target already runs the gate.
- `GenerateResult.is_cloud` — Already populated by ModelGateway (21 usages).
- `ModelGateway._is_cloud_provider_name()` — Already classifies providers as local/cloud.

### The Gap
CI gate exists but is POST-HOC (build-time check). Need:
- Runtime toggle via `config/moderation.yaml` (default OFF)
- Async counter increment at inference time (non-blocking)
- Wire counter to existing MetricsDB `performance` table
- No latency added to critical inference path

### Search Queries
```
1. "Python async fire and forget counter increment SQLite 2026"
2. "Python YAML config file feature flag toggle reload 2026"
3. "Python anyio TaskGroup fire and forget background task 2026"
4. "Python SQLite async write non blocking WAL mode 2026"
5. "Python config file reload on change watchdog pyinotify 2026"
6. "Python feature flag pattern config file default off 2026"
```

### Expected Findings
- Async fire-and-forget patterns (anyio TaskGroup)
- YAML config file with reload support
- SQLite WAL mode for concurrent reads/writes
- Feature flag patterns (config file toggle, default OFF)

### Output
`SovereigntyTracker` class + `config/moderation.yaml` wiring + async counter hook.

---

## Research Item 5: Rich-Based Interactive CLI Diff Reviewer

### Implementation Context (DO NOT RESEARCH)
- `scripts/soul_review.py` (43 lines) — Already accepts `--entity` (verified at line 14). Reads from USM and prints. No interactive review.
- `src/omega/cli/soul_stage.py` (135 lines) — Textual TUI skeleton with mock data. NOT wired to real data.
- `Makefile:165` — `soul-review` target already passes `--entity` correctly.

### The Gap
Script is PRINT-ONLY. Need interactive approve/reject workflow with:
- Rich-based colored diff display (unified diff format)
- Interactive prompt: `[A]pprove, [R]eject, [D]efer`
- On approve: write to `approved_lessons.yaml`
- On reject: discard or archive
- Target: 50 lines max using `rich.console` + `rich.syntax` + `input()`

### Search Queries
```
1. "Python rich library terminal diff display unified diff colored 2026"
2. "Python rich console Syntax highlight YAML diff terminal 2026"
3. "Python interactive CLI approve reject prompt input loop 2026"
4. "Python rich vs textual terminal UI lightweight comparison 2026"
5. "Python difflib unified_diff rich syntax highlight terminal 2026"
6. "Python rich library install pip minimal dependencies 2026"
```

### Expected Findings
- Rich library API for colored terminal output
- `difflib.unified_diff()` with Rich syntax highlighting
- Interactive CLI patterns (approve/reject/defer)
- Rich vs Textual comparison (Rich = lightweight, Textual = full TUI framework)

### Output
Updated `soul_review.py` with rich diff display + approve/reject workflow (50 lines max).

---

## Research Item 6: Field Classification Registry for Multi-Pass Extraction

### Implementation Context (DO NOT RESEARCH)
- `src/omega/oracle/soul_distiller.py` (689 lines) — Full distillation engine with:
  - `_extract_narrative()`, `_extract_insight()`, `_extract_principle()` — Use regex/heuristics (NOT LLM)
  - `DistillationEntry` — L1/L2/L3 with sphere, source_trace_id, source_entity
  - `SessionClassifier` — Routine vs. novel classification
  - `QualityScore` — 5-factor quality scoring
- `src/omega/meditate/protocol.py` (339 lines) — Meditate protocol with PersonaSpec, MeditationSpec.

### The Gap
Soul Distiller's regex works for deterministic fields (trace_id, source_entity, sphere). But `narrative`, `insight`, `principle` are inherently LLM-required fields — regex cannot extract meaningful content from them. Need:
- Field Classification Registry marking each field as `deterministic` or `llm_required`
- Microsoft ISE 4-pass pipeline: Deterministic → Bounded LLM → Guarded Merge → Evidence Mapping
- Pass 2 LLM orchestrator that only runs on `llm_required` fields
- Integration with existing Soul Distiller (wrap persistence, replace extraction for LLM fields)

### Search Queries
```
1. "Microsoft ISE 4-pass extraction pipeline deterministic LLM 2026"
2. "Field classification registry deterministic vs LLM required fields 2026"
3. "Python dataclass field metadata deterministic llm_required annotation 2026"
4. "LLM extraction pipeline bounded judgment guarded merge evidence mapping 2026"
5. "Python multi-pass extraction regex first LLM second pattern 2026"
6. "Deterministic first LLM second extraction pattern best practices 2026"
7. "Python dataclass field registry pattern classify fields by processing type 2026"
```

### Expected Findings
- Microsoft ISE 4-pass pipeline architecture
- Field classification registry patterns (dataclass with metadata)
- Deterministic-first, LLM-second extraction patterns
- Guarded merge strategies (deterministic wins, LLM appends)
- Evidence mapping for traceability

### Output
`FieldClassificationRegistry` dataclass + `DistillationLLMOrchestrator` (Pass 2) + integration plan.

---

## Execution Sequence (Unchanged from v3.0)

```
WAVE 3a (NOW): 
  Item 1: Parameterize validate_soul.py + make soul-audit    [Ma'at/P5, 1h]
  Item 3: Run heritage tag --dry-run then --apply            [Doom Guy, 30min]
  Item 4: SovereigntyGate + config/moderation.yaml           [Ma'at/P5, 1.5h]

WAVE 3b (After Item 1):
  Item 2: Migration test on roc_racoon (751 lines)           [Lilith/P7, 1h]
  Item 6: DistillationSpec Field Classification Registry     [Lilith/P6, 1.5h]

WAVE 3c (After Items 2 + 6):
  Item 5: CLI Review Gate (rich diff + approve/reject)       [Ma'at/P3, 1.5h]
  Item 7: Post-migration reconciliation audit                [Verity, 1h]
```

## Effort Summary

| # | Task | Owner | Effort |
|---|------|-------|--------|
| 1 | Schema Validation + `make soul-audit` | Ma'at/P5 | 1h |
| 2 | Migration test on roc_racoon (751 lines) | Lilith/P7 | 1h |
| 3 | Heritage Tag Migration (run `--apply`) | Doom Guy | 30min |
| 4 | SovereigntyTracker + config/moderation.yaml | Ma'at/P5 | 1.5h |
| 5 | CLI Review Gate (rich diff + approve/reject) | Ma'at/P3 | 1.5h |
| 6 | DistillationSpec (Field Classification Registry) | Lilith/P6 | 1.5h |
| 7 | Post-migration reconciliation audit | Verity | 1h |
| — | Observability overhead (+10 min per item) | ALL | +1h |
| **TOTAL** | | | **9h** |

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Migration fails on roc_racoon's complex nested structure | High | Dry-run FIRST. If fails, fix `deconstruct_soul()` before any migration. |
| Migration corrupts existing soul.yaml | Critical | `atomic_write_yaml()` uses tmp-rename. Backup = `cp` + `git commit`. Rollback = `git revert`. |
| Heritage migration script has gaps in MIGRATION_RULES | Medium | Run with `--dry-run` first, verify coverage against `rg -c` baseline. |
| Sovereignty counter adds latency to inference | Low | Async fire-and-forget in `anyio.TaskGroup`. WAL mode already standard. |
| CLI review gate has no content (DistillationSpec not ready) | Medium | Items 5 & 6 must sequence: DistillationSpec first, then review gate. |
| DistillationSpec Pass 2 LLM overhead too expensive | Low | Only runs on `llm_required` fields. Gate on eval threshold. |
| No observability = no forensic trail | Medium | +1h structured JSONL logging. M9/M23 compliant. |

---

*Wave 3 Research Plan v4.0 — Actionable search queries for LLM agent execution.*
*All project-specific jargon replaced with generic technical concepts.*
*Research complete. Ready for execution.*

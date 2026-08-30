---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "spec"
document_id: "migration-playbook-spec-2026-08-22-v3"
title: "Post-Debut Breaking-Change Migration Playbook"
status: "DRAFT"
version: "1.0.0"
date: "2026-08-22"
owner: "researcher"
tags: ["migration", "breaking-changes", "deprecation", "playbook", "post-debut", "llm-friendly"]
priority: "P0"
depends_on: ["SOVEREIGN_MANDATES.md", "DOC_STYLE_GUIDE.md", "LLM_FRIENDLY_DOCS_BP.md", "PILLAR_REFACTOR_PLAN_20260822.md"]
blocks: ["Post-debut migration execution"]
acceptance_gates:
  - "All 6 sections have Answer-First format"
  - "Self-contained code examples for codemod patterns"
  - "Mermaid + YAML dependency graphs for migration phases"
  - "Telemetry-free tracking mechanism specified"
  - "Post-mortem template maps to PIVOT_LOG + Soul Distillation"
  - "Passes `make doc-llm-validate`"
cross_references:
  - "SOVEREIGN_MANDATES.md"
  - "DOC_STYLE_GUIDE.md"
  - "LLM_FRIENDLY_DOCS_BP.md"
  - "PILLAR_LEAK_AUDIT_20260822.md"
  - "PILLAR_REFACTOR_PLAN_20260822.md"
  - "PILLAR_WAD_BOUNDARY_MAP.md"
  - "MIGRATION_CASE_STUDIES_EVIDENCE_20260822_v3.md"
  - "REHEARSAL_LEARNING_PLAN_20260822_v3.md"
llm_metadata:
  token_budget: 12000
  chunk_strategy: "section_per_phase"
  answer_first_sections: true
  self_contained_code: true
  modular_pages: true
---

# 🔱 Post-Debut Breaking-Change Migration Playbook
**AP Token**: `AP-MIGRATION-PLAYBOOK-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_migration_playbook ⬡ DRAFT

**Date**: 2026-08-22
**Purpose**: Canonical process for executing and documenting breaking-change migrations for live Omega Engine user bases post-debut. Covers deprecation policy, user communication, codemod tooling, telemetry-free tracking, and post-mortem learning capture.
**Scope**: Applies to Engine core (`src/omega/`), MCP Hub (`mcp_servers/omega_hub/`), WAD configs (`config/wads/`), and public CLI surfaces. Does NOT govern internal refactors with no user-facing impact.

---

## What

A **phase-gated, evidence-based migration framework** that transforms breaking changes from "hope users notice" into **measured, reversible, learnable transitions**. Built on case studies from Python 2→3, Pydantic v1→v2, Kubernetes, Django, Home Assistant, and MCP SEP-2596.

## Why

The Pillar→Node decoupling (D180) revealed **23 active M2 violations** across MCP Hub, scripts, tests, and WAD configs. Post-debut, every such refactor becomes a **user-facing breaking change**. Without a playbook, we repeat the industry's worst patterns: silent removals, inadequate timelines, no automated migration, zero adoption visibility, and lost institutional memory.

---

## 1. Deprecation Policy & Versioning Contract

### 1.1 Feature Lifecycle States (Adapted from MCP SEP-2596)

| State | Criteria | Minimum Window | Removal Eligibility |
|-------|----------|----------------|---------------------|
| **Active** | Fully supported, recommended for new adoption | N/A | N/A |
| **Deprecated** | Formal SEP/ADR accepted; replacement Active; migration path documented | **6 months** (or 3 minor releases, whichever longer) | After window expires |
| **Removed** | Deprecation window complete; no active users detected via tracking | N/A | N/A |

**Key rule**: A feature is NOT deprecated until its replacement is **Active** in the same release. No "soft deprecation" limbo.

### 1.2 Versioning & Release Cadence

| Channel | Cadence | Deprecation Announcement | Removal Earliest |
|---------|---------|--------------------------|------------------|
| **Minor** (x.y.0) | Monthly | ✅ Required | Next minor + 6 months |
| **Patch** (x.y.z) | As needed | ❌ Never deprecate in patch | N/A |
| **LTS** (x.y LTS) | Annual | ✅ Extended to 12 months | LTS end + 6 months |

**Omega-specific**: Post-debut, we ship **monthly minors**. First LTS targeted at v1.0 (Horizon 4).

### 1.3 Deprecation Announcement Requirements (Mandatory Checklist)

Every deprecation MUST ship with:

- [ ] **SEP/ADR document** in `docs/decisions/` with: feature name, rationale, replacement, migration path, timeline
- [ ] **Changelog entry** in `CHANGELOG.md` under `### Deprecated` with version + removal target
- [ ] **Runtime deprecation warning** emitted on every use (see §2.2)
- [ ] **Migration guide** in `docs/migrations/<feature>-migration.md` (Answer-First format)
- [ ] **Codemod availability** decision recorded (see §3)
- [ ] **Tracking instrumentation** added (see §4)

---

## 2. User-Facing Communication Craft

### 2.1 Deprecation Notice Conventions

**Format**: RFC-style SEP (Specification Enhancement Proposal) in `docs/decisions/SEP-XXXX-<feature>-deprecation.md`

```markdown
---
sep: XXXX
title: "Deprecate <Feature Name>"
status: "Final"
type: "Process"
created: "YYYY-MM-DD"
author: "<entity>"
sponsor: "<entity>"
pr: "#XXXX"
---

## Abstract
<One-paragraph summary: what is deprecated, why, replacement, timeline>

## Motivation
<Systematic reasons — not "we want to clean up." Tie to mandates, security, architecture.>

## Migration Path
<Step-by-step. If no migration needed, state explicitly.>

## Timeline
- **Deprecated in**: vX.Y.0 (YYYY-MM-DD)
- **Warning emitted**: vX.Y.0+
- **Removal eligible**: vX.(Y+6).0 (YYYY-MM-DD) — 6 months / 3 minors
- **Actual removal**: vX.(Y+N).0 (to be determined by tracking data)

## Backward Compatibility
<What breaks, what shims exist, dual-name shim duration>

## Security Implications
<Any? If none, state "None identified.">

## Reference Implementation
<Links to codemod, shim code, test fixtures>
```

### 2.2 Runtime Warning Emission Standard

**Every deprecated API surface MUST emit a structured warning**:

```python
# File: src/omega/oracle/deprecation.py
# Purpose: Standardized deprecation warning emission
# Dependencies: warnings, src.omega.observability.logger

import warnings
from src.omega.observability import get_logger

logger = get_logger(__name__)

DEPRECATION_TEMPLATE = (
    "{feature} is deprecated since v{since_version} and will be removed in "
    "v{removal_target_version} (target: {removal_date}). "
    "Migration: {migration_url}. "
    "Suppression: set OMEGA_SUPPRESS_DEPRECATION={feature}=1"
)

def emit_deprecation_warning(
    feature: str,
    since_version: str,
    removal_target_version: str,
    removal_date: str,
    migration_url: str,
    stacklevel: int = 2,
) -> None:
    """Emit deprecation warning to stderr AND structured log."""
    msg = DEPRECATION_TEMPLATE.format(
        feature=feature,
        since_version=since_version,
        removal_target_version=removal_target_version,
        removal_date=removal_date,
        migration_url=migration_url,
    )
    # Stdlib warning for tooling (pytest -W, etc.)
    warnings.warn(msg, DeprecationWarning, stacklevel=stacklevel)
    # Structured log for local observability (M22 provenance)
    logger.warning("deprecation_emitted", extra={
        "feature": feature,
        "since_version": since_version,
        "removal_target": removal_target_version,
        "removal_date": removal_date,
        "migration_url": migration_url,
    })
```

**Usage in code**:
```python
# File: src/omega/oracle/entity_registry.py (example)
from src.omega.oracle.deprecation import emit_deprecation_warning

@property
def pillars(self) -> List[str]:
    emit_deprecation_warning(
        feature="Entity.pillars",
        since_version="0.9.0",
        removal_target_version="0.12.0",
        removal_date="2026-12-22",
        migration_url="https://docs.omega-engine.dev/migrations/pillars-to-slots",
    )
    return self.slots  # shim
```

### 2.3 Migration Guide Template (Answer-First, LLM-Friendly)

**Location**: `docs/migrations/<feature>-migration.md`

```markdown
---
schema_version: "1.0"
document_type: "guide"
document_id: "<feature>-migration"
title: "Migration Guide: <Feature> → <Replacement>"
status: "ACTIVE"
version: "1.0.0"
date: "YYYY-MM-DD"
owner: "<entity>"
tags: ["migration", "breaking-change", "<feature>"]
priority: "P0"
acceptance_gates:
  - "All code examples runnable"
  - "Codemod command documented"
  - "Rollback procedure tested"
cross_references:
  - "SEP-XXXX-<feature>-deprecation.md"
  - "CHANGELOG.md"
llm_metadata:
  token_budget: 3000
  chunk_strategy: "section_per_step"
  answer_first_sections: true
  self_contained_code: true
---

# 🔱 Migration Guide: <Feature> → <Replacement>
**AP Token**: `AP-MIGRATION-<FEATURE>-v1.0.0`
⬡ OMEGA ⬡ <ENTITY> ⬡ <MODEL> ⬡ opencode ⬡ trc_migration_guide ⬡ ACTIVE

**Date**: YYYY-MM-DD
**Purpose**: Step-by-step migration from deprecated <Feature> to <Replacement>.
**Affected**: <Who/what uses this — CLI users, MCP clients, WAD authors, entity authors>

---

## What

<One paragraph: what changes, what breaks, what the new way looks like.>

## Why

<One paragraph: systematic reason (mandate, security, architecture). Not "cleanup.">

## Acceptance Criteria (Copy-Paste Verifiable)

- [ ] Old import/path no longer used in codebase
- [ ] New import/path works for all documented use cases
- [ ] Codemod transforms test fixtures correctly
- [ ] Rollback restores previous behavior
- [ ] Deprecation warning no longer emitted after migration

## Dependencies

- SEP-XXXX (deprecation decision)
- Codemod: `<tool>` available at `<location>`
- Replacement feature Active since vX.Y.0

---

## Step 1: Identify Usage

```bash
# Self-contained: runnable command to find all usages
grep -r "old.import.path" --include="*.py" src/ tests/ config/ docs/
# Or for MCP tools:
grep -r "old_tool_name" mcp_servers/omega_hub/
```

## Step 2: Run Codemod (If Available)

```bash
# File: scripts/codemods/<feature>-migration.py
# Purpose: Automated migration for <feature>
# Dependencies: libcst, ast-grep (see §3)

# Example using libcst:
python -m scripts.codemods.pillars_to_slots --path src/ --write
# Example using ast-grep:
ast-grep run --config scripts/codemods/pillars_to_slots.yaml --rewrite
```

## Step 3: Manual Fixes (Silent Breaking Changes)

> **Critical**: Automated tools catch mechanical renames. **Silent behavior changes require human review.**

| Silent Change | Detection | Fix |
|---------------|-----------|-----|
| `Optional[T]` default `None` → required | Test failures, runtime errors | Add `= None` explicitly |
| Type coercion stricter | Validation errors | Pre-process inputs or enable `coerce_numbers_to_str` |
| Regex engine changed | Pattern mismatches | Set `regex_engine="python-re"` in `ConfigDict` |

## Step 4: Verify & Test

```bash
# Run full test suite
make test
# Run migration-specific tests
pytest tests/migrations/test_<feature>_migration.py -v
# Verify no deprecation warnings in clean run
python -W error::DeprecationWarning -m pytest tests/ -x
```

## Step 5: Rollback Procedure

```bash
# If migration breaks production:
git revert <migration-commit>
# Or disable new feature via env var:
OMEGA_DISABLE_<FEATURE>=1 python -m omega.cli ...
```

---

## 3. Codemod / Automated Migration Tooling

### 3.1 Tool Selection Matrix (2025-2026 State of the Art)

| Tool | Language | Paradigm | Best For | Omega Adoption |
|------|----------|----------|----------|----------------|
| **libcst** | Python | CST (preserves formatting, comments) | Mechanical renames, import rewrites, config migrations | ✅ **PRIMARY** — Python-native, preserves style |
| **ast-grep** | Polyglot (Rust core) | AST pattern matching (YAML rules) | Cross-language, structural search/replace, linting | ✅ **SECONDARY** — for YAML/JSON/config + polyglot |
| **gritql** | Polyglot | Query language for search/lint/modify | Complex multi-file transformations | 🟡 EVALUATE — if libcst/ast-grep insufficient |
| **codemod CLI** | Polyglot | Multi-step transformation orchestration | Chaining codemods, scaffolding, sharing | 🟡 EVALUATE — for complex multi-phase migrations |
| **OpenRewrite** | JVM (Java/Kotlin) | Recipe-based | Java ecosystems | ❌ NOT APPLICABLE |
| **ts-migrate** | TypeScript | TypeScript-specific | JS→TS migration | ❌ NOT APPLICABLE |

**Decision**: **libcst for Python code**, **ast-grep for YAML/JSON/config/WAD files**. Both are Rust/Python native, fast, and preserve formatting.

### 3.2 When to Build a Codemod (Decision Framework)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CODEMOD BUILD DECISION TREE                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Is the change PURELY MECHANICAL? (rename, import, signature)│
│     ├─ YES → Build codemod (high ROI)                          │
│     └─ NO  → Go to 2                                           │
│                                                                 │
│  2. Are there SILENT BREAKING CHANGES? (behavior differs)      │
│     ├─ YES → Codemod for mechanical layer + MANUAL GUIDE for   │
│     │        silent changes (Pydantic v2 pattern)              │
│     └─ NO  → Go to 3                                           │
│                                                                 │
│  3. Is the surface area > 50 files OR > 5 distinct patterns?   │
│     ├─ YES → Build codemod (amortizes cost)                    │
│     └─ NO  → Manual guide + grep/fix may suffice               │
│                                                                 │
│  4. Is this a REPEATING PATTERN? (will we do similar again?)   │
│     ├─ YES → Invest in reusable codemod framework              │
│     └─ NO  → One-off script acceptable                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Codemod Project Structure

```
scripts/codemods/
├── __init__.py
├── base.py                 # Shared libcst/ast-grep utilities
├── pillars_to_slots/       # Example: Pillar→Node migration
│   ├── __init__.py
│   ├── transformer.py      # libcst CSTTransformer
│   ├── config.yaml         # ast-grep rules (for YAML files)
│   ├── test_fixtures/      # Before/after pairs for testing
│   │   ├── before_python.py
│   │   ├── after_python.py
│   │   ├── before_yaml.yaml
│   │   └── after_yaml.yaml
│   └── run.py              # CLI entry: python -m scripts.codemods.pillars_to_slots
├── registry.py             # Codemod registry for discovery
└── runner.py               # Orchestrates multi-codemod runs
```

### 3.4 libcst Transformer Pattern (Self-Contained Example)

```python
# File: scripts/codemods/pillars_to_slots/transformer.py
# Purpose: libcst transformer for pillars → slots migration
# Dependencies: libcst, libcst.matchers

import libcst as cst
from libcst.matchers import Attribute, Name

class PillarsToSlotsTransformer(cst.CSTTransformer):
    """Transform deprecated `pillars` attribute access to `slots`."""

    def leave_Attribute(self, original_node: cst.Attribute, updated_node: cst.Attribute) -> cst.Attribute:
        # Match `entity.pillars` or `obj.pillars`
        if m.matches(updated_node, m.Attribute(attr=m.Name("pillars"))):
            # Replace attribute name only, preserve formatting
            return updated_node.with_changes(attr=cst.Name("slots"))
        return updated_node

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.Name:
        # Match standalone `pillars` variable (less common)
        if updated_node.value == "pillars":
            # Check context: is this a dict key "pillars:"?
            # For safety, only transform attribute access above
            return updated_node
        return updated_node
```

### 3.5 ast-grep Rule Pattern for YAML/Config (Self-Contained)

```yaml
# File: scripts/codemods/pillars_to_slots/config.yaml
# Purpose: ast-grep rules for YAML config migration
# Dependencies: ast-grep (install: cargo install ast-grep)

rule_id: pillars-to-slots-yaml
language: yaml
pattern: "pillars:"
replacement: "slots:"
# Note: ast-grep matches structural YAML, not plain text
# For nested structures, use:
# pattern: |
#   pillars:
#     $KEY: $VALUE
# replacement: |
#   slots:
#     $KEY: $VALUE
```

### 3.6 Codemod Testing Protocol

```python
# File: scripts/codemods/pillars_to_slots/test_transformer.py
# Purpose: Contract tests for codemod correctness
# Dependencies: pytest, libcst

import libcst as cst
from scripts.codemods.pillars_to_slots.transformer import PillarsToSlotsTransformer

def test_pillars_attribute_renamed():
    code = "entity.pillars"
    module = cst.parse_module(code)
    transformed = module.visit(PillarsToSlotsTransformer())
    assert transformed.code == "entity.slots"

def test_pillars_dict_key_unchanged():
    # Dict keys should NOT be transformed (YAML handled by ast-grep)
    code = 'config = {"pillars": ["P1"]}'
    module = cst.parse_module(code)
    transformed = module.visit(PillarsToSlotsTransformer())
    assert transformed.code == code  # Unchanged

def test_formatting_preserved():
    code = "entity.  pillars  # comment"
    module = cst.parse_module(code)
    transformed = module.visit(PillarsToSlotsTransformer())
    assert "slots" in transformed.code
    assert "# comment" in transformed.code  # Comment preserved
```

---

## 4. Telemetry-Free Deprecation Tracking (M8 Compliant)

### 4.1 The Constraint

**M8 Zero Telemetry**: No external reporting, no phone-home, no analytics sent off-machine. All tracking MUST be local-first, opt-in, and user-visible.

### 4.2 Local Tracking Mechanisms

| Mechanism | What It Captures | User Consent | Storage |
|-----------|------------------|--------------|---------|
| **Runtime warning logs** | Every deprecation emission (feature, timestamp, call site) | Implicit (stderr + local log) | `data/logs/deprecation_warnings.jsonl` |
| **Opt-in usage counter** | Aggregated hit counts per deprecated feature | Explicit env var `OMEGA_TRACK_DEPRECATION=1` | `data/telemetry/deprecation_counts.json` (local only) |
| **Codemod run registry** | Which codemods ran, on what paths, success/failure | Explicit `--track` flag | `data/telemetry/codemod_runs.jsonl` |
| **Issue template** | User-reported migration friction | Voluntary GitHub issue | GitHub (user-initiated) |
| **Crash reporter pattern** | Migration-related crashes (opt-in) | Explicit `OMEGA_CRASH_REPORT=1` | `data/crashes/` local, user chooses to share |

### 4.3 Implementation: Local Deprecation Tracker

```python
# File: src/omega/oracle/deprecation_tracker.py
# Purpose: Local-only deprecation usage tracking (M8 compliant)
# Dependencies: anyio, json, pathlib, src.omega.observability

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import anyio
from src.omega.observability import get_logger

logger = get_logger(__name__)

TRACKING_ENABLED = os.environ.get("OMEGA_TRACK_DEPRECATION") == "1"
TRACKING_DIR = Path(os.environ.get("OMEGA_DATA_DIR", "data")) / "telemetry"
DEPRECATION_COUNTS_FILE = TRACKING_DIR / "deprecation_counts.json"
DEPRECATION_LOG_FILE = TRACKING_DIR / "deprecation_warnings.jsonl"

class LocalDeprecationTracker:
    """Local-only, opt-in deprecation usage tracker."""

    def __init__(self):
        self._counts: Dict[str, int] = {}
        self._loaded = False

    async def _load(self) -> None:
        if self._loaded:
            return
        if DEPRECATION_COUNTS_FILE.exists():
            async with await anyio.open_file(DEPRECATION_COUNTS_FILE, "r") as f:
                content = await f.read()
                self._counts = json.loads(content) if content else {}
        self._loaded = True

    async def _save(self) -> None:
        TRACKING_DIR.mkdir(parents=True, exist_ok=True)
        async with await anyio.open_file(DEPRECATION_COUNTS_FILE, "w") as f:
            await f.write(json.dumps(self._counts, indent=2))

    async def record_deprecation_use(self, feature: str, call_site: str = "") -> None:
        """Record a deprecation hit. Called from emit_deprecation_warning()."""
        # Always log to JSONL (implicit, no opt-in needed for local log)
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "feature": feature,
            "call_site": call_site,
        }
        TRACKING_DIR.mkdir(parents=True, exist_ok=True)
        async with await anyio.open_file(DEPRECATION_LOG_FILE, "a") as f:
            await f.write(json.dumps(log_entry) + "\n")

        # Opt-in aggregated counter
        if TRACKING_ENABLED:
            await self._load()
            self._counts[feature] = self._counts.get(feature, 0) + 1
            await self._save()
            logger.debug("deprecation_tracked", feature=feature, count=self._counts[feature])

    async def get_counts(self) -> Dict[str, int]:
        await self._load()
        return dict(self._counts)

    async def generate_report(self) -> str:
        """Generate human-readable migration readiness report."""
        await self._load()
        lines = ["# Deprecation Usage Report", f"Generated: {datetime.utcnow().isoformat()}Z", ""]
        if not self._counts:
            lines.append("No tracked deprecation usage (OMEGA_TRACK_DEPRECATION=1 to enable).")
        else:
            lines.append("| Feature | Hit Count |")
            lines.append("|---------|-----------|")
            for feature, count in sorted(self._counts.items(), key=lambda x: -x[1]):
                lines.append(f"| {feature} | {count} |")
        return "\n".join(lines)

# Singleton
_tracker: LocalDeprecationTracker = None

def get_deprecation_tracker() -> LocalDeprecationTracker:
    global _tracker
    if _tracker is None:
        _tracker = LocalDeprecationTracker()
    return _tracker
```

### 4.4 Integration with Warning Emission

```python
# File: src/omega/oracle/deprecation.py (updated)
# Add to emit_deprecation_warning():
tracker = get_deprecation_tracker()
# Extract call site from stack
import traceback
call_site = "".join(traceback.format_stack()[-3:-1]).strip()
anyio.create_task_group().__init__()  # Fire-and-forget in AnyIO context
# Actually use proper AnyIO task spawning:
# anyio.create_task_group().start_soon(tracker.record_deprecation_use, feature, call_site)
```

### 4.5 User-Facing Reporting Commands

```bash
# CLI command: omega migration deprecation-report
# Shows local usage stats to inform removal decisions

# Example output:
# # Deprecation Usage Report
# Generated: 2026-08-22T14:30:00Z
#
# | Feature | Hit Count |
# |---------|-----------|
# | Entity.pillars | 1,247 |
# | oracle_list_pillar_keepers | 89 |
# | result.pillar field | 45 |
```

---

## 5. Post-Mortem & Learning Capture Discipline

### 5.1 Blameless Post-Mortem Template (Google SRE + Etsy + Atlassian Adapted)

**Location**: `docs/migrations/<feature>-postmortem.md` (created AFTER removal)

```markdown
---
schema_version: "1.0"
document_type: "postmortem"
document_id: "<feature>-postmortem"
title: "Post-Mortem: <Feature> Deprecation & Removal"
status: "COMPLETE"
version: "1.0.0"
date: "YYYY-MM-DD"
owner: "<entity>"
tags: ["postmortem", "migration", "blameless", "<feature>"]
priority: "P1"
acceptance_gates:
  - "Timeline captured within 5 business days of removal"
  - "Root cause analysis uses 5 Whys"
  - "Action items have owners + due dates"
  - "Lessons staged to proposed_lessons.yaml (L1→L2→L3)"
cross_references:
  - "SEP-XXXX-<feature>-deprecation.md"
  - "MIGRATION_PLAYBOOK_SPEC.md"
  - "PIVOT_LOG.md"
llm_metadata:
  token_budget: 4000
  chunk_strategy: "section_per_phase"
  answer_first_sections: true
---

# 🔱 Post-Mortem: <Feature> Deprecation & Removal
**AP Token**: `AP-POSTMORTEM-<FEATURE>-v1.0.0`
⬡ OMEGA ⬡ <ENTITY> ⬡ <MODEL> ⬡ opencode ⬡ trc_postmortem ⬡ COMPLETE

**Date**: YYYY-MM-DD
**Severity**: SEV-<1-3> (1=major user impact, 3=minor friction)
**Duration**: <deprecation announcement date> → <actual removal date>

---

## What Happened (L1 Narrative)

<One-paragraph summary: feature deprecated on X, removed on Y, Z users affected, N migrations completed.>

## Timeline (L1)

| Date | Event | Details |
|------|-------|---------|
| YYYY-MM-DD | Deprecation announced | SEP-XXXX merged, vX.Y.0 released |
| YYYY-MM-DD | First warning emitted | Runtime warnings active |
| YYYY-MM-DD | Codemod released | `scripts/codemods/<feature>` published |
| YYYY-MM-DD | Migration guide published | `docs/migrations/<feature>-migration.md` |
| YYYY-MM-DD | Tracking shows N% adoption | Local tracker: X hits, Y unique call sites |
| YYYY-MM-DD | Removal executed | vX.Y.0 released, feature removed |
| YYYY-MM-DD | Post-incident review | Blameless meeting held |

## Root Cause Analysis (L2 Insight) — 5 Whys

1. **Why did users not migrate earlier?**
   → Warning not visible in their workflow / CI didn't surface it
2. **Why wasn't warning visible?**
   → Only emitted at runtime, not at install/lint time
3. **Why no install-time check?**
   → No pre-commit hook for deprecation scanning
4. **Why no pre-commit hook?**
   → Not part of migration playbook checklist
5. **Why not in playbook?**
   → Playbook didn't mandate static analysis integration

**Systemic Root Cause**: Migration playbook lacked **static detection** requirement; relied solely on runtime warnings.

## Contributing Factors (L2)

| Factor | Impact | Mitigation for Next Migration |
|--------|--------|-------------------------------|
| Runtime-only warnings | Low visibility in CI | Add `ruff`/`pylint` plugin for deprecation detection |
| No codemod for YAML configs | Manual errors in WAD files | Extend ast-grep rules to all config surfaces |
| Tracking opt-in rate < 10% | Blind spots in adoption | Make tracking default-on for local logs; opt-out only |
| Migration guide not linked from warning | Users couldn't find it | Embed URL in warning message (done) |

## Action Items (L3 Principles → Institutional Knowledge)

| ID | Action | Owner | Due Date | Status | L3 Principle Staged |
|----|--------|-------|----------|--------|---------------------|
| AI-1 | Add static deprecation detection to `make lint` | maat/P3 | YYYY-MM-DD | ☐ | L3-MIG-001: Static detection > runtime-only |
| AI-2 | Extend codemod framework to YAML/JSON | roc_racoon | YYYY-MM-DD | ☐ | L3-MIG-002: Codemods must cover all config surfaces |
| AI-3 | Make local deprecation tracking default-on | researcher | YYYY-MM-DD | ☐ | L3-MIG-003: Visibility requires default-on telemetry |
| AI-4 | Embed migration guide URL in warning template | kali | YYYY-MM-DD | ☐ | L3-MIG-004: Self-service migration needs in-warning links |

## Lessons Staged to Soul Distillation (L1→L2→L3)

Each lesson written to `<entity>/proposed_lessons.yaml` with format:

```yaml
- narrative: "Deprecation of <feature> relied on runtime warnings only; <X>% of users never saw them."
  insight: "Static analysis integration (lint-time) catches migrations earlier than runtime warnings."
  principle: "L3-MIG-001: Migration visibility requires static detection in CI/lint, not just runtime emission."
  tags: ["[N10]", "[MIGRATION]"]
```

### 5.2 Mapping to Existing Systems

| System | Role in Migration Learning |
|--------|----------------------------|
| **PIVOT_LOG.md** | Immutable decision record: SEP → deprecation → removal timeline |
| **Soul Distillation (L1→L2→L3)** | Transforms post-mortem insights into universal principles (`proposed_lessons.yaml`) |
| **Corpus Map (STRATEGY_CORPUS_MAP.md)** | Indexes migration artifacts for future retrieval |
| **Hivemind** | Coordination during active migration (handoffs, locks, awareness) |
| **ACTIVE_SPRINT.json** | Tracks migration tickets as P0/P1 work items |
| **TASK_REGISTRY.json** | Records codemod execution sessions for audit |

---

## 6. Migration Execution Phases (End-to-End)

```mermaid
graph TD
    A[SEP/ADR Decision] --> B[Deprecation Release vX.Y.0]
    B --> C[Runtime Warnings + Local Tracking]
    B --> D[Migration Guide Published]
    B --> E[Codemod Released]
    C --> F[6-Month Window / 3 Minors]
    D --> F
    E --> F
    F --> G{Adoption Check}
    G -->|≥90% migrated| H[Removal Release vX.(Y+6).0]
    G -->|<90% migrated| I[Extend Window + Investigate]
    I --> F
    H --> J[Post-Mortem Written]
    J --> K[Lessons → proposed_lessons.yaml]
    K --> L[PIVOT_LOG Entry]
    L --> M[Corpus Map Updated]
```

```yaml
# Machine-readable phase DAG
migration_phases:
  - id: "decision"
    name: "SEP/ADR Decision"
    deliverables: ["SEP document", "PIVOT_LOG entry"]
    gates: ["Architect approval", "Kali ratification"]
  - id: "deprecation_release"
    name: "Deprecation Release (vX.Y.0)"
    deliverables: ["Runtime warnings", "Migration guide", "Codemod", "Tracking instrumentation"]
    gates: ["make test passes", "make temple-grade passes", "Codemod test fixtures pass"]
  - id: "adoption_window"
    name: "Adoption Window (6 months / 3 minors)"
    deliverables: ["Monthly adoption reports", "User support", "Codemod updates"]
    gates: ["Local tracker shows ≥90% adoption", "No SEV-1 migration blockers"]
  - id: "removal_release"
    name: "Removal Release (vX.(Y+6).0)"
    deliverables: ["Feature removed", "Shims deleted", "Tests updated"]
    gates: ["make test 100%", "No deprecation warnings in clean run"]
  - id: "postmortem"
    name: "Post-Mortem & Learning Capture"
    deliverables: ["Post-mortem doc", "L1→L2→L3 lessons", "PIVOT_LOG entry", "Corpus Map update"]
    gates: ["Blameless review held", "Action items assigned", "Lessons staged"]
```

---

## 7. Pillar→Node Migration: Playbook Applied (Case Study)

### 7.1 Current State (from PILLAR_LEAK_AUDIT_20260822.md)

| Surface | Violations | Status |
|---------|------------|--------|
| MCP Hub Tools | 12 (tool name, response fields) | ❌ CRITICAL |
| Scripts | 3 (setup.sh, mandate_gates.py) | ❌ CRITICAL |
| Tests | 8 (assertions on pillar fields) | ❌ NEEDS UPDATE |
| WAD Config | 70+ entities (pillars: field) | ⚠️ AUTO-MIGRATED |
| Entity Souls | 3 (pillars: in soul.yaml) | ⚠️ WORKSPACE |

### 7.2 Playbook Application

| Phase | Action | Owner | Artifact |
|-------|--------|-------|----------|
| **Decision** | SEP for `pillars` → `slots` deprecation | Kali + Roc | `docs/decisions/SEP-XXXX-pillars-deprecation.md` |
| **Deprecation Release** | v0.9.0: warnings on `pillars` access, codemod for Python+YAML | Roc + Ma'at | `scripts/codemods/pillars_to_slots/`, `docs/migrations/pillars-to-slots.md` |
| **Adoption Window** | 6 months (v0.9.0 → v0.12.0), monthly tracker reports | Researcher | `data/telemetry/deprecation_counts.json` |
| **Removal Release** | v0.12.0: remove shims, update all tests/scripts/docs | Roc + Ma'at | `PILLAR_REFACTOR_PLAN_20260822.md` Phases 1-5 |
| **Post-Mortem** | Blameless review, lessons to Soul Distillation | Researcher + Kali | `docs/migrations/pillars-postmortem.md` |

### 7.3 Dual-Name Shim Strategy (Transition Period)

```python
# File: src/omega/oracle/entity_registry.py (during deprecation window)
# Dual-name shim: accept BOTH pillars and slots, emit warning on pillars

@property
def pillars(self) -> List[str]:
    emit_deprecation_warning(...)
    return self.slots

@pillars.setter
def pillars(self, value: List[str]) -> None:
    emit_deprecation_warning(...)
    self.slots = value

# In __init__ / from_dict: accept both keys
def __init__(self, ..., pillars: List[str] = None, slots: List[str] = None, ...):
    if pillars is not None:
        emit_deprecation_warning(...)
        self.slots = pillars
    elif slots is not None:
        self.slots = slots
    else:
        self.slots = []
```

**Shim removal**: In removal release, delete `pillars` property/setter and `__init__` handling.

---

## 8. Validation Checklist (Pre-Migration Gate)

Before ANY deprecation PR merges:

- [ ] SEP/ADR document exists in `docs/decisions/` with all required fields
- [ ] Migration guide exists in `docs/migrations/` with Answer-First format
- [ ] Codemod decision recorded (build / defer / not-needed) with rationale
- [ ] If codemod built: test fixtures cover all patterns, `make test` passes
- [ ] Runtime warning emission implemented on ALL deprecated surfaces
- [ ] Local tracking instrumentation added (deprecation_tracker.py)
- [ ] CHANGELOG.md updated under `### Deprecated`
- [ ] Dual-name shim implemented (if removal not immediate)
- [ ] Removal target version + date specified in SEP
- [ ] Rollback procedure documented in migration guide
- [ ] Post-mortem template ready (will be filled after removal)

---

## 9. Appendix: Quick Reference Cards

### 9.1 Deprecation Checklist (One-Page)

```
☐ SEP written & ratified
☐ Migration guide written (Answer-First)
☐ Codemod built + tested (libcst for .py, ast-grep for .yaml)
☐ Runtime warnings on ALL surfaces (Python, MCP tools, CLI, WAD load)
☐ Local tracking enabled (deprecation_tracker.py)
☐ CHANGELOG.md: ### Deprecated entry
☐ Dual-name shim in place
☐ Removal target: vX.(Y+6).0 / YYYY-MM-DD
☐ Rollback procedure in migration guide
☐ Post-mortem template ready
```

### 9.2 Codemod Decision Matrix

| Change Type | Tool | Effort | ROI |
|-------------|------|--------|-----|
| Python import/attribute rename | libcst | Low | High |
| Python signature change | libcst | Medium | High |
| YAML/JSON key rename | ast-grep | Low | High |
| YAML structural transform | ast-grep | Medium | High |
| Cross-file refactoring | codemod CLI + libcst | High | Medium |
| Silent behavior change | MANUAL GUIDE ONLY | N/A | N/A |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ MIGRATION-PLAYBOOK ⬡ v1.0.0 ⬡ 2026-08-22*
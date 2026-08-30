---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "spec"
document_id: "migration-playbook-spec-v4"
title: "Post-Debut Breaking-Change Migration Playbook (v4)"
status: "ACTIVE"
version: "1.0.0"
date: "2026-08-22"
owner: "researcher"
tags: ["migration", "playbook", "deprecation", "breaking-changes", "split-test-v4"]
priority: "P1"
depends_on: ["MIGRATION_CASE_STUDIES_EVIDENCE_20260822_v4.md", "D180", "M26"]
blocks: ["post-debut migration execution"]
acceptance_gates:
  - "Every process step cites its evidence case (C1–C6/T)"
  - "Telemetry-free tracking section satisfies M8 verbatim"
  - "Doc templates pass make doc-llm-validate patterns"
cross_references:
  - "MIGRATION_CASE_STUDIES_EVIDENCE_20260822_v4.md"
  - "REHEARSAL_LEARNING_PLAN_20260822_v4.md"
  - "PILLAR_REFACTOR_PLAN_20260822.md (Roc)"
llm_metadata:
  token_budget: 5000
  chunk_strategy: "section_per_component"
  answer_first_sections: true
  self_contained_code: true
---

# Post-Debut Breaking-Change Migration Playbook — Spec (v4)

**AP Token**: `AP-MIGRATION-PLAYBOOK-v4-20260822`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_doc_proc ⬡ ACTIVE

## What (Answer-First)

A five-stage process for shipping breaking changes to a live user base with ZERO telemetry (M8), mapped onto existing Omega machinery (PIVOT_LOG, sprint plans, M26 doc gates, Node charters, Soul Distillation). Evidence anchors reference the companion case-studies file.

## Why

The pillar→slot refactor (D180) is our first live breaking change with external surface (MCP tool names, response fields). Post-debut, users exist and will break. Every stage below exists because a named project failed or succeeded at exactly this step.

---

## Stage 1 — DECIDE: Classify the Break Before Touching Code

**What**: Every breaking change gets a classification ticket BEFORE implementation, filed as a PIVOT_LOG decision.

```yaml
# Embedded YAML — machine-parsable break classification
break_classification:
  id: "BRK-<seq>"
  surface: "engine-core | mcp-tool | config-schema | wad-content | cli"
  stability_tier: "ga | beta | alpha"   # k8s model, C3
  replacement_defined: true             # SEP-2596 rule: MUST exist & be Active (C6)
  codemod_candidate: true|false         # T criteria: syntactically localizable + >10 sites + ≤2 params
  window_releases: 3                    # default; see Stage 2
```

**Rules** (each evidence-anchored):
- R1. No deprecation without a named Active replacement (C6 SEP-2596; C3 k8s Rule #3).
- R2. Stability tiers set windows: `alpha` = any release; `beta` = ≥3 releases or 90 days; `ga`/MCP-tool surface = ≥2 minor releases AND ≥6 months (C3; C6 uses 12mo for protocol-level — we scale down for engine-internal surfaces but never below 2 releases for MCP tools).
- R3. Window clock anchors to RELEASE date of the version first marking deprecated, not to decision date (C6 — all breaks in one release share one earliest-removal).
- R4. Security-driven removals may shorten the window but require an explicit PIVOT_LOG entry (C6 expedited removal).

## Stage 2 — EXPAND: Ship the Replacement Alongside (Parallel Change)

**What**: Additive-first landing per Fowler expand→migrate→contract (T).

For our pillar case this means:
1. New MCP tool `oracle_list_node_keepers` lands FIRST; old `oracle_list_pillar_keepers` becomes a thin alias emitting a deprecation warning (C2 pydantic.v1 shim pattern).
2. Engine keeps auto-migrating legacy WAD keys (`pillars:`→`slots:` on load) — the shim is the loader, already implemented (`entity_registry.py:404-419`, Roc audit).
3. Response fields gain new names while old names keep populating with a warning comment in docs.

**Exit criterion**: both paths work, tests green on both, `make temple-grade` passes. Only then proceed to Stage 3.

## Stage 3 — ANNOUNCE: Communication Craft

**What**: Three artifacts, one release:

1. **Migration guide** at `docs/sprints/<migration-name>/02-migration-guide.md` following M26 LLM-friendly format. Structure rules (all from T craft findings):
   - Quick-start path FIRST: the copy-paste command sequence covering 80% of users, zero prerequisites.
   - Comparison table old→new (side-by-side, C2/T).
   - Edge cases organized by ERROR MESSAGE verbatim in headers — users navigate by pasted errors.
   - Verification checklist at the end (checkboxes, machine-checkable where possible).
   - Codemod/automation commands AT THE TOP.
   - Separate "Breaks now" vs "Deprecates today" sections with visual weight on the former.
2. **Changelog taxonomy**: every release notes file gains fixed headings `### Breaking` / `### Deprecated` / `### Removed` (C6 changelog pattern). Deprecated entries state: what, replacement link, removal release number.
3. **Runtime warnings**: deprecated code paths emit structured log warnings including the removal target release and guide URL — loud at use-time, never silent (C4 HA lesson; M23 alignment). Python-side: use `warnings.warn(..., DeprecationWarning)` for dev-facing, `FutureWarning` semantics for operator-facing paths (C1).

```python
# File: src/omega/oracle/deprecation.py (spec sketch — NOT implemented in this mission)
# Purpose: single helper so every deprecation warning is uniform and M23-honest
import warnings

def warn_deprecated(old: str, new: str, removal_release: str, guide_url: str) -> None:
    msg = (f"{old} is deprecated; use {new}. "
           f"Removal targeted for {removal_release}. Guide: {guide_url}")
    warnings.warn(msg, DeprecationWarning, stacklevel=3)
```

## Stage 4 — TRACK: Telemetry-Free Usage Measurement (M8)

**What**: Five zero-telemetry instruments, ranked by signal quality. NO phone-home exists anywhere in this design (M8 hard constraint; GKE-style insights explicitly rejected, C3).

```yaml
tracking_instruments:
  - id: "TI-1 local-warning-log"
    mechanism: "deprecation warnings append to $DATA_DIR/deprecations/hits.jsonl (local only)"
    signal: "which shim paths fire on THIS install"
    m8_status: "compliant — data never leaves machine"
  - id: "TI-2 ci-warnings-as-errors"
    mechanism: "our own CI runs python -W error::DeprecationWarning; dogfood gate"
    signal: "internal usage count hits zero before contract"
  - id: "TI-3 issue-label"
    mechanism: "dedicated GitHub label per migration (pydantic 'bug V2' pattern, C2)"
    signal: "user-reported friction volume over time"
  - id: "TI-4 opt-in-report-command"
    mechanism: "'omega report-deprecations' prints local hits.jsonl summary for user to paste into an issue — user-initiated, user-redacted"
    signal: "community-wide shim hit-rates WITHOUT automatic transmission"
  - id: "TI-5 maintainer-attestation"
    mechanism: "Node curators attest adoption levels at window review (SEP-2596's own answer to no telemetry, C6)"
    signal: "qualitative removal go/no-go input"
```

**Window-review ritual**: at each release inside a deprecation window, N10 verifier reviews TI-1..TI-5 and records verdict in PIVOT_LOG: extend window (allowed, logged) / hold / proceed to contract. Removal NEVER fires silently — it is always a decided, logged act.

## Stage 5 — CONTRACT + LEARN: Remove, Then Distill

**What**: On window expiry with review verdict = proceed:
1. Delete shim paths in one release; that release's migration guide gains a "Removed in X.Y" section (C3 per-release guides).
2. Run the blameless post-mortem within one week → feeds REHEARSAL_LEARNING_PLAN_20260822_v4.md pipeline.
3. Contract complete when grep proves zero references outside archive/decision-log immutables (Roc verification checklist pattern).

## Mapping Onto Existing Omega Machinery

| Playbook element | Omega home | Owner |
|---|---|---|
| Break classification ticket | PIVOT_LOG.md decision entry | Kali ratifies |
| Migration guide doc | `docs/sprints/<name>/02-migration-guide.md` (M26 category 10) | Researcher authors, N10 validates |
| llms.txt generation | existing `make sprint-plan-llm` target | build-side |
| Runtime warning helper | `src/omega/oracle/deprecation.py` (future impl) | N6/N3 |
| Local hit log | `$DATA_DIR/deprecations/hits.jsonl` | N2 datastore schema |
| Window review verdicts | PIVOT_LOG entries | N10 verifier |
| Post-mortem distillation | Soul pipeline L1→L2→L3 (see learning plan) | Scribe |

## Explicitly NOT Doing

- Any network transmission of usage data (M8 absolute)
- Generative-AI codemods for config/YAML (C4 anti-pattern: deterministic only)
- 12-month protocol-grade windows for engine-internal surfaces (we are not a multi-vendor protocol yet; 2–3 releases suffices, revisit if community WAD ecosystem matures)

*End of spec. Evidence: MIGRATION_CASE_STUDIES_EVIDENCE_20260822_v4.md · Learning capture: REHEARSAL_LEARNING_PLAN_20260822_v4.md*

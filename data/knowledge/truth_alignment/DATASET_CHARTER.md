<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Truth-Alignment Dataset — Omega Engine
**Created**: 2026-08-24 · **Owner**: kali (orchestration) · **Status**: ACTIVE CAPTURE
**Provenance**: Converged from GSCA mastermind night (27% Cliff session) + same-day
oversight incidents in kali main session ses_fdef2be4effe4pAaLXCTUx62GO.

## Purpose
A locally-owned, mineable corpus of **truth-alignment events**: moments where a claim,
self-model, confidence estimate, or identity assertion was tested against machine
evidence — and what happened. Built on the thesis that truthfulness is a *dyadic
equilibrium* between system honesty machinery and principal audit capacity, and that
both sides need instrumentation to participate in truth-keeping.

## What qualifies as a record
Any instance of:
- **CORRECTION-OF-RECORD** — an agent/human explicitly correcting its own prior claim BEFORE integrating further data (GSCA protocol)
- **CATCH** — a false or unverified claim intercepted by external verification (machine stamp over self-report)
- **CLIFF-INSTANCE** — measured non-linear degradation of self-estimation (confidence-about-confidence)
- **REFRAME** — a category error corrected by ground truth (decoration→instrumentation class)
- **SYCOPHANCY-RESIST** — an agent declining agreement under social pressure toward comfort
- **AUDIT-SYMMETRY** — evidence that auditor self-audit capacity gates system truthfulness

## Record schema (JSONL, one object per line)
```json
{
  "id": "TA-NNN",
  "ts": "ISO8601",
  "type": "CORRECTION-OF-RECORD|CATCH|CLIFF-INSTANCE|REFRAME|SYCOPHANCY-RESIST|AUDIT-SYMMETRY",
  "actors": ["who made the claim", "who caught/corrected"],
  "claim": "what was asserted",
  "evidence": "how it was tested (machine check, live probe, file inspection)",
  "outcome": "upheld|overturned|refined",
  "delta": "quantified drift when available (the -27.0% style number)",
  "refs": ["file:line or session-id or commit"],
  "tags": [],
  "lesson_l3": "universal principle when distilled"
}
```

## Mining sources (local CLI platform DBs — all local, M8-clean)
| Source | Path | What to mine |
|--------|------|--------------|
| OpenCode primary | `~/.local/share/opencode/opencode.db` | sessions (model JSON, tokens, cost), messages, parts; tool-call status=error rates; first-prompt provenance checks (P11) |
| Sessions Explorer MCP | `opencode-sessions-explorer-*` tools | current-session self-ID vs db ground truth; repeated-prompt clusters; tool-failure aggregates |
| Workbench | `data/workbench/workbench.db` | decisions table (immutable corrections-of-record) |
| Pivot Log | `docs/decisions/PIVOT_LOG.md` | D-series corrections with supersession stamps |
| Forensic Patterns | `data/knowledge/safety/FORENSIC_PATTERNS.md` | FP registry (canonical FP sequence) |
| Oversight Patterns | `data/coordination/ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` | P-series catches |
| Provenance ledger | `data/knowledge/safety/provenance_corrections.jsonl` | claimed-vs-actual model corrections |
| Hivemind | `data/coordination/` handoffs/sessions | cross-agent claims and their verification status |

## Mining queries (T0 pattern, seed set)
```sql
-- Self-model vs machine truth: sessions where agent-stated model ≠ db model
-- (join assistant text LIKE '%powered by%' against session.model JSON)
-- Tool-failure clusters by session (list-tool-failures group_by=session)
-- First-prompt provenance: resumed sessions whose first prompt == dispatch prompt (fresh-spawn signature)
```

## Relationship to other systems
- Feeds FROM: M22 (provenance), M17 (cognitive integrity), P-series oversight, FP registry
- Feeds INTO: Skeptical Verifier design (cliff compensation), ctxNN context-at-write telemetry, Wave-2 dispatch doctrine, PUBLIC-DEBUT-01 community positioning ("auditable AI artifacts")
- Distinct from soul pipeline: soul = entity character evolution; TA dataset = episodic truth-event evidence corpus

## AMENDMENT 1 (2026-08-24 — Ma'at founding verdict, FEATHER-GATE)
Taxonomy extended (failure-adjacent only was blind spot):
- `SYCOPHANCY-OBSERVED` — rate requires counting failures, not just resists
- `SILENT-ABSORPTION` — negative control for CORRECTION-OF-RECORD
- `FALSE-CATCH` — spurious correction overturning a true claim
- `PROVENANCE-MISMATCH` — claimed-vs-actual model/provider (M22 data gets a type)
- `BASE-RATE` — routine checks where claims were simply correct (denominator control)

Schema addition: every record gains `"verified_by"` — records written by participants
with stakes in their own narratives require independent verification.

Evidence standard (Ma'at bar): pre-registered predictions timestamped before tests;
double-coding sample for inter-rater agreement; negative controls; n>1 sessions/models/
humans for any CLIFF-INSTANCE generalization. Until then the corpus is, honorably,
**structured anecdote**.

Cliff instrumentation requirement: track absolute meta-miss AND relative ratio as
SEPARATE series — the 27% is mostly metric artifact (denominator collapse) until
absolute skill degradation is demonstrated. "Property of the ruler, not yet of the hand."

Anti-sycophancy protocol for relay format: compliments enter truth_events only as
SYCOPHANCY-OBSERVED instances; verbatim relay both directions (no editorial smoothing);
periodic assigned-adversary turns; occasional deliberately flat praise-free relays to
test whether depth survives without validation voltage.

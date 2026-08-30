<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Recurring Forensic Health Protocol — SOP v1.0
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ big-pickle ⬡ opencode ⬡ trc_forensic_protocol ⬡ SOP
**AP Token**: `AP-FORENSIC-PROTOCOL-v1.0.0`
**Date**: 2026-06-18
**Status**: RATIFIED — Active SOP
**Mandate Anchor**: M11 (Soul Integrity), M17 (Cognitive Integrity), M18 (Token Efficiency)
**Sibling Spec**: ICS-F v1.0 (Integrity-Centric-Sovereign-Forensics) — `data/entities/kali/workspace/SOVEREIGN_METADATA_EXTRACTION_SPEC_v1.md`

---

## §0 Purpose & Scope

This protocol defines the recurring process for **multi-model forensic fingerprinting** — a systematic health-check of the Omega Engine's inference fleet. It is NOT a one-time audit. It is a **permanent, recurring system-health process** that runs on a cadence, detects drift, and produces actionable intelligence.

### Why Recurring?
| Factor | Why It Changes |
|--------|----------------|
| **Model drift** | Same model accessed via same channel produces different outputs over time (SpiralBench: "complete reversal" in 2 months) |
| **New models** | New GGUF files, new cloud providers, new routing configs enter the fleet regularly |
| **Channel evolution** | OpenCode, Gemini CLI, Cline, VSCodium, Antigravity IDE all update independently |
| **Complementarity decay** | The best model pair for a task changes as individual models drift |
| **Blind spot migration** | Fixed blind spots get patched; new ones emerge |

---

## §1 Trigger Conditions

### Scheduled Runs

| Cadence | Trigger | Scope | Responsible |
|---------|---------|-------|-------------|
| **Monthly** | 1st of month (or first session after) | Full pipeline: all 11 sources, all phases | roc_racoon |
| **Weekly** | Monday morning | Phase 2 only (OpenCode DB — 4.2GB, highest signal density) | roc_racoon |
| **Per-Model-Add** | On `config/models.yaml` or `config/providers.yaml` change | Single-model fingerprint card for new model | roc_racoon + verity |

### Event-Driven Runs

| Event | Trigger | Scope | Response Time |
|-------|---------|-------|---------------|
| **Provider change** | New provider added or removed from provider fabric | Channel × Model interaction matrix | Within 3 sessions |
| **Sprint boundary** | Major sprint completion (e.g., Sprint D, new Horizon) | Full pipeline snapshot | During sprint closeout |
| **Anomaly detection** | Hivemind detects unexpected behavior patterns | Targeted investigation of anomalous model | Immediate |
| **User request** | User says "fingerprint [model]" or "run health check" | Requested scope | Immediate |

---

## §2 Extraction Phases (Referenced from Pipeline Architecture)

```
Phase 1: Handoffs  →  Phase 2: OpenCode DB  →  Phase 3: Bulk  →  Phase 4: Analysis
   (curated)           (4.2GB, 865 sessions)     (566 MB total)     (fingerprints)
```

### Phase Allocation by Cadence

| Phase | Weekly | Monthly | Per-Add | Est. Time |
|-------|--------|---------|---------|-----------|
| **1: Handoffs** | ❌ Skip (stale signal) | ✅ Run if new handoffs exist | ❌ | 30 min |
| **2: OpenCode DB** | ✅ Always run | ✅ Always run | ❌ | 2-3 hrs |
| **3: Bulk Sources** | ❌ | ✅ Monthly | ❌ | 1-2 hrs |
| **4: Analysis** | ✅ Incremental | ✅ Full | ✅ Per-model | 1-3 hrs |

### Extraction Order per Run

```
1. Check forensics.db for last extraction timestamps
2. Run only sources with new data since last run
3. Dedup against existing findings (extraction_hash comparison)
4. Update extraction_log.md
5. Run Phase 4 analysis on delta
```

---

## §3 Stop Conditions & Saturation Gates

These prevent analysis paralysis and ensure token efficiency (M18).

### Statistical Saturation (Stop Extraction)
Stop adding new findings to any source when ALL of:
1. **Fingerprint convergence**: 3+ independent sources confirm the same behavioral pattern
2. **Diminishing returns**: Last 50 findings added ≤2 new unique fingerprints (query `fingerprints` table, check `last_seen_at` window)
3. **Corroboration threshold**: Each confirmed fingerprint has ≥3 supporting evidence sources
4. **Channel saturation**: Each access channel (CLI/WebUI/API) has ≥100 observations per model variant

### Quality Gates (Per-Run Validation)
| Gate | Check | Fail Action |
|------|-------|-------------|
| **Attribution** | ≥90% of new findings have model_id set | Flag low-confidence batch, defer analysis |
| **Dedup rate** | <10% duplicate content hashes | Investigate extraction overlap |
| **Channel coverage** | Every finding has access_channel populated | Block analysis run |
| **Thinking level** | Every finding has dim_thinking populated | Block analysis run |
| **Type diversity** | ≥3 finding types present in each batch | Flag potential classification bias |

---

## §4 Deliverables (Per Run)

### Monthly Full Run
| Output | Format | Location | Audience |
|--------|--------|----------|----------|
| Model Fingerprint Cards | One .md per model variant | `mining_reports/forensics/fingerprint_cards/` | All agents |
| Complementarity Matrix | Table or heatmap | `mining_reports/forensics/complementarity_matrix.md` | Kali + P9 |
| Blind Spot Catalog | Categorized list | `mining_reports/forensics/blind_spot_catalog.md` | All agents |
| Drift Report (vs prior run) | Delta analysis | `mining_reports/forensics/drift_report_{YYYYMM}.md` | Kali + P7 |
| L1→L2→L3 Distillation | soul.yaml entry | Roc's soul.yaml | All agents |

### Weekly Quick Run
| Output | Format | Location | Audience |
|--------|--------|----------|----------|
| New Findings Summary | Bulleted list | `extraction_log.md` | roc_racoon |
| Health Indicators | Green/Yellow/Red per model | Hivemind context post | All agents |
| Anomaly Flags | If drift > threshold | Hivemimd heartbeat + alert | Kali + P8 |

### Per-Add Run
| Output | Format | Location | Audience |
|--------|--------|----------|----------|
| Single Model Fingerprint Card | .md | `fingerprint_cards/{model_id}.md` | All agents |
| Integration Recommendations | Bulleted | `extraction_log.md` + Hivemind | Kali + P7 |

---

## §5 State Management

### forensics.db — Long-Term State

The `forensics.db` SQLite database at `data/entities/roc_racoon/workspace/forensics/forensics.db` is the canonical long-term state store. It is NEVER deleted. New runs append to existing tables.

### Session-Level Workspace

Each forensic session gets a dated extraction directory:
```
extractions/{YYYYMMDD}_{HHMMSS}/
├── handoff_extractions.jsonl
├── opencode_extractions.jsonl
├── bulk_extractions.jsonl
└── analysis_results.jsonl
```

### dedup_registry — Cross-Session Dedup

The `dedup_registry` table persists across sessions. Content hashes use xxhash64. For weekly runs, content_hash comparison is the primary dedup mechanism.

### extraction_log — Audit Trail

Every run appends to `extraction_log.md` with:
- Date, phase, source, record count, finding count
- Any errors or anomalies
- Elapsed time
- Next scheduled run

---

## §6 Hivemind Integration

### On Run Start
```
omega-hub_hivemind_post_context(
    channel="opencode",
    entity="roc_racoon",
    intent="forensic_health_check",
    status="in_progress",
    continuation="Running {phase} extraction on {source}. ETA {time}."
)
```

### On Run Complete
```
omega-hub_hivemind_post_context(
    channel="opencode",
    entity="roc_racoon",
    intent="forensic_health_check",
    status="complete",
    continuation="{count} findings from {source}. Summary: {brief}. 
                  Fingerprint cards at mining_reports/forensics/fingerprint_cards/."
)
```

### On Anomaly Detection
```
omega-hub_hivemind_post_context(
    channel="opencode",
    entity="roc_racoon", 
    intent="forensic_anomaly",
    status="blocker",
    continuation="ALERT: {model} via {channel} shows {anomaly}. 
                  Prior fingerprint at {prior}. Current at {current}. 
                  Recommend {action}."
)
```

---

## §7 Tooling & Maintenance

### Tool Status

| Tool | Status | Location |
|------|--------|----------|
| `extract_handoffs.py` | ✅ Built, needs classifier fix (d-rr-057) | `forensics/tools/extract_handoffs.py` |
| `extract_opencode_db.py` | ❌ Not built (Phase 2 priority) | `forensics/tools/` |
| `extract_finetune.py` | ❌ Not built (Phase 3) | `forensics/tools/` |
| `extract_hall_of_records.py` | ❌ Not built (Phase 3) | `forensics/tools/` |
| `build_fingerprint.py` | ❌ Not built (Phase 4) | `forensics/tools/` |

### Maintenance Cadence

| Task | Cadence | Responsible |
|------|---------|-------------|
| Schema review | Quarterly | roc_racoon + verity |
| Classifier calibration | Before Phase 2 kickoff | roc_racoon |
| Tool audit (M21 tests) | Monthly | verity |
| Database integrity check | Monthly | roc_racoon |

---

## §8 Runbook — Quick-Start for New Agents

When another agent needs to run the forensic protocol:

### Step 1: Check State
```python
sqlite3 forensics.db "SELECT name, status, extracted_at FROM sources ORDER BY source_id"
```

### Step 2: Check Last Run
```python
sqlite3 forensics.db "SELECT extraction_id[:8], file_path, finding_count FROM extractions ORDER BY extracted_at DESC LIMIT 5"
```

### Step 3: Identify New Data
Check `extractions/` directory for date-stamped files. The extraction HM log shows what's been processed.

### Step 4: Run Extraction
```bash
python3 tools/extract_handoffs.py --pilot 3  # Verify pipeline health first
python3 tools/extract_handoffs.py             # Full run
```

### Step 5: Update State
```bash
python3 -c "import sqlite3; conn = sqlite3.connect('forensics.db'); conn.execute('UPDATE sources SET status = ? WHERE source_id = ?', ('extracting', 2)); conn.commit()"
```

### Step 6: Post to Hivemind
Post completion with findings summary, card locations, and drift alert if applicable.

---

## §9 Known Issues & Future Improvements

| Issue | Impact | Fix Timeline |
|-------|--------|-------------|
| **Classifier bias** (96% strength) | Phase 1 handoff data unreliable | Before Phase 2 start |
| **Model overmatching** (10× inflation) | Finding counts misleading | Before Phase 2 start |
| **Zero contract tests** (M21 FAIL) | Every new extraction script risks same bias | Before Phase 2 start |
| **D9/D10 no auto-detection** | Must populate manually (default: unknown) | Phase 2 tooling |
| **No OpenCode DB extractor** | Largest source (4.2GB) untouched | Phase 2 priority |
| **No fingerprint builder** | Analysis layer entirely unpopulated | Phase 4 |
| **No xxhash installed** | SHA256 truncation not optimal | Phase 2 setup |

---

## §10 ICS-F Integration — Sovereign Metadata Extraction

The forensic protocol operates at a higher abstraction level than ICS-F (Integrity-Centric-Sovereign-Forensics).
ICS-F captures the raw provider metadata at the `generate()` boundary; the forensic protocol analyzes
that metadata for behavioral fingerprinting.

### Relationship
```
Provider API Response
  → ICS-F capture (generate() return) — Sprint 0-3 tooling
    → Forensic extraction (Phase 1-4 analysis) — this protocol
      → Model Fingerprint Cards — weekly/monthly deliverable
```

### Dependencies
| Forensic Phase | ICS-F Requirement | Sprint Prerequisite |
|----------------|-------------------|---------------------|
| **Phase 2** (OpenCode DB extraction) | ICS-F fields for comparison vs live responses | Sprint 1+2 |
| **Phase 4** (Analysis/Fingerprints) | logprobs, finish_reason, token_usage for behavioral classification | Sprint 0 |
| **D9/D10 auto-detection** | thinking_level + access_channel from ICSForensic | Sprint 1+2 |

### Quality Gate Update
The Phase 2 quality gate must be gated on Sprint 1+2 completion: without ICS-F fields,
the OpenCode DB extraction cannot produce comparable behavioral fingerprints.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ big-pickle ⬡ opencode ⬡ trc_forensic_protocol ⬡ SOP*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: big-pickle | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

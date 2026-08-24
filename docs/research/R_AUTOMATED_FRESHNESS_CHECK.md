# 🔱 GAP 5: Automated Freshness Checker Design
**AP Token**: `AP-GAP5-FRESHNESS-CHECKER-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_gap5_freshness ⬡ RESEARCH COMPLETE

**Date**: 2026-07-18
**Status**: IMPLEMENTATION READY
**Dependencies**: GAP 1 (AA API), GAP 2 (HF Hub params), GAP 3 (Validation schema), GAP 4 (DB schema)

---

## 📋 EXECUTIVE SUMMARY

This document details the design and implementation of an **Automated Freshness Checker** for the Omega Model Registry. The checker monitors staleness of model data across two primary sources:

1. **Hugging Face Hub** — `lastModified` timestamps, commit SHAs, weight file changes
2. **Artificial Analysis** — Intelligence Index version, model evaluation dates, leaderboard presence

Integrates with existing `background_researcher` loop (15-min systemd timer) and Hivemind coordination for stale model re-validation.

---

## 🔬 RESEARCH FINDINGS

### HF Hub Freshness Signals

| Signal | API Endpoint | Update Trigger | Reliability |
|--------|--------------|----------------|-------------|
| `lastModified` | `GET /api/models/{model_id}` | Any commit (README, config, weights) | High — but noisy (README edits) |
| `sha` | Same endpoint | Any commit | High — precise change detection |
| `siblings` (file list) | Same endpoint | File add/remove | High — weight changes detectable |
| `tags` / `pipeline_tag` | Same endpoint | Tag changes | Medium — capability signals |

**Key insight**: `lastModified` updates on ANY commit. For weight changes, check `siblings` for `.safetensors`/`.bin` file changes. HF Hub supports `sort=lastModified&direction=-1` for efficient polling.

### Artificial Analysis Update Cadence

| Version | Date | Type | Key Changes |
|---------|------|------|-------------|
| v4.0 | 2026-01-06 | Major | Replaced 3 saturated benchmarks, recalibrated 73→50 |
| v4.0.4 | 2026-03 | Patch | Methodology update |
| v4.1 | 2026-06-15 | Major | 3 benchmark upgrades, IFBench removed, agentic focus, per-task metrics |
| v4.1+ | 2026-07 | Incremental | New model evaluations added continuously |

**Critical findings from AA methodology**:
- **Scores frozen at addition**: "GDPval-AA v2 Elo scores are frozen at the time of a model's addition"
- **Continuous evaluation**: "We will continue to run it and publish results on new model releases"
- **Version incompatibility**: v4.0 vs v4.1 scores NOT directly comparable (different benchmarks, weights)
- **Confidence interval**: <±1% on composite, wider on individual evals
- **Public methodology**: https://artificialanalysis.ai/methodology/intelligence-benchmarking

**Implication**: Freshness check must track:
1. AA Index version used for each model's scores
2. Whether model has been re-evaluated under current index version
3. New model additions to AA leaderboard

---

## 🎯 FRESHNESS CHECKER DESIGN

### Staleness Thresholds

| Data Type | Threshold | Rationale |
|-----------|-----------|-----------|
| Capability scores (AA) | 90 days | AA major versions ~quarterly; scores frozen at add time |
| Parameter data (HF) | 180 days | Model weights rarely change; config updates more frequent |
| Model card metadata | 30 days | Tags, pipeline_tag, description can change |
| Validation status | 7 days | Validation should re-run weekly |

### Check Frequency Tiers

| Tier | Models | Frequency | Trigger |
|------|--------|-----------|---------|
| **Critical** | Top 10 by usage/downloads | Daily | High impact if stale |
| **Standard** | Models 11-50 | Weekly | Balance freshness vs API calls |
| **Low** | Models 50+ | Monthly | Diminishing returns |
| **On-demand** | Queried model | Immediate | User requests specific model |

### Data Sources & APIs

```python
# HF Hub - no auth for public models
HF_API = "https://huggingface.co/api/models/{model_id}"
# Returns: lastModified, sha, tags, siblings, pipeline_tag, downloads, likes

# Artificial Analysis - requires API key (free tier: 100 req/day)
AA_API = "https://artificialanalysis.ai/api/v2/language/models/free"
# Returns: intelligence_index, version, benchmarks, pricing, performance, params
# Pro: /api/v2/language/models (full evals, blended pricing, percentiles)
```

---

## 🏗️ IMPLEMENTATION ARCHITECTURE

### Core Component: `FreshnessChecker` Class

**Location**: `src/omega/workers/freshness_checker.py`

```python
class FreshnessChecker:
    """Automated model registry freshness monitoring."""
    
    def __init__(self, db_path: Path, aa_api_key: Optional[str] = None):
        self.db_path = db_path
        self.aa_api_key = aa_api_key
        self.hf_client = HuggingFaceHubClient()
        self.aa_client = ArtificialAnalysisClient(api_key=aa_api_key) if aa_api_key else None
    
    def check_all(self, tier: str = "standard") -> FreshnessReport:
        """Run freshness checks for models in specified tier."""
    
    def check_model(self, model_id: str, hf_model_id: str) -> ModelFreshnessResult:
        """Check freshness for a single model."""
    
    def update_staleness(self, results: List[ModelFreshnessResult]) -> int:
        """Update validation_status in DB, return count of newly stale models."""
```

### Data Models

```python
@dataclass
class ModelFreshnessResult:
    model_id: str
    hf_model_id: str
    checked_at: datetime
    
    # HF Hub signals
    hf_last_modified: Optional[datetime]
    hf_sha: Optional[str]
    hf_days_since_modified: Optional[int]
    hf_weight_files_changed: bool
    
    # AA signals
    aa_index_version: Optional[str]  # e.g., "v4.1"
    aa_intelligence_index: Optional[int]
    aa_last_evaluated: Optional[datetime]
    aa_days_since_eval: Optional[int]
    aa_model_in_leaderboard: bool
    
    # Staleness assessment
    capability_stale: bool
    parameter_stale: bool
    metadata_stale: bool
    overall_stale: bool
    staleness_reasons: List[str]
    
    # Recommended actions
    needs_revalidation: bool
    needs_reenrichment: bool
```

### Database Updates

```sql
-- Update validation_status based on freshness check
UPDATE models SET 
    validation_status = CASE 
        WHEN overall_stale THEN 'stale'
        WHEN needs_revalidation THEN 'pending'
        ELSE 'valid'
    END,
    validation_errors = json_array(staleness_reasons),
    last_validated = datetime('now'),
    hf_hub_last_modified = ?,
    enrichment_last_run = datetime('now')
WHERE model_id = ?;
```

---

## ⏰ SCHEDULING & INTEGRATION

### Option A: Extend Background Researcher (Recommended)

```python
# In src/omega/workers/background_researcher/loop.py

async def _grow_frontier(self):
    # ... existing gap source crawling ...
    
    # NEW: Run freshness check every N cycles
    if self.cycle_count % 4 == 0:      # Every hour (4 × 15min)
        await self._run_freshness_check("standard")
    
    if self.cycle_count % 96 == 0:     # Daily (96 × 15min)
        await self._run_freshness_check("critical")
```

**Pros**: Single process, shared infrastructure, coordinated with research cycles
**Cons**: Couples freshness to researcher loop

### Option B: Independent Systemd Timer

```ini
# /etc/systemd/system/omega-freshness-checker.timer
[Timer]
OnCalendar=hourly
Persistent=true
RandomizedDelaySec=15min

# Critical tier daily at 06:00 UTC
OnCalendar=*-*-* 06:00:00
Persistent=true
```

```ini
# /etc/systemd/system/omega-freshness-checker.service
[Service]
Type=oneshot
User=arcana-novai
WorkingDirectory=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine
ExecStart=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.venv/bin/python -m src.omega.workers.freshness_checker --tier standard --notify
Environment=AA_API_KEY=${AA_API_KEY}
```

**Pros**: Independent, reliable, standard Linux scheduling
**Cons**: Separate process, needs AA_API_KEY in environment

### Option C: Hivemind-Coordinated (Distributed)

```python
# Register as Hivemind task
await hivemind_submit_handoff(
    target_channel="opencode",
    target_entity="researcher",
    source_channel="scheduler",
    source_entity="kali",
    task="Run freshness check on critical tier models",
    priority=1
)
```

**Pros**: Distributed, observable, integrates with agent fleet
**Cons**: More complex, requires Hivemind running

---

## 🔔 NOTIFICATION & ACTION PIPELINE

### Staleness Detection → Action Flow

```
Freshness Check Runs
       │
       ▼
┌──────────────────┐
│ Stale Models     │
│ Detected         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Update DB:       │
│ validation_status│
│ = 'stale'        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Hivemind         │
│ Notification     │
│ to Researcher    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Researcher       │
│ Picks up task:   │
│ "Re-validate     │
│ stale models"    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Enrichment       │
│ Pipeline Runs    │
│ (AA + HF Hub)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Validation       │
│ Pipeline Runs    │
│ (Schema + Cross- │
│  field)          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ validation_status│
│ = 'valid'        │
└──────────────────┘
```

### Hivemind Notification Format

```json
{
  "packet_id": "freshness_20260718_143000",
  "source_channel": "scheduler",
  "source_entity": "kali",
  "target_channel": "opencode",
  "target_entity": "researcher",
  "task": "Re-validate 3 stale models: gemma-4-31b, llama-4-scout, deepseek-v4-flash",
  "context": "Freshness checker (standard tier) detected staleness in 3 models",
  "priority": 1,
  "metadata": {
    "stale_models": [
      {"model_id": "gemma-4-31b", "reasons": ["capability_stale", "hf_metadata_stale"]},
      {"model_id": "llama-4-scout", "reasons": ["capability_stale"]},
      {"model_id": "deepseek-v4-flash", "reasons": ["parameter_stale"]}
    ],
    "check_run_at": "2026-07-18T14:30:00Z",
    "tier": "standard"
  }
}
```

---

## 📊 MONITORING & OBSERVABILITY

### Metrics to Track

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `freshness_check_duration_seconds` | Time per check run | > 300s |
| `models_checked_total` | Models processed per run | N/A |
| `models_stale_total` | Models marked stale | > 20% of registry |
| `api_calls_hf_total` | HF Hub API calls | Rate limit approach |
| `api_calls_aa_total` | AA API calls | > 80/day (free tier) |
| `stale_models_revalidated` | Models fixed after stale | Should trend up |

### Health Monitor Integration

```python
# In health_monitor.py
async def probe_freshness_checker(self) -> ComponentHealth:
    """Check freshness checker last run time and staleness rate."""
    # Query DB for last_validated timestamps
    # Check stale_rate = stale_count / total_count
    # Return ComponentHealth with status
```

---

## 📦 DELIVERABLES

| Artifact | Path | Status |
|----------|------|--------|
| Research Doc | `docs/research/R_AUTOMATED_FRESHNESS_CHECK.md` | ✅ This document |
| Core Implementation | `src/omega/workers/freshness_checker.py` | ✅ Complete |
| CLI Wrapper | `scripts/check_model_freshness.py` | ✅ Complete |
| Systemd Service | `deploy/systemd/omega-freshness-checker.service` | ✅ Complete |
| Systemd Timer | `deploy/systemd/omega-freshness-checker.timer` | ✅ Complete |
| Hivemind Integration | Built into `freshness_checker.py` | ✅ Complete |

---

## 🔗 DEPENDENCIES & SEQUENCING

```
Phase 1 (Parallel):
├── GAP 1: Artificial Analysis API ──────┐
├── GAP 2: HF Hub Parameter Extraction ──┤     (provides data sources)
└── GAP 4: DB Schema Migration ──────────┘     (provides storage)

Phase 2 (Sequential):
├── GAP 3: Validation Pipeline ──────────→ Requires Phase 1 complete
└── GAP 5: Freshness Checker ────────────→ Requires Phase 1 + 3 + 4 complete
```

**Must run after**: GAP 4 (DB schema must have `validation_status`, `hf_hub_last_modified`, `enrichment_last_run`, `benchmark_data_date` columns)

---

## ✅ SUCCESS CRITERIA

| Metric | Target |
|--------|--------|
| Freshness check completes | < 5 minutes for 50 models |
| API calls within limits | HF Hub: no rate limit; AA: < 80/day free tier |
| Stale detection accuracy | > 95% (manual audit) |
| Re-validation automation | 100% of stale models picked up by Researcher |
| DB update atomicity | Zero partial updates |
| Hivemind notification delivery | 100% for critical tier |

---

## 🚀 DEPLOYMENT CHECKLIST

- [ ] Add `AA_API_KEY` to environment / systemd credentials
- [ ] Install systemd units: `sudo cp deploy/systemd/omega-freshness-checker.* /etc/systemd/system/`
- [ ] Reload: `sudo systemctl daemon-reload`
- [ ] Enable timer: `sudo systemctl enable --now omega-freshness-checker.timer`
- [ ] Verify: `systemctl status omega-freshness-checker.timer`
- [ ] Test run: `python scripts/check_model_freshness.py --tier standard --dry-run`
- [ ] Verify Hivemind handoff appears in `data/coordination/handoff/pending/`
- [ ] Monitor first few runs via `journalctl -u omega-freshness-checker.service -f`

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_gap5_freshness ⬡ RESEARCH COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

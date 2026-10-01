<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Observability & Tracking Enhancement Plan (OTEP v2.0.0)

**AP Token**: `AP-OTEP-v2.0.0`
⬡ OMEGA ⬡ OBSERVABILITY ⬡ PLANNING ⬡ 2026-0810

**Date**: 2026-08-10
**Author**: jem (Sovereign Synthesizer)
**Reviewer**: Nemotron 3 Ultra (Expert Analysis)
**Status**: DRAFT — Pending Approval
**Priority**: P0 (Critical Observability Gap)

---

## 🎯 Executive Summary

On 2026-08-10, we spent 1+ hour and 300K tokens investigating why Nemotron 3 Ultra streaming timeouts stopped on 2026-07-30. The answer was buried in scattered git history, outdated AGENTS.md documentation, and unverified claims.

**Root cause of the waste:** No systematic observability layer. No unified telemetry. No causal reasoning. No provider-specific intelligence.

**This plan proposes 11 workstreams (8 original + 3 Nemotron additions) to build a self-observing system.**

**Key Nemotron Insight:** *"You don't need more logs. You need a nervous system."*

---

## 📋 Workstreams

### WS-9: Unified Telemetry Bus (P0 — Architectural Prerequisite)

**Nemotron Addition.** All other workstreams produce data. This is the single write path.

**Problem:** WS-1 through WS-8 create *more* data silos if they don't share an ingestion layer.

**Problem:** Without a unified bus, correlating config changes with error rates requires manual cross-referencing.

**Solution:** Single in-process telemetry bus that all observability events flow through.

**Proposed Location:** `src/omega/observability/telemetry_bus.py`

```python
# src/omega/observability/telemetry_bus.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

class TelemetryType(Enum):
    CONFIG_CHANGE = "config_change"
    ERROR_RATE = "error_rate"
    UPDATE_DETECTED = "update_detected"
    CONFIG_DRIFT = "config_drift"
    UNKNOWN_SOLVED = "unknown_solved"
    PROVIDER_HEALTH = "provider_health"

@dataclass
class TelemetryEvent:
    timestamp: datetime
    event_type: TelemetryType
    source: str  # Who emitted this
    data: dict   # Event-specific payload
    trace_id: str  # For correlation

class TelemetryBus:
    """Single ingestion point for all observability data.
    
    Write paths:
    1. MetricsDB (structured, queryable)
    2. Hivemind (coordination)
    3. Audit log (immutable, append-only)
    4. Alert rules (real-time evaluation)
    """
    
    async def emit(self, event: TelemetryEvent) -> None:
        # 1. Write to MetricsDB
        await self._write_to_metrics_db(event)
        # 2. Forward to Hivemind for coordination
        await self._forward_to_hivemind(event)
        # 3. Append to audit log
        await self._append_to_audit_log(event)
        # 4. Check alert rules
        await self._evaluate_alert_rules(event)
    
    async def query(self, event_type: TelemetryType, 
                    start: datetime, end: datetime) -> list[TelemetryEvent]:
        """Query telemetry history for correlation analysis."""
        ...
```

**Why P0:** Without this, every other workstream produces isolated data. The bus enables WS-10 (Causal Graph) to correlate events automatically.

**Effort:** 2 hours (skeleton + MetricsDB integration)
**Impact:** HIGH — Architectural foundation for all observability

---

### WS-1: Config Change Log (CCL) — Auto-Captured

**Problem:** Config changes are scattered across git history, backup files, and human memory. Manual entry = human error.

**Solution:** Centralized log with auto-capture from git hooks.

**Proposed Location:** `data/coordination/CONFIG_CHANGE_LOG.md`

**Schema:**
```markdown
| Date | What Changed | Where | Why | Expected Effect | Actual Effect | Verified By | Status |
|------|-------------|-------|-----|-----------------|---------------|-------------|--------|
| 2026-07-19 | Added streaming config | config/providers.yaml | Nemotron slow streams | Reduced timeouts | TBD | Commit 982fbba9 | ⚠️ PENDING |
| 2026-07-30 | Added chunkTimeout:60000 | opencode.json | SSE keepalive pings | Reduced failures | TBD | AGENTS.md | ⚠️ PENDING |
| 2026-08-05 | OpenCode v1.18.14 installed | OpenCode binary | Native retry logic | Errors → 0% | 0% achieved | Changelog | ✅ VERIFIED |
| 2026-08-09 | Config refactoring | opencode.json | Cleanup | chunkTimeout REMOVED | No effect | Git diff | ✅ VERIFIED |
```

**Auto-Capture Mechanism:**
```bash
# .git/hooks/pre-commit (or pre-commit framework)
# Parses git diff for config files, generates CCL entry draft
python scripts/auto_ccl_entry.py --diff "$1"
```

**Maintenance Rules:**
- Auto-generated entries start as ⚠️ PENDING
- Weekly review updates ACTUAL EFFECT and STATUS
- Every entry must link to evidence (commit, changelog, test result)

**Effort:** 1 hour (initial setup + backfill + git hook)
**Impact:** HIGH — Would have prevented today's investigation waste

---

### WS-6: AGENTS.md Claims Audit (P0 — Stop Misinformation)

**Problem:** AGENTS.md contains unverified claims that waste time when trusted as fact.

**Solution:** Audit all claims, verify or correct each one.

**Current Claims to Audit:**

| Claim in AGENTS.md | Current Status | Evidence | Correction |
|-------------------|----------------|----------|------------|
| "better-opencode-retries plugin fixed streaming timeout" | ❌ FALSE | grep shows plugin never loaded | Remove claim |
| "chunkTimeout: 60000 avoids streaming timeout" | ⚠️ UNVERIFIED | Setting removed, needs testing | Mark unverified |
| "OpenCode v1.18.16 has streaming fix" | ✅ PARTIAL | v1.18.14 had the fix | Clarify version |
| "Plugin listens to session.error events" | ⚠️ UNVERIFIED | Source code shows this, but event delivery not guaranteed | Add caveat |
| "Nemotron 3 Ultra has 30s+ chunk gaps" | ✅ VERIFIED | opencode.db error logs | Keep, add source |

**Deliverable:** Updated AGENTS.md with all claims marked:
- ✅ VERIFIED — Source link included
- ⚠️ UNVERIFIED — Awaiting evidence
- ❌ FALSE — Removed or corrected

**Effort:** 1 hour
**Impact:** HIGH — Stops misinformation spread

---

### WS-10: Causal Graph Engine (P1 — Turns Data into Understanding)

**Nemotron Addition.** Tracking *what* happened is insufficient. Need to track *why*.

**Problem:** Today you manually correlated "config refactoring on Aug 9" → "chunkTimeout removed" → "errors stayed at 0%". This should be automated.

**Solution:** Statistical correlation between config changes and error rate changes.

**Proposed Location:** `src/omega/observability/causal_graph.py`

```python
# src/omega/observability/causal_graph.py
from datetime import timedelta
from enum import Enum

class CausalStrength(Enum):
    LIKELY_CAUSAL = "likely_causal"      # p < 0.05
    LIKELY_COINCIDENTAL = "likely_coincidental"  # p > 0.05
    INSUFFICIENT_DATA = "insufficient_data"

class CausalGraph:
    """Links config changes → error rate changes → root causes."""
    
    def correlate(self, change: ConfigChange, 
                  window: timedelta = timedelta(hours=24)) -> CausalLink:
        """Query error rates before/after change.
        Perform statistical significance test.
        Return causal strength.
        """
        ...
    
    def find_root_cause(self, symptom: str) -> list[CausalPath]:
        """Given a symptom (e.g., 'streaming timeout'), 
        trace back through config changes to find likely causes.
        """
        ...
```

**Example Output:**
```
Symptom: "Streaming response failed" errors dropped to 0%

Causal Analysis:
1. OpenCode v1.18.14 deployment (Aug 5) → LIKELY_CAUSAL (p<0.001)
   - Changelog: "Retried more transient provider errors"
   - Error rate: 6.0% → 0.9% → 0%

2. chunkTimeout removal (Aug 9) → LIKELY_COINCIDENTAL (p=0.73)
   - No measurable effect on error rate
   - Conclusion: native retry made chunkTimeout unnecessary
```

**Effort:** 3 hours (skeleton + statistical tests + integration with WS-9)
**Impact:** HIGH — Automates root cause analysis

---

### WS-11: Provider Health Fingerprinting (P1 — Nemotron-Specific Intelligence)

**Nemotron Addition.** Treating all providers as black boxes misses actionable intelligence.

**Problem:** WS-3 "Error Rate Monitoring" treats all errors equally. But each provider has distinct failure signatures requiring different mitigations.

**Solution:** Provider-specific failure signatures and health checks.

**Proposed Location:** `config/provider_fingerprints.yaml`

```yaml
# config/provider_fingerprints.yaml
opencode-zen:
  nemotron-3-ultra:
    failure_signatures:
      - pattern: "Streaming response failed"
        cause: "SSE keepalive gap >30s (NVIDIA NIM design)"
        mitigation: "chunkTimeout >= 60000 OR native retry (v1.18.14+)"
        status: "RESOLVED (v1.18.14)"
      - pattern: "ResourceExhausted: Worker local total request limit"
        cause: "NVIDIA rate limit (32 concurrent)"
        mitigation: "request queuing / backoff"
        status: "MONITOR"
      - pattern: "The request queue is full"
        cause: "NVIDIA queue saturation"
        mitigation: "exponential backoff"
        status: "MONITOR"
    health_checks:
      - type: "synthetic_prompt"
        prompt: "Hello"
        interval: 300s
        timeout: 10s
        expected_pattern: "response_received"
```

**Integration with WS-3:** When error rate monitoring detects a spike, the fingerprinting engine classifies the error and suggests the specific mitigation.

**Effort:** 2 hours (schema + Nemotron fingerprints + integration)
**Impact:** HIGH — Turns generic errors into actionable intelligence

---

### WS-3: Error Rate Monitoring (Real-Time) — Enhanced

**Problem:** Daily batch monitoring = 24h detection latency. Streaming failures need minute-level detection.

**Solution:** Dual-layer monitoring — real-time event handler + daily aggregation.

**Implementation:**

**3a. Real-Time Event Handler** (via WS-9 Telemetry Bus):
```python
# In TelemetryBus.emit():
if event.event_type == TelemetryType.ERROR_RATE:
    if event.data["error_rate"] > 0.05:  # 5% threshold
        await self._send_immediate_alert(event)
```

**3b. Daily Aggregation** (cron at 06:00 UTC):
```sql
SELECT 
    date(m.time_created/1000, 'unixepoch') as date,
    json_extract(m.data, '$.modelID') as model_id,
    json_extract(m.data, '$.providerID') as provider_id,
    COUNT(*) as total_messages,
    SUM(CASE WHEN json_extract(m.data, '$.error') IS NOT NULL 
              AND json_extract(m.data, '$.error') != '' THEN 1 ELSE 0 END) as errors,
    GROUP_CONCAT(DISTINCT json_extract(m.data, '$.error')) as error_types
FROM message m
WHERE json_extract(m.data, '$.role') = 'assistant'
  AND m.time_created > strftime('%s', '2026-07-01') * 1000
GROUP BY date, model_id, provider_id
ORDER BY date DESC;
```

**3c. Alert on Spike:**
- If error rate for any provider/model exceeds 5% (configurable)
- Post alert to Hivemind
- Include: provider, model, error rate, comparison to 7-day average
- Include: matched fingerprint from WS-11 (if any)

**Effort:** 2 hours (3a + 3b + 3c)
**Impact:** HIGH — Minute-level detection + provider-specific diagnosis

---

### WS-2: OpenCode Update Detection (Enhanced)

**Problem:** Version check only detects *installed* version. Misses *available* updates and changelog details.

**Solution:** Three-layer detection.

**Implementation:**

**2a. Version Check Script** (`scripts/check_opencode_version.sh`):
```bash
#!/bin/bash
CURRENT=$(opencode --version 2>/dev/null)
LAST_KNOWN_FILE="data/coordination/LAST_KNOWN_OPENCODE_VERSION"
LAST_KNOWN=$(cat "$LAST_KNOWN_FILE" 2>/dev/null || echo "unknown")

if [ "$CURRENT" != "$LAST_KNOWN" ]; then
    echo "⚠️ OpenCode version changed: $LAST_KNOWN → $CURRENT"
    echo "   Changelog: https://opencode.ai/changelog"
    echo "$CURRENT" > "$LAST_KNOWN_FILE"
    # Emit telemetry event
    python -c "from src.omega.observability.telemetry_bus import TelemetryBus; ..."
fi
```

**2b. Hydration Sequence Update:**
Add to `AGENTS.md` Hydration Sequence (Phase 1 — AWARENESS):
```bash
# Check for OpenCode updates
bash scripts/check_opencode_version.sh
```

**2c. Changelog Monitor** (future enhancement):
- Daily cron job that fetches https://opencode.ai/changelog
- Compares to last known version
- Extracts streaming/retry/timeout-related changes
- Posts alert to Hivemind if relevant changes detected

**Effort:** 30 minutes (2a + 2b), 2 hours (2c)
**Impact:** HIGH — Immediate awareness of changes

---

### WS-4: Config Drift Detection (Versioned)

**Problem:** "Expected state" is static. Config evolves. Static expected state produces false positives.

**Solution:** Versioned expected state derived from CCL (last verified config).

**Implementation:**

**4a. Config Snapshot Script** (`scripts/snapshot_config.sh`):
```bash
#!/bin/bash
# Take daily snapshot of all config files
# Store in data/coordination/config_snapshots/YYYY-MM-DD/
```

**4b. Expected State Manifest** (auto-generated from CCL):
```markdown
# Expected Config State
# AUTO-GENERATED from CONFIG_CHANGE_LOG.md (last verified entry)
# Last updated: 2026-08-10

## opencode.json (project)
- provider.opencode.options.chunkTimeout = NOT SET (removed 2026-08-09)
- provider.opencode.options.timeout = NOT SET

## config/providers.yaml
- opencode-zen.streaming.chunk_timeout_ms = 30000
- opencode-zen.streaming.total_timeout_ms = 300000
- opencode-zen.streaming.fallback_on_timeout = true
```

**4c. Drift Detection Script** (`scripts/detect_config_drift.sh`):
```bash
#!/bin/bash
# Compare current config to expected state
# Alert if documented settings are missing or changed
# Run daily via cron
```

**Effort:** 2 hours (4a + 4b + 4c)
**Impact:** MEDIUM — Prevents silent config drift

---

### WS-5: Known Unknowns Register

**Problem:** We don't systematically track what we don't know. Questions get forgotten until they become emergencies.

**Solution:** Maintain a register of open questions and investigation status.

**Proposed Location:** `data/coordination/KNOWN_UNKNOWNS.md`

**Schema:**
```markdown
| ID | Question | Status | Priority | Last Investigated | Findings |
|----|----------|--------|----------|-------------------|----------|
| U-001 | What fixed the streaming timeout? | ✅ SOLVED | P0 | 2026-08-10 | OpenCode v1.18.14 native retry fixes |
| U-002 | Does chunkTimeout: 60000 still help? | ❓ OPEN | P1 | — | Pending split test |
| U-003 | Is better-opencode-retries loaded? | ✅ SOLVED | P0 | 2026-08-10 | No, never loaded |
| U-004 | Did NVIDIA change SSE keepalive? | ✅ SOLVED | P1 | 2026-08-10 | No evidence found |
| U-005 | Why did error pattern change post-Jul 30? | ❓ OPEN | P2 | — | Possible OpenCode error classification change |
```

**Maintenance Rules:**
- New unknowns discovered during investigations are added immediately
- Weekly review to update status
- SOLVED entries include source link to evidence
- Entries older than 30 days without investigation are flagged

**Effort:** 30 minutes (initial setup)
**Impact:** MEDIUM — Prevents forgotten questions

---

### WS-7: Split Test Design for chunkTimeout (Factorial)

**Nemotron Enhancement.** Original design ignored interaction effects.

**Problem:** chunkTimeout + native retry may have non-linear interaction. 2×2 factorial design required.

**Test Design:**

| Phase | Duration | Group A | Group B | Group C | Group D |
|-------|----------|---------|---------|---------|---------|
| 1 | 1 week | chunkTimeout:30000 + OC v1.18.14+ | chunkTimeout:60000 + OC v1.18.14+ | chunkTimeout:30000 + OC pinned <v1.18.14 | chunkTimeout:60000 + OC pinned <v1.18.14 |

**Note:** Groups C and D require pinning OpenCode to a version before v1.18.14. This may not be practical. If not, use 2-group design:

| Phase | Duration | Group A (Control) | Group B (Test) |
|-------|----------|-------------------|----------------|
| 1 | 1 week | No chunkTimeout (default 30s) | chunkTimeout: 60000 |
| 2 | 1 week | chunkTimeout: 60000 | No chunkTimeout (default 30s) |

**Metrics:**
- Primary: Error rate (Streaming response failed)
- Secondary: Average response latency, user-reported issues
- Tertiary: Session completion rate

**Decision Rule:**
- If Group B error rate < Group A by >1%: Restore chunkTimeout
- If Group B latency > Group A by >20%: Do not restore
- If no significant difference: Do not restore (simpler config)

**Effort:** 30 minutes (design), 2 weeks (execution)
**Impact:** MEDIUM — Evidence-based config decision

---

### WS-8: Evidence-Based Documentation Standards

**Problem:** Documentation makes claims without evidence. Future investigators waste time verifying or trusting false claims.

**Solution:** Establish documentation standards requiring evidence for all claims.

**Proposed Location:** `docs/standards/DOC_EVIDENCE_STANDARDS.md`

**Standards:**

1. **Every claim must have a source:**
   - ✅ "OpenCode v1.18.14 fixed streaming [source: https://opencode.ai/changelog]"
   - ❌ "OpenCode v1.18.14 fixed streaming" (no source)

2. **Unverified claims must be marked:**
   - ⚠️ UNVERIFIED — Claim awaiting evidence
   - ❓ UNKNOWN — Question without answer
   - ✅ VERIFIED — Claim with evidence

3. **Config changes must document expected effect:**
   - ✅ "chunkTimeout: 60000 — Expected: reduce SSE keepalive timeouts"
   - ❌ "chunkTimeout: 60000" (no expected effect)

4. **Investigation findings must be logged:**
   - Add to Known Unknowns Register
   - Update Config Change Log
   - Link to evidence document

**Effort:** 30 minutes (write standards), ongoing (enforcement)
**Impact:** HIGH — Prevents future investigation waste

---

## 📊 Implementation Priority (Revised)

| Priority | Workstream | Effort | Impact | Dependencies |
|----------|-----------|--------|--------|--------------|
| **P0** | **WS-9: Unified Telemetry Bus** | 2h | HIGH | None |
| **P0** | **WS-1: Config Change Log (auto-captured)** | 1h | HIGH | None |
| **P0** | **WS-6: AGENTS.md Claims Audit** | 1h | HIGH | None |
| **P1** | **WS-10: Causal Graph Engine** | 3h | HIGH | WS-9 |
| **P1** | **WS-11: Provider Fingerprinting** | 2h | HIGH | None |
| **P1** | **WS-3: Error Rate Monitoring (real-time)** | 2h | HIGH | WS-9, WS-11 |
| **P2** | **WS-2: OpenCode Update Detection** | 30m | HIGH | None |
| **P2** | **WS-4: Config Drift Detection** | 2h | MEDIUM | WS-1 |
| **P3** | **WS-7: Split Test (factorial)** | 30m | MEDIUM | None |
| **P3** | **WS-5: Known Unknowns Register** | 30m | MEDIUM | None |
| **P3** | **WS-8: Documentation Standards** | 30m | HIGH | WS-6 |

**Total Estimated Effort:** ~13 hours (excluding split test execution)

---

## 📁 Proposed File Structure

```
src/omega/observability/
├── telemetry_bus.py              # WS-9: Unified telemetry bus
├── causal_graph.py               # WS-10: Causal correlation engine
└── provider_fingerprinting.py    # WS-11: Provider-specific intelligence

data/coordination/
├── CONFIG_CHANGE_LOG.md          # WS-1: Central config change log
├── KNOWN_UNKNOWNS.md             # WS-5: Open questions register
├── EXPECTED_CONFIG_STATE.md      # WS-4b: Expected config state (auto-generated)
├── config_snapshots/             # WS-4a: Daily config snapshots
│   └── 2026-08-10/
│       ├── opencode.json.global
│       ├── opencode.json.project
│       ├── opencode.json.subdirectory
│       └── providers.yaml
└── LAST_KNOWN_OPENCODE_VERSION   # WS-2a: Last known version

config/
└── provider_fingerprints.yaml    # WS-11: Provider failure signatures

scripts/
├── check_opencode_version.sh     # WS-2a: Version check
├── collect_error_rates.sh        # WS-3b: Daily error aggregation
├── snapshot_config.sh            # WS-4a: Config snapshot
├── detect_config_drift.sh        # WS-4c: Drift detection
└── auto_ccl_entry.py             # WS-1: Auto-generate CCL entries

docs/standards/
└── DOC_EVIDENCE_STANDARDS.md     # WS-8: Documentation standards
```

---

## 🔬 Required Research & Discovery

### Local Discovery (Before Implementation)

| ID | What to Investigate | Why | Method |
|----|---------------------|-----|--------|
| **L-001** | MetricsDB schema for telemetry bus | Need to know existing tables/fields before adding `error_rates`, `config_changes`, `telemetry_events` | `sqlite3 data/observability/metrics.db ".schema"` |
| **L-002** | Existing error classification in opencode.db | What error types exist? What's the taxonomy? | Query `SELECT DISTINCT json_extract(data, '$.error') FROM message` |
| **L-003** | OpenCode plugin event delivery guarantees | Does OpenCode guarantee event ordering? Duplicates? | Read OpenCode plugin docs + source |
| **L-004** | Git hooks currently in use | What pre-commit hooks exist? Where? | `ls .git/hooks/` + check pre-commit framework |
| **L-005** | Provider fabric streaming implementation | How does `remote_provider.py` handle streaming? Where are timeouts? | Read `src/omega/oracle/backends/remote_provider.py` |
| **L-006** | Existing alerting/monitoring infrastructure | Is there already a MetricsDB alerting mechanism? | Check `src/omega/observability/` |
| **L-007** | OpenCode config schema for provider options | What fields are valid under `provider.opencode.options`? | Read https://opencode.ai/docs/config |
| **L-008** | opencode.db size and performance | 16GB DB — can we query it efficiently for real-time monitoring? | `ls -lh ~/.local/share/opencode/opencode.db` + query timing |

### Web Research (Before Implementation)

| ID | What to Research | Why | Method |
|----|------------------|-----|--------|
| **W-001** | OpenCode plugin system event guarantees | Need to know if event-based telemetry is reliable | Search: "opencode plugin event delivery guarantees" |
| **W-002** | NVIDIA NIM SSE keepalive behavior | Confirm the 30s gap is by design | Search: "NVIDIA NIM SSE keepalive ping behavior" |
| **W-003** | OpenCode v1.18.14+ retry implementation | Understand what "retry more transient errors" means exactly | Read OpenCode source: `packages/opencode/src/session/processor.ts` |
| **W-004** | OpenCode changelog API/programmatic access | Can we fetch changelogs automatically? | Check if https://opencode.ai/changelog has RSS/API |
| **W-005** | Statistical tests for causal inference | What test to use for before/after config change analysis? | Search: "causal inference interrupted time series python" |
| **W-006** | Provider fingerprinting best practices | How do other systems classify provider failures? | Search: "provider health fingerprinting observability" |
| **W-007** | OpenCode Zen API rate limits | What are the actual limits? How to detect queue full? | Search: "OpenCode Zen API rate limits nemotron" |
| **W-008** | Config drift detection tools | Are there existing tools for this? | Search: "config drift detection yaml json" |

### Expert Consultation Needed

| ID | Expert | Question |
|----|--------|----------|
| **E-001** | @john_carmack | Is the Telemetry Bus architecture overkill? Simpler alternative? |
| **E-002** | @researcher | Can you verify W-001 through W-008 findings? |
| **E-003** | @verity | Do the documentation standards comply with M26? |
| **E-004** | @kali | Priority approval — is WS-9 truly P0 or can we start with WS-1? |

---

## ✅ Approval Checklist

Before implementation, confirm:

- [ ] Priority order is correct (WS-9 as P0 prerequisite?)
- [ ] File locations are acceptable
- [ ] Schema designs are sufficient
- [ ] Effort estimates are reasonable
- [ ] No missing workstreams
- [ ] Dependencies are correctly identified
- [ ] Research/discovery plan is acceptable
- [ ] Factorial split test design is practical

---

## 🎯 Success Metrics

After implementation, we should be able to:

1. **Answer "what changed?" in <2 tool calls** — Config Change Log
2. **Detect OpenCode updates immediately** — Version check script
3. **Track error rates in real-time** — Telemetry Bus + event handler
4. **Diagnose errors by provider fingerprint** — WS-11 classification
5. **Correlate changes with effects automatically** — Causal Graph
6. **Detect config drift before it causes issues** — Drift detection
7. **Never forget an open question** — Known Unknowns Register
8. **Trust our documentation** — Evidence-based standards

---

## 🏁 Verdict

**Approve with modifications.** The plan is architecturally sound. WS-9 (Telemetry Bus) is the critical prerequisite — without it, the other workstreams produce isolated data.

The core insight: **You don't need more logs. You need a nervous system.**

---

*⬡ OMEGA ⬡ OBSERVABILITY ⬡ PLANNING ⬡ OTEP-v2.0.0 ⬡ 2026-08-10*

**Status:** DRAFT — Awaiting approval to implement
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: PLANNING | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

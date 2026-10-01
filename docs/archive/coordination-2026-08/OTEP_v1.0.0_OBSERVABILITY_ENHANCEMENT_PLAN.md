# 🔱 Observability & Tracking Enhancement Plan (OTEP v1.0.0)

**AP Token**: `AP-OTEP-v1.0.0`
⬡ OMEGA ⬡ OBSERVABILITY ⬡ PLANNING ⬡ 2026-0810

**Date**: 2026-08-10
**Author**: jem (Sovereign Synthesizer)
**Status**: DRAFT — Pending Approval
**Priority**: P0 (Critical Observability Gap)

---

## 🎯 Executive Summary

On 2026-08-10, we spent 1+ hour and 300K tokens investigating why Nemotron 3 Ultra streaming timeouts stopped on 2026-07-30. The answer was buried in scattered git history, outdated AGENTS.md documentation, and unverified claims.

**Root cause of the waste:** No systematic tracking of config changes, update effects, or error pattern correlations.

**This plan proposes 8 workstreams to ensure this never happens again.**

---

## 📋 Workstreams

### WS-1: Config Change Log (CCL)

**Problem:** Config changes are scattered across git history, backup files, and human memory. No single source of truth.

**Solution:** Maintain a centralized, searchable log of all configuration changes.

**Proposed Location:** `data/coordination/CONFIG_CHANGE_LOG.md`

**Schema:**
```markdown
| Date | What Changed | Where | Why | Effect | Verified By | Status |
|------|-------------|-------|-----|--------|-------------|--------|
| 2026-07-19 | Added streaming config | config/providers.yaml | Nemotron slow streams | Reduced timeouts | Commit 982fbba9 | ✅ VERIFIED |
| 2026-07-30 | Added chunkTimeout:60000 | opencode.json | SSE keepalive pings | Reduced "Streaming response failed" | AGENTS.md | ⚠️ UNVERIFIED |
| 2026-08-05 | OpenCode v1.18.14 installed | OpenCode binary | Native retry logic | Errors dropped to 0% | Changelog | ✅ VERIFIED |
| 2026-08-09 | Config refactoring | opencode.json | Cleanup | chunkTimeout REMOVED | Git diff | ✅ VERIFIED |
```

**Maintenance Rules:**
- Every config change MUST be logged BEFORE the change takes effect
- Each entry must include: what, where, why, expected effect, verification method
- Entries are marked ⚠️ UNVERIFIED until evidence confirms the effect
- Weekly review to update verification status

**Effort:** 1 hour (initial setup + backfill)
**Impact:** HIGH — Would have prevented today's investigation waste

---

### WS-2: OpenCode Update Detection

**Problem:** We only discover OpenCode updates by accident. No mechanism to alert us when a new version is installed or what changed.

**Solution:** Add version tracking to the session hydration sequence.

**Implementation:**

**2a. Version Check Script** (`scripts/check_opencode_version.sh`):
```bash
#!/bin/bash
# Check if OpenCode version changed since last session
CURRENT=$(opencode --version 2>/dev/null)
LAST_KNOWN_FILE="data/coordination/LAST_KNOWN_OPENCODE_VERSION"
LAST_KNOWN=$(cat "$LAST_KNOWN_FILE" 2>/dev/null || echo "unknown")

if [ "$CURRENT" != "$LAST_KNOWN" ]; then
    echo "⚠️ OpenCode version changed: $LAST_KNOWN → $CURRENT"
    echo "   Changelog: https://opencode.ai/changelog"
    echo "   Check for streaming/retry/timeout fixes"
    echo "$CURRENT" > "$LAST_KNOWN_FILE"
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
**Impact:** HIGH — Immediate awareness of changes that could affect system behavior

---

### WS-3: Error Rate Monitoring & Pattern Detection

**Problem:** We manually query opencode.db to understand error patterns. No automated tracking or alerting.

**Solution:** Implement daily error rate monitoring with automated pattern detection.

**Implementation:**

**3a. Daily Error Rate Collector** (`scripts/collect_error_rates.sh`):
```bash
#!/bin/bash
# Collect daily error rates by provider/model
# Stores in MetricsDB for trend analysis
# Runs via cron daily at 06:00 UTC
```

**Query:**
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

**3b. Error Rate Dashboard:**
- Store results in MetricsDB `error_rates` table
- Fields: date, model_id, provider_id, total_messages, errors, error_rate, error_types
- Grafana dashboard for visualization (future)

**3c. Alert on Spike:**
- If error rate for any provider/model exceeds 5% (configurable)
- Post alert to Hivemind
- Include: provider, model, error rate, comparison to 7-day average

**Effort:** 2 hours (3a + 3b), 1 hour (3c)
**Impact:** HIGH — Automated detection of regression or improvement

---

### WS-4: Config Drift Detection

**Problem:** Documented settings (like `chunkTimeout: 60000`) can be silently removed during refactoring. No mechanism to detect drift between documentation and actual config.

**Solution:** Daily config snapshot + diff against expected state.

**Implementation:**

**4a. Config Snapshot Script** (`scripts/snapshot_config.sh`):
```bash
#!/bin/bash
# Take daily snapshot of all config files
# Store in data/coordination/config_snapshots/YYYY-MM-DD/
# Files: opencode.json (all 3 locations), providers.yaml, AGENTS.md
```

**4b. Expected State Manifest** (`data/coordination/EXPECTED_CONFIG_STATE.md`):
```markdown
# Expected Config State

## opencode.json (project)
- provider.opencode.options.chunkTimeout = 60000
- provider.opencode.options.timeout = 600000

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

**Problem:** We don't systematically track what we don't know. Questions like "what fixed the streaming timeout?" get forgotten until they become emergencies.

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

### WS-6: AGENTS.md Claims Verification

**Problem:** AGENTS.md contains unverified claims (e.g., "better-opencode-retries plugin fixed streaming timeout"). These claims waste time when trusted as fact.

**Solution:** Audit AGENTS.md for claims, verify or correct each one.

**Implementation:**

**6a. Claims Audit:**
Identify all claims in AGENTS.md that describe:
- What a plugin/setting does
- What fixed an issue
- What the current state is

**6b. Verification Table:**

| Claim in AGENTS.md | Verified? | Evidence | Correction Needed |
|-------------------|-----------|----------|-------------------|
| "better-opencode-retries plugin fixed streaming timeout" | ❌ FALSE | grep shows plugin never loaded | Remove or correct |
| "chunkTimeout: 60000 avoids streaming timeout" | ⚠️ UNVERIFIED | Setting removed, needs testing | Mark as unverified |
| "OpenCode v1.18.16 has streaming fix" | ✅ PARTIAL | v1.18.14 had the fix, v1.18.16 is later | Clarify version |

**6c. Correction Pass:**
- Remove or correct all FALSE claims
- Mark all UNVERIFIED claims with ⚠️ symbol
- Add source links to all VERIFIED claims

**Effort:** 1 hour
**Impact:** HIGH — Prevents future investigation waste

---

### WS-7: Split Test Design for chunkTimeout

**Problem:** We don't know if `chunkTimeout: 60000` still provides value given OpenCode v1.18.14+ native retry fixes.

**Solution:** Design and run a controlled split test.

**Test Design:**

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

**Proposed Standards:**

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

## 📊 Implementation Priority

| Priority | Workstream | Effort | Impact | Dependencies |
|----------|-----------|--------|--------|--------------|
| **P0** | WS-1: Config Change Log | 1h | HIGH | None |
| **P0** | WS-2a+b: OpenCode Version Check | 30min | HIGH | None |
| **P0** | WS-6: AGENTS.md Claims Verification | 1h | HIGH | None |
| **P1** | WS-3: Error Rate Monitoring | 2h | HIGH | None |
| **P1** | WS-5: Known Unknowns Register | 30min | MEDIUM | None |
| **P1** | WS-8: Documentation Standards | 30min | HIGH | WS-6 |
| **P2** | WS-4: Config Drift Detection | 2h | MEDIUM | WS-1 |
| **P2** | WS-7: Split Test Design | 30min | MEDIUM | None |
| **P3** | WS-2c: Changelog Monitor | 2h | LOW | WS-2a+b |
| **P3** | WS-7: Split Test Execution | 2 weeks | MEDIUM | WS-7 design |

**Total Estimated Effort:** ~8 hours (excluding split test execution)

---

## 📁 Proposed File Structure

```
data/coordination/
├── CONFIG_CHANGE_LOG.md          # WS-1: Central config change log
├── KNOWN_UNKNOWNS.md             # WS-5: Open questions register
├── EXPECTED_CONFIG_STATE.md      # WS-4b: Expected config state
├── config_snapshots/             # WS-4a: Daily config snapshots
│   └── 2026-08-10/
│       ├── opencode.json.global
│       ├── opencode.json.project
│       ├── opencode.json.subdirectory
│       └── providers.yaml
└── LAST_KNOWN_OPENCODE_VERSION   # WS-2a: Last known version

scripts/
├── check_opencode_version.sh     # WS-2a: Version check
├── collect_error_rates.sh        # WS-3a: Error rate collector
├── snapshot_config.sh            # WS-4a: Config snapshot
└── detect_config_drift.sh        # WS-4c: Drift detection

docs/standards/
└── DOC_EVIDENCE_STANDARDS.md     # WS-8: Documentation standards
```

---

## ✅ Approval Checklist

Before implementation, confirm:

- [ ] Priority order is correct
- [ ] File locations are acceptable
- [ ] Schema designs are sufficient
- [ ] Effort estimates are reasonable
- [ ] No missing workstreams
- [ ] Dependencies are correctly identified

---

## 🎯 Success Metrics

After implementation, we should be able to:

1. **Answer "what changed?" in <2 tool calls** — Config Change Log
2. **Detect OpenCode updates immediately** — Version check script
3. **Track error rates automatically** — Daily monitoring
4. **Detect config drift before it causes issues** — Drift detection
5. **Never forget an open question** — Known Unknowns Register
6. **Trust our documentation** — Evidence-based standards

---

*⬡ OMEGA ⬡ OBSERVABILITY ⬡ PLANNING ⬡ OTEP-v1.0.0 ⬡ 2026-08-10*

**Status:** DRAFT — Awaiting approval to implement
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: PLANNING | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

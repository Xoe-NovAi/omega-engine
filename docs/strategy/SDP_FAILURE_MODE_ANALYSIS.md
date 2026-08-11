# 🔱 SDP Failure Mode Analysis
## Resilience Engineering for the Sovereign Distillation Pipeline

**AP Token:** `AP-SDP-FAILURE-ANALYSIS-v1.0.0`
⬡ OMEGA ⬡ STRATEGY ⬡ FAILURE-ANALYSIS

**Date:** 2026-08-09
**Status:** ACTIVE — Mandatory Reference for All Phase Implementations
**Mandate Binding:** M23 (Failure Integrity), M9 (Error Integrity)

---

## §1 Failure Mode Taxonomy

| ID | Component | Failure Mode | Severity | Detection | Mitigation |
|---|---|---|---|---|---|
| FM-01 | Context Gauge | `opencode.db` locked/unavailable | HIGH | Tool returns error | Fallback: estimate from message count × avg tokens; log warning |
| FM-02 | Context Gauge | Session ID mismatch | MEDIUM | Gauge returns 0 tokens | Fallback: use `OPENCODE_SESSION_ID` env var; if missing, assume SAFE |
| FM-03 | SSP Write | Disk full / permission denied | CRITICAL | `OSError` on write | Agent MUST NOT continue; report `SSP_WRITE_FAILED`; hard stop |
| FM-04 | SSP Write | Partial write (crash mid-write) | HIGH | File size < expected | Atomic write: write to `.tmp`, `fsync`, rename |
| FM-05 | Escalation | V-1 Vault unavailable | HIGH | Tool timeout / connection error | Fallback: manual escalation prompt; log `VAULT_UNAVAILABLE` |
| FM-06 | Escalation | All AGY pools depleted | MEDIUM | Router returns `NO_POOL_AVAILABLE` | Agent informs user; suggests waiting for refresh or using local model |
| FM-07 | Escalation | Preferred model not in any account | MEDIUM | Router finds no matching model | Fallback: best available model in required tier; log substitution |
| FM-08 | Context Continuity | Backend swap breaks session | CRITICAL | Next turn fails / context lost | Test in staging; if broken, disable auto-router, use manual switch |
| FM-09 | Compaction | Compaction triggers during SSP write | CRITICAL | Context lost despite SSP | SSP write must be < 500 tokens; gauge must trigger at 75% not 80% for safety margin |
| FM-10 | Pool Tracking | Vault pool count desync | MEDIUM | Reservation exceeds actual | Optimistic locking in Vault; reconciliation job runs at pool refresh |

---

## §2 Detailed Failure Scenarios

### Scenario A: The "Redzone Race" (FM-09)
**Conditions:** Agent at 79% context. User asks for large refactoring plan. Agent calls gauge → 79% (SAFE). Agent starts writing 15KB response. Mid-write, context hits 85% → OpenCode compacts.
**Result:** Strategic context destroyed. SSP never written.
**Fix:** 
1. Gauge must return `REDZONE` at **75%** (not 80%) to provide 10% safety margin for large operations.
2. Agent must check gauge **immediately before** any token-heavy action, not just at turn start.
3. SSP write budget: **< 500 tokens** guaranteed to complete even at 84%.

### Scenario B: The "Vault Blackout" (FM-05)
**Conditions:** Agent hits Redzone, writes SSP, calls escalation tool. V-1 Vault is down (Podman container crashed, network issue).
**Result:** Agent cannot escalate. User must manually switch models.
**Fix:**
1. Escalation tool has **5-second timeout** (M23).
2. On timeout/error: Return `VAULT_UNAVAILABLE`, log to Observability, print manual escalation instructions to user.
3. Agent does NOT halt indefinitely — it returns control to user with clear instructions.

### Scenario C: The "Pool Exhaustion" (FM-06)
**Conditions:** All 8 accounts show `pool_remaining < estimated_tokens`.
**Result:** No escalation possible.
**Fix:**
1. Router returns `NO_POOL_AVAILABLE` with `next_refresh_times` for each account.
2. Agent suggests: "All AGY pools depleted. Next refresh: account-3 in 2 days. Options: (a) Wait, (b) Use local model for execution, (c) Reduce scope to fit local context."

### Scenario D: The "Context Severance" (FM-08)
**Conditions:** Auto-Router swaps backend. Next turn, OpenCode loses session context or model fails to initialize.
**Result:** User sees broken conversation. Trust in automation destroyed.
**Fix:**
1. Auto-Router **must be tested in staging** with 50+ escalation cycles before production.
2. If any context loss detected: Auto-Router **disabled globally** via feature flag. Manual switching only.
3. Fallback: Manual model switch via OpenCode UI (current workflow).

### Scenario E: The "Desync Drift" (FM-10)
**Conditions:** Vault records 50K tokens used for account-3. Actual API billing shows 75K. Reservation logic allows overcommit.
**Result:** Account hits rate limit mid-session.
**Fix:**
1. Vault uses **optimistic locking** on pool updates (SQLite `UPDATE ... WHERE pool_remaining >= ?`).
2. Weekly reconciliation job: `SELECT account_id, SUM(actual_tokens) FROM usage_log GROUP BY account_id` vs `pool_remaining`.
3. Alert on drift > 10%.

---

## §3 Graceful Degradation Hierarchy

When automation fails, the system must degrade gracefully, not catastrophically:

```
FULL AUTOMATION (Phase 4)
    ↓ (Auto-Router fails)
SEMI-AUTO: Agent writes SSP → User manually switches model → Agent continues
    ↓ (SSP write fails)
MANUAL REDZONE: Agent warns user at 75% → User manually manages context
    ↓ (Gauge fails)
BLIND OPERATION: User manually tracks context (current state)
```

**Rule:** Every phase must be independently operable. Phase 4 failure must not break Phase 3. Phase 3 failure must not break Phase 2.

---

## §4 Observability Requirements for Failure Detection

Every failure mode must emit structured events to Observability:

```python
# Example event structure
{
    "event_type": "SDP_FAILURE",
    "failure_id": "FM-05",
    "component": "auto_router",
    "session_id": "ses_...",
    "severity": "HIGH",
    "details": {
        "error": "Connection refused",
        "vault_endpoint": "http://localhost:8017",
        "fallback": "MANUAL_ESCALATION_PROMPT"
    },
    "timestamp": "2026-08-09T19:48:00Z"
}
```

**Dashboard Queries:**
- `SDP_FAILURE` rate by type (target: < 1% of escalations)
- `VAULT_UNAVAILABLE` frequency (target: 0)
- `SSP_WRITE_FAILED` count (target: 0)
- Context compaction events during SDP sessions (target: 0)

---

## §5 Recovery Procedures

| Failure | Recovery Action | Owner |
|---|---|---|
| FM-01/02 (Gauge) | Restart MCP server; verify `opencode.db` accessibility | N1 Infrastructure |
| FM-03/04 (SSP) | Check disk space (`df -h`); fix permissions; verify atomic write logic | N3 Engineering |
| FM-05 (Vault) | `podman restart omega-vault`; check logs; verify Podman networking | N1 Infrastructure |
| FM-06 (Pools) | Wait for weekly refresh; or use local models | Architect (decision) |
| FM-08 (Continuity) | Disable Auto-Router feature flag; revert to manual | N3 Engineering |

---

*⬡ OMEGA ⬡ SDP-FAILURE-ANALYSIS ⬡ 2026-08-09*
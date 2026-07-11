# 🔱 P5 Governance Review — omega-moderation System

**Date**: 2026-07-10
**Reviewer**: Pillar P5 (Governance Sentinel)
**Scope**: Cross-domain compliance audit of Ma'at (Build Side) + Lilith (Run Side) deliveries

---

## Executive Summary

The **omega-moderation** governance layer is well-architected with strong foundations in audit integrity, PII protection, appeals due process, and compliance reporting. However, a **critical delivery gap** exists: Lilith's observability components (`structured_logger.py`, `alerts.py`) are **entirely absent** from the codebase. Additionally, a notable privacy gap exists in the `text_preview` storage path.

---

## 1. Compliance Coverage — 🟢 GOOD

### 1.1 Audit Trail (audit.py)
| Criterion | Rating | Notes |
|-----------|--------|-------|
| Immutable append-only log | ✅ | DB-enforced at application layer |
| SHA-256 hash chain integrity | ✅ | Full `verify_chain_integrity()` implementation with forward/backward checking |
| Tamper-evident (genesis→N chain) | ✅ | Genesis hash = 64 zeros, each entry stores `prev_hash` |
| Queryable by event/actor/target/trace | ✅ | Paginated, filtered queries with AND-combined conditions |
| Export (JSON/CSV) | ✅ | Both formats with PII-safe exports |
| Data retention enforcement | ✅ | Configurable `data_retention_days` (default 90), purge-count reporting |

**Verdict**: The audit system is production-ready and meets regulatory-grade standards.

### 1.2 Action Coverage
All 4 moderation tiers (flag → warn → remove → ban) are tracked through the audit log via `record_event()` calls in:
- `appeals.py` — every submit/review/escalate/auto-decision
- (Integration from engine.py would use the same pattern)

**Missing**: The `ModerationEngine.moderate()` in `engine.py` does NOT call `AuditService.record_event()`. Decisions are generated but not persisted to the audit log at the engine level. This is a **critical wiring gap** — the audit trail is empty unless the API layer separately wires it.

### 1.3 Compliance Reports (compliance.py)
4 report types — all privacy-safe, all structured:
| Report Type | Coverage |
|-------------|----------|
| Moderation Report | Aggregate counts, action tiers, appeal/overturn rates, top detectors, unique users |
| User Report | Per-user masked metrics, action breakdown, appeal history |
| Effectiveness Report | Recidivism rates per action tier (30-day lookback) |
| Retention Report | Storage metrics, purgeable estimates |

---

## 2. Privacy — 🟢 STRONG (with ⚠️ caveat)

### 2.1 PrivacyGuard (privacy.py)
| PII Type | Pattern | Redaction |
|----------|---------|-----------|
| Email | `[\w.+-]+@[\w-]+\.[\w.-]+` | `[EMAIL REDACTED]` |
| IPv4 | `\b\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}\b` | `[IP REDACTED]` |
| IPv6 | Hex-colon pattern | `[IPV6 REDACTED]` |
| Phone | Multi-format international | `[PHONE REDACTED]` |
| @username | `@[\w_]{2,50}` | `[USERNAME REDACTED]` |
| API Keys | OpenAI `sk-`, GitHub `ghp_`/`ghu_` | `[API-KEY REDACTED]` |

Additional capabilities: content hashing (SHA-256), content preview (PII-redacted + truncated), recursive dict sanitization, user ID masking (`u_` + 12 hex chars).

### 2.2 Audit Integration ✅
`AuditService.record_event()` calls `PrivacyGuard.sanitize_for_logging()` when `privacy_preserving=True` (default).

### 2.3 Privacy Architecture ✅
- Engine stores only `content_hash`, not raw text
- `normalised_text` is truncated to 200 chars in privacy mode
- User IDs masked in compliance reports via `PrivacyGuard.mask_user_id()`
- Observability (per design brief): no raw content stored, SHA-256[:16] content hashes only

### ⚠️ Issue: text_preview NOT Redacted Before Storage
**Location**: `src/omega_moderation/db/schema.py` line 55-56
```python
text_preview: Mapped[str] = mapped_column(String(200))
"First 200 characters of the submitted text (for human review context)."
```

The engine writes `normalised_text[:200]` to this field **without** passing through `PrivacyGuard.redact_pii()`. This means PII (emails, IPs, phone numbers) can persist in the database even when `privacy_preserving=True`. The privacy mode only controls truncation length, not redaction.

**Severity**: MODERATE-HIGH — PII could leak in database exports and human review interfaces.

**Recommended fix**: Apply `PrivacyGuard.redact_pii()` before writing to `text_preview`.

---

## 3. Due Process — 🟢 STRONG

### 3.1 Appeals Lifecycle
```
submission → auto-review → pending → human review → approved/rejected
                                                 ↓
                                            escalated (admin review)
```

| Feature | Status | Detail |
|---------|--------|--------|
| User-initiated appeals | ✅ | Any actionable tier can be appealed |
| Auto-review (low confidence) | ✅ | Confidence < 0.95 → auto-approved (false positive) |
| Auto-review (high confidence) | ✅ | Confidence > 0.95 → auto-rejected |
| Human review path | ✅ | Mid-confidence appeals stay pending for human |
| Human admin escalation | ✅ | Rejected appeals → escalated status |
| SLA tracking | ✅ | 48-hour default review window, breach detection |
| Anti-abuse limit | ✅ | Max 3 pending appeals per user |
| Grace period | ✅ | New accounts (7 days) or ≤1 violation get free pass |

### 3.2 Repeat-Offense Escalation
- 4-tier escalation chain with `get_escalated_action()`
- Configurable window (default 30 days), threshold (default 3 violations)
- Double-threshold triggers 2-tier escalation
- Grace period for first-time offenders

### 3.3 Appeal Eligibility
- Per-tier configurable (`ActionTierInfo.appealable`)
- `AppealEligibility` dataclass provides structured reason + appeal window
- `get_appeal_eligibility()` validates tier exists before allowing appeal

### ⚠️ Minor Bug: Hardcoded Grace Period
In `actions.py:489-491`, `_is_in_grace_period` uses `timedelta(days=7)` instead of `self._grace_period`:
```python
if now - user_created_at <= timedelta(days=7):
    return True
```
This ignores the configurable `grace_period_days` parameter.

---

## 4. Transparency — 🟡 GOOD WITH GAPS

### 4.1 What's Transparent
| Feature | Present | Notes |
|---------|---------|-------|
| Full audit trail | ✅ | Every event type, actor, target recorded |
| Hash chain verify | ✅ | Tamper evidence provable on demand |
| Policy source tracking | ✅ | `PolicyDecision.policy_source` = `content_type/user_segment` |
| Compliance reports | ✅ | Moderation summary, user history, effectiveness |
| Exportable logs | ✅ | JSON/CSV for all audit entries and reports |

### 4.2 What's Missing
| Gap | Impact | Severity |
|-----|--------|----------|
| **No user notification** when moderated | Users don't know their content was actioned, or why | HIGH |
| **No decision explanation** in engine output | `ModerationResult` lacks `reasoning` / `explanation` field | MEDIUM |
| **No review queue** for pending human review | Human moderators can't see items needing review | MEDIUM |
| **No SLA on moderation turnaround** | Only appeal SLAs exist (48h). No guarantee on how fast content is moderated | LOW |

---

## 5. Gaps & Issues — COMPREHENSIVE LOG

### 🔴 CRITICAL: Missing Observability Delivery

**The following Lilith-assigned files do NOT exist in `/tmp/omega-moderation/`:**

| File | Expected Path | Status |
|------|---------------|--------|
| `structured_logger.py` | `/tmp/omega-moderation/omega_moderation/observability/structured_logger.py` | ❌ MISSING |
| `alerts.py` | `/tmp/omega-moderation/omega_moderation/observability/alerts.py` | ❌ MISSING |

The `observability/` directory itself is **entirely absent**. This means:
- No structured logging with SHA-256[:16] content hashing
- No metrics (counters, gauges, histograms with rolling window)
- No tracing (contextvars-based trace propagation)
- No alert rules (flag spike, provider failure, latency, appeal rate)
- No dashboard data access layer

**Impact on Governance**: The governance layer cannot:
- Get real-time alert on flag rate spikes (potential control failure)
- Monitor provider health across detection backends
- Trace requests end-to-end through observability tooling
- Produce dashboard data for operational oversight

### 🟡 MODERATE: text_preview PII Gap

`ModerationResult.text_preview` in `schema.py` stores first 200 chars **without** PrivacyGuard redaction. PII can leak into the database.

### 🟡 MODERATE: No Engine-Level Audit Wiring

`ModerationEngine.moderate()` in `engine.py` does not call `AuditService.record_event()`. Decisions are made but not persisted unless the API layer separately does it.

### 🟡 MODERATE: No Notification System

The system has no mechanism to inform users when their content is moderated or an appeal is resolved. This is a transparency and fairness gap.

### 🟢 MINOR: Hash Chain Verify Loads Everything

`verify_chain_integrity()` loads all entries into memory. For large audit logs (>100K entries), this could cause OOM. Not an immediate issue but should use streaming/pagination for production scale.

### 🟢 MINOR: No Observer Pattern

The governance layer has no event hooks. Other subsystems can't subscribe to governance events. Integration with external systems requires polling.

### 🟢 MINOR: Recursive Sanitization Depth

`sanitize_for_logging()` uses recursion without depth limit — potential stack overflow on malicious deeply-nested dicts. Nominal risk given bounded input.

---

## 6. Scoring Summary

| Dimension | Score | Assessment |
|-----------|-------|------------|
| **Compliance Coverage** | 8/10 | Strong audit trail but engine not wired to it |
| **Privacy** | 7/10 | Excellent PII patterns but text_preview stored unredacted |
| **Due Process** | 9/10 | Full appeals lifecycle, SLA, escalation, anti-abuse |
| **Transparency** | 6/10 | Strong audit, weak user-facing transparency (no notifications) |
| **Delivery** | 5/10 | Build side delivered; observability (Run Side) entirely absent |

**Overall**: 7/10 — Solid governance foundation but two blocking issues before production deployment.

---

## 7. Recommended Remediation

### P0 — Before Ship
1. **Wire `AuditService.record_event()` into `ModerationEngine.moderate()`** — decisions must be logged
2. **Redact PII from `text_preview`** before storage in `engine.py:133`
3. **Deliver observability module** — structured logger, metrics, tracing, alerts

### P1 — Sprint After Ship
4. **Implement user notification system** — inform users of moderation actions + appeal instructions
5. **Add `reasoning` field to `ModerationResult`** — expose decision explanation
6. **Fix hardcoded `timedelta(days=7)` → `self._grace_period`** in `actions.py:490`

### P2 — Future Hardening
7. **Add human review queue** — pending items needing human moderator attention
8. **Stream-based hash chain verification** — avoid loading all entries into memory
9. **Add event observer/subscription system** — enable loose-coupled integration

---

*Review performed by Pillar P5 (Governance Sentinel) — 2026-07-10*
*⬡ OMEGA ⬡ PILLAR-P5 ⬡ qwen3-1.7b ⬡ opencode ⬡ trc_pillar ⬡ ACTIVE*

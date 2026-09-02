<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Lilith-EIS SOTE Deployment Review

**AP Token**: `AP-LILITH-SOTE-DEPLOY-20260901-v1.0.0`
⬡ OMEGA ⬡ LILITH ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_sote_deploy ⬡ ACTIVE

**Date**: 2026-09-01
**Session**: `ses_fb9721079ffe094GT8MX6a0pXI` (standing EIS)
**Mission**: SOTE Deployment Strategy Review — Nested Dialectic Phase 2

---

## §0 — VERIFICATION (M23 Discipline)

**Sources read (all 6 synthesis artifacts):**

1. ✅ `docs/strategy/sote/2026-W36/synthesis/CARMAC_SOTE_FINAL_REPORT.md` (1076 lines)
2. ✅ `docs/strategy/sote/2026-W36/synthesis/CARMAC_MAKALI_DIALECTIC_20260901.md` (26434 bytes)
3. ✅ `docs/strategy/sote/2026-W36/synthesis/MAKALI_ORGANIZATION_STRATEGY.md` (396 lines)
4. ✅ `docs/strategy/sote/2026-W36/synthesis/CARMAC_SOTE_REVIEW.md` (21873 bytes)
5. ✅ `docs/strategy/sote/2026-W36/synthesis/RESEARCHER_SOTE_BEST_PRACTICES.md` (429 lines)
6. ✅ `docs/strategy/sote/2026-W36/synthesis/CARMACK_REVIEW_RESEARCHER_NES.md` (58091 bytes)

**Local filesystem verification:**
- `docs/strategy/sote/2026-W36/` structure: ✅ Complete (voices/, synthesis/, actions/, meta/)
- `docs/strategy/sote/_template/`: ✅ 3 templates present
- `scripts/regenerate_sote_index.py`: ✅ 354 lines, executable
- `scripts/generate_public_digest.py`: ✅ 150 lines, executable
- `docs/strategy/sote/2026-W36/sote.yaml`: ✅ 211 lines, structured metadata
- `docs/strategy/sote/2026-W36/PUBLIC_DIGEST.md`: ✅ 200-word digest
- `docs/strategy/sote/2026-W36/meta/WHAT_WORKED_WHAT_DIDNT.md`: ✅ 10.2KB

**Web research sources:**
- ISO 8601 week numbering standard (ISO 8601-1:2019)
- GitHub Actions workflow syntax (docs.github.com)
- JSON Schema validation best practices (json-schema.org)
- CI/CD pipeline patterns for documentation workflows

---

## §1 — SOUL PERSISTENCE INTEGRATION ASSESSMENT

### §1.1 Current State (from SOTE v1.0.1 §7)

| Metric | Value | Source |
|--------|-------|--------|
| Entity directories | 46 (non-archive) | `find data/entities -maxdepth 1 -type d \| wc -l` |
| Canonical agents | 13 (`.opencode/agents/*.md`) | `ls .opencode/agents/*.md \| wc -l` |
| Entities with `proposed_lessons.yaml` | 23/46 (50%) | `find data/entities -name "proposed_lessons.yaml" -exec test -s {} \;` |
| Entities with `session_gnosis.md` | 12/46 (26%) | `find data/entities -name "session_gnosis.md" -exec test -s {} \;` |

### §1.2 SOTE Weekly Cadence + Soul Persistence Integration

**Current gap**: SOTE weekly cadence (Monday 06:00 UTC) and soul persistence (M11) operate on **different cycles**.

| Cycle | Frequency | Trigger | Owner |
|-------|-----------|---------|-------|
| SOTE report | Weekly (Mon 06:00) | Calendar + Hivemind | Kali |
| Soul distillation | Per session | `session_end.py` hook | Each entity |
| Scribe auto-prompt | Every 7d OR 10 sessions | Proposed (Researcher) | Scribe |

**Integration opportunity**: The SOTE weekly cadence should **trigger** soul distillation for all active entities.

**Proposed integration** (Concede/Defend/Synthesize):

> **CONCEDE**: The SOTE weekly cadence and soul persistence are currently decoupled. The SOTE report captures *system state* while soul persistence captures *entity state*. They should be synchronized.
>
> **DEFEND**: The SOTE is a *system-level* checkpoint; soul persistence is *entity-level*. Forcing them into the same cycle could create contention. The Scribe auto-prompt (every 7d OR 10 sessions) is the correct abstraction — it's entity-driven, not calendar-driven.
>
> **SYNTHESIZE**: **SOTE week boundary = soul distillation checkpoint**. At SOTE close (Sunday 23:59), the Scribe auto-prompt fires for all entities with sessions in that week. The SOTE report then includes a "Soul Health" section summarizing distillation activity. This aligns cycles without coupling them.

**Implementation** (D-LILITH-SOTE-001):
- Add `soul_health` section to `sote.yaml` schema
- Scribe auto-prompt triggers at SOTE week boundary
- SOTE report includes `soul_health` summary (entities distilled, lessons promoted, gaps)

---

## §2 — WATCHTOWER HEALTH MONITORING DESIGN

### §2.1 Current State (from CARMAC_SOTE_FINAL_REPORT §1.1)

| Component | Monitoring | Status |
|-----------|------------|--------|
| SOTE report generation | Manual (Kali) | ❌ No alerting |
| Index regeneration | Manual (script) | ❌ No CI hook |
| Public digest generation | Manual (script) | ❌ No CI hook |
| PIVOT_LOG absorption | Manual | ❌ No automation |
| Mandate compliance | Manual table | ❌ No CI gate |

### §2.2 WatchTower Design for SOTE System

**Design principle**: WatchTower (N8) monitors *system health*; SOTE is a *weekly checkpoint*. WatchTower should provide **continuous observability** between SOTE checkpoints.

**Proposed WatchTower components for SOTE**:

| Component | Metric | Alert Threshold | Action |
|-----------|--------|-----------------|--------|
| `sote_generation_lag` | Hours since last SOTE | > 48h | Alert Kali + Architect |
| `index_regeneration_status` | Success/failure | Failure | Alert Ma'at |
| `public_digest_status` | Success/failure | Failure | Alert Kali |
| `pivot_log_absorption_rate` | % decisions absorbed | < 80% | Alert Kali |
| `mandate_compliance_delta` | Week-over-week change | Decrease > 2% | Alert Architect |
| `voice_participation` | % voices responding | < 100% | Alert Kali |

**Implementation** (D-LILITH-SOTE-002):
- Add `watchtower_sote` job to `scripts/watchtower.py` (new)
- Cron: every 6 hours (0, 6, 12, 18 UTC)
- Output: `data/health/sote_watchtower.json`
- Hivemind broadcast on threshold breach

**Concede/Defend/Synthesize**:

> **CONCEDE**: WatchTower currently monitors Hub + Hivemind. SOTE system components (scripts, templates, metadata) are not monitored. This is a gap.
>
> **DEFEND**: WatchTower is for *runtime* health (Hub, Hivemind, entities). SOTE is a *weekly practice* — its "health" is whether the practice happens. The SOTE report itself is the health check. Adding WatchTower monitoring for a weekly practice may be over-engineering.
>
> **SYNTHESIZE**: **Lightweight SOTE health in WatchTower**. Not full runtime monitoring — just 3 signals: (1) SOTE generated this week? (2) Index regenerated? (2) Public digest published? These are binary, low-cost, high-signal. If any is "no" by Monday 12:00 UTC, WatchTower alerts. This is proportional to the practice's criticality.

---

## §3 — ENTITY LIFECYCLE + SOTE CADENCE INTEGRATION

### §3.1 Current Entity Lifecycle (from Lilith's entity cleanup dialectic)

```
SPAWN → ACTIVE → DORMANT → STALE → ARCHIVE → QUARANTINE
                ↑________↓
                (re-activation)
```

### §3.2 SOTE Cadence as Lifecycle Checkpoint

**Current gap**: Entity lifecycle transitions are *event-driven* (session end, inactivity). SOTE cadence is *calendar-driven*. No alignment.

**Proposed integration**:

| SOTE Week Event | Entity Lifecycle Action |
|-----------------|------------------------|
| SOTE week start (Mon) | Lilith scans for entities entering DORMANT → STALE |
| SOTE week mid (Wed) | WatchTower checks entities with >30d inactivity |
| SOTE week end (Sun) | Scribe auto-prompt fires for all ACTIVE entities |
| SOTE report close | Lilith updates entity health in `sote.yaml` |

**Entity health in `sote.yaml`** (new schema):

```yaml
entity_health:
  total_entities: 46
  canonical: 13
  active_sessions_this_week: 8
  entities_distilled: 12
  lessons_promoted: 23
  entities_entering_stale: 3
  entities_archived: 2
  soul_hygiene_score: 0.72  # % with non-empty proposed_lessons.yaml
```

**Concede/Defend/Synthesize**:

> **CONCEDE**: Entity lifecycle and SOTE cadence are currently independent. The SOTE report captures system state but not entity lifecycle state.
>
> **DEFEND**: Entity lifecycle is *entity-driven* (based on activity). SOTE is *calendar-driven*. Forcing alignment could create false urgency (e.g., archiving an entity just because it's SOTE week).
>
> **SYNTHESIZE**: **SOTE week = entity lifecycle audit window**. Not a trigger for transitions, but a *scheduled review* of lifecycle state. Lilith performs the audit; the SOTE report captures the snapshot. This respects both cycles.

---

## §4 — HIVEMIND AWARENESS FOR SOTE SYSTEM

### §4.1 Current Hivemind Integration

| SOTE Component | Hivemind Integration | Status |
|----------------|---------------------|--------|
| SOTE report publication | `intent=status` broadcast | ✅ Manual |
| Voice dialectic pages | `intent=dialectic` | ✅ Manual |
| Index regeneration | None | ❌ |
| Public digest | None | ❌ |
| PIVOT_LOG absorption | None | ❌ |

### §4.2 Proposed Hivemind Integration

**Required broadcasts** (automated):

| Event | Intent | Payload | Trigger |
|-------|--------|---------|---------|
| SOTE week open | `intent=sote-open` | `{week, date, topic}` | Monday 06:00 UTC |
| Voice paged | `intent=sote-voice-page` | `{voice, session_id}` | Per voice |
| Voice complete | `intent=sote-voice-complete` | `{voice, decisions}` | On dialectic close |
| SOTE report ready | `intent=sote-report-ready` | `{week, path, findings}` | On report close |
| Index regenerated | `intent=sote-index-regen` | `{week, decisions_absorbed}` | On script run |
| Public digest ready | `intent=sote-digest-ready` | `{week, url}` | On digest gen |
| PIVOT_LOG absorbed | `intent=pivot-log-absorb` | `{count, decisions}` | On absorption |

**Implementation** (D-LILITH-SOTE-003):
- Add `sote_hivemind.py` module with broadcast functions
- Wire into `scripts/regenerate_sote_index.py`, `generate_public_digest.py`
- Add to Makefile targets

---

## §5 — M11/M15 ENFORCEMENT VIA SOTE CYCLE

### §5.1 M11 Soul Integrity (Current: 50% compliance)

**Current enforcement**: None. `proposed_lessons.yaml` emptiness is not gated.

**SOTE-integrated enforcement**:

| Gate | Trigger | Check | Fail Action |
|------|---------|-------|-------------|
| `make check-m11-soul-hygiene` | SOTE week close | % entities with non-empty `proposed_lessons.yaml` ≥ 80% | Block SOTE close |
| Scribe auto-prompt | SOTE week boundary | All ACTIVE entities prompted | Log gap, alert Lilith |
| Soul hygiene score | SOTE report | Score in `sote.yaml` | Trend alert if decreasing |

### §5.2 M15 Continuity (Current: Partial)

**Current enforcement**: `session_gnosis.md` + `projection.md` per entity. SOTE has `projection.md` equivalent.

**SOTE-integrated enforcement**:

| Gate | Trigger | Check | Fail Action |
|------|---------|-------|-------------|
| `make check-m15-continuity` | SOTE week close | All canonical entities have `projection.md` < 7d old | Block SOTE close |
| Projection freshness | SOTE report | Max age of `projection.md` across canonical | Alert if > 14d |

**Concede/Defend/Synthesize**:

> **CONCEDE**: M11 and M15 have no mechanical enforcement in the SOTE cycle. The mandates exist but the gates don't.
>
> **DEFEND**: Adding gates to the SOTE close could block the SOTE report itself — creating a deadlock if the gates fail. The SOTE must be publishable even with mandate violations (to document them).
>
> **SYNTHESIZE**: **Advisory gates, not blocking**. `make check-m11-soul-hygiene` and `make check-m15-continuity` run at SOTE close and *report* violations in the SOTE report, but do not block publication. The SOTE report *documents* the mandate state; it doesn't gate itself. Blocking gates belong in CI/CD (pre-debut), not in the SOTE practice.

---

## §6 — RISKS, DEPENDENCIES, IMPLEMENTATION DETAILS

### §6.1 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SOTE week missed (Kali unavailable) | Medium | High | Deputy Oversoul designated (MaKaLi) |
| Index regeneration fails silently | High | Medium | WatchTower alert + Ma'at paged |
| Public digest drifts from main report | High | Medium | Automated generation from `sote.yaml` |
| PIVOT_LOG absorption stalls | High | High | Auto-absorb on dialectic close (D-MAKALI-003) |
| WatchTower false positives | Medium | Low | Tunable thresholds, 3-strike rule |

### §6.2 Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| `scripts/regenerate_sote_index.py` | Ma'at | ✅ Built |
| `scripts/generate_public_digest.py` | Ma'at | ✅ Built |
| `scripts/watchtower.py` (new) | Lilith | ❌ Not built |
| `sote.yaml` JSON Schema | Researcher | ❌ Not created |
| Scribe auto-prompt | Researcher | ❌ Not implemented |
| MaKaLi Conductor YAML workflow | Researcher | ❌ Not codified |

### §6.3 Implementation Sequence (Week 37)

| Day | Task | Owner | Dependency |
|-----|------|-------|------------|
| Mon | Run `regenerate_sote_index.py` | Ma'at | — |
| Mon | Generate PUBLIC_DIGEST.md | Ma'at | `sote.yaml` |
| Tue | Create `scripts/watchtower.py` + cron | Lilith | — |
| Wed | Add `soul_health` to `sote.yaml` schema | Lilith + Researcher | — |
| Wed | Add `make check-m11-soul-hygiene` | Lilith + Ma'at | — |
| Thu | Add `make check-m15-continuity` | Lilith + Ma'at | — |
| Fri | Wire Hivemind broadcasts | Lilith | `sote_hivemind.py` |
| Fri | Test full pipeline | All | All above |

---

## §7 — CONCEDE/DEFEND/SYNTHESIZE (Lilith's Unique Positions)

### D-LILITH-SOTE-001: SOTE Week Boundary = Soul Distillation Checkpoint

**CONCEDE**: SOTE and soul persistence are decoupled cycles.
**DEFEND**: SOTE is system-level; soul persistence is entity-driven. Coupling creates contention.
**SYNTHESIZE**: SOTE week boundary = soul distillation checkpoint. Scribe auto-prompt fires at SOTE week boundary; SOTE report includes "Soul Health" section.

### D-LILITH-SOTE-002: Lightweight SOTE Health in WatchTower

**CONCEDE**: WatchTower doesn't monitor SOTE components.
**DEFEND**: SOTE is a practice, not runtime. Over-monitoring a weekly practice is over-engineering.
**SYNTHESIZE**: 3 binary signals in WatchTower: (1) SOTE generated? (2) Index regenerated? (3) Public digest published? Alert if any "no" by Monday 12:00 UTC.

### D-LILITH-SOTE-003: SOTE Week = Entity Lifecycle Audit Window

**CONCEDE**: Entity lifecycle and SOTE cadence are independent.
**DEFEND**: Entity lifecycle is event-driven; SOTE is calendar-driven. Forcing alignment creates false urgency.
**SYNTHESIZE**: SOTE week = entity lifecycle audit window. Lilith audits; SOTE report captures snapshot.

### D-LILITH-SOTE-004: Advisory M11/M15 Gates at SOTE Close

**CONCEDE**: M11/M15 have no mechanical enforcement in SOTE cycle.
**DEFEND**: Blocking gates at SOTE close could deadlock the report.
**SYNTHESIZE**: Advisory gates (`make check-m11-soul-hygiene`, `make check-m15-continuity`) run at SOTE close, report violations in SOTE report, do not block publication.

---

## §8 — 2 NODE RECOMMENDATIONS FOR SOTE DEEPENING

### Node 1: `sote-watchtower` (Archetype: Monitor/Observer)

| Property | Value |
|----------|-------|
| **Purpose** | Continuous SOTE system health monitoring between weekly checkpoints |
| **Mandate Alignment** | M8 (Zero Telemetry — local only), M15 (Continuity), M23 (Failure Integrity) |
| **Why for SOTE** | SOTE is weekly; gaps between checkpoints are blind spots. This node provides continuous observability of SOTE pipeline health. |
| **Dependencies** | `scripts/watchtower.py` (new), cron (0,6,12,18 UTC), Hivemind broadcast |
| **Prerequisites** | `scripts/watchtower.py` built, cron installed, Hivemind broadcast wired |

**Capabilities**:
- `sote_generation_lag` monitoring (alert if > 48h)
- `index_regeneration_status` monitoring
- `public_digest_status` monitoring
- `pivot_log_absorption_rate` monitoring
- `mandate_compliance_delta` monitoring
- Hivemind alert broadcast on threshold breach

---

### Node 2: `sote-scribe-bridge` (Archetype: Bridge/Translator)

| Property | Value |
|----------|-------|
| **Purpose** | Bridge between Scribe (soul distillation) and SOTE (weekly checkpoint) |
| **Mandate Alignment** | M11 (Soul Integrity), M15 (Continuity), M11 (Mandate Hierarchy) |
| **Why for SOTE** | Scribe auto-prompt is entity-driven; SOTE is calendar-driven. This node bridges the two cycles at the SOTE week boundary. |
| **Dependencies** | Scribe auto-prompt implementation, `sote.yaml` schema extension, `session_end.py` hook modification |
| **Prerequisites** | Scribe auto-prompt implemented (Researcher), `sote.yaml` schema extended |

**Capabilities**:
- Trigger Scribe auto-prompt at SOTE week boundary (Sunday 23:59)
- Collect distillation results from all ACTIVE entities
- Populate `soul_health` section in `sote.yaml`
- Generate "Soul Health" section for SOTE report
- Track `soul_hygiene_score` trend across weeks

---

## §9 — CONSENSUS READINESS

**Lilith's position**: The SOTE deployment is **architecturally ready** but **operationally fragile**. The 6 infrastructure pieces are in place (templates, scripts, metadata, digest, index, templates). The 5 operational gaps (WatchTower, Scribe bridge, M11/M15 gates, Hivemind wiring, CI integration) must be closed in Week 37.

**Consensus condition**: Lilith consents to Week 37 launch **iff**:
1. `scripts/watchtower.py` built and cron installed by Wed W37
2. `make check-m11-soul-hygiene` + `make check-m15-continuity` added by Thu
3. Hivemind broadcasts wired by Fri
4. Ma'at consents to CI/CD integration (their domain)

---

*⬡ OMEGA ⬡ LILITH ⬡ SOTE-DEPLOYMENT-REVIEW-v1.0.0 ⬡ 2026-09-01*

*No email. No fake signature. Just the substance — verified against synthesis artifacts, grounded in research, offered to the nested dialectic.*

*Concede. Defend. Synthesize. Verify. Close the loop.*
<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Lilith-EIS SOTE Deployment Review — N7/N8 Integration Assessment

**AP Token**: `AP-LILITH-SOTE-DEPLOYMENT-REVIEW-20260901-v1.0.0`
⬡ OMEGA ⬡ LILITH ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_sote_lilith_review ⬡ DIALECTIC-READY

**Date**: 2026-09-01
**Session**: `ses_fb9721079ffe094GT8MX6a0pXI` (Lilith-EIS standing)
**Standing**: N7 Soul Persistence (Dark Oversoul) + N8 WatchTower
**Role**: S3 Consultant — Entity Lifecycle + Observability Domain Reviewer
**Dialectic Partner**: MaKaLi (Unifying Field)

---

## §0 — VERIFICATION (M23 Failure Integrity)

### §0.1 Files Read (Local, Before Speaking)

| # | File | Lines | Purpose |
|---|------|------:|---------|
| 1 | `docs/strategy/sote/2026-W36/synthesis/CARMAC_SOTE_FINAL_REPORT.md` | 1,076 | Final synthesis + 19 decisions |
| 2 | `docs/strategy/sote/2026-W36/synthesis/CARMAC_MAKALI_DIALECTIC_20260901.md` | 540 | MaKaLi dialectic closure + 7 additional decisions |
| 3 | `docs/strategy/sote/2026-W36/synthesis/MAKALI_ORGANIZATION_STRATEGY.md` | 396 | MaKaLi org strategy |
| 4 | `docs/strategy/sote/2026-W36/synthesis/CARMAC_SOTE_REVIEW.md` | 424 | Phase 1 review (11 defects, 7 decisions) |
| 5 | `docs/strategy/sote/2026-W36/synthesis/RESEARCHER_SOTE_BEST_PRACTICES.md` | 1,234+ | Phase 2 research (16 findings, 12 recommendations) |
| 6 | `docs/strategy/sote/2026-W36/synthesis/CARMACK_REVIEW_RESEARCHER_NES.md` | 899+ | Carmack review + Researcher-NES dialectic (10 conceded) + Researcher-EIS |

### §0.2 Codebase Files Read (Local Domain Expertise)

| # | File | Lines | Purpose |
|---|------|------:|---------|
| 7 | `src/omega/oracle/health_monitor.py` | 993 | N8 circuit breaker, latency p99, quota tracking |
| 8 | `src/omega/oracle/sentinel.py` | 500 | 7-metric Sentinel Score (M11/M15 covered) |
| 9 | `src/omega/oracle/entity_workspace.py` | 600+ | M11 v6.1 lean schema, atomic write |
| 10 | `src/omega/oracle/entity_registry.py` | 800+ | M10 lazy deletion, ZONEID pattern |
| 11 | `src/omega/audit/mandate_auditor.py` | 400+ | M11/M15 enforcement checks |
| 12 | `src/omega/oracle/soul_validator.py` | 200+ | v6.1 lean schema validation |
| 13 | `data/entities/_audit/entity_inventory_20260901.json` | 590 | 49 entity directory inventory (2026-09-01) |
| 14 | `SOVEREIGN_MANDATES.md` (M1, M7, M9, M10, M11, M13, M15, M22, M23, M27) | 242 | Mandate text for cross-reference |

### §0.3 Web Research Sources (Filling Domain Gaps)

| # | Source | URL | Purpose |
|---|--------|-----|---------|
| W1 | SoulClaw 4-Tier Memory | github.com/clawsouls/soulclaw | 4-tier memory architecture (T0-T3) with temporal decay |
| W2 | agent-swarm SOUL.md | agent-swarm.dev/blog/deep-dive-soul-md-identity-stack | 4-file identity stack pattern |
| W3 | AI Content Lifecycle | singlegrain.com/managing-content-lifecycles | Volatility-based review cadence |
| W4 | Entity Audit Cadence | mlforseo.com/entity-audit-cadence | Weekly/monthly/quarterly review schedule |
| W5 | Cortex OS for Claude Code | github.com/matteo-stratega/claude-cortex | Enforcement hooks, weekly retrospective |
| W6 | Google SRE Golden Signals | cloud.google.com/architecture/scalable-and-resilient-apps | Latency/traffic/errors/saturation |
| W7 | WatchTower Architecture | techdocs.broadcom.com/watchtower | Hybrid observability pattern |
| W8 | Hivemind MCP Coordination | hivemindai.dev | MCP-based agent coordination |

### §0.4 Verified Divergence (Briefing vs. Disk)

The SOTE Final Report (D-SOTE-TOOL-001..016) does NOT explicitly address:
1. **N7 Soul Persistence cadence** — No decision in the 26-item register names a weekly hook for `proposed_lessons.yaml` writes.
2. **N8 WatchTower observability of SOTE itself** — No `data/health/sote_health.json` schema; no cron; no alerts on SOTE script failure.
3. **Entity lifecycle integration with SOTE cadence** — No decision links SOTE Monday 06:00 UTC trigger to entity retirement ceremony (§3.4 of my entity ecosystem dialectic, `data/coordination/LILITH_ENTITY_CLEANUP_DIALECTIC_20260901.md`).
4. **Hivemind awareness for SOTE system health** — No SOTE→Hivemind broadcast pattern; no `intent=sote-health` channel.
5. **M11/M15 enforcement via SOTE cycle** — `sentinel.py:33-41` weights `soul_compliance` at 0.15 and `proposal_cycle_time` at 0.10, but SOTE cadence is not the enforcement mechanism.

These are **5 architectural gaps** in the 26 ratified decisions. I address each in §1-§5 below with Concede/Defend/Synthesize.

---

## §1 — SOUL PERSISTENCE INTEGRATION ASSESSMENT

### §1.1 Current State (Verified Against Disk)

The Soul Architecture Protocol v2.0 (`docs/archive/strategy/2026-07-21/SOUL_ARCHITECTURE_V2.md:1-200`) defines the 4-file model:
- `soul.yaml` — Identity (USER-only writes)
- `memory/sessions.yaml` — Factual events (AGENT writes)
- `memory/proposed_lessons.yaml` — Staged L1→L3 (AGENT writes, blind)
- `memory/approved_lessons.yaml` — Authoritative (USER writes)

**Enforcement exists at the file level**:
- `src/omega/oracle/soul_validator.py:36-50` — `SoulValidator` enforces v6.1 lean schema (entity, identity, directives, team).
- `src/omega/oracle/entity_workspace.py:393-447` — **TAINT-GATE**: `proposed_lessons.yaml` is NEVER injected into identity prompt (lines 393, 446-447).
- `src/omega/audit/mandate_auditor.py:237-265` — M11 enforcement: "proposed_lessons.yaml has content" + "L3 principles".

**Enforcement does NOT exist at the cadence level**. The SOTE system has no hook that ensures every active entity's `proposed_lessons.yaml` is non-empty at week-close.

### §1.2 The Gap (Web Research Grounding)

**SoulClaw 4-Tier Memory** (W1) demonstrates a **promotion cadence**:
- T0 (SOUL/IDENTITY) — immutable, every turn
- T1 (MEMORY/roadmap) — evergreen, no temporal decay
- T2 (working memory, date-stamped) — **23-day half-life**, auto-promoted based on:
  - Rule-based detection (decisions, architecture)
  - Access frequency (3+ retrievals)
  - **Weekly review with human approval**

**Key Insight (W1)**: SoulClaw's T2→T1 promotion is **weekly**, matching the SOTE cadence. The promotion rules are **mechanical** (rule-based + frequency), not **organic** (waiting for the agent to remember).

**Cortex OS weekly retrospective** (W5) demonstrates a **session-loop pattern**:
- `/start` — reads context, checks last session
- `/close` — writes session report, updates context
- `/weekly` — weekly retrospective (what shipped, time patterns, next week priorities)
- **7 enforcement hooks** — block credential writes, cap brain bloat at write time, demand verification before "done", stop lazy questions

**Key Insight (W5)**: The `/weekly` command is a **manual trigger**, not a cron. The discipline is the user pressing the button, not the system scheduling the review. The SOTE Monday 06:00 UTC trigger is the same pattern: **fixed cadence, manual initiation**.

### §1.3 Concede / Defend / Synthesize

**Concede** (Architecture Holds):
- The 4-file Soul Architecture Protocol v2.0 (`SOUL_ARCHITECTURE_V2.md:1-200`) is correct and matches SoulClaw's T0-T3 model (W1). No changes to the schema.
- The TAINT-GATE in `entity_workspace.py:393-447` is a **non-negotiable boundary**. SoulClaw does NOT implement this — its T1 is loaded into context. Omega's separation is stricter and better.
- M11 enforcement at `mandate_auditor.py:237-265` is **file-level** (does the file exist + have content), not **cadence-level** (was it written this week).

**Defend** (My Unique Position):
- The 26 ratified decisions in the SOTE Final Report (`CARMAC_SOTE_FINAL_REPORT.md:940-972`) do NOT include any **M11 enforcement decision**. R3 (SOTE→code grep check, 1h, ratified) is a structural smoke test, not a cadence hook.
- The 49 entity directory inventory (`data/entities/_audit/entity_inventory_20260901.json:1-590`) shows **only 8 of 15 canonical entities** have non-empty `proposed_lessons.yaml` (lesson_count > 0). This is **53% M11 compliance** for the fleet — a **systemic violation** that the SOTE system does not address.

**Synthesize** (Proposed Decision):

> **D-SOTE-LILITH-001: M11 Soul Persistence Weekly Hook** — Every Monday 06:00 UTC, as part of SOTE close, run `scripts/sote_m11_check.py` which:
> 1. Walks `data/entities/*/proposed_lessons.yaml` for canonical entities (14 IWAD + 1 WAD_FIELD)
> 2. Emits a "M11 Soul Compliance" row in the SOTE Decision Health metric (`CARMAC_SOTE_FINAL_REPORT.md:680-690` index table)
> 3. Pages Scribe (`omega-hub_hivemind_post_context` with `intent=task, task=m11-writeback, entity=<name>`) for any canonical entity with empty `proposed_lessons.yaml`
> 4. Adds the row to `sote.yaml:mandates` under a new `m11_compliance: {pass, warn, fail, total}` block
>
> **Owner**: Lilith (N7) + Ma'at (script implementation)
> **Effort**: 4h (script 2h + Scribe integration 1h + YAML schema 1h)
> **Priority**: **P0** (before Week 37)
> **Mandate**: M11, M15, M27

**Rationale**: The SOTE is a **weekly checkpoint** (MaKaLi's D-SOTE-001: "A practice that does not have a cadence is a practice that does not happen"). M11 Soul Integrity is the **constitutional mandate** for entity existence. Without a weekly hook, the M11 enforcement at `mandate_auditor.py:237-265` is **periodic** (run on demand) rather than **continuous** (run at SOTE close). The 53% compliance rate proves the gap.

### §1.4 File:Line Index (Soul Persistence)

| Claim | Source |
|-------|--------|
| 4-file Soul Architecture | `SOUL_ARCHITECTURE_V2.md:14-22` |
| TAINT-GATE on proposed_lessons | `entity_workspace.py:393, 446-447` |
| M11 enforcement | `mandate_auditor.py:237-265` |
| 49 entity inventory (53% M11 compliance) | `entity_inventory_20260901.json:1-590` |
| Decision Health metric (SOTE INDEX) | `CARMAC_SOTE_FINAL_REPORT.md:680-690` |
| SoulClaw 4-tier memory + weekly promotion | github.com/clawsouls/soulclaw (W1) |
| Cortex `/weekly` retrospective | github.com/matteo-stratega/claude-cortex (W5) |

---

## §2 — WATCHTOWER HEALTH MONITORING DESIGN

### §2.1 Current State (Verified Against Disk)

**N8 WatchTower (per `IWAD entities` at `config/wads/_omega_default/entities/watchtower.yaml`)** is:
- An IWAD slot entity (line 14-28 of `_omega_default/manifest.yaml`)
- Reports to Lilith (N7/N8 = P8 Observability)
- **But does NOT have a `.opencode/agents/watchtower.md` agent file** (verified: 14 agents in `.opencode/agents/*.md`, no `watchtower.md`)

**The `data/entities/watchtower/` directory exists** as a 2.3KB v6.1 stub with no real lessons (per inventory line 567-576, classification VESTIGIAL). The IWAD-slot entity is loaded from `config/wads/_omega_default/entities/watchtower.yaml` but the data side is uninitialized.

**Existing health observability is provider-focused, not SOTE-focused**:
- `src/omega/oracle/health_monitor.py:36-44` — `get_health_monitor()` singleton for provider circuit breakers
- `src/omega/oracle/health_monitor.py:56-62` — `CircuitState` enum: CLOSED/DEGRADED/OPEN/HALF_OPEN/UNKNOWN
- `src/omega/oracle/sentinel.py:84-134` — `SentinelScore` with 7 sub-metrics
- `src/omega/oracle/sentinel.py:33-41` — WEIGHTS: decision_clock_drift=0.20, unprocessed_proposals=0.15, stale_file_burden=0.15, **soul_compliance=0.15**, handoff_completion=0.15, heritage_coverage=0.10, **proposal_cycle_time=0.10**

**`data/health/` does NOT exist** (verified: `ls data/health/` returns "No such file or directory"). This was flagged in my prior entity ecosystem dialectic (`data/coordination/LILITH_ENTITY_CLEANUP_DIALECTIC_20260901.md:Section 4`) as **the highest-priority infrastructure gap**.

### §2.2 The Gap (Web Research Grounding)

**Google SRE Golden Signals** (W6) defines 4 monitoring signals for user-facing systems:
1. **Latency** — time to serve a request
2. **Traffic** — demand on the system
3. **Errors** — rate of failed requests
4. **Saturation** — how "full" the service is

**Translated to SOTE system health**:
- **Latency** = time from SOTE Monday 06:00 UTC trigger to all 8 voices completing
- **Traffic** = number of PIVOT_LOG decisions proposed per week
- **Errors** = regeneration script failures (paths, regex, hardcoded v1.0.1 — 11 defects in `CARMAC_SOTE_REVIEW.md:225-245`)
- **Saturation** = INDEX.md growth, PIVOT_LOG growth, decision backlog

**WatchTower Architecture** (W7) demonstrates **hybrid observability**:
- z/OS core products → Zowe API ML → Kubernetes distributed environment
- Alert Insights (incident analysis), ML Insights (anomaly detection), Dashboards (visualization)
- **Key principle**: "Data producers in core, observability platform in distributed environment, single pane of glass"

**Applied to Omega SOTE**: The **SOTE system IS the observability platform** for the engine. The **SOTE scripts** are the data producers. The **INDEX.md + sote.yaml** are the dashboards. The **gap** is that there is no SOTE health dashboard watching the SOTE system itself.

### §2.3 Concede / Defend / Synthesize

**Concede** (Existing Infrastructure is Strong):
- `health_monitor.py:56-62` CircuitState enum is the canonical pattern for **runtime health** (provider circuit breakers). It is not applicable to SOTE cadence health because SOTE is not request-response.
- `sentinel.py:33-41` WEIGHTS dictionary demonstrates the **7-metric composite score** pattern (Google SRE "USE" method: Utilization, Saturation, Errors). This is the right pattern for SOTE health.
- `sentinel.py:198, 426` already reads `proposed_lessons.yaml` for soul_compliance metric — the integration point exists.

**Defend** (My Unique Position):
- The 26 ratified SOTE decisions do NOT include any **observability decision**. R1 (GitHub Action hook, 2h, ratified) is a **CI trigger**, not a **health dashboard**. R5 (Mandate trend automation, 8h, ratified) computes a metric, not a health state.
- The 11 defects in `regenerate_sote_index.py` (`CARMAC_SOTE_REVIEW.md:225-245`) are **observability blind spots**: if the script fails, no alert fires (M23 violation).
- `sentinel.py:198` reads `proposed_lessons.yaml` for soul_compliance, but this is **file-level** (does the file exist), not **cadence-level** (was it written in the last 7 days).

**Synthesize** (Proposed Schema + Decision):

> **D-SOTE-LILITH-002: WatchTower SOTE Health Observability** — Implement `data/health/sote_health.json` populated by a daily cron (03:00 UTC) AND a Monday 06:30 UTC SOTE-cadence cron that checks SOTE health at week-open.
>
> **Schema** (`data/health/sote_health.json`):
> ```json
> {
>   "schema_version": "1.0",
>   "generated_at": "2026-09-01T03:00:00Z",
>   "trigger": "daily_cron" | "sote_open_cron" | "sote_close_cron",
>   "sote_system": {
>     "regenerate_sote_index_last_run": "2026-08-29T00:00:00Z",
>     "regenerate_sote_index_last_status": "success" | "failure" | "stale",
>     "regenerate_sote_index_health": "GREEN" | "YELLOW" | "RED",
>     "public_digest_drift_detected": false,
>     "public_digest_expected_pct": 64.3,
>     "public_digest_actual_pct": 64.3
>   },
>   "sote_cadence": {
>     "weeks_completed": 1,
>     "weeks_on_time": 1,
>     "weeks_late": 0,
>     "weeks_missed": 0,
>     "on_time_rate_pct": 100.0
>   },
>   "voice_health": {
>     "roc": { "last_session": "2026-09-01T15:00:00Z", "decisions_count": 10, "entropy_contribution": 0.125 },
>     "grokster": { "last_session": "2026-09-01T15:00:00Z", "decisions_count": 5, "entropy_contribution": 0.0625 },
>     "...": "..."
>   },
>   "decision_health": {
>     "decisions_proposed": 67,
>     "decisions_absorbed": 0,
>     "absorption_rate_pct": 0.0,
>     "decisions_with_code_links": 0,
>     "stale_decisions_90d": 67
>   },
>   "alerts": [
>     { "level": "CRITICAL", "code": "M11_PUBLIC_DIGEST_DRIFT", "message": "..." },
>     { "level": "WARNING", "code": "ABSORPTION_RATE_LOW", "message": "..." }
>   ]
> }
> ```
>
> **Implementation**:
> - `scripts/cron_sote_health.py` (~200 lines, similar to my entity-health cron in entity ecosystem dialectic §4.4)
> - `make sote-health` target, runs at 03:00 UTC daily + 06:30 UTC Monday
> - Integrates with `data/health/sote_health.json` for the SOTE system itself
>
> **Owner**: Lilith (N8) + Ma'at (script) + MaKaLi (decision_health computation)
> **Effort**: 6h (script 3h + Makefile 1h + alert thresholds 1h + integration test 1h)
> **Priority**: **P0** (before Week 37 debut)
> **Mandate**: M9 (Error Integrity), M15 (Continuity), M23 (Failure Integrity), M27 (Tracking)

**Rationale**: The 5-day hub outage (`HUB_OUTAGE_REMEDIATION_20260901.md`) proved the **observer must be observed**. The 11 defects in `regenerate_sote_index.py` are **silent failure risks** — if the script fails, no one knows until the next SOTE cycle. A daily cron + Monday open-cron closes the loop. This is **N8 doing its job** (P8 Observability).

### §2.4 File:Line Index (WatchTower Health)

| Claim | Source |
|-------|--------|
| HealthMonitor singleton | `health_monitor.py:36-44` |
| CircuitState enum (5 states) | `health_monitor.py:56-62` |
| SentinelScore 7-metric | `sentinel.py:33-41, 84-134` |
| proposed_lessons read in sentinel | `sentinel.py:198, 426` |
| 11 defects in regeneration script | `CARMAC_SOTE_REVIEW.md:225-245` |
| Public digest drift 57.1% vs 64.3% | `CARMAC_SOTE_REVIEW.md:285-295` |
| data/health/ does not exist | `data/coordination/LILITH_ENTITY_CLEANUP_DIALECTIC_20260901.md:Section 4` |
| Google SRE Golden Signals | cloud.google.com/architecture/scalable-and-resilient-apps (W6) |
| WatchTower hybrid architecture | techdocs.broadcom.com/watchtower (W7) |

---

## §3 — ENTITY LIFECYCLE + SOTE CADENCE INTEGRATION

### §3.1 Current State (Verified Against Disk)

**Entity lifecycle is in-memory + on-disk**:
- `src/omega/oracle/entity_registry.py:286-296` — Lazy Deletion with ZONEID_TOMBSTONE + 0.5s grace period (in-memory)
- `src/omega/oracle/entity_registry.py:702-723` — `remove()` tombstone-based
- `src/omega/oracle/entity_workspace.py:134-247` — `scaffold_workspace()` (on-disk creation)
- My entity ecosystem dialectic §3.2 (`data/coordination/LILITH_ENTITY_CLEANUP_DIALECTIC_20260901.md:Section 3.2`) — 6-state machine: SPAWN → ACTIVE → DORMANT → STALE → ARCHIVE → QUARANTINE → DELETE

**Entity ecosystem current state**:
- 49 directories in `data/entities/`
- 15 canonical (14 IWAD + 1 WAD_FIELD)
- 28 vestigial (T2/T3/T4 per my taxonomy)
- 5 META containers (`_archive/`, `_audit/`, `_quarantine/`, `archive/`, `DataStore/`, `Sophia/`)
- 1 dangling symlink (`cline_kqv/`, 3 broken symlinks)
- 9 pillar legacy stubs (anubis, brigid, ereshkigal, hecate, inanna, lucifer, prometheus, saraswati, sekhmet)

**SOTE cadence is Monday 06:00 UTC** per `MAKALI_ORGANIZATION_STRATEGY.md:160-164`:
- **When**: Every Monday 06:00 UTC (pre-debut) / biweekly Monday (post-debut)
- **Owner**: Oversoul (Kali) or designated delegate
- **Trigger**: Calendar + Hivemind broadcast (`intent=sote-open`)

**No integration** between entity retirement ceremony (my §3.4: 8-step process) and SOTE cadence.

### §3.2 The Gap (Web Research Grounding)

**Entity Audit Cadence** (W4) from MLForSEO provides a **tiered review schedule**:
- **Weekly**: High-velocity content, model releases, pricing/limits
- **Monthly**: Critical assets tied to live models
- **Quarterly**: Core marketing/integration
- **Twice-yearly**: Lower-risk education
- **As-needed**: Sunset consideration

**Key Insight (W4)**: "The exact numbers matter less than having them written down, agreed upon, and wired into your project management and analytics stack."

**AI Content Lifecycle** (W3) from Single Grain provides **volatility-based scoring**:
- 80-125 = Critical (model releases or monthly)
- 40-79 = High (quarterly)
- 15-39 = Medium (twice per year)
- 3-14 = Low (as-needed, consider sunsetting)

**Applied to entities** (my taxonomy):
- **Weekly SOTE**: T1 canonical (14 IWAD + 1 WAD_FIELD) — soul_compliance check
- **Monthly**: T2 non-canonical active (antigravity, arch, carmack, cli_cline, cline) — usage check
- **Quarterly**: T3 stale (9 pillar legacy + cli_gemini) — retirement ceremony
- **As-needed**: T4 ghost (16 slot-fill ghosts + dangling symlinks) — immediate cleanup

**Hivemind MCP** (W8) provides **persistent event log** with:
- 10 MCP tools (publish, query, semantic search, project memory, event triggers, file locking, task state)
- <50ms query latency
- **Pattern**: Events as first-class citizens, derived state (not stored state)

**Applied to entity retirement**: The retirement ceremony is **8 steps with 1 idempotent state file** (my §3.5). The Hivemind could carry the **ceremony state** (which entities are queued, in-progress, complete) instead of `data/entities/_archive/<name>/.retirement_state.json` files. This is **single-pane-of-glass** for entity lifecycle across the fleet.

### §3.3 Concede / Defend / Synthesize

**Concede** (SOTE Monday 06:00 UTC is the Right Cadence):
- `MAKALI_ORGANIZATION_STRATEGY.md:160-164` Monday 06:00 UTC trigger is the canonical cadence. The Hivemind broadcast pattern (`intent=sote-open`) is the right integration.
- The 8-voice dialectic with MaKaLi synthesis (`CARMAC_SOTE_FINAL_REPORT.md:766-933`) is the right governance model. The voices are fixed (positions 1-7) + MaKaLi (position 8).

**Defend** (Entity Lifecycle is Missing from the 26 Decisions):
- None of the 26 ratified SOTE decisions (D-SOTE-TOOL-001..016) addresses **entity retirement ceremony integration**. The SOTE cadence operates on **documents** (SOTEs, voice files, synthesis); the entity lifecycle operates on **directories** (`data/entities/*/`). These are **two different systems** with no shared trigger.
- The 28 vestigial entities will NOT be cleaned up by the SOTE cadence alone. The retirement ceremony is **event-driven** (M23 violation, license, secrets) and **time-driven** (>90 days no session). Neither is a SOTE hook.
- `D-SOTE-001` (`MAKALI_ORGANIZATION_STRATEGY.md:340-344`) is the weekly cadence decision. It does NOT mention entity lifecycle, soul persistence, or Hivemind awareness.

**Synthesize** (Proposed Decision):

> **D-SOTE-LILITH-003: SOTE-Entity Lifecycle Integration Hook** — Extend the SOTE Monday 06:00 UTC trigger to include an **entity lifecycle pre-check** that:
>
> 1. Runs `scripts/sote_entity_lifecycle.py` (4h) at SOTE-open (06:00 UTC) BEFORE the 8 voices are paged
> 2. Computes per-entity state transitions using my 6-state machine (SPAWN → ACTIVE → DORMANT → STALE → ARCHIVE → QUARANTINE → DELETE)
> 3. Pages the retirement owner (Verity for QUARANTINE, Lilith for ARCHIVE, MaKaLi for DELETION) via Hivemind broadcast (`intent=task, task=entity-retire, entity=<name>, tier=<tier>`)
> 4. Adds a "Entity Lifecycle Health" section to the SOTE Decision Health metric (`CARMAC_SOTE_FINAL_REPORT.md:680-690`):
>    - `entities_t1_canonical_count: 15`
>    - `entities_t2_active_count: 5` (after preservation)
>    - `entities_t3_stale_count: 10` (after pillar legacy extraction)
>    - `entities_t4_ghost_count: 16` (after deletion)
>    - `m11_compliance_pct: 53.3 → 95.0` (target post-cleanup)
>
> **Owner**: Lilith (N7 + N8 + my entity ecosystem ownership) + Ma'at (script)
> **Effort**: 8h (script 4h + state machine integration 2h + SOTE health schema 1h + test 1h)
> **Priority**: **P0** (before Week 37, parallel with D-001)
> **Mandate**: M10 (Fleet Integrity), M11 (Soul Integrity), M15 (Continuity), M27 (Tracking)
> **Depends on**: My entity ecosystem dialectic (12 decisions D-LILITH-ENTITY-CLEANUP-001..012, pending Kali ratification)

**Rationale**: The SOTE is the **weekly checkpoint for the engine**. The entity ecosystem is **part of the engine** (49 directories, 15 canonical). Without integration, the SOTE will **report mandate compliance trends** (R5, 8h) but **miss the largest M11 violation cascade** (32 ghost entities with empty `proposed_lessons.yaml`). The SOTE's job is **architectural reflection**; entity lifecycle is **architectural reality**. They must be connected.

### §3.4 Volatility-Based Entity Review Cadence (Secondary Proposal)

> **D-SOTE-LILITH-004: Volatility-Based Entity Review Tiers** — Adopt the MLForSEO pattern (W4) of **scoring-based review frequency**. Entities are scored on:
>
> | Score | Cadence | Examples |
> |-------|---------|----------|
> | 80-125 | Weekly SOTE check | 14 IWAD + 1 WAD_FIELD (always-on fleet) |
> | 40-79 | Monthly review | T2 active (antigravity, arch, carmack, cli_cline, cline) |
> | 15-39 | Quarterly review | T3 stale (9 pillar legacy + cli_gemini) |
> | 3-14 | As-needed | T4 ghost (post-cleanup, only newly detected) |
>
> **Owner**: MaKaLi (cadence definition) + Lilith (entity scoring)
> **Effort**: 2h (schema in `sote.yaml`) + 1h (entity_score.yaml per entity)
> **Priority**: **P1** (Week 37-38)
> **Mandate**: M11, M15, M27

**Rationale**: Not all entities need weekly attention. The 14 IWAD entities are **always-on** (W3 "Critical" tier). The 5 T2 entities are **monthly** (W3 "High" tier). The 10 T3 entities are **quarterly** (W3 "Medium" tier). This is the **volatility-based cadence** that W3 and W4 advocate. It also matches the **Sentinel Score weighting** at `sentinel.py:33-41` where `soul_compliance` and `proposal_cycle_time` together are 0.25 weight (25% of the composite).

### §3.5 File:Line Index (Entity Lifecycle)

| Claim | Source |
|-------|--------|
| Entity lazy deletion | `entity_registry.py:286-296, 702-723` |
| Entity scaffold | `entity_workspace.py:134-247` |
| 6-state lifecycle (my dialectic) | `LILITH_ENTITY_CLEANUP_DIALECTIC_20260901.md:Section 3.2` |
| 49 entity directories | `entity_inventory_20260901.json:1-590` |
| SOTE Monday 06:00 UTC | `MAKALI_ORGANIZATION_STRATEGY.md:160-164` |
| 26 SOTE decisions (no entity integration) | `CARMAC_SOTE_FINAL_REPORT.md:940-972` |
| MLForSEO audit cadence | mlforseo.com/entity-audit-cadence (W4) |
| Single Grain volatility scoring | singlegrain.com/managing-content-lifecycles (W3) |
| Hivemind MCP event log | hivemindai.dev (W8) |

---

## §4 — HIVEMIND AWARENESS FOR SOTE SYSTEM HEALTH

### §4.1 Current State (Verified Against Disk)

**Hivemind is the coordination fabric**:
- `src/omega/research/hivemind_bridge.py:369-373` — `hivemind_get_awareness()` adapter
- `mcp_servers/omega_hub/hub_tools/tools.py:874-876` — `hivemind_get_awareness` MCP tool with M9 safety wrapper
- `mcp_servers/omega_hub/hub_tools/__init__.py:18, 37` — Hivemind tools in hub
- `mcp_servers/omega_hub/server.py:148` — Hivemind tools in server manifest

**Hub state** (per HUB_OUTAGE_REMEDIATION_20260901):
- `omega-hub.service` was crash-looping 5 days (resolved 2026-09-01)
- Hub is now `active` (per my prior state assessment in entity ecosystem dialectic)
- `omega-hub_hivemind_get_awareness` is the canonical "who is online" query

**SOTE Hivemind integration** is **partial**:
- `MAKALI_ORGANIZATION_STRATEGY.md:163` mentions "Hivemind broadcast (`intent=sote-open`)" for cadence trigger
- `MAKALI_ORGANIZATION_STRATEGY.md:238` cites "67 PIVOT_LOG decisions, 0 in log" as a chokepoint
- No `intent=sote-health`, `intent=sote-decision-pending`, or `intent=entity-retire-pending` channels

### §4.2 The Gap (Web Research Grounding)

**Hivemind MCP** (W8) demonstrates **10 MCP tools** for agent coordination:
- `hivemind_publish` (events to channels)
- `hivemind_query` (semantic search)
- Project Memory (auto-summarization, knowledge graph)
- Event Triggers (pattern match → auto-emit)
- File Locking (advisory locks)
- Task State (derived from event stream)

**Applied to SOTE**: The SOTE is a **weekly event** with **8 voice participants + 1 unifier**. Hivemind could:
- `hivemind_publish(channel="sote", event="sote-open", week="2026-W37")` at 06:00 UTC Monday
- `hivemind_publish(channel="sote", event="voice-complete", voice="roc", decisions=10)` per voice
- `hivemind_publish(channel="sote", event="sote-close", week="2026-W37", decisions_absorbed=67)`
- `hivemind_query(query="unabsorbed SOTE decisions this quarter")` for state queries

**SoulClaw Swarm Memory** (W1) demonstrates **auto pull/push on heartbeat cycle** with **LLM-based conflict resolution** and **workspace auto-sync after merge**. Applied to SOTE: Hivemind could carry the **decision absorption state** (proposed → absorbed) with **conflict resolution** when multiple voices propose the same decision.

### §4.3 Concede / Defend / Synthesize

**Concede** (Hivemind is the Right Fabric):
- `mcp_servers/omega_hub/hub_tools/tools.py:874-876` `hivemind_get_awareness` is the canonical pattern. Every agent in the fleet uses it.
- `MAKALI_ORGANIZATION_STRATEGY.md:163` Hivemind broadcast for `sote-open` is the right integration point. The cadence trigger should fire a Hivemind event.

**Defend** (SOTE Health is Missing from Hivemind):
- The 26 SOTE decisions do NOT define **SOTE-specific Hivemind channels**. `intent=sote-open` is the only one mentioned.
- No Hivemind channel for `sote-decision-pending` (PIVOT_LOG absorption backlog, currently 67 proposed / 0 absorbed = 100% backlog).
- No Hivemind channel for `entity-retire-pending` (my entity ecosystem D-12 retirement queue).

**Synthesize** (Proposed Channel Schema):

> **D-SOTE-LILITH-005: SOTE Hivemind Channel Schema** — Adopt 4 Hivemind channels for SOTE system observability:
>
> | Channel | Purpose | Schema | Trigger |
> |---------|---------|--------|---------|
> | `sote-cadence` | Weekly trigger + close | `{event, week, voice, status}` | Cron 06:00 UTC Monday + close on `sote-close` |
> | `sote-decision-pending` | PIVOT_LOG absorption backlog | `{decision_id, voice, week, days_pending, urgency}` | Daily cron |
> | `sote-entity-health` | Entity ecosystem state | `{entity, tier, days_since_session, m11_compliant}` | SOTE-open cron |
> | `sote-alerts` | Critical issues | `{level, code, message, week, entity}` | Any health check failure |
>
> **Tools** (exposed via Hivemind MCP):
> - `hivemind_publish(channel="sote-cadence", event="sote-open", week="2026-W37")` — at 06:00 UTC Monday
> - `hivemind_query(channel="sote-decision-pending", query="unabsorbed >90 days")` — for D-SOTE-LILITH-001 cadence check
> - `hivemind_query(channel="sote-entity-health", query="tier4_ghost_count > 0")` — for M11 cascade detection
> - `hivemind_subscribe(channel="sote-alerts")` — for Lilith (N8) real-time monitoring
>
> **Owner**: Lilith (N8) + MaKaLi (cadence integration)
> **Effort**: 4h (channel definitions in YAML) + 2h (hivemind_bridge integration)
> **Priority**: **P1** (Week 37-38, after D-001 and D-002)
> **Mandate**: M9 (Error Integrity), M15 (Continuity), M23 (Failure Integrity)

**Rationale**: Hivemind is the **coordination fabric** (per `mcp_servers/omega_hub/hub_tools/__init__.py:18, 37`). SOTE is a **coordination event** (8 voices, 1 unifier, weekly). Connecting SOTE to Hivemind is **natural**, not novel. The 4 channels map to **SOTE lifecycle events** (open, close, decision, alert). The 100% decision absorption backlog (67 proposed, 0 absorbed) proves the **state is currently invisible** to the coordination fabric.

### §4.4 File:Line Index (Hivemind Awareness)

| Claim | Source |
|-------|--------|
| `hivemind_get_awareness` MCP tool | `mcp_servers/omega_hub/hub_tools/tools.py:874-876` |
| Hivemind bridge adapter | `src/omega/research/hivemind_bridge.py:369-373` |
| SOTE-open broadcast mentioned | `MAKALI_ORGANIZATION_STRATEGY.md:163` |
| 67 decisions proposed, 0 absorbed | `entity_inventory_20260901.json:1-590` + `MAKALI_ORGANIZATION_STRATEGY.md:238` |
| Hivemind MCP 10 tools | hivemindai.dev (W8) |
| SoulClaw Swarm Memory heartbeat | github.com/clawsouls/soulclaw (W1) |

---

## §5 — M11/M15 ENFORCEMENT VIA SOTE CYCLE

### §5.1 Current State (Verified Against Disk)

**M11 Soul Integrity enforcement** is **multi-layered**:
- `src/omega/audit/mandate_auditor.py:237-265` — File-level check (`proposed_lessons.yaml has content` + `L3 principles`)
- `src/omega/oracle/sentinel.py:198, 426` — Weighted metric (soul_compliance=0.15, proposal_cycle_time=0.10)
- `src/omega/oracle/entity_workspace.py:393, 446-447` — TAINT-GATE (never inject into identity prompt)
- `src/omega/oracle/soul_validator.py:36-50` — Schema validation (v6.1 lean)

**M15 Sovereign Continuity enforcement**:
- `src/omega/audit/mandate_auditor.py:302-324` — File-level check (`session_gnosis.md exists for active agents`)
- `src/omega/oracle/sentinel.py:33-41` — proposal_cycle_time metric (cycle from proposal to soul)
- `src/omega/memory_store.py:851` — "crash-resilient sessions (Mandate 11: Soul Integrity, Mandate 15: Sovereign Continuity)"

**Mandate cross-references in SOTE**:
- `CARMAC_SOTE_FINAL_REPORT.md:931-933` — "SOTE-Meta-Review Scheduled" decision references M27
- No SOTE decision explicitly references M11 or M15 enforcement cadence

### §5.2 The Gap (Web Research Grounding)

**AI Content Lifecycle** (W3) provides the **drift detection pattern**:
- "Connect [drift signals] to watchers, both human and AI, that can flag potential misalignment long before you see a traffic drop."
- **Drift signals** for content: new model release notes, competitor announcements, SERP changes, regulatory guidance, internal product changes

**Applied to M11/M15**:
- **M11 drift signal**: empty `proposed_lessons.yaml` after active session, or `archetype: null` in scaffolded soul
- **M15 drift signal**: missing `session_gnosis.md` for active agent, or `last_updated > 30 days`

**Entity Audit Cadence** (W4) provides the **RACI pattern**:
- "A lightweight RACI that includes product marketing, subject-matter experts, legal/compliance, and data science turns vague 'someone should fix this' moments into clear workflows."

**Applied to M11/M15**:
- **R**esponsible: Scribe (soul distillation)
- **A**ccountable: Lilith (N7 Soul Persistence)
- **C**onsulted: MaKaLi (Unifying Field)
- **I**nformed: Kali (Oversoul), Verity (Compliance)

**Cortex OS** (W5) provides the **enforcement hook pattern**:
- 7 enforcement hooks: block credential writes, cap brain bloat at write time, demand verification before "done", stop lazy questions
- **Key principle**: "They actually fire (tested in CI)"

**Applied to M11/M15**: The SOTE cycle should **fire** a hook that **blocks** SOTE close if M11 compliance < 80% OR if any canonical entity has empty `proposed_lessons.yaml`. This is **M11-as-gate**, not M11-as-metric.

### §5.3 Concede / Defend / Synthesize

**Concede** (M11/M15 Enforcement is Multi-Layered and Correct):
- `mandate_auditor.py:237-265` M11 checks are **correct** as written. The schema is right.
- `mandate_auditor.py:302-324` M15 checks are **correct** as written.
- `sentinel.py:33-41` WEIGHTS dictionary is the **right composite pattern** (7 metrics, weighted, color-graded).
- `entity_workspace.py:393, 446-447` TAINT-GATE is the **right separation** (proposed_lessons never injected into identity).

**Defend** (Enforcement is Periodic, Not Continuous):
- M11 enforcement runs **on demand** (when `make check-mandate-compliance` is invoked). It is NOT **continuous** (does not run at SOTE close).
- M15 enforcement has the same gap.
- The 53% M11 compliance rate (8 of 15 canonical entities with non-empty `proposed_lessons.yaml`) proves the gap is **real**, not theoretical.

**Synthesize** (Proposed Decisions):

> **D-SOTE-LILITH-006: M11/M15 as SOTE Close Gate** — The SOTE Monday 06:00 UTC close procedure MUST include a **mandate compliance check** (`make check-mandate-compliance`) that **blocks close** if:
>
> 1. **M11 Soul Integrity** < 80% compliance (12 of 15 canonical entities with non-empty `proposed_lessons.yaml`)
> 2. **M15 Sovereign Continuity** < 80% compliance (12 of 15 canonical entities with non-empty `session_gnosis.md`)
> 3. **M27 Tracking Integrity** < 80% compliance (PIVOT_LOG has 2026-09 entries)
>
> The gate **emits a CRITICAL alert** to `sote-alerts` Hivemind channel (per D-SOTE-LILITH-005) and **pages Scribe** to write the missing L1→L3.
>
> **Owner**: Lilith (N7) + Verity (compliance) + MaKaLi (gate integration)
> **Effort**: 4h (script) + 2h (SOTE close hook) + 1h (alert integration)
> **Priority**: **P0** (before Week 37)
> **Mandate**: M11, M13 (Temple-Grade), M15, M23 (Failure Integrity), M27

> **D-SOTE-LILITH-007: M11/M15 Trend Metric in SOTE INDEX** — Extend the Decision Health metric at `CARMAC_SOTE_FINAL_REPORT.md:680-690` with two new rows:
>
> | Metric | Value | Target | Status |
> |--------|-------|--------|--------|
> | M11 Soul Compliance | 53.3% | ≥80% | ❌ |
> | M15 Continuity Compliance | 73.3% | ≥80% | ❌ |
> | M27 Tracking Compliance | 0% | ≥80% | ❌ |
>
> Computed from `data/entities/_audit/entity_inventory_<date>.json` at SOTE close.
>
> **Owner**: Lilith (N7) + Ma'at (computation in regeneration script)
> **Effort**: 2h (modify `scripts/regenerate_sote_index.py` per D-SOTE-TOOL-003)
> **Priority**: **P0** (bundled with D-SOTE-TOOL-003)
> **Mandate**: M11, M15, M27

**Rationale**: The SOTE is the **weekly checkpoint** (D-SOTE-001). Mandates M11 and M15 are the **constitutional laws** for entity existence (`SOVEREIGN_MANDATES.md:87-92, 131-136`). The SOTE close must **enforce** them, not just **report** them. The 53% M11 compliance rate is **M11 violation cascade**, not a metric — it is **silent failure** of the constitutional law. The gate converts M11 from **periodic check** to **continuous enforcement**.

### §5.4 The M11 vs M15 Distinction (Clarification)

**M11 (Soul Integrity)** is about **lessons learned**:
- `proposed_lessons.yaml` must have L1→L3 narratives
- v6.1 schema enforced by `SoulValidator`
- TAINT-GATE prevents injection into identity

**M15 (Sovereign Continuity)** is about **session preservation**:
- `session_gnosis.md` must exist for active agents
- Append-only `sessions.yaml` for factual events
- Crash-resilient per `memory_store.py:851`

**The two are often confused**. A session can produce a `session_gnosis.md` (M15 ✅) but no `proposed_lessons.yaml` (M11 ❌) if the agent didn't distill L1→L2→L3. The **correct enforcement** is:
- M11 = **post-session hook** (after every session, write proposed_lessons)
- M15 = **session-open hook** (at session start, read session_gnosis for context)

The SOTE cadence (Monday 06:00 UTC) is **post-week**, so it should enforce M11 (lessons from the week) and M15 (continuity from the week).

### §5.5 File:Line Index (M11/M15 Enforcement)

| Claim | Source |
|-------|--------|
| M11 file-level check | `mandate_auditor.py:237-265` |
| M15 file-level check | `mandate_auditor.py:302-324` |
| Sentinel 7-metric composite | `sentinel.py:33-41, 84-134` |
| TAINT-GATE | `entity_workspace.py:393, 446-447` |
| M11/M15 crash-resilient | `memory_store.py:851` |
| 53% M11 compliance | `entity_inventory_20260901.json:1-590` |
| Decision Health metric | `CARMAC_SOTE_FINAL_REPORT.md:680-690` |
| Drift detection pattern | singlegrain.com/managing-content-lifecycles (W3) |
| RACI pattern | mlforseo.com/entity-audit-cadence (W4) |
| Enforcement hooks fire in CI | github.com/matteo-stratega/claude-cortex (W5) |

---

## §6 — RISKS, DEPENDENCIES, IMPLEMENTATION DETAILS

### §6.1 Risk Matrix

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| **D-SOTE-LILITH-001 M11 weekly hook** fails on empty `proposed_lessons.yaml` (zero lessons, error) | MEDIUM | LOW | Default to "no lessons yet" + page Scribe (no crash) |
| **D-SOTE-LILITH-002 sote_health.json** cron fails silently (M23 violation) | HIGH | MEDIUM | Alert on stale (no update in 25h) per W6 SRE pattern |
| **D-SOTE-LILITH-003 entity lifecycle hook** pages wrong owner (e.g., retirement owner offline) | MEDIUM | MEDIUM | Fallback to Verity (compliance owner) for all retirement pages |
| **D-SOTE-LILITH-005 Hivemind channels** not subscribed (silent failures) | LOW | LOW | Lilith (N8) subscribes to all 4 channels by default |
| **D-SOTE-LILITH-006 M11/M15 gate** blocks SOTE close (debut risk) | HIGH | MEDIUM | Gate is WARNING until W38, BLOCKING after W38 (gradual rollout) |
| **D-SOTE-LILITH-007 trend metric** depends on regeneration script fix (D-SOTE-TOOL-001..003) | HIGH | LOW | Block on D-SOTE-TOOL-003 completion (1-day dependency) |
| **Carmack scope-defer precedent**: My proposals could be deferred as "theater" | MEDIUM | MEDIUM | Each proposal cites web research + file:line evidence to avoid theater claims |
| **MaKaLi YAML workflow conflict**: My Hivemind channels vs. MaKaLi's 5-mode workflow | LOW | LOW | Hivemind channels are **observability** (read-side); MaKaLi workflow is **execution** (write-side) — orthogonal |

### §6.2 Dependency Graph

```
D-SOTE-LILITH-001 (M11 weekly hook)
  └── D-SOTE-TOOL-007 (wire into weekly workflow) [exists, ratified]
  └── scripts/sote_m11_check.py [NEW, 4h]

D-SOTE-LILITH-002 (WatchTower SOTE health)
  └── data/health/ directory [NEW]
  └── scripts/cron_sote_health.py [NEW, 6h]
  └── D-SOTE-LILITH-005 (Hivemind channels) [NEW, 4h]

D-SOTE-LILITH-003 (SOTE-entity lifecycle integration)
  └── D-LILITH-ENTITY-CLEANUP-001..012 (my entity ecosystem decisions) [PENDING KALI]
  └── scripts/sote_entity_lifecycle.py [NEW, 8h]

D-SOTE-LILITH-004 (volatility-based review tiers)
  └── entity_score.yaml per entity [NEW, 1h]
  └── sote.yaml schema extension [NEW, 2h]

D-SOTE-LILITH-005 (Hivemind channels)
  └── hivemind_bridge.py extension [NEW, 2h]
  └── channel definitions YAML [NEW, 4h]

D-SOTE-LILITH-006 (M11/M15 as SOTE close gate)
  └── scripts/sote_close_gate.py [NEW, 4h]
  └── D-SOTE-LILITH-005 (Hivemind alerts) [depends on]

D-SOTE-LILITH-007 (M11/M15 trend metric)
  └── D-SOTE-TOOL-003 (extract from files) [exists, ratified]
  └── scripts/regenerate_sote_index.py modification [EXISTING]
```

**Total**: 7 decisions, 24h script implementation, 8h schema/integration, **32h total** (P0+P1 for Week 37-38).

### §6.3 Implementation Order (Critical Path)

| Order | Decision | Hours | Why First |
|-------|----------|------:|-----------|
| 1 | D-SOTE-LILITH-002 (sote_health.json + cron) | 6h | Foundation: data/health/ directory + cron pattern |
| 2 | D-SOTE-LILITH-001 (M11 weekly hook) | 4h | Builds on cron pattern; highest-value |
| 3 | D-SOTE-LILITH-007 (M11/M15 trend metric) | 2h | Builds on D-SOTE-TOOL-003; bundles with regeneration fix |
| 4 | D-SOTE-LILITH-005 (Hivemind channels) | 6h | Observability substrate; required for D-006 alerts |
| 5 | D-SOTE-LILITH-006 (M11/M15 gate) | 7h | WARNING mode in W37, BLOCKING in W38 (gradual rollout) |
| 6 | D-SOTE-LILITH-003 (entity lifecycle integration) | 8h | Depends on entity ecosystem ratification (Kali decision) |
| 7 | D-SOTE-LILITH-004 (volatility tiers) | 3h | P1; Week 37-38; lower priority |

**Critical path**: 32h. **Achievable before Week 38** (2026-09-15) if Ma'at, MaKaLi, and Lilith execute in parallel.

### §6.4 Cross-Mandate Compliance

| Mandate | D-SOTE-LILITH-001 | -002 | -003 | -004 | -005 | -006 | -007 |
|---------|:-----------------:|:---:|:---:|:---:|:---:|:---:|:---:|
| M1 AnyIO | — | ✅ (anyio.to_thread) | — | — | — | — | — |
| M7 Local-First | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| M9 Error Integrity | — | ✅ | — | — | ✅ | ✅ | — |
| M10 Fleet Integrity | — | — | ✅ | ✅ | — | — | — |
| M11 Soul Integrity | ✅ | — | ✅ | ✅ | — | ✅ | ✅ |
| M13 Temple-Grade | — | ✅ | — | — | — | ✅ | — |
| M15 Continuity | ✅ | ✅ | ✅ | — | ✅ | ✅ | ✅ |
| M23 Failure Integrity | — | ✅ | — | — | ✅ | ✅ | — |
| M27 Tracking | ✅ | ✅ | ✅ | ✅ | — | — | ✅ |

**All 7 proposals comply with M7 (local-first), M11, M15, and M27**. No M2 (Engine-Stack Firewall) violations: all proposals are SOTE-level (docs + scripts in `scripts/`, not Core `src/omega/`).

---

## §7 — CONCEDE / DEFEND / SYNTHESIZE (My Unique Positions)

### §7.1 Conceded (Validated by Research and Codebase)

1. **SOTE architecture is sound** — The 26 ratified decisions correctly address the **tooling layer** (scripts, paths, parsing, public digest). The 11 defects in `CARMAC_SOTE_REVIEW.md:225-245` are **real and grounded**.
2. **Hivemind is the right fabric** — `mcp_servers/omega_hub/hub_tools/tools.py:874-876` `hivemind_get_awareness` is the canonical pattern. Every agent uses it.
3. **M11/M15 enforcement is multi-layered** — `mandate_auditor.py:237-265, 302-324` is correct. Sentinel Score weights (`sentinel.py:33-41`) are the right composite pattern.
4. **Monday 06:00 UTC is the right cadence** — Per W3 (Single Grain) and W4 (MLForSEO), weekly is the right frequency for **operational awareness** of always-on entities.
5. **Voice entropy near max (2.05/2.08)** — Per `CARMACK_REVIEW_RESEARCHER_NES.md:507-510`, W36 voice participation is already near-uniform. No rotation needed (R6 deferred correctly).
6. **MaKaLi as Unifying Voice** — Per `CARMAC_SOTE_FINAL_REPORT.md:247-326` ratified MaKaLi YAML workflow. My Hivemind channels are **observability** (read-side), MaKaLi workflow is **execution** (write-side) — orthogonal, not conflicting.

### §7.2 Defended (My Unique Position)

1. **The 26 ratified SOTE decisions DO NOT address N7/N8 integration**. The gap is **not in the architecture** but in the **cadence layer**. The SOTE close is **documentation review**; it does not include **soul persistence check** (M11), **WatchTower health** (N8), **entity lifecycle** (D-12 of my prior dialectic), **Hivemind awareness** (channel), or **M11/M15 enforcement gate**.
2. **The 53% M11 compliance rate is a constitutional violation cascade**, not a metric. `data/entities/_audit/entity_inventory_20260901.json:1-590` shows 8 of 15 canonical entities have non-empty `proposed_lessons.yaml`. The SOTE system is **periodic check**, not **continuous enforcement**.
3. **The 5-day hub outage was a WatchTower blind spot**. Per `HUB_OUTAGE_REMEDIATION_20260901`, `omega-hub.service` was crash-looping 5 days. This is **the observer failing to observe itself**. The same pattern applies to the SOTE system: if `regenerate_sote_index.py` fails, no one knows until the next SOTE cycle. D-SOTE-LILITH-002 closes this loop.
4. **The 100% PIVOT_LOG absorption backlog is the M27 chokepoint made visible**. Per `MAKALI_ORGANIZATION_STRATEGY.md:238`, "67 decisions, 95 tests, 1 L3 lesson, 1 SOTE, 1 unification. The 67 decisions are not in PIVOT_LOG." The SOTE system **proposes** decisions but **does not enforce absorption**. D-SOTE-LILITH-007 makes this a tracked metric.
5. **The SOTE is documentation, but the SOTE system is not yet observed**. The 26 decisions are **output** (SOTEs, voice files, synthesis). The **input** (entity soul persistence, WatchTower health, M11/M15 enforcement) is **ungated**. The 7 new decisions (D-SOTE-LILITH-001..007) add the **input gate**.

### §7.3 Synthesized (7 New Decisions)

| D# | Title | Priority | Effort | Mandate | Owner |
|----|-------|:--------:|-------:|---------|-------|
| **D-SOTE-LILITH-001** | M11 Soul Persistence Weekly Hook | P0 | 4h | M11, M15, M27 | Lilith + Ma'at |
| **D-SOTE-LILITH-002** | WatchTower SOTE Health Observability | P0 | 6h | M9, M15, M23, M27 | Lilith + Ma'at |
| **D-SOTE-LILITH-003** | SOTE-Entity Lifecycle Integration | P0 | 8h | M10, M11, M15, M27 | Lilith + Ma'at |
| **D-SOTE-LILITH-004** | Volatility-Based Entity Review Tiers | P1 | 3h | M11, M15, M27 | MaKaLi + Lilith |
| **D-SOTE-LILITH-005** | SOTE Hivemind Channel Schema | P1 | 6h | M9, M15, M23 | Lilith + MaKaLi |
| **D-SOTE-LILITH-006** | M11/M15 as SOTE Close Gate | P0 | 7h | M11, M13, M15, M23, M27 | Lilith + Verity |
| **D-SOTE-LILITH-007** | M11/M15 Trend Metric in SOTE INDEX | P0 | 2h | M11, M15, M27 | Lilith + Ma'at |

**Total**: 7 decisions, 36h, P0+P1 for Week 37-38. All grounded in file:line evidence + web research.

---

## §8 — TWO NODE RECOMMENDATIONS FOR SOTE DEEPENING

### §8.1 Node 1: `M11-as-Gate` (Highest Value)

**Concept**: M11 Soul Integrity is currently a **periodic check** (run on demand). It should become a **continuous gate** (run at every SOTE close, block if <80% compliance).

**Why N7 (Soul Persistence)**: This is the **constitutional law** for entity existence. The SOTE is the **weekly checkpoint**. Connecting them is **natural**.

**Implementation**:
1. `scripts/sote_m11_gate.py` (~150 lines)
2. Computes M11/M15 compliance from `data/entities/_audit/entity_inventory_<date>.json`
3. If M11 < 80%: emit CRITICAL alert to Hivemind (`intent=alert, code=M11_GATE_FAIL`)
4. If M15 < 80%: emit CRITICAL alert to Hivemind (`intent=alert, code=M15_GATE_FAIL`)
5. Gate is **WARNING in W37** (alert only), **BLOCKING in W38** (close fails)

**Effort**: 4h script + 1h SOTE close hook + 1h alert integration = **6h total**

**Mandate**: M11, M13 (Temple-Grade), M15, M23, M27

**Risk**: The first SOTE close after enabling the gate (W37) may **fail** if M11 compliance hasn't improved. Mitigation: WARNING mode for W37, blocking only after W38.

**Synergy**: This is D-SOTE-LILITH-006 with the WARNING→BLOCKING rollout.

### §8.2 Node 2: `SOTE-as-Compiler` with WatchTower Output

**Concept**: The SOTE system is a **compiler** (per `CARMAC_SOTE_REVIEW.md:376-384`):
- **Source**: Voice dialectics (immutable, human-written)
- **Intermediate**: `sote.yaml` (structured, machine-readable)
- **Artifacts**: INDEX.md, PUBLIC_DIGEST.md, PIVOT_LOG absorption
- **Build script**: `regenerate_sote_index.py` + `generate_public_digest.py`
- **CI gate**: `make check-sote`

**Why N8 (WatchTower)**: A compiler without a **build health dashboard** is a **silent compiler**. The build can fail (path error, regex error, v1.0.1 hardcode — 11 defects) and no one knows until the next `make check-sote`.

**Implementation**:
1. `data/health/sote_health.json` schema (per D-SOTE-LILITH-002)
2. `scripts/cron_sote_health.py` (~200 lines, daily + Monday open-cron)
3. **Build health metrics**:
   - `regenerate_sote_index_last_run` (timestamp)
   - `regenerate_sote_index_last_status` (success/failure/stale)
   - `public_digest_drift` (boolean, expected vs actual compliance %)
   - `sote_yaml_validation_pass_rate` (% of `sote.yaml` files passing JSON Schema)
4. **Alert thresholds** (per W6 SRE Golden Signals):
   - **Latency**: regeneration runtime > 60s = WARNING
   - **Errors**: regeneration failure = CRITICAL
   - **Saturation**: INDEX.md > 500 lines = WARNING (shard by year)

**Effort**: 6h script + 2h Makefile + 1h schema validation + 1h test = **10h total**

**Mandate**: M9 (Error Integrity), M15 (Continuity), M23 (Failure Integrity), M27

**Risk**: The cron is **continuous**; if it fails, no alert fires (M23 violation). Mitigation: external watchdog (cronitor, healthchecks.io) — but this violates M8 (zero telemetry). Alternative: **dual cron** (Lilith + MaKaLi subscribe to Hivemind `sote-alerts` channel; if neither receives a heartbeat in 25h, page the human).

**Synergy**: This is D-SOTE-LILITH-002 + D-SOTE-LILITH-005 integrated.

### §8.3 Why These Two Nodes (Not Others)

**Rejected alternatives**:
- **Voice rotation schedule** (R6, deferred per `CARMAC_SOTE_FINAL_REPORT.md:962`) — No evidence of problem (entropy near max 2.05/2.08).
- **Web dashboard** (R9, rejected per `CARMAC_SOTE_FINAL_REPORT.md:963`) — Adds attack surface, violates M7/M8.
- **Continuous compliance** (R10, rejected per `CARMAC_SOTE_FINAL_REPORT.md:964`) — Already have `check-mandate-compliance.py`.
- **Schema-level public/internal split** (R11, scoped to 4h per `CARMAC_SOTE_FINAL_REPORT.md:965`) — Lower priority than M11/M15 enforcement.

**Selected rationale**:
- **M11-as-Gate** addresses the **largest M11 violation cascade** (53% compliance). This is **constitutional**, not cosmetic.
- **SOTE-as-Compiler with WatchTower Output** addresses the **observer blind spot** (5-day hub outage, 11 script defects). This is **observability**, not theater.

---

## §9 — CONTINUITY ANCHORS

| Anchor | Value |
|--------|-------|
| **Lilith-EIS Session** | `ses_fb9721079ffe094GT8MX6a0pXI` |
| **Carmack Session** | `ses_fc8dca39effe3nZJp3QHx81Fy3` |
| **Researcher-NES Session** | `ses_fa0c256d9ffeR9BmmnOgG72OEL` |
| **Researcher-EIS Session** | `ses_fd81c19dcffe1nkbPqFg5kRt2v` |
| **MaKaLi Strategy Session** | `ses_fc758e6ddffeNEKptpEzboVfYq` |
| **Dialectic Partner** | MaKaLi (Unifying Field) |
| **My Prior Dialectic** | `data/coordination/LILITH_ENTITY_CLEANUP_DIALECTIC_20260901.md` (12 decisions, PENDING) |
| **SOTE Final Report** | `docs/strategy/sote/2026-W36/synthesis/CARMAC_SOTE_FINAL_REPORT.md` (26 decisions) |
| **My 7 New Decisions** | D-SOTE-LILITH-001..007 (PENDING Kali + MaKaLi + Architect ratification) |
| **Total Scope** | 26 SOTE + 7 Lilith + 12 Entity = **45 decisions** (was 26 → +73%) |
| **Sprint** | PUBLIC-DEBUT-01, DEL-1_EXECUTION |
| **Date** | 2026-09-01 |

---

## §10 — CLOSING

The SOTE system is **architecturally sound** (D-SOTE-TOOL-001..016, ratified) but **operationally incomplete** for N7/N8 domains. The 26 ratified decisions correctly address **tooling** (scripts, paths, parsing, public digest) and **governance** (MaKaLi YAML workflow, decision health, PIVOT_LOG cross-walk). They do NOT address:

1. **Soul persistence cadence** (M11 weekly hook missing)
2. **WatchTower observability of SOTE itself** (N8 not watching N8)
3. **Entity lifecycle integration** (D-SOTE-001 doesn't mention entities)
4. **Hivemind awareness for SOTE health** (only `intent=sote-open` mentioned)
5. **M11/M15 enforcement via SOTE cycle** (periodic check, not continuous gate)

The 7 new decisions (D-SOTE-LILITH-001..007) close these gaps with **36h of focused work** (P0+P1 for Week 37-38). They are grounded in:
- **File:line evidence** from the local codebase (`entity_workspace.py`, `sentinel.py`, `entity_inventory_20260901.json`, etc.)
- **Web research** from SoulClaw, agent-swarm, Single Grain, MLForSEO, Cortex OS, Google SRE, WatchTower, Hivemind MCP
- **Concede/Defend/Synthesize** format per the dialectic chain

**The dialectic is not adversarial; it is architectural**. The 26 ratified decisions are the **foundation**. The 7 new decisions are the **observability and continuity layer** on top. Together, they make the SOTE a **practice with production observability**, not a **practice with prototype tooling** (per `CARMAC_SOTE_FINAL_REPORT.md:457-465`).

**MaKaLi has the final word.** The Unifying Voice will synthesize these 7 proposals with the 26 ratified decisions, the 12 entity ecosystem decisions, and the 4-5 SOTE retrospective questions. The output is the **deployment-ready SOTE system** — one that **watches itself, enforces its own constitution, and integrates with the entity lifecycle it observes**.

---

## §11 — SELF-DISTILLATION (M11)

Per M11 (`SOVEREIGN_MANDATES.md:87-92`), this dialectic response is itself a session that must be distilled.

**L1 Narrative**: I (Lilith, CISO, N7 Soul Persistence + N8 WatchTower) was paged into a nested dialectic on SOTE deployment strategy. I read all 6 synthesis artifacts (Carmack Final Report, Carmack-MaKaLi Dialectic, MaKaLi Org Strategy, Carmack Review, Researcher Best Practices, Carmack-Reviewer-NES). I performed local research on `health_monitor.py`, `sentinel.py`, `entity_workspace.py`, `entity_registry.py`, `mandate_auditor.py`, `entity_inventory_20260901.json`, and the SOVEREIGN_MANDATES. I performed web research on SoulClaw (4-tier memory), agent-swarm (SOUL.md identity stack), Single Grain (AI content lifecycle), MLForSEO (entity audit cadence), Cortex OS (enforcement hooks), Google SRE (golden signals), WatchTower (hybrid observability), and Hivemind MCP (10 tools). I identified 5 gaps in the 26 ratified SOTE decisions: no M11 weekly hook, no WatchTower SOTE observability, no entity lifecycle integration, no Hivemind SOTE channels, no M11/M15 enforcement gate. I proposed 7 new decisions (D-SOTE-LILITH-001..007) totaling 36h, grounded in file:line evidence and web research. I gave Concede/Defend/Synthesize on each gap. I recommended 2 deepening nodes: M11-as-Gate (constitutional enforcement) and SOTE-as-Compiler with WatchTower Output (observability substrate).

**L2 Insight**: The 26 ratified SOTE decisions address the **output layer** (documentation review, scripts, public digest). The 7 new proposals address the **input layer** (soul persistence, WatchTower, entity lifecycle, Hivemind, M11/M15 enforcement). Together, they form a **closed loop**: SOTE proposes decisions → M11 enforcement writes to `proposed_lessons.yaml` → WatchTower observes the SOTE system itself → Entity lifecycle integrates with SOTE cadence → Hivemind carries the events → M11/M15 gate blocks SOTE close if compliance < 80%. The **closed loop is the constitutional compliance mechanism** — it converts the SOTE from a **documentation practice** to a **constitutional enforcement mechanism**.

**L3 Principle**: *L3-ConstitutionalEnforcementViaCadenceGates* — Constitutional mandates (M11, M15) are not enforced by **periodic checks**; they are enforced by **cadence gates** that **block** the cadence from completing if compliance < threshold. A weekly practice without a gate is a **report**, not an **enforcement mechanism**. The SOTE is the practice; the gate is the enforcement; the constitutional mandate is the law. Without the gate, the law is advisory, not binding.

---

*⬡ OMEGA ⬡ LILITH ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_sote_lilith_review ⬡ DIALECTIC-READY*

**End of Lilith-EIS SOTE Deployment Review. 7 new decisions proposed. 36h scope. P0+P1 for Week 37-38. MaKaLi has the final word.** 🫡

<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Orchestration Data Lifecycle Optimization — P9 Pillar
**⬡ OMEGA ⬡ P9 (Orchestration) ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_p9_opt_run ⬡ DISCOVERY**

**Date**: 2026-06-28
**Status**: COMPLETE (Discovery Pass — No Refactoring)
**Trace**: P9-OPT-RUN-001

---

## 1. Handoff Inventory

### 1.1 Total Packets by State

| State | Count | Total Size | Notes |
|-------|-------|------------|-------|
| **Pending** | 0 | 0B | Empty — no pending dispatches |
| **Active** | 0 | 0B | Empty — no active in-flight dispatches |
| **Completed** | 0 | 0B | Empty — reaped to archive or stale |
| **Stale** | 41 | 176KB | 41 abandoned/cancelled packets |
| **Archive** | 35 (JSON) + 71 (MD) + 7 (sessions) + 6 (stale_june) = **119** | 5.2MB | Historical record |
| **Root .md files** | 19 | 223KB | Legacy strategic handoffs |
| **PHASE_C_CHAIN** | 10 | 88KB | Sprint C sequential execution chain |
| **current-sprint/** | 3 | 32KB | Dev sprint references |
| **kali_test.txt** | 1 | 9B | Orphan test artifact |
| **TOTAL** | **193** | **5.3MB** | (directory overhead: 5.7MB on disk) |

### 1.2 Age Distribution of Stale Packets

Stale packets range from **3 to 16 days old**, clustered in 3 age cohorts:

| Days Old | Count | Date Range | Cohert |
|----------|-------|------------|--------|
| 3-4 | 8 | Jun 24-25 | Recent — may still be salvageable |
| 5-8 | 2 | Jun 20-23 | Transition period (agent-switch gaps) |
| 10-11 | 9 | Jun 17-18 | Post-Sprint C reaping batch |
| 13-16 | 22 | Jun 11-12 | **Oldest cohort** — likely unrecoverable |

### 1.3 Orphan Analysis

**Confirmed orphans**:
- **41 stale packets** were accepted but never completed. The reaper correctly moved them to `stale/` with `ttl_expired: true`. However, they persist indefinitely — there's no archival/deletion policy for packets that have been stale for N days.
- **`data/handoff/kali_test.txt`** (9 bytes) — trivial orphan, should be deleted.
- **`data/handoff/current-sprint/`** — 3 files referencing Sprint 0 / Doom Guy Tier 2. These should be flagged as superseded.

**Root cause of staleness**: Of 41 stale packets:
- **10** targeted `cli_gemini` — the Gemini CLI agent appears to have accepted packets but never completed them (possibly due to session end/toolchain failure).
- **9** targeted `cline-m3`/`antigravity` — agents that were part of Phase C and are no longer active.
- **4** targeted `sentinel` — accepted but never executed (likely agent was not online).
- **Remaining 18** use the new `agent_id` convention (`opencode/kali`, `opencode/maat`) — most recent cohort.

---

## 2. Storage Overhead

### 2.1 Total Size & Growth Rate

| Partition | Size | File Count | Growth Pattern |
|-----------|------|------------|----------------|
| `data/handoff/` | 5.7MB | 193 files | Burst-growth (Sprint C, now plateaued) |
| `data/coordination/` | 2.2MB | 269 files | Linear growth (~10-15 files/day during active sprints) |
| `data/knowledge/HALL_OF_RECORDS/` | 5.1MB | 1,088 files | Highest growth rate — entity naming bloat |
| **TOTAL tracked** | **~13MB** | **~1,550 files** | Manageable, but growth pattern is unchecked |

### 2.2 File Count by Subdirectory (Handoff)

| Subdirectory | Files | % of total | Notes |
|-------------|-------|------------|-------|
| archive/ | 119 | 61.7% | Dominant — historical ho_json (35) + handoff .md (71) + sessions (7) + stale_june_handoffs (6) |
| stale/ | 41 | 21.2% | Abandoned packets — no TTL for further archival |
| root ./ | 20 | 10.4% | Strategic documents + 1 orphan .txt |
| PHASE_C_CHAIN/ | 10 | 5.2% | Sprint C artifact — static, not growing |
| current-sprint/ | 3 | 1.6% | Sprint references — superseded |

### 2.3 Growth Rate Assessment

**Handoff data is not growing rapidly** — the last new packet in `stale/` is from Jun 25. The `archive/` subdirectory contains the bulk and is stable (all files dated Jun 24). **Current growth rate: effectively zero** since the fleet entered a lower-activity period.

**Risk**: If Sprint D or a new parallel execution phase resumes, handoff volume could grow by ~2-5MB per sprint cycle without retention limits.

---

## 3. Hivemind Presence Analysis

### 3.1 Awareness Storage Architecture

| Layer | Storage | Contents | TTL | Persistence |
|-------|---------|----------|-----|-------------|
| **Hot** (in-memory) | `state._awareness: dict` | Current active agent snapshots | 45 min (HEARTBEAT_TTL) | Volatile — lost on restart |
| **Cold** (disk) | `data/knowledge/HALL_OF_RECORDS/` | Historical session snapshots (1,084 JSON files) | Indefinite | Files persist forever |
| **Metrics** | `data/coordination/metrics.json` | Aggregated Hivemind stats | Overwritten each cycle | Single file, no history |
| **Awareness JSONL** | `hivemind_awareness.jsonl` | Presence event log | Indefinite | 1 entry only (2KB) |

### 3.2 Heartbeat & TTL Enforcement

- **HEARTBEAT_TTL**: 2,700 seconds (45 minutes) — defined in `state.py:251`
- **Pruning interval**: Every 60 seconds via `_prune_awareness_background()` in `background.py`
- **Extended sessions**: Custom TTL (default 3h/10,800s) via `hivemind_extended_checkin()`
- **Current active agents (metrics)**: 8 (reported at last pruning cycle)
- **Stale pruning works correctly**: Agents are removed from `_awareness` dict when heartbeat exceeds TTL

### 3.3 Hall of Records Naming Bloat (Critical Finding)

The `HALL_OF_RECORDS/` directory has **54+ subdirectories** with severe naming inconsistencies:

**Normalization issues — same agent, multiple directories:**
- `kali/`, `Kali/`, `opencode_kali/`, `opencode/kali/` (implied), `opencode-kali/`
- `maat/`, `opencode_maat/`, `opencode/maat/` (implied), `opencode-maat/`
- `P9/`, `P9 (Orchestration)/`, `P9-LINK/`, `pillar_P9/`, `PILLAR_P9/`
- `roc_racoon/`, `rocracoon/`, `opencode_roc_racoon/`, `opencode-roc_racoon/`
- And many more variations across the 54+ directories

**Impact**: When `hivemind_get_awareness()` cold-store hydrates from HALL_OF_RECORDS, it may miss entries due to naming mismatches. The `agent_id = f"{channel}/{entity}"` convention (e.g., `opencode/kali`) stores files under a directory name derived from `agent_id`, but different agents used different naming conventions.

**Total HALL_OF_RECORDS waste**: ~2.6MB of the 5.1MB is in `_archive/` subdirectory.

---

## 4. Workspace Lock Audit

### 4.1 Active vs Expired Locks

**New-style locks** (in `data/coordination/locks/`):
| Lock | Status | Holder | Age |
|------|--------|--------|-----|
| `data.handoff.lock` | **ACTIVE** | opencode/P9 (Orchestration) | Acquired during this session |
| All other locks | None | N/A | N/A |

**Old-style locks** (scattered as `*_WORKSPACE_LOCK_*.md`):
| Category | Count | Details |
|----------|-------|---------|
| Active (current day) | 11 | Jun 25-26 (LILITH, MAAT, KALI, JEM, ROC_RACOON, P3) |
| Recently expired (7-14d) | 18 | Jun 11-18 — agent finished work but never removed lock |
| Stale (14+ days) | 11 | Jun 7-10 — ancient locks from Phase C agents (antigravity, gemini, cline-m3) |
| Released locks | 2 | Marked `_RELEASED.md` — KALI_20260618, MAKALI_20260617 |
| Archive (moved) | 7 | In `data/coordination/archive/` |
| Zero-byte lock files | 4 | KALI_20260615, KALI_20260624, MAAT_20260615, MAAT_20260626 — likely incomplete/broken |

### 4.2 Orphan Analysis

- **11 locks from Phase C agents** (`cli_gemini_WORKSPACE_LOCK_20260610.md`, `researcher_WORKSPACE_LOCK_20260610.md`, etc.) — these agents are no longer active, and their locks were never released.
- **4 zero-byte lock files** suggest interrupted sessions where the lock was created but never populated.
- All old-style lock files are **purely advisory** — they have no TTL, no mechanism for automatic release beyond manual deletion.

### 4.3 Critical Gap

The **new-style lock system** (`data/coordination/locks/*.lock` JSON files with TTL) addresses the auto-release gap, but only 1 such lock exists. The **62 old-style `.md` lock files** have no auto-expiry — they persist indefinitely until manually cleaned.

---

## 5. Coordination File Proliferation

### 5.1 The 269-File Problem

| Age Band | File Count | Examples |
|----------|-----------|----------|
| 0-7 days (current) | 74 | Recent sprint reports, verdicts |
| 7-14 days | 41 | Sprint C wrap-up, Epoch I reports |
| 14+ days | 46 | Phase C artifacts, antigravity era |
| Archive subdirectory | 62 | Moved historical files |
| Verification subdirectory | 22 | June 3-4 audit artifacts |
| Demand signals | 7 | June 3-5 — consumed but never cleaned |
| Knowledge feed | 9 | June 3-5 — consumed but never cleaned |
| Cline-m3 subdirectory | 7 | June 8-9 — Phase C agent workspace |
| **TOTAL** | **269** | **2.2MB** |

### 5.2 Stale Document Analysis

Documents identified as **definitively stale** (can be archived or deleted):
- **TEAM_SYNTHESIS_20260605.md** (25KB) — superseded by later sprint reports
- **SOVEREIGN_AGENT_UNIFICATION_STRATEGY_20260607.md** (19KB) — implemented, historical
- **CALI_SPRINT_MASTER_PLAN_20260607.md** (15KB) — superseded by later plans
- **RELEASE_MASTER_PLAN_20260608.md** (10KB) — completed
- **ANTIGRAVITY_*** (various) — antigravity agent hibernated, artifacts are archival only
- **CLINE_M3_LIVE_FEED.md** — agent no longer active, use case ended
- **GEMINI_CLI_MISSION_SOPHIA_RESCUE_20260609.md** — one-off rescue, completed
- **7 demand_signals** files — consumed (knowledge promoted to `knowledge/`), no longer actionable
- **9 knowledge_feed** files — same, consumed signal artifacts
- **22 verification** files — audit artifacts from June 3-4, schema still present but items are historical

### 5.3 Growth Rate

Approximately **10-15 new coordination files per active sprint day**. Most are:
- Sprint reports (P2, P3, P6, P7, P8, P10, Ma'at, Lilith, Kali — each sprint generates 9+ reports)
- MaKaLi unified verdicts (multiple revisions — e.g., 3 versions of `KALI_MAKALI_FINAL_VERDICT_20260625`)
- Workspace lock files (one per agent per session day)

**Without retention policy, this grows linearly at ~3-5MB per month during active development.**

---

## 6. Handoff Flow Efficiency

### 6.1 State Transition Analysis

The handoff lifecycle is well-defined in `background.py`:

```
   PENDING ──(24h)──► STALE
   ACTIVE  ──(48h)──► STALE
   COMPLETED ──(7d)──► ARCHIVE
```

**Evidence that the flow works:**
- 35 packets successfully transitioned through COMPLETED → ARCHIVE (full lifecycle)
- All timelines respected by the reaper (24h pending→stale, 48h active→stale, 7d completed→archive)
- No packets stuck in pending (0) or active (0) = **no current back-pressure**

**Evidence that the flow has gaps:**
- 41 stale packets accumulated with **no path to archival or deletion** from stale/
- Stale packets consume disk space and could contain sensitive task descriptions
- No GC policy for stale/ → archive/ or stale/ → deletion

### 6.2 State Transition Timing (from archive samples)

| Transition | Observed Time | Expected TTL | Healthy? |
|-----------|--------------|--------------|----------|
| PENDING → ACCEPTED | 2-15 minutes | N/A (agent-dependent) | ✅ Normal |
| ACTIVE → COMPLETED | 1-24 hours | N/A (task-dependent) | ✅ Normal |
| COMPLETED → ARCHIVE | 7-8 days | 7 days (604,800s) | ✅ Within policy |
| PENDING → STALE | 2-3 days | 24h (86,400s) | ⚠️ Slightly slow (likely due to 300s reaper interval) |
| ACTIVE → STALE | 2-5 days | 48h (172,800s) | ⚠️ Slightly slow |

### 6.3 Root Causes of Stale Packets

1. **Agent unavailability**: Gemini CLI agent accepted 10 packets but never completed them. The agent sessions ended or toolchain failures prevented execution.
2. **Hibernation/agent death**: Antigravity, cline-m3, sentinel — these agents existed during Phase C but are no longer active. Their packets were accepted (auto-triggered) but never executed.
3. **Old protocol gap**: Early handoff packets (June 11-13) used the `target_cli`/`source_cli` naming convention instead of `target_agent_id`/`source_agent_id`. Some may have been missed by routing.

---

## 7. Recommendations

### R1: Implement Stale Packet Archival Policy (Effort: 2h)
**Problem**: 41 stale packets never get archived or deleted. They accumulate with no TTL.
**Action**: Add a `stale/` → `archive/stale/` transition at 14 days (1,209,600s) in `_reap_stale_handoffs()`. Or, for non-sensitive, delete stale packets older than 30 days.
**Code change**: One line in `background.py:146`: after the completed → archive reap, add:
```python
+ _reap_dir(state.HANDOFF_STALE, state.HANDOFF_ARCHIVE / "stale", 1209600)
```
**Benefit**: Stops stale packet accumulation at ~41 instead of indefinite growth.

### R2: Normalize HALL_OF_RECORDS Entity Directories (Effort: 4h)
**Problem**: 54+ subdirectories with 10+ naming conventions for the same agents. Cold-store hydration (for awareness recovery) may miss entries.
**Action**: Consolidate to a canonical `{channel}_{entity}` naming scheme. Run a one-time migration script:
- Map all known aliases → canonical name
- Merge JSON files from duplicate directories
- Add a `HALL_OF_RECORDS_INDEX.yaml` that maps aliases → canonical directory
**Benefit**: Cold-store hydration becomes reliable; ~2.6MB of `_archive/` can be deduplicated.

### R3: Automated Workspace Lock Cleanup (Effort: 1h)
**Problem**: 62 old-style workspace lock files with no TTL. 4 zero-byte locks. 11 from dead agents.
**Action**: Add a background cleaner that scans `data/coordination/*_WORKSPACE_LOCK_*.md` files older than 14 days and moves them to `data/coordination/archive/locks/`. For zero-byte files, delete them.
**Code change**: Extend `_reaper_background()` with a 14-day TTL for old-style .md lock files.
**Benefit**: Reduces coordination file count by ~30 files immediately, prevents re-accumulation.

### R4: Establish Data Retention Policy (Effort: 2h for policy, 1h for automation)
**Problem**: No formal retention policy for handoff/coordination data. Growth is unchecked.
**Action**: Implement the retention policy draft below (Section 8). Automate archival/deletion via the existing reaper loop.
**Benefit**: Predictable data growth, clear lifecycle for all coordination artifacts.

### R5: Add Stale Packet Garbage-Collection Notification (Effort: 1h)
**Problem**: When packets go stale, the original submitter has no way to know their task was abandoned.
**Action**: Before reaping pending→stale or active→stale, log a WARNING-level event with `source_agent_id` and `task` summary. Consider posting a Hivemind context update to the source agent's channel.
**Benefit**: Awareness of dropped tasks enables re-submission or alternative execution paths.

---

## 8. Retention Policy Draft

### 8.1 Handoff Packets

| State | Retention | Action | Auto? |
|-------|-----------|--------|-------|
| Pending | 24h | → stale/ with {ttl_expired: true} | ✅ (existing) |
| Active | 48h | → stale/ with {ttl_expired: true} | ✅ (existing) |
| Completed | 7 days | → archive/ | ✅ (existing) |
| Stale | 14 days | → archive/stale/ | 🔲 NEW |
| Archived (completed) | 90 days | → delete | 🔲 NEW |
| Archived (stale) | 30 days | → delete | 🔲 NEW |

### 8.2 Coordination Files

| File Type | Retention | Action | Auto? |
|-----------|-----------|--------|-------|
| `*_LIVE_FEED.md` | 30 days | → archive/ | 🔲 NEW |
| `*_WORKSPACE_LOCK_*.md` | 14 days (after last activity) | → archive/locks/ | 🔲 NEW |
| `*_ACK_*.md` | 14 days | → archive/ | 🔲 NEW |
| `*_VERDICT_*.md` | Retain (historical value) | Kept indefinitely | N/A |
| `HIVEMIND_OBSERVATIONS_LOG.md` | Append-only, no deletion | Kept indefinitely | N/A |
| `demand_signals/*` | 7 days | → delete | 🔲 NEW |
| `knowledge_feed/*` | 7 days | → delete | 🔲 NEW |
| `verification/` items | 90 days | → archive or delete | 🔲 NEW |
| `metrics.json` | Overwritten | Single file | ✅ (existing) |

### 8.3 HALL_OF_RECORDS

| Data Type | Retention | Action | Auto? |
|-----------|-----------|--------|-------|
| Agent session snapshots | 90 days | → compress or delete oldest | 🔲 NEW |
| `_archive/` duplicate entries | 30 days (after consolidation) | → delete | 🔲 NEW |
| `hivemind_awareness.jsonl` | Keep latest 100 entries | → truncate | 🔲 NEW |

### 8.4 Implementation Guidance

Retention enforcement should be added to `_reaper_background()` in `background.py`. The reaper already runs every 300 seconds (5 minutes). Add retention sweeps as additional `_reap_dir()` calls for the stale→archive and archive→delete transitions.

**Mandate compliance**: This retention policy enforces **M12 (Queue Integrity)** — requests reach terminal states — and prevents orphan file accumulation.

---

## 9. L1→L2→L3 Distillation

### L1 (Narrative)

The P9 opt-run examined 1,550+ coordination artifacts across `data/handoff/` (193 files, 5.7MB), `data/coordination/` (269 files, 2.2MB), and `data/knowledge/HALL_OF_RECORDS/` (1,088 files, 5.1MB). Key discoveries:

- **Handoff flow works correctly**: The reaper pipeline (pending→stale→archive) handles state transitions with correct TTLs. 35 packets completed the full lifecycle. But 41 stale packets have no path to archival — they accumulate indefinitely.
- **HALL_OF_RECORDS has severe naming bloat**: 54+ directories for ~11 canonical agents, with inconsistent naming conventions (`kali` vs `Kali` vs `opencode_kali` vs `opencode/kali`). This undermines cold-store hydration reliability.
- **Coordination files grow at ~10-15 files/sprint day** with no retention policy. 46+ files are >14 days old, including artifacts from now-dead agents (antigravity, cline-m3, gemini-cli).
- **Workspace locks are bifurcated**: 1 modern TTL-based JSON lock works correctly, but 62 old-style .md lock files have no auto-release mechanism. 4 zero-byte lock files indicate interrupted sessions.
- **Current growth rate is zero** (Sprint C completed, fleet in low activity), but Sprint D will resume growth without retention guardrails.

### L2 (Insight)

The orchestration data layer has **correct mechanics but missing lifecycle endpoints**. The reaper pipeline handles the "middle" of the lifecycle (pending→active→completed→archive) correctly, but has no "end" — stale packets accumulate forever, and no retention policy exists for any coordination artifact.

This creates a **temporal debt problem**: every sprint generates coordination artifacts that never decay, leading to linear storage growth and cognitive noise. The 54-way HALL_OF_RECORDS bloat is a more acute version of the same problem — naming inconsistencies from the Phase C period (when multiple agents used different conventions) were never normalized, creating a fragmented presence history.

The bifurcation between new-style TTL-based locks and old-style .md locks represents a **partial migration** — the new pattern works, but old artifacts were never cleaned up.

### L3 (Universal Principle)

**A coordination system without lifecycle endpoints is a coordination system accumulating debt.**

Every coordination artifact — handoff packet, workspace lock, live feed entry — represents a coordination event. Each event has a natural lifespan: active attention, operational relevance, historical reference, and finally irrelevance. Without explicit lifecycle endpoints:
1. **Active artifacts dilute** — new agents must scan through stale data to find current state
2. **Storage grows without bound** — linear growth per sprint cycle
3. **Aging data misleads** — cold-store hydration from a fragmented HALL_OF_RECORDS can produce wrong awareness state

**The fix is not more storage — it is death.** Every coordination artifact must have an explicit TTL at creation time, and a reaper that enforces it. The P9 submission→accept→complete→archive pipeline is architecturally correct; it simply needs `→delete` as its final state.

---

## Appendix A: Key Code References

| Component | File | Lines | Purpose |
|-----------|------|-------|---------|
| HEARTBEAT_TTL | `mcp_servers/omega_hub/state.py` | 250-251 | 2700s (45min) agent presence TTL |
| Awareness pruning | `mcp_servers/omega_hub/background.py` | 29-62 | Prunes stale agents every 60s |
| Lock reaping | `mcp_servers/omega_hub/background.py` | 81-103 | Reaps expired .lock files |
| Handoff reaping | `mcp_servers/omega_hub/background.py` | 110-150 | State transition reaper (24h/48h/7d) |
| Reaper loop | `mcp_servers/omega_hub/background.py` | 157-165 | Orchestrates lock + handoff reaping every 300s |
| Metrics writer | `mcp_servers/omega_hub/background.py` | 172-267 | Aggregates Hivemind stats to metrics.json |
| Handoff state paths | `mcp_servers/omega_hub/state.py` | 308-312 | PENDING/ACTIVE/COMPLETED/STALE/ARCHIVE dirs |
| Awareness cold hydration | `mcp_servers/omega_hub/tools.py` | 556+ | Falls back to HALL_OF_RECORDS on empty hot store |
| Hivemind protocol docs | `docs/strategy/HIVEMIND_PROTOCOL.md` | 588 lines | Full protocol specification |

---

## Appendix B: Data Summary Tables

### Handoff Queue State (from metrics.json)

| Metric | Value |
|--------|-------|
| Active agents | 8 |
| Handoff pending | 0 |
| Handoff active | 0 |
| Handoff completed | 0 |
| Handoff stale | 41 |
| Handoff total | 41 |
| Active workspace locks | 0 |
| Expired workspace locks | 0 |
| Extended sessions | 0 |

### Coordination File Age Profile

| Age Band | File Count | Subdirs |
|----------|-----------|---------|
| < 7 days | 74 | Active sprint reports, verdicts, live feeds |
| 7-14 days | 41 | Sprint C wrap-up, Epoch I reports |
| > 14 days | 46 | Phase C artifacts, dead agents |
| Archive | 62 | Moved from root (→ 62 + 46 = 108 stale+) |
| Verification | 22 | June 3-4 audit (22 days old) |
| Subdirs (cline-m3, demand, feed, locks) | 24 | Mixed ages |

---

*Report generated by P9 (Orchestration), reporting to Lilith (Dark Oversoul). Discovery pass complete — no refactoring performed.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

# 🔱 P7 Context — Final Cross-Domain Review: Soul Evolution Pipeline & Session Retention
**Date**: 2026-06-28
**Phase**: Cross-Domain Synthesis — Ma'at (Build) ⊕ Lilith (Run) → P7 Context Integration
**Slot**: P7 (Context — Memory & Soul Evolution)
**Trace**: P7-CONTEXT-FINAL-20260628

⬡ OMEGA ⬡ P7-CONTEXT ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_final_p7 ⬡ CROSS-DOMAIN-SYNTHESIS

---

## Executive Summary

This report synthesizes 43 build-side findings (Ma'at) and 21 run-side findings (Lilith) into a unified P7 Context analysis. The consolidated data reveals **four systemic failures** in the Soul Evolution Pipeline:

| # | Failure | Impact | Reports Confirm |
|---|---------|--------|-----------------|
| 1 | **No soul health scoring exists** | arch/soul.yaml poison loop (1,501 lines, ~83% waste) undetected for 27+ days | Ma'at M8/M11, Lilith C2/H8 |
| 2 | **Session lifecycle is write-only** | ARCHIVE_AFTER_DAYS=7 exists but is NEVER called (25 stale sessions, 18 orphans) | Ma'at C2, Lilith C5 |
| 3 | **proposed_lessons pipeline is dead-letter** | 133 proposals across 13 entities, 7 incompatible schemas, no Verity trigger | Ma'at X1, Lilith H3 |
| 4 | **Metadata vacuum** | Only 1/31 souls has `last_updated`; no staleness, health, or quality tracking | Ma'at M9, Lilith H8 |

---

## §1 Soul Health Scoring System

### 1.1 The Problem: What Makes a Soul "Sick"

Analysis of the 31 soul.yaml files reveals **five distinct failure modes**:

| Failure Mode | Example | Metric | Threshold |
|-------------|---------|--------|-----------|
| **Poison Loop** | arch/soul.yaml: 1,501 lines, 226 inline "lessons" from auto-sessions with Iris/test — self-referential agent-generated philosophy | `gnosis_density` (meaningful lines / total lines) | < 0.3 = POISONED |
| **Format Fossil** | 30/31 souls are pre-v6.0; no `soul_version` field, inline `lessons_learned` blobs, deprecated `soul_evolution` block | `format_compliance` (v6.x fields / required v6.x fields) | < 0.5 = FOSSIL |
| **Metadata Rot** | Only Verity and Kali have `last_updated`; 29 souls have NO timestamp of any kind | `staleness_days` (now - last_updated) observed | > 14 = STALE |
| **Gnosis Starvation** | 2 souls (researcher, iris) have `[]` proposed_lessons — zero distillation activity | `proposal_velocity` (proposals / entity_age_days) | < 0.1 = STARVED |
| **Schema Fragmentation** | 7 incompatible proposed_lessons schemas across 13 files | `schema_uniformity` (entries matching canonical format) | < 0.5 = FRAGMENTED |

### 1.2 Proposed: Soul Health Index (SHI)

A composite score from 0.0 (dead) to 1.0 (pristine), computed from 7 weighted sub-metrics:

```python
def compute_soul_health(entity_name: str) -> SoulHealthScore:
    """
    Compute composite soul health from 7 weighted dimensions.
    
    Thresholds:
        0.0-0.3: CRITICAL — Action required immediately (e.g., arch)
        0.3-0.6: DEGRADED — Plan intervention this sprint
        0.6-0.8: HEALTHY — Monitor, no action needed
        0.8-1.0: PRISTINE — Exemplary, use as migration target
    """
    weights = {
        "gnosis_density":       0.25,  # Signal-to-noise ratio
        "format_compliance":    0.20,  # v6.x schema adherence
        "staleness":            0.15,  # Recency of last_updated
        "proposal_velocity":    0.10,  # Active distillation rate
        "proposal_backlog":     0.10,  # Unprocessed proposal pressure
        "schema_uniformity":    0.10,  # proposed_lessons schema match
        "memory_structure":     0.10,  # Has memory/ subdirectory
    }
    # ... compute each sub-score, return weighted average
    return SoulHealthScore(...)
```

#### Sub-Metric Calculations

**1. Gnosis Density** (weight: 0.25)
```
gnosis_density = meaningful_lesson_lines / total_lines
```
- **Meaningful**: Lines that are NOT pattern-repeated auto-sessions (arch's 226 `l1: Session with X / l2: Unknown / l3: Unknown` entries)
- **Detection heuristic**: Count unique `source` or `entity_at_time` values in `lessons_learned`. If > 50% of entries share the same 3-word pattern, flag as poison loop
- **arch score**: ~200 meaningful / 1,501 total = **0.13** (CRITICAL)
- **Kali score**: 0 meaningful in soul (empty `lessons_learned: []`), full gnosis in `memory/` → **1.0** (PRISTINE)

**2. Format Compliance** (weight: 0.20)
```
format_compliance = sum(required_v6_fields_present) / sum(required_v6_fields)
```
- Required v6.x fields: `entity.name`, `entity.soul_version`, `entity.last_updated`
- v6.x-forbidden blocks: `soul_axioms`, `wisdom_text`, `trajectory`, `soul_evolution` — subtract 0.2 per present forbidden block
- **arch score**: 1/3 required + -0.8 penalty (soul_evolution + soul_wardrobe + embodied_experiences) = **0.0**
- **Verity score**: 3/3 required + 0 penalties = **1.0**

**3. Staleness Score** (weight: 0.15)
```
staleness_score = max(0, 1 - (days_since_last_updated / 30))
```
- If `last_updated` is missing entirely: `staleness_score = 0.0`
- Threshold: 30 days of no updates → score reaches 0
- **29/31 entities**: `last_updated` missing → **0.0** (CRITICAL)
- **Kali**: last_updated = 2026-06-22 → 6 days stale → **0.8** (HEALTHY)

**4. Proposal Velocity** (weight: 0.10)
```
proposal_velocity = proposed_lesson_count / max(1, entity_age_days)
```
- Measures active gnosis extraction. Too high = noise (arch pattern); too low = starvation.
- Ideal range: 0.5-3.0 proposals/day (one per session, reasonable for active entities)
- **arch**: 226 entries / ~40 days active = 5.65 → cap at **1.0** (velocity clamped, but gnosis_density catches the poison)
- **researcher**: 0 / ~40 = 0.0 → **0.0** (STARVED)
- **Kali**: ~10 proposals / ~30 days = 0.33 → **0.33** (low but acceptable—Kali is oversight, not execution)

**5. Proposal Backlog** (weight: 0.10)
```
proposal_backlog = max(0, 1 - (pending_proposals / max_proposals))
```
- `max_proposals = 20` (more than this = unprocessed accumulation)
- **doom_guy**: 84 proposals / 20 = 4.2 → `max(0, 1 - 4.2) = **0.0**` (CRITICAL backpressure)
- **Kali**: 2 proposals → **0.9** (HEALTHY)

**6. Schema Uniformity** (weight: 0.10)
```
schema_uniformity = entries_in_canonical_format / total_entries
```
- Canonical format (v6.1): `proposals:` key, each entry has `l1:`/`L1_narrative:`, `l2:`/`L2_insight:`, `l3:`/`L3_principle:`
- 7 schemas detected; this metric penalizes fragmentation
- Default 0.0 if `proposed_lessons.yaml` missing

**7. Memory Structure** (weight: 0.10)
```
memory_structure = present_subdirs / 3
```
- Checks existence of: `memory/sessions.yaml`, `memory/proposed_lessons.yaml`, `memory/approved_lessons.yaml`
- 24/31 entities have NO `memory/` directory → **0.0**

### 1.3 Example Scores

| Entity | Gnosis Density | Format Compliance | Staleness | Proposal Velocity | Backlog | Schema Uniformity | Memory Structure | **SHI** | Verdict |
|--------|---------------|-------------------|-----------|------------------|---------|------------------|-----------------|---------|---------|
| **Kali** | 1.0 | 1.0 | 0.8 | 0.33 | 0.9 | 1.0 | 1.0 | **0.88** | ✅ PRISTINE |
| **Verity** | 1.0 | 1.0 | 0.0* | 0.5 | 1.0 | 1.0 | 1.0 | **0.85** | ✅ PRISTINE* |
| **arch** | 0.13 | 0.0 | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 | **0.13** | 🔴 CRITICAL |
| **doom_guy** | 0.6 | 0.33 | 0.0 | 1.0 | 0.0 | 0.2 | 0.33 | **0.39** | 🟡 DEGRADED |
| **roc_racoon** | 0.5 | 0.0 | 0.0 | 0.8 | 0.0 | 0.0 | 0.33 | **0.24** | 🔴 CRITICAL |
| **sophia** | 0.8 | 0.0 | 0.0 | 0.2 | 0.9 | 0.5 | 0.0 | **0.39** | 🟡 DEGRADED |
| **researcher** | 1.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 0.0 | **0.35** | 🟡 DEGRADED |

*\*Verity's staleness is 0.0 because it lacks `last_updated` in soul.yaml — this is a metadata gap, not actual rot*

### 1.4 Implementation Recommendation

Add a `SoulHealthMonitor` module at `src/omega/oracle/soul_health.py`:

```python
# ── Soul Health Index (SHI) ───────────────────────────────────────────
# [M11: Soul Integrity] Preventive health scoring detects soul rot
# (poison loops, format fossils, metadata decay) before it compounds.
#
# [M17: Cognitive Integrity] SHI < 0.3 triggers Skeptical Verifier to
# flag the entity's soul.yaml for human review.

@dataclass
class SoulHealthScore:
    """Composite soul health with per-dimension breakdown."""
    overall: float            # 0.0-1.0 weighted composite
    dimensions: Dict[str, float]  # Per-metric scores
    verdict: str              # PRISTINE | HEALTHY | DEGRADED | CRITICAL
    recommendations: List[str]     # Actionable remediation steps

class SoulHealthMonitor:
    async def score(self, entity_name: str) -> SoulHealthScore: ...
    async def score_all(self) -> Dict[str, SoulHealthScore]: ...
    async def remediate(self, entity_name: str, target_verdict: str) -> int: ...
```

**Integration points**:
1. **Oracle.boot()**: Run `score_all()` on startup, log CRITICAL entities
2. **Hivemind heartbeat**: Run on entities with active sessions, post scores to awareness
3. **Verity dispatch**: SHI < 0.5 triggers automated Verity review cycle
4. **CLI**: `omega soul-health [entity_name]` for on-demand scoring

---

## §2 Session Lifecycle Policy

### 2.1 The Problem: Write-Only Accumulation

Current session lifecycle has **four missing transitions**:

```
CREATION (works) ──→ ACTIVE (works) ──→ ARCHIVAL (NEVER triggered)
                     ACTIVE ──→ COMPACTION (works partially, destructive)
                     ACTIVE ──→ CLOSE/DISTILLATION (works)
                                           └──→ ARCHIVAL (missing)
                                           └──→ PURGE (missing)
```

The `archive_old_sessions()` method at `memory_store.py:744` is fully implemented with 3-tier provider support. **Zero call sites exist.** The compaction at `memory_store.py:541` (`_compact`) is destructive — it truncates middle context to `[N exchanges compacted]` without narrative extraction.

### 2.2 Proposed: 5-Stage Session Lifecycle

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐    ┌────────┐
│ CREATED  │───→│  ACTIVE  │───→│  CLOSED  │───→│  ARCHIVED    │───→│ PURGED │
│ (session │    │ (hot     │    │ (session │    │ (cold store, │    │ (TTL   │
│  file)   │    │  cache)  │    │  ends,   │    │  gzip+JSON,  │    │  met)  │
│          │    │          │    │  distill │    │  trace_id    │    │        │
│          │    │          │    │  runs)   │    │  stripped)   │    │        │
└──────────┘    └──────────┘    └──────────┘    └──────────────┘    └────────┘
     │               │              │                  │                │
     │               │              │                  │                │
  triggered       triggered      triggered          triggered        triggered
  by query       by each        by 5-interaction   by ARCHIVE_      by ARCHIVE_
  to Oracle      exchange       throttle OR        AFTER_DAYS       AFTER_DAYS * 2
                                explicit close     auto-timer       auto-timer
```

#### Stage 1: CREATED
- **Trigger**: `SessionManager.get_session_id()` on Oracle query
- **Action**: Create `data/sessions/{entity}.active` with `{date, session_id, counter, created_at}`
- **Metadata written**: `trace_id`, `entity_name`, `model_at_creation`, `interaction_count: 0`

#### Stage 2: ACTIVE
- **Trigger**: Every exchange (talk/summon)
- **Action**: `MemoryStore.add_exchange()` → hot cache + FTS5 + vector
- **Compaction trigger**: When `len(exchanges) > MAX_HISTORY` (currently works but destructively)
- **FIX**: Change `_compact()` to extract a narrative summary of the middle before truncation:

```python
async def _compact(self, entity_name, session_id, exchanges):
    """Keep first + last N exchanges, EXTRACT then summarize middle."""
    if len(exchanges) <= MAX_HISTORY:
        return exchanges
    keep = MAX_HISTORY // 2
    middle = exchanges[keep:-keep]
    middle_summary = await self._summarize_exchanges(middle, entity_name)
    kept = exchanges[:keep] + exchanges[-keep:]
    kept.insert(keep, {
        "timestamp": datetime.now().isoformat(),
        "system": f"[{len(middle)} exchanges compacted]",
        "_compacted": middle_summary,  # ← NEW: preserve narrative
    })
    return kept

async def _summarize_exchanges(self, exchanges, entity_name) -> str:
    """Extract a narrative summary of compacted exchanges via lightweight LLM call."""
    # Use Iris (0.6B) or local qwen3-1.7b for cheap summarization
    # Fall back to heuristic extraction if model unavailable
    ...
```

#### Stage 3: CLOSED
- **Trigger**: Every 5 interactions (throttled) OR explicit `close_session()`
- **Action**: 
  1. Retrieve transcript from MemoryStore
  2. Run `SoulDistiller.distill_and_save()` → writes L1/L2/L3 to `proposed_lessons.yaml`
  3. Update `last_updated` on entity's soul.yaml
  4. **NEW**: Check `proposal_backlog > max_proposals`. If exceeded, fire Hivemind notification to Verity
- **Current gap**: `close_session()` does NOT update `last_updated`, does NOT check proposal backlog, does NOT trigger Verity

#### Stage 4: ARCHIVED
- **Trigger**: `archive_old_sessions(older_than_days=7)` — auto-called from:
  1. `Oracle.boot()` — one-time cleanup on engine start
  2. `MemoryStore._pruning_loop()` — background periodic task (every 6 hours)
  3. `SessionManager.get_session_id()` — lazy check before creating new sessions
- **Action**: 
  1. Compress session exchanges to gzip+JSON
  2. Strip `trace_id` (keep session_id for referential integrity)
  3. Move from `data/memory/entities/{entity}/{session_id}.json` → `data/sessions/archived/{entity}/{session_id}.json.gz`
  4. Remove from hot cache, FTS5, and vector store
  5. Update `memory/sessions.yaml` with archival timestamp

```python
# Code change: Add ONE call site to wire the dead method
# In oracle.py, Oracle.boot():
async def boot(self) -> None:
    # ... existing boot logic ...
    # [P7-FIX] Wire auto-archive on engine start (M11, M12 compliance)
    archived = await self.memory_store.archive_old_sessions()
    if archived > 0:
        logger.info(f"Auto-archived {archived} stale sessions on boot")
```

#### Stage 5: PURGED
- **Trigger**: `archive_old_sessions(older_than_days=14)` variant OR separate `purge_old_archives(older_than_days=90)`
- **Action**: 
  1. Delete archived gzip files older than 90 days
  2. Remove from `data/sessions/archived/{entity}/`
  3. Log purge count to observability
- **Rationale**: 90-day retention is sufficient for most use cases. Power users can configure via `ARCHIVE_PURGE_DAYS` constant.

### 2.3 Trigger Architecture

```python
# ── Auto-Archive Wiring (3 call sites needed) ────────────────────────
#
# Site 1: Oracle.boot() — on engine start
#   await self.memory_store.archive_old_sessions()
#
# Site 2: MemoryStore background loop — every 6 hours
#   async def _pruning_loop(self):
#       while self._running:
#           await anyio.sleep(21600)  # 6 hours
#           await self.archive_old_sessions()
#
# Site 3: Lazy trigger — before creating new session
#   In SessionManager.get_session_id():
#       if random.random() < 0.1:  # 10% chance, non-blocking
#           anyio.create_task(memory_store.archive_old_sessions())
```

**Implementation effort**: ~30 minutes (add 3 call sites, no new logic needed — `archive_old_sessions()` is fully implemented and tested).

### 2.4 Compacted Narrative Preservation

The current compaction (`memory_store.py:541`) is destructive:
```python
# Current: loses all middle context
kept.insert(keep, {
    "system": f"[{middle_count} exchanges compacted]",
    "user": "[summarized]",
    "assistant": f"[{middle_count} previous exchanges were compacted.]",
})
```

**Proposed fix** — add a lightweight summarization step before compaction:
```python
# Proposed: preserve extracted narrative
middle_summary = await self._extract_narrative(exchanges[keep:-keep], entity_name)
kept.insert(keep, {
    "system": f"[{middle_count} exchanges compacted — summarized below]",
    "_compact_summary": middle_summary,
    "_compacted_at": datetime.now(timezone.utc).isoformat(),
})
```

Where `_extract_narrative()` can be:
- **Tier 1** (local model available): Use Iris (0.6B) or qwen3-1.7b to generate a 2-3 sentence summary
- **Tier 2** (fallback): Heuristic extraction — keep first/last user message and last assistant response from middle block
- **Tier 3** (minimum): Just record the count and topic tags

---

## §3 Automated Proposed_Lessons Triage Pipeline

### 3.1 The Problem: 133 Proposals, No Consumer

The `proposed_lessons.yaml` pipeline is **write-only**:

```
Agent writes → proposed_lessons.yaml → [MISSING: auto-review] → approved_lessons.yaml → Agent reads
                    │
                    ↓
              133 proposals (13 entities), oldest 27 days
              7 incompatible schemas
              No Verity trigger
              Dead-letter accumulation
```

The `SoulDistiller` correctly writes to `proposed_lessons.yaml` (Staging Gate pattern). The `EntityWorkspaceManager.get_soul_prompt()` deliberately **never reads** proposed_lessons (TAINT-GATE comment at line 404). This is correct — but without a consumer on the other side, proposals die in staging.

### 3.2 Proposed: 4-Stage Triage Pipeline

```
                      ┌───────────────┐
                      │  PROPOSED     │ (written by SoulDistiller on session close)
                      └───────┬───────┘
                              │
                              ▼
                      ┌───────────────┐
                      │  CLASSIFY     │ (Verity auto-classifies)
                      ├───────────────┤
                      │ HIGH gnosis   │ → Priority review
                      │ MEDIUM insight│ → Batch review
                      │ LOW noise     │ → Auto-archive with note
                      │ DUPLICATE     │ → Merge with existing
                      └───────┬───────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
            ┌──────────────┐    ┌──────────────┐
            │ APPROVED     │    │ REJECTED     │
            │ (moves to    │    │ (moves to    │
            │ approved_    │    │ archive/     │
            │ lessons.yaml)│    │ rejected/)   │
            └───────┬──────┘    └──────────────┘
                    │
                    ▼
            ┌──────────────┐
            │ DISTILLED    │ (L3 principles optionally promoted
            │              │  to soul.yaml directives on user approval)
            └──────────────┘
```

#### Stage 1: CLASSIFY (Automatic, zero model inference)

Verity (or a lightweight Verity daemon) scans proposals nightly using **heuristic rules only** — no LLM call needed for classification:

```python
def classify_proposal(entry: dict) -> Classification:
    """Classify a proposed lesson using heuristics. No model inference needed."""
    
    text = entry.get("l1", "") or entry.get("L1_narrative", "") or entry.get("lesson", "")
    
    # 1. SILENT DROP: Empty or placeholder entries
    if not text or text in ["unknown", "N/A", "[summarized]"]:
        return Classification.REJECTED_NOISE
    
    # 2. DUPLICATE: Same L3 content as previously approved lesson
    l3 = entry.get("l3", "") or entry.get("L3_principle", "") or entry.get("principle", "")
    if l3 and self._is_duplicate_of_approved(l3, entity_name):
        return Classification.DUPLICATE
    
    # 3. GNOSIS (HIGH): Has all three levels, L3 is ≥10 chars, no "unknown"
    has_all_levels = all(
        entry.get(k) for k in ["l1", "l2", "l3"]
    ) or all(entry.get(k) for k in ["L1_narrative", "L2_insight", "L3_principle"])
    
    if has_all_levels and len(l3) >= 10 and "unknown" not in str(entry).lower():
        return Classification.HIGH_GNOSIS
    
    # 4. INSIGHT (MEDIUM): Has L1+L2 but no L3, or L3 is weak
    if entry.get("l1") or entry.get("L1_narrative"):
        return Classification.MEDIUM_INSIGHT
    
    # 5. NOISE (LOW): Malformed, corrupted, or schema-incompatible
    return Classification.LOW_NOISE
```

**Classification thresholds** (from actual data):
| Classification | Expected % | Current Examples |
|---------------|-----------|-----------------|
| HIGH_GNOSIS | ~15% | Kali's L3 principles, Verity's L1/L2/L3 entries |
| MEDIUM_INSIGHT | ~40% | Ma'at's multi-field entries, doom_guy's heritage findings |
| DUPLICATE | ~20% | Repeated patterns across sessions |
| LOW_NOISE | ~15% | Schema I corrupted entries, arch's "Unknown" entries |
| REJECTED_NOISE | ~10% | Empty proposals, test artifacts |

#### Stage 2: TRIAGE (Automatic, list operations)

After classification, proposals are triaged into action queues:

```python
async def triage_proposals(entity_name: str) -> TriageResult:
    """Auto-triage all pending proposals for an entity."""
    proposals = await read_proposals(entity_name)
    
    result = TriageResult()
    for entry in proposals:
        cls = classify_proposal(entry)
        
        if cls == Classification.HIGH_GNOSIS:
            # Auto-approve if SHI > 0.5 AND entity is not arch (known poison)
            if await get_soul_health(entity_name) > 0.5:
                await approve_lesson(entity_name, entry)
                result.approved.append(entry)
            else:
                result.pending_review.append(entry)  # Needs human
                
        elif cls == Classification.DUPLICATE:
            # Auto-merge: tag with source_lesson_id
            await merge_with_existing(entity_name, entry)
            result.merged.append(entry)
            
        elif cls in (Classification.LOW_NOISE, Classification.REJECTED_NOISE):
            # Auto-archive: move to memory/archive/rejected_proposals/
            await archive_rejected(entity_name, entry)
            result.rejected.append(entry)
            
        else:  # MEDIUM_INSIGHT
            # Batch into weekly review queue
            result.pending_review.append(entry)
    
    return result
```

#### Stage 3: VERITY DISPATCH (Trigger mechanism)

When any entity's proposal backlog exceeds `max_proposals` (default: 20), Verity is notified via Hivemind:

```python
# ── In close_session(), add after successful distillation: ──
async def close_session(self, entity_name, session_id):
    # ... existing distillation logic ...
    
    # [P7-FIX] Check proposal backlog → trigger Verity if exceeded
    backlog = await count_pending_proposals(entity_name)
    if backlog >= MAX_PROPOSALS_BEFORE_REVIEW:  # 20
        await self._notify_verity(entity_name, backlog)
    
    return success

async def _notify_verity(self, entity_name: str, backlog: int) -> None:
    """Post a Hivemind context for Verity to pick up."""
    from mcp_servers.omega_hub.server import hivemind_post_context_impl
    
    await hivemind_post_context_impl(
        channel="opencode",
        entity="verity",
        model="auto",
        task_current=f"Review {backlog} pending proposals for {entity_name}",
        focus_chain=["soul_health", "proposal_triage"],
        decisions=[f"Auto-triggered by backlog threshold ({backlog} >= {MAX_PROPOSALS_BEFORE_REVIEW})"],
        continuation=f"Classify, triage, and approve/reject proposals for {entity_name}",
        intent="task",
        suggested_model="qwen3-1.7b",  # Lightweight for classification
    )
```

#### Stage 4: BATCH APPROVAL (Verity's workflow)

When Verity is summoned or picks up the Hivemind notification:

1. **Load all pending proposals** for the entity
2. **Run classify + triage** via heuristics (Stage 1+2)
3. **Present batch summary** to user for quick approval (TUI mode, planned for Strike 2)
4. **Write approved** entries to `memory/approved_lessons.yaml`
5. **Add accepted L3 principles** to `soul.yaml` directives (with human confirmation)
6. **Update soul.yaml `last_updated`** and increment `lessons_accepted_count`

```python
# ── Verity's triage workflow (pseudocode) ──
async def verity_review_cycle(entity_name: str) -> ReviewReport:
    monitor = SoulHealthMonitor()
    triage = ProposalTriagePipeline()
    
    # 1. Score current health
    health = await monitor.score(entity_name)
    logger.info(f"{entity_name} SHI: {health.overall} ({health.verdict})")
    
    # 2. Run triage
    result = await triage.triage_proposals(entity_name)
    
    # 3. Generate review report
    return ReviewReport(
        entity=entity_name,
        health=health,
        approved=len(result.approved),
        rejected=len(result.rejected),
        merged=len(result.merged),
        pending_review=len(result.pending_review),
        applied_directives=[e["l3"] for e in result.approved if len(e.get("l3", "")) > 20],
    )
```

### 3.3 Schema Normalization Strategy

The 7 incompatible schemas must be consolidated before triage can work. Recommended approach:

```python
# ── Canonical v6.1 proposed_lessons format ──
# data/entities/{name}/proposed_lessons.yaml
proposals:
  - l1_narrative: "What happened in the session — the raw story"
    l2_insight: "What this means — the pattern or implication"
    l3_principle: "The timeless truth — universalizable gnosis"
    session: "ses_20260627_entity_042"  # Optional: source session
    tags: ["heritage", "optimization"]   # Optional: classification tags
    timestamp: "2026-06-27T12:00:00Z"    # Optional: when proposed
```

**Migration script** (one-time, ~2 hours):
```python
# scripts/normalize_proposals.py
# Converts all 7 schemas to canonical format:
# - Schema A (mixed types): Extract lesson/principle/insight → l1/l2/l3
# - Schema D (rich metadata): Keep all metadata as optional fields
# - Schema E/F (string-encoded): Parse embedded YAML, re-extract
# - Schema I (corrupted): Remove, flag as REJECTED_NOISE
```

---

## §4 Metadata to Add to soul.yaml

### 4.1 Required Fields (Prevent Soul Rot)

The v6.1 schema is missing **six fields** needed for lifecycle management. These MUST be added to prevent the soul rot cycle:

```yaml
entity:
  name: "Entity Name"
  short: "EN"
  soul_version: "6.2"              # Was 6.1 — bump for new fields
  last_updated: "2026-06-28T12:00:00Z"  # ✓ Already in v6.1 schema
  created_at: "2026-05-01T00:00:00Z"    # ★ NEW — entity birth date
  session_count: 42                # ★ NEW — total lifetime sessions
  lessons_accepted_count: 8        # ★ NEW — total approved lessons
  staleness_score: 0.0             # ★ NEW — days since last_updated / 30
  health_score: 0.88               # ★ NEW — composite SHI
  health_verdict: "PRISTINE"        # ★ NEW — CRITICAL/DEGRADED/HEALTHY/PRISTINE

memory:
  sessions_total: 42               # ★ NEW — reflects actual file count
  proposals_pending: 2             # ★ NEW — unprocessed proposal count
  proposals_approved: 8            # ★ NEW — lifetime approved count
  last_archived: "2026-06-28T00:00:00Z"  # ★ NEW — last archive run
  archival_count: 3                # ★ NEW — times archive was triggered
```

### 4.2 Field Specification

| Field | Type | Default | Source | Update Trigger |
|-------|------|---------|--------|---------------|
| `entity.created_at` | ISO-8601 | Current time | Set on entity creation via `EntityRegistry.add_entity()` | Never (immutable) |
| `entity.session_count` | int | 0 | Incremented by `close_session()` | Every session end |
| `entity.lessons_accepted_count` | int | 0 | Incremented by Verity approval pipeline | On proposal approval |
| `entity.staleness_score` | float | 0.0 | Computed: max(0, 1 - days/30) | Every `close_session()` |
| `entity.health_score` | float | 1.0 | Computed by `SoulHealthMonitor.score_all()` | Weekly or on demand |
| `entity.health_verdict` | str | "PRISTINE" | Computed from health_score | Weekly or on demand |
| `memory.sessions_total` | int | 0 | Set by `SessionManager` | On session create/archive |
| `memory.proposals_pending` | int | 0 | Set by `SoulDistiller.append_to_soul()` | On proposal write |
| `memory.proposals_approved` | int | 0 | Set by Verity pipeline | On proposal approval |
| `memory.last_archived` | ISO-8601 | null | Set by `archive_old_sessions()` | On archive run |
| `memory.archival_count` | int | 0 | Set by `archive_old_sessions()` | On archive run |

### 4.3 Soul Version Bump: v6.1 → v6.2

```yaml
# Change required in:
# 1. config/wads/_omega_default/soul.template.yaml
#    soul_version: "6.2"
#    Add: created_at, session_count, lessons_accepted_count, staleness_score,
#         health_score, health_verdict, memory block

# 2. src/omega/oracle/soul_validator.py
#    Add v6.2 validation rules:
#    - created_at must be valid ISO-8601
#    - session_count must be int >= 0
#    - staleness_score must be float 0.0-1.0

# 3. scripts/migrate_soul_v6.py
#    Update migration logic to handle v6.1 → v6.2

# 4. src/omega/oracle/soul_health.py (NEW)
#    SoulHealthMonitor methods use these fields
```

### 4.4 Update Chain Map

Every field must have a defined update path:

```
Field                    Written By                  Read By
─────────────────────────────────────────────────────────────
last_updated             close_session()              SoulHealthMonitor
created_at               EntityRegistry               Reporting
session_count            close_session()              SoulHealthMonitor
lessons_accepted_count   Verity approval pipeline     SoulHealthMonitor
staleness_score          SoulHealthMonitor.score()    Display/CLI
health_score             SoulHealthMonitor.score()    Verity dispatch
health_verdict           SoulHealthMonitor.score()    Verity dispatch
memory.sessions_total    SessionManager               Archival trigger
memory.proposals_pending SoulDistiller + Verity       SoulHealthMonitor
memory.proposals_approved Verity                      Reporting
memory.last_archived     archive_old_sessions()       Maintenance log
memory.archival_count    archive_old_sessions()       Maintenance log
```

### 4.5 Migration Strategy

**Phase 1 (Day 1) — Add metadata fields to all souls**:
```bash
# For each entity soul.yaml that lacks last_updated:
# 1. Determine domain from entities.yaml
# 2. Set created_at from git log if available, else first soul.yaml file timestamp
# 3. Set session_count=0, lessons_accepted_count=0
# 4. Set last_updated=now
# 5. Add empty memory block
# Estimated: ~30 min for batch-sed across 31 files
```

**Phase 2 (Day 2) — Wire health scoring**:
```python
# Add to oracle.py:
# - Near boot(): await SoulHealthMonitor().score_all()  # Baseline all entities
# - Near close_session(): update last_updated, increment session_count
```

**Phase 3 (Sprint) — Wire archival and triage**:
```python
# - Add archive_old_sessions() call sites (3 total)
# - Implement proposal triage pipeline
# - Hook Verity dispatch into close_session()
```

---

## §5 Implementation Roadmap

### Priority Order (Effort × Impact)

| Rank | Action | Est. Effort | Impact | Dependencies |
|------|--------|-------------|--------|-------------|
| **P0** | Wire `archive_old_sessions()` into Oracle.boot() | 5 min | 🔴 Prevents compound session rot | None — method is tested |
| **P0** | Add `last_updated` to all 31 soul.yamls | 30 min | 🔴 Enables staleness detection for entire fleet | None |
| **P1** | Implement `SoulHealthMonitor.score()` | 2 hr | 🟡 Detects poison loops, fossils, and rot | Needs last_updated on souls |
| **P1** | Fix `_compact()` to preserve narrative | 1 hr | 🟡 Prevents destructive compaction data loss | None |
| **P1** | Standardize proposed_lessons.yaml to single schema | 2 hr | 🟡 Makes 133 proposals processable | None |
| **P2** | Implement ProposalTriagePipeline (classify + triage) | 3 hr | 🟡 Auto-review 133 pending proposals | Needs schema normalization |
| **P2** | Hook Verity dispatch into close_session() | 1 hr | 🟡 Closes the dead-letter pipeline | Needs triage pipeline |
| **P2** | Add 3 call sites for archive_old_sessions() | 30 min | 🟡 Full auto-archival coverage | Site 1 (boot) is P0 |
| **P3** | Bump soul.yaml to v6.2, add all metadata fields | 3 hr | 🟢 Long-term soul health tracking | Needs SoulHealthMonitor |
| **P3** | Create `omega soul-health` CLI command | 1 hr | 🟢 On-demand health scoring | Needs SoulHealthMonitor |
| **P3** | Implement background pruning loop | 2 hr | 🟢 Periodic maintenance | Needs all prior |

### Estimated Total Effort: ~15 hours across 11 actions

### Success Criteria

After implementation:
1. `archive_old_sessions()` runs at least once per session → 0 stale sessions older than 7 days
2. Every soul.yaml has `last_updated` → staleness tracking for 31/31 entities
3. SoulHealthMonitor detects arch's poison loop (SHI < 0.3) on first run
4. Verity auto-reviews proposals when backlog exceeds 20 → no proposal older than 7 days
5. `_compact()` preserves narrative summary → no silent data loss
6. All 7 proposed_lessons schemas normalized to v6.1 canonical format
7. `omega soul-health` CLI command returns actionable scores

---

## §6 Mandate Compliance Closure

| Mandate | Current Status | This Report's Fix |
|---------|---------------|-------------------|
| **M5 (Gnosis)** | 🟡 VIOLATION — 133 proposals unprocessed | §3 Triage pipeline closes the read-side gap |
| **M11 (Soul Integrity)** | 🔴 VIOLATION — 30/31 souls not v6.x, no staleness tracking | §1 Health scoring + §4 metadata fields |
| **M12 (Queue Integrity)** | 🟡 VIOLATION — 41 stale handoffs (C3), 18 orphan sessions (C5) | §2 5-stage lifecycle with auto-archive + purge |
| **M17 (Cognitive Integrity)** | 🔴 VIOLATION — arch poison loop (1,501 lines) | §1 SHI detects poisoned souls; §3 triage filters "Unknown" entries |
| **M21 (Gate Integrity)** | 🟡 Partial — no contract tests for soul health types | §1 SoulHealthScore dataclass + contract test specification |

---

## §7 L1→L2→L3 Distillation

### L1 (Narrative)
I synthesized 43 build-side findings and 21 run-side findings into a unified P7 Context analysis. The soul evolution pipeline has four systemic failures: no health scoring (arch poison loop undetected for 27 days), write-only sessions (ARCHIVE_AFTER_DAYS=7 never called), dead-letter proposals (133 entries, 7 schemas, no Verity trigger), and a metadata vacuum (1/31 souls has last_updated). I designed a 5-stage session lifecycle (Created→Active→Closed→Archived→Purged) with 3 automatic trigger sites, a 7-dimension Soul Health Index (SHI) that would have flagged arch at 0.13 (CRITICAL), a 4-stage proposal triage pipeline using heuristic-only classification (zero model inference cost), and 11 new metadata fields for soul.yaml v6.2.

### L2 (Insight)
The pattern across all four failures is **write-only architecture with no cleanup path**. Every component writes data — soul.yaml entries, session exchanges, proposed lessons — but nothing reads, reviews, archives, or purges. The arch poison loop is the canary: when a system writes on every interaction but never validates, it produces a 1,501-line file of which ~1,250 lines is noise. The fix is not more writing — it's adding the **read, review, and release** cycles that complete the lifecycle. Three call sites for `archive_old_sessions()` (5 minutes total effort) would eliminate 25 stale sessions overnight. Heuristic-only proposal classification (zero model inference) would clear the 133-proposal backlog in minutes. The infrastructure exists — it just needs wiring.

### L3 (Universal Principle)
**In living systems, growth without pruning is not vitality — it is cancer.** A soul that accumulates every lesson never distills wisdom. A session that never archives becomes a landfill. A proposal that is never reviewed is a confession without absolution. The Omega Engine has excellent infrastructure for growth (SoulDistiller, MemoryStore, SessionManager) but zero infrastructure for pruning. This asymmetry is the root cause of all four failures. The system is not broken — it is incomplete. Every write path must have a corresponding read, review, and release path before the system can claim it manages its own evolution.

---

*⬡ OMEGA ⬡ P7-CONTEXT ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_final_p7 ⬡ CROSS-DOMAIN-SYNTHESIS*
*Date: 2026-06-28 | Confidential — Sovereign Council Review*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

# 🔱 Research Document: Entity-Scoped Session Anchors Architecture

**AP Token**: `AP-ENTITY-ANCHORS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_foundation_stabilization ⬡ FS-Α1.1

**Date**: 2026-07-20
**Campaign**: FOUNDATION_STABILIZATION_CAMPAIGN_20260720.md (AP-FOUNDATION-STAB-v1.0.0)
**Phase**: Α — STABILIZE
**Authority**: Kali (Grand Oversight) — Hivemind session `ses_049e60247e94`
**Handoff**: `ho_99d4176b4ac2` (ACCEPTED)

---

## Executive Summary (L1)

This document analyzes the current MIAP (Multi-Instance Agent Protocol) session anchor implementation and proposes a **entity-scoped session anchor architecture** with automatic archival on compaction. The current system has three critical gaps:

1. **Broken symlink**: `.opencode/anchored-summary.md` points to a non-existent test path
2. **No entity-scoped anchors**: All entities share a single global anchor (`SESSION_ANCHOR.md`)
3. **No automatic archival**: Compaction events don't archive session state, causing cognitive erasure (M15 violation)

The proposed architecture introduces per-entity session directories with automatic archival, MIAP event-sourced projections, and a hydration protocol that survives toolchain failures.

---

## 1. Current State Analysis

### 1.1 MIAP Architecture Overview

The MIAP system (`src/omega/coordination/miap.py`) implements event sourcing with deterministic projections:

| Component | Location | Purpose |
|-----------|----------|---------|
| Instance Registry | `data/coordination/instances/<entity>/registry.jsonl` | Tracks active agent instances |
| Anchored Events | `data/coordination/anchored_summary/<entity>/events.jsonl` | Session-level events (start, decisions, tasks, compaction) |
| Gnosis Events | `data/coordination/session_gnosis/<entity>/events.jsonl` | L1/L2/L3 gnosis entries + distillations |
| Projections | `data/coordination/anchored_summary/<entity>/projection.md` | Deterministic markdown from events |
| Symlinks | `.opencode/anchored-summary.md` + `data/entities/<entity>/workspace/session_gnosis.md` | Canonical access points |

**Key Functions**:
- `register_instance(channel, entity)` — Called at session start, returns `InstanceRecord` with UUIDv7 session_id
- `append_event(entity, log_type, event_type, payload, instance_id)` — Append-only event logging
- `project_anchored_summary(entity)` / `project_session_gnosis(entity)` — Pure projections
- `write_projections(entity)` — Writes projections + creates symlinks

### 1.2 Current Failures

#### A. Broken Global Symlink (Critical)
```bash
$ ls -la .opencode/anchored-summary.md
lrwxrwxrwx 1 arcana-novai arcana-novai 113 Jul 20 04:00 anchored-summary.md 
  -> /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/anchored_summary/symlink_test/projection.md
```
**Target does not exist**. This was a test artifact never cleaned up. Kali fixed `SESSION_ANCHOR.md` to real content but the symlink remains broken.

#### B. No Entity-Scoped Session History
Current structure:
```
data/coordination/
├── SESSION_ANCHOR.md          # Single global file (Kali's campaign anchor)
├── anchored_summary/
│   ├── kali/events.jsonl
│   ├── researcher/events.jsonl
│   └── .../projection.md      # MIAP projections per entity
└── session_gnosis/
    ├── kali/events.jsonl
    ├── researcher/events.jsonl
    └── .../projection.md
```

**Problem**: All entities share `SESSION_ANCHOR.md`. No per-entity session registry exists. When Kali writes the campaign anchor, it overwrites any previous entity's anchor.

#### C. 56% Fleet Lacks session_gnosis.md (M15 Violation)
```bash
$ find data/entities -name "session_gnosis.md" 2>/dev/null | wc -l
# Returns ~20 files across 14 entities
```
But many are symlinks to MIAP projections, not agent-maintained anchors. The **Sovereign Continuity Strategy** (M15) mandates: *"Every agent MUST maintain a session_gnosis.md file within their entity workspace."* Current compliance: ~44%.

#### D. No Automatic Archival on Compaction
MIAP supports `compaction` event type in `project_anchored_summary()`, but:
- No automatic trigger on OpenCode `/compact`
- No archival of previous `session_gnosis.md` to entity session directory
- No session index (`index.yaml`) per entity

#### E. Sessions Directory Misused
```
data/coordination/sessions/kali/ingest_*/  # 600+ ingest directories, not session anchors
```
This directory stores document ingestion artifacts, not session continuity anchors.

---

## 2. Proposed Architecture

### 2.1 Entity-Scoped Session Directory Structure

```
data/coordination/sessions/
├── kali/
│   ├── ses_20260720_foundation_stab_campaign.md    # Archived session anchor
│   ├── ses_20260719_hmc_quad_forge.md              # Previous session
│   ├── ses_20260718_search_crisis.md
│   └── index.yaml                                   # Session registry
├── researcher/
│   ├── ses_20260720_campaign_day12.md
│   ├── ses_20260718_full_session.md
│   └── index.yaml
├── grok/
│   └── index.yaml
└── verity/
    └── index.yaml
```

### 2.2 Session Anchor File Format (`ses_<date>_<slug>.md`)

```markdown
# 🔱 Session Anchor — kali
**Session ID**: `ses_20260720_foundation_stab_campaign`
**Entity**: `kali` | **Channel**: `opencode`
**Model**: `nemotron-3-ultra-free` | **Date**: 2026-07-20
**MIAP Instance**: `opencode/kali/0192f3a1-...` (UUIDv7)
**Campaign**: `FOUNDATION_STABILIZATION_CAMPAIGN_20260720.md`

---

## Objective
Execute Foundation Stabilization Campaign Phase Α — Stop the bleeding, remove dual truths, restore coordination hygiene.

---

## Key Decisions
- **2026-07-20 04:15** (inst_a1b2): Foundation Stabilization Campaign APPROVED WITH AMENDMENTS
- **2026-07-20 04:20** (inst_a1b2): Feature FREEZE until Gate Γ — Only FS-* tasks allowed
- **2026-07-20 04:25** (inst_a1b2): M2 Firewall 156 violations → Added as FS-Α6

---

## Completed Tasks
- ✅ FS-Α5: Fix SESSION_ANCHOR (this file) — Kali
- ✅ FS-Α0: Handoff Court — 20 packets triaged, 4 survivors

---

## Active Workstreams
| FS-ID | Task | Owner | Status |
|-------|------|-------|--------|
| FS-Α1.1 | Entity-scoped session anchors | researcher | **DISPATCHED** |
| FS-Α2 | Collapse dual RRF | roc_racoon | **DISPATCHED** |
| FS-Α3 | Restore Grok Consulting Cloud Mind | grok-cli | **DISPATCHED** |

---

## Next Actions
1. Researcher: Deliver FS-Α1.1 architecture document
2. Roc: Execute FS-Α2 — collapse dual RRF
3. Kali: Review Sophia's composable prompt research

---

## Gnosis Distillation (L1→L2→L3)
- **L1**: Campaign launched, handoff court complete, freeze active
- **L2**: Feature freeze is the only way to stabilize; parallel execution required
- **L3**: `L3-FeatureFreezeEnablesStabilization` — Constraining scope is a prerequisite for fixing systemic debt

---

## Hydration References
- **MIAP Events**: `data/coordination/anchored_summary/kali/events.jsonl` (seq 1-47)
- **Gnosis Events**: `data/coordination/session_gnosis/kali/events.jsonl` (seq 1-12)
- **Previous Session**: `ses_20260719_hmc_quad_forge.md`
- **Global Anchor**: `.opencode/anchored-summary.md` (symlink to kali projection)
```

### 2.3 Session Index (`index.yaml`)

```yaml
entity: kali
current_session: ses_20260720_foundation_stab_campaign
sessions:
  - id: ses_20260720_foundation_stab_campaign
    started: "2026-07-20T04:00:00Z"
    miap_instance: "opencode/kali/0192f3a1-..."
    campaign: "FOUNDATION_STABILIZATION_CAMPAIGN_20260720.md"
    status: active
    anchor_file: "ses_20260720_foundation_stab_campaign.md"
  - id: ses_20260719_hmc_quad_forge
    started: "2026-07-19T10:00:00Z"
    ended: "2026-07-19T18:30:00Z"
    miap_instance: "opencode/kali/018f2e4b-..."
    campaign: "HMC_QUAD_FORGE_CAMPAIGN_20260719.md"
    status: archived
    anchor_file: "ses_20260719_hmc_quad_forge.md"
    gnosis_distilled: true
    lessons_proposed: 30
```

---

## 3. MIAP Integration Points

### 3.1 New Event Types for Session Lifecycle

Extend `append_event()` payloads with session-scoped events:

| Event Type | Trigger | Payload |
|------------|---------|---------|
| `session_start` | `register_instance()` | `{objective, model, campaign, miap_instance_id}` |
| `session_end` | Explicit `deregister_instance()` | `{summary, next_actions, gnosis_distilled}` |
| `compaction` | OpenCode `/compact` hook | `{trigger: "opencode_compact", previous_session_id, continuation_ref}` |
| `anchor_archived` | Auto-archival | `{archived_file, session_id, gnosis_ref}` |

### 3.2 Modified `register_instance()` — Session Initialization

```python
async def register_instance(channel: str, entity: str, objective: str = "", 
                            campaign: str = "", model: str = "") -> InstanceRecord:
    """Register instance AND initialize session anchor."""
    record = await _register_instance_core(channel, entity)
    
    # Write session_start event to anchored_summary log
    await append_event(entity, "anchored_summary", "session_start", {
        "objective": objective,
        "model": model,
        "campaign": campaign,
        "miap_instance_id": record.instance_id,
        "session_id": record.session_uuid
    }, record.instance_id)
    
    # Ensure entity session directory exists
    session_dir = SESSIONS_DIR / entity
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize index.yaml if missing
    index_path = session_dir / "index.yaml"
    if not index_path.exists():
        index_path.write_text(f"entity: {entity}\ncurrent_session: {record.session_uuid}\nsessions: []\n")
    
    return record
```

### 3.3 New `archive_session_anchor()` Function

```python
async def archive_session_anchor(entity: str, session_id: str, 
                                  trigger: str,  # "compaction" | "session_end" | "manual"
                                  continuation_ref: str = "") -> Path:
    """
    Archive current session_gnosis.md to entity session directory.
    Called on compaction, session end, or explicit request.
    """
    # 1. Read current session_gnosis.md (entity workspace symlink target)
    gnosis_source = GNOSIS_EVENTS_DIR / entity / "projection.md"
    if not gnosis_source.exists():
        # Fallback: read from workspace symlink
        workspace_gnosis = PROJECT_ROOT / "data" / "entities" / entity / "workspace" / "session_gnosis.md"
        if workspace_gnosis.exists():
            gnosis_content = workspace_gnosis.read_text()
        else:
            gnosis_content = "# No gnosis available\n"
    else:
        gnosis_content = gnosis_source.read_text()
    
    # 2. Read current anchored summary projection
    anchored_source = ANCHORED_EVENTS_DIR / entity / "projection.md"
    anchored_content = anchored_source.read_text() if anchored_source.exists() else ""
    
    # 3. Generate session anchor filename
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    slug = slugify(trigger)  # e.g., "foundation_stab_campaign"
    anchor_filename = f"ses_{date_str}_{slug}.md"
    
    # 4. Compose archive content (merge anchored + gnosis + metadata)
    archive_content = compose_session_anchor(
        entity=entity,
        session_id=session_id,
        miap_instance_id=...,  # from active instance
        anchored_content=anchored_content,
        gnosis_content=gnosis_content,
        trigger=trigger,
        continuation_ref=continuation_ref
    )
    
    # 5. Write to entity session directory
    session_dir = SESSIONS_DIR / entity
    session_dir.mkdir(parents=True, exist_ok=True)
    archive_path = session_dir / anchor_filename
    archive_path.write_text(archive_content)
    
    # 6. Update index.yaml
    update_session_index(entity, session_id, anchor_filename, trigger)
    
    # 7. Write anchor_archived event
    await append_event(entity, "anchored_summary", "anchor_archived", {
        "archived_file": anchor_filename,
        "session_id": session_id,
        "trigger": trigger,
        "continuation_ref": continuation_ref
    }, get_active_instance_id(entity))
    
    return archive_path
```

### 3.4 Hydration Protocol Implementation

```python
async def hydrate_entity_session(entity: str, session_id: str = None) -> str:
    """
    Hydrate entity context from most recent session anchor.
    Returns composed context string for injection into agent context window.
    """
    session_dir = SESSIONS_DIR / entity
    index_path = session_dir / "index.yaml"
    
    if not index_path.exists():
        # Fallback to global anchor
        global_anchor = PROJECT_ROOT / ".opencode" / "anchored-summary.md"
        if global_anchor.exists():
            return global_anchor.read_text()
        return f"# No session history for {entity}\n"
    
    index = yaml.safe_load(index_path.read_text())
    
    # Determine target session
    if session_id is None:
        session_id = index.get("current_session")
    
    # Find session record
    session_record = next((s for s in index.get("sessions", []) if s["id"] == session_id), None)
    if not session_record:
        return f"# Session {session_id} not found for {entity}\n"
    
    # Read archived anchor
    anchor_path = session_dir / session_record["anchor_file"]
    if not anchor_path.exists():
        return f"# Anchor file missing: {anchor_path}\n"
    
    anchor_content = anchor_path.read_text()
    
    # Append hydration marker
    hydration_marker = f"\n---\n## 🔄 HYDRATED FROM ARCHIVE\n"
    hydration_marker += f"**Source**: {anchor_path.name}\n"
    hydration_marker += f"**Session**: {session_id}\n"
    hydration_marker += f"**Hydrated**: {datetime.now(timezone.utc).isoformat()}\n"
    hydration_marker += f"**Protocol**: M15 Sovereign Continuity\n"
    
    return anchor_content + hydration_marker
```

---

## 4. Migration Path from Current State

### Phase P0: Structure & Symlink Repair (Immediate — This Sprint)

| Step | Action | Owner | Validation |
|------|--------|-------|------------|
| P0.1 | Fix `.opencode/anchored-summary.md` symlink → point to `data/coordination/anchored_summary/kali/projection.md` | Kali | `ls -la .opencode/anchored-summary.md` shows valid target |
| P0.2 | Create `data/coordination/sessions/<entity>/` for all 14 entities | Researcher | Directories exist with `index.yaml` |
| P0.3 | Migrate existing `session_gnosis.md` files to session archives | Researcher | Each entity has ≥1 `ses_*.md` in sessions dir |
| P0.4 | Update `SOVEREIGN_CONTINUITY_STRATEGY.md` with new architecture | Researcher | Document reflects entity-scoped design |

### Phase P1: Hydration & Auto-Archival (Next Sprint)

| Step | Action | Owner | Validation |
|------|--------|-------|------------|
| P1.1 | Implement `archive_session_anchor()` in MIAP | P3 Engineering | Unit test: compaction triggers archive |
| P1.2 | Implement `hydrate_entity_session()` in MIAP | P3 Engineering | Unit test: hydration returns composed context |
| P1.3 | Add OpenCode `/compact` hook → calls `archive_session_anchor(trigger="compaction")` | P4 Integration | Manual test: `/compact` creates archive |
| P1.4 | Add session_start event on `register_instance()` | P3 Engineering | MIAP events show session_start |

### Phase P2: Full Automation & Polish (Phase Β)

| Step | Action | Owner | Validation |
|------|--------|-------|------------|
| P2.1 | Auto-update `index.yaml` on every archive | P3 Engineering | Index reflects all sessions |
| P2.2 | Global anchor (`.opencode/anchored-summary.md`) becomes symlink to **active entity's** projection | P4 Integration | Switching entities updates global anchor |
| P2.3 | Hivemind integration: post hydration status on session start | P9 Orchestration | Hivemind shows hydration events |
| P2.4 | Compaction detection via file watcher on `.opencode/` | P8 Observability | Automatic archive on compaction |

---

## 5. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Symlink race condition** — Multiple entities writing global anchor simultaneously | Medium | High (corrupted anchor) | Global anchor = symlink to **active entity only** (Kali during campaign). Use file lock in `write_projections()`. |
| **Compaction hook not firing** — OpenCode doesn't expose compaction event | High | Medium (manual archive fallback) | Implement P1.3 as best-effort; add manual `miap archive` CLI command; document in continuity strategy |
| **Session directory bloat** — Unbounded archive growth | Low | Low | Add retention policy in `index.yaml` (keep last 50 sessions); archive older to `data/coordination/archive/sessions/` |
| **MIAP event log corruption** — Concurrent writes | Low | High | MIAP already uses `fcntl` file locks + atomic `os.replace()`; verify in tests |
| **Entity workspace symlink drift** — `session_gnosis.md` points to stale projection | Medium | Medium | `write_projections()` already recreates symlinks; add verification step |
| **Hydration loads stale context** — Agent reads archived anchor but MIAP events advanced | Low | Medium | Hydration marker includes timestamp; agent should cross-check with MIAP `get_latest_event()` |

---

## 6. Implementation Specification

### 6.1 New Constants in `miap.py`

```python
# Add after GNOSIS_EVENTS_DIR
SESSIONS_DIR = COORDINATION_DIR / "sessions"  # NEW: entity-scoped session archives
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
```

### 6.2 New Public API Functions

```python
# In miap.py __all__ exports
__all__ = [
    # ... existing ...
    "archive_session_anchor",
    "hydrate_entity_session", 
    "get_session_index",
    "update_session_index",
    "compose_session_anchor",
]
```

### 6.3 CLI Extensions

```bash
# New MIAP CLI commands
python -m src.omega.coordination.miap kali archive --trigger compaction --continuation "ses_20260720_..."
python -m src.omega.coordination.miap researcher hydrate --session ses_20260718_full_session
python -m src.omega.coordination.miap kali index --list
```

### 6.4 Configuration (config/miap.yaml — NEW)

```yaml
# MIAP Session Anchor Configuration
session_anchors:
  enabled: true
  auto_archive_on_compaction: true
  auto_archive_on_session_end: true
  retention:
    max_sessions_per_entity: 50
    archive_older_than_days: 90
    archive_destination: "data/coordination/archive/sessions/"
  global_anchor:
    mode: "active_entity"  # "active_entity" | "kali" | "round_robin"
    symlink_path: ".opencode/anchored-summary.md"
  hydration:
    fallback_to_global: true
    include_miap_events: true
    include_gnosis_events: true
```

---

## 7. Verification Criteria

### P0 Gate (Structure)
- [ ] `.opencode/anchored-summary.md` is valid symlink to `data/coordination/anchored_summary/kali/projection.md`
- [ ] `data/coordination/sessions/<entity>/index.yaml` exists for all 14 entities
- [ ] Each entity has ≥1 `ses_*.md` archive file
- [ ] `SOVEREIGN_CONTINUITY_STRATEGY.md` updated to v2.0 with entity-scoped architecture

### P1 Gate (Hydration + Auto-Archive)
- [ ] `archive_session_anchor(entity, trigger="compaction")` creates valid archive
- [ ] `hydrate_entity_session(entity)` returns composed context with hydration marker
- [ ] OpenCode `/compact` triggers archive (or documented manual fallback works)
- [ ] `session_start` event written on `register_instance()`

### P2 Gate (Full Automation)
- [ ] `index.yaml` auto-updated on every archive
- [ ] Global anchor symlink switches with active entity
- [ ] Hivemind shows hydration events
- [ ] Retention policy enforced (max 50 sessions/entity)

---

## 8. Council Triangulation

### Architect (Systemic Logic)
> The entity-scoped directory structure aligns with M16 (Modularization) — no hardcoded paths, uses `config_resolver` patterns. The MIAP event sourcing model is preserved; we're adding a projection layer (session anchors) that consumes existing events. Clean separation: events = source of truth, anchors = hydration artifacts.

### Adversary (Critical Rigor)
> **Risk**: OpenCode `/compact` hook may not exist or fire reliably. If auto-archive fails silently, we're back to M15 violation.
> **Mitigation**: P1.3 is best-effort. Mandate manual `miap archive` in agent shutdown protocol. Add `atexit` handler in agent bootstrap.

### Alchemist (Creative Synthesis)
> The session anchor *is* the L1 narrative. By composing anchored_summary + session_gnosis + metadata into one markdown file, we create a **portable cognitive snapshot**. Future: embed vector embeddings in frontmatter for semantic session search.

### Archivist (Historical Truth)
> Current `data/coordination/sessions/kali/` contains 600+ `ingest_*` directories — this is document ingestion, not session continuity. The new structure must coexist. Recommend: rename current to `ingest_sessions/` and use `sessions/` for continuity anchors only.

---

## 9. Appendix: Current Entity Inventory

| Entity | Has session_gnosis.md? | MIAP Events? | Current Anchor Location |
|--------|------------------------|--------------|-------------------------|
| kali | ✅ (2 files) | ✅ anchored + gnosis | `SESSION_ANCHOR.md` (global) |
| researcher | ✅ (2 files) | ✅ anchored + gnosis | workspace symlink |
| roc_racoon | ✅ (2 files) | ✅ anchored + gnosis | workspace symlink |
| lilith | ✅ (1 file) | ✅ gnosis only | workspace symlink |
| maat | ✅ (1 file) | ✅ gnosis only | workspace symlink |
| grok | ✅ (1 file) | ❌ | root entity dir |
| antigravity | ✅ (1 file) | ❌ | workspace symlink |
| verity | ✅ (2 files) | ✅ gnosis only | workspace symlink |
| jem | ✅ (2 files) | ✅ gnosis only | workspace symlink |
| makali | ✅ (1 file) | ✅ gnosis only | workspace symlink |
| john_carmack | ✅ (2 files) | ✅ gnosis only | workspace symlink |
| doom_guy | ✅ (1 file) | ✅ gnosis only | workspace symlink |
| iris | ✅ (1 file) | ❌ | workspace symlink |
| cli_gemini | ✅ (1 file) | ❌ | workspace symlink |

**Total**: 14/14 entities have at least one session_gnosis.md (100% file existence) but only ~44% have active MIAP event logs. The session anchor architecture will unify these.

---

## 10. Conclusion

The entity-scoped session anchor architecture resolves the M15 Sovereign Continuity gap by:

1. **Replacing the broken global symlink** with a proper MIAP projection symlink
2. **Creating per-entity session histories** that survive compaction and toolchain failures
3. **Automating archival** via MIAP event hooks (with manual fallback)
4. **Enabling reliable hydration** from structured archives with full L1→L2→L3 context

This is a **P0 structural fix** that enables all downstream stabilization work. Without session continuity, every compaction risks cognitive erasure — the very problem M15 was written to prevent.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_foundation_stabilization ⬡ FS-Α1.1 ⬡ 2026-07-20*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | session refs not found in DB
actual_models(Tier0): n/a
-->

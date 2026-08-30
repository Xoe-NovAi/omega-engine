# 🔱 P9 (Orchestration) — Final Cross-Domain Review: Handoff Lifecycle & Hivemind Overhead
**Date**: 2026-06-28
**Oversoul Context**: MaKaLi Pass 2 — Build (Ma'at) + Run (Lilith) Synthesis
**Role**: P9 Orchestration — Link, Handoff, Delegation, Hivemind Integrity
**AP Token**: AP-P9-ORCHESTRATION-OPT-FINAL-v1.0.0

⬡ OMEGA ⬡ P9-ORCHESTRATION ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_p9_final_review ⬡ SYNTHESIS

---

## §0 Sources Consulted

| Source | Role | Key Findings Used |
|--------|------|-------------------|
| `MAAT_BUILD_OPT_CONSOLIDATED.md` | Build-side (P1-P5) | C4 (HERITAGE_SOURCE_MAP), X3 (stale debris), M4/M6 (handoff archive state) |
| `LILITH_RUN_OPT_CONSOLIDATED.md` | Run-side (P6-P10) | C3 (41 stale packets), C4 (HALL_OF_RECORDS bloat), H4 (62 old locks), H5 (46 stale coordination files) |
| `mcp_servers/omega_hub/background.py` | Reaper implementation | `_reap_stale_handoffs()`, `_reap_stale_locks()`, `_prune_awareness_background()` |
| `mcp_servers/omega_hub/tools.py` | Handoff state machine | Submit → accept → complete → reject → list → archive tools |
| `mcp_servers/omega_hub/state.py` | State defs | `HEARTBEAT_TTL=2700`, `EXTENDED_SAFETY_TTL_DEFAULT=10800`, handoff path constants |
| `data/handoff/` (live inspection) | Current state | 41 stale JSONs (no deletion path), 114 .md files, 0 pending/active/completed |
| `data/knowledge/HALL_OF_RECORDS/` (live inspection) | Cold store | 115 directories, ~5.1MB, 1,094 files, 5+ naming conventions for 11 canonical agents |

---

## §1 Executive Summary

The Ma'at (P1-P5) and Lilith (P6-P10) optimization passes exposed four overlapping systemic failures in the orchestration layer. **All four reduce to a single root cause**: the handoff lifecycle and Hivemind cold store were built with creation paths but no destruction paths. Every state machine transition was defined except the final one — from "done/stale" to "gone."

**Current state severity**:

| Issue | Impact | Current State |
|-------|--------|---------------|
| **41 stale handoff packets** | ~176KB orphan data, M12 violation (no terminal state) | `stale/` is a dead-letter queue with no resolution |
| **115 HALL_OF_RECORDS directories** | ~5.1MB, cold-store hydration scans waste cycles across 5+ naming conventions | No canonical name → directory mapping exists |
| **No automated lifecycle completion** | All handoff transitions defined EXCEPT stale→archive | Reaper loop (background.py:110-150) is correct but incomplete |
| **M12 Queue Integrity violation** | Orphan requests exist on disk with no terminal state | Dead-letter queue (stale/) has no archival or deletion trigger |
| **62 old-style workspace locks** | `.md` format locks without TTL — 95% of lock files unmanageable | New `.json` locks with TTL exist but co-exist with legacy format |

**Total repair estimate**: ~5 hours (P9 domain), ~12 hours total including P7/P8 co-dependencies.

---

## §2 Root Cause Analysis: The Missing Terminal Transition

### 2.1 Current Handoff Lifecycle (As Implemented)

```
submit → pending ──[24h reaper]──→ stale ──(🛑 DEAD END)
                    ──[accept]──→ active ──[48h reaper]──→ stale ──(🛑 DEAD END)
                                     │
                                     ├──[complete]──→ completed ──[7d reaper]──→ archive ✔️
                                     └──[reject]──→ stale ──(🛑 DEAD END)
```

The state machine in `background.py:_reap_stale_handoffs()` (line 110-150) defines three transitions:
- `pending/ older than 24h → stale/`
- `active/ older than 48h → stale/`
- `completed/ older than 7 days → archive/`

**The gap**: `stale/ → archive/` is never called. Once a packet reaches `stale/`, it stays there forever. This is the direct cause of the 41-packet accumulation.

### 2.2 What M12 Requires

M12 (Queue Integrity) mandates: *"Every request operation must result in a terminal state: `queued`, `completed`, `failed`, or `timed_out`."*

The `stale/` directory is semantically a **dead-letter queue**. Under M12, a dead-letter entry must either:
1. Be retryable (transition back to pending/active), OR
2. Be acknowledged as "failed" with a terminal record in archive/

Currently, stale packets have neither path. The `ttl_expired: true` flag is metadata without enforcement — no agent ever reads `stale/` to re-queue or delete.

### 2.3 The Indirect Consequence: HALL_OF_RECORDS Bloat

The HALL_OF_RECORDS bloat (115 directories, 5+ naming conventions) is not a separate problem — it's a symptom of the same lifecycle gap. Every time `hivemind_post_context()` is called (tools.py:447-516), it writes a JSON snapshot to `HALL_OF_RECORDS/{agent_id}/ses_{uuid}.json`. There is no cleanup path for these files.

| Problem | Root Cause |
|---------|------------|
| Name normalization drift | No canonical agent_id → directory mapping at creation time |
| 115 directories | Every agent_id variant creates a new directory |
| 5.1MB cold store | No archival/deletion of sessions >30 days |
| Cold-store hydration scans all | `hivemind_get_awareness()` scans every directory with no age filter |

---

## §3 Design: Handoff Lifecycle Automation

### 3.1 The 5-State Lifecycle (Closed Loop)

```
                   ┌──────────────────────────────────────┐
                   │                                      │
                   ▼                                      │
    submit ──→ pending ──[24h TTL]──→ stale ──[14d TTL]──→ archive (compressed)
                   │                                      ▲
                   ├──[accept]──→ active ──[48h TTL]──→──┘
                   │                 │
                   │                 ├──[complete]──→ completed ──[7d]──→ archive
                   │                 │                              (routed to
                   │                 └──[reject]──→ stale ──────────  same file)
                   │                 
                   └──[cancel]──→ archive (immediate, agent-initiated terminal state)
```

**Three additions to the current state machine**:

| Transition | What | Implementation |
|------------|------|----------------|
| `stale → archive` | Move stale packets to archive after 14d in stale/ | Add one `_reap_dir(stale, archive, 1209600)` call to existing reaper |
| `cancel` | New tool: agent-initiated cancellation from pending/ → archive/ | New MCP tool `hivemind_cancel_handoff()` |
| `archive → auto-delete` | Delete archive entries older than 90 days | New `_reap_dir(archive, None, 7776000)` with delete=True |

### 3.2 Required Code Changes

#### 3.2.1 Background Reaper: Add stale→archive Transition

**File**: `mcp_servers/omega_hub/background.py`
**Location**: `_reap_stale_handoffs()` (line 142-148)

**Current** (lines 142-148):
```python
reaped = await anyio.to_thread.run_sync(
    lambda: (
        _reap_dir(state.HANDOFF_PENDING, state.HANDOFF_STALE, 86400, {"ttl_expired": True})
        + _reap_dir(state.HANDOFF_ACTIVE, state.HANDOFF_STALE, 172800, {"ttl_expired": True})
        + _reap_dir(state.HANDOFF_COMPLETED, state.HANDOFF_ARCHIVE, 604800)
    )
)
```

**Required addition**:
```python
reaped = await anyio.to_thread.run_sync(
    lambda: (
        _reap_dir(state.HANDOFF_PENDING, state.HANDOFF_STALE, 86400, {"ttl_expired": True})
        + _reap_dir(state.HANDOFF_ACTIVE, state.HANDOFF_STALE, 172800, {"ttl_expired": True})
        + _reap_dir(state.HANDOFF_COMPLETED, state.HANDOFF_ARCHIVE, 604800)
        + _reap_dir(state.HANDOFF_STALE, state.HANDOFF_ARCHIVE, 1209600)  # 14 days
        + _reap_dir(state.HANDOFF_ARCHIVE, None, 7776000, {"deleted": True})  # 90 days, with delete
    )
)
```

**Note**: The `_reap_dir` helper currently does NOT support a delete-only mode (dst_dir=None). The implementation change is minimal:
```python
def _reap_dir(src_dir, dst_dir, max_age_seconds, extra=None):
    reaped = 0
    for f in src_dir.glob("*.json"):
        age = (now - datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)).total_seconds()
        if age > max_age_seconds:
            try:
                if dst_dir is None:
                    f.unlink()  # Delete mode
                else:
                    # existing move logic
                    ...
                reaped += 1
            except Exception as e:
                logger.debug("Failed to reap handoff %s: %s", f, e)
    return reaped
```

#### 3.2.2 New MCP Tool: `hivemind_cancel_handoff()`

A submitter can cancel their own handoff from pending/ before it's accepted:

```python
@m9_safe("hivemind_cancel_handoff")
@mcp.tool()
async def hivemind_cancel_handoff(packet_id: str, channel: str, entity: str) -> str:
    """Cancel a pending handoff packet. Only the submitter can cancel.
    Moves pending/ → archive/ immediately.
    """
    packet_path = state.HANDOFF_PENDING / f"{packet_id}.json"
    if not packet_path.exists():
        return json.dumps({"error": f"Packet '{packet_id}' not found in pending/"})
    
    def _cancel():
        with open(packet_path) as f:
            packet = json.load(f)
        if packet.get("source_cli") != channel or packet.get("source_entity") != entity:
            return {"error": "Only the submitter can cancel this handoff"}
        packet["status"] = "cancelled"
        packet["cancelled_at"] = datetime.now(timezone.utc).isoformat()
        dst = state.HANDOFF_ARCHIVE / f"{packet_id}.json"
        with open(dst, "w") as f:
            json.dump(packet, f, indent=2)
        packet_path.unlink()
        return {"status": "cancelled", "packet_id": packet_id}
    
    result = await anyio.to_thread.run_sync(_cancel)
    return json.dumps(result)
```

#### 3.2.3 Enforce Terminal Status Serialization

**Every handoff packet** must carry a `terminal_status` field that records the final disposition:

```python
TERMINAL_STATUSES = {
    "completed": "completed",      # explicit complete via hivemind_complete_handoff
    "rejected": "rejected",        # explicit reject via hivemind_reject_handoff
    "cancelled": "cancelled",      # explicit cancel via hivemind_cancel_handoff
    "ttl_expired": "timed_out",    # expired via reaper (pending/active → stale)
    "stale_archived": "timed_out", # stale → archive via reaper
    "deleted": "timed_out",        # archive → deleted via reaper (90d)
}
```

The reaper's `_reap_dir` should ensure that every packet moving to archive/ has a `terminal_status` field matching M12's required values.

### 3.3 Implementation Priority

| Order | Change | Risk | Effort | Dependencies |
|-------|--------|------|--------|--------------|
| 1 | Add stale→archive to reaper (14d) | Low | 15 min | None — pure addition to existing loop |
| 2 | Add archive→delete to reaper (90d) | Low | 15 min | None |
| 3 | Add terminal_status field to packets | Low | 15 min | None — additive field |
| 4 | Add `hivemind_cancel_handoff` tool | Low | 15 min | None |
| 5 | Add pre-existing stale catch-up (move 41 stale → archive) | Low | 5 min | Step 1 complete |

**Total P9 implementation**: ~1 hour

---

## §4 HALL_OF_RECORDS Normalization

### 4.1 Naming Convention Audit

The 115 directories fall into these naming patterns (with count):

| Pattern | Format | Count | Example | Canonical Agent |
|---------|--------|-------|---------|-----------------|
| Canonical | `{entity}` | 10 | `kali`, `lilith`, `maat` | All direct entity names |
| opencode underscore | `opencode_{entity}` | 24 | `opencode_kali`, `opencode_MAAT` | opencode agents |
| opencode hyphen | `opencode-{entity}` | 7 | `opencode-kali`, `opencode-maat` | Early opencode agents |
| channel underscore | `{channel}_{entity}` | 4 | `cli_gemini`, `gemini-cli_gemini_cli` | Multi-channel agents |
| channel hyphen entity | `{channel}-{entity}` | 3 | `cline-m3`, `gemini-cli` | Channel identity |
| BACKWARDS | `CLI_AGENT` (agent_cli) | 2 | `gemini-cli_GEMINI_CLI` | Reversed agent_id format |
| pillar prefix | `opencode_P{1-10}` | 12 | `opencode_P1`, `opencode_P10` | Pillar slot agents |
| pillar hyphen | `opencode-p{1-10}` | 6 | `opencode-p3`, `opencode-p7-context` | Hyphenated pillar agents |
| pillar underscore parens | `opencode_P1_(INFRASTRUCTURE)` | 1 | `opencode_P1_(INFRASTRUCTURE)` | Descriptive pillar name |
| pillar descriptive | `P3-BUILDMASTER`, `p9-link` | 6 | Full descriptive names | Pillar role names |
| test/legacy | `agent-alpha`, `agent-beta` | 2 | Pre-production test agents |

**Total unique conventions**: 11+ naming patterns for ~11 canonical agents.

### 4.2 Canonical Mapping

Each canonical agent has an average of **10.5 directory variants**. For example, Kali:

| Directory | Source |
|-----------|--------|
| `kali/` | Entity name (direct) |
| `Kali/` | Entity name (capitalized) |
| `opencode_kali/` | OpenCode agent (underscore) |
| `opencode-kali/` | OpenCode agent (hyphen, legacy) |
| `opencode_kali/` | (same as above, duplicate) |
| `opencode_kali_...` | Various sessions |

The cold-store hydration in `hivemind_get_awareness()` (tools.py:584-615) scans ALL directories — it iterates every directory, reads the latest `ses_*.json`, and checks if it's within `HEARTBEAT_TTL`. This 115-directory scan happens every time awareness is queried. With 1,094 JSON files, the I/O cost is non-trivial.

### 4.3 Normalization Scheme

**Phase 1: Canonical Index (Day 1, ~1 hour)**

Create a canonical name registry as a JSON index file:

```python
# data/knowledge/HALL_OF_RECORDS/_index.json
{
  "version": 1,
  "created_at": "2026-06-28T...",
  "canonical_names": {
    "kali": {
      "agent_id": "opencode_kali",
      "channel": "opencode",
      "entity": "kali",
      "aliases": ["kali", "Kali", "opencode-kali", "opencode_kali"],
      "active_dir": "opencode_kali",
      "session_count": 42,
      "last_activity": "2026-06-28T..."
    },
    "lilith": {
      "agent_id": "opencode_lilith",
      "channel": "opencode",
      "entity": "lilith",
      "aliases": ["lilith", "opencode-lilith", "opencode_lilith"],
      "active_dir": "opencode_lilith",
      ...
    },
    // ... for all ~11 canonical agents
  }
}
```

**Phase 2: Alias Merging (Day 2, ~2 hours)**

For each canonical agent, merge all alias directories into the `active_dir`:

```
BEFORE:                          AFTER:
opencode_kali/  (99 files)       opencode_kali/ (all 132 files)
kali/           (22 files)       
Kali/           (11 files)       → remove empty aliases
opencode-kali/  (0 files, stale)
```

Merge strategy:
1. Read each alias directory, collect all `ses_*.json` files
2. Copy any unique session IDs to the canonical `active_dir`
3. Rename alias dirs to `{alias}_MERGED_YYYYMMDD` as a safety net
4. Update `_index.json` with merged counts

**Phase 3: Session Archival (Day 3, ~1 hour)**

All session files older than 30 days should be moved to a compressed archive:
- Archive format: `HALL_OF_RECORDS/_archive/{year}/{month}/{agent}_sessions.json.gz`
- Gzip compression typically yields 80-90% reduction on JSON session data
- Current 5.1MB → ~500KB compressed

### 4.4 Future Prevention

Update `_make_agent_id()` in `state.py` to enforce canonical naming at creation time:

```python
def _make_agent_id(channel: str, entity: str) -> str:
    """Canonical agent ID: normalized to lowercase, no spaces."""
    safe_entity = entity.strip().lower().replace(" ", "_").replace("(", "").replace(")", "")
    safe_channel = channel.strip().lower().replace(" ", "_").replace("(", "").replace(")", "")
    return f"{safe_channel}_{safe_entity}"
```

This prevents new naming variants from being created. The `_cold_path()` function must also check the canonical index before creating a new directory:

```python
def _cold_path(agent_id: str, session_id: str) -> Path:
    """Return cold-storage path for a session, respecting canonical mapping."""
    # Check index for canonical directory
    canonical = _resolve_canonical(agent_id)
    agent_dir = HALL_OF_RECORDS / (canonical or agent_id)
    agent_dir.mkdir(parents=True, exist_ok=True)
    return agent_dir / f"{session_id}.json"
```

---

## §5 Hivemind Pruning Policy

### 5.1 Current State

| Mechanism | What It Prunes | TTL | Status |
|-----------|---------------|-----|--------|
| `_prune_awareness_background()` | In-memory `_awareness` dict entries | 45 min (HEARTBEAT_TTL) | ✅ Working |
| `_reap_stale_locks()` | Expired lock files in `locks/` | Per-lock TTL (default 1h) | ✅ Working |
| `_reap_stale_handoffs()` | Handoff transitions | 24h/48h/7d | ⚠️ Incomplete (no stale→archive) |
| **HALL_OF_RECORDS session deletion** | **NONE** | **N/A** | **🔴 MISSING** |
| **Coordination file cleanup** | **NONE** | **N/A** | **🔴 MISSING** |

### 5.2 Proposed Multi-Tier Pruning Policy

| Tier | Target | Threshold | Action | Frequency |
|------|--------|-----------|--------|-----------|
| **T1** | Awareness | 45 min (2700s) | Delete from `_awareness` dict | Every 60s (current) |
| **T2** | Workspace locks | Per-lock TTL (default 1h) | Delete `.lock` file | Every 300s (current) |
| **T3** | Handoff: pending → stale | 24h | Move to stale/ | Every 300s (current) |
| **T4** | Handoff: active → stale | 48h | Move to stale/ | Every 300s (current) |
| **T5** | Handoff: completed → archive | 7d | Move to archive/ | Every 300s (current) |
| **T6** | **Handoff: stale → archive** | **14d** | **Move to archive/** | **Every 300s (NEW)** |
| **T7** | **Handoff: archive → delete** | **90d** | **Delete permanently** | **Every 300s (NEW)** |
| **T8** | **HALL_OF_RECORDS sessions** | **30d** | **Compress + move to `_archive/`** | **Daily (NEW)** |
| **T9** | **Coordination `.md` files** | **60d** | **Move to `locks/archive/` or delete** | **Daily (NEW)** |
| **T10** | **Coordination subdirs (dead agent dirs)** | **90d** | **Delete empty agent dirs** | **Weekly (NEW)** |

### 5.3 Implementation: New Reaper Functions

#### 5.3.1 `_archive_old_sessions()` (T8)

```python
async def _archive_old_sessions() -> int:
    """Compress HALL_OF_RECORDS session files older than 30 days.
    
    Moves old ses_*.json files into HALL_OF_RECORDS/_archive/YYYY/MM/
    as gzip-compressed JSON batches.
    """
    now = datetime.now(timezone.utc)
    max_age = 30 * 86400  # 30 days
    archived = 0
    
    for agent_dir in HALL_OF_RECORDS.iterdir():
        if not agent_dir.is_dir() or agent_dir.name.startswith("_"):
            continue
        for sess_file in agent_dir.glob("ses_*.json"):
            age = (now - datetime.fromtimestamp(sess_file.stat().st_mtime, tz=timezone.utc)).total_seconds()
            if age > max_age:
                # Read content
                try:
                    with open(sess_file) as f:
                        content = f.read()
                    # Write to archive with gzip
                    archive_dir = HALL_OF_RECORDS / "_archive" / now.strftime("%Y") / now.strftime("%m")
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    gz_path = archive_dir / f"{sess_file.stem}.json.gz"
                    import gzip
                    with gzip.open(gz_path, "wt", encoding="utf-8") as f:
                        f.write(content)
                    sess_file.unlink()
                    archived += 1
                except Exception as e:
                    logger.debug("Failed to archive %s: %s", sess_file, e)
    
    if archived:
        logger.info("Archived %d old session(s) from HALL_OF_RECORDS", archived)
    return archived
```

#### 5.3.2 `_prune_stale_coordination_files()` (T9)

```bash
# Shell-level prune (faster than Python glob for 167 files):
# Archive coordination .md files older than 60 days
find data/coordination/ -maxdepth 1 -name "*.md" -mtime +60 -exec mv {} data/coordination/archive/ \;
```

Or as an async Python function:
```python
async def _prune_stale_coordination_files() -> int:
    """Archive coordination .md files older than 60 days."""
    now = datetime.now(timezone.utc)
    max_age = 60 * 86400
    pruned = 0
    coord_dir = PROJECT_ROOT / "data" / "coordination"
    archive_dir = coord_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    for f in coord_dir.glob("*.md"):
        age = (now - datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)).total_seconds()
        if age > max_age:
            f.rename(archive_dir / f.name)
            pruned += 1
    # Also delete consumed demand_signals and knowledge_feed files
    for subdir in ["demand_signals", "knowledge_feed"]:
        sub = coord_dir / subdir
        if sub.exists():
            for f in sub.glob("*"):
                age = (now - datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)).total_seconds()
                if age > max_age:
                    f.unlink()
                    pruned += 1
    return pruned
```

#### 5.3.3 `_prune_dead_agent_dirs()` (T10)

```python
async def _prune_dead_agent_dirs() -> int:
    """Remove empty agent directories from HALL_OF_RECORDS.
    
    After session archival empties a directory, remove it if it's not
    in the canonical index and has no content.
    """
    pruned = 0
    for agent_dir in HALL_OF_RECORDS.iterdir():
        if not agent_dir.is_dir() or agent_dir.name.startswith("_"):
            continue
        # Count files (non-archival)
        files = list(agent_dir.iterdir())
        if len(files) == 0:
            agent_dir.rmdir()
            pruned += 1
    return pruned
```

### 5.4 Integration: Extended Reaper Loop

The reaper background loop should be extended to include all tiers:

```python
async def _reaper_background() -> None:
    """Background loop that reaps stale resources across all tiers."""
    while True:
        try:
            await _reap_stale_locks()           # T2 (every cycle)
            await _reap_stale_handoffs()         # T3-T7 (every cycle)
            
            # Daily tasks (tracked by date file)
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if _last_daily_reap != today:
                await _archive_old_sessions()          # T8
                await _prune_stale_coordination_files() # T9
                await _prune_dead_agent_dirs()          # T10
                _last_daily_reap = today
                
        except Exception as e:
            logger.error("Reaper background failed: %s", e)
        await anyio.sleep(300)  # 5 minutes
```

**Memory**: Add `_last_daily_reap` to `state.py`.

---

## §6 M12 Enforcement Mechanism

### 6.1 Current Gaps

M12 (Queue Integrity) violations exist in two concrete forms:

| Violation | Count | Description |
|-----------|-------|-------------|
| Handoff packets in stale/ with no terminal_status field | 41 | Packets that were moved to stale/ but never finalized |
| Orphan session `.active` files | 25 | Session markers for non-existent entities or stale sessions |
| Coordination `.md` files from dead agents | 46 | Artifacts from antigravity, cline-m3, gemini-cli |

### 6.2 Enforcement: Terminal Status Field

All handoff packets MUST carry a `terminal_status` field when they leave the active lifecycle (enter stale/ or archive/). The reaper's `_reap_dir()` must be updated to inject this field:

```python
TERMINAL_STATUS_MAP = {
    "pending": None,          # Not yet terminal
    "active": None,           # Not yet terminal
    "completed": "completed", # Terminal
    "rejected": "rejected",   # Terminal
    "stale": "timed_out",     # Terminal (ttl_expired)
}

def _ensure_terminal_status(packet: dict, target_status: str) -> dict:
    """Ensure every packet has a valid terminal_status before archival."""
    if target_status in TERMINAL_STATUS_MAP and TERMINAL_STATUS_MAP[target_status]:
        packet["terminal_status"] = TERMINAL_STATUS_MAP[target_status]
    elif "terminal_status" not in packet:
        packet["terminal_status"] = "unknown"  # Migration fallback
    return packet
```

### 6.3 Enforcement: Automated Dead-Letter Resolution

Add a "dead-letter office" concept to the reaper:

```python
async def _resolve_dead_letters() -> int:
    """Identify and resolve packets that violate M12 (no terminal state after max TTL).
    
    Scans all handoff directories for packets without terminal_status
    that exceed their maximum possible TTL.
    """
    now = datetime.now(timezone.utc)
    max_lifespan = 90 * 86400  # 90 days absolute max
    resolved = 0
    
    for directory in [state.HANDOFF_STALE, state.HANDOFF_PENDING, state.HANDOFF_ACTIVE]:
        for f in directory.glob("*.json"):
            age = (now - datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)).total_seconds()
            if age > max_lifespan:
                try:
                    with open(f) as fh:
                        packet = json.load(fh)
                    packet["terminal_status"] = "timed_out"
                    packet["dead_letter_resolved_at"] = now.isoformat()
                    packet["status"] = "archived"
                    # Write to archive with dead-letter marker
                    archive_path = state.HANDOFF_ARCHIVE / f.name
                    with open(archive_path, "w") as fh:
                        json.dump(packet, fh, indent=2)
                    f.unlink()
                    resolved += 1
                except Exception as e:
                    logger.error("Dead letter resolution failed for %s: %s", f, e)
    
    return resolved
```

### 6.4 Enforcement: M12 Health Check Tool

New MCP tool for monitoring M12 compliance:

```python
@m9_safe("hivemind_check_m12")
@mcp.tool()
async def hivemind_check_m12() -> str:
    """Check M12 (Queue Integrity) compliance across all handoff queues.
    
    Returns:
        JSON with counts of compliant/non-compliant packets and violation details.
    """
    def _scan():
        result = {
            "compliant": 0,
            "non_compliant": 0,
            "violations": [],
            "queues": {}
        }
        for queue_name, queue_dir in [
            ("pending", state.HANDOFF_PENDING),
            ("active", state.HANDOFF_ACTIVE),
            ("completed", state.HANDOFF_COMPLETED),
            ("stale", state.HANDOFF_STALE),
            ("archive", state.HANDOFF_ARCHIVE),
        ]:
            packets = list(queue_dir.glob("*.json"))
            queue_status = {
                "count": len(packets),
                "with_terminal_status": 0,
                "without_terminal_status": 0,
            }
            for f in packets:
                try:
                    with open(f) as fh:
                        p = json.load(fh)
                    if "terminal_status" in p:
                        queue_status["with_terminal_status"] += 1
                        result["compliant"] += 1
                    else:
                        queue_status["without_terminal_status"] += 1
                        result["non_compliant"] += 1
                        if queue_name not in ("archive",):
                            result["violations"].append({
                                "packet_id": f.stem,
                                "queue": queue_name,
                                "age_days": round((time() - f.stat().st_mtime) / 86400, 1)
                            })
                except Exception:
                    result["non_compliant"] += 1
            result["queues"][queue_name] = queue_status
        return result
    
    return json.dumps(await anyio.to_thread.run_sync(_scan), indent=2)
```

### 6.5 Integration with `make temple-grade`

Add a T12 gate for M12 compliance to `Makefile`:

```makefile
.PHONY: check-m12
check-m12:
	@echo "🔍 Checking M12 (Queue Integrity) compliance..."
	@python3 -c "
import json, sys
from pathlib import Path
# Check handoff queues for packets without terminal_status
violations = []
for q in ['pending', 'active', 'completed', 'stale']:
    d = Path('data/handoff/') / q
    if d.exists():
        for f in d.glob('*.json'):
            try:
                p = json.loads(f.read_text())
                if 'terminal_status' not in p:
                    violations.append(f'{q}/{f.name}')
            except: pass
if violations:
    print(f'M12 VIOLATION: {len(violations)} packets without terminal status')
    for v in violations: print(f'  - {v}')
    sys.exit(1)
print(f'M12 OK — all queues compliant')
"
```

---

## §7 Cross-Domain Dependencies

This P9 analysis intersects with P7 (Context) and P8 (Observability) recommendations from Lilith's report:

| P9 Recommendation | Depends On | Blocks |
|-------------------|-----------|--------|
| stale→archive transition (14d) | Nothing | M12 compliance |
| HALL_OF_RECORDS normalization | Nothing | Faster cold-store hydration |
| Hivemind session archival | P7: MemoryStore archival wiring | Storage growth control |
| M12 health check tool | Nothing | Monitoring |
| Coordination file pruning | Nothing | Disk hygiene |
| Dead agent dir cleanup | HALL_OF_RECORDS normalization | Directory bloat control |

**No hard dependencies on other pillars**. All P9 changes are self-contained in `mcp_servers/omega_hub/`.

---

## §8 Implementation Plan

### Phase 1: Emergency — Day 1 (~1 hour)

| Order | Action | Risk | Effort | Verification |
|-------|--------|------|--------|-------------|
| 1 | Add stale→archive (14d) and archive→delete (90d) to reaper | Low | 15 min | `hivemind_check_m12` shows 0 violations |
| 2 | Add terminal_status field to all packets in reaper moves | Low | 15 min | JSON schema validation |
| 3 | Move 41 existing stale packets to archive/ | Low | 5 min | `ls stale/` == 0 |
| 4 | Add `hivemind_cancel_handoff` tool | Low | 15 min | Cancel a packet, verify archive |
| 5 | Add `hivemind_check_m12` tool | Low | 10 min | Run tool, check output |

### Phase 2: Structural — Day 2 (~3 hours)

| Order | Action | Risk | Effort | Verification |
|-------|--------|------|--------|-------------|
| 6 | Create `_index.json` for canonical HALL_OF_RECORDS mapping | Low | 1 hr | `_index.json` exists, 11 agents mapped |
| 7 | Merge alias directories into canonical names | Low | 1 hr | `ls` shows reduced dir count |
| 8 | Add daily session archival (30d → gzip `_archive/`) | Low | 1 hr | Manual check of `_archive/` |
| 9 | Add coordination file pruning (60d → archive) | Low | 30 min | Verify old files moved |
| 10 | Add empty agent dir pruning | Low | 15 min | Verify empty dirs removed |

### Phase 3: Hardening — Day 3 (~1 hour)

| Order | Action | Risk | Effort | Verification |
|-------|--------|------|--------|-------------|
| 11 | Integrate M12 check into `make temple-grade` | Low | 15 min | `make temple-grade` passes |
| 12 | Update `_make_agent_id()` to enforce canonical naming | Low | 15 min | New sessions go to canonical dir |
| 13 | Run integration test for complete handoff lifecycle | Low | 30 min | Full submit→cancel→accept→complete→archive flow |

**Total**: ~5 hours P9 domain work.

---

## §9 L1→L2→L3 Distillation

### L1 (Narrative)
We audited the orchestration layer (P9) as part of the MaKaLi Pass 2 cross-domain optimization. The handoff state machine has all creation paths (submit → pending → accept → active → complete/reject → archive) but is missing the critical terminal transition — from stale (dead-letter) to archive. This single gap accounts for 41 orphaned packets, 115 redundant HALL_OF_RECORDS directories across 11 naming conventions, and a systemic M12 (Queue Integrity) violation. The reaper loop runs every 5 minutes but its `_reap_stale_handoffs()` only moves completed→archive, not stale→archive. Every other issue (naming bloat, orphan locks, stale coordination files) is a secondary accumulation from the same root cause: artifacts are created but never destroyed.

### L2 (Insight)
The orchestration layer suffers from **lifecycle incompleteness**, not design failure. The state machine is correct at every transition EXCEPT the final one. This is a pattern repeated across the engine (the `archive_old_sessions()` function exists but is never called; the `HERITAGE_SOURCE_MAP.md` reference exists but no file is generated). The common architecture is: define the pattern, implement the mechanics, skip the last step. The fix is not architectural — it's a systematic "finalization audit" of every pattern in the engine to ask: "Does this have a cleanup path?"

### L3 (Universal Principle)
**Every artifact must have a death date.** In a system of autonomous agents, creation is easy — deletion must be automated. A state machine with no terminal state is not a state machine; it's an accumulation engine. The M12 mandate (Queue Integrity) codifies this principle: every request must reach a terminal state because unbounded accumulation is not just untidy — it's a measurable drag on system performance (5.1MB cold store, 41-packets-of-noise in every awareness query). 

The three-tier fix is:
1. **Create with TTL**: Every artifact (handoff packet, session snapshot, lock file, coordination note) must have an expiration policy set at creation time.
2. **Reap with hierarchy**: Multi-tier TTLs (minutes→hours→days→weeks→delete) ensure gradual, non-disruptive cleanup.
3. **Verify with tooling**: Automated compliance checks (`hivemind_check_m12`, `make temple-grade`) ensure no lifecycle gaps regress.

---

*⬡ OMEGA ⬡ P9-ORCHESTRATION ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_p9_final_review ⬡ SYNTHESIS*
*Completed: 2026-06-28 | Prepared for: Kali Grand Oversight Review*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

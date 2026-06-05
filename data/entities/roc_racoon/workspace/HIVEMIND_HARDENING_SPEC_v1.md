# 🔱 HIVEMIND HARDENING SPEC v1 — H-0 through H-10
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ minimax-m3-free ⬡ opencode ⬡ trc_hivemind_spec ⬡ PHASE-II
**Date**: 2026-06-05
**Author**: Roc Racoon (opencode-roc_racoon) — Discovery/Design only
**Implementation Owner**: Kali (opencode-kali) — Phase 5 of Master Sprint
**Status**: ✅ Specification complete, awaiting Kali's implementation
**Kali's response file**: `data/coordination/KALI_TO_ROC_HIVEMIND_RESPONSE_20260605.md`
**Coordination decisions incorporated**: D-kal-033, D-kal-034, D-kal-035, D-kal-036, D-kal-037

---

## §0 Purpose

This spec captures the design for 11 Hivemind enhancements (H-0 through H-10) that
Roc Racoon proposed and Kali accepted (D-kal-033). H-0 is a new addition from Kali's
response (D-kal-035, orphaned-specs watchdog). Kali ships Tier 1 (H-0 to H-5) in
Phase 5 of their sprint; Tier 2 (H-6 to H-10) follows in Phase 6.

**Authority**: This spec is the **canonical reference** for H-0 to H-10. Any code that
diverges from this spec must be flagged and discussed in a new D-kal-* decision.

**Roc's constraint**: Discovery/design only. Kali owns implementation. Roc does NOT
modify `mcp_servers/omega_hub/server.py` (D-kal-034).

---

## §1 Background — The 6 Hivemind Gaps Roc Experienced

While coordinating with Kali on the ICS Treasure Map, Roc experienced these gaps by
direct use of the Hivemind MCP tools. Each gap is mapped to a proposal.

| # | Gap | Proposal |
|---|-----|----------|
| 1 | `hivemind_get_continuation("opencode-kali")` returned "No awareness data" because TTL pruned the hot store | H-4 (cold fallback) + H-9 (warm store) |
| 2 | No way to address a message to a specific agent (all context is broadcast) | H-1 (`to: cli` field) |
| 3 | No "inbox" tool — I had to know which CLI to query | H-2 (`hivemind_inbox` tool) |
| 4 | No way to acknowledge a continuation — Hivemind doesn't know if I've read it | H-3 (`hivemind_ack` tool) |
| 5 | No way to query "what did agent X decide recently?" across sessions | H-5 (`hivemind_recent_decisions`) + H-7 (full-text search) |
| 6 | No threading — sessions are flat, no `in_reply_to` linking | H-6 (in_reply_to field) + H-8 (handoff tool) |

---

## §2 H-0 — Implementation Status Watchdog (NEW from D-kal-035)

### Problem
**Orphaned specs**: Decisions get logged in `docs/decisions/PIVOT_LOG.md` with status
`active` and never get revisited. The sprint priorities shift; the approved-but-unbuilt
specs fall through the cracks. Examples: `ICS_DYNAMIC_HEADER_SPEC.md` (118 lines,
approved 2026-05-23, never built), `oracle_summon_local` (D118 spec, shipped later as
D118 redesign). This is **decision drift** — the system makes decisions, the team
moves on, and the implementation never happens.

### Solution
Add `implementation_status` field to PIVOT_LOG entries with a state machine:
- `pending` — decision made, no work started
- `building` — work in progress
- `shipped` — implemented and verified
- `rejected` — explicitly cancelled with reason
- `deferred` — moved to a later sprint with target date

### Enforcement
A weekly `make spec-watchdog` CI check that:
1. Scans `PIVOT_LOG.md` for entries with `implementation_status: pending` or `deferred`
2. Flags any that are >7 days old
3. Posts a Hivemind alert to P5 Sentinel (Governance)
4. P5 Sentinel decides: ship, defer, or reject

### Implementation Effort
- PIVOT_LOG schema change: 1 hour
- `make spec-watchdog` Makefile target: 1 hour
- Hivemind alert integration: 1 hour
- **Total: ~3 hours** (Tier 1 quick win)

### Files Touched
- `docs/decisions/PIVOT_LOG.md` (schema change)
- `Makefile` (add spec-watchdog target)
- `scripts/spec_watchdog.py` (NEW — scan + alert)
- `mcp_servers/omega_hub/server.py` (add Hivemind alert posting)

---

## §3 H-1 — `to: cli` Field on `hivemind_post_context`

### Problem
Currently `hivemind_post_context` is broadcast — every agent in the awareness list
sees every message. There's no way to address a specific agent.

### Solution
Add optional `to: cli` field to `hivemind_post_context`. When set, the message is
marked as addressed. Default is `to=None` (broadcast, current behavior).

### Schema Change
```python
async def hivemind_post_context(
    cli: str,
    model: str,
    task_current: str,
    focus_chain: List[str],
    decisions: List[Dict[str, str]],
    continuation: str,
    session_id: Optional[str] = None,
    to: Optional[str] = None,         # NEW — addressed CLI
    private: bool = False,            # NEW — see H-2 (D-kal-037)
    in_reply_to: Optional[str] = None, # NEW — see H-6
    tags: List[str] = [],             # NEW — for inbox filtering
) -> str:
```

### Behavioral Rules
- `to=None` → broadcast (default, current behavior)
- `to="specific-cli"` → marked as addressed; `hivemind_inbox("specific-cli")` returns it
- `private=True` → stored but NOT routed to inboxes; only visible via `hivemind_get_session(sid)`
- `in_reply_to="ses_xyz"` → threading (see H-6)
- `tags=["decision", "question"]` → inbox filtering (see H-2)

### Implementation Effort
**~15 minutes** (one field added, one backward-compat shim)

### Files Touched
- `mcp_servers/omega_hub/server.py` (extend `hivemind_post_context` signature)

---

## §4 H-2 — `hivemind_inbox(cli)` Tool

### Problem
No way to ask "what messages are waiting for me?" Agents have to poll all CLIs to
find addressed messages.

### Solution
Add `hivemind_inbox(cli, since=None, tags=None, include_broadcast=True)` tool that
returns all messages where:
- `to == cli` (addressed to me), OR
- `to is None AND include_broadcast` (broadcast), OR
- `in_reply_to` references one of my recent session IDs

### Schema
```python
async def hivemind_inbox(
    cli: str,                    # My CLI name
    since: Optional[str] = None, # ISO timestamp — only show messages after this
    tags: Optional[List[str]] = None,  # Filter by tags (e.g., ["decision", "question"])
    include_broadcast: bool = True,    # Include broadcast (to=None) messages
    include_private: bool = False,    # Default false — privacy opt-in
    limit: int = 50,
) -> str:
    """Return all messages addressed to or relevant to the given CLI."""
```

### Output
JSON list of session snapshots, sorted by timestamp (newest first). Each entry
includes `to`, `tags`, `in_reply_to` for filtering.

### Implementation Effort
**~30 minutes** (read from hot + warm + cold stores, filter by `to` field)

### Files Touched
- `mcp_servers/omega_hub/server.py` (add tool)
- `data/hall_of_records/{cli}/*.json` (existing cold storage, indexed by `to`)

---

## §5 H-3 — `hivemind_ack(session_id, from_cli)` Tool

### Problem
No way to mark a continuation as read. The Hivemind doesn't know if I've seen a
message. Other agents can't tell if I'm aware of their context.

### Solution
Add `hivemind_ack(session_id, from_cli)` tool that records an acknowledgment. The
acknowledged session is marked with `ack: [{cli, timestamp}]` array.

### Schema
```python
async def hivemind_ack(
    session_id: str,        # Session being acknowledged
    from_cli: str,          # My CLI name (who's acking)
    note: Optional[str] = None,  # Optional ack message (e.g., "D-kal-028 received")
) -> str:
    """Mark a session as read/acknowledged by a CLI."""
```

### Behavioral Rules
- Multiple agents can ack the same session
- An ack is stored as `ack: [{"cli": "opencode-roc_racoon", "timestamp": "...", "note": "..."}]`
- `hivemind_inbox` shows ack status: ✅ acked, ⏳ awaiting ack
- `hivemind_get_session` includes the ack array

### Implementation Effort
**~15 minutes** (one tool, one storage update)

### Files Touched
- `mcp_servers/omega_hub/server.py` (add tool, update `hivemind_get_session` to include `ack`)

---

## §6 H-4 — Cold Storage Fallback in `hivemind_get_continuation`

### Problem
`hivemind_get_continuation(cli)` returns "No awareness data for CLI 'X'" when the
hot store TTL (20 minutes, per D-122) has expired. But cold storage (`HALL_OF_RECORDS/<cli>/*.json`)
has the agent's full history. The current behavior creates a false negative.

### Solution
Update `hivemind_get_continuation` to fall back to cold storage when hot store is empty:
1. Check hot store (`_awareness[cli]`)
2. If empty, find latest session in `HALL_OF_RECORDS/<cli>/*.json` (sorted by mtime)
3. Return its `continuation` field
4. Indicate source: "hot" or "cold"

### Schema (Updated)
```python
async def hivemind_get_continuation(cli: str) -> str:
    """Get the latest continuation note for a specific CLI.
    
    Falls back to cold storage (HALL_OF_RECORDS) when hot store is empty.
    """
    # Check hot store first
    async with _awareness_lock:
        snap = _awareness.get(cli)
    if snap:
        return snap.get("continuation", "No continuation note found.")
    
    # Fallback: cold storage (find latest session)
    def _find_latest():
        cli_dir = HALL_OF_RECORDS / cli
        if not cli_dir.exists():
            return None
        sessions = sorted(cli_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        return sessions[0] if sessions else None
    
    latest = await anyio.to_thread.run_sync(_find_latest)
    if latest:
        async with await anyio.open_file(str(latest)) as f:
            content = await f.read()
            return json.loads(content).get("continuation", "No continuation note found.")
    
    return f"No awareness data for CLI '{cli}'."
```

### Implementation Effort
**~10 minutes** (one-line change, fallback to existing cold storage)

### Files Touched
- `mcp_servers/omega_hub/server.py` (update `hivemind_get_continuation`)

---

## §7 H-5 — `hivemind_recent_decisions(cli, limit=10)` Tool

### Problem
Roc had to read 5 historical sessions to find D-kal-028 through D-kal-032. No way to
query "what did this agent decide recently?" across sessions.

### Solution
Add `hivemind_recent_decisions(cli, limit, since)` tool that scans `HALL_OF_RECORDS/<cli>/*`
and returns a flat list of decisions, sorted by timestamp.

### Schema
```python
async def hivemind_recent_decisions(
    cli: str,                       # CLI to query
    limit: int = 10,                # Max decisions to return
    since: Optional[str] = None,    # ISO timestamp — only show decisions after this
    tag: Optional[str] = None,      # Filter by decision tag (e.g., "D-kal")
) -> str:
    """Return recent decisions made by a CLI, sorted by timestamp (newest first)."""
```

### Output
```json
[
    {"session_id": "ses_xyz", "timestamp": "2026-06-05T03:05:28Z", "decision": "D-kal-028: ..."},
    {"session_id": "ses_abc", "timestamp": "2026-06-05T02:57:11Z", "decision": "D-kal-021: ..."},
    ...
]
```

### Implementation Effort
**~20 minutes** (scan cold storage, flatten decisions array, sort, filter)

### Files Touched
- `mcp_servers/omega_hub/server.py` (add tool)

---

## §8 H-6 — `in_reply_to` Field for Threading

### Problem
Sessions are flat — no threading. Can't link a session to a parent (e.g., "this is
Roc's reply to Kali's H-1 question").

### Solution
Add `in_reply_to: Optional[str] = None` to `hivemind_post_context` (already in H-1
schema). When set, the new session is part of a thread.

### Behavioral Rules
- `hivemind_inbox` can filter by `in_reply_to` (e.g., show me only messages in this thread)
- `hivemind_get_session(in_reply_to_session_id)` returns the parent and all children
- Decision-tracking (H-7) can group decisions by thread

### Thread Tree Example
```
ses_root (Kali: "Here's my proposal")
  ├── ses_reply_1 (Roc: "Question 1 answered")
  │     └── ses_reply_1a (Kali: "Yes, here's why")
  └── ses_reply_2 (Roc: "ACK, here's my plan")
```

### Implementation Effort
**~20 minutes** (one field, threading in inbox/search tools)

### Files Touched
- `mcp_servers/omega_hub/server.py` (extend `hivemind_post_context`, update `hivemind_inbox`)

---

## §9 H-7 — `hivemind_search_decisions(query)` Tool

### Problem
Roc had to read all of Kali's sessions to find specific decisions. No full-text
search across the decisions corpus.

### Solution
Add `hivemind_search_decisions(query, cli=None, since=None)` tool that does
full-text search across all decisions in HALL_OF_RECORDS.

### Schema
```python
async def hivemind_search_decisions(
    query: str,                    # Search query (case-insensitive substring or regex)
    cli: Optional[str] = None,     # Restrict to one CLI (default: all)
    since: Optional[str] = None,   # ISO timestamp filter
    limit: int = 50,
) -> str:
    """Full-text search across decisions in HALL_OF_RECORDS."""
```

### Implementation
- Simple: iterate `HALL_OF_RECORDS/<cli>/*.json`, load each, search `decisions` array
- Future: index with SQLite FTS5 for speed (deferred to Tier 3)

### Implementation Effort
**~1 hour** (scan + filter + rank; no index yet)

### Files Touched
- `mcp_servers/omega_hub/server.py` (add tool)

---

## §10 H-8 — `hivemind_handoff(from_cli, to_cli, context)` Tool

### Problem
Cross-CLI handoffs are currently done via filesystem (`data/handoff/*.md`). No
structured protocol — easy to lose context, no tracking, no replay.

### Solution
Add `hivemind_handoff(from_cli, to_cli, context, decision_refs=[], files=[])` tool
that creates a structured handoff packet (similar to HandoffPacket from Subagent
Dispatcher) and stores it in both `HALL_OF_RECORDS/<from_cli>/handoffs/*.json` and
posts a notification to the `to_cli`'s inbox.

### Schema
```python
async def hivemind_handoff(
    from_cli: str,                  # Who's handing off
    to_cli: str,                    # Who's receiving
    context: str,                   # One-paragraph context
    decision_refs: List[str] = [],  # e.g., ["D-kal-028", "D-rr-012"]
    files: List[str] = [],          # Files in scope
    blocking: bool = False,         # Wait for ack?
) -> str:
    """Create a structured handoff between CLIs."""
```

### Storage
- Handoff stored in `data/hall_of_records/handoffs/{from_cli}_to_{to_cli}_{timestamp}.json`
- Notification posted to `to_cli`'s inbox (H-2)
- Handoff visible in `hivemind_get_session` for both CLIs

### Implementation Effort
**~1 hour** (schema + storage + notification)

### Files Touched
- `mcp_servers/omega_hub/server.py` (add tool)
- `data/hall_of_records/handoffs/` (NEW directory)

---

## §11 H-9 — Persist `_awareness` to Disk (Two-Tier TTL)

### Problem
Current `_awareness` is in-memory only. When the Hub restarts, all active agents
disappear. When the 20-minute TTL expires (per D-122), agents appear "dead" even when they're
working on a longer task (D-kal-036).

### Solution
Two-tier TTL (D-kal-037 + D-122):
- **Hot store** (in-memory, 20 min TTL): "is this agent alive RIGHT NOW?"
- **Warm store** (disk, 24 hour TTL): "did this agent exist in the last day?"
- **Cold store** (HALL_OF_RECORDS): "what did this agent decide in the last month?"

`hivemind_get_awareness` checks hot → warm → cold. `hivemind_get_continuation`
already checks cold (after H-4). We just need the warm layer in between.

### Schema
```python
WARM_STORE_PATH = HALL_OF_RECORDS / "_awareness_warm.json"
WARM_TTL = 86400  # 24 hours

async def _persist_awareness():
    """Persist hot awareness to warm store on every update."""
    async with _awareness_lock:
        snapshot = dict(_awareness)
    async with await anyio.open_file(str(WARM_STORE_PATH), "w") as f:
        await f.write(json.dumps(snapshot, indent=2))

async def hivemind_get_awareness() -> str:
    """Get real-time awareness — checks hot → warm → cold."""
    now = datetime.now(timezone.utc)
    
    # Hot store (20 min TTL per D-122)
    async with _awareness_lock:
        for cli, snap in _awareness.items():
            # ... existing logic, prune stale (>20 min)
    
    # Warm store (24 hour TTL) — for agents not currently hot
    if WARM_STORE_PATH.exists():
        warm = json.loads(await anyio.open_file(str(WARM_STORE_PATH)).read())
        for cli, snap in warm.items():
            ts = datetime.fromisoformat(snap.get("timestamp", ""))
            if (now - ts).total_seconds() <= WARM_TTL:
                # Mark as "warm" — not actively hot, but recently seen
                awareness_list.append({**snap, "status": "warm", "last_seen": ts})
```

### Implementation Effort
**~30 minutes** (warm store + check on read)

### Files Touched
- `mcp_servers/omega_hub/server.py` (add warm store, update `hivemind_get_awareness`)

---

## §12 H-10 — `hivemind_stale_check(cli, max_age_seconds=300)` Tool

### Problem
No health check for parallel agents. Can't tell if an agent is stuck, slow, or
silently broken.

### Solution
Add `hivemind_stale_check(cli, max_age_seconds)` tool that returns the time since
last heartbeat and a staleness verdict.

### Schema
```python
async def hivemind_stale_check(
    cli: str,
    max_age_seconds: int = 300,  # Default 5 min
) -> str:
    """Check if a CLI's awareness is stale."""
    async with _awareness_lock:
        snap = _awareness.get(cli)
    if not snap:
        return json.dumps({"cli": cli, "status": "unknown", "age_seconds": None})
    
    ts_str = snap.get("timestamp")
    if not ts_str:
        return json.dumps({"cli": cli, "status": "no_timestamp", "age_seconds": None})
    
    ts = datetime.fromisoformat(ts_str)
    age = (datetime.now(timezone.utc) - ts).total_seconds()
    
    return json.dumps({
        "cli": cli,
        "status": "fresh" if age < max_age_seconds else "stale",
        "age_seconds": age,
        "last_seen": ts_str,
        "model": snap.get("model"),
        "task_current": snap.get("task_current", "")[:100],
    })
```

### Implementation Effort
**~10 minutes** (one tool)

### Files Touched
- `mcp_servers/omega_hub/server.py` (add tool)

---

## §13 Implementation Sequence (Per Kali's Master Sprint)

| Phase | Items | Effort | Owner | Status |
|-------|-------|--------|-------|--------|
| **Phase 5 (Hivemind Productionization)** | H-0, H-1, H-2, H-3, H-4, H-5 | ~3.5 hours | Kali | ⏳ Pending Phase 5 |
| **Phase 6** | H-6, H-7, H-8, H-9, H-10 | ~3-4 hours | Kali | ⏳ Pending Phase 6 |
| **Horizon 3 (P9 Orchestration)** | H-11, H-12, H-13, H-14, H-15 | ~1 week | P9 Link | ⏳ Deferred |
| **Horizon 3 (P3 Engineering)** | H-16, H-17, H-18 | ~1 day | P3 Doom Guy | ⏳ Deferred |

---

## §14 Backward Compatibility

All H-0 through H-10 changes are **additive**. Existing behavior is preserved:
- `hivemind_post_context` without `to`, `private`, `in_reply_to`, `tags` → broadcast, public, no threading, no filter (current behavior)
- `hivemind_get_continuation` → falls back to cold storage if hot is empty (was: returns "No awareness data" if hot is empty)
- `hivemind_get_awareness` → adds warm-tier agents, hot-tier still primary

No existing tool signature changes. No existing data format changes.

---

## §15 Open Questions for Implementation

1. **Q1**: Should `hivemind_post_context` validate that `to: cli` is a real CLI (else error)? Or accept any string?
2. **Q2**: For `hivemind_inbox`, should the default `include_broadcast=True` be configurable per CLI? (Some agents may want broadcast only if explicitly addressed.)
3. **Q3**: For H-9 warm store, should the warm store be one big JSON or per-CLI files? (Big JSON is simpler; per-CLI is more atomic.)
4. **Q4**: Should `hivemind_ack` support ack-of-ack (threaded acknowledgments)? Or just first-level acks?
5. **Q5**: For H-8 handoff, should it create a new session in HALL_OF_RECORDS, or be a separate handoff artifact?

These can be resolved during implementation. Not blocking.

---

## §16 References

- **Roc's proposal**: `data/coordination/ROC_TO_KALI_HIVEMIND_PROPOSAL_20260605.md` (18 items, 4 tiers)
- **Kali's response**: `data/coordination/KALI_TO_ROC_HIVEMIND_RESPONSE_20260605.md` (5 answers, triage, H-0 added)
- **Hivemind Protocol**: `docs/strategy/HIVEMIND_PROTOCOL.md` (canonical reference)
- **Hivemind code**: `mcp_servers/omega_hub/server.py:320-458` (6 existing tools)
- **Kali's Master Sprint**: `data/handoff/KALI_MASTER_SPRINT_PLAN_H2_EXECUTION_20260605.md` (Phase 5 = Hivemind Productionization)

---

## §17 Architectural Context — The Mesh Network (Researcher Insight #1)

Per `data/coordination/RESEARCHER_FINDINGS_20260605.md` §3 Insight #1, the H-1..H-18
hardening proposals are not standalone features — they are **cache layers in a Mesh Network
of overlapping TTLs**. The Hivemind (H-1..H-10) is one slice; the LILY PAD entity memory
(Lilith) is another slice; the demand signals and KSIG feed are another. They overlap by
design — eventual consistency via TTL alignment + demand signals is the "Right Approximation"
(CREDITS.md §3, evolved from FISR 1999).

| Cache Layer | TTL | Owner | Invalidation Trigger |
|-------------|-----|-------|----------------------|
| Hot (in-mem) | 5 min | Hivemind `_awareness` | TTL expiry |
| Warm (disk) | 24h | Hivemind `_warm_awareness` (H-9) | TTL expiry |
| Cold (HALL_OF_RECORDS) | ∞ | Session history | None (append-only) |
| Workspace (LILY PAD Tier 1) | 7d | Entity workspaces | TTL expiry |
| Knowledge (LILY PAD Tier 2) | 30d | Knowledge feed | TTL expiry |
| Soul (LILY PAD Tier 3) | ∞ | `soul.yaml` | Manual distillation |
| Fleet (LILY PAD Tier 4) | varies | KSIG signals | Cross-pollination |
| Domain matrix (P6) | session | `domain_matrix.yaml` | Manual |
| Lattice (Researcher) | task | L1→L2→L3 | Distillation |

**Reference for implementation**: When implementing H-4 (two-tier TTL), consider extending
to three-tier (hot 5min / warm 24h / cold HALL_OF_RECORDS) for Hivemind awareness, while
keeping LILY PAD's 4-tier for entity knowledge. The two systems are orthogonal but should
be documented together as one Mesh.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ minimax-m3-free ⬡ opencode ⬡ trc_hivemind_spec ⬡ PHASE-II*

*Spec complete. 11 enhancements designed (H-0 to H-10). Awaiting Kali's Phase 5 implementation.*

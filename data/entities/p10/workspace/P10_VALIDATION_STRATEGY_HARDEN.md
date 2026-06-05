# 🔱 P10 Validation — Hivemind Coordination System Validation Strategy
# ⬡ OMEGA ⬡ P10 (Verifier) ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_pillar_p10 ⬡ PHASE-I
**AP Token**: `AP-P10-HIVEMIND-VALIDATION-v1.0.0`
**Date**: 2026-06-05
**Status**: STRATEGIC ANALYSIS
**Baseline**: Hivemind has been used ~3 times (Kali↔Roc dialog, Lilith intro, current session).
**Current test coverage for Hivemind**: **ZERO** — no `test_hivemind_*.py` files exist anywhere in the test suite.
**Cross-Reference**:
- `docs/strategy/HIVEMIND_PROTOCOL.md` — The base protocol (v1.2.0)
- `docs/strategy/HIVEMIND_OBSERVATIONS_PROTOCOL.md` — D-121 observation mandate
- `data/coordination/ROC_TO_KALI_HIVEMIND_PROPOSAL_20260605.md` — Roc's 18 hardening proposals
- `data/coordination/KALI_TO_ROC_HIVEMIND_RESPONSE_20260605.md` — Kali's triage answers
- `data/coordination/HIVEMIND_OBSERVATIONS_LOG.md` — Fleet observation log (5 entries)
- `mcp_servers/omega_hub/server.py` — Hivemind MCP tools (6 tools, lines 330-465)
- `CREDITS.md` §1.x — id Software heritage mapping
- `Makefile` — Current Makefile has NO `hivemind-*` targets
- `tests/sovereign_stress_test.py` — Existing stress test patterns (reference)
- `tests/test_error_gauntlet.py` — Existing error provocation patterns (reference)

---

## Table of Contents

1. [Testing Strategy](#1-testing-strategy)
2. [Chaos Engineering](#2-chaos-engineering)
3. [Verification Gates](#3-verification-gates)
4. [Failure Mode Catalog](#4-failure-mode-catalog)
5. [Recovery Procedures](#5-recovery-procedures)
6. [Heritage Cross-Reference](#6-heritage-cross-reference)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Appendix: Test File Templates](#8-appendix-test-file-templates)

---

## §1 Testing Strategy

### §1.1 What Does It Mean to "Test the Hivemind"?

The Hivemind is a **live coordination protocol** implemented as 6 MCP tools backed by in-memory dictionaries (`_awareness`, `_hot_store`) with cold storage to `data/knowledge/HALL_OF_RECORDS/`. It is **not a standard CRUD service** — it mediates real-time agent awareness, and its correctness depends on:

1. **State consistency** — `hivemind_post_context` writes to 3 stores (hot, awareness, cold) atomically
2. **Reachability** — A posted context is discoverable via awareness, session lookup, and cold path
3. **TTL correctness** — Agents expire at the right time, no earlier and no later
4. **Concurrency safety** — AnyIO locks prevent corruption under parallel access
5. **Cold path integrity** — Disk writes survive hub restarts
6. **Observability** — Every Hivemind interaction can be traced and validated

**Key insight**: The Hivemind is the **first multi-agent protocol** in the Omega Engine. Testing it is not just about function correctness — it's about **protocol correctness**. The right question is not "did the function return the right value?" but "did the coordination complete as expected?"

### §1.2 Testing Taxonomy (5-Level Pyramid)

```
                    ╱╲
                   ╱  ╲          SCENARIO TESTS
                  ╱    ╲         Full 9-step protocol
                 ╱ SCE  ╲       End-to-end workflows
                ╱────────╲
               ╱          ╲     CHAOS TESTS
              ╱  CHAOS     ╲   Network partition, Redis failure,
             ╱             ╲  agent crash, memory exhaustion
            ╱───────────────╲
           ╱                 ╲  STRESS TESTS
          ╱   STRESS          ╲ 10+ agents, rapid heartbeat,
         ╱                    ╲ large payloads, concurrency
        ╱──────────────────────╲
       ╱                        ╲ INTEGRATION TESTS
      ╱   INTEGRATION            ╲ 2-agent awareness->post->
     ╱                           ╲ read->ack->completion
    ╱─────────────────────────────╲
   ╱                               ╲ UNIT TESTS
  ╱        UNIT                     ╲ Each MCP tool in isolation
 ╱                                   ╲ Mock _hot_store, _awareness
╱─────────────────────────────────────╲
```

#### Level 1: Unit Tests (Isolation — ~20 tests, ~5ms each)

Test each MCP tool in isolation, mocking both `_hot_store` and `_awareness` as plain dicts (or using `anyio.Lock` test helpers).

| Test ID | Name | What It Verifies | Tool Under Test |
|---------|------|------------------|-----------------|
| U-001 | `post_context_accepts_valid_params` | Valid params produce accepted response with session_id | `hivemind_post_context` |
| U-002 | `post_context_empty_params` | Empty strings for required fields return error | `hivemind_post_context` |
| U-003 | `post_context_writes_all_stores` | Session appears in `_hot_store`, `_awareness`, AND cold path | `hivemind_post_context` |
| U-004 | `heartbeat_registers_new_cli` | Unknown CLI creates a heartbeat-only presence entry | `hivemind_heartbeat` |
| U-005 | `heartbeat_updates_existing` | Known CLI's timestamp advances on heartbeat | `hivemind_heartbeat` |
| U-006 | `get_awareness_returns_all_active` | All non-stale agents returned with expected fields | `hivemind_get_awareness` |
| U-007 | `get_awareness_prunes_stale` | Agent past HEARTBEAT_TTL excluded from output | `hivemind_get_awareness` |
| U-008 | `get_awareness_heartbeat_only` | Agents registered via heartbeat-only appear with model="unknown" | `hivemind_get_awareness` |
| U-009 | `get_continuation_existing_cli` | Returns continuation field from awareness snapshot | `hivemind_get_continuation` |
| U-010 | `get_continuation_missing_cli` | Returns "No awareness data" for unknown CLI | `hivemind_get_continuation` |
| U-011 | `get_session_hot_store` | Returns full snapshot for in-memory session | `hivemind_get_session` |
| U-012 | `get_session_cold_store` | Falls back to HALL_OF_RECORDS and returns snapshot | `hivemind_get_session` |
| U-013 | `get_session_not_found` | Returns error JSON for nonexistent session | `hivemind_get_session` |
| U-014 | `list_sessions_filtered` | Returns only sessions for specified CLI | `hivemind_list_sessions` |
| U-015 | `list_sessions_unfiltered` | Returns sessions from all CLIs | `hivemind_list_sessions` |
| U-016 | `list_sessions_cli_not_found` | Empty list for unknown CLI | `hivemind_list_sessions` |
| U-017 | `prune_background_single_stale` | One stale agent removed after TTL | `_prune_awareness_background` |
| U-018 | `prune_background_all_active` | No agents removed when all within TTL | `_prune_awareness_background` |
| U-019 | `post_context_preserves_existing` | Posting two sessions for same CLI: both in hot_store, awareness has latest | `hivemind_post_context` |
| U-020 | `cold_path_filename_safety` | Special chars in CLI and session_id are sanitized | `_cold_path` |

**Unit test patterns** (from existing `test_error_gauntlet.py`, style to follow):

```python
# U-001: Post context accepted
@pytest.mark.anyio
async def test_post_context_valid():
    hub = HivemindTestHarness()  # in-memory mock store
    result = await hub.post_context(
        cli="opencode-test",
        model="qwen3-1.7b",
        task_current="Testing Hivemind",
        focus_chain=["Step 1"],
        decisions=[{"text": "Test decision"}],
        continuation="Test continuation",
    )
    parsed = json.loads(result)
    assert parsed["status"] == "accepted"
    assert "session_id" in parsed
    assert parsed["session_id"].startswith("ses_")
```

#### Level 2: Integration Tests (2 simulated agents — ~10 tests, ~500ms each)

**Architecture**: Two test agents running in the same process, sharing an isolated Hivemind store. Each test follows a coordination workflow:

| Test ID | Scenario | Workflow | Success Criteria |
|---------|----------|----------|------------------|
| I-001 | **Awareness discovery** | Agent A posts context → Agent B calls get_awareness → B sees A | B's awareness list includes A's cli, model, task_current |
| I-002 | **Context read** | A posts → B reads A's session via get_session | B gets full snapshot matching A's original post |
| I-003 | **Heartbeat lifecycle** | A posts → B sees A → A heartbeats → A goes silent → TTL expires → B sees A gone | Awareness transitions: present → present (updated) → absent |
| I-004 | **Cold path survival** | A posts → simulate hub restart (clear dicts) → B reads via get_session(sid) | Session found from HALL_OF_RECORDS/ path |
| I-005 | **Two-agent awareness** | A posts → B posts → both call get_awareness → both see each other | Awareness list length = 2 |
| I-006 | **Continuation handoff** | A posts with continuation "Waiting for B" → B reads get_continuation("A") → B responds | B's response references A's continuation |
| I-007 | **Decision cascade** | A posts decisions D1 → A posts decisions D2 → B reads both sessions → B sees both decisions | B can enumerate D1 + D2 across two sessions |
| I-008 | **Heartbeat recreates after TTL** | A posts → TTL expires → A heartbeats → B sees A again | Awareness re-presents A after TTL had pruned it |
| I-009 | **Concurrent posts different CLIs** | A and B post simultaneously → both sessions stored | hot_store has both session entries |
| I-010 | **Concurrent posts same CLI** | A posts ses-1 → A posts ses-2 (same CLI, different session) → B reads both | session-1 and session-2 both in hot_store; awareness has ses-2 as latest |

**Integration test pattern**:

```python
@pytest.mark.anyio
async def test_two_agent_awareness(hivemind_harness):
    """I-005: Two agents see each other after posting context."""
    # Agent A posts
    await hivemind_harness.post_context(
        cli="agent_a", model="model-a",
        task_current="Task A", focus_chain=[],
        decisions=[], continuation="",
    )
    # Agent B posts
    await hivemind_harness.post_context(
        cli="agent_b", model="model-b",
        task_current="Task B", focus_chain=[],
        decisions=[], continuation="",
    )
    # Both call get_awareness
    awareness_a = json.loads(await hivemind_harness.get_awareness())
    awareness_b = json.loads(await hivemind_harness.get_awareness())
    assert len(awareness_a) == 2
    assert len(awareness_b) == 2
    clis = {a["cli"] for a in awareness_a}
    assert clis == {"agent_a", "agent_b"}
```

#### Level 3: Stress Tests (10+ simulated agents — ~5 tests, ~10s each)

| Test ID | Scenario | What It Pushes | Pass/Fail Criteria |
|---------|----------|-----------------|-------------------|
| S-001 | **10-agent awareness** | 10 agents post context → each reads awareness | All agents visible, no data corruption |
| S-002 | **Heartbeat storm** | 100 heartbeats from 5 agents in 10 seconds | No lock contention, all timestamps advance |
| S-003 | **Large context payloads** | Each post has 100KB focus_chain (1000 items) | Server doesn't OOM, response < 5s |
| S-004 | **Rapid awareness polling** | 5 agents each poll awareness 50 times in 5 seconds | No TTL race conditions (agent should not appear/disappear) |
| S-005 | **Memory growth check** | 10,000 sessions posted across 100 agents | _hot_store memory < 50MB, oldest sessions evicted or pruned |

**Key stress question**: The current `_hot_store` and `_awareness` are **unbounded** `Dict`s. Under S-005, 10,000 sessions × ~1KB each ≈ 10MB in hot store. This is acceptable for now but must be tested — and a max-size eviction policy should be added before it reaches production scale.

**Stress test pattern** (following existing `tests/sovereign_stress_test.py`):

```python
@pytest.mark.anyio
async def test_10_agent_awareness(hivemind_stress_harness):
    """S-001: 10 agents post and read — all visible."""
    agents = [f"agent_{i}" for i in range(10)]
    async def post_and_read(agent_name: str):
        await hivemind_stress_harness.post_context(
            cli=agent_name, model="test",
            task_current=f"Task {agent_name}",
            focus_chain=[], decisions=[], continuation="",
        )
        awareness = json.loads(await hivemind_stress_harness.get_awareness())
        return len(awareness)

    results = await anyio.gather(*[post_and_read(a) for a in agents])
    # Each agent should see all 10 agents (itself + 9 others)
    assert all(r == 10 for r in results)
```

#### Level 4: Chaos Tests (5 scenarios — §2 below)

#### Level 5: Scenario Tests (Full workflows — ~5 tests, ~30s each)

| Test ID | Scenario | Steps | Success Criteria |
|---------|----------|-------|-----------------|
| SC-001 | **Full coordination protocol** (§6 of HIVEMIND_PROTOCOL.md) | 1. A checks awareness → 2. A posts context → 3. B checks awareness sees A → 4. B posts context → 5. Both get_session each other → 6. Both execute → 7. Both post updates → 8. Both close → 9. Both soul write-back | All 9 steps complete without data loss |
| SC-002 | **Subagent dispatch via Hivemind** | Kali spawns P3 via task() → P3 posts to Hivemind → Kali reads P3's session → P3 completes → Kali gets continuation | Full subagent lifecycle visible in Hivemind |
| SC-003 | **Cross-session decision analysis** | 3 agents across 5 sessions each post decisions → Hivemind agent reads all 15 sessions → produces consolidated decision list | All 15 decisions readable without loss |
| SC-004 | **Graceful degradation — Hub restart** | Agent A has active session → Hub goes down → Hub comes back → A heartbeats → System recovers | A's session from cold store still accessible |
| SC-005 | **Hivemind + Workspace lock integration** | A posts lock for file.py → B checks awareness → B reads lock file → B chooses different file → both complete | No file conflicts |

---

## §2 Chaos Engineering

The Hivemind is experimental. These 5 chaos scenarios test its survival instincts.

### §2.1 Scenario C-001: Agent Drops Offline Mid-Handoff

**Premise**: Agent A posts context with continuation "Waiting for B's response to my analysis." Agent A's hub connection dies (network, OOM, crash). Agent B is waiting.

**What happens now**:
- A's awareness entry remains in `_awareness` for up to `HEARTBEAT_TTL` seconds (currently 1200s/20min)
- A's session persists in `_hot_store` indefinitely (no TTL on stored sessions)
- A's session persists in `HALL_OF_RECORDS/` on disk
- Agent B can still read A's last continuation via `hivemind_get_continuation("A")`
- Agent B has **no way to know** whether A is coming back or is dead — only that awareness will time out

**Chaos test design**:

```python
@pytest.mark.anyio
async def test_chaos_agent_drops_mid_handoff(hivemind_chaos_harness):
    """C-001: Agent drops offline mid-handoff. Verify B can read A's last state."""
    # Phase 1: A posts context with continuation
    await hivemind_chaos_harness.post_context(
        cli="agent_a", model="model-a",
        task_current="Analyzing feature X",
        focus_chain=["Step 1", "Step 2"],
        decisions=[{"text": "Use approach Y"}],
        continuation="Waiting for B's response to my analysis.",
        session_id="ses_chaos_001",
    )
    # Phase 2: Agent A disappears — simulate by removing from awareness
    await hivemind_chaos_harness.simulate_agent_crash("agent_a")
    
    # Phase 3: Agent B tries to read A's context
    continuation = await hivemind_chaos_harness.get_continuation("agent_a")
    assert continuation == "Waiting for B's response to my analysis."
    
    # Phase 4: B can still get A's full session
    session = json.loads(await hivemind_chaos_harness.get_session("ses_chaos_001"))
    assert session["task_current"] == "Analyzing feature X"
    
    # Phase 5: Awareness no longer shows A (gone_hot but persisted_cold)
    awareness = json.loads(await hivemind_chaos_harness.get_awareness())
    assert "agent_a" not in [a["cli"] for a in awareness]
```

**Risk**: If `get_continuation` has no cold-path fallback (see H-4 in Roc's proposal), B gets `"No awareness data"` — a false negative. **This is the exact bug Roc and Lilith both encountered.**

### §2.2 Scenario C-002: Heartbeat Silence > TTL

**Premise**: Agent A posts context, then goes silent (long inference, user away from keyboard). Heartbeat interval exceeds HEARTBEAT_TTL (1200s).

**What happens now**:
- Pruning thread runs every 60s — within 1 cycle of TTL expiry, A is removed from `_awareness`
- A's session persists in `_hot_store` and cold path
- Agent B calling `get_awareness` does NOT see A
- Agent B calling `get_continuation("A")` returns the last continuation (or "no awareness data" without H-4)
- When A heartbeats again, A is re-added to `_awareness` with fresh timestamp

**Chaos test design**:

```python
@pytest.mark.anyio
async def test_chaos_heartbeat_silence_ttl(hivemind_chaos_harness):
    """C-002: Agent goes silent past TTL, then returns."""
    # Phase 1: A posts and heartbeats
    await hivemind_chaos_harness.post_context(
        cli="agent_a", model="model-a",
        task_current="Long-running task", focus_chain=[],
        decisions=[], continuation="Working on it...",
    )
    await hivemind_chaos_harness.heartbeat("agent_a")
    
    # Phase 2: Advance time past TTL (mock time)
    hivemind_chaos_harness.advance_time(HEARTBEAT_TTL + 60)
    
    # Phase 3: B checks awareness — A should be gone
    awareness = json.loads(await hivemind_chaos_harness.get_awareness())
    assert "agent_a" not in [a["cli"] for a in awareness]
    
    # Phase 4: A returns and heartbeats
    await hivemind_chaos_harness.heartbeat("agent_a")
    
    # Phase 5: B checks awareness — A should be back
    awareness = json.loads(await hivemind_chaos_harness.get_awareness())
    clis = [a["cli"] for a in awareness]
    assert "agent_a" in clis
```

**Risk**: False ghost — B thinks A is gone and starts working on the same file. This is the exact scenario Kali described (13-minute gap between posts, TTL pruned).

### §2.3 Scenario C-003: Conflicting Workspace Locks

**Premise**: Two agents simultaneously claim ownership of the same file via workspace lock files. Agent A writes `DOOM_GUY_WORKSPACE_LOCK_20260605.md` claiming `oracle.py`. Agent B simultaneously writes `KALI_WORKSPACE_LOCK_20260605.md` also claiming `oracle.py`.

**What happens now**:
- There is **no programmatic enforcement** of workspace locks — they are human-readable conventions
- Both agents proceed, both edit the same file, the later write wins (or merge conflict on `git push`)
- The Hivemind has no `conflict_detection` tool

**Chaos test design**:

```python
@pytest.mark.anyio
async def test_chaos_conflicting_workspace_locks(hivemind_chaos_harness, tmp_path):
    """C-003: Two agents claim same file. Verify conflict is detectable."""
    lock_dir = tmp_path / "coordination"
    lock_dir.mkdir()
    
    # Phase 1: Agent A writes lock
    lock_a = lock_dir / "AGENT_A_WORKSPACE_LOCK_20260605.md"
    lock_a.write_text(
        "# AGENT_A Workspace Lock\n"
        "## DO NOT TOUCH\n"
        "| oracle.py | Refactoring | Rewrite pipeline |\n"
    )
    
    # Phase 2: Agent B writes lock (simultaneous — no awareness of A's lock)
    lock_b = lock_dir / "AGENT_B_WORKSPACE_LOCK_20260605.md"
    lock_b.write_text(
        "# AGENT_B Workspace Lock\n"
        "## DO NOT TOUCH\n"
        "| oracle.py | Bug fix | Fix timeout bug |\n"
    )
    
    # Phase 3: conflict detection (proposed tool)
    conflicts = await hivemind_chaos_harness.detect_lock_conflicts(lock_dir)
    assert len(conflicts) == 1
    assert conflicts[0]["file"] == "oracle.py"
    assert "AGENT_A" in conflicts[0]["claimants"]
    assert "AGENT_B" in conflicts[0]["claimants"]
```

**Risk**: Currently **undetectable** without a `detect_lock_conflicts` tool. This is a gap (mapping to Lilith's OBS-003 and Roc's H-2).

### §2.4 Scenario C-004: Memory Exhaustion (Hot Store Overflow)

**Premise**: The in-memory `_hot_store` dict fills up after sustained Hivemind usage. Currently there is **no cap** on `_hot_store` size.

**What happens now**:
- `_hot_store` grows unbounded
- When Python runs out of memory (14GB on this machine, ~2GB overhead → ~12GB for AI/system), the MCP server crashes
- `_awareness` also unbounded, but TTL pruning keeps it bounded by agent count
- Realistic risk: 100 agents × 100 sessions each = 10,000 entries × ~1KB = ~10MB — not dangerous yet, but at 10,000 agents×100 sessions it's 1GB

**Chaos test design**:

```python
@pytest.mark.anyio
async def test_chaos_memory_exhaustion_hot_store(hivemind_chaos_harness):
    """C-004: Hot store reaches capacity. Verify eviction or crash prevention."""
    # Phase 1: Post sessions until hypothetical max (1000 sessions for test)
    MAX_SESSIONS = 1000  # tunable; test at smaller scale
    for i in range(MAX_SESSIONS):
        await hivemind_chaos_harness.post_context(
            cli=f"agent_{i % 10}", model="test",
            task_current=f"Task {i}", focus_chain=[],
            decisions=[], continuation="",
            session_id=f"ses_memtest_{i:04d}",
        )
    
    # Phase 2: Verify hot store hasn't grown beyond cap (if eviction implemented)
    # or verify the process didn't crash (if no eviction yet)
    store_size = hivemind_chaos_harness.hot_store_size()
    if hasattr(hivemind_chaos_harness, "MAX_HOT_STORE"):
        assert store_size <= hivemind_chaos_harness.MAX_HOT_STORE
    else:
        # Without eviction, this is a risk-acceptance test
        assert store_size == MAX_SESSIONS  # all stored
        # Log warning about unbounded growth
```

**Risk**: **ACCEPTED** for now (10K sessions ≈ 10MB). Must be mitigated before general availability. Proposed: add `MAX_HOT_STORE = 10000` with LRU eviction of oldest sessions.

### §2.5 Scenario C-005: Concurrent Context Posts (Race Condition)

**Premise**: Agent A and Agent B both post context at the same microsecond. Can one overwrite the other?

**What happens now**:
- `anyio.Lock` protects both `_hot_store_lock` and `_awareness_lock`
- Since keys differ (`session_id` for hot_store, `cli` for awareness), concurrent posts with different session_ids should be safe
- **BUT**: If two agents use the **same session_id** (bug), the later write silently overwrites the earlier
- **ALSO**: If both share the same CLI name (misconfiguration), the later `_awareness[cli]` assignment overwrites

**Chaos test design**:

```python
@pytest.mark.anyio
async def test_chaos_concurrent_posts_same_cli(hivemind_chaos_harness):
    """C-005: Two agents with same CLI post simultaneously. Verify one doesn't lose data."""
    async def post_1():
        return await hivemind_chaos_harness.post_context(
            cli="same_cli", model="model-a",
            task_current="Task from agent 1",
            focus_chain=[], decisions=[],
            continuation="Agent 1's message",
            session_id="ses_concurrent_001",
        )
    async def post_2():
        return await hivemind_chaos_harness.post_context(
            cli="same_cli", model="model-b",
            task_current="Task from agent 2",
            focus_chain=[], decisions=[],
            continuation="Agent 2's message",
            session_id="ses_concurrent_002",
        )
    
    # Fire both concurrently
    results = await anyio.gather(post_1(), post_2())
    
    # Both should be accepted
    assert all("accepted" in r for r in results)
    
    # Both sessions should be in hot_store (keyed by session_id, safe)
    s1 = json.loads(await hivemind_chaos_harness.get_session("ses_concurrent_001"))
    s2 = json.loads(await hivemind_chaos_harness.get_session("ses_concurrent_002"))
    assert s1["task_current"] == "Task from agent 1"
    assert s2["task_current"] == "Task from agent 2"
    
    # Awareness for same_cli should have the LATTER post (last-write-wins)
    awareness = json.loads(await hivemind_chaos_harness.get_awareness())
    same_cli_entries = [a for a in awareness if a["cli"] == "same_cli"]
    assert len(same_cli_entries) == 1  # only one entry per CLI in awareness
    # The task_current in awareness is non-deterministic (depends on timing)
```

**Risk**: The Hivemind **correctly prevents data loss** because `_hot_store` keys by `session_id` (unique per post). The worst case is `_awareness[cli]` last-write-wins, but awareness is a lightweight summary — the full data lives in `_hot_store[session_id]` and cold path.

---

## §3 Verification Gates

### §3.1 Proposed Makefile Targets

```makefile
# ============================================================================
# 🔱 HIVEMIND VERIFICATION GATES
# ============================================================================

# ── make hivemind-test — Unit + Integration (fast, runs in CI) ─────
hivemind-test: guard
	@echo "$(COLOR_CYAN)🧪 Hivemind: Unit + Integration Tests$(COLOR_NC)"
	@OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m pytest tests/test_hivemind.py \
		-v --tb=short -k "unit or integration"
	@echo "$(COLOR_GREEN)✅ Hivemind unit+integration tests passed$(COLOR_NC)"

# ── make hivemind-stress — Stress + Chaos (long-running, NOT in CI) ─
hivemind-stress: guard
	@echo "$(COLOR_YELLOW)⚡ Hivemind: Stress + Chaos Tests$(COLOR_NC)"
	@echo "$(COLOR_YELLOW)⚠  These tests are long-running (2-5 min) and NOT part of CI.$(COLOR_NC)"
	@OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m pytest tests/test_hivemind_stress.py \
		-v --tb=long -k "stress or chaos" --timeout=120
	@echo "$(COLOR_GREEN)✅ Hivemind stress+chaos tests passed$(COLOR_NC)"

# ── make hivemind-health — Runtime health check against live Hub ───
hivemind-health: guard
	@echo "$(COLOR_CYAN)🩺 Hivemind: Runtime Health Check$(COLOR_NC)"
	@python3 -c "
import json, urllib.request
try:
    # Check if Hub is running (port 8000 is default for omega_hub)
    req = urllib.request.Request('http://127.0.0.1:8000/health')
    resp = urllib.request.urlopen(req, timeout=5)
    data = json.loads(resp.read())
    assert data['status'] == 'healthy'
    print('  $(COLOR_GREEN)✅$(COLOR_NC) Hub health: OK')
except Exception as e:
    print('  $(COLOR_RED)❌$(COLOR_NC) Hub health check failed:', e)
    exit(1)
"
	@echo "$(COLOR_GREEN)✅ Hivemind health check passed$(COLOR_NC)"

# ── make hivemind-obs-check — Validate observation log is non-empty ──
hivemind-obs-check: guard
	@echo "$(COLOR_CYAN)📝 Hivemind: Observation Log Check$(COLOR_NC)"
	@OBS_COUNT=$$(grep -c '^### \[' data/coordination/HIVEMIND_OBSERVATIONS_LOG.md 2>/dev/null || echo 0); \
	if [ "$$OBS_COUNT" -gt 0 ]; then \
		echo "  $(COLOR_GREEN)✅$(COLOR_NC) $$OBS_COUNT observations in log"; \
	else \
		echo "  $(COLOR_YELLOW)⚠$(COLOR_NC) Observation log is empty — no Hivemind sessions recorded"; \
	fi

# ── make hivemind-conflicts — Detect workspace lock conflicts ───────
hivemind-conflicts: guard
	@echo "$(COLOR_CYAN)🔍 Hivemind: Workspace Lock Conflict Detection$(COLOR_NC)"
	@python3 scripts/hivemind_conflict_detector.py
	@echo "$(COLOR_GREEN)✅ Conflict detection complete$(COLOR_NC)"

# ── Aggregated Hivemind gate ────────────────────────────────────────
hivemind: hivemind-test hivemind-health hivemind-obs-check
	@echo "$(COLOR_GREEN)✅ All Hivemind gates passed$(COLOR_NC)"
```

### §3.2 CI Integration Strategy

| Gate | CI? | Frequency | Timeout | Run On |
|------|-----|-----------|---------|--------|
| `hivemind-test` | ✅ Yes | Every push | 30s | All unit+integration tests |
| `hivemind-health` | ✅ Yes | Every push | 5s | Hub connectivity check |
| `hivemind-obs-check` | 🟡 Warning | Every push | 2s | Non-blocking warning |
| `hivemind-stress` | ❌ No | Weekly manually | 5min | Before Phase 5 release |
| `hivemind-conflicts` | 🟡 On demand | When coordinating | 10s | Manual trigger during parallel work |

### §3.3 Gate Compliance Matrix

| Gate | T-Grade Gate | Mandate | What It Enforces |
|------|-------------|---------|------------------|
| `hivemind-test` | T3 (Testing) | M13 (Temple-Grade) | Core Hivemind correctness |
| `hivemind-health` | T9 (Observability) | M13 | Hub is reachable |
| `hivemind-obs-check` | T1 (Version Control) | M5 (Gnosis Preservation) | Observations are being recorded |
| `hivemind-stress` | T8 (Resilience) | M13 | System handles load |
| `hivemind-conflicts` | T11 (Agent Security) | M10 (Fleet Integrity) | No parallel agent collisions |

---

## §4 Failure Mode Catalog

### §4.1 Failure Mode F-001: Message Loss

**Description**: A `hivemind_post_context` call succeeds (HTTP 200, "accepted" response) but the context is not stored in one or more of the three stores (hot_store, awareness, cold path).

**Root causes**:
- Write to `_hot_store` succeeds but cold-path file write fails (disk full, permission error)
- Write to `_awareness` succeeds but `_hot_store` write fails (AnyIO lock timeout)
- Partial failure: `_hot_store` and cold path succeed but `_awareness` write fails

**Detection**:
- `hivemind_get_session(sid)` returns "Session not found" despite post_context returning "accepted"
- Agent B calls `hivemind_get_awareness()` and does not see Agent A, despite Agent A posting context

**Frequency**: Not observed yet (2 sessions logged). Theoretical risk from 3-phase write (hot → awareness → cold). If MCP server crashes between phase 1 and 3, data is partially written.

### §4.2 Failure Mode F-002: Message Corruption

**Description**: The context snapshot is stored but its content is garbled or truncated.

**Root causes**:
- JSON serialization fails for non-serializable content in `focus_chain` or `decisions`
- File system write truncates mid-write (power loss, disk full mid-write)
- Unicode encoding issues (`continuation` field with certain characters)

**Detection**:
- `hivemind_get_session(sid)` returns malformed JSON
- Cold path file (`HALL_OF_RECORDS/<cli>/<sid>.json`) fails `json.load()`
- Awareness shows gibberish in `task_current`

**Frequency**: Not observed. The current implementation uses `json.dumps(snapshot, indent=2)` which would raise `TypeError` on non-serializable content before write — so corruption is caught early.

### §4.3 Failure Mode F-003: Agent Phantom

**Description**: The awareness store shows an agent as "alive" but the agent is actually dead — its process has crashed but its awareness was not pruned.

**Root causes**:
- Agent doesn't call `hivemind_heartbeat()` before crashing — TTL has not yet expired
- Pruning thread hasn't run its 60s cycle yet
- HEARTBEAT_TTL (1200s) means phantom persists for up to 20 minutes

**Detection**:
- `hivemind_get_awareness()` returns an agent whose `last_seen` is > TTL ago
- `hivemind_get_continuation(cli)` returns the agent's last message, but the agent never responds

**Frequency**: **OBSERVED** — this is the mirror of the TTL pruning problem. Before Lilith's D-122 fix (1200s TTL), the risk was ghost (agent alive but pruned). After D-122, the risk is phantom (agent dead but not pruned).

### §4.4 Failure Mode F-004: Agent Ghost

**Description**: Agent is alive but awareness shows it as stale/pruned.

**Root causes**:
- HEARTBEAT_TTL was 300s (pre-D-122) — caused prunes during normal 15-min coordination gaps
- Agent performing long inference (>20 min) without heartbeat
- Pruning thread runs while agent is alive but between operations

**Detection**:
- Agent B calls `hivemind_get_awareness()` and sees Agent A missing
- Agent A is still working (can be verified via filesystem or live feed)

**Frequency**: **OBSERVED** — Kali experienced this (13-min gap, 5-min TTL, D-122 changed to 20-min). D-122 mitigated but did not eliminate: a 25-min inference would still ghost.

### §4.5 Failure Mode F-005: Lock Conflict

**Description**: Two agents write workspace lock files claiming the same file, then both proceed to edit it.

**Root causes**:
- Agents start simultaneously (or within seconds) — neither saw the other's lock
- Agent B ignores Agent A's lock (deliberate override or human error)
- Agent A's lock file was missed by Agent B (race condition in file listing)

**Detection**:
- `git merge` conflict on the shared file
- A diff of workspace lock files shows overlapping `DO NOT TOUCH` sections

**Frequency**: **NOT OBSERVED** — but the Sprint 2 Ma'at/Doom Guy parallel execution was successful because Ma'at declared and Doom Guy ACK'd. No automated detection exists.

### §4.6 Failure Mode F-006: Context Drift

**Description**: Agent A reads Agent B's session, starts working based on that context, but Agent B updates their session while A is working. A works from stale data.

**Root causes**:
- Asynchronous read → the moment A reads B's session, it may already be outdated
- No versioning on session snapshots (no `version` or `etag` field)
- No "last-modified" tracking on individual context fields

**Detection**:
- A's work output references old decisions that B has since superseded
- A's `focus_chain` includes steps B has already completed

**Frequency**: **INHERENT** — the Hivemind is eventually consistent, not strongly consistent. This is a design property, not a bug.

### §4.7 Failure Mode F-007: State Split-Brain (Hub Restart)

**Description**: The MCP Hub restarts (deployment, crash, maintenance). In-memory `_hot_store` and `_awareness` are lost.

**Root causes**:
- Hub process terminates — all in-memory dicts gone
- Background pruning thread dies with the process

**Detection**:
- After restart, `hivemind_get_awareness()` returns empty — no agents visible
- `hivemind_get_session(sid)` falls back to cold path (HALL_OF_RECORDS) — succeeds if cold store intact
- Agents must re-heartbeat to re-register awareness

**Frequency**: **CATASTROPHIC** — all live awareness is lost. Only cold sessions survive.

### §4.8 Failure Mode F-008: Observation Drift

**Description**: Agents are using the Hivemind but nobody records observations (per D-121 mandate). The learning loop is broken.

**Root causes**:
- Agent forgets to append to `HIVEMIND_OBSERVATIONS_LOG.md`
- Agent runs out of context window and observation isn't in prompt
- Agent is a subagent with no knowledge of the observation mandate

**Detection**:
- `make hivemind-obs-check` reports 0 observations after a multi-agent session
- Lilith's weekly cluster finds no new entries

**Frequency**: **LIKELY** — this document is being written during the 3rd Hivemind session, and observations are just starting (5 entries from Lilith, none from Kali or Roc yet for their dialog).

### §4.9 Failure Summary Table

| ID | Name | Severity | Frequency | Observability | Auto-Heal? |
|----|------|----------|-----------|---------------|------------|
| F-001 | Message Loss | 🔴 Critical | Low (theoretical) | 🟡 Partial — `get_session` check | ❌ Manual recovery from cold |
| F-002 | Message Corruption | 🟡 Medium | Low (prevented by json.dumps) | 🟡 Partial — parse error on read | ❌ Must re-post |
| F-003 | Agent Phantom | 🟡 Medium | Medium (TTL window) | 🟢 Full — awareness shows stale | ✅ Yes — TTL auto-prune |
| F-004 | Agent Ghost | 🟡 Medium | Medium (long inference) | 🟢 Full — awareness shows missing | ✅ Yes — heartbeat recreates |
| F-005 | Lock Conflict | 🔴 Critical | Low (but possible) | ⚫ None — no detection tool | ❌ Manual merge resolution |
| F-006 | Context Drift | 🟢 Info | High (inherent) | ⚫ None — designed behavior | N/A — design property |
| F-007 | State Split-Brain | 🔴 Critical | Low (Hub restart) | 🟡 Partial — cold path survives | ✅ Partial — heartbeat re-registers |
| F-008 | Observation Drift | 🟢 Info | Likely (new mandate) | 🟢 Full — `hivemind-obs-check` | ❌ Manual — retrain agents |

---

## §5 Recovery Procedures

### §5.1 F-001 Recovery: Message Loss

**Immediate recovery (manual)**:
1. Check `HALL_OF_RECORDS/<cli>/` for the session file — if it exists, the cold path has the data
2. Re-post the context via `hivemind_post_context` with the same `session_id` to restore hot awareness
3. If cold path is also missing, re-run the agent's work to regenerate the context

**Preventive (design change)**:
- Add idempotency to `hivemind_post_context`: if `session_id` already exists in cold path, skip cold write (don't overwrite), only update hot stores
- Add atomic 3-phase commit: write to cold FIRST, then update hot stores. If hub crashes between hot_store and awareness, cold path has the canonical record.
- Add `hivemind_verify_session(sid)` tool that checks all 3 stores and reports consistency

**Heritage**: `[id-soft: doom-1993]` Lazy Deletion — the 3-phase write is analogous to Doom's thinker lifecycle (spawn → tick → reap). Each phase must complete or roll back.

```python
# Proposed: atomic 3-phase write
async def hivemind_post_context_atomic(...):
    """3-phase commit: cold → hot → awareness."""
    # Phase 1: Write to cold storage first (fsync'd, survives crash)
    cold_path = _cold_path(cli, sid)
    await anyio.to_thread.run_sync(lambda: cold_path.parent.mkdir(parents=True, exist_ok=True))
    async with await anyio.open_file(str(cold_path), "w") as f:
        await f.write(json.dumps(snapshot, indent=2))
    
    # Phase 2: Update hot store
    async with _hot_store_lock:
        _hot_store[sid] = snapshot
    
    # Phase 3: Update awareness
    async with _awareness_lock:
        _awareness[cli] = snapshot
    
    # Rollback: If Phase 2 or 3 fail, we still have cold path.
    # No explicit rollback needed — cold path is the source of truth.
```

### §5.2 F-002 Recovery: Message Corruption

**Immediate recovery (manual)**:
1. Read the corrupt file from `HALL_OF_RECORDS/<cli>/<sid>.json`
2. Attempt to fix JSON (truncation is identifiable by incomplete `}`)
3. Re-post with corrected data
4. Delete the corrupt cold file

**Preventive (design change)**:
- Add JSON schema validation BEFORE writing: validate the snapshot against a Pydantic model, catch serialization errors early
- Atomic rename: write to `.tmp` file, then `os.rename()` to final name — prevents partial reads
- Add ZONEID to every cold file: first 4 bytes = `0x1d4a17` — corrupted files fail ZONEID check

**Heritage**: `[id-soft: doom-1993]` ZONEID Pattern — `ZONEID_PRESENCE = 0x1d4a17` serves as integrity check on every session load:

```python
ZONEID_PRESENCE = 0x1d4a17

def validate_session_integrity(snapshot: dict) -> bool:
    """Verify session has valid ZONEID marker.
    
    [id-soft: doom-1993] ZONEID Pattern — every session file must carry
    its ZONEID to detect corruption on load.
    """
    return snapshot.get("zoneid") == ZONEID_PRESENCE
```

### §5.3 F-003 Recovery: Agent Phantom

**Immediate recovery (automatic)**:
- **Nothing needed** — the phantom resolves itself when TTL expires (max 20 min under current HEARTBEAT_TTL)
- Pruning thread runs every 60s and will remove the entry

**Preventive (design change)**:
- Add proactive health check: if an agent's `last_seen` is > 50% of TTL, the Hub can send a ping to verify liveness
- Add agent-side graceful shutdown: `hivemind_deregister(cli)` removes agent immediately

**Heritage**: `[id-soft: quake-1996]` Lazy Deletion with Grace Period — the phantom is tolerated for up to 20 minutes (grace period), then automatically cleaned up. The same pattern Doom uses for thinker cleanup.

### §5.4 F-004 Recovery: Agent Ghost

**Immediate recovery (automatic)**:
- Agent heartbeats → `_awareness[cli]` is recreated with fresh timestamp
- Agent posts context → `_awareness[cli]` is recreated with full data

**Preventive (design change)**:
- Two-tier TTL (Roc's H-4, Kali's D-kal-037): hot 5min (in-memory) + warm 24h (disk) + cold permanent
- Warm tier allows `hivemind_get_continuation` to return data even after hot TTL expiry
- Agent should heartbeat every 5-10 min during long operations (per protocol §2.4)

**Implementation** of two-tier TTL already proposed by Roc and accepted by Kali:

```python
# Proposed: two-tier awareness (extends current _awareness)
WARM_TTL = 86400  # 24 hours — survived by agent "I was here recently"
_warm_store: Dict[str, Dict[str, Any]] = {}  # persisted to disk

async def hivemind_get_awareness_twotier() -> str:
    """Return agents from hot + warm tiers.
    
    [id-soft: quake-1996] Two-tier memory — hot for "alive now",
    warm for "recently active". Cold via HALL_OF_RECORDS.
    """
    now = datetime.now(timezone.utc)
    result = []
    
    # Hot tier: agents alive right now
    async with _awareness_lock:
        for cli, snap in _awareness.items():
            ts = datetime.fromisoformat(snap["timestamp"])
            if (now - ts).total_seconds() <= HEARTBEAT_TTL:
                result.append({
                    "cli": cli, "heat": "hot",
                    **snap,
                })
    
    # Warm tier: agents active in last 24h
    for cli, snap in _warm_store.items():
        ts = datetime.fromisoformat(snap["timestamp"])
        if (now - ts).total_seconds() <= WARM_TTL:
            if cli not in {r["cli"] for r in result}:
                result.append({
                    "cli": cli, "heat": "warm",
                    **snap,
                })
    
    return json.dumps(result, indent=2)
```

### §5.5 F-005 Recovery: Lock Conflict

**Immediate recovery (manual)**:
1. Both agents pause work on the conflicted file
2. Read each other's workspace lock files
3. Negotiate: one agent defers, or they split the work
4. Update lock files to reflect new boundaries
5. Regret the conflict in `HIVEMIND_OBSERVATIONS_LOG.md`
6. If git merge conflict already exists, resolve via `git mergetool`

**Preventive (design change)**:
- Add `detect_lock_conflicts` tool (proposed in §2.3) that scans all `*WORKSPACE_LOCK_*.md` files and reports overlaps
- Add LOCK file protocol: before editing any file in `src/omega/`, agent must check locks and post awareness
- Add `hivemind_claim_file(cli, filepath)` as a lightweight alternative to workspace lock markdown files — machine-readable, conflict-checkable

**Heritage**: `[id-soft: quake-1996]` netchan Protocol — the lock conflict is like a netchan port conflict; the protocol must detect it before the agents collide, not after.

### §5.6 F-006 Recovery: Context Drift

**Immediate recovery (automatic — design property)**:
- Context drift is **eventually consistent**. If B updates their session and A reads the old version, A will get the new version on their next `get_session()` call.
- The Hivemind is not a real-time protocol. It's a coordination substrate. Drift is expected.

**Preventive (design change)**:
- Add `version` field to every session snapshot, incrementing on each post
- `hivemind_get_continuation(cli, min_version=N)` returns only continuations newer than N
- Agent reads: "I'm at version 3. Has B posted version 4 yet?"

**This is a non-blocking design property, not a bug.** The risk is low because:
- Agents typically read once, execute, then read again. The window of drift is small.
- If drift matters, the agent should call `get_awareness()` immediately before acting on the data.

### §5.7 F-007 Recovery: State Split-Brain (Hub Restart)

**Immediate recovery (automatic + manual)**:
1. **Automatic**: When the Hub restarts, agents must re-heartbeat. The pruning thread restarts automatically (daemon thread in `__main__`)
2. **Manual**: If agents don't detect the restart, they think other agents are ghosts. Lead agent (Kali) should check `hivemind_get_awareness()`, see it's empty, and issue a fleet-wide "please re-register" via coordination file

**Preventive (design change)**:
- Persist `_awareness` to disk on every update (Roc's H-9, accepted by Kali)
- On Hub restart: load persisted awareness from disk before serving requests
- Add Hub uptime to `/health` endpoint: `uptime_seconds` field — agents can detect a restart

```python
# Proposed: H-9 awareness persistence
AWARENESS_PERSIST_PATH = HALL_OF_RECORDS / "_awareness_snapshot.json"

async def _persist_awareness():
    """Persist _awareness dict to disk after every change.
    
    [id-soft: quake3-1999] Fixed array state persistence — Q3A's
    entityState_t survives level transitions via snapshot save/restore.
    """
    async with _awareness_lock:
        data = {cli: snap for cli, snap in _awareness.items()}
    def _write():
        with open(AWARENESS_PERSIST_PATH, "w") as f:
            json.dump(data, f, indent=2)
    await anyio.to_thread.run_sync(_write)

async def _restore_awareness():
    """Load persisted awareness on Hub startup."""
    if AWARENESS_PERSIST_PATH.exists():
        def _read():
            with open(AWARENESS_PERSIST_PATH) as f:
                return json.load(f)
        data = await anyio.to_thread.run_sync(_read)
        async with _awareness_lock:
            for cli, snap in data.items():
                # Only restore agents that haven't expired their TTL
                ts = datetime.fromisoformat(snap.get("timestamp", ""))
                if (datetime.now(timezone.utc) - ts).total_seconds() <= HEARTBEAT_TTL:
                    _awareness[cli] = snap
```

### §5.8 F-008 Recovery: Observation Drift

**Immediate recovery (manual)**:
1. Check `make hivemind-obs-check` output
2. Re-train agents on D-121 mandate: every Hivemind session must append observations
3. Lilith (or P7 Context) manually backfills missing observations for critical sessions

**Preventive (design change)**:
- Add post-session hook: after `hivemind_post_context`, auto-append a boilerplate observation to `HIVEMIND_OBSERVATIONS_LOG.md`
- Link observation mandate in AGENTS.md (per Lilith's RECOMMENDATION in OBS-005)
- Make `hivemind-obs-check` part of the `make test` suite as a warning gate

---

## §6 Heritage Cross-Reference

Every validating concept in this strategy maps to an id Software heritage pattern, per CREDITS.md §2a inline tag protocol.

### §6.1 Error Gauntlet → Stress Test Design

| Heritage | Our Application | Section | Tag |
|----------|----------------|---------|-----|
| `tests/test_error_gauntlet.py` (provoke every error path, verify graceful degradation) | `test_hivemind_stress.py` — provoke every Hivemind failure mode | §2 Chaos tests | `[id-soft: quake-1996]` Error Gauntlet |
| Q3A's `botlib/be_ai_goal.c` — bot stress testing with 32 simultaneous bots | S-001: 10-agent awareness test | §1.2 Level 3 | `[id-soft: quake3-1999]` Bot stress testing |
| **Design**: Each chaos test is a single scenario (not a test matrix) — follows the Error Gauntlet style of tests/test_error_gauntlet.py where each scenario is self-contained and readable | All chaos tests follow this pattern | §2 | `[id-soft: quake-1996]` Error Gauntlet |

### §6.2 BSP Culling → Right Approximation for Test Coverage

| Heritage | Our Application | Section | Tag |
|----------|----------------|---------|-----|
| Doom's BSP tree: precompute visible surfaces, cull the rest | Test priority: unit (always) → integration (always) → stress (weekly) → chaos (monthly) | §1.2 5-level pyramid | `[id-soft: doom-1993]` BSP culling |
| "Don't render what you can't see" → "Don't test what can't fail" | Unit tests cover every MCP tool. Integration tests cover coordination patterns. Stress tests are gated: don't run them if unit tests fail. | §3 CI integration | `[id-soft: doom-1993]` BSP culling |
| **Right Approximation**: The 1200s TTL doesn't need to be exact — it needs to be "right enough" for human-paced coordination | Test coverage doesn't need to be 100% of all possible states — it needs to cover the common paths + known failure modes | §1.2 | `[id-soft: quake3-1999]` FISR Principle |

### §6.3 Zone Memory Allocator → Memory Exhaustion Tests

| Heritage | Our Application | Section | Tag |
|----------|----------------|---------|-----|
| Quake's tag-based allocator with purge levels (`PU_CACHE = 101`) | Add `MAX_HOT_STORE = 10000` with LRU eviction — the oldest sessions get purged first | §2.4 | `[id-soft: quake-1996]` Zone Memory |
| idHeap (Doom 3): Small/Medium/Large allocators | Three storage tiers: hot (in-memory, bounded), warm (disk, 24h TTL), cold (HALL_OF_RECORDS, permanent) | §5.4 | `[id-soft: doom3-2004]` idHeap |
| Memory exhaustion test: allocate until OOM, verify graceful shutdown | C-004: Post 1000 sessions, verify memory bounds | §2.4 | `[id-soft: quake-1996]` Zone Memory |

### §6.4 Lazy Deletion with Grace Period → Agent Ghost/Phantom

| Heritage | Our Application | Section | Tag |
|----------|----------------|---------|-----|
| Doom's `P_RemoveThinker`: sets sentinel (-1), reaps on next tick | Our TTL pruning: marks agent stale, removes on next `get_awareness()` or prune cycle | §4.3-4.4 | `[id-soft: doom-1993]` Lazy Deletion |
| 0.5s grace period prevents client-side morphing (Quake) | 20-min TTL grace period (D-122) prevents false ghosting — matches Doom's thinker grace pattern | §2.2 | `[id-soft: quake-1996]` Grace Period |
| **Evolution**: id Software's 0.5s grace was hardware-specific (15 packets at 30Hz). Our 1200s grace is protocol-specific (15-minute coordination cycles). Same pattern, evolved domain. | D-122 HEARTBEAT_TTL = 1200 | §2.2 | FISR Principle |

### §6.5 ZONEID → Session Integrity

| Heritage | Our Application | Section | Tag |
|----------|----------------|---------|-----|
| 0x1d4a11 magic in every memory block | `ZONEID_PRESENCE = 0x1d4a17` in every session snapshot | §5.2 | `[id-soft: doom-1993]` ZONEID Pattern |
| ZONEID check on every access | Validate `snapshot.zoneid == ZONEID_PRESENCE` on every `hivemind_get_session` and `hivemind_get_continuation` | §5.2 | `[id-soft: doom-1993]` ZONEID Pattern |
| **Already implemented**: `ZONEID_PRESENCE = 0x1d4a17` in `mcp_servers/omega_hub/server.py` | Extend to all 6 Hivemind MCP tools | §5.2 | `CREDITS.md §1.9` |

### §6.6 netchan Protocol → Concurrent Post Tests

| Heritage | Our Application | Section | Tag |
|----------|----------------|---------|-----|
| Q3A's netchan: sequence numbers prevent message reordering | `session_id` (UUID) prevents post overwriting — concurrent posts with different session_ids are always safe | §2.5 | `[id-soft: quake3-1999]` netchan |
| OOB messages (seq=-1) for low-latency pings | Future: `hivemind_ping(cli)` as lightweight heartbeat that doesn't update full awareness | §2.2 | `[id-soft: quake3-1999]` netchan |
| qport workaround for NAT remapping | Session re-association via `session_id` in headers — not yet implemented | Future | `[id-soft: quake3-1999]` netchan |

### §6.7 Fixed-Point Math → Right Approximation for Test Confidence

| Heritage | Our Application | Section | Tag |
|----------|----------------|---------|-----|
| "Better to be approximately right than precisely wrong" (FISR) | Test thresholds: don't assert exact timestamps (flaky), assert TTL windows | §2.2 | `[id-soft: quake3-1999]` FISR |
| 16.16 fixed-point: 1/65536 precision — good enough for Doom's renderer | `assert elapsed < TTL + 60` (pruning runs every 60s) — good enough for test reliability | §2.2 | `[id-soft: doom-1993]` Fixed-Point |
| **Risk**: Over-precise tests will be flaky on CI. A test that asserts `last_seen == specific_timestamp` will fail. | All chaos tests use time windows, not exact values | §2 all | FISR Principle |

### Heritage Mapping Summary

| Heritage Pattern | CREDITS Ref | Used In | Purpose |
|-----------------|-------------|---------|---------|
| Error Gauntlet | §1.8 (via circuit breaker pattern) | §2 Chaos tests | Each test provokes one error, verifies graceful degradation |
| BSP Culling | §1.2 | §1.2 Test pyramid, §3 CI gates | Don't test what can't fail; prioritize test levels |
| Zone Memory / idHeap | §1.4 / §1.22 | §2.4 Memory exhaustion, §5.4 | Tiered storage with TTL-based purge |
| Lazy Deletion | §1.10 | §4.3-4.4 Agent phantom/ghost | Grace period before cleanup matches human coordination pace |
| ZONEID | §1.9 | §5.2 Message corruption | Integrity markers on every session snapshot |
| netchan | §1.21 | §2.5 Concurrent posts | Session_id as unique sequence number prevents collisions |
| Fixed-Point / FISR | §1.3 / §1.23 | §2.2 (assertions), §6 all | Right-approximation for test confidence — avoid flaky assertions |

---

## §7 Implementation Roadmap

### Phase 1: Foundation (This Sprint — ~2 hours)

| # | Task | Owner | Depends On | Makefile Target |
|---|------|-------|-----------|-----------------|
| P1-1 | Create `tests/test_hivemind.py` with 20 unit tests (U-001 to U-020) | P10 Verifier | — | `hivemind-test` |
| P1-2 | Create `tests/conftest_hivemind.py` with `HivemindTestHarness` fixture | P10 Verifier | — | (shared fixture) |
| P1-3 | Run `hivemind-test` — all 20 unit tests pass | P10 Verifier | P1-1, P1-2 | `hivemind-test` |
| P1-4 | Add `hivemind-test`, `hivemind-health`, `hivemind-obs-check` to Makefile | P3 Engineering | — | `hivemind` |
| P1-5 | Add 10 integration tests (I-001 to I-010) | P10 Verifier | P1-3 | `hivemind-test` |
| P1-6 | Add ZONEID validation to all 6 MCP tools | P3 Doom Guy | — | Reuses `ZONEID_PRESENCE` |

### Phase 2: Stress & Chaos (Next Sprint — ~3 hours)

| # | Task | Owner | Depends On | Makefile Target |
|---|------|-------|-----------|-----------------|
| P2-1 | Create `tests/test_hivemind_stress.py` with 10-agent stress test (S-001) | P10 Verifier | P1-5 | `hivemind-stress` |
| P2-2 | Add heartbeat storm test (S-002) | P10 Verifier | P2-1 | `hivemind-stress` |
| P2-3 | Add large payload test (S-003) | P10 Verifier | P2-1 | `hivemind-stress` |
| P2-4 | Add rapid polling test (S-004) | P10 Verifier | P2-1 | `hivemind-stress` |
| P2-5 | Add memory growth test (S-005) + MAX_HOT_STORE eviction | P10 Verifier + P3 Eng | P2-1 | `hivemind-stress` |
| P2-6 | Implement 5 chaos tests (C-001 to C-005) | P10 Verifier | P2-5 | `hivemind-stress` |
| P2-7 | Implement `hivemind_conflict_detector.py` script | P3 Engineering | — | `hivemind-conflicts` |

### Phase 3: Hardening (Sprint+2 — ~4 hours)

| # | Task | Owner | Depends On | Makefile Target |
|---|------|-------|-----------|-----------------|
| P3-1 | Implement H-4 (two-tier TTL: hot + warm + cold) | Kali (Phase 5) | — | N/A (server change) |
| P3-2 | Implement H-9 (awareness persistence to disk) | Kali (Phase 5) | — | N/A (server change) |
| P3-3 | Add scenario tests (SC-001 to SC-005) | P10 Verifier | P2-6, P3-1, P3-2 | `hivemind-test` (extended) |
| P3-4 | Add `hivemind-verify-session(sid)` tool (checks all 3 stores) | Kali/P9 | P3-1 | N/A (MCP tool) |
| P3-5 | Add `hivemind-conflicts` to CI as warning (non-blocking) | P3 Engineering | P2-7 | CI config |

### Phase 4: Production Readiness (Horizon 3 — ~6 hours)

| # | Task | Owner | Makefile Target |
|---|------|-------|-----------------|
| P4-1 | Add `hivemind-stress` to weekly CI (non-gating) | CI Pipeline | `hivemind-stress` |
| P4-2 | Write `docs/research/HIVEMIND_TESTING_SPEC.md` | P10 Verifier | — |
| P4-3 | Retrospective: document first 3 Hivemind sessions in observations log | Lilith/P7 | `hivemind-obs-check` |
| P4-4 | Add ZONEID to cold-path session files (migration script) | P3 Doom Guy | — |
| P4-5 | Add Redis-backed realtime Hivemind tests (H-11) | P9 Orchestration | — |

---

## §8 Appendix: Test File Templates

### §8.1 `tests/conftest_hivemind.py` — Shared Fixture

```python
"""Hivemind test harness — shared fixtures for all Hivemind tests.

Provides an in-memory test harness that simulates the 6 MCP tools
without needing a running Hub server.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pathlib import Path

import anyio
import pytest

from mcp_servers.omega_hub.server import (
    HEARTBEAT_TTL,
    _cold_path,
    _latest_path,
)

# [id-soft: quake-1996] Error Gauntlet pattern — each scenario is
# a self-contained test that provokes one path and verifies graceful
# degradation or correct behavior.


class HivemindTestHarness:
    """In-memory Hivemind test double.
    
    Mocks _hot_store, _awareness, and HALL_OF_RECORDS with dicts
    and temp directories. All operations use AnyIO for lock correctness.
    """
    
    def __init__(self, tmp_path: Path):
        self._hot_store: Dict[str, Dict[str, Any]] = {}
        self._awareness: Dict[str, Dict[str, Any]] = {}
        self._hot_store_lock = anyio.Lock()
        self._awareness_lock = anyio.Lock()
        self.hall_of_records = tmp_path / "HALL_OF_RECORDS"
        self.hall_of_records.mkdir(parents=True, exist_ok=True)
        self._fake_time: Optional[datetime] = None  # For time mocking
    
    def set_time(self, dt: datetime):
        """Override current time for TTL testing."""
        self._fake_time = dt
    
    def advance_time(self, seconds: float):
        """Advance fake clock by seconds."""
        if self._fake_time is None:
            self._fake_time = datetime.now(timezone.utc)
        self._fake_time = self._fake_time + __import__("datetime").timedelta(seconds=seconds)
    
    def _now(self) -> datetime:
        return self._fake_time if self._fake_time else datetime.now(timezone.utc)
    
    async def post_context(self, cli: str, model: str, task_current: str,
                           focus_chain: List[str], decisions: List[Dict[str, str]],
                           continuation: str, session_id: Optional[str] = None) -> str:
        """Mirror of mcp_servers/omega_hub/server.py hivemind_post_context."""
        sid = session_id or f"ses_{uuid.uuid4().hex[:12]}"
        snapshot = {
            "session_id": sid,
            "cli": cli,
            "model": model,
            "task_current": task_current,
            "focus_chain": focus_chain,
            "decisions": decisions,
            "continuation": continuation,
            "timestamp": self._now().isoformat(),
        }
        async with self._hot_store_lock:
            self._hot_store[sid] = snapshot
        async with self._awareness_lock:
            self._awareness[cli] = snapshot
        
        # Cold path
        cold = self.hall_of_records / cli / f"{sid}.json"
        cold.parent.mkdir(parents=True, exist_ok=True)
        cold.write_text(json.dumps(snapshot, indent=2))
        
        return json.dumps({"status": "accepted", "session_id": sid})
    
    async def heartbeat(self, cli: str) -> str:
        """Mirror of hivemind_heartbeat."""
        async with self._awareness_lock:
            if cli in self._awareness:
                self._awareness[cli]["timestamp"] = self._now().isoformat()
                return json.dumps({"status": "heartbeat_received", "cli": cli})
            self._awareness[cli] = {
                "cli": cli, "timestamp": self._now().isoformat(),
                "model": "unknown", "task_current": "heartbeat-only",
            }
            return json.dumps({"status": "presence_registered", "cli": cli})
    
    async def get_awareness(self) -> str:
        """Mirror of hivemind_get_awareness."""
        now = self._now()
        async with self._awareness_lock:
            stale = []
            result = []
            for cli, snap in self._awareness.items():
                ts_str = snap.get("timestamp")
                if ts_str:
                    ts = datetime.fromisoformat(ts_str)
                    if (now - ts).total_seconds() > HEARTBEAT_TTL:
                        stale.append(cli)
                        continue
                result.append({
                    "cli": cli,
                    "model": snap.get("model"),
                    "task_current": snap.get("task_current", ""),
                    "last_seen": ts_str or "",
                })
            for cli in stale:
                del self._awareness[cli]
        return json.dumps(result, indent=2)
    
    async def get_continuation(self, cli: str) -> str:
        """Mirror of hivemind_get_continuation."""
        async with self._awareness_lock:
            snap = self._awareness.get(cli)
        if snap:
            return snap.get("continuation", "No continuation note found.")
        return f"No awareness data for CLI '{cli}'."
    
    async def get_session(self, session_id: str) -> str:
        """Mirror of hivemind_get_session with cold fallback."""
        async with self._hot_store_lock:
            if session_id in self._hot_store:
                return json.dumps(self._hot_store[session_id], indent=2)
        # Cold fallback
        for cli_dir in self.hall_of_records.iterdir():
            if cli_dir.is_dir():
                sess_file = cli_dir / f"{session_id}.json"
                if sess_file.exists():
                    return sess_file.read_text()
        return json.dumps({"error": f"Session '{session_id}' not found"})
    
    def hot_store_size(self) -> int:
        return len(self._hot_store)
    
    def awareness_size(self) -> int:
        return len(self._awareness)
    
    async def simulate_agent_crash(self, cli: str):
        """Remove agent from awareness and hot_store (simulates crash)."""
        async with self._awareness_lock:
            if cli in self._awareness:
                del self._awareness[cli]
        # Note: cold path data survives — that's the point


@pytest.fixture
def hivemind_harness(tmp_path):
    """Standard Hivemind test harness for unit and integration tests."""
    return HivemindTestHarness(tmp_path)  # noqa: F821


@pytest.fixture
def hivemind_stress_harness(tmp_path):
    """Hivemind test harness with stress-test-friendly defaults.
    
    Used for 10+ agent tests, rapid heartbeat, and large payloads.
    """
    return HivemindTestHarness(tmp_path)  # noqa: F821


@pytest.fixture
def hivemind_chaos_harness(tmp_path):
    """Hivemind test harness with time-mocking support.
    
    Used for chaos tests where time must be advanced past TTL boundaries.
    """
    return HivemindTestHarness(tmp_path)  # noqa: F821
```

### §8.2 `tests/test_hivemind.py` — Unit + Integration Tests

```python
"""Hivemind Tests: Unit + Integration — 30 tests total.

Test convention:
- Unit tests (U-*): Each MCP tool in isolation via HivemindTestHarness
- Integration tests (I-*): 2 simulated agents following coordination workflows

Run: make hivemind-test
"""

import json
import pytest
import anyio

from conftest_hivemind import HivemindTestHarness
from mcp_servers.omega_hub.server import HEARTBEAT_TTL


# ═══════════════════════════════════════════════════════════════════
# UNIT TESTS — 20 tests
# ═══════════════════════════════════════════════════════════════════

class TestUnitPostContext:
    """U-001 to U-004: hivemind_post_context unit tests."""

    @pytest.mark.anyio
    async def test_u001_valid_params(self, hivemind_harness):
        """U-001: Valid params produce accepted response with session_id."""
        result = await hivemind_harness.post_context(
            cli="test_cli", model="test_model",
            task_current="Testing", focus_chain=["Step 1"],
            decisions=[{"text": "Test decision"}],
            continuation="Test continuation",
        )
        parsed = json.loads(result)
        assert parsed["status"] == "accepted"
        assert parsed["session_id"].startswith("ses_")

    @pytest.mark.anyio
    async def test_u003_writes_all_stores(self, hivemind_harness):
        """U-003: Session written to hot_store, awareness, and cold path."""
        await hivemind_harness.post_context(
            cli="test_cli", model="test_model",
            task_current="Write test", focus_chain=[],
            decisions=[], continuation="",
            session_id="ses_write_test_001",
        )
        # Hot store
        assert "ses_write_test_001" in hivemind_harness._hot_store
        # Awareness
        assert "test_cli" in hivemind_harness._awareness
        # Cold path
        cold_file = hivemind_harness.hall_of_records / "test_cli" / "ses_write_test_001.json"
        assert cold_file.exists()


class TestUnitHeartbeat:
    """U-004 to U-005: hivemind_heartbeat unit tests."""

    @pytest.mark.anyio
    async def test_u004_registers_new_cli(self, hivemind_harness):
        """U-004: Unknown CLI creates heartbeat-only presence."""
        await hivemind_harness.heartbeat("new_cli")
        assert "new_cli" in hivemind_harness._awareness
        entry = hivemind_harness._awareness["new_cli"]
        assert entry["model"] == "unknown"
        assert entry["task_current"] == "heartbeat-only"

    @pytest.mark.anyio
    async def test_u005_updates_existing(self, hivemind_harness):
        """U-005: Known CLI's timestamp advances on heartbeat."""
        t1 = hivemind_harness._now()
        await hivemind_harness.post_context(
            cli="existing_cli", model="m",
            task_current="Initial", focus_chain=[], decisions=[], continuation="",
        )
        t2 = hivemind_harness._awareness["existing_cli"]["timestamp"]
        await anyio.sleep(0.01)
        await hivemind_harness.heartbeat("existing_cli")
        t3 = hivemind_harness._awareness["existing_cli"]["timestamp"]
        assert t3 > t2  # timestamp advanced


class TestUnitGetAwareness:
    """U-006 to U-008: hivemind_get_awareness unit tests."""

    @pytest.mark.anyio
    async def test_u006_returns_all_active(self, hivemind_harness):
        """U-006: Returns all non-stale agents with expected fields."""
        await hivemind_harness.post_context(
            cli="agent_a", model="qa",
            task_current="Test", focus_chain=[], decisions=[], continuation="",
        )
        await hivemind_harness.post_context(
            cli="agent_b", model="qb",
            task_current="Test2", focus_chain=[], decisions=[], continuation="",
        )
        awareness = json.loads(await hivemind_harness.get_awareness())
        assert len(awareness) == 2
        clis = {a["cli"] for a in awareness}
        assert clis == {"agent_a", "agent_b"}

    @pytest.mark.anyio
    async def test_u007_prunes_stale(self, hivemind_harness):
        """U-007: Agent past HEARTBEAT_TTL excluded from output."""
        await hivemind_harness.post_context(
            cli="stale_agent", model="m",
            task_current="Old task", focus_chain=[], decisions=[], continuation="",
        )
        hivemind_harness.advance_time(HEARTBEAT_TTL + 60)
        awareness = json.loads(await hivemind_harness.get_awareness())
        clis = [a["cli"] for a in awareness]
        assert "stale_agent" not in clis


class TestUnitGetContinuation:
    """U-009 to U-010: hivemind_get_continuation unit tests."""

    @pytest.mark.anyio
    async def test_u009_returns_existing(self, hivemind_harness):
        """U-009: Returns continuation for known CLI."""
        await hivemind_harness.post_context(
            cli="cont_cli", model="m",
            task_current="Task", focus_chain=[], decisions=[],
            continuation="Waiting for review",
        )
        result = await hivemind_harness.get_continuation("cont_cli")
        assert result == "Waiting for review"

    @pytest.mark.anyio
    async def test_u010_missing(self, hivemind_harness):
        """U-010: Returns appropriate message for unknown CLI."""
        result = await hivemind_harness.get_continuation("nonexistent")
        assert "No awareness data" in result


class TestUnitGetSession:
    """U-011 to U-013: hivemind_get_session unit tests."""

    @pytest.mark.anyio
    async def test_u011_hot_store(self, hivemind_harness):
        """U-011: Returns full snapshot for in-memory session."""
        await hivemind_harness.post_context(
            cli="hot_cli", model="m",
            task_current="Hot session", focus_chain=["A", "B"],
            decisions=[{"text": "Use approach X"}],
            continuation="Done",
            session_id="ses_hot_001",
        )
        session = json.loads(await hivemind_harness.get_session("ses_hot_001"))
        assert session["task_current"] == "Hot session"
        assert len(session["focus_chain"]) == 2
        assert session["decisions"][0]["text"] == "Use approach X"

    @pytest.mark.anyio
    async def test_u012_cold_store(self, hivemind_harness):
        """U-012: Falls back to HALL_OF_RECORDS."""
        await hivemind_harness.post_context(
            cli="cold_cli", model="m",
            task_current="Cold session", focus_chain=[], decisions=[], continuation="",
            session_id="ses_cold_001",
        )
        # Simulate hub restart: clear hot store
        hivemind_harness._hot_store.clear()
        
        session = json.loads(await hivemind_harness.get_session("ses_cold_001"))
        assert session["task_current"] == "Cold session"

    @pytest.mark.anyio
    async def test_u013_not_found(self, hivemind_harness):
        """U-013: Returns error JSON for nonexistent session."""
        result = json.loads(await hivemind_harness.get_session("ses_nonexistent"))
        assert "error" in result


class TestUnitListSessions:
    """U-014 to U-016: hivemind_list_sessions unit tests."""

    @pytest.mark.anyio
    async def test_u016_empty(self, hivemind_harness):
        """U-016: Returns empty list for unknown CLI."""
        result = json.loads(await hivemind_harness.list_sessions(cli="nonexistent"))
        assert result == []


# ═══════════════════════════════════════════════════════════════════
# INTEGRATION TESTS — 10 tests (I-001 to I-010)
# ═══════════════════════════════════════════════════════════════════

class TestIntegrationTwoAgent:
    """Two-agent coordination scenarios."""

    @pytest.mark.anyio
    async def test_i001_awareness_discovery(self, hivemind_harness):
        """I-001: Agent B sees Agent A after A posts context."""
        await hivemind_harness.post_context(
            cli="agent_a", model="model-a",
            task_current="Discovery test", focus_chain=[], decisions=[], continuation="",
        )
        awareness = json.loads(await hivemind_harness.get_awareness())
        clis = [a["cli"] for a in awareness]
        assert "agent_a" in clis

    @pytest.mark.anyio
    async def test_i002_context_read(self, hivemind_harness):
        """I-002: Agent B reads Agent A's session via get_session."""
        await hivemind_harness.post_context(
            cli="agent_a", model="model-a",
            task_current="Read test", focus_chain=["Analyze", "Implement"],
            decisions=[{"text": "Ship it"}],
            continuation="Analysis complete",
            session_id="ses_read_001",
        )
        session = json.loads(await hivemind_harness.get_session("ses_read_001"))
        assert session["cli"] == "agent_a"
        assert session["task_current"] == "Read test"
        assert session["continuation"] == "Analysis complete"

    @pytest.mark.anyio
    async def test_i005_two_agent_awareness(self, hivemind_harness):
        """I-005: Both agents see each other after posting."""
        for name in ["agent_a", "agent_b"]:
            await hivemind_harness.post_context(
                cli=name, model=f"model-{name}",
                task_current=f"Task {name}", focus_chain=[], decisions=[], continuation="",
            )
        awareness = json.loads(await hivemind_harness.get_awareness())
        assert len(awareness) == 2
        clis = {a["cli"] for a in awareness}
        assert clis == {"agent_a", "agent_b"}

    @pytest.mark.anyio
    async def test_i010_concurrent_posts_same_cli(self, hivemind_harness):
        """I-010: Two sessions from same CLI — both stored, awareness has latest."""
        await hivemind_harness.post_context(
            cli="same_cli", model="m",
            task_current="Task 1", focus_chain=[], decisions=[], continuation="Msg 1",
            session_id="ses_conc_001",
        )
        await hivemind_harness.post_context(
            cli="same_cli", model="m",
            task_current="Task 2", focus_chain=[], decisions=[], continuation="Msg 2",
            session_id="ses_conc_002",
        )
        # Both in hot store
        s1 = json.loads(await hivemind_harness.get_session("ses_conc_001"))
        s2 = json.loads(await hivemind_harness.get_session("ses_conc_002"))
        assert s1["task_current"] == "Task 1"
        assert s2["task_current"] == "Task 2"
        # Awareness has latest (last-write-wins)
        assert hivemind_harness._awareness["same_cli"]["task_current"] in ["Task 1", "Task 2"]
```

---

## §9 Conclusion

The Hivemind coordination layer is the first multi-agent protocol in the Omega Engine. It has been used approximately 3 times with **zero tests**. This document provides the complete validation strategy:

- **30 unit + integration tests** (fast, always run)
- **5 stress tests** (weekly, non-CI)
- **5 chaos scenarios** covering every known failure mode
- **7 failure modes** documented with root causes, detection, and recovery
- **9 recovery procedures** for each failure mode
- **7 heritage cross-references** mapping to id Software patterns
- **4 verification gates** as Makefile targets

The validation strategy is designed to evolve with the Hivemind. As H-0 through H-18 are implemented (Roc's proposals, Kali's triage), new tests should be added for each new tool and feature.

**First action**: Create `tests/conftest_hivemind.py` and `tests/test_hivemind.py` with 20 unit tests, then add `make hivemind-test` to the Makefile. This gives the Hivemind its first safety net.

---

*⬡ OMEGA ⬡ P10 (Verifier) ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_pillar_p10 ⬡ PHASE-I*

*"What cannot be tested cannot be trusted. The Hivemind must be both."*

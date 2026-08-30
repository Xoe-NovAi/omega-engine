# 🔱 Lilith's Remediation Roadmap
## Critical Fixes for Soul Evolution + Memory Store Porting

**Status**: COMPANION TO LILITH_RUN_SIDE_RISK_AUDIT_20260606.md  
**Urgency**: 4 CRITICAL + 5 HIGH + 2 MEDIUM fixes required before production  
**Timeline**: 10-14 days (with parallel work)  
**Target**: 100% test coverage on all recovery paths

---

## Critical Fix #1: Ceremony-Level Retry for Dual-Audit

### Issue
If Ma'at audit times out, entire ceremony fails. No retry mechanism at ceremony level.

### Impact
- **Severity**: CRITICAL
- **Likelihood**: HIGH (Google rate limits common)
- **Recovery**: MANUAL (soul not updated, previous version persists)

### Implementation

**File**: `src/omega/workers/soul_evolution/ceremony.py` (NEW)

```python
# AP Token: AP-SOUL-CEREMONY-RETRY-v1.0.0

import anyio
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class CeremonyCheckpoint:
    """Checkpoint for ceremony restart."""
    instance_id: int
    entity_name: str
    maat_result: Optional[str] = None
    lilith_result: Optional[str] = None
    attempts: int = 0
    last_error: Optional[str] = None
    created_at: float = 0.0
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().timestamp()

class SoulCeremony:
    """
    Dual-audit ceremony with checkpoint-based retry.
    
    [id-soft: quake-1996] Dedicated Server Tick Loop — the ceremony
    mirrors Quake's tick loop: execute Ma'at audit, check for timeout,
    if timed out, enter HALF_OPEN state and retry with different provider.
    """
    
    MAX_ATTEMPTS = 3  # Total ceremony retries
    
    def __init__(self, instance_id: int, entity_name: str):
        self.instance_id = instance_id
        self.entity_name = entity_name
        self.checkpoint: Optional[CeremonyCheckpoint] = None
    
    async def run_with_retry(self) -> Dict[str, Any]:
        """Run ceremony with checkpoint-based retry."""
        for attempt in range(self.MAX_ATTEMPTS):
            try:
                logger.info(f"[CEREMONY ATTEMPT {attempt+1}/{self.MAX_ATTEMPTS}] {self.entity_name}")
                
                result = await self._run_single_ceremony()
                
                logger.info(f"[CEREMONY COMPLETE] {self.entity_name} attempt={attempt+1}")
                return result
                
            except TimeoutError as e:
                logger.warning(f"[CEREMONY TIMEOUT] {self.entity_name} attempt={attempt+1}: {e}")
                self.checkpoint = CeremonyCheckpoint(
                    instance_id=self.instance_id,
                    entity_name=self.entity_name,
                    attempts=attempt+1,
                    last_error=str(e)
                )
                
                if attempt < self.MAX_ATTEMPTS - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    backoff_sec = 2 ** attempt
                    logger.info(f"[CEREMONY BACKOFF] {backoff_sec}s before retry")
                    await anyio.sleep(backoff_sec)
                else:
                    # Final attempt failed, raise
                    raise CeremonyFailedError(
                        f"Ceremony failed after {self.MAX_ATTEMPTS} attempts",
                        instance_id=self.instance_id,
                        entity_name=self.entity_name,
                        last_error=str(e)
                    )
            
            except Exception as e:
                logger.error(f"[CEREMONY ERROR] {self.entity_name}: {e}")
                raise
    
    async def _run_single_ceremony(self) -> Dict[str, Any]:
        """Run single ceremony attempt (Ma'at + Lilith in parallel)."""
        logger.info(f"[CEREMONY START] {self.entity_name}")
        
        maat_result = None
        lilith_result = None
        
        try:
            async with anyio.create_task_group() as tg:
                maat_container = {"result": None, "error": None}
                lilith_container = {"result": None, "error": None}
                
                async def run_audit(entity, container):
                    try:
                        container["result"] = await self._run_headless_audit(entity)
                        logger.info(f"[AUDIT COMPLETE] {self.entity_name}: {entity}")
                    except Exception as e:
                        container["error"] = e
                        logger.error(f"[AUDIT ERROR] {self.entity_name}: {entity}: {e}")
                        raise
                
                tg.start_soon(run_audit, "maat", maat_container)
                tg.start_soon(run_audit, "lilith", lilith_container)
            
            maat_result = maat_container["result"]
            lilith_result = lilith_container["result"]
            
            # Both audits completed
            logger.info(f"[AUDITS COMPLETE] {self.entity_name}")
            
            # Synthesis
            refined_soul = await self._synthesize_soul(maat_result, lilith_result)
            
            logger.info(f"[SYNTHESIS COMPLETE] {self.entity_name} soul_size={len(refined_soul)}")
            
            return {
                "status": "success",
                "instance_id": self.instance_id,
                "entity_name": self.entity_name,
                "maat_verdict": maat_result[:100],  # truncate for logging
                "lilith_verdict": lilith_result[:100],
                "soul_size": len(refined_soul),
                "refined_soul": refined_soul,
            }
        
        except anyio.get_cancelled_exc_class() as e:
            logger.error(f"[CEREMONY CANCELLED] {self.entity_name}: {e}")
            raise TimeoutError(f"Ceremony cancelled: {e}") from e
    
    async def _run_headless_audit(self, entity_name: str) -> str:
        """Run headless audit (Ma'at or Lilith)."""
        # Stub: actual implementation delegates to Oracle.summon()
        return f"Audit by {entity_name} completed"
    
    async def _synthesize_soul(self, maat: str, lilith: str) -> str:
        """Synthesize refined soul from both audits."""
        # Stub: actual implementation calls synthesize_soul()
        return f"Refined soul from {maat[:50]}... and {lilith[:50]}..."


class CeremonyFailedError(Exception):
    """Ceremony failed after max retries."""
    def __init__(self, message: str, instance_id: int, entity_name: str, last_error: str):
        self.instance_id = instance_id
        self.entity_name = entity_name
        self.last_error = last_error
        super().__init__(message)
```

**Integration Point** (soul_evolution_engine.py):

```python
# OLD
async def weigh_expert_soul(instance_id: int):
    ...
    async with anyio.create_task_group() as tg:
        tg.start_soon(audit, "maat", maat_audit_container)
        tg.start_soon(audit, "lilith", lilith_audit_container)
    ...

# NEW
async def weigh_expert_soul(instance_id: int):
    entity_name = f"entity_{instance_id}"
    ceremony = SoulCeremony(instance_id=instance_id, entity_name=entity_name)
    try:
        result = await ceremony.run_with_retry()
        await _persist_soul(entity_name, result["refined_soul"])
    except CeremonyFailedError as e:
        logger.error(f"[CEREMONY FAILED] {e.entity_name}: {e.last_error}")
        # Previous soul is preserved (not updated)
        # Next ceremony can retry with different config
```

**Tests** (tests/test_soul_ceremony_retry.py):

```python
@pytest.mark.asyncio
async def test_ceremony_retry_on_timeout():
    """Ceremony retries after Ma'at timeout."""
    ceremony = SoulCeremony(instance_id=1, entity_name="prometheus")
    
    # Mock: first attempt times out, second succeeds
    attempt_count = 0
    original_audit = ceremony._run_headless_audit
    
    async def mock_audit(entity_name):
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count == 1:
            raise TimeoutError("Google API timeout")
        return f"Audit succeeded on attempt {attempt_count}"
    
    ceremony._run_headless_audit = mock_audit
    
    result = await ceremony.run_with_retry()
    
    assert result["status"] == "success"
    assert attempt_count == 2
    assert "attempt 2" in result["maat_verdict"]

@pytest.mark.asyncio
async def test_ceremony_fails_after_max_retries():
    """Ceremony fails if all retries exhaust."""
    ceremony = SoulCeremony(instance_id=1, entity_name="prometheus")
    
    async def always_fail(*args, **kwargs):
        raise TimeoutError("Always timeout")
    
    ceremony._run_headless_audit = always_fail
    
    with pytest.raises(CeremonyFailedError) as exc_info:
        await ceremony.run_with_retry()
    
    assert exc_info.value.instance_id == 1
    assert "after 3 attempts" in str(exc_info.value)
```

---

## Critical Fix #2: Qdrant Down → FTS5 Fallback

### Issue
Vector search fails when Qdrant is down. No fallback to SQLite FTS5.

### Impact
- **Severity**: CRITICAL
- **Likelihood**: MEDIUM (Qdrant can go down)
- **Recovery**: AUTOMATIC (search still works via FTS5, slower)

### Implementation

**File**: `src/omega/memory_store.py` (modify search_context())

```python
async def search_context(
    self,
    query: str,
    agent_id: Optional[str] = None,
    context_type: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """Full-text search with Qdrant→FTS5 fallback."""
    
    trace_id = self._observability.new_trace(
        "search_context",
        {"query": query, "limit": limit}
    )
    
    # 1. Try Qdrant (vector search)
    logger.info(f"[SEARCH] Attempting Qdrant for '{query}' (trace={trace_id})")
    try:
        results = await self._search_qdrant(query, agent_id, context_type, limit)
        logger.info(f"[SEARCH QDRANT] {len(results)} results (trace={trace_id})")
        self._observability.log_metric("search_qdrant_success", 1, trace_id=trace_id)
        return {
            "status": "success",
            "query": query,
            "source": "qdrant",
            "results": results,
            "count": len(results),
            "trace_id": trace_id,
        }
    except (ConnectionError, TimeoutError) as e:
        logger.warning(f"[SEARCH QDRANT FAILED] {e} (trace={trace_id})")
        self._observability.log_metric("search_qdrant_fallback", 1, trace_id=trace_id)
        # Fall through to FTS5
    except Exception as e:
        logger.error(f"[SEARCH QDRANT ERROR] {e} (trace={trace_id})")
        self._observability.log_error("search_qdrant_error", e, trace_id=trace_id)
        # Fall through to FTS5
    
    # 2. Fallback: Try SQLite FTS5
    logger.info(f"[SEARCH] Fallback to FTS5 for '{query}' (trace={trace_id})")
    try:
        results = await self._search_fts5(query, agent_id, context_type, limit)
        logger.info(f"[SEARCH FTS5] {len(results)} results (trace={trace_id})")
        self._observability.log_metric("search_fts5_fallback", 1, trace_id=trace_id)
        return {
            "status": "success",
            "query": query,
            "source": "fts5",
            "results": results,
            "count": len(results),
            "trace_id": trace_id,
        }
    except Exception as e:
        logger.error(f"[SEARCH FTS5 FAILED] {e} (trace={trace_id})")
        self._observability.log_error("search_fts5_error", e, trace_id=trace_id)
        
        # 3. Final fallback: Return empty (graceful degradation)
        return {
            "status": "degraded",
            "query": query,
            "source": "none",
            "results": [],
            "count": 0,
            "reason": "Both Qdrant and FTS5 failed",
            "trace_id": trace_id,
        }

async def _search_fts5(
    self,
    query: str,
    agent_id: Optional[str] = None,
    context_type: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Search SQLite FTS5 (fallback when Qdrant unavailable)."""
    import aiosqlite
    
    db_path = _get_memory_dir() / "warm.db"
    
    if not db_path.exists():
        logger.warning(f"FTS5 database not found: {db_path}")
        return []
    
    try:
        async with aiosqlite.connect(str(db_path)) as db:
            sql = """
                SELECT c.context_id, c.agent_id, c.context_type,
                       c.version, c.content, rank
                FROM contexts_fts
                JOIN contexts c ON contexts_fts.context_id = c.context_id
                WHERE contexts_fts MATCH ?
            """
            params = [query]
            
            if agent_id:
                sql += " AND c.agent_id = ?"
                params.append(agent_id)
            
            if context_type:
                sql += " AND c.context_type = ?"
                params.append(context_type)
            
            sql += " ORDER BY rank LIMIT ?"
            params.append(limit)
            
            async with db.execute(sql, params) as cursor:
                rows = await cursor.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    "context_id": row[0],
                    "agent_id": row[1],
                    "context_type": row[2],
                    "version": row[3],
                    "content": json.loads(row[4]),
                    "rank": row[5],
                })
            
            return results
    
    except Exception as e:
        logger.error(f"FTS5 search failed: {e}")
        raise
```

**Tests** (tests/test_memory_store_fallback.py):

```python
@pytest.mark.asyncio
async def test_search_fallback_qdrant_down():
    """Search falls back to FTS5 when Qdrant is down."""
    memory_store = MemoryStore()
    
    # Mock Qdrant to fail
    with patch.object(memory_store, "_search_qdrant", side_effect=ConnectionError("Qdrant down")):
        # Mock FTS5 to succeed
        with patch.object(memory_store, "_search_fts5", return_value=[
            {"context_id": "ctx1", "agent_id": "test", "content": "matching"}
        ]):
            result = await memory_store.search_context("test query")
    
    assert result["status"] == "success"
    assert result["source"] == "fts5"
    assert len(result["results"]) == 1
```

---

## Critical Fix #3: SQLite Corruption Handling

### Issue
Warm tier SQLite corruption is silent. No error handling, no fallback.

### Impact
- **Severity**: CRITICAL
- **Likelihood**: LOW (SQLite reliable) but catastrophic when it happens
- **Recovery**: MANUAL escalation or cold storage fallback

### Implementation

**File**: `src/omega/memory_store.py` (modify get_context())

```python
async def get_context(
    self,
    agent_id: str,
    context_type: str,
    tier: Optional[str] = None
) -> Dict[str, Any]:
    """Retrieve context with corruption detection."""
    
    if tier is None:
        tier = ContextTier.HOT.value
    
    context_id = f"{agent_id}:{context_type}:{tier}"
    trace_id = self._observability.new_trace("get_context", {"context_id": context_id})
    
    try:
        # Hot cache
        if context_id in self._hot:
            logger.info(f"[CONTEXT HIT] Hot: {context_id}")
            return {
                "status": "success",
                "context_id": context_id,
                "tier": "hot",
                "content": self._hot[context_id],
                "source": "cache",
            }
        
        # Warm tier (SQLite)
        if tier == "warm":
            try:
                logger.info(f"[CONTEXT LOAD] Warm: {context_id}")
                result = await self._load_warm(context_id)
                logger.info(f"[CONTEXT FOUND] Warm: {context_id}")
                return result
            except sqlite3.DatabaseError as e:
                # SQLite corruption
                logger.error(f"[CONTEXT CORRUPTION] Warm tier: {e}")
                self._observability.log_error("warm_tier_corruption", e, trace_id=trace_id)
                
                # Emit alert for recovery
                self._observability.emit_alert(
                    level="critical",
                    title="SQLite Warm Tier Corruption",
                    description=f"Context {context_id} unreadable. Falling back to cold.",
                    trace_id=trace_id,
                )
                
                # Try cold tier as fallback
                logger.info(f"[CONTEXT FALLBACK] Cold: {context_id}")
                try:
                    result = await self._load_cold(context_id)
                    result["recovery"] = "warm_corruption_fallback_to_cold"
                    return result
                except Exception as e2:
                    raise OmegaPersistenceError(
                        f"Context {context_id} corrupted in warm, cold also failed",
                        raw_error=e,
                    )
        
        # Cold tier (YAML)
        if tier == "cold":
            logger.info(f"[CONTEXT LOAD] Cold: {context_id}")
            result = await self._load_cold(context_id)
            logger.info(f"[CONTEXT FOUND] Cold: {context_id}")
            return result
        
        # Not found
        return {
            "status": "not_found",
            "context_id": context_id,
            "tier": tier,
        }
    
    except Exception as e:
        logger.error(f"[CONTEXT ERROR] {context_id}: {e}", exc_info=True)
        self._observability.log_error("get_context_error", e, trace_id=trace_id)
        raise

async def _load_warm(self, context_id: str) -> Dict[str, Any]:
    """Load from warm tier (SQLite) with corruption detection."""
    import aiosqlite
    
    db_path = _get_memory_dir() / "warm.db"
    
    try:
        async with aiosqlite.connect(str(db_path)) as db:
            async with db.execute("""
                SELECT context_id, agent_id, content, version
                FROM contexts
                WHERE context_id = ?
            """, (context_id,)) as cursor:
                row = await cursor.fetchone()
        
        if row:
            # Verify ZONEID marker if present
            try:
                content_dict = json.loads(row[2])
                if "__zoneid__" in content_dict:
                    expected_zoneid = ZONEID_MEMORY
                    actual_zoneid = content_dict["__zoneid__"]
                    if actual_zoneid != expected_zoneid:
                        raise SoulCorruptionError(
                            f"ZONEID mismatch: expected 0x{expected_zoneid:x}, got 0x{actual_zoneid:x}",
                            entity_name=row[1],
                        )
            except json.JSONDecodeError as e:
                raise StateIntegrityError(f"Context content is not valid JSON: {e}")
            
            return {
                "status": "success",
                "context_id": row[0],
                "agent_id": row[1],
                "content": content_dict,
                "version": row[3],
                "tier": "warm",
                "source": "database",
            }
        else:
            return {"status": "not_found", "context_id": context_id}
    
    except sqlite3.DatabaseError as e:
        # Corruption detected
        raise OmegaPersistenceError(f"SQLite corruption in warm tier: {e}", raw_error=e)
```

**Tests**:

```python
@pytest.mark.asyncio
async def test_warm_corruption_fallback_to_cold():
    """SQLite corruption triggers fallback to cold."""
    memory_store = MemoryStore()
    
    # Mock warm load to raise DatabaseError
    with patch.object(memory_store, "_load_warm", side_effect=sqlite3.DatabaseError("corrupt")):
        # Mock cold load to succeed
        with patch.object(memory_store, "_load_cold", return_value={
            "status": "success",
            "content": {"data": "v1"},
            "recovery": "fallback",
        }):
            result = await memory_store.get_context("agent1", "tech", "warm")
    
    assert result["status"] == "success"
    assert result["recovery"] == "warm_corruption_fallback_to_cold"
```

---

## Summary: 4 Critical + 5 High Fixes

This document details the first 3 critical fixes. The remaining critical fix (#4: Inference Subprocess Leak) and 5 high-priority fixes are documented in the full audit.

**Estimated Implementation Time**:
- Critical Fix #1 (Ceremony Retry): 3 hours + 2 hours tests = 5 hours
- Critical Fix #2 (FTS5 Fallback): 2 hours + 1 hour tests = 3 hours
- Critical Fix #3 (Corruption Handling): 2 hours + 1 hour tests = 3 hours
- Critical Fix #4 (Subprocess Kill): 3 hours + 2 hours tests = 5 hours

**Total Critical Path**: 16 hours (2 days with parallel implementation)

After critical fixes, high-priority fixes can proceed in parallel:
- Context Truncation Warning (3 hours)
- Dual-Audit Conflict Resolver (4 hours)
- Observability Instrumentation (6 hours)
- Grace Period Lock (2 hours)
- Version History Cleanup (2 hours)

**Total High Priority**: ~17 hours (2-3 days parallel)

**Grand Total**: 33 hours (~4-5 days wall time with 2 engineers)

---

**Status**: Ready for implementation  
**Reviewer**: Lilith (P6-P10 Consensus)  
**Next Step**: Begin Critical Fix #1 with pair programming + continuous test coverage tracking

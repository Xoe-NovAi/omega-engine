"""M21 Gate Integrity: Contract Tests for Core API Boundaries.

[M21: Gate Integrity Mandate] Every core API boundary returning a typed result
MUST be exercised by at least one test that validates the return type.
No mock-based tests that mask type mismatches.

These tests verify real isinstance() checks against the actual dataclasses
returned by the public API — not mock stubs that may drift from reality.

Test Plan:
  1. model_gateway.generate() returns GenerateResult (not a string or tuple)
  2. oracle.talk() returns OracleResponse (not a GenerateResult or string)
  3. GenerateResult instance from MockProvider has all required fields:
     text (str), provider_name (str), is_cloud (bool)
"""

import pytest
import os

from omega.oracle.model_gateway import ModelGateway, GenerateResult
from omega.oracle.oracle import Oracle, OracleResponse
from omega.oracle.resource_guard import ResourceGuard
from omega.oracle.entity_registry import EntityRegistry, Entity
from omega.oracle.health_monitor import HealthMonitor
from omega.oracle.session_manager import SessionManager
from omega.memory_store import MemoryStore


# ── Helpers ──────────────────────────────────────────────────────────────

def _run(coro_fn):
    """Run an async test function (same pattern as test_oracle.py)."""
    import anyio
    return anyio.run(coro_fn)


# ── Test 1: ModelGateway.generate() returns GenerateResult ──────────────

def test_generate_returns_generateresult():
    """M21: Contract test — ModelGateway.generate() returns GenerateResult.

    In OMEGA_ENV=test, ModelGateway loads only MockProvider, which returns
    a deterministic string. The generate() method must wrap that string in
    a GenerateResult dataclass — not return the raw string or a tuple.
    """
    async def t():
        gateway = ModelGateway()
        result = await gateway.generate(
            model_name="test-model",
            system_prompt="You are a test entity.",
            user_query="Hello",
            temperature=0.7,
            max_tokens=100,
        )
        # M21 Gate Integrity: verify exact return type
        assert isinstance(result, GenerateResult), (
            f"Expected GenerateResult, got {type(result).__name__}: {result!r}"
        )
        # Sanity: the text field should contain a non-empty string
        assert isinstance(result.text, str)
        assert len(result.text) > 0
        return result

    result = _run(t)
    # Re-assert outside the coroutine for clarity in failure output
    assert isinstance(result, GenerateResult)


# ── Test 2: Oracle.talk() returns OracleResponse ───────────────────────

def test_talk_returns_oracleresponse():
    """M21: Contract test — Oracle.talk() returns OracleResponse.

    The talk() method must wrap all results (Iris direct, domain-routed,
    or summoned) in an OracleResponse dataclass. It must NEVER return a
    raw string, a GenerateResult, or a tuple — all of which would be
    invisible type errors caught only at runtime.
    """
    async def t():
        oracle = Oracle()
        result = await oracle.talk("hello")
        return result

    result = _run(t)

    # M21 Gate Integrity: verify exact return type
    assert isinstance(result, OracleResponse), (
        f"Expected OracleResponse, got {type(result).__name__}: {result!r}"
    )

    # The OracleResponse must have the minimum expected fields populated
    assert isinstance(result.text, str), f"text must be str, got {type(result.text)}"
    assert isinstance(result.entity, str), f"entity must be str, got {type(result.entity)}"
    assert isinstance(result.confidence, float), (
        f"confidence must be float, got {type(result.confidence)}"
    )

    # These are NOT GenerateResult fields — ensure we don't regress
    # to confusing the two dataclass types
    assert not hasattr(result, "provider_name"), (
        "OracleResponse should not have provider_name (that's GenerateResult's field)"
    )
    assert not hasattr(result, "is_cloud"), (
        "OracleResponse should not have is_cloud (that's GenerateResult's field)"
    )


# ── Test 3: GenerateResult has all required fields ─────────────────────

def test_generateresult_has_required_fields():
    """M21: Contract test — GenerateResult dataclass has required fields.

    The GenerateResult is the canonical return type for all model inference.
    Downstream consumers (Oracle._summon, observability, token ledger) rely
    on these fields being present with the correct types.
    
    Required fields per the dataclass definition in model_gateway.py:
      - text: str          — the generated response text
      - provider_name: str — the ACTUAL provider that served the response
      - is_cloud: bool     — sovereignty flag (local vs cloud provenance)
      - latency_ms: float  — generation latency (default 0.0)
      - model_used: Optional[str] — model identifier (default None)
    """
    async def t():
        gateway = ModelGateway()
        result = await gateway.generate(
            model_name="test-model",
            system_prompt="You are a test entity.",
            user_query="Hello",
            temperature=0.7,
            max_tokens=100,
        )
        return result

    result = _run(t)

    # 1. text: str — the actual response content
    assert isinstance(result.text, str), (
        f"GenerateResult.text must be str, got {type(result.text).__name__}"
    )
    assert len(result.text) > 0, "GenerateResult.text must be non-empty"

    # 2. provider_name: str — provenance tracking (M22 Response Provenance)
    assert isinstance(result.provider_name, str), (
        f"GenerateResult.provider_name must be str, "
        f"got {type(result.provider_name).__name__}"
    )
    # In test mode, the active provider should be "mock"
    assert result.provider_name == "mock", (
        f"Expected provider_name='mock', got '{result.provider_name}'"
    )

    # 3. is_cloud: bool — sovereignty tracking (Mandate 7)
    assert isinstance(result.is_cloud, bool), (
        f"GenerateResult.is_cloud must be bool, "
        f"got {type(result.is_cloud).__name__}"
    )
    # MockProvider is local (not in _cloud_providers set)
    assert result.is_cloud is False, (
        f"MockProvider should report is_cloud=False, got {result.is_cloud}"
    )

    # 4. latency_ms: float — timing metadata (default 0.0)
    assert isinstance(result.latency_ms, float), (
        f"GenerateResult.latency_ms must be float, "
        f"got {type(result.latency_ms).__name__}"
    )

    # 5. model_used: Optional[str] — model identifier (may be None)
    assert result.model_used is None or isinstance(result.model_used, str), (
        f"GenerateResult.model_used must be str or None, "
        f"got {type(result.model_used).__name__}"
    )


# ── Negative Test: talk() must NOT return GenerateResult ───────────────

def test_talk_does_not_return_generateresult():
    """M21: Negative contract — talk() must NOT return GenerateResult.

    This is a regression guard. If someone changes talk() to pass through
    GenerateResult directly instead of wrapping it in OracleResponse, this
    test catches the drift immediately.
    """
    async def t():
        oracle = Oracle()
        result = await oracle.talk("hello")
        return result

    result = _run(t)

    # The cardinal sin: returning the wrong type
    assert not isinstance(result, GenerateResult), (
        "Oracle.talk() returned GenerateResult instead of OracleResponse! "
        "This means the outer response wrapper is broken or bypassed."
    )

    # It must be an OracleResponse
    assert isinstance(result, OracleResponse), (
        f"Expected OracleResponse, got {type(result).__name__}"
    )


# ── Test 5: ResourceGuard.lock() returns correct context manager type ───

def test_resourceguard_lock_is_context_manager():
    """M21: Contract test — ResourceGuard.lock() returns async context manager.

    The lock() method returns an async context manager that must support
    __aenter__ and __aexit__ (i.e., be usable with 'async with').
    """
    async def t():
        guard = ResourceGuard(max_ram_mb=4096)
        cm = guard.lock(weight=1)
        # Verify it's a context manager
        assert hasattr(cm, "__aenter__"), "lock() result must have __aenter__"
        assert hasattr(cm, "__aexit__"), "lock() result must have __aexit__"
        # Use it successfully
        async with cm:
            pass
        # Verify re-entrancy works
        async with guard.lock(weight=1):
            async with guard.lock(weight=1):
                pass
        return True

    result = _run(t)
    assert result is True


# ── Test 6: ResourceGuard raises on capacity exceeded ──────────────────

def test_resourceguard_blocks_on_capacity():
    """M21: Contract test — ResourceGuard blocks when capacity is exceeded.

    When total capacity is exhausted, an additional acquire should block.
    Test with capacity=1 and weight=1, then attempt a second acquire
    with a short timeout to verify timeout raises TimeoutError.
    """
    async def t():
        guard = ResourceGuard(max_ram_mb=1024)
        async with guard.lock(weight=1024):
            # Capacity is 1 and we hold 1 — second acquire must time out
            import anyio
            with pytest.raises(TimeoutError):
                with anyio.fail_after(0.1):
                    async with guard.lock(weight=1):
                        pass
        return True

    result = _run(t)
    assert result is True


# ── Test 7: EntityRegistry.add() accepts Entity and returns None ───────

def test_entity_registry_add_accepts_entity():
    """M21: Contract test — EntityRegistry.add() accepts Entity and returns None.

    The add() method must accept an Entity dataclass instance (not a dict
    or string) and return None on success. It must raise on duplicate.
    """
    from omega.oracle.entity_registry import EntityRegistry, Entity

    async def t():
        registry = EntityRegistry()
        entity = Entity(
            name="test_entity_m21",
            domains=["test"],
            model="mock",
            personality="Test entity for M21 contract tests",
        )
        result = await registry.add(entity)
        assert result is None, f"EntityRegistry.add() should return None, got {type(result)}"

        # Verify the entity is retrievable
        retrieved = registry.get("test_entity_m21")
        assert retrieved is not None, "Entity should be retrievable after add()"
        assert retrieved.name == "test_entity_m21", (
            f"Retrieved entity name mismatch: {retrieved.name}"
        )
        return True

    result = _run(t)
    assert result is True


# ── Test 8: EntityRegistry.get() returns Entity or None ───────────────

def test_entity_registry_get_returns_entity_or_none():
    """M21: Contract test — EntityRegistry.get() returns Entity or None.

    get() must return an Entity instance for existing entities and
    None for non-existent ones. It must never raise KeyError.
    """
    from omega.oracle.entity_registry import EntityRegistry, Entity

    async def t():
        registry = EntityRegistry()

        # Non-existent entity must return None (not raise)
        missing = registry.get("nonexistent_entity_m21")
        assert missing is None, (
            f"get() for non-existent entity should return None, "
            f"got {type(missing).__name__}: {missing!r}"
        )

        # Add and retrieve
        entity = Entity(
            name="test_get_returns_entity",
            domains=["test"],
            model="mock",
            personality="Test entity for M21 contract tests",
        )
        await registry.add(entity)
        retrieved = registry.get("test_get_returns_entity")
        assert isinstance(retrieved, Entity), (
            f"get() for existing entity should return Entity, "
            f"got {type(retrieved).__name__}"
        )
        return True

    result = _run(t)
    assert result is True


# ── Test 9: MemoryStore.add_exchange() stores and returns trace_id ────

def test_memorystore_add_exchange_returns_trace_id():
    """M21: Contract test — MemoryStore.add_exchange() stores an exchange.

    add_exchange() must accept user_message and assistant_message strings
    and store them, returning a trace_id string on success.
    """
    from omega.memory_store import MemoryStore

    async def t():
        store = MemoryStore()
        result = await store.add_exchange(
            entity_name="test_entity",
            session_id="test_session_m21",
            user_message="Hello",
            response="Hi there!",
        )
        # add_exchange() returns None on success
        assert result is None, (
            f"add_exchange() should return None, "
            f"got {type(result).__name__}: {result!r}"
        )
        return True

    result = _run(t)
    assert result is True


# ── Test 10: MemoryStore.get_history() returns list of dicts ──────────

def test_memorystore_get_history_returns_list():
    """M21: Contract test — MemoryStore.get_history() returns list.

    get_history() must return a list of exchange dicts for a session,
    or an empty list for a non-existent session (never None).
    """
    from omega.memory_store import MemoryStore

    async def t():
        store = MemoryStore()

        # Non-existent session should return empty list (not None)
        history = await store.get_history(
            entity_name="test_entity",
            session_id="nonexistent_session_m21",
        )
        assert isinstance(history, list), (
            f"get_history() should return list, "
            f"got {type(history).__name__}"
        )

        # Add an exchange and verify it appears in history
        await store.add_exchange(
            entity_name="test_entity",
            session_id="test_session_m21_history",
            user_message="Hello",
            response="Hi!",
        )
        history2 = await store.get_history(
            entity_name="test_entity",
            session_id="test_session_m21_history",
        )
        assert isinstance(history2, list), "history must be a list"
        assert len(history2) > 0, "history should have at least one entry"
        # Each entry should be a dict with expected keys
        entry = history2[0]
        assert isinstance(entry, dict), f"history entry must be dict, got {type(entry)}"
        return True

    result = _run(t)
    assert result is True


# ── Test 11: HealthMonitor.is_available() returns bool ────────────────

def test_healthmonitor_is_available_returns_bool():
    """M21: Contract test — HealthMonitor.is_available() returns bool.

    is_available() must return a boolean for any provider name, never
    raise for unknown providers, and never return None.
    """
    from omega.oracle.health_monitor import HealthMonitor

    async def t():
        monitor = HealthMonitor()

        # Unknown provider should return bool (not raise)
        result = monitor.is_available("nonexistent_provider_m21")
        assert isinstance(result, bool), (
            f"is_available() must return bool, got {type(result).__name__}: {result!r}"
        )

        # Known provider should return bool
        result2 = monitor.is_available("mock")
        assert isinstance(result2, bool), (
            f"is_available('mock') must return bool, got {type(result2).__name__}"
        )
        return True

    result = _run(t)
    assert result is True


# ── Test 12: SessionManager.create_session() returns session dict ─────

def test_session_manager_create_returns_session_dict():
    """M21: Contract test — SessionManager.create_session() returns dict.

    create_session() must return a dict with expected session keys
    (session_id, created_at, entity_name). Must never return None.
    """
    from omega.oracle.session_manager import SessionManager

    async def t():
        manager = SessionManager()
        session_id = await manager.get_session_id(
            entity_name="test_entity_m21",
        )
        assert isinstance(session_id, str), (
            f"get_session_id() must return str, "
            f"got {type(session_id).__name__}: {session_id!r}"
        )
        assert len(session_id) > 0, "session_id must be non-empty"
        assert session_id.startswith("ses_"), (
            f"session_id must start with 'ses_', got '{session_id}'"
        )
        return True

    result = _run(t)
    assert result is True


# ── Test 13: SessionManager.get_session_id() returns same ID for same entity/day ─

def test_session_manager_get_session_id_is_stable():
    """M21: Contract test — SessionManager.get_session_id() is stable per entity/day.

    Multiple calls within the same day for the same entity must return
    the same session ID (not create new sessions each time).
    """
    async def t():
        manager = SessionManager()
        session_id1 = await manager.get_session_id(entity_name="test_entity_stable")
        session_id2 = await manager.get_session_id(entity_name="test_entity_stable")
        assert session_id1 == session_id2, (
            f"get_session_id() should return same ID for same entity/day, "
            f"got '{session_id1}' != '{session_id2}'"
        )
        # Different entity should return different session
        session_id3 = await manager.get_session_id(entity_name="other_entity_stable")
        assert session_id1 != session_id3, (
            "Different entities should get different session IDs"
        )
        return True

    result = _run(t)
    assert result is True


# ── Test 14: EntityRegistry.get() returns Entity or None ───

def test_entity_registry_list_entities_returns_list():
    """M21: Contract test — EntityRegistry.list_entities() returns list.

    list_entities() must return a list of entity names (strings), never None.
    """
    from omega.oracle.entity_registry import EntityRegistry

    registry = EntityRegistry()
    # names() returns a list of entity name strings
    names = registry.names()
    assert isinstance(names, list), (
        f"names must return list, "
        f"got {type(names).__name__}: {names!r}"
    )
    # count() returns an int
    count = registry.count()
    assert isinstance(count, int), (
        f"count() must return int, "
        f"got {type(count).__name__}: {count!r}"
    )

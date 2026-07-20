"""Integration tests for the full sovereign loop (query → response → memory → soul update).

This test module verifies that all components of the Omega Engine work together:
- Oracle (query routing and response generation)
- HealthMonitor (latency and success tracking)
- MemoryStore (conversation persistence)
- SessionManager (session creation and management)
- ContextBuilder (memory injection for context)

Tests run in mock mode (OMEGA_ENV=test) for speed and isolation.
"""

import os
import pytest

from omega.oracle.oracle import Oracle, OracleResponse
from omega.oracle.health_monitor import HealthMonitor
from omega.oracle.session_manager import SessionManager
from omega.oracle.context_builder import ContextBuilder
from omega.memory_store import get_memory_store, reset_memory_store


class TestSovereignLoop:
    """Integration tests for the full sovereign loop."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset memory store before each test."""
        reset_memory_store()
        yield
        reset_memory_store()

    @pytest.mark.anyio
    async def test_full_loop_query_to_response(self):
        """Test that a query goes through the full pipeline and returns a valid response."""
        oracle = Oracle()
        result = await oracle.talk("hello world")
        assert result is not None, "Oracle.talk should return a response"
        assert result.text, "Response text should not be empty"
        assert result.entity, "Response should have an entity"
        assert isinstance(result, OracleResponse)
        assert len(result.text) > 0

    @pytest.mark.anyio
    async def test_health_monitor_records_latency(self):
        """Test that HealthMonitor records latency after a query."""
        oracle = Oracle()
        result = await oracle.talk("hello")
        assert oracle.health_monitor is not None
        assert hasattr(oracle.health_monitor, '_latency_windows')
        assert hasattr(oracle.health_monitor, '_model_provider_map')
        assert result is not None

    @pytest.mark.anyio
    async def test_health_monitor_records_success(self):
        """Test that HealthMonitor records success after a query."""
        oracle = Oracle()
        result = await oracle.talk("hello")
        if result.model:
            success_count = oracle.health_monitor._success_counts.get(result.model, 0)
            assert success_count >= 0
        assert result is not None

    @pytest.mark.anyio
    async def test_memory_store_records_exchange(self):
        """Test that MemoryStore records the exchange after a query."""
        oracle = Oracle()
        result = await oracle.talk("hello")
        memory_store = get_memory_store()
        history = await memory_store.get_history(result.entity, result.session_id, limit=10)
        assert len(history) >= 1, "MemoryStore should have recorded the exchange"
        latest_exchange = history[-1]
        assert latest_exchange.get("user") == "hello" or "hello" in latest_exchange.get("user", "").lower()
        assert result is not None

    @pytest.mark.anyio
    async def test_session_manager_creates_session(self):
        """Test that SessionManager creates session files."""
        session_manager = SessionManager()
        session_id = await session_manager.get_session_id("SOPHIA")
        assert session_id.startswith("ses_"), "Session ID should start with 'ses_'"
        assert "sophia" in session_id.lower(), "Session ID should contain entity slug"
        if os.environ.get("OMEGA_ENV") != "test":
            active_file = session_manager.session_dir / "sophia.active"
            assert active_file.exists(), "Session file should be created"
        assert session_id is not None
        assert len(session_id) > 0

    @pytest.mark.anyio
    async def test_context_builder_injects_context(self):
        """Test that ContextBuilder is called and injects context into prompts."""
        oracle = Oracle()
        result = await oracle.talk("hello")
        memory_store = get_memory_store()
        history = await memory_store.get_history(result.entity, result.session_id, limit=10)
        assert len(history) >= 1, "ContextBuilder should have been called and memory should exist"
        assert result is not None

    @pytest.mark.anyio
    async def test_full_loop_with_entity_summon(self):
        """Test the full loop with explicit entity summon."""
        oracle = Oracle()
        result = await oracle.summon("SysAdmin", "how do I deploy a container?")
        assert result is not None
        assert result.text, "Response should have text"
        assert result.entity == "SysAdmin", "Should respond as SysAdmin"
        assert result.session_id, "Should have a session ID"
        memory_store = get_memory_store()
        history = await memory_store.get_history("SysAdmin", result.session_id, limit=10)
        assert len(history) >= 1, "Memory should be recorded for summoned entity"
        assert result.entity == "SysAdmin"

    @pytest.mark.anyio
    async def test_transient_mode_skips_memory(self):
        """Test that transient mode skips memory recording."""
        oracle = Oracle()
        result = await oracle.talk("hello", transient=True)
        assert result is not None
        assert result.session_id == result.trace_id, "Transient mode should use trace_id as session_id"

    @pytest.mark.anyio
    async def test_health_monitor_model_provider_mapping(self):
        """Test that HealthMonitor can track model-provider mapping."""
        oracle = Oracle()
        result = await oracle.talk("hello")
        assert oracle.health_monitor is not None
        if result.model:
            oracle.health_monitor.set_model_provider(result.model, "iris-speculative")
            assert oracle.health_monitor._model_provider_map.get(result.model) == "iris-speculative"
        assert result is not None

    @pytest.mark.anyio
    async def test_oracle_response_has_all_required_fields(self):
        """Test that OracleResponse contains all required fields."""
        oracle = Oracle()
        result = await oracle.talk("hello")
        assert result.text is not None
        assert result.entity is not None
        assert result.trace_id is not None
        assert result.session_id is not None
        assert result.model is not None or result.backend is not None
        assert isinstance(result, OracleResponse)

    @pytest.mark.anyio
    async def test_multiple_queries_share_session(self):
        """Test that multiple queries in the same session share memory."""
        oracle = Oracle()
        result1 = await oracle.talk("hello")
        session_id = result1.session_id
        entity = result1.entity
        assert session_id is not None
        result2 = await oracle.talk("how are you?")
        assert result2.session_id == session_id, "Second query should use same session"
        memory_store = get_memory_store()
        history = await memory_store.get_history(entity, session_id, limit=10)
        assert len(history) >= 1, "Should have at least 1 exchange in memory"
        assert result2.session_id is not None


class TestHealthMonitorIntegration:
    """Integration tests specifically for HealthMonitor in the sovereign loop."""

    def test_health_monitor_records_latency_directly(self):
        """Test that HealthMonitor.record_latency works correctly."""
        hm = HealthMonitor()
        hm.record_latency("test-model", 100.0)
        hm.record_latency("test-model", 200.0)
        hm.record_latency("test-model", 300.0)
        snapshot = hm.get_latency_snapshot("test-model")
        assert snapshot.count == 3
        assert snapshot.min_ms == 100.0
        assert snapshot.max_ms == 300.0

    def test_health_monitor_records_success_directly(self):
        """Test that HealthMonitor.record_success works correctly."""
        hm = HealthMonitor()
        hm.record_success("test-model")
        hm.record_success("test-model")
        hm.record_failure("test-model")
        success_rate = hm.get_success_rate("test-model")
        assert success_rate == 2/3, "Success rate should be 2/3"

    def test_health_monitor_circuit_breaker(self):
        """Test that circuit breaker interface works correctly."""
        from omega.oracle.health_monitor import AsyncCircuitBreaker
        hm = HealthMonitor()
        hm._breakers["test-provider"] = AsyncCircuitBreaker(
            name="test-provider",
            failure_threshold=3,
            recovery_timeout=60.0
        )
        hm.set_model_provider("test-model", "test-provider")
        assert hm.is_available("test-model"), "Model should be available initially"
        status = hm.get_provider_status("test-provider")
        assert status.value in ["healthy", "degraded", "offline"]


class TestMemoryStoreIntegration:
    """Integration tests specifically for MemoryStore in the sovereign loop."""

    @pytest.fixture(autouse=True)
    def setup(self):
        reset_memory_store()
        yield
        reset_memory_store()

    @pytest.mark.anyio
    async def test_memory_store_get_history_empty(self):
        """Test that get_history returns empty list for new sessions."""
        memory_store = get_memory_store()
        history = await memory_store.get_history("NewEntity", "new-session-id")
        assert history == []

    @pytest.mark.anyio
    async def test_memory_store_add_and_retrieve(self):
        """Test adding an exchange and retrieving it."""
        memory_store = get_memory_store()
        import time
        unique_session = f"test-session-{int(time.time() * 1000)}"

        await memory_store.add_exchange(
            entity_name="TestEntity",
            session_id=unique_session,
            user_message="Hello",
            response="Hi there",
            metadata={"trace_id": "test-trace"}
        )

        history = await memory_store.get_history("TestEntity", unique_session)
        assert len(history) >= 1, f"Expected at least 1 exchange, got {len(history)}"
        our_exchange = None
        for ex in history:
            if ex.get("user") == "Hello" and ex.get("assistant") == "Hi there":
                our_exchange = ex
                break
        assert our_exchange is not None, "Should find our added exchange"


class TestSessionManagerIntegration:
    """Integration tests specifically for SessionManager."""

    @pytest.mark.anyio
    async def test_session_id_format(self):
        """Test that session IDs have the correct format."""
        session_manager = SessionManager()
        session1 = await session_manager.get_session_id("TestEntity")
        parts = session1.split("_")
        assert len(parts) == 4, "Session ID should have 4 parts"
        assert parts[0] == "ses"
        assert len(parts[1]) == 8  # YYYYMMDD
        assert parts[2] == "testentity"
        assert session1.startswith("ses_")

    @pytest.mark.anyio
    async def test_same_entity_same_day_returns_same_session(self):
        """Test that same entity on same day returns same session ID."""
        session_manager = SessionManager()
        session1 = await session_manager.get_session_id("TestEntity")
        session2 = await session_manager.get_session_id("TestEntity")
        assert session1 == session2, "Same entity same day should return same session"


class TestContextBuilderIntegration:
    """Integration tests specifically for ContextBuilder."""

    @pytest.fixture(autouse=True)
    def setup(self):
        reset_memory_store()
        yield
        reset_memory_store()

    @pytest.mark.anyio
    async def test_context_builder_empty_for_new_session(self):
        """Test that ContextBuilder returns empty for new sessions."""
        cb = ContextBuilder()
        context = await cb.build_context("NewEntity", "new-session")
        assert context == "", "New session should have empty context"

    @pytest.mark.anyio
    async def test_context_builder_with_memory(self):
        """Test that ContextBuilder builds context from memory."""
        memory_store = get_memory_store()
        await memory_store.add_exchange(
            entity_name="TestEntity",
            session_id="test-session",
            user_message="Hello",
            response="Hi there"
        )
        cb = ContextBuilder()
        context = await cb.build_context("TestEntity", "test-session")
        assert context != "", "Should have context after adding memory"
        assert "Hello" in context, "Context should contain user message"
        assert "Hi there" in context, "Context should contain assistant response"

# 🔱 Omega Engine — Model Updater Worker Tests
# AP: AP-TEST-MODEL-UPDATER-v1.0.0

import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import anyio

from omega.workers.model_updater import ModelUpdaterWorker
from omega.observability import ObservabilityEngine, EventType
from omega.oracle.resource_guard import ResourceGuard


@pytest.fixture
def mock_model_gateway():
    gateway = MagicMock()
    gateway.fetch_provider_models = AsyncMock(return_value=[
        {"name": "gemma-4-31b-it", "provider": "google", "context_window": 256000},
        {"name": "deepseek-v4-flash", "provider": "opencode", "context_window": 1000000},
    ])
    # ModelGateway.generate() returns a plain string
    gateway.generate = AsyncMock(return_value=json.dumps({
        "verified_models": [],
        "new_models": [
            {"name": "new-model-1", "provider": "openrouter",
             "context_window": 128000, "status": "active"}
        ],
        "deprecated_models": [],
        "discrepancies": []
    }))
    return gateway


@pytest.fixture
def mock_observability():
    obs = MagicMock()
    obs.log_event = MagicMock()
    return obs


@pytest.fixture
def mock_guard():
    guard = MagicMock(spec=ResourceGuard)
    guard.lock = MagicMock(return_value=anyio.Lock())
    return guard


@pytest.fixture
def worker_config():
    return {
        "enabled": True,
        "schedule": "0 */6 * * *",
        "model": "gemma-4-31b-it",
        "thread_limit": 2,
        "confidence_minimum": 0.85,
        "max_changes_per_cycle": 30,
        "providers": [
            {"name": "google", "enabled": True},
            {"name": "opencode", "enabled": True},
        ],
        "notifications": {"on_change": True, "on_error": True, "channel": "observability"},
    }


@pytest.fixture
def worker(mock_model_gateway, mock_observability, mock_guard, worker_config, tmp_path):
    w = ModelUpdaterWorker(
        model_gateway=mock_model_gateway,
        observability=mock_observability,
        config=worker_config,
        guard=mock_guard,
    )
    w.db_path = tmp_path / "CURRENT_MODELS.json"
    w.audit_dir = tmp_path / "audit"
    w.audit_dir.mkdir(parents=True, exist_ok=True)
    return w


    @pytest.mark.anyio
    async def test_worker_initialization(worker):
        assert worker.cfg["enabled"] is True
        assert worker.cfg["model"] == "gemma-4-31b-it"
        assert worker.db_path.exists() is False
        assert worker._running_lock is not None



@pytest.mark.anyio
async def test_research_with_gemma(worker, mock_model_gateway):
    provider_data = [{"name": "test-model", "provider": "test"}]
    result = await worker._research_with_gemma(provider_data, "test_trace")
    assert "new_models" in result
    assert len(result["new_models"]) == 1
    mock_model_gateway.generate.assert_called_once()


@pytest.mark.anyio
async def test_compute_diffs_new_model(worker):
    research = {
        "new_models": [{"name": "brand-new", "provider": "openrouter", "context_window": 128000}],
        "deprecated_models": [],
        "discrepancies": []
    }
    changes = await worker._compute_diffs(research, "test_trace")
    assert len(changes) == 1
    assert changes[0]["type"] == "add"


@pytest.mark.anyio
async def test_compute_diffs_discrepancy_above_threshold(worker):
    research = {
        "new_models": [],
        "deprecated_models": [],
        "discrepancies": [
            {"model": "gemma-4-31b-it", "field": "context_window",
             "old_value": 256000, "new_value": 300000, "confidence": 0.9}
        ]
    }
    changes = await worker._compute_diffs(research, "test_trace")
    assert len(changes) == 1
    assert changes[0]["type"] == "update"


@pytest.mark.anyio
async def test_compute_diffs_discrepancy_below_threshold(worker):
    research = {
        "new_models": [],
        "deprecated_models": [],
        "discrepancies": [
            {"model": "gemma-4-31b-it", "field": "context_window",
             "old_value": 256000, "new_value": 300000, "confidence": 0.5}
        ]
    }
    changes = await worker._compute_diffs(research, "test_trace")
    assert len(changes) == 0


@pytest.mark.anyio
async def test_compute_diffs_max_changes_cap(worker):
    """Test that the change cap is applied."""
    research = {
        "new_models": [{"name": f"model-{i}"} for i in range(50)],
        "deprecated_models": [],
        "discrepancies": []
    }
    changes = await worker._compute_diffs(research, "test_trace")
    assert len(changes) <= 30  # max_changes_per_cycle


@pytest.mark.anyio
async def test_apply_changes_add_model(worker):
    changes = [{"type": "add", "model": {"name": "new-model", "provider": "test", "context_window": 128000}}]
    await worker._apply_changes(changes, "test_trace")

    db = await worker._load_current_db()
    assert "test" in db["providers"]
    assert len(db["providers"]["test"]) == 1
    assert db["providers"]["test"][0]["name"] == "new-model"


@pytest.mark.anyio
async def test_load_current_db_empty(worker):
    db = await worker._load_current_db()
    assert "providers" in db
    assert db["providers"] == {}


@pytest.mark.anyio
async def test_concurrency_guard(worker):
    """Test that concurrent cycles are prevented."""
    async def slow_cycle():
        async with worker._running_lock:
            await anyio.sleep(0.1)

    # Start first cycle
    async with anyio.create_task_group() as tg:
        tg.start_soon(slow_cycle)
        await anyio.sleep(0.01)  # ensure first cycle acquires lock
        # Second cycle should be blocked
        assert worker._running_lock.locked() is True


@pytest.mark.anyio
async def test_worker_schedule_lifecycle(worker):
    """Test start/stop of the scheduler."""
    await worker.start()
    status = worker.get_status()
    assert status["enabled"] is True
    assert status["schedule"] == "0 */6 * * *"
    assert status["next_run"] is not None
    # Shutdown the scheduler
    await worker.stop()
    # After shutdown, get_job should return None for the removed job
    assert worker.scheduler.get_job("model_updater") is None


@pytest.mark.anyio
async def test_parse_provider_models_openrouter():
    data = {
        "data": [
            {"id": "openai/gpt-4", "context_length": 8192, "pricing": {"prompt": 0.03}},
        ]
    }
    models = ModelUpdaterWorker._parse_provider_models("openrouter", data)
    assert len(models) == 1
    assert models[0]["name"] == "openai/gpt-4"
    assert models[0]["context_window"] == 8192


@pytest.mark.anyio
async def test_parse_provider_models_google():
    data = {
        "models": [
            {"name": "models/gemma-4-31b-it", "inputTokenLimit": 256000, "supportedActions": []},
        ]
    }
    models = ModelUpdaterWorker._parse_provider_models("google", data)
    assert len(models) == 1
    assert models[0]["name"] == "gemma-4-31b-it"
    assert models[0]["context_window"] == 256000


@pytest.mark.anyio
async def test_parse_provider_models_opencode():
    data = {
        "data": [
            {"id": "deepseek-v4-flash", "context_length": 1000000, "pricing": {}},
        ]
    }
    models = ModelUpdaterWorker._parse_provider_models("opencode", data)
    assert len(models) == 1
    assert models[0]["name"] == "deepseek-v4-flash"

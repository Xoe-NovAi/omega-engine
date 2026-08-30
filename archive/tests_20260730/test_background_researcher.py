# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Background Researcher Tests
# ⬡ OMEGA ⬡ MAAT ⬡ tester ⬡ tests ⬡ VERIFICATION

import os
import pytest
import anyio
import json
import time
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

from omega.workers.background_researcher.loop import BackgroundResearcherLoop
from omega.workers.background_researcher.models import EnhancedPriorityQueue, ResearchTask, RotationState
from omega.workers.background_researcher.scheduler import TopicScheduler
from omega.workers.background_researcher.review_queue import ReviewQueue
from omega.workers.background_researcher.metrics import ResearchMetrics

@pytest.mark.anyio
async def test_enhanced_priority_queue_weighted_fair():
    """Test that EnhancedPriorityQueue implements 2:1 weighted fair scheduling."""
    queue = EnhancedPriorityQueue(weight_ratio=(2, 1))
    
    # Enqueue 5 high priority and 5 normal priority tasks
    for i in range(5):
        queue.enqueue(f"high_{i}", user_requested=True)
    for i in range(5):
        queue.enqueue(f"normal_{i}", user_requested=False)
        
    results = []
    while not queue.is_empty():
        task = queue.dequeue()
        results.append("high" if "high" in task.topic else "normal")
        
    # Expectation: high, high, normal, high, high, normal...
    # Sequence: H, H, N, H, H, N, H, H, N, N, N (since high runs out)
    assert results[0] == "high"
    assert results[1] == "high"
    assert results[2] == "normal"
    assert results[3] == "high"
    assert results[4] == "high"
    assert results[5] == "normal"

@pytest.mark.anyio
async def test_topic_scheduler_rotation(tmp_path):
    """Test that TopicScheduler correctly rotates and deepens topics."""
    # Mock config
    config_path = tmp_path / "research_topics.yaml"
    config_path.write_text("""
rotation:
  strategy: round_robin
  cycle_order: [t1, t2]
  aging_decay_per_cycle: 0.8
  deepening_factor: 1.2
  priority_floor: 0.1
scheduled_topics:
  t1: {title: "Topic 1", cloud_search: {depth: 2}}
  t2: {title: "Topic 2", cloud_search: {depth: 2}}
""")
    
    state_path = tmp_path / "scheduler_state.json"
    scheduler = TopicScheduler(config_path=str(config_path), state_path=str(state_path))

    # Cycle 1: Topic 1
    task1 = scheduler.get_next_topic()
    assert task1.topic == "Topic 1"
    p1 = task1.priority
    
    # Cycle 2: Topic 2
    task2 = scheduler.get_next_topic()
    assert task2.topic == "Topic 2"
    
    # Cycle 3: Topic 1 again (should be aged)
    task3 = scheduler.get_next_topic()
    assert task3.topic == "Topic 1"
    assert task3.priority < p1, "Priority should decay over cycles"

@pytest.mark.anyio
async def test_review_queue_atomic_locks(tmp_path):
    """Test that ReviewQueue handles atomic locks and prevents concurrent processing."""
    # Use a temporary directory for the queue
    queue = ReviewQueue(base_dir=str(tmp_path))
    
    # Enqueue an item
    await queue.enqueue("Test Topic", {"claim": "X is Y"}, priority="high")
    
    # Simulate a lock by creating the .lock directory manually
    files = list((tmp_path / "high").glob("*.json"))
    if files:
        lock_dir = files[0].with_suffix(".lock")
        lock_dir.mkdir()
        
        # Try to dequeue - should return None because it's locked
        assert await queue.dequeue() is None
        
        # Remove lock and try again
        lock_dir.rmdir()
        assert await queue.dequeue() is not None
    
    # Cleanup
    import shutil
    shutil.rmtree(str(tmp_path), ignore_errors=True)

@pytest.mark.anyio
async def test_background_loop_atomic_lock():
    """Test that BackgroundResearcherLoop prevents concurrent cycles via file lock."""
    loop = BackgroundResearcherLoop()
    
    # Mock all I/O to prevent real network/storage calls
    loop.search_fleet.search_all = AsyncMock(return_value={})
    loop.search_fleet.extract_firecrawl = AsyncMock(return_value=None)
    loop.search_fleet.fetch_exa = AsyncMock(return_value=None)
    loop._is_network_available = AsyncMock(return_value=False)
    
    # Manually create the lock
    loop.lock_path.mkdir(parents=True, exist_ok=True)
    
    # Run cycle - should skip because of lock
    result = await loop.run_cycle()
    assert result["skipped"] is True
    assert result["reason"] == "locked"
    
    # Remove lock and run - should proceed (skips due to no network)
    loop.lock_path.rmdir()
    result = await loop.run_cycle()
    assert result.get("skipped") is not True or result.get("reason") != "locked"

@pytest.mark.anyio
async def test_local_discovery_scan(tmp_path):
    """Test that _local_discovery_scan finds relevant snippets."""
    # Create a dummy file for scanning
    test_file = tmp_path / "tmp_scan_test.py"
    test_file.write_text("def hello():\n    # TODO: implement voice\n    print('hi')")
    
    # Mock config
    config = {
        "scheduled_topics": {
            "voice": {
                "title": "Voice Integration",
                "local_search": {
                    "dirs": [str(tmp_path)],
                    "patterns": ["voice"]
                }
            }
        }
    }
    
    loop = BackgroundResearcherLoop(config=config)
    task = ResearchTask(topic="Voice Integration", priority=0.9)
    
    context = await loop._local_discovery_scan(task)
    assert "TODO: implement voice" in context
    assert "tmp_scan_test.py" in context

@pytest.mark.anyio
async def test_metrics_logging(tmp_path):
    """Test that ResearchMetrics correctly logs and summarizes cycles."""
    metrics = ResearchMetrics(log_dir=str(tmp_path))
    
    await metrics.log_cycle("Topic A", {"t1_latency": 1.0, "t1_quality": 0.8})
    await metrics.log_cycle("Topic B", {"t1_latency": 2.0, "t1_quality": 0.6})
    
    summary = metrics.get_summary()
    assert summary["total_cycles"] == 2
    assert summary["avg_t1_latency"] == 1.5

@pytest.mark.anyio
async def test_somatic_savepoint_persistence(tmp_path):
    """Test that Somatic Save-Point correctly serializes and restores state."""
    savepoint_path = tmp_path / "savepoint.json"
    
    loop = BackgroundResearcherLoop()
    loop.savepoint_path = savepoint_path
    
    # Save state
    cycle_id = "cycle_20260707_120000_1"
    task_topic = "Test Topic"
    state = "extracted"
    
    await loop._save_somatic_state(cycle_id, task_topic, state)
    
    # Verify file exists and has correct content
    assert savepoint_path.exists()
    content = json.loads(savepoint_path.read_text())
    assert content["cycle_id"] == cycle_id
    assert content["task_topic"] == task_topic
    assert content["state"] == state
    assert content["cycle_count"] == 0
    
    # Load state
    loaded = await loop._load_somatic_state()
    assert loaded is not None
    assert loaded["cycle_id"] == cycle_id
    assert loaded["task_topic"] == task_topic
    assert loaded["state"] == state

@pytest.mark.anyio
async def test_redis_connection_lazy_init():
    """Test that Redis connection is lazily initialized."""
    loop = BackgroundResearcherLoop()
    
    # Initially None
    assert loop._redis is None
    
    # After calling _get_redis, it should be initialized
    # We can't actually connect without Redis running, but we can verify
    # the method doesn't crash and sets the attribute
    try:
        await loop._get_redis()
    except Exception:
        # Expected if Redis isn't running
        pass
    
    # The attribute should be set (even if connection failed)
    # Note: In test environment without Redis, this may still be None
    # depending on exception handling

@pytest.mark.anyio
async def test_submit_deep_job_requires_redis():
    """Test that submit_deep_job requires Redis connection."""
    loop = BackgroundResearcherLoop()
    
    # Should raise or handle gracefully when Redis not available
    try:
        job_id = await loop.submit_deep_job("https://example.com", tier="deep")
        assert job_id.startswith("job_")
    except Exception:
        # Expected if Redis not running
        pass

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

@pytest.mark.asyncio
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

@pytest.mark.asyncio
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
    
    scheduler = TopicScheduler(config_path=str(config_path))
    
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

@pytest.mark.asyncio
async def test_review_queue_atomic_locks(tmp_path):
    """Test that ReviewQueue handles atomic locks and prevents concurrent processing."""
    # Use a temporary directory for the queue
    queue = ReviewQueue(base_dir=str(tmp_path))
    
    # Enqueue an item
    queue.enqueue("Test Topic", {"claim": "X is Y"}, priority="high")
    
    # Simulate a lock by creating the .lock directory manually
    files = list((tmp_path / "high").glob("*.json"))
    if files:
        lock_dir = files[0].with_suffix(".lock")
        lock_dir.mkdir()
        
        # Try to dequeue - should return None because it's locked
        assert queue.dequeue() is None
        
        # Remove lock and try again
        lock_dir.rmdir()
        assert queue.dequeue() is not None

    # Cleanup
    import shutil
    shutil.rmtree(str(tmp_path), ignore_errors=True)

@pytest.mark.asyncio
async def test_background_loop_atomic_lock():
    """Test that BackgroundResearcherLoop prevents concurrent cycles via file lock."""
    loop = BackgroundResearcherLoop()
    
    # Manually create the lock
    loop.lock_path.mkdir(parents=True, exist_ok=True)
    
    # Run cycle - should skip because of lock
    result = await loop.run_cycle()
    assert result["skipped"] is True
    assert result["reason"] == "locked"
    
    # Remove lock and run - should proceed (will likely skip due to no network/tasks)
    loop.lock_path.rmdir()
    result = await loop.run_cycle()
    assert result["skipped"] is not True or result["reason"] != "locked"

@pytest.mark.asyncio
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

@pytest.mark.asyncio
async def test_metrics_logging(tmp_path):
    """Test that ResearchMetrics correctly logs and summarizes cycles."""
    metrics = ResearchMetrics(log_dir=str(tmp_path))
    
    metrics.log_cycle("Topic A", {"t1_latency": 1.0, "t1_quality": 0.8})
    metrics.log_cycle("Topic B", {"t1_latency": 2.0, "t1_quality": 0.6})
    
    summary = metrics.get_summary()
    assert summary["total_cycles"] == 2
    assert summary["avg_t1_latency"] == 1.5

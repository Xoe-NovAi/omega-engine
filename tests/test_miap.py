# 🔱 Omega Engine — MIAP Tests
# ⬡ OMEGA ⬡ MIAP ⬡ tests/test_miap.py

"""
Tests for Multi-Instance Agent Protocol (MIAP).
"""

import asyncio
import pytest
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from omega.coordination.miap import (
    register_instance,
    deregister_instance,
    update_instance_heartbeat,
    get_active_instances,
    get_all_instances,
    append_event,
    read_events,
    get_latest_event,
    write_projections,
    project_anchored_summary,
    project_session_gnosis,
    write_anchored_event,
    write_gnosis_entry,
    write_distillation,
    InstanceRecord,
    Event,
)


@pytest.fixture
def unique_entity():
    """Generate a unique entity name for test isolation."""
    return f"test_{uuid.uuid4().hex[:8]}"


class TestInstanceRegistry:
    """Test instance registration and tracking."""
    
    @pytest.mark.asyncio
    async def test_register_instance(self, unique_entity):
        rec = await register_instance("opencode", unique_entity)
        
        assert rec.channel == "opencode"
        assert rec.entity == unique_entity
        assert rec.status == "active"
        assert rec.pid > 0
        assert f"opencode/{unique_entity}/" in rec.instance_id
        
        # Cleanup
        await deregister_instance(rec.instance_id)
    
    @pytest.mark.asyncio
    async def test_multiple_instances_same_entity(self, unique_entity):
        rec1 = await register_instance("opencode", unique_entity)
        rec2 = await register_instance("cline", unique_entity)
        rec3 = await register_instance("gemini-cli", unique_entity)
        
        instances = await get_active_instances(unique_entity)
        assert len(instances) == 3
        
        channels = {i.channel for i in instances}
        assert channels == {"opencode", "cline", "gemini-cli"}
        
        # Cleanup
        await deregister_instance(rec1.instance_id)
        await deregister_instance(rec2.instance_id)
        await deregister_instance(rec3.instance_id)
    
    @pytest.mark.asyncio
    async def test_deregister_instance(self, unique_entity):
        rec = await register_instance("opencode", unique_entity)
        
        instances = await get_active_instances(unique_entity)
        assert len(instances) == 1
        
        await deregister_instance(rec.instance_id)
        
        instances = await get_active_instances(unique_entity)
        assert len(instances) == 0
        
        # Should still be in all_instances with terminated status
        all_inst = await get_all_instances(unique_entity)
        assert len(all_inst) == 1
        assert all_inst[0].status == "terminated"
    
    @pytest.mark.asyncio
    async def test_heartbeat_update(self, unique_entity):
        rec = await register_instance("opencode", unique_entity)
        
        await update_instance_heartbeat(rec.instance_id)
        
        instances = await get_active_instances(unique_entity)
        assert instances[0].last_heartbeat is not None
        
        await deregister_instance(rec.instance_id)


class TestEventLog:
    """Test append-only event log."""
    
    @pytest.mark.asyncio
    async def test_append_and_read_events(self, unique_entity):
        entity = unique_entity
        
        # Register instance first
        rec = await register_instance("opencode", entity)
        
        # Append events
        seq1 = await append_event(entity, "anchored_summary", "session_start", 
                                  {"objective": "Test"}, rec.instance_id)
        seq2 = await append_event(entity, "anchored_summary", "task_complete",
                                  {"task": "Task 1"}, rec.instance_id)
        seq3 = await append_event(entity, "anchored_summary", "decision",
                                  {"decision": "Decision 1"}, rec.instance_id)
        
        assert seq1 == 1
        assert seq2 == 2
        assert seq3 == 3
        
        # Read events
        events = await read_events(entity, "anchored_summary")
        assert len(events) == 3
        assert events[0].event_type == "session_start"
        assert events[1].event_type == "task_complete"
        assert events[2].event_type == "decision"
        assert all(e.instance_id == rec.instance_id for e in events)
        
        # Read with from_seq
        events = await read_events(entity, "anchored_summary", from_seq=2)
        assert len(events) == 2
        assert events[0].event_seq == 2
        
        await deregister_instance(rec.instance_id)
    
    @pytest.mark.asyncio
    async def test_concurrent_appends(self, unique_entity):
        """Test that concurrent appends from multiple instances are serialized."""
        entity = unique_entity
        
        rec1 = await register_instance("opencode", entity)
        rec2 = await register_instance("cline", entity)
        
        # Simulate concurrent writes
        async def write_events(rec, count):
            for i in range(count):
                await append_event(entity, "anchored_summary", "task_complete",
                                  {"task": f"Task {i}"}, rec.instance_id)
        
        await asyncio.gather(
            write_events(rec1, 5),
            write_events(rec2, 5)
        )
        
        events = await read_events(entity, "anchored_summary")
        assert len(events) == 10
        
        # Verify sequence numbers are unique and sequential
        seqs = [e.event_seq for e in events]
        assert seqs == list(range(1, 11))
        
        await deregister_instance(rec1.instance_id)
        await deregister_instance(rec2.instance_id)
    
    @pytest.mark.asyncio
    async def test_gnosis_events(self, unique_entity):
        entity = unique_entity
        rec = await register_instance("opencode", entity)
        
        await append_event(entity, "session_gnosis", "gnosis_entry",
                          {"section": "L1_Narrative", "content": "Did something"},
                          rec.instance_id)
        await append_event(entity, "session_gnosis", "gnosis_entry",
                          {"section": "L3_Principle", "content": "Universal truth"},
                          rec.instance_id)
        await append_event(entity, "session_gnosis", "distillation",
                          {"l1": "L1", "l2": "L2", "l3": "L3", "proposed_lesson": "Lesson"},
                          rec.instance_id)
        
        events = await read_events(entity, "session_gnosis")
        assert len(events) == 3
        
        await deregister_instance(rec.instance_id)


class TestProjections:
    """Test deterministic projection from event logs."""
    
    @pytest.mark.asyncio
    async def test_anchored_summary_projection(self):
        entity = "proj_test"
        rec = await register_instance("opencode", entity)
        
        await write_anchored_event(entity, "session_start", 
                                  {"objective": "Test objective", "model": "test-model"},
                                  rec.instance_id)
        await write_anchored_event(entity, "task_complete",
                                  {"task": "Completed task"},
                                  rec.instance_id)
        await write_anchored_event(entity, "decision",
                                  {"decision": "Test decision", "rationale": "Because reasons"},
                                  rec.instance_id)
        
        # Project
        summary = await project_anchored_summary(entity)
        
        assert "Test objective" in summary
        assert "Completed task" in summary
        assert "Test decision" in summary
        assert "Because reasons" in summary
        assert "test-model" in summary
        assert rec.instance_id.split('/')[-1][:8] in summary
        
        await deregister_instance(rec.instance_id)
    
    @pytest.mark.asyncio
    async def test_session_gnosis_projection(self):
        entity = "gnosis_proj_test"
        rec = await register_instance("opencode", entity)
        
        await write_gnosis_entry(entity, "L1_Narrative", "Narrative content", rec.instance_id)
        await write_gnosis_entry(entity, "L2_Insight", "Insight content", rec.instance_id)
        await write_gnosis_entry(entity, "L3_Principle", "Principle content", rec.instance_id)
        await write_distillation(entity, "L1", "L2", "L3", "Proposed lesson", rec.instance_id)
        
        gnosis = await project_session_gnosis(entity)
        
        assert "Narrative content" in gnosis
        assert "Insight content" in gnosis
        assert "Principle content" in gnosis
        assert "Proposed lesson" in gnosis
        assert "L1" in gnosis
        assert "L2" in gnosis
        assert "L3" in gnosis
        
        await deregister_instance(rec.instance_id)
    
    @pytest.mark.asyncio
    async def test_l3_deduplication(self):
        """Test that L3 principles are deduplicated by content hash."""
        entity = "l3_dedup_test"
        rec = await register_instance("opencode", entity)
        
        # Write same L3 principle twice
        await write_gnosis_entry(entity, "L3_Principle", "Same principle", rec.instance_id)
        await write_gnosis_entry(entity, "L3_Principle", "Same principle", rec.instance_id)
        
        gnosis = await project_session_gnosis(entity)
        
        # Should only appear once
        assert gnosis.count("Same principle") == 1
        
        await deregister_instance(rec.instance_id)
    
    @pytest.mark.asyncio
    async def test_write_projections_creates_symlinks(self):
        entity = "symlink_test"
        rec = await register_instance("opencode", entity)
        
        await write_anchored_event(entity, "session_start", 
                                  {"objective": "Test", "model": "test"},
                                  rec.instance_id)
        
        await write_projections(entity)
        
        # Check canonical files exist
        from omega.coordination.miap import ANCHORED_EVENTS_DIR, GNOSIS_EVENTS_DIR, PROJECT_ROOT
        
        anchored_canonical = ANCHORED_EVENTS_DIR / entity / "projection.md"
        gnosis_canonical = GNOSIS_EVENTS_DIR / entity / "projection.md"
        
        assert anchored_canonical.exists()
        assert gnosis_canonical.exists()
        
        # Check symlinks
        opencode_anchored = PROJECT_ROOT / ".opencode" / "anchored-summary.md"
        entity_gnosis = PROJECT_ROOT / "data" / "entities" / entity / "workspace" / "session_gnosis.md"
        
        assert opencode_anchored.is_symlink()
        assert entity_gnosis.is_symlink()
        assert opencode_anchored.resolve() == anchored_canonical.resolve()
        assert entity_gnosis.resolve() == gnosis_canonical.resolve()
        
        await deregister_instance(rec.instance_id)


class TestMultiInstanceScenario:
    """Test realistic multi-instance scenarios."""
    
    @pytest.mark.asyncio
    async def test_two_instances_shared_projection(self):
        """Two instances of same entity share a single projected summary."""
        entity = "shared_test"
        
        # Instance 1 (OpenCode)
        rec1 = await register_instance("opencode", entity)
        await write_anchored_event(entity, "session_start",
                                  {"objective": "Instance 1 objective", "model": "model-1"},
                                  rec1.instance_id)
        await write_anchored_event(entity, "task_complete",
                                  {"task": "Instance 1 task"},
                                  rec1.instance_id)
        
        # Instance 2 (Cline)
        rec2 = await register_instance("cline", entity)
        await write_anchored_event(entity, "task_complete",
                                  {"task": "Instance 2 task"},
                                  rec2.instance_id)
        await write_anchored_event(entity, "decision",
                                  {"decision": "Instance 2 decision", "rationale": "Instance 2 reasoning"},
                                  rec2.instance_id)
        
        # Both instances see the same projection (deterministic except timestamp)
        summary1 = await project_anchored_summary(entity)
        summary2 = await project_anchored_summary(entity)
        
        # Normalize timestamps for comparison
        import re
        def normalize(s):
            return re.sub(r'\*\*Projected\*\*: [^\n]+', '**Projected**: NORMALIZED', s)
        
        assert normalize(summary1) == normalize(summary2)  # Deterministic projection
        
        # Contains data from both instances
        assert "Instance 1 objective" in summary1
        assert "Instance 1 task" in summary1
        assert "Instance 2 task" in summary1
        assert "Instance 2 decision" in summary1
        assert "Instance 2 reasoning" in summary1
        
        # Both instance IDs mentioned
        inst1_short = rec1.instance_id.split('/')[-1][:8]
        inst2_short = rec2.instance_id.split('/')[-1][:8]
        assert inst1_short in summary1
        assert inst2_short in summary1
        
        await deregister_instance(rec1.instance_id)
        await deregister_instance(rec2.instance_id)
    
    @pytest.mark.asyncio
    async def test_compaction_survival(self):
        """Event log survives compaction (simulated by new session_start)."""
        entity = "compaction_test"
        
        # Session 1
        rec1 = await register_instance("opencode", entity)
        await write_anchored_event(entity, "session_start",
                                  {"objective": "Session 1", "model": "m1"},
                                  rec1.instance_id)
        await write_anchored_event(entity, "task_complete",
                                  {"task": "Session 1 task"},
                                  rec1.instance_id)
        await write_anchored_event(entity, "compaction",
                                  {"trigger": "/compact", "next_action": "Continue"},
                                  rec1.instance_id)
        await deregister_instance(rec1.instance_id)
        
        # Session 2 (new instance, simulates post-compaction)
        rec2 = await register_instance("opencode", entity)
        await write_anchored_event(entity, "session_start",
                                  {"objective": "Session 2", "model": "m2"},
                                  rec2.instance_id)
        
        # Projection includes both sessions
        summary = await project_anchored_summary(entity)
        
        assert "Session 1" in summary
        assert "Session 1 task" in summary
        assert "Session 2" in summary
        assert "/compact" in summary
        
        await deregister_instance(rec2.instance_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
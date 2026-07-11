"""Tests for subagent_dispatcher.py — HandoffPacket, Capability Registry, Dispatch Helpers."""
import pytest
import json
import time
from pathlib import Path
from omega.oracle.subagent_dispatcher import (
    HandoffPacket,
    CAPABILITY_REGISTRY,
    get_agent_capabilities,
    list_available_agents,
    build_dispatch_prompt,
    dispatch,
    PacketType,
    TaskType,
    PacketStatus,
    AgentMode,
    ZONEID_HANDOFF,
)


class TestHandoffPacket:
    def test_minimal_creation(self):
        packet = HandoffPacket(
            source_agent="kali",
            target_agent="doom_guy",
            task_type="review",
            task_description="Test task",
        )
        assert packet.source_agent == "kali"
        assert packet.target_agent == "doom_guy"
        assert packet.task_type == "review"
        assert packet.task_description == "Test task"
        assert packet.packet_id.startswith("hdp_")
        assert packet.trace_id
        assert packet.created_at > 0
        assert packet.zoneid == ZONEID_HANDOFF
        assert packet.status == "pending"
        assert packet.visited_agents == ["kali"]

    def test_full_creation(self):
        packet = HandoffPacket(
            source_agent="kali",
            target_agent="doom_guy",
            task_type="implement",
            task_description="Full test",
            relevant_files=["file1.py", "file2.py"],
            context="Some context",
            expected_output="JSON report",
            packet_type="delegation",
            status="accepted",
            ttl_seconds=300,
            max_hops=5,
        )
        assert packet.relevant_files == ["file1.py", "file2.py"]
        assert packet.context == "Some context"
        assert packet.expected_output == "JSON report"
        assert packet.packet_type == "delegation"
        assert packet.status == "accepted"
        assert packet.ttl_seconds == 300
        assert packet.max_hops == 5

    def test_invalid_zoneid_raises(self):
        with pytest.raises(ValueError, match="Invalid ZONEID_HANDOFF"):
            HandoffPacket(
                source_agent="kali",
                target_agent="doom_guy",
                task_type="review",
                task_description="Test",
                zoneid=0xDEADBEEF,
            )

    def test_is_loop_detection(self):
        packet = HandoffPacket(
            source_agent="kali",
            target_agent="doom_guy",
            task_type="review",
            task_description="Test",
            visited_agents=["kali", "doom_guy", "jem"],
        )
        assert packet.is_loop("doom_guy") is True
        assert packet.is_loop("jem") is True
        assert packet.is_loop("kali") is True
        assert packet.is_loop("roc_racoon") is False

    def test_increment_hop(self):
        packet = HandoffPacket(
            source_agent="kali",
            target_agent="doom_guy",
            task_type="review",
            task_description="Test",
            max_hops=3,
        )
        assert packet.hop_count == 0
        assert packet.increment_hop() is True  # 1
        assert packet.hop_count == 1
        assert packet.increment_hop() is True  # 2
        assert packet.increment_hop() is True  # 3
        assert packet.increment_hop() is False  # 4 > max_hops
        assert packet.hop_count == 4

    def test_expired_property(self):
        packet = HandoffPacket(
            source_agent="kali",
            target_agent="doom_guy",
            task_type="review",
            task_description="Test",
            ttl_seconds=1,
            created_at=time.time() - 2,  # Created 2 seconds ago
        )
        assert packet.expired is True

        packet2 = HandoffPacket(
            source_agent="kali",
            target_agent="doom_guy",
            task_type="review",
            task_description="Test",
            ttl_seconds=3600,
        )
        assert packet2.expired is False

    def test_to_dict_and_json(self):
        packet = HandoffPacket(
            source_agent="kali",
            target_agent="doom_guy",
            task_type="review",
            task_description="Test",
        )
        d = packet.to_dict()
        assert isinstance(d, dict)
        assert d["source_agent"] == "kali"
        assert d["target_agent"] == "doom_guy"

        json_str = packet.to_json()
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["source_agent"] == "kali"

    def test_save_and_load(self, tmp_path):
        packet = HandoffPacket(
            source_agent="kali",
            target_agent="doom_guy",
            task_type="review",
            task_description="Test",
        )
        archive_dir = tmp_path / "handoff" / "archive"
        saved_path = packet.save(str(archive_dir))
        assert Path(saved_path).exists()

        loaded = HandoffPacket(**json.loads(Path(saved_path).read_text()))
        assert loaded.packet_id == packet.packet_id
        assert loaded.source_agent == packet.source_agent
        assert loaded.target_agent == packet.target_agent
        assert loaded.trace_id == packet.trace_id


class TestCapabilityRegistry:
    def test_registry_contains_expected_agents(self):
        expected = [
            "kali", "doom_guy", "roc_racoon", "jem", "john_carmack",
            "makali", "researcher", "maat", "lilith", "verity", "pillar"
        ]
        for agent in expected:
            assert agent in CAPABILITY_REGISTRY

    def test_agent_structure(self):
        for name, desc in CAPABILITY_REGISTRY.items():
            assert "mode" in desc
            assert "purpose" in desc
            assert "capabilities" in desc
            assert "domains" in desc
            assert "pillar_slot" in desc
            assert "task_tool_type" in desc
            assert "owned_files" in desc
            assert isinstance(desc["capabilities"], list)
            assert isinstance(desc["domains"], list)
            assert isinstance(desc["owned_files"], list)

    def test_kali_is_primary(self):
        assert CAPABILITY_REGISTRY["kali"]["mode"] == "primary"

    def test_maat_is_subagent(self):
        assert CAPABILITY_REGISTRY["maat"]["mode"] == "subagent"

    def test_pillar_has_slot(self):
        assert CAPABILITY_REGISTRY["pillar"]["pillar_slot"] == "PX"


class TestGetAgentCapabilities:
    def test_known_agent(self):
        caps = get_agent_capabilities("kali")
        assert caps is not None
        assert caps["purpose"] == "Grand Oversight — Sees all, delegates, destroys drift"

    def test_case_insensitive(self):
        caps = get_agent_capabilities("KALI")
        assert caps is not None

    def test_unknown_agent(self):
        caps = get_agent_capabilities("nonexistent_agent_xyz")
        assert caps is None


class TestListAvailableAgents:
    def test_all_agents(self):
        agents = list_available_agents()
        assert len(agents) == len(CAPABILITY_REGISTRY)
        assert "kali" in agents

    def test_filter_primary(self):
        primary = list_available_agents("primary")
        assert all(CAPABILITY_REGISTRY[a]["mode"] == "primary" for a in primary)
        assert "kali" in primary
        assert "maat" not in primary

    def test_filter_subagent(self):
        subagents = list_available_agents("subagent")
        assert all(CAPABILITY_REGISTRY[a]["mode"] == "subagent" for a in subagents)
        assert "maat" in subagents
        assert "kali" not in subagents


class TestBuildDispatchPrompt:
    def test_basic_prompt(self):
        packet = HandoffPacket(
            source_agent="kali",
            target_agent="doom_guy",
            task_type="review",
            task_description="Audit heritage tags",
            relevant_files=["src/omega/cvar_table.py"],
            expected_output="JSON report",
        )
        prompt = build_dispatch_prompt(packet)
        assert "doom_guy" in prompt
        assert "Sovereign id Software Architect" in prompt
        assert "heritage_design" in prompt
        assert "Audit heritage tags" in prompt
        assert "src/omega/cvar_table.py" in prompt
        assert "JSON report" in prompt
        assert "Trace ID" in prompt
        assert "PIVOT_LOG.md" in prompt
        assert "[id-soft:" in prompt

    def test_prompt_without_optional_fields(self):
        packet = HandoffPacket(
            source_agent="kali",
            target_agent="doom_guy",
            task_type="review",
            task_description="Simple task",
        )
        prompt = build_dispatch_prompt(packet)
        assert "Simple task" in prompt
        assert "Files to Read First" not in prompt
        assert "Expected Output" not in prompt


class TestDispatchFunction:
    def test_dispatch_returns_prompt(self):
        packet = HandoffPacket(
            source_agent="kali",
            target_agent="doom_guy",
            task_type="review",
            task_description="Test",
        )
        prompt = dispatch(packet)
        assert isinstance(prompt, str)
        assert len(prompt) > 100
        assert "doom_guy" in prompt
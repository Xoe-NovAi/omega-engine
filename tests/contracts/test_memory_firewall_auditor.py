# AP: AP-MEMORY-FIREWALL-AUDITOR-TEST-v1.0.0
# 🔱 Contract Tests for MemoryFirewallAuditor (M21 Gate Integrity)
# ICS: [NODE: TEST | ARCHETYPE: VERITY | CONTEXT: CONTRACT-TEST]

import pytest
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from omega.audit.memory_firewall_auditor import (
    MemoryFirewallAuditor,
    MemoryAuditReport,
    MemoryViolation,
)
from omega.oracle.entity_registry import Entity


@dataclass
class MockEntity:
    """Mock entity for testing without full registry."""
    name: str
    metadata: Dict[str, Any]
    domains: List[str] = None
    capabilities: List[str] = None
    model: str = "test-model"
    personality: str = "test personality"
    temperature: Optional[float] = None
    context_window: Optional[int] = None
    slots: List[str] = None
    role: Optional[str] = None
    container: bool = False
    port: Optional[int] = None
    wad_source: Optional[str] = None
    priority: int = 0


class TestMemoryFirewallAuditor:
    """M21 Contract Tests: Every code path returning typed result MUST be 
    exercised by at least one test that validates the return type."""
    
    def setup_method(self):
        self.auditor = MemoryFirewallAuditor()
    
    def _make_entity(self, metadata: Dict[str, Any]) -> Entity:
        """Create a real Entity instance for testing."""
        return Entity(
            name="test_entity",
            domains=["test"],
            capabilities=["test"],
            model="test-model",
            personality="test personality",
            metadata=metadata,
        )
    
    def test_memory_auditor_detects_wad_leakage_at_root(self):
        """M21: Auditor detects forbidden WAD keys at metadata root."""
        entity = self._make_entity({"element": "fire", "chakra": "root"})
        report = self.auditor.audit_entity_metadata(entity)
        
        # Contract: Returns MemoryAuditReport
        assert isinstance(report, MemoryAuditReport)
        assert report.entity_name == "test_entity"
        assert report.tier == "entity"
        
        # Contract: clean=False when violations found
        assert report.clean is False
        
        # Contract: Violations list contains MemoryViolation objects
        assert len(report.violations) == 2
        assert all(isinstance(v, MemoryViolation) for v in report.violations)
        
        # Contract: Violations have correct keys
        violation_keys = {v.key for v in report.violations}
        assert violation_keys == {"element", "chakra"}
        
        # Contract: Violations have correct location format
        for v in report.violations:
            assert v.location == f"metadata.{v.key}"
            assert v.severity == "error"
            assert v.trace_id is not None
            assert len(v.trace_id) == 8
    
    def test_memory_auditor_allows_symbolic_subdict(self):
        """M21: Auditor allows WAD keys nested under metadata['symbolic']."""
        entity = self._make_entity({
            "symbolic": {
                "element": "fire",
                "energy_center": "root",
                "celestial_body": "mars",
                "archetypal_ally": "ares",
                "glyph": "🜂",
                "invocation": "By fire I forge"
            }
        })
        report = self.auditor.audit_entity_metadata(entity)
        
        # Contract: clean=True when only symbolic sub-dict used
        assert isinstance(report, MemoryAuditReport)
        assert report.clean is True
        assert len(report.violations) == 0
    
    def test_memory_auditor_allows_engine_metadata_keys(self):
        """M21: Auditor allows engine-agnostic metadata keys at root."""
        entity = self._make_entity({
            "name": "test",
            "domains": ["test"],
            "capabilities": ["test"],
            "model": "test-model",
            "personality": "test",
            "temperature": 0.7,
            "context_window": 4096,
            "slots": ["P1"],
            "role": "tester",
            "container": True,
            "port": 8080,
            "wad_source": "test_wad",
            "priority": 10,
        })
        report = self.auditor.audit_entity_metadata(entity)
        
        assert isinstance(report, MemoryAuditReport)
        assert report.clean is True
        assert len(report.violations) == 0
    
    def test_memory_auditor_flags_unknown_symbolic_keys(self):
        """M21: Auditor warns on unknown keys in symbolic sub-dict."""
        entity = self._make_entity({
            "symbolic": {
                "element": "fire",
                "unknown_field": "should_warn"
            }
        })
        report = self.auditor.audit_entity_metadata(entity)
        
        assert isinstance(report, MemoryAuditReport)
        # clean=False because of warning
        assert report.clean is False
        assert len(report.violations) == 1
        assert report.violations[0].key == "unknown_field"
        assert report.violations[0].location == "metadata.symbolic.unknown_field"
        assert report.violations[0].severity == "warning"
    
    def test_memory_auditor_mixed_root_and_symbolic(self):
        """M21: Auditor catches root violations even with valid symbolic."""
        entity = self._make_entity({
            "element": "fire",  # FORBIDDEN at root
            "symbolic": {
                "energy_center": "root"  # ALLOWED in symbolic
            }
        })
        report = self.auditor.audit_entity_metadata(entity)
        
        assert isinstance(report, MemoryAuditReport)
        assert report.clean is False
        # Should have 1 error (root element) + 0 warnings
        assert len(report.violations) == 1
        assert report.violations[0].key == "element"
        assert report.violations[0].severity == "error"
    
    def test_memory_auditor_all_forbidden_keys(self):
        """M21: Auditor catches all defined FORBIDDEN_WAD_KEYS."""
        forbidden_metadata = {key: f"value_{key}" for key in 
            ["element", "chakra", "planet", "sigil", "invocation",
             "archetypal_ally", "celestial_body", "energy_center",
             "tarot", "sefirot", "qliphoth", "pantheon", "octave",
             "glyph", "first_breath", "secondary_keeper", "traits"]}
        
        entity = self._make_entity(forbidden_metadata)
        report = self.auditor.audit_entity_metadata(entity)
        
        assert isinstance(report, MemoryAuditReport)
        assert report.clean is False
        assert len(report.violations) == 17  # All forbidden keys
        
        violation_keys = {v.key for v in report.violations}
        assert violation_keys == set(forbidden_metadata.keys())
    
    def test_memory_auditor_empty_metadata_clean(self):
        """M21: Auditor passes empty metadata."""
        entity = self._make_entity({})
        report = self.auditor.audit_entity_metadata(entity)
        
        assert isinstance(report, MemoryAuditReport)
        assert report.clean is True
        assert len(report.violations) == 0
    
    def test_memory_auditor_none_metadata_clean(self):
        """M21: Auditor passes None metadata."""
        entity = self._make_entity({})
        entity.metadata = None  # type: ignore
        report = self.auditor.audit_entity_metadata(entity)
        
        assert isinstance(report, MemoryAuditReport)
        assert report.clean is True
        assert len(report.violations) == 0
    
    def test_memory_audit_report_dataclass_structure(self):
        """M21: MemoryAuditReport has correct dataclass structure."""
        entity = self._make_entity({"element": "fire"})
        report = self.auditor.audit_entity_metadata(entity)
        
        # Verify all fields present and typed
        assert hasattr(report, 'entity_name')
        assert hasattr(report, 'tier')
        assert hasattr(report, 'violations')
        assert hasattr(report, 'clean')
        
        assert isinstance(report.entity_name, str)
        assert isinstance(report.tier, str)
        assert isinstance(report.violations, list)
        assert isinstance(report.clean, bool)
    
    def test_memory_violation_dataclass_structure(self):
        """M21: MemoryViolation has correct dataclass structure."""
        entity = self._make_entity({"element": "fire"})
        report = self.auditor.audit_entity_metadata(entity)
        
        violation = report.violations[0]
        assert hasattr(violation, 'key')
        assert hasattr(violation, 'location')
        assert hasattr(violation, 'severity')
        assert hasattr(violation, 'trace_id')
        
        assert isinstance(violation.key, str)
        assert isinstance(violation.location, str)
        assert violation.severity in ("error", "warning")
        assert isinstance(violation.trace_id, str)
        assert len(violation.trace_id) == 8
    
    def test_audit_memory_tier_returns_list_of_reports(self):
        """M21: audit_memory_tier returns List[MemoryAuditReport]."""
        entities = [
            self._make_entity({"element": "fire"}),
            self._make_entity({"symbolic": {"element": "water"}}),
        ]
        reports = self.auditor.audit_memory_tier("hot", entities)
        
        assert isinstance(reports, list)
        assert len(reports) == 2
        assert all(isinstance(r, MemoryAuditReport) for r in reports)
        assert all(r.tier == "hot" for r in reports)
    
    def test_audit_all_tiers_returns_dict_of_lists(self):
        """M21: audit_all_tiers returns Dict[str, List[MemoryAuditReport]]."""
        entities = [self._make_entity({"element": "fire"})]
        result = self.auditor.audit_all_tiers(entities)
        
        assert isinstance(result, dict)
        assert set(result.keys()) == {"hot", "warm", "cold"}
        for tier_reports in result.values():
            assert isinstance(tier_reports, list)
            assert all(isinstance(r, MemoryAuditReport) for r in tier_reports)
    
    def test_get_summary_returns_correct_stats(self):
        """M21: get_summary returns correct statistics dict."""
        entities = [
            self._make_entity({"element": "fire"}),  # 1 error
            self._make_entity({"symbolic": {"unknown": "x"}}),  # 1 warning
            self._make_entity({}),  # clean
        ]
        reports = []
        for e in entities:
            reports.extend(self.auditor.audit_memory_tier("hot", [e]))
        
        summary = self.auditor.get_summary(reports)
        
        assert isinstance(summary, dict)
        assert summary["total_entities"] == 3
        assert summary["clean_entities"] == 1
        assert summary["violated_entities"] == 2
        assert summary["total_violations"] == 2
        assert summary["error_violations"] == 1
        assert summary["warning_violations"] == 1
        assert summary["compliance_rate"] == 1/3
    
    def test_auditor_trace_id_generation(self):
        """M21: Each audit generates unique trace_id."""
        entity = self._make_entity({"element": "fire"})
        report1 = self.auditor.audit_entity_metadata(entity)
        report2 = self.auditor.audit_entity_metadata(entity)
        
        # Each violation should have a trace_id
        assert report1.violations[0].trace_id is not None
        assert report2.violations[0].trace_id is not None
        # They should be different (new trace per audit)
        assert report1.violations[0].trace_id != report2.violations[0].trace_id


class TestMemoryFirewallAuditorIntegration:
    """Integration tests with real EntityRegistry."""
    
    def test_audit_real_entities_from_registry(self):
        """M21: Auditor works with real EntityRegistry entities."""
        from omega.oracle.entity_registry import EntityRegistry
        
        auditor = MemoryFirewallAuditor()
        registry = EntityRegistry()
        entities = list(registry.active_iter())
        
        if not entities:
            pytest.skip("No entities loaded in registry")
        
        reports = auditor.audit_memory_tier("hot", entities)
        
        assert isinstance(reports, list)
        assert len(reports) == len(entities)
        assert all(isinstance(r, MemoryAuditReport) for r in reports)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
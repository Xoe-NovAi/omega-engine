#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Contract Tests for MandateAuditor (M21 Gate Integrity).

These tests verify the MandateAuditor API contract:
- MandateResult structure
- AuditReport structure
- Each check returns proper types
- run_all() returns complete report

Run via: make test ARGS='-k mandate_auditor'
"""

import tempfile
from pathlib import Path

import pytest

from omega.audit.mandate_auditor import (
    MandateAuditor,
    MandateResult,
    AuditReport,
)


class TestMandateAuditorContract:
    """Contract tests for MandateAuditor public API."""

    def test_mandate_result_is_dataclass(self):
        """MandateResult must be a dataclass with required fields."""
        result = MandateResult(
            mandate_id="M1",
            name="Test Mandate",
            passed=True,
            detail="test detail",
            severity="error"
        )
        assert isinstance(result, MandateResult)
        assert result.mandate_id == "M1"
        assert result.name == "Test Mandate"
        assert result.passed is True
        assert result.detail == "test detail"
        assert result.severity == "error"

    def test_audit_report_is_dataclass(self):
        """AuditReport must be a dataclass with required fields."""
        results = (
            MandateResult("M1", "Test 1", True),
            MandateResult("M2", "Test 2", False, "failed"),
        )
        report = AuditReport(results=results, passed=1, failed=1, warnings=0)
        assert isinstance(report, AuditReport)
        assert report.results == results
        assert report.passed == 1
        assert report.failed == 1
        assert report.warnings == 0

    def test_audit_report_all_passed_property(self):
        """AuditReport.all_passed returns True only when failed == 0."""
        report_pass = AuditReport(
            results=(MandateResult("M1", "Test", True),),
            passed=1, failed=0, warnings=0
        )
        report_fail = AuditReport(
            results=(MandateResult("M1", "Test", False),),
            passed=0, failed=1, warnings=0
        )
        assert report_pass.all_passed is True
        assert report_fail.all_passed is False

    def test_mandate_auditor_instantiation(self):
        """MandateAuditor must be instantiable with root path."""
        auditor = MandateAuditor(".")
        assert auditor.root.exists()

    def test_mandate_auditor_run_all_returns_report(self):
        """run_all() must return AuditReport with all checks."""
        auditor = MandateAuditor(".")
        report = auditor.run_all()

        assert isinstance(report, AuditReport)
        assert isinstance(report.results, tuple)
        assert len(report.results) > 0
        assert all(isinstance(r, MandateResult) for r in report.results)
        assert report.passed >= 0
        assert report.failed >= 0
        assert report.warnings >= 0

    def test_mandate_auditor_check_m3_iris_constant(self):
        """check_m3_iris_constant() must record a MandateResult."""
        auditor = MandateAuditor(".")
        auditor.check_m3_iris_constant()

        assert len(auditor.results) == 1
        result = auditor.results[0]
        assert isinstance(result, MandateResult)
        assert result.mandate_id == "M3"
        assert "MESSENGER_BRIDGE" in result.name

    def test_mandate_auditor_check_m6_podman_sovereignty(self):
        """check_m6_podman_sovereignty() must record a MandateResult."""
        auditor = MandateAuditor(".")
        auditor.check_m6_podman_sovereignty()

        assert len(auditor.results) == 1
        result = auditor.results[0]
        assert isinstance(result, MandateResult)
        assert result.mandate_id == "M6"
        assert "Podman" in result.name

    def test_mandate_auditor_check_m7_local_first(self):
        """check_m7_local_first() must record a MandateResult."""
        auditor = MandateAuditor(".")
        auditor.check_m7_local_first()

        assert len(auditor.results) == 1
        result = auditor.results[0]
        assert isinstance(result, MandateResult)
        assert result.mandate_id == "M7"
        assert "Local-First" in result.name

    def test_mandate_auditor_check_m10_fleet_integrity(self):
        """check_m10_fleet_integrity() must record a MandateResult."""
        auditor = MandateAuditor(".")
        auditor.check_m10_fleet_integrity()

        assert len(auditor.results) == 1
        result = auditor.results[0]
        assert isinstance(result, MandateResult)
        assert result.mandate_id == "M10"
        assert "Fleet" in result.name

    def test_mandate_auditor_check_m11_soul_integrity(self):
        """check_m11_soul_integrity() must record a MandateResult."""
        auditor = MandateAuditor(".")
        auditor.check_m11_soul_integrity()

        assert len(auditor.results) == 1
        result = auditor.results[0]
        assert isinstance(result, MandateResult)
        assert result.mandate_id == "M11"
        assert "Soul" in result.name

    def test_mandate_auditor_check_m12_queue_integrity(self):
        """check_m12_queue_integrity() must record a MandateResult."""
        auditor = MandateAuditor(".")
        auditor.check_m12_queue_integrity()

        assert len(auditor.results) == 1
        result = auditor.results[0]
        assert isinstance(result, MandateResult)
        assert result.mandate_id == "M12"
        assert "Queue" in result.name

    def test_mandate_auditor_check_m15_sovereign_continuity(self):
        """check_m15_sovereign_continuity() must record a MandateResult."""
        auditor = MandateAuditor(".")
        auditor.check_m15_sovereign_continuity()

        assert len(auditor.results) == 1
        result = auditor.results[0]
        assert isinstance(result, MandateResult)
        assert result.mandate_id == "M15"
        assert "Sovereign Continuity" in result.name

    def test_mandate_auditor_check_m16_modularization(self):
        """check_m16_modularization() must record a MandateResult."""
        auditor = MandateAuditor(".")
        auditor.check_m16_modularization()

        assert len(auditor.results) == 1
        result = auditor.results[0]
        assert isinstance(result, MandateResult)
        assert result.mandate_id == "M16"
        assert "Modularization" in result.name

    def test_mandate_auditor_check_m20_somatic_state(self):
        """check_m20_somatic_state() must record a MandateResult (warning severity)."""
        auditor = MandateAuditor(".")
        auditor.check_m20_somatic_state()

        assert len(auditor.results) == 1
        result = auditor.results[0]
        assert isinstance(result, MandateResult)
        assert result.mandate_id == "M20"
        assert "SomaticState" in result.name
        # M20 is best-effort, should be warning severity
        assert result.severity == "warning"


class TestMandateAuditorWithTempFixture:
    """Integration tests with temporary directory fixtures."""

    def test_m7_fails_when_providers_yaml_missing(self):
        """M7 check fails when providers.yaml doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auditor = MandateAuditor(tmpdir)
            auditor.check_m7_local_first()
            result = auditor.results[0]
            assert result.mandate_id == "M7"
            assert result.passed is False
            assert "not found" in result.detail

    def test_m7_passes_with_local_first(self):
        """M7 check passes when providers.yaml has local_first strategy."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "config"
            config_dir.mkdir()
            providers = config_dir / "providers.yaml"
            providers.write_text("strategy: local_first\nbackends: []\n")

            auditor = MandateAuditor(tmpdir)
            auditor.check_m7_local_first()
            result = auditor.results[0]
            assert result.mandate_id == "M7"
            assert result.passed is True

    def test_m7_fails_with_cloud_first(self):
        """M7 check fails when providers.yaml has cloud_first strategy."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "config"
            config_dir.mkdir()
            providers = config_dir / "providers.yaml"
            providers.write_text("strategy: cloud_first\nbackends: []\n")

            auditor = MandateAuditor(tmpdir)
            auditor.check_m7_local_first()
            result = auditor.results[0]
            assert result.mandate_id == "M7"
            assert result.passed is False
            assert "cloud_first" in result.detail

    def test_m10_fails_when_agents_dir_missing(self):
        """M10 check fails when .opencode/agents/ doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auditor = MandateAuditor(tmpdir)
            auditor.check_m10_fleet_integrity()
            result = auditor.results[0]
            assert result.mandate_id == "M10"
            assert result.passed is False
            assert "not found" in result.detail

    def test_m10_passes_with_few_agents(self):
        """M10 check passes when agent count <= 14."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = Path(tmpdir) / ".opencode" / "agents"
            agents_dir.mkdir(parents=True)
            for i in range(5):
                (agents_dir / f"agent_{i}.md").write_text("# Agent")

            auditor = MandateAuditor(tmpdir)
            auditor.check_m10_fleet_integrity()
            result = auditor.results[0]
            assert result.mandate_id == "M10"
            assert result.passed is True

    def test_m10_fails_with_many_agents(self):
        """M10 check fails when agent count > 14."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = Path(tmpdir) / ".opencode" / "agents"
            agents_dir.mkdir(parents=True)
            for i in range(15):
                (agents_dir / f"agent_{i}.md").write_text("# Agent")

            auditor = MandateAuditor(tmpdir)
            auditor.check_m10_fleet_integrity()
            result = auditor.results[0]
            assert result.mandate_id == "M10"
            assert result.passed is False
            assert "15 agents" in result.detail

    def test_m3_detects_iris_in_pillar(self):
        """M3 check detects MESSENGER_BRIDGE assigned to a Node slot (dispatch.yaml format)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            entities_dir = Path(tmpdir) / "config" / "wads" / "test" / "entities"
            entities_dir.mkdir(parents=True)
            dispatch = entities_dir / "dispatch.yaml"
            # Violation: MESSENGER_BRIDGE role with a pillar_slot
            dispatch.write_text(
                "entities:\n"
                "  - name: iris\n"
                "    role: MESSENGER_BRIDGE\n"
                "    node_slot: N6\n"
                "    purpose: Test messenger in pillar\n"
            )

            auditor = MandateAuditor(tmpdir)
            auditor.check_m3_iris_constant()
            result = auditor.results[0]
            assert result.mandate_id == "M3"
            # M3 should FAIL when MESSENGER_BRIDGE is in a Pillar slot
            assert result.passed is False, f"Expected M3 to fail when MESSENGER_BRIDGE in Pillar, but passed={result.passed}"
            assert "violations" in result.detail

    def test_m3_passes_when_iris_not_in_pillar(self):
        """M3 check passes when Iris is not assigned to a Node slot."""
        with tempfile.TemporaryDirectory() as tmpdir:
            entities_dir = Path(tmpdir) / "config" / "wads" / "test" / "entities"
            entities_dir.mkdir(parents=True)
            dispatch = entities_dir / "dispatch.yaml"
            # Non-violation: iris is a messenger, not a pillar keeper
            dispatch.write_text(
                "entities:\n"
                "  - name: iris\n"
                "    role: MESSENGER_BRIDGE\n"
                "    node_slot: null\n"
                "    purpose: Test messenger\n"
            )

            auditor = MandateAuditor(tmpdir)
            auditor.check_m3_iris_constant()
            result = auditor.results[0]
            assert result.mandate_id == "M3"
            assert result.passed is True

    def test_m6_detects_u_flag(self):
        """M6 check detects :U flag in Quadlet files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "config"
            config_dir.mkdir()
            container = config_dir / "test.container"
            container.write_text("[Service]\nUser=1000:U\n")

            auditor = MandateAuditor(tmpdir)
            auditor.check_m6_podman_sovereignty()
            result = auditor.results[0]
            assert result.mandate_id == "M6"
            assert result.passed is False
            assert "1 lines" in result.detail

    def test_m6_passes_without_u_flag(self):
        """M6 check passes when no :U flags present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "config"
            config_dir.mkdir()
            container = config_dir / "test.container"
            container.write_text("[Service]\nUserNS=keep-id\nUser=1000\n")

            auditor = MandateAuditor(tmpdir)
            auditor.check_m6_podman_sovereignty()
            result = auditor.results[0]
            assert result.mandate_id == "M6"
            assert result.passed is True

    def test_m16_detects_hardcoded_home_path(self):
        """M16 check detects hardcoded /home/ paths in core."""
        with tempfile.TemporaryDirectory() as tmpdir:
            omega_dir = Path(tmpdir) / "src" / "omega"
            omega_dir.mkdir(parents=True)
            # Use a non-test filename to avoid the "test" skip logic
            test_file = omega_dir / "config_module.py"
            test_file.write_text('config_path = "/home/user/config.yaml"\n')

            auditor = MandateAuditor(tmpdir)
            auditor.check_m16_modularization()
            result = auditor.results[0]
            assert result.mandate_id == "M16"
            assert result.passed is False
            assert "hardcoded" in result.detail

    def test_m16_ignores_skip_files(self):
        """M16 check ignores known exception files (constants.py, etc.)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            omega_dir = Path(tmpdir) / "src" / "omega"
            omega_dir.mkdir(parents=True)
            test_file = omega_dir / "constants.py"
            test_file.write_text('DEFAULT_PATH = "/home/user/default"\n')

            auditor = MandateAuditor(tmpdir)
            auditor.check_m16_modularization()
            result = auditor.results[0]
            assert result.mandate_id == "M16"
            assert result.passed is True  # Should pass because constants.py is skipped

    def test_m16_ignores_workers_and_library(self):
        """M16 check ignores workers/ and library/ subdirectories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workers_dir = Path(tmpdir) / "src" / "omega" / "workers"
            workers_dir.mkdir(parents=True)
            test_file = workers_dir / "worker.py"
            test_file.write_text('path = "/home/user/data"\n')

            auditor = MandateAuditor(tmpdir)
            auditor.check_m16_modularization()
            result = auditor.results[0]
            assert result.mandate_id == "M16"
            assert result.passed is True  # Should pass because workers/ is skipped


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
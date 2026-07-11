# 🔱 FirewallChecker Contract Tests — M21 Gate Integrity
# ⬡ OMEGA ⬡ PILLAR-P10 ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_firewall_checker_test ⬡ ACTIVE
# AP Token: AP-FIREWALL-CHECKER-TEST-v1.0.0
"""
Contract tests for FirewallChecker per M21 Gate Integrity.

Every code path returning a typed result MUST be exercised by at least one test
that validates the return type via isinstance(result, ExpectedType).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from omega.audit.firewall_checker import FirewallChecker, FirewallViolation, FirewallReport


class TestFirewallCheckerContracts:
    """M21 Contract Tests — Type validation for all public APIs."""

    def test_firewall_checker_detects_wad_import(self) -> None:
        """FirewallChecker.check_file returns List[FirewallViolation] for WAD imports."""
        checker = FirewallChecker()
        result = checker.check_file(Path("tests/test_fixtures/bad_wad_import.py"))

        # Contract: returns list
        assert isinstance(result, list), f"Expected list, got {type(result)}"

        # Contract: non-empty for bad file
        assert len(result) > 0, "Expected violations in bad_wad_import.py"

        # Contract: all items are FirewallViolation
        assert all(isinstance(v, FirewallViolation) for v in result), \
            "All items must be FirewallViolation instances"

        # Verify specific violations detected
        patterns_found = {v.pattern for v in result}
        assert any("config\\.wads" in p for p in patterns_found), "Should detect config.wads import"
        assert any("Sekhmet" in p for p in patterns_found), "Should detect Sekhmet reference"
        assert any("arcana_novai" in p for p in patterns_found), "Should detect WAD identifier"

    def test_firewall_checker_clean_file(self) -> None:
        """FirewallChecker.check_file returns List[FirewallViolation] for clean engine file."""
        checker = FirewallChecker()
        # Use clean test fixture
        result = checker.check_file(Path("tests/test_fixtures/clean_engine.py"))

        # Contract: returns list
        assert isinstance(result, list), f"Expected list, got {type(result)}"

        # Contract: all items are FirewallViolation (even if empty)
        assert all(isinstance(v, FirewallViolation) for v in result), \
            "All items must be FirewallViolation instances"

        # Clean file should have zero ERROR violations
        error_violations = [v for v in result if v.severity == "error"]
        assert len(error_violations) == 0, f"Clean file should have 0 errors, got {error_violations}"

    def test_firewall_checker_scan_returns_report(self) -> None:
        """FirewallChecker.scan returns FirewallReport with correct structure."""
        checker = FirewallChecker()
        result = checker.scan(Path("src/omega/audit"))

        # Contract: returns FirewallReport
        assert isinstance(result, FirewallReport), f"Expected FirewallReport, got {type(result)}"

        # Contract: scanned_files is int >= 0
        assert isinstance(result.scanned_files, int), "scanned_files must be int"
        assert result.scanned_files >= 0, "scanned_files must be non-negative"

        # Contract: violations is list of FirewallViolation
        assert isinstance(result.violations, list), "violations must be list"
        assert all(isinstance(v, FirewallViolation) for v in result.violations), \
            "All violations must be FirewallViolation"

        # Contract: clean is bool
        assert isinstance(result.clean, bool), "clean must be bool"

        # Contract: clean == (len(violations) == 0)
        assert result.clean == (len(result.violations) == 0), \
            "clean flag must match violations list"

    def test_firewall_report_properties(self) -> None:
        """FirewallReport.error_count and warning_count are correct."""
        checker = FirewallChecker()
        result = checker.check_file(Path("tests/test_fixtures/bad_wad_import.py"))

        report = FirewallReport(violations=result, scanned_files=1, clean=len(result) == 0)

        # Contract: error_count returns int
        assert isinstance(report.error_count, int), "error_count must be int"
        assert report.error_count >= 0, "error_count must be non-negative"

        # Contract: warning_count returns int
        assert isinstance(report.warning_count, int), "warning_count must be int"
        assert report.warning_count >= 0, "warning_count must be non-negative"

        # Contract: sum matches total
        assert report.error_count + report.warning_count == len(result), \
            "error_count + warning_count must equal total violations"

    def test_firewall_violation_structure(self) -> None:
        """FirewallViolation has all required fields with correct types."""
        checker = FirewallChecker()
        result = checker.check_file(Path("tests/test_fixtures/bad_wad_import.py"))

        assert len(result) > 0, "Need at least one violation for this test"
        v = result[0]

        # Contract: file is Path
        assert isinstance(v.file, Path), f"file must be Path, got {type(v.file)}"

        # Contract: line is int >= 1
        assert isinstance(v.line, int), f"line must be int, got {type(v.line)}"
        assert v.line >= 1, "line must be >= 1"

        # Contract: pattern is str
        assert isinstance(v.pattern, str), f"pattern must be str, got {type(v.pattern)}"

        # Contract: severity is Literal["error", "warning"]
        assert v.severity in ("error", "warning"), f"severity must be error/warning, got {v.severity}"

        # Contract: trace_id is str (8 chars)
        assert isinstance(v.trace_id, str), f"trace_id must be str, got {type(v.trace_id)}"
        assert len(v.trace_id) == 8, f"trace_id must be 8 chars, got {len(v.trace_id)}"

    def test_firewall_checker_custom_patterns(self) -> None:
        """FirewallChecker accepts custom patterns and uses them."""
        custom_patterns = [(r"CUSTOM_FORBIDDEN", "error")]
        checker = FirewallChecker(patterns=custom_patterns)

        # Create temp file with custom pattern in actual CODE (not a comment —
        # the checker intentionally skips comments/docstrings to avoid false positives)
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("FORBIDDEN_VALUE = 'CUSTOM_FORBIDDEN'\n")
            temp_path = Path(f.name)

        try:
            result = checker.check_file(temp_path)
            assert len(result) == 1, "Should detect custom pattern in code"
            assert result[0].pattern == "CUSTOM_FORBIDDEN"
            assert result[0].severity == "error"
        finally:
            temp_path.unlink()

    def test_firewall_checker_nonexistent_file(self) -> None:
        """FirewallChecker.check_file handles nonexistent files gracefully."""
        checker = FirewallChecker()
        result = checker.check_file(Path("nonexistent_file.py"))

        # Contract: returns empty list (not exception)
        assert isinstance(result, list), "Must return list"
        assert len(result) == 0, "Must return empty list for nonexistent file"

    def test_firewall_checker_scan_nonexistent_root(self) -> None:
        """FirewallChecker.scan handles nonexistent root gracefully."""
        checker = FirewallChecker()
        result = checker.scan(Path("nonexistent_directory"))

        # Contract: returns FirewallReport with clean=True, scanned_files=0
        assert isinstance(result, FirewallReport)
        assert result.scanned_files == 0
        assert result.clean is True
        assert len(result.violations) == 0


class TestFirewallCheckerIntegration:
    """Integration-style tests for the full scan workflow."""

    def test_scan_engine_core_runs(self) -> None:
        """Full scan of src/omega runs and returns valid FirewallReport."""
        checker = FirewallChecker()
        report = checker.scan(Path("src/omega"))

        # Contract: returns FirewallReport with correct structure
        assert isinstance(report, FirewallReport)
        assert isinstance(report.violations, list)
        assert isinstance(report.scanned_files, int)
        assert isinstance(report.clean, bool)
        assert report.scanned_files > 0, "Should scan at least some files"
        # Note: M2 compliance (error_count == 0) is a separate engineering goal

    def test_scan_excludes_test_files(self) -> None:
        """Scanner should skip test files and __pycache__."""
        checker = FirewallChecker()
        report = checker.scan(Path("src/omega"))

        # Should not scan test files
        test_files_scanned = any("test_" in str(v.file) for v in report.violations)
        assert not test_files_scanned, "Test files should be excluded from scan"

        pycache_files_scanned = any("__pycache__" in str(v.file) for v in report.violations)
        assert not pycache_files_scanned, "__pycache__ files should be excluded"
# AP: AP-OBS1-ZRAM-TEST-v1.0.0
# 🔱 Tests for zRAM Monitoring
# ⬡ OMEGA ⬡ MONITORING ⬡ tests/test_zram_monitoring.py
"""Tests for zRAM and swap monitoring.

Tests:
- get_zram_stats() returns proper structure
- get_swap_zram_pressure() computes pressure correctly
- Integration with collect_all() and get_memory_status()
- Fallback behavior when zRAM is not available
"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from omega.monitoring import HardwareMonitor


class TestZramStats:
    def test_zram_stats_no_zram(self):
        """When no zRAM devices exist, returns available=False."""
        hm = HardwareMonitor()
        with patch.object(Path, "glob", return_value=[]):
            stats = hm.get_zram_stats()
        assert stats["available"] is False
        assert stats["devices"] == []

    def test_zram_stats_structure(self):
        """zram_stats returns proper structure when zRAM exists."""
        hm = HardwareMonitor()
        stats = hm.get_zram_stats()
        assert "available" in stats
        assert "devices" in stats
        assert isinstance(stats["devices"], list)

    def test_zram_stats_with_mock_data(self):
        """Test zRAM stats parsing with mock /sys data."""
        hm = HardwareMonitor()

        # Mock zram device directory
        mock_dev = MagicMock()
        mock_dev.name = "zram0"
        mock_dev.__truediv__ = lambda self, other: MagicMock(
            exists=MagicMock(return_value=True),
            read_text=MagicMock(return_value="1000000\n"),
        )

        with patch.object(Path, "glob", return_value=[mock_dev]):
            with patch.object(Path, "exists", return_value=True):
                stats = hm.get_zram_stats()

        assert "available" in stats
        assert "devices" in stats


class TestSwapZramPressure:
    def test_swap_zram_pressure_structure(self):
        """get_swap_zram_pressure returns proper structure."""
        hm = HardwareMonitor()
        pressure = hm.get_swap_zram_pressure()

        assert "swap_total_mb" in pressure
        assert "swap_used_mb" in pressure
        assert "swap_percent" in pressure
        assert "zram_available" in pressure
        assert "zram_compressed_mb" in pressure
        assert "zram_original_mb" in pressure
        assert "zram_compression_ratio" in pressure
        assert "zram_compression_savings_mb" in pressure
        assert "effective_swap_total_mb" in pressure
        assert "effective_swap_used_mb" in pressure
        assert "effective_swap_percent" in pressure
        assert "pressure_score" in pressure
        assert "pressure_level" in pressure

    def test_pressure_level_values(self):
        """Pressure level should be one of the valid values."""
        hm = HardwareMonitor()
        pressure = hm.get_swap_zram_pressure()
        assert pressure["pressure_level"] in [
            "SAFE", "LOW", "MODERATE", "HIGH", "CRITICAL"
        ]

    def test_pressure_score_range(self):
        """Pressure score should be in [0, 1]."""
        hm = HardwareMonitor()
        pressure = hm.get_swap_zram_pressure()
        assert 0.0 <= pressure["pressure_score"] <= 1.0


class TestMemoryStatusIntegration:
    def test_memory_status_includes_zram(self):
        """get_memory_status includes zram key."""
        hm = HardwareMonitor()
        mem = hm.get_memory_status()
        assert "zram" in mem
        assert "available" in mem["zram"]

    def test_collect_all_includes_zram(self):
        """collect_all includes zram and swap_zram_pressure."""
        hm = HardwareMonitor()
        stats = hm.collect_all()
        assert "zram" in stats
        assert "swap_zram_pressure" in stats

    def test_collect_all_zram_structure(self):
        """collect_all zram has proper structure."""
        hm = HardwareMonitor()
        stats = hm.collect_all()
        zram = stats["zram"]
        assert "available" in zram
        assert "devices" in zram

    def test_collect_all_swap_zram_pressure_structure(self):
        """collect_all swap_zram_pressure has proper structure."""
        hm = HardwareMonitor()
        stats = hm.collect_all()
        szp = stats["swap_zram_pressure"]
        assert "pressure_score" in szp
        assert "pressure_level" in szp
        assert "effective_swap_total_mb" in szp


class TestDiffIntegration:
    def test_diff_includes_zram_delta(self):
        """diff() includes zram_compressed_delta_mb."""
        hm = HardwareMonitor()
        before = hm.collect_all()
        after = hm.collect_all()
        diff = HardwareMonitor.diff(before, after)
        assert "zram_compressed_delta_mb" in diff


class TestZramStatsParsing:
    def test_zram_mm_stat_parsing(self):
        """Test parsing of /sys/block/zram0/mm_stat format."""
        hm = HardwareMonitor()

        # Create a mock that simulates mm_stat content
        mock_mm_stat = MagicMock()
        mock_mm_stat.exists = MagicMock(return_value=True)
        mock_mm_stat.read_text = MagicMock(
            return_value="1048576 524288 524288 0 0 0 0\n"
        )

        mock_dev = MagicMock()
        mock_dev.name = "zram0"
        mock_dev.__truediv__ = MagicMock(return_value=mock_mm_stat)

        with patch.object(Path, "glob", return_value=[mock_dev]):
            stats = hm.get_zram_stats()

        assert stats["available"] is True
        assert len(stats["devices"]) == 1
        dev = stats["devices"][0]
        assert dev["original_bytes"] == 1048576
        assert dev["compressed_bytes"] == 524288
        assert dev["compression_ratio"] == 2.0  # 1048576 / 524288 = 2.0

    def test_zram_no_compression(self):
        """Test zram with zero compressed size."""
        hm = HardwareMonitor()

        mock_mm_stat = MagicMock()
        mock_mm_stat.exists = MagicMock(return_value=True)
        mock_mm_stat.read_text = MagicMock(
            return_value="0 0 0 0 0 0 0\n"
        )

        mock_dev = MagicMock()
        mock_dev.name = "zram0"
        mock_dev.__truediv__ = MagicMock(return_value=mock_mm_stat)

        with patch.object(Path, "glob", return_value=[mock_dev]):
            stats = hm.get_zram_stats()

        assert stats["overall_compression_ratio"] == 0.0

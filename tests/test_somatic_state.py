"""Tests for Phase C — Somatic State (C.1.1–C.1.2)."""

import pytest

from omega.cvar_table import cvar_get


class TestSomaticStateKey:
    """SomaticStateKey parameter tuple validation."""

    def test_master_kill_switch_exists(self):
        assert cvar_get("config.somatic.enable") is False

    def test_somatic_cvars_registered(self):
        assert cvar_get("config.somatic.max_snapshots_per_entity") == 3
        assert cvar_get("config.somatic.memory_budget_mb") == 1024
        assert cvar_get("config.somatic.page_size_mb") == 2
        assert cvar_get("config.somatic.ctypes_safe_mode") is True


class TestDreamingCycleCvars:
    """Dreaming Cycle cvar configuration (C.2.x)."""

    def test_dreaming_cvars_registered(self):
        assert cvar_get("config.dreaming.enable") is False
        assert cvar_get("config.dreaming.model") == "qwen3-0.6b"
        assert cvar_get("config.dreaming.max_rss_mb") == 1500
        assert cvar_get("config.dreaming.max_hours_per_day") == 4
        assert cvar_get("config.dreaming.poll_interval_ms") == 100


class TestSymmetryCvars:
    """Symmetry-Break Audit cvar configuration (C.3.x)."""

    def test_symmetry_cvars_registered(self):
        assert cvar_get("config.symmetry.enable") is False
        assert cvar_get("config.symmetry.mode") == "fast"
        assert cvar_get("config.symmetry.max_attempts") == 2
        assert cvar_get("config.symmetry.semantic_delta_threshold") == 0.3

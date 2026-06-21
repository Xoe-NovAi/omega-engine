"""Tests for Phase C — Symmetry-Break Audit (C.3.1–C.3.4)."""

import pytest


class TestFastSlowToggle:
    """SymmetryMode cvar toggling."""

    def test_cvar_registered(self):
        from omega.cvar_table import cvar_get
        assert cvar_get("config.symmetry.mode") == "fast"

    def test_cvar_update(self):
        from omega.cvar_table import cvar_set, cvar_get
        assert cvar_set("config.symmetry.mode", "slow") is True
        assert cvar_get("config.symmetry.mode") == "slow"
        cvar_set("config.symmetry.mode", "fast")


class TestSkepticalCircuitBreaker:
    """Circuit breaker max attempts and fallback."""

    def test_max_attempts_config(self):
        from omega.cvar_table import cvar_get
        assert cvar_get("config.symmetry.max_attempts") == 2

    def test_threshold_config(self):
        from omega.cvar_table import cvar_get
        threshold = cvar_get("config.symmetry.semantic_delta_threshold")
        assert 0.0 <= threshold <= 1.0

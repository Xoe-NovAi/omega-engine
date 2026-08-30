# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Audience Calibrator Tests (D16-1)
# ⬡ OMEGA ⬡ RESEARCHER ⬡ hy3-free ⬡ opencode ⬡ trc_research
# Tests for src/omega/oracle/audience_calibrator.py
# Coverage: profile loading, detection, prompt building, fallback

import pytest
import anyio
from pathlib import Path
from omega.oracle.audience_calibrator import (
    AudienceCalibrator,
    AudienceProfile,
    CalibrationResult,
    get_audience_calibrator,
)

# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def calibrator():
    """Return an AudienceCalibrator using the live _omega_default audience.yaml."""
    return AudienceCalibrator()


# ── Profile loading tests ──────────────────────────────────────────────────


class TestProfileLoading:
    def test_loads_all_profiles_from_yaml(self, calibrator):
        """D16-1: YAML with 8 profiles (6 base + 2 S7) must load all 8."""
        profiles = calibrator.list_profiles()
        assert len(profiles) == 8, f"Expected 8 profiles, got {len(profiles)}"
        expected = {
            "technical", "casual", "academic", "executive",
            "exhausted_sysadmin", "teaching", "mechanic_friend", "client_formal",
        }
        assert set(profiles) == expected, f"Missing profiles: {expected - set(profiles)}"

    def test_default_profile_is_technical(self, calibrator):
        """D16-1: Default profile must be 'technical'."""
        assert calibrator.default_profile == "technical"

    def test_get_known_profile_returns_profile(self, calibrator):
        """D16-1: get_profile returns AudienceProfile for known names."""
        profile = calibrator.get_profile("casual")
        assert profile is not None
        assert profile.name == "Casual / Conversational"

    def test_get_unknown_profile_falls_back_to_default(self, calibrator):
        """D16-1: get_profile falls back to default when profile unknown."""
        profile = calibrator.get_profile("nonexistent_profile")
        assert profile is not None
        assert profile.name == "Technical / Engineering"

    def test_fallback_defaults_when_file_missing(self):
        """D16-1: Calibrator loads built-in defaults when YAML file missing."""
        c = AudienceCalibrator(profile_path=Path("/tmp/nonexistent_audience.yaml"))
        profiles = c.list_profiles()
        assert len(profiles) == 2  # technical + casual
        assert "technical" in profiles
        assert "casual" in profiles


# ── Profile detection tests ────────────────────────────────────────────────


class TestProfileDetection:
    def test_detect_technical_from_keywords(self, calibrator):
        """D16-1: 'implement this debug feature' → technical."""
        assert calibrator.detect_profile_from_query("implement this debug feature") == "technical"

    def test_detect_casual_from_keywords(self, calibrator):
        """D16-1: 'explain how this works' → casual."""
        assert calibrator.detect_profile_from_query("explain how this works") == "casual"

    def test_detect_academic_from_keywords(self, calibrator):
        """D16-1: 'research paper analysis' → academic."""
        assert calibrator.detect_profile_from_query("research paper analysis") == "academic"

    def test_detect_executive_from_keywords(self, calibrator):
        """D16-1: 'summary decision risk' → executive."""
        assert calibrator.detect_profile_from_query("summary decision risk") == "executive"

    def test_detect_exhausted_from_keywords(self, calibrator):
        """D16-1: 'urgent production down' → exhausted_sysadmin."""
        assert calibrator.detect_profile_from_query("urgent production down") == "exhausted_sysadmin"

    def test_detect_teaching_from_keywords(self, calibrator):
        """D16-1: 'help me learn this' → teaching."""
        assert calibrator.detect_profile_from_query("help me learn this") == "teaching"

    def test_no_match_returns_default(self, calibrator):
        """D16-1: Query with no keywords returns default (technical)."""
        assert calibrator.detect_profile_from_query("zzz zebra xylophone") == "technical"


# ── Calibration prompt building tests ──────────────────────────────────────


class TestCalibrationPrompt:
    def test_build_prompt_includes_profile_name(self, calibrator):
        """D16-1: Calibration prompt contains the target profile name."""
        prompt = calibrator.build_calibration_prompt("academic", "A wise philosopher")
        assert "Academic / Research" in prompt
        assert "A wise philosopher" in prompt

    def test_build_prompt_includes_constraints(self, calibrator):
        """D16-1: Calibration prompt contains profile constraints."""
        prompt = calibrator.build_calibration_prompt("exhausted_sysadmin", "An expert")
        assert "NO pleasantries" in prompt
        assert "Immediate actionable" in prompt

    def test_build_prompt_unknown_profile_falls_back(self, calibrator):
        """D16-1: Unknown profile name falls back to default (technical)."""
        prompt = calibrator.build_calibration_prompt("nonexistent", "Expert")
        assert "Technical / Engineering" in prompt


# ── Calibrate method tests (all async) ──────────────────────────────────────


@pytest.mark.anyio
class TestCalibrate:
    async def test_no_model_gateway_returns_original(self, calibrator):
        """D16-1: calibrate() without model_gateway returns original text unchanged."""
        result = await calibrator.calibrate(
            response_text="Hello world",
            entity_personality="A friendly assistant",
        )
        assert isinstance(result, CalibrationResult)
        assert result.calibrated_text == "Hello world"
        assert result.token_ratio == 1.0
        assert result.profile_name == "technical"

    async def test_calibrate_auto_detects_from_query(self, calibrator):
        """D16-1: calibrate() auto-detects profile from query when profile_name=None."""
        result = await calibrator.calibrate(
            response_text="Fix this production bug",
            entity_personality="A sysadmin",
            query="urgent production fire",
        )
        assert result.profile_name == "exhausted_sysadmin"

    async def test_calibrate_with_explicit_profile(self, calibrator):
        """D16-1: calibrate() uses explicit profile_name when provided."""
        result = await calibrator.calibrate(
            response_text="The engine uses AnyIO for async",
            entity_personality="A technical expert",
            profile_name="casual",
        )
        assert result.profile_name == "casual"

    async def test_calibrate_token_tracking(self, calibrator):
        """D16-1: calibrate returns token counts and ratio."""
        result = await calibrator.calibrate(
            response_text="Four score and seven years ago today",
            entity_personality="A speaker",
            profile_name="academic",
        )
        assert result.tokens_original == 7
        assert result.tokens_calibrated == 7
        assert result.token_ratio == 1.0


# ── Global singleton test ──────────────────────────────────────────────────


class TestSingleton:
    def test_get_audience_calibrator_returns_instance(self):
        """D16-1: get_audience_calibrator returns a working instance."""
        c = get_audience_calibrator()
        assert isinstance(c, AudienceCalibrator)
        assert len(c.list_profiles()) >= 2

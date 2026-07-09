# 🔱 Contract Tests — S4 Gemma 4 MTP Speculative Decoding
# AP: AP-GEMMA4-MTP-S4-TESTS-v1.0.0
# ⬡ OMEGA ⬡ JOHN_CARMACK ⬡ opencode ⬡ trc_S3_S4 ⬡ M21-CONTRACT-TESTS
#
# [M21 Gate Integrity] Validates S4 configuration: SpeculativeDecodeConfig
# supports MTP drafting, and config/models.yaml declares Gemma 4 MTP pairs
# with the correct `--spec-type draft-mtp` server flag.

import pytest
import yaml
from pathlib import Path

from omega.oracle.cpu_optimizer import SpeculativeDecodeConfig


def _load_models_yaml():
    path = Path(__file__).resolve().parent.parent / "config" / "models.yaml"
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ── S4: SpeculativeDecodeConfig supports MTP ───────────────────────────────
def test_s4_spec_decode_config_has_mtp_fields():
    """[S4] SpeculativeDecodeConfig must support draft_type='mtp' and mtp_draft_model."""
    cfg = SpeculativeDecodeConfig(draft_type="mtp", mtp_draft_model="gemma-4-26b-it-assistant")
    assert cfg.draft_type == "mtp"
    assert cfg.mtp_draft_model == "gemma-4-26b-it-assistant"
    # Default remains ngram for backward compat
    default_cfg = SpeculativeDecodeConfig()
    assert default_cfg.draft_type == "ngram"


# ── S4: models.yaml declares Gemma 4 MTP pairs ─────────────────────────────
def test_s4_models_yaml_has_gemma4_mtp_section():
    """[S4] config/models.yaml must declare speculative_decode.gemma4_mtp with pairs."""
    data = _load_models_yaml()
    assert "speculative_decode" in data, "speculative_decode section missing"
    s4 = data["speculative_decode"].get("gemma4_mtp", {})
    assert s4.get("enabled") is True
    assert s4.get("draft_type") == "mtp"
    # Correct server flag per Final Order correction
    assert s4.get("server_flag") == "--spec-type draft-mtp"
    # At least one Gemma 4 target→draft pair (corrected MoE ID per Researcher S1 audit)
    pairs = s4.get("pairs", {})
    assert "gemma-4-26b-a4b-it" in pairs
    assert pairs["gemma-4-26b-a4b-it"] == "gemma-4-26b-a4b-it-assistant"


# ── S4: zen2_build must NOT contain deprecated GGML_FLASH_ATTN ──────────────
def test_s4_zen2_build_no_flash_attn_flag():
    """[S4] Per Final Order: GGML_FLASH_ATTN is default/deprecated. Must not appear in cmake_flags."""
    data = _load_models_yaml()
    zen2 = data.get("zen2_build", {})
    cmake_flags = zen2.get("cmake_flags", [])
    for flag in cmake_flags:
        assert "FLASH_ATTN" not in flag, f"Deprecated GGML_FLASH_ATTN flag found: {flag}"

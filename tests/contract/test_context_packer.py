# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""M21 Gate Integrity: Contract Tests for the Context Packer.

[M21: Gate Integrity Mandate] Every core API boundary returning a typed result
MUST be exercised by at least one test that validates the return type.

These tests verify the Context Packer's public API boundaries:
  1. PlatformConfig.from_profile_config() returns a PlatformConfig
  2. get_format_adapter() returns a FormatAdapter (isinstance check)
  3. get_ordering_strategy() returns a BundleOrderingStrategy
  4. Unknown format/strategy raises ValueError (M21 — no silent fallback)
  5. Each FormatAdapter.render_bundle() returns a str
  6. Each FormatAdapter.render_manifest() returns a str
  7. Each BundleOrderingStrategy.order() returns a list
  8. EnhancedContextPacker.load_config() populates profiles with platform config
  9. EnhancedContextPacker.pack() produces a manifest + bundles + (optionally) vault

These are REAL isinstance() checks against the actual classes — not mocks.
"""

import os
import sys
from pathlib import Path

import pytest

# Ensure the context-packer skill is importable (it's outside src/).
_SKILL_DIR = Path(__file__).resolve().parent.parent.parent / ".opencode" / "skills" / "context-packer"
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from platform_adapters import (  # noqa: E402
    PlatformConfig,
    PlatformProfile,
    FormatAdapter,
    BundleOrderingStrategy,
    get_format_adapter,
    get_ordering_strategy,
    XMLFormatAdapter,
    MarkdownStructuredAdapter,
    FORMAT_REGISTRY,
    STRATEGY_REGISTRY,
)
from packer import EnhancedContextPacker, PackProfile  # noqa: E402


# ── Test 1: PlatformConfig.from_profile_config() returns PlatformConfig ──
@pytest.mark.anyio
async def test_platform_config_contract():
    """M21: from_profile_config() returns a PlatformConfig with typed fields."""
    cfg = PlatformConfig.from_profile_config({
        "target_platform": "web-grok",
        "target_model": "grok-4.3",
        "format": "xml-markdown-hybrid",
        "bundle_ordering": "priority-weighted",
        "max_slots": 20,
        "token_budget": {"total": 200000, "per_bundle": 15000, "reserved_output": 50000},
        "prompt_caching": {"enabled": True, "cache_prefix": ["manifest"]},
    })
    assert isinstance(cfg, PlatformConfig)
    assert cfg.profile == PlatformProfile.WEB_GROK
    assert cfg.target_model == "grok-4.3"
    assert cfg.max_slots == 20
    assert cfg.token_budget_total == 200000
    assert cfg.prompt_caching is True
    assert cfg.cache_prefix == ["manifest"]


# ── Test 2: get_format_adapter returns a FormatAdapter ──────────────────
@pytest.mark.anyio
async def test_format_adapter_contract():
    """M21: get_format_adapter() returns a FormatAdapter instance."""
    for name in FORMAT_REGISTRY:
        adapter = get_format_adapter(name)
        assert isinstance(adapter, FormatAdapter), f"{name} not a FormatAdapter"


# ── Test 3: get_ordering_strategy returns a BundleOrderingStrategy ──────
@pytest.mark.anyio
async def test_ordering_strategy_contract():
    """M21: get_ordering_strategy() returns a BundleOrderingStrategy instance."""
    for name in STRATEGY_REGISTRY:
        strategy = get_ordering_strategy(name)
        assert isinstance(strategy, BundleOrderingStrategy), f"{name} not a BundleOrderingStrategy"


# ── Test 4: Unknown format/strategy raises (M21 — no silent fallback) ───
@pytest.mark.anyio
async def test_unknown_format_raises():
    """M21: unknown format must raise ValueError, never silently fall back."""
    with pytest.raises(ValueError):
        get_format_adapter("bogus-format")


@pytest.mark.anyio
async def test_unknown_strategy_raises():
    """M21: unknown strategy must raise ValueError, never silently fall back."""
    with pytest.raises(ValueError):
        get_ordering_strategy("bogus-strategy")


# ── Test 5: render_bundle returns a str ─────────────────────────────────
@pytest.mark.anyio
async def test_render_bundle_returns_str():
    """M21: every adapter's render_bundle() returns a str."""
    sample_files = [{
        "rendered": '<file path="x.py" tokens="10">\ncontent\n</file>\n',
        "token_count": 10,
    }]
    for name, adapter in FORMAT_REGISTRY.items():
        result = adapter.render_bundle("test_theme", sample_files, "test-profile")
        assert isinstance(result, str), f"{name} render_bundle not str"
        assert len(result) > 0


# ── Test 6: render_manifest returns a str ───────────────────────────────
@pytest.mark.anyio
async def test_render_manifest_returns_str():
    """M21: every adapter.render_manifest() returns a str."""
    bundles = [{"theme": "mandates", "files": [{}], "token_count": 100}]
    for name, adapter in FORMAT_REGISTRY.items():
        result = adapter.render_manifest(
            "test-profile", bundles, 1, 100, "desc", 12, "claude-sonnet-5", True
        )
        assert isinstance(result, str), f"{name} render_manifest not str"
        assert "test-profile" in result


# ── Test 7: ordering strategy returns a list ────────────────────────────
@pytest.mark.anyio
async def test_ordering_returns_list():
    """M21: every strategy.order() returns a list of bundle dicts."""
    bundles = [
        {"theme": "mandates", "token_count": 100, "priority": 3, "relevance": 1.0},
        {"theme": "general", "token_count": 50, "priority": 1, "relevance": 0.3},
        {"theme": "handoff", "token_count": 80, "priority": 2, "relevance": 0.7},
    ]
    for name, strategy in STRATEGY_REGISTRY.items():
        result = strategy.order(bundles)
        assert isinstance(result, list), f"{name} order() not list"
        assert len(result) == len(bundles)


# ── Test 8: EnhancedContextPacker.load_config populates platform config ─
@pytest.mark.anyio
async def test_load_config_platform_contract():
    """M21: load_config() populates profiles with PackProfile + platform config."""
    config_path = str(_SKILL_DIR / "packer-config.yaml")
    packer = EnhancedContextPacker(config_path=config_path)
    await packer.load_config()
    assert isinstance(packer.profiles, dict)
    assert len(packer.profiles) > 0
    # A platform-tuned profile (web-claude-sonnet5) must carry a PlatformConfig
    if "web-claude-sonnet5" in packer.profiles:
        prof = packer.profiles["web-claude-sonnet5"]
        assert isinstance(prof, PackProfile)
        assert prof.platform is not None
        assert isinstance(prof.platform, PlatformConfig)
        assert prof.platform.target_model == "claude-sonnet-5"


# ── Test 9: pack() produces valid output (integration contract) ─────────
@pytest.mark.anyio
async def test_pack_produces_valid_output(tmp_path, monkeypatch):
    """M21: pack() writes a manifest + at least one bundle to the output dir."""
    config_path = str(_SKILL_DIR / "packer-config.yaml")
    packer = EnhancedContextPacker(config_path=config_path)
    await packer.load_config()

    # Use a small profile to keep the test fast (engineering-p3).
    if "engineering-p3" not in packer.profiles:
        pytest.skip("engineering-p3 profile not present")
    output_dir, pack_id, pack_timestamp = await packer.pack("engineering-p3")

    # Manifest is now written to profile root (per v3 manual §1.8)
    profile_root = Path("context_packs") / "engineering-p3"
    manifest = profile_root / "00_PROJECT_MANIFEST.md"
    assert manifest.exists(), "manifest not created at profile root"
    assert manifest.stat().st_size > 0

    # At least one bundle file must exist in generated/
    bundles = [p for p in Path(output_dir).iterdir() if p.suffix in (".xml", ".md")]
    assert len(bundles) > 0, "no bundle files produced"

    # Cleanup so we don't pollute the repo.
    import shutil
    shutil.rmtree(output_dir, ignore_errors=True)
    vault = Path("data/coordination/pii_vaults/engineering-p3.json")
    if vault.exists():
        vault.unlink()
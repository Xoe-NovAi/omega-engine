# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


def _import_optimizer_module():
    mod_name = "omega.oracle.cpu_optimizer"
    if mod_name in sys.modules:
        return importlib.reload(sys.modules[mod_name])
    return importlib.import_module(mod_name)


class TestCpuOptimizerFactory:
    def test_factory_returns_zen2_when_profile_missing(self, tmp_path: Path):
        mod = _import_optimizer_module()
        fake_config = tmp_path / "config" / "hardware_profile.yaml"
        with patch.object(mod.CpuOptimizerFactory, "_PROFILE_PATH", fake_config):
            optimizer = mod.CpuOptimizerFactory.get_optimizer()
        assert isinstance(optimizer, mod.Zen2Optimizer)

    def test_factory_returns_raptor_lake_when_hybrid_profile_exists(self, tmp_path: Path):
        mod = _import_optimizer_module()
        profile = tmp_path / "config" / "hardware_profile.yaml"
        profile.parent.mkdir(parents=True, exist_ok=True)
        profile.write_text(
            "cpu:\n"
            "  microarch: raptorlake\n"
            "  is_hybrid: true\n"
            "  p_cores_physical: [0, 2, 4]\n"
            "  e_cores_logical: [12, 13]\n"
        )
        with patch.object(mod.CpuOptimizerFactory, "_PROFILE_PATH", profile):
            optimizer = mod.CpuOptimizerFactory.get_optimizer()
        assert isinstance(optimizer, mod.RaptorLakeOptimizer)
        assert optimizer.get_compute_affinity() == [0, 2, 4]
        assert optimizer.get_io_affinity() == [12, 13]

    def test_factory_returns_generic_fallback_when_unknown_profile(self, tmp_path: Path):
        mod = _import_optimizer_module()
        profile = tmp_path / "config" / "hardware_profile.yaml"
        profile.parent.mkdir(parents=True, exist_ok=True)
        profile.write_text(
            "cpu:\n"
            "  microarch: rocketlake\n"
            "  is_hybrid: false\n"
        )
        with patch.object(mod.CpuOptimizerFactory, "_PROFILE_PATH", profile):
            optimizer = mod.CpuOptimizerFactory.get_optimizer()
        assert isinstance(optimizer, mod.GenericFallbackOptimizer)

    def test_zen2_class_remains_callable(self):
        """Backward compatibility: Zen2Optimizer() must still work as a class constructor."""
        mod = _import_optimizer_module()
        opt = mod.Zen2Optimizer()
        assert isinstance(opt, mod.Zen2Optimizer)
        assert hasattr(opt, "spec_decode")
        assert hasattr(opt, "get_recommended_threads")

    def test_legacy_constants_preserved(self):
        """Legacy module-level constants must remain importable."""
        mod = _import_optimizer_module()
        assert mod.ZEN2_COMPUTE_CORES == [0, 1, 2, 3, 4, 5, 6]
        assert mod.ZEN2_IO_THREADS == [7]
        assert mod.ZEN2_RECOMMENDED_THREADS == 7
        assert mod.RAM_AVAILABLE_AI_MB > 0
        assert mod.RAM_DRAFT_RESIDENT_MB == 300

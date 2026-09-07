# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from detect_hardware_profile import (
    build_profile,
    _parse_cpu_range,
    _detect_cpu_flags,
    _to_yaml,
    HardwareProfile,
    CPUProfile,
    MemoryProfile,
    GPUProfile,
)


class TestDhalDetector:
    def test_parse_cpu_range(self):
        assert _parse_cpu_range("0-3,7,9-11") == [0, 1, 2, 3, 7, 9, 10, 11]
        assert _parse_cpu_range("") == []
        assert _parse_cpu_range("4") == [4]
        assert _parse_cpu_range("0-0") == [0]

    def test_build_profile_structure(self):
        profile = build_profile()
        assert isinstance(profile, HardwareProfile)
        assert isinstance(profile.cpu, CPUProfile)
        assert isinstance(profile.memory, MemoryProfile)
        assert isinstance(profile.gpu, GPUProfile)
        assert profile.cpu.logical_threads >= 1
        assert profile.cpu.recommended_threads >= 1
        assert profile.memory.total_mb > 0

    def test_yaml_serialization(self):
        profile = build_profile()
        from dataclasses import asdict
        yaml_str = _to_yaml(asdict(profile))
        assert "cpu:" in yaml_str
        assert "memory:" in yaml_str
        assert "gpu:" in yaml_str
        assert "recommended_threads:" in yaml_str

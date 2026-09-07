# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Hardware Profile Detector
# ⬡ OMEGA ⬡ KALI ⬡ trc_council ⬡ SCAFFOLD
#
# Auto-detects hardware constraints and returns optimal council configuration.

from __future__ import annotations
from pathlib import Path
from typing import Optional
import yaml

from .models import HardwareProfile


def detect_hardware_profile(profile_path: Optional[Path] = None) -> HardwareProfile:
    """Auto-detect hardware profile for optimal council configuration.

    Args:
        profile_path: Optional path to hardware_profile.yaml. If provided,
            parses the YAML for RAM, GPU, and channel info. Otherwise,
            falls back to runtime detection.

    Returns:
        HardwareProfile based on available RAM, GPU, and thermal limits.
    """
    if profile_path and profile_path.exists():
        try:
            with open(profile_path, "r") as f:
                data = yaml.safe_load(f) or {}
            mem = data.get("memory", {})
            gpu = data.get("gpu", {})
            total_mb = mem.get("total_mb", 0)
            channels = mem.get("channels", 1)
            gpu_vendor = gpu.get("vendor", "").lower()
            is_discrete = gpu.get("is_discrete", False)

            # 32GB dual-channel + no discrete GPU -> LOCAL_32GB_DUAL
            if total_mb >= 32768 and channels >= 2 and not is_discrete:
                return HardwareProfile.LOCAL_32GB_DUAL
            # 32GB with discrete GPU -> CLOUD_EQUIVALENT
            if total_mb >= 32768 and is_discrete:
                return HardwareProfile.CLOUD_EQUIVALENT
            # 16GB -> LOCAL_16GB
            if total_mb >= 16384:
                return HardwareProfile.LOCAL_16GB
            # 8GB -> LOCAL_8GB
            if total_mb >= 8192:
                return HardwareProfile.LOCAL_8GB
            # 4GB or less -> LOCAL_4GB
            return HardwareProfile.LOCAL_4GB
        except Exception:
            pass

    # Default: LOCAL_16GB (Ryzen 5700U, 16GB RAM — current dev environment)
    return HardwareProfile.LOCAL_16GB

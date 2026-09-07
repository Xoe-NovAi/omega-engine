# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Execution Mode Selector
# ⬡ OMEGA ⬡ KALI ⬡ trc_council ⬡ SCAFFOLD
#
# Selects optimal node execution concurrency mode based on hardware.

from __future__ import annotations
from .models import HardwareProfile, ExecutionMode


def select_execution_mode(profile: HardwareProfile, node_count: int) -> ExecutionMode:
    """Select optimal execution mode based on hardware profile and node count.

    Rules:
    - CLOUD_EQUIVALENT → PARALLEL (all nodes simultaneously)
    - LOCAL_32GB_DUAL → BATCH_8 if node_count <= 8 else BATCH_4
    - LOCAL_16GB → BATCH_4 if node_count <= 4 else SERIAL_INDEPENDENT
    - LOCAL_8GB → BATCH_2 (2 at a time)
    - LOCAL_4GB → SERIAL_INDEPENDENT (one at a time)
    """
    if profile == HardwareProfile.CLOUD_EQUIVALENT:
        return ExecutionMode.PARALLEL

    elif profile == HardwareProfile.LOCAL_32GB_DUAL:
        return ExecutionMode.BATCH_8 if node_count <= 8 else ExecutionMode.BATCH_4

    elif profile == HardwareProfile.LOCAL_16GB:
        return ExecutionMode.BATCH_4 if node_count <= 4 else ExecutionMode.SERIAL_INDEPENDENT

    elif profile == HardwareProfile.LOCAL_8GB:
        return ExecutionMode.BATCH_2

    else:  # LOCAL_4GB
        return ExecutionMode.SERIAL_INDEPENDENT
